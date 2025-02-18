"""
Module to handle the Metrics of the Prowlarr Service
"""

import time
from datetime import datetime

from scraparr.util import get
from scraparr.metrics.general import UP
import scraparr.metrics.prowlarr as prowlarr_metrics

def get_indexers(url, api_key, version, alias):
    """Grab the Indexers from the Prowlarr Endpoint"""

    initial_time = time.time()
    res = get(f"{url}/api/{version}/indexer", api_key)
    end_time = time.time()

    if res == {}:
        UP.labels(alias, 'prowlarr').set(0)
    else:
        status = get(f"{url}/api/{version}/indexerstatus", api_key)

        # Create a dictionary for fast lookup
        stat_dict = {stat['indexerId']: stat for stat in status}

        # Update the status if the id matches
        for indexer in res:
            if indexer['id'] in stat_dict:
                indexer['status'] = stat_dict[indexer['id']]

        UP.labels(alias, 'prowlarr').set(1)
        prowlarr_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        prowlarr_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
    return res

def get_applications(url, api_key, version, alias):
    """Grab the Applications from the Prowlarr Endpoint"""

    res = get(f"{url}/api/{version}/applications", api_key)

    if res == {}:
        UP.labels(alias).set(0)
    else:
        UP.labels(alias).set(1)
    return res

def update_system_data(data, alias):
    """Update the System Data"""

    start_time = datetime.strptime(data["status"]["startTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    build_time = datetime.strptime(data["status"]["buildTime"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    prowlarr_metrics.START_TIME.labels(alias).set(start_time)
    prowlarr_metrics.BUILD_TIME.labels(alias).set(build_time)

def analyse_applications(applications, detailed, alias):
    """Analyse the Applications"""

    prowlarr_metrics.APPLICATION_COUNT.labels(alias).set(len(applications))
    enabled_t = 0
    sync_level_count = {}

    for application in applications:
        enabled = 1 if application["enable"] else 0
        enabled_t += enabled
        sync_level = application["syncLevel"]
        if sync_level in sync_level_count:
            sync_level_count[sync_level] += 1
        else:
            sync_level_count[sync_level] = 1

        if detailed:
            prowlarr_metrics.APPLICATION_ENABLED.labels(alias, application["name"]).set(enabled)
            (prowlarr_metrics
                .APPLICATION_SYNC_LEVEL
                .labels(alias, application["name"], sync_level).set(1)
            )

    prowlarr_metrics.APPLICATION_ENABLED_T.labels(alias).set(enabled_t)
    for sync_level, count in sync_level_count.items():
        (prowlarr_metrics
            .APPLICATION_SYNC_LEVEL_T
            .labels(alias, sync_level).set(count)
        )

def analyse_indexers(indexers, detailed, alias):
    """Analyse the Indexers"""

    indexer_count = {
        "total": {"total": len(indexers), "enabled": 0, "private": 0, "public": 0},
        "usenet": {"total": 0, "enabled": 0, "private": 0, "public": 0},
        "torrent": {"total": 0, "enabled": 0, "private": 0, "public": 0}
    }

    prowlarr_metrics.VIP_EXPIRATION.clear()
    prowlarr_metrics.INDEXER_STATUS.clear()
    prowlarr_metrics.INDEXER_ENABLED.clear()

    for indexer in indexers:
        enabled = 1 if indexer["enable"] else 0
        indexer_count["total"]["enabled"] += enabled
        indexer_count["total"][indexer["privacy"]] += 1

        indexer_count[indexer["protocol"]]["total"] += 1
        indexer_count[indexer["protocol"]]["enabled"] += enabled
        indexer_count[indexer["protocol"]][indexer["privacy"]] += 1

        name = indexer["name"]

        for field in indexer['fields']:
            if field['name'] == 'vipExpiration':
                vip_expiration = field['value']
                if vip_expiration:
                    vip_expiration = datetime.strptime(vip_expiration, "%Y-%m-%d").timestamp()
                    prowlarr_metrics.VIP_EXPIRATION.labels(alias, name).set(vip_expiration)
                break

        if detailed:
            (prowlarr_metrics.INDEXER_ENABLED
                .labels(alias, indexer["protocol"], name)
                .set(enabled)
            )
            if "status" in indexer:
                status = indexer["status"].get("status", "unknown")
            else:
                status = "unknown"
            prowlarr_metrics.INDEXER_STATUS.labels(alias, name, status).set(1)

    for types, counts in indexer_count.items():
        if types == "total":
            prowlarr_metrics.INDEXER_COUNT_T.labels(alias).set(counts["total"])
            prowlarr_metrics.INDEXER_ENABLED_T.labels(alias).set(counts["enabled"])
            prowlarr_metrics.INDEXER_PRIVACY_T.labels(alias, "private").set(counts["private"])
            prowlarr_metrics.INDEXER_PRIVACY_T.labels(alias, "public").set(counts["public"])
        else:
            prowlarr_metrics.INDEXER_COUNT.labels(alias, types).set(counts["total"])
            prowlarr_metrics.INDEXER_ENABLED.labels(alias, types, "total").set(counts["enabled"])
            prowlarr_metrics.INDEXER_PRIVACY.labels(alias, types, "private").set(counts["private"])
            prowlarr_metrics.INDEXER_PRIVACY.labels(alias, types, "public").set(counts["public"])


def scrape(config):
    """Scrape the Prowlarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    api_version = config.get('api_version', 'v1')
    alias = config.get('alias', 'prowlarr')

    return {
        'indexer': get_indexers(url, api_key, api_version, alias),
        'applications': get_applications(url, api_key, api_version, alias)
    }

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Prowlarr Service"""

    update_system_data(data["system"], alias)
    analyse_indexers(data["data"]['indexer'], detailed, alias)
    analyse_applications(data["data"]['applications'], detailed, alias)
