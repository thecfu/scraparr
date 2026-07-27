"""Metrics for the Komga Service"""

from prometheus_client import Gauge

# Scrape Metrics
LAST_SCRAPE = Gauge("komga_last_scrape", "Last time the Komga service was scraped", ["alias"])
SCRAPE_DURATION = Gauge("komga_scrape_duration", "Duration of the last Komga scrape in seconds", ["alias"])

# Server Info
VERSION = Gauge("komga_version", "Komga server version", ["alias", "version"])

# Library Metrics
LIBRARY_COUNT = Gauge("komga_library_count", "Total number of libraries", ["alias"])
LIBRARY_SERIES_COUNT = Gauge("komga_library_series_count", "Number of series in a library", ["alias", "library"])
LIBRARY_BOOKS_COUNT = Gauge("komga_library_books_count", "Number of books in a library", ["alias", "library"])

# Series Metrics
SERIES_COUNT = Gauge("komga_series_count", "Total number of series", ["alias"])
SERIES_STATUS_COUNT = Gauge("komga_series_status_count", "Number of series by status", ["alias", "status"])

# Book Metrics
BOOK_COUNT = Gauge("komga_book_count", "Total number of books", ["alias"])
BOOK_MEDIA_STATUS_COUNT = Gauge("komga_book_media_status_count", "Number of books by media status", ["alias", "status"])

# Collection and Readlist Metrics
COLLECTION_COUNT = Gauge("komga_collection_count", "Total number of collections", ["alias"])
READLIST_COUNT = Gauge("komga_readlist_count", "Total number of read lists", ["alias"])

# User Metrics
USER_COUNT = Gauge("komga_user_count", "Total number of users", ["alias"])

# Detailed Series Metrics (per series, behind detailed flag)
SERIES_BOOKS_COUNT = Gauge("komga_series_books_count", "Number of books in a series", ["alias", "library", "series"])
SERIES_BOOKS_UNREAD = Gauge("komga_series_books_unread", "Number of unread books in a series", ["alias", "library", "series"])
SERIES_BOOKS_READ = Gauge("komga_series_books_read", "Number of read books in a series", ["alias", "library", "series"])
SERIES_BOOKS_IN_PROGRESS = Gauge("komga_series_books_in_progress", "Number of in-progress books in a series", ["alias", "library", "series"])

# Detailed Library Metrics (behind detailed flag)
LIBRARY_GENRE_COUNT = Gauge("komga_library_genre_count", "Count of series per genre in a library", ["alias", "library", "genre"])
