"""Metrics for the Kavita Service"""

from prometheus_client import Gauge

# General Metrics
LAST_SCRAPE = Gauge("kavita_last_scrape", "Last time the Kavita Service was scraped", ["alias"])
SCRAPE_DURATION = Gauge("kavita_scrape_duration", "Duration of the last Kavita scrape", ["alias"])

# Version Info
VERSION = Gauge("kavita_version", "Kavita version", ["alias", "version"])
IS_DOCKER = Gauge("kavita_is_docker", "Whether Kavita is running in Docker", ["alias"])

# Server Statistics (Total)
SERIES_COUNT = Gauge("kavita_series_count", "Total number of series in Kavita", ["alias"])
VOLUME_COUNT = Gauge("kavita_volume_count", "Total number of volumes in Kavita", ["alias"])
CHAPTER_COUNT = Gauge("kavita_chapter_count", "Total number of chapters in Kavita", ["alias"])
TOTAL_FILES = Gauge("kavita_total_files", "Total number of files in Kavita", ["alias"])
TOTAL_SIZE = Gauge("kavita_total_size_bytes", "Total size of all files in Kavita in bytes", ["alias"])
TOTAL_GENRES = Gauge("kavita_total_genres", "Total number of genres in Kavita", ["alias"])
TOTAL_TAGS = Gauge("kavita_total_tags", "Total number of tags in Kavita", ["alias"])
TOTAL_PEOPLE = Gauge("kavita_total_people", "Total number of people in Kavita", ["alias"])
TOTAL_READING_TIME = Gauge("kavita_total_reading_time", "Total reading time in Kavita", ["alias"])

# Library Metrics
LIBRARY_COUNT = Gauge("kavita_library_count", "Total number of libraries in Kavita", ["alias"])
LIBRARY_SERIES_COUNT = Gauge("kavita_library_series_count", "Number of series in a library", ["alias", "library"])
LIBRARY_FOLDER_WATCHING = Gauge("kavita_library_folder_watching", "Whether folder watching is enabled for a library", ["alias", "library"])
LIBRARY_SCROBBLING = Gauge("kavita_library_scrobbling", "Whether scrobbling is enabled for a library", ["alias", "library"])
LIBRARY_TYPE = Gauge("kavita_library_type", "Type of the library", ["alias", "library", "type"])

# Detailed Library Metrics (per library aggregates)
LIBRARY_TOTAL_PAGES = Gauge("kavita_library_total_pages", "Total pages in a library", ["alias", "library"])
LIBRARY_TOTAL_WORD_COUNT = Gauge("kavita_library_total_word_count", "Total word count in a library", ["alias", "library"])
LIBRARY_AVG_READING_TIME = Gauge("kavita_library_avg_reading_time_hours", "Average reading time in hours for a library", ["alias", "library"])
LIBRARY_GENRE_COUNT = Gauge("kavita_library_genre_count", "Count of series per genre in a library", ["alias", "library", "genre"])
LIBRARY_FORMAT_COUNT = Gauge("kavita_library_format_count", "Count of series per format in a library", ["alias", "library", "format"])

# Series Metrics (detailed - per series)
SERIES_PAGES = Gauge("kavita_series_pages", "Number of pages in a series", ["alias", "library", "series"])
SERIES_WORD_COUNT = Gauge("kavita_series_word_count", "Word count in a series", ["alias", "library", "series"])
SERIES_PAGES_READ = Gauge("kavita_series_pages_read", "Number of pages read in a series", ["alias", "library", "series"])
SERIES_USER_RATING = Gauge("kavita_series_user_rating", "User rating for a series", ["alias", "library", "series"])
SERIES_AVG_HOURS_TO_READ = Gauge("kavita_series_avg_hours_to_read", "Average hours to read a series", ["alias", "library", "series"])
SERIES_MIN_HOURS_TO_READ = Gauge("kavita_series_min_hours_to_read", "Minimum hours to read a series", ["alias", "library", "series"])
SERIES_MAX_HOURS_TO_READ = Gauge("kavita_series_max_hours_to_read", "Maximum hours to read a series", ["alias", "library", "series"])
SERIES_FORMAT = Gauge("kavita_series_format", "Format of a series", ["alias", "library", "series", "format"])

# Publication Status Metrics
PUBLICATION_STATUS_COUNT = Gauge("kavita_publication_status_count", "Count of series by publication status", ["alias", "status"])

# Manga Format Metrics
MANGA_FORMAT_COUNT = Gauge("kavita_manga_format_count", "Count of series by manga format", ["alias", "format"])

# User Metrics
USER_COUNT = Gauge("kavita_user_count", "Total number of users in Kavita", ["alias"])

# File Extension Metrics
FILE_EXTENSION_COUNT = Gauge("kavita_file_extension_count", "Count of files by extension", ["alias", "extension"])
FILE_EXTENSION_SIZE = Gauge("kavita_file_extension_size_bytes", "Size of files by extension in bytes", ["alias", "extension"])
