# T-Developer API Documentation

## Overview

The T-Developer API provides a complete 9-agent pipeline for generating production-ready applications from natural language descriptions. This comprehensive documentation covers all endpoints, data models, and usage patterns.

## Base URL
```
Production: https://api.t-developer.com/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication using API keys:

```http
Authorization: Bearer YOUR_API_KEY
```

## Core Endpoints

### 1. Project Generation

#### Generate Complete Project
```http
POST /generate
```

Initiates the complete 9-agent pipeline to generate a project.

**Request Body:**
```json
{
  "query": "Create a todo app with React and TypeScript",
  "project_type": "web_app",
  "complexity": "medium",
  "target_environments": ["development", "production"],
  "preferences": {
    "framework": "react",
    "language": "typescript",
    "testing": true,
    "ci_cd": true
  },
  "metadata": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "success": true,
  "project_id": "proj_abc123",
  "execution_time": 28.5,
  "pipeline_result": {
    "framework": "react",
    "generated_files": 45,
    "download_url": "https://api.t-developer.com/v1/download/abc123",
    "project_structure": {
      "src/": ["App.tsx", "components/", "hooks/"],
      "public/": ["index.html"],
      "root": ["package.json", "tsconfig.json", "README.md"]
    }
  },
  "stage_results": {
    "nl_input": {
      "success": true,
      "execution_time": 2.1,
      "requirements": ["todo management", "react ui", "typescript"],
      "intent": "create_web_application"
    },
    "ui_selection": {
      "success": true,
      "execution_time": 3.2,
      "framework": "react",
      "components": ["TodoList", "TodoItem", "AddTodo"],
      "styling": "css_modules"
    },
    "generation": {
      "success": true,
      "execution_time": 12.8,
      "files_generated": 45,
      "lines_of_code": 1250
    },
    "assembly": {
      "success": true,
      "execution_time": 4.2,
      "package_size": "2.3MB",
      "compression_ratio": 0.65
    }
  },
  "performance_metrics": {
    "total_execution_time": 28.5,
    "cache_hit_rate": 0.15,
    "memory_usage_mb": 145.2,
    "success_rate": 1.0
  }
}
```

### 2. Project Status

#### Get Project Status
```http
GET /projects/{project_id}/status
```

Returns the current status of a project generation.

**Response:**
```json
{
  "project_id": "proj_abc123",
  "status": "completed",
  "current_stage": "download",
  "progress": 100,
  "completed_stages": [
    "nl_input", "ui_selection", "parser", "component_decision",
    "match_rate", "search", "generation", "assembly", "download"
  ],
  "estimated_completion": "2024-01-15T10:30:00Z",
  "can_download": true
}
```

### 3. Download Management

#### Download Project
```http
GET /download/{download_token}
```

Downloads the generated project package.

**Response:** Binary file (ZIP/TAR format)

**Headers:**
```http
Content-Type: application/zip
Content-Disposition: attachment; filename="todo-app-20240115.zip"
Content-Length: 2457600
```

#### Get Download Info
```http
GET /downloads/{download_token}/info
```

**Response:**
```json
{
  "download_token": "abc123",
  "file_name": "todo-app-20240115.zip",
  "file_size": 2457600,
  "format": "zip",
  "expires_at": "2024-01-16T10:30:00Z",
  "checksum": "sha256:abcd1234...",
  "metadata": {
    "project_name": "Todo App",
    "framework": "react",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 4. Agent-Specific Endpoints

#### NL Input Analysis
```http
POST /agents/nl-input/analyze
```

**Request:**
```json
{
  "user_input": "Build an e-commerce platform with user authentication"
}
```

**Response:**
```json
{
  "intent": "create_ecommerce_platform",
  "requirements": [
    "user authentication",
    "product catalog",
    "shopping cart",
    "payment processing"
  ],
  "suggested_tech_stack": {
    "frontend": "react",
    "backend": "node.js",
    "database": "postgresql"
  },
  "complexity_score": 8.5,
  "estimated_development_time": "2-3 months"
}
```

#### UI Selection
```http
POST /agents/ui-selection/recommend
```

**Request:**
```json
{
  "requirements": ["responsive design", "modern ui", "accessibility"],
  "project_type": "web_app",
  "target_devices": ["desktop", "mobile"]
}
```

**Response:**
```json
{
  "recommended_framework": "react",
  "ui_library": "material-ui",
  "components": [
    {
      "name": "Navigation",
      "type": "layout",
      "responsive": true
    },
    {
      "name": "ProductCard", 
      "type": "display",
      "variants": ["grid", "list"]
    }
  ],
  "theme": {
    "primary_color": "#1976d2",
    "secondary_color": "#dc004e",
    "typography": "roboto"
  }
}
```

### 5. Analytics & Monitoring

#### Get Performance Metrics
```http
GET /analytics/performance
```

**Query Parameters:**
- `period`: "1h", "24h", "7d", "30d"
- `metric_type`: "execution_time", "memory", "success_rate"

**Response:**
```json
{
  "period": "24h",
  "metrics": {
    "avg_execution_time": 32.4,
    "p95_execution_time": 58.2,
    "success_rate": 0.94,
    "total_requests": 156,
    "cache_hit_rate": 0.23
  },
  "stage_performance": {
    "nl_input": {"avg_time": 2.1, "success_rate": 0.98},
    "generation": {"avg_time": 15.2, "success_rate": 0.91},
    "assembly": {"avg_time": 4.8, "success_rate": 0.96}
  }
}
```

#### Get Security Status
```http
GET /security/status
```

**Response:**
```json
{
  "last_scan": "2024-01-15T09:00:00Z",
  "security_score": 87.5,
  "vulnerabilities": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 12
  },
  "compliance": {
    "owasp_top_10": true,
    "pci_dss": false,
    "gdpr": true
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid project type specified",
    "details": {
      "field": "project_type",
      "allowed_values": ["web_app", "mobile_app", "api", "fullstack"]
    },
    "request_id": "req_xyz789"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `AUTHENTICATION_ERROR` | Invalid API key | 401 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `PIPELINE_ERROR` | Agent pipeline failure | 500 |
| `TIMEOUT_ERROR` | Request timed out | 504 |

## Rate Limiting

- **Free Tier**: 10 requests per hour
- **Pro Tier**: 100 requests per hour  
- **Enterprise**: 1000 requests per hour

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1642248000
```

## Webhooks

Configure webhooks to receive real-time updates on project generation.

### Webhook Events

#### project.generation.started
```json
{
  "event": "project.generation.started",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-15T10:00:00Z",
  "data": {
    "user_query": "Create a todo app",
    "estimated_completion": "2024-01-15T10:30:00Z"
  }
}
```

#### project.generation.completed
```json
{
  "event": "project.generation.completed",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-15T10:28:34Z",
  "data": {
    "success": true,
    "execution_time": 28.34,
    "download_url": "https://api.t-developer.com/v1/download/abc123",
    "files_generated": 45
  }
}
```

#### project.generation.failed
```json
{
  "event": "project.generation.failed",
  "project_id": "proj_abc123",
  "timestamp": "2024-01-15T10:15:22Z",
  "data": {
    "error_stage": "generation",
    "error_message": "Insufficient requirements provided",
    "retry_possible": true
  }
}
```

### Configuring Webhooks
```http
POST /webhooks
```

**Request:**
```json
{
  "url": "https://your-app.com/webhooks/t-developer",
  "events": [
    "project.generation.completed",
    "project.generation.failed"
  ],
  "secret": "your-webhook-secret"
}
```

## SDK Integration

### JavaScript/Node.js
```bash
npm install @t-developer/sdk
```

```javascript
import { TDeveloperClient } from '@t-developer/sdk';

const client = new TDeveloperClient({
  apiKey: 'your-api-key',
  environment: 'production'
});

async function generateProject() {
  const result = await client.generate({
    query: 'Create a React todo app',
    preferences: {
      framework: 'react',
      language: 'typescript'
    }
  });
  
  console.log('Project generated:', result.project_id);
  
  // Download when ready
  if (result.success) {
    const download = await client.download(result.download_token);
    console.log('Downloaded to:', download.filePath);
  }
}
```

### Python
```bash
pip install t-developer-sdk
```

```python
from t_developer import TDeveloperClient

client = TDeveloperClient(api_key='your-api-key')

result = client.generate(
    query='Create a FastAPI todo app',
    preferences={
        'framework': 'fastapi',
        'database': 'postgresql'
    }
)

if result.success:
    print(f"Project ID: {result.project_id}")
    
    # Wait for completion
    status = client.wait_for_completion(result.project_id, timeout=300)
    
    if status.completed:
        download_path = client.download(result.download_token)
        print(f"Downloaded to: {download_path}")
```

## Best Practices

### 1. Request Optimization
- Use specific, detailed queries for better results
- Include context and constraints in your requests
- Leverage caching by using consistent parameters

### 2. Error Handling
- Always check the `success` field in responses
- Implement exponential backoff for retries
- Handle rate limiting gracefully

### 3. Performance
- Use webhooks for long-running operations
- Cache responses when appropriate
- Monitor your usage with analytics endpoints

### 4. Security
- Never expose API keys in client-side code
- Use HTTPS for all requests
- Validate webhook signatures

## Support & Resources

- **API Status**: https://status.t-developer.com
- **Support**: support@t-developer.com
- **Documentation**: https://docs.t-developer.com
- **GitHub**: https://github.com/t-developer-mvp

## Changelog

### v1.2.0 (2024-01-15)
- Added security scanning endpoints
- Improved performance metrics
- Enhanced webhook support

### v1.1.0 (2024-01-01) 
- Added agent-specific endpoints
- Implemented download management
- Added analytics dashboard

### v1.0.0 (2023-12-01)
- Initial release
- Core 9-agent pipeline
- Basic project generation