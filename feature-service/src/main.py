import threading
from confluent_kafka import Consumer, KafkaError
from fastapi import FastAPI
from prometheus_client import make_asgi_app, Counter

from .config import KAFKA_BOOTSTRAP, KAFKA_TOPIC, KAFKA_GROUP
from .processor import process_event
from .refresh import refresh_all_items

app = FastAPI(title="feature-service")
app.mount("/metrics", make_asgi_app())

PROCESSED = Counter("feature_events_processed_total", "Events processed")
ERRORS    = Counter("feature_events_error_total", "Events with errors")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/refresh")
def refresh():
    threading.Thread(target=refresh_all_items, daemon=True).start()
    return {"status": "refresh_started"}


def consume():
    c = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": KAFKA_GROUP,
        "auto.offset.reset": "earliest",
    })
    c.subscribe([KAFKA_TOPIC])
    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    ERRORS.inc()
                continue
            try:
                process_event(msg.value())
                PROCESSED.inc()
            except Exception as e:
                ERRORS.inc()
                print(f"process_event error: {e}", flush=True)
    finally:
        c.close()


threading.Thread(target=consume, daemon=True).start()
