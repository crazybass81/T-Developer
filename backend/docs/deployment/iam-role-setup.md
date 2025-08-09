# IAM Role 기반 보안 설정

## 🔐 올바른 AWS 보안 구조

```
EC2 Instance → IAM Role → Secrets Manager/Parameter Store → API Keys
```

하드코딩 없이 안전하게 관리하는 방법:

## 1. EC2 인스턴스에 IAM Role 연결

### AWS Console에서 설정:

1. **IAM Role 생성**
   ```
   AWS Console → IAM → Roles → Create Role
   - Trusted entity: AWS service → EC2
   - Role name: t-developer-ec2-role
   ```

2. **필요한 정책 연결**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "secretsmanager:GetSecretValue",
           "secretsmanager:DescribeSecret"
         ],
         "Resource": "arn:aws:secretsmanager:*:*:secret:t-developer/*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "ssm:GetParameter",
           "ssm:GetParameters",
           "ssm:GetParametersByPath"
         ],
         "Resource": "arn:aws:ssm:*:*:parameter/t-developer/*"
       }
     ]
   }
   ```

3. **EC2 인스턴스에 Role 연결**
   ```
   EC2 → Instances → 인스턴스 선택
   Actions → Security → Modify IAM Role
   → t-developer-ec2-role 선택
   ```

## 2. Secrets Manager에 시크릿 저장

### AWS CLI 사용 (Role 연결 후):
```bash
# API 키들을 Secrets Manager에 저장
aws secretsmanager create-secret \
  --name t-developer/openai-api-key \
  --secret-string "sk-xxxxx"

aws secretsmanager create-secret \
  --name t-developer/anthropic-api-key \
  --secret-string "sk-ant-xxxxx"

aws secretsmanager create-secret \
  --name t-developer/database-url \
  --secret-string "postgresql://user:pass@host/db"
```

### Parameter Store 사용 (비밀이 아닌 설정):
```bash
# 일반 설정은 Parameter Store 사용
aws ssm put-parameter \
  --name /t-developer/environment \
  --value "production" \
  --type String

aws ssm put-parameter \
  --name /t-developer/region \
  --value "us-east-1" \
  --type String
```

## 3. 애플리케이션에서 시크릿 사용

### Python 코드:
```python
import boto3
import json
import os

class SecureConfig:
    def __init__(self):
        # IAM Role을 통해 자동으로 인증됨
        self.sm_client = boto3.client('secretsmanager')
        self.ssm_client = boto3.client('ssm')
    
    def get_secret(self, secret_name):
        """Secrets Manager에서 시크릿 가져오기"""
        try:
            response = self.sm_client.get_secret_value(
                SecretId=f't-developer/{secret_name}'
            )
            return response['SecretString']
        except Exception as e:
            print(f"Error getting secret: {e}")
            # 로컬 개발용 폴백
            return os.getenv(secret_name.upper().replace('-', '_'))
    
    def get_parameter(self, param_name):
        """Parameter Store에서 파라미터 가져오기"""
        try:
            response = self.ssm_client.get_parameter(
                Name=f'/t-developer/{param_name}'
            )
            return response['Parameter']['Value']
        except Exception as e:
            print(f"Error getting parameter: {e}")
            return os.getenv(param_name.upper().replace('-', '_'))

# 사용 예시
config = SecureConfig()
openai_key = config.get_secret('openai-api-key')
environment = config.get_parameter('environment')
```

## 4. 로컬 개발 환경 설정

### 로컬에서는 환경 변수 사용:
```bash
# .env.local (git에 추가하지 않음)
OPENAI_API_KEY=sk-local-test
ANTHROPIC_API_KEY=sk-ant-local-test
DATABASE_URL=postgresql://localhost/test
```

### Docker Compose 설정:
```yaml
services:
  api:
    environment:
      - USE_AWS_SECRETS=false  # 로컬에서는 비활성화
    env_file:
      - .env.local  # 로컬 시크릿 파일
```

## 5. 계층적 보안 구조

```
Production (EC2/ECS/Lambda):
├── IAM Role (인스턴스/태스크/함수에 연결)
├── Secrets Manager (민감한 정보)
│   ├── API Keys
│   ├── Database Passwords
│   └── OAuth Tokens
└── Parameter Store (일반 설정)
    ├── Environment Variables
    ├── Feature Flags
    └── Configuration

Local Development:
├── .env.local (gitignore)
└── Docker Secrets (개발용)
```

## 6. 자동화 스크립트

### setup-iam-role.sh:
```bash
#!/bin/bash
# IAM Role 설정 확인 스크립트

# EC2 메타데이터 확인
ROLE=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/)

if [ -z "$ROLE" ]; then
    echo "❌ No IAM Role attached"
    echo "Please attach an IAM Role with SecretManager permissions"
else
    echo "✅ IAM Role: $ROLE"
    
    # Role 권한 테스트
    aws secretsmanager list-secrets --query 'SecretList[?starts_with(Name, `t-developer/`)].Name' 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Can access Secrets Manager"
    else
        echo "❌ Cannot access Secrets Manager"
    fi
fi
```

## 7. 장점

1. **No Hardcoding**: 코드에 시크릿 없음
2. **Automatic Rotation**: AWS가 자동으로 키 로테이션
3. **Audit Trail**: 모든 접근이 CloudTrail에 기록
4. **Fine-grained Access**: IAM Policy로 세밀한 권한 제어
5. **Zero-downtime Updates**: 시크릿 변경 시 재배포 불필요

## 8. 비용

- Secrets Manager: $0.40/월/시크릿 + API 호출 비용
- Parameter Store: 
  - Standard: 무료 (4KB, 10,000개까지)
  - Advanced: $0.05/월/파라미터

## 결론

**"닭이 먼저냐 달걀이 먼저냐" 문제의 해결책 = IAM Role**

IAM Role은 AWS가 자동으로 관리하는 임시 자격 증명을 제공하므로, 
어떤 것도 하드코딩할 필요가 없습니다!