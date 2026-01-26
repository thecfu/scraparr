"""
Shared pytest fixtures for tests.

Currently contains Sonarr-specific fixtures; add other connector fixtures here as needed.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_metrics():
    """Create mock metrics module that mimics sonarr_metrics structure."""
    metrics = MagicMock()

    # Create mock gauges with labels method that returns a mock with set/inc methods
    def create_mock_gauge():
        gauge = MagicMock()
        gauge.labels.return_value = MagicMock()
        gauge.remove_by_labels = MagicMock()
        return gauge

    # Scraping stats
    metrics.LAST_SCRAPE = create_mock_gauge()
    metrics.SCRAPE_DURATION = create_mock_gauge()

    # Status stats
    metrics.START_TIME = create_mock_gauge()
    metrics.BUILD_TIME = create_mock_gauge()

    # Queue stats
    metrics.QUEUE_COUNT = create_mock_gauge()
    metrics.QUEUE_ERROR = create_mock_gauge()
    metrics.QUEUE_WARNING = create_mock_gauge()

    # Series counts
    metrics.SERIES_COUNT = create_mock_gauge()
    metrics.SERIES_COUNT_T = create_mock_gauge()
    metrics.EPISODE_COUNT = create_mock_gauge()
    metrics.EPISODE_COUNT_T = create_mock_gauge()
    metrics.TOTAL_DISK_SIZE = create_mock_gauge()
    metrics.TOTAL_DISK_SIZE_T = create_mock_gauge()
    metrics.FREE_DISK_SIZE = create_mock_gauge()
    metrics.AVAILABLE_DISK_SIZE = create_mock_gauge()

    # Quality metrics
    metrics.QUALITY_EPISODE_COUNT = create_mock_gauge()
    metrics.QUALITY_EPISODE_COUNT_T = create_mock_gauge()

    # Genre metrics
    metrics.SERIES_GENRES_COUNT = create_mock_gauge()
    metrics.SERIES_GENRES_COUNT_T = create_mock_gauge()

    # Missing/monitored
    metrics.MISSING_EPISODE_COUNT = create_mock_gauge()
    metrics.MISSING_EPISODE_COUNT_T = create_mock_gauge()
    metrics.MONITORED_SERIES = create_mock_gauge()
    metrics.MONITORED_SERIES_T = create_mock_gauge()
    metrics.UNMONITORED_SERIES = create_mock_gauge()
    metrics.UNMONITORED_SERIES_T = create_mock_gauge()

    # Status metrics
    metrics.CONTINUING_SERIES = create_mock_gauge()
    metrics.CONTINUING_SERIES_T = create_mock_gauge()
    metrics.UPCOMING_SERIES = create_mock_gauge()
    metrics.UPCOMING_SERIES_T = create_mock_gauge()
    metrics.ENDED_SERIES = create_mock_gauge()
    metrics.ENDED_SERIES_T = create_mock_gauge()
    metrics.DELETED_SERIES = create_mock_gauge()
    metrics.DELETED_SERIES_T = create_mock_gauge()

    # Per-series metrics (for detailed mode)
    metrics.SERIES_EPISODE_COUNT = create_mock_gauge()
    metrics.SERIES_SEASON_COUNT = create_mock_gauge()
    metrics.SERIES_DOWNLOAD_PERCENTAGE = create_mock_gauge()
    metrics.SERIES_MONITORED = create_mock_gauge()
    metrics.SERIES_DISK_SIZE = create_mock_gauge()
    metrics.SERIES_MISSING_EPISODE_COUNT = create_mock_gauge()

    return metrics


@pytest.fixture
def sample_series_data():
    """Sample series data returned by /series endpoint."""
    return [
        {
            "id": 1,
            "title": "Test Series 1",
            "titleSlug": "test-series-1",
            "status": "continuing",
            "monitored": True,
            "rootFolderPath": "/tv",
            "genres": ["Drama"],
            "seasons": [
                {
                    "seasonNumber": 1,
                    "monitored": True,
                    "statistics": {
                        "episodeCount": 10,
                        "episodeFileCount": 8
                    }
                }
            ],
            "statistics": {
                "episodeCount": 10,
                "episodeFileCount": 8,
                "seasonCount": 1,
                "sizeOnDisk": 5000000000,
                "percentOfEpisodes": 80.0
            }
        },
        {
            "id": 2,
            "title": "Test Series 2",
            "titleSlug": "test-series-2",
            "status": "ended",
            "monitored": False,
            "rootFolderPath": "/tv",
            "genres": ["Comedy"],
            "seasons": [
                {
                    "seasonNumber": 1,
                    "monitored": False,
                    "statistics": {
                        "episodeCount": 5,
                        "episodeFileCount": 5
                    }
                }
            ],
            "statistics": {
                "episodeCount": 5,
                "episodeFileCount": 5,
                "seasonCount": 1,
                "sizeOnDisk": 2000000000,
                "percentOfEpisodes": 100.0
            }
        }
    ]


@pytest.fixture
def sample_episodefile_data():
    """Sample episode file data returned by /episodefile endpoint."""
    return {
        1: [
            {"id": 101, "quality": {"quality": {"name": "HDTV-1080p"}}},
            {"id": 102, "quality": {"quality": {"name": "HDTV-1080p"}}},
            {"id": 103, "quality": {"quality": {"name": "WEBDL-1080p"}}},
        ],
        2: [
            {"id": 201, "quality": {"quality": {"name": "Bluray-1080p"}}},
            {"id": 202, "quality": {"quality": {"name": "Bluray-1080p"}}},
        ]
    }
