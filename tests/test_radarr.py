"""Tests for the N+1 query fix in radarr connector."""

from unittest.mock import patch, MagicMock

from scraparr.connectors.radarr import Module


class TestNormalizeMovieFile:

    def setup_method(self):
        """Create a Module instance for testing."""
        config = {
            'url': 'http://test',
            'api_key': 'key',
            'api_version': 'v3',
            'alias': 'test_radarr',
            'detailed': False
        }
        self.module = Module(config)

    def test_no_file_returns_empty_list(self):
        """Movies without files return empty list."""
        movie = {'id': 1, 'hasFile': False, 'statistics': {'movieFileCount': 0}}
        assert self.module._normalize_movie_file(movie) == []

    def test_single_file_wraps_in_list(self):
        """Single-file movies use embedded data, wrapped in list."""
        embedded = {'quality': {'quality': {'name': 'Bluray-1080p'}}}
        movie = {
            'id': 1,
            'hasFile': True,
            'statistics': {'movieFileCount': 1},
            'movieFile': embedded
        }
        result = self.module._normalize_movie_file(movie)
        assert result == [embedded]

    @patch.object(Module, 'get')
    def test_multi_file_falls_back_to_api(self, mock_get):
        """Multi-file movies make API call."""
        mock_get.return_value = [{'id': 100}, {'id': 101}]
        movie = {'id': 1, 'hasFile': True, 'statistics': {'movieFileCount': 2}}

        result = self.module._normalize_movie_file(movie)

        mock_get.assert_called_once_with('/moviefile?movieId=1')
        assert result == [{'id': 100}, {'id': 101}]

    def test_missing_movie_file_key_returns_empty(self):
        """Defensive: missing movieFile key returns empty list."""
        movie = {'id': 1, 'statistics': {'movieFileCount': 1}}
        result = self.module._normalize_movie_file(movie)
        assert result == []
