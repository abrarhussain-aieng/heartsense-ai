from mlflow.tracking import MlflowClient
from heartsense.config import settings
import os

def experiment_summary() -> dict:
    if not settings.mlflow_tracking_uri:
        return {"configured": False, "error": "MLFLOW_TRACKING_URI is not set in .env", "runs": []}

    # Ensure credentials are explicitly set for the MLflow client
    os.environ["MLFLOW_TRACKING_USERNAME"] = settings.mlflow_tracking_username
    os.environ["MLFLOW_TRACKING_PASSWORD"] = settings.mlflow_tracking_password

    try:
        client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
        exp = client.get_experiment_by_name(settings.mlflow_experiment)
        
        if exp is None:
            return {"configured": True, "error": f"Experiment '{settings.mlflow_experiment}' not found on DagsHub.", "runs": []}

        runs = client.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=["metrics.roc_auc DESC"],
            max_results=10,
        )
        return {
            "configured": True,
            "experiment": exp.name,
            "experiment_id": exp.experiment_id,
            "runs": [
                {
                    "run_id": r.info.run_id,
                    "status": r.info.status,
                    "metrics": dict(r.data.metrics),
                    "params": dict(r.data.params),
                }
                for r in runs
            ],
        }
    except Exception as e:
        # Catch Auth errors, connection timeouts, etc.
        return {"configured": True, "error": str(e), "runs": []}