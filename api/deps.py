import sqlite3
from pathlib import Path

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
    conn.commit()
    conn.close()

def log_prediction(prediction: int, p0: float, p1: float):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO predictions (prediction, p0, p1) VALUES (?, ?, ?)",
        (prediction, p0, p1),
    )
    conn.commit()
    conn.close()