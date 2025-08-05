#!/bin/bash
# T-Developer MVP - Backend Dependencies Installation

set -e

echo "🔧 백엔드 의존성 설치 시작..."

cd backend

# Node.js 의존성 설치
echo "📦 Node.js 의존성 설치 중..."
npm install

# Python 의존성 설치
echo "🐍 Python 의존성 설치 중..."
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

# Agno 프레임워크 확인
if ! npm list agno > /dev/null 2>&1; then
    echo "⚠️ Agno 설치 확인 필요"
    npm install agno@latest
fi

# Agent Squad 확인
if ! npm list agent-squad > /dev/null 2>&1; then
    echo "⚠️ Agent Squad 설치 확인 필요"
    npm install agent-squad@latest
fi

echo "✅ 백엔드 의존성 설치 완료!"