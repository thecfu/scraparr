"""Metrics for the Bazarr Service"""
from prometheus_client import Gauge

LAST_SCRAPE = Gauge("bazarr_last_scrape", "Last time the Bazarr Service was scraped", ["alias"])
SCRAPE_DURATION = Gauge("bazarr_scrape_duration", "Duration of the Bazarr scrape", ["alias"])

START_TIME = Gauge("bazarr_start_time", "Start Time of the Bazarr Service", ["alias"])
BUILD_TIME = Gauge("bazarr_build_time", "Build Time of the Bazarr Service", ["alias"])

SERIES_COUNT_TOTAL = Gauge("bazarr_series_total", "Total Number of Series", ["alias"])
MOVIE_COUNT_TOTAL = Gauge("bazarr_movies_total", "Total Number of Movies", ["alias"])

WANTED_EPISODE_COUNT = Gauge("bazarr_wanted_episodes", "Number of Wanted Episodes", ["alias", "series"])
WANTED_EPISODE_COUNT_TOTAL = Gauge("bazarr_wanted_episodes_total", "Total Number of Wanted Episodes", ["alias"])
WANTED_MOVIE_COUNT = Gauge("bazarr_wanted_movies", "Number of Wanted Movies", ["alias", "movie"])
WANTED_MOVIE_COUNT_TOTAL = Gauge("bazarr_wanted_movies_total", "Total Number of Wanted Movies", ["alias"])

PROVIDER_COUNT = Gauge("bazarr_providers", "Number of Providers", ["alias"])
PROVIDER_STATUS = Gauge("bazarr_provider_status", "Status of the Provider", ["alias", "provider", "status"])
