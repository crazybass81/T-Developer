# Phase 5: 오케스트레이션 시스템 - Tasks 5.1~5.3 SubTask 구조

## 📋 Task 5.1~5.3 SubTask 리스트

### Task 5.1: 중앙 오케스트레이터 설계 및 구현

- **SubTask 5.1.1**: 오케스트레이터 아키텍처 설계
- **SubTask 5.1.2**: 에이전트 통합 인터페이스
- **SubTask 5.1.3**: 워크플로우 상태 관리
- **SubTask 5.1.4**: 이벤트 기반 통신 시스템

### Task 5.2: 워크플로우 엔진 구축

- **SubTask 5.2.1**: 워크플로우 정의 모델
- **SubTask 5.2.2**: 워크플로우 파서 및 검증기
- **SubTask 5.2.3**: 실행 스케줄러
- **SubTask 5.2.4**: 워크플로우 실행 모니터

### Task 5.3: 에이전트 라이프사이클 관리

- **SubTask 5.3.1**: 에이전트 레지스트리
- **SubTask 5.3.2**: 에이전트 헬스 체크 시스템
- **SubTask 5.3.3**: 동적 에이전트 스케일링
- **SubTask 5.3.4**: 에이전트 버전 관리

---

## 📝 세부 작업지시서

### Task 5.1: 중앙 오케스트레이터 설계 및 구현

#### SubTask 5.1.1: 오케스트레이터 아키텍처 설계

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 16시간

**작업 내용**:

```python
# backend/src/orchestration/core/orchestrator.py
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
import uuid

@dataclass
class OrchestratorConfig:
    max_concurrent_workflows: int = 100
    max_concurrent_tasks: int = 500
    task_timeout_seconds: int = 300
    workflow_timeout_seconds: int = 3600
    enable_auto_recovery: bool = True
    enable_metrics: bool = True
    state_storage_type: str = "dynamodb"
    message_queue_type: str = "sqs"

@dataclass
class WorkflowState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskState(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class CentralOrchestrator:
    """T-Developer 중앙 오케스트레이션 시스템"""

    def __init__(self, config: OrchestratorConfig):
        self.config = config

        # 핵심 컴포넌트
        self.agent_registry: AgentRegistry = None
        self.workflow_engine: WorkflowEngine = None
        self.task_scheduler: TaskScheduler = None
        self.state_manager: StateManager = None
        self.event_bus: EventBus = None
        self.metrics_collector: MetricsCollector = None
        self.resource_manager: ResourceManager = None

        # 실행 상태 추적
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.active_tasks: Dict[str, AgentTask] = {}
        self.workflow_semaphore = asyncio.Semaphore(config.max_concurrent_workflows)
        self.task_semaphore = asyncio.Semaphore(config.max_concurrent_tasks)

        # 동기화 프리미티브
        self.workflow_lock = asyncio.Lock()
        self.task_lock = asyncio.Lock()
        self.shutdown_event = asyncio.Event()

    async def initialize(self):
        """오케스트레이터 초기화"""
        logger.info("Initializing Central Orchestrator...")

        # 1. 상태 저장소 초기화
        self.state_manager = await self._initialize_state_manager()

        # 2. 이벤트 버스 초기화
        self.event_bus = EventBus()
        await self.event_bus.start()

        # 3. 에이전트 레지스트리 초기화
        self.agent_registry = AgentRegistry(self.event_bus)
        await self.agent_registry.initialize()

        # 4. 워크플로우 엔진 초기화
        self.workflow_engine = WorkflowEngine(self)

        # 5. 태스크 스케줄러 초기화
        self.task_scheduler = TaskScheduler(
            self.agent_registry,
            self.task_semaphore
        )

        # 6. 리소스 관리자 초기화
        self.resource_manager = ResourceManager(self.config)

        # 7. 메트릭 수집기 초기화
        if self.config.enable_metrics:
            self.metrics_collector = MetricsCollector(self)
            await self.metrics_collector.start()

        # 8. 이벤트 핸들러 등록
        self._register_event_handlers()

        # 9. 중단된 워크플로우 복구
        if self.config.enable_auto_recovery:
            await self._recover_interrupted_workflows()

        logger.info("Central Orchestrator initialized successfully")

    async def submit_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """워크플로우 제출"""
        async with self.workflow_semaphore:
            # 워크플로우 정의 로드
            workflow_def = await self._load_workflow_definition(workflow_id)

            # 입력 검증
            await self._validate_workflow_input(workflow_def, input_data)

            # 워크플로우 실행 생성
            execution = await self.workflow_engine.create_execution(
                workflow_def,
                input_data,
                options or {}
            )

            # 활성 워크플로우 추가
            async with self.workflow_lock:
                self.active_workflows[execution.id] = execution

            # 실행 시작
            asyncio.create_task(
                self._execute_workflow(execution)
            )

            # 워크플로우 시작 이벤트 발행
            await self.event_bus.publish(
                OrchestratorEvent(
                    event_type="workflow.started",
                    workflow_id=execution.id,
                    timestamp=datetime.utcnow(),
                    data={"workflow_def_id": workflow_id}
                )
            )

            return execution.id

    async def _execute_workflow(self, execution: WorkflowExecution):
        """워크플로우 실행 (내부)"""
        try:
            # 워크플로우 실행
            result = await self.workflow_engine.execute(execution)

            # 완료 처리
            execution.state = WorkflowState.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.result = result

            # 완료 이벤트 발행
            await self.event_bus.publish(
                OrchestratorEvent(
                    event_type="workflow.completed",
                    workflow_id=execution.id,
                    timestamp=datetime.utcnow(),
                    data={"result": result}
                )
            )

        except Exception as e:
            # 실패 처리
            execution.state = WorkflowState.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error = str(e)

            # 실패 이벤트 발행
            await self.event_bus.publish(
                OrchestratorEvent(
                    event_type="workflow.failed",
                    workflow_id=execution.id,
                    timestamp=datetime.utcnow(),
                    data={"error": str(e)}
                )
            )

        finally:
            # 상태 저장
            await self.state_manager.save_workflow_state(
                execution.id,
                execution
            )

            # 활성 워크플로우에서 제거
            async with self.workflow_lock:
                self.active_workflows.pop(execution.id, None)
```

**검증 기준**:

- [ ] 오케스트레이터 핵심 아키텍처 구현
- [ ] 동시성 제어 메커니즘
- [ ] 상태 관리 통합
- [ ] 이벤트 기반 통신

#### SubTask 5.1.2: 에이전트 통합 인터페이스

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/orchestration/core/agent_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import httpx
import asyncio
from datetime import datetime, timedelta

@dataclass
class AgentCapability:
    name: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    timeout_seconds: int = 300
    max_retries: int = 3

@dataclass
class AgentInfo:
    id: str
    type: str
    name: str
    version: str
    endpoint: str
    capabilities: List[AgentCapability]
    health_check_endpoint: str
    status: str = "unknown"
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentInterface(ABC):
    """에이전트 통합을 위한 표준 인터페이스"""

    @abstractmethod
    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        """태스크 실행"""
        pass

    @abstractmethod
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """태스크 상태 조회"""
        pass

    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        """태스크 취소"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        pass

class HTTPAgentProxy(AgentInterface):
    """HTTP 기반 에이전트 프록시"""

    def __init__(self, agent_info: AgentInfo):
        self.agent_info = agent_info
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=5.0,
                read=300.0,
                write=30.0,
                pool=5.0
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10
            )
        )
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=httpx.HTTPError
        )

    async def execute(self, task: AgentTask) -> Dict[str, Any]:
        """에이전트 태스크 실행"""
        @self._circuit_breaker
        async def _execute():
            # 입력 데이터 준비
            request_data = {
                "task_id": task.id,
                "input": task.input_data,
                "context": task.context,
                "timeout": task.timeout
            }

            # 에이전트 호출
            response = await self.client.post(
                f"{self.agent_info.endpoint}/execute",
                json=request_data,
                headers={
                    "X-Task-ID": task.id,
                    "X-Workflow-ID": task.workflow_id,
                    "X-Request-ID": str(uuid.uuid4())
                }
            )

            # 응답 처리
            if response.status_code == 202:  # Accepted
                # 비동기 실행 - 폴링 필요
                return {
                    "status": "accepted",
                    "task_id": task.id,
                    "poll_url": response.headers.get("Location")
                }
            elif response.status_code == 200:
                # 동기 실행 완료
                return response.json()
            else:
                raise AgentExecutionError(
                    f"Agent returned {response.status_code}: {response.text}"
                )

        return await _execute()

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """태스크 상태 조회"""
        response = await self.client.get(
            f"{self.agent_info.endpoint}/tasks/{task_id}/status"
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"status": "not_found"}
        else:
            raise AgentStatusError(
                f"Failed to get status: {response.status_code}"
            )

    async def cancel(self, task_id: str) -> bool:
        """태스크 취소"""
        try:
            response = await self.client.post(
                f"{self.agent_info.endpoint}/tasks/{task_id}/cancel"
            )
            return response.status_code in [200, 202]
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        try:
            response = await self.client.get(
                self.agent_info.health_check_endpoint,
                timeout=5.0
            )

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow(),
                    "details": response.json()
                }
            else:
                return {
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow(),
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }

class AgentProxyFactory:
    """에이전트 프록시 팩토리"""

    @staticmethod
    def create_proxy(agent_info: AgentInfo) -> AgentInterface:
        """에이전트 타입에 따른 프록시 생성"""
        if agent_info.endpoint.startswith("http"):
            return HTTPAgentProxy(agent_info)
        elif agent_info.endpoint.startswith("grpc"):
            return GRPCAgentProxy(agent_info)
        elif agent_info.endpoint.startswith("lambda"):
            return LambdaAgentProxy(agent_info)
        else:
            raise ValueError(f"Unknown agent type: {agent_info.endpoint}")
```

**검증 기준**:

- [ ] 표준 에이전트 인터페이스 정의
- [ ] HTTP/gRPC/Lambda 프록시 구현
- [ ] Circuit Breaker 패턴 적용
- [ ] 에러 핸들링 및 재시도 로직

#### SubTask 5.1.3: 워크플로우 상태 관리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/orchestration/core/state_manager.py
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import json

class StateStorage(ABC):
    """상태 저장소 추상 클래스"""

    @abstractmethod
    async def save(self, key: str, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def list_keys(self, prefix: str) -> List[str]:
        pass

class DynamoDBStateStorage(StateStorage):
    """DynamoDB 기반 상태 저장소"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    async def save(self, key: str, data: Dict[str, Any]) -> None:
        """상태 저장"""
        item = {
            'id': key,
            'data': json.dumps(data, default=str),
            'timestamp': datetime.utcnow().isoformat(),
            'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }

        await asyncio.to_thread(
            self.table.put_item,
            Item=item
        )

    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        """상태 로드"""
        response = await asyncio.to_thread(
            self.table.get_item,
            Key={'id': key}
        )

        if 'Item' in response:
            return json.loads(response['Item']['data'])
        return None

class StateManager:
    """워크플로우 및 태스크 상태 관리자"""

    def __init__(self, storage: StateStorage):
        self.storage = storage
        self.state_cache = TTLCache(maxsize=1000, ttl=300)
        self.cache_lock = asyncio.Lock()
        self.write_buffer = asyncio.Queue(maxsize=1000)
        self.writer_task = None

    async def start(self):
        """상태 관리자 시작"""
        self.writer_task = asyncio.create_task(self._write_worker())

    async def stop(self):
        """상태 관리자 중지"""
        if self.writer_task:
            self.writer_task.cancel()

    async def save_workflow_state(
        self,
        workflow_id: str,
        execution: WorkflowExecution
    ) -> None:
        """워크플로우 상태 저장"""
        state_data = {
            "workflow_id": execution.workflow_id,
            "execution_id": execution.id,
            "state": execution.state.value,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat()
                if execution.completed_at else None,
            "tasks": {
                task_id: self._serialize_task(task)
                for task_id, task in execution.tasks.items()
            },
            "context": execution.context,
            "result": execution.result,
            "error": execution.error,
            "metadata": execution.metadata
        }

        # 캐시 업데이트
        async with self.cache_lock:
            self.state_cache[workflow_id] = state_data

        # 비동기 저장 큐에 추가
        await self.write_buffer.put((
            f"workflow:{workflow_id}",
            state_data
        ))

    async def load_workflow_state(
        self,
        workflow_id: str
    ) -> Optional[WorkflowExecution]:
        """워크플로우 상태 로드"""
        # 캐시 확인
        async with self.cache_lock:
            if workflow_id in self.state_cache:
                state_data = self.state_cache[workflow_id]
                return self._deserialize_workflow(state_data)

        # 저장소에서 로드
        state_data = await self.storage.load(f"workflow:{workflow_id}")
        if state_data:
            # 캐시 업데이트
            async with self.cache_lock:
                self.state_cache[workflow_id] = state_data
            return self._deserialize_workflow(state_data)

        return None

    async def update_task_state(
        self,
        workflow_id: str,
        task_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """태스크 상태 업데이트"""
        # 워크플로우 상태 로드
        execution = await self.load_workflow_state(workflow_id)
        if not execution:
            raise ValueError(f"Workflow {workflow_id} not found")

        # 태스크 업데이트
        if task_id not in execution.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = execution.tasks[task_id]
        for key, value in updates.items():
            setattr(task, key, value)

        # 타임스탬프 업데이트
        if updates.get("status") == "completed":
            task.completed_at = datetime.utcnow()
        elif updates.get("status") == "running":
            task.started_at = datetime.utcnow()

        # 상태 저장
        await self.save_workflow_state(workflow_id, execution)

    async def list_active_workflows(self) -> List[str]:
        """활성 워크플로우 목록 조회"""
        keys = await self.storage.list_keys("workflow:")
        workflows = []

        for key in keys:
            workflow_id = key.replace("workflow:", "")
            execution = await self.load_workflow_state(workflow_id)

            if execution and execution.state in [
                WorkflowState.PENDING,
                WorkflowState.RUNNING
            ]:
                workflows.append(workflow_id)

        return workflows

    async def _write_worker(self):
        """비동기 쓰기 워커"""
        batch = []

        while True:
            try:
                # 배치 수집 (최대 100개 또는 1초)
                deadline = asyncio.create_task(asyncio.sleep(1.0))

                while len(batch) < 100:
                    get_task = asyncio.create_task(self.write_buffer.get())

                    done, pending = await asyncio.wait(
                        [get_task, deadline],
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    if get_task in done:
                        batch.append(get_task.result())
                    else:
                        get_task.cancel()
                        break

                # 배치 저장
                if batch:
                    await self._save_batch(batch)
                    batch.clear()

            except asyncio.CancelledError:
                # 남은 데이터 저장
                if batch:
                    await self._save_batch(batch)
                break
            except Exception as e:
                logger.error(f"Write worker error: {e}")
```

**검증 기준**:

- [ ] 상태 저장/로드 메커니즘
- [ ] 캐싱 전략 구현
- [ ] 배치 쓰기 최적화
- [ ] 상태 복구 기능

#### SubTask 5.1.4: 이벤트 기반 통신 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/orchestration/core/event_bus.py
from typing import Dict, List, Callable, Optional, Any
import asyncio
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class OrchestratorEvent:
    event_id: str
    event_type: str
    source: str
    workflow_id: Optional[str]
    task_id: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "workflow_id": self.workflow_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "correlation_id": self.correlation_id
        }

class EventHandler:
    """이벤트 핸들러 래퍼"""

    def __init__(
        self,
        handler: Callable,
        filter_func: Optional[Callable] = None,
        priority: int = 0
    ):
        self.handler = handler
        self.filter_func = filter_func
        self.priority = priority
        self.is_async = asyncio.iscoroutinefunction(handler)

    async def handle(self, event: OrchestratorEvent) -> Any:
        """이벤트 처리"""
        # 필터 확인
        if self.filter_func and not self.filter_func(event):
            return None

        # 핸들러 실행
        if self.is_async:
            return await self.handler(event)
        else:
            return self.handler(event)

class EventBus:
    """중앙 이벤트 버스"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.subscribers: Dict[str, List[EventHandler]] = {}
        self.event_queue = asyncio.Queue(
            maxsize=self.config.get("queue_size", 10000)
        )
        self.event_store: Optional[EventStore] = None
        self.running = False
        self.workers = []
        self.stats = EventBusStats()

    async def start(self):
        """이벤트 버스 시작"""
        self.running = True

        # 이벤트 저장소 초기화
        if self.config.get("enable_event_store", True):
            self.event_store = EventStore(
                self.config.get("event_store_config", {})
            )
            await self.event_store.initialize()

        # 워커 시작
        num_workers = self.config.get("num_workers", 4)
        for i in range(num_workers):
            worker = asyncio.create_task(
                self._event_worker(f"worker-{i}")
            )
            self.workers.append(worker)

        logger.info(f"Event bus started with {num_workers} workers")

    async def stop(self):
        """이벤트 버스 중지"""
        self.running = False

        # 워커 중지
        for worker in self.workers:
            worker.cancel()

        # 남은 이벤트 처리
        await self._flush_events()

        # 이벤트 저장소 종료
        if self.event_store:
            await self.event_store.close()

    async def publish(
        self,
        event: OrchestratorEvent,
        priority: int = 0
    ) -> None:
        """이벤트 발행"""
        # 이벤트 ID 생성
        if not event.event_id:
            event.event_id = str(uuid.uuid4())

        # 통계 업데이트
        self.stats.increment_published(event.event_type)

        # 이벤트 저장
        if self.event_store:
            await self.event_store.save(event)

        # 큐에 추가
        try:
            await asyncio.wait_for(
                self.event_queue.put((priority, event)),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            logger.error(f"Event queue full, dropping event: {event.event_id}")
            self.stats.increment_dropped()

    def subscribe(
        self,
        event_type: str,
        handler: Callable,
        filter_func: Optional[Callable] = None,
        priority: int = 0
    ) -> str:
        """이벤트 구독"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        event_handler = EventHandler(handler, filter_func, priority)
        self.subscribers[event_type].append(event_handler)

        # 우선순위 정렬
        self.subscribers[event_type].sort(
            key=lambda h: h.priority,
            reverse=True
        )

        subscription_id = f"{event_type}:{id(handler)}"
        logger.info(f"Subscribed to {event_type}: {subscription_id}")

        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """구독 취소"""
        event_type, handler_id = subscription_id.split(":")

        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                h for h in self.subscribers[event_type]
                if id(h.handler) != int(handler_id)
            ]
            return True

        return False

    async def _event_worker(self, worker_id: str):
        """이벤트 처리 워커"""
        logger.info(f"Event worker {worker_id} started")

        while self.running:
            try:
                # 이벤트 가져오기
                priority, event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )

                # 이벤트 처리
                await self._process_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event worker {worker_id} error: {e}")

        logger.info(f"Event worker {worker_id} stopped")

    async def _process_event(self, event: OrchestratorEvent):
        """이벤트 처리"""
        start_time = datetime.utcnow()

        try:
            # 전역 핸들러 (*) 실행
            if "*" in self.subscribers:
                for handler in self.subscribers["*"]:
                    await self._execute_handler(handler, event)

            # 특정 이벤트 핸들러 실행
            if event.event_type in self.subscribers:
                handlers = self.subscribers[event.event_type]

                # 병렬 실행 가능한 핸들러 그룹화
                async_tasks = []

                for handler in handlers:
                    if handler.is_async:
                        task = asyncio.create_task(
                            self._execute_handler(handler, event)
                        )
                        async_tasks.append(task)
                    else:
                        # 동기 핸들러는 순차 실행
                        await self._execute_handler(handler, event)

                # 비동기 핸들러 대기
                if async_tasks:
                    await asyncio.gather(*async_tasks, return_exceptions=True)

            # 처리 시간 기록
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.stats.record_processing_time(event.event_type, duration)

        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            self.stats.increment_errors(event.event_type)

    async def _execute_handler(
        self,
        handler: EventHandler,
        event: OrchestratorEvent
    ):
        """개별 핸들러 실행"""
        try:
            await handler.handle(event)
        except Exception as e:
            logger.error(
                f"Handler error for event {event.event_id}: {e}",
                exc_info=True
            )
```

**검증 기준**:

- [ ] 이벤트 발행/구독 메커니즘
- [ ] 비동기 이벤트 처리
- [ ] 이벤트 우선순위 관리
- [ ] 이벤트 저장 및 재생

### Task 5.2: 워크플로우 엔진 구축

#### SubTask 5.2.1: 워크플로우 정의 모델

**담당자**: 시니어 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/orchestration/workflow/workflow_definition.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json

@dataclass
class TaskDependency:
    task_id: str
    condition: Optional[str] = None
    wait_for_completion: bool = True

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: int = 1
    max_delay: int = 60
    multiplier: float = 2.0
    retry_on: List[str] = field(default_factory=lambda: ["error", "timeout"])

@dataclass
class WorkflowTask:
    id: str
    name: str
    agent_type: str
    description: Optional[str] = None

    # 입출력 매핑
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)

    # 의존성
    dependencies: List[TaskDependency] = field(default_factory=list)

    # 실행 설정
    timeout_seconds: int = 300
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)

    # 조건부 실행
    conditions: List[str] = field(default_factory=list)
    skip_on_failure: bool = False

    # 에러 핸들링
    error_handler: Optional[str] = None
    compensation_task: Optional[str] = None

@dataclass
class ParallelBlock:
    """병렬 실행 블록"""
    id: str
    tasks: List[Union[WorkflowTask, 'ConditionalBlock']]
    max_concurrency: Optional[int] = None
    fail_fast: bool = True

@dataclass
class ConditionalBlock:
    """조건부 실행 블록"""
    id: str
    condition: str
    if_tasks: List[Union[WorkflowTask, ParallelBlock]]
    else_tasks: Optional[List[Union[WorkflowTask, ParallelBlock]]] = None

@dataclass
class LoopBlock:
    """반복 실행 블록"""
    id: str
    iterator: str  # 반복할 데이터 경로
    variable: str  # 반복 변수 이름
    tasks: List[Union[WorkflowTask, ParallelBlock, ConditionalBlock]]
    max_iterations: Optional[int] = None
    parallel: bool = False

@dataclass
class WorkflowDefinition:
    """워크플로우 정의"""
    id: str
    name: str
    version: str
    description: str

    # 입출력 스키마
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

    # 워크플로우 구조
    tasks: List[Union[WorkflowTask, ParallelBlock, ConditionalBlock, LoopBlock]]

    # 전역 설정
    timeout_seconds: int = 3600
    max_retries: int = 1

    # 에러 핸들러
    error_handlers: Dict[str, str] = field(default_factory=dict)

    # 메타데이터
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowLoader:
    """워크플로우 정의 로더"""

    def __init__(self):
        self.validators = {
            'yaml': self._validate_yaml,
            'json': self._validate_json,
            'dsl': self._validate_dsl
        }

    async def load_from_file(self, file_path: str) -> WorkflowDefinition:
        """파일에서 워크플로우 로드"""
        with open(file_path, 'r') as f:
            content = f.read()

        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return await self.load_from_yaml(content)
        elif file_path.endswith('.json'):
            return await self.load_from_json(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    async def load_from_yaml(self, yaml_content: str) -> WorkflowDefinition:
        """YAML에서 워크플로우 로드"""
        data = yaml.safe_load(yaml_content)
        await self._validate_yaml(data)
        return self._parse_workflow_data(data)

    async def load_from_json(self, json_content: str) -> WorkflowDefinition:
        """JSON에서 워크플로우 로드"""
        data = json.loads(json_content)
        await self._validate_json(data)
        return self._parse_workflow_data(data)

    def _parse_workflow_data(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """워크플로우 데이터 파싱"""
        # 기본 정보
        workflow = WorkflowDefinition(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            description=data.get('description', ''),
            input_schema=data.get('input_schema', {}),
            output_schema=data.get('output_schema', {}),
            timeout_seconds=data.get('timeout_seconds', 3600),
            max_retries=data.get('max_retries', 1),
            error_handlers=data.get('error_handlers', {}),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )

        # 태스크 파싱
        workflow.tasks = self._parse_tasks(data.get('tasks', []))

        return workflow

    def _parse_tasks(
        self,
        tasks_data: List[Dict[str, Any]]
    ) -> List[Union[WorkflowTask, ParallelBlock, ConditionalBlock, LoopBlock]]:
        """태스크 리스트 파싱"""
        tasks = []

        for task_data in tasks_data:
            task_type = task_data.get('type', 'task')

            if task_type == 'task':
                task = self._parse_workflow_task(task_data)
            elif task_type == 'parallel':
                task = self._parse_parallel_block(task_data)
            elif task_type == 'conditional':
                task = self._parse_conditional_block(task_data)
            elif task_type == 'loop':
                task = self._parse_loop_block(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            tasks.append(task)

        return tasks
```

**검증 기준**:

- [ ] 포괄적인 워크플로우 모델
- [ ] YAML/JSON 로더 구현
- [ ] 태스크 타입 지원 (순차/병렬/조건/반복)
- [ ] 입출력 매핑 및 의존성 관리

#### SubTask 5.2.2: 워크플로우 파서 및 검증기

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/orchestration/workflow/workflow_validator.py
from typing import Dict, List, Set, Optional, Any
import networkx as nx
from jsonschema import validate, ValidationError

class WorkflowValidator:
    """워크플로우 정의 검증기"""

    def __init__(self):
        self.schema_validator = SchemaValidator()
        self.dependency_validator = DependencyValidator()
        self.expression_validator = ExpressionValidator()

    async def validate(
        self,
        workflow: WorkflowDefinition
    ) -> ValidationResult:
        """워크플로우 전체 검증"""
        errors = []
        warnings = []

        # 1. 기본 구조 검증
        structural_errors = await self._validate_structure(workflow)
        errors.extend(structural_errors)

        # 2. 태스크 검증
        task_errors = await self._validate_tasks(workflow)
        errors.extend(task_errors)

        # 3. 의존성 검증
        dependency_result = await self.dependency_validator.validate(workflow)
        errors.extend(dependency_result.errors)
        warnings.extend(dependency_result.warnings)

        # 4. 입출력 매핑 검증
        mapping_errors = await self._validate_mappings(workflow)
        errors.extend(mapping_errors)

        # 5. 조건식 검증
        expression_errors = await self._validate_expressions(workflow)
        errors.extend(expression_errors)

        # 6. 리소스 사용량 추정
        resource_warnings = await self._estimate_resources(workflow)
        warnings.extend(resource_warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    async def _validate_structure(
        self,
        workflow: WorkflowDefinition
    ) -> List[ValidationError]:
        """기본 구조 검증"""
        errors = []

        # 필수 필드 확인
        if not workflow.id:
            errors.append(ValidationError("Workflow ID is required"))
        if not workflow.name:
            errors.append(ValidationError("Workflow name is required"))
        if not workflow.version:
            errors.append(ValidationError("Workflow version is required"))

        # 버전 형식 검증
        if not self._is_valid_version(workflow.version):
            errors.append(
                ValidationError(f"Invalid version format: {workflow.version}")
            )

        # 태스크 존재 확인
        if not workflow.tasks:
            errors.append(ValidationError("Workflow must have at least one task"))

        return errors

    async def _validate_tasks(
        self,
        workflow: WorkflowDefinition
    ) -> List[ValidationError]:
        """태스크 검증"""
        errors = []
        task_ids = set()

        for task in self._flatten_tasks(workflow.tasks):
            # ID 중복 확인
            if task.id in task_ids:
                errors.append(
                    ValidationError(f"Duplicate task ID: {task.id}")
                )
            task_ids.add(task.id)

            # 에이전트 타입 검증
            if not await self._is_valid_agent_type(task.agent_type):
                errors.append(
                    ValidationError(
                        f"Unknown agent type: {task.agent_type} in task {task.id}"
                    )
                )

            # 타임아웃 검증
            if task.timeout_seconds <= 0:
                errors.append(
                    ValidationError(
                        f"Invalid timeout for task {task.id}: {task.timeout_seconds}"
                    )
                )

        return errors

class DependencyValidator:
    """의존성 검증기"""

    async def validate(
        self,
        workflow: WorkflowDefinition
    ) -> DependencyValidationResult:
        """의존성 검증"""
        errors = []
        warnings = []

        # 의존성 그래프 생성
        dep_graph = self._build_dependency_graph(workflow)

        # 1. 순환 의존성 검사
        cycles = list(nx.simple_cycles(dep_graph))
        if cycles:
            for cycle in cycles:
                errors.append(
                    ValidationError(
                        f"Circular dependency detected: {' -> '.join(cycle)}"
                    )
                )

        # 2. 미해결 의존성 검사
        all_task_ids = set(dep_graph.nodes())

        for task_id, task_data in dep_graph.nodes(data=True):
            task = task_data['task']

            for dep in task.dependencies:
                if dep.task_id not in all_task_ids:
                    errors.append(
                        ValidationError(
                            f"Task {task_id} depends on unknown task: {dep.task_id}"
                        )
                    )

        # 3. 도달 불가능한 태스크 검사
        if dep_graph.number_of_nodes() > 0:
            # 시작 노드 찾기 (의존성이 없는 노드)
            start_nodes = [
                n for n in dep_graph.nodes()
                if dep_graph.in_degree(n) == 0
            ]

            if not start_nodes:
                warnings.append(
                    ValidationWarning(
                        "No start tasks found (all tasks have dependencies)"
                    )
                )
            else:
                # 도달 가능한 노드 찾기
                reachable = set()
                for start in start_nodes:
                    reachable.update(
                        nx.descendants(dep_graph, start)
                    )
                reachable.update(start_nodes)

                # 도달 불가능한 노드
                unreachable = all_task_ids - reachable
                if unreachable:
                    warnings.append(
                        ValidationWarning(
                            f"Unreachable tasks: {unreachable}"
                        )
                    )

        return DependencyValidationResult(errors, warnings)
```

**검증 기준**:

- [ ] 구조적 검증 (필수 필드, 형식)
- [ ] 태스크 검증 (ID 중복, 타입)
- [ ] 의존성 검증 (순환, 미해결)
- [ ] 표현식 및 매핑 검증

#### SubTask 5.2.3: 실행 스케줄러

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/orchestration/workflow/task_scheduler.py
from typing import Dict, List, Set, Optional, Any
import asyncio
from datetime import datetime
from collections import deque

class TaskScheduler:
    """태스크 실행 스케줄러"""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        max_concurrent_tasks: int = 100
    ):
        self.agent_registry = agent_registry
        self.max_concurrent_tasks = max_concurrent_tasks

        # 실행 큐
        self.ready_queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Set[str] = set()

        # 동기화
        self.task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.scheduler_lock = asyncio.Lock()

    async def schedule_workflow(
        self,
        execution: WorkflowExecution,
        workflow_def: WorkflowDefinition
    ) -> None:
        """워크플로우 스케줄링"""
        # 태스크 의존성 분석
        task_graph = self._build_task_graph(workflow_def.tasks)

        # 초기 실행 가능 태스크 찾기
        ready_tasks = self._find_ready_tasks(
            task_graph,
            set(),
            execution.context
        )

        # 준비된 태스크 큐에 추가
        for task_id in ready_tasks:
            await self.ready_queue.put(task_id)

        # 스케줄러 실행
        await self._run_scheduler(execution, task_graph)

    async def _run_scheduler(
        self,
        execution: WorkflowExecution,
        task_graph: TaskGraph
    ) -> None:
        """스케줄러 메인 루프"""
        while True:
            # 종료 조건 확인
            if self._is_workflow_complete(execution, task_graph):
                break

            # 준비된 태스크 가져오기
            try:
                task_id = await asyncio.wait_for(
                    self.ready_queue.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                # 데드락 감지
                if self._detect_deadlock(execution, task_graph):
                    raise WorkflowDeadlockError("Workflow deadlock detected")
                continue

            # 태스크 실행
            await self._execute_task(task_id, execution, task_graph)

    async def _execute_task(
        self,
        task_id: str,
        execution: WorkflowExecution,
        task_graph: TaskGraph
    ) -> None:
        """개별 태스크 실행"""
        task = execution.tasks[task_id]

        async with self.task_semaphore:
            try:
                # 태스크 상태 업데이트
                task.status = TaskState.RUNNING
                task.started_at = datetime.utcnow()

                # 에이전트 프록시 가져오기
                agent_proxy = await self.agent_registry.get_agent(
                    task.agent_type
                )

                # 입력 데이터 준비
                input_data = self._prepare_task_input(
                    task,
                    execution.context
                )

                # 태스크 실행
                execution_task = asyncio.create_task(
                    self._run_task_with_timeout(
                        agent_proxy,
                        task,
                        input_data
                    )
                )

                async with self.scheduler_lock:
                    self.running_tasks[task_id] = execution_task

                # 결과 대기
                result = await execution_task

                # 성공 처리
                await self._handle_task_success(
                    task_id,
                    result,
                    execution,
                    task_graph
                )

            except asyncio.TimeoutError:
                await self._handle_task_timeout(task_id, execution)
            except Exception as e:
                await self._handle_task_failure(task_id, e, execution)
            finally:
                async with self.scheduler_lock:
                    self.running_tasks.pop(task_id, None)

    async def _run_task_with_timeout(
        self,
        agent_proxy: AgentInterface,
        task: AgentTask,
        input_data: Dict[str, Any]
    ) -> Any:
        """타임아웃이 있는 태스크 실행"""
        return await asyncio.wait_for(
            agent_proxy.execute(task),
            timeout=task.timeout_seconds
        )

    async def _handle_task_success(
        self,
        task_id: str,
        result: Any,
        execution: WorkflowExecution,
        task_graph: TaskGraph
    ) -> None:
        """태스크 성공 처리"""
        task = execution.tasks[task_id]

        # 상태 업데이트
        task.status = TaskState.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = result

        # 출력 매핑
        self._apply_output_mapping(task, result, execution.context)

        # 완료 태스크 추가
        async with self.scheduler_lock:
            self.completed_tasks.add(task_id)

        # 다음 실행 가능 태스크 찾기
        next_tasks = self._find_ready_tasks(
            task_graph,
            self.completed_tasks,
            execution.context
        )

        # 준비된 태스크 큐에 추가
        for next_task_id in next_tasks:
            await self.ready_queue.put(next_task_id)

    def _prepare_task_input(
        self,
        task: WorkflowTask,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """태스크 입력 데이터 준비"""
        input_data = {}

        for target_key, source_path in task.input_mapping.items():
            # JSONPath 또는 단순 키로 값 추출
            value = self._extract_value(context, source_path)
            input_data[target_key] = value

        return input_data

    def _apply_output_mapping(
        self,
        task: WorkflowTask,
        result: Any,
        context: Dict[str, Any]
    ) -> None:
        """태스크 출력 매핑 적용"""
        for source_key, target_path in task.output_mapping.items():
            # 결과에서 값 추출
            if isinstance(result, dict):
                value = result.get(source_key)
            else:
                value = result

            # 컨텍스트에 저장
            self._set_value(context, target_path, value)
```

**검증 기준**:

- [ ] 태스크 스케줄링 알고리즘
- [ ] 동시 실행 제어
- [ ] 의존성 기반 실행 순서
- [ ] 데드락 감지 및 처리

#### SubTask 5.2.4: 워크플로우 실행 모니터

**담당자**: 백엔드 개발자  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/orchestration/workflow/execution_monitor.py
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timedelta

@dataclass
class WorkflowMetrics:
    workflow_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    average_task_duration: float
    total_duration: Optional[float]
    resource_usage: Dict[str, Any]

class ExecutionMonitor:
    """워크플로우 실행 모니터"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.active_executions: Dict[str, WorkflowMetrics] = {}
        self.metrics_store = MetricsStore()
        self.alert_manager = AlertManager()

        # 모니터링 설정
        self.monitoring_interval = 5  # seconds
        self.monitoring_task = None

    async def start(self):
        """모니터 시작"""
        # 이벤트 구독
        self.event_bus.subscribe("workflow.started", self._on_workflow_started)
        self.event_bus.subscribe("workflow.completed", self._on_workflow_completed)
        self.event_bus.subscribe("workflow.failed", self._on_workflow_failed)
        self.event_bus.subscribe("task.started", self._on_task_started)
        self.event_bus.subscribe("task.completed", self._on_task_completed)
        self.event_bus.subscribe("task.failed", self._on_task_failed)

        # 모니터링 루프 시작
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop(self):
        """모니터 중지"""
        if self.monitoring_task:
            self.monitoring_task.cancel()

    async def get_execution_status(
        self,
        execution_id: str
    ) -> Optional[WorkflowMetrics]:
        """실행 상태 조회"""
        return self.active_executions.get(execution_id)

    async def get_execution_history(
        self,
        workflow_id: str,
        limit: int = 10
    ) -> List[WorkflowMetrics]:
        """실행 이력 조회"""
        return await self.metrics_store.get_workflow_history(
            workflow_id,
            limit
        )

    async def _monitoring_loop(self):
        """모니터링 루프"""
        while True:
            try:
                await asyncio.sleep(self.monitoring_interval)

                # 활성 실행 모니터링
                for execution_id, metrics in self.active_executions.items():
                    await self._monitor_execution(execution_id, metrics)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")

    async def _monitor_execution(
        self,
        execution_id: str,
        metrics: WorkflowMetrics
    ):
        """개별 실행 모니터링"""
        # 실행 시간 확인
        elapsed_time = (datetime.utcnow() - metrics.start_time).total_seconds()

        # SLA 위반 확인
        sla_config = await self._get_sla_config(metrics.workflow_id)
        if sla_config:
            if elapsed_time > sla_config.max_duration:
                await self.alert_manager.send_alert(
                    AlertType.SLA_VIOLATION,
                    {
                        "execution_id": execution_id,
                        "elapsed_time": elapsed_time,
                        "max_duration": sla_config.max_duration
                    }
                )

        # 정체 태스크 확인
        stalled_tasks = await self._find_stalled_tasks(execution_id)
        if stalled_tasks:
            await self.alert_manager.send_alert(
                AlertType.STALLED_TASKS,
                {
                    "execution_id": execution_id,
                    "stalled_tasks": stalled_tasks
                }
            )

        # 리소스 사용량 확인
        resource_usage = await self._get_resource_usage(execution_id)
        metrics.resource_usage = resource_usage

        # 메트릭 저장
        await self.metrics_store.save_metrics(metrics)

    async def _on_workflow_started(self, event: OrchestratorEvent):
        """워크플로우 시작 이벤트 처리"""
        metrics = WorkflowMetrics(
            workflow_id=event.data["workflow_def_id"],
            execution_id=event.workflow_id,
            start_time=event.timestamp,
            end_time=None,
            total_tasks=event.data.get("total_tasks", 0),
            completed_tasks=0,
            failed_tasks=0,
            running_tasks=0,
            average_task_duration=0.0,
            total_duration=None,
            resource_usage={}
        )

        self.active_executions[event.workflow_id] = metrics

    async def _on_workflow_completed(self, event: OrchestratorEvent):
        """워크플로우 완료 이벤트 처리"""
        if event.workflow_id in self.active_executions:
            metrics = self.active_executions[event.workflow_id]
            metrics.end_time = event.timestamp
            metrics.total_duration = (
                metrics.end_time - metrics.start_time
            ).total_seconds()

            # 최종 메트릭 저장
            await self.metrics_store.save_final_metrics(metrics)

            # 활성 실행에서 제거
            del self.active_executions[event.workflow_id]
```

**검증 기준**:

- [ ] 실시간 실행 모니터링
- [ ] 메트릭 수집 및 저장
- [ ] SLA 모니터링
- [ ] 알림 시스템 통합

### Task 5.3: 에이전트 라이프사이클 관리

#### SubTask 5.3.1: 에이전트 레지스트리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/orchestration/agent/agent_registry.py
from typing import Dict, List, Optional, Set
import asyncio
from datetime import datetime

class AgentRegistry:
    """에이전트 레지스트리"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_proxies: Dict[str, AgentInterface] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}

        # 동기화
        self.registry_lock = asyncio.Lock()

        # 디스커버리
        self.discovery_service = AgentDiscoveryService()
        self.discovery_interval = 30  # seconds
        self.discovery_task = None

    async def initialize(self):
        """레지스트리 초기화"""
        # 기존 에이전트 로드
        await self._load_registered_agents()

        # 디스커버리 시작
        self.discovery_task = asyncio.create_task(
            self._discovery_loop()
        )

        # 이벤트 구독
        self.event_bus.subscribe(
            "agent.registered",
            self._on_agent_registered
        )
        self.event_bus.subscribe(
            "agent.unregistered",
            self._on_agent_unregistered
        )

    async def register_agent(
        self,
        agent_info: AgentInfo
    ) -> str:
        """에이전트 등록"""
        async with self.registry_lock:
            # 중복 확인
            if agent_info.id in self.agents:
                raise ValueError(f"Agent {agent_info.id} already registered")

            # 에이전트 정보 저장
            self.agents[agent_info.id] = agent_info

            # 프록시 생성
            proxy = AgentProxyFactory.create_proxy(agent_info)
            self.agent_proxies[agent_info.id] = proxy

            # 능력 인덱싱
            self._index_capabilities(agent_info)

            # 영구 저장
            await self._persist_agent(agent_info)

            # 등록 이벤트 발행
            await self.event_bus.publish(
                OrchestratorEvent(
                    event_type="agent.registered",
                    source="agent_registry",
                    timestamp=datetime.utcnow(),
                    data={"agent": agent_info.to_dict()}
                )
            )

            logger.info(f"Agent registered: {agent_info.id} ({agent_info.type})")

        return agent_info.id

    async def unregister_agent(self, agent_id: str) -> bool:
        """에이전트 등록 해제"""
        async with self.registry_lock:
            if agent_id not in self.agents:
                return False

            agent_info = self.agents[agent_id]

            # 레지스트리에서 제거
            del self.agents[agent_id]
            del self.agent_proxies[agent_id]

            # 능력 인덱스에서 제거
            self._remove_from_capabilities(agent_id)

            # 영구 저장소에서 제거
            await self._remove_persisted_agent(agent_id)

            # 등록 해제 이벤트 발행
            await self.event_bus.publish(
                OrchestratorEvent(
                    event_type="agent.unregistered",
                    source="agent_registry",
                    timestamp=datetime.utcnow(),
                    data={"agent_id": agent_id}
                )
            )

            logger.info(f"Agent unregistered: {agent_id}")

        return True

    async def get_agent(
        self,
        agent_type: str,
        version: Optional[str] = None
    ) -> AgentInterface:
        """에이전트 프록시 가져오기"""
        candidates = []

        async with self.registry_lock:
            for agent_id, agent_info in self.agents.items():
                if agent_info.type == agent_type:
                    if version is None or agent_info.version == version:
                        if agent_info.status == "healthy":
                            candidates.append(agent_id)

        if not candidates:
            raise AgentNotFoundError(
                f"No healthy agent found for type: {agent_type}"
            )

        # 로드 밸런싱 (라운드 로빈)
        selected_id = await self._select_agent(candidates)

        return self.agent_proxies[selected_id]

    async def find_agents_by_capability(
        self,
        capability_name: str
    ) -> List[AgentInfo]:
        """능력으로 에이전트 찾기"""
        agent_ids = self.agent_capabilities.get(capability_name, [])

        agents = []
        async with self.registry_lock:
            for agent_id in agent_ids:
                if agent_id in self.agents:
                    agents.append(self.agents[agent_id])

        return agents

    async def get_all_agents(
        self,
        agent_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[AgentInfo]:
        """전체 에이전트 목록"""
        agents = []

        async with self.registry_lock:
            for agent_info in self.agents.values():
                if agent_type and agent_info.type != agent_type:
                    continue
                if status and agent_info.status != status:
                    continue
                agents.append(agent_info)

        return agents

    def _index_capabilities(self, agent_info: AgentInfo):
        """에이전트 능력 인덱싱"""
        for capability in agent_info.capabilities:
            if capability.name not in self.agent_capabilities:
                self.agent_capabilities[capability.name] = []
            self.agent_capabilities[capability.name].append(agent_info.id)

    async def _discovery_loop(self):
        """에이전트 디스커버리 루프"""
        while True:
            try:
                await asyncio.sleep(self.discovery_interval)

                # 새로운 에이전트 탐색
                discovered = await self.discovery_service.discover_agents()

                for agent_info in discovered:
                    if agent_info.id not in self.agents:
                        await self.register_agent(agent_info)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Discovery error: {e}")
```

**검증 기준**:

- [ ] 에이전트 등록/해제
- [ ] 능력 기반 검색
- [ ] 자동 디스커버리
- [ ] 로드 밸런싱

#### SubTask 5.3.2: 에이전트 헬스 체크 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/orchestration/agent/health_check.py
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta

@dataclass
class HealthStatus:
    agent_id: str
    status: str  # healthy, unhealthy, degraded
    last_check: datetime
    response_time: float
    error_count: int
    consecutive_failures: int
    details: Dict[str, Any]

class HealthCheckManager:
    """에이전트 헬스 체크 관리자"""

    def __init__(
        self,
        registry: AgentRegistry,
        event_bus: EventBus
    ):
        self.registry = registry
        self.event_bus = event_bus

        # 헬스 체크 설정
        self.check_interval = 10  # seconds
        self.timeout = 5  # seconds
        self.failure_threshold = 3
        self.recovery_threshold = 2

        # 상태 추적
        self.health_status: Dict[str, HealthStatus] = {}
        self.check_tasks: Dict[str, asyncio.Task] = {}

    async def start(self):
        """헬스 체크 시작"""
        # 모든 에이전트에 대해 헬스 체크 시작
        agents = await self.registry.get_all_agents()

        for agent in agents:
            await self.start_health_check(agent.id)

    async def stop(self):
        """헬스 체크 중지"""
        # 모든 헬스 체크 태스크 취소
        for task in self.check_tasks.values():
            task.cancel()

    async def start_health_check(self, agent_id: str):
        """특정 에이전트 헬스 체크 시작"""
        if agent_id in self.check_tasks:
            return

        # 초기 상태
        self.health_status[agent_id] = HealthStatus(
            agent_id=agent_id,
            status="unknown",
            last_check=datetime.utcnow(),
            response_time=0.0,
            error_count=0,
            consecutive_failures=0,
            details={}
        )

        # 헬스 체크 태스크 시작
        task = asyncio.create_task(
            self._health_check_loop(agent_id)
        )
        self.check_tasks[agent_id] = task

    async def stop_health_check(self, agent_id: str):
        """특정 에이전트 헬스 체크 중지"""
        if agent_id in self.check_tasks:
            self.check_tasks[agent_id].cancel()
            del self.check_tasks[agent_id]
            del self.health_status[agent_id]

    async def _health_check_loop(self, agent_id: str):
        """헬스 체크 루프"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                await self._perform_health_check(agent_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error for {agent_id}: {e}")

    async def _perform_health_check(self, agent_id: str):
        """헬스 체크 수행"""
        agent_info = self.registry.agents.get(agent_id)
        if not agent_info:
            return

        proxy = self.registry.agent_proxies.get(agent_id)
        if not proxy:
            return

        status = self.health_status[agent_id]
        start_time = datetime.utcnow()

        try:
            # 헬스 체크 호출
            result = await asyncio.wait_for(
                proxy.health_check(),
                timeout=self.timeout
            )

            # 응답 시간 계산
            response_time = (datetime.utcnow() - start_time).total_seconds()

            # 상태 업데이트
            status.last_check = datetime.utcnow()
            status.response_time = response_time
            status.details = result

            # 헬스 상태 결정
            if result.get("status") == "healthy":
                await self._handle_healthy_response(agent_id, status)
            else:
                await self._handle_unhealthy_response(agent_id, status, result)

        except asyncio.TimeoutError:
            await self._handle_timeout(agent_id, status)
        except Exception as e:
            await self._handle_error(agent_id, status, e)

    async def _handle_healthy_response(
        self,
        agent_id: str,
        status: HealthStatus
    ):
        """정상 응답 처리"""
        previous_status = status.status

        if status.consecutive_failures > 0:
            # 복구 중
            status.consecutive_failures = 0
            status.error_count = max(0, status.error_count - 1)

            if status.error_count <= self.recovery_threshold:
                status.status = "healthy"

                # 복구 이벤트
                if previous_status != "healthy":
                    await self._emit_health_event(
                        agent_id,
                        "agent.recovered",
                        status
                    )
        else:
            status.status = "healthy"

        # 에이전트 상태 업데이트
        await self._update_agent_status(agent_id, "healthy")

    async def _handle_unhealthy_response(
        self,
        agent_id: str,
        status: HealthStatus,
        result: Dict[str, Any]
    ):
        """비정상 응답 처리"""
        status.consecutive_failures += 1
        status.error_count += 1

        if status.consecutive_failures >= self.failure_threshold:
            status.status = "unhealthy"
            await self._update_agent_status(agent_id, "unhealthy")

            # 장애 이벤트
            await self._emit_health_event(
                agent_id,
                "agent.unhealthy",
                status
            )
        else:
            status.status = "degraded"
            await self._update_agent_status(agent_id, "degraded")
```

**검증 기준**:

- [ ] 주기적 헬스 체크
- [ ] 장애 감지 및 복구
- [ ] 상태 전이 관리
- [ ] 이벤트 발행

#### SubTask 5.3.3: 동적 에이전트 스케일링

**담당자**: 인프라 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/orchestration/agent/auto_scaling.py
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta

@dataclass
class ScalingPolicy:
    agent_type: str
    min_instances: int
    max_instances: int
    target_cpu_percent: float
    target_memory_percent: float
    target_queue_depth: int
    scale_up_threshold: float
    scale_down_threshold: float
    cooldown_seconds: int

@dataclass
class ScalingDecision:
    agent_type: str
    current_instances: int
    desired_instances: int
    reason: str
    metrics: Dict[str, float]

class AutoScaler:
    """에이전트 자동 스케일링"""

    def __init__(
        self,
        registry: AgentRegistry,
        metrics_collector: MetricsCollector,
        infrastructure_manager: InfrastructureManager
    ):
        self.registry = registry
        self.metrics_collector = metrics_collector
        self.infrastructure = infrastructure_manager

        # 스케일링 정책
        self.policies: Dict[str, ScalingPolicy] = {}

        # 스케일링 상태
        self.last_scaling: Dict[str, datetime] = {}
        self.scaling_lock = asyncio.Lock()

        # 모니터링
        self.check_interval = 30  # seconds
        self.monitoring_task = None

    async def start(self):
        """자동 스케일링 시작"""
        # 정책 로드
        await self._load_scaling_policies()

        # 모니터링 시작
        self.monitoring_task = asyncio.create_task(
            self._scaling_loop()
        )

    async def stop(self):
        """자동 스케일링 중지"""
        if self.monitoring_task:
            self.monitoring_task.cancel()

    async def set_policy(
        self,
        agent_type: str,
        policy: ScalingPolicy
    ):
        """스케일링 정책 설정"""
        self.policies[agent_type] = policy
        await self._persist_policy(agent_type, policy)

    async def _scaling_loop(self):
        """스케일링 모니터링 루프"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)

                # 각 에이전트 타입별 확인
                for agent_type, policy in self.policies.items():
                    await self._check_and_scale(agent_type, policy)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scaling loop error: {e}")

    async def _check_and_scale(
        self,
        agent_type: str,
        policy: ScalingPolicy
    ):
        """스케일링 필요성 확인 및 실행"""
        # 쿨다운 확인
        if not self._is_cooldown_expired(agent_type, policy):
            return

        # 현재 메트릭 수집
        metrics = await self._collect_metrics(agent_type)

        # 현재 인스턴스 수
        current_instances = await self._count_instances(agent_type)

        # 스케일링 결정
        decision = self._make_scaling_decision(
            policy,
            current_instances,
            metrics
        )

        # 스케일링 실행
        if decision.desired_instances != current_instances:
            await self._execute_scaling(decision)

    async def _collect_metrics(
        self,
        agent_type: str
    ) -> Dict[str, float]:
        """에이전트 메트릭 수집"""
        agents = await self.registry.get_all_agents(
            agent_type=agent_type,
            status="healthy"
        )

        if not agents:
            return {}

        # 집계 메트릭
        total_cpu = 0.0
        total_memory = 0.0
        total_queue_depth = 0

        for agent in agents:
            agent_metrics = await self.metrics_collector.get_agent_metrics(
                agent.id
            )

            total_cpu += agent_metrics.get("cpu_percent", 0)
            total_memory += agent_metrics.get("memory_percent", 0)
            total_queue_depth += agent_metrics.get("queue_depth", 0)

        # 평균 계산
        avg_cpu = total_cpu / len(agents)
        avg_memory = total_memory / len(agents)

        return {
            "cpu_percent": avg_cpu,
            "memory_percent": avg_memory,
            "queue_depth": total_queue_depth,
            "instance_count": len(agents)
        }

    def _make_scaling_decision(
        self,
        policy: ScalingPolicy,
        current_instances: int,
        metrics: Dict[str, float]
    ) -> ScalingDecision:
        """스케일링 결정"""
        desired_instances = current_instances
        reason = "No scaling needed"

        # CPU 기반 스케일링
        if metrics.get("cpu_percent", 0) > policy.scale_up_threshold:
            desired_instances = min(
                current_instances + 1,
                policy.max_instances
            )
            reason = f"High CPU usage: {metrics['cpu_percent']:.1f}%"

        elif metrics.get("cpu_percent", 100) < policy.scale_down_threshold:
            if current_instances > policy.min_instances:
                desired_instances = current_instances - 1
                reason = f"Low CPU usage: {metrics['cpu_percent']:.1f}%"

        # 큐 깊이 기반 스케일링
        queue_depth = metrics.get("queue_depth", 0)
        if queue_depth > policy.target_queue_depth * 1.5:
            desired_instances = min(
                current_instances + 1,
                policy.max_instances
            )
            reason = f"High queue depth: {queue_depth}"

        return ScalingDecision(
            agent_type=policy.agent_type,
            current_instances=current_instances,
            desired_instances=desired_instances,
            reason=reason,
            metrics=metrics
        )

    async def _execute_scaling(self, decision: ScalingDecision):
        """스케일링 실행"""
        async with self.scaling_lock:
            diff = decision.desired_instances - decision.current_instances

            if diff > 0:
                # 스케일 업
                await self._scale_up(decision.agent_type, diff)
            else:
                # 스케일 다운
                await self._scale_down(decision.agent_type, abs(diff))

            # 마지막 스케일링 시간 기록
            self.last_scaling[decision.agent_type] = datetime.utcnow()

            # 스케일링 이벤트 발행
            await self.event_bus.publish(
                OrchestratorEvent(
                    event_type="agent.scaled",
                    source="auto_scaler",
                    timestamp=datetime.utcnow(),
                    data={
                        "agent_type": decision.agent_type,
                        "from_instances": decision.current_instances,
                        "to_instances": decision.desired_instances,
                        "reason": decision.reason
                    }
                )
            )
```

**검증 기준**:

- [ ] 메트릭 기반 스케일링
- [ ] 정책 관리
- [ ] 쿨다운 메커니즘
- [ ] 인프라 통합

#### SubTask 5.3.4: 에이전트 버전 관리

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/orchestration/agent/version_manager.py
from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime
import semver

@dataclass
class AgentVersion:
    agent_type: str
    version: str
    release_date: datetime
    changelog: str
    compatibility: Dict[str, str]  # dependency -> version
    deprecated: bool = False
    end_of_life: Optional[datetime] = None

@dataclass
class DeploymentStrategy:
    strategy_type: str  # canary, blue-green, rolling
    canary_percent: Optional[int] = None
    rollback_threshold: Optional[float] = None
    health_check_interval: int = 30

class VersionManager:
    """에이전트 버전 관리"""

    def __init__(
        self,
        registry: AgentRegistry,
        deployment_manager: DeploymentManager
    ):
        self.registry = registry
        self.deployment_manager = deployment_manager

        # 버전 정보
        self.versions: Dict[str, List[AgentVersion]] = {}
        self.active_deployments: Dict[str, DeploymentStatus] = {}

        # 동기화
        self.deployment_lock = asyncio.Lock()

    async def register_version(
        self,
        agent_type: str,
        version: AgentVersion
    ):
        """새 버전 등록"""
        if agent_type not in self.versions:
            self.versions[agent_type] = []

        # 버전 유효성 검증
        self._validate_version(version)

        # 호환성 확인
        await self._check_compatibility(agent_type, version)

        # 버전 추가
        self.versions[agent_type].append(version)
        self.versions[agent_type].sort(
            key=lambda v: semver.VersionInfo.parse(v.version),
            reverse=True
        )

        logger.info(
            f"Registered version {version.version} for {agent_type}"
        )

    async def deploy_version(
        self,
        agent_type: str,
        target_version: str,
        strategy: DeploymentStrategy
    ) -> str:
        """버전 배포"""
        async with self.deployment_lock:
            # 현재 버전 확인
            current_version = await self._get_current_version(agent_type)

            if current_version == target_version:
                raise ValueError("Target version is already deployed")

            # 배포 계획 생성
            deployment_plan = await self._create_deployment_plan(
                agent_type,
                current_version,
                target_version,
                strategy
            )

            # 배포 실행
            deployment_id = await self._execute_deployment(
                deployment_plan
            )

            return deployment_id

    async def rollback_version(
        self,
        agent_type: str,
        target_version: Optional[str] = None
    ):
        """버전 롤백"""
        async with self.deployment_lock:
            # 이전 안정 버전 찾기
            if not target_version:
                target_version = await self._find_last_stable_version(
                    agent_type
                )

            if not target_version:
                raise ValueError("No stable version found for rollback")

            # 롤백 실행
            await self._execute_rollback(agent_type, target_version)

    async def _create_deployment_plan(
        self,
        agent_type: str,
        current_version: str,
        target_version: str,
        strategy: DeploymentStrategy
    ) -> DeploymentPlan:
        """배포 계획 생성"""
        plan = DeploymentPlan(
            agent_type=agent_type,
            from_version=current_version,
            to_version=target_version,
            strategy=strategy,
            steps=[]
        )

        if strategy.strategy_type == "canary":
            plan.steps = self._create_canary_steps(
                agent_type,
                target_version,
                strategy.canary_percent
            )
        elif strategy.strategy_type == "blue-green":
            plan.steps = self._create_blue_green_steps(
                agent_type,
                target_version
            )
        elif strategy.strategy_type == "rolling":
            plan.steps = self._create_rolling_steps(
                agent_type,
                target_version
            )

        return plan

    def _create_canary_steps(
        self,
        agent_type: str,
        target_version: str,
        canary_percent: int
    ) -> List[DeploymentStep]:
        """카나리 배포 단계 생성"""
        return [
            DeploymentStep(
                name="Deploy canary instances",
                action="deploy_percent",
                parameters={
                    "version": target_version,
                    "percent": canary_percent
                }
            ),
            DeploymentStep(
                name="Monitor canary health",
                action="monitor",
                parameters={
                    "duration_seconds": 300,
                    "metrics": ["error_rate", "response_time"]
                }
            ),
            DeploymentStep(
                name="Evaluate canary",
                action="evaluate",
                parameters={
                    "threshold": 0.95,
                    "rollback_on_failure": True
                }
            ),
            DeploymentStep(
                name="Promote canary",
                action="promote",
                parameters={
                    "version": target_version
                }
            )
        ]

    async def _check_version_health(
        self,
        agent_type: str,
        version: str
    ) -> VersionHealth:
        """버전 건강 상태 확인"""
        agents = await self.registry.get_all_agents(
            agent_type=agent_type
        )

        version_agents = [
            a for a in agents
            if a.version == version
        ]

        if not version_agents:
            return VersionHealth(
                version=version,
                healthy_count=0,
                total_count=0,
                error_rate=0.0,
                avg_response_time=0.0
            )

        # 건강한 에이전트 수
        healthy_count = len([
            a for a in version_agents
            if a.status == "healthy"
        ])

        # 메트릭 수집
        total_errors = 0
        total_requests = 0
        total_response_time = 0

        for agent in version_agents:
            metrics = await self.metrics_collector.get_agent_metrics(
                agent.id,
                time_range=timedelta(minutes=5)
            )

            total_errors += metrics.get("error_count", 0)
            total_requests += metrics.get("request_count", 0)
            total_response_time += metrics.get("total_response_time", 0)

        error_rate = total_errors / total_requests if total_requests > 0 else 0
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0

        return VersionHealth(
            version=version,
            healthy_count=healthy_count,
            total_count=len(version_agents),
            error_rate=error_rate,
            avg_response_time=avg_response_time
        )
```

**검증 기준**:

- [ ] 버전 등록 및 관리
- [ ] 배포 전략 구현 (Canary/Blue-Green/Rolling)
- [ ] 버전 호환성 검증
- [ ] 롤백 메커니즘

---

# Phase 5: 오케스트레이션 시스템 - Tasks 5.4~5.6 SubTask 구조

## 📋 Task 5.4~5.6 SubTask 리스트

### Task 5.4: 워크플로우 정의 언어 (DSL) 구현

- **SubTask 5.4.1**: DSL 문법 설계 및 명세
- **SubTask 5.4.2**: DSL 파서 및 컴파일러 구현
- **SubTask 5.4.3**: DSL 검증기 및 타입 시스템
- **SubTask 5.4.4**: DSL IDE 지원 및 도구

### Task 5.5: 동적 워크플로우 생성 및 수정

- **SubTask 5.5.1**: 런타임 워크플로우 빌더
- **SubTask 5.5.2**: 워크플로우 수정 API
- **SubTask 5.5.3**: 동적 분기 및 조건부 실행
- **SubTask 5.5.4**: 워크플로우 버전 관리

### Task 5.6: 워크플로우 템플릿 및 재사용 시스템

- **SubTask 5.6.1**: 템플릿 저장소 구축
- **SubTask 5.6.2**: 템플릿 파라미터화 시스템
- **SubTask 5.6.3**: 템플릿 상속 및 확장 메커니즘
- **SubTask 5.6.4**: 템플릿 공유 마켓플레이스

---

## 📝 세부 작업지시서

### Task 5.4: 워크플로우 정의 언어 (DSL) 구현

#### SubTask 5.4.1: DSL 문법 설계 및 명세

**담당자**: 언어 설계 전문가  
**예상 소요시간**: 16시간

**작업 내용**:

```typescript
// backend/src/orchestration/dsl/grammar.ts
export interface DSLGrammar {
  version: string;
  keywords: string[];
  operators: string[];
  types: string[];
  builtins: string[];
}

// T-Developer Workflow DSL (TWDSL) 문법 정의
export const TWDSLGrammar: DSLGrammar = {
  version: "1.0.0",
  keywords: [
    "workflow",
    "task",
    "parallel",
    "sequence",
    "if",
    "else",
    "while",
    "foreach",
    "input",
    "output",
    "depends",
    "timeout",
    "retry",
    "on_error",
    "on_success",
    "import",
    "export",
    "template",
  ],
  operators: [
    "->",
    "=>",
    "==",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
    "&&",
    "||",
    "!",
    "+",
    "-",
    "*",
    "/",
    "%",
    "=",
    ".",
  ],
  types: [
    "string",
    "number",
    "boolean",
    "object",
    "array",
    "any",
    "datetime",
    "duration",
    "file",
    "url",
  ],
  builtins: [
    "env",
    "context",
    "result",
    "error",
    "retry_count",
    "current_time",
    "workflow_id",
    "task_id",
  ],
};

// DSL 예제
const dslExample = `
workflow CreateFullStackApp {
  version: "1.0.0"
  description: "Full-stack application generation workflow"
  
  input {
    project_name: string
    tech_stack: {
      frontend: string
      backend: string
      database: string
    }
    features: array<string>
  }
  
  output {
    project_url: string
    documentation_url: string
    deployment_status: string
  }
  
  // 병렬 실행 블록
  parallel {
    // Frontend 생성
    task generateFrontend {
      agent: "UISelectionAgent"
      input: {
        framework: tech_stack.frontend
        features: features.filter(f => f.startsWith("ui_"))
      }
      timeout: 5m
      retry: 3
    }
    
    // Backend 생성
    task generateBackend {
      agent: "BackendAgent"
      input: {
        framework: tech_stack.backend
        database: tech_stack.database
        features: features.filter(f => f.startsWith("api_"))
      }
      timeout: 10m
    }
  }
  
  // 순차 실행
  sequence {
    // 통합 테스트
    task runIntegrationTests {
      agent: "TestAgent"
      depends: [generateFrontend, generateBackend]
      input: {
        frontend_output: generateFrontend.result
        backend_output: generateBackend.result
      }
      on_error: {
        retry: 2
        fallback: skipTests
      }
    }
    
    // 조건부 배포
    if (runIntegrationTests.result.passed) {
      task deployApplication {
        agent: "DeploymentAgent"
        input: {
          frontend: generateFrontend.result.build_path
          backend: generateBackend.result.build_path
        }
      }
    } else {
      task notifyFailure {
        agent: "NotificationAgent"
        input: {
          message: "Integration tests failed"
          details: runIntegrationTests.result.errors
        }
      }
    }
  }
  
  // 반복 실행
  foreach feature in features {
    task generateFeatureTests {
      agent: "TestGenerationAgent"
      input: {
        feature_name: feature
        project_context: context
      }
    }
  }
}
`;

// DSL 언어 명세
export class DSLSpecification {
  // 구문 규칙
  syntaxRules = {
    workflow: {
      pattern: /workflow\s+(\w+)\s*{/,
      required: ["version", "input", "output"],
      optional: ["description", "timeout", "on_error"],
    },
    task: {
      pattern: /task\s+(\w+)\s*{/,
      required: ["agent"],
      optional: [
        "input",
        "depends",
        "timeout",
        "retry",
        "on_error",
        "on_success",
      ],
    },
    parallel: {
      pattern: /parallel\s*{/,
      children: ["task", "sequence", "if", "foreach"],
    },
    sequence: {
      pattern: /sequence\s*{/,
      children: ["task", "parallel", "if", "foreach", "while"],
    },
    conditional: {
      pattern: /if\s*\((.*?)\)\s*{/,
      elseBranch: /else\s*{/,
    },
    loop: {
      foreach: /foreach\s+(\w+)\s+in\s+(.*?)\s*{/,
      while: /while\s*\((.*?)\)\s*{/,
    },
  };

  // 타입 시스템
  typeSystem = {
    primitives: ["string", "number", "boolean", "null"],
    complex: ["object", "array"],
    custom: ["datetime", "duration", "file", "url"],

    typeInference: {
      string: /^["'].*["']$/,
      number: /^-?\d+(\.\d+)?$/,
      boolean: /^(true|false)$/,
      null: /^null$/,
      array: /^\[.*\]$/,
      object: /^{.*}$/,
    },
  };

  // 표현식 평가 규칙
  expressionRules = {
    // 변수 참조
    variableRef: /(\w+)\.(\w+)/,

    // 함수 호출
    functionCall: /(\w+)\((.*?)\)/,

    // 연산자 우선순위
    operatorPrecedence: {
      "||": 1,
      "&&": 2,
      "==": 3,
      "!=": 3,
      ">": 4,
      "<": 4,
      ">=": 4,
      "<=": 4,
      "+": 5,
      "-": 5,
      "*": 6,
      "/": 6,
      "%": 6,
      "!": 7,
      ".": 8,
    },
  };
}
```

**검증 기준**:

- [ ] 완전한 DSL 문법 명세
- [ ] 타입 시스템 정의
- [ ] 표현식 평가 규칙
- [ ] 예제 및 문서화

#### SubTask 5.4.2: DSL 파서 및 컴파일러 구현

**담당자**: 컴파일러 개발자  
**예상 소요시간**: 20시간

**작업 내용**:

```typescript
// backend/src/orchestration/dsl/parser.ts
import { Lexer, Token } from "./lexer";
import { ASTNode, WorkflowAST } from "./ast";

export class DSLParser {
  private lexer: Lexer;
  private currentToken: Token;
  private position: number = 0;

  constructor(private source: string) {
    this.lexer = new Lexer(source);
  }

  // 메인 파싱 함수
  parse(): WorkflowAST {
    const tokens = this.lexer.tokenize();
    this.position = 0;
    this.currentToken = tokens[0];

    const workflow = this.parseWorkflow();

    if (this.position < tokens.length - 1) {
      throw new ParseError(
        `Unexpected token: ${this.currentToken.value}`,
        this.currentToken.line,
        this.currentToken.column
      );
    }

    return workflow;
  }

  // 워크플로우 파싱
  private parseWorkflow(): WorkflowAST {
    this.expect("workflow");
    const name = this.expectIdentifier();
    this.expect("{");

    const workflow: WorkflowAST = {
      type: "workflow",
      name,
      version: "",
      description: "",
      input: {},
      output: {},
      body: [],
    };

    while (!this.check("}")) {
      if (this.match("version")) {
        this.expect(":");
        workflow.version = this.expectString();
      } else if (this.match("description")) {
        this.expect(":");
        workflow.description = this.expectString();
      } else if (this.match("input")) {
        workflow.input = this.parseInputOutput();
      } else if (this.match("output")) {
        workflow.output = this.parseInputOutput();
      } else {
        // 워크플로우 바디 파싱
        workflow.body.push(this.parseStatement());
      }
    }

    this.expect("}");
    return workflow;
  }

  // 문장 파싱
  private parseStatement(): ASTNode {
    if (this.match("task")) {
      return this.parseTask();
    } else if (this.match("parallel")) {
      return this.parseParallel();
    } else if (this.match("sequence")) {
      return this.parseSequence();
    } else if (this.match("if")) {
      return this.parseConditional();
    } else if (this.match("foreach")) {
      return this.parseForeach();
    } else if (this.match("while")) {
      return this.parseWhile();
    } else {
      throw new ParseError(
        `Unexpected statement: ${this.currentToken.value}`,
        this.currentToken.line,
        this.currentToken.column
      );
    }
  }

  // 태스크 파싱
  private parseTask(): ASTNode {
    const name = this.expectIdentifier();
    this.expect("{");

    const task: TaskAST = {
      type: "task",
      name,
      agent: "",
      input: {},
      depends: [],
      timeout: null,
      retry: null,
      onError: null,
      onSuccess: null,
    };

    while (!this.check("}")) {
      if (this.match("agent")) {
        this.expect(":");
        task.agent = this.expectString();
      } else if (this.match("input")) {
        this.expect(":");
        task.input = this.parseExpression();
      } else if (this.match("depends")) {
        this.expect(":");
        task.depends = this.parseArray();
      } else if (this.match("timeout")) {
        this.expect(":");
        task.timeout = this.parseDuration();
      } else if (this.match("retry")) {
        this.expect(":");
        task.retry = this.expectNumber();
      } else if (this.match("on_error")) {
        task.onError = this.parseErrorHandler();
      } else if (this.match("on_success")) {
        task.onSuccess = this.parseSuccessHandler();
      }
    }

    this.expect("}");
    return task;
  }

  // 표현식 파싱
  private parseExpression(): ASTNode {
    return this.parseOrExpression();
  }

  private parseOrExpression(): ASTNode {
    let left = this.parseAndExpression();

    while (this.match("||")) {
      const operator = this.previous();
      const right = this.parseAndExpression();
      left = {
        type: "binary",
        operator: operator.value,
        left,
        right,
      };
    }

    return left;
  }

  // ... 추가 파싱 메서드들
}

// DSL 컴파일러
export class DSLCompiler {
  constructor(private optimizer: DSLOptimizer) {}

  // AST를 실행 가능한 워크플로우로 컴파일
  compile(ast: WorkflowAST): CompiledWorkflow {
    // 1. 의미 분석
    const analyzed = this.semanticAnalysis(ast);

    // 2. 최적화
    const optimized = this.optimizer.optimize(analyzed);

    // 3. 중간 표현(IR) 생성
    const ir = this.generateIR(optimized);

    // 4. 코드 생성
    const code = this.generateCode(ir);

    return {
      id: this.generateWorkflowId(ast.name),
      name: ast.name,
      version: ast.version,
      compiledAt: new Date(),
      code,
      metadata: this.extractMetadata(ast),
    };
  }

  // 의미 분석
  private semanticAnalysis(ast: WorkflowAST): AnalyzedAST {
    const analyzer = new SemanticAnalyzer();

    // 타입 검사
    analyzer.checkTypes(ast);

    // 변수 스코프 분석
    analyzer.analyzeScopes(ast);

    // 의존성 분석
    analyzer.analyzeDependencies(ast);

    // 도달 가능성 분석
    analyzer.checkReachability(ast);

    return analyzer.getAnalyzedAST();
  }

  // 중간 표현 생성
  private generateIR(ast: AnalyzedAST): IntermediateRepresentation {
    const irGenerator = new IRGenerator();

    // 기본 블록 생성
    const blocks = irGenerator.createBasicBlocks(ast);

    // 제어 흐름 그래프 생성
    const cfg = irGenerator.createControlFlowGraph(blocks);

    // 데이터 흐름 분석
    const dataFlow = irGenerator.analyzeDataFlow(cfg);

    return {
      blocks,
      cfg,
      dataFlow,
      symbols: irGenerator.getSymbolTable(),
    };
  }

  // 실행 코드 생성
  private generateCode(ir: IntermediateRepresentation): ExecutableCode {
    const codeGen = new CodeGenerator();

    // 워크플로우 정의 생성
    const workflowDef = codeGen.generateWorkflowDefinition(ir);

    // 태스크 정의 생성
    const taskDefs = codeGen.generateTaskDefinitions(ir);

    // 런타임 헬퍼 생성
    const helpers = codeGen.generateHelpers(ir);

    return {
      workflow: workflowDef,
      tasks: taskDefs,
      helpers,
      entryPoint: codeGen.getEntryPoint(),
    };
  }
}

// DSL 최적화기
export class DSLOptimizer {
  optimize(ast: AnalyzedAST): OptimizedAST {
    // 1. 죽은 코드 제거
    this.removeDeadCode(ast);

    // 2. 상수 폴딩
    this.constantFolding(ast);

    // 3. 공통 부분식 제거
    this.commonSubexpressionElimination(ast);

    // 4. 병렬화 기회 식별
    this.identifyParallelization(ast);

    // 5. 태스크 병합
    this.mergeCompatibleTasks(ast);

    return ast as OptimizedAST;
  }

  private removeDeadCode(ast: AnalyzedAST): void {
    // 도달 불가능한 태스크 제거
    const visitor = new ASTVisitor();

    visitor.visitWorkflow(ast, (node) => {
      if (node.type === "task" && !node.reachable) {
        // 부모 노드에서 제거
        this.removeNode(ast, node);
      }
    });
  }

  private identifyParallelization(ast: AnalyzedAST): void {
    // 독립적인 태스크 찾기
    const dependencyGraph = this.buildDependencyGraph(ast);
    const independentTasks = this.findIndependentTasks(dependencyGraph);

    // 병렬 블록으로 그룹화
    for (const group of independentTasks) {
      if (group.length > 1) {
        this.wrapInParallelBlock(ast, group);
      }
    }
  }
}
```

**검증 기준**:

- [ ] 완전한 파서 구현
- [ ] AST 생성 및 변환
- [ ] 의미 분석 및 타입 검사
- [ ] 코드 생성 및 최적화

#### SubTask 5.4.3: DSL 검증기 및 타입 시스템

**담당자**: 타입 시스템 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/orchestration/dsl/validator.ts
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  hints: ValidationHint[];
}

export class DSLValidator {
  private typeChecker: TypeChecker;
  private dependencyChecker: DependencyChecker;
  private semanticChecker: SemanticChecker;

  constructor() {
    this.typeChecker = new TypeChecker();
    this.dependencyChecker = new DependencyChecker();
    this.semanticChecker = new SemanticChecker();
  }

  async validate(source: string): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    const hints: ValidationHint[] = [];

    try {
      // 1. 렉싱 검증
      const lexer = new Lexer(source);
      const tokens = lexer.tokenize();

      // 2. 파싱 검증
      const parser = new DSLParser(source);
      const ast = parser.parse();

      // 3. 타입 검증
      const typeErrors = await this.typeChecker.check(ast);
      errors.push(...typeErrors);

      // 4. 의존성 검증
      const depResult = await this.dependencyChecker.check(ast);
      errors.push(...depResult.errors);
      warnings.push(...depResult.warnings);

      // 5. 의미적 검증
      const semanticResult = await this.semanticChecker.check(ast);
      errors.push(...semanticResult.errors);
      warnings.push(...semanticResult.warnings);
      hints.push(...semanticResult.hints);

      // 6. 모범 사례 검증
      const bestPractices = await this.checkBestPractices(ast);
      hints.push(...bestPractices);
    } catch (e) {
      if (e instanceof ParseError) {
        errors.push({
          type: "parse_error",
          message: e.message,
          line: e.line,
          column: e.column,
          severity: "error",
        });
      } else {
        errors.push({
          type: "unknown_error",
          message: e.message,
          severity: "error",
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      hints,
    };
  }

  private async checkBestPractices(
    ast: WorkflowAST
  ): Promise<ValidationHint[]> {
    const hints: ValidationHint[] = [];

    // 태스크 수 확인
    const taskCount = this.countTasks(ast);
    if (taskCount > 50) {
      hints.push({
        type: "complexity",
        message:
          "Consider breaking down the workflow into smaller sub-workflows",
        severity: "hint",
      });
    }

    // 중복 코드 감지
    const duplicates = this.findDuplicatePatterns(ast);
    for (const dup of duplicates) {
      hints.push({
        type: "duplication",
        message: `Consider extracting repeated pattern into a template: ${dup.pattern}`,
        severity: "hint",
      });
    }

    return hints;
  }
}

// 타입 체커
export class TypeChecker {
  private typeEnvironment: TypeEnvironment;
  private inferenceEngine: TypeInferenceEngine;

  constructor() {
    this.typeEnvironment = new TypeEnvironment();
    this.inferenceEngine = new TypeInferenceEngine();
  }

  async check(ast: WorkflowAST): Promise<ValidationError[]> {
    const errors: ValidationError[] = [];

    // 글로벌 타입 환경 초기화
    this.initializeGlobalTypes();

    // 입출력 타입 등록
    this.registerIOTypes(ast);

    // AST 순회하며 타입 검사
    const visitor = new TypeCheckVisitor(this.typeEnvironment);

    visitor.on("type_error", (error) => {
      errors.push(error);
    });

    visitor.visit(ast);

    return errors;
  }

  private initializeGlobalTypes(): void {
    // 내장 타입 등록
    this.typeEnvironment.registerType("string", PrimitiveType.String);
    this.typeEnvironment.registerType("number", PrimitiveType.Number);
    this.typeEnvironment.registerType("boolean", PrimitiveType.Boolean);

    // 복합 타입
    this.typeEnvironment.registerType("array", new ArrayType());
    this.typeEnvironment.registerType("object", new ObjectType());

    // 커스텀 타입
    this.typeEnvironment.registerType("datetime", new DateTimeType());
    this.typeEnvironment.registerType("duration", new DurationType());
  }
}

// 타입 추론 엔진
export class TypeInferenceEngine {
  infer(expression: ASTNode, context: TypeContext): Type {
    switch (expression.type) {
      case "literal":
        return this.inferLiteralType(expression);

      case "identifier":
        return this.inferIdentifierType(expression, context);

      case "binary":
        return this.inferBinaryType(expression, context);

      case "function_call":
        return this.inferFunctionType(expression, context);

      case "member_access":
        return this.inferMemberType(expression, context);

      default:
        return new AnyType();
    }
  }

  private inferLiteralType(literal: LiteralNode): Type {
    if (typeof literal.value === "string") {
      return PrimitiveType.String;
    } else if (typeof literal.value === "number") {
      return PrimitiveType.Number;
    } else if (typeof literal.value === "boolean") {
      return PrimitiveType.Boolean;
    } else if (literal.value === null) {
      return new NullType();
    } else if (Array.isArray(literal.value)) {
      return new ArrayType(this.inferArrayElementType(literal.value));
    } else if (typeof literal.value === "object") {
      return this.inferObjectType(literal.value);
    }

    return new AnyType();
  }
}

// 의존성 검사기
export class DependencyChecker {
  async check(ast: WorkflowAST): Promise<DependencyCheckResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // 의존성 그래프 구축
    const depGraph = this.buildDependencyGraph(ast);

    // 1. 순환 의존성 검사
    const cycles = this.findCycles(depGraph);
    for (const cycle of cycles) {
      errors.push({
        type: "circular_dependency",
        message: `Circular dependency detected: ${cycle.join(" -> ")}`,
        severity: "error",
      });
    }

    // 2. 미해결 의존성 검사
    const unresolved = this.findUnresolvedDependencies(ast, depGraph);
    for (const dep of unresolved) {
      errors.push({
        type: "unresolved_dependency",
        message: `Task '${dep.from}' depends on unknown task '${dep.to}'`,
        severity: "error",
      });
    }

    // 3. 도달 불가능한 태스크
    const unreachable = this.findUnreachableTasks(depGraph);
    for (const task of unreachable) {
      warnings.push({
        type: "unreachable_task",
        message: `Task '${task}' is unreachable`,
        severity: "warning",
      });
    }

    return { errors, warnings };
  }

  private buildDependencyGraph(ast: WorkflowAST): DependencyGraph {
    const graph = new DependencyGraph();

    const visitor = new DependencyVisitor();
    visitor.visit(ast, (task) => {
      graph.addNode(task.name);

      if (task.depends) {
        for (const dep of task.depends) {
          graph.addEdge(task.name, dep);
        }
      }
    });

    return graph;
  }
}
```

**검증 기준**:

- [ ] 종합적인 검증 시스템
- [ ] 타입 검사 및 추론
- [ ] 의존성 분석
- [ ] 모범 사례 검증

#### SubTask 5.4.4: DSL IDE 지원 및 도구

**담당자**: 도구 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/orchestration/dsl/language-server.ts
import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  CompletionItem,
  CompletionItemKind,
  TextDocumentPositionParams,
  Hover,
  Definition,
} from "vscode-languageserver/node";

export class TWDSLLanguageServer {
  private connection = createConnection(ProposedFeatures.all);
  private documents = new TextDocuments(TextDocument);
  private validator = new DSLValidator();
  private completionProvider = new CompletionProvider();
  private hoverProvider = new HoverProvider();

  constructor() {
    this.setupHandlers();
  }

  private setupHandlers(): void {
    // 초기화
    this.connection.onInitialize((params: InitializeParams) => {
      return {
        capabilities: {
          textDocumentSync: TextDocumentSyncKind.Incremental,
          completionProvider: {
            resolveProvider: true,
            triggerCharacters: [".", ":"],
          },
          hoverProvider: true,
          definitionProvider: true,
          documentFormattingProvider: true,
          codeActionProvider: true,
          signatureHelpProvider: {
            triggerCharacters: ["(", ","],
          },
        },
      };
    });

    // 자동 완성
    this.connection.onCompletion(
      async (params: TextDocumentPositionParams): Promise<CompletionItem[]> => {
        const document = this.documents.get(params.textDocument.uri);
        if (!document) return [];

        return this.completionProvider.provideCompletions(
          document,
          params.position
        );
      }
    );

    // 호버 정보
    this.connection.onHover(
      async (params: TextDocumentPositionParams): Promise<Hover | null> => {
        const document = this.documents.get(params.textDocument.uri);
        if (!document) return null;

        return this.hoverProvider.provideHover(document, params.position);
      }
    );

    // 문서 검증
    this.documents.onDidChangeContent(async (change) => {
      await this.validateDocument(change.document);
    });
  }

  private async validateDocument(document: TextDocument): Promise<void> {
    const text = document.getText();
    const result = await this.validator.validate(text);

    // 진단 정보 생성
    const diagnostics: Diagnostic[] = [];

    // 오류
    for (const error of result.errors) {
      diagnostics.push({
        severity: DiagnosticSeverity.Error,
        range: {
          start: { line: error.line - 1, character: error.column - 1 },
          end: { line: error.line - 1, character: error.column },
        },
        message: error.message,
        source: "twdsl",
      });
    }

    // 경고
    for (const warning of result.warnings) {
      diagnostics.push({
        severity: DiagnosticSeverity.Warning,
        range: {
          start: { line: warning.line - 1, character: warning.column - 1 },
          end: { line: warning.line - 1, character: warning.column },
        },
        message: warning.message,
        source: "twdsl",
      });
    }

    // 힌트
    for (const hint of result.hints) {
      diagnostics.push({
        severity: DiagnosticSeverity.Hint,
        range: {
          start: { line: hint.line - 1, character: hint.column - 1 },
          end: { line: hint.line - 1, character: hint.column },
        },
        message: hint.message,
        source: "twdsl",
      });
    }

    this.connection.sendDiagnostics({ uri: document.uri, diagnostics });
  }

  start(): void {
    this.documents.listen(this.connection);
    this.connection.listen();
  }
}

// 자동 완성 제공자
export class CompletionProvider {
  private keywords = TWDSLGrammar.keywords;
  private builtins = TWDSLGrammar.builtins;
  private agentTypes = [
    "NLInputAgent",
    "UISelectionAgent",
    "ParserAgent",
    "ComponentDecisionAgent",
    "MatchRateAgent",
    "SearchAgent",
    "GenerationAgent",
    "AssemblyAgent",
    "DownloadAgent",
  ];

  async provideCompletions(
    document: TextDocument,
    position: Position
  ): Promise<CompletionItem[]> {
    const context = this.getCompletionContext(document, position);
    const completions: CompletionItem[] = [];

    // 컨텍스트별 완성 항목
    switch (context.type) {
      case "workflow_body":
        completions.push(...this.getWorkflowBodyCompletions());
        break;

      case "task_body":
        completions.push(...this.getTaskBodyCompletions());
        break;

      case "agent_value":
        completions.push(...this.getAgentCompletions());
        break;

      case "expression":
        completions.push(...this.getExpressionCompletions(context));
        break;

      default:
        completions.push(...this.getGeneralCompletions());
    }

    return completions;
  }

  private getWorkflowBodyCompletions(): CompletionItem[] {
    return [
      {
        label: "task",
        kind: CompletionItemKind.Keyword,
        insertText: 'task ${1:taskName} {\n  agent: "${2:agentType}"\n  $0\n}',
        insertTextFormat: InsertTextFormat.Snippet,
        documentation: "Define a new task",
      },
      {
        label: "parallel",
        kind: CompletionItemKind.Keyword,
        insertText: "parallel {\n  $0\n}",
        insertTextFormat: InsertTextFormat.Snippet,
        documentation: "Execute tasks in parallel",
      },
      {
        label: "sequence",
        kind: CompletionItemKind.Keyword,
        insertText: "sequence {\n  $0\n}",
        insertTextFormat: InsertTextFormat.Snippet,
        documentation: "Execute tasks in sequence",
      },
      {
        label: "if",
        kind: CompletionItemKind.Keyword,
        insertText: "if (${1:condition}) {\n  $0\n}",
        insertTextFormat: InsertTextFormat.Snippet,
        documentation: "Conditional execution",
      },
    ];
  }

  private getAgentCompletions(): CompletionItem[] {
    return this.agentTypes.map((agent) => ({
      label: agent,
      kind: CompletionItemKind.Value,
      detail: `Agent type: ${agent}`,
      documentation: this.getAgentDocumentation(agent),
    }));
  }
}

// 포매터
export class DSLFormatter {
  private indentSize: number = 2;
  private indentChar: string = " ";

  format(source: string): string {
    const parser = new DSLParser(source);
    const ast = parser.parse();

    return this.formatAST(ast, 0);
  }

  private formatAST(node: ASTNode, indent: number): string {
    const indentStr = this.indentChar.repeat(indent * this.indentSize);

    switch (node.type) {
      case "workflow":
        return this.formatWorkflow(node as WorkflowAST, indent);

      case "task":
        return this.formatTask(node as TaskAST, indent);

      case "parallel":
        return this.formatParallel(node as ParallelAST, indent);

      // ... 기타 노드 타입

      default:
        return "";
    }
  }

  private formatWorkflow(workflow: WorkflowAST, indent: number): string {
    const ind = this.getIndent(indent);
    let result = `workflow ${workflow.name} {\n`;

    result += `${ind}  version: "${workflow.version}"\n`;

    if (workflow.description) {
      result += `${ind}  description: "${workflow.description}"\n`;
    }

    result += "\n";
    result += this.formatInputOutput("input", workflow.input, indent + 1);
    result += "\n";
    result += this.formatInputOutput("output", workflow.output, indent + 1);
    result += "\n";

    for (const stmt of workflow.body) {
      result += this.formatAST(stmt, indent + 1) + "\n";
    }

    result += `${ind}}`;
    return result;
  }
}

// 디버거 지원
export class DSLDebugAdapter {
  private breakpoints: Map<string, Breakpoint[]> = new Map();
  private runtime: DSLRuntime;

  async attach(workflowId: string): Promise<void> {
    this.runtime = await this.getRuntimeInstance(workflowId);

    this.runtime.on("taskStart", this.handleTaskStart.bind(this));
    this.runtime.on("taskComplete", this.handleTaskComplete.bind(this));
    this.runtime.on("breakpoint", this.handleBreakpoint.bind(this));
  }

  setBreakpoint(file: string, line: number): Breakpoint {
    const bp = new Breakpoint(file, line);

    if (!this.breakpoints.has(file)) {
      this.breakpoints.set(file, []);
    }

    this.breakpoints.get(file)!.push(bp);
    return bp;
  }

  async stepOver(): Promise<void> {
    await this.runtime.stepOver();
  }

  async stepInto(): Promise<void> {
    await this.runtime.stepInto();
  }

  async continue(): Promise<void> {
    await this.runtime.continue();
  }

  async evaluate(expression: string): Promise<any> {
    return this.runtime.evaluate(expression);
  }
}
```

**검증 기준**:

- [ ] Language Server Protocol 구현
- [ ] 자동 완성 기능
- [ ] 구문 강조 및 포매팅
- [ ] 디버깅 지원

### Task 5.5: 동적 워크플로우 생성 및 수정

#### SubTask 5.5.1: 런타임 워크플로우 빌더

**담당자**: 백엔드 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/orchestration/dynamic/workflow_builder.ts
export class DynamicWorkflowBuilder {
  private workflow: WorkflowDefinition;
  private validators: WorkflowValidator[] = [];
  private optimizers: WorkflowOptimizer[] = [];

  constructor(name: string, version: string = "1.0.0") {
    this.workflow = {
      id: this.generateId(name),
      name,
      version,
      description: "",
      input_schema: {},
      output_schema: {},
      tasks: [],
      timeout_seconds: 3600,
      max_retries: 1,
      error_handlers: {},
      tags: [],
      metadata: {},
    };
  }

  // 플루언트 API
  description(desc: string): this {
    this.workflow.description = desc;
    return this;
  }

  input(schema: Record<string, any>): this {
    this.workflow.input_schema = schema;
    return this;
  }

  output(schema: Record<string, any>): this {
    this.workflow.output_schema = schema;
    return this;
  }

  timeout(seconds: number): this {
    this.workflow.timeout_seconds = seconds;
    return this;
  }

  // 태스크 추가
  addTask(task: WorkflowTask | TaskBuilder): this {
    if (task instanceof TaskBuilder) {
      this.workflow.tasks.push(task.build());
    } else {
      this.workflow.tasks.push(task);
    }
    return this;
  }

  // 병렬 블록 추가
  parallel(configure: (builder: ParallelBuilder) => void): this {
    const parallelBuilder = new ParallelBuilder();
    configure(parallelBuilder);
    this.workflow.tasks.push(parallelBuilder.build());
    return this;
  }

  // 조건부 블록 추가
  conditional(
    condition: string,
    configure: (builder: ConditionalBuilder) => void
  ): this {
    const conditionalBuilder = new ConditionalBuilder(condition);
    configure(conditionalBuilder);
    this.workflow.tasks.push(conditionalBuilder.build());
    return this;
  }

  // 반복 블록 추가
  foreach(
    iterator: string,
    variable: string,
    configure: (builder: LoopBuilder) => void
  ): this {
    const loopBuilder = new LoopBuilder("foreach", iterator, variable);
    configure(loopBuilder);
    this.workflow.tasks.push(loopBuilder.build());
    return this;
  }

  // 검증 및 빌드
  async build(): Promise<WorkflowDefinition> {
    // 검증
    for (const validator of this.validators) {
      const result = await validator.validate(this.workflow);
      if (!result.valid) {
        throw new WorkflowValidationError(result.errors);
      }
    }

    // 최적화
    let optimized = this.workflow;
    for (const optimizer of this.optimizers) {
      optimized = await optimizer.optimize(optimized);
    }

    return optimized;
  }

  // 검증기 추가
  withValidator(validator: WorkflowValidator): this {
    this.validators.push(validator);
    return this;
  }

  // 최적화기 추가
  withOptimizer(optimizer: WorkflowOptimizer): this {
    this.optimizers.push(optimizer);
    return this;
  }
}

// 태스크 빌더
export class TaskBuilder {
  private task: Partial<WorkflowTask>;

  constructor(id: string, name: string, agentType: string) {
    this.task = {
      id,
      name,
      agent_type: agentType,
      input_mapping: {},
      output_mapping: {},
      dependencies: [],
      timeout_seconds: 300,
      retry_policy: new RetryPolicy(),
      conditions: [],
    };
  }

  input(mapping: Record<string, string>): this {
    this.task.input_mapping = mapping;
    return this;
  }

  output(mapping: Record<string, string>): this {
    this.task.output_mapping = mapping;
    return this;
  }

  dependsOn(...taskIds: string[]): this {
    this.task.dependencies = taskIds.map((id) => ({
      task_id: id,
      wait_for_completion: true,
    }));
    return this;
  }

  conditionalDependsOn(taskId: string, condition: string): this {
    this.task.dependencies!.push({
      task_id: taskId,
      condition,
      wait_for_completion: true,
    });
    return this;
  }

  timeout(seconds: number): this {
    this.task.timeout_seconds = seconds;
    return this;
  }

  retry(policy: Partial<RetryPolicy>): this {
    this.task.retry_policy = { ...new RetryPolicy(), ...policy };
    return this;
  }

  condition(expr: string): this {
    this.task.conditions!.push(expr);
    return this;
  }

  onError(handler: string): this {
    this.task.error_handler = handler;
    return this;
  }

  build(): WorkflowTask {
    if (!this.task.id || !this.task.name || !this.task.agent_type) {
      throw new Error("Task requires id, name, and agent_type");
    }
    return this.task as WorkflowTask;
  }
}

// 병렬 빌더
export class ParallelBuilder {
  private tasks: (WorkflowTask | ConditionalBlock)[] = [];
  private maxConcurrency?: number;
  private failFast: boolean = true;

  task(configure: (builder: TaskBuilder) => TaskBuilder): this {
    const taskBuilder = new TaskBuilder(`task_${Date.now()}`, "unnamed", "");
    const configured = configure(taskBuilder);
    this.tasks.push(configured.build());
    return this;
  }

  conditional(
    condition: string,
    configure: (builder: ConditionalBuilder) => void
  ): this {
    const conditionalBuilder = new ConditionalBuilder(condition);
    configure(conditionalBuilder);
    this.tasks.push(conditionalBuilder.build());
    return this;
  }

  concurrency(max: number): this {
    this.maxConcurrency = max;
    return this;
  }

  continueOnFailure(): this {
    this.failFast = false;
    return this;
  }

  build(): ParallelBlock {
    return {
      id: `parallel_${Date.now()}`,
      tasks: this.tasks,
      max_concurrency: this.maxConcurrency,
      fail_fast: this.failFast,
    };
  }
}

// 동적 워크플로우 생성 예제
export class WorkflowFactory {
  static createDataProcessingWorkflow(
    config: DataProcessingConfig
  ): DynamicWorkflowBuilder {
    const builder = new DynamicWorkflowBuilder("data-processing", "1.0.0")
      .description("Dynamic data processing workflow")
      .input({
        source: { type: "string", required: true },
        format: { type: "string", enum: ["csv", "json", "xml"] },
        transformations: { type: "array", items: { type: "string" } },
      })
      .output({
        processed_data: { type: "object" },
        statistics: { type: "object" },
      });

    // 데이터 소스에 따른 동적 태스크 추가
    if (config.source.type === "database") {
      builder.addTask(
        new TaskBuilder("fetch_db", "Fetch from Database", "DataFetchAgent")
          .input({
            connection_string: "input.source",
            query: `"${config.source.query}"`,
          })
          .output({
            raw_data: "context.raw_data",
          })
      );
    } else if (config.source.type === "api") {
      builder.addTask(
        new TaskBuilder("fetch_api", "Fetch from API", "APIFetchAgent")
          .input({
            url: "input.source",
            headers: JSON.stringify(config.source.headers || {}),
          })
          .output({
            raw_data: "context.raw_data",
          })
      );
    }

    // 변환 태스크 동적 추가
    config.transformations.forEach((transform, index) => {
      const prevTaskId =
        index === 0
          ? config.source.type === "database"
            ? "fetch_db"
            : "fetch_api"
          : `transform_${index - 1}`;

      builder.addTask(
        new TaskBuilder(
          `transform_${index}`,
          `Transform: ${transform.type}`,
          "DataTransformAgent"
        )
          .dependsOn(prevTaskId)
          .input({
            data:
              index === 0
                ? "context.raw_data"
                : `transform_${index - 1}.result`,
            transformation: JSON.stringify(transform),
          })
          .output({
            result: `context.transform_${index}_result`,
          })
      );
    });

    // 최종 집계
    builder.addTask(
      new TaskBuilder("aggregate", "Aggregate Results", "AggregationAgent")
        .dependsOn(`transform_${config.transformations.length - 1}`)
        .input({
          data: `transform_${config.transformations.length - 1}.result`,
        })
        .output({
          processed_data: "output.processed_data",
          statistics: "output.statistics",
        })
    );

    return builder;
  }
}

// 런타임 워크플로우 수정
export class RuntimeWorkflowModifier {
  constructor(
    private orchestrator: CentralOrchestrator,
    private validator: WorkflowValidator
  ) {}

  async modifyRunningWorkflow(
    executionId: string,
    modifications: WorkflowModification[]
  ): Promise<ModificationResult> {
    // 현재 실행 상태 가져오기
    const execution = await this.orchestrator.getExecution(executionId);

    if (!execution) {
      throw new Error(`Workflow execution ${executionId} not found`);
    }

    if (execution.state !== WorkflowState.RUNNING) {
      throw new Error(`Workflow is not running: ${execution.state}`);
    }

    // 수정 가능성 검증
    const canModify = await this.validateModifications(
      execution,
      modifications
    );

    if (!canModify.valid) {
      return {
        success: false,
        errors: canModify.errors,
      };
    }

    // 수정 적용
    const results = [];
    for (const mod of modifications) {
      const result = await this.applyModification(execution, mod);
      results.push(result);
    }

    return {
      success: true,
      results,
    };
  }

  private async applyModification(
    execution: WorkflowExecution,
    modification: WorkflowModification
  ): Promise<any> {
    switch (modification.type) {
      case "add_task":
        return this.addTaskToRunning(execution, modification);

      case "skip_task":
        return this.skipTask(execution, modification);

      case "modify_timeout":
        return this.modifyTimeout(execution, modification);

      case "inject_data":
        return this.injectData(execution, modification);

      default:
        throw new Error(`Unknown modification type: ${modification.type}`);
    }
  }
}
```

**검증 기준**:

- [ ] 플루언트 API 설계
- [ ] 동적 태스크 생성
- [ ] 런타임 수정 지원
- [ ] 검증 및 최적화

#### SubTask 5.5.2: 워크플로우 수정 API

**담당자**: API 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/orchestration/dynamic/modification_api.ts
import { Router } from "express";
import { body, param, validationResult } from "express-validator";

export class WorkflowModificationAPI {
  private router: Router;
  private modificationService: WorkflowModificationService;
  private authMiddleware: AuthMiddleware;

  constructor(orchestrator: CentralOrchestrator) {
    this.router = Router();
    this.modificationService = new WorkflowModificationService(orchestrator);
    this.authMiddleware = new AuthMiddleware();
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // 실행 중인 워크플로우 수정
    this.router.patch(
      "/workflows/:workflowId/executions/:executionId",
      this.authMiddleware.requirePermission("workflow:modify"),
      [
        param("workflowId").isString(),
        param("executionId").isUUID(),
        body("modifications").isArray(),
        body("modifications.*.type").isIn([
          "add_task",
          "remove_task",
          "skip_task",
          "modify_task",
          "inject_data",
          "modify_timeout",
        ]),
      ],
      this.modifyExecution.bind(this)
    );

    // 태스크 추가
    this.router.post(
      "/workflows/:workflowId/executions/:executionId/tasks",
      this.authMiddleware.requirePermission("workflow:modify"),
      [
        param("executionId").isUUID(),
        body("task").isObject(),
        body("position").optional().isString(),
      ],
      this.addTask.bind(this)
    );

    // 태스크 스킵
    this.router.post(
      "/workflows/:workflowId/executions/:executionId/tasks/:taskId/skip",
      this.authMiddleware.requirePermission("workflow:modify"),
      [
        param("executionId").isUUID(),
        param("taskId").isString(),
        body("reason").optional().isString(),
      ],
      this.skipTask.bind(this)
    );

    // 데이터 주입
    this.router.post(
      "/workflows/:workflowId/executions/:executionId/data",
      this.authMiddleware.requirePermission("workflow:modify"),
      [
        param("executionId").isUUID(),
        body("path").isString(),
        body("value").exists(),
      ],
      this.injectData.bind(this)
    );

    // 조건부 분기 강제
    this.router.post(
      "/workflows/:workflowId/executions/:executionId/force-branch",
      this.authMiddleware.requirePermission("workflow:modify"),
      [
        param("executionId").isUUID(),
        body("branchId").isString(),
        body("condition").isString(),
      ],
      this.forceBranch.bind(this)
    );
  }

  private async modifyExecution(req: Request, res: Response): Promise<void> {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { executionId } = req.params;
    const { modifications } = req.body;

    try {
      // 수정 권한 확인
      const canModify = await this.checkModificationPermissions(
        req.user,
        executionId
      );

      if (!canModify) {
        return res.status(403).json({
          error: "Insufficient permissions to modify workflow",
        });
      }

      // 수정 사항 검증
      const validation = await this.modificationService.validateModifications(
        executionId,
        modifications
      );

      if (!validation.valid) {
        return res.status(400).json({
          error: "Invalid modifications",
          details: validation.errors,
        });
      }

      // 수정 적용
      const result = await this.modificationService.applyModifications(
        executionId,
        modifications
      );

      // 감사 로그
      await this.auditLog.log({
        action: "workflow_modified",
        executionId,
        userId: req.user.id,
        modifications,
        result,
      });

      res.json({
        success: true,
        result,
      });
    } catch (error) {
      logger.error("Failed to modify workflow", { error, executionId });
      res.status(500).json({
        error: "Failed to modify workflow",
        message: error.message,
      });
    }
  }

  private async addTask(req: Request, res: Response): Promise<void> {
    const { executionId } = req.params;
    const { task, position } = req.body;

    try {
      // 태스크 빌더로 검증
      const taskBuilder = new TaskBuilder(
        task.id || `dynamic_${Date.now()}`,
        task.name,
        task.agent_type
      );

      // 태스크 구성
      if (task.input) taskBuilder.input(task.input);
      if (task.output) taskBuilder.output(task.output);
      if (task.dependencies) taskBuilder.dependsOn(...task.dependencies);
      if (task.timeout) taskBuilder.timeout(task.timeout);

      const builtTask = taskBuilder.build();

      // 추가 위치 결정
      const insertPosition = position || "end";

      // 태스크 추가
      const result = await this.modificationService.addTaskToExecution(
        executionId,
        builtTask,
        insertPosition
      );

      res.json({
        success: true,
        taskId: result.taskId,
        position: result.position,
      });
    } catch (error) {
      logger.error("Failed to add task", { error, executionId });
      res.status(500).json({
        error: "Failed to add task",
        message: error.message,
      });
    }
  }
}

// 워크플로우 수정 서비스
export class WorkflowModificationService {
  private modificationQueue: Queue<ModificationRequest>;
  private modificationHandlers: Map<string, ModificationHandler>;

  constructor(private orchestrator: CentralOrchestrator) {
    this.modificationQueue = new Queue();
    this.registerHandlers();
    this.startModificationProcessor();
  }

  private registerHandlers(): void {
    this.modificationHandlers = new Map([
      ["add_task", new AddTaskHandler()],
      ["remove_task", new RemoveTaskHandler()],
      ["skip_task", new SkipTaskHandler()],
      ["modify_task", new ModifyTaskHandler()],
      ["inject_data", new InjectDataHandler()],
      ["modify_timeout", new ModifyTimeoutHandler()],
      ["force_branch", new ForceBranchHandler()],
    ]);
  }

  async validateModifications(
    executionId: string,
    modifications: WorkflowModification[]
  ): Promise<ValidationResult> {
    const execution = await this.orchestrator.getExecution(executionId);

    if (!execution) {
      return {
        valid: false,
        errors: ["Execution not found"],
      };
    }

    const errors: string[] = [];

    for (const mod of modifications) {
      const handler = this.modificationHandlers.get(mod.type);

      if (!handler) {
        errors.push(`Unknown modification type: ${mod.type}`);
        continue;
      }

      const validation = await handler.validate(execution, mod);
      if (!validation.valid) {
        errors.push(...validation.errors);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  async applyModifications(
    executionId: string,
    modifications: WorkflowModification[]
  ): Promise<ModificationResult[]> {
    const results: ModificationResult[] = [];

    // 수정 요청을 큐에 추가
    for (const mod of modifications) {
      const request: ModificationRequest = {
        id: uuid(),
        executionId,
        modification: mod,
        timestamp: new Date(),
        status: "pending",
      };

      await this.modificationQueue.enqueue(request);

      // 동기적으로 처리 대기
      const result = await this.waitForModification(request.id);
      results.push(result);
    }

    return results;
  }

  private async processModification(
    request: ModificationRequest
  ): Promise<ModificationResult> {
    const handler = this.modificationHandlers.get(request.modification.type);

    if (!handler) {
      return {
        requestId: request.id,
        success: false,
        error: `Unknown modification type: ${request.modification.type}`,
      };
    }

    try {
      // 실행 상태 잠금
      await this.orchestrator.lockExecution(request.executionId);

      // 수정 적용
      const result = await handler.apply(
        this.orchestrator,
        request.executionId,
        request.modification
      );

      // 이벤트 발행
      await this.orchestrator.eventBus.publish({
        event_type: "workflow.modified",
        workflow_id: request.executionId,
        timestamp: new Date(),
        data: {
          modification: request.modification,
          result,
        },
      });

      return {
        requestId: request.id,
        success: true,
        result,
      };
    } catch (error) {
      return {
        requestId: request.id,
        success: false,
        error: error.message,
      };
    } finally {
      // 잠금 해제
      await this.orchestrator.unlockExecution(request.executionId);
    }
  }
}

// 수정 핸들러 인터페이스
abstract class ModificationHandler {
  abstract validate(
    execution: WorkflowExecution,
    modification: WorkflowModification
  ): Promise<ValidationResult>;

  abstract apply(
    orchestrator: CentralOrchestrator,
    executionId: string,
    modification: WorkflowModification
  ): Promise<any>;
}

// 태스크 추가 핸들러
class AddTaskHandler extends ModificationHandler {
  async validate(
    execution: WorkflowExecution,
    modification: WorkflowModification
  ): Promise<ValidationResult> {
    const { task, position } = modification.data;

    // 태스크 검증
    if (!task.agent_type) {
      return {
        valid: false,
        errors: ["Task must specify agent_type"],
      };
    }

    // 위치 검증
    if (position && position !== "end") {
      const targetTask = execution.tasks[position];
      if (!targetTask) {
        return {
          valid: false,
          errors: [`Invalid position: ${position}`],
        };
      }

      // 실행 중이거나 완료된 태스크 뒤에는 추가 불가
      if (targetTask.status !== "pending") {
        return {
          valid: false,
          errors: ["Cannot add task after running/completed task"],
        };
      }
    }

    return { valid: true, errors: [] };
  }

  async apply(
    orchestrator: CentralOrchestrator,
    executionId: string,
    modification: WorkflowModification
  ): Promise<any> {
    const { task, position } = modification.data;

    // 태스크 생성
    const newTask = new AgentTask({
      id: task.id || `dynamic_${Date.now()}`,
      ...task,
      workflow_id: executionId,
      status: "pending",
      created_at: new Date(),
    });

    // 실행에 추가
    await orchestrator.addTaskToExecution(executionId, newTask, position);

    return {
      taskId: newTask.id,
      position: position || "end",
    };
  }
}

// 동적 워크플로우 빌더 UI 지원
export class WorkflowBuilderUISupport {
  async getAvailableAgents(): Promise<AgentInfo[]> {
    return this.orchestrator.registry.getAllAgents();
  }

  async getTaskTemplates(): Promise<TaskTemplate[]> {
    return [
      {
        id: "data_fetch",
        name: "Data Fetch",
        description: "Fetch data from various sources",
        agent_type: "DataFetchAgent",
        default_config: {
          timeout: 300,
          retry: 2,
        },
      },
      {
        id: "data_transform",
        name: "Data Transform",
        description: "Transform data using various operations",
        agent_type: "DataTransformAgent",
        default_config: {
          timeout: 600,
          retry: 1,
        },
      },
      // ... 더 많은 템플릿
    ];
  }

  async validateWorkflowDraft(draft: WorkflowDraft): Promise<ValidationResult> {
    const builder = new DynamicWorkflowBuilder(draft.name, draft.version);

    // 드래프트를 빌더로 변환
    builder
      .description(draft.description)
      .input(draft.input_schema)
      .output(draft.output_schema);

    for (const task of draft.tasks) {
      builder.addTask(task);
    }

    // 검증
    try {
      await builder.build();
      return { valid: true, errors: [] };
    } catch (error) {
      return {
        valid: false,
        errors: [error.message],
      };
    }
  }
}
```

**검증 기준**:

- [ ] RESTful API 설계
- [ ] 수정 검증 로직
- [ ] 권한 관리
- [ ] 실시간 수정 지원

#### SubTask 5.5.3: 동적 분기 및 조건부 실행

**담당자**: 워크플로우 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/orchestration/dynamic/conditional_execution.ts
export class ConditionalExecutor {
  private expressionEvaluator: ExpressionEvaluator;
  private branchPredictor: BranchPredictor;

  constructor() {
    this.expressionEvaluator = new ExpressionEvaluator();
    this.branchPredictor = new BranchPredictor();
  }

  async evaluateCondition(
    condition: string,
    context: ExecutionContext
  ): Promise<boolean> {
    try {
      // 표현식 파싱
      const expression = this.expressionEvaluator.parse(condition);

      // 컨텍스트 값 해결
      const resolvedContext = await this.resolveContextValues(
        expression,
        context
      );

      // 평가
      const result = await this.expressionEvaluator.evaluate(
        expression,
        resolvedContext
      );

      // 결과 타입 검증
      if (typeof result !== "boolean") {
        throw new Error(
          `Condition must evaluate to boolean, got ${typeof result}`
        );
      }

      return result;
    } catch (error) {
      logger.error("Failed to evaluate condition", {
        condition,
        error: error.message,
      });
      throw new ConditionEvaluationError(
        `Failed to evaluate condition: ${error.message}`
      );
    }
  }

  async executeDynamicBranch(
    branchConfig: DynamicBranchConfig,
    context: ExecutionContext
  ): Promise<BranchExecutionResult> {
    const startTime = Date.now();
    const results: TaskExecutionResult[] = [];

    try {
      // 분기 예측
      const prediction = await this.branchPredictor.predict(
        branchConfig,
        context
      );

      // 예측 기반 리소스 사전 할당
      if (prediction.confidence > 0.8) {
        await this.preAllocateResources(prediction.predictedBranch);
      }

      // 조건 평가
      const branchDecision = await this.decideBranch(branchConfig, context);

      // 선택된 분기 실행
      const selectedBranch = branchConfig.branches[branchDecision.branchIndex];

      logger.info("Executing dynamic branch", {
        branchId: selectedBranch.id,
        condition: branchDecision.condition,
        evaluated: branchDecision.evaluated,
      });

      // 태스크 실행
      for (const task of selectedBranch.tasks) {
        const result = await this.executeTask(task, context);
        results.push(result);

        // 결과를 컨텍스트에 반영
        this.updateContext(context, task, result);
      }

      return {
        branchId: selectedBranch.id,
        executed: true,
        results,
        duration: Date.now() - startTime,
      };
    } catch (error) {
      return {
        branchId: null,
        executed: false,
        error: error.message,
        duration: Date.now() - startTime,
      };
    }
  }

  private async decideBranch(
    config: DynamicBranchConfig,
    context: ExecutionContext
  ): Promise<BranchDecision> {
    // switch 스타일 분기
    if (config.type === "switch") {
      const switchValue = await this.evaluateExpression(
        config.switchExpression!,
        context
      );

      for (let i = 0; i < config.branches.length; i++) {
        const branch = config.branches[i];

        if (branch.caseValue === switchValue) {
          return {
            branchIndex: i,
            condition: `${config.switchExpression} == ${branch.caseValue}`,
            evaluated: true,
          };
        }
      }

      // default 분기
      const defaultIndex = config.branches.findIndex((b) => b.isDefault);
      if (defaultIndex >= 0) {
        return {
          branchIndex: defaultIndex,
          condition: "default",
          evaluated: true,
        };
      }
    } else {
      // if-else 스타일 분기
      for (let i = 0; i < config.branches.length; i++) {
        const branch = config.branches[i];

        if (!branch.condition) {
          // else 분기
          return {
            branchIndex: i,
            condition: "else",
            evaluated: true,
          };
        }

        const conditionMet = await this.evaluateCondition(
          branch.condition,
          context
        );

        if (conditionMet) {
          return {
            branchIndex: i,
            condition: branch.condition,
            evaluated: conditionMet,
          };
        }
      }
    }

    throw new Error("No branch condition met");
  }
}

// 동적 반복 실행
export class DynamicLoopExecutor {
  constructor(
    private taskExecutor: TaskExecutor,
    private conditionEvaluator: ConditionalExecutor
  ) {}

  async executeLoop(
    loopConfig: LoopConfig,
    context: ExecutionContext
  ): Promise<LoopExecutionResult> {
    const results: TaskExecutionResult[] = [];
    let iterations = 0;
    const maxIterations = loopConfig.maxIterations || 1000;

    try {
      if (loopConfig.type === "foreach") {
        // ForEach 루프
        results.push(...(await this.executeForeach(loopConfig, context)));
      } else if (loopConfig.type === "while") {
        // While 루프
        results.push(
          ...(await this.executeWhile(loopConfig, context, maxIterations))
        );
      } else if (loopConfig.type === "do-while") {
        // Do-While 루프
        results.push(
          ...(await this.executeDoWhile(loopConfig, context, maxIterations))
        );
      } else if (loopConfig.type === "for") {
        // For 루프
        results.push(...(await this.executeFor(loopConfig, context)));
      }

      return {
        completed: true,
        iterations: results.length,
        results,
      };
    } catch (error) {
      return {
        completed: false,
        iterations,
        results,
        error: error.message,
      };
    }
  }

  private async executeForeach(
    config: LoopConfig,
    context: ExecutionContext
  ): Promise<TaskExecutionResult[]> {
    const results: TaskExecutionResult[] = [];

    // 반복 대상 가져오기
    const iterable = await this.resolveIterable(config.iterator!, context);

    if (!Array.isArray(iterable)) {
      throw new Error(`Iterator must be an array, got ${typeof iterable}`);
    }

    // 병렬 실행 여부
    if (config.parallel) {
      const promises = iterable.map((item, index) =>
        this.executeLoopIteration(config, context, item, index)
      );

      const parallelResults = await Promise.allSettled(promises);

      for (const result of parallelResults) {
        if (result.status === "fulfilled") {
          results.push(...result.value);
        } else {
          logger.error("Parallel loop iteration failed", result.reason);
        }
      }
    } else {
      // 순차 실행
      for (let i = 0; i < iterable.length; i++) {
        const item = iterable[i];
        const iterationResults = await this.executeLoopIteration(
          config,
          context,
          item,
          i
        );
        results.push(...iterationResults);

        // early break 조건 확인
        if (config.breakCondition) {
          const shouldBreak = await this.conditionEvaluator.evaluateCondition(
            config.breakCondition,
            context
          );
          if (shouldBreak) break;
        }
      }
    }

    return results;
  }

  private async executeLoopIteration(
    config: LoopConfig,
    baseContext: ExecutionContext,
    item: any,
    index: number
  ): Promise<TaskExecutionResult[]> {
    // 반복 컨텍스트 생성
    const iterationContext = this.createIterationContext(
      baseContext,
      config.variable!,
      item,
      index
    );

    const results: TaskExecutionResult[] = [];

    for (const task of config.tasks) {
      const result = await this.taskExecutor.execute(task, iterationContext);
      results.push(result);

      // 결과를 컨텍스트에 반영
      this.updateIterationContext(iterationContext, task, result);
    }

    return results;
  }

  private createIterationContext(
    baseContext: ExecutionContext,
    variableName: string,
    item: any,
    index: number
  ): ExecutionContext {
    return {
      ...baseContext,
      loop: {
        ...baseContext.loop,
        [variableName]: item,
        [`${variableName}_index`]: index,
      },
    };
  }
}

// 동적 에러 처리
export class DynamicErrorHandler {
  private errorPatterns: Map<string, ErrorPattern>;
  private recoveryStrategies: Map<string, RecoveryStrategy>;

  constructor() {
    this.errorPatterns = new Map();
    this.recoveryStrategies = new Map();
    this.registerDefaultPatterns();
  }

  async handleError(
    error: Error,
    task: WorkflowTask,
    context: ExecutionContext
  ): Promise<ErrorHandlingResult> {
    // 에러 패턴 매칭
    const pattern = this.matchErrorPattern(error);

    // 복구 전략 선택
    const strategy = this.selectRecoveryStrategy(pattern, task, context);

    // 전략 실행
    return await this.executeRecoveryStrategy(strategy, error, task, context);
  }

  private matchErrorPattern(error: Error): ErrorPattern | null {
    for (const [name, pattern] of this.errorPatterns) {
      if (pattern.matches(error)) {
        return pattern;
      }
    }
    return null;
  }

  private selectRecoveryStrategy(
    pattern: ErrorPattern | null,
    task: WorkflowTask,
    context: ExecutionContext
  ): RecoveryStrategy {
    // 태스크별 에러 핸들러 확인
    if (task.error_handler) {
      const customStrategy = this.recoveryStrategies.get(task.error_handler);
      if (customStrategy) return customStrategy;
    }

    // 패턴 기반 전략
    if (pattern && pattern.recoveryStrategy) {
      const patternStrategy = this.recoveryStrategies.get(
        pattern.recoveryStrategy
      );
      if (patternStrategy) return patternStrategy;
    }

    // 기본 전략
    return this.recoveryStrategies.get("default")!;
  }

  private async executeRecoveryStrategy(
    strategy: RecoveryStrategy,
    error: Error,
    task: WorkflowTask,
    context: ExecutionContext
  ): Promise<ErrorHandlingResult> {
    try {
      const result = await strategy.execute(error, task, context);

      if (result.recovered) {
        logger.info("Error recovered", {
          taskId: task.id,
          strategy: strategy.name,
          action: result.action,
        });
      }

      return result;
    } catch (recoveryError) {
      logger.error("Recovery strategy failed", {
        taskId: task.id,
        strategy: strategy.name,
        error: recoveryError.message,
      });

      return {
        recovered: false,
        action: "fail",
        error: recoveryError,
      };
    }
  }

  registerErrorPattern(name: string, pattern: ErrorPattern): void {
    this.errorPatterns.set(name, pattern);
  }

  registerRecoveryStrategy(name: string, strategy: RecoveryStrategy): void {
    this.recoveryStrategies.set(name, strategy);
  }

  private registerDefaultPatterns(): void {
    // 네트워크 오류
    this.registerErrorPattern("network", {
      name: "network",
      matches: (error) => {
        return (
          error.message.includes("ECONNREFUSED") ||
          error.message.includes("ETIMEDOUT") ||
          error.message.includes("ENOTFOUND")
        );
      },
      recoveryStrategy: "retry_with_backoff",
    });

    // 리소스 부족
    this.registerErrorPattern("resource_exhausted", {
      name: "resource_exhausted",
      matches: (error) => {
        return (
          error.message.includes("insufficient resources") ||
          error.message.includes("quota exceeded")
        );
      },
      recoveryStrategy: "wait_and_retry",
    });

    // 권한 오류
    this.registerErrorPattern("permission_denied", {
      name: "permission_denied",
      matches: (error) => {
        return (
          error.message.includes("permission denied") ||
          error.message.includes("unauthorized")
        );
      },
      recoveryStrategy: "escalate",
    });
  }
}

// 분기 예측기
class BranchPredictor {
  private history: Map<string, BranchHistory>;

  constructor() {
    this.history = new Map();
  }

  async predict(
    config: DynamicBranchConfig,
    context: ExecutionContext
  ): Promise<BranchPrediction> {
    const historyKey = this.generateHistoryKey(config, context);
    const branchHistory = this.history.get(historyKey);

    if (!branchHistory || branchHistory.samples < 10) {
      // 히스토리가 부족하면 예측하지 않음
      return {
        predictedBranch: null,
        confidence: 0,
      };
    }

    // 가장 자주 실행된 분기 찾기
    const mostFrequent = branchHistory.getMostFrequentBranch();

    return {
      predictedBranch: mostFrequent.branchId,
      confidence: mostFrequent.frequency / branchHistory.samples,
    };
  }

  recordExecution(
    config: DynamicBranchConfig,
    context: ExecutionContext,
    executedBranch: string
  ): void {
    const historyKey = this.generateHistoryKey(config, context);

    if (!this.history.has(historyKey)) {
      this.history.set(historyKey, new BranchHistory());
    }

    this.history.get(historyKey)!.record(executedBranch);
  }

  private generateHistoryKey(
    config: DynamicBranchConfig,
    context: ExecutionContext
  ): string {
    // 컨텍스트의 주요 값들로 키 생성
    const relevantContext = this.extractRelevantContext(config, context);
    return `${config.id}:${JSON.stringify(relevantContext)}`;
  }
}
```

**검증 기준**:

- [ ] 조건부 실행 엔진
- [ ] 동적 반복 처리
- [ ] 에러 처리 및 복구
- [ ] 분기 예측 최적화

#### SubTask 5.5.4: 워크플로우 버전 관리

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/orchestration/dynamic/version_control.ts
export class WorkflowVersionControl {
  private versionStore: VersionStore;
  private diffEngine: DiffEngine;
  private mergeEngine: MergeEngine;

  constructor(storage: StorageBackend) {
    this.versionStore = new VersionStore(storage);
    this.diffEngine = new DiffEngine();
    this.mergeEngine = new MergeEngine();
  }

  async createVersion(
    workflow: WorkflowDefinition,
    metadata: VersionMetadata
  ): Promise<WorkflowVersion> {
    // 버전 번호 생성
    const versionNumber = await this.generateVersionNumber(
      workflow.id,
      metadata.versionType
    );

    // 이전 버전과의 차이 계산
    const previousVersion = await this.getLatestVersion(workflow.id);
    const diff = previousVersion
      ? await this.diffEngine.calculateDiff(
          previousVersion.definition,
          workflow
        )
      : null;

    // 버전 생성
    const version: WorkflowVersion = {
      id: uuid(),
      workflowId: workflow.id,
      version: versionNumber,
      definition: workflow,
      diff,
      metadata: {
        ...metadata,
        createdAt: new Date(),
        createdBy: metadata.userId,
        changeLog: await this.generateChangeLog(diff),
      },
      status: "draft",
    };

    // 저장
    await this.versionStore.save(version);

    return version;
  }

  async promoteVersion(
    workflowId: string,
    versionId: string,
    environment: string
  ): Promise<PromotionResult> {
    const version = await this.versionStore.get(versionId);

    if (!version) {
      throw new Error(`Version ${versionId} not found`);
    }

    // 검증
    const validation = await this.validatePromotion(version, environment);

    if (!validation.valid) {
      return {
        success: false,
        errors: validation.errors,
      };
    }

    // 프로모션 실행
    const promotion = await this.executePromotion(version, environment);

    // 프로모션 기록
    await this.recordPromotion(version, environment, promotion);

    return promotion;
  }

  async compareVersions(
    versionId1: string,
    versionId2: string
  ): Promise<VersionComparison> {
    const [version1, version2] = await Promise.all([
      this.versionStore.get(versionId1),
      this.versionStore.get(versionId2),
    ]);

    if (!version1 || !version2) {
      throw new Error("One or both versions not found");
    }

    const diff = await this.diffEngine.calculateDiff(
      version1.definition,
      version2.definition
    );

    return {
      version1: {
        id: version1.id,
        version: version1.version,
        createdAt: version1.metadata.createdAt,
      },
      version2: {
        id: version2.id,
        version: version2.version,
        createdAt: version2.metadata.createdAt,
      },
      diff,
      summary: this.summarizeDiff(diff),
    };
  }

  async mergeVersions(
    baseVersionId: string,
    sourceVersionId: string,
    targetVersionId: string,
    strategy: MergeStrategy = "three-way"
  ): Promise<MergeResult> {
    const [base, source, target] = await Promise.all([
      this.versionStore.get(baseVersionId),
      this.versionStore.get(sourceVersionId),
      this.versionStore.get(targetVersionId),
    ]);

    if (!base || !source || !target) {
      throw new Error("One or more versions not found");
    }

    // 병합 실행
    const mergeResult = await this.mergeEngine.merge(
      base.definition,
      source.definition,
      target.definition,
      strategy
    );

    if (mergeResult.conflicts.length > 0) {
      return {
        success: false,
        conflicts: mergeResult.conflicts,
        merged: null,
      };
    }

    // 병합된 버전 생성
    const mergedVersion = await this.createVersion(mergeResult.merged, {
      versionType: "merge",
      description: `Merge of ${source.version} into ${target.version}`,
      userId: "system",
      mergeInfo: {
        base: baseVersionId,
        source: sourceVersionId,
        target: targetVersionId,
      },
    });

    return {
      success: true,
      conflicts: [],
      merged: mergedVersion,
    };
  }

  async rollbackVersion(
    workflowId: string,
    targetVersionId: string,
    reason: string
  ): Promise<RollbackResult> {
    const currentVersion = await this.getCurrentVersion(workflowId);
    const targetVersion = await this.versionStore.get(targetVersionId);

    if (!targetVersion) {
      throw new Error(`Target version ${targetVersionId} not found`);
    }

    // 롤백 가능성 확인
    const canRollback = await this.validateRollback(
      currentVersion,
      targetVersion
    );

    if (!canRollback.valid) {
      return {
        success: false,
        errors: canRollback.errors,
      };
    }

    // 롤백 실행
    const rollbackVersion = await this.createVersion(targetVersion.definition, {
      versionType: "rollback",
      description: `Rollback to ${targetVersion.version}: ${reason}`,
      userId: "system",
      rollbackInfo: {
        from: currentVersion.id,
        to: targetVersionId,
        reason,
      },
    });

    // 즉시 활성화
    await this.activateVersion(rollbackVersion.id);

    return {
      success: true,
      rollbackVersion,
    };
  }

  private async generateVersionNumber(
    workflowId: string,
    versionType: VersionType
  ): Promise<string> {
    const latestVersion = await this.getLatestVersion(workflowId);

    if (!latestVersion) {
      return "1.0.0";
    }

    const current = semver.parse(latestVersion.version);

    switch (versionType) {
      case "major":
        return semver.inc(current, "major");
      case "minor":
        return semver.inc(current, "minor");
      case "patch":
        return semver.inc(current, "patch");
      case "prerelease":
        return semver.inc(current, "prerelease", "beta");
      default:
        return semver.inc(current, "patch");
    }
  }
}

// 버전 차이 엔진
export class DiffEngine {
  async calculateDiff(
    oldDef: WorkflowDefinition,
    newDef: WorkflowDefinition
  ): Promise<WorkflowDiff> {
    const diff: WorkflowDiff = {
      metadata: this.diffMetadata(oldDef, newDef),
      tasks: await this.diffTasks(oldDef.tasks, newDef.tasks),
      structure: this.diffStructure(oldDef, newDef),
      inputs: this.diffSchema(oldDef.input_schema, newDef.input_schema),
      outputs: this.diffSchema(oldDef.output_schema, newDef.output_schema),
    };

    return diff;
  }

  private async diffTasks(
    oldTasks: WorkflowTask[],
    newTasks: WorkflowTask[]
  ): Promise<TaskDiff[]> {
    const diffs: TaskDiff[] = [];
    const oldTaskMap = new Map(oldTasks.map((t) => [t.id, t]));
    const newTaskMap = new Map(newTasks.map((t) => [t.id, t]));

    // 추가된 태스크
    for (const [id, task] of newTaskMap) {
      if (!oldTaskMap.has(id)) {
        diffs.push({
          type: "added",
          taskId: id,
          task,
        });
      }
    }

    // 삭제된 태스크
    for (const [id, task] of oldTaskMap) {
      if (!newTaskMap.has(id)) {
        diffs.push({
          type: "removed",
          taskId: id,
          task,
        });
      }
    }

    // 수정된 태스크
    for (const [id, newTask] of newTaskMap) {
      const oldTask = oldTaskMap.get(id);
      if (oldTask) {
        const changes = this.compareTask(oldTask, newTask);
        if (changes.length > 0) {
          diffs.push({
            type: "modified",
            taskId: id,
            changes,
          });
        }
      }
    }

    return diffs;
  }

  private compareTask(
    oldTask: WorkflowTask,
    newTask: WorkflowTask
  ): TaskChange[] {
    const changes: TaskChange[] = [];

    // 속성별 비교
    const properties = [
      "agent_type",
      "timeout_seconds",
      "retry_policy",
      "input_mapping",
      "output_mapping",
      "dependencies",
    ];

    for (const prop of properties) {
      if (!_.isEqual(oldTask[prop], newTask[prop])) {
        changes.push({
          property: prop,
          oldValue: oldTask[prop],
          newValue: newTask[prop],
        });
      }
    }

    return changes;
  }
}

// 버전 병합 엔진
export class MergeEngine {
  async merge(
    base: WorkflowDefinition,
    source: WorkflowDefinition,
    target: WorkflowDefinition,
    strategy: MergeStrategy
  ): Promise<MergeResult> {
    if (strategy === "three-way") {
      return this.threeWayMerge(base, source, target);
    } else if (strategy === "ours") {
      return { merged: target, conflicts: [] };
    } else if (strategy === "theirs") {
      return { merged: source, conflicts: [] };
    } else {
      throw new Error(`Unknown merge strategy: ${strategy}`);
    }
  }

  private async threeWayMerge(
    base: WorkflowDefinition,
    source: WorkflowDefinition,
    target: WorkflowDefinition
  ): Promise<MergeResult> {
    const conflicts: MergeConflict[] = [];
    const merged = _.cloneDeep(target);

    // 메타데이터 병합
    const metadataConflicts = this.mergeMetadata(base, source, target, merged);
    conflicts.push(...metadataConflicts);

    // 태스크 병합
    const taskConflicts = await this.mergeTasks(
      base.tasks,
      source.tasks,
      target.tasks,
      merged
    );
    conflicts.push(...taskConflicts);

    // 스키마 병합
    const schemaConflicts = this.mergeSchemas(base, source, target, merged);
    conflicts.push(...schemaConflicts);

    return {
      merged: conflicts.length === 0 ? merged : null,
      conflicts,
    };
  }

  private async mergeTasks(
    baseTasks: WorkflowTask[],
    sourceTasks: WorkflowTask[],
    targetTasks: WorkflowTask[],
    merged: WorkflowDefinition
  ): Promise<MergeConflict[]> {
    const conflicts: MergeConflict[] = [];
    const baseMap = new Map(baseTasks.map((t) => [t.id, t]));
    const sourceMap = new Map(sourceTasks.map((t) => [t.id, t]));
    const targetMap = new Map(targetTasks.map((t) => [t.id, t]));

    const allTaskIds = new Set([
      ...baseMap.keys(),
      ...sourceMap.keys(),
      ...targetMap.keys(),
    ]);

    const mergedTasks: WorkflowTask[] = [];

    for (const taskId of allTaskIds) {
      const baseTask = baseMap.get(taskId);
      const sourceTask = sourceMap.get(taskId);
      const targetTask = targetMap.get(taskId);

      if (!baseTask && sourceTask && !targetTask) {
        // Source에만 추가됨
        mergedTasks.push(sourceTask);
      } else if (!baseTask && !sourceTask && targetTask) {
        // Target에만 추가됨
        mergedTasks.push(targetTask);
      } else if (baseTask && !sourceTask && targetTask) {
        // Source에서 삭제됨
        if (_.isEqual(baseTask, targetTask)) {
          // Target에서 변경 없음 - 삭제 적용
          continue;
        } else {
          // 충돌: Source에서 삭제, Target에서 수정
          conflicts.push({
            type: "delete-modify",
            path: `tasks.${taskId}`,
            base: baseTask,
            source: null,
            target: targetTask,
          });
        }
      } else if (baseTask && sourceTask && !targetTask) {
        // Target에서 삭제됨
        if (_.isEqual(baseTask, sourceTask)) {
          // Source에서 변경 없음 - 삭제 적용
          continue;
        } else {
          // 충돌: Source에서 수정, Target에서 삭제
          conflicts.push({
            type: "modify-delete",
            path: `tasks.${taskId}`,
            base: baseTask,
            source: sourceTask,
            target: null,
          });
        }
      } else if (baseTask && sourceTask && targetTask) {
        // 모두에 존재 - 3-way 병합
        const mergedTask = await this.mergeTask(
          baseTask,
          sourceTask,
          targetTask
        );

        if (mergedTask.conflicts.length > 0) {
          conflicts.push(...mergedTask.conflicts);
        } else {
          mergedTasks.push(mergedTask.task);
        }
      }
    }

    if (conflicts.length === 0) {
      merged.tasks = mergedTasks;
    }

    return conflicts;
  }
}

// 버전 이력 추적
export class VersionHistory {
  private timeline: VersionTimeline;

  constructor(private versionStore: VersionStore) {
    this.timeline = new VersionTimeline();
  }

  async getHistory(
    workflowId: string,
    options: HistoryOptions = {}
  ): Promise<VersionHistoryEntry[]> {
    const versions = await this.versionStore.listVersions(workflowId, options);

    const history: VersionHistoryEntry[] = [];

    for (const version of versions) {
      const entry: VersionHistoryEntry = {
        version: version.version,
        createdAt: version.metadata.createdAt,
        createdBy: version.metadata.createdBy,
        type: version.metadata.versionType,
        description: version.metadata.description,
        changes: await this.summarizeChanges(version),
        promotions: await this.getPromotions(version.id),
      };

      history.push(entry);
    }

    return history;
  }

  async getVersionGraph(workflowId: string): Promise<VersionGraph> {
    const versions = await this.versionStore.listVersions(workflowId);
    const graph = new VersionGraph();

    // 노드 추가
    for (const version of versions) {
      graph.addNode({
        id: version.id,
        version: version.version,
        metadata: version.metadata,
      });
    }

    // 엣지 추가 (부모-자식 관계)
    for (const version of versions) {
      if (version.metadata.parentVersion) {
        graph.addEdge(
          version.metadata.parentVersion,
          version.id,
          version.metadata.versionType
        );
      }
    }

    return graph;
  }

  async getBranches(workflowId: string): Promise<VersionBranch[]> {
    const graph = await this.getVersionGraph(workflowId);
    return graph.identifyBranches();
  }
}
```

**검증 기준**:

- [ ] 버전 생성 및 관리
- [ ] 버전 비교 및 병합
- [ ] 프로모션 및 롤백
- [ ] 버전 이력 추적

### Task 5.6: 워크플로우 템플릿 및 재사용 시스템

#### SubTask 5.6.1: 템플릿 저장소 구축

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/orchestration/templates/template_repository.ts
export interface WorkflowTemplate {
  id: string;
  name: string;
  version: string;
  description: string;
  category: string;
  tags: string[];
  author: string;
  organization?: string;
  visibility: "public" | "private" | "organization";

  // 템플릿 내용
  definition: TemplateDefinition;
  parameters: TemplateParameter[];
  examples: TemplateExample[];

  // 메타데이터
  created_at: Date;
  updated_at: Date;
  downloads: number;
  rating: number;
  verified: boolean;
}

export class TemplateRepository {
  private storage: TemplateStorage;
  private validator: TemplateValidator;
  private indexer: TemplateIndexer;

  constructor(config: RepositoryConfig) {
    this.storage = new TemplateStorage(config.storage);
    this.validator = new TemplateValidator();
    this.indexer = new TemplateIndexer(config.search);
  }

  async createTemplate(
    template: Omit<
      WorkflowTemplate,
      "id" | "created_at" | "updated_at" | "downloads" | "rating"
    >
  ): Promise<WorkflowTemplate> {
    // 검증
    const validation = await this.validator.validate(template);
    if (!validation.valid) {
      throw new TemplateValidationError(validation.errors);
    }

    // ID 생성
    const id = this.generateTemplateId(template.name, template.version);

    // 템플릿 생성
    const fullTemplate: WorkflowTemplate = {
      ...template,
      id,
      created_at: new Date(),
      updated_at: new Date(),
      downloads: 0,
      rating: 0,
    };

    // 저장
    await this.storage.save(fullTemplate);

    // 인덱싱
    await this.indexer.index(fullTemplate);

    // 이벤트 발행
    await this.publishEvent("template.created", fullTemplate);

    return fullTemplate;
  }

  async searchTemplates(
    query: TemplateSearchQuery
  ): Promise<TemplateSearchResult> {
    // 검색 실행
    const searchResults = await this.indexer.search(query);

    // 템플릿 로드
    const templates = await Promise.all(
      searchResults.hits.map((hit) => this.storage.get(hit.id))
    );

    // 필터링 적용
    const filtered = this.applyFilters(templates, query.filters);

    // 정렬
    const sorted = this.sortTemplates(filtered, query.sort);

    // 페이징
    const paginated = this.paginate(sorted, query.page, query.limit);

    return {
      templates: paginated,
      total: filtered.length,
      page: query.page,
      limit: query.limit,
      facets: await this.calculateFacets(filtered),
    };
  }

  async getTemplate(
    templateId: string,
    options: GetTemplateOptions = {}
  ): Promise<WorkflowTemplate | null> {
    const template = await this.storage.get(templateId);

    if (!template) {
      return null;
    }

    // 접근 권한 확인
    if (!(await this.checkAccess(template, options.userId))) {
      throw new TemplateAccessError("Access denied");
    }

    // 다운로드 카운트 증가
    if (options.incrementDownload) {
      await this.incrementDownloadCount(templateId);
    }

    // 관련 템플릿 로드
    if (options.includeRelated) {
      template.related = await this.findRelatedTemplates(template);
    }

    return template;
  }

  async updateTemplate(
    templateId: string,
    updates: Partial<WorkflowTemplate>,
    userId: string
  ): Promise<WorkflowTemplate> {
    const existing = await this.getTemplate(templateId);

    if (!existing) {
      throw new TemplateNotFoundError(templateId);
    }

    // 권한 확인
    if (existing.author !== userId && !(await this.isAdmin(userId))) {
      throw new TemplateAccessError("Only author can update template");
    }

    // 업데이트 적용
    const updated = {
      ...existing,
      ...updates,
      updated_at: new Date(),
    };

    // 버전 관리
    if (updates.definition && !updates.version) {
      updated.version = this.incrementVersion(existing.version);
    }

    // 검증
    const validation = await this.validator.validate(updated);
    if (!validation.valid) {
      throw new TemplateValidationError(validation.errors);
    }

    // 저장
    await this.storage.save(updated);

    // 재인덱싱
    await this.indexer.reindex(updated);

    // 이벤트 발행
    await this.publishEvent("template.updated", updated);

    return updated;
  }

  async forkTemplate(
    templateId: string,
    userId: string,
    modifications: Partial<WorkflowTemplate> = {}
  ): Promise<WorkflowTemplate> {
    const original = await this.getTemplate(templateId);

    if (!original) {
      throw new TemplateNotFoundError(templateId);
    }

    // 포크 생성
    const forked = {
      ...original,
      ...modifications,
      id: undefined as any,
      name: modifications.name || `${original.name} (Fork)`,
      author: userId,
      visibility: "private" as const,
      downloads: 0,
      rating: 0,
      verified: false,
      forked_from: templateId,
      created_at: new Date(),
      updated_at: new Date(),
    };

    // 새 템플릿으로 생성
    return this.createTemplate(forked);
  }

  async rateTemplate(
    templateId: string,
    userId: string,
    rating: number
  ): Promise<void> {
    if (rating < 1 || rating > 5) {
      throw new Error("Rating must be between 1 and 5");
    }

    // 중복 평가 방지
    const existingRating = await this.storage.getRating(templateId, userId);
    if (existingRating) {
      throw new Error("User has already rated this template");
    }

    // 평가 저장
    await this.storage.saveRating(templateId, userId, rating);

    // 평균 평점 재계산
    const newAverage = await this.storage.calculateAverageRating(templateId);

    // 템플릿 업데이트
    await this.storage.updateRating(templateId, newAverage);
  }

  private async checkAccess(
    template: WorkflowTemplate,
    userId?: string
  ): Promise<boolean> {
    if (template.visibility === "public") {
      return true;
    }

    if (!userId) {
      return false;
    }

    if (template.author === userId) {
      return true;
    }

    if (template.visibility === "organization" && template.organization) {
      return await this.userBelongsToOrganization(
        userId,
        template.organization
      );
    }

    return false;
  }
}

// 템플릿 저장소
export class TemplateStorage {
  private db: Database;
  private s3: S3Client;

  constructor(config: StorageConfig) {
    this.db = new Database(config.database);
    this.s3 = new S3Client(config.s3);
  }

  async save(template: WorkflowTemplate): Promise<void> {
    // 메타데이터는 DB에 저장
    await this.db.templates.upsert({
      id: template.id,
      name: template.name,
      version: template.version,
      description: template.description,
      category: template.category,
      tags: template.tags,
      author: template.author,
      organization: template.organization,
      visibility: template.visibility,
      created_at: template.created_at,
      updated_at: template.updated_at,
      downloads: template.downloads,
      rating: template.rating,
      verified: template.verified,
    });

    // 템플릿 정의는 S3에 저장
    const definitionKey = `templates/${template.id}/definition.json`;
    await this.s3.putObject({
      Bucket: "workflow-templates",
      Key: definitionKey,
      Body: JSON.stringify(template.definition),
      ContentType: "application/json",
    });

    // 파라미터 저장
    const parametersKey = `templates/${template.id}/parameters.json`;
    await this.s3.putObject({
      Bucket: "workflow-templates",
      Key: parametersKey,
      Body: JSON.stringify(template.parameters),
      ContentType: "application/json",
    });

    // 예제 저장
    for (let i = 0; i < template.examples.length; i++) {
      const exampleKey = `templates/${template.id}/examples/${i}.json`;
      await this.s3.putObject({
        Bucket: "workflow-templates",
        Key: exampleKey,
        Body: JSON.stringify(template.examples[i]),
        ContentType: "application/json",
      });
    }
  }

  async get(templateId: string): Promise<WorkflowTemplate | null> {
    // 메타데이터 로드
    const metadata = await this.db.templates.findById(templateId);
    if (!metadata) {
      return null;
    }

    // 템플릿 정의 로드
    const definitionKey = `templates/${templateId}/definition.json`;
    const definitionObj = await this.s3.getObject({
      Bucket: "workflow-templates",
      Key: definitionKey,
    });
    const definition = JSON.parse(definitionObj.Body.toString());

    // 파라미터 로드
    const parametersKey = `templates/${templateId}/parameters.json`;
    const parametersObj = await this.s3.getObject({
      Bucket: "workflow-templates",
      Key: parametersKey,
    });
    const parameters = JSON.parse(parametersObj.Body.toString());

    // 예제 로드
    const examples = await this.loadExamples(templateId);

    return {
      ...metadata,
      definition,
      parameters,
      examples,
    };
  }

  private async loadExamples(templateId: string): Promise<TemplateExample[]> {
    const examples: TemplateExample[] = [];
    let i = 0;

    while (true) {
      try {
        const exampleKey = `templates/${templateId}/examples/${i}.json`;
        const exampleObj = await this.s3.getObject({
          Bucket: "workflow-templates",
          Key: exampleKey,
        });
        examples.push(JSON.parse(exampleObj.Body.toString()));
        i++;
      } catch (error) {
        if (error.Code === "NoSuchKey") {
          break;
        }
        throw error;
      }
    }

    return examples;
  }
}

// 템플릿 인덱서
export class TemplateIndexer {
  private searchClient: ElasticsearchClient;

  constructor(config: SearchConfig) {
    this.searchClient = new ElasticsearchClient(config);
  }

  async index(template: WorkflowTemplate): Promise<void> {
    const document = {
      id: template.id,
      name: template.name,
      description: template.description,
      category: template.category,
      tags: template.tags,
      author: template.author,
      organization: template.organization,
      visibility: template.visibility,
      downloads: template.downloads,
      rating: template.rating,
      verified: template.verified,
      created_at: template.created_at,

      // 검색용 필드
      search_text: `${template.name} ${template.description} ${template.tags.join(" ")}`,

      // 패싯용 필드
      category_facet: template.category,
      tags_facet: template.tags,
      author_facet: template.author,
      visibility_facet: template.visibility,
    };

    await this.searchClient.index({
      index: "workflow-templates",
      id: template.id,
      body: document,
    });
  }

  async search(query: TemplateSearchQuery): Promise<SearchResult> {
    const searchBody = {
      query: this.buildQuery(query),
      aggs: this.buildAggregations(),
      from: (query.page - 1) * query.limit,
      size: query.limit,
      sort: this.buildSort(query.sort),
    };

    const response = await this.searchClient.search({
      index: "workflow-templates",
      body: searchBody,
    });

    return {
      hits: response.hits.hits.map((hit) => ({
        id: hit._id,
        score: hit._score,
        ...hit._source,
      })),
      total: response.hits.total.value,
      aggregations: response.aggregations,
    };
  }

  private buildQuery(query: TemplateSearchQuery): any {
    const must = [];
    const filter = [];

    // 텍스트 검색
    if (query.text) {
      must.push({
        multi_match: {
          query: query.text,
          fields: ["name^3", "description^2", "tags", "search_text"],
          type: "best_fields",
          fuzziness: "AUTO",
        },
      });
    }

    // 필터
    if (query.filters) {
      if (query.filters.category) {
        filter.push({
          term: { category_facet: query.filters.category },
        });
      }

      if (query.filters.tags && query.filters.tags.length > 0) {
        filter.push({
          terms: { tags_facet: query.filters.tags },
        });
      }

      if (query.filters.author) {
        filter.push({
          term: { author_facet: query.filters.author },
        });
      }

      if (query.filters.visibility) {
        filter.push({
          term: { visibility_facet: query.filters.visibility },
        });
      }

      if (query.filters.verified !== undefined) {
        filter.push({
          term: { verified: query.filters.verified },
        });
      }

      if (query.filters.minRating) {
        filter.push({
          range: { rating: { gte: query.filters.minRating } },
        });
      }
    }

    return {
      bool: {
        must,
        filter,
      },
    };
  }

  private buildAggregations(): any {
    return {
      categories: {
        terms: {
          field: "category_facet",
          size: 20,
        },
      },
      tags: {
        terms: {
          field: "tags_facet",
          size: 50,
        },
      },
      authors: {
        terms: {
          field: "author_facet",
          size: 20,
        },
      },
      visibility: {
        terms: {
          field: "visibility_facet",
        },
      },
      rating_ranges: {
        range: {
          field: "rating",
          ranges: [
            { from: 4, to: 5, key: "4-5 stars" },
            { from: 3, to: 4, key: "3-4 stars" },
            { from: 2, to: 3, key: "2-3 stars" },
            { from: 1, to: 2, key: "1-2 stars" },
          ],
        },
      },
    };
  }

  private buildSort(sort?: TemplateSort): any {
    if (!sort) {
      return [{ downloads: "desc" }, { rating: "desc" }];
    }

    switch (sort.field) {
      case "downloads":
        return [{ downloads: sort.order }];
      case "rating":
        return [{ rating: sort.order }];
      case "created_at":
        return [{ created_at: sort.order }];
      case "name":
        return [{ "name.keyword": sort.order }];
      default:
        return [{ _score: "desc" }];
    }
  }
}
```

**검증 기준**:

- [ ] 템플릿 CRUD 작업
- [ ] 검색 및 필터링
- [ ] 버전 관리
- [ ] 권한 및 공유

#### SubTask 5.6.2: 템플릿 파라미터화 시스템

**담당자**: 템플릿 엔진 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/orchestration/templates/parameterization.ts
export interface TemplateParameter {
  name: string;
  type: ParameterType;
  description?: string;
  required: boolean;
  default?: any;
  validation?: ParameterValidation;
  ui_hints?: UIHints;
}

export enum ParameterType {
  STRING = "string",
  NUMBER = "number",
  BOOLEAN = "boolean",
  ARRAY = "array",
  OBJECT = "object",
  CHOICE = "choice",
  FILE = "file",
  SECRET = "secret",
  TEMPLATE_REF = "template_ref",
}

export interface ParameterValidation {
  // String validations
  minLength?: number;
  maxLength?: number;
  pattern?: string;

  // Number validations
  min?: number;
  max?: number;
  step?: number;

  // Array validations
  minItems?: number;
  maxItems?: number;
  uniqueItems?: boolean;

  // Choice validations
  choices?: any[];

  // Custom validation
  custom?: string; // JavaScript expression
}

export class TemplateParameterizer {
  private validator: ParameterValidator;
  private resolver: ParameterResolver;
  private transformer: ParameterTransformer;

  constructor() {
    this.validator = new ParameterValidator();
    this.resolver = new ParameterResolver();
    this.transformer = new ParameterTransformer();
  }

  async instantiateTemplate(
    template: WorkflowTemplate,
    parameters: Record<string, any>
  ): Promise<WorkflowDefinition> {
    // 1. 파라미터 검증
    const validation = await this.validator.validateParameters(
      template.parameters,
      parameters
    );

    if (!validation.valid) {
      throw new ParameterValidationError(validation.errors);
    }

    // 2. 기본값 적용
    const resolvedParams = this.applyDefaults(template.parameters, parameters);

    // 3. 템플릿 변환
    const transformed = await this.transformer.transform(
      template.definition,
      resolvedParams
    );

    // 4. 후처리
    const postProcessed = await this.postProcess(transformed, resolvedParams);

    return postProcessed;
  }

  private applyDefaults(
    paramDefs: TemplateParameter[],
    provided: Record<string, any>
  ): Record<string, any> {
    const result = { ...provided };

    for (const paramDef of paramDefs) {
      if (!(paramDef.name in result) && paramDef.default !== undefined) {
        result[paramDef.name] = paramDef.default;
      }
    }

    return result;
  }

  async generateParameterForm(
    template: WorkflowTemplate
  ): Promise<ParameterForm> {
    const form: ParameterForm = {
      sections: [],
      validation: {},
      dependencies: {},
    };

    // 파라미터를 섹션별로 그룹화
    const sections = this.groupParameters(template.parameters);

    for (const [sectionName, params] of sections) {
      const section: FormSection = {
        name: sectionName,
        title: this.humanize(sectionName),
        fields: [],
      };

      for (const param of params) {
        const field = await this.generateField(param);
        section.fields.push(field);

        // 검증 규칙 추가
        if (param.validation) {
          form.validation[param.name] = param.validation;
        }
      }

      form.sections.push(section);
    }

    // 파라미터 간 의존성 분석
    form.dependencies = this.analyzeDependencies(template.parameters);

    return form;
  }

  private async generateField(param: TemplateParameter): Promise<FormField> {
    const field: FormField = {
      name: param.name,
      label: param.ui_hints?.label || this.humanize(param.name),
      type: this.mapParameterTypeToFieldType(param.type),
      required: param.required,
      description: param.description,
      placeholder: param.ui_hints?.placeholder,
      help: param.ui_hints?.help,
    };

    // 타입별 특수 처리
    switch (param.type) {
      case ParameterType.CHOICE:
        field.options = param.validation?.choices?.map((choice) => ({
          value: choice.value || choice,
          label: choice.label || choice,
        }));
        break;

      case ParameterType.FILE:
        field.accept = param.ui_hints?.accept;
        field.maxSize = param.validation?.maxSize;
        break;

      case ParameterType.SECRET:
        field.type = "password";
        field.autocomplete = "off";
        break;

      case ParameterType.TEMPLATE_REF:
        field.type = "template-selector";
        field.templateFilter = param.ui_hints?.templateFilter;
        break;
    }

    return field;
  }
}

// 파라미터 변환기
export class ParameterTransformer {
  private templateEngine: TemplateEngine;
  private expressionEvaluator: ExpressionEvaluator;

  constructor() {
    this.templateEngine = new TemplateEngine();
    this.expressionEvaluator = new ExpressionEvaluator();
  }

  async transform(
    definition: TemplateDefinition,
    parameters: Record<string, any>
  ): Promise<WorkflowDefinition> {
    // 깊은 복사
    const result = _.cloneDeep(definition);

    // 컨텍스트 생성
    const context = this.createTransformContext(parameters);

    // 재귀적 변환
    await this.transformNode(result, context);

    return result as WorkflowDefinition;
  }

  private async transformNode(
    node: any,
    context: TransformContext
  ): Promise<void> {
    if (typeof node === "string") {
      // 문자열 템플릿 처리
      return this.transformString(node, context);
    } else if (Array.isArray(node)) {
      // 배열 처리
      for (let i = 0; i < node.length; i++) {
        node[i] = await this.transformNode(node[i], context);
      }
    } else if (typeof node === "object" && node !== null) {
      // 객체 처리
      for (const key of Object.keys(node)) {
        // 특수 키 처리
        if (key === "$if") {
          await this.handleConditional(node, context);
        } else if (key === "$foreach") {
          await this.handleLoop(node, context);
        } else if (key === "$include") {
          await this.handleInclude(node, context);
        } else {
          // 일반 속성 변환
          node[key] = await this.transformNode(node[key], context);
        }
      }
    }

    return node;
  }

  private async transformString(
    str: string,
    context: TransformContext
  ): Promise<any> {
    // 템플릿 변수 패턴: ${variable}
    const templatePattern = /\$\{([^}]+)\}/g;

    // 표현식 패턴: ${{expression}}
    const expressionPattern = /\$\{\{([^}]+)\}\}/g;

    let result = str;

    // late{s} 처리
    result = await this.templateEngine.render(result, context.parameters);

    // 표현식 처리
    const expressions = result.matchAll(expressionPattern);
    for (const match of expressions) {
      const expression = match[1];
      const value = await this.expressionEvaluator.evaluate(
        expression,
        context
      );
      result = result.replace(match[0], value);
    }

    // 타입 변환 시도
    if (result === str) {
      // 변환되지 않은 경우 원본 반환
      return str;
    } else if (result === "true" || result === "false") {
      return result === "true";
    } else if (!isNaN(Number(result))) {
      return Number(result);
    }

    return result;
  }

  private async handleConditional(
    node: any,
    context: TransformContext
  ): Promise<void> {
    const condition = node.$if;
    const thenBlock = node.$then;
    const elseBlock = node.$else;

    const conditionResult = await this.expressionEvaluator.evaluate(
      condition,
      context
    );

    if (conditionResult) {
      // then 블록 적용
      Object.assign(node, thenBlock);
    } else if (elseBlock) {
      // else 블록 적용
      Object.assign(node, elseBlock);
    }

    // 특수 키 제거
    delete node.$if;
    delete node.$then;
    delete node.$else;
  }

  private async handleLoop(
    node: any,
    context: TransformContext
  ): Promise<void> {
    const loopSpec = node.$foreach;
    const itemVar = loopSpec.item || "item";
    const indexVar = loopSpec.index || "index";
    const collection = await this.resolveValue(loopSpec.in, context);
    const template = node.$body;

    if (!Array.isArray(collection)) {
      throw new Error(`$foreach requires an array, got ${typeof collection}`);
    }

    const results = [];

    for (let i = 0; i < collection.length; i++) {
      // 루프 컨텍스트 생성
      const loopContext = {
        ...context,
        [itemVar]: collection[i],
        [indexVar]: i,
      };

      // 템플릿 인스턴스화
      const instance = _.cloneDeep(template);
      await this.transformNode(instance, loopContext);
      results.push(instance);
    }

    // 결과로 대체
    if (node.$target) {
      node[node.$target] = results;
      delete node.$foreach;
      delete node.$body;
      delete node.$target;
    } else {
      // 부모 노드를 배열로 대체
      return results;
    }
  }
}

// 파라미터 검증기
export class ParameterValidator {
  async validateParameters(
    definitions: TemplateParameter[],
    provided: Record<string, any>
  ): Promise<ValidationResult> {
    const errors: ValidationError[] = [];

    for (const def of definitions) {
      const value = provided[def.name];

      // 필수 파라미터 검사
      if (def.required && value === undefined) {
        errors.push({
          parameter: def.name,
          message: `Required parameter '${def.name}' is missing`,
          type: "required",
        });
        continue;
      }

      if (value !== undefined) {
        // 타입 검증
        const typeErrors = this.validateType(def, value);
        errors.push(...typeErrors);

        // 제약 조건 검증
        if (def.validation) {
          const constraintErrors = await this.validateConstraints(def, value);
          errors.push(...constraintErrors);
        }
      }
    }

    // 추가 파라미터 검사
    const definedNames = new Set(definitions.map((d) => d.name));
    for (const providedName of Object.keys(provided)) {
      if (!definedNames.has(providedName)) {
        errors.push({
          parameter: providedName,
          message: `Unknown parameter '${providedName}'`,
          type: "unknown",
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  private validateType(def: TemplateParameter, value: any): ValidationError[] {
    const errors: ValidationError[] = [];

    switch (def.type) {
      case ParameterType.STRING:
        if (typeof value !== "string") {
          errors.push({
            parameter: def.name,
            message: `Expected string, got ${typeof value}`,
            type: "type_mismatch",
          });
        }
        break;

      case ParameterType.NUMBER:
        if (typeof value !== "number") {
          errors.push({
            parameter: def.name,
            message: `Expected number, got ${typeof value}`,
            type: "type_mismatch",
          });
        }
        break;

      case ParameterType.BOOLEAN:
        if (typeof value !== "boolean") {
          errors.push({
            parameter: def.name,
            message: `Expected boolean, got ${typeof value}`,
            type: "type_mismatch",
          });
        }
        break;

      case ParameterType.ARRAY:
        if (!Array.isArray(value)) {
          errors.push({
            parameter: def.name,
            message: `Expected array, got ${typeof value}`,
            type: "type_mismatch",
          });
        }
        break;

      case ParameterType.OBJECT:
        if (typeof value !== "object" || value === null) {
          errors.push({
            parameter: def.name,
            message: `Expected object, got ${typeof value}`,
            type: "type_mismatch",
          });
        }
        break;
    }

    return errors;
  }

  private async validateConstraints(
    def: TemplateParameter,
    value: any
  ): Promise<ValidationError[]> {
    const errors: ValidationError[] = [];
    const validation = def.validation!;

    // String constraints
    if (def.type === ParameterType.STRING) {
      if (validation.minLength && value.length < validation.minLength) {
        errors.push({
          parameter: def.name,
          message: `Minimum length is ${validation.minLength}`,
          type: "constraint_violation",
        });
      }

      if (validation.maxLength && value.length > validation.maxLength) {
        errors.push({
          parameter: def.name,
          message: `Maximum length is ${validation.maxLength}`,
          type: "constraint_violation",
        });
      }

      if (validation.pattern) {
        const regex = new RegExp(validation.pattern);
        if (!regex.test(value)) {
          errors.push({
            parameter: def.name,
            message: `Does not match pattern: ${validation.pattern}`,
            type: "constraint_violation",
          });
        }
      }
    }

    // Number constraints
    if (def.type === ParameterType.NUMBER) {
      if (validation.min !== undefined && value < validation.min) {
        errors.push({
          parameter: def.name,
          message: `Minimum value is ${validation.min}`,
          type: "constraint_violation",
        });
      }

      if (validation.max !== undefined && value > validation.max) {
        errors.push({
          parameter: def.name,
          message: `Maximum value is ${validation.max}`,
          type: "constraint_violation",
        });
      }
    }

    // Choice constraints
    if (def.type === ParameterType.CHOICE && validation.choices) {
      const validChoices = validation.choices.map((c) => c.value || c);
      if (!validChoices.includes(value)) {
        errors.push({
          parameter: def.name,
          message: `Invalid choice. Must be one of: ${validChoices.join(", ")}`,
          type: "constraint_violation",
        });
      }
    }

    // Custom validation
    if (validation.custom) {
      try {
        const customResult = await this.evaluateCustomValidation(
          validation.custom,
          value,
          def
        );
        if (!customResult.valid) {
          errors.push({
            parameter: def.name,
            message: customResult.message || "Custom validation failed",
            type: "custom_validation",
          });
        }
      } catch (e) {
        errors.push({
          parameter: def.name,
          message: `Custom validation error: ${e.message}`,
          type: "validation_error",
        });
      }
    }

    return errors;
  }

  private async evaluateCustomValidation(
    expression: string,
    value: any,
    parameter: TemplateParameter
  ): Promise<{ valid: boolean; message?: string }> {
    // 안전한 컨텍스트에서 표현식 평가
    const sandbox = {
      value,
      parameter,
      // 유틸리티 함수들
      isEmail: (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
      isURL: (v: string) => {
        try {
          new URL(v);
          return true;
        } catch {
          return false;
        }
      },
      isUUID: (v: string) =>
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
          v
        ),
    };

    // 표현식 실행
    const fn = new Function(...Object.keys(sandbox), `return ${expression}`);
    const result = fn(...Object.values(sandbox));

    if (typeof result === "boolean") {
      return { valid: result };
    } else if (typeof result === "object" && result !== null) {
      return result;
    } else {
      return {
        valid: false,
        message: "Validation must return boolean or {valid, message}",
      };
    }
  }
}
```

**검증 기준**:

- [ ] 파라미터 정의 시스템
- [ ] 템플릿 변환 엔진
- [ ] 동적 폼 생성
- [ ] 검증 및 타입 체크

#### SubTask 5.6.3: 템플릿 상속 및 확장 메커니즘

**담당자**: 템플릿 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/orchestration/templates/inheritance.ts
export interface TemplateInheritance {
  extends?: string; // 부모 템플릿 ID
  abstract?: boolean; // 추상 템플릿 여부
  overrides?: string[]; // 오버라이드 가능한 섹션
  final?: string[]; // 오버라이드 불가능한 섹션
  mixins?: string[]; // 믹스인 템플릿 ID들
}

export class TemplateInheritanceEngine {
  private templateRepo: TemplateRepository;
  private mergeEngine: TemplateMergeEngine;
  private overrideValidator: OverrideValidator;

  constructor(repo: TemplateRepository) {
    this.templateRepo = repo;
    this.mergeEngine = new TemplateMergeEngine();
    this.overrideValidator = new OverrideValidator();
  }

  async resolveTemplate(
    templateId: string,
    visited: Set<string> = new Set()
  ): Promise<ResolvedTemplate> {
    // 순환 참조 방지
    if (visited.has(templateId)) {
      throw new CircularInheritanceError(
        `Circular inheritance detected: ${Array.from(visited).join(" -> ")} -> ${templateId}`
      );
    }
    visited.add(templateId);

    // 템플릿 로드
    const template = await this.templateRepo.getTemplate(templateId);
    if (!template) {
      throw new TemplateNotFoundError(templateId);
    }

    // 상속 정보 확인
    const inheritance = template.definition.inheritance;
    if (!inheritance || !inheritance.extends) {
      // 기본 템플릿인 경우
      return this.applyMixins(template, inheritance);
    }

    // 부모 템플릿 해결
    const parent = await this.resolveTemplate(
      inheritance.extends,
      new Set(visited)
    );

    // 상속 검증
    await this.validateInheritance(parent, template);

    // 템플릿 병합
    const merged = await this.mergeTemplates(parent, template);

    // 믹스인 적용
    return this.applyMixins(merged, inheritance);
  }

  private async validateInheritance(
    parent: ResolvedTemplate,
    child: WorkflowTemplate
  ): Promise<void> {
    const parentDef = parent.definition;
    const childDef = child.definition;

    // 추상 템플릿은 직접 사용 불가
    if (parentDef.inheritance?.abstract) {
      // 자식도 추상이어야 함
      if (!childDef.inheritance?.abstract) {
        throw new InheritanceError(
          "Cannot extend abstract template unless child is also abstract"
        );
      }
    }

    // final 섹션 오버라이드 검사
    if (parentDef.inheritance?.final) {
      const overrides = this.findOverrides(parentDef, childDef);
      const violations = overrides.filter((o) =>
        parentDef.inheritance!.final!.includes(o)
      );

      if (violations.length > 0) {
        throw new InheritanceError(
          `Cannot override final sections: ${violations.join(", ")}`
        );
      }
    }

    // 필수 오버라이드 검사
    if (parentDef.inheritance?.overrides) {
      const required = parentDef.inheritance.overrides
        .filter((o) => o.startsWith("required:"))
        .map((o) => o.substring(9));

      const implemented = this.findOverrides(parentDef, childDef);
      const missing = required.filter((r) => !implemented.includes(r));

      if (missing.length > 0) {
        throw new InheritanceError(
          `Missing required overrides: ${missing.join(", ")}`
        );
      }
    }
  }

  private async mergeTemplates(
    parent: ResolvedTemplate,
    child: WorkflowTemplate
  ): Promise<ResolvedTemplate> {
    const merged = _.cloneDeep(parent);

    // 메타데이터 병합
    merged.name = child.name;
    merged.version = child.version;
    merged.description = child.description;
    merged.author = child.author;

    // 파라미터 병합
    merged.parameters = this.mergeParameters(
      parent.parameters,
      child.parameters
    );

    // 정의 병합
    merged.definition = await this.mergeEngine.merge(
      parent.definition,
      child.definition,
      {
        strategy: "override",
        preservePaths: parent.definition.inheritance?.final || [],
      }
    );

    // 상속 체인 업데이트
    merged.inheritanceChain = [
      ...(parent.inheritanceChain || []),
      {
        templateId: child.id,
        templateName: child.name,
        version: child.version,
      },
    ];

    return merged;
  }

  private mergeParameters(
    parentParams: TemplateParameter[],
    childParams: TemplateParameter[]
  ): TemplateParameter[] {
    const merged = [...parentParams];
    const parentNames = new Set(parentParams.map((p) => p.name));

    for (const childParam of childParams) {
      const existingIndex = merged.findIndex((p) => p.name === childParam.name);

      if (existingIndex >= 0) {
        // 오버라이드
        merged[existingIndex] = this.mergeParameter(
          merged[existingIndex],
          childParam
        );
      } else {
        // 새 파라미터
        merged.push(childParam);
      }
    }

    return merged;
  }

  private mergeParameter(
    parent: TemplateParameter,
    child: TemplateParameter
  ): TemplateParameter {
    return {
      ...parent,
      ...child,
      // 검증 규칙은 병합
      validation: {
        ...parent.validation,
        ...child.validation,
      },
      // UI 힌트도 병합
      ui_hints: {
        ...parent.ui_hints,
        ...child.ui_hints,
      },
    };
  }

  private async applyMixins(
    template: ResolvedTemplate,
    inheritance?: TemplateInheritance
  ): Promise<ResolvedTemplate> {
    if (!inheritance?.mixins || inheritance.mixins.length === 0) {
      return template;
    }

    let result = template;

    for (const mixinId of inheritance.mixins) {
      const mixin = await this.templateRepo.getTemplate(mixinId);

      if (!mixin) {
        throw new TemplateNotFoundError(`Mixin ${mixinId} not found`);
      }

      // 믹스인은 특정 섹션만 제공
      result = await this.applyMixin(result, mixin);
    }

    return result;
  }

  private async applyMixin(
    target: ResolvedTemplate,
    mixin: WorkflowTemplate
  ): Promise<ResolvedTemplate> {
    const mixinDef = mixin.definition;

    // 믹스인에서 제공하는 섹션 식별
    const providedSections = mixinDef.mixin?.provides || [];

    for (const section of providedSections) {
      const sectionData = _.get(mixinDef, section);

      if (sectionData) {
        // 타겟에 섹션 추가/병합
        const existing = _.get(target.definition, section);

        if (existing && Array.isArray(existing) && Array.isArray(sectionData)) {
          // 배열 병합
          _.set(target.definition, section, [...existing, ...sectionData]);
        } else if (
          existing &&
          typeof existing === "object" &&
          typeof sectionData === "object"
        ) {
          // 객체 병합
          _.set(target.definition, section, _.merge({}, existing, sectionData));
        } else {
          // 덮어쓰기
          _.set(target.definition, section, sectionData);
        }
      }
    }

    // 믹스인 체인에 추가
    target.mixinChain = [
      ...(target.mixinChain || []),
      {
        templateId: mixin.id,
        templateName: mixin.name,
        sections: providedSections,
      },
    ];

    return target;
  }
}

// 템플릿 확장 빌더
export class TemplateExtensionBuilder {
  private baseTemplate: WorkflowTemplate;
  private extensions: TemplateExtension[] = [];

  constructor(baseTemplate: WorkflowTemplate) {
    this.baseTemplate = baseTemplate;
  }

  extend(extension: TemplateExtension): this {
    this.extensions.push(extension);
    return this;
  }

  override(path: string, value: any): this {
    this.extensions.push({
      type: "override",
      path,
      value,
    });
    return this;
  }

  addTask(position: string, task: WorkflowTask): this {
    this.extensions.push({
      type: "add_task",
      position,
      task,
    });
    return this;
  }

  removeTask(taskId: string): this {
    this.extensions.push({
      type: "remove_task",
      taskId,
    });
    return this;
  }

  modifyTask(taskId: string, modifications: Partial<WorkflowTask>): this {
    this.extensions.push({
      type: "modify_task",
      taskId,
      modifications,
    });
    return this;
  }

  addParameter(parameter: TemplateParameter): this {
    this.extensions.push({
      type: "add_parameter",
      parameter,
    });
    return this;
  }

  build(): ExtendedTemplate {
    const extended = _.cloneDeep(this.baseTemplate);

    // 확장 적용
    for (const extension of this.extensions) {
      this.applyExtension(extended, extension);
    }

    // 상속 정보 추가
    extended.definition.inheritance = {
      extends: this.baseTemplate.id,
      overrides: this.collectOverrides(),
    };

    return extended;
  }

  private applyExtension(
    template: WorkflowTemplate,
    extension: TemplateExtension
  ): void {
    switch (extension.type) {
      case "override":
        _.set(template.definition, extension.path, extension.value);
        break;

      case "add_task":
        const tasks = template.definition.tasks || [];
        const position = this.findPosition(tasks, extension.position);
        tasks.splice(position, 0, extension.task);
        break;

      case "remove_task":
        template.definition.tasks = template.definition.tasks?.filter(
          (t) => t.id !== extension.taskId
        );
        break;

      case "modify_task":
        const task = template.definition.tasks?.find(
          (t) => t.id === extension.taskId
        );
        if (task) {
          Object.assign(task, extension.modifications);
        }
        break;

      case "add_parameter":
        template.parameters.push(extension.parameter);
        break;
    }
  }

  private collectOverrides(): string[] {
    return this.extensions
      .filter((e) => e.type === "override")
      .map((e) => e.path);
  }
}

// 템플릿 조합기
export class TemplateComposer {
  async composeTemplate(
    composition: TemplateComposition
  ): Promise<WorkflowTemplate> {
    const templates: WorkflowTemplate[] = [];

    // 모든 템플릿 로드
    for (const ref of composition.templates) {
      const template = await this.loadTemplateRef(ref);
      templates.push(template);
    }

    // 조합 전략에 따라 병합
    let composed: WorkflowTemplate;

    switch (composition.strategy) {
      case "sequential":
        composed = this.composeSequential(templates);
        break;

      case "parallel":
        composed = this.composeParallel(templates);
        break;

      case "conditional":
        composed = this.composeConditional(templates, composition.conditions!);
        break;

      case "pipeline":
        composed = this.composePipeline(templates);
        break;

      default:
        throw new Error(
          `Unknown composition strategy: ${composition.strategy}`
        );
    }

    // 메타데이터 설정
    composed.name = composition.name;
    composed.description = composition.description;
    composed.composition = composition;

    return composed;
  }

  private composeSequential(templates: WorkflowTemplate[]): WorkflowTemplate {
    const composed = this.createEmptyTemplate();

    // 순차적으로 태스크 연결
    let lastTasks: string[] = [];

    for (const template of templates) {
      const offset = composed.definition.tasks.length;

      // 태스크 복사 (ID 조정)
      const adjustedTasks = template.definition.tasks.map((task, index) => ({
        ...task,
        id: `${template.id}_${task.id}`,
        dependencies: [
          ...task.dependencies.map((d) => ({
            ...d,
            task_id: `${template.id}_${d.task_id}`,
          })),
          // 이전 템플릿의 마지막 태스크들에 의존
          ...lastTasks.map((taskId) => ({
            task_id: taskId,
            wait_for_completion: true,
          })),
        ],
      }));

      composed.definition.tasks.push(...adjustedTasks);

      // 이 템플릿의 마지막 태스크들 찾기
      lastTasks = this.findTerminalTasks(adjustedTasks);

      // 파라미터 병합
      composed.parameters.push(...template.parameters);
    }

    return composed;
  }

  private composeParallel(templates: WorkflowTemplate[]): WorkflowTemplate {
    const composed = this.createEmptyTemplate();

    // 병렬 블록 생성
    const parallelBlock: ParallelBlock = {
      id: "parallel_composition",
      tasks: [],
      max_concurrency: templates.length,
    };

    for (const template of templates) {
      // 각 템플릿을 서브워크플로우로 변환
      const subWorkflow = {
        id: `sub_${template.id}`,
        type: "subworkflow",
        workflow_id: template.id,
        input_mapping: this.createInputMapping(template),
        output_mapping: this.createOutputMapping(template),
      };

      parallelBlock.tasks.push(subWorkflow);
    }

    composed.definition.tasks.push(parallelBlock);

    // 모든 파라미터 병합 (중복 제거)
    const paramMap = new Map<string, TemplateParameter>();

    for (const template of templates) {
      for (const param of template.parameters) {
        if (!paramMap.has(param.name)) {
          paramMap.set(param.name, param);
        }
      }
    }

    composed.parameters = Array.from(paramMap.values());

    return composed;
  }
}
```

**검증 기준**:

- [ ] 템플릿 상속 시스템
- [ ] 믹스인 지원
- [ ] 확장 빌더 API
- [ ] 템플릿 조합 전략

#### SubTask 5.6.4: 템플릿 공유 마켓플레이스

**담당자**: 풀스택 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/orchestration/templates/marketplace.ts
export class TemplateMarketplace {
  private repository: TemplateRepository;
  private reviewService: TemplateReviewService;
  private analyticsService: TemplateAnalyticsService;
  private paymentService: PaymentService;

  constructor(config: MarketplaceConfig) {
    this.repository = new TemplateRepository(config.repository);
    this.reviewService = new TemplateReviewService();
    this.analyticsService = new TemplateAnalyticsService();
    this.paymentService = new PaymentService(config.payment);
  }

  async publishTemplate(
    template: WorkflowTemplate,
    publishOptions: PublishOptions
  ): Promise<PublishedTemplate> {
    // 1. 품질 검사
    const qualityCheck = await this.performQualityCheck(template);

    if (!qualityCheck.passed) {
      throw new QualityCheckError(qualityCheck.issues);
    }

    // 2. 라이선스 설정
    template.license = publishOptions.license || "MIT";
    template.pricing = publishOptions.pricing || { type: "free" };

    // 3. 카테고리 자동 분류
    if (!template.category) {
      template.category = await this.categorizeTemplate(template);
    }

    // 4. 태그 자동 생성
    const autoTags = await this.generateTags(template);
    template.tags = [...new Set([...template.tags, ...autoTags])];

    // 5. 검증 마크 부여 (조건 충족 시)
    if (await this.qualifiesForVerification(template)) {
      template.verified = true;
    }

    // 6. 저장 및 발행
    const published = await this.repository.createTemplate(template);

    // 7. 검색 인덱싱
    await this.indexForSearch(published);

    // 8. 알림 발송
    await this.notifyFollowers(published);

    return {
      ...published,
      publishedAt: new Date(),
      status: "published",
    };
  }

  async purchaseTemplate(
    templateId: string,
    userId: string,
    paymentMethod: PaymentMethod
  ): Promise<PurchaseResult> {
    const template = await this.repository.getTemplate(templateId);

    if (!template) {
      throw new TemplateNotFoundError(templateId);
    }

    // 무료 템플릿 처리
    if (template.pricing.type === "free") {
      return {
        success: true,
        templateId,
        transactionId: null,
        accessGranted: true,
      };
    }

    // 이미 구매한 경우
    if (await this.hasAccess(userId, templateId)) {
      return {
        success: true,
        templateId,
        transactionId: "existing",
        accessGranted: true,
      };
    }

    // 결제 처리
    const payment = await this.paymentService.processPayment({
      amount: template.pricing.amount,
      currency: template.pricing.currency,
      userId,
      templateId,
      paymentMethod,
    });

    if (payment.success) {
      // 접근 권한 부여
      await this.grantAccess(userId, templateId);

      // 판매자에게 수익 분배
      await this.distributeRevenue(
        template.author,
        payment.amount,
        template.pricing.revenueShare || 0.7
      );

      // 판매 통계 업데이트
      await this.analyticsService.recordPurchase(templateId, userId);
    }

    return {
      success: payment.success,
      templateId,
      transactionId: payment.transactionId,
      accessGranted: payment.success,
    };
  }

  async getMarketplaceStats(): Promise<MarketplaceStats> {
    const stats = await this.analyticsService.getGlobalStats();

    return {
      totalTemplates: stats.templateCount,
      totalAuthors: stats.authorCount,
      totalDownloads: stats.downloadCount,
      totalRevenue: stats.totalRevenue,
      topCategories: await this.getTopCategories(),
      trendingTemplates: await this.getTrendingTemplates(),
      featuredTemplates: await this.getFeaturedTemplates(),
    };
  }

  async reviewTemplate(
    templateId: string,
    userId: string,
    review: TemplateReview
  ): Promise<void> {
    // 구매/사용 확인
    if (!(await this.hasUsedTemplate(userId, templateId))) {
      throw new Error("You must use the template before reviewing");
    }

    // 리뷰 저장
    await this.reviewService.addReview({
      templateId,
      userId,
      rating: review.rating,
      title: review.title,
      content: review.content,
      pros: review.pros,
      cons: review.cons,
      createdAt: new Date(),
    });

    // 평균 평점 재계산
    const avgRating =
      await this.reviewService.calculateAverageRating(templateId);
    await this.repository.updateTemplate(
      templateId,
      { rating: avgRating },
      "system"
    );

    // 작성자에게 알림
    const template = await this.repository.getTemplate(templateId);
    if (template) {
      await this.notifyAuthor(template.author, "new_review", {
        templateId,
        reviewId: review.id,
        rating: review.rating,
      });
    }
  }

  private async performQualityCheck(
    template: WorkflowTemplate
  ): Promise<QualityCheckResult> {
    const issues: QualityIssue[] = [];

    // 1. 문서화 검사
    if (!template.description || template.description.length < 100) {
      issues.push({
        severity: "error",
        category: "documentation",
        message: "Description must be at least 100 characters",
      });
    }

    if (!template.examples || template.examples.length === 0) {
      issues.push({
        severity: "error",
        category: "documentation",
        message: "At least one example is required",
      });
    }

    // 2. 파라미터 검사
    for (const param of template.parameters) {
      if (!param.description) {
        issues.push({
          severity: "warning",
          category: "parameters",
          message: `Parameter '${param.name}' lacks description`,
        });
      }
    }

    // 3. 보안 검사
    const securityIssues = await this.checkSecurity(template);
    issues.push(...securityIssues);

    // 4. 성능 검사
    const performanceIssues = await this.checkPerformance(template);
    issues.push(...performanceIssues);

    // 5. 모범 사례 검사
    const bestPracticeIssues = await this.checkBestPractices(template);
    issues.push(...bestPracticeIssues);

    return {
      passed: issues.filter((i) => i.severity === "error").length === 0,
      issues,
      score: this.calculateQualityScore(issues),
    };
  }

  private async checkSecurity(
    template: WorkflowTemplate
  ): Promise<QualityIssue[]> {
    const issues: QualityIssue[] = [];
    const securityScanner = new TemplateSecurityScanner();

    // 민감한 데이터 노출 검사
    const exposures = await securityScanner.findDataExposures(template);
    for (const exposure of exposures) {
      issues.push({
        severity: "error",
        category: "security",
        message: `Potential data exposure: ${exposure.description}`,
        location: exposure.location,
      });
    }

    // 권한 에스컬레이션 검사
    const escalations =
      await securityScanner.findPrivilegeEscalations(template);
    for (const escalation of escalations) {
      issues.push({
        severity: "warning",
        category: "security",
        message: `Potential privilege escalation: ${escalation.description}`,
        location: escalation.location,
      });
    }

    // 인젝션 취약점 검사
    const injections =
      await securityScanner.findInjectionVulnerabilities(template);
    for (const injection of injections) {
      issues.push({
        severity: "error",
        category: "security",
        message: `Potential injection vulnerability: ${injection.description}`,
        location: injection.location,
      });
    }

    return issues;
  }

  private async categorizeTemplate(
    template: WorkflowTemplate
  ): Promise<string> {
    const classifier = new TemplateCategorizer();

    // 템플릿 내용 분석
    const features = await classifier.extractFeatures(template);

    // ML 모델로 카테고리 예측
    const predictions = await classifier.predict(features);

    // 가장 높은 신뢰도의 카테고리 선택
    return predictions[0].category;
  }

  private async generateTags(template: WorkflowTemplate): Promise<string[]> {
    const tagger = new TemplateAutoTagger();

    // 다양한 소스에서 태그 추출
    const tags = new Set<string>();

    // 1. 에이전트 타입에서 추출
    const agentTypes = this.extractAgentTypes(template);
    agentTypes.forEach((type) => tags.add(type.toLowerCase()));

    // 2. 기술 스택에서 추출
    const techStack = await tagger.detectTechnologyStack(template);
    techStack.forEach((tech) => tags.add(tech.toLowerCase()));

    // 3. 도메인 키워드 추출
    const domainKeywords = await tagger.extractDomainKeywords(template);
    domainKeywords.forEach((keyword) => tags.add(keyword.toLowerCase()));

    // 4. 패턴 인식
    const patterns = await tagger.recognizePatterns(template);
    patterns.forEach((pattern) => tags.add(pattern.toLowerCase()));

    return Array.from(tags);
  }
}

// 템플릿 리뷰 서비스
export class TemplateReviewService {
  private reviewStore: ReviewStore;
  private sentimentAnalyzer: SentimentAnalyzer;
  private spamDetector: SpamDetector;

  async addReview(review: TemplateReview): Promise<void> {
    // 스팸 검사
    if (await this.spamDetector.isSpam(review.content)) {
      throw new Error("Review appears to be spam");
    }

    // 감정 분석
    review.sentiment = await this.sentimentAnalyzer.analyze(review.content);

    // 유용성 점수 초기화
    review.helpfulCount = 0;
    review.totalVotes = 0;

    // 저장
    await this.reviewStore.save(review);

    // 인사이트 추출
    await this.extractInsights(review);
  }

  async voteReview(
    reviewId: string,
    userId: string,
    helpful: boolean
  ): Promise<void> {
    // 중복 투표 방지
    if (await this.hasVoted(userId, reviewId)) {
      throw new Error("Already voted on this review");
    }

    // 투표 기록
    await this.reviewStore.recordVote(reviewId, userId, helpful);

    // 유용성 업데이트
    const review = await this.reviewStore.get(reviewId);
    if (review) {
      if (helpful) {
        review.helpfulCount++;
      }
      review.totalVotes++;
      await this.reviewStore.update(review);
    }
  }

  private async extractInsights(review: TemplateReview): Promise<void> {
    const insights = new InsightExtractor();

    // 주요 키워드 추출
    const keywords = await insights.extractKeywords(review.content);

    // 개선 제안 추출
    const suggestions = await insights.extractSuggestions(review.content);

    // 감정 트렌드 분석
    const sentimentTrend = await insights.analyzeSentimentTrend(
      review.templateId
    );

    // 인사이트 저장
    await this.storeInsights({
      templateId: review.templateId,
      reviewId: review.id,
      keywords,
      suggestions,
      sentimentTrend,
    });
  }
}

// 템플릿 분석 서비스
export class TemplateAnalyticsService {
  private metricsCollector: MetricsCollector;
  private trendAnalyzer: TrendAnalyzer;

  async recordUsage(
    templateId: string,
    userId: string,
    usage: TemplateUsage
  ): Promise<void> {
    await this.metricsCollector.record({
      type: "template_usage",
      templateId,
      userId,
      timestamp: new Date(),
      duration: usage.duration,
      success: usage.success,
      errors: usage.errors,
    });

    // 실시간 트렌드 업데이트
    await this.trendAnalyzer.updateTrend(templateId);
  }

  async getTemplateAnalytics(
    templateId: string,
    timeRange: TimeRange
  ): Promise<TemplateAnalytics> {
    const metrics = await this.metricsCollector.query({
      templateId,
      startTime: timeRange.start,
      endTime: timeRange.end,
    });

    return {
      downloads: metrics.downloads,
      uniqueUsers: metrics.uniqueUsers,
      successRate: metrics.successRate,
      averageDuration: metrics.averageDuration,
      errorRate: metrics.errorRate,
      userRetention: await this.calculateRetention(templateId, timeRange),
      geographicDistribution: await this.getGeographicDistribution(templateId),
      usagePatterns: await this.analyzeUsagePatterns(templateId),
      performanceTrends: await this.getPerformanceTrends(templateId, timeRange),
    };
  }

  async getTrendingTemplates(
    category?: string,
    limit: number = 10
  ): Promise<TrendingTemplate[]> {
    const trends = await this.trendAnalyzer.getTopTrends({
      category,
      metric: "composite", // 다운로드, 평점, 최근 활동 종합
      timeWindow: "7d",
      limit,
    });

    return trends.map((trend) => ({
      templateId: trend.entityId,
      score: trend.score,
      momentum: trend.momentum,
      rank: trend.rank,
      previousRank: trend.previousRank,
      metrics: {
        downloads: trend.metrics.downloads,
        rating: trend.metrics.rating,
        reviews: trend.metrics.reviews,
      },
    }));
  }
}
```

**검증 기준**:

- [ ] 템플릿 발행 시스템
- [ ] 품질 검사 및 검증
- [ ] 리뷰 및 평점 시스템
- [ ] 분석 및 트렌드 추적

---
