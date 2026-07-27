from unittest.mock import patch, MagicMock
import numpy as np
import sys, pathlib

_ROOT = pathlib.Path(__file__).parents[2]
sys.path.insert(0, str(_ROOT / "proto/gen/python"))
sys.path.insert(0, str(_ROOT / "scripts"))  # idhash.point_id


def _make_fake_event():
    from video_ingested_pb2 import VideoIngested
    clip = np.random.randn(512).astype(np.float32)
    text = np.random.randn(384).astype(np.float32)
    return VideoIngested(
        video_id="v000001", creator_id="c0001", created_at=1000,
        clip_embed=clip.tobytes(), text_embed=text.tobytes(),
        category="music", duration_s=15.0,
    ).SerializeToString()


def test_process_event_writes_to_qdrant_and_redis():
    from src.processor import process_event
    mock_qdrant = MagicMock()
    mock_redis  = MagicMock()
    mock_projector = MagicMock(return_value=np.zeros(256, dtype=np.float32))

    with (
        patch("src.processor.get_qdrant", return_value=mock_qdrant),
        patch("src.processor.get_redis",  return_value=mock_redis),
        patch("src.processor.project",    mock_projector),
    ):
        process_event(_make_fake_event())

    assert mock_qdrant.upsert.called
    assert mock_redis.hset.called
    call_args = mock_redis.hset.call_args
    assert call_args[0][0] == "item:v000001"
