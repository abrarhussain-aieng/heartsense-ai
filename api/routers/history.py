from fastapi import APIRouter
import sqlite3
from api.deps import DB_PATH, init_db

router = APIRouter(tags=["history"])

@router.get("/history")
def history(limit: int = 50):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, prediction, p0, p1, created_at FROM predictions ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "prediction": r[1], "probabilities": [r[2], r[3]], "created_at": r[4]}
        for r in rows
    ]