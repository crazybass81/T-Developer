# API Gateway (Future Expansion)

## 🚧 현재 상태: 준비됨 (미구현)

현재는 `simple_api.py`가 모든 API 요청을 처리하지만, 향후 마이크로서비스 확장을 위해 구조가 준비되어 있습니다.

## 🎯 미래 구현 예정 기능

### 1. 에이전트별 독립 엔드포인트
```typescript
// 각 에이전트가 독립적인 API 엔드포인트를 가짐
/api/v1/agents/nl-input
/api/v1/agents/ui-selection
/api/v1/agents/parser
/api/v1/agents/component-decision
/api/v1/agents/match-rate
/api/v1/agents/search
/api/v1/agents/generation
/api/v1/agents/assembly
/api/v1/agents/download
```

### 2. Monitoring 폴더
- **목적**: 각 에이전트별 성능 모니터링
- **기능**: 응답시간, 에러율, 처리량 추적
- **연동**: CloudWatch, Prometheus 메트릭

### 3. Versioning 폴더
- **목적**: API 버전 관리
- **기능**: v1, v2 병렬 지원
- **호환성**: 하위 호환성 보장

## 🔄 마이그레이션 계획

### Phase 1: 현재 (Single API)
```
simple_api.py → All 9 Agents
```

### Phase 2: Gateway 도입
```
API Gateway → Route to simple_api.py
```

### Phase 3: 마이크로서비스 분할
```
API Gateway → Agent-specific services
              ├── nl-input-service
              ├── ui-selection-service
              └── ...
```

## 💾 DynamoDB 연동 계획

### 테이블 설계
- `agent_executions` - 에이전트 실행 상태
- `pipeline_sessions` - 파이프라인 세션 관리
- `user_preferences` - 사용자 설정 저장
- `project_history` - 프로젝트 생성 이력

### Step Functions 연동
- 각 에이전트 상태를 DynamoDB에 저장
- 실패 시 재시작 지점 복구
- 장시간 실행 워크플로우 지원

## 🛡️ 보안 미들웨어

### 현재 적용됨
- CORS 미들웨어 ✅
- 입력 검증 ✅

### 향후 추가 예정
- JWT 인증
- 레이트 리미팅
- IP 화이트리스트
- 요청 로깅

## 📊 성능 최적화

### 현재 적용
- 메모리 최적화 ✅
- 에이전트별 타임아웃 ✅

### 향후 추가
- 로드 밸런싱
- 캐시 레이어
- 연결 풀링
- Circuit Breaker

---
**⚠️ 중요**: 이 폴더의 구성요소들은 현재 사용되지 않지만, 시스템 확장 시 필수적입니다. 삭제하지 마세요!