#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing T-Developer v1.0 as a systemd service${NC}"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root${NC}"
  echo "Try: sudo $0"
  exit 1
fi

# Get the absolute path to the T-Developer directory
T_DEVELOPER_DIR=$(realpath $(dirname $(dirname $0)))
echo "T-Developer directory: $T_DEVELOPER_DIR"

# Copy the systemd service file
SERVICE_FILE="/etc/systemd/system/tdeveloper.service"
echo "Creating systemd service file: $SERVICE_FILE"
cp $T_DEVELOPER_DIR/scripts/tdeveloper.service $SERVICE_FILE

# Update paths in the service file if needed
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$T_DEVELOPER_DIR|" $SERVICE_FILE
sed -i "s|EnvironmentFile=.*|EnvironmentFile=$T_DEVELOPER_DIR/.env|" $SERVICE_FILE
sed -i "s|ExecStart=.*|ExecStart=$T_DEVELOPER_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000|" $SERVICE_FILE

# Make sure .env file exists
if [ ! -f "$T_DEVELOPER_DIR/.env" ]; then
  echo "Creating .env file from .env.example"
  cp $T_DEVELOPER_DIR/.env.example $T_DEVELOPER_DIR/.env
  echo -e "${YELLOW}Please edit $T_DEVELOPER_DIR/.env with your actual credentials${NC}"
fi

# Make sure Lambda features are disabled for v1.0
echo "Ensuring Lambda features are disabled for v1.0"
if grep -q "USE_LAMBDA_NOTIFIER" "$T_DEVELOPER_DIR/.env"; then
  sed -i 's/USE_LAMBDA_NOTIFIER=.*/USE_LAMBDA_NOTIFIER=false/' "$T_DEVELOPER_DIR/.env"
else
  echo "USE_LAMBDA_NOTIFIER=false" >> "$T_DEVELOPER_DIR/.env"
fi

if grep -q "USE_LAMBDA_TEST_EXECUTOR" "$T_DEVELOPER_DIR/.env"; then
  sed -i 's/USE_LAMBDA_TEST_EXECUTOR=.*/USE_LAMBDA_TEST_EXECUTOR=false/' "$T_DEVELOPER_DIR/.env"
else
  echo "USE_LAMBDA_TEST_EXECUTOR=false" >> "$T_DEVELOPER_DIR/.env"
fi

# Install pytest if not already installed
echo "Ensuring pytest is installed"
$T_DEVELOPER_DIR/venv/bin/pip install pytest

# Reload systemd
echo "Reloading systemd"
systemctl daemon-reload

# Enable the service
echo "Enabling tdeveloper service"
systemctl enable tdeveloper.service

# Start the service
echo "Starting tdeveloper service"
systemctl start tdeveloper.service

# Check status
echo "Service status:"
systemctl status tdeveloper.service --no-pager

echo -e "\n${GREEN}T-Developer v1.0 service installed and started!${NC}"
echo "You can manage it with these commands:"
echo "  sudo systemctl start tdeveloper"
echo "  sudo systemctl stop tdeveloper"
echo "  sudo systemctl restart tdeveloper"
echo "  sudo systemctl status tdeveloper"
echo "  sudo journalctl -u tdeveloper -f"