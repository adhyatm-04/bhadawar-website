"""Community request handlers."""
from backend.runtime import *
from datetime import datetime
from sqlalchemy import case, func, select, update
from backend.database import lock_transaction, model_to_dict
from backend.models import Booking, FoodStory, Order, Review, WalletAccount, WalletTransaction

class CommunityHandlers:
    def handle_get_stories(self, query):
        status_filter = query.get('status', ['approved'])[0]
        if status_filter != 'approved' and not self._require_role('admin'):
            return
        conn = get_db()
        rows = [model_to_dict(row) for row in conn.scalars(
            select(FoodStory).where(FoodStory.status == status_filter).order_by(FoodStory.created_at.desc())
        )]
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
            lock_transaction(conn)
            if order_id:
                order = conn.get(Order, order_id)
                if (not order or _normal_phone(order.customer_phone) != _normal_phone(phone)
                        or str(order.status).lower() not in ('delivered', 'completed')
                        or float(order.subtotal or 0) <= 599):
                    conn.close()
                    self._send_json({"success": False, "error": "Only your completed orders with a food subtotal above ₹599 can be linked."}, 400)
                    return
                if conn.scalar(select(FoodStory.id).where(FoodStory.order_id == order_id)):
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
            conn.add(FoodStory(
                id=story_id, author=author, phone=phone, dish=dish, dish_id=dish_id,
                rating=rating, text=text, photo=relative_media, media_type=media_type,
                pts=1, order_above_599=1 if order_id else 0, order_id=order_id, status='pending',
            ))
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
        lock_transaction(conn)
        story = conn.scalar(select(FoodStory).where(FoodStory.id == story_id).with_for_update())
        if not story:
            conn.close()
            self._send_json({"error": "Story not found"}, 404)
            return

        if story.status != 'pending':
            conn.close()
            self._send_json({"success": False, "error": "Only pending stories can be approved."}, 409)
            return
        story.status, story.pts, story.story_rewarded = 'approved', 1, 1
        phone = story.phone
        wallet = conn.get(WalletAccount, phone)
        if not wallet:
            wallet = WalletAccount(phone=phone, customer_name=story.author, balance=0)
            conn.add(wallet)
            conn.flush()
        wallet.balance = int(wallet.balance or 0) + 1
        conn.add(WalletTransaction(phone=phone, type='credit', amount=1, label=f"Food Story Approved: {story.dish}"))
        bonus = self._award_order_bonus(conn, story.order_id)
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
        lock_transaction(conn)
        story = conn.scalar(select(FoodStory).where(FoodStory.id == story_id).with_for_update())
        if not story or story.status != 'pending':
            conn.close()
            self._send_json({"success": False, "error": "Only pending stories can be rejected."}, 409)
            return
        story.status = 'rejected'
        conn.commit()
        conn.close()
        self._send_json({"success": True, "message": "Story rejected."})

    def handle_like_story(self):
        data = self._read_json_body()
        story_id = data.get('story_id')
        conn = get_db()
        delta = 1 if data.get('liked') else -1
        result = conn.execute(update(FoodStory).where(
            FoodStory.id == story_id, FoodStory.status == 'approved'
        ).values(likes=case((FoodStory.likes + delta < 0, 0), else_=FoodStory.likes + delta)))
        if result.rowcount == 0:
            conn.close()
            self._send_json({"success": False, "error": "Approved story not found."}, 404)
            return
        likes = conn.scalar(select(FoodStory.likes).where(FoodStory.id == story_id))
        conn.commit()
        conn.close()
        self._send_json({"success": True, "likes": likes})

    def handle_get_leaderboard(self, query):
        conn = get_db()
        def rankings(monthly=False):
            stmt = select(
                FoodStory.author.label('name'), func.count(FoodStory.id).label('blogs'),
                func.sum(FoodStory.pts).label('points'),
            ).where(FoodStory.status == 'approved')
            if monthly:
                now = datetime.utcnow()
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                stmt = stmt.where(FoodStory.created_at >= month_start)
            stmt = stmt.group_by(FoodStory.author).order_by(
                func.count(FoodStory.id).desc(), func.sum(FoodStory.pts).desc(), func.lower(FoodStory.author).asc()
            )
            result = []
            for i, row in enumerate(conn.execute(stmt)):
                row_name = row.name
                result.append({
                    "rank": i + 1,
                    "name": row_name,
                    "avatar": row_name[0].upper() if row_name else 'F',
                    "blogs": row.blogs,
                    "points": row.points or 0,
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
        accounts = conn.scalars(select(WalletAccount)).all()
        acc = next((row for row in accounts if _normal_phone(row.phone) == _normal_phone(phone)), None)
        wallet_phone = acc.phone if acc else phone
        txs = [model_to_dict(row) for row in conn.scalars(
            select(WalletTransaction).where(WalletTransaction.phone == wallet_phone)
            .order_by(WalletTransaction.created_at.desc()).limit(20)
        )]
        conn.close()

        balance = acc.balance if acc else 0
        name = acc.customer_name if acc else 'Bhadawar Guest'

        self._send_json({
            "success": True,
            "phone": phone,
            "name": name,
            "balance": balance,
            "transactions": txs
        })

    def handle_get_reviews(self):
        conn = get_db()
        rows = [model_to_dict(row) for row in conn.scalars(select(Review).order_by(Review.created_at.desc()))]
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
        conn.add(Review(name=name, rating=rating, review_text=text))
        conn.commit()
        conn.close()
        self._send_json({"success": True, "message": "Feedback saved for the restaurant team."})

    def handle_get_stats(self):
        if not self._require_role('admin'):
            return
        conn = get_db()
        orders_count = conn.scalar(select(func.count(Order.id))) or 0
        bookings_count = conn.scalar(select(func.count(Booking.id))) or 0
        published_stories = conn.scalar(select(func.count(FoodStory.id)).where(FoodStory.status == 'approved')) or 0
        pending_stories = conn.scalar(select(func.count(FoodStory.id)).where(FoodStory.status == 'pending')) or 0
        conn.close()

        self._send_json({
            "success": True,
            "orders": orders_count,
            "bookings": bookings_count,
            "published_stories": published_stories,
            "pending_stories": pending_stories
        })
