import io, sys, pathlib
import pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "scripts"))  # idhash.point_id
from idhash import point_id
from conftest import INGEST_URL, FEED_URL, EVENT_URL, wait_for

def test_services_healthy(http):
    for url, name in [
        (f"{INGEST_URL}/healthz", "ingest"),
        (f"{FEED_URL}/healthz",   "feed-api"),
        (f"{EVENT_URL}/healthz",  "user-event"),
    ]:
        r = http.get(url)
        assert r.status_code == 200, f"{name} not healthy: {r.text}"

def test_ingest_creates_video_in_postgres(http, pg):
    fake_video = io.BytesIO(b"\x00" * 32)
    r = http.post(
        f"{INGEST_URL}/videos",
        data={"creator_id": "c_inttest", "category": "tech", "duration_s": "12.0"},
        files={"file": ("test.mp4", fake_video, "video/mp4")},
    )
    assert r.status_code == 200, r.text
    video_id = r.json()["video_id"]
    assert video_id.startswith("v")

    cur = pg.cursor()
    cur.execute("SELECT video_id FROM videos WHERE video_id = %s", (video_id,))
    assert cur.fetchone() is not None, f"video {video_id} not found in postgres"

def test_ingest_video_appears_in_qdrant(http, qdrant):
    """Ingest a video and wait for feature-service to write it to Qdrant."""
    fake_video = io.BytesIO(b"\x00" * 32)
    r = http.post(
        f"{INGEST_URL}/videos",
        data={"creator_id": "c_qdrant_test", "category": "music", "duration_s": "8.0"},
        files={"file": ("qdrant_test.mp4", fake_video, "video/mp4")},
    )
    assert r.status_code == 200
    video_id = r.json()["video_id"]
    pid = point_id(video_id)

    wait_for(lambda: len(qdrant.retrieve("items", ids=[pid])) > 0,
             timeout=30, msg=f"video {video_id} in Qdrant")
    results = qdrant.retrieve("items", ids=[pid], with_payload=True)
    assert results[0].payload["video_id"] == video_id

def test_user_event_recorded_in_redis(http, rdb):
    user_id  = "u_inttest_001"
    video_id = "v000001"
    r = http.post(f"{EVENT_URL}/events", json={
        "user_id": user_id, "video_id": video_id,
        "event_type": "watch", "watch_ms": 8000, "duration_ms": 12000,
    })
    assert r.status_code == 200

    wait_for(lambda: rdb.llen(f"session:{user_id}") > 0,
             timeout=10, msg="event in redis session")
    assert video_id in rdb.lrange(f"session:{user_id}", 0, -1)

def test_feed_api_returns_feed(http):
    r = http.get(f"{FEED_URL}/feed", params={"user_id": "u000000", "limit": 5})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "feed" in body
    assert "model_version" in body
    assert "latency_ms" in body
    assert isinstance(body["feed"], list)
    assert len(body["feed"]) > 0  # after seed, should have candidates

def test_feed_response_schema(http):
    r = http.get(f"{FEED_URL}/feed", params={"user_id": "u000001", "limit": 10})
    assert r.status_code == 200
    for item in r.json()["feed"]:
        for field in ("video_id", "score", "rank", "creator_id", "duration_s"):
            assert field in item

def test_feed_missing_user_id_returns_400(http):
    r = http.get(f"{FEED_URL}/feed")
    assert r.status_code == 400
