#!/bin/bash
# scripts/install-global-tools.sh

echo "🔧 전역 개발 도구 설치 중..."

# TypeScript
npm install -g typescript

# AWS CDK
npm install -g aws-cdk

# Serverless Framework
npm install -g serverless

# PM2 (프로세스 관리)
npm install -g pm2

# Lerna (모노레포 관리)
npm install -g lerna

echo "✅ 전역 도구 설치 완료!"

# 설치 확인
echo -e "\n📋 설치된 도구 버전:"
echo "TypeScript: $(tsc --version)"
echo "AWS CDK: $(cdk --version)"
echo "Serverless: $(serverless --version)"
echo "PM2: $(pm2 --version)"
echo "Lerna: $(lerna --version)"