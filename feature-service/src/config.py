import os

KAFKA_BOOTSTRAP   = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC       = "video.ingested"
KAFKA_GROUP       = "feature-service"
QDRANT_HOST       = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT       = int(os.getenv("QDRANT_PORT", 6333))
REDIS_HOST        = os.getenv("REDIS_HOST", "redis")
REDIS_PORT        = int(os.getenv("REDIS_PORT", 6379))
MINIO_HOST        = os.getenv("MINIO_HOST", "minio:9000")
MINIO_ACCESS_KEY  = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY  = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET      = "siphon-models"
POSTGRES_DSN      = (
    f"postgresql://{os.getenv('POSTGRES_USER','siphon')}"
    f":{os.getenv('POSTGRES_PASSWORD','siphon')}"
    f"@{os.getenv('POSTGRES_HOST','postgres')}"
    f":{os.getenv('POSTGRES_PORT','5432')}"
    f"/{os.getenv('POSTGRES_DB','siphon')}"
)
