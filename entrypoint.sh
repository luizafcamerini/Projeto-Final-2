#!/bin/sh
set -e

# Wait for DB? Optional: user can add wait-for-it logic if needed.

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server: $@"
exec "$@"
