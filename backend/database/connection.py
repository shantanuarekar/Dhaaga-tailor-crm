"""
Small wrapper around sqlite3 so the rest of the app never has to
think about connection setup, row factories, or foreign keys.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "dhaaga.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Open a connection with sane defaults for a small local app."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def is_new_database() -> bool:
    return not DB_PATH.exists()


def run_schema(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
