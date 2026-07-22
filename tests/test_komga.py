"""Tests for the Komga connector."""

from scraparr.const import ACTIVE_CONNECTORS, API_VERSIONS


def test_komga_registered_in_active_connectors():
    assert 'komga' in ACTIVE_CONNECTORS


def test_komga_api_version_is_v1():
    assert API_VERSIONS.get('komga') == 'v1'
