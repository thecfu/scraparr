"""
Module to handle the Metrics of the Readarr Service
"""

import time
from dateutil.parser import parse

from scraparr.connectors.module import ConnectorModule
from scraparr.metrics.general import UP
import scraparr.metrics.readarr as readarr_metrics

class Module(ConnectorModule):
    """Module Class for Readarr"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "readarr")
        self.url = f"{self.url}/api/{self.api_version}"

    def clear(self):
        """Clear the metrics"""

        readarr_metrics.BOOK_DISK_SIZE.remove_by_labels({"alias": self.alias})
        readarr_metrics.BOOK_PERCENTAGE.remove_by_labels({"alias": self.alias})
        readarr_metrics.BOOK_RATING.remove_by_labels({"alias": self.alias})
        readarr_metrics.BOOK_RATING_TOTAL.remove_by_labels({"alias": self.alias})
        readarr_metrics.AUTHOR_BOOK_COUNT.remove_by_labels({"alias": self.alias})
        readarr_metrics.AUTHOR_STATUS.remove_by_labels({"alias": self.alias})
        readarr_metrics.AUTHOR_DISK_SIZE.remove_by_labels({"alias": self.alias})
        readarr_metrics.AUTHOR_RATING.remove_by_labels({"alias": self.alias})
        readarr_metrics.AUTHOR_RATING_TOTAL.remove_by_labels({"alias": self.alias})

    def get_authors(self):
        """Grab the Authors from the Readarr Endpoint"""

        initial_time = time.time()
        res = self.get("/author")
        end_time = time.time()

        if res == {}:
            UP.labels(self.api_key, 'readarr').set(0)
        else:
            UP.labels(self.api_key, 'readarr').set(1)
            readarr_metrics.LAST_SCRAPE.labels(self.api_key).set(end_time)
            readarr_metrics.SCRAPE_DURATION.labels(self.api_key).set(end_time - initial_time)
        return res

    def get_books(self):
        """Grab the Books from the Readarr Endpoint"""

        res = self.get("/book")

        if res == {}:
            UP.labels(self.api_key, "readarr").set(0)
        else:
            UP.labels(self.api_key, "readarr").set(0)
        return res

    def update_system_data(self, data):
        """Update the System Data Metrics"""
        for disk in data['root_folder']:
            (readarr_metrics.FREE_DISK_SIZE.labels(self.api_key, disk["path"])
             .set(disk["freeSpace"]))
            (readarr_metrics.AVAILABLE_DISK_SIZE.labels(self.api_key, disk["path"])
             .set(disk["totalSpace"]))

        readarr_metrics.QUEUE_COUNT.labels(self.api_key).set(data["queue"]["totalCount"])
        readarr_metrics.QUEUE_ERROR.labels(self.api_key).set(data["queue"]["errors"])
        readarr_metrics.QUEUE_WARNING.labels(self.api_key).set(data["queue"]["warnings"])

        start_time = parse(data["status"]["startTime"]).timestamp()
        build_time = parse(data["status"]["buildTime"]).timestamp()
        readarr_metrics.START_TIME.labels(self.api_key).set(start_time)
        readarr_metrics.BUILD_TIME.labels(self.api_key).set(build_time)

    def analyse_authors(self, authors):
        """Analyse the Authors from the Readarr Endpoint"""

        authors_status = {}
        author_rating = []

        for author in authors:
            status = author.get("status", "Unknown")
            authors_status[status] = author.get(status, 0) + 1

            if author.get("ratings") and author["ratings"].get("value") is not None:
                author_rating.append(author["ratings"]["value"])

            if self.detailed:
                if author.get("statistics", None) is not None:
                    (readarr_metrics.AUTHOR_DISK_SIZE
                     .labels(self.api_key, author["sortName"])
                     .set(author["statistics"]["sizeOnDisk"])
                     )
                    (readarr_metrics.AUTHOR_BOOK_COUNT
                     .labels(self.api_key, author["sortName"])
                     .set(author["statistics"]["bookCount"])
                    )
                    (readarr_metrics.AUTHOR_RATING
                     .labels(self.api_key, author["sortName"])
                     .set(author["ratings"]["value"])
                     )

        for status, count in authors_status.items():
            readarr_metrics.AUTHOR_STATUS.labels(self.api_key, status).set(count)
        overall_rating = sum(author_rating) / len(author_rating)
        readarr_metrics.AUTHOR_RATING_TOTAL.labels(self.api_key).set(overall_rating)


    def analyse_books(self, books):
        """Analyse the Books from the Readarr Endpoint"""

        book_genres = {}
        book_disk_size = []
        book_rating = []

        for book in books:

            for genre in book["genres"]:
                book_genres[genre] = book_genres.get(genre, 0) + 1

            if book.get("statistics") and book["statistics"].get("sizeOnDisk") is not None:
                book_disk_size.append(book["statistics"]["sizeOnDisk"])

            if book.get("ratings") and book["ratings"].get("value") is not None:
                book_rating.append(book["ratings"]["value"])

            if self.detailed:
                if book.get("statistics", None) is not None:
                    (readarr_metrics.BOOK_DISK_SIZE
                     .labels(self.api_key, book["title"])
                      .set(book["statistics"]["sizeOnDisk"])
                    )
                    (readarr_metrics.BOOK_PERCENTAGE
                     .labels(self.api_key, book["title"])
                     .set(book["statistics"]["percentOfBooks"])
                    )
                    (readarr_metrics.BOOK_RATING
                     .labels(self.api_key, book["title"])
                      .set(book["ratings"]["value"])
                    )

        overall_rating = sum(book_rating) / len(book_rating)
        readarr_metrics.BOOK_RATING_TOTAL.labels(self.api_key).set(overall_rating)
        readarr_metrics.BOOK_DISK_SIZE_TOTAL.labels(self.api_key).set(sum(book_disk_size))
        for genre, genre_count in book_genres.items():
            readarr_metrics.BOOK_GENRES.labels(self.api_key, genre).set(genre_count)

    def scrape(self):
        """Scrape the Readarr Service"""

        scrape_data = {
            "system": {
                "root_folder": self.get_root_folder(),
                "queue": self.get("/queue/status"),
                "status": self.get("/system/status")
            },
            "data": {
                "books": self.get_books(),
                "authors": self.get_authors()
            }
        }

        if scrape_data["data"]["books"] == {} or scrape_data["system"]["status"] == {}:
            return {}

        return scrape_data

    def update_metrics(self, data):
        """Update the Metrics for the Readarr Service"""

        self.analyse_authors(data["data"]["authors"])
        self.analyse_books(data["data"]["books"])
        self.update_system_data(data["system"])
