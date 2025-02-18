"""Metrics for the Prowlarr Service"""

from prometheus_client import Gauge

# General Metrics
LAST_SCRAPE = Gauge("prowlarr_last_scrape", "Last time the Prowlarr Service was scraped")
SCRAPE_DURATION = Gauge("prowlarr_scrape_duration", "Duration of the last Prowlarr scrape")
START_TIME = Gauge("prowlarr_start_time", "Start time of the Prowlarr Service")
BUILD_TIME = Gauge("prowlarr_build_time", "Build time of the Prowlarr Service")

# Application Metrics
APPLICATION_COUNT = Gauge("prowlarr_applications_total", "Total number of Applications")
APPLICATION_ENABLED = Gauge("prowlarr_application_enabled", "Count of all Enabled Applications", ["application"])
APPLICATION_ENABLED_T = Gauge("prowlarr_application_enabled_total", "Enabled status of the Applications")
APPLICATION_SYNC_LEVEL = Gauge("prowlarr_application_sync_level", "Sync Level of the Applications", ["application", "sync_level"])
APPLICATION_SYNC_LEVEL_T = Gauge("prowlarr_application_sync_level_total", "Sync Level Count of all Applications", ["sync_level"])

# Indexer Metrics
INDEXER_COUNT = Gauge("prowlarr_indexer_count", "Total number of Indexers by Type", ["type"])
INDEXER_COUNT_T = Gauge("prowlarr_indexer_count_total", "Total number of Indexers")
INDEXER_ENABLED = Gauge("prowlarr_indexer_enabled", "Enabled status of the Indexers", ["type", "indexer"])
INDEXER_PRIVACY = Gauge("prowlarr_indexer_privacy", "Privacy status of the Indexers", ["type", "privacy"])
INDEXER_ENABLED_T = Gauge("prowlarr_indexer_enabled_total", "Enabled status of the Indexers")
INDEXER_PRIVACY_T = Gauge("prowlarr_indexer_privacy_total", "Privacy status of the Indexers", ["privacy"])
VIP_EXPIRATION = Gauge("prowlarr_vip_expiration", "VIP Expiration of the Indexers", ["indexer"])
INDEXER_STATUS = Gauge("prowlarr_indexer_status", "Status of the Indexers", ["indexer", "status"])
