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

    def test_parse_bare_zero(self):
        assert _parse_size("0") == 0.0

    def test_parse_short_unit_gigabytes(self):
        assert _parse_size("11.6 G") == 11.6 * 1024 ** 3

    def test_parse_short_unit_terabytes(self):
        assert _parse_size("154.4 T") == 154.4 * 1024 ** 4

    def test_parse_malformed_returns_zero(self):
        assert _parse_size("invalid") == 0.0

    def test_parse_empty_returns_zero(self):
        assert _parse_size("") == 0.0


class TestSabnzbdScrape:

    QUEUE_RESP = {"queue": {
        "status": "Downloading", "kbpersec": "1024.0",
        "mb": "500.0", "mbleft": "250.0", "paused_all": False,
        "diskspace1": "100.0", "diskspacetotal1": "500.0", "noofslots": 3
    }}
    HISTORY_RESP = {"history": {
        "day_size": "1.5 GB", "week_size": "10.2 GB",
        "month_size": "50.0 GB", "total_size": "2.3 TB",
        "noofslots": 100, "slots": []
    }}
    SERVER_STATS_RESP = {"server_stats": {"servers": {
        "news.example.com": {
            "day": 1000000, "week": 7000000,
            "month": 30000000, "total": 365000000,
            "articles_tried": 10000, "articles_success": 9800
        }
    }}}
    FAILED_RESP = {"history": {"noofslots": 5}}

    def setup_method(self):
        self.config = {
            'url': 'http://localhost:8080',
            'api_key': 'testkey',
            'alias': 'test_sabnzbd',
        }
        self.module = Module(self.config)

    @patch.object(Module, 'get')
    def test_scrape_returns_combined_dict(self, mock_get):
        mock_get.side_effect = [
            self.QUEUE_RESP, self.HISTORY_RESP,
            self.SERVER_STATS_RESP, self.FAILED_RESP,
        ]
        result = self.module.scrape()
        assert result["queue"] == self.QUEUE_RESP["queue"]
        assert result["history"] == self.HISTORY_RESP["history"]
        assert result["server_stats"] == self.SERVER_STATS_RESP["server_stats"]
        assert result["failed_count"] == 5

    @patch.object(Module, 'get')
    def test_scrape_fails_on_empty_queue(self, mock_get):
        mock_get.side_effect = [
            {}, self.HISTORY_RESP, self.SERVER_STATS_RESP, self.FAILED_RESP,
        ]
        assert self.module.scrape() == {}

    @patch.object(Module, 'get')
    def test_scrape_fails_on_empty_history(self, mock_get):
        mock_get.side_effect = [
            self.QUEUE_RESP, {}, self.SERVER_STATS_RESP, self.FAILED_RESP,
        ]
        assert self.module.scrape() == {}

    @patch.object(Module, 'get')
    def test_scrape_fails_on_empty_server_stats(self, mock_get):
        mock_get.side_effect = [
            self.QUEUE_RESP, self.HISTORY_RESP, {}, self.FAILED_RESP,
        ]
        assert self.module.scrape() == {}

    @patch.object(Module, 'get')
    def test_scrape_sets_up_gauge_on_success(self, mock_get):
        mock_get.side_effect = [
            self.QUEUE_RESP, self.HISTORY_RESP,
            self.SERVER_STATS_RESP, self.FAILED_RESP,
        ]
        with patch('scraparr.connectors.sabnzbd.UP') as mock_up:
            self.module.scrape()
            mock_up.labels.assert_called_with('test_sabnzbd', 'sabnzbd')
            mock_up.labels.return_value.set.assert_called_with(1)

    @patch.object(Module, 'get')
    def test_scrape_sets_up_gauge_to_zero_on_failure(self, mock_get):
        mock_get.side_effect = [{}, {}, {}, {}]
        with patch('scraparr.connectors.sabnzbd.UP') as mock_up:
            self.module.scrape()
            mock_up.labels.return_value.set.assert_called_with(0)

    @patch.object(Module, 'get')
    def test_scrape_sets_last_scrape_on_success(self, mock_get):
        mock_get.side_effect = [
            self.QUEUE_RESP, self.HISTORY_RESP,
            self.SERVER_STATS_RESP, self.FAILED_RESP,
        ]
        with patch('scraparr.connectors.sabnzbd.sabnzbd_metrics.LAST_SCRAPE') as mock_last_scrape:
            self.module.scrape()
            mock_last_scrape.labels.assert_called_with('test_sabnzbd')
            mock_last_scrape.labels.return_value.set.assert_called_once()
            # Verify that the set call was made with a numeric value
            call_args = mock_last_scrape.labels.return_value.set.call_args
            assert call_args is not None
            assert isinstance(call_args[0][0], (int, float))

    @patch.object(Module, 'get')
    def test_scrape_sets_scrape_duration_on_success(self, mock_get):
        mock_get.side_effect = [
            self.QUEUE_RESP, self.HISTORY_RESP,
            self.SERVER_STATS_RESP, self.FAILED_RESP,
        ]
        with patch('scraparr.connectors.sabnzbd.sabnzbd_metrics.SCRAPE_DURATION') as mock_duration:
            self.module.scrape()
            mock_duration.labels.assert_called_with('test_sabnzbd')
            mock_duration.labels.return_value.set.assert_called_once()
            # Verify that the set call was made with a value >= 0
            call_args = mock_duration.labels.return_value.set.call_args
            assert call_args is not None
            assert call_args[0][0] >= 0


class TestSabnzbdUpdateMetrics:

    def setup_method(self):
        self.module = Module({
            'url': 'http://localhost:8080',
            'api_key': 'key',
            'alias': 'test',
        })

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_queue_speed_converted_to_bytes(self, mock_metrics):
        self.module._update_queue({
            "kbpersec": "1024.0", "mb": "0", "mbleft": "0",
            "paused_all": False, "diskspace1": "0",
            "diskspacetotal1": "0", "noofslots": 0
        })
        mock_metrics.QUEUE_SPEED.labels.return_value.set.assert_called_with(1024.0 * 1024)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_queue_size_converted_to_bytes(self, mock_metrics):
        self.module._update_queue({
            "kbpersec": "0", "mb": "500.0", "mbleft": "250.0",
            "paused_all": False, "diskspace1": "0",
            "diskspacetotal1": "0", "noofslots": 0
        })
        mock_metrics.QUEUE_SIZE.labels.return_value.set.assert_called_with(500.0 * 1024 * 1024)
        mock_metrics.QUEUE_REMAINING.labels.return_value.set.assert_called_with(250.0 * 1024 * 1024)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_queue_paused_true_sets_one(self, mock_metrics):
        self.module._update_queue({
            "kbpersec": "0", "mb": "0", "mbleft": "0",
            "paused_all": True, "diskspace1": "0",
            "diskspacetotal1": "0", "noofslots": 0
        })
        mock_metrics.QUEUE_PAUSED.labels.return_value.set.assert_called_with(1)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_queue_disk_space_converted_to_bytes(self, mock_metrics):
        self.module._update_queue({
            "kbpersec": "0", "mb": "0", "mbleft": "0",
            "paused_all": False, "diskspace1": "100.0",
            "diskspacetotal1": "500.0", "noofslots": 0
        })
        mock_metrics.DISK_SPACE.labels.return_value.set.assert_called_with(
            100.0 * 1024 * 1024 * 1024
        )
        mock_metrics.DISK_SPACE_TOTAL.labels.return_value.set.assert_called_with(
            500.0 * 1024 * 1024 * 1024
        )

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_history_size_strings_parsed_to_bytes(self, mock_metrics):
        self.module._update_history(
            {
                "day_size": "1.5 GB", "week_size": "10.0 GB",
                "month_size": "50.0 GB", "total_size": "2.0 TB",
            },
            failed_count=7
        )
        mock_metrics.HISTORY_DAY.labels.return_value.set.assert_called_with(1.5 * 1024 ** 3)
        mock_metrics.HISTORY_TOTAL.labels.return_value.set.assert_called_with(2.0 * 1024 ** 4)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_history_failed_count_set(self, mock_metrics):
        self.module._update_history(
            {"day_size": "0 B", "week_size": "0 B", "month_size": "0 B", "total_size": "0 B"},
            failed_count=12
        )
        mock_metrics.HISTORY_FAILED.labels.return_value.set.assert_called_with(12)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_server_stats_labeled_by_server_name(self, mock_metrics):
        self.module._update_server_stats({"servers": {
            "news.example.com": {
                "day": 1000000, "week": 7000000,
                "month": 30000000, "total": 365000000,
                "articles_tried": 10000, "articles_success": 9800,
            }
        }})
        mock_metrics.SERVER_TOTAL.labels.assert_called_with('test', 'news.example.com')
        mock_metrics.SERVER_TOTAL.labels.return_value.set.assert_called_with(365000000)
        mock_metrics.SERVER_TRIED.labels.return_value.set.assert_called_with(10000)
        mock_metrics.SERVER_SUCCESS.labels.return_value.set.assert_called_with(9800)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_server_stats_articles_as_daily_dicts(self, mock_metrics):
        """SABnzbd returns articles_tried/success as date-keyed dicts, not integers."""
        self.module._update_server_stats({"servers": {
            "news.example.com": {
                "day": 0, "week": 0, "month": 0, "total": 0,
                "articles_tried": {"2026-07-15": 6126, "2026-07-16": 2212, "2026-07-17": 0},
                "articles_success": {"2026-07-15": 0, "2026-07-16": 0, "2026-07-17": 0},
            }
        }})
        mock_metrics.SERVER_TRIED.labels.return_value.set.assert_called_with(8338)
        mock_metrics.SERVER_SUCCESS.labels.return_value.set.assert_called_with(0)

    @patch('scraparr.connectors.sabnzbd.sabnzbd_metrics')
    def test_clear_removes_per_server_labels(self, mock_metrics):
        self.module.clear()
        for gauge_name in ('SERVER_TOTAL', 'SERVER_DAY', 'SERVER_WEEK',
                           'SERVER_MONTH', 'SERVER_TRIED', 'SERVER_SUCCESS'):
            getattr(mock_metrics, gauge_name).remove_by_labels.assert_called_with(
                {"alias": "test"}
            )
