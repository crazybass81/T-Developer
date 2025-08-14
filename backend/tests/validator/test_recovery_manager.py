"""
RecoveryManager Tests - Day 33
Tests for system recovery and rollback capabilities
"""

import json
import time
from datetime import datetime

import pytest

from src.validator.recovery_manager import RecoveryManager


class TestRecoveryManager:
    """Tests for RecoveryManager"""

    @pytest.fixture
    def manager(self):
        """Create RecoveryManager instance"""
        return RecoveryManager()

    @pytest.fixture
    def sample_state(self):
        """Sample system state"""
        return {
            "version": "1.0.0",
            "services": {
                "validator": {"status": "running", "health": 100},
                "builder": {"status": "running", "health": 95},
            },
            "configuration": {"max_workers": 4, "timeout": 30, "retry_limit": 3},
            "timestamp": datetime.now().isoformat(),
        }

    def test_manager_initialization(self, manager):
        """Test RecoveryManager initialization"""
        assert manager is not None
        assert hasattr(manager, "checkpoints")
        assert hasattr(manager, "recovery_plans")
        assert manager.max_checkpoints == 10

    def test_create_checkpoint(self, manager, sample_state):
        """Test checkpoint creation"""
        checkpoint_id = manager.create_checkpoint(sample_state)

        assert checkpoint_id is not None
        assert len(manager.checkpoints) == 1
        assert manager.checkpoints[0]["state"] == sample_state

    def test_restore_checkpoint(self, manager, sample_state):
        """Test checkpoint restoration"""
        checkpoint_id = manager.create_checkpoint(sample_state)

        # Modify current state
        current_state = sample_state.copy()
        current_state["services"]["validator"]["status"] = "failed"

        restored = manager.restore_checkpoint(checkpoint_id)

        assert restored["success"] is True
        assert restored["state"]["services"]["validator"]["status"] == "running"

    def test_automatic_checkpoint_rotation(self, manager):
        """Test automatic checkpoint rotation"""
        # Create more than max_checkpoints
        for i in range(15):
            manager.create_checkpoint({"version": f"1.0.{i}"})

        assert len(manager.checkpoints) == 10
        # Oldest should be removed
        versions = [c["state"]["version"] for c in manager.checkpoints]
        assert "1.0.0" not in versions
        assert "1.0.14" in versions

    def test_rollback_strategy(self, manager, sample_state):
        """Test rollback strategy selection"""
        error = {"type": "DeploymentError", "severity": "high", "component": "validator"}

        strategy = manager.select_rollback_strategy(error)

        assert strategy["type"] in ["full", "partial", "component"]
        assert strategy["confidence"] > 0.5
        assert "steps" in strategy

    def test_service_restart(self, manager):
        """Test service restart functionality"""
        service_name = "validator"

        result = manager.restart_service(service_name)

        assert result["restarted"] is True
        assert result["service"] == service_name
        assert "duration" in result

    def test_graceful_degradation(self, manager):
        """Test graceful degradation"""
        failed_components = ["optimizer", "analyzer"]

        result = manager.degrade_gracefully(failed_components)

        assert result["degraded"] is True
        assert result["disabled_features"] == failed_components
        assert result["running_features"] is not None

    def test_health_check(self, manager):
        """Test system health check"""
        health = manager.check_health()

        assert "overall_health" in health
        assert "component_health" in health
        assert 0 <= health["overall_health"] <= 100

    def test_auto_recovery(self, manager):
        """Test automatic recovery"""
        issue = {"type": "MemoryLeak", "component": "cache", "severity": "medium"}

        result = manager.auto_recover(issue)

        assert result["recovered"] is True
        assert result["action"] in ["clear_cache", "restart_component", "gc_collect"]
        assert "time_taken" in result

    def test_recovery_plan_execution(self, manager):
        """Test recovery plan execution"""
        plan = {
            "name": "database_recovery",
            "steps": [
                {"action": "stop_service", "target": "api"},
                {"action": "restore_backup", "target": "database"},
                {"action": "start_service", "target": "api"},
            ],
        }

        result = manager.execute_recovery_plan(plan)

        assert result["executed"] is True
        assert result["steps_completed"] == 3
        assert "duration" in result

    def test_failover_mechanism(self, manager):
        """Test failover to backup systems"""
        primary_failure = {"service": "database", "type": "ConnectionLost"}

        result = manager.failover(primary_failure)

        assert result["failover_success"] is True
        assert result["new_primary"] == "database_backup"
        assert result["old_primary_status"] == "standby"

    def test_state_validation(self, manager, sample_state):
        """Test state validation before restore"""
        # Valid state
        valid = manager.validate_state(sample_state)
        assert valid["valid"] is True

        # Invalid state
        invalid_state = {"invalid": "structure"}
        invalid = manager.validate_state(invalid_state)
        assert invalid["valid"] is False
        assert "errors" in invalid

    def test_recovery_metrics(self, manager):
        """Test recovery metrics collection"""
        # Simulate some recoveries
        manager.record_recovery("restart", success=True, duration=2.5)
        manager.record_recovery("rollback", success=True, duration=5.0)
        manager.record_recovery("failover", success=False, duration=10.0)

        metrics = manager.get_recovery_metrics()

        assert metrics["total_recoveries"] == 3
        assert metrics["success_rate"] == 2 / 3
        assert metrics["average_duration"] > 0

    def test_disaster_recovery(self, manager):
        """Test disaster recovery mode"""
        result = manager.initiate_disaster_recovery()

        assert result["mode"] == "disaster_recovery"
        assert result["backup_restored"] is True
        assert result["services_restarted"] is True
        assert "recovery_time" in result

    def test_configuration_rollback(self, manager):
        """Test configuration rollback"""
        old_config = {"max_workers": 4, "timeout": 30}
        new_config = {"max_workers": 8, "timeout": 60}

        # Apply new config
        manager.apply_configuration(new_config)

        # Rollback on error
        result = manager.rollback_configuration()

        assert result["rolled_back"] is True
        assert result["restored_config"] == old_config

    def test_recovery_scheduling(self, manager):
        """Test scheduled recovery tasks"""
        task = {"type": "cleanup", "schedule": "hourly", "target": "cache"}

        task_id = manager.schedule_recovery_task(task)

        assert task_id is not None
        scheduled = manager.get_scheduled_tasks()
        assert len(scheduled) == 1
        assert scheduled[0]["id"] == task_id

    def test_recovery_dependencies(self, manager):
        """Test recovery with dependencies"""
        recovery = {"component": "api", "dependencies": ["database", "cache"]}

        result = manager.recover_with_dependencies(recovery)

        assert result["success"] is True
        assert result["order"] == ["database", "cache", "api"]
        assert result["all_recovered"] is True

    def test_recovery_timeout(self, manager):
        """Test recovery timeout handling"""
        slow_recovery = {"action": "restore_large_backup", "timeout": 0.1}  # 100ms timeout

        def slow_operation():
            time.sleep(0.2)  # Takes longer than timeout

        result = manager.recover_with_timeout(slow_operation, slow_recovery["timeout"])

        assert result["success"] is False
        assert result["error"] == "timeout"

    def test_incremental_recovery(self, manager):
        """Test incremental recovery approach"""
        issues = [
            {"component": "cache", "severity": "low"},
            {"component": "optimizer", "severity": "medium"},
            {"component": "database", "severity": "high"},
        ]

        result = manager.incremental_recovery(issues)

        assert result["strategy"] == "incremental"
        assert result["phases"] == 3
        assert result["success"] is True

    def test_recovery_report(self, manager, tmp_path):
        """Test recovery report generation"""
        # Perform some recoveries
        manager.record_recovery("restart", True, 2.5)
        manager.record_recovery("rollback", False, 5.0)

        report_file = tmp_path / "recovery_report.json"
        manager.generate_report(report_file)

        assert report_file.exists()

        with open(report_file) as f:
            report = json.load(f)
        assert "recoveries" in report
        assert "metrics" in report
