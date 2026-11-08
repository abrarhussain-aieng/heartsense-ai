"""Pure service function used by both API and MCP tools."""
import joblib
import pandas as pd
from pathlib import Path
from functools import lru_cache

MODEL_PATH = Path("artifacts/heart_disease_pipeline.joblib")

@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        raise RuntimeError("Model artifact missing. Run `dvc repro` first.")
    return joblib.load(MODEL_PATH)

def predict_single(payload: dict) -> dict:
    model = load_model()
    row = pd.DataFrame([payload])
    pred = int(model.predict(row)[0])
    proba = model.predict_proba(row)[0].tolist()
    return {"prediction": pred, "probabilities": proba}