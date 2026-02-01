#!/usr/bin/env bash
set -e

pg_ctlcluster 16 main start

su postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='voice_agent'\" | grep -q 1 || psql -c 'CREATE DATABASE voice_agent'"

chroma run --host 0.0.0.0 --port "${CHROMA_PORT:-8100}" --path /app/chroma_data &

alembic upgrade head

if [ "${SEED_DATA:-false}" = "true" ]; then
    python -m scripts.seed_test_data || echo "Warning: seed script failed, continuing..."
fi

exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
