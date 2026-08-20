-- Dhaaga CRM — Database Schema
-- Digitising the tailor's register

CREATE TABLE IF NOT EXISTS users (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    password_salt   TEXT NOT NULL,
    display_name    TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    phone           TEXT NOT NULL UNIQUE,
    referred_by     INTEGER REFERENCES customers(customer_id),
    last_visit_date TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    chest           REAL,
    waist           REAL,
    hip             REAL,
    shoulder        REAL,
    sleeve_length   REAL,
    length          REAL,
    notes           TEXT,
    voice_note_url  TEXT,
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    garment_type    TEXT NOT NULL,
    fabric_photo_url TEXT,
    price           REAL NOT NULL,
    delivery_date   TEXT,
    status          TEXT NOT NULL DEFAULT 'Cut',
    delivered_at    TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    amount          REAL NOT NULL,
    type            TEXT NOT NULL,
    method          TEXT,
    payment_date    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS followups (
    followup_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    occasion_tag    TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    flagged_at      TEXT DEFAULT (datetime('now')),
    last_contacted  TEXT
);
