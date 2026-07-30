import numpy as np
import base64

CATEGORIES = ["music","comedy","sports","food","travel","tech","fashion","gaming","news","dance",
              "fitness","pets","art","science","nature","diy","beauty","cars","finance","education"]
_CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
USER_FEAT_DIM = 24  # 4 rates + 20 category one-hot


def build_user_features(user_id: str, conn) -> np.ndarray:
    """Aggregate last 500 interactions into a 24-dim user feature vector."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT i.watch_frac, i.event_type, v.category
               FROM interactions i
               LEFT JOIN videos v ON i.video_id = v.video_id
               WHERE i.user_id = %s
               ORDER BY i.created_at DESC
               LIMIT 500""",
            (user_id,),
        )
        rows = cur.fetchall()

    if not rows:
        return np.zeros(USER_FEAT_DIM, dtype=np.float32)

    watch_fracs, likes, shares, skips = [], [], [], []
    cat_counts = np.zeros(len(CATEGORIES), dtype=np.float32)

    for watch_frac, event_type, category in rows:
        watch_fracs.append(watch_frac)
        likes.append(1.0 if event_type == "like" else 0.0)
        shares.append(1.0 if event_type == "share" else 0.0)
        skips.append(1.0 if event_type == "skip" else 0.0)
        if category and category in _CAT_IDX:
            cat_counts[_CAT_IDX[category]] += 1.0

    total = cat_counts.sum()
    cat_dist = cat_counts / total if total > 0 else cat_counts

    feat = np.array([
        float(np.mean(watch_fracs)),
        float(np.mean(likes)),
        float(np.mean(shares)),
        float(np.mean(skips)),
    ], dtype=np.float32)
    return np.concatenate([feat, cat_dist]).astype(np.float32)


def build_item_features(video_id: str, rdb) -> np.ndarray | None:
    """Fetch the 256-dim projected item embedding from Redis (field item_vec_b64).

    Must be the same projected space feature-service writes to Qdrant. Never
    fall back to raw CLIP — training and serving must use the same distribution.
    """
    raw = rdb.hget(f"item:{video_id}", "item_vec_b64")
    if raw is None:
        return None
    vec = np.frombuffer(base64.b64decode(raw), dtype=np.float32)
    if vec.shape[0] != 256 or not np.all(np.isfinite(vec)):
        return None  # malformed/poisoned cache entry: skip rather than train on garbage
    norm = np.linalg.norm(vec)
    return (vec / norm).astype(np.float32) if norm > 1e-8 else vec.astype(np.float32)
