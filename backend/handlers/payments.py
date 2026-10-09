"""Payments request handlers."""
from backend.runtime import *
from sqlalchemy import select
from backend.database import lock_transaction, model_to_dict
from backend.models import Booking

class PaymentsHandlers:
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
            conn.add(Booking(
                id=booking_id, booking_type=booking_type, customer_name=name, customer_phone=phone,
                booking_date=date, booking_time=time, guest_count=guests,
                notes='Dine-in table reservation' if booking_type == 'dine' else 'Parties & Gatherings',
                status='payment_pending', deposit_amount=deposit, payment_status='pending',
            ))
            conn.commit()
            conn.close()
            try:
                order = self._razorpay_call('POST', 'orders', {
                    'amount': deposit * 100, 'currency': 'INR', 'receipt': booking_id,
                    'notes': {'booking_id': booking_id, 'booking_type': booking_type, 'guest_count': str(guests)}
                })
            except Exception:
                conn = get_db()
                booking = conn.get(Booking, booking_id)
                if booking:
                    booking.status = 'payment_failed'
                    booking.payment_status = 'failed'
                conn.commit()
                conn.close()
                raise
            conn = get_db()
            booking = conn.get(Booking, booking_id)
            if booking:
                booking.razorpay_order_id = order['id']
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
        booking = conn.get(Booking, booking_id)
        if not booking or booking.booking_type not in ('party', 'dine'):
            conn.close()
            return False, 'Booking was not found.'
        expected = hmac.new(RAZORPAY_KEY_SECRET.encode(), f'{order_id}|{payment_id}'.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            conn.close()
            return False, 'Payment signature could not be verified.'
        if booking.payment_status == 'paid':
            conn.close()
            return (booking.razorpay_payment_id == payment_id), 'This booking payment was already confirmed.'
        if booking.razorpay_order_id != order_id:
            conn.close()
            return False, 'Payment does not match this booking.'
        try:
            payment = self._razorpay_call('GET', f'payments/{urllib.parse.quote(payment_id)}')
        except Exception as error:
            conn.close()
            return False, f'Could not confirm payment status: {error}'
        expected_paise = int(round(float(booking.deposit_amount) * 100))
        if payment.get('order_id') != order_id or payment.get('currency') != 'INR' or int(payment.get('amount', 0)) != expected_paise or payment.get('status') != 'captured':
            conn.close()
            return False, 'Payment is not captured for the correct booking amount.'
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.razorpay_payment_id = payment_id
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
                    row = conn.scalar(select(Booking.id).where(
                        Booking.razorpay_order_id == order_id, Booking.payment_status == 'pending'
                    ))
                    conn.close()
                    if row:
                        # Reuse the provider API fetch and amount checks before confirming.
                        conn = get_db()
                        booking = conn.get(Booking, row)
                        booking_data = model_to_dict(booking) if booking else None
                        conn.close()
                        # Webhooks use their own signature; verify the fetched payment and stored order instead.
                        payment = self._razorpay_call('GET', f'payments/{urllib.parse.quote(payment_id)}')
                        if (booking_data and payment.get('order_id') == order_id and payment.get('currency') == 'INR'
                                and int(payment.get('amount', 0)) == int(round(float(booking_data['deposit_amount']) * 100))
                                and payment.get('status') == 'captured'):
                            conn = get_db()
                            booking = conn.get(Booking, row)
                            if booking and booking.payment_status == 'pending':
                                booking.payment_status = 'paid'
                                booking.status = 'confirmed'
                                booking.razorpay_payment_id = payment_id
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
        lock_transaction(conn)
        booking = conn.scalar(select(Booking).where(
            Booking.id == booking_id, Booking.booking_type == 'party'
        ).with_for_update())
        if not booking:
            conn.close()
            self._send_json({'success': False, 'error': 'Party booking was not found.'}, 404)
            return
        if booking.payment_status != 'paid':
            conn.close()
            self._send_json({'success': False, 'error': 'Only a paid party booking can be settled.'}, 409)
            return
        if booking.final_bill is not None:
            conn.close()
            self._send_json({'success': False, 'error': 'This booking has already been settled.'}, 409)
            return
        deposit = float(booking.deposit_amount or 0)
        due = max(0, round(final_bill - deposit, 2))
        refund = max(0, round(deposit - final_bill, 2))
        booking.final_bill = final_bill
        booking.balance_due = due
        booking.refund_due = refund
        booking.settled_at = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'final_bill': final_bill, 'deposit_credit': deposit, 'balance_due': due,
                         'refund_due': refund, 'message': 'Party bill settled.'})
