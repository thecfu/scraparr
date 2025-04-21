from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('jellyfin_last_scrape', 'Last time Jellyfin was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('jellyfin_scrape_duration', 'Duration of Jellyfin scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('jellyfin_start_time', 'Jellyfin start time', ['alias'] )
BUILD_TIME = Gauge('jellyfin_build_time', 'Jellyfin build time', ['alias'] )
NUMBER_OF_DEVICES = Gauge('jellyfin_number_of_devices', 'Jellyfin number of devices', ['alias'])
NUMBER_OF_USERS = Gauge('jellyfin_number_of_users', 'Jellyfin number of users', ['alias'])
NUMBER_OF_MOVIES = Gauge('jellyfin_number_of_movies', 'Jellyfin number of movies', ['alias'])
NUMBER_OF_SERIES = Gauge('jellyfin_number_of_series', 'Jellyfin number of series', ['alias'])
GENRES = Gauge('jellyfin_genres_total', 'Jellyfin number of genres', ['alias', 'genre'])
