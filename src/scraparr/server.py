"""
WSGI server helpers for Scraparr

Wraps :func:`wsgiref.simple_server.make_server` so that the configured
``general.address`` may be an IPv6 address. ``wsgiref`` hardcodes the
``AF_INET`` address family, so the family has to be resolved from the
address before the server class is built.
"""

import socket
from wsgiref.simple_server import make_server, WSGIServer


def resolve_bind_address(address, port):
    """
    Resolve the address to bind to into an ``(address_family, host)`` tuple.

    Accepts IPv4 addresses, IPv6 addresses (with or without the surrounding
    brackets used in URLs) and hostnames. Falls back to ``AF_INET`` when the
    address cannot be resolved so that the caller keeps the previous behaviour.
    """

    host = address.strip() if address else ""
    if host.startswith('[') and host.endswith(']'):
        host = host[1:-1]

    try:
        infos = socket.getaddrinfo(
            host or None, port,
            type=socket.SOCK_STREAM,
            flags=socket.AI_PASSIVE
        )
    except socket.gaierror:
        return socket.AF_INET, host

    for family, _, _, _, sockaddr in infos:
        if family in (socket.AF_INET, socket.AF_INET6):
            return family, sockaddr[0]

    return socket.AF_INET, host


def make_wsgi_server(address, port, app, handler_class):
    """Create a WSGI server bound to ``address``, supporting IPv4 and IPv6"""

    family, host = resolve_bind_address(address, port)

    class Server(WSGIServer):
        """WSGIServer using the address family resolved from the config"""
        address_family = family

    return make_server(host, port, app, server_class=Server, handler_class=handler_class)
