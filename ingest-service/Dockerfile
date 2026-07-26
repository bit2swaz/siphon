# Build context is REPO ROOT (set in docker-compose.yml) so proto/gen is reachable
# python:3.11-slim + CPU-only torch wheel (~250MB vs 2GB GPU build).
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ingest-service/requirements.txt .
# CPU only torch first (tiny index URL); remaining deps from PyPI.
RUN pip install --no-cache-dir \
      torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY ingest-service/src/ ./src/
COPY proto/gen/python/ ./proto/gen/python/

ENV PYTHONPATH=/app:/app/proto/gen/python
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
