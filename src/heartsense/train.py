import os
import json
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score

from heartsense.config import settings
from heartsense.data import load_raw, clean, split_xy, NUMERIC, CATEGORICAL, TARGET


os.environ["MLFLOW_TRACKING_USERNAME"] = settings.mlflow_tracking_username
os.environ["MLFLOW_TRACKING_PASSWORD"] = settings.mlflow_tracking_password

ARTIFACT_DIR = Path("artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)

def build_preprocessor():
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, NUMERIC),
        ("categorical", categorical_pipe, CATEGORICAL),
    ])

def train():
    df = clean(load_raw())
    X, y = split_xy(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("model", RandomForestClassifier(random_state=42, n_jobs=1)),
    ])

    param_dist = {
        "model__n_estimators": [100, 200, 300],
        "model__max_depth": [None, 5, 8, 12],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 4],
        "model__max_features": ["sqrt", "log2", 0.5],
        "model__class_weight": [None, "balanced", "balanced_subsample"],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # 1. TRAIN THE MODEL (This happens no matter what)
    search = RandomizedSearchCV(
        pipeline, param_dist, n_iter=30, scoring="roc_auc",
        cv=cv, n_jobs=-1, random_state=42, refit=True,
    )
    search.fit(X_train, y_train)
    best = search.best_estimator_

    y_pred = best.predict(X_test)
    y_prob = best.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "cv_roc_auc": search.best_score_,
    }

    # 2. SAVE LOCALLY (Crucial for Docker)
    out_path = ARTIFACT_DIR / "heart_disease_pipeline.joblib"
    joblib.dump(best, out_path)
    (ARTIFACT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("\n✅ Model trained and saved locally!")

    # 3. TRY TO LOG TO MLFLOW (Fail-safe: won't crash if DagsHub fails)
    try:
        if settings.mlflow_tracking_uri:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            mlflow.set_experiment(settings.mlflow_experiment)

        with mlflow.start_run(run_name="rf_random_search"):
            mlflow.log_params(search.best_params_)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(best, name="model", serialization_format="pickle")
            mlflow.log_artifact(str(out_path))
            print("✅ Successfully logged to MLflow!")
    except Exception as e:
        print(f"\n⚠️ MLflow Logging Failed (Skipping DagsHub upload): {e}")
        print("The model was still saved locally and is ready for deployment.")

    return metrics

if __name__ == "__main__":
    print(train())