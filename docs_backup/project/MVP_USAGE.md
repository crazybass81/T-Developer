# 🚀 T-Developer MVP 사용 가이드

## 현재 상태

- ✅ **백엔드**: <http://localhost:8000> (FastAPI)
- ✅ **프론트엔드**: <http://localhost:3001> (React + Vite)
- ✅ **API 연결**: 정상 작동
- ✅ **Evolution**: Mock agents로 기본 사이클 작동

## 🎯 접속 정보

### 웹 UI

```
http://localhost:3001
```

### API 문서

```
http://localhost:8000/docs
```

## 🔧 실행 중인 서비스

### 백엔드 (Port 8000)

- FastAPI 서버
- Mock Agents (research, planner, refactor, evaluator)
- Evolution Engine 오케스트레이터
- WebSocket 지원

### 프론트엔드 (Port 3001)

- React Dashboard
- Real-time Updates
- Evolution Control Panel
- Metrics Visualization

## 📋 Evolution 실행 방법

### 1. UI에서 실행

1. <http://localhost:3001> 접속
2. "Evolution" 탭 클릭
3. Target Path 입력 (예: `/home/ec2-user/T-DeveloperMVP/backend/packages/agents/base.py`)
4. Dry Run 체크 (안전 모드)
5. "Start Evolution" 클릭

### 2. API로 실행

```bash
curl -X POST http://localhost:8000/api/evolution/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_path": "./backend/packages/agents/base.py",
    "max_cycles": 1,
    "focus_areas": ["documentation", "quality"],
    "dry_run": true
  }'
```

### 3. 상태 확인

```bash
curl http://localhost:8000/api/evolution/status | jq .
```

## 🏗️ 현재 아키텍처

```
User → Frontend (3001) → Backend API (8000) → Evolution Engine
                                                     ↓
                                             Agent Manager
                                                     ↓
                                        Mock Agents (로컬 실행)
```

## ⚙️ 환경 설정

### API Keys (이미 설정됨)

- `OPENAI_API_KEY`: GPT-4 사용
- `ANTHROPIC_API_KEY`: Claude 3 사용

### Evolution 설정

- `EVOLUTION_MODE`: disabled (Mock agents 사용)
- `AI_AUTONOMY_LEVEL`: 0.85
- Dry Run 모드 기본 활성화

## 🎮 주요 API 엔드포인트

| 엔드포인트 | 메소드 | 설명 |
|-----------|--------|------|
| `/` | GET | 서버 상태 확인 |
| `/api/agents` | GET | 에이전트 목록 |
| `/api/evolution/start` | POST | Evolution 시작 |
| `/api/evolution/status` | GET | Evolution 상태 |
| `/api/evolution/stop` | POST | Evolution 중지 |
| `/api/metrics` | GET | 시스템 메트릭 |
| `/ws` | WebSocket | 실시간 업데이트 |

## 🚦 다음 단계

### 단기 (1-2시간)

1. **실제 에이전트 활성화**
   - Mock agents → Real agents
   - AI 모델 통합 테스트
   - 실제 코드 분석 구현

2. **첫 실제 Evolution**
   - 간단한 파일로 테스트
   - Docstring 개선
   - 결과 검증

### 중기 (1-2일)

1. **안전장치 강화**
   - Git 브랜치 자동 생성
   - 변경사항 롤백 기능
   - 테스트 자동 실행

2. **메트릭 개선**
   - 실제 코드 품질 측정
   - 성능 벤치마크
   - 비용 추적

### 장기 (1주일+)

1. **AgentCore 마이그레이션**
   - AWS Bedrock 통합
   - Lambda 배포
   - DynamoDB 상태 관리

2. **프로덕션 준비**
   - 인증/권한 관리
   - 멀티테넌시
   - 모니터링/알림

## 🐛 문제 해결

### 서버가 시작되지 않을 때

```bash
# 포트 확인
lsof -i :8000
lsof -i :3001

# 프로세스 종료
kill $(lsof -t -i:8000)
kill $(lsof -t -i:3001)
```

### Evolution이 실패할 때

1. 로그 확인: `backend/server.log`
2. Mock agents 상태 확인
3. Dry run 모드 확인

### API 연결 실패

1. CORS 설정 확인
2. 포트 번호 확인
3. 방화벽 설정 확인

## 📚 참고 자료

- [FastAPI Docs](http://localhost:8000/docs)
- [CLAUDE.md](./CLAUDE.md) - AI 규칙 및 가이드
- [MASTER_PLAN.md](./MASTER_PLAN.md) - 전체 계획

---

**현재 MVP는 정상 작동 중입니다!** 🎉

Backend: <http://localhost:8000>
Frontend: <http://localhost:3001>

Mock agents로 기본 Evolution 사이클이 작동하며,
실제 AI 통합을 위한 준비가 완료되었습니다.
