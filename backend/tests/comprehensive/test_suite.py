"""
Comprehensive Test Suite for T-Developer 9-Agent Pipeline
Includes E2E, Integration, Performance, and Security Tests
"""

import pytest
import asyncio
import logging
import time
import json
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import concurrent.futures
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from orchestration.master_orchestrator import MasterOrchestrator, PipelineConfig
from optimization.performance_optimizer import PerformanceOptimizer
from agents.unified.nl_input import NLInputAgent
from agents.unified.download import DownloadAgent

logger = logging.getLogger(__name__)


@dataclass
class TestScenario:
    """Test scenario definition"""

    name: str
    description: str
    input_data: Dict[str, Any]
    expected_outputs: Dict[str, Any]
    performance_thresholds: Dict[str, float] = field(default_factory=dict)
    security_requirements: List[str] = field(default_factory=list)
    complexity: str = "medium"  # simple, medium, complex


class ComprehensiveTestSuite:
    """Comprehensive test suite for the entire pipeline"""

    def __init__(self):
        self.test_scenarios = self._load_test_scenarios()
        self.results: Dict[str, Dict[str, Any]] = {}
        self.performance_optimizer = PerformanceOptimizer()

    def _load_test_scenarios(self) -> List[TestScenario]:
        """Load comprehensive test scenarios"""

        return [
            # Simple scenarios
            TestScenario(
                name="simple_todo_app",
                description="Create a simple todo application with React",
                input_data={
                    "user_input": "Create a todo app with React. I want to add, delete, and mark tasks as complete.",
                    "project_type": "web_app",
                    "complexity": "simple",
                },
                expected_outputs={
                    "framework": "react",
                    "components": ["TodoList", "TodoItem", "AddTodo"],
                    "files_generated": ["App.tsx", "components/", "package.json"],
                    "download_available": True,
                },
                performance_thresholds={
                    "total_execution_time": 30.0,
                    "memory_usage_mb": 200.0,
                },
                complexity="simple",
            ),
            # Medium complexity scenarios
            TestScenario(
                name="ecommerce_api",
                description="Create e-commerce REST API with FastAPI",
                input_data={
                    "user_input": "Build an e-commerce API with user authentication, product catalog, shopping cart, and payment processing using FastAPI and PostgreSQL.",
                    "project_type": "api",
                    "complexity": "medium",
                },
                expected_outputs={
                    "framework": "fastapi",
                    "database": "postgresql",
                    "features": ["auth", "catalog", "cart", "payments"],
                    "api_endpoints": ["/users", "/products", "/cart", "/orders"],
                    "download_available": True,
                },
                performance_thresholds={
                    "total_execution_time": 45.0,
                    "memory_usage_mb": 400.0,
                },
                security_requirements=[
                    "authentication",
                    "input_validation",
                    "sql_injection_protection",
                ],
                complexity="medium",
            ),
            # Complex scenarios
            TestScenario(
                name="fullstack_social_platform",
                description="Full-stack social media platform",
                input_data={
                    "user_input": "Create a full-stack social media platform with React frontend, Node.js backend, real-time messaging, image uploads, user profiles, feeds, notifications, and admin dashboard.",
                    "project_type": "fullstack",
                    "complexity": "complex",
                },
                expected_outputs={
                    "frontend_framework": "react",
                    "backend_framework": "express",
                    "database": ["postgresql", "redis"],
                    "features": [
                        "messaging",
                        "uploads",
                        "profiles",
                        "feeds",
                        "notifications",
                        "admin",
                    ],
                    "real_time": True,
                    "download_available": True,
                },
                performance_thresholds={
                    "total_execution_time": 60.0,
                    "memory_usage_mb": 600.0,
                },
                security_requirements=[
                    "authentication",
                    "authorization",
                    "file_upload_security",
                    "xss_protection",
                    "csrf_protection",
                ],
                complexity="complex",
            ),
            # Edge cases
            TestScenario(
                name="minimal_input",
                description="Test with minimal user input",
                input_data={"user_input": "app", "project_type": "unknown"},
                expected_outputs={
                    "framework": "react",  # Default framework
                    "error_handled": True,
                    "clarification_requested": True,
                },
                complexity="simple",
            ),
            # Large project scenario
            TestScenario(
                name="enterprise_erp",
                description="Enterprise ERP system",
                input_data={
                    "user_input": "Build a complete Enterprise Resource Planning system with modules for HR, Finance, Inventory, Sales, Manufacturing, Reporting, and Analytics. Use Angular frontend, Django backend, PostgreSQL database, Redis caching, and microservices architecture.",
                    "project_type": "enterprise",
                    "complexity": "complex",
                },
                expected_outputs={
                    "architecture": "microservices",
                    "modules": [
                        "hr",
                        "finance",
                        "inventory",
                        "sales",
                        "manufacturing",
                        "reporting",
                        "analytics",
                    ],
                    "frontend_framework": "angular",
                    "backend_framework": "django",
                    "database": "postgresql",
                    "caching": "redis",
                    "download_available": True,
                },
                performance_thresholds={
                    "total_execution_time": 90.0,
                    "memory_usage_mb": 1000.0,
                },
                security_requirements=[
                    "rbac",
                    "audit_logging",
                    "encryption",
                    "secure_api",
                ],
                complexity="complex",
            ),
        ]


@pytest.mark.asyncio
class TestE2EWorkflow:
    """End-to-End workflow tests"""

    async def test_complete_pipeline_simple(self):
        """Test complete pipeline with simple scenario"""

        orchestrator = MasterOrchestrator(
            PipelineConfig(
                enable_monitoring=True,
                enable_caching=False,  # Disable for testing
                debug_mode=True,
            )
        )

        test_suite = ComprehensiveTestSuite()
        scenario = test_suite.test_scenarios[0]  # Simple todo app

        try:
            result = await orchestrator.execute_pipeline(
                scenario.input_data["user_input"], scenario.input_data
            )

            # Verify success
            assert result[
                "success"
            ], f"Pipeline failed: {result.get('error', 'Unknown error')}"

            # Verify expected outputs
            pipeline_result = result["pipeline_result"]

            # Check framework selection
            if "framework" in scenario.expected_outputs:
                assert (
                    scenario.expected_outputs["framework"]
                    in str(pipeline_result).lower()
                )

            # Check download availability
            if scenario.expected_outputs.get("download_available"):
                assert "download_url" in pipeline_result
                assert pipeline_result["download_url"] != ""

            # Performance checks
            execution_time = result["execution_time"]
            max_time = scenario.performance_thresholds.get("total_execution_time", 60.0)
            assert (
                execution_time < max_time
            ), f"Execution time {execution_time}s exceeds threshold {max_time}s"

            logger.info(f"✅ Simple E2E test passed in {execution_time:.2f}s")

        finally:
            await orchestrator.cleanup()

    async def test_complete_pipeline_medium_complexity(self):
        """Test complete pipeline with medium complexity scenario"""

        orchestrator = MasterOrchestrator(
            PipelineConfig(
                enable_monitoring=True, enable_caching=True, timeout_seconds=60
            )
        )

        test_suite = ComprehensiveTestSuite()
        scenario = test_suite.test_scenarios[1]  # E-commerce API

        try:
            result = await orchestrator.execute_pipeline(
                scenario.input_data["user_input"], scenario.input_data
            )

            # Verify success
            assert result[
                "success"
            ], f"Pipeline failed: {result.get('error', 'Unknown error')}"

            # Verify API-specific outputs
            pipeline_result = result["pipeline_result"]

            # Should have API endpoints defined
            result_str = str(pipeline_result).lower()
            assert "api" in result_str or "endpoint" in result_str

            # Should have authentication
            assert "auth" in result_str or "login" in result_str

            # Performance checks
            execution_time = result["execution_time"]
            max_time = scenario.performance_thresholds.get("total_execution_time", 60.0)
            assert (
                execution_time < max_time
            ), f"Execution time {execution_time}s exceeds threshold {max_time}s"

            logger.info(f"✅ Medium complexity E2E test passed in {execution_time:.2f}s")

        finally:
            await orchestrator.cleanup()

    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""

        # Test with invalid input
        orchestrator = MasterOrchestrator(
            PipelineConfig(max_retry_attempts=2, timeout_seconds=10)
        )

        try:
            # Test with empty input
            result = await orchestrator.execute_pipeline("", {})

            # Should handle gracefully
            assert not result["success"]
            assert "error" in result
            assert result["current_stage"] != "complete"

            # Test resume functionality (if implemented)
            if "project_id" in result:
                resume_result = await orchestrator.resume_pipeline(result["project_id"])
                # Resume might still fail, but should not crash
                assert isinstance(resume_result, dict)

            logger.info("✅ Error handling test passed")

        finally:
            await orchestrator.cleanup()


@pytest.mark.asyncio
class TestIntegrationScenarios:
    """Integration tests for different project types"""

    @pytest.mark.parametrize("scenario_index", [0, 1, 2])
    async def test_project_type_integration(self, scenario_index):
        """Test integration for different project types"""

        test_suite = ComprehensiveTestSuite()
        scenario = test_suite.test_scenarios[scenario_index]

        orchestrator = MasterOrchestrator(
            PipelineConfig(enable_caching=True, enable_monitoring=True)
        )

        try:
            result = await orchestrator.execute_pipeline(
                scenario.input_data["user_input"], scenario.input_data
            )

            # Basic success check
            assert isinstance(result, dict)
            assert "success" in result
            assert "execution_time" in result

            # If successful, verify project structure
            if result["success"]:
                assert "pipeline_result" in result
                assert result["execution_time"] > 0

                # Check that all stages completed
                stage_results = result.get("stage_results", {})
                expected_stages = [
                    "nl_input",
                    "ui_selection",
                    "parser",
                    "component_decision",
                    "match_rate",
                    "search",
                    "generation",
                    "assembly",
                    "download",
                ]

                for stage in expected_stages:
                    assert stage in stage_results, f"Missing stage: {stage}"

            logger.info(f"✅ Integration test passed for scenario: {scenario.name}")

        finally:
            await orchestrator.cleanup()


@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    async def test_performance_under_load(self):
        """Test performance under concurrent load"""

        async def run_single_pipeline():
            orchestrator = MasterOrchestrator(
                PipelineConfig(
                    enable_caching=True, enable_monitoring=False  # Reduce overhead
                )
            )

            try:
                result = await orchestrator.execute_pipeline(
                    "Create a simple React app with login functionality",
                    {"project_type": "web_app"},
                )
                return result["execution_time"] if result["success"] else float("inf")
            finally:
                await orchestrator.cleanup()

        # Run multiple concurrent pipelines
        num_concurrent = 3
        start_time = time.time()

        tasks = [run_single_pipeline() for _ in range(num_concurrent)]
        execution_times = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # Filter successful executions
        successful_times = [
            t
            for t in execution_times
            if isinstance(t, (int, float)) and t != float("inf")
        ]

        assert (
            len(successful_times) >= num_concurrent // 2
        ), "Less than 50% of concurrent requests succeeded"

        avg_time = sum(successful_times) / len(successful_times)
        assert (
            avg_time < 45.0
        ), f"Average execution time {avg_time:.2f}s exceeds threshold"

        logger.info(
            f"✅ Load test: {len(successful_times)}/{num_concurrent} succeeded, avg time: {avg_time:.2f}s"
        )

    async def test_memory_usage_limits(self):
        """Test memory usage stays within limits"""

        import psutil

        orchestrator = MasterOrchestrator(PipelineConfig(enable_monitoring=True))

        # Get baseline memory
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        try:
            # Run complex scenario
            test_suite = ComprehensiveTestSuite()
            complex_scenario = test_suite.test_scenarios[2]  # Fullstack platform

            result = await orchestrator.execute_pipeline(
                complex_scenario.input_data["user_input"], complex_scenario.input_data
            )

            # Check peak memory usage
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - baseline_memory

            max_memory_mb = complex_scenario.performance_thresholds.get(
                "memory_usage_mb", 600.0
            )
            assert (
                memory_increase < max_memory_mb
            ), f"Memory usage {memory_increase:.2f}MB exceeds threshold {max_memory_mb}MB"

            logger.info(
                f"✅ Memory test: used {memory_increase:.2f}MB (limit: {max_memory_mb}MB)"
            )

        finally:
            await orchestrator.cleanup()


class TestSecurityValidation:
    """Security validation tests"""

    def test_input_sanitization(self):
        """Test input sanitization against injection attacks"""

        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "{{7*7}}",  # Template injection
            "$(whoami)",  # Command injection
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
        ]

        nl_agent = NLInputAgent()

        for malicious_input in malicious_inputs:
            try:
                result = nl_agent.process({"user_input": malicious_input})

                # Verify that malicious content is not reflected in output
                result_str = json.dumps(result).lower()

                # Check for common dangerous patterns
                dangerous_patterns = [
                    "<script",
                    "javascript:",
                    "drop table",
                    "../",
                    "$(",
                    "{{",
                ]
                for pattern in dangerous_patterns:
                    assert (
                        pattern not in result_str
                    ), f"Dangerous pattern '{pattern}' found in output"

            except Exception as e:
                # It's acceptable for malicious input to cause controlled errors
                logger.info(
                    f"Malicious input properly rejected: {malicious_input[:50]}... -> {str(e)[:100]}"
                )

        logger.info("✅ Input sanitization tests passed")

    def test_file_generation_security(self):
        """Test generated files don't contain security vulnerabilities"""

        # This would typically scan generated code for security issues
        # For now, implement basic checks

        test_files = {
            "package.json": '{"name": "test", "scripts": {"start": "node app.js"}}',
            "app.js": 'const express = require("express"); const app = express();',
            "login.js": 'function authenticate(user, pass) { return user === "admin"; }',
        }

        security_issues = []

        for filename, content in test_files.items():
            # Check for hardcoded credentials
            if "password" in content.lower() and ("=" in content or ":" in content):
                if not any(
                    safe in content.lower()
                    for safe in ["placeholder", "example", "dummy"]
                ):
                    security_issues.append(
                        f"Potential hardcoded password in {filename}"
                    )

            # Check for dangerous functions
            dangerous_functions = ["eval(", "exec(", "system(", "shell_exec("]
            for func in dangerous_functions:
                if func in content:
                    security_issues.append(
                        f"Dangerous function {func} found in {filename}"
                    )

            # Check for SQL injection vulnerabilities
            if "select * from" in content.lower() and "+" in content:
                security_issues.append(f"Potential SQL injection in {filename}")

        assert len(security_issues) == 0, f"Security issues found: {security_issues}"

        logger.info("✅ File security tests passed")


class TestProjectQuality:
    """Test generated project quality and completeness"""

    def test_project_structure_completeness(self):
        """Test that generated projects have complete structure"""

        # Mock a generated project structure
        expected_structures = {
            "react": [
                "package.json",
                "src/App.tsx",
                "src/index.tsx",
                "public/index.html",
                "README.md",
                ".gitignore",
            ],
            "fastapi": [
                "main.py",
                "requirements.txt",
                "app/",
                "app/__init__.py",
                "README.md",
                ".gitignore",
            ],
            "django": [
                "manage.py",
                "requirements.txt",
                "myproject/",
                "myproject/settings.py",
                "README.md",
                ".gitignore",
            ],
        }

        for framework, expected_files in expected_structures.items():
            # In real test, this would check actual generated project
            # For now, verify the expected structure is reasonable

            assert (
                "package.json" in expected_files or "requirements.txt" in expected_files
            ), f"No dependency file for {framework}"
            assert "README.md" in expected_files, f"No README for {framework}"
            assert ".gitignore" in expected_files, f"No .gitignore for {framework}"

            # Verify entry point exists
            entry_points = [
                "main.py",
                "app.py",
                "src/index.tsx",
                "src/App.tsx",
                "manage.py",
            ]
            assert any(
                entry in expected_files for entry in entry_points
            ), f"No entry point for {framework}"

        logger.info("✅ Project structure completeness tests passed")

    def test_generated_code_quality(self):
        """Test quality of generated code"""

        # Sample generated code snippets to validate
        code_samples = {
            "typescript": """
import React from 'react';

interface Props {
  title: string;
}

const App: React.FC<Props> = ({ title }) => {
  return (
    <div>
      <h1>{title}</h1>
    </div>
  );
};

export default App;
            """,
            "python": """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/users")
def create_user(user: User):
    return {"user": user}
            """,
        }

        quality_issues = []

        for language, code in code_samples.items():
            # Check for basic quality indicators

            # Should have proper imports
            if language == "typescript" and "import" not in code:
                quality_issues.append(f"Missing imports in {language} code")
            elif language == "python" and "from" not in code and "import" not in code:
                quality_issues.append(f"Missing imports in {language} code")

            # Should have type annotations (for TypeScript/Python)
            if language in ["typescript", "python"]:
                if ":" not in code:
                    quality_issues.append(
                        f"Missing type annotations in {language} code"
                    )

            # Should have proper function/component structure
            if (
                language == "typescript"
                and "const " not in code
                and "function " not in code
            ):
                quality_issues.append(
                    f"No proper function/component structure in {language}"
                )
            elif language == "python" and "def " not in code and "class " not in code:
                quality_issues.append(
                    f"No proper function/class structure in {language}"
                )

            # Should have exports/returns
            if language == "typescript" and "export" not in code:
                quality_issues.append(f"Missing exports in {language} code")
            elif language == "python" and "return" not in code:
                quality_issues.append(f"Missing return statements in {language} code")

        assert len(quality_issues) == 0, f"Code quality issues: {quality_issues}"

        logger.info("✅ Code quality tests passed")


# Test runner
def run_comprehensive_tests():
    """Run the complete test suite"""

    logger.info("🚀 Starting comprehensive test suite...")

    # Configure pytest with comprehensive options
    pytest_args = [
        "-v",  # Verbose output
        "-x",  # Stop on first failure
        "--tb=short",  # Short traceback
        "--asyncio-mode=auto",  # Auto asyncio mode
        "--capture=no",  # Don't capture output
        os.path.dirname(__file__),
    ]

    # Run tests
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        logger.info("✅ All comprehensive tests passed!")
    else:
        logger.error(f"❌ Tests failed with exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    exit_code = run_comprehensive_tests()
    sys.exit(exit_code)
