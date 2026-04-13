#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    flask db upgrade
    echo "Migrations complete."
fi

exec gunicorn \
    -w "${GUNICORN_WORKERS:-4}" \
    -b "0.0.0.0:${PORT:-8000}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
