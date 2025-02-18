"""
This is the Middleware module for the WSGI application.
"""

import base64
from werkzeug.wrappers import Request

class Middleware:
    """WSGI Middleware to only allow /metrics path with authentication"""
    def __init__(self, app, username=None, password=None, api_token=None):
        self.app = app
        self.username = username
        self.password = password
        self.api_token = api_token

    def __call__(self, environ, start_response):
        request = Request(environ)

        # Only allow access to /metrics
        if request.path != "/metrics":
            return self.show_html_page(start_response)

        # Check authentication
        if (self.username and self.password) or self.api_token:
            if not self.is_authenticated(request):
                return self.show_unauthorized_response(start_response)

        return self.app(environ, start_response)

    def is_authenticated(self, request):
        """Checks if the request is authenticated using either Basic Auth or API Token"""
        # Check for Basic Authentication
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Basic "):
            encoded_credentials = auth_header.split(" ", 1)[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
            if username == self.username and password == self.password:
                return True

        # Check for API Token in the Authorization header
        if auth_header and auth_header == f"Bearer {self.api_token}":
            return True

        # If no valid authentication is found
        return False

    @staticmethod
    def show_html_page(start_response):
        """Returns a simple HTML page for non-/metrics paths"""
        html_content = b"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scraparr Exporter</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: grey; }
                h1 { color: #333; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <h1>Scraparr Exporter</h1>
            <p><a href="/metrics">Metrics</a></p>
        </body>
        </html>
        """
        start_response("200 OK", [("Content-Type", "text/html")])
        return [html_content]

    @staticmethod
    def show_unauthorized_response(start_response):
        """Returns a 401 Unauthorized response"""
        start_response(
            "401 Unauthorized",
            [
                ("Content-Type", "text/plain"),
                ("WWW-Authenticate", 'Basic realm="Login Required"')
            ]
        )
        return [b"Unauthorized access. Please provide valid credentials."]
