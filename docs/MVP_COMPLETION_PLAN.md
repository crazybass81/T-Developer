# 📋 T-Developer v2 MVP 완성 계획

## 🎯 현재 상태 분석

### ✅ 완료된 구성요소

1. **백엔드 서버** (FastAPI)
   - API 엔드포인트 구현 완료
   - WebSocket 실시간 통신 지원
   - SharedContextStore 통합

2. **Evolution Engine**
   - 4단계 진화 사이클 구현
   - 병렬 처리 (Research + Analysis)
   - 3-way 비교 평가 시스템

3. **Agent 시스템**
   - ResearchAgent, CodeAnalysisAgent, PlannerAgent, RefactorAgent, EvaluatorAgent 구현
   - AgentManager를 통한 중앙 관리
   - 비동기 태스크 처리

4. **Frontend UI** (React/TypeScript)
   - Dashboard, Agents, Evolution, Metrics 페이지
   - Redux 상태 관리
   - WebSocket 연결

### ⚠️ 미완성 항목

1. **Agent-SharedContextStore 통합**
   - 각 Agent에 context_store 속성 추가 필요
   - 데이터 플로우 연결 미완성

2. **Claude Code 통합**
   - Claude Code SDK/CLI 설정 필요
   - MCP (Model Context Protocol) 구성
   - RefactorAgent를 Claude Code 기반으로 재구현

3. **AWS 인프라**
   - Lambda 핸들러 미배포
   - API Gateway 미구성
   - DynamoDB 테이블 미생성

4. **Frontend-Backend 통합**
   - API 호출 연결 미완성
   - 실시간 데이터 업데이트 구현 필요

## 🚀 MVP 완성 로드맵

### Phase 1: 핵심 기능 연결 (1-2일)

#### 1.1 Agent-SharedContextStore 통합

```python
# backend/packages/agents/base.py에 추가
def __init__(self):
    self.context_store = get_context_store()
```

#### 1.2 Claude Code 통합 설정

```bash
# Claude Code CLI 설치
pip install claude-code-sdk
# 또는 npm install -g @anthropic/claude-code

# MCP 설정 파일 생성
cat > mcp_config.json << EOF
{
  "tools": ["filesystem", "git", "github"],
  "write_scope": ["backend/", "frontend/src/"],
  "pr_only": true,
  "sandbox": true
}
EOF
```

#### 1.3 RefactorAgent를 Claude Code 기반으로 재구현

```python
# backend/packages/agents/claude_code_refactor.py
from claude_code import ClaudeCodeClient

class ClaudeCodeRefactorAgent:
    def __init__(self):
        self.client = ClaudeCodeClient(
            mcp_config="mcp_config.json",
            pr_only=True  # PR만 생성, main 직접 push 차단
        )

    async def execute(self, tasks, target_path):
        # Claude Code에게 코드 수정 지시
        result = await self.client.refactor(
            instructions=tasks,
            path=target_path,
            create_pr=True
        )
        return result
```

### Phase 2: Frontend-Backend 완전 통합 (2-3일)

#### 2.1 API 연결 구현

- `frontend/src/services/api.ts` 완성
- 실제 API 호출로 교체
- 에러 핸들링 추가

#### 2.2 실시간 업데이트

- WebSocket 메시지 처리
- Redux 액션 디스패치
- UI 자동 업데이트

#### 2.3 상태 동기화

- Backend 상태와 Frontend 동기화
- 진화 진행 상황 실시간 표시
- 메트릭 대시보드 업데이트

### Phase 3: AWS 인프라 구축 (2-3일)

#### 3.1 Lambda 함수 배포

```bash
python scripts/update_lambda_handlers.py
```

#### 3.2 API Gateway 구성

```bash
python scripts/create_api_gateway.py
```

#### 3.3 DynamoDB 테이블 생성

- evolution_history 테이블
- agent_metrics 테이블
- pattern_library 테이블

### Phase 4: 테스트 및 검증 (1-2일)

#### 4.1 통합 테스트

```bash
python scripts/test_end_to_end.py
```

#### 4.2 Evolution 실행 테스트

```bash
./run_evolution.sh
```

#### 4.3 성능 및 안정성 테스트

- Load testing (K6)
- Error recovery 테스트
- Rollback 메커니즘 검증

### Phase 5: 문서화 및 배포 (1일)

#### 5.1 사용자 문서

- Quick Start Guide 업데이트
- API 문서 완성
- 비디오 튜토리얼 작성

#### 5.2 배포 준비

- Docker 이미지 빌드
- 환경 변수 정리
- CI/CD 파이프라인 구성

## 📊 성공 지표

### MVP 완성 기준

- [ ] Evolution 사이클 자동 실행
- [ ] 실제 코드 개선 확인 (15% 이상)
- [ ] UI에서 전체 프로세스 모니터링
- [ ] 오류 없이 5회 연속 실행
- [ ] 문서화 100% 완료

### 성능 목표

- Evolution 사이클: < 5분/cycle
- API 응답 시간: < 500ms
- WebSocket 지연: < 100ms
- 메모리 사용: < 512MB
- CPU 사용: < 80%

## 🔧 즉시 실행 가능한 작업

### 1. Agent Context 통합 (30분)

```bash
# 각 Agent에 context_store 추가
cd backend/packages/agents
# research.py, planner.py, refactor.py, evaluator.py 수정
```

### 2. Claude Code 설치 및 설정 (10분)

```bash
# Claude Code SDK 설치
pip install claude-code-sdk anthropic
# MCP 툴 설치
pip install mcp-filesystem mcp-git
pip freeze > requirements.txt
```

### 3. Frontend API 연결 (1시간)

```typescript
// frontend/src/services/api.ts 완성
// 실제 백엔드 API 호출 구현
```

### 4. Evolution 테스트 실행 (20분)

```bash
# Backend 서버 시작
cd backend && python main.py

# 별도 터미널에서 Evolution 실행
./run_evolution.sh
```

## 📅 일정 요약

| 단계 | 작업 | 예상 시간 | 우선순위 |
|------|------|-----------|----------|
| 1 | Agent-Context 통합 | 1일 | 🔴 Critical |
| 2 | Frontend-Backend 통합 | 2일 | 🔴 Critical |
| 3 | AWS 인프라 구축 | 2일 | 🟡 High |
| 4 | 테스트 및 검증 | 1일 | 🟡 High |
| 5 | 문서화 및 배포 | 1일 | 🟢 Medium |

**총 예상 시간**: 7-10일

## 🚨 리스크 및 대응

### 기술적 리스크

1. **AWS 권한 문제**
   - 대응: IAM 역할 검증, 로컬 테스트 우선

2. **Evolution 무한 루프**
   - 대응: Circuit breaker, 타임아웃 설정

3. **코드 손상 위험**
   - 대응: Git 백업, 드라이런 모드 기본값

### 일정 리스크

1. **의존성 충돌**
   - 대응: 가상환경 사용, 버전 고정

2. **테스트 실패**
   - 대응: 단계별 검증, 롤백 계획

## 🎯 다음 단계 액션

1. **즉시 시작**: Agent-Context 통합
2. **오늘 완료**: 의존성 설치 및 테스트
3. **내일 시작**: Frontend API 연결
4. **이번 주 목표**: Phase 1-2 완료

---

**작성일**: 2025-08-17
**작성자**: T-Developer System
**버전**: 1.0.0
**상태**: 🟢 Ready to Execute
