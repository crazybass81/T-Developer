#!/bin/bash

echo "🚀 T-Developer 개발 환경 시작..."

# Docker 실행 확인
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker가 실행되지 않았습니다. Docker Desktop을 시작하세요."
    exit 1
fi

# 환경 변수 설정
export REDIS_PASSWORD=devpassword
export DB_USER=developer
export DB_PASSWORD=devpassword

# Docker Compose 실행
echo "🐳 Docker 서비스 시작 중..."
docker-compose up -d

# 서비스 준비 대기
echo "⏳ 서비스 준비 대기 중..."
sleep 30

# LocalStack 초기화
echo "🔧 LocalStack 초기화 중..."
python3 scripts/setup-localstack.py

# LocalStack 테스트
echo "🧪 LocalStack 서비스 테스트..."
python3 scripts/test-localstack.py

# 서비스 상태 확인
echo "📊 서비스 상태 확인:"
echo "- DynamoDB: http://localhost:8000"
echo "- Redis: localhost:6379"
echo "- LocalStack: http://localhost:4566"
echo "- PostgreSQL: localhost:5432"
echo "- Elasticsearch: http://localhost:9200"
echo "- Kibana: http://localhost:5601"
echo "- Jaeger: http://localhost:16686"

echo "✅ 개발 환경 준비 완료!"