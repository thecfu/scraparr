"""
Module to handle the Metrics of the Whisparr Service
"""

import scraparr.metrics.whisparr as whisparr_metrics
from scraparr.connectors.sonarr_api import SonarrApi

class Module(SonarrApi):
    """Class to handle the Whisparr Metrics"""

    def __init__(self, config):
        SonarrApi.__init__(self, "whisparr", config, whisparr_metrics)
