import threading
import psycopg2
import redis as redis_lib
from confluent_kafka import Consumer, KafkaError
from fastapi import FastAPI
from prometheus_client import make_asgi_app, Counter
from minio import Minio
from qdrant_client import QdrantClient

from .config import (
    KAFKA_BOOTSTRAP, KAFKA_TOPIC, KAFKA_GROUP, POSTGRES_DSN,
    REDIS_HOST, REDIS_PORT, MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
    QDRANT_HOST, QDRANT_PORT, RETRAIN_EVERY_N,
)
from .consumer import buffer_event
from .trainer import train_and_export
from .notifier import notify_feature_refresh, notify_model_reload

app = FastAPI(title="training-service")
app.mount("/metrics", make_asgi_app())

_state = {"model_version": 0, "interactions_since_last_train": 0}

EVENTS_BUFFERED = Counter("training_events_buffered_total", "Events buffered")
TRAIN_RUNS      = Counter("training_runs_total", "Training runs completed")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/status")
def status():
    return _state.copy()


def _consume_loop():
    conn   = psycopg2.connect(POSTGRES_DSN)
    rdb    = redis_lib.Redis(host=REDIS_HOST, port=REDIS_PORT)
    qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    minio  = Minio(MINIO_HOST, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    c = Consumer({"bootstrap.servers": KAFKA_BOOTSTRAP, "group.id": KAFKA_GROUP, "auto.offset.reset": "earliest"})
    c.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Kafka error: {msg.error()}", flush=True)
                continue
            try:
                buffer_event(msg.value(), conn)
                EVENTS_BUFFERED.inc()
                _state["interactions_since_last_train"] += 1
            except Exception as e:
                print(f"buffer_event error: {e}", flush=True)

            if _state["interactions_since_last_train"] >= RETRAIN_EVERY_N:
                _state["interactions_since_last_train"] = 0
                try:
                    new_ver = train_and_export(conn, rdb, qdrant, minio, _state["model_version"])
                    if new_ver > _state["model_version"]:
                        _state["model_version"] = new_ver
                        notify_feature_refresh()
                        notify_model_reload(new_ver)
                        TRAIN_RUNS.inc()
                except Exception as e:
                    print(f"train_and_export error: {e}", flush=True)
    finally:
        c.close()
        conn.close()


threading.Thread(target=_consume_loop, daemon=True).start()
