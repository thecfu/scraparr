"""Tests for the jellyfin module connection pooling."""

from unittest.mock import MagicMock, patch

import requests

from scraparr.connectors import jellyfin
from scraparr.connectors.jellyfin import Module


class TestJellyfinUsesSharedSession:
    """Tests that Jellyfin API calls use module's shared session."""

    def setup_method(self):
        """Create a Module instance for testing."""
        config = {
            'url': 'http://jellyfin',
            'api_key': 'test-token',
            'alias': 'test_jellyfin',
            'detailed': False,
            'within': 300,
        }
        self.module = Module(config)
        self.module.get_header()

    @patch.object(jellyfin, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_number_of_devices_uses_session(self, mock_up, mock_get_session):
        """get_number_of_devices() uses _get_session() for connection pooling."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'TotalRecordCount': 5}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = self.module.get_number_of_devices()

        mock_get_session.assert_called_once()
        mock_session.get.assert_called_once_with(
            'http://jellyfin/Devices',
            headers={'Authorization': 'Mediabrowser Token=test-token'},
            timeout=10
        )
        assert result == 5

    @patch.object(jellyfin, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_request_exception_returns_none(self, mock_up, mock_get_session):
        """API functions return None on RequestException."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_get_session.return_value = mock_session

        result = self.module.get_number_of_devices()

        assert result is None

    @patch.object(jellyfin, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_genres_uses_session(self, mock_up, mock_get_session):
        """get_genres() uses _get_session() for connection pooling."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'Items': [{'Name': 'Action'}]}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = self.module.get_genres()

        mock_get_session.assert_called_once()
        assert 'Action' in result
