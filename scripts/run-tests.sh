#!/bin/bash
set -e

echo "🧪 T-Developer 테스트 실행"
echo "=========================="

# 환경 변수 설정
export NODE_ENV=test
export AWS_REGION=us-east-1
export DYNAMODB_ENDPOINT=http://localhost:8000

# 테스트 타입 선택
if [ "$1" == "unit" ]; then
    echo "🔬 단위 테스트 실행..."
    cd backend
    npm run test:unit
elif [ "$1" == "integration" ]; then
    echo "🔗 통합 테스트 실행..."
    cd backend
    npm run test:integration
elif [ "$1" == "e2e" ]; then
    echo "🌐 E2E 테스트 실행..."
    cd backend
    npm run test:e2e
elif [ "$1" == "seed" ]; then
    echo "🌱 테스트 데이터 시딩..."
    cd backend
    npm run test:seed
elif [ "$1" == "all" ]; then
    echo "📊 전체 테스트 실행..."
    cd backend
    npm run test:unit && npm run test:integration && npm run test:e2e
else
    echo "사용법: ./run-tests.sh [unit|integration|e2e|seed|all]"
    echo ""
    echo "옵션:"
    echo "  unit        - 단위 테스트만 실행"
    echo "  integration - 통합 테스트만 실행"
    echo "  e2e         - E2E 테스트만 실행"
    echo "  seed        - 테스트 데이터 시딩"
    echo "  all         - 모든 테스트 실행"
    exit 1
fi

echo "✅ 테스트 완료!"