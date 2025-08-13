# ⚡ Performance Optimization Strategy

## 개요

T-Developer 플랫폼의 대규모 확장성과 고성능을 보장하기 위한 종합적인 성능 최적화 전략입니다. 캐싱, 데이터베이스 최적화, 네트워크 최적화, 애플리케이션 최적화를 포함한 다층 접근 방식을 제공합니다.

## 🎯 성능 목표

### 1. 응답 시간 목표
```yaml
API 응답 시간:
  P50: < 100ms
  P95: < 200ms  
  P99: < 500ms
  P99.9: < 1000ms

Agent 실행 시간:
  Cold Start: < 2초
  Warm Start: < 100ms
  
Database 쿼리:
  Simple Queries: < 10ms
  Complex Queries: < 100ms
  Analytics Queries: < 1초
```

### 2. 처리량 목표
```yaml
API 처리량:
  Peak Load: 10,000 req/sec
  Sustained Load: 5,000 req/sec
  
Agent 실행:
  Concurrent Executions: 50,000+
  Agent Instantiation: 1,000/sec
  
Database:
  Read Operations: 100,000 ops/sec
  Write Operations: 10,000 ops/sec
```

### 3. 리소스 효율성 목표
```yaml
메모리 사용량:
  Agent Memory: < 6.5KB (Agno Framework)
  API Server: < 2GB per instance
  Database: < 80% of allocated memory

CPU 사용량:
  Normal Load: < 60%
  Peak Load: < 80%
  
Network:
  Bandwidth Utilization: < 70%
  Connection Pool: 90%+ efficiency
```

## 🏗️ 다층 캐싱 아키텍처

### Layer 1: In-Memory Caching (L1)

#### 1.1 Application-Level 캐시
```python
# backend/src/cache/l1_memory_cache.py

import asyncio
import time
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from collections import OrderedDict
import threading

@dataclass
class CacheEntry:
    value: Any
    expires_at: float
    hit_count: int = 0
    last_accessed: float = 0.0

class L1MemoryCache:
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0
        }
        
        # Background cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_expired())
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        with self.lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # 만료 확인
            if time.time() > entry.expires_at:
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            # 통계 업데이트
            entry.hit_count += 1
            entry.last_accessed = time.time()
            self.stats["hits"] += 1
            
            # LRU 업데이트
            self.cache.move_to_end(key)
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """캐시에 값 저장"""
        with self.lock:
            expires_at = time.time() + (ttl or self.default_ttl)
            
            # 용량 초과 시 LRU 제거
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at,
                last_accessed=time.time()
            )
            self.cache.move_to_end(key)
            self.stats["sets"] += 1
    
    def _evict_lru(self) -> None:
        """LRU 제거"""
        if self.cache:
            self.cache.popitem(last=False)
            self.stats["evictions"] += 1
    
    async def _cleanup_expired(self) -> None:
        """만료된 항목 정리"""
        while True:
            await asyncio.sleep(60)  # 1분마다 정리
            
            with self.lock:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.cache.items()
                    if current_time > entry.expires_at
                ]
                
                for key in expired_keys:
                    del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "hit_rate": hit_rate,
                "stats": self.stats.copy()
            }
```

#### 1.2 Agent Code 캐싱
```python
# backend/src/cache/agent_code_cache.py

import hashlib
import pickle
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CompiledAgent:
    bytecode: bytes
    metadata: Dict[str, Any]
    compiled_at: float
    dependencies: Dict[str, str]  # dependency -> version

class AgentCodeCache:
    def __init__(self):
        self.compiled_agents: Dict[str, CompiledAgent] = {}
        self.code_hashes: Dict[str, str] = {}  # agent_id -> code_hash
    
    def get_compiled_agent(self, agent_id: str, code: str) -> Optional[CompiledAgent]:
        """컴파일된 에이전트 조회"""
        code_hash = self._calculate_code_hash(code)
        
        # 코드 변경 확인
        if agent_id in self.code_hashes:
            if self.code_hashes[agent_id] != code_hash:
                # 코드가 변경됨, 캐시 무효화
                self._invalidate_agent(agent_id)
                return None
        
        return self.compiled_agents.get(agent_id)
    
    def cache_compiled_agent(self, agent_id: str, code: str, 
                           compiled_agent: CompiledAgent) -> None:
        """컴파일된 에이전트 캐싱"""
        code_hash = self._calculate_code_hash(code)
        self.code_hashes[agent_id] = code_hash
        self.compiled_agents[agent_id] = compiled_agent
    
    def _calculate_code_hash(self, code: str) -> str:
        """코드 해시 계산"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _invalidate_agent(self, agent_id: str) -> None:
        """에이전트 캐시 무효화"""
        if agent_id in self.compiled_agents:
            del self.compiled_agents[agent_id]
        if agent_id in self.code_hashes:
            del self.code_hashes[agent_id]
```

### Layer 2: Distributed Cache (L2)

#### 2.1 Redis 클러스터 캐싱
```python
# backend/src/cache/l2_redis_cache.py

import asyncio
import json
import pickle
import redis.asyncio as redis
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass
class RedisClusterConfig:
    nodes: List[Dict[str, Any]]
    password: Optional[str] = None
    ssl: bool = True
    max_connections: int = 100
    retry_on_timeout: bool = True

class L2RedisCache:
    def __init__(self, config: RedisClusterConfig):
        self.config = config
        self.redis_cluster = None
        self.serialization_methods = {
            "json": (json.dumps, json.loads),
            "pickle": (pickle.dumps, pickle.loads)
        }
    
    async def initialize(self):
        """Redis 클러스터 초기화"""
        startup_nodes = [
            redis.RedisCluster.ClusterNode(
                host=node["host"], 
                port=node["port"]
            ) for node in self.config.nodes
        ]
        
        self.redis_cluster = redis.RedisCluster(
            startup_nodes=startup_nodes,
            password=self.config.password,
            ssl=self.config.ssl,
            max_connections=self.config.max_connections,
            retry_on_timeout=self.config.retry_on_timeout,
            decode_responses=False  # 바이너리 데이터 지원
        )
    
    async def get(self, key: str, serialization: str = "json") -> Optional[Any]:
        """분산 캐시에서 값 조회"""
        try:
            raw_value = await self.redis_cluster.get(key)
            if raw_value is None:
                return None
            
            serializer, deserializer = self.serialization_methods[serialization]
            return deserializer(raw_value)
            
        except Exception as e:
            # 캐시 실패 시 None 반환 (graceful degradation)
            print(f"Redis cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600, 
                 serialization: str = "json") -> bool:
        """분산 캐시에 값 저장"""
        try:
            serializer, deserializer = self.serialization_methods[serialization]
            serialized_value = serializer(value)
            
            await self.redis_cluster.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            print(f"Redis cache set error: {e}")
            return False
    
    async def mget(self, keys: List[str], serialization: str = "json") -> Dict[str, Any]:
        """다중 키 조회"""
        try:
            raw_values = await self.redis_cluster.mget(keys)
            serializer, deserializer = self.serialization_methods[serialization]
            
            result = {}
            for key, raw_value in zip(keys, raw_values):
                if raw_value is not None:
                    result[key] = deserializer(raw_value)
            
            return result
            
        except Exception as e:
            print(f"Redis cache mget error: {e}")
            return {}
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """패턴 매칭으로 캐시 무효화"""
        try:
            # 모든 노드에서 패턴 매칭 키 검색
            keys_to_delete = []
            for node in self.redis_cluster.get_nodes():
                async for key in node.scan_iter(match=pattern):
                    keys_to_delete.append(key)
            
            if keys_to_delete:
                deleted = await self.redis_cluster.delete(*keys_to_delete)
                return deleted
            
            return 0
            
        except Exception as e:
            print(f"Redis cache invalidation error: {e}")
            return 0
```

#### 2.2 지능형 캐시 전략
```python
# backend/src/cache/intelligent_cache_strategy.py

import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class CacheStrategy(Enum):
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"

@dataclass
class CachePolicy:
    strategy: CacheStrategy
    ttl: int
    refresh_threshold: float = 0.8  # TTL의 80%에서 백그라운드 새로고침
    max_stale_time: int = 300  # 최대 5분 동안 stale 데이터 허용

class IntelligentCacheManager:
    def __init__(self, l1_cache: L1MemoryCache, l2_cache: L2RedisCache):
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache
        self.policies: Dict[str, CachePolicy] = {}
        self.refresh_queue = asyncio.Queue()
        
        # 백그라운드 새로고침 워커 시작
        asyncio.create_task(self._refresh_worker())
    
    def set_policy(self, key_pattern: str, policy: CachePolicy):
        """키 패턴별 캐시 정책 설정"""
        self.policies[key_pattern] = policy
    
    async def get(self, key: str, fetch_func: Callable = None) -> Optional[Any]:
        """다층 캐시에서 값 조회"""
        # L1 캐시 확인
        value = self.l1_cache.get(key)
        if value is not None:
            await self._check_refresh_ahead(key, fetch_func)
            return value
        
        # L2 캐시 확인
        value = await self.l2_cache.get(key)
        if value is not None:
            # L1에 승격
            policy = self._get_policy(key)
            self.l1_cache.set(key, value, ttl=policy.ttl // 4)  # L1은 더 짧은 TTL
            
            await self._check_refresh_ahead(key, fetch_func)
            return value
        
        # 캐시 미스 - 원본 데이터 조회
        if fetch_func:
            value = await fetch_func()
            if value is not None:
                await self.set(key, value)
            return value
        
        return None
    
    async def set(self, key: str, value: Any) -> None:
        """다층 캐시에 값 저장"""
        policy = self._get_policy(key)
        
        if policy.strategy == CacheStrategy.WRITE_THROUGH:
            # L1, L2에 동시 저장
            self.l1_cache.set(key, value, ttl=policy.ttl // 4)
            await self.l2_cache.set(key, value, ttl=policy.ttl)
        
        elif policy.strategy == CacheStrategy.WRITE_BEHIND:
            # L1에 즉시 저장, L2는 비동기
            self.l1_cache.set(key, value, ttl=policy.ttl // 4)
            asyncio.create_task(self.l2_cache.set(key, value, ttl=policy.ttl))
        
        elif policy.strategy == CacheStrategy.CACHE_ASIDE:
            # L1만 저장
            self.l1_cache.set(key, value, ttl=policy.ttl // 4)
    
    async def _check_refresh_ahead(self, key: str, fetch_func: Callable):
        """Refresh-ahead 전략 확인"""
        if not fetch_func:
            return
        
        policy = self._get_policy(key)
        if policy.strategy == CacheStrategy.REFRESH_AHEAD:
            # TTL 임계값 확인하여 백그라운드 새로고침 스케줄
            await self.refresh_queue.put((key, fetch_func))
    
    async def _refresh_worker(self):
        """백그라운드 새로고침 워커"""
        while True:
            try:
                key, fetch_func = await self.refresh_queue.get()
                
                # 백그라운드에서 데이터 새로고침
                fresh_value = await fetch_func()
                if fresh_value is not None:
                    await self.set(key, fresh_value)
                
                self.refresh_queue.task_done()
                
            except Exception as e:
                print(f"Refresh worker error: {e}")
                await asyncio.sleep(1)
    
    def _get_policy(self, key: str) -> CachePolicy:
        """키에 대한 캐시 정책 조회"""
        for pattern, policy in self.policies.items():
            if pattern in key:  # 간단한 패턴 매칭
                return policy
        
        # 기본 정책
        return CachePolicy(
            strategy=CacheStrategy.WRITE_THROUGH,
            ttl=3600
        )
```

### Layer 3: CDN 및 Edge 캐싱 (L3)

#### 3.1 CloudFront 최적화
```yaml
# infrastructure/cdn/cloudfront-config.yaml

CloudFrontDistribution:
  Type: AWS::CloudFront::Distribution
  Properties:
    DistributionConfig:
      Comment: "T-Developer API and Static Assets CDN"
      Enabled: true
      HttpVersion: http2
      IPV6Enabled: true
      
      # Origin 구성
      Origins:
        - Id: "api-origin"
          DomainName: "api.t-developer.com"
          CustomOriginConfig:
            HTTPPort: 443
            HTTPSPort: 443
            OriginProtocolPolicy: "https-only"
            OriginSSLProtocols: ["TLSv1.2"]
        
        - Id: "static-origin"
          DomainName: "static.t-developer.com"
          S3OriginConfig:
            OriginAccessIdentity: !Sub "${OriginAccessIdentity}"
      
      # 캐시 동작 설정
      DefaultCacheBehavior:
        TargetOriginId: "api-origin"
        ViewerProtocolPolicy: "redirect-to-https"
        CachePolicyId: "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"  # CachingDisabled
        OriginRequestPolicyId: "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"  # CORS-S3Origin
        ResponseHeadersPolicyId: "67f7725c-6f97-4210-82d7-5512b31e9d03"  # SecurityHeaders
        
        # Edge Lambda 함수
        LambdaFunctionAssociations:
          - EventType: "origin-request"
            LambdaFunctionARN: !Sub "${EdgeOptimizer}:${EdgeOptimizerVersion}"
      
      # 추가 캐시 동작
      CacheBehaviors:
        # API 엔드포인트별 캐시 설정
        - PathPattern: "/api/v1/agents/*/status"
          TargetOriginId: "api-origin"
          ViewerProtocolPolicy: "https-only"
          CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6"  # CachingOptimized
          TTL:
            DefaultTTL: 300      # 5분
            MaxTTL: 3600         # 1시간
            MinTTL: 0
        
        - PathPattern: "/api/v1/agents"
          TargetOriginId: "api-origin"  
          ViewerProtocolPolicy: "https-only"
          CachePolicyId: "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"  # CachingDisabled
        
        # 정적 파일 최적화
        - PathPattern: "*.js"
          TargetOriginId: "static-origin"
          ViewerProtocolPolicy: "https-only"
          TTL:
            DefaultTTL: 86400    # 1일
            MaxTTL: 31536000     # 1년
            MinTTL: 0
          Compress: true
        
        - PathPattern: "*.css"
          TargetOriginId: "static-origin"
          ViewerProtocolPolicy: "https-only"
          TTL:
            DefaultTTL: 86400    # 1일
            MaxTTL: 31536000     # 1년
            MinTTL: 0
          Compress: true
      
      # 지역별 Edge Location 최적화
      PriceClass: "PriceClass_All"  # 전 세계 모든 엣지 로케이션 사용
      
      # HTTP/2 Push 최적화
      ViewerCertificate:
        AcmCertificateArn: !Ref SSLCertificate
        SslSupportMethod: "sni-only"
        MinimumProtocolVersion: "TLSv1.2_2021"
```

#### 3.2 Edge Computing 최적화
```javascript
// Edge Lambda Function for Request Optimization
export const handler = async (event) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    
    // User-Agent 기반 최적화
    const userAgent = headers['user-agent'][0].value.toLowerCase();
    if (userAgent.includes('mobile')) {
        // 모바일 사용자를 위한 압축된 응답
        headers['accept-encoding'] = [{ key: 'Accept-Encoding', value: 'gzip, br' }];
    }
    
    // 지역별 라우팅 최적화
    const cloudFrontRegion = headers['cloudfront-viewer-country'][0].value;
    if (cloudFrontRegion === 'KR') {
        // 한국 사용자를 위한 서울 리전 라우팅
        request.origin.custom.domainName = 'api-ap-northeast-2.t-developer.com';
    }
    
    // API 키 기반 캐싱 전략
    const apiKey = headers['x-api-key'];
    if (apiKey) {
        const tier = await getTierFromApiKey(apiKey[0].value);
        if (tier === 'premium') {
            // 프리미엄 사용자는 더 긴 캐시 TTL
            headers['cache-control'] = [{ key: 'Cache-Control', value: 'max-age=3600' }];
        }
    }
    
    return request;
};
```

## 🗄️ 데이터베이스 최적화

### 1. 데이터베이스 샤딩 전략

#### 1.1 수평적 샤딩 구현
```python
# backend/src/database/sharding_manager.py

import hashlib
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ShardingStrategy(Enum):
    HASH_BASED = "hash"
    RANGE_BASED = "range"
    DIRECTORY_BASED = "directory"

@dataclass
class ShardConfig:
    shard_id: str
    connection_string: str
    weight: float = 1.0
    is_active: bool = True
    read_only: bool = False

class DatabaseShardingManager:
    def __init__(self, sharding_strategy: ShardingStrategy = ShardingStrategy.HASH_BASED):
        self.strategy = sharding_strategy
        self.shards: Dict[str, ShardConfig] = {}
        self.shard_ring: List[str] = []  # Consistent hashing ring
        self.connections: Dict[str, Any] = {}  # DB connection pools
        
    def add_shard(self, config: ShardConfig) -> None:
        """샤드 추가"""
        self.shards[config.shard_id] = config
        
        if self.strategy == ShardingStrategy.HASH_BASED:
            self._rebuild_hash_ring()
    
    def _rebuild_hash_ring(self) -> None:
        """Consistent Hashing Ring 재구성"""
        self.shard_ring.clear()
        
        for shard_id, config in self.shards.items():
            if config.is_active:
                # 가중치에 따라 더 많은 가상 노드 생성
                virtual_nodes = int(config.weight * 100)
                
                for i in range(virtual_nodes):
                    virtual_key = f"{shard_id}:{i}"
                    hash_value = hashlib.md5(virtual_key.encode()).hexdigest()
                    self.shard_ring.append((hash_value, shard_id))
        
        # 해시값으로 정렬
        self.shard_ring.sort(key=lambda x: x[0])
    
    def get_shard_for_key(self, key: str) -> str:
        """키에 대한 적절한 샤드 반환"""
        if self.strategy == ShardingStrategy.HASH_BASED:
            return self._get_shard_by_hash(key)
        elif self.strategy == ShardingStrategy.RANGE_BASED:
            return self._get_shard_by_range(key)
        elif self.strategy == ShardingStrategy.DIRECTORY_BASED:
            return self._get_shard_by_directory(key)
    
    def _get_shard_by_hash(self, key: str) -> str:
        """해시 기반 샤드 선택"""
        if not self.shard_ring:
            raise ValueError("No active shards available")
        
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        # Ring에서 key_hash보다 큰 첫 번째 노드 찾기
        for ring_hash, shard_id in self.shard_ring:
            if ring_hash >= key_hash:
                return shard_id
        
        # 마지막까지 찾지 못하면 첫 번째 노드 반환 (ring의 특성)
        return self.shard_ring[0][1]
    
    async def execute_query(self, key: str, query: str, params: Dict = None, 
                          read_only: bool = False) -> Any:
        """샤드별 쿼리 실행"""
        if read_only:
            # 읽기 전용 쿼리는 읽기 복제본 사용
            shard_id = self._get_read_replica(key)
        else:
            shard_id = self.get_shard_for_key(key)
        
        connection = await self._get_connection(shard_id)
        
        try:
            if params:
                result = await connection.execute(query, params)
            else:
                result = await connection.execute(query)
            
            return result
            
        except Exception as e:
            # 샤드 장애 시 자동 페일오버
            if not read_only:
                backup_shard = self._get_backup_shard(shard_id)
                if backup_shard:
                    connection = await self._get_connection(backup_shard)
                    return await connection.execute(query, params or {})
            raise e
    
    async def execute_distributed_query(self, query: str, 
                                      params: Dict = None) -> List[Any]:
        """모든 샤드에 분산 쿼리 실행"""
        tasks = []
        
        for shard_id in self.shards.keys():
            if self.shards[shard_id].is_active:
                task = self._execute_on_shard(shard_id, query, params)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 성공한 결과만 수집
        successful_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        return successful_results
    
    def _get_read_replica(self, key: str) -> str:
        """읽기 복제본 선택"""
        primary_shard = self.get_shard_for_key(key)
        
        # 읽기 전용 복제본이 있으면 사용
        for shard_id, config in self.shards.items():
            if (config.is_active and config.read_only and 
                shard_id.startswith(f"{primary_shard}_replica")):
                return shard_id
        
        # 복제본이 없으면 원본 샤드 사용
        return primary_shard
```

#### 1.2 자동 샤드 리밸런싱
```python
# backend/src/database/shard_rebalancer.py

import asyncio
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ShardMetrics:
    shard_id: str
    data_size: int  # bytes
    query_count: int
    cpu_usage: float
    memory_usage: float
    connection_count: int
    last_updated: float

class ShardRebalancer:
    def __init__(self, sharding_manager: DatabaseShardingManager):
        self.sharding_manager = sharding_manager
        self.metrics: Dict[str, ShardMetrics] = {}
        self.rebalancing_threshold = 0.8  # 80% 임계값
        self.monitoring_interval = 300  # 5분마다 모니터링
    
    async def start_monitoring(self):
        """샤드 모니터링 시작"""
        while True:
            await self._collect_metrics()
            await self._analyze_and_rebalance()
            await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self):
        """각 샤드의 메트릭 수집"""
        for shard_id in self.sharding_manager.shards.keys():
            try:
                metrics = await self._get_shard_metrics(shard_id)
                self.metrics[shard_id] = metrics
            except Exception as e:
                print(f"Failed to collect metrics for shard {shard_id}: {e}")
    
    async def _get_shard_metrics(self, shard_id: str) -> ShardMetrics:
        """특정 샤드의 메트릭 조회"""
        connection = await self.sharding_manager._get_connection(shard_id)
        
        # 데이터 크기 조회
        size_query = "SELECT pg_database_size(current_database())"
        data_size = await connection.fetchval(size_query)
        
        # 연결 수 조회
        conn_query = "SELECT count(*) FROM pg_stat_activity"
        connection_count = await connection.fetchval(conn_query)
        
        # CPU/메모리 사용량은 CloudWatch나 시스템 메트릭에서 가져옴
        cpu_usage = await self._get_cpu_usage(shard_id)
        memory_usage = await self._get_memory_usage(shard_id)
        
        return ShardMetrics(
            shard_id=shard_id,
            data_size=data_size,
            query_count=0,  # 추후 구현
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            connection_count=connection_count,
            last_updated=time.time()
        )
    
    async def _analyze_and_rebalance(self):
        """메트릭 분석 및 리밸런싱 실행"""
        if len(self.metrics) < 2:
            return
        
        # 부하가 높은 샤드 식별
        overloaded_shards = self._identify_overloaded_shards()
        
        if overloaded_shards:
            print(f"Overloaded shards detected: {overloaded_shards}")
            
            for shard_id in overloaded_shards:
                await self._rebalance_shard(shard_id)
    
    def _identify_overloaded_shards(self) -> List[str]:
        """과부하 샤드 식별"""
        overloaded = []
        
        for shard_id, metrics in self.metrics.items():
            if (metrics.cpu_usage > self.rebalancing_threshold or
                metrics.memory_usage > self.rebalancing_threshold):
                overloaded.append(shard_id)
        
        return overloaded
    
    async def _rebalance_shard(self, overloaded_shard_id: str):
        """특정 샤드 리밸런싱"""
        # 1. 새로운 샤드 생성
        new_shard_id = f"{overloaded_shard_id}_split_{int(time.time())}"
        await self._create_new_shard(new_shard_id)
        
        # 2. 데이터 마이그레이션 계획 수립
        migration_plan = await self._create_migration_plan(
            overloaded_shard_id, new_shard_id
        )
        
        # 3. 점진적 데이터 마이그레이션
        await self._execute_migration(migration_plan)
        
        # 4. 라우팅 테이블 업데이트
        await self._update_routing_table(overloaded_shard_id, new_shard_id)
        
        print(f"Rebalancing completed: {overloaded_shard_id} -> {new_shard_id}")
```

### 2. 쿼리 최적화

#### 2.1 지능형 쿼리 캐시
```python
# backend/src/database/query_cache.py

import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class QueryCacheEntry:
    result: Any
    cached_at: float
    ttl: int
    hit_count: int = 0
    execution_time: float = 0.0
    query_complexity: int = 1

class IntelligentQueryCache:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: Dict[str, QueryCacheEntry] = {}
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        
    def get_cache_key(self, query: str, params: Dict = None) -> str:
        """쿼리 캐시 키 생성"""
        query_normalized = self._normalize_query(query)
        params_str = str(sorted(params.items())) if params else ""
        
        combined = f"{query_normalized}:{params_str}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def _normalize_query(self, query: str) -> str:
        """쿼리 정규화"""
        # 공백 정리
        normalized = " ".join(query.split())
        
        # 대소문자 통일
        normalized = normalized.lower()
        
        # SQL 키워드 정규화
        normalized = normalized.replace("  ", " ")
        
        return normalized
    
    async def get_or_execute(self, query: str, params: Dict = None, 
                           executor_func=None, ttl: int = 300) -> Any:
        """캐시 조회 또는 쿼리 실행"""
        cache_key = self.get_cache_key(query, params)
        
        # 캐시 확인
        cached_entry = self._get_from_cache(cache_key)
        if cached_entry:
            return cached_entry.result
        
        # 캐시 미스 - 쿼리 실행
        start_time = time.time()
        result = await executor_func(query, params)
        execution_time = time.time() - start_time
        
        # 쿼리 복잡도 분석
        complexity = self._analyze_query_complexity(query)
        
        # 캐시에 저장 (복잡한 쿼리일수록 더 오래 캐시)
        dynamic_ttl = self._calculate_dynamic_ttl(execution_time, complexity, ttl)
        self._store_in_cache(cache_key, result, dynamic_ttl, execution_time, complexity)
        
        # 통계 업데이트
        self._update_query_stats(cache_key, execution_time, complexity)
        
        return result
    
    def _get_from_cache(self, cache_key: str) -> Optional[QueryCacheEntry]:
        """캐시에서 조회"""
        if cache_key not in self.cache:
            return None
        
        entry = self.cache[cache_key]
        
        # TTL 확인
        if time.time() - entry.cached_at > entry.ttl:
            del self.cache[cache_key]
            return None
        
        # 히트 카운트 증가
        entry.hit_count += 1
        
        return entry
    
    def _store_in_cache(self, cache_key: str, result: Any, ttl: int, 
                       execution_time: float, complexity: int):
        """캐시에 저장"""
        # 용량 초과 시 LRU + 복잡도 기반 제거
        if len(self.cache) >= self.max_size:
            self._evict_entries()
        
        self.cache[cache_key] = QueryCacheEntry(
            result=result,
            cached_at=time.time(),
            ttl=ttl,
            execution_time=execution_time,
            query_complexity=complexity
        )
    
    def _analyze_query_complexity(self, query: str) -> int:
        """쿼리 복잡도 분석"""
        complexity_score = 1
        
        query_lower = query.lower()
        
        # JOIN 개수
        join_count = query_lower.count("join")
        complexity_score += join_count * 2
        
        # 서브쿼리 개수
        subquery_count = query_lower.count("(select")
        complexity_score += subquery_count * 3
        
        # 집계 함수
        aggregation_keywords = ["group by", "order by", "having", "window"]
        for keyword in aggregation_keywords:
            if keyword in query_lower:
                complexity_score += 2
        
        # CTE (Common Table Expression)
        if "with" in query_lower:
            complexity_score += 3
        
        return min(complexity_score, 10)  # 최대 10점
    
    def _calculate_dynamic_ttl(self, execution_time: float, 
                             complexity: int, base_ttl: int) -> int:
        """동적 TTL 계산"""
        # 실행 시간이 길수록 더 오래 캐시
        time_factor = min(execution_time / 1.0, 5.0)  # 최대 5배
        
        # 복잡도가 높을수록 더 오래 캐시
        complexity_factor = complexity / 5.0
        
        dynamic_ttl = int(base_ttl * (1 + time_factor + complexity_factor))
        
        return min(dynamic_ttl, 3600)  # 최대 1시간
    
    def _evict_entries(self):
        """캐시 항목 제거"""
        # LRU + 복잡도 기반 점수 계산
        scored_entries = []
        
        for cache_key, entry in self.cache.items():
            # 점수가 높을수록 유지 (hit_count와 complexity가 높고, 오래되지 않은 것)
            age = time.time() - entry.cached_at
            score = (entry.hit_count * entry.query_complexity) / (age + 1)
            scored_entries.append((score, cache_key))
        
        # 점수 순으로 정렬하여 하위 25% 제거
        scored_entries.sort()
        to_remove = len(scored_entries) // 4
        
        for _, cache_key in scored_entries[:to_remove]:
            del self.cache[cache_key]
```

## 📊 성능 모니터링 및 분석

### 1. Real-time Performance Monitoring
```python
# backend/src/monitoring/performance_monitor.py

import asyncio
import time
import psutil
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    active_connections: int
    response_times: Dict[str, List[float]]  # endpoint -> [response_times]
    error_rates: Dict[str, float]
    cache_hit_rates: Dict[str, float]

class PerformanceMonitor:
    def __init__(self, collection_interval: int = 5):
        self.collection_interval = collection_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.alert_callbacks: List[Callable] = []
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "response_time_p95": 1000.0,  # ms
            "error_rate": 0.05,  # 5%
            "cache_hit_rate_min": 0.8  # 80%
        }
        
    async def start_monitoring(self):
        """성능 모니터링 시작"""
        while True:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # 최근 1시간 데이터만 유지
                cutoff = time.time() - 3600
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff
                ]
                
                # 임계값 확인 및 알림
                await self._check_thresholds(metrics)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                
            await asyncio.sleep(self.collection_interval)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """시스템 메트릭 수집"""
        # CPU 사용률
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 디스크 I/O
        disk_io = psutil.disk_io_counters()
        disk_metrics = {
            "read_bytes_per_sec": disk_io.read_bytes,
            "write_bytes_per_sec": disk_io.write_bytes,
            "read_ops_per_sec": disk_io.read_count,
            "write_ops_per_sec": disk_io.write_count
        }
        
        # 네트워크 I/O
        network_io = psutil.net_io_counters()
        network_metrics = {
            "bytes_sent_per_sec": network_io.bytes_sent,
            "bytes_recv_per_sec": network_io.bytes_recv,
            "packets_sent_per_sec": network_io.packets_sent,
            "packets_recv_per_sec": network_io.packets_recv
        }
        
        # 활성 연결 수
        active_connections = len(psutil.net_connections())
        
        # 애플리케이션 메트릭 (외부에서 주입)
        response_times = await self._get_response_times()
        error_rates = await self._get_error_rates()
        cache_hit_rates = await self._get_cache_hit_rates()
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_io=disk_metrics,
            network_io=network_metrics,
            active_connections=active_connections,
            response_times=response_times,
            error_rates=error_rates,
            cache_hit_rates=cache_hit_rates
        )
    
    async def _check_thresholds(self, metrics: PerformanceMetrics):
        """임계값 확인 및 알림"""
        alerts = []
        
        # CPU 사용률 확인
        if metrics.cpu_usage > self.thresholds["cpu_usage"]:
            alerts.append({
                "type": "HIGH_CPU_USAGE",
                "value": metrics.cpu_usage,
                "threshold": self.thresholds["cpu_usage"],
                "severity": "WARNING" if metrics.cpu_usage < 90 else "CRITICAL"
            })
        
        # 메모리 사용률 확인
        if metrics.memory_usage > self.thresholds["memory_usage"]:
            alerts.append({
                "type": "HIGH_MEMORY_USAGE", 
                "value": metrics.memory_usage,
                "threshold": self.thresholds["memory_usage"],
                "severity": "WARNING" if metrics.memory_usage < 95 else "CRITICAL"
            })
        
        # 응답 시간 확인
        for endpoint, times in metrics.response_times.items():
            if times:
                p95_time = self._calculate_percentile(times, 95)
                if p95_time > self.thresholds["response_time_p95"]:
                    alerts.append({
                        "type": "HIGH_RESPONSE_TIME",
                        "endpoint": endpoint,
                        "value": p95_time,
                        "threshold": self.thresholds["response_time_p95"],
                        "severity": "WARNING"
                    })
        
        # 에러율 확인
        for endpoint, error_rate in metrics.error_rates.items():
            if error_rate > self.thresholds["error_rate"]:
                alerts.append({
                    "type": "HIGH_ERROR_RATE",
                    "endpoint": endpoint,
                    "value": error_rate,
                    "threshold": self.thresholds["error_rate"],
                    "severity": "CRITICAL" if error_rate > 0.1 else "WARNING"
                })
        
        # 캐시 히트율 확인
        for cache_name, hit_rate in metrics.cache_hit_rates.items():
            if hit_rate < self.thresholds["cache_hit_rate_min"]:
                alerts.append({
                    "type": "LOW_CACHE_HIT_RATE",
                    "cache": cache_name,
                    "value": hit_rate,
                    "threshold": self.thresholds["cache_hit_rate_min"],
                    "severity": "WARNING"
                })
        
        # 알림 전송
        for alert in alerts:
            await self._send_alert(alert)
    
    def get_performance_summary(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """성능 요약 조회"""
        cutoff = time.time() - (duration_minutes * 60)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available"}
        
        # 평균값 계산
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        
        # 응답 시간 통계
        all_response_times = []
        for metrics in recent_metrics:
            for endpoint_times in metrics.response_times.values():
                all_response_times.extend(endpoint_times)
        
        response_time_stats = {
            "p50": self._calculate_percentile(all_response_times, 50),
            "p95": self._calculate_percentile(all_response_times, 95),
            "p99": self._calculate_percentile(all_response_times, 99)
        } if all_response_times else {}
        
        return {
            "period": f"{duration_minutes} minutes",
            "avg_cpu_usage": round(avg_cpu, 2),
            "avg_memory_usage": round(avg_memory, 2),
            "response_time_stats": response_time_stats,
            "total_data_points": len(recent_metrics)
        }
```

### 2. Automated Performance Optimization
```python
# backend/src/optimization/auto_optimizer.py

import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class OptimizationAction:
    action_type: str
    target: str
    parameters: Dict[str, Any]
    expected_improvement: float
    risk_level: str  # LOW, MEDIUM, HIGH

class AutoPerformanceOptimizer:
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.monitor = performance_monitor
        self.optimization_rules = self._load_optimization_rules()
        self.applied_optimizations: List[OptimizationAction] = []
        
    def _load_optimization_rules(self) -> List[Dict[str, Any]]:
        """최적화 규칙 로드"""
        return [
            {
                "condition": "high_cpu_usage",
                "threshold": 80.0,
                "actions": [
                    {
                        "type": "scale_up_instances",
                        "parameters": {"scale_factor": 1.5},
                        "expected_improvement": 0.3,
                        "risk_level": "LOW"
                    },
                    {
                        "type": "enable_cpu_throttling",
                        "parameters": {"max_cpu_per_request": 50},
                        "expected_improvement": 0.2,
                        "risk_level": "MEDIUM"
                    }
                ]
            },
            {
                "condition": "high_memory_usage", 
                "threshold": 85.0,
                "actions": [
                    {
                        "type": "increase_cache_eviction",
                        "parameters": {"eviction_rate": 1.2},
                        "expected_improvement": 0.15,
                        "risk_level": "LOW"
                    },
                    {
                        "type": "scale_up_memory",
                        "parameters": {"memory_multiplier": 1.3},
                        "expected_improvement": 0.4,
                        "risk_level": "MEDIUM"
                    }
                ]
            },
            {
                "condition": "low_cache_hit_rate",
                "threshold": 0.7,
                "actions": [
                    {
                        "type": "increase_cache_size",
                        "parameters": {"size_multiplier": 1.5},
                        "expected_improvement": 0.25,
                        "risk_level": "LOW"
                    },
                    {
                        "type": "optimize_cache_policy",
                        "parameters": {"ttl_multiplier": 1.2},
                        "expected_improvement": 0.15,
                        "risk_level": "LOW"
                    }
                ]
            }
        ]
    
    async def run_optimization_cycle(self):
        """최적화 사이클 실행"""
        current_metrics = self.monitor.metrics_history[-1] if self.monitor.metrics_history else None
        
        if not current_metrics:
            return
        
        # 최적화 기회 식별
        optimization_actions = self._identify_optimization_opportunities(current_metrics)
        
        # 안전한 최적화만 자동 적용
        safe_actions = [
            action for action in optimization_actions 
            if action.risk_level == "LOW"
        ]
        
        for action in safe_actions:
            success = await self._apply_optimization(action)
            if success:
                self.applied_optimizations.append(action)
                print(f"Applied optimization: {action.action_type}")
        
        # 위험도가 높은 최적화는 승인 요청
        risky_actions = [
            action for action in optimization_actions 
            if action.risk_level in ["MEDIUM", "HIGH"]
        ]
        
        if risky_actions:
            await self._request_approval_for_risky_optimizations(risky_actions)
    
    def _identify_optimization_opportunities(self, 
                                          metrics: PerformanceMetrics) -> List[OptimizationAction]:
        """최적화 기회 식별"""
        opportunities = []
        
        for rule in self.optimization_rules:
            condition = rule["condition"]
            threshold = rule["threshold"]
            
            should_optimize = False
            
            if condition == "high_cpu_usage" and metrics.cpu_usage > threshold:
                should_optimize = True
            elif condition == "high_memory_usage" and metrics.memory_usage > threshold:
                should_optimize = True
            elif condition == "low_cache_hit_rate":
                avg_hit_rate = sum(metrics.cache_hit_rates.values()) / len(metrics.cache_hit_rates)
                if avg_hit_rate < threshold:
                    should_optimize = True
            
            if should_optimize:
                for action_config in rule["actions"]:
                    action = OptimizationAction(
                        action_type=action_config["type"],
                        target="system",
                        parameters=action_config["parameters"],
                        expected_improvement=action_config["expected_improvement"],
                        risk_level=action_config["risk_level"]
                    )
                    opportunities.append(action)
        
        return opportunities
    
    async def _apply_optimization(self, action: OptimizationAction) -> bool:
        """최적화 적용"""
        try:
            if action.action_type == "scale_up_instances":
                return await self._scale_up_instances(action.parameters)
            elif action.action_type == "increase_cache_size":
                return await self._increase_cache_size(action.parameters)
            elif action.action_type == "optimize_cache_policy":
                return await self._optimize_cache_policy(action.parameters)
            elif action.action_type == "increase_cache_eviction":
                return await self._increase_cache_eviction(action.parameters)
            # ... 기타 최적화 액션들
            
            return False
            
        except Exception as e:
            print(f"Optimization failed: {action.action_type}, Error: {e}")
            return False
```

## 🎯 성능 최적화 로드맵

### Phase 1: 기본 최적화 (1-2주)
- L1/L2 캐싱 시스템 구현
- 데이터베이스 인덱스 최적화
- API 응답 압축 설정

### Phase 2: 고급 최적화 (2-3주)
- 데이터베이스 샤딩 구현
- CDN 및 Edge 캐싱 설정
- 지능형 쿼리 캐싱

### Phase 3: 자동 최적화 (1-2주)
- 실시간 성능 모니터링
- 자동 성능 최적화 시스템
- 예측적 스케일링

이 성능 최적화 전략을 통해 T-Developer 플랫폼이 대규모 트래픽과 복잡한 AI 워크로드를 효율적으로 처리할 수 있습니다.