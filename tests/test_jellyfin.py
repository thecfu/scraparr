"""Tests for the jellyfin module connection pooling."""

from unittest.mock import MagicMock, patch

import requests

from scraparr.connectors import jellyfin, util


class TestJellyfinUsesSharedSession:
    """Tests that Jellyfin API calls use util's shared session."""

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_api_calls_use_util_session(self, mock_up, mock_get_session):
        """Jellyfin API functions use util._get_session() for connection pooling."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'TotalRecordCount': 5}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_number_of_devices(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        mock_get_session.assert_called_once()
        mock_session.get.assert_called_once_with(
            'http://jellyfin/Devices',
            headers={'Authorization': 'token'},
            timeout=10
        )
        assert result == 5

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_request_exception_returns_none(self, mock_up, mock_get_session):
        """API functions return None on RequestException."""
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_get_session.return_value = mock_session

        result = jellyfin.get_number_of_devices(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        assert result is None
