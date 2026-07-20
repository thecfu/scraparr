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


@patch('scraparr.connectors.jellyfin.jellyfin_metrics')
class TestUpdateSessionDetails:
    """Tests for session_details metric updates."""

    def _make_module(self, session_details=True, client_info=False):
        config = {
            'url': 'http://jellyfin',
            'api_key': 'test-token',
            'alias': 'test_jellyfin',
            'detailed': False,
            'within': 300,
            'session_details': session_details,
            'client_info': client_info,
        }
        return Module(config)

    def _make_session(self, **overrides):
        session = {
            'UserName': 'alice',
            'DeviceName': 'Living Room TV',
            'Client': 'Jellyfin Web',
            'ApplicationVersion': '10.9.0',
            'NowPlayingItem': {
                'Type': 'Episode',
                'RunTimeTicks': 36000000000,
            },
            'PlayState': {
                'PositionTicks': 9000000000,
                'IsPaused': False,
                'PlayMethod': 'DirectPlay',
            },
        }
        session.update(overrides)
        return session

    def test_sets_position_seconds(self, mock_metrics):
        """Position is converted from ticks to seconds."""
        module = self._make_module()
        session = self._make_session()
        module.update_session_details([session])
        mock_metrics.SESSION_POSITION.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', 'Episode', 'DirectPlay',
        ).set.assert_called_with(900.0)

    def test_sets_duration_seconds(self, mock_metrics):
        """Duration is converted from ticks to seconds."""
        module = self._make_module()
        session = self._make_session()
        module.update_session_details([session])
        mock_metrics.SESSION_DURATION.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', 'Episode', 'DirectPlay',
        ).set.assert_called_with(3600.0)

    def test_sets_transcoding_flag(self, mock_metrics):
        """Transcoding gauge is 1 when PlayMethod is Transcode."""
        module = self._make_module()
        session = self._make_session()
        session['PlayState']['PlayMethod'] = 'Transcode'
        session['TranscodingInfo'] = {'Bitrate': 5000000}
        module.update_session_details([session])
        mock_metrics.SESSION_TRANSCODING.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', 'Episode', 'Transcode',
        ).set.assert_called_with(1)

    def test_sets_paused_flag(self, mock_metrics):
        """Paused gauge is 1 when IsPaused is True."""
        module = self._make_module()
        session = self._make_session()
        session['PlayState']['IsPaused'] = True
        module.update_session_details([session])
        mock_metrics.SESSION_PAUSED.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', 'Episode', 'DirectPlay',
        ).set.assert_called_with(1)

    def test_sets_bitrate_from_transcoding_info(self, mock_metrics):
        """Bitrate is read from TranscodingInfo when present."""
        module = self._make_module()
        session = self._make_session()
        session['PlayState']['PlayMethod'] = 'Transcode'
        session['TranscodingInfo'] = {'Bitrate': 8000000}
        module.update_session_details([session])
        mock_metrics.SESSION_BITRATE.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', 'Episode', 'Transcode',
        ).set.assert_called_with(8000000)

    def test_bitrate_zero_for_direct_play(self, mock_metrics):
        """Bitrate is 0 when no TranscodingInfo is present."""
        module = self._make_module()
        session = self._make_session()
        module.update_session_details([session])
        mock_metrics.SESSION_BITRATE.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', 'Episode', 'DirectPlay',
        ).set.assert_called_with(0)

    def test_skips_sessions_without_now_playing(self, mock_metrics):
        """Sessions without NowPlayingItem are ignored."""
        module = self._make_module()
        session = self._make_session()
        del session['NowPlayingItem']
        module.update_session_details([session])
        mock_metrics.SESSION_POSITION.labels.assert_not_called()

    def test_disabled_does_nothing(self, mock_metrics):
        """No metrics set when session_details is False."""
        module = self._make_module(session_details=False)
        session = self._make_session()
        module.update_session_details([session])
        mock_metrics.SESSION_POSITION.labels.assert_not_called()

    def test_client_info_gauge_set(self, mock_metrics):
        """Client info gauge is set when client_info is True."""
        module = self._make_module(client_info=True)
        session = self._make_session()
        module.update_session_details([session])
        mock_metrics.SESSION_CLIENT_INFO.labels(
            'test_jellyfin', 'alice', 'Living Room TV',
            'Jellyfin Web', '10.9.0',
        ).set.assert_called_with(1)

    def test_client_info_disabled_by_default(self, mock_metrics):
        """Client info gauge is not set when client_info is False."""
        module = self._make_module(client_info=False)
        session = self._make_session()
        module.update_session_details([session])
        mock_metrics.SESSION_CLIENT_INFO.labels.assert_not_called()
