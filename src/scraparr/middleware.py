"""
This is the Middleware module for the WSGI application.
"""

from werkzeug.wrappers import Request

class Middleware:
    """WSGI Middleware to only allow /metrics path"""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)

        # Only allow /metrics
        if request.path != "/metrics":
            return self.show_html_page(start_response)

        return self.app(environ, start_response)

    def show_html_page(self, start_response):
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
