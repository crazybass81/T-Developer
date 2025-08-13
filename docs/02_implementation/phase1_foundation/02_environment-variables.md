# T-Developer 환경변수 가이드

## 🔐 환경변수 관리 체계

T-Developer는 **로컬 .env 파일을 사용하지 않습니다**. 모든 환경변수는 AWS에서 중앙 관리됩니다.

### 저장 위치

#### 1. **AWS Parameter Store** (일반 설정 - 무료)
- Database 연결 정보 (패스워드 제외)
- Redis 연결 정보 (패스워드 제외)
- AWS Bedrock 설정
- 서버 설정 (PORT, NODE_ENV 등)
- Feature flags
- API 설정

#### 2. **AWS Secrets Manager** (민감한 정보 - $0.40/월)
- 패스워드 (DB, Redis)
- JWT 시크릿 키
- 암호화 키
- AWS 자격 증명

## 🚀 서버 실행 방법

### 개발 환경

```bash
# AWS 자격 증명 설정 (최초 1회)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# 백엔드 서버 실행
cd backend
npm run dev

# 또는 main.ts 직접 실행
npx ts-node src/main.ts
```

서버 시작 시 자동으로:
1. Parameter Store에서 일반 설정 로드
2. Secrets Manager에서 민감한 정보 로드
3. 환경변수로 설정

### 프로덕션 환경

EC2 인스턴스나 ECS에서는 IAM Role을 사용하여 자동으로 인증됩니다.

```bash
NODE_ENV=production npm start
```

## 📝 환경변수 목록

### Parameter Store (`/t-developer/development/`)

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| DB_HOST | PostgreSQL 호스트 | localhost |
| DB_PORT | PostgreSQL 포트 | 5432 |
| DB_NAME | 데이터베이스 이름 | t_developer |
| DB_USER | 데이터베이스 사용자 | postgres |
| REDIS_HOST | Redis 호스트 | localhost |
| REDIS_PORT | Redis 포트 | 6379 |
| BEDROCK_AGENT_ID | AWS Bedrock Agent ID | - |
| BEDROCK_AGENT_ALIAS_ID | Bedrock Agent Alias | - |
| PORT | 서버 포트 | 8000 |
| NODE_ENV | 실행 환경 | development |
| LOG_LEVEL | 로그 레벨 | info |
| FRONTEND_URL | 프론트엔드 URL | http://localhost:5173 |
| ... 외 17개 추가 파라미터 |

### Secrets Manager (`t-developer/development/secrets`)

| 변수명 | 설명 |
|--------|------|
| DB_PASSWORD | PostgreSQL 패스워드 |
| REDIS_PASSWORD | Redis 패스워드 |
| JWT_SECRET | JWT 서명 키 |
| JWT_REFRESH_SECRET | JWT 리프레시 키 |
| ENCRYPTION_KEY | 데이터 암호화 키 |
| AWS_ACCESS_KEY_ID | AWS 액세스 키 |
| AWS_SECRET_ACCESS_KEY | AWS 시크릿 키 |

## 🛠️ 환경변수 관리 스크립트

### 1. 초기 설정
```bash
# Parameter Store 설정
./scripts/aws/setup-parameters.sh development

# Secrets Manager 설정
./scripts/aws/setup-secrets.sh development

# 누락된 파라미터 추가
./scripts/aws/add-missing-parameters.sh development
```

### 2. 환경변수 확인
```bash
# Parameter Store 확인
aws ssm get-parameters-by-path \
  --path '/t-developer/development' \
  --recursive \
  --region us-east-1

# Secrets Manager 확인
aws secretsmanager get-secret-value \
  --secret-id 't-developer/development/secrets' \
  --region us-east-1
```

### 3. 환경변수 업데이트
```bash
# 개별 파라미터 업데이트
aws ssm put-parameter \
  --name "/t-developer/development/PORT" \
  --value "8080" \
  --overwrite \
  --region us-east-1

# 시크릿 업데이트
# 1. /tmp/secrets.json 파일 생성
# 2. 업데이트 실행
aws secretsmanager update-secret \
  --secret-id "t-developer/development/secrets" \
  --secret-string file:///tmp/secrets.json \
  --region us-east-1
```

## 💡 주의사항

1. **로컬 .env 파일 사용 금지**
   - 모든 .env 파일은 삭제되었습니다
   - .env.example만 참고용으로 유지

2. **AWS 자격 증명 필요**
   - 개발 시 AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY 필요
   - 프로덕션에서는 IAM Role 사용

3. **비용 최적화**
   - Parameter Store: 무료 (31개 파라미터)
   - Secrets Manager: $0.40/월 (7개 시크릿)
   - 총 비용: $0.40/월

4. **보안**
   - 민감한 정보는 반드시 Secrets Manager에 저장
   - AWS 자격 증명은 절대 코드에 하드코딩 금지

## 🔄 Migration from .env

기존 .env 파일 사용자를 위한 마이그레이션 가이드:

1. AWS 자격 증명 설정
2. 스크립트 실행: `./scripts/aws/setup-parameters.sh`
3. 로컬 .env 파일 삭제
4. 서버 재시작

## 📚 관련 문서

- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [HybridConfigManager 소스 코드](../backend/src/config/config-manager.ts)
