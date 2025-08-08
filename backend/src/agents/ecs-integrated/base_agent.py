"""
ECS-Optimized Base Agent for T-Developer
Production-ready base class for all 9 agents
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from enum import Enum
import logging
import hashlib

# AWS SDK
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# Redis for caching
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Monitoring
try:
    from aws_lambda_powertools import Logger, Tracer, Metrics
    from aws_lambda_powertools.metrics import MetricUnit
    POWERTOOLS_AVAILABLE = True
    logger = Logger()
    tracer = Tracer()
    metrics = Metrics()
except ImportError:
    POWERTOOLS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    
T = TypeVar('T')

class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"
    TIMEOUT = "timeout"

@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str
    version: str = "1.0.0"
    timeout: int = 300  # 5 minutes default
    retries: int = 3
    cache_ttl: int = 3600  # 1 hour
    enable_monitoring: bool = True
    enable_caching: bool = True
    aws_region: str = "us-east-1"
    
@dataclass
class AgentContext:
    """Shared context between agents"""
    trace_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    parent_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    
@dataclass 
class AgentResult(Generic[T]):
    """Standard agent result"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """
    Base agent class for ECS deployment
    Provides common functionality for all 9 agents
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.IDLE
        self.redis_client: Optional[redis.Redis] = None
        self.ssm_client = None
        self.secrets_client = None
        self.metrics_buffer = []
        self.processing_count = 0
        self.error_count = 0
        self.total_processing_time = 0
        
        # Initialize AWS clients if available
        if AWS_AVAILABLE:
            self._init_aws_clients()
            
        # Setup logging
        self.logger = logger if POWERTOOLS_AVAILABLE else logging.getLogger(self.config.name)
        
    def _init_aws_clients(self):
        """Initialize AWS service clients"""
        try:
            session = boto3.Session(region_name=self.config.aws_region)
            self.ssm_client = session.client('ssm')
            self.secrets_client = session.client('secretsmanager')
        except Exception as e:
            self.logger.warning(f"Failed to initialize AWS clients: {e}")
    
    async def initialize(self):
        """Initialize agent resources"""
        self.logger.info(f"Initializing {self.config.name} v{self.config.version}")
        
        # Initialize Redis if enabled
        if self.config.enable_caching and REDIS_AVAILABLE:
            await self._init_redis()
            
        # Custom initialization
        await self._custom_initialize()
        
        self.logger.info(f"{self.config.name} initialization complete")
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            redis_url = await self._get_config("REDIS_URL", "redis://localhost:6379")
            self.redis_client = await redis.from_url(redis_url)
            await self.redis_client.ping()
            self.logger.info("Redis cache initialized")
        except Exception as e:
            self.logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    @abstractmethod
    async def _custom_initialize(self):
        """Custom initialization for specific agent"""
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> AgentResult:
        """Main processing method - must be implemented by each agent"""
        pass
    
    async def execute(self, input_data: Dict[str, Any], context: Optional[AgentContext] = None) -> AgentResult:
        """Execute agent with monitoring and error handling"""
        
        # Create context if not provided
        if context is None:
            context = AgentContext(
                trace_id=self._generate_trace_id(),
                metadata={"agent": self.config.name}
            )
        
        start_time = time.time()
        self.status = AgentStatus.PROCESSING
        
        try:
            # Log start
            self.logger.info(
                f"Processing started",
                extra={
                    "agent": self.config.name,
                    "trace_id": context.trace_id,
                    "input_size": len(str(input_data))
                }
            )
            
            # Check cache if enabled
            if self.config.enable_caching:
                cached_result = await self._get_cached_result(input_data, context)
                if cached_result:
                    self.logger.info("Cache hit")
                    return cached_result
            
            # Process with timeout
            result = await asyncio.wait_for(
                self.process(input_data, context),
                timeout=self.config.timeout
            )
            
            # Cache result if successful
            if result.success and self.config.enable_caching:
                await self._cache_result(input_data, result, context)
            
            # Update metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            self.total_processing_time += processing_time
            self.processing_count += 1
            
            # Log completion
            self.logger.info(
                f"Processing completed",
                extra={
                    "agent": self.config.name,
                    "trace_id": context.trace_id,
                    "processing_time": processing_time,
                    "success": result.success
                }
            )
            
            # Record metrics
            if self.config.enable_monitoring and POWERTOOLS_AVAILABLE:
                metrics.add_metric(name=f"{self.config.name}_processing_time", unit=MetricUnit.Seconds, value=processing_time)
                metrics.add_metric(name=f"{self.config.name}_success", unit=MetricUnit.Count, value=1 if result.success else 0)
            
            self.status = AgentStatus.COMPLETED
            return result
            
        except asyncio.TimeoutError:
            self.status = AgentStatus.TIMEOUT
            self.error_count += 1
            error_msg = f"Processing timeout after {self.config.timeout}s"
            self.logger.error(error_msg)
            return AgentResult(success=False, error=error_msg)
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.error_count += 1
            error_msg = f"Processing error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return AgentResult(success=False, error=error_msg)
            
        finally:
            # Emit metrics
            if self.config.enable_monitoring and POWERTOOLS_AVAILABLE:
                try:
                    metrics.flush_metrics()
                except:
                    pass
    
    async def _get_cached_result(self, input_data: Dict[str, Any], context: AgentContext) -> Optional[AgentResult]:
        """Get cached result if available"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key(input_data, context)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                result_dict = json.loads(cached_data)
                return AgentResult(**result_dict)
                
        except Exception as e:
            self.logger.warning(f"Cache retrieval failed: {e}")
            
        return None
    
    async def _cache_result(self, input_data: Dict[str, Any], result: AgentResult, context: AgentContext):
        """Cache result"""
        if not self.redis_client or not result.success:
            return
            
        try:
            cache_key = self._generate_cache_key(input_data, context)
            result_dict = {
                "success": result.success,
                "data": result.data,
                "metadata": result.metadata
            }
            
            await self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps(result_dict, default=str)
            )
            
        except Exception as e:
            self.logger.warning(f"Cache storage failed: {e}")
    
    def _generate_cache_key(self, input_data: Dict[str, Any], context: AgentContext) -> str:
        """Generate cache key from input"""
        key_data = {
            "agent": self.config.name,
            "version": self.config.version,
            "input": input_data
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"agent:{self.config.name}:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_hex = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"{timestamp}-{random_hex}"
    
    async def _get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration from environment or SSM"""
        import os
        
        # Try environment variable first
        value = os.environ.get(key)
        if value:
            return value
            
        # Try SSM Parameter Store
        if self.ssm_client:
            try:
                param_name = f"/t-developer/{self.config.name}/{key}"
                response = self.ssm_client.get_parameter(Name=param_name)
                return response['Parameter']['Value']
            except:
                pass
                
        return default
    
    async def _get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        if not self.secrets_client:
            return None
            
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            return response.get('SecretString')
        except Exception as e:
            self.logger.warning(f"Failed to retrieve secret {secret_name}: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        health = {
            "status": "healthy",
            "agent": self.config.name,
            "version": self.config.version,
            "uptime": time.time() - (getattr(self, '_start_time', time.time())),
            "metrics": {
                "processed": self.processing_count,
                "errors": self.error_count,
                "avg_processing_time": self.total_processing_time / max(1, self.processing_count)
            }
        }
        
        # Check Redis connection
        if self.config.enable_caching:
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    health["cache"] = "connected"
                else:
                    health["cache"] = "disconnected"
            except:
                health["cache"] = "error"
                health["status"] = "degraded"
        
        return health
    
    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info(f"Cleaning up {self.config.name}")
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
            
        # Custom cleanup
        await self._custom_cleanup()
        
        self.logger.info(f"{self.config.name} cleanup complete")
    
    async def _custom_cleanup(self):
        """Custom cleanup for specific agent"""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            "agent": self.config.name,
            "version": self.config.version,
            "status": self.status.value,
            "total_processed": self.processing_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(1, self.processing_count),
            "avg_processing_time": self.total_processing_time / max(1, self.processing_count),
            "total_processing_time": self.total_processing_time
        }