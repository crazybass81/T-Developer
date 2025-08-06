#!/bin/bash

echo "🐳 Docker 서비스 헬스 체크 시작..."

# 서비스 상태 확인
services=("t-developer-dynamodb" "t-developer-redis" "t-developer-localstack" "t-developer-elasticsearch")

for service in "${services[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "$service"; then
        echo "✅ $service 실행 중"
    else
        echo "❌ $service 중지됨"
    fi
done

# 포트 연결 확인
echo -e "\n🔌 포트 연결 확인:"

ports=("8000:DynamoDB" "6379:Redis" "4566:LocalStack" "9200:Elasticsearch")

for port_service in "${ports[@]}"; do
    port=$(echo $port_service | cut -d: -f1)
    service=$(echo $port_service | cut -d: -f2)
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $service (포트 $port) 연결 가능"
    else
        echo "❌ $service (포트 $port) 연결 불가"
    fi
done

echo -e "\n📊 Docker 리소스 사용량:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"