"""Tests for skipping title fetching when detailed=False in seerr connector."""

from unittest.mock import patch, MagicMock

from scraparr.connectors.seerr import Seerr


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

    @patch.object(Seerr, 'get_title')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_requests_skips_title_when_detailed_false(self, mock_fetch, mock_get_title):
        """When detailed=False, get_requests() does not call get_title()."""
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

        mock_get_title.assert_not_called()
        assert requests[0]['title'] == ''

    @patch.object(Seerr, 'get_title')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_requests_fetches_title_when_detailed_true(self, mock_fetch, mock_get_title):
        """When detailed=True, get_requests() calls get_title()."""
        mock_fetch.return_value = {
            'results': [{
                'id': 1,
                'type': 'movie',
                'createdAt': '2024-01-01T00:00:00Z',
                'status': 2,
                'media': {'status': 5},
            }]
        }
        mock_get_title.return_value = ('Test Movie', 0)
        seerr = Seerr(self._create_config(detailed=True), self._create_mock_metrics(), 'jellyseerr')

        requests = seerr.get_requests()

        mock_get_title.assert_called_once()
        assert requests[0]['title'] == 'Test Movie'

    @patch.object(Seerr, 'get_title')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_issues_skips_title_when_detailed_false(self, mock_fetch, mock_get_title):
        """When detailed=False, get_issues() does not call get_title()."""
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

        mock_get_title.assert_not_called()
        assert issues[0]['title'] == ''

    @patch.object(Seerr, 'get_title')
    @patch.object(Seerr, 'fetch_paginated_results')
    def test_get_issues_fetches_title_when_detailed_true(self, mock_fetch, mock_get_title):
        """When detailed=True, get_issues() calls get_title()."""
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
        mock_get_title.return_value = ('Test Movie', 0)
        seerr = Seerr(self._create_config(detailed=True), self._create_mock_metrics(), 'jellyseerr')

        issues = seerr.get_issues()

        mock_get_title.assert_called_once()
        assert issues[0]['title'] == 'Test Movie'
