from prometheus_client import Gauge, Enum

# Scraping Stats
LAST_SCRAPE = Gauge('jellyfin_last_scrape', 'Last time Jellyfin was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('jellyfin_scrape_duration', 'Duration of Jellyfin scrape', ['alias'] )

# Status Stats
START_TIME = Gauge('jellyfin_start_time', 'Jellyfin start time', ['alias'] )
BUILD_TIME = Gauge('jellyfin_build_time', 'Jellyfin build time', ['alias'] )