# Phase 0: 프로젝트 초기화 - Q-Developer 작업지시서

## 📋 작업 개요
- **Phase**: 0 - 사전 준비 및 환경 설정
- **목표**: T-Developer MVP 프로젝트 기본 구조 설정 및 개발 환경 구축
- **예상 소요시간**: 8시간

---

## 🎯 Task 0.1: 개발 환경 초기 설정

### 작업 지시사항

#### 1. 프로젝트 디렉토리 구조 생성

```bash
# 다음 디렉토리 구조를 생성하세요
T-DeveloperMVP/
├── backend/
│   ├── src/
│   │   ├── agents/         # AI 에이전트 모듈
│   │   ├── api/           # API 엔드포인트
│   │   ├── config/        # 설정 파일
│   │   ├── database/      # DB 관련
│   │   ├── middlewares/   # Express 미들웨어
│   │   ├── models/        # 데이터 모델
│   │   ├── services/      # 비즈니스 로직
│   │   └── utils/         # 유틸리티
│   ├── tests/             # 테스트 파일
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API 서비스
│   │   ├── store/         # 상태 관리
│   │   └── utils/         # 유틸리티
│   └── package.json
├── infrastructure/
│   ├── terraform/         # IaC 코드
│   ├── docker/           # Docker 설정
│   └── kubernetes/       # K8s 매니페스트
├── scripts/              # 빌드/배포 스크립트
├── docs/                # 문서
└── tests/               # E2E 테스트
```

**구현 명령어**:
```bash
# scripts/init-project-structure.sh 파일을 생성하고 실행하세요
#!/bin/bash

# 기본 디렉토리 생성
mkdir -p backend/src/{agents,api,config,database,middlewares,models,services,utils}
mkdir -p backend/tests
mkdir -p frontend/src/{components,pages,hooks,services,store,utils}
mkdir -p infrastructure/{terraform,docker,kubernetes}
mkdir -p scripts
mkdir -p docs
mkdir -p tests/e2e

echo "✅ 프로젝트 구조 생성 완료"
```

#### 2. 기본 package.json 파일 생성

**backend/package.json**:
```json
{
  "name": "t-developer-backend",
  "version": "0.1.0",
  "description": "T-Developer MVP Backend",
  "main": "dist/index.js",
  "scripts": {
    "dev": "nodemon --exec ts-node src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "winston": "^3.11.0",
    "@aws-sdk/client-bedrock-runtime": "^3.478.0",
    "@aws-sdk/client-dynamodb": "^3.478.0",
    "@aws-sdk/lib-dynamodb": "^3.478.0",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "joi": "^17.11.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/node": "^20.10.5",
    "@types/express": "^4.17.21",
    "@types/cors": "^2.8.17",
    "@types/jest": "^29.5.11",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2",
    "prettier": "^3.1.1",
    "ts-jest": "^29.1.1",
    "ts-node": "^10.9.2",
    "typescript": "^5.3.3"
  }
}
```

**frontend/package.json**:
```json
{
  "name": "t-developer-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.14.2",
    "zustand": "^4.4.7",
    "@mui/material": "^5.15.1",
    "@emotion/react": "^11.11.3",
    "@emotion/styled": "^11.11.0",
    "react-hook-form": "^7.48.2",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "vite": "^5.0.10",
    "vitest": "^1.1.0",
    "typescript": "^5.3.3",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext ts,tsx",
    "format": "prettier --write src/**/*.{ts,tsx}"
  }
}
```

#### 3. TypeScript 설정 파일 생성

**backend/tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"]
    },
    "typeRoots": ["./node_modules/@types", "./src/types"],
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

**frontend/tsconfig.json**:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### 4. 환경 변수 설정

**.env.example** (프로젝트 루트):
```env
# Application
NODE_ENV=development
PORT=3000
FRONTEND_URL=http://localhost:5173

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# AWS Services
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
DYNAMODB_TABLE_PREFIX=t-developer

# Authentication
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRES_IN=7d

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tdeveloper

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=debug
```

#### 5. Docker 설정

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tdeveloper
      POSTGRES_USER: tdeveloper
      POSTGRES_PASSWORD: tdeveloper123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://tdeveloper:tdeveloper123@postgres:5432/tdeveloper
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - /app/node_modules

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:3000
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  redis_data:
```

---

## 🎯 Task 0.2: Git 및 버전 관리 설정

### 작업 지시사항

#### 1. Git 초기화 및 설정

```bash
# Git 초기화 (이미 되어 있다면 스킵)
git init

# .gitignore 파일 생성
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov

# Production
dist/
build/

# Environment
.env
.env.local
.env.*.local
*.env

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# OS
Thumbs.db

# Docker
docker/data/

# Terraform
*.tfstate
*.tfstate.*
.terraform/
EOF
```

#### 2. pre-commit hooks 설정

**package.json** (프로젝트 루트):
```json
{
  "name": "t-developer-mvp",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "prepare": "husky install",
    "backend:dev": "cd backend && npm run dev",
    "frontend:dev": "cd frontend && npm run dev",
    "dev": "concurrently \"npm run backend:dev\" \"npm run frontend:dev\"",
    "test": "npm run test:backend && npm run test:frontend",
    "test:backend": "cd backend && npm test",
    "test:frontend": "cd frontend && npm test",
    "lint": "npm run lint:backend && npm run lint:frontend",
    "lint:backend": "cd backend && npm run lint",
    "lint:frontend": "cd frontend && npm run lint"
  },
  "devDependencies": {
    "husky": "^8.0.3",
    "lint-staged": "^15.2.0",
    "@commitlint/cli": "^18.4.3",
    "@commitlint/config-conventional": "^18.4.3",
    "concurrently": "^8.2.2"
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
}
```

---

## 🎯 Task 0.3: AWS 환경 설정

### 작업 지시사항

#### 1. AWS 프로필 설정 스크립트

**scripts/setup-aws.sh**:
```bash
#!/bin/bash

echo "🔧 AWS 환경 설정 시작..."

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    echo "AWS CLI를 설치해주세요: https://aws.amazon.com/cli/"
    exit 1
fi

# AWS 프로필 설정
aws configure --profile t-developer

# 필요한 AWS 서비스 권한 확인
aws sts get-caller-identity --profile t-developer

echo "✅ AWS 설정 완료"
```

#### 2. IAM 정책 생성

**infrastructure/terraform/iam-policy.json**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "dynamodb:*",
        "s3:*",
        "lambda:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## ✅ 검증 체크리스트

완료 후 다음 사항을 확인하세요:

- [ ] 모든 디렉토리 구조가 생성되었는가?
- [ ] package.json 파일들이 올바르게 설정되었는가?
- [ ] TypeScript 설정이 완료되었는가?
- [ ] Docker 환경이 정상 작동하는가?
- [ ] Git hooks가 정상 작동하는가?
- [ ] AWS 프로필이 설정되었는가?
- [ ] 환경 변수 파일이 생성되었는가?

---

## 🚀 다음 단계

Phase 0 완료 후:
1. `npm install`로 의존성 설치
2. `docker-compose up`으로 로컬 환경 실행
3. Phase 1: 백엔드 기초 구현 시작

---

## 📝 참고사항

- 모든 작업은 feature 브랜치에서 진행
- 커밋 메시지는 conventional commits 규칙 준수
- 코드 리뷰 후 main 브랜치에 merge
- 문제 발생 시 `docs/troubleshooting.md` 참조