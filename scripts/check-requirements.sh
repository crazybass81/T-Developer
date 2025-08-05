#!/bin/bash
# check-requirements.sh - T-Developer 개발 환경 체크

echo "🔍 개발 환경 체크 시작..."

# Node.js 버전 확인
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    if [[ "$NODE_VERSION" =~ ^v(18|19|20|21)\. ]]; then
        echo "✅ Node.js: $NODE_VERSION"
    else
        echo "❌ Node.js 18+ 필요 (현재: $NODE_VERSION)"
        exit 1
    fi
else
    echo "❌ Node.js가 설치되지 않음"
    exit 1
fi

# Python 버전 확인
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    if [[ "$PYTHON_VERSION" =~ Python\ 3\.(9|10|11|12)\. ]]; then
        echo "✅ Python: $PYTHON_VERSION"
    else
        echo "❌ Python 3.9+ 필요 (현재: $PYTHON_VERSION)"
        exit 1
    fi
else
    echo "❌ Python3가 설치되지 않음"
    exit 1
fi

# AWS CLI 확인
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d/ -f2 | cut -d' ' -f1)
    echo "✅ AWS CLI: $AWS_VERSION"
else
    echo "❌ AWS CLI가 설치되지 않음"
    exit 1
fi

# Docker 확인
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo "✅ Docker: $DOCKER_VERSION"
else
    echo "❌ Docker가 설치되지 않음"
    exit 1
fi

# Git 확인
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    echo "✅ Git: $GIT_VERSION"
else
    echo "❌ Git이 설치되지 않음"
    exit 1
fi

echo ""
echo "✅ 모든 필수 도구가 설치되어 있습니다!"
echo ""
echo "📋 다음 단계:"
echo "1. AWS 자격 증명 설정: aws configure"
echo "2. Docker 서비스 시작 확인"
echo "3. 프로젝트 의존성 설치"