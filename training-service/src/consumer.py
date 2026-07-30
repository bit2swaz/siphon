import sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "proto/gen/python"))

from user_event_pb2 import UserEvent

_POSITIVE_TYPES = {"like", "share", "replay"}
_VALID_TYPES    = {"watch", "like", "share", "skip", "replay"}


def buffer_event(raw_bytes: bytes, conn) -> int:
    """Parse UserEvent, insert into interactions, return label (0 or 1)."""
    ev = UserEvent()
    ev.ParseFromString(raw_bytes)

    # Validate at trust boundary: Kafka is unauthed so any process can inject events
    # Unknown event_type -> drop. Out-of-range watch_frac (including NaN/Inf) -> clamp to 0
    if ev.event_type not in _VALID_TYPES:
        return 0
    watch_frac = float(ev.watch_frac)
    if not (0.0 <= watch_frac <= 1.0):  # rejects NaN, Inf, -Inf
        watch_frac = 0.0

    label = 1 if (watch_frac >= 0.5 or ev.event_type in _POSITIVE_TYPES) else 0
    now   = int(time.time() * 1000)

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO interactions(user_id, video_id, label, watch_frac, event_type, created_at) VALUES(%s,%s,%s,%s,%s,%s)",
            (ev.user_id, ev.video_id, label, watch_frac, ev.event_type, now),
        )
    conn.commit()
    return label
