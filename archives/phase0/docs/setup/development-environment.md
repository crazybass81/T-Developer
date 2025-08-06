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
```

### 2. Python (v3.9+)
```bash
# macOS
brew install python@3.9

# Ubuntu
sudo apt update
sudo apt install python3.9 python3.9-venv
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
```

## 프로젝트 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-org/t-developer.git
cd t-developer
```

### 2. 의존성 설치
```bash
# Backend 의존성
cd backend
npm install

# Frontend 의존성
cd ../frontend
npm install
```

## 환경 변수 구성

### 1. 환경 변수 파일 생성
```bash
cp .env.example .env
chmod 600 .env
```

### 2. 필수 환경 변수 설정
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
ANTHROPIC_API_KEY=sk-ant-...

# 보안
JWT_SECRET=your-super-secure-jwt-secret-min-32-chars
ENCRYPTION_KEY=your-32-character-encryption-key!!
```

## AWS 서비스 설정

### 1. DynamoDB 테이블 생성
```bash
npm run setup:aws:dynamodb
```

### 2. S3 버킷 생성
```bash
npm run setup:aws:s3
```

## 로컬 개발 환경

### 1. 로컬 서비스 시작
```bash
# Docker Compose로 모든 서비스 시작
docker-compose up -d
```

### 2. 개발 서버 시작
```bash
# Backend
cd backend
npm run dev

# Frontend
cd frontend
npm run dev
```

### 3. 서비스 접속
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000
- **API 문서**: http://localhost:3000/api-docs

## 검증 및 테스트

### 1. 환경 검증
```bash
npm run verify:env
```

### 2. 테스트 실행
```bash
npm test
npm run test:integration
npm run test:e2e
```

## 문제 해결

### 포트 충돌
```bash
lsof -i :3000
kill -9 <PID>
```

### Docker 문제
```bash
docker-compose down
docker-compose up -d
```

### AWS 연결 문제
```bash
aws sts get-caller-identity
```

## 다음 단계

1. [아키텍처 문서](../architecture/overview.md) 읽기
2. [개발 가이드](../development/getting-started.md) 확인
3. [첫 번째 에이전트 만들기](../tutorials/first-agent.md)