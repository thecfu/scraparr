"""Module for handling connector configurations and data validation."""
from abc import ABC, abstractmethod
import threading

import requests

from scraparr.connectors import Connectors
from scraparr.connectors.util import get_logger

_thread_local = threading.local()


def _get_session():
    """Get or create a thread-local requests.Session for connection pooling."""
    if not hasattr(_thread_local, 'session'):
        _thread_local.session = requests.Session()
    return _thread_local.session


class ConnectorModule(ABC): # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """Base Class for Connector Modules"""

    def __init__(self, config, service):
        self.url = config.get('url')
        self.api_key = config.get('api_key')
        self.alias = config.get('alias', service)
        self.api_version = config.get('api_version')
        self.service = service
        self.detailed = config.get('detailed', False)
        self.interval = config.get('interval', 30)
        self.last_hash = None
        self.exclude = set(config.get('exclude', []))
        self.logger = get_logger(f"connectors.{self.service}", self.alias)

    def validate_data(self, new_data):
        """Validate the Data"""
        if not new_data:
            return False

        new_hash = Connectors.get_hash(new_data)
        if new_hash != self.last_hash:
            self.last_hash = new_hash
            return True
        self.logger.info("No changes detected")
        return False

    def start(self):
        """Start the Scraping"""
        data = self.scrape()
        if data:
            if self.validate_data(data):
                self.clear()
                self.update_metrics(data)
                self.logger.info("metrics updated")
        else:
            self.logger.error("No data found, assuming failure")

    def get(self, endpoint):
        """Get data from API and Logs errors"""
        session = _get_session()
        api_url = self.url + (("/" + endpoint) if not endpoint.startswith("/") else endpoint)
        try:
            r = session.get(api_url, headers={"X-Api-Key": self.api_key}, timeout=20)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 401:
                self.logger.error("Unauthorized when trying to access %s: %s",
                                  self.url, r.status_code)
            elif r.status_code == 404:
                self.logger.error("Not Found, check API Version and Docs: %s, returned HTML %s",
                                  api_url, r.status_code)
            else:
                self.logger.debug("Request for %s returned unexpected HTML Status Code: %s",
                                  api_url, r.status_code)
        except requests.exceptions.RequestException as e:
            self.logger.debug("Request for %s failed with: %s", api_url, e)
        return {}

    def post(self, endpoint, data):
        """Post data to API and Logs errors"""
        session = _get_session()
        api_url = self.url + ("/" + endpoint if not endpoint.startswith("/") else endpoint)
        try:
            r = session.post(api_url, headers={"X-Api-Key": self.api_key}, json=data, timeout=20)
            if r.status_code in (200, 201):
                return r.json()
            if r.status_code == 401:
                self.logger.error("Unauthorized when trying to access %s: %s",
                                  self.url, r.status_code)
            elif r.status_code == 404:
                self.logger.error("Not Found, check API Version and Docs: %s, returned HTML %s",
                                  api_url, r.status_code)
            else:
                self.logger.debug("Request for %s returned unexpected HTML Status Code: %s",
                                  api_url, r.status_code)
        except requests.exceptions.RequestException as e:
            self.logger.debug("Request for %s failed with: %s", api_url, e)
        return {}

    def get_root_folder(self):
        """Get the Root Folder Data"""

        def filter_data(folder, disks):
            report = []
            seen_paths = set()  # To keep track of added paths

            for rootfolder in folder:
                for disk in disks:
                    if disk["path"] == rootfolder["path"]:
                        if disk["path"] not in seen_paths:
                            report.append(disk)
                            seen_paths.add(disk["path"])
                        break
                else:
                    for disk in disks:
                        if rootfolder["path"].startswith(disk["path"]) and disk["path"] != '/':
                            if disk["path"] not in seen_paths:
                                report.append(disk)
                                seen_paths.add(disk["path"])
                            break
                    else:
                        self.logger.warning("No diskspace data found for %s,"
                                        " using only available Data", rootfolder["path"])
                        report.append({
                            "path": rootfolder["path"],
                            "freeSpace": rootfolder["freeSpace"],
                            "totalSpace": -1
                        })
                        seen_paths.add(rootfolder["path"])
            return report

        data = self.get("/rootfolder")
        if data:
            diskspace_data = self.get("/diskspace")
            if diskspace_data:
                return filter_data(data, diskspace_data)
        self.logger.warning("No rootfolder data found")
        return None

    @abstractmethod
    def scrape(self):
        """Scrape the Service"""

    @abstractmethod
    def update_metrics(self, data):
        """Update the Metrics for the Service"""

    @abstractmethod
    def clear(self):
        """Clear the Metrics for the Service"""
