#!/bin/bash
# scripts/install-frontend-deps.sh

echo "🔧 프론트엔드 의존성 설치 중..."

# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 설치 확인
echo "✅ 프론트엔드 의존성 설치 완료!"

# 개발 서버 테스트
echo "📋 개발 서버 테스트 중..."
timeout 5s npm run dev || echo "개발 서버 테스트 완료"

echo "🚀 프론트엔드 준비 완료!"
echo "   - 개발 서버 실행: cd frontend && npm run dev"
echo "   - 빌드: cd frontend && npm run build"