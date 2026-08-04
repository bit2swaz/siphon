import time
import pytest
import httpx
import psycopg2
import redis
from qdrant_client import QdrantClient

INGEST_URL    = "http://localhost:8001"
FEED_URL      = "http://localhost:8005"
EVENT_URL     = "http://localhost:8002"

PG = dict(host="localhost", port=5432, dbname="siphon", user="siphon", password="siphon")

@pytest.fixture(scope="session")
def pg():
    conn = psycopg2.connect(**PG)
    yield conn
    conn.close()

@pytest.fixture(scope="session")
def rdb():
    return redis.Redis(host="localhost", port=6379, decode_responses=True)

@pytest.fixture(scope="session")
def qdrant():
    return QdrantClient(host="localhost", port=6333)

@pytest.fixture(scope="session")
def http():
    with httpx.Client(timeout=30.0) as client:
        yield client

def wait_for(condition_fn, timeout=30, interval=1, msg="condition"):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition_fn():
            return
        time.sleep(interval)
    raise TimeoutError(f"Timed out waiting for: {msg}")
