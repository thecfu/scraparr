"""
Module to handle the Metrics of the Kavita Service
"""
import base64
import json
import time
import concurrent.futures
from datetime import datetime

from binascii import Error as BinasciiError
from requests.exceptions import RequestException

from scraparr.connectors.module import ConnectorModule, _get_session
from scraparr.metrics.general import UP
import scraparr.metrics.kavita as kavita_metrics

# Maximum number of parallel requests for series metadata
MAX_METADATA_WORKERS = 5

# Library Type mappings from Kavita API
LIBRARY_TYPES = {
    0: "Manga",
    1: "Comic",
    2: "Book",
    3: "Images",
    4: "LightNovel",
    5: "ComicVine"
}

# Publication Status mappings from Kavita API
PUBLICATION_STATUS = {
    0: "Ongoing",
    1: "Hiatus",
    2: "Completed",
    3: "Cancelled",
    4: "Ended"
}

# Manga Format mappings from Kavita API
MANGA_FORMAT = {
    0: "Image",
    1: "Archive",
    2: "Unknown",
    3: "Epub",
    4: "Pdf"
}


def get_expiration(jwt):
    """Get Expiration Time from JWT Token"""
    try:
        payload_part = jwt.split('.')[1]
        # Add padding if necessary
        padding = 4 - len(payload_part) % 4
        if padding != 4:
            payload_part += '=' * padding
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes)
        return payload.get('exp')
    except (IndexError, ValueError, json.JSONDecodeError, BinasciiError):
        return None


class Module(ConnectorModule):  # pylint: disable=too-many-instance-attributes
    """Module Class for Kavita"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "kavita")
        # Use legacy JWT authentication if legacy_auth=true, otherwise use x-api-key header
        self.legacy_auth = config.get('legacy_auth', False)
        self.api_key_expires_at = None
        # JWT authentication fields (only used when legacy_auth=true)
        self.jwt = None
        self.refresh_token = None
        self.expires_at = None

    def _get_auth_header(self):
        """Get the authorization header for API requests"""
        # Use JWT authentication if legacy_auth is enabled
        if self.legacy_auth:
            if self.expires_at is None or time.time() >= self.expires_at - 60:
                if not self._generate_jwt():
                    return None
            return {"Authorization": f"Bearer {self.jwt}"}

        # Default: use x-api-key header (Auth Key method)
        return {"x-api-key": self.api_key}

    def _check_api_key_expiration(self):
        """Check if the API key has an expiration date. Null implies no expiration."""
        if self.legacy_auth:
            return None

        try:
            session = _get_session()
            api_url = f"{self.url}/api/plugin/authkey-expires"
            res = session.get(
                api_url, headers={"x-api-key": self.api_key}, timeout=20
            )
            if res.status_code == 200:
                expiration = res.json()
                if expiration:
                    expiration = expiration.get("expiresAt")
                    if not expiration:
                        raise RequestException("API key expiration endpoint missing 'expiresAt' field")
                    self.api_key_expires_at = expiration  # None if no expiration
                    self.logger.debug("API key expires at: %s", expiration)
                    # Parse ISO datetime and convert to unix timestamp
                    try:
                        exp_dt = datetime.fromisoformat(
                            expiration.replace("Z", "+00:00"))
                        kavita_metrics.API_KEY_EXPIRATION.labels(
                            self.alias).set(exp_dt.timestamp())
                    except (ValueError, TypeError):
                        kavita_metrics.API_KEY_EXPIRATION.labels(self.alias).set(0)
                else:
                    self.api_key_expires_at = None
                    self.logger.debug("API key has no expiration")
                    kavita_metrics.API_KEY_EXPIRATION.labels(self.alias).set(0)
                return expiration
            self.logger.warning(
                "Failed to check API key expiration: %s", res.status_code
            )
        except (RequestException, ValueError) as e:
            self.api_key_expires_at = None
            self.logger.debug("Error checking API key expiration: %s", e)
        return None

    def _generate_jwt(self):
        """Generate JWT Token for Kavita API Authentication (legacy fallback method)"""
        try:
            session = _get_session()
            auth_url = (f"{self.url}/api/Plugin/authenticate"
                        f"?apiKey={self.api_key}&pluginName=scraparr")
            jwt_request = session.post(auth_url, timeout=20)
            jwt_request.raise_for_status()
            jwt_json = jwt_request.json()
            self.jwt = jwt_json["token"]
            self.refresh_token = jwt_json["refreshToken"]
            self.expires_at = get_expiration(self.jwt)
            return True
        except (RequestException, KeyError, ValueError) as e:
            self.logger.error("Error generating JWT token: %s", e)
            return False

    def _api_get(self, endpoint):
        """Make an authenticated GET request to the Kavita API"""
        headers = self._get_auth_header()
        if headers is None:
            return None

        if endpoint.startswith("/"):
            api_url = f"{self.url}{endpoint}"
        else:
            api_url = f"{self.url}/{endpoint}"

        try:
            session = _get_session()
            res = session.get(api_url, headers=headers, timeout=20)
            if res.status_code == 200:
                return res.json()
            self.logger.debug(
                "Request for %s returned status code: %s", api_url, res.status_code
            )
        except (RequestException, ValueError) as e:
            self.logger.debug("Request for %s failed with: %s", api_url, e)
        return None

    def clear(self):
        """Clear Kavita metrics to remove any previous data."""
        alias_filter = {"alias": self.alias}
        kavita_metrics.LIBRARY_SERIES_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_FOLDER_WATCHING.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_SCROBBLING.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_TYPE.remove_by_labels(alias_filter)
        kavita_metrics.PUBLICATION_STATUS_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.MANGA_FORMAT_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.FILE_EXTENSION_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.FILE_EXTENSION_SIZE.remove_by_labels(alias_filter)
        kavita_metrics.VERSION.remove_by_labels(alias_filter)
        kavita_metrics.API_KEY_EXPIRATION.remove_by_labels(alias_filter)
        # Detailed metrics
        kavita_metrics.LIBRARY_TOTAL_PAGES.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_TOTAL_WORD_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_AVG_READING_TIME.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_GENRE_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.LIBRARY_FORMAT_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_PAGES.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_WORD_COUNT.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_PAGES_READ.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_USER_RATING.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_AVG_HOURS_TO_READ.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_MIN_HOURS_TO_READ.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_MAX_HOURS_TO_READ.remove_by_labels(alias_filter)
        kavita_metrics.SERIES_FORMAT.remove_by_labels(alias_filter)

    def get_server_info(self):
        """Get server information from Kavita"""
        return self._api_get("api/Server/server-info-slim")

    def get_server_stats(self):
        """Get server statistics from Kavita"""
        return self._api_get("api/Stats/server/stats")

    def get_libraries(self):
        """Get all libraries from Kavita"""
        return self._api_get("api/Library/libraries")

    def get_publication_status_counts(self):
        """Get publication status counts from Kavita"""
        return self._api_get("api/Stats/server/count/publication-status")

    def get_manga_format_counts(self):
        """Get manga format counts from Kavita"""
        return self._api_get("api/Stats/server/count/manga-format")

    def get_users(self):
        """Get all users from Kavita"""
        return self._api_get("api/Users")

    def get_file_extensions(self):
        """Get file extension statistics from Kavita"""
        return self._api_get("api/Stats/server/file-breakdown")

    def get_series_metadata(self, series_id):
        """Get metadata for a specific series"""
        return self._api_get(f"api/Series/metadata?seriesId={series_id}")

    def get_series_for_library(self, library_id):
        """Get all series for a specific library using session pooling"""
        filter_dto = {
            "statements": [
                {"field": 19, "value": str(library_id), "comparison": 0}
            ],
            "combination": 1,
            "limitTo": 0,
            "sortOptions": {"isAscending": True, "sortField": 1},
        }

        headers = self._get_auth_header()
        if headers is None:
            return None

        headers["Content-Type"] = "application/json"

        try:
            session = _get_session()
            api_url = f"{self.url}/api/Series/v2"
            res = session.post(api_url, headers=headers, json=filter_dto, timeout=30)
            if res.status_code == 200:
                return res.json()
            self.logger.debug(
                "Request for series in library %s returned status code: %s",
                library_id, res.status_code
            )
        except (RequestException, ValueError) as e:
            self.logger.debug(
                "Request for series in library %s failed with: %s", library_id, e
            )
        return None

    def _fetch_series_metadata(self, series):
        """Helper to fetch metadata for a single series"""
        series_id = series.get("id")
        if series_id:
            metadata = self.get_series_metadata(series_id)
            if metadata:
                series["metadata"] = metadata
        return series

    def _fetch_library_data(self, libraries):
        """Fetch series data for all libraries"""
        library_data = {}
        for library in libraries:
            lib_id = library["id"]
            lib_name = library.get("name", "unknown")
            series_list = self.get_series_for_library(lib_id)

            library_data[lib_id] = {
                "name": lib_name,
                "series": series_list or [],
                "series_count": len(series_list) if series_list else 0,
            }

            if self.detailed and series_list:
                self._fetch_metadata_parallel(library_data[lib_id], lib_name)

        return library_data

    def _fetch_metadata_parallel(self, lib_data, lib_name):
        """Fetch metadata for all series in a library in parallel"""
        series_list = lib_data["series"]
        self.logger.debug(
            "Fetching metadata for %d series in library %s",
            len(series_list), lib_name
        )
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_METADATA_WORKERS
        ) as executor:
            futures = {
                executor.submit(self._fetch_series_metadata, series): series
                for series in series_list
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except (RequestException, ValueError) as e:
                    self.logger.debug("Error fetching series metadata: %s", e)

    def scrape(self):
        """Scrape the Kavita Service with session pooling and parallel requests"""
        initial_time = time.time()

        self.logger.debug("Scraping Kavita Service")

        # Use JWT if legacy_auth enabled, otherwise check API key expiration
        if self.legacy_auth:
            if not self._generate_jwt():
                UP.labels(self.alias, 'kavita').set(0)
                return None
        else:
            self._check_api_key_expiration()

        UP.labels(self.alias, 'kavita').set(1)

        server_info = self.get_server_info()
        server_stats = self.get_server_stats()
        libraries = self.get_libraries()

        if any(x is None for x in (server_info, server_stats, libraries)):
            UP.labels(self.alias, 'kavita').set(0)
            return None

        library_data = self._fetch_library_data(libraries)

        end_time = time.time()
        kavita_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
        kavita_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        self.logger.debug("Scrape completed in %.2f seconds", end_time - initial_time)
        return {
            "server_info": server_info,
            "server_stats": server_stats,
            "libraries": libraries,
            "library_data": library_data,
            "publication_status": self.get_publication_status_counts() or [],
            "manga_formats": self.get_manga_format_counts() or [],
            "users": self.get_users() or [],
            "file_breakdown": self.get_file_extensions() or []
        }

    def _update_server_metrics(self, server_info, server_stats):
        """Update server-related metrics"""
        version = server_info.get("kavitaVersion", "unknown")
        kavita_metrics.VERSION.labels(self.alias, version).set(1)
        is_docker = 1 if server_info.get("isDocker", False) else 0
        kavita_metrics.IS_DOCKER.labels(self.alias).set(is_docker)

        kavita_metrics.SERIES_COUNT.labels(self.alias).set(
            server_stats.get("seriesCount", 0))
        kavita_metrics.VOLUME_COUNT.labels(self.alias).set(
            server_stats.get("volumeCount", 0))
        kavita_metrics.CHAPTER_COUNT.labels(self.alias).set(
            server_stats.get("chapterCount", 0))
        kavita_metrics.TOTAL_FILES.labels(self.alias).set(
            server_stats.get("totalFiles", 0))
        kavita_metrics.TOTAL_SIZE.labels(self.alias).set(
            server_stats.get("totalSize", 0))
        kavita_metrics.TOTAL_GENRES.labels(self.alias).set(
            server_stats.get("totalGenres", 0))
        kavita_metrics.TOTAL_TAGS.labels(self.alias).set(
            server_stats.get("totalTags", 0))
        kavita_metrics.TOTAL_PEOPLE.labels(self.alias).set(
            server_stats.get("totalPeople", 0))
        kavita_metrics.TOTAL_READING_TIME.labels(self.alias).set(
            server_stats.get("totalReadingTime", 0))

    def _update_library_metrics(self, libraries, library_data):
        """Update library-related metrics"""
        kavita_metrics.LIBRARY_COUNT.labels(self.alias).set(len(libraries))

        for library in libraries:
            lib_name = library.get("name", "unknown")
            lib_id = library.get("id")
            lib_type = LIBRARY_TYPES.get(library.get("type", 0), "Unknown")

            folder_watching = 1 if library.get("folderWatching", False) else 0
            kavita_metrics.LIBRARY_FOLDER_WATCHING.labels(
                self.alias, lib_name).set(folder_watching)

            scrobbling = 1 if library.get("allowScrobbling", False) else 0
            kavita_metrics.LIBRARY_SCROBBLING.labels(
                self.alias, lib_name).set(scrobbling)

            kavita_metrics.LIBRARY_TYPE.labels(
                self.alias, lib_name, lib_type).set(1)

            if lib_id in library_data:
                lib_info = library_data[lib_id]
                kavita_metrics.LIBRARY_SERIES_COUNT.labels(
                    self.alias, lib_name).set(lib_info["series_count"])

                if lib_info["series"]:
                    self._update_library_detailed_metrics(
                        lib_name, lib_info["series"])

    def _update_status_metrics(self, publication_status, manga_formats):
        """Update publication status and manga format metrics"""
        for status_item in publication_status:
            status_value = status_item.get("value", 0)
            status_name = PUBLICATION_STATUS.get(
                status_value, f"Unknown({status_value})")
            count = status_item.get("count", 0)
            kavita_metrics.PUBLICATION_STATUS_COUNT.labels(
                self.alias, status_name).set(count)

        for format_item in manga_formats:
            format_value = format_item.get("value", 0)
            format_name = MANGA_FORMAT.get(
                format_value, f"Unknown({format_value})")
            count = format_item.get("count", 0)
            kavita_metrics.MANGA_FORMAT_COUNT.labels(
                self.alias, format_name).set(count)

    def _update_file_metrics(self, file_breakdown):
        """Update file extension metrics"""
        for ext_item in file_breakdown.get("fileBreakdown", []):
            extension = ext_item.get("extension", "unknown")
            count = ext_item.get("totalFiles", 0)
            size = ext_item.get("totalSize", 0)
            kavita_metrics.FILE_EXTENSION_COUNT.labels(
                self.alias, extension).set(count)
            kavita_metrics.FILE_EXTENSION_SIZE.labels(
                self.alias, extension).set(size)

    def update_metrics(self, data):
        """Update the Metrics for the Kavita Service"""
        self._update_server_metrics(data["server_info"], data["server_stats"])
        self._update_library_metrics(data["libraries"], data["library_data"])
        self._update_status_metrics(
            data["publication_status"], data["manga_formats"])
        kavita_metrics.USER_COUNT.labels(self.alias).set(len(data["users"]))
        self._update_file_metrics(data["file_breakdown"])

    def _update_series_metrics(self, lib_name, series, series_label, fmt_name):
        """Update per-series detailed metrics"""
        kavita_metrics.SERIES_PAGES.labels(
            self.alias, lib_name, series_label
        ).set(series.get("pages", 0))
        kavita_metrics.SERIES_WORD_COUNT.labels(
            self.alias, lib_name, series_label
        ).set(series.get("wordCount", 0))
        kavita_metrics.SERIES_PAGES_READ.labels(
            self.alias, lib_name, series_label
        ).set(series.get("pagesRead", 0))
        kavita_metrics.SERIES_USER_RATING.labels(
            self.alias, lib_name, series_label
        ).set(series.get("userRating", 0))
        kavita_metrics.SERIES_AVG_HOURS_TO_READ.labels(
            self.alias, lib_name, series_label
        ).set(series.get("avgHoursToRead", 0))
        kavita_metrics.SERIES_MIN_HOURS_TO_READ.labels(
            self.alias, lib_name, series_label
        ).set(series.get("minHoursToRead", 0))
        kavita_metrics.SERIES_MAX_HOURS_TO_READ.labels(
            self.alias, lib_name, series_label
        ).set(series.get("maxHoursToRead", 0))
        kavita_metrics.SERIES_FORMAT.labels(
            self.alias, lib_name, series_label, fmt_name
        ).set(1)

    def _update_library_detailed_metrics(self, lib_name, series_list):
        """Update detailed metrics for a library based on its series"""
        ctx = {
            "lib_name": lib_name,
            "totals": {"pages": 0, "word_count": 0, "avg_hours": 0},
            "format_counts": {},
            "genre_counts": {},
        }

        for series in series_list:
            self._process_series(series, ctx)

        self._set_library_aggregate_metrics(ctx, len(series_list))

    def _process_series(self, series, ctx):
        """Process a single series for metrics"""
        series_name = series.get("name", "unknown")
        series_label = series_name.lower().replace(" ", "-")
        series_label = ''.join(
            e for e in series_label if e.isalnum() or e == "-"
        )

        ctx["totals"]["pages"] += series.get("pages", 0)
        ctx["totals"]["word_count"] += series.get("wordCount", 0)
        ctx["totals"]["avg_hours"] += series.get("avgHoursToRead", 0)

        format_value = series.get("format", 0)
        format_name = MANGA_FORMAT.get(format_value, f"Unknown({format_value})")
        ctx["format_counts"][format_name] = (
            ctx["format_counts"].get(format_name, 0) + 1
        )

        metadata = series.get("metadata")
        if metadata:
            for genre in metadata.get("genres", []):
                genre_name = genre.get("title", "Unknown")
                ctx["genre_counts"][genre_name] = (
                    ctx["genre_counts"].get(genre_name, 0) + 1
                )

        if self.detailed:
            self._update_series_metrics(
                ctx["lib_name"], series, series_label, format_name)

    def _set_library_aggregate_metrics(self, ctx, series_count):
        """Set aggregate metrics for a library"""
        lib_name = ctx["lib_name"]
        totals = ctx["totals"]

        kavita_metrics.LIBRARY_TOTAL_PAGES.labels(
            self.alias, lib_name).set(totals["pages"])
        kavita_metrics.LIBRARY_TOTAL_WORD_COUNT.labels(
            self.alias, lib_name).set(totals["word_count"])

        if series_count > 0:
            avg_time = totals["avg_hours"] / series_count
            kavita_metrics.LIBRARY_AVG_READING_TIME.labels(
                self.alias, lib_name).set(avg_time)

        for format_name, count in ctx["format_counts"].items():
            kavita_metrics.LIBRARY_FORMAT_COUNT.labels(
                self.alias, lib_name, format_name).set(count)

        for genre_name, count in ctx["genre_counts"].items():
            kavita_metrics.LIBRARY_GENRE_COUNT.labels(
                self.alias, lib_name, genre_name).set(count)
