"""
Module to handle the Metrics of the Sonarr Service
"""

from scraparr.connectors import sonarr_api
import scraparr.metrics.sonarr as sonarr_metrics

def scrape(config):
    """Scrape the Sonarr Service"""

    api = sonarr_api.SonarrApi("sonarr", config, sonarr_metrics)
    return api.scrape()

def update_metrics(series, detailed, alias):
    """Update the Metrics for the Sonarr Service"""

    config = {"detailed": detailed, "alias": alias}

    api = sonarr_api.SonarrApi("sonarr", config, sonarr_metrics)
    api.update_metrics(series)
