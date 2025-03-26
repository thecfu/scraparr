"""
Module to handle the Metrics of the Whisparr Service
"""

from scraparr.connectors import sonarr_api
import scraparr.metrics.whisparr as whisparr_metrics

def scrape(config):
    """Scrape the Whisparr Service"""

    api = sonarr_api.SonarrApi("sonarr", config, whisparr_metrics)
    return api.scrape()

def update_metrics(series, detailed, alias):
    """Update the Metrics for the Whisparr Service"""

    config = {"detailed": detailed, "alias": alias}

    api = sonarr_api.SonarrApi("whisparr", config, whisparr_metrics)
    api.update_metrics(series)
