"""
Module to handle the Metrics of the Radarr Service
"""

import time
from datetime import datetime
import scraparr.metrics.radarr as radarr_metrics
from scraparr.metrics.general import UP
from scraparr import util

def get_movies(url, api_key, version):
    """Grab the Movies from the Radarr Endpoint"""

    initial_time = time.time()
    res = util.get(f"{url}/api/{version}/movie", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels("radarr").set(0)
    else:
        for movie in res:
            movie_file = util.get(f"{url}/api/{version}/moviefile?movieId={movie['id']}", api_key)
            movie["movieFile"] = movie_file

        UP.labels("radarr").set(1)
        radarr_metrics.LAST_SCRAPE.set(end_time)
        radarr_metrics.SCRAPE_DURATION.set(end_time - initial_time)
    return res

def analyse_movies(movies, detailed):
    """Analyse the Movies and set the Correct Metrics"""

    # Reset Titled Metrics to insure deletion of old Movies
    radarr_metrics.MOVIE_FILE_COUNT.clear()
    radarr_metrics.MOVIE_DISK_SIZE.clear()
    radarr_metrics.MOVIE_MONITORED.clear()
    radarr_metrics.MOVIE_MISSING.clear()

    status_labels = {
        "tba": {"func": radarr_metrics.TBA_MOVIES, "paths": {"total": 0}},
        "in cinemas": {"func": radarr_metrics.IN_CINEMAS_MOVIES, "paths": {"total": 0}},
        "announced": {"func": radarr_metrics.ANNOUNCED_MOVIES, "paths": {"total": 0}},
        "released": {"func": radarr_metrics.RELEASED_MOVIES, "paths": {"total": 0}},
        "deleted": {"func": radarr_metrics.DELETED_MOVIES, "paths": {"total": 0}}
    }

    quality_count = {}
    genre_count = {}

    used_size = {"total": 0}
    movie_count = {
        "total": {"paths": {"total": len(movies) }, "func": radarr_metrics.MOVIE_COUNT},
        "missing": {"paths": {"total": 0 }, "func": radarr_metrics.MISSING_MOVIES_COUNT},
        "monitored": {"paths": {"total": 0 }, "func": radarr_metrics.MONITORED_MOVIES},
        "unmonitored": {"paths": {"total": 0 }, "func": radarr_metrics.UNMONITORED_MOVIES}
    }

    for movie in movies:
        title = movie["title"].lower().replace(" ", "-")
        title = ''.join(e for e in title if e.isalnum() or e == "-")

        root_folder = movie["rootFolderPath"]

        util.increase_quality_count(quality_count, movie["movieFile"], root_folder)

        size_on_disk = movie["statistics"]["sizeOnDisk"]
        util.update_count(
            [size_on_disk, used_size],
            root_folder, movie_count, status_labels)

        if detailed:
            radarr_metrics.MOVIE_FILE_COUNT.labels(title).set(movie["statistics"]["movieFileCount"])
            radarr_metrics.MOVIE_DISK_SIZE.labels(title).set(size_on_disk)
            radarr_metrics.MOVIE_MONITORED.labels(title).set(1 if movie["monitored"] else 0)

        # Status-Verarbeitung mit Dictionary
        status = movie["status"].lower()
        util.update_status(status, root_folder, status_labels)

        util.update_genre_count(movie["genres"], genre_count, root_folder)

        util.update_monitoring(
            [movie, movie_count],
            title, root_folder,
            detailed, radarr_metrics.MOVIE_MISSING
        )

    util.update_media_metrics(
        [quality_count, radarr_metrics.QUALITY_MOVIE_COUNT],
        [used_size, radarr_metrics.TOTAL_DISK_SIZE],
        [genre_count, radarr_metrics.MOVIE_GENRES_COUNT],
        status_labels, movie_count,
    )

def update_system_data(data):
    """Update the System Metrics"""

    for disk in data['root_folder']:
        radarr_metrics.FREE_DISK_SIZE.labels(disk["path"]).set(disk["freeSpace"])
        radarr_metrics.AVAILABLE_DISK_SIZE.labels(disk["path"]).set(disk["totalSpace"])

    radarr_metrics.QUEUE_COUNT.set(data["queue"]["totalCount"])
    radarr_metrics.QUEUE_ERROR.set(data["queue"]["errors"])
    radarr_metrics.QUEUE_WARNING.set(data["queue"]["warnings"])

    start_time = datetime.strptime(data["status"]["startTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    build_time = datetime.strptime(data["status"]["buildTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    radarr_metrics.START_TIME.set(start_time)
    radarr_metrics.BUILD_TIME.set(build_time)

def scrape(config):
    """Scrape the Radarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    api_version = config.get('api_version', 'v3')

    return get_movies(url, api_key, api_version)

def update_metrics(data, detailed):
    """Update the Radarr Metrics"""

    analyse_movies(data['data'], detailed)
    update_system_data(data['system'])
