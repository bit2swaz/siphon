import psycopg2
from .config import POSTGRES_DSN

def db_insert_video(video_id: str, creator_id: str, category: str, duration_s: float, created_at: int) -> None:
    conn = psycopg2.connect(POSTGRES_DSN)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO videos(video_id,creator_id,category,duration_s,created_at) VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (video_id, creator_id, category, duration_s, created_at),
            )
    finally:
        conn.close()
