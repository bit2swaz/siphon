from functools import lru_cache

from confluent_kafka import Producer
from video_ingested_pb2 import VideoIngested
from .config import KAFKA_BOOTSTRAP, KAFKA_TOPIC


@lru_cache(maxsize=None)
def _get_producer() -> Producer:
    return Producer({"bootstrap.servers": KAFKA_BOOTSTRAP, "acks": "all", "retries": 3})


def publish_video_ingested(event: VideoIngested) -> None:
    _get_producer().produce(
        KAFKA_TOPIC,
        key=event.video_id.encode(),
        value=event.SerializeToString(),
    )
