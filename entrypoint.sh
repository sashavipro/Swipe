#!/bin/sh

set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Applying database migrations..."
    alembic upgrade head
    echo "Migrations applied successfully."
else
    echo "Skipping migrations (RUN_MIGRATIONS not set)."
fi

exec "$@"
