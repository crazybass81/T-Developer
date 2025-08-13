# ⚠️ Agent Size Constraint Violations

## Critical Issue
All agents MUST be under 6.5KB (6656 bytes) to meet the T-Developer architecture constraints.

## Current Violations (2025-08-13)

| Agent | Current Size | Required Reduction | Priority |
|-------|-------------|-------------------|----------|
| unified/generation/agent.py | 66.83KB | -60.33KB | CRITICAL |
| unified/nl_input/agent.py | 49.84KB | -43.34KB | CRITICAL |
| unified/parser/agent.py | 37.89KB | -31.39KB | CRITICAL |
| unified/component_decision/agent.py | 33.54KB | -27.04KB | CRITICAL |
| unified/assembly/agent.py | 30.66KB | -24.16KB | CRITICAL |
| unified/ui_selection/agent.py | 27.65KB | -21.15KB | CRITICAL |
| unified/match_rate/agent.py | 23.59KB | -17.09KB | CRITICAL |
| unified/search/agent.py | 22.68KB | -16.18KB | CRITICAL |
| unified/base/unified_base_agent.py | 18.78KB | -12.28KB | CRITICAL |
| unified/download/agent.py | 16.04KB | -9.54KB | CRITICAL |
| data_transformer/agent.py | 13.81KB | -7.31KB | CRITICAL |

## Required Actions

### 1. Immediate Refactoring Needed
- Split large agents into micro-services
- Remove all docstrings and comments
- Use minimal variable names
- Extract shared code to base classes
- Move non-essential logic to modules

### 2. Architecture Pattern
```python
# CORRECT: Under 6.5KB
class MiniAgent:
    def __init__(self):
        self.m = __import__('modules.core')
    def e(self, d):  # execute
        return self.m.process(d)
```

### 3. Modularization Strategy
- Core agent: < 6.5KB (loader/router only)
- Modules: Separate files for actual logic
- Dynamic imports: Load modules on demand
- Shared utilities: Common base classes

## Compliance Status
❌ **0/11 agents compliant** (0% compliance)

## Impact
- **CI/CD**: Builds will fail until fixed
- **Production**: Cannot deploy oversized agents
- **Evolution**: Violates core architecture constraint

## Resolution Timeline
- **Immediate**: Document issue ✅
- **Day 13**: Refactor all agents to compliance
- **Day 14**: Verify all agents < 6.5KB
- **Day 15**: Update CI/CD checks

---
*This is a blocking issue that must be resolved before proceeding with evolution system.*
