#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Tagging T-Developer v1.0 Release${NC}"
echo "=================================="

# Get the absolute path to the T-Developer directory
T_DEVELOPER_DIR=$(realpath $(dirname $(dirname $0)))
cd $T_DEVELOPER_DIR

# Check if git is initialized
if [ ! -d ".git" ]; then
  echo -e "${RED}Error: .git directory not found. Is this a git repository?${NC}"
  exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  echo -e "${RED}Error: There are uncommitted changes in the repository.${NC}"
  echo "Please commit or stash your changes before tagging."
  exit 1
fi

# Create the tag
echo "Creating git tag v1.0..."
git tag -a v1.0 -m "T-Developer v1.0 - EC2-based release without Lambda dependencies"

# Push the tag
echo "Pushing tag to remote repository..."
git push origin v1.0

echo -e "\n${GREEN}T-Developer v1.0 has been tagged!${NC}"
echo "This version is now frozen as the EC2-only implementation."
echo "Future Lambda-based development should proceed on the main branch."