from prometheus_client import Gauge, Enum

# Scraping Stats
LAST_SCRAPE = Gauge('jellyfin_last_scrape', 'Last time Jellyfin was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('jellyfin_scrape_duration', 'Duration of Jellyfin scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('jellyfin_start_time', 'Jellyfin start time', ['alias'] )
BUILD_TIME = Gauge('jellyfin_build_time', 'Jellyfin build time', ['alias'] )
JELLYFIN_NUMBER_OF_DEVICES = ('jellyfin_number_of_devices', 'Jellyfin number of devices', ['alias'])
JELLYFIN_NUMBER_OF_USERS = ('jellyfin_number_of_users', 'Jellyfin number of users', ['alias'])
JELLYFIN_NUMBER_OF_MOVIES = ('jellyfin_number_of_movies', 'Jellyfin number of movies', ['alias'])
JELLYFIN_NUMBER_OF_SERIES = ('jellyfin_number_of_series', 'Jellyfin number of series', ['alias'])