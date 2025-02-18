from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('radarr_last_scrape', 'Last time Radarr was scraped')
SCRAPE_DURATION = Gauge('radarr_scrape_duration', 'Duration of Radarr scrape')

# Status Stats
START_TIME = Gauge('radarr_start_time', 'Radarr start time')
BUILD_TIME = Gauge('radarr_build_time', 'Radarr build time')

# Queue Stats
QUEUE_COUNT = Gauge('radarr_queue_count', 'Number of items in Radarr queue')
QUEUE_ERROR = Gauge('radarr_queue_error', 'Item in Radarr queue with error')
QUEUE_WARNING = Gauge('radarr_queue_warning', 'Item in Radarr queue with warning')

# Metrics for Total Count
MOVIE_COUNT = Gauge('radarr_movies', 'Number of movies in Radarr', ['path'])
MOVIE_COUNT_T = Gauge('radarr_movies_total', 'Number of movies in Radarr')
TOTAL_DISK_SIZE = Gauge('radarr_disk_size', 'Total disk size of movies in Radarr', ['path'])
TOTAL_DISK_SIZE_T = Gauge('radarr_disk_size_total', 'Total disk size of movies in Radarr')
FREE_DISK_SIZE = Gauge('radarr_free_disk_size', 'Free disk size in Radarr', ['path'])
AVAILABLE_DISK_SIZE = Gauge('radarr_available_disk_size', 'Available disk size in Radarr', ['path'])

QUALITY_MOVIE_COUNT = Gauge('radarr_quality_movies', 'Number of movies per quality in Radarr', ['quality', 'path'])
QUALITY_MOVIE_COUNT_T = Gauge('radarr_quality_movies_total', 'Number of movies per quality in Radarr', ['quality'])
MOVIE_GENRES_COUNT = Gauge('radarr_genres_count', 'Number of Movies per Genres in Radarr', ['genre', 'path'])
MOVIE_GENRES_COUNT_T = Gauge('radarr_genres_count_total', 'Number of Movies per Genres in Radarr', ['genre'])

MISSING_MOVIES_COUNT = Gauge('radarr_missing_movies', 'Number of missing movies in Radarr', ['path'])
MISSING_MOVIES_COUNT_T = Gauge('radarr_missing_movies_total', 'Number of missing movies in Radarr')
MONITORED_MOVIES = Gauge('radarr_monitored_movies', 'Number of monitored movies in Radarr', ['path'])
MONITORED_MOVIES_T = Gauge('radarr_monitored_movies_total', 'Number of monitored movies in Radarr')
UNMONITORED_MOVIES = Gauge('radarr_unmonitored_movies', 'Number of unmonitored movies in Radarr', ['path'])
UNMONITORED_MOVIES_T = Gauge('radarr_unmonitored_movies_total', 'Number of unmonitored movies in Radarr')

# TBA movies
TBA_MOVIES = Gauge('radarr_tba_movies', 'Number of TBA movies in Radarr', ['path'])
TBA_MOVIES_T = Gauge('radarr_tba_movies_total', 'Total number of TBA movies in Radarr')

# In Cinemas movies
IN_CINEMAS_MOVIES = Gauge('radarr_in_cinemas_movies', 'Number of movies in cinemas in Radarr', ['path'])
IN_CINEMAS_MOVIES_T = Gauge('radarr_in_cinemas_movies_total', 'Total number of movies in cinemas in Radarr')

# Announced movies
ANNOUNCED_MOVIES = Gauge('radarr_announced_movies', 'Number of announced movies in Radarr', ['path'])
ANNOUNCED_MOVIES_T = Gauge('radarr_announced_movies_total', 'Total number of announced movies in Radarr')

# Released movies
RELEASED_MOVIES = Gauge('radarr_released_movies', 'Number of released movies in Radarr', ['path'])
RELEASED_MOVIES_T = Gauge('radarr_released_movies_total', 'Total number of released movies in Radarr')

# Deleted movies
DELETED_MOVIES = Gauge('radarr_deleted_movies', 'Number of deleted movies in Radarr', ['path'])
DELETED_MOVIES_T = Gauge('radarr_deleted_movies_total', 'Total number of deleted movies in Radarr')
# Metrics per Movie
MOVIE_MISSING = Gauge('radarr_movie_missing', 'Is the movie missing', ['movie'])
MOVIE_FILE_COUNT = Gauge('radarr_movie_files', 'Number of files in a movie', ['movie'])
MOVIE_MONITORED = Gauge('radarr_movie_monitored', 'Is the movie monitored', ['movie'])
MOVIE_DISK_SIZE = Gauge('radarr_movie_disk_size', 'Disk size of a movie', ['movie'])
