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

# Create logs directory if it doesn't exist
mkdir -p $T_DEVELOPER_DIR/logs
echo "Created logs directory: $T_DEVELOPER_DIR/logs"

# Copy the systemd service file
SERVICE_FILE="/etc/systemd/system/tdeveloper.service"
echo "Creating systemd service file: $SERVICE_FILE"
cp $T_DEVELOPER_DIR/scripts/tdeveloper.service $SERVICE_FILE

# Update paths in the service file if needed
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$T_DEVELOPER_DIR|" $SERVICE_FILE
sed -i "s|EnvironmentFile=.*|EnvironmentFile=$T_DEVELOPER_DIR/.env|" $SERVICE_FILE
sed -i "s|StandardOutput=file:.*|StandardOutput=file:$T_DEVELOPER_DIR/logs/tdeveloper.out.log|" $SERVICE_FILE
sed -i "s|StandardError=file:.*|StandardError=file:$T_DEVELOPER_DIR/logs/tdeveloper.err.log|" $SERVICE_FILE

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