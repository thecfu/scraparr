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

# Session Details
SESSION_LABELS = ['alias', 'username', 'device', 'client', 'type', 'method']

SESSION_POSITION = Gauge(
    'jellyfin_session_position_seconds',
    'Current playback position in seconds',
    SESSION_LABELS)
SESSION_DURATION = Gauge(
    'jellyfin_session_duration_seconds',
    'Total media duration in seconds',
    SESSION_LABELS)
SESSION_TRANSCODING = Gauge(
    'jellyfin_session_transcoding',
    '1 if session is transcoding, 0 otherwise',
    SESSION_LABELS)
SESSION_PAUSED = Gauge(
    'jellyfin_session_paused',
    '1 if session is paused, 0 if playing',
    SESSION_LABELS)
SESSION_BITRATE = Gauge(
    'jellyfin_session_bitrate_bits',
    'Current stream bitrate in bits per second',
    SESSION_LABELS)

SESSION_CLIENT_INFO = Gauge(
    'jellyfin_session_client_info',
    'Info gauge for active session client versions',
    ['alias', 'username', 'device', 'client', 'client_version'])
