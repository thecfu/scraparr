"""
Connectors module to dynamically get the Services.
And update their Metrics
"""

import hashlib
import json
import time
import logging
import concurrent.futures

from scraparr.const import API_VERSIONS

class Connectors:
    """Class to initialize Variables that are used to Identify the Connectors
    and log the last Scrape"""
    def __init__(self, workers):
        self.connectors = {}
        self.last_scrape = {}
        self.workers = workers

    def add_connector(self, service, configs):
        """Function to add a Connector on successful load into the List of Connectors"""
        importer = self.load_connector(service)

        if importer:
            self.connectors[service] = []
            if configs is not None:
                for config in configs:
                    if config.get('api_version') is None:
                        config['api_version'] = API_VERSIONS[service]
                    connector = importer.Module(config)
                    self.connectors[service].append(connector)
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

    def scrape(self):
        """Run all connectors in a threaded scheduler loop"""
        next_run = {}
        for service, conns in self.connectors.items():
            for i, conn in enumerate(conns):
                next_run[(service, i)] = time.time() + conn.interval

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            while True:
                now = time.time()
                for (service, i), run_at in next_run.items():
                    if now >= run_at:
                        connector = self.connectors[service][i]
                        executor.submit(self._scrape_connector, service, connector)
                        # keep interval consistent (no drift)
                        next_run[(service, i)] += connector.interval
                time.sleep(1)

    @staticmethod
    def _scrape_connector(service, connector):
        logging.debug("Scraping %s config %s", service, connector)
        try:
            connector.start()
        except Exception as e: # pylint: disable=broad-except
            logging.error("[%s] scrape failed: %s", service, e)
