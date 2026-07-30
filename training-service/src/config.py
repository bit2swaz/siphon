import os

KAFKA_BOOTSTRAP   = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC       = "user.events"
KAFKA_GROUP       = "training-service"
POSTGRES_DSN      = (
    f"postgresql://{os.getenv('POSTGRES_USER','siphon')}"
    f":{os.getenv('POSTGRES_PASSWORD','siphon')}"
    f"@{os.getenv('POSTGRES_HOST','postgres')}"
    f":{os.getenv('POSTGRES_PORT','5432')}"
    f"/{os.getenv('POSTGRES_DB','siphon')}"
)
QDRANT_HOST       = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT       = int(os.getenv("QDRANT_PORT", 6333))
MINIO_HOST        = os.getenv("MINIO_HOST", "minio:9000")
MINIO_ACCESS_KEY  = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY  = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET      = "siphon-models"
REDIS_HOST        = os.getenv("REDIS_HOST", "redis")
REDIS_PORT        = int(os.getenv("REDIS_PORT", 6379))
RETRAIN_EVERY_N   = int(os.getenv("RETRAIN_EVERY_N", 10000))
FEATURE_SERVICE_URL = os.getenv("FEATURE_SERVICE_URL", "http://feature-service:8007")
MODEL_SERVER_URL    = os.getenv("MODEL_SERVER_URL",   "http://model-server:8004")
USER_FEAT_DIM     = 24   # 4 rate features + 20 category one-hot
ITEM_FEAT_DIM     = 256
EMBED_DIM         = 256
