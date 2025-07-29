#!/bin/bash
# check-requirements.sh

echo "🔍 개발 환경 체크 시작..."

# Node.js 버전 확인
NODE_VERSION=$(node -v 2>/dev/null)
if [[ ! "$NODE_VERSION" =~ ^v18\.|^v20\.|^v22\. ]]; then
    echo "❌ Node.js 18+ 필요 (현재: $NODE_VERSION)"
    exit 1
fi

# Python 버전 확인
PYTHON_VERSION=$(python3 --version 2>/dev/null)
if [[ ! "$PYTHON_VERSION" =~ 3\.(9|10|11|12) ]]; then
    echo "❌ Python 3.9+ 필요 (현재: $PYTHON_VERSION)"
    exit 1
fi

# AWS CLI 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않음"
    exit 1
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않음"
    exit 1
fi

echo "✅ 모든 필수 도구가 설치되어 있습니다!"
echo "Node.js: $NODE_VERSION"
echo "Python: $PYTHON_VERSION"
echo "AWS CLI: $(aws --version)"
echo "Docker: $(docker --version)"