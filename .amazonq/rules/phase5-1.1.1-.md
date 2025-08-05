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
# Phase 5: 오케스트레이션 시스템 - Tasks 5.7~5.9 SubTask 구조

## 📋 Task 5.7~5.9 SubTask 리스트

### Task 5.7: 리소스 풀 관리 시스템
- **SubTask 5.7.1**: 리소스 풀 아키텍처 설계
- **SubTask 5.7.2**: 리소스 할당 및 해제 메커니즘
- **SubTask 5.7.3**: 리소스 모니터링 및 추적
- **SubTask 5.7.4**: 리소스 최적화 및 재조정

### Task 5.8: 지능형 작업 스케줄러
- **SubTask 5.8.1**: 스케줄링 알고리즘 구현
- **SubTask 5.8.2**: 우선순위 기반 큐 시스템
- **SubTask 5.8.3**: 예측 기반 스케줄링
- **SubTask 5.8.4**: 스케줄러 성능 최적화

### Task 5.9: 부하 분산 및 자동 스케일링
- **SubTask 5.9.1**: 부하 분산 전략 구현
- **SubTask 5.9.2**: 자동 스케일링 정책 엔진
- **SubTask 5.9.3**: 리소스 예측 및 사전 프로비저닝
- **SubTask 5.9.4**: 멀티 리전 분산 처리

---

## 📝 세부 작업지시서

### Task 5.7: 리소스 풀 관리 시스템

#### SubTask 5.7.1: 리소스 풀 아키텍처 설계
**담당자**: 시스템 아키텍트  
**예상 소요시간**: 14시간

**작업 내용**:
```typescript
// backend/src/orchestration/resources/resource_pool.ts
export enum ResourceType {
  CPU = 'cpu',
  MEMORY = 'memory',
  GPU = 'gpu',
  STORAGE = 'storage',
  NETWORK = 'network',
  AGENT = 'agent',
  CONTAINER = 'container',
  LAMBDA = 'lambda'
}

export interface ResourceUnit {
  id: string;
  type: ResourceType;
  capacity: number;
  unit: string; // 'cores', 'GB', 'Mbps', etc.
  available: number;
  allocated: number;
  metadata: Record<string, any>;
}

export interface ResourcePool {
  id: string;
  name: string;
  region: string;
  resources: Map<ResourceType, ResourceUnit[]>;
  policies: ResourcePolicy[];
  constraints: ResourceConstraint[];
  status: PoolStatus;
  metrics: PoolMetrics;
}

export class ResourcePoolManager {
  private pools: Map<string, ResourcePool> = new Map();
  private allocator: ResourceAllocator;
  private monitor: ResourceMonitor;
  private optimizer: ResourceOptimizer;
  
  constructor(config: ResourcePoolConfig) {
    this.allocator = new ResourceAllocator(config.allocation);
    this.monitor = new ResourceMonitor(config.monitoring);
    this.optimizer = new ResourceOptimizer(config.optimization);
  }

  async createPool(poolConfig: PoolConfiguration): Promise<ResourcePool> {
    const pool: ResourcePool = {
      id: this.generatePoolId(poolConfig.name),
      name: poolConfig.name,
      region: poolConfig.region,
      resources: new Map(),
      policies: poolConfig.policies || [],
      constraints: poolConfig.constraints || [],
      status: PoolStatus.INITIALIZING,
      metrics: {
        totalCapacity: {},
        currentUsage: {},
        peakUsage: {},
        efficiency: 0,
        lastUpdated: new Date()
      }
    };

    // 리소스 초기화
    for (const resourceDef of poolConfig.resources) {
      await this.initializeResource(pool, resourceDef);
    }

    // 정책 검증
    await this.validatePolicies(pool);

    // 모니터링 시작
    await this.monitor.startMonitoring(pool);

    // 풀 등록
    this.pools.set(pool.id, pool);
    pool.status = PoolStatus.ACTIVE;

    logger.info(`Resource pool created: ${pool.id}`);
    return pool;
  }

  private async initializeResource(
    pool: ResourcePool,
    resourceDef: ResourceDefinition
  ): Promise<void> {
    const resources: ResourceUnit[] = [];

    switch (resourceDef.type) {
      case ResourceType.CPU:
        resources.push(...await this.initializeCPUResources(resourceDef));
        break;
      
      case ResourceType.MEMORY:
        resources.push(...await this.initializeMemoryResources(resourceDef));
        break;
      
      case ResourceType.GPU:
        resources.push(...await this.initializeGPUResources(resourceDef));
        break;
      
      case ResourceType.AGENT:
        resources.push(...await this.initializeAgentResources(resourceDef));
        break;
      
      case ResourceType.CONTAINER:
        resources.push(...await this.initializeContainerResources(resourceDef));
        break;
      
      case ResourceType.LAMBDA:
        resources.push(...await this.initializeLambdaResources(resourceDef));
        break;
    }

    pool.resources.set(resourceDef.type, resources);
  }

  private async initializeCPUResources(
    def: ResourceDefinition
  ): Promise<ResourceUnit[]> {
    const cpuResources: ResourceUnit[] = [];
    const nodeInfo = await this.getNodeInformation();

    for (const node of nodeInfo) {
      const cpuResource: ResourceUnit = {
        id: `cpu-${node.id}`,
        type: ResourceType.CPU,
        capacity: node.cpuCores * def.overcommitRatio,
        unit: 'cores',
        available: node.cpuCores * def.overcommitRatio,
        allocated: 0,
        metadata: {
          nodeId: node.id,
          architecture: node.cpuArchitecture,
          model: node.cpuModel,
          frequency: node.cpuFrequency,
          numa: node.numaNodes,
          hyperthreading: node.hyperthreadingEnabled
        }
      };

      cpuResources.push(cpuResource);
    }

    return cpuResources;
  }

  async allocateResources(
    request: ResourceRequest
  ): Promise<ResourceAllocation> {
    const startTime = Date.now();

    try {
      // 1. 요청 검증
      const validation = await this.validateRequest(request);
      if (!validation.valid) {
        throw new ResourceValidationError(validation.errors);
      }

      // 2. 적합한 풀 찾기
      const candidatePools = await this.findCandidatePools(request);
      if (candidatePools.length === 0) {
        throw new NoResourceAvailableError('No suitable resource pool found');
      }

      // 3. 최적 풀 선택
      const selectedPool = await this.selectOptimalPool(
        candidatePools,
        request
      );

      // 4. 리소스 할당
      const allocation = await this.allocator.allocate(
        selectedPool,
        request
      );

      // 5. 할당 기록
      await this.recordAllocation(allocation);

      // 6. 메트릭 업데이트
      await this.updateMetrics(selectedPool, allocation);

      logger.info(`Resources allocated: ${allocation.id}`, {
        poolId: selectedPool.id,
        duration: Date.now() - startTime
      });

      return allocation;

    } catch (error) {
      logger.error('Resource allocation failed', { error, request });
      throw error;
    }
  }

  private async findCandidatePools(
    request: ResourceRequest
  ): Promise<ResourcePool[]> {
    const candidates: ResourcePool[] = [];

    for (const pool of this.pools.values()) {
      // 상태 확인
      if (pool.status !== PoolStatus.ACTIVE) {
        continue;
      }

      // 리전 확인
      if (request.regionPreference && 
          !this.matchesRegion(pool.region, request.regionPreference)) {
        continue;
      }

      // 리소스 가용성 확인
      if (await this.hasAvailableResources(pool, request)) {
        candidates.push(pool);
      }
    }

    return candidates;
  }

  private async hasAvailableResources(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<boolean> {
    for (const requirement of request.requirements) {
      const resources = pool.resources.get(requirement.type);
      
      if (!resources) {
        return false;
      }

      const availableCapacity = resources.reduce(
        (sum, resource) => sum + resource.available,
        0
      );

      if (availableCapacity < requirement.amount) {
        return false;
      }
    }

    return true;
  }

  private async selectOptimalPool(
    candidates: ResourcePool[],
    request: ResourceRequest
  ): Promise<ResourcePool> {
    const scores = new Map<string, number>();

    for (const pool of candidates) {
      const score = await this.calculatePoolScore(pool, request);
      scores.set(pool.id, score);
    }

    // 최고 점수 풀 선택
    const sorted = Array.from(scores.entries())
      .sort((a, b) => b[1] - a[1]);

    const selectedId = sorted[0][0];
    return candidates.find(p => p.id === selectedId)!;
  }

  private async calculatePoolScore(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<number> {
    let score = 100;

    // 1. 활용률 (낮을수록 좋음)
    const utilization = this.calculateUtilization(pool);
    score -= utilization * 0.3;

    // 2. 지역성 (같은 리전이면 가산점)
    if (request.regionPreference === pool.region) {
      score += 20;
    }

    // 3. 성능 메트릭
    const performanceScore = await this.getPerformanceScore(pool);
    score += performanceScore * 0.2;

    // 4. 비용 (낮을수록 좋음)
    const costScore = await this.calculateCostScore(pool, request);
    score += costScore * 0.3;

    // 5. 친화성 규칙
    const affinityScore = this.calculateAffinityScore(pool, request);
    score += affinityScore * 0.2;

    return Math.max(0, Math.min(100, score));
  }
}

// 리소스 정책
export interface ResourcePolicy {
  id: string;
  name: string;
  type: PolicyType;
  rules: PolicyRule[];
  priority: number;
  enabled: boolean;
}

export enum PolicyType {
  ALLOCATION = 'allocation',
  SCALING = 'scaling',
  EVICTION = 'eviction',
  RESERVATION = 'reservation',
  QUOTA = 'quota'
}

export class ResourcePolicyEngine {
  private policies: Map<string, ResourcePolicy[]> = new Map();

  async evaluateAllocationPolicy(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<PolicyDecision> {
    const poolPolicies = this.policies.get(pool.id) || [];
    const applicablePolicies = poolPolicies
      .filter(p => p.type === PolicyType.ALLOCATION && p.enabled)
      .sort((a, b) => b.priority - a.priority);

    for (const policy of applicablePolicies) {
      const decision = await this.evaluatePolicy(policy, {
        pool,
        request,
        currentState: await this.getCurrentState(pool)
      });

      if (decision.action === 'deny') {
        return decision;
      }

      if (decision.modifications) {
        this.applyModifications(request, decision.modifications);
      }
    }

    return { action: 'allow', reason: 'All policies passed' };
  }

  private async evaluatePolicy(
    policy: ResourcePolicy,
    context: PolicyContext
  ): Promise<PolicyDecision> {
    const results: RuleResult[] = [];

    for (const rule of policy.rules) {
      const result = await this.evaluateRule(rule, context);
      results.push(result);

      if (rule.stopOnMatch && result.matched) {
        break;
      }
    }

    // 정책 결정 로직
    return this.makeDecision(policy, results);
  }

  private async evaluateRule(
    rule: PolicyRule,
    context: PolicyContext
  ): Promise<RuleResult> {
    const evaluator = new RuleEvaluator();
    
    try {
      const matched = await evaluator.evaluate(rule.condition, context);
      
      if (matched) {
        return {
          matched: true,
          action: rule.action,
          modifications: rule.modifications,
          message: rule.message
        };
      }

      return { matched: false };

    } catch (error) {
      logger.error('Rule evaluation failed', { rule, error });
      return { 
        matched: false, 
        error: error.message 
      };
    }
  }
}

// 리소스 제약
export interface ResourceConstraint {
  id: string;
  type: ConstraintType;
  target: ConstraintTarget;
  operator: ConstraintOperator;
  value: any;
  enforcement: 'soft' | 'hard';
}

export enum ConstraintType {
  AFFINITY = 'affinity',
  ANTI_AFFINITY = 'anti_affinity',
  LOCATION = 'location',
  CAPABILITY = 'capability',
  ISOLATION = 'isolation'
}

export class ResourceConstraintEvaluator {
  async evaluate(
    constraints: ResourceConstraint[],
    allocation: CandidateAllocation
  ): Promise<ConstraintResult> {
    const violations: ConstraintViolation[] = [];
    let score = 100;

    for (const constraint of constraints) {
      const result = await this.evaluateConstraint(constraint, allocation);
      
      if (!result.satisfied) {
        if (constraint.enforcement === 'hard') {
          violations.push({
            constraint,
            reason: result.reason,
            severity: 'error'
          });
        } else {
          violations.push({
            constraint,
            reason: result.reason,
            severity: 'warning'
          });
          score -= result.penalty || 10;
        }
      } else if (result.bonus) {
        score += result.bonus;
      }
    }

    return {
      satisfied: violations.filter(v => v.severity === 'error').length === 0,
      violations,
      score: Math.max(0, Math.min(100, score))
    };
  }

  private async evaluateConstraint(
    constraint: ResourceConstraint,
    allocation: CandidateAllocation
  ): Promise<SingleConstraintResult> {
    switch (constraint.type) {
      case ConstraintType.AFFINITY:
        return this.evaluateAffinity(constraint, allocation);
      
      case ConstraintType.ANTI_AFFINITY:
        return this.evaluateAntiAffinity(constraint, allocation);
      
      case ConstraintType.LOCATION:
        return this.evaluateLocation(constraint, allocation);
      
      case ConstraintType.CAPABILITY:
        return this.evaluateCapability(constraint, allocation);
      
      case ConstraintType.ISOLATION:
        return this.evaluateIsolation(constraint, allocation);
      
      default:
        return { satisfied: true };
    }
  }

  private async evaluateAffinity(
    constraint: ResourceConstraint,
    allocation: CandidateAllocation
  ): Promise<SingleConstraintResult> {
    // 친화성 규칙: 특정 리소스와 함께 배치
    const targetResources = await this.findTargetResources(
      constraint.target
    );

    for (const resource of allocation.resources) {
      const colocated = this.isColocated(resource, targetResources);
      
      if (!colocated && constraint.enforcement === 'hard') {
        return {
          satisfied: false,
          reason: `Resource ${resource.id} not colocated with target`
        };
      }
    }

    return { satisfied: true };
  }
}
```

**검증 기준**:
- [ ] 리소스 풀 생성 및 관리
- [ ] 다양한 리소스 타입 지원
- [ ] 정책 및 제약 시스템
- [ ] 최적 풀 선택 알고리즘

#### SubTask 5.7.2: 리소스 할당 및 해제 메커니즘
**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/resources/resource_allocator.ts
export interface AllocationStrategy {
  name: string;
  allocate(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<ResourceAllocation>;
  deallocate(
    pool: ResourcePool,
    allocation: ResourceAllocation
  ): Promise<void>;
}

export class ResourceAllocator {
  private strategies: Map<string, AllocationStrategy>;
  private lockManager: ResourceLockManager;
  private allocationTracker: AllocationTracker;
  
  constructor(config: AllocatorConfig) {
    this.strategies = new Map();
    this.lockManager = new ResourceLockManager();
    this.allocationTracker = new AllocationTracker();
    
    // 전략 등록
    this.registerStrategy('first-fit', new FirstFitStrategy());
    this.registerStrategy('best-fit', new BestFitStrategy());
    this.registerStrategy('worst-fit', new WorstFitStrategy());
    this.registerStrategy('round-robin', new RoundRobinStrategy());
    this.registerStrategy('bin-packing', new BinPackingStrategy());
  }

  async allocate(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<ResourceAllocation> {
    // 1. 전략 선택
    const strategy = this.selectStrategy(request);
    
    // 2. 리소스 잠금
    const locks = await this.acquireLocks(pool, request);
    
    try {
      // 3. 할당 수행
      const allocation = await strategy.allocate(pool, request);
      
      // 4. 할당 추적
      await this.allocationTracker.track(allocation);
      
      // 5. 리소스 상태 업데이트
      await this.updateResourceStates(pool, allocation);
      
      // 6. 이벤트 발행
      await this.publishAllocationEvent(allocation);
      
      return allocation;
      
    } catch (error) {
      // 롤백
      await this.rollbackAllocation(pool, request);
      throw error;
      
    } finally {
      // 잠금 해제
      await this.releaseLocks(locks);
    }
  }

  async deallocate(
    allocationId: string
  ): Promise<void> {
    const allocation = await this.allocationTracker.get(allocationId);
    
    if (!allocation) {
      throw new AllocationNotFoundError(allocationId);
    }

    const pool = await this.getPool(allocation.poolId);
    const strategy = this.strategies.get(allocation.strategy)!;
    
    // 1. 리소스 잠금
    const locks = await this.acquireDeallocationLocks(allocation);
    
    try {
      // 2. 해제 전 검증
      await this.validateDeallocation(allocation);
      
      // 3. 해제 수행
      await strategy.deallocate(pool, allocation);
      
      // 4. 리소스 상태 업데이트
      await this.releaseResourceStates(pool, allocation);
      
      // 5. 추적 제거
      await this.allocationTracker.remove(allocationId);
      
      // 6. 이벤트 발행
      await this.publishDeallocationEvent(allocation);
      
    } finally {
      await this.releaseLocks(locks);
    }
  }

  private async acquireLocks(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<ResourceLock[]> {
    const locks: ResourceLock[] = [];
    
    for (const requirement of request.requirements) {
      const resources = pool.resources.get(requirement.type);
      
      if (!resources) continue;
      
      // 필요한 리소스에 대한 잠금 획득
      const resourceLocks = await this.lockManager.acquireMultiple(
        resources.map(r => ({
          resourceId: r.id,
          lockType: 'write',
          timeout: 30000
        }))
      );
      
      locks.push(...resourceLocks);
    }
    
    return locks;
  }

  private async updateResourceStates(
    pool: ResourcePool,
    allocation: ResourceAllocation
  ): Promise<void> {
    for (const allocated of allocation.allocatedResources) {
      const resources = pool.resources.get(allocated.type);
      const resource = resources?.find(r => r.id === allocated.resourceId);
      
      if (resource) {
        resource.allocated += allocated.amount;
        resource.available = resource.capacity - resource.allocated;
        
        // 메타데이터 업데이트
        resource.metadata.lastAllocation = {
          allocationId: allocation.id,
          timestamp: new Date(),
          amount: allocated.amount
        };
      }
    }
    
    // 풀 메트릭 업데이트
    pool.metrics.currentUsage = this.calculateCurrentUsage(pool);
    pool.metrics.lastUpdated = new Date();
  }
}

// First-Fit 전략
export class FirstFitStrategy implements AllocationStrategy {
  name = 'first-fit';

  async allocate(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<ResourceAllocation> {
    const allocation: ResourceAllocation = {
      id: uuid(),
      requestId: request.id,
      poolId: pool.id,
      strategy: this.name,
      allocatedResources: [],
      status: 'allocated',
      createdAt: new Date(),
      expiresAt: request.duration 
        ? new Date(Date.now() + request.duration) 
        : undefined
    };

    for (const requirement of request.requirements) {
      const allocated = await this.allocateRequirement(
        pool,
        requirement
      );
      
      if (!allocated) {
        throw new InsufficientResourceError(
          `Cannot allocate ${requirement.amount} ${requirement.type}`
        );
      }
      
      allocation.allocatedResources.push(...allocated);
    }

    return allocation;
  }

  private async allocateRequirement(
    pool: ResourcePool,
    requirement: ResourceRequirement
  ): Promise<AllocatedResource[] | null> {
    const resources = pool.resources.get(requirement.type);
    if (!resources) return null;

    const allocated: AllocatedResource[] = [];
    let remaining = requirement.amount;

    // First-fit: 첫 번째 가용 리소스부터 할당
    for (const resource of resources) {
      if (remaining <= 0) break;
      
      if (resource.available > 0) {
        const toAllocate = Math.min(resource.available, remaining);
        
        allocated.push({
          resourceId: resource.id,
          type: requirement.type,
          amount: toAllocate,
          metadata: requirement.metadata
        });
        
        remaining -= toAllocate;
      }
    }

    return remaining === 0 ? allocated : null;
  }

  async deallocate(
    pool: ResourcePool,
    allocation: ResourceAllocation
  ): Promise<void> {
    for (const allocated of allocation.allocatedResources) {
      const resources = pool.resources.get(allocated.type);
      const resource = resources?.find(r => r.id === allocated.resourceId);
      
      if (resource) {
        resource.allocated -= allocated.amount;
        resource.available += allocated.amount;
      }
    }
  }
}

// Best-Fit 전략
export class BestFitStrategy implements AllocationStrategy {
  name = 'best-fit';

  async allocate(
    pool: ResourcePool,
    request: ResourceRequest
  ): Promise<ResourceAllocation> {
    const allocation: ResourceAllocation = {
      id: uuid(),
      requestId: request.id,
      poolId: pool.id,
      strategy: this.name,
      allocatedResources: [],
      status: 'allocated',
      createdAt: new Date()
    };

    for (const requirement of request.requirements) {
      const allocated = await this.allocateBestFit(
        pool,
        requirement
      );
      
      if (!allocated) {
        throw new InsufficientResourceError(
          `Cannot allocate ${requirement.amount} ${requirement.type}`
        );
      }
      
      allocation.allocatedResources.push(...allocated);
    }

    return allocation;
  }

  private async allocateBestFit(
    pool: ResourcePool,
    requirement: ResourceRequirement
  ): Promise<AllocatedResource[] | null> {
    const resources = pool.resources.get(requirement.type);
    if (!resources) return null;

    // Best-fit: 가장 적합한 크기의 리소스 찾기
    const candidates = resources
      .filter(r => r.available >= requirement.amount)
      .sort((a, b) => a.available - b.available);

    if (candidates.length === 0) {
      // 단일 리소스로 충족 불가능한 경우 분할 할당
      return this.allocateFragmented(resources, requirement);
    }

    const bestFit = candidates[0];
    
    return [{
      resourceId: bestFit.id,
      type: requirement.type,
      amount: requirement.amount,
      metadata: requirement.metadata
    }];
  }

  private allocateFragmented(
    resources: ResourceUnit[],
    requirement: ResourceRequirement
  ): AllocatedResource[] | null {
    // 가용 리소스를 크기 순으로 정렬
    const sorted = resources
      .filter(r => r.available > 0)
      .sort((a, b) => b.available - a.available);

    const allocated: AllocatedResource[] = [];
    let remaining = requirement.amount;

    for (const resource of sorted) {
      if (remaining <= 0) break;
      
      const toAllocate = Math.min(resource.available, remaining);
      
      allocated.push({
        resourceId: resource.id,
        type: requirement.type,
        amount: toAllocate,
        metadata: requirement.metadata
      });
      
      remaining -= toAllocate;
    }

    return remaining === 0 ? allocated : null;
  }

  async deallocate(
    pool: ResourcePool,
    allocation: ResourceAllocation
  ): Promise<void> {
    // First-Fit과 동일한 해제 로직
    for (const allocated of allocation.allocatedResources) {
      const resources = pool.resources.get(allocated.type);
      const resource = resources?.find(r => r.id === allocated.resourceId);
      
      if (resource) {
        resource.allocated -= allocated.amount;
        resource.available += allocated.amount;
      }
    }
  }
}

// 리소스 예약 시스템
export class ResourceReservationSystem {
  private reservations: Map<string, ResourceReservation> = new Map();
  private scheduler: ReservationScheduler;

  constructor() {
    this.scheduler = new ReservationScheduler();
  }

  async reserve(
    request: ReservationRequest
  ): Promise<ResourceReservation> {
    // 1. 예약 가능성 확인
    const availability = await this.checkAvailability(request);
    
    if (!availability.available) {
      throw new ReservationUnavailableError(availability.reason);
    }

    // 2. 예약 생성
    const reservation: ResourceReservation = {
      id: uuid(),
      requestId: request.id,
      poolId: request.poolId,
      resources: request.resources,
      startTime: request.startTime,
      endTime: request.endTime,
      status: 'pending',
      createdAt: new Date(),
      createdBy: request.userId
    };

    // 3. 예약 등록
    this.reservations.set(reservation.id, reservation);

    // 4. 스케줄링
    await this.scheduler.schedule(reservation);

    // 5. 알림 설정
    this.setupNotifications(reservation);

    return reservation;
  }

  async cancel(
    reservationId: string,
    reason?: string
  ): Promise<void> {
    const reservation = this.reservations.get(reservationId);
    
    if (!reservation) {
      throw new ReservationNotFoundError(reservationId);
    }

    // 1. 취소 가능 여부 확인
    if (reservation.status === 'active') {
      throw new Error('Cannot cancel active reservation');
    }

    // 2. 예약 취소
    reservation.status = 'cancelled';
    reservation.cancelledAt = new Date();
    reservation.cancellationReason = reason;

    // 3. 스케줄 제거
    await this.scheduler.unschedule(reservationId);

    // 4. 리소스 해제
    if (reservation.allocatedResources) {
      await this.releaseReservedResources(reservation);
    }

    // 5. 알림 발송
    await this.notifyCancellation(reservation);
  }

  private async checkAvailability(
    request: ReservationRequest
  ): Promise<AvailabilityResult> {
    const pool = await this.getPool(request.poolId);
    
    // 시간대별 가용성 확인
    const timeline = await this.buildAvailabilityTimeline(
      pool,
      request.startTime,
      request.endTime
    );

    for (const requirement of request.resources) {
      const available = this.checkResourceAvailability(
        timeline,
        requirement
      );
      
      if (!available) {
        return {
          available: false,
          reason: `Insufficient ${requirement.type} during requested period`
        };
      }
    }

    return { available: true };
  }

  private async buildAvailabilityTimeline(
    pool: ResourcePool,
    startTime: Date,
    endTime: Date
  ): Promise<AvailabilityTimeline> {
    const timeline = new AvailabilityTimeline();

    // 현재 할당 상태
    timeline.addSnapshot(new Date(), pool.resources);

    // 기존 예약 반영
    const existingReservations = await this.getReservationsInPeriod(
      pool.id,
      startTime,
      endTime
    );

    for (const reservation of existingReservations) {
      timeline.addReservation(reservation);
    }

    // 예측된 해제 반영
    const predictedReleases = await this.predictReleases(
      pool.id,
      startTime,
      endTime
    );

    for (const release of predictedReleases) {
      timeline.addRelease(release);
    }

    return timeline;
  }
}

// 할당 추적기
export class AllocationTracker {
  private allocations: Map<string, TrackedAllocation> = new Map();
  private expirationQueue: PriorityQueue<string>;
  private metricsCollector: MetricsCollector;

  constructor() {
    this.expirationQueue = new PriorityQueue((a, b) => {
      const allocationA = this.allocations.get(a)!;
      const allocationB = this.allocations.get(b)!;
      return allocationA.expiresAt!.getTime() - allocationB.expiresAt!.getTime();
    });
    
    this.metricsCollector = new MetricsCollector();
    this.startExpirationMonitor();
  }

  async track(allocation: ResourceAllocation): Promise<void> {
    const tracked: TrackedAllocation = {
      ...allocation,
      trackingStarted: new Date(),
      lastHeartbeat: new Date(),
      metrics: {
        cpuUsage: [],
        memoryUsage: [],
        networkIO: [],
        diskIO: []
      }
    };

    this.allocations.set(allocation.id, tracked);

    if (allocation.expiresAt) {
      this.expirationQueue.enqueue(allocation.id);
    }

    // 메트릭 수집 시작
    this.metricsCollector.startCollecting(allocation.id);
  }

  async remove(allocationId: string): Promise<void> {
    const allocation = this.allocations.get(allocationId);
    
    if (allocation) {
      // 메트릭 수집 중지
      this.metricsCollector.stopCollecting(allocationId);
      
      // 최종 메트릭 저장
      await this.saveMetrics(allocation);
      
      // 추적 제거
      this.allocations.delete(allocationId);
    }
  }

  private startExpirationMonitor(): void {
    setInterval(async () => {
      await this.checkExpirations();
    }, 10000); // 10초마다 확인
  }

  private async checkExpirations(): Promise<void> {
    const now = new Date();

    while (!this.expirationQueue.isEmpty()) {
      const allocationId = this.expirationQueue.peek()!;
      const allocation = this.allocations.get(allocationId);

      if (!allocation || !allocation.expiresAt) {
        this.expirationQueue.dequeue();
        continue;
      }

      if (allocation.expiresAt > now) {
        break; // 아직 만료되지 않음
      }

      // 만료된 할당 처리
      this.expirationQueue.dequeue();
      await this.handleExpiration(allocation);
    }
  }

  private async handleExpiration(
    allocation: TrackedAllocation
  ): Promise<void> {
    logger.info(`Allocation expired: ${allocation.id}`);

    // 자동 해제 여부 확인
    if (allocation.autoRelease) {
      await this.releaseAllocation(allocation.id);
    } else {
      // 만료 알림
      await this.notifyExpiration(allocation);
    }
  }
}
```

**검증 기준**:
- [ ] 다양한 할당 전략 구현
- [ ] 리소스 잠금 메커니즘
- [ ] 예약 시스템
- [ ] 할당 추적 및 만료 처리

#### SubTask 5.7.3: 리소스 모니터링 및 추적
**담당자**: 모니터링 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:
```typescript
// backend/src/orchestration/resources/resource_monitor.ts
export class ResourceMonitor {
  private collectors: Map<ResourceType, MetricCollector> = new Map();
  private aggregator: MetricAggregator;
  private alertManager: AlertManager;
  private dashboardUpdater: DashboardUpdater;

  constructor(config: MonitorConfig) {
    this.aggregator = new MetricAggregator(config.aggregation);
    this.alertManager = new AlertManager(config.alerts);
    this.dashboardUpdater = new DashboardUpdater(config.dashboard);
    
    this.initializeCollectors();
  }

  private initializeCollectors(): void {
    this.collectors.set(ResourceType.CPU, new CPUCollector());
    this.collectors.set(ResourceType.MEMORY, new MemoryCollector());
    this.collectors.set(ResourceType.GPU, new GPUCollector());
    this.collectors.set(ResourceType.NETWORK, new NetworkCollector());
    this.collectors.set(ResourceType.STORAGE, new StorageCollector());
    this.collectors.set(ResourceType.AGENT, new AgentCollector());
  }

  async startMonitoring(pool: ResourcePool): Promise<void> {
    logger.info(`Starting monitoring for pool: ${pool.id}`);

    // 각 리소스 타입별 모니터링 시작
    for (const [type, resources] of pool.resources) {
      const collector = this.collectors.get(type);
      
      if (collector) {
        for (const resource of resources) {
          await collector.startCollecting(resource);
        }
      }
    }

    // 주기적 집계 시작
    this.scheduleAggregation(pool);

    // 실시간 모니터링 스트림 시작
    this.startRealtimeStream(pool);

    // 알림 규칙 등록
    await this.registerAlertRules(pool);
  }

  private scheduleAggregation(pool: ResourcePool): void {
    // 1분 단위 집계
    setInterval(async () => {
      await this.aggregateMetrics(pool, '1m');
    }, 60 * 1000);

    // 5분 단위 집계
    setInterval(async () => {
      await this.aggregateMetrics(pool, '5m');
    }, 5 * 60 * 1000);

    // 1시간 단위 집계
    setInterval(async () => {
      await this.aggregateMetrics(pool, '1h');
    }, 60 * 60 * 1000);
  }

  private async aggregateMetrics(
    pool: ResourcePool,
    interval: string
  ): Promise<void> {
    const metrics: PoolMetrics = {
      timestamp: new Date(),
      interval,
      resources: {}
    };

    for (const [type, resources] of pool.resources) {
      const collector = this.collectors.get(type);
      
      if (!collector) continue;

      const typeMetrics: ResourceTypeMetrics = {
        total: 0,
        used: 0,
        available: 0,
        utilization: 0,
        details: []
      };

      for (const resource of resources) {
        const resourceMetrics = await collector.getMetrics(
          resource.id,
          interval
        );

        typeMetrics.total += resource.capacity;
        typeMetrics.used += resource.allocated;
        typeMetrics.available += resource.available;
        
        typeMetrics.details.push({
          resourceId: resource.id,
          metrics: resourceMetrics
        });
      }

      typeMetrics.utilization = (typeMetrics.used / typeMetrics.total) * 100;
      metrics.resources[type] = typeMetrics;
    }

    // 집계된 메트릭 저장
    await this.aggregator.save(pool.id, metrics);

    // 대시보드 업데이트
    await this.dashboardUpdater.update(pool.id, metrics);

    // 알림 확인
    await this.checkAlerts(pool, metrics);
  }

  private async checkAlerts(
    pool: ResourcePool,
    metrics: PoolMetrics
  ): Promise<void> {
    const rules = await this.alertManager.getRules(pool.id);

    for (const rule of rules) {
      const triggered = await this.evaluateAlertRule(rule, metrics);
      
      if (triggered) {
        await this.alertManager.trigger({
          ruleId: rule.id,
          poolId: pool.id,
          severity: rule.severity,
          message: rule.message,
          metrics: this.extractRelevantMetrics(metrics, rule),
          timestamp: new Date()
        });
      }
    }
  }

  private async evaluateAlertRule(
    rule: AlertRule,
    metrics: PoolMetrics
  ): Promise<boolean> {
    switch (rule.condition.type) {
      case 'threshold':
        return this.evaluateThreshold(rule.condition, metrics);
      
      case 'rate':
        return this.evaluateRate(rule.condition, metrics);
      
      case 'anomaly':
        return this.evaluateAnomaly(rule.condition, metrics);
      
      case 'composite':
        return this.evaluateComposite(rule.condition, metrics);
      
      default:
        return false;
    }
  }

  private startRealtimeStream(pool: ResourcePool): void {
    const stream = new RealtimeMetricStream(pool.id);

    // 실시간 메트릭 수집
    for (const [type, resources] of pool.resources) {
      const collector = this.collectors.get(type);
      
      if (!collector) continue;

      for (const resource of resources) {
        collector.onMetricUpdate(resource.id, (metric) => {
          stream.publish({
            resourceId: resource.id,
            type,
            metric,
            timestamp: new Date()
          });
        });
      }
    }

    // WebSocket을 통한 실시간 전송
    stream.onSubscribe((client) => {
      logger.info(`Client subscribed to pool ${pool.id} metrics`);
    });
  }
}

// CPU 메트릭 수집기
export class CPUCollector implements MetricCollector {
  private intervals: Map<string, NodeJS.Timer> = new Map();

  async startCollecting(resource: ResourceUnit): Promise<void> {
    const interval = setInterval(async () => {
      const metrics = await this.collectCPUMetrics(resource);
      await this.store(resource.id, metrics);
    }, 5000); // 5초마다

    this.intervals.set(resource.id, interval);
  }

  async stopCollecting(resourceId: string): Promise<void> {
    const interval = this.intervals.get(resourceId);
    if (interval) {
      clearInterval(interval);
      this.intervals.delete(resourceId);
    }
  }

  private async collectCPUMetrics(
    resource: ResourceUnit
  ): Promise<CPUMetrics> {
    const nodeId = resource.metadata.nodeId;
    
    // 시스템 메트릭 수집
    const usage = await this.getCPUUsage(nodeId);
    const temperature = await this.getCPUTemperature(nodeId);
    const frequency = await this.getCPUFrequency(nodeId);
    
    return {
      usage: {
        user: usage.user,
        system: usage.system,
        idle: usage.idle,
        iowait: usage.iowait,
        steal: usage.steal
      },
      temperature,
      frequency: {
        current: frequency.current,
        min: frequency.min,
        max: frequency.max
      },
      cores: {
        allocated: resource.allocated,
        available: resource.available,
        total: resource.capacity
      },
      processes: await this.getProcessCount(nodeId),
      loadAverage: await this.getLoadAverage(nodeId)
    };
  }

  async getMetrics(
    resourceId: string,
    interval: string
  ): Promise<AggregatedMetrics> {
    const raw = await this.getRawMetrics(resourceId, interval);
    
    return {
      avg: this.calculateAverage(raw),
      min: this.calculateMin(raw),
      max: this.calculateMax(raw),
      p50: this.calculatePercentile(raw, 50),
      p90: this.calculatePercentile(raw, 90),
      p99: this.calculatePercentile(raw, 99),
      stdDev: this.calculateStdDev(raw)
    };
  }
}

// 리소스 추적 시스템
export class ResourceTracker {
  private history: Map<string, ResourceHistory> = new Map();
  private changeDetector: ChangeDetector;
  private predictiveAnalyzer: PredictiveAnalyzer;

  constructor() {
    this.changeDetector = new ChangeDetector();
    this.predictiveAnalyzer = new PredictiveAnalyzer();
  }

  async trackChange(
    poolId: string,
    change: ResourceChange
  ): Promise<void> {
    let history = this.history.get(poolId);
    
    if (!history) {
      history = {
        poolId,
        changes: [],
        snapshots: []
      };
      this.history.set(poolId, history);
    }

    // 변경 사항 기록
    history.changes.push({
      ...change,
      timestamp: new Date()
    });

    // 스냅샷 생성 (주요 변경 시)
    if (this.isSignificantChange(change)) {
      const snapshot = await this.createSnapshot(poolId);
      history.snapshots.push(snapshot);
    }

    // 이상 탐지
    const anomaly = await this.changeDetector.detect(change, history);
    if (anomaly) {
      await this.handleAnomaly(anomaly);
    }

    // 예측 모델 업데이트
    await this.predictiveAnalyzer.updateModel(poolId, history);
  }

  async getHistory(
    poolId: string,
    options: HistoryOptions
  ): Promise<ResourceHistory> {
    const history = this.history.get(poolId);
    
    if (!history) {
      return { poolId, changes: [], snapshots: [] };
    }

    // 시간 범위 필터링
    let filtered = history;
    
    if (options.startTime || options.endTime) {
      filtered = this.filterByTimeRange(
        history,
        options.startTime,
        options.endTime
      );
    }

    // 변경 타입 필터링
    if (options.changeTypes) {
      filtered = this.filterByChangeType(
        filtered,
        options.changeTypes
      );
    }

    return filtered;
  }

  async predictUsage(
    poolId: string,
    timeframe: number
  ): Promise<UsagePrediction> {
    const history = this.history.get(poolId);
    
    if (!history || history.changes.length < 100) {
      return {
        confidence: 0,
        predictions: [],
        reasoning: 'Insufficient historical data'
      };
    }

    return this.predictiveAnalyzer.predict(
      history,
      timeframe
    );
  }

  private isSignificantChange(change: ResourceChange): boolean {
    // 주요 변경 사항 판단 로직
    if (change.type === 'allocation' && change.amount > 100) {
      return true;
    }
    
    if (change.type === 'pool_resize') {
      return true;
    }
    
    if (change.type === 'failure') {
      return true;
    }
    
    return false;
  }

  private async createSnapshot(poolId: string): Promise<ResourceSnapshot> {
    const pool = await this.getPool(poolId);
    
    return {
      timestamp: new Date(),
      poolId,
      resources: this.serializeResources(pool.resources),
      metrics: { ...pool.metrics },
      allocations: await this.getCurrentAllocations(poolId)
    };
  }
}

// 대시보드 업데이터
export class DashboardUpdater {
  private websocketServer: WebSocketServer;
  private dashboardCache: Map<string, DashboardData> = new Map();

  constructor(config: DashboardConfig) {
    this.websocketServer = new WebSocketServer(config.wsPort);
  }

  async update(
    poolId: string,
    metrics: PoolMetrics
  ): Promise<void> {
    // 대시보드 데이터 준비
    const dashboardData = this.prepareDashboardData(poolId, metrics);
    
    // 캐시 업데이트
    this.dashboardCache.set(poolId, dashboardData);
    
    // 연결된 클라이언트에 브로드캐스트
    this.broadcast(poolId, dashboardData);
    
    // 영구 저장 (히스토리)
    await this.saveToDashboardHistory(poolId, dashboardData);
  }

  private prepareDashboardData(
    poolId: string,
    metrics: PoolMetrics
  ): DashboardData {
    return {
      poolId,
      timestamp: metrics.timestamp,
      summary: {
        totalResources: this.countTotalResources(metrics),
        utilization: this.calculateOverallUtilization(metrics),
        efficiency: this.calculateEfficiency(metrics),
        health: this.assessHealth(metrics)
      },
      resourceBreakdown: this.createResourceBreakdown(metrics),
      trends: this.calculateTrends(poolId, metrics),
      alerts: this.getActiveAlerts(poolId),
      recommendations: this.generateRecommendations(metrics)
    };
  }

  private createResourceBreakdown(
    metrics: PoolMetrics
  ): ResourceBreakdown[] {
    const breakdown: ResourceBreakdown[] = [];

    for (const [type, typeMetrics] of Object.entries(metrics.resources)) {
      breakdown.push({
        type: type as ResourceType,
        total: typeMetrics.total,
        used: typeMetrics.used,
        available: typeMetrics.available,
        utilization: typeMetrics.utilization,
        trend: this.calculateResourceTrend(type, typeMetrics),
        topConsumers: this.getTopConsumers(typeMetrics)
      });
    }

    return breakdown;
  }

  private calculateTrends(
    poolId: string,
    currentMetrics: PoolMetrics
  ): TrendData {
    const history = this.getHistoricalData(poolId);
    
    return {
      utilization: {
        current: currentMetrics.utilization,
        change1h: this.calculateChange(history, '1h', 'utilization'),
        change24h: this.calculateChange(history, '24h', 'utilization'),
        change7d: this.calculateChange(history, '7d', 'utilization'),
        forecast: this.forecastMetric(history, 'utilization', '24h')
      },
      allocations: {
        current: currentMetrics.activeAllocations,
        change1h: this.calculateChange(history, '1h', 'allocations'),
        change24h: this.calculateChange(history, '24h', 'allocations'),
        peak24h: this.findPeak(history, '24h', 'allocations')
      }
    };
  }

  private generateRecommendations(
    metrics: PoolMetrics
  ): Recommendation[] {
    const recommendations: Recommendation[] = [];

    // 고사용률 경고
    if (metrics.utilization > 80) {
      recommendations.push({
        type: 'scaling',
        priority: 'high',
        message: 'Resource utilization is high. Consider scaling up.',
        action: {
          type: 'scale_up',
          amount: Math.ceil(metrics.total * 0.3)
        }
      });
    }

    // 저사용률 최적화
    if (metrics.utilization < 20 && metrics.age > 24 * 60 * 60 * 1000) {
      recommendations.push({
        type: 'optimization',
        priority: 'medium',
        message: 'Resource utilization is low. Consider scaling down.',
        action: {
          type: 'scale_down',
          amount: Math.floor(metrics.total * 0.3)
        }
      });
    }

    // 불균형 감지
    const imbalance = this.detectImbalance(metrics);
    if (imbalance) {
      recommendations.push({
        type: 'rebalancing',
        priority: 'medium',
        message: `Resource imbalance detected: ${imbalance.description}`,
        action: {
          type: 'rebalance',
          target: imbalance.target
        }
      });
    }

    return recommendations;
  }

  private broadcast(poolId: string, data: DashboardData): void {
    const message = JSON.stringify({
      type: 'dashboard_update',
      poolId,
      data
    });

    this.websocketServer.broadcast(
      `/pools/${poolId}/dashboard`,
      message
    );
  }
}
```

**검증 기준**:
- [ ] 다양한 메트릭 수집기
- [ ] 실시간 모니터링 스트림
- [ ] 이상 탐지 및 알림
- [ ] 대시보드 통합

#### SubTask 5.7.4: 리소스 최적화 및 재조정
**담당자**: 성능 최적화 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/resources/resource_optimizer.ts
export class ResourceOptimizer {
  private analyzer: ResourceAnalyzer;
  private rebalancer: ResourceRebalancer;
  private predictor: ResourcePredictor;
  private optimizer: OptimizationEngine;

  constructor(config: OptimizerConfig) {
    this.analyzer = new ResourceAnalyzer();
    this.rebalancer = new ResourceRebalancer();
    this.predictor = new ResourcePredictor();
    this.optimizer = new OptimizationEngine(config);
  }

  async optimizePool(
    pool: ResourcePool,
    objectives: OptimizationObjective[]
  ): Promise<OptimizationResult> {
    const startTime = Date.now();

    // 1. 현재 상태 분석
    const analysis = await this.analyzer.analyze(pool);

    // 2. 최적화 기회 식별
    const opportunities = await this.identifyOpportunities(
      pool,
      analysis
    );

    // 3. 최적화 계획 수립
    const plan = await this.optimizer.createPlan(
      pool,
      opportunities,
      objectives
    );

    // 4. 계획 실행
    const result = await this.executePlan(pool, plan);

    // 5. 결과 평가
    const evaluation = await this.evaluateResult(
      pool,
      result,
      objectives
    );

    return {
      poolId: pool.id,
      duration: Date.now() - startTime,
      plan,
      result,
      evaluation,
      improvements: this.calculateImprovements(analysis, evaluation)
    };
  }

  private async identifyOpportunities(
    pool: ResourcePool,
    analysis: PoolAnalysis
  ): Promise<OptimizationOpportunity[]> {
    const opportunities: OptimizationOpportunity[] = [];

    // 1. 조각화 감소
    if (analysis.fragmentation > 0.3) {
      opportunities.push({
        type: 'defragmentation',
        priority: 'high',
        estimatedBenefit: {
          efficiency: 0.2,
          capacity: analysis.fragmentedCapacity
        },
        cost: {
          migrations: this.estimateMigrations(pool),
          downtime: 0
        }
      });
    }

    // 2. 부하 재분배
    const imbalance = analysis.loadImbalance;
    if (imbalance.score > 0.4) {
      opportunities.push({
        type: 'rebalancing',
        priority: 'medium',
        estimatedBenefit: {
          performance: 0.15,
          reliability: 0.1
        },
        cost: {
          migrations: imbalance.requiredMigrations,
          networkTraffic: imbalance.estimatedTraffic
        }
      });
    }

    // 3. 미사용 리소스 회수
    if (analysis.idleResources.length > 0) {
      opportunities.push({
        type: 'reclamation',
        priority: 'low',
        estimatedBenefit: {
          capacity: analysis.idleCapacity,
          cost: analysis.idleCost
        },
        cost: {
          processing: 'minimal'
        }
      });
    }

    // 4. 예측 기반 사전 스케일링
    const prediction = await this.predictor.predictDemand(pool, 24);
    if (prediction.peakDemand > pool.capacity * 0.9) {
      opportunities.push({
        type: 'predictive_scaling',
        priority: 'high',
        estimatedBenefit: {
          availability: 0.99,
          performanceSLA: 0.95
        },
        cost: {
          additionalResources: prediction.requiredCapacity
        }
      });
    }

    return opportunities;
  }

  private async executePlan(
    pool: ResourcePool,
    plan: OptimizationPlan
  ): Promise<ExecutionResult> {
    const executor = new PlanExecutor(pool);
    const result: ExecutionResult = {
      steps: [],
      success: true,
      rollbacks: []
    };

    for (const step of plan.steps) {
      try {
        // 단계 실행
        const stepResult = await executor.executeStep(step);
        result.steps.push(stepResult);

        // 검증
        if (!await this.validateStep(pool, stepResult)) {
          throw new ValidationError(`Step ${step.id} validation failed`);
        }

      } catch (error) {
        // 롤백
        result.success = false;
        result.error = error;
        
        // 이전 단계들 롤백
        for (let i = result.steps.length - 1; i >= 0; i--) {
          const rollback = await executor.rollbackStep(result.steps[i]);
          result.rollbacks.push(rollback);
        }
        
        break;
      }
    }

    return result;
  }
}

// 리소스 재조정기
export class ResourceRebalancer {
  async rebalance(
    pool: ResourcePool,
    strategy: RebalanceStrategy
  ): Promise<RebalanceResult> {
    switch (strategy) {
      case 'round-robin':
        return this.roundRobinRebalance(pool);
      
      case 'least-loaded':
        return this.leastLoadedRebalance(pool);
      
      case 'affinity-aware':
        return this.affinityAwareRebalance(pool);
      
      case 'cost-optimized':
        return this.costOptimizedRebalance(pool);
      
      default:
        throw new Error(`Unknown rebalance strategy: ${strategy}`);
    }
  }

  private async leastLoadedRebalance(
    pool: ResourcePool
  ): Promise<RebalanceResult> {
    const allocations = await this.getAllocations(pool);
    const migrations: Migration[] = [];

    // 리소스별 부하 계산
    const loads = this.calculateResourceLoads(pool);
    
    // 부하가 높은 리소스에서 낮은 리소스로 이동
    const overloaded = loads.filter(l => l.utilization > 0.8);
    const underloaded = loads.filter(l => l.utilization < 0.4);

    for (const source of overloaded) {
      const candidates = allocations.filter(
        a => a.resourceId === source.resourceId
      );

      for (const allocation of candidates) {
        // 적합한 대상 찾기
        const target = this.findBestTarget(
          allocation,
          underloaded,
          pool
        );

        if (target) {
          migrations.push({
            allocationId: allocation.id,
            from: source.resourceId,
            to: target.resourceId,
            size: allocation.amount,
            estimatedDuration: this.estimateMigrationTime(allocation)
          });

          // 부하 업데이트
          source.utilization -= allocation.amount / source.capacity;
          target.utilization += allocation.amount / target.capacity;

          if (source.utilization <= 0.7) break;
        }
      }
    }

    // 마이그레이션 실행
    return this.executeMigrations(migrations);
  }

  private async executeMigrations(
    migrations: Migration[]
  ): Promise<RebalanceResult> {
    const results: MigrationResult[] = [];
    const startTime = Date.now();

    // 병렬 실행 가능한 마이그레이션 그룹화
    const groups = this.groupMigrations(migrations);

    for (const group of groups) {
      const groupResults = await Promise.all(
        group.map(m => this.executeMigration(m))
      );
      results.push(...groupResults);
    }

    return {
      totalMigrations: migrations.length,
      successfulMigrations: results.filter(r => r.success).length,
      failedMigrations: results.filter(r => !r.success).length,
      duration: Date.now() - startTime,
      details: results
    };
  }

  private groupMigrations(
    migrations: Migration[]
  ): Migration[][] {
    // 의존성이 없는 마이그레이션끼리 그룹화
    const groups: Migration[][] = [];
    const processed = new Set<string>();

    while (processed.size < migrations.length) {
      const group: Migration[] = [];

      for (const migration of migrations) {
        if (processed.has(migration.allocationId)) continue;

        // 같은 리소스를 사용하는 다른 마이그레이션이 없는지 확인
        const hasConflict = group.some(
          g => g.from === migration.from || 
               g.to === migration.to ||
               g.from === migration.to ||
               g.to === migration.from
        );

        if (!hasConflict) {
          group.push(migration);
          processed.add(migration.allocationId);
        }
      }

      if (group.length > 0) {
        groups.push(group);
      }
    }

    return groups;
  }
}

// 조각화 제거기
export class DefragmentationEngine {
  async defragment(
    pool: ResourcePool,
    options: DefragOptions = {}
  ): Promise<DefragResult> {
    const startTime = Date.now();

    // 1. 조각화 분석
    const fragmentation = await this.analyzeFragmentation(pool);

    if (fragmentation.score < (options.threshold || 0.2)) {
      return {
        needed: false,
        fragmentationBefore: fragmentation.score,
        message: 'Fragmentation below threshold'
      };
    }

    // 2. 조각화 제거 계획
    const plan = this.createDefragPlan(pool, fragmentation);

    // 3. 실행
    const result = await this.executeDefragPlan(plan, options);

    // 4. 결과 분석
    const newFragmentation = await this.analyzeFragmentation(pool);

    return {
      needed: true,
      fragmentationBefore: fragmentation.score,
      fragmentationAfter: newFragmentation.score,
      duration: Date.now() - startTime,
      compactedAllocations: result.compacted,
      freedCapacity: result.freedCapacity
    };
  }

  private async analyzeFragmentation(
    pool: ResourcePool
  ): Promise<FragmentationAnalysis> {
    const analysis: FragmentationAnalysis = {
      score: 0,
      fragments: [],
      largestFreeBlock: 0,
      totalFreeSpace: 0
    };

    for (const [type, resources] of pool.resources) {
      for (const resource of resources) {
        const fragments = this.findFragments(resource);
        analysis.fragments.push(...fragments);

        // 조각화 점수 계산
        if (resource.available > 0) {
          const fragScore = 1 - (fragments[0]?.size || 0) / resource.available;
          analysis.score += fragScore * (resource.available / pool.totalCapacity);
        }
      }
    }

    return analysis;
  }

  private findFragments(resource: ResourceUnit): Fragment[] {
    const allocations = this.getAllocationsForResource(resource.id);
    const fragments: Fragment[] = [];

    // 할당된 영역 정렬
    allocations.sort((a, b) => a.offset - b.offset);

    let currentOffset = 0;

    for (const allocation of allocations) {
      if (allocation.offset > currentOffset) {
        // 빈 공간 발견
        fragments.push({
          offset: currentOffset,
          size: allocation.offset - currentOffset,
          resourceId: resource.id
        });
      }
      currentOffset = allocation.offset + allocation.size;
    }

    // 마지막 빈 공간
    if (currentOffset < resource.capacity) {
      fragments.push({
        offset: currentOffset,
        size: resource.capacity - currentOffset,
        resourceId: resource.id
      });
    }

    return fragments.sort((a, b) => b.size - a.size);
  }

  private createDefragPlan(
    pool: ResourcePool,
    fragmentation: FragmentationAnalysis
  ): DefragPlan {
    const moves: AllocationMove[] = [];

    // 각 리소스별로 압축 계획
    for (const [type, resources] of pool.resources) {
      for (const resource of resources) {
        const resourceMoves = this.planResourceCompaction(resource);
        moves.push(...resourceMoves);
      }
    }

    return {
      moves,
      estimatedDuration: this.estimateDuration(moves),
      requiredSpace: this.calculateRequiredSpace(moves)
    };
  }

  private planResourceCompaction(
    resource: ResourceUnit
  ): AllocationMove[] {
    const allocations = this.getAllocationsForResource(resource.id);
    const moves: AllocationMove[] = [];

    // 왼쪽으로 압축
    let targetOffset = 0;

    for (const allocation of allocations) {
      if (allocation.offset > targetOffset) {
        moves.push({
          allocationId: allocation.id,
          fromOffset: allocation.offset,
          toOffset: targetOffset,
          size: allocation.size
        });
      }
      targetOffset += allocation.size;
    }

    return moves;
  }
}

// 비용 최적화 엔진
export class CostOptimizer {
  private pricingModel: PricingModel;
  private usageAnalyzer: UsageAnalyzer;

  constructor() {
    this.pricingModel = new PricingModel();
    this.usageAnalyzer = new UsageAnalyzer();
  }

  async optimizeCost(
    pool: ResourcePool,
    constraints: CostConstraints
  ): Promise<CostOptimizationResult> {
    // 1. 현재 비용 분석
    const currentCost = await this.calculateCurrentCost(pool);

    // 2. 사용 패턴 분석
    const usagePattern = await this.usageAnalyzer.analyze(pool);

    // 3. 최적화 전략 수립
    const strategies = this.generateStrategies(
      pool,
      usagePattern,
      constraints
    );

    // 4. 최적 전략 선택
    const optimalStrategy = this.selectOptimalStrategy(
      strategies,
      constraints
    );

    // 5. 예상 절감액 계산
    const projectedCost = await this.projectCost(
      pool,
      optimalStrategy
    );

    return {
      currentCost,
      projectedCost,
      savings: currentCost - projectedCost,
      savingsPercentage: ((currentCost - projectedCost) / currentCost) * 100,
      strategy: optimalStrategy,
      implementation: this.createImplementationPlan(optimalStrategy)
    };
  }

  private generateStrategies(
    pool: ResourcePool,
    usage: UsagePattern,
    constraints: CostConstraints
  ): CostStrategy[] {
    const strategies: CostStrategy[] = [];

    // 1. 예약 인스턴스 전략
    if (usage.predictability > 0.8) {
      strategies.push({
        type: 'reserved_instances',
        description: 'Convert to reserved instances for predictable workloads',
        estimatedSavings: 0.3,
        requiredCommitment: '1year',
        risk: 'low'
      });
    }

    // 2. 스팟 인스턴스 활용
    if (constraints.allowSpot && usage.interruptibilityTolerance > 0.7) {
      strategies.push({
        type: 'spot_instances',
        description: 'Use spot instances for interruptible workloads',
        estimatedSavings: 0.7,
        requiredChanges: ['implement_checkpointing', 'add_retry_logic'],
        risk: 'medium'
      });
    }

    // 3. 자동 스케일링 최적화
    if (usage.variability > 0.5) {
      strategies.push({
        type: 'auto_scaling',
        description: 'Optimize auto-scaling policies',
        estimatedSavings: 0.25,
        requiredChanges: ['tune_scaling_policies', 'implement_predictive_scaling'],
        risk: 'low'
      });
    }

    // 4. 리소스 적정 크기 조정
    const rightsizing = this.analyzeRightsizing(pool, usage);
    if (rightsizing.opportunities.length > 0) {
      strategies.push({
        type: 'rightsizing',
        description: 'Adjust resource sizes based on actual usage',
        estimatedSavings: rightsizing.estimatedSavings,
        changes: rightsizing.opportunities,
        risk: 'low'
      });
    }

    return strategies;
  }

  private analyzeRightsizing(
    pool: ResourcePool,
    usage: UsagePattern
  ): RightsizingAnalysis {
    const opportunities: RightsizingOpportunity[] = [];
    let totalSavings = 0;

    for (const [type, resources] of pool.resources) {
      for (const resource of resources) {
        const utilization = usage.resourceUtilization.get(resource.id);
        
        if (!utilization) continue;

        // 과소 사용 리소스
        if (utilization.average < 0.3 && utilization.peak < 0.5) {
          const recommendedSize = resource.capacity * 0.6;
          const savings = this.calculateSizingSavings(
            resource,
            recommendedSize
          );

          opportunities.push({
            resourceId: resource.id,
            currentSize: resource.capacity,
            recommendedSize,
            estimatedSavings: savings,
            reason: 'Underutilized resource'
          });

          totalSavings += savings;
        }

        // 과다 사용 리소스 (비용 증가할 수 있지만 성능 향상)
        if (utilization.average > 0.8 || utilization.peak > 0.95) {
          const recommendedSize = resource.capacity * 1.5;
          
          opportunities.push({
            resourceId: resource.id,
            currentSize: resource.capacity,
            recommendedSize,
            estimatedSavings: -this.calculateSizingSavings(
              resource,
              recommendedSize
            ),
            reason: 'Overutilized resource - performance risk'
          });
        }
      }
    }

    return {
      opportunities,
      estimatedSavings: totalSavings / this.calculateCurrentCost(pool)
    };
  }
}
```

**검증 기준**:
- [ ] 다양한 최적화 전략
- [ ] 리소스 재조정 메커니즘
- [ ] 조각화 제거
- [ ] 비용 최적화

### Task 5.8: 지능형 작업 스케줄러

#### SubTask 5.8.1: 스케줄링 알고리즘 구현
**담당자**: 알고리즘 엔지니어  
**예상 소요시간**: 16시간

**작업 내용**:
```typescript
// backend/src/orchestration/scheduler/scheduling_algorithms.ts
export interface SchedulingAlgorithm {
  name: string;
  schedule(
    tasks: Task[],
    resources: ResourcePool[],
    constraints: SchedulingConstraints
  ): Promise<Schedule>;
}

export class IntelligentScheduler {
  private algorithms: Map<string, SchedulingAlgorithm>;
  private mlPredictor: MLTaskPredictor;
  private constraintSolver: ConstraintSolver;
  
  constructor(config: SchedulerConfig) {
    this.algorithms = new Map();
    this.mlPredictor = new MLTaskPredictor(config.mlModel);
    this.constraintSolver = new ConstraintSolver();
    
    // 알고리즘 등록
    this.registerAlgorithm('fifo', new FIFOAlgorithm());
    this.registerAlgorithm('sjf', new ShortestJobFirst());
    this.registerAlgorithm('priority', new PriorityScheduling());
    this.registerAlgorithm('round-robin', new RoundRobinScheduling());
    this.registerAlgorithm('edf', new EarliestDeadlineFirst());
    this.registerAlgorithm('genetic', new GeneticAlgorithm());
    this.registerAlgorithm('ml-optimized', new MLOptimizedScheduling(this.mlPredictor));
  }

  async schedule(
    request: SchedulingRequest
  ): Promise<SchedulingResult> {
    const startTime = Date.now();

    // 1. 태스크 분석 및 예측
    const analyzedTasks = await this.analyzeTasks(request.tasks);

    // 2. 리소스 상태 확인
    const resourceState = await this.getResourceState(request.resources);

    // 3. 제약 조건 전처리
    const constraints = await this.preprocessConstraints(
      request.constraints,
      analyzedTasks,
      resourceState
    );

    // 4. 최적 알고리즘 선택
    const algorithm = await this.selectAlgorithm(
      analyzedTasks,
      resourceState,
      constraints
    );

    // 5. 스케줄 생성
    const schedule = await algorithm.schedule(
      analyzedTasks,
      resourceState,
      constraints
    );

    // 6. 스케줄 최적화
    const optimized = await this.optimizeSchedule(schedule);

    // 7. 검증
    const validation = await this.validateSchedule(optimized);
    
    if (!validation.valid) {
      throw new SchedulingError(validation.errors);
    }

    return {
      schedule: optimized,
      algorithm: algorithm.name,
      metrics: {
        makespan: this.calculateMakespan(optimized),
        utilization: this.calculateUtilization(optimized),
        waitTime: this.calculateAverageWaitTime(optimized),
        throughput: this.calculateThroughput(optimized)
      },
      duration: Date.now() - startTime
    };
  }

  private async analyzeTasks(tasks: Task[]): Promise<AnalyzedTask[]> {
    return Promise.all(tasks.map(async task => {
      // ML 기반 예측
      const prediction = await this.mlPredictor.predict(task);

      return {
        ...task,
        predictedDuration: prediction.duration,
        predictedResources: prediction.resources,
        predictedSuccess: prediction.successProbability,
        complexity: this.calculateComplexity(task),
        dependencies: await this.resolveDependencies(task),
        criticalPath: await this.calculateCriticalPath(task)
      };
    }));
  }

  private async selectAlgorithm(
    tasks: AnalyzedTask[],
    resources: ResourceState,
    constraints: ProcessedConstraints
  ): Promise<SchedulingAlgorithm> {
    // 휴리스틱 기반 알고리즘 선택
    const characteristics = this.analyzeWorkloadCharacteristics(tasks);

    if (characteristics.isRealTime) {
      return this.algorithms.get('edf')!;
    }

    if (characteristics.hasPriorities && characteristics.priorityVariance > 0.5) {
      return this.algorithms.get('priority')!;
    }

    if (characteristics.taskCount > 1000 && characteristics.hasComplexConstraints) {
      return this.algorithms.get('genetic')!;
    }

    if (characteristics.isPredictable && this.mlPredictor.isReady()) {
      return this.algorithms.get('ml-optimized')!;
    }

    // 기본값
    return this.algorithms.get('sjf')!;
  }
}

// Shortest Job First 알고리즘
export class ShortestJobFirst implements SchedulingAlgorithm {
  name = 'shortest-job-first';

  async schedule(
    tasks: AnalyzedTask[],
    resources: ResourcePool[],
    constraints: SchedulingConstraints
  ): Promise<Schedule> {
    // 예측 실행 시간 기준 정렬
    const sortedTasks = [...tasks].sort(
      (a, b) => a.predictedDuration - b.predictedDuration
    );

    const schedule = new Schedule();
    const resourceQueues = new Map<string, TaskQueue>();

    // 각 리소스별 큐 초기화
    for (const resource of resources) {
      resourceQueues.set(resource.id, new TaskQueue());
    }

    // 태스크 스케줄링
    for (const task of sortedTasks) {
      // 가장 빨리 사용 가능한 리소스 찾기
      const bestResource = this.findBestResource(
        task,
        resources,
        resourceQueues,
        constraints
      );

      if (!bestResource) {
        throw new NoResourceAvailableError(`No resource for task ${task.id}`);
      }

      // 스케줄에 추가
      const startTime = this.calculateStartTime(
        task,
        bestResource,
        resourceQueues.get(bestResource.id)!
      );

      schedule.addTask({
        taskId: task.id,
        resourceId: bestResource.id,
        startTime,
        endTime: new Date(startTime.getTime() + task.predictedDuration),
        allocatedResources: task.predictedResources
      });

      // 리소스 큐 업데이트
      resourceQueues.get(bestResource.id)!.enqueue(task);
    }

    return schedule;
  }

  private findBestResource(
    task: AnalyzedTask,
    resources: ResourcePool[],
    queues: Map<string, TaskQueue>,
    constraints: SchedulingConstraints
  ): ResourcePool | null {
    let bestResource: ResourcePool | null = null;
    let earliestAvailable = Infinity;

    for (const resource of resources) {
      // 리소스 제약 확인
      if (!this.meetsResourceRequirements(task, resource)) {
        continue;
      }

      // 제약 조건 확인
      if (!this.meetsConstraints(task, resource, constraints)) {
        continue;
      }

      // 가용 시간 계산
      const queue = queues.get(resource.id)!;
      const availableTime = queue.getNextAvailableTime();

      if (availableTime < earliestAvailable) {
        earliestAvailable = availableTime;
        bestResource = resource;
      }
    }

    return bestResource;
  }
}

// ML 최적화 스케줄링
export class MLOptimizedScheduling implements SchedulingAlgorithm {
  name = 'ml-optimized';

  constructor(private predictor: MLTaskPredictor) {}

  async schedule(
    tasks: AnalyzedTask[],
    resources: ResourcePool[],
    constraints: SchedulingConstraints
  ): Promise<Schedule> {
    // 1. 특징 추출
    const features = await this.extractFeatures(tasks, resources);

    // 2. ML 모델로 최적 스케줄 예측
    const mlSchedule = await this.predictor.predictOptimalSchedule(features);

    // 3. 예측 결과를 실제 스케줄로 변환
    const schedule = new Schedule();

    for (const prediction of mlSchedule.assignments) {
      const task = tasks.find(t => t.id === prediction.taskId);
      const resource = resources.find(r => r.id === prediction.resourceId);

      if (!task || !resource) continue;

      // 제약 조건 검증
      if (this.validateAssignment(task, resource, constraints)) {
        schedule.addTask({
          taskId: task.id,
          resourceId: resource.id,
          startTime: prediction.startTime,
          endTime: prediction.endTime,
          allocatedResources: prediction.resources,
          confidence: prediction.confidence
        });
      } else {
        // 대체 스케줄링
        await this.handleInvalidPrediction(
          task,
          resources,
          schedule,
          constraints
        );
      }
    }

    // 4. 후처리 최적화
    return this.postProcessOptimization(schedule);
  }

  private async extractFeatures(
    tasks: AnalyzedTask[],
    resources: ResourcePool[]
  ): Promise<SchedulingFeatures> {
    return {
      taskFeatures: tasks.map(t => ({
        duration: t.predictedDuration,
        priority: t.priority,
        dependencies: t.dependencies.length,
        resourceRequirements: this.encodeResources(t.predictedResources),
        complexity: t.complexity,
        historicalSuccess: t.historicalMetrics?.successRate || 1.0
      })),
      resourceFeatures: resources.map(r => ({
        capacity: r.capacity,
        currentUtilization: r.utilization,
        reliability: r.metrics.reliability,
        cost: r.cost,
        location: this.encodeLocation(r.location)
      })),
      globalFeatures: {
        totalTasks: tasks.length,
        totalResources: resources.length,
        averageComplexity: this.average(tasks.map(t => t.complexity)),
        timeOfDay: new Date().getHours(),
        dayOfWeek: new Date().getDay()
      }
    };
  }
}

// 유전자 알고리즘 스케줄링
export class GeneticAlgorithm implements SchedulingAlgorithm {
  name = 'genetic';
  
  private populationSize = 100;
  private generations = 500;
  private mutationRate = 0.1;
  private eliteSize = 10;

  async schedule(
    tasks: AnalyzedTask[],
    resources: ResourcePool[],
    constraints: SchedulingConstraints
  ): Promise<Schedule> {
    // 1. 초기 population 생성
    let population = this.initializePopulation(
      tasks,
      resources,
      this.populationSize
    );

    // 2. 진화 시작
    for (let gen = 0; gen < this.generations; gen++) {
      // 적합도 평가
      const fitness = population.map(individual => ({
        individual,
        fitness: this.evaluateFitness(individual, constraints)
      }));

      // 정렬
      fitness.sort((a, b) => b.fitness - a.fitness);

      // 수렴 확인
      if (this.hasConverged(fitness)) {
        break;
      }

      // 선택 및 교배
      const nextPopulation: Individual[] = [];

      // 엘리트 보존
      for (let i = 0; i < this.eliteSize; i++) {
        nextPopulation.push(fitness[i].individual);
      }

      // 교배로 새로운 개체 생성
      while (nextPopulation.length < this.populationSize) {
        const parent1 = this.tournamentSelection(fitness);
        const parent2 = this.tournamentSelection(fitness);
        
        const offspring = this.crossover(parent1, parent2);
        
        // 변이
        if (Math.random() < this.mutationRate) {
          this.mutate(offspring, tasks, resources);
        }

        nextPopulation.push(offspring);
      }

      population = nextPopulation;
    }

    // 최적 개체를 스케줄로 변환
    const best = population.reduce((a, b) => 
      this.evaluateFitness(a, constraints) > this.evaluateFitness(b, constraints) ? a : b
    );

    return this.individualToSchedule(best);
  }

  private initializePopulation(
    tasks: AnalyzedTask[],
    resources: ResourcePool[],
    size: number
  ): Individual[] {
    const population: Individual[] = [];

    for (let i = 0; i < size; i++) {
      const individual: Individual = {
        genes: []
      };

      // 무작위 할당
      for (const task of tasks) {
        const validResources = resources.filter(r => 
          this.canAllocate(task, r)
        );

        if (validResources.length > 0) {
          const resource = validResources[
            Math.floor(Math.random() * validResources.length)
          ];

          individual.genes.push({
            taskId: task.id,
            resourceId: resource.id,
            startTime: this.randomStartTime(task)
          });
        }
      }

      population.push(individual);
    }

    return population;
  }

  private evaluateFitness(
    individual: Individual,
    constraints: SchedulingConstraints
  ): number {
    let fitness = 0;

    // 1. Makespan (최소화)
    const makespan = this.calculateMakespan(individual);
    fitness += 1000 / (1 + makespan);

    // 2. 리소스 활용률 (최대화)
    const utilization = this.calculateUtilization(individual);
    fitness += utilization * 100;

    // 3. 제약 위반 페널티
    const violations = this.countConstraintViolations(individual, constraints);
    fitness -= violations * 50;

    // 4. 로드 밸런싱
    const balance = this.calculateLoadBalance(individual);
    fitness += balance * 50;

    // 5. 비용 (최소화)
    const cost = this.calculateCost(individual);
    fitness += 100 / (1 + cost);

    return fitness;
  }

  private crossover(parent1: Individual, parent2: Individual): Individual {
    const offspring: Individual = { genes: [] };
    
    // 단일점 교차
    const crossoverPoint = Math.floor(Math.random() * parent1.genes.length);
    
    for (let i = 0; i < parent1.genes.length; i++) {
      if (i < crossoverPoint) {
        offspring.genes.push({ ...parent1.genes[i] });
      } else if (i < parent2.genes.length) {
        offspring.genes.push({ ...parent2.genes[i] });
      }
    }

    return offspring;
  }

  private mutate(
    individual: Individual,
    tasks: AnalyzedTask[],
    resources: ResourcePool[]
  ): void {
    // 무작위 유전자 선택
    const geneIndex = Math.floor(Math.random() * individual.genes.length);
    const gene = individual.genes[geneIndex];
    
    // 변이 타입 선택
    const mutationType = Math.random();
    
    if (mutationType < 0.5) {
      // 리소스 변경
      const task = tasks.find(t => t.id === gene.taskId)!;
      const validResources = resources.filter(r => 
        this.canAllocate(task, r) && r.id !== gene.resourceId
      );
      
      if (validResources.length > 0) {
        gene.resourceId = validResources[
          Math.floor(Math.random() * validResources.length)
        ].id;
      }
    } else {
      // 시작 시간 변경
      gene.startTime = this.mutateStartTime(gene.startTime);
    }
  }
}

// 제약 해결기
export class ConstraintSolver {
  async solve(
    tasks: AnalyzedTask[],
    resources: ResourcePool[],
    constraints: SchedulingConstraints
  ): Promise<ConstraintSolution> {
    // CSP (Constraint Satisfaction Problem) 해결
    const problem = this.formulateProblem(tasks, resources, constraints);
    
    // 백트래킹 + 제약 전파
    const solution = await this.backtrackingSearch(problem);
    
    if (!solution) {
      // 제약 완화
      const relaxed = await this.relaxConstraints(problem);
      return this.backtrackingSearch(relaxed);
    }
    
    return solution;
  }

  private formulateProblem(
    tasks: AnalyzedTask[],
    resources: ResourcePool[],
    constraints: SchedulingConstraints
  ): CSPProblem {
    return {
      variables: tasks.map(t => ({
        id: t.id,
        domain: this.generateDomain(t, resources)
      })),
      constraints: [
        ...this.generateResourceConstraints(resources),
        ...this.generateDependencyConstraints(tasks),
        ...this.generateCustomConstraints(constraints)
      ]
    };
  }

  private async backtrackingSearch(
    problem: CSPProblem
  ): Promise<ConstraintSolution | null> {
    const assignment: Map<string, Assignment> = new Map();
    
    return this.backtrack(problem, assignment);
  }

  private async backtrack(
    problem: CSPProblem,
    assignment: Map<string, Assignment>
  ): Promise<ConstraintSolution | null> {
    // 모든 변수가 할당됨
    if (assignment.size === problem.variables.length) {
      return this.assignmentToSolution(assignment);
    }

    // 다음 변수 선택 (MRV 휴리스틱)
    const variable = this.selectUnassignedVariable(problem, assignment);
    
    // 도메인 값 순서화 (LCV 휴리스틱)
    const orderedDomain = this.orderDomainValues(variable, assignment, problem);
    
    for (const value of orderedDomain) {
      if (this.isConsistent(variable, value, assignment, problem)) {
        // 할당
        assignment.set(variable.id, value);
        
        // 제약 전파
        const inferences = await this.inference(
          variable,
          value,
          assignment,
          problem
        );
        
        if (inferences !== null) {
          // 재귀 호출
          const result = await this.backtrack(problem, assignment);
          
          if (result !== null) {
            return result;
          }
        }
        
        // 백트랙
        assignment.delete(variable.id);
        this.removeInferences(inferences);
      }
    }
    
    return null;
  }

  private selectUnassignedVariable(
    problem: CSPProblem,
    assignment: Map<string, Assignment>
  ): Variable {
    // Minimum Remaining Values (MRV) 휴리스틱
    let minVariable: Variable | null = null;
    let minDomainSize = Infinity;
    
    for (const variable of problem.variables) {
      if (!assignment.has(variable.id)) {
        const domainSize = this.getDomainSize(variable, assignment, problem);
        
        if (domainSize < minDomainSize) {
          minDomainSize = domainSize;
          minVariable = variable;
        }
      }
    }
    
    return minVariable!;
  }
}
```

**검증 기준**:
- [ ] 다양한 스케줄링 알고리즘
- [ ] ML 기반 최적화
- [ ] 유전자 알고리즘
- [ ] 제약 해결기

#### SubTask 5.8.2: 우선순위 기반 큐 시스템
**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:
```typescript
// backend/src/orchestration/scheduler/priority_queue_system.ts
export class PriorityQueueSystem {
  private queues: Map<string, PriorityQueue<ScheduledTask>>;
  private queueManager: QueueManager;
  private priorityEngine: PriorityEngine;
  private fairnessController: FairnessController;

  constructor(config: QueueSystemConfig) {
    this.queues = new Map();
    this.queueManager = new QueueManager(config);
    this.priorityEngine = new PriorityEngine(config.priority);
    this.fairnessController = new FairnessController(config.fairness);
  }

  async enqueue(task: Task): Promise<void> {
    // 1. 우선순위 계산
    const priority = await this.priorityEngine.calculatePriority(task);

    // 2. 큐 선택
    const queueId = this.selectQueue(task, priority);

    // 3. 스케줄된 태스크 생성
    const scheduledTask: ScheduledTask = {
      ...task,
      priority,
      enqueuedAt: new Date(),
      attempts: 0,
      queueId
    };

    // 4. 큐에 추가
    const queue = this.getOrCreateQueue(queueId);
    await queue.enqueue(scheduledTask, priority);

    // 5. 이벤트 발행
    await this.publishEnqueueEvent(scheduledTask);
  }

  async dequeue(resourceType: ResourceType): Promise<ScheduledTask | null> {
    // 1. 적합한 큐들 찾기
    const eligibleQueues = this.findEligibleQueues(resourceType);

    if (eligibleQueues.length === 0) {
      return null;
    }

    // 2. 공정성 고려한 큐 선택
    const selectedQueue = await this.fairnessController.selectQueue(
      eligibleQueues
    );

    // 3. 태스크 추출
    const task = await selectedQueue.dequeue();

    if (task) {
      // 4. 통계 업데이트
      await this.updateDequeueStats(task);

      // 5. 이벤트 발행
      await this.publishDequeueEvent(task);
    }

    return task;
  }

  private getOrCreateQueue(queueId: string): PriorityQueue<ScheduledTask> {
    if (!this.queues.has(queueId)) {
      const queue = new AdaptivePriorityQueue<ScheduledTask>({
        comparator: (a, b) => {
          // 우선순위가 높을수록 먼저
          if (a.priority !== b.priority) {
            return b.priority - a.priority;
          }
          // 같은 우선순위면 먼저 들어온 것 먼저 (FIFO)
          return a.enqueuedAt.getTime() - b.enqueuedAt.getTime();
        },
        capacity: this.queueManager.getQueueCapacity(queueId)
      });

      this.queues.set(queueId, queue);
    }

    return this.queues.get(queueId)!;
  }
}

// 우선순위 계산 엔진
export class PriorityEngine {
  private rules: PriorityRule[];
  private mlPriorityModel: MLPriorityModel;

  constructor(config: PriorityConfig) {
    this.rules = config.rules || [];
    this.mlPriorityModel = new MLPriorityModel(config.mlModel);
  }

  async calculatePriority(task: Task): Promise<number> {
    let basePriority = task.priority || 50;

    // 1. 규칙 기반 조정
    for (const rule of this.rules) {
      if (await rule.applies(task)) {
        basePriority = rule.adjust(basePriority, task);
      }
    }

    // 2. ML 기반 조정
    if (this.mlPriorityModel.isReady()) {
      const mlAdjustment = await this.mlPriorityModel.predictPriorityAdjustment(task);
      basePriority += mlAdjustment;
    }

    // 3. 동적 조정 요소
    const dynamicFactors = await this.calculateDynamicFactors(task);
    basePriority = this.applyDynamicFactors(basePriority, dynamicFactors);

    // 범위 제한 (0-100)
    return Math.max(0, Math.min(100, basePriority));
  }

  private async calculateDynamicFactors(task: Task): Promise<DynamicFactors> {
    return {
      // 대기 시간 요소
      waitTime: task.createdAt 
        ? Date.now() - task.createdAt.getTime() 
        : 0,
      
      // 데드라인 긴급도
      urgency: task.deadline 
        ? this.calculateUrgency(task.deadline) 
        : 0,
      
      // 의존성 임계도
      dependencyCriticality: await this.calculateDependencyCriticality(task),
      
      // 사용자 중요도
      userImportance: await this.getUserImportance(task.userId),
      
      // 리소스 가용성
      resourceAvailability: await this.checkResourceAvailability(task)
    };
  }

  private calculateUrgency(deadline: Date): number {
    const timeUntilDeadline = deadline.getTime() - Date.now();
    
    if (timeUntilDeadline < 0) {
      return 100; // 이미 지났음
    }
    
    // 지수 함수로 긴급도 계산
    const hoursUntilDeadline = timeUntilDeadline / (1000 * 60 * 60);
    return Math.min(100, 100 * Math.exp(-hoursUntilDeadline / 24));
  }

  private applyDynamicFactors(
    basePriority: number,
    factors: DynamicFactors
  ): number {
    let priority = basePriority;

    // 대기 시간 보너스 (Aging)
    const waitHours = factors.waitTime / (1000 * 60 * 60);
    priority += Math.min(20, waitHours * 2);

    // 긴급도 보너스
    priority += factors.urgency * 0.3;

    // 의존성 임계도
    priority += factors.dependencyCriticality * 0.2;

    // 사용자 중요도
    priority *= (1 + factors.userImportance * 0.1);

    // 리소스 가용성 페널티
    if (factors.resourceAvailability < 0.3) {
      priority *= 0.8; // 리소스 부족 시 우선순위 감소
    }

    return priority;
  }
}

// 공정성 컨트롤러
export class FairnessController {
  private queueStats: Map<string, QueueStatistics>;
  private fairnessPolicy: FairnessPolicy;

  constructor(config: FairnessConfig) {
    this.queueStats = new Map();
    this.fairnessPolicy = config.policy || 'weighted-round-robin';
  }

  async selectQueue(
    queues: PriorityQueue<ScheduledTask>[]
  ): Promise<PriorityQueue<ScheduledTask>> {
    switch (this.fairnessPolicy) {
      case 'strict-priority':
        return this.selectStrictPriority(queues);
      
      case 'weighted-round-robin':
        return this.selectWeightedRoundRobin(queues);
      
      case 'fair-share':
        return this.selectFairShare(queues);
      
      case 'lottery':
        return this.selectLottery(queues);
      
      default:
        return queues[0];
    }
  }

  private async selectWeightedRoundRobin(
    queues: PriorityQueue<ScheduledTask>[]
  ): Promise<PriorityQueue<ScheduledTask>> {
    // 각 큐의 가중치 계산
    const weights = await Promise.all(
      queues.map(q => this.calculateQueueWeight(q))
    );

    // 가중치 기반 선택
    const totalWeight = weights.reduce((sum, w) => sum + w, 0);
    let random = Math.random() * totalWeight;

    for (let i = 0; i < queues.length; i++) {
      random -= weights[i];
      if (random <= 0) {
        // 선택된 큐의 통계 업데이트
        this.updateQueueStats(queues[i].id, 'selected');
        return queues[i];
      }
    }

    return queues[queues.length - 1];
  }

  private async calculateQueueWeight(
    queue: PriorityQueue<ScheduledTask>
  ): Promise<number> {
    const stats = this.getQueueStats(queue.id);
    
    // 기본 가중치
    let weight = queue.size();

    // 기아 방지: 오래 기다린 큐에 보너스
    const timeSinceLastService = Date.now() - stats.lastServiceTime.getTime();
    weight *= (1 + timeSinceLastService / (1000 * 60 * 60)); // 시간당 보너스

    // 우선순위 고려
    const avgPriority = await this.getAveragePriority(queue);
    weight *= (avgPriority / 50); // 50을 기준으로 조정

    // 공정성 팩터
    const fairnessFactor = 1 / (1 + stats.totalServiced / 1000);
    weight *= fairnessFactor;

    return weight;
  }

  private getQueueStats(queueId: string): QueueStatistics {
    if (!this.queueStats.has(queueId)) {
      this.queueStats.set(queueId, {
        queueId,
        totalEnqueued: 0,
        totalServiced: 0,
        totalDropped: 0,
        avgWaitTime: 0,
        lastServiceTime: new Date(0),
        lastUpdateTime: new Date()
      });
    }

    return this.queueStats.get(queueId)!;
  }
}

// 적응형 우선순위 큐
export class AdaptivePriorityQueue<T> implements PriorityQueue<T> {
  private heap: Heap<T>;
  private indexMap: Map<string, number>;
  private config: AdaptiveQueueConfig;
  private adaptiveController: AdaptiveController;

  constructor(config: AdaptiveQueueConfig) {
    this.config = config;
    this.heap = new Heap(config.comparator);
    this.indexMap = new Map();
    this.adaptiveController = new AdaptiveController();
  }

  async enqueue(item: T, priority: number): Promise<void> {
    // 용량 확인
    if (this.heap.size() >= this.config.capacity) {
      await this.handleOverflow(item, priority);
      return;
    }

    // 힙에 추가
    this.heap.insert(item);

    // 인덱스 업데이트
    if (this.hasId(item)) {
      this.indexMap.set(this.getId(item), this.heap.size() - 1);
    }

    // 적응형 조정
    await this.adaptiveController.onEnqueue(this);
  }

  async dequeue(): Promise<T | null> {
    if (this.heap.isEmpty()) {
      return null;
    }

    const item = this.heap.extractMin();

    // 인덱스 업데이트
    if (this.hasId(item)) {
      this.indexMap.delete(this.getId(item));
    }

    // 힙 재구성
    this.rebuild();

    // 적응형 조정
    await this.adaptiveController.onDequeue(this);

    return item;
  }

  private async handleOverflow(item: T, priority: number): Promise<void> {
    switch (this.config.overflowPolicy) {
      case 'drop-lowest':
        // 가장 낮은 우선순위 제거
        const lowest = this.findLowestPriority();
        if (lowest && this.comparePriority(item, lowest) > 0) {
          await this.remove(lowest);
          await this.enqueue(item, priority);
        }
        break;

      case 'drop-oldest':
        // 가장 오래된 항목 제거
        const oldest = this.findOldest();
        if (oldest) {
          await this.remove(oldest);
          await this.enqueue(item, priority);
        }
        break;

      case 'reject':
        // 새 항목 거부
        throw new QueueOverflowError('Queue is full');

      case 'expand':
        // 동적 확장
        this.config.capacity *= 1.5;
        await this.enqueue(item, priority);
        break;
    }
  }

  async reprioritize(
    itemId: string,
    newPriority: number
  ): Promise<void> {
    const index = this.indexMap.get(itemId);
    
    if (index === undefined) {
      throw new Error(`Item ${itemId} not found in queue`);
    }

    // 우선순위 업데이트
    const item = this.heap.get(index);
    if (this.hasUpdatePriority(item)) {
      this.updatePriority(item, newPriority);
    }

    // 힙 속성 복구
    this.heap.updateAt(index);

    // 인덱스 재계산
    this.rebuildIndex();
  }

  peek(): T | null {
    return this.heap.peek();
  }

  size(): number {
    return this.heap.size();
  }

  isEmpty(): boolean {
    return this.heap.isEmpty();
  }

  private rebuild(): void {
    this.indexMap.clear();
    
    const items = this.heap.toArray();
    for (let i = 0; i < items.length; i++) {
      if (this.hasId(items[i])) {
        this.indexMap.set(this.getId(items[i]), i);
      }
    }
  }

  private hasId(item: any): boolean {
    return item && typeof item.id === 'string';
  }

  private getId(item: any): string {
    return item.id;
  }
}

// 다단계 큐 스케줄러
export class MultiLevelQueueScheduler {
  private levels: QueueLevel[];
  private migrationPolicy: MigrationPolicy;
  private quantumCalculator: QuantumCalculator;

  constructor(config: MultiLevelConfig) {
    this.levels = this.initializeLevels(config.levels);
    this.migrationPolicy = new MigrationPolicy(config.migration);
    this.quantumCalculator = new QuantumCalculator();
  }

  private initializeLevels(levelConfigs: LevelConfig[]): QueueLevel[] {
    return levelConfigs.map((config, index) => ({
      id: `level-${index}`,
      priority: config.priority,
      queue: new AdaptivePriorityQueue({
        comparator: config.comparator || defaultComparator,
        capacity: config.capacity || 1000,
        overflowPolicy: 'drop-lowest'
      }),
      quantum: config.quantum || 100,
      policy: config.policy || 'round-robin'
    }));
  }

  async schedule(): Promise<ScheduledTask | null> {
    // 최상위 레벨부터 확인
    for (const level of this.levels) {
      if (!level.queue.isEmpty()) {
        const task = await level.queue.dequeue();
        
        if (task) {
          // 퀀텀 할당
          task.quantum = this.quantumCalculator.calculate(task, level);
          
          // 레벨 정보 추가
          task.currentLevel = level.id;
          
          return task;
        }
      }
    }

    return null;
  }

  async feedback(
    task: ScheduledTask,
    execution: ExecutionResult
  ): Promise<void> {
    const currentLevel = this.findLevel(task.currentLevel);
    
    if (!currentLevel) return;

    // 마이그레이션 결정
    const migration = await this.migrationPolicy.decide(
      task,
      execution,
      currentLevel
    );

    if (migration.shouldMigrate) {
      const targetLevel = this.findLevel(migration.targetLevel);
      
      if (targetLevel) {
        // 우선순위 조정
        if (migration.adjustPriority) {
          task.priority = migration.newPriority;
        }

        // 레벨 이동
        await targetLevel.queue.enqueue(task, task.priority);
        
        // 통계 업데이트
        this.updateMigrationStats(task, currentLevel, targetLevel);
      }
    } else {
      // 같은 레벨에 재진입
      await currentLevel.queue.enqueue(task, task.priority);
    }
  }

  private findLevel(levelId: string): QueueLevel | undefined {
    return this.levels.find(l => l.id === levelId);
  }
}

// 지능형 백프레셔 시스템
export class BackpressureSystem {
  private thresholds: BackpressureThresholds;
  private currentPressure: Map<string, PressureMetrics>;
  private adaptiveController: AdaptiveBackpressureController;

  constructor(config: BackpressureConfig) {
    this.thresholds = config.thresholds;
    this.currentPressure = new Map();
    this.adaptiveController = new AdaptiveBackpressureController(config);
  }

  async checkPressure(queueId: string): Promise<PressureLevel> {
    const metrics = await this.collectMetrics(queueId);
    const pressure = this.calculatePressure(metrics);

    // 압력 레벨 결정
    if (pressure > this.thresholds.critical) {
      return PressureLevel.CRITICAL;
    } else if (pressure > this.thresholds.high) {
      return PressureLevel.HIGH;
    } else if (pressure > this.thresholds.medium) {
      return PressureLevel.MEDIUM;
    } else {
      return PressureLevel.LOW;
    }
  }

  async applyBackpressure(
    queueId: string,
    level: PressureLevel
  ): Promise<BackpressureAction> {
    switch (level) {
      case PressureLevel.CRITICAL:
        return {
          action: 'reject',
          throttleRate: 0,
          message: 'System overloaded, rejecting new tasks'
        };

      case PressureLevel.HIGH:
        return {
          action: 'throttle',
          throttleRate: 0.2, // 20% 처리율
          delayMs: 1000
        };

      case PressureLevel.MEDIUM:
        return {
          action: 'throttle',
          throttleRate: 0.6, // 60% 처리율
          delayMs: 100
        };

      case PressureLevel.LOW:
        return {
          action: 'accept',
          throttleRate: 1.0
        };
    }
  }

  private calculatePressure(metrics: QueueMetrics): number {
    // 복합 압력 지표 계산
    const queuePressure = metrics.queueDepth / metrics.queueCapacity;
    const latencyPressure = metrics.avgLatency / metrics.targetLatency;
    const errorPressure = metrics.errorRate / metrics.errorThreshold;
    const resourcePressure = metrics.resourceUtilization / 100;

    // 가중 평균
    return (
      queuePressure * 0.3 +
      latencyPressure * 0.3 +
      errorPressure * 0.2 +
      resourcePressure * 0.2
    );
  }
}
```

**검증 기준**:
- [ ] 우선순위 계산 엔진
- [ ] 공정성 제어
- [ ] 다단계 큐 시스템
- [ ] 백프레셔 메커니즘

#### SubTask 5.8.3: 예측 기반 스케줄링
**담당자**: ML 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:
```typescript
// backend/src/orchestration/scheduler/predictive_scheduling.ts
export class PredictiveScheduler {
  private predictor: TaskPredictor;
  private workloadAnalyzer: WorkloadAnalyzer;
  private resourceForecaster: ResourceForecaster;
  private optimizationEngine: ScheduleOptimizer;

  constructor(config: PredictiveConfig) {
    this.predictor = new TaskPredictor(config.model);
    this.workloadAnalyzer = new WorkloadAnalyzer();
    this.resourceForecaster = new ResourceForecaster();
    this.optimizationEngine = new ScheduleOptimizer();
  }

  async generatePredictiveSchedule(
    upcomingTasks: Task[],
    currentState: SystemState,
    horizon: TimeHorizon
  ): Promise<PredictiveSchedule> {
    // 1. 워크로드 분석 및 예측
    const workloadPrediction = await this.workloadAnalyzer.predictWorkload(
      upcomingTasks,
      horizon
    );

    // 2. 리소스 가용성 예측
    const resourcePrediction = await this.resourceForecaster.forecast(
      currentState.resources,
      horizon
    );

    // 3. 태스크별 예측
    const taskPredictions = await this.predictTaskMetrics(upcomingTasks);

    // 4. 최적 스케줄 생성
    const schedule = await this.optimizationEngine.optimize({
      tasks: taskPredictions,
      resources: resourcePrediction,
      workload: workloadPrediction,
      objectives: ['minimize_makespan', 'maximize_utilization'],
      constraints: currentState.constraints
    });

    // 5. 신뢰도 평가
    const confidence = await this.evaluateConfidence(schedule);

    return {
      schedule,
      predictions: taskPredictions,
      confidence,
      recommendations: this.generateRecommendations(schedule, confidence)
    };
  }

  private async predictTaskMetrics(
    tasks: Task[]
  ): Promise<TaskPrediction[]> {
    return Promise.all(tasks.map(async task => {
      const features = await this.extractTaskFeatures(task);
      const prediction = await this.predictor.predict(features);

      return {
        taskId: task.id,
        estimatedDuration: prediction.duration,
        confidenceInterval: prediction.confidenceInterval,
        resourceRequirements: prediction.resources,
        successProbability: prediction.successRate,
        potentialBottlenecks: prediction.bottlenecks,
        optimalStartTime: prediction.optimalStart
      };
    }));
  }

  private async extractTaskFeatures(task: Task): Promise<TaskFeatures> {
    const historicalData = await this.getHistoricalData(task.type);
    const contextualFeatures = await this.extractContextualFeatures(task);

    return {
      // Task intrinsic features
      taskType: task.type,
      priority: task.priority,
      complexity: this.estimateComplexity(task),
      dataSize: task.inputSize || 0,
      
      // Historical features
      avgDuration: historicalData.avgDuration,
      stdDevDuration: historicalData.stdDev,
      failureRate: historicalData.failureRate,
      
      // Contextual features
      timeOfDay: new Date().getHours(),
      dayOfWeek: new Date().getDay(),
      currentLoad: contextualFeatures.systemLoad,
      queueDepth: contextualFeatures.queueDepth,
      
      // Dependencies
      dependencyCount: task.dependencies?.length || 0,
      criticalPathLength: await this.calculateCriticalPath(task)
    };
  }
}

// 태스크 예측 모델
export class TaskPredictor {
  private model: TensorFlowModel;
  private featureEncoder: FeatureEncoder;
  private confidenceEstimator: ConfidenceEstimator;

  constructor(modelConfig: ModelConfig) {
    this.model = new TensorFlowModel(modelConfig);
    this.featureEncoder = new FeatureEncoder();
    this.confidenceEstimator = new ConfidenceEstimator();
  }

  async predict(features: TaskFeatures): Promise<TaskPrediction> {
    // 특징 인코딩
    const encoded = await this.featureEncoder.encode(features);

    // 모델 예측
    const prediction = await this.model.predict(encoded);

    // 신뢰 구간 계산
    const confidence = await this.confidenceEstimator.estimate(
      prediction,
      features
    );

    return {
      duration: prediction.duration,
      confidenceInterval: {
        lower: prediction.duration * (1 - confidence.margin),
        upper: prediction.duration * (1 + confidence.margin)
      },
      resources: {
        cpu: prediction.cpuRequirement,
        memory: prediction.memoryRequirement,
        io: prediction.ioRequirement
      },
      successRate: prediction.successProbability,
      bottlenecks: await this.identifyBottlenecks(prediction, features),
      optimalStart: await this.calculateOptimalStart(prediction, features)
    };
  }

  async train(trainingData: TrainingDataset): Promise<void> {
    // 데이터 전처리
    const processed = await this.preprocessTrainingData(trainingData);

    // 모델 훈련
    await this.model.train(processed, {
      epochs: 100,
      batchSize: 32,
      validationSplit: 0.2,
      callbacks: {
        onEpochEnd: (epoch, logs) => {
          logger.info(`Epoch ${epoch}: loss=${logs.loss}`);
        }
      }
    });

    // 모델 평가
    const evaluation = await this.evaluate(processed.validation);
    logger.info('Model evaluation:', evaluation);
  }

  private async identifyBottlenecks(
    prediction: ModelPrediction,
    features: TaskFeatures
  ): Promise<Bottleneck[]> {
    const bottlenecks: Bottleneck[] = [];

    // CPU 병목
    if (prediction.cpuRequirement > 0.8) {
      bottlenecks.push({
        type: 'cpu',
        severity: 'high',
        impact: 0.3,
        mitigation: 'Consider CPU-optimized instance or parallel processing'
      });
    }

    // 메모리 병목
    if (prediction.memoryRequirement > 0.7) {
      bottlenecks.push({
        type: 'memory',
        severity: 'medium',
        impact: 0.2,
        mitigation: 'Increase memory allocation or optimize memory usage'
      });
    }

    // I/O 병목
    if (prediction.ioRequirement > 0.6 && features.dataSize > 1000000) {
      bottlenecks.push({
        type: 'io',
        severity: 'medium',
        impact: 0.25,
        mitigation: 'Use SSD storage or implement caching strategy'
      });
    }

    // 의존성 병목
    if (features.dependencyCount > 5) {
      bottlenecks.push({
        type: 'dependency',
        severity: 'low',
        impact: 0.15,
        mitigation: 'Consider dependency optimization or parallelization'
      });
    }

    return bottlenecks;
  }
}

// 워크로드 분석기
export class WorkloadAnalyzer {
  private patternDetector: PatternDetector;
  private seasonalityAnalyzer: SeasonalityAnalyzer;
  private anomalyDetector: AnomalyDetector;

  constructor() {
    this.patternDetector = new PatternDetector();
    this.seasonalityAnalyzer = new SeasonalityAnalyzer();
    this.anomalyDetector = new AnomalyDetector();
  }

  async predictWorkload(
    tasks: Task[],
    horizon: TimeHorizon
  ): Promise<WorkloadPrediction> {
    // 1. 과거 데이터 수집
    const historicalData = await this.collectHistoricalData(horizon.start);

    // 2. 패턴 감지
    const patterns = await this.patternDetector.detect(historicalData);

    // 3. 계절성 분석
    const seasonality = await this.seasonalityAnalyzer.analyze(historicalData);

    // 4. 트렌드 분석
    const trend = this.analyzeTrend(historicalData);

    // 5. 예측 모델 적용
    const forecast = await this.forecastWorkload(
      historicalData,
      patterns,
      seasonality,
      trend,
      horizon
    );

    // 6. 이상치 감지
    const anomalies = await this.anomalyDetector.detect(forecast);

    return {
      forecast,
      patterns,
      seasonality,
      trend,
      anomalies,
      confidence: this.calculateConfidence(forecast, historicalData)
    };
  }

  private async forecastWorkload(
    historical: WorkloadData[],
    patterns: Pattern[],
    seasonality: Seasonality,
    trend: Trend,
    horizon: TimeHorizon
  ): Promise<WorkloadForecast[]> {
    const forecasts: WorkloadForecast[] = [];
    
    // ARIMA 모델 적용
    const arimaModel = new ARIMAModel(historical);
    const arimaForecast = await arimaModel.forecast(horizon);

    // 시간대별 예측
    const timeSlots = this.generateTimeSlots(horizon);
    
    for (const slot of timeSlots) {
      const baseLoad = arimaForecast.getValueAt(slot.start);
      
      // 패턴 적용
      let adjustedLoad = baseLoad;
      for (const pattern of patterns) {
        if (pattern.matches(slot)) {
          adjustedLoad *= pattern.multiplier;
        }
      }

      // 계절성 적용
      adjustedLoad *= seasonality.getFactorAt(slot.start);

      // 트렌드 적용
      adjustedLoad += trend.getValueAt(slot.start);

      forecasts.push({
        timeSlot: slot,
        expectedTasks: Math.round(adjustedLoad),
        confidence: this.calculateSlotConfidence(slot, historical),
        resourceDemand: this.estimateResourceDemand(adjustedLoad)
      });
    }

    return forecasts;
  }

  private estimateResourceDemand(taskCount: number): ResourceDemand {
    // 과거 데이터 기반 리소스 수요 예측
    return {
      cpu: taskCount * 0.3, // 평균 CPU 사용량
      memory: taskCount * 512, // MB
      io: taskCount * 10, // IOPS
      network: taskCount * 1 // Mbps
    };
  }
}

// 리소스 예측기
export class ResourceForecaster {
  private availabilityPredictor: AvailabilityPredictor;
  private capacityPlanner: CapacityPlanner;
  private failurePredictor: FailurePredictor;

  async forecast(
    resources: ResourcePool[],
    horizon: TimeHorizon
  ): Promise<ResourceForecast> {
    const forecasts: ResourcePrediction[] = [];

    for (const resource of resources) {
      // 가용성 예측
      const availability = await this.availabilityPredictor.predict(
        resource,
        horizon
      );

      // 용량 계획
      const capacity = await this.capacityPlanner.plan(
        resource,
        horizon
      );

      // 장애 예측
      const failureProbability = await this.failurePredictor.predict(
        resource,
        horizon
      );

      forecasts.push({
        resourceId: resource.id,
        availability,
        capacity,
        failureProbability,
        maintenanceWindows: await this.getMaintenanceWindows(resource, horizon),
        costProjection: await this.projectCost(resource, capacity, horizon)
      });
    }

    return {
      resources: forecasts,
      aggregateCapacity: this.calculateAggregateCapacity(forecasts),
      recommendations: await this.generateCapacityRecommendations(forecasts)
    };
  }

  private async generateCapacityRecommendations(
    forecasts: ResourcePrediction[]
  ): Promise<CapacityRecommendation[]> {
    const recommendations: CapacityRecommendation[] = [];

    for (const forecast of forecasts) {
      // 용량 부족 예측
      if (forecast.capacity.utilization > 0.8) {
        recommendations.push({
          resourceId: forecast.resourceId,
          type: 'scale-up',
          urgency: forecast.capacity.utilization > 0.9 ? 'high' : 'medium',
          recommendation: `Scale up by ${Math.ceil((forecast.capacity.utilization - 0.7) * 100)}%`,
          estimatedCost: forecast.costProjection.scaleUpCost
        });
      }

      // 과잉 용량
      if (forecast.capacity.utilization < 0.3) {
        recommendations.push({
          resourceId: forecast.resourceId,
          type: 'scale-down',
          urgency: 'low',
          recommendation: `Consider scaling down by ${Math.floor((0.5 - forecast.capacity.utilization) * 100)}%`,
          estimatedSavings: forecast.costProjection.scaleDownSavings
        });
      }

      // 장애 위험
      if (forecast.failureProbability > 0.1) {
        recommendations.push({
          resourceId: forecast.resourceId,
          type: 'maintenance',
          urgency: 'high',
          recommendation: 'Schedule preventive maintenance',
          risk: forecast.failureProbability
        });
      }
    }

    return recommendations;
  }
}

// 스케줄 최적화 엔진
export class ScheduleOptimizer {
  private solver: OptimizationSolver;
  private evaluator: ScheduleEvaluator;

  constructor() {
    this.solver = new GeneticOptimizationSolver();
    this.evaluator = new ScheduleEvaluator();
  }

  async optimize(params: OptimizationParams): Promise<OptimizedSchedule> {
    // 1. 초기 스케줄 생성
    const initialSchedule = this.generateInitialSchedule(
      params.tasks,
      params.resources
    );

    // 2. 최적화 문제 정의
    const problem = this.formulateOptimizationProblem(params);

    // 3. 최적화 실행
    const solution = await this.solver.solve(problem, {
      initialSolution: initialSchedule,
      maxIterations: 1000,
      timeLimit: 30000 // 30초
    });

    // 4. 스케줄 평가
    const evaluation = await this.evaluator.evaluate(
      solution.schedule,
      params.objectives
    );

    return {
      schedule: solution.schedule,
      objectives: evaluation,
      improvements: this.calculateImprovements(initialSchedule, solution.schedule),
      confidence: solution.confidence
    };
  }

  private formulateOptimizationProblem(
    params: OptimizationParams
  ): OptimizationProblem {
    return {
      variables: this.createDecisionVariables(params.tasks, params.resources),
      objectives: params.objectives.map(obj => this.createObjectiveFunction(obj)),
      constraints: [
        ...this.createResourceConstraints(params.resources),
        ...this.createDependencyConstraints(params.tasks),
        ...this.createCustomConstraints(params.constraints)
      ]
    };
  }

  private createObjectiveFunction(objective: string): ObjectiveFunction {
    switch (objective) {
      case 'minimize_makespan':
        return {
          type: 'minimize',
          function: (schedule: Schedule) => this.calculateMakespan(schedule)
        };

      case 'maximize_utilization':
        return {
          type: 'maximize',
          function: (schedule: Schedule) => this.calculateUtilization(schedule)
        };

      case 'minimize_cost':
        return {
          type: 'minimize',
          function: (schedule: Schedule) => this.calculateCost(schedule)
        };

      case 'balance_load':
        return {
          type: 'minimize',
          function: (schedule: Schedule) => this.calculateLoadImbalance(schedule)
        };

      default:
        throw new Error(`Unknown objective: ${objective}`);
    }
  }
}

// 예측 신뢰도 평가기
export class ConfidenceEstimator {
  private uncertaintyQuantifier: UncertaintyQuantifier;
  private validationMetrics: ValidationMetrics;

  async estimate(
    prediction: any,
    features: any
  ): Promise<ConfidenceEstimate> {
    // 1. 불확실성 정량화
    const uncertainty = await this.uncertaintyQuantifier.quantify(
      prediction,
      features
    );

    // 2. 과거 정확도 분석
    const historicalAccuracy = await this.getHistoricalAccuracy(
      features.taskType
    );

    // 3. 특징 신뢰도
    const featureConfidence = this.assessFeatureQuality(features);

    // 4. 모델 신뢰도
    const modelConfidence = await this.assessModelConfidence(prediction);

    // 종합 신뢰도 계산
    const overallConfidence = this.combineConfidenceScores({
      uncertainty: 1 - uncertainty.epistemic,
      accuracy: historicalAccuracy,
      features: featureConfidence,
      model: modelConfidence
    });

    return {
      overall: overallConfidence,
      components: {
        dataQuality: featureConfidence,
        modelCertainty: modelConfidence,
        historicalPerformance: historicalAccuracy
      },
      margin: uncertainty.aleatoric,
      recommendation: this.getConfidenceRecommendation(overallConfidence)
    };
  }

  private combineConfidenceScores(scores: ConfidenceComponents): number {
    // 가중 조화 평균
    const weights = {
      uncertainty: 0.3,
      accuracy: 0.3,
      features: 0.2,
      model: 0.2
    };

    let weightedSum = 0;
    let totalWeight = 0;

    for (const [key, value] of Object.entries(scores)) {
      const weight = weights[key] || 0.1;
      weightedSum += weight / value;
      totalWeight += weight;
    }

    return totalWeight / weightedSum;
  }

  private getConfidenceRecommendation(confidence: number): string {
    if (confidence > 0.9) {
      return 'High confidence - proceed with predicted schedule';
    } else if (confidence > 0.7) {
      return 'Moderate confidence - monitor closely';
    } else if (confidence > 0.5) {
      return 'Low confidence - consider fallback options';
    } else {
      return 'Very low confidence - use conservative estimates';
    }
  }
}

// 적응형 스케줄러
export class AdaptiveScheduler {
  private baseScheduler: PredictiveScheduler;
  private performanceMonitor: PerformanceMonitor;
  private adaptationEngine: AdaptationEngine;

  async scheduleWithAdaptation(
    request: SchedulingRequest
  ): Promise<AdaptiveSchedule> {
    // 1. 초기 예측 스케줄
    const predictiveSchedule = await this.baseScheduler.generatePredictiveSchedule(
      request.tasks,
      request.currentState,
      request.horizon
    );

    // 2. 적응형 조정
    const adaptedSchedule = await this.adaptationEngine.adapt(
      predictiveSchedule,
      await this.performanceMonitor.getCurrentPerformance()
    );

    // 3. 실시간 모니터링 설정
    const monitoringPlan = this.setupMonitoring(adaptedSchedule);

    // 4. 피드백 루프 설정
    this.setupFeedbackLoop(adaptedSchedule);

    return {
      schedule: adaptedSchedule,
      monitoringPlan,
      adaptationRules: this.generateAdaptationRules(adaptedSchedule),
      fallbackOptions: await this.generateFallbacks(adaptedSchedule)
    };
  }

  private setupFeedbackLoop(schedule: Schedule): void {
    // 실행 결과 수집
    schedule.onTaskComplete((task, result) => {
      this.performanceMonitor.recordExecution(task, result);
      
      // 예측 정확도 업데이트
      this.updatePredictionAccuracy(task, result);
      
      // 필요시 재스케줄링
      if (this.needsRescheduling(result)) {
        this.triggerRescheduling(schedule, task);
      }
    });

    // 주기적 성능 평가
    setInterval(() => {
      this.evaluateSchedulePerformance(schedule);
    }, 60000); // 1분마다
  }

  private generateAdaptationRules(
    schedule: Schedule
  ): AdaptationRule[] {
    return [
      {
        condition: 'task_duration_deviation > 20%',
        action: 'reschedule_dependent_tasks',
        priority: 'high'
      },
      {
        condition: 'resource_failure',
        action: 'migrate_to_backup_resource',
        priority: 'critical'
      },
      {
        condition: 'queue_depth > threshold',
        action: 'enable_burst_capacity',
        priority: 'medium'
      },
      {
        condition: 'success_rate < 0.8',
        action: 'increase_retry_budget',
        priority: 'medium'
      }
    ];
  }

  async triggerRescheduling(
    currentSchedule: Schedule,
    triggerTask: Task
  ): Promise<void> {
    // 영향받는 태스크 식별
    const affectedTasks = this.identifyAffectedTasks(
      currentSchedule,
      triggerTask
    );

    // 부분 재스케줄링
    const partialSchedule = await this.baseScheduler.reschedulePartial(
      affectedTasks,
      currentSchedule
    );

    // 스케줄 업데이트
    await this.applyScheduleUpdate(currentSchedule, partialSchedule);
  }
}
```

**검증 기준**:
- [ ] ML 기반 태스크 예측
- [ ] 워크로드 패턴 분석
- [ ] 리소스 가용성 예측
- [ ] 적응형 스케줄링

#### SubTask 5.8.4: 스케줄러 성능 최적화
**담당자**: 성능 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:
```typescript
// backend/src/orchestration/scheduler/performance_optimization.ts
export class SchedulerPerformanceOptimizer {
  private profiler: SchedulerProfiler;
  private cacheManager: ScheduleCacheManager;
  private parallelizer: ScheduleParallelizer;
  private indexOptimizer: IndexOptimizer;

  constructor(config: OptimizerConfig) {
    this.profiler = new SchedulerProfiler();
    this.cacheManager = new ScheduleCacheManager(config.cache);
    this.parallelizer = new ScheduleParallelizer(config.parallelism);
    this.indexOptimizer = new IndexOptimizer();
  }

  async optimizeScheduler(
    scheduler: IntelligentScheduler
  ): Promise<OptimizationResult> {
    // 1. 성능 프로파일링
    const profile = await this.profiler.profile(scheduler);

    // 2. 병목 지점 식별
    const bottlenecks = this.identifyBottlenecks(profile);

    // 3. 최적화 전략 적용
    const optimizations = await this.applyOptimizations(
      scheduler,
      bottlenecks
    );

    // 4. 성능 검증
    const validation = await this.validateOptimizations(
      scheduler,
      optimizations
    );

    return {
      originalPerformance: profile,
      optimizations,
      improvement: validation.improvement,
      recommendations: this.generateRecommendations(validation)
    };
  }

  private async applyOptimizations(
    scheduler: IntelligentScheduler,
    bottlenecks: Bottleneck[]
  ): Promise<AppliedOptimization[]> {
    const optimizations: AppliedOptimization[] = [];

    for (const bottleneck of bottlenecks) {
      switch (bottleneck.type) {
        case 'algorithm_complexity':
          optimizations.push(
            await this.optimizeAlgorithmComplexity(scheduler, bottleneck)
          );
          break;

        case 'data_structure':
          optimizations.push(
            await this.optimizeDataStructures(scheduler, bottleneck)
          );
          break;

        case 'io_bound':
          optimizations.push(
            await this.optimizeIO(scheduler, bottleneck)
          );
          break;

        case 'cache_miss':
          optimizations.push(
            await this.optimizeCaching(scheduler, bottleneck)
          );
          break;

        case 'lock_contention':
          optimizations.push(
            await this.optimizeLocking(scheduler, bottleneck)
          );
          break;
      }
    }

    return optimizations;
  }

  private async optimizeAlgorithmComplexity(
    scheduler: IntelligentScheduler,
    bottleneck: Bottleneck
  ): Promise<AppliedOptimization> {
    // 휴리스틱 개선
    if (bottleneck.location === 'task_sorting') {
      // 힙 기반 정렬로 변경
      return {
        type: 'algorithm',
        description: 'Replace quicksort with heap-based sorting',
        implementation: async () => {
          scheduler.setSortingAlgorithm(new HeapSort());
        },
        expectedImprovement: 0.3
      };
    }

    // 동적 프로그래밍 적용
    if (bottleneck.location === 'dependency_resolution') {
      return {
        type: 'algorithm',
        description: 'Apply dynamic programming to dependency resolution',
        implementation: async () => {
          scheduler.setDependencyResolver(new DPDependencyResolver());
        },
        expectedImprovement: 0.4
      };
    }

    return null;
  }

  private async optimizeCaching(
    scheduler: IntelligentScheduler,
    bottleneck: Bottleneck
  ): Promise<AppliedOptimization> {
    const cacheConfig = await this.cacheManager.analyzeAndConfigure(
      bottleneck
    );

    return {
      type: 'caching',
      description: 'Implement multi-level caching strategy',
      implementation: async () => {
        // L1 캐시 - 자주 사용되는 스케줄 결정
        scheduler.addCache('l1', new LRUCache({
          maxSize: 1000,
          ttl: 60000 // 1분
        }));

        // L2 캐시 - 태스크 예측 결과
        scheduler.addCache('l2', new RedisCache({
          maxSize: 10000,
          ttl: 300000 // 5분
        }));

        // 캐시 워밍
        await this.warmCache(scheduler);
      },
      expectedImprovement: 0.5
    };
  }

  private async warmCache(scheduler: IntelligentScheduler): Promise<void> {
    // 자주 사용되는 패턴 사전 계산
    const commonPatterns = await this.identifyCommonPatterns();

    for (const pattern of commonPatterns) {
      const result = await scheduler.computeSchedule(pattern);
      await scheduler.cache.set(pattern.key, result);
    }
  }
}

// 스케줄 캐시 관리자
export class ScheduleCacheManager {
  private caches: Map<string, ICache>;
  private hitRateMonitor: HitRateMonitor;
  private evictionPolicy: EvictionPolicy;

  constructor(config: CacheConfig) {
    this.caches = new Map();
    this.hitRateMonitor = new HitRateMonitor();
    this.evictionPolicy = new AdaptiveEvictionPolicy(config);
  }

  async get(
    key: string,
    compute: () => Promise<any>
  ): Promise<CacheResult> {
    const startTime = Date.now();
    
    // 다단계 캐시 확인
    for (const [name, cache] of this.caches) {
      const value = await cache.get(key);
      
      if (value !== undefined) {
        this.hitRateMonitor.recordHit(name);
        
        return {
          value,
          cached: true,
          cacheLevel: name,
          latency: Date.now() - startTime
        };
      }
    }

    // 캐시 미스 - 계산 수행
    this.hitRateMonitor.recordMiss();
    const value = await compute();

    // 캐시에 저장
    await this.store(key, value);

    return {
      value,
      cached: false,
      latency: Date.now() - startTime
    };
  }

  private async store(key: string, value: any): Promise<void> {
    // 적응형 캐싱 - 값의 중요도에 따라 캐시 레벨 결정
    const importance = await this.calculateImportance(key, value);
    
    if (importance > 0.8) {
      // 모든 레벨에 저장
      for (const [name, cache] of this.caches) {
        await cache.set(key, value);
      }
    } else if (importance > 0.5) {
      // L1, L2에만 저장
      await this.caches.get('l1')?.set(key, value);
      await this.caches.get('l2')?.set(key, value);
    } else {
      // L1에만 저장
      await this.caches.get('l1')?.set(key, value);
    }
  }

  async invalidate(pattern: string): Promise<void> {
    const tasks = [];
    
    for (const [name, cache] of this.caches) {
      tasks.push(cache.invalidate(pattern));
    }

    await Promise.all(tasks);
  }

  getStats(): CacheStatistics {
    return {
      hitRate: this.hitRateMonitor.getOverallHitRate(),
      levelStats: this.hitRateMonitor.getLevelStats(),
      memoryUsage: this.calculateMemoryUsage(),
      evictionStats: this.evictionPolicy.getStats()
    };
  }
}

// 병렬 스케줄링 최적화
export class ScheduleParallelizer {
  private workerPool: WorkerPool;
  private taskPartitioner: TaskPartitioner;
  private resultAggregator: ResultAggregator;

  constructor(config: ParallelismConfig) {
    this.workerPool = new WorkerPool(config.workers);
    this.taskPartitioner = new TaskPartitioner();
    this.resultAggregator = new ResultAggregator();
  }

  async parallelSchedule(
    tasks: Task[],
    resources: ResourcePool[]
  ): Promise<Schedule> {
    // 1. 태스크 분할
    const partitions = await this.taskPartitioner.partition(
      tasks,
      this.workerPool.size
    );

    // 2. 병렬 스케줄링
    const partialSchedules = await Promise.all(
      partitions.map((partition, index) => 
        this.workerPool.execute(index, {
          type: 'schedule',
          tasks: partition,
          resources: resources
        })
      )
    );

    // 3. 결과 병합
    const mergedSchedule = await this.resultAggregator.merge(
      partialSchedules
    );

    // 4. 충돌 해결
    const resolved = await this.resolveConflicts(mergedSchedule);

    return resolved;
  }

  private async resolveConflicts(
    schedule: Schedule
  ): Promise<Schedule> {
    const conflicts = this.detectConflicts(schedule);
    
    if (conflicts.length === 0) {
      return schedule;
    }

    // 충돌 해결 전략
    const resolver = new ConflictResolver();
    
    for (const conflict of conflicts) {
      const resolution = await resolver.resolve(conflict);
      this.applyResolution(schedule, resolution);
    }

    // 재귀적으로 확인
    return this.resolveConflicts(schedule);
  }
}

// 인덱스 최적화
export class IndexOptimizer {
  private indexAnalyzer: IndexAnalyzer;
  private indexBuilder: IndexBuilder;

  async optimizeIndices(
    scheduler: IntelligentScheduler
  ): Promise<IndexOptimization[]> {
    // 1. 쿼리 패턴 분석
    const queryPatterns = await this.indexAnalyzer.analyzeQueries(
      scheduler.getQueryLog()
    );

    // 2. 인덱스 추천
    const recommendations = this.recommendIndices(queryPatterns);

    // 3. 인덱스 구축
    const optimizations: IndexOptimization[] = [];

    for (const rec of recommendations) {
      const index = await this.indexBuilder.build(rec);
      
      optimizations.push({
        name: rec.name,
        type: rec.type,
        fields: rec.fields,
        improvement: await this.measureImprovement(scheduler, index)
      });

      // 스케줄러에 인덱스 적용
      scheduler.addIndex(index);
    }

    return optimizations;
  }

  private recommendIndices(
    patterns: QueryPattern[]
  ): IndexRecommendation[] {
    const recommendations: IndexRecommendation[] = [];

    // 빈도가 높은 쿼리 패턴에 대한 인덱스
    const frequentPatterns = patterns.filter(p => p.frequency > 100);
    
    for (const pattern of frequentPatterns) {
      if (pattern.type === 'task_by_priority') {
        recommendations.push({
          name: 'idx_task_priority',
          type: 'btree',
          fields: ['priority', 'created_at'],
          unique: false
        });
      }

      if (pattern.type === 'resource_availability') {
        recommendations.push({
          name: 'idx_resource_availability',
          type: 'bitmap',
          fields: ['resource_id', 'available'],
          unique: false
        });
      }

      if (pattern.type === 'dependency_lookup') {
        recommendations.push({
          name: 'idx_task_dependencies',
          type: 'hash',
          fields: ['task_id', 'depends_on'],
          unique: false
        });
      }
    }

    return recommendations;
  }
}

// JIT 컴파일 최적화
export class JITOptimizer {
  private compiler: JITCompiler;
  private hotspotDetector: HotspotDetector;

  async optimize(scheduler: IntelligentScheduler): Promise<void> {
    // 1. 핫스팟 감지
    const hotspots = await this.hotspotDetector.detect(scheduler);

    // 2. 핫 경로 컴파일
    for (const hotspot of hotspots) {
      if (hotspot.invocations > 10000) {
        const optimizedCode = await this.compiler.compile(
          hotspot.function,
          {
            level: 'aggressive',
            inlining: true,
            vectorization: true
          }
        );

        // 원본 함수 교체
        scheduler.replaceFunction(
          hotspot.functionName,
          optimizedCode
        );
      }
    }

    // 3. 인라인 캐싱
    this.enableInlineCaching(scheduler);
  }

  private enableInlineCaching(scheduler: IntelligentScheduler): void {
    // 다형성 호출 사이트 최적화
    scheduler.enableFeature('inline_caching', {
      maxCacheSize: 8,
      monomorphicThreshold: 0.95,
      polymorphicThreshold: 0.8
    });
  }
}

// 메모리 최적화
export class MemoryOptimizer {
  private memoryProfiler: MemoryProfiler;
  private objectPoolManager: ObjectPoolManager;
  private gcTuner: GCTuner;

  async optimizeMemory(scheduler: IntelligentScheduler): Promise<void> {
    // 1. 메모리 프로파일링
    const profile = await this.memoryProfiler.profile(scheduler);

    // 2. 객체 풀 적용
    if (profile.allocationRate > 1000) { // 초당 1000개 이상 할당
      await this.applyObjectPooling(scheduler, profile);
    }

    // 3. GC 튜닝
    await this.gcTuner.tune({
      heapSize: profile.heapSize,
      allocationRate: profile.allocationRate,
      gcPauseTarget: 10 // 10ms
    });

    // 4. 메모리 압축
    if (profile.fragmentation > 0.3) {
      await this.compactMemory(scheduler);
    }
  }

  private async applyObjectPooling(
    scheduler: IntelligentScheduler,
    profile: MemoryProfile
  ): Promise<void> {
    // 자주 할당되는 객체 타입 식별
    const hotTypes = profile.hotAllocationTypes;

    for (const type of hotTypes) {
      const pool = this.objectPoolManager.createPool({
        type,
        initialSize: 100,
        maxSize: 1000,
        factory: () => new type(),
        reset: (obj) => obj.reset()
      });

      // 스케줄러에 풀 등록
      scheduler.registerObjectPool(type, pool);
    }
  }

  private async compactMemory(
    scheduler: IntelligentScheduler
  ): Promise<void> {
    // 메모리 압축 전략
    await scheduler.pauseScheduling();
    
    // 1. 불필요한 참조 제거
    scheduler.cleanupReferences();
    
    // 2. 강제 GC
    if (global.gc) {
      global.gc();
    }
    
    // 3. 메모리 재구성
    await scheduler.reorganizeMemory();
    
    await scheduler.resumeScheduling();
  }
}
```

**검증 기준**:
- [ ] 성능 프로파일링 시스템
- [ ] 캐싱 전략 구현
- [ ] 병렬 처리 최적화
- [ ] 메모리 및 GC 최적화

### Task 5.9: 부하 분산 및 자동 스케일링

#### SubTask 5.9.1: 부하 분산 전략 구현
**담당자**: 인프라 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/loadbalancing/load_balancer.ts
export interface LoadBalancingStrategy {
  name: string;
  selectTarget(
    request: WorkloadRequest,
    targets: Target[],
    metrics: TargetMetrics[]
  ): Promise<Target | null>;
}

export class IntelligentLoadBalancer {
  private strategies: Map<string, LoadBalancingStrategy>;
  private metricsCollector: MetricsCollector;
  private healthChecker: HealthChecker;
  private circuitBreaker: CircuitBreaker;

  constructor(config: LoadBalancerConfig) {
    this.strategies = new Map();
    this.metricsCollector = new MetricsCollector(config.metrics);
    this.healthChecker = new HealthChecker(config.health);
    this.circuitBreaker = new CircuitBreaker(config.circuitBreaker);
    
    this.registerStrategies();
  }

  private registerStrategies(): void {
    this.strategies.set('round-robin', new RoundRobinStrategy());
    this.strategies.set('least-connections', new LeastConnectionsStrategy());
    this.strategies.set('weighted-round-robin', new WeightedRoundRobinStrategy());
    this.strategies.set('least-response-time', new LeastResponseTimeStrategy());
    this.strategies.set('hash-based', new HashBasedStrategy());
    this.strategies.set('adaptive', new AdaptiveStrategy());
    this.strategies.set('ml-optimized', new MLOptimizedStrategy());
  }

  async route(request: WorkloadRequest): Promise<RoutingResult> {
    const startTime = Date.now();

    try {
      // 1. 건강한 타겟 필터링
      const healthyTargets = await this.getHealthyTargets();

      if (healthyTargets.length === 0) {
        throw new NoHealthyTargetsError('No healthy targets available');
      }

      // 2. 타겟 메트릭 수집
      const metrics = await this.collectTargetMetrics(healthyTargets);

      // 3. 전략 선택
      const strategy = await this.selectStrategy(request, metrics);

      // 4. 타겟 선택
      const target = await strategy.selectTarget(
        request,
        healthyTargets,
        metrics
      );

      if (!target) {
        throw new NoSuitableTargetError('No suitable target found');
      }

      // 5. 서킷 브레이커 확인
      if (await this.circuitBreaker.isOpen(target.id)) {
        return this.handleCircuitOpen(request, target);
      }

      // 6. 라우팅 실행
      const result = await this.executeRouting(request, target);

      // 7. 메트릭 업데이트
      await this.updateMetrics(target, result, Date.now() - startTime);

      return result;

    } catch (error) {
      logger.error('Load balancing failed', { error, request });
      throw error;
    }
  }

  private async getHealthyTargets(): Promise<Target[]> {
    const allTargets = await this.getAllTargets();
    const healthChecks = await Promise.all(
      allTargets.map(target => this.healthChecker.check(target))
    );

    return allTargets.filter((target, index) => healthChecks[index].healthy);
  }

  private async selectStrategy(
    request: WorkloadRequest,
    metrics: TargetMetrics[]
  ): Promise<LoadBalancingStrategy> {
    // 요청 특성에 따른 전략 선택
    if (request.requiresAffinity) {
      return this.strategies.get('hash-based')!;
    }

    if (request.priority === 'high') {
      return this.strategies.get('least-response-time')!;
    }

    // 시스템 상태에 따른 적응형 선택
    const systemLoad = this.calculateSystemLoad(metrics);
    if (systemLoad.variance > 0.3) {
      return this.strategies.get('adaptive')!;
    }

    // 기본 전략
    return this.strategies.get('weighted-round-robin')!;
  }

  private async executeRouting(
    request: WorkloadRequest,
    target: Target
  ): Promise<RoutingResult> {
    try {
      // 연결 수 증가
      await this.incrementConnections(target);

      // 실제 라우팅
      const response = await this.forwardRequest(request, target);

      return {
        success: true,
        target,
        response,
        latency: response.latency
      };

    } catch (error) {
      // 실패 처리
      await this.handleRoutingFailure(target, error);
      throw error;

    } finally {
      // 연결 수 감소
      await this.decrementConnections(target);
    }
  }
}

// 적응형 부하 분산 전략
export class AdaptiveStrategy implements LoadBalancingStrategy {
  name = 'adaptive';
  
  private predictor: LoadPredictor;
  private optimizer: TargetOptimizer;

  constructor() {
    this.predictor = new LoadPredictor();
    this.optimizer = new TargetOptimizer();
  }

  async selectTarget(
    request: WorkloadRequest,
    targets: Target[],
    metrics: TargetMetrics[]
  ): Promise<Target | null> {
    // 1. 미래 부하 예측
    const predictions = await this.predictor.predictLoad(targets, metrics);

    // 2. 최적화 점수 계산
    const scores = await this.calculateOptimizationScores(
      request,
      targets,
      metrics,
      predictions
    );

    // 3. 최적 타겟 선택
    const optimal = this.selectOptimalTarget(scores);

    return optimal;
  }

  private async calculateOptimizationScores(
    request: WorkloadRequest,
    targets: Target[],
    metrics: TargetMetrics[],
    predictions: LoadPrediction[]
  ): Promise<TargetScore[]> {
    const scores: TargetScore[] = [];

    for (let i = 0; i < targets.length; i++) {
      const target = targets[i];
      const metric = metrics[i];
      const prediction = predictions[i];

      const score = await this.optimizer.calculateScore({
        target,
        currentMetrics: metric,
        predictedLoad: prediction,
        requestCharacteristics: request,
        weights: {
          responseTime: 0.3,
          throughput: 0.2,
          errorRate: 0.2,
          resourceUtilization: 0.2,
          predictedAvailability: 0.1
        }
      });

      scores.push({ target, score });
    }

    return scores;
  }

  private selectOptimalTarget(scores: TargetScore[]): Target | null {
    if (scores.length === 0) return null;

    // 점수 기반 확률적 선택 (높은 점수일수록 선택 확률 증가)
    const totalScore = scores.reduce((sum, s) => sum + s.score, 0);
    
    if (totalScore === 0) {
      // 모든 점수가 0인 경우 균등 선택
      return scores[Math.floor(Math.random() * scores.length)].target;
    }

    let random = Math.random() * totalScore;
    
    for (const { target, score } of scores) {
      random -= score;
      if (random <= 0) {
        return target;
      }
    }

    return scores[scores.length - 1].target;
  }
}

// ML 최적화 부하 분산
export class MLOptimizedStrategy implements LoadBalancingStrategy {
  name = 'ml-optimized';
  
  private model: LoadBalancingModel;
  private featureExtractor: FeatureExtractor;

  constructor() {
    this.model = new LoadBalancingModel();
    this.featureExtractor = new FeatureExtractor();
  }

  async selectTarget(
    request: WorkloadRequest,
    targets: Target[],
    metrics: TargetMetrics[]
  ): Promise<Target | null> {
    // 1. 특징 추출
    const features = await this.featureExtractor.extract({
      request,
      targets,
      metrics,
      timestamp: new Date()
    });

    // 2. ML 모델 예측
    const predictions = await this.model.predict(features);

    // 3. 최적 타겟 선택
    const targetIndex = predictions.optimalTargetIndex;
    
    if (targetIndex >= 0 && targetIndex < targets.length) {
      return targets[targetIndex];
    }

    // 폴백: 최소 응답 시간
    return this.fallbackSelection(targets, metrics);
  }

  private fallbackSelection(
    targets: Target[],
    metrics: TargetMetrics[]
  ): Target | null {
    let minResponseTime = Infinity;
    let selectedTarget: Target | null = null;

    for (let i = 0; i < targets.length; i++) {
      if (metrics[i].avgResponseTime < minResponseTime) {
        minResponseTime = metrics[i].avgResponseTime;
        selectedTarget = targets[i];
      }
    }

    return selectedTarget;
  }
}

// 지역 인식 부하 분산
export class GeoAwareLoadBalancer {
  private geoResolver: GeoResolver;
  private latencyPredictor: LatencyPredictor;
  private complianceChecker: ComplianceChecker;

  async route(request: WorkloadRequest): Promise<RoutingResult> {
    // 1. 요청 지역 확인
    const requestLocation = await this.geoResolver.resolve(request.clientIP);

    // 2. 규정 준수 확인
    const complianceRequirements = await this.complianceChecker.check(
      requestLocation,
      request.dataType
    );

    // 3. 적합한 타겟 필터링
    const eligibleTargets = await this.filterByCompliance(
      await this.getAllTargets(),
      complianceRequirements
    );

    // 4. 지연 시간 예측
    const latencyPredictions = await this.latencyPredictor.predict(
      requestLocation,
      eligibleTargets
    );

    // 5. 최적 타겟 선택
    const optimal = this.selectOptimalByLatency(
      eligibleTargets,
      latencyPredictions
    );

    return this.executeRouting(request, optimal);
  }

  private async filterByCompliance(
    targets: Target[],
    requirements: ComplianceRequirements
  ): Promise<Target[]> {
    return targets.filter(target => {
      // 데이터 상주 요구사항
      if (requirements.dataResidency) {
        if (!requirements.allowedRegions.includes(target.region)) {
          return false;
        }
      }

      // GDPR 준수
      if (requirements.gdprCompliant && !target.gdprCertified) {
        return false;
      }

      // 기타 규정
      return true;
    });
  }

  private selectOptimalByLatency(
    targets: Target[],
    predictions: LatencyPrediction[]
  ): Target {
    // P95 지연시간 기준 선택
    let minP95 = Infinity;
    let optimalTarget = targets[0];

    for (let i = 0; i < targets.length; i++) {
      if (predictions[i].p95 < minP95) {
        minP95 = predictions[i].p95;
        optimalTarget = targets[i];
      }
    }

    return optimalTarget;
  }
}

// 세션 친화성 관리
export class SessionAffinityManager {
  private sessionStore: SessionStore;
  private affinityRules: AffinityRule[];

  async getTargetForSession(
    sessionId: string,
    availableTargets: Target[]
  ): Promise<Target | null> {
    // 1. 기존 세션 확인
    const existingAffinity = await this.sessionStore.get(sessionId);
    
    if (existingAffinity) {
      const target = availableTargets.find(
        t => t.id === existingAffinity.targetId
      );
      
      if (target) {
        // 세션 갱신
        await this.sessionStore.refresh(sessionId);
        return target;
      }
    }

    // 2. 새 타겟 할당
    const newTarget = await this.assignNewTarget(
      sessionId,
      availableTargets
    );

    // 3. 세션 저장
    await this.sessionStore.set(sessionId, {
      targetId: newTarget.id,
      createdAt: new Date(),
      lastAccessed: new Date()
    });

    return newTarget;
  }

  private async assignNewTarget(
    sessionId: string,
    targets: Target[]
  ): Promise<Target> {
    // 세션 기반 일관된 해싱
    const hash = this.hashSession(sessionId);
    const index = hash % targets.length;
    
    return targets[index];
  }

  private hashSession(sessionId: string): number {
    let hash = 0;
    for (let i = 0; i < sessionId.length; i++) {
      const char = sessionId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }
}

// 동적 가중치 관리
export class DynamicWeightManager {
  private weights: Map<string, number>;
  private performanceTracker: PerformanceTracker;
  private adjustmentPolicy: WeightAdjustmentPolicy;

  async updateWeights(
    targets: Target[],
    metrics: TargetMetrics[]
  ): Promise<void> {
    for (let i = 0; i < targets.length; i++) {
      const target = targets[i];
      const metric = metrics[i];

      // 성능 점수 계산
      const performanceScore = await this.calculatePerformanceScore(metric);

      // 가중치 조정
      const currentWeight = this.weights.get(target.id) || 1.0;
      const newWeight = await this.adjustmentPolicy.adjust(
        currentWeight,
        performanceScore,
        metric
      );

      this.weights.set(target.id, newWeight);
    }

    // 정규화
    this.normalizeWeights();
  }

  private async calculatePerformanceScore(
    metrics: TargetMetrics
  ): Promise<number> {
    // 복합 성능 지표
    const responseTimeScore = 1 / (1 + metrics.avgResponseTime / 100);
    const errorRateScore = 1 - metrics.errorRate;
    const throughputScore = metrics.throughput / 1000;
    const availabilityScore = metrics.availability;

    return (
      responseTimeScore * 0.3 +
      errorRateScore * 0.3 +
      throughputScore * 0.2 +
      availabilityScore * 0.2
    );
  }

  private normalizeWeights(): void {
    const total = Array.from(this.weights.values()).reduce(
      (sum, w) => sum + w,
      0
    );

    if (total > 0) {
      for (const [targetId, weight] of this.weights.entries()) {
        this.weights.set(targetId, weight / total);
      }
    }
  }

  getWeight(targetId: string): number {
    return this.weights.get(targetId) || 0;
  }
}

// 부하 분산 상태 모니터
export class LoadBalancerMonitor {
  private metricsCollector: MetricsCollector;
  private anomalyDetector: AnomalyDetector;
  private dashboardReporter: DashboardReporter;

  async monitor(loadBalancer: IntelligentLoadBalancer): Promise<void> {
    // 실시간 메트릭 수집
    setInterval(async () => {
      const metrics = await this.collectMetrics(loadBalancer);
      
      // 이상 감지
      const anomalies = await this.anomalyDetector.detect(metrics);
      
      if (anomalies.length > 0) {
        await this.handleAnomalies(anomalies);
      }

      // 대시보드 업데이트
      await this.dashboardReporter.update(metrics);
      
    }, 5000); // 5초마다
  }

  private async collectMetrics(
    loadBalancer: IntelligentLoadBalancer
  ): Promise<LoadBalancerMetrics> {
    return {
      timestamp: new Date(),
      requestRate: await this.metricsCollector.getRequestRate(),
      avgResponseTime: await this.metricsCollector.getAvgResponseTime(),
      errorRate: await this.metricsCollector.getErrorRate(),
      targetDistribution: await this.getTargetDistribution(loadBalancer),
      activeConnections: await this.getActiveConnections(),
      queueDepth: await this.getQueueDepth()
    };
  }

  private async handleAnomalies(anomalies: Anomaly[]): Promise<void> {
    for (const anomaly of anomalies) {
      logger.warn('Load balancer anomaly detected', anomaly);

      switch (anomaly.type) {
        case 'uneven_distribution':
          // 재분배 트리거
          await this.triggerRebalancing();
          break;

        case 'high_error_rate':
          // 서킷 브레이커 활성화
          await this.activateCircuitBreaker(anomaly.targetId);
          break;

        case 'response_time_spike':
          // 백프레셔 적용
          await this.applyBackpressure(anomaly.targetId);
          break;
      }
    }
  }
}
```

**검증 기준**:
- [ ] 다양한 부하 분산 전략
- [ ] 적응형 및 ML 기반 라우팅
- [ ] 지역 인식 및 규정 준수
- [ ] 세션 친화성 및 모니터링

#### SubTask 5.9.2: 자동 스케일링 정책 엔진
**담당자**: DevOps 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:
```typescript
// backend/src/orchestration/autoscaling/scaling_engine.ts
export interface ScalingPolicy {
  id: string;
  name: string;
  type: ScalingPolicyType;
  triggers: ScalingTrigger[];
  actions: ScalingAction[];
  cooldown: number;
  enabled: boolean;
}

export class AutoScalingEngine {
  private policies: Map<string, ScalingPolicy>;
  private metricsEvaluator: MetricsEvaluator;
  private scaler: ResourceScaler;
  private policyEvaluator: PolicyEvaluator;
  private cooldownManager: CooldownManager;

  constructor(config: AutoScalingConfig) {
    this.policies = new Map();
    this.metricsEvaluator = new MetricsEvaluator(config.metrics);
    this.scaler = new ResourceScaler(config.scaling);
    this.policyEvaluator = new PolicyEvaluator();
    this.cooldownManager = new CooldownManager();
  }

  async evaluateAndScale(): Promise<ScalingResult> {
    const results: ScalingDecision[] = [];

    // 1. 현재 메트릭 수집
    const currentMetrics = await this.metricsEvaluator.collectMetrics();

    // 2. 각 정책 평가
    for (const policy of this.policies.values()) {
      if (!policy.enabled) continue;

      // 쿨다운 확인
      if (await this.cooldownManager.isInCooldown(policy.id)) {
        continue;
      }

      // 정책 평가
      const decision = await this.policyEvaluator.evaluate(
        policy,
        currentMetrics
      );

      if (decision.shouldScale) {
        results.push(decision);
      }
    }

    // 3. 충돌 해결
    const resolvedDecisions = await this.resolveConflicts(results);

    // 4. 스케일링 실행
    const scalingResults = await this.executeScaling(resolvedDecisions);

    // 5. 쿨다운 설정
    for (const result of scalingResults) {
      if (result.success) {
        await this.cooldownManager.setCooldown(
          result.policyId,
          result.policy.cooldown
        );
      }
    }

    return {
      decisions: resolvedDecisions,
      results: scalingResults,
      metrics: currentMetrics
    };
  }

  private async resolveConflicts(
    decisions: ScalingDecision[]
  ): Promise<ScalingDecision[]> {
    // 리소스별로 그룹화
    const resourceGroups = new Map<string, ScalingDecision[]>();

    for (const decision of decisions) {
      const resourceId = decision.targetResource;
      if (!resourceGroups.has(resourceId)) {
        resourceGroups.set(resourceId, []);
      }
      resourceGroups.get(resourceId)!.push(decision);
    }

    // 각 리소스별 최종 결정
    const resolved: ScalingDecision[] = [];

    for (const [resourceId, group] of resourceGroups) {
      if (group.length === 1) {
        resolved.push(group[0]);
      } else {
        // 충돌 해결: 가장 공격적인 스케일링 선택
        const winner = this.selectMostAggressiveScaling(group);
        resolved.push(winner);
      }
    }

    return resolved;
  }

  private selectMostAggressiveScaling(
    decisions: ScalingDecision[]
  ): ScalingDecision {
    // Scale out이 scale in보다 우선
    const scaleOutDecisions = decisions.filter(d => d.direction === 'out');
    if (scaleOutDecisions.length > 0) {
      // 가장 큰 증가량 선택
      return scaleOutDecisions.reduce((max, d) => 
        d.scalingAmount > max.scalingAmount ? d : max
      );
    }

    // Scale in 중 가장 작은 감소량 선택 (안전하게)
    return decisions.reduce((min, d) => 
      Math.abs(d.scalingAmount) < Math.abs(min.scalingAmount) ? d : min
    );
  }

  private async executeScaling(
    decisions: ScalingDecision[]
  ): Promise<ScalingExecutionResult[]> {
    const results: ScalingExecutionResult[] = [];

    for (const decision of decisions) {
      try {
        const result = await this.scaler.scale(decision);
        results.push({
          ...result,
          policyId: decision.policyId,
          policy: this.policies.get(decision.policyId)!
        });

        // 성공 이벤트
        await this.publishScalingEvent({
          type: 'scaling_success',
          decision,
          result
        });

      } catch (error) {
        results.push({
          success: false,
          policyId: decision.policyId,
          policy: this.policies.get(decision.policyId)!,
          error: error.message
        });

        // 실패 이벤트
        await this.publishScalingEvent({
          type: 'scaling_failed',
          decision,
          error
        });
      }
    }

    return results;
  }
}

// 메트릭 기반 스케일링 정책
export class MetricBasedScalingPolicy implements ScalingPolicy {
  id: string;
  name: string;
  type = ScalingPolicyType.METRIC_BASED;
  triggers: MetricTrigger[];
  actions: ScalingAction[];
  cooldown: number;
  enabled: boolean;

  async evaluate(metrics: SystemMetrics): Promise<boolean> {
    for (const trigger of this.triggers) {
      const metricValue = this.getMetricValue(metrics, trigger.metric);
      
      if (this.checkThreshold(metricValue, trigger)) {
        return true;
      }
    }

    return false;
  }

  private checkThreshold(value: number, trigger: MetricTrigger): boolean {
    switch (trigger.comparison) {
      case 'greater_than':
        return value > trigger.threshold;
      case 'less_than':
        return value < trigger.threshold;
      case 'greater_than_or_equal':
        return value >= trigger.threshold;
      case 'less_than_or_equal':
        return value <= trigger.threshold;
      default:
        return false;
    }
  }

  calculateScalingAmount(currentCapacity: number): number {
    const action = this.actions[0]; // 첫 번째 액션 사용

    switch (action.type) {
      case 'change_capacity':
        return action.value;
      case 'percent_change':
        return Math.ceil(currentCapacity * (action.value / 100));
      case 'exact_capacity':
        return action.value - currentCapacity;
      default:
        return 0;
    }
  }
}

// 예측 기반 스케일링
export class PredictiveScalingPolicy implements ScalingPolicy {
  id: string;
  name: string;
  type = ScalingPolicyType.PREDICTIVE;
  triggers: PredictiveTrigger[];
  actions: ScalingAction[];
  cooldown: number;
  enabled: boolean;

  private predictor: WorkloadPredictor;
  private confidenceThreshold: number = 0.8;

  constructor(config: PredictivePolicyConfig) {
    this.predictor = new WorkloadPredictor(config.model);
    this.confidenceThreshold = config.confidenceThreshold || 0.8;
  }

  async evaluate(metrics: SystemMetrics): Promise<ScalingDecision | null> {
    // 1. 워크로드 예측
    const prediction = await this.predictor.predict({
      historicalMetrics: metrics.history,
      timeHorizon: this.triggers[0].lookahead || 300 // 5분
    });

    // 2. 신뢰도 확인
    if (prediction.confidence < this.confidenceThreshold) {
      return null;
    }

    // 3. 예측된 수요와 현재 용량 비교
    const currentCapacity = metrics.current.capacity;
    const predictedDemand = prediction.expectedLoad;
    const buffer = 1.2; // 20% 버퍼

    if (predictedDemand * buffer > currentCapacity) {
      // Scale out 필요
      return {
        shouldScale: true,
        direction: 'out',
        scalingAmount: Math.ceil(predictedDemand * buffer - currentCapacity),
        reason: `Predicted demand (${predictedDemand}) exceeds capacity`,
        confidence: prediction.confidence
      };
    } else if (predictedDemand < currentCapacity * 0.4) {
      // Scale in 가능
      return {
        shouldScale: true,
        direction: 'in',
        scalingAmount: Math.floor(currentCapacity * 0.3),
        reason: `Predicted demand (${predictedDemand}) is low`,
        confidence: prediction.confidence
      };
    }

    return null;
  }
}

// 스케줄 기반 스케일링
export class ScheduleBasedScalingPolicy implements ScalingPolicy {
  id: string;
  name: string;
  type = ScalingPolicyType.SCHEDULED;
  triggers: ScheduleTrigger[];
  actions: ScalingAction[];
  cooldown: number;
  enabled: boolean;

  private scheduler: CronScheduler;

  constructor() {
    this.scheduler = new CronScheduler();
  }

  async initialize(): Promise<void> {
    for (const trigger of this.triggers) {
      await this.scheduler.schedule(
        trigger.cronExpression,
        async () => {
          await this.executeScheduledScaling(trigger);
        }
      );
    }
  }

  private async executeScheduledScaling(
    trigger: ScheduleTrigger
  ): Promise<void> {
    const action = this.actions.find(a => a.id === trigger.actionId);
    
    if (!action) {
      logger.error(`Action ${trigger.actionId} not found for trigger`);
      return;
    }

    // 스케일링 실행
    await this.scaler.scale({
      targetResource: trigger.targetResource,
      scalingAction: action,
      reason: `Scheduled scaling: ${trigger.description}`
    });
  }
}

// 복합 스케일링 정책
export class CompositeScalingPolicy implements ScalingPolicy {
  id: string;
  name: string;
  type = ScalingPolicyType.COMPOSITE;
  triggers: CompositeTrigger[];
  actions: ScalingAction[];
  cooldown: number;
  enabled: boolean;

  private subPolicies: ScalingPolicy[];
  private aggregationRule: AggregationRule;

  async evaluate(metrics: SystemMetrics): Promise<ScalingDecision | null> {
    const subDecisions: ScalingDecision[] = [];

    // 모든 하위 정책 평가
    for (const policy of this.subPolicies) {
      const decision = await policy.evaluate(metrics);
      if (decision) {
        subDecisions.push(decision);
      }
    }

    // 집계 규칙 적용
    return this.aggregate(subDecisions);
  }

  private aggregate(decisions: ScalingDecision[]): ScalingDecision | null {
    if (decisions.length === 0) return null;

    switch (this.aggregationRule) {
      case 'all':
        // 모든 정책이 동의해야 함
        if (decisions.length !== this.subPolicies.length) {
          return null;
        }
        break;

      case 'any':
        // 하나라도 트리거되면 실행
        if (decisions.length > 0) {
          return decisions[0];
        }
        break;

      case 'majority':
        // 과반수 동의
        if (decisions.length > this.subPolicies.length / 2) {
          return this.mergeDecisions(decisions);
        }
        break;
    }

    return null;
  }

  private mergeDecisions(decisions: ScalingDecision[]): ScalingDecision {
    // 평균값 사용
    const avgScaling = decisions.reduce((sum, d) => sum + d.scalingAmount, 0) / decisions.length;
    
    return {
      shouldScale: true,
      direction: avgScaling > 0 ? 'out' : 'in',
      scalingAmount: Math.round(avgScaling),
      reason: `Composite policy: ${decisions.length} sub-policies triggered`,
      confidence: decisions.reduce((sum, d) => sum + (d.confidence || 1), 0) / decisions.length
    };
  }
}

// 리소스 스케일러
export class ResourceScaler {
  private providers: Map<string, ScalingProvider>;
  private validator: ScalingValidator;
  private rollbackManager: RollbackManager;

  async scale(decision: ScalingDecision): Promise<ScalingResult> {
    // 1. 검증
    const validation = await this.validator.validate(decision);
    if (!validation.valid) {
      throw new ScalingValidationError(validation.errors);
    }

    // 2. 프로바이더 선택
    const provider = this.selectProvider(decision.targetResource);

    // 3. 스케일링 실행
    try {
      const result = await provider.scale({
        resourceId: decision.targetResource,
        direction: decision.direction,
        amount: decision.scalingAmount,
        metadata: decision.metadata
      });

      // 4. 헬스 체크
      await this.waitForHealthy(result.instances);

      return {
        success: true,
        scaledInstances: result.instances,
        previousCapacity: result.previousCapacity,
        newCapacity: result.newCapacity,
        duration: result.duration
      };

    } catch (error) {
      // 5. 롤백
      await this.rollbackManager.rollback(decision, error);
      throw error;
    }
  }

  private async waitForHealthy(
    instances: Instance[],
    timeout: number = 300000 // 5분
  ): Promise<void> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const healthChecks = await Promise.all(
        instances.map(i => this.checkHealth(i))
      );

      if (healthChecks.every(h => h.healthy)) {
        return;
      }

      await this.sleep(5000); // 5초 대기
    }

    throw new ScalingTimeoutError('Instances did not become healthy in time');
  }
}

// 스케일링 정책 최적화
export class ScalingPolicyOptimizer {
  private performanceAnalyzer: ScalingPerformanceAnalyzer;
  private costAnalyzer: ScalingCostAnalyzer;
  private mlOptimizer: MLPolicyOptimizer;

  async optimizePolicies(
    policies: ScalingPolicy[],
    historicalData: ScalingHistory
  ): Promise<OptimizedPolicies> {
    const optimizations: PolicyOptimization[] = [];

    for (const policy of policies) {
      // 1. 성능 분석
      const performance = await this.performanceAnalyzer.analyze(
        policy,
        historicalData
      );

      // 2. 비용 분석
      const cost = await this.costAnalyzer.analyze(
        policy,
        historicalData
      );

      // 3. ML 기반 최적화
      const mlSuggestions = await this.mlOptimizer.optimize(
        policy,
        performance,
        cost
      );

      optimizations.push({
        policyId: policy.id,
        currentPerformance: performance,
        currentCost: cost,
        suggestions: mlSuggestions,
        estimatedImprovement: this.calculateImprovement(
          performance,
          cost,
          mlSuggestions
        )
      });
    }

    return {
      optimizations,
      recommendations: this.generateRecommendations(optimizations)
    };
  }

  private generateRecommendations(
    optimizations: PolicyOptimization[]
  ): PolicyRecommendation[] {
    const recommendations: PolicyRecommendation[] = [];

    for (const opt of optimizations) {
      // 임계값 조정 추천
      if (opt.currentPerformance.falsePositiveRate > 0.3) {
        recommendations.push({
          policyId: opt.policyId,
          type: 'adjust_threshold',
          description: 'Increase threshold to reduce false positives',
          impact: 'high',
          implementation: {
            threshold: opt.suggestions.optimalThreshold
          }
        });
      }

      // 쿨다운 조정 추천
      if (opt.currentPerformance.thrashing > 0.2) {
        recommendations.push({
          policyId: opt.policyId,
          type: 'increase_cooldown',
          description: 'Increase cooldown to prevent thrashing',
          impact: 'medium',
          implementation: {
            cooldown: opt.suggestions.optimalCooldown
          }
        });
      }

      // 예측 모델 추가 추천
      if (opt.currentPerformance.reactionTime > 180) { // 3분 이상
        recommendations.push({
          policyId: opt.policyId,
          type: 'add_predictive',
          description: 'Add predictive scaling to improve reaction time',
          impact: 'high',
          implementation: {
            model: 'arima',
            lookahead: 300
          }
        });
      }
    }

    return recommendations;
  }
}

// 다중 클라우드 스케일링
export class MultiCloudScaler {
  private cloudProviders: Map<string, CloudProvider>;
  private costOptimizer: MultiCloudCostOptimizer;
  private loadDistributor: MultiCloudLoadDistributor;

  async scaleAcrossClouds(
    demand: number,
    constraints: MultiCloudConstraints
  ): Promise<MultiCloudScalingResult> {
    // 1. 각 클라우드의 현재 상태 확인
    const cloudStates = await this.getCloudStates();

    // 2. 비용 최적화 분석
    const costAnalysis = await this.costOptimizer.analyze(
      demand,
      cloudStates,
      constraints
    );

    // 3. 최적 분배 계산
    const distribution = await this.loadDistributor.calculate(
      demand,
      cloudStates,
      costAnalysis,
      constraints
    );

    // 4. 각 클라우드에서 스케일링 실행
    const results = await this.executeMultiCloudScaling(distribution);

    return {
      distribution,
      results,
      totalCost: this.calculateTotalCost(results),
      estimatedSavings: costAnalysis.savings
    };
  }

  private async executeMultiCloudScaling(
    distribution: CloudDistribution
  ): Promise<CloudScalingResult[]> {
    const tasks = [];

    for (const [cloudId, allocation] of distribution.allocations) {
      const provider = this.cloudProviders.get(cloudId);
      
      if (!provider) continue;

      tasks.push(
        provider.scale({
          targetCapacity: allocation.capacity,
          instanceType: allocation.instanceType,
          region: allocation.region
        })
      );
    }

    return Promise.all(tasks);
  }
}

// 스케일링 이벤트 핸들러
export class ScalingEventHandler {
  private eventBus: EventBus;
  private notificationService: NotificationService;
  private auditLogger: AuditLogger;

  async handleScalingEvent(event: ScalingEvent): Promise<void> {
    // 1. 감사 로깅
    await this.auditLogger.log({
      type: 'scaling_event',
      event,
      timestamp: new Date(),
      user: event.triggeredBy || 'system'
    });

    // 2. 알림 발송
    if (this.shouldNotify(event)) {
      await this.notificationService.send({
        type: 'scaling',
        severity: this.getSeverity(event),
        message: this.formatMessage(event),
        recipients: await this.getRecipients(event)
      });
    }

    // 3. 메트릭 업데이트
    await this.updateMetrics(event);

    // 4. 후속 액션 트리거
    if (event.type === 'scaling_failed') {
      await this.handleScalingFailure(event);
    }
  }

  private shouldNotify(event: ScalingEvent): boolean {
    // 중요 이벤트만 알림
    return event.type === 'scaling_failed' ||
           event.type === 'scaling_completed' && event.scalingAmount > 10 ||
           event.type === 'cost_threshold_exceeded';
  }

  private async handleScalingFailure(event: ScalingEvent): Promise<void> {
    // 재시도 정책 확인
    const policy = await this.getRetryPolicy(event.policyId);
    
    if (policy && event.attemptNumber < policy.maxRetries) {
      // 재시도 스케줄링
      setTimeout(() => {
        this.retryScaling(event);
      }, policy.retryDelay * Math.pow(2, event.attemptNumber)); // 지수 백오프
    } else {
      // 최종 실패 처리
      await this.handleFinalFailure(event);
    }
  }
}
```

**검증 기준**:
- [ ] 다양한 스케일링 정책 구현
- [ ] 예측 기반 스케일링
- [ ] 정책 충돌 해결
- [ ] 다중 클라우드 지원

#### SubTask 5.9.3: 리소스 예측 및 사전 프로비저닝
**담당자**: ML 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/autoscaling/resource_prediction.ts
export class ResourcePredictor {
  private timeSeriesAnalyzer: TimeSeriesAnalyzer;
  private patternRecognizer: PatternRecognizer;
  private anomalyDetector: AnomalyDetector;
  private mlModels: Map<string, PredictionModel>;

  constructor(config: PredictorConfig) {
    this.timeSeriesAnalyzer = new TimeSeriesAnalyzer();
    this.patternRecognizer = new PatternRecognizer();
    this.anomalyDetector = new AnomalyDetector();
    this.mlModels = this.initializeModels(config);
  }

  async predictResourceDemand(
    historicalData: ResourceUsageHistory,
    horizon: TimeHorizon
  ): Promise<ResourceDemandForecast> {
    // 1. 데이터 전처리
    const preprocessed = await this.preprocessData(historicalData);

    // 2. 패턴 인식
    const patterns = await this.patternRecognizer.identify(preprocessed);

    // 3. 시계열 분석
    const timeSeriesAnalysis = await this.timeSeriesAnalyzer.analyze(
      preprocessed,
      {
        seasonality: patterns.seasonality,
        trend: patterns.trend,
        cyclic: patterns.cyclic
      }
    );

    // 4. ML 예측
    const predictions = await this.generatePredictions(
      preprocessed,
      timeSeriesAnalysis,
      horizon
    );

    // 5. 이상치 보정
    const corrected = await this.correctForAnomalies(predictions);

    // 6. 신뢰 구간 계산
    const confidence = await this.calculateConfidenceIntervals(corrected);

    return {
      predictions: corrected,
      confidence,
      patterns,
      recommendations: await this.generateRecommendations(corrected)
    };
  }

  private async generatePredictions(
    data: ProcessedData,
    analysis: TimeSeriesAnalysis,
    horizon: TimeHorizon
  ): Promise<ResourcePrediction[]> {
    const predictions: ResourcePrediction[] = [];

    // 각 리소스 타입별 예측
    for (const resourceType of ['cpu', 'memory', 'disk', 'network']) {
      const model = this.mlModels.get(resourceType)!;
      
      // 특징 추출
      const features = await this.extractFeatures(data, analysis, resourceType);
      
      // 모델 예측
      const forecast = await model.predict(features, horizon);
      
      predictions.push({
        resourceType,
        timeSeries: forecast.values,
        peaks: await this.identifyPeaks(forecast),
        valleys: await this.identifyValleys(forecast)
      });
    }

    return predictions;
  }

  private async extractFeatures(
    data: ProcessedData,
    analysis: TimeSeriesAnalysis,
    resourceType: string
  ): Promise<FeatureVector> {
    return {
      // 시계열 특징
      mean: data.statistics[resourceType].mean,
      std: data.statistics[resourceType].std,
      trend: analysis.trend.coefficient,
      seasonalityStrength: analysis.seasonality.strength,
      
      // 시간 특징
      hourOfDay: new Date().getHours(),
      dayOfWeek: new Date().getDay(),
      dayOfMonth: new Date().getDate(),
      isWeekend: [0, 6].includes(new Date().getDay()),
      
      // 이벤트 특징
      upcomingEvents: await this.getUpcomingEvents(),
      
      // 외부 요인
      weather: await this.getWeatherForecast(),
      holidays: await this.getHolidayCalendar()
    };
  }
}

// 사전 프로비저닝 관리자
export class ProactiveProvisioner {
  private predictor: ResourcePredictor;
  private provisioner: ResourceProvisioner;
  private costCalculator: CostCalculator;
  private riskAssessor: RiskAssessor;

  async planProvisioning(
    currentState: ResourceState,
    constraints: ProvisioningConstraints
  ): Promise<ProvisioningPlan> {
    // 1. 수요 예측
    const forecast = await this.predictor.predictResourceDemand(
      currentState.history,
      { start: new Date(), end: this.addHours(new Date(), 24) }
    );

    // 2. 프로비저닝 전략 수립
    const strategies = await this.generateStrategies(
      forecast,
      currentState,
      constraints
    );

    // 3. 각 전략 평가
    const evaluations = await Promise.all(
      strategies.map(s => this.evaluateStrategy(s, forecast))
    );

    // 4. 최적 전략 선택
    const optimal = this.selectOptimalStrategy(evaluations, constraints);

    // 5. 실행 계획 생성
    return this.createExecutionPlan(optimal);
  }

  private async generateStrategies(
    forecast: ResourceDemandForecast,
    currentState: ResourceState,
    constraints: ProvisioningConstraints
  ): Promise<ProvisioningStrategy[]> {
    const strategies: ProvisioningStrategy[] = [];

    // 1. 보수적 전략 (최소 비용)
    strategies.push({
      name: 'conservative',
      description: 'Provision for average demand with small buffer',
      provisions: this.calculateConservativeProvisions(forecast),
      riskLevel: 'medium'
    });

    // 2. 공격적 전략 (최고 성능)
    strategies.push({
      name: 'aggressive',
      description: 'Provision for peak demand with large buffer',
      provisions: this.calculateAggressiveProvisions(forecast),
      riskLevel: 'low'
    });

    // 3. 적응형 전략 (동적 조정)
    strategies.push({
      name: 'adaptive',
      description: 'Dynamic provisioning based on real-time metrics',
      provisions: this.calculateAdaptiveProvisions(forecast),
      riskLevel: 'low-medium'
    });

    // 4. 비용 최적화 전략
    strategies.push({
      name: 'cost-optimized',
      description: 'Balance between cost and performance',
      provisions: await this.calculateCostOptimizedProvisions(
        forecast,
        constraints.budget
      ),
      riskLevel: 'medium'
    });

    return strategies;
  }

  private async evaluateStrategy(
    strategy: ProvisioningStrategy,
    forecast: ResourceDemandForecast
  ): Promise<StrategyEvaluation> {
    // 비용 계산
    const cost = await this.costCalculator.calculate(strategy.provisions);

    // 위험 평가
    const risk = await this.riskAssessor.assess(
      strategy,
      forecast
    );

    // 성능 시뮬레이션
    const performance = await this.simulatePerformance(
      strategy,
      forecast
    );

    return {
      strategy,
      cost,
      risk,
      performance,
      score: this.calculateScore(cost, risk, performance)
    };
  }

  private calculateScore(
    cost: CostEstimate,
    risk: RiskAssessment,
    performance: PerformanceMetrics
  ): number {
    // 가중 점수 계산
    const costScore = 1 / (1 + cost.total / 10000); // 정규화
    const riskScore = 1 - risk.overallRisk;
    const performanceScore = performance.slaCompliance;

    return (
      costScore * 0.3 +
      riskScore * 0.3 +
      performanceScore * 0.4
    );
  }
}

// 예측 모델 앙상블
export class PredictionModelEnsemble {
  private models: PredictionModel[];
  private weights: number[];
  private performanceTracker: ModelPerformanceTracker;

  constructor() {
    this.models = [
      new ARIMAModel(),
      new LSTMModel(),
      new ProphetModel(),
      new XGBoostModel(),
      new ExponentialSmoothingModel()
    ];
    
    this.weights = new Array(this.models.length).fill(1 / this.models.length);
    this.performanceTracker = new ModelPerformanceTracker();
  }

  async predict(
    data: TimeSeriesData,
    horizon: number
  ): Promise<EnsemblePrediction> {
    // 1. 각 모델 예측
    const predictions = await Promise.all(
      this.models.map(model => model.predict(data, horizon))
    );

    // 2. 가중 평균
    const ensemble = this.weightedAverage(predictions, this.weights);

    // 3. 불확실성 계산
    const uncertainty = this.calculateUncertainty(predictions);

    // 4. 개별 모델 기여도
    const contributions = this.calculateContributions(predictions, ensemble);

    return {
      forecast: ensemble,
      uncertainty,
      contributions,
      confidence: this.calculateConfidence(predictions)
    };
  }

  private weightedAverage(
    predictions: Prediction[],
    weights: number[]
  ): number[] {
    const length = predictions[0].values.length;
    const result = new Array(length).fill(0);

    for (let t = 0; t < length; t++) {
      for (let i = 0; i < predictions.length; i++) {
        result[t] += predictions[i].values[t] * weights[i];
      }
    }

    return result;
  }

  async updateWeights(
    actualValues: number[]
  ): Promise<void> {
    // 각 모델의 성능 평가
    const performances = await Promise.all(
      this.models.map((model, index) => 
        this.performanceTracker.evaluate(model, actualValues)
      )
    );

    // 성능 기반 가중치 업데이트
    const totalPerformance = performances.reduce((sum, p) => sum + p.score, 0);
    
    this.weights = performances.map(p => p.score / totalPerformance);
  }
}

// 시계열 분해
export class TimeSeriesDecomposer {
  async decompose(
    data: TimeSeriesData
  ): Promise<TimeSeriesComponents> {
    // STL 분해 (Seasonal and Trend decomposition using Loess)
    const stl = new STLDecomposition({
      seasonal: 'periodic',
      trend: 'loess',
      robust: true
    });

    const components = await stl.fit(data);

    return {
      trend: components.trend,
      seasonal: components.seasonal,
      residual: components.residual,
      
      // 추가 분석
      seasonalPeriod: await this.detectSeasonalPeriod(data),
      trendStrength: this.calculateTrendStrength(components.trend),
      seasonalStrength: this.calculateSeasonalStrength(components.seasonal),
      noise: this.calculateNoise(components.residual)
    };
  }

  private async detectSeasonalPeriod(
    data: TimeSeriesData
  ): Promise<number> {
    // FFT를 사용한 주기 감지
    const fft = new FastFourierTransform();
    const spectrum = fft.forward(data.values);
    
    // 주요 주파수 찾기
    const peaks = this.findSpectralPeaks(spectrum);
    
    if (peaks.length === 0) {
      return 0; // 계절성 없음
    }

    // 가장 강한 주기 반환
    return Math.round(data.values.length / peaks[0].frequency);
  }
}

// 이상치 감지 및 보정
export class AnomalyDetectorAndCorrector {
  private detectors: AnomalyDetector[];
  
  constructor() {
    this.detectors = [
      new IsolationForestDetector(),
      new LocalOutlierFactorDetector(),
      new OneClassSVMDetector(),
      new AutoencoderDetector()
    ];
  }

  async detectAndCorrect(
    data: TimeSeriesData
  ): Promise<CorrectedData> {
    // 1. 다중 감지기로 이상치 감지
    const detections = await Promise.all(
      this.detectors.map(d => d.detect(data))
    );

    // 2. 합의 기반 이상치 결정
    const anomalies = this.consensusAnomalies(detections);

    // 3. 이상치 보정
    const corrected = await this.correctAnomalies(data, anomalies);

    return {
      data: corrected,
      anomalies,
      corrections: this.generateCorrections(data, corrected, anomalies)
    };
  }

  private consensusAnomalies(
    detections: AnomalyDetection[]
  ): number[] {
    const threshold = Math.ceil(detections.length * 0.6); // 60% 동의
    const anomalyCounts = new Map<number, number>();

    // 각 포인트별 감지 횟수 계산
    for (const detection of detections) {
      for (const index of detection.anomalyIndices) {
        const count = anomalyCounts.get(index) || 0;
        anomalyCounts.set(index, count + 1);
      }
    }

    // 임계값 이상인 포인트만 선택
    return Array.from(anomalyCounts.entries())
      .filter(([_, count]) => count >= threshold)
      .map(([index, _]) => index);
  }

  private async correctAnomalies(
    data: TimeSeriesData,
    anomalies: number[]
  ): Promise<TimeSeriesData> {
    const corrected = { ...data, values: [...data.values] };

    for (const index of anomalies) {
      // 주변 값들의 가중 평균으로 대체
      const window = 5;
      const start = Math.max(0, index - window);
      const end = Math.min(data.values.length - 1, index + window);
      
      let sum = 0;
      let weightSum = 0;
      
      for (let i = start; i <= end; i++) {
        if (!anomalies.includes(i)) {
          const weight = 1 / (1 + Math.abs(i - index));
          sum += data.values[i] * weight;
          weightSum += weight;
        }
      }
      
      if (weightSum > 0) {
        corrected.values[index] = sum / weightSum;
      }
    }

    return corrected;
  }
}

// 용량 계획 최적화
export class CapacityPlanningOptimizer {
  private scenarioGenerator: ScenarioGenerator;
  private simulator: CapacitySimulator;
  private optimizer: ConstrainedOptimizer;

  async optimizeCapacityPlan(
    forecast: ResourceDemandForecast,
    constraints: CapacityConstraints
  ): Promise<OptimalCapacityPlan> {
    // 1. 시나리오 생성
    const scenarios = await this.scenarioGenerator.generate(forecast);

    // 2. 각 시나리오 시뮬레이션
    const simulations = await Promise.all(
      scenarios.map(s => this.simulator.simulate(s, constraints))
    );

    // 3. 최적화 문제 정의
    const problem = this.formulateOptimizationProblem(
      simulations,
      constraints
    );

    // 4. 최적해 찾기
    const solution = await this.optimizer.solve(problem);

    // 5. 실행 가능한 계획 생성
    return this.createExecutablePlan(solution, constraints);
  }

  private formulateOptimizationProblem(
    simulations: SimulationResult[],
    constraints: CapacityConstraints
  ): OptimizationProblem {
    return {
      objective: {
        // 비용 최소화 + SLA 위반 페널티
        minimize: (x: number[]) => {
          let cost = 0;
          let penalty = 0;
          
          for (let i = 0; i < simulations.length; i++) {
            cost += x[i] * simulations[i].cost;
            penalty += (1 - simulations[i].slaCompliance) * 10000;
          }
          
          return cost + penalty;
        }
      },
      
      constraints: [
        // 예산 제약
        {
          type: 'inequality',
          function: (x: number[]) => {
            const totalCost = x.reduce((sum, xi, i) => 
              sum + xi * simulations[i].cost, 0
            );
            return constraints.budget - totalCost; // >= 0
          }
        },
        
        // 최소 가용성 제약
        {
          type: 'inequality',
          function: (x: number[]) => {
            const availability = this.calculateAvailability(x, simulations);
            return availability - constraints.minAvailability; // >= 0
          }
        }
      ],
      
      bounds: simulations.map(s => ({
        min: s.minCapacity,
        max: s.maxCapacity
      }))
    };
  }
}

// 실시간 조정 시스템
export class RealtimeAdjuster {
  private monitor: ResourceMonitor;
  private adjuster: DynamicAdjuster;
  private feedbackLoop: FeedbackController;

  async startRealtimeAdjustment(): Promise<void> {
    // 모니터링 루프
    setInterval(async () => {
      // 현재 상태 확인
      const currentState = await this.monitor.getCurrentState();
      
      // 예측과 실제 비교
      const deviation = await this.calculateDeviation(currentState);
      
      // 조정 필요 여부 판단
      if (this.needsAdjustment(deviation)) {
        await this.performAdjustment(currentState, deviation);
      }
      
      // 피드백 수집
      await this.feedbackLoop.collect(currentState, deviation);
      
    }, 30000); // 30초마다
  }

  private async performAdjustment(
    state: ResourceState,
    deviation: Deviation
  ): Promise<void> {
    // 조정 계획 수립
    const adjustmentPlan = await this.adjuster.plan(state, deviation);
    
    // 점진적 조정
    for (const step of adjustmentPlan.steps) {
      await this.executeAdjustmentStep(step);
      
      // 효과 확인
      await this.waitAndVerify(step.expectedDuration);
      
      // 조기 종료 조건
      if (await this.isAdjustmentSufficient()) {
        break;
      }
    }
  }

  private async waitAndVerify(duration: number): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, duration));
    
    const newState = await this.monitor.getCurrentState();
    const improvement = this.calculateImprovement(newState);
    
    if (improvement < 0) {
      // 역효과 발생 - 롤백
      throw new AdjustmentFailureError('Adjustment had negative effect');
    }
  }
}
```

**검증 기준**:
- [ ] 시계열 예측 모델
- [ ] 사전 프로비저닝 전략
- [ ] 이상치 감지 및 보정
- [ ] 실시간 조정 시스템

#### SubTask 5.9.4: 멀티 리전 분산 처리
**담당자**: 분산 시스템 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:
```typescript
// backend/src/orchestration/multiregion/distributed_processing.ts
export class MultiRegionOrchestrator {
  private regions: Map<string, RegionController>;
  private globalCoordinator: GlobalCoordinator;
  private dataReplicator: DataReplicator;
  private latencyOptimizer: LatencyOptimizer;

  constructor(config: MultiRegionConfig) {
    this.regions = this.initializeRegions(config.regions);
    this.globalCoordinator = new GlobalCoordinator();
    this.dataReplicator = new DataReplicator(config.replication);
    this.latencyOptimizer = new LatencyOptimizer();
  }

  async distributeWorkload(
    workload: Workload,
    constraints: DistributionConstraints
  ): Promise<DistributionPlan> {
    // 1. 워크로드 분석
    const analysis = await this.analyzeWorkload(workload);

    // 2. 지역별 상태 확인
    const regionStates = await this.getRegionStates();

    // 3. 최적 분배 계획
    const distribution = await this.latencyOptimizer.optimize({
      workload: analysis,
      regions: regionStates,
      constraints
    });

    // 4. 데이터 복제 계획
    const replicationPlan = await this.dataReplicator.plan(
      distribution,
      analysis.dataRequirements
    );

    // 5. 실행 계획 생성
    return {
      distribution,
      replication: replicationPlan,
      estimatedLatency: distribution.expectedLatency,
      estimatedCost: await this.calculateCost(distribution)
    };
  }

  private async analyzeWorkload(
    workload: Workload
  ): Promise<WorkloadAnalysis> {
    return {
      type: this.classifyWorkload(workload),
      dataRequirements: await this.analyzeDataRequirements(workload),
      computeRequirements: this.estimateComputeRequirements(workload),
      latencySensitivity: this.assessLatencySensitivity(workload),
      regionAffinity: await this.determineRegionAffinity(workload)
    };
  }

  async executeDistributed(
    plan: DistributionPlan
  ): Promise<DistributedExecutionResult> {
    // 1. 데이터 복제 실행
    await this.executeReplication(plan.replication);

    // 2. 지역별 태스크 배포
    const deployments = await this.deployToRegions(plan.distribution);

    // 3. 글로벌 조정 시작
    const coordination = await this.globalCoordinator.coordinate(
      deployments
    );

    // 4. 실행 모니터링
    const monitor = new DistributedExecutionMonitor(deployments);
    
    return {
      deployments,
      coordination,
      monitor
    };
  }
}

// 글로벌 조정자
export class GlobalCoordinator {
  private consensusProtocol: ConsensusProtocol;
  private stateManager: GlobalStateManager;
  private conflictResolver: ConflictResolver;

  async coordinate(
    deployments: RegionDeployment[]
  ): Promise<CoordinationHandle> {
    // 1. 글로벌 상태 초기화
    await this.stateManager.initialize(deployments);

    // 2. 합의 프로토콜 시작
    await this.consensusProtocol.establish(
      deployments.map(d => d.region)
    );

    // 3. 조정 핸들 생성
    const handle = new CoordinationHandle({
      deployments,
      stateManager: this.stateManager,
      conflictResolver: this.conflictResolver
    });

    // 4. 이벤트 리스너 설정
    this.setupEventListeners(handle);

    return handle;
  }

  private setupEventListeners(handle: CoordinationHandle): void {
    // 상태 변경 감지
    handle.on('stateChange', async (change) => {
      await this.handleStateChange(change);
    });

    // 충돌 감지
    handle.on('conflict', async (conflict) => {
      await this.resolveConflict(conflict);
    });

    // 장애 감지
    handle.on('regionFailure', async (failure) => {
      await this.handleRegionFailure(failure);
    });
  }

  private async handleStateChange(
    change: StateChange
  ): Promise<void> {
    // 1. 변경 사항 검증
    const validation = await this.validateStateChange(change);
    
    if (!validation.valid) {
      throw new InvalidStateChangeError(validation.errors);
    }

    // 2. 글로벌 상태 업데이트
    await this.stateManager.applyChange(change);

    // 3. 다른 지역에 전파
    await this.propagateChange(change);
  }

  private async resolveConflict(
    conflict: StateConflict
  ): Promise<Resolution> {
    // 충돌 해결 전략 선택
    const strategy = this.selectResolutionStrategy(conflict);

    switch (strategy) {
      case 'last-write-wins':
        return this.lastWriteWins(conflict);
      
      case 'vector-clock':
        return this.vectorClockResolution(conflict);
      
      case 'crdt':
        return this.crdtMerge(conflict);
      
      case 'consensus':
        return this.consensusResolution(conflict);
      
      default:
        throw new Error(`Unknown resolution strategy: ${strategy}`);
    }
  }
}

// 지역 간 데이터 복제
export class DataReplicator {
  private replicationStrategies: Map<string, ReplicationStrategy>;
  private consistencyManager: ConsistencyManager;
  private bandwidthOptimizer: BandwidthOptimizer;

  async plan(
    distribution: Distribution,
    dataRequirements: DataRequirement[]
  ): Promise<ReplicationPlan> {
    const plan: ReplicationPlan = {
      replications: [],
      estimatedTime: 0,
      estimatedCost: 0,
      consistencyLevel: 'eventual'
    };

    for (const requirement of dataRequirements) {
      // 1. 소스 지역 확인
      const sourceRegion = await this.findDataSource(requirement.dataId);

      // 2. 타겟 지역 결정
      const targetRegions = this.determineTargetRegions(
        requirement,
        distribution
      );

      // 3. 복제 전략 선택
      const strategy = this.selectStrategy(requirement, targetRegions);

      // 4. 복제 계획 추가
      plan.replications.push({
        dataId: requirement.dataId,
        source: sourceRegion,
        targets: targetRegions,
        strategy,
        priority: requirement.priority || 'normal',
        consistencyRequirement: requirement.consistency || 'eventual'
      });
    }

    // 5. 최적화
    await this.optimizeReplicationPlan(plan);

    return plan;
  }

  private async optimizeReplicationPlan(
    plan: ReplicationPlan
  ): Promise<void> {
    // 대역폭 최적화
    const optimized = await this.bandwidthOptimizer.optimize(
      plan.replications
    );

    // 우선순위 기반 스케줄링
    plan.replications = this.scheduleReplications(optimized);

    // 시간 및 비용 추정
    plan.estimatedTime = await this.estimateReplicationTime(plan.replications);
    plan.estimatedCost = await this.estimateReplicationCost(plan.replications);
  }

  async execute(
    plan: ReplicationPlan
  ): Promise<ReplicationResult> {
    const results: ReplicationTaskResult[] = [];

    // 병렬 복제 그룹 생성
    const groups = this.createParallelGroups(plan.replications);

    for (const group of groups) {
      // 그룹 내 병렬 실행
      const groupResults = await Promise.all(
        group.map(rep => this.executeReplication(rep))
      );
      
      results.push(...groupResults);

      // 일관성 체크포인트
      await this.consistencyManager.checkpoint(groupResults);
    }

    return {
      success: results.every(r => r.success),
      results,
      consistencyReport: await this.consistencyManager.report()
    };
  }

  private async executeReplication(
    replication: ReplicationTask
  ): Promise<ReplicationTaskResult> {
    const startTime = Date.now();

    try {
      // 1. 데이터 읽기
      const data = await this.readData(
        replication.source,
        replication.dataId
      );

      // 2. 압축 (선택적)
      const compressed = await this.compressIfBeneficial(data);

      // 3. 전송
      const transfers = await Promise.all(
        replication.targets.map(target =>
          this.transferData(compressed, replication.source, target)
        )
      );

      // 4. 검증
      await this.verifyReplications(transfers);

      return {
        success: true,
        replicationId: replication.id,
        duration: Date.now() - startTime,
        bytesTransferred: compressed.size * replication.targets.length
      };

    } catch (error) {
      return {
        success: false,
        replicationId: replication.id,
        error: error.message,
        duration: Date.now() - startTime
      };
    }
  }
}

// 지연 시간 최적화
export class LatencyOptimizer {
  private latencyPredictor: LatencyPredictor;
  private routingOptimizer: RoutingOptimizer;
  private cacheManager: GeoCacheManager;

  async optimize(
    params: LatencyOptimizationParams
  ): Promise<OptimizedDistribution> {
    // 1. 지연 시간 예측 매트릭스 생성
    const latencyMatrix = await this.createLatencyMatrix(params.regions);

    // 2. 작업 배치 최적화
    const placement = await this.optimizePlacement(
      params.workload,
      latencyMatrix,
      params.constraints
    );

    // 3. 라우팅 최적화
    const routing = await this.routingOptimizer.optimize(
      placement,
      latencyMatrix
    );

    // 4. 캐시 전략
    const cacheStrategy = await this.cacheManager.optimize(
      placement,
      params.workload.accessPatterns
    );

    return {
      placement,
      routing,
      cacheStrategy,
      expectedLatency: this.calculateExpectedLatency(
        placement,
        routing,
        latencyMatrix
      )
    };
  }

  private async createLatencyMatrix(
    regions: Region[]
  ): Promise<LatencyMatrix> {
    const matrix: number[][] = [];

    for (let i = 0; i < regions.length; i++) {
      matrix[i] = [];
      for (let j = 0; j < regions.length; j++) {
        if (i === j) {
          matrix[i][j] = 0;
        } else {
          matrix[i][j] = await this.latencyPredictor.predict(
            regions[i],
            regions[j]
          );
        }
      }
    }

    return new LatencyMatrix(matrix, regions);
  }

  private async optimizePlacement(
    workload: WorkloadAnalysis,
    latencyMatrix: LatencyMatrix,
    constraints: DistributionConstraints
  ): Promise<Placement> {
    // ILP (Integer Linear Programming) 문제로 변환
    const problem = this.formulatePlacementProblem(
      workload,
      latencyMatrix,
      constraints
    );

    // 솔버 실행
    const solution = await this.solvePlacement(problem);

    return this.solutionToPlacement(solution, workload);
  }
}

// 장애 복구 관리자
export class MultiRegionFailoverManager {
  private healthMonitor: RegionHealthMonitor;
  private failoverCoordinator: FailoverCoordinator;
  private stateReplicator: StateReplicator;

  async handleRegionFailure(
    failedRegion: string
  ): Promise<FailoverResult> {
    logger.error(`Region failure detected: ${failedRegion}`);

    // 1. 영향 범위 평가
    const impact = await this.assessImpact(failedRegion);

    // 2. 대체 지역 선택
    const alternateRegions = await this.selectAlternateRegions(
      failedRegion,
      impact
    );

    // 3. 상태 복구
    const stateRecovery = await this.recoverState(
      failedRegion,
      alternateRegions
    );

    // 4. 트래픽 리라우팅
    const rerouting = await this.rerouteTraffic(
      failedRegion,
      alternateRegions
    );

    // 5. 서비스 재시작
    const serviceRestoration = await this.restoreServices(
      impact.affectedServices,
      alternateRegions
    );

    return {
      failedRegion,
      alternateRegions,
      recoveredState: stateRecovery,
      reroutedTraffic: rerouting,
      restoredServices: serviceRestoration,
      totalDowntime: this.calculateDowntime(impact)
    };
  }

  private async selectAlternateRegions(
    failedRegion: string,
    impact: ImpactAssessment
  ): Promise<string[]> {
    const candidates = await this.getHealthyRegions();
    const scored: ScoredRegion[] = [];

    for (const candidate of candidates) {
      const score = await this.scoreRegion(candidate, {
        capacity: await this.getAvailableCapacity(candidate),
        latency: await this.getLatencyFrom(failedRegion, candidate),
        dataLocality: await this.getDataLocality(candidate, impact),
        cost: await this.getRegionCost(candidate)
      });

      scored.push({ region: candidate, score });
    }

    // 점수 기준 정렬 및 선택
    scored.sort((a, b) => b.score - a.score);
    
    const selected = [];
    let remainingLoad = impact.totalLoad;

    for (const { region } of scored) {
      const capacity = await this.getAvailableCapacity(region);
      selected.push(region);
      remainingLoad -= capacity;

      if (remainingLoad <= 0) break;
    }

    return selected;
  }

  private async recoverState(
    failedRegion: string,
    alternateRegions: string[]
  ): Promise<StateRecoveryResult> {
    // 1. 최신 상태 스냅샷 찾기
    const snapshot = await this.findLatestSnapshot(failedRegion);

    // 2. 델타 변경 사항 수집
    const deltas = await this.collectDeltas(
      failedRegion,
      snapshot.timestamp
    );

    // 3. 상태 재구성
    const reconstructed = await this.reconstructState(snapshot, deltas);

    // 4. 대체 지역에 배포
    const deployments = await Promise.all(
      alternateRegions.map(region =>
        this.deployState(reconstructed, region)
      )
    );

    return {
      snapshot,
      deltasApplied: deltas.length,
      deployments,
      dataLoss: this.assessDataLoss(snapshot, deltas)
    };
  }
}

// 지역 간 일관성 관리
export class CrossRegionConsistencyManager {
  private vectorClockManager: VectorClockManager;
  private conflictDetector: ConflictDetector;
  private reconciler: StateReconciler;

  async ensureConsistency(
    regions: string[]
  ): Promise<ConsistencyReport> {
    // 1. 각 지역의 벡터 클럭 수집
    const clocks = await this.collectVectorClocks(regions);

    // 2. 일관성 검사
    const inconsistencies = await this.detectInconsistencies(clocks);

    // 3. 충돌 감지
    const conflicts = await this.conflictDetector.detect(inconsistencies);

    // 4. 조정 실행
    const reconciliations = await this.reconcile(conflicts);

    return {
      regions,
      consistencyLevel: this.calculateConsistencyLevel(inconsistencies),
      conflicts: conflicts.length,
      reconciled: reconciliations.length,
      timestamp: new Date()
    };
  }

  private async reconcile(
    conflicts: Conflict[]
  ): Promise<Reconciliation[]> {
    const reconciliations: Reconciliation[] = [];

    for (const conflict of conflicts) {
      const strategy = this.selectReconciliationStrategy(conflict);
      const result = await this.reconciler.reconcile(conflict, strategy);
      
      reconciliations.push(result);

      // 조정 결과 전파
      await this.propagateReconciliation(result);
    }

    return reconciliations;
  }

  private selectReconciliationStrategy(
    conflict: Conflict
  ): ReconciliationStrategy {
    // 충돌 유형에 따른 전략 선택
    switch (conflict.type) {
      case 'write-write':
        return conflict.dataType === 'counter' 
          ? 'crdt-merge' 
          : 'last-write-wins';
      
      case 'write-delete':
        return 'resurrection';
      
      case 'ordering':
        return 'causal-ordering';
      
      default:
        return 'manual-resolution';
    }
  }
}

// 성능 모니터링 대시보드
export class MultiRegionPerformanceDashboard {
  private metricsCollector: GlobalMetricsCollector;
  private visualizer: MetricsVisualizer;
  private alertSystem: GlobalAlertSystem;

  async initialize(): Promise<void> {
    // 실시간 메트릭 스트림 설정
    await this.setupMetricStreams();

    // 대시보드 UI 초기화
    await this.initializeDashboard();

    // 알림 규칙 설정
    await this.configureAlerts();
  }

  private async setupMetricStreams(): Promise<void> {
    // 각 지역별 메트릭 스트림
    const regions = await this.getAllRegions();

    for (const region of regions) {
      const stream = await this.metricsCollector.createStream(region);
      
      stream.on('metrics', async (metrics) => {
        await this.processRegionMetrics(region, metrics);
      });

      stream.on('error', (error) => {
        logger.error(`Metrics stream error for ${region}:`, error);
      });
    }

    // 글로벌 집계 스트림
    const globalStream = await this.metricsCollector.createGlobalStream();
    
    globalStream.on('aggregate', async (aggregate) => {
      await this.updateGlobalView(aggregate);
    });
  }

  private async processRegionMetrics(
    region: string,
    metrics: RegionMetrics
  ): Promise<void> {
    // 1. 실시간 업데이트
    await this.visualizer.updateRegion(region, metrics);

    // 2. 이상 감지
    const anomalies = await this.detectAnomalies(region, metrics);
    
    if (anomalies.length > 0) {
      await this.handleAnomalies(region, anomalies);
    }

    // 3. 추세 분석
    await this.analyzeTrends(region, metrics);
  }

  private async updateGlobalView(
    aggregate: GlobalAggregate
  ): Promise<void> {
    // 글로벌 대시보드 업데이트
    await this.visualizer.updateGlobal({
      totalRequests: aggregate.totalRequests,
      avgLatency: aggregate.avgLatency,
      errorRate: aggregate.errorRate,
      regionHealth: aggregate.regionHealth,
      crossRegionTraffic: aggregate.crossRegionTraffic
    });

    // 비용 분석
    const costAnalysis = await this.analyzeCosts(aggregate);
    await this.visualizer.updateCosts(costAnalysis);
  }
}
```

**검증 기준**:
- [ ] 멀티 리전 워크로드 분배
- [ ] 글로벌 상태 조정
- [ ] 지역 간 데이터 복제
- [ ] 장애 복구 및 일관성 관리

---

# Phase 5: 오케스트레이션 시스템 - Tasks 5.10~5.12 SubTask 구조

## 📋 Task 5.10~5.12 SubTask 리스트

### Task 5.10: 실시간 오케스트레이션 모니터링
- **SubTask 5.10.1**: 실시간 이벤트 스트리밍 시스템
- **SubTask 5.10.2**: 워크플로우 실행 추적
- **SubTask 5.10.3**: 알림 및 경고 시스템
- **SubTask 5.10.4**: 로그 집계 및 분석

### Task 5.11: 성능 메트릭 및 분석 시스템
- **SubTask 5.11.1**: 메트릭 수집 파이프라인
- **SubTask 5.11.2**: 시계열 데이터 저장소
- **SubTask 5.11.3**: 성능 분석 엔진
- **SubTask 5.11.4**: 예측 분석 및 최적화 제안

### Task 5.12: 관리자 대시보드 및 제어 패널
- **SubTask 5.12.1**: 대시보드 UI/UX 설계
- **SubTask 5.12.2**: 실시간 모니터링 뷰
- **SubTask 5.12.3**: 제어 및 관리 기능
- **SubTask 5.12.4**: 보고서 생성 및 내보내기

---

## 📝 세부 작업지시서

### Task 5.10: 실시간 오케스트레이션 모니터링

#### SubTask 5.10.1: 실시간 이벤트 스트리밍 시스템
**담당자**: 백엔드 개발자  
**예상 소요시간**: 14시간

**작업 내용**:
```typescript
// backend/src/orchestration/monitoring/event_streaming.ts
export enum EventType {
  WORKFLOW_STARTED = 'workflow.started',
  WORKFLOW_COMPLETED = 'workflow.completed',
  WORKFLOW_FAILED = 'workflow.failed',
  TASK_STARTED = 'task.started',
  TASK_COMPLETED = 'task.completed',
  TASK_FAILED = 'task.failed',
  TASK_RETRIED = 'task.retried',
  RESOURCE_ALLOCATED = 'resource.allocated',
  RESOURCE_RELEASED = 'resource.released',
  SCALING_TRIGGERED = 'scaling.triggered',
  ERROR_OCCURRED = 'error.occurred',
  PERFORMANCE_DEGRADATION = 'performance.degradation'
}

export interface OrchestrationEvent {
  id: string;
  type: EventType;
  timestamp: Date;
  source: string;
  correlationId?: string;
  workflowId?: string;
  taskId?: string;
  data: Record<string, any>;
  metadata: EventMetadata;
}

export class EventStreamingSystem {
  private kafka: KafkaClient;
  private eventStore: EventStore;
  private streamProcessors: Map<string, StreamProcessor>;
  private eventEnricher: EventEnricher;

  constructor(config: EventStreamingConfig) {
    this.kafka = new KafkaClient(config.kafka);
    this.eventStore = new EventStore(config.storage);
    this.streamProcessors = new Map();
    this.eventEnricher = new EventEnricher();
    
    this.initialize();
  }

  private async initialize(): Promise<void> {
    // Kafka topics 생성
    await this.createTopics();
    
    // Stream processors 등록
    this.registerProcessors();
    
    // Consumer groups 시작
    await this.startConsumers();
  }

  private async createTopics(): Promise<void> {
    const topics = [
      {
        name: 'orchestration-events',
        partitions: 12,
        replicationFactor: 3
      },
      {
        name: 'orchestration-events-dlq',
        partitions: 6,
        replicationFactor: 3
      },
      {
        name: 'orchestration-metrics',
        partitions: 8,
        replicationFactor: 3
      },
      {
        name: 'orchestration-alerts',
        partitions: 4,
        replicationFactor: 3
      }
    ];

    for (const topic of topics) {
      await this.kafka.createTopic(topic);
    }
  }

  async publishEvent(event: Partial<OrchestrationEvent>): Promise<void> {
    // 이벤트 생성 및 보강
    const enrichedEvent = await this.eventEnricher.enrich({
      id: event.id || uuid(),
      timestamp: event.timestamp || new Date(),
      ...event
    } as OrchestrationEvent);

    // 이벤트 저장
    await this.eventStore.save(enrichedEvent);

    // Kafka로 발행
    await this.kafka.send({
      topic: 'orchestration-events',
      messages: [{
        key: enrichedEvent.workflowId || enrichedEvent.id,
        value: JSON.stringify(enrichedEvent),
        headers: {
          eventType: enrichedEvent.type,
          source: enrichedEvent.source,
          timestamp: enrichedEvent.timestamp.toISOString()
        }
      }]
    });

    // 실시간 처리
    await this.processRealtime(enrichedEvent);
  }

  private async processRealtime(event: OrchestrationEvent): Promise<void> {
    // 관련 프로세서 찾기
    const processors = this.findProcessors(event.type);

    // 병렬 처리
    await Promise.all(
      processors.map(processor => 
        processor.process(event).catch(error => {
          logger.error('Event processing failed', { error, event });
          return this.handleProcessingError(event, error);
        })
      )
    );
  }

  registerProcessor(name: string, processor: StreamProcessor): void {
    this.streamProcessors.set(name, processor);
  }

  async subscribe(
    eventTypes: EventType[],
    handler: EventHandler
  ): Promise<Subscription> {
    const consumerId = uuid();
    const consumer = this.kafka.consumer({
      groupId: `orchestration-monitor-${consumerId}`,
      sessionTimeout: 30000,
      heartbeatInterval: 3000
    });

    await consumer.connect();
    await consumer.subscribe({
      topic: 'orchestration-events',
      fromBeginning: false
    });

    const subscription = new Subscription(consumerId, consumer);

    consumer.run({
      eachMessage: async ({ message }) => {
        const event = JSON.parse(message.value.toString());
        
        if (eventTypes.includes(event.type)) {
          await handler(event);
        }
      }
    });

    return subscription;
  }
}

// 이벤트 보강기
export class EventEnricher {
  private contextProvider: ContextProvider;
  private metadataExtractor: MetadataExtractor;

  async enrich(event: OrchestrationEvent): Promise<OrchestrationEvent> {
    // 컨텍스트 정보 추가
    const context = await this.contextProvider.getContext(event);
    
    // 메타데이터 추출
    const metadata = await this.metadataExtractor.extract(event);

    return {
      ...event,
      data: {
        ...event.data,
        context
      },
      metadata: {
        ...event.metadata,
        ...metadata,
        enrichedAt: new Date()
      }
    };
  }
}

// 스트림 프로세서
export abstract class StreamProcessor {
  abstract name: string;
  abstract eventTypes: EventType[];

  async process(event: OrchestrationEvent): Promise<void> {
    if (!this.shouldProcess(event)) {
      return;
    }

    try {
      await this.preProcess(event);
      await this.processEvent(event);
      await this.postProcess(event);
    } catch (error) {
      await this.handleError(event, error);
    }
  }

  protected shouldProcess(event: OrchestrationEvent): boolean {
    return this.eventTypes.includes(event.type);
  }

  protected async preProcess(event: OrchestrationEvent): Promise<void> {
    // Override in subclasses
  }

  protected abstract processEvent(event: OrchestrationEvent): Promise<void>;

  protected async postProcess(event: OrchestrationEvent): Promise<void> {
    // Override in subclasses
  }

  protected async handleError(
    event: OrchestrationEvent,
    error: Error
  ): Promise<void> {
    logger.error(`${this.name} processing failed`, { event, error });
  }
}

// 실시간 상태 추적기
export class RealtimeStateTracker extends StreamProcessor {
  name = 'realtime-state-tracker';
  eventTypes = Object.values(EventType);

  private stateStore: StateStore;
  private stateAggregator: StateAggregator;
  private websocketServer: WebSocketServer;

  constructor(config: StateTrackerConfig) {
    super();
    this.stateStore = new StateStore(config.redis);
    this.stateAggregator = new StateAggregator();
    this.websocketServer = new WebSocketServer(config.websocket);
  }

  protected async processEvent(event: OrchestrationEvent): Promise<void> {
    // 상태 업데이트
    const stateUpdate = await this.updateState(event);

    // 집계 업데이트
    const aggregates = await this.stateAggregator.update(event);

    // WebSocket으로 브로드캐스트
    await this.broadcast({
      type: 'state-update',
      event,
      state: stateUpdate,
      aggregates
    });
  }

  private async updateState(
    event: OrchestrationEvent
  ): Promise<StateUpdate> {
    switch (event.type) {
      case EventType.WORKFLOW_STARTED:
        return this.handleWorkflowStarted(event);
      
      case EventType.WORKFLOW_COMPLETED:
        return this.handleWorkflowCompleted(event);
      
      case EventType.TASK_STARTED:
        return this.handleTaskStarted(event);
      
      case EventType.TASK_COMPLETED:
        return this.handleTaskCompleted(event);
      
      default:
        return this.handleGenericEvent(event);
    }
  }

  private async handleWorkflowStarted(
    event: OrchestrationEvent
  ): Promise<StateUpdate> {
    const workflowState: WorkflowState = {
      id: event.workflowId!,
      status: 'running',
      startTime: event.timestamp,
      tasks: [],
      metadata: event.data
    };

    await this.stateStore.setWorkflowState(event.workflowId!, workflowState);

    return {
      type: 'workflow-state',
      id: event.workflowId!,
      state: workflowState
    };
  }

  private async broadcast(update: any): Promise<void> {
    const message = JSON.stringify(update);
    
    // 전체 클라이언트에 브로드캐스트
    this.websocketServer.broadcast(message);

    // 특정 구독자에게 전송
    if (update.event.workflowId) {
      this.websocketServer.sendToRoom(
        `workflow:${update.event.workflowId}`,
        message
      );
    }
  }
}

// 이벤트 집계기
export class EventAggregator extends StreamProcessor {
  name = 'event-aggregator';
  eventTypes = Object.values(EventType);

  private windowManager: WindowManager;
  private aggregationRules: AggregationRule[];

  constructor(config: AggregatorConfig) {
    super();
    this.windowManager = new WindowManager(config.windows);
    this.aggregationRules = config.rules;
  }

  protected async processEvent(event: OrchestrationEvent): Promise<void> {
    // 각 윈도우에 이벤트 추가
    await this.windowManager.addEvent(event);

    // 집계 규칙 실행
    for (const rule of this.aggregationRules) {
      if (rule.matches(event)) {
        await this.executeAggregation(rule, event);
      }
    }

    // 만료된 윈도우 처리
    await this.processExpiredWindows();
  }

  private async executeAggregation(
    rule: AggregationRule,
    event: OrchestrationEvent
  ): Promise<void> {
    const window = this.windowManager.getWindow(rule.windowType);
    const events = await window.getEvents();

    const result = await rule.aggregate(events);

    if (result.shouldEmit) {
      await this.emitAggregatedEvent({
        type: EventType.AGGREGATED,
        timestamp: new Date(),
        source: 'aggregator',
        data: {
          rule: rule.name,
          window: rule.windowType,
          result: result.value
        }
      });
    }
  }
}

// 실시간 알림 프로세서
export class AlertProcessor extends StreamProcessor {
  name = 'alert-processor';
  eventTypes = [
    EventType.WORKFLOW_FAILED,
    EventType.TASK_FAILED,
    EventType.ERROR_OCCURRED,
    EventType.PERFORMANCE_DEGRADATION
  ];

  private alertManager: AlertManager;
  private notificationService: NotificationService;

  protected async processEvent(event: OrchestrationEvent): Promise<void> {
    // 알림 규칙 평가
    const alerts = await this.alertManager.evaluate(event);

    // 알림 발송
    for (const alert of alerts) {
      await this.notificationService.send(alert);
    }

    // 알림 기록
    await this.recordAlerts(alerts);
  }
}

// WebSocket 서버
export class WebSocketServer {
  private io: SocketIOServer;
  private rooms: Map<string, Set<string>> = new Map();

  constructor(config: WebSocketConfig) {
    this.io = new SocketIOServer(config.port, {
      cors: config.cors,
      transports: ['websocket', 'polling']
    });

    this.setupHandlers();
  }

  private setupHandlers(): void {
    this.io.on('connection', (socket) => {
      logger.info('Client connected', { socketId: socket.id });

      // 인증
      socket.on('authenticate', async (token) => {
        const auth = await this.authenticate(token);
        if (auth.valid) {
          socket.data.user = auth.user;
          socket.emit('authenticated');
        } else {
          socket.disconnect();
        }
      });

      // 룸 구독
      socket.on('subscribe', (rooms: string[]) => {
        for (const room of rooms) {
          socket.join(room);
          this.addToRoom(room, socket.id);
        }
      });

      // 연결 해제
      socket.on('disconnect', () => {
        this.removeFromAllRooms(socket.id);
        logger.info('Client disconnected', { socketId: socket.id });
      });
    });
  }

  broadcast(message: string): void {
    this.io.emit('event', message);
  }

  sendToRoom(room: string, message: string): void {
    this.io.to(room).emit('event', message);
  }

  private addToRoom(room: string, socketId: string): void {
    if (!this.rooms.has(room)) {
      this.rooms.set(room, new Set());
    }
    this.rooms.get(room)!.add(socketId);
  }

  private removeFromAllRooms(socketId: string): void {
    for (const [room, sockets] of this.rooms.entries()) {
      sockets.delete(socketId);
      if (sockets.size === 0) {
        this.rooms.delete(room);
      }
    }
  }
}
```

**검증 기준**:
- [ ] Kafka 기반 이벤트 스트리밍
- [ ] 실시간 상태 추적
- [ ] WebSocket 통신
- [ ] 이벤트 집계 및 보강

#### SubTask 5.10.2: 워크플로우 실행 추적
**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/monitoring/workflow_tracking.ts
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  version: string;
  status: WorkflowStatus;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  input: Record<string, any>;
  output?: Record<string, any>;
  error?: Error;
  tasks: TaskExecution[];
  metadata: ExecutionMetadata;
  trace: ExecutionTrace;
}

export class WorkflowExecutionTracker {
  private executionStore: ExecutionStore;
  private traceCollector: TraceCollector;
  private lineageTracker: LineageTracker;
  private executionAnalyzer: ExecutionAnalyzer;

  constructor(config: TrackerConfig) {
    this.executionStore = new ExecutionStore(config.storage);
    this.traceCollector = new TraceCollector(config.tracing);
    this.lineageTracker = new LineageTracker();
    this.executionAnalyzer = new ExecutionAnalyzer();
  }

  async startTracking(
    workflowId: string,
    input: Record<string, any>
  ): Promise<ExecutionContext> {
    const executionId = uuid();
    const trace = this.traceCollector.createTrace(executionId);

    const execution: WorkflowExecution = {
      id: executionId,
      workflowId,
      version: await this.getWorkflowVersion(workflowId),
      status: WorkflowStatus.RUNNING,
      startTime: new Date(),
      input,
      tasks: [],
      metadata: {
        triggeredBy: await this.getCurrentUser(),
        environment: process.env.NODE_ENV || 'development',
        correlationId: trace.correlationId
      },
      trace
    };

    // 실행 저장
    await this.executionStore.save(execution);

    // 계보 추적 시작
    await this.lineageTracker.startTracking(execution);

    // 컨텍스트 반환
    return new ExecutionContext(execution, this);
  }

  async trackTaskExecution(
    executionId: string,
    task: TaskDefinition
  ): Promise<TaskExecutionContext> {
    const execution = await this.executionStore.get(executionId);
    if (!execution) {
      throw new Error(`Execution ${executionId} not found`);
    }

    const taskExecution: TaskExecution = {
      id: uuid(),
      taskId: task.id,
      name: task.name,
      type: task.type,
      status: TaskStatus.PENDING,
      createdAt: new Date(),
      dependencies: task.dependencies || [],
      retries: 0,
      maxRetries: task.maxRetries || 3
    };

    // 태스크 추가
    execution.tasks.push(taskExecution);
    await this.executionStore.update(execution);

    // 트레이스 스팬 생성
    const span = this.traceCollector.createSpan(
      execution.trace,
      `task:${task.name}`
    );

    return new TaskExecutionContext(taskExecution, span, this);
  }

  async updateTaskStatus(
    executionId: string,
    taskId: string,
    update: TaskStatusUpdate
  ): Promise<void> {
    const execution = await this.executionStore.get(executionId);
    if (!execution) return;

    const task = execution.tasks.find(t => t.id === taskId);
    if (!task) return;

    // 상태 업데이트
    task.status = update.status;
    
    if (update.status === TaskStatus.RUNNING) {
      task.startTime = new Date();
    } else if (update.status === TaskStatus.COMPLETED) {
      task.endTime = new Date();
      task.duration = task.endTime.getTime() - task.startTime!.getTime();
      task.output = update.output;
    } else if (update.status === TaskStatus.FAILED) {
      task.endTime = new Date();
      task.error = update.error;
      task.retries++;
    }

    // 저장
    await this.executionStore.update(execution);

    // 이벤트 발행
    await this.publishTaskEvent(execution, task, update);
  }

  async completeExecution(
    executionId: string,
    result: ExecutionResult
  ): Promise<void> {
    const execution = await this.executionStore.get(executionId);
    if (!execution) return;

    // 실행 완료
    execution.status = result.success 
      ? WorkflowStatus.COMPLETED 
      : WorkflowStatus.FAILED;
    execution.endTime = new Date();
    execution.duration = execution.endTime.getTime() - execution.startTime.getTime();
    
    if (result.success) {
      execution.output = result.output;
    } else {
      execution.error = result.error;
    }

    // 저장
    await this.executionStore.update(execution);

    // 트레이스 완료
    await this.traceCollector.completeTrace(execution.trace);

    // 계보 완료
    await this.lineageTracker.completeTracking(execution);

    // 분석 실행
    await this.executionAnalyzer.analyze(execution);
  }

  async getExecutionHistory(
    workflowId: string,
    options: HistoryOptions = {}
  ): Promise<ExecutionHistory> {
    const executions = await this.executionStore.findByWorkflow(
      workflowId,
      options
    );

    // 통계 계산
    const stats = this.calculateStatistics(executions);

    // 트렌드 분석
    const trends = await this.analyzeTrends(executions);

    return {
      executions,
      stats,
      trends,
      totalCount: await this.executionStore.count(workflowId)
    };
  }

  private calculateStatistics(
    executions: WorkflowExecution[]
  ): ExecutionStatistics {
    if (executions.length === 0) {
      return {
        totalExecutions: 0,
        successRate: 0,
        averageDuration: 0,
        medianDuration: 0,
        p95Duration: 0
      };
    }

    const successful = executions.filter(
      e => e.status === WorkflowStatus.COMPLETED
    );
    const durations = executions
      .filter(e => e.duration)
      .map(e => e.duration!)
      .sort((a, b) => a - b);

    return {
      totalExecutions: executions.length,
      successRate: successful.length / executions.length,
      averageDuration: this.average(durations),
      medianDuration: this.percentile(durations, 50),
      p95Duration: this.percentile(durations, 95),
      taskStatistics: this.calculateTaskStatistics(executions)
    };
  }
}

// 실행 컨텍스트
export class ExecutionContext {
  constructor(
    private execution: WorkflowExecution,
    private tracker: WorkflowExecutionTracker
  ) {}

  async trackTask(task: TaskDefinition): Promise<TaskExecutionContext> {
    return this.tracker.trackTaskExecution(this.execution.id, task);
  }

  async updateStatus(status: WorkflowStatus): Promise<void> {
    this.execution.status = status;
    await this.save();
  }

  async addMetadata(key: string, value: any): Promise<void> {
    this.execution.metadata[key] = value;
    await this.save();
  }

  async complete(result: ExecutionResult): Promise<void> {
    await this.tracker.completeExecution(this.execution.id, result);
  }

  private async save(): Promise<void> {
    await this.tracker.executionStore.update(this.execution);
  }
}

// 분산 추적
export class TraceCollector {
  private tracer: Tracer;
  private propagator: TracePropagator;

  constructor(config: TracingConfig) {
    this.tracer = new Tracer(config);
    this.propagator = new TracePropagator();
  }

  createTrace(executionId: string): ExecutionTrace {
    const trace = this.tracer.startSpan('workflow-execution', {
      attributes: {
        'workflow.execution.id': executionId,
        'workflow.start.time': new Date().toISOString()
      }
    });

    return {
      traceId: trace.spanContext().traceId,
      spanId: trace.spanContext().spanId,
      correlationId: uuid(),
      baggage: new Map(),
      spans: [trace]
    };
  }

  createSpan(
    parentTrace: ExecutionTrace,
    name: string,
    attributes?: Record<string, any>
  ): Span {
    const span = this.tracer.startSpan(name, {
      parent: parentTrace.spans[0],
      attributes
    });

    parentTrace.spans.push(span);
    return span;
  }

  async completeTrace(trace: ExecutionTrace): Promise<void> {
    // 모든 스팬 완료
    for (const span of trace.spans.reverse()) {
      span.end();
    }

    // 트레이스 데이터 전송
    await this.tracer.flush();
  }

  injectContext(carrier: any, trace: ExecutionTrace): void {
    this.propagator.inject(trace, carrier);
  }

  extractContext(carrier: any): ExecutionTrace | null {
    return this.propagator.extract(carrier);
  }
}

// 데이터 계보 추적
export class LineageTracker {
  private lineageGraph: LineageGraph;
  private datasetRegistry: DatasetRegistry;

  async startTracking(execution: WorkflowExecution): Promise<void> {
    // 입력 데이터셋 등록
    const inputDatasets = await this.identifyDatasets(execution.input);
    
    for (const dataset of inputDatasets) {
      await this.datasetRegistry.register(dataset);
      await this.lineageGraph.addNode({
        type: 'dataset',
        id: dataset.id,
        metadata: dataset
      });
    }

    // 실행 노드 추가
    await this.lineageGraph.addNode({
      type: 'execution',
      id: execution.id,
      metadata: {
        workflowId: execution.workflowId,
        startTime: execution.startTime
      }
    });

    // 입력 엣지 생성
    for (const dataset of inputDatasets) {
      await this.lineageGraph.addEdge({
        from: dataset.id,
        to: execution.id,
        type: 'input',
        timestamp: execution.startTime
      });
    }
  }

  async trackDataTransformation(
    executionId: string,
    taskId: string,
    transformation: DataTransformation
  ): Promise<void> {
    // 변환 노드 추가
    await this.lineageGraph.addNode({
      type: 'transformation',
      id: `${executionId}:${taskId}`,
      metadata: transformation
    });

    // 입력/출력 엣지 추가
    for (const input of transformation.inputs) {
      await this.lineageGraph.addEdge({
        from: input,
        to: `${executionId}:${taskId}`,
        type: 'transform-input'
      });
    }

    for (const output of transformation.outputs) {
      await this.lineageGraph.addEdge({
        from: `${executionId}:${taskId}`,
        to: output,
        type: 'transform-output'
      });
    }
  }

  async getLineage(
    datasetId: string,
    direction: 'upstream' | 'downstream' | 'both' = 'both'
  ): Promise<LineageInfo> {
    const paths = await this.lineageGraph.findPaths(datasetId, {
      direction,
      maxDepth: 10
    });

    return {
      datasetId,
      upstream: direction !== 'downstream' ? paths.upstream : [],
      downstream: direction !== 'upstream' ? paths.downstream : [],
      impactAnalysis: await this.analyzeImpact(paths)
    };
  }
}

// 실행 분석기
export class ExecutionAnalyzer {
  private patternDetector: PatternDetector;
  private anomalyDetector: AnomalyDetector;
  private performanceAnalyzer: PerformanceAnalyzer;

  async analyze(execution: WorkflowExecution): Promise<ExecutionAnalysis> {
    // 패턴 감지
    const patterns = await this.patternDetector.detect(execution);

    // 이상 감지
    const anomalies = await this.anomalyDetector.detect(execution);

    // 성능 분석
    const performance = await this.performanceAnalyzer.analyze(execution);

    // 병목 지점 식별
    const bottlenecks = this.identifyBottlenecks(execution);

    // 개선 제안
    const recommendations = await this.generateRecommendations({
      patterns,
      anomalies,
      performance,
      bottlenecks
    });

    return {
      executionId: execution.id,
      patterns,
      anomalies,
      performance,
      bottlenecks,
      recommendations
    };
  }

  private identifyBottlenecks(
    execution: WorkflowExecution
  ): Bottleneck[] {
    const bottlenecks: Bottleneck[] = [];

    // 태스크별 실행 시간 분석
    const taskDurations = execution.tasks
      .filter(t => t.duration)
      .sort((a, b) => b.duration! - a.duration!);

    // 상위 20% 태스크를 병목으로 식별
    const threshold = taskDurations.length * 0.2;
    
    for (let i = 0; i < Math.min(threshold, taskDurations.length); i++) {
      const task = taskDurations[i];
      bottlenecks.push({
        type: 'task',
        id: task.id,
        name: task.name,
        duration: task.duration!,
        impact: task.duration! / execution.duration!,
        suggestions: this.getBottleneckSuggestions(task)
      });
    }

    return bottlenecks;
  }
}

// 실시간 진행 상황 추적
export class ProgressTracker {
  private progressStore: ProgressStore;
  private estimator: ProgressEstimator;
  private broadcaster: ProgressBroadcaster;

  async updateProgress(
    executionId: string,
    update: ProgressUpdate
  ): Promise<void> {
    // 진행률 계산
    const progress = await this.calculateProgress(executionId, update);

    // 남은 시간 예측
    const eta = await this.estimator.estimateTimeRemaining(
      executionId,
      progress
    );

    // 저장
    await this.progressStore.update(executionId, {
      ...progress,
      eta,
      updatedAt: new Date()
    });

    // 브로드캐스트
    await this.broadcaster.broadcast({
      executionId,
      progress,
      eta
    });
  }

  private async calculateProgress(
    executionId: string,
    update: ProgressUpdate
  ): Promise<Progress> {
    const execution = await this.getExecution(executionId);
    
    const totalTasks = execution.tasks.length;
    const completedTasks = execution.tasks.filter(
      t => t.status === TaskStatus.COMPLETED
    ).length;
    const runningTasks = execution.tasks.filter(
      t => t.status === TaskStatus.RUNNING
    ).length;

    // 가중치 기반 진행률
    let weightedProgress = 0;
    let totalWeight = 0;

    for (const task of execution.tasks) {
      const weight = task.estimatedDuration || 1;
      totalWeight += weight;

      if (task.status === TaskStatus.COMPLETED) {
        weightedProgress += weight;
      } else if (task.status === TaskStatus.RUNNING && task.progress) {
        weightedProgress += weight * task.progress;
      }
    }

    return {
      percentage: totalWeight > 0 ? (weightedProgress / totalWeight) * 100 : 0,
      completedTasks,
      totalTasks,
      runningTasks,
      phase: this.determinePhase(execution)
    };
  }

  private determinePhase(execution: WorkflowExecution): string {
    // 워크플로우 단계 결정 로직
    const completionRate = execution.tasks.filter(
      t => t.status === TaskStatus.COMPLETED
    ).length / execution.tasks.length;

    if (completionRate === 0) return 'initialization';
    if (completionRate < 0.3) return 'early';
    if (completionRate < 0.7) return 'middle';
    if (completionRate < 1) return 'final';
    return 'completed';
  }
}
```

**검증 기준**:
- [ ] 전체 실행 추적
- [ ] 분산 추적 통합
- [ ] 데이터 계보 추적
- [ ] 실행 분석 및 병목 감지

#### SubTask 5.10.3: 알림 및 경고 시스템
**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:
```typescript
// backend/src/orchestration/monitoring/alert_system.ts
export interface AlertRule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  conditions: AlertCondition[];
  actions: AlertAction[];
  severity: AlertSeverity;
  cooldown?: number;
  metadata?: Record<string, any>;
}

export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

export class AlertingSystem {
  private ruleEngine: AlertRuleEngine;
  private notificationManager: NotificationManager;
  private alertStore: AlertStore;
  private deduplicator: AlertDeduplicator;

  constructor(config: AlertingConfig) {
    this.ruleEngine = new AlertRuleEngine(config.rules);
    this.notificationManager = new NotificationManager(config.notifications);
    this.alertStore = new AlertStore(config.storage);
    this.deduplicator = new AlertDeduplicator();
  }

  async evaluateEvent(event: OrchestrationEvent): Promise<void> {
    // 적용 가능한 규칙 찾기
    const applicableRules = await this.ruleEngine.findApplicableRules(event);

    for (const rule of applicableRules) {
      try {
        const triggered = await this.evaluateRule(rule, event);
        
        if (triggered) {
          await this.handleTriggeredAlert(rule, event);
        }
      } catch (error) {
        logger.error('Alert rule evaluation failed', { rule, event, error });
      }
    }
  }

  private async evaluateRule(
    rule: AlertRule,
    event: OrchestrationEvent
  ): Promise<boolean> {
    // 모든 조건 평가
    for (const condition of rule.conditions) {
      const met = await this.evaluateCondition(condition, event);
      
      if (!met) {
        return false; // AND 로직
      }
    }

    return true;
  }

  private async evaluateCondition(
    condition: AlertCondition,
    event: OrchestrationEvent
  ): Promise<boolean> {
    switch (condition.type) {
      case 'threshold':
        return this.evaluateThreshold(condition, event);
      
      case 'pattern':
        return this.evaluatePattern(condition, event);
      
      case 'anomaly':
        return this.evaluateAnomaly(condition, event);
      
      case 'expression':
        return this.evaluateExpression(condition, event);
      
      default:
        return false;
    }
  }

  private async handleTriggeredAlert(
    rule: AlertRule,
    event: OrchestrationEvent
  ): Promise<void> {
    // 중복 제거
    if (await this.deduplicator.isDuplicate(rule, event)) {
      return;
    }

    // 알림 생성
    const alert: Alert = {
      id: uuid(),
      ruleId: rule.id,
      ruleName: rule.name,
      severity: rule.severity,
      triggeredAt: new Date(),
      triggeredBy: event,
      status: AlertStatus.ACTIVE,
      metadata: {
        ...rule.metadata,
        eventData: event.data
      }
    };

    // 저장
    await this.alertStore.save(alert);

    // 액션 실행
    await this.executeActions(rule.actions, alert);

    // 쿨다운 설정
    if (rule.cooldown) {
      await this.deduplicator.setCooldown(rule, rule.cooldown);
    }
  }

  private async executeActions(
    actions: AlertAction[],
    alert: Alert
  ): Promise<void> {
    for (const action of actions) {
      try {
        await this.executeAction(action, alert);
      } catch (error) {
        logger.error('Alert action execution failed', { action, alert, error });
      }
    }
  }

  private async executeAction(
    action: AlertAction,
    alert: Alert
  ): Promise<void> {
    switch (action.type) {
      case 'notification':
        await this.sendNotification(action, alert);
        break;
      
      case 'webhook':
        await this.callWebhook(action, alert);
        break;
      
      case 'escalation':
        await this.escalate(action, alert);
        break;
      
      case 'auto-remediation':
        await this.autoRemediate(action, alert);
        break;
    }
  }

  private async sendNotification(
    action: AlertAction,
    alert: Alert
  ): Promise<void> {
    const notification: Notification = {
      channels: action.config.channels,
      recipients: await this.resolveRecipients(action.config.recipients),
      template: action.config.template,
      data: {
        alert,
        severity: alert.severity,
        timestamp: alert.triggeredAt,
        details: this.formatAlertDetails(alert)
      }
    };

    await this.notificationManager.send(notification);
  }
}

// 알림 규칙 엔진
export class AlertRuleEngine {
  private rules: Map<string, AlertRule> = new Map();
  private ruleIndex: RuleIndex;
  private compiler: RuleCompiler;

  constructor(config: RuleEngineConfig) {
    this.ruleIndex = new RuleIndex();
    this.compiler = new RuleCompiler();
    
    this.loadRules(config.rules);
  }

  async findApplicableRules(event: OrchestrationEvent): Promise<AlertRule[]> {
    // 이벤트 타입 기반 인덱스 검색
    const candidateRules = await this.ruleIndex.findByEventType(event.type);

    // 활성화된 규칙만 필터링
    return candidateRules.filter(rule => rule.enabled);
  }

  async addRule(rule: AlertRule): Promise<void> {
    // 규칙 검증
    const validation = await this.validateRule(rule);
    if (!validation.valid) {
      throw new ValidationError(validation.errors);
    }

    // 규칙 컴파일
    const compiled = await this.compiler.compile(rule);

    // 저장
    this.rules.set(rule.id, compiled);
    
    // 인덱스 업데이트
    await this.ruleIndex.index(compiled);
  }

  async updateRule(ruleId: string, updates: Partial<AlertRule>): Promise<void> {
    const existing = this.rules.get(ruleId);
    if (!existing) {
      throw new Error(`Rule ${ruleId} not found`);
    }

    const updated = { ...existing, ...updates };
    await this.addRule(updated);
  }

  async deleteRule(ruleId: string): Promise<void> {
    this.rules.delete(ruleId);
    await this.ruleIndex.remove(ruleId);
  }

  private async validateRule(rule: AlertRule): Promise<ValidationResult> {
    const errors: string[] = [];

    // 필수 필드 검증
    if (!rule.name) {
      errors.push('Rule name is required');
    }

    if (rule.conditions.length === 0) {
      errors.push('At least one condition is required');
    }

    if (rule.actions.length === 0) {
      errors.push('At least one action is required');
    }

    // 조건 검증
    for (const condition of rule.conditions) {
      const conditionErrors = await this.validateCondition(condition);
      errors.push(...conditionErrors);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// 알림 관리자
export class NotificationManager {
  private channels: Map<string, NotificationChannel>;
  private templateEngine: TemplateEngine;
  private rateLimiter: RateLimiter;

  constructor(config: NotificationConfig) {
    this.channels = this.initializeChannels(config.channels);
    this.templateEngine = new TemplateEngine(config.templates);
    this.rateLimiter = new RateLimiter(config.rateLimit);
  }

  private initializeChannels(
    channelConfigs: ChannelConfig[]
  ): Map<string, NotificationChannel> {
    const channels = new Map();

    for (const config of channelConfigs) {
      switch (config.type) {
        case 'email':
          channels.set(config.name, new EmailChannel(config));
          break;
        
        case 'slack':
          channels.set(config.name, new SlackChannel(config));
          break;
        
        case 'webhook':
          channels.set(config.name, new WebhookChannel(config));
          break;
        
        case 'sms':
          channels.set(config.name, new SMSChannel(config));
          break;
        
        case 'pagerduty':
          channels.set(config.name, new PagerDutyChannel(config));
          break;
      }
    }

    return channels;
  }

  async send(notification: Notification): Promise<void> {
    // 속도 제한 확인
    const allowed = await this.rateLimiter.allow(
      notification.recipients.join(',')
    );

    if (!allowed) {
      logger.warn('Notification rate limited', { notification });
      return;
    }

    // 템플릿 렌더링
    const content = await this.templateEngine.render(
      notification.template,
      notification.data
    );

    // 각 채널로 발송
    const promises = notification.channels.map(channelName => {
      const channel = this.channels.get(channelName);
      
      if (!channel) {
        logger.error(`Channel ${channelName} not found`);
        return Promise.resolve();
      }

      return channel.send({
        recipients: notification.recipients,
        content,
        metadata: notification.data
      });
    });

    await Promise.allSettled(promises);
  }
}

// 이메일 채널
export class EmailChannel implements NotificationChannel {
  private transporter: EmailTransporter;

  constructor(config: EmailChannelConfig) {
    this.transporter = createTransporter(config);
  }

  async send(message: ChannelMessage): Promise<void> {
    const emailOptions = {
      to: message.recipients,
      subject: message.content.subject,
      html: message.content.body,
      attachments: message.content.attachments
    };

    await this.transporter.sendMail(emailOptions);
  }
}

// Slack 채널
export class SlackChannel implements NotificationChannel {
  private client: SlackWebClient;

  constructor(config: SlackChannelConfig) {
    this.client = new SlackWebClient(config.token);
  }

  async send(message: ChannelMessage): Promise<void> {
    for (const recipient of message.recipients) {
      await this.client.chat.postMessage({
        channel: recipient,
        text: message.content.text,
        blocks: this.createBlocks(message.content),
        attachments: message.content.attachments
      });
    }
  }

  private createBlocks(content: NotificationContent): any[] {
    const blocks = [];

    // 헤더 블록
    if (content.title) {
      blocks.push({
        type: 'header',
        text: {
          type: 'plain_text',
          text: content.title
        }
      });
    }

    // 본문 블록
    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: content.body
      }
    });

    // 필드 블록
    if (content.fields) {
      blocks.push({
        type: 'section',
        fields: Object.entries(content.fields).map(([key, value]) => ({
          type: 'mrkdwn',
          text: `*${key}:* ${value}`
        }))
      });
    }

    // 액션 블록
    if (content.actions) {
      blocks.push({
        type: 'actions',
        elements: content.actions.map(action => ({
          type: 'button',
          text: {
            type: 'plain_text',
            text: action.label
          },
          url: action.url,
          style: action.style
        }))
      });
    }

    return blocks;
  }
}

// 알림 중복 제거
export class AlertDeduplicator {
  private cache: LRUCache<string, Date>;
  private fingerprinter: AlertFingerprinter;

  constructor() {
    this.cache = new LRUCache({ max: 10000 });
    this.fingerprinter = new AlertFingerprinter();
  }

  async isDuplicate(rule: AlertRule, event: OrchestrationEvent): Promise<boolean> {
    const fingerprint = await this.fingerprinter.generate(rule, event);
    const lastSeen = this.cache.get(fingerprint);

    if (!lastSeen) {
      this.cache.set(fingerprint, new Date());
      return false;
    }

    const timeSinceLastSeen = Date.now() - lastSeen.getTime();
    const deduplicationWindow = rule.deduplication?.window || 300000; // 5분

    return timeSinceLastSeen < deduplicationWindow;
  }

  async setCooldown(rule: AlertRule, duration: number): Promise<void> {
    const key = `cooldown:${rule.id}`;
    this.cache.set(key, new Date(), { ttl: duration });
  }
}

// 에스컬레이션 관리
export class EscalationManager {
  private policies: Map<string, EscalationPolicy>;
  private escalationTracker: EscalationTracker;

  async escalate(alert: Alert, policy: EscalationPolicy): Promise<void> {
    const level = await this.escalationTracker.getCurrentLevel(alert.id);
    const nextLevel = level + 1;

    if (nextLevel >= policy.levels.length) {
      logger.warn('Max escalation level reached', { alert, level });
      return;
    }

    const escalationLevel = policy.levels[nextLevel];

    // 다음 레벨 담당자에게 알림
    await this.notifyLevel(alert, escalationLevel);

    // 에스컬레이션 기록
    await this.escalationTracker.recordEscalation(alert.id, nextLevel);

    // 다음 에스컬레이션 예약
    if (escalationLevel.timeout) {
      setTimeout(() => {
        this.checkAndEscalate(alert, policy);
      }, escalationLevel.timeout);
    }
  }

  private async notifyLevel(
    alert: Alert,
    level: EscalationLevel
  ): Promise<void> {
    const notification = {
      channels: level.channels,
      recipients: level.recipients,
      template: 'escalation',
      data: {
        alert,
        level: level.name,
        priority: level.priority
      }
    };

    await this.notificationManager.send(notification);
  }
}

// 자동 복구
export class AutoRemediator {
  private remediationScripts: Map<string, RemediationScript>;
  private executor: ScriptExecutor;

  async remediate(alert: Alert, action: RemediationAction): Promise<void> {
    const script = this.remediationScripts.get(action.scriptId);
    
    if (!script) {
      throw new Error(`Remediation script ${action.scriptId} not found`);
    }

    // 실행 컨텍스트 준비
    const context = {
      alert,
      parameters: action.parameters,
      environment: await this.getEnvironment()
    };

    // 스크립트 실행
    const result = await this.executor.execute(script, context);

    // 결과 기록
    await this.recordRemediation({
      alertId: alert.id,
      scriptId: script.id,
      executedAt: new Date(),
      result
    });

    // 성공 시 알림 해제
    if (result.success) {
      await this.resolveAlert(alert.id);
    }
  }
}
```

**검증 기준**:
- [ ] 규칙 기반 알림 엔진
- [ ] 다중 채널 알림 지원
- [ ] 알림 중복 제거
- [ ] 에스컬레이션 및 자동 복구

#### SubTask 5.10.4: 로그 집계 및 분석
**담당자**: 데이터 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:
```typescript
// backend/src/orchestration/monitoring/log_aggregation.ts
export interface LogEntry {
  timestamp: Date;
  level: LogLevel;
  source: string;
  correlationId?: string;
  workflowId?: string;
  taskId?: string;
  message: string;
  metadata?: Record<string, any>;
  stackTrace?: string;
}

export class LogAggregationSystem {
  private collectors: Map<string, LogCollector>;
  private pipeline: LogPipeline;
  private storage: LogStorage;
  private analyzer: LogAnalyzer;

  constructor(config: LogAggregationConfig) {
    this.collectors = this.initializeCollectors(config.sources);
    this.pipeline = new LogPipeline(config.pipeline);
    this.storage = new LogStorage(config.storage);
    this.analyzer = new LogAnalyzer();
  }

  private initializeCollectors(
    sources: LogSourceConfig[]
  ): Map<string, LogCollector> {
    const collectors = new Map();

    for (const source of sources) {
      switch (source.type) {
        case 'file':
          collectors.set(source.name, new FileLogCollector(source));
          break;
        
        case 'syslog':
          collectors.set(source.name, new SyslogCollector(source));
          break;
        
        case 'cloudwatch':
          collectors.set(source.name, new CloudWatchCollector(source));
          break;
        
        case 'kubernetes':
          collectors.set(source.name, new KubernetesLogCollector(source));
          break;
        
        case 'application':
          collectors.set(source.name, new ApplicationLogCollector(source));
          break;
      }
    }

    return collectors;
  }

  async start(): Promise<void> {
    // 각 수집기 시작
    for (const [name, collector] of this.collectors) {
      await collector.start();
      
      // 로그 스트림 처리
      collector.on('log', async (log) => {
        await this.processLog(log);
      });

      collector.on('error', (error) => {
        logger.error(`Collector ${name} error:`, error);
      });
    }

    // 파이프라인 시작
    await this.pipeline.start();
  }

  private async processLog(log: LogEntry): Promise<void> {
    try {
      // 파이프라인 처리
      const processed = await this.pipeline.process(log);

      // 저장
      await this.storage.store(processed);

      // 실시간 분석
      await this.analyzer.analyze(processed);

    } catch (error) {
      logger.error('Log processing failed', { log, error });
    }
  }

  async query(params: LogQueryParams): Promise<LogQueryResult> {
    // 쿼리 최적화
    const optimized = await this.optimizeQuery(params);

    // 실행
    const results = await this.storage.query(optimized);

    // 집계
    const aggregations = params.aggregations 
      ? await this.aggregate(results, params.aggregations)
      : undefined;

    return {
      logs: results,
      total: await this.storage.count(optimized),
      aggregations
    };
  }
}

// 로그 파이프라인
export class LogPipeline {
  private stages: PipelineStage[];
  private errorHandler: ErrorHandler;

  constructor(config: PipelineConfig) {
    this.stages = this.createStages(config.stages);
    this.errorHandler = new ErrorHandler(config.errorHandling);
  }

  private createStages(stageConfigs: StageConfig[]): PipelineStage[] {
    return stageConfigs.map(config => {
      switch (config.type) {
        case 'parser':
          return new ParserStage(config);
        case 'filter':
          return new FilterStage(config);
        case 'enricher':
          return new EnricherStage(config);
        case 'transformer':
          return new TransformerStage(config);
        case 'aggregator':
          return new AggregatorStage(config);
        default:
          throw new Error(`Unknown stage type: ${config.type}`);
      }
    });
  }

  async process(log: LogEntry): Promise<LogEntry> {
    let current = log;

    for (const stage of this.stages) {
      try {
        current = await stage.process(current);
        
        if (!current) {
          // 필터링된 경우
          return null;
        }
      } catch (error) {
        current = await this.errorHandler.handle(current, error, stage);
      }
    }

    return current;
  }
}

// 로그 파서 스테이지
export class ParserStage implements PipelineStage {
  private parsers: Map<string, LogParser>;

  constructor(config: ParserStageConfig) {
    this.parsers = new Map();
    
    // 파서 등록
    this.parsers.set('json', new JSONParser());
    this.parsers.set('regex', new RegexParser(config.patterns));
    this.parsers.set('grok', new GrokParser(config.grokPatterns));
    this.parsers.set('kv', new KeyValueParser());
  }

  async process(log: LogEntry): Promise<LogEntry> {
    // 자동 파서 선택
    const parser = this.selectParser(log);
    
    if (!parser) {
      return log;
    }

    // 파싱
    const parsed = await parser.parse(log.message);
    
    // 메타데이터 병합
    return {
      ...log,
      metadata: {
        ...log.metadata,
        ...parsed
      }
    };
  }

  private selectParser(log: LogEntry): LogParser | null {
    // JSON 감지
    if (log.message.trim().startsWith('{')) {
      return this.parsers.get('json');
    }

    // 키-값 쌍 감지
    if (log.message.includes('=')) {
      return this.parsers.get('kv');
    }

    // 기본 정규식 파서
    return this.parsers.get('regex');
  }
}

// 로그 보강 스테이지
export class EnricherStage implements PipelineStage {
  private enrichers: Enricher[];

  constructor(config: EnricherStageConfig) {
    this.enrichers = [
      new GeoIPEnricher(),
      new UserAgentEnricher(),
      new HostEnricher(),
      new TraceEnricher(),
      new MetadataEnricher(config.metadata)
    ];
  }

  async process(log: LogEntry): Promise<LogEntry> {
    let enriched = log;

    for (const enricher of this.enrichers) {
      enriched = await enricher.enrich(enriched);
    }

    return enriched;
  }
}

// 로그 저장소
export class LogStorage {
  private elasticsearch: ElasticsearchClient;
  private s3: S3Client;
  private retentionManager: RetentionManager;

  constructor(config: StorageConfig) {
    this.elasticsearch = new ElasticsearchClient(config.elasticsearch);
    this.s3 = new S3Client(config.s3);
    this.retentionManager = new RetentionManager(config.retention);
  }

  async store(log: LogEntry): Promise<void> {
    // 인덱스 이름 생성
    const indexName = this.getIndexName(log);

    // Elasticsearch에 저장
    await this.elasticsearch.index({
      index: indexName,
      body: log,
      pipeline: 'log-processing'
    });

    // 장기 보관이 필요한 경우 S3에도 저장
    if (this.shouldArchive(log)) {
      await this.archiveToS3(log);
    }
  }

  private getIndexName(log: LogEntry): string {
    const date = log.timestamp.toISOString().split('T')[0];
    const prefix = log.workflowId ? 'workflow-logs' : 'application-logs';
    return `${prefix}-${date}`;
  }

  async query(params: LogQueryParams): Promise<LogEntry[]> {
    const query = this.buildQuery(params);

    const response = await this.elasticsearch.search({
      index: params.index || 'logs-*',
      body: {
        query,
        sort: params.sort || [{ timestamp: 'desc' }],
        size: params.size || 100,
        from: params.from || 0,
        _source: params.fields
      }
    });

    return response.hits.hits.map(hit => hit._source as LogEntry);
  }

  private buildQuery(params: LogQueryParams): any {
    const must = [];
    const filter = [];

    // 시간 범위
    if (params.startTime || params.endTime) {
      filter.push({
        range: {
          timestamp: {
            gte: params.startTime?.toISOString(),
            lte: params.endTime?.toISOString()
          }
        }
      });
    }

    // 텍스트 검색
    if (params.search) {
      must.push({
        multi_match: {
          query: params.search,
          fields: ['message', 'metadata.*'],
          type: 'phrase_prefix'
        }
      });
    }

    // 필터
    if (params.filters) {
      for (const [field, value] of Object.entries(params.filters)) {
        filter.push({ term: { [field]: value } });
      }
    }

    return {
      bool: {
        must,
        filter
      }
    };
  }
}

// 로그 분석기
export class LogAnalyzer {
  private patternMiner: PatternMiner;
  private anomalyDetector: LogAnomalyDetector;
  private errorAnalyzer: ErrorAnalyzer;
  private performanceAnalyzer: LogPerformanceAnalyzer;

  async analyze(log: LogEntry): Promise<void> {
    // 패턴 마이닝
    await this.patternMiner.process(log);

    // 이상 감지
    const anomaly = await this.anomalyDetector.detect(log);
    if (anomaly) {
      await this.handleAnomaly(anomaly);
    }

    // 에러 분석
    if (log.level === 'error' || log.level === 'fatal') {
      await this.errorAnalyzer.analyze(log);
    }

    // 성능 분석
    if (this.isPerformanceRelated(log)) {
      await this.performanceAnalyzer.analyze(log);
    }
  }

  private isPerformanceRelated(log: LogEntry): boolean {
    const keywords = ['duration', 'latency', 'response time', 'slow'];
    return keywords.some(keyword => 
      log.message.toLowerCase().includes(keyword)
    );
  }
}

// 패턴 마이닝
export class PatternMiner {
  private patterns: Map<string, LogPattern>;
  private clustering: LogClustering;

  async process(log: LogEntry): Promise<void> {
    // 로그 정규화
    const normalized = this.normalize(log.message);

    // 패턴 매칭
    let matched = false;
    for (const [id, pattern] of this.patterns) {
      if (pattern.matches(normalized)) {
        await this.updatePattern(pattern, log);
        matched = true;
        break;
      }
    }

    // 새 패턴 발견
    if (!matched) {
      await this.discoverNewPattern(log, normalized);
    }
  }

  private normalize(message: string): string {
    // 숫자, 날짜, ID 등을 플레이스홀더로 치환
    return message
      .replace(/\b\d+\b/g, '<NUM>')
      .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '<UUID>')
      .replace(/\b\d{4}-\d{2}-\d{2}\b/g, '<DATE>')
      .replace(/\b\d{2}:\d{2}:\d{2}\b/g, '<TIME>')
      .replace(/\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/g, '<IP>');
  }

  private async discoverNewPattern(
    log: LogEntry,
    normalized: string
  ): Promise<void> {
    // 클러스터링을 통한 패턴 발견
    const cluster = await this.clustering.assignCluster(normalized);

    if (cluster.size > 10) {
      // 충분한 샘플이 모이면 패턴으로 등록
      const pattern = new LogPattern({
        id: uuid(),
        template: this.extractTemplate(cluster),
        frequency: cluster.size,
        firstSeen: new Date(),
        lastSeen: new Date()
      });

      this.patterns.set(pattern.id, pattern);
    }
  }
}

// 로그 시각화 데이터 생성
export class LogVisualizationGenerator {
  async generateDashboardData(
    logs: LogEntry[],
    timeRange: TimeRange
  ): Promise<DashboardData> {
    return {
      timeSeries: this.generateTimeSeries(logs, timeRange),
      logLevelDistribution: this.calculateLogLevelDistribution(logs),
      topErrors: this.findTopErrors(logs),
      errorRate: this.calculateErrorRate(logs),
      sources: this.analyzeSources(logs),
      patterns: await this.extractPatterns(logs)
    };
  }

  private generateTimeSeries(
    logs: LogEntry[],
    timeRange: TimeRange
  ): TimeSeriesData {
    const buckets = this.createTimeBuckets(timeRange);
    const series: Record<string, number[]> = {};

    // 로그 레벨별 시계열
    for (const level of ['debug', 'info', 'warn', 'error', 'fatal']) {
      series[level] = new Array(buckets.length).fill(0);
    }

    // 로그 분류
    for (const log of logs) {
      const bucketIndex = this.findBucketIndex(log.timestamp, buckets);
      if (bucketIndex >= 0) {
        series[log.level][bucketIndex]++;
      }
    }

    return {
      timestamps: buckets.map(b => b.start),
      series
    };
  }

  private calculateLogLevelDistribution(
    logs: LogEntry[]
  ): Record<string, number> {
    const distribution: Record<string, number> = {};

    for (const log of logs) {
      distribution[log.level] = (distribution[log.level] || 0) + 1;
    }

    return distribution;
  }

  private findTopErrors(logs: LogEntry[], limit: number = 10): ErrorSummary[] {
    const errorGroups = new Map<string, ErrorSummary>();

    const errors = logs.filter(log => 
      log.level === 'error' || log.level === 'fatal'
    );

    for (const error of errors) {
      const fingerprint = this.generateErrorFingerprint(error);
      
      if (!errorGroups.has(fingerprint)) {
        errorGroups.set(fingerprint, {
          message: error.message,
          count: 0,
          firstSeen: error.timestamp,
          lastSeen: error.timestamp,
          stackTrace: error.stackTrace
        });
      }

      const group = errorGroups.get(fingerprint)!;
      group.count++;
      group.lastSeen = error.timestamp;
    }

    // 상위 N개 반환
    return Array.from(errorGroups.values())
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);
  }

  private generateErrorFingerprint(log: LogEntry): string {
    // 스택 트레이스나 메시지 패턴으로 fingerprint 생성
    if (log.stackTrace) {
      const lines = log.stackTrace.split('\n');
      const relevantLines = lines.slice(0, 3).join('\n');
      return crypto.createHash('md5').update(relevantLines).digest('hex');
    }

    // 메시지 정규화
    const normalized = log.message
      .replace(/\b\d+\b/g, 'N')
      .replace(/\b[0-9a-f-]{36}\b/gi, 'ID');

    return crypto.createHash('md5').update(normalized).digest('hex');
  }
}
```

**검증 기준**:
- [ ] 다중 소스 로그 수집
- [ ] 로그 파이프라인 처리
- [ ] 패턴 마이닝 및 분석
- [ ] 로그 시각화 데이터 생성

### Task 5.11: 성능 메트릭 및 분석 시스템

#### SubTask 5.11.1: 메트릭 수집 파이프라인
**담당자**: 데이터 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/metrics/collection_pipeline.ts
export interface Metric {
  name: string;
  value: number;
  timestamp: Date;
  tags: Record<string, string>;
  type: MetricType;
  unit?: string;
  metadata?: Record<string, any>;
}

export enum MetricType {
  COUNTER = 'counter',
  GAUGE = 'gauge',
  HISTOGRAM = 'histogram',
  SUMMARY = 'summary'
}

export class MetricsCollectionPipeline {
  private collectors: Map<string, MetricCollector>;
  private processors: MetricProcessor[];
  private exporters: Map<string, MetricExporter>;
  private aggregator: MetricAggregator;
  private buffer: MetricBuffer;

  constructor(config: PipelineConfig) {
    this.collectors = this.initializeCollectors(config.collectors);
    this.processors = this.initializeProcessors(config.processors);
    this.exporters = this.initializeExporters(config.exporters);
    this.aggregator = new MetricAggregator(config.aggregation);
    this.buffer = new MetricBuffer(config.buffer);
  }

  private initializeCollectors(
    configs: CollectorConfig[]
  ): Map<string, MetricCollector> {
    const collectors = new Map();

    for (const config of configs) {
      switch (config.type) {
        case 'system':
          collectors.set(config.name, new SystemMetricsCollector(config));
          break;
        
        case 'application':
          collectors.set(config.name, new ApplicationMetricsCollector(config));
          break;
        
        case 'custom':
          collectors.set(config.name, new CustomMetricsCollector(config));
          break;
        
        case 'prometheus':
          collectors.set(config.name, new PrometheusCollector(config));
          break;
        
        case 'statsd':
          collectors.set(config.name, new StatsDCollector(config));
          break;
      }
    }

    return collectors;
  }

  async start(): Promise<void> {
    // 컬렉터 시작
    for (const [name, collector] of this.collectors) {
      await collector.start();
      
      collector.on('metrics', async (metrics) => {
        await this.processMetrics(metrics);
      });

      collector.on('error', (error) => {
        logger.error(`Collector ${name} error:`, error);
      });
    }

    // 주기적 플러시
    this.startPeriodicFlush();
  }

  private async processMetrics(metrics: Metric[]): Promise<void> {
    // 1. 버퍼에 추가
    await this.buffer.add(metrics);

    // 2. 프로세싱
    let processed = metrics;
    for (const processor of this.processors) {
      processed = await processor.process(processed);
    }

    // 3. 집계
    const aggregated = await this.aggregator.aggregate(processed);

    // 4. 내보내기
    await this.export(aggregated);
  }

  private async export(metrics: Metric[]): Promise<void> {
    const promises = [];

    for (const [name, exporter] of this.exporters) {
      promises.push(
        exporter.export(metrics).catch(error => {
          logger.error(`Exporter ${name} failed:`, error);
        })
      );
    }

    await Promise.all(promises);
  }

  private startPeriodicFlush(): void {
    setInterval(async () => {
      const buffered = await this.buffer.flush();
      if (buffered.length > 0) {
        await this.processMetrics(buffered);
      }
    }, 10000); // 10초마다
  }
}

// 시스템 메트릭 수집기
export class SystemMetricsCollector extends MetricCollector {
  private osUtils: OSUtils;
  private processMonitor: ProcessMonitor;

  constructor(config: SystemCollectorConfig) {
    super(config);
    this.osUtils = new OSUtils();
    this.processMonitor = new ProcessMonitor();
  }

  async collect(): Promise<Metric[]> {
    const metrics: Metric[] = [];
    const timestamp = new Date();

    // CPU 메트릭
    const cpuUsage = await this.osUtils.getCPUUsage();
    metrics.push({
      name: 'system.cpu.usage',
      value: cpuUsage.total,
      timestamp,
      tags: { cpu: 'all' },
      type: MetricType.GAUGE,
      unit: 'percent'
    });

    // 코어별 CPU
    cpuUsage.cores.forEach((usage, index) => {
      metrics.push({
        name: 'system.cpu.core.usage',
        value: usage,
        timestamp,
        tags: { core: index.toString() },
        type: MetricType.GAUGE,
        unit: 'percent'
      });
    });

    // 메모리 메트릭
    const memory = await this.osUtils.getMemoryInfo();
    metrics.push(
      {
        name: 'system.memory.total',
        value: memory.total,
        timestamp,
        tags: {},
        type: MetricType.GAUGE,
        unit: 'bytes'
      },
      {
        name: 'system.memory.used',
        value: memory.used,
        timestamp,
        tags: {},
        type: MetricType.GAUGE,
        unit: 'bytes'
      },
      {
        name: 'system.memory.free',
        value: memory.free,
        timestamp,
        tags: {},
        type: MetricType.GAUGE,
        unit: 'bytes'
      },
      {
        name: 'system.memory.usage',
        value: (memory.used / memory.total) * 100,
        timestamp,
        tags: {},
        type: MetricType.GAUGE,
        unit: 'percent'
      }
    );

    // 디스크 메트릭
    const disks = await this.osUtils.getDiskInfo();
    for (const disk of disks) {
      const tags = { device: disk.device, mount: disk.mount };
      
      metrics.push(
        {
          name: 'system.disk.total',
          value: disk.total,
          timestamp,
          tags,
          type: MetricType.GAUGE,
          unit: 'bytes'
        },
        {
          name: 'system.disk.used',
          value: disk.used,
          timestamp,
          tags,
          type: MetricType.GAUGE,
          unit: 'bytes'
        },
        {
          name: 'system.disk.usage',
          value: (disk.used / disk.total) * 100,
          timestamp,
          tags,
          type: MetricType.GAUGE,
          unit: 'percent'
        }
      );
    }

    // 네트워크 메트릭
    const network = await this.osUtils.getNetworkInfo();
    for (const iface of network.interfaces) {
      const tags = { interface: iface.name };
      
      metrics.push(
        {
          name: 'system.network.rx.bytes',
          value: iface.rxBytes,
          timestamp,
          tags,
          type: MetricType.COUNTER,
          unit: 'bytes'
        },
        {
          name: 'system.network.tx.bytes',
          value: iface.txBytes,
          timestamp,
          tags,
          type: MetricType.COUNTER,
          unit: 'bytes'
        },
        {
          name: 'system.network.rx.packets',
          value: iface.rxPackets,
          timestamp,
          tags,
          type: MetricType.COUNTER,
          unit: 'packets'
        },
        {
          name: 'system.network.tx.packets',
          value: iface.txPackets,
          timestamp,
          tags,
          type: MetricType.COUNTER,
          unit: 'packets'
        }
      );
    }

    // 프로세스 메트릭
    const processInfo = await this.processMonitor.getInfo();
    metrics.push(
      {
        name: 'process.cpu.usage',
        value: processInfo.cpuUsage,
        timestamp,
        tags: { pid: processInfo.pid.toString() },
        type: MetricType.GAUGE,
        unit: 'percent'
      },
      {
        name: 'process.memory.rss',
        value: processInfo.memoryRss,
        timestamp,
        tags: { pid: processInfo.pid.toString() },
        type: MetricType.GAUGE,
        unit: 'bytes'
      },
      {
        name: 'process.memory.heap.used',
        value: processInfo.heapUsed,
        timestamp,
        tags: { pid: processInfo.pid.toString() },
        type: MetricType.GAUGE,
        unit: 'bytes'
      },
      {
        name: 'process.memory.heap.total',
        value: processInfo.heapTotal,
        timestamp,
        tags: { pid: processInfo.pid.toString() },
        type: MetricType.GAUGE,
        unit: 'bytes'
      }
    );

    return metrics;
  }
}

// 애플리케이션 메트릭 수집기
export class ApplicationMetricsCollector extends MetricCollector {
  private metricsRegistry: MetricsRegistry;
  
  constructor(config: ApplicationCollectorConfig) {
    super(config);
    this.metricsRegistry = MetricsRegistry.getInstance();
  }

  async collect(): Promise<Metric[]> {
    const metrics: Metric[] = [];
    const timestamp = new Date();

    // 워크플로우 메트릭
    const workflowMetrics = this.metricsRegistry.getWorkflowMetrics();
    
    metrics.push(
      {
        name: 'workflow.executions.total',
        value: workflowMetrics.totalExecutions,
        timestamp,
        tags: {},
        type: MetricType.COUNTER
      },
      {
        name: 'workflow.executions.active',
        value: workflowMetrics.activeExecutions,
        timestamp,
        tags: {},
        type: MetricType.GAUGE
      },
      {
        name: 'workflow.executions.success',
        value: workflowMetrics.successfulExecutions,
        timestamp,
        tags: {},
        type: MetricType.COUNTER
      },
      {
        name: 'workflow.executions.failed',
        value: workflowMetrics.failedExecutions,
        timestamp,
        tags: {},
        type: MetricType.COUNTER
      }
    );

    // 태스크 메트릭
    const taskMetrics = this.metricsRegistry.getTaskMetrics();
    
    for (const [taskType, metrics] of taskMetrics) {
      const tags = { task_type: taskType };
      
      metrics.push(
        {
          name: 'task.executions.total',
          value: metrics.total,
          timestamp,
          tags,
          type: MetricType.COUNTER
        },
        {
          name: 'task.duration.seconds',
          value: metrics.averageDuration,
          timestamp,
          tags,
          type: MetricType.HISTOGRAM,
          unit: 'seconds'
        },
        {
          name: 'task.success.rate',
          value: metrics.successRate,
          timestamp,
          tags,
          type: MetricType.GAUGE,
          unit: 'ratio'
        }
      );
    }

    // 리소스 메트릭
    const resourceMetrics = this.metricsRegistry.getResourceMetrics();
    
    metrics.push(
      {
        name: 'resource.utilization',
        value: resourceMetrics.overallUtilization,
        timestamp,
        tags: {},
        type: MetricType.GAUGE,
        unit: 'percent'
      },
      {
        name: 'resource.allocations.active',
        value: resourceMetrics.activeAllocations,
        timestamp,
        tags: {},
        type: MetricType.GAUGE
      },
      {
        name: 'resource.queue.depth',
        value: resourceMetrics.queueDepth,
        timestamp,
        tags: {},
        type: MetricType.GAUGE
      }
    );

    // API 메트릭
    const apiMetrics = this.metricsRegistry.getAPIMetrics();
    
    for (const [endpoint, metrics] of apiMetrics) {
      const tags = { endpoint, method: metrics.method };
      
      metrics.push(
        {
          name: 'api.requests.total',
          value: metrics.totalRequests,
          timestamp,
          tags,
          type: MetricType.COUNTER
        },
        {
          name: 'api.requests.duration',
          value: metrics.averageDuration,
          timestamp,
          tags,
          type: MetricType.HISTOGRAM,
          unit: 'milliseconds'
        },
        {
          name: 'api.requests.errors',
          value: metrics.errorCount,
          timestamp,
          tags,
          type: MetricType.COUNTER
        }
      );
    }

    return metrics;
  }
}

// 메트릭 프로세서
export abstract class MetricProcessor {
  abstract async process(metrics: Metric[]): Promise<Metric[]>;
}

// 레이트 계산 프로세서
export class RateProcessor extends MetricProcessor {
  private previousValues: Map<string, number> = new Map();

  async process(metrics: Metric[]): Promise<Metric[]> {
    const processed: Metric[] = [];

    for (const metric of metrics) {
      processed.push(metric);

      // 카운터 타입인 경우 레이트 계산
      if (metric.type === MetricType.COUNTER) {
        const key = this.getMetricKey(metric);
        const previousValue = this.previousValues.get(key);

        if (previousValue !== undefined) {
          const rate = (metric.value - previousValue) / 
                      (Date.now() - metric.timestamp.getTime()) * 1000;

          processed.push({
            name: `${metric.name}.rate`,
            value: rate,
            timestamp: metric.timestamp,
            tags: metric.tags,
            type: MetricType.GAUGE,
            unit: `${metric.unit || 'units'}/second`
          });
        }

        this.previousValues.set(key, metric.value);
      }
    }

    return processed;
  }

  private getMetricKey(metric: Metric): string {
    const tagStr = Object.entries(metric.tags)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}:${v}`)
      .join(',');
    
    return `${metric.name}:{${tagStr}}`;
  }
}

// 태그 보강 프로세서
export class TagEnrichmentProcessor extends MetricProcessor {
  private enrichmentRules: EnrichmentRule[];

  constructor(rules: EnrichmentRule[]) {
    super();
    this.enrichmentRules = rules;
  }

  async process(metrics: Metric[]): Promise<Metric[]> {
    return Promise.all(metrics.map(async metric => {
      const enrichedTags = { ...metric.tags };

      for (const rule of this.enrichmentRules) {
        if (rule.matches(metric)) {
          Object.assign(enrichedTags, await rule.getTags(metric));
        }
      }

      return {
        ...metric,
        tags: enrichedTags
      };
    }));
  }
}

// 메트릭 집계기
export class MetricAggregator {
  private windows: Map<string, AggregationWindow>;

  constructor(config: AggregationConfig) {
    this.windows = new Map();
    
    // 집계 윈도우 생성
    for (const windowConfig of config.windows) {
      this.windows.set(
        windowConfig.name,
        new AggregationWindow(windowConfig)
      );
    }
  }

  async aggregate(metrics: Metric[]): Promise<Metric[]> {
    const aggregated: Metric[] = [...metrics];

    for (const metric of metrics) {
      // 각 윈도우에서 집계
      for (const [name, window] of this.windows) {
        const agg = await window.aggregate(metric);
        
        if (agg) {
          aggregated.push(...agg);
        }
      }
    }

    return aggregated;
  }
}

// 집계 윈도우
export class AggregationWindow {
  private buffer: Map<string, Metric[]> = new Map();
  private lastFlush: Date = new Date();

  constructor(private config: WindowConfig) {}

  async aggregate(metric: Metric): Promise<Metric[] | null> {
    const key = this.getAggregationKey(metric);
    
    if (!this.buffer.has(key)) {
      this.buffer.set(key, []);
    }

    this.buffer.get(key)!.push(metric);

    // 윈도우 만료 확인
    if (this.shouldFlush()) {
      return this.flush();
    }

    return null;
  }

  private shouldFlush(): boolean {
    const elapsed = Date.now() - this.lastFlush.getTime();
    return elapsed >= this.config.duration;
  }

  private flush(): Metric[] {
    const aggregated: Metric[] = [];

    for (const [key, metrics] of this.buffer) {
      if (metrics.length === 0) continue;

      const values = metrics.map(m => m.value);
      const timestamp = new Date();
      const tags = metrics[0].tags;

      // 집계 통계 계산
      aggregated.push(
        {
          name: `${metrics[0].name}.min`,
          value: Math.min(...values),
          timestamp,
          tags,
          type: MetricType.GAUGE,
          metadata: { window: this.config.name }
        },
        {
          name: `${metrics[0].name}.max`,
          value: Math.max(...values),
          timestamp,
          tags,
          type: MetricType.GAUGE,
          metadata: { window: this.config.name }
        },
        {
          name: `${metrics[0].name}.avg`,
          value: values.reduce((a, b) => a + b, 0) / values.length,
          timestamp,
          tags,
          type: MetricType.GAUGE,
          metadata: { window: this.config.name }
        },
        {
          name: `${metrics[0].name}.count`,
          value: values.length,
          timestamp,
          tags,
          type: MetricType.GAUGE,
          metadata: { window: this.config.name }
        }
      );

      // 백분위수
      const sorted = values.sort((a, b) => a - b);
      const percentiles = [50, 90, 95, 99];
      
      for (const p of percentiles) {
        const index = Math.ceil((p / 100) * sorted.length) - 1;
        aggregated.push({
          name: `${metrics[0].name}.p${p}`,
          value: sorted[index],
          timestamp,
          tags,
          type: MetricType.GAUGE,
          metadata: { window: this.config.name }
        });
      }
    }

    // 버퍼 초기화
    this.buffer.clear();
    this.lastFlush = new Date();

    return aggregated;
  }

  private getAggregationKey(metric: Metric): string {
    const tagStr = Object.entries(metric.tags)
      .filter(([k]) => this.config.groupBy.includes(k))
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}:${v}`)
      .join(',');
    
    return `${metric.name}:{${tagStr}}`;
  }
}

// 메트릭 내보내기
export abstract class MetricExporter {
  abstract async export(metrics: Metric[]): Promise<void>;
}

// Prometheus 내보내기
export class PrometheusExporter extends MetricExporter {
  private registry: PrometheusRegistry;

  constructor(config: PrometheusExporterConfig) {
    super();
    this.registry = new PrometheusRegistry();
  }

  async export(metrics: Metric[]): Promise<void> {
    for (const metric of metrics) {
      const promMetric = this.getOrCreateMetric(metric);
      
      switch (metric.type) {
        case MetricType.COUNTER:
          (promMetric as Counter).inc(metric.value);
          break;
        
        case MetricType.GAUGE:
          (promMetric as Gauge).set(metric.value);
          break;
        
        case MetricType.HISTOGRAM:
          (promMetric as Histogram).observe(metric.value);
          break;
        
        case MetricType.SUMMARY:
          (promMetric as Summary).observe(metric.value);
          break;
      }
    }
  }

  private getOrCreateMetric(metric: Metric): PrometheusMetric {
    const name = metric.name.replace(/\./g, '_');
    const labels = Object.keys(metric.tags);

    let promMetric = this.registry.getSingleMetric(name);

    if (!promMetric) {
      const config = {
        name,
        help: `${metric.name} (${metric.unit || 'units'})`,
        labelNames: labels
      };

      switch (metric.type) {
        case MetricType.COUNTER:
          promMetric = new Counter(config);
          break;
        
        case MetricType.GAUGE:
          promMetric = new Gauge(config);
          break;
        
        case MetricType.HISTOGRAM:
          promMetric = new Histogram({
            ...config,
            buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300]
          });
          break;
        
        case MetricType.SUMMARY:
          promMetric = new Summary({
            ...config,
            percentiles: [0.5, 0.9, 0.95, 0.99]
          });
          break;
      }

      this.registry.registerMetric(promMetric);
    }

    return promMetric;
  }

  getMetrics(): string {
    return this.registry.metrics();
  }
}
```

**검증 기준**:
- [ ] 다양한 메트릭 수집기
- [ ] 메트릭 처리 파이프라인
- [ ] 집계 및 윈도우 처리
- [ ] 다중 내보내기 지원

#### SubTask 5.11.2: 시계열 데이터 저장소
**담당자**: 데이터베이스 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:
```typescript
// backend/src/orchestration/metrics/timeseries_storage.ts
export interface TimeSeriesPoint {
  timestamp: Date;
  value: number;
  tags: Record<string, string>;
}

export interface TimeSeriesQuery {
  metric: string;
  start: Date;
  end: Date;
  tags?: Record<string, string>;
  aggregation?: AggregationFunction;
  groupBy?: string[];
  interval?: string;
  fill?: FillMethod;
}

export class TimeSeriesStorage {
  private influxDB: InfluxDBClient;
  private clickhouse: ClickHouseClient;
  private cache: TimeSeriesCache;
  private compactor: DataCompactor;

  constructor(config: TimeSeriesStorageConfig) {
    this.influxDB = new InfluxDBClient(config.influxdb);
    this.clickhouse = new ClickHouseClient(config.clickhouse);
    this.cache = new TimeSeriesCache(config.cache);
    this.compactor = new DataCompactor(config.compaction);
  }

  async write(
    metric: string,
    points: TimeSeriesPoint[]
  ): Promise<void> {
    // 캐시에 쓰기
    await this.cache.write(metric, points);

    // 배치 쓰기를 위한 버퍼링
    const batches = this.createBatches(points, 5000);

    for (const batch of batches) {
      await Promise.all([
        // InfluxDB에 쓰기 (실시간 쿼리용)
        this.writeToInfluxDB(metric, batch),
        
        // ClickHouse에 쓰기 (장기 보관 및 분석용)
        this.writeToClickHouse(metric, batch)
      ]);
    }
  }

  private async writeToInfluxDB(
    metric: string,
    points: TimeSeriesPoint[]
  ): Promise<void> {
    const writeApi = this.influxDB.getWriteApi();

    for (const point of points) {
      const influxPoint = new Point(metric)
        .timestamp(point.timestamp);

      // 태그 추가
      for (const [key, value] of Object.entries(point.tags)) {
        influxPoint.tag(key, value);
      }

      // 값 추가
      influxPoint.floatField('value', point.value);

      writeApi.writePoint(influxPoint);
    }

    await writeApi.close();
  }

  private async writeToClickHouse(
    metric: string,
    points: TimeSeriesPoint[]
  ): Promise<void> {
    const rows = points.map(point => ({
      metric,
      timestamp: point.timestamp.toISOString(),
      value: point.value,
      tags: point.tags,
      date: point.timestamp.toISOString().split('T')[0]
    }));

    await this.clickhouse.insert({
      table: 'metrics',
      values: rows,
      format: 'JSONEachRow'
    });
  }

  async query(params: TimeSeriesQuery): Promise<TimeSeriesData> {
    // 캐시 확인
    const cached = await this.cache.get(params);
    if (cached) {
      return cached;
    }

    // 쿼리 최적화
    const optimized = this.optimizeQuery(params);

    // 적절한 저장소 선택
    const data = await this.selectStorageAndQuery(optimized);

    // 후처리
    const processed = await this.postProcess(data, params);

    // 캐시에 저장
    await this.cache.set(params, processed);

    return processed;
  }

  private async selectStorageAndQuery(
    query: TimeSeriesQuery
  ): Promise<TimeSeriesData> {
    const timeRange = query.end.getTime() - query.start.getTime();
    const oneDay = 24 * 60 * 60 * 1000;

    if (timeRange <= oneDay) {
      // 최근 데이터는 InfluxDB에서
      return this.queryInfluxDB(query);
    } else if (timeRange <= 30 * oneDay) {
      // 중간 범위는 병렬 쿼리
      const [influxData, clickhouseData] = await Promise.all([
        this.queryInfluxDB(query),
        this.queryClickHouse(query)
      ]);
      
      return this.mergeData(influxData, clickhouseData);
    } else {
      // 장기 데이터는 ClickHouse에서
      return this.queryClickHouse(query);
    }
  }

  private async queryInfluxDB(
    query: TimeSeriesQuery
  ): Promise<TimeSeriesData> {
    const fluxQuery = this.buildFluxQuery(query);
    const queryApi = this.influxDB.getQueryApi();
    const rows: any[] = [];

    await queryApi.collectRows(fluxQuery, (row) => {
      rows.push(row);
    });

    return this.transformInfluxData(rows, query);
  }

  private buildFluxQuery(query: TimeSeriesQuery): string {
    let flux = `
      from(bucket: "metrics")
        |> range(start: ${query.start.toISOString()}, stop: ${query.end.toISOString()})
        |> filter(fn: (r) => r._measurement == "${query.metric}")
    `;

    // 태그 필터
    if (query.tags) {
      for (const [key, value] of Object.entries(query.tags)) {
        flux += `\n        |> filter(fn: (r) => r.${key} == "${value}")`;
      }
    }

    // 집계
    if (query.aggregation && query.interval) {
      flux += `\n        |> aggregateWindow(every: ${query.interval}, fn: ${query.aggregation})`;
    }

    // 그룹화
    if (query.groupBy) {
      flux += `\n        |> group(columns: [${query.groupBy.map(g => `"${g}"`).join(', ')}])`;
    }

    return flux;
  }

  private async queryClickHouse(
    query: TimeSeriesQuery
  ): Promise<TimeSeriesData> {
    const sql = this.buildClickHouseQuery(query);
    const result = await this.clickhouse.query({
      query: sql,
      format: 'JSONEachRow'
    });

    return this.transformClickHouseData(result.data, query);
  }

  private buildClickHouseQuery(query: TimeSeriesQuery): string {
    let sql = 'SELECT ';

    // 시간 버킷팅
    if (query.interval) {
      sql += `toStartOfInterval(timestamp, INTERVAL ${query.interval}) as time, `;
    } else {
      sql += 'timestamp as time, ';
    }

    // 집계 함수
    const aggFunc = query.aggregation || 'avg';
    sql += `${aggFunc}(value) as value`;

    // 그룹화 컬럼
    if (query.groupBy) {
      sql += `, ${query.groupBy.map(g => `tags['${g}'] as ${g}`).join(', ')}`;
    }

    sql += `
      FROM metrics
      WHERE metric = '${query.metric}'
        AND timestamp >= '${query.start.toISOString()}'
        AND timestamp <= '${query.end.toISOString()}'
    `;

    // 태그 필터
    if (query.tags) {
      for (const [key, value] of Object.entries(query.tags)) {
        sql += `\n        AND tags['${key}'] = '${value}'`;
      }
    }

    // GROUP BY
    if (query.interval || query.groupBy) {
      sql += '\n      GROUP BY time';
      if (query.groupBy) {
        sql += `, ${query.groupBy.join(', ')}`;
      }
    }

    sql += '\n      ORDER BY time ASC';

    return sql;
  }

  async downsample(
    metric: string,
    retention: RetentionPolicy
  ): Promise<void> {
    const rules = retention.downsamplingRules;

    for (const rule of rules) {
      await this.applyDownsamplingRule(metric, rule);
    }
  }

  private async applyDownsamplingRule(
    metric: string,
    rule: DownsamplingRule
  ): Promise<void> {
    const cutoffTime = new Date(Date.now() - rule.after);

    // 원본 데이터 쿼리
    const data = await this.query({
      metric,
      start: new Date(0),
      end: cutoffTime,
      interval: rule.interval,
      aggregation: rule.aggregation
    });

    // 다운샘플된 테이블에 쓰기
    const downsampledMetric = `${metric}_${rule.interval}`;
    await this.write(downsampledMetric, data.points);

    // 원본 데이터 삭제 (선택적)
    if (rule.deleteOriginal) {
      await this.deleteData(metric, new Date(0), cutoffTime);
    }
  }

  async compact(): Promise<CompactionResult> {
    return this.compactor.compact({
      tables: ['metrics'],
      strategy: 'time-based',
      settings: {
        chunkSize: '1d',
        compressionLevel: 9,
        deduplication: true
      }
    });
  }
}

// 시계열 캐시
export class TimeSeriesCache {
  private redis: RedisClient;
  private memcached: MemcachedClient;
  private localCache: LRUCache<string, TimeSeriesData>;

  constructor(config: CacheConfig) {
    this.redis = new RedisClient(config.redis);
    this.memcached = new MemcachedClient(config.memcached);
    this.localCache = new LRUCache({ max: 1000 });
  }

  async get(query: TimeSeriesQuery): Promise<TimeSeriesData | null> {
    const key = this.generateCacheKey(query);

    // L1 캐시 (로컬)
    const local = this.localCache.get(key);
    if (local) return local;

    // L2 캐시 (Memcached)
    const memcached = await this.memcached.get(key);
    if (memcached) {
      this.localCache.set(key, memcached);
      return memcached;
    }

    // L3 캐시 (Redis)
    const redis = await this.redis.get(key);
    if (redis) {
      const data = JSON.parse(redis);
      this.localCache.set(key, data);
      await this.memcached.set(key, data, 300); // 5분
      return data;
    }

    return null;
  }

  async set(
    query: TimeSeriesQuery,
    data: TimeSeriesData
  ): Promise<void> {
    const key = this.generateCacheKey(query);
    const ttl = this.calculateTTL(query);

    // 모든 레벨에 저장
    this.localCache.set(key, data);
    await this.memcached.set(key, data, ttl);
    await this.redis.setex(key, ttl, JSON.stringify(data));
  }

  private generateCacheKey(query: TimeSeriesQuery): string {
    const parts = [
      query.metric,
      query.start.getTime(),
      query.end.getTime(),
      query.aggregation || 'none',
      query.interval || 'none',
      JSON.stringify(query.tags || {}),
      (query.groupBy || []).join(',')
    ];

    return crypto
      .createHash('md5')
      .update(parts.join(':'))
      .digest('hex');
  }

  private calculateTTL(query: TimeSeriesQuery): number {
    const now = Date.now();
    const queryEnd = query.end.getTime();

    if (queryEnd < now - 86400000) { // 1일 이상 과거
      return 3600; // 1시간
    } else if (queryEnd < now) { // 과거 데이터
      return 300; // 5분
    } else { // 실시간 데이터
      return 60; // 1분
    }
  }
}

// 데이터 압축기
export class DataCompactor {
  private compressionEngine: CompressionEngine;
  
  constructor(config: CompactionConfig) {
    this.compressionEngine = new CompressionEngine(config.compression);
  }

  async compact(options: CompactionOptions): Promise<CompactionResult> {
    const result: CompactionResult = {
      tablesCompacted: [],
      spaceSaved: 0,
      duration: 0
    };

    const startTime = Date.now();

    for (const table of options.tables) {
      const tableResult = await this.compactTable(table, options);
      result.tablesCompacted.push(tableResult);
      result.spaceSaved += tableResult.spaceSaved;
    }

    result.duration = Date.now() - startTime;
    return result;
  }

  private async compactTable(
    table: string,
    options: CompactionOptions
  ): Promise<TableCompactionResult> {
    const originalSize = await this.getTableSize(table);

    // 1. 중복 제거
    if (options.settings.deduplication) {
      await this.deduplicateData(table);
    }

    // 2. 파티션 병합
    await this.mergePartitions(table, options.settings.chunkSize);

    // 3. 압축
    await this.compressData(table, options.settings.compressionLevel);

    const newSize = await this.getTableSize(table);

    return {
      table,
      originalSize,
      newSize,
      spaceSaved: originalSize - newSize,
      compressionRatio: newSize / originalSize
    };
  }

  private async deduplicateData(table: string): Promise<void> {
    // ClickHouse의 ReplacingMergeTree 활용
    const sql = `
      OPTIMIZE TABLE ${table} 
      FINAL 
      DEDUPLICATE BY metric, timestamp, tags
    `;

    await this.clickhouse.query({ query: sql });
  }

  private async mergePartitions(
    table: string,
    chunkSize: string
  ): Promise<void> {
    const sql = `
      ALTER TABLE ${table}
      MODIFY SETTING 
        merge_max_block_size = ${this.parseChunkSize(chunkSize)}
    `;

    await this.clickhouse.query({ query: sql });

    // 강제 병합 트리거
    await this.clickhouse.query({
      query: `OPTIMIZE TABLE ${table} PARTITION tuple()`
    });
  }

  private async compressData(
    table: string,
    level: number
  ): Promise<void> {
    const codec = level > 7 ? 'ZSTD' : 'LZ4';
    
    const sql = `
      ALTER TABLE ${table}
      MODIFY COLUMN value 
      CODEC(${codec}(${level}))
    `;

    await this.clickhouse.query({ query: sql });
  }
}

// 시계열 데이터 분석
export class TimeSeriesAnalyzer {
  private statisticsCalculator: StatisticsCalculator;
  private anomalyDetector: TimeSeriesAnomalyDetector;
  private forecaster: TimeSeriesForecaster;

  async analyze(
    data: TimeSeriesData,
    options: AnalysisOptions = {}
  ): Promise<TimeSeriesAnalysis> {
    // 기본 통계
    const statistics = await this.statisticsCalculator.calculate(data);

    // 이상치 감지
    const anomalies = await this.anomalyDetector.detect(data, {
      method: options.anomalyMethod || 'isolation-forest',
      sensitivity: options.sensitivity || 0.95
    });

    // 예측 (옵션)
    let forecast: TimeSeriesForecast | undefined;
    if (options.includeForecast) {
      forecast = await this.forecaster.forecast(data, {
        horizon: options.forecastHorizon || 24,
        method: options.forecastMethod || 'prophet'
      });
    }

    // 패턴 분석
    const patterns = await this.analyzePatterns(data);

    return {
      statistics,
      anomalies,
      forecast,
      patterns,
      quality: this.assessDataQuality(data)
    };
  }

  private async analyzePatterns(
    data: TimeSeriesData
  ): Promise<PatternAnalysis> {
    return {
      trend: await this.detectTrend(data),
      seasonality: await this.detectSeasonality(data),
      changePoints: await this.detectChangePoints(data),
      cycles: await this.detectCycles(data)
    };
  }

  private assessDataQuality(data: TimeSeriesData): DataQuality {
    const points = data.points;
    const timestamps = points.map(p => p.timestamp.getTime());
    
    // 간격 분석
    const intervals = [];
    for (let i = 1; i < timestamps.length; i++) {
      intervals.push(timestamps[i] - timestamps[i - 1]);
    }

    const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    const intervalStdDev = Math.sqrt(
      intervals.reduce((sum, i) => sum + Math.pow(i - avgInterval, 2), 0) / intervals.length
    );

    // 결측값 감지
    const expectedPoints = Math.floor(
      (data.end.getTime() - data.start.getTime()) / avgInterval
    );
    const missingRatio = 1 - (points.length / expectedPoints);

    return {
      completeness: 1 - missingRatio,
      consistency: 1 - (intervalStdDev / avgInterval),
      validity: this.calculateValidity(points),
      timeliness: this.calculateTimeliness(data.end)
    };
  }
}
```

**검증 기준**:
- [ ] 이중 저장소 구조 (InfluxDB + ClickHouse)
- [ ] 다층 캐싱 시스템
- [ ] 데이터 압축 및 다운샘플링
- [ ] 시계열 분석 기능

#### SubTask 5.11.3: 성능 분석 엔진
**담당자**: 성능 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:
```typescript
// backend/src/orchestration/metrics/performance_analysis.ts
export interface PerformanceMetrics {
  latency: LatencyMetrics;
  throughput: ThroughputMetrics;
  errorRate: ErrorMetrics;
  saturation: SaturationMetrics;
  availability: AvailabilityMetrics;
}

export class PerformanceAnalysisEngine {
  private metricsStore: TimeSeriesStorage;
  private analyzer: MetricsAnalyzer;
  private baselineCalculator: BaselineCalculator;
  private correlationEngine: CorrelationEngine;

  constructor(config: AnalysisEngineConfig) {
    this.metricsStore = new TimeSeriesStorage(config.storage);
    this.analyzer = new MetricsAnalyzer();
    this.baselineCalculator = new BaselineCalculator();
    this.correlationEngine = new CorrelationEngine();
  }

  async analyzePerformance(
    timeRange: TimeRange,
    options: AnalysisOptions = {}
  ): Promise<PerformanceAnalysisResult> {
    // 1. 메트릭 수집
    const metrics = await this.collectMetrics(timeRange);

    // 2. 기준선 계산
    const baselines = await this.baselineCalculator.calculate(
      metrics,
      options.baselinePeriod || 7 // 7일
    );

    // 3. 이상 감지
    const anomalies = await this.detectAnomalies(metrics, baselines);

    // 4. 성능 점수 계산
    const scores = await this.calculatePerformanceScores(metrics);

    // 5. 병목 지점 식별
    const bottlenecks = await this.identifyBottlenecks(metrics);

    // 6. 상관 관계 분석
    const correlations = await this.correlationEngine.analyze(metrics);

    // 7. 추세 분석
    const trends = await this.analyzeTrends(metrics, timeRange);

    // 8. 권장 사항 생성
    const recommendations = await this.generateRecommendations({
      metrics,
      anomalies,
      bottlenecks,
      correlations,
      trends
    });

    return {
      summary: this.generateSummary(metrics),
      scores,
      anomalies,
      bottlenecks,
      correlations,
      trends,
      recommendations
    };
  }

  private async collectMetrics(
    timeRange: TimeRange
  ): Promise<PerformanceMetrics> {
    const [latency, throughput, errorRate, saturation, availability] = 
      await Promise.all([
        this.collectLatencyMetrics(timeRange),
        this.collectThroughputMetrics(timeRange),
        this.collectErrorMetrics(timeRange),
        this.collectSaturationMetrics(timeRange),
        this.collectAvailabilityMetrics(timeRange)
      ]);

    return {
      latency,
      throughput,
      errorRate,
      saturation,
      availability
    };
  }

  private async collectLatencyMetrics(
    timeRange: TimeRange
  ): Promise<LatencyMetrics> {
    const queries = [
      // API 레이턴시
      {
        metric: 'api.requests.duration',
        aggregation: 'percentile',
        percentiles: [50, 90, 95, 99]
      },
      // 워크플로우 레이턴시
      {
        metric: 'workflow.execution.duration',
        aggregation: 'percentile',
        percentiles: [50, 90, 95, 99]
      },
      // 태스크 레이턴시
      {
        metric: 'task.execution.duration',
        aggregation: 'percentile',
        percentiles: [50, 90, 95, 99]
      }
    ];

    const results = await Promise.all(
      queries.map(q => this.metricsStore.query({
        ...q,
        start: timeRange.start,
        end: timeRange.end
      }))
    );

    return {
      api: this.processLatencyData(results[0]),
      workflow: this.processLatencyData(results[1]),
      task: this.processLatencyData(results[2])
    };
  }

  private async detectAnomalies(
    metrics: PerformanceMetrics,
    baselines: PerformanceBaselines
  ): Promise<PerformanceAnomaly[]> {
    const anomalies: PerformanceAnomaly[] = [];

    // 레이턴시 이상
    const latencyAnomalies = await this.detectLatencyAnomalies(
      metrics.latency,
      baselines.latency
    );
    anomalies.push(...latencyAnomalies);

    // 처리량 이상
    const throughputAnomalies = await this.detectThroughputAnomalies(
      metrics.throughput,
      baselines.throughput
    );
    anomalies.push(...throughputAnomalies);

    // 에러율 이상
    const errorAnomalies = await this.detectErrorAnomalies(
      metrics.errorRate,
      baselines.errorRate
    );
    anomalies.push(...errorAnomalies);

    // 상관 관계 기반 이상
    const correlationAnomalies = await this.detectCorrelationAnomalies(metrics);
    anomalies.push(...correlationAnomalies);

    return anomalies;
  }

  private async detectLatencyAnomalies(
    current: LatencyMetrics,
    baseline: LatencyBaseline
  ): Promise<PerformanceAnomaly[]> {
    const anomalies: PerformanceAnomaly[] = [];

    // P95 레이턴시 비교
    for (const [component, data] of Object.entries(current)) {
      const baselineP95 = baseline[component]?.p95 || 0;
      const currentP95 = data.p95;

      if (currentP95 > baselineP95 * 1.5) { // 50% 증가
        anomalies.push({
          type: 'latency_spike',
          component,
          severity: this.calculateSeverity(currentP95, baselineP95),
          current: currentP95,
          baseline: baselineP95,
          deviation: (currentP95 - baselineP95) / baselineP95,
          timestamp: new Date(),
          description: `${component} P95 latency increased by ${Math.round((currentP95 / baselineP95 - 1) * 100)}%`
        });
      }
    }

    return anomalies;
  }

  private async identifyBottlenecks(
    metrics: PerformanceMetrics
  ): Promise<Bottleneck[]> {
    const bottlenecks: Bottleneck[] = [];

    // 1. CPU 병목
    if (metrics.saturation.cpu > 80) {
      bottlenecks.push({
        type: 'cpu',
        severity: 'high',
        component: 'system',
        metric: 'cpu_utilization',
        value: metrics.saturation.cpu,
        threshold: 80,
        impact: await this.estimateImpact('cpu', metrics.saturation.cpu),
        recommendations: [
          'Scale up CPU resources',
          'Optimize CPU-intensive operations',
          'Enable horizontal scaling'
        ]
      });
    }

    // 2. 메모리 병목
    if (metrics.saturation.memory > 85) {
      bottlenecks.push({
        type: 'memory',
        severity: 'high',
        component: 'system',
        metric: 'memory_utilization',
        value: metrics.saturation.memory,
        threshold: 85,
        impact: await this.estimateImpact('memory', metrics.saturation.memory),
        recommendations: [
          'Increase memory allocation',
          'Implement memory caching',
          'Review memory leaks'
        ]
      });
    }

    // 3. I/O 병목
    if (metrics.saturation.io > 70) {
      bottlenecks.push({
        type: 'io',
        severity: 'medium',
        component: 'storage',
        metric: 'io_utilization',
        value: metrics.saturation.io,
        threshold: 70,
        impact: await this.estimateImpact('io', metrics.saturation.io),
        recommendations: [
          'Optimize database queries',
          'Implement read replicas',
          'Use SSD storage'
        ]
      });
    }

    // 4. 네트워크 병목
    if (metrics.saturation.network > 75) {
      bottlenecks.push({
        type: 'network',
        severity: 'medium',
        component: 'network',
        metric: 'network_utilization',
        value: metrics.saturation.network,
        threshold: 75,
        impact: await this.estimateImpact('network', metrics.saturation.network),
        recommendations: [
          'Implement CDN',
          'Enable compression',
          'Optimize payload sizes'
        ]
      });
    }

    // 5. 애플리케이션 레벨 병목
    const appBottlenecks = await this.identifyApplicationBottlenecks(metrics);
    bottlenecks.push(...appBottlenecks);

    return bottlenecks.sort((a, b) => b
