# 🔌 WebSocket API Documentation

## Overview

Real-time bidirectional communication for T-Developer evolution system monitoring and control.

## Endpoint

```
wss://ws.t-developer.com/v1/evolution
```

## Authentication

### Connection with Token
```javascript
const ws = new WebSocket('wss://ws.t-developer.com/v1/evolution', {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
});
```

### Authentication Message
```json
{
  "type": "auth",
  "token": "<jwt_token>"
}
```

## Message Format

### Standard Message Structure
```json
{
  "id": "unique-message-id",
  "type": "message-type",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    // Message-specific data
  }
}
```

## Event Types

### Client → Server Events

#### Subscribe to Evolution Updates
```json
{
  "type": "subscribe",
  "channel": "evolution",
  "filters": {
    "generation_min": 100,
    "fitness_min": 0.9
  }
}
```

#### Control Evolution
```json
{
  "type": "control",
  "action": "start|stop|pause|resume",
  "parameters": {
    "population_size": 100,
    "mutation_rate": 0.15
  }
}
```

#### Request Agent Status
```json
{
  "type": "get_agent",
  "agent_id": "agent-123"
}
```

#### Execute Command
```json
{
  "type": "command",
  "cmd": "rollback",
  "args": {
    "generation": 95
  }
}
```

### Server → Client Events

#### Evolution Update
```json
{
  "type": "evolution_update",
  "data": {
    "generation": 101,
    "average_fitness": 0.956,
    "best_fitness": 0.981,
    "improvement": 0.052,
    "agents_evolved": 100,
    "mutations_applied": 15,
    "crossovers": 70
  }
}
```

#### Agent Status Update
```json
{
  "type": "agent_update",
  "data": {
    "agent_id": "agent-123",
    "name": "NL_Input_Agent_v42",
    "status": "evolving",
    "fitness": 0.943,
    "memory_kb": 6.2,
    "speed_us": 2.7,
    "generation": 101
  }
}
```

#### System Metrics
```json
{
  "type": "metrics",
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "active_agents": 847,
    "requests_per_second": 1250,
    "average_latency_ms": 42,
    "error_rate": 0.001
  }
}
```

#### Alert Notification
```json
{
  "type": "alert",
  "severity": "warning|error|critical",
  "data": {
    "alert_id": "alert-789",
    "title": "Fitness Regression Detected",
    "message": "Generation 102 fitness dropped by 8%",
    "details": {
      "previous_fitness": 0.956,
      "current_fitness": 0.879,
      "affected_agents": ["agent-123", "agent-456"]
    },
    "recommended_action": "rollback"
  }
}
```

#### Evolution Log
```json
{
  "type": "log",
  "level": "info|warning|error",
  "data": {
    "message": "Mutation applied to agent-123",
    "details": {
      "mutation_type": "parameter_adjustment",
      "gene_modified": "learning_rate",
      "old_value": 0.01,
      "new_value": 0.015
    }
  }
}
```

## Channels

### Available Channels
```javascript
const CHANNELS = {
  EVOLUTION: 'evolution',      // Evolution updates
  AGENTS: 'agents',            // Agent status updates
  METRICS: 'metrics',          // System metrics
  ALERTS: 'alerts',            // System alerts
  LOGS: 'logs',               // Evolution logs
  CONTROL: 'control'          // Control commands
};
```

### Channel Subscription
```json
{
  "type": "subscribe",
  "channels": ["evolution", "metrics", "alerts"]
}
```

### Channel Unsubscription
```json
{
  "type": "unsubscribe",
  "channels": ["logs"]
}
```

## Connection Management

### Connection Lifecycle
```javascript
// Connection established
ws.onopen = (event) => {
  console.log('Connected to evolution system');
  
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: localStorage.getItem('jwt_token')
  }));
};

// Message received
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

// Error occurred
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Connection closed
ws.onclose = (event) => {
  console.log('Disconnected:', event.reason);
  // Implement reconnection logic
  setTimeout(reconnect, 5000);
};
```

### Heartbeat/Ping-Pong
```javascript
// Client sends ping
setInterval(() => {
  ws.send(JSON.stringify({
    type: 'ping',
    timestamp: Date.now()
  }));
}, 30000); // Every 30 seconds

// Server responds with pong
{
  "type": "pong",
  "timestamp": 1704067200000
}
```

## Binary Data Support

### Binary Message Format
```javascript
// Sending binary data (agent code)
const encoder = new TextEncoder();
const binaryData = encoder.encode(agentCode);

ws.send(new Blob([
  JSON.stringify({ type: 'agent_code', agent_id: 'agent-123' }),
  binaryData
]));
```

### Receiving Binary Data
```javascript
ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    event.data.text().then(text => {
      const [metadata, ...code] = text.split('\n');
      const meta = JSON.parse(metadata);
      handleBinaryMessage(meta, code.join('\n'));
    });
  }
};
```

## Error Handling

### Error Message Format
```json
{
  "type": "error",
  "error": {
    "code": "EVOLUTION_FAILED",
    "message": "Evolution process failed",
    "details": {
      "generation": 102,
      "reason": "Memory constraint violation",
      "agent_id": "agent-789"
    }
  }
}
```

### Error Codes
- `AUTH_FAILED` - Authentication failed
- `UNAUTHORIZED` - Not authorized for action
- `EVOLUTION_FAILED` - Evolution process error
- `AGENT_NOT_FOUND` - Agent doesn't exist
- `INVALID_COMMAND` - Unknown command
- `RATE_LIMITED` - Too many messages
- `CONSTRAINT_VIOLATION` - Memory/speed limit exceeded

## Rate Limiting

- **Message Rate**: 100 messages/second
- **Connection Limit**: 10 concurrent connections per user
- **Data Rate**: 10MB/minute

## Code Examples

### JavaScript Client
```javascript
class EvolutionWebSocket {
  constructor(token) {
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.messageQueue = [];
  }
  
  connect() {
    this.ws = new WebSocket('wss://ws.t-developer.com/v1/evolution');
    
    this.ws.onopen = () => {
      this.authenticate();
      this.subscribe(['evolution', 'metrics', 'alerts']);
      this.flushMessageQueue();
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.reconnect();
    };
  }
  
  authenticate() {
    this.send({
      type: 'auth',
      token: this.token
    });
  }
  
  subscribe(channels) {
    this.send({
      type: 'subscribe',
      channels: channels
    });
  }
  
  send(message) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }
  
  handleMessage(message) {
    switch(message.type) {
      case 'evolution_update':
        this.onEvolutionUpdate(message.data);
        break;
      case 'alert':
        this.onAlert(message.data);
        break;
      case 'metrics':
        this.onMetrics(message.data);
        break;
    }
  }
  
  reconnect() {
    if (this.reconnectAttempts < 5) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, Math.pow(2, this.reconnectAttempts) * 1000);
    }
  }
}
```

### Python Client
```python
import asyncio
import websockets
import json

class EvolutionWebSocket:
    def __init__(self, token):
        self.token = token
        self.uri = 'wss://ws.t-developer.com/v1/evolution'
    
    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            # Authenticate
            await self.authenticate(websocket)
            
            # Subscribe to channels
            await self.subscribe(websocket, ['evolution', 'metrics'])
            
            # Listen for messages
            async for message in websocket:
                await self.handle_message(json.loads(message))
    
    async def authenticate(self, websocket):
        await websocket.send(json.dumps({
            'type': 'auth',
            'token': self.token
        }))
    
    async def subscribe(self, websocket, channels):
        await websocket.send(json.dumps({
            'type': 'subscribe',
            'channels': channels
        }))
    
    async def handle_message(self, message):
        if message['type'] == 'evolution_update':
            await self.on_evolution_update(message['data'])
        elif message['type'] == 'alert':
            await self.on_alert(message['data'])
    
    async def on_evolution_update(self, data):
        print(f"Generation {data['generation']}: "
              f"Fitness {data['average_fitness']:.3f}")
    
    async def on_alert(self, data):
        print(f"Alert: {data['title']} - {data['message']}")

# Usage
async def main():
    client = EvolutionWebSocket('your-jwt-token')
    await client.connect()

asyncio.run(main())
```

---

**API Version**: 1.0.0  
**Protocol**: WebSocket (RFC 6455)  
**Last Updated**: 2024-01-01
