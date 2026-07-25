.PHONY: up down seed test proto lint

up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up -d --wait

down:
	docker compose down -v

seed:
	docker compose run --rm \
	  -e PYTHONPATH=/app \
	  -e POSTGRES_HOST=postgres \
	  -e POSTGRES_USER=$${POSTGRES_USER:-siphon} \
	  -e POSTGRES_PASSWORD=$${POSTGRES_PASSWORD:-siphon} \
	  -e POSTGRES_DB=$${POSTGRES_DB:-siphon} \
	  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
	  -e QDRANT_HOST=qdrant \
	  -e REDIS_HOST=redis \
	  -e MINIO_HOST=minio:9000 \
	  -v $$(pwd)/scripts:/app/scripts \
	  -v $$(pwd)/proto:/proto \
	  --network siphon_siphon-net \
	  python:3.13-slim bash -c "pip install -q psycopg2-binary redis kafka-python qdrant-client minio numpy && python /app/scripts/seed.py"

test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --wait
	pytest tests/integration/ -v
	docker compose -f docker-compose.yml -f docker-compose.test.yml down -v

proto:
	./scripts/compile_proto.sh

lint:
	cd ingest-service && ruff check src/ tests/
	cd feature-service && ruff check src/ tests/
	cd training-service && ruff check src/ tests/
	cd sim-engine && ruff check src/ tests/
	cd user-event-service && go vet ./...
	cd feed-api && go vet ./...
	cd dashboard-api && go vet ./...
