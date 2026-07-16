"""Tests for the SABnzbd connector."""
import requests
from unittest.mock import patch, MagicMock

import scraparr.metrics.sabnzbd as sabnzbd_metrics


class TestSabnzbdMetrics:
    def test_metrics_module_importable(self):
        assert hasattr(sabnzbd_metrics, 'QUEUE_SPEED')
        assert hasattr(sabnzbd_metrics, 'SERVER_TOTAL')
        assert hasattr(sabnzbd_metrics, 'HISTORY_FAILED')
