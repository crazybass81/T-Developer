프로젝트 지식을 확인하여 Phase 6의 API 게이트웨이 구축 (Tasks 6.1-6.5)에 대한 SubTask 리스트와 작업지시서를 작성하겠습니다.## Phase 6: API 게이트웨이 구축 (Tasks 6.1-6.5) - SubTask 리스트 및 작업지시서

### 📋 SubTask 전체 리스트

#### Task 6.1: API Gateway 아키텍처 설계
- **SubTask 6.1.1**: 게이트웨이 패턴 선택 및 설계
- **SubTask 6.1.2**: 마이크로서비스 통합 아키텍처
- **SubTask 6.1.3**: 게이트웨이 계층 구조 설계
- **SubTask 6.1.4**: 고가용성 및 장애 복구 설계

#### Task 6.2: 라우팅 및 엔드포인트 관리
- **SubTask 6.2.1**: 동적 라우팅 엔진 구현
- **SubTask 6.2.2**: 엔드포인트 레지스트리 시스템
- **SubTask 6.2.3**: 경로 매칭 및 파라미터 처리
- **SubTask 6.2.4**: 라우팅 규칙 관리 인터페이스

#### Task 6.3: 요청/응답 변환 레이어
- **SubTask 6.3.1**: 요청 파서 및 검증기
- **SubTask 6.3.2**: 프로토콜 변환 엔진
- **SubTask 6.3.3**: 응답 포맷터 및 압축
- **SubTask 6.3.4**: 데이터 변환 파이프라인

#### Task 6.4: API 버전 관리 시스템
- **SubTask 6.4.1**: 버전 라우팅 전략 구현
- **SubTask 6.4.2**: 하위 호환성 관리
- **SubTask 6.4.3**: 버전 마이그레이션 도구
- **SubTask 6.4.4**: 버전별 문서 자동 생성

#### Task 6.5: 게이트웨이 로드 밸런싱
- **SubTask 6.5.1**: 로드 밸런싱 알고리즘 구현
- **SubTask 6.5.2**: 헬스 체크 및 서비스 디스커버리
- **SubTask 6.5.3**: 트래픽 분산 정책 엔진
- **SubTask 6.5.4**: 자동 스케일링 통합

---

## 📝 세부 작업지시서

### Task 6.1: API Gateway 아키텍처 설계

#### SubTask 6.1.1: 게이트웨이 패턴 선택 및 설계

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api-gateway/architecture/gateway-pattern.ts
export enum GatewayPattern {
  BFF = 'Backend for Frontend',
  API_AGGREGATION = 'API Aggregation',
  PROXY = 'Simple Proxy',
  HYBRID = 'Hybrid Pattern'
}

export interface GatewayArchitecture {
  pattern: GatewayPattern;
  layers: GatewayLayer[];
  components: GatewayComponent[];
  integrations: ServiceIntegration[];
}

export class GatewayArchitectureDesigner {
  private pattern: GatewayPattern;
  private config: GatewayConfig;
  
  constructor(config: GatewayConfig) {
    this.config = config;
    this.pattern = this.selectOptimalPattern();
  }
  
  private selectOptimalPattern(): GatewayPattern {
    // T-Developer의 9개 에이전트를 위한 최적 패턴 선택
    if (this.config.clientTypes.length > 1) {
      return GatewayPattern.BFF; // 다양한 클라이언트 지원
    }
    if (this.config.services.length > 5) {
      return GatewayPattern.API_AGGREGATION; // 마이크로서비스 집합
    }
    return GatewayPattern.HYBRID;
  }
  
  async designArchitecture(): Promise<GatewayArchitecture> {
    return {
      pattern: this.pattern,
      layers: [
        {
          name: 'Security Layer',
          responsibilities: ['Authentication', 'Authorization', 'Rate Limiting'],
          components: ['JWT Validator', 'OAuth Provider', 'Rate Limiter']
        },
        {
          name: 'Routing Layer',
          responsibilities: ['Path Matching', 'Load Balancing', 'Service Discovery'],
          components: ['Router', 'Load Balancer', 'Service Registry']
        },
        {
          name: 'Transformation Layer',
          responsibilities: ['Request Transformation', 'Response Aggregation', 'Protocol Translation'],
          components: ['Request Parser', 'Response Formatter', 'Protocol Adapter']
        },
        {
          name: 'Integration Layer',
          responsibilities: ['Service Communication', 'Circuit Breaking', 'Retry Logic'],
          components: ['HTTP Client', 'Circuit Breaker', 'Retry Manager']
        }
      ],
      components: this.defineComponents(),
      integrations: this.defineIntegrations()
    };
  }
  
  private defineComponents(): GatewayComponent[] {
    return [
      {
        name: 'Agent Orchestrator',
        type: 'Core',
        description: '9개 에이전트 간 통신 조정',
        interfaces: ['REST', 'GraphQL', 'WebSocket']
      },
      {
        name: 'Request Router',
        type: 'Routing',
        description: '요청을 적절한 에이전트로 라우팅',
        interfaces: ['HTTP', 'WebSocket']
      },
      {
        name: 'Response Aggregator',
        type: 'Processing',
        description: '여러 에이전트 응답 집계',
        interfaces: ['JSON', 'Protocol Buffers']
      }
    ];
  }
}
```

**검증 기준**:
- [ ] 9개 에이전트 통합 지원
- [ ] 확장 가능한 아키텍처
- [ ] 성능 최적화 고려
- [ ] 장애 격리 설계

#### SubTask 6.1.2: 마이크로서비스 통합 아키텍처

**담당자**: 통합 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api_gateway/integration/microservice_integration.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
from enum import Enum

@dataclass
class ServiceEndpoint:
    name: str
    url: str
    health_check: str
    timeout: int
    retry_policy: RetryPolicy
    circuit_breaker_config: CircuitBreakerConfig

class ServiceIntegrationType(Enum):
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"
    EVENT_DRIVEN = "event"
    STREAMING = "stream"

class MicroserviceIntegrator:
    """9개 에이전트 서비스 통합 관리"""
    
    def __init__(self):
        self.services = self._initialize_services()
        self.discovery_client = ServiceDiscoveryClient()
        self.circuit_breakers = {}
        self.connection_pools = {}
        
    def _initialize_services(self) -> Dict[str, ServiceEndpoint]:
        """T-Developer 에이전트 서비스 초기화"""
        return {
            'nl_input': ServiceEndpoint(
                name='NL Input Agent',
                url='http://nl-input-service:8001',
                health_check='/health',
                timeout=30000,
                retry_policy=RetryPolicy(max_attempts=3, backoff='exponential'),
                circuit_breaker_config=CircuitBreakerConfig(
                    failure_threshold=5,
                    timeout=60000,
                    half_open_requests=3
                )
            ),
            'ui_selection': ServiceEndpoint(
                name='UI Selection Agent',
                url='http://ui-selection-service:8002',
                health_check='/health',
                timeout=20000,
                retry_policy=RetryPolicy(max_attempts=2),
                circuit_breaker_config=CircuitBreakerConfig()
            ),
            'parser': ServiceEndpoint(
                name='Parser Agent',
                url='http://parser-service:8003',
                health_check='/health',
                timeout=25000,
                retry_policy=RetryPolicy(max_attempts=3),
                circuit_breaker_config=CircuitBreakerConfig()
            ),
            # ... 나머지 6개 에이전트
        }
    
    async def integrate_service(
        self, 
        service_name: str,
        integration_type: ServiceIntegrationType
    ) -> ServiceConnection:
        """서비스 통합 설정"""
        
        service = self.services.get(service_name)
        if not service:
            raise ServiceNotFoundError(f"Service {service_name} not found")
        
        # 서비스 디스커버리로 실제 엔드포인트 확인
        actual_endpoint = await self.discovery_client.discover(service_name)
        if actual_endpoint:
            service.url = actual_endpoint
        
        # Circuit Breaker 설정
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service.circuit_breaker_config
            )
        
        # Connection Pool 설정
        if service_name not in self.connection_pools:
            self.connection_pools[service_name] = ConnectionPool(
                max_connections=100,
                min_connections=10,
                connection_timeout=5000
            )
        
        # 통합 타입별 설정
        if integration_type == ServiceIntegrationType.STREAMING:
            return await self._setup_streaming_connection(service)
        elif integration_type == ServiceIntegrationType.EVENT_DRIVEN:
            return await self._setup_event_connection(service)
        else:
            return await self._setup_http_connection(service)
    
    async def _setup_streaming_connection(
        self, 
        service: ServiceEndpoint
    ) -> StreamingConnection:
        """WebSocket/SSE 스트리밍 연결"""
        return StreamingConnection(
            url=service.url.replace('http://', 'ws://') + '/stream',
            heartbeat_interval=30000,
            reconnect_policy=ReconnectPolicy(
                max_attempts=5,
                initial_delay=1000,
                max_delay=30000
            )
        )
```

**검증 기준**:
- [ ] 모든 에이전트 서비스 통합
- [ ] 서비스 디스커버리 구현
- [ ] Circuit Breaker 패턴 적용
- [ ] Connection Pool 관리

#### SubTask 6.1.3: 게이트웨이 계층 구조 설계

**담당자**: 소프트웨어 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api-gateway/layers/layer-architecture.ts
export interface LayerDefinition {
  name: string;
  order: number;
  responsibilities: string[];
  middlewares: Middleware[];
  errorHandlers: ErrorHandler[];
}

export class GatewayLayerArchitecture {
  private layers: Map<string, LayerDefinition>;
  
  constructor() {
    this.layers = new Map();
    this.initializeLayers();
  }
  
  private initializeLayers(): void {
    // 1. 진입점 계층
    this.addLayer({
      name: 'Entry Layer',
      order: 1,
      responsibilities: [
        'Request reception',
        'Initial validation',
        'Request ID generation',
        'Request logging'
      ],
      middlewares: [
        new RequestIdMiddleware(),
        new RequestLoggerMiddleware(),
        new RequestValidationMiddleware()
      ],
      errorHandlers: [
        new BadRequestHandler(),
        new ValidationErrorHandler()
      ]
    });
    
    // 2. 보안 계층
    this.addLayer({
      name: 'Security Layer',
      order: 2,
      responsibilities: [
        'Authentication',
        'Authorization',
        'Rate limiting',
        'DDoS protection'
      ],
      middlewares: [
        new AuthenticationMiddleware(),
        new AuthorizationMiddleware(),
        new RateLimitMiddleware(),
        new DDoSProtectionMiddleware()
      ],
      errorHandlers: [
        new UnauthorizedHandler(),
        new ForbiddenHandler(),
        new RateLimitExceededHandler()
      ]
    });
    
    // 3. 변환 계층
    this.addLayer({
      name: 'Transformation Layer',
      order: 3,
      responsibilities: [
        'Request transformation',
        'Protocol conversion',
        'Data validation',
        'Schema validation'
      ],
      middlewares: [
        new RequestTransformerMiddleware(),
        new ProtocolConverterMiddleware(),
        new SchemaValidatorMiddleware()
      ],
      errorHandlers: [
        new TransformationErrorHandler(),
        new SchemaValidationErrorHandler()
      ]
    });
    
    // 4. 라우팅 계층
    this.addLayer({
      name: 'Routing Layer',
      order: 4,
      responsibilities: [
        'Path matching',
        'Service resolution',
        'Load balancing',
        'Request forwarding'
      ],
      middlewares: [
        new PathMatcherMiddleware(),
        new ServiceResolverMiddleware(),
        new LoadBalancerMiddleware(),
        new RequestForwarderMiddleware()
      ],
      errorHandlers: [
        new ServiceNotFoundHandler(),
        new ServiceUnavailableHandler()
      ]
    });
    
    // 5. 통합 계층
    this.addLayer({
      name: 'Integration Layer',
      order: 5,
      responsibilities: [
        'Service communication',
        'Response aggregation',
        'Error handling',
        'Retry logic'
      ],
      middlewares: [
        new ServiceClientMiddleware(),
        new ResponseAggregatorMiddleware(),
        new RetryMiddleware(),
        new CircuitBreakerMiddleware()
      ],
      errorHandlers: [
        new ServiceTimeoutHandler(),
        new CircuitOpenHandler()
      ]
    });
    
    // 6. 응답 계층
    this.addLayer({
      name: 'Response Layer',
      order: 6,
      responsibilities: [
        'Response formatting',
        'Response caching',
        'Compression',
        'Response logging'
      ],
      middlewares: [
        new ResponseFormatterMiddleware(),
        new ResponseCacheMiddleware(),
        new CompressionMiddleware(),
        new ResponseLoggerMiddleware()
      ],
      errorHandlers: [
        new InternalServerErrorHandler(),
        new GenericErrorHandler()
      ]
    });
  }
  
  async processRequest(request: GatewayRequest): Promise<GatewayResponse> {
    let context = new RequestContext(request);
    
    // 순서대로 각 계층 처리
    const sortedLayers = Array.from(this.layers.values())
      .sort((a, b) => a.order - b.order);
    
    for (const layer of sortedLayers) {
      try {
        context = await this.processLayer(layer, context);
      } catch (error) {
        return await this.handleLayerError(layer, error, context);
      }
    }
    
    return context.response;
  }
}
```

**검증 기준**:
- [ ] 명확한 계층 분리
- [ ] 각 계층 책임 정의
- [ ] 에러 처리 전략
- [ ] 미들웨어 체인 구성

#### SubTask 6.1.4: 고가용성 및 장애 복구 설계

**담당자**: 인프라 아키텍트  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/api_gateway/ha/high_availability.py
from typing import List, Dict, Optional, Set
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class HAConfiguration:
    """고가용성 구성"""
    cluster_size: int = 3
    min_healthy_nodes: int = 2
    health_check_interval: int = 5000  # ms
    failover_timeout: int = 30000  # ms
    data_sync_interval: int = 1000  # ms
    leader_election_timeout: int = 5000  # ms

class HighAvailabilityManager:
    """API Gateway 고가용성 관리"""
    
    def __init__(self, config: HAConfiguration):
        self.config = config
        self.cluster_nodes: Dict[str, GatewayNode] = {}
        self.leader_node: Optional[str] = None
        self.state_store = DistributedStateStore()
        self.health_monitor = HealthMonitor()
        self.failover_manager = FailoverManager()
        
    async def initialize_cluster(self) -> None:
        """HA 클러스터 초기화"""
        
        # 1. 클러스터 노드 초기화
        for i in range(self.config.cluster_size):
            node = GatewayNode(
                id=f"gateway-node-{i}",
                role=NodeRole.FOLLOWER,
                status=NodeStatus.INITIALIZING
            )
            self.cluster_nodes[node.id] = node
            
        # 2. 리더 선출
        await self.elect_leader()
        
        # 3. 상태 동기화 시작
        asyncio.create_task(self.sync_cluster_state())
        
        # 4. 헬스 체크 시작
        asyncio.create_task(self.monitor_health())
        
    async def elect_leader(self) -> None:
        """리더 노드 선출 (Raft 알고리즘)"""
        
        election = LeaderElection(
            nodes=list(self.cluster_nodes.values()),
            timeout=self.config.leader_election_timeout
        )
        
        leader_id = await election.elect()
        self.leader_node = leader_id
        
        # 리더 노드 역할 업데이트
        if leader_id in self.cluster_nodes:
            self.cluster_nodes[leader_id].role = NodeRole.LEADER
            
        # 이벤트 발생
        await self.emit_event(LeaderElectedEvent(leader_id))
        
    async def handle_node_failure(self, failed_node_id: str) -> None:
        """노드 장애 처리"""
        
        failed_node = self.cluster_nodes.get(failed_node_id)
        if not failed_node:
            return
            
        # 1. 노드 상태 업데이트
        failed_node.status = NodeStatus.FAILED
        failed_node.last_failure = datetime.now()
        
        # 2. 리더 노드 장애 시 재선출
        if failed_node_id == self.leader_node:
            await self.elect_leader()
            
        # 3. 트래픽 재분배
        await self.redistribute_traffic(failed_node_id)
        
        # 4. 장애 복구 시작
        asyncio.create_task(self.recover_failed_node(failed_node_id))
        
    async def redistribute_traffic(self, excluded_node: str) -> None:
        """트래픽 재분배"""
        
        healthy_nodes = [
            node for node_id, node in self.cluster_nodes.items()
            if node_id != excluded_node and node.status == NodeStatus.HEALTHY
        ]
        
        if len(healthy_nodes) < self.config.min_healthy_nodes:
            # 최소 노드 수 미달 시 경고
            await self.emit_alert(ClusterDegradedAlert(
                healthy_count=len(healthy_nodes),
                required_count=self.config.min_healthy_nodes
            ))
            
        # 로드 밸런서 업데이트
        await self.update_load_balancer(healthy_nodes)
        
    async def recover_failed_node(self, node_id: str) -> None:
        """장애 노드 복구"""
        
        recovery_strategy = NodeRecoveryStrategy(
            max_attempts=5,
            backoff_multiplier=2,
            initial_delay=5000
        )
        
        attempt = 0
        while attempt < recovery_strategy.max_attempts:
            try:
                # 1. 노드 재시작
                await self.restart_node(node_id)
                
                # 2. 헬스 체크
                if await self.health_monitor.check_node(node_id):
                    # 3. 클러스터 재합류
                    await self.rejoin_cluster(node_id)
                    
                    # 4. 상태 동기화
                    await self.sync_node_state(node_id)
                    
                    # 5. 트래픽 재활성화
                    await self.enable_traffic(node_id)
                    
                    return
                    
            except Exception as e:
                attempt += 1
                delay = recovery_strategy.get_delay(attempt)
                await asyncio.sleep(delay / 1000)
                
        # 복구 실패 시 노드 제거
        await self.remove_node(node_id)
        
    async def sync_cluster_state(self) -> None:
        """클러스터 상태 동기화"""
        
        while True:
            try:
                # 분산 상태 저장소 동기화
                state = await self.collect_cluster_state()
                await self.state_store.update(state)
                
                # 각 노드에 상태 전파
                await self.propagate_state(state)
                
            except Exception as e:
                await self.handle_sync_error(e)
                
            await asyncio.sleep(self.config.data_sync_interval / 1000)
```

**검증 기준**:
- [ ] 클러스터 구성 및 관리
- [ ] 리더 선출 메커니즘
- [ ] 자동 장애 복구
- [ ] 상태 동기화 전략

---

### Task 6.2: 라우팅 및 엔드포인트 관리

#### SubTask 6.2.1: 동적 라우팅 엔진 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/api-gateway/routing/dynamic-router.ts
export interface Route {
  id: string;
  path: string;
  method: string | string[];
  handler: RouteHandler;
  middleware?: Middleware[];
  metadata?: RouteMetadata;
  priority?: number;
  constraints?: RouteConstraints;
}

export class DynamicRoutingEngine {
  private routes: Map<string, Route> = new Map();
  private routeTree: RadixTree<Route>;
  private dynamicRoutes: Set<string> = new Set();
  
  constructor() {
    this.routeTree = new RadixTree();
    this.initializeDefaultRoutes();
  }
  
  async addRoute(route: Route): Promise<void> {
    // 경로 정규화
    const normalizedPath = this.normalizePath(route.path);
    
    // 경로 트리에 추가
    this.routeTree.insert(normalizedPath, route);
    
    // 라우트 맵에 추가
    this.routes.set(route.id, route);
    
    // 동적 라우트 표시
    if (this.isDynamicRoute(route)) {
      this.dynamicRoutes.add(route.id);
    }
    
    // 라우트 캐시 무효화
    await this.invalidateRouteCache();
  }
  
  async removeRoute(routeId: string): Promise<void> {
    const route = this.routes.get(routeId);
    if (!route) return;
    
    // 트리에서 제거
    this.routeTree.remove(route.path);
    
    // 맵에서 제거
    this.routes.delete(routeId);
    this.dynamicRoutes.delete(routeId);
    
    // 캐시 무효화
    await this.invalidateRouteCache();
  }
  
  async match(request: IncomingRequest): Promise<RouteMatch | null> {
    const path = request.path;
    const method = request.method;
    
    // 1. 정확한 매칭 시도
    let matches = this.routeTree.lookup(path);
    
    // 2. 와일드카드 매칭
    if (!matches.length) {
      matches = this.routeTree.lookupWildcard(path);
    }
    
    // 3. 메서드 필터링
    matches = matches.filter(route => 
      this.matchMethod(route, method)
    );
    
    // 4. 제약 조건 검증
    matches = await this.validateConstraints(matches, request);
    
    // 5. 우선순위 정렬
    matches.sort((a, b) => (b.priority || 0) - (a.priority || 0));
    
    if (matches.length === 0) {
      return null;
    }
    
    const selectedRoute = matches[0];
    
    // 6. 파라미터 추출
    const params = this.extractParams(selectedRoute.path, path);
    
    return {
      route: selectedRoute,
      params,
      query: request.query,
      metadata: await this.enrichMetadata(selectedRoute, request)
    };
  }
  
  private extractParams(pattern: string, path: string): Record<string, string> {
    const params: Record<string, string> = {};
    
    // /users/:id/posts/:postId 형식 파싱
    const patternParts = pattern.split('/');
    const pathParts = path.split('/');
    
    for (let i = 0; i < patternParts.length; i++) {
      const part = patternParts[i];
      if (part.startsWith(':')) {
        const paramName = part.substring(1);
        params[paramName] = pathParts[i];
      }
    }
    
    return params;
  }
  
  async updateRouteHandler(routeId: string, handler: RouteHandler): Promise<void> {
    const route = this.routes.get(routeId);
    if (!route) {
      throw new RouteNotFoundError(routeId);
    }
    
    // 핸들러 업데이트
    route.handler = handler;
    
    // 트리 업데이트
    this.routeTree.update(route.path, route);
    
    // 동적 라우트 표시
    this.dynamicRoutes.add(routeId);
    
    // 이벤트 발생
    await this.emit('route:updated', { routeId, route });
  }
}
```

**검증 기준**:
- [ ] 동적 라우트 추가/제거
- [ ] 효율적인 경로 매칭
- [ ] 파라미터 추출
- [ ] 우선순위 기반 라우팅

---

## Task 6.2: 라우팅 및 엔드포인트 관리 (계속)

### SubTask 6.2.2: 엔드포인트 레지스트리 시스템

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api_gateway/registry/endpoint_registry.py
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from enum import Enum

@dataclass
class EndpointDefinition:
    """엔드포인트 정의"""
    id: str
    service: str  # 담당 에이전트 서비스
    path: str
    method: str
    version: str
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    replacement: Optional[str] = None
    documentation: Optional[str] = None
    rate_limit: Optional[RateLimit] = None
    auth_required: bool = True
    scopes: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EndpointRegistry:
    """T-Developer 에이전트 엔드포인트 레지스트리"""
    
    def __init__(self):
        self.endpoints: Dict[str, EndpointDefinition] = {}
        self.service_endpoints: Dict[str, List[str]] = {}
        self.version_map: Dict[str, Set[str]] = {}
        self.deprecated_endpoints: Set[str] = set()
        self.watchers: List[EndpointWatcher] = []
        
    async def register_endpoint(self, endpoint: EndpointDefinition) -> None:
        """엔드포인트 등록"""
        
        # 1. 유효성 검증
        await self.validate_endpoint(endpoint)
        
        # 2. 중복 체크
        if self.is_duplicate(endpoint):
            raise DuplicateEndpointError(f"Endpoint {endpoint.path} already exists")
        
        # 3. 레지스트리에 추가
        self.endpoints[endpoint.id] = endpoint
        
        # 4. 서비스별 인덱싱
        if endpoint.service not in self.service_endpoints:
            self.service_endpoints[endpoint.service] = []
        self.service_endpoints[endpoint.service].append(endpoint.id)
        
        # 5. 버전별 인덱싱
        if endpoint.version not in self.version_map:
            self.version_map[endpoint.version] = set()
        self.version_map[endpoint.version].add(endpoint.id)
        
        # 6. Deprecated 추적
        if endpoint.deprecated:
            self.deprecated_endpoints.add(endpoint.id)
            
        # 7. 감시자 알림
        await self.notify_watchers('endpoint_registered', endpoint)
        
    async def discover_endpoints(
        self, 
        filters: Optional[EndpointFilter] = None
    ) -> List[EndpointDefinition]:
        """엔드포인트 검색"""
        
        results = list(self.endpoints.values())
        
        if filters:
            # 서비스 필터
            if filters.service:
                results = [e for e in results if e.service == filters.service]
                
            # 버전 필터
            if filters.version:
                results = [e for e in results if e.version == filters.version]
                
            # 태그 필터
            if filters.tags:
                results = [e for e in results if filters.tags.issubset(e.tags)]
                
            # Deprecated 제외
            if filters.exclude_deprecated:
                results = [e for e in results if not e.deprecated]
                
            # 인증 필요 여부
            if filters.auth_required is not None:
                results = [e for e in results if e.auth_required == filters.auth_required]
                
        return results
    
    async def get_service_endpoints(self, service: str) -> List[EndpointDefinition]:
        """특정 서비스의 모든 엔드포인트"""
        
        endpoint_ids = self.service_endpoints.get(service, [])
        return [self.endpoints[eid] for eid in endpoint_ids if eid in self.endpoints]
    
    async def update_endpoint(
        self, 
        endpoint_id: str, 
        updates: Dict[str, Any]
    ) -> EndpointDefinition:
        """엔드포인트 업데이트"""
        
        if endpoint_id not in self.endpoints:
            raise EndpointNotFoundError(f"Endpoint {endpoint_id} not found")
            
        endpoint = self.endpoints[endpoint_id]
        
        # 허용된 필드만 업데이트
        allowed_fields = {
            'documentation', 'rate_limit', 'auth_required', 
            'scopes', 'tags', 'metadata', 'deprecated', 
            'deprecation_date', 'replacement'
        }
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(endpoint, field, value)
                
        # Deprecated 상태 업데이트
        if 'deprecated' in updates:
            if updates['deprecated']:
                self.deprecated_endpoints.add(endpoint_id)
            else:
                self.deprecated_endpoints.discard(endpoint_id)
                
        # 변경 알림
        await self.notify_watchers('endpoint_updated', endpoint)
        
        return endpoint
    
    async def deprecate_endpoint(
        self, 
        endpoint_id: str,
        deprecation_date: datetime,
        replacement: Optional[str] = None
    ) -> None:
        """엔드포인트 Deprecation"""
        
        await self.update_endpoint(endpoint_id, {
            'deprecated': True,
            'deprecation_date': deprecation_date,
            'replacement': replacement
        })
        
        # Deprecation 알림
        endpoint = self.endpoints[endpoint_id]
        await self.notify_watchers('endpoint_deprecated', endpoint)
```

**검증 기준**:
- [ ] 엔드포인트 등록/조회/업데이트
- [ ] 서비스별 그룹핑
- [ ] 버전 관리
- [ ] Deprecation 처리

### SubTask 6.2.3: 경로 매칭 및 파라미터 처리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api-gateway/routing/path-matcher.ts
export class PathMatcher {
  private patterns: Map<string, CompiledPattern> = new Map();
  private cache: LRUCache<string, MatchResult>;
  
  constructor() {
    this.cache = new LRUCache({ max: 10000 });
  }
  
  compile(pattern: string): CompiledPattern {
    // 캐시 확인
    if (this.patterns.has(pattern)) {
      return this.patterns.get(pattern)!;
    }
    
    const compiled = this.compilePattern(pattern);
    this.patterns.set(pattern, compiled);
    return compiled;
  }
  
  private compilePattern(pattern: string): CompiledPattern {
    // 파라미터 패턴 분석
    // /users/:id/posts/:postId -> /users/([^/]+)/posts/([^/]+)
    
    const segments: PathSegment[] = [];
    const params: string[] = [];
    let regexStr = '^';
    
    const parts = pattern.split('/').filter(p => p.length > 0);
    
    for (const part of parts) {
      if (part.startsWith(':')) {
        // 파라미터
        const paramName = part.substring(1);
        params.push(paramName);
        segments.push({
          type: 'param',
          name: paramName,
          pattern: '([^/]+)'
        });
        regexStr += '/([^/]+)';
      } else if (part === '*') {
        // 와일드카드
        segments.push({
          type: 'wildcard',
          pattern: '.*'
        });
        regexStr += '/.*';
      } else if (part.includes('*')) {
        // 부분 와일드카드 (예: *.json)
        const escapedPart = part.replace('*', '.*');
        segments.push({
          type: 'pattern',
          pattern: escapedPart
        });
        regexStr += '/' + escapedPart;
      } else {
        // 정적 세그먼트
        segments.push({
          type: 'static',
          value: part
        });
        regexStr += '/' + this.escapeRegex(part);
      }
    }
    
    regexStr += '$';
    
    return {
      original: pattern,
      regex: new RegExp(regexStr),
      segments,
      params,
      priority: this.calculatePriority(segments)
    };
  }
  
  match(path: string, pattern: string | CompiledPattern): MatchResult | null {
    // 캐시 확인
    const cacheKey = `${path}:${typeof pattern === 'string' ? pattern : pattern.original}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }
    
    const compiled = typeof pattern === 'string' 
      ? this.compile(pattern) 
      : pattern;
    
    const matches = path.match(compiled.regex);
    
    if (!matches) {
      this.cache.set(cacheKey, null);
      return null;
    }
    
    // 파라미터 추출
    const params: Record<string, string> = {};
    for (let i = 0; i < compiled.params.length; i++) {
      params[compiled.params[i]] = decodeURIComponent(matches[i + 1]);
    }
    
    const result: MatchResult = {
      matched: true,
      pattern: compiled.original,
      path,
      params,
      wildcards: this.extractWildcards(path, compiled, matches)
    };
    
    this.cache.set(cacheKey, result);
    return result;
  }
  
  matchBest(path: string, patterns: string[]): MatchResult | null {
    const candidates: Array<{
      result: MatchResult;
      priority: number;
    }> = [];
    
    for (const pattern of patterns) {
      const result = this.match(path, pattern);
      if (result) {
        const compiled = this.compile(pattern);
        candidates.push({
          result,
          priority: compiled.priority
        });
      }
    }
    
    if (candidates.length === 0) {
      return null;
    }
    
    // 우선순위가 가장 높은 것 선택
    candidates.sort((a, b) => b.priority - a.priority);
    return candidates[0].result;
  }
  
  private calculatePriority(segments: PathSegment[]): number {
    let priority = 0;
    
    for (const segment of segments) {
      switch (segment.type) {
        case 'static':
          priority += 1000;  // 정적 세그먼트 우선
          break;
        case 'param':
          priority += 100;   // 파라미터
          break;
        case 'pattern':
          priority += 10;    // 패턴 매칭
          break;
        case 'wildcard':
          priority += 1;     // 와일드카드 최하위
          break;
      }
    }
    
    return priority;
  }
}

// 파라미터 처리기
export class ParameterProcessor {
  private validators: Map<string, ParameterValidator> = new Map();
  private transformers: Map<string, ParameterTransformer> = new Map();
  
  async processParameters(
    params: Record<string, string>,
    schema: ParameterSchema
  ): Promise<ProcessedParameters> {
    const processed: ProcessedParameters = {
      values: {},
      errors: []
    };
    
    for (const [name, value] of Object.entries(params)) {
      const paramSchema = schema.parameters[name];
      
      if (!paramSchema) {
        // 스키마에 정의되지 않은 파라미터
        if (schema.strict) {
          processed.errors.push({
            param: name,
            error: 'Unknown parameter'
          });
        }
        continue;
      }
      
      try {
        // 1. 타입 변환
        let converted = await this.convertType(value, paramSchema.type);
        
        // 2. 검증
        if (paramSchema.validators) {
          for (const validatorName of paramSchema.validators) {
            const validator = this.validators.get(validatorName);
            if (validator) {
              await validator.validate(converted, paramSchema);
            }
          }
        }
        
        // 3. 변환
        if (paramSchema.transformer) {
          const transformer = this.transformers.get(paramSchema.transformer);
          if (transformer) {
            converted = await transformer.transform(converted);
          }
        }
        
        processed.values[name] = converted;
        
      } catch (error) {
        processed.errors.push({
          param: name,
          error: error.message
        });
      }
    }
    
    // 필수 파라미터 체크
    for (const [name, paramSchema] of Object.entries(schema.parameters)) {
      if (paramSchema.required && !(name in processed.values)) {
        processed.errors.push({
          param: name,
          error: 'Required parameter missing'
        });
      }
    }
    
    return processed;
  }
}
```

**검증 기준**:
- [ ] 효율적인 경로 매칭 알고리즘
- [ ] 파라미터 추출 및 검증
- [ ] 우선순위 기반 매칭
- [ ] 캐싱 메커니즘

### SubTask 6.2.4: 라우팅 규칙 관리 인터페이스

**담당자**: 풀스택 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api_gateway/routing/rule_manager.py
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

@dataclass
class RoutingRule:
    """라우팅 규칙"""
    id: str
    name: str
    description: str
    condition: RuleCondition
    action: RuleAction
    priority: int
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class RoutingRuleManager:
    """라우팅 규칙 관리"""
    
    def __init__(self):
        self.rules: Dict[str, RoutingRule] = {}
        self.rule_engine = RuleEngine()
        self.rule_store = RuleStore()
        self.audit_logger = AuditLogger()
        
    async def create_rule(self, rule_spec: Dict[str, Any]) -> RoutingRule:
        """라우팅 규칙 생성"""
        
        # 1. 규칙 생성
        rule = RoutingRule(
            id=generate_rule_id(),
            name=rule_spec['name'],
            description=rule_spec.get('description', ''),
            condition=self.parse_condition(rule_spec['condition']),
            action=self.parse_action(rule_spec['action']),
            priority=rule_spec.get('priority', 100),
            enabled=rule_spec.get('enabled', True)
        )
        
        # 2. 유효성 검증
        await self.validate_rule(rule)
        
        # 3. 충돌 검사
        conflicts = await self.check_conflicts(rule)
        if conflicts:
            raise RuleConflictError(f"Rule conflicts with: {conflicts}")
        
        # 4. 저장
        self.rules[rule.id] = rule
        await self.rule_store.save(rule)
        
        # 5. 엔진에 등록
        await self.rule_engine.register(rule)
        
        # 6. 감사 로그
        await self.audit_logger.log('rule_created', {
            'rule_id': rule.id,
            'name': rule.name,
            'user': get_current_user()
        })
        
        return rule
    
    async def update_rule(
        self, 
        rule_id: str, 
        updates: Dict[str, Any]
    ) -> RoutingRule:
        """라우팅 규칙 업데이트"""
        
        if rule_id not in self.rules:
            raise RuleNotFoundError(f"Rule {rule_id} not found")
        
        rule = self.rules[rule_id]
        original = copy.deepcopy(rule)
        
        # 업데이트 적용
        for field, value in updates.items():
            if hasattr(rule, field):
                setattr(rule, field, value)
        
        rule.updated_at = datetime.now()
        
        # 유효성 재검증
        await self.validate_rule(rule)
        
        # 엔진 업데이트
        await self.rule_engine.update(rule)
        
        # 저장
        await self.rule_store.save(rule)
        
        # 감사 로그
        await self.audit_logger.log('rule_updated', {
            'rule_id': rule.id,
            'changes': self.diff_rules(original, rule),
            'user': get_current_user()
        })
        
        return rule
    
    async def evaluate_rules(
        self, 
        request: IncomingRequest
    ) -> List[RuleEvaluation]:
        """요청에 대한 규칙 평가"""
        
        evaluations = []
        
        # 활성화된 규칙만 평가
        active_rules = [
            rule for rule in self.rules.values() 
            if rule.enabled
        ]
        
        # 우선순위 순으로 정렬
        active_rules.sort(key=lambda r: r.priority, reverse=True)
        
        for rule in active_rules:
            evaluation = await self.rule_engine.evaluate(rule, request)
            evaluations.append(evaluation)
            
            # 첫 번째 매칭 규칙에서 중단 (설정에 따라)
            if evaluation.matched and rule.action.stop_on_match:
                break
        
        return evaluations
    
    async def import_rules(self, rules_json: str) -> List[RoutingRule]:
        """규칙 일괄 가져오기"""
        
        try:
            rules_data = json.loads(rules_json)
        except json.JSONDecodeError as e:
            raise InvalidRuleFormatError(f"Invalid JSON: {e}")
        
        imported_rules = []
        
        for rule_spec in rules_data:
            try:
                rule = await self.create_rule(rule_spec)
                imported_rules.append(rule)
            except Exception as e:
                # 개별 규칙 실패 시 계속 진행
                await self.audit_logger.log('rule_import_failed', {
                    'rule_name': rule_spec.get('name'),
                    'error': str(e)
                })
        
        return imported_rules
    
    async def export_rules(
        self, 
        rule_ids: Optional[List[str]] = None
    ) -> str:
        """규칙 내보내기"""
        
        if rule_ids:
            rules_to_export = [
                self.rules[rid] for rid in rule_ids 
                if rid in self.rules
            ]
        else:
            rules_to_export = list(self.rules.values())
        
        export_data = []
        
        for rule in rules_to_export:
            export_data.append({
                'name': rule.name,
                'description': rule.description,
                'condition': self.serialize_condition(rule.condition),
                'action': self.serialize_action(rule.action),
                'priority': rule.priority,
                'enabled': rule.enabled,
                'metadata': rule.metadata
            })
        
        return json.dumps(export_data, indent=2)

# 관리 인터페이스 API
class RoutingRuleAPI:
    """라우팅 규칙 관리 REST API"""
    
    def __init__(self, manager: RoutingRuleManager):
        self.manager = manager
        self.router = APIRouter(prefix="/api/routing-rules")
        self.setup_routes()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.router.get("/")
        async def list_rules(
            enabled: Optional[bool] = None,
            skip: int = 0,
            limit: int = 100
        ):
            """규칙 목록 조회"""
            rules = list(self.manager.rules.values())
            
            if enabled is not None:
                rules = [r for r in rules if r.enabled == enabled]
            
            return {
                'rules': rules[skip:skip+limit],
                'total': len(rules)
            }
        
        @self.router.post("/")
        async def create_rule(rule_spec: Dict[str, Any]):
            """규칙 생성"""
            rule = await self.manager.create_rule(rule_spec)
            return {'rule': rule, 'message': 'Rule created successfully'}
        
        @self.router.put("/{rule_id}")
        async def update_rule(rule_id: str, updates: Dict[str, Any]):
            """규칙 업데이트"""
            rule = await self.manager.update_rule(rule_id, updates)
            return {'rule': rule, 'message': 'Rule updated successfully'}
        
        @self.router.delete("/{rule_id}")
        async def delete_rule(rule_id: str):
            """규칙 삭제"""
            await self.manager.delete_rule(rule_id)
            return {'message': 'Rule deleted successfully'}
        
        @self.router.post("/test")
        async def test_rules(test_request: Dict[str, Any]):
            """규칙 테스트"""
            request = create_mock_request(test_request)
            evaluations = await self.manager.evaluate_rules(request)
            return {'evaluations': evaluations}
```

**검증 기준**:
- [ ] 규칙 CRUD 작업
- [ ] 규칙 평가 엔진
- [ ] 가져오기/내보내기
- [ ] 관리 API 구현

---

## Task 6.3: 요청/응답 변환 레이어

### SubTask 6.3.1: 요청 파서 및 검증기

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api-gateway/transformation/request-parser.ts
export interface ParsedRequest {
  headers: Record<string, string>;
  params: Record<string, any>;
  query: Record<string, any>;
  body: any;
  cookies: Record<string, string>;
  metadata: RequestMetadata;
}

export class RequestParser {
  private validators: Map<string, Validator> = new Map();
  private parsers: Map<string, Parser> = new Map();
  
  constructor() {
    this.initializeParsers();
    this.initializeValidators();
  }
  
  private initializeParsers(): void {
    // JSON 파서
    this.parsers.set('application/json', new JSONParser());
    
    // XML 파서
    this.parsers.set('application/xml', new XMLParser());
    
    // Form 파서
    this.parsers.set('application/x-www-form-urlencoded', new FormParser());
    
    // Multipart 파서
    this.parsers.set('multipart/form-data', new MultipartParser());
    
    // GraphQL 파서
    this.parsers.set('application/graphql', new GraphQLParser());
    
    // Protocol Buffers 파서
    this.parsers.set('application/protobuf', new ProtobufParser());
  }
  
  async parse(request: IncomingRequest): Promise<ParsedRequest> {
    const contentType = request.headers['content-type'] || 'application/json';
    const parser = this.selectParser(contentType);
    
    // 1. 헤더 파싱
    const headers = this.parseHeaders(request.headers);
    
    // 2. 쿼리 파라미터 파싱
    const query = this.parseQueryParams(request.url);
    
    // 3. 경로 파라미터 파싱
    const params = request.params || {};
    
    // 4. 쿠키 파싱
    const cookies = this.parseCookies(request.headers.cookie);
    
    // 5. 바디 파싱
    let body = null;
    if (request.body) {
      body = await parser.parse(request.body);
    }
    
    // 6. 메타데이터 추출
    const metadata = this.extractMetadata(request);
    
    return {
      headers,
      params,
      query,
      body,
      cookies,
      metadata
    };
  }
  
  async validate(
    parsedRequest: ParsedRequest,
    schema: ValidationSchema
  ): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    
    // 헤더 검증
    if (schema.headers) {
      const headerErrors = await this.validateHeaders(
        parsedRequest.headers,
        schema.headers
      );
      errors.push(...headerErrors);
    }
    
    // 파라미터 검증
    if (schema.params) {
      const paramErrors = await this.validateParams(
        parsedRequest.params,
        schema.params
      );
      errors.push(...paramErrors);
    }
    
    // 쿼리 검증
    if (schema.query) {
      const queryErrors = await this.validateQuery(
        parsedRequest.query,
        schema.query
      );
      errors.push(...queryErrors);
    }
    
    // 바디 검증
    if (schema.body) {
      const bodyErrors = await this.validateBody(
        parsedRequest.body,
        schema.body
      );
      errors.push(...bodyErrors);
    }
    
    return {
      valid: errors.length === 0,
      errors,
      sanitized: await this.sanitize(parsedRequest, schema)
    };
  }
  
  private async sanitize(
    request: ParsedRequest,
    schema: ValidationSchema
  ): Promise<ParsedRequest> {
    const sanitized = { ...request };
    
    // XSS 방지
    if (schema.sanitize?.xss) {
      sanitized.body = this.sanitizeXSS(request.body);
      sanitized.params = this.sanitizeXSS(request.params);
      sanitized.query = this.sanitizeXSS(request.query);
    }
    
    // SQL Injection 방지
    if (schema.sanitize?.sql) {
      sanitized.params = this.sanitizeSQL(request.params);
      sanitized.query = this.sanitizeSQL(request.query);
    }
    
    // 타입 강제 변환
    if (schema.coerce) {
      sanitized.body = await this.coerceTypes(request.body, schema.body);
      sanitized.params = await this.coerceTypes(request.params, schema.params);
      sanitized.query = await this.coerceTypes(request.query, schema.query);
    }
    
    return sanitized;
  }
}

// 요청 검증기
export class RequestValidator {
  private ajv: Ajv;
  private schemas: Map<string, any> = new Map();
  
  constructor() {
    this.ajv = new Ajv({
      allErrors: true,
      coerceTypes: true,
      removeAdditional: true
    });
    
    // 커스텀 포맷 추가
    this.ajv.addFormat('email', /^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    this.ajv.addFormat('uuid', /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
    this.ajv.addFormat('iso8601', /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/);
  }
  
  async validateRequest(
    request: ParsedRequest,
    endpointSchema: EndpointSchema
  ): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    
    // OpenAPI 스키마 기반 검증
    if (endpointSchema.openapi) {
      const openApiErrors = await this.validateOpenAPI(
        request,
        endpointSchema.openapi
      );
      errors.push(...openApiErrors);
    }
    
    // 커스텀 검증 규칙
    if (endpointSchema.customValidators) {
      for (const validator of endpointSchema.customValidators) {
        const customErrors = await validator.validate(request);
        errors.push(...customErrors);
      }
    }
    
    // 비즈니스 규칙 검증
    if (endpointSchema.businessRules) {
      const ruleErrors = await this.validateBusinessRules(
        request,
        endpointSchema.businessRules
      );
      errors.push(...ruleErrors);
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings: await this.checkWarnings(request, endpointSchema)
    };
  }
}
```

**검증 기준**:
- [ ] 다양한 콘텐츠 타입 파싱
- [ ] 스키마 기반 검증
- [ ] 보안 살균 처리
- [ ] 에러 상세 정보

### SubTask 6.3.2: 프로토콜 변환 엔진

**담당자**: 백엔드 개발자  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/api_gateway/transformation/protocol_converter.py
from typing import Any, Dict, Optional, Union
from abc import ABC, abstractmethod
import json
import xml.etree.ElementTree as ET
from google.protobuf import message as protobuf_message

class ProtocolConverter(ABC):
    """프로토콜 변환 기본 클래스"""
    
    @abstractmethod
    async def convert(self, data: Any, target_format: str) -> Any:
        pass

class UniversalProtocolConverter:
    """범용 프로토콜 변환 엔진"""
    
    def __init__(self):
        self.converters = self._initialize_converters()
        self.schema_registry = SchemaRegistry()
        
    def _initialize_converters(self) -> Dict[str, Dict[str, ProtocolConverter]]:
        """변환기 초기화"""
        return {
            'json': {
                'xml': JSONToXMLConverter(),
                'protobuf': JSONToProtobufConverter(),
                'graphql': JSONToGraphQLConverter(),
                'msgpack': JSONToMsgPackConverter(),
                'yaml': JSONToYAMLConverter()
            },
            'xml': {
                'json': XMLToJSONConverter(),
                'protobuf': XMLToProtobufConverter(),
                'graphql': XMLToGraphQLConverter()
            },
            'protobuf': {
                'json': ProtobufToJSONConverter(),
                'xml': ProtobufToXMLConverter(),
                'graphql': ProtobufToGraphQLConverter()
            },
            'graphql': {
                'json': GraphQLToJSONConverter(),
                'xml': GraphQLToXMLConverter(),
                'protobuf': GraphQLToProtobufConverter()
            }
        }
    
    async def convert(
        self,
        data: Any,
        source_format: str,
        target_format: str,
        schema: Optional[Any] = None
    ) -> ConversionResult:
        """프로토콜 변환 실행"""
        
        if source_format == target_format:
            return ConversionResult(
                success=True,
                data=data,
                format=target_format
            )
        
        # 직접 변환 가능 확인
        if source_format in self.converters and target_format in self.converters[source_format]:
            converter = self.converters[source_format][target_format]
            
            try:
                converted_data = await converter.convert(data, target_format)
                
                # 스키마 검증
                if schema:
                    await self.validate_against_schema(converted_data, schema, target_format)
                
                return ConversionResult(
                    success=True,
                    data=converted_data,
                    format=target_format,
                    metadata={'direct_conversion': True}
                )
                
            except Exception as e:
                return ConversionResult(
                    success=False,
                    error=str(e),
                    format=target_format
                )
        
        # 간접 변환 (중간 형식 사용)
        return await self.convert_via_intermediate(
            data, source_format, target_format, schema
        )
    
    async def convert_via_intermediate(
        self,
        data: Any,
        source_format: str,
        target_format: str,
        schema: Optional[Any] = None
    ) -> ConversionResult:
        """중간 형식을 통한 변환"""
        
        # JSON을 중간 형식으로 사용
        intermediate_format = 'json'
        
        # 1단계: source -> intermediate
        if source_format != intermediate_format:
            intermediate_result = await self.convert(
                data, source_format, intermediate_format
            )
            
            if not intermediate_result.success:
                return intermediate_result
                
            intermediate_data = intermediate_result.data
        else:
            intermediate_data = data
        
        # 2단계: intermediate -> target
        final_result = await self.convert(
            intermediate_data, intermediate_format, target_format, schema
        )
        
        if final_result.success:
            final_result.metadata['via_intermediate'] = intermediate_format
        
        return final_result

class JSONToProtobufConverter(ProtocolConverter):
    """JSON to Protocol Buffers 변환"""
    
    async def convert(self, json_data: Dict, target_format: str) -> bytes:
        # 스키마 로드
        proto_schema = await self.load_proto_schema(json_data.get('__schema__'))
        
        # 메시지 생성
        message_class = self.get_message_class(proto_schema)
        message = message_class()
        
        # JSON 데이터를 Protobuf 메시지로 변환
        self.populate_message(message, json_data)
        
        # 직렬화
        return message.SerializeToString()
    
    def populate_message(
        self,
        message: protobuf_message.Message,
        data: Dict[str, Any]
    ) -> None:
        """Protobuf 메시지 채우기"""
        
        for field, value in data.items():
            if field.startswith('__'):  # 메타데이터 스킵
                continue
                
            if hasattr(message, field):
                field_descriptor = message.DESCRIPTOR.fields_by_name.get(field)
                
                if field_descriptor:
                    if field_descriptor.label == field_descriptor.LABEL_REPEATED:
                        # 반복 필드
                        repeated_field = getattr(message, field)
                        for item in value:
                            if field_descriptor.type == field_descriptor.TYPE_MESSAGE:
                                sub_message = repeated_field.add()
                                self.populate_message(sub_message, item)
                            else:
                                repeated_field.append(item)
                    elif field_descriptor.type == field_descriptor.TYPE_MESSAGE:
                        # 중첩 메시지
                        sub_message = getattr(message, field)
                        self.populate_message(sub_message, value)
                    else:
                        # 단순 필드
                        setattr(message, field, value)

class GraphQLConverter:
    """GraphQL 변환 처리"""
    
    async def convert_request(
        self,
        graphql_request: Dict[str, Any]
    ) -> RESTRequest:
        """GraphQL 요청을 REST로 변환"""
        
        query = graphql_request.get('query')
        variables = graphql_request.get('variables', {})
        operation_name = graphql_request.get('operationName')
        
        # GraphQL 파싱
        parsed = self.parse_graphql(query)
        
        # 작업 타입 확인
        operation = self.get_operation(parsed, operation_name)
        
        if operation.type == 'query':
            return self.convert_query_to_rest(operation, variables)
        elif operation.type == 'mutation':
            return self.convert_mutation_to_rest(operation, variables)
        elif operation.type == 'subscription':
            return self.convert_subscription_to_websocket(operation, variables)
        
    def convert_query_to_rest(
        self,
        operation: GraphQLOperation,
        variables: Dict
    ) -> RESTRequest:
        """GraphQL 쿼리를 REST GET으로 변환"""
        
        # 필드 선택을 쿼리 파라미터로 변환
        fields = self.extract_fields(operation.selection_set)
        
        return RESTRequest(
            method='GET',
            path=f"/api/{operation.name}",
            query_params={
                **variables,
                'fields': ','.join(fields)
            }
        )
```

**검증 기준**:
- [ ] 다양한 프로토콜 지원
- [ ] 양방향 변환
- [ ] 스키마 기반 변환
- [ ] 중간 형식 활용

### SubTask 6.3.3: 응답 포맷터 및 압축

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api-gateway/transformation/response-formatter.ts
export class ResponseFormatter {
  private formatters: Map<string, Formatter> = new Map();
  private compressors: Map<string, Compressor> = new Map();
  
  constructor() {
    this.initializeFormatters();
    this.initializeCompressors();
  }
  
  private initializeFormatters(): void {
    this.formatters.set('json', new JSONFormatter());
    this.formatters.set('xml', new XMLFormatter());
    this.formatters.set('html', new HTMLFormatter());
    this.formatters.set('csv', new CSVFormatter());
    this.formatters.set('yaml', new YAMLFormatter());
  }
  
  private initializeCompressors(): void {
    this.compressors.set('gzip', new GzipCompressor());
    this.compressors.set('deflate', new DeflateCompressor());
    this.compressors.set('br', new BrotliCompressor());
    this.compressors.set('zstd', new ZstdCompressor());
  }
  
  async format(
    data: any,
    options: FormattingOptions
  ): Promise<FormattedResponse> {
    // 1. 응답 구조 정규화
    const normalized = this.normalizeResponse(data, options);
    
    // 2. 포맷 선택
    const format = options.format || 'json';
    const formatter = this.formatters.get(format);
    
    if (!formatter) {
      throw new UnsupportedFormatError(`Format ${format} not supported`);
    }
    
    // 3. 포맷팅 실행
    let formatted = await formatter.format(normalized, options);
    
    // 4. 후처리
    if (options.prettify) {
      formatted = await this.prettify(formatted, format);
    }
    
    // 5. 압축
    if (options.compress) {
      formatted = await this.compress(formatted, options.compress);
    }
    
    return {
      data: formatted,
      contentType: formatter.getContentType(),
      encoding: options.compress?.algorithm,
      size: this.calculateSize(formatted)
    };
  }
  
  private normalizeResponse(
    data: any,
    options: FormattingOptions
  ): NormalizedResponse {
    // 표준 응답 구조
    const normalized: NormalizedResponse = {
      success: true,
      data: null,
      metadata: {},
      timestamp: new Date().toISOString()
    };
    
    // 데이터 처리
    if (data instanceof Error) {
      normalized.success = false;
      normalized.error = {
        code: data.code || 'INTERNAL_ERROR',
        message: data.message,
        details: options.includeStackTrace ? data.stack : undefined
      };
    } else {
      normalized.data = data;
    }
    
    // 메타데이터 추가
    if (options.includeMetadata) {
      normalized.metadata = {
        version: options.apiVersion,
        requestId: options.requestId,
        processingTime: options.processingTime,
        ...options.customMetadata
      };
    }
    
    // 페이지네이션 정보
    if (options.pagination) {
      normalized.pagination = {
        page: options.pagination.page,
        limit: options.pagination.limit,
        total: options.pagination.total,
        hasNext: options.pagination.hasNext,
        hasPrev: options.pagination.hasPrev
      };
    }
    
    return normalized;
  }
  
  async compress(
    data: Buffer | string,
    compression: CompressionOptions
  ): Promise<Buffer> {
    const algorithm = compression.algorithm || 'gzip';
    const compressor = this.compressors.get(algorithm);
    
    if (!compressor) {
      throw new UnsupportedCompressionError(`Compression ${algorithm} not supported`);
    }
    
    const input = Buffer.isBuffer(data) ? data : Buffer.from(data);
    
    // 압축 임계값 체크
    if (input.length < (compression.threshold || 1024)) {
      return input; // 작은 데이터는 압축하지 않음
    }
    
    const compressed = await compressor.compress(input, {
      level: compression.level || 6,
      strategy: compression.strategy
    });
    
    // 압축 효율 체크
    const ratio = compressed.length / input.length;
    if (ratio > 0.9) {
      // 압축 효과가 미미하면 원본 반환
      return input;
    }
    
    return compressed;
  }
}

// 적응형 응답 포매터
export class AdaptiveResponseFormatter {
  private formatter: ResponseFormatter;
  private analyzer: ClientAnalyzer;
  
  async formatForClient(
    data: any,
    request: IncomingRequest
  ): Promise<FormattedResponse> {
    // 클라이언트 분석
    const clientProfile = await this.analyzer.analyze(request);
    
    // 최적 포맷 선택
    const format = this.selectOptimalFormat(clientProfile, request);
    
    // 압축 전략 결정
    const compression = this.selectCompression(clientProfile, request);
    
    // 포맷팅 옵션 구성
    const options: FormattingOptions = {
      format,
      compress: compression,
      prettify: clientProfile.isDevelopment,
      includeMetadata: clientProfile.requiresMetadata,
      apiVersion: request.headers['api-version'] || 'v1',
      requestId: request.id,
      processingTime: Date.now() - request.startTime
    };
    
    return await this.formatter.format(data, options);
  }
  
  private selectOptimalFormat(
    profile: ClientProfile,
    request: IncomingRequest
  ): string {
    // Accept 헤더 확인
    const accept = request.headers['accept'];
    
    if (accept) {
      // 클라이언트 선호도 반영
      const preferred = this.parseAcceptHeader(accept);
      for (const format of preferred) {
        if (this.formatter.supports(format)) {
          return format;
        }
      }
    }
    
    // 클라이언트 타입별 기본 포맷
    switch (profile.type) {
      case 'browser':
        return 'json';
      case 'mobile':
        return 'json'; // 또는 protobuf
      case 'api':
        return profile.preferredFormat || 'json';
      default:
        return 'json';
    }
  }
}
```

**검증 기준**:
- [ ] 다양한 응답 포맷 지원
- [ ] 효율적인 압축 알고리즘
- [ ] 적응형 포맷 선택
- [ ] 성능 최적화

### SubTask 6.3.4: 데이터 변환 파이프라인

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api_gateway/transformation/data_pipeline.py
from typing import List, Any, Callable, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class PipelineStage:
    """파이프라인 스테이지"""
    name: str
    transformer: Callable
    condition: Optional[Callable] = None
    error_handler: Optional[Callable] = None
    parallel: bool = False
    timeout: Optional[float] = None

class DataTransformationPipeline:
    """데이터 변환 파이프라인"""
    
    def __init__(self):
        self.stages: List[PipelineStage] = []
        self.context = PipelineContext()
        self.metrics = PipelineMetrics()
        
    def add_stage(self, stage: PipelineStage) -> 'DataTransformationPipeline':
        """스테이지 추가"""
        self.stages.append(stage)
        return self
        
    async def execute(self, data: Any) -> PipelineResult:
        """파이프라인 실행"""
        
        result = PipelineResult(
            input_data=data,
            output_data=data,
            stages_executed=[],
            errors=[],
            metrics={}
        )
        
        current_data = data
        
        for stage in self.stages:
            # 조건 체크
            if stage.condition and not await stage.condition(current_data, self.context):
                continue
                
            try:
                # 타임아웃 설정
                if stage.timeout:
                    current_data = await asyncio.wait_for(
                        self.execute_stage(stage, current_data),
                        timeout=stage.timeout
                    )
                else:
                    current_data = await self.execute_stage(stage, current_data)
                    
                result.stages_executed.append(stage.name)
                
            except asyncio.TimeoutError:
                error = StageTimeoutError(f"Stage {stage.name} timed out")
                result.errors.append(error)
                
                if stage.error_handler:
                    current_data = await stage.error_handler(current_data, error)
                else:
                    raise error
                    
            except Exception as e:
                error = StageExecutionError(f"Stage {stage.name} failed: {e}")
                result.errors.append(error)
                
                if stage.error_handler:
                    current_data = await stage.error_handler(current_data, e)
                else:
                    raise error
        
        result.output_data = current_data
        result.metrics = await self.metrics.collect()
        
        return result
    
    async def execute_stage(
        self,
        stage: PipelineStage,
        data: Any
    ) -> Any:
        """단일 스테이지 실행"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            if stage.parallel and isinstance(data, list):
                # 병렬 처리
                tasks = [stage.transformer(item, self.context) for item in data]
                transformed = await asyncio.gather(*tasks)
            else:
                # 순차 처리
                transformed = await stage.transformer(data, self.context)
            
            # 메트릭 기록
            elapsed = asyncio.get_event_loop().time() - start_time
            await self.metrics.record_stage_execution(stage.name, elapsed)
            
            return transformed
            
        except Exception as e:
            await self.metrics.record_stage_error(stage.name, e)
            raise

# 사전 정의된 변환 스테이지
class CommonTransformers:
    """공통 변환기 모음"""
    
    @staticmethod
    async def validate_schema(data: Any, context: PipelineContext) -> Any:
        """스키마 검증"""
        schema = context.get('schema')
        if schema:
            validator = SchemaValidator(schema)
            validator.validate(data)
        return data
    
    @staticmethod
    async def enrich_data(data: Any, context: PipelineContext) -> Any:
        """데이터 보강"""
        enrichments = context.get('enrichments', {})
        
        if isinstance(data, dict):
            data.update(enrichments)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item.update(enrichments)
        
        return data
    
    @staticmethod
    async def filter_fields(data: Any, context: PipelineContext) -> Any:
        """필드 필터링"""
        allowed_fields = context.get('allowed_fields')
        
        if not allowed_fields:
            return data
        
        def filter_dict(d: dict) -> dict:
            return {k: v for k, v in d.items() if k in allowed_fields}
        
        if isinstance(data, dict):
            return filter_dict(data)
        elif isinstance(data, list):
            return [filter_dict(item) if isinstance(item, dict) else item for item in data]
        
        return data
    
    @staticmethod
    async def transform_keys(data: Any, context: PipelineContext) -> Any:
        """키 변환 (camelCase <-> snake_case)"""
        transform_type = context.get('key_transform', 'camel_to_snake')
        
        def to_camel_case(snake_str: str) -> str:
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])
        
        def to_snake_case(camel_str: str) -> str:
            import re
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        transformer = to_snake_case if transform_type == 'camel_to_snake' else to_camel_case
        
        def transform_dict(d: dict) -> dict:
            return {transformer(k): v for k, v in d.items()}
        
        if isinstance(data, dict):
            return transform_dict(data)
        elif isinstance(data, list):
            return [transform_dict(item) if isinstance(item, dict) else item for item in data]
        
        return data

# 파이프라인 빌더
class PipelineBuilder:
    """파이프라인 구성 빌더"""
    
    def __init__(self):
        self.pipeline = DataTransformationPipeline()
        
    def validate(self, schema: Any) -> 'PipelineBuilder':
        """검증 스테이지 추가"""
        self.pipeline.add_stage(PipelineStage(
            name='validation',
            transformer=CommonTransformers.validate_schema
        ))
        self.pipeline.context.set('schema', schema)
        return self
        
    def enrich(self, enrichments: Dict) -> 'PipelineBuilder':
        """보강 스테이지 추가"""
        self.pipeline.add_stage(PipelineStage(
            name='enrichment',
            transformer=CommonTransformers.enrich_data
        ))
        self.pipeline.context.set('enrichments', enrichments)
        return self
        
    def filter(self, fields: List[str]) -> 'PipelineBuilder':
        """필터 스테이지 추가"""
        self.pipeline.add_stage(PipelineStage(
            name='filtering',
            transformer=CommonTransformers.filter_fields
        ))
        self.pipeline.context.set('allowed_fields', fields)
        return self
        
    def custom(
        self,
        name: str,
        transformer: Callable,
        **kwargs
    ) -> 'PipelineBuilder':
        """커스텀 스테이지 추가"""
        self.pipeline.add_stage(PipelineStage(
            name=name,
            transformer=transformer,
            **kwargs
        ))
        return self
        
    def build(self) -> DataTransformationPipeline:
        """파이프라인 빌드"""
        return self.pipeline
```

**검증 기준**:
- [ ] 유연한 파이프라인 구성
- [ ] 병렬 처리 지원
- [ ] 에러 처리 및 복구
- [ ] 성능 메트릭 수집

---

## Task 6.4: API 버전 관리 시스템

### SubTask 6.4.1: 버전 라우팅 전략 구현

**담당자**: 백엔드 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api-gateway/versioning/version-router.ts
export enum VersioningStrategy {
  URL_PATH = 'url_path',      // /api/v1/users
  HEADER = 'header',           // API-Version: 1.0
  QUERY_PARAM = 'query_param', // /api/users?version=1
  CONTENT_TYPE = 'content_type' // application/vnd.api+json;version=1
}

export class VersionRouter {
  private strategies: Map<VersioningStrategy, VersionExtractor>;
  private versionMap: Map<string, VersionedEndpoint[]>;
  private defaultVersion: string;
  
  constructor(config: VersioningConfig) {
    this.strategies = this.initializeStrategies();
    this.versionMap = new Map();
    this.defaultVersion = config.defaultVersion || 'v1';
  }
  
  private initializeStrategies(): Map<VersioningStrategy, VersionExtractor> {
    const strategies = new Map();
    
    // URL 경로 기반
    strategies.set(VersioningStrategy.URL_PATH, {
      extract: (request: Request) => {
        const match = request.path.match(/\/api\/v(\d+(?:\.\d+)?)/);
        return match ? `v${match[1]}` : null;
      },
      rewrite: (request: Request, version: string) => {
        request.path = request.path.replace(/\/api\/v\d+(?:\.\d+)?/, `/api/${version}`);
      }
    });
    
    // 헤더 기반
    strategies.set(VersioningStrategy.HEADER, {
      extract: (request: Request) => {
        return request.headers['api-version'] || request.headers['x-api-version'];
      },
      rewrite: (request: Request, version: string) => {
        request.headers['x-resolved-version'] = version;
      }
    });
    
    // 쿼리 파라미터 기반
    strategies.set(VersioningStrategy.QUERY_PARAM, {
      extract: (request: Request) => {
        return request.query.version || request.query.v;
      },
      rewrite: (request: Request, version: string) => {
        delete request.query.version;
        delete request.query.v;
      }
    });
    
    // Content-Type 기반
    strategies.set(VersioningStrategy.CONTENT_TYPE, {
      extract: (request: Request) => {
        const contentType = request.headers['content-type'];
        const match = contentType?.match(/version=(\d+(?:\.\d+)?)/);
        return match ? `v${match[1]}` : null;
      },
      rewrite: (request: Request, version: string) => {
        // Content-Type에서 버전 정보 제거
        if (request.headers['content-type']) {
          request.headers['content-type'] = 
            request.headers['content-type'].replace(/;version=\d+(?:\.\d+)?/, '');
        }
      }
    });
    
    return strategies;
  }
  
  async route(request: Request): Promise<VersionedEndpoint> {
    // 1. 버전 추출
    const version = this.extractVersion(request) || this.defaultVersion;
    
    // 2. 버전 검증
    if (!this.isValidVersion(version)) {
      throw new InvalidVersionError(`Invalid API version: ${version}`);
    }
    
    // 3. 엔드포인트 매칭
    const endpoint = await this.matchEndpoint(request, version);
    
    if (!endpoint) {
      // 폴백 버전 시도
      const fallbackVersion = this.getFallbackVersion(version);
      if (fallbackVersion) {
        return await this.matchEndpoint(request, fallbackVersion);
      }
      
      throw new EndpointNotFoundError(
        `Endpoint not found for version ${version}`
      );
    }
    
    // 4. 요청 변환
    await this.transformRequest(request, version, endpoint);
    
    return endpoint;
  }
  
  private extractVersion(request: Request): string | null {
    // 설정된 전략 순서대로 시도
    for (const [strategy, extractor] of this.strategies) {
      const version = extractor.extract(request);
      if (version) {
        return this.normalizeVersion(version);
      }
    }
    
    return null;
  }
  
  private normalizeVersion(version: string): string {
    // v1, 1.0, v1.0 등을 표준 형식으로 변환
    if (!version.startsWith('v')) {
      version = `v${version}`;
    }
    
    // 메이저 버전만 있으면 .0 추가
    if (!version.includes('.')) {
      version += '.0';
    }
    
    return version;
  }
  
  async registerEndpoint(
    version: string,
    endpoint: VersionedEndpoint
  ): Promise<void> {
    if (!this.versionMap.has(version)) {
      this.versionMap.set(version, []);
    }
    
    const endpoints = this.versionMap.get(version)!;
    
    // 중복 체크
    const existing = endpoints.find(e => 
      e.path === endpoint.path && e.method === endpoint.method
    );
    
    if (existing) {
      throw new DuplicateEndpointError(
        `Endpoint ${endpoint.method} ${endpoint.path} already exists for version ${version}`
      );
    }
    
    endpoints.push(endpoint);
    
    // 버전 간 호환성 체크
    await this.checkCompatibility(version, endpoint);
  }
}
```

**검증 기준**:
- [ ] 다양한 버전 지정 방식
- [ ] 버전 추출 및 검증
- [ ] 폴백 메커니즘
- [ ] 버전별 라우팅

### SubTask 6.4.2: 하위 호환성 관리

**담당자**: API 아키텍트  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/api_gateway/versioning/compatibility_manager.py
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

class BreakingChangeType(Enum):
    """Breaking Change 유형"""
    REMOVED_FIELD = "removed_field"
    RENAMED_FIELD = "renamed_field"
    TYPE_CHANGED = "type_changed"
    REQUIRED_FIELD_ADDED = "required_field_added"
    REMOVED_ENDPOINT = "removed_endpoint"
    METHOD_CHANGED = "method_changed"
    AUTHENTICATION_CHANGED = "auth_changed"

@dataclass
class CompatibilityRule:
    """호환성 규칙"""
    source_version: str
    target_version: str
    change_type: BreakingChangeType
    transformation: Optional[Callable] = None
    migration_guide: Optional[str] = None

class BackwardCompatibilityManager:
    """하위 호환성 관리자"""
    
    def __init__(self):
        self.compatibility_matrix: Dict[str, Dict[str, List[CompatibilityRule]]] = {}
        self.version_chain: List[str] = []
        self.deprecation_policy = DeprecationPolicy()
        
    async def check_compatibility(
        self,
        from_version: str,
        to_version: str,
        endpoint: EndpointDefinition
    ) -> CompatibilityReport:
        """버전 간 호환성 체크"""
        
        report = CompatibilityReport(
            from_version=from_version,
            to_version=to_version,
            endpoint=endpoint.path,
            compatible=True,
            breaking_changes=[],
            warnings=[],
            migration_required=False
        )
        
        # 버전 체인에서 위치 확인
        from_idx = self.version_chain.index(from_version)
        to_idx = self.version_chain.index(to_version)
        
        if from_idx >= to_idx:
            # 동일 버전이거나 다운그레이드
            return report
        
        # 변경 사항 수집
        for version_idx in range(from_idx, to_idx):
            current = self.version_chain[version_idx]
            next_version = self.version_chain[version_idx + 1]
            
            changes = await self.get_changes(current, next_version, endpoint)
            
            for change in changes:
                if change.is_breaking:
                    report.compatible = False
                    report.breaking_changes.append(change)
                    report.migration_required = True
                else:
                    report.warnings.append(change)
        
        # 자동 마이그레이션 가능 여부 확인
        if report.migration_required:
            report.auto_migration_available = await self.can_auto_migrate(
                report.breaking_changes
            )
        
        return report
    
    async def apply_compatibility_layer(
        self,
        request: Request,
        source_version: str,
        target_version: str
    ) -> Request:
        """호환성 레이어 적용"""
        
        # 호환성 규칙 조회
        rules = self.get_compatibility_rules(source_version, target_version)
        
        transformed_request = request
        
        for rule in rules:
            if rule.transformation:
                transformed_request = await rule.transformation(transformed_request)
            else:
                transformed_request = await self.apply_default_transformation(
                    transformed_request,
                    rule
                )
        
        # 헤더에 변환 정보 추가
        transformed_request.headers['X-API-Compatibility-Applied'] = 'true'
        transformed_request.headers['X-Original-Version'] = source_version
        transformed_request.headers['X-Target-Version'] = target_version
        
        return transformed_request
    
    async def apply_default_transformation(
        self,
        request: Request,
        rule: CompatibilityRule
    ) -> Request:
        """기본 변환 적용"""
        
        if rule.change_type == BreakingChangeType.RENAMED_FIELD:
            # 필드 이름 변경
            if rule.old_name in request.body:
                request.body[rule.new_name] = request.body.pop(rule.old_name)
                
        elif rule.change_type == BreakingChangeType.TYPE_CHANGED:
            # 타입 변환
            if rule.field_name in request.body:
                request.body[rule.field_name] = await self.convert_type(
                    request.body[rule.field_name],
                    rule.old_type,
                    rule.new_type
                )
                
        elif rule.change_type == BreakingChangeType.REMOVED_FIELD:
            # 제거된 필드 처리
            if rule.field_name in request.body:
                # 경고 로그
                await self.log_compatibility_warning(
                    f"Field {rule.field_name} is deprecated in {rule.target_version}"
                )
                # 필드 제거
                del request.body[rule.field_name]
                
        elif rule.change_type == BreakingChangeType.REQUIRED_FIELD_ADDED:
            # 새로운 필수 필드 추가
            if rule.field_name not in request.body:
                request.body[rule.field_name] = rule.default_value
        
        return request

class DeprecationManager:
    """Deprecation 관리"""
    
    def __init__(self):
        self.deprecations: Dict[str, DeprecationInfo] = {}
        self.sunset_policy = SunsetPolicy()
        
    async def deprecate_feature(
        self,
        feature_id: str,
        version: str,
        deprecation_date: datetime,
        sunset_date: datetime,
        replacement: Optional[str] = None,
        migration_guide: Optional[str] = None
    ) -> None:
        """기능 Deprecation 등록"""
        
        deprecation = DeprecationInfo(
            feature_id=feature_id,
            deprecated_in_version=version,
            deprecation_date=deprecation_date,
            sunset_date=sunset_date,
            replacement=replacement,
            migration_guide=migration_guide,
            warnings_sent=0
        )
        
        self.deprecations[feature_id] = deprecation
        
        # 알림 스케줄링
        await self.schedule_deprecation_notices(deprecation)
    
    async def check_deprecation(
        self,
        feature_id: str,
        request: Request
    ) -> Optional[DeprecationWarning]:
        """Deprecation 체크"""
        
        if feature_id not in self.deprecations:
            return None
        
        deprecation = self.deprecations[feature_id]
        
        # Sunset 날짜 확인
        if datetime.now() >= deprecation.sunset_date:
            raise FeatureSunsetError(
                f"Feature {feature_id} has been sunset as of {deprecation.sunset_date}"
            )
        
        # Deprecation 경고 생성
        warning = DeprecationWarning(
            feature=feature_id,
            message=f"This feature is deprecated and will be removed on {deprecation.sunset_date}",
            deprecated_since=deprecation.deprecation_date,
            sunset_date=deprecation.sunset_date,
            replacement=deprecation.replacement,
            migration_guide=deprecation.migration_guide
        )
        
        # 응답 헤더에 경고 추가
        request.response_headers['Deprecation'] = 'true'
        request.response_headers['Sunset'] = deprecation.sunset_date.isoformat()
        
        if deprecation.replacement:
            request.response_headers['Link'] = f'<{deprecation.replacement}>; rel="successor-version"'
        
        # 경고 카운트 증가
        deprecation.warnings_sent += 1
        
        return warning
```

**검증 기준**:
- [ ] Breaking change 감지
- [ ] 자동 호환성 변환
- [ ] Deprecation 관리
- [ ] 마이그레이션 가이드

### SubTask 6.4.3: 버전 마이그레이션 도구

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api-gateway/versioning/migration-tool.ts
export class VersionMigrationTool {
  private migrationStrategies: Map<string, MigrationStrategy>;
  private validator: MigrationValidator;
  private rollbackManager: RollbackManager;
  
  constructor() {
    this.migrationStrategies = new Map();
    this.validator = new MigrationValidator();
    this.rollbackManager = new RollbackManager();
    this.initializeStrategies();
  }
  
  async createMigrationPlan(
    fromVersion: string,
    toVersion: string,
    scope: MigrationScope
  ): Promise<MigrationPlan> {
    // 1. 변경 사항 분석
    const changes = await this.analyzeChanges(fromVersion, toVersion);
    
    // 2. 영향 평가
    const impact = await this.assessImpact(changes, scope);
    
    // 3. 마이그레이션 단계 생성
    const steps = this.generateMigrationSteps(changes, impact);
    
    // 4. 검증 계획 수립
    const validationPlan = this.createValidationPlan(steps);
    
    // 5. 롤백 계획 수립
    const rollbackPlan = await this.rollbackManager.createPlan(steps);
    
    return {
      id: generateMigrationId(),
      fromVersion,
      toVersion,
      scope,
      changes,
      impact,
      steps,
      validationPlan,
      rollbackPlan,
      estimatedDuration: this.estimateDuration(steps),
      risk: this.assessRisk(impact)
    };
  }
  
  async executeMigration(
    plan: MigrationPlan,
    options: MigrationOptions = {}
  ): Promise<MigrationResult> {
    const result = new MigrationResult();
    result.planId = plan.id;
    result.startTime = new Date();
    
    try {
      // 1. Pre-migration 검증
      await this.validator.validatePreConditions(plan);
      
      // 2. 백업 생성
      if (options.createBackup) {
        result.backupId = await this.createBackup(plan);
      }
      
      // 3. 단계별 실행
      for (const step of plan.steps) {
        try {
          await this.executeStep(step, result);
          
          // 중간 검증
          if (options.validateAfterEachStep) {
            await this.validator.validateStep(step, result);
          }
          
        } catch (error) {
          result.failedStep = step;
          result.error = error;
          
          if (options.rollbackOnError) {
            await this.rollback(plan, result);
          }
          
          throw error;
        }
      }
      
      // 4. Post-migration 검증
      await this.validator.validatePostConditions(plan, result);
      
      // 5. 정리 작업
      await this.cleanup(plan, result);
      
      result.success = true;
      result.endTime = new Date();
      
    } catch (error) {
      result.success = false;
      result.error = error;
      result.endTime = new Date();
    }
    
    return result;
  }
  
  private async executeStep(
    step: MigrationStep,
    result: MigrationResult
  ): Promise<void> {
    const stepResult = new StepResult();
    stepResult.stepId = step.id;
    stepResult.startTime = new Date();
    
    try {
      // 전략 선택
      const strategy = this.migrationStrategies.get(step.type);
      if (!strategy) {
        throw new Error(`Unknown migration step type: ${step.type}`);
      }
      
      // 실행
      await strategy.execute(step, result.context);
      
      stepResult.success = true;
      
    } catch (error) {
      stepResult.success = false;
      stepResult.error = error;
      throw error;
      
    } finally {
      stepResult.endTime = new Date();
      result.steps.push(stepResult);
    }
  }
  
  async generateMigrationScript(
    plan: MigrationPlan,
    format: 'sql' | 'json' | 'yaml'
  ): Promise<string> {
    const script = new MigrationScriptBuilder();
    
    // 헤더 추가
    script.addHeader({
      planId: plan.id,
      fromVersion: plan.fromVersion,
      toVersion: plan.toVersion,
      generated: new Date(),
      estimatedDuration: plan.estimatedDuration
    });
    
    // 단계별 스크립트 생성
    for (const step of plan.steps) {
      const stepScript = await this.generateStepScript(step, format);
      script.addStep(stepScript);
    }
    
    // 검증 스크립트 추가
    script.addValidation(plan.validationPlan);
    
    // 롤백 스크립트 추가
    script.addRollback(plan.rollbackPlan);
    
    return script.build(format);
  }
}

// 자동 마이그레이션 클라이언트 생성기
export class MigrationClientGenerator {
  async generateClient(
    plan: MigrationPlan,
    language: 'typescript' | 'python' | 'java'
  ): Promise<string> {
    const template = this.getTemplate(language);
    
    return template.render({
      planId: plan.id,
      fromVersion: plan.fromVersion,
      toVersion: plan.toVersion,
      endpoints: plan.changes.endpoints,
      models: plan.changes.models,
      transformations: this.generateTransformations(plan.changes, language)
    });
  }
  
  private generateTransformations(
    changes: VersionChanges,
    language: string
  ): string {
    // 언어별 변환 코드 생성
    switch (language) {
      case 'typescript':
        return this.generateTypeScriptTransformations(changes);
      case 'python':
        return this.generatePythonTransformations(changes);
      case 'java':
        return this.generateJavaTransformations(changes);
    }
  }
}
```

**검증 기준**:
- [ ] 마이그레이션 계획 수립
- [ ] 단계별 실행
- [ ] 롤백 메커니즘
- [ ] 클라이언트 코드 생성

### SubTask 6.4.4: 버전별 문서 자동 생성

**담당자**: 풀스택 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api_gateway/versioning/doc_generator.py
class VersionedDocumentationGenerator:
    """버전별 API 문서 생성기"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.schema_generator = SchemaGenerator()
        self.change_tracker = ChangeTracker()
        
    async def generate_documentation(
        self,
        version: str,
        endpoints: List[VersionedEndpoint],
        options: DocGenerationOptions
    ) -> Documentation:
        """버전별 문서 생성"""
        
        doc = Documentation(
            version=version,
            generated_at=datetime.now(),
            format=options.format
        )
        
        # 1. 개요 섹션
        doc.overview = await self.generate_overview(version, endpoints)
        
        # 2. 변경 사항 섹션
        if options.include_changelog:
            doc.changelog = await self.generate_changelog(version)
        
        # 3. 엔드포인트 문서
        doc.endpoints = await self.document_endpoints(endpoints, options)
        
        # 4. 모델/스키마 문서
        doc.schemas = await self.generate_schemas(endpoints)
        
        # 5. 예제 코드
        if options.include_examples:
            doc.examples = await self.generate_examples(endpoints, options.languages)
        
        # 6. 마이그레이션 가이드
        if options.include_migration:
            doc.migration_guide = await self.generate_migration_guide(version)
        
        # 7. OpenAPI/Swagger 스펙
        if options.generate_openapi:
            doc.openapi_spec = await self.generate_openapi_spec(version, endpoints)
        
        return doc
    
    async def generate_changelog(self, version: str) -> Changelog:
        """변경 로그 생성"""
        
        changelog = Changelog(version=version)
        
        # 이전 버전과 비교
        previous_version = self.get_previous_version(version)
        
        if previous_version:
            changes = await self.change_tracker.get_changes(
                previous_version,
                version
            )
            
            # 변경 사항 분류
            changelog.breaking_changes = [
                c for c in changes if c.is_breaking
            ]
            
            changelog.new_features = [
                c for c in changes if c.type == ChangeType.ADDED
            ]
            
            changelog.improvements = [
                c for c in changes if c.type == ChangeType.IMPROVED
            ]
            
            changelog.deprecations = [
                c for c in changes if c.type == ChangeType.DEPRECATED
            ]
            
            changelog.bug_fixes = [
                c for c in changes if c.type == ChangeType.FIXED
            ]
        
        return changelog
    
    async def generate_interactive_docs(
        self,
        version: str,
        endpoints: List[VersionedEndpoint]
    ) -> str:
        """인터랙티브 문서 생성 (Swagger UI 스타일)"""
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>T-Developer API v{version}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
    <style>
        .version-selector {{
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }}
        .deprecated {{
            opacity: 0.6;
            text-decoration: line-through;
        }}
        .new-endpoint {{
            background: #e8f5e9;
        }}
        .breaking-change {{
            background: #ffebee;
        }}
    </style>
</head>
<body>
    <div class="version-selector">
        <select id="version-select" onchange="switchVersion(this.value)">
            {version_options}
        </select>
    </div>
    
    <div id="swagger-ui"></div>
    
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
        const spec = {openapi_spec};
        
        window.ui = SwaggerUIBundle({{
            spec: spec,
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout",
            onComplete: function() {{
                // 커스텀 스타일 적용
                markDeprecatedEndpoints();
                highlightNewEndpoints();
                showBreakingChanges();
            }}
        }});
        
        function switchVersion(version) {{
            window.location.href = `/docs/api/${{version}}`;
        }}
        
        function markDeprecatedEndpoints() {{
            {deprecation_script}
        }}
        
        function highlightNewEndpoints() {{
            {new_endpoints_script}
        }}
        
        function showBreakingChanges() {{
            {breaking_changes_script}
        }}
    </script>
</body>
</html>
        """
        
        # OpenAPI 스펙 생성
        openapi_spec = await self.generate_openapi_spec(version, endpoints)
        
        # 버전 옵션 생성
        version_options = self.generate_version_options(version)
        
        # 스크립트 생성
        deprecation_script = self.generate_deprecation_script(endpoints)
        new_endpoints_script = self.generate_new_endpoints_script(endpoints)
        breaking_changes_script = self.generate_breaking_changes_script(version)
        
        return html_template.format(
            version=version,
            version_options=version_options,
            openapi_spec=json.dumps(openapi_spec),
            deprecation_script=deprecation_script,
            new_endpoints_script=new_endpoints_script,
            breaking_changes_script=breaking_changes_script
        )
```

**검증 기준**:
- [ ] 버전별 문서 생성
- [ ] 변경 로그 자동화
- [ ] OpenAPI 스펙 생성
- [ ] 인터랙티브 문서

---

## Task 6.5: 게이트웨이 로드 밸런싱

### SubTask 6.5.1: 로드 밸런싱 알고리즘 구현

**담당자**: 시스템 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api-gateway/loadbalancing/algorithms.ts
export interface LoadBalancingAlgorithm {
  name: string;
  selectServer(servers: Server[], request?: Request): Server;
  updateServerStats(server: Server, response: Response): void;
}

// Round Robin 알고리즘
export class RoundRobinAlgorithm implements LoadBalancingAlgorithm {
  name = 'round-robin';
  private currentIndex = 0;
  
  selectServer(servers: Server[]): Server {
    const server = servers[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % servers.length;
    return server;
  }
  
  updateServerStats(server: Server, response: Response): void {
    // Round Robin은 통계 업데이트 불필요
  }
}

// Weighted Round Robin
export class WeightedRoundRobinAlgorithm implements LoadBalancingAlgorithm {
  name = 'weighted-round-robin';
  private currentWeights: Map<string, number> = new Map();
  
  selectServer(servers: Server[]): Server {
    // 가중치 기반 선택
    let totalWeight = 0;
    let selectedServer: Server | null = null;
    
    for (const server of servers) {
      const currentWeight = this.currentWeights.get(server.id) || 0;
      const effectiveWeight = currentWeight + server.weight;
      
      this.currentWeights.set(server.id, effectiveWeight);
      totalWeight += server.weight;
      
      if (!selectedServer || effectiveWeight > this.currentWeights.get(selectedServer.id)!) {
        selectedServer = server;
      }
    }
    
    if (selectedServer) {
      this.currentWeights.set(
        selectedServer.id,
        this.currentWeights.get(selectedServer.id)! - totalWeight
      );
    }
    
    return selectedServer!;
  }
  
  updateServerStats(server: Server, response: Response): void {
    // 응답 시간에 따른 가중치 조정
    if (response.time > server.targetResponseTime * 2) {
      server.weight = Math.max(1, server.weight - 1);
    } else if (response.time < server.targetResponseTime * 0.5) {
      server.weight = Math.min(10, server.weight + 1);
    }
  }
}

// Least Connections
export class LeastConnectionsAlgorithm implements LoadBalancingAlgorithm {
  name = 'least-connections';
  private connections: Map<string, number> = new Map();
  
  selectServer(servers: Server[]): Server {
    let minConnections = Infinity;
    let selectedServer: Server | null = null;
    
    for (const server of servers) {
      const connections = this.connections.get(server.id) || 0;
      
      if (connections < minConnections) {
        minConnections = connections;
        selectedServer = server;
      }
    }
    
    if (selectedServer) {
      this.connections.set(
        selectedServer.id,
        (this.connections.get(selectedServer.id) || 0) + 1
      );
    }
    
    return selectedServer!;
  }
  
  updateServerStats(server: Server, response: Response): void {
    // 연결 완료 시 카운트 감소
    const current = this.connections.get(server.id) || 0;
    this.connections.set(server.id, Math.max(0, current - 1));
  }
}

// IP Hash (Sticky Session)
export class IPHashAlgorithm implements LoadBalancingAlgorithm {
  name = 'ip-hash';
  
  selectServer(servers: Server[], request: Request): Server {
    const ip = request.clientIP;
    const hash = this.hashIP(ip);
    const index = hash % servers.length;
    return servers[index];
  }
  
  private hashIP(ip: string): number {
    let hash = 0;
    for (let i = 0; i < ip.length; i++) {
      hash = ((hash << 5) - hash) + ip.charCodeAt(i);
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }
  
  updateServerStats(server: Server, response: Response): void {
    // IP Hash는 통계 업데이트 불필요
  }
}

// Adaptive Load Balancing
export class AdaptiveLoadBalancer implements LoadBalancingAlgorithm {
  name = 'adaptive';
  private metrics: ServerMetrics;
  private predictor: LoadPredictor;
  
  constructor() {
    this.metrics = new ServerMetrics();
    this.predictor = new LoadPredictor();
  }
  
  selectServer(servers: Server[], request: Request): Server {
    // 1. 현재 메트릭 수집
    const currentMetrics = servers.map(s => ({
      server: s,
      cpu: this.metrics.getCPU(s.id),
      memory: this.metrics.getMemory(s.id),
      responseTime: this.metrics.getAvgResponseTime(s.id),
      errorRate: this.metrics.getErrorRate(s.id),
      activeConnections: this.metrics.getActiveConnections(s.id)
    }));
    
    // 2. 부하 예측
    const predictions = currentMetrics.map(m => ({
      ...m,
      predictedLoad: this.predictor.predict(m, request)
    }));
    
    // 3. 스코어 계산
    const scores = predictions.map(p => ({
      server: p.server,
      score: this.calculateScore(p)
    }));
    
    // 4. 최적 서버 선택
    scores.sort((a, b) => b.score - a.score);
    return scores[0].server;
  }
  
  private calculateScore(metrics: any): number {
    // 가중치 기반 스코어 계산
    const weights = {
      cpu: 0.3,
      memory: 0.2,
      responseTime: 0.3,
      errorRate: 0.1,
      connections: 0.1
    };
    
    return (
      (100 - metrics.cpu) * weights.cpu +
      (100 - metrics.memory) * weights.memory +
      (1000 / (metrics.responseTime + 1)) * weights.responseTime +
      (100 - metrics.errorRate) * weights.errorRate +
      (100 / (metrics.activeConnections + 1)) * weights.connections
    );
  }
  
  updateServerStats(server: Server, response: Response): void {
    this.metrics.update(server.id, {
      responseTime: response.time,
      success: response.status < 500,
      timestamp: Date.now()
    });
  }
}
```

**검증 기준**:
- [ ] 다양한 알고리즘 구현
- [ ] 동적 가중치 조정
- [ ] 세션 유지 지원
- [ ] 적응형 로드 밸런싱

### SubTask 6.5.2: 헬스 체크 및 서비스 디스커버리

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api_gateway/loadbalancing/health_check.py
class HealthChecker:
    """서비스 헬스 체크"""
    
    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self.health_status: Dict[str, ServiceHealth] = {}
        self.check_tasks: Dict[str, asyncio.Task] = {}
        
    async def start_monitoring(self, services: List[Service]) -> None:
        """헬스 체크 모니터링 시작"""
        
        for service in services:
            if service.id not in self.check_tasks:
                task = asyncio.create_task(
                    self.monitor_service(service)
                )
                self.check_tasks[service.id] = task
    
    async def monitor_service(self, service: Service) -> None:
        """개별 서비스 모니터링"""
        
        consecutive_failures = 0
        consecutive_successes = 0
        
        while True:
            try:
                # 헬스 체크 실행
                health = await self.check_health(service)
                
                if health.is_healthy:
                    consecutive_successes += 1
                    consecutive_failures = 0
                    
                    if consecutive_successes >= self.config.healthy_threshold:
                        await self.mark_healthy(service)
                else:
                    consecutive_failures += 1
                    consecutive_successes = 0
                    
                    if consecutive_failures >= self.config.unhealthy_threshold:
                        await self.mark_unhealthy(service)
                
                # 상태 업데이트
                self.health_status[service.id] = health
                
            except Exception as e:
                await self.handle_check_error(service, e)
                
            await asyncio.sleep(self.config.interval)
    
    async def check_health(self, service: Service) -> ServiceHealth:
        """헬스 체크 실행"""
        
        health = ServiceHealth(
            service_id=service.id,
            timestamp=datetime.now()
        )
        
        # HTTP 헬스 체크
        if service.health_check_type == 'http':
            health = await self.http_health_check(service, health)
            
        # TCP 헬스 체크
        elif service.health_check_type == 'tcp':
            health = await self.tcp_health_check(service, health)
            
        # 커스텀 헬스 체크
        elif service.health_check_type == 'custom':
            health = await self.custom_health_check(service, health)
        
        return health
    
    async def http_health_check(
        self,
        service: Service,
        health: ServiceHealth
    ) -> ServiceHealth:
        """HTTP 헬스 체크"""
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service.url}{service.health_check_path}",
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    
                    health.response_time = time.time() - start_time
                    health.status_code = response.status
                    
                    if response.status == 200:
                        # 상세 헬스 정보 파싱
                        if response.content_type == 'application/json':
                            data = await response.json()
                            health.details = data
                            health.is_healthy = data.get('healthy', True)
                        else:
                            health.is_healthy = True
                    else:
                        health.is_healthy = False
                        
        except asyncio.TimeoutError:
            health.is_healthy = False
            health.error = 'Health check timeout'
            
        except Exception as e:
            health.is_healthy = False
            health.error = str(e)
        
        return health

class ServiceDiscovery:
    """서비스 디스커버리"""
    
    def __init__(self, provider: str = 'consul'):
        self.provider = self.init_provider(provider)
        self.cache = ServiceCache()
        self.watchers: List[ServiceWatcher] = []
        
    async def register_service(self, service: Service) -> None:
        """서비스 등록"""
        
        registration = ServiceRegistration(
            id=service.id,
            name=service.name,
            address=service.address,
            port=service.port,
            tags=service.tags,
            meta=service.metadata,
            health_check=HealthCheckDefinition(
                type=service.health_check_type,
                path=service.health_check_path,
                interval=service.health_check_interval,
                timeout=service.health_check_timeout
            )
        )
        
        await self.provider.register(registration)
        await self.cache.add(service)
        await self.notify_watchers('service_registered', service)
    
    async def discover_services(
        self,
        service_name: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Service]:
        """서비스 검색"""
        
        # 캐시 확인
        cached = await self.cache.get(service_name, tags)
        if cached and not self.cache.is_stale(service_name):
            return cached
        
        # Provider에서 조회
        services = await self.provider.discover(service_name, tags)
        
        # 캐시 업데이트
        await self.cache.update(service_name, services)
        
        return services
    
    async def watch_services(
        self,
        callback: Callable,
        service_name: Optional[str] = None
    ) -> ServiceWatcher:
        """서비스 변경 감시"""
        
        watcher = ServiceWatcher(
            callback=callback,
            service_name=service_name
        )
        
        self.watchers.append(watcher)
        
        # Provider 감시 시작
        await self.provider.watch(
            service_name,
            lambda changes: self.handle_changes(changes, watcher)
        )
        
        return watcher
```

**검증 기준**:
- [ ] 다양한 헬스 체크 방식
- [ ] 서비스 자동 등록/해제
- [ ] 실시간 서비스 감시
- [ ] 캐싱 메커니즘

### SubTask 6.5.3: 트래픽 분산 정책 엔진

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 14시간

**작업 내용**:

```typescript
// backend/src/api-gateway/loadbalancing/traffic-policy.ts
export interface TrafficPolicy {
  id: string;
  name: string;
  conditions: PolicyCondition[];
  actions: PolicyAction[];
  priority: number;
  enabled: boolean;
}

export class TrafficPolicyEngine {
  private policies: Map<string, TrafficPolicy> = new Map();
  private policyEvaluator: PolicyEvaluator;
  private actionExecutor: ActionExecutor;
  
  constructor() {
    this.policyEvaluator = new PolicyEvaluator();
    this.actionExecutor = new ActionExecutor();
    this.initializeDefaultPolicies();
  }
  
  private initializeDefaultPolicies(): void {
    // Canary 배포 정책
    this.addPolicy({
      id: 'canary-deployment',
      name: 'Canary Deployment Policy',
      conditions: [
        {
          type: 'header',
          field: 'x-canary',
          operator: 'equals',
          value: 'true'
        }
      ],
      actions: [
        {
          type: 'route',
          target: 'canary-servers',
          weight: 100
        }
      ],
      priority: 100,
      enabled: true
    });
    
    // A/B 테스팅 정책
    this.addPolicy({
      id: 'ab-testing',
      name: 'A/B Testing Policy',
      conditions: [
        {
          type: 'cookie',
          field: 'experiment-group',
          operator: 'exists'
        }
      ],
      actions: [
        {
          type: 'split',
          splits: [
            { group: 'A', weight: 50, target: 'version-a' },
            { group: 'B', weight: 50, target: 'version-b' }
          ]
        }
      ],
      priority: 90,
      enabled: true
    });
    
    // 지역 기반 라우팅
    this.addPolicy({
      id: 'geo-routing',
      name: 'Geographic Routing Policy',
      conditions: [
        {
          type: 'geo',
          field: 'country',
          operator: 'in',
          value: ['KR', 'JP', 'CN']
        }
      ],
      actions: [
        {
          type: 'route',
          target: 'asia-servers',
          weight: 100
        }
      ],
      priority: 80,
      enabled: true
    });
  }
  
  async evaluatePolicies(
    request: Request,
    availableServers: Server[]
  ): Promise<RoutingDecision> {
    // 활성화된 정책을 우선순위 순으로 정렬
    const activePolicies = Array.from(this.policies.values())
      .filter(p => p.enabled)
      .sort((a, b) => b.priority - a.priority);
    
    for (const policy of activePolicies) {
      // 조건 평가
      const matches = await this.policyEvaluator.evaluate(
        policy.conditions,
        request
      );
      
      if (matches) {
        // 액션 실행
        const decision = await this.actionExecutor.execute(
          policy.actions,
          request,
          availableServers
        );
        
        if (decision) {
          return {
            ...decision,
            appliedPolicy: policy.id
          };
        }
      }
    }
    
    // 기본 라우팅 결정
    return {
      servers: availableServers,
      strategy: 'default',
      appliedPolicy: 'none'
    };
  }
  
  async addDynamicPolicy(
    policy: TrafficPolicy,
    validateConflicts: boolean = true
  ): Promise<void> {
    if (validateConflicts) {
      const conflicts = await this.detectConflicts(policy);
      if (conflicts.length > 0) {
        throw new PolicyConflictError(
          `Policy conflicts detected: ${conflicts.join(', ')}`
        );
      }
    }
    
    this.policies.set(policy.id, policy);
    await this.reorderPolicies();
  }
}

// 트래픽 쉐이핑
export class TrafficShaper {
  private rateLimiters: Map<string, RateLimiter> = new Map();
  private throttlers: Map<string, Throttler> = new Map();
  
  async shapeTraffic(
    request: Request,
    policy: TrafficShapingPolicy
  ): Promise<ShapingResult> {
    const result = new ShapingResult();
    
    // 1. Rate Limiting
    if (policy.rateLimit) {
      const limiter = this.getRateLimiter(policy.rateLimit);
      const allowed = await limiter.tryAcquire(request);
      
      if (!allowed) {
        result.rejected = true;
        result.reason = 'rate_limit_exceeded';
        result.retryAfter = limiter.getRetryAfter();
        return result;
      }
    }
    
    // 2. Throttling
    if (policy.throttle) {
      const throttler = this.getThrottler(policy.throttle);
      const delay = await throttler.calculateDelay(request);
      
      if (delay > 0) {
        result.delayed = true;
        result.delay = delay;
        await this.delay(delay);
      }
    }
    
    // 3. Burst Control
    if (policy.burstControl) {
      const burstAllowed = await this.checkBurst(request, policy.burstControl);
      if (!burstAllowed) {
        result.rejected = true;
        result.reason = 'burst_limit_exceeded';
        return result;
      }
    }
    
    // 4. Circuit Breaking
    if (policy.circuitBreaker) {
      const circuit = this.getCircuitBreaker(policy.circuitBreaker);
      if (circuit.isOpen()) {
        result.rejected = true;
        result.reason = 'circuit_open';
        result.fallback = policy.circuitBreaker.fallback;
        return result;
      }
    }
    
    result.allowed = true;
    return result;
  }
}
```

**검증 기준**:
- [ ] 정책 기반 라우팅
- [ ] 트래픽 쉐이핑
- [ ] A/B 테스팅 지원
- [ ] Circuit Breaker 패턴

### SubTask 6.5.4: 자동 스케일링 통합

**담당자**: DevOps 엔지니어  
**예상 소요시간**: 14시간

**작업 내용**:

```python
# backend/src/api_gateway/loadbalancing/auto_scaling.py
class AutoScalingManager:
    """자동 스케일링 관리"""
    
    def __init__(self, config: AutoScalingConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.scaling_engine = ScalingEngine()
        self.cloud_provider = self.init_cloud_provider()
        
    async def monitor_and_scale(self) -> None:
        """모니터링 및 스케일링 루프"""
        
        while True:
            try:
                # 1. 메트릭 수집
                metrics = await self.collect_metrics()
                
                # 2. 스케일링 결정
                decision = await self.make_scaling_decision(metrics)
                
                # 3. 스케일링 실행
                if decision.action != ScalingAction.NONE:
                    await self.execute_scaling(decision)
                
                # 4. 쿨다운 기간
                await asyncio.sleep(self.config.evaluation_period)
                
            except Exception as e:
                await self.handle_scaling_error(e)
    
    async def make_scaling_decision(
        self,
        metrics: SystemMetrics
    ) -> ScalingDecision:
        """스케일링 결정"""
        
        decision = ScalingDecision(
            action=ScalingAction.NONE,
            reason='',
            target_capacity=self.current_capacity
        )
        
        # CPU 기반 스케일링
        if self.config.cpu_scaling:
            if metrics.avg_cpu > self.config.scale_up_threshold:
                decision.action = ScalingAction.SCALE_UP
                decision.reason = f'CPU usage {metrics.avg_cpu}% > {self.config.scale_up_threshold}%'
                decision.target_capacity = self.calculate_scale_up_capacity()
                
            elif metrics.avg_cpu < self.config.scale_down_threshold:
                decision.action = ScalingAction.SCALE_DOWN
                decision.reason = f'CPU usage {metrics.avg_cpu}% < {self.config.scale_down_threshold}%'
                decision.target_capacity = self.calculate_scale_down_capacity()
        
        # 요청 수 기반 스케일링
        if self.config.request_scaling:
            requests_per_instance = metrics.total_requests / self.current_capacity
            
            if requests_per_instance > self.config.max_requests_per_instance:
                decision.action = ScalingAction.SCALE_UP
                decision.reason = f'Requests per instance {requests_per_instance} > {self.config.max_requests_per_instance}'
                decision.target_capacity = math.ceil(
                    metrics.total_requests / self.config.target_requests_per_instance
                )
        
        # 예측 기반 스케일링
        if self.config.predictive_scaling:
            predicted_load = await self.predict_future_load(metrics)
            
            if predicted_load > self.config.predictive_threshold:
                decision.action = ScalingAction.SCALE_UP
                decision.reason = f'Predicted load {predicted_load} > {self.config.predictive_threshold}'
                decision.target_capacity = self.calculate_predictive_capacity(predicted_load)
        
        # 제약 조건 확인
        decision = self.apply_constraints(decision)
        
        return decision
    
    async def execute_scaling(self, decision: ScalingDecision) -> None:
        """스케일링 실행"""
        
        # 1. 스케일링 이벤트 기록
        await self.log_scaling_event(decision)
        
        # 2. 인스턴스 조정
        if decision.action == ScalingAction.SCALE_UP:
            await self.scale_up(decision.target_capacity)
        elif decision.action == ScalingAction.SCALE_DOWN:
            await self.scale_down(decision.target_capacity)
        
        # 3. 로드 밸런서 업데이트
        await self.update_load_balancer()
        
        # 4. 헬스 체크 대기
        await self.wait_for_healthy_state()
        
        # 5. 메트릭 업데이트
        self.current_capacity = decision.target_capacity
        await self.metrics_collector.record_scaling(decision)
    
    async def scale_up(self, target_capacity: int) -> None:
        """스케일 업 실행"""
        
        instances_to_add = target_capacity - self.current_capacity
        
        # 인스턴스 시작
        new_instances = await self.cloud_provider.launch_instances(
            count=instances_to_add,
            instance_type=self.config.instance_type,
            ami_id=self.config.ami_id,
            security_groups=self.config.security_groups,
            subnet_ids=self.config.subnet_ids,
            user_data=self.generate_user_data()
        )
        
        # 인스턴스 초기화 대기
        await self.wait_for_instances_ready(new_instances)
        
        # 로드 밸런서에 추가
        await self.register_instances(new_instances)
    
    async def scale_down(self, target_capacity: int) -> None:
        """스케일 다운 실행"""
        
        instances_to_remove = self.current_capacity - target_capacity
        
        # 제거할 인스턴스 선택
        instances = await self.select_instances_to_terminate(instances_to_remove)
        
        # 로드 밸런서에서 제거
        await self.deregister_instances(instances)
        
        # 연결 드레이닝
        await self.drain_connections(instances)
        
        # 인스턴스 종료
        await self.cloud_provider.terminate_instances(instances)
    
    async def predict_future_load(
        self,
        current_metrics: SystemMetrics
    ) -> float:
        """미래 부하 예측"""
        
        # 시계열 데이터 수집
        historical_data = await self.metrics_collector.get_historical_metrics(
            duration=timedelta(hours=24)
        )
        
        # ML 모델을 사용한 예측
        predictor = LoadPredictor(model='lstm')
        predicted_load = predictor.predict(
            historical_data,
            forecast_horizon=timedelta(minutes=30)
        )
        
        return predicted_load
```

**검증 기준**:
- [ ] 다양한 스케일링 트리거
- [ ] 예측 기반 스케일링
- [ ] 클라우드 프로바이더 통합
- [ ] 안전한 스케일 다운

---

## 📊 Phase 6 Task 6.1-6.5 완료 현황

### ✅ 완료된 작업
- **Task 6.1**: API Gateway 아키텍처 설계 (4 SubTasks)
- **Task 6.2**: 라우팅 및 엔드포인트 관리 (4 SubTasks)
- **Task 6.3**: 요청/응답 변환 레이어 (4 SubTasks)
- **Task 6.4**: API 버전 관리 시스템 (4 SubTasks)
- **Task 6.5**: 게이트웨이 로드 밸런싱 (4 SubTasks)

### 📈 진행률
- Tasks 6.1-6.5 진행률: 100%
- 총 20개 SubTasks 완료
- 예상 소요시간: 240시간

### 🎯 주요 성과
1. **완전한 API Gateway 구축**
   - 9개 에이전트 통합 지원
   - 다양한 프로토콜 지원
   - 고가용성 아키텍처

2. **고급 라우팅 기능**
   - 동적 라우팅 엔진
   - 경로 매칭 및 파라미터 처리
   - 라우팅 규칙 관리

3. **프로토콜 변환**
   - 다양한 포맷 지원
   - 요청/응답 변환
   - 데이터 파이프라인

4. **버전 관리**
   - 다양한 버전 전략
   - 하위 호환성 관리
   - 자동 마이그레이션

5. **로드 밸런싱**
   - 다양한 알고리즘
   - 헬스 체크 및 서비스 디스커버리
   - 자동 스케일링 통합

---
## Phase 6: RESTful API 구현 (Tasks 6.6-6.10) - SubTask 리스트 및 작업지시서

### 📋 SubTask 전체 리스트

#### Task 6.6: REST 엔드포인트 설계
- **SubTask 6.6.1**: RESTful 리소스 모델링
- **SubTask 6.6.2**: URL 구조 및 네이밍 규칙
- **SubTask 6.6.3**: HTTP 메서드 매핑
- **SubTask 6.6.4**: 리소스 관계 및 중첩 구조

#### Task 6.7: CRUD 작업 구현
- **SubTask 6.7.1**: Create 작업 구현
- **SubTask 6.7.2**: Read 작업 구현
- **SubTask 6.7.3**: Update 작업 구현
- **SubTask 6.7.4**: Delete 작업 구현

#### Task 6.8: 페이지네이션 및 필터링
- **SubTask 6.8.1**: 페이지네이션 전략 구현
- **SubTask 6.8.2**: 필터링 시스템 구축
- **SubTask 6.8.3**: 정렬 및 검색 기능
- **SubTask 6.8.4**: 커서 기반 페이지네이션

#### Task 6.9: 응답 포맷 표준화
- **SubTask 6.9.1**: 응답 구조 표준 정의
- **SubTask 6.9.2**: HATEOAS 구현
- **SubTask 6.9.3**: 콘텐츠 협상 처리
- **SubTask 6.9.4**: 응답 메타데이터 관리

#### Task 6.10: RESTful 에러 처리
- **SubTask 6.10.1**: 에러 응답 표준화
- **SubTask 6.10.2**: HTTP 상태 코드 매핑
- **SubTask 6.10.3**: 문제 세부사항 (RFC 7807) 구현
- **SubTask 6.10.4**: 에러 복구 및 재시도 전략

---

## 📝 세부 작업지시서

### Task 6.6: REST 엔드포인트 설계

#### SubTask 6.6.1: RESTful 리소스 모델링

**담당자**: API 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api/rest/resource-modeling.ts
export interface Resource {
  id: string;
  type: string;
  attributes: Record<string, any>;
  relationships?: Record<string, Relationship>;
  links?: ResourceLinks;
  meta?: Record<string, any>;
}

export interface Relationship {
  data: ResourceIdentifier | ResourceIdentifier[];
  links?: RelationshipLinks;
  meta?: Record<string, any>;
}

export class ResourceModeler {
  private resources: Map<string, ResourceDefinition> = new Map();
  
  constructor() {
    this.initializeResources();
  }
  
  private initializeResources(): void {
    // T-Developer 핵심 리소스 정의
    
    // 프로젝트 리소스
    this.defineResource({
      name: 'project',
      plural: 'projects',
      attributes: [
        { name: 'name', type: 'string', required: true },
        { name: 'description', type: 'string' },
        { name: 'framework', type: 'string', enum: ['react', 'vue', 'angular'] },
        { name: 'status', type: 'string', enum: ['draft', 'active', 'completed'] },
        { name: 'createdAt', type: 'datetime', readonly: true },
        { name: 'updatedAt', type: 'datetime', readonly: true }
      ],
      relationships: [
        { name: 'owner', type: 'user', cardinality: 'one' },
        { name: 'components', type: 'component', cardinality: 'many' },
        { name: 'agents', type: 'agent-execution', cardinality: 'many' }
      ],
      actions: ['create', 'read', 'update', 'delete', 'generate', 'export']
    });
    
    // 컴포넌트 리소스
    this.defineResource({
      name: 'component',
      plural: 'components',
      attributes: [
        { name: 'name', type: 'string', required: true },
        { name: 'type', type: 'string', required: true },
        { name: 'category', type: 'string' },
        { name: 'code', type: 'text' },
        { name: 'style', type: 'text' },
        { name: 'props', type: 'json' },
        { name: 'dependencies', type: 'array' },
        { name: 'version', type: 'string' }
      ],
      relationships: [
        { name: 'project', type: 'project', cardinality: 'one' },
        { name: 'parent', type: 'component', cardinality: 'one' },
        { name: 'children', type: 'component', cardinality: 'many' },
        { name: 'usedBy', type: 'component', cardinality: 'many' }
      ],
      actions: ['create', 'read', 'update', 'delete', 'duplicate', 'validate']
    });
    
    // 에이전트 실행 리소스
    this.defineResource({
      name: 'agent-execution',
      plural: 'agent-executions',
      attributes: [
        { name: 'agentType', type: 'string', required: true },
        { name: 'status', type: 'string', enum: ['pending', 'running', 'completed', 'failed'] },
        { name: 'input', type: 'json' },
        { name: 'output', type: 'json' },
        { name: 'startedAt', type: 'datetime' },
        { name: 'completedAt', type: 'datetime' },
        { name: 'duration', type: 'number' },
        { name: 'error', type: 'json' }
      ],
      relationships: [
        { name: 'project', type: 'project', cardinality: 'one' },
        { name: 'triggeredBy', type: 'user', cardinality: 'one' },
        { name: 'dependsOn', type: 'agent-execution', cardinality: 'many' }
      ],
      actions: ['create', 'read', 'cancel', 'retry']
    });
    
    // 사용자 리소스
    this.defineResource({
      name: 'user',
      plural: 'users',
      attributes: [
        { name: 'email', type: 'string', required: true, unique: true },
        { name: 'name', type: 'string' },
        { name: 'role', type: 'string', enum: ['admin', 'developer', 'viewer'] },
        { name: 'preferences', type: 'json' },
        { name: 'lastLogin', type: 'datetime' }
      ],
      relationships: [
        { name: 'projects', type: 'project', cardinality: 'many' },
        { name: 'teams', type: 'team', cardinality: 'many' }
      ],
      actions: ['create', 'read', 'update', 'delete', 'authenticate']
    });
  }
  
  defineResource(definition: ResourceDefinition): void {
    this.resources.set(definition.name, definition);
    
    // 자동으로 collection 리소스도 정의
    this.defineCollectionResource(definition);
    
    // 관계 검증
    this.validateRelationships(definition);
  }
  
  generateResourceSchema(resourceName: string): JSONSchema {
    const definition = this.resources.get(resourceName);
    if (!definition) {
      throw new Error(`Resource ${resourceName} not found`);
    }
    
    const schema: JSONSchema = {
      $schema: 'http://json-schema.org/draft-07/schema#',
      type: 'object',
      title: definition.name,
      properties: {
        id: { type: 'string', format: 'uuid' },
        type: { type: 'string', const: definition.name }
      },
      required: ['id', 'type']
    };
    
    // 속성 스키마 생성
    const attributesSchema: JSONSchema = {
      type: 'object',
      properties: {},
      required: []
    };
    
    for (const attr of definition.attributes) {
      attributesSchema.properties![attr.name] = this.attributeToSchema(attr);
      if (attr.required) {
        attributesSchema.required!.push(attr.name);
      }
    }
    
    schema.properties!.attributes = attributesSchema;
    
    // 관계 스키마 생성
    if (definition.relationships.length > 0) {
      schema.properties!.relationships = this.relationshipsToSchema(definition.relationships);
    }
    
    return schema;
  }
}

// 리소스 변환기
export class ResourceTransformer {
  transform(entity: any, resourceType: string): Resource {
    const definition = this.getResourceDefinition(resourceType);
    
    const resource: Resource = {
      id: entity.id || entity._id || generateId(),
      type: resourceType,
      attributes: {},
      relationships: {},
      links: {
        self: `/api/${definition.plural}/${entity.id}`
      }
    };
    
    // 속성 변환
    for (const attr of definition.attributes) {
      if (entity[attr.name] !== undefined) {
        resource.attributes[attr.name] = this.transformAttribute(
          entity[attr.name],
          attr
        );
      }
    }
    
    // 관계 변환
    for (const rel of definition.relationships) {
      if (entity[rel.name]) {
        resource.relationships![rel.name] = this.transformRelationship(
          entity[rel.name],
          rel
        );
      }
    }
    
    return resource;
  }
  
  private transformRelationship(data: any, relationship: RelationshipDefinition): Relationship {
    if (relationship.cardinality === 'one') {
      return {
        data: {
          type: relationship.type,
          id: typeof data === 'object' ? data.id : data
        },
        links: {
          self: `/api/${relationship.type}s/${data.id || data}`,
          related: `/api/${this.currentResource}/relationships/${relationship.name}`
        }
      };
    } else {
      const items = Array.isArray(data) ? data : [data];
      return {
        data: items.map(item => ({
          type: relationship.type,
          id: typeof item === 'object' ? item.id : item
        })),
        links: {
          self: `/api/${this.currentResource}/relationships/${relationship.name}`,
          related: `/api/${this.currentResource}/${relationship.name}`
        }
      };
    }
  }
}
```

**검증 기준**:
- [ ] 리소스 정의 완성도
- [ ] 관계 모델링 정확성
- [ ] JSON Schema 생성
- [ ] 변환 로직 구현

#### SubTask 6.6.2: URL 구조 및 네이밍 규칙

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/rest/url_structure.py
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

@dataclass
class URLPattern:
    """URL 패턴 정의"""
    pattern: str
    resource: str
    action: str
    method: str
    parameters: List[str]
    description: str

class RESTfulURLBuilder:
    """RESTful URL 구조 빌더"""
    
    def __init__(self):
        self.base_path = "/api/v1"
        self.patterns: List[URLPattern] = []
        self.naming_rules = NamingRules()
        self.initialize_patterns()
    
    def initialize_patterns(self):
        """T-Developer API URL 패턴 초기화"""
        
        # 프로젝트 관련 URL
        self.add_patterns([
            # Collection operations
            URLPattern(
                pattern="/projects",
                resource="project",
                action="list",
                method="GET",
                parameters=[],
                description="List all projects"
            ),
            URLPattern(
                pattern="/projects",
                resource="project",
                action="create",
                method="POST",
                parameters=[],
                description="Create a new project"
            ),
            
            # Instance operations
            URLPattern(
                pattern="/projects/{projectId}",
                resource="project",
                action="get",
                method="GET",
                parameters=["projectId"],
                description="Get a specific project"
            ),
            URLPattern(
                pattern="/projects/{projectId}",
                resource="project",
                action="update",
                method="PUT",
                parameters=["projectId"],
                description="Update a project"
            ),
            URLPattern(
                pattern="/projects/{projectId}",
                resource="project",
                action="partial_update",
                method="PATCH",
                parameters=["projectId"],
                description="Partially update a project"
            ),
            URLPattern(
                pattern="/projects/{projectId}",
                resource="project",
                action="delete",
                method="DELETE",
                parameters=["projectId"],
                description="Delete a project"
            ),
            
            # Nested resources
            URLPattern(
                pattern="/projects/{projectId}/components",
                resource="component",
                action="list",
                method="GET",
                parameters=["projectId"],
                description="List project components"
            ),
            URLPattern(
                pattern="/projects/{projectId}/components/{componentId}",
                resource="component",
                action="get",
                method="GET",
                parameters=["projectId", "componentId"],
                description="Get a specific component"
            ),
            
            # Custom actions
            URLPattern(
                pattern="/projects/{projectId}/generate",
                resource="project",
                action="generate",
                method="POST",
                parameters=["projectId"],
                description="Generate project code"
            ),
            URLPattern(
                pattern="/projects/{projectId}/export",
                resource="project",
                action="export",
                method="GET",
                parameters=["projectId"],
                description="Export project"
            ),
            
            # Agent executions
            URLPattern(
                pattern="/projects/{projectId}/agents/{agentType}/execute",
                resource="agent",
                action="execute",
                method="POST",
                parameters=["projectId", "agentType"],
                description="Execute an agent"
            ),
            URLPattern(
                pattern="/projects/{projectId}/agents/executions",
                resource="agent-execution",
                action="list",
                method="GET",
                parameters=["projectId"],
                description="List agent executions"
            )
        ])
        
        # 컴포넌트 라이브러리 URL
        self.add_patterns([
            URLPattern(
                pattern="/components/library",
                resource="component",
                action="search",
                method="GET",
                parameters=[],
                description="Search component library"
            ),
            URLPattern(
                pattern="/components/library/{componentId}",
                resource="component",
                action="get",
                method="GET",
                parameters=["componentId"],
                description="Get library component"
            ),
            URLPattern(
                pattern="/components/library/{componentId}/fork",
                resource="component",
                action="fork",
                method="POST",
                parameters=["componentId"],
                description="Fork a library component"
            )
        ])
    
    def build_url(
        self,
        resource: str,
        action: str,
        params: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, str]] = None
    ) -> str:
        """URL 생성"""
        
        # 패턴 찾기
        pattern = self.find_pattern(resource, action)
        if not pattern:
            raise ValueError(f"No pattern found for {resource}.{action}")
        
        # URL 구성
        url = self.base_path + pattern.pattern
        
        # 파라미터 치환
        if params:
            for param_name, param_value in params.items():
                placeholder = f"{{{param_name}}}"
                if placeholder in url:
                    url = url.replace(placeholder, str(param_value))
        
        # 쿼리 스트링 추가
        if query:
            query_string = self.build_query_string(query)
            url += f"?{query_string}"
        
        return url
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """URL 유효성 검증"""
        
        # 기본 형식 검증
        if not url.startswith(self.base_path):
            return False, f"URL must start with {self.base_path}"
        
        # 네이밍 규칙 검증
        path = url[len(self.base_path):]
        segments = path.split('/')
        
        for segment in segments:
            if segment and not self.naming_rules.validate_segment(segment):
                return False, f"Invalid segment: {segment}"
        
        # 패턴 매칭 검증
        matched = False
        for pattern in self.patterns:
            if self.match_pattern(url, pattern):
                matched = True
                break
        
        if not matched:
            return False, "URL does not match any defined pattern"
        
        return True, None

class NamingRules:
    """네이밍 규칙 관리"""
    
    def __init__(self):
        self.rules = {
            'case': 'kebab-case',  # kebab-case for URLs
            'plural': True,         # Use plural for collections
            'max_length': 50,       # Maximum segment length
            'allowed_chars': r'^[a-z0-9\-]+$'  # Allowed characters
        }
    
    def validate_segment(self, segment: str) -> bool:
        """세그먼트 유효성 검증"""
        
        # 파라미터는 제외
        if segment.startswith('{') and segment.endswith('}'):
            return True
        
        # 길이 검증
        if len(segment) > self.rules['max_length']:
            return False
        
        # 문자 검증
        if not re.match(self.rules['allowed_chars'], segment):
            return False
        
        # 케이스 검증
        if self.rules['case'] == 'kebab-case':
            if segment != segment.lower():
                return False
            if '__' in segment or segment.startswith('-') or segment.endswith('-'):
                return False
        
        return True
    
    def format_resource_name(self, name: str, plural: bool = True) -> str:
        """리소스 이름 포맷팅"""
        
        # CamelCase to kebab-case
        formatted = re.sub('([A-Z]+)', r'-\1', name).lower()
        formatted = formatted.strip('-')
        
        # 복수형 변환
        if plural and self.rules['plural']:
            formatted = self.pluralize(formatted)
        
        return formatted
    
    def pluralize(self, word: str) -> str:
        """단어 복수형 변환"""
        
        # 특별 규칙
        irregular = {
            'person': 'people',
            'child': 'children',
            'man': 'men',
            'woman': 'women',
            'foot': 'feet',
            'tooth': 'teeth',
            'goose': 'geese',
            'mouse': 'mice'
        }
        
        if word in irregular:
            return irregular[word]
        
        # 일반 규칙
        if word.endswith('y') and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        elif word.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z')):
            return word + 'es'
        elif word.endswith('f'):
            return word[:-1] + 'ves'
        elif word.endswith('fe'):
            return word[:-2] + 'ves'
        else:
            return word + 's'

# URL 문서 생성기
class URLDocumentationGenerator:
    """URL 구조 문서 생성"""
    
    def generate_documentation(self, patterns: List[URLPattern]) -> str:
        """마크다운 형식의 URL 문서 생성"""
        
        doc = "# API URL Structure\n\n"
        doc += "## Base URL\n"
        doc += "```\nhttps://api.t-developer.com/api/v1\n```\n\n"
        
        # 리소스별 그룹핑
        grouped = self.group_by_resource(patterns)
        
        for resource, resource_patterns in grouped.items():
            doc += f"## {resource.title()} Resource\n\n"
            
            for pattern in resource_patterns:
                doc += f"### {pattern.description}\n"
                doc += f"- **Method**: `{pattern.method}`\n"
                doc += f"- **URL**: `{pattern.pattern}`\n"
                
                if pattern.parameters:
                    doc += f"- **Parameters**: {', '.join(f'`{p}`' for p in pattern.parameters)}\n"
                
                doc += "\n"
                
                # 예제 추가
                example_url = self.generate_example_url(pattern)
                doc += f"**Example**:\n```\n{pattern.method} {example_url}\n```\n\n"
        
        return doc
```

**검증 기준**:
- [ ] URL 패턴 정의
- [ ] 네이밍 규칙 적용
- [ ] URL 유효성 검증
- [ ] 문서 자동 생성

#### SubTask 6.6.3: HTTP 메서드 매핑

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/rest/http-method-mapper.ts
export enum HTTPMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH',
  DELETE = 'DELETE',
  HEAD = 'HEAD',
  OPTIONS = 'OPTIONS'
}

export interface MethodMapping {
  method: HTTPMethod;
  action: string;
  description: string;
  idempotent: boolean;
  safe: boolean;
  requestBody: boolean;
  responseBody: boolean;
  cacheable: boolean;
}

export class HTTPMethodMapper {
  private mappings: Map<string, MethodMapping> = new Map();
  
  constructor() {
    this.initializeMappings();
  }
  
  private initializeMappings(): void {
    // 표준 CRUD 매핑
    this.addMapping({
      method: HTTPMethod.GET,
      action: 'retrieve',
      description: 'Retrieve resource(s)',
      idempotent: true,
      safe: true,
      requestBody: false,
      responseBody: true,
      cacheable: true
    });
    
    this.addMapping({
      method: HTTPMethod.POST,
      action: 'create',
      description: 'Create new resource',
      idempotent: false,
      safe: false,
      requestBody: true,
      responseBody: true,
      cacheable: false
    });
    
    this.addMapping({
      method: HTTPMethod.PUT,
      action: 'replace',
      description: 'Replace entire resource',
      idempotent: true,
      safe: false,
      requestBody: true,
      responseBody: true,
      cacheable: false
    });
    
    this.addMapping({
      method: HTTPMethod.PATCH,
      action: 'update',
      description: 'Partially update resource',
      idempotent: false,
      safe: false,
      requestBody: true,
      responseBody: true,
      cacheable: false
    });
    
    this.addMapping({
      method: HTTPMethod.DELETE,
      action: 'remove',
      description: 'Delete resource',
      idempotent: true,
      safe: false,
      requestBody: false,
      responseBody: false,
      cacheable: false
    });
    
    // 특수 작업 매핑
    this.addMapping({
      method: HTTPMethod.HEAD,
      action: 'check',
      description: 'Check resource existence',
      idempotent: true,
      safe: true,
      requestBody: false,
      responseBody: false,
      cacheable: true
    });
    
    this.addMapping({
      method: HTTPMethod.OPTIONS,
      action: 'describe',
      description: 'Get allowed methods',
      idempotent: true,
      safe: true,
      requestBody: false,
      responseBody: true,
      cacheable: true
    });
  }
  
  mapActionToMethod(action: string, context?: ActionContext): HTTPMethod {
    // 표준 액션 매핑
    const standardMappings: Record<string, HTTPMethod> = {
      'list': HTTPMethod.GET,
      'get': HTTPMethod.GET,
      'create': HTTPMethod.POST,
      'update': HTTPMethod.PUT,
      'patch': HTTPMethod.PATCH,
      'delete': HTTPMethod.DELETE,
      'search': HTTPMethod.GET,
      'filter': HTTPMethod.GET
    };
    
    // 커스텀 액션 매핑 (T-Developer 특화)
    const customMappings: Record<string, HTTPMethod> = {
      'generate': HTTPMethod.POST,    // 코드 생성
      'execute': HTTPMethod.POST,     // 에이전트 실행
      'analyze': HTTPMethod.POST,     // 분석 실행
      'validate': HTTPMethod.POST,    // 검증 실행
      'export': HTTPMethod.GET,       // 내보내기
      'import': HTTPMethod.POST,      // 가져오기
      'duplicate': HTTPMethod.POST,   // 복제
      'fork': HTTPMethod.POST,        // 포크
      'merge': HTTPMethod.POST,       // 병합
      'preview': HTTPMethod.GET,      // 미리보기
      'download': HTTPMethod.GET,     // 다운로드
      'upload': HTTPMethod.POST       // 업로드
    };
    
    // 우선순위: 커스텀 > 표준
    if (customMappings[action]) {
      return customMappings[action];
    }
    
    if (standardMappings[action]) {
      return standardMappings[action];
    }
    
    // 컨텍스트 기반 추론
    if (context) {
      return this.inferMethodFromContext(action, context);
    }
    
    // 기본값
    return HTTPMethod.POST;
  }
  
  private inferMethodFromContext(action: string, context: ActionContext): HTTPMethod {
    // 액션 이름 분석
    const actionLower = action.toLowerCase();
    
    // 읽기 작업 패턴
    const readPatterns = ['get', 'fetch', 'retrieve', 'find', 'list', 'search', 'show', 'view'];
    if (readPatterns.some(pattern => actionLower.includes(pattern))) {
      return HTTPMethod.GET;
    }
    
    // 생성 작업 패턴
    const createPatterns = ['create', 'add', 'new', 'generate', 'build', 'make'];
    if (createPatterns.some(pattern => actionLower.includes(pattern))) {
      return HTTPMethod.POST;
    }
    
    // 업데이트 작업 패턴
    const updatePatterns = ['update', 'edit', 'modify', 'change', 'set'];
    if (updatePatterns.some(pattern => actionLower.includes(pattern))) {
      return context.partial ? HTTPMethod.PATCH : HTTPMethod.PUT;
    }
    
    // 삭제 작업 패턴
    const deletePatterns = ['delete', 'remove', 'destroy', 'clear'];
    if (deletePatterns.some(pattern => actionLower.includes(pattern))) {
      return HTTPMethod.DELETE;
    }
    
    return HTTPMethod.POST;
  }
  
  validateMethodUsage(method: HTTPMethod, operation: Operation): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    const mapping = this.getMappingForMethod(method);
    
    // GET 메서드 검증
    if (method === HTTPMethod.GET) {
      if (operation.requestBody && Object.keys(operation.requestBody).length > 0) {
        errors.push('GET requests should not have a request body');
      }
      if (operation.sideEffects) {
        errors.push('GET requests must be safe (no side effects)');
      }
    }
    
    // DELETE 메서드 검증
    if (method === HTTPMethod.DELETE) {
      if (operation.responseBody && operation.responseBody !== '204 No Content') {
        warnings.push('DELETE requests typically return 204 No Content');
      }
    }
    
    // PUT vs PATCH 검증
    if (method === HTTPMethod.PUT && operation.partial) {
      warnings.push('Consider using PATCH for partial updates');
    }
    
    if (method === HTTPMethod.PATCH && !operation.partial) {
      warnings.push('PATCH should be used for partial updates only');
    }
    
    // POST 멱등성 경고
    if (method === HTTPMethod.POST && operation.idempotent) {
      warnings.push('POST is not idempotent by default, consider PUT');
    }
    
    // 캐싱 검증
    if (operation.cacheable && !mapping?.cacheable) {
      errors.push(`${method} responses should not be cached`);
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }
}

// 메서드 오버라이드 핸들러
export class MethodOverrideHandler {
  private overrideHeaders = ['X-HTTP-Method-Override', 'X-Method-Override'];
  
  detectOverride(request: Request): HTTPMethod | null {
    // 헤더 기반 오버라이드
    for (const header of this.overrideHeaders) {
      const overrideMethod = request.headers[header.toLowerCase()];
      if (overrideMethod) {
        return overrideMethod.toUpperCase() as HTTPMethod;
      }
    }
    
    // 쿼리 파라미터 기반 오버라이드
    if (request.query._method) {
      return request.query._method.toUpperCase() as HTTPMethod;
    }
    
    // POST 본문 기반 오버라이드
    if (request.method === 'POST' && request.body?._method) {
      return request.body._method.toUpperCase() as HTTPMethod;
    }
    
    return null;
  }
  
  applyOverride(request: Request): Request {
    const override = this.detectOverride(request);
    
    if (override && this.isValidOverride(request.method, override)) {
      request.originalMethod = request.method;
      request.method = override;
      
      // 오버라이드 정보 기록
      request.metadata.methodOverridden = true;
      request.metadata.originalMethod = request.originalMethod;
    }
    
    return request;
  }
  
  private isValidOverride(original: string, override: string): boolean {
    // POST 메서드만 오버라이드 허용
    if (original !== 'POST') {
      return false;
    }
    
    // 안전하지 않은 메서드로만 오버라이드 허용
    const allowedOverrides = ['PUT', 'PATCH', 'DELETE'];
    return allowedOverrides.includes(override);
  }
}
```

**검증 기준**:
- [ ] 표준 HTTP 메서드 매핑
- [ ] 커스텀 액션 처리
- [ ] 메서드 사용 검증
- [ ] 메서드 오버라이드 지원

#### SubTask 6.6.4: 리소스 관계 및 중첩 구조

**담당자**: API 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api/rest/resource_relationships.py
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

class RelationshipType(Enum):
    """관계 유형"""
    ONE_TO_ONE = "one-to-one"
    ONE_TO_MANY = "one-to-many"
    MANY_TO_ONE = "many-to-one"
    MANY_TO_MANY = "many-to-many"

@dataclass
class ResourceRelationship:
    """리소스 관계 정의"""
    name: str
    source_resource: str
    target_resource: str
    type: RelationshipType
    inverse_name: Optional[str] = None
    nested: bool = False
    embedded: bool = False
    cascade_delete: bool = False
    required: bool = False

class ResourceRelationshipManager:
    """리소스 관계 관리"""
    
    def __init__(self):
        self.relationships: Dict[str, List[ResourceRelationship]] = {}
        self.initialize_relationships()
    
    def initialize_relationships(self):
        """T-Developer 리소스 관계 초기화"""
        
        # Project 관계
        self.add_relationship(ResourceRelationship(
            name="owner",
            source_resource="project",
            target_resource="user",
            type=RelationshipType.MANY_TO_ONE,
            inverse_name="projects",
            required=True
        ))
        
        self.add_relationship(ResourceRelationship(
            name="components",
            source_resource="project",
            target_resource="component",
            type=RelationshipType.ONE_TO_MANY,
            inverse_name="project",
            nested=True,
            cascade_delete=True
        ))
        
        self.add_relationship(ResourceRelationship(
            name="executions",
            source_resource="project",
            target_resource="agent_execution",
            type=RelationshipType.ONE_TO_MANY,
            inverse_name="project",
            nested=True,
            cascade_delete=False
        ))
        
        # Component 관계
        self.add_relationship(ResourceRelationship(
            name="parent",
            source_resource="component",
            target_resource="component",
            type=RelationshipType.MANY_TO_ONE,
            inverse_name="children",
            nested=False
        ))
        
        self.add_relationship(ResourceRelationship(
            name="dependencies",
            source_resource="component",
            target_resource="component",
            type=RelationshipType.MANY_TO_MANY,
            inverse_name="dependents",
            embedded=False
        ))
        
        # Agent Execution 관계
        self.add_relationship(ResourceRelationship(
            name="triggered_by",
            source_resource="agent_execution",
            target_resource="user",
            type=RelationshipType.MANY_TO_ONE,
            inverse_name="triggered_executions",
            required=True
        ))
        
        self.add_relationship(ResourceRelationship(
            name="depends_on",
            source_resource="agent_execution",
            target_resource="agent_execution",
            type=RelationshipType.MANY_TO_MANY,
            inverse_name="dependent_executions"
        ))
    
    def generate_nested_routes(self, relationship: ResourceRelationship) -> List[Route]:
        """중첩 라우트 생성"""
        
        routes = []
        
        if not relationship.nested:
            return routes
        
        source_plural = self.pluralize(relationship.source_resource)
        target_plural = self.pluralize(relationship.target_resource)
        
        if relationship.type in [RelationshipType.ONE_TO_MANY, RelationshipType.MANY_TO_MANY]:
            # 컬렉션 라우트
            routes.extend([
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}",
                    method="GET",
                    handler=f"list_{relationship.name}",
                    description=f"List {relationship.name} of {relationship.source_resource}"
                ),
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}",
                    method="POST",
                    handler=f"add_{relationship.name}",
                    description=f"Add {relationship.name} to {relationship.source_resource}"
                )
            ])
            
            # 개별 리소스 라우트
            routes.extend([
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}/{{target_id}}",
                    method="GET",
                    handler=f"get_{relationship.name}_item",
                    description=f"Get specific {relationship.target_resource}"
                ),
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}/{{target_id}}",
                    method="PUT",
                    handler=f"update_{relationship.name}_item",
                    description=f"Update {relationship.target_resource}"
                ),
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}/{{target_id}}",
                    method="DELETE",
                    handler=f"remove_{relationship.name}_item",
                    description=f"Remove {relationship.target_resource}"
                )
            ])
        
        elif relationship.type == RelationshipType.ONE_TO_ONE:
            routes.extend([
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}",
                    method="GET",
                    handler=f"get_{relationship.name}",
                    description=f"Get {relationship.name} of {relationship.source_resource}"
                ),
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}",
                    method="PUT",
                    handler=f"set_{relationship.name}",
                    description=f"Set {relationship.name} for {relationship.source_resource}"
                ),
                Route(
                    path=f"/{source_plural}/{{source_id}}/{relationship.name}",
                    method="DELETE",
                    handler=f"remove_{relationship.name}",
                    description=f"Remove {relationship.name} from {relationship.source_resource}"
                )
            ])
        
        return routes
    
    def build_relationship_links(
        self,
        resource_type: str,
        resource_id: str
    ) -> Dict[str, str]:
        """관계 링크 생성"""
        
        links = {}
        relationships = self.relationships.get(resource_type, [])
        
        for rel in relationships:
            if rel.nested:
                # 중첩 관계 링크
                links[rel.name] = f"/api/{self.pluralize(resource_type)}/{resource_id}/{rel.name}"
            else:
                # 관계 링크
                links[f"related_{rel.name}"] = f"/api/{self.pluralize(resource_type)}/{resource_id}/relationships/{rel.name}"
        
        return links

class NestedResourceHandler:
    """중첩 리소스 처리"""
    
    def __init__(self, relationship_manager: ResourceRelationshipManager):
        self.relationship_manager = relationship_manager
        self.max_nesting_depth = 3
    
    async def handle_nested_request(
        self,
        request: Request,
        path_segments: List[str]
    ) -> Response:
        """중첩 요청 처리"""
        
        # 경로 분석
        resource_chain = self.parse_resource_chain(path_segments)
        
        # 깊이 검증
        if len(resource_chain) > self.max_nesting_depth:
            raise NestingDepthExceededError(
                f"Maximum nesting depth ({self.max_nesting_depth}) exceeded"
            )
        
        # 관계 검증
        for i in range(len(resource_chain) - 1):
            parent = resource_chain[i]
            child = resource_chain[i + 1]
            
            if not self.validate_relationship(parent.resource_type, child.resource_type):
                raise InvalidRelationshipError(
                    f"No relationship between {parent.resource_type} and {child.resource_type}"
                )
        
        # 권한 검증
        await self.validate_access_chain(resource_chain, request.user)
        
        # 요청 처리
        return await self.process_nested_request(request, resource_chain)
    
    def parse_resource_chain(self, segments: List[str]) -> List[ResourceNode]:
        """리소스 체인 파싱"""
        
        chain = []
        i = 0
        
        while i < len(segments):
            # 리소스 타입
            resource_type = self.singularize(segments[i])
            i += 1
            
            # 리소스 ID (있는 경우)
            resource_id = None
            if i < len(segments) and not self.is_resource_name(segments[i]):
                resource_id = segments[i]
                i += 1
            
            chain.append(ResourceNode(
                resource_type=resource_type,
                resource_id=resource_id
            ))
        
        return chain
    
    async def expand_relationships(
        self,
        resource: Dict,
        expand: List[str],
        depth: int = 1
    ) -> Dict:
        """관계 확장"""
        
        if depth > self.max_nesting_depth:
            return resource
        
        expanded = resource.copy()
        
        for rel_name in expand:
            if '.' in rel_name:
                # 중첩 확장
                parts = rel_name.split('.', 1)
                primary = parts[0]
                nested = parts[1]
                
                # 1차 관계 확장
                if primary not in expanded:
                    expanded[primary] = await self.load_relationship(
                        resource['type'],
                        resource['id'],
                        primary
                    )
                
                # 중첩 관계 확장
                if isinstance(expanded[primary], list):
                    for item in expanded[primary]:
                        await self.expand_relationships(item, [nested], depth + 1)
                else:
                    await self.expand_relationships(expanded[primary], [nested], depth + 1)
            else:
                # 단순 확장
                expanded[rel_name] = await self.load_relationship(
                    resource['type'],
                    resource['id'],
                    rel_name
                )
        
        return expanded
```

**검증 기준**:
- [ ] 관계 유형 정의
- [ ] 중첩 라우트 생성
- [ ] 관계 링크 구성
- [ ] 관계 확장 처리

---

### Task 6.7: CRUD 작업 구현

#### SubTask 6.7.1: Create 작업 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api/rest/crud/create.ts
export interface CreateOperation<T> {
  validate(data: Partial<T>): Promise<ValidationResult>;
  preProcess(data: Partial<T>): Promise<T>;
  execute(data: T): Promise<T>;
  postProcess(created: T): Promise<T>;
  generateResponse(resource: T): Response;
}

export class CreateOperationHandler<T> implements CreateOperation<T> {
  constructor(
    private resourceType: string,
    private repository: Repository<T>,
    private validator: Validator<T>,
    private eventEmitter: EventEmitter
  ) {}
  
  async handle(request: Request): Promise<Response> {
    try {
      // 1. 요청 데이터 추출
      const requestData = this.extractData(request);
      
      // 2. 유효성 검증
      const validation = await this.validate(requestData);
      if (!validation.valid) {
        return this.errorResponse(400, validation.errors);
      }
      
      // 3. 전처리
      const processedData = await this.preProcess(requestData);
      
      // 4. 중복 체크
      await this.checkDuplicates(processedData);
      
      // 5. 생성 실행
      const created = await this.execute(processedData);
      
      // 6. 후처리
      const finalResource = await this.postProcess(created);
      
      // 7. 이벤트 발생
      await this.emitCreatedEvent(finalResource);
      
      // 8. 응답 생성
      return this.generateResponse(finalResource);
      
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  async validate(data: Partial<T>): Promise<ValidationResult> {
    // 스키마 검증
    const schemaValidation = await this.validator.validateSchema(data);
    if (!schemaValidation.valid) {
      return schemaValidation;
    }
    
    // 필수 필드 검증
    const requiredFields = this.getRequiredFields();
    const missingFields = requiredFields.filter(field => !(field in data));
    
    if (missingFields.length > 0) {
      return {
        valid: false,
        errors: missingFields.map(field => ({
          field,
          message: `${field} is required`
        }))
      };
    }
    
    // 비즈니스 규칙 검증
    return await this.validator.validateBusinessRules(data);
  }
  
  async preProcess(data: Partial<T>): Promise<T> {
    const processed = { ...data } as T;
    
    // ID 생성
    if (!processed['id']) {
      processed['id'] = generateUUID();
    }
    
    // 타임스탬프 추가
    const now = new Date();
    processed['createdAt'] = now;
    processed['updatedAt'] = now;
    
    // 기본값 설정
    const defaults = this.getDefaultValues();
    for (const [key, value] of Object.entries(defaults)) {
      if (!(key in processed)) {
        processed[key] = value;
      }
    }
    
    // 데이터 정규화
    return this.normalizeData(processed);
  }
  
  async execute(data: T): Promise<T> {
    // 트랜잭션 시작
    const transaction = await this.repository.beginTransaction();
    
    try {
      // 리소스 생성
      const created = await this.repository.create(data, { transaction });
      
      // 관련 리소스 생성
      await this.createRelatedResources(created, transaction);
      
      // 트랜잭션 커밋
      await transaction.commit();
      
      return created;
      
    } catch (error) {
      // 트랜잭션 롤백
      await transaction.rollback();
      throw error;
    }
  }
  
  async postProcess(created: T): Promise<T> {
    // 관계 로드
    const withRelations = await this.loadRelationships(created);
    
    // 계산 필드 추가
    const withComputedFields = this.addComputedFields(withRelations);
    
    // 캐시 업데이트
    await this.updateCache(withComputedFields);
    
    // 검색 인덱스 업데이트
    await this.updateSearchIndex(withComputedFields);
    
    return withComputedFields;
  }
  
  generateResponse(resource: T): Response {
    return {
      status: 201,
      headers: {
        'Location': `/api/${this.resourceType}s/${resource['id']}`,
        'Content-Type': 'application/json'
      },
      body: {
        data: this.transformToResource(resource),
        links: {
          self: `/api/${this.resourceType}s/${resource['id']}`
        }
      }
    };
  }
  
  private async checkDuplicates(data: T): Promise<void> {
    const uniqueFields = this.getUniqueFields();
    
    for (const field of uniqueFields) {
      if (data[field]) {
        const existing = await this.repository.findOne({
          [field]: data[field]
        });
        
        if (existing) {
          throw new DuplicateResourceError(
            `${this.resourceType} with ${field}='${data[field]}' already exists`
          );
        }
      }
    }
  }
}

// 일괄 생성 핸들러
export class BulkCreateHandler<T> {
  constructor(
    private createHandler: CreateOperationHandler<T>,
    private batchSize: number = 100
  ) {}
  
  async handleBulk(request: Request): Promise<Response> {
    const items = request.body.data;
    
    if (!Array.isArray(items)) {
      return this.errorResponse(400, 'Request body must contain an array');
    }
    
    const results = {
      created: [],
      failed: []
    };
    
    // 배치 처리
    for (let i = 0; i < items.length; i += this.batchSize) {
      const batch = items.slice(i, i + this.batchSize);
      const batchResults = await this.processBatch(batch);
      
      results.created.push(...batchResults.created);
      results.failed.push(...batchResults.failed);
    }
    
    return {
      status: 207, // Multi-Status
      body: {
        data: results.created,
        errors: results.failed,
        meta: {
          total: items.length,
          created: results.created.length,
          failed: results.failed.length
        }
      }
    };
  }
  
  private async processBatch(items: Partial<T>[]): Promise<BatchResult> {
    const results = {
      created: [],
      failed: []
    };
    
    // 병렬 처리
    const promises = items.map(async (item, index) => {
      try {
        const created = await this.createHandler.handle({
          body: item
        } as Request);
        
        return { success: true, data: created, index };
      } catch (error) {
        return { 
          success: false, 
          error: error.message,
          index,
          item 
        };
      }
    });
    
    const batchResults = await Promise.all(promises);
    
    for (const result of batchResults) {
      if (result.success) {
        results.created.push(result.data);
      } else {
        results.failed.push({
          index: result.index,
          item: result.item,
          error: result.error
        });
      }
    }
    
    return results;
  }
}
```

**검증 기준**:
- [ ] 완전한 생성 플로우
- [ ] 유효성 검증
- [ ] 트랜잭션 처리
- [ ] 일괄 생성 지원

---

### Task 6.7: CRUD 작업 구현 (계속)

#### SubTask 6.7.2: Read 작업 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/rest/crud/read.py
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class ReadOptions:
    """읽기 옵션"""
    fields: Optional[List[str]] = None  # 선택 필드
    expand: Optional[List[str]] = None  # 확장 관계
    include: Optional[List[str]] = None  # 포함 리소스
    exclude: Optional[List[str]] = None  # 제외 필드

class ReadOperationHandler:
    """Read 작업 핸들러"""
    
    def __init__(self, resource_type: str, repository: Repository):
        self.resource_type = resource_type
        self.repository = repository
        self.cache_manager = CacheManager()
        self.field_selector = FieldSelector()
    
    async def get_single(self, resource_id: str, options: ReadOptions) -> Response:
        """단일 리소스 조회"""
        
        try:
            # 1. 캐시 확인
            cache_key = self.build_cache_key(resource_id, options)
            cached = await self.cache_manager.get(cache_key)
            
            if cached:
                return self.create_response(cached, from_cache=True)
            
            # 2. 데이터베이스 조회
            resource = await self.repository.find_by_id(resource_id)
            
            if not resource:
                raise ResourceNotFoundError(
                    f"{self.resource_type} with id '{resource_id}' not found"
                )
            
            # 3. 권한 확인
            await self.check_read_permission(resource)
            
            # 4. 필드 선택
            if options.fields:
                resource = self.field_selector.select(resource, options.fields)
            
            # 5. 관계 확장
            if options.expand:
                resource = await self.expand_relationships(resource, options.expand)
            
            # 6. 포함 리소스 로드
            if options.include:
                resource = await self.include_resources(resource, options.include)
            
            # 7. 제외 필드 처리
            if options.exclude:
                resource = self.field_selector.exclude(resource, options.exclude)
            
            # 8. 캐시 저장
            await self.cache_manager.set(cache_key, resource, ttl=300)
            
            # 9. 응답 생성
            return self.create_response(resource)
            
        except Exception as e:
            return self.handle_error(e)
    
    async def get_collection(
        self,
        filters: Optional[Dict] = None,
        options: ReadOptions = None
    ) -> Response:
        """컬렉션 조회"""
        
        try:
            # 1. 쿼리 구성
            query = self.build_query(filters)
            
            # 2. 총 개수 조회 (페이지네이션용)
            total_count = await self.repository.count(query)
            
            # 3. 리소스 조회
            resources = await self.repository.find_many(query)
            
            # 4. 권한 필터링
            resources = await self.filter_by_permission(resources)
            
            # 5. 필드 처리
            if options:
                resources = [
                    await self.process_resource(r, options) 
                    for r in resources
                ]
            
            # 6. 응답 생성
            return self.create_collection_response(resources, total_count)
            
        except Exception as e:
            return self.handle_error(e)
    
    async def expand_relationships(
        self,
        resource: Dict,
        relationships: List[str]
    ) -> Dict:
        """관계 확장"""
        
        expanded = resource.copy()
        
        for rel_path in relationships:
            # 중첩 관계 처리 (예: author.profile)
            if '.' in rel_path:
                parts = rel_path.split('.')
                current = expanded
                
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = await self.load_relationship(
                            current['id'],
                            part
                        )
                    current = current[part]
                
                # 마지막 관계 로드
                final_part = parts[-1]
                if current:
                    current[final_part] = await self.load_relationship(
                        current['id'],
                        final_part
                    )
            else:
                # 단순 관계
                expanded[rel_path] = await self.load_relationship(
                    resource['id'],
                    rel_path
                )
        
        return expanded
    
    async def include_resources(
        self,
        resource: Dict,
        includes: List[str]
    ) -> Dict:
        """관련 리소스 포함"""
        
        included = []
        
        for include_path in includes:
            related = await self.load_related_resources(resource, include_path)
            included.extend(related)
        
        # JSON:API 스타일 응답
        return {
            'data': resource,
            'included': included
        }
    
    def create_response(
        self,
        resource: Dict,
        from_cache: bool = False
    ) -> Response:
        """응답 생성"""
        
        headers = {
            'Content-Type': 'application/json',
            'ETag': self.generate_etag(resource)
        }
        
        if from_cache:
            headers['X-Cache'] = 'HIT'
        else:
            headers['X-Cache'] = 'MISS'
        
        return Response(
            status=200,
            headers=headers,
            body={
                'data': self.transform_resource(resource),
                'links': self.generate_links(resource),
                'meta': self.generate_meta(resource)
            }
        )

class StreamingReadHandler:
    """스트리밍 읽기 핸들러"""
    
    def __init__(self, repository: Repository):
        self.repository = repository
        self.chunk_size = 100
    
    async def stream_collection(
        self,
        filters: Dict,
        options: ReadOptions
    ) -> AsyncIterator:
        """대용량 컬렉션 스트리밍"""
        
        # 커서 기반 조회
        cursor = None
        
        while True:
            # 청크 조회
            chunk = await self.repository.find_many(
                filters,
                cursor=cursor,
                limit=self.chunk_size
            )
            
            if not chunk:
                break
            
            # 각 리소스 처리 및 전송
            for resource in chunk:
                processed = await self.process_resource(resource, options)
                yield self.format_stream_item(processed)
            
            # 다음 커서 설정
            cursor = chunk[-1]['id']
    
    def format_stream_item(self, resource: Dict) -> bytes:
        """스트림 아이템 포맷"""
        
        # NDJSON (Newline Delimited JSON) 형식
        return json.dumps(resource).encode('utf-8') + b'\n'

class ConditionalReadHandler:
    """조건부 읽기 핸들러"""
    
    async def handle_conditional_get(
        self,
        resource_id: str,
        if_none_match: Optional[str] = None,
        if_modified_since: Optional[datetime] = None
    ) -> Response:
        """조건부 GET 처리"""
        
        # 리소스 메타데이터 조회
        metadata = await self.get_resource_metadata(resource_id)
        
        # ETag 검증
        if if_none_match:
            current_etag = metadata['etag']
            if if_none_match == current_etag:
                return Response(
                    status=304,  # Not Modified
                    headers={'ETag': current_etag}
                )
        
        # 수정 시간 검증
        if if_modified_since:
            last_modified = metadata['updated_at']
            if last_modified <= if_modified_since:
                return Response(
                    status=304,  # Not Modified
                    headers={'Last-Modified': last_modified.isoformat()}
                )
        
        # 변경된 경우 전체 리소스 반환
        resource = await self.get_resource(resource_id)
        
        return Response(
            status=200,
            headers={
                'ETag': metadata['etag'],
                'Last-Modified': metadata['updated_at'].isoformat()
            },
            body={'data': resource}
        )
```

**검증 기준**:
- [ ] 단일/컬렉션 조회
- [ ] 필드 선택 및 확장
- [ ] 캐싱 전략
- [ ] 조건부 읽기 지원

#### SubTask 6.7.3: Update 작업 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api/rest/crud/update.ts
export interface UpdateOperation<T> {
  validateUpdate(id: string, data: Partial<T>): Promise<ValidationResult>;
  checkConcurrency(id: string, version: string): Promise<void>;
  applyUpdate(existing: T, updates: Partial<T>): T;
  executeUpdate(id: string, data: T): Promise<T>;
}

export class UpdateOperationHandler<T> implements UpdateOperation<T> {
  constructor(
    private resourceType: string,
    private repository: Repository<T>,
    private validator: Validator<T>,
    private auditLogger: AuditLogger
  ) {}
  
  async handlePut(request: Request): Promise<Response> {
    /**
     * PUT - 전체 교체
     */
    const resourceId = request.params.id;
    const replacementData = request.body;
    
    try {
      // 1. 기존 리소스 조회
      const existing = await this.repository.findById(resourceId);
      if (!existing) {
        // PUT은 멱등성을 위해 없으면 생성할 수도 있음
        if (this.config.allowPutCreate) {
          return await this.createWithPut(resourceId, replacementData);
        }
        throw new ResourceNotFoundError(`${this.resourceType} not found`);
      }
      
      // 2. 권한 확인
      await this.checkUpdatePermission(existing);
      
      // 3. 전체 교체 데이터 검증
      const validation = await this.validator.validateComplete(replacementData);
      if (!validation.valid) {
        return this.errorResponse(400, validation.errors);
      }
      
      // 4. 불변 필드 보존
      const preserved = this.preserveImmutableFields(existing, replacementData);
      
      // 5. 업데이트 실행
      const updated = await this.executeReplace(resourceId, preserved);
      
      // 6. 감사 로그
      await this.auditLogger.logUpdate(
        this.resourceType,
        resourceId,
        existing,
        updated,
        request.user
      );
      
      // 7. 응답
      return this.createUpdateResponse(updated);
      
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  async handlePatch(request: Request): Promise<Response> {
    /**
     * PATCH - 부분 업데이트
     */
    const resourceId = request.params.id;
    const patchData = request.body;
    
    try {
      // 1. 기존 리소스 조회
      const existing = await this.repository.findById(resourceId);
      if (!existing) {
        throw new ResourceNotFoundError(`${this.resourceType} not found`);
      }
      
      // 2. 낙관적 잠금 확인
      if (request.headers['if-match']) {
        await this.checkConcurrency(resourceId, request.headers['if-match']);
      }
      
      // 3. 권한 확인
      await this.checkUpdatePermission(existing);
      
      // 4. 패치 작업 파싱
      const operations = this.parsePatchOperations(patchData);
      
      // 5. 각 작업 검증 및 적용
      let updated = { ...existing };
      for (const operation of operations) {
        updated = await this.applyPatchOperation(updated, operation);
      }
      
      // 6. 최종 검증
      const validation = await this.validator.validate(updated);
      if (!validation.valid) {
        return this.errorResponse(400, validation.errors);
      }
      
      // 7. 업데이트 실행
      const saved = await this.executeUpdate(resourceId, updated);
      
      // 8. 변경 이벤트 발생
      await this.emitUpdateEvent(existing, saved);
      
      // 9. 응답
      return this.createUpdateResponse(saved);
      
    } catch (error) {
      return this.handleError(error);
    }
  }
  
  private parsePatchOperations(patchData: any): PatchOperation[] {
    // JSON Patch (RFC 6902) 지원
    if (Array.isArray(patchData)) {
      return patchData.map(op => ({
        op: op.op,
        path: op.path,
        value: op.value,
        from: op.from
      }));
    }
    
    // JSON Merge Patch (RFC 7396) 지원
    return this.convertMergePatchToOperations(patchData);
  }
  
  private async applyPatchOperation(
    resource: T,
    operation: PatchOperation
  ): Promise<T> {
    switch (operation.op) {
      case 'add':
        return this.applyAdd(resource, operation.path, operation.value);
        
      case 'remove':
        return this.applyRemove(resource, operation.path);
        
      case 'replace':
        return this.applyReplace(resource, operation.path, operation.value);
        
      case 'move':
        return this.applyMove(resource, operation.from, operation.path);
        
      case 'copy':
        return this.applyCopy(resource, operation.from, operation.path);
        
      case 'test':
        const testResult = this.applyTest(resource, operation.path, operation.value);
        if (!testResult) {
          throw new PatchTestFailedError(`Test operation failed at ${operation.path}`);
        }
        return resource;
        
      default:
        throw new InvalidPatchOperationError(`Unknown operation: ${operation.op}`);
    }
  }
  
  private preserveImmutableFields(existing: T, replacement: T): T {
    const immutableFields = ['id', 'createdAt', 'createdBy'];
    const result = { ...replacement };
    
    for (const field of immutableFields) {
      if (field in existing) {
        result[field] = existing[field];
      }
    }
    
    // 업데이트 타임스탬프
    result['updatedAt'] = new Date();
    
    return result;
  }
  
  async checkConcurrency(id: string, version: string): Promise<void> {
    const current = await this.repository.getVersion(id);
    
    if (current !== version) {
      throw new ConcurrencyError(
        'Resource has been modified',
        {
          currentVersion: current,
          providedVersion: version
        }
      );
    }
  }
}

// 일괄 업데이트 핸들러
export class BulkUpdateHandler<T> {
  constructor(
    private updateHandler: UpdateOperationHandler<T>,
    private batchSize: number = 50
  ) {}
  
  async handleBulkUpdate(request: Request): Promise<Response> {
    const updates = request.body.updates;
    
    if (!Array.isArray(updates)) {
      return this.errorResponse(400, 'Updates must be an array');
    }
    
    const results = {
      updated: [],
      failed: []
    };
    
    // 트랜잭션으로 처리
    const transaction = await this.repository.beginTransaction();
    
    try {
      for (const update of updates) {
        try {
          const updated = await this.updateHandler.handlePatch({
            params: { id: update.id },
            body: update.data,
            headers: request.headers
          } as Request);
          
          results.updated.push(updated);
        } catch (error) {
          results.failed.push({
            id: update.id,
            error: error.message
          });
        }
      }
      
      // 모두 성공한 경우만 커밋
      if (results.failed.length === 0) {
        await transaction.commit();
      } else {
        await transaction.rollback();
        return this.errorResponse(400, {
          message: 'Bulk update failed',
          failed: results.failed
        });
      }
      
      return {
        status: 200,
        body: {
          data: results.updated,
          meta: {
            total: updates.length,
            updated: results.updated.length
          }
        }
      };
      
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }
}

// 조건부 업데이트
export class ConditionalUpdateHandler<T> {
  async handleConditionalUpdate(
    id: string,
    updates: Partial<T>,
    conditions: UpdateConditions
  ): Promise<Response> {
    // 조건 검증
    const existing = await this.repository.findById(id);
    
    // If-Match 헤더 검증
    if (conditions.ifMatch && existing.etag !== conditions.ifMatch) {
      return {
        status: 412, // Precondition Failed
        headers: {
          'ETag': existing.etag
        },
        body: {
          error: 'ETag mismatch'
        }
      };
    }
    
    // If-Unmodified-Since 검증
    if (conditions.ifUnmodifiedSince) {
      if (existing.updatedAt > conditions.ifUnmodifiedSince) {
        return {
          status: 412, // Precondition Failed
          headers: {
            'Last-Modified': existing.updatedAt.toISOString()
          },
          body: {
            error: 'Resource has been modified'
          }
        };
      }
    }
    
    // 업데이트 실행
    const updated = await this.executeUpdate(id, updates);
    
    return {
      status: 200,
      headers: {
        'ETag': updated.etag,
        'Last-Modified': updated.updatedAt.toISOString()
      },
      body: {
        data: updated
      }
    };
  }
}
```

**검증 기준**:
- [ ] PUT/PATCH 메서드 구분
- [ ] JSON Patch 지원
- [ ] 낙관적 잠금
- [ ] 일괄 업데이트

#### SubTask 6.7.4: Delete 작업 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/rest/crud/delete.py
class DeleteOperationHandler:
    """Delete 작업 핸들러"""
    
    def __init__(self, resource_type: str, repository: Repository):
        self.resource_type = resource_type
        self.repository = repository
        self.cascade_manager = CascadeDeleteManager()
        self.archive_manager = ArchiveManager()
    
    async def handle_delete(self, resource_id: str, options: DeleteOptions) -> Response:
        """리소스 삭제"""
        
        try:
            # 1. 리소스 존재 확인
            resource = await self.repository.find_by_id(resource_id)
            if not resource:
                # 멱등성을 위해 404 대신 204 반환 가능
                if options.idempotent:
                    return Response(status=204)
                raise ResourceNotFoundError(f"{self.resource_type} not found")
            
            # 2. 권한 확인
            await self.check_delete_permission(resource)
            
            # 3. 삭제 가능 여부 확인
            await self.validate_deletion(resource)
            
            # 4. 소프트 삭제 vs 하드 삭제
            if options.soft_delete:
                result = await self.soft_delete(resource)
            else:
                result = await self.hard_delete(resource, options)
            
            # 5. 삭제 이벤트 발생
            await self.emit_delete_event(resource, options)
            
            # 6. 응답 생성
            return self.create_delete_response(result, options)
            
        except Exception as e:
            return self.handle_error(e)
    
    async def soft_delete(self, resource: Dict) -> Dict:
        """소프트 삭제"""
        
        # 삭제 마킹
        resource['deleted'] = True
        resource['deleted_at'] = datetime.now()
        resource['deleted_by'] = get_current_user()
        
        # 업데이트
        updated = await self.repository.update(resource['id'], resource)
        
        # 관련 리소스 처리
        await self.handle_soft_delete_relations(resource)
        
        return updated
    
    async def hard_delete(self, resource: Dict, options: DeleteOptions) -> None:
        """하드 삭제"""
        
        # 트랜잭션 시작
        transaction = await self.repository.begin_transaction()
        
        try:
            # 1. 아카이브 (선택적)
            if options.archive:
                await self.archive_manager.archive(resource)
            
            # 2. 종속 리소스 처리
            if options.cascade:
                await self.cascade_manager.delete_dependencies(
                    self.resource_type,
                    resource['id'],
                    transaction
                )
            else:
                # 종속성 확인
                dependencies = await self.check_dependencies(resource['id'])
                if dependencies:
                    raise DependencyConstraintError(
                        f"Cannot delete: {len(dependencies)} dependent resources exist"
                    )
            
            # 3. 리소스 삭제
            await self.repository.delete(resource['id'], transaction)
            
            # 4. 캐시 무효화
            await self.invalidate_cache(resource['id'])
            
            # 5. 검색 인덱스 제거
            await self.remove_from_search_index(resource['id'])
            
            # 커밋
            await transaction.commit()
            
        except Exception as e:
            await transaction.rollback()
            raise e
    
    async def validate_deletion(self, resource: Dict) -> None:
        """삭제 가능 여부 검증"""
        
        # 보호된 리소스 확인
        if resource.get('protected'):
            raise ProtectedResourceError(
                f"This {self.resource_type} is protected and cannot be deleted"
            )
        
        # 상태 확인
        if resource.get('status') in ['processing', 'active']:
            raise InvalidStateError(
                f"Cannot delete {self.resource_type} in {resource['status']} state"
            )
        
        # 비즈니스 규칙 검증
        await self.validate_business_rules(resource)
    
    async def check_dependencies(self, resource_id: str) -> List[Dependency]:
        """종속성 확인"""
        
        dependencies = []
        
        # 정의된 관계 확인
        relationships = self.get_resource_relationships()
        
        for rel in relationships:
            if rel.cascade_delete:
                continue
                
            count = await self.repository.count_related(
                resource_id,
                rel.name
            )
            
            if count > 0:
                dependencies.append(Dependency(
                    type=rel.target_resource,
                    count=count,
                    relationship=rel.name
                ))
        
        return dependencies
    
    def create_delete_response(
        self,
        result: Optional[Dict],
        options: DeleteOptions
    ) -> Response:
        """삭제 응답 생성"""
        
        if options.soft_delete and options.return_deleted:
            # 소프트 삭제 시 삭제된 리소스 반환
            return Response(
                status=200,
                body={'data': result}
            )
        
        # 일반적으로 204 No Content
        return Response(
            status=204,
            headers={'Content-Length': '0'}
        )

class BulkDeleteHandler:
    """일괄 삭제 핸들러"""
    
    def __init__(self, delete_handler: DeleteOperationHandler):
        self.delete_handler = delete_handler
        self.batch_size = 100
    
    async def handle_bulk_delete(
        self,
        resource_ids: List[str],
        options: DeleteOptions
    ) -> Response:
        """일괄 삭제"""
        
        results = {
            'deleted': [],
            'failed': [],
            'skipped': []
        }
        
        # 삭제 순서 결정 (종속성 고려)
        ordered_ids = await self.order_by_dependencies(resource_ids)
        
        # 배치 처리
        for batch in self.batch_iterator(ordered_ids, self.batch_size):
            batch_results = await self.process_batch(batch, options)
            
            results['deleted'].extend(batch_results['deleted'])
            results['failed'].extend(batch_results['failed'])
            results['skipped'].extend(batch_results['skipped'])
        
        return Response(
            status=207,  # Multi-Status
            body={
                'meta': {
                    'total': len(resource_ids),
                    'deleted': len(results['deleted']),
                    'failed': len(results['failed']),
                    'skipped': len(results['skipped'])
                },
                'data': results
            }
        )
    
    async def order_by_dependencies(
        self,
        resource_ids: List[str]
    ) -> List[str]:
        """종속성에 따른 삭제 순서 결정"""
        
        # 종속성 그래프 구성
        graph = DependencyGraph()
        
        for resource_id in resource_ids:
            dependencies = await self.get_dependencies(resource_id)
            graph.add_node(resource_id, dependencies)
        
        # 위상 정렬
        return graph.topological_sort()

class RecycleBinManager:
    """휴지통 관리"""
    
    def __init__(self):
        self.retention_period = timedelta(days=30)
    
    async def move_to_recycle_bin(self, resource: Dict) -> None:
        """휴지통으로 이동"""
        
        recycled = {
            'original_id': resource['id'],
            'resource_type': resource['type'],
            'resource_data': resource,
            'deleted_at': datetime.now(),
            'deleted_by': get_current_user(),
            'expires_at': datetime.now() + self.retention_period
        }
        
        await self.recycle_repository.create(recycled)
    
    async def restore_from_recycle_bin(
        self,
        recycle_id: str
    ) -> Dict:
        """휴지통에서 복원"""
        
        recycled = await self.recycle_repository.find_by_id(recycle_id)
        
        if not recycled:
            raise ResourceNotFoundError("Recycled item not found")
        
        if datetime.now() > recycled['expires_at']:
            raise ExpiredResourceError("Recycled item has expired")
        
        # 원본 복원
        restored = recycled['resource_data']
        restored['restored_at'] = datetime.now()
        restored['restored_by'] = get_current_user()
        
        # 원본 위치로 복원
        await self.repository.create(restored)
        
        # 휴지통에서 제거
        await self.recycle_repository.delete(recycle_id)
        
        return restored
    
    async def empty_recycle_bin(self) -> None:
        """휴지통 비우기 (만료된 항목)"""
        
        expired = await self.recycle_repository.find_expired()
        
        for item in expired:
            await self.recycle_repository.delete(item['id'])
```

**검증 기준**:
- [ ] 소프트/하드 삭제
- [ ] 종속성 처리
- [ ] 일괄 삭제
- [ ] 휴지통 기능

---

### Task 6.8: 페이지네이션 및 필터링

#### SubTask 6.8.1: 페이지네이션 전략 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/api/rest/pagination/pagination-strategies.ts
export interface PaginationStrategy {
  paginate(query: Query, params: PaginationParams): Promise<PaginatedResult>;
  generateLinks(result: PaginatedResult, baseUrl: string): PaginationLinks;
  generateMetadata(result: PaginatedResult): PaginationMetadata;
}

// 오프셋 기반 페이지네이션
export class OffsetPagination implements PaginationStrategy {
  constructor(
    private defaultLimit: number = 20,
    private maxLimit: number = 100
  ) {}
  
  async paginate(query: Query, params: PaginationParams): Promise<PaginatedResult> {
    // 파라미터 추출
    const page = Math.max(1, params.page || 1);
    const limit = Math.min(this.maxLimit, params.limit || this.defaultLimit);
    const offset = (page - 1) * limit;
    
    // 총 개수 조회
    const totalCount = await query.count();
    
    // 데이터 조회
    const items = await query
      .offset(offset)
      .limit(limit)
      .execute();
    
    // 페이지 정보 계산
    const totalPages = Math.ceil(totalCount / limit);
    const hasNext = page < totalPages;
    const hasPrev = page > 1;
    
    return {
      items,
      pagination: {
        page,
        limit,
        offset,
        totalCount,
        totalPages,
        hasNext,
        hasPrev
      }
    };
  }
  
  generateLinks(result: PaginatedResult, baseUrl: string): PaginationLinks {
    const { page, limit, totalPages, hasNext, hasPrev } = result.pagination;
    const links: PaginationLinks = {
      self: `${baseUrl}?page=${page}&limit=${limit}`
    };
    
    if (hasNext) {
      links.next = `${baseUrl}?page=${page + 1}&limit=${limit}`;
      links.last = `${baseUrl}?page=${totalPages}&limit=${limit}`;
    }
    
    if (hasPrev) {
      links.prev = `${baseUrl}?page=${page - 1}&limit=${limit}`;
      links.first = `${baseUrl}?page=1&limit=${limit}`;
    }
    
    return links;
  }
  
  generateMetadata(result: PaginatedResult): PaginationMetadata {
    return {
      pagination: {
        ...result.pagination,
        type: 'offset',
        pageSize: result.pagination.limit,
        currentPage: result.pagination.page
      }
    };
  }
}

// 커서 기반 페이지네이션
export class CursorPagination implements PaginationStrategy {
  constructor(
    private cursorField: string = 'id',
    private defaultLimit: number = 20
  ) {}
  
  async paginate(query: Query, params: PaginationParams): Promise<PaginatedResult> {
    const limit = params.limit || this.defaultLimit;
    const cursor = params.cursor;
    const direction = params.direction || 'next';
    
    // 커서 기반 쿼리
    let paginatedQuery = query.limit(limit + 1); // +1 for hasMore check
    
    if (cursor) {
      if (direction === 'next') {
        paginatedQuery = paginatedQuery.where(
          this.cursorField,
          '>',
          this.decodeCursor(cursor)
        );
      } else {
        paginatedQuery = paginatedQuery.where(
          this.cursorField,
          '<',
          this.decodeCursor(cursor)
        ).orderBy(this.cursorField, 'desc');
      }
    }
    
    // 데이터 조회
    const items = await paginatedQuery.execute();
    
    // 다음 페이지 존재 여부
    const hasMore = items.length > limit;
    if (hasMore) {
      items.pop(); // Remove extra item
    }
    
    // 커서 생성
    const startCursor = items.length > 0 
      ? this.encodeCursor(items[0][this.cursorField])
      : null;
    
    const endCursor = items.length > 0
      ? this.encodeCursor(items[items.length - 1][this.cursorField])
      : null;
    
    return {
      items,
      pagination: {
        limit,
        hasNextPage: hasMore && direction === 'next',
        hasPrevPage: hasMore && direction === 'prev',
        startCursor,
        endCursor
      }
    };
  }
  
  private encodeCursor(value: any): string {
    return Buffer.from(JSON.stringify({
      field: this.cursorField,
      value
    })).toString('base64');
  }
  
  private decodeCursor(cursor: string): any {
    const decoded = Buffer.from(cursor, 'base64').toString();
    return JSON.parse(decoded).value;
  }
  
  generateLinks(result: PaginatedResult, baseUrl: string): PaginationLinks {
    const links: PaginationLinks = {
      self: baseUrl
    };
    
    if (result.pagination.hasNextPage) {
      links.next = `${baseUrl}?cursor=${result.pagination.endCursor}&limit=${result.pagination.limit}`;
    }
    
    if (result.pagination.hasPrevPage) {
      links.prev = `${baseUrl}?cursor=${result.pagination.startCursor}&direction=prev&limit=${result.pagination.limit}`;
    }
    
    return links;
  }
}

// 키셋 페이지네이션 (성능 최적화)
export class KeysetPagination implements PaginationStrategy {
  constructor(
    private sortFields: string[] = ['id'],
    private defaultLimit: number = 20
  ) {}
  
  async paginate(query: Query, params: PaginationParams): Promise<PaginatedResult> {
    const limit = params.limit || this.defaultLimit;
    const keyset = params.keyset ? this.parseKeyset(params.keyset) : null;
    
    // 키셋 기반 쿼리 구성
    let paginatedQuery = query.limit(limit + 1);
    
    if (keyset) {
      // 복합 키 비교
      const conditions = this.buildKeysetConditions(keyset);
      paginatedQuery = paginatedQuery.whereRaw(conditions);
    }
    
    // 정렬 적용
    for (const field of this.sortFields) {
      paginatedQuery = paginatedQuery.orderBy(field);
    }
    
    // 실행
    const items = await paginatedQuery.execute();
    
    const hasMore = items.length > limit;
    if (hasMore) {
      items.pop();
    }
    
    // 다음 키셋 생성
    const nextKeyset = hasMore && items.length > 0
      ? this.createKeyset(items[items.length - 1])
      : null;
    
    return {
      items,
      pagination: {
        limit,
        hasMore,
        nextKeyset
      }
    };
  }
  
  private buildKeysetConditions(keyset: any): string {
    // 복합 키 비교 조건 생성
    // (a, b, c) > (x, y, z) 형태
    const fields = this.sortFields;
    const values = fields.map(f => keyset[f]);
    
    return `(${fields.join(',')}) > (${values.map(() => '?').join(',')})`;
  }
  
  private createKeyset(item: any): string {
    const keyset = {};
    for (const field of this.sortFields) {
      keyset[field] = item[field];
    }
    return Buffer.from(JSON.stringify(keyset)).toString('base64');
  }
  
  private parseKeyset(keyset: string): any {
    return JSON.parse(Buffer.from(keyset, 'base64').toString());
  }
}

// 무한 스크롤 지원
export class InfiniteScrollPagination {
  private cursorPagination: CursorPagination;
  
  constructor() {
    this.cursorPagination = new CursorPagination();
  }
  
  async loadMore(
    query: Query,
    lastCursor: string | null,
    limit: number = 20
  ): Promise<InfiniteScrollResult> {
    const result = await this.cursorPagination.paginate(query, {
      cursor: lastCursor,
      limit
    });
    
    return {
      items: result.items,
      nextCursor: result.pagination.endCursor,
      hasMore: result.pagination.hasNextPage,
      meta: {
        loadedCount: result.items.length,
        timestamp: new Date()
      }
    };
  }
}
```

**검증 기준**:
- [ ] 다양한 페이지네이션 전략
- [ ] 커서 기반 구현
- [ ] 링크 생성
- [ ] 무한 스크롤 지원

#### SubTask 6.8.2: 필터링 시스템 구축

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api/rest/filtering/filter_system.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class FilterOperator(Enum):
    """필터 연산자"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "nin"
    CONTAINS = "contains"
    STARTS_WITH = "starts"
    ENDS_WITH = "ends"
    REGEX = "regex"
    EXISTS = "exists"
    BETWEEN = "between"

@dataclass
class FilterDefinition:
    """필터 정의"""
    field: str
    operator: FilterOperator
    value: Any
    case_sensitive: bool = True
    data_type: Optional[str] = None

class FilterParser:
    """필터 파서"""
    
    def parse_filters(self, query_params: Dict) -> List[FilterDefinition]:
        """쿼리 파라미터에서 필터 파싱"""
        
        filters = []
        
        # 단순 필터 (field=value)
        for key, value in query_params.items():
            if not self.is_filter_param(key):
                continue
            
            # 연산자 포함 필터 (field[operator]=value)
            if '[' in key and ']' in key:
                field, operator = self.parse_filter_key(key)
                filters.append(FilterDefinition(
                    field=field,
                    operator=FilterOperator(operator),
                    value=self.parse_filter_value(value)
                ))
            else:
                # 기본 equals 연산자
                filters.append(FilterDefinition(
                    field=key,
                    operator=FilterOperator.EQUALS,
                    value=value
                ))
        
        # 복합 필터 파싱 (filter 파라미터)
        if 'filter' in query_params:
            complex_filters = self.parse_complex_filter(query_params['filter'])
            filters.extend(complex_filters)
        
        return filters
    
    def parse_complex_filter(self, filter_string: str) -> List[FilterDefinition]:
        """복합 필터 문자열 파싱"""
        # 예: "status:active,created_at:>2024-01-01,tags:in:python,java"
        
        filters = []
        filter_parts = filter_string.split(',')
        
        for part in filter_parts:
            if ':' not in part:
                continue
            
            components = part.split(':')
            
            if len(components) == 2:
                # field:value
                field, value = components
                filters.append(FilterDefinition(
                    field=field,
                    operator=FilterOperator.EQUALS,
                    value=value
                ))
            elif len(components) == 3:
                # field:operator:value
                field, operator, value = components
                filters.append(FilterDefinition(
                    field=field,
                    operator=self.parse_operator(operator),
                    value=self.parse_value(value)
                ))
        
        return filters
    
    def parse_operator(self, op_string: str) -> FilterOperator:
        """연산자 문자열 파싱"""
        
        operator_map = {
            '=': FilterOperator.EQUALS,
            '!=': FilterOperator.NOT_EQUALS,
            '>': FilterOperator.GREATER_THAN,
            '>=': FilterOperator.GREATER_THAN_OR_EQUAL,
            '<': FilterOperator.LESS_THAN,
            '<=': FilterOperator.LESS_THAN_OR_EQUAL,
            'in': FilterOperator.IN,
            'nin': FilterOperator.NOT_IN,
            'contains': FilterOperator.CONTAINS,
            'starts': FilterOperator.STARTS_WITH,
            'ends': FilterOperator.ENDS_WITH,
            'regex': FilterOperator.REGEX,
            'exists': FilterOperator.EXISTS,
            'between': FilterOperator.BETWEEN
        }
        
        return operator_map.get(op_string, FilterOperator.EQUALS)

class FilterBuilder:
    """필터 쿼리 빌더"""
    
    def __init__(self, allowed_fields: List[str]):
        self.allowed_fields = allowed_fields
        self.validators = FilterValidators()
    
    def build_query(
        self,
        base_query: Query,
        filters: List[FilterDefinition]
    ) -> Query:
        """필터를 쿼리에 적용"""
        
        query = base_query
        
        for filter_def in filters:
            # 필드 검증
            if filter_def.field not in self.allowed_fields:
                raise InvalidFilterFieldError(
                    f"Field '{filter_def.field}' is not filterable"
                )
            
            # 값 검증
            if not self.validators.validate(filter_def):
                raise InvalidFilterValueError(
                    f"Invalid value for filter {filter_def.field}"
                )
            
            # 쿼리 적용
            query = self.apply_filter(query, filter_def)
        
        return query
    
    def apply_filter(self, query: Query, filter_def: FilterDefinition) -> Query:
        """단일 필터 적용"""
        
        field = filter_def.field
        operator = filter_def.operator
        value = filter_def.value
        
        if operator == FilterOperator.EQUALS:
            return query.where(field, '=', value)
            
        elif operator == FilterOperator.NOT_EQUALS:
            return query.where(field, '!=', value)
            
        elif operator == FilterOperator.GREATER_THAN:
            return query.where(field, '>', value)
            
        elif operator == FilterOperator.GREATER_THAN_OR_EQUAL:
            return query.where(field, '>=', value)
            
        elif operator == FilterOperator.LESS_THAN:
            return query.where(field, '<', value)
            
        elif operator == FilterOperator.LESS_THAN_OR_EQUAL:
            return query.where(field, '<=', value)
            
        elif operator == FilterOperator.IN:
            values = value if isinstance(value, list) else [value]
            return query.where_in(field, values)
            
        elif operator == FilterOperator.NOT_IN:
            values = value if isinstance(value, list) else [value]
            return query.where_not_in(field, values)
            
        elif operator == FilterOperator.CONTAINS:
            return query.where(field, 'LIKE', f'%{value}%')
            
        elif operator == FilterOperator.STARTS_WITH:
            return query.where(field, 'LIKE', f'{value}%')
            
        elif operator == FilterOperator.ENDS_WITH:
            return query.where(field, 'LIKE', f'%{value}')
            
        elif operator == FilterOperator.REGEX:
            return query.where_raw(f"{field} REGEXP ?", [value])
            
        elif operator == FilterOperator.EXISTS:
            if value:
                return query.where_not_null(field)
            else:
                return query.where_null(field)
                
        elif operator == FilterOperator.BETWEEN:
            if isinstance(value, list) and len(value) == 2:
                return query.where_between(field, value[0], value[1])
            
        return query

class AdvancedFilterSystem:
    """고급 필터링 시스템"""
    
    def __init__(self):
        self.parser = FilterParser()
        self.builder = FilterBuilder(self.get_allowed_fields())
        self.cache = FilterCache()
    
    async def apply_filters(
        self,
        request: Request,
        base_query: Query
    ) -> FilteredQuery:
        """요청에서 필터 추출 및 적용"""
        
        # 캐시 키 생성
        cache_key = self.generate_cache_key(request.query)
        
        # 캐시 확인
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # 필터 파싱
        filters = self.parser.parse_filters(request.query)
        
        # 중첩 필터 처리
        if 'nested' in request.query:
            nested_filters = self.parse_nested_filters(request.query['nested'])
            filters.extend(nested_filters)
        
        # 논리 연산자 처리
        logical_op = request.query.get('op', 'AND')
        
        # 쿼리 구성
        if logical_op == 'OR':
            query = self.build_or_query(base_query, filters)
        else:
            query = self.build_and_query(base_query, filters)
        
        # 결과 캐싱
        result = FilteredQuery(query=query, filters=filters)
        await self.cache.set(cache_key, result)
        
        return result
    
    def build_or_query(
        self,
        base_query: Query,
        filters: List[FilterDefinition]
    ) -> Query:
        """OR 조건 쿼리 구성"""
        
        query = base_query
        or_conditions = []
        
        for filter_def in filters:
            condition = self.filter_to_condition(filter_def)
            or_conditions.append(condition)
        
        if or_conditions:
            query = query.where(lambda q: 
                q.where_any(or_conditions)
            )
        
        return query

class FacetedSearch:
    """패싯 검색"""
    
    async def generate_facets(
        self,
        base_query: Query,
        facet_fields: List[str]
    ) -> Dict[str, List[FacetValue]]:
        """패싯 생성"""
        
        facets = {}
        
        for field in facet_fields:
            # 필드별 고유 값과 개수 조회
            facet_query = base_query.group_by(field).select(
                field,
                'COUNT(*) as count'
            )
            
            results = await facet_query.execute()
            
            facets[field] = [
                FacetValue(
                    value=row[field],
                    count=row['count'],
                    label=self.format_label(field, row[field])
                )
                for row in results
            ]
        
        return facets
```

**검증 기준**:
- [ ] 다양한 필터 연산자
- [ ] 복합 필터 지원
- [ ] 논리 연산자 (AND/OR)
- [ ] 패싯 검색

#### SubTask 6.8.3: 정렬 및 검색 기능

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/rest/search/search-sort.ts
export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
  nullsFirst?: boolean;
  caseInsensitive?: boolean;
}

export class SortingHandler {
  private allowedSortFields: Set<string>;
  private defaultSort: SortOptions;
  
  constructor(config: SortConfig) {
    this.allowedSortFields = new Set(config.allowedFields);
    this.defaultSort = config.defaultSort || { field: 'id', direction: 'asc' };
  }
  
  parseSortParams(params: any): SortOptions[] {
    const sortOptions: SortOptions[] = [];
    
    // 단일 정렬 파라미터
    if (params.sort) {
      const parsed = this.parseSortString(params.sort);
      sortOptions.push(...parsed);
    }
    
    // 다중 정렬 파라미터
    if (params.sort_by && params.order) {
      sortOptions.push({
        field: params.sort_by,
        direction: params.order.toLowerCase() as 'asc' | 'desc'
      });
    }
    
    // 기본 정렬
    if (sortOptions.length === 0) {
      sortOptions.push(this.defaultSort);
    }
    
    return this.validateSortOptions(sortOptions);
  }
  
  private parseSortString(sortString: string): SortOptions[] {
    // 형식: "field1:asc,field2:desc" 또는 "-field1,+field2"
    const sortOptions: SortOptions[] = [];
    const parts = sortString.split(',');
    
    for (const part of parts) {
      const trimmed = part.trim();
      
      if (trimmed.startsWith('-')) {
        sortOptions.push({
          field: trimmed.substring(1),
          direction: 'desc'
        });
      } else if (trimmed.startsWith('+')) {
        sortOptions.push({
          field: trimmed.substring(1),
          direction: 'asc'
        });
      } else if (trimmed.includes(':')) {
        const [field, direction] = trimmed.split(':');
        sortOptions.push({
          field,
          direction: direction.toLowerCase() as 'asc' | 'desc'
        });
      } else {
        sortOptions.push({
          field: trimmed,
          direction: 'asc'
        });
      }
    }
    
    return sortOptions;
  }
  
  private validateSortOptions(options: SortOptions[]): SortOptions[] {
    return options.filter(option => {
      if (!this.allowedSortFields.has(option.field)) {
        console.warn(`Sort field '${option.field}' is not allowed`);
        return false;
      }
      return true;
    });
  }
  
  applySort(query: Query, sortOptions: SortOptions[]): Query {
    let sortedQuery = query;
    
    for (const option of sortOptions) {
      sortedQuery = this.applySingleSort(sortedQuery, option);
    }
    
    return sortedQuery;
  }
  
  private applySingleSort(query: Query, option: SortOptions): Query {
    const direction = option.direction.toUpperCase();
    
    if (option.caseInsensitive) {
      // 대소문자 구분 없는 정렬
      return query.orderByRaw(`LOWER(${option.field}) ${direction}`);
    }
    
    if (option.nullsFirst !== undefined) {
      // NULL 값 처리
      const nullsOrder = option.nullsFirst ? 'NULLS FIRST' : 'NULLS LAST';
      return query.orderByRaw(`${option.field} ${direction} ${nullsOrder}`);
    }
    
    return query.orderBy(option.field, direction);
  }
}

// 전문 검색
export class FullTextSearchHandler {
  private searchableFields: string[];
  private searchEngine: SearchEngine;
  
  constructor(config: SearchConfig) {
    this.searchableFields = config.searchableFields;
    this.searchEngine = this.initSearchEngine(config.engine);
  }
  
  async search(
    query: string,
    options: SearchOptions = {}
  ): Promise<SearchResult> {
    // 검색어 전처리
    const processedQuery = this.preprocessQuery(query);
    
    // 검색 실행
    const results = await this.searchEngine.search({
      query: processedQuery,
      fields: options.fields || this.searchableFields,
      fuzzy: options.fuzzy !== false,
      boost: options.boost || {},
      filters: options.filters || []
    });
    
    // 하이라이팅
    if (options.highlight) {
      results.items = this.addHighlighting(results.items, processedQuery);
    }
    
    // 관련도 점수 계산
    if (options.includeScore) {
      results.items = this.calculateRelevanceScores(results.items, processedQuery);
    }
    
    return results;
  }
  
  private preprocessQuery(query: string): ProcessedQuery {
    // 특수 문자 이스케이프
    let processed = this.escapeSpecialChars(query);
    
    // 불용어 제거
    processed = this.removeStopWords(processed);
    
    // 동의어 확장
    processed = this.expandSynonyms(processed);
    
    // 검색 연산자 파싱
    const operators = this.parseOperators(processed);
    
    return {
      original: query,
      processed,
      tokens: this.tokenize(processed),
      operators
    };
  }
  
  private addHighlighting(items: any[], query: ProcessedQuery): any[] {
    return items.map(item => {
      const highlighted = { ...item };
      
      for (const field of this.searchableFields) {
        if (item[field] && typeof item[field] === 'string') {
          highlighted[`${field}_highlighted`] = this.highlightText(
            item[field],
            query.tokens
          );
        }
      }
      
      return highlighted;
    });
  }
  
  private highlightText(text: string, tokens: string[]): string {
    let highlighted = text;
    
    for (const token of tokens) {
      const regex = new RegExp(`(${token})`, 'gi');
      highlighted = highlighted.replace(regex, '<mark>$1</mark>');
    }
    
    return highlighted;
  }
}

// 복합 검색 및 정렬
export class AdvancedSearchSort {
  private sortHandler: SortingHandler;
  private searchHandler: FullTextSearchHandler;
  private filterBuilder: FilterBuilder;
  
  async executeAdvancedQuery(
    request: Request
  ): Promise<QueryResult> {
    const { q, filters, sort, page, limit } = request.query;
    
    // 기본 쿼리
    let query = this.repository.createQuery();
    
    // 1. 전문 검색 적용
    if (q) {
      const searchResults = await this.searchHandler.search(q);
      const ids = searchResults.items.map(item => item.id);
      query = query.whereIn('id', ids);
    }
    
    // 2. 필터 적용
    if (filters) {
      query = this.filterBuilder.build(query, filters);
    }
    
    // 3. 정렬 적용
    const sortOptions = this.sortHandler.parseSortParams({ sort });
    query = this.sortHandler.applySort(query, sortOptions);
    
    // 4. 페이지네이션 적용
    const paginated = await this.paginationHandler.paginate(query, {
      page,
      limit
    });
    
    // 5. 부가 정보 추가
    return {
      ...paginated,
      query: q,
      appliedFilters: filters,
      appliedSort: sortOptions
    };
  }
}
```

**검증 기준**:
- [ ] 다중 정렬 지원
- [ ] 전문 검색 기능
- [ ] 검색어 하이라이팅
- [ ] 복합 쿼리 처리

#### SubTask 6.8.4: 커서 기반 페이지네이션

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/rest/pagination/cursor_pagination.py
from typing import Optional, List, Dict, Any, Tuple
import base64
import json
from datetime import datetime

class CursorPaginationHandler:
    """커서 기반 페이지네이션 핸들러"""
    
    def __init__(
        self,
        order_fields: List[str],
        default_limit: int = 20,
        max_limit: int = 100
    ):
        self.order_fields = order_fields
        self.default_limit = default_limit
        self.max_limit = max_limit
    
    def encode_cursor(self, record: Dict[str, Any]) -> str:
        """커서 인코딩"""
        
        cursor_data = {
            'values': {},
            'direction': 'forward',
            'timestamp': datetime.now().isoformat()
        }
        
        # 정렬 필드 값 추출
        for field in self.order_fields:
            value = record.get(field)
            
            # 타입별 직렬화
            if isinstance(value, datetime):
                cursor_data['values'][field] = value.isoformat()
            elif value is not None:
                cursor_data['values'][field] = value
        
        # Base64 인코딩
        json_str = json.dumps(cursor_data, separators=(',', ':'))
        return base64.urlsafe_b64encode(json_str.encode()).decode()
    
    def decode_cursor(self, cursor: str) -> Dict[str, Any]:
        """커서 디코딩"""
        
        try:
            json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
            cursor_data = json.loads(json_str)
            
            # 타입 복원
            for field, value in cursor_data['values'].items():
                if field in self.date_fields:
                    cursor_data['values'][field] = datetime.fromisoformat(value)
            
            return cursor_data
            
        except Exception as e:
            raise InvalidCursorError(f"Invalid cursor: {e}")
    
    async def paginate_forward(
        self,
        query: Query,
        after_cursor: Optional[str] = None,
        first: int = None
    ) -> CursorPage:
        """순방향 페이지네이션"""
        
        limit = min(first or self.default_limit, self.max_limit)
        
        # 커서 조건 적용
        if after_cursor:
            cursor_data = self.decode_cursor(after_cursor)
            query = self.apply_cursor_condition(query, cursor_data, 'after')
        
        # 정렬 적용
        for field in self.order_fields:
            query = query.order_by(field, 'ASC')
        
        # +1 개 조회 (hasNext 확인용)
        items = await query.limit(limit + 1).execute()
        
        has_next = len(items) > limit
        if has_next:
            items = items[:-1]  # 마지막 아이템 제거
        
        # 엣지 생성
        edges = [
            {
                'node': item,
                'cursor': self.encode_cursor(item)
            }
            for item in items
        ]
        
        # 페이지 정보
        page_info = {
            'hasNextPage': has_next,
            'hasPreviousPage': after_cursor is not None,
            'startCursor': edges[0]['cursor'] if edges else None,
            'endCursor': edges[-1]['cursor'] if edges else None
        }
        
        return CursorPage(
            edges=edges,
            pageInfo=page_info,
            totalCount=await self.get_total_count(query)
        )
    
    async def paginate_backward(
        self,
        query: Query,
        before_cursor: Optional[str] = None,
        last: int = None
    ) -> CursorPage:
        """역방향 페이지네이션"""
        
        limit = min(last or self.default_limit, self.max_limit)
        
        # 커서 조건 적용
        if before_cursor:
            cursor_data = self.decode_cursor(before_cursor)
            query = self.apply_cursor_condition(query, cursor_data, 'before')
        
        # 역방향 정렬
        for field in self.order_fields:
            query = query.order_by(field, 'DESC')
        
        # +1 개 조회
        items = await query.limit(limit + 1).execute()
        
        has_prev = len(items) > limit
        if has_prev:
            items = items[:-1]
        
        # 순서 복원
        items.reverse()
        
        # 엣지 생성
        edges = [
            {
                'node': item,
                'cursor': self.encode_cursor(item)
            }
            for item in items
        ]
        
        # 페이지 정보
        page_info = {
            'hasNextPage': before_cursor is not None,
            'hasPreviousPage': has_prev,
            'startCursor': edges[0]['cursor'] if edges else None,
            'endCursor': edges[-1]['cursor'] if edges else None
        }
        
        return CursorPage(
            edges=edges,
            pageInfo=page_info,
            totalCount=await self.get_total_count(query)
        )
    
    def apply_cursor_condition(
        self,
        query: Query,
        cursor_data: Dict,
        direction: str
    ) -> Query:
        """커서 조건 적용"""
        
        values = cursor_data['values']
        
        # 복합 키 비교 조건 생성
        conditions = []
        
        for i, field in enumerate(self.order_fields):
            if field not in values:
                break
            
            # 이전 필드들은 같아야 함
            for j in range(i):
                prev_field = self.order_fields[j]
                conditions.append(f"{prev_field} = {values[prev_field]}")
            
            # 현재 필드는 커서 방향에 따라
            operator = '>' if direction == 'after' else '<'
            conditions.append(f"{field} {operator} {values[field]}")
        
        # OR 조건으로 결합
        where_clause = ' OR '.join(
            f"({' AND '.join(cond_group)})"
            for cond_group in conditions
        )
        
        return query.where_raw(where_clause)

class RelayStylePagination:
    """GraphQL Relay 스타일 페이지네이션"""
    
    def __init__(self, cursor_handler: CursorPaginationHandler):
        self.cursor_handler = cursor_handler
    
    async def paginate(
        self,
        query: Query,
        args: RelayPaginationArgs
    ) -> Connection:
        """Relay 스타일 페이지네이션"""
        
        # 인자 검증
        self.validate_args(args)
        
        # 순방향/역방향 결정
        if args.first is not None:
            page = await self.cursor_handler.paginate_forward(
                query,
                args.after,
                args.first
            )
        else:
            page = await self.cursor_handler.paginate_backward(
                query,
                args.before,
                args.last
            )
        
        return Connection(
            edges=page.edges,
            pageInfo=page.pageInfo,
            totalCount=page.totalCount
        )
    
    def validate_args(self, args: RelayPaginationArgs):
        """페이지네이션 인자 검증"""
        
        # first와 last 동시 사용 불가
        if args.first is not None and args.last is not None:
            raise ValueError("Cannot use both 'first' and 'last'")
        
        # after와 before 동시 사용 불가
        if args.after is not None and args.before is not None:
            raise ValueError("Cannot use both 'after' and 'before'")
        
        # 음수 불가
        if args.first is not None and args.first < 0:
            raise ValueError("'first' must be non-negative")
        
        if args.last is not None and args.last < 0:
            raise ValueError("'last' must be non-negative")
```

**검증 기준**:
- [ ] 커서 인코딩/디코딩
- [ ] 양방향 페이지네이션
- [ ] Relay 스타일 지원
- [ ] 복합 키 커서

---

### Task 6.9: 응답 포맷 표준화

#### SubTask 6.9.1: 응답 구조 표준 정의

**담당자**: API 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/rest/response/response-standards.ts
export interface StandardResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ErrorDetail;
  meta?: ResponseMetadata;
  links?: ResponseLinks;
  included?: any[];
}

export interface ResponseMetadata {
  timestamp: string;
  version: string;
  requestId: string;
  processingTime?: number;
  pagination?: PaginationMeta;
  rateLimit?: RateLimitMeta;
}

export class ResponseFormatter {
  private config: ResponseConfig;
  
  constructor(config: ResponseConfig) {
    this.config = config;
  }
  
  formatSuccess<T>(
    data: T,
    options: ResponseOptions = {}
  ): StandardResponse<T> {
    const response: StandardResponse<T> = {
      success: true,
      data
    };
    
    // 메타데이터 추가
    if (this.config.includeMetadata) {
      response.meta = this.generateMetadata(options);
    }
    
    // 링크 추가
    if (options.links) {
      response.links = options.links;
    }
    
    // 포함 리소스
    if (options.included) {
      response.included = options.included;
    }
    
    return response;
  }
  
  formatError(
    error: Error | ErrorDetail,
    options: ResponseOptions = {}
  ): StandardResponse {
    const errorDetail = this.normalizeError(error);
    
    const response: StandardResponse = {
      success: false,
      error: errorDetail
    };
    
    if (this.config.includeMetadata) {
      response.meta = this.generateMetadata(options);
    }
    
    return response;
  }
  
  formatCollection<T>(
    items: T[],
    pagination: PaginationMeta,
    options: ResponseOptions = {}
  ): StandardResponse<T[]> {
    const response = this.formatSuccess(items, options);
    
    if (!response.meta) {
      response.meta = {} as ResponseMetadata;
    }
    
    response.meta.pagination = pagination;
    
    return response;
  }
  
  private generateMetadata(options: ResponseOptions): ResponseMetadata {
    return {
      timestamp: new Date().toISOString(),
      version: this.config.apiVersion,
      requestId: options.requestId || generateRequestId(),
      processingTime: options.processingTime,
      rateLimit: options.rateLimit
    };
  }
  
  private normalizeError(error: Error | ErrorDetail): ErrorDetail {
    if (this.isErrorDetail(error)) {
      return error;
    }
    
    return {
      code: error.code || 'INTERNAL_ERROR',
      message: error.message,
      details: this.config.includeErrorDetails ? error.stack : undefined
    };
  }
}

// JSON:API 형식
export class JSONAPIFormatter {
  format(resource: any, type: string): JSONAPIResponse {
    return {
      data: this.formatResource(resource, type),
      jsonapi: {
        version: '1.0'
      }
    };
  }
  
  private formatResource(resource: any, type: string): JSONAPIResource {
    const { id, ...attributes } = resource;
    
    return {
      type,
      id: String(id),
      attributes,
      relationships: this.extractRelationships(resource),
      links: {
        self: `/api/${type}s/${id}`
      }
    };
  }
  
  formatCollection(
    resources: any[],
    type: string,
    pagination?: PaginationMeta
  ): JSONAPIResponse {
    const response: JSONAPIResponse = {
      data: resources.map(r => this.formatResource(r, type)),
      jsonapi: {
        version: '1.0'
      }
    };
    
    if (pagination) {
      response.meta = { pagination };
      response.links = this.generatePaginationLinks(pagination);
    }
    
    return response;
  }
}

// HAL 형식
export class HALFormatter {
  format(resource: any, type: string): HALResponse {
    return {
      ...resource,
      _links: this.generateLinks(resource, type),
      _embedded: this.extractEmbedded(resource)
    };
  }
  
  private generateLinks(resource: any, type: string): HALLinks {
    return {
      self: {
        href: `/api/${type}s/${resource.id}`
      },
      collection: {
        href: `/api/${type}s`
      }
    };
  }
}
```

**검증 기준**:
- [ ] 표준 응답 구조
- [ ] JSON:API 지원
- [ ] HAL 지원
- [ ] 메타데이터 포함

#### SubTask 6.9.2: HATEOAS 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api/rest/response/hateoas.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Link:
    """HATEOAS 링크"""
    rel: str  # 관계 타입
    href: str  # URL
    method: str = "GET"
    title: Optional[str] = None
    type: Optional[str] = None  # 미디어 타입
    templated: bool = False
    deprecation: Optional[str] = None

class HATEOASBuilder:
    """HATEOAS 링크 빌더"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.link_registry = LinkRegistry()
    
    def build_resource_links(
        self,
        resource_type: str,
        resource_id: str,
        context: Optional[Dict] = None
    ) -> List[Link]:
        """리소스 링크 생성"""
        
        links = []
        
        # Self 링크
        links.append(Link(
            rel="self",
            href=f"{self.base_url}/{resource_type}s/{resource_id}",
            method="GET",
            title=f"Get {resource_type}"
        ))
        
        # Collection 링크
        links.append(Link(
            rel="collection",
            href=f"{self.base_url}/{resource_type}s",
            method="GET",
            title=f"List {resource_type}s"
        ))
        
        # CRUD 작업 링크
        links.extend(self.build_crud_links(resource_type, resource_id))
        
        # 관계 링크
        links.extend(self.build_relationship_links(resource_type, resource_id))
        
        # 커스텀 액션 링크
        links.extend(self.build_action_links(resource_type, resource_id, context))
        
        return links
    
    def build_crud_links(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[Link]:
        """CRUD 작업 링크"""
        
        base_path = f"{self.base_url}/{resource_type}s/{resource_id}"
        
        return [
            Link(
                rel="update",
                href=base_path,
                method="PUT",
                title=f"Update {resource_type}"
            ),
            Link(
                rel="partial-update",
                href=base_path,
                method="PATCH",
                title=f"Partially update {resource_type}"
            ),
            Link(
                rel="delete",
                href=base_path,
                method="DELETE",
                title=f"Delete {resource_type}"
            )
        ]
    
    def build_relationship_links(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[Link]:
        """관계 링크 생성"""
        
        links = []
        relationships = self.link_registry.get_relationships(resource_type)
        
        for rel in relationships:
            # 관계 리소스 링크
            links.append(Link(
                rel=rel.name,
                href=f"{self.base_url}/{resource_type}s/{resource_id}/{rel.name}",
                method="GET",
                title=f"Get {rel.name} of {resource_type}"
            ))
            
            # 관계 관리 링크
            if rel.mutable:
                links.append(Link(
                    rel=f"add-{rel.name}",
                    href=f"{self.base_url}/{resource_type}s/{resource_id}/relationships/{rel.name}",
                    method="POST",
                    title=f"Add {rel.name} to {resource_type}"
                ))
                
                links.append(Link(
                    rel=f"remove-{rel.name}",
                    href=f"{self.base_url}/{resource_type}s/{resource_id}/relationships/{rel.name}",
                    method="DELETE",
                    title=f"Remove {rel.name} from {resource_type}"
                ))
        
        return links
    
    def build_action_links(
        self,
        resource_type: str,
        resource_id: str,
        context: Optional[Dict] = None
    ) -> List[Link]:
        """커스텀 액션 링크"""
        
        links = []
        actions = self.link_registry.get_actions(resource_type)
        
        for action in actions:
            # 액션 가능 여부 확인
            if context and not self.is_action_allowed(action, context):
                continue
            
            link = Link(
                rel=action.name,
                href=f"{self.base_url}/{resource_type}s/{resource_id}/{action.name}",
                method=action.method,
                title=action.description
            )
            
            # 템플릿 URL
            if action.parameters:
                link.href += "{?" + ",".join(action.parameters) + "}"
                link.templated = True
            
            links.append(link)
        
        return links

class HATEOASResponse:
    """HATEOAS 응답 래퍼"""
    
    def __init__(self, data: Any, links: List[Link]):
        self.data = data
        self.links = links
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        
        return {
            **self.data,
            "_links": self.format_links()
        }
    
    def format_links(self) -> Dict[str, Any]:
        """링크 포맷팅"""
        
        formatted = {}
        
        for link in self.links:
            link_data = {
                "href": link.href,
                "method": link.method
            }
            
            if link.title:
                link_data["title"] = link.title
            
            if link.type:
                link_data["type"] = link.type
            
            if link.templated:
                link_data["templated"] = True
            
            if link.deprecation:
                link_data["deprecation"] = link.deprecation
            
            # 같은 rel이 여러 개인 경우 배열로
            if link.rel in formatted:
                if not isinstance(formatted[link.rel], list):
                    formatted[link.rel] = [formatted[link.rel]]
                formatted[link.rel].append(link_data)
            else:
                formatted[link.rel] = link_data
        
        return formatted

class SmartLinkGenerator:
    """컨텍스트 기반 스마트 링크 생성"""
    
    def generate_contextual_links(
        self,
        resource: Dict,
        user_context: UserContext
    ) -> List[Link]:
        """컨텍스트 기반 링크 생성"""
        
        links = []
        
        # 권한 기반 링크
        if user_context.has_permission('edit', resource):
            links.append(self.create_edit_link(resource))
        
        if user_context.has_permission('delete', resource):
            links.append(self.create_delete_link(resource))
        
        # 상태 기반 링크
        state = resource.get('status')
        
        if state == 'draft':
            links.append(Link(
                rel="publish",
                href=f"/api/projects/{resource['id']}/publish",
                method="POST",
                title="Publish project"
            ))
        elif state == 'published':
            links.append(Link(
                rel="unpublish",
                href=f"/api/projects/{resource['id']}/unpublish",
                method="POST",
                title="Unpublish project"
            ))
        
        # 워크플로우 링크
        next_actions = self.get_workflow_actions(resource, user_context)
        for action in next_actions:
            links.append(Link(
                rel=f"workflow:{action.name}",
                href=f"/api/projects/{resource['id']}/workflow/{action.name}",
                method="POST",
                title=action.description
            ))
        
        return links
```

**검증 기준**:
- [ ] HATEOAS 링크 생성
- [ ] 관계 링크 포함
- [ ] 액션 링크 동적 생성
- [ ] 컨텍스트 기반 링크

#### SubTask 6.9.3: 콘텐츠 협상 처리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/rest/response/content-negotiation.ts
export class ContentNegotiator {
  private formatters: Map<string, ResponseFormatter>;
  private defaultFormat: string = 'application/json';
  
  constructor() {
    this.initializeFormatters();
  }
  
  private initializeFormatters(): void {
    this.formatters = new Map([
      ['application/json', new JSONFormatter()],
      ['application/xml', new XMLFormatter()],
      ['application/hal+json', new HALFormatter()],
      ['application/vnd.api+json', new JSONAPIFormatter()],
      ['text/html', new HTMLFormatter()],
      ['text/csv', new CSVFormatter()],
      ['application/yaml', new YAMLFormatter()],
      ['application/msgpack', new MessagePackFormatter()]
    ]);
  }
  
  negotiate(request: Request): ContentType {
    // Accept 헤더 파싱
    const acceptHeader = request.headers['accept'];
    
    if (!acceptHeader) {
      return this.defaultFormat;
    }
    
    // 미디어 타입 파싱 및 우선순위 정렬
    const acceptedTypes = this.parseAcceptHeader(acceptHeader);
    
    // 지원하는 형식 찾기
    for (const type of acceptedTypes) {
      const formatter = this.findFormatter(type);
      if (formatter) {
        return type.mediaType;
      }
    }
    
    // 기본 형식 반환
    return this.defaultFormat;
  }
  
  private parseAcceptHeader(header: string): AcceptType[] {
    const types = header.split(',').map(part => {
      const [mediaType, ...params] = part.trim().split(';');
      
      let quality = 1.0;
      const qParam = params.find(p => p.trim().startsWith('q='));
      
      if (qParam) {
        quality = parseFloat(qParam.split('=')[1]);
      }
      
      return {
        mediaType: mediaType.trim(),
        quality,
        params
      };
    });
    
    // Quality 값으로 정렬
    return types.sort((a, b) => b.quality - a.quality);
  }
  
  async format(
    data: any,
    contentType: string,
    options: FormatOptions = {}
  ): Promise<FormattedResponse> {
    const formatter = this.formatters.get(contentType);
    
    if (!formatter) {
      throw new UnsupportedMediaTypeError(
        `Content type ${contentType} is not supported`
      );
    }
    
    const formatted = await formatter.format(data, options);
    
    return {
      contentType,
      body: formatted,
      headers: {
        'Content-Type': contentType
      }
    };
  }
}

// 언어 협상
export class LanguageNegotiator {
  private supportedLanguages: Set<string>;
  private defaultLanguage: string = 'en';
  
  constructor(languages: string[]) {
    this.supportedLanguages = new Set(languages);
  }
  
  negotiate(request: Request): string {
    const acceptLanguage = request.headers['accept-language'];
    
    if (!acceptLanguage) {
      return this.defaultLanguage;
    }
    
    const languages = this.parseAcceptLanguage(acceptLanguage);
    
    for (const lang of languages) {
      if (this.supportedLanguages.has(lang.code)) {
        return lang.code;
      }
      
      // 언어 코드만 체크 (예: en-US -> en)
      const baseCode = lang.code.split('-')[0];
      if (this.supportedLanguages.has(baseCode)) {
        return baseCode;
      }
    }
    
    return this.defaultLanguage;
  }
  
  private parseAcceptLanguage(header: string): LanguagePreference[] {
    return header.split(',').map(part => {
      const [code, ...params] = part.trim().split(';');
      
      let quality = 1.0;
      const qParam = params.find(p => p.trim().startsWith('q='));
      
      if (qParam) {
        quality = parseFloat(qParam.split('=')[1]);
      }
      
      return { code: code.trim(), quality };
    }).sort((a, b) => b.quality - a.quality);
  }
}

// 인코딩 협상
export class EncodingNegotiator {
  private encoders: Map<string, Encoder>;
  
  constructor() {
    this.encoders = new Map([
      ['gzip', new GzipEncoder()],
      ['br', new BrotliEncoder()],
      ['deflate', new DeflateEncoder()],
      ['identity', new IdentityEncoder()]
    ]);
  }
  
  negotiate(request: Request): string[] {
    const acceptEncoding = request.headers['accept-encoding'];
    
    if (!acceptEncoding) {
      return ['identity'];
    }
    
    const encodings = acceptEncoding
      .split(',')
      .map(e => e.trim())
      .filter(e => this.encoders.has(e));
    
    return encodings.length > 0 ? encodings : ['identity'];
  }
  
  async encode(
    data: Buffer,
    encoding: string
  ): Promise<EncodedResponse> {
    const encoder = this.encoders.get(encoding);
    
    if (!encoder) {
      return {
        data,
        encoding: 'identity'
      };
    }
    
    const encoded = await encoder.encode(data);
    
    return {
      data: encoded,
      encoding,
      headers: {
        'Content-Encoding': encoding
      }
    };
  }
}

// 통합 콘텐츠 협상 미들웨어
export class ContentNegotiationMiddleware {
  private contentNegotiator: ContentNegotiator;
  private languageNegotiator: LanguageNegotiator;
  private encodingNegotiator: EncodingNegotiator;
  
  async handle(request: Request, next: Handler): Promise<Response> {
    // 협상 실행
    const contentType = this.contentNegotiator.negotiate(request);
    const language = this.languageNegotiator.negotiate(request);
    const encodings = this.encodingNegotiator.negotiate(request);
    
    // 컨텍스트에 저장
    request.negotiated = {
      contentType,
      language,
      encodings
    };
    
    // 다음 핸들러 실행
    const response = await next(request);
    
    // 응답 변환
    if (response.data) {
      // 언어 적용
      const localizedData = await this.applyLocalization(
        response.data,
        language
      );
      
      // 포맷 적용
      const formatted = await this.contentNegotiator.format(
        localizedData,
        contentType
      );
      
      response.body = formatted.body;
      response.headers = {
        ...response.headers,
        ...formatted.headers,
        'Content-Language': language
      };
      
      // 인코딩 적용
      if (encodings[0] !== 'identity') {
        const encoded = await this.encodingNegotiator.encode(
          Buffer.from(response.body),
          encodings[0]
        );
        
        response.body = encoded.data;
        response.headers = {
          ...response.headers,
          ...encoded.headers
        };
      }
    }
    
    // Vary 헤더 추가
    response.headers['Vary'] = 'Accept, Accept-Language, Accept-Encoding';
    
    return response;
  }
}
```

**검증 기준**:
- [ ] Accept 헤더 파싱
- [ ] 다양한 콘텐츠 타입 지원
- [ ] 언어 협상
- [ ] 인코딩 협상

#### SubTask 6.9.4: 응답 메타데이터 관리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/api/rest/response/metadata_manager.py
class ResponseMetadataManager:
    """응답 메타데이터 관리"""
    
    def __init__(self):
        self.metadata_providers = []
        self.register_default_providers()
    
    def register_default_providers(self):
        """기본 메타데이터 제공자 등록"""
        
        self.add_provider(TimestampProvider())
        self.add_provider(VersionProvider())
        self.add_provider(RequestIdProvider())
        self.add_provider(ProcessingTimeProvider())
        self.add_provider(RateLimitProvider())
        self.add_provider(CacheProvider())
        self.add_provider(DebugProvider())
    
    async def generate_metadata(
        self,
        request: Request,
        response: Response,
        context: Dict
    ) -> Dict[str, Any]:
        """메타데이터 생성"""
        
        metadata = {}
        
        for provider in self.metadata_providers:
            if provider.should_include(request, context):
                provider_meta = await provider.generate(request, response, context)
                metadata.update(provider_meta)
        
        return metadata

class TimestampProvider(MetadataProvider):
    """타임스탬프 메타데이터"""
    
    async def generate(
        self,
        request: Request,
        response: Response,
        context: Dict
    ) -> Dict:
        return {
            'timestamp': datetime.now().isoformat(),
            'timezone': 'UTC'
        }

class ProcessingTimeProvider(MetadataProvider):
    """처리 시간 메타데이터"""
    
    async def generate(
        self,
        request: Request,
        response: Response,
        context: Dict
    ) -> Dict:
        start_time = context.get('start_time')
        
        if not start_time:
            return {}
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'processingTime': {
                'total': processing_time,
                'unit': 'milliseconds',
                'breakdown': context.get('time_breakdown', {})
            }
        }

class RateLimitProvider(MetadataProvider):
    """Rate Limit 메타데이터"""
    
    async def generate(
        self,
        request: Request,
        response: Response,
        context: Dict
    ) -> Dict:
        rate_limit = context.get('rate_limit')
        
        if not rate_limit:
            return {}
        
        return {
            'rateLimit': {
                'limit': rate_limit.limit,
                'remaining': rate_limit.remaining,
                'reset': rate_limit.reset_at.isoformat(),
                'retryAfter': rate_limit.retry_after
            }
        }

class CacheProvider(MetadataProvider):
    """캐시 메타데이터"""
    
    async def generate(
        self,
        request: Request,
        response: Response,
        context: Dict
    ) -> Dict:
        cache_info = context.get('cache_info')
        
        if not cache_info:
            return {}
        
        return {
            'cache': {
                'status': cache_info.status,  # HIT, MISS, BYPASS
                'ttl': cache_info.ttl,
                'age': cache_info.age,
                'tags': cache_info.tags
            }
        }

class DebugProvider(MetadataProvider):
    """디버그 메타데이터"""
    
    def should_include(self, request: Request, context: Dict) -> bool:
        """개발 환경이거나 디버그 모드일 때만 포함"""
        
        return (
            context.get('environment') == 'development' or
            request.headers.get('X-Debug') == 'true'
        )
    
    async def generate(
        self,
        request: Request,
        response: Response,
        context: Dict
    ) -> Dict:
        return {
            'debug': {
                'query': context.get('executed_query'),
                'queryCount': context.get('query_count'),
                'memoryUsage': self.get_memory_usage(),
                'stackTrace': context.get('stack_trace'),
                'logs': context.get('debug_logs', [])
            }
        }

class ResponseEnricher:
    """응답 보강"""
    
    def __init__(self):
        self.enrichers = []
    
    async def enrich(
        self,
        response: Dict,
        request: Request,
        context: Dict
    ) -> Dict:
        """응답 데이터 보강"""
        
        enriched = response.copy()
        
        # 메타데이터 추가
        metadata = await self.metadata_manager.generate_metadata(
            request,
            response,
            context
        )
        
        if metadata:
            enriched['meta'] = metadata
        
        # 하이퍼미디어 추가
        if context.get('include_links'):
            links = await self.link_generator.generate_links(
                response,
                request
            )
            enriched['links'] = links
        
        # 번역 적용
        if context.get('language'):
            enriched = await self.translator.translate(
                enriched,
                context['language']
            )
        
        # 필드 마스킹
        if context.get('mask_sensitive'):
            enriched = self.mask_sensitive_fields(enriched)
        
        return enriched
```

**검증 기준**:
- [ ] 다양한 메타데이터 제공
- [ ] 조건부 메타데이터 포함
- [ ] 디버그 정보 관리
- [ ] 응답 보강 기능

---

### Task 6.10: RESTful 에러 처리

#### SubTask 6.10.1: 에러 응답 표준화

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/rest/error/error-standards.ts
export interface StandardErrorResponse {
  success: false;
  error: ErrorDetail;
  meta?: ErrorMetadata;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: any;
  field?: string;
  helpUrl?: string;
  timestamp?: string;
  traceId?: string;
}

export class ErrorResponseBuilder {
  private config: ErrorConfig;
  
  constructor(config: ErrorConfig) {
    this.config = config;
  }
  
  build(error: Error | AppError): StandardErrorResponse {
    const errorDetail = this.extractErrorDetail(error);
    
    const response: StandardErrorResponse = {
      success: false,
      error: errorDetail
    };
    
    // 메타데이터 추가
    if (this.config.includeMetadata) {
      response.meta = this.generateMetadata(error);
    }
    
    // 민감한 정보 제거
    if (this.config.environment === 'production') {
      this.sanitizeError(response);
    }
    
    return response;
  }
  
  private extractErrorDetail(error: Error | AppError): ErrorDetail {
    if (this.isAppError(error)) {
      return {
        code: error.code,
        message: error.message,
        details: error.details,
        field: error.field,
        helpUrl: this.generateHelpUrl(error.code),
        timestamp: new Date().toISOString(),
        traceId: error.traceId || generateTraceId()
      };
    }
    
    // 일반 에러
    return {
      code: 'INTERNAL_ERROR',
      message: this.config.genericErrorMessage || 'An error occurred',
      timestamp: new Date().toISOString(),
      traceId: generateTraceId()
    };
  }
  
  private sanitizeError(response: StandardErrorResponse): void {
    // 스택 트레이스 제거
    delete response.error.details?.stack;
    
    // 내부 경로 정보 제거
    if (response.error.details?.path) {
      response.error.details.path = this.sanitizePath(response.error.details.path);
    }
    
    // 데이터베이스 정보 제거
    delete response.error.details?.query;
    delete response.error.details?.connection;
  }
}

// 다국어 에러 메시지
export class LocalizedErrorMessages {
  private messages: Map<string, Map<string, string>>;
  
  constructor() {
    this.loadMessages();
  }
  
  private loadMessages(): void {
    this.messages = new Map([
      ['en', new Map([
        ['VALIDATION_ERROR', 'Validation failed'],
        ['NOT_FOUND', 'Resource not found'],
        ['UNAUTHORIZED', 'Authentication required'],
        ['FORBIDDEN', 'Access denied'],
        ['RATE_LIMIT', 'Too many requests'],
        ['INTERNAL_ERROR', 'Internal server error']
      ])],
      ['ko', new Map([
        ['VALIDATION_ERROR', '유효성 검사 실패'],
        ['NOT_FOUND', '리소스를 찾을 수 없습니다'],
        ['UNAUTHORIZED', '인증이 필요합니다'],
        ['FORBIDDEN', '접근이 거부되었습니다'],
        ['RATE_LIMIT', '요청이 너무 많습니다'],
        ['INTERNAL_ERROR', '내부 서버 오류']
      ])]
    ]);
  }
  
  getMessage(code: string, language: string = 'en'): string {
    const languageMessages = this.messages.get(language) || this.messages.get('en');
    return languageMessages?.get(code) || code;
  }
}

// 구조화된 검증 에러
export class ValidationErrorFormatter {
  format(validationErrors: ValidationError[]): ErrorDetail {
    return {
      code: 'VALIDATION_ERROR',
      message: 'Validation failed',
      details: {
        errors: validationErrors.map(err => ({
          field: err.field,
          code: err.code,
          message: err.message,
          value: this.sanitizeValue(err.value)
        }))
      }
    };
  }
  
  private sanitizeValue(value: any): any {
    // 민감한 필드 마스킹
    if (typeof value === 'string' && value.length > 100) {
      return value.substring(0, 100) + '...';
    }
    return value;
  }
}
```

**검증 기준**:
- [ ] 표준 에러 구조
- [ ] 다국어 지원
- [ ] 민감 정보 제거
- [ ] 검증 에러 포맷

#### SubTask 6.10.2: HTTP 상태 코드 매핑

**담당자**: 백엔드 개발자  
**예상 소요시간**: 8시간

**작업 내용**:

```python
# backend/src/api/rest/error/status_code_mapper.py
from enum import Enum
from typing import Dict, Type

class HTTPStatus(Enum):
    """HTTP 상태 코드"""
    
    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    PARTIAL_CONTENT = 206
    
    # 3xx Redirection
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    
    # 4xx Client Error
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    IM_A_TEAPOT = 418  # RFC 2324
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    TOO_EARLY = 425
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    
    # 5xx Server Error
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511

class StatusCodeMapper:
    """에러 코드를 HTTP 상태 코드로 매핑"""
    
    def __init__(self):
        self.mappings = self.initialize_mappings()
        self.custom_mappings = {}
    
    def initialize_mappings(self) -> Dict[str, int]:
        """기본 매핑 초기화"""
        
        return {
            # 검증 에러
            'VALIDATION_ERROR': HTTPStatus.BAD_REQUEST.value,
            'INVALID_INPUT': HTTPStatus.BAD_REQUEST.value,
            'MISSING_FIELD': HTTPStatus.BAD_REQUEST.value,
            'INVALID_FORMAT': HTTPStatus.BAD_REQUEST.value,
            
            # 인증/인가
            'AUTHENTICATION_REQUIRED': HTTPStatus.UNAUTHORIZED.value,
            'INVALID_CREDENTIALS': HTTPStatus.UNAUTHORIZED.value,
            'TOKEN_EXPIRED': HTTPStatus.UNAUTHORIZED.value,
            'ACCESS_DENIED': HTTPStatus.FORBIDDEN.value,
            'INSUFFICIENT_PERMISSIONS': HTTPStatus.FORBIDDEN.value,
            
            # 리소스 에러
            'RESOURCE_NOT_FOUND': HTTPStatus.NOT_FOUND.value,
            'ENDPOINT_NOT_FOUND': HTTPStatus.NOT_FOUND.value,
            'RESOURCE_ALREADY_EXISTS': HTTPStatus.CONFLICT.value,
            'RESOURCE_CONFLICT': HTTPStatus.CONFLICT.value,
            'RESOURCE_GONE': HTTPStatus.GONE.value,
            
            # 요청 에러
            'METHOD_NOT_ALLOWED': HTTPStatus.METHOD_NOT_ALLOWED.value,
            'UNSUPPORTED_MEDIA_TYPE': HTTPStatus.UNSUPPORTED_MEDIA_TYPE.value,
            'NOT_ACCEPTABLE': HTTPStatus.NOT_ACCEPTABLE.value,
            'REQUEST_TOO_LARGE': HTTPStatus.PAYLOAD_TOO_LARGE.value,
            'RATE_LIMIT_EXCEEDED': HTTPStatus.TOO_MANY_REQUESTS.value,
            
            # 비즈니스 로직 에러
            'BUSINESS_RULE_VIOLATION': HTTPStatus.UNPROCESSABLE_ENTITY.value,
            'PRECONDITION_FAILED': HTTPStatus.PRECONDITION_FAILED.value,
            'OPERATION_NOT_ALLOWED': HTTPStatus.UNPROCESSABLE_ENTITY.value,
            
            # 서버 에러
            'INTERNAL_ERROR': HTTPStatus.INTERNAL_SERVER_ERROR.value,
            'SERVICE_UNAVAILABLE': HTTPStatus.SERVICE_UNAVAILABLE.value,
            'DEPENDENCY_ERROR': HTTPStatus.BAD_GATEWAY.value,
            'TIMEOUT': HTTPStatus.GATEWAY_TIMEOUT.value,
            'NOT_IMPLEMENTED': HTTPStatus.NOT_IMPLEMENTED.value
        }
    
    def map_error_to_status(self, error: AppError) -> int:
        """에러를 상태 코드로 매핑"""
        
        # 커스텀 매핑 확인
        if error.code in self.custom_mappings:
            return self.custom_mappings[error.code]
        
        # 기본 매핑 확인
        if error.code in self.mappings:
            return self.mappings[error.code]
        
        # 에러 타입별 기본값
        if isinstance(error, ValidationError):
            return HTTPStatus.BAD_REQUEST.value
        elif isinstance(error, AuthenticationError):
            return HTTPStatus.UNAUTHORIZED.value
        elif isinstance(error, AuthorizationError):
            return HTTPStatus.FORBIDDEN.value
        elif isinstance(error, NotFoundError):
            return HTTPStatus.NOT_FOUND.value
        elif isinstance(error, ConflictError):
            return HTTPStatus.CONFLICT.value
        elif isinstance(error, RateLimitError):
            return HTTPStatus.TOO_MANY_REQUESTS.value
        
        # 기본값
        return HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def add_custom_mapping(self, error_code: str, status_code: int):
        """커스텀 매핑 추가"""
        
        self.custom_mappings[error_code] = status_code
    
    def get_status_description(self, status_code: int) -> str:
        """상태 코드 설명"""
        
        descriptions = {
            200: "OK - Request succeeded",
            201: "Created - Resource created successfully",
            204: "No Content - Request succeeded with no response body",
            400: "Bad Request - Invalid request syntax or parameters",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access denied",
            404: "Not Found - Resource does not exist",
            409: "Conflict - Request conflicts with current state",
            422: "Unprocessable Entity - Request understood but invalid",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - Server encountered an error",
            503: "Service Unavailable - Server temporarily unavailable"
        }
        
        return descriptions.get(status_code, "Unknown status code")
```

**검증 기준**:
- [ ] 완전한 상태 코드 매핑
- [ ] 에러 타입별 기본값
- [ ] 커스텀 매핑 지원
- [ ] 상태 코드 설명

#### SubTask 6.10.3: 문제 세부사항 (RFC 7807) 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/api/rest/error/problem-details.ts
export interface ProblemDetails {
  type?: string;      // URI reference
  title: string;      // Short summary
  status: number;     // HTTP status code
  detail?: string;    // Specific error details
  instance?: string;  // URI reference to specific occurrence
  [key: string]: any; // Additional members
}

export class ProblemDetailsBuilder {
  private problemTypes: Map<string, ProblemType>;
  
  constructor() {
    this.initializeProblemTypes();
  }
  
  private initializeProblemTypes(): void {
    this.problemTypes = new Map([
      ['validation-error', {
        type: 'https://api.t-developer.com/problems/validation-error',
        title: 'Validation Error',
        status: 400
      }],
      ['authentication-required', {
        type: 'https://api.t-developer.com/problems/authentication-required',
        title: 'Authentication Required',
        status: 401
      }],
      ['insufficient-balance', {
        type: 'https://api.t-developer.com/problems/insufficient-balance',
        title: 'Insufficient Balance',
        status: 402
      }],
      ['resource-not-found', {
        type: 'https://api.t-developer.com/problems/resource-not-found',
        title: 'Resource Not Found',
        status: 404
      }],
      ['rate-limit-exceeded', {
        type: 'https://api.t-developer.com/problems/rate-limit-exceeded',
        title: 'Rate Limit Exceeded',
        status: 429
      }]
    ]);
  }
  
  build(error: AppError, request?: Request): ProblemDetails {
    const problemType = this.problemTypes.get(error.problemType) || {
      title: 'Error',
      status: 500
    };
    
    const problem: ProblemDetails = {
      type: problemType.type,
      title: problemType.title,
      status: problemType.status,
      detail: error.message
    };
    
    // Instance URI
    if (request) {
      problem.instance = request.url;
    }
    
    // 추가 속성
    this.addExtensions(problem, error);
    
    return problem;
  }
  
  private addExtensions(problem: ProblemDetails, error: AppError): void {
    // 검증 에러 확장
    if (error.type === 'validation' && error.validationErrors) {
      problem['errors'] = error.validationErrors.map(ve => ({
        field: ve.field,
        message: ve.message,
        code: ve.code
      }));
    }
    
    // Rate Limit 확장
    if (error.type === 'rate-limit') {
      problem['rate-limit'] = {
        limit: error.limit,
        remaining: error.remaining,
        reset: error.resetAt
      };
    }
    
    // 트레이싱 정보
    if (error.traceId) {
      problem['trace-id'] = error.traceId;
    }
    
    // 도움말 링크
    if (error.helpUrl) {
      problem['help'] = error.helpUrl;
    }
  }
}

// Problem Details 미들웨어
export class ProblemDetailsMiddleware {
  private builder: ProblemDetailsBuilder;
  private contentType = 'application/problem+json';
  
  constructor() {
    this.builder = new ProblemDetailsBuilder();
  }
  
  async handle(error: Error, request: Request): Promise<Response> {
    // AppError로 변환
    const appError = this.toAppError(error);
    
    // Problem Details 생성
    const problemDetails = this.builder.build(appError, request);
    
    // 응답 생성
    return {
      status: problemDetails.status,
      headers: {
        'Content-Type': this.contentType
      },
      body: problemDetails
    };
  }
  
  private toAppError(error: Error): AppError {
    if (error instanceof AppError) {
      return error;
    }
    
    // 일반 에러를 AppError로 변환
    return new AppError({
      code: 'INTERNAL_ERROR',
      message: error.message,
      problemType: 'internal-error'
    });
  }
}

// 커스텀 Problem Type 정의
export class CustomProblemType {
  constructor(
    private baseUrl: string = 'https://api.t-developer.com/problems'
  ) {}
  
  define(name: string, definition: ProblemTypeDefinition): string {
    const typeUrl = `${this.baseUrl}/${name}`;
    
    // 문서 생성
    this.generateDocumentation(typeUrl, definition);
    
    return typeUrl;
  }
  
  private generateDocumentation(
    typeUrl: string,
    definition: ProblemTypeDefinition
  ): void {
    const doc = `
# Problem Type: ${definition.title}

**URI**: ${typeUrl}
**Status**: ${definition.status}

## Description
${definition.description}

## Members
${this.documentMembers(definition.members)}

## Example
\`\`\`json
${JSON.stringify(definition.example, null, 2)}
\`\`\`
    `;
    
    // 문서 저장
    this.saveDocumentation(typeUrl, doc);
  }
}
```

**검증 기준**:
- [ ] RFC 7807 준수
- [ ] Problem Type 정의
- [ ] 확장 필드 지원
- [ ] 문서화 자동 생성

#### SubTask 6.10.4: 에러 복구 및 재시도 전략

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/api/rest/error/recovery_strategy.py
from typing import Optional, Callable, Any
import asyncio
from datetime import datetime, timedelta

class RetryStrategy:
    """재시도 전략"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """재시도 지연 시간 계산"""
        
        # Exponential backoff
        delay = self.initial_delay * (self.exponential_base ** attempt)
        
        # 최대 지연 제한
        delay = min(delay, self.max_delay)
        
        # Jitter 추가 (랜덤성)
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """재시도 여부 결정"""
        
        # 최대 시도 횟수 확인
        if attempt >= self.max_attempts:
            return False
        
        # 재시도 가능한 에러인지 확인
        if not self.is_retryable(error):
            return False
        
        return True
    
    def is_retryable(self, error: Exception) -> bool:
        """재시도 가능한 에러 판단"""
        
        # 네트워크 에러
        if isinstance(error, (ConnectionError, TimeoutError)):
            return True
        
        # HTTP 상태 코드 기반
        if hasattr(error, 'status_code'):
            retryable_statuses = [
                408,  # Request Timeout
                429,  # Too Many Requests
                500,  # Internal Server Error
                502,  # Bad Gateway
                503,  # Service Unavailable
                504   # Gateway Timeout
            ]
            return error.status_code in retryable_statuses
        
        return False

class CircuitBreaker:
    """Circuit Breaker 패턴"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Circuit Breaker를 통한 함수 호출"""
        
        # OPEN 상태 확인
        if self.state == CircuitState.OPEN:
            if self.should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit breaker is OPEN")
        
        try:
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 성공 시 처리
            self.on_success()
            
            return result
            
        except self.expected_exception as e:
            # 실패 시 처리
            self.on_failure()
            raise e
    
    def on_success(self):
        """성공 시 처리"""
        
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
    
    def on_failure(self):
        """실패 시 처리"""
        
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def should_attempt_reset(self) -> bool:
        """리셋 시도 여부"""
        
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > 
            timedelta(seconds=self.recovery_timeout)
        )

class ErrorRecoveryManager:
    """에러 복구 관리"""
    
    def __init__(self):
        self.retry_strategy = RetryStrategy()
        self.circuit_breakers = {}
        self.fallback_handlers = {}
    
    async def execute_with_recovery(
        self,
        func: Callable,
        *args,
        recovery_options: RecoveryOptions = None,
        **kwargs
    ) -> Any:
        """복구 전략과 함께 실행"""
        
        options = recovery_options or RecoveryOptions()
        
        # Circuit Breaker 적용
        if options.use_circuit_breaker:
            circuit_breaker = self.get_circuit_breaker(options.service_name)
            func = partial(circuit_breaker.call, func)
        
        # 재시도 로직
        last_error = None
        
        for attempt in range(options.max_retries + 1):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_error = e
                
                # 재시도 가능 여부 확인
                if not self.retry_strategy.should_retry(e, attempt):
                    break
                
                # 재시도 지연
                delay = self.retry_strategy.calculate_delay(attempt)
                await asyncio.sleep(delay)
                
                # 로깅
                await self.log_retry(func.__name__, attempt, e, delay)
        
        # 모든 재시도 실패
        if options.fallback:
            return await self.execute_fallback(
                options.fallback,
                last_error,
                *args,
                **kwargs
            )
        
        raise last_error
    
    async def execute_fallback(
        self,
        fallback: Callable,
        original_error: Exception,
        *args,
        **kwargs
    ) -> Any:
        """Fallback 실행"""
        
        try:
            return await fallback(original_error, *args, **kwargs)
        except Exception as fallback_error:
            # Fallback도 실패한 경우
            raise FallbackError(
                "Fallback execution failed",
                original_error=original_error,
                fallback_error=fallback_error
            )
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """서비스별 Circuit Breaker 조회"""
        
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        
        return self.circuit_breakers[service_name]

class CompensationHandler:
    """보상 트랜잭션 처리"""
    
    def __init__(self):
        self.compensation_stack = []
    
    async def execute_with_compensation(
        self,
        operations: List[Operation]
    ) -> Any:
        """보상 가능한 작업 실행"""
        
        completed_operations = []
        
        try:
            # 순차적으로 작업 실행
            for operation in operations:
                result = await operation.execute()
                completed_operations.append(operation)
                
                # 보상 작업 등록
                if operation.has_compensation:
                    self.compensation_stack.append(operation)
            
            return result
            
        except Exception as e:
            # 실패 시 보상 실행
            await self.compensate(completed_operations)
            raise e
    
    async def compensate(self, operations: List[Operation]):
        """보상 작업 실행"""
        
        # 역순으로 보상 실행
        for operation in reversed(operations):
            if operation.has_compensation:
                try:
                    await operation.compensate()
                except Exception as comp_error:
                    # 보상 실패 로깅
                    await self.log_compensation_failure(
                        operation,
                        comp_error
                    )

class AdaptiveRetryStrategy:
    """적응형 재시도 전략"""
    
    def __init__(self):
        self.success_rate_threshold = 0.8
        self.window_size = 100
        self.history = deque(maxlen=self.window_size)
    
    def update_strategy(self, success: bool):
        """전략 업데이트"""
        
        self.history.append(success)
        
        if len(self.history) >= self.window_size:
            success_rate = sum(self.history) / len(self.history)
            
            if success_rate < self.success_rate_threshold:
                # 재시도 간격 증가
                self.increase_delay()
            else:
                # 재시도 간격 감소
                self.decrease_delay()
    
    def increase_delay(self):
        """지연 시간 증가"""
        
        self.initial_delay = min(self.initial_delay * 1.5, self.max_delay)
        self.max_attempts = max(self.max_attempts - 1, 1)
    
    def decrease_delay(self):
        """지연 시간 감소"""
        
        self.initial_delay = max(self.initial_delay * 0.8, 0.1)
        self.max_attempts = min(self.max_attempts + 1, 10)

# 에러 복구 데코레이터
def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """재시도 데코레이터"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_strategy = RetryStrategy(
                max_attempts=max_attempts,
                initial_delay=delay
            )
            
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    
                    if attempt < max_attempts - 1:
                        delay = retry_strategy.calculate_delay(attempt)
                        await asyncio.sleep(delay)
                    else:
                        raise e
            
            raise last_error
        
        return wrapper
    return decorator

def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60
):
    """Circuit Breaker 데코레이터"""
    
    circuit_breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout
    )
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator

class ErrorRecoveryMiddleware:
    """에러 복구 미들웨어"""
    
    def __init__(self):
        self.recovery_manager = ErrorRecoveryManager()
        self.metrics = RecoveryMetrics()
    
    async def handle(self, request: Request, next: Handler) -> Response:
        """요청 처리 with 복구"""
        
        recovery_options = self.get_recovery_options(request)
        
        try:
            # 정상 처리
            response = await self.recovery_manager.execute_with_recovery(
                next,
                request,
                recovery_options=recovery_options
            )
            
            # 성공 메트릭
            await self.metrics.record_success(request.path)
            
            return response
            
        except Exception as e:
            # 실패 메트릭
            await self.metrics.record_failure(request.path, e)
            
            # 에러 응답 생성
            return self.create_error_response(e, request)
    
    def get_recovery_options(self, request: Request) -> RecoveryOptions:
        """요청별 복구 옵션"""
        
        # 엔드포인트별 설정
        endpoint_config = self.get_endpoint_config(request.path)
        
        return RecoveryOptions(
            max_retries=endpoint_config.get('max_retries', 3),
            use_circuit_breaker=endpoint_config.get('circuit_breaker', True),
            fallback=endpoint_config.get('fallback'),
            timeout=endpoint_config.get('timeout', 30)
        )
```

**검증 기준**:
- [ ] 재시도 전략 구현
- [ ] Circuit Breaker 패턴
- [ ] 보상 트랜잭션
- [ ] 적응형 복구 전략

---

## 📊 Phase 6 Tasks 6.6-6.10 완료 현황

### ✅ 완료된 작업
- **Task 6.6**: REST 엔드포인트 설계 (4 SubTasks)
  - RESTful 리소스 모델링
  - URL 구조 및 네이밍 규칙
  - HTTP 메서드 매핑
  - 리소스 관계 및 중첩 구조

- **Task 6.7**: CRUD 작업 구현 (4 SubTasks)
  - Create 작업 구현
  - Read 작업 구현
  - Update 작업 구현
  - Delete 작업 구현

- **Task 6.8**: 페이지네이션 및 필터링 (4 SubTasks)
  - 페이지네이션 전략 구현
  - 필터링 시스템 구축
  - 정렬 및 검색 기능
  - 커서 기반 페이지네이션

- **Task 6.9**: 응답 포맷 표준화 (4 SubTasks)
  - 응답 구조 표준 정의
  - HATEOAS 구현
  - 콘텐츠 협상 처리
  - 응답 메타데이터 관리

- **Task 6.10**: RESTful 에러 처리 (4 SubTasks)
  - 에러 응답 표준화
  - HTTP 상태 코드 매핑
  - 문제 세부사항 (RFC 7807) 구현
  - 에러 복구 및 재시도 전략

### 📈 진행률
- Tasks 6.6-6.10 진행률: 100%
- 총 20개 SubTasks 완료
- 예상 소요시간: 220시간

### 🎯 주요 성과

1. **완전한 RESTful API 구현**
   - T-Developer 9개 에이전트 통합
   - 표준 REST 원칙 준수
   - 리소스 중심 설계

2. **고급 CRUD 기능**
   - 트랜잭션 처리
   - 낙관적 잠금
   - 소프트/하드 삭제
   - 일괄 작업 지원

3. **강력한 쿼리 기능**
   - 다양한 페이지네이션 전략
   - 고급 필터링 시스템
   - 전문 검색 및 정렬
   - 커서 기반 무한 스크롤

4. **표준 준수 응답 포맷**
   - JSON:API, HAL 지원
   - HATEOAS 구현
   - 콘텐츠 협상
   - 풍부한 메타데이터

5. **견고한 에러 처리**
   - RFC 7807 Problem Details
   - 완전한 HTTP 상태 코드 매핑
   - Circuit Breaker 패턴
   - 자동 재시도 및 복구

### 📋 전체 Phase 6 진행 상황
- **완료된 Tasks**: 10/15 (Tasks 6.1-6.10)
- **진행률**: 66.7%
- **남은 Tasks**: 
  - Task 6.11: GraphQL API 구현
  - Task 6.12: WebSocket 통신
  - Task 6.13: API 문서화
  - Task 6.14: SDK 생성
  - Task 6.15: API 게이트웨이 통합 테스트

### 🔗 연관성 및 통합 포인트

**에이전트 시스템 통합**:
- 9개 에이전트 엔드포인트 완성
- 각 에이전트별 CRUD 작업
- 에이전트 실행 상태 추적

**API Gateway 연동**:
- 라우팅 엔진과 REST 엔드포인트 매핑
- 버전 관리 시스템 통합
- 로드 밸런싱 적용

**보안 및 성능**:
- Rate Limiting 통합
- 캐싱 전략 구현
- 인증/인가 미들웨어

---
