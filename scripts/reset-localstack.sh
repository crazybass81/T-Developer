#!/bin/bash

echo "🔄 LocalStack 리셋 중..."

# LocalStack 컨테이너 재시작
docker-compose restart localstack

# 초기화 대기
echo "⏳ LocalStack 재시작 대기 중..."
sleep 15

# 다시 초기화
echo "🔧 LocalStack 재초기화..."
python3 scripts/setup-localstack.py

# 테스트
echo "🧪 서비스 테스트..."
python3 scripts/test-localstack.py

echo "✅ LocalStack 리셋 완료!"