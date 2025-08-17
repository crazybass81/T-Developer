# 🔗 T-Developer UI 통합 계획

## 📊 현재 시스템 구조 분석

### ✅ 이미 구축된 것들

1. **Backend Infrastructure**
   - AWS Account: 036284794745
   - Region: us-east-1
   - DynamoDB tables 정의됨
   - Lambda 배포 스크립트 존재
   - API Gateway 설정 준비됨

2. **Agent System**
   - ResearchAgent ✅
   - PlannerAgent ✅
   - RefactorAgent ✅
   - EvaluatorAgent ✅
   - AgentCore 런타임 ✅
   - Bedrock 통합 ✅

3. **Evolution System**
   - `run_real_evolution.py` - 실제 진화 실행
   - AI 통합 (OpenAI/Anthropic)
   - Git 통합
   - 메트릭 수집

4. **Frontend UI**
   - React Dashboard ✅
   - WebSocket 클라이언트 ✅
   - Redux 상태 관리 ✅
   - Chart.js 시각화 ✅

## 🎯 통합 전략

### Phase 1: AWS 인프라 활용 (오늘)

```bash
# 1. DynamoDB 테이블 생성
python scripts/deploy_aws_infrastructure.py

# 2. Lambda 함수 배포
python scripts/deploy_agents_to_lambda.py

# 3. API Gateway 설정
# scripts/deploy_aws_infrastructure.py에 포함됨
```

### Phase 2: Frontend 연동 (내일)

```javascript
// Frontend에서 API Gateway 엔드포인트 사용
const API_ENDPOINT = 'https://xxxx.execute-api.us-east-1.amazonaws.com/prod';

// Lambda 함수 호출
await fetch(`${API_ENDPOINT}/agents/execute`, {
  method: 'POST',
  body: JSON.stringify({ agent: 'research', task: {...} })
});
```

### Phase 3: Evolution UI 연동

- `run_real_evolution.py`를 Lambda로 래핑
- UI에서 Evolution 시작/중지 제어
- DynamoDB에서 진행 상황 읽기

## 🗑️ 정리할 파일들

- ❌ api_server.py (중복)
- ❌ api_server_simple.py (테스트용)
- ❌ test_integration.py (임시)
- ❌ test_agentcore.py (임시)

## 📁 유지할 구조

```
T-DeveloperMVP/
├── packages/           # ✅ 핵심 에이전트 시스템
├── scripts/           # ✅ 배포 스크립트
├── frontend/          # ✅ React UI
├── docs/             # ✅ 문서
├── tests/            # ✅ 테스트
└── run_real_evolution.py  # ✅ 진화 실행

```

## 🚀 실행 계획

### 1. AWS 리소스 생성

```bash
cd /home/ec2-user/T-DeveloperMVP
python scripts/deploy_aws_infrastructure.py
```

### 2. Lambda 함수 배포

```bash
python scripts/deploy_agents_to_lambda.py
```

### 3. Frontend 업데이트

```javascript
// frontend/src/services/api.ts 수정
const API_BASE_URL = process.env.REACT_APP_API_GATEWAY_URL;
```

### 4. 테스트

```bash
# Lambda 함수 테스트
aws lambda invoke --function-name tdev-research-agent out.json

# API Gateway 테스트
curl https://xxxx.execute-api.us-east-1.amazonaws.com/prod/agents
```

## ⚠️ 주의사항

- 새로운 API 서버 만들지 말 것
- 기존 Lambda/DynamoDB 활용
- WebSocket 대신 Lambda 이벤트 스트림 사용 고려
- 비용 최적화를 위해 온디맨드 실행
