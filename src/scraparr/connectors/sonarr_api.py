"""
Module to handle the Metrics of the SonarrAPI
"""

import time
from dateutil.parser import parse

from scraparr.connectors import util
from scraparr.connectors.module import ConnectorModule
from scraparr.metrics.general import UP

class SonarrApi(ConnectorModule):
    """Class to handle the SonarrAPI Metrics"""

    def __init__(self, service, config, metrics):
        ConnectorModule.__init__(self, config, service)
        self.metrics = metrics
        self.url = f"{self.url}/api/{self.api_version}"

    def clear(self):
        """Clear the metrics"""

        self.metrics.SERIES_EPISODE_COUNT.remove_by_labels({"alias": self.alias})
        self.metrics.SERIES_MISSING_EPISODE_COUNT.remove_by_labels({"alias": self.alias})
        self.metrics.SERIES_COUNT.remove_by_labels({"alias": self.alias})
        self.metrics.SERIES_DISK_SIZE.remove_by_labels({"alias": self.alias})
        self.metrics.SERIES_DOWNLOAD_PERCENTAGE.remove_by_labels({"alias": self.alias})
        self.metrics.SERIES_MONITORED.remove_by_labels({"alias": self.alias})

    def get_series(self):
        """Grab the Series from the SonarrAPI Endpoint"""

        initial_time = time.time()
        res = self.get("/series")
        end_time = time.time()
        if res == {}:
            UP.labels(self.alias, self.service).set(0)
        else:
            for series in res:
                episodes = self.get(f"/episodefile?seriesId={series['id']}")
                series["episodes"] = episodes

            UP.labels(self.alias, self.service).set(1)
            self.metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
            self.metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)
        return res

    def analyse_series(self, series):
        """Analyse the Series and set the Correct Metrics"""

        status_labels = {
            "continuing": {
                "func": [self.metrics.CONTINUING_SERIES, self.metrics.CONTINUING_SERIES_T],
                "paths": {"total": 0}
            },
            "upcoming": {
                "func": [self.metrics.UPCOMING_SERIES, self.metrics.UPCOMING_SERIES_T],
                "paths": {"total": 0}
            },
            "ended": {
                "func": [self.metrics.ENDED_SERIES, self.metrics.ENDED_SERIES_T],
                "paths": {"total": 0}
            },
            "deleted": {
                "func": [self.metrics.DELETED_SERIES, self.metrics.DELETED_SERIES_T],
                "paths": {"total": 0}
            }
        }

        quality_count = {}
        genre_count = {}

        self.metrics.SERIES_COUNT_T.labels(self.alias).set(len(series))

        used_size = {"total": 0}

        counter = {
            "path": {
                "total": {"paths": {}, "func": self.metrics.SERIES_COUNT},
                "missing": {"paths": {}, "func": self.metrics.MISSING_EPISODE_COUNT},
                "monitored": {"paths": {}, "func": self.metrics.MONITORED_SERIES},
                "unmonitored": {"paths": {}, "func": self.metrics.UNMONITORED_SERIES},
                "episode": {"paths": {}, "func": self.metrics.EPISODE_COUNT}
            },
            "total": {
                "missing": [0, self.metrics.MISSING_EPISODE_COUNT_T],
                "monitored": [0, self.metrics.MONITORED_SERIES_T],
                "unmonitored": [0, self.metrics.UNMONITORED_SERIES_T],
                "episode": [0, self.metrics.EPISODE_COUNT_T]
            }
        }

        for serie in series:
            title = serie["titleSlug"]
            stats = serie.get("statistics", None)

            if stats is None:
                self.logger.warning("No statistics found for %s", title)
                continue

            util.increase_quality_count(quality_count, serie["episodes"], serie["rootFolderPath"])

            root_folder = serie["rootFolderPath"]

            util.update_count(
                [stats["sizeOnDisk"], used_size],
                root_folder, counter["path"],
                status_labels, [stats["episodeFileCount"], counter["total"]]
            )

            util.update_status(serie["status"], root_folder, status_labels)

            util.update_genre_count(serie["genres"], genre_count, root_folder)

            for season in serie["seasons"]:
                if season["monitored"]:
                    s_episode_count = season["statistics"]["episodeCount"]
                    missing = s_episode_count - season["statistics"]["episodeFileCount"]
                    counter["total"]["missing"][0] += missing
                    counter["path"]["missing"]["paths"][root_folder] += missing
                    if self.detailed:
                        (self.metrics.SERIES_MISSING_EPISODE_COUNT
                         .labels(self.alias, title).inc(missing))

            if self.detailed:
                (self.metrics.SERIES_EPISODE_COUNT.labels(self.alias, title)
                 .set(stats["episodeCount"]))
                (self.metrics.SERIES_SEASON_COUNT.labels(self.alias, title)
                 .set(stats["seasonCount"]))
                (self.metrics.SERIES_DISK_SIZE.labels(self.alias, title)
                 .set(stats["sizeOnDisk"]))
                (self.metrics
                    .SERIES_DOWNLOAD_PERCENTAGE.labels(self.alias, title)
                    .set(stats["percentOfEpisodes"]))
                (self.metrics.SERIES_MONITORED.labels(self.alias, title)
                 .set(1 if serie["monitored"] else 0))

            if serie["monitored"]:
                counter["total"]["monitored"][0] += 1
                counter["path"]["monitored"]["paths"][root_folder] += 1
            else:
                counter["total"]["unmonitored"][0] += 1
                counter["path"]["unmonitored"]["paths"][root_folder] += 1

        util.update_media_metrics(
            [[
                quality_count,
                self.metrics.QUALITY_EPISODE_COUNT,
                self.metrics.QUALITY_EPISODE_COUNT_T
            ],
            [used_size, self.metrics.TOTAL_DISK_SIZE, self.metrics.TOTAL_DISK_SIZE_T],
            [genre_count, self.metrics.SERIES_GENRES_COUNT, self.metrics.SERIES_GENRES_COUNT_T],
            status_labels, counter], self.alias
        )

    def update_system_data(self, data):
        """Update the System Data Metrics"""
        for disk in data['root_folder']:
            (self.metrics.FREE_DISK_SIZE.labels(self.alias, disk["path"])
             .set(disk["freeSpace"]))
            (self.metrics.AVAILABLE_DISK_SIZE.labels(self.alias, disk["path"])
             .set(disk["totalSpace"]))

        self.metrics.QUEUE_COUNT.labels(self.alias).set(data["queue"]["totalCount"])
        self.metrics.QUEUE_ERROR.labels(self.alias).set(data["queue"]["errors"])
        self.metrics.QUEUE_WARNING.labels(self.alias).set(data["queue"]["warnings"])

        start_time = parse(data["status"]["startTime"]).timestamp()
        build_time = parse(data["status"]["buildTime"]).timestamp()
        self.metrics.START_TIME.labels(self.alias).set(start_time)
        self.metrics.BUILD_TIME.labels(self.alias).set(build_time)

    def scrape(self):
        """Scrape the SonarrAPI Service"""

        queue = self.get("/queue/status")
        status = self.get("/system/status")

        scrape_data = {
            "system": {
                "root_folder": self.get_root_folder(),
                "queue": queue,
                "status": status
            },
            "data": self.get_series()
        }

        if scrape_data["data"] == {} or scrape_data["system"]["status"] == {}:
            return {}

        return scrape_data

    def update_metrics(self, data):
        """Update the Metrics for the SonarrAPI Service"""

        self.analyse_series(data["data"])
        self.update_system_data(data["system"])
