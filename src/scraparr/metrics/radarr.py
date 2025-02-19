from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('radarr_last_scrape', 'Last time Radarr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('radarr_scrape_duration', 'Duration of Radarr scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('radarr_start_time', 'Radarr start time', ['alias'] )
BUILD_TIME = Gauge('radarr_build_time', 'Radarr build time', ['alias'] )

# Queue Stats
QUEUE_COUNT = Gauge('radarr_queue_count', 'Number of items in Radarr queue', ['alias'] )
QUEUE_ERROR = Gauge('radarr_queue_error', 'Item in Radarr queue with error', ['alias'] )
QUEUE_WARNING = Gauge('radarr_queue_warning', 'Item in Radarr queue with warning', ['alias'] )

# Metrics for Total Count
MOVIE_COUNT = Gauge('radarr_movies', 'Number of movies in Radarr', ['alias', 'path'])
MOVIE_COUNT_T = Gauge('radarr_movies_total', 'Number of movies in Radarr', ['alias'] )
TOTAL_DISK_SIZE = Gauge('radarr_disk_size', 'Total disk size of movies in Radarr', ['alias', 'path'])
TOTAL_DISK_SIZE_T = Gauge('radarr_disk_size_total', 'Total disk size of movies in Radarr', ['alias'] )
FREE_DISK_SIZE = Gauge('radarr_free_disk_size', 'Free disk size in Radarr', ['alias', 'path'])
AVAILABLE_DISK_SIZE = Gauge('radarr_available_disk_size', 'Available disk size in Radarr', ['alias', 'path'])

QUALITY_MOVIE_COUNT = Gauge('radarr_quality_movies', 'Number of movies per quality in Radarr', ['alias', 'quality', 'path'])
QUALITY_MOVIE_COUNT_T = Gauge('radarr_quality_movies_total', 'Number of movies per quality in Radarr', ['alias', 'quality'])
MOVIE_GENRES_COUNT = Gauge('radarr_genres_count', 'Number of Movies per Genres in Radarr', ['alias', 'genre', 'path'])
MOVIE_GENRES_COUNT_T = Gauge('radarr_genres_count_total', 'Number of Movies per Genres in Radarr', ['alias', 'genre'])

MISSING_MOVIES_COUNT = Gauge('radarr_missing_movies', 'Number of missing movies in Radarr', ['alias', 'path'])
MISSING_MOVIES_COUNT_T = Gauge('radarr_missing_movies_total', 'Number of missing movies in Radarr', ['alias'] )
MONITORED_MOVIES = Gauge('radarr_monitored_movies', 'Number of monitored movies in Radarr', ['alias', 'path'])
MONITORED_MOVIES_T = Gauge('radarr_monitored_movies_total', 'Number of monitored movies in Radarr', ['alias'] )
UNMONITORED_MOVIES = Gauge('radarr_unmonitored_movies', 'Number of unmonitored movies in Radarr', ['alias', 'path'])
UNMONITORED_MOVIES_T = Gauge('radarr_unmonitored_movies_total', 'Number of unmonitored movies in Radarr', ['alias'] )

# TBA movies
TBA_MOVIES = Gauge('radarr_tba_movies', 'Number of TBA movies in Radarr', ['alias', 'path'])
TBA_MOVIES_T = Gauge('radarr_tba_movies_total', 'Total number of TBA movies in Radarr', ['alias'] )

# In Cinemas movies
IN_CINEMAS_MOVIES = Gauge('radarr_in_cinemas_movies', 'Number of movies in cinemas in Radarr', ['alias', 'path'])
IN_CINEMAS_MOVIES_T = Gauge('radarr_in_cinemas_movies_total', 'Total number of movies in cinemas in Radarr', ['alias'] )

# Announced movies
ANNOUNCED_MOVIES = Gauge('radarr_announced_movies', 'Number of announced movies in Radarr', ['alias', 'path'])
ANNOUNCED_MOVIES_T = Gauge('radarr_announced_movies_total', 'Total number of announced movies in Radarr', ['alias'] )

# Released movies
RELEASED_MOVIES = Gauge('radarr_released_movies', 'Number of released movies in Radarr', ['alias', 'path'])
RELEASED_MOVIES_T = Gauge('radarr_released_movies_total', 'Total number of released movies in Radarr', ['alias'] )

# Deleted movies
DELETED_MOVIES = Gauge('radarr_deleted_movies', 'Number of deleted movies in Radarr', ['alias', 'path'])
DELETED_MOVIES_T = Gauge('radarr_deleted_movies_total', 'Total number of deleted movies in Radarr', ['alias'] )
# Metrics per Movie
MOVIE_MISSING = Gauge('radarr_movie_missing', 'Is the movie missing', ['alias', 'movie'])
MOVIE_FILE_COUNT = Gauge('radarr_movie_files', 'Number of files in a movie', ['alias', 'movie'])
MOVIE_MONITORED = Gauge('radarr_movie_monitored', 'Is the movie monitored', ['alias', 'movie'])
MOVIE_DISK_SIZE = Gauge('radarr_movie_disk_size', 'Disk size of a movie', ['alias', 'movie'])
