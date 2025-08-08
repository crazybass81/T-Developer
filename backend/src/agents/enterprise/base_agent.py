"""
Base Agent Class for Enterprise Implementation
Provides common functionality for all agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
import time
import hashlib
import json
import traceback
from contextlib import asynccontextmanager

import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import structlog
from opentelemetry import trace
from circuitbreaker import circuit

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"

@dataclass
class AgentConfig:
    """Configuration for enterprise agents"""
    name: str
    version: str = "1.0.0"
    timeout: int = 30  # seconds
    retries: int = 3
    retry_delay: int = 1  # seconds
    memory_limit: str = "2GB"
    cpu_limit: float = 2.0
    gpu_required: bool = False
    cache_ttl: int = 3600  # seconds
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    rate_limit: int = 100  # requests per minute
    batch_size: int = 10
    priority: int = 5  # 1-10, higher is more important
    
@dataclass
class AgentContext:
    """Execution context for agents"""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    environment: str = "production"
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.utcnow)
    
class EnterpriseBaseAgent(ABC):
    """
    Base class for all enterprise agents
    Provides caching, monitoring, error handling, and circuit breaking
    """
    
    # Class-level metrics
    _metrics_initialized = False
    _request_count = None
    _request_duration = None
    _error_count = None
    _cache_hits = None
    _cache_misses = None
    _active_requests = None
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = structlog.get_logger(self.config.name)
        self.tracer = trace.get_tracer(self.config.name, self.config.version)
        
        # Initialize metrics once per class
        if not self.__class__._metrics_initialized:
            self._initialize_metrics()
            self.__class__._metrics_initialized = True
        
        # Redis cache connection
        self.redis_client: Optional[redis.Redis] = None
        self._cache_namespace = f"agent:{self.config.name}:{self.config.version}"
        
        # Circuit breaker for external calls
        self.circuit_breaker = circuit(
            failure_threshold=self.config.circuit_breaker_threshold,
            recovery_timeout=self.config.circuit_breaker_timeout,
            expected_exception=Exception
        )
        
        # Rate limiting
        self._rate_limiter = AsyncRateLimiter(
            rate=self.config.rate_limit,
            period=60  # per minute
        )
        
        # Performance tracking
        self._performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_duration": 0.0,
            "cache_hit_rate": 0.0
        }
        
    @classmethod
    def _initialize_metrics(cls):
        """Initialize Prometheus metrics"""
        cls._request_count = Counter(
            f'{cls.__name__}_requests_total',
            'Total number of requests',
            ['status', 'tenant_id']
        )
        cls._request_duration = Histogram(
            f'{cls.__name__}_request_duration_seconds',
            'Request duration in seconds',
            ['tenant_id']
        )
        cls._error_count = Counter(
            f'{cls.__name__}_errors_total',
            'Total number of errors',
            ['error_type', 'tenant_id']
        )
        cls._cache_hits = Counter(
            f'{cls.__name__}_cache_hits_total',
            'Total number of cache hits',
            ['tenant_id']
        )
        cls._cache_misses = Counter(
            f'{cls.__name__}_cache_misses_total',
            'Total number of cache misses',
            ['tenant_id']
        )
        cls._active_requests = Gauge(
            f'{cls.__name__}_active_requests',
            'Number of active requests',
            ['tenant_id']
        )
    
    async def initialize(self):
        """Initialize agent resources"""
        try:
            # Connect to Redis
            self.redis_client = await redis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            self.logger.info("Redis connection established")
            
            # Custom initialization for derived classes
            await self._custom_initialize()
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise
    
    async def _custom_initialize(self):
        """Override in derived classes for custom initialization"""
        pass
    
    async def cleanup(self):
        """Cleanup agent resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            # Custom cleanup for derived classes
            await self._custom_cleanup()
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
    
    async def _custom_cleanup(self):
        """Override in derived classes for custom cleanup"""
        pass
    
    @asynccontextmanager
    async def _track_performance(self, context: AgentContext):
        """Context manager for performance tracking"""
        start_time = time.time()
        tenant_id = context.tenant_id or "default"
        
        # Increment active requests
        self._active_requests.labels(tenant_id=tenant_id).inc()
        
        try:
            yield
            
            # Record success
            duration = time.time() - start_time
            self._request_count.labels(status="success", tenant_id=tenant_id).inc()
            self._request_duration.labels(tenant_id=tenant_id).observe(duration)
            
            # Update stats
            self._performance_stats["total_requests"] += 1
            self._performance_stats["successful_requests"] += 1
            self._performance_stats["total_duration"] += duration
            
        except Exception as e:
            # Record failure
            duration = time.time() - start_time
            self._request_count.labels(status="failed", tenant_id=tenant_id).inc()
            self._request_duration.labels(tenant_id=tenant_id).observe(duration)
            self._error_count.labels(
                error_type=type(e).__name__,
                tenant_id=tenant_id
            ).inc()
            
            # Update stats
            self._performance_stats["total_requests"] += 1
            self._performance_stats["failed_requests"] += 1
            self._performance_stats["total_duration"] += duration
            
            raise
            
        finally:
            # Decrement active requests
            self._active_requests.labels(tenant_id=tenant_id).dec()
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[AgentContext] = None
    ) -> Dict[str, Any]:
        """
        Main execution method with full enterprise features
        """
        if context is None:
            context = AgentContext()
        
        # Create span for tracing
        with self.tracer.start_as_current_span(
            f"{self.config.name}.execute",
            attributes={
                "agent.name": self.config.name,
                "agent.version": self.config.version,
                "trace.id": context.trace_id,
                "tenant.id": context.tenant_id or "default"
            }
        ) as span:
            try:
                # Check rate limit
                await self._check_rate_limit(context)
                
                # Track performance
                async with self._track_performance(context):
                    
                    # Check cache
                    cache_key = self._generate_cache_key(input_data, context)
                    cached_result = await self._get_from_cache(cache_key, context)
                    
                    if cached_result is not None:
                        self.logger.info(
                            "Cache hit",
                            cache_key=cache_key,
                            trace_id=context.trace_id
                        )
                        span.set_attribute("cache.hit", True)
                        return cached_result
                    
                    span.set_attribute("cache.hit", False)
                    
                    # Execute with retry logic
                    result = await self._execute_with_retry(
                        input_data,
                        context,
                        span
                    )
                    
                    # Cache result
                    await self._set_cache(cache_key, result, context)
                    
                    # Validate output
                    validated_result = await self._validate_output(result, context)
                    
                    return validated_result
                    
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                
                self.logger.error(
                    "Agent execution failed",
                    agent=self.config.name,
                    error=str(e),
                    trace_id=context.trace_id,
                    traceback=traceback.format_exc()
                )
                
                # Return error response
                return self._create_error_response(e, context)
    
    async def _execute_with_retry(
        self,
        input_data: Dict[str, Any],
        context: AgentContext,
        span
    ) -> Dict[str, Any]:
        """Execute with retry logic"""
        last_error = None
        
        for attempt in range(self.config.retries):
            try:
                # Add retry attempt to span
                span.set_attribute("retry.attempt", attempt)
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._process_with_circuit_breaker(input_data, context),
                    timeout=self.config.timeout
                )
                
                return result
                
            except asyncio.TimeoutError:
                last_error = TimeoutError(f"Agent {self.config.name} timeout after {self.config.timeout}s")
                self.logger.warning(
                    "Agent timeout",
                    agent=self.config.name,
                    attempt=attempt + 1,
                    trace_id=context.trace_id
                )
                
            except Exception as e:
                last_error = e
                self.logger.warning(
                    "Agent execution attempt failed",
                    agent=self.config.name,
                    attempt=attempt + 1,
                    error=str(e),
                    trace_id=context.trace_id
                )
            
            # Wait before retry
            if attempt < self.config.retries - 1:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        
        # All retries failed
        raise last_error or Exception("All retry attempts failed")
    
    @circuit
    async def _process_with_circuit_breaker(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """Process with circuit breaker protection"""
        return await self.process(input_data, context)
    
    @abstractmethod
    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Core processing logic - must be implemented by derived classes
        """
        pass
    
    async def _validate_output(
        self,
        output: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """Validate and enrich output"""
        # Add metadata
        output["_metadata"] = {
            "agent": self.config.name,
            "version": self.config.version,
            "trace_id": context.trace_id,
            "timestamp": datetime.utcnow().isoformat(),
            "duration": (datetime.utcnow() - context.start_time).total_seconds()
        }
        
        # Custom validation in derived classes
        return await self._custom_validate_output(output, context)
    
    async def _custom_validate_output(
        self,
        output: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """Override in derived classes for custom validation"""
        return output
    
    def _generate_cache_key(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """Generate cache key from input"""
        # Create deterministic key from input
        key_data = {
            "input": input_data,
            "tenant_id": context.tenant_id,
            "version": self.config.version
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"{self._cache_namespace}:{key_hash}"
    
    async def _get_from_cache(
        self,
        key: str,
        context: AgentContext
    ) -> Optional[Dict[str, Any]]:
        """Get result from cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = await self.redis_client.get(key)
            if cached:
                self._cache_hits.labels(
                    tenant_id=context.tenant_id or "default"
                ).inc()
                return json.loads(cached)
            else:
                self._cache_misses.labels(
                    tenant_id=context.tenant_id or "default"
                ).inc()
                return None
                
        except Exception as e:
            self.logger.warning(f"Cache get failed: {str(e)}")
            return None
    
    async def _set_cache(
        self,
        key: str,
        value: Dict[str, Any],
        context: AgentContext
    ):
        """Set result in cache"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                key,
                self.config.cache_ttl,
                json.dumps(value)
            )
        except Exception as e:
            self.logger.warning(f"Cache set failed: {str(e)}")
    
    async def _check_rate_limit(self, context: AgentContext):
        """Check rate limit for tenant"""
        tenant_id = context.tenant_id or "default"
        
        if not await self._rate_limiter.allow(tenant_id):
            raise RateLimitExceeded(
                f"Rate limit exceeded for tenant {tenant_id}"
            )
    
    def _create_error_response(
        self,
        error: Exception,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "error": True,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "agent": self.config.name,
            "trace_id": context.trace_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for agent"""
        health = {
            "agent": self.config.name,
            "version": self.config.version,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self._performance_stats
        }
        
        # Check Redis connection
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health["redis"] = "connected"
            except:
                health["redis"] = "disconnected"
                health["status"] = "degraded"
        
        # Check circuit breaker
        if hasattr(self, 'circuit_breaker'):
            health["circuit_breaker"] = "open" if self.circuit_breaker.opened else "closed"
            if self.circuit_breaker.opened:
                health["status"] = "degraded"
        
        return health

class AsyncRateLimiter:
    """Async rate limiter implementation"""
    
    def __init__(self, rate: int, period: int):
        self.rate = rate
        self.period = period
        self.allowances = {}
        self.last_check = {}
    
    async def allow(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        if key not in self.allowances:
            self.allowances[key] = self.rate
            self.last_check[key] = now
            return True
        
        time_passed = now - self.last_check[key]
        self.last_check[key] = now
        
        self.allowances[key] += time_passed * (self.rate / self.period)
        
        if self.allowances[key] > self.rate:
            self.allowances[key] = self.rate
        
        if self.allowances[key] < 1.0:
            return False
        
        self.allowances[key] -= 1.0
        return True

class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    pass

class AgentTimeout(Exception):
    """Agent timeout exception"""
    pass