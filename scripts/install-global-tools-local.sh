#!/bin/bash
# scripts/install-global-tools-local.sh

echo "🔧 로컬 개발 도구 설치 중..."

# 로컬 node_modules에 설치
npm install --save-dev typescript
npm install --save-dev @aws-cdk/core
npm install --save-dev serverless
npm install --save-dev pm2
npm install --save-dev lerna

echo "✅ 로컬 개발 도구 설치 완료!"

# 설치 확인
echo -e "\n📋 설치된 도구 확인:"
echo "TypeScript: $(npx tsc --version 2>/dev/null || echo 'Not installed')"
echo "AWS CDK: $(cdk --version 2>/dev/null || echo 'Already installed globally')"
echo "Serverless: $(npx serverless --version 2>/dev/null || echo 'Not installed')"
echo "PM2: $(npx pm2 --version 2>/dev/null || echo 'Not installed')"
echo "Lerna: $(npx lerna --version 2>/dev/null || echo 'Not installed')"

echo -e "\n📋 사용법:"
echo "- TypeScript: npx tsc"
echo "- Serverless: npx serverless"
echo "- PM2: npx pm2"
echo "- Lerna: npx lerna"