"""Fetch MLflow experiment info from the configured tracking server."""
from mlflow.tracking import MlflowClient
from heartsense.config import settings

def experiment_summary() -> dict:
    if not settings.mlflow_tracking_uri:
        return {"configured": False}
    client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
    exp = client.get_experiment_by_name(settings.mlflow_experiment)
    if exp is None:
        return {"configured": True, "experiment": None}

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