#!/bin/bash

echo "🚀 Starting T-Developer UI System..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo -e "${BLUE}📦 Installing dependencies...${NC}"

# Install frontend dependencies
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# Install Python dependencies for API server
cd ..
pip install -q fastapi uvicorn python-socketio aiosqlite

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Start API server in background
echo -e "${BLUE}🔧 Starting API server...${NC}"
python3 api_server.py &
API_PID=$!
echo "API server PID: $API_PID"

# Wait for API server to start
sleep 3

# Start frontend
echo -e "${BLUE}🎨 Starting frontend...${NC}"
cd frontend
npm run start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo -e "${GREEN}✅ T-Developer UI is running!${NC}"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Server: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping services...'; kill $API_PID $FRONTEND_PID; exit" INT
wait
