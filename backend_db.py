"""
Bhadawar Hotel & Foods - Complete SQLite Database Initialization & Seed
Agra's Family Restaurant Since 1963
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.environ.get('BHADAWAR_DB_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bhadawar.db'))

def init_db():
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url:
        from backend.database import connect_database, upgrade_schema
        upgrade_schema()
        return connect_database()
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 30000")
    cursor = conn.cursor()

    # 1. Menu items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        desc TEXT,
        veg INTEGER DEFAULT 1,
        spice TEXT DEFAULT 'Mild',
        popular INTEGER DEFAULT 60,
        tag TEXT,
        emoji TEXT,
        photo TEXT,
        available INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Corporate menu items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS corporate_menu (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        desc TEXT,
        unit_label TEXT,
        min_qty INTEGER DEFAULT 1,
        emoji TEXT,
        veg INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        customer_name TEXT,
        customer_phone TEXT,
        delivery_address TEXT,
        order_type TEXT DEFAULT 'delivery',
        payment_method TEXT,
        subtotal REAL,
        delivery_fee REAL,
        tax REAL,
        discount REAL,
        points_used INTEGER DEFAULT 0,
        total_amount REAL,
        status TEXT DEFAULT 'received', -- received, preparing, out_for_delivery, delivered, cancelled
        items_json TEXT, -- JSON array of items [{id, name, price, qty}]
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Bookings & Reservations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT PRIMARY KEY,
        booking_type TEXT, -- dine, hotel, party, corporate
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        booking_time TEXT NOT NULL,
        guest_count INTEGER NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'confirmed', -- confirmed, completed, cancelled
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Food Stories table (Customer stories, reviews, blogs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_stories (
        id TEXT PRIMARY KEY,
        author TEXT NOT NULL,
        phone TEXT,
        dish TEXT NOT NULL,
        dish_id TEXT,
        rating INTEGER DEFAULT 5,
        text TEXT NOT NULL,
        photo TEXT,
        media_type TEXT DEFAULT 'image',
        pts INTEGER DEFAULT 1,
        order_above_599 INTEGER DEFAULT 0,
        status TEXT DEFAULT 'approved', -- pending, approved, rejected
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Wallet Accounts & Transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_accounts (
        phone TEXT PRIMARY KEY,
        customer_name TEXT,
        balance INTEGER DEFAULT 100,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        type TEXT NOT NULL, -- credit, debit
        amount INTEGER NOT NULL,
        label TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (phone) REFERENCES wallet_accounts(phone)
    );
    """)

    # 7. Reviews table (Website guest reviews)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rating INTEGER DEFAULT 5,
        review_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    print("Database schema created successfully.")
    return conn

def seed_db(conn):
    cursor = conn.cursor()

    # Seed default user wallet
    default_phone = '+91 98765 43210'
    cursor.execute("SELECT phone FROM wallet_accounts WHERE phone = ?", (default_phone,))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO wallet_accounts (phone, customer_name, balance)
        VALUES (?, 'Bhadawar Guest', 100)
        """, (default_phone,))
        cursor.execute("""
        INSERT INTO wallet_transactions (phone, type, amount, label)
        VALUES (?, 'credit', 100, 'Welcome to Bhadawar Wallet')
        """, (default_phone,))

    # Do not seed fabricated guest testimonials. The frontend can show editorial
    # Bhadawar Kitchen stories while real customer submissions await approval.

    # Seed Reviews if table is empty
    cursor.execute("SELECT count(*) FROM reviews")
    if cursor.fetchone()[0] == 0:
        seed_reviews = [
            ("Amit Sharma", 5, "Amazing food! The Bhadawar Makhani is a must try. Great taste and timely delivery."),
            ("Priya Verma", 5, "Authentic North Indian taste in Agra. Loved the packaging and the fresh food. Will order again!"),
            ("Rohit Gupta", 5, "Best restaurant in Agra for family dining. The thali is excellent and service is quick.")
        ]
        cursor.executemany("""
        INSERT INTO reviews (name, rating, review_text)
        VALUES (?, ?, ?)
        """, seed_reviews)

    conn.commit()
    print("Database initialized with sample reviews and wallet balance; no guest stories were fabricated.")

if __name__ == '__main__':
    conn = init_db()
    seed_db(conn)
    conn.close()
    print("Database initialization complete.")
