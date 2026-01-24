"""Tests for the N+1 query fix in radarr connector."""

from unittest.mock import patch

from scraparr.connectors.radarr import _normalize_movie_file


class TestNormalizeMovieFile:

    def test_no_file_returns_empty_list(self):
        """Movies without files return empty list."""
        movie = {'id': 1, 'hasFile': False, 'statistics': {'movieFileCount': 0}}
        assert _normalize_movie_file(movie, 'http://test', 'key', 'v3') == []

    def test_single_file_wraps_in_list(self):
        """Single-file movies use embedded data, wrapped in list."""
        embedded = {'quality': {'quality': {'name': 'Bluray-1080p'}}}
        movie = {
            'id': 1,
            'hasFile': True,
            'statistics': {'movieFileCount': 1},
            'movieFile': embedded
        }
        result = _normalize_movie_file(movie, 'http://test', 'key', 'v3')
        assert result == [embedded]

    @patch('scraparr.connectors.radarr.util.get')
    def test_multi_file_falls_back_to_api(self, mock_get):
        """Multi-file movies make API call."""
        mock_get.return_value = [{'id': 100}, {'id': 101}]
        movie = {'id': 1, 'hasFile': True, 'statistics': {'movieFileCount': 2}}

        result = _normalize_movie_file(movie, 'http://test', 'key', 'v3')

        mock_get.assert_called_once_with('http://test/api/v3/moviefile?movieId=1', 'key')
        assert result == [{'id': 100}, {'id': 101}]

    def test_missing_movie_file_key_returns_empty(self):
        """Defensive: missing movieFile key returns empty list."""
        movie = {'id': 1, 'statistics': {'movieFileCount': 1}}
        result = _normalize_movie_file(movie, 'http://test', 'key', 'v3')
        assert result == []
