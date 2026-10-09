"""Bookings request handlers."""
from backend.runtime import *
from sqlalchemy import select
from backend.database import model_to_dict
from backend.models import Booking

class BookingsHandlers:
    def handle_get_bookings(self, query):
        if not self._require_role('admin'):
            return
        conn = get_db()
        rows = [model_to_dict(row) for row in conn.scalars(
            select(Booking).order_by(Booking.created_at.desc()).limit(50)
        )]
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
        conn.add(Booking(
            id=booking_id, booking_type=booking_type, customer_name=name,
            customer_phone=phone, booking_date=date, booking_time=time,
            guest_count=guests, notes=notes,
        ))
        conn.commit()
        conn.close()
        self._send_json({"success": True, "booking_id": booking_id, "message": "Reservation saved"})
