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

# Kill any existing process on port 8000
kill $(lsof -t -i:8000) 2>/dev/null || true

# Start backend with detailed error output
echo "Starting backend on port 8000..."
PYTHONPATH=. uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug