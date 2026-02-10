"""
Module to handle the Metrics of the Radarr Service
"""

import time
from dateutil.parser import parse

import scraparr.metrics.radarr as radarr_metrics
from scraparr.connectors.module import ConnectorModule
from scraparr.metrics.general import UP
from scraparr.connectors import util

class Module(ConnectorModule):
    """Module Class for Radarr"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "Radarr")
        self.url = f"{self.url}/api/{self.api_version}"

    def clear(self):
        """Clear the Radarr metrics"""
        radarr_metrics.MOVIE_FILE_COUNT.remove_by_labels({"alias": self.alias})
        radarr_metrics.MOVIE_DISK_SIZE.remove_by_labels({"alias": self.alias})
        radarr_metrics.MOVIE_MONITORED.remove_by_labels({"alias": self.alias})
        radarr_metrics.MOVIE_MISSING.remove_by_labels({"alias": self.alias})

    def _normalize_movie_file(self, movie):
        """Normalize movieFile to list format, using embedded data when possible."""
        movie_file_count = movie.get('statistics', {}).get('movieFileCount', 0)

        if movie_file_count == 0:
            return []

        if movie_file_count > 1:
            return self.get(f"/moviefile?movieId={movie['id']}")

        embedded_file = movie.get('movieFile')
        return [embedded_file] if embedded_file else []

    def get_movies(self):
        """Grab the Movies from the Radarr Endpoint"""

        res = self.get("/movie")

        if res == {}:
            UP.labels(self.alias, 'radarr').set(0)
        else:
            for movie in res:
                movie["movieFile"] = self._normalize_movie_file(movie)

            UP.labels(self.alias, 'radarr').set(1)
        return res

    def analyse_movies(self, movies):
        """Analyse the Movies and set the Correct Metrics"""

        status_labels = {
            "tba": {
                "func": [radarr_metrics.TBA_MOVIES, radarr_metrics.TBA_MOVIES_T],
                "paths": {"total": 0}
            },
            "in cinemas": {
                "func": [radarr_metrics.IN_CINEMAS_MOVIES, radarr_metrics.IN_CINEMAS_MOVIES_T],
                "paths": {"total": 0}
            },
            "announced": {
                "func": [radarr_metrics.ANNOUNCED_MOVIES, radarr_metrics.ANNOUNCED_MOVIES_T],
                "paths": {"total": 0}
            },
            "released": {
                "func": [radarr_metrics.RELEASED_MOVIES, radarr_metrics.RELEASED_MOVIES_T],
                "paths": {"total": 0}
            },
            "deleted": {
                "func": [radarr_metrics.DELETED_MOVIES, radarr_metrics.DELETED_MOVIES_T],
                "paths": {"total": 0}
            }
        }

        quality_count = {}
        genre_count = {}

        radarr_metrics.MOVIE_COUNT_T.labels(self.alias).set(len(movies))

        used_size = {"total": 0}

        counter = {
            "path": {
                "total": {"paths": {}, "func": radarr_metrics.MOVIE_COUNT},
                "missing": {"paths": {}, "func": radarr_metrics.MISSING_MOVIES_COUNT},
                "monitored": {"paths": {}, "func": radarr_metrics.MONITORED_MOVIES},
                "unmonitored": {"paths": {}, "func": radarr_metrics.UNMONITORED_MOVIES}
            },
            "total": {
                "missing": [0, radarr_metrics.MISSING_MOVIES_COUNT_T],
                "monitored": [0, radarr_metrics.MONITORED_MOVIES_T],
                "unmonitored": [0, radarr_metrics.UNMONITORED_MOVIES_T]
            }
        }

        for movie in movies:
            title = movie["title"].lower().replace(" ", "-")
            title = ''.join(e for e in title if e.isalnum() or e == "-")

            root_folder = movie["rootFolderPath"]

            util.increase_quality_count(quality_count, movie["movieFile"], root_folder)

            size_on_disk = movie["statistics"]["sizeOnDisk"]
            util.update_count(
                [size_on_disk, used_size],
                root_folder, counter["path"], status_labels)

            if self.detailed:
                (radarr_metrics.MOVIE_FILE_COUNT
                    .labels(self.alias, title)
                    .set(movie["statistics"]["movieFileCount"])
                )
                (radarr_metrics.MOVIE_DISK_SIZE.labels(self.alias, title)
                 .set(size_on_disk))
                (radarr_metrics.MOVIE_MONITORED.labels(self.alias, title)
                 .set(1 if movie["monitored"] else 0))

            # Status-Verarbeitung mit Dictionary
            status = movie["status"].lower()
            util.update_status(status, root_folder, status_labels)

            util.update_genre_count(movie["genres"], genre_count, root_folder)

            util.update_monitoring(
                [movie, counter["path"], counter["total"]],
                [title, root_folder,
                self.detailed, radarr_metrics.MOVIE_MISSING],
                self.alias
            )

        util.update_media_metrics(
            [[quality_count, radarr_metrics.QUALITY_MOVIE_COUNT,
              radarr_metrics.QUALITY_MOVIE_COUNT_T],
            [used_size, radarr_metrics.TOTAL_DISK_SIZE, radarr_metrics.TOTAL_DISK_SIZE_T],
            [genre_count, radarr_metrics.MOVIE_GENRES_COUNT, radarr_metrics.MOVIE_GENRES_COUNT_T],
            status_labels, counter], self.alias
        )

    def update_system_data(self, data):
        """Update the System Metrics"""

        for disk in data['root_folder']:
            (radarr_metrics.FREE_DISK_SIZE.labels(self.alias, disk["path"])
             .set(disk["freeSpace"]))
            (radarr_metrics.AVAILABLE_DISK_SIZE.labels(self.alias, disk["path"])
             .set(disk["totalSpace"]))

        radarr_metrics.QUEUE_COUNT.labels(self.alias).set(data["queue"]["totalCount"])
        radarr_metrics.QUEUE_ERROR.labels(self.alias).set(data["queue"]["errors"])
        radarr_metrics.QUEUE_WARNING.labels(self.alias).set(data["queue"]["warnings"])

        start_time = parse(data["status"]["startTime"]).timestamp()
        build_time = parse(data["status"]["buildTime"]).timestamp()
        radarr_metrics.START_TIME.labels(self.alias).set(start_time)
        radarr_metrics.BUILD_TIME.labels(self.alias).set(build_time)

    def scrape(self):
        """Scrape the Radarr Service"""
        initial_time = time.time()
        queue = self.get("/queue/status")
        status = self.get("/system/status")

        data = self.get_movies()
        system = {
            "root_folder": self.get_root_folder(),
            "queue": queue,
            "status": status
        }
        end_time = time.time()

        radarr_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
        radarr_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)

        if data == {} or system["status"] == {}:
            return {}

        return {"data": data, "system": system}

    def update_metrics(self, data):
        """Update the Radarr Metrics"""

        self.analyse_movies(data['data'])
        self.update_system_data(data['system'])
