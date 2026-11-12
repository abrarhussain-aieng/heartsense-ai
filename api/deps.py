import sqlite3
from pathlib import Path
from fastapi import Depends
from heartsense.config import settings

DB_PATH = Path("artifacts/history.db")
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction INTEGER NOT NULL,
            p0 REAL NOT NULL,
            p1 REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            firebase_uid TEXT UNIQUE, 
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    conn.commit()
    conn.close()

def get_current_user():
    """
    Since we removed Firebase login, we bypass authentication 
    and just return a static user for the dashboard.
    """
    return "abrar@heartsense.ai"

def get_or_create_user(email: str, name: str):
    """
    Creates or retrieves the user from the local SQLite database.
    Firebase UID logic has been removed.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        # Insert the user if they don't exist (firebase_uid is set to NULL)
        cursor.execute(
            "INSERT INTO users (email, name, firebase_uid) VALUES (?, ?, NULL)",
            (email, name)
        )
        conn.commit()
        
    cursor.execute("SELECT email, name FROM users WHERE email = ?", (email,))
    res = cursor.fetchone()
    conn.close()
    return {"email": res[0], "name": res[1] if res[1] else res[0]}

def log_prediction(prediction: int, p0: float, p1: float):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (prediction, p0, p1) VALUES (?, ?, ?)",
        (prediction, p0, p1),
    )
    conn.commit()
    conn.close()