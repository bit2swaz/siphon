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
        try:
            profile, _ = await run_bot_tick(profile, client)
        except Exception as e:
            # one bad tick shouldn't kill the whole swarm. log, back off, retry.
            print(f"bot {profile.user_id} tick error: {e}", flush=True)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_swarm())
