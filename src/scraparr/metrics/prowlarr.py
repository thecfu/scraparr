"""Metrics for the Prowlarr Service"""

from prometheus_client import Gauge

# General Metrics
LAST_SCRAPE = Gauge("prowlarr_last_scrape", "Last time the Prowlarr Service was scraped")
SCRAPE_DURATION = Gauge("prowlarr_scrape_duration", "Duration of the last Prowlarr scrape")
START_TIME = Gauge("prowlarr_start_time", "Start time of the Prowlarr Service")
BUILD_TIME = Gauge("prowlarr_build_time", "Build time of the Prowlarr Service")

# Application Metrics
APPLICATION_COUNT = Gauge("prowlarr_application_count", "Total number of Applications")
APPLICATION_ENABLED = Gauge("prowlarr_application_enabled", "Enabled status of the Applications", ["application"])
APPLICATION_SYNC_LEVEL = Gauge("prowlarr_application_sync_level", "Sync Level of the Applications", ["application", "sync_level"])

# Indexer Metrics
INDEXER_COUNT = Gauge("prowlarr_indexer_count", "Total number of Indexers", ["type"])
INDEXER_ENABLED = Gauge("prowlarr_indexer_enabled", "Enabled status of the Indexers", ["type", "indexer"])
INDEXER_PRIVACY = Gauge("prowlarr_indexer_privacy", "Privacy status of the Indexers", ["type", "privacy"])
VIP_EXPIRATION = Gauge("prowlarr_vip_expiration", "VIP Expiration of the Indexers", ["indexer"])
INDEXER_STATUS = Gauge("prowlarr_indexer_status", "Status of the Indexers value 0 is unhealthy, 1 is healthy", ["indexer", "status"])
