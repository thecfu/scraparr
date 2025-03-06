"""Module to declare the overseerr Metrics"""

from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('overseerr_last_scrape', 'Last time overseerr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('overseerr_scrape_duration', 'Duration of overseerr scrape', ['alias'] )

# User Stats
USER_COUNT = Gauge('overseerr_user_total', 'Number of users in overseerr', ['alias'])
USER_REQUEST_COUNT = Gauge('overseerr_user_requests', 'Number of requests per user in overseerr', ['alias', 'user'])

# Request Stats

REQUEST_COUNT = Gauge('overseerr_request_total', 'Number of requests in overseerr', ['alias'])
REQUEST_TV = Gauge('overseerr_request_tv', 'Number of TV requests in overseerr', ['alias'])
REQUEST_MOVIE = Gauge('overseerr_request_movie', 'Number of Movie requests in overseerr', ['alias'])
REQUEST_STATUS = Gauge('overseerr_request_status', 'Status of the request in overseerr', ['alias', 'status'])
REQUEST_SEASONS_T = Gauge('overseerr_request_seasons_total', 'Total number of Requested Seasons in overseerr', ['alias'])
# Detailed
REQUEST_TIMESTAMP = Gauge('overseerr_request_timestamp', 'Timestamp of the request in overseerr', ['alias', 'request'])
REQUEST_SEASONS = Gauge('overseerr_request_seasons', 'Number of seasons in the request in overseerr', ['alias', 'request'])

# Issue Stats

ISSUE_COUNT = Gauge('overseerr_issue_total', 'Number of issues in overseerr', ['alias'])
ISSUE_STATUS = Gauge('overseerr_issue_status', 'Status of the issue in overseerr', ['alias', 'status'])
ISSUE_TYPE = Gauge('overseerr_issue_type', 'Type of the issue in overseerr', ['alias', 'type'])
ISSUE_MEDIA_TYPE = Gauge('overseerr_issue_media_type', 'Media Type of the issue in overseerr', ['alias', 'media_type'])
ISSUE_AND_MEDIA_TYPE = Gauge('overseerr_issue_and_media_type', 'Issue and Media Type of the issue in overseerr', ['alias', 'issue_type', 'media_type'])
# Detailed
ISSUE_TITLE = Gauge('overseerr_issue_title', 'Title of the issue in overseerr', ['alias', 'issue'])
ISSUE_CREATED = Gauge('overseerr_issue_created', 'Created time of the issue in overseerr', ['alias', 'issue'])
ISSUE_UPDATED = Gauge('overseerr_issue_updated', 'Update time of the issue in overseerr', ['alias', 'issue'])
