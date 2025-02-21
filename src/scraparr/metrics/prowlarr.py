"""Metrics for the Prowlarr Service"""

from prometheus_client import Gauge

# General Metrics
LAST_SCRAPE = Gauge("prowlarr_last_scrape", "Last time the Prowlarr Service was scraped", ["alias"])
SCRAPE_DURATION = Gauge("prowlarr_scrape_duration", "Duration of the last Prowlarr scrape", ["alias"])
START_TIME = Gauge("prowlarr_start_time", "Start time of the Prowlarr Service", ["alias"])
BUILD_TIME = Gauge("prowlarr_build_time", "Build time of the Prowlarr Service", ["alias"])

# Application Metrics
APPLICATION_COUNT = Gauge("prowlarr_applications_total", "Total number of Applications", ["alias"])
APPLICATION_ENABLED = Gauge("prowlarr_application_enabled", "Count of all Enabled Applications", ["alias", "application"])
APPLICATION_ENABLED_T = Gauge("prowlarr_application_enabled_total", "Enabled status of the Applications", ["alias"])
APPLICATION_SYNC_LEVEL = Gauge("prowlarr_application_sync_level", "Sync Level of the Applications", ["alias", "application", "sync_level"])
APPLICATION_SYNC_LEVEL_T = Gauge("prowlarr_application_sync_level_total", "Sync Level Count of all Applications", ["alias", "sync_level"])

# Indexer Metrics
INDEXER_COUNT = Gauge("prowlarr_indexer_count", "Total number of Indexers by Type", ["alias", "type"])
INDEXER_COUNT_T = Gauge("prowlarr_indexer_count_total", "Total number of Indexers", ["alias"])
INDEXER_ENABLED = Gauge("prowlarr_indexer_enabled", "Enabled status of the Indexers", ["alias", "type", "indexer"])
INDEXER_PRIVACY = Gauge("prowlarr_indexer_privacy", "Privacy status of the Indexers", ["alias", "type", "privacy"])
INDEXER_ENABLED_T = Gauge("prowlarr_indexer_enabled_total", "Enabled status of the Indexers", ["alias"])
INDEXER_PRIVACY_T = Gauge("prowlarr_indexer_privacy_total", "Privacy status of the Indexers", ["alias", "privacy"])
VIP_EXPIRATION = Gauge("prowlarr_vip_expiration", "VIP Expiration of the Indexers", ["alias", "indexer"])
INDEXER_STATUS = Gauge("prowlarr_indexer_status", "Status of the Indexers value 0 is unhealthy, 1 is healthy", ["alias", "indexer", "status"])
