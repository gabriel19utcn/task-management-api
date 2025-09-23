#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
WAIT_SECONDS=${DB_WAIT_SECONDS:-30}
SLEEP_INTERVAL=1

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT} (timeout: ${WAIT_SECONDS}s)..."
for (( i=0; i<WAIT_SECONDS; i++ )); do
  if python - <<'PY'
import os,sys,psycopg2
host=os.getenv('POSTGRES_HOST','db')
port=os.getenv('POSTGRES_PORT','5432')
user=os.getenv('POSTGRES_USER','postgres')
pwd=os.getenv('POSTGRES_PASSWORD','postgres')
db=os.getenv('POSTGRES_DB','postgres')
try:
    psycopg2.connect(host=host,port=port,user=user,password=pwd,dbname=db,connect_timeout=2).close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  then
    echo "PostgreSQL is up after $i seconds"; break
  fi
  sleep $SLEEP_INTERVAL
done

if [ "$i" -ge "$WAIT_SECONDS" ]; then
  echo "ERROR: PostgreSQL not reachable after ${WAIT_SECONDS}s" >&2
  exit 1
fi

# Only run migrations if this container is designated to do so (default: run in api)
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
if [ "$RUN_MIGRATIONS" = "true" ] && command -v alembic &> /dev/null; then
  echo "Running migrations..."
  alembic upgrade head || { echo "Migrations failed" >&2; exit 1; }
fi

exec "$@"
