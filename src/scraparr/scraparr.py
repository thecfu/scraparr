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
from dotenv import load_dotenv
from prometheus_client import make_wsgi_app

from scraparr.connectors import util
from scraparr.middleware import Middleware
import scraparr.connectors
from scraparr.parser import parse_env_config
from scraparr.config_loader import (
    load_yaml_config_safe, deep_merge, coerce_config_types, MissingEnvVarError
)

from scraparr.const import ACTIVE_CONNECTORS, BEAUTIFUL_CONNECTORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load .env file into os.environ (if present) before parsing config
# This allows ${VAR} in YAML to reference .env values
load_dotenv()

CONFIG_FILE_LOCATION = "/scraparr/config/config.yaml"

config_file = None

try:
    yaml_config = load_yaml_config_safe(CONFIG_FILE_LOCATION)
    env_config = parse_env_config()
    # Merge: YAML (base) <- environment variables (includes .env values)
    config_file = coerce_config_types(deep_merge(yaml_config, env_config))
except PermissionError:
    logging.error("Permission denied to read the configuration file: %s", CONFIG_FILE_LOCATION)
    sys.exit(1)
except yaml.YAMLError as exc:
    logging.error("Error parsing YAML file: %s", exc)
    sys.exit(1)
except MissingEnvVarError as exc:
    logging.error("Missing required environment variable in config: %s", exc)
    sys.exit(1)
except ValueError as exc:
    logging.error("Invalid config value: %s", exc)
    sys.exit(1)

if not config_file:
    logging.error("Configuration is empty. Please provide a valid configuration.")
    sys.exit(1)

GENERAL = config_file.get('general', {})
PATH = GENERAL.get('path', "/metrics")
ADDRESS = GENERAL.get('address', "0.0.0.0")
PORT = int(GENERAL.get('port', 7100))
WORKERS = GENERAL.get('workers', 5)

AUTH = config_file.get('auth', {})
USERNAME = AUTH.get('username', None)
PASSWORD = AUTH.get('password', None)
BEARER_TOKEN = AUTH.get('token', None)

metrics_app = make_wsgi_app()
app = Middleware(metrics_app, USERNAME, PASSWORD, BEARER_TOKEN)

def main():
    """Main function to start the Scraparr Prometheus Exporter"""
    if not any(section in config_file for section in ACTIVE_CONNECTORS):
        logging.error("No configuration found for %s", BEAUTIFUL_CONNECTORS)
        sys.exit(1)

    util.log_level = GENERAL.get('log_level', 'INFO').upper()

    connectors = scraparr.connectors.Connectors(WORKERS)

    for service in config_file:
        if service in ACTIVE_CONNECTORS:
            if isinstance(config_file[service], dict):
                config = [config_file[service]]
            else:
                config = config_file[service]
            connectors.add_connector(service, config)

    httpd = make_server(ADDRESS, PORT, app)

    def run_server():
        """Starts the WSGI server"""
        httpd.serve_forever()
        logging.info("Metrics Endpoint Stopped")

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    connectors.scrape()
    httpd.shutdown()


if __name__ == '__main__':
    main()
