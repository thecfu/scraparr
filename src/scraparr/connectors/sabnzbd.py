"""Module to handle the Metrics of the SABnzbd Service"""
import threading

import requests

from scraparr.connectors.module import ConnectorModule

_thread_local = threading.local()


def _get_session():
    if not hasattr(_thread_local, 'session'):
        _thread_local.session = requests.Session()
    return _thread_local.session


def _parse_size(size_str):
    """Convert SABnzbd human-readable size string (e.g. '1.5 GB') to bytes."""
    units = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}
    parts = str(size_str).strip().split()
    if len(parts) != 2:
        return 0.0
    try:
        return float(parts[0]) * units.get(parts[1].upper(), 1)
    except (ValueError, KeyError):
        return 0.0


class Module(ConnectorModule):
    """Module Class for SABnzbd"""

    def __init__(self, config):
        ConnectorModule.__init__(self, config, "sabnzbd")

    def get(self, endpoint, **extra_params):
        """Override: SABnzbd uses ?apikey= query param at a single /api endpoint."""
        session = _get_session()
        params = {'output': 'json', 'mode': endpoint, 'apikey': self.api_key}
        params.update(extra_params)
        try:
            r = session.get(f"{self.url}/api", params=params, timeout=20)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 401:
                self.logger.error("Unauthorized: %s", self.url)
            elif r.status_code == 404:
                self.logger.error("Not Found: %s/api?mode=%s", self.url, endpoint)
            else:
                self.logger.debug("Unexpected status %s for mode=%s", r.status_code, endpoint)
        except requests.exceptions.RequestException as e:
            self.logger.debug("Request failed for mode=%s: %s", endpoint, e)
        return {}

    def scrape(self):
        return {}

    def update_metrics(self, data):
        pass

    def clear(self):
        pass
