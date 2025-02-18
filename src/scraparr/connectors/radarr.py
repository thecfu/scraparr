"""
Module to handle the Metrics of the Radarr Service
"""

import time
from datetime import datetime
import scraparr.metrics.radarr as radarr_metrics
from scraparr.metrics.general import UP
from scraparr import util

def get_movies(url, api_key, version, alias):
    """Grab the Movies from the Radarr Endpoint"""

    initial_time = time.time()
    res = util.get(f"{url}/api/{version}/movie", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels(alias).set(0)
    else:
        for movie in res:
            movie_file = util.get(f"{url}/api/{version}/moviefile?movieId={movie['id']}", api_key)
            movie["movieFile"] = movie_file

        UP.labels(alias).set(1)
        radarr_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        radarr_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
    return res

def analyse_movies(movies, detailed, alias):
    """Analyse the Movies and set the Correct Metrics"""

    # Reset Titled Metrics to insure deletion of old Movies
    radarr_metrics.MOVIE_FILE_COUNT.clear()
    radarr_metrics.MOVIE_DISK_SIZE.clear()
    radarr_metrics.MOVIE_MONITORED.clear()
    radarr_metrics.MOVIE_MISSING.clear()

    status_labels = {
        "tba": {
            "func": [radarr_metrics.TBA_MOVIES, radarr_metrics.TBA_MOVIES_T],
            "paths": {"total": 0}
        },
        "in cinemas": {
            "func": [radarr_metrics.IN_CINEMAS_MOVIES, radarr_metrics.IN_CINEMAS_MOVIES_T],
            "paths": {"total": 0}
        },
        "announced": {
            "func": [radarr_metrics.ANNOUNCED_MOVIES, radarr_metrics.ANNOUNCED_MOVIES_T],
            "paths": {"total": 0}
        },
        "released": {
            "func": [radarr_metrics.RELEASED_MOVIES, radarr_metrics.RELEASED_MOVIES_T],
            "paths": {"total": 0}
        },
        "deleted": {
            "func": [radarr_metrics.DELETED_MOVIES, radarr_metrics.DELETED_MOVIES_T],
            "paths": {"total": 0}
        }
    }

    quality_count = {}
    genre_count = {}

    radarr_metrics.MOVIE_COUNT_T.labels(alias).set(len(movies))

    used_size = {"total": 0}

    counter = {
        "path": {
            "total": {"paths": {}, "func": radarr_metrics.MOVIE_COUNT},
            "missing": {"paths": {}, "func": radarr_metrics.MISSING_MOVIES_COUNT},
            "monitored": {"paths": {}, "func": radarr_metrics.MONITORED_MOVIES},
            "unmonitored": {"paths": {}, "func": radarr_metrics.UNMONITORED_MOVIES}
        },
        "total": {
            "missing": [0, radarr_metrics.MISSING_MOVIES_COUNT_T],
            "monitored": [0, radarr_metrics.MONITORED_MOVIES_T],
            "unmonitored": [0, radarr_metrics.UNMONITORED_MOVIES_T]
        }
    }

    for movie in movies:
        title = movie["title"].lower().replace(" ", "-")
        title = ''.join(e for e in title if e.isalnum() or e == "-")

        root_folder = movie["rootFolderPath"]

        util.increase_quality_count(quality_count, movie["movieFile"], root_folder)

        size_on_disk = movie["statistics"]["sizeOnDisk"]
        util.update_count(
            [size_on_disk, used_size],
            root_folder, counter["path"], status_labels)

        if detailed:
            (radarr_metrics.MOVIE_FILE_COUNT
                .labels(alias, title)
                .set(movie["statistics"]["movieFileCount"])
            )
            radarr_metrics.MOVIE_DISK_SIZE.labels(alias, title).set(size_on_disk)
            radarr_metrics.MOVIE_MONITORED.labels(alias, title).set(1 if movie["monitored"] else 0)

        # Status-Verarbeitung mit Dictionary
        status = movie["status"].lower()
        util.update_status(status, root_folder, status_labels)

        util.update_genre_count(movie["genres"], genre_count, root_folder)

        util.update_monitoring(
            [movie, counter["path"], counter["total"]],
            [title, root_folder,
            detailed, radarr_metrics.MOVIE_MISSING],
            alias
        )

    util.update_media_metrics(
        [[quality_count, radarr_metrics.QUALITY_MOVIE_COUNT, radarr_metrics.QUALITY_MOVIE_COUNT_T],
        [used_size, radarr_metrics.TOTAL_DISK_SIZE, radarr_metrics.TOTAL_DISK_SIZE_T],
        [genre_count, radarr_metrics.MOVIE_GENRES_COUNT, radarr_metrics.MOVIE_GENRES_COUNT_T],
        status_labels, counter], alias
    )

def update_system_data(data, alias):
    """Update the System Metrics"""

    for disk in data['root_folder']:
        radarr_metrics.FREE_DISK_SIZE.labels(alias, disk["path"]).set(disk["freeSpace"])
        radarr_metrics.AVAILABLE_DISK_SIZE.labels(alias, disk["path"]).set(disk["totalSpace"])

    radarr_metrics.QUEUE_COUNT.labels(alias).set(data["queue"]["totalCount"])
    radarr_metrics.QUEUE_ERROR.labels(alias).set(data["queue"]["errors"])
    radarr_metrics.QUEUE_WARNING.labels(alias).set(data["queue"]["warnings"])

    start_time = datetime.strptime(data["status"]["startTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    build_time = datetime.strptime(data["status"]["buildTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    radarr_metrics.START_TIME.labels(alias).set(start_time)
    radarr_metrics.BUILD_TIME.labels(alias).set(build_time)

def scrape(config):
    """Scrape the Radarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    api_version = config.get('api_version', 'v3')
    alias = config.get('alias', 'radarr')

    return get_movies(url, api_key, api_version, alias)

def update_metrics(data, detailed, alias):
    """Update the Radarr Metrics"""

    analyse_movies(data['data'], detailed, alias)
    update_system_data(data['system'], alias)
