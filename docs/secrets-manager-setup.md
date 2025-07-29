# AWS Secrets Manager 설정 가이드

## 📋 개요
T-Developer는 AWS Secrets Manager를 사용하여 민감한 설정 정보를 안전하게 관리합니다.

## 🔧 설정 단계

### 1. IAM 권한 설정
다음 권한이 필요합니다:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:CreateSecret",
        "secretsmanager:UpdateSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:t-developer/*"
    }
  ]
}
```

### 2. 시크릿 생성
```bash
cd backend
npm run setup-secrets
```

### 3. AWS Console에서 값 업데이트
1. AWS Console > Secrets Manager 이동
2. `t-developer/production/config` 시크릿 선택
3. "Retrieve secret value" 클릭
4. "Edit" 버튼으로 실제 값 입력:
   - `JWT_ACCESS_SECRET`: 강력한 랜덤 문자열
   - `JWT_REFRESH_SECRET`: 다른 강력한 랜덤 문자열
   - `OPENAI_API_KEY`: OpenAI API 키
   - `ANTHROPIC_API_KEY`: Anthropic API 키
   - `GITHUB_TOKEN`: GitHub Personal Access Token

## 🌍 환경별 시크릿
- `t-developer/development/config` - 개발 환경
- `t-developer/staging/config` - 스테이징 환경  
- `t-developer/production/config` - 프로덕션 환경

## 🔄 자동 로딩
프로덕션 환경에서는 서버 시작 시 자동으로 시크릿을 로드합니다:
- 5분간 캐시
- 환경 변수가 없는 경우에만 설정
- 실패 시 로컬 .env 파일 사용

## ⚠️ 주의사항
- 개발 환경에서는 로컬 .env 파일 사용
- 시크릿 값 변경 후 애플리케이션 재시작 필요
- 캐시 TTL은 5분 (보안과 성능의 균형)