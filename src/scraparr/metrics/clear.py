"""Clear metrics for various services in Scraparr."""

import scraparr.metrics.prowlarr as prowlarr_metrics
import scraparr.metrics.radarr as radarr_metrics
import scraparr.metrics.bazarr as bazarr_metrics
import scraparr.metrics.readarr as readarr_metrics
import scraparr.metrics.jellyseerr as jellyseerr_metrics
import scraparr.metrics.overseerr as overseerr_metrics
import scraparr.metrics.sonarr as sonarr_metrics
import scraparr.metrics.whisparr as whisparr_metrics


def clear(service):
    """
    Clear the metrics for the specified service.
    :param service: The service for which to clear metrics.
    """
    if service == "prowlarr":
        clearProwlarrMetrics()
    elif service == "radarr":
        clearRadarrMetrics()
    elif service == "bazarr":
        clearBazarrMetrics()
    elif service == "readarr":
        clearReadarrMetrics()
    elif service == "jellyseerr":
        clearJellyseerrMetrics()
    elif service == "overseerr":
        clearOverseerrMetrics()
    elif service == "sonarr":
        clearSonarrMetrics()
    elif service == "whisparr":
        clearWhisparrMetrics()

def clearProwlarrMetrics():
    """
    Clear all metrics with labels to remove any previous data.
    """
    prowlarr_metrics.VIP_EXPIRATION.clear()
    prowlarr_metrics.INDEXER_STATUS.clear()
    prowlarr_metrics.INDEXER_ENABLED.clear()

def clearRadarrMetrics():
    """
    Clear all Radarr metrics to remove any previous data.
    """
    radarr_metrics.MOVIE_FILE_COUNT.clear()
    radarr_metrics.MOVIE_DISK_SIZE.clear()
    radarr_metrics.MOVIE_MONITORED.clear()
    radarr_metrics.MOVIE_MISSING.clear()

def clearBazarrMetrics():
    """
    Clear all Bazarr metrics to remove any previous data.
    """

    bazarr_metrics.WANTED_EPISODE_COUNT.clear()
    bazarr_metrics.WANTED_MOVIE_COUNT.clear()
    bazarr_metrics.PROVIDER_STATUS.clear()

def clearReadarrMetrics():
    """
    Clear all Readarr metrics to remove any previous data.
    """

    readarr_metrics.BOOK_DISK_SIZE.clear()
    readarr_metrics.BOOK_PERCENTAGE.clear()
    readarr_metrics.BOOK_RATING.clear()
    readarr_metrics.BOOK_RATING_TOTAL.clear()
    readarr_metrics.AUTHOR_BOOK_COUNT.clear()
    readarr_metrics.AUTHOR_STATUS.clear()
    readarr_metrics.AUTHOR_DISK_SIZE.clear()
    readarr_metrics.AUTHOR_RATING.clear()
    readarr_metrics.AUTHOR_RATING_TOTAL.clear()

def clearJellyseerrMetrics():
    """
    Clear all Jellyseerr metrics to remove any previous data.
    """

    jellyseerr_metrics.REQUEST_TIMESTAMP.clear()
    jellyseerr_metrics.REQUEST_SEASONS.clear()
    jellyseerr_metrics.ISSUE_TITLE.clear()
    jellyseerr_metrics.ISSUE_CREATED.clear()
    jellyseerr_metrics.ISSUE_UPDATED.clear()
    jellyseerr_metrics.ISSUE_TITLE.clear()

def clearOverseerrMetrics():
    """
    Clear all Overseerr metrics to remove any previous data.
    """

    overseerr_metrics.REQUEST_TIMESTAMP.clear()
    overseerr_metrics.REQUEST_SEASONS.clear()
    overseerr_metrics.ISSUE_TITLE.clear()
    overseerr_metrics.ISSUE_CREATED.clear()
    overseerr_metrics.ISSUE_UPDATED.clear()
    overseerr_metrics.ISSUE_TITLE.clear()

def clearSonarrMetrics():
    """
    Clear all Sonarr metrics to remove any previous data.
    """
    sonarr_metrics.SERIES_EPISODE_COUNT.clear()
    sonarr_metrics.SERIES_MISSING_EPISODE_COUNT.clear()
    sonarr_metrics.SERIES_COUNT.clear()
    sonarr_metrics.SERIES_DISK_SIZE.clear()
    sonarr_metrics.SERIES_DOWNLOAD_PERCENTAGE.clear()
    sonarr_metrics.SERIES_MONITORED.clear()

def clearWhisparrMetrics():
    """
    Clear all Whisparr metrics to remove any previous data.
    """
    whisparr_metrics.SERIES_EPISODE_COUNT.clear()
    whisparr_metrics.SERIES_MISSING_EPISODE_COUNT.clear()
    whisparr_metrics.SERIES_COUNT.clear()
    whisparr_metrics.SERIES_DISK_SIZE.clear()
    whisparr_metrics.SERIES_DOWNLOAD_PERCENTAGE.clear()
    whisparr_metrics.SERIES_MONITORED.clear()
