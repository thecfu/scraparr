"""Module for General Metrics"""
from prometheus_client import Gauge

UP = Gauge('scraparr_services_up', 'If the scrape of the Service was successful', ['alias', 'scraparr_services'])
