"""
Connectors module to dynamically get the Services.
And update their Metrics
"""

import hashlib
import json
import logging
import concurrent.futures
from scraparr.util import get

indexers = ["sonarr", "radarr"]

class Connectors:
    """Class to initialize Variable that are used to Identify the Connectors
     and log the last Scrape"""
    def __init__(self):
        self.connectors = {}
        self.last_scrape = {}

    def add_connector(self, service, config):
        """Function to add a Connector on successful load into the List of Connectors"""
        importer = self.load_connector(service)

        if importer:
            self.connectors[service] = {}
            self.connectors[service]["function"] = importer
            self.connectors[service]["config"] = config
            self.last_scrape[service] = None
        else:
            logging.error("Couldn't import Connector")

    @staticmethod
    def load_connector(service):
        """Function to Load the Connector from the Connectors Folder"""
        try:
            return __import__(f"scraparr.connectors.{service}", fromlist=[service])
        except ImportError:
            logging.error("No connector found for %s", service)
            return None

    @staticmethod
    def get_hash(data):
        """Function to get the Hash of the Data"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()

    def scrape_service(self, service):
        """Function to Scrape the Service and Update the Metrics"""
        config = self.connectors[service]["config"]
        scrape_data = {"data": self.connectors[service]["function"].scrape(config),
                       "system": self.get_system_data(service)}
        if scrape_data["data"] is not None and scrape_data["system"] is not None:
            new_hash = self.get_hash(scrape_data)
            if new_hash != self.last_scrape[service]:
                self.last_scrape[service] = new_hash
                func = self.connectors[service]["function"]
                func.update_metrics(scrape_data, config.get('detailed'))
                logging.info("%s metrics updated", service)
            else:
                logging.info("No changes detected in %s", service)
        else:
            logging.warning("% scrape failed", service)

    def get_system_data(self, service):
        """Function to get the System Data"""
        def root_folder():
            def filter_data(folder, disks):
                report = []
                seen_paths = set()  # To keep track of added paths

                for rootfolder in folder:
                    for disk in disks:
                        if disk["path"] == rootfolder["path"]:
                            if not disk["path"] in seen_paths:
                                report.append(disk)
                                seen_paths.add(disk["path"])
                            break
                    else:
                        for disk in disks:
                            if rootfolder["path"].startswith(disk["path"]) and disk["path"] != '/':
                                if not disk["path"] in seen_paths:
                                    report.append(disk)
                                    seen_paths.add(disk["path"])
                                break
                        else:
                            logging.warning("No diskspace data found for %s,"
                                            " using only available Data", rootfolder["path"])
                            report.append({
                                "path": rootfolder["path"],
                                "freeSpace": rootfolder["freeSpace"],
                                "totalSpace": -1
                            })
                            seen_paths.add(rootfolder["path"])
                return report
            data = get(f"{url}/api/{api_version}/rootfolder", api_key)
            if data:
                diskspace_data = get(f"{url}/api/{api_version}/diskspace", api_key)
                if diskspace_data:
                    return filter_data(data, diskspace_data)
            logging.warning("No rootfolder data found")
            return None

        def queue():
            return get(f"{url}/api/{api_version}/queue/status", api_key)

        def status():
            return get(f"{url}/api/{api_version}/system/status", api_key)

        url = self.connectors[service]["config"].get('url')
        api_key = self.connectors[service]["config"].get('api_key')
        api_version = self.connectors[service]["config"].get('api_version', 'v1')

        if service in indexers:
            return {'root_folder': root_folder(), 'queue': queue(), 'status': status()}
        return {'status': status()}

    def scrape(self):
        """Function to Scrape all the Services"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.scrape_service, service): service
                for service in self.connectors
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error("Scrape failed for %s: %s", futures[future], e)
                    raise e
