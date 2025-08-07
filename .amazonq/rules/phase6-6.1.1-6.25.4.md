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
## Phase 6: GraphQL API 구현 & WebSocket 통신 (Tasks 6.11-6.16) - SubTask 리스트 및 작업지시서

### 📋 SubTask 전체 리스트

#### Task 6.11: GraphQL 스키마 정의
- **SubTask 6.11.1**: 타입 시스템 및 스칼라 정의
- **SubTask 6.11.2**: 객체 타입 및 인터페이스 설계
- **SubTask 6.11.3**: 쿼리 및 뮤테이션 스키마
- **SubTask 6.11.4**: 스키마 유효성 검증 및 최적화

#### Task 6.12: Resolver 구현
- **SubTask 6.12.1**: 쿼리 리졸버 구현
- **SubTask 6.12.2**: 뮤테이션 리졸버 구현
- **SubTask 6.12.3**: 필드 리졸버 및 관계 처리
- **SubTask 6.12.4**: DataLoader 및 배치 처리

#### Task 6.13: Subscription 및 실시간 업데이트
- **SubTask 6.13.1**: Subscription 스키마 정의
- **SubTask 6.13.2**: PubSub 시스템 구현
- **SubTask 6.13.3**: 실시간 이벤트 필터링
- **SubTask 6.13.4**: 연결 관리 및 확장성

#### Task 6.14: WebSocket 서버 구현
- **SubTask 6.14.1**: WebSocket 서버 초기화
- **SubTask 6.14.2**: 연결 핸들링 및 인증
- **SubTask 6.14.3**: 메시지 프로토콜 정의
- **SubTask 6.14.4**: 연결 풀 관리

#### Task 6.15: 실시간 이벤트 스트리밍
- **SubTask 6.15.1**: 이벤트 스트림 아키텍처
- **SubTask 6.15.2**: 이벤트 발행 시스템
- **SubTask 6.15.3**: 구독 관리 시스템
- **SubTask 6.15.4**: 백프레셔 및 흐름 제어

#### Task 6.16: 양방향 통신 프로토콜
- **SubTask 6.16.1**: 메시지 포맷 정의
- **SubTask 6.16.2**: RPC over WebSocket
- **SubTask 6.16.3**: 상태 동기화 메커니즘
- **SubTask 6.16.4**: 오류 처리 및 재연결 전략

---

## 📝 세부 작업지시서

### Task 6.11: GraphQL 스키마 정의

#### SubTask 6.11.1: 타입 시스템 및 스칼라 정의

**담당자**: 백엔드 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/graphql/schema/scalars.ts
import { GraphQLScalarType, Kind } from 'graphql';

// DateTime 스칼라 타입
export const DateTimeScalar = new GraphQLScalarType({
  name: 'DateTime',
  description: 'Date and time in ISO 8601 format',
  serialize(value: any): string {
    if (value instanceof Date) {
      return value.toISOString();
    }
    return value;
  },
  parseValue(value: any): Date {
    return new Date(value);
  },
  parseLiteral(ast): Date | null {
    if (ast.kind === Kind.STRING) {
      return new Date(ast.value);
    }
    return null;
  }
});

// JSON 스칼라 타입
export const JSONScalar = new GraphQLScalarType({
  name: 'JSON',
  description: 'Arbitrary JSON object',
  serialize(value: any): any {
    return value;
  },
  parseValue(value: any): any {
    return value;
  },
  parseLiteral(ast): any {
    switch (ast.kind) {
      case Kind.STRING:
      case Kind.BOOLEAN:
        return ast.value;
      case Kind.INT:
      case Kind.FLOAT:
        return parseFloat(ast.value);
      case Kind.OBJECT:
        return parseObject(ast);
      case Kind.LIST:
        return ast.values.map(parseLiteral);
      default:
        return null;
    }
  }
});

// UUID 스칼라 타입
export const UUIDScalar = new GraphQLScalarType({
  name: 'UUID',
  description: 'UUID v4',
  serialize(value: any): string {
    return value;
  },
  parseValue(value: any): string {
    if (!isValidUUID(value)) {
      throw new Error('Invalid UUID format');
    }
    return value;
  },
  parseLiteral(ast): string | null {
    if (ast.kind === Kind.STRING && isValidUUID(ast.value)) {
      return ast.value;
    }
    return null;
  }
});

// 커스텀 스칼라: ComponentCode
export const ComponentCodeScalar = new GraphQLScalarType({
  name: 'ComponentCode',
  description: 'React/Vue/Angular component code',
  serialize(value: any): string {
    return value;
  },
  parseValue(value: any): string {
    // 코드 유효성 검증
    validateComponentCode(value);
    return value;
  },
  parseLiteral(ast): string | null {
    if (ast.kind === Kind.STRING) {
      validateComponentCode(ast.value);
      return ast.value;
    }
    return null;
  }
});

// 파일 업로드 스칼라
export const UploadScalar = new GraphQLScalarType({
  name: 'Upload',
  description: 'File upload',
  parseValue(value: any): any {
    return value; // Apollo Server의 파일 업로드 처리
  },
  parseLiteral(ast): never {
    throw new Error('Upload literal unsupported');
  },
  serialize(): never {
    throw new Error('Upload serialization unsupported');
  }
});

// 타입 정의 생성기
export class TypeSystemBuilder {
  private customScalars: Map<string, GraphQLScalarType> = new Map();
  
  constructor() {
    this.registerDefaultScalars();
  }
  
  private registerDefaultScalars(): void {
    this.customScalars.set('DateTime', DateTimeScalar);
    this.customScalars.set('JSON', JSONScalar);
    this.customScalars.set('UUID', UUIDScalar);
    this.customScalars.set('ComponentCode', ComponentCodeScalar);
    this.customScalars.set('Upload', UploadScalar);
  }
  
  generateScalarDefinitions(): string {
    const scalars = Array.from(this.customScalars.keys());
    return scalars.map(name => `scalar ${name}`).join('\n');
  }
  
  getScalarResolvers(): Record<string, GraphQLScalarType> {
    const resolvers: Record<string, GraphQLScalarType> = {};
    
    this.customScalars.forEach((scalar, name) => {
      resolvers[name] = scalar;
    });
    
    return resolvers;
  }
}

// Enum 타입 정의
export const EnumDefinitions = `
  enum ProjectStatus {
    DRAFT
    ACTIVE
    COMPLETED
    ARCHIVED
  }
  
  enum ComponentType {
    FUNCTIONAL
    CLASS
    HOOKS
    PROVIDER
    LAYOUT
  }
  
  enum AgentType {
    REQUIREMENTS_ANALYZER
    UI_GENERATOR
    COMPONENT_DESIGNER
    API_INTEGRATOR
    STATE_MANAGER
    ROUTE_CONFIGURATOR
    STYLE_OPTIMIZER
    TEST_GENERATOR
    DEPLOYMENT_PREPARER
  }
  
  enum SortOrder {
    ASC
    DESC
  }
  
  enum FilterOperator {
    EQ
    NE
    GT
    GTE
    LT
    LTE
    IN
    NIN
    CONTAINS
    STARTS_WITH
    ENDS_WITH
  }
`;

// Input 타입 정의
export const InputTypeDefinitions = `
  input PaginationInput {
    page: Int
    limit: Int
    cursor: String
  }
  
  input SortInput {
    field: String!
    order: SortOrder!
  }
  
  input FilterInput {
    field: String!
    operator: FilterOperator!
    value: JSON!
  }
  
  input QueryOptions {
    pagination: PaginationInput
    sort: [SortInput!]
    filters: [FilterInput!]
  }
`;
```

**검증 기준**:
- [ ] 커스텀 스칼라 타입 정의
- [ ] 유효성 검증 로직
- [ ] Enum 타입 완성도
- [ ] Input 타입 구조

#### SubTask 6.11.2: 객체 타입 및 인터페이스 설계

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```graphql
# backend/src/graphql/schema/types.graphql

# 인터페이스 정의
interface Node {
  id: ID!
}

interface Timestamped {
  createdAt: DateTime!
  updatedAt: DateTime!
}

interface Owned {
  owner: User!
}

# 프로젝트 타입
type Project implements Node & Timestamped & Owned {
  id: ID!
  name: String!
  description: String
  framework: String!
  status: ProjectStatus!
  owner: User!
  components: [Component!]!
  agents: [AgentExecution!]!
  settings: ProjectSettings!
  statistics: ProjectStatistics!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type ProjectSettings {
  id: ID!
  project: Project!
  theme: JSON
  buildConfig: JSON
  deploymentConfig: JSON
  environmentVariables: [EnvironmentVariable!]!
}

type ProjectStatistics {
  componentCount: Int!
  linesOfCode: Int!
  lastBuildTime: DateTime
  buildStatus: String
  testCoverage: Float
}

# 컴포넌트 타입
type Component implements Node & Timestamped {
  id: ID!
  name: String!
  type: ComponentType!
  category: String
  code: ComponentCode!
  styles: String
  props: [PropDefinition!]!
  dependencies: [Dependency!]!
  parent: Component
  children: [Component!]!
  project: Project!
  version: String!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type PropDefinition {
  name: String!
  type: String!
  required: Boolean!
  defaultValue: JSON
  description: String
}

type Dependency {
  name: String!
  version: String!
  type: String! # npm, component, asset
}

# 에이전트 실행 타입
type AgentExecution implements Node & Timestamped {
  id: ID!
  agent: AgentType!
  status: ExecutionStatus!
  input: JSON!
  output: JSON
  project: Project!
  triggeredBy: User!
  startedAt: DateTime
  completedAt: DateTime
  duration: Int
  error: ExecutionError
  logs: [ExecutionLog!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type ExecutionError {
  code: String!
  message: String!
  details: JSON
  stackTrace: String
}

type ExecutionLog {
  timestamp: DateTime!
  level: String!
  message: String!
  data: JSON
}

# 사용자 타입
type User implements Node & Timestamped {
  id: ID!
  email: String!
  name: String
  avatar: String
  role: UserRole!
  projects: [Project!]!
  executions: [AgentExecution!]!
  preferences: UserPreferences!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type UserPreferences {
  theme: String!
  language: String!
  notifications: NotificationSettings!
  shortcuts: JSON
}

type NotificationSettings {
  email: Boolean!
  push: Boolean!
  inApp: Boolean!
  agentCompleted: Boolean!
  deploymentStatus: Boolean!
}

# 페이지네이션 타입
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
  totalCount: Int
}

type ProjectConnection {
  edges: [ProjectEdge!]!
  pageInfo: PageInfo!
}

type ProjectEdge {
  node: Project!
  cursor: String!
}

# Union 타입
union SearchResult = Project | Component | User

# 에러 타입
type ValidationError {
  field: String!
  message: String!
  code: String!
}

type MutationResponse {
  success: Boolean!
  message: String
  errors: [ValidationError!]
}
```

```python
# backend/src/graphql/schema/type_registry.py
from typing import Dict, List, Type
from graphql import GraphQLObjectType, GraphQLInterfaceType

class TypeRegistry:
    """GraphQL 타입 레지스트리"""
    
    def __init__(self):
        self.types: Dict[str, GraphQLObjectType] = {}
        self.interfaces: Dict[str, GraphQLInterfaceType] = {}
        self.resolvers: Dict[str, Dict[str, callable]] = {}
    
    def register_type(self, name: str, type_def: GraphQLObjectType):
        """타입 등록"""
        self.types[name] = type_def
    
    def register_interface(self, name: str, interface: GraphQLInterfaceType):
        """인터페이스 등록"""
        self.interfaces[name] = interface
    
    def register_resolver(self, type_name: str, field_name: str, resolver: callable):
        """리졸버 등록"""
        if type_name not in self.resolvers:
            self.resolvers[type_name] = {}
        self.resolvers[type_name][field_name] = resolver
    
    def get_type_map(self) -> Dict:
        """전체 타입 맵 반환"""
        return {
            **self.types,
            **self.interfaces
        }

class TypeValidator:
    """타입 유효성 검증"""
    
    def validate_schema(self, schema: str) -> List[str]:
        """스키마 유효성 검증"""
        errors = []
        
        # 순환 참조 체크
        errors.extend(self.check_circular_references(schema))
        
        # 필수 필드 체크
        errors.extend(self.check_required_fields(schema))
        
        # 타입 일관성 체크
        errors.extend(self.check_type_consistency(schema))
        
        return errors
```

**검증 기준**:
- [ ] 인터페이스 설계
- [ ] 타입 관계 정의
- [ ] 페이지네이션 타입
- [ ] Union/Interface 활용

#### SubTask 6.11.3: 쿼리 및 뮤테이션 스키마

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```graphql
# backend/src/graphql/schema/operations.graphql

type Query {
  # 단일 조회
  project(id: ID!): Project
  component(id: ID!): Component
  user(id: ID!): User
  agentExecution(id: ID!): AgentExecution
  
  # 목록 조회
  projects(
    options: QueryOptions
    status: ProjectStatus
    ownerId: ID
  ): ProjectConnection!
  
  components(
    projectId: ID!
    options: QueryOptions
    type: ComponentType
  ): ComponentConnection!
  
  agentExecutions(
    projectId: ID
    agentType: AgentType
    status: ExecutionStatus
    options: QueryOptions
  ): AgentExecutionConnection!
  
  # 검색
  search(
    query: String!
    types: [String!]
    limit: Int = 10
  ): [SearchResult!]!
  
  # 통계
  projectStatistics(projectId: ID!): ProjectStatistics!
  userStatistics(userId: ID!): UserStatistics!
  systemStatistics: SystemStatistics!
  
  # 현재 사용자
  me: User
  myProjects(options: QueryOptions): ProjectConnection!
  
  # 컴포넌트 라이브러리
  componentLibrary(
    category: String
    framework: String
    options: QueryOptions
  ): ComponentConnection!
  
  # 에이전트 정보
  availableAgents: [AgentInfo!]!
  agentStatus(agentType: AgentType!): AgentStatus!
}

type Mutation {
  # 프로젝트 관리
  createProject(input: CreateProjectInput!): ProjectPayload!
  updateProject(id: ID!, input: UpdateProjectInput!): ProjectPayload!
  deleteProject(id: ID!): DeletePayload!
  archiveProject(id: ID!): ProjectPayload!
  
  # 컴포넌트 관리
  createComponent(input: CreateComponentInput!): ComponentPayload!
  updateComponent(id: ID!, input: UpdateComponentInput!): ComponentPayload!
  deleteComponent(id: ID!): DeletePayload!
  duplicateComponent(id: ID!): ComponentPayload!
  
  # 에이전트 실행
  executeAgent(input: ExecuteAgentInput!): AgentExecutionPayload!
  cancelAgentExecution(id: ID!): AgentExecutionPayload!
  retryAgentExecution(id: ID!): AgentExecutionPayload!
  
  # 코드 생성
  generateCode(projectId: ID!, options: GenerateOptions): GenerateCodePayload!
  generateComponent(input: GenerateComponentInput!): ComponentPayload!
  optimizeStyles(componentId: ID!): OptimizeStylesPayload!
  
  # 배포
  deployProject(projectId: ID!, environment: String!): DeploymentPayload!
  rollbackDeployment(deploymentId: ID!): DeploymentPayload!
  
  # 사용자 관리
  updateProfile(input: UpdateProfileInput!): UserPayload!
  updatePreferences(input: UpdatePreferencesInput!): UserPayload!
  
  # 협업
  shareProject(projectId: ID!, userId: ID!, role: String!): SharePayload!
  removeCollaborator(projectId: ID!, userId: ID!): MutationResponse!
  
  # 버전 관리
  createVersion(projectId: ID!, tag: String!): VersionPayload!
  restoreVersion(versionId: ID!): ProjectPayload!
}

# Input 타입들
input CreateProjectInput {
  name: String!
  description: String
  framework: String!
  template: String
  settings: ProjectSettingsInput
}

input UpdateProjectInput {
  name: String
  description: String
  status: ProjectStatus
  settings: ProjectSettingsInput
}

input CreateComponentInput {
  projectId: ID!
  name: String!
  type: ComponentType!
  category: String
  parentId: ID
  code: ComponentCode
  styles: String
}

input UpdateComponentInput {
  name: String
  category: String
  code: ComponentCode
  styles: String
  props: [PropDefinitionInput!]
}

input ExecuteAgentInput {
  projectId: ID!
  agentType: AgentType!
  input: JSON!
  options: AgentOptions
}

input AgentOptions {
  timeout: Int
  priority: Int
  parallel: Boolean
}

# Payload 타입들
type ProjectPayload {
  project: Project
  success: Boolean!
  message: String
  errors: [ValidationError!]
}

type ComponentPayload {
  component: Component
  success: Boolean!
  message: String
  errors: [ValidationError!]
}

type AgentExecutionPayload {
  execution: AgentExecution
  success: Boolean!
  message: String
  errors: [ValidationError!]
}

type GenerateCodePayload {
  code: String!
  files: [GeneratedFile!]!
  success: Boolean!
  message: String
}

type GeneratedFile {
  path: String!
  content: String!
  type: String!
}
```

```typescript
// backend/src/graphql/schema/schema-builder.ts
import { makeExecutableSchema } from '@graphql-tools/schema';
import { mergeTypeDefs, mergeResolvers } from '@graphql-tools/merge';

export class SchemaBuilder {
  private typeDefs: string[] = [];
  private resolvers: any[] = [];
  
  constructor() {
    this.loadTypeDefs();
    this.loadResolvers();
  }
  
  private loadTypeDefs(): void {
    // 기본 타입 정의
    this.typeDefs.push(ScalarDefinitions);
    this.typeDefs.push(EnumDefinitions);
    this.typeDefs.push(InterfaceDefinitions);
    this.typeDefs.push(TypeDefinitions);
    this.typeDefs.push(QueryDefinitions);
    this.typeDefs.push(MutationDefinitions);
    this.typeDefs.push(SubscriptionDefinitions);
  }
  
  private loadResolvers(): void {
    // 리졸버 로드
    this.resolvers.push(ScalarResolvers);
    this.resolvers.push(QueryResolvers);
    this.resolvers.push(MutationResolvers);
    this.resolvers.push(SubscriptionResolvers);
    this.resolvers.push(TypeResolvers);
  }
  
  build(): GraphQLSchema {
    const mergedTypeDefs = mergeTypeDefs(this.typeDefs);
    const mergedResolvers = mergeResolvers(this.resolvers);
    
    return makeExecutableSchema({
      typeDefs: mergedTypeDefs,
      resolvers: mergedResolvers,
      inheritResolversFromInterfaces: true
    });
  }
  
  addPlugin(plugin: GraphQLPlugin): void {
    if (plugin.typeDefs) {
      this.typeDefs.push(plugin.typeDefs);
    }
    if (plugin.resolvers) {
      this.resolvers.push(plugin.resolvers);
    }
  }
}
```

**검증 기준**:
- [ ] 완전한 Query 정의
- [ ] 완전한 Mutation 정의
- [ ] Input/Payload 타입
- [ ] 스키마 조합 로직

#### SubTask 6.11.4: 스키마 유효성 검증 및 최적화

**담당자**: 백엔드 아키텍트  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/graphql/schema/validator.py
from graphql import validate, parse, build_schema
from typing import List, Dict, Any

class SchemaValidator:
    """GraphQL 스키마 검증기"""
    
    def __init__(self):
        self.rules = self.load_validation_rules()
        self.warnings = []
        self.errors = []
    
    def validate_schema(self, schema_string: str) -> ValidationResult:
        """스키마 유효성 검증"""
        
        try:
            # 스키마 파싱
            schema = build_schema(schema_string)
            
            # 구조적 검증
            self.validate_structure(schema)
            
            # 네이밍 규칙 검증
            self.validate_naming_conventions(schema)
            
            # 순환 참조 검증
            self.validate_circular_references(schema)
            
            # 복잡도 검증
            self.validate_complexity(schema)
            
            # 보안 검증
            self.validate_security(schema)
            
            return ValidationResult(
                valid=len(self.errors) == 0,
                errors=self.errors,
                warnings=self.warnings
            )
            
        except Exception as e:
            self.errors.append(f"Schema parsing error: {str(e)}")
            return ValidationResult(valid=False, errors=self.errors)
    
    def validate_structure(self, schema):
        """구조적 유효성 검증"""
        
        # Query 타입 존재 확인
        if not schema.query_type:
            self.errors.append("Query type is required")
        
        # 모든 타입의 필드 검증
        for type_name, type_def in schema.type_map.items():
            if type_name.startswith("__"):
                continue
                
            # 빈 타입 체크
            if hasattr(type_def, 'fields') and not type_def.fields:
                self.warnings.append(f"Type {type_name} has no fields")
            
            # 필드 타입 검증
            if hasattr(type_def, 'fields'):
                for field_name, field in type_def.fields.items():
                    self.validate_field(type_name, field_name, field)
    
    def validate_naming_conventions(self, schema):
        """네이밍 규칙 검증"""
        
        for type_name in schema.type_map:
            if type_name.startswith("__"):
                continue
            
            # 타입 이름은 PascalCase
            if not self.is_pascal_case(type_name):
                self.warnings.append(
                    f"Type {type_name} should be in PascalCase"
                )
            
            type_def = schema.type_map[type_name]
            
            # 필드 이름은 camelCase
            if hasattr(type_def, 'fields'):
                for field_name in type_def.fields:
                    if not self.is_camel_case(field_name):
                        self.warnings.append(
                            f"Field {type_name}.{field_name} should be in camelCase"
                        )
    
    def validate_circular_references(self, schema):
        """순환 참조 검증"""
        
        visited = set()
        rec_stack = set()
        
        def has_cycle(type_name: str) -> bool:
            visited.add(type_name)
            rec_stack.add(type_name)
            
            type_def = schema.type_map.get(type_name)
            if not type_def or not hasattr(type_def, 'fields'):
                rec_stack.remove(type_name)
                return False
            
            for field_name, field in type_def.fields.items():
                field_type = self.get_base_type(field.type)
                
                if field_type not in visited:
                    if has_cycle(field_type):
                        return True
                elif field_type in rec_stack:
                    self.warnings.append(
                        f"Circular reference detected: {type_name} -> {field_type}"
                    )
            
            rec_stack.remove(type_name)
            return False
        
        for type_name in schema.type_map:
            if type_name not in visited and not type_name.startswith("__"):
                has_cycle(type_name)

class SchemaOptimizer:
    """스키마 최적화"""
    
    def optimize(self, schema: str) -> str:
        """스키마 최적화"""
        
        # 중복 타입 제거
        schema = self.remove_duplicate_types(schema)
        
        # 사용하지 않는 타입 제거
        schema = self.remove_unused_types(schema)
        
        # 필드 최적화
        schema = self.optimize_fields(schema)
        
        # 쿼리 복잡도 최적화
        schema = self.optimize_query_complexity(schema)
        
        return schema
    
    def analyze_complexity(self, query: str, schema) -> ComplexityAnalysis:
        """쿼리 복잡도 분석"""
        
        ast = parse(query)
        
        complexity = 0
        depth = 0
        
        def visit_field(node, current_depth=0):
            nonlocal complexity, depth
            
            complexity += self.calculate_field_complexity(node)
            depth = max(depth, current_depth)
            
            if hasattr(node, 'selection_set') and node.selection_set:
                for selection in node.selection_set.selections:
                    visit_field(selection, current_depth + 1)
        
        for definition in ast.definitions:
            if hasattr(definition, 'selection_set'):
                for selection in definition.selection_set.selections:
                    visit_field(selection)
        
        return ComplexityAnalysis(
            complexity=complexity,
            depth=depth,
            exceeds_limit=complexity > 1000 or depth > 10
        )

class DeprecationManager:
    """스키마 deprecation 관리"""
    
    def mark_deprecated(
        self,
        schema,
        type_name: str,
        field_name: str,
        reason: str,
        removal_date: str
    ):
        """필드 deprecation 마킹"""
        
        directive = f'@deprecated(reason: "{reason}", removalDate: "{removal_date}")'
        
        # 스키마에 deprecation 디렉티브 추가
        return self.add_directive(schema, type_name, field_name, directive)
    
    def get_deprecated_fields(self, schema) -> List[DeprecatedField]:
        """Deprecated 필드 목록 조회"""
        
        deprecated = []
        
        for type_name, type_def in schema.type_map.items():
            if hasattr(type_def, 'fields'):
                for field_name, field in type_def.fields.items():
                    if field.is_deprecated:
                        deprecated.append(DeprecatedField(
                            type=type_name,
                            field=field_name,
                            reason=field.deprecation_reason
                        ))
        
        return deprecated
```

**검증 기준**:
- [ ] 스키마 구조 검증
- [ ] 네이밍 규칙 검증
- [ ] 순환 참조 감지
- [ ] 복잡도 분석

---

### Task 6.12: Resolver 구현

#### SubTask 6.12.1: 쿼리 리졸버 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```typescript
// backend/src/graphql/resolvers/query-resolvers.ts
import { IResolvers } from '@graphql-tools/utils';
import { Context } from '../context';

export const QueryResolvers: IResolvers = {
  Query: {
    // 단일 조회 리졸버
    project: async (parent, { id }, context: Context) => {
      // 권한 확인
      await context.authorize('project:read', id);
      
      // 데이터 로드
      const project = await context.dataSources.projectAPI.getProject(id);
      
      if (!project) {
        throw new NotFoundError(`Project ${id} not found`);
      }
      
      return project;
    },
    
    component: async (parent, { id }, context: Context) => {
      const component = await context.dataSources.componentAPI.getComponent(id);
      
      // 프로젝트 권한 확인
      await context.authorize('project:read', component.projectId);
      
      return component;
    },
    
    // 목록 조회 리졸버
    projects: async (parent, args, context: Context) => {
      const { options, status, ownerId } = args;
      
      // 필터 구성
      const filters: any = {};
      if (status) filters.status = status;
      if (ownerId) filters.ownerId = ownerId;
      
      // 페이지네이션 처리
      const connection = await context.dataSources.projectAPI.getProjects({
        filters,
        ...options
      });
      
      return connection;
    },
    
    components: async (parent, { projectId, options, type }, context: Context) => {
      // 프로젝트 권한 확인
      await context.authorize('project:read', projectId);
      
      const filters: any = { projectId };
      if (type) filters.type = type;
      
      return await context.dataSources.componentAPI.getComponents({
        filters,
        ...options
      });
    },
    
    // 검색 리졸버
    search: async (parent, { query, types, limit }, context: Context) => {
      const searchService = context.services.searchService;
      
      const results = await searchService.search({
        query,
        types: types || ['Project', 'Component', 'User'],
        limit,
        userId: context.user.id
      });
      
      // Union 타입 리졸버를 위한 __typename 추가
      return results.map(result => ({
        ...result,
        __typename: result.type
      }));
    },
    
    // 통계 리졸버
    projectStatistics: async (parent, { projectId }, context: Context) => {
      await context.authorize('project:read', projectId);
      
      const stats = await context.services.analyticsService.getProjectStats(projectId);
      
      return {
        componentCount: stats.components,
        linesOfCode: stats.loc,
        lastBuildTime: stats.lastBuild,
        buildStatus: stats.buildStatus,
        testCoverage: stats.coverage
      };
    },
    
    // 현재 사용자
    me: async (parent, args, context: Context) => {
      if (!context.user) {
        return null;
      }
      
      return await context.dataSources.userAPI.getUser(context.user.id);
    },
    
    myProjects: async (parent, { options }, context: Context) => {
      if (!context.user) {
        throw new AuthenticationError('Not authenticated');
      }
      
      return await context.dataSources.projectAPI.getProjects({
        filters: { ownerId: context.user.id },
        ...options
      });
    },
    
    // 컴포넌트 라이브러리
    componentLibrary: async (parent, { category, framework, options }, context: Context) => {
      const filters: any = { isLibrary: true };
      if (category) filters.category = category;
      if (framework) filters.framework = framework;
      
      return await context.dataSources.componentAPI.getLibraryComponents({
        filters,
        ...options
      });
    },
    
    // 에이전트 정보
    availableAgents: async (parent, args, context: Context) => {
      const agents = await context.services.agentService.getAvailableAgents();
      
      return agents.map(agent => ({
        type: agent.type,
        name: agent.name,
        description: agent.description,
        status: agent.status,
        capabilities: agent.capabilities
      }));
    },
    
    agentStatus: async (parent, { agentType }, context: Context) => {
      const status = await context.services.agentService.getAgentStatus(agentType);
      
      return {
        type: agentType,
        available: status.available,
        queueLength: status.queueLength,
        averageExecutionTime: status.avgTime,
        successRate: status.successRate
      };
    }
  }
};

// 효율적인 배치 처리를 위한 DataLoader 사용
export class QueryOptimizer {
  constructor(private context: Context) {}
  
  createLoaders() {
    return {
      projectLoader: new DataLoader(async (ids: string[]) => {
        const projects = await this.context.dataSources.projectAPI.getProjectsByIds(ids);
        return ids.map(id => projects.find(p => p.id === id));
      }),
      
      componentLoader: new DataLoader(async (ids: string[]) => {
        const components = await this.context.dataSources.componentAPI.getComponentsByIds(ids);
        return ids.map(id => components.find(c => c.id === id));
      }),
      
      userLoader: new DataLoader(async (ids: string[]) => {
        const users = await this.context.dataSources.userAPI.getUsersByIds(ids);
        return ids.map(id => users.find(u => u.id === id));
      })
    };
  }
}
```

**검증 기준**:
- [ ] 모든 Query 리졸버 구현
- [ ] 권한 확인 로직
- [ ] DataLoader 통합
- [ ] 에러 처리

#### SubTask 6.12.2: 뮤테이션 리졸버 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/graphql/resolvers/mutation_resolvers.py
from typing import Dict, Any
from graphql import GraphQLError

class MutationResolvers:
    """뮤테이션 리졸버"""
    
    @staticmethod
    async def create_project(parent, args, context):
        """프로젝트 생성"""
        
        input_data = args['input']
        
        # 권한 확인
        if not context.user:
            raise GraphQLError("Authentication required")
        
        # 입력 검증
        validation_errors = await validate_project_input(input_data)
        if validation_errors:
            return {
                'project': None,
                'success': False,
                'errors': validation_errors
            }
        
        try:
            # 프로젝트 생성
            project = await context.services.project_service.create_project({
                **input_data,
                'owner_id': context.user.id
            })
            
            # 초기 설정 생성
            if input_data.get('settings'):
                await context.services.project_service.update_settings(
                    project.id,
                    input_data['settings']
                )
            
            # 템플릿 적용
            if input_data.get('template'):
                await context.services.template_service.apply_template(
                    project.id,
                    input_data['template']
                )
            
            # 이벤트 발생
            await context.pubsub.publish('project_created', {
                'projectCreated': project
            })
            
            return {
                'project': project,
                'success': True,
                'message': 'Project created successfully'
            }
            
        except Exception as e:
            return {
                'project': None,
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    async def execute_agent(parent, args, context):
        """에이전트 실행"""
        
        input_data = args['input']
        
        # 프로젝트 권한 확인
        await context.authorize('project:write', input_data['project_id'])
        
        # 에이전트 실행 생성
        execution = await context.services.agent_service.create_execution({
            'project_id': input_data['project_id'],
            'agent_type': input_data['agent_type'],
            'input': input_data['input'],
            'triggered_by': context.user.id,
            'options': input_data.get('options', {})
        })
        
        # 비동기 실행 시작
        asyncio.create_task(
            self._execute_agent_async(execution.id, context)
        )
        
        # 실시간 업데이트를 위한 구독 트리거
        await context.pubsub.publish(f'agent_execution_{execution.id}', {
            'agentExecutionUpdated': execution
        })
        
        return {
            'execution': execution,
            'success': True,
            'message': 'Agent execution started'
        }
    
    @staticmethod
    async def _execute_agent_async(execution_id: str, context):
        """비동기 에이전트 실행"""
        
        try:
            # 에이전트 실행
            result = await context.services.agent_service.execute(execution_id)
            
            # 상태 업데이트
            await context.services.agent_service.update_execution(
                execution_id,
                {
                    'status': 'completed',
                    'output': result,
                    'completed_at': datetime.now()
                }
            )
            
        except Exception as e:
            # 실패 처리
            await context.services.agent_service.update_execution(
                execution_id,
                {
                    'status': 'failed',
                    'error': {
                        'code': 'EXECUTION_ERROR',
                        'message': str(e)
                    }
                }
            )
        
        finally:
            # 완료 이벤트 발생
            execution = await context.services.agent_service.get_execution(execution_id)
            await context.pubsub.publish(f'agent_execution_{execution_id}', {
                'agentExecutionUpdated': execution
            })
    
    @staticmethod
    async def generate_code(parent, args, context):
        """코드 생성"""
        
        project_id = args['project_id']
        options = args.get('options', {})
        
        # 권한 확인
        await context.authorize('project:write', project_id)
        
        # 프로젝트 로드
        project = await context.services.project_service.get_project(project_id)
        
        # 코드 생성 파이프라인 실행
        pipeline = CodeGenerationPipeline(project, options)
        
        # 각 에이전트 순차 실행
        agents = [
            'requirements_analyzer',
            'ui_generator',
            'component_designer',
            'api_integrator',
            'state_manager',
            'route_configurator',
            'style_optimizer',
            'test_generator',
            'deployment_preparer'
        ]
        
        generated_files = []
        
        for agent_type in agents:
            # 에이전트 실행
            result = await context.services.agent_service.execute_sync(
                project_id,
                agent_type,
                pipeline.get_input_for_agent(agent_type)
            )
            
            # 결과 처리
            pipeline.process_agent_result(agent_type, result)
            
            # 파일 생성
            files = pipeline.generate_files_from_result(agent_type, result)
            generated_files.extend(files)
        
        # 최종 코드 조합
        final_code = pipeline.combine_results()
        
        return {
            'code': final_code,
            'files': generated_files,
            'success': True,
            'message': f'Generated {len(generated_files)} files'
        }
    
    @staticmethod
    async def deploy_project(parent, args, context):
        """프로젝트 배포"""
        
        project_id = args['project_id']
        environment = args['environment']
        
        # 권한 확인
        await context.authorize('project:deploy', project_id)
        
        # 배포 전 검증
        validation = await context.services.deployment_service.validate_deployment(
            project_id,
            environment
        )
        
        if not validation['valid']:
            return {
                'deployment': None,
                'success': False,
                'message': 'Deployment validation failed',
                'errors': validation['errors']
            }
        
        # 배포 생성
        deployment = await context.services.deployment_service.create_deployment({
            'project_id': project_id,
            'environment': environment,
            'initiated_by': context.user.id
        })
        
        # 비동기 배포 시작
        asyncio.create_task(
            context.services.deployment_service.execute_deployment(deployment.id)
        )
        
        return {
            'deployment': deployment,
            'success': True,
            'message': 'Deployment initiated'
        }
```

**검증 기준**:
- [ ] 모든 Mutation 리졸버
- [ ] 트랜잭션 처리
- [ ] 비동기 작업 처리
- [ ] 에러 핸들링

#### SubTask 6.12.3: 필드 리졸버 및 관계 처리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/graphql/resolvers/field-resolvers.ts
export const FieldResolvers = {
  Project: {
    owner: async (project, args, context) => {
      // DataLoader를 사용한 배치 로딩
      return context.loaders.userLoader.load(project.ownerId);
    },
    
    components: async (project, { limit, offset }, context) => {
      return await context.dataSources.componentAPI.getComponentsByProject(
        project.id,
        { limit, offset }
      );
    },
    
    agents: async (project, args, context) => {
      return await context.dataSources.agentAPI.getExecutionsByProject(project.id);
    },
    
    settings: async (project, args, context) => {
      // 캐싱된 설정 반환
      const cacheKey = `project_settings_${project.id}`;
      const cached = await context.cache.get(cacheKey);
      
      if (cached) {
        return cached;
      }
      
      const settings = await context.dataSources.projectAPI.getSettings(project.id);
      await context.cache.set(cacheKey, settings, 300); // 5분 캐싱
      
      return settings;
    },
    
    statistics: async (project, args, context) => {
      // 통계는 실시간 계산
      return await context.services.analyticsService.calculateProjectStats(project.id);
    }
  },
  
  Component: {
    project: async (component, args, context) => {
      return context.loaders.projectLoader.load(component.projectId);
    },
    
    parent: async (component, args, context) => {
      if (!component.parentId) return null;
      return context.loaders.componentLoader.load(component.parentId);
    },
    
    children: async (component, args, context) => {
      return await context.dataSources.componentAPI.getChildComponents(component.id);
    },
    
    dependencies: async (component, args, context) => {
      // 의존성 분석
      const deps = await context.services.dependencyService.analyze(component.code);
      return deps.map(dep => ({
        name: dep.name,
        version: dep.version,
        type: dep.type
      }));
    }
  },
  
  AgentExecution: {
    project: async (execution, args, context) => {
      return context.loaders.projectLoader.load(execution.projectId);
    },
    
    triggeredBy: async (execution, args, context) => {
      return context.loaders.userLoader.load(execution.triggeredById);
    },
    
    logs: async (execution, { level, limit }, context) => {
      const filters: any = {};
      if (level) filters.level = level;
      
      return await context.dataSources.logsAPI.getExecutionLogs(
        execution.id,
        { filters, limit }
      );
    },
    
    duration: (execution) => {
      if (!execution.startedAt || !execution.completedAt) {
        return null;
      }
      return execution.completedAt.getTime() - execution.startedAt.getTime();
    }
  },
  
  User: {
    projects: async (user, { limit, offset }, context) => {
      // 사용자의 프로젝트만 조회 가능
      if (context.user.id !== user.id && !context.user.isAdmin) {
        throw new ForbiddenError('Cannot access other user projects');
      }
      
      return await context.dataSources.projectAPI.getUserProjects(
        user.id,
        { limit, offset }
      );
    },
    
    executions: async (user, args, context) => {
      if (context.user.id !== user.id && !context.user.isAdmin) {
        return [];
      }
      
      return await context.dataSources.agentAPI.getUserExecutions(user.id);
    },
    
    preferences: async (user, args, context) => {
      // 자신의 설정만 조회 가능
      if (context.user.id !== user.id) {
        return null;
      }
      
      return await context.dataSources.userAPI.getPreferences(user.id);
    }
  },
  
  // Union 타입 리졸버
  SearchResult: {
    __resolveType(obj) {
      if (obj.framework) return 'Project';
      if (obj.code) return 'Component';
      if (obj.email) return 'User';
      return null;
    }
  },
  
  // Interface 리졸버
  Node: {
    __resolveType(obj) {
      return obj.__typename;
    }
  }
};

// 관계 최적화
export class RelationshipOptimizer {
  optimizeQuery(info: GraphQLResolveInfo): QueryPlan {
    const fields = this.parseSelectionSet(info);
    
    // 필요한 관계 파악
    const requiredJoins = this.identifyRequiredJoins(fields);
    
    // 쿼리 계획 생성
    return {
      joins: requiredJoins,
      projections: this.getProjections(fields),
      batchKeys: this.getBatchKeys(fields)
    };
  }
  
  private parseSelectionSet(info: GraphQLResolveInfo): FieldNode[] {
    const selections = info.fieldNodes[0].selectionSet?.selections || [];
    return this.flattenSelections(selections);
  }
  
  private identifyRequiredJoins(fields: FieldNode[]): string[] {
    const joins = new Set<string>();
    
    for (const field of fields) {
      if (this.isRelationField(field)) {
        joins.add(field.name.value);
      }
    }
    
    return Array.from(joins);
  }
}
```

**검증 기준**:
- [ ] 모든 타입 필드 리졸버
- [ ] DataLoader 활용
- [ ] 캐싱 전략
- [ ] Union/Interface 리졸버

#### SubTask 6.12.4: DataLoader 및 배치 처리

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/graphql/resolvers/dataloaders.py
from aiodataloader import DataLoader
from typing import List, Dict, Any
import asyncio

class ProjectLoader(DataLoader):
    """프로젝트 DataLoader"""
    
    def __init__(self, project_service):
        super().__init__()
        self.project_service = project_service
    
    async def batch_load_fn(self, project_ids: List[str]) -> List[Any]:
        """배치 로드 함수"""
        
        # 한 번의 쿼리로 모든 프로젝트 조회
        projects = await self.project_service.get_projects_by_ids(project_ids)
        
        # ID 순서대로 정렬
        project_map = {p.id: p for p in projects}
        return [project_map.get(pid) for pid in project_ids]

class ComponentLoader(DataLoader):
    """컴포넌트 DataLoader"""
    
    def __init__(self, component_service):
        super().__init__()
        self.component_service = component_service
        self.max_batch_size = 100
    
    async def batch_load_fn(self, component_ids: List[str]) -> List[Any]:
        # 대량 요청 분할 처리
        if len(component_ids) > self.max_batch_size:
            return await self._load_in_chunks(component_ids)
        
        components = await self.component_service.get_components_by_ids(component_ids)
        component_map = {c.id: c for c in components}
        return [component_map.get(cid) for cid in component_ids]
    
    async def _load_in_chunks(self, ids: List[str]) -> List[Any]:
        """청크 단위 로드"""
        
        chunks = [
            ids[i:i + self.max_batch_size]
            for i in range(0, len(ids), self.max_batch_size)
        ]
        
        results = await asyncio.gather(*[
            self.component_service.get_components_by_ids(chunk)
            for chunk in chunks
        ])
        
        # 결과 병합
        all_components = []
        for chunk_result in results:
            all_components.extend(chunk_result)
        
        component_map = {c.id: c for c in all_components}
        return [component_map.get(cid) for cid in ids]

class RelationshipLoader(DataLoader):
    """관계 DataLoader"""
    
    def __init__(self, relationship_service):
        super().__init__()
        self.relationship_service = relationship_service
        self.cache_enabled = True
    
    async def batch_load_fn(self, keys: List[tuple]) -> List[Any]:
        """관계 배치 로드
        
        keys: [(parent_type, parent_id, relation_name), ...]
        """
        
        # 타입별로 그룹화
        grouped = {}
        for parent_type, parent_id, relation in keys:
            key = (parent_type, relation)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(parent_id)
        
        # 각 그룹별로 쿼리
        results = {}
        for (parent_type, relation), parent_ids in grouped.items():
            relation_data = await self.relationship_service.get_relations(
                parent_type,
                parent_ids,
                relation
            )
            
            for parent_id, data in relation_data.items():
                results[(parent_type, parent_id, relation)] = data
        
        # 원래 순서대로 반환
        return [results.get(key, None) for key in keys]

class DataLoaderRegistry:
    """DataLoader 레지스트리"""
    
    def __init__(self, services):
        self.services = services
        self.loaders = {}
        self.initialize_loaders()
    
    def initialize_loaders(self):
        """로더 초기화"""
        
        self.loaders['project'] = ProjectLoader(
            self.services.project_service
        )
        
        self.loaders['component'] = ComponentLoader(
            self.services.component_service
        )
        
        self.loaders['user'] = UserLoader(
            self.services.user_service
        )
        
        self.loaders['relationship'] = RelationshipLoader(
            self.services.relationship_service
        )
        
        # 캐싱 로더
        self.loaders['cached_stats'] = CachedStatsLoader(
            self.services.analytics_service
        )
    
    def get_loader(self, name: str) -> DataLoader:
        """로더 조회"""
        
        if name not in self.loaders:
            raise ValueError(f"Loader {name} not found")
        
        return self.loaders[name]
    
    def create_context_loaders(self) -> Dict[str, DataLoader]:
        """컨텍스트용 로더 생성"""
        
        # 각 요청마다 새로운 로더 인스턴스 생성
        return {
            'projectLoader': ProjectLoader(self.services.project_service),
            'componentLoader': ComponentLoader(self.services.component_service),
            'userLoader': UserLoader(self.services.user_service),
            'relationshipLoader': RelationshipLoader(self.services.relationship_service)
        }

class BatchProcessor:
    """배치 처리 최적화"""
    
    def __init__(self):
        self.batch_size = 50
        self.batch_delay = 10  # ms
    
    async def process_batch(
        self,
        items: List[Any],
        processor: callable
    ) -> List[Any]:
        """배치 처리"""
        
        # 지연 시간 대기 (더 많은 요청 수집)
        await asyncio.sleep(self.batch_delay / 1000)
        
        # 배치 실행
        return await processor(items)
    
    def optimize_query(self, query: str, batch_size: int) -> str:
        """쿼리 최적화"""
        
        # IN 절 사용
        if batch_size > 1:
            return query.replace('= ?', 'IN (?)')
        
        return query
```

**검증 기준**:
- [ ] DataLoader 구현
- [ ] 배치 처리 최적화
- [ ] 캐싱 통합
- [ ] N+1 문제 해결

---

### Task 6.13: Subscription 및 실시간 업데이트

#### SubTask 6.13.1: Subscription 스키마 정의

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```graphql
# backend/src/graphql/schema/subscriptions.graphql

type Subscription {
  # 프로젝트 실시간 업데이트
  projectUpdated(projectId: ID!): Project!
  projectDeleted(projectId: ID!): ID!
  
  # 컴포넌트 변경 알림
  componentChanged(projectId: ID!): ComponentChangeEvent!
  
  # 에이전트 실행 상태
  agentExecutionUpdated(executionId: ID!): AgentExecution!
  agentExecutionLog(executionId: ID!): ExecutionLog!
  
  # 코드 생성 진행 상황
  codeGenerationProgress(projectId: ID!): GenerationProgress!
  
  # 배포 상태
  deploymentStatusChanged(deploymentId: ID!): DeploymentStatus!
  
  # 협업 이벤트
  collaboratorJoined(projectId: ID!): CollaboratorEvent!
  collaboratorLeft(projectId: ID!): CollaboratorEvent!
  
  # 실시간 코드 편집
  codeEdited(componentId: ID!): CodeEditEvent!
  cursorMoved(componentId: ID!): CursorEvent!
  
  # 시스템 알림
  systemNotification(userId: ID!): SystemNotification!
  
  # 성능 메트릭
  performanceMetrics(projectId: ID!): PerformanceMetric!
}

# 이벤트 타입들
type ComponentChangeEvent {
  type: ChangeType!
  component: Component!
  changedBy: User!
  timestamp: DateTime!
  changes: [FieldChange!]!
}

type FieldChange {
  field: String!
  oldValue: JSON
  newValue: JSON
}

enum ChangeType {
  CREATED
  UPDATED
  DELETED
  MOVED
  RENAMED
}

type GenerationProgress {
  projectId: ID!
  currentAgent: AgentType!
  progress: Float!
  message: String!
  estimatedTimeRemaining: Int
  completedAgents: [AgentType!]!
  pendingAgents: [AgentType!]!
}

type DeploymentStatus {
  deploymentId: ID!
  status: String!
  stage: String!
  progress: Float!
  logs: [String!]!
  error: String
  url: String
}

type CollaboratorEvent {
  projectId: ID!
  user: User!
  action: String!
  timestamp: DateTime!
}

type CodeEditEvent {
  componentId: ID!
  userId: ID!
  changes: [CodeChange!]!
  timestamp: DateTime!
}

type CodeChange {
  line: Int!
  column: Int!
  action: String! # insert, delete, replace
  text: String
}

type CursorEvent {
  componentId: ID!
  userId: ID!
  line: Int!
  column: Int!
  selection: Selection
}

type Selection {
  startLine: Int!
  startColumn: Int!
  endLine: Int!
  endColumn: Int!
}

type SystemNotification {
  id: ID!
  type: NotificationType!
  title: String!
  message: String!
  severity: NotificationSeverity!
  timestamp: DateTime!
  data: JSON
}

enum NotificationType {
  INFO
  WARNING
  ERROR
  SUCCESS
  AGENT_COMPLETED
  DEPLOYMENT_READY
  COLLABORATION_REQUEST
}

enum NotificationSeverity {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

type PerformanceMetric {
  projectId: ID!
  timestamp: DateTime!
  buildTime: Float
  bundleSize: Int
  memoryUsage: Float
  cpuUsage: Float
  responseTime: Float
}
```

```typescript
// backend/src/graphql/subscriptions/subscription-manager.ts
export class SubscriptionManager {
  private pubsub: PubSub;
  private connections: Map<string, Set<string>> = new Map();
  
  constructor() {
    this.pubsub = new PubSub();
    this.setupEventListeners();
  }
  
  private setupEventListeners(): void {
    // 도메인 이벤트 리스너
    eventBus.on('project:updated', (data) => {
      this.pubsub.publish(`project_${data.projectId}`, {
        projectUpdated: data.project
      });
    });
    
    eventBus.on('component:changed', (data) => {
      this.pubsub.publish(`component_changes_${data.projectId}`, {
        componentChanged: data
      });
    });
    
    eventBus.on('agent:execution:updated', (data) => {
      this.pubsub.publish(`agent_execution_${data.executionId}`, {
        agentExecutionUpdated: data.execution
      });
    });
  }
  
  async subscribe(
    topic: string,
    connectionId: string,
    filter?: any
  ): AsyncIterator {
    // 연결 추적
    if (!this.connections.has(connectionId)) {
      this.connections.set(connectionId, new Set());
    }
    this.connections.get(connectionId)!.add(topic);
    
    // 필터링된 구독
    if (filter) {
      return this.pubsub.asyncIterator(topic, {
        filter: (payload) => this.applyFilter(payload, filter)
      });
    }
    
    return this.pubsub.asyncIterator(topic);
  }
  
  private applyFilter(payload: any, filter: any): boolean {
    // 필터 로직 구현
    for (const [key, value] of Object.entries(filter)) {
      if (payload[key] !== value) {
        return false;
      }
    }
    return true;
  }
  
  unsubscribe(connectionId: string, topic?: string): void {
    if (topic) {
      this.connections.get(connectionId)?.delete(topic);
    } else {
      this.connections.delete(connectionId);
    }
  }
}
```

**검증 기준**:
- [ ] 완전한 Subscription 스키마
- [ ] 이벤트 타입 정의
- [ ] 구독 관리 시스템
- [ ] 필터링 지원

---

### Task 6.13: Subscription 및 실시간 업데이트 (계속)

#### SubTask 6.13.2: PubSub 시스템 구현

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/graphql/subscriptions/pubsub_system.py
import asyncio
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass
import redis.asyncio as redis

@dataclass
class Subscription:
    """구독 정보"""
    id: str
    topic: str
    filter: Optional[Dict] = None
    connection_id: str = None
    created_at: datetime = field(default_factory=datetime.now)

class PubSubSystem:
    """발행-구독 시스템"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.subscriptions: Dict[str, Set[Subscription]] = {}
        self.connections: Dict[str, Set[str]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        
        # Redis를 사용한 분산 PubSub
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
            self.redis_pubsub = self.redis_client.pubsub()
            self.use_redis = True
        else:
            self.use_redis = False
    
    async def publish(self, topic: str, payload: Any) -> None:
        """이벤트 발행"""
        
        event = {
            'topic': topic,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.use_redis:
            # Redis를 통한 분산 발행
            await self.redis_client.publish(
                topic,
                json.dumps(event, default=str)
            )
        else:
            # 로컬 발행
            await self.event_queue.put(event)
            await self._notify_subscribers(topic, payload)
    
    async def subscribe(
        self,
        topic: str,
        connection_id: str,
        filter_fn: Optional[callable] = None
    ) -> AsyncIterator:
        """토픽 구독"""
        
        subscription = Subscription(
            id=generate_id(),
            topic=topic,
            filter=filter_fn,
            connection_id=connection_id
        )
        
        # 구독 등록
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(subscription)
        
        # 연결별 구독 추적
        if connection_id not in self.connections:
            self.connections[connection_id] = set()
        self.connections[connection_id].add(subscription.id)
        
        # Redis 구독
        if self.use_redis:
            await self.redis_pubsub.subscribe(topic)
        
        # 비동기 이터레이터 반환
        return self._create_async_iterator(subscription)
    
    async def _create_async_iterator(
        self,
        subscription: Subscription
    ) -> AsyncIterator:
        """비동기 이터레이터 생성"""
        
        queue = asyncio.Queue()
        
        async def message_handler():
            while True:
                try:
                    if self.use_redis:
                        # Redis에서 메시지 수신
                        message = await self.redis_pubsub.get_message(
                            ignore_subscribe_messages=True,
                            timeout=1.0
                        )
                        
                        if message:
                            data = json.loads(message['data'])
                            if self._should_deliver(data['payload'], subscription):
                                await queue.put(data['payload'])
                    else:
                        # 로컬 큐에서 메시지 수신
                        event = await self.event_queue.get()
                        if event['topic'] == subscription.topic:
                            if self._should_deliver(event['payload'], subscription):
                                await queue.put(event['payload'])
                                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    await self.handle_error(e, subscription)
        
        # 백그라운드 태스크 시작
        task = asyncio.create_task(message_handler())
        
        try:
            while True:
                yield await queue.get()
        finally:
            task.cancel()
    
    def _should_deliver(
        self,
        payload: Any,
        subscription: Subscription
    ) -> bool:
        """메시지 전달 여부 결정"""
        
        if not subscription.filter:
            return True
        
        return subscription.filter(payload)
    
    async def unsubscribe(
        self,
        subscription_id: str,
        connection_id: str
    ) -> None:
        """구독 해제"""
        
        # 구독 찾기
        subscription = None
        for topic_subs in self.subscriptions.values():
            for sub in topic_subs:
                if sub.id == subscription_id:
                    subscription = sub
                    break
        
        if not subscription:
            return
        
        # 구독 제거
        self.subscriptions[subscription.topic].discard(subscription)
        
        # 연결 추적 제거
        if connection_id in self.connections:
            self.connections[connection_id].discard(subscription_id)
        
        # Redis 구독 해제
        if self.use_redis:
            # 해당 토픽의 다른 구독이 없으면 unsubscribe
            if not self.subscriptions.get(subscription.topic):
                await self.redis_pubsub.unsubscribe(subscription.topic)
    
    async def disconnect(self, connection_id: str) -> None:
        """연결 종료 시 모든 구독 해제"""
        
        if connection_id not in self.connections:
            return
        
        subscription_ids = self.connections[connection_id].copy()
        
        for sub_id in subscription_ids:
            await self.unsubscribe(sub_id, connection_id)
        
        del self.connections[connection_id]

class EventAggregator:
    """이벤트 집계기"""
    
    def __init__(self, pubsub: PubSubSystem):
        self.pubsub = pubsub
        self.buffers: Dict[str, List[Any]] = {}
        self.timers: Dict[str, asyncio.Task] = {}
        
    async def aggregate(
        self,
        topic: str,
        event: Any,
        window: float = 1.0,
        max_size: int = 100
    ) -> None:
        """이벤트 집계 및 배치 발행"""
        
        # 버퍼에 추가
        if topic not in self.buffers:
            self.buffers[topic] = []
        
        self.buffers[topic].append(event)
        
        # 크기 제한 확인
        if len(self.buffers[topic]) >= max_size:
            await self.flush(topic)
            return
        
        # 타이머 설정
        if topic not in self.timers or self.timers[topic].done():
            self.timers[topic] = asyncio.create_task(
                self._flush_after_delay(topic, window)
            )
    
    async def _flush_after_delay(self, topic: str, delay: float) -> None:
        """지연 후 플러시"""
        
        await asyncio.sleep(delay)
        await self.flush(topic)
    
    async def flush(self, topic: str) -> None:
        """버퍼 플러시"""
        
        if topic not in self.buffers or not self.buffers[topic]:
            return
        
        # 배치 이벤트 발행
        batch = self.buffers[topic].copy()
        self.buffers[topic].clear()
        
        await self.pubsub.publish(topic, {
            'type': 'batch',
            'events': batch,
            'count': len(batch)
        })
        
        # 타이머 취소
        if topic in self.timers:
            self.timers[topic].cancel()
            del self.timers[topic]

class SubscriptionResolvers:
    """Subscription 리졸버"""
    
    def __init__(self, pubsub: PubSubSystem):
        self.pubsub = pubsub
        self.aggregator = EventAggregator(pubsub)
    
    async def project_updated(self, parent, args, context, info):
        """프로젝트 업데이트 구독"""
        
        project_id = args['project_id']
        
        # 권한 확인
        await context.authorize('project:read', project_id)
        
        # 구독
        return self.pubsub.subscribe(
            f'project_{project_id}',
            context.connection_id
        )
    
    async def agent_execution_updated(self, parent, args, context, info):
        """에이전트 실행 상태 구독"""
        
        execution_id = args['execution_id']
        
        # 실행 정보 조회 및 권한 확인
        execution = await context.services.agent_service.get_execution(execution_id)
        await context.authorize('project:read', execution.project_id)
        
        return self.pubsub.subscribe(
            f'agent_execution_{execution_id}',
            context.connection_id
        )
    
    async def code_generation_progress(self, parent, args, context, info):
        """코드 생성 진행 상황 구독"""
        
        project_id = args['project_id']
        await context.authorize('project:read', project_id)
        
        # 집계된 이벤트 구독
        return self.pubsub.subscribe(
            f'generation_progress_{project_id}',
            context.connection_id,
            filter_fn=lambda payload: payload.get('type') == 'progress'
        )
```

**검증 기준**:
- [ ] PubSub 시스템 구현
- [ ] Redis 통합 (분산)
- [ ] 이벤트 집계
- [ ] 구독 관리

#### SubTask 6.13.3: 실시간 이벤트 필터링

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/graphql/subscriptions/event-filtering.ts
export interface EventFilter {
  field: string;
  operator: FilterOperator;
  value: any;
}

export class EventFilteringSystem {
  private filters: Map<string, EventFilter[]> = new Map();
  private compiledFilters: Map<string, CompiledFilter> = new Map();
  
  addFilter(subscriptionId: string, filter: EventFilter): void {
    if (!this.filters.has(subscriptionId)) {
      this.filters.set(subscriptionId, []);
    }
    
    this.filters.get(subscriptionId)!.push(filter);
    this.compileFilter(subscriptionId);
  }
  
  private compileFilter(subscriptionId: string): void {
    const filters = this.filters.get(subscriptionId);
    if (!filters) return;
    
    // 필터를 최적화된 함수로 컴파일
    const compiled = new CompiledFilter(filters);
    this.compiledFilters.set(subscriptionId, compiled);
  }
  
  shouldDeliver(subscriptionId: string, event: any): boolean {
    const compiled = this.compiledFilters.get(subscriptionId);
    if (!compiled) return true;
    
    return compiled.evaluate(event);
  }
}

class CompiledFilter {
  private filterFn: (event: any) => boolean;
  
  constructor(filters: EventFilter[]) {
    this.filterFn = this.compile(filters);
  }
  
  private compile(filters: EventFilter[]): (event: any) => boolean {
    // 필터를 JavaScript 함수로 컴파일
    const conditions: string[] = [];
    
    for (const filter of filters) {
      const condition = this.compileCondition(filter);
      conditions.push(condition);
    }
    
    const fnBody = `return ${conditions.join(' && ')};`;
    return new Function('event', fnBody) as (event: any) => boolean;
  }
  
  private compileCondition(filter: EventFilter): string {
    const field = `event.${filter.field}`;
    const value = JSON.stringify(filter.value);
    
    switch (filter.operator) {
      case FilterOperator.EQUALS:
        return `${field} === ${value}`;
      case FilterOperator.NOT_EQUALS:
        return `${field} !== ${value}`;
      case FilterOperator.GREATER_THAN:
        return `${field} > ${value}`;
      case FilterOperator.LESS_THAN:
        return `${field} < ${value}`;
      case FilterOperator.IN:
        return `${value}.includes(${field})`;
      case FilterOperator.CONTAINS:
        return `${field}.includes(${value})`;
      default:
        return 'true';
    }
  }
  
  evaluate(event: any): boolean {
    try {
      return this.filterFn(event);
    } catch (error) {
      console.error('Filter evaluation error:', error);
      return false;
    }
  }
}

// 권한 기반 필터링
export class PermissionBasedFilter {
  constructor(private authService: AuthService) {}
  
  async createFilter(userId: string, resourceType: string): Promise<EventFilter[]> {
    const permissions = await this.authService.getUserPermissions(userId);
    const filters: EventFilter[] = [];
    
    // 리소스 타입별 필터 생성
    switch (resourceType) {
      case 'Project':
        // 사용자가 접근 가능한 프로젝트만
        const projectIds = await this.authService.getAccessibleProjects(userId);
        filters.push({
          field: 'projectId',
          operator: FilterOperator.IN,
          value: projectIds
        });
        break;
        
      case 'Component':
        // 컴포넌트는 프로젝트 권한을 상속
        const componentProjectIds = await this.authService.getAccessibleProjects(userId);
        filters.push({
          field: 'project.id',
          operator: FilterOperator.IN,
          value: componentProjectIds
        });
        break;
    }
    
    return filters;
  }
}

// 이벤트 변환 및 필터링 파이프라인
export class EventPipeline {
  private transformers: Array<(event: any) => any> = [];
  private filters: Array<(event: any) => boolean> = [];
  
  addTransformer(transformer: (event: any) => any): void {
    this.transformers.push(transformer);
  }
  
  addFilter(filter: (event: any) => boolean): void {
    this.filters.push(filter);
  }
  
  async process(event: any): Promise<any | null> {
    // 변환 적용
    let transformed = event;
    for (const transformer of this.transformers) {
      transformed = await transformer(transformed);
    }
    
    // 필터 적용
    for (const filter of this.filters) {
      if (!await filter(transformed)) {
        return null; // 필터링됨
      }
    }
    
    return transformed;
  }
}

// 이벤트 샘플링
export class EventSampler {
  private sampleRates: Map<string, number> = new Map();
  private counters: Map<string, number> = new Map();
  
  setSampleRate(eventType: string, rate: number): void {
    this.sampleRates.set(eventType, rate);
  }
  
  shouldSample(eventType: string): boolean {
    const rate = this.sampleRates.get(eventType);
    if (!rate || rate >= 1) return true;
    if (rate <= 0) return false;
    
    // 카운터 기반 샘플링
    const counter = this.counters.get(eventType) || 0;
    this.counters.set(eventType, counter + 1);
    
    return (counter % Math.floor(1 / rate)) === 0;
  }
}

// 이벤트 윈도우 필터
export class WindowFilter {
  private windows: Map<string, TimeWindow> = new Map();
  
  createWindow(
    id: string,
    duration: number,
    maxEvents: number
  ): void {
    this.windows.set(id, new TimeWindow(duration, maxEvents));
  }
  
  shouldAccept(windowId: string, event: any): boolean {
    const window = this.windows.get(windowId);
    if (!window) return true;
    
    return window.accept(event);
  }
}

class TimeWindow {
  private events: Array<{ timestamp: number; event: any }> = [];
  
  constructor(
    private duration: number, // seconds
    private maxEvents: number
  ) {}
  
  accept(event: any): boolean {
    const now = Date.now();
    
    // 오래된 이벤트 제거
    this.events = this.events.filter(
      e => (now - e.timestamp) < this.duration * 1000
    );
    
    // 최대 이벤트 수 확인
    if (this.events.length >= this.maxEvents) {
      return false;
    }
    
    this.events.push({ timestamp: now, event });
    return true;
  }
}
```

**검증 기준**:
- [ ] 이벤트 필터링 시스템
- [ ] 권한 기반 필터
- [ ] 샘플링 지원
- [ ] 윈도우 기반 필터

#### SubTask 6.13.4: 연결 관리 및 확장성

**담당자**: 시스템 아키텍트  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/graphql/subscriptions/connection_manager.py
from typing import Dict, Set, Optional
import asyncio
from dataclasses import dataclass

@dataclass
class ConnectionInfo:
    """연결 정보"""
    id: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    connected_at: datetime
    last_ping: datetime
    subscriptions: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)

class ConnectionManager:
    """WebSocket 연결 관리"""
    
    def __init__(self):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.health_checker = ConnectionHealthChecker()
        self.rate_limiter = ConnectionRateLimiter()
        
    async def add_connection(
        self,
        connection_id: str,
        websocket,
        request_info: Dict
    ) -> ConnectionInfo:
        """연결 추가"""
        
        # Rate limiting
        if not await self.rate_limiter.check_limit(request_info['ip']):
            raise RateLimitExceededError("Too many connections")
        
        # 연결 정보 생성
        conn_info = ConnectionInfo(
            id=connection_id,
            user_id=request_info.get('user_id'),
            ip_address=request_info['ip'],
            user_agent=request_info.get('user_agent', ''),
            connected_at=datetime.now(),
            last_ping=datetime.now()
        )
        
        # 저장
        self.connections[connection_id] = conn_info
        
        # 사용자별 연결 추적
        if conn_info.user_id:
            if conn_info.user_id not in self.user_connections:
                self.user_connections[conn_info.user_id] = set()
            self.user_connections[conn_info.user_id].add(connection_id)
        
        # Health check 시작
        asyncio.create_task(
            self.health_checker.start_monitoring(connection_id, websocket)
        )
        
        return conn_info
    
    async def remove_connection(self, connection_id: str) -> None:
        """연결 제거"""
        
        if connection_id not in self.connections:
            return
        
        conn_info = self.connections[connection_id]
        
        # 사용자 연결 추적 제거
        if conn_info.user_id:
            self.user_connections[conn_info.user_id].discard(connection_id)
            if not self.user_connections[conn_info.user_id]:
                del self.user_connections[conn_info.user_id]
        
        # Health check 중지
        await self.health_checker.stop_monitoring(connection_id)
        
        # 연결 정보 제거
        del self.connections[connection_id]
        
        # 정리 이벤트 발생
        await self.emit_disconnection_event(conn_info)
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionInfo]:
        """연결 정보 조회"""
        return self.connections.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> List[ConnectionInfo]:
        """사용자의 모든 연결 조회"""
        
        connection_ids = self.user_connections.get(user_id, set())
        return [
            self.connections[cid]
            for cid in connection_ids
            if cid in self.connections
        ]
    
    async def broadcast_to_user(
        self,
        user_id: str,
        message: Any
    ) -> None:
        """사용자의 모든 연결에 브로드캐스트"""
        
        connections = self.get_user_connections(user_id)
        
        await asyncio.gather(*[
            self.send_to_connection(conn.id, message)
            for conn in connections
        ])
    
    def get_statistics(self) -> Dict:
        """연결 통계"""
        
        return {
            'total_connections': len(self.connections),
            'unique_users': len(self.user_connections),
            'connections_by_user': {
                user_id: len(conns)
                for user_id, conns in self.user_connections.items()
            },
            'average_connection_duration': self.calculate_avg_duration(),
            'peak_connections': self.get_peak_connections()
        }

class ConnectionHealthChecker:
    """연결 상태 체크"""
    
    def __init__(self):
        self.ping_interval = 30  # seconds
        self.pong_timeout = 10   # seconds
        self.monitors: Dict[str, asyncio.Task] = {}
    
    async def start_monitoring(
        self,
        connection_id: str,
        websocket
    ) -> None:
        """연결 모니터링 시작"""
        
        async def monitor():
            while True:
                try:
                    # Ping 전송
                    pong_waiter = await websocket.ping()
                    
                    # Pong 대기
                    await asyncio.wait_for(
                        pong_waiter,
                        timeout=self.pong_timeout
                    )
                    
                    # 상태 업데이트
                    await self.update_health_status(connection_id, True)
                    
                    await asyncio.sleep(self.ping_interval)
                    
                except asyncio.TimeoutError:
                    # Pong 타임아웃
                    await self.handle_unhealthy_connection(connection_id)
                    break
                    
                except Exception as e:
                    # 연결 오류
                    await self.handle_connection_error(connection_id, e)
                    break
        
        self.monitors[connection_id] = asyncio.create_task(monitor())
    
    async def stop_monitoring(self, connection_id: str) -> None:
        """모니터링 중지"""
        
        if connection_id in self.monitors:
            self.monitors[connection_id].cancel()
            del self.monitors[connection_id]

class ScalableSubscriptionManager:
    """확장 가능한 구독 관리"""
    
    def __init__(self, redis_cluster: RedisCluster):
        self.redis = redis_cluster
        self.local_cache = TTLCache(maxsize=10000, ttl=60)
        self.shard_manager = ShardManager()
    
    async def distribute_subscription(
        self,
        subscription_id: str,
        topic: str,
        connection_id: str
    ) -> str:
        """구독 분산"""
        
        # 샤드 결정
        shard = self.shard_manager.get_shard(topic)
        
        # Redis에 구독 정보 저장
        key = f"subscription:{shard}:{subscription_id}"
        value = {
            'topic': topic,
            'connection_id': connection_id,
            'shard': shard,
            'created_at': datetime.now().isoformat()
        }
        
        await self.redis.hset(key, mapping=value)
        
        # 로컬 캐시 업데이트
        self.local_cache[subscription_id] = value
        
        # 샤드별 구독 카운트 증가
        await self.redis.hincrby(f"shard:stats:{shard}", "subscriptions", 1)
        
        return shard
    
    async def rebalance_shards(self) -> None:
        """샤드 재균형"""
        
        # 각 샤드의 부하 측정
        shard_loads = await self.measure_shard_loads()
        
        # 불균형 감지
        if self.is_imbalanced(shard_loads):
            # 재균형 계획 수립
            plan = self.create_rebalancing_plan(shard_loads)
            
            # 구독 마이그레이션
            await self.migrate_subscriptions(plan)
            
            # 샤드 맵 업데이트
            await self.shard_manager.update_shard_map(plan)

class ConnectionRateLimiter:
    """연결 속도 제한"""
    
    def __init__(self):
        self.limits = {
            'connections_per_ip': 10,
            'connections_per_user': 5,
            'new_connections_per_minute': 20
        }
        self.counters = {}
    
    async def check_limit(self, identifier: str) -> bool:
        """제한 확인"""
        
        current = self.counters.get(identifier, 0)
        
        if current >= self.limits['connections_per_ip']:
            return False
        
        self.counters[identifier] = current + 1
        
        # 시간 기반 제한
        return await self.check_time_based_limit(identifier)
    
    async def check_time_based_limit(self, identifier: str) -> bool:
        """시간 기반 제한 확인"""
        
        key = f"rate_limit:{identifier}:{int(time.time() / 60)}"
        
        count = await redis_client.incr(key)
        
        if count == 1:
            await redis_client.expire(key, 60)
        
        return count <= self.limits['new_connections_per_minute']

class AutoScalingManager:
    """자동 스케일링 관리"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.scaler = K8sScaler()
        self.thresholds = {
            'cpu_high': 80,
            'cpu_low': 20,
            'memory_high': 85,
            'memory_low': 30,
            'connections_per_pod': 1000
        }
    
    async def monitor_and_scale(self) -> None:
        """모니터링 및 스케일링"""
        
        while True:
            metrics = await self.metrics.collect()
            
            # 스케일 아웃 필요 여부
            if self.should_scale_out(metrics):
                await self.scale_out()
            
            # 스케일 인 필요 여부
            elif self.should_scale_in(metrics):
                await self.scale_in()
            
            await asyncio.sleep(30)
    
    def should_scale_out(self, metrics: Dict) -> bool:
        """스케일 아웃 필요 여부"""
        
        return (
            metrics['cpu'] > self.thresholds['cpu_high'] or
            metrics['memory'] > self.thresholds['memory_high'] or
            metrics['connections_per_pod'] > self.thresholds['connections_per_pod']
        )
    
    async def scale_out(self) -> None:
        """스케일 아웃"""
        
        current_replicas = await self.scaler.get_replicas()
        new_replicas = min(current_replicas + 1, 10)  # 최대 10개
        
        await self.scaler.set_replicas(new_replicas)
        
        # 이벤트 로깅
        await self.log_scaling_event('scale_out', current_replicas, new_replicas)
```

**검증 기준**:
- [ ] 연결 관리 시스템
- [ ] Health Check
- [ ] 분산 구독 관리
- [ ] 자동 스케일링

---

### Task 6.14: WebSocket 서버 구현

#### SubTask 6.14.1: WebSocket 서버 초기화

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/websocket/server.ts
import { Server } from 'ws';
import { createServer } from 'http';
import { parse } from 'url';

export class WebSocketServer {
  private wss: Server;
  private httpServer: any;
  private connections: Map<string, WebSocket> = new Map();
  private handlers: Map<string, MessageHandler> = new Map();
  
  constructor(private config: WebSocketConfig) {
    this.initialize();
  }
  
  private initialize(): void {
    // HTTP 서버 생성
    this.httpServer = createServer();
    
    // WebSocket 서버 생성
    this.wss = new Server({
      server: this.httpServer,
      path: this.config.path || '/ws',
      maxPayload: this.config.maxPayload || 100 * 1024 * 1024, // 100MB
      perMessageDeflate: {
        zlibDeflateOptions: {
          chunkSize: 1024,
          memLevel: 7,
          level: 3
        },
        zlibInflateOptions: {
          chunkSize: 10 * 1024
        },
        clientNoContextTakeover: true,
        serverNoContextTakeover: true,
        serverMaxWindowBits: 10,
        concurrencyLimit: 10,
        threshold: 1024
      }
    });
    
    this.setupEventHandlers();
    this.registerDefaultHandlers();
  }
  
  private setupEventHandlers(): void {
    // 연결 이벤트
    this.wss.on('connection', async (ws, request) => {
      const connectionId = generateConnectionId();
      const clientInfo = this.extractClientInfo(request);
      
      try {
        // 연결 처리
        await this.handleConnection(ws, connectionId, clientInfo);
      } catch (error) {
        console.error('Connection handling error:', error);
        ws.close(1002, 'Connection error');
      }
    });
    
    // 서버 에러
    this.wss.on('error', (error) => {
      console.error('WebSocket server error:', error);
      this.handleServerError(error);
    });
    
    // 서버 종료
    this.wss.on('close', () => {
      console.log('WebSocket server closed');
      this.cleanup();
    });
  }
  
  private async handleConnection(
    ws: WebSocket,
    connectionId: string,
    clientInfo: ClientInfo
  ): Promise<void> {
    console.log(`New connection: ${connectionId}`);
    
    // 연결 저장
    this.connections.set(connectionId, ws);
    
    // 연결 컨텍스트 생성
    const context = new ConnectionContext(connectionId, clientInfo);
    ws['context'] = context;
    
    // 환영 메시지
    await this.sendMessage(ws, {
      type: 'connection',
      payload: {
        connectionId,
        version: this.config.version,
        features: this.config.features
      }
    });
    
    // 메시지 핸들러 설정
    ws.on('message', async (data) => {
      await this.handleMessage(ws, data, context);
    });
    
    // 에러 핸들러
    ws.on('error', (error) => {
      console.error(`Connection ${connectionId} error:`, error);
      this.handleConnectionError(connectionId, error);
    });
    
    // 연결 종료 핸들러
    ws.on('close', (code, reason) => {
      console.log(`Connection ${connectionId} closed: ${code} ${reason}`);
      this.handleDisconnection(connectionId, code, reason);
    });
    
    // Ping/Pong 설정
    this.setupHeartbeat(ws, connectionId);
  }
  
  private setupHeartbeat(ws: WebSocket, connectionId: string): void {
    const interval = this.config.heartbeatInterval || 30000;
    let isAlive = true;
    
    ws.on('pong', () => {
      isAlive = true;
    });
    
    const heartbeat = setInterval(() => {
      if (!isAlive) {
        // 연결 종료
        this.terminateConnection(connectionId);
        return;
      }
      
      isAlive = false;
      ws.ping();
    }, interval);
    
    ws['heartbeat'] = heartbeat;
  }
  
  private extractClientInfo(request: any): ClientInfo {
    const url = parse(request.url || '', true);
    
    return {
      ip: request.socket.remoteAddress,
      userAgent: request.headers['user-agent'],
      origin: request.headers['origin'],
      query: url.query,
      headers: request.headers
    };
  }
  
  async start(port: number = 8080): Promise<void> {
    return new Promise((resolve, reject) => {
      this.httpServer.listen(port, () => {
        console.log(`WebSocket server listening on port ${port}`);
        resolve();
      });
      
      this.httpServer.on('error', reject);
    });
  }
  
  async stop(): Promise<void> {
    // 모든 연결 종료
    for (const [connectionId, ws] of this.connections) {
      ws.close(1001, 'Server shutting down');
    }
    
    // 서버 종료
    return new Promise((resolve) => {
      this.wss.close(() => {
        this.httpServer.close(() => {
          resolve();
        });
      });
    });
  }
}

// WebSocket 설정
export interface WebSocketConfig {
  path?: string;
  maxPayload?: number;
  heartbeatInterval?: number;
  version: string;
  features: string[];
  ssl?: {
    cert: string;
    key: string;
  };
  cors?: {
    origin: string | string[];
    credentials: boolean;
  };
}

// 연결 컨텍스트
export class ConnectionContext {
  public authenticated: boolean = false;
  public user?: User;
  public subscriptions: Set<string> = new Set();
  public metadata: Map<string, any> = new Map();
  
  constructor(
    public connectionId: string,
    public clientInfo: ClientInfo
  ) {
    this.metadata.set('connectedAt', new Date());
  }
  
  authenticate(user: User): void {
    this.authenticated = true;
    this.user = user;
    this.metadata.set('authenticatedAt', new Date());
  }
  
  addSubscription(subscriptionId: string): void {
    this.subscriptions.add(subscriptionId);
  }
  
  removeSubscription(subscriptionId: string): void {
    this.subscriptions.delete(subscriptionId);
  }
}
```

**검증 기준**:
- [ ] WebSocket 서버 설정
- [ ] 연결 처리
- [ ] Heartbeat 메커니즘
- [ ] 컨텍스트 관리

#### SubTask 6.14.2: 연결 핸들링 및 인증

**담당자**: 백엔드 개발자  
**예상 소요시간**: 12시간

**작업 내용**:

```python
# backend/src/websocket/connection_handler.py
import jwt
from typing import Optional, Dict, Any
import asyncio

class ConnectionHandler:
    """WebSocket 연결 핸들러"""
    
    def __init__(self, auth_service, connection_manager):
        self.auth_service = auth_service
        self.connection_manager = connection_manager
        self.pending_auth: Dict[str, asyncio.Task] = {}
    
    async def handle_new_connection(
        self,
        websocket,
        connection_id: str,
        request_info: Dict
    ) -> Optional[ConnectionContext]:
        """새 연결 처리"""
        
        try:
            # 1. 초기 검증
            if not await self.validate_origin(request_info):
                await websocket.close(1008, "Invalid origin")
                return None
            
            # 2. Rate limiting 체크
            if not await self.check_rate_limit(request_info['ip']):
                await websocket.close(1008, "Rate limit exceeded")
                return None
            
            # 3. 연결 컨텍스트 생성
            context = ConnectionContext(
                connection_id=connection_id,
                websocket=websocket,
                ip_address=request_info['ip'],
                user_agent=request_info.get('user_agent')
            )
            
            # 4. 인증 처리
            auth_token = self.extract_auth_token(request_info)
            if auth_token:
                # 즉시 인증
                auth_result = await self.authenticate_connection(
                    context,
                    auth_token
                )
                if not auth_result:
                    await websocket.close(1008, "Authentication failed")
                    return None
            else:
                # 인증 대기 (grace period)
                self.schedule_auth_timeout(context)
            
            # 5. 연결 등록
            await self.connection_manager.add_connection(
                connection_id,
                websocket,
                context
            )
            
            # 6. 환영 메시지
            await self.send_welcome_message(context)
            
            return context
            
        except Exception as e:
            await websocket.close(1011, "Server error")
            raise e
    
    async def authenticate_connection(
        self,
        context: ConnectionContext,
        token: str
    ) -> bool:
        """연결 인증"""
        
        try:
            # JWT 토큰 검증
            payload = jwt.decode(
                token,
                self.auth_service.secret_key,
                algorithms=['HS256']
            )
            
            # 사용자 정보 조회
            user = await self.auth_service.get_user(payload['user_id'])
            if not user:
                return False
            
            # 권한 확인
            permissions = await self.auth_service.get_permissions(user.id)
            
            # 컨텍스트 업데이트
            context.authenticate(user, permissions)
            
            # 인증 성공 메시지
            await context.send({
                'type': 'auth_success',
                'payload': {
                    'user_id': user.id,
                    'permissions': permissions
                }
            })
            
            return True
            
        except jwt.ExpiredSignatureError:
            await context.send({
                'type': 'auth_error',
                'payload': {'error': 'Token expired'}
            })
            return False
            
        except jwt.InvalidTokenError:
            await context.send({
                'type': 'auth_error',
                'payload': {'error': 'Invalid token'}
            })
            return False
    
    def extract_auth_token(self, request_info: Dict) -> Optional[str]:
        """인증 토큰 추출"""
        
        # 1. Query parameter
        if 'token' in request_info.get('query', {}):
            return request_info['query']['token']
        
        # 2. Cookie
        cookies = request_info.get('cookies', {})
        if 'auth_token' in cookies:
            return cookies['auth_token']
        
        # 3. Authorization header
        auth_header = request_info.get('headers', {}).get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        return None
    
    def schedule_auth_timeout(self, context: ConnectionContext):
        """인증 타임아웃 스케줄링"""
        
        async def auth_timeout():
            await asyncio.sleep(30)  # 30초 대기
            
            if not context.authenticated:
                await context.send({
                    'type': 'auth_required',
                    'payload': {
                        'message': 'Authentication required',
                        'timeout': 30
                    }
                })
                
                await asyncio.sleep(10)  # 추가 10초 대기
                
                if not context.authenticated:
                    await context.websocket.close(
                        1008,
                        "Authentication timeout"
                    )
        
        task = asyncio.create_task(auth_timeout())
        self.pending_auth[context.connection_id] = task
    
    async def handle_auth_message(
        self,
        context: ConnectionContext,
        message: Dict
    ):
        """인증 메시지 처리"""
        
        token = message.get('token')
        if not token:
            await context.send({
                'type': 'auth_error',
                'payload': {'error': 'Token required'}
            })
            return
        
        # 인증 시도
        success = await self.authenticate_connection(context, token)
        
        if success:
            # 타임아웃 태스크 취소
            if context.connection_id in self.pending_auth:
                self.pending_auth[context.connection_id].cancel()
                del self.pending_auth[context.connection_id]
        else:
            # 인증 실패 카운터
            context.auth_attempts += 1
            
            if context.auth_attempts >= 3:
                await context.websocket.close(
                    1008,
                    "Too many authentication attempts"
                )

class PermissionChecker:
    """권한 체크"""
    
    def __init__(self):
        self.permission_cache = TTLCache(maxsize=1000, ttl=300)
    
    async def check_permission(
        self,
        context: ConnectionContext,
        resource: str,
        action: str
    ) -> bool:
        """권한 확인"""
        
        if not context.authenticated:
            return False
        
        # 캐시 확인
        cache_key = f"{context.user.id}:{resource}:{action}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
        
        # 권한 체크
        has_permission = await self.evaluate_permission(
            context.permissions,
            resource,
            action
        )
        
        # 캐시 저장
        self.permission_cache[cache_key] = has_permission
        
        return has_permission
    
    async def evaluate_permission(
        self,
        permissions: List[str],
        resource: str,
        action: str
    ) -> bool:
        """권한 평가"""
        
        required = f"{resource}:{action}"
        
        # 직접 권한
        if required in permissions:
            return True
        
        # 와일드카드 권한
        if f"{resource}:*" in permissions:
            return True
        
        if "*:*" in permissions:  # 관리자
            return True
        
        return False

class SecureConnectionUpgrade:
    """보안 연결 업그레이드"""
    
    async def upgrade_to_secure(
        self,
        context: ConnectionContext
    ) -> bool:
        """TLS 업그레이드"""
        
        # TLS 핸드셰이크
        await context.send({
            'type': 'security_upgrade',
            'payload': {
                'method': 'TLS',
                'version': '1.3'
            }
        })
        
        # 클라이언트 응답 대기
        response = await context.receive()
        
        if response.get('type') == 'security_upgrade_accept':
            # TLS 연결 설정
            context.secure = True
            context.tls_version = '1.3'
            return True
        
        return False
```

**검증 기준**:
- [ ] 연결 인증 시스템
- [ ] JWT 토큰 처리
- [ ] 권한 관리
- [ ] 보안 업그레이드

#### SubTask 6.14.3: 메시지 프로토콜 정의

**담당자**: 백엔드 개발자  
**예상 소요시간**: 10시간

**작업 내용**:

```typescript
// backend/src/websocket/protocol.ts
export interface Message {
  id: string;
  type: MessageType;
  payload: any;
  timestamp: number;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  correlationId?: string;
  replyTo?: string;
  ttl?: number;
  priority?: number;
  compression?: string;
}

export enum MessageType {
  // 연결 관리
  CONNECTION = 'connection',
  PING = 'ping',
  PONG = 'pong',
  CLOSE = 'close',
  
  // 인증
  AUTH_REQUEST = 'auth_request',
  AUTH_RESPONSE = 'auth_response',
  AUTH_ERROR = 'auth_error',
  
  // 구독
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  SUBSCRIPTION_DATA = 'subscription_data',
  
  // RPC
  RPC_REQUEST = 'rpc_request',
  RPC_RESPONSE = 'rpc_response',
  RPC_ERROR = 'rpc_error',
  
  // 이벤트
  EVENT = 'event',
  BROADCAST = 'broadcast',
  
  // 에러
  ERROR = 'error'
}

export class MessageProtocol {
  private version: string = '1.0';
  private encoders: Map<string, MessageEncoder> = new Map();
  private decoders: Map<string, MessageDecoder> = new Map();
  
  constructor() {
    this.registerEncoders();
    this.registerDecoders();
  }
  
  private registerEncoders(): void {
    // JSON 인코더
    this.encoders.set('json', {
      encode: (message: Message) => JSON.stringify(message),
      contentType: 'application/json'
    });
    
    // MessagePack 인코더
    this.encoders.set('msgpack', {
      encode: (message: Message) => msgpack.encode(message),
      contentType: 'application/msgpack'
    });
    
    // Protocol Buffers 인코더
    this.encoders.set('protobuf', {
      encode: (message: Message) => this.encodeProtobuf(message),
      contentType: 'application/protobuf'
    });
  }
  
  encode(
    message: Message,
    format: string = 'json'
  ): Buffer | string {
    const encoder = this.encoders.get(format);
    if (!encoder) {
      throw new Error(`Unknown encoding format: ${format}`);
    }
    
    // 메시지 유효성 검증
    this.validateMessage(message);
    
    // 메타데이터 추가
    message.timestamp = message.timestamp || Date.now();
    message.id = message.id || generateMessageId();
    
    return encoder.encode(message);
  }
  
  decode(data: Buffer | string, format: string = 'json'): Message {
    const decoder = this.decoders.get(format);
    if (!decoder) {
      throw new Error(`Unknown decoding format: ${format}`);
    }
    
    const message = decoder.decode(data);
    
    // 메시지 유효성 검증
    this.validateMessage(message);
    
    return message;
  }
  
  private validateMessage(message: Message): void {
    if (!message.type) {
      throw new Error('Message type is required');
    }
    
    if (!message.id) {
      message.id = generateMessageId();
    }
    
    // 타입별 페이로드 검증
    this.validatePayload(message.type, message.payload);
  }
  
  private validatePayload(type: MessageType, payload: any): void {
    const schema = this.getPayloadSchema(type);
    if (!schema) return;
    
    const validator = new Ajv();
    const valid = validator.validate(schema, payload);
    
    if (!valid) {
      throw new Error(`Invalid payload: ${validator.errors}`);
    }
  }
}

// 메시지 빌더
export class MessageBuilder {
  private message: Partial<Message> = {};
  
  static create(type: MessageType): MessageBuilder {
    const builder = new MessageBuilder();
    builder.message.type = type;
    return builder;
  }
  
  withPayload(payload: any): MessageBuilder {
    this.message.payload = payload;
    return this;
  }
  
  withCorrelationId(id: string): MessageBuilder {
    if (!this.message.metadata) {
      this.message.metadata = {};
    }
    this.message.metadata.correlationId = id;
    return this;
  }
  
  withReplyTo(replyTo: string): MessageBuilder {
    if (!this.message.metadata) {
      this.message.metadata = {};
    }
    this.message.metadata.replyTo = replyTo;
    return this;
  }
  
  withPriority(priority: number): MessageBuilder {
    if (!this.message.metadata) {
      this.message.metadata = {};
    }
    this.message.metadata.priority = priority;
    return this;
  }
  
  build(): Message {
    return {
      id: generateMessageId(),
      type: this.message.type!,
      payload: this.message.payload,
      timestamp: Date.now(),
      metadata: this.message.metadata
    } as Message;
  }
}

// 메시지 라우터
export class MessageRouter {
  private routes: Map<MessageType, MessageHandler[]> = new Map();
  private middleware: MessageMiddleware[] = [];
  
  use(middleware: MessageMiddleware): void {
    this.middleware.push(middleware);
  }
  
  on(type: MessageType, handler: MessageHandler): void {
    if (!this.routes.has(type)) {
      this.routes.set(type, []);
    }
    this.routes.get(type)!.push(handler);
  }
  
  async route(
    message: Message,
    context: ConnectionContext
  ): Promise<void> {
    // 미들웨어 실행
    for (const mw of this.middleware) {
      const shouldContinue = await mw(message, context);
      if (!shouldContinue) return;
    }
    
    // 핸들러 실행
    const handlers = this.routes.get(message.type) || [];
    
    for (const handler of handlers) {
      try {
        await handler(message, context);
      } catch (error) {
        await this.handleError(error, message, context);
      }
    }
  }
  
  private async handleError(
    error: Error,
    message: Message,
    context: ConnectionContext
  ): Promise<void> {
    const errorMessage = MessageBuilder
      .create(MessageType.ERROR)
      .withPayload({
        error: error.message,
        originalMessage: message.id,
        code: 'HANDLER_ERROR'
      })
      .withCorrelationId(message.id)
      .build();
    
    await context.send(errorMessage);
  }
}
```

**검증 기준**:
- [ ] 메시지 프로토콜 정의
- [ ] 인코딩/디코딩
- [ ] 메시지 검증
- [ ] 라우팅 시스템

#### SubTask 6.14.4: 연결 풀 관리

**담당자**: 시스템 엔지니어  
**예상 소요시간**: 10시간

**작업 내용**:

```python
# backend/src/websocket/connection_pool.py
from typing import Dict, List, Optional, Set
import asyncio
from dataclasses import dataclass

@dataclass
class PoolConfig:
    """연결 풀 설정"""
    min_size: int = 10
    max_size: int = 1000
    max_idle_time: int = 300  # seconds
    max_lifetime: int = 3600  # seconds
    health_check_interval: int = 30
    overflow_policy: str = 'reject'  # reject, queue, scale

class ConnectionPool:
    """WebSocket 연결 풀"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self.connections: Dict[str, PooledConnection] = {}
        self.available: asyncio.Queue = asyncio.Queue()
        self.in_use: Set[str] = set()
        self.waiting: asyncio.Queue = asyncio.Queue()
        self.stats = PoolStatistics()
        
    async def initialize(self):
        """풀 초기화"""
        
        # 최소 연결 생성
        for _ in range(self.config.min_size):
            conn = await self.create_connection()
            await self.available.put(conn)
        
        # 헬스 체크 시작
        asyncio.create_task(self.health_check_loop())
        
        # 정리 작업 시작
        asyncio.create_task(self.cleanup_loop())
    
    async def acquire(
        self,
        timeout: Optional[float] = None
    ) -> PooledConnection:
        """연결 획득"""
        
        self.stats.acquire_attempts += 1
        
        try:
            # 사용 가능한 연결 확인
            if not self.available.empty():
                conn = await self.available.get()
                
                # 연결 상태 확인
                if await self.validate_connection(conn):
                    self.in_use.add(conn.id)
                    self.stats.active_connections += 1
                    return conn
                else:
                    # 연결 재생성
                    await self.destroy_connection(conn)
                    return await self.acquire(timeout)
            
            # 풀 크기 확인
            current_size = len(self.connections)
            
            if current_size < self.config.max_size:
                # 새 연결 생성
                conn = await self.create_connection()
                self.in_use.add(conn.id)
                self.stats.active_connections += 1
                return conn
            
            # 오버플로우 정책 적용
            return await self.handle_overflow(timeout)
            
        except asyncio.TimeoutError:
            self.stats.acquire_timeouts += 1
            raise PoolExhaustedError("Connection pool exhausted")
    
    async def release(self, connection: PooledConnection):
        """연결 반환"""
        
        if connection.id not in self.in_use:
            return
        
        self.in_use.remove(connection.id)
        self.stats.active_connections -= 1
        
        # 연결 상태 확인
        if await self.validate_connection(connection):
            # 재사용 가능
            connection.last_used = datetime.now()
            await self.available.put(connection)
            
            # 대기 중인 요청 처리
            if not self.waiting.empty():
                waiter = await self.waiting.get()
                waiter.set_result(connection)
        else:
            # 연결 폐기
            await self.destroy_connection(connection)
            
            # 새 연결 생성
            if len(self.connections) < self.config.min_size:
                new_conn = await self.create_connection()
                await self.available.put(new_conn)
    
    async def handle_overflow(
        self,
        timeout: Optional[float]
    ) -> PooledConnection:
        """오버플로우 처리"""
        
        if self.config.overflow_policy == 'reject':
            raise PoolExhaustedError("Connection pool at maximum capacity")
            
        elif self.config.overflow_policy == 'queue':
            # 대기 큐에 추가
            future = asyncio.Future()
            await self.waiting.put(future)
            
            if timeout:
                return await asyncio.wait_for(future, timeout)
            else:
                return await future
                
        elif self.config.overflow_policy == 'scale':
            # 동적 스케일링
            await self.scale_up()
            return await self.acquire(timeout)
    
    async def health_check_loop(self):
        """헬스 체크 루프"""
        
        while True:
            await asyncio.sleep(self.config.health_check_interval)
            
            # 모든 연결 체크
            for conn in list(self.connections.values()):
                if not await self.ping_connection(conn):
                    await self.handle_unhealthy_connection(conn)
            
            # 통계 업데이트
            self.stats.update()
    
    async def cleanup_loop(self):
        """정리 작업 루프"""
        
        while True:
            await asyncio.sleep(60)  # 1분마다
            
            now = datetime.now()
            
            # 유휴 연결 정리
            while not self.available.empty():
                conn = await self.available.get()
                
                idle_time = (now - conn.last_used).total_seconds()
                lifetime = (now - conn.created_at).total_seconds()
                
                if (idle_time > self.config.max_idle_time or
                    lifetime > self.config.max_lifetime):
                    await self.destroy_connection(conn)
                else:
                    await self.available.put(conn)
                    break
            
            # 최소 크기 유지
            await self.maintain_min_size()

@dataclass
class PooledConnection:
    """풀링된 연결"""
    id: str
    websocket: Any
    created_at: datetime
    last_used: datetime
    metadata: Dict = field(default_factory=dict)

class ConnectionPoolManager:
    """연결 풀 관리자"""
    
    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self.default_config = PoolConfig()
    
    def create_pool(
        self,
        name: str,
        config: Optional[PoolConfig] = None
    ) -> ConnectionPool:
        """풀 생성"""
        
        if name in self.pools:
            raise ValueError(f"Pool {name} already exists")
        
        config = config or self.default_config
        pool = ConnectionPool(config)
        self.pools[name] = pool
        
        return pool
    
    def get_pool(self, name: str) -> Optional[ConnectionPool]:
        """풀 조회"""
        return self.pools.get(name)
    
    async def get_connection(
        self,
        pool_name: str = 'default'
    ) -> PooledConnection:
        """연결 획득"""
        
        pool = self.get_pool(pool_name)
        if not pool:
            pool = self.create_pool(pool_name)
            await pool.initialize()
        
        return await pool.acquire()
    
    def get_statistics(self) -> Dict[str, PoolStatistics]:
        """통계 조회"""
        
        return {
            name: pool.stats
            for name, pool in self.pools.items()
        }

class PoolStatistics:
    """풀 통계"""
    
    def __init__(self):
        self.total_connections = 0
        self.active_connections = 0
        self.idle_connections = 0
        self.acquire_attempts = 0
        self.acquire_timeouts = 0
        self.connection_errors = 0
        self.created_connections = 0
        self.destroyed_connections = 0
    
    def update(self):
        """통계 업데이트"""
        
        self.idle_connections = self.total_connections - self.active_connections
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        
        return {
            'total': self.total_connections,
            'active': self.active_connections,
            'idle': self.idle_connections,
            'acquire_attempts': self.acquire_attempts,
            'acquire_timeouts': self.acquire_timeouts,
            'errors': self.connection_errors,
            'created': self.created_connections,
            'destroyed': self.destroyed_connections,
            'utilization': (
                self.active_connections / self.total_connections * 100
                if self.total_connections > 0 else 0
            )
        }
```

**검증 기준**:
- [ ] 연결 풀링
- [ ] 오버플로우 정책
- [ ] 헬스 체크
- [ ] 통계 수집

---

## Task 6.15: 실시간 이벤트 스트리밍

### Task 6.15.1: SSE Server Implementation

```python
# src/api/streaming/sse_server.py
from typing import AsyncIterator, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
import uuid

@dataclass
class SSEClient:
    """SSE 클라이언트"""
    id: str
    subscriptions: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)

class SSEBroadcaster:
    """SSE 브로드캐스터"""
    
    def __init__(self):
        self.clients: Dict[str, SSEClient] = {}
        self.channels: Dict[str, Set[str]] = {}
        
    async def connect(self, client_id: Optional[str] = None) -> str:
        """클라이언트 연결"""
        client_id = client_id or str(uuid.uuid4())
        self.clients[client_id] = SSEClient(id=client_id)
        return client_id
    
    async def subscribe(self, client_id: str, channel: str):
        """채널 구독"""
        if client_id in self.clients:
            self.clients[client_id].subscriptions.add(channel)
            if channel not in self.channels:
                self.channels[channel] = set()
            self.channels[channel].add(client_id)
    
    async def publish(self, channel: str, event: str, data: Any):
        """이벤트 발행"""
        if channel in self.channels:
            for client_id in self.channels[channel]:
                yield self._format_sse(event, data)
    
    def _format_sse(self, event: str, data: Any) -> str:
        """SSE 포맷"""
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"
```

### Task 6.15.2: WebSocket Streaming

```python
# src/api/streaming/websocket_stream.py
from fastapi import WebSocket
from typing import Dict, Any, Optional
import asyncio
import json

class WebSocketStreamer:
    """WebSocket 스트리머"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.streams: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """연결 수립"""
        await websocket.accept()
        self.connections[client_id] = websocket
        
    async def stream_data(
        self,
        client_id: str,
        data_source: AsyncIterator[Any],
        chunk_size: int = 1024
    ):
        """데이터 스트리밍"""
        websocket = self.connections.get(client_id)
        if not websocket:
            return
            
        try:
            async for chunk in data_source:
                await websocket.send_json({
                    "type": "data",
                    "chunk": chunk,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
```

### Task 6.15.3: Event Stream Processor

```python
# src/api/streaming/event_processor.py
from typing import AsyncIterator, Optional, List, Callable
from dataclasses import dataclass
import asyncio

@dataclass
class StreamEvent:
    """스트림 이벤트"""
    type: str
    data: Any
    timestamp: float

class EventStreamPipeline:
    """이벤트 스트림 파이프라인"""
    
    def __init__(self):
        self.processors: List[Callable] = []
        self.filters: List[Callable] = []
        
    async def process_stream(
        self,
        input_stream: AsyncIterator[StreamEvent]
    ) -> AsyncIterator[StreamEvent]:
        """스트림 처리"""
        async for event in input_stream:
            if await self._apply_filters(event):
                event = await self._apply_processors(event)
                if event:
                    yield event
    
    async def _apply_filters(self, event: StreamEvent) -> bool:
        """필터 적용"""
        for filter_func in self.filters:
            if not await filter_func(event):
                return False
        return True
    
    async def _apply_processors(self, event: StreamEvent) -> Optional[StreamEvent]:
        """프로세서 적용"""
        for processor in self.processors:
            event = await processor(event)
            if event is None:
                break
        return event
```

### Task 6.15.4: Stream Monitoring & Metrics

```python
# src/api/streaming/stream_metrics.py
from dataclasses import dataclass, field
from typing import Dict
import time

@dataclass
class StreamMetrics:
    """스트림 메트릭"""
    events_sent: int = 0
    events_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    errors: int = 0
    latency_ms: float = 0
    
class StreamMonitor:
    """스트림 모니터"""
    
    def __init__(self):
        self.metrics: Dict[str, StreamMetrics] = {}
        
    def record_event(self, stream_id: str, event_type: str, size: int):
        """이벤트 기록"""
        if stream_id not in self.metrics:
            self.metrics[stream_id] = StreamMetrics()
            
        metrics = self.metrics[stream_id]
        if event_type == "sent":
            metrics.events_sent += 1
            metrics.bytes_sent += size
        elif event_type == "received":
            metrics.events_received += 1
            metrics.bytes_received += size
            
    def get_metrics(self, stream_id: str) -> StreamMetrics:
        """메트릭 조회"""
        return self.metrics.get(stream_id, StreamMetrics())
```

**검증 기준**:
- [ ] SSE 서버 구현
- [ ] WebSocket 스트리밍
- [ ] 이벤트 프로세싱
- [ ] 메트릭 수집

---

## Task 6.16: 양방향 통신 프로토콜

### Task 6.16.1: Protocol Design

```python
# src/api/protocol/protocol_design.py
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import uuid

class MessageType(Enum):
    """메시지 타입"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    
@dataclass
class ProtocolMessage:
    """프로토콜 메시지"""
    id: str
    type: MessageType
    method: Optional[str]
    params: Optional[Dict[str, Any]]
    result: Optional[Any]
    error: Optional[Dict[str, Any]]
    
    @classmethod
    def create_request(cls, method: str, params: Dict = None):
        """요청 생성"""
        return cls(
            id=str(uuid.uuid4()),
            type=MessageType.REQUEST,
            method=method,
            params=params,
            result=None,
            error=None
        )
    
    @classmethod
    def create_response(cls, request_id: str, result: Any):
        """응답 생성"""
        return cls(
            id=request_id,
            type=MessageType.RESPONSE,
            method=None,
            params=None,
            result=result,
            error=None
        )
```

### Task 6.16.2: Message Router

```python
# src/api/protocol/message_router.py
from typing import Dict, Callable, Any
import asyncio

class MessageRouter:
    """메시지 라우터"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
    def register_handler(self, method: str, handler: Callable):
        """핸들러 등록"""
        self.handlers[method] = handler
        
    async def route_message(self, message: ProtocolMessage) -> Optional[ProtocolMessage]:
        """메시지 라우팅"""
        if message.type == MessageType.REQUEST:
            return await self._handle_request(message)
        elif message.type == MessageType.RESPONSE:
            return await self._handle_response(message)
        elif message.type == MessageType.NOTIFICATION:
            return await self._handle_notification(message)
            
    async def _handle_request(self, message: ProtocolMessage) -> ProtocolMessage:
        """요청 처리"""
        handler = self.handlers.get(message.method)
        if not handler:
            return ProtocolMessage.create_error(
                message.id,
                code=-32601,
                message="Method not found"
            )
            
        try:
            result = await handler(message.params)
            return ProtocolMessage.create_response(message.id, result)
        except Exception as e:
            return ProtocolMessage.create_error(
                message.id,
                code=-32603,
                message=str(e)
            )
```

### Task 6.16.3: RPC Implementation

```python
# src/api/protocol/rpc_impl.py
from typing import Any, Dict, Optional
import asyncio

class RPCClient:
    """RPC 클라이언트"""
    
    def __init__(self, transport):
        self.transport = transport
        self.pending: Dict[str, asyncio.Future] = {}
        
    async def call(
        self,
        method: str,
        params: Dict = None,
        timeout: float = 30.0
    ) -> Any:
        """원격 프로시저 호출"""
        request = ProtocolMessage.create_request(method, params)
        future = asyncio.Future()
        self.pending[request.id] = future
        
        await self.transport.send(request)
        
        try:
            result = await asyncio.wait_for(future, timeout)
            return result
        except asyncio.TimeoutError:
            del self.pending[request.id]
            raise TimeoutError(f"RPC call {method} timed out")
            
    async def handle_response(self, response: ProtocolMessage):
        """응답 처리"""
        if response.id in self.pending:
            future = self.pending.pop(response.id)
            if response.error:
                future.set_exception(Exception(response.error))
            else:
                future.set_result(response.result)

class RPCServer:
    """RPC 서버"""
    
    def __init__(self):
        self.methods: Dict[str, Callable] = {}
        
    def register(self, name: str = None):
        """메소드 등록 데코레이터"""
        def decorator(func):
            method_name = name or func.__name__
            self.methods[method_name] = func
            return func
        return decorator
        
    async def handle_request(self, request: ProtocolMessage) -> ProtocolMessage:
        """요청 처리"""
        method = self.methods.get(request.method)
        if not method:
            return ProtocolMessage.create_error(
                request.id,
                code=-32601,
                message=f"Method {request.method} not found"
            )
            
        try:
            result = await method(**request.params)
            return ProtocolMessage.create_response(request.id, result)
        except Exception as e:
            return ProtocolMessage.create_error(
                request.id,
                code=-32000,
                message=str(e)
            )
```

### Task 6.16.4: Protocol Negotiation

```python
# src/api/protocol/negotiation.py
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ProtocolCapability:
    """프로토콜 기능"""
    name: str
    version: str
    features: List[str]
    
class ProtocolNegotiator:
    """프로토콜 협상"""
    
    def __init__(self):
        self.supported_protocols = {
            "jsonrpc": ProtocolCapability("jsonrpc", "2.0", ["batch", "notification"]),
            "websocket": ProtocolCapability("websocket", "13", ["binary", "text"]),
            "sse": ProtocolCapability("sse", "1.0", ["retry", "id"])
        }
        
    async def negotiate(
        self,
        client_capabilities: List[str]
    ) -> Optional[ProtocolCapability]:
        """프로토콜 협상"""
        for cap in client_capabilities:
            if cap in self.supported_protocols:
                return self.supported_protocols[cap]
        return None
        
    def get_capabilities(self) -> Dict[str, ProtocolCapability]:
        """지원 기능 조회"""
        return self.supported_protocols
```

**검증 기준**:
- [ ] 프로토콜 설계
- [ ] 메시지 라우팅
- [ ] RPC 구현
- [ ] 프로토콜 협상

---

## Task 6.17: 인증/인가 시스템

### Task 6.17.1: Authentication Service

```python
# src/api/auth/authentication.py
from typing import Optional, Dict, Any
from dataclasses import dataclass
import hashlib
import secrets

@dataclass
class User:
    """사용자"""
    id: str
    username: str
    email: str
    password_hash: str
    
class AuthenticationService:
    """인증 서비스"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, str] = {}
        
    def hash_password(self, password: str, salt: bytes = None) -> str:
        """비밀번호 해싱"""
        if salt is None:
            salt = secrets.token_bytes(32)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
        
    async def register(self, username: str, email: str, password: str) -> User:
        """사용자 등록"""
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=self.hash_password(password)
        )
        self.users[user.id] = user
        return user
        
    async def authenticate(self, username: str, password: str) -> Optional[str]:
        """사용자 인증"""
        for user in self.users.values():
            if user.username == username:
                if self.verify_password(password, user.password_hash):
                    session_id = secrets.token_urlsafe(32)
                    self.sessions[session_id] = user.id
                    return session_id
        return None
```

### Task 6.17.2: Authorization Engine

```python
# src/api/auth/authorization.py
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum

class Permission(Enum):
    """권한"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    
@dataclass
class Role:
    """역할"""
    name: str
    permissions: Set[Permission]
    
class AuthorizationEngine:
    """인가 엔진"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self._init_default_roles()
        
    def _init_default_roles(self):
        """기본 역할 초기화"""
        self.roles["viewer"] = Role("viewer", {Permission.READ})
        self.roles["editor"] = Role("editor", {Permission.READ, Permission.WRITE})
        self.roles["admin"] = Role("admin", {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN})
        
    def assign_role(self, user_id: str, role_name: str):
        """역할 할당"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        self.user_roles[user_id].add(role_name)
        
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """권한 확인"""
        if user_id not in self.user_roles:
            return False
            
        for role_name in self.user_roles[user_id]:
            role = self.roles.get(role_name)
            if role and permission in role.permissions:
                return True
        return False
```

### Task 6.17.3: Session Management

```python
# src/api/auth/session.py
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import secrets

@dataclass
class Session:
    """세션"""
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    
class SessionManager:
    """세션 관리자"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.sessions: Dict[str, Session] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        
    def create_session(self, user_id: str, data: Dict = None) -> str:
        """세션 생성"""
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        
        session = Session(
            id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + self.ttl,
            data=data or {}
        )
        
        self.sessions[session_id] = session
        return session_id
        
    def get_session(self, session_id: str) -> Optional[Session]:
        """세션 조회"""
        session = self.sessions.get(session_id)
        if session and session.expires_at > datetime.utcnow():
            return session
        elif session:
            del self.sessions[session_id]
        return None
        
    def refresh_session(self, session_id: str) -> bool:
        """세션 갱신"""
        session = self.get_session(session_id)
        if session:
            session.expires_at = datetime.utcnow() + self.ttl
            return True
        return False
```

### Task 6.17.4: MFA Implementation

```python
# src/api/auth/mfa.py
import pyotp
import qrcode
from io import BytesIO
from typing import Optional

class MFAService:
    """다중 인증 서비스"""
    
    def __init__(self):
        self.user_secrets: Dict[str, str] = {}
        
    def generate_secret(self, user_id: str) -> str:
        """비밀키 생성"""
        secret = pyotp.random_base32()
        self.user_secrets[user_id] = secret
        return secret
        
    def generate_qr_code(self, user_id: str, issuer: str = "MyApp") -> bytes:
        """QR 코드 생성"""
        secret = self.user_secrets.get(user_id)
        if not secret:
            secret = self.generate_secret(user_id)
            
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name=issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
        
    def verify_token(self, user_id: str, token: str) -> bool:
        """토큰 검증"""
        secret = self.user_secrets.get(user_id)
        if not secret:
            return False
            
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

**검증 기준**:
- [ ] 인증 서비스
- [ ] 인가 엔진
- [ ] 세션 관리
- [ ] MFA 구현

---

## Task 6.18: OAuth 2.0/JWT 구현

### Task 6.18.1: OAuth Provider

```python
# src/api/oauth/provider.py
from typing import Dict, Optional, List
from dataclasses import dataclass
import secrets
from datetime import datetime, timedelta

@dataclass
class OAuthClient:
    """OAuth 클라이언트"""
    client_id: str
    client_secret: str
    redirect_uris: List[str]
    scopes: List[str]
    
@dataclass
class AuthorizationCode:
    """인가 코드"""
    code: str
    client_id: str
    user_id: str
    scopes: List[str]
    expires_at: datetime
    
class OAuthProvider:
    """OAuth 2.0 제공자"""
    
    def __init__(self):
        self.clients: Dict[str, OAuthClient] = {}
        self.auth_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, Dict] = {}
        
    def register_client(
        self,
        redirect_uris: List[str],
        scopes: List[str]
    ) -> OAuthClient:
        """클라이언트 등록"""
        client = OAuthClient(
            client_id=secrets.token_urlsafe(32),
            client_secret=secrets.token_urlsafe(64),
            redirect_uris=redirect_uris,
            scopes=scopes
        )
        self.clients[client.client_id] = client
        return client
        
    def authorize(
        self,
        client_id: str,
        user_id: str,
        scopes: List[str],
        redirect_uri: str
    ) -> str:
        """인가 코드 발급"""
        client = self.clients.get(client_id)
        if not client or redirect_uri not in client.redirect_uris:
            raise ValueError("Invalid client or redirect URI")
            
        code = secrets.token_urlsafe(32)
        auth_code = AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        self.auth_codes[code] = auth_code
        return code
```

### Task 6.18.2: JWT Token Service

```python
# src/api/oauth/jwt_service.py
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class JWTService:
    """JWT 토큰 서비스"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def create_access_token(
        self,
        subject: str,
        scopes: List[str] = None,
        expires_delta: timedelta = None
    ) -> str:
        """액세스 토큰 생성"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        payload = {
            "sub": subject,
            "scopes": scopes or [],
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    def create_refresh_token(
        self,
        subject: str,
        expires_delta: timedelta = None
    ) -> str:
        """리프레시 토큰 생성"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=30)
            
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

### Task 6.18.3: Token Refresh Logic

```python
# src/api/oauth/token_refresh.py
from typing import Optional, Tuple
from datetime import datetime, timedelta

class TokenRefreshService:
    """토큰 갱신 서비스"""
    
    def __init__(self, jwt_service: JWTService):
        self.jwt_service = jwt_service
        self.refresh_tokens: Dict[str, str] = {}
        
    def issue_token_pair(
        self,
        user_id: str,
        scopes: List[str] = None
    ) -> Tuple[str, str]:
        """토큰 쌍 발급"""
        access_token = self.jwt_service.create_access_token(
            subject=user_id,
            scopes=scopes,
            expires_delta=timedelta(minutes=15)
        )
        
        refresh_token = self.jwt_service.create_refresh_token(
            subject=user_id,
            expires_delta=timedelta(days=30)
        )
        
        self.refresh_tokens[refresh_token] = user_id
        
        return access_token, refresh_token
        
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """액세스 토큰 갱신"""
        payload = self.jwt_service.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
            
        if refresh_token not in self.refresh_tokens:
            return None
            
        user_id = payload["sub"]
        
        new_access_token = self.jwt_service.create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=15)
        )
        
        return new_access_token
        
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """리프레시 토큰 취소"""
        if refresh_token in self.refresh_tokens:
            del self.refresh_tokens[refresh_token]
            return True
        return False
```

### Task 6.18.4: JWKS Management

```python
# src/api/oauth/jwks.py
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Dict, List
import base64
import json

class JWKSManager:
    """JWKS 관리자"""
    
    def __init__(self):
        self.keys: Dict[str, Dict] = {}
        
    def generate_key_pair(self, kid: str) -> Dict:
        """키 쌍 생성"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        # JWK 형식으로 변환
        public_numbers = public_key.public_numbers()
        
        jwk = {
            "kty": "RSA",
            "use": "sig",
            "kid": kid,
            "n": base64.urlsafe_b64encode(
                public_numbers.n.to_bytes(256, 'big')
            ).rstrip(b'=').decode('utf-8'),
            "e": base64.urlsafe_b64encode(
                public_numbers.e.to_bytes(3, 'big')
            ).rstrip(b'=').decode('utf-8')
        }
        
        self.keys[kid] = {
            "private_key": private_key,
            "public_key": public_key,
            "jwk": jwk
        }
        
        return jwk
        
    def get_jwks(self) -> Dict:
        """JWKS 조회"""
        return {
            "keys": [key_data["jwk"] for key_data in self.keys.values()]
        }
        
    def rotate_keys(self) -> str:
        """키 순환"""
        new_kid = f"key-{datetime.utcnow().timestamp()}"
        self.generate_key_pair(new_kid)
        
        # 이전 키 보관 (일정 기간)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        for kid in list(self.keys.keys()):
            if self._parse_kid_timestamp(kid) < cutoff:
                del self.keys[kid]
                
        return new_kid
```

**검증 기준**:
- [ ] OAuth 제공자
- [ ] JWT 토큰 서비스
- [ ] 토큰 갱신 로직
- [ ] JWKS 관리

---

## Task 6.19: API 키 관리

### Task 6.19.1: API Key Generation

```python
# src/api/keys/key_generation.py
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets
import hashlib

@dataclass
class APIKey:
    """API 키"""
    id: str
    name: str
    key_hash: str
    prefix: str
    created_at: datetime
    expires_at: Optional[datetime]
    scopes: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
class APIKeyGenerator:
    """API 키 생성기"""
    
    def __init__(self, prefix: str = "sk"):
        self.prefix = prefix
        self.keys: Dict[str, APIKey] = {}
        
    def generate_key(
        self,
        name: str,
        scopes: List[str] = None,
        expires_in: Optional[timedelta] = None
    ) -> tuple[str, APIKey]:
        """API 키 생성"""
        # 키 생성
        raw_key = secrets.token_urlsafe(32)
        full_key = f"{self.prefix}_{raw_key}"
        
        # 키 해시
        key_hash = self._hash_key(full_key)
        
        # 키 객체 생성
        api_key = APIKey(
            id=secrets.token_hex(16),
            name=name,
            key_hash=key_hash,
            prefix=full_key[:8],  # 키 프리픽스 저장
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + expires_in if expires_in else None,
            scopes=scopes or [],
            metadata={}
        )
        
        self.keys[api_key.id] = api_key
        
        return full_key, api_key
        
    def _hash_key(self, key: str) -> str:
        """키 해싱"""
        return hashlib.sha256(key.encode()).hexdigest()
        
    def validate_key(self, key: str) -> Optional[APIKey]:
        """키 검증"""
        key_hash = self._hash_key(key)
        
        for api_key in self.keys.values():
            if api_key.key_hash == key_hash:
                if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                    return None
                return api_key
                
        return None
```

### Task 6.19.2: Key Rotation System

```python
# src/api/keys/key_rotation.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio

@dataclass
class KeyRotationPolicy:
    """키 순환 정책"""
    rotation_interval: timedelta
    grace_period: timedelta
    auto_rotate: bool = True
    notify_before: timedelta = timedelta(days=7)
    
class KeyRotationService:
    """키 순환 서비스"""
    
    def __init__(self, generator: APIKeyGenerator):
        self.generator = generator
        self.policies: Dict[str, KeyRotationPolicy] = {}
        self.rotation_schedule: Dict[str, datetime] = {}
        
    def set_rotation_policy(
        self,
        key_id: str,
        policy: KeyRotationPolicy
    ):
        """순환 정책 설정"""
        self.policies[key_id] = policy
        
        # 다음 순환 일정 설정
        api_key = self.generator.keys.get(key_id)
        if api_key:
            next_rotation = api_key.created_at + policy.rotation_interval
            self.rotation_schedule[key_id] = next_rotation
            
    async def rotate_key(
        self,
        key_id: str
    ) -> Optional[tuple[str, APIKey]]:
        """키 순환"""
        old_key = self.generator.keys.get(key_id)
        if not old_key:
            return None
            
        policy = self.policies.get(key_id)
        
        # 새 키 생성
        new_full_key, new_api_key = self.generator.generate_key(
            name=f"{old_key.name}_rotated",
            scopes=old_key.scopes,
            expires_in=policy.rotation_interval if policy else None
        )
        
        # 이전 키에 유예 기간 설정
        if policy:
            old_key.expires_at = datetime.utcnow() + policy.grace_period
            
        # 순환 일정 업데이트
        if policy:
            self.rotation_schedule[new_api_key.id] = datetime.utcnow() + policy.rotation_interval
            
        return new_full_key, new_api_key
        
    async def check_rotation_schedule(self):
        """순환 일정 확인"""
        now = datetime.utcnow()
        
        for key_id, next_rotation in list(self.rotation_schedule.items()):
            if now >= next_rotation:
                policy = self.policies.get(key_id)
                if policy and policy.auto_rotate:
                    await self.rotate_key(key_id)
```

### Task 6.19.3: Key Validation

```python
# src/api/keys/key_validation.py
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ValidationResult:
    """검증 결과"""
    valid: bool
    key_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
class KeyValidator:
    """키 검증기"""
    
    def __init__(self, generator: APIKeyGenerator):
        self.generator = generator
        self.blacklist: Set[str] = set()
        self.rate_limits: Dict[str, List[datetime]] = {}
        
    def validate(
        self,
        key: str,
        required_scopes: List[str] = None
    ) -> ValidationResult:
        """키 검증"""
        # 형식 검증
        if not self._validate_format(key):
            return ValidationResult(
                valid=False,
                error="Invalid key format"
            )
            
        # 블랙리스트 확인
        if key in self.blacklist:
            return ValidationResult(
                valid=False,
                error="Key is blacklisted"
            )
            
        # 키 존재 및 만료 확인
        api_key = self.generator.validate_key(key)
        if not api_key:
            return ValidationResult(
                valid=False,
                error="Invalid or expired key"
            )
            
        # 스코프 확인
        if required_scopes:
            if not all(scope in api_key.scopes for scope in required_scopes):
                return ValidationResult(
                    valid=False,
                    key_id=api_key.id,
                    error="Insufficient scopes"
                )
                
        # 레이트 리밋 확인
        if not self._check_rate_limit(api_key.id):
            return ValidationResult(
                valid=False,
                key_id=api_key.id,
                error="Rate limit exceeded"
            )
            
        return ValidationResult(
            valid=True,
            key_id=api_key.id,
            scopes=api_key.scopes
        )
        
    def _validate_format(self, key: str) -> bool:
        """형식 검증"""
        pattern = r'^[a-zA-Z]+_[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, key))
        
    def _check_rate_limit(
        self,
        key_id: str,
        limit: int = 100,
        window: timedelta = timedelta(minutes=1)
    ) -> bool:
        """레이트 리밋 확인"""
        now = datetime.utcnow()
        
        if key_id not in self.rate_limits:
            self.rate_limits[key_id] = []
            
        # 윈도우 밖 요청 제거
        self.rate_limits[key_id] = [
            ts for ts in self.rate_limits[key_id]
            if now - ts < window
        ]
        
        # 리밋 확인
        if len(self.rate_limits[key_id]) >= limit:
            return False
            
        self.rate_limits[key_id].append(now)
        return True
        
    def revoke_key(self, key_id: str):
        """키 취소"""
        if key_id in self.generator.keys:
            api_key = self.generator.keys[key_id]
            self.blacklist.add(api_key.key_hash)
```

### Task 6.19.4: Key Analytics

```python
# src/api/keys/key_analytics.py
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

@dataclass
class KeyUsageMetrics:
    """키 사용 메트릭"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_used: Optional[datetime] = None
    endpoints_accessed: Dict[str, int] = field(default_factory=dict)
    
class KeyAnalytics:
    """키 분석"""
    
    def __init__(self):
        self.metrics: Dict[str, KeyUsageMetrics] = {}
        self.hourly_stats: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        
    def record_usage(
        self,
        key_id: str,
        endpoint: str,
        success: bool,
        response_time: float
    ):
        """사용 기록"""
        if key_id not in self.metrics:
            self.metrics[key_id] = KeyUsageMetrics()
            
        metrics = self.metrics[key_id]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            
        metrics.last_used = datetime.utcnow()
        
        if endpoint not in metrics.endpoints_accessed:
            metrics.endpoints_accessed[endpoint] = 0
        metrics.endpoints_accessed[endpoint] += 1
        
        # 시간별 통계
        hour = datetime.utcnow().hour
        self.hourly_stats[key_id][hour] += 1
        
    def get_metrics(self, key_id: str) -> KeyUsageMetrics:
        """메트릭 조회"""
        return self.metrics.get(key_id, KeyUsageMetrics())
        
    def get_usage_report(
        self,
        key_id: str,
        period: timedelta = timedelta(days=30)
    ) -> Dict:
        """사용 리포트 생성"""
        metrics = self.get_metrics(key_id)
        
        return {
            "key_id": key_id,
            "period": period.days,
            "total_requests": metrics.total_requests,
            "success_rate": (
                metrics.successful_requests / metrics.total_requests * 100
                if metrics.total_requests > 0 else 0
            ),
            "last_used": metrics.last_used.isoformat() if metrics.last_used else None,
            "top_endpoints": sorted(
                metrics.endpoints_accessed.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "hourly_distribution": dict(self.hourly_stats[key_id])
        }
        
    def detect_anomalies(self, key_id: str) -> List[str]:
        """이상 탐지"""
        anomalies = []
        metrics = self.get_metrics(key_id)
        
        # 높은 실패율
        if metrics.total_requests > 100:
            failure_rate = metrics.failed_requests / metrics.total_requests
            if failure_rate > 0.1:
                anomalies.append(f"High failure rate: {failure_rate:.2%}")
                
        # 비정상적인 사용 패턴
        hourly = self.hourly_stats[key_id]
        if hourly:
            avg_hourly = sum(hourly.values()) / len(hourly)
            for hour, count in hourly.items():
                if count > avg_hourly * 3:
                    anomalies.append(f"Spike at hour {hour}: {count} requests")
                    
        return anomalies
```

**검증 기준**:
- [ ] API 키 생성
- [ ] 키 순환 시스템
- [ ] 키 검증
- [ ] 키 분석

---

## Task 6.20: Rate Limiting 및 Throttling

### Task 6.20.1: Token Bucket Algorithm

```python
# src/api/ratelimit/token_bucket.py
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time

@dataclass
class TokenBucket:
    """토큰 버킷"""
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float
    
class TokenBucketRateLimiter:
    """토큰 버킷 레이트 리미터"""
    
    def __init__(self, capacity: int = 100, refill_rate: float = 10):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, TokenBucket] = {}
        
    def _get_bucket(self, key: str) -> TokenBucket:
        """버킷 가져오기"""
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(
                capacity=self.capacity,
                refill_rate=self.refill_rate,
                tokens=self.capacity,
                last_refill=time.time()
            )
        return self.buckets[key]
        
    def _refill(self, bucket: TokenBucket):
        """토큰 리필"""
        now = time.time()
        time_passed = now - bucket.last_refill
        tokens_to_add = time_passed * bucket.refill_rate
        
        bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
        bucket.last_refill = now
        
    async def consume(
        self,
        key: str,
        tokens: int = 1
    ) -> tuple[bool, float]:
        """토큰 소비"""
        bucket = self._get_bucket(key)
        self._refill(bucket)
        
        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            return True, bucket.tokens
        
        # 대기 시간 계산
        tokens_needed = tokens - bucket.tokens
        wait_time = tokens_needed / bucket.refill_rate
        
        return False, wait_time
        
    def get_status(self, key: str) -> Dict:
        """상태 조회"""
        bucket = self._get_bucket(key)
        self._refill(bucket)
        
        return {
            "available_tokens": bucket.tokens,
            "capacity": bucket.capacity,
            "refill_rate": bucket.refill_rate
        }
```

### Task 6.20.2: Sliding Window Counter

```python
# src/api/ratelimit/sliding_window.py
from typing import Dict, List
from datetime import datetime, timedelta
from collections import deque
import time

class SlidingWindowRateLimiter:
    """슬라이딩 윈도우 레이트 리미터"""
    
    def __init__(
        self,
        window_size: timedelta = timedelta(minutes=1),
        max_requests: int = 60
    ):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: Dict[str, deque] = {}
        
    def _cleanup_old_requests(self, key: str):
        """오래된 요청 정리"""
        if key not in self.requests:
            self.requests[key] = deque()
            return
            
        cutoff = time.time() - self.window_size.total_seconds()
        
        while self.requests[key] and self.requests[key][0] < cutoff:
            self.requests[key].popleft()
            
    async def check_limit(self, key: str) -> tuple[bool, Dict]:
        """리밋 확인"""
        self._cleanup_old_requests(key)
        
        current_count = len(self.requests[key])
        
        if current_count < self.max_requests:
            self.requests[key].append(time.time())
            return True, {
                "allowed": True,
                "current": current_count + 1,
                "limit": self.max_requests,
                "remaining": self.max_requests - current_count - 1,
                "reset_at": datetime.utcnow() + self.window_size
            }
        
        # 다음 슬롯까지 대기 시간
        oldest_request = self.requests[key][0]
        reset_time = oldest_request + self.window_size.total_seconds()
        wait_time = reset_time - time.time()
        
        return False, {
            "allowed": False,
            "current": current_count,
            "limit": self.max_requests,
            "remaining": 0,
            "retry_after": wait_time,
            "reset_at": datetime.fromtimestamp(reset_time)
        }
        
    def get_usage(self, key: str) -> Dict:
        """사용량 조회"""
        self._cleanup_old_requests(key)
        
        current_count = len(self.requests.get(key, []))
        
        return {
            "current": current_count,
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - current_count),
            "window_size": self.window_size.total_seconds()
        }
```

### Task 6.20.3: Distributed Rate Limiting

```python
# src/api/ratelimit/distributed.py
import redis
from typing import Optional, Dict
import time
import json

class DistributedRateLimiter:
    """분산 레이트 리미터"""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        prefix: str = "ratelimit"
    ):
        self.redis = redis_client
        self.prefix = prefix
        
    async def check_limit(
        self,
        key: str,
        limit: int,
        window: int  # seconds
    ) -> tuple[bool, Dict]:
        """분산 리밋 확인"""
        redis_key = f"{self.prefix}:{key}"
        
        # Lua 스크립트로 원자적 실행
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        local current = redis.call('GET', key)
        if current == false then
            redis.call('SET', key, 1)
            redis.call('EXPIRE', key, window)
            return {1, 1, limit - 1}
        end
        
        current = tonumber(current)
        if current < limit then
            local new_value = redis.call('INCR', key)
            local ttl = redis.call('TTL', key)
            return {1, new_value, limit - new_value}
        else
            local ttl = redis.call('TTL', key)
            return {0, current, ttl}
        end
        """
        
        result = self.redis.eval(
            lua_script,
            1,
            redis_key,
            limit,
            window,
            int(time.time())
        )
        
        allowed, current, remaining_or_ttl = result
        
        if allowed:
            return True, {
                "allowed": True,
                "current": current,
                "limit": limit,
                "remaining": remaining_or_ttl
            }
        else:
            return False, {
                "allowed": False,
                "current": current,
                "limit": limit,
                "retry_after": remaining_or_ttl
            }
            
    async def reset(self, key: str):
        """카운터 리셋"""
        redis_key = f"{self.prefix}:{key}"
        self.redis.delete(redis_key)
        
    async def get_usage(self, pattern: str = "*") -> Dict[str, int]:
        """사용량 조회"""
        keys = self.redis.keys(f"{self.prefix}:{pattern}")
        usage = {}
        
        for key in keys:
            value = self.redis.get(key)
            if value:
                clean_key = key.decode().replace(f"{self.prefix}:", "")
                usage[clean_key] = int(value)
                
        return usage
```

### Task 6.20.4: Adaptive Throttling

```python
# src/api/ratelimit/adaptive.py
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

@dataclass
class SystemMetrics:
    """시스템 메트릭"""
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    
class AdaptiveThrottler:
    """적응형 스로틀러"""
    
    def __init__(self):
        self.base_limits: Dict[str, int] = {}
        self.current_limits: Dict[str, int] = {}
        self.metrics_history: List[SystemMetrics] = []
        self.adjustment_factor = 1.0
        
    def set_base_limit(self, key: str, limit: int):
        """기본 리밋 설정"""
        self.base_limits[key] = limit
        self.current_limits[key] = limit
        
    def update_metrics(self, metrics: SystemMetrics):
        """메트릭 업데이트"""
        self.metrics_history.append(metrics)
        
        # 최근 메트릭만 유지
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)
            
        # 조정 계수 계산
        self._calculate_adjustment_factor()
        
        # 리밋 조정
        self._adjust_limits()
        
    def _calculate_adjustment_factor(self):
        """조정 계수 계산"""
        if len(self.metrics_history) < 10:
            return
            
        recent_metrics = self.metrics_history[-10:]
        
        avg_cpu = statistics.mean(m.cpu_usage for m in recent_metrics)
        avg_memory = statistics.mean(m.memory_usage for m in recent_metrics)
        avg_response_time = statistics.mean(m.response_time for m in recent_metrics)
        avg_error_rate = statistics.mean(m.error_rate for m in recent_metrics)
        
        # 시스템 부하 점수 계산
        load_score = (
            avg_cpu * 0.3 +
            avg_memory * 0.2 +
            min(avg_response_time / 1000, 1.0) * 0.3 +
            avg_error_rate * 0.2
        )
        
        # 조정 계수 설정
        if load_score > 0.8:
            self.adjustment_factor = max(0.5, self.adjustment_factor - 0.1)
        elif load_score < 0.4:
            self.adjustment_factor = min(1.5, self.adjustment_factor + 0.1)
        else:
            self.adjustment_factor = 1.0
            
    def _adjust_limits(self):
        """리밋 조정"""
        for key, base_limit in self.base_limits.items():
            adjusted_limit = int(base_limit * self.adjustment_factor)
            self.current_limits[key] = max(1, adjusted_limit)
            
    def get_current_limit(self, key: str) -> int:
        """현재 리밋 조회"""
        return self.current_limits.get(key, self.base_limits.get(key, 100))
        
    def get_status(self) -> Dict:
        """상태 조회"""
        return {
            "adjustment_factor": self.adjustment_factor,
            "base_limits": self.base_limits,
            "current_limits": self.current_limits,
            "metrics_count": len(self.metrics_history)
        }
```

**검증 기준**:
- [ ] 토큰 버킷 알고리즘
- [ ] 슬라이딩 윈도우 카운터
- [ ] 분산 레이트 리미팅
- [ ] 적응형 스로틀링

---

## Task 6.21: API 캐싱 전략

### Task 6.21.1: Response Cache

```python
# src/api/cache/response_cache.py
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

@dataclass
class CacheEntry:
    """캐시 엔트리"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    hit_count: int = 0
    
class ResponseCache:
    """응답 캐시"""
    
    def __init__(self, default_ttl: timedelta = timedelta(minutes=5)):
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        
    def generate_key(
        self,
        method: str,
        path: str,
        params: Dict = None,
        headers: Dict = None
    ) -> str:
        """캐시 키 생성"""
        key_data = {
            "method": method,
            "path": path,
            "params": params or {},
            "headers": headers or {}
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
        
    async def get(
        self,
        key: str
    ) -> Optional[Any]:
        """캐시 조회"""
        entry = self.cache.get(key)
        
        if not entry:
            return None
            
        # 만료 확인
        if datetime.utcnow() > entry.expires_at:
            del self.cache[key]
            return None
            
        # 히트 카운트 증가
        entry.hit_count += 1
        
        return entry.value
        
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ):
        """캐시 저장"""
        ttl = ttl or self.default_ttl
        now = datetime.utcnow()
        
        self.cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl,
            hit_count=0
        )
        
    async def invalidate(self, pattern: str = "*"):
        """캐시 무효화"""
        if pattern == "*":
            self.cache.clear()
        else:
            keys_to_delete = [
                key for key in self.cache.keys()
                if self._match_pattern(key, pattern)
            ]
            for key in keys_to_delete:
                del self.cache[key]
```

### Task 6.21.2: CDN Integration

```python
# src/api/cache/cdn_integration.py
from typing import Dict, Optional, List
from dataclasses import dataclass
import aiohttp

@dataclass
class CDNConfig:
    """CDN 설정"""
    provider: str
    api_key: str
    zone_id: str
    base_url: str
    
class CDNManager:
    """CDN 관리자"""
    
    def __init__(self, config: CDNConfig):
        self.config = config
        self.session = None
        
    async def initialize(self):
        """초기화"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}"
            }
        )
        
    async def purge_cache(
        self,
        urls: List[str] = None,
        tags: List[str] = None
    ):
        """CDN 캐시 퍼지"""
        if self.config.provider == "cloudflare":
            return await self._purge_cloudflare(urls, tags)
        elif self.config.provider == "fastly":
            return await self._purge_fastly(urls, tags)
            
    async def _purge_cloudflare(
        self,
        urls: List[str] = None,
        tags: List[str] = None
    ):
        """Cloudflare 캐시 퍼지"""
        endpoint = f"https://api.cloudflare.com/client/v4/zones/{self.config.zone_id}/purge_cache"
        
        data = {}
        if urls:
            data["files"] = urls
        if tags:
            data["tags"] = tags
        if not data:
            data["purge_everything"] = True
            
        async with self.session.post(endpoint, json=data) as response:
            return await response.json()
            
    async def set_cache_headers(
        self,
        path: str,
        max_age: int,
        s_maxage: int = None
    ) -> Dict:
        """캐시 헤더 설정"""
        headers = {
            "Cache-Control": f"public, max-age={max_age}"
        }
        
        if s_maxage:
            headers["Cache-Control"] += f", s-maxage={s_maxage}"
            
        headers["CDN-Cache-Control"] = f"max-age={s_maxage or max_age}"
        
        return headers
```

### Task 6.21.3: Cache Invalidation

```python
# src/api/cache/invalidation.py
from typing import List, Dict, Set, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class InvalidationRule:
    """무효화 규칙"""
    name: str
    pattern: str
    dependencies: List[str]
    cascade: bool = False
    
class CacheInvalidator:
    """캐시 무효화기"""
    
    def __init__(self):
        self.rules: Dict[str, InvalidationRule] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.invalidation_queue: asyncio.Queue = asyncio.Queue()
        
    def add_rule(self, rule: InvalidationRule):
        """무효화 규칙 추가"""
        self.rules[rule.name] = rule
        
        # 의존성 맵핑
        for dep in rule.dependencies:
            if dep not in self.dependencies:
                self.dependencies[dep] = set()
            self.dependencies[dep].add(rule.name)
            
    async def invalidate(
        self,
        key: str,
        cascade: bool = True
    ):
        """캐시 무효화"""
        await self.invalidation_queue.put({
            "key": key,
            "cascade": cascade,
            "timestamp": datetime.utcnow()
        })
        
        if cascade:
            await self._cascade_invalidation(key)
            
    async def _cascade_invalidation(self, key: str):
        """계단식 무효화"""
        if key in self.dependencies:
            for dependent in self.dependencies[key]:
                await self.invalidation_queue.put({
                    "key": dependent,
                    "cascade": True,
                    "timestamp": datetime.utcnow()
                })
                
    async def process_invalidations(self):
        """무효화 처리"""
        while True:
            item = await self.invalidation_queue.get()
            
            # 실제 무효화 수행
            await self._perform_invalidation(item)
            
    async def _perform_invalidation(self, item: Dict):
        """실제 무효화 수행"""
        # 로컬 캐시 무효화
        # CDN 캐시 무효화
        # 데이터베이스 캐시 무효화
        pass
```

### Task 6.21.4: Edge Caching

```python
# src/api/cache/edge_cache.py
from typing import Dict, Optional, List
from dataclasses import dataclass
import asyncio

@dataclass
class EdgeLocation:
    """엣지 위치"""
    id: str
    region: str
    endpoint: str
    latency: float
    
class EdgeCacheManager:
    """엣지 캐시 관리자"""
    
    def __init__(self):
        self.locations: Dict[str, EdgeLocation] = {}
        self.cache_policies: Dict[str, Dict] = {}
        
    def add_location(self, location: EdgeLocation):
        """엣지 위치 추가"""
        self.locations[location.id] = location
        
    async def distribute_cache(
        self,
        key: str,
        value: Any,
        locations: List[str] = None
    ):
        """캐시 분산"""
        target_locations = locations or list(self.locations.keys())
        
        tasks = [
            self._push_to_edge(loc_id, key, value)
            for loc_id in target_locations
        ]
        
        await asyncio.gather(*tasks)
        
    async def _push_to_edge(
        self,
        location_id: str,
        key: str,
        value: Any
    ):
        """엣지로 푸시"""
        location = self.locations.get(location_id)
        if not location:
            return
            
        # 엣지 캐시 업데이트
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{location.endpoint}/cache",
                json={"key": key, "value": value}
            )
            
    def get_optimal_location(self, client_region: str) -> Optional[EdgeLocation]:
        """최적 위치 선택"""
        best_location = None
        min_latency = float('inf')
        
        for location in self.locations.values():
            if location.region == client_region:
                return location
                
            if location.latency < min_latency:
                min_latency = location.latency
                best_location = location
                
        return best_location
```

**검증 기준**:
- [ ] 응답 캐시
- [ ] CDN 통합
- [ ] 캐시 무효화
- [ ] 엣지 캐싱

---

## Task 6.22: 응답 압축 및 최적화

### Task 6.22.1: Compression Algorithms

```python
# src/api/compression/algorithms.py
import gzip
import brotli
import zlib
from typing import bytes, Optional, Dict
from enum import Enum

class CompressionType(Enum):
    """압축 타입"""
    GZIP = "gzip"
    BROTLI = "br"
    DEFLATE = "deflate"
    NONE = "identity"
    
class CompressionHandler:
    """압축 핸들러"""
    
    def __init__(self):
        self.algorithms = {
            CompressionType.GZIP: self._gzip_compress,
            CompressionType.BROTLI: self._brotli_compress,
            CompressionType.DEFLATE: self._deflate_compress
        }
        
    def compress(
        self,
        data: bytes,
        algorithm: CompressionType,
        level: int = 6
    ) -> bytes:
        """데이터 압축"""
        if algorithm == CompressionType.NONE:
            return data
            
        compressor = self.algorithms.get(algorithm)
        if not compressor:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
            
        return compressor(data, level)
        
    def _gzip_compress(self, data: bytes, level: int) -> bytes:
        """GZIP 압축"""
        return gzip.compress(data, compresslevel=level)
        
    def _brotli_compress(self, data: bytes, level: int) -> bytes:
        """Brotli 압축"""
        return brotli.compress(data, quality=level)
        
    def _deflate_compress(self, data: bytes, level: int) -> bytes:
        """Deflate 압축"""
        return zlib.compress(data, level)
        
    def decompress(
        self,
        data: bytes,
        algorithm: CompressionType
    ) -> bytes:
        """데이터 압축 해제"""
        if algorithm == CompressionType.GZIP:
            return gzip.decompress(data)
        elif algorithm == CompressionType.BROTLI:
            return brotli.decompress(data)
        elif algorithm == CompressionType.DEFLATE:
            return zlib.decompress(data)
        else:
            return data
            
    def get_compression_ratio(self, original: bytes, compressed: bytes) -> float:
        """압축률 계산"""
        return 1 - (len(compressed) / len(original))
```

### Task 6.22.2: Payload Optimization

```python
# src/api/compression/payload_optimizer.py
from typing import Dict, Any, List, Optional
import json

class PayloadOptimizer:
    """페이로드 최적화기"""
    
    def __init__(self):
        self.field_mappings: Dict[str, str] = {}
        self.excluded_fields: Set[str] = set()
        
    def optimize_json(
        self,
        data: Dict,
        minify: bool = True,
        exclude_nulls: bool = True
    ) -> str:
        """JSON 최적화"""
        optimized = self._optimize_dict(data, exclude_nulls)
        
        if minify:
            return json.dumps(optimized, separators=(',', ':'))
        else:
            return json.dumps(optimized)
            
    def _optimize_dict(
        self,
        data: Dict,
        exclude_nulls: bool
    ) -> Dict:
        """딕셔너리 최적화"""
        result = {}
        
        for key, value in data.items():
            # 제외 필드 확인
            if key in self.excluded_fields:
                continue
                
            # null 제외
            if exclude_nulls and value is None:
                continue
                
            # 필드 매핑
            mapped_key = self.field_mappings.get(key, key)
            
            # 재귀적 최적화
            if isinstance(value, dict):
                result[mapped_key] = self._optimize_dict(value, exclude_nulls)
            elif isinstance(value, list):
                result[mapped_key] = [
                    self._optimize_dict(item, exclude_nulls) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[mapped_key] = value
                
        return result
        
    def create_field_mapping(self, verbose_to_short: Dict[str, str]):
        """필드 매핑 생성"""
        self.field_mappings = verbose_to_short
        
    def batch_optimize(
        self,
        items: List[Dict],
        dedup: bool = True
    ) -> List[Dict]:
        """배치 최적화"""
        if dedup:
            # 중복 제거
            seen = set()
            unique_items = []
            
            for item in items:
                item_hash = hash(json.dumps(item, sort_keys=True))
                if item_hash not in seen:
                    seen.add(item_hash)
                    unique_items.append(item)
                    
            items = unique_items
            
        return [self._optimize_dict(item, True) for item in items]
```

### Task 6.22.3: Image Optimization

```python
# src/api/compression/image_optimizer.py
from PIL import Image
from typing import Tuple, Optional
import io

class ImageOptimizer:
    """이미지 최적화기"""
    
    def __init__(self):
        self.quality_presets = {
            "high": 95,
            "medium": 85,
            "low": 75,
            "thumbnail": 60
        }
        
    def optimize_image(
        self,
        image_data: bytes,
        format: str = "JPEG",
        quality: str = "medium",
        max_size: Optional[Tuple[int, int]] = None
    ) -> bytes:
        """이미지 최적화"""
        # 이미지 열기
        img = Image.open(io.BytesIO(image_data))
        
        # 크기 조정
        if max_size:
            img.thumbnail(max_size, Image.LANCZOS)
            
        # 최적화 옵션
        save_kwargs = {
            "format": format,
            "optimize": True
        }
        
        if format in ["JPEG", "WEBP"]:
            save_kwargs["quality"] = self.quality_presets.get(quality, 85)
            save_kwargs["progressive"] = True
            
        # 저장
        output = io.BytesIO()
        img.save(output, **save_kwargs)
        
        return output.getvalue()
        
    def convert_format(
        self,
        image_data: bytes,
        target_format: str
    ) -> bytes:
        """포맷 변환"""
        img = Image.open(io.BytesIO(image_data))
        
        output = io.BytesIO()
        img.save(output, format=target_format)
        
        return output.getvalue()
        
    def generate_responsive_images(
        self,
        image_data: bytes,
        sizes: List[Tuple[int, int]]
    ) -> Dict[str, bytes]:
        """반응형 이미지 생성"""
        img = Image.open(io.BytesIO(image_data))
        result = {}
        
        for width, height in sizes:
            resized = img.copy()
            resized.thumbnail((width, height), Image.LANCZOS)
            
            output = io.BytesIO()
            resized.save(output, format="WEBP", optimize=True, quality=85)
            
            result[f"{width}x{height}"] = output.getvalue()
            
        return result
```

### Task 6.22.4: Streaming Compression

```python
# src/api/compression/streaming.py
import asyncio
from typing import AsyncIterator, Optional
import gzip

class StreamingCompressor:
    """스트리밍 압축기"""
    
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        
    async def compress_stream(
        self,
        input_stream: AsyncIterator[bytes],
        algorithm: str = "gzip"
    ) -> AsyncIterator[bytes]:
        """스트림 압축"""
        if algorithm == "gzip":
            compressor = gzip.GzipFile(mode='wb')
            
            async for chunk in input_stream:
                compressed = compressor.compress(chunk)
                if compressed:
                    yield compressed
                    
            # 남은 데이터 플러시
            final = compressor.flush()
            if final:
                yield final
                
    async def decompress_stream(
        self,
        input_stream: AsyncIterator[bytes],
        algorithm: str = "gzip"
    ) -> AsyncIterator[bytes]:
        """스트림 압축 해제"""
        if algorithm == "gzip":
            decompressor = gzip.GzipFile(mode='rb')
            
            async for chunk in input_stream:
                decompressed = decompressor.decompress(chunk)
                if decompressed:
                    yield decompressed
                    
    async def adaptive_compression(
        self,
        input_stream: AsyncIterator[bytes],
        threshold: int = 1024
    ) -> AsyncIterator[bytes]:
        """적응형 압축"""
        buffer = b""
        
        async for chunk in input_stream:
            buffer += chunk
            
            if len(buffer) >= threshold:
                # 압축 효율 확인
                compressed = gzip.compress(buffer)
                
                if len(compressed) < len(buffer) * 0.9:
                    # 압축 효과가 있으면 압축
                    yield compressed
                else:
                    # 압축 효과가 없으면 원본
                    yield buffer
                    
                buffer = b""
                
        # 남은 데이터 처리
        if buffer:
            yield gzip.compress(buffer)
```

**검증 기준**:
- [ ] 압축 알고리즘
- [ ] 페이로드 최적화
- [ ] 이미지 최적화
- [ ] 스트리밍 압축

---

## Task 6.23: 비동기 처리 및 큐잉

### Task 6.23.1: Job Queue System

```python
# src/api/queue/job_queue.py
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid

class JobStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    """작업"""
    id: str
    type: str
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3

class JobQueue:
    """작업 큐"""
    
    def __init__(self):
        self.queues: Dict[str, asyncio.PriorityQueue] = {}
        self.jobs: Dict[str, Job] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def create_queue(self, name: str, max_size: int = 0):
        """큐 생성"""
        self.queues[name] = asyncio.PriorityQueue(maxsize=max_size)
        
    async def enqueue(
        self,
        queue_name: str,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 0
    ) -> str:
        """작업 추가"""
        job = Job(
            id=str(uuid.uuid4()),
            type=job_type,
            payload=payload,
            priority=priority
        )
        
        self.jobs[job.id] = job
        
        queue = self.queues.get(queue_name)
        if not queue:
            self.create_queue(queue_name)
            queue = self.queues[queue_name]
            
        await queue.put((-priority, job.created_at, job.id))
        
        return job.id
        
    async def dequeue(self, queue_name: str) -> Optional[Job]:
        """작업 가져오기"""
        queue = self.queues.get(queue_name)
        if not queue:
            return None
            
        try:
            _, _, job_id = await queue.get()
            return self.jobs.get(job_id)
        except asyncio.QueueEmpty:
            return None
            
    def register_handler(self, job_type: str, handler: Callable):
        """핸들러 등록"""
        self.handlers[job_type] = handler
        
    async def process_job(self, job: Job):
        """작업 처리"""
        handler = self.handlers.get(job.type)
        if not handler:
            job.status = JobStatus.FAILED
            job.error = f"No handler for job type: {job.type}"
            return
            
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        try:
            result = await handler(job.payload)
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.retries += 1
            
            if job.retries < job.max_retries:
                # 재시도
                job.status = JobStatus.PENDING
```

### Task 6.23.2: Background Workers

```python
# src/api/queue/workers.py
from typing import List, Dict, Optional
import asyncio
from dataclasses import dataclass

@dataclass
class WorkerConfig:
    """워커 설정"""
    name: str
    queue_name: str
    concurrency: int = 1
    poll_interval: float = 1.0
    
class Worker:
    """백그라운드 워커"""
    
    def __init__(self, config: WorkerConfig, job_queue: JobQueue):
        self.config = config
        self.job_queue = job_queue
        self.running = False
        self.tasks: List[asyncio.Task] = []
        
    async def start(self):
        """워커 시작"""
        self.running = True
        
        for i in range(self.config.concurrency):
            task = asyncio.create_task(
                self._worker_loop(f"{self.config.name}-{i}")
            )
            self.tasks.append(task)
            
    async def stop(self):
        """워커 중지"""
        self.running = False
        
        for task in self.tasks:
            task.cancel()
            
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        
    async def _worker_loop(self, worker_id: str):
        """워커 루프"""
        while self.running:
            try:
                job = await self.job_queue.dequeue(self.config.queue_name)
                
                if job:
                    await self.job_queue.process_job(job)
                else:
                    await asyncio.sleep(self.config.poll_interval)
                    
            except Exception as e:
                # 에러 로깅
                await asyncio.sleep(self.config.poll_interval)

class WorkerPool:
    """워커 풀"""
    
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        
    def add_worker(self, worker: Worker):
        """워커 추가"""
        self.workers[worker.config.name] = worker
        
    async def start_all(self):
        """모든 워커 시작"""
        for worker in self.workers.values():
            await worker.start()
            
    async def stop_all(self):
        """모든 워커 중지"""
        for worker in self.workers.values():
            await worker.stop()
            
    def scale_worker(self, name: str, concurrency: int):
        """워커 스케일링"""
        worker = self.workers.get(name)
        if worker:
            worker.config.concurrency = concurrency
```

### Task 6.23.3: Event Bus

```python
# src/api/queue/event_bus.py
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
import asyncio

@dataclass
class Event:
    """이벤트"""
    type: str
    data: Any
    source: str
    timestamp: datetime
    
class EventBus:
    """이벤트 버스"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.filters: Dict[str, Callable] = {}
        
    def subscribe(
        self,
        event_type: str,
        handler: Callable,
        filter_func: Optional[Callable] = None
    ):
        """이벤트 구독"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        self.subscribers[event_type].append(handler)
        
        if filter_func:
            handler_id = id(handler)
            self.filters[handler_id] = filter_func
            
    def unsubscribe(self, event_type: str, handler: Callable):
        """구독 해제"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            
        handler_id = id(handler)
        if handler_id in self.filters:
            del self.filters[handler_id]
            
    async def publish(
        self,
        event_type: str,
        data: Any,
        source: str = "system"
    ):
        """이벤트 발행"""
        event = Event(
            type=event_type,
            data=data,
            source=source,
            timestamp=datetime.utcnow()
        )
        
        await self.event_queue.put(event)
        
    async def process_events(self):
        """이벤트 처리"""
        while True:
            event = await self.event_queue.get()
            
            handlers = self.subscribers.get(event.type, [])
            
            for handler in handlers:
                # 필터 확인
                handler_id = id(handler)
                filter_func = self.filters.get(handler_id)
                
                if filter_func and not filter_func(event):
                    continue
                    
                # 비동기 처리
                asyncio.create_task(self._handle_event(handler, event))
                
    async def _handle_event(self, handler: Callable, event: Event):
        """이벤트 핸들링"""
        try:
            await handler(event)
        except Exception as e:
            # 에러 처리
            await self.publish(
                "event.error",
                {"event": event, "error": str(e)},
                "event_bus"
            )
```

### Task 6.23.4: Dead Letter Queue

```python
# src/api/queue/dead_letter.py
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DeadLetter:
    """데드 레터"""
    id: str
    original_queue: str
    job: Job
    error: str
    attempts: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
class DeadLetterQueue:
    """데드 레터 큐"""
    
    def __init__(self, max_size: int = 10000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.letters: Dict[str, DeadLetter] = {}
        self.retry_policies: Dict[str, Dict] = {}
        
    async def add(
        self,
        job: Job,
        queue_name: str,
        error: str
    ):
        """데드 레터 추가"""
        letter = DeadLetter(
            id=str(uuid.uuid4()),
            original_queue=queue_name,
            job=job,
            error=error,
            attempts=job.retries
        )
        
        self.letters[letter.id] = letter
        await self.queue.put(letter)
        
    async def retry(
        self,
        letter_id: str,
        job_queue: JobQueue
    ) -> bool:
        """재시도"""
        letter = self.letters.get(letter_id)
        if not letter:
            return False
            
        # 재시도 정책 확인
        policy = self.retry_policies.get(letter.job.type, {})
        max_retries = policy.get("max_retries", 3)
        
        if letter.attempts >= max_retries:
            return False
            
        # 작업 재추가
        await job_queue.enqueue(
            letter.original_queue,
            letter.job.type,
            letter.job.payload,
            letter.job.priority
        )
        
        # DLQ에서 제거
        del self.letters[letter_id]
        
        return True
        
    async def process_dlq(self, job_queue: JobQueue):
        """DLQ 처리"""
        while True:
            try:
                letter = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=10.0
                )
                
                # 재시도 정책에 따라 처리
                policy = self.retry_policies.get(letter.job.type, {})
                
                if policy.get("auto_retry", False):
                    delay = policy.get("retry_delay", 60)
                    await asyncio.sleep(delay)
                    await self.retry(letter.id, job_queue)
                    
            except asyncio.TimeoutError:
                continue
                
    def get_statistics(self) -> Dict:
        """통계 조회"""
        stats = {
            "total": len(self.letters),
            "by_queue": {},
            "by_type": {},
            "by_error": {}
        }
        
        for letter in self.letters.values():
            # 큐별 통계
            queue = letter.original_queue
            stats["by_queue"][queue] = stats["by_queue"].get(queue, 0) + 1
            
            # 타입별 통계
            job_type = letter.job.type
            stats["by_type"][job_type] = stats["by_type"].get(job_type, 0) + 1
            
            # 에러별 통계
            error = letter.error[:50]  # 에러 메시지 축약
            stats["by_error"][error] = stats["by_error"].get(error, 0) + 1
            
        return stats
```

**검증 기준**:
- [ ] 작업 큐 시스템
- [ ] 백그라운드 워커
- [ ] 이벤트 버스
- [ ] 데드 레터 큐

---

## Task 6.24: API 문서 자동 생성 (OpenAPI/Swagger)

### Task 6.24.1: OpenAPI Schema Generation

```python
# src/api/docs/openapi_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import inspect

@dataclass
class OpenAPIInfo:
    """OpenAPI 정보"""
    title: str
    version: str
    description: str
    contact: Dict = None
    license: Dict = None
    
class OpenAPIGenerator:
    """OpenAPI 스키마 생성기"""
    
    def __init__(self, info: OpenAPIInfo):
        self.info = info
        self.paths: Dict[str, Dict] = {}
        self.components: Dict[str, Any] = {
            "schemas": {},
            "securitySchemes": {},
            "parameters": {}
        }
        
    def generate_schema(self) -> Dict:
        """OpenAPI 스키마 생성"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.info.title,
                "version": self.info.version,
                "description": self.info.description,
                "contact": self.info.contact,
                "license": self.info.license
            },
            "paths": self.paths,
            "components": self.components
        }
        
    def add_path(
        self,
        path: str,
        method: str,
        operation: Dict
    ):
        """경로 추가"""
        if path not in self.paths:
            self.paths[path] = {}
            
        self.paths[path][method.lower()] = operation
        
    def add_schema(self, name: str, schema: Dict):
        """스키마 추가"""
        self.components["schemas"][name] = schema
        
    def generate_from_function(self, func: Callable) -> Dict:
        """함수에서 생성"""
        signature = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        
        operation = {
            "summary": doc.split("\n")[0] if doc else func.__name__,
            "description": doc,
            "parameters": [],
            "responses": {}
        }
        
        # 파라미터 추출
        for param_name, param in signature.parameters.items():
            if param_name in ["self", "cls"]:
                continue
                
            param_schema = self._get_param_schema(param)
            operation["parameters"].append({
                "name": param_name,
                "in": "query",
                "schema": param_schema,
                "required": param.default == inspect.Parameter.empty
            })
            
        # 응답 스키마
        return_annotation = signature.return_annotation
        if return_annotation != inspect.Signature.empty:
            operation["responses"]["200"] = {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": self._get_type_schema(return_annotation)
                    }
                }
            }
            
        return operation
        
    def _get_param_schema(self, param: inspect.Parameter) -> Dict:
        """파라미터 스키마 가져오기"""
        if param.annotation != inspect.Parameter.empty:
            return self._get_type_schema(param.annotation)
        return {"type": "string"}
        
    def _get_type_schema(self, type_hint: Any) -> Dict:
        """타입 스키마 가져오기"""
        if type_hint == str:
            return {"type": "string"}
        elif type_hint == int:
            return {"type": "integer"}
        elif type_hint == float:
            return {"type": "number"}
        elif type_hint == bool:
            return {"type": "boolean"}
        elif hasattr(type_hint, "__origin__"):
            # Generic types
            if type_hint.__origin__ == list:
                return {
                    "type": "array",
                    "items": self._get_type_schema(type_hint.__args__[0])
                }
            elif type_hint.__origin__ == dict:
                return {"type": "object"}
        return {"type": "object"}
```

### Task 6.24.2: Swagger UI Integration

```python
# src/api/docs/swagger_ui.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

class SwaggerUI:
    """Swagger UI 통합"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()
        
    def setup_routes(self):
        """라우트 설정"""
        
        @self.app.get("/docs", include_in_schema=False)
        async def swagger_ui():
            return get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=f"{self.app.title} - Swagger UI",
                oauth2_redirect_url="/docs/oauth2-redirect",
                swagger_js_url="/static/swagger-ui-bundle.js",
                swagger_css_url="/static/swagger-ui.css"
            )
            
        @self.app.get("/openapi.json", include_in_schema=False)
        async def openapi_schema():
            return self.get_openapi_schema()
            
    def get_openapi_schema(self) -> Dict:
        """OpenAPI 스키마 가져오기"""
        if not self.app.openapi_schema:
            self.app.openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description,
                routes=self.app.routes
            )
        return self.app.openapi_schema
        
    def customize_swagger_ui(
        self,
        theme: str = "default",
        custom_css: str = None
    ):
        """Swagger UI 커스터마이징"""
        
        @self.app.get("/static/custom.css")
        async def custom_css_endpoint():
            css = custom_css or self._get_theme_css(theme)
            return Response(content=css, media_type="text/css")
            
    def _get_theme_css(self, theme: str) -> str:
        """테마 CSS 가져오기"""
        themes = {
            "dark": """
                .swagger-ui { background: #1a1a1a; }
                .swagger-ui .topbar { background: #2a2a2a; }
            """,
            "blue": """
                .swagger-ui .topbar { background: #0066cc; }
            """
        }
        return themes.get(theme, "")
```

### Task 6.24.3: Example Generation

```python
# src/api/docs/example_generator.py
from typing import Dict, Any, List
import random
import string
from datetime import datetime

class ExampleGenerator:
    """예제 생성기"""
    
    def __init__(self):
        self.type_generators = {
            "string": self._generate_string,
            "integer": self._generate_integer,
            "number": self._generate_number,
            "boolean": self._generate_boolean,
            "array": self._generate_array,
            "object": self._generate_object
        }
        
    def generate_example(self, schema: Dict) -> Any:
        """예제 생성"""
        if "example" in schema:
            return schema["example"]
            
        if "enum" in schema:
            return random.choice(schema["enum"])
            
        schema_type = schema.get("type", "string")
        generator = self.type_generators.get(schema_type)
        
        if generator:
            return generator(schema)
            
        return None
        
    def _generate_string(self, schema: Dict) -> str:
        """문자열 생성"""
        if schema.get("format") == "date":
            return datetime.utcnow().date().isoformat()
        elif schema.get("format") == "date-time":
            return datetime.utcnow().isoformat()
        elif schema.get("format") == "email":
            return "user@example.com"
        elif schema.get("format") == "uuid":
            return str(uuid.uuid4())
            
        min_length = schema.get("minLength", 5)
        max_length = schema.get("maxLength", 20)
        length = random.randint(min_length, max_length)
        
        return ''.join(random.choices(string.ascii_letters, k=length))
        
    def _generate_integer(self, schema: Dict) -> int:
        """정수 생성"""
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 100)
        return random.randint(minimum, maximum)
        
    def _generate_number(self, schema: Dict) -> float:
        """숫자 생성"""
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 100.0)
        return random.uniform(minimum, maximum)
        
    def _generate_boolean(self, schema: Dict) -> bool:
        """불린 생성"""
        return random.choice([True, False])
        
    def _generate_array(self, schema: Dict) -> List:
        """배열 생성"""
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 5)
        count = random.randint(min_items, max_items)
        
        return [
            self.generate_example(items_schema)
            for _ in range(count)
        ]
        
    def _generate_object(self, schema: Dict) -> Dict:
        """객체 생성"""
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        result = {}
        
        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.random() > 0.5:
                result[prop_name] = self.generate_example(prop_schema)
                
        return result
```

### Task 6.24.4: API Versioning Docs

```python
# src/api/docs/versioning.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class APIVersion:
    """API 버전"""
    version: str
    status: str  # current, deprecated, sunset
    released_at: datetime
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    changes: List[str] = None
    
class VersioningDocumentation:
    """버전 문서화"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.current_version: str = None
        
    def add_version(self, version: APIVersion):
        """버전 추가"""
        self.versions[version.version] = version
        
        if version.status == "current":
            self.current_version = version.version
            
    def generate_version_docs(self) -> Dict:
        """버전 문서 생성"""
        return {
            "current": self.current_version,
            "versions": [
                {
                    "version": v.version,
                    "status": v.status,
                    "released": v.released_at.isoformat(),
                    "deprecated": v.deprecated_at.isoformat() if v.deprecated_at else None,
                    "sunset": v.sunset_at.isoformat() if v.sunset_at else None,
                    "changes": v.changes or []
                }
                for v in self.versions.values()
            ]
        }
        
    def generate_migration_guide(
        self,
        from_version: str,
        to_version: str
    ) -> Dict:
        """마이그레이션 가이드 생성"""
        guide = {
            "from": from_version,
            "to": to_version,
            "breaking_changes": [],
            "deprecations": [],
            "new_features": []
        }
        
        # 변경 사항 수집
        from_v = self.versions.get(from_version)
        to_v = self.versions.get(to_version)
        
        if from_v and to_v:
            # 버전 간 변경 사항 분석
            guide["changes"] = to_v.changes or []
            
        return guide
        
    def check_version_compatibility(
        self,
        client_version: str,
        api_version: str
    ) -> Dict:
        """버전 호환성 확인"""
        client_v = self.versions.get(client_version)
        api_v = self.versions.get(api_version)
        
        if not client_v or not api_v:
            return {"compatible": False, "reason": "Unknown version"}
            
        if client_v.status == "sunset":
            return {"compatible": False, "reason": "Client version is sunset"}
            
        # 호환성 규칙 확인
        major_client = int(client_version.split(".")[0])
        major_api = int(api_version.split(".")[0])
        
        if major_client != major_api:
            return {"compatible": False, "reason": "Major version mismatch"}
            
        return {"compatible": True}
```

**검증 기준**:
- [ ] OpenAPI 스키마 생성
- [ ] Swagger UI 통합
- [ ] 예제 생성
- [ ] API 버전 문서

---

## Task 6.25: API 테스트 자동화

### Task 6.25.1: Contract Testing

```python
# src/api/testing/contract_testing.py
from typing import Dict, List, Any
from dataclasses import dataclass
import jsonschema

@dataclass
class Contract:
    """API 계약"""
    name: str
    request_schema: Dict
    response_schema: Dict
    headers: Dict = None
    
class ContractTester:
    """계약 테스터"""
    
    def __init__(self):
        self.contracts: Dict[str, Contract] = {}
        self.test_results: List[Dict] = []
        
    def add_contract(self, contract: Contract):
        """계약 추가"""
        self.contracts[contract.name] = contract
        
    async def test_contract(
        self,
        contract_name: str,
        request_data: Dict,
        response_data: Dict
    ) -> Dict:
        """계약 테스트"""
        contract = self.contracts.get(contract_name)
        if not contract:
            return {"passed": False, "error": "Contract not found"}
            
        result = {
            "contract": contract_name,
            "passed": True,
            "errors": []
        }
        
        # 요청 검증
        try:
            jsonschema.validate(request_data, contract.request_schema)
        except jsonschema.ValidationError as e:
            result["passed"] = False
            result["errors"].append(f"Request validation failed: {e.message}")
            
        # 응답 검증
        try:
            jsonschema.validate(response_data, contract.response_schema)
        except jsonschema.ValidationError as e:
            result["passed"] = False
            result["errors"].append(f"Response validation failed: {e.message}")
            
        self.test_results.append(result)
        return result
        
    def generate_contract_from_openapi(self, openapi_spec: Dict) -> List[Contract]:
        """OpenAPI에서 계약 생성"""
        contracts = []
        
        for path, methods in openapi_spec.get("paths", {}).items():
            for method, operation in methods.items():
                contract = Contract(
                    name=f"{method.upper()} {path}",
                    request_schema=self._extract_request_schema(operation),
                    response_schema=self._extract_response_schema(operation)
                )
                contracts.append(contract)
                
        return contracts
```

### Task 6.25.2: Load Testing

```python
# src/api/testing/load_testing.py
from typing import Dict, List, Callable
from dataclasses import dataclass
import asyncio
import time
import statistics

@dataclass
class LoadTestConfig:
    """부하 테스트 설정"""
    url: str
    duration: int  # seconds
    users: int
    ramp_up: int  # seconds
    
class LoadTester:
    """부하 테스터"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[Dict] = []
        self.errors: List[str] = []
        
    async def run_test(self, test_func: Callable) -> Dict:
        """테스트 실행"""
        start_time = time.time()
        end_time = start_time + self.config.duration
        
        # 사용자 램프업
        tasks = []
        for i in range(self.config.users):
            delay = (self.config.ramp_up / self.config.users) * i
            task = asyncio.create_task(
                self._user_simulation(test_func, start_time + delay, end_time)
            )
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        
        return self._analyze_results()
        
    async def _user_simulation(
        self,
        test_func: Callable,
        start_time: float,
        end_time: float
    ):
        """사용자 시뮬레이션"""
        await asyncio.sleep(max(0, start_time - time.time()))
        
        while time.time() < end_time:
            request_start = time.time()
            
            try:
                await test_func()
                response_time = time.time() - request_start
                
                self.results.append({
                    "timestamp": request_start,
                    "response_time": response_time,
                    "success": True
                })
            except Exception as e:
                self.errors.append(str(e))
                self.results.append({
                    "timestamp": request_start,
                    "response_time": time.time() - request_start,
                    "success": False
                })
                
    def _analyze_results(self) -> Dict:
        """결과 분석"""
        if not self.results:
            return {"error": "No results"}
            
        response_times = [r["response_time"] for r in self.results if r["success"]]
        success_count = sum(1 for r in self.results if r["success"])
        
        return {
            "total_requests": len(self.results),
            "successful_requests": success_count,
            "failed_requests": len(self.results) - success_count,
            "error_rate": (len(self.results) - success_count) / len(self.results) * 100,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "percentiles": {
                "p50": statistics.median(response_times) if response_times else 0,
                "p95": self._percentile(response_times, 95) if response_times else 0,
                "p99": self._percentile(response_times, 99) if response_times else 0
            },
            "requests_per_second": len(self.results) / self.config.duration
        }
        
    def _percentile(self, data: List[float], percentile: int) -> float:
        """백분위수 계산"""
        size = len(data)
        if size == 0:
            return 0
        sorted_data = sorted(data)
        index = int(size * (percentile / 100))
        return sorted_data[min(index, size - 1)]
```

### Task 6.25.3: Security Testing

```python
# src/api/testing/security_testing.py
from typing import Dict, List, Optional
import re

class SecurityTester:
    """보안 테스터"""
    
    def __init__(self):
        self.vulnerability_checks = {
            "sql_injection": self._check_sql_injection,
            "xss": self._check_xss,
            "csrf": self._check_csrf,
            "auth": self._check_authentication,
            "rate_limiting": self._check_rate_limiting
        }
        
    async def run_security_tests(self, endpoint: str) -> Dict:
        """보안 테스트 실행"""
        results = {
            "endpoint": endpoint,
            "vulnerabilities": [],
            "passed": True
        }
        
        for check_name, check_func in self.vulnerability_checks.items():
            result = await check_func(endpoint)
            
            if not result["passed"]:
                results["passed"] = False
                results["vulnerabilities"].append({
                    "type": check_name,
                    "details": result["details"]
                })
                
        return results
        
    async def _check_sql_injection(self, endpoint: str) -> Dict:
        """SQL 인젝션 확인"""
        payloads = [
            "' OR '1'='1",
            "1; DROP TABLE users--",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in payloads:
            # 테스트 요청 전송
            # 응답 분석
            pass
            
        return {"passed": True, "details": None}
        
    async def _check_xss(self, endpoint: str) -> Dict:
        """XSS 확인"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        for payload in payloads:
            # 테스트 요청 전송
            # 응답에서 페이로드 확인
            pass
            
        return {"passed": True, "details": None}
        
    async def _check_csrf(self, endpoint: str) -> Dict:
        """CSRF 확인"""
        # CSRF 토큰 확인
        # Referer 헤더 확인
        return {"passed": True, "details": None}
        
    async def _check_authentication(self, endpoint: str) -> Dict:
        """인증 확인"""
        # 인증 없이 접근 시도
        # 잘못된 토큰으로 접근 시도
        return {"passed": True, "details": None}
        
    async def _check_rate_limiting(self, endpoint: str) -> Dict:
        """레이트 리미팅 확인"""
        # 다수의 요청 전송
        # 응답 확인
        return {"passed": True, "details": None}
```

### Task 6.25.4: Smoke Testing

```python
# src/api/testing/smoke_testing.py
from typing import Dict, List, Optional
import asyncio
import aiohttp

@dataclass
class SmokeTest:
    """스모크 테스트"""
    name: str
    endpoint: str
    method: str = "GET"
    expected_status: int = 200
    timeout: float = 5.0
    
class SmokeTester:
    """스모크 테스터"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.tests: List[SmokeTest] = []
        self.results: List[Dict] = []
        
    def add_test(self, test: SmokeTest):
        """테스트 추가"""
        self.tests.append(test)
        
    async def run_all_tests(self) -> Dict:
        """모든 테스트 실행"""
        tasks = [self._run_test(test) for test in self.tests]
        results = await asyncio.gather(*tasks)
        
        passed = sum(1 for r in results if r["passed"])
        failed = len(results) - passed
        
        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(results) * 100) if results else 0,
            "results": results
        }
        
    async def _run_test(self, test: SmokeTest) -> Dict:
        """개별 테스트 실행"""
        result = {
            "test": test.name,
            "passed": False,
            "response_time": None,
            "error": None
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                async with session.request(
                    test.method,
                    f"{self.base_url}{test.endpoint}",
                    timeout=aiohttp.ClientTimeout(total=test.timeout)
                ) as response:
                    result["response_time"] = time.time() - start_time
                    
                    if response.status == test.expected_status:
                        result["passed"] = True
                    else:
                        result["error"] = f"Expected {test.expected_status}, got {response.status}"
                        
        except asyncio.TimeoutError:
            result["error"] = "Request timeout"
        except Exception as e:
            result["error"] = str(e)
            
        self.results.append(result)
        return result
        
    def generate_report(self) -> str:
        """테스트 리포트 생성"""
        report = ["Smoke Test Report", "=" * 50]
        
        for result in self.results:
            status = "✓" if result["passed"] else "✗"
            report.append(f"{status} {result['test']}")
            
            if result["response_time"]:
                report.append(f"  Response time: {result['response_time']:.3f}s")
                
            if result["error"]:
                report.append(f"  Error: {result['error']}")
                
        return "\n".join(report)
```

**검증 기준**:
- [ ] 계약 테스트
- [ ] 부하 테스트
- [ ] 보안 테스트
- [ ] 스모크 테스트

---

