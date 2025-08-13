# 🧪 T-Developer Complete Testing Guide

## 📋 Overview

Comprehensive testing guide for the AI Autonomous Evolution System, covering unit, integration, evolution, and performance testing.

## 🎯 Testing Strategy

### Test Pyramid
```
         /\
        /E2E\        5%  - End-to-end tests
       /------\
      /Integr. \    15%  - Integration tests  
     /----------\
    / Evolution  \  20%  - Evolution safety tests
   /--------------\
  /   Unit Tests   \ 60%  - Unit tests
 /------------------\
```

### Coverage Requirements
- **Overall**: ≥ 87%
- **Unit Tests**: ≥ 80%
- **Integration**: 100% of APIs
- **Evolution**: 100% safety validation
- **Performance**: All constraints validated

## 🔧 Test Structure

### Directory Organization
```
tests/
├── unit/                 # Unit tests
│   ├── agents/          # Agent-specific tests
│   ├── evolution/       # Evolution engine tests
│   └── core/           # Core functionality
├── integration/         # Integration tests
│   ├── api/            # API endpoint tests
│   ├── workflow/       # Workflow tests
│   └── database/       # Database tests
├── evolution/          # Evolution-specific tests
│   ├── safety/         # Safety validation
│   ├── fitness/        # Fitness evaluation
│   └── constraints/    # Constraint validation
├── e2e/               # End-to-end tests
├── performance/       # Performance tests
└── fixtures/          # Test data and mocks
```

## 📝 Unit Testing

### Agent Testing Template
```python
import pytest
from unittest.mock import Mock, patch

class TestAgent:
    """Test template for agents"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return MyAgent()
    
    def test_memory_constraint(self, agent):
        """Test agent stays within 6.5KB"""
        import sys
        size = sys.getsizeof(agent)
        assert size <= 6656  # 6.5KB in bytes
    
    def test_instantiation_speed(self, agent):
        """Test agent instantiates in < 3μs"""
        import time
        start = time.perf_counter()
        new_agent = MyAgent()
        duration = (time.perf_counter() - start) * 1_000_000
        assert duration < 3.0  # microseconds
    
    def test_evolution_capability(self, agent):
        """Test agent can evolve"""
        assert hasattr(agent, 'evolve')
        assert agent.evolution_enabled == True
```

### Testing Best Practices
1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies
3. **Fixtures**: Use pytest fixtures for setup
4. **Parametrization**: Test multiple scenarios
5. **Assertions**: Clear, specific assertions

## 🔄 Integration Testing

### API Testing
```python
import pytest
from fastapi.testclient import TestClient

class TestAPI:
    @pytest.fixture
    def client(self):
        from src.main import app
        return TestClient(app)
    
    def test_evolution_endpoint(self, client):
        response = client.post("/api/v1/evolution/start")
        assert response.status_code == 200
        assert response.json()["status"] == "evolving"
    
    def test_agent_pipeline(self, client):
        """Test complete agent pipeline"""
        payload = {"query": "Create todo app"}
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 200
        assert "download_url" in response.json()
```

### Database Testing
```python
@pytest.mark.asyncio
async def test_agent_persistence():
    """Test agent state persistence"""
    async with get_db() as db:
        agent = await create_agent(db, agent_data)
        assert agent.id is not None
        
        retrieved = await get_agent(db, agent.id)
        assert retrieved.fitness_score == agent.fitness_score
```

## 🧬 Evolution Testing

### Safety Validation
```python
class TestEvolutionSafety:
    def test_memory_violation_rollback(self):
        """Test rollback on memory violation"""
        engine = EvolutionEngine()
        bad_genome = create_oversized_genome()  # > 6.5KB
        
        result = engine.evolve(bad_genome)
        assert result.rolled_back == True
        assert result.reason == "memory_violation"
    
    def test_malicious_pattern_detection(self):
        """Test detection of malicious evolution"""
        safety = EvolutionSafety()
        malicious_genome = create_malicious_genome()
        
        is_safe = safety.validate(malicious_genome)
        assert is_safe == False
    
    def test_fitness_regression_prevention(self):
        """Test prevention of fitness regression"""
        engine = EvolutionEngine()
        current_fitness = 0.95
        
        new_genome = engine.evolve(current_genome)
        assert new_genome.fitness >= current_fitness * 0.98
```

### Constraint Testing
```python
@pytest.mark.parametrize("memory_kb", [5.0, 6.0, 6.5])
def test_memory_constraints(memory_kb):
    """Test various memory constraints"""
    agent = create_agent_with_memory(memory_kb)
    assert agent.validate_constraints() == True

@pytest.mark.parametrize("speed_us", [2.0, 2.5, 3.0])
def test_speed_constraints(speed_us):
    """Test various speed constraints"""
    agent = create_agent_with_speed(speed_us)
    assert agent.validate_constraints() == True
```

## ⚡ Performance Testing

### Load Testing
```python
import asyncio
import time

async def test_parallel_agents():
    """Test 10,000 parallel agents"""
    agents = []
    start = time.time()
    
    # Create 10,000 agents
    for _ in range(10000):
        agents.append(create_agent())
    
    # Run all agents in parallel
    results = await asyncio.gather(*[
        agent.process() for agent in agents
    ])
    
    duration = time.time() - start
    assert len(results) == 10000
    assert duration < 30  # Should complete in 30 seconds
```

### Benchmark Testing
```python
def test_evolution_benchmark():
    """Benchmark evolution performance"""
    engine = EvolutionEngine()
    generations = []
    
    for gen in range(10):
        start = time.perf_counter()
        new_gen = engine.evolve_generation()
        duration = time.perf_counter() - start
        
        generations.append({
            'generation': gen,
            'fitness': new_gen.average_fitness,
            'duration': duration
        })
        
        # Each generation should improve
        if gen > 0:
            assert new_gen.average_fitness > generations[gen-1]['fitness']
```

## 🔍 End-to-End Testing

### Complete Workflow Test
```python
@pytest.mark.e2e
async def test_complete_evolution_cycle():
    """Test complete evolution cycle"""
    # 1. Initialize system
    system = EvolutionSystem()
    await system.initialize()
    
    # 2. Create initial population
    population = await system.create_population(size=100)
    assert len(population) == 100
    
    # 3. Run evolution
    for generation in range(5):
        population = await system.evolve(population)
        assert population.average_fitness > 0.9
        assert population.best_agent.memory_kb <= 6.5
        assert population.best_agent.speed_us <= 3.0
    
    # 4. Deploy best agent
    deployed = await system.deploy(population.best_agent)
    assert deployed.status == "active"
    
    # 5. Verify performance
    metrics = await deployed.get_metrics()
    assert metrics.success_rate > 0.95
```

## 🛠️ Test Commands

### Running Tests
```bash
# All tests
pytest

# Specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/evolution/

# With coverage
pytest --cov=src --cov-report=html

# Parallel execution
pytest -n auto

# Verbose output
pytest -v

# Specific test file
pytest tests/unit/test_agents.py

# Specific test function
pytest tests/unit/test_agents.py::test_memory_constraint
```

### Test Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=87
markers =
    unit: Unit tests
    integration: Integration tests
    evolution: Evolution tests
    e2e: End-to-end tests
    slow: Slow tests
```

## 📊 Test Metrics

### Current Coverage
| Component | Coverage | Target |
|-----------|----------|--------|
| Agents | 92% | 80% |
| Evolution | 88% | 85% |
| API | 95% | 90% |
| Core | 91% | 85% |
| **Overall** | **87%** | **87%** |

### Test Execution Time
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds
- Evolution tests: < 1 minute
- E2E tests: < 5 minutes
- **Total**: < 7 minutes

## 🔧 Continuous Testing

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Unit Tests
        entry: pytest tests/unit/ -x
        language: system
        pass_filenames: false
        always_run: true
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pytest --cov=src --cov-fail-under=87
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📝 Test Documentation

### Writing Test Cases
1. **Given**: Initial state/setup
2. **When**: Action being tested
3. **Then**: Expected outcome

### Test Naming Convention
```python
def test_<what>_<condition>_<expected_result>():
    """
    Test that <what> <does something> when <condition>.
    """
    pass

# Examples:
def test_agent_memory_under_limit_passes_validation():
def test_evolution_fitness_regression_triggers_rollback():
def test_api_invalid_input_returns_400():
```

## 🚨 Troubleshooting

### Common Issues
1. **Memory Test Failures**: Check agent initialization
2. **Speed Test Failures**: Profile with cProfile
3. **Evolution Test Failures**: Verify constraints
4. **Integration Test Failures**: Check service dependencies

### Debug Commands
```bash
# Run with debugging
pytest --pdb

# Show print statements
pytest -s

# Run failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "evolution"

# Profile test performance
pytest --profile
```

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-01  
**Test Framework**: Pytest 7.x
