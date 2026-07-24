"""Module to handle the Metrics of the Komga Service"""
import time

from scraparr.connectors.module import ConnectorModule
from scraparr.metrics.general import UP
import scraparr.metrics.komga as komga_metrics

SERIES_STATUSES = ("ENDED", "ONGOING", "ABANDONED", "HIATUS")
BOOK_MEDIA_STATUSES = ("UNKNOWN", "ERROR", "READY", "UNSUPPORTED", "OUTDATED")
PAGE_SIZE = 500


class Module(ConnectorModule):
    """Module Class for Komga"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "komga")

    @staticmethod
    def _wrap_list(data):
        """Wrap a plain list response into paginated format for consistency."""
        if isinstance(data, list):
            return {"content": data, "totalElements": len(data), "totalPages": 1}
        return data

    def _get_paged(self, endpoint, fetch_all=False):
        separator = "&" if "?" in endpoint else "?"
        first_page = self.get(f"{endpoint}{separator}page=0&size={PAGE_SIZE}")
        if not first_page:
            return first_page

        first_page = self._wrap_list(first_page)
        if "content" not in first_page:
            return first_page

        if not fetch_all or first_page.get("totalPages", 1) <= 1:
            return first_page

        all_content = list(first_page["content"])
        for page_num in range(1, first_page["totalPages"]):
            page = self.get(f"{endpoint}{separator}page={page_num}&size={PAGE_SIZE}")
            if page and "content" in page:
                all_content.extend(page["content"])

        first_page["content"] = all_content
        return first_page

    def scrape(self):
        initial_time = time.time()
        self.logger.debug("Scraping Komga service")

        server_info = self.get("/actuator/info")
        if not server_info:
            self.logger.error("Failed to retrieve server info")
            UP.labels(self.alias, 'komga').set(0)
            return None

        UP.labels(self.alias, 'komga').set(1)

        libraries = self._get_paged("/api/v1/libraries")
        series = self._get_paged("/api/v1/series", fetch_all=True)
        books = self._get_paged("/api/v1/books", fetch_all=False)
        collections = self._get_paged("/api/v1/collections")
        readlists = self._get_paged("/api/v1/readlists")
        users = self._get_paged("/api/v2/users")

        if not all(r and "content" in r for r in (libraries, series, books)):
            self.logger.error("Failed to retrieve core data")
            UP.labels(self.alias, 'komga').set(0)
            return None

        end_time = time.time()
        komga_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
        komga_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        return {
            "server_info": server_info,
            "libraries": libraries,
            "series": series,
            "books": books,
            "collections": collections,
            "readlists": readlists,
            "users": users,
        }

    def update_metrics(self, data):
        self._update_server_metrics(data["server_info"])
        self._update_library_metrics(data["libraries"], data["series"])
        self._update_series_metrics(data["series"], data["libraries"])
        self._update_book_metrics(data["books"])
        self._update_collection_metrics(data["collections"])
        self._update_readlist_metrics(data["readlists"])
        self._update_user_metrics(data["users"])

    def _update_server_metrics(self, server_info):
        version = server_info.get("build", {}).get("version", "unknown")
        komga_metrics.VERSION.labels(self.alias, version).set(1)

    def _update_library_metrics(self, libraries, series):
        lib_list = libraries.get("content", [])
        count = 0
        for lib in lib_list:
            lib_name = lib.get("name", "unknown")
            lib_id = lib.get("id")
            if lib_name in self.exclude or str(lib_id) in self.exclude:
                continue
            count += 1
            lib_series = [s for s in series.get("content", [])
                          if s.get("libraryId") == lib_id]
            komga_metrics.LIBRARY_SERIES_COUNT.labels(self.alias, lib_name).set(len(lib_series))

            lib_books = sum(s.get("booksCount", 0) for s in lib_series)
            komga_metrics.LIBRARY_BOOKS_COUNT.labels(self.alias, lib_name).set(lib_books)

            if self.detailed:
                self._update_library_detail(lib_name, lib_series)

        komga_metrics.LIBRARY_COUNT.labels(self.alias).set(count)

    def _update_library_detail(self, lib_name, lib_series):
        genre_counts = {}
        for s in lib_series:
            for genre in s.get("metadata", {}).get("genres", []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        for genre, cnt in genre_counts.items():
            komga_metrics.LIBRARY_GENRE_COUNT.labels(self.alias, lib_name, genre).set(cnt)

    def _update_series_metrics(self, series, libraries):
        lib_id_to_name = {
            lib["id"]: lib.get("name", "unknown") for lib in libraries.get("content", [])
        }

        series_list = series.get("content", [])
        series_list = [
            s for s in series_list
            if lib_id_to_name.get(s.get("libraryId"), "unknown") not in self.exclude
            and s.get("libraryId") not in self.exclude
        ]
        komga_metrics.SERIES_COUNT.labels(self.alias).set(len(series_list))

        status_counts = {s: 0 for s in SERIES_STATUSES}
        for s in series_list:
            status = s.get("metadata", {}).get("status", "UNKNOWN")
            if status in status_counts:
                status_counts[status] += 1
        for status, cnt in status_counts.items():
            komga_metrics.SERIES_STATUS_COUNT.labels(self.alias, status).set(cnt)

        if self.detailed:
            for s in series_list:
                series_name = s.get("name", "unknown")
                series_label = ''.join(
                    e for e in series_name.lower().replace(" ", "-") if e.isalnum() or e == "-"
                )
                lib_name = lib_id_to_name.get(s.get("libraryId"), "unknown")
                komga_metrics.SERIES_BOOKS_COUNT.labels(self.alias, lib_name, series_label).set(
                    s.get("booksCount", 0))
                komga_metrics.SERIES_BOOKS_UNREAD.labels(self.alias, lib_name, series_label).set(
                    s.get("booksUnreadCount", 0))
                komga_metrics.SERIES_BOOKS_READ.labels(self.alias, lib_name, series_label).set(
                    s.get("booksReadCount", 0))
                komga_metrics.SERIES_BOOKS_IN_PROGRESS.labels(
                    self.alias, lib_name, series_label).set(
                    s.get("booksInProgressCount", 0))

    def _update_book_metrics(self, books):
        books_list = books.get("content", [])
        komga_metrics.BOOK_COUNT.labels(self.alias).set(books.get("totalElements", len(books_list)))

        media_counts = {s: 0 for s in BOOK_MEDIA_STATUSES}
        for b in books_list:
            status = b.get("media", {}).get("status", "UNKNOWN")
            if status in media_counts:
                media_counts[status] += 1
        for status, cnt in media_counts.items():
            komga_metrics.BOOK_MEDIA_STATUS_COUNT.labels(self.alias, status).set(cnt)

    def _update_collection_metrics(self, collections):
        komga_metrics.COLLECTION_COUNT.labels(self.alias).set(
            collections.get("totalElements", len(collections.get("content", [])))
            if collections else 0
        )

    def _update_readlist_metrics(self, readlists):
        komga_metrics.READLIST_COUNT.labels(self.alias).set(
            readlists.get("totalElements", len(readlists.get("content", [])))
            if readlists else 0
        )

    def _update_user_metrics(self, users):
        komga_metrics.USER_COUNT.labels(self.alias).set(
            users.get("totalElements", len(users.get("content", [])))
            if users else 0
        )

    def clear(self):
        alias_filter = {"alias": self.alias}
        komga_metrics.VERSION.remove_by_labels(alias_filter)
        komga_metrics.LIBRARY_COUNT.remove_by_labels(alias_filter)
        komga_metrics.LIBRARY_SERIES_COUNT.remove_by_labels(alias_filter)
        komga_metrics.LIBRARY_BOOKS_COUNT.remove_by_labels(alias_filter)
        komga_metrics.SERIES_COUNT.remove_by_labels(alias_filter)
        komga_metrics.SERIES_STATUS_COUNT.remove_by_labels(alias_filter)
        komga_metrics.BOOK_COUNT.remove_by_labels(alias_filter)
        komga_metrics.BOOK_MEDIA_STATUS_COUNT.remove_by_labels(alias_filter)
        komga_metrics.COLLECTION_COUNT.remove_by_labels(alias_filter)
        komga_metrics.READLIST_COUNT.remove_by_labels(alias_filter)
        komga_metrics.USER_COUNT.remove_by_labels(alias_filter)
        komga_metrics.SERIES_BOOKS_COUNT.remove_by_labels(alias_filter)
        komga_metrics.SERIES_BOOKS_UNREAD.remove_by_labels(alias_filter)
        komga_metrics.SERIES_BOOKS_READ.remove_by_labels(alias_filter)
        komga_metrics.SERIES_BOOKS_IN_PROGRESS.remove_by_labels(alias_filter)
        komga_metrics.LIBRARY_GENRE_COUNT.remove_by_labels(alias_filter)
