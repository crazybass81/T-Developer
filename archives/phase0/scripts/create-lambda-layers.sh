#!/bin/bash
# scripts/create-lambda-layers.sh

echo "🔧 Lambda 레이어 생성 중..."

# Node.js 레이어 생성
mkdir -p layers/nodejs-common/nodejs
cd layers/nodejs-common/nodejs

# package.json 생성
cat > package.json << EOF
{
  "name": "t-developer-common-layer",
  "version": "1.0.0",
  "dependencies": {
    "@aws-sdk/client-bedrock": "^3.0.0",
    "@aws-sdk/client-dynamodb": "^3.0.0",
    "@aws-sdk/client-s3": "^3.0.0",
    "axios": "^1.6.0",
    "lodash": "^4.17.21",
    "uuid": "^9.0.0",
    "joi": "^17.11.0"
  }
}
EOF

npm install --production

cd ..
zip -r nodejs-common-layer.zip nodejs/
echo "✅ Node.js 레이어 생성 완료: nodejs-common-layer.zip"

# Python 레이어 생성
mkdir -p ../python-common/python
cd ../python-common

cat > requirements.txt << EOF
boto3>=1.26.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
pydantic>=2.0.0
EOF

pip install -r requirements.txt -t python/
zip -r python-common-layer.zip python/
echo "✅ Python 레이어 생성 완료: python-common-layer.zip"

cd ../../..
echo "✅ Lambda 레이어 생성 완료!"
echo "📋 생성된 파일:"
echo "  - layers/nodejs-common/nodejs-common-layer.zip"
echo "  - layers/python-common/python-common-layer.zip"