# T-Developer 테스트 구조 가이드

## 📋 개요
T-Developer는 Python 기반의 9개 핵심 에이전트를 가진 멀티 에이전트 시스템입니다.

## 🏗️ 테스트 구조

### 표준화된 테스트 디렉토리
```
backend/
├── src/
│   └── agents/
│       └── implementations/
│           ├── nl_input/
│           │   └── tests/
│           │       └── test_nl_input_agent.py
│           ├── ui_selection/
│           │   └── tests/
│           │       └── test_ui_selection_agent.py
│           ├── parser/
│           │   └── tests/
│           │       └── test_parser_agent.py
│           ├── component_decision/
│           │   └── tests/
│           ├── match_rate/
│           │   └── tests/
│           │       └── test_match_rate_agent.py
│           ├── search/
│           │   └── tests/
│           ├── generation/
│           │   └── tests/
│           │       └── test_generation_agent.py
│           ├── assembly/
│           │   └── tests/
│           └── download/
│               └── tests/
├── tests/                           # 중앙 테스트 디렉토리
│   ├── integration/                 # 통합 테스트
│   │   └── test_nl_to_parser_workflow.py
│   ├── e2e/                         # End-to-End 테스트
│   │   └── test_complete_workflow.py
│   └── conftest.py                  # pytest 설정
├── pytest.ini                      # pytest 구성
├── requirements.txt                 # Python 의존성
└── main.py                         # FastAPI 엔트리포인트
```

## 🧪 테스트 실행

### 전체 테스트
```bash
cd backend
pytest
```

### 단위 테스트만
```bash
pytest src/agents/implementations/*/tests/
```

### 통합 테스트만
```bash
pytest tests/integration/
```

### E2E 테스트만
```bash
pytest tests/e2e/ -m e2e
```

## 📋 테스트 작성 규칙

### 파일명 규칙
- **단위 테스트**: `test_{agent_name}_agent.py`
- **통합 테스트**: `test_{workflow_name}.py`
- **E2E 테스트**: `test_{scenario_name}.py`

### 테스트 클래스명
```python
class TestNLInputAgent:
    """NL Input Agent 단위 테스트"""
    pass
```

### 비동기 테스트
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## 🔧 의존성 관리
- **uv** 사용 (pip 대신)
- **Python 3.11+** 필수
- **pytest-asyncio** 비동기 테스트용

---
**업데이트**: 2024년 12월  
**언어**: Python 통일  
**상태**: 활성