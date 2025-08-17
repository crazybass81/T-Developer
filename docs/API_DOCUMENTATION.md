# 📡 T-Developer v2 API 문서

## 개요

T-Developer v2는 RESTful API와 WebSocket을 통해 진화 프로세스를 제어하고 모니터링할 수 있습니다.

**Base URL**: `http://localhost:8000`
**API Version**: `v2`
**인증**: 현재 개발 단계에서는 인증 없음

## 인증

현재 개발 버전에서는 인증이 비활성화되어 있습니다. 프로덕션 배포 시 다음 인증 방법을 지원할 예정입니다:

- API Key
- JWT Token
- OAuth 2.0

## 공통 응답 형식

### 성공 응답

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-08-17T12:00:00Z"
}
```

### 오류 응답

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  },
  "timestamp": "2025-08-17T12:00:00Z"
}
```

## 엔드포인트

### 시스템 상태

#### GET /health

시스템 상태 확인

**응답**:

```json
{
  "status": "healthy",
  "service": "T-Developer v2 Backend",
  "timestamp": "2025-08-17T12:00:00Z",
  "evolution_status": "idle",
  "agents_ready": 4
}
```

#### GET /

서비스 정보

**응답**:

```json
{
  "service": "T-Developer Backend",
  "version": "2.0.0",
  "status": "running",
  "evolution_status": "idle"
}
```

### 진화 제어

#### POST /api/evolution/start

새로운 진화 사이클 시작

**요청 본문**:

```json
{
  "target_path": "/path/to/project",
  "max_cycles": 1,
  "focus_areas": ["documentation", "quality", "performance"],
  "dry_run": true
}
```

**응답**:

```json
{
  "success": true,
  "message": "Evolution started",
  "status": {
    "status": "running",
    "current_phase": "research",
    "progress": 0,
    "start_time": "2025-08-17T12:00:00Z"
  }
}
```

#### GET /api/evolution/status

현재 진화 상태 조회

**응답**:

```json
{
  "status": "running",
  "current_phase": "planning",
  "progress": 45,
  "results": [],
  "start_time": "2025-08-17T12:00:00Z",
  "end_time": null,
  "target_path": "/path/to/project",
  "dry_run": true
}
```

#### POST /api/evolution/stop

진행 중인 진화 중지

**응답**:

```json
{
  "success": true,
  "message": "Evolution stopped",
  "status": {
    "status": "stopped",
    "end_time": "2025-08-17T12:05:00Z"
  }
}
```

### SharedContext 관리

#### GET /api/context/current

현재 활성 컨텍스트 조회

**응답**:

```json
{
  "evolution_id": "uuid-here",
  "target_path": "/path/to/project",
  "focus_areas": ["documentation"],
  "created_at": "2025-08-17T12:00:00Z",
  "phases": {
    "original_analysis": { ... },
    "external_research": { ... },
    "improvement_plan": { ... },
    "implementation_log": { ... },
    "evaluation_results": { ... }
  }
}
```

#### GET /api/context/{evolution_id}

특정 진화 컨텍스트 조회

**매개변수**:

- `evolution_id`: 진화 ID (UUID)

**응답**: 위와 동일

#### GET /api/context/comparison/{evolution_id}

진화 전/중/후 비교 데이터

**응답**:

```json
{
  "before": {
    "metrics": {
      "docstring_coverage": 45,
      "test_coverage": 60,
      "complexity": 75
    },
    "issues": [ ... ]
  },
  "plan": {
    "tasks": [ ... ],
    "estimated_impact": 0.25
  },
  "after": {
    "metrics": {
      "docstring_coverage": 85,
      "test_coverage": 75,
      "complexity": 65
    },
    "changes": [ ... ]
  }
}
```

#### GET /api/context/list

모든 진화 컨텍스트 목록

**쿼리 매개변수**:

- `limit`: 결과 수 제한 (기본값: 10)
- `offset`: 시작 위치 (기본값: 0)
- `sort`: 정렬 기준 (created_at, status)

**응답**:

```json
{
  "contexts": [
    {
      "evolution_id": "uuid-1",
      "created_at": "2025-08-17T12:00:00Z",
      "target_path": "/project1",
      "status": "completed"
    },
    ...
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

#### POST /api/context/export/{evolution_id}

진화 데이터 내보내기

**응답**:

```json
{
  "success": true,
  "export_path": "/exports/evolution_uuid.json",
  "size_bytes": 12345
}
```

### Agent 관리

#### GET /api/agents

모든 Agent 상태 조회

**응답**:

```json
[
  {
    "id": "research-001",
    "name": "ResearchAgent",
    "type": "research",
    "status": "ready",
    "metrics": {
      "tasksCompleted": 42,
      "successRate": 95,
      "avgExecutionTime": 2.5
    },
    "lastActivity": "2025-08-17T12:00:00Z"
  },
  ...
]
```

#### GET /api/agents/{agent_id}

특정 Agent 상태 조회

**매개변수**:

- `agent_id`: Agent 식별자

**응답**: 위 배열의 단일 객체

#### POST /api/agents/{agent_id}/execute

Agent 태스크 실행

**요청 본문**:

```json
{
  "task_type": "analyze",
  "parameters": {
    "target": "/path/to/code",
    "depth": "comprehensive"
  }
}
```

**응답**:

```json
{
  "success": true,
  "agent_id": "research-001",
  "task_type": "analyze",
  "result": { ... }
}
```

### 메트릭

#### GET /api/metrics

시스템 메트릭 조회

**응답**:

```json
{
  "agents": {
    "total": 5,
    "ready": 4,
    "busy": 1
  },
  "tasks": {
    "completed": 156,
    "success_rate": 92.5
  },
  "evolution": {
    "cycles_completed": 12,
    "current_status": "idle"
  }
}
```

#### GET /api/metrics/realtime

실시간 메트릭 조회

**응답**:

```json
{
  "timestamp": "2025-08-17T12:00:00Z",
  "cpu_usage": 45.2,
  "memory_usage": 62.8,
  "active_tasks": 2,
  "queue_size": 5
}
```

## WebSocket

### 연결

`ws://localhost:8000/ws`

### 메시지 형식

#### 클라이언트 → 서버

```json
{
  "type": "subscribe",
  "channel": "evolution",
  "data": { }
}
```

#### 서버 → 클라이언트

**연결 확인**:

```json
{
  "type": "connection",
  "message": "Connected to T-Developer backend",
  "timestamp": "2025-08-17T12:00:00Z"
}
```

**진화 업데이트**:

```json
{
  "type": "evolution:progress",
  "data": {
    "phase": "planning",
    "progress": 45,
    "message": "Creating improvement tasks"
  },
  "timestamp": "2025-08-17T12:00:00Z"
}
```

**Agent 상태**:

```json
{
  "type": "agent:status",
  "agentId": "research-001",
  "status": "busy",
  "metrics": { ... }
}
```

### 이벤트 유형

| 이벤트 | 설명 |
|--------|------|
| `connection` | WebSocket 연결 성공 |
| `evolution:started` | 진화 시작됨 |
| `evolution:progress` | 진화 진행 상황 업데이트 |
| `evolution:completed` | 진화 완료 |
| `evolution:failed` | 진화 실패 |
| `agent:status` | Agent 상태 변경 |
| `metrics:update` | 메트릭 업데이트 |

## 오류 코드

| 코드 | 설명 | HTTP 상태 |
|------|------|-----------|
| `EVOLUTION_RUNNING` | 이미 진화가 진행 중 | 400 |
| `NO_EVOLUTION` | 진행 중인 진화 없음 | 400 |
| `AGENT_NOT_FOUND` | Agent를 찾을 수 없음 | 404 |
| `CONTEXT_NOT_FOUND` | 컨텍스트를 찾을 수 없음 | 404 |
| `INVALID_PARAMETERS` | 잘못된 매개변수 | 400 |
| `INTERNAL_ERROR` | 내부 서버 오류 | 500 |

## 제한 사항

- **요청 크기**: 최대 10MB
- **동시 연결**: WebSocket 최대 100개
- **Rate Limiting**: 분당 600 요청 (개발 모드에서는 비활성화)
- **타임아웃**: API 요청 30초, WebSocket 유휴 시간 5분

## SDK 예제

### Python

```python
import httpx
import asyncio

async def start_evolution():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/evolution/start",
            json={
                "target_path": "/my/project",
                "focus_areas": ["documentation"],
                "dry_run": True
            }
        )
        return response.json()

# 실행
result = asyncio.run(start_evolution())
print(result)
```

### JavaScript

```javascript
// 진화 시작
fetch('http://localhost:8000/api/evolution/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    target_path: '/my/project',
    focus_areas: ['documentation'],
    dry_run: true
  })
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket 연결
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### cURL

```bash
# 상태 확인
curl http://localhost:8000/health

# 진화 시작
curl -X POST http://localhost:8000/api/evolution/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_path": "/my/project",
    "focus_areas": ["documentation"],
    "dry_run": true
  }'

# 현재 컨텍스트 조회
curl http://localhost:8000/api/context/current
```

---

**버전**: 2.0.0
**마지막 업데이트**: 2025-08-17
**API 스키마**: OpenAPI 3.0 (Swagger UI: <http://localhost:8000/docs>)
