from fastapi import APIRouter
from heartsense.monitoring.mlflow_utils import experiment_summary

router = APIRouter(tags=["monitoring"])

@router.get("/monitoring")
def monitoring():
    try:
        return experiment_summary()
    except Exception as e:
        return {"configured": False, "error": str(e)}