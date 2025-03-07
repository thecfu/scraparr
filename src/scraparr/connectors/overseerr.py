"""Module to handle the overseerr Connector"""

import scraparr.connectors.seer
import scraparr.metrics.overseerr as overseerr_metrics

def scrape(config):
    """Function to Scrape the Overseerr Service"""

    if config.get("alias", None) is None:
        config["alias"] = "overseerr"

    get_seer = scraparr.connectors.seer.GetSeer(config, overseerr_metrics)
    users, requests, issues = get_seer.get()

    if not users or not requests or not issues:
        return None

    return {"users": users, "requests": requests, "issues": issues}

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Overseerr Service"""

    update_seer = scraparr.connectors.seer.UpdateSeer(detailed, alias, overseerr_metrics)
    update_seer.update(data)
