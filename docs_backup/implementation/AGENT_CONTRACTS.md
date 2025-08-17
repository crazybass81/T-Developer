# Agent Contracts & Interfaces

## Core Agent Interface

All agents MUST implement this base interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    OK = "ok"
    RETRY = "retry"
    FAIL = "fail"

@dataclass
class AgentInput:
    """Standard input for all agents."""
    intent: str  # "research", "plan", "code", "evaluate"
    task_id: str  # Unique identifier for idempotency
    payload: Dict[str, Any]  # Task-specific data
    context: Optional[Dict[str, Any]] = None  # Repo, branch, user, etc.
    constraints: Optional[Dict[str, Any]] = None  # Time, cost, quality limits

@dataclass
class AgentOutput:
    """Standard output from all agents."""
    task_id: str
    status: AgentStatus
    artifacts: List['Artifact'] = None
    metrics: Dict[str, float] = None
    events: List['Event'] = None
    next_tasks: List[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class Artifact:
    """Represents a produced artifact."""
    kind: str  # "diff", "file", "report", "pr", "metric"
    ref: str  # Path or URL
    content: Optional[Any] = None
    metadata: Dict[str, Any] = None

@dataclass
class Event:
    """Event for async communication."""
    type: str  # e.g., "code.patch.ready"
    key: str  # Deduplication key
    data: Any
    visibility: str = "internal"  # "internal" or "a2a"

class BaseAgent(ABC):
    """Base class for all T-Developer agents."""

    @abstractmethod
    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute the agent's primary task."""
        pass

    @abstractmethod
    async def validate(self, output: AgentOutput) -> bool:
        """Validate the agent's output."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for discovery."""
        pass
```

## Research Agent Contract

```python
class ResearchAgentInput:
    """Research-specific input for EXTERNAL research."""
    query: str  # What to research (e.g., "best practices for documentation")
    scope: str = "external"  # Always external for ResearchAgent
    focus_areas: List[str] = ["documentation", "testing", "complexity"]

class ResearchAgentOutput:
    """Research-specific output."""
    best_practices: List[str]  # External best practices found
    references: List[Reference]  # External resources
    patterns: List[Pattern]  # Design patterns discovered
    trends: List[str]  # Current industry trends

    # Stored in SharedContextStore.external_research

@dataclass
class Reference:
    """External reference found."""
    url: str
    title: str
    relevance: float  # 0-1 score
    summary: str

@dataclass
class Pattern:
    """Design pattern found."""
    name: str
    description: str
    applicability: float  # 0-1 score
    example: Optional[str]
```

## CodeAnalysis Agent Contract (NEW)

```python
class CodeAnalysisAgentInput:
    """Code analysis-specific input for INTERNAL analysis."""
    target_path: str  # Repository or directory to analyze
    focus_areas: List[str] = ["documentation", "complexity", "type_hints"]
    max_files: int = 10  # Limit files to scan
    enable_deep_analysis: bool = True

class CodeAnalysisAgentOutput:
    """Code analysis-specific output."""
    files_analyzed: int
    metrics: Dict[str, Any]  # complexity, coverage, etc.
    issues: List[Issue]  # Code smells, antipatterns
    improvements: List[Improvement]  # Specific improvements needed
    patterns: List[str]  # Patterns found in code

    # Stored in SharedContextStore.original_analysis

@dataclass
class Issue:
    """Code issue found."""
    type: str  # "code_smell", "antipattern", "security"
    location: str  # file:line
    severity: str  # "low", "medium", "high"
    description: str

@dataclass
class Improvement:
    """Specific improvement needed."""
    type: str  # "docstring", "type_hints", "complexity"
    location: str  # file:line
    priority: str  # "high", "medium", "low"
    description: str
    estimated_hours: float
    priority_score: float  # 0.0 to 1.0
    tags: List[str] = None
```

## Planner Agent Contract

```python
class PlannerAgentInput:
    """Planner-specific input from SharedContextStore."""
    external_research: Dict[str, Any]  # From SharedContextStore.external_research
    internal_analysis: Dict[str, Any]  # From SharedContextStore.original_analysis
    focus_areas: List[str]  # Areas to focus on
    max_tasks: int = 5  # Maximum number of tasks to create
    constraints: Dict[str, Any] = None  # Resource, time constraints

class PlannerAgentOutput:
    """Planner-specific output."""
    tasks: List[Task]  # Tasks created from actual improvements
    priority_order: List[str]  # Task IDs in priority order
    estimated_impact: float  # 0-1 score of expected improvement
    total_hours: float  # Total estimated hours

    # Stored in SharedContextStore.improvement_plan

@dataclass
class ExecutionPlan:
    """Hierarchical execution plan."""
    id: str
    tasks: List[Task]
    dependencies: Dict[str, List[str]]  # task_id -> [dependency_ids]
    dag: Dict[str, Any]  # DAG representation
    metadata: Dict[str, Any]

@dataclass
class Task:
    """Single executable task."""
    id: str
    type: str  # "code", "test", "document", "refactor"
    description: str
    estimated_hours: float
    priority: int  # 1-10
    assigned_agent: str  # Which agent will execute
    input_artifacts: List[str]  # Required artifacts
    output_artifacts: List[str]  # Expected outputs
    success_criteria: Dict[str, Any]
    retry_policy: Dict[str, Any] = None
```

## Refactor Agent Contract

```python
class RefactorAgentInput:
    """Refactor-specific input."""
    tasks: List[Task]  # From SharedContextStore.improvement_plan
    target_path: str  # Project path
    enable_modification: bool = False  # Actually modify files
    use_bedrock: bool = True  # Use AWS Bedrock for modifications
    use_external_tools: bool = True  # Use Black, autopep8, etc.

class RefactorAgentOutput:
    """Refactor-specific output."""
    modified_files: List[str]  # Paths of modified files
    changes: List[Change]  # List of changes made
    rollback_points: List[RollbackPoint]  # For reverting if needed
    total_changes: int

    # Stored in SharedContextStore.implementation_log

@dataclass
class Change:
    """Single change made."""
    file: str
    change_type: str  # "docstring_added", "complexity_reduced", etc.
    description: str
    status: str  # "completed", "failed", "skipped"

@dataclass
class ChangedFile:
    """Represents a modified file."""
    path: str
    diff: str  # Unified diff format
    change_summary: str
    lines_added: int
    lines_removed: int

@dataclass
class DiffStats:
    """Statistics about changes."""
    files_changed: int
    insertions: int
    deletions: int
    test_coverage_delta: float
    complexity_delta: float
```

## Evaluator Agent Contract

```python
class EvaluatorAgentInput:
    """Evaluator-specific input with 3-way comparison."""
    comparison_data: Dict[str, Any]  # From SharedContextStore.get_comparison_data()
    # Contains: before (original_analysis), plan (improvement_plan), after (current state)
    changes: List[Change]  # From implementation_log
    target_path: str
    criteria: List[str] = ["quality", "security", "performance"]

class EvaluatorAgentOutput:
    """Evaluator-specific output."""
    metrics: Dict[str, Metric]
    passed: bool
    score: float  # Overall score 0-100
    report: EvaluationReport
    recommendations: List[str]

@dataclass
class Metric:
    """Single metric measurement."""
    name: str
    value: float
    previous_value: float
    delta: float
    delta_percent: float
    threshold: Optional[float]
    passed: bool

@dataclass
class EvaluationReport:
    """Comprehensive evaluation report."""
    summary: str
    metrics_table: Dict[str, Dict[str, Any]]
    failed_checks: List[str]
    warnings: List[str]
    improvements: List[str]
    regression_risk: str  # "low", "medium", "high"
```

## MCP Tool Contracts

```python
@dataclass
class ToolCall:
    """Request to execute a tool via MCP."""
    tool: str  # "fs", "git", "github", "browser", "tracker"
    action: str  # Tool-specific action
    args: Dict[str, Any]
    timeout: Optional[int] = 30
    retry_on_failure: bool = True

@dataclass
class ToolResponse:
    """Response from MCP tool execution."""
    tool: str
    action: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration_ms: int

# Filesystem Tool
class FileSystemTool:
    actions = ["read", "write", "list", "delete", "move", "copy"]
    scope = ["packages/**", "tests/**", "scripts/**"]

# Git Tool
class GitTool:
    actions = ["branch", "commit", "diff", "status", "log", "checkout"]
    branch_pattern = "tdev/auto/*"

# GitHub Tool
class GitHubTool:
    actions = ["create_pr", "comment_pr", "list_issues", "get_pr_status"]
    permissions = ["pull_request:write", "issues:read"]
```

## A2A External Agent Contracts

```python
@dataclass
class A2ARequest:
    """Request to external A2A agent."""
    agent_id: str
    capability: str  # Must be in agent's capability list
    payload: Dict[str, Any]
    timeout: int = 300
    callback_url: Optional[str] = None

@dataclass
class A2AResponse:
    """Response from external A2A agent."""
    agent_id: str
    request_id: str
    status: str  # "success", "failure", "timeout"
    result: Any
    metadata: Dict[str, Any]
    billing: Optional[Dict[str, float]] = None

# Security Scanner Agent
class SecurityScannerContract:
    capabilities = ["scan", "review", "fix_suggestions"]
    input_schema = {
        "files": "List[str]",
        "scan_type": "str",  # "full", "incremental", "secrets"
        "severity_threshold": "str"  # "low", "medium", "high", "critical"
    }
    output_schema = {
        "vulnerabilities": "List[Vulnerability]",
        "passed": "bool",
        "fix_suggestions": "List[FixSuggestion]"
    }

# Test Generator Agent
class TestGeneratorContract:
    capabilities = ["generate_unit", "generate_integration", "generate_property"]
    input_schema = {
        "target_files": "List[str]",
        "test_type": "str",
        "coverage_target": "float"
    }
    output_schema = {
        "test_files": "List[str]",
        "coverage_achieved": "float",
        "test_count": "int"
    }
```

## Event Bus Contracts (Future)

```python
@dataclass
class EventSubscription:
    """Subscription to event bus."""
    agent_id: str
    event_patterns: List[str]  # Glob patterns like "code.*"
    filter: Optional[Dict[str, Any]] = None
    handler: str  # Method to call

@dataclass
class EventPublication:
    """Publishing to event bus."""
    event: Event
    target_agents: Optional[List[str]] = None  # None = broadcast
    priority: int = 5  # 1-10
    ttl: int = 3600  # Seconds

# Common Events
EVENTS = {
    "research.complete": {"insights": "List[Insight]"},
    "plan.ready": {"plan": "ExecutionPlan"},
    "code.changed": {"files": "List[str]", "pr_url": "str"},
    "evaluation.complete": {"passed": "bool", "metrics": "Dict"},
    "security.alert": {"severity": "str", "details": "Dict"},
    "test.generated": {"test_files": "List[str]", "coverage": "float"}
}
```

## Validation Rules

All agents MUST:

1. Validate input against schema before processing
2. Return valid output conforming to contract
3. Handle errors gracefully with proper status codes
4. Emit events for significant state changes
5. Respect timeout and retry configurations
6. Log all operations with trace IDs
7. Report metrics for monitoring

## Version Compatibility

```python
CONTRACT_VERSION = "2.0.0"

def check_compatibility(agent_version: str, contract_version: str) -> bool:
    """Check if agent is compatible with contract version."""
    # Semantic versioning rules
    # Major version must match
    # Minor version can be higher
    # Patch version ignored
    pass
```
