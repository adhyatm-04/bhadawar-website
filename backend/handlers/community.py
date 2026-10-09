"""Community request handlers."""
from backend.runtime import *

class CommunityHandlers:
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
        cursor.execute("INSERT INTO wallet_accounts (phone, customer_name, balance) VALUES (?, ?, 0) ON CONFLICT (phone) DO NOTHING", (phone, story['author']))
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
        likes_expression = 'GREATEST(0, likes + ?)' if DATABASE_URL else 'MAX(0, likes + ?)'
        cursor.execute(f"UPDATE food_stories SET likes = {likes_expression} WHERE id = ? AND status = 'approved'", (delta, story_id))
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
            month_start = "date_trunc('month', CURRENT_TIMESTAMP)" if DATABASE_URL else "date('now', 'start of month')"
            month_filter = f" AND created_at >= {month_start}" if monthly else ''
            name_sort = "lower(author) ASC" if DATABASE_URL else "author COLLATE NOCASE ASC"
            cursor.execute(f"""
                SELECT author AS name, COUNT(*) AS blogs, SUM(pts) AS points
                FROM food_stories WHERE status = 'approved'{month_filter}
                GROUP BY author ORDER BY blogs DESC, points DESC, {name_sort}
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
