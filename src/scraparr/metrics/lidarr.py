from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('lidarr_last_scrape', 'Last time Lidarr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('lidarr_scrape_duration', 'Duration of Lidarr scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('lidarr_start_time', 'Lidarr start time', ['alias'] )
BUILD_TIME = Gauge('lidarr_build_time', 'Lidarr build time', ['alias'] )

# Queue Stats
QUEUE_COUNT = Gauge('lidarr_queue_count', 'Number of items in Lidarr queue', ['alias'] )
QUEUE_ERROR = Gauge('lidarr_queue_error', 'Item in Lidarr queue with error', ['alias'] )
QUEUE_WARNING = Gauge('lidarr_queue_warning', 'Item in Lidarr queue with warning', ['alias'] )

# Metrics for Total Count
ARTIST_COUNT = Gauge('lidarr_artists', 'Number of artists in Lidarr', ['alias', 'path'])
ARTIST_COUNT_T = Gauge('lidarr_artists_total', 'Number of artists in Lidarr', ['alias'] )
RELEASE_COUNT = Gauge('lidarr_releases', 'Number of releases in Lidarr', ['alias', 'path'])
RELEASE_COUNT_T = Gauge('lidarr_releases_total', 'Number of releases in Lidarr', ['alias'] )
TRACK_COUNT = Gauge('lidarr_tracks', 'Number of tracks in Lidarr', ['alias', 'path'])
TRACK_COUNT_T = Gauge('lidarr_tracks_total', 'Number of tracks in Lidarr', ['alias'] )
TOTAL_DISK_SIZE = Gauge('lidarr_disk_size', 'Total disk size of artists in Lidarr', ['alias', 'path'])
TOTAL_DISK_SIZE_T = Gauge('lidarr_disk_size_total', 'Total disk size of artists in Lidarr', ['alias'] )
FREE_DISK_SIZE = Gauge('lidarr_free_disk_size', 'Free disk size in Lidarr', ['alias', 'path'])
AVAILABLE_DISK_SIZE = Gauge('lidarr_available_disk_size', 'Available disk size in Lidarr', ['alias', 'path'])

MONITORED_ARTIST = Gauge('lidarr_monitored_artists', 'Number of monitored artists in Lidarr', ['alias', 'path'])
MONITORED_ARTIST_T = Gauge('lidarr_monitored_artists_total', 'Number of monitored artists in Lidarr', ['alias'] )
UNMONITORED_ARTIST = Gauge('lidarr_unmonitored_artists', 'Number of unmonitored artists in Lidarr', ['alias', 'path'])
UNMONITORED_ARTIST_T = Gauge('lidarr_unmonitored_artists_total', 'Number of unmonitored artists in Lidarr', ['alias'] )

QUALITY_TRACK_COUNT = Gauge('lidarr_quality_tracks', 'Number of tracks per quality in Lidarr', ['alias', 'quality', 'path'])
QUALITY_TRACK_COUNT_T = Gauge('lidarr_quality_tracks_total', 'Number of tracks per quality in Lidarr', ['alias', 'quality'])
RELEASE_TYPE_COUNT = Gauge('lidarr_release_type_count', 'Number of releases per type in Lidarr', ['alias', 'type', 'path'])
RELEASE_TYPE_COUNT_T = Gauge('lidarr_release_type_count_total', 'Number of releases per type in Lidarr', ['alias', 'type'])

MISSING_RELEASE_COUNT = Gauge('lidarr_missing_releases', 'Number of missing releases in Lidarr', ['alias', 'path'])
MISSING_RELEASE_COUNT_T = Gauge('lidarr_missing_releases_total', 'Number of missing releases in Lidarr', ['alias'] )
MONITORED_RELEASE = Gauge('lidarr_monitored_releases', 'Number of monitored releases in Lidarr', ['alias', 'path'])
MONITORED_RELEASE_T = Gauge('lidarr_monitored_releases_total', 'Number of monitored releases in Lidarr', ['alias'] )
UNMONITORED_RELEASE = Gauge('lidarr_unmonitored_releases', 'Number of unmonitored releases in Lidarr', ['alias', 'path'])
UNMONITORED_RELEASE_T = Gauge('lidarr_unmonitored_releases_total', 'Number of unmonitored releases in Lidarr', ['alias'] )

# Continuing, Inactive
CONTINUING_ARTIST = Gauge('lidarr_continuing_artists', 'Number of continuing artists in Lidarr', ['alias', 'path'])
CONTINUING_ARTIST_T = Gauge('lidarr_continuing_artists_total', 'Number of continuing artists in Lidarr', ['alias'] )
ENDED_ARTIST = Gauge('lidarr_inactive_artists', 'Number of ended artists in Lidarr', ['alias', 'path'])
ENDED_ARTIST_T = Gauge('lidarr_inactive_artists_total', 'Number of ended artists in Lidarr', ['alias'] )

# Metrics per Artist
ARTIST_TRACK_COUNT = Gauge('lidarr_artist_tracks', 'Number of tracks for an artist', ['alias', 'artist'])
ARTIST_RELEASE_COUNT = Gauge('lidarr_artist_releases', 'Number of releases for an artist', ['alias', 'artist'])
ARTIST_MONITORED = Gauge('lidarr_artist_monitored', 'Is the artist monitored', ['alias', 'artist'])
ARTIST_DISK_SIZE = Gauge('lidarr_artist_disk_size', 'Disk size of an artist', ['alias', 'artist'])
ARTIST_MISSING_RELEASE_COUNT = Gauge('lidarr_artist_missing_releases', 'Number of missing releases for an artist', ['alias', 'artist'])
