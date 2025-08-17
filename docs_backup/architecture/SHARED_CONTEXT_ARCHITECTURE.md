# SharedContextStore Architecture

## Overview

SharedContextStore is the centralized data management system for T-Developer's evolution process. It eliminates data duplication, enables parallel agent execution, and provides comprehensive context for intelligent decision-making.

## Core Design Principles

### 1. Single Source of Truth

- All evolution data stored in one place
- No agent maintains private state
- Complete audit trail of all phases

### 2. Phase-Based Organization

- Data organized by evolution phases
- Clear separation of concerns
- Easy to track progress

### 3. Context Preservation

- Full history maintained
- Three-way comparison enabled
- Learning from past evolutions

## Architecture Components

```
┌────────────────────────────────────────────────────────────┐
│                    SharedContextStore                        │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              EvolutionContext                        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  evolution_id: str         # Unique identifier       │   │
│  │  created_at: datetime      # Creation timestamp      │   │
│  │  target_path: str          # Project being evolved   │   │
│  │  focus_areas: List[str]    # Areas of focus         │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Phase Data Storage                          │   │   │
│  │  ├──────────────────────────────────────────────┤   │   │
│  │  │  original_analysis: Dict   # Before state    │   │   │
│  │  │  external_research: Dict   # Best practices  │   │   │
│  │  │  improvement_plan: Dict    # Tasks to do     │   │   │
│  │  │  implementation_log: Dict  # What was done   │   │   │
│  │  │  evaluation_results: Dict  # Success metrics │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  status: str              # Current status           │   │
│  │  current_phase: str       # Active phase            │   │
│  │  error_log: List[str]     # Any errors             │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## Data Flow Through Phases

### Phase 1: Research (Parallel Execution)

```python
# Two agents run in parallel
async def research_phase():
    # ResearchAgent → external_research
    await store.store_external_research(
        best_practices=["Use type hints", "Add docstrings"],
        references=[{"url": "...", "title": "..."}],
        patterns=[{"name": "Factory", "applicability": 0.8}]
    )

    # CodeAnalysisAgent → original_analysis
    await store.store_original_analysis(
        files_analyzed=10,
        metrics={"complexity": 3.5, "coverage": 75},
        issues=[{"type": "code_smell", "location": "file:42"}],
        improvements=[{"type": "docstring", "priority": "high"}]
    )
```

### Phase 2: Planning (Context-Aware)

```python
# PlannerAgent reads both research results
async def planning_phase():
    context = await store.get_context()

    # Use actual improvements from analysis
    improvements = context.original_analysis["improvements"]
    best_practices = context.external_research["best_practices"]

    # Create targeted tasks
    tasks = create_tasks_from_improvements(improvements, best_practices)

    # Store plan
    await store.store_improvement_plan(
        tasks=tasks,
        priorities=["task-1", "task-2"],
        dependencies={},
        estimated_impact=0.7
    )
```

### Phase 3: Implementation

```python
# RefactorAgent executes plan
async def implementation_phase():
    context = await store.get_context()
    tasks = context.improvement_plan["tasks"]

    # Execute with external services
    changes = await execute_with_bedrock(tasks)

    # Store implementation details
    await store.store_implementation_log(
        modified_files=["agent.py", "planner.py"],
        changes=[{"file": "agent.py", "type": "docstring_added"}],
        rollback_points=[{"id": "checkpoint-1", "timestamp": "..."}]
    )
```

### Phase 4: Evaluation (Three-Way Comparison)

```python
# EvaluatorAgent compares all states
async def evaluation_phase():
    # Get comprehensive comparison data
    comparison = await store.get_comparison_data()

    # Three-way comparison
    before = comparison["before"]      # original_analysis
    plan = comparison["plan"]          # improvement_plan
    after = comparison["after"]        # current state
    implementation = comparison["implementation"]  # what was done

    # Evaluate goal achievement
    goals_achieved = evaluate_goals(before, plan, after)

    # Store results
    await store.store_evaluation_results(
        goals_achieved=goals_achieved,
        metrics_comparison={
            "before": before["metrics"],
            "after": current_metrics,
            "delta": calculate_delta(before, after)
        },
        success_rate=0.85
    )
```

## Key Methods

### Core Operations

```python
class SharedContextStore:
    # Lifecycle
    async def create_context(target_path, focus_areas) -> str
    async def get_context(evolution_id=None) -> EvolutionContext
    async def update_phase(phase, evolution_id=None) -> bool

    # Phase-specific storage
    async def store_original_analysis(...)
    async def store_external_research(...)
    async def store_improvement_plan(...)
    async def store_implementation_log(...)
    async def store_evaluation_results(...)

    # Comparison & Analysis
    async def get_comparison_data() -> Dict[str, Any]
    async def get_all_contexts() -> List[Dict]

    # Export & Import
    async def export_context(evolution_id) -> str
    async def import_context(file_path) -> str
```

## Benefits

### 1. **Eliminates Duplication**

- No need for agents to pass data directly
- Central storage prevents data inconsistency
- Single point for data updates

### 2. **Enables Parallelism**

- Research and CodeAnalysis run simultaneously
- No blocking between phases
- Faster evolution cycles (50% reduction)

### 3. **Improves Intelligence**

- PlannerAgent creates tasks from real issues
- EvaluatorAgent performs comprehensive comparison
- Learning system has complete context

### 4. **Simplifies Debugging**

- Complete audit trail
- Easy to reproduce issues
- Export/import for testing

## Usage Example

```python
from backend.packages.shared_context import get_context_store
from backend.evolution_engine import EvolutionEngine, EvolutionConfig

# Initialize
engine = EvolutionEngine()
store = get_context_store()

# Run evolution
config = EvolutionConfig(
    target_path="./my-project",
    focus_areas=["documentation", "complexity"]
)
results = await engine.run_evolution(config)

# Access context
context = await store.get_context()
print(f"Evolution ID: {context.evolution_id}")
print(f"Files analyzed: {context.original_analysis['files_analyzed']}")
print(f"Tasks created: {len(context.improvement_plan['tasks'])}")
print(f"Goals achieved: {context.evaluation_results['goals_achieved']}")

# Export for analysis
export_path = await store.export_context()
print(f"Context exported to: {export_path}")
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Memory per context | ~10KB | Compressed JSON |
| Max contexts | 1000 | Configurable |
| Access time | <1ms | In-memory |
| Persistence | Optional | File/DB backend |
| Concurrency | Safe | AsyncIO locks |

## Future Enhancements

### Near-term (v2.1)

- [ ] Redis backend for distributed systems
- [ ] Context compression for large evolutions
- [ ] Real-time streaming of context updates
- [ ] GraphQL API for flexible queries

### Long-term (v3.0)

- [ ] Machine learning on context patterns
- [ ] Automatic context pruning
- [ ] Multi-tenant isolation
- [ ] Time-travel debugging

## Configuration

```python
# Environment variables
CONTEXT_STORE_BACKEND=memory  # memory|redis|dynamodb
CONTEXT_STORE_MAX_SIZE=1000
CONTEXT_STORE_TTL=86400  # 24 hours
CONTEXT_STORE_COMPRESSION=true

# Programmatic
store = SharedContextStore(
    backend="memory",
    max_contexts=1000,
    enable_compression=True,
    export_path="./contexts"
)
```

## Monitoring

Key metrics to track:

- Context creation rate
- Average context size
- Phase transition times
- Comparison query frequency
- Export/import operations

## Security Considerations

1. **Access Control**: Future versions will implement RBAC
2. **Data Encryption**: Sensitive data encrypted at rest
3. **Audit Logging**: All operations logged
4. **Input Validation**: All data validated before storage
5. **Resource Limits**: Maximum size and count enforced

---

**Version**: 1.0.0
**Last Updated**: 2025-08-17
**Status**: Production Ready
