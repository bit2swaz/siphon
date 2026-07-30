# build context = repo root
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY training-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY training-service/src/ ./src/
COPY proto/gen/python/ ./proto/gen/python/
COPY scripts/idhash.py ./scripts/idhash.py
ENV PYTHONPATH=/app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
