"""
Unified Base Agent for T-Developer
Combines Phase 2 core interfaces with ECS optimization
"""

import asyncio
import json
import time
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
from enum import Enum
import logging
import os

# Phase 2 Core Imports
from src.core.interfaces import (
    BaseAgent as Phase2BaseAgent,
    AgentInput, 
    ProcessingStatus,
    PipelineContext,
    ValidationResult
)
from src.core.event_bus import publish_agent_event, EventType
from src.core.monitoring import get_metrics_collector, get_performance_tracker
from src.core.state_manager import PipelineStateManager
from src.core.security import InputValidator

# AWS SDK (optional)
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# Redis for caching (optional)
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Monitoring tools (optional)
try:
    from aws_lambda_powertools import Logger, Tracer, Metrics
    from aws_lambda_powertools.metrics import MetricUnit
    POWERTOOLS_AVAILABLE = True
    powertools_logger = Logger()
    tracer = Tracer()
    powertools_metrics = Metrics()
except ImportError:
    POWERTOOLS_AVAILABLE = False
    powertools_logger = None

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
    """Unified agent configuration"""
    name: str
    version: str = "1.0.0"
    timeout: int = 300  # 5 minutes default
    retries: int = 3
    cache_ttl: int = 3600  # 1 hour
    enable_monitoring: bool = True
    enable_caching: bool = True
    enable_state_management: bool = True
    aws_region: str = "us-east-1"
    ecs_optimized: bool = False  # Toggle ECS-specific features

@dataclass
class AgentContext:
    """Extended context with ECS support"""
    trace_id: str
    pipeline_context: Optional[PipelineContext] = None  # Phase 2 context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    parent_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

@dataclass
class AgentResult(Generic[T]):
    """Unified agent result"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    status: ProcessingStatus = ProcessingStatus.PENDING
    agent_name: str = ""
    agent_version: str = ""
    confidence: float = 0.0
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedBaseAgent(Phase2BaseAgent, ABC):
    """
    Unified Base Agent combining Phase 2 and ECS features
    Inherits from Phase 2 BaseAgent for compatibility
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        # Initialize Phase 2 base agent
        if config:
            super().__init__(name=config.name, version=config.version)
            self.config = config
        else:
            # Fallback for Phase 2 compatibility
            name = kwargs.get('name', 'unnamed_agent')
            version = kwargs.get('version', '1.0.0')
            super().__init__(name=name, version=version)
            self.config = AgentConfig(name=name, version=version)
        
        # Agent state
        self.status = AgentStatus.IDLE
        self.processing_count = 0
        self.error_count = 0
        self.total_processing_time = 0
        
        # Service clients
        self.redis_client: Optional[redis.Redis] = None
        self.ssm_client = None
        self.secrets_client = None
        self.state_manager: Optional[PipelineStateManager] = None
        
        # Monitoring
        self.metrics = get_metrics_collector()
        self.perf_tracker = get_performance_tracker()
        
        # Logger setup
        if POWERTOOLS_AVAILABLE and self.config.ecs_optimized:
            self.logger = powertools_logger
        else:
            self.logger = logging.getLogger(self.config.name)
        
        # Initialize AWS clients if available
        if AWS_AVAILABLE and self.config.ecs_optimized:
            self._init_aws_clients()
    
    def _init_aws_clients(self):
        """Initialize AWS service clients for ECS mode"""
        try:
            session = boto3.Session(region_name=self.config.aws_region)
            self.ssm_client = session.client('ssm')
            self.secrets_client = session.client('secretsmanager')
            self.logger.info("AWS clients initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize AWS clients: {e}")
    
    async def initialize(self):
        """Initialize agent resources"""
        self.logger.info(f"Initializing {self.config.name} v{self.config.version}")
        
        # Initialize Redis if enabled
        if self.config.enable_caching and REDIS_AVAILABLE:
            await self._init_redis()
        
        # Initialize state manager if enabled
        if self.config.enable_state_management:
            self.state_manager = PipelineStateManager()
            await self.state_manager.initialize()
        
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
    
    async def execute(self, input_data: Any, context: Optional[Any] = None) -> AgentResult:
        """
        Execute agent with unified interface
        Supports both Phase 2 AgentInput and ECS dict input
        """
        # Normalize input
        if isinstance(input_data, AgentInput):
            # Phase 2 mode
            agent_input = input_data
            agent_context = AgentContext(
                trace_id=input_data.context.pipeline_id,
                pipeline_context=input_data.context,
                metadata={"source": "phase2"}
            )
        else:
            # ECS mode or dict input
            if isinstance(context, AgentContext):
                agent_context = context
            else:
                agent_context = AgentContext(
                    trace_id=self._generate_trace_id(),
                    metadata={"source": "ecs"}
                )
            
            # Create AgentInput wrapper if needed
            if isinstance(input_data, dict):
                pipeline_ctx = agent_context.pipeline_context or PipelineContext()
                agent_input = AgentInput(
                    context=pipeline_ctx,
                    data=input_data
                )
            else:
                agent_input = input_data
        
        start_time = time.time()
        self.status = AgentStatus.PROCESSING
        timer_id = None
        
        try:
            # Start monitoring
            if self.perf_tracker:
                timer_id = self.perf_tracker.start_timer(f"{self.config.name}_processing")
            
            # Log start
            self.logger.info(
                f"Processing started",
                extra={
                    "agent": self.config.name,
                    "trace_id": agent_context.trace_id
                }
            )
            
            # Publish start event
            if agent_context.pipeline_context:
                await publish_agent_event(
                    EventType.AGENT_STARTED,
                    self.config.name,
                    agent_context.pipeline_context.pipeline_id,
                    {"trace_id": agent_context.trace_id}
                )
            
            # Check cache if enabled
            cached_result = None
            if self.config.enable_caching:
                cached_result = await self._get_cached_result(agent_input, agent_context)
                if cached_result:
                    self.logger.info("Cache hit")
                    return cached_result
            
            # Process with timeout
            if hasattr(self, 'process'):
                # Phase 2 style processing
                result = await asyncio.wait_for(
                    self.process(agent_input),
                    timeout=self.config.timeout
                )
            else:
                # ECS style processing
                result = await asyncio.wait_for(
                    self._process_internal(agent_input.data, agent_context),
                    timeout=self.config.timeout
                )
            
            # Normalize result
            if not isinstance(result, AgentResult):
                # Convert Phase 2 AgentResult to unified AgentResult
                unified_result = AgentResult(
                    success=result.status == ProcessingStatus.COMPLETED,
                    data=result.data,
                    error=result.error,
                    processing_time=time.time() - start_time,
                    status=result.status,
                    agent_name=self.config.name,
                    agent_version=self.config.version,
                    confidence=getattr(result, 'confidence', 0.0),
                    quality_score=getattr(result, 'quality_score', 0.0),
                    metadata=getattr(result, 'metadata', {})
                )
                result = unified_result
            
            # Cache successful results
            if result.success and self.config.enable_caching:
                await self._cache_result(agent_input, result, agent_context)
            
            # Save state if enabled
            if result.success and self.state_manager and agent_context.pipeline_context:
                await self.state_manager.save_agent_result(
                    agent_context.pipeline_context.pipeline_id,
                    self.config.name,
                    result.data
                )
            
            # Update metrics
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            self.total_processing_time += processing_time
            self.processing_count += 1
            
            # Stop timer
            if timer_id and self.perf_tracker:
                self.perf_tracker.stop_timer(timer_id)
            
            # Record metrics
            if self.metrics:
                self.metrics.increment_counter(f"{self.config.name}.processed")
                self.metrics.set_gauge(f"{self.config.name}.confidence", result.confidence)
            
            # Publish completion event
            if agent_context.pipeline_context:
                await publish_agent_event(
                    EventType.AGENT_COMPLETED,
                    self.config.name,
                    agent_context.pipeline_context.pipeline_id,
                    {
                        "success": result.success,
                        "processing_time": processing_time
                    }
                )
            
            self.status = AgentStatus.COMPLETED
            return result
            
        except asyncio.TimeoutError:
            self.status = AgentStatus.TIMEOUT
            self.error_count += 1
            error_msg = f"Processing timeout after {self.config.timeout}s"
            self.logger.error(error_msg)
            
            if agent_context.pipeline_context:
                await publish_agent_event(
                    EventType.AGENT_FAILED,
                    self.config.name,
                    agent_context.pipeline_context.pipeline_id,
                    {"error": error_msg}
                )
            
            return AgentResult(
                success=False,
                error=error_msg,
                status=ProcessingStatus.FAILED,
                agent_name=self.config.name,
                agent_version=self.config.version
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.error_count += 1
            error_msg = f"Processing error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            if agent_context.pipeline_context:
                await publish_agent_event(
                    EventType.AGENT_FAILED,
                    self.config.name,
                    agent_context.pipeline_context.pipeline_id,
                    {"error": error_msg}
                )
            
            return AgentResult(
                success=False,
                error=error_msg,
                status=ProcessingStatus.FAILED,
                agent_name=self.config.name,
                agent_version=self.config.version
            )
        
        finally:
            # Stop timer if still running
            if timer_id and self.perf_tracker:
                try:
                    self.perf_tracker.stop_timer(timer_id)
                except:
                    pass
    
    @abstractmethod
    async def _process_internal(self, input_data: Dict[str, Any], context: AgentContext) -> AgentResult:
        """
        Internal processing method for ECS mode
        Override this OR the process() method from Phase 2
        """
        pass
    
    async def _get_cached_result(self, input_data: Any, context: AgentContext) -> Optional[AgentResult]:
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
    
    async def _cache_result(self, input_data: Any, result: AgentResult, context: AgentContext):
        """Cache result"""
        if not self.redis_client or not result.success:
            return
        
        try:
            cache_key = self._generate_cache_key(input_data, context)
            result_dict = {
                "success": result.success,
                "data": result.data,
                "metadata": result.metadata,
                "confidence": result.confidence,
                "quality_score": result.quality_score
            }
            
            await self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps(result_dict, default=str)
            )
            
        except Exception as e:
            self.logger.warning(f"Cache storage failed: {e}")
    
    def _generate_cache_key(self, input_data: Any, context: AgentContext) -> str:
        """Generate cache key from input"""
        # Extract data for hashing
        if isinstance(input_data, AgentInput):
            data = input_data.data
        elif isinstance(input_data, dict):
            data = input_data
        else:
            data = str(input_data)
        
        key_data = {
            "agent": self.config.name,
            "version": self.config.version,
            "input": data
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
        # Try environment variable first
        value = os.environ.get(key)
        if value:
            return value
        
        # Try SSM Parameter Store (ECS mode)
        if self.ssm_client and self.config.ecs_optimized:
            try:
                param_name = f"/t-developer/{self.config.name}/{key}"
                response = self.ssm_client.get_parameter(Name=param_name)
                return response['Parameter']['Value']
            except:
                pass
        
        return default
    
    async def _get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        if not self.secrets_client or not self.config.ecs_optimized:
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
            "mode": "ecs" if self.config.ecs_optimized else "phase2",
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
        
        # Check state manager
        if self.config.enable_state_management and self.state_manager:
            health["state_manager"] = "enabled"
        
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


# Export classes
__all__ = ['UnifiedBaseAgent', 'AgentConfig', 'AgentContext', 'AgentResult', 'AgentStatus']