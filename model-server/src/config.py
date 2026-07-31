import os

MINIO_HOST       = os.getenv("MINIO_HOST", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET     = "siphon-models"
GRPC_PORT        = int(os.getenv("GRPC_PORT", 50051))
HTTP_PORT        = int(os.getenv("HTTP_PORT", 8004))
