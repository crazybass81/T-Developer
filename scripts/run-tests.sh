#!/bin/bash
set -e

echo "🧪 T-Developer 테스트 실행"
echo "=========================="

# 환경 변수 설정
export NODE_ENV=test
export AWS_REGION=us-east-1
export DYNAMODB_ENDPOINT=http://localhost:8000

cd backend

# 테스트 타입 선택
if [ "$1" == "unit" ]; then
    echo "🔬 단위 테스트 실행..."
    npm run test:unit
elif [ "$1" == "integration" ]; then
    echo "🔗 통합 테스트 실행..."
    npm run test:integration
elif [ "$1" == "e2e" ]; then
    echo "🌐 E2E 테스트 실행..."
    npm run test:e2e
elif [ "$1" == "seed" ]; then
    echo "🌱 테스트 데이터 시딩..."
    npm run test:seed
elif [ "$1" == "all" ]; then
    echo "📊 전체 테스트 실행..."
    npm run test:all
else
    echo "사용법: ./run-tests.sh [unit|integration|e2e|seed|all]"
    exit 1
fi

echo "✅ 테스트 완료!"
