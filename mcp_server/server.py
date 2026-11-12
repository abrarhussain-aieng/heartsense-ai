from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path
import sqlite3

from heartsense.rag.retriever import retrieve as rag_retrieve

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "artifacts" / "heart_disease_pipeline.joblib"
DB_PATH = BASE_DIR / "artifacts" / "history.db"

_model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

mcp = FastMCP(
    "HeartSense AI MCP",
    stateless_http=True,
    streamable_http_path="/mcp",
    host="0.0.0.0",     # Moved here
    port=8001,          # Moved here
)

class PredictInput(BaseModel):
    Age: int = Field(ge=1, le=120)
    Sex: str
    ChestPainType: str
    RestingBP: int
    Cholesterol: int
    FastingBS: int
    RestingECG: str
    MaxHR: int
    ExerciseAngina: str
    Oldpeak: float
    ST_Slope: str

@mcp.tool()
def predict_heart_disease(input: PredictInput) -> dict:
    """Predict heart disease risk from patient clinical features."""
    try:
        if _model is None:
            return {"error": "Model artifact not available."}
        row = pd.DataFrame([input.model_dump()])
        pred = int(_model.predict(row)[0])
        proba = _model.predict_proba(row)[0].tolist()
        return {"prediction": pred, "probabilities": proba}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@mcp.tool()
def search_medical_knowledge(query: str, k: int = 4) -> list[dict]:
    """Retrieve grounded cardiovascular knowledge excerpts with source metadata."""
    try:
        return rag_retrieve(query, k=k)
    except Exception as e:
        return [{"content": "Medical database unavailable.", "title": "Error", "url": ""}]


@mcp.tool()
def get_prediction_analytics(limit: int = 100) -> str:
    """Return authorized prediction history summaries in plain text."""
    import sqlite3
    try:
        conn = sqlite3.connect("artifacts/history.db")
        cur = conn.cursor()
        
        # Get Total
        cur.execute("SELECT COUNT(*) FROM predictions")
        total = cur.fetchone()[0]
        
        if total == 0:
            return "The user has not made any predictions yet."
            
        # Get Breakdown
        cur.execute("SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction")
        rows = cur.fetchall()
        
        high = 0
        low = 0
        for r in rows:
            if r[0] == 1: high = r[1]
            else: low = r[1]
            
        conn.close()
        
        return f"The user has made a total of {total} predictions. Out of these, {high} were High Risk and {low} were Low Risk."
    except Exception as e:
        return f"Error querying database: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http") # Removed host and port from here