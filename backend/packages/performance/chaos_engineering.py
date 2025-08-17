"""Chaos Engineering - Failure injection and resilience testing.

Phase 6: P6-T2 - Reliability Engineering
Implement chaos engineering practices for T-Developer system.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

import psutil

# Constants
DEFAULT_EXPERIMENT_DURATION: int = 300  # 5 minutes
DEFAULT_BLAST_RADIUS: float = 0.1  # 10% of components
MIN_RECOVERY_TIME: int = 30  # 30 seconds

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures that can be injected."""

    NETWORK_PARTITION = "network_partition"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FILL = "disk_fill"
    DISK_IO_STRESS = "disk_io_stress"
    PROCESS_KILL = "process_kill"
    SERVICE_SHUTDOWN = "service_shutdown"
    DATABASE_CORRUPTION = "database_corruption"
    DEPENDENCY_FAILURE = "dependency_failure"
    CONFIGURATION_CHAOS = "configuration_chaos"


class ExperimentStatus(Enum):
    """Chaos experiment status."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RECOVERING = "recovering"


@dataclass
class ChaosTarget:
    """Target for chaos engineering experiment."""

    name: str
    type: str  # service, process, network, disk, etc.
    identifier: str  # PID, service name, IP, etc.
    properties: dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Check if target is healthy."""
        if self.type == "process":
            try:
                pid = int(self.identifier)
                return psutil.pid_exists(pid)
            except (ValueError, psutil.NoSuchProcess):
                return False
        elif self.type == "service":
            # Check service status (simplified)
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", self.identifier],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False
        return True


@dataclass
class ChaosExperiment:
    """Chaos engineering experiment definition."""

    name: str
    description: str
    failure_type: FailureType
    targets: list[ChaosTarget]
    duration: int = DEFAULT_EXPERIMENT_DURATION
    blast_radius: float = DEFAULT_BLAST_RADIUS

    # Experiment controls
    steady_state_hypothesis: Optional[Callable[[], bool]] = None
    method: dict[str, Any] = field(default_factory=dict)
    rollbacks: list[Callable[[], None]] = field(default_factory=list)

    # Safety mechanisms
    circuit_breaker: bool = True
    max_impact: float = 0.5  # Maximum 50% impact
    safety_checks: list[Callable[[], bool]] = field(default_factory=list)

    # Metadata
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        """Validate experiment configuration."""
        if not self.targets:
            return False
        if self.blast_radius < 0 or self.blast_radius > 1:
            return False
        if self.duration <= 0:
            return False
        return True


@dataclass
class ChaosResult:
    """Result of chaos engineering experiment."""

    experiment_name: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None

    # Results
    steady_state_before: bool = False
    steady_state_after: bool = False
    impact_measured: dict[str, Any] = field(default_factory=dict)
    recovery_time: Optional[float] = None

    # Observations
    observations: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    # Learning
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Determine if experiment was successful."""
        return (
            self.status == ExperimentStatus.COMPLETED
            and self.steady_state_before
            and self.steady_state_after
            and self.recovery_time is not None
            and self.recovery_time <= 300  # 5 minutes max recovery
        )


class FailureInjector(ABC):
    """Abstract base class for failure injection."""

    @abstractmethod
    async def inject_failure(self, targets: list[ChaosTarget], **kwargs) -> bool:
        """Inject failure into targets."""
        pass

    @abstractmethod
    async def recover(self, targets: list[ChaosTarget]) -> bool:
        """Recover from injected failure."""
        pass

    @abstractmethod
    def is_failure_active(self, targets: list[ChaosTarget]) -> bool:
        """Check if failure is currently active."""
        pass


class NetworkLatencyInjector(FailureInjector):
    """Inject network latency using traffic control."""

    def __init__(self, latency_ms: int = 500, jitter_ms: int = 100):
        """Initialize network latency injector.

        Args:
            latency_ms: Base latency in milliseconds
            jitter_ms: Jitter in milliseconds
        """
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.active_interfaces: list[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    async def inject_failure(self, targets: list[ChaosTarget], **kwargs) -> bool:
        """Inject network latency."""
        try:
            for target in targets:
                if target.type == "network":
                    interface = target.identifier

                    # Add traffic control rules
                    cmd = [
                        "tc",
                        "qdisc",
                        "add",
                        "dev",
                        interface,
                        "root",
                        "netem",
                        "delay",
                        f"{self.latency_ms}ms",
                        f"{self.jitter_ms}ms",
                    ]

                    result = await self._run_command(cmd)
                    if result.returncode == 0:
                        self.active_interfaces.append(interface)
                        self.logger.info(f"Injected {self.latency_ms}ms latency on {interface}")
                    else:
                        self.logger.error(
                            f"Failed to inject latency on {interface}: {result.stderr}"
                        )
                        return False

            return True

        except Exception as e:
            self.logger.error(f"Network latency injection failed: {e}")
            return False

    async def recover(self, targets: list[ChaosTarget]) -> bool:
        """Remove network latency."""
        try:
            for interface in self.active_interfaces:
                cmd = ["tc", "qdisc", "del", "dev", interface, "root"]
                result = await self._run_command(cmd)

                if result.returncode == 0:
                    self.logger.info(f"Removed latency from {interface}")
                else:
                    self.logger.warning(f"Failed to remove latency from {interface}")

            self.active_interfaces.clear()
            return True

        except Exception as e:
            self.logger.error(f"Network latency recovery failed: {e}")
            return False

    def is_failure_active(self, targets: list[ChaosTarget]) -> bool:
        """Check if network latency is active."""
        return bool(self.active_interfaces)

    async def _run_command(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """Run system command."""
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        return subprocess.CompletedProcess(
            args=cmd, returncode=process.returncode, stdout=stdout.decode(), stderr=stderr.decode()
        )


class CPUStressInjector(FailureInjector):
    """Inject CPU stress using stress-ng or similar tools."""

    def __init__(self, cpu_percent: int = 80, workers: Optional[int] = None):
        """Initialize CPU stress injector.

        Args:
            cpu_percent: Target CPU utilization percentage
            workers: Number of worker processes (default: CPU count)
        """
        self.cpu_percent = cpu_percent
        self.workers = workers or psutil.cpu_count()
        self.stress_processes: list[subprocess.Popen] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    async def inject_failure(self, targets: list[ChaosTarget], **kwargs) -> bool:
        """Inject CPU stress."""
        try:
            # Use stress-ng if available, otherwise use Python-based stress
            if await self._has_stress_ng():
                await self._inject_with_stress_ng()
            else:
                await self._inject_with_python()

            self.logger.info(
                f"Injected CPU stress: {self.cpu_percent}% with {self.workers} workers"
            )
            return True

        except Exception as e:
            self.logger.error(f"CPU stress injection failed: {e}")
            return False

    async def recover(self, targets: list[ChaosTarget]) -> bool:
        """Stop CPU stress."""
        try:
            for process in self.stress_processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

            self.stress_processes.clear()
            self.logger.info("Stopped CPU stress")
            return True

        except Exception as e:
            self.logger.error(f"CPU stress recovery failed: {e}")
            return False

    def is_failure_active(self, targets: list[ChaosTarget]) -> bool:
        """Check if CPU stress is active."""
        active_processes = []
        for process in self.stress_processes:
            if process.poll() is None:  # Process is still running
                active_processes.append(process)

        self.stress_processes = active_processes
        return bool(active_processes)

    async def _has_stress_ng(self) -> bool:
        """Check if stress-ng is available."""
        try:
            result = await asyncio.create_subprocess_exec(
                "stress-ng",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _inject_with_stress_ng(self) -> None:
        """Inject CPU stress using stress-ng."""
        duration = "0"  # Run indefinitely until killed

        process = await asyncio.create_subprocess_exec(
            "stress-ng",
            "--cpu",
            str(self.workers),
            "--cpu-load",
            str(self.cpu_percent),
            "--timeout",
            duration,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self.stress_processes.append(process)

    async def _inject_with_python(self) -> None:
        """Inject CPU stress using Python."""

        def cpu_stress_worker():
            """CPU stress worker function."""
            while True:
                # Busy work to consume CPU
                for _ in range(1000000):
                    pass
                # Small sleep to allow process control
                time.sleep(0.001)

        # Start worker threads
        for _ in range(self.workers):
            thread = threading.Thread(target=cpu_stress_worker, daemon=True)
            thread.start()


class ProcessKillInjector(FailureInjector):
    """Kill processes to simulate failures."""

    def __init__(self, kill_signal: int = signal.SIGTERM):
        """Initialize process kill injector.

        Args:
            kill_signal: Signal to send to processes
        """
        self.kill_signal = kill_signal
        self.killed_processes: list[int] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    async def inject_failure(self, targets: list[ChaosTarget], **kwargs) -> bool:
        """Kill target processes."""
        try:
            for target in targets:
                if target.type == "process":
                    pid = int(target.identifier)

                    if psutil.pid_exists(pid):
                        try:
                            process = psutil.Process(pid)
                            process.send_signal(self.kill_signal)
                            self.killed_processes.append(pid)
                            self.logger.info(f"Killed process {pid} ({target.name})")
                        except psutil.NoSuchProcess:
                            self.logger.warning(f"Process {pid} no longer exists")
                        except psutil.AccessDenied:
                            self.logger.error(f"Access denied killing process {pid}")
                            return False
                    else:
                        self.logger.warning(f"Process {pid} does not exist")

            return True

        except Exception as e:
            self.logger.error(f"Process kill injection failed: {e}")
            return False

    async def recover(self, targets: list[ChaosTarget]) -> bool:
        """Recovery is external - processes should be restarted by supervisors."""
        # Wait for processes to be restarted
        recovery_timeout = 60  # 1 minute
        start_time = time.time()

        for target in targets:
            if target.type == "process":
                while time.time() - start_time < recovery_timeout:
                    if target.is_healthy():
                        break
                    await asyncio.sleep(1)
                else:
                    self.logger.error(f"Process {target.name} did not recover")
                    return False

        self.killed_processes.clear()
        return True

    def is_failure_active(self, targets: list[ChaosTarget]) -> bool:
        """Check if any killed processes are still down."""
        for target in targets:
            if target.type == "process" and not target.is_healthy():
                return True
        return False


class MemoryStressInjector(FailureInjector):
    """Inject memory stress by consuming available memory."""

    def __init__(self, memory_mb: int = 1024):
        """Initialize memory stress injector.

        Args:
            memory_mb: Amount of memory to consume in MB
        """
        self.memory_mb = memory_mb
        self.memory_blocks: list[bytearray] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    async def inject_failure(self, targets: list[ChaosTarget], **kwargs) -> bool:
        """Inject memory stress."""
        try:
            # Allocate memory in chunks to avoid sudden allocation failures
            chunk_size = 100 * 1024 * 1024  # 100MB chunks
            chunks_needed = self.memory_mb // 100

            for _ in range(chunks_needed):
                chunk = bytearray(chunk_size)
                # Write to the memory to ensure it's actually allocated
                for i in range(0, chunk_size, 4096):
                    chunk[i] = 0x42
                self.memory_blocks.append(chunk)
                await asyncio.sleep(0.1)  # Small delay between allocations

            self.logger.info(f"Allocated {self.memory_mb}MB of memory")
            return True

        except MemoryError:
            self.logger.error("Failed to allocate memory - system limit reached")
            return False
        except Exception as e:
            self.logger.error(f"Memory stress injection failed: {e}")
            return False

    async def recover(self, targets: list[ChaosTarget]) -> bool:
        """Release allocated memory."""
        try:
            self.memory_blocks.clear()
            # Force garbage collection
            import gc

            gc.collect()

            self.logger.info("Released allocated memory")
            return True

        except Exception as e:
            self.logger.error(f"Memory stress recovery failed: {e}")
            return False

    def is_failure_active(self, targets: list[ChaosTarget]) -> bool:
        """Check if memory stress is active."""
        return bool(self.memory_blocks)


class ChaosOrchestrator:
    """Orchestrate chaos engineering experiments."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize chaos orchestrator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.experiments: dict[str, ChaosExperiment] = {}
        self.results: dict[str, ChaosResult] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Safety settings
        self.safety_enabled = self.config.get("safety_enabled", True)
        self.max_concurrent_experiments = self.config.get("max_concurrent", 1)
        self.running_experiments: dict[str, asyncio.Task] = {}

        # Initialize failure injectors
        self.injectors: dict[FailureType, FailureInjector] = {
            FailureType.NETWORK_LATENCY: NetworkLatencyInjector(),
            FailureType.CPU_STRESS: CPUStressInjector(),
            FailureType.PROCESS_KILL: ProcessKillInjector(),
            FailureType.MEMORY_STRESS: MemoryStressInjector(),
        }

    def register_experiment(self, experiment: ChaosExperiment) -> None:
        """Register a chaos experiment.

        Args:
            experiment: Chaos experiment to register
        """
        if not experiment.validate():
            raise ValueError(f"Invalid experiment: {experiment.name}")

        self.experiments[experiment.name] = experiment
        self.logger.info(f"Registered experiment: {experiment.name}")

    async def run_experiment(self, experiment_name: str) -> ChaosResult:
        """Run a single chaos experiment.

        Args:
            experiment_name: Name of experiment to run

        Returns:
            Experiment result
        """
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment '{experiment_name}' not found")

        experiment = self.experiments[experiment_name]

        # Check safety constraints
        if self.safety_enabled and not await self._safety_check(experiment):
            raise RuntimeError(f"Safety check failed for experiment: {experiment_name}")

        # Check concurrent experiment limit
        if len(self.running_experiments) >= self.max_concurrent_experiments:
            raise RuntimeError("Maximum concurrent experiments limit reached")

        self.logger.info(f"Starting chaos experiment: {experiment_name}")

        # Initialize result
        result = ChaosResult(
            experiment_name=experiment_name,
            status=ExperimentStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            # Check steady state before experiment
            if experiment.steady_state_hypothesis:
                result.steady_state_before = experiment.steady_state_hypothesis()
                if not result.steady_state_before:
                    self.logger.warning("Steady state check failed before experiment")

            # Get failure injector
            injector = self.injectors.get(experiment.failure_type)
            if not injector:
                raise ValueError(f"No injector for failure type: {experiment.failure_type}")

            # Inject failure
            failure_injected = await injector.inject_failure(
                experiment.targets, **experiment.method
            )

            if not failure_injected:
                raise RuntimeError("Failed to inject failure")

            result.observations.append(f"Failure injected: {experiment.failure_type}")

            # Monitor during experiment
            await self._monitor_experiment(experiment, result, injector)

            # Recover from failure
            recovery_start = time.time()
            recovered = await injector.recover(experiment.targets)
            recovery_time = time.time() - recovery_start

            if recovered:
                result.recovery_time = recovery_time
                result.observations.append(f"Recovery completed in {recovery_time:.2f}s")
            else:
                result.observations.append("Recovery failed")

            # Check steady state after experiment
            if experiment.steady_state_hypothesis:
                # Wait a bit for system to stabilize
                await asyncio.sleep(MIN_RECOVERY_TIME)
                result.steady_state_after = experiment.steady_state_hypothesis()

            result.status = ExperimentStatus.COMPLETED
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

            # Generate insights
            result.insights = self._generate_insights(experiment, result)
            result.recommendations = self._generate_recommendations(experiment, result)

        except Exception as e:
            self.logger.error(f"Chaos experiment failed: {experiment_name} - {e}")
            result.status = ExperimentStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()

            # Emergency recovery
            await self._emergency_recovery(experiment)

        self.results[experiment_name] = result
        self.logger.info(f"Chaos experiment completed: {experiment_name} - {result.status.value}")

        return result

    async def _safety_check(self, experiment: ChaosExperiment) -> bool:
        """Perform safety checks before running experiment."""
        # Check blast radius
        if experiment.blast_radius > experiment.max_impact:
            self.logger.error(
                f"Blast radius {experiment.blast_radius} exceeds max impact {experiment.max_impact}"
            )
            return False

        # Check system health
        for check in experiment.safety_checks:
            if not check():
                self.logger.error("Safety check failed")
                return False

        # Check target health
        unhealthy_targets = [t for t in experiment.targets if not t.is_healthy()]
        if unhealthy_targets:
            self.logger.error(f"Unhealthy targets found: {[t.name for t in unhealthy_targets]}")
            return False

        return True

    async def _monitor_experiment(
        self, experiment: ChaosExperiment, result: ChaosResult, injector: FailureInjector
    ) -> None:
        """Monitor experiment progress."""
        monitor_interval = 10  # 10 seconds
        total_duration = experiment.duration
        elapsed = 0

        while elapsed < total_duration:
            await asyncio.sleep(monitor_interval)
            elapsed += monitor_interval

            # Check if failure is still active
            if not injector.is_failure_active(experiment.targets):
                result.observations.append(f"Failure naturally recovered at {elapsed}s")
                break

            # Check circuit breaker conditions
            if experiment.circuit_breaker:
                for check in experiment.safety_checks:
                    if not check():
                        result.observations.append(f"Circuit breaker triggered at {elapsed}s")
                        return

            # Collect metrics
            result.metrics[f"checkpoint_{elapsed}s"] = {
                "timestamp": datetime.now().isoformat(),
                "failure_active": injector.is_failure_active(experiment.targets),
                "target_health": [t.is_healthy() for t in experiment.targets],
            }

        result.observations.append(f"Experiment duration completed: {elapsed}s")

    async def _emergency_recovery(self, experiment: ChaosExperiment) -> None:
        """Perform emergency recovery."""
        self.logger.info(f"Performing emergency recovery for {experiment.name}")

        # Try to recover using all available injectors
        for injector in self.injectors.values():
            try:
                await injector.recover(experiment.targets)
            except Exception as e:
                self.logger.error(
                    f"Emergency recovery failed with {injector.__class__.__name__}: {e}"
                )

        # Execute custom rollbacks
        for rollback in experiment.rollbacks:
            try:
                rollback()
            except Exception as e:
                self.logger.error(f"Custom rollback failed: {e}")

    def _generate_insights(self, experiment: ChaosExperiment, result: ChaosResult) -> list[str]:
        """Generate insights from experiment results."""
        insights = []

        if result.success:
            insights.append("System demonstrated resilience to the injected failure")
            if result.recovery_time and result.recovery_time < 60:
                insights.append("System recovery was fast (< 1 minute)")
        else:
            insights.append("System showed vulnerability to the injected failure")
            if not result.steady_state_after:
                insights.append("System did not return to steady state")
            if result.recovery_time and result.recovery_time > 300:
                insights.append("System recovery was slow (> 5 minutes)")

        return insights

    def _generate_recommendations(
        self, experiment: ChaosExperiment, result: ChaosResult
    ) -> list[str]:
        """Generate recommendations based on experiment results."""
        recommendations = []

        if not result.success:
            if experiment.failure_type == FailureType.NETWORK_LATENCY:
                recommendations.append("Consider implementing timeout and retry mechanisms")
                recommendations.append("Add circuit breakers for external dependencies")
            elif experiment.failure_type == FailureType.CPU_STRESS:
                recommendations.append("Implement CPU throttling and load shedding")
                recommendations.append("Consider horizontal scaling for CPU-intensive workloads")
            elif experiment.failure_type == FailureType.PROCESS_KILL:
                recommendations.append("Ensure proper process supervision and restart policies")
                recommendations.append("Implement graceful shutdown handling")
            elif experiment.failure_type == FailureType.MEMORY_STRESS:
                recommendations.append("Implement memory limits and monitoring")
                recommendations.append("Add memory-based auto-scaling")

        if result.recovery_time and result.recovery_time > 60:
            recommendations.append("Investigate and optimize recovery procedures")
            recommendations.append("Consider implementing faster health checks")

        return recommendations

    async def run_experiment_suite(self, experiment_names: list[str]) -> dict[str, ChaosResult]:
        """Run multiple experiments in sequence.

        Args:
            experiment_names: List of experiment names to run

        Returns:
            Dictionary of experiment results
        """
        results = {}

        for name in experiment_names:
            try:
                result = await self.run_experiment(name)
                results[name] = result

                # Wait between experiments for system stabilization
                if result.status == ExperimentStatus.COMPLETED:
                    await asyncio.sleep(MIN_RECOVERY_TIME)
                else:
                    # Wait longer if experiment failed
                    await asyncio.sleep(MIN_RECOVERY_TIME * 2)

            except Exception as e:
                self.logger.error(f"Failed to run experiment {name}: {e}")
                results[name] = ChaosResult(
                    experiment_name=name,
                    status=ExperimentStatus.FAILED,
                    start_time=datetime.now(),
                    error_message=str(e),
                )

        return results

    def generate_chaos_report(self, output_path: Path) -> None:
        """Generate comprehensive chaos engineering report.

        Args:
            output_path: Path to save report
        """
        if not self.results:
            self.logger.warning("No experiment results to report")
            return

        report_content = f"""# Chaos Engineering Report

Generated: {datetime.now()}

## Summary

- **Total Experiments**: {len(self.results)}
- **Successful Experiments**: {sum(1 for r in self.results.values() if r.success)}
- **Failed Experiments**: {sum(1 for r in self.results.values() if not r.success)}
- **Success Rate**: {sum(1 for r in self.results.values() if r.success) / len(self.results):.1%}

## Experiment Results

| Experiment | Status | Duration | Recovery Time | Steady State | Insights |
|------------|--------|----------|---------------|--------------|----------|
"""

        for result in self.results.values():
            status = "✅ PASS" if result.success else "❌ FAIL"
            duration = f"{result.duration:.1f}s" if result.duration else "N/A"
            recovery = f"{result.recovery_time:.1f}s" if result.recovery_time else "N/A"
            steady_state = "✅" if result.steady_state_after else "❌"
            insights_count = len(result.insights)

            report_content += f"| {result.experiment_name} | {status} | {duration} | {recovery} | {steady_state} | {insights_count} |\n"

        report_content += "\n## Detailed Results\n"

        for result in self.results.values():
            report_content += f"""
### {result.experiment_name}

- **Status**: {result.status.value}
- **Duration**: {result.duration:.2f if result.duration else 0}s
- **Recovery Time**: {result.recovery_time:.2f if result.recovery_time else 'N/A'}s
- **Steady State Before**: {'✅' if result.steady_state_before else '❌'}
- **Steady State After**: {'✅' if result.steady_state_after else '❌'}

#### Observations
"""
            for obs in result.observations:
                report_content += f"- {obs}\n"

            if result.insights:
                report_content += "\n#### Insights\n"
                for insight in result.insights:
                    report_content += f"- {insight}\n"

            if result.recommendations:
                report_content += "\n#### Recommendations\n"
                for rec in result.recommendations:
                    report_content += f"- {rec}\n"

            if result.error_message:
                report_content += f"\n**Error**: {result.error_message}\n"

        # Overall recommendations
        report_content += """
## Overall Recommendations

Based on the chaos experiments:

1. **Resilience Improvements**: Focus on failed experiments for resilience gaps
2. **Recovery Optimization**: Improve recovery times for slow-recovering systems
3. **Monitoring Enhancement**: Add monitoring for failure scenarios tested
4. **Automation**: Automate recovery procedures that were manually executed

## Next Steps

1. Address identified vulnerabilities
2. Implement recommended resilience patterns
3. Schedule regular chaos experiments
4. Create runbooks for failure scenarios
"""

        output_path.write_text(report_content)
        self.logger.info(f"Chaos engineering report generated: {output_path}")


# Predefined experiments for T-Developer
def create_t_developer_experiments() -> list[ChaosExperiment]:
    """Create predefined chaos experiments for T-Developer."""
    experiments = []

    # API latency experiment
    api_latency_exp = ChaosExperiment(
        name="api_latency_test",
        description="Test API resilience to network latency",
        failure_type=FailureType.NETWORK_LATENCY,
        targets=[ChaosTarget("api_network", "network", "eth0")],
        duration=180,  # 3 minutes
        method={"latency_ms": 500, "jitter_ms": 100},
    )
    experiments.append(api_latency_exp)

    # Agent process kill experiment
    agent_kill_exp = ChaosExperiment(
        name="agent_process_kill",
        description="Test agent recovery from process termination",
        failure_type=FailureType.PROCESS_KILL,
        targets=[
            ChaosTarget("research_agent", "process", "research_agent.py"),
            ChaosTarget("planner_agent", "process", "planner_agent.py"),
        ],
        duration=120,  # 2 minutes
        blast_radius=0.5,  # Kill 50% of agent processes
    )
    experiments.append(agent_kill_exp)

    # Memory stress experiment
    memory_stress_exp = ChaosExperiment(
        name="memory_stress_test",
        description="Test system behavior under memory pressure",
        failure_type=FailureType.MEMORY_STRESS,
        targets=[ChaosTarget("system_memory", "system", "memory")],
        duration=300,  # 5 minutes
        method={"memory_mb": 2048},  # 2GB stress
    )
    experiments.append(memory_stress_exp)

    return experiments


# Main chaos engineering function
async def run_chaos_experiments(output_dir: Path) -> dict[str, Any]:
    """Run chaos engineering experiments.

    Args:
        output_dir: Directory to save results

    Returns:
        Chaos engineering results summary
    """
    output_dir.mkdir(exist_ok=True, parents=True)

    # Initialize chaos orchestrator
    orchestrator = ChaosOrchestrator()

    # Register predefined experiments
    experiments = create_t_developer_experiments()
    for exp in experiments:
        orchestrator.register_experiment(exp)

    # Run experiments
    experiment_names = [exp.name for exp in experiments]
    results = await orchestrator.run_experiment_suite(experiment_names)

    # Generate report
    timestamp = int(time.time())
    report_path = output_dir / f"chaos_engineering_report_{timestamp}.md"
    orchestrator.generate_chaos_report(report_path)

    # Calculate summary
    total_experiments = len(results)
    successful_experiments = sum(1 for r in results.values() if r.success)

    return {
        "total_experiments": total_experiments,
        "successful_experiments": successful_experiments,
        "success_rate": successful_experiments / total_experiments if total_experiments > 0 else 0,
        "report_path": str(report_path),
        "results": {name: result.success for name, result in results.items()},
    }
