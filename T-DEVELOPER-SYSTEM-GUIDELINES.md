# 🎯 T-Developer System 통합 개발 지침

## 📌 핵심 개요

T-Developer는 **AI 기반 멀티 에이전트 개발 플랫폼**으로, 자연어 설명만으로 완전한 애플리케이션을 생성하는 시스템입니다.

### 시스템 목표
- 자연어 → 실행 가능한 애플리케이션 자동 변환
- 초고성능 에이전트 실행 (3μs 인스턴스화, 6.5KB 메모리)
- 엔터프라이즈급 보안 및 확장성
- 8시간 장기 세션 지원

## 🏗️ 핵심 아키텍처 구성요소

### 1. 기술 스택 통합
```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 인터페이스 계층                     │
│  - 자연어 입력 (7개 언어 지원)                               │
│  - 실시간 진행 상황 추적                                     │
│  - 라이브 코드 프리뷰                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              AWS Agent Squad 오케스트레이션                  │
│  - SupervisorAgent (프로젝트 매니저)                         │
│  - 지능형 작업 라우팅 (오픈소스, API 키 불필요)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    9개 핵심 에이전트                         │
│  Phase 1: NL Input → UI Selection → Parser                  │
│  Phase 2: Component Decision → Match Rate → Search          │
│  Phase 3: Generation → Assembly → Download                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│     Agno Framework (초고속 에이전트 실행 엔진)               │
│  - 3μs 인스턴스화 / 6.5KB 메모리 / 10,000+ 동시 실행        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         AWS Bedrock AgentCore (엔터프라이즈 런타임)          │
│  - 8시간 세션 지원 / 자동 스케일링 / 보안 격리               │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 핵심 개발 지침

### 1. 에이전트 개발 원칙

#### 1.1 에이전트 생성 규칙
```python
# 모든 에이전트는 다음 패턴을 따라야 함
class CustomAgent:
    def __init__(self):
        # Agno Framework 사용 (초고속 인스턴스화)
        self.agent = Agent(
            name="에이전트명",
            model=AwsBedrock(id="모델ID"),  # Bedrock 우선 사용
            memory=DiskMemory(dir="agents/경로"),  # 상태 영속성
            tools=[필요한_도구들],  # 최소한의 도구만 사용
            instructions=["명확한_지시사항"]  # 구체적 역할 정의
        )
```

#### 1.2 에이전트 간 통신
```python
# 비동기 이벤트 기반 통신 사용
async def communicate():
    # EventBridge 통한 느슨한 결합
    await event_bus.publish({
        "source": "agent.source",
        "detail-type": "TaskCompleted",
        "detail": result
    })
```

### 2. 성능 최적화 필수 사항

#### 2.1 Agno Framework 활용
- **반드시** Agno Framework 사용하여 3μs 인스턴스화 달성
- 에이전트당 메모리 6.5KB 제한 준수
- 에이전트 풀링 사용하여 재사용성 극대화

#### 2.2 병렬 처리
```python
# 가능한 모든 작업은 병렬로 처리
tasks = [agent.arun(task) for task in subtasks]
results = await asyncio.gather(*tasks)
```

### 3. AWS 서비스 통합 규칙

#### 3.1 Bedrock 모델 사용 우선순위
```python
MODEL_PRIORITY = [
    "amazon.nova-pro-v1:0",      # 기본 모델
    "anthropic.claude-3-sonnet",  # 복잡한 분석
    "anthropic.claude-3-haiku",   # 빠른 응답
    "cohere-command",             # 코드 생성
]
```

#### 3.2 DynamoDB 세션 저장
```python
# 모든 세션 데이터는 DynamoDB에 저장
session_store = DynamoDBSessionStore(
    table_name="t-developer-sessions",
    ttl=28800  # 8시간
)
```

### 4. 9개 에이전트 워크플로우

#### Phase 1: 요구사항 분석 (완료도: 87.5%)
```python
# 1. NL Input Agent (100% 완료)
- 자연어 프로젝트 설명 처리
- 멀티모달 입력 지원
- 7개 언어 지원

# 2. UI Selection Agent (100% 완료) 
- 최적 프론트엔드 프레임워크 선택
- 디자인 시스템 통합
- 접근성 검증

# 3. Parser Agent (62.5% 완료)
- 기존 코드 분석
- AST 분석 및 패턴 감지
- 재사용 가능 컴포넌트 추출
```

#### Phase 2: 컴포넌트 선택 (45.8%)
```python
# 4. Component Decision Agent (50% 완료)
- 아키텍처 결정
- 다중 기준 의사결정 (MCDM)
- 리스크 평가

# 5. Match Rate Agent (50% 완료)
- 호환성 점수 계산
- 의미적 유사도 분석

# 6. Search Agent (37.5% 완료)
- NPM/PyPI/GitHub 검색
- 실시간 인덱싱
```

#### Phase 3: 코드 생성 및 배포 (52.1%)
```python
# 7. Generation Agent (75% 완료)
- AI 모델 사용한 코드 생성
- 템플릿 시스템

# 8. Assembly Agent (50% 완료)
- 컴포넌트 통합
- 통합 테스트

# 9. Download Agent (31.25% 완료)
- 프로젝트 패키징
- 빌드 시스템 통합
```

## 🔒 보안 및 규정 준수

### 1. 인증/인가
```python
# JWT 기반 인증 필수
AUTH_CONFIG = {
    "type": "JWT",
    "secret_manager": "AWS Secrets Manager",
    "rotation": "30 days"
}
```

### 2. 데이터 보호
- 전송 중 암호화: TLS 1.3
- 저장 시 암호화: AES-256-GCM
- PII 데이터 마스킹 필수

### 3. API Rate Limiting
```python
RATE_LIMITS = {
    "general": "100/minute",
    "ai_generation": "10/minute", 
    "download": "5/minute"
}
```

## 📊 모니터링 및 로깅

### 1. 필수 메트릭
```python
REQUIRED_METRICS = [
    "agent_instantiation_time",  # 목표: <5μs
    "memory_per_agent",          # 목표: <10KB
    "api_response_time",         # 목표: <500ms
    "project_generation_time",   # 목표: <10분
    "error_rate",               # 목표: <0.1%
]
```

### 2. 로깅 표준
```python
logger.info({
    "agent": agent_name,
    "action": action_type,
    "duration": elapsed_time,
    "user_id": user_id,
    "session_id": session_id,
    "result": result_status
})
```

## 🚀 배포 체크리스트

### 환경 변수 설정
```bash
# AWS 자격 증명
AWS_ACCESS_KEY_ID=필수
AWS_SECRET_ACCESS_KEY=필수
AWS_REGION=us-east-1

# Bedrock 설정
AWS_BEDROCK_REGION=us-east-1
BEDROCK_AGENTCORE_RUNTIME_ID=필수

# AI 모델 (선택적)
OPENAI_API_KEY=선택
ANTHROPIC_API_KEY=선택

# 성능 설정
AGNO_MAX_WORKERS=10
MAX_CONCURRENT_AGENTS=50
```

### 필수 AWS 리소스
- [ ] DynamoDB 테이블 생성
- [ ] S3 버킷 설정
- [ ] Lambda 함수 배포
- [ ] CloudWatch 대시보드 구성
- [ ] EventBridge 규칙 설정

## 📝 코드 작성 규칙

### 1. TypeScript/Python 표준
```typescript
// TypeScript
interface AgentResponse {
    success: boolean;
    data?: any;
    error?: Error;
    metadata: {
        agentName: string;
        processingTime: number;
        tokensUsed: number;
    };
}
```

```python
# Python
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AgentResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]
```

### 2. 에러 처리
```python
try:
    result = await agent.process(request)
except AgentTimeoutError:
    # 재시도 로직
    result = await retry_with_backoff(agent.process, request)
except Exception as e:
    # 로깅 및 폴백
    logger.error(f"Agent failed: {e}")
    result = await fallback_agent.process(request)
```

### 3. 테스트 요구사항
- 단위 테스트 커버리지: 80% 이상
- 통합 테스트: 모든 에이전트 워크플로우
- E2E 테스트: 전체 프로젝트 생성 플로우

## 🔄 지속적 개선

### 1. 성능 모니터링
- CloudWatch 대시보드 일일 확인
- 병목 현상 식별 및 최적화
- 에이전트 메모리 사용량 추적

### 2. 사용자 피드백
- 생성된 코드 품질 평가
- 응답 시간 만족도
- 기능 요청 우선순위화

### 3. 모델 업데이트
- 새로운 Bedrock 모델 평가
- 프롬프트 엔지니어링 개선
- 파인튜닝 기회 식별

## 🎯 핵심 성공 지표 (KPI)

1. **기술적 KPI**
   - 에이전트 인스턴스화: <5μs (현재: 3μs ✅)
   - API 응답 시간: <500ms (목표)
   - 동시 사용자: 10,000+ (목표)
   - 가용성: 99.99% (목표)

2. **비즈니스 KPI**
   - 프로젝트 생성 성공률: >95%
   - 사용자 만족도: >4.5/5
   - 평균 프로젝트 생성 시간: <5분
   - 코드 품질 점수: >85/100

## ⚠️ 주의사항

1. **절대 하지 말아야 할 것**
   - Agno Framework 없이 에이전트 생성 ❌
   - 동기식 블로킹 호출 ❌
   - 하드코딩된 자격 증명 ❌
   - 테스트 없는 배포 ❌

2. **항상 해야 할 것**
   - 비동기 패턴 사용 ✅
   - 에러 처리 및 재시도 로직 ✅
   - 성능 메트릭 로깅 ✅
   - 보안 베스트 프랙티스 준수 ✅

---

**이 지침은 T-Developer 시스템의 모든 개발 활동에 적용되며, 정기적으로 업데이트됩니다.**

마지막 업데이트: 2025-08-06
버전: 1.0.0