"""
Connectors module to dynamically get the Services.
And update their Metrics
"""

import hashlib
import json
import time
import logging
import concurrent.futures

class Connectors:
    """Class to initialize Variables that are used to Identify the Connectors
    and log the last Scrape"""
    def __init__(self):
        self.connectors = {}
        self.last_scrape = {}

    def add_connector(self, service, configs):
        """Function to add a Connector on successful load into the List of Connectors"""
        importer = self.load_connector(service)

        api_versions = {
            "sonarr": "v3",
            "radarr": "v3",
            "prowlarr": "v1", 
            "bazarr": "dummy",
            "readarr": "v1",
            "jellyseerr": "v1",
            "overseerr": "v1",
        }

        if importer:
            self.connectors[service] = []
            if configs is not None:
                for config in configs:
                    if config.get('api_version') is None:
                        config['api_version'] = api_versions[service]
                    connector_entry = {
                        "function": importer,
                        "config": config
                    }
                    self.connectors[service].append(connector_entry)
                    self.last_scrape[service] = [None] * len(configs)
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

    def scrape_service(self, service, config_index):
        """Function to Scrape the Service and Update the Metrics"""
        config = self.connectors[service][config_index]["config"]
        alias = config.get('alias', service)
        scrape_data = self.connectors[service][config_index]["function"].scrape(config)
        if scrape_data:
            new_hash = self.get_hash(scrape_data)
            if new_hash != self.last_scrape[service][config_index]:
                self.last_scrape[service][config_index] = new_hash
                func = self.connectors[service][config_index]["function"]
                func.update_metrics(
                    scrape_data,
                    config.get('detailed', False),
                    alias
                )
                logging.info("%s metrics updated for config %s", service, alias)
            else:
                logging.info("No changes detected in %s for config %s", service, alias)
        else:
            logging.error("%s scrape failed for config %s", service, alias)

    def scrape(self):
        """Function to Scrape all the Services"""

        running = True

        def scrape_with_interval(service, config_index, interval):
            while running:
                self.scrape_service(service, config_index)
                time.sleep(interval)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for service, configs in self.connectors.items():
                for config_index, config in enumerate(configs):
                    interval = config["config"].get('interval', 30)
                    futures.append(executor.submit(
                        scrape_with_interval,
                        service,
                        config_index,
                        interval
                    ))
