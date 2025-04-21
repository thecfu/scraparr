"""
Module to handle the Metrics of the Jellyfin Service
"""
import time
import logging
import requests
import scraparr.metrics.jellyfin as jellyfin_metrics
from scraparr.metrics.general import UP
from scraparr.connectors import util

QUERY = "SortBy=SortName%2CProductionYear&SortOrder=Ascending&Recursive=true"

def get_header(api_key):
    """Translate the API Key into a Header for Jellyfin"""
    token = f"Mediabrowser Token={api_key}"
    return {"Authorization": token}

def get_number_of_devices(url, headers_auth, alias):
    """Grab the Devices from the Jellyfin Endpoint"""
    try:
        res = requests.get(f"{url}/Devices", headers=headers_auth, timeout=10)
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        UP.labels(alias).set(1)
        return res.json()['TotalRecordCount']
    except requests.exceptions.RequestException as e:
        UP.labels(alias).set(0)
        print(f"Request failed: {e}")
        return None


def get_genres(url, headers_auth, alias):
    """Grab the Genres from the Jellyfin Endpoint"""
    try:
        res = requests.get(f"{url}/Genres", headers=headers_auth, timeout=10)
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        UP.labels(alias).set(1)
        data = res.json()
        genre_names = {item["Name"]: 1 for item in data.get("Items", [])}
        return genre_names
    except requests.exceptions.RequestException as e:
        UP.labels(alias).set(0)
        print(f"Request failed: {e}")
        return None

def get_number_of_user(url, headers_auth, alias):
    """Grab the Users from the Jellyfin Endpoint"""
    try:
        res = requests.get(f"{url}/Users", headers=headers_auth, timeout=10)
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        UP.labels(alias).set(1)
        data = res.json()
        return len(data)
    except requests.exceptions.RequestException as e:
        UP.labels(alias).set(0)
        print(f"Request failed: {e}")
        return None

def get_number_of_movies(url, headers_auth, alias):
    """Grab the Movies from the Jellyfin Endpoint"""
    try:
        res = requests.get(f"{url}/Items?{QUERY}&IncludeItemTypes=Movie",
                           headers=headers_auth, timeout=10)
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        UP.labels(alias).set(1)
        return res.json()['TotalRecordCount']
    except requests.exceptions.RequestException as e:
        UP.labels(alias).set(0)
        print(f"Request failed: {e}")
        return None

def get_number_of_series(url, headers_auth, alias):
    """Grab the Series from the Jellyfin Endpoint"""
    try:
        res = requests.get(f"{url}/Items?{QUERY}&IncludeItemTypes=Series",
                           headers=headers_auth, timeout=10)
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        UP.labels(alias).set(1)
        return res.json()['TotalRecordCount']
    except requests.exceptions.RequestException as e:
        UP.labels(alias).set(0)
        print(f"Request failed: {e}")
        return None

def scrape(config):
    """Scrape the Jellyfin Service"""
    initial_time = time.time()
    url = config.get('url')
    api_key = config.get('api_key')
    alias = config.get('alias', 'jellyfin')

    headers_auth=get_header(api_key)

    n_devices = get_number_of_devices(url, headers_auth, alias)
    n_user = get_number_of_user(url, headers_auth, alias)
    n_movies = get_number_of_movies(url, headers_auth, alias)
    n_series = get_number_of_series(url, headers_auth, alias)
    genres = get_genres(url, headers_auth, alias)

    end_time = time.time()
    jellyfin_metrics.LAST_SCRAPE.labels(alias).set(end_time)
    jellyfin_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)

    if any((n_devices, n_user, n_movies, n_series, genres) is None):
        logging.error("No Data found for Jellyfin, assuming Failure")
        return None
    return{
        "n_devices": n_devices,
        "n_user": n_user,
        "n_movies": n_movies,
        "n_series": n_series,
        "genres": genres
    }

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Jellyfin Service"""
    jellyfin_metrics.JELLYFIN_NUMBER_OF_DEVICES.labels(alias).set(data["n_devices"])
    jellyfin_metrics.JELLYFIN_NUMBER_OF_USERS.labels(alias).set(data["n_devices"])
    jellyfin_metrics.JELLYFIN_NUMBER_OF_MOVIES.labels(alias).set(data["n_movies"])
    jellyfin_metrics.JELLYFIN_NUMBER_OF_SERIES.labels(alias).set(data["n_series"])

    jellyfin_metrics.JELLYFIN_GENRES.clear()
    util.total_with_label(
        [{
            "total": data["genres"]},
            None,
            jellyfin_metrics.JELLYFIN_GENRES
        ],
        alias)
