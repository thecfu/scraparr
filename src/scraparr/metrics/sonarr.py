from prometheus_client import Gauge, Enum

# Scraping Stats
LAST_SCRAPE = Gauge('sonarr_last_scrape', 'Last time Sonarr was scraped')
SCRAPE_DURATION = Gauge('sonarr_scrape_duration', 'Duration of Sonarr scrape')

# Status Stats
START_TIME = Gauge('sonarr_start_time', 'Sonarr start time')
BUILD_TIME = Gauge('sonarr_build_time', 'Sonarr build time')

# Queue Stats
QUEUE_COUNT = Gauge('sonarr_queue_count', 'Number of items in Sonarr queue')
QUEUE_ERROR = Gauge('sonarr_queue_error', 'Item in Sonarr queue with error')
QUEUE_WARNING = Gauge('sonarr_queue_warning', 'Item in Sonarr queue with warning')

# Metrics for Total Count
SERIES_COUNT = Gauge('sonarr_series', 'Number of series in Sonarr', ['path'])
SERIES_COUNT_T = Gauge('sonarr_series_total', 'Number of series in Sonarr')
EPISODE_COUNT = Gauge('sonarr_episodes', 'Number of episodes in Sonarr', ['path'])
EPISODE_COUNT_T = Gauge('sonarr_episodes_total', 'Number of episodes in Sonarr')
TOTAL_DISK_SIZE = Gauge('sonarr_disk_size', 'Total disk size of Series in Sonarr', ['path'])
TOTAL_DISK_SIZE_T = Gauge('sonarr_disk_size_total', 'Total disk size of Series in Sonarr')
FREE_DISK_SIZE = Gauge('sonarr_free_disk_size', 'Free disk size in Sonarr', ['path'])
AVAILABLE_DISK_SIZE = Gauge('sonarr_available_disk_size', 'Available disk size in Sonarr', ['path'])

QUALITY_EPISODE_COUNT = Gauge('sonarr_quality_episodes', 'Number of episodes per quality in Sonarr', ['quality', 'path'])
QUALITY_EPISODE_COUNT_T = Gauge('sonarr_quality_episodes_total', 'Number of episodes per quality in Sonarr', ['quality'])
SERIES_GENRES_COUNT = Gauge('sonarr_genres_count', 'Number of Series per Genres in Sonarr', ['genre', 'path'])
SERIES_GENRES_COUNT_T = Gauge('sonarr_genres_count_total', 'Number of Series per Genres in Sonarr', ['genre'])

MISSING_EPISODE_COUNT = Gauge('sonarr_missing_episodes', 'Number of missing episodes in Sonarr', ['path'])
MISSING_EPISODE_COUNT_T = Gauge('sonarr_missing_episodes_total', 'Number of missing episodes in Sonarr')
MONITORED_SERIES = Gauge('sonarr_monitored_series', 'Number of monitored series in Sonarr', ['path'])
MONITORED_SERIES_T = Gauge('sonarr_monitored_series_total', 'Number of monitored series in Sonarr')
UNMONITORED_SERIES = Gauge('sonarr_unmonitored_series', 'Number of unmonitored series in Sonarr', ['path'])
UNMONITORED_SERIES_T = Gauge('sonarr_unmonitored_series_total', 'Number of unmonitored series in Sonarr')

# Continuing, Upcoming, Ended, Deleted
CONTINUING_SERIES = Gauge('sonarr_continuing_series', 'Number of continuing series in Sonarr', ['path'])
CONTINUING_SERIES_T = Gauge('sonarr_continuing_series_total', 'Number of continuing series in Sonarr')
UPCOMING_SERIES = Gauge('sonarr_upcoming_series', 'Number of upcoming series in Sonarr', ['path'])
UPCOMING_SERIES_T = Gauge('sonarr_upcoming_series_total', 'Number of upcoming series in Sonarr')
ENDED_SERIES = Gauge('sonarr_ended_series', 'Number of ended series in Sonarr', ['path'])
ENDED_SERIES_T = Gauge('sonarr_ended_series_total', 'Number of ended series in Sonarr')
DELETED_SERIES = Gauge('sonarr_deleted_series', 'Number of deleted series in Sonarr', ['path'])
DELETED_SERIES_T = Gauge('sonarr_deleted_series_total', 'Number of deleted series in Sonarr')

# Metrics per Series
SERIES_EPISODE_COUNT = Gauge('sonarr_series_episodes', 'Number of episodes in a series', ['series'])
SERIES_SEASON_COUNT = Gauge('sonarr_series_seasons', 'Number of seasons in a series', ['series'])
SERIES_DOWNLOAD_PERCENTAGE = Gauge('sonarr_series_download_percentage', 'Percentage of downloaded episodes in a series', ['series'])
SERIES_MONITORED = Gauge('sonarr_series_monitored', 'Is the series monitored', ['series'])
SERIES_DISK_SIZE = Gauge('sonarr_series_disk_size', 'Disk size of a series', ['series'])
SERIES_MISSING_EPISODE_COUNT = Gauge('sonarr_series_missing_episodes', 'Number of missing episodes in a series', ['series'])
