"""Auth request handlers."""
from backend.runtime import *
from sqlalchemy import func, select, update
from backend.database import lock_transaction
from backend.models import CustomerAccount, DeliveryRider, Order

class AuthHandlers:
    @staticmethod
    def _public_customer(account):
        """Return only customer profile fields; never expose password hashes or provider IDs."""
        if not account:
            return None
        return {
            'phone': account.phone,
            'name': account.name,
            'email': account.email,
            'phone_verified_at': account.phone_verified_at,
            'email_verified_at': account.email_verified_at,
            'created_at': account.created_at.isoformat(sep=' ', timespec='seconds')
            if isinstance(account.created_at, datetime) else account.created_at,
        }

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
        row = conn.get(CustomerAccount, session['phone'])
        conn.close()
        if not row:
            CUSTOMER_SESSIONS.pop(token, None)
            return None
        return self._public_customer(row)

    def _customer_cookie(self, token, max_age):
        suffix = self._secure_cookie_attribute()
        return f'bhadawar_customer={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={max_age}{suffix}'

    def _secure_cookie_attribute(self):
        secure = self.headers.get('X-Forwarded-Proto', '').split(',', 1)[0].strip().lower() == 'https'
        if not secure:
            origin = urllib.parse.urlparse(self.headers.get('Origin', ''))
            secure = origin.scheme == 'https'
        return '; Secure' if secure else ''

    def _require_role(self, *roles):
        staff = self._staff()
        if not staff:
            self._send_json({'success': False, 'error': 'Staff sign-in required.'}, 401)
            return None
        if roles and staff['role'] not in roles:
            self._send_json({'success': False, 'error': 'Your staff role cannot access this action.'}, 403)
            return None
        return staff

    def _start_customer_session(self, phone):
        token = secrets.token_urlsafe(32)
        CUSTOMER_SESSIONS[token] = {
            'phone': phone,
            'expires': datetime.utcnow().timestamp() + CUSTOMER_SESSION_MAX_AGE,
        }
        conn = get_db()
        account = conn.get(CustomerAccount, phone)
        conn.close()
        self._send_json({'success': True, 'customer': self._public_customer(account)}, extra_headers={
            'Set-Cookie': self._customer_cookie(token, CUSTOMER_SESSION_MAX_AGE),
            'Cache-Control': 'no-store',
        })

    def handle_customer_google_config(self):
        self._send_json(
            {'success': True, 'configured': bool(GOOGLE_CLIENT_ID), 'client_id': GOOGLE_CLIENT_ID},
            extra_headers={'Cache-Control': 'no-store'},
        )

    def _read_google_login_challenge(self, token):
        token = str(token or '').strip()
        if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token):
            return None
        try:
            challenge = CUSTOMER_GOOGLE_LOGIN_CHALLENGES[token]
        except KeyError:
            return None
        if float(challenge.get('expires', 0)) <= time.time():
            CUSTOMER_GOOGLE_LOGIN_CHALLENGES.pop(token, None)
            return None
        return challenge

    def handle_customer_google_start(self):
        if not GOOGLE_CLIENT_ID:
            self._send_json({'success': False, 'error': 'Google sign-in is not configured yet.'}, 503,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        data = self._read_json_body()
        credential = str(data.get('credential', '')).strip()
        if not credential or len(credential) > 12000:
            self._send_json({'success': False, 'error': 'Google could not verify this sign-in. Please try again.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        try:
            from google.auth import exceptions as google_auth_exceptions
            from google.auth.transport.requests import Request as GoogleAuthRequest
            from google.oauth2 import id_token
        except ImportError:
            self._send_json({'success': False, 'error': 'Google sign-in service is unavailable. Please try again later.'}, 503,
                            extra_headers={'Cache-Control': 'no-store'})
            return

        class _ShortTimeoutGoogleRequest(GoogleAuthRequest):
            def __call__(self, *args, **kwargs):
                kwargs.setdefault('timeout', 5)
                return super().__call__(*args, **kwargs)

        try:
            claims = id_token.verify_oauth2_token(credential, _ShortTimeoutGoogleRequest(), GOOGLE_CLIENT_ID)
        except (google_auth_exceptions.GoogleAuthError, ValueError):
            self._send_json({'success': False, 'error': 'Google could not verify this sign-in. Please try again.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        except (TimeoutError, OSError):
            self._send_json({'success': False, 'error': 'Google sign-in is temporarily unavailable. Please try again.'}, 502,
                            extra_headers={'Cache-Control': 'no-store'})
            return

        subject = str(claims.get('sub', '')).strip()
        email = str(claims.get('email', '')).strip().lower()[:254]
        email_verified = claims.get('email_verified') is True or str(claims.get('email_verified', '')).lower() == 'true'
        if (not subject or not email_verified or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)):
            self._send_json({'success': False, 'error': 'Use a Google account with a verified email address.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return

        token = secrets.token_urlsafe(36)
        expires = time.time() + 10 * 60
        CUSTOMER_GOOGLE_LOGIN_CHALLENGES[token] = {
            'sub': subject,
            'email': email,
            'name': str(claims.get('name', '')).strip()[:120],
            'expires': expires,
        }
        self._send_json({
            'success': True,
            'challenge': token,
            'email': email,
            'name': str(claims.get('name', '')).strip()[:120],
            'expires_in': 600,
        }, extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_google_otp_request(self):
        data = self._read_json_body()
        challenge_token = str(data.get('challenge', '')).strip()
        challenge = self._read_google_login_challenge(challenge_token)
        phone = _canonical_indian_phone(data.get('phone'))
        digits = _normal_phone(phone)
        if not challenge:
            self._send_json({'success': False, 'error': 'Your Google sign-in expired. Please start again.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if not phone or len(digits) != 10 or digits[0] not in '6789':
            self._send_json({'success': False, 'error': 'Enter a valid Indian mobile number.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if not MSG91_AUTH_KEY or not MSG91_OTP_TEMPLATE_ID:
            self._send_json({'success': False, 'error': 'SMS verification is not configured yet. Add the MSG91 auth key and approved OTP template on the server.'}, 503,
                            extra_headers={'Cache-Control': 'no-store'})
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
        challenge['phone'] = phone
        challenge['otp_sent'] = True
        CUSTOMER_GOOGLE_LOGIN_CHALLENGES[challenge_token] = challenge
        self._send_json({'success': True, 'message': 'A verification code was sent by SMS.'},
                        extra_headers={'Cache-Control': 'no-store'})

    def handle_customer_google_otp_verify(self):
        data = self._read_json_body()
        challenge_token = str(data.get('challenge', '')).strip()
        challenge = self._read_google_login_challenge(challenge_token)
        phone = _canonical_indian_phone(data.get('phone'))
        digits = _normal_phone(phone)
        otp = str(data.get('otp', '')).strip()
        if (not challenge or not challenge.get('otp_sent') or challenge.get('phone') != phone):
            self._send_json({'success': False, 'error': 'Request a new mobile verification code and try again.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        if not phone or len(digits) != 10 or digits[0] not in '6789' or not re.fullmatch(r'\d{4,8}', otp):
            self._send_json({'success': False, 'error': 'Enter your mobile number and the 4–8 digit SMS code.'}, 400,
                            extra_headers={'Cache-Control': 'no-store'})
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

        verified_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        conn = get_db()
        try:
            lock_transaction(conn)
            account = conn.scalar(select(CustomerAccount).where(
                CustomerAccount.phone == phone
            ).with_for_update())
            google_account = conn.scalar(select(CustomerAccount).where(
                CustomerAccount.google_sub == challenge['sub']
            ).with_for_update())
            if google_account and google_account.phone != phone:
                conn.rollback()
                self._send_json({'success': False, 'error': 'This Google account is already linked to another mobile number. Sign in with that number.'}, 409,
                                extra_headers={'Cache-Control': 'no-store'})
                return
            if account and account.google_sub and account.google_sub != challenge['sub']:
                conn.rollback()
                self._send_json({'success': False, 'error': 'This mobile number is linked to a different Google account.'}, 409,
                                extra_headers={'Cache-Control': 'no-store'})
                return
            email_owner = conn.scalar(select(CustomerAccount.phone).where(
                func.lower(CustomerAccount.email) == challenge['email'],
                CustomerAccount.phone != phone,
            ).limit(1))
            if email_owner:
                conn.rollback()
                self._send_json({'success': False, 'error': 'This Google email is already saved on another account. Sign in with that account’s mobile number.'}, 409,
                                extra_headers={'Cache-Control': 'no-store'})
                return
            if account is None:
                salt = secrets.token_bytes(16)
                password_hash = hashlib.pbkdf2_hmac('sha256', secrets.token_bytes(32), salt, 260_000).hex()
                account = CustomerAccount(
                    phone=phone,
                    name=challenge.get('name') or challenge['email'].split('@', 1)[0],
                    email=challenge['email'],
                    password_salt=salt.hex(),
                    password_hash=password_hash,
                    phone_verified_at=verified_at,
                    email_verified_at=verified_at,
                    google_sub=challenge['sub'],
                )
                conn.add(account)
            else:
                account.google_sub = challenge['sub']
                account.phone_verified_at = account.phone_verified_at or verified_at
                if not account.name:
                    account.name = challenge.get('name') or challenge['email'].split('@', 1)[0]
                if not account.email:
                    account.email = challenge['email']
                    account.email_verified_at = verified_at
                elif account.email.casefold() == challenge['email']:
                    account.email_verified_at = account.email_verified_at or verified_at
            conn.commit()
        except Exception as error:
            conn.rollback()
            if is_integrity_error(error):
                self._send_json({'success': False, 'error': 'This Google account or mobile number is already linked to another profile.'}, 409,
                                extra_headers={'Cache-Control': 'no-store'})
            else:
                self._send_json({'success': False, 'error': 'Could not finish sign-in. Please try again.'}, 500,
                                extra_headers={'Cache-Control': 'no-store'})
            return
        finally:
            conn.close()
        CUSTOMER_GOOGLE_LOGIN_CHALLENGES.pop(challenge_token, None)
        self._start_customer_session(phone)

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
            lock_transaction(conn)
            account = conn.scalar(select(CustomerAccount).where(
                CustomerAccount.phone == phone
            ).with_for_update())
            if purpose == 'register':
                if email and conn.scalar(select(CustomerAccount.phone).where(
                    func.lower(CustomerAccount.email) == email
                ).limit(1)):
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
                conn.add(CustomerAccount(
                    phone=phone, name=name, email=email, password_salt=salt.hex(),
                    password_hash=password_hash, phone_verified_at=verified_at,
                ))
            else:
                if not account:
                    conn.rollback()
                    conn.close()
                    self._send_json({'success': False, 'error': 'No account uses this number yet. Create an account first.'}, 404,
                                    extra_headers={'Cache-Control': 'no-store'})
                    return
                if not account.phone_verified_at:
                    account.phone_verified_at = verified_at
            conn.commit()
        except Exception as error:
            if not is_integrity_error(error):
                conn.rollback()
                conn.close()
                self._send_json({'success': False, 'error': 'Could not finish sign-in. Please try again.'}, 500,
                                extra_headers={'Cache-Control': 'no-store'})
                return
            conn.rollback()
            conn.close()
            self._send_json({'success': False, 'error': 'An account already uses this number. Choose Sign in instead.'}, 409,
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
            conn.add(CustomerAccount(phone=phone, name=name, email=email,
                                     password_salt=salt.hex(), password_hash=password_hash))
            conn.commit()
        except Exception as error:
            if not is_integrity_error(error):
                conn.close()
                self._send_json({'success': False, 'error': 'Your account could not be created. Please try again.'}, 500)
                return
            conn.close()
            self._send_json({'success': False, 'error': 'An account already uses this phone number. Sign in instead.'}, 409)
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
        row = conn.get(CustomerAccount, phone)
        conn.close()
        valid = False
        if row:
            try:
                actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(row.password_salt), 260_000).hex()
                valid = hmac.compare_digest(actual, row.password_hash)
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
        lock_transaction(conn)
        if email and conn.scalar(select(CustomerAccount.phone).where(
            func.lower(CustomerAccount.email) == email, CustomerAccount.phone != customer['phone']
        ).limit(1)):
            conn.close()
            self._send_json({'success': False, 'error': 'This email is already linked to another account.'}, 409,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        email_verified_at = customer.get('email_verified_at') if email == customer.get('email') else None
        account = conn.get(CustomerAccount, customer['phone'])
        if not account:
            conn.close()
            self._send_json({'success': False, 'error': 'Customer account not found.'}, 404)
            return
        account.name, account.email, account.email_verified_at = name, email, email_verified_at
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
            else:
                CUSTOMER_EMAIL_OTP_CHALLENGES[phone] = challenge
            self._send_json({'success': False, 'error': 'That email code is incorrect or has expired.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        verified_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        conn = get_db()
        account = conn.scalar(select(CustomerAccount).where(
            CustomerAccount.phone == phone, CustomerAccount.email == challenge['email']
        ).with_for_update())
        updated = account is not None
        if account:
            account.email_verified_at = verified_at
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
        accounts = conn.scalars(select(CustomerAccount.phone).where(
            func.lower(CustomerAccount.email) == email, CustomerAccount.email_verified_at.is_not(None)
        ).limit(2)).all()
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
            'phone': accounts[0],
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
            else:
                CUSTOMER_EMAIL_LOGIN_CHALLENGES[email_key] = challenge
            self._send_json({'success': False, 'error': 'That email code is incorrect or has expired.'}, 401,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        conn = get_db()
        account = conn.scalar(select(CustomerAccount).where(
            CustomerAccount.phone == challenge['phone'], func.lower(CustomerAccount.email) == email,
            CustomerAccount.email_verified_at.is_not(None),
        ))
        conn.close()
        CUSTOMER_EMAIL_LOGIN_CHALLENGES.pop(email_key, None)
        if not account:
            self._send_json({'success': False, 'error': 'This email is no longer verified on the account. Sign in by SMS to verify it again.'}, 409,
                            extra_headers={'Cache-Control': 'no-store'})
            return
        self._start_customer_session(account.phone)

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
            'Set-Cookie': f'bhadawar_staff={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_MAX_AGE}{self._secure_cookie_attribute()}'
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
            'Set-Cookie': f'bhadawar_staff={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_MAX_AGE}{self._secure_cookie_attribute()}'
        })

    def handle_staff_logout(self):
        staff_cookie = self.headers.get('Cookie', '')
        token = next((part.strip().split('=', 1)[1] for part in staff_cookie.split(';')
                      if part.strip().startswith('bhadawar_staff=')), '')
        session = STAFF_SESSIONS.get(token)
        if session and session.get('role') == 'delivery':
            conn = get_db()
            lock_transaction(conn)
            rider = conn.get(DeliveryRider, session['username'])
            if rider:
                rider.is_available = 0
                rider.updated_at = datetime.utcnow()
            conn.execute(update(Order).where(
                Order.delivery_rider == session['username'], Order.status == 'ready_for_pickup'
            ).values(delivery_rider=None))
            self._assign_waiting_delivery_orders(conn)
            conn.commit()
            conn.close()
        STAFF_SESSIONS.pop(token, None)
        self._send_json({'success': True}, extra_headers={
            'Set-Cookie': f'bhadawar_staff=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0{self._secure_cookie_attribute()}'
        })
