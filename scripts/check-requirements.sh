#!/bin/bash
# T-Developer MVP - Requirements Check

echo "🔍 개발 환경 체크 시작..."

# Node.js 버전 확인
NODE_VERSION=$(node -v 2>/dev/null || echo "not installed")
if [[ ! "$NODE_VERSION" =~ ^v1[89]\.|^v2[0-9]\. ]]; then
    echo "❌ Node.js 18+ 필요 (현재: $NODE_VERSION)"
    exit 1
fi
echo "✅ Node.js: $NODE_VERSION"

# Python 버전 확인
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "not installed")
if [[ ! "$PYTHON_VERSION" =~ Python\ 3\.(9|1[0-9])\. ]]; then
    echo "❌ Python 3.9+ 필요 (현재: $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python: $PYTHON_VERSION"

# AWS CLI 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않음"
    exit 1
fi
echo "✅ AWS CLI: $(aws --version)"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않음"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

# Git 확인
if ! command -v git &> /dev/null; then
    echo "❌ Git이 설치되지 않음"
    exit 1
fi
echo "✅ Git: $(git --version)"

echo "🎉 모든 필수 도구가 설치되어 있습니다!"