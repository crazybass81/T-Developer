# T-Developer Testing Guide

## 🧪 Testing Strategy

### Test Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Integration across agents
    │                 │
    ├─────────────────┤
    │ Integration     │  ← Agent interactions
    │ Tests           │
    ├─────────────────┤
    │   Unit Tests    │  ← Individual components
    │                 │
    └─────────────────┘
```

## 🔧 Test Setup

### Prerequisites
```bash
# Install test dependencies
uv pip install pytest pytest-asyncio pytest-mock

# Install development tools
uv pip install black flake8 mypy
```

### Environment Configuration
```bash
# Test environment variables
export NODE_ENV=test
export AWS_REGION=us-east-1
export DYNAMODB_ENDPOINT=http://localhost:8000
```

## 🤖 Agent Testing

### Unit Tests
```python
# Example: NL Input Agent test
import pytest
from agents.nl_input_agent import NLInputAgent

@pytest.mark.asyncio
async def test_nl_input_processing():
    agent = NLInputAgent()
    result = await agent.process_description(
        "Build a React todo app with authentication"
    )
    
    assert result.project_type == "web_application"
    assert "authentication" in result.technical_requirements
    assert len(result.functional_requirements) > 0
```

### Integration Tests
```python
# Example: Agent collaboration test
@pytest.mark.asyncio
async def test_agent_workflow():
    # NL Input → Parser → Component Decision
    nl_agent = NLInputAgent()
    parser_agent = ParserAgent()
    decision_agent = ComponentDecisionAgent()
    
    # Process requirements
    requirements = await nl_agent.process_description(test_input)
    parsed = await parser_agent.parse_requirements(requirements)
    decisions = await decision_agent.make_decisions(parsed)
    
    assert decisions.architecture_pattern is not None
    assert len(decisions.component_selections) > 0
```

## 📊 Performance Testing

### Load Testing
```python
import asyncio
import time

async def test_agent_performance():
    """Test agent instantiation speed (target: <3μs)"""
    start = time.perf_counter_ns()
    agent = NLInputAgent()
    end = time.perf_counter_ns()
    
    instantiation_time_us = (end - start) / 1000
    assert instantiation_time_us < 3.0  # 3μs target
```

### Memory Testing
```python
import psutil
import os

def test_agent_memory_usage():
    """Test memory usage per agent (target: <6.5KB)"""
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss
    
    agents = [NLInputAgent() for _ in range(1000)]
    
    memory_after = process.memory_info().rss
    memory_per_agent_kb = (memory_after - memory_before) / 1000 / 1024
    
    assert memory_per_agent_kb < 6.5  # 6.5KB target
```

## 🔍 Test Categories

### 1. Unit Tests (`tests/unit/`)
- Individual agent methods
- Utility functions
- Data models
- Validation logic

### 2. Integration Tests (`tests/integration/`)
- Agent-to-agent communication
- Database interactions
- External API calls
- Template rendering

### 3. End-to-End Tests (`tests/e2e/`)
- Complete user workflows
- Multi-agent orchestration
- Performance benchmarks
- Error scenarios

## 🚀 Running Tests

### All Tests
```bash
# Run complete test suite
pytest

# With coverage
pytest --cov=backend/src --cov-report=html
```

### Specific Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/ -m performance
```

### Agent-Specific Tests
```bash
# Test specific agent
pytest tests/agents/test_nl_input_agent.py

# Test with verbose output
pytest tests/agents/ -v
```

## 📋 Test Checklist

### Before Committing
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Code coverage > 80%
- [ ] No linting errors
- [ ] Type checking passes

### Before Deployment
- [ ] E2E tests pass
- [ ] Performance benchmarks met
- [ ] Load testing completed
- [ ] Security tests pass
- [ ] Documentation updated

## 🐛 Debugging Tests

### Common Issues
1. **Async/Await Problems**
   ```python
   # Wrong
   def test_async_function():
       result = agent.async_method()
   
   # Correct
   @pytest.mark.asyncio
   async def test_async_function():
       result = await agent.async_method()
   ```

2. **Mock Configuration**
   ```python
   @pytest.fixture
   def mock_bedrock():
       with patch('boto3.client') as mock:
           yield mock
   ```

3. **Environment Variables**
   ```python
   @pytest.fixture(autouse=True)
   def setup_test_env(monkeypatch):
       monkeypatch.setenv("NODE_ENV", "test")
   ```

## 📈 Test Metrics

### Coverage Targets
- Unit Tests: >90%
- Integration Tests: >80%
- E2E Tests: >70%
- Overall: >85%

### Performance Targets
- Agent instantiation: <3μs
- Memory per agent: <6.5KB
- Response time: <200ms
- Concurrent agents: 10,000+