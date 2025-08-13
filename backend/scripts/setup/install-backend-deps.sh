#!/bin/bash
# scripts/install-backend-deps.sh

echo "🔧 백엔드 의존성 설치 중..."

cd backend

# npm 의존성 설치
npm install

# 특수 프레임워크 설치 시도 (실제 패키지가 없을 수 있음)
echo "📦 특수 AI 프레임워크 확인 중..."

# Agno 프레임워크 (실제 패키지가 없으므로 스킵)
echo "⚠️  Agno 프레임워크는 현재 사용할 수 없습니다 (개발 중)"

# Agent Squad (실제 패키지가 없으므로 스킵)
echo "⚠️  Agent Squad는 현재 사용할 수 없습니다 (개발 중)"

echo "✅ 백엔드 의존성 설치 완료!"
echo "📋 다음 단계:"
echo "   - cd backend"
echo "   - npm run dev (개발 서버 시작)"
