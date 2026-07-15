"""
Module to handle the Metrics of the Lidarr Service
"""

import time
import logging
from dateutil.parser import parse

import scraparr.metrics.lidarr as lidarr_metrics
from scraparr.connectors.module import ConnectorModule
from scraparr.metrics.general import UP
from scraparr.connectors import util

class Module(ConnectorModule):
    """Module Class for Lidarr"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "Lidarr")
        self.url = f"{self.url}/api/{self.api_version}"

    def clear(self):
        """Clear the Lidarr metrics"""
        lidarr_metrics.ARTIST_TRACK_COUNT.remove_by_labels({"alias": self.alias})
        lidarr_metrics.ARTIST_RELEASE_COUNT.remove_by_labels({"alias": self.alias})
        lidarr_metrics.ARTIST_MONITORED.remove_by_labels({"alias": self.alias})
        lidarr_metrics.ARTIST_DISK_SIZE.remove_by_labels({"alias": self.alias})
        lidarr_metrics.ARTIST_MISSING_RELEASE_COUNT.remove_by_labels({"alias": self.alias})

    def get_artists(self):
        """Grab Artist information from the Lidarr endpoint"""

        initial_time = time.time()
        res = self.get("/artist")
        end_time = time.time()
        if res == {}:
            UP.labels(self.alias, 'lidarr').set(0)
        else:
            for artist in res:
                releases = self.get(f"/album?artistId={artist["id"]}")
                track_files = self.get(f"/trackfile?artistId={artist["id"]}")
                artist["releases"] = releases
                artist["trackFiles"] = track_files
            UP.labels(self.alias, 'lidarr').set(1)
            lidarr_metrics.LAST_SCRAPE.labels(self.alias).set(end_time)
            lidarr_metrics.SCRAPE_DURATION.labels(self.alias).set(end_time - initial_time)
        return res

    # pylint: disable=too-many-locals, too-many-statements, too-many-branches
    def analyse_artists(self, artists):
        """Analyse Artists and set the correct metrics"""

        status_labels = {
            "continuing": {
                "func": [lidarr_metrics.CONTINUING_ARTIST, lidarr_metrics.CONTINUING_ARTIST_T],
                "paths": {"total": 0}
            },
            "ended": {
                "func": [lidarr_metrics.ENDED_ARTIST, lidarr_metrics.ENDED_ARTIST_T],
                "paths": {"total": 0}
            }
        }

        quality_count = {}
        type_count = {}

        artist_count = 0

        used_size = {"total": 0}

        counter = {
            "path": {
                "total": {"paths": {}, "func": lidarr_metrics.ARTIST_COUNT},
                "missing": {"paths": {}, "func": lidarr_metrics.MISSING_RELEASE_COUNT},
                "monitored": {"paths": {}, "func": lidarr_metrics.MONITORED_ARTIST},
                "unmonitored": {"paths": {}, "func": lidarr_metrics.UNMONITORED_ARTIST}
            },
            "total": {
                "missing": [0, lidarr_metrics.MISSING_RELEASE_COUNT_T],
                "monitored": [0, lidarr_metrics.MONITORED_ARTIST_T],
                "unmonitored": [0, lidarr_metrics.UNMONITORED_ARTIST_T]
            }
        }

        release_counter = {
            "path": {
                "monitored": {"paths": {}},
                "unmonitored": {"paths": {}}
            },
            "total": {
                "monitored": 0,
                "unmonitored": 0
            }
        }

        for artist in artists:
            root_folder = artist["rootFolderPath"]
            if root_folder in self.exclude:
                self.logger.debug("Excluding %s (rootFolderPath: %s)",
                                  artist["cleanName"], root_folder)
                continue
            artist_count += 1

            name = artist["cleanName"]
            stats = artist.get("statistics", None)

            if stats is None:
                logging.warning("No statistics found for %s", name)
                continue

            release_counter["path"]["monitored"]["paths"].setdefault(root_folder, 0)
            release_counter["path"]["unmonitored"]["paths"].setdefault(root_folder, 0)

            util.increase_quality_count(quality_count, artist["trackFiles"], root_folder)

            util.update_count(
                [stats["sizeOnDisk"], used_size],
                root_folder, counter["path"],
                status_labels
            )

            util.update_status(artist["status"], root_folder, status_labels)

            util.update_type_count(artist["releases"], type_count, root_folder)

            missing_release_count = 0
            for release in artist["releases"]:
                if release.get("statistics", None) is None:
                    logging.warning("No statistics found for %s by %s", release["title"], name)
                    continue
                if release["monitored"]:
                    release_counter["total"]["monitored"] += 1
                    release_counter["path"]["monitored"]["paths"][root_folder] += 1
                    missing = release["statistics"]["percentOfTracks"] != 100
                    if missing:
                        missing_release_count += 1
                        counter["total"]["missing"][0] += 1
                        counter["path"]["missing"]["paths"][root_folder] += 1
                else:
                    release_counter["total"]["unmonitored"] += 1
                    release_counter["path"]["unmonitored"]["paths"][root_folder] += 1

            if self.detailed:
                (lidarr_metrics.ARTIST_RELEASE_COUNT.labels(self.alias, name)
                .set(stats["albumCount"]))
                (lidarr_metrics.ARTIST_TRACK_COUNT.labels(self.alias, name)
                .set(stats["trackCount"]))
                (lidarr_metrics.ARTIST_DISK_SIZE.labels(self.alias, name)
                .set(stats["sizeOnDisk"]))
                (lidarr_metrics.ARTIST_MISSING_RELEASE_COUNT.labels(self.alias, name)
                .set(missing_release_count))
                (lidarr_metrics.ARTIST_MONITORED.labels(self.alias, name)
                .set(1 if artist["monitored"] else 0))

            # pylint: disable=duplicate-code
            if artist["monitored"]:
                counter["total"]["monitored"][0] += 1
                counter["path"]["monitored"]["paths"][root_folder] += 1
            else:
                counter["total"]["unmonitored"][0] += 1
                counter["path"]["unmonitored"]["paths"][root_folder] += 1

        lidarr_metrics.ARTIST_COUNT_T.labels(self.alias).set(artist_count)

        (lidarr_metrics.MONITORED_RELEASE_T.labels(self.alias)
         .set(release_counter["total"]["monitored"]))
        (lidarr_metrics.UNMONITORED_RELEASE_T.labels(self.alias)
         .set(release_counter["total"]["unmonitored"]))
        for folder, count in release_counter["path"]["monitored"]["paths"].items():
            lidarr_metrics.MONITORED_RELEASE.labels(self.alias, folder).set(count)
        for folder, count in release_counter["path"]["unmonitored"]["paths"].items():
            lidarr_metrics.UNMONITORED_RELEASE.labels(self.alias, folder).set(count)

        util.update_media_metrics(
            [[
                quality_count,
                lidarr_metrics.QUALITY_TRACK_COUNT,
                lidarr_metrics.QUALITY_TRACK_COUNT_T
            ],
            [used_size, lidarr_metrics.TOTAL_DISK_SIZE, lidarr_metrics.TOTAL_DISK_SIZE_T],
            [type_count, lidarr_metrics.RELEASE_TYPE_COUNT, lidarr_metrics.RELEASE_TYPE_COUNT_T],
            status_labels, counter], self.alias
        )

    def update_system_data(self, data):
        """Update the System Data Metrics"""
        for disk in data["root_folder"]:
            lidarr_metrics.FREE_DISK_SIZE.labels(self.alias, disk["path"]).set(disk["freeSpace"])
            (lidarr_metrics.AVAILABLE_DISK_SIZE.labels(self.alias, disk["path"])
             .set(disk["totalSpace"]))

        lidarr_metrics.QUEUE_COUNT.labels(self.alias).set(data["queue"]["totalCount"])
        lidarr_metrics.QUEUE_ERROR.labels(self.alias).set(data["queue"]["errors"])
        lidarr_metrics.QUEUE_WARNING.labels(self.alias).set(data["queue"]["warnings"])

        start_time = parse(data["status"]["startTime"]).timestamp()
        build_time = parse(data["status"]["buildTime"]).timestamp()
        lidarr_metrics.START_TIME.labels(self.alias).set(start_time)
        lidarr_metrics.BUILD_TIME.labels(self.alias).set(build_time)

    def scrape(self):
        """Scrape the Lidarr Service"""

        data = self.get_artists()
        system = {
            "root_folder": self.get_root_folder(),
            "queue": self.get("/queue/status"),
            "status": self.get("/system/status")
        }

        if data == {} or system["status"] == {}:
            logging.error("No Data found for Lidarr, assuming Failure")
            return {}

        return {"data": data, "system": system}

    def update_metrics(self, data):
        """Update the Lidarr Metrics"""

        self.analyse_artists(data["data"])
        self.update_system_data(data["system"])
