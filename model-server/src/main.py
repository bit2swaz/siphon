from fastapi import FastAPI
from prometheus_client import make_asgi_app

from .scorer import load_model, current_version
from .grpc_server import serve

app = FastAPI(title="model-server")
app.mount("/metrics", make_asgi_app())

# serve() returns a running server; keep the ref so it isnt garbage collected
_grpc = serve()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "model_version": current_version()}


@app.post("/reload")
def reload(version: int):
    ok = load_model(version)
    return {"success": ok, "model_version": current_version()}
