# httpx AsyncClient get/post
from __future__ import annotations
import asyncio, random
import numpy as np

from .config import FEED_API_URL, EVENT_API_URL, SPEED_MULTIPLIER, DRIFT_EVERY_N_TICKS
from .profile import UserProfile, watch_probability, drift

# global tick counter, one entry per user (N=500 → bounded). move onto
# the profile if the swarm ever spans processes
_tick_counts: dict[str, int] = {}


async def run_bot_tick(profile: UserProfile, client) -> tuple[UserProfile, int]:
    """One tick: fetch feed, watch/skip each video, emit events. Returns (updated_profile, events_emitted)."""
    uid = profile.user_id
    _tick_counts[uid] = _tick_counts.get(uid, 0) + 1

    try:
        resp = await client.get(f"{FEED_API_URL}/feed", params={"user_id": uid, "limit": 20})
        if resp.status_code != 200:
            return profile, 0
        feed = resp.json().get("feed", [])
    except Exception:
        return profile, 0

    events_emitted = 0
    for item in feed:
        duration_s = float(item.get("duration_s", 15.0))
        # feed-api returns no embed -> fall back to a random probe vector
        embed = item.get("embed") or np.random.randn(256).tolist()

        p_watch = watch_probability(profile, embed)
        watch_frac = float(np.random.beta(
            a=max(0.5, p_watch * 5),
            b=max(0.5, (1 - p_watch) * 5),
        ))
        payload = {
            "user_id":     uid,
            "video_id":    item["video_id"],
            "event_type":  _choose_event_type(watch_frac, profile.like_rate_bias),
            "watch_ms":    int(watch_frac * duration_s * 1000),
            "duration_ms": int(duration_s * 1000),
        }
        try:
            await client.post(f"{EVENT_API_URL}/events", json=payload)
            events_emitted += 1
        except Exception:
            pass

        # sleep proportional to simulated watch time
        await asyncio.sleep(watch_frac * duration_s / SPEED_MULTIPLIER)

    if _tick_counts[uid] % DRIFT_EVERY_N_TICKS == 0:
        profile = drift(profile)

    return profile, events_emitted


def _choose_event_type(watch_frac: float, like_bias: float) -> str:
    if watch_frac < 0.2:
        return "skip"
    if watch_frac > 0.8 and random.random() < like_bias:
        return random.choice(["like", "replay", "share"])
    return "watch"
