"""
Scraparr Prometheus Exporter

This module collects metrics from various services of the *arr suite
and exposes them in a Prometheus compatible format.

Author: TheGameProfi (maintained and published by TheCfU)
Contributors: TheGameProfi
License: GPL-3.0
"""

import sys
import threading
import logging
from wsgiref.simple_server import make_server

import yaml
from prometheus_client import make_wsgi_app

from scraparr.middleware import Middleware
import scraparr.connectors

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    with open('/scraparr/config/config.yaml', 'r', encoding='utf-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file)
except FileNotFoundError:
    logging.error("Configuration file not found: /scraparr/config/config.yaml,"
                  " pls check the path or convert your .cnf to .yaml")
    sys.exit(1)
except yaml.YAMLError as exc:
    logging.error("Error parsing YAML file: %s", exc)
    sys.exit(1)

PATH = CONFIG.get('GENERAL', {}).get('path', "/metrics")
ADDRESS = CONFIG.get('GENERAL', {}).get('address', "0.0.0.0")
PORT = CONFIG.get('GENERAL', {}).get('port', 7100)

USERNAME = CONFIG.get('AUTH', {}).get('username', None)
PASSWORD = CONFIG.get('AUTH', {}).get('password', None)
BEARER_TOKEN = CONFIG.get('AUTH', {}).get('token', None)

metrics_app = make_wsgi_app()
app = Middleware(metrics_app, USERNAME, PASSWORD, BEARER_TOKEN)

ACTIVE_CONNECTORS = [
    'sonarr',
    'radarr',
    'prowlarr',
    'bazarr',
    'readarr',
    'jellyseerr',
    'overseerr',
    'whisparr',
    'jellyfin'
]
BEAUTIFUL_CONNECTORS = ", ".join(ACTIVE_CONNECTORS[:-1]) + " or " + ACTIVE_CONNECTORS[-1]

RUNNING = True

if __name__ == '__main__':
    if not any(section in CONFIG for section in ACTIVE_CONNECTORS):
        logging.info("No configuration found for %s", BEAUTIFUL_CONNECTORS)
        sys.exit(1)

    connectors = scraparr.connectors.Connectors()

    for service in CONFIG:
        if service in ACTIVE_CONNECTORS:
            if isinstance(CONFIG[service], dict):
                config = [CONFIG[service]]
            else:
                config = CONFIG[service]
            connectors.add_connector(service, config)

    def run_server():
        """Starts the WSGI server"""
        httpd = make_server(ADDRESS, PORT, app)
        while RUNNING:
            httpd.handle_request()
        logging.info("Metrics Endpoint Stopped")

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    connectors.scrape()
    RUNNING = False
