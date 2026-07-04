"""Module to declare the seerr Metrics"""

from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('seerr_last_scrape', 'Last time seerr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('seerr_scrape_duration', 'Duration of seerr scrape', ['alias'] )

# User Stats
USER_COUNT = Gauge('seerr_user_total', 'Number of users in seerr', ['alias'])
USER_REQUEST_COUNT = Gauge('seerr_user_requests', 'Number of requests per user in seerr', ['alias', 'user'])

# Request Stats

REQUEST_COUNT = Gauge('seerr_request_total', 'Number of requests in seerr', ['alias'])
REQUEST_TV = Gauge('seerr_request_tv', 'Number of TV requests in seerr', ['alias'])
REQUEST_MOVIE = Gauge('seerr_request_movie', 'Number of Movie requests in seerr', ['alias'])
REQUEST_STATUS = Gauge('seerr_request_status', 'Status of the request in seerr', ['alias', 'status'])
REQUEST_SEASONS_T = Gauge('seerr_request_seasons_total', 'Total number of Requested Seasons in seerr', ['alias'])
# Detailed
REQUEST_TIMESTAMP = Gauge('seerr_request_timestamp', 'Timestamp of the request in seerr', ['alias', 'request'])
REQUEST_SEASONS = Gauge('seerr_request_seasons', 'Number of seasons in the request in seerr', ['alias', 'request'])

# Issue Stats

ISSUE_COUNT = Gauge('seerr_issue_total', 'Number of issues in seerr', ['alias'])
ISSUE_STATUS = Gauge('seerr_issue_status', 'Status of the issue in seerr', ['alias', 'status'])
ISSUE_TYPE = Gauge('seerr_issue_type', 'Type of the issue in seerr', ['alias', 'type'])
ISSUE_MEDIA_TYPE = Gauge('seerr_issue_media_type', 'Media Type of the issue in seerr', ['alias', 'media_type'])
ISSUE_AND_MEDIA_TYPE = Gauge('seerr_issue_and_media_type', 'Issue and Media Type of the issue in seerr', ['alias', 'issue_type', 'media_type'])
# Detailed
ISSUE_TITLE = Gauge('seerr_issue_title', 'Title of the issue in seerr', ['alias', 'issue'])
ISSUE_CREATED = Gauge('seerr_issue_created', 'Created time of the issue in seerr', ['alias', 'issue'])
ISSUE_UPDATED = Gauge('seerr_issue_updated', 'Update time of the issue in seerr', ['alias', 'issue'])
