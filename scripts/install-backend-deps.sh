#!/bin/bash
# scripts/install-backend-deps.sh

cd backend
npm install

# Agno 프레임워크 설치 확인
if ! npm list agno > /dev/null 2>&1; then
    echo "⚠️  Agno 설치 확인 필요"
    npm install agno@latest
fi

# Agent Squad 설치 확인
if ! npm list agent-squad > /dev/null 2>&1; then
    echo "⚠️  Agent Squad 설치 확인 필요"
    npm install agent-squad@latest
fi

echo "✅ 백엔드 의존성 설치 완료!"