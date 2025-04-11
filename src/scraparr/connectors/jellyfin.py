"""
Module to handle the Metrics of the Whisparr Service
"""
import time

import requests 
import scraparr.metrics.jellyfin as jellyfin_metrics
import logging
from scraparr.metrics.general import UP


def get_header(api_key):
    token = f"Mediabrowser Token={api_key}"
    return {"Authorization": token}


def get_number_of_devices(url, headers_auth, alias):
    """Grab the Indexers from the Jellyfin Endpoint"""
    try:        
        res = requests.get(f"{url}/Devices", headers=headers_auth, timeout=10)  # Adding timeout
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return res.json()['TotalRecordCount']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
   

"""     if res == {}:
        UP.labels(alias, 'prowlarr').set(0)
    else:
        UP.labels(alias, 'prowlarr').set(1)
        jellyfin_metrics.LAST_SCRAPE.labels(alias).set(end_time)
        jellyfin_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time) """

def scrape(config):
    """Scrape the Bazarr Service"""

    url = config.get('url')
    api_key = config.get('api_key')
    alias = config.get('alias', 'bazarr')
    n_devices = get_number_of_devices(url, api_key,alias)
    
#    system = get_system_data(url, api_key, alias)
#    providers = get_providers(url, api_key, alias)
#    data = get_data(url, api_key)
#    wanted = get_wanted(url, api_key)
#
#    if system and providers and data and wanted:
#        return {"data": data, "system": system, "providers": providers, "wanted": wanted}

    logging.info("Passing through Jellyfin Scrape")
    return{"n_devices": n_devices}

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Jellyseerr Service"""
    jellyfin_metrics.JELLYFIN_NUMBER_OF_DEVICES = data["n_devices"]
    print(jellyfin_metrics.JELLYFIN_NUMBER_OF_DEVICES)
    logging.info("Updating Jellyfin metrics")

