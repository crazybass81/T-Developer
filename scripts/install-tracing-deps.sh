#!/bin/bash

echo "📦 OpenTelemetry 의존성 설치 중..."

cd backend

# OpenTelemetry 핵심 패키지
npm install --save \
  @opentelemetry/api \
  @opentelemetry/sdk-trace-node \
  @opentelemetry/resources \
  @opentelemetry/semantic-conventions \
  @opentelemetry/exporter-jaeger \
  @opentelemetry/sdk-trace-base \
  @opentelemetry/instrumentation \
  @opentelemetry/instrumentation-http \
  @opentelemetry/instrumentation-express

echo "✅ OpenTelemetry 패키지 설치 완료!"

# 설치된 패키지 확인
echo ""
echo "📋 설치된 패키지 목록:"
npm list | grep opentelemetry

echo ""
echo "🔍 다음 단계:"
echo "   1. docker-compose -f docker-compose.tracing.yml up -d"
echo "   2. Jaeger UI 접속: http://localhost:16686"
echo "   3. Express 앱에 추적 미들웨어 추가"