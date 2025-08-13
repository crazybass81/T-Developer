"""
OpenTelemetry Tracing
분산 트레이싱 및 모니터링
"""

import os
from typing import Optional, Dict, Any, Callable
from functools import wraps
import logging

from opentelemetry import trace, metrics, baggage
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)


class TracingConfig:
    """트레이싱 설정"""

    def __init__(self):
        self.service_name = os.getenv("SERVICE_NAME", "tdeveloper-backend")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")

        # Exporters
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "localhost:4317")
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "localhost:14250")
        self.use_console_exporter = (
            os.getenv("USE_CONSOLE_EXPORTER", "false").lower() == "true"
        )

        # Metrics
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))

        # Sampling
        self.sampling_rate = float(os.getenv("TRACE_SAMPLING_RATE", "1.0"))

        # Resource attributes
        self.resource = Resource.create(
            {
                SERVICE_NAME: self.service_name,
                SERVICE_VERSION: self.service_version,
                "environment": self.environment,
                "deployment.environment": self.environment,
                "service.namespace": "tdeveloper",
                "telemetry.sdk.language": "python",
                "telemetry.sdk.name": "opentelemetry",
                "host.name": os.getenv("HOSTNAME", "unknown"),
            }
        )


class TelemetryManager:
    """텔레메트리 관리자"""

    def __init__(self, config: Optional[TracingConfig] = None):
        self.config = config or TracingConfig()
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None

        # Metrics
        self.request_counter = None
        self.request_duration = None
        self.active_requests = None
        self.error_counter = None

    def initialize(self):
        """텔레메트리 초기화"""
        try:
            # Initialize tracing
            self._init_tracing()

            # Initialize metrics
            self._init_metrics()

            # Auto-instrument libraries
            self._auto_instrument()

            logger.info("Telemetry initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize telemetry: {e}")

    def _init_tracing(self):
        """트레이싱 초기화"""
        # Create tracer provider
        self.tracer_provider = TracerProvider(
            resource=self.config.resource,
            active_span_processor=BatchSpanProcessor(
                OTLPSpanExporter(endpoint=self.config.otlp_endpoint, insecure=True)
            )
            if self.config.environment != "development"
            else None,
        )

        # Add Jaeger exporter
        if self.config.environment in ["staging", "production"]:
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.config.jaeger_endpoint.split(":")[0],
                agent_port=int(self.config.jaeger_endpoint.split(":")[1]),
                max_tag_value_length=8192,
            )
            self.tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

        # Add console exporter for development
        if self.config.use_console_exporter:
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(ConsoleSpanExporter())
            )

        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)

        # Set propagator for distributed tracing
        set_global_textmap(B3MultiFormat())

        # Get tracer
        self.tracer = trace.get_tracer(
            self.config.service_name, self.config.service_version
        )

    def _init_metrics(self):
        """메트릭 초기화"""
        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=self.config.resource, metric_readers=[PrometheusMetricReader()]
        )

        # Set global meter provider
        set_meter_provider(self.meter_provider)

        # Get meter
        self.meter = metrics.get_meter(
            self.config.service_name, self.config.service_version
        )

        # Create metrics
        self.request_counter = self.meter.create_counter(
            "http_requests_total", description="Total number of HTTP requests", unit="1"
        )

        self.request_duration = self.meter.create_histogram(
            "http_request_duration_seconds",
            description="HTTP request duration in seconds",
            unit="s",
        )

        self.active_requests = self.meter.create_up_down_counter(
            "http_active_requests",
            description="Number of active HTTP requests",
            unit="1",
        )

        self.error_counter = self.meter.create_counter(
            "http_errors_total", description="Total number of HTTP errors", unit="1"
        )

        # Start Prometheus metrics server
        if self.config.environment != "testing":
            start_http_server(self.config.prometheus_port)
            logger.info(
                f"Prometheus metrics available at port {self.config.prometheus_port}"
            )

    def _auto_instrument(self):
        """자동 계측"""
        # FastAPI
        FastAPIInstrumentor.instrument(
            tracer_provider=self.tracer_provider, meter_provider=self.meter_provider
        )

        # Requests
        RequestsInstrumentor().instrument(tracer_provider=self.tracer_provider)

        # SQLAlchemy
        from ..database.base import engine

        SQLAlchemyInstrumentor().instrument(
            engine=engine, tracer_provider=self.tracer_provider
        )

        # Redis
        RedisInstrumentor().instrument(tracer_provider=self.tracer_provider)

        # Celery
        CeleryInstrumentor().instrument(tracer_provider=self.tracer_provider)

        # Logging
        LoggingInstrumentor().instrument(
            tracer_provider=self.tracer_provider, set_logging_format=True
        )

    def create_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """새 스팬 생성"""
        if not self.tracer:
            return None

        span = self.tracer.start_span(name, kind=kind, attributes=attributes or {})

        return span

    def trace_function(
        self,
        name: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """함수 트레이싱 데코레이터"""

        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"

                with self.tracer.start_as_current_span(
                    span_name, kind=kind, attributes=attributes or {}
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"

                with self.tracer.start_as_current_span(
                    span_name, kind=kind, attributes=attributes or {}
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise

            # Return appropriate wrapper
            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def record_metric(
        self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None
    ):
        """메트릭 기록"""
        if metric_name == "request_count":
            self.request_counter.add(1, labels or {})
        elif metric_name == "request_duration":
            self.request_duration.record(value, labels or {})
        elif metric_name == "active_requests":
            self.active_requests.add(value, labels or {})
        elif metric_name == "error_count":
            self.error_counter.add(1, labels or {})

    def get_current_span(self) -> Optional[trace.Span]:
        """현재 활성 스팬 가져오기"""
        return trace.get_current_span()

    def add_span_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """현재 스팬에 이벤트 추가"""
        span = self.get_current_span()
        if span:
            span.add_event(name, attributes or {})

    def set_span_attribute(self, key: str, value: Any):
        """현재 스팬에 속성 추가"""
        span = self.get_current_span()
        if span:
            span.set_attribute(key, value)

    def set_baggage(self, key: str, value: str):
        """Baggage 설정 (컨텍스트 전파)"""
        ctx = baggage.set_baggage(key, value)
        return ctx

    def get_baggage(self, key: str) -> Optional[str]:
        """Baggage 가져오기"""
        return baggage.get_baggage(key)

    def shutdown(self):
        """텔레메트리 종료"""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        if self.meter_provider:
            self.meter_provider.shutdown()


# Global instance
telemetry = TelemetryManager()


# Decorator for tracing
def trace_method(
    name: Optional[str] = None, kind: SpanKind = SpanKind.INTERNAL, **attributes
):
    """메서드 트레이싱 데코레이터"""
    return telemetry.trace_function(name, kind, attributes)
