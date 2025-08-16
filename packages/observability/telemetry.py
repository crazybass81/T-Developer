"""Telemetry and observability implementation."""

import asyncio
import functools
import logging
import os
import psutil
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Configure structured logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class TelemetryManager:
    """Manages telemetry for the application."""
    
    def __init__(self, service_name: str = "t-developer"):
        """Initialize telemetry manager.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_VERSION: os.getenv("SERVICE_VERSION", "2.0.0"),
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development")
        })
        
        # Initialize providers
        self._init_tracing()
        self._init_metrics()
        self._init_logging()
    
    def _init_tracing(self):
        """Initialize tracing provider."""
        self.tracer_provider = TracerProvider(resource=self.resource)
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(self.service_name)
    
    def _init_metrics(self):
        """Initialize metrics provider."""
        self.meter_provider = MeterProvider(resource=self.resource)
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(self.service_name)
    
    def _init_logging(self):
        """Initialize logging."""
        self.logger = logging.getLogger(self.service_name)
        
        if STRUCTLOG_AVAILABLE:
            structlog.configure(
                processors=[
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
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
    
    def configure_exporters(
        self,
        endpoint: str,
        service_name: Optional[str] = None
    ):
        """Configure OTLP exporters.
        
        Args:
            endpoint: OTLP endpoint
            service_name: Override service name
        """
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
            
            # Configure trace exporter
            trace_exporter = OTLPSpanExporter(endpoint=endpoint)
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(trace_exporter)
            )
            
            # Configure metric exporter
            metric_exporter = OTLPMetricExporter(endpoint=endpoint)
            reader = PeriodicExportingMetricReader(
                exporter=metric_exporter,
                export_interval_millis=60000  # 1 minute
            )
            
        except ImportError:
            self.logger.warning("OTLP exporters not available")
    
    @contextmanager
    def create_span(self, name: str, **attributes):
        """Create a trace span.
        
        Args:
            name: Span name
            **attributes: Span attributes
            
        Yields:
            Span object
        """
        with self.tracer.start_as_current_span(name) as span:
            for key, value in attributes.items():
                span.set_attribute(key, value)
            yield span
    
    def record_counter(
        self,
        name: str,
        value: int,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a counter metric.
        
        Args:
            name: Metric name
            value: Counter value
            labels: Metric labels
        """
        counter = self.meter.create_counter(name)
        counter.add(value, labels or {})
    
    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a histogram metric.
        
        Args:
            name: Metric name
            value: Histogram value
            labels: Metric labels
        """
        histogram = self.meter.create_histogram(name)
        histogram.record(value, labels or {})


class MetricsCollector:
    """Collects various metrics."""
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system metrics.
        
        Returns:
            System metrics dictionary
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_connections": len(psutil.net_connections()),
            "boot_time": psutil.boot_time()
        }
    
    def collect_process_metrics(self) -> Dict[str, float]:
        """Collect process metrics.
        
        Returns:
            Process metrics dictionary
        """
        process = psutil.Process()
        
        return {
            "threads": process.num_threads(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections())
        }
    
    def collect_agent_metrics(
        self,
        agent_name: str,
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect agent-specific metrics.
        
        Args:
            agent_name: Name of the agent
            stats: Agent statistics
            
        Returns:
            Agent metrics dictionary
        """
        requests = stats.get("requests", 0)
        errors = stats.get("errors", 0)
        
        return {
            "agent_name": agent_name,
            "requests": requests,
            "errors": errors,
            "error_rate": errors / requests if requests > 0 else 0,
            "latency_ms": stats.get("latency_ms", 0),
            "last_execution": stats.get("last_execution", None)
        }
    
    def aggregate_metrics(
        self,
        metrics_list: List[Dict[str, Any]],
        key: str
    ) -> Dict[str, float]:
        """Aggregate metrics.
        
        Args:
            metrics_list: List of metrics
            key: Key to aggregate
            
        Returns:
            Aggregated metrics
        """
        values = [m[key] for m in metrics_list if key in m]
        
        if not values:
            return {}
        
        return {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "count": len(values),
            "sum": sum(values)
        }


class TracingManager:
    """Manages distributed tracing."""
    
    def __init__(self):
        """Initialize tracing manager."""
        self.tracer = trace.get_tracer(__name__)
    
    @contextmanager
    def start_trace(self, operation: str, **attributes):
        """Start a trace.
        
        Args:
            operation: Operation name
            **attributes: Trace attributes
            
        Yields:
            Span object
        """
        with self.tracer.start_as_current_span(operation) as span:
            for key, value in attributes.items():
                span.set_attribute(key, value)
            yield span
    
    def trace(self, operation: str):
        """Decorator for tracing functions.
        
        Args:
            operation: Operation name
            
        Returns:
            Decorated function
        """
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.start_trace(operation):
                        return await func(*args, **kwargs)
                return async_wrapper
            else:
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    with self.start_trace(operation):
                        return func(*args, **kwargs)
                return wrapper
        return decorator
    
    def add_event(
        self,
        span: Any,  # OpenTelemetry Span object
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Add event to span.
        
        Args:
            span: Span object
            name: Event name
            attributes: Event attributes
        """
        span.add_event(name, attributes or {})
    
    def record_exception(self, span: Any, exception: Exception):
        """Record exception in span.
        
        Args:
            span: Span object
            exception: Exception to record
        """
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR))


class LogManager:
    """Manages structured logging."""
    
    def __init__(self, service_name: str):
        """Initialize log manager.
        
        Args:
            service_name: Service name
        """
        self.service_name = service_name
        self._correlation_id = None
    
    def get_logger(self, module: str) -> logging.Logger:
        """Get logger for module.
        
        Args:
            module: Module name
            
        Returns:
            Logger object
        """
        return logging.getLogger(f"{self.service_name}.{module}")
    
    def log_structured(
        self,
        level: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Log structured message.
        
        Args:
            level: Log level
            message: Log message
            data: Additional data
        """
        if STRUCTLOG_AVAILABLE:
            logger = structlog.get_logger()
            log_func = getattr(logger, level.lower())
            log_func(message, **(data or {}))
        else:
            logger = self.get_logger("default")
            log_func = getattr(logger, level.lower())
            log_func(f"{message} | {data}")
    
    @contextmanager
    def with_correlation_id(self, correlation_id: str):
        """Context manager for correlation ID.
        
        Args:
            correlation_id: Correlation ID
            
        Yields:
            None
        """
        old_id = self._correlation_id
        self._correlation_id = correlation_id
        try:
            yield
        finally:
            self._correlation_id = old_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID.
        
        Returns:
            Correlation ID
        """
        return self._correlation_id


class HealthChecker:
    """Health checking system."""
    
    def __init__(self):
        """Initialize health checker."""
        self.checks = {}
        self.async_checks = {}
    
    def register_check(
        self,
        name: str,
        check_func: Callable[[], Tuple[bool, str]]
    ):
        """Register health check.
        
        Args:
            name: Check name
            check_func: Function that returns (healthy, message)
        """
        self.checks[name] = check_func
    
    def register_async_check(
        self,
        name: str,
        check_func: Callable[[], Tuple[bool, str]]
    ):
        """Register async health check.
        
        Args:
            name: Check name
            check_func: Async function that returns (healthy, message)
        """
        self.async_checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks.
        
        Returns:
            Health check results
        """
        results = {"checks": {}, "overall": True}
        
        for name, check_func in self.checks.items():
            try:
                healthy, message = check_func()
                results["checks"][name] = {
                    "healthy": healthy,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                if not healthy:
                    results["overall"] = False
            except Exception as e:
                results["checks"][name] = {
                    "healthy": False,
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                results["overall"] = False
        
        return results
    
    async def run_async_checks(self) -> Dict[str, Any]:
        """Run all async health checks.
        
        Returns:
            Health check results
        """
        results = {"checks": {}, "overall": True}
        
        for name, check_func in self.async_checks.items():
            try:
                healthy, message = await check_func()
                results["checks"][name] = {
                    "healthy": healthy,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                if not healthy:
                    results["overall"] = False
            except Exception as e:
                results["checks"][name] = {
                    "healthy": False,
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                results["overall"] = False
        
        return results
    
    def liveness(self) -> Dict[str, Any]:
        """Liveness probe.
        
        Returns:
            Liveness status
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def readiness(self) -> Dict[str, Any]:
        """Readiness probe.
        
        Returns:
            Readiness status
        """
        results = self.run_checks()
        
        return {
            "ready": results["overall"],
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results["checks"]
        }