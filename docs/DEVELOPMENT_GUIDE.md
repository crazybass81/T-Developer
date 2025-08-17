# 👨‍💻 T-Developer v2 개발 가이드

## 개요

이 가이드는 T-Developer v2 시스템을 개발하고 확장하는 방법을 설명합니다.

## 개발 환경 설정

### 필수 요구사항

- Python 3.9+
- Git
- AWS CLI (선택사항)
- Docker (선택사항)

### 초기 설정

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/t-developer-v2.git
cd t-developer-v2

# 2. 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 설정

# 5. 사전 커밋 훅 설정
pre-commit install
```

## 프로젝트 구조

```
T-DeveloperMVP/
├── backend/
│   ├── core/                 # 핵심 엔진
│   │   ├── evolution_engine.py
│   │   └── agent_manager.py
│   ├── packages/             # 모듈 패키지
│   │   ├── agents/          # Agent 구현
│   │   ├── shared_context.py # SharedContextStore
│   │   └── ...
│   ├── api/                 # API 라우트
│   │   └── routes/
│   ├── models/              # 데이터 모델
│   └── main.py             # 서버 진입점
├── scripts/                 # 유틸리티 스크립트
│   ├── evolution/          # 진화 실행
│   └── verification/       # 검증 도구
├── tests/                   # 테스트
├── docs/                    # 문서
└── frontend/               # UI (개발 중)
```

## 코딩 표준

### Python 스타일 가이드

**PEP 8 준수**:

```python
# 좋은 예
def calculate_metrics(
    data: List[Dict[str, Any]],
    threshold: float = 0.8
) -> Dict[str, float]:
    """Calculate metrics from data.

    Args:
        data: Input data list
        threshold: Minimum threshold value

    Returns:
        Dictionary of calculated metrics
    """
    pass

# 나쁜 예
def calc_metrics(d,t=0.8):
    # 메트릭 계산
    pass
```

**타입 힌트 필수**:

```python
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EvolutionResult:
    success: bool
    metrics: Dict[str, float]
    errors: Optional[List[str]] = None
```

**Docstring 형식 (Google Style)**:

```python
def complex_operation(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """Perform a complex operation.

    This function demonstrates proper documentation format
    with detailed explanations.

    Args:
        param1: The first parameter description
        param2: Optional second parameter

    Returns:
        A dictionary containing:
            - result: Operation result
            - metadata: Additional information

    Raises:
        ValueError: If param1 is invalid
        TimeoutError: If operation exceeds timeout

    Example:
        >>> result = complex_operation("test", 42)
        >>> print(result["result"])
    """
    pass
```

### 비동기 프로그래밍

**async/await 패턴**:

```python
import asyncio
from typing import List

async def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch data asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def process_multiple(urls: List[str]) -> List[Dict]:
    """Process multiple URLs concurrently."""
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

## Agent 개발

### 새 Agent 생성

1. **BaseAgent 상속**:

```python
# backend/packages/agents/custom_agent.py
from typing import Dict, Any
from packages.agents.base import BaseAgent, AgentInput, AgentOutput

class CustomAgent(BaseAgent):
    """Custom agent for specific task."""

    def __init__(self, name: str):
        super().__init__(name)
        self.context_store = get_context_store()  # 중요!

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute agent task."""
        try:
            # 1. 입력 검증
            self._validate_input(input_data)

            # 2. 처리 로직
            result = await self._process(input_data)

            # 3. SharedContext에 저장
            await self.context_store.store_custom_data(
                self.evolution_id,
                result
            )

            # 4. 결과 반환
            return AgentOutput(
                status="success",
                data=result,
                metrics=self._calculate_metrics(result)
            )

        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return AgentOutput(
                status="failed",
                error=str(e)
            )
```

2. **Agent 등록**:

```python
# backend/core/agent_manager.py
from packages.agents.custom_agent import CustomAgent

class AgentManager:
    def __init__(self):
        self.agents = {
            # 기존 agents...
            "custom": CustomAgent("custom_agent")
        }
```

3. **테스트 작성**:

```python
# tests/agents/test_custom_agent.py
import pytest
from packages.agents.custom_agent import CustomAgent

@pytest.mark.asyncio
async def test_custom_agent_execution():
    agent = CustomAgent("test")
    input_data = AgentInput(
        task_type="custom",
        parameters={"key": "value"}
    )

    result = await agent.execute(input_data)

    assert result.status == "success"
    assert "data" in result
```

## SharedContextStore 통합

### Context 저장

```python
# Agent 내에서 컨텍스트 저장
async def store_analysis_results(self):
    await self.context_store.store_original_analysis(
        evolution_id=self.evolution_id,
        files_analyzed=42,
        metrics={"coverage": 85},
        issues=[{"type": "missing_docstring", "count": 10}],
        improvements=[{"type": "add_types", "priority": "high"}]
    )
```

### Context 조회

```python
# 다른 Agent에서 컨텍스트 조회
async def get_previous_results(self):
    context = await self.context_store.get_context(self.evolution_id)

    # 이전 단계 데이터 사용
    original_metrics = context.original_analysis.get("metrics", {})
    planned_tasks = context.improvement_plan.get("tasks", [])
```

## API 엔드포인트 추가

### 새 라우트 생성

```python
# backend/api/routes/custom.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/custom", tags=["custom"])

class CustomRequest(BaseModel):
    param1: str
    param2: int = 10

@router.post("/process")
async def process_custom(request: CustomRequest):
    """Process custom request."""
    try:
        # 처리 로직
        result = await process_data(request.param1, request.param2)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status."""
    status = await get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status
```

### 라우트 등록

```python
# backend/main.py
from api.routes.custom import router as custom_router

app.include_router(custom_router)
```

## 테스트

### 단위 테스트

```python
# tests/test_shared_context.py
import pytest
from packages.shared_context import SharedContextStore

@pytest.fixture
async def context_store():
    store = SharedContextStore()
    await store.initialize()
    yield store
    await store.cleanup()

@pytest.mark.asyncio
async def test_context_creation(context_store):
    evolution_id = await context_store.create_context(
        target_path="/test",
        focus_areas=["test"]
    )

    assert evolution_id is not None
    assert len(evolution_id) == 36  # UUID length
```

### 통합 테스트

```python
# tests/integration/test_evolution_cycle.py
import pytest
from backend.core.evolution_engine import EvolutionEngine

@pytest.mark.asyncio
async def test_full_evolution_cycle():
    engine = EvolutionEngine()
    config = EvolutionConfig(
        target_path="/tmp/test_project",
        dry_run=True
    )

    result = await engine.evolve(config)

    assert result["success"] is True
    assert "phases_completed" in result
    assert result["phases_completed"] == 4
```

### 테스트 실행

```bash
# 모든 테스트
pytest

# 특정 테스트
pytest tests/test_shared_context.py

# 커버리지 포함
pytest --cov=backend --cov-report=html

# 병렬 실행
pytest -n auto
```

## 디버깅

### 로깅 설정

```python
import logging

# 로거 생성
logger = logging.getLogger(__name__)

# 로그 레벨 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 사용
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 디버거 사용

```python
# breakpoint() 사용 (Python 3.7+)
def complex_function():
    data = process_data()
    breakpoint()  # 여기서 중단
    return transform_data(data)

# pdb 사용
import pdb

def debug_function():
    pdb.set_trace()
    # 디버깅할 코드
```

### 프로파일링

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # 프로파일링할 코드
    result = expensive_operation()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 상위 10개
```

## 배포

### Docker 빌드

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY scripts/ ./scripts/

EXPOSE 8000

CMD ["python", "backend/main.py"]
```

```bash
# 빌드
docker build -t t-developer:v2 .

# 실행
docker run -p 8000:8000 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID t-developer:v2
```

### 환경별 설정

```python
# backend/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 환경별 설정
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

    # API 설정
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # AWS 설정
    aws_region: str = "us-east-1"

    # 리소스 제한
    max_memory_mb: int = 500 if environment == "development" else 2000
    max_cpu_percent: int = 80 if environment == "development" else 90

    class Config:
        env_file = ".env"

settings = Settings()
```

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest --cov=backend

    - name: Check code quality
      run: |
        black --check backend/
        mypy backend/

    - name: Security scan
      run: |
        semgrep --config=auto backend/
```

## 기여 가이드라인

### 브랜치 전략

```bash
# 기능 개발
git checkout -b feature/agent-improvement

# 버그 수정
git checkout -b fix/context-store-bug

# 문서 업데이트
git checkout -b docs/api-update
```

### 커밋 메시지

```bash
# 형식: type(scope): description

feat(agent): Add new CustomAgent for data processing
fix(context): Resolve race condition in SharedContextStore
docs(api): Update API documentation for v2
test(evolution): Add integration tests for evolution cycle
refactor(core): Simplify evolution engine logic
```

### Pull Request 체크리스트

- [ ] 테스트 추가/업데이트
- [ ] 문서 업데이트
- [ ] 타입 힌트 추가
- [ ] Docstring 작성
- [ ] 코드 포맷팅 (Black)
- [ ] 린트 통과 (mypy, flake8)
- [ ] 보안 검사 통과
- [ ] 성능 영향 평가

## 문제 해결

### 일반적인 이슈

**ImportError**:

```python
# sys.path 확인
import sys
sys.path.insert(0, '/path/to/backend')
```

**AsyncIO 경고**:

```python
# 이벤트 루프 정리
import asyncio

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
```

**메모리 누수**:

```python
# 객체 참조 확인
import gc
import objgraph

gc.collect()
objgraph.show_most_common_types(limit=10)
```

---

**버전**: 2.0.0
**마지막 업데이트**: 2025-08-17
