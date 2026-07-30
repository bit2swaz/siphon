import httpx
from .config import FEATURE_SERVICE_URL, MODEL_SERVER_URL


def notify_feature_refresh() -> None:
    try:
        httpx.post(f"{FEATURE_SERVICE_URL}/refresh", timeout=5.0)
    except Exception as e:
        print(f"notify feature-service failed: {e}", flush=True)


def notify_model_reload(version: int) -> None:
    try:
        httpx.post(f"{MODEL_SERVER_URL}/reload", params={"version": version}, timeout=5.0)
    except Exception as e:
        print(f"notify model-server failed: {e}", flush=True)
