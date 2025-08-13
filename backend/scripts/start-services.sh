#!/bin/bash

echo "🚀 Starting T-Developer Services..."

# Kill existing processes on ports
echo "Cleaning up existing processes..."
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null

# Start backend
echo "Starting backend..."
cd /home/ec2-user/T-DeveloperMVP/backend
npm start &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd /home/ec2-user/T-DeveloperMVP/frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "Backend PID: $BACKEND_PID (http://localhost:8000)"
echo "Frontend PID: $FRONTEND_PID (http://localhost:5173)"
echo ""
echo "To stop services, run: kill $BACKEND_PID $FRONTEND_PID"

# Keep script running
wait
