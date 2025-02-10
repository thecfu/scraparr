"""
Utility functions for Scraparr API interactions.

This module contains helper functions to avoid duplicate code.
"""

import logging
import requests

def get(api_url, api_key):
    """Get data from API and Logs errors"""
    try:
        r = requests.get(api_url, headers={"X-Api-Key": api_key}, timeout=20)
        if r.status_code == 200:
            return r.json()

        logging.error("Error: %s", r.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Error: %s", e)
    return {}
