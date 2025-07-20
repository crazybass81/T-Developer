#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}T-Developer v1.0 Deployment Verification${NC}"
echo "========================================="

# Check if backend is running
echo -n "Checking if backend is running... "
if systemctl is-active --quiet tdeveloper; then
  echo -e "${GREEN}✓ Backend is running${NC}"
else
  echo -e "${RED}✗ Backend is not running${NC}"
  echo "Try starting it with: sudo systemctl start tdeveloper"
  exit 1
fi

# Get backend URL
EC2_PUBLIC_DNS=$(curl -s http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || echo "localhost")
BACKEND_URL="http://${EC2_PUBLIC_DNS}:8000"

# Check backend health
echo -n "Checking backend health... "
if curl -s "${BACKEND_URL}/health" > /dev/null; then
  echo -e "${GREEN}✓ Backend is healthy${NC}"
else
  echo -e "${RED}✗ Backend health check failed${NC}"
  echo "Check logs with: sudo journalctl -u tdeveloper -f"
  exit 1
fi

# Check S3 frontend
echo -n "Checking S3 frontend bucket... "
FRONTEND_BUCKET="tdeveloper-frontend"
REGION=$(aws configure get region)
if aws s3api head-bucket --bucket ${FRONTEND_BUCKET} 2>/dev/null; then
  echo -e "${GREEN}✓ Frontend bucket exists${NC}"
  
  # Check if website hosting is enabled
  if aws s3api get-bucket-website --bucket ${FRONTEND_BUCKET} 2>/dev/null; then
    echo -e "${GREEN}✓ Website hosting is enabled${NC}"
    
    # Get website URL
    WEBSITE_URL="http://${FRONTEND_BUCKET}.s3-website-${REGION}.amazonaws.com"
    echo "Frontend URL: ${WEBSITE_URL}"
    
    # Check if index.html exists
    if aws s3 ls s3://${FRONTEND_BUCKET}/index.html 2>/dev/null; then
      echo -e "${GREEN}✓ index.html exists${NC}"
    else
      echo -e "${RED}✗ index.html not found${NC}"
      echo "Deploy the frontend with: ./deploy_frontend.sh"
    fi
  else
    echo -e "${RED}✗ Website hosting not enabled${NC}"
    echo "Deploy the frontend with: ./deploy_frontend.sh"
  fi
else
  echo -e "${RED}✗ Frontend bucket not found${NC}"
  echo "Deploy the frontend with: ./deploy_frontend.sh"
fi

# Check DynamoDB tables
echo -n "Checking DynamoDB tables... "
TABLE_PREFIX=$(grep DYNAMODB_TABLE_PREFIX /home/ec2-user/T-Developer/.env | cut -d'=' -f2)
if aws dynamodb list-tables | grep -q "${TABLE_PREFIX}"; then
  echo -e "${GREEN}✓ DynamoDB tables exist${NC}"
else
  echo -e "${YELLOW}⚠ DynamoDB tables not found${NC}"
  echo "They will be created when you run the application"
fi

# Check Lambda settings
echo -n "Checking Lambda settings... "
if grep -q "USE_LAMBDA_NOTIFIER=false" /home/ec2-user/T-Developer/.env && \
   grep -q "USE_LAMBDA_TEST_EXECUTOR=false" /home/ec2-user/T-Developer/.env; then
  echo -e "${GREEN}✓ Lambda features are disabled (v1.0 mode)${NC}"
else
  echo -e "${RED}✗ Lambda features may be enabled${NC}"
  echo "For v1.0, ensure these settings in .env:"
  echo "USE_LAMBDA_NOTIFIER=false"
  echo "USE_LAMBDA_TEST_EXECUTOR=false"
  echo "USE_LAMBDA_CODE_GENERATOR=false"
fi

echo -e "\n${GREEN}Deployment Verification Complete${NC}"
echo "Next steps:"
echo "1. Create a project via the frontend or API"
echo "2. Submit a task and monitor its progress"
echo "3. Verify Slack notifications and GitHub PR creation"
echo "4. Check task results (plan, diff, test log)"