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
SERIES_COUNT = Gauge('sonarr_total_series', 'Number of series in Sonarr', ['path'])
EPISODE_COUNT = Gauge('sonarr_total_episodes', 'Number of episodes in Sonarr', ['path'])
TOTAL_DISK_SIZE = Gauge('sonarr_total_disk_size', 'Total disk size of Series in Sonarr', ['path'])
FREE_DISK_SIZE = Gauge('sonarr_free_disk_size', 'Free disk size in Sonarr', ['path'])
AVAILABLE_DISK_SIZE = Gauge('sonarr_available_disk_size', 'Available disk size in Sonarr', ['path'])
MISSING_EPISODE_COUNT = Gauge('sonarr_missing_episodes', 'Number of missing episodes in Sonarr', ['path'])

SERIES_GENRES_COUNT = Gauge('sonarr_genres_count', 'Number of Series per Genres in Sonarr', ['genre', 'path'])

MONITORED_SERIES = Gauge('sonarr_monitored_series', 'Number of monitored series in Sonarr', ['path'])
UNMONITORED_SERIES = Gauge('sonarr_unmonitored_series', 'Number of unmonitored series in Sonarr', ['path'])

# Continuing, Upcoming, Ended, Deleted
CONTINUING_SERIES = Gauge('sonarr_continuing_series', 'Number of continuing series in Sonarr', ['path'])
UPCOMING_SERIES = Gauge('sonarr_upcoming_series', 'Number of upcoming series in Sonarr', ['path'])
ENDED_SERIES = Gauge('sonarr_ended_series', 'Number of ended series in Sonarr', ['path'])
DELETED_SERIES = Gauge('sonarr_deleted_series', 'Number of deleted series in Sonarr', ['path'])

# Metrics per Series
SERIES_EPISODE_COUNT = Gauge('sonarr_series_episodes', 'Number of episodes in a series', ['series'])
SERIES_SEASON_COUNT = Gauge('sonarr_series_seasons', 'Number of seasons in a series', ['series'])
SERIES_DOWNLOAD_PERCENTAGE = Gauge('sonarr_series_download_percentage', 'Percentage of downloaded episodes in a series', ['series'])
SERIES_MONITORED = Gauge('sonarr_series_monitored', 'Is the series monitored', ['series'])
SERIES_DISK_SIZE = Gauge('sonarr_series_disk_size', 'Disk size of a series', ['series'])
SERIES_MISSING_EPISODE_COUNT = Gauge('sonarr_series_missing_episodes', 'Number of missing episodes in a series', ['series'])
