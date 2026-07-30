import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "proto/gen/python"))
from unittest.mock import MagicMock
from user_event_pb2 import UserEvent


def _make_event(event_type="watch", watch_frac=0.8) -> bytes:
    return UserEvent(
        user_id="u000001", video_id="v000001",
        event_type=event_type, timestamp=1000000,
        watch_frac=watch_frac, session_id="s1",
    ).SerializeToString()


def test_buffer_event_inserts_to_db():
    from src.consumer import buffer_event
    mock_conn = MagicMock()
    mock_cur  = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cur
    mock_conn.cursor.return_value.__exit__  = MagicMock(return_value=False)

    count = buffer_event(_make_event(event_type="watch", watch_frac=0.8), mock_conn)
    assert mock_cur.execute.called
    args = mock_cur.execute.call_args[0]
    assert "interactions" in args[0]
    assert count == 1  # label=1 (watch_frac >= 0.5)


def test_buffer_event_label_skip():
    from src.consumer import buffer_event
    mock_conn = MagicMock()
    mock_cur  = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cur
    mock_conn.cursor.return_value.__exit__  = MagicMock(return_value=False)

    count = buffer_event(_make_event(event_type="skip", watch_frac=0.2), mock_conn)
    insert_args = mock_cur.execute.call_args[0][1]
    assert insert_args[2] == 0  # label=0
