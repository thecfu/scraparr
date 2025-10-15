"""Module for handling connector configurations and data validation."""
import abc
import logging
from abc import ABC

from scraparr.connectors import Connectors

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

    def validate_data(self, new_data):
        """Validate the Data"""
        if not new_data:
            return False

        new_hash = Connectors.get_hash(new_data)
        if new_hash != self.last_hash:
            self.last_hash = new_hash
            return True
        logging.info("No changes detected in %s for config %s", self.service, self.alias)
        return False

    def start(self):
        """Start the Scraping"""
        data = self.scrape()
        if data:
            if self.validate_data(data):
                self.update_metrics(data)
                logging.info("%s metrics updated", self.service)

    @abc.abstractmethod
    def scrape(self):
        """Scrape the Service"""

    @abc.abstractmethod
    def update_metrics(self, data):
        """Update the Metrics for the Service"""
