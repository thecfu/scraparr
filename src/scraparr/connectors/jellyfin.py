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
   



def getGenres(url, headers_auth, alias):
    try:
        
        res = requests.get(f"{url}/Genres", headers=headers_auth, timeout=10)  # Adding timeout
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = res.json()
        genre_names = [item["Name"] for item in data.get("Items", [])]
                
        return genre_names
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")    
        
        
def get_number_of_user(url, headers_auth, alias):
    """Grab the Indexers from the Jellyfin Endpoint"""
    try:
        
        res = requests.get(f"{url}/Users", headers=headers_auth, timeout=10)  # Adding timeout
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        #print(res.json())  # or res.text if it's not JSON
        data = res.json()
       
        return len(data)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
   
def get_number_of_movies(url, headers_auth, alias):
    """Grab the Indexers from the Jellyfin Endpoint"""
    try:
        
        res = requests.get(f"{url}/Items?SortBy=SortName%2CProductionYear&SortOrder=Ascending&IncludeItemTypes=Movie&Recursive=true", headers=headers_auth, timeout=10)  # Adding timeout
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
       
        return res.json()['TotalRecordCount']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
   
def get_number_of_series(url, headers_auth, alias):
    """Grab the Indexers from the Jellyfin Endpoint"""
    try:
        
        res = requests.get(f"{url}/Items?SortBy=SortName%2CProductionYear&SortOrder=Ascending&IncludeItemTypes=Series&Recursive=true", headers=headers_auth, timeout=10)  # Adding timeout
        res.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
       
        return res.json()['TotalRecordCount']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
   
   
def scrape(config):
    initial_time = time.time()
    """Scrape the Bazarr Service"""
    url = config.get('url')
    api_key = config.get('api_key')
    alias = config.get('alias', 'bazarr')
    
    headers_auth=get_header(api_key)
    
    n_devices = get_number_of_devices(url, headers_auth,alias)
    n_user = get_number_of_user(url, headers_auth,alias)
    n_movies = get_number_of_movies(url, headers_auth,alias)
    n_series = get_number_of_series(url, headers_auth,alias)

    end_time = time.time()
    jellyfin_metrics.LAST_SCRAPE.labels(alias).set(end_time)
    jellyfin_metrics.SCRAPE_DURATION.labels(alias).set(end_time - initial_time)
    

    logging.info("Passing through Jellyfin Scrape")
    return{"n_devices": n_devices, "n_user": n_user, "n_movies": n_movies, "n_series": n_series}

def update_metrics(data, detailed, alias):
    """Update the Metrics for the Jellyseerr Service"""
    jellyfin_metrics.JELLYFIN_NUMBER_OF_DEVICES = data["n_devices"]
    jellyfin_metrics.JELLYFIN_NUMBER_OF_USERS = data["n_devices"]
    jellyfin_metrics.JELLYFIN_NUMBER_OF_MOVIES = data["n_movies"]
    jellyfin_metrics.JELLYFIN_NUMBER_OF_SERIES = data["n_series"]

    logging.info("Updating Jellyfin metrics")

