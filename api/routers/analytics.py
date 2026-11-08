from fastapi import APIRouter
import sqlite3
from api.deps import DB_PATH, init_db

router = APIRouter(tags=["analytics"])

@router.get("/analytics")
def analytics():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    positive = conn.execute("SELECT COUNT(*) FROM predictions WHERE prediction=1").fetchone()[0]
    negative = conn.execute("SELECT COUNT(*) FROM predictions WHERE prediction=0").fetchone()[0]
    rows = conn.execute(
        "SELECT substr(created_at, 1, 10) d, COUNT(*) c FROM predictions GROUP BY d ORDER BY d"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "daily": [{"date": r[0], "count": r[1]} for r in rows],
    }