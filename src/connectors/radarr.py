import logging
import time
import requests
import scraparr.metrics.radarr as radarr_metrics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_movies(url, api_key):
    try:
        initial_time = time.time()

        r = requests.get(f"{url}/api/v3/movie", headers={"X-Api-Key": api_key}, timeout=20)

        end_time = time.time()

        if r.status_code == 200:
            radarr_metrics.LAST_SCRAPE.set(end_time)
            radarr_metrics.SCRAPE_DURATION.set(end_time - initial_time)
            return r.json()

        logging.error("Error: %s", r.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Error: %s", e)
        return None

def analyse_movies(movies, detailed):
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
            radarr_metrics.MISSING_MOVIES_COUNT.labels("total").set(0 if movie["hasFile"] else 1)
            radarr_metrics.MISSING_MOVIES_COUNT.labels(movie["rootFolderPath"]).set(0 if movie["hasFile"] else 1)

            if detailed:
                radarr_metrics.MOVIE_MISSING.labels(title).set(0 if movie["hasFile"] else 1)

            radarr_metrics.MONITORED_MOVIES.labels("total").inc()
            radarr_metrics.MONITORED_MOVIES.labels(movie["rootFolderPath"]).inc()
        else:
            radarr_metrics.UNMONITORED_MOVIES.labels("total").inc()
            radarr_metrics.UNMONITORED_MOVIES.labels(movie["rootFolderPath"]).inc()

def update_system_data(data):
    for disk in data['root_folder']:
        radarr_metrics.FREE_DISK_SIZE.labels(disk["path"]).set(disk["freeSpace"])
        radarr_metrics.AVAILABLE_DISK_SIZE.labels(disk["path"]).set(disk["totalSpace"])

    radarr_metrics.QUEUE_COUNT.set(data["queue"]["totalCount"])
    radarr_metrics.QUEUE_ERROR.set(data["queue"]["errors"])
    radarr_metrics.QUEUE_WARNING.set(data["queue"]["warnings"])

def scrape(config):

    url = config.get('url')
    api_key = config.get('api_key')

    return get_movies(url, api_key)

def update_metrics(data, detailed):
    analyse_movies(data['data'], detailed)
    update_system_data(data['system'])
