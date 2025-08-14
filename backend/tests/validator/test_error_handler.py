"""
ErrorHandler Tests - Day 32
Tests for error handling and recovery system
"""

import json
from datetime import datetime

import pytest

from src.validator.error_handler import ErrorHandler


class TestErrorHandler:
    """Tests for ErrorHandler"""

    @pytest.fixture
    def handler(self):
        """Create ErrorHandler instance"""
        return ErrorHandler()

    @pytest.fixture
    def sample_error(self):
        """Sample error data"""
        return {
            "type": "ValidationError",
            "message": "Service validation failed",
            "code": "VAL_001",
            "severity": "high",
            "context": {
                "service": "DataProcessor",
                "component": "parser",
                "timestamp": datetime.now().isoformat(),
            },
        }

    def test_handler_initialization(self, handler):
        """Test ErrorHandler initialization"""
        assert handler is not None
        assert hasattr(handler, "error_log")
        assert hasattr(handler, "recovery_strategies")
        assert handler.max_retries == 3

    def test_log_error(self, handler, sample_error):
        """Test error logging"""
        result = handler.log_error(sample_error)

        assert result["logged"] is True
        assert result["error_id"] is not None
        assert len(handler.error_log) == 1
        assert handler.error_log[0]["type"] == "ValidationError"

    def test_categorize_error(self, handler, sample_error):
        """Test error categorization"""
        category = handler.categorize(sample_error)

        assert category["category"] == "validation"
        assert category["severity"] == "high"
        assert category["recoverable"] is True

    def test_handle_validation_error(self, handler):
        """Test validation error handling"""
        error = {
            "type": "ValidationError",
            "message": "Invalid service structure",
            "recoverable": True,
        }

        result = handler.handle(error)

        assert result["handled"] is True
        assert result["strategy"] == "retry_with_fixes"
        assert "recovery_steps" in result

    def test_handle_runtime_error(self, handler):
        """Test runtime error handling"""
        error = {"type": "RuntimeError", "message": "Service execution failed", "code": "RUN_001"}

        result = handler.handle(error)

        assert result["handled"] is True
        assert result["strategy"] in ["restart", "rollback", "failover"]

    def test_handle_critical_error(self, handler):
        """Test critical error handling"""
        error = {"type": "CriticalError", "severity": "critical", "message": "System failure"}

        result = handler.handle(error)

        assert result["handled"] is True
        assert result["escalated"] is True
        assert result["alert_sent"] is True

    def test_retry_mechanism(self, handler):
        """Test retry mechanism"""

        def failing_operation():
            raise ValueError("Operation failed")

        result = handler.retry(failing_operation, max_attempts=3)

        assert result["success"] is False
        assert result["attempts"] == 3
        assert "error" in result

    def test_retry_with_backoff(self, handler):
        """Test exponential backoff retry"""
        attempts = []

        def operation_with_tracking():
            attempts.append(datetime.now())
            if len(attempts) < 2:
                raise ValueError("Still failing")
            return "Success"

        result = handler.retry_with_backoff(operation_with_tracking)

        assert result["success"] is True
        assert result["value"] == "Success"
        assert len(attempts) == 2

    def test_circuit_breaker(self, handler):
        """Test circuit breaker pattern"""
        breaker = handler.get_circuit_breaker("test_service")

        # Simulate failures
        for _ in range(5):
            breaker.record_failure()

        assert breaker.is_open is True
        assert breaker.should_attempt() is False

        # Test half-open state after timeout
        breaker.last_failure_time = datetime.now().timestamp() - 61
        assert breaker.should_attempt() is True

    def test_error_aggregation(self, handler):
        """Test error aggregation and patterns"""
        # Log multiple similar errors
        for i in range(10):
            handler.log_error(
                {
                    "type": "ValidationError",
                    "message": f"Validation failed {i}",
                    "component": "parser",
                }
            )

        patterns = handler.analyze_patterns()

        assert patterns["most_common_type"] == "ValidationError"
        assert patterns["error_rate"] > 0
        assert "hotspots" in patterns

    def test_recovery_strategy_selection(self, handler):
        """Test recovery strategy selection"""
        error = {"type": "ServiceTimeout", "component": "api_gateway", "retry_count": 2}

        strategy = handler.select_recovery_strategy(error)

        assert strategy["name"] in ["increase_timeout", "use_cache", "failover"]
        assert strategy["confidence"] > 0.5

    def test_error_context_enrichment(self, handler):
        """Test error context enrichment"""
        basic_error = {"type": "Error", "message": "Something went wrong"}

        enriched = handler.enrich_context(basic_error)

        assert "timestamp" in enriched
        assert "stack_trace" in enriched
        assert "environment" in enriched
        assert "session_id" in enriched

    def test_error_notification(self, handler):
        """Test error notification system"""
        error = {
            "type": "CriticalError",
            "severity": "critical",
            "message": "Database connection lost",
        }

        result = handler.notify(error)

        assert result["notifications_sent"] > 0
        assert "email" in result["channels"]
        assert "slack" in result["channels"]

    def test_error_recovery_tracking(self, handler):
        """Test recovery action tracking"""
        error_id = "ERR_123"

        handler.start_recovery(error_id, "restart_service")
        status = handler.get_recovery_status(error_id)

        assert status["in_progress"] is True
        assert status["strategy"] == "restart_service"

        handler.complete_recovery(error_id, success=True)
        status = handler.get_recovery_status(error_id)

        assert status["in_progress"] is False
        assert status["success"] is True

    def test_error_metrics(self, handler):
        """Test error metrics collection"""
        # Generate some errors
        for _ in range(5):
            handler.log_error({"type": "ValidationError"})
        for _ in range(3):
            handler.log_error({"type": "RuntimeError"})

        metrics = handler.get_metrics()

        assert metrics["total_errors"] == 8
        assert metrics["error_types"]["ValidationError"] == 5
        assert metrics["error_types"]["RuntimeError"] == 3
        assert "error_rate" in metrics

    def test_auto_healing(self, handler):
        """Test auto-healing capabilities"""
        error = {
            "type": "ConfigurationError",
            "message": "Invalid configuration",
            "config_key": "max_workers",
            "current_value": -1,
        }

        result = handler.auto_heal(error)

        assert result["healed"] is True
        assert result["action"] == "reset_to_default"
        assert result["new_value"] == 4  # default value

    def test_error_deduplication(self, handler):
        """Test error deduplication"""
        # Log same error multiple times
        error = {"type": "DuplicateError", "message": "Same error"}

        for _ in range(10):
            handler.log_error(error)

        unique_errors = handler.get_unique_errors()

        assert len(unique_errors) == 1
        assert unique_errors[0]["count"] == 10

    def test_error_correlation(self, handler):
        """Test error correlation"""
        # Log related errors
        handler.log_error(
            {"type": "ConnectionError", "service": "database", "correlation_id": "CORR_001"}
        )
        handler.log_error({"type": "QueryError", "service": "api", "correlation_id": "CORR_001"})

        correlated = handler.get_correlated_errors("CORR_001")

        assert len(correlated) == 2
        assert {e["type"] for e in correlated} == {"ConnectionError", "QueryError"}

    def test_error_export(self, handler, sample_error, tmp_path):
        """Test error log export"""
        handler.log_error(sample_error)

        export_file = tmp_path / "error_log.json"
        handler.export_errors(export_file)

        assert export_file.exists()

        with open(export_file) as f:
            exported = json.load(f)
        assert len(exported["errors"]) == 1
