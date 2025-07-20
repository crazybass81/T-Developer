#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}T-Developer v1.0 Deployment Monitor${NC}"
echo "====================================="

# Check backend status
echo -e "\n${GREEN}Backend Status:${NC}"
echo "----------------"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if [[ $HEALTH_RESPONSE == *"\"status\":\"ok\""* ]]; then
  echo -e "${GREEN}✓ Backend is running and healthy${NC}"
  echo "  Version: $(echo $HEALTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")"
else
  echo -e "${RED}✗ Backend health check failed${NC}"
  echo "  Response: $HEALTH_RESPONSE"
fi

# Check detailed health
DETAILED_HEALTH=$(curl -s http://localhost:8000/health/detailed)
echo -e "\n${GREEN}System Stats:${NC}"
echo "-------------"
echo "  CPU Usage: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['system']['cpu_usage'])")%"
echo "  Memory Usage: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['system']['memory_usage'])")%"
echo "  Disk Usage: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['system']['disk_usage'])")%"
echo "  Uptime: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['system']['uptime_human'])")"

# Check connections
echo -e "\n${GREEN}Connections:${NC}"
echo "------------"
echo "  AWS: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['connections']['aws'])")"
echo "  GitHub: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['connections']['github'])")"
echo "  Slack: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['connections']['slack'])")"

# Check projects and tasks
echo -e "\n${GREEN}Projects and Tasks:${NC}"
echo "------------------"
echo "  Projects: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['projects'])")"
echo "  Total Tasks: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['tasks']['total'])")"
echo "  Completed Tasks: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['tasks']['completed'])")"
echo "  Error Tasks: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['tasks']['error'])")"
echo "  In Progress Tasks: $(echo $DETAILED_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['tasks']['in_progress'])")"

# Check frontend
echo -e "\n${GREEN}Frontend Status:${NC}"
echo "---------------"
FRONTEND_URL="http://tdeveloper-frontend.s3-website-us-east-1.amazonaws.com"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [[ $FRONTEND_STATUS == "200" ]]; then
  echo -e "${GREEN}✓ Frontend is accessible${NC}"
  echo "  URL: $FRONTEND_URL"
else
  echo -e "${RED}✗ Frontend check failed with status $FRONTEND_STATUS${NC}"
  echo "  URL: $FRONTEND_URL"
fi

# Check environment variables
echo -e "\n${GREEN}Environment Variables:${NC}"
echo "---------------------"
ENV_FILE="/home/ec2-user/T-Developer/.env"
if [[ -f "$ENV_FILE" ]]; then
  echo -e "${GREEN}✓ Environment file exists${NC}"
  
  # Check Lambda settings
  if grep -q "USE_LAMBDA_NOTIFIER=false" "$ENV_FILE" && \
     grep -q "USE_LAMBDA_TEST_EXECUTOR=false" "$ENV_FILE"; then
    echo -e "${GREEN}✓ Lambda features are disabled (v1.0 mode)${NC}"
  else
    echo -e "${YELLOW}⚠ Lambda features may be enabled${NC}"
    echo "  For v1.0, ensure these settings in .env:"
    echo "  USE_LAMBDA_NOTIFIER=false"
    echo "  USE_LAMBDA_TEST_EXECUTOR=false"
  fi
else
  echo -e "${RED}✗ Environment file not found${NC}"
fi

echo -e "\n${GREEN}Deployment Status: OPERATIONAL${NC}"