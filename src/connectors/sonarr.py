import time
import logging
import requests
import scraparr.metrics.sonarr as sonarr_metrics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_series(url, api_key):
    try:
        initial_time = time.time()

        r = requests.get(f"{url}/api/v3/series", headers={"X-Api-Key": api_key}, timeout=20)

        end_time = time.time()

        if r.status_code == 200:
            sonarr_metrics.LAST_SCRAPE.set(end_time)
            sonarr_metrics.SCRAPE_DURATION.set(end_time - initial_time)
            return r.json()

        logging.error("Error: %s", r.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Error: %s", e)
        return None

def analyse_series(series, detailed):
    sonarr_metrics.SERIES_COUNT.labels("total").set(len(series))

    for serie in series:

        episode_count = serie["statistics"]["episodeCount"]
        episode_file_count = serie["statistics"]["episodeFileCount"]
        size_on_disk = serie["statistics"]["sizeOnDisk"]
        season_count = serie["statistics"]["seasonCount"]
        percent_of_episodes = serie["statistics"]["percentOfEpisodes"]

        sonarr_metrics.SERIES_COUNT.labels(serie["rootFolderPath"]).inc()

        sonarr_metrics.EPISODE_COUNT.labels("total").inc(episode_count)
        sonarr_metrics.EPISODE_COUNT.labels(serie["rootFolderPath"]).inc()

        for season in serie["seasons"]:
            if season['monitored']:
                missing = episode_count - episode_file_count
                sonarr_metrics.MISSING_EPISODE_COUNT.labels("total").inc(missing)
                sonarr_metrics.MISSING_EPISODE_COUNT.labels(serie["rootFolderPath"]).inc(missing)
                if detailed:
                    sonarr_metrics.SERIES_MISSING_EPISODE_COUNT.labels(serie["titleSlug"]).set(missing)


        sonarr_metrics.TOTAL_DISK_SIZE.labels("total").inc(size_on_disk)
        sonarr_metrics.TOTAL_DISK_SIZE.labels(serie["rootFolderPath"]).inc(size_on_disk)
        if detailed:
            sonarr_metrics.SERIES_EPISODE_COUNT.labels(serie["titleSlug"]).set(episode_count)
            sonarr_metrics.SERIES_SEASON_COUNT.labels(serie["titleSlug"]).set(season_count)
            sonarr_metrics.SERIES_DISK_SIZE.labels(serie["titleSlug"]).set(size_on_disk)
            sonarr_metrics.SERIES_DOWNLOAD_PERCENTAGE.labels(serie["titleSlug"]).set(percent_of_episodes)
            sonarr_metrics.SERIES_MONITORED.labels(serie["titleSlug"]).set(1 if serie["monitored"] else 0)

        if serie["status"] == "continuing":
            sonarr_metrics.CONTINUING_SERIES.labels("total").inc()
            sonarr_metrics.CONTINUING_SERIES.labels(serie["rootFolderPath"]).inc()
        elif serie["status"] == "upcoming":
            sonarr_metrics.UPCOMING_SERIES.labels("total").inc()
            sonarr_metrics.UPCOMING_SERIES.labels(serie["rootFolderPath"]).inc()
        elif serie["status"] == "ended":
            sonarr_metrics.ENDED_SERIES.labels("total").inc()
            sonarr_metrics.ENDED_SERIES.labels(serie["rootFolderPath"]).inc()
        elif serie["status"] == "deleted":
            sonarr_metrics.DELETED_SERIES.labels("total").inc()
            sonarr_metrics.DELETED_SERIES.labels(serie["rootFolderPath"]).inc()

        for genre in serie["genres"]:
            sonarr_metrics.SERIES_GENRES_COUNT.labels(genre, "total").inc()
            sonarr_metrics.SERIES_GENRES_COUNT.labels(genre, serie["rootFolderPath"]).inc()

        if serie["monitored"]:
            sonarr_metrics.MONITORED_SERIES.labels("total").inc()
            sonarr_metrics.MONITORED_SERIES.labels(serie["rootFolderPath"]).inc()
        else:
            sonarr_metrics.UNMONITORED_SERIES.labels("total").inc()
            sonarr_metrics.UNMONITORED_SERIES.labels(serie["rootFolderPath"]).inc()

def update_system_data(data):
    for disk in data['root_folder']:
        sonarr_metrics.FREE_DISK_SIZE.labels(disk["path"]).set(disk["freeSpace"])
        sonarr_metrics.AVAILABLE_DISK_SIZE.labels(disk["path"]).set(disk["totalSpace"])

    sonarr_metrics.QUEUE_COUNT.set(data["queue"]["totalCount"])
    sonarr_metrics.QUEUE_ERROR.set(data["queue"]["errors"])
    sonarr_metrics.QUEUE_WARNING.set(data["queue"]["warnings"])

def scrape(config):

    url = config.get('url')
    api_key = config.get('api_key')

    return get_series(url, api_key)

def update_metrics(series, detailed):
    analyse_series(series["data"], detailed)
    update_system_data(series["system"])
