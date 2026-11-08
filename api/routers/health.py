from fastapi import APIRouter
from heartsense.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "mlflow_configured": bool(settings.mlflow_tracking_uri),
        "gemini_configured": bool(settings.gemini_api_key),
        "groq_configured": bool(settings.groq_api_key),
    }