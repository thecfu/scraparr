"""
Scraparr Prometheus Exporter

This module collects metrics from various services of the *arr suite
and exposes them in a Prometheus compatible format.

Author: TheGameProfi (maintained and published by TheCfU)
Contributors: TheGameProfi
License: GPL-3.0
"""

import time
import sys
import threading
import configparser
import logging

from wsgiref.simple_server import make_server
from prometheus_client import make_wsgi_app

from scraparr.middleware import Middleware
import scraparr.connectors

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG = configparser.ConfigParser()
CONFIG.read('scraparr/config.cnf')

PATH = CONFIG.get('GENERAL', 'path', fallback="/metrics")
ADDRESS = CONFIG.get('GENERAL', 'address', fallback="0.0.0.0")
PORT = CONFIG.get('GENERAL', 'port', fallback=7100)

USERNAME = CONFIG.get('AUTH', 'username', fallback=None)
PASSWORD = CONFIG.get('AUTH', 'password', fallback=None)
BEARER_TOKEN = CONFIG.get('AUTH', 'token', fallback=None)

metrics_app = make_wsgi_app()
app = Middleware(metrics_app, USERNAME, PASSWORD, BEARER_TOKEN)

ACTIVE_CONNECTORS = ['SONARR', 'RADARR', 'PROWLARR']
BEAUTIFUL_CONNECTORS = ", ".join(ACTIVE_CONNECTORS[:-1]) + " or " + ACTIVE_CONNECTORS[-1]

if __name__ == '__main__':
    if not any(section in CONFIG.sections() for section in ACTIVE_CONNECTORS):
        logging.info("No configuration found for %s", BEAUTIFUL_CONNECTORS)
        sys.exit(1)

    connectors = scraparr.connectors.Connectors()

    for section in CONFIG.sections():
        if section in ACTIVE_CONNECTORS:
            connectors.add_connector(section.lower(), dict(CONFIG.items(section)))

    try:
        def run_server():
            """Starts the WSGI server"""
            httpd = make_server(ADDRESS, PORT, app)
            httpd.serve_forever()

        server_thread = threading.Thread(target=run_server)
        server_thread.start()

        while True:
            logging.info("Scraping...")
            connectors.scrape()
            time.sleep(30)

    except KeyboardInterrupt:
        logging.info("Shutting down")
        sys.exit(0)
