#!/bin/bash

echo "🏥 T-Developer 서비스 상태 확인..."

# 서비스 상태 확인 함수
check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo "✅ $name: 정상"
    else
        echo "❌ $name: 비정상"
    fi
}

# 각 서비스 확인
check_service "DynamoDB" "http://localhost:8000"
check_service "LocalStack" "http://localhost:4566/_localstack/health"
check_service "Elasticsearch" "http://localhost:9200"
check_service "Kibana" "http://localhost:5601" 302
check_service "Jaeger" "http://localhost:16686"

# Redis 확인 (별도 처리)
if redis-cli -h localhost -p 6379 -a devpassword ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis: 정상"
else
    echo "❌ Redis: 비정상"
fi

# PostgreSQL 확인
if pg_isready -h localhost -p 5432 -U developer 2>/dev/null; then
    echo "✅ PostgreSQL: 정상"
else
    echo "❌ PostgreSQL: 비정상"
fi

echo "📊 상태 확인 완료!"