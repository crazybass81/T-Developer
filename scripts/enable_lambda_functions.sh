#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Enabling Lambda functions for T-Developer${NC}"
echo "========================================="

# Get the absolute path to the T-Developer directory
T_DEVELOPER_DIR=$(realpath $(dirname $(dirname $0)))
ENV_FILE="$T_DEVELOPER_DIR/.env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo -e "${RED}.env file not found: $ENV_FILE${NC}"
  exit 1
fi

# Update .env file to enable Lambda functions
echo "Updating .env file to enable Lambda functions"

# Check if USE_LAMBDA_NOTIFIER already exists in .env
if grep -q "USE_LAMBDA_NOTIFIER" "$ENV_FILE"; then
  # Update existing setting
  sed -i 's/USE_LAMBDA_NOTIFIER=.*/USE_LAMBDA_NOTIFIER=true/' "$ENV_FILE"
else
  # Add new setting
  echo "USE_LAMBDA_NOTIFIER=true" >> "$ENV_FILE"
fi

# Check if USE_LAMBDA_TEST_EXECUTOR already exists in .env
if grep -q "USE_LAMBDA_TEST_EXECUTOR" "$ENV_FILE"; then
  # Update existing setting
  sed -i 's/USE_LAMBDA_TEST_EXECUTOR=.*/USE_LAMBDA_TEST_EXECUTOR=true/' "$ENV_FILE"
else
  # Add new setting
  echo "USE_LAMBDA_TEST_EXECUTOR=true" >> "$ENV_FILE"
fi

echo -e "${GREEN}Lambda functions enabled in .env file${NC}"

# Deploy Lambda functions
echo "Deploying Lambda functions..."
cd "$T_DEVELOPER_DIR"
bash lambda/deploy_lambdas.sh

# Restart the service if it's running
if systemctl is-active --quiet t-developer; then
  echo "Restarting T-Developer service..."
  sudo systemctl restart t-developer
  echo "Service restarted"
else
  echo "T-Developer service is not running"
fi

echo -e "\n${GREEN}Lambda functions enabled and deployed!${NC}"
echo "T-Developer will now use Lambda functions for:"
echo "  - Slack notifications"
echo "  - Test execution"