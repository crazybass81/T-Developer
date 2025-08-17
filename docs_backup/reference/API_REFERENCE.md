# API Reference

## REST API Endpoints

### Base URL

```
http://localhost:8000/api
```

### Authentication

```http
# Currently no authentication required for local development
# Production will use API keys
```

---

## Evolution Endpoints

### Start Evolution Cycle

```http
POST /api/evolution/start
```

**Request Body:**

```json
{
  "target_path": "./backend/packages",
  "max_cycles": 1,
  "focus_areas": ["documentation", "complexity", "type_hints"],
  "dry_run": false,
  "max_files": 10,
  "enable_code_modification": true
}
```

**Response:**

```json
{
  "status": {
    "status": "running",
    "current_cycle": 1,
    "max_cycles": 1,
    "evolution_id": "6e7cbcf9-487c-4903-a7e2-b1f8baa9c7d0"
  },
  "context_store": {
    "evolution_id": "6e7cbcf9-487c-4903-a7e2-b1f8baa9c7d0",
    "phases_completed": []
  }
}
```

### Get Evolution Status

```http
GET /api/evolution/status
```

**Response:**

```json
{
  "status": "completed",
  "current_cycle": 1,
  "results": [
    {
      "cycle_number": 1,
      "research_result": {
        "external_research": {
          "best_practices": ["Use type hints", "Add docstrings"],
          "references_found": 3
        },
        "internal_analysis": {
          "files_analyzed": 5,
          "issues_found": 8,
          "improvements": [
            {"type": "docstring", "count": 5, "priority": "high"},
            {"type": "complexity", "count": 3, "priority": "medium"}
          ]
        }
      },
      "plan_result": {
        "tasks": [
          {"id": "1", "type": "add_docstrings", "priority": "high"},
          {"id": "2", "type": "reduce_complexity", "priority": "medium"}
        ],
        "estimated_impact": 0.7
      },
      "implementation_result": {
        "files_modified": 3,
        "changes": [
          {"file": "agent.py", "change_type": "docstring_added", "status": "completed"}
        ]
      },
      "evaluation_result": {
        "quality_score": 85,
        "goals_achieved": ["improved_documentation", "reduced_complexity"],
        "metrics_improved": {
          "docstring_coverage": "+10%",
          "complexity": "-15%"
        }
      },
      "success": true
    }
  ],
  "shared_context": {
    "evolution_id": "6e7cbcf9-487c-4903-a7e2-b1f8baa9c7d0",
    "has_data": true
  }
}
```

### Stop Evolution

```http
POST /api/evolution/stop
```

**Request Body:**

```json
{
  "force": false,
  "reason": "Manual intervention required"
}
```

### List Evolution History

```http
GET /evolution/history
```

**Query Parameters:**

- `since`: ISO 8601 date
- `until`: ISO 8601 date
- `status`: "success" | "failed" | "in_progress"
- `limit`: number (default: 20)
- `offset`: number (default: 0)

---

## Agent Endpoints

### List Agents

```http
GET /agents
```

**Response:**

```json
{
  "agents": [
    {
      "id": "research-agent",
      "name": "Research Agent",
      "status": "active",
      "version": "2.0.1",
      "capabilities": ["code_analysis", "pattern_detection"],
      "health": "healthy"
    }
  ]
}
```

### Get Agent Details

```http
GET /agents/{agent_id}
```

### Execute Agent Task

```http
POST /agents/{agent_id}/execute
```

**Request Body:**

```json
{
  "task": {
    "intent": "research",
    "payload": {
      "target_path": "packages/agents",
      "focus_areas": ["documentation", "testing"]
    }
  },
  "timeout": 300,
  "async": true
}
```

### Get Agent Metrics

```http
GET /agents/{agent_id}/metrics
```

---

## Metrics Endpoints

### Get Current Metrics

```http
GET /metrics/current
```

**Response:**

```json
{
  "timestamp": "2024-01-15T12:00:00Z",
  "metrics": {
    "docstring_coverage": 78.5,
    "test_coverage": 85.2,
    "complexity_mi": 72.3,
    "security_score": 95,
    "technical_debt_hours": 45.5
  }
}
```

### Get Metrics History

```http
GET /metrics/history
```

**Query Parameters:**

- `metric`: Specific metric name
- `since`: ISO 8601 date
- `until`: ISO 8601 date
- `granularity`: "hour" | "day" | "week"

### Get Metrics Comparison

```http
GET /metrics/compare
```

**Query Parameters:**

- `baseline`: Git ref or date
- `target`: Git ref or date

---

## SharedContextStore Endpoints

### Get Current Context

```http
GET /api/context/current
```

**Response:**

```json
{
  "evolution_id": "6e7cbcf9-487c-4903-a7e2-b1f8baa9c7d0",
  "created_at": "2025-08-17T04:42:31.943328",
  "target_path": "/tmp/test_evolution",
  "focus_areas": ["documentation", "complexity", "type_hints"],
  "current_phase": "evaluation",
  "status": "completed",
  "has_data": {
    "original_analysis": true,
    "external_research": true,
    "improvement_plan": true,
    "implementation_log": true,
    "evaluation_results": true
  }
}
```

### Get Comparison Data

```http
GET /api/context/comparison/{evolution_id}
```

**Response:**

```json
{
  "before": {
    "files_analyzed": 5,
    "metrics": {"complexity": 3.5, "docstring_coverage": 45},
    "issues": [...]
  },
  "plan": {
    "tasks": [...],
    "estimated_impact": 0.7
  },
  "after": {
    "metrics": {"complexity": 2.8, "docstring_coverage": 75}
  },
  "implementation": {
    "modified_files": ["agent.py", "planner.py"],
    "total_changes": 8
  }
}
```

### Export Context

```http
POST /api/context/export/{evolution_id}
```

**Response:**

```json
{
  "export_path": "evolution_6e7cbcf9_20250817_044238.json",
  "size_bytes": 24576,
  "download_url": "/api/context/download/evolution_6e7cbcf9_20250817_044238.json"
}
```

### List All Contexts

```http
GET /api/context/list
```

**Response:**

```json
{
  "contexts": [
    {
      "evolution_id": "6e7cbcf9-487c-4903-a7e2-b1f8baa9c7d0",
      "created_at": "2025-08-17T04:42:31",
      "target_path": "/tmp/test_evolution",
      "status": "completed",
      "current_phase": "evaluation",
      "has_errors": false
    }
  ],
  "total": 1
}
```

---

## Planning Endpoints

### Create Execution Plan

```http
POST /planning/create
```

**Request Body:**

```json
{
  "insights": [
    {
      "type": "docstring",
      "severity": "medium",
      "location": "agents/research.py:45"
    }
  ],
  "constraints": {
    "max_hours_per_task": 4,
    "parallel_tasks": 3
  }
}
```

### Get Plan Details

```http
GET /planning/{plan_id}
```

### Execute Plan

```http
POST /planning/{plan_id}/execute
```

---

## Quality Gates Endpoints

### Run Quality Checks

```http
POST /quality/check
```

**Request Body:**

```json
{
  "target": "packages/agents",
  "checks": ["security", "complexity", "coverage", "documentation"]
}
```

### Get Gate Configuration

```http
GET /quality/gates
```

### Update Gate Thresholds

```http
PUT /quality/gates/{gate_name}
```

**Request Body:**

```json
{
  "threshold": 85,
  "enforcement": "blocking"
}
```

---

## Security Endpoints

### Run Security Scan

```http
POST /security/scan
```

**Request Body:**

```json
{
  "target": "packages/",
  "scan_types": ["secrets", "vulnerabilities", "dependencies"],
  "severity_threshold": "medium"
}
```

### Get Security Report

```http
GET /security/report/{scan_id}
```

---

## Learning Endpoints

### Get Patterns

```http
GET /learning/patterns
```

**Query Parameters:**

- `type`: Pattern type
- `success_rate_min`: Minimum success rate

### Add Pattern

```http
POST /learning/patterns
```

**Request Body:**

```json
{
  "pattern": {
    "type": "improvement",
    "context": {...},
    "action": {...},
    "outcome": {...},
    "success_rate": 0.92
  }
}
```

### Get Recommendations

```http
GET /learning/recommendations
```

**Query Parameters:**

- `context`: Current context
- `limit`: Number of recommendations

---

## Artifact Endpoints

### List Artifacts

```http
GET /artifacts
```

### Get Artifact

```http
GET /artifacts/{artifact_id}
```

### Download Artifact

```http
GET /artifacts/{artifact_id}/download
```

---

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.t-developer.your-domain.com/v1/ws');
```

### Authentication

```json
{
  "type": "auth",
  "token": "<bearer_token>"
}
```

### Subscribe to Events

```json
{
  "type": "subscribe",
  "events": ["evolution.started", "evolution.phase_complete", "agent.status"]
}
```

### Event Format

```json
{
  "event": "evolution.phase_complete",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "evolution_id": "evo_1234567890",
    "phase": "research",
    "results": {...}
  }
}
```

---

## Error Responses

### Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "cycles",
      "issue": "Must be between 1 and 10"
    }
  },
  "request_id": "req_abc123"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input |
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down |

---

## Rate Limits

| Endpoint Pattern | Limit | Window |
|-----------------|-------|---------|
| `/evolution/start` | 10 | 1 hour |
| `/agents/*/execute` | 100 | 1 hour |
| `/metrics/*` | 1000 | 1 hour |
| All others | 500 | 1 hour |

**Rate Limit Headers:**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Pagination

**Request:**

```http
GET /evolution/history?limit=20&offset=40
```

**Response Headers:**

```http
X-Total-Count: 150
X-Page-Count: 8
Link: </evolution/history?limit=20&offset=60>; rel="next",
      </evolution/history?limit=20&offset=20>; rel="prev"
```

---

## Versioning

The API uses URL versioning. The current version is `v1`.

**Deprecated Endpoint Response:**

```http
Sunset: Sat, 31 Dec 2024 23:59:59 GMT
Link: </v2/new-endpoint>; rel="successor-version"
```

---

## SDK Examples

### Python

```python
from t_developer import Client

client = Client(api_key="your_api_key")

# Start evolution
evolution = client.evolution.start(
    target="packages/agents",
    cycles=1
)

# Check status
status = client.evolution.get_status(evolution.id)
```

### JavaScript

```javascript
import { TDeveloperClient } from '@t-developer/sdk';

const client = new TDeveloperClient({ apiKey: 'your_api_key' });

// Start evolution
const evolution = await client.evolution.start({
  target: 'packages/agents',
  cycles: 1
});

// Check status
const status = await client.evolution.getStatus(evolution.id);
```

### CLI

```bash
# Using the t-dev CLI
t-dev evolution start --target packages/agents --cycles 1

# Check status
t-dev evolution status evo_1234567890

# Get metrics
t-dev metrics current --format json
```
