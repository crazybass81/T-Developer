"""Load Testing - Automated load testing for T-Developer.

Phase 6: P6-T2 - Reliability Engineering
Comprehensive load testing automation and reporting.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

# Constants
DEFAULT_K6_BINARY: str = "k6"
DEFAULT_TEST_DURATION: int = 300  # 5 minutes
DEFAULT_VU_COUNT: int = 10
DEFAULT_RPS_TARGET: int = 100

logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    name: str
    script_path: Path
    duration: int = DEFAULT_TEST_DURATION
    virtual_users: int = DEFAULT_VU_COUNT
    rps_target: Optional[int] = None
    environment: dict[str, str] = field(default_factory=dict)
    thresholds: dict[str, list[str]] = field(default_factory=dict)
    scenarios: dict[str, Any] = field(default_factory=dict)

    def to_k6_options(self) -> dict[str, Any]:
        """Convert to k6 options format."""
        options = {
            "duration": f"{self.duration}s",
            "vus": self.virtual_users,
        }

        if self.rps_target:
            options["scenarios"] = {
                "constant_request_rate": {
                    "executor": "constant-arrival-rate",
                    "rate": self.rps_target,
                    "timeUnit": "1s",
                    "duration": f"{self.duration}s",
                    "preAllocatedVUs": self.virtual_users,
                    "maxVUs": self.virtual_users * 2,
                }
            }
        elif self.scenarios:
            options["scenarios"] = self.scenarios

        if self.thresholds:
            options["thresholds"] = self.thresholds

        return options


@dataclass
class LoadTestResult:
    """Load test execution result."""

    test_name: str
    success: bool
    start_time: datetime
    end_time: datetime
    duration: float

    # K6 metrics
    http_reqs: int = 0
    http_req_duration_avg: float = 0.0
    http_req_duration_p95: float = 0.0
    http_req_duration_p99: float = 0.0
    http_req_failed_rate: float = 0.0
    vus_max: int = 0
    iterations: int = 0

    # Custom metrics
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    response_time_ms: float = 0.0

    # Detailed results
    raw_output: str = ""
    error_message: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed_thresholds(self) -> bool:
        """Check if all thresholds passed."""
        return (
            self.http_req_duration_p95 < 200
            and self.http_req_failed_rate < 0.01  # P95 < 200ms
            and self.error_rate < 0.05  # Error rate < 1%  # Custom error rate < 5%
        )


@dataclass
class LoadTestSuite:
    """Collection of load tests."""

    name: str
    description: str
    tests: list[LoadTestConfig] = field(default_factory=list)
    results: list[LoadTestResult] = field(default_factory=list)
    global_config: dict[str, Any] = field(default_factory=dict)

    def add_test(self, test_config: LoadTestConfig) -> None:
        """Add test to suite."""
        self.tests.append(test_config)

    def get_overall_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.results:
            return 0.0
        successful = sum(1 for r in self.results if r.success and r.passed_thresholds)
        return successful / len(self.results)


class K6Runner:
    """Execute k6 load tests."""

    def __init__(self, k6_binary: str = DEFAULT_K6_BINARY):
        """Initialize k6 runner.

        Args:
            k6_binary: Path to k6 binary
        """
        self.k6_binary = k6_binary
        self.logger = logging.getLogger(self.__class__.__name__)

        # Verify k6 is available
        self._verify_k6_installation()

    def _verify_k6_installation(self) -> None:
        """Verify k6 is installed and accessible."""
        try:
            result = subprocess.run(
                [self.k6_binary, "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError(f"k6 not found or not working: {result.stderr}")
            self.logger.info(f"k6 version: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(f"k6 not available: {e}")

    async def run_test(self, config: LoadTestConfig) -> LoadTestResult:
        """Run a single load test.

        Args:
            config: Load test configuration

        Returns:
            Load test result
        """
        self.logger.info(f"Starting load test: {config.name}")

        start_time = datetime.now()

        try:
            # Prepare test script
            script_path = await self._prepare_test_script(config)

            # Build k6 command
            cmd = self._build_k6_command(script_path, config)

            # Execute test
            result = await self._execute_k6_test(cmd, config)

            # Parse results
            test_result = self._parse_k6_output(result, config, start_time)

            self.logger.info(
                f"Load test completed: {config.name} - {'PASS' if test_result.success else 'FAIL'}"
            )

            return test_result

        except Exception as e:
            self.logger.error(f"Load test failed: {config.name} - {e}")

            return LoadTestResult(
                test_name=config.name,
                success=False,
                start_time=start_time,
                end_time=datetime.now(),
                duration=(datetime.now() - start_time).total_seconds(),
                error_message=str(e),
            )

    async def _prepare_test_script(self, config: LoadTestConfig) -> Path:
        """Prepare k6 test script with configuration."""
        # Read original script
        with open(config.script_path) as f:
            script_content = f.read()

        # Inject configuration
        k6_options = config.to_k6_options()
        options_json = json.dumps(k6_options, indent=2)

        # Replace or inject options
        if "export const options" in script_content:
            # Replace existing options
            import re

            pattern = r"export const options = \{[^}]*\};"
            replacement = f"export const options = {options_json};"
            script_content = re.sub(pattern, replacement, script_content, flags=re.DOTALL)
        else:
            # Inject options after imports
            injection_point = script_content.find("\n\n")
            if injection_point == -1:
                injection_point = 0

            options_block = f"\n\nexport const options = {options_json};\n\n"
            script_content = (
                script_content[:injection_point] + options_block + script_content[injection_point:]
            )

        # Create temporary script file
        temp_dir = Path(tempfile.mkdtemp(prefix="k6_test_"))
        temp_script = temp_dir / f"{config.name}.js"

        with open(temp_script, "w") as f:
            f.write(script_content)

        return temp_script

    def _build_k6_command(self, script_path: Path, config: LoadTestConfig) -> list[str]:
        """Build k6 command line."""
        cmd = [self.k6_binary, "run", "--out", "json=results.json", "--quiet"]

        # Add environment variables
        for key, value in config.environment.items():
            cmd.extend(["--env", f"{key}={value}"])

        # Add script path
        cmd.append(str(script_path))

        return cmd

    async def _execute_k6_test(
        self, cmd: list[str], config: LoadTestConfig
    ) -> subprocess.CompletedProcess:
        """Execute k6 test command."""
        # Set timeout based on test duration
        timeout = config.duration + 120  # Add 2 minutes buffer

        # Run k6 test
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=Path.cwd()
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

            return subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout=stdout.decode(),
                stderr=stderr.decode(),
            )

        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError(f"Test timeout after {timeout} seconds")

    def _parse_k6_output(
        self, result: subprocess.CompletedProcess, config: LoadTestConfig, start_time: datetime
    ) -> LoadTestResult:
        """Parse k6 output into test result."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Initialize test result
        test_result = LoadTestResult(
            test_name=config.name,
            success=result.returncode == 0,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            raw_output=result.stdout,
        )

        if result.returncode != 0:
            test_result.error_message = result.stderr
            return test_result

        # Parse k6 summary from output
        try:
            # Look for metrics in output
            output_lines = result.stdout.split("\n")

            for line in output_lines:
                line = line.strip()

                if "http_reqs" in line:
                    # Extract request count
                    import re

                    match = re.search(r"(\d+)", line)
                    if match:
                        test_result.http_reqs = int(match.group(1))

                elif "http_req_duration" in line and "avg" in line:
                    # Extract average duration
                    match = re.search(r"avg=(\d+(?:\.\d+)?)ms", line)
                    if match:
                        test_result.http_req_duration_avg = float(match.group(1))

                elif "http_req_duration" in line and "p(95)" in line:
                    # Extract P95 duration
                    match = re.search(r"p\(95\)=(\d+(?:\.\d+)?)ms", line)
                    if match:
                        test_result.http_req_duration_p95 = float(match.group(1))

                elif "http_req_duration" in line and "p(99)" in line:
                    # Extract P99 duration
                    match = re.search(r"p\(99\)=(\d+(?:\.\d+)?)ms", line)
                    if match:
                        test_result.http_req_duration_p99 = float(match.group(1))

                elif "http_req_failed" in line:
                    # Extract failure rate
                    match = re.search(r"(\d+(?:\.\d+)?)%", line)
                    if match:
                        test_result.http_req_failed_rate = float(match.group(1)) / 100

                elif "vus_max" in line:
                    # Extract max VUs
                    match = re.search(r"(\d+)", line)
                    if match:
                        test_result.vus_max = int(match.group(1))

                elif "iterations" in line:
                    # Extract iterations
                    match = re.search(r"(\d+)", line)
                    if match:
                        test_result.iterations = int(match.group(1))

            # Calculate derived metrics
            if duration > 0:
                test_result.throughput_rps = test_result.http_reqs / duration

            test_result.error_rate = test_result.http_req_failed_rate
            test_result.response_time_ms = test_result.http_req_duration_avg

        except Exception as e:
            self.logger.warning(f"Error parsing k6 output: {e}")

        return test_result


class LoadTestManager:
    """Manage load testing suites and execution."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize load test manager.

        Args:
            config: Global configuration
        """
        self.config = config or {}
        self.runner = K6Runner(self.config.get("k6_binary", DEFAULT_K6_BINARY))
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load test configurations
        self.suites: dict[str, LoadTestSuite] = {}

    def create_suite(self, name: str, description: str) -> LoadTestSuite:
        """Create a new test suite.

        Args:
            name: Suite name
            description: Suite description

        Returns:
            Created test suite
        """
        suite = LoadTestSuite(name=name, description=description)
        self.suites[name] = suite
        return suite

    def load_suite_from_config(self, config_path: Path) -> LoadTestSuite:
        """Load test suite from configuration file.

        Args:
            config_path: Path to suite configuration

        Returns:
            Loaded test suite
        """
        with open(config_path) as f:
            if config_path.suffix.lower() == ".yaml":
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)

        suite = LoadTestSuite(
            name=config_data["name"],
            description=config_data.get("description", ""),
            global_config=config_data.get("global_config", {}),
        )

        # Load test configurations
        for test_config in config_data.get("tests", []):
            test = LoadTestConfig(
                name=test_config["name"],
                script_path=Path(test_config["script_path"]),
                duration=test_config.get("duration", DEFAULT_TEST_DURATION),
                virtual_users=test_config.get("virtual_users", DEFAULT_VU_COUNT),
                rps_target=test_config.get("rps_target"),
                environment=test_config.get("environment", {}),
                thresholds=test_config.get("thresholds", {}),
                scenarios=test_config.get("scenarios", {}),
            )
            suite.add_test(test)

        self.suites[suite.name] = suite
        return suite

    async def run_suite(self, suite_name: str) -> LoadTestSuite:
        """Run all tests in a suite.

        Args:
            suite_name: Name of suite to run

        Returns:
            Suite with results
        """
        if suite_name not in self.suites:
            raise ValueError(f"Suite '{suite_name}' not found")

        suite = self.suites[suite_name]
        self.logger.info(f"Running load test suite: {suite_name}")

        # Clear previous results
        suite.results.clear()

        # Run tests sequentially or in parallel based on configuration
        run_parallel = suite.global_config.get("run_parallel", False)

        if run_parallel:
            # Run tests in parallel
            tasks = [self.runner.run_test(test) for test in suite.tests]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Test failed with exception: {result}")
                else:
                    suite.results.append(result)
        else:
            # Run tests sequentially
            for test in suite.tests:
                result = await self.runner.run_test(test)
                suite.results.append(result)

                # Optional delay between tests
                delay = suite.global_config.get("test_delay", 0)
                if delay > 0:
                    await asyncio.sleep(delay)

        self.logger.info(f"Load test suite completed: {suite_name}")
        self.logger.info(f"Success rate: {suite.get_overall_success_rate():.1%}")

        return suite

    async def run_continuous_testing(
        self, suite_name: str, interval_minutes: int = 60, max_iterations: Optional[int] = None
    ) -> None:
        """Run continuous load testing.

        Args:
            suite_name: Name of suite to run continuously
            interval_minutes: Minutes between test runs
            max_iterations: Maximum number of iterations (None for infinite)
        """
        iteration = 0

        while max_iterations is None or iteration < max_iterations:
            self.logger.info(f"Starting continuous test iteration {iteration + 1}")

            try:
                suite = await self.run_suite(suite_name)

                # Log results
                success_rate = suite.get_overall_success_rate()
                self.logger.info(f"Iteration {iteration + 1} success rate: {success_rate:.1%}")

                # Generate report
                report_path = Path(f"load_test_report_{int(time.time())}.json")
                self.generate_json_report(suite, report_path)

            except Exception as e:
                self.logger.error(f"Continuous test iteration failed: {e}")

            iteration += 1

            # Wait for next iteration
            if max_iterations is None or iteration < max_iterations:
                self.logger.info(f"Waiting {interval_minutes} minutes for next iteration...")
                await asyncio.sleep(interval_minutes * 60)

    def generate_report(self, suite: LoadTestSuite, output_path: Path) -> None:
        """Generate load test report.

        Args:
            suite: Test suite with results
            output_path: Path to save report
        """
        report_content = f"""# Load Test Report: {suite.name}

Generated: {datetime.now()}
Description: {suite.description}

## Summary

- **Tests Run**: {len(suite.results)}
- **Success Rate**: {suite.get_overall_success_rate():.1%}
- **Total Duration**: {sum(r.duration for r in suite.results):.1f} seconds

## Test Results

| Test Name | Status | Duration | RPS | P95 Latency | Error Rate | Thresholds |
|-----------|--------|----------|-----|-------------|------------|------------|
"""

        for result in suite.results:
            status = "✅ PASS" if result.success and result.passed_thresholds else "❌ FAIL"
            thresholds = "✅ PASS" if result.passed_thresholds else "❌ FAIL"

            report_content += f"| {result.test_name} | {status} | {result.duration:.1f}s | {result.throughput_rps:.1f} | {result.http_req_duration_p95:.1f}ms | {result.error_rate:.1%} | {thresholds} |\n"

        report_content += "\n## Detailed Results\n"

        for result in suite.results:
            report_content += f"""
### {result.test_name}

- **Status**: {'PASS' if result.success else 'FAIL'}
- **Duration**: {result.duration:.2f} seconds
- **Total Requests**: {result.http_reqs:,}
- **Throughput**: {result.throughput_rps:.1f} RPS
- **Response Times**:
  - Average: {result.http_req_duration_avg:.1f}ms
  - P95: {result.http_req_duration_p95:.1f}ms
  - P99: {result.http_req_duration_p99:.1f}ms
- **Error Rate**: {result.error_rate:.2%}
- **Max VUs**: {result.vus_max}
- **Iterations**: {result.iterations:,}

**Threshold Compliance**: {'PASS' if result.passed_thresholds else 'FAIL'}
"""

            if result.error_message:
                report_content += f"\n**Error**: {result.error_message}\n"

        # Performance targets comparison
        report_content += """
## Performance Targets

| Metric | Target | Status |
|--------|--------|---------|
| P95 Latency | < 200ms | TBD |
| Error Rate | < 1% | TBD |
| Throughput | > 100 RPS | TBD |

## Recommendations

Based on the load test results:

1. **Performance Optimization**: Focus on tests that failed latency thresholds
2. **Error Investigation**: Investigate tests with high error rates
3. **Capacity Planning**: Consider scaling if throughput targets not met
4. **Monitoring**: Set up alerts for performance degradation

## Next Steps

1. Address failed tests and performance bottlenecks
2. Set up continuous load testing in CI/CD pipeline
3. Establish performance baseline and regression detection
4. Implement auto-scaling based on load test results
"""

        output_path.write_text(report_content)
        self.logger.info(f"Load test report generated: {output_path}")

    def generate_json_report(self, suite: LoadTestSuite, output_path: Path) -> None:
        """Generate JSON format report for automation.

        Args:
            suite: Test suite with results
            output_path: Path to save JSON report
        """
        report_data = {
            "suite_name": suite.name,
            "description": suite.description,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "tests_run": len(suite.results),
                "success_rate": suite.get_overall_success_rate(),
                "total_duration": sum(r.duration for r in suite.results),
                "overall_status": "PASS" if suite.get_overall_success_rate() >= 0.8 else "FAIL",
            },
            "results": [],
        }

        for result in suite.results:
            result_data = {
                "test_name": result.test_name,
                "success": result.success,
                "passed_thresholds": result.passed_thresholds,
                "duration": result.duration,
                "metrics": {
                    "http_reqs": result.http_reqs,
                    "throughput_rps": result.throughput_rps,
                    "response_time_avg": result.http_req_duration_avg,
                    "response_time_p95": result.http_req_duration_p95,
                    "response_time_p99": result.http_req_duration_p99,
                    "error_rate": result.error_rate,
                    "max_vus": result.vus_max,
                    "iterations": result.iterations,
                },
                "error_message": result.error_message,
                "metadata": result.metadata,
            }
            report_data["results"].append(result_data)

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"JSON report generated: {output_path}")


# Main load testing function
async def run_load_tests(test_config_path: Path, output_dir: Path) -> dict[str, Any]:
    """Run load tests from configuration.

    Args:
        test_config_path: Path to test configuration file
        output_dir: Directory to save results

    Returns:
        Load test results summary
    """
    output_dir.mkdir(exist_ok=True, parents=True)

    # Initialize load test manager
    manager = LoadTestManager()

    # Load test suite
    suite = manager.load_suite_from_config(test_config_path)

    # Run tests
    completed_suite = await manager.run_suite(suite.name)

    # Generate reports
    timestamp = int(time.time())

    # Markdown report
    report_path = output_dir / f"load_test_report_{timestamp}.md"
    manager.generate_report(completed_suite, report_path)

    # JSON report for automation
    json_report_path = output_dir / f"load_test_results_{timestamp}.json"
    manager.generate_json_report(completed_suite, json_report_path)

    # Return summary
    return {
        "suite_name": completed_suite.name,
        "tests_run": len(completed_suite.results),
        "success_rate": completed_suite.get_overall_success_rate(),
        "overall_status": "PASS" if completed_suite.get_overall_success_rate() >= 0.8 else "FAIL",
        "reports": {"markdown": str(report_path), "json": str(json_report_path)},
    }
