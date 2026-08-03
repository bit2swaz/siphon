import asyncio, httpx
from .config import NUM_USERS, KUAIREC_PATH
from .profile import load_profiles
from .bot import run_bot_tick


async def run_swarm():
    profiles = load_profiles(NUM_USERS, kuairec_path=KUAIREC_PATH)
    print(f"sim-engine: starting {len(profiles)} bots", flush=True)

    async with httpx.AsyncClient(timeout=10.0) as client:
        await asyncio.gather(*[_bot_loop(p, client) for p in profiles])


async def _bot_loop(profile, client):
    while True:
        profile, _ = await run_bot_tick(profile, client)


if __name__ == "__main__":
    asyncio.run(run_swarm())
