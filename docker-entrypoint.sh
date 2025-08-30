#!/bin/sh

set -e

echo "waiting for database at $DB_HOST:$DB_PORT..."

# wait until postgres is ready
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "database is up!"

# run dbs migrations
echo "applying migrations..."
python manage.py migrate --noinput

exec "$@"
