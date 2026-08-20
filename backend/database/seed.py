"""
Runs once, the very first time the app starts (when dhaaga.db doesn't
exist yet). Creates the login account and a bit of sample data so the
app isn't empty when you open it.
"""

import os
import secrets
import sqlite3

from backend.security import hash_password


def seed_admin_user(conn: sqlite3.Connection) -> None:
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(9)
    password_hash, salt = hash_password(password)

    conn.execute(
        """INSERT INTO users (username, password_hash, password_salt, display_name)
           VALUES (?, ?, ?, ?)""",
        (username, password_hash, salt, "Shop Owner"),
    )
    conn.commit()

    print("----------------------------------------------------")
    print("Dhaaga CRM — first run: login account created")
    print(f"  Username: {username}")
    if "ADMIN_PASSWORD" in os.environ:
        print("  Password: set via ADMIN_PASSWORD env var")
    else:
        print(f"  Password: {password}  (auto-generated — change it after logging in)")
    print("----------------------------------------------------")


def seed_sample_data(conn: sqlite3.Connection) -> None:
    customers = [
        ("Anita Deshmukh", "9876543210"),
        ("Rohan Patil", "9823456780"),
        ("Meera Kulkarni", "9765432109"),
    ]
    cursor = conn.cursor()
    ids = []
    for name, phone in customers:
        cursor.execute(
            "INSERT INTO customers (name, phone, last_visit_date) VALUES (?, ?, date('now'))",
            (name, phone),
        )
        ids.append(cursor.lastrowid)

    cursor.execute(
        """INSERT INTO orders (customer_id, garment_type, price, delivery_date, status)
           VALUES (?, 'Formal Shirt', 1200, date('now', '+3 day'), 'Stitching')""",
        (ids[0],),
    )
    cursor.execute(
        """INSERT INTO orders (customer_id, garment_type, price, delivery_date, status)
           VALUES (?, 'Blouse', 900, date('now', '+1 day'), 'Ready')""",
        (ids[1],),
    )
    conn.commit()
    print("Seeded sample data into dhaaga.db")
