from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import sqlite3
from api.deps import DB_PATH, init_db
from api.schemas import ReportRequest

router = APIRouter(tags=["report"])

@router.post("/report", response_class=PlainTextResponse)
def report(req: ReportRequest):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, prediction, p0, p1, created_at FROM predictions ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()

    lines = [f"HeartSense AI Report for patient {req.patient_id}", "=" * 50, ""]
    for r in rows:
        risk = "Elevated" if r[1] == 1 else "Low"
        lines.append(
            f"#{r[0]} at {r[4]}  →  {risk} risk  (p0={r[2]:.3f}, p1={r[3]:.3f})"
        )
    lines.append("")
    lines.append("This report is for educational use only. Not a diagnosis.")
    return "\n".join(lines)