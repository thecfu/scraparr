"""Tests for the IPv4/IPv6 aware WSGI server helpers"""

import socket
import threading
from urllib.request import urlopen
from wsgiref.simple_server import WSGIRequestHandler

import pytest

from scraparr.server import resolve_bind_address, make_wsgi_server


def _has_ipv6():
    """Check whether the host can actually bind an IPv6 socket"""
    if not socket.has_ipv6:
        return False
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
            sock.bind(('::1', 0))
        return True
    except OSError:
        return False


@pytest.mark.parametrize("address,expected_family,expected_host", [
    ("0.0.0.0", socket.AF_INET, "0.0.0.0"),
    ("127.0.0.1", socket.AF_INET, "127.0.0.1"),
    ("::", socket.AF_INET6, "::"),
    ("::1", socket.AF_INET6, "::1"),
    ("[::1]", socket.AF_INET6, "::1"),
    ("  ::1  ", socket.AF_INET6, "::1"),
])
def test_resolve_bind_address(address, expected_family, expected_host):
    """Literal addresses resolve to the matching address family"""
    assert resolve_bind_address(address, 7100) == (expected_family, expected_host)


def test_resolve_bind_address_unresolvable_falls_back_to_ipv4():
    """An unresolvable address keeps the previous AF_INET behaviour"""
    family, host = resolve_bind_address("this-host-does-not-exist.invalid", 7100)
    assert family == socket.AF_INET
    assert host == "this-host-does-not-exist.invalid"


@pytest.mark.parametrize("address", [None, ""])
def test_resolve_bind_address_empty(address):
    """An empty address binds to all interfaces"""
    family, host = resolve_bind_address(address, 7100)
    assert family in (socket.AF_INET, socket.AF_INET6)
    assert host in ("0.0.0.0", "::")


def _serve(address, expected_family):
    """Start a server on a random port and return the body it serves"""

    def app(_environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'ok']

    httpd = make_wsgi_server(address, 0, app, WSGIRequestHandler)
    assert httpd.socket.family == expected_family

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        host = f"[{address}]" if expected_family == socket.AF_INET6 else address
        with urlopen(f"http://{host}:{port}/", timeout=5) as response:
            return response.read()
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
        httpd.server_close()


def test_make_wsgi_server_ipv4():
    """The server still serves over IPv4"""
    assert _serve("127.0.0.1", socket.AF_INET) == b'ok'


@pytest.mark.skipif(not _has_ipv6(), reason="No IPv6 support on this host")
def test_make_wsgi_server_ipv6():
    """The server serves over IPv6 (issue #215)"""
    assert _serve("::1", socket.AF_INET6) == b'ok'
