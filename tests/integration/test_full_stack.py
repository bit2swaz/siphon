import httpx
import pytest

SERVICES = [
    ("ingest-service",     "http://localhost:8001/healthz"),
    ("feature-service",    "http://localhost:8007/healthz"),
    ("user-event-service", "http://localhost:8002/healthz"),
    ("training-service",   "http://localhost:8003/healthz"),
    ("model-server",       "http://localhost:8004/healthz"),
    ("feed-api",           "http://localhost:8005/healthz"),
    ("dashboard-api",      "http://localhost:8006/healthz"),
]

@pytest.mark.parametrize("name,url", SERVICES)
def test_service_healthy(name, url):
    r = httpx.get(url, timeout=10.0)
    assert r.status_code == 200, f"{name} not healthy at {url}: {r.text}"
    assert r.json().get("status") == "ok", f"{name} returned unexpected: {r.json()}"
