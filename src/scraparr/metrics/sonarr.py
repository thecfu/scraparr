from prometheus_client import Gauge, Enum

# Scraping Stats
LAST_SCRAPE = Gauge('sonarr_last_scrape', 'Last time Sonarr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('sonarr_scrape_duration', 'Duration of Sonarr scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('sonarr_start_time', 'Sonarr start time', ['alias'] )
BUILD_TIME = Gauge('sonarr_build_time', 'Sonarr build time', ['alias'] )

# Queue Stats
QUEUE_COUNT = Gauge('sonarr_queue_count', 'Number of items in Sonarr queue', ['alias'] )
QUEUE_ERROR = Gauge('sonarr_queue_error', 'Item in Sonarr queue with error', ['alias'] )
QUEUE_WARNING = Gauge('sonarr_queue_warning', 'Item in Sonarr queue with warning', ['alias'] )

# Metrics for Total Count
SERIES_COUNT = Gauge('sonarr_series', 'Number of series in Sonarr', ['alias', 'path'])
SERIES_COUNT_T = Gauge('sonarr_series_total', 'Number of series in Sonarr', ['alias'] )
EPISODE_COUNT = Gauge('sonarr_episodes', 'Number of episodes in Sonarr', ['alias', 'path'])
EPISODE_COUNT_T = Gauge('sonarr_episodes_total', 'Number of episodes in Sonarr', ['alias'] )
TOTAL_DISK_SIZE = Gauge('sonarr_disk_size', 'Total disk size of Series in Sonarr', ['alias', 'path'])
TOTAL_DISK_SIZE_T = Gauge('sonarr_disk_size_total', 'Total disk size of Series in Sonarr', ['alias'] )
FREE_DISK_SIZE = Gauge('sonarr_free_disk_size', 'Free disk size in Sonarr', ['alias', 'path'])
AVAILABLE_DISK_SIZE = Gauge('sonarr_available_disk_size', 'Available disk size in Sonarr', ['alias', 'path'])

QUALITY_EPISODE_COUNT = Gauge('sonarr_quality_episodes', 'Number of episodes per quality in Sonarr', ['alias', 'quality', 'path'])
QUALITY_EPISODE_COUNT_T = Gauge('sonarr_quality_episodes_total', 'Number of episodes per quality in Sonarr', ['alias', 'quality'])
SERIES_GENRES_COUNT = Gauge('sonarr_genres_count', 'Number of Series per Genres in Sonarr', ['alias', 'genre', 'path'])
SERIES_GENRES_COUNT_T = Gauge('sonarr_genres_count_total', 'Number of Series per Genres in Sonarr', ['alias', 'genre'])

MISSING_EPISODE_COUNT = Gauge('sonarr_missing_episodes', 'Number of missing episodes in Sonarr', ['alias', 'path'])
MISSING_EPISODE_COUNT_T = Gauge('sonarr_missing_episodes_total', 'Number of missing episodes in Sonarr', ['alias'] )
MONITORED_SERIES = Gauge('sonarr_monitored_series', 'Number of monitored series in Sonarr', ['alias', 'path'])
MONITORED_SERIES_T = Gauge('sonarr_monitored_series_total', 'Number of monitored series in Sonarr', ['alias'] )
UNMONITORED_SERIES = Gauge('sonarr_unmonitored_series', 'Number of unmonitored series in Sonarr', ['alias', 'path'])
UNMONITORED_SERIES_T = Gauge('sonarr_unmonitored_series_total', 'Number of unmonitored series in Sonarr', ['alias'] )

# Continuing, Upcoming, Ended, Deleted
CONTINUING_SERIES = Gauge('sonarr_continuing_series', 'Number of continuing series in Sonarr', ['alias', 'path'])
CONTINUING_SERIES_T = Gauge('sonarr_continuing_series_total', 'Number of continuing series in Sonarr', ['alias'] )
UPCOMING_SERIES = Gauge('sonarr_upcoming_series', 'Number of upcoming series in Sonarr', ['alias', 'path'])
UPCOMING_SERIES_T = Gauge('sonarr_upcoming_series_total', 'Number of upcoming series in Sonarr', ['alias'] )
ENDED_SERIES = Gauge('sonarr_ended_series', 'Number of ended series in Sonarr', ['alias', 'path'])
ENDED_SERIES_T = Gauge('sonarr_ended_series_total', 'Number of ended series in Sonarr', ['alias'] )
DELETED_SERIES = Gauge('sonarr_deleted_series', 'Number of deleted series in Sonarr', ['alias', 'path'])
DELETED_SERIES_T = Gauge('sonarr_deleted_series_total', 'Number of deleted series in Sonarr', ['alias'] )

# Metrics per Series
SERIES_EPISODE_COUNT = Gauge('sonarr_series_episodes', 'Number of episodes in a series', ['alias', 'series'])
SERIES_SEASON_COUNT = Gauge('sonarr_series_seasons', 'Number of seasons in a series', ['alias', 'series'])
SERIES_DOWNLOAD_PERCENTAGE = Gauge('sonarr_series_download_percentage', 'Percentage of downloaded episodes in a series', ['alias', 'series'])
SERIES_MONITORED = Gauge('sonarr_series_monitored', 'Is the series monitored', ['alias', 'series'])
SERIES_DISK_SIZE = Gauge('sonarr_series_disk_size', 'Disk size of a series', ['alias', 'series'])
SERIES_MISSING_EPISODE_COUNT = Gauge('sonarr_series_missing_episodes', 'Number of missing episodes in a series', ['alias', 'series'])
