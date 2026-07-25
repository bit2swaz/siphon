"""stable string -> int64 for Qdrant point IDs

pythons built-in hash() is randomised per process (PYTHONHASHSEED), so seed.py, 
feature-service and training-service would each map the same video_id to a
DIFFERENT id and silently create duplicate points. md5 is stable everywhere.
Go services must match this: FNV-1a-64 is used there (see Phase 6); IDs only need
to be stable WITHIN each store's writer set. items are only ever written by
Python, users only by Python, so md5 covers every Qdrant writer
"""
import hashlib


def point_id(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")
