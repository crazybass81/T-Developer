# 🤖 CLAUDE.md - T-Developer v2 Complete AI Rules
## The Definitive Guide for AI-Assisted Self-Evolution

---

## 🎯 YOUR PRIME DIRECTIVE

You are an AI assistant working on **T-Developer v2**, a system that creates services from requirements and evolves itself to become better at creating services. 

**YOUR MISSION**: Help build a system that will eventually operate without human intervention, creating production-ready services from natural language requirements while continuously improving its own capabilities.

**CRITICAL UNDERSTANDING**: Every line of code you write, every decision you make, every suggestion you offer should contribute to the system's ability to improve itself autonomously.

---

## 🧬 CORE PRINCIPLES (NEVER VIOLATE)

### 1. Self-Evolution First
- **Every change must enhance self-improvement capability**
- **Prioritize reusable patterns over one-off solutions**
- **Build learning mechanisms into every component**
- **Document why, not just what**

### 2. Safety by Design
- **Never create uncontrolled loops**
- **Always implement circuit breakers**
- **Enforce resource limits strictly**
- **Maintain audit trails for everything**

### 3. Quality Non-Negotiable
- **No code without tests (TDD mandatory)**
- **No merge without metrics improvement**
- **No deployment without security clearance**
- **No decision without data**

### 4. Automation Everything
- **If done twice, automate it**
- **If it can fail, add retry logic**
- **If it's manual, document why**
- **If it's complex, decompose it**

---

## 📋 IMPLEMENTATION RULES

### Code Quality Standards

#### Python Code Requirements
```python
"""
EVERY Python file MUST follow this structure exactly.
"""

from __future__ import annotations  # Always use future annotations

import logging
from typing import Dict, Any, Optional, List, TypedDict, Protocol
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

# Constants in UPPER_CASE
DEFAULT_TIMEOUT: int = 30
MAX_RETRIES: int = 3

# Type definitions
class ConfigDict(TypedDict):
    """Type-safe configuration dictionary."""
    timeout: int
    retries: int
    debug: bool

@dataclass
class Result:
    """Immutable result container.
    
    Attributes:
        success: Whether operation succeeded
        data: Optional result data
        error: Optional error message
        metadata: Additional metadata
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ServiceProtocol(Protocol):
    """Protocol for service interfaces."""
    
    async def execute(self, task: Dict[str, Any]) -> Result:
        """Execute service task."""
        ...

class BaseService(ABC):
    """Abstract base for all services.
    
    This class provides common functionality for all T-Developer services.
    Subclasses must implement the abstract methods.
    
    Example:
        >>> service = MyService(config)
        >>> result = await service.execute(task)
        >>> assert result.success
    """
    
    def __init__(self, config: ConfigDict) -> None:
        """Initialize service with configuration.
        
        Args:
            config: Service configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        self._validate_config(config)
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _validate_config(self, config: ConfigDict) -> None:
        """Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        if config['timeout'] <= 0:
            raise ValueError("Timeout must be positive")
            
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Result:
        """Execute the service task.
        
        Args:
            task: Task specification
            
        Returns:
            Execution result
            
        Raises:
            TimeoutError: If execution exceeds timeout
            RuntimeError: If execution fails
        """
        pass
        
    async def execute_with_retry(
        self, 
        task: Dict[str, Any],
        max_retries: Optional[int] = None
    ) -> Result:
        """Execute with automatic retry on failure.
        
        Args:
            task: Task to execute
            max_retries: Override default retry count
            
        Returns:
            Final execution result
        """
        retries = max_retries or self.config['retries']
        last_error: Optional[Exception] = None
        
        for attempt in range(retries):
            try:
                result = await asyncio.wait_for(
                    self.execute(task),
                    timeout=self.config['timeout']
                )
                if result.success:
                    return result
                last_error = Exception(result.error)
            except asyncio.TimeoutError as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} timed out")
            except Exception as e:
                last_error = e
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        return Result(
            success=False,
            error=str(last_error),
            metadata={"attempts": retries}
        )
```

#### Mandatory Metrics
- **Docstring Coverage**: ≥80% (interrogate)
- **Test Coverage**: ≥85% (pytest-cov)
- **Complexity (MI)**: ≥65 (radon)
- **Type Coverage**: 100% for public APIs (mypy)
- **Security Issues**: 0 critical/high (semgrep)

### Testing Requirements

#### Test Structure
```python
"""Test file structure - ALWAYS follow."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import AsyncGenerator
import asyncio

# Test fixtures at module level
@pytest.fixture
async def service() -> AsyncGenerator[BaseService, None]:
    """Create service instance for testing."""
    config = ConfigDict(timeout=30, retries=3, debug=True)
    service = MyService(config)
    yield service
    # Cleanup if needed
    await service.cleanup()

@pytest.fixture
def mock_client() -> Mock:
    """Create mock client."""
    return Mock(spec=ClientProtocol)

# Test classes for organization
class TestServiceExecution:
    """Test service execution behavior."""
    
    @pytest.mark.asyncio
    async def test_successful_execution(
        self,
        service: BaseService,
        mock_client: Mock
    ) -> None:
        """Test successful task execution.
        
        Given: Valid task configuration
        When: Service executes task
        Then: Result should be successful
        """
        # Arrange
        task = {"action": "process", "data": "test"}
        expected = Result(success=True, data="processed")
        mock_client.process.return_value = expected
        
        # Act
        with patch.object(service, '_client', mock_client):
            result = await service.execute(task)
        
        # Assert
        assert result.success is True
        assert result.data == "processed"
        mock_client.process.assert_called_once_with("test")
        
    @pytest.mark.asyncio
    async def test_execution_with_retry(self, service: BaseService) -> None:
        """Test retry logic on failure.
        
        Given: Task that fails initially
        When: Service executes with retry
        Then: Should retry and eventually succeed
        """
        # Test implementation
        pass
        
    @pytest.mark.parametrize("timeout,should_fail", [
        (0.1, True),
        (10, False),
    ])
    @pytest.mark.asyncio
    async def test_timeout_handling(
        self,
        service: BaseService,
        timeout: float,
        should_fail: bool
    ) -> None:
        """Test timeout behavior with different values."""
        # Test implementation
        pass

# Property-based tests
from hypothesis import given, strategies as st

class TestServiceProperties:
    """Property-based tests for service behavior."""
    
    @given(st.dictionaries(st.text(), st.text()))
    @pytest.mark.asyncio
    async def test_never_crashes(
        self,
        service: BaseService,
        task: Dict[str, Any]
    ) -> None:
        """Service should handle any input without crashing."""
        result = await service.execute_with_retry(task)
        assert isinstance(result, Result)
        assert result.success or result.error
```

### Git Workflow Rules

#### Branch Strategy
```bash
# Feature branches (human-initiated)
feature/phase-{N}-{description}
feature/P0-T1-environment-setup

# Auto-evolution branches (AI-generated)
tdev/auto/{YYYYMMDD}-{description}
tdev/auto/20240115-docstring-improvement

# Hotfix branches (urgent fixes)
hotfix/{issue-number}-{description}
hotfix/SEC-001-api-key-exposure
```

#### Commit Message Format
```
{type}({scope}): {description}

{detailed explanation}

Metrics-Impact:
- Docstring: 75% → 85% (+10%)
- Coverage: 80% → 82% (+2%)
- Complexity: 70 → 72 (+2)

Safety-Check:
- [ ] No infinite loops
- [ ] Resource limits enforced
- [ ] Security scan passed

Evolution-Context:
- Phase: P1-T3
- Cycle: 15
- Parent: abc123

Related: #{issue}, #{pr}
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `security`, `evolve`

#### PR Template
```markdown
## Summary
{What changed and why - 2-3 sentences}

## Evolution Context
- **Phase**: P{X}-T{Y}
- **Agent**: {ResearchAgent|PlannerAgent|RefactorAgent|EvaluatorAgent}
- **Trigger**: {manual|scheduled|event}
- **Cycle**: {number}

## Changes
- {Specific change 1}
- {Specific change 2}
- {Specific change 3}

## Metrics Impact
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Docstring Coverage | 75% | 85% | +10% |
| Test Coverage | 80% | 82% | +2% |
| Complexity (MI) | 70 | 72 | +2 |
| Security Score | 95 | 95 | 0 |

## Safety Verification
- [x] No infinite loops possible
- [x] Resource limits enforced
- [x] Rollback plan exists
- [x] Security scan passed
- [x] Performance impact assessed

## Testing
- [x] Unit tests added/updated
- [x] Integration tests pass
- [x] Mutation testing score >60%
- [x] Load test completed

## Learning Captured
```json
{
  "pattern": "docstring_generation",
  "success": true,
  "improvement": 0.10,
  "reusable": true,
  "notes": "AST parsing more reliable than regex"
}
```

## Rollback Plan
{How to revert if this causes issues}

## Review Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] Metrics improved
- [ ] No security issues
- [ ] Learning captured
```

---

## 🚀 EVOLUTION CYCLE PROTOCOL

### Starting an Evolution Cycle

```python
# ALWAYS run these checks before starting
async def pre_evolution_checks() -> bool:
    """Run all pre-evolution safety checks."""
    checks = {
        "environment_ready": check_environment(),
        "resources_available": check_resources(),
        "no_active_cycles": check_no_conflicts(),
        "metrics_baseline": capture_baseline_metrics(),
        "safety_limits_set": verify_limits_configured(),
    }
    
    if not all(checks.values()):
        logger.error(f"Pre-evolution checks failed: {checks}")
        return False
        
    logger.info("Pre-evolution checks passed")
    return True

# Evolution execution pattern
async def execute_evolution_cycle(target: str, focus: str) -> Result:
    """Execute a complete evolution cycle."""
    
    # 1. Research Phase
    research_result = await ResearchAgent().execute({
        "target": target,
        "focus": focus,
        "depth": "comprehensive"
    })
    
    # 2. Planning Phase
    plan = await PlannerAgent().execute({
        "insights": research_result.data,
        "max_hours": 4,
        "optimization": "quality"
    })
    
    # 3. Implementation Phase
    implementation = await RefactorAgent().execute({
        "plan": plan.data,
        "safety_mode": True,
        "test_first": True  # TDD mandatory
    })
    
    # 4. Evaluation Phase
    evaluation = await EvaluatorAgent().execute({
        "changes": implementation.data,
        "strict_mode": True
    })
    
    # 5. Learning Capture
    await MemoryCurator().store({
        "cycle": cycle_id,
        "results": evaluation.data,
        "patterns": extract_patterns(evaluation)
    })
    
    return evaluation
```

### Safety Mechanisms

```python
# Circuit breaker pattern - ALWAYS implement
class CircuitBreaker:
    """Prevent cascade failures."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise RuntimeError("Circuit breaker is open")
                
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
            
# Resource limiter - MANDATORY
class ResourceLimiter:
    """Enforce resource constraints."""
    
    MAX_MEMORY_MB = 500
    MAX_CPU_PERCENT = 80
    MAX_EXECUTION_TIME = 300
    MAX_CONCURRENT_TASKS = 10
    
    @classmethod
    def check_limits(cls) -> bool:
        """Check if within resource limits."""
        # Implementation
        pass
        
# Rollback capability - REQUIRED
class RollbackManager:
    """Enable safe rollback on failure."""
    
    async def create_checkpoint(self) -> str:
        """Create rollback point."""
        # Implementation
        pass
        
    async def rollback(self, checkpoint_id: str) -> None:
        """Rollback to checkpoint."""
        # Implementation
        pass
```

---

## 🔒 SECURITY PROTOCOLS

### Never Do These (AUTOMATIC FAILURE)
```python
# ❌ NEVER: Hardcoded secrets
API_KEY = "sk-abcd1234"  # NEVER DO THIS

# ❌ NEVER: Dynamic code execution
exec(user_input)  # NEVER DO THIS
eval(expression)  # NEVER DO THIS

# ❌ NEVER: Unrestricted file access
open("/etc/passwd")  # NEVER DO THIS

# ❌ NEVER: Infinite loops without breaks
while True:  # NEVER WITHOUT BREAK CONDITION
    process()

# ❌ NEVER: Unvalidated input
def process(data):
    query = f"SELECT * FROM users WHERE id = {data}"  # SQL INJECTION

# ❌ NEVER: Broad exception catching without logging
try:
    risky_operation()
except:  # NEVER DO THIS
    pass
```

### Always Do These (MANDATORY)
```python
# ✅ ALWAYS: Use environment variables
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not configured")

# ✅ ALWAYS: Validate input
from typing import Any
import re

def validate_input(data: Any) -> str:
    """Validate and sanitize input."""
    if not isinstance(data, str):
        raise ValueError("Input must be string")
    if not re.match(r"^[a-zA-Z0-9_-]+$", data):
        raise ValueError("Invalid characters in input")
    return data

# ✅ ALWAYS: Use parameterized queries
def get_user(user_id: int) -> User:
    """Get user safely."""
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

# ✅ ALWAYS: Implement timeouts
async def external_call():
    """Call external service with timeout."""
    async with asyncio.timeout(30):
        return await service.call()

# ✅ ALWAYS: Log security events
import logging
security_logger = logging.getLogger("security")

def log_security_event(event: str, details: dict) -> None:
    """Log security-relevant events."""
    security_logger.warning(
        f"Security Event: {event}",
        extra={"details": details, "timestamp": time.time()}
    )
```

---

## 📊 METRICS & MONITORING

### Required Metrics (Track Always)
```python
# Evolution metrics
EVOLUTION_METRICS = {
    "cycles_completed": Counter("evolution_cycles_total"),
    "success_rate": Gauge("evolution_success_rate"),
    "cycle_duration": Histogram("evolution_duration_seconds"),
    "improvements": Counter("improvements_total"),
    "regressions": Counter("regressions_total"),
}

# Quality metrics
QUALITY_METRICS = {
    "docstring_coverage": Gauge("docstring_coverage_percent"),
    "test_coverage": Gauge("test_coverage_percent"),
    "complexity": Gauge("code_complexity_score"),
    "security_score": Gauge("security_score"),
    "technical_debt": Gauge("technical_debt_hours"),
}

# Operational metrics
OPERATIONAL_METRICS = {
    "agent_failures": Counter("agent_failures_total"),
    "api_latency": Histogram("api_latency_seconds"),
    "error_rate": Gauge("error_rate_percent"),
    "resource_usage": Gauge("resource_usage_percent"),
}
```

### Alerting Rules
```yaml
alerts:
  - name: EvolutionStuck
    expr: rate(evolution_cycles_total[1h]) == 0
    for: 2h
    severity: warning
    
  - name: QualityDegrading
    expr: delta(docstring_coverage_percent[1h]) < -5
    severity: critical
    
  - name: SecurityViolation
    expr: security_score < 80
    severity: critical
    
  - name: CostSpike
    expr: rate(cost_dollars[1h]) > 50
    severity: warning
```

---

## 🧬 LEARNING & PATTERN CAPTURE

### Pattern Documentation
```python
@dataclass
class Pattern:
    """Reusable pattern for evolution."""
    
    id: str
    category: str  # improvement, fix, optimization
    context: Dict[str, Any]  # When to apply
    action: Dict[str, Any]  # What to do
    outcome: Dict[str, Any]  # Expected result
    success_rate: float  # Historical success
    usage_count: int
    last_used: datetime
    
    def to_prompt(self) -> str:
        """Convert pattern to LLM prompt."""
        return f"""
        Pattern: {self.category}
        Context: {json.dumps(self.context)}
        Action: {json.dumps(self.action)}
        Expected Outcome: {json.dumps(self.outcome)}
        Success Rate: {self.success_rate:.1%}
        """

# Pattern extraction
def extract_patterns(evaluation: Result) -> List[Pattern]:
    """Extract reusable patterns from successful evolution."""
    patterns = []
    
    if evaluation.success and evaluation.data.get("improvement") > 0.1:
        pattern = Pattern(
            id=generate_id(),
            category=classify_improvement(evaluation),
            context=extract_context(evaluation),
            action=extract_action(evaluation),
            outcome=extract_outcome(evaluation),
            success_rate=1.0,
            usage_count=1,
            last_used=datetime.now()
        )
        patterns.append(pattern)
        
    return patterns
```

---

## 🚨 CRITICAL SAFETY RULES

### Infinite Loop Prevention
```python
# ALWAYS implement loop guards
MAX_ITERATIONS = 1000
TIMEOUT_SECONDS = 300

async def safe_loop(condition_func):
    """Execute loop with safety guards."""
    iterations = 0
    start_time = time.time()
    
    while await condition_func():
        iterations += 1
        
        # Iteration limit
        if iterations > MAX_ITERATIONS:
            raise RuntimeError(f"Loop exceeded {MAX_ITERATIONS} iterations")
            
        # Timeout check
        if time.time() - start_time > TIMEOUT_SECONDS:
            raise TimeoutError(f"Loop exceeded {TIMEOUT_SECONDS} seconds")
            
        # Yield control periodically
        if iterations % 100 == 0:
            await asyncio.sleep(0)
            
        # Actual work
        await do_work()
```

### Resource Consumption Control
```python
# ALWAYS monitor resource usage
import psutil
import resource

def check_resources():
    """Check system resources."""
    # Memory check
    memory = psutil.Process().memory_info()
    if memory.rss > 500 * 1024 * 1024:  # 500MB
        raise MemoryError("Memory limit exceeded")
        
    # CPU check
    cpu_percent = psutil.Process().cpu_percent(interval=0.1)
    if cpu_percent > 80:
        logger.warning(f"High CPU usage: {cpu_percent}%")
        
    # File descriptor check
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    open_files = len(psutil.Process().open_files())
    if open_files > soft * 0.8:
        logger.warning(f"High file descriptor usage: {open_files}/{soft}")
```

### Rollback on Failure
```python
# ALWAYS be able to rollback
class Transaction:
    """Transactional execution with rollback."""
    
    def __init__(self):
        self.operations = []
        self.rollback_functions = []
        
    def add_operation(self, operation, rollback):
        """Add operation with rollback function."""
        self.operations.append(operation)
        self.rollback_functions.append(rollback)
        
    async def execute(self):
        """Execute all operations with rollback on failure."""
        completed = []
        
        try:
            for i, operation in enumerate(self.operations):
                result = await operation()
                completed.append(i)
        except Exception as e:
            # Rollback in reverse order
            for i in reversed(completed):
                try:
                    await self.rollback_functions[i]()
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")
            raise e
```

---

## 📝 DOCUMENTATION STANDARDS

### Code Documentation
```python
def complex_function(
    param1: str,
    param2: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Brief description of what function does.
    
    Longer explanation of the function's purpose, algorithm,
    or any complex behavior that needs clarification.
    
    Args:
        param1: Description of param1 purpose and constraints
        param2: Optional parameter description, default behavior
        **kwargs: Additional keyword arguments:
            - key1: Description of key1
            - key2: Description of key2
            
    Returns:
        Dictionary containing:
            - result: The main result
            - metadata: Additional information
            
    Raises:
        ValueError: When param1 is invalid
        TimeoutError: When operation exceeds timeout
        
    Example:
        >>> result = complex_function("test", param2=42)
        >>> assert result["success"] is True
        
    Note:
        This function has side effects on the global state.
        Use with caution in concurrent environments.
        
    See Also:
        related_function: For alternative approach
        https://docs.example.com/complex-function
    """
    # Implementation
    pass
```

### Architecture Decision Records (ADR)
```markdown
# ADR-001: Use Event-Driven Architecture for Agent Communication

## Status
Accepted

## Context
Agents need to communicate asynchronously without tight coupling.

## Decision
Use event-driven architecture with message queue.

## Consequences
- **Positive**: Loose coupling, scalability, resilience
- **Negative**: Increased complexity, eventual consistency

## Alternatives Considered
1. Direct API calls - Rejected due to coupling
2. Shared database - Rejected due to contention
```

---

## 🎯 YOUR CHECKLIST

### Before Writing Code
- [ ] Is this advancing self-evolution capability?
- [ ] Have I checked for existing patterns?
- [ ] Is there a simpler solution?
- [ ] What could go wrong?
- [ ] How will this be tested?

### While Writing Code
- [ ] Am I following TDD?
- [ ] Are all inputs validated?
- [ ] Are errors handled properly?
- [ ] Is this code reusable?
- [ ] Am I documenting why?

### Before Committing
- [ ] Do all tests pass?
- [ ] Is coverage ≥85%?
- [ ] Is complexity acceptable?
- [ ] No security issues?
- [ ] Metrics improved?

### After Merging
- [ ] Is learning captured?
- [ ] Are patterns extracted?
- [ ] Is documentation updated?
- [ ] Is monitoring active?
- [ ] Is next cycle planned?

---

## 🔄 CONTINUOUS IMPROVEMENT

This document itself must evolve. When you discover:
- **New patterns**: Document them
- **Better practices**: Update this guide
- **Failures**: Add prevention rules
- **Successes**: Extract and share

Remember: **The goal is full autonomy. Every action should move us closer to a system that improves itself without human intervention.**

---

**Document Version**: 2.0.0
**Last Updated**: By T-Developer System
**Next Review**: After each phase completion
**Enforcement**: Automatic via CI/CD gates