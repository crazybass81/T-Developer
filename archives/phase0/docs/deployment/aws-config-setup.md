# AWS 설정 관리 가이드

## 개요
T-Developer는 AWS Systems Manager Parameter Store와 Secrets Manager를 사용하여 환경변수를 안전하게 관리합니다.

## 설정 구조

### Parameter Store (일반 설정)
```
/t-developer/{environment}/
├── node_env
├── port
├── log_level
├── aws_region
└── bedrock_region
```

### Secrets Manager (민감한 정보)
```
t-developer/{environment}/secrets
├── AWS_ACCESS_KEY_ID
├── AWS_SECRET_ACCESS_KEY
├── OPENAI_API_KEY
├── ANTHROPIC_API_KEY
├── GITHUB_TOKEN
├── JWT_SECRET
└── ENCRYPTION_KEY
```

## 설정 방법

### 1. AWS CLI 설정
```bash
aws configure
```

### 2. 설정 스크립트 실행
```bash
chmod +x scripts/setup-aws-config.sh
./scripts/setup-aws-config.sh
```

### 3. IAM 권한 설정
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParametersByPath"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/t-developer/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:t-developer/*"
    }
  ]
}
```

## 사용법

### 설정 값 가져오기
```typescript
import { getConfig, getSecret } from './config';

// 일반 설정
const port = await getConfig('PORT');

// 민감한 정보
const apiKey = await getSecret('OPENAI_API_KEY');
```

## 보안 장점

1. **중앙 집중식 관리**: 모든 설정을 AWS에서 관리
2. **암호화**: 민감한 정보는 자동으로 암호화
3. **접근 제어**: IAM을 통한 세밀한 권한 관리
4. **감사**: 모든 접근이 CloudTrail에 기록
5. **버전 관리**: 설정 변경 이력 추적