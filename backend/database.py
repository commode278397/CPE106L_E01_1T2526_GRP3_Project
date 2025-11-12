# database.py

import sqlite3
from pathlib import Path

# This will create a file named SkillBridge.db beside this file
DB_PATH = Path(__file__).resolve().parent / "SkillBridge.db"


def get_connection():
    """Open a connection to the SkillBridge SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows accessing columns by name
    return conn


def _ensure_column(cur, table: str, column: str, definition: str):
    """Add a column to an existing table if it is missing."""
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row["name"] for row in cur.fetchall()}
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    """Create tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            skills TEXT
        );
        """
    )

    # Requests table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            required_skills TEXT,
            requester_name TEXT NOT NULL
        );
        """
    )
    # Backfill new columns for older databases.
    _ensure_column(cur, "requests", "location", "TEXT")
    _ensure_column(
        cur,
        "requests",
        "status",
        "TEXT NOT NULL DEFAULT 'open'",
    )

    # Volunteer skill offerings
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS volunteer_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    # Volunteer acceptances for requests
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS request_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            volunteer_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'accepted',
            accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(request_id) REFERENCES requests(id) ON DELETE CASCADE,
            FOREIGN KEY(volunteer_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()
