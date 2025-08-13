#!/bin/bash

# Simple Local Deployment without Docker
# 도커 없이 간단한 로컬 배포

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}T-Developer Simple Local Deployment${NC}"
echo "===================================="
echo ""

# Kill existing processes
echo -e "${YELLOW}Stopping existing services...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p /home/ec2-user/T-DeveloperMVP/backend/logs
mkdir -p /home/ec2-user/T-DeveloperMVP/backend/cache
mkdir -p /home/ec2-user/T-DeveloperMVP/backend/downloads

# Install minimal Python dependencies
echo -e "${YELLOW}Installing minimal Python dependencies...${NC}"
cd /home/ec2-user/T-DeveloperMVP/backend
pip3 install --user fastapi uvicorn aiofiles python-multipart pydantic python-dotenv 2>/dev/null || true

# Create minimal .env file
echo -e "${YELLOW}Creating .env file...${NC}"
cat > /home/ec2-user/T-DeveloperMVP/backend/.env << EOF
ENVIRONMENT=development
PORT=8000
LOG_LEVEL=DEBUG
DOWNLOAD_PATH=/home/ec2-user/T-DeveloperMVP/backend/downloads
CACHE_PATH=/home/ec2-user/T-DeveloperMVP/backend/cache
FRONTEND_URL=http://localhost:5173
USE_LOCAL_MODE=true
EOF

# Create a simple test API if main.ts doesn't work
echo -e "${YELLOW}
