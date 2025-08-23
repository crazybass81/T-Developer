#!/bin/bash
# Script to run the T-Developer v2 API server

echo "========================================"
echo "Starting T-Developer v2 API Server"
echo "========================================"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Installing uvicorn..."
    pip install uvicorn fastapi pydantic
fi

# Set environment variables if needed
export AWS_DEFAULT_REGION=us-east-1

# Run the API server
echo "Starting API server on http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

python -m uvicorn backend.api.upgrade_api:app --host 0.0.0.0 --port 8000 --reload