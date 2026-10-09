"""Shared Vercel proxy handler for the durable Bhadawar API service."""
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import os


class handler(BaseHTTPRequestHandler):
    def _proxy(self):
        origin = os.environ.get('BHADAWAR_API_ORIGIN', '').strip().rstrip('/')
        if not origin:
            self._json_error(503, 'Production API is not configured yet.')
            return

        parsed = urlsplit(origin)
        if (parsed.scheme not in ('https', 'http') or not parsed.netloc
                or parsed.username or parsed.password or parsed.path not in ('', '/')
                or parsed.query or parsed.fragment):
            self._json_error(500, 'Production API origin is invalid.')
            return
        if parsed.scheme != 'https' and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
            self._json_error(500, 'Production API origin must use HTTPS.')
            return
        if parsed.netloc.casefold() == str(self.headers.get('Host', '')).casefold():
            self._json_error(500, 'Production API cannot point back to this Vercel deployment.')
            return

        body = None
        if self.command in ('POST', 'PUT', 'PATCH', 'DELETE'):
            try:
                length = int(self.headers.get('Content-Length', '0') or 0)
            except ValueError:
                self._json_error(400, 'Invalid request body length.')
                return
            if length > 5 * 1024 * 1024:
                self._json_error(413, 'Request body is too large.')
                return
            body = self.rfile.read(length) if length else b''

        headers = {}
        for name in ('Accept', 'Content-Type', 'Cookie', 'X-Razorpay-Signature', 'User-Agent', 'Origin'):
            value = self.headers.get(name)
            if value:
                headers[name] = value
        if self.headers.get('X-Forwarded-Proto', '').lower() == 'https':
            headers['X-Forwarded-Proto'] = 'https'

        try:
            upstream_request = Request(origin + self.path, data=body, headers=headers, method=self.command)
            try:
                upstream = urlopen(upstream_request, timeout=25)
                status = upstream.status
            except HTTPError as error:
                upstream = error
                status = error.code
            response_body = upstream.read()
            response_headers = upstream.headers
        except (URLError, TimeoutError, OSError):
            self._json_error(502, 'The production backend could not be reached.')
            return

        self.send_response(status)
        for name in ('Content-Type', 'Cache-Control', 'Expires', 'Pragma', 'Vary'):
            value = response_headers.get(name)
            if value:
                self.send_header(name, value)
        for cookie in response_headers.get_all('Set-Cookie', []):
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def _json_error(self, status, message):
        import json
        body = json.dumps({'success': False, 'error': message}).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_PATCH(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_OPTIONS(self):
        self._proxy()

    def do_HEAD(self):
        self._proxy()
