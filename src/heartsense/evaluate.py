"""Standalone evaluation of the saved model against a hold-out split."""
import json
import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
)

from heartsense.data import load_raw, clean, split_xy

MODEL_PATH = Path("artifacts/heart_disease_pipeline.joblib")
OUT_PATH = Path("artifacts/evaluation.json")

def evaluate() -> dict:
    df = clean(load_raw())
    X, y = split_xy(df)
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = joblib.load(MODEL_PATH)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }
    OUT_PATH.write_text(json.dumps(metrics, indent=2, default=str))
    return metrics

if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, default=str))