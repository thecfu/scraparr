"""Module to handle the overseerr Connector"""

import scraparr.metrics.overseerr as overseerr_metrics
from scraparr.connectors.seerr import Seerr

class Module(Seerr):
    """Class to handle the Overseerr Metrics"""

    def __init__(self, alias):
        Seerr.__init__(self, "overseerr", alias, overseerr_metrics)
