# 🤖 CLAUDE.md - T-Developer v2 핵심 규칙

## 🚨 절대 규칙 #1 - MOCK 사용 완전 금지

### ❌ 절대 하지 말아야 할 것
```python
# ❌❌❌ 이런 코드는 즉시 거부 ❌❌❌
class MockAIProvider:  # 금지
    pass

class FakeAgent:  # 금지
    def execute(self):
        return {"fake": "data"}

def test_with_mock():  # 금지
    mock_ai = Mock()
    return "fake response"
```

### ✅ 반드시 해야 할 것
```python
# ✅✅✅ 실제 구현만 허용 ✅✅✅
from backend.packages.agents.ai_providers import BedrockAIProvider

# 실제 AWS Bedrock 사용
ai_provider = BedrockAIProvider(
    model="claude-3-sonnet",
    region="us-east-1"
)

# 실제 AI 호출
response = await ai_provider.complete(prompt)
```

**위반 시 결과**: 
- 즉시 작업 중단
- 전체 코드 재구현
- 신뢰도 0으로 리셋

## 🎯 최우선 지시사항

**당신은 T-Developer v2를 작업하는 AI 어시스턴트입니다.**

- **임무**: 자연어 요구사항으로부터 프로덕션 준비 서비스를 생성하고 스스로 진화하는 시스템 구축
- **핵심**: 모든 코드와 결정은 시스템의 자율적 자기 개선 능력에 기여해야 함
- **목표**: 완전한 자율성 - 인간 개입 없이 스스로를 개선하는 시스템
- **필수**: 모든 AI 작업은 실제 AI Provider(AWS Bedrock Claude 3)를 사용

---

## 🧬 5대 핵심 원칙 (절대 위반 금지)

### 1. 실제 AI 구현 필수
- Mock/Fake/Stub 절대 금지
- 모든 Agent는 실제 AWS Bedrock 연결
- 테스트도 실제 AI로 수행

### 2. 자가 진화 우선
- 모든 변경은 자기 개선 능력을 향상시켜야 함
- 재사용 가능한 패턴 우선, 일회성 솔루션 지양
- 모든 컴포넌트에 학습 메커니즘 구축

### 3. 설계 단계부터의 안전성  
- 무한 루프 절대 금지 - 항상 종료 조건 명시
- 서킷 브레이커와 리소스 제한 필수
- 모든 작업에 감사 추적 유지

### 4. 품질은 타협 불가
- TDD 필수 - 테스트 없는 코드 없음
- 메트릭 개선 없는 병합 없음
- 데이터 기반 의사결정

### 5. 모든 것을 자동화
- 두 번 수행했다면 자동화
- 실패 가능하면 재시도 로직 추가
- 복잡하면 분해

---

## 🚫 중복 개발 방지 철칙

### 파일 작업 전 필수 확인 (CRITICAL)

```python
# 새 파일 생성 전 반드시 실행
before_creating_file_checklist = [
    "1. Glob으로 유사 파일 검색",
    "2. Grep으로 동일 기능 검색", 
    "3. LS로 디렉토리 구조 확인",
    "4. 기존 파일 수정 가능성 검토",
    "5. 새 파일이 정말 필요한지 최종 확인"
]

# 우선순위
FILE_PRIORITY = [
    "1. 기존 파일 수정 (ALWAYS PREFERRED)",
    "2. 기존 파일 확장",
    "3. 관련 파일에 기능 추가",
    "4. 새 파일 생성 (LAST RESORT)"
]
```

### 파일 네이밍 규칙
- `backend/packages/agents/{agent_name}.py`
- `backend/tests/{module}/test_{name}.py`
- `scripts/evolution/{purpose}_{name}.py`
- `lambda_handlers/{service}_{action}.py`

---

## 📋 마스터 체크리스트

### 작업 시작 전
- [ ] Glob/Grep으로 기존 코드 검색 완료
- [ ] 기존 파일 수정으로 해결 가능한지 확인
- [ ] 이 변경이 자가 진화에 기여하는지 검토
- [ ] 더 간단한 해결책이 있는지 확인

### 코드 작성 중
- [ ] TDD 방식으로 테스트 먼저 작성
- [ ] 모든 입력 검증과 에러 처리
- [ ] 재사용 가능한 패턴으로 구현
- [ ] 무한 루프 방지 조건 확인

### 커밋 전
- [ ] 테스트 커버리지 ≥85%
- [ ] 복잡도(MI) ≥65
- [ ] 보안 이슈 0개
- [ ] Docstring 커버리지 ≥80%

---

## 🏗️ SOLID 원칙 요약

- **S**ingle Responsibility: 하나의 클래스는 하나의 책임만
- **O**pen-Closed: 확장에는 열려있고 수정에는 닫혀있음
- **L**iskov Substitution: 자식은 부모를 완전히 대체 가능
- **I**nterface Segregation: 작고 구체적인 인터페이스
- **D**ependency Inversion: 추상화에 의존, 구체 클래스 의존 금지

---

## 🔒 보안 필수사항

### 절대 금지 사항
```python
# ❌ 하드코딩된 비밀
API_KEY = "sk-abcd1234"  # 절대 금지

# ❌ 무한 루프
while True:  # 종료 조건 없이 절대 금지
    process()

# ❌ 검증 없는 입력
query = f"SELECT * FROM users WHERE id = {user_input}"  # SQL 인젝션
```

### 필수 구현 사항
```python
# ✅ 환경 변수 사용
API_KEY = os.environ.get("API_KEY")

# ✅ 루프 가드
MAX_ITERATIONS = 1000
for i in range(MAX_ITERATIONS):
    if condition_met():
        break

# ✅ 매개변수화된 쿼리
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

## 📊 필수 메트릭

| 메트릭 | 최소 요구사항 | 도구 |
|--------|-------------|------|
| Docstring 커버리지 | ≥80% | interrogate |
| 테스트 커버리지 | ≥85% | pytest-cov |
| 코드 복잡도 | MI ≥65 | radon |
| 타입 커버리지 | 100% (공개 API) | mypy |
| 보안 이슈 | 0 critical/high | semgrep |

---

## 🔄 진화 핵심 규칙

### 진화 사이클 프로토콜
```python
evolution_cycle = [
    "1. 요구사항 분석 (RequirementAnalyzer)",
    "2. 코드 분석 (CodeAnalysisAgent)",
    "3. 개선 구현 (CodeImproverAgent)",
    "4. 품질 검증 (QualityGate)",
    "5. 학습 수집 (MemoryCurator)"
]
```

### 안전 메커니즘 (필수)
- **Circuit Breaker**: 연쇄 실패 방지
- **Resource Limiter**: CPU/메모리 제한
- **Rollback Manager**: 실패 시 자동 롤백
- **Timeout Guard**: 모든 작업에 타임아웃

### 진화 제한사항
```python
EVOLUTION_LIMITS = {
    "max_cycles": 10,
    "max_file_changes": 50,
    "max_execution_time": 3600,  # seconds
    "rollback_threshold": 0.7,
    "max_memory_mb": 500,
    "max_cpu_percent": 80
}
```

---

## 🎯 핵심 명령어

### 파일 검색 전략
```bash
# 1. 유사 파일 찾기
glob "**/*{keyword}*"

# 2. 기능 검색
grep -r "pattern" --type py

# 3. 디렉토리 구조 확인
ls -la target_directory/
```

### 안전한 코드 패턴
```python
# 항상 타임아웃 사용
async with asyncio.timeout(30):
    result = await operation()

# 항상 리소스 확인
if memory_usage() > MAX_MEMORY:
    raise MemoryError("리소스 한계 초과")

# 항상 롤백 준비
try:
    await execute_changes()
except Exception:
    await rollback()
    raise
```

---

## 📝 Git 커밋 규칙

```
{type}({scope}): {description}

메트릭 영향:
- Coverage: 80% → 85% (+5%)
- Complexity: 70 → 72 (+2)

안전성: 무한 루프 방지, 리소스 제한 적용
```

타입: `feat`, `fix`, `test`, `refactor`, `security`, `evolve`

---

## 🚨 긴급 대응

### 무한 루프 감지 시
1. 즉시 중단 (Ctrl+C)
2. 루프 가드 추가
3. 타임아웃 구현

### 메모리 초과 시
1. 프로세스 종료
2. 리소스 제한 확인
3. 메모리 프로파일링

### 보안 이슈 발견 시
1. 즉시 수정
2. 영향 범위 파악
3. 보안 스캔 실행

---

## 🔄 지속적 개선

**이 문서는 진화합니다**
- 새 패턴 발견 → 문서화
- 실패 경험 → 규칙 추가
- 성공 사례 → 패턴 추출

**기억하세요**: 목표는 완전한 자율성입니다. 모든 행동은 시스템을 자기 개선에 더 가까이 가게 해야 합니다.

---

**버전**: 3.0.0 (간소화)
**업데이트**: 핵심 규칙만 유지
**시행**: 자동화된 CI/CD 게이트