"""Tests for exclude filtering feature (issue #161)."""

import pytest


class FakeConnector:
    """Minimal stub to test ConnectorModule.__init__ exclude parsing."""

    def __init__(self, config):
        from scraparr.connectors.module import ConnectorModule
        # Call ConnectorModule.__init__ directly
        ConnectorModule.__init__(self, config, "test_service")


def test_exclude_parsed_as_set():
    config = {
        "url": "http://localhost",
        "api_key": "key",
        "exclude": ["/data/test", "/mnt/archive"],
    }
    connector = FakeConnector(config)
    assert connector.exclude == {"/data/test", "/mnt/archive"}


def test_exclude_defaults_to_empty_set():
    config = {"url": "http://localhost", "api_key": "key"}
    connector = FakeConnector(config)
    assert connector.exclude == set()


def test_exclude_in_service_fields():
    from scraparr.const import SERVICE_FIELDS
    assert "exclude" in SERVICE_FIELDS
