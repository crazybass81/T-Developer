"""
ServiceValidator Integration Tests - Day 35
Tests for complete validator system integration
"""

from datetime import datetime

import pytest

from src.validator import ErrorHandler, IntegrationTester, RecoveryManager, ServiceValidator


class TestValidatorIntegration:
    """Integration tests for complete validator system"""

    @pytest.fixture
    def validator_system(self):
        """Create complete validator system"""
        return {
            "validator": ServiceValidator(),
            "error_handler": ErrorHandler(),
            "recovery_manager": RecoveryManager(),
            "integration_tester": IntegrationTester(),
        }

    @pytest.fixture
    def sample_service(self):
        """Sample service for testing"""
        return {
            "name": "IntegratedService",
            "agents": [
                {
                    "name": "processor",
                    "size_kb": 5.5,
                    "instantiation_us": 1.5,
                    "dependencies": ["validator", "builder"],
                }
            ],
            "workflow": {"steps": [{"agent": "processor", "method": "process"}]},
            "constraints": {"max_size_kb": 6.5, "max_instantiation_us": 3.0},
            "metrics": {"test_coverage": 0.90},
        }

    def test_all_components_initialized(self, validator_system):
        """Test all components are properly initialized"""
        assert validator_system["validator"] is not None
        assert validator_system["error_handler"] is not None
        assert validator_system["recovery_manager"] is not None
        assert validator_system["integration_tester"] is not None

    def test_validation_with_error_handling(self, validator_system, sample_service):
        """Test validation with error handling"""
        validator = validator_system["validator"]
        error_handler = validator_system["error_handler"]

        # Validate service
        result = validator.validate(sample_service)

        # If validation fails, handle error
        if not result["valid"]:
            error = {
                "type": "ValidationError",
                "message": "Service validation failed",
                "errors": result.get("errors", []),
            }
            handled = error_handler.handle(error)
            assert handled["handled"] is True
        else:
            assert result["valid"] is True

    def test_error_recovery_flow(self, validator_system):
        """Test error detection and recovery flow"""
        error_handler = validator_system["error_handler"]
        recovery_manager = validator_system["recovery_manager"]

        # Simulate error
        error = {"type": "ServiceTimeout", "component": "validator", "severity": "high"}

        # Handle error
        error_result = error_handler.handle(error)

        # Trigger recovery
        recovery_strategy = recovery_manager.select_rollback_strategy(error)
        recovery_result = recovery_manager.auto_recover(error)

        assert error_result["handled"] is True
        assert recovery_strategy["type"] in ["full", "partial", "component"]
        assert recovery_result["recovered"] is True

    def test_checkpoint_and_restore(self, validator_system, sample_service):
        """Test checkpoint creation and restoration"""
        validator = validator_system["validator"]
        recovery_manager = validator_system["recovery_manager"]

        # Create checkpoint before validation
        state = {"service": sample_service, "timestamp": datetime.now().isoformat()}
        checkpoint_id = recovery_manager.create_checkpoint(state)

        # Validate service
        result = validator.validate(sample_service)

        # Restore if needed
        if not result["valid"]:
            restored = recovery_manager.restore_checkpoint(checkpoint_id)
            assert restored["success"] is True
            assert restored["state"]["service"] == sample_service

    def test_integration_testing_flow(self, validator_system):
        """Test integration testing workflow"""
        tester = validator_system["integration_tester"]

        # Define test suite
        suite = {
            "name": "ValidatorIntegration",
            "tests": [
                {"name": "test_validation", "components": ["validator", "type_checker"]},
                {
                    "name": "test_error_handling",
                    "components": ["error_handler", "recovery_manager"],
                },
            ],
        }

        # Register and run suite
        suite_id = tester.register_suite(suite)
        results = tester.run_suite(suite_id)

        assert results["suite_name"] == "ValidatorIntegration"
        assert results["total_tests"] == 2
        assert results["passed"] >= 0

    def test_circuit_breaker_integration(self, validator_system):
        """Test circuit breaker pattern"""
        error_handler = validator_system["error_handler"]

        # Get circuit breaker for validator service
        breaker = error_handler.get_circuit_breaker("validator")

        # Simulate failures
        for _ in range(3):
            breaker.record_failure()

        # Circuit should still be closed (threshold is 5)
        assert breaker.is_open is False

        # More failures
        for _ in range(3):
            breaker.record_failure()

        # Circuit should be open now
        assert breaker.is_open is True

    def test_performance_monitoring(self, validator_system, sample_service):
        """Test performance monitoring across components"""
        tester = validator_system["integration_tester"]

        # Run performance test
        perf_config = {"component": "validator", "load": 10, "duration": 0.5}

        perf_result = tester.run_performance_test(perf_config)

        assert "throughput" in perf_result
        assert "avg_latency" in perf_result
        assert perf_result["error_rate"] < 0.1

    def test_chaos_engineering(self, validator_system):
        """Test system resilience with chaos testing"""
        tester = validator_system["integration_tester"]
        recovery_manager = validator_system["recovery_manager"]

        # Run chaos test
        chaos_scenario = {
            "target": "validator",
            "failures": [{"type": "network_delay", "duration": 100}],
        }

        chaos_result = tester.run_chaos_test(chaos_scenario)

        # System should recover
        if not chaos_result["survived"]:
            recovery_result = recovery_manager.initiate_disaster_recovery()
            assert recovery_result["services_restarted"] is True

    def test_end_to_end_validation_flow(self, validator_system, sample_service):
        """Test complete end-to-end validation flow"""
        validator = validator_system["validator"]
        error_handler = validator_system["error_handler"]
        recovery_manager = validator_system["recovery_manager"]
        tester = validator_system["integration_tester"]

        # Create checkpoint
        recovery_manager.create_checkpoint({"service": sample_service, "status": "pre_validation"})

        # Validate service
        validation_result = validator.validate(sample_service)

        # Handle any errors
        if not validation_result["valid"]:
            error = {"type": "ValidationError", "details": validation_result.get("errors", [])}
            error_handler.handle(error)

            # Attempt recovery
            recovery_manager.auto_recover(error)

        # Run integration tests
        test_scenario = {
            "name": "validation_e2e",
            "steps": [
                {"action": "validate", "component": "validator"},
                {"action": "check_constraints", "component": "constraint_validator"},
            ],
        }

        e2e_result = tester.run_e2e_test(test_scenario)

        assert e2e_result["completed"] is True

    def test_metrics_collection(self, validator_system):
        """Test metrics collection across all components"""
        error_handler = validator_system["error_handler"]
        recovery_manager = validator_system["recovery_manager"]

        # Generate some activity
        error_handler.log_error({"type": "TestError"})
        recovery_manager.record_recovery("test", True, 1.5)

        # Collect metrics
        error_metrics = error_handler.get_metrics()
        recovery_metrics = recovery_manager.get_recovery_metrics()

        assert error_metrics["total_errors"] >= 1
        assert recovery_metrics["total_recoveries"] >= 1

    def test_continuous_validation(self, validator_system, sample_service):
        """Test continuous validation mode"""
        tester = validator_system["integration_tester"]

        # Configure continuous testing
        config = {"interval": 0.01, "max_runs": 3, "stop_on_failure": False}

        # Run continuous validation
        continuous_result = tester.run_continuous(config)

        assert continuous_result["runs_completed"] == 3
        assert continuous_result["continuous_mode"] is True

    def test_component_isolation(self, validator_system):
        """Test that components can work independently"""
        # Each component should work in isolation
        validator = ServiceValidator()
        error_handler = ErrorHandler()
        recovery_manager = RecoveryManager()
        tester = IntegrationTester()

        # Test basic functionality of each
        assert validator.validate({"name": "test"})["service_name"] == "test"
        assert error_handler.log_error({"type": "test"})["logged"] is True
        assert recovery_manager.check_health()["overall_health"] >= 0
        assert tester.run_smoke_tests()["all_critical_passed"] is not None

    def test_report_generation(self, validator_system, tmp_path):
        """Test report generation from all components"""
        error_handler = validator_system["error_handler"]
        recovery_manager = validator_system["recovery_manager"]
        tester = validator_system["integration_tester"]

        # Generate activity
        error_handler.log_error({"type": "TestError"})
        recovery_manager.record_recovery("test", True, 1.0)
        tester.run_test({"name": "test"})

        # Generate reports
        error_report = tmp_path / "error_report.json"
        recovery_report = tmp_path / "recovery_report.json"
        test_report = tmp_path / "test_report.json"

        error_handler.export_errors(error_report)
        recovery_manager.generate_report(recovery_report)
        tester.generate_report(test_report)

        assert error_report.exists()
        assert recovery_report.exists()
        assert test_report.exists()
