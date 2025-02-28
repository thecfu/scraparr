"""Metrics for the Readarr Service"""

from prometheus_client import Gauge

# General Metrics
LAST_SCRAPE = Gauge("readarr_last_scrape", "Last time the Readarr Service was scraped", ["alias"])
SCRAPE_DURATION = Gauge("readarr_scrape_duration", "Duration of the last Readarr scrape", ["alias"])
START_TIME = Gauge("readarr_start_time", "Start time of the Readarr Service", ["alias"])
BUILD_TIME = Gauge("readarr_build_time", "Build time of the Readarr Service", ["alias"])

FREE_DISK_SIZE = Gauge("readarr_free_disk_size", "Free Disk Size of the Readarr Service", ["alias", "path"])
AVAILABLE_DISK_SIZE = Gauge("readarr_available_disk_size", "Available Disk Size of the Readarr Service", ["alias", "path"])

QUEUE_COUNT = Gauge("readarr_queue_count", "Number of items in the Readarr Queue", ["alias"])
QUEUE_ERROR = Gauge("readarr_queue_error", "Number of errors in the Readarr Queue", ["alias"])
QUEUE_WARNING = Gauge("readarr_queue_warning", "Number of warnings in the Readarr Queue", ["alias"])

AUTHOR_STATUS = Gauge("readarr_author_status", "Status of the Authors in Readarr", ["alias", "status"])
AUTHOR_DISK_SIZE = Gauge("readarr_author_disk_size", "Disk Size of the Authors in Readarr", ["alias", "author"])
AUTHOR_BOOK_COUNT = Gauge("readarr_author_book_count", "Book Count of the Authors in Readarr", ["alias", "author"])
AUTHOR_RATING = Gauge("readarr_author_rating", "Rating of the Authors in Readarr", ["alias", "author"])
AUTHOR_RATING_TOTAL = Gauge("readarr_author_rating_total", "Overall Rating of the Authors in Readarr", ["alias"])

BOOK_GENRES = Gauge("readarr_book_genres", "Genres of the Books in Readarr", ["alias", "genre"])
BOOK_DISK_SIZE = Gauge("readarr_book_disk_size", "Disk Size of the Books in Readarr", ["alias", "book"])
BOOK_DISK_SIZE_TOTAL = Gauge("readarr_book_disk_size_total", "Disk Size of the Books in Readarr", ["alias", "book"])
BOOK_RATING = Gauge("readarr_book_rating", "Rating of the Books in Readarr", ["alias", "book"])
BOOK_RATING_TOTAL = Gauge("readarr_book_rating_total", "Overall Rating of the Books in Readarr", ["alias"])
