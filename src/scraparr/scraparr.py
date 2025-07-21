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
from scraparr.parser import parse_env_config

from scraparr.const import ACTIVE_CONNECTORS, BEAUTIFUL_CONNECTORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE_LOCATION = "/scraparr/config/config.yaml"

try:
    with open(CONFIG_FILE_LOCATION, 'r', encoding='utf-8') as yaml_file:
        CONFIG = yaml.safe_load(yaml_file)
except FileNotFoundError:
    logging.error(
    	"Configuration file not found: %s, will try to load from environment variables",
    	CONFIG_FILE_LOCATION
    )

    CONFIG = parse_env_config()

    if not CONFIG:
        logging.error("No configuration found in environment variables.")
        sys.exit(1)
except PermissionError:
    logging.error("Permission denied to read the configuration file: %s", CONFIG_FILE_LOCATION)
    sys.exit(1)
except yaml.YAMLError as exc:
    logging.error("Error parsing YAML file: %s", exc)
    sys.exit(1)

PATH = CONFIG.get('GENERAL', {}).get('path', "/metrics") # type: ignore
ADDRESS = CONFIG.get('GENERAL', {}).get('address', "0.0.0.0") # type: ignore
PORT = CONFIG.get('GENERAL', {}).get('port', 7100) # type: ignore

USERNAME = CONFIG.get('AUTH', {}).get('username', None) # type: ignore
PASSWORD = CONFIG.get('AUTH', {}).get('password', None) # type: ignore
BEARER_TOKEN = CONFIG.get('AUTH', {}).get('token', None) # type: ignore

metrics_app = make_wsgi_app()
app = Middleware(metrics_app, USERNAME, PASSWORD, BEARER_TOKEN)

RUNNING = True

def main():
    """Main function to start the Scraparr Prometheus Exporter"""
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
        httpd = make_server(ADDRESS, PORT, app) # type: ignore
        while RUNNING:
            httpd.handle_request()
        logging.info("Metrics Endpoint Stopped")

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    connectors.scrape()
    RUNNING = False


if __name__ == '__main__':
    main()
