"""Tests for observability implementation."""

from unittest.mock import Mock, patch

import pytest
from packages.observability.telemetry import (
    HealthChecker,
    LogManager,
    MetricsCollector,
    TelemetryManager,
    TracingManager,
)


class TestTelemetryManager:
    """Test telemetry manager."""

    def test_initialization(self):
        """Test telemetry manager initialization."""
        manager = TelemetryManager()

        assert manager.tracer is not None
        assert manager.meter is not None
        assert manager.logger is not None

    def test_configure_exporters(self):
        """Test exporter configuration."""
        manager = TelemetryManager()

        # Just test that the method doesn't crash
        # OTLP exporters are optional dependencies
        manager.configure_exporters(endpoint="http://localhost:4317", service_name="test-service")

        # Should log warning about missing exporters
        assert True

    def test_create_span(self):
        """Test span creation."""
        manager = TelemetryManager()

        with manager.create_span("test_operation") as span:
            span.set_attribute("test.attribute", "value")
            assert span is not None

    def test_record_metric(self):
        """Test metric recording."""
        manager = TelemetryManager()

        # Record counter
        manager.record_counter("test.counter", 1, {"label": "value"})

        # Record histogram
        manager.record_histogram("test.histogram", 100, {"label": "value"})

        # No exceptions should be raised
        assert True


class TestMetricsCollector:
    """Test metrics collector."""

    @pytest.fixture
    def collector(self):
        """Create metrics collector."""
        return MetricsCollector()

    def test_collect_system_metrics(self, collector):
        """Test system metrics collection."""
        metrics = collector.collect_system_metrics()

        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_usage" in metrics
        assert metrics["cpu_percent"] >= 0
        assert metrics["memory_percent"] >= 0

    def test_collect_process_metrics(self, collector):
        """Test process metrics collection."""
        metrics = collector.collect_process_metrics()

        assert "threads" in metrics
        assert "memory_mb" in metrics
        assert "cpu_percent" in metrics
        assert metrics["threads"] >= 1

    def test_collect_agent_metrics(self, collector):
        """Test agent metrics collection."""
        agent_stats = {"requests": 100, "errors": 5, "latency_ms": 250}

        metrics = collector.collect_agent_metrics("test_agent", agent_stats)

        assert metrics["agent_name"] == "test_agent"
        assert metrics["requests"] == 100
        assert metrics["errors"] == 5
        assert metrics["error_rate"] == 0.05
        assert metrics["latency_ms"] == 250

    def test_aggregate_metrics(self, collector):
        """Test metrics aggregation."""
        metrics_list = [
            {"value": 10, "timestamp": 1},
            {"value": 20, "timestamp": 2},
            {"value": 30, "timestamp": 3},
        ]

        aggregated = collector.aggregate_metrics(metrics_list, "value")

        assert aggregated["avg"] == 20
        assert aggregated["min"] == 10
        assert aggregated["max"] == 30
        assert aggregated["count"] == 3


class TestTracingManager:
    """Test tracing manager."""

    @pytest.fixture
    def tracer(self):
        """Create tracing manager."""
        return TracingManager()

    def test_start_trace(self, tracer):
        """Test starting a trace."""
        with tracer.start_trace("test_operation") as span:
            assert span is not None
            span.set_attribute("test", "value")

    def test_trace_decorator(self, tracer):
        """Test trace decorator."""

        @tracer.trace("test_function")
        def test_func(x, y):
            return x + y

        result = test_func(1, 2)
        assert result == 3

    @pytest.mark.asyncio
    async def test_async_trace_decorator(self, tracer):
        """Test async trace decorator."""

        @tracer.trace("async_test_function")
        async def async_test_func(x, y):
            return x + y

        result = await async_test_func(1, 2)
        assert result == 3

    def test_add_event(self, tracer):
        """Test adding events to span."""
        with tracer.start_trace("test_operation") as span:
            tracer.add_event(span, "test_event", {"key": "value"})
            # No exception should be raised
            assert True

    def test_record_exception(self, tracer):
        """Test recording exceptions."""
        with tracer.start_trace("test_operation") as span:
            try:
                raise ValueError("Test error")
            except ValueError as e:
                tracer.record_exception(span, e)
                # No exception should be raised
                assert True


class TestLogManager:
    """Test log manager."""

    @pytest.fixture
    def log_manager(self):
        """Create log manager."""
        return LogManager("test_service")

    def test_get_logger(self, log_manager):
        """Test getting logger."""
        logger = log_manager.get_logger("test_module")

        assert logger is not None
        assert logger.name == "test_service.test_module"

    def test_structured_logging(self, log_manager):
        """Test structured logging."""
        logger = log_manager.get_logger("test")

        with patch("structlog.get_logger") as mock_structlog:
            mock_logger = Mock()
            mock_structlog.return_value = mock_logger

            log_manager.log_structured("info", "Test message", {"key": "value"})

            mock_structlog.assert_called()

    def test_correlation_id(self, log_manager):
        """Test correlation ID in logs."""
        correlation_id = "test-correlation-123"

        with log_manager.with_correlation_id(correlation_id):
            logger = log_manager.get_logger("test")
            # Correlation ID should be in context
            assert log_manager.get_correlation_id() == correlation_id

    def test_log_levels(self, log_manager):
        """Test different log levels."""
        logger = log_manager.get_logger("test")

        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        assert True


class TestHealthChecker:
    """Test health checker."""

    @pytest.fixture
    def health_checker(self):
        """Create health checker."""
        return HealthChecker()

    def test_register_check(self, health_checker):
        """Test registering health check."""

        def check_database():
            return True, "Database is healthy"

        health_checker.register_check("database", check_database)

        assert "database" in health_checker.checks

    def test_run_checks(self, health_checker):
        """Test running health checks."""
        # Register checks
        health_checker.register_check("service1", lambda: (True, "Service 1 is healthy"))
        health_checker.register_check("service2", lambda: (False, "Service 2 is down"))

        results = health_checker.run_checks()

        assert results["overall"] is False
        assert results["checks"]["service1"]["healthy"] is True
        assert results["checks"]["service2"]["healthy"] is False

    def test_liveness_probe(self, health_checker):
        """Test liveness probe."""
        result = health_checker.liveness()

        assert result["status"] == "alive"
        assert "timestamp" in result

    def test_readiness_probe(self, health_checker):
        """Test readiness probe."""
        # Register a failing check
        health_checker.register_check("dependency", lambda: (False, "Not ready"))

        result = health_checker.readiness()

        assert result["ready"] is False
        assert "checks" in result

    @pytest.mark.asyncio
    async def test_async_health_check(self, health_checker):
        """Test async health check."""

        async def async_check():
            return True, "Async check passed"

        health_checker.register_async_check("async_service", async_check)

        results = await health_checker.run_async_checks()

        assert results["checks"]["async_service"]["healthy"] is True
