#!/bin/bash

echo "🔧 Git 훅 설정 시작..."

# 현재 디렉토리가 Git 저장소인지 확인
if [ ! -d ".git" ]; then
  echo "❌ Git 저장소가 아닙니다. git init을 먼저 실행하세요."
  exit 1
fi

# Husky 및 commitlint 설치
echo "📦 Husky 및 commitlint 설치 중..."
npm install --save-dev husky @commitlint/cli @commitlint/config-conventional

# Husky 초기화
echo "🔧 Husky 초기화 중..."
npx husky install

# Git 훅 디렉토리 생성
mkdir -p .husky

# commit-msg 훅 추가
echo "📝 commit-msg 훅 추가 중..."
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit $1'

# pre-commit 훅 추가
echo "🔍 pre-commit 훅 추가 중..."
npx husky add .husky/pre-commit 'npm run pre-commit'

# pre-push 훅 추가
echo "🚀 pre-push 훅 추가 중..."
npx husky add .husky/pre-push 'npm run pre-push'

# package.json에 스크립트 추가
echo "📋 package.json 스크립트 업데이트 중..."
npm pkg set scripts.prepare="husky install"
npm pkg set scripts.pre-commit="npm run lint && npm run test:unit"
npm pkg set scripts.pre-push="npm run test:integration"

echo "✅ Git 훅 설정 완료!"
echo ""
echo "📋 설정된 훅:"
echo "  • commit-msg: 커밋 메시지 규칙 검증"
echo "  • pre-commit: 린트 및 단위 테스트"
echo "  • pre-push: 통합 테스트"
