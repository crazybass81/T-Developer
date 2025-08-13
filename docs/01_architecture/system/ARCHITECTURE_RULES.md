# 🏛️ Architecture Rules & Guidelines

> **Note**: This document consolidates all architecture rules previously in `.amazonq/rules/`

## 🧬 AI Autonomous Evolution System Rules

### Core Architecture Principles
1. **AI Autonomy**: 85% of system decisions made by AI
2. **Memory Constraint**: 6.5KB maximum per agent
3. **Speed Target**: 3μs instantiation time
4. **Safety First**: 100% malicious pattern prevention
5. **Evolution Rate**: 5% improvement per generation

### System Architecture Documents
- [**Evolution Architecture**](00-evolution-architecture.md) - Core evolution system design
- [**System Architecture**](architecture.md) - Overall system architecture
- [**Folder Structure**](folder-structure.md) - Project organization
- [**Backend Structure**](backend-structure.md) - Backend architecture

## 🎯 Mandatory Rules

### 1. Python-Only Backend
- NO TypeScript in backend
- NO JavaScript in core logic
- Use UV package manager (not pip)
- Python 3.11+ required

### 2. Agent Constraints
```python
class AgentRules:
    MAX_MEMORY_KB = 6.5
    MAX_INSTANTIATION_US = 3.0
    MIN_FITNESS_SCORE = 0.95
    EVOLUTION_ENABLED = True
```

### 3. Framework Requirements
- **Agno Framework**: Ultra-lightweight agent creation
- **AWS Bedrock AgentCore**: Serverless runtime
- **Agent Squad**: Multi-agent orchestration

### 4. Security Requirements
- All AI outputs must be validated
- Evolution patterns must be monitored
- Rollback capability required
- Checkpoint system mandatory

### 5. Documentation Requirements
- All code must have docstrings
- Complex logic needs Korean comments
- Architecture decisions in ADR format
- Changes must update relevant docs

## 📁 Project Structure Rules

### Folder Organization
```
/docs                 # All documentation
  /00_planning       # Strategic plans
  /01_architecture   # Technical architecture
  /02_implementation # Development guides
  /03_api           # API documentation
  /04_testing       # Test documentation
  /05_operations    # Operations & security

/backend            # Python-only backend
  /src              # Source code
  /tests            # Test suites
  /migrations       # Database migrations
```

### Naming Conventions
- Python files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Agents: `{function}_agent.py`

## 🚫 Forbidden Practices

### Never Do
- ❌ Mock implementations in production
- ❌ Hardcoded credentials
- ❌ TypeScript in backend
- ❌ Synchronous evolution operations
- ❌ Unvalidated AI outputs
- ❌ Direct database access in agents
- ❌ Global mutable state

### Always Do
- ✅ Real implementations only
- ✅ Environment variables for config
- ✅ Python-only backend
- ✅ Async evolution operations
- ✅ Validate all AI outputs
- ✅ Use repository pattern
- ✅ Immutable state management

## 🔄 Evolution Rules

### Genetic Algorithm Requirements
1. Fitness evaluation must be multi-dimensional
2. Selection must preserve diversity
3. Mutation rate: 5-30% (adaptive)
4. Crossover must maintain constraints
5. Elite preservation: top 10%

### Safety Framework
```python
EVOLUTION_SAFETY_RULES = {
    "max_memory_kb": 6.5,
    "max_instantiation_us": 3.0,
    "min_safety_score": 1.0,
    "rollback_on_regression": True,
    "checkpoint_interval": 5  # generations
}
```

## 📊 Performance Rules

### Metrics Requirements
- Agent memory: < 6.5KB
- Instantiation: < 3μs
- API response: < 1s
- Evolution cycle: < 30s
- Parallel agents: 10,000+

### Monitoring Requirements
- Real-time performance tracking
- Evolution metrics dashboard
- Cost tracking per operation
- Security event monitoring
- Automatic alerting

## 🎭 Development Workflow Rules

### Git Workflow
1. Branch from `main` or `feature/T-Orchestrator`
2. Prefix: `feat/`, `fix/`, `docs/`, `refactor/`
3. Commit with conventional commits
4. Push immediately after meaningful changes
5. No force push to main branches

### Testing Requirements
- Unit tests: > 80% coverage
- Integration tests: All API endpoints
- Evolution tests: Safety validation
- Performance tests: Constraint validation
- Security tests: Injection prevention

## 🔐 Security Rules

### AI Security
1. Prompt injection defense required
2. Output validation mandatory
3. PII detection and masking
4. Rate limiting on all endpoints
5. Audit logging for all operations

### Evolution Security
1. Pattern analysis before deployment
2. Rollback capability required
3. Checkpoint validation
4. Safety score must be 100%
5. Manual override capability

---

**Remember**: These rules are non-negotiable. Any deviation requires explicit documentation and approval.