import io, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "proto/gen/python"))
from unittest.mock import patch
import numpy as np
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

FAKE_EMBED_512 = np.zeros(512, dtype=np.float32)
FAKE_EMBED_384 = np.zeros(384, dtype=np.float32)

def test_post_video_returns_video_id():
    with (
        patch("src.main.extract_clip_embed", return_value=FAKE_EMBED_512),
        patch("src.main.extract_text_embed", return_value=FAKE_EMBED_384),
        patch("src.main.transcribe_video", return_value="test transcript"),
        patch("src.main.publish_video_ingested"),
        patch("src.main.db_insert_video"),
    ):
        fake_video = io.BytesIO(b"\x00" * 16)
        r = client.post(
            "/videos",
            data={"creator_id": "c0001", "category": "music", "duration_s": "15.0"},
            files={"file": ("test.mp4", fake_video, "video/mp4")},
        )
    assert r.status_code == 200
    body = r.json()
    assert "video_id" in body
    assert body["status"] == "ingested"
    assert body["video_id"].startswith("v")

def test_post_video_missing_creator_returns_422():
    r = client.post(
        "/videos",
        data={"category": "music", "duration_s": "15.0"},
        files={"file": ("test.mp4", io.BytesIO(b"\x00"), "video/mp4")},
    )
    assert r.status_code == 422
