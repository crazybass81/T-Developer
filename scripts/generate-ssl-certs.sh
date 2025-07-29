#!/bin/bash
# scripts/generate-ssl-certs.sh

CERT_DIR="./certs"
DOMAIN="localhost"

# 인증서 디렉토리 생성
mkdir -p $CERT_DIR

# Root CA 생성
openssl genrsa -out $CERT_DIR/rootCA.key 2048
openssl req -x509 -new -nodes -key $CERT_DIR/rootCA.key -sha256 -days 365 \
    -out $CERT_DIR/rootCA.crt \
    -subj "/C=US/ST=State/L=City/O=T-Developer/CN=T-Developer Root CA"

# 서버 키 생성
openssl genrsa -out $CERT_DIR/server.key 2048

# 인증서 요청 생성
openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr \
    -subj "/C=US/ST=State/L=City/O=T-Developer/CN=$DOMAIN"

# SAN 설정 파일 생성
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
openssl x509 -req -in $CERT_DIR/server.csr -CA $CERT_DIR/rootCA.crt \
    -CAkey $CERT_DIR/rootCA.key -CAcreateserial \
    -out $CERT_DIR/server.crt -days 365 -sha256 \
    -extfile $CERT_DIR/server.conf -extensions v3_req

# PEM 형식으로 변환
cat $CERT_DIR/server.crt $CERT_DIR/server.key > $CERT_DIR/server.pem

echo "✅ SSL 인증서 생성 완료!"
echo "📁 인증서 위치: $CERT_DIR/"
echo "🔐 Root CA를 시스템에 신뢰할 인증서로 추가하세요:"
echo "   - macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $CERT_DIR/rootCA.crt"
echo "   - Ubuntu: sudo cp $CERT_DIR/rootCA.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates"