#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Committing T-Developer v1.0 Changes${NC}"
echo "=================================="

# Get the absolute path to the T-Developer directory
T_DEVELOPER_DIR=$(realpath $(dirname $(dirname $0)))
cd $T_DEVELOPER_DIR

# Check if git is initialized
if [ ! -d ".git" ]; then
  echo -e "${RED}Error: .git directory not found. Is this a git repository?${NC}"
  exit 1
fi

# Show changes
echo -e "${YELLOW}Changes to be committed:${NC}"
git status --short

# Confirm with user
read -p "Do you want to commit these changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Commit aborted"
  exit 0
fi

# Add all changes
git add .

# Commit
git commit -m "Finalize T-Developer v1.0 - EC2-based implementation without Lambda dependencies"

# Push
echo "Pushing changes to remote repository..."
git push

echo -e "\n${GREEN}Changes committed and pushed successfully!${NC}"
echo "You can now tag the v1.0 release with: ./scripts/tag_v1.0.sh"