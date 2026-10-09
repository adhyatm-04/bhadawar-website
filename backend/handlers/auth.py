"""Auth request handlers."""
from backend.runtime import *

class AuthHandlers:
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
        except Exception as error:
            if not is_integrity_error(error):
                conn.close()
                self._send_json({'success': False, 'error': 'Your account could not be created. Please try again.'}, 500)
                return
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
            else:
                CUSTOMER_EMAIL_OTP_CHALLENGES[phone] = challenge
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
            else:
                CUSTOMER_EMAIL_LOGIN_CHALLENGES[email_key] = challenge
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
