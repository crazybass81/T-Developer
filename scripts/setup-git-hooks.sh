#!/bin/bash

echo "🔧 Git 훅 설정 시작..."

# Husky 설치 및 초기화
npm install --save-dev husky @commitlint/cli @commitlint/config-conventional
npx husky install

# pre-commit 훅 추가
npx husky add .husky/pre-commit 'npm run lint && npm run format:check'

# pre-push 훅 추가  
npx husky add .husky/pre-push 'npm test'

echo "✅ Git 훅 설정 완료!"