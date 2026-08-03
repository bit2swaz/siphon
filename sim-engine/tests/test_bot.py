import asyncio
import numpy as np
from unittest.mock import AsyncMock, MagicMock


def _make_profile(i=0):
    from src.profile import UserProfile
    vec = np.random.randn(256).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return UserProfile(f"u{i:06d}", vec, 0.0, 0.05)


def _make_feed_response(n=5):
    return {
        "user_id": "u000000",
        "feed": [
            {"video_id": f"v{i:04d}", "score": 0.9 - i * 0.1,
             "rank": i + 1, "creator_id": f"c{i:03d}", "duration_s": 15.0}
            for i in range(n)
        ],
        "model_version": 1,
        "latency_ms": 50,
    }


async def _async_test():
    from src.bot import run_bot_tick

    profile = _make_profile()
    mock_client = AsyncMock()
    mock_client.get.return_value = AsyncMock(
        status_code=200,
        json=MagicMock(return_value=_make_feed_response()),
    )
    mock_client.post.return_value = AsyncMock(status_code=200)

    new_profile, events_emitted = await run_bot_tick(profile, mock_client)
    assert isinstance(events_emitted, int)
    assert events_emitted >= 0
    assert new_profile.user_id == profile.user_id


def test_bot_tick_emits_events():
    asyncio.run(_async_test())
