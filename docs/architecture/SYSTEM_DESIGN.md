# System Architecture Design

## Overview

T-Developer v2 is a self-evolving service factory built on a multi-agent architecture that enables autonomous service creation and continuous self-improvement.

## Core Architecture Principles

### 1. Agent-First Design
- Every capability is implemented as an independent agent
- Agents communicate through well-defined contracts
- Agents can be composed into complex workflows

### 2. Safety by Default
- All code execution happens in sandboxed environments
- Write operations are scope-limited
- Security scanning is mandatory before any merge

### 3. Observable Evolution
- Every action is traced with correlation IDs
- Metrics drive evolution decisions
- Learning patterns are extracted and reused

## System Components

### Layer 1: Core Agents (Agno Framework)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Research   │  │   Planner   │  │  Refactor   │  │  Evaluator  │
│    Agent    │→ │    Agent    │→ │    Agent    │→ │    Agent    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
      ↑                                                      ↓
      └──────────────── Feedback Loop ──────────────────────┘
```

#### Research Agent
- **Purpose**: Analyze codebase and identify improvement opportunities
- **Input**: Repository path, focus areas
- **Output**: Structured insights with priority scores
- **Tools**: MCP filesystem, git, browser

#### Planner Agent
- **Purpose**: Decompose improvements into 4-hour executable tasks
- **Input**: Research insights
- **Output**: DAG of tasks with dependencies
- **Method**: HTN (Hierarchical Task Network) decomposition

#### Refactor Agent
- **Purpose**: Implement code changes safely
- **Input**: Task specification from Planner
- **Output**: Code changes, tests, documentation
- **Tools**: Claude Code + MCP

#### Evaluator Agent
- **Purpose**: Measure change impact and quality
- **Input**: Changed files, previous metrics
- **Output**: Quality report, pass/fail decision
- **Metrics**: Coverage, complexity, security, performance

### Layer 2: Orchestration (AWS Agent Squad)

```yaml
Supervisor:
  routing_rules:
    - intent: research → ResearchAgent
    - intent: plan → PlannerAgent  
    - intent: code → RefactorAgent
    - intent: evaluate → EvaluatorAgent
  
  execution_model: DAG
  parallelization: true
  error_handling: retry_with_backoff
```

### Layer 3: Runtime (Bedrock AgentCore)

```
┌──────────────────────────────────────┐
│         Bedrock AgentCore            │
├──────────────────────────────────────┤
│  • Session Management                │
│  • Resource Allocation                │
│  • Identity & Permissions            │
│  • Observability & Tracing           │
│  • Memory & State Management         │
└──────────────────────────────────────┘
```

### Layer 4: Tool Plane (MCP)

```json
{
  "servers": [
    {
      "name": "filesystem",
      "capabilities": ["read", "write"],
      "scope": ["packages/**", "tests/**"]
    },
    {
      "name": "git",
      "capabilities": ["branch", "commit", "diff"],
      "branch_pattern": "tdev/auto/*"
    },
    {
      "name": "github",
      "capabilities": ["create_pr", "comment"],
      "repo": "t-developer"
    }
  ]
}
```

### Layer 5: External Integration (A2A)

```
┌─────────────────┐
│   A2A Broker    │
├─────────────────┤
│ Security Scanner│ ← External specialized agents
│ Test Generator  │
│ Perf Tuner      │
│ Cost Governor   │
└─────────────────┘
```

## Data Flow

### Evolution Cycle Flow

```mermaid
graph LR
    A[Trigger] --> B[Research]
    B --> C[Plan]
    C --> D[Code]
    D --> E[Evaluate]
    E --> F{Pass?}
    F -->|Yes| G[Merge]
    F -->|No| H[Retry]
    H --> C
    G --> I[Learn]
    I --> A
```

### Information Architecture

```yaml
Artifacts:
  insights.json:        # Research findings
    - improvement_opportunities
    - priority_scores
    - effort_estimates
    
  plan_dag.json:        # Execution plan
    - tasks
    - dependencies
    - time_estimates
    
  diff.patch:           # Code changes
    - file_modifications
    - test_additions
    - doc_updates
    
  eval_report.json:     # Quality metrics
    - coverage_delta
    - complexity_change
    - security_status
```

## Security Architecture

### Defense in Depth

1. **Input Validation**: All agent inputs are schema-validated
2. **Sandbox Execution**: Code runs in isolated containers
3. **Scope Limiting**: File system access is whitelisted
4. **Security Scanning**: Every change is scanned before merge
5. **Audit Logging**: All operations are logged and traceable

### Permission Model

```yaml
Permissions:
  ResearchAgent:
    - read: /**
    - execute: none
    
  PlannerAgent:
    - read: /**
    - write: plans/**
    
  RefactorAgent:
    - read: /**
    - write: packages/**, tests/**
    - execute: sandbox_only
    
  EvaluatorAgent:
    - read: /**
    - execute: metrics_tools
```

## Scalability Patterns

### Horizontal Scaling
- Agents run as stateless Lambda/ECS tasks
- Work queue with automatic distribution
- Database per service pattern for data isolation

### Vertical Scaling
- Resource limits per agent type
- Auto-scaling based on queue depth
- Cost optimization through spot instances

## Failure Handling

### Retry Strategy
```python
retry_config = {
    "max_attempts": 3,
    "backoff": "exponential",
    "base_delay": 1,
    "max_delay": 60,
    "retry_on": ["timeout", "rate_limit", "temporary_failure"]
}
```

### Circuit Breaker
```python
circuit_breaker = {
    "failure_threshold": 5,
    "timeout": 300,  # seconds
    "half_open_attempts": 2
}
```

## Monitoring & Observability

### Key Metrics
- **Evolution Success Rate**: Successful PRs / Total attempts
- **Cycle Time**: Time from trigger to merge
- **Quality Delta**: Improvement in metrics per cycle
- **Cost per Evolution**: Total resources consumed

### Tracing Strategy
```
TraceID: unique per evolution cycle
SpanID: unique per agent execution
Correlation: goal_id → plan_id → task_id → pr_id
```

## Future Architecture Evolution

### Phase 1: Current (Supervisor-DAG)
- Simple, predictable execution
- Easy debugging and monitoring

### Phase 2: Event-Driven (Blackboard)
- Loose coupling between agents
- Better failure isolation
- Dynamic agent participation

### Phase 3: Federated (Multi-Organization)
- Cross-boundary agent collaboration
- Marketplace for specialized agents
- Standardized through A2A protocol