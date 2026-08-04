# Build context is the repo root so proto/gen/python is in reach.
# We install the CPU-only torch wheel (~250MB, against ~2GB for the CUDA build).
# The scorer runs fine on CPU: it checks torch.cuda.is_available() and falls back.
# Same approach ingest-service uses.
FROM python:3.13-slim
WORKDIR /app
COPY model-server/requirements.txt .
# CPU-only torch first (small index), remaining deps from PyPI.
RUN pip install --no-cache-dir torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt
COPY model-server/src/ ./src/
COPY proto/gen/python/ ./proto/gen/python/
ENV PYTHONPATH=/app:/app/proto/gen/python
EXPOSE 8004 50051
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"]
