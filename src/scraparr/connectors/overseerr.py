"""Module to handle the overseerr Connector

.. deprecated:: Use the unified 'seerr' integration instead.
"""

import logging

import scraparr.metrics.overseerr as overseerr_metrics
from scraparr.connectors.seerr import Seerr

logger = logging.getLogger(__name__)

class Module(Seerr):
    """Deprecated: Use seerr instead."""

    def __init__(self, config):
        logger.warning("The 'overseerr' integration is deprecated. "
                       "Please migrate to 'seerr' in your config.")
        Seerr.__init__(self, config, overseerr_metrics, "overseerr")
