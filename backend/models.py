"""SQLAlchemy schema for persistent Bhadawar application data."""
from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column("desc", Text)
    veg = Column(Integer, server_default=text("1"))
    spice = Column(String, server_default=text("'Mild'"))
    popular = Column(Integer, server_default=text("60"))
    tag = Column(String)
    emoji = Column(String)
    photo = Column(Text)
    available = Column(Integer, server_default=text("1"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class CorporateMenuItem(Base):
    __tablename__ = "corporate_menu"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column("desc", Text)
    unit_label = Column(String)
    min_qty = Column(Integer, server_default=text("1"))
    emoji = Column(String)
    veg = Column(Integer, server_default=text("1"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True)
    customer_name = Column(Text)
    customer_phone = Column(Text)
    delivery_address = Column(Text)
    order_type = Column(String, server_default=text("'delivery'"))
    payment_method = Column(String)
    subtotal = Column(Float)
    delivery_fee = Column(Float)
    tax = Column(Float)
    discount = Column(Float)
    points_used = Column(Integer, server_default=text("0"))
    total_amount = Column(Float)
    status = Column(String, server_default=text("'received'"))
    items_json = Column(Text)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    delivery_latitude = Column(Float)
    delivery_longitude = Column(Float)
    cod_status = Column(String, nullable=False, server_default=text("'not_applicable'"))
    cod_collected_via = Column(String)
    cod_collected_amount = Column(Float, nullable=False, server_default=text("0"))
    delivery_instructions = Column(Text)
    rider_feedback = Column(Text)
    issue_note = Column(Text)
    delivery_rider = Column(String)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(String, primary_key=True)
    booking_type = Column(String)
    customer_name = Column(Text, nullable=False)
    customer_phone = Column(Text, nullable=False)
    booking_date = Column(String, nullable=False)
    booking_time = Column(String, nullable=False)
    guest_count = Column(Integer, nullable=False)
    notes = Column(Text)
    status = Column(String, server_default=text("'confirmed'"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    deposit_amount = Column(Float, nullable=False, server_default=text("0"))
    payment_status = Column(String, nullable=False, server_default=text("'not_required'"))
    razorpay_order_id = Column(String)
    razorpay_payment_id = Column(String)
    final_bill = Column(Float)
    balance_due = Column(Float)
    refund_due = Column(Float)
    settled_at = Column(String)


class FoodStory(Base):
    __tablename__ = "food_stories"
    id = Column(String, primary_key=True)
    author = Column(Text, nullable=False)
    phone = Column(Text)
    dish = Column(Text, nullable=False)
    dish_id = Column(String)
    rating = Column(Integer, server_default=text("5"))
    text = Column(Text, nullable=False)
    photo = Column(Text)
    media_type = Column(String, server_default=text("'image'"))
    pts = Column(Integer, server_default=text("1"))
    order_above_599 = Column(Integer, server_default=text("0"))
    status = Column(String, server_default=text("'approved'"))
    likes = Column(Integer, server_default=text("0"))
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    order_id = Column(String)
    story_rewarded = Column(Integer, nullable=False, server_default=text("0"))
    bonus_rewarded = Column(Integer, nullable=False, server_default=text("0"))


Index(
    "idx_food_stories_order_id",
    FoodStory.order_id,
    unique=True,
    postgresql_where=FoodStory.order_id.is_not(None),
    sqlite_where=FoodStory.order_id.is_not(None),
)


class WalletAccount(Base):
    __tablename__ = "wallet_accounts"
    phone = Column(String, primary_key=True)
    customer_name = Column(Text)
    balance = Column(Integer, server_default=text("100"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String, ForeignKey("wallet_accounts.phone"), nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    label = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    rating = Column(Integer, server_default=text("5"))
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class CustomerAccount(Base):
    __tablename__ = "customer_accounts"
    phone = Column(String, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, server_default=text("''"))
    password_salt = Column(Text, nullable=False)
    password_hash = Column(Text, nullable=False)
    phone_verified_at = Column(String)
    email_verified_at = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class DeliveryRider(Base):
    __tablename__ = "delivery_riders"
    username = Column(String, primary_key=True)
    is_available = Column(Integer, nullable=False, server_default=text("0"))
    updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


Index(
    "idx_bookings_razorpay_order",
    Booking.razorpay_order_id,
    unique=True,
    postgresql_where=Booking.razorpay_order_id.is_not(None),
    sqlite_where=Booking.razorpay_order_id.is_not(None),
)
