# build context = repo root
FROM python:3.13-slim
WORKDIR /app
COPY feature-service/requirements.txt .
# CPU-only torch first (~250MB vs multi-GB CUDA build); remaining deps from PyPI.
RUN pip install --no-cache-dir torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt
COPY feature-service/src/ ./src/
COPY proto/gen/python/ ./proto/gen/python/
COPY scripts/idhash.py ./idhash.py
ENV PYTHONPATH=/app:/app/proto/gen/python
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8007"]
