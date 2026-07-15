"""Tests for exclude filtering feature (issue #161)."""

import pytest


class FakeConnector:
    """Minimal stub to test ConnectorModule.__init__ exclude parsing."""

    def __init__(self, config):
        from scraparr.connectors.module import ConnectorModule
        # Call ConnectorModule.__init__ directly
        ConnectorModule.__init__(self, config, "test_service")


def test_exclude_parsed_as_set():
    config = {
        "url": "http://localhost",
        "api_key": "key",
        "exclude": ["/data/test", "/mnt/archive"],
    }
    connector = FakeConnector(config)
    assert connector.exclude == {"/data/test", "/mnt/archive"}


def test_exclude_defaults_to_empty_set():
    config = {"url": "http://localhost", "api_key": "key"}
    connector = FakeConnector(config)
    assert connector.exclude == set()


def test_exclude_in_service_fields():
    from scraparr.const import SERVICE_FIELDS
    assert "exclude" in SERVICE_FIELDS


from unittest.mock import MagicMock, patch


def make_sonarr_series(title_slug, root_folder, episodes=None, monitored=True,
                       status="continuing", genres=None):
    """Helper to build a fake series dict matching the Sonarr API shape."""
    return {
        "titleSlug": title_slug,
        "rootFolderPath": root_folder,
        "monitored": monitored,
        "status": status,
        "genres": genres or [],
        "episodes": episodes or [],
        "seasons": [],
        "statistics": {
            "episodeCount": 10,
            "episodeFileCount": 8,
            "seasonCount": 1,
            "sizeOnDisk": 1000,
            "percentOfEpisodes": 80.0,
        },
    }


class TestSonarrApiExclude:
    """Tests for SonarrApi.analyse_series exclude filtering."""

    def _make_api(self, exclude=None):
        metrics = MagicMock()
        config = {
            "url": "http://localhost:8989",
            "api_key": "key",
            "api_version": "v3",
            "exclude": exclude or [],
        }
        from scraparr.connectors.sonarr_api import SonarrApi
        api = SonarrApi("sonarr", config, metrics)
        return api, metrics

    def test_excluded_series_not_counted(self):
        api, metrics = self._make_api(exclude=["/data/test"])
        series = [
            make_sonarr_series("show-a", "/data/media"),
            make_sonarr_series("show-b", "/data/test"),
        ]
        api.analyse_series(series)
        # SERIES_COUNT_T should reflect only non-excluded items
        metrics.SERIES_COUNT_T.labels.return_value.set.assert_called_with(1)

    def test_no_exclude_counts_all(self):
        api, metrics = self._make_api(exclude=[])
        series = [
            make_sonarr_series("show-a", "/data/media"),
            make_sonarr_series("show-b", "/data/test"),
        ]
        api.analyse_series(series)
        metrics.SERIES_COUNT_T.labels.return_value.set.assert_called_with(2)

    def test_excluded_series_skips_detailed_metrics(self):
        api, metrics = self._make_api(exclude=["/data/test"])
        api.detailed = True
        series = [
            make_sonarr_series("show-a", "/data/media"),
            make_sonarr_series("show-b", "/data/test"),
        ]
        api.analyse_series(series)
        # show-b should never appear in detailed metric calls
        for call in metrics.SERIES_EPISODE_COUNT.labels.call_args_list:
            assert "show-b" not in call[0], "Excluded series should not appear in detailed metrics"
