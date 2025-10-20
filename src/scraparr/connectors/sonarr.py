"""
Module to handle the Metrics of the Sonarr Service
"""

import scraparr.metrics.sonarr as sonarr_metrics
from scraparr.connectors.sonarr_api import SonarrApi

class Module(SonarrApi):
    """Scrape the Sonarr Service"""

    def __init__(self, config):
        SonarrApi.__init__(self, "sonarr", config, sonarr_metrics)
