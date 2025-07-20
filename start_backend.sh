#!/bin/bash
set -e

# Navigate to project directory
cd ~/T-Developer

# Activate virtual environment
source venv/bin/activate

# Make sure .env file exists
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env file from .env.example"
  echo "Please edit .env with your actual credentials"
fi

# Find available port
find_available_port() {
    local base_port=$1
    local port=$base_port
    while lsof -i:$port >/dev/null 2>&1; do
        port=$((port + 1))
    done
    echo $port
}

# Find available port for backend
BACKEND_PORT=$(find_available_port 8000)

# Start backend with detailed error output
echo "Starting backend on port $BACKEND_PORT..."
PYTHONPATH=. uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload --log-level debug