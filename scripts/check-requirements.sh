#\!/bin/bash

# T-Developer Environment Check Script
# Phase 0: Verify all requirements are installed

echo "======================================"
echo "🔍 T-Developer 개발 환경 체크 시작..."
echo "======================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $2 설치됨${NC}"
        return 0
    else
        echo -e "${RED}❌ $2 설치 필요${NC}"
        return 1
    fi
}

echo ""
echo "1. 필수 도구 확인"
echo "-------------------"

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    if [[ "$NODE_VERSION" =~ ^v(18|19|20|21|22) ]]; then
        echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
    else
        echo -e "${YELLOW}⚠️  Node.js: $NODE_VERSION (18+ 권장)${NC}"
    fi
else
    echo -e "${RED}❌ Node.js 설치 필요${NC}"
fi

# npm
check_command npm "npm"

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 설치 필요${NC}"
fi

# Git
check_command git "Git"

# Docker
check_command docker "Docker"

# AWS CLI
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1)
    echo -e "${GREEN}✅ AWS CLI: $AWS_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  AWS CLI 미설치 (선택사항)${NC}"
fi

echo ""
echo "======================================"
echo "📋 체크 완료\!"
echo "======================================"
