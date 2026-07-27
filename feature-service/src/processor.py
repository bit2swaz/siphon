import base64, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "proto/gen/python"))
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "scripts"))

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import redis as redis_lib

from video_ingested_pb2 import VideoIngested
from idhash import point_id
from .config import QDRANT_HOST, QDRANT_PORT, REDIS_HOST, REDIS_PORT
from .projector import project

_qdrant: QdrantClient | None = None
_redis: redis_lib.Redis | None = None


def get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _qdrant


def get_redis() -> redis_lib.Redis:
    global _redis
    if _redis is None:
        _redis = redis_lib.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
    return _redis


def process_event(raw_bytes: bytes) -> None:
    event = VideoIngested()
    event.ParseFromString(raw_bytes)

    clip_embed = np.frombuffer(event.clip_embed, dtype=np.float32)
    text_embed = np.frombuffer(event.text_embed, dtype=np.float32)
    item_vec = project(clip_embed, text_embed)

    point = PointStruct(
        id=point_id(event.video_id),
        vector=item_vec.tolist(),
        payload=dict(
            video_id=event.video_id,
            creator_id=event.creator_id,
            category=event.category,
            duration_s=event.duration_s,
            created_at=event.created_at,
        ),
    )
    get_qdrant().upsert("items", points=[point])

    get_redis().hset(f"item:{event.video_id}", mapping={
        "video_id":     event.video_id,
        "creator_id":   event.creator_id,
        "category":     event.category,
        "duration_s":   str(event.duration_s),
        "created_at":   str(event.created_at),
        "clip_embed":   base64.b64encode(event.clip_embed),
        "item_vec_b64": base64.b64encode(item_vec.tobytes()),
    })
