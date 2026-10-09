"""Orders request handlers."""
from backend.runtime import *
from datetime import timedelta
from sqlalchemy import and_, case, func, or_, select, update
from backend.database import lock_transaction, model_to_dict
from backend.models import DeliveryRider, FoodStory, Order, WalletAccount, WalletTransaction


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
            conn.add(Order(
                id=order_id, customer_name=name, customer_phone=phone, delivery_address=event_description,
                order_type='corporate', payment_method='invoice', subtotal=subtotal, delivery_fee=0,
                tax=0, discount=discount, points_used=0, total_amount=subtotal - discount,
                status='received', items_json=items_json,
            ))
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
        lock_transaction(conn)
        order = conn.scalar(select(Order).where(Order.id == order_id).with_for_update())
        if not order:
            conn.close()
            self._send_json({'success': False, 'error': 'Order not found.'}, 404)
            return
        current = order.status or 'received'
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
            if order.order_type != 'delivery' or order.delivery_rider != staff['username'] or status not in ('picked_up', 'delivered'):
                valid_transition = False
            if status == 'delivered' and str(order.payment_method or '').lower() in ('cod', 'cash on delivery') and order.cod_status not in ('collected', 'not_collected'):
                conn.close()
                self._send_json({'success': False, 'error': 'Record whether COD was collected before marking delivery complete.'}, 409)
                return
        if not valid_transition:
            conn.close()
            self._send_json({'success': False, 'error': 'That order step is not available for your role or the current order status.'}, 409)
            return
        order.status = status
        if status == 'ready_for_pickup' and order.order_type == 'delivery':
            self._assign_waiting_delivery_orders(conn)
        bonus = self._award_order_bonus(conn, order_id) if status == 'delivered' else 0
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
        lock_transaction(conn)
        order = conn.scalar(select(Order).where(Order.id == order_id).with_for_update())
        if not order:
            conn.close()
            self._send_json({'success': False, 'error': 'Order not found.'}, 404)
            return
        if order.order_type != 'delivery' or str(order.payment_method or '').lower() not in ('cod', 'cash on delivery'):
            conn.close()
            self._send_json({'success': False, 'error': 'This order does not require delivery COD collection.'}, 409)
            return
        if order.delivery_rider != staff['username']:
            conn.close()
            self._send_json({'success': False, 'error': 'This delivery is assigned to another rider.'}, 403)
            return
        if order.status not in ('picked_up', 'delivered'):
            conn.close()
            self._send_json({'success': False, 'error': 'COD can be confirmed after the rider picks up the order.'}, 409)
            return
        if cod_status == 'collected':
            collection_method = str(data.get('collection_method', '')).strip().lower()
            if collection_method not in ('cash', 'upi'):
                conn.close()
                self._send_json({'success': False, 'error': 'Choose whether the customer paid cash or UPI.'}, 400)
                return
            order.cod_status = cod_status
            order.cod_collected_via = collection_method
            order.cod_collected_amount = order.total_amount
        else:
            order.cod_status = cod_status
            order.cod_collected_via = None
            order.cod_collected_amount = 0
        conn.commit()
        conn.close()
        self._send_json({'success': True, 'cod_status': cod_status,
                         'collection_method': collection_method if cod_status == 'collected' else None,
                         'amount': float(order.total_amount or 0) if cod_status == 'collected' else 0,
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
        cursor = conn.execute(update(Order).where(
            Order.id == order_id, Order.delivery_rider == staff['username'], Order.order_type == 'delivery',
            Order.status.in_(('picked_up', 'delivered')),
        ).values(rider_feedback=feedback))
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
        cursor = conn.execute(update(Order).where(Order.id == order_id).values(issue_note=note or None))
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

    def _award_order_bonus(self, conn, order_id):
        if not order_id:
            return 0
        pair = conn.execute(select(FoodStory, Order).join(
            Order, Order.id == FoodStory.order_id
        ).where(FoodStory.order_id == order_id).with_for_update()).first()
        if not pair:
            return 0
        story, order = pair
        if (story.status != 'approved' or story.bonus_rewarded
                or str(order.status).lower() not in ('delivered', 'completed')
                or float(order.subtotal or 0) <= 599):
            return 0
        phone = story.phone
        wallet = conn.get(WalletAccount, phone) if phone else None
        if not wallet:
            wallet = WalletAccount(phone=phone, customer_name=story.author, balance=0)
            conn.add(wallet)
            conn.flush()
        wallet.balance = int(wallet.balance or 0) + 2
        conn.add(WalletTransaction(phone=phone, type='credit', amount=2,
                                   label=f"Completed order bonus: #{order_id}"))
        story.bonus_rewarded = 1
        story.pts = int(story.pts or 0) + 2
        story.order_above_599 = 1
        return 2

    def handle_get_orders(self, query):
        staff = self._staff()
        if not staff:
            self._require_role()
            return
        conn = get_db()
        if staff['role'] == 'delivery':
            lock_transaction(conn)
            self._assign_waiting_delivery_orders(conn)
            conn.commit()
        summary = None
        if staff['role'] == 'admin':
            local_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
            local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            day_start = local_midnight - timedelta(hours=5, minutes=30)
            day_end = day_start + timedelta(days=1)
            today_match = and_(Order.created_at >= day_start, Order.created_at < day_end)
            cod_payment = func.lower(Order.payment_method).in_(('cod', 'cash on delivery'))
            issue = or_(and_(Order.issue_note.is_not(None), func.trim(Order.issue_note) != ''),
                        Order.status == 'cancelled',
                        and_(cod_payment, Order.cod_status.in_(('not_collected', 'not_confirmed'))))
            stats_stmt = select(
                func.sum(case((today_match, 1), else_=0)).label('received_today'),
                func.sum(case((and_(Order.status == 'cancelled', today_match), 1), else_=0)).label('cancelled_today'),
                func.sum(case((and_(Order.status.in_(('delivered', 'completed')), today_match), 1), else_=0)).label('completed_today'),
                func.sum(case((and_(cod_payment, Order.cod_status == 'collected', Order.cod_collected_via == 'cash', today_match), Order.cod_collected_amount), else_=0)).label('cod_cash_today'),
                func.sum(case((and_(cod_payment, Order.cod_status == 'collected', Order.cod_collected_via == 'upi', today_match), Order.cod_collected_amount), else_=0)).label('cod_upi_today'),
                func.sum(case((and_(func.lower(Order.payment_method).not_in(('cod', 'cash on delivery', 'invoice', 'cash')), today_match), Order.total_amount), else_=0)).label('online_selected_today'),
                func.sum(case((issue, 1), else_=0)).label('issue_count'),
            )
            today = conn.execute(stats_stmt).one()._mapping
            summary = {key: (float(value or 0) if key.startswith(('cod_', 'online_')) else int(value or 0)) for key, value in today.items()}
            rows = conn.scalars(select(Order).where(
                func.lower(Order.status).in_(('delivered', 'completed', 'cancelled'))
            ).order_by(Order.created_at.desc()).limit(200)).all()
        elif staff['role'] == 'kitchen':
            rows = conn.scalars(select(Order).where(
                Order.status.in_(('received', 'accepted', 'preparing'))
            ).order_by(Order.created_at.desc()).limit(100)).all()
        else:
            rows = conn.scalars(select(Order).where(
                Order.order_type == 'delivery', Order.delivery_rider == staff['username'],
                Order.status.in_(('ready_for_pickup', 'picked_up', 'delivered')),
            ).order_by(Order.created_at.desc()).limit(100)).all()
        rows = [model_to_dict(row) for row in rows]
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

    def _assign_waiting_delivery_orders(self, conn):
        stale_cutoff = datetime.utcnow() - timedelta(minutes=2)
        stale_riders = conn.scalars(select(DeliveryRider).where(
            DeliveryRider.is_available == 1, DeliveryRider.updated_at < stale_cutoff
        ).with_for_update()).all()
        if stale_riders:
            for rider in stale_riders:
                rider.is_available = 0
            unavailable = conn.scalars(select(DeliveryRider.username).where(DeliveryRider.is_available == 0)).all()
            if unavailable:
                conn.execute(update(Order).where(
                    Order.status == 'ready_for_pickup', Order.delivery_rider.in_(unavailable)
                ).values(delivery_rider=None))
        waiting = conn.scalars(select(Order).where(
            Order.order_type == 'delivery', Order.status == 'ready_for_pickup', Order.delivery_rider.is_(None)
        ).order_by(Order.created_at.asc(), Order.id.asc()).with_for_update()).all()
        available = conn.scalars(select(DeliveryRider).where(DeliveryRider.is_available == 1)).all()
        active_counts = dict(conn.execute(select(Order.delivery_rider, func.count(Order.id)).where(
            Order.delivery_rider.is_not(None), Order.status.in_(('ready_for_pickup', 'picked_up'))
        ).group_by(Order.delivery_rider)).all())
        for waiting_order in waiting:
            if not available:
                break
            rider = min(available, key=lambda item: (active_counts.get(item.username, 0), item.updated_at, item.username))
            waiting_order.delivery_rider = rider.username
            active_counts[rider.username] = active_counts.get(rider.username, 0) + 1

    def handle_get_rider_availability(self):
        staff = self._require_role('admin', 'delivery')
        if not staff:
            return
        conn = get_db()
        lock_transaction(conn)
        self._assign_waiting_delivery_orders(conn)
        conn.commit()
        rider_records = conn.scalars(select(DeliveryRider).order_by(DeliveryRider.username)).all()
        active_counts = dict(conn.execute(select(Order.delivery_rider, func.count(Order.id)).where(
            Order.delivery_rider.is_not(None), Order.status.in_(('ready_for_pickup', 'picked_up'))
        ).group_by(Order.delivery_rider)).all())
        riders = [dict(model_to_dict(rider), active_assignments=active_counts.get(rider.username, 0)) for rider in rider_records]
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
        lock_transaction(conn)
        rider = conn.get(DeliveryRider, staff['username'])
        if not rider:
            rider = DeliveryRider(username=staff['username'])
            conn.add(rider)
        rider.is_available = 1 if available else 0
        rider.updated_at = datetime.utcnow()
        if not available:
            conn.execute(update(Order).where(
                Order.delivery_rider == staff['username'], Order.status == 'ready_for_pickup'
            ).values(delivery_rider=None))
        self._assign_waiting_delivery_orders(conn)
        conn.commit()
        active = conn.scalar(select(func.count(Order.id)).where(
            Order.delivery_rider == staff['username'], Order.status.in_(('ready_for_pickup', 'picked_up'))
        )) or 0
        available_count = conn.scalar(select(func.count(DeliveryRider.username)).where(DeliveryRider.is_available == 1)) or 0
        conn.close()
        self._send_json({'success': True, 'is_available': available, 'available_riders': available_count,
                         'active_assignments': active, 'message': 'Availability updated. Ready orders are assigned to available riders.'})

    def handle_get_customer_order_history(self, query):
        customer = self._customer()
        if not customer:
            self._send_json({'success': False, 'error': 'Sign in to view your order history.'}, 401)
            return
        conn = get_db()
        rows = [model_to_dict(row) for row in conn.scalars(
            select(Order).order_by(Order.created_at.desc()).limit(500)
        ) if _normal_phone(row.customer_phone) == _normal_phone(customer['phone'])]
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
        row = conn.scalar(select(Order).where(func.upper(Order.id) == order_id))
        conn.close()
        if not row or _normal_phone(row.customer_phone) != phone:
            self._send_json({'success': False, 'error': 'We could not find an order matching those details.'}, 404)
            return
        self._send_json({'success': True, 'order': {
            'id': row.id, 'order_type': row.order_type, 'status': row.status,
            'created_at': model_to_dict(row)['created_at'], 'total_amount': row.total_amount
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
            lock_transaction(conn)
            existing_phones = conn.scalars(select(Order.customer_phone).where(Order.order_type != 'corporate')).all()
            first_order = not any(_normal_phone(phone_value) == _normal_phone(customer_phone) for phone_value in existing_phones)
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
                accounts = conn.scalars(select(WalletAccount).with_for_update()).all()
                wallet_account = next((row for row in accounts if _normal_phone(row.phone) == _normal_phone(customer_phone)), None)
                wallet_balance = int(wallet_account.balance or 0) if wallet_account else 0
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
            conn.add(Order(
                id=order_id, customer_name=customer_name, customer_phone=customer_phone,
                delivery_address=delivery_address, delivery_latitude=delivery_latitude,
                delivery_longitude=delivery_longitude, delivery_instructions=delivery_instructions,
                order_type=order_type, payment_method=payment_method, subtotal=totals['subtotal'],
                delivery_fee=totals['delivery_fee'], tax=totals['tax'], discount=totals['discount'],
                points_used=points_used, total_amount=totals['total_amount'], status='received',
                items_json=items_json, cod_status='pending' if payment_method == 'cod' else 'not_applicable',
            ))

            if points_used:
                wallet_account.balance = int(wallet_account.balance or 0) - points_used
                wallet_account.updated_at = datetime.utcnow()
                conn.add(WalletTransaction(
                    phone=wallet_account.phone, type='debit', amount=points_used,
                    label=f'Redeemed on Order #{order_id}',
                ))
                wallet_balance_after = int(wallet_account.balance)
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
        lock_transaction(conn)
        order = conn.scalar(select(Order).where(Order.id == order_id).with_for_update())
        if not order:
            conn.close()
            self._send_json({"success": False, "error": "Order not found."}, 404)
            return
        if str(order.status).lower() == 'cancelled':
            conn.close()
            self._send_json({"success": False, "error": "Cancelled orders cannot be completed."}, 409)
            return
        order.status = 'delivered'
        bonus = self._award_order_bonus(conn, order_id)
        conn.commit()
        conn.close()
        message = 'Order marked completed.' + (f' +{bonus} feedback bonus points added.' if bonus else '')
        self._send_json({"success": True, "bonus_points_awarded": bonus, "message": message})
