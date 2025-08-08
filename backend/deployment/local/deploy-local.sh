#!/bin/bash

# T-Developer Local Deployment Script
# 로컬 개발 환경 배포 스크립트

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}T-Developer Local Development Deployment${NC}"
echo "=========================================="
echo ""

# Function to check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}$1 is not installed${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ $1 is installed${NC}"
    return 0
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
check_command docker
check_command docker-compose
check_command python3
check_command pip3
check_command npm
check_command node

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p /home/ec2-user/T-DeveloperMVP/backend/logs
mkdir -p /home/ec2-user/T-DeveloperMVP/backend/cache
mkdir -p /home/ec2-user/T-DeveloperMVP/backend/downloads

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd /home/ec2-user/T-DeveloperMVP/backend
pip3 install --user -r requirements.txt || true

# Create .env file for local development
echo -e "${YELLOW}Creating .env file...${NC}"
cat > /home/ec2-user/T-DeveloperMVP/backend/.env << EOF
# T-Developer Local Environment Variables
ENVIRONMENT=development
PORT=8000
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/t_developer

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# AWS (Local/Mock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=local-development
AWS_SECRET_ACCESS_KEY=local-development
USE_LOCAL_AWS=true

# AI Keys (Replace with actual keys)
OPENAI_API_KEY=sk-local-development
ANTHROPIC_API_KEY=sk-ant-local-development

# Storage
DOWNLOAD_PATH=/home/ec2-user/T-DeveloperMVP/backend/downloads
CACHE_PATH=/home/ec2-user/T-DeveloperMVP/backend/cache

# Frontend
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
EOF

echo -e "${GREEN}.env file created${NC}"

# Start Docker Compose services
echo -e "${YELLOW}Starting Docker services...${NC}"
cd /home/ec2-user/T-DeveloperMVP/backend/deployment/ecs

# Check if docker-compose is already running
if docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}Docker services are already running. Restarting...${NC}"
    docker-compose down
fi

# Start only essential services for local development
docker-compose up -d postgres redis nginx

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"
docker-compose ps

echo -e "${GREEN}Docker services started${NC}"

# Create database if not exists
echo -e "${YELLOW}Setting up database...${NC}"
docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE t_developer;" 2>/dev/null || true

# Start backend API server
echo -e "${YELLOW}Starting backend API server...${NC}"
cd /home/ec2-user/T-DeveloperMVP/backend

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the API server in background
echo -e "${YELLOW}Starting API server on port 8000...${NC}"
nohup python3 -m uvicorn src.api.squad_api:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!
echo "API Server PID: $API_PID"

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}API is ready!${NC}"
        break
    fi
    echo "Attempt $i/30: Waiting for API..."
    sleep 2
done

# Start frontend
echo -e "${YELLOW}Starting frontend...${NC}"
cd /home/ec2-user/T-DeveloperMVP/frontend

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Kill any existing process on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Start frontend in background
nohup npm run dev > ../backend/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Summary
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Local Deployment Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Services Running:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - API Server: http://localhost:8000"
echo "  - Frontend: http://localhost:5173"
echo "  - Nginx Proxy: http://localhost:80"
echo ""
echo "Logs:"
echo "  - API: backend/logs/api.log"
echo "  - Frontend: backend/logs/frontend.log"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "To stop services:"
echo "  - Docker: cd backend/deployment/ecs && docker-compose down"
echo "  - API: kill $API_PID"
echo "  - Frontend: kill $FRONTEND_PID"
echo ""

# Create stop script
cat > /home/ec2-user/T-DeveloperMVP/stop-local.sh << EOF
#!/bin/bash
echo "Stopping T-Developer services..."
cd /home/ec2-user/T-DeveloperMVP/backend/deployment/ecs && docker-compose down
kill $API_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
echo "Services stopped"
EOF
chmod +x /home/ec2-user/T-DeveloperMVP/stop-local.sh

echo "Stop script created: /home/ec2-user/T-DeveloperMVP/stop-local.sh"