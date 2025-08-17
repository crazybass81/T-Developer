#!/bin/bash

# T-Developer Perfect Evolution Runner
# Executes a complete evolution cycle with all safety checks

set -e  # Exit on error

echo "==============================================="
echo "🧬 T-Developer Perfect Evolution Runner"
echo "==============================================="
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend server not running. Starting it now..."
    cd backend
    python main.py &
    BACKEND_PID=$!
    echo "Waiting for backend to start..."
    sleep 5

    # Check again
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "❌ Failed to start backend server"
        exit 1
    fi
    echo "✅ Backend server started (PID: $BACKEND_PID)"
else
    echo "✅ Backend server is running"
fi

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  AWS credentials not set. Loading from .env if available..."
    if [ -f .env ]; then
        export $(cat .env | xargs)
    else
        echo "❌ No AWS credentials found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        exit 1
    fi
fi

# Check for required tools
echo ""
echo "Checking required tools..."
for tool in black autopep8 doq pyupgrade; do
    if ! command -v $tool &> /dev/null; then
        echo "⚠️  $tool not found. Installing..."
        pip install $tool
    else
        echo "✅ $tool installed"
    fi
done

# Create test target if it doesn't exist
if [ ! -d "/tmp/test_evolution_target" ]; then
    echo ""
    echo "Creating test target project..."
    python scripts/create_test_target.py
fi

# Run the evolution
echo ""
echo "==============================================="
echo "🚀 Starting Evolution Cycle"
echo "==============================================="
echo ""

python scripts/run_perfect_evolution.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================="
    echo "✅ Evolution cycle completed successfully!"
    echo "==============================================="
    echo ""
    echo "📊 Check the following for results:"
    echo "  • evolution_results/ - Exported evolution data"
    echo "  • evolution_run.log - Detailed execution log"
    echo "  • /tmp/test_evolution_target - Modified code"
    echo ""
else
    echo ""
    echo "==============================================="
    echo "❌ Evolution cycle failed"
    echo "==============================================="
    echo "Check evolution_run.log for details"
    exit 1
fi
