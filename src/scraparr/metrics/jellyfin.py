from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('jellyfin_last_scrape', 'Last time Jellyfin was scraped', ['alias'])
SCRAPE_DURATION = Gauge('jellyfin_scrape_duration', 'Duration of Jellyfin scrape', ['alias'])

VERSION = Gauge('jellyfin_version', 'Jellyfin version', ['alias', 'version'])
HAS_UPDATE = Gauge('jellyfin_has_update', 'Jellyfin has update available', ['alias'])

# Status Stats
NUMBER_OF_DEVICES = Gauge('jellyfin_number_of_devices', 'Jellyfin number of devices', ['alias'])
NUMBER_OF_USERS = Gauge('jellyfin_number_of_users', 'Jellyfin number of users', ['alias'])
NUMBER_OF_MOVIES = Gauge('jellyfin_number_of_movies', 'Jellyfin number of movies', ['alias'])
NUMBER_OF_SERIES = Gauge('jellyfin_number_of_series', 'Jellyfin number of series', ['alias'])
GENRES = Gauge('jellyfin_genres_total', 'Jellyfin number of genres', ['alias', 'genre'])

SESSIONS_T = Gauge('jellyfin_sessions_total', 'Jellyfin number of sessions within Configured amount of Seconds', ['alias'])
SESSIONS = Gauge('jellyfin_sessions', 'Jellyfin number of sessions within Configured amount of Seconds', ['alias', 'user_id', 'user_name'])