#!/bin/bash
# scripts/setup-frontend.sh

echo "🚀 프론트엔드 설정 시작..."

cd frontend

# Node.js v18 사용 (React 호환성)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

echo "📦 의존성 설치 중..."
npm install

echo "🔧 타입 체크..."
npm run type-check

echo "✅ 프론트엔드 설정 완료!"
echo "📋 사용 가능한 명령어:"
echo "  - npm run dev     : 개발 서버 시작"
echo "  - npm run build   : 프로덕션 빌드"
echo "  - npm run preview : 빌드 미리보기"
echo "  - npm run lint    : 코드 린팅"