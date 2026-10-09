"""Orders request handlers."""
from backend.runtime import *

class OrdersHandlers:
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
        cursor.execute("INSERT INTO wallet_accounts (phone, customer_name, balance) VALUES (?, ?, 0) ON CONFLICT (phone) DO NOTHING",
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
            if DATABASE_URL:
                today_match = "CAST(created_at + INTERVAL '5 hours 30 minutes' AS DATE) = CAST(CURRENT_TIMESTAMP + INTERVAL '5 hours 30 minutes' AS DATE)"
            else:
                today_match = "date(created_at, '+5 hours', '+30 minutes') = date('now', '+5 hours', '+30 minutes')"
            today = cursor.execute(f"""SELECT
                SUM(CASE WHEN {today_match} THEN 1 ELSE 0 END) AS received_today,
                SUM(CASE WHEN status = 'cancelled' AND {today_match} THEN 1 ELSE 0 END) AS cancelled_today,
                SUM(CASE WHEN status IN ('delivered', 'completed') AND {today_match} THEN 1 ELSE 0 END) AS completed_today,
                SUM(CASE WHEN lower(payment_method) IN ('cod', 'cash on delivery') AND cod_status = 'collected' AND cod_collected_via = 'cash' AND {today_match} THEN cod_collected_amount ELSE 0 END) AS cod_cash_today,
                SUM(CASE WHEN lower(payment_method) IN ('cod', 'cash on delivery') AND cod_status = 'collected' AND cod_collected_via = 'upi' AND {today_match} THEN cod_collected_amount ELSE 0 END) AS cod_upi_today,
                SUM(CASE WHEN lower(payment_method) NOT IN ('cod', 'cash on delivery', 'invoice', 'cash') AND {today_match} THEN total_amount ELSE 0 END) AS online_selected_today,
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
        stale_cutoff = "CURRENT_TIMESTAMP - INTERVAL '2 minutes'" if DATABASE_URL else "datetime('now', '-2 minutes')"
        stale_riders = cursor.execute(f"SELECT username FROM delivery_riders WHERE is_available = 1 AND updated_at < {stale_cutoff}").fetchall()
        if stale_riders:
            cursor.execute(f"UPDATE delivery_riders SET is_available = 0 WHERE is_available = 1 AND updated_at < {stale_cutoff}")
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
