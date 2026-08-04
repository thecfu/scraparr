"""
Module to handle the Metrics of the Sportarr Service
"""

import scraparr.metrics.sportarr as sportarr_metrics
from scraparr.connectors.sonarr_api import SonarrApi

class Module(SonarrApi):
    """Class to handle the Sportarr Metrics"""

    def __init__(self, config):
        SonarrApi.__init__(self, "sportarr", config, sportarr_metrics)
