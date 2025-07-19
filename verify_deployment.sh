#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8001
FRONTEND_PORT=3000
BACKEND_URL="http://localhost:${BACKEND_PORT}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"

echo -e "${GREEN}T-Developer v1.0 Deployment Verification${NC}"
echo "========================================"

# Check if backend is running
echo -n "Checking if backend is running... "
if curl -s "${BACKEND_URL}/health" > /dev/null; then
  echo -e "${GREEN}✓ Backend is running${NC}"
else
  echo -e "${RED}✗ Backend is not running${NC}"
  echo "Starting backend..."
  cd ~/T-Developer
  source venv/bin/activate
  uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload &
  sleep 3
  if curl -s "${BACKEND_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend started successfully${NC}"
  else
    echo -e "${RED}✗ Failed to start backend${NC}"
    exit 1
  fi
fi

# Check if frontend is running
echo -n "Checking if frontend is running... "
if curl -s "${FRONTEND_URL}" > /dev/null; then
  echo -e "${GREEN}✓ Frontend is running${NC}"
else
  echo -e "${RED}✗ Frontend is not running${NC}"
  echo "Starting frontend..."
  cd ~/T-Developer/frontend
  npm start &
  sleep 10
  if curl -s "${FRONTEND_URL}" > /dev/null; then
    echo -e "${GREEN}✓ Frontend started successfully${NC}"
  else
    echo -e "${RED}✗ Failed to start frontend${NC}"
    exit 1
  fi
fi

# Check AWS resources
echo -n "Checking AWS credentials... "
if aws sts get-caller-identity > /dev/null 2>&1; then
  echo -e "${GREEN}✓ AWS credentials are valid${NC}"
else
  echo -e "${RED}✗ AWS credentials are not valid${NC}"
  echo "Please configure AWS credentials and try again"
  exit 1
fi

# Check DynamoDB tables
echo -n "Checking DynamoDB tables... "
TABLE_PREFIX=$(grep DYNAMODB_TABLE_PREFIX ~/T-Developer/.env | cut -d'=' -f2)
if aws dynamodb list-tables | grep -q "${TABLE_PREFIX}"; then
  echo -e "${GREEN}✓ DynamoDB tables exist${NC}"
else
  echo -e "${RED}✗ DynamoDB tables do not exist${NC}"
  echo "They will be created when you run the application"
fi

# Check S3 bucket
echo -n "Checking S3 bucket... "
S3_BUCKET=$(grep S3_BUCKET_NAME ~/T-Developer/.env | cut -d'=' -f2)
if aws s3 ls "s3://${S3_BUCKET}" > /dev/null 2>&1; then
  echo -e "${GREEN}✓ S3 bucket exists${NC}"
else
  echo -e "${RED}✗ S3 bucket does not exist${NC}"
  echo "It will be created when you run the application"
fi

# Check GitHub connectivity
echo -n "Checking GitHub connectivity... "
GITHUB_TOKEN=$(grep GITHUB_TOKEN ~/T-Developer/.env | cut -d'=' -f2)
GITHUB_OWNER=$(grep GITHUB_OWNER ~/T-Developer/.env | cut -d'=' -f2)
GITHUB_REPO=$(grep GITHUB_REPO ~/T-Developer/.env | cut -d'=' -f2)
if curl -s -H "Authorization: token ${GITHUB_TOKEN}" "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}" | grep -q "id"; then
  echo -e "${GREEN}✓ GitHub repository is accessible${NC}"
else
  echo -e "${RED}✗ GitHub repository is not accessible${NC}"
  echo "Please check your GitHub token and repository settings"
fi

# Check Slack connectivity
echo -n "Checking Slack connectivity... "
SLACK_TOKEN=$(grep SLACK_BOT_TOKEN ~/T-Developer/.env | cut -d'=' -f2)
if curl -s -H "Authorization: Bearer ${SLACK_TOKEN}" "https://slack.com/api/auth.test" | grep -q "\"ok\":true"; then
  echo -e "${GREEN}✓ Slack connection is working${NC}"
else
  echo -e "${RED}✗ Slack connection is not working${NC}"
  echo "Please check your Slack token"
fi

echo -e "\n${GREEN}Verification complete!${NC}"
echo "Next steps:"
echo "1. Open ${FRONTEND_URL} in your browser"
echo "2. Create a project with GitHub repo and Slack channel"
echo "3. Submit a task and monitor its progress"
echo "4. Verify Slack notifications, GitHub PR, and S3 artifacts"
echo "5. When ready for production, build the frontend with:"
echo "   cd ~/T-Developer/frontend && REACT_APP_API_URL=\"https://your-api-url\" npm run build"
echo "6. Deploy to S3 with:"
echo "   aws s3 sync build/ s3://your-frontend-bucket/ --acl public-read"