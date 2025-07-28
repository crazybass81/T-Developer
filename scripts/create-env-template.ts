#!/usr/bin/env node
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
console.log('3. AWS 자격 증명 설정');
console.log('4. API 키 획득 및 설정');

// .env 파일이 없으면 템플릿을 복사
const envPath = path.join(process.cwd(), '.env');
if (!fs.existsSync(envPath)) {
    fs.copyFileSync(envExamplePath, envPath);
    console.log('✅ .env 파일도 생성했습니다 (실제 값으로 업데이트 필요)');
}