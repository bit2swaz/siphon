import io, json, sys, pathlib, time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
from qdrant_client.models import PointStruct
from minio import Minio

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "scripts"))
from idhash import point_id  # stable string→int64 (scripts/idhash.py)

from .model import TwoTower
from .features import build_user_features, build_item_features
from .config import USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM, MINIO_BUCKET

_AUC_THRESHOLD = 0.65
_EPOCHS        = 5
_BATCH_SIZE    = 256
_LR            = 1e-3
_device        = "cuda" if torch.cuda.is_available() else "cpu"


def train_and_export(conn, rdb, qdrant_client, minio_client: Minio, current_version: int) -> int:
    """Train two-tower, check AUC >= 0.65, export to MinIO, refresh embeddings. Returns new version."""
    X_user, X_item, y = _build_dataset(conn, rdb)
    if len(y) < 100:
        print("Not enough labelled interactions to train.", flush=True)
        return current_version

    model, loss_history = _fit(X_user, X_item, y)
    auc = _compute_auc(model, X_user, X_item, y)
    print(f"Training AUC: {auc:.4f}", flush=True)

    if auc < _AUC_THRESHOLD:
        print(f"AUC {auc:.4f} below threshold {_AUC_THRESHOLD}, not promoting.", flush=True)
        return current_version

    new_version = current_version + 1
    _export(model, minio_client, new_version, loss_history, auc, conn)
    _refresh_user_embeddings(model, conn, qdrant_client)
    return new_version


def _build_dataset(conn, rdb):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT user_id, video_id, label, watch_frac, event_type FROM interactions ORDER BY created_at DESC LIMIT 50000"
        )
        rows = cur.fetchall()

    # cache user features: training touches ~50k rows but only ~hundreds of distinct users
    user_feat_cache: dict[str, np.ndarray] = {}

    X_user, X_item, y = [], [], []
    for user_id, video_id, label, watch_frac, event_type in rows:
        uf = user_feat_cache.get(user_id)
        if uf is None:
            uf = build_user_features(user_id, conn)
            user_feat_cache[user_id] = uf
        itf = build_item_features(video_id, rdb)
        if itf is None:
            itf = np.zeros(ITEM_FEAT_DIM, dtype=np.float32)
        X_user.append(uf)
        X_item.append(itf)
        y.append(float(label))

    return (
        np.array(X_user,  dtype=np.float32),
        np.array(X_item,  dtype=np.float32),
        np.array(y,       dtype=np.float32),
    )


def _fit(X_user: np.ndarray, X_item: np.ndarray, y: np.ndarray):
    model = TwoTower(USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM).to(_device)
    opt   = torch.optim.Adam(model.parameters(), lr=_LR)
    loss_fn = nn.BCEWithLogitsLoss()

    ds = TensorDataset(
        torch.from_numpy(X_user),
        torch.from_numpy(X_item),
        torch.from_numpy(y),
    )
    loader = DataLoader(ds, batch_size=_BATCH_SIZE, shuffle=True)
    history = []
    for _ in range(_EPOCHS):
        epoch_loss = 0.0
        for ub, ib, yb in loader:
            ub, ib, yb = ub.to(_device), ib.to(_device), yb.to(_device)
            scores = model(ub, ib)
            loss   = loss_fn(scores, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
        history.append(epoch_loss / len(loader))
    model.eval()
    return model, history


def _compute_auc(model: TwoTower, X_user, X_item, y) -> float:
    with torch.no_grad():
        ub = torch.from_numpy(X_user).to(_device)
        ib = torch.from_numpy(X_item).to(_device)
        scores = model(ub, ib).cpu().numpy()
    return float(roc_auc_score(y, scores))


def _export(model: TwoTower, client: Minio, version: int, loss_history, auc: float, conn):
    prefix = f"models/two_tower/v{version}/"

    def _upload(name: str, state_dict):
        buf = io.BytesIO()
        torch.save(state_dict, buf)
        size = buf.tell()
        buf.seek(0)
        client.put_object(MINIO_BUCKET, prefix + name, buf, size, content_type="application/octet-stream")

    _upload("user_tower.pt", model._user_tower.state_dict())
    _upload("item_tower.pt",  model._item_tower.state_dict())

    meta = json.dumps({"version": version, "auc": auc, "loss": loss_history})
    buf  = io.BytesIO(meta.encode())
    client.put_object(MINIO_BUCKET, prefix + "meta.json", buf, len(meta), content_type="application/json")

    now = int(time.time() * 1000)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO training_runs(version, started_at, finished_at, loss_json, auc) VALUES(%s,%s,%s,%s,%s)",
            (version, now, now, json.dumps(loss_history), auc),
        )
    conn.commit()


def _refresh_user_embeddings(model: TwoTower, conn, qdrant_client):
    """Regenerate all user embeddings and upsert into Qdrant."""
    with conn.cursor() as cur:
        cur.execute("SELECT user_id FROM users")
        user_ids = [r[0] for r in cur.fetchall()]

    points = []
    for user_id in user_ids:
        uf = build_user_features(user_id, conn)
        t  = torch.from_numpy(uf).unsqueeze(0).to(_device)
        with torch.no_grad():
            vec = model.user_embed(t).squeeze(0).cpu().numpy()
        points.append(PointStruct(
            id=point_id(user_id),
            vector=vec.tolist(),
            payload=dict(user_id=user_id, last_updated=int(time.time() * 1000)),
        ))
        if len(points) >= 100:
            qdrant_client.upsert("users", points=points)
            points.clear()
    if points:
        qdrant_client.upsert("users", points=points)
    print(f"Refreshed {len(user_ids)} user embeddings.", flush=True)
