#!/usr/bin/env python3
"""Unified test runner for T-Developer project."""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestRunner:
    """Test runner for different test types."""

    def __init__(self, verbose: bool = False):
        """Initialize test runner."""
        self.verbose = verbose
        self.backend_dir = PROJECT_ROOT / "backend"
        self.frontend_dir = PROJECT_ROOT / "frontend"

    def run_backend_unit_tests(self) -> bool:
        """Run backend unit tests."""
        print("\n🧪 Running Backend Unit Tests...")
        cmd = [
            "python", "-m", "pytest",
            "backend/tests",
            "-v" if self.verbose else "",
            "--cov=backend/packages",
            "--cov-report=term-missing",
            "-x",  # Stop on first failure
            "--ignore=backend/tests/integration",
            "--ignore=backend/tests/e2e"
        ]
        return self._run_command(cmd)

    def run_backend_integration_tests(self) -> bool:
        """Run backend integration tests."""
        print("\n🔗 Running Backend Integration Tests...")
        cmd = [
            "python", "-m", "pytest",
            "backend/tests/integration",
            "-v" if self.verbose else "",
            "-x"
        ]
        return self._run_command(cmd)

    def run_backend_e2e_tests(self) -> bool:
        """Run backend E2E tests."""
        print("\n🌐 Running Backend E2E Tests...")
        
        # Check if services are running
        if not self._check_services():
            print("❌ Services not running. Start them with: npm run dev")
            return False
        
        cmd = [
            "python", "-m", "pytest",
            "backend/tests/e2e",
            "-v" if self.verbose else "",
            "-x"
        ]
        return self._run_command(cmd)

    def run_frontend_tests(self) -> bool:
        """Run frontend tests."""
        print("\n⚛️ Running Frontend Tests...")
        os.chdir(self.frontend_dir)
        cmd = ["npm", "run", "test:ci"]
        result = self._run_command(cmd)
        os.chdir(PROJECT_ROOT)
        return result

    def run_lambda_tests(self) -> bool:
        """Run Lambda handler tests."""
        print("\n⚡ Running Lambda Handler Tests...")
        cmd = [
            "python", "-m", "pytest",
            "backend/tests/test_evolution_handler.py",
            "backend/tests/test_agent_handler.py",
            "backend/tests/test_metrics_handler.py",
            "-v" if self.verbose else "",
            "-x"
        ]
        return self._run_command(cmd)

    def run_security_tests(self) -> bool:
        """Run security tests."""
        print("\n🔒 Running Security Tests...")
        
        # Run bandit for security issues
        print("Running Bandit security scan...")
        bandit_cmd = [
            "bandit", "-r",
            "backend/packages",
            "lambda_handlers",
            "-ll",  # Only show medium and high severity
            "-f", "json",
            "-o", "security_report.json"
        ]
        self._run_command(bandit_cmd)
        
        # Run safety for dependency vulnerabilities
        print("Checking dependency vulnerabilities...")
        safety_cmd = ["safety", "check", "--json"]
        return self._run_command(safety_cmd)

    def run_linting(self) -> bool:
        """Run linting checks."""
        print("\n✨ Running Linting Checks...")
        
        # Python linting
        print("Python linting with ruff...")
        ruff_cmd = ["ruff", "check", "backend", "lambda_handlers", "scripts"]
        python_lint = self._run_command(ruff_cmd)
        
        # TypeScript linting
        print("TypeScript linting...")
        os.chdir(self.frontend_dir)
        ts_lint_cmd = ["npm", "run", "lint"]
        ts_lint = self._run_command(ts_lint_cmd)
        os.chdir(PROJECT_ROOT)
        
        return python_lint and ts_lint

    def run_type_checking(self) -> bool:
        """Run type checking."""
        print("\n📝 Running Type Checks...")
        
        # Python type checking
        print("Python type checking with mypy...")
        mypy_cmd = [
            "mypy",
            "backend/packages",
            "lambda_handlers",
            "--ignore-missing-imports"
        ]
        python_types = self._run_command(mypy_cmd)
        
        # TypeScript type checking
        print("TypeScript type checking...")
        os.chdir(self.frontend_dir)
        ts_types_cmd = ["npm", "run", "type-check"]
        ts_types = self._run_command(ts_types_cmd)
        os.chdir(PROJECT_ROOT)
        
        return python_types and ts_types

    def run_all_tests(self) -> bool:
        """Run all tests."""
        results = {
            "Unit Tests": self.run_backend_unit_tests(),
            "Integration Tests": self.run_backend_integration_tests(),
            "Frontend Tests": self.run_frontend_tests(),
            "Lambda Tests": self.run_lambda_tests(),
            "Linting": self.run_linting(),
            "Type Checking": self.run_type_checking(),
        }
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        for test_type, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_type:.<30} {status}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed. Please check the output above.")
        
        return all_passed

    def _run_command(self, cmd: List[str]) -> bool:
        """Run a command and return success status."""
        # Filter out empty strings
        cmd = [c for c in cmd if c]
        
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                cwd=PROJECT_ROOT
            )
            return result.returncode == 0
        except FileNotFoundError:
            print(f"❌ Command not found: {cmd[0]}")
            return False
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return False

    def _check_services(self) -> bool:
        """Check if required services are running."""
        import requests
        
        services = {
            "Frontend": "http://localhost:3000",
            "Backend API": "http://localhost:8000/health"
        }
        
        all_running = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} is running")
                else:
                    print(f"❌ {name} returned status {response.status_code}")
                    all_running = False
            except requests.exceptions.RequestException:
                print(f"❌ {name} is not responding at {url}")
                all_running = False
        
        return all_running


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="T-Developer Test Runner")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=[
            "all", "unit", "integration", "e2e", "frontend",
            "lambda", "security", "lint", "type", "quick"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    
    # Map test types to runner methods
    test_map = {
        "all": runner.run_all_tests,
        "unit": runner.run_backend_unit_tests,
        "integration": runner.run_backend_integration_tests,
        "e2e": runner.run_backend_e2e_tests,
        "frontend": runner.run_frontend_tests,
        "lambda": runner.run_lambda_tests,
        "security": runner.run_security_tests,
        "lint": runner.run_linting,
        "type": runner.run_type_checking,
        "quick": lambda: (
            runner.run_backend_unit_tests() and
            runner.run_linting()
        )
    }
    
    # Run selected tests
    success = test_map[args.test_type]()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()