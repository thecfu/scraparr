"""Module to handle the jellyseerr Connector"""

import scraparr.connectors.seerr
import scraparr.metrics.jellyseerr as jellyseerr_metrics

def scrape(config):
    """Function to Scrape the Jellyseerr Service"""

    if config.get("alias", None) is None:
        config["alias"] = "jellyseerr"

    get_seerr = scraparr.connectors.seerr.GetSeerr(config, jellyseerr_metrics)
    users, requests, issues = get_seerr.get()

    if not users or not requests or not issues:
        return None

    return {"users": users, "requests": requests, "issues": issues}

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Jellyseerr Service"""

    update_seerr = scraparr.connectors.seerr.UpdateSeerr(detailed, alias, jellyseerr_metrics)
    update_seerr.update(data)
