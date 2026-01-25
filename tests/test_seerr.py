"""Tests for the parallel title fetching in seerr connector."""

from unittest.mock import patch

from scraparr.connectors.seerr import _fetch_all_titles


class TestFetchAllTitles:

    def test_empty_list_returns_empty_dict(self):
        """Empty requests list returns empty dict without making API calls."""
        result = _fetch_all_titles([], 'http://test/api/v1', 'key')
        assert result == {}

    @patch('scraparr.connectors.seerr.get')
    def test_single_movie_request_fetches_title(self, mock_get):
        """Single movie request fetches its title from /movie endpoint."""
        mock_get.return_value = {'title': 'Test Movie'}
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': 12345}
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        mock_get.assert_called_once_with('http://test/api/v1/movie/12345', 'key')
        assert result == {1: ('Test Movie', 0)}

    @patch('scraparr.connectors.seerr.get')
    def test_single_tv_request_fetches_title_with_seasons(self, mock_get):
        """Single TV request fetches title and preserves season count."""
        mock_get.return_value = {'title': 'Test Show'}
        requests_list = [{
            'id': 2,
            'type': 'tv',
            'media': {'tmdbId': 67890},
            'seasonCount': 5
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        mock_get.assert_called_once_with('http://test/api/v1/tv/67890', 'key')
        assert result == {2: ('Test Show', 5)}

    @patch('scraparr.connectors.seerr.get')
    def test_multiple_requests_fetches_all_in_parallel(self, mock_get):
        """Multiple requests fetch titles for each."""
        def side_effect(url, _api_key):
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

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        assert mock_get.call_count == 3
        assert result[1] == ('Movie A', 0)
        assert result[2] == ('Show B', 3)
        assert result[3] == ('Movie C', 0)

    @patch('scraparr.connectors.seerr.get')
    def test_issue_uses_media_mediatype(self, mock_get):
        """Issues use media.mediaType instead of type field."""
        mock_get.return_value = {'title': 'Issue Title'}
        requests_list = [{
            'id': 1,
            'media': {'tmdbId': 12345, 'mediaType': 'movie'},
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        mock_get.assert_called_once_with('http://test/api/v1/movie/12345', 'key')
        assert result == {1: ('Issue Title', 0)}

    @patch('scraparr.connectors.seerr.get')
    def test_fallback_to_imdbid_when_tmdbid_missing(self, mock_get):
        """Falls back to imdbId when tmdbId is not available."""
        mock_get.return_value = {'title': 'IMDB Movie'}
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': None, 'imdbId': 'tt1234567'}
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        mock_get.assert_called_once_with('http://test/api/v1/movie/tt1234567', 'key')
        assert result == {1: ('IMDB Movie', 0)}

    @patch('scraparr.connectors.seerr.get')
    def test_fallback_to_tvdbid_when_others_missing(self, mock_get):
        """Falls back to tvdbId when tmdbId and imdbId are not available."""
        mock_get.return_value = {'title': 'TVDB Show'}
        requests_list = [{
            'id': 1,
            'type': 'tv',
            'media': {'tmdbId': None, 'imdbId': None, 'tvdbId': 98765}
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        mock_get.assert_called_once_with('http://test/api/v1/tv/98765', 'key')
        assert result == {1: ('TVDB Show', 0)}

    @patch('scraparr.connectors.seerr.get')
    def test_api_failure_returns_media_id_as_fallback(self, mock_get):
        """API failure returns media ID as title fallback."""
        mock_get.return_value = {}  # Empty response
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': 12345}
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        # When API returns empty dict, media_id is used as fallback
        assert result == {1: (12345, 0)}

    @patch('scraparr.connectors.seerr.get')
    def test_exception_isolation_continues_on_failure(self, mock_get):
        """One failed request doesn't prevent other titles from being fetched."""
        def side_effect(url, _api_key):
            if '/movie/200' in url:
                raise ConnectionError("Network error")
            return {'title': 'Success Title'}

        mock_get.side_effect = side_effect
        requests_list = [
            {'id': 1, 'type': 'movie', 'media': {'tmdbId': 100}},
            {'id': 2, 'type': 'movie', 'media': {'tmdbId': 200}},  # Will fail
            {'id': 3, 'type': 'movie', 'media': {'tmdbId': 300}},
        ]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        assert mock_get.call_count == 3
        assert result[1] == ('Success Title', 0)
        assert result[2] == ('200', 0)  # Fallback to media_id as string
        assert result[3] == ('Success Title', 0)

    @patch('scraparr.connectors.seerr.get')
    def test_custom_max_workers_works(self, mock_get):
        """Verify custom max_workers parameter is accepted and functional."""
        mock_get.return_value = {'title': 'Test'}
        requests_list = [
            {'id': i, 'type': 'movie', 'media': {'tmdbId': i * 100}}
            for i in range(5)
        ]

        result = _fetch_all_titles(
            requests_list, 'http://test/api/v1', 'key', max_workers=2
        )

        assert len(result) == 5
        assert mock_get.call_count == 5

    @patch('scraparr.connectors.seerr.get')
    def test_missing_title_in_response_uses_media_id(self, mock_get):
        """When API response lacks 'title' key, falls back to media_id."""
        mock_get.return_value = {'status': 'ok'}  # No 'title' key
        requests_list = [{
            'id': 1,
            'type': 'movie',
            'media': {'tmdbId': 99999}
        }]

        result = _fetch_all_titles(requests_list, 'http://test/api/v1', 'key')

        assert result == {1: (99999, 0)}
