#!/bin/bash
set -e

# Kill any existing processes on ports 8001 and 3000
kill $(lsof -t -i:8001) 2>/dev/null || true
kill $(lsof -t -i:3000) 2>/dev/null || true

# Start backend
cd ~/T-Developer
source venv/bin/activate
echo "Starting backend on port 8001..."
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start frontend
cd ~/T-Developer/frontend
echo "Starting frontend on port 3000..."
npm start &
FRONTEND_PID=$!

echo "T-Developer is now running!"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop"

# Keep script running until user presses Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait