"""Module for General Metrics"""
from prometheus_client import Gauge

UP = Gauge('up', 'If the scrape of the Service was successful', ['service'])
