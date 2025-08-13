#!/bin/bash

# T-Developer ECS Entrypoint Script
set -e

# Function to wait for dependencies
wait_for_service() {
    local service=$1
    local port=$2
    local max_tries=30
    local tries=0

    echo "Waiting for $service on port $port..."

    while ! nc -z $service $port; do
        tries=$((tries + 1))
        if [ $tries -gt $max_tries ]; then
            echo "Failed to connect to $service after $max_tries attempts"
            exit 1
        fi
        echo "Attempt $tries/$max_tries: $service is not ready yet..."
        sleep 2
    done

    echo "$service is ready!"
}

# Set default environment variables
export ENVIRONMENT=${ENVIRONMENT:-production}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Run based on command
case "$1" in
    "api")
        echo "Starting T-Developer API Server..."
        exec uvicorn src.api.squad_api:app \
            --host 0.0.0.0 \
            --port $PORT \
            --workers $WORKERS \
            --log-level $LOG_LEVEL \
            --access-log \
            --use-colors
        ;;

    "worker")
        echo "Starting T-Developer Celery Worker..."
        exec celery -A src.tasks worker \
            --loglevel=$LOG_LEVEL \
            --concurrency=4 \
            --max-tasks-per-child=100
        ;;

    "beat")
        echo "Starting T-Developer Celery Beat..."
        exec celery -A src.tasks beat \
            --loglevel=$LOG_LEVEL
        ;;

    "migrate")
        echo "Running database migrations..."
        exec alembic upgrade head
        ;;

    "shell")
        echo "Starting Python shell..."
        exec python
        ;;

    *)
        echo "Unknown command: $1"
        echo "Available commands: api, worker, beat, migrate, shell"
        exit 1
        ;;
esac
