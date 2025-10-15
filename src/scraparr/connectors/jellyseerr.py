"""Module to handle the jellyseerr Connector"""

import scraparr.metrics.jellyseerr as jellyseerr_metrics
from scraparr.connectors.seerr import Seerr

class Module(Seerr):
    """Class to handle the Jellyseerr Metrics"""

    def __init__(self, alias):
        Seerr.__init__(self, "jellyseerr", alias, jellyseerr_metrics)
