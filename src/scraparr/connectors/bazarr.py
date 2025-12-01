"""
Module to handle the Metrics of the Bazarr Service
"""

import time
from dateutil.parser import parse

from scraparr.connectors.module import ConnectorModule
from scraparr.connectors.util import get
from scraparr.metrics.general import UP
import scraparr.metrics.bazarr as bazarr_metrics

class Module(ConnectorModule):
    """Module Class for Bazarr"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "bazarr")

    def clear(self):
        """Clear Radarr metrics to remove any previous data."""
        bazarr_metrics.WANTED_EPISODE_COUNT.remove_by_labels({"alias": self.alias})
        bazarr_metrics.WANTED_MOVIE_COUNT.remove_by_labels({"alias": self.alias})
        bazarr_metrics.PROVIDER_STATUS.remove_by_labels({"alias": self.alias})

    def scrape(self):
        """Scrape the Bazarr Service"""

        system = self.get_system_data()
        providers = self.get_providers()
        data = self.get_data()
        wanted = self.get_wanted()

        if system and providers and data and wanted:
            return {"data": data, "system": system, "providers": providers, "wanted": wanted}
        return {}

    def update_metrics(self, data):
        """Update the Metrics for the Bazarr Service"""

        self.analyse_providers(data["providers"])
        self.analyse_data(data["data"], data["wanted"])

    def analyse_providers(self, providers):
        """Analyse the Providers and set the Correct Metrics"""

        bazarr_metrics.PROVIDER_COUNT.labels(self.alias).set(len(providers["data"]))

        for provider in providers["data"]:
            bazarr_metrics.PROVIDER_STATUS.labels(
                self.alias,
                provider["name"],
                provider["status"]
            ).set(1)

    def get_system_data(self):
        """Grab the System Data from the Bazarr Endpoint"""

        initial_time = time.time()
        res = get(f"{self.url}/api/system/status", self.api_key)
        end_time = time.time()

        if res == {}:
            UP.labels(self.alias, 'bazarr').set(0)
            return res

        data = res["data"]

        UP.labels(self.alias, 'bazarr').set(1)
        bazarr_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
        bazarr_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        bazarr_metrics.START_TIME.labels(self.alias).set(data['start_time'])

        releases = get(f"{self.url}/api/system/releases", self.api_key)

        if releases != {}:
            for release in releases["data"]:
                if release["name"] == f"v{data['bazarr_version']}":
                    build_time = parse(release["date"]).timestamp()
                    bazarr_metrics.BUILD_TIME.labels(self.alias).set(build_time)
                    break

        return data

    def get_providers(self):
        """Grab the Providers from the Bazarr Endpoint"""

        initial_time = time.time()
        res = get(f"{self.url}/api/providers", self.api_key)
        end_time = time.time()

        if res == {}:
            UP.labels(self.alias, 'bazarr').set(0)
        else:
            UP.labels(self.alias, 'bazarr').set(1)
            bazarr_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
            bazarr_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        return res

    def get_data(self):
        """Grab the Data from the Bazarr Endpoint"""

        series = get(f"{self.url}/api/series", self.api_key)
        movies = get(f"{self.url}/api/movies", self.api_key)

        return {"series": series, "movies": movies}

    def get_wanted(self):
        """Grab the Wanted from the Bazarr Endpoint"""

        movies = get(f"{self.url}/api/movies/wanted", self.api_key)
        episodes = get(f"{self.url}/api/episodes/wanted", self.api_key)

        return {"movies": movies, "episodes": episodes}

    def analyse_data(self, data, wanted):
        """Analyse the Data and set the Correct Metrics"""

        wanted_episodes = {}
        wanted_movies = {}
        count = {"movies": 0, "series": 0}

        for series in data["series"]["data"]:
            if series["profileId"] is not None:
                count["series"] += 1
        for movie in data["movies"]["data"]:
            if movie["profileId"] is not None:
                count["movies"] += 1

        (bazarr_metrics.WANTED_MOVIE_COUNT_TOTAL.labels(self.alias)
            .set(wanted["movies"]["total"]))
        (bazarr_metrics.WANTED_EPISODE_COUNT_TOTAL.labels(self.alias)
            .set(wanted["episodes"]["total"]))

        if self.detailed:
            for wanted_ep in wanted["episodes"]["data"]:
                wanted_episodes[wanted_ep["seriesTitle"]] = (wanted_episodes
                                                             .get(wanted_ep["seriesTitle"], 0)
                                                             + 1)

            for wanted_mov in wanted["movies"]["data"]:
                wanted_movies[wanted_mov["title"]] = wanted_movies.get(wanted_mov["title"], 0) + 1

            for series, s_count in wanted_episodes.items():
                bazarr_metrics.WANTED_EPISODE_COUNT.labels(self.alias, series).set(s_count)
            for movie, m_count in wanted_movies.items():
                bazarr_metrics.WANTED_MOVIE_COUNT.labels(self.alias, movie).set(m_count)

        bazarr_metrics.SERIES_COUNT_TOTAL.labels(self.alias).set(count["series"])
        bazarr_metrics.MOVIE_COUNT_TOTAL.labels(self.alias).set(count["movies"])
