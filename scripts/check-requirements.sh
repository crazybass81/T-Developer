#!/bin/bash
# check-requirements.sh

echo "🔍 개발 환경 체크 시작..."

# Node.js 버전 확인
NODE_VERSION=$(node -v)
if [[ ! "$NODE_VERSION" =~ ^v18\.|^v20\.|^v22\. ]]; then
    echo "❌ Node.js 18+ 필요 (현재: $NODE_VERSION)"
    exit 1
fi
echo "✅ Node.js: $NODE_VERSION"

# Python 버전 확인
PYTHON_VERSION=$(python3 --version)
if [[ ! "$PYTHON_VERSION" =~ 3\.(9|10|11|12) ]]; then
    echo "❌ Python 3.9+ 필요 (현재: $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python: $PYTHON_VERSION"

# AWS CLI 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않음"
    exit 1
fi
AWS_VERSION=$(aws --version)
echo "✅ AWS CLI: $AWS_VERSION"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않음"
    exit 1
fi
DOCKER_VERSION=$(docker --version)
echo "✅ Docker: $DOCKER_VERSION"

# Git 확인
if ! command -v git &> /dev/null; then
    echo "❌ Git이 설치되지 않음"
    exit 1
fi
GIT_VERSION=$(git --version)
echo "✅ Git: $GIT_VERSION"

echo ""
echo "🎉 모든 필수 도구가 설치되어 있습니다!"
echo "📋 다음 단계: AWS 계정 설정 및 환경 변수 구성"