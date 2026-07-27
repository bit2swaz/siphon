# build context = repo root
FROM python:3.13-slim
WORKDIR /app
COPY feature-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY feature-service/src/ ./src/
COPY proto/gen/python/ ./proto/gen/python/
COPY scripts/idhash.py ./idhash.py
ENV PYTHONPATH=/app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8007"]
