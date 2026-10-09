"""Bookings request handlers."""
from backend.runtime import *

class BookingsHandlers:
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
