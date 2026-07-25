import importlib.util, sys, pathlib
import pytest

sys.path.insert(0, "proto/gen/python")

def test_python_protos_importable():
    gen = pathlib.Path("proto/gen/python")
    for name in ["video_ingested_pb2", "user_event_pb2", "model_server_pb2"]:
        spec = importlib.util.spec_from_file_location(name, gen / f"{name}.py")
        assert spec is not None, f"could not find {name}.py"
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)  # type: ignore[union-attr]

def test_videoing_ested_round_trip():
    from video_ingested_pb2 import VideoIngested  # type: ignore[import-untyped]
    import struct
    embed = struct.pack("<512f", *([0.1] * 512))
    msg = VideoIngested(video_id="v1", creator_id="c1", created_at=1000, clip_embed=embed, category="music", duration_s=15.0)
    raw = msg.SerializeToString()
    msg2 = VideoIngested()
    msg2.ParseFromString(raw)
    assert msg2.video_id == "v1"
    assert msg2.duration_s == 15.0

def test_user_event_round_trip():
    from user_event_pb2 import UserEvent  # type: ignore[import-untyped]
    msg = UserEvent(user_id="u1", video_id="v1", event_type="watch", timestamp=9999, watch_frac=0.75, session_id="s1")
    raw = msg.SerializeToString()
    msg2 = UserEvent()
    msg2.ParseFromString(raw)
    assert msg2.watch_frac == pytest.approx(0.75, abs=1e-5)
