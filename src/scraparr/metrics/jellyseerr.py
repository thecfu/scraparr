"""Module to declare the jellyseerr Metrics"""

from prometheus_client import Gauge

# Scraping Stats
LAST_SCRAPE = Gauge('jellyseerr_last_scrape', 'Last time jellyseerr was scraped', ['alias'] )
SCRAPE_DURATION = Gauge('jellyseerr_scrape_duration', 'Duration of jellyseerr scrape', ['alias'] )

# User Stats
USER_COUNT = Gauge('jellyseerr_user_total', 'Number of users in jellyseerr', ['alias'])
USER_REQUEST_COUNT = Gauge('jellyseerr_user_requests', 'Number of requests per user in jellyseerr', ['alias', 'user'])

# Request Stats

REQUEST_COUNT = Gauge('jellyseerr_request_total', 'Number of requests in jellyseerr', ['alias'])
REQUEST_TV = Gauge('jellyseerr_request_tv', 'Number of TV requests in jellyseerr', ['alias'])
REQUEST_MOVIE = Gauge('jellyseerr_request_movie', 'Number of Movie requests in jellyseerr', ['alias'])
REQUEST_STATUS = Gauge('jellyseerr_request_status', 'Status of the request in jellyseerr', ['alias', 'status'])
REQUEST_SEASONS_T = Gauge('jellyseerr_request_seasons_total', 'Total number of Requested Seasons in jellyseerr', ['alias'])
# Detailed
REQUEST_TIMESTAMP = Gauge('jellyseerr_request_timestamp', 'Timestamp of the request in jellyseerr', ['alias', 'request'])
REQUEST_SEASONS = Gauge('jellyseerr_request_seasons', 'Number of seasons in the request in jellyseerr', ['alias', 'request'])

# Issue Stats

ISSUE_COUNT = Gauge('jellyseerr_issue_total', 'Number of issues in jellyseerr', ['alias'])
ISSUE_STATUS = Gauge('jellyseerr_issue_status', 'Status of the issue in jellyseerr', ['alias', 'status'])
ISSUE_TYPE = Gauge('jellyseerr_issue_type', 'Type of the issue in jellyseerr', ['alias', 'type'])
ISSUE_MEDIA_TYPE = Gauge('jellyseerr_issue_media_type', 'Media Type of the issue in jellyseerr', ['alias', 'media_type'])
ISSUE_AND_MEDIA_TYPE = Gauge('jellyseerr_issue_and_media_type', 'Issue and Media Type of the issue in jellyseerr', ['alias', 'issue_type', 'media_type'])
# Detailed
ISSUE_TITLE = Gauge('jellyseerr_issue_title', 'Title of the issue in jellyseerr', ['alias', 'issue'])
ISSUE_CREATED = Gauge('jellyseerr_issue_created', 'Created time of the issue in jellyseerr', ['alias', 'issue'])
ISSUE_UPDATED = Gauge('jellyseerr_issue_updated', 'Update time of the issue in jellyseerr', ['alias', 'issue'])
