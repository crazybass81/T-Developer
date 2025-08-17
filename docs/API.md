# T-Developer API Documentation

## Overview

T-Developer provides a comprehensive REST API for managing code evolution, agents, and metrics. All API endpoints require authentication via API key.

## Base URL

```
Production: https://api.t-developer.io
Development: http://localhost:8000/api
```

## Authentication

Include your API key in the request headers:

```http
X-API-Key: your-api-key-here
```

## Endpoints

### Evolution API

#### Start Evolution

Start a new evolution cycle for code improvement.

**Endpoint:** `POST /evolution/start`

**Request Body:**

```json
{
  "target_path": "/backend/packages",
  "max_cycles": 10,
  "min_improvement": 0.05,
  "safety_checks": true,
  "dry_run": false,
  "auto_mode": false,
  "config": {
    "focus_areas": ["documentation", "testing", "performance"]
  }
}
```

**Response:**

```json
{
  "evolution_id": "evo-20250817120000-abc123",
  "status": "running",
  "message": "Evolution cycle started successfully",
  "created_at": "2025-08-17T12:00:00Z",
  "metadata": {
    "execution_arn": "arn:aws:states:...",
    "target_path": "/backend/packages"
  }
}
```

#### Get Evolution Status

Retrieve the current status of an evolution cycle.

**Endpoint:** `GET /evolution/{evolution_id}`

**Response:**

```json
{
  "evolution_id": "evo-20250817120000-abc123",
  "status": "running",
  "target_path": "/backend/packages",
  "current_cycle": 3,
  "max_cycles": 10,
  "improvements": {
    "docstring": 15.5,
    "coverage": 8.2,
    "complexity": -5.3,
    "security": 2.1
  },
  "created_at": "2025-08-17T12:00:00Z",
  "updated_at": "2025-08-17T12:15:00Z"
}
```

#### Stop Evolution

Stop a running evolution cycle.

**Endpoint:** `POST /evolution/stop`

**Request Body:**

```json
{
  "evolution_id": "evo-20250817120000-abc123"
}
```

**Response:**

```json
{
  "evolution_id": "evo-20250817120000-abc123",
  "status": "stopped",
  "message": "Evolution stopped successfully"
}
```

### Agents API

#### List Agents

Get a list of all agents.

**Endpoint:** `GET /agents`

**Query Parameters:**

- `type` (optional): Filter by agent type (research, planner, refactor, evaluator)

**Response:**

```json
[
  {
    "agent_id": "agent-uuid-123",
    "name": "ResearchAgent",
    "type": "research",
    "status": "idle",
    "enabled": true,
    "metrics": {
      "total_executions": 100,
      "successful_executions": 95,
      "failed_executions": 5,
      "avg_execution_time": 2.5,
      "last_execution": "2025-08-17T11:30:00Z"
    }
  }
]
```

#### Create Agent

Create a new agent instance.

**Endpoint:** `POST /agents/create`

**Request Body:**

```json
{
  "name": "CustomAgent",
  "type": "research",
  "config": {
    "timeout": 300,
    "max_retries": 3,
    "custom_param": "value"
  },
  "enabled": true
}
```

**Response:**

```json
{
  "agent_id": "agent-uuid-456",
  "name": "CustomAgent",
  "type": "research",
  "status": "created",
  "message": "Agent CustomAgent created successfully"
}
```

#### Execute Agent

Execute a task with a specific agent.

**Endpoint:** `POST /agents/execute`

**Request Body:**

```json
{
  "agent_id": "agent-uuid-123",
  "task": {
    "action": "analyze",
    "target": "/backend/packages/agents/base.py",
    "parameters": {
      "depth": "comprehensive",
      "include_metrics": true
    }
  }
}
```

**Response:**

```json
{
  "execution_id": "exec-20250817120000-xyz789",
  "agent_id": "agent-uuid-123",
  "status": "queued",
  "message": "Task queued for execution"
}
```

#### Update Agent

Update agent configuration or status.

**Endpoint:** `PUT /agents/{agent_id}`

**Request Body:**

```json
{
  "status": "idle",
  "config": {
    "timeout": 600
  },
  "enabled": false
}
```

#### Delete Agent

Disable an agent (soft delete).

**Endpoint:** `DELETE /agents/{agent_id}`

### Metrics API

#### Get Metrics

Retrieve metrics with optional filtering.

**Endpoint:** `GET /metrics`

**Query Parameters:**

- `name`: Metric name filter
- `start`: Start time (ISO 8601)
- `end`: End time (ISO 8601)
- `limit`: Maximum results (default: 100)

**Response:**

```json
[
  {
    "metric_id": "metric-uuid-789",
    "metric_name": "evolution.improvement.rate",
    "value": 12.5,
    "tags": {
      "phase": "refactoring",
      "target": "backend"
    },
    "timestamp": "2025-08-17T12:00:00Z"
  }
]
```

#### Save Metric

Record a new metric value.

**Endpoint:** `POST /metrics`

**Request Body:**

```json
{
  "metric_name": "custom.metric",
  "value": 42.5,
  "tags": {
    "component": "agent",
    "environment": "production"
  },
  "timestamp": "2025-08-17T12:00:00Z"
}
```

#### Get Metrics Summary

Get aggregated metrics summary.

**Endpoint:** `GET /metrics/summary`

**Response:**

```json
{
  "timestamp": "2025-08-17T12:00:00Z",
  "kpis": {
    "evolution_cycles": 50,
    "agent_executions": 1000,
    "improvement_rate": 15.2,
    "error_rate": 2.1,
    "avg_execution_time": 3.5
  },
  "health": {
    "cpu_usage": 45.5,
    "memory_usage": 60.2,
    "disk_usage": 30.8,
    "active_agents": 5,
    "queue_depth": 10
  },
  "recent_metrics": []
}
```

#### Get Real-time Metrics

Get metrics from the last 5 minutes.

**Endpoint:** `GET /metrics/realtime`

#### Batch Save Metrics

Save multiple metrics in one request.

**Endpoint:** `POST /metrics/batch`

**Request Body:**

```json
{
  "metrics": [
    {
      "metric_name": "metric1",
      "value": 10,
      "tags": {}
    },
    {
      "metric_name": "metric2",
      "value": 20,
      "tags": {}
    }
  ]
}
```

## WebSocket Events

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('wss://api.t-developer.io/ws')
```

### Event Types

#### Evolution Events

- `evolution:started` - Evolution cycle started
- `evolution:phase_changed` - Phase transition
- `evolution:progress` - Progress update
- `evolution:completed` - Evolution completed
- `evolution:failed` - Evolution failed

#### Agent Events

- `agent:started` - Agent execution started
- `agent:completed` - Agent execution completed
- `agent:failed` - Agent execution failed
- `agent:status_changed` - Agent status changed

#### Metrics Events

- `metrics:update` - New metrics available
- `metrics:point` - Single metric point

#### System Events

- `system:status` - System status update
- `system:error` - System error
- `system:warning` - System warning

### Message Format

```json
{
  "type": "evolution:progress",
  "payload": {
    "evolutionId": "evo-123",
    "phase": "refactoring",
    "progress": 0.75
  },
  "timestamp": "2025-08-17T12:00:00Z",
  "id": "msg-uuid-123"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Rate Limits

- 100 requests per minute per API key
- 10 concurrent WebSocket connections
- 1000 metrics per minute

## SDKs

### Python

```python
from t_developer import Client

client = Client(api_key="your-api-key")
evolution = client.evolution.start(target_path="/backend")
```

### JavaScript/TypeScript

```typescript
import { TDeveloperClient } from '@t-developer/sdk'

const client = new TDeveloperClient({ apiKey: 'your-api-key' })
const evolution = await client.evolution.start({ targetPath: '/backend' })
```

## Postman Collection

Download our [Postman Collection](https://api.t-developer.io/postman-collection.json) for easy API testing.

## Support

For API support, please contact:

- Email: <api-support@t-developer.io>
- GitHub Issues: <https://github.com/t-developer/api/issues>
