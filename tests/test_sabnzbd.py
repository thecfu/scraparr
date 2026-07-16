"""Tests for the SABnzbd connector."""
import requests
from unittest.mock import patch, MagicMock

import scraparr.metrics.sabnzbd as sabnzbd_metrics
from scraparr.connectors.sabnzbd import Module, _parse_size


class TestSabnzbdMetrics:
    def test_metrics_module_importable(self):
        assert hasattr(sabnzbd_metrics, 'QUEUE_SPEED')
        assert hasattr(sabnzbd_metrics, 'SERVER_TOTAL')
        assert hasattr(sabnzbd_metrics, 'HISTORY_FAILED')


class TestSabnzbdGet:

    def setup_method(self):
        self.config = {
            'url': 'http://localhost:8080',
            'api_key': 'testkey',
            'alias': 'test_sabnzbd',
        }

    @patch('scraparr.connectors.sabnzbd._get_session')
    def test_get_builds_correct_url(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"queue": {"status": "Downloading"}}
        mock_session.get.return_value = mock_response

        module = Module(self.config)
        result = module.get("queue")

        mock_session.get.assert_called_once_with(
            'http://localhost:8080/api',
            params={'output': 'json', 'mode': 'queue', 'apikey': 'testkey'},
            timeout=20
        )
        assert result == {"queue": {"status": "Downloading"}}

    @patch('scraparr.connectors.sabnzbd._get_session')
    def test_get_passes_extra_params(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        module = Module(self.config)
        module.get("history", failed_only=1, limit=0)

        mock_session.get.assert_called_once_with(
            'http://localhost:8080/api',
            params={'output': 'json', 'mode': 'history', 'apikey': 'testkey',
                    'failed_only': 1, 'limit': 0},
            timeout=20
        )

    @patch('scraparr.connectors.sabnzbd._get_session')
    def test_get_returns_empty_dict_on_401(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response

        module = Module(self.config)
        assert module.get("queue") == {}

    @patch('scraparr.connectors.sabnzbd._get_session')
    def test_get_returns_empty_dict_on_connection_error(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.get.side_effect = requests.exceptions.ConnectionError("refused")

        module = Module(self.config)
        assert module.get("queue") == {}


class TestParseSabnzbdSize:

    def test_parse_gigabytes(self):
        assert _parse_size("1.5 GB") == 1.5 * 1024 ** 3

    def test_parse_terabytes(self):
        assert _parse_size("2.3 TB") == 2.3 * 1024 ** 4

    def test_parse_megabytes(self):
        assert _parse_size("500 MB") == 500 * 1024 ** 2

    def test_parse_zero_bytes(self):
        assert _parse_size("0 B") == 0.0

    def test_parse_malformed_returns_zero(self):
        assert _parse_size("invalid") == 0.0

    def test_parse_empty_returns_zero(self):
        assert _parse_size("") == 0.0
