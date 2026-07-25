import subprocess, os, psycopg2, json
import redis
from qdrant_client import QdrantClient

PG: dict[str, str | int] = dict(host="localhost", port=5432, dbname="siphon", user="siphon", password="siphon")

def test_postgres_tables_exist():
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    for table in ["videos", "users", "interactions", "training_runs"]:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name=%s", (table,))
        assert cur.fetchone(), f"missing table: {table}"
    conn.close()

def test_videos_seeded():
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM videos")
    row = cur.fetchone()
    assert row is not None
    assert row[0] >= 1000, f"expected >= 1000 videos, got {row[0]}"
    conn.close()

def test_users_seeded():
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    row = cur.fetchone()
    assert row is not None
    assert row[0] >= 500, f"expected >= 500 users, got {row[0]}"
    conn.close()

def test_qdrant_collections_exist():
    q = QdrantClient(host="localhost", port=6333)
    names = [c.name for c in q.get_collections().collections]
    assert "items" in names
    assert "users" in names

def test_qdrant_items_populated():
    q = QdrantClient(host="localhost", port=6333)
    info = q.get_collection("items")
    assert (info.points_count or 0) >= 1000

def test_redis_trending_exists():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    count = r.zcard("trending:24h")
    assert count == 50, f"expected 50 trending items, got {count}"

def test_redis_flagged_key_exists():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    assert r.exists("flagged") == 1, "flagged set must exist (seeded empty)"

def test_redis_item_cache_has_projected_vector():
    import base64, numpy as np
    r = redis.Redis(host="localhost", port=6379, decode_responses=False)
    raw = r.hget(b"item:v000000", b"item_vec_b64")
    assert raw is not None, "item:{id} must cache item_vec_b64"
    vec = np.frombuffer(base64.b64decode(raw), dtype=np.float32)
    assert vec.shape == (256,), f"expected 256-dim projected vector, got {vec.shape}"
