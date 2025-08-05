# REST API Reference

## Overview
T-Developer REST API provides endpoints for managing projects, agents, and workflows.

## Base URL
```
https://api.t-developer.com/v1
```

## Authentication
```http
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### Projects
```http
POST /projects
GET /projects
GET /projects/{id}
PUT /projects/{id}
DELETE /projects/{id}
```

### Agents
```http
GET /agents
GET /agents/{type}/status
POST /agents/{type}/execute
```

### Workflows
```http
POST /workflows
GET /workflows/{id}/status
POST /workflows/{id}/cancel
```

## Request/Response Examples

### Create Project
```http
POST /projects
Content-Type: application/json

{
  "name": "My Todo App",
  "description": "React todo application with authentication",
  "requirements": {
    "framework": "react",
    "features": ["auth", "crud", "responsive"]
  }
}
```

### Response
```json
{
  "id": "proj_123",
  "status": "processing",
  "workflow_id": "wf_456",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Error Handling
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid project requirements",
    "details": {}
  }
}
```