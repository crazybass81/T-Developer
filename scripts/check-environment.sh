#!/bin/bash

echo "🔍 T-Developer Phase 1 환경 체크 시작..."
echo "================================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 체크 결과 저장
CHECKS_PASSED=0
TOTAL_CHECKS=4

# Node.js 버전 확인
echo -n "Node.js 18+ 확인: "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | sed 's/v//')
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d. -f1)
    if [ "$MAJOR_VERSION" -ge 18 ]; then
        echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}❌ Node.js $NODE_VERSION (18+ 필요)${NC}"
    fi
else
    echo -e "${RED}❌ Node.js가 설치되지 않음${NC}"
fi

# Python 버전 확인
echo -n "Python 3.9+ 확인: "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -ge 9 ]; then
        echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}❌ Python $PYTHON_VERSION (3.9+ 필요)${NC}"
    fi
else
    echo -e "${RED}❌ Python3가 설치되지 않음${NC}"
fi

# AWS CLI 확인
echo -n "AWS CLI 확인: "
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
    # AWS 자격 증명 확인
    if aws sts get-caller-identity &> /dev/null; then
        echo -e "${GREEN}✅ AWS CLI $AWS_VERSION (자격증명 설정됨)${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  AWS CLI $AWS_VERSION (자격증명 필요)${NC}"
        echo "   aws configure를 실행하여 자격증명을 설정하세요"
    fi
else
    echo -e "${RED}❌ AWS CLI가 설치되지 않음${NC}"
fi

# Docker 확인
echo -n "Docker 확인: "
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        echo -e "${GREEN}✅ Docker $DOCKER_VERSION (실행 중)${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  Docker가 설치되어 있지만 실행되지 않음${NC}"
        echo "   Docker Desktop을 시작하세요"
    fi
else
    echo -e "${RED}❌ Docker가 설치되지 않음${NC}"
fi

echo "================================================"

# 결과 요약
if [ $CHECKS_PASSED -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}🎉 모든 환경 요구사항이 충족되었습니다! ($CHECKS_PASSED/$TOTAL_CHECKS)${NC}"
    echo ""
    echo "다음 단계:"
    echo "1. cd T-DeveloperMVP"
    echo "2. npm install"
    echo "3. pip install -r requirements.txt"
    echo "4. npm run phase1:start"
else
    echo -e "${RED}❌ 환경 설정이 완료되지 않았습니다 ($CHECKS_PASSED/$TOTAL_CHECKS)${NC}"
    echo ""
    echo "누락된 요구사항을 설치한 후 다시 실행하세요:"
    echo "./scripts/check-environment.sh"
fi

exit $((TOTAL_CHECKS - CHECKS_PASSED))