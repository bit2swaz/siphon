import os

KAFKA_BOOTSTRAP  = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC      = "video.ingested"
POSTGRES_DSN     = (
    f"postgresql://{os.getenv('POSTGRES_USER','siphon')}"
    f":{os.getenv('POSTGRES_PASSWORD','siphon')}"
    f"@{os.getenv('POSTGRES_HOST','postgres')}"
    f":{os.getenv('POSTGRES_PORT','5432')}"
    f"/{os.getenv('POSTGRES_DB','siphon')}"
)
WHISPER_MODEL    = os.getenv("WHISPER_MODEL", "base")
CLIP_MODEL       = os.getenv("CLIP_MODEL", "ViT-B/32")
CLIP_DIM         = 512   # ViT-B/32 output dim; update if CLIP_MODEL changes
TEXT_DIM         = 384   # all-MiniLM-L6-v2 output dim
