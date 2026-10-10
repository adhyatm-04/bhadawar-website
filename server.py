"""ASGI-compatible request context and local backend entry point."""
import html
import io
import json
from backend.handlers import AuthHandlers, BookingHandlers, CommunityHandlers, OrderHandlers, PaymentHandlers
from backend.runtime import *


class BhadawarRequestContext(AuthHandlers, BookingHandlers, CommunityHandlers, OrderHandlers, PaymentHandlers):
    """Adapts an API request to the existing domain handlers."""
    def __init__(self, path, method, headers, body=b"", client_host="127.0.0.1"):
        self.path = path
        self.command = method.upper()
        self.headers = headers
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.client_address = (client_host or "127.0.0.1", 0)
        self.response_status = 200
        self.response_headers = []

    def send_response(self, status, message=None):
        self.response_status = int(status)

    def send_header(self, name, value):
        self.response_headers.append((str(name), str(value)))

    def end_headers(self):
        defaults = {
            "Content-Security-Policy": "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
            "form-action 'self' https://api.razorpay.com; "
            "script-src 'self' 'unsafe-inline' https://checkout.razorpay.com https://accounts.google.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://accounts.google.com/gsi/style; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; "
            "connect-src 'self' https: https://accounts.google.com; frame-src https://www.google.com https://maps.google.com https://*.razorpay.com https://accounts.google.com",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(self), camera=(), microphone=()",
        }
        existing = {name.lower() for name, _ in self.response_headers}
        for name, value in defaults.items():
            if name.lower() not in existing:
                self.response_headers.append((name, value))

    def send_error(self, status, message=None, explain=None):
        self.send_response(status)
        reason = message or {404: "Not Found", 405: "Method Not Allowed"}.get(int(status), "Request Failed")
        body = f"<!doctype html><title>{html.escape(str(reason))}</title><h1>{html.escape(str(reason))}</h1>".encode("utf-8")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data, status=200, extra_headers=None):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Razorpay-Signature')
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _read_json_body(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len == 0:
            return {}
        body = self.rfile.read(content_len).decode('utf-8')
        try:
            return json.loads(body)
        except Exception:
            return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        decoded_path = path
        for _ in range(3):
            next_path = urllib.parse.unquote(decoded_path)
            if next_path == decoded_path:
                break
            decoded_path = next_path
        decoded_path = decoded_path.replace('\\', '/')

        if PUBLIC_PREVIEW_MODE:
            public_path = decoded_path.lower()
            path_parts = [part for part in public_path.split('/') if part]
            blocked_top_level = {'work', 'outputs', '__pycache__'}
            blocked_extensions = ('.py', '.md', '.db', '.sqlite', '.sqlite3', '.log', '.db-wal', '.db-shm', '.db-journal', '.sqlite-wal', '.sqlite-shm', '.sqlite-journal')
            if (path_parts and path_parts[0] in blocked_top_level) or public_path.endswith(blocked_extensions):
                self.send_error(404)
                return

        # Never expose local secrets or project configuration through static serving.
        if any(part.startswith('.') for part in decoded_path.split('/') if part):
            self.send_error(404)
            return

        # A customer page must not download the corporate price list.
        if path in ('/corporate-menu.js', '/corporate-menu.json') and not (self._staff() or {}).get('role') == 'admin':
            self.send_error(404)
            return

        # API Routes
        if path == '/api/preview-config':
            self._send_json({'success': True, 'public_preview': PUBLIC_PREVIEW_MODE}, extra_headers={'Cache-Control': 'no-store'})
        elif path == '/api/auth/preview-credentials':
            if PUBLIC_PREVIEW_MODE or self.client_address[0] not in ('127.0.0.1', '::1'):
                self.send_error(404)
                return
            role = str(query.get('role', [''])[0]).lower()
            account = DEMO_STAFF.get(role)
            if not account:
                self._send_json({'success': False, 'error': 'Unknown preview role.'}, 400)
                return
            self._send_json({'success': True, 'username': account[0], 'password': account[1]})
        elif path == '/api/auth/me':
            staff = self._staff()
            self._send_json({'success': True, 'staff': staff} if staff else {'success': True, 'staff': None})
        elif path == '/api/customer-auth/me':
            self._send_json({'success': True, 'customer': self._customer()}, extra_headers={'Cache-Control': 'no-store'})
        elif path == '/api/customer-auth/google/config':
            self.handle_customer_google_config()
        elif path == '/api/payment-config':
            self._send_json({'success': True, 'razorpay_enabled': razorpay_enabled(),
                             'key_id': RAZORPAY_KEY_ID if razorpay_enabled() else '',
                             'mode': 'test' if RAZORPAY_KEY_ID.startswith('rzp_test_') else 'live' if razorpay_enabled() else 'unconfigured'})
        elif path == '/api/corporate-menu':
            if not self._require_role('admin', 'corporate'):
                return
            try:
                with open(CORPORATE_MENU_PATH, 'r', encoding='utf-8') as menu_file:
                    self._send_json({'success': True, 'items': json.load(menu_file)})
            except Exception:
                self._send_json({'success': False, 'error': 'Corporate menu is unavailable.'}, 500)
        elif path == '/api/orders':
            self.handle_get_orders(query)
        elif path == '/api/rider/availability':
            self.handle_get_rider_availability()
        elif path == '/api/orders/history':
            self.handle_get_customer_order_history(query)
        elif path == '/api/wallet' and PUBLIC_PREVIEW_MODE:
            self.send_error(404)
        elif path == '/api/bookings':
            self.handle_get_bookings(query)
        elif path == '/api/food-stories':
            self.handle_get_stories(query)
        elif path == '/api/leaderboard':
            self.handle_get_leaderboard(query)
        elif path == '/api/wallet':
            self.handle_get_wallet(query)
        elif path == '/api/reviews':
            self.handle_get_reviews()
        elif path == '/api/stats':
            self.handle_get_stats()
        else:
            if API_ONLY_MODE:
                self.send_error(404)
                return
            # Fallback to static file server
            self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if PUBLIC_PREVIEW_MODE and path in {
            '/api/party-payment/create', '/api/party-payment/verify', '/api/payments/razorpay-webhook'
        }:
            self._send_json({'success': False, 'error': 'This action is disabled during the public demo preview.'}, 403)
            return

        if path in ('/api/customer-auth/register', '/api/customer-auth/login'):
            self._send_json({'success': False, 'error': 'Password access has been replaced by SMS verification.'}, 410)
        elif path == '/api/customer-auth/otp/request':
            self.handle_customer_otp_request()
        elif path == '/api/customer-auth/otp/verify':
            self.handle_customer_otp_verify()
        elif path == '/api/customer-auth/google/start':
            self.handle_customer_google_start()
        elif path == '/api/customer-auth/google/otp/request':
            self.handle_customer_google_otp_request()
        elif path == '/api/customer-auth/google/otp/verify':
            self.handle_customer_google_otp_verify()
        elif path == '/api/customer-auth/email-otp/request':
            self.handle_customer_email_otp_request()
        elif path == '/api/customer-auth/email-otp/verify':
            self.handle_customer_email_otp_verify()
        elif path == '/api/customer-auth/email-login/request':
            self.handle_customer_email_login_request()
        elif path == '/api/customer-auth/email-login/verify':
            self.handle_customer_email_login_verify()
        elif path == '/api/customer-auth/profile':
            self.handle_customer_profile()
        elif path == '/api/customer-auth/logout':
            self.handle_customer_logout()
        elif path == '/api/auth/login':
            self.handle_staff_login()
        elif path == '/api/corporate-auth/login':
            self.handle_corporate_login()
        elif path == '/api/auth/logout':
            self.handle_staff_logout()
        elif path == '/api/orders':
            self.handle_create_order()
        elif path == '/api/orders/track':
            self.handle_track_order()
        elif path == '/api/bookings':
            self.handle_create_booking()
        elif path == '/api/party-payment/create':
            self.handle_create_party_payment()
        elif path == '/api/party-payment/verify':
            self.handle_verify_party_payment()
        elif path == '/api/payments/razorpay-webhook':
            self.handle_razorpay_webhook()
        elif path == '/api/bookings/settle':
            self.handle_settle_booking()
        elif path == '/api/corporate-orders':
            self.handle_create_corporate_order()
        elif path == '/api/orders/status':
            self.handle_update_order_status()
        elif path == '/api/orders/cod-status':
            self.handle_update_cod_status()
        elif path == '/api/orders/rider-note':
            self.handle_update_rider_feedback()
        elif path == '/api/orders/issue':
            self.handle_update_order_issue()
        elif path == '/api/rider/availability':
            self.handle_update_rider_availability()
        elif path == '/api/food-stories':
            self.handle_create_story()
        elif path == '/api/food-stories/approve':
            self.handle_approve_story()
        elif path == '/api/food-stories/reject':
            self.handle_reject_story()
        elif path == '/api/food-stories/like':
            self.handle_like_story()
        elif path == '/api/orders/complete':
            self.handle_complete_order()
        elif path == '/api/reviews':
            self.handle_create_review()
        else:
            self._send_json({"error": "Endpoint not found"}, 404)


def run_server():
    import uvicorn
    uvicorn.run("backend.app:app", host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    run_server()
