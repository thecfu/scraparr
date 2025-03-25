from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('whisparr_last_scrape', 'Last time Whisparr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('whisparr_scrape_duration', 'Duration of Whisparr scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('whisparr_start_time', 'Whisparr start time', ['alias'] )
BUILD_TIME = Gauge('whisparr_build_time', 'Whisparr build time', ['alias'] )

# Queue Stats
QUEUE_COUNT = Gauge('whisparr_queue_count', 'Number of items in Whisparr queue', ['alias'] )
QUEUE_ERROR = Gauge('whisparr_queue_error', 'Item in Whisparr queue with error', ['alias'] )
QUEUE_WARNING = Gauge('whisparr_queue_warning', 'Item in Whisparr queue with warning', ['alias'] )

# Metrics for Total Count
SERIES_COUNT = Gauge('whisparr_series', 'Number of series in Whisparr', ['alias', 'path'])
SERIES_COUNT_T = Gauge('whisparr_series_total', 'Number of series in Whisparr', ['alias'] )
EPISODE_COUNT = Gauge('whisparr_episodes', 'Number of episodes in Whisparr', ['alias', 'path'])
EPISODE_COUNT_T = Gauge('whisparr_episodes_total', 'Number of episodes in Whisparr', ['alias'] )
TOTAL_DISK_SIZE = Gauge('whisparr_disk_size', 'Total disk size of Series in Whisparr', ['alias', 'path'])
TOTAL_DISK_SIZE_T = Gauge('whisparr_disk_size_total', 'Total disk size of Series in Whisparr', ['alias'] )
FREE_DISK_SIZE = Gauge('whisparr_free_disk_size', 'Free disk size in Whisparr', ['alias', 'path'])
AVAILABLE_DISK_SIZE = Gauge('whisparr_available_disk_size', 'Available disk size in Whisparr', ['alias', 'path'])

QUALITY_EPISODE_COUNT = Gauge('whisparr_quality_episodes', 'Number of episodes per quality in Whisparr', ['alias', 'quality', 'path'])
QUALITY_EPISODE_COUNT_T = Gauge('whisparr_quality_episodes_total', 'Number of episodes per quality in Whisparr', ['alias', 'quality'])
SERIES_GENRES_COUNT = Gauge('whisparr_genres_count', 'Number of Series per Genres in Whisparr', ['alias', 'genre', 'path'])
SERIES_GENRES_COUNT_T = Gauge('whisparr_genres_count_total', 'Number of Series per Genres in Whisparr', ['alias', 'genre'])

MISSING_EPISODE_COUNT = Gauge('whisparr_missing_episodes', 'Number of missing episodes in Whisparr', ['alias', 'path'])
MISSING_EPISODE_COUNT_T = Gauge('whisparr_missing_episodes_total', 'Number of missing episodes in Whisparr', ['alias'] )
MONITORED_SERIES = Gauge('whisparr_monitored_series', 'Number of monitored series in Whisparr', ['alias', 'path'])
MONITORED_SERIES_T = Gauge('whisparr_monitored_series_total', 'Number of monitored series in Whisparr', ['alias'] )
UNMONITORED_SERIES = Gauge('whisparr_unmonitored_series', 'Number of unmonitored series in Whisparr', ['alias', 'path'])
UNMONITORED_SERIES_T = Gauge('whisparr_unmonitored_series_total', 'Number of unmonitored series in Whisparr', ['alias'] )

# Continuing, Upcoming, Ended, Deleted
CONTINUING_SERIES = Gauge('whisparr_continuing_series', 'Number of continuing series in Whisparr', ['alias', 'path'])
CONTINUING_SERIES_T = Gauge('whisparr_continuing_series_total', 'Number of continuing series in Whisparr', ['alias'] )
UPCOMING_SERIES = Gauge('whisparr_upcoming_series', 'Number of upcoming series in Whisparr', ['alias', 'path'])
UPCOMING_SERIES_T = Gauge('whisparr_upcoming_series_total', 'Number of upcoming series in Whisparr', ['alias'] )
ENDED_SERIES = Gauge('whisparr_ended_series', 'Number of ended series in Whisparr', ['alias', 'path'])
ENDED_SERIES_T = Gauge('whisparr_ended_series_total', 'Number of ended series in Whisparr', ['alias'] )
DELETED_SERIES = Gauge('whisparr_deleted_series', 'Number of deleted series in Whisparr', ['alias', 'path'])
DELETED_SERIES_T = Gauge('whisparr_deleted_series_total', 'Number of deleted series in Whisparr', ['alias'] )

# Metrics per Series
SERIES_EPISODE_COUNT = Gauge('whisparr_series_episodes', 'Number of episodes in a series', ['alias', 'series'])
SERIES_SEASON_COUNT = Gauge('whisparr_series_seasons', 'Number of seasons in a series', ['alias', 'series'])
SERIES_DOWNLOAD_PERCENTAGE = Gauge('whisparr_series_download_percentage', 'Percentage of downloaded episodes in a series', ['alias', 'series'])
SERIES_MONITORED = Gauge('whisparr_series_monitored', 'Is the series monitored', ['alias', 'series'])
SERIES_DISK_SIZE = Gauge('whisparr_series_disk_size', 'Disk size of a series', ['alias', 'series'])
SERIES_MISSING_EPISODE_COUNT = Gauge('whisparr_series_missing_episodes', 'Number of missing episodes in a series', ['alias', 'series'])
