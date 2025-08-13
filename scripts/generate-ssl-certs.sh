#!/bin/bash

# 개발용 SSL 인증서 생성 스크립트

CERT_DIR="./certs"
DOMAIN="localhost"

echo "🔐 SSL 인증서 생성 시작..."

# 인증서 디렉토리 생성
mkdir -p $CERT_DIR

# Root CA 생성
echo "📋 Root CA 생성 중..."
openssl genrsa -out $CERT_DIR/rootCA.key 2048
openssl req -x509 -new -nodes -key $CERT_DIR/rootCA.key -sha256 -days 365 \
    -out $CERT_DIR/rootCA.crt \
    -subj "/C=US/ST=State/L=City/O=T-Developer/CN=T-Developer Root CA"

# 서버 키 생성
echo "🔑 서버 키 생성 중..."
openssl genrsa -out $CERT_DIR/server.key 2048

# 인증서 요청 생성
echo "📝 인증서 요청 생성 중..."
openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr \
    -subj "/C=US/ST=State/L=City/O=T-Developer/CN=$DOMAIN"

# SAN 설정 파일 생성
echo "⚙️  SAN 설정 파일 생성 중..."
cat > $CERT_DIR/server.conf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# 서버 인증서 생성
echo "🏆 서버 인증서 생성 중..."
openssl x509 -req -in $CERT_DIR/server.csr -CA $CERT_DIR/rootCA.crt \
    -CAkey $CERT_DIR/rootCA.key -CAcreateserial \
    -out $CERT_DIR/server.crt -days 365 -sha256 \
    -extfile $CERT_DIR/server.conf -extensions v3_req

# PEM 형식으로 변환
echo "🔄 PEM 형식 변환 중..."
cat $CERT_DIR/server.crt $CERT_DIR/server.key > $CERT_DIR/server.pem

# 임시 파일 정리
rm $CERT_DIR/server.csr $CERT_DIR/server.conf $CERT_DIR/rootCA.srl

echo ""
echo "✅ SSL 인증서 생성 완료!"
echo "📁 인증서 위치: $CERT_DIR/"
echo ""
echo "📋 생성된 파일:"
echo "  - rootCA.crt (Root CA 인증서)"
echo "  - rootCA.key (Root CA 개인키)"
echo "  - server.crt (서버 인증서)"
echo "  - server.key (서버 개인키)"
echo "  - server.pem (서버 인증서 + 키 통합)"
echo ""
echo "🔐 Root CA를 시스템에 신뢰할 인증서로 추가하세요:"
echo "   - macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $CERT_DIR/rootCA.crt"
echo "   - Ubuntu: sudo cp $CERT_DIR/rootCA.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates"
echo "   - Windows: certlm.msc에서 신뢰할 수 있는 루트 인증 기관에 rootCA.crt 추가"
echo ""
echo "🚀 HTTPS 서버 사용법:"
echo "   NODE_ENV=development USE_HTTPS=true npm run dev"
