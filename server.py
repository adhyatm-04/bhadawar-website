"""
Bhadawar Hotel & Foods - Complete Full-Featured Backend Server
Handles static file serving + REST APIs for Orders, Bookings, Food Stories, Leaderboard, Wallet, Reviews.
"""
import http.server
import socketserver
import os
import json
import sqlite3
import urllib.parse
import urllib.request
import urllib.error
import uuid
import base64
import hashlib
import hmac
import secrets
import math
import re
import time
from pathlib import Path
from email.parser import BytesParser
from email.policy import default as email_policy
from datetime import datetime
from order_pricing import checkout_totals, distance_km, load_menu_catalog

PORT = int(os.environ.get('PORT', '4175'))
HOST = os.environ.get('HOST', '127.0.0.1')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('BHADAWAR_DB_PATH', os.path.join(BASE_DIR, 'bhadawar.db'))
CORPORATE_MENU_PATH = os.path.join(BASE_DIR, 'corporate-menu.json')

def load_local_env():
    """Load simple KEY=value settings from the private local .env file."""
    env_path = Path(BASE_DIR) / '.env'
    try:
        lines = env_path.read_text(encoding='utf-8').splitlines()
    except FileNotFoundError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        name, value = line.split('=', 1)
        name, value = name.strip(), value.strip()
        if not name or name in os.environ:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        os.environ[name] = value

load_local_env()

PUBLIC_PREVIEW_MODE = os.environ.get('BHADAWAR_PUBLIC_PREVIEW', '').lower() == 'true'
ORDER_TAX_PERCENT = float(os.environ.get('BHADAWAR_TAX_PERCENT', '5'))
DELIVERY_FEE_UNDER_5 = int(os.environ.get('BHADAWAR_DELIVERY_FEE_UNDER_5', '35'))
DELIVERY_FEE_5_TO_10 = int(os.environ.get('BHADAWAR_DELIVERY_FEE_5_TO_10', '50'))
MAX_WALLET_REDEEM_PERCENT = max(0, min(100, int(os.environ.get('BHADAWAR_MAX_REDEEM_PERCENT', '50'))))

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '').strip()
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '').strip()
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '').strip()
RAZORPAY_ALLOW_LIVE = os.environ.get('BHADAWAR_ENABLE_LIVE_PAYMENTS', '').lower() == 'true'
MSG91_AUTH_KEY = os.environ.get('MSG91_AUTH_KEY', '').strip()
MSG91_OTP_TEMPLATE_ID = os.environ.get('MSG91_OTP_TEMPLATE_ID', '').strip()
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '').strip()
RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', '').strip()
API_ONLY_MODE = os.environ.get('BHADAWAR_API_ONLY', '').lower() == 'true'
DEMO_STAFF = {
    'admin': (os.environ.get('BHADAWAR_ADMIN_USER', 'admin'), os.environ.get('BHADAWAR_ADMIN_PASSWORD', 'BhadawarAdminDemo!')),
    'kitchen': (os.environ.get('BHADAWAR_KITCHEN_USER', 'kitchen'), os.environ.get('BHADAWAR_KITCHEN_PASSWORD', 'BhadawarKitchenDemo!')),
    'delivery': (os.environ.get('BHADAWAR_DELIVERY_USER', 'delivery'), os.environ.get('BHADAWAR_DELIVERY_PASSWORD', 'BhadawarDeliveryDemo!')),
}
DELIVERY_STAFF = {DEMO_STAFF['delivery'][0]: DEMO_STAFF['delivery'][1]}
for _rider_credential in os.environ.get('BHADAWAR_RIDER_CREDENTIALS', '').split(';'):
    if '=' in _rider_credential:
        _rider_username, _rider_password = _rider_credential.split('=', 1)
        if _rider_username.strip() and _rider_password:
            DELIVERY_STAFF[_rider_username.strip()] = _rider_password
CORPORATE_COMPANY = os.environ.get('BHADAWAR_CORPORATE_COMPANY', 'Bhadawar Demo Company').strip()
CORPORATE_STAFF_IDS = {
    staff_id.strip().casefold()
    for staff_id in os.environ.get('BHADAWAR_CORPORATE_STAFF_IDS', 'CORP-1001').split(',')
    if staff_id.strip()
}
STAFF_SESSIONS = {}
SESSION_MAX_AGE = 8 * 60 * 60
CUSTOMER_SESSIONS = {}
CUSTOMER_SESSION_MAX_AGE = 30 * 24 * 60 * 60
CUSTOMER_OTP_SENDS = {}
CUSTOMER_OTP_VERIFIES = {}
CUSTOMER_EMAIL_OTP_SENDS = {}
CUSTOMER_EMAIL_OTP_VERIFIES = {}
CUSTOMER_EMAIL_OTP_CHALLENGES = {}
CUSTOMER_EMAIL_LOGIN_CHALLENGES = {}

def party_deposit_for_guests(guests):
    return int(guests) * (30 if int(guests) >= 12 else 50)

def razorpay_enabled():
    return bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and
                (RAZORPAY_KEY_ID.startswith('rzp_test_') or RAZORPAY_ALLOW_LIVE))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _migrate_db(conn)
    return conn

def _migrate_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS customer_accounts (
        phone TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL DEFAULT '',
        password_salt TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        phone_verified_at TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    customer_columns = {row[1] for row in conn.execute("PRAGMA table_info(customer_accounts)")}
    if 'phone_verified_at' not in customer_columns:
        conn.execute('ALTER TABLE customer_accounts ADD COLUMN phone_verified_at TEXT')
    if 'email_verified_at' not in customer_columns:
        conn.execute('ALTER TABLE customer_accounts ADD COLUMN email_verified_at TEXT')
    story_columns = {row[1] for row in conn.execute("PRAGMA table_info(food_stories)")}
    for name, declaration in (
        ('order_id', 'TEXT'),
        ('story_rewarded', 'INTEGER NOT NULL DEFAULT 0'),
        ('bonus_rewarded', 'INTEGER NOT NULL DEFAULT 0'),
    ):
        if name not in story_columns:
            conn.execute(f'ALTER TABLE food_stories ADD COLUMN {name} {declaration}')
    conn.execute("UPDATE food_stories SET story_rewarded = 1 WHERE status = 'approved' AND story_rewarded = 0")
    conn.execute("UPDATE food_stories SET pts = 1, order_above_599 = 0 WHERE order_id IS NULL AND bonus_rewarded = 0")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_food_stories_order_id ON food_stories(order_id) WHERE order_id IS NOT NULL")
    booking_columns = {row[1] for row in conn.execute("PRAGMA table_info(bookings)")}
    for name, declaration in (
        ('deposit_amount', 'REAL NOT NULL DEFAULT 0'),
        ('payment_status', "TEXT NOT NULL DEFAULT 'not_required'"),
        ('razorpay_order_id', 'TEXT'),
        ('razorpay_payment_id', 'TEXT'),
        ('final_bill', 'REAL'),
        ('balance_due', 'REAL'),
        ('refund_due', 'REAL'),
        ('settled_at', 'TEXT'),
    ):
        if name not in booking_columns:
            conn.execute(f'ALTER TABLE bookings ADD COLUMN {name} {declaration}')
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_razorpay_order ON bookings(razorpay_order_id) WHERE razorpay_order_id IS NOT NULL")
    order_columns = {row[1] for row in conn.execute("PRAGMA table_info(orders)")}
    for name, declaration in (
        ('delivery_latitude', 'REAL'),
        ('delivery_longitude', 'REAL'),
        ('cod_status', "TEXT NOT NULL DEFAULT 'not_applicable'"),
        ('cod_collected_via', 'TEXT'),
        ('cod_collected_amount', 'REAL NOT NULL DEFAULT 0'),
        ('delivery_instructions', 'TEXT'),
        ('rider_feedback', 'TEXT'),
        ('issue_note', 'TEXT'),
        ('delivery_rider', 'TEXT'),
    ):
        if name not in order_columns:
            conn.execute(f'ALTER TABLE orders ADD COLUMN {name} {declaration}')
    conn.execute("UPDATE orders SET status = 'picked_up' WHERE order_type = 'delivery' AND status = 'out_for_delivery'")
    conn.execute("UPDATE orders SET cod_status = 'pending' WHERE lower(payment_method) IN ('cod', 'cash on delivery') AND status NOT IN ('delivered', 'cancelled') AND cod_status = 'not_applicable'")
    conn.execute("UPDATE orders SET cod_status = 'not_confirmed' WHERE lower(payment_method) IN ('cod', 'cash on delivery') AND status = 'delivered' AND cod_status = 'not_applicable'")
    conn.execute("""CREATE TABLE IF NOT EXISTS delivery_riders (
        username TEXT PRIMARY KEY,
        is_available INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()

def _normal_phone(value):
    return ''.join(char for char in str(value or '') if char.isdigit())[-10:]

def _canonical_indian_phone(value):
    raw = ''.join(char for char in str(value or '') if char.isdigit())
    if len(raw) == 12 and raw.startswith('91'):
        digits = raw[2:]
    elif len(raw) == 10:
        digits = raw
    else:
        return None
    return f'+91 {digits[:5]} {digits[5:]}'

def _otp_rate_limit(bucket, key, limit, window_seconds, cooldown_seconds=0):
    now = time.time()
    recent = [stamp for stamp in bucket.get(key, []) if now - stamp < window_seconds]
    if cooldown_seconds and recent and now - recent[-1] < cooldown_seconds:
        retry = int(cooldown_seconds - (now - recent[-1])) + 1
        bucket[key] = recent
        return retry
    if len(recent) >= limit:
        retry = int(window_seconds - (now - recent[0])) + 1
        bucket[key] = recent
        return max(1, retry)
    recent.append(now)
    bucket[key] = recent
    if len(bucket) > 20000:
        for old_key in list(bucket):
            if not bucket[old_key] or now - bucket[old_key][-1] >= window_seconds:
                bucket.pop(old_key, None)
    return 0

def _msg91_call(method, endpoint, body=None):
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body or {}).encode('utf-8') if method == 'POST' else None,
        headers={
            'authkey': MSG91_AUTH_KEY,
            'accept': 'application/json',
            'content-type': 'application/json',
        },
        method=method,
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        raw = response.read(64 * 1024).decode('utf-8', errors='replace')
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        raise RuntimeError('The SMS provider returned an unreadable response.')

def _resend_send_otp(email, code):
    safe_code = re.sub(r'[^0-9]', '', code)
    body = {
        'from': RESEND_FROM_EMAIL,
        'to': [email],
        'subject': 'Your Bhadawar email verification code',
        'html': '<div style="font-family:Arial,sans-serif;color:#2a1b18;max-width:520px;margin:auto;padding:24px">'
                '<p style="color:#b51f2e;font-weight:700;letter-spacing:2px">BHADAWAR HOTEL &amp; FOODS</p>'
                '<h1 style="font-size:24px">Verify your email</h1>'
                f'<p>Your one-time verification code is <strong style="font-size:28px;letter-spacing:5px">{safe_code}</strong>.</p>'
                '<p>This code expires in 10 minutes. If you did not request it, you can ignore this email.</p></div>',
        'text': f'Your Bhadawar email verification code is {safe_code}. It expires in 10 minutes. If you did not request it, ignore this email.'
    }
    request = urllib.request.Request(
        'https://api.resend.com/emails',
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        raw = response.read(64 * 1024).decode('utf-8', errors='replace')
    try:
        result = json.loads(raw)
    except (ValueError, TypeError):
        raise RuntimeError('The email provider returned an unreadable response.')
    if not result.get('id'):
        raise RuntimeError('The email provider did not confirm sending.')
    return result

class BhadawarBackendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header(
            'Content-Security-Policy',
            "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
            "form-action 'self' https://api.razorpay.com; "
            "script-src 'self' 'unsafe-inline' https://checkout.razorpay.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; "
            "connect-src 'self' https:; frame-src https://www.google.com https://maps.google.com https://*.razorpay.com"
        )
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Permissions-Policy', 'geolocation=(self), camera=(), microphone=()')
        super().end_headers()

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

    def _staff(self):
        cookie = self.headers.get('Cookie', '')
        token = ''
        for part in cookie.split(';'):
            name, _, value = part.strip().partition('=')
            if name == 'bhadawar_staff':
                token = value
                break
        session = STAFF_SESSIONS.get(token)
        if not session:
            return None
        if session['expires'] <= datetime.utcnow().timestamp():
            STAFF_SESSIONS.pop(token, None)
            return None
        staff = {'role': session['role'], 'username': session['username']}
        if session.get('company'):
            staff['company'] = session['company']
        return staff

    def _customer(self):
        token = ''
        for part in self.headers.get('Cookie', '').split(';'):
            name, _, value = part.strip().partition('=')
            if name == 'bhadawar_customer':
                token = value
                break
        session = CUSTOMER_SESSIONS.get(token)
        if not session:
            return None
        if session['expires'] <= datetime.utcnow().timestamp():
            CUSTOMER_SESSIONS.pop(token, None)
            return None
        conn = get_db()
        row = conn.execute('SELECT phone, name, email, phone_verified_at, email_verified_at FROM customer_accounts WHERE phone = ?', (session['phone'],)).fetchone()
        conn.close()
        if not row:
            CUSTOMER_SESSIONS.pop(token, None)
            return None
        return dict(row)

    def _customer_cookie(self, token, max_age):
        secure = self.headers.get('X-Forwarded-Proto', '').lower() == 'https'
        origin = urllib.parse.urlparse(self.headers.get('Origin', ''))
        secure = secure or origin.scheme == 'https'
        suffix = '; Secure' if secure else ''
        return f'bhadawar_customer={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={max_age}{suffix}'

    def _require_role(self, *roles):
        staff = self._staff()
        if not staff:
            self._send_json({'success': False, 'error': 'Staff sign-in required.'}, 401)
            return None
        if roles and staff['role'] not in roles:
            self._send_json({'success': False, 'error': 'Your staff role cannot access this action.'}, 403)
            return None
        return staff

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
            super().do_GET()

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

    # ==========================================
    # API HANDLERS
    # ==========================================

    def _start_customer_session(self, phone):
        token = secrets.token_urlsafe(32)
        CUSTOMER_SESSIONS[token] = {
            'phone': phone,
            'expires': datetime.utcnow().timestamp() + CUSTOMER_SESSION_MAX_AGE,
        }
        conn = get_db()
        account = conn.execute('SELECT phone, name, email, phone_verified_at, email_verified_at FROM customer_accounts WHERE phone = ?', (phone,)).fetchone()
        conn.close()
        self._send_json({'success': True, 'customer': dict(account) if account else None}, extra_headers={
            'Set-Cookie': self._customer_cookie(token, CUSTOMER_SESSION_MAX_AGE),
            'Cache-Control': 'no-store',
        })

    def handle_customer_otp_request(self):
        data = self._read_json_body()
        purpose = str(data.get('purpose', '')).strip().lower()
        phone = _canonical_indian_phone(data.get('phone'))
        digits = _normal_phone(phone)
        if purpose not in ('register', 'login') or not phone or len(digits) != 10 or digits[0] not in '6789':
            self._send_json({'success': False, 'error': 'Enter a valid Indian mobile number.'}, 400)
            return

        name = str(data.get('name', '')).strip()[:120]
        email = str(data.get('email', '')).strip().lower()[:254]
        if purpose == 'register':
            if not name:
                self._send_json({'success': False, 'error': 'Enter your name before requesting a code.'}, 400)
                return
            if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                self._send_json({'success': False, 'error': 'Enter a valid email address or leave it blank.'}, 400)
                return

        if not MSG91_AUTH_KEY or not MSG91_OTP_TEMPLATE_ID:
            self._send_json({'success': False, 'error': 'SMS verification is not configured yet. Add the MSG91 auth key and approved OTP template on the server.'}, 503, extra_headers={'Cache-Control': 'no-store'})
            return

        retry = _otp_rate_limit(CUSTOMER_OTP_SENDS, digits, 5, 60 * 60, 30)
        if retry:
            self._send_json({'success': False, 'error': f'Please wait {retry} seconds before requesting another code.'}, 429,
                            extra_headers={'Retry-After': str(retry), 'Cache-Control': 'no-store'})
            return

        query = urllib.parse.urlencode({'template_id': MSG91_OTP_TEMPLATE_ID, 'mobile': f'91{digits}'})
        try:
            result = _msg91_call('POST', f'https://control.msg91.com/api/v5/otp?{query}', {})
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError):
            self._send_json({'success': False, 'error': 'The SMS provider could not be reached. Please try again shortly.'}, 502,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if str(result.get('type', '')).lower() != 'success':
            self._send_json({'success': False, 'error': 'MSG91 could not send the code. Check the approved template and sender setup.'}, 502,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        # Keep the response generic so callers cannot discover whether a phone has an account.
        self._send_json({'success': True, 'message': 'If the number is eligible, a verification code has been sent.'},
                        extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_otp_verify(self):
        data = self._read_json_body()
        purpose = str(data.get('purpose', '')).strip().lower()
        phone = _canonical_indian_phone(data.get('phone'))
        digits = _normal_phone(phone)
        otp = str(data.get('otp', '')).strip()
        if purpose not in ('register', 'login') or not phone or len(digits) != 10 or digits[0] not in '6789' or not re.fullmatch(r'\d{4,8}', otp):
            self._send_json({'success': False, 'error': 'Enter your mobile number and the 4–8 digit SMS code.'}, 400)
            return
        if not MSG91_AUTH_KEY or not MSG91_OTP_TEMPLATE_ID:
            self._send_json({'success': False, 'error': 'SMS verification is not configured yet. Add the MSG91 auth key and approved OTP template on the server.'}, 503,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        retry = _otp_rate_limit(CUSTOMER_OTP_VERIFIES, digits, 6, 15 * 60)
        if retry:
            self._send_json({'success': False, 'error': 'Too many code attempts. Request a new code and try later.'}, 429,
                            extra_headers={'Retry-After': str(retry), 'Cache-Control': 'no-store'})
            return

        query = urllib.parse.urlencode({'otp': otp, 'mobile': f'91{digits}'})
        try:
            result = _msg91_call('GET', f'https://control.msg91.com/api/v5/otp/verify?{query}')
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError):
            self._send_json({'success': False, 'error': 'The SMS provider could not be reached. Please try again shortly.'}, 502,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if str(result.get('type', '')).lower() != 'success':
            self._send_json({'success': False, 'error': 'That verification code is incorrect or has expired.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return

        name = str(data.get('name', '')).strip()[:120]
        email = str(data.get('email', '')).strip().lower()[:254]
        if purpose == 'register':
            if not name:
                self._send_json({'success': False, 'error': 'Enter your name to create an account.'}, 400)
                return
            if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                self._send_json({'success': False, 'error': 'Enter a valid email address or leave it blank.'}, 400)
                return

        verified_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        conn = get_db()
        try:
            conn.execute('BEGIN IMMEDIATE')
            account = conn.execute('SELECT phone FROM customer_accounts WHERE phone = ?', (phone,)).fetchone()
            if purpose == 'register':
                if email and conn.execute('SELECT 1 FROM customer_accounts WHERE lower(email) = ? LIMIT 1', (email,)).fetchone():
                    conn.rollback()
                    conn.close()
                    self._send_json({'success': False, 'error': 'This email is already linked to another account.'}, 409,
                                    extra_headers={'Cache-Control': 'no-store'})
                    return
                if account:
                    conn.rollback()
                    conn.close()
                    self._send_json({'success': False, 'error': 'An account already uses this number. Choose Sign in instead.'}, 409,
                                    extra_headers={'Cache-Control': 'no-store'})
                    return
                salt = secrets.token_bytes(16)
                random_password = secrets.token_bytes(32)
                password_hash = hashlib.pbkdf2_hmac('sha256', random_password, salt, 260_000).hex()
                conn.execute('''INSERT INTO customer_accounts
                    (phone, name, email, password_salt, password_hash, phone_verified_at)
                    VALUES (?, ?, ?, ?, ?, ?)''', (phone, name, email, salt.hex(), password_hash, verified_at))
            else:
                if not account:
                    conn.rollback()
                    conn.close()
                    self._send_json({'success': False, 'error': 'No account uses this number yet. Create an account first.'}, 404,
                                    extra_headers={'Cache-Control': 'no-store'})
                    return
                conn.execute('UPDATE customer_accounts SET phone_verified_at = COALESCE(phone_verified_at, ?) WHERE phone = ?',
                             (verified_at, phone))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            self._send_json({'success': False, 'error': 'An account already uses this number. Choose Sign in instead.'}, 409,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        except Exception:
            conn.rollback()
            conn.close()
            self._send_json({'success': False, 'error': 'Could not finish sign-in. Please try again.'}, 500,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        conn.close()
        self._start_customer_session(phone)

    def handle_customer_register(self):
        data = self._read_json_body()
        name = str(data.get('name', '')).strip()[:120]
        email = str(data.get('email', '')).strip().lower()[:254]
        phone = _canonical_indian_phone(data.get('phone'))
        password = str(data.get('password', ''))
        digits = ''.join(char for char in str(data.get('phone', '')) if char.isdigit())
        if not name or not phone or (len(digits) == 10 and digits[0] not in '6789'):
            self._send_json({'success': False, 'error': 'Enter your name and a valid Indian mobile number.'}, 400)
            return
        if len(password) < 8 or len(password) > 256:
            self._send_json({'success': False, 'error': 'Choose a password with at least 8 characters.'}, 400)
            return
        if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            self._send_json({'success': False, 'error': 'Enter a valid email address or leave it blank.'}, 400)
            return
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 260_000).hex()
        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO customer_accounts (phone, name, email, password_salt, password_hash) VALUES (?, ?, ?, ?, ?)',
                (phone, name, email, salt.hex(), password_hash),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            self._send_json({'success': False, 'error': 'An account already uses this phone number. Sign in instead.'}, 409)
            return
        except Exception:
            conn.close()
            self._send_json({'success': False, 'error': 'Your account could not be created. Please try again.'}, 500)
            return
        conn.close()
        self._start_customer_session(phone)

    def handle_customer_login(self):
        data = self._read_json_body()
        phone = _canonical_indian_phone(data.get('phone'))
        password = str(data.get('password', ''))
        if not phone or not password or len(password) > 256:
            self._send_json({'success': False, 'error': 'Enter your registered mobile number and password.'}, 400)
            return
        conn = get_db()
        row = conn.execute('SELECT phone, password_salt, password_hash FROM customer_accounts WHERE phone = ?', (phone,)).fetchone()
        conn.close()
        valid = False
        if row:
            try:
                actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(row['password_salt']), 260_000).hex()
                valid = hmac.compare_digest(actual, row['password_hash'])
            except (ValueError, TypeError):
                valid = False
        if not valid:
            self._send_json({'success': False, 'error': 'Mobile number or password is incorrect.'}, 401)
            return
        self._start_customer_session(phone)

    def handle_customer_profile(self):
        customer = self._customer()
        if not customer:
            self._send_json({'success': False, 'error': 'Customer sign-in required.'}, 401)
            return
        data = self._read_json_body()
        name = str(data.get('name', '')).strip()[:120]
        email = str(data.get('email', '')).strip().lower()[:254]
        if not name:
            self._send_json({'success': False, 'error': 'Enter your name.'}, 400)
            return
        if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            self._send_json({'success': False, 'error': 'Enter a valid email address or leave it blank.'}, 400)
            return
        conn = get_db()
        if email and conn.execute('SELECT 1 FROM customer_accounts WHERE lower(email) = ? AND phone != ? LIMIT 1',
                                  (email, customer['phone'])).fetchone():
            conn.close()
            self._send_json({'success': False, 'error': 'This email is already linked to another account.'}, 409,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        email_verified_at = customer.get('email_verified_at') if email == customer.get('email') else None
        conn.execute('UPDATE customer_accounts SET name = ?, email = ?, email_verified_at = ? WHERE phone = ?',
                     (name, email, email_verified_at, customer['phone']))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'customer': {
            'name': name, 'email': email, 'phone': customer['phone'],
            'phone_verified_at': customer.get('phone_verified_at'),
            'email_verified_at': email_verified_at,
        }}, extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_email_otp_request(self):
        customer = self._customer()
        if not customer:
            self._send_json({'success': False, 'error': 'Sign in to verify your email address.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        email = str(customer.get('email') or '').strip().lower()
        if not email or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            self._send_json({'success': False, 'error': 'Save a valid email address in your profile first.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if customer.get('email_verified_at'):
            self._send_json({'success': True, 'already_verified': True, 'message': 'This email is already verified.',
                             'customer': customer},
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if not RESEND_API_KEY or not RESEND_FROM_EMAIL:
            self._send_json({'success': False, 'error': 'Email verification is not configured yet. Add the Resend API key and verified sender address on the server.'}, 503,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        phone = customer['phone']
        retry = _otp_rate_limit(CUSTOMER_EMAIL_OTP_SENDS, phone, 5, 60 * 60, 60)
        if retry:
            self._send_json({'success': False, 'error': f'Please wait {retry} seconds before requesting another email code.'}, 429,
                            extra_headers={'Retry-After': str(retry), 'Cache-Control': 'no-store'})
            return
        code = f'{secrets.randbelow(1_000_000):06d}'
        salt = secrets.token_bytes(16)
        code_hash = hashlib.pbkdf2_hmac('sha256', code.encode('ascii'), salt, 120_000).hex()
        try:
            _resend_send_otp(email, code)
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError):
            self._send_json({'success': False, 'error': 'Resend could not send the email code. Check the API key and verified sender domain.'}, 502,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        CUSTOMER_EMAIL_OTP_CHALLENGES[phone] = {
            'email': email,
            'salt': salt.hex(),
            'code_hash': code_hash,
            'expires': time.time() + 10 * 60,
            'attempts': 0,
        }
        self._send_json({'success': True, 'message': 'A verification code was sent to your saved email address.'},
                        extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_email_otp_verify(self):
        customer = self._customer()
        if not customer:
            self._send_json({'success': False, 'error': 'Sign in to verify your email address.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        data = self._read_json_body()
        code = str(data.get('otp', '')).strip()
        if not re.fullmatch(r'\d{6}', code):
            self._send_json({'success': False, 'error': 'Enter the 6-digit code sent to your email.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        phone = customer['phone']
        retry = _otp_rate_limit(CUSTOMER_EMAIL_OTP_VERIFIES, phone, 6, 15 * 60)
        if retry:
            self._send_json({'success': False, 'error': 'Too many code attempts. Request a new email code and try later.'}, 429,
                            extra_headers={'Retry-After': str(retry), 'Cache-Control': 'no-store'})
            return
        challenge = CUSTOMER_EMAIL_OTP_CHALLENGES.get(phone)
        if (not challenge or challenge.get('email') != str(customer.get('email') or '').strip().lower()
                or challenge.get('expires', 0) < time.time()):
            CUSTOMER_EMAIL_OTP_CHALLENGES.pop(phone, None)
            self._send_json({'success': False, 'error': 'Your email code has expired. Request a new one.'}, 410,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        actual_hash = hashlib.pbkdf2_hmac('sha256', code.encode('ascii'), bytes.fromhex(challenge['salt']), 120_000).hex()
        if not hmac.compare_digest(actual_hash, challenge['code_hash']):
            challenge['attempts'] += 1
            if challenge['attempts'] >= 6:
                CUSTOMER_EMAIL_OTP_CHALLENGES.pop(phone, None)
            self._send_json({'success': False, 'error': 'That email code is incorrect or has expired.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        verified_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        conn = get_db()
        cursor = conn.execute('UPDATE customer_accounts SET email_verified_at = ? WHERE phone = ? AND email = ?',
                              (verified_at, phone, challenge['email']))
        updated = cursor.rowcount == 1
        conn.commit()
        conn.close()
        CUSTOMER_EMAIL_OTP_CHALLENGES.pop(phone, None)
        if not updated:
            self._send_json({'success': False, 'error': 'Your email changed. Save the new address and request another code.'}, 409,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        self._send_json({'success': True, 'customer': {
            'phone': customer['phone'], 'name': customer['name'], 'email': customer['email'],
            'phone_verified_at': customer.get('phone_verified_at'), 'email_verified_at': verified_at,
        }}, extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_email_login_request(self):
        data = self._read_json_body()
        email = str(data.get('email', '')).strip().lower()[:254]
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            self._send_json({'success': False, 'error': 'Enter a valid email address.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if not RESEND_API_KEY or not RESEND_FROM_EMAIL:
            self._send_json({'success': False, 'error': 'Email sign-in is not configured yet. Add the Resend API key and verified sender address on the server.'}, 503,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        email_key = hashlib.sha256(email.encode('utf-8')).hexdigest()
        retry = _otp_rate_limit(CUSTOMER_EMAIL_OTP_SENDS, f'login:{email_key}', 5, 60 * 60, 60)
        if retry:
            self._send_json({'success': False, 'error': f'Please wait {retry} seconds before requesting another email code.'}, 429,
                            extra_headers={'Retry-After': str(retry), 'Cache-Control': 'no-store'})
            return
        conn = get_db()
        accounts = conn.execute('SELECT phone FROM customer_accounts WHERE lower(email) = ? AND email_verified_at IS NOT NULL LIMIT 2',
                                (email,)).fetchall()
        conn.close()
        if len(accounts) != 1:
            self._send_json({'success': True, 'message': 'If a verified account uses this email, a sign-in code has been sent.'},
                            extra_headers={'Cache-Control': 'no-store'})
            return
        code = f'{secrets.randbelow(1_000_000):06d}'
        salt = secrets.token_bytes(16)
        code_hash = hashlib.pbkdf2_hmac('sha256', code.encode('ascii'), salt, 120_000).hex()
        try:
            _resend_send_otp(email, code)
        except (urllib.error.URLError, TimeoutError, OSError, RuntimeError):
            self._send_json({'success': False, 'error': 'Resend could not send the email code. Check the API key and verified sender domain.'}, 502,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        CUSTOMER_EMAIL_LOGIN_CHALLENGES[email_key] = {
            'email': email,
            'phone': accounts[0]['phone'],
            'salt': salt.hex(),
            'code_hash': code_hash,
            'expires': time.time() + 10 * 60,
            'attempts': 0,
        }
        self._send_json({'success': True, 'message': 'If a verified account uses this email, a sign-in code has been sent.'},
                        extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_email_login_verify(self):
        data = self._read_json_body()
        email = str(data.get('email', '')).strip().lower()[:254]
        code = str(data.get('otp', '')).strip()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or not re.fullmatch(r'\d{6}', code):
            self._send_json({'success': False, 'error': 'Enter your email address and the 6-digit code.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        email_key = hashlib.sha256(email.encode('utf-8')).hexdigest()
        retry = _otp_rate_limit(CUSTOMER_EMAIL_OTP_VERIFIES, f'login:{email_key}', 6, 15 * 60)
        if retry:
            self._send_json({'success': False, 'error': 'Too many code attempts. Request a new email code and try later.'}, 429,
                            extra_headers={'Retry-After': str(retry), 'Cache-Control': 'no-store'})
            return
        challenge = CUSTOMER_EMAIL_LOGIN_CHALLENGES.get(email_key)
        if (not challenge or challenge.get('email') != email or challenge.get('expires', 0) < time.time()):
            CUSTOMER_EMAIL_LOGIN_CHALLENGES.pop(email_key, None)
            self._send_json({'success': False, 'error': 'Your email code has expired. Request a new one or sign in by SMS.'}, 410,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        actual_hash = hashlib.pbkdf2_hmac('sha256', code.encode('ascii'), bytes.fromhex(challenge['salt']), 120_000).hex()
        if not hmac.compare_digest(actual_hash, challenge['code_hash']):
            challenge['attempts'] += 1
            if challenge['attempts'] >= 6:
                CUSTOMER_EMAIL_LOGIN_CHALLENGES.pop(email_key, None)
            self._send_json({'success': False, 'error': 'That email code is incorrect or has expired.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        conn = get_db()
        account = conn.execute('SELECT phone FROM customer_accounts WHERE phone = ? AND lower(email) = ? AND email_verified_at IS NOT NULL',
                               (challenge['phone'], email)).fetchone()
        conn.close()
        CUSTOMER_EMAIL_LOGIN_CHALLENGES.pop(email_key, None)
        if not account:
            self._send_json({'success': False, 'error': 'This email is no longer verified on the account. Sign in by SMS to verify it again.'}, 409,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        self._start_customer_session(account['phone'])

    def handle_customer_logout(self):
        token = ''
        for part in self.headers.get('Cookie', '').split(';'):
            name, _, value = part.strip().partition('=')
            if name == 'bhadawar_customer':
                token = value
                break
        CUSTOMER_SESSIONS.pop(token, None)
        self._send_json({'success': True}, extra_headers={
            'Set-Cookie': self._customer_cookie('', 0),
            'Cache-Control': 'no-store',
        })

    def handle_staff_login(self):
        data = self._read_json_body()
        role = str(data.get('role', '')).lower()
        username = str(data.get('username', '')).strip()
        password = str(data.get('password', ''))
        configured = DEMO_STAFF.get(role)
        if role == 'delivery':
            valid_login = username in DELIVERY_STAFF and hmac.compare_digest(password, DELIVERY_STAFF.get(username, ''))
        else:
            valid_login = bool(configured and hmac.compare_digest(username, configured[0]) and hmac.compare_digest(password, configured[1]))
        if not valid_login:
            self._send_json({'success': False, 'error': 'Invalid staff sign-in details.'}, 401)
            return
        token = secrets.token_urlsafe(32)
        STAFF_SESSIONS[token] = {'role': role, 'username': username, 'expires': datetime.utcnow().timestamp() + SESSION_MAX_AGE}
        self._send_json({'success': True, 'staff': {'role': role, 'username': username}}, extra_headers={
            'Set-Cookie': f'bhadawar_staff={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_MAX_AGE}'
        })

    def handle_corporate_login(self):
        data = self._read_json_body()
        staff_id = str(data.get('staff_id', '')).strip()
        company = str(data.get('company_name', '')).strip()
        valid_company = bool(company and hmac.compare_digest(company.casefold(), CORPORATE_COMPANY.casefold()))
        valid_staff_id = any(hmac.compare_digest(staff_id.casefold(), allowed_id) for allowed_id in CORPORATE_STAFF_IDS)
        if not staff_id or not valid_staff_id or not valid_company:
            self._send_json({'success': False, 'error': 'Company name or staff ID was not recognized.'}, 401)
            return
        token = secrets.token_urlsafe(32)
        STAFF_SESSIONS[token] = {
            'role': 'corporate', 'username': staff_id, 'company': CORPORATE_COMPANY,
            'expires': datetime.utcnow().timestamp() + SESSION_MAX_AGE
        }
        self._send_json({'success': True, 'staff': {'role': 'corporate', 'username': staff_id, 'company': CORPORATE_COMPANY}}, extra_headers={
            'Set-Cookie': f'bhadawar_staff={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_MAX_AGE}'
        })

    def handle_staff_logout(self):
        staff_cookie = self.headers.get('Cookie', '')
        token = next((part.strip().split('=', 1)[1] for part in staff_cookie.split(';')
                      if part.strip().startswith('bhadawar_staff=')), '')
        session = STAFF_SESSIONS.get(token)
        if session and session.get('role') == 'delivery':
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute('UPDATE delivery_riders SET is_available = 0, updated_at = CURRENT_TIMESTAMP WHERE username = ?', (session['username'],))
            cursor.execute("UPDATE orders SET delivery_rider = NULL WHERE delivery_rider = ? AND status = 'ready_for_pickup'", (session['username'],))
            self._assign_waiting_delivery_orders(cursor)
            conn.commit()
            conn.close()
        STAFF_SESSIONS.pop(token, None)
        self._send_json({'success': True}, extra_headers={'Set-Cookie': 'bhadawar_staff=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'})

    def _razorpay_call(self, method, path, payload=None):
        if not razorpay_enabled():
            raise RuntimeError('Razorpay test credentials are not configured.')
        raw = json.dumps(payload).encode('utf-8') if payload is not None else None
        request = urllib.request.Request(f'https://api.razorpay.com/v1/{path.lstrip("/")}', data=raw, method=method)
        token = base64.b64encode(f'{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}'.encode()).decode('ascii')
        request.add_header('Authorization', f'Basic {token}')
        if raw is not None:
            request.add_header('Content-Type', 'application/json')
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as error:
            detail = error.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'Razorpay request failed ({error.code}): {detail[:240]}') from error

    def handle_create_party_payment(self):
        data = self._read_json_body()
        try:
            booking_type = str(data.get('booking_type', 'party')).strip().lower()
            name = str(data.get('name', '')).strip()
            phone = str(data.get('phone', '')).strip()
            date = str(data.get('date', '')).strip()
            time = str(data.get('time', '')).strip()
            guests = int(data.get('guests', 0))
            min_guests = 10 if booking_type == 'party' else 1
            if booking_type not in ('party', 'dine') or not name or not phone or not date or not time or guests < min_guests or guests > 500:
                self._send_json({'success': False, 'error': 'Please provide valid booking details and a guest count within the allowed range.'}, 400)
                return
            if not razorpay_enabled():
                self._send_json({'success': False, 'error': 'Online booking deposits are unavailable until Razorpay test credentials are configured.'}, 503)
                return
            booking_id = f"BK{uuid.uuid4().hex[:10].upper()}"
            deposit = party_deposit_for_guests(guests) if booking_type == 'party' else guests * 50
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO bookings
                (id, booking_type, customer_name, customer_phone, booking_date, booking_time, guest_count, notes,
                 status, deposit_amount, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'payment_pending', ?, 'pending')""",
                (booking_id, booking_type, name, phone, date, time, guests,
                 'Dine-in table reservation' if booking_type == 'dine' else 'Parties & Gatherings', deposit))
            conn.commit()
            conn.close()
            try:
                order = self._razorpay_call('POST', 'orders', {
                    'amount': deposit * 100, 'currency': 'INR', 'receipt': booking_id,
                    'notes': {'booking_id': booking_id, 'booking_type': booking_type, 'guest_count': str(guests)}
                })
            except Exception:
                conn = get_db()
                conn.execute("UPDATE bookings SET status = 'payment_failed', payment_status = 'failed' WHERE id = ?", (booking_id,))
                conn.commit()
                conn.close()
                raise
            conn = get_db()
            conn.execute('UPDATE bookings SET razorpay_order_id = ? WHERE id = ?', (order['id'], booking_id))
            conn.commit()
            conn.close()
            self._send_json({'success': True, 'booking_id': booking_id, 'amount': deposit * 100,
                             'currency': 'INR', 'razorpay_order_id': order['id'], 'key_id': RAZORPAY_KEY_ID,
                             'mode': 'test' if RAZORPAY_KEY_ID.startswith('rzp_test_') else 'live'})
        except (ValueError, RuntimeError) as error:
            self._send_json({'success': False, 'error': str(error)}, 400 if isinstance(error, ValueError) else 502)
        except Exception as error:
            self._send_json({'success': False, 'error': f'Could not start deposit payment: {error}'}, 500)

    def _confirm_party_payment(self, booking_id, payment_id, order_id, signature):
        if not all((RAZORPAY_KEY_SECRET, booking_id, payment_id, order_id, signature)):
            return False, 'Payment verification details are incomplete.'
        conn = get_db()
        row = conn.execute("SELECT * FROM bookings WHERE id = ? AND booking_type IN ('party', 'dine')", (booking_id,)).fetchone()
        if not row:
            conn.close()
            return False, 'Booking was not found.'
        expected = hmac.new(RAZORPAY_KEY_SECRET.encode(), f'{order_id}|{payment_id}'.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            conn.close()
            return False, 'Payment signature could not be verified.'
        if row['payment_status'] == 'paid':
            conn.close()
            return (row['razorpay_payment_id'] == payment_id), 'This booking payment was already confirmed.'
        if row['razorpay_order_id'] != order_id:
            conn.close()
            return False, 'Payment does not match this booking.'
        try:
            payment = self._razorpay_call('GET', f'payments/{urllib.parse.quote(payment_id)}')
        except Exception as error:
            conn.close()
            return False, f'Could not confirm payment status: {error}'
        expected_paise = int(round(float(row['deposit_amount']) * 100))
        if payment.get('order_id') != order_id or payment.get('currency') != 'INR' or int(payment.get('amount', 0)) != expected_paise or payment.get('status') != 'captured':
            conn.close()
            return False, 'Payment is not captured for the correct booking amount.'
        conn.execute("""UPDATE bookings SET payment_status = 'paid', status = 'confirmed', razorpay_payment_id = ?
                     WHERE id = ? AND payment_status = 'pending'""", (payment_id, booking_id))
        conn.commit()
        conn.close()
        return True, 'Booking confirmed and advance recorded.'

    def handle_verify_party_payment(self):
        data = self._read_json_body()
        ok, message = self._confirm_party_payment(str(data.get('booking_id', '')), str(data.get('razorpay_payment_id', '')),
                                                  str(data.get('razorpay_order_id', '')), str(data.get('razorpay_signature', '')))
        self._send_json({'success': ok, 'message': message}, 200 if ok else 400)

    def handle_razorpay_webhook(self):
        content_len = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(content_len) if 0 < content_len <= 1024 * 1024 else b''
        signature = self.headers.get('X-Razorpay-Signature', '')
        if not RAZORPAY_WEBHOOK_SECRET or not raw:
            self._send_json({'success': False, 'error': 'Webhook is not configured.'}, 503)
            return
        expected = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            self._send_json({'success': False, 'error': 'Invalid webhook signature.'}, 400)
            return
        try:
            event = json.loads(raw.decode('utf-8'))
            if event.get('event') in ('payment.captured', 'order.paid'):
                entity = event.get('payload', {}).get('payment', {}).get('entity') or event.get('payload', {}).get('order', {}).get('entity') or {}
                order_id = entity.get('order_id') or entity.get('id')
                payment_id = entity.get('id') if entity.get('order_id') else ''
                if order_id and payment_id:
                    conn = get_db()
                    row = conn.execute('SELECT id FROM bookings WHERE razorpay_order_id = ? AND payment_status = \'pending\'', (order_id,)).fetchone()
                    conn.close()
                    if row:
                        # Reuse the provider API fetch and amount checks before confirming.
                        conn = get_db()
                        booking = conn.execute('SELECT * FROM bookings WHERE id = ?', (row['id'],)).fetchone()
                        conn.close()
                        # Webhooks use their own signature; verify the fetched payment and stored order instead.
                        payment = self._razorpay_call('GET', f'payments/{urllib.parse.quote(payment_id)}')
                        if payment.get('order_id') == order_id and payment.get('currency') == 'INR' and int(payment.get('amount', 0)) == int(round(float(booking['deposit_amount']) * 100)) and payment.get('status') == 'captured':
                            conn = get_db()
                            conn.execute("UPDATE bookings SET payment_status = 'paid', status = 'confirmed', razorpay_payment_id = ? WHERE id = ? AND payment_status = 'pending'", (payment_id, row['id']))
                            conn.commit()
                            conn.close()
            self._send_json({'success': True})
        except Exception as error:
            self._send_json({'success': False, 'error': str(error)}, 500)

    def handle_settle_booking(self):
        if not self._require_role('admin'):
            return
        data = self._read_json_body()
        booking_id = str(data.get('booking_id', ''))
        try:
            final_bill = float(data.get('final_bill'))
            if not booking_id or final_bill < 0:
                raise ValueError()
        except (TypeError, ValueError):
            self._send_json({'success': False, 'error': 'Enter a valid final bill amount.'}, 400)
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('BEGIN IMMEDIATE')
        booking = cursor.execute("SELECT * FROM bookings WHERE id = ? AND booking_type = 'party'", (booking_id,)).fetchone()
        if not booking:
            conn.close()
            self._send_json({'success': False, 'error': 'Party booking was not found.'}, 404)
            return
        if booking['payment_status'] != 'paid':
            conn.close()
            self._send_json({'success': False, 'error': 'Only a paid party booking can be settled.'}, 409)
            return
        if booking['final_bill'] is not None:
            conn.close()
            self._send_json({'success': False, 'error': 'This booking has already been settled.'}, 409)
            return
        deposit = float(booking['deposit_amount'] or 0)
        due = max(0, round(final_bill - deposit, 2))
        refund = max(0, round(deposit - final_bill, 2))
        cursor.execute("UPDATE bookings SET final_bill = ?, balance_due = ?, refund_due = ?, settled_at = ? WHERE id = ? AND final_bill IS NULL",
                       (final_bill, due, refund, datetime.utcnow().isoformat(timespec='seconds') + 'Z', booking_id))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'final_bill': final_bill, 'deposit_credit': deposit, 'balance_due': due,
                         'refund_due': refund, 'message': 'Party bill settled.'})

    def handle_create_corporate_order(self):
        staff = self._require_role('admin', 'corporate')
        if not staff:
            return
        data = self._read_json_body()
        name = str(staff.get('company') if staff['role'] == 'corporate' else data.get('customer_name', '')).strip()
        phone = str(data.get('customer_phone', '')).strip()
        event_date = str(data.get('event_date', '')).strip()
        event_location = str(data.get('event_location', '')).strip()
        items = data.get('items', [])
        if not name or not phone or not items:
            self._send_json({'success': False, 'error': 'Customer name, phone, and at least one menu item are required.'}, 400)
            return
        try:
            with open(CORPORATE_MENU_PATH, 'r', encoding='utf-8') as menu_file:
                menu_by_id = {item['id']: item for item in json.load(menu_file)}
            normalized = []
            for item in items:
                item_id = str(item.get('id', ''))
                quantity = int(item.get('qty', 0))
                if item_id not in menu_by_id or quantity < 1 or quantity > 500:
                    raise ValueError('One or more corporate menu quantities are invalid.')
                product = menu_by_id[item_id]
                if quantity < int(product.get('minQty') or 1):
                    raise ValueError(f"{product['name']} requires a minimum quantity of {product.get('minQty', 1)}.")
                normalized.append({'id': item_id, 'name': product['name'], 'price': float(product['price']), 'qty': quantity})
            subtotal = sum(item['price'] * item['qty'] for item in normalized)
            discount = round(subtotal * (0.15 if subtotal > 20000 else 0.10 if subtotal > 10000 else 0))
            order_id = f"CO{uuid.uuid4().hex[:10].upper()}"
            items_json = json.dumps(normalized)
            event_description = 'Corporate event' + (f' · {event_date}' if event_date else '') + (f' · {event_location}' if event_location else '')
            conn = get_db()
            conn.execute("""INSERT INTO orders (id, customer_name, customer_phone, delivery_address, order_type,
                         payment_method, subtotal, delivery_fee, tax, discount, points_used, total_amount, status, items_json)
                         VALUES (?, ?, ?, ?, 'corporate', 'invoice', ?, 0, 0, ?, 0, ?, 'received', ?)""",
                         (order_id, name, phone, event_description, subtotal, discount, subtotal - discount, items_json))
            conn.commit()
            conn.close()
            self._send_json({'success': True, 'order_id': order_id, 'subtotal': subtotal, 'discount': discount,
                             'total': subtotal - discount, 'message': 'Corporate catering order saved.'})
        except (ValueError, TypeError, OverflowError, KeyError) as error:
            self._send_json({'success': False, 'error': str(error)}, 400)
        except Exception as error:
            self._send_json({'success': False, 'error': f'Could not save corporate order: {error}'}, 500)

    def handle_update_order_status(self):
        staff = self._staff()
        if not staff:
            self._require_role()
            return
        data = self._read_json_body()
        order_id = str(data.get('order_id', ''))
        status = str(data.get('status', '')).lower()
        allowed = {
            'admin': {'accepted', 'preparing', 'ready_for_pickup', 'picked_up', 'delivered', 'cancelled'},
            'kitchen': {'accepted', 'preparing', 'ready_for_pickup'},
            'delivery': {'picked_up', 'delivered'},
        }
        if status not in allowed.get(staff['role'], set()):
            self._send_json({'success': False, 'error': 'Your role cannot set that order status.'}, 403)
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('BEGIN IMMEDIATE')
        order = cursor.execute('SELECT status, order_type, payment_method, cod_status, delivery_rider, total_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
        if not order:
            conn.close()
            self._send_json({'success': False, 'error': 'Order not found.'}, 404)
            return
        current = order['status'] or 'received'
        transitions = {
            'received': {'accepted'},
            'accepted': {'preparing'},
            'preparing': {'ready_for_pickup'},
            'ready_for_pickup': {'picked_up'},
            'picked_up': {'delivered'},
        }
        if status == 'cancelled' and staff['role'] == 'admin':
            valid_transition = current not in ('delivered', 'cancelled')
        else:
            valid_transition = status in transitions.get(current, set())
        if staff['role'] == 'kitchen' and status not in ('accepted', 'preparing', 'ready_for_pickup'):
            valid_transition = False
        if staff['role'] == 'delivery':
            if order['order_type'] != 'delivery' or order['delivery_rider'] != staff['username'] or status not in ('picked_up', 'delivered'):
                valid_transition = False
            if status == 'delivered' and str(order['payment_method'] or '').lower() in ('cod', 'cash on delivery') and order['cod_status'] not in ('collected', 'not_collected'):
                conn.close()
                self._send_json({'success': False, 'error': 'Record whether COD was collected before marking delivery complete.'}, 409)
                return
        if not valid_transition:
            conn.close()
            self._send_json({'success': False, 'error': 'That order step is not available for your role or the current order status.'}, 409)
            return
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        if status == 'ready_for_pickup' and order['order_type'] == 'delivery':
            self._assign_waiting_delivery_orders(cursor)
        bonus = self._award_order_bonus(cursor, order_id) if status == 'delivered' else 0
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'bonus_points_awarded': bonus, 'status': status,
                         'message': f'Order updated to {status.replace("_", " ")}.'})

    def handle_update_cod_status(self):
        staff = self._staff()
        if not staff:
            self._require_role()
            return
        if staff.get('role') != 'delivery':
            self._send_json({'success': False, 'error': 'Only delivery staff can update COD collection.'}, 403)
            return
        data = self._read_json_body()
        order_id = str(data.get('order_id', ''))
        cod_status = str(data.get('cod_status', '')).lower()
        if cod_status not in ('collected', 'not_collected'):
            self._send_json({'success': False, 'error': 'Choose COD received or not received.'}, 400)
            return
        conn = get_db()
        order = conn.execute('SELECT order_type, status, payment_method, delivery_rider, total_amount FROM orders WHERE id = ?', (order_id,)).fetchone()
        if not order:
            conn.close()
            self._send_json({'success': False, 'error': 'Order not found.'}, 404)
            return
        if order['order_type'] != 'delivery' or str(order['payment_method'] or '').lower() not in ('cod', 'cash on delivery'):
            conn.close()
            self._send_json({'success': False, 'error': 'This order does not require delivery COD collection.'}, 409)
            return
        if order['delivery_rider'] != staff['username']:
            conn.close()
            self._send_json({'success': False, 'error': 'This delivery is assigned to another rider.'}, 403)
            return
        if order['status'] not in ('picked_up', 'delivered'):
            conn.close()
            self._send_json({'success': False, 'error': 'COD can be confirmed after the rider picks up the order.'}, 409)
            return
        if cod_status == 'collected':
            collection_method = str(data.get('collection_method', '')).strip().lower()
            if collection_method not in ('cash', 'upi'):
                conn.close()
                self._send_json({'success': False, 'error': 'Choose whether the customer paid cash or UPI.'}, 400)
                return
            conn.execute('UPDATE orders SET cod_status = ?, cod_collected_via = ?, cod_collected_amount = total_amount WHERE id = ?',
                         (cod_status, collection_method, order_id))
        else:
            conn.execute("UPDATE orders SET cod_status = ?, cod_collected_via = NULL, cod_collected_amount = 0 WHERE id = ?",
                         (cod_status, order_id))
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'cod_status': cod_status,
                         'collection_method': collection_method if cod_status == 'collected' else None,
                         'amount': float(order['total_amount'] or 0) if cod_status == 'collected' else 0,
                         'message': 'COD collection status saved.'})

    def handle_update_rider_feedback(self):
        staff = self._require_role('delivery')
        if not staff:
            return
        data = self._read_json_body()
        order_id = str(data.get('order_id', '')).strip()
        feedback = str(data.get('feedback', '')).strip()[:500]
        if not feedback:
            self._send_json({'success': False, 'error': 'Add a short delivery note before saving.'}, 400)
            return
        conn = get_db()
        cursor = conn.execute("UPDATE orders SET rider_feedback = ? WHERE id = ? AND delivery_rider = ? AND order_type = 'delivery' AND status IN ('picked_up', 'delivered')",
                              (feedback, order_id, staff['username']))
        conn.commit()
        conn.close()
        if cursor.rowcount == 0:
            self._send_json({'success': False, 'error': 'This delivery is not assigned to your rider account.'}, 403)
            return
        self._send_json({'success': True, 'message': 'Delivery feedback saved.'})

    def handle_update_order_issue(self):
        staff = self._staff()
        if not staff:
            self._require_role()
            return
        if staff.get('role') != 'admin':
            self._send_json({'success': False, 'error': 'Only admins can update order issue notes.'}, 403)
            return
        data = self._read_json_body()
        order_id = str(data.get('order_id', ''))
        note = str(data.get('issue_note', '')).strip()[:500]
        conn = get_db()
        cursor = conn.execute('UPDATE orders SET issue_note = ? WHERE id = ?', (note or None, order_id))
        conn.commit()
        conn.close()
        if cursor.rowcount == 0:
            self._send_json({'success': False, 'error': 'Order not found.'}, 404)
            return
        self._send_json({'success': True, 'message': 'Order issue note saved.'})

    def _read_multipart_body(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len <= 0 or content_len > 52 * 1024 * 1024:
            raise ValueError('Upload must be smaller than 50 MB.')
        raw = self.rfile.read(content_len)
        content_type = self.headers.get('Content-Type', '')
        message = BytesParser(policy=email_policy).parsebytes(
            f'Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n'.encode('ascii') + raw
        )
        fields = {}
        upload = None
        for part in message.iter_parts():
            name = part.get_param('name', header='content-disposition')
            if not name:
                continue
            filename = part.get_filename()
            payload = part.get_payload(decode=True) or b''
            if filename:
                upload = {'filename': filename, 'content_type': part.get_content_type(), 'data': payload}
            else:
                charset = part.get_content_charset() or 'utf-8'
                fields[name] = payload.decode(charset, errors='replace')
        return fields, upload

    def _award_order_bonus(self, cursor, order_id):
        if not order_id:
            return 0
        cursor.execute("""
            SELECT s.*, o.status AS order_status, o.subtotal AS order_subtotal
            FROM food_stories s JOIN orders o ON o.id = s.order_id
            WHERE s.order_id = ?
        """, (order_id,))
        story = cursor.fetchone()
        if (not story or story['status'] != 'approved' or story['bonus_rewarded']
                or str(story['order_status']).lower() not in ('delivered', 'completed')
                or float(story['order_subtotal'] or 0) <= 599):
            return 0
        phone = story['phone']
        cursor.execute("INSERT OR IGNORE INTO wallet_accounts (phone, customer_name, balance) VALUES (?, ?, 0)",
                       (phone, story['author']))
        cursor.execute("UPDATE wallet_accounts SET balance = balance + 2 WHERE phone = ?", (phone,))
        cursor.execute("""INSERT INTO wallet_transactions (phone, type, amount, label)
                          VALUES (?, 'credit', 2, ?)""", (phone, f"Completed order bonus: #{order_id}"))
        cursor.execute("UPDATE food_stories SET bonus_rewarded = 1, pts = pts + 2, order_above_599 = 1 WHERE id = ?",
                       (story['id'],))
        return 2

    def handle_get_orders(self, query):
        staff = self._staff()
        if not staff:
            self._require_role()
            return
        conn = get_db()
        cursor = conn.cursor()
        if staff['role'] == 'delivery':
            cursor.execute('BEGIN IMMEDIATE')
            self._assign_waiting_delivery_orders(cursor)
            conn.commit()
        summary = None
        if staff['role'] == 'admin':
            cursor.execute("SELECT * FROM orders WHERE lower(status) IN ('delivered', 'completed', 'cancelled') ORDER BY created_at DESC LIMIT 200")
            today = cursor.execute("""SELECT
                SUM(CASE WHEN date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes') THEN 1 ELSE 0 END) AS received_today,
                SUM(CASE WHEN status = 'cancelled' AND date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes') THEN 1 ELSE 0 END) AS cancelled_today,
                SUM(CASE WHEN status IN ('delivered', 'completed') AND date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes') THEN 1 ELSE 0 END) AS completed_today,
                SUM(CASE WHEN lower(payment_method) IN ('cod', 'cash on delivery') AND cod_status = 'collected' AND cod_collected_via = 'cash' AND date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes') THEN cod_collected_amount ELSE 0 END) AS cod_cash_today,
                SUM(CASE WHEN lower(payment_method) IN ('cod', 'cash on delivery') AND cod_status = 'collected' AND cod_collected_via = 'upi' AND date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes') THEN cod_collected_amount ELSE 0 END) AS cod_upi_today,
                SUM(CASE WHEN lower(payment_method) NOT IN ('cod', 'cash on delivery', 'invoice', 'cash') AND date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes') THEN total_amount ELSE 0 END) AS online_selected_today,
                SUM(CASE WHEN issue_note IS NOT NULL AND trim(issue_note) != '' OR status = 'cancelled' OR (lower(payment_method) IN ('cod', 'cash on delivery') AND cod_status IN ('not_collected', 'not_confirmed')) THEN 1 ELSE 0 END) AS issue_count
                FROM orders""").fetchone()
            summary = {key: (float(value or 0) if key.startswith(('cod_', 'online_')) else int(value or 0)) for key, value in dict(today).items()}
        elif staff['role'] == 'kitchen':
            cursor.execute("SELECT * FROM orders WHERE status IN ('received', 'accepted', 'preparing') ORDER BY created_at DESC LIMIT 100")
        else:
            cursor.execute("SELECT * FROM orders WHERE order_type = 'delivery' AND delivery_rider = ? AND status IN ('ready_for_pickup', 'picked_up', 'delivered') ORDER BY created_at DESC LIMIT 100", (staff['username'],))
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            if r.get('items_json'):
                try:
                    r['items'] = json.loads(r['items_json'])
                except Exception:
                    r['items'] = []
            if staff['role'] == 'kitchen':
                for private_field in ('customer_phone', 'delivery_address', 'delivery_latitude',
                                      'delivery_longitude', 'delivery_instructions'):
                    r.pop(private_field, None)
        conn.close()
        self._send_json({"success": True, "orders": rows, **({'summary': summary} if summary is not None else {})})

    def _assign_waiting_delivery_orders(self, cursor):
        stale_riders = cursor.execute("SELECT username FROM delivery_riders WHERE is_available = 1 AND updated_at < datetime('now', '-2 minutes')").fetchall()
        if stale_riders:
            cursor.execute("UPDATE delivery_riders SET is_available = 0 WHERE is_available = 1 AND updated_at < datetime('now', '-2 minutes')")
            cursor.execute("UPDATE orders SET delivery_rider = NULL WHERE status = 'ready_for_pickup' AND delivery_rider IN (SELECT username FROM delivery_riders WHERE is_available = 0)")
        waiting = cursor.execute("""SELECT id FROM orders
            WHERE order_type = 'delivery' AND status = 'ready_for_pickup' AND delivery_rider IS NULL
            ORDER BY created_at ASC, id ASC""").fetchall()
        for waiting_order in waiting:
            rider = cursor.execute("""SELECT r.username FROM delivery_riders r
                WHERE r.is_available = 1
                ORDER BY (SELECT COUNT(*) FROM orders o WHERE o.delivery_rider = r.username
                    AND o.status IN ('ready_for_pickup', 'picked_up')) ASC,
                    r.updated_at ASC, r.username ASC LIMIT 1""").fetchone()
            if not rider:
                break
            cursor.execute("UPDATE orders SET delivery_rider = ? WHERE id = ? AND delivery_rider IS NULL",
                           (rider['username'], waiting_order['id']))

    def handle_get_rider_availability(self):
        staff = self._require_role('admin', 'delivery')
        if not staff:
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('BEGIN IMMEDIATE')
        self._assign_waiting_delivery_orders(cursor)
        conn.commit()
        riders = [dict(row) for row in conn.execute("""SELECT r.username, r.is_available,
            (SELECT COUNT(*) FROM orders o WHERE o.delivery_rider = r.username AND o.status IN ('ready_for_pickup', 'picked_up')) AS active_assignments
            FROM delivery_riders r ORDER BY r.username""").fetchall()]
        row = next((rider for rider in riders if rider['username'] == staff['username']), None)
        available_count = sum(1 for rider in riders if rider['is_available'])
        conn.close()
        self._send_json({'success': True, 'is_available': bool(row['is_available']) if row else False,
                         'available_riders': available_count, 'active_assignments': row['active_assignments'] if row else 0,
                         'riders': riders})

    def handle_update_rider_availability(self):
        staff = self._require_role('delivery')
        if not staff:
            return
        data = self._read_json_body()
        available = data.get('is_available')
        if not isinstance(available, bool):
            self._send_json({'success': False, 'error': 'Choose whether you are available to take orders.'}, 400)
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute("""INSERT INTO delivery_riders (username, is_available, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(username) DO UPDATE SET is_available = excluded.is_available, updated_at = CURRENT_TIMESTAMP""",
            (staff['username'], 1 if available else 0))
        if not available:
            cursor.execute("UPDATE orders SET delivery_rider = NULL WHERE delivery_rider = ? AND status = 'ready_for_pickup'", (staff['username'],))
        self._assign_waiting_delivery_orders(cursor)
        conn.commit()
        active = cursor.execute("SELECT COUNT(*) FROM orders WHERE delivery_rider = ? AND status IN ('ready_for_pickup', 'picked_up')", (staff['username'],)).fetchone()[0]
        available_count = cursor.execute('SELECT COUNT(*) FROM delivery_riders WHERE is_available = 1').fetchone()[0]
        conn.close()
        self._send_json({'success': True, 'is_available': available, 'available_riders': available_count,
                         'active_assignments': active, 'message': 'Availability updated. Ready orders are assigned to available riders.'})

    def handle_get_customer_order_history(self, query):
        customer = self._customer()
        if not customer:
            self._send_json({'success': False, 'error': 'Sign in to view your order history.'}, 401)
            return
        conn = get_db()
        rows = [dict(row) for row in conn.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT 500').fetchall()
                if _normal_phone(row['customer_phone']) == _normal_phone(customer['phone'])]
        conn.close()
        for row in rows:
            try:
                row['items'] = json.loads(row.get('items_json') or '[]')
            except (TypeError, ValueError):
                row['items'] = []
        self._send_json({'success': True, 'orders': rows})

    def handle_track_order(self):
        data = self._read_json_body()
        order_id = str(data.get('order_id', '')).strip().upper()
        phone = _normal_phone(data.get('phone', ''))
        if not order_id or len(phone) < 10:
            self._send_json({'success': False, 'error': 'Enter your order number and 10-digit phone number.'}, 400)
            return
        conn = get_db()
        row = conn.execute('SELECT id, customer_name, customer_phone, order_type, status, created_at, total_amount FROM orders WHERE upper(id) = ?', (order_id,)).fetchone()
        conn.close()
        if not row or _normal_phone(row['customer_phone']) != phone:
            self._send_json({'success': False, 'error': 'We could not find an order matching those details.'}, 404)
            return
        self._send_json({'success': True, 'order': {
            'id': row['id'], 'order_type': row['order_type'], 'status': row['status'],
            'created_at': row['created_at'], 'total_amount': row['total_amount']
        }})

    def handle_create_order(self):
        customer = self._customer()
        if not customer:
            self._send_json({'success': False, 'error': 'Sign in before placing an order.'}, 401)
            return
        data = self._read_json_body()
        requested_items = data.get('items')
        if not isinstance(requested_items, list) or not requested_items:
            self._send_json({'success': False, 'error': 'Add at least one menu item before ordering.'}, 400)
            return

        order_type = str(data.get('order_type', 'delivery')).strip().lower()
        if order_type not in ('delivery', 'takeaway', 'dine_in'):
            self._send_json({'success': False, 'error': 'Choose delivery, takeaway, or dine-in.'}, 400)
            return
        if order_type == 'corporate' or any(str(item.get('id', '')).startswith('corp-') for item in requested_items if isinstance(item, dict)):
            self._send_json({'success': False, 'error': 'Corporate catering orders must use the corporate order form.'}, 400)
            return

        customer_name = customer['name']
        customer_phone = customer['phone']
        delivery_address = str(data.get('delivery_address', '')).strip()[:500]
        delivery_instructions = str(data.get('delivery_instructions', '')).strip()[:500]
        if not customer_name or not customer_phone:
            self._send_json({'success': False, 'error': 'Enter your name and a valid 10-digit Indian phone number.'}, 400)
            return
        if order_type == 'delivery' and len(delivery_address) < 6:
            self._send_json({'success': False, 'error': 'Enter your delivery address before placing the order.'}, 400)
            return

        payment_method = str(data.get('payment_method', 'upi')).strip().lower()
        if payment_method not in ('upi', 'card', 'cod'):
            self._send_json({'success': False, 'error': 'Choose a supported payment method.'}, 400)
            return

        try:
            delivery_latitude = float(data['delivery_latitude']) if data.get('delivery_latitude') is not None else None
            delivery_longitude = float(data['delivery_longitude']) if data.get('delivery_longitude') is not None else None
            raw_points = data.get('points_used', 0)
            if isinstance(raw_points, bool) or int(raw_points) != float(raw_points):
                raise ValueError('Wallet points must be a whole number.')
            points_used = int(raw_points)
        except (TypeError, ValueError, OverflowError):
            self._send_json({'success': False, 'error': 'The delivery pin or wallet points are invalid.'}, 400)
            return
        if points_used < 0:
            self._send_json({'success': False, 'error': 'Wallet points cannot be negative.'}, 400)
            return
        if (delivery_latitude is None) != (delivery_longitude is None):
            self._send_json({'success': False, 'error': 'Both delivery coordinates are required for a map pin.'}, 400)
            return
        if order_type == 'delivery' and delivery_latitude is None:
            self._send_json({'success': False, 'error': 'Pin your delivery location so the delivery range and fee can be checked.'}, 400)
            return
        if delivery_latitude is not None and not (-90 <= delivery_latitude <= 90 and -180 <= delivery_longitude <= 180):
            self._send_json({'success': False, 'error': 'The delivery map pin is outside valid coordinates.'}, 400)
            return
        if order_type != 'delivery':
            delivery_latitude = delivery_longitude = None

        try:
            catalog = load_menu_catalog()
            quantities = {}
            for requested in requested_items:
                if not isinstance(requested, dict):
                    raise ValueError('One or more menu items are invalid.')
                item_id = str(requested.get('id', '')).strip()
                raw_qty = requested.get('qty', 0)
                if isinstance(raw_qty, bool) or int(raw_qty) != float(raw_qty):
                    raise ValueError('Menu quantities must be whole numbers.')
                quantity = int(raw_qty)
                if item_id not in catalog or quantity < 1 or quantity > 99:
                    raise ValueError('One or more menu items or quantities are invalid.')
                quantities[item_id] = quantities.get(item_id, 0) + quantity
                if quantities[item_id] > 99:
                    raise ValueError('A menu item quantity cannot exceed 99.')
            items = [
                {**catalog[item_id], 'qty': quantity}
                for item_id, quantity in quantities.items()
            ]
        except (ValueError, TypeError, OverflowError, KeyError) as error:
            self._send_json({'success': False, 'error': str(error)}, 400)
            return
        except Exception:
            self._send_json({'success': False, 'error': 'The published menu could not be checked. Please try again.'}, 500)
            return

        destination_distance = None
        if order_type == 'delivery':
            destination_distance = distance_km(delivery_latitude, delivery_longitude)
            if destination_distance > 10:
                self._send_json({'success': False, 'error': 'Delivery is available only within 10 km of the restaurant.'}, 400)
                return

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('BEGIN IMMEDIATE')

            existing_phones = cursor.execute(
                "SELECT customer_phone FROM orders WHERE order_type != 'corporate'"
            ).fetchall()
            first_order = not any(_normal_phone(row['customer_phone']) == _normal_phone(customer_phone) for row in existing_phones)
            totals = checkout_totals(
                items, order_type, destination_distance, first_order,
                tax_percent=ORDER_TAX_PERCENT,
                delivery_fee_under_5=DELIVERY_FEE_UNDER_5,
                delivery_fee_5_to_10=DELIVERY_FEE_5_TO_10,
            )
            if totals['subtotal'] <= 0 or totals['total_before_points'] <= 0:
                conn.rollback()
                conn.close()
                self._send_json({'success': False, 'error': 'Your order total must be greater than ₹0. Check your cart and try again.'}, 400)
                return

            wallet_account = None
            if points_used:
                accounts = cursor.execute('SELECT phone, balance FROM wallet_accounts').fetchall()
                wallet_account = next((row for row in accounts if _normal_phone(row['phone']) == _normal_phone(customer_phone)), None)
                wallet_balance = int(wallet_account['balance'] or 0) if wallet_account else 0
                max_redeem = math.floor(totals['total_before_points'] * MAX_WALLET_REDEEM_PERCENT / 100)
                if points_used > wallet_balance:
                    conn.rollback()
                    conn.close()
                    self._send_json({'success': False, 'error': 'Your wallet balance is lower than the points requested.'}, 409)
                    return
                if points_used > max_redeem:
                    conn.rollback()
                    conn.close()
                    self._send_json({'success': False, 'error': f'You can use up to {max_redeem} points on this order.'}, 400)
                    return

            totals['points_used'] = points_used
            totals['total_amount'] = totals['total_before_points'] - points_used
            if totals['total_amount'] <= 0:
                conn.rollback()
                conn.close()
                self._send_json({'success': False, 'error': 'Your payable total must be greater than ₹0. Reduce wallet points or add an item.'}, 400)
                return
            order_id = f"BH{datetime.now().strftime('%y%m%d%H%M%S')}{secrets.token_hex(3).upper()}"
            items_json = json.dumps(items, ensure_ascii=False)
            cursor.execute("""
            INSERT INTO orders (id, customer_name, customer_phone, delivery_address, delivery_latitude, delivery_longitude, delivery_instructions, order_type,
                                payment_method, subtotal, delivery_fee, tax, discount, points_used,
                                total_amount, status, items_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'received', ?)
            """, (order_id, customer_name, customer_phone, delivery_address, delivery_latitude, delivery_longitude, delivery_instructions, order_type,
                  payment_method, totals['subtotal'], totals['delivery_fee'], totals['tax'], totals['discount'], points_used,
                  totals['total_amount'], items_json))

            if payment_method == 'cod':
                cursor.execute("UPDATE orders SET cod_status = 'pending' WHERE id = ?", (order_id,))

            if points_used:
                cursor.execute('UPDATE wallet_accounts SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP WHERE phone = ?',
                               (points_used, wallet_account['phone']))
                cursor.execute("""
                INSERT INTO wallet_transactions (phone, type, amount, label)
                VALUES (?, 'debit', ?, ?)
                """, (wallet_account['phone'], points_used, f'Redeemed on Order #{order_id}'))
                wallet_balance_after = int(wallet_account['balance']) - points_used
            else:
                wallet_balance_after = None

            conn.commit()
            conn.close()
            self._send_json({
                'success': True,
                'order_id': order_id,
                'message': 'Order created successfully',
                'items': items,
                'subtotal': totals['subtotal'],
                'delivery_fee': totals['delivery_fee'],
                'tax': totals['tax'],
                'discount': totals['discount'],
                'points_used': totals['points_used'],
                'total_amount': totals['total_amount'],
                'wallet_balance': wallet_balance_after,
                'first_order': first_order,
                'delivery_distance_km': round(destination_distance, 2) if destination_distance is not None else None,
            })
        except Exception:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
            self._send_json({'success': False, 'error': 'The order could not be saved. Please try again.'}, 500)

    def handle_complete_order(self):
        if not self._require_role('admin'):
            return
        data = self._read_json_body()
        order_id = data.get('order_id')
        if not order_id:
            self._send_json({"success": False, "error": "Missing order_id"}, 400)
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            conn.close()
            self._send_json({"success": False, "error": "Order not found."}, 404)
            return
        if str(order['status']).lower() == 'cancelled':
            conn.close()
            self._send_json({"success": False, "error": "Cancelled orders cannot be completed."}, 409)
            return
        cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = ?", (order_id,))
        bonus = self._award_order_bonus(cursor, order_id)
        conn.commit()
        conn.close()
        message = 'Order marked completed.' + (f' +{bonus} feedback bonus points added.' if bonus else '')
        self._send_json({"success": True, "bonus_points_awarded": bonus, "message": message})

    def handle_get_bookings(self, query):
        if not self._require_role('admin'):
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings ORDER BY created_at DESC LIMIT 50")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        self._send_json({"success": True, "bookings": rows})

    def handle_create_booking(self):
        data = self._read_json_body()
        booking_id = f"BK{int(datetime.now().timestamp()*1000)%1000000:06d}"
        booking_type = data.get('booking_type', 'dine')
        if booking_type != 'dine':
            self._send_json({'success': False, 'error': 'Only dine-in reservations use this request endpoint.'}, 400)
            return
        name = data.get('name', 'Guest')
        phone = data.get('phone', '')
        date = data.get('date', '')
        time = data.get('time', '')
        guests = int(data.get('guests', 2))
        notes = data.get('notes', '')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO bookings (id, booking_type, customer_name, customer_phone, booking_date, booking_time, guest_count, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (booking_id, booking_type, name, phone, date, time, guests, notes))
        conn.commit()
        conn.close()
        self._send_json({"success": True, "booking_id": booking_id, "message": "Reservation saved"})

    def handle_get_stories(self, query):
        status_filter = query.get('status', ['approved'])[0]
        if status_filter != 'approved' and not self._require_role('admin'):
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food_stories WHERE status = ? ORDER BY created_at DESC", (status_filter,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        self._send_json({"success": True, "stories": rows})

    def handle_create_story(self):
        try:
            if self.headers.get('Content-Type', '').lower().startswith('multipart/form-data'):
                data, upload = self._read_multipart_body()
            else:
                data, upload = self._read_json_body(), None
            author = str(data.get('author', '')).strip()
            phone = str(data.get('phone', '')).strip()
            dish = str(data.get('dish', '')).strip()
            dish_id = str(data.get('dish_id', '')).strip()
            text = str(data.get('text', '')).strip()
            rating = int(data.get('rating', 0))
            order_id = str(data.get('order_id', '')).strip() or None
            if not author or not phone or not dish or not text or rating not in range(1, 6):
                self._send_json({"success": False, "error": "Name, phone, dish, story, and a 1–5 rating are required."}, 400)
                return
            if not upload or not upload['data']:
                self._send_json({"success": False, "error": "Choose a food photo or video to upload."}, 400)
                return
            if len(upload['data']) > 50 * 1024 * 1024:
                self._send_json({"success": False, "error": "Upload must be smaller than 50 MB."}, 413)
                return
            allowed = {
                'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp', 'image/gif': '.gif',
                'video/mp4': '.mp4', 'video/webm': '.webm', 'video/quicktime': '.mov', 'video/x-m4v': '.m4v'
            }
            ext = allowed.get(upload['content_type'])
            if not ext:
                self._send_json({"success": False, "error": "Use a JPG, PNG, WebP, GIF, MP4, WebM, or MOV file."}, 415)
                return

            conn = get_db()
            cursor = conn.cursor()
            if order_id:
                cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
                order = cursor.fetchone()
                if (not order or _normal_phone(order['customer_phone']) != _normal_phone(phone)
                        or str(order['status']).lower() not in ('delivered', 'completed')
                        or float(order['subtotal'] or 0) <= 599):
                    conn.close()
                    self._send_json({"success": False, "error": "Only your completed orders with a food subtotal above ₹599 can be linked."}, 400)
                    return
                cursor.execute("SELECT id FROM food_stories WHERE order_id = ?", (order_id,))
                if cursor.fetchone():
                    conn.close()
                    self._send_json({"success": False, "error": "This order already has a submitted feedback story."}, 409)
                    return

            story_id = f"fs-{uuid.uuid4().hex[:16]}"
            filename = f"{uuid.uuid4().hex}{ext}"
            relative_media = f"uploads/food-stories/{filename}"
            upload_dir = os.path.join(BASE_DIR, 'uploads', 'food-stories')
            os.makedirs(upload_dir, exist_ok=True)
            with open(os.path.join(upload_dir, filename), 'wb') as media_file:
                media_file.write(upload['data'])
            media_type = 'video' if upload['content_type'].startswith('video/') else 'image'
            cursor.execute("""
                INSERT INTO food_stories
                  (id, author, phone, dish, dish_id, rating, text, photo, media_type, pts,
                   order_above_599, order_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 'pending')
            """, (story_id, author, phone, dish, dish_id, rating, text, relative_media, media_type,
                  1 if order_id else 0, order_id))
            conn.commit()
            conn.close()
            self._send_json({"success": True, "story_id": story_id, "pts": 1, "message": "Story submitted for approval"})
        except ValueError as error:
            self._send_json({"success": False, "error": str(error)}, 400)
        except Exception as error:
            self._send_json({"success": False, "error": f"Story upload failed: {error}"}, 500)

    def handle_approve_story(self):
        if not self._require_role('admin'):
            return
        data = self._read_json_body()
        story_id = data.get('story_id')
        if not story_id:
            self._send_json({"error": "Missing story_id"}, 400)
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT * FROM food_stories WHERE id = ?", (story_id,))
        story = cursor.fetchone()
        if not story:
            conn.close()
            self._send_json({"error": "Story not found"}, 404)
            return

        if story['status'] != 'pending':
            conn.close()
            self._send_json({"success": False, "error": "Only pending stories can be approved."}, 409)
            return
        cursor.execute("UPDATE food_stories SET status = 'approved', pts = 1, story_rewarded = 1 WHERE id = ? AND status = 'pending'", (story_id,))
        phone = story['phone']
        cursor.execute("INSERT OR IGNORE INTO wallet_accounts (phone, customer_name, balance) VALUES (?, ?, 0)", (phone, story['author']))
        cursor.execute("UPDATE wallet_accounts SET balance = balance + 1 WHERE phone = ?", (phone,))
        cursor.execute("INSERT INTO wallet_transactions (phone, type, amount, label) VALUES (?, 'credit', 1, ?)",
                       (phone, f"Food Story Approved: {story['dish']}"))
        bonus = self._award_order_bonus(cursor, story['order_id'])
        conn.commit()
        conn.close()
        self._send_json({"success": True, "points_awarded": 1 + bonus, "message": f"Story approved. +1 point{f' and +{bonus} order bonus' if bonus else ''} added to the wallet."})

    def handle_reject_story(self):
        if not self._require_role('admin'):
            return
        data = self._read_json_body()
        story_id = data.get('story_id')
        if not story_id:
            self._send_json({"success": False, "error": "Missing story_id"}, 400)
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE food_stories SET status = 'rejected' WHERE id = ? AND status = 'pending'", (story_id,))
        if cursor.rowcount == 0:
            conn.close()
            self._send_json({"success": False, "error": "Only pending stories can be rejected."}, 409)
            return
        conn.commit()
        conn.close()
        self._send_json({"success": True, "message": "Story rejected."})

    def handle_like_story(self):
        data = self._read_json_body()
        story_id = data.get('story_id')
        conn = get_db()
        cursor = conn.cursor()
        delta = 1 if data.get('liked') else -1
        cursor.execute("UPDATE food_stories SET likes = MAX(0, likes + ?) WHERE id = ? AND status = 'approved'", (delta, story_id))
        if cursor.rowcount == 0:
            conn.close()
            self._send_json({"success": False, "error": "Approved story not found."}, 404)
            return
        cursor.execute("SELECT likes FROM food_stories WHERE id = ?", (story_id,))
        likes = cursor.fetchone()['likes']
        conn.commit()
        conn.close()
        self._send_json({"success": True, "likes": likes})

    def handle_get_leaderboard(self, query):
        conn = get_db()
        cursor = conn.cursor()
        def rankings(monthly=False):
            month_filter = " AND created_at >= date('now', 'start of month')" if monthly else ''
            cursor.execute(f"""
                SELECT author AS name, COUNT(*) AS blogs, SUM(pts) AS points
                FROM food_stories WHERE status = 'approved'{month_filter}
                GROUP BY author ORDER BY blogs DESC, points DESC, name COLLATE NOCASE ASC
            """)
            result = []
            for i, row in enumerate(cursor.fetchall()):
                result.append({
                    "rank": i + 1,
                    "name": row['name'],
                    "avatar": row['name'][0].upper() if row['name'] else 'F',
                    "blogs": row['blogs'],
                    "points": row['points'] or 0,
                    "badge": '🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else ''
                })
            return result
        alltime = rankings()
        monthly = rankings(monthly=True)
        conn.close()
        self._send_json({"success": True, "alltime": alltime, "monthly": monthly})

    def handle_get_wallet(self, query):
        phone = query.get('phone', ['+91 98765 43210'])[0]
        conn = get_db()
        cursor = conn.cursor()
        accounts = cursor.execute("SELECT * FROM wallet_accounts").fetchall()
        acc = next((row for row in accounts if _normal_phone(row['phone']) == _normal_phone(phone)), None)
        wallet_phone = acc['phone'] if acc else phone
        cursor.execute("SELECT * FROM wallet_transactions WHERE phone = ? ORDER BY created_at DESC LIMIT 20", (wallet_phone,))
        txs = [dict(r) for r in cursor.fetchall()]
        conn.close()

        balance = acc['balance'] if acc else 0
        name = acc['customer_name'] if acc else 'Bhadawar Guest'

        self._send_json({
            "success": True,
            "phone": phone,
            "name": name,
            "balance": balance,
            "transactions": txs
        })

    def handle_get_reviews(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        self._send_json({"success": True, "reviews": rows})

    def handle_create_review(self):
        data = self._read_json_body()
        name = str(data.get('name', '')).strip()[:60]
        text = str(data.get('text', '')).strip()[:1000]
        try:
            rating = int(data.get('rating', 0))
        except (TypeError, ValueError, OverflowError):
            self._send_json({'success': False, 'error': 'Choose a rating from 1 to 5.'}, 400)
            return
        if not name or len(text) < 10 or rating < 1 or rating > 5:
            self._send_json({'success': False, 'error': 'Add a name, a rating from 1 to 5, and at least 10 characters of feedback.'}, 400)
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (name, rating, review_text) VALUES (?, ?, ?)", (name, rating, text))
        conn.commit()
        conn.close()
        self._send_json({"success": True, "message": "Feedback saved for the restaurant team."})

    def handle_get_stats(self):
        if not self._require_role('admin'):
            return
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM bookings")
        bookings_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM food_stories WHERE status = 'approved'")
        published_stories = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM food_stories WHERE status = 'pending'")
        pending_stories = cursor.fetchone()[0]
        conn.close()

        self._send_json({
            "success": True,
            "orders": orders_count,
            "bookings": bookings_count,
            "published_stories": published_stories,
            "pending_stories": pending_stories
        })

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), BhadawarBackendHandler) as httpd:
        print(f"Bhadawar Hotel Backend Server running at http://{HOST}:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
