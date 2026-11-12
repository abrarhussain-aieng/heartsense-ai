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

    lines = [f"HeartSense AI Health Report", "=" * 50, f"Patient ID: {req.patient_id}", ""]
    for r in rows:
        risk = "Elevated (High Risk)" if r[1] == 1 else "Low Risk"
        lines.append(f"[{r[4]}] Risk Level: {risk} | Probability: {(r[3]*100):.1f}%")
    
    lines.append("\nDisclaimer: This report is for educational use only. Not medical advice.")
    
    headers = {
        "Content-Disposition": f"attachment; filename=heartsense_report_{req.patient_id}.txt"
    }
    return PlainTextResponse(content="\n".join(lines), headers=headers)