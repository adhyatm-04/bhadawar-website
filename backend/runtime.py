"""
Bhadawar Hotel & Foods - Complete Full-Featured Backend Server
Handles static file serving + REST APIs for Orders, Bookings, Food Stories, Leaderboard, Wallet, Reviews.
"""
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
import threading
from pathlib import Path
from email.parser import BytesParser
from email.policy import default as email_policy
from datetime import datetime
from order_pricing import checkout_totals, distance_km, load_menu_catalog
from backend.state import StateStore

PORT = int(os.environ.get('PORT', '4175'))
HOST = os.environ.get('HOST', '127.0.0.1')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

DB_PATH = os.environ.get('BHADAWAR_DB_PATH', os.path.join(BASE_DIR, 'bhadawar.db'))
PUBLIC_PREVIEW_MODE = os.environ.get('BHADAWAR_PUBLIC_PREVIEW', '').lower() == 'true'
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
REDIS_URL = os.environ.get('REDIS_URL', '').strip()
DEPLOYMENT_ENV = os.environ.get('BHADAWAR_ENV', 'development').strip().lower()
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
SESSION_MAX_AGE = 8 * 60 * 60
CUSTOMER_SESSION_MAX_AGE = 30 * 24 * 60 * 60
STAFF_SESSIONS = StateStore('staff_sessions', SESSION_MAX_AGE)
CUSTOMER_SESSIONS = StateStore('customer_sessions', CUSTOMER_SESSION_MAX_AGE)
CUSTOMER_OTP_SENDS = StateStore('customer_otp_sends', 60 * 60)
CUSTOMER_OTP_VERIFIES = StateStore('customer_otp_verifies', 15 * 60)
CUSTOMER_EMAIL_OTP_SENDS = StateStore('customer_email_otp_sends', 60 * 60)
CUSTOMER_EMAIL_OTP_VERIFIES = StateStore('customer_email_otp_verifies', 15 * 60)
CUSTOMER_EMAIL_OTP_CHALLENGES = StateStore('customer_email_otp_challenges', 10 * 60)
CUSTOMER_EMAIL_LOGIN_CHALLENGES = StateStore('customer_email_login_challenges', 10 * 60)

def party_deposit_for_guests(guests):
    return int(guests) * (30 if int(guests) >= 12 else 50)

def razorpay_enabled():
    return bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and
                (RAZORPAY_KEY_ID.startswith('rzp_test_') or RAZORPAY_ALLOW_LIVE))

_DATABASE_SCHEMA_LOCK = threading.Lock()
_SQLITE_SCHEMA_READY = False
_POSTGRES_SCHEMA_READY = False


def validate_production_services():
    if DEPLOYMENT_ENV == 'production':
        missing = [name for name, value in (('DATABASE_URL', DATABASE_URL), ('REDIS_URL', REDIS_URL)) if not value]
        if missing:
            raise RuntimeError('Production mode requires configured persistent services: ' + ', '.join(missing))


def is_integrity_error(error):
    """Recognize unique/foreign-key conflicts from SQLite and PostgreSQL drivers."""
    return isinstance(error, sqlite3.IntegrityError) or error.__class__.__name__ == 'IntegrityError'


def _ensure_postgres_schema():
    global _POSTGRES_SCHEMA_READY
    if _POSTGRES_SCHEMA_READY:
        return
    with _DATABASE_SCHEMA_LOCK:
        if not _POSTGRES_SCHEMA_READY:
            from backend.database import upgrade_schema
            upgrade_schema()
            _POSTGRES_SCHEMA_READY = True


def get_db():
    if DATABASE_URL:
        _ensure_postgres_schema()
        from backend.database import connect_database
        return connect_database()

    global _SQLITE_SCHEMA_READY
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout = 30000')
    conn.execute('PRAGMA journal_mode = WAL')
    with _DATABASE_SCHEMA_LOCK:
        if not _SQLITE_SCHEMA_READY:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'orders' not in tables:
                from backend_db import init_db
                bootstrap = init_db()
                bootstrap.close()
            _migrate_db(conn)
            _SQLITE_SCHEMA_READY = True
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
    if bucket.remote_enabled:
        return bucket.rate_limit(key, limit, window_seconds, cooldown_seconds)
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

__all__ = [name for name in globals() if not name.startswith("__")]
