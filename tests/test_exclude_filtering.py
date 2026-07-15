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


def make_radarr_movie(title, root_folder, monitored=True, status="released",
                      genres=None, has_file=True):
    """Helper to build a fake movie dict matching the Radarr API shape."""
    return {
        "title": title,
        "rootFolderPath": root_folder,
        "monitored": monitored,
        "hasFile": has_file,
        "status": status,
        "genres": genres or [],
        "movieFile": [],
        "statistics": {
            "movieFileCount": 1 if has_file else 0,
            "sizeOnDisk": 2000,
        },
    }


class TestRadarrExclude:
    """Tests for Radarr.analyse_movies exclude filtering."""

    def _make_module(self, exclude=None):
        config = {
            "url": "http://localhost:7878",
            "api_key": "key",
            "api_version": "v3",
            "exclude": exclude or [],
        }
        from scraparr.connectors.radarr import Module
        with patch("scraparr.metrics.radarr") as metrics:
            module = Module(config)
        return module

    def test_excluded_movie_not_counted(self):
        module = self._make_module(exclude=["/data/test"])
        movies = [
            make_radarr_movie("Movie A", "/data/media"),
            make_radarr_movie("Movie B", "/data/test"),
        ]
        import scraparr.metrics.radarr as radarr_metrics
        with patch.object(radarr_metrics, "MOVIE_COUNT_T") as mock_count:
            module.analyse_movies(movies)
            mock_count.labels.return_value.set.assert_called_with(1)

    def test_no_exclude_counts_all(self):
        module = self._make_module(exclude=[])
        movies = [
            make_radarr_movie("Movie A", "/data/media"),
            make_radarr_movie("Movie B", "/data/test"),
        ]
        import scraparr.metrics.radarr as radarr_metrics
        with patch.object(radarr_metrics, "MOVIE_COUNT_T") as mock_count:
            module.analyse_movies(movies)
            mock_count.labels.return_value.set.assert_called_with(2)


def make_lidarr_artist(name, root_folder, monitored=True, status="continuing"):
    """Helper to build a fake artist dict matching the Lidarr API shape."""
    return {
        "cleanName": name,
        "rootFolderPath": root_folder,
        "monitored": monitored,
        "status": status,
        "releases": [],
        "trackFiles": [],
        "statistics": {
            "albumCount": 5,
            "trackCount": 50,
            "sizeOnDisk": 3000,
        },
    }


class TestLidarrExclude:
    """Tests for Lidarr.analyse_artists exclude filtering."""

    def _make_module(self, exclude=None):
        config = {
            "url": "http://localhost:8686",
            "api_key": "key",
            "api_version": "v1",
            "exclude": exclude or [],
        }
        from scraparr.connectors.lidarr import Module
        return Module(config)

    def test_excluded_artist_not_counted(self):
        module = self._make_module(exclude=["/data/test"])
        artists = [
            make_lidarr_artist("artist-a", "/data/media"),
            make_lidarr_artist("artist-b", "/data/test"),
        ]
        import scraparr.metrics.lidarr as lidarr_metrics
        with patch.object(lidarr_metrics, "ARTIST_COUNT_T") as mock_count:
            module.analyse_artists(artists)
            mock_count.labels.return_value.set.assert_called_with(1)

    def test_no_exclude_counts_all(self):
        module = self._make_module(exclude=[])
        artists = [
            make_lidarr_artist("artist-a", "/data/media"),
            make_lidarr_artist("artist-b", "/data/test"),
        ]
        import scraparr.metrics.lidarr as lidarr_metrics
        with patch.object(lidarr_metrics, "ARTIST_COUNT_T") as mock_count:
            module.analyse_artists(artists)
            mock_count.labels.return_value.set.assert_called_with(2)


def make_readarr_author(name, root_folder, status="continuing", rating=4.0):
    """Helper to build a fake author dict matching the Readarr API shape."""
    return {
        "sortName": name,
        "rootFolderPath": root_folder,
        "status": status,
        "ratings": {"value": rating},
        "statistics": {
            "bookCount": 3,
            "sizeOnDisk": 500,
        },
    }


class TestReadarrExclude:
    """Tests for Readarr.analyse_authors exclude filtering."""

    def _make_module(self, exclude=None):
        config = {
            "url": "http://localhost:8787",
            "api_key": "key",
            "api_version": "v1",
            "exclude": exclude or [],
        }
        from scraparr.connectors.readarr import Module
        return Module(config)

    def test_excluded_author_skipped(self):
        module = self._make_module(exclude=["/data/test"])
        authors = [
            make_readarr_author("Author A", "/data/media", rating=4.0),
            make_readarr_author("Author B", "/data/test", rating=2.0),
        ]
        import scraparr.metrics.readarr as readarr_metrics
        with patch.object(readarr_metrics, "AUTHOR_RATING_TOTAL") as mock_rating:
            module.analyse_authors(authors)
            # Only Author A's rating (4.0) should be used
            mock_rating.labels.return_value.set.assert_called_with(4.0)

    def test_no_exclude_includes_all_authors(self):
        module = self._make_module(exclude=[])
        authors = [
            make_readarr_author("Author A", "/data/media", rating=4.0),
            make_readarr_author("Author B", "/data/test", rating=2.0),
        ]
        import scraparr.metrics.readarr as readarr_metrics
        with patch.object(readarr_metrics, "AUTHOR_RATING_TOTAL") as mock_rating:
            module.analyse_authors(authors)
            # Average of both: (4.0 + 2.0) / 2 = 3.0
            mock_rating.labels.return_value.set.assert_called_with(3.0)
