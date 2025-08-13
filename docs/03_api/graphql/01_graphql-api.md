# 📊 GraphQL API Documentation

## Overview

GraphQL API for flexible querying of T-Developer evolution system data.

## Endpoint

```
POST https://api.t-developer.com/graphql
```

## Authentication

```http
Authorization: Bearer <jwt_token>
```

## Schema

### Types

```graphql
type Agent {
  id: ID!
  name: String!
  type: AgentType!
  generation: Int!
  fitness: Float!
  memory_kb: Float!
  speed_us: Float!
  code: String!
  status: AgentStatus!
  created_at: DateTime!
  updated_at: DateTime!
  metrics: AgentMetrics
  evolution_history: [Evolution!]
}

type Evolution {
  id: ID!
  generation: Int!
  parent_id: ID
  mutation_type: String
  fitness_before: Float!
  fitness_after: Float!
  timestamp: DateTime!
}

type AgentMetrics {
  success_rate: Float!
  average_response_time: Float!
  total_requests: Int!
  error_count: Int!
  last_evaluation: DateTime!
}

type Generation {
  number: Int!
  average_fitness: Float!
  best_fitness: Float!
  worst_fitness: Float!
  agent_count: Int!
  improvement_rate: Float!
  created_at: DateTime!
}

enum AgentType {
  NL_INPUT
  UI_SELECTION
  PARSER
  COMPONENT_DECISION
  MATCH_RATE
  SEARCH
  GENERATION
  ASSEMBLY
  DOWNLOAD
  SERVICE_BUILDER
  SERVICE_IMPROVER
}

enum AgentStatus {
  ACTIVE
  EVOLVING
  TESTING
  DEPRECATED
  FAILED
}
```

### Queries

```graphql
type Query {
  # Agent queries
  agent(id: ID!): Agent
  agents(
    type: AgentType
    status: AgentStatus
    generation: Int
    limit: Int = 10
    offset: Int = 0
  ): [Agent!]!
  
  # Evolution queries
  currentGeneration: Generation
  generation(number: Int!): Generation
  generations(
    limit: Int = 10
    offset: Int = 0
  ): [Generation!]!
  
  evolutionHistory(
    agentId: ID!
    limit: Int = 50
  ): [Evolution!]!
  
  # Metrics queries
  systemMetrics: SystemMetrics
  evolutionMetrics: EvolutionMetrics
  performanceMetrics: PerformanceMetrics
}

type SystemMetrics {
  total_agents: Int!
  active_agents: Int!
  average_fitness: Float!
  memory_usage_mb: Float!
  cpu_usage_percent: Float!
  uptime_seconds: Int!
}

type EvolutionMetrics {
  current_generation: Int!
  total_evolutions: Int!
  improvement_rate: Float!
  rollback_count: Int!
  safety_score: Float!
  autonomy_level: Float!
}

type PerformanceMetrics {
  requests_per_second: Float!
  average_latency_ms: Float!
  error_rate: Float!
  success_rate: Float!
  cache_hit_rate: Float!
}
```

### Mutations

```graphql
type Mutation {
  # Evolution control
  startEvolution(
    population_size: Int = 100
    mutation_rate: Float = 0.15
  ): EvolutionSession!
  
  stopEvolution(
    session_id: ID!
  ): EvolutionSession!
  
  rollbackGeneration(
    generation: Int!
  ): Generation!
  
  # Agent management
  createAgent(
    input: CreateAgentInput!
  ): Agent!
  
  updateAgent(
    id: ID!
    input: UpdateAgentInput!
  ): Agent!
  
  deleteAgent(
    id: ID!
  ): Boolean!
  
  # Manual intervention
  adjustFitness(
    agent_id: ID!
    fitness: Float!
    reason: String!
  ): Agent!
  
  forceEvolution(
    agent_id: ID!
  ): Evolution!
}

input CreateAgentInput {
  name: String!
  type: AgentType!
  code: String!
  initial_fitness: Float
}

input UpdateAgentInput {
  name: String
  code: String
  status: AgentStatus
}

type EvolutionSession {
  id: ID!
  status: SessionStatus!
  started_at: DateTime!
  ended_at: DateTime
  generations_completed: Int!
  total_improvements: Float!
}

enum SessionStatus {
  RUNNING
  PAUSED
  COMPLETED
  FAILED
}
```

### Subscriptions

```graphql
type Subscription {
  # Real-time evolution updates
  evolutionProgress: EvolutionUpdate!
  
  # Agent status changes
  agentStatusChanged(
    agent_id: ID
  ): AgentStatusUpdate!
  
  # Metrics stream
  metricsUpdate(
    interval: Int = 5000
  ): MetricsUpdate!
  
  # Alert notifications
  systemAlert: Alert!
}

type EvolutionUpdate {
  generation: Int!
  fitness: Float!
  improvement: Float!
  agents_evolved: Int!
  timestamp: DateTime!
}

type AgentStatusUpdate {
  agent_id: ID!
  old_status: AgentStatus!
  new_status: AgentStatus!
  reason: String
  timestamp: DateTime!
}

type MetricsUpdate {
  system: SystemMetrics!
  evolution: EvolutionMetrics!
  performance: PerformanceMetrics!
  timestamp: DateTime!
}

type Alert {
  id: ID!
  severity: AlertSeverity!
  type: AlertType!
  message: String!
  details: String
  timestamp: DateTime!
}

enum AlertSeverity {
  INFO
  WARNING
  ERROR
  CRITICAL
}

enum AlertType {
  FITNESS_REGRESSION
  MEMORY_VIOLATION
  SPEED_VIOLATION
  SECURITY_THREAT
  SYSTEM_ERROR
}
```

## Example Queries

### Get Current Generation Info
```graphql
query GetCurrentGeneration {
  currentGeneration {
    number
    average_fitness
    best_fitness
    agent_count
    improvement_rate
  }
  
  evolutionMetrics {
    current_generation
    total_evolutions
    autonomy_level
  }
}
```

### Get Agent Details
```graphql
query GetAgent($id: ID!) {
  agent(id: $id) {
    id
    name
    type
    generation
    fitness
    memory_kb
    speed_us
    status
    metrics {
      success_rate
      average_response_time
      error_count
    }
    evolution_history(limit: 10) {
      generation
      fitness_before
      fitness_after
      mutation_type
      timestamp
    }
  }
}
```

### Get Top Performing Agents
```graphql
query GetTopAgents {
  agents(
    status: ACTIVE
    limit: 10
  ) {
    id
    name
    type
    fitness
    metrics {
      success_rate
    }
  }
}
```

## Example Mutations

### Start Evolution
```graphql
mutation StartEvolution {
  startEvolution(
    population_size: 150
    mutation_rate: 0.2
  ) {
    id
    status
    started_at
  }
}
```

### Force Agent Evolution
```graphql
mutation ForceEvolution($agentId: ID!) {
  forceEvolution(agent_id: $agentId) {
    id
    generation
    fitness_before
    fitness_after
    timestamp
  }
}
```

## Example Subscriptions

### Monitor Evolution Progress
```graphql
subscription MonitorEvolution {
  evolutionProgress {
    generation
    fitness
    improvement
    agents_evolved
    timestamp
  }
}
```

### Monitor System Alerts
```graphql
subscription MonitorAlerts {
  systemAlert {
    id
    severity
    type
    message
    details
    timestamp
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "errors": [
    {
      "message": "Agent not found",
      "extensions": {
        "code": "AGENT_NOT_FOUND",
        "agentId": "123",
        "timestamp": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

### Error Codes
- `AGENT_NOT_FOUND` - Requested agent doesn't exist
- `EVOLUTION_IN_PROGRESS` - Cannot modify during evolution
- `CONSTRAINT_VIOLATION` - Memory or speed constraint violated
- `UNAUTHORIZED` - Invalid or missing authentication
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Rate Limiting

- **Queries**: 1000 requests/minute
- **Mutations**: 100 requests/minute
- **Subscriptions**: 10 concurrent connections

## Best Practices

1. **Use Fragments** for repeated fields
2. **Implement Pagination** for large datasets
3. **Subscribe Selectively** to avoid overwhelming clients
4. **Cache Queries** when possible
5. **Batch Mutations** for efficiency

---

**API Version**: 1.0.0  
**Last Updated**: 2024-01-01