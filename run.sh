#!/bin/bash
set -e

# Run cleanup script to terminate any duplicate processes
echo "Cleaning up any duplicate processes..."
./cleanup_duplicates.sh

# Find available ports
find_available_port() {
    local base_port=$1
    local port=$base_port
    while lsof -i:$port >/dev/null 2>&1; do
        port=$((port + 1))
    done
    echo $port
}

# Find available ports for backend and frontend
BACKEND_PORT=$(find_available_port 8001)
FRONTEND_PORT=$(find_available_port 3000)

# Start backend
cd ~/T-Developer
source venv/bin/activate
echo "Starting backend on port $BACKEND_PORT..."
uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start frontend with custom port
cd ~/T-Developer/frontend
echo "Starting frontend on port $FRONTEND_PORT..."
PORT=$FRONTEND_PORT npm start &
FRONTEND_PID=$!

echo "T-Developer is now running!"
echo "Backend: http://localhost:$BACKEND_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Press Ctrl+C to stop"

# Keep script running until user presses Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait