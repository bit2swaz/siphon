import io
import numpy as np
import torch
import torch.nn as nn
from minio import Minio

from .config import MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET

_minio: Minio | None = None


def _get_minio() -> Minio:
    global _minio
    if _minio is None:
        _minio = Minio(MINIO_HOST, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    return _minio

_INPUT_DIM  = 512 + 384
_OUTPUT_DIM = 256

# random projection on cold start; replaced by load_latest_model()
_projection = nn.Linear(_INPUT_DIM, _OUTPUT_DIM, bias=False)
nn.init.xavier_uniform_(_projection.weight)
_projection.eval()
_device = "cuda" if torch.cuda.is_available() else "cpu"
_projection.to(_device)


def project(clip_embed: np.ndarray, text_embed: np.ndarray) -> np.ndarray:
    concat = np.concatenate([clip_embed, text_embed]).astype(np.float32)
    t = torch.from_numpy(concat).unsqueeze(0).to(_device)
    with torch.no_grad():
        out = _projection(t).squeeze(0).cpu().numpy()
    norm = np.linalg.norm(out)
    return (out / norm).astype(np.float32) if norm > 1e-8 else out.astype(np.float32)


def load_latest_model() -> None:
    """Hot-swap _projection with the latest item_tower.pt from MinIO."""
    global _projection
    client = _get_minio()
    objects = list(client.list_objects(MINIO_BUCKET, prefix="models/two_tower/", recursive=False))
    versions = sorted([o.object_name for o in objects if o.is_dir], reverse=True)
    if not versions:
        print("load_latest_model: no model versions found in MinIO, keeping current projection", flush=True)
        return
    resp = client.get_object(MINIO_BUCKET, f"{versions[0]}item_tower.pt")
    try:
        weights = io.BytesIO(resp.read())
    finally:
        resp.close()
        resp.release_conn()
    state = torch.load(weights, map_location=_device, weights_only=True)
    new_proj = nn.Linear(_INPUT_DIM, _OUTPUT_DIM, bias=False)
    try:
        new_proj.load_state_dict(state)
    except RuntimeError as e:
        print(f"load_latest_model: state_dict mismatch, keeping current projection: {e}", flush=True)
        return
    new_proj.eval().to(_device)
    _projection = new_proj
