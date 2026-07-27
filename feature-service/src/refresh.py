import base64
import numpy as np
import psycopg2
from qdrant_client.models import PointStruct

from idhash import point_id
from .config import POSTGRES_DSN
from .processor import get_qdrant, get_redis
from .projector import project, load_latest_model


def refresh_all_items() -> None:
    """re-project every video in Postgres using latest model, upsert to Qdrant."""
    load_latest_model()
    with psycopg2.connect(POSTGRES_DSN) as conn, conn.cursor() as cur:
        cur.execute("SELECT video_id, creator_id, category, duration_s, created_at FROM videos")
        rows = cur.fetchall()

    q = get_qdrant()
    r = get_redis()
    batch = []
    reprojected = 0
    for video_id, creator_id, category, duration_s, created_at in rows:
        raw = r.hget(f"item:{video_id}", "clip_embed")
        if raw is None:
            continue
        clip_embed = np.frombuffer(base64.b64decode(raw), dtype=np.float32)
        # text embed not stored in Redis; zeros used so re-projection stays fast
        text_embed = np.zeros(384, dtype=np.float32)
        vec = project(clip_embed, text_embed)
        r.hset(f"item:{video_id}", "item_vec_b64", base64.b64encode(vec.tobytes()))
        batch.append(PointStruct(
            id=point_id(video_id),
            vector=vec.tolist(),
            payload=dict(video_id=video_id, creator_id=creator_id, category=category,
                         duration_s=duration_s, created_at=created_at),
        ))
        reprojected += 1
        if len(batch) >= 100:
            q.upsert("items", points=batch)
            batch.clear()
    if batch:
        q.upsert("items", points=batch)
    print(f"refresh_all_items: re-projected {reprojected}/{len(rows)} items", flush=True)
