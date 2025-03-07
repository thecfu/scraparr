"""Module to handle the jellyseerr Connector"""

import scraparr.connectors.seer
import scraparr.metrics.jellyseerr as jellyseerr_metrics

def scrape(config):
    """Function to Scrape the Jellyseerr Service"""

    if config.get("alias", None) is None:
        config["alias"] = "jellyseerr"

    get_seer = scraparr.connectors.seer.GetSeer(config, jellyseerr_metrics)
    users, requests, issues = get_seer.get()

    if not users or not requests or not issues:
        return None

    return {"users": users, "requests": requests, "issues": issues}

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Jellyseerr Service"""

    update_seer = scraparr.connectors.seer.UpdateSeer(detailed, alias, jellyseerr_metrics)
    update_seer.update(data)
