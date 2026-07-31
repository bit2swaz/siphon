import io
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from minio import Minio

from .config import MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET

_device = "cuda" if torch.cuda.is_available() else "cpu"
_model_version = 0

# identity linear on cold start; replaced by load_model()
_item_tower = nn.Linear(256, 256, bias=False)
nn.init.eye_(_item_tower.weight)
_item_tower.eval()
_item_tower.to(_device)


def score_batch(
    user_embed: np.ndarray,
    video_ids: list[str],
    item_embeds: list[np.ndarray],
) -> list[tuple[str, float]]:
    """cosine similarity between user_embed and each item_embed after item tower projection"""
    u = torch.from_numpy(user_embed).unsqueeze(0).to(_device)
    u = F.normalize(u, dim=-1)

    items = np.stack(item_embeds).astype(np.float32)  # (N, 256)
    t = torch.from_numpy(items).to(_device)
    with torch.no_grad():
        v = F.normalize(_item_tower(t), dim=-1)        # (N, 256)
    scores = (u * v).sum(dim=-1).cpu().numpy()         # (N,)
    return list(zip(video_ids, scores.tolist()))


def load_model(version: int) -> bool:
    """hot load item_tower.pt from MinIO. returns True on success"""
    global _item_tower, _model_version
    client = Minio(MINIO_HOST, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    path = f"models/two_tower/v{version}/item_tower.pt"
    try:
        obj = client.get_object(MINIO_BUCKET, path)
        buf = io.BytesIO(obj.read())
        # weights_only=True so a malicious .pt cant run arbitrary code on load
        state = torch.load(buf, map_location=_device, weights_only=True)
        # training-service saves the item tower as nn.Sequential(nn.Linear(256, 256)),
        # so its state_dict keys are 0.weight/0.bias. rebuild the same module to match.
        new_tower = nn.Sequential(nn.Linear(256, 256))
        new_tower.load_state_dict(state)
        new_tower.eval()
        new_tower.to(_device)
        _item_tower = new_tower
        _model_version = version
        return True
    except Exception as e:
        print(f"load_model v{version} failed: {e}", flush=True)
        return False


def current_version() -> int:
    return _model_version
