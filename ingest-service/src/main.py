import tempfile, os, time, uuid

from fastapi import FastAPI, File, Form, UploadFile
from prometheus_client import make_asgi_app, Counter

from .embedder import extract_clip_embed, extract_text_embed, transcribe_video
from .publisher import publish_video_ingested
from .db import db_insert_video
from video_ingested_pb2 import VideoIngested

app = FastAPI(title="ingest-service")
app.mount("/metrics", make_asgi_app())

INGEST_COUNT = Counter("ingest_total", "Total videos ingested")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/videos")
async def ingest_video(
    file: UploadFile = File(...),
    creator_id: str = Form(...),
    category: str = Form(...),
    duration_s: float = Form(...),
):
    video_id = f"v{uuid.uuid4().hex[:12]}"
    created_at = int(time.time() * 1000)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        clip_embed = extract_clip_embed(tmp_path)
        transcript = transcribe_video(tmp_path)
        text_embed = extract_text_embed(transcript)
    finally:
        os.unlink(tmp_path)

    event = VideoIngested(
        video_id=video_id,
        creator_id=creator_id,
        created_at=created_at,
        clip_embed=clip_embed.tobytes(),
        text_embed=text_embed.tobytes(),
        category=category,
        duration_s=duration_s,
    )
    db_insert_video(video_id, creator_id, category, duration_s, created_at)
    publish_video_ingested(event)
    INGEST_COUNT.inc()
    return {"video_id": video_id, "status": "ingested"}
