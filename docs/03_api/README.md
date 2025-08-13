# 📡 API Documentation

## Overview
T-Developer AI Autonomous Evolution System의 API 문서입니다. REST, GraphQL, WebSocket 인터페이스를 제공합니다.

## 📁 API Types

### REST API
- [**REST API Reference**](rest/01_rest-api-reference.md) - Complete REST API documentation
- **Base URL**: `https://api.t-developer.com/v1`
- **Authentication**: Bearer JWT

### GraphQL API
- [**GraphQL API Schema**](graphql/01_graphql-api.md) - GraphQL schema and queries
- **Endpoint**: `https://api.t-developer.com/graphql`
- **Subscriptions**: Real-time updates

### WebSocket API
- [**WebSocket API Events**](websocket/01_websocket-api.md) - Real-time event documentation
- **Endpoint**: `wss://ws.t-developer.com/v1/evolution`
- **Channels**: evolution, metrics, alerts

## 🔑 Authentication

### JWT Token
```http
Authorization: Bearer <jwt_token>
```

### API Key (deprecated)
```http
X-API-Key: <api_key>
```

## 📊 Quick Reference

### Common Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/evolution/start` | Start evolution process |
| GET | `/agents` | List all agents |
| GET | `/generation/current` | Get current generation |
| POST | `/rollback` | Rollback to previous generation |

### Rate Limits
- **REST**: 1000 req/min
- **GraphQL**: 100 queries/min
- **WebSocket**: 10 concurrent connections

## 🔗 Related Documents
- [Architecture](../01_architecture/README.md)
- [Implementation](../02_implementation/README.md)
- [Testing](../04_testing/README.md)
- [Error Handling](../05_operations/01_error-handling-guide.md)

## 📈 API Status
- **Version**: v1
- **Status**: 🟢 Operational
- **Uptime**: 99.95%

## 💻 Code Examples

### REST Example
```python
import requests

response = requests.post(
    "https://api.t-developer.com/v1/evolution/start",
    headers={"Authorization": f"Bearer {token}"},
    json={"population_size": 100}
)
```

### GraphQL Example
```graphql
query GetCurrentGeneration {
  currentGeneration {
    number
    average_fitness
    agent_count
  }
}
```

### WebSocket Example
```javascript
const ws = new WebSocket('wss://ws.t-developer.com/v1/evolution');
ws.on('evolution_update', (data) => {
  console.log(`Generation ${data.generation}: ${data.fitness}`);
});
```

---
**API Version**: 1.0.0  
**Last Updated**: 2024-01-01