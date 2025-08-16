# API Reference

## REST API Endpoints

### Base URL
```
https://api.t-developer.your-domain.com/v1
```

### Authentication
```http
Authorization: Bearer <token>
X-API-Key: <api-key>
```

---

## Evolution Endpoints

### Start Evolution Cycle
```http
POST /evolution/start
```

**Request Body:**
```json
{
  "target": "packages/agents",
  "cycles": 1,
  "focus": "quality",
  "constraints": {
    "max_hours": 4,
    "max_cost": 10,
    "quality_threshold": 0.85
  }
}
```

**Response:**
```json
{
  "evolution_id": "evo_1234567890",
  "status": "started",
  "estimated_completion": "2024-01-15T14:30:00Z",
  "tracking_url": "/evolution/status/evo_1234567890"
}
```

### Get Evolution Status
```http
GET /evolution/status/{evolution_id}
```

**Response:**
```json
{
  "evolution_id": "evo_1234567890",
  "status": "in_progress",
  "phase": "planning",
  "progress": 45,
  "phases_completed": ["research"],
  "current_metrics": {
    "docstring_coverage": 75.5,
    "test_coverage": 82.3,
    "complexity": 68.2
  },
  "artifacts": [
    {
      "type": "insights",
      "url": "/artifacts/insights_1234.json"
    }
  ]
}
```

### Stop Evolution
```http
POST /evolution/stop/{evolution_id}
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