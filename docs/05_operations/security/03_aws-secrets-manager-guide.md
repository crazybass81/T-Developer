# AWS Secrets Manager Integration Guide

## 개요

T-Developer MVP는 AWS Secrets Manager를 사용하여 민감한 정보를 안전하게 관리합니다. 이 가이드는 AWS Secrets Manager를 설정하고 사용하는 방법을 설명합니다.

## 📋 목차

1. [초기 설정](#초기-설정)
2. [시크릿 관리](#시크릿-관리)
3. [애플리케이션 통합](#애플리케이션-통합)
4. [테스트 및 배포](#테스트-및-배포)
5. [보안 모범 사례](#보안-모범-사례)

## 초기 설정

### 1. AWS CLI 설정

```bash
# AWS CLI 설치 (이미 설치되어 있다면 건너뛰기)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# AWS 자격 증명 구성
aws configure
```

### 2. 필요한 패키지 설치

```bash
# Backend 디렉토리에서
cd backend
npm install @aws-sdk/client-secrets-manager

# Root 디렉토리에서
cd ..
npm install @aws-sdk/client-secrets-manager
```

### 3. IAM 권한 설정

AWS IAM에서 다음 권한이 있는 정책을 생성하고 사용자/역할에 연결:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:ListSecrets"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:t-developer/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:UpdateSecret",
        "secretsmanager:TagResource"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:t-developer/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

## 시크릿 관리

### 1. 시크릿 생성

```bash
# 개발 환경 시크릿 생성
node scripts/setup-aws-secrets.js create development

# 스테이징 환경 시크릿 생성
node scripts/setup-aws-secrets.js create staging

# 프로덕션 환경 시크릿 생성
node scripts/setup-aws-secrets.js create production

# 모든 환경 한번에 설정
node scripts/setup-aws-secrets.js setup-all
```

### 2. 시크릿 조회

```bash
# 특정 환경의 시크릿 조회
node scripts/setup-aws-secrets.js get development

# 모든 시크릿 목록 조회
node scripts/setup-aws-secrets.js list
```

### 3. 시크릿 업데이트

```bash
# 기존 시크릿 업데이트
node scripts/setup-aws-secrets.js update development
```

## 애플리케이션 통합

### 1. Backend 통합

Backend 애플리케이션은 시작 시 자동으로 AWS Secrets Manager에서 설정을 로드합니다:

```typescript
// backend/src/main.ts
import { configManager } from './config/aws-secrets';

async function startServer() {
  // AWS Secrets Manager에서 설정 초기화
  await configManager.initialize();
  
  // 설정 값 사용
  const port = configManager.get<number>('app.port');
  const dbConfig = configManager.get('database');
  
  // 서버 시작...
}
```

### 2. 설정 값 접근

```typescript
// 특정 설정 값 가져오기
const jwtSecret = configManager.get<string>('auth.jwtSecret');
const dbHost = configManager.get<string>('database.host');

// 전체 설정 가져오기
const allConfig = configManager.getAll();

// 설정 새로고침 (캐시 클리어)
await configManager.refresh();
```

### 3. 환경 변수 폴백

AWS Secrets Manager를 사용할 수 없는 경우, 시스템은 자동으로 환경 변수로 폴백합니다:

```bash
# .env 파일 또는 환경 변수 설정
export DB_HOST=localhost
export DB_PORT=5432
export JWT_SECRET=your-secret-key
```

## 테스트 및 배포

### 1. 로컬 개발

```bash
# 개발 환경 시크릿을 .env 파일로 다운로드
node scripts/setup-aws-secrets.js get development > .env

# 또는 AWS Secrets Manager 직접 사용
NODE_ENV=development npm run dev
```

### 2. 테스트 스크립트

```bash
# 테스트 실행 (자동으로 시크릿 로드)
./test-complete-squad.sh development

# 특정 환경으로 테스트
./test-complete-squad.sh staging
./test-complete-squad.sh production
```

### 3. Docker 배포

```dockerfile
# Dockerfile
FROM node:18-alpine

# AWS SDK 자격 증명 설정
ENV AWS_REGION=us-east-1

# 빌드 시 시크릿은 포함하지 않음
COPY . .
RUN npm install

# 런타임에 Secrets Manager에서 로드
CMD ["node", "src/main.js"]
```

### 4. CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
env:
  AWS_REGION: us-east-1
  NODE_ENV: production

steps:
  - name: Configure AWS credentials
    uses: aws-actions/configure-aws-credentials@v1
    with:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-region: us-east-1
  
  - name: Deploy application
    run: |
      # 애플리케이션이 시작될 때 자동으로 시크릿 로드
      npm run deploy
```

## 보안 모범 사례

### 1. 접근 제어

- **최소 권한 원칙**: 각 환경별로 필요한 최소한의 권한만 부여
- **IAM 역할 사용**: EC2, Lambda 등에서는 IAM 역할 사용
- **MFA 활성화**: 프로덕션 시크릿 접근 시 MFA 필수

### 2. 시크릿 로테이션

```bash
# 정기적인 시크릿 로테이션 스케줄 설정
aws secretsmanager rotate-secret \
  --secret-id t-developer/prod \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation
```

### 3. 감사 및 모니터링

- **CloudTrail 활성화**: 모든 시크릿 접근 로그 기록
- **CloudWatch 알람**: 비정상적인 시크릿 접근 감지
- **정기 감사**: 사용하지 않는 시크릿 정리

### 4. 암호화

- **전송 중 암호화**: HTTPS/TLS 사용
- **저장 시 암호화**: AWS KMS 키로 자동 암호화
- **애플리케이션 레벨 암호화**: 추가 민감 데이터는 별도 암호화

## 문제 해결

### 1. 권한 오류

```bash
# IAM 권한 확인
aws secretsmanager describe-secret --secret-id t-developer/dev

# 권한이 없다면 IAM 정책 확인 및 수정
```

### 2. 리전 문제

```bash
# 올바른 리전 설정 확인
export AWS_REGION=us-east-1

# 또는 스크립트에서 직접 지정
AWS_REGION=us-east-1 node scripts/setup-aws-secrets.js list
```

### 3. 네트워크 문제

```bash
# VPC 엔드포인트 생성 (프라이빗 서브넷인 경우)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxx \
  --service-name com.amazonaws.us-east-1.secretsmanager
```

## 비용 최적화

1. **캐싱 활용**: 5분 캐시로 API 호출 최소화
2. **배치 조회**: 여러 시크릿을 한 번에 조회
3. **환경별 분리**: 개발/스테이징은 더 저렴한 리전 사용 고려

## 마이그레이션 가이드

### 기존 .env 파일에서 마이그레이션

```bash
# 1. 기존 .env 파일 백업
cp .env .env.backup

# 2. Secrets Manager에 업로드
node scripts/setup-aws-secrets.js create development
# 프롬프트에서 .env 파일의 값 입력

# 3. 애플리케이션 코드 업데이트
# config.ts를 aws-secrets.ts로 교체

# 4. 테스트
npm run test

# 5. .env 파일 제거 (선택사항)
rm .env
```

## 추가 리소스

- [AWS Secrets Manager 공식 문서](https://docs.aws.amazon.com/secretsmanager/)
- [AWS SDK for JavaScript v3](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/)
- [보안 모범 사례](https://aws.amazon.com/secrets-manager/best-practices/)

## 지원

문제가 있거나 도움이 필요한 경우:
1. 이 문서의 문제 해결 섹션 확인
2. AWS CloudWatch 로그 확인
3. 팀 Slack 채널에 문의

---

*최종 업데이트: 2024년 1월*
