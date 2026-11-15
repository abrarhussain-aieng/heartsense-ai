from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from api.routers import predict, health, history, analytics, report, assistant, monitoring, auth

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="HeartSense AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://heartsense-ai.duckdns.org",  # Your new secure production domain
        "http://3.25.121.3",                  # Your original EC2 IP (fallback)
        "http://localhost:3000",              # For local frontend development
        "http://localhost:8000"               # For local FastAPI docs testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")

frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")