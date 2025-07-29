#!/bin/bash

echo "🚀 Starting E2E Test Suite..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Set test environment
export NODE_ENV=test
export DYNAMODB_ENDPOINT=http://localhost:8000
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Clean up any existing containers
echo "🧹 Cleaning up existing test containers..."
docker stop $(docker ps -q --filter "ancestor=amazon/dynamodb-local") 2>/dev/null || true
docker stop $(docker ps -q --filter "ancestor=redis:7-alpine") 2>/dev/null || true

# Wait for cleanup
sleep 2

# Run E2E tests
echo "🧪 Running E2E tests..."
cd backend
npm run test:e2e

# Capture exit code
TEST_EXIT_CODE=$?

# Cleanup
echo "🧹 Cleaning up test environment..."
docker stop $(docker ps -q --filter "ancestor=amazon/dynamodb-local") 2>/dev/null || true
docker stop $(docker ps -q --filter "ancestor=redis:7-alpine") 2>/dev/null || true

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ E2E tests passed!"
else
    echo "❌ E2E tests failed!"
fi

exit $TEST_EXIT_CODE