"""Tests for the jellyfin module connection pooling."""

from unittest.mock import MagicMock, patch

import requests

from scraparr.connectors import jellyfin, util


class TestJellyfinApiCalls:
    """Tests for Jellyfin API calls using session-based requests."""

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_number_of_devices_uses_session(self, mock_up, mock_get_session):
        """get_number_of_devices() uses util's shared session."""
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
    def test_get_genres_uses_session(self, mock_up, mock_get_session):
        """get_genres() uses util's shared session."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'Items': [{'Name': 'Action'}, {'Name': 'Drama'}]}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_genres(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        mock_get_session.assert_called_once()
        assert 'Action' in result
        assert 'Drama' in result

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_number_of_user_uses_session(self, mock_up, mock_get_session):
        """get_number_of_user() uses util's shared session."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [{'Id': '1'}, {'Id': '2'}]
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_number_of_user(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        mock_get_session.assert_called_once()
        assert result == 2

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_number_of_movies_uses_session(self, mock_up, mock_get_session):
        """get_number_of_movies() uses util's shared session."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'TotalRecordCount': 100}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_number_of_movies(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        mock_get_session.assert_called_once()
        assert result == 100

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_number_of_series_uses_session(self, mock_up, mock_get_session):
        """get_number_of_series() uses util's shared session."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'TotalRecordCount': 50}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_number_of_series(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        mock_get_session.assert_called_once()
        assert result == 50

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_infos_uses_session(self, mock_up, mock_get_session):
        """get_infos() uses util's shared session."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'Version': '10.8.0'}
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_infos(
            'http://jellyfin', {'Authorization': 'token'}, 'alias'
        )

        mock_get_session.assert_called_once()
        mock_session.get.assert_called_once_with(
            'http://jellyfin/System/Info',
            headers={'Authorization': 'token'},
            timeout=10
        )
        assert result == {'Version': '10.8.0'}

    @patch.object(util, '_get_session')
    @patch('scraparr.connectors.jellyfin.UP')
    def test_get_sessions_uses_session(self, mock_up, mock_get_session):
        """get_sessions() uses util's shared session."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = [{'UserId': '1', 'UserName': 'test'}]
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = jellyfin.get_sessions(
            'http://jellyfin', {'Authorization': 'token'}, 'alias', 300
        )

        mock_get_session.assert_called_once()
        mock_session.get.assert_called_once_with(
            'http://jellyfin/Sessions?activeWithinSeconds=300',
            headers={'Authorization': 'token'},
            timeout=10
        )
        assert len(result) == 1

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
        mock_up.labels.assert_called_with('alias', 'jellyfin')
