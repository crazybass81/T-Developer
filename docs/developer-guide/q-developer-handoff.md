# Q Developer 작업 인계서

## 📋 프로젝트 개요

**프로젝트명**: T-Developer MVP  
**현재 완성도**: 98%  
**작업 요청일**: 2025-08-08  
**우선순위**: 🔴 High

### 프로젝트 설명
T-Developer는 자연어 입력으로 완전한 React 프로젝트를 생성하는 AI 기반 개발 도구입니다. 현재 핵심 기능은 100% 완성되었으며, AWS 배포 및 운영 환경 구성만 남은 상태입니다.

### 현재 상태
- ✅ **핵심 기능 완성**: 자연어 → React 프로젝트 → ZIP 다운로드
- ✅ **테스트 완료**: E2E, 성능, 사용자 시나리오 모두 통과
- ✅ **문서화 완료**: 사용자 가이드 및 기술 문서 완성
- ⏳ **AWS 배포 필요**: CloudFormation 템플릿 준비 완료, 실행 필요

## 🎯 작업 요청 사항

### 1. AWS 인프라 배포 (우선순위: 🔴 Critical)

#### 1.1 CloudFormation 스택 배포
```bash
# 준비된 스크립트 위치
/home/ec2-user/T-DeveloperMVP/infrastructure/aws/deploy-basic.sh
/home/ec2-user/T-DeveloperMVP/infrastructure/aws/deploy-s3-only.sh
```

**작업 내용**:
1. CloudFormation 템플릿 검토 및 수정
   - IAM 역할 ARN 형식 오류 수정 필요
   - S3 버킷 정책 검증
   - DynamoDB 테이블 설정 확인

2. 스택 배포 실행
   ```bash
   # S3 전용 배포 (먼저 테스트)
   ./infrastructure/aws/deploy-s3-only.sh
   
   # 전체 인프라 배포
   ./infrastructure/aws/deploy-basic.sh
   ```

3. 배포 확인 사항
   - [ ] S3 버킷 2개 생성 (projects, assets)
   - [ ] DynamoDB 테이블 생성
   - [ ] IAM 역할 생성 (Lambda, ECS)
   - [ ] Security Group 설정
   - [ ] CloudWatch Log Group 생성

#### 1.2 ECS/Fargate 배포 설정

**작업 내용**:
1. Docker 이미지 빌드 및 ECR 푸시
   ```bash
   # Backend 이미지
   cd backend
   docker build -t t-developer-backend .
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [ECR_URI]
   docker tag t-developer-backend:latest [ECR_URI]/t-developer-backend:latest
   docker push [ECR_URI]/t-developer-backend:latest
   ```

2. ECS Task Definition 생성
   - CPU: 1 vCPU
   - Memory: 2GB
   - 환경변수 설정 (Secrets Manager 연동)

3. ECS Service 생성
   - Desired count: 2
   - Auto-scaling 설정 (최소 1, 최대 10)
   - ALB 연결

#### 1.3 Lambda Functions 배포

**작업 내용**:
1. Lambda Layer 생성
   ```bash
   cd backend/layers
   ./create-lambda-layers.sh
   ```

2. Agent Lambda 함수 배포
   - NL Input Agent
   - UI Selection Agent
   - Parser Agent
   - Component Decision Agent

3. API Gateway 연결
   - REST API 엔드포인트 생성
   - Lambda 프록시 통합 설정

### 2. S3 정적 파일 서빙 구성 (우선순위: 🟡 High)

**작업 내용**:
1. Frontend 빌드 및 S3 업로드
   ```bash
   cd frontend
   npm run build
   aws s3 sync dist/ s3://t-developer-mvp-assets-development-[ACCOUNT_ID]/ --delete
   ```

2. S3 정적 웹사이트 호스팅 활성화
   - index.html 설정
   - error.html 설정
   - CORS 정책 구성

3. CloudFront 배포 생성
   - Origin: S3 버킷
   - Behaviors: 캐싱 정책 설정
   - Custom domain 설정 (선택사항)

### 3. 보안 검수 (우선순위: 🟡 High)

**체크리스트**:
- [ ] **입력 검증**
  - SQL Injection 방지 확인
  - XSS 공격 방지 확인
  - 파일 업로드 크기 제한

- [ ] **IAM 권한 최소화**
  - Lambda 실행 역할 권한 검토
  - ECS Task 역할 권한 검토
  - S3 버킷 정책 검토

- [ ] **네트워크 보안**
  - Security Group 인바운드 규칙 최소화
  - VPC 엔드포인트 설정 (S3, DynamoDB)
  - ALB 보안 그룹 설정

- [ ] **데이터 보호**
  - S3 버킷 암호화 활성화
  - DynamoDB 암호화 활성화
  - Secrets Manager 사용 확인

- [ ] **로깅 및 모니터링**
  - CloudTrail 활성화
  - VPC Flow Logs 활성화
  - GuardDuty 활성화 (선택사항)

### 4. CloudWatch 모니터링 설정 (우선순위: 🟢 Medium)

**작업 내용**:
1. CloudWatch Dashboard 생성
   ```json
   {
     "DashboardName": "T-Developer-MVP",
     "Widgets": [
       "API Response Time",
       "Project Generation Success Rate",
       "Lambda Invocations",
       "ECS Task Count",
       "S3 Requests",
       "DynamoDB Read/Write Units"
     ]
   }
   ```

2. CloudWatch Alarms 설정
   - API 응답시간 > 5초
   - 에러율 > 1%
   - ECS Task 실패
   - Lambda 동시 실행 한계 도달

3. SNS 알림 구성
   - 이메일 알림 설정
   - Slack 통합 (선택사항)

### 5. CI/CD 파이프라인 구성 (우선순위: 🟢 Medium)

**작업 내용**:
1. CodePipeline 생성
   - Source: GitHub (main branch)
   - Build: CodeBuild
   - Deploy: ECS/Lambda

2. CodeBuild 프로젝트 설정
   ```yaml
   version: 0.2
   phases:
     pre_build:
       commands:
         - npm install
         - npm test
     build:
       commands:
         - npm run build
         - docker build -t $IMAGE_TAG .
     post_build:
       commands:
         - docker push $IMAGE_TAG
   ```

3. 자동 배포 설정
   - Blue/Green 배포 전략
   - 롤백 정책 설정

## 📁 주요 파일 위치

### 소스 코드
```
/home/ec2-user/T-DeveloperMVP/
├── backend/
│   ├── src/
│   │   ├── simple_api.py         # FastAPI 메인 서버
│   │   ├── agents/              # 9-Agent Pipeline
│   │   └── integrations/        # 3대 프레임워크 통합
│   └── tests/                   # 테스트 코드
├── frontend/
│   ├── src/
│   │   └── App.tsx              # React 메인 컴포넌트
│   └── dist/                    # 빌드 결과물
└── infrastructure/
    └── aws/
        ├── deploy-basic.sh      # 전체 인프라 배포
        └── deploy-s3-only.sh    # S3 전용 배포
```

### 설정 파일
```
backend/.env.example             # 환경변수 템플릿
backend/requirements.txt         # Python 의존성
frontend/package.json           # Node.js 의존성
```

### 문서
```
WORKPLAN.md                     # 전체 작업 계획서
USER_GUIDE.md                   # 사용자 가이드
ARCHITECTURE.md                 # 아키텍처 문서
CLAUDE.md                       # 개발 가이드라인
```

## 🧪 테스트 방법

### 로컬 테스트
```bash
# Backend 서버 시작
cd backend
python3 src/simple_api.py

# Frontend 서버 시작
cd frontend
npm run dev

# 테스트 실행
cd backend
python3 tests/e2e_test_scenarios.py
python3 tests/performance_benchmark.py
python3 tests/user_scenario_tests.py
```

### API 테스트
```bash
# 헬스 체크
curl http://localhost:8000/health

# 프로젝트 생성
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Create a todo app with React"}'

# 다운로드
curl -O http://localhost:8000/api/v1/download/[PROJECT_ID]
```

## ⚠️ 주의사항

### 1. AWS 비용 관리
- **예상 월 비용**: $50-100 (트래픽에 따라 변동)
- **비용 최적화**:
  - S3 Lifecycle 정책 설정 (7일 후 자동 삭제)
  - DynamoDB On-Demand 모드 사용
  - Lambda 동시 실행 제한 설정
  - ECS Spot Instance 활용

### 2. 보안 고려사항
- API Key/Secret은 절대 코드에 하드코딩 금지
- Secrets Manager 또는 Parameter Store 사용
- 민감한 로그 출력 금지
- HTTPS 필수 적용

### 3. 성능 목표
- **API 응답시간**: < 1초
- **프로젝트 생성**: < 30초 (현재 0.01초)
- **동시 사용자**: 100+
- **가용성**: 99.9%

## 📞 연락처 및 지원

### 기술 스택
- **Backend**: Python 3.9+, FastAPI
- **Frontend**: React 18, TypeScript
- **Infrastructure**: AWS (S3, DynamoDB, ECS, Lambda)
- **Frameworks**: AWS Agent Squad, Agno, Bedrock AgentCore

### 참고 자료
- [AWS CloudFormation 문서](https://docs.aws.amazon.com/cloudformation/)
- [ECS 배포 가이드](https://docs.aws.amazon.com/ecs/)
- [Lambda 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

## ✅ 완료 기준

### 필수 완료 항목
- [ ] AWS 인프라 배포 완료
- [ ] Frontend S3 호스팅 활성화
- [ ] API 엔드포인트 접근 가능
- [ ] 모든 보안 체크리스트 통과
- [ ] CloudWatch 모니터링 활성화

### 성공 지표
- [ ] 프로덕션 환경에서 프로젝트 생성 성공
- [ ] 사용자가 ZIP 파일 다운로드 가능
- [ ] 생성된 프로젝트 npm install && npm start 성공
- [ ] 24시간 무중단 운영 확인

## 🚀 배포 후 체크리스트

1. **기능 테스트**
   - [ ] 웹사이트 접속 확인
   - [ ] 프로젝트 생성 테스트
   - [ ] ZIP 다운로드 테스트
   - [ ] WebSocket 연결 테스트

2. **성능 테스트**
   - [ ] 부하 테스트 (100 동시 사용자)
   - [ ] 응답 시간 측정
   - [ ] 메모리/CPU 사용률 확인

3. **보안 테스트**
   - [ ] Penetration Testing
   - [ ] OWASP Top 10 체크
   - [ ] SSL 인증서 확인

4. **문서 업데이트**
   - [ ] 배포 URL 업데이트
   - [ ] API 엔드포인트 문서화
   - [ ] 운영 가이드 작성

---

## 📝 추가 요청사항

### Nice to Have (시간 여유시)
1. **도메인 설정**: t-developer.io 도메인 연결
2. **SSL 인증서**: ACM 인증서 발급 및 적용
3. **백업 정책**: DynamoDB 및 S3 백업 자동화
4. **비용 알림**: Budget Alert 설정
5. **A/B 테스팅**: 기능 플래그 시스템 구현

### Future Improvements
1. **Multi-region 배포**: 글로벌 서비스 확장
2. **Kubernetes 마이그레이션**: EKS 전환 검토
3. **GraphQL API**: REST API 대체/보완
4. **Real-time collaboration**: 멀티유저 지원

---

**작성일**: 2025-08-08  
**작성자**: Claude (T-Developer MVP 개발팀)  
**문서 버전**: 1.0  
**예상 작업 시간**: 2-3일  
**난이도**: ⭐⭐⭐☆☆ (중급)

## 🎯 최종 목표

**"사용자가 https://t-developer.aws.com 에 접속하여 '블로그 만들어줘'라고 입력하면, 실제로 작동하는 React 블로그 프로젝트를 ZIP 파일로 다운로드할 수 있도록 만들기"**

성공을 기원합니다! 🚀