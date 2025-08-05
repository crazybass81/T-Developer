# T-Developer MVP

AI-powered multi-agent development platform.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- AWS Account
- Docker

### Installation
```bash
# Check requirements
bash scripts/check-requirements.sh

# Install dependencies (coming next)
npm install
```

## 📚 Documentation
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api.md)
- [Agent Guide](./docs/agents.md)

## ✅ 완료된 SubTasks

### SubTask 0.1.1: 필수 도구 설치 확인
- `scripts/check-requirements.sh` - 개발 환경 체크 스크립트
- Node.js 18+, Python 3.9+, AWS CLI, Docker, Git 확인
- 현재 환경에서 모든 도구가 정상 설치됨을 확인

### SubTask 0.1.2: AWS 계정 및 권한 설정
- `scripts/setup-aws-profile.py` - AWS 계정 설정 확인 스크립트
- `scripts/aws-policy.json` - T-Developer 필요 IAM 정책
- AWS 계정 (036284794745) 연결 확인 완료

### SubTask 0.1.3: 프로젝트 저장소 초기화
- `scripts/init-repository.sh` - Git 저장소 초기화 스크립트
- `.gitignore` - Git 무시 파일 설정
- Git 저장소 초기화 및 기본 커밋 완료

### SubTask 0.1.5: 개발 도구 설정 파일 생성
- `.vscode/settings.json` - VS Code 에디터 설정
- `.eslintrc.js` - ESLint 코드 품질 검사 설정
- `.prettierrc` - Prettier 코드 포맷팅 설정
- `.editorconfig` - 에디터 공통 설정

### SubTask 0.2.1: DynamoDB 로컬 설정
- `docker-compose.dev.yml` - DynamoDB Local 및 Redis 설정
- `scripts/setup-local-db.ts` - 로컬 DB 테이블 생성 스크립트
- DynamoDB Local: http://localhost:8000
- DynamoDB Admin: http://localhost:8001
- Redis: localhost:6380

### SubTask 0.2.2: S3 버킷 생성 스크립트
- `scripts/create-s3-buckets.py` - S3 버킷 생성 자동화 스크립트
- t-developer-artifacts, components, templates, backups 버킷 확인
- CloudFront 연동을 위한 버킷 정책 설정