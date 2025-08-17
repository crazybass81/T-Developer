# 🧬 T-Developer v2 진화 가이드

## 개요

이 가이드는 T-Developer v2 시스템을 사용하여 코드베이스를 자동으로 개선하는 방법을 설명합니다.

## 진화란?

**진화(Evolution)**는 T-Developer가 코드베이스를 분석하고, 개선 계획을 수립하며, 실제로 코드를 수정하고, 결과를 평가하는 전체 프로세스입니다.

### 진화의 특징

- **자동화**: 인간 개입 최소화
- **학습**: 각 진화에서 패턴 학습
- **안전**: 롤백 가능한 변경
- **측정 가능**: 메트릭 기반 평가

## 진화 프로세스

### 1단계: 연구 & 분석 (Research & Analysis)

**병렬 실행되는 두 가지 활동:**

#### ResearchAgent

- 외부 베스트 프랙티스 검색
- 유사 프로젝트 패턴 분석
- 최신 기술 동향 수집

#### CodeAnalysisAgent

- 대상 코드베이스 스캔
- 메트릭 측정 (커버리지, 복잡도 등)
- 이슈 및 개선점 식별

**저장되는 데이터:**

```json
{
  "original_analysis": {
    "files_analyzed": 42,
    "metrics": {
      "docstring_coverage": 45,
      "test_coverage": 60,
      "complexity": 75
    },
    "issues": [...],
    "improvements": [...]
  },
  "external_research": {
    "best_practices": [...],
    "references": [...],
    "patterns": [...]
  }
}
```

### 2단계: 계획 (Planning)

**PlannerAgent의 작업:**

- 1단계 데이터 종합
- 구체적 태스크 생성
- 우선순위 설정
- 의존성 매핑

**생성되는 계획 예시:**

```json
{
  "tasks": [
    {
      "id": "task-1",
      "type": "add_docstrings",
      "target": "backend/core/*.py",
      "priority": 1,
      "estimated_impact": 0.15
    },
    {
      "id": "task-2",
      "type": "add_type_hints",
      "target": "backend/packages/**/*.py",
      "priority": 2,
      "estimated_impact": 0.10
    }
  ],
  "dependencies": {
    "task-2": ["task-1"]
  }
}
```

### 3단계: 구현 (Implementation)

**RefactorAgent의 작업:**

- 계획된 태스크 실행
- 외부 도구 활용 (Black, autopep8, doq 등)
- 변경사항 추적
- 백업 생성

**사용 도구:**
| 도구 | 용도 |
|------|------|
| Black | 코드 포맷팅 |
| autopep8 | PEP8 준수 |
| doq | Docstring 생성 |
| pyupgrade | Python 문법 현대화 |
| isort | Import 정렬 |

### 4단계: 평가 (Evaluation)

**EvaluatorAgent의 3-way 비교:**

```
이전 (Before)     계획 (Plan)      이후 (After)
     ↓               ↓                ↓
  [메트릭]        [목표]           [결과]
     └───────────────┼───────────────┘
                     ↓
                 [평가 결과]
```

**평가 기준:**

- 목표 달성도
- 메트릭 개선율
- 부작용 여부
- 전체 성공률

## 진화 실행 방법

### 빠른 시작

```bash
# 1. 백엔드 시작
cd backend && python main.py

# 2. 진화 실행
./run_evolution.sh
```

### 상세 설정

#### 1. 진화 설정 파일 생성

`evolution_config.json`:

```json
{
  "target_path": "/path/to/your/project",
  "focus_areas": [
    "documentation",
    "type_safety",
    "code_quality",
    "error_handling",
    "performance"
  ],
  "max_iterations": 1,
  "improvement_threshold": 0.15,
  "safety_checks_enabled": true,
  "auto_commit": false,
  "dry_run": false
}
```

#### 2. Python 스크립트로 실행

```python
from backend.core.evolution_engine import EvolutionEngine, EvolutionConfig
from backend.models.evolution import FocusArea

async def run_custom_evolution():
    config = EvolutionConfig(
        target_path="/my/project",
        focus_areas=[
            FocusArea.DOCUMENTATION,
            FocusArea.TYPE_SAFETY
        ],
        improvement_threshold=0.20
    )

    engine = EvolutionEngine()
    result = await engine.evolve(config)

    print(f"Success: {result['success']}")
    print(f"Improvements: {result['improvements']}")

asyncio.run(run_custom_evolution())
```

### 3. API를 통한 실행

```bash
# 진화 시작
curl -X POST http://localhost:8000/api/evolution/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_path": "/my/project",
    "focus_areas": ["documentation"],
    "dry_run": false
  }'

# 상태 확인
curl http://localhost:8000/api/evolution/status

# 결과 조회
curl http://localhost:8000/api/context/current
```

## Focus Areas 상세

### documentation

- Docstring 추가/개선
- README 업데이트
- 인라인 주석 추가

### type_safety

- Type hints 추가
- Protocol 정의
- Generic 타입 사용

### code_quality

- 코드 포맷팅
- 복잡도 감소
- 중복 제거

### error_handling

- Try-except 블록 추가
- 에러 메시지 개선
- 로깅 추가

### performance

- 알고리즘 최적화
- 캐싱 추가
- 비동기 처리

## 모니터링

### 실시간 로그

```bash
# 진화 로그 확인
tail -f evolution_run.log

# 특정 단계 필터링
tail -f evolution_run.log | grep "Phase"
```

### 메트릭 추적

```python
# 진화 전후 메트릭 비교
import json

with open("evolution_results/evolution_*.json") as f:
    data = json.load(f)

before = data["comparison"]["before"]["metrics"]
after = data["comparison"]["after"]["metrics"]

for metric, value in before.items():
    improvement = ((after[metric] - value) / value) * 100
    print(f"{metric}: {value} → {after[metric]} ({improvement:+.1f}%)")
```

### WebSocket 모니터링

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  if (msg.type === 'evolution:progress') {
    console.log(`Phase: ${msg.data.phase}, Progress: ${msg.data.progress}%`);
  }
};
```

## 안전 장치

### 드라이런 모드

실제 변경 없이 시뮬레이션:

```json
{
  "dry_run": true
}
```

### 백업 및 롤백

```bash
# 백업 확인
ls -la /tmp/test_evolution_target/.backup_*

# Git을 사용한 롤백
cd /target/project
git status
git diff
git checkout -- .  # 모든 변경 되돌리기
```

### 리소스 제한

`evolution_config.py`:

```python
MAX_MEMORY_MB = 500
MAX_CPU_PERCENT = 80
MAX_EXECUTION_TIME = 300
```

## 결과 분석

### 성공 기준

진화가 성공으로 간주되는 조건:

- ✅ 모든 단계 완료
- ✅ 목표 개선율 달성 (기본 15%)
- ✅ 테스트 통과
- ✅ 보안 검사 통과

### 결과 파일 구조

```
evolution_results/
├── evolution_20250817_120000.json  # 전체 결과
├── metrics_comparison.csv          # 메트릭 비교
├── changes_log.txt                 # 변경 로그
└── patterns_learned.json           # 학습된 패턴
```

### 결과 내보내기

```bash
# JSON 형식
curl -X POST http://localhost:8000/api/context/export/{evolution_id}

# CSV 형식 (메트릭만)
python scripts/export_metrics.py --format csv --output metrics.csv
```

## 고급 설정

### 커스텀 Agent 추가

```python
from backend.packages.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, input_data):
        # 커스텀 로직
        result = await self.process(input_data)

        # SharedContext에 저장
        await self.context_store.store_custom_data(
            self.evolution_id,
            result
        )

        return result
```

### 진화 체인

여러 진화를 연속 실행:

```python
async def evolution_chain():
    targets = [
        "/project1",
        "/project2",
        "/project3"
    ]

    for target in targets:
        config = EvolutionConfig(target_path=target)
        result = await engine.evolve(config)

        if not result['success']:
            logger.error(f"Failed at {target}")
            break
```

### 조건부 진화

특정 조건에서만 진화:

```python
async def conditional_evolution():
    metrics = await analyze_current_metrics()

    if metrics['test_coverage'] < 70:
        config.focus_areas = [FocusArea.TESTING]
    elif metrics['docstring_coverage'] < 80:
        config.focus_areas = [FocusArea.DOCUMENTATION]
    else:
        logger.info("No evolution needed")
        return

    await engine.evolve(config)
```

## 트러블슈팅

### 일반적인 문제

#### 진화가 시작되지 않음

- 백엔드 서버 실행 확인
- 대상 경로 존재 확인
- 이미 진행 중인 진화 확인

#### 개선율이 낮음

- Focus areas 조정
- 더 구체적인 목표 설정
- 여러 사이클 실행

#### 메모리 부족

- 대상 프로젝트 크기 확인
- 리소스 제한 증가
- 파일 필터링 적용

### 디버깅

```bash
# 상세 로그 활성화
export LOG_LEVEL=DEBUG
python scripts/evolution/run_perfect_evolution.py

# 특정 Agent 디버그
export DEBUG_AGENT=PlannerAgent
```

## 베스트 프랙티스

1. **작은 프로젝트부터 시작**: 큰 프로젝트 전에 테스트
2. **드라이런 먼저**: 실제 변경 전 시뮬레이션
3. **백업 확인**: 진화 전 백업 생성
4. **메트릭 기준선 설정**: 진화 전 현재 상태 측정
5. **점진적 개선**: 한 번에 모든 것보다 단계별 개선
6. **학습 활용**: 이전 진화에서 학습된 패턴 재사용

---

**버전**: 2.0.0
**마지막 업데이트**: 2025-08-17
