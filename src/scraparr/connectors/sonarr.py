"""
Module to handle the Metrics of the Sonarr Service
"""

import time
from dateutil.parser import parse

from scraparr import util
from scraparr.metrics.general import UP
import scraparr.metrics.sonarr as sonarr_metrics

def get_series(url, api_key, version, alias):
    """Grab the Series from the Sonarr Endpoint"""

    initial_time = time.time()
    res = util.get(f"{url}/api/{version}/series", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels(alias, 'sonarr').set(0)
    else:
        for series in res:
            episodes = util.get(f"{url}/api/{version}/episodefile?seriesId={series['id']}", api_key)
            series["episodes"] = episodes

        UP.labels(alias, 'sonarr').set(1)
        sonarr_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        sonarr_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
    return res

def analyse_series(series, detailed, alias):
    """Analyse the Series and set the Correct Metrics"""

    status_labels = {
        "continuing": {
            "func": [sonarr_metrics.CONTINUING_SERIES, sonarr_metrics.CONTINUING_SERIES_T],
            "paths": {"total": 0}
        },
        "upcoming": {
            "func": [sonarr_metrics.UPCOMING_SERIES, sonarr_metrics.UPCOMING_SERIES_T],
            "paths": {"total": 0}
        },
        "ended": {
            "func": [sonarr_metrics.ENDED_SERIES, sonarr_metrics.ENDED_SERIES_T],
            "paths": {"total": 0}
        },
        "deleted": {
            "func": [sonarr_metrics.DELETED_SERIES, sonarr_metrics.DELETED_SERIES_T],
            "paths": {"total": 0}
        }
    }

    quality_count = {}
    genre_count = {}

    sonarr_metrics.SERIES_COUNT_T.labels(alias).set(len(series))

    used_size = {"total": 0}

    counter = {
        "path": {
            "total": {"paths": {}, "func": sonarr_metrics.SERIES_COUNT},
            "missing": {"paths": {}, "func": sonarr_metrics.MISSING_EPISODE_COUNT},
            "monitored": {"paths": {}, "func": sonarr_metrics.MONITORED_SERIES},
            "unmonitored": {"paths": {}, "func": sonarr_metrics.UNMONITORED_SERIES},
            "episode": {"paths": {}, "func": sonarr_metrics.EPISODE_COUNT}
        },
        "total": {
            "missing": [0, sonarr_metrics.MISSING_EPISODE_COUNT_T],
            "monitored": [0, sonarr_metrics.MONITORED_SERIES_T],
            "unmonitored": [0, sonarr_metrics.UNMONITORED_SERIES_T],
            "episode": [0, sonarr_metrics.EPISODE_COUNT_T]
        }
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

        util.increase_quality_count(quality_count, serie["episodes"], serie["rootFolderPath"])

        stats = serie["statistics"]
        root_folder = serie["rootFolderPath"]

        util.update_count(
            [stats["sizeOnDisk"], used_size],
            root_folder, counter["path"],
            status_labels, [stats["episodeFileCount"], counter["total"]]
        )

        util.update_status(serie["status"], root_folder, status_labels)

        util.update_genre_count(serie["genres"], genre_count, root_folder)

        for season in serie["seasons"]:
            if season["monitored"]:
                s_episode_count = season["statistics"]["episodeCount"]
                missing = s_episode_count - season["statistics"]["episodeFileCount"]
                counter["total"]["missing"][0] += missing
                counter["path"]["missing"]["paths"][root_folder] += missing
                if detailed:
                    sonarr_metrics.SERIES_MISSING_EPISODE_COUNT.labels(alias, title).inc(missing)

        if detailed:
            sonarr_metrics.SERIES_EPISODE_COUNT.labels(alias, title).set(stats["episodeCount"])
            sonarr_metrics.SERIES_SEASON_COUNT.labels(alias, title).set(stats["seasonCount"])
            sonarr_metrics.SERIES_DISK_SIZE.labels(alias, title).set(stats["sizeOnDisk"])
            (sonarr_metrics
                .SERIES_DOWNLOAD_PERCENTAGE.labels(alias, title)
                .set(stats["percentOfEpisodes"]))
            sonarr_metrics.SERIES_MONITORED.labels(alias, title).set(1 if serie["monitored"] else 0)

        if serie["monitored"]:
            counter["total"]["monitored"][0] += 1
            counter["path"]["monitored"]["paths"][root_folder] += 1
        else:
            counter["total"]["unmonitored"][0] += 1
            counter["path"]["unmonitored"]["paths"][root_folder] += 1

    util.update_media_metrics(
        [[
            quality_count,
            sonarr_metrics.QUALITY_EPISODE_COUNT,
            sonarr_metrics.QUALITY_EPISODE_COUNT_T
        ],
        [used_size, sonarr_metrics.TOTAL_DISK_SIZE, sonarr_metrics.TOTAL_DISK_SIZE_T],
        [genre_count, sonarr_metrics.SERIES_GENRES_COUNT, sonarr_metrics.SERIES_GENRES_COUNT_T],
        status_labels, counter], alias
    )

def update_system_data(data, alias):
    """Update the System Data Metrics"""
    for disk in data['root_folder']:
        sonarr_metrics.FREE_DISK_SIZE.labels(alias, disk["path"]).set(disk["freeSpace"])
        sonarr_metrics.AVAILABLE_DISK_SIZE.labels(alias, disk["path"]).set(disk["totalSpace"])

    sonarr_metrics.QUEUE_COUNT.labels(alias).set(data["queue"]["totalCount"])
    sonarr_metrics.QUEUE_ERROR.labels(alias).set(data["queue"]["errors"])
    sonarr_metrics.QUEUE_WARNING.labels(alias).set(data["queue"]["warnings"])

    start_time = parse(data["status"]["startTime"]).timestamp()
    build_time = parse(data["status"]["buildTime"]).timestamp()
    sonarr_metrics.START_TIME.labels(alias).set(start_time)
    sonarr_metrics.BUILD_TIME.labels(alias).set(build_time)

def scrape(config):
    """Scrape the Sonarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    api_version = config.get('api_version')
    alias = config.get('alias', 'sonarr')

    return get_series(url, api_key, api_version, alias)

def update_metrics(series, detailed, alias):
    """Update the Metrics for the Sonarr Service"""

    analyse_series(series["data"], detailed, alias)
    update_system_data(series["system"], alias)
