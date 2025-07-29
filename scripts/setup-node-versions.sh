#!/bin/bash
# scripts/setup-node-versions.sh

echo "🔧 Node.js 버전 관리 설정..."

# NVM 로드
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 현재 설치된 Node.js 버전 확인
echo "📋 설치된 Node.js 버전:"
nvm list

# Node.js v18을 기본으로 설정
nvm alias default 18
nvm use 18

echo ""
echo "✅ Node.js 설정 완료!"
echo "현재 버전: $(node -v)"
echo "NPM 버전: $(npm -v)"

echo ""
echo "📋 사용법:"
echo "- Agent Squad 사용 시: nvm use 18"
echo "- 최신 Node.js 사용 시: nvm use 22"
echo "- 기본 버전 확인: nvm current"