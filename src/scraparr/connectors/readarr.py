"""
Module to handle the Metrics of the Readarr Service
"""

import time
import logging
from dateutil.parser import parse

from scraparr.connectors import util
from scraparr.metrics.general import UP
import scraparr.metrics.readarr as readarr_metrics

def get_authors(url, api_key, version, alias):
    """Grab the Authors from the Readarr Endpoint"""

    initial_time = time.time()
    res = util.get(f"{url}/api/{version}/author", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels(alias, 'readarr').set(0)
    else:
        UP.labels(alias, 'readarr').set(1)
        readarr_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        readarr_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
    return res

def get_books(url, api_key, version, alias):
    """Grab the Books from the Readarr Endpoint"""

    res = util.get(f"{url}/api/{version}/book", api_key)

    if res == {}:
        UP.labels(alias, "readarr").set(0)
    else:
        UP.labels(alias, "readarr").set(0)
    return res

def update_system_data(data, alias):
    """Update the System Data Metrics"""
    for disk in data['root_folder']:
        readarr_metrics.FREE_DISK_SIZE.labels(alias, disk["path"]).set(disk["freeSpace"])
        readarr_metrics.AVAILABLE_DISK_SIZE.labels(alias, disk["path"]).set(disk["totalSpace"])

    readarr_metrics.QUEUE_COUNT.labels(alias).set(data["queue"]["totalCount"])
    readarr_metrics.QUEUE_ERROR.labels(alias).set(data["queue"]["errors"])
    readarr_metrics.QUEUE_WARNING.labels(alias).set(data["queue"]["warnings"])

    start_time = parse(data["status"]["startTime"]).timestamp()
    build_time = parse(data["status"]["buildTime"]).timestamp()
    readarr_metrics.START_TIME.labels(alias).set(start_time)
    readarr_metrics.BUILD_TIME.labels(alias).set(build_time)

def analyse_authors(authors, detailed, alias):
    """Analyse the Authors from the Readarr Endpoint"""

    authors_status = {}
    author_rating = []

    readarr_metrics.AUTHOR_BOOK_COUNT.clear()
    readarr_metrics.AUTHOR_STATUS.clear()
    readarr_metrics.AUTHOR_DISK_SIZE.clear()
    readarr_metrics.AUTHOR_RATING.clear()
    readarr_metrics.AUTHOR_RATING_TOTAL.clear()

    for author in authors:
        status = author.get("status", "Unknown")
        authors_status[status] = author.get(status, 0) + 1

        if author.get("ratings") and author["ratings"].get("value") is not None:
            author_rating.append(author["ratings"]["value"])

        if detailed:
            if author.get("statistics", None) is not None:
                (readarr_metrics.AUTHOR_DISK_SIZE
                 .labels(alias, author["sortName"])
                 .set(author["statistics"]["sizeOnDisk"])
                 )
                (readarr_metrics.AUTHOR_BOOK_COUNT
                 .labels(alias, author["sortName"])
                 .set(author["statistics"]["bookCount"])
                )
                (readarr_metrics.AUTHOR_RATING
                 .labels(alias, author["sortName"])
                 .set(author["ratings"]["value"])
                 )

    for status, count in authors_status.items():
        readarr_metrics.AUTHOR_STATUS.labels(alias, status).set(count)
    overall_rating = sum(author_rating) / len(author_rating)
    readarr_metrics.AUTHOR_RATING_TOTAL.labels(alias).set(overall_rating)


def analyse_books(books, detailed, alias):
    """Analyse the Books from the Readarr Endpoint"""

    book_genres = {}
    book_disk_size = []
    book_rating = []

    readarr_metrics.BOOK_DISK_SIZE.clear()
    readarr_metrics.BOOK_PERCENTAGE.clear()
    readarr_metrics.BOOK_RATING.clear()
    readarr_metrics.BOOK_RATING_TOTAL.clear()

    for book in books:

        for genre in book["genres"]:
            book_genres[genre] = book_genres.get(genre, 0) + 1

        if book.get("statistics") and book["statistics"].get("sizeOnDisk") is not None:
            book_disk_size.append(book["statistics"]["sizeOnDisk"])

        if book.get("ratings") and book["ratings"].get("value") is not None:
            book_rating.append(book["ratings"]["value"])

        if detailed:
            if book.get("statistics", None) is not None:
                (readarr_metrics.BOOK_DISK_SIZE
                 .labels(alias, book["title"])
                  .set(book["statistics"]["sizeOnDisk"])
                )
                (readarr_metrics.BOOK_PERCENTAGE
                 .labels(alias, book["title"])
                 .set(book["statistics"]["percentOfBooks"])
                )
                (readarr_metrics.BOOK_RATING
                 .labels(alias, book["title"])
                  .set(book["ratings"]["value"])
                )

    overall_rating = sum(book_rating) / len(book_rating)
    readarr_metrics.BOOK_RATING_TOTAL.labels(alias).set(overall_rating)
    readarr_metrics.BOOK_DISK_SIZE_TOTAL.labels(alias).set(sum(book_disk_size))
    for genre, genre_count in book_genres.items():
        readarr_metrics.BOOK_GENRES.labels(alias, genre).set(genre_count)

def scrape(config):
    """Scrape the Sonarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    api_version = config.get('api_version')
    alias = config.get('alias', 'sonarr')

    scrape_data = {
        "system": {
            "root_folder": util.get_root_folder(url, api_version, api_key),
            "queue": util.get(f"{url}/api/{api_version}/queue/status", api_key),
            "status": util.get(f"{url}/api/{api_version}/system/status", api_key)
        },
        "data": {
            "books": get_books(url, api_key, api_version, alias),
            "authors": get_authors(url, api_key, api_version, alias)
        }
    }

    if scrape_data["data"]["books"] == {} or scrape_data["system"]["status"] == {}:
        logging.error("No Data found for Sonarr, assuming Failure")
        return {}

    return scrape_data

def update_metrics(series, detailed, alias):
    """Update the Metrics for the Sonarr Service"""

    analyse_authors(series["data"]["authors"], detailed, alias)
    analyse_books(series["data"]["books"], detailed, alias)
    update_system_data(series["system"], alias)
