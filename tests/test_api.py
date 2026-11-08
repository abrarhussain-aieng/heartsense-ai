from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_analytics_shape():
    r = client.get("/api/analytics")
    assert r.status_code == 200
    body = r.json()
    assert {"total", "positive", "negative", "daily"} <= body.keys()

def test_assistant_requires_body():
    r = client.post("/api/assistant", json={"question": ""})
    assert r.status_code == 422