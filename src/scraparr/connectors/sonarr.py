"""
Module to handle the Metrics of the Sonarr Service
"""

import time
import logging
from datetime import datetime
from scraparr import util
from scraparr.metrics.general import UP
import scraparr.metrics.sonarr as sonarr_metrics

def get_series(url, api_key, version):
    """Grab the Series from the Sonarr Endpoint"""

    initial_time = time.time()
    res = util.get(f"{url}/api/{version}/series", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels("sonarr").set(0)
    else:
        for series in res:
            episodes = util.get(f"{url}/api/{version}/episodefile?seriesId={series['id']}", api_key)
            series["episodes"] = episodes

        UP.labels("sonarr").set(1)
        sonarr_metrics.LAST_SCRAPE.set(end_time)
        sonarr_metrics.SCRAPE_DURATION.set(end_time - initial_time)
    return res
def analyse_series(series, detailed):
    """Analyse the Series and set the Correct Metrics"""

    sonarr_metrics.SERIES_COUNT.labels("total").set(len(series))

    status_labels = {
        "continuing": {"func": sonarr_metrics.CONTINUING_SERIES, "paths": {"total": 0 }},
        "upcoming": {"func": sonarr_metrics.UPCOMING_SERIES, "paths": {"total": 0 }},
        "ended": {"func": sonarr_metrics.ENDED_SERIES, "paths": {"total": 0 }},
        "deleted": {"func": sonarr_metrics.DELETED_SERIES, "paths": {"total": 0 }}
    }

    quality_count = {}
    genre_count = {}

    used_size = {"total": 0}
    series_count = {
        "total": {"paths": {"total": len(series) }, "func": sonarr_metrics.SERIES_COUNT},
        "missing": {"paths": {"total": 0 }, "func": sonarr_metrics.MISSING_EPISODE_COUNT},
        "monitored": {"paths": {"total": 0 }, "func": sonarr_metrics.MONITORED_SERIES},
        "unmonitored": {"paths": {"total": 0 }, "func": sonarr_metrics.UNMONITORED_SERIES},
        "episode": {"paths": {"total": 0 }, "func": sonarr_metrics.EPISODE_COUNT}
    }

    # Reset Titled Metrics to insure deletion of old Series
    sonarr_metrics.SERIES_EPISODE_COUNT.clear()
    sonarr_metrics.SERIES_MISSING_EPISODE_COUNT.clear()
    sonarr_metrics.SERIES_COUNT.clear()
    sonarr_metrics.SERIES_DISK_SIZE.clear()
    sonarr_metrics.SERIES_DOWNLOAD_PERCENTAGE.clear()
    sonarr_metrics.SERIES_MONITORED.clear()

    for serie in series:
        title = serie["titleSlug"]
        stats = serie.get("statistics", None)

        if stats is None:
            logging.warning("No statistics found for %s", title)
            continue

        util.increase_quality_count(quality_count, serie["episodes"], serie["rootFolderPath"])

        root_folder = serie["rootFolderPath"]

        util.update_count(
            [stats["sizeOnDisk"], used_size],
            root_folder, series_count,
            status_labels, stats["episodeFileCount"]
        )

        util.update_status(serie["status"], root_folder, status_labels)

        util.update_genre_count(serie["genres"], genre_count, root_folder)

        for season in serie["seasons"]:
            if season["monitored"]:
                s_episode_count = season["statistics"]["episodeCount"]
                missing = s_episode_count - season["statistics"]["episodeFileCount"]
                series_count["missing"]["paths"]["total"] += missing
                series_count["missing"]["paths"][root_folder] += missing
                if detailed:
                    sonarr_metrics.SERIES_MISSING_EPISODE_COUNT.labels(title).inc(missing)

        if detailed:
            sonarr_metrics.SERIES_EPISODE_COUNT.labels(title).set(stats["episodeCount"])
            sonarr_metrics.SERIES_SEASON_COUNT.labels(title).set(stats["seasonCount"])
            sonarr_metrics.SERIES_DISK_SIZE.labels(title).set(stats["sizeOnDisk"])
            sonarr_metrics.SERIES_DOWNLOAD_PERCENTAGE.labels(title).set(stats["percentOfEpisodes"])
            sonarr_metrics.SERIES_MONITORED.labels(title).set(1 if serie["monitored"] else 0)

        if serie["monitored"]:
            series_count["monitored"]["paths"]["total"] += 1
            series_count["monitored"]["paths"][root_folder] += 1
        else:
            series_count["unmonitored"]["paths"]["total"] += 1
            series_count["unmonitored"]["paths"][root_folder] += 1

    util.update_media_metrics(
        [quality_count, sonarr_metrics.QUALITY_EPISODE_COUNT],
        [used_size, sonarr_metrics.TOTAL_DISK_SIZE],
        [genre_count, sonarr_metrics.SERIES_GENRES_COUNT],
        status_labels, series_count,
    )

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
    api_version = config.get('api_version', 'v3')

    return get_series(url, api_key, api_version)

def update_metrics(series, detailed):
    """Update the Metrics for the Sonarr Service"""

    analyse_series(series["data"], detailed)
    update_system_data(series["system"])
