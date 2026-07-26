import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "proto/gen/python"))
from unittest.mock import patch, MagicMock
from video_ingested_pb2 import VideoIngested
from src.publisher import publish_video_ingested

def test_publish_calls_kafka_send():
    mock_producer = MagicMock()
    with patch("src.publisher._get_producer", return_value=mock_producer):
        event = VideoIngested(
            video_id="v000001",
            creator_id="c0001",
            created_at=1000000,
            clip_embed=bytes(512 * 4),
            text_embed=bytes(384 * 4),
            category="music",
            duration_s=15.0,
        )
        publish_video_ingested(event)
    mock_producer.produce.assert_called_once_with(
        "video.ingested",
        key=b"v000001",
        value=event.SerializeToString(),
    )
