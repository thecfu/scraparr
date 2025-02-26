"""
Module to handle the Metrics of the Bazarr Service
"""

import time
import logging
from dateutil.parser import parse

from scraparr.connectors.util import get
from scraparr.metrics.general import UP
import scraparr.metrics.bazarr as bazarr_metrics

def get_system_data(url, api_key, alias):
    """Grab the System Data from the Bazarr Endpoint"""

    initial_time = time.time()
    res = get(f"{url}/api/system/status", api_key)["data"]
    end_time = time.time()

    if res == {}:
        UP.labels(alias, 'bazarr').set(0)
    else:
        UP.labels(alias, 'bazarr').set(1)
        bazarr_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        bazarr_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)

        bazarr_metrics.START_TIME.labels(alias).set(res['start_time'])

        releases = get(f"{url}/api/system/releases", api_key)

        if releases != {}:
            for release in releases["data"]:
                if release["name"] == f"v{res['bazarr_version']}":
                    build_time = parse(release["date"]).timestamp()
                    bazarr_metrics.BUILD_TIME.labels(alias).set(build_time)
                    break

    return res

def get_providers(url, api_key, alias):
    """Grab the Providers from the Bazarr Endpoint"""

    initial_time = time.time()
    res = get(f"{url}/api/providers", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels(alias, 'bazarr').set(0)
    else:
        UP.labels(alias, 'bazarr').set(1)
        bazarr_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        bazarr_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)

    return res

def get_data(url, api_key):
    """Grab the Data from the Bazarr Endpoint"""

    series = get(f"{url}/api/series", api_key)
    movies = get(f"{url}/api/movies", api_key)

    return {"series": series, "movies": movies}

def get_wanted(url, api_key):
    """Grab the Wanted from the Bazarr Endpoint"""

    movies = get(f"{url}/api/movies/wanted", api_key)
    episodes = get(f"{url}/api/episodes/wanted", api_key)

    return {"movies": movies, "episodes": episodes}

def analyse_data(data, wanted, detailed, alias):
    """Analyse the Data and set the Correct Metrics"""

    bazarr_metrics.WANTED_EPISODE_COUNT.clear()
    bazarr_metrics.WANTED_MOVIE_COUNT.clear()

    wanted_episodes = {}
    wanted_movies = {}
    count = {"movies": 0, "series": 0}

    for series in data["series"]["data"]:
        if series["profileId"] is not None:
            count["series"] += 1
    for movie in data["movies"]["data"]:
        if movie["profileId"] is not None:
            count["movies"] += 1

    bazarr_metrics.WANTED_MOVIE_COUNT_TOTAL.labels(alias).set(wanted["movies"]["total"])
    bazarr_metrics.WANTED_EPISODE_COUNT_TOTAL.labels(alias).set(wanted["episodes"]["total"])

    if detailed:
        for wanted_ep in wanted["episodes"]["data"]:
            wanted_episodes[wanted_ep["seriesTitle"]] = (wanted_episodes
                                                         .get(wanted_ep["seriesTitle"], 0)
                                                         + 1)

        for wanted_mov in wanted["movies"]["data"]:
            wanted_movies[wanted_mov["title"]] = wanted_movies.get(wanted_mov["title"], 0) + 1

        for series, s_count in wanted_episodes.items():
            bazarr_metrics.WANTED_EPISODE_COUNT.labels(alias, series).set(s_count)
        for movie, m_count in wanted_movies.items():
            bazarr_metrics.WANTED_MOVIE_COUNT.labels(alias, movie).set(m_count)

    bazarr_metrics.SERIES_COUNT_TOTAL.labels(alias).set(count["series"])
    bazarr_metrics.MOVIE_COUNT_TOTAL.labels(alias).set(count["movies"])

def analyse_providers(providers, alias):
    """Analyse the Providers and set the Correct Metrics"""

    bazarr_metrics.PROVIDER_COUNT.labels(alias).set(len(providers["data"]))
    bazarr_metrics.PROVIDER_STATUS.clear()

    for provider in providers["data"]:
        bazarr_metrics.PROVIDER_STATUS.labels(alias, provider["name"], provider["status"]).set(1)


def scrape(config):
    """Scrape the Bazarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    alias = config.get('alias', 'bazarr')

    system = get_system_data(url, api_key, alias)
    providers = get_providers(url, api_key, alias)
    data = get_data(url, api_key)
    wanted = get_wanted(url, api_key)

    if system and providers and data and wanted:
        return {"data": data, "system": system, "providers": providers, "wanted": wanted}

    logging.error("No Data found for Bazarr, assuming Failure")
    return {}

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Bazarr Service"""

    analyse_providers(data["providers"], alias)
    analyse_data(data["data"], data["wanted"], detailed, alias)
