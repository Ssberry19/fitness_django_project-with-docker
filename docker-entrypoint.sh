#!/bin/bash

# Docker entrypoint script for Django Fitness Application
# This script will run migrations, collect static files, and start the server

set -e

# Function to check if PostgreSQL is ready
postgres_ready() {
  python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(
        dbname="${DB_NAME}",
        user="${DB_USER}",
        password="${DB_PASSWORD}",
        host="${DB_HOST}",
        port="${DB_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready
until postgres_ready; do
  echo "PostgreSQL is unavailable - waiting..."
  sleep 2
done
echo "PostgreSQL is up - continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if DJANGO_SUPERUSER_* environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput
fi

# Start server
echo "Starting server..."
# exec gunicorn fitness_django.wsgi:application --bind 0.0.0.0:8000
exec python manage.py runserver 0.0.0.0:8004
