#!/bin/sh
set -e

echo "=== Wanderly Production Startup ==="

echo "1. Applying Alembic database migrations..."
alembic upgrade head

echo "2. Seeding initial travel destinations (idempotent)..."
python -m app.seed.seed_data || echo "Seeding completed or already present"

echo "3. Starting Wanderly FastAPI production server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips='*'
