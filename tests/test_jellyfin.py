"""Tests for the jellyfin module connection pooling."""

from unittest.mock import MagicMock, patch

import requests

from scraparr.connectors import jellyfin
from scraparr.connectors.jellyfin import Module


@patch('scraparr.connectors.jellyfin.jellyfin_metrics')
@patch('scraparr.connectors.jellyfin.util')
class TestUpdateMetrics:
    """Tests for update_metrics correctness."""

    def setup_method(self):
        config = {
            'url': 'http://jellyfin',
            'api_key': 'test-token',
            'alias': 'test_jellyfin',
            'detailed': False,
            'within': 300,
        }
        self.module = Module(config)

    def test_number_of_users_uses_n_user(self, mock_util, mock_metrics):
        """NUMBER_OF_USERS must be set from n_user, not n_devices."""
        data = {
            "n_devices": 10,
            "n_user": 3,
            "n_movies": 100,
            "n_series": 50,
            "genres": {"Action": {"total": 1}},
            "sessions": [],
            "infos": {"Version": "10.9.0", "HasUpdateAvailable": False},
        }
        self.module.update_metrics(data)
        mock_metrics.NUMBER_OF_USERS.labels('test_jellyfin').set.assert_called_with(3)


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

    def test_session_details_defaults_false(self):
        """session_details defaults to False when not in config."""
        assert self.module.session_details is False

    def test_client_info_defaults_false(self):
        """client_info defaults to False when not in config."""
        assert self.module.client_info is False

    def test_session_details_reads_config(self):
        """session_details reads from config when set."""
        config = {
            'url': 'http://jellyfin',
            'api_key': 'test-token',
            'alias': 'test_jellyfin',
            'detailed': False,
            'within': 300,
            'session_details': True,
        }
        module = Module(config)
        assert module.session_details is True
