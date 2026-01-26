"""Tests for the parallel episode file fetching in sonarr connector."""

from unittest.mock import patch, MagicMock

import requests

from scraparr.connectors.sonarr_api import SonarrApi


class TestFetchAllEpisodeFiles:

    def setup_method(self):
        """Create a SonarrApi instance for testing."""
        config = {
            'url': 'http://test',
            'api_key': 'key',
            'api_version': 'v3',
            'alias': 'test_sonarr',
            'detailed': False
        }
        # Create a mock metrics object
        self.mock_metrics = MagicMock()
        self.api = SonarrApi('sonarr', config, self.mock_metrics)

    def test_empty_series_list_returns_empty_dict(self):
        """Empty series list returns empty dict without making API calls."""
        result = self.api._fetch_all_episode_files([])
        assert result == {}

    @patch.object(SonarrApi, 'get')
    def test_single_series_fetches_episodes(self, mock_get):
        """Single series fetches its episode files."""
        mock_get.return_value = [{'id': 100, 'quality': {'quality': {'name': 'HDTV-720p'}}}]
        series_list = [{'id': 1, 'title': 'Test Show'}]

        result = self.api._fetch_all_episode_files(series_list)

        mock_get.assert_called_once_with('/episodefile?seriesId=1')
        assert result == {1: [{'id': 100, 'quality': {'quality': {'name': 'HDTV-720p'}}}]}

    @patch.object(SonarrApi, 'get')
    def test_multiple_series_fetches_all_in_parallel(self, mock_get):
        """Multiple series fetch episode files for each."""
        def side_effect(url):
            if 'seriesId=1' in url:
                return [{'id': 100}]
            elif 'seriesId=2' in url:
                return [{'id': 200}, {'id': 201}]
            elif 'seriesId=3' in url:
                return []
            return []

        mock_get.side_effect = side_effect
        series_list = [
            {'id': 1, 'title': 'Show A'},
            {'id': 2, 'title': 'Show B'},
            {'id': 3, 'title': 'Show C'},
        ]

        result = self.api._fetch_all_episode_files(series_list)

        assert mock_get.call_count == 3
        assert result[1] == [{'id': 100}]
        assert result[2] == [{'id': 200}, {'id': 201}]
        assert result[3] == []

    @patch.object(SonarrApi, 'get')
    def test_api_failure_returns_empty_dict_for_series(self, mock_get):
        """API failure for a series returns empty dict (get behavior)."""
        mock_get.return_value = {}
        series_list = [{'id': 1, 'title': 'Test Show'}]

        result = self.api._fetch_all_episode_files(series_list)

        assert result == {1: {}}

    @patch.object(SonarrApi, 'get')
    def test_custom_max_workers_works(self, mock_get):
        """Verify custom max_workers parameter is accepted and functional."""
        mock_get.return_value = []
        series_list = [{'id': i, 'title': f'Show {i}'} for i in range(5)]

        # Should not raise any errors with custom max_workers
        result = self.api._fetch_all_episode_files(series_list, max_workers=2)

        # All series should have entries in result
        assert len(result) == 5
        assert mock_get.call_count == 5

    @patch.object(SonarrApi, 'get')
    def test_exception_isolation_continues_on_failure(self, mock_get):
        """One failed request doesn't prevent other series from being fetched."""
        def side_effect(url):
            if 'seriesId=2' in url:
                raise requests.exceptions.ConnectionError("Network error")
            return [{'id': 100}]

        mock_get.side_effect = side_effect
        series_list = [
            {'id': 1, 'title': 'Show A'},
            {'id': 2, 'title': 'Show B'},  # This one will fail
            {'id': 3, 'title': 'Show C'},
        ]

        result = self.api._fetch_all_episode_files(series_list)

        # Series 1 and 3 should succeed, series 2 should have empty list
        assert mock_get.call_count == 3
        assert result[1] == [{'id': 100}]
        assert result[2] == []  # Failed series gets empty list
        assert result[3] == [{'id': 100}]
