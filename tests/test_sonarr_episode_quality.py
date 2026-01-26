"""Tests for episode_quality_stats configuration option."""

import pytest
from unittest.mock import MagicMock, patch, call
from scraparr.connectors.sonarr_api import SonarrApi


class TestEpisodeQualityStatsConfig:
    """Test that episode_quality_stats config is handled correctly."""

    def test_config_missing_defaults_to_true(self, mock_metrics):
        """When episode_quality_stats is not in config, it should default to True."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
        }
        api = SonarrApi("sonarr", config, mock_metrics)
        assert api.episode_quality_stats is True

    def test_config_explicit_false(self, mock_metrics):
        """When episode_quality_stats is explicitly False."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": False,
        }
        api = SonarrApi("sonarr", config, mock_metrics)
        assert api.episode_quality_stats is False

    def test_config_explicit_true(self, mock_metrics):
        """When episode_quality_stats is explicitly True."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": True,
        }
        api = SonarrApi("sonarr", config, mock_metrics)
        assert api.episode_quality_stats is True

    def test_detailed_config_independent(self, mock_metrics):
        """detailed and episode_quality_stats should be independent."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "detailed": True,
            "episode_quality_stats": False,
        }
        api = SonarrApi("sonarr", config, mock_metrics)
        assert api.detailed is True
        assert api.episode_quality_stats is False


class TestGetSeriesEpisodeFileFetching:
    """Test that episodefile API calls are made/skipped based on config."""

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_no_episodefile_calls_when_disabled(
        self, mock_get, mock_up, mock_metrics, sample_series_data
    ):
        """When episode_quality_stats=False, no /episodefile calls should be made."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": False,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        # Mock /series to return sample data
        mock_get.return_value = sample_series_data.copy()

        result = api.get_series()

        # Should only call /series once
        mock_get.assert_called_once_with("/series")

        # All series should have empty episodes list
        for series in result:
            assert series["episodes"] == []

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_episodefile_calls_when_config_missing(
        self, mock_get, mock_up, mock_metrics, sample_series_data, sample_episodefile_data
    ):
        """When episode_quality_stats is missing from config, /episodefile calls should be made (default True)."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        def mock_get_side_effect(endpoint):
            if endpoint == "/series":
                return sample_series_data.copy()
            elif endpoint.startswith("/episodefile?seriesId="):
                series_id = int(endpoint.split("=")[1])
                return sample_episodefile_data.get(series_id, [])
            return {}

        mock_get.side_effect = mock_get_side_effect

        result = api.get_series()

        # Should call /series + /episodefile for each series (default is True)
        assert mock_get.call_count == 3  # 1 series + 2 episodefile calls

        # Verify episodefile calls were made
        calls = mock_get.call_args_list
        assert call("/series") in calls
        assert call("/episodefile?seriesId=1") in calls
        assert call("/episodefile?seriesId=2") in calls

        # Series should have episode data populated
        series_by_id = {s["id"]: s for s in result}
        assert len(series_by_id[1]["episodes"]) == 3
        assert len(series_by_id[2]["episodes"]) == 2

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_episodefile_calls_when_enabled(
        self, mock_get, mock_up, mock_metrics, sample_series_data, sample_episodefile_data
    ):
        """When episode_quality_stats=True, /episodefile calls should be made."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": True,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        def mock_get_side_effect(endpoint):
            if endpoint == "/series":
                return sample_series_data.copy()
            elif endpoint.startswith("/episodefile?seriesId="):
                series_id = int(endpoint.split("=")[1])
                return sample_episodefile_data.get(series_id, [])
            return {}

        mock_get.side_effect = mock_get_side_effect

        result = api.get_series()

        # Should call /series + /episodefile for each series
        assert mock_get.call_count == 3  # 1 series + 2 episodefile calls

        # Verify episodefile calls were made
        calls = mock_get.call_args_list
        assert call("/series") in calls
        assert call("/episodefile?seriesId=1") in calls
        assert call("/episodefile?seriesId=2") in calls

        # Series should have episode data populated
        series_by_id = {s["id"]: s for s in result}
        assert len(series_by_id[1]["episodes"]) == 3
        assert len(series_by_id[2]["episodes"]) == 2


class TestAnalyseSeriesQualityMetrics:
    """Test that quality metrics are set/skipped based on config."""

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_quality_metrics_skipped_when_disabled(
        self, mock_get, mock_up, mock_metrics, sample_series_data
    ):
        """When episode_quality_stats=False, quality metrics should not be set."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": False,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        # Add empty episodes to series data (as get_series would do)
        for series in sample_series_data:
            series["episodes"] = []

        api.analyse_series(sample_series_data)

        # Quality metrics should NOT have labels() called
        mock_metrics.QUALITY_EPISODE_COUNT.labels.assert_not_called()
        mock_metrics.QUALITY_EPISODE_COUNT_T.labels.assert_not_called()

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_quality_metrics_set_when_enabled(
        self, mock_get, mock_up, mock_metrics, sample_series_data, sample_episodefile_data
    ):
        """When episode_quality_stats=True, quality metrics should be set."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": True,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        # Add episode data to series
        for series in sample_series_data:
            series["episodes"] = sample_episodefile_data.get(series["id"], [])

        api.analyse_series(sample_series_data)

        # Quality metrics should have labels() called
        assert mock_metrics.QUALITY_EPISODE_COUNT.labels.called
        assert mock_metrics.QUALITY_EPISODE_COUNT_T.labels.called


class TestDetailedAndEpisodeQualityCombinations:
    """Test all combinations of detailed and episode_quality_stats."""

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_detailed_false_quality_false(
        self, mock_get, mock_up, mock_metrics, sample_series_data
    ):
        """detailed=False, episode_quality_stats=False."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "detailed": False,
            "episode_quality_stats": False,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        for series in sample_series_data:
            series["episodes"] = []

        api.analyse_series(sample_series_data)

        # Per-series detailed metrics should NOT be set
        mock_metrics.SERIES_EPISODE_COUNT.labels.assert_not_called()
        mock_metrics.SERIES_DISK_SIZE.labels.assert_not_called()

        # Quality metrics should NOT be set
        mock_metrics.QUALITY_EPISODE_COUNT.labels.assert_not_called()

        # Aggregate metrics SHOULD still be set
        assert mock_metrics.SERIES_COUNT_T.labels.called

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_detailed_true_quality_false(
        self, mock_get, mock_up, mock_metrics, sample_series_data
    ):
        """detailed=True, episode_quality_stats=False."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "detailed": True,
            "episode_quality_stats": False,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        for series in sample_series_data:
            series["episodes"] = []

        api.analyse_series(sample_series_data)

        # Per-series detailed metrics SHOULD be set
        assert mock_metrics.SERIES_EPISODE_COUNT.labels.called
        assert mock_metrics.SERIES_DISK_SIZE.labels.called

        # Quality metrics should NOT be set
        mock_metrics.QUALITY_EPISODE_COUNT.labels.assert_not_called()

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_detailed_false_quality_true(
        self, mock_get, mock_up, mock_metrics, sample_series_data, sample_episodefile_data
    ):
        """detailed=False, episode_quality_stats=True."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "detailed": False,
            "episode_quality_stats": True,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        for series in sample_series_data:
            series["episodes"] = sample_episodefile_data.get(series["id"], [])

        api.analyse_series(sample_series_data)

        # Per-series detailed metrics should NOT be set
        mock_metrics.SERIES_EPISODE_COUNT.labels.assert_not_called()
        mock_metrics.SERIES_DISK_SIZE.labels.assert_not_called()

        # Quality metrics SHOULD be set
        assert mock_metrics.QUALITY_EPISODE_COUNT.labels.called

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_detailed_true_quality_true(
        self, mock_get, mock_up, mock_metrics, sample_series_data, sample_episodefile_data
    ):
        """detailed=True, episode_quality_stats=True."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "detailed": True,
            "episode_quality_stats": True,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        for series in sample_series_data:
            series["episodes"] = sample_episodefile_data.get(series["id"], [])

        api.analyse_series(sample_series_data)

        # Per-series detailed metrics SHOULD be set
        assert mock_metrics.SERIES_EPISODE_COUNT.labels.called
        assert mock_metrics.SERIES_DISK_SIZE.labels.called

        # Quality metrics SHOULD be set
        assert mock_metrics.QUALITY_EPISODE_COUNT.labels.called


class TestUtilUpdateMediaMetrics:
    """Test util.update_media_metrics handles empty quality_data."""

    def test_empty_quality_data_no_error(self):
        """update_media_metrics should not error when quality_data[0] is empty dict."""
        from scraparr.connectors import util

        mock_gauge = MagicMock()
        mock_gauge.labels.return_value = MagicMock()

        # Simulate the structure passed to update_media_metrics with empty quality_count
        quality_data = [{}, mock_gauge, mock_gauge]  # Empty dict for quality_count
        used_size = [{"total": 1000, "/tv": 1000}, mock_gauge, mock_gauge]
        genre_count = [{"Drama": {"total": 1, "/tv": 1}}, mock_gauge, mock_gauge]
        status_labels = {
            "continuing": {"func": [mock_gauge, mock_gauge], "paths": {"total": 1, "/tv": 1}},
            "upcoming": {"func": [mock_gauge, mock_gauge], "paths": {"total": 0, "/tv": 0}},
            "ended": {"func": [mock_gauge, mock_gauge], "paths": {"total": 0, "/tv": 0}},
            "deleted": {"func": [mock_gauge, mock_gauge], "paths": {"total": 0, "/tv": 0}},
        }
        media_count = {
            "path": {
                "total": {"paths": {"/tv": 1}, "func": mock_gauge},
                "missing": {"paths": {"/tv": 0}, "func": mock_gauge},
                "monitored": {"paths": {"/tv": 1}, "func": mock_gauge},
                "unmonitored": {"paths": {"/tv": 0}, "func": mock_gauge},
                "episode": {"paths": {"/tv": 10}, "func": mock_gauge},
            },
            "total": {
                "missing": [0, mock_gauge],
                "monitored": [1, mock_gauge],
                "unmonitored": [0, mock_gauge],
                "episode": [10, mock_gauge],
            }
        }

        media = [quality_data, used_size, genre_count, status_labels, media_count]

        # Should not raise an exception
        util.update_media_metrics(media, "test-alias")

        # Quality gauge should NOT have labels called (empty dict = no iterations)
        # Only the path/total metrics should have labels called
        quality_gauge_calls = [c for c in mock_gauge.labels.call_args_list
                               if len(c[0]) == 3 and c[0][1] in ["HDTV-1080p", "WEBDL-1080p"]]
        assert len(quality_gauge_calls) == 0

    def test_valid_quality_data_is_processed(self):
        """update_media_metrics should process quality_data when not None."""
        from scraparr.connectors import util

        mock_gauge = MagicMock()
        mock_gauge.labels.return_value = MagicMock()

        quality_count = {"HDTV-1080p": {"total": 5, "/tv": 5}}
        quality_data = [quality_count, mock_gauge, mock_gauge]
        used_size = [{"total": 1000, "/tv": 1000}, mock_gauge, mock_gauge]
        genre_count = [{"Drama": {"total": 1, "/tv": 1}}, mock_gauge, mock_gauge]
        status_labels = {
            "continuing": {"func": [mock_gauge, mock_gauge], "paths": {"total": 1, "/tv": 1}},
            "upcoming": {"func": [mock_gauge, mock_gauge], "paths": {"total": 0, "/tv": 0}},
            "ended": {"func": [mock_gauge, mock_gauge], "paths": {"total": 0, "/tv": 0}},
            "deleted": {"func": [mock_gauge, mock_gauge], "paths": {"total": 0, "/tv": 0}},
        }
        media_count = {
            "path": {
                "total": {"paths": {"/tv": 1}, "func": mock_gauge},
                "missing": {"paths": {"/tv": 0}, "func": mock_gauge},
                "monitored": {"paths": {"/tv": 1}, "func": mock_gauge},
                "unmonitored": {"paths": {"/tv": 0}, "func": mock_gauge},
                "episode": {"paths": {"/tv": 10}, "func": mock_gauge},
            },
            "total": {
                "missing": [0, mock_gauge],
                "monitored": [1, mock_gauge],
                "unmonitored": [0, mock_gauge],
                "episode": [10, mock_gauge],
            }
        }

        media = [quality_data, used_size, genre_count, status_labels, media_count]

        util.update_media_metrics(media, "test-alias")

        # Quality gauge should have been called with the quality label
        # The total_with_label function iterates over quality_count
        assert mock_gauge.labels.called


class TestEmptySeriesResponse:
    """Test handling of empty /series response."""

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_empty_series_response(self, mock_get, mock_up, mock_metrics):
        """Empty /series response should be handled gracefully."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": True,  # Even with this enabled
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        mock_get.return_value = {}  # Empty response

        result = api.get_series()

        # Should handle gracefully
        assert result == {}
        mock_up.labels.return_value.set.assert_called_with(0)

    @patch("scraparr.connectors.sonarr_api.UP")
    @patch.object(SonarrApi, "get")
    def test_empty_series_list(self, mock_get, mock_up, mock_metrics):
        """Empty series list should be handled gracefully."""
        config = {
            "url": "http://localhost:8989",
            "api_key": "test-key",
            "api_version": "v3",
            "episode_quality_stats": True,
        }
        api = SonarrApi("sonarr", config, mock_metrics)

        mock_get.return_value = []  # Empty list

        result = api.get_series()

        # Should return empty list, not crash
        assert result == []
