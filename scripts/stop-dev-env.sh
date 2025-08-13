#!/bin/bash

echo "🛑 T-Developer 개발 환경 중지..."

# Docker Compose 중지
docker-compose down

# 볼륨 정리 (선택사항)
if [ "$1" == "--clean" ]; then
    echo "🧹 데이터 볼륨 정리 중..."
    docker-compose down -v
    docker system prune -f
    echo "✅ 모든 데이터가 정리되었습니다."
else
    echo "💾 데이터 볼륨이 보존되었습니다."
    echo "   완전 정리: ./scripts/stop-dev-env.sh --clean"
fi

echo "✅ 개발 환경 중지 완료!"
