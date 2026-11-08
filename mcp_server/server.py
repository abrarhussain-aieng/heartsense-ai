from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path

from heartsense.rag.retriever import retrieve as rag_retrieve
from mcp_server.auth import BearerTokenMiddleware

MODEL_PATH = Path("artifacts/heart_disease_pipeline.joblib")
_model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

mcp = FastMCP(
    "HeartSense AI MCP",
    stateless_http=True,
    host="0.0.0.0",
    port=8001,
    path="/mcp",
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
    if _model is None:
        raise ToolError("Model artifact not available.")
    row = pd.DataFrame([input.model_dump()])
    pred = int(_model.predict(row)[0])
    proba = _model.predict_proba(row)[0].tolist()
    return {"prediction": pred, "probabilities": proba}

@mcp.tool()
def search_medical_knowledge(query: str, k: int = 4) -> list[dict]:
    """Retrieve grounded cardiovascular knowledge excerpts with source metadata."""
    return rag_retrieve(query, k=k)

@mcp.tool()
def get_prediction_analytics(limit: int = 100) -> dict:
    """Return authorized prediction history summaries."""
    import sqlite3
    conn = sqlite3.connect("artifacts/history.db")
    cur = conn.cursor()
    cur.execute("SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction")
    rows = cur.fetchall()
    conn.close()
    return {"counts": [{"prediction": r[0], "count": r[1]} for r in rows]}

# Build the ASGI app and wrap with our bearer-token middleware
app = FastAPI(title="HeartSense MCP")
app.add_middleware(BearerTokenMiddleware)

# Mount the FastMCP streamable-http app
mcp_app = mcp.streamable_http_app()
app.mount("/", mcp_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)