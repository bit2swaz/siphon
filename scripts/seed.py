#!/usr/bin/env python3
"""cold start seed: creates schema, generates synthetic data, populates all stores."""
import base64, json, os, random, struct, time, uuid
import numpy as np
import psycopg2
import redis
from confluent_kafka.admin import AdminClient, NewTopic  # type: ignore[import-untyped]
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from minio import Minio

from idhash import point_id  # stable string -> int64, shared by all services

# ── config ───
PG: dict[str, str | int] = dict(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", 5432)),
    dbname=os.getenv("POSTGRES_DB", "siphon"),
    user=os.getenv("POSTGRES_USER", "siphon"),
    password=os.getenv("POSTGRES_PASSWORD", "siphon"),
)
REDIS_HOST  = os.getenv("REDIS_HOST", "localhost")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
MINIO_HOST  = os.getenv("MINIO_HOST", "localhost:9000")

NUM_VIDEOS  = 1000
NUM_USERS   = 500
CATEGORIES  = ["music","comedy","sports","food","travel","tech","fashion","gaming","news","dance",
                "fitness","pets","art","science","nature","diy","beauty","cars","finance","education"]

def main():
    pg_setup()
    qdrant_setup()
    kafka_setup()
    minio_setup()
    redis_setup()
    print("Seed complete.")

def pg_setup():
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    schema = open(os.path.join(os.path.dirname(__file__), "schema.sql")).read()
    cur.execute(schema)

    now_ms = int(time.time() * 1000)
    videos = []
    for i in range(NUM_VIDEOS):
        videos.append((
            f"v{i:06d}",
            f"c{random.randint(0, 99):04d}",
            random.choice(CATEGORIES),
            round(random.uniform(5.0, 60.0), 1),
            now_ms - random.randint(0, 86400_000 * 30),
        ))
    cur.executemany(
        "INSERT INTO videos(video_id,creator_id,category,duration_s,created_at) VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        videos,
    )

    users = []
    for i in range(NUM_USERS):
        vec = np.random.randn(256).astype(np.float32)
        vec /= np.linalg.norm(vec)
        users.append((
            f"u{i:06d}",
            json.dumps(vec.tolist()),
            round(random.gauss(0.5, 0.1), 3),
            round(random.gauss(0.1, 0.05), 3),
        ))
    cur.executemany(
        "INSERT INTO users(user_id,interest_vector_json,watch_frac_bias,like_rate_bias) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        users,
    )
    conn.commit()
    conn.close()
    print(f"  postgres: {NUM_VIDEOS} videos, {NUM_USERS} users")

def qdrant_setup():
    q = QdrantClient(host=QDRANT_HOST, port=6333)
    for name in ["items", "users"]:
        existing = [c.name for c in q.get_collections().collections]
        if name not in existing:
            q.create_collection(name, vectors_config=VectorParams(size=256, distance=Distance.COSINE))

    # Seed random item embeddings (pre-training cold start)
    # The SAME 256-dim vector is cached to Redis under item:{id}/item_vec_b64 so
    # training-service reads the identical projected space it will serve on
    points = []
    now_ms = int(time.time() * 1000)
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=False)
    rpipe = r.pipeline()
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    cur.execute("SELECT video_id, creator_id, category, duration_s, created_at FROM videos")
    for row in cur.fetchall():
        video_id, creator_id, category, duration_s, created_at = row
        vec = np.random.randn(256).astype(np.float32)
        vec /= np.linalg.norm(vec)
        points.append(PointStruct(
            id=point_id(video_id),
            vector=vec.tolist(),
            payload=dict(video_id=video_id, creator_id=creator_id, category=category,
                         duration_s=duration_s, created_at=created_at),
        ))
        rpipe.hset(f"item:{video_id}", mapping={
            b"video_id":    video_id.encode(),
            b"creator_id":  creator_id.encode(),
            b"category":    category.encode(),
            b"duration_s":  str(duration_s).encode(),
            b"created_at":  str(created_at).encode(),
            b"item_vec_b64": base64.b64encode(vec.tobytes()),  # 256-dim projected vector
        })
    conn.close()
    rpipe.execute()
    q.upsert("items", points=points)

    # Seed random user embeddings
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    cur.execute("SELECT user_id, interest_vector_json FROM users")
    upoints = []
    for user_id, vec_json in cur.fetchall():
        vec = np.array(json.loads(vec_json), dtype=np.float32)
        upoints.append(PointStruct(
            id=point_id(user_id),
            vector=vec.tolist(),
            payload=dict(user_id=user_id, last_updated=int(time.time() * 1000)),
        ))
    conn.close()
    q.upsert("users", points=upoints)
    print(f"  qdrant: {len(points)} items, {len(upoints)} users")

def kafka_setup():
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    existing = admin.list_topics(timeout=10).topics
    topics = [
        NewTopic(name, num_partitions=4, replication_factor=1)
        for name in ["video.ingested", "user.events"]
        if name not in existing
    ]
    if topics:
        fs = admin.create_topics(topics)
        for name, f in fs.items():
            f.result()  # raises on error
    print("  kafka: topics ready")

def minio_setup():
    client = Minio(MINIO_HOST, access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
                   secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"), secure=False)
    if not client.bucket_exists("siphon-models"):
        client.make_bucket("siphon-models")
    print("  minio: bucket siphon-models ready")

def redis_setup():
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    # trending:24h : top 50 videos by random initial score
    conn = psycopg2.connect(**PG)  # type: ignore[call-overload]
    cur = conn.cursor()
    cur.execute("SELECT video_id FROM videos ORDER BY random() LIMIT 50")
    pipe = r.pipeline()
    pipe.delete("trending:24h")
    for (video_id,) in cur.fetchall():
        pipe.zadd("trending:24h", {video_id: random.uniform(10, 1000)})
    # flagged: safety-filter set read by feed-api. seeded empty (create the key so
    # SISMEMBER/SMEMBERS never error). add video_ids here to hard-block them.
    pipe.sadd("flagged", "__init__")  # sentinel keeps key alive; not a real video_id
    pipe.execute()
    conn.close()
    print("  redis: trending:24h seeded with 50 items, flagged set initialised")

if __name__ == "__main__":
    main()
