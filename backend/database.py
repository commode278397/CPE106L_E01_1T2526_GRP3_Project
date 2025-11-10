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

    conn.commit()
    conn.close()
