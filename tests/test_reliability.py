"""Comprehensive tests for reliability components.

Phase 6: P6-TEST-2 - Reliability Testing
Test coverage >85% for all reliability engineering components.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from packages.performance.chaos_engineering import (
    ChaosExperiment,
    ChaosOrchestrator,
    ChaosResult,
    ChaosTarget,
    CPUStressInjector,
    ExperimentStatus,
    FailureType,
    MemoryStressInjector,
    NetworkLatencyInjector,
    ProcessKillInjector,
    create_t_developer_experiments,
    run_chaos_experiments,
)

# Import reliability components
from packages.performance.load_testing import (
    K6Runner,
    LoadTestConfig,
    LoadTestManager,
    LoadTestResult,
    LoadTestSuite,
    run_load_tests,
)
from packages.performance.monitoring import (
    Alert,
    AlertManager,
    AlertSeverity,
    AlertStatus,
    EmailNotificationChannel,
    Metric,
    MetricCollector,
    MetricType,
    MonitoringDashboard,
    NotificationChannel,
    SlackNotificationChannel,
    create_t_developer_alerts,
    start_monitoring_system,
)


# Test fixtures
@pytest.fixture
def temp_directory():
    """Temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_k6_script(temp_directory):
    """Sample k6 script for testing."""
    script_content = """
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  duration: '10s',
  vus: 1,
};

export default function() {
  const response = http.get('http://httpbin.org/get');
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
}
"""

    script_path = temp_directory / "test-script.js"
    script_path.write_text(script_content)
    return script_path


@pytest.fixture
def mock_k6_output():
    """Mock k6 output for testing."""
    return """
     ✓ status is 200

     checks.....................: 100.00% ✓ 10      ✗ 0
     data_received..............: 3.2 kB  320 B/s
     data_sent..................: 1.2 kB  120 B/s
     http_req_blocked...........: avg=123.45ms min=1.23ms med=100.23ms max=245.67ms p(90)=200.34ms p(95)=223.45ms
     http_req_connecting........: avg=45.67ms  min=0s     med=34.56ms  max=89.12ms  p(90)=78.9ms   p(95)=83.45ms
     http_req_duration..........: avg=156.78ms min=123.45ms med=150.23ms max=189.34ms p(90)=178.9ms p(95)=184.12ms
     http_req_failed............: 0.00%   ✓ 0       ✗ 10
     http_req_receiving.........: avg=1.23ms   min=0.98ms   med=1.12ms   max=1.67ms   p(90)=1.45ms   p(95)=1.56ms
     http_req_sending...........: avg=0.89ms   min=0.67ms   med=0.87ms   max=1.23ms   p(90)=1.12ms   p(95)=1.18ms
     http_req_tls_handshaking...: avg=0s       min=0s       med=0s       max=0s       p(90)=0s       p(95)=0s
     http_req_waiting...........: avg=154.66ms min=121.8ms  med=148.24ms max=186.44ms p(90)=176.33ms p(95)=181.38ms
     http_reqs..................: 10      1/s
     iteration_duration.........: avg=1.15s    min=1.12s    med=1.15s    max=1.19s    p(90)=1.18s    p(95)=1.18s
     iterations.................: 10      1/s
     vus........................: 1       min=1     max=1
     vus_max....................: 1       min=1     max=1
"""


# Load Testing Tests
class TestLoadTestConfig:
    """Test load test configuration."""

    def test_load_test_config_creation(self, sample_k6_script):
        """Test LoadTestConfig creation."""
        config = LoadTestConfig(
            name="test_load_test",
            script_path=sample_k6_script,
            duration=300,
            virtual_users=10,
            rps_target=50,
        )

        assert config.name == "test_load_test"
        assert config.script_path == sample_k6_script
        assert config.duration == 300
        assert config.virtual_users == 10
        assert config.rps_target == 50

    def test_load_test_config_to_k6_options(self, sample_k6_script):
        """Test converting config to k6 options."""
        config = LoadTestConfig(
            name="test", script_path=sample_k6_script, duration=60, virtual_users=5, rps_target=10
        )

        options = config.to_k6_options()

        assert options["duration"] == "60s"
        assert "scenarios" in options
        assert options["scenarios"]["constant_request_rate"]["rate"] == 10

    def test_load_test_config_without_rps(self, sample_k6_script):
        """Test config without RPS target."""
        config = LoadTestConfig(
            name="test", script_path=sample_k6_script, duration=60, virtual_users=5
        )

        options = config.to_k6_options()

        assert options["vus"] == 5
        assert "scenarios" not in options or not options["scenarios"]


class TestLoadTestResult:
    """Test load test result functionality."""

    def test_load_test_result_creation(self):
        """Test LoadTestResult creation."""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=5)

        result = LoadTestResult(
            test_name="test_load",
            success=True,
            start_time=start_time,
            end_time=end_time,
            duration=300.0,
            http_reqs=1000,
            http_req_duration_p95=150.0,
            http_req_failed_rate=0.01,
        )

        assert result.test_name == "test_load"
        assert result.success is True
        assert result.duration == 300.0

    def test_load_test_result_passed_thresholds(self):
        """Test threshold checking."""
        # Passing thresholds
        result = LoadTestResult(
            test_name="test",
            success=True,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=300.0,
            http_req_duration_p95=150.0,  # < 200ms
            http_req_failed_rate=0.005,  # < 1%
            error_rate=0.02,  # < 5%
        )

        assert result.passed_thresholds is True

        # Failing thresholds
        result.http_req_duration_p95 = 250.0  # > 200ms
        assert result.passed_thresholds is False


class TestK6Runner:
    """Test k6 runner functionality."""

    def test_k6_runner_creation(self):
        """Test K6Runner creation."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            runner = K6Runner()
            assert runner.k6_binary == "k6"

    def test_k6_runner_verification_failure(self):
        """Test k6 verification failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=1, stderr="command not found"
            )

            with pytest.raises(RuntimeError, match="k6 not found"):
                K6Runner()

    @pytest.mark.asyncio
    async def test_k6_runner_run_test(self, sample_k6_script, mock_k6_output):
        """Test running k6 test."""
        with patch("subprocess.run") as mock_run:
            # Mock k6 version check
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            runner = K6Runner()

            config = LoadTestConfig(
                name="test_run", script_path=sample_k6_script, duration=10, virtual_users=1
            )

            with patch.object(runner, "_execute_k6_test") as mock_execute:
                mock_execute.return_value = subprocess.CompletedProcess(
                    args=["k6", "run"], returncode=0, stdout=mock_k6_output
                )

                result = await runner.run_test(config)

                assert isinstance(result, LoadTestResult)
                assert result.test_name == "test_run"
                assert result.success is True

    def test_k6_runner_parse_output(self, mock_k6_output):
        """Test parsing k6 output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            runner = K6Runner()

            completed_process = subprocess.CompletedProcess(
                args=["k6", "run"], returncode=0, stdout=mock_k6_output
            )

            config = LoadTestConfig(
                name="test_parse", script_path=Path("test.js"), duration=10, virtual_users=1
            )

            result = runner._parse_k6_output(completed_process, config, datetime.now())

            assert result.success is True
            assert result.http_reqs == 10
            assert result.http_req_failed_rate == 0.0

    def test_k6_runner_build_command(self, sample_k6_script):
        """Test building k6 command."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            runner = K6Runner()

            config = LoadTestConfig(
                name="test",
                script_path=sample_k6_script,
                duration=60,
                virtual_users=5,
                environment={"BASE_URL": "http://localhost:8000"},
            )

            cmd = runner._build_k6_command(sample_k6_script, config)

            assert cmd[0] == "k6"
            assert "run" in cmd
            assert "--env" in cmd
            assert "BASE_URL=http://localhost:8000" in cmd
            assert str(sample_k6_script) in cmd


class TestLoadTestManager:
    """Test load test manager functionality."""

    def test_load_test_manager_creation(self):
        """Test LoadTestManager creation."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            manager = LoadTestManager()
            assert manager is not None
            assert hasattr(manager, "runner")
            assert hasattr(manager, "suites")

    def test_create_suite(self):
        """Test creating test suite."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            manager = LoadTestManager()

            suite = manager.create_suite("test_suite", "Test description")

            assert suite.name == "test_suite"
            assert suite.description == "Test description"
            assert "test_suite" in manager.suites

    def test_load_suite_from_config(self, temp_directory, sample_k6_script):
        """Test loading suite from configuration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            manager = LoadTestManager()

            # Create config file
            config_data = {
                "name": "test_suite",
                "description": "Test suite from config",
                "tests": [
                    {
                        "name": "test1",
                        "script_path": str(sample_k6_script),
                        "duration": 60,
                        "virtual_users": 5,
                    }
                ],
            }

            config_file = temp_directory / "load_test_config.json"
            config_file.write_text(json.dumps(config_data))

            suite = manager.load_suite_from_config(config_file)

            assert suite.name == "test_suite"
            assert len(suite.tests) == 1
            assert suite.tests[0].name == "test1"

    @pytest.mark.asyncio
    async def test_run_suite(self, sample_k6_script, mock_k6_output):
        """Test running test suite."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            manager = LoadTestManager()

            # Create suite
            suite = manager.create_suite("test_suite", "Test")
            config = LoadTestConfig(
                name="test1", script_path=sample_k6_script, duration=10, virtual_users=1
            )
            suite.add_test(config)

            # Mock k6 execution
            with patch.object(manager.runner, "run_test") as mock_run_test:
                mock_result = LoadTestResult(
                    test_name="test1",
                    success=True,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration=10.0,
                )
                mock_run_test.return_value = mock_result

                completed_suite = await manager.run_suite("test_suite")

                assert len(completed_suite.results) == 1
                assert completed_suite.results[0].success is True


class TestLoadTestSuite:
    """Test load test suite functionality."""

    def test_load_test_suite_creation(self):
        """Test LoadTestSuite creation."""
        suite = LoadTestSuite(name="test_suite", description="Test description")

        assert suite.name == "test_suite"
        assert suite.description == "Test description"
        assert len(suite.tests) == 0
        assert len(suite.results) == 0

    def test_add_test(self, sample_k6_script):
        """Test adding test to suite."""
        suite = LoadTestSuite("test_suite", "Test")

        config = LoadTestConfig(
            name="test1", script_path=sample_k6_script, duration=60, virtual_users=5
        )

        suite.add_test(config)

        assert len(suite.tests) == 1
        assert suite.tests[0].name == "test1"

    def test_overall_success_rate(self):
        """Test calculating overall success rate."""
        suite = LoadTestSuite("test_suite", "Test")

        # Add results
        suite.results = [
            LoadTestResult(
                test_name="test1",
                success=True,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration=60.0,
                http_req_duration_p95=150.0,
                http_req_failed_rate=0.005,
                error_rate=0.02,
            ),
            LoadTestResult(
                test_name="test2",
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration=60.0,
            ),
        ]

        success_rate = suite.get_overall_success_rate()
        assert success_rate == 0.5  # 1 out of 2 passed thresholds


# Chaos Engineering Tests
class TestChaosTarget:
    """Test chaos target functionality."""

    def test_chaos_target_creation(self):
        """Test ChaosTarget creation."""
        target = ChaosTarget(
            name="test_service",
            type="process",
            identifier="1234",
            properties={"restart_policy": "always"},
        )

        assert target.name == "test_service"
        assert target.type == "process"
        assert target.identifier == "1234"
        assert target.properties["restart_policy"] == "always"

    def test_chaos_target_health_check_process(self):
        """Test health check for process target."""
        with patch("psutil.pid_exists") as mock_exists:
            mock_exists.return_value = True

            target = ChaosTarget("test", "process", "1234")
            assert target.is_healthy() is True

            mock_exists.return_value = False
            assert target.is_healthy() is False

    def test_chaos_target_health_check_service(self):
        """Test health check for service target."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["systemctl", "is-active", "test_service"], returncode=0
            )

            target = ChaosTarget("test", "service", "test_service")
            assert target.is_healthy() is True

            mock_run.return_value.returncode = 1
            assert target.is_healthy() is False


class TestChaosExperiment:
    """Test chaos experiment functionality."""

    def test_chaos_experiment_creation(self):
        """Test ChaosExperiment creation."""
        targets = [
            ChaosTarget("api", "process", "1234"),
            ChaosTarget("db", "service", "postgresql"),
        ]

        experiment = ChaosExperiment(
            name="network_chaos",
            description="Test network resilience",
            failure_type=FailureType.NETWORK_LATENCY,
            targets=targets,
            duration=300,
            blast_radius=0.5,
        )

        assert experiment.name == "network_chaos"
        assert experiment.failure_type == FailureType.NETWORK_LATENCY
        assert len(experiment.targets) == 2
        assert experiment.blast_radius == 0.5

    def test_chaos_experiment_validation(self):
        """Test experiment validation."""
        # Valid experiment
        experiment = ChaosExperiment(
            name="test",
            description="Test",
            failure_type=FailureType.CPU_STRESS,
            targets=[ChaosTarget("test", "process", "1234")],
            duration=300,
            blast_radius=0.3,
        )

        assert experiment.validate() is True

        # Invalid - no targets
        experiment.targets = []
        assert experiment.validate() is False

        # Invalid - blast radius out of range
        experiment.targets = [ChaosTarget("test", "process", "1234")]
        experiment.blast_radius = 1.5
        assert experiment.validate() is False

        # Invalid - negative duration
        experiment.blast_radius = 0.3
        experiment.duration = -1
        assert experiment.validate() is False


class TestChaosResult:
    """Test chaos result functionality."""

    def test_chaos_result_creation(self):
        """Test ChaosResult creation."""
        result = ChaosResult(
            experiment_name="test_experiment",
            status=ExperimentStatus.COMPLETED,
            start_time=datetime.now(),
            steady_state_before=True,
            steady_state_after=True,
            recovery_time=60.0,
        )

        assert result.experiment_name == "test_experiment"
        assert result.status == ExperimentStatus.COMPLETED

    def test_chaos_result_success_property(self):
        """Test success property calculation."""
        result = ChaosResult(
            experiment_name="test",
            status=ExperimentStatus.COMPLETED,
            start_time=datetime.now(),
            steady_state_before=True,
            steady_state_after=True,
            recovery_time=60.0,
        )

        assert result.success is True

        # Failure cases
        result.status = ExperimentStatus.FAILED
        assert result.success is False

        result.status = ExperimentStatus.COMPLETED
        result.steady_state_after = False
        assert result.success is False

        result.steady_state_after = True
        result.recovery_time = 400.0  # > 5 minutes
        assert result.success is False


class TestNetworkLatencyInjector:
    """Test network latency injector."""

    def test_network_latency_injector_creation(self):
        """Test NetworkLatencyInjector creation."""
        injector = NetworkLatencyInjector(latency_ms=500, jitter_ms=100)

        assert injector.latency_ms == 500
        assert injector.jitter_ms == 100
        assert len(injector.active_interfaces) == 0

    @pytest.mark.asyncio
    async def test_inject_failure(self):
        """Test injecting network latency."""
        injector = NetworkLatencyInjector()

        targets = [ChaosTarget("network", "network", "eth0")]

        with patch.object(injector, "_run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["tc", "qdisc", "add"], returncode=0, stdout="", stderr=""
            )

            result = await injector.inject_failure(targets)

            assert result is True
            assert "eth0" in injector.active_interfaces

    @pytest.mark.asyncio
    async def test_recover_failure(self):
        """Test recovering from network latency."""
        injector = NetworkLatencyInjector()
        injector.active_interfaces = ["eth0"]

        targets = [ChaosTarget("network", "network", "eth0")]

        with patch.object(injector, "_run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["tc", "qdisc", "del"], returncode=0, stdout="", stderr=""
            )

            result = await injector.recover(targets)

            assert result is True
            assert len(injector.active_interfaces) == 0

    def test_is_failure_active(self):
        """Test checking if failure is active."""
        injector = NetworkLatencyInjector()

        targets = [ChaosTarget("network", "network", "eth0")]

        assert injector.is_failure_active(targets) is False

        injector.active_interfaces = ["eth0"]
        assert injector.is_failure_active(targets) is True


class TestCPUStressInjector:
    """Test CPU stress injector."""

    def test_cpu_stress_injector_creation(self):
        """Test CPUStressInjector creation."""
        injector = CPUStressInjector(cpu_percent=80, workers=4)

        assert injector.cpu_percent == 80
        assert injector.workers == 4
        assert len(injector.stress_processes) == 0

    @pytest.mark.asyncio
    async def test_inject_failure_with_stress_ng(self):
        """Test injecting CPU stress with stress-ng."""
        injector = CPUStressInjector()

        targets = [ChaosTarget("system", "system", "cpu")]

        with patch.object(injector, "_has_stress_ng") as mock_has:
            mock_has.return_value = True

            with patch.object(injector, "_inject_with_stress_ng") as mock_inject:
                result = await injector.inject_failure(targets)

                assert result is True
                mock_inject.assert_called_once()

    @pytest.mark.asyncio
    async def test_inject_failure_with_python(self):
        """Test injecting CPU stress with Python."""
        injector = CPUStressInjector()

        targets = [ChaosTarget("system", "system", "cpu")]

        with patch.object(injector, "_has_stress_ng") as mock_has:
            mock_has.return_value = False

            with patch.object(injector, "_inject_with_python") as mock_inject:
                result = await injector.inject_failure(targets)

                assert result is True
                mock_inject.assert_called_once()

    @pytest.mark.asyncio
    async def test_recover_cpu_stress(self):
        """Test recovering from CPU stress."""
        injector = CPUStressInjector()

        # Mock process
        mock_process = Mock()
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = None
        injector.stress_processes = [mock_process]

        targets = [ChaosTarget("system", "system", "cpu")]

        result = await injector.recover(targets)

        assert result is True
        assert len(injector.stress_processes) == 0
        mock_process.terminate.assert_called_once()


class TestProcessKillInjector:
    """Test process kill injector."""

    def test_process_kill_injector_creation(self):
        """Test ProcessKillInjector creation."""
        injector = ProcessKillInjector()

        assert injector.kill_signal == 15  # SIGTERM
        assert len(injector.killed_processes) == 0

    @pytest.mark.asyncio
    async def test_inject_failure(self):
        """Test killing processes."""
        injector = ProcessKillInjector()

        targets = [ChaosTarget("app", "process", "1234")]

        with patch("psutil.pid_exists") as mock_exists:
            mock_exists.return_value = True

            with patch("psutil.Process") as mock_process_class:
                mock_process = Mock()
                mock_process_class.return_value = mock_process

                result = await injector.inject_failure(targets)

                assert result is True
                assert 1234 in injector.killed_processes
                mock_process.send_signal.assert_called_once()

    @pytest.mark.asyncio
    async def test_recover_process_kill(self):
        """Test recovering from process kill."""
        injector = ProcessKillInjector()

        # Mock healthy target
        target = Mock()
        target.type = "process"
        target.is_healthy.return_value = True
        targets = [target]

        result = await injector.recover(targets)

        assert result is True
        assert len(injector.killed_processes) == 0


class TestMemoryStressInjector:
    """Test memory stress injector."""

    def test_memory_stress_injector_creation(self):
        """Test MemoryStressInjector creation."""
        injector = MemoryStressInjector(memory_mb=1024)

        assert injector.memory_mb == 1024
        assert len(injector.memory_blocks) == 0

    @pytest.mark.asyncio
    async def test_inject_failure(self):
        """Test injecting memory stress."""
        injector = MemoryStressInjector(memory_mb=200)  # Small amount for testing

        targets = [ChaosTarget("system", "system", "memory")]

        result = await injector.inject_failure(targets)

        assert result is True
        assert len(injector.memory_blocks) > 0

    @pytest.mark.asyncio
    async def test_recover_memory_stress(self):
        """Test recovering from memory stress."""
        injector = MemoryStressInjector()
        injector.memory_blocks = [bytearray(1024)]  # Add some memory

        targets = [ChaosTarget("system", "system", "memory")]

        result = await injector.recover(targets)

        assert result is True
        assert len(injector.memory_blocks) == 0

    def test_is_failure_active(self):
        """Test checking if memory stress is active."""
        injector = MemoryStressInjector()

        targets = [ChaosTarget("system", "system", "memory")]

        assert injector.is_failure_active(targets) is False

        injector.memory_blocks = [bytearray(1024)]
        assert injector.is_failure_active(targets) is True


class TestChaosOrchestrator:
    """Test chaos orchestrator functionality."""

    def test_chaos_orchestrator_creation(self):
        """Test ChaosOrchestrator creation."""
        orchestrator = ChaosOrchestrator()

        assert orchestrator is not None
        assert len(orchestrator.experiments) == 0
        assert len(orchestrator.results) == 0
        assert orchestrator.safety_enabled is True

    def test_register_experiment(self):
        """Test registering chaos experiment."""
        orchestrator = ChaosOrchestrator()

        experiment = ChaosExperiment(
            name="test_experiment",
            description="Test",
            failure_type=FailureType.CPU_STRESS,
            targets=[ChaosTarget("test", "process", "1234")],
        )

        orchestrator.register_experiment(experiment)

        assert "test_experiment" in orchestrator.experiments

    def test_register_invalid_experiment(self):
        """Test registering invalid experiment."""
        orchestrator = ChaosOrchestrator()

        # Invalid experiment (no targets)
        experiment = ChaosExperiment(
            name="invalid", description="Invalid", failure_type=FailureType.CPU_STRESS, targets=[]
        )

        with pytest.raises(ValueError):
            orchestrator.register_experiment(experiment)

    @pytest.mark.asyncio
    async def test_run_experiment(self):
        """Test running chaos experiment."""
        orchestrator = ChaosOrchestrator()

        # Mock safety check
        orchestrator.safety_enabled = False

        experiment = ChaosExperiment(
            name="test_experiment",
            description="Test",
            failure_type=FailureType.CPU_STRESS,
            targets=[ChaosTarget("test", "process", "1234")],
            duration=1,  # Short duration for testing
        )

        orchestrator.register_experiment(experiment)

        # Mock injector
        mock_injector = Mock()
        mock_injector.inject_failure.return_value = True
        mock_injector.recover.return_value = True
        mock_injector.is_failure_active.return_value = False

        orchestrator.injectors[FailureType.CPU_STRESS] = mock_injector

        result = await orchestrator.run_experiment("test_experiment")

        assert isinstance(result, ChaosResult)
        assert result.experiment_name == "test_experiment"
        assert result.status == ExperimentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_safety_check(self):
        """Test safety check functionality."""
        orchestrator = ChaosOrchestrator()

        # Healthy targets
        target = Mock()
        target.is_healthy.return_value = True

        experiment = ChaosExperiment(
            name="test",
            description="Test",
            failure_type=FailureType.CPU_STRESS,
            targets=[target],
            blast_radius=0.3,
            max_impact=0.5,
        )

        safety_ok = await orchestrator._safety_check(experiment)
        assert safety_ok is True

        # Unhealthy targets
        target.is_healthy.return_value = False
        safety_ok = await orchestrator._safety_check(experiment)
        assert safety_ok is False

    def test_generate_insights(self):
        """Test generating insights from experiment."""
        orchestrator = ChaosOrchestrator()

        experiment = ChaosExperiment(
            name="test",
            description="Test",
            failure_type=FailureType.NETWORK_LATENCY,
            targets=[ChaosTarget("test", "process", "1234")],
        )

        # Successful result
        result = ChaosResult(
            experiment_name="test",
            status=ExperimentStatus.COMPLETED,
            start_time=datetime.now(),
            steady_state_before=True,
            steady_state_after=True,
            recovery_time=30.0,
        )

        insights = orchestrator._generate_insights(experiment, result)

        assert len(insights) > 0
        assert any("resilience" in insight.lower() for insight in insights)

    def test_generate_recommendations(self):
        """Test generating recommendations from experiment."""
        orchestrator = ChaosOrchestrator()

        experiment = ChaosExperiment(
            name="test",
            description="Test",
            failure_type=FailureType.NETWORK_LATENCY,
            targets=[ChaosTarget("test", "process", "1234")],
        )

        # Failed result
        result = ChaosResult(
            experiment_name="test",
            status=ExperimentStatus.FAILED,
            start_time=datetime.now(),
            steady_state_before=True,
            steady_state_after=False,
        )

        recommendations = orchestrator._generate_recommendations(experiment, result)

        assert len(recommendations) > 0
        assert any("timeout" in rec.lower() or "retry" in rec.lower() for rec in recommendations)


class TestCreateTDeveloperExperiments:
    """Test predefined T-Developer experiments."""

    def test_create_experiments(self):
        """Test creating predefined experiments."""
        experiments = create_t_developer_experiments()

        assert len(experiments) > 0
        assert all(isinstance(exp, ChaosExperiment) for exp in experiments)

        # Check for specific experiment types
        experiment_names = [exp.name for exp in experiments]
        assert "api_latency_test" in experiment_names
        assert "agent_process_kill" in experiment_names
        assert "memory_stress_test" in experiment_names


# Monitoring Tests
class TestMetric:
    """Test metric functionality."""

    def test_metric_creation(self):
        """Test Metric creation."""
        metric = Metric(
            name="cpu_usage",
            value=75.5,
            metric_type=MetricType.GAUGE,
            labels={"host": "server1", "region": "us-east"},
            help_text="CPU usage percentage",
        )

        assert metric.name == "cpu_usage"
        assert metric.value == 75.5
        assert metric.metric_type == MetricType.GAUGE
        assert metric.labels["host"] == "server1"

    def test_metric_to_prometheus_format(self):
        """Test converting metric to Prometheus format."""
        metric = Metric(
            name="http_requests_total",
            value=1000,
            metric_type=MetricType.COUNTER,
            labels={"method": "GET", "endpoint": "/api/v1"},
        )

        prometheus_format = metric.to_prometheus_format()

        assert "http_requests_total{" in prometheus_format
        assert 'method="GET"' in prometheus_format
        assert 'endpoint="/api/v1"' in prometheus_format
        assert "1000" in prometheus_format


class TestAlert:
    """Test alert functionality."""

    def test_alert_creation(self):
        """Test Alert creation."""
        alert = Alert(
            name="high_cpu",
            description="CPU usage is high",
            severity=AlertSeverity.WARNING,
            condition="cpu_usage > 80",
            threshold=80,
            duration=300,
        )

        assert alert.name == "high_cpu"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.threshold == 80
        assert alert.status == AlertStatus.ACTIVE

    def test_alert_is_firing(self):
        """Test alert firing status."""
        alert = Alert(
            name="test",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition="metric > 50",
            threshold=50,
        )

        assert alert.is_firing() is False

        alert.triggered_at = datetime.now()
        assert alert.is_firing() is True

        alert.status = AlertStatus.RESOLVED
        assert alert.is_firing() is False

    def test_alert_should_notify(self):
        """Test alert notification timing."""
        alert = Alert(
            name="test",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition="metric > 50",
            threshold=50,
        )

        # Not firing
        assert alert.should_notify() is False

        # Firing but never notified
        alert.status = AlertStatus.ACTIVE
        alert.triggered_at = datetime.now()
        assert alert.should_notify() is True

        # Recently notified
        alert.last_notification = datetime.now()
        assert alert.should_notify() is False

        # Notification cooldown expired
        alert.last_notification = datetime.now() - timedelta(minutes=10)
        assert alert.should_notify(cooldown_seconds=300) is True


class TestMetricCollector:
    """Test metric collector functionality."""

    def test_metric_collector_creation(self):
        """Test MetricCollector creation."""
        collector = MetricCollector(collection_interval=10)

        assert collector.collection_interval == 10
        assert len(collector.metrics) == 0
        assert len(collector.custom_collectors) == 0
        assert collector._running is False

    def test_add_custom_collector(self):
        """Test adding custom metric collector."""
        collector = MetricCollector()

        def custom_collector():
            return [Metric("custom_metric", 42, MetricType.GAUGE)]

        collector.add_custom_collector(custom_collector)

        assert len(collector.custom_collectors) == 1

    @pytest.mark.asyncio
    async def test_start_stop_collection(self):
        """Test starting and stopping metric collection."""
        collector = MetricCollector(collection_interval=0.1)  # Fast for testing

        await collector.start_collection()
        assert collector._running is True
        assert collector._task is not None

        # Let it collect a few metrics
        await asyncio.sleep(0.2)

        await collector.stop_collection()
        assert collector._running is False

    def test_collect_system_metrics(self):
        """Test collecting system metrics."""
        collector = MetricCollector()

        metrics = collector._collect_system_metrics()

        assert len(metrics) > 0
        metric_names = [m.name for m in metrics]
        assert "system_cpu_usage_percent" in metric_names
        assert "system_memory_usage_percent" in metric_names

    def test_collect_application_metrics(self):
        """Test collecting application metrics."""
        collector = MetricCollector()

        metrics = collector._collect_application_metrics()

        assert len(metrics) > 0
        metric_names = [m.name for m in metrics]
        assert "api_requests_total" in metric_names

    def test_get_metric_history(self):
        """Test getting metric history."""
        collector = MetricCollector()

        # Add some test metrics
        now = datetime.now()
        for i in range(10):
            metric = Metric(
                name="test_metric",
                value=i,
                metric_type=MetricType.GAUGE,
                timestamp=now - timedelta(minutes=i),
            )
            collector.metrics["test_metric"].append(metric)

        # Get recent history
        history = collector.get_metric_history("test_metric", duration_minutes=5)

        assert len(history) <= 6  # Last 5 minutes plus current

    def test_get_metric_statistics(self):
        """Test getting metric statistics."""
        collector = MetricCollector()

        # Add test metrics
        values = [10, 20, 30, 40, 50]
        now = datetime.now()
        for i, value in enumerate(values):
            metric = Metric(
                name="test_metric",
                value=value,
                metric_type=MetricType.GAUGE,
                timestamp=now - timedelta(minutes=i),
            )
            collector.metrics["test_metric"].append(metric)

        stats = collector.get_metric_statistics("test_metric", duration_minutes=60)

        assert stats["count"] == 5
        assert stats["min"] == 10
        assert stats["max"] == 50
        assert stats["mean"] == 30


class TestAlertManager:
    """Test alert manager functionality."""

    def test_alert_manager_creation(self):
        """Test AlertManager creation."""
        manager = AlertManager()

        assert manager is not None
        assert len(manager.alerts) == 0
        assert len(manager.notification_channels) == 0
        assert manager._running is False

    def test_register_alert(self):
        """Test registering alert."""
        manager = AlertManager()

        alert = Alert(
            name="test_alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition="metric > 50",
            threshold=50,
        )

        manager.register_alert(alert)

        assert "test_alert" in manager.alerts

    def test_add_notification_channel(self):
        """Test adding notification channel."""
        manager = AlertManager()

        channel = Mock(spec=NotificationChannel)
        manager.add_notification_channel(channel)

        assert len(manager.notification_channels) == 1

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self):
        """Test starting and stopping alert monitoring."""
        manager = AlertManager({"evaluation_interval": 0.1})
        collector = Mock()

        await manager.start_monitoring(collector)
        assert manager._running is True

        await asyncio.sleep(0.2)  # Let it run briefly

        await manager.stop_monitoring()
        assert manager._running is False

    def test_get_metric_value_for_condition(self):
        """Test extracting metric value from condition."""
        manager = AlertManager()

        # Mock metric collector
        collector = Mock()
        mock_metric = Mock()
        mock_metric.value = 75.0
        collector.metrics = {"cpu_usage": [mock_metric]}

        value = manager._get_metric_value_for_condition("cpu_usage > 80", collector)

        assert value == 75.0

    def test_check_threshold(self):
        """Test threshold checking."""
        manager = AlertManager()

        assert manager._check_threshold(85, 80, "cpu_usage > 80") is True
        assert manager._check_threshold(75, 80, "cpu_usage > 80") is False
        assert manager._check_threshold(75, 80, "cpu_usage < 80") is True
        assert manager._check_threshold(85, 80, "cpu_usage < 80") is False

    @pytest.mark.asyncio
    async def test_evaluate_single_alert(self):
        """Test evaluating single alert."""
        manager = AlertManager()

        alert = Alert(
            name="test_alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            condition="cpu_usage > 80",
            threshold=80,
            duration=0,  # No duration for immediate alerting
        )

        # Mock metric collector
        collector = Mock()
        mock_metric = Mock()
        mock_metric.value = 85.0  # Above threshold
        collector.metrics = {"cpu_usage": [mock_metric]}

        # Mock notification
        mock_channel = AsyncMock()
        manager.notification_channels = [mock_channel]

        await manager._evaluate_single_alert(alert, collector)

        assert alert.status == AlertStatus.ACTIVE
        assert alert.triggered_at is not None


class TestNotificationChannels:
    """Test notification channels."""

    def test_slack_notification_channel_creation(self):
        """Test SlackNotificationChannel creation."""
        channel = SlackNotificationChannel(
            webhook_url="https://hooks.slack.com/webhook", channel="#alerts"
        )

        assert channel.webhook_url == "https://hooks.slack.com/webhook"
        assert channel.channel == "#alerts"

    @pytest.mark.asyncio
    async def test_slack_send_notification(self):
        """Test sending Slack notification."""
        channel = SlackNotificationChannel(webhook_url="https://hooks.slack.com/webhook")

        alert = Alert(
            name="test_alert",
            description="Test alert",
            severity=AlertSeverity.WARNING,
            condition="metric > 50",
            threshold=50,
        )

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response

            await channel.send_notification(alert, "FIRING")

            mock_post.assert_called_once()

    def test_email_notification_channel_creation(self):
        """Test EmailNotificationChannel creation."""
        channel = EmailNotificationChannel(
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="user@example.com",
            password="password",
            recipients=["alert@example.com"],
        )

        assert channel.smtp_server == "smtp.example.com"
        assert channel.smtp_port == 587
        assert len(channel.recipients) == 1

    @pytest.mark.asyncio
    async def test_email_send_notification(self):
        """Test sending email notification."""
        channel = EmailNotificationChannel(
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="user@example.com",
            password="password",
            recipients=["alert@example.com"],
        )

        alert = Alert(
            name="test_alert",
            description="Test alert",
            severity=AlertSeverity.CRITICAL,
            condition="metric > 90",
            threshold=90,
        )

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value = mock_server

            await channel.send_notification(alert, "FIRING")

            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()


class TestMonitoringDashboard:
    """Test monitoring dashboard functionality."""

    def test_dashboard_creation(self):
        """Test MonitoringDashboard creation."""
        collector = Mock()
        manager = Mock()

        dashboard = MonitoringDashboard(collector, manager)

        assert dashboard.metric_collector == collector
        assert dashboard.alert_manager == manager

    def test_generate_dashboard_data(self):
        """Test generating dashboard data."""
        collector = Mock()
        manager = Mock()

        # Mock metric collector
        collector.metrics = {
            "system_cpu_usage_percent": [Mock(value=75.0)],
            "system_memory_usage_percent": [Mock(value=60.0)],
        }
        collector.get_metric_statistics.return_value = {"count": 10, "mean": 50.0, "p95": 80.0}

        # Mock alert manager
        mock_alert = Mock()
        mock_alert.is_firing.return_value = True
        mock_alert.name = "test_alert"
        mock_alert.severity = AlertSeverity.WARNING
        mock_alert.description = "Test alert"
        mock_alert.triggered_at = datetime.now()

        manager.alerts = {"test_alert": mock_alert}

        dashboard = MonitoringDashboard(collector, manager)

        data = dashboard.generate_dashboard_data()

        assert "timestamp" in data
        assert "system_overview" in data
        assert "active_alerts" in data
        assert "metric_summary" in data
        assert "performance_indicators" in data

    def test_calculate_health_score(self):
        """Test calculating health score."""
        collector = Mock()
        manager = Mock()

        # Mock alerts
        warning_alert = Mock()
        warning_alert.is_firing.return_value = True
        warning_alert.severity = AlertSeverity.WARNING

        critical_alert = Mock()
        critical_alert.is_firing.return_value = True
        critical_alert.severity = AlertSeverity.CRITICAL

        manager.alerts = {"warning": warning_alert, "critical": critical_alert}

        dashboard = MonitoringDashboard(collector, manager)

        score = dashboard._calculate_health_score()

        # Should be reduced by 10 (warning) + 20 (critical) = 30
        assert score == 70.0


class TestCreateTDeveloperAlerts:
    """Test predefined T-Developer alerts."""

    def test_create_alerts(self):
        """Test creating predefined alerts."""
        alerts = create_t_developer_alerts()

        assert len(alerts) > 0
        assert all(isinstance(alert, Alert) for alert in alerts)

        # Check for specific alert types
        alert_names = [alert.name for alert in alerts]
        assert "high_cpu_usage" in alert_names
        assert "high_memory_usage" in alert_names
        assert "high_disk_usage" in alert_names
        assert "high_api_latency" in alert_names

        # Check alert properties
        cpu_alert = next(a for a in alerts if a.name == "high_cpu_usage")
        assert cpu_alert.threshold == 80
        assert cpu_alert.severity == AlertSeverity.WARNING


# Integration Tests
class TestReliabilityIntegration:
    """Integration tests for reliability components."""

    @pytest.mark.asyncio
    async def test_run_load_tests_integration(self, temp_directory, sample_k6_script):
        """Test end-to-end load testing."""
        # Create test configuration
        config_data = {
            "name": "integration_test",
            "description": "Integration test suite",
            "tests": [
                {
                    "name": "basic_test",
                    "script_path": str(sample_k6_script),
                    "duration": 5,
                    "virtual_users": 1,
                }
            ],
        }

        config_file = temp_directory / "load_test_config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["k6", "version"], returncode=0, stdout="k6 v0.40.0"
            )

            with patch("asyncio.create_subprocess_exec") as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"test output", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                result = await run_load_tests(config_file, temp_directory)

                assert isinstance(result, dict)
                assert "suite_name" in result
                assert "tests_run" in result

    @pytest.mark.asyncio
    async def test_run_chaos_experiments_integration(self, temp_directory):
        """Test end-to-end chaos engineering."""
        # Mock experiment execution
        with patch(
            "packages.performance.chaos_engineering.ChaosOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            # Mock experiment results
            mock_results = {
                "test_experiment": ChaosResult(
                    experiment_name="test_experiment",
                    status=ExperimentStatus.COMPLETED,
                    start_time=datetime.now(),
                    steady_state_before=True,
                    steady_state_after=True,
                    recovery_time=30.0,
                )
            }

            mock_orchestrator.run_experiment_suite.return_value = mock_results

            result = await run_chaos_experiments(temp_directory)

            assert isinstance(result, dict)
            assert "total_experiments" in result
            assert "success_rate" in result

    @pytest.mark.asyncio
    async def test_start_monitoring_system_integration(self):
        """Test end-to-end monitoring system."""
        config = {"collection_interval": 1, "alerting": {"evaluation_interval": 1}}

        components = await start_monitoring_system(config)

        assert isinstance(components, dict)
        assert "metric_collector" in components
        assert "alert_manager" in components
        assert "dashboard" in components
        assert components["status"] == "running"

        # Cleanup
        await components["metric_collector"].stop_collection()
        await components["alert_manager"].stop_monitoring()


# Error Handling Tests
class TestReliabilityErrorHandling:
    """Test error handling in reliability components."""

    @pytest.mark.asyncio
    async def test_load_test_k6_not_found(self):
        """Test handling when k6 is not available."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("k6 not found")

            with pytest.raises(RuntimeError, match="k6 not available"):
                K6Runner()

    @pytest.mark.asyncio
    async def test_chaos_experiment_safety_failure(self):
        """Test handling safety check failures."""
        orchestrator = ChaosOrchestrator()

        # Create experiment that will fail safety check
        experiment = ChaosExperiment(
            name="unsafe_test",
            description="Test",
            failure_type=FailureType.CPU_STRESS,
            targets=[],  # No targets - will fail validation
            blast_radius=2.0,  # Invalid blast radius
        )

        with pytest.raises(ValueError):
            orchestrator.register_experiment(experiment)

    @pytest.mark.asyncio
    async def test_monitoring_metric_collection_error(self):
        """Test handling metric collection errors."""
        collector = MetricCollector(collection_interval=0.1)

        # Mock system metric collection to fail
        with patch.object(collector, "_collect_system_metrics") as mock_collect:
            mock_collect.side_effect = Exception("Collection failed")

            await collector.start_collection()
            await asyncio.sleep(0.2)  # Let it try to collect
            await collector.stop_collection()

            # Should not crash, just log errors


# Performance Tests for Reliability Components
class TestReliabilityPerformance:
    """Test performance of reliability components."""

    @pytest.mark.asyncio
    async def test_metric_collection_performance(self):
        """Test metric collection performance."""
        collector = MetricCollector(collection_interval=0.01)  # Very fast

        start_time = time.time()

        await collector.start_collection()
        await asyncio.sleep(0.1)  # Collect for 100ms
        await collector.stop_collection()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        assert duration < 1.0

        # Should have collected some metrics
        assert len(collector.metrics) > 0

    @pytest.mark.asyncio
    async def test_alert_evaluation_performance(self):
        """Test alert evaluation performance."""
        manager = AlertManager({"evaluation_interval": 0.01})

        # Register many alerts
        for i in range(100):
            alert = Alert(
                name=f"alert_{i}",
                description=f"Test alert {i}",
                severity=AlertSeverity.WARNING,
                condition=f"metric_{i} > {i * 10}",
                threshold=i * 10,
            )
            manager.register_alert(alert)

        # Mock collector with metrics
        collector = Mock()
        collector.metrics = {}
        for i in range(100):
            mock_metric = Mock()
            mock_metric.value = i * 5  # Below threshold
            collector.metrics[f"metric_{i}"] = [mock_metric]

        start_time = time.time()

        await manager._evaluate_alerts(collector)

        end_time = time.time()
        duration = end_time - start_time

        # Should evaluate all alerts quickly
        assert duration < 0.1  # 100ms

    def test_chaos_experiment_creation_performance(self):
        """Test chaos experiment creation performance."""
        start_time = time.time()

        # Create many experiments
        experiments = []
        for i in range(1000):
            experiment = ChaosExperiment(
                name=f"experiment_{i}",
                description=f"Test experiment {i}",
                failure_type=FailureType.CPU_STRESS,
                targets=[ChaosTarget(f"target_{i}", "process", str(1000 + i))],
            )
            experiments.append(experiment)

        end_time = time.time()
        duration = end_time - start_time

        # Should create experiments quickly
        assert duration < 0.1  # 100ms
        assert len(experiments) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=packages.performance", "--cov-report=html"])
