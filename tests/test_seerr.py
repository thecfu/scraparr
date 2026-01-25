"""Tests for the parallel title fetching in seerr connector."""

from unittest.mock import patch, MagicMock

from scraparr.connectors.seerr import Seerr


class TestFetchAllTitles:

    def setup_method(self):
        """Create a Seerr instance for testing."""
        config = {
            'url': 'http://test',
            'api_key': 'key',
            'api_version': 'v1',
            'alias': 'test_seerr',
            'detailed': True  # Need detailed=True to test title fetching
        }
        self.mock_metrics = MagicMock()
        self.seerr = Seerr(config, self.mock_metrics, 'overseerr')

    def test_empty_list_returns_empty_dict(self):
        """Empty requests list returns empty dict without making API calls."""
        result = self.seerr._fetch_all_titles([])
        assert result == {}

    @patch.object(Seerr, 'get')
    def test_single_movie_request_fetches_title(self, mock_get):
        """Single movie request fetches its title from /movie endpoint."""
        mock_get.return_value = {'title': 'Test Movie'}
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': 12345}
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        mock_get.assert_called_once_with('/movie/12345')
        assert result == {1: ('Test Movie', 0)}

    @patch.object(Seerr, 'get')
    def test_single_tv_request_fetches_title_with_seasons(self, mock_get):
        """Single TV request fetches title and preserves season count."""
        mock_get.return_value = {'title': 'Test Show'}
        requests_list = [{
            'id': 2,
            'type': 'tv',
            'media': {'tmdbId': 67890},
            'seasonCount': 5
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        mock_get.assert_called_once_with('/tv/67890')
        assert result == {2: ('Test Show', 5)}

    @patch.object(Seerr, 'get')
    def test_multiple_requests_fetches_all_in_parallel(self, mock_get):
        """Multiple requests fetch titles for each."""
        def side_effect(url):
            if '/movie/100' in url:
                return {'title': 'Movie A'}
            elif '/tv/200' in url:
                return {'title': 'Show B'}
            elif '/movie/300' in url:
                return {'title': 'Movie C'}
            return {}

        mock_get.side_effect = side_effect
        requests_list = [
            {'id': 1, 'type': 'movie', 'media': {'tmdbId': 100}},
            {'id': 2, 'type': 'tv', 'media': {'tmdbId': 200}, 'seasonCount': 3},
            {'id': 3, 'type': 'movie', 'media': {'tmdbId': 300}},
        ]

        result = self.seerr._fetch_all_titles(requests_list)

        assert mock_get.call_count == 3
        assert result[1] == ('Movie A', 0)
        assert result[2] == ('Show B', 3)
        assert result[3] == ('Movie C', 0)

    @patch.object(Seerr, 'get')
    def test_issue_uses_media_mediatype(self, mock_get):
        """Issues use media.mediaType instead of type field."""
        mock_get.return_value = {'title': 'Issue Title'}
        requests_list = [{
            'id': 1,
            'media': {'tmdbId': 12345, 'mediaType': 'movie'},
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        mock_get.assert_called_once_with('/movie/12345')
        assert result == {1: ('Issue Title', 0)}

    @patch.object(Seerr, 'get')
    def test_fallback_to_imdbid_when_tmdbid_missing(self, mock_get):
        """Falls back to imdbId when tmdbId is not available."""
        mock_get.return_value = {'title': 'IMDB Movie'}
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': None, 'imdbId': 'tt1234567'}
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        mock_get.assert_called_once_with('/movie/tt1234567')
        assert result == {1: ('IMDB Movie', 0)}

    @patch.object(Seerr, 'get')
    def test_fallback_to_tvdbid_when_others_missing(self, mock_get):
        """Falls back to tvdbId when tmdbId and imdbId are not available."""
        mock_get.return_value = {'title': 'TVDB Show'}
        requests_list = [{
            'id': 1,
            'type': 'tv',
            'media': {'tmdbId': None, 'imdbId': None, 'tvdbId': 98765}
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        mock_get.assert_called_once_with('/tv/98765')
        assert result == {1: ('TVDB Show', 0)}

    @patch.object(Seerr, 'get')
    def test_api_failure_returns_media_id_as_fallback(self, mock_get):
        """API failure returns media ID as title fallback."""
        mock_get.return_value = {}  # Empty response
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': 12345}
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        # When API returns empty dict, media_id is used as fallback (as string)
        assert result == {1: ('12345', 0)}

    @patch.object(Seerr, 'get')
    def test_exception_isolation_continues_on_failure(self, mock_get):
        """One failed request doesn't prevent other titles from being fetched."""
        def side_effect(url):
            if '/movie/200' in url:
                raise ConnectionError("Network error")
            return {'title': 'Success Title'}

        mock_get.side_effect = side_effect
        requests_list = [
            {'id': 1, 'type': 'movie', 'media': {'tmdbId': 100}},
            {'id': 2, 'type': 'movie', 'media': {'tmdbId': 200}},  # Will fail
            {'id': 3, 'type': 'movie', 'media': {'tmdbId': 300}},
        ]

        result = self.seerr._fetch_all_titles(requests_list)

        assert mock_get.call_count == 3
        assert result[1] == ('Success Title', 0)
        assert result[2] == ('200', 0)  # Fallback to media_id as string
        assert result[3] == ('Success Title', 0)

    @patch.object(Seerr, 'get')
    def test_custom_max_workers_works(self, mock_get):
        """Verify custom max_workers parameter is accepted and functional."""
        mock_get.return_value = {'title': 'Test'}
        # media IDs: 0, 100, 200, 300, 400
        # ID 0 is skipped by our new logic
        requests_list = [
            {'id': i, 'type': 'movie', 'media': {'tmdbId': i * 100}}
            for i in range(5)
        ]

        result = self.seerr._fetch_all_titles(requests_list, max_workers=2)

        assert len(result) == 5
        # 0 is skipped, so 100, 200, 300, 400 are fetched = 4 calls
        assert mock_get.call_count == 4

    @patch.object(Seerr, 'get')
    def test_deduplication_fetches_once_for_multiple_requests(self, mock_get):
        """Verify that multiple requests for same media only trigger one API call."""
        mock_get.return_value = {'title': 'Shared Title'}
        requests_list = [
            {'id': 1, 'type': 'movie', 'media': {'tmdbId': 123}},
            {'id': 2, 'type': 'movie', 'media': {'tmdbId': 123}},
            {'id': 3, 'type': 'movie', 'media': {'tmdbId': 123}},
        ]

        result = self.seerr._fetch_all_titles(requests_list)

        assert len(result) == 3
        mock_get.assert_called_once_with('/movie/123')
        assert result[1] == ('Shared Title', 0)
        assert result[2] == ('Shared Title', 0)
        assert result[3] == ('Shared Title', 0)

    @patch.object(Seerr, 'get')
    def test_missing_title_in_response_uses_media_id(self, mock_get):
        """When API response lacks 'title' key, falls back to media_id."""
        mock_get.return_value = {'status': 'ok'}  # No 'title' key
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': 99999}
        }]

        result = self.seerr._fetch_all_titles(requests_list)

        assert result == {1: ('99999', 0)}


class TestSkipTitleFetching:
    """Tests for skipping title fetching when detailed=False."""

    def _create_config(self, detailed=False):
        return {
            'url': 'http://test',
            'api_version': 'v1',
            'api_key': 'testkey',
            'alias': 'test',
            'detailed': detailed,
        }

    def _create_mock_metrics(self):
        metrics = MagicMock()
        metrics.LAST_SCRAPE.labels.return_value = MagicMock()
        metrics.SCRAPE_DURATION.labels.return_value = MagicMock()
        return metrics

    @patch.object(Seerr, '_fetch_all_titles')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_requests_skips_titles_when_detailed_false(self, mock_fetch, mock_fetch_titles):
        """When detailed=False, get_requests() does not call _fetch_all_titles()."""
        mock_fetch.return_value = {
            'results': [{
                'id': 1,
                'type': 'movie',
                'createdAt': '2024-01-01T00:00:00Z',
                'status': 2,
                'media': {'status': 5},
            }]
        }
        seerr = Seerr(self._create_config(detailed=False), self._create_mock_metrics(), 'jellyseerr')

        requests = seerr.get_requests()

        mock_fetch_titles.assert_not_called()
        assert requests[0]['title'] == ''

    @patch.object(Seerr, '_fetch_all_titles')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_requests_fetches_titles_when_detailed_true(self, mock_fetch, mock_fetch_titles):
        """When detailed=True, get_requests() calls _fetch_all_titles()."""
        mock_fetch.return_value = {
            'results': [{
                'id': 1,
                'type': 'movie',
                'createdAt': '2024-01-01T00:00:00Z',
                'status': 2,
                'media': {'status': 5},
            }]
        }
        mock_fetch_titles.return_value = {1: ('Test Movie', 0)}
        seerr = Seerr(self._create_config(detailed=True), self._create_mock_metrics(), 'jellyseerr')

        requests = seerr.get_requests()

        mock_fetch_titles.assert_called_once()
        assert requests[0]['title'] == 'Test Movie'

    @patch.object(Seerr, '_fetch_all_titles')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_issues_skips_titles_when_detailed_false(self, mock_fetch, mock_fetch_titles):
        """When detailed=False, get_issues() does not call _fetch_all_titles()."""
        mock_fetch.return_value = {
            'results': [{
                'id': 1,
                'createdAt': '2024-01-01T00:00:00Z',
                'updatedAt': '2024-01-02T00:00:00Z',
                'status': 1,
                'issueType': 1,
                'media': {'mediaType': 'movie'},
            }]
        }
        seerr = Seerr(self._create_config(detailed=False), self._create_mock_metrics(), 'jellyseerr')

        issues = seerr.get_issues()

        mock_fetch_titles.assert_not_called()
        assert issues[0]['title'] == ''

    @patch.object(Seerr, '_fetch_all_titles')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_issues_fetches_titles_when_detailed_true(self, mock_fetch, mock_fetch_titles):
        """When detailed=True, get_issues() calls _fetch_all_titles()."""
        mock_fetch.return_value = {
            'results': [{
                'id': 1,
                'createdAt': '2024-01-01T00:00:00Z',
                'updatedAt': '2024-01-02T00:00:00Z',
                'status': 1,
                'issueType': 1,
                'media': {'mediaType': 'movie'},
            }]
        }
        mock_fetch_titles.return_value = {1: ('Test Movie', 0)}
        seerr = Seerr(self._create_config(detailed=True), self._create_mock_metrics(), 'jellyseerr')

        issues = seerr.get_issues()

        mock_fetch_titles.assert_called_once()
        assert issues[0]['title'] == 'Test Movie'
