"""
Module to handle the Metrics of the Sonarr Service
"""

import time
from datetime import datetime
from scraparr.util import get
from scraparr.metrics.general import UP
import scraparr.metrics.sonarr as sonarr_metrics

def get_series(url, api_key):
    """Grab the Series from the Sonarr Endpoint"""

    initial_time = time.time()
    res = get(f"{url}/api/v3/series", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels("sonarr").set(0)
    else:
        UP.labels("sonarr").set(1)
        sonarr_metrics.LAST_SCRAPE.set(end_time)
        sonarr_metrics.SCRAPE_DURATION.set(end_time - initial_time)
    return res
def analyse_series(series, detailed):
    """Analyse the Series and set the Correct Metrics"""

    sonarr_metrics.SERIES_COUNT.labels("total").set(len(series))

    status_labels = {
        "continuing": sonarr_metrics.CONTINUING_SERIES,
        "upcoming": sonarr_metrics.UPCOMING_SERIES,
        "ended": sonarr_metrics.ENDED_SERIES,
        "deleted": sonarr_metrics.DELETED_SERIES
    }

    for serie in series:
        title = serie["titleSlug"]


        stats = serie["statistics"]
        episode_count = stats["episodeCount"]
        episode_file_count = stats["episodeFileCount"]
        size_on_disk = stats["sizeOnDisk"]

        sonarr_metrics.SERIES_COUNT.labels(serie["rootFolderPath"]).inc()
        sonarr_metrics.EPISODE_COUNT.labels("total").inc(episode_count)
        sonarr_metrics.EPISODE_COUNT.labels(serie["rootFolderPath"]).inc()

        monitored_seasons = any(season['monitored'] for season in serie["seasons"])
        if monitored_seasons:
            missing = episode_count - episode_file_count
            sonarr_metrics.MISSING_EPISODE_COUNT.labels("total").inc(missing)
            sonarr_metrics.MISSING_EPISODE_COUNT.labels(serie["rootFolderPath"]).inc(missing)
            if detailed:
                sonarr_metrics.SERIES_MISSING_EPISODE_COUNT.labels(title).set(missing)

        sonarr_metrics.TOTAL_DISK_SIZE.labels("total").inc(size_on_disk)
        sonarr_metrics.TOTAL_DISK_SIZE.labels(serie["rootFolderPath"]).inc(size_on_disk)

        if detailed:
            sonarr_metrics.SERIES_EPISODE_COUNT.labels(title).set(episode_count)
            sonarr_metrics.SERIES_SEASON_COUNT.labels(title).set(stats["seasonCount"])
            sonarr_metrics.SERIES_DISK_SIZE.labels(title).set(size_on_disk)
            sonarr_metrics.SERIES_DOWNLOAD_PERCENTAGE.labels(title).set(stats["percentOfEpisodes"])
            sonarr_metrics.SERIES_MONITORED.labels(title).set(1 if serie["monitored"] else 0)

        # Status mit Dictionary verarbeiten
        if serie["status"] in status_labels:
            status_labels[serie["status"]].labels("total").inc()
            status_labels[serie["status"]].labels(serie["rootFolderPath"]).inc()

        for genre in serie["genres"]:
            sonarr_metrics.SERIES_GENRES_COUNT.labels(genre, "total").inc()
            sonarr_metrics.SERIES_GENRES_COUNT.labels(genre, serie["rootFolderPath"]).inc()

        if serie["monitored"]:
            monitored_label = sonarr_metrics.MONITORED_SERIES
        else:
            monitored_label = sonarr_metrics.UNMONITORED_SERIES
        monitored_label.labels("total").inc()
        monitored_label.labels(serie["rootFolderPath"]).inc()

def update_system_data(data):
    """Update the System Data Metrics"""
    for disk in data['root_folder']:
        sonarr_metrics.FREE_DISK_SIZE.labels(disk["path"]).set(disk["freeSpace"])
        sonarr_metrics.AVAILABLE_DISK_SIZE.labels(disk["path"]).set(disk["totalSpace"])

    sonarr_metrics.QUEUE_COUNT.set(data["queue"]["totalCount"])
    sonarr_metrics.QUEUE_ERROR.set(data["queue"]["errors"])
    sonarr_metrics.QUEUE_WARNING.set(data["queue"]["warnings"])

    start_time = datetime.strptime(data["status"]["startTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    build_time = datetime.strptime(data["status"]["buildTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    sonarr_metrics.START_TIME.set(start_time)
    sonarr_metrics.BUILD_TIME.set(build_time)

def scrape(config):
    """Scrape the Sonarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')

    return get_series(url, api_key)

def update_metrics(series, detailed):
    """Update the Metrics for the Sonarr Service"""

    analyse_series(series["data"], detailed)
    update_system_data(series["system"])
