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
SERIES_COUNT = Gauge('whisparr_sites', 'Number of sites in Whisparr', ['alias', 'path'])
SERIES_COUNT_T = Gauge('whisparr_sites_total', 'Number of sites in Whisparr', ['alias'] )
EPISODE_COUNT = Gauge('whisparr_scenes', 'Number of scenes in Whisparr', ['alias', 'path'])
EPISODE_COUNT_T = Gauge('whisparr_scenes_total', 'Number of scenes in Whisparr', ['alias'] )
TOTAL_DISK_SIZE = Gauge('whisparr_disk_size', 'Total disk size of Sites in Whisparr', ['alias', 'path'])
TOTAL_DISK_SIZE_T = Gauge('whisparr_disk_size_total', 'Total disk size of Sites in Whisparr', ['alias'] )
FREE_DISK_SIZE = Gauge('whisparr_free_disk_size', 'Free disk size in Whisparr', ['alias', 'path'])
AVAILABLE_DISK_SIZE = Gauge('whisparr_available_disk_size', 'Available disk size in Whisparr', ['alias', 'path'])

QUALITY_EPISODE_COUNT = Gauge('whisparr_quality_scenes', 'Number of scenes per quality in Whisparr', ['alias', 'quality', 'path'])
QUALITY_EPISODE_COUNT_T = Gauge('whisparr_quality_scenes_total', 'Number of scenes per quality in Whisparr', ['alias', 'quality'])
SERIES_GENRES_COUNT = Gauge('whisparr_genres_count', 'Number of Sites per Genres in Whisparr', ['alias', 'genre', 'path'])
SERIES_GENRES_COUNT_T = Gauge('whisparr_genres_count_total', 'Number of Sites per Genres in Whisparr', ['alias', 'genre'])

MISSING_EPISODE_COUNT = Gauge('whisparr_missing_scenes', 'Number of missing scenes in Whisparr', ['alias', 'path'])
MISSING_EPISODE_COUNT_T = Gauge('whisparr_missing_scenes_total', 'Number of missing scenes in Whisparr', ['alias'] )
MONITORED_SERIES = Gauge('whisparr_monitored_sites', 'Number of monitored sites in Whisparr', ['alias', 'path'])
MONITORED_SERIES_T = Gauge('whisparr_monitored_sites_total', 'Number of monitored sites in Whisparr', ['alias'] )
UNMONITORED_SERIES = Gauge('whisparr_unmonitored_sites', 'Number of unmonitored sites in Whisparr', ['alias', 'path'])
UNMONITORED_SERIES_T = Gauge('whisparr_unmonitored_sites_total', 'Number of unmonitored sites in Whisparr', ['alias'] )

# Continuing, Upcoming, Ended, Deleted
CONTINUING_SERIES = Gauge('whisparr_continuing_sites', 'Number of continuing sites in Whisparr', ['alias', 'path'])
CONTINUING_SERIES_T = Gauge('whisparr_continuing_sites_total', 'Number of continuing sites in Whisparr', ['alias'] )
UPCOMING_SERIES = Gauge('whisparr_upcoming_sites', 'Number of upcoming sites in Whisparr', ['alias', 'path'])
UPCOMING_SERIES_T = Gauge('whisparr_upcoming_sites_total', 'Number of upcoming sites in Whisparr', ['alias'] )
ENDED_SERIES = Gauge('whisparr_ended_sites', 'Number of ended sites in Whisparr', ['alias', 'path'])
ENDED_SERIES_T = Gauge('whisparr_ended_sites_total', 'Number of ended sites in Whisparr', ['alias'] )
DELETED_SERIES = Gauge('whisparr_deleted_sites', 'Number of deleted sites in Whisparr', ['alias', 'path'])
DELETED_SERIES_T = Gauge('whisparr_deleted_sites_total', 'Number of deleted sites in Whisparr', ['alias'] )

# Metrics per Sites
SERIES_EPISODE_COUNT = Gauge('whisparr_sites_scenes', 'Number of scenes in a sites', ['alias', 'sites'])
SERIES_SEASON_COUNT = Gauge('whisparr_sites_seasons', 'Number of seasons in a sites', ['alias', 'sites'])
SERIES_DOWNLOAD_PERCENTAGE = Gauge('whisparr_sites_download_percentage', 'Percentage of downloaded scenes in a sites', ['alias', 'sites'])
SERIES_MONITORED = Gauge('whisparr_sites_monitored', 'Is the sites monitored', ['alias', 'sites'])
SERIES_DISK_SIZE = Gauge('whisparr_sites_disk_size', 'Disk size of a sites', ['alias', 'sites'])
SERIES_MISSING_EPISODE_COUNT = Gauge('whisparr_sites_missing_scenes', 'Number of missing scenes in a sites', ['alias', 'sites'])
