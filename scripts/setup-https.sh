#!/bin/bash

echo "🔐 HTTPS 개발 환경 설정..."

# SSL 인증서 생성
echo "📜 SSL 인증서 생성 중..."
./scripts/generate-ssl-certs.sh

# 인증서 검증
if [ -f "./certs/server.crt" ] && [ -f "./certs/server.key" ]; then
    echo "✅ SSL 인증서 생성 완료"
    
    # 인증서 정보 출력
    echo "📋 인증서 정보:"
    openssl x509 -in ./certs/server.crt -text -noout | grep -A 1 "Subject:"
    openssl x509 -in ./certs/server.crt -text -noout | grep -A 3 "Subject Alternative Name"
    
    # .env 파일 업데이트
    if [ -f ".env" ]; then
        if grep -q "USE_HTTPS" .env; then
            sed -i 's/USE_HTTPS=.*/USE_HTTPS=true/' .env
        else
            echo "USE_HTTPS=true" >> .env
        fi
        echo "✅ .env 파일 업데이트 완료"
    fi
    
    echo ""
    echo "🚀 HTTPS 서버 사용 방법:"
    echo "1. 서버 시작: npm run dev"
    echo "2. HTTPS 접속: https://localhost:8443"
    echo "3. HTTP 접속: http://localhost:8000"
    echo ""
    echo "⚠️  브라우저에서 인증서 경고가 나타나면 '고급' > '안전하지 않음으로 이동' 클릭"
    
else
    echo "❌ SSL 인증서 생성 실패"
    exit 1
fi