from prometheus_client import Gauge, Enum

# Scraping Stats
LAST_SCRAPE = Gauge('sportarr_last_scrape', 'Last time Sportarr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('sportarr_scrape_duration', 'Duration of Sportarr scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('sportarr_start_time', 'Sportarr start time', ['alias'] )
BUILD_TIME = Gauge('sportarr_build_time', 'Sportarr build time', ['alias'] )

# Queue Stats
QUEUE_COUNT = Gauge('sportarr_queue_count', 'Number of items in Sportarr queue', ['alias'] )
QUEUE_ERROR = Gauge('sportarr_queue_error', 'Item in Sportarr queue with error', ['alias'] )
QUEUE_WARNING = Gauge('sportarr_queue_warning', 'Item in Sportarr queue with warning', ['alias'] )

# Metrics for Total Count
SERIES_COUNT = Gauge('sportarr_series', 'Number of series in Sportarr', ['alias', 'path'])
SERIES_COUNT_T = Gauge('sportarr_series_total', 'Number of series in Sportarr', ['alias'] )
EPISODE_COUNT = Gauge('sportarr_episodes', 'Number of episodes in Sportarr', ['alias', 'path'])
EPISODE_COUNT_T = Gauge('sportarr_episodes_total', 'Number of episodes in Sportarr', ['alias'] )
TOTAL_DISK_SIZE = Gauge('sportarr_disk_size', 'Total disk size of Series in Sportarr', ['alias', 'path'])
TOTAL_DISK_SIZE_T = Gauge('sportarr_disk_size_total', 'Total disk size of Series in Sportarr', ['alias'] )
FREE_DISK_SIZE = Gauge('sportarr_free_disk_size', 'Free disk size in Sportarr', ['alias', 'path'])
AVAILABLE_DISK_SIZE = Gauge('sportarr_available_disk_size', 'Available disk size in Sportarr', ['alias', 'path'])

QUALITY_EPISODE_COUNT = Gauge('sportarr_quality_episodes', 'Number of episodes per quality in Sportarr', ['alias', 'quality', 'path'])
QUALITY_EPISODE_COUNT_T = Gauge('sportarr_quality_episodes_total', 'Number of episodes per quality in Sportarr', ['alias', 'quality'])
SERIES_GENRES_COUNT = Gauge('sportarr_genres_count', 'Number of Series per Genres in Sportarr', ['alias', 'genre', 'path'])
SERIES_GENRES_COUNT_T = Gauge('sportarr_genres_count_total', 'Number of Series per Genres in Sportarr', ['alias', 'genre'])

MISSING_EPISODE_COUNT = Gauge('sportarr_missing_episodes', 'Number of missing episodes in Sportarr', ['alias', 'path'])
MISSING_EPISODE_COUNT_T = Gauge('sportarr_missing_episodes_total', 'Number of missing episodes in Sportarr', ['alias'] )
MONITORED_SERIES = Gauge('sportarr_monitored_series', 'Number of monitored series in Sportarr', ['alias', 'path'])
MONITORED_SERIES_T = Gauge('sportarr_monitored_series_total', 'Number of monitored series in Sportarr', ['alias'] )
UNMONITORED_SERIES = Gauge('sportarr_unmonitored_series', 'Number of unmonitored series in Sportarr', ['alias', 'path'])
UNMONITORED_SERIES_T = Gauge('sportarr_unmonitored_series_total', 'Number of unmonitored series in Sportarr', ['alias'] )

# Continuing, Upcoming, Ended, Deleted
CONTINUING_SERIES = Gauge('sportarr_continuing_series', 'Number of continuing series in Sportarr', ['alias', 'path'])
CONTINUING_SERIES_T = Gauge('sportarr_continuing_series_total', 'Number of continuing series in Sportarr', ['alias'] )
UPCOMING_SERIES = Gauge('sportarr_upcoming_series', 'Number of upcoming series in Sportarr', ['alias', 'path'])
UPCOMING_SERIES_T = Gauge('sportarr_upcoming_series_total', 'Number of upcoming series in Sportarr', ['alias'] )
ENDED_SERIES = Gauge('sportarr_ended_series', 'Number of ended series in Sportarr', ['alias', 'path'])
ENDED_SERIES_T = Gauge('sportarr_ended_series_total', 'Number of ended series in Sportarr', ['alias'] )
DELETED_SERIES = Gauge('sportarr_deleted_series', 'Number of deleted series in Sportarr', ['alias', 'path'])
DELETED_SERIES_T = Gauge('sportarr_deleted_series_total', 'Number of deleted series in Sportarr', ['alias'] )

# Metrics per Series
SERIES_EPISODE_COUNT = Gauge('sportarr_series_episodes', 'Number of episodes in a series', ['alias', 'series'])
SERIES_SEASON_COUNT = Gauge('sportarr_series_seasons', 'Number of seasons in a series', ['alias', 'series'])
SERIES_DOWNLOAD_PERCENTAGE = Gauge('sportarr_series_download_percentage', 'Percentage of downloaded episodes in a series', ['alias', 'series'])
SERIES_MONITORED = Gauge('sportarr_series_monitored', 'Is the series monitored', ['alias', 'series'])
SERIES_DISK_SIZE = Gauge('sportarr_series_disk_size', 'Disk size of a series', ['alias', 'series'])
SERIES_MISSING_EPISODE_COUNT = Gauge('sportarr_series_missing_episodes', 'Number of missing episodes in a series', ['alias', 'series'])
