"""Metrics for the SABnzbd Service"""
from prometheus_client import Gauge

LAST_SCRAPE     = Gauge('sabnzbd_last_scrape',     'Last time SABnzbd was scraped',          ['alias'])
SCRAPE_DURATION = Gauge('sabnzbd_scrape_duration', 'Duration of SABnzbd scrape in seconds',  ['alias'])

QUEUE_SPEED     = Gauge('sabnzbd_queue_speed_bytes',     'Current download speed in bytes/s',         ['alias'])
QUEUE_SIZE      = Gauge('sabnzbd_queue_size_bytes',      'Total size of queued items in bytes',       ['alias'])
QUEUE_REMAINING = Gauge('sabnzbd_queue_remaining_bytes', 'Remaining download size in bytes',          ['alias'])
QUEUE_SLOTS     = Gauge('sabnzbd_queue_slots',           'Number of items in the queue',              ['alias'])
QUEUE_PAUSED    = Gauge('sabnzbd_queue_paused',          '1 if the queue is paused, 0 otherwise',    ['alias'])
DISK_SPACE      = Gauge('sabnzbd_disk_space_bytes',      'Free disk space on download dir in bytes',  ['alias'])
DISK_SPACE_TOTAL= Gauge('sabnzbd_disk_space_total_bytes','Total disk space on download dir in bytes', ['alias'])

HISTORY_TOTAL   = Gauge('sabnzbd_history_total_bytes', 'All-time downloaded bytes',       ['alias'])
HISTORY_DAY     = Gauge('sabnzbd_history_day_bytes',   'Downloaded bytes today',          ['alias'])
HISTORY_WEEK    = Gauge('sabnzbd_history_week_bytes',  'Downloaded bytes this week',      ['alias'])
HISTORY_MONTH   = Gauge('sabnzbd_history_month_bytes', 'Downloaded bytes this month',     ['alias'])
HISTORY_FAILED  = Gauge('sabnzbd_history_failed_jobs', 'Number of failed download jobs',  ['alias'])

SERVER_TOTAL    = Gauge('sabnzbd_server_total_bytes',      'All-time downloaded bytes per server',    ['alias', 'server'])
SERVER_DAY      = Gauge('sabnzbd_server_day_bytes',        'Downloaded bytes today per server',       ['alias', 'server'])
SERVER_WEEK     = Gauge('sabnzbd_server_week_bytes',       'Downloaded bytes this week per server',   ['alias', 'server'])
SERVER_MONTH    = Gauge('sabnzbd_server_month_bytes',      'Downloaded bytes this month per server',  ['alias', 'server'])
SERVER_TRIED    = Gauge('sabnzbd_server_articles_tried',   'Articles tried per server',               ['alias', 'server'])
SERVER_SUCCESS  = Gauge('sabnzbd_server_articles_success', 'Articles successfully retrieved',         ['alias', 'server'])
