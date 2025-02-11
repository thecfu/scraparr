"""
Module to handle the Metrics of the Radarr Service
"""

import time
from datetime import datetime
import scraparr.metrics.radarr as radarr_metrics
from scraparr.metrics.general import UP
from scraparr.util import get

def get_movies(url, api_key):
    """Grab the Movies from the Radarr Endpoint"""

    initial_time = time.time()
    res = get(f"{url}/api/v3/movie", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels("radarr").set(0)
    else:
        UP.labels("radarr").set(1)
        radarr_metrics.LAST_SCRAPE.set(end_time)
        radarr_metrics.SCRAPE_DURATION.set(end_time - initial_time)
    return res

def analyse_movies(movies, detailed):
    """Analyse the Movies and set the Correct Metrics"""

    radarr_metrics.MOVIE_COUNT.labels("total").set(len(movies))

    for movie in movies:
        title = movie["title"].lower().replace(" ", "-")
        # Remove special characters from title
        title = ''.join(e for e in title if e.isalnum() or e == "-")

        radarr_metrics.MOVIE_COUNT.labels(movie["rootFolderPath"]).inc()

        size_on_disk = movie["statistics"]["sizeOnDisk"]


        radarr_metrics.TOTAL_DISK_SIZE.labels("total").inc(size_on_disk)
        radarr_metrics.TOTAL_DISK_SIZE.labels(movie["rootFolderPath"]).inc(size_on_disk)

        if detailed:
            radarr_metrics.MOVIE_FILE_COUNT.labels(title).set(movie["statistics"]["movieFileCount"])
            radarr_metrics.MOVIE_DISK_SIZE.labels(title).set(size_on_disk)
            radarr_metrics.MOVIE_MONITORED.labels(title).set(1 if movie["monitored"] else 0)

        if movie["status"] == "tba":
            radarr_metrics.TBA_MOVIES.labels("total").inc()
            radarr_metrics.TBA_MOVIES.labels(movie["rootFolderPath"]).inc()
        elif movie["status"] == "in cinemas":
            radarr_metrics.IN_CINEMAS_MOVIES.labels("total").inc()
            radarr_metrics.IN_CINEMAS_MOVIES.labels(movie["rootFolderPath"]).inc()
        elif movie["status"] == "announced":
            radarr_metrics.ANNOUNCED_MOVIES.labels("total").inc()
            radarr_metrics.ANNOUNCED_MOVIES.labels(movie["rootFolderPath"]).inc()
        elif movie["status"] == "released":
            radarr_metrics.RELEASED_MOVIES.labels("total").inc()
            radarr_metrics.RELEASED_MOVIES.labels(movie["rootFolderPath"]).inc()
        elif movie["status"] == "deleted":
            radarr_metrics.DELETED_MOVIES.labels("total").inc()
            radarr_metrics.DELETED_MOVIES.labels(movie["rootFolderPath"]).inc()

        for genre in movie["genres"]:
            radarr_metrics.MOVIE_GENRES_COUNT.labels(genre, "total").inc()
            radarr_metrics.MOVIE_GENRES_COUNT.labels(genre, movie["rootFolderPath"]).inc()

        if movie["monitored"]:
            movie_count = movie["hasFile"]
            if not movie_count:
                radarr_metrics.MISSING_MOVIES_COUNT.labels("total").inc()
                radarr_metrics.MISSING_MOVIES_COUNT.labels(movie["rootFolderPath"]).inc()

                if detailed:
                    radarr_metrics.MOVIE_MISSING.labels(title).set(movie_count)

            radarr_metrics.MONITORED_MOVIES.labels("total").inc()
            radarr_metrics.MONITORED_MOVIES.labels(movie["rootFolderPath"]).inc()
        else:
            radarr_metrics.UNMONITORED_MOVIES.labels("total").inc()
            radarr_metrics.UNMONITORED_MOVIES.labels(movie["rootFolderPath"]).inc()

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

    return get_movies(url, api_key)

def update_metrics(data, detailed):
    """Update the Radarr Metrics"""

    analyse_movies(data['data'], detailed)
    update_system_data(data['system'])
