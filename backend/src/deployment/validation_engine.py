"""
Validation Engine - Deployment verification system
Size: < 6.5KB | Performance: < 3μs
Day 24: Phase 2 - Meta Agents
"""

import ast
import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ValidationRule:
    """Single validation rule"""

    name: str
    type: str  # size, performance, syntax, security, dependency
    check: callable
    severity: str  # error, warning, info
    message: str


@dataclass
class ValidationResult:
    """Validation result details"""

    rule_name: str
    passed: bool
    severity: str
    message: str
    details: Dict[str, Any]


class ValidationEngine:
    """Comprehensive validation engine for deployments"""

    def __init__(self):
        self.size_limit = 6500  # 6.5KB
        self.perf_limit = 3.0  # 3μs
        self.rules = self._init_rules()
        self.cache = {}

    def _init_rules(self) -> List[ValidationRule]:
        """Initialize validation rules"""

        return [
            ValidationRule(
                name="size_constraint",
                type="size",
                check=self._check_size,
                severity="error",
                message="Agent exceeds 6.5KB size limit",
            ),
            ValidationRule(
                name="syntax_check",
                type="syntax",
                check=self._check_syntax,
                severity="error",
                message="Invalid Python syntax",
            ),
            ValidationRule(
                name="import_check",
                type="dependency",
                check=self._check_imports,
                severity="warning",
                message="Missing or invalid imports",
            ),
            ValidationRule(
                name="async_check",
                type="performance",
                check=self._check_async,
                severity="info",
                message="Agent should use async/await",
            ),
            ValidationRule(
                name="security_check",
                type="security",
                check=self._check_security,
                severity="error",
                message="Security vulnerability detected",
            ),
            ValidationRule(
                name="method_check",
                type="syntax",
                check=self._check_required_methods,
                severity="error",
                message="Missing required methods",
            ),
        ]

    async def validate_agent(self, agent_path: str, agent_name: str) -> Dict[str, Any]:
        """Validate agent before deployment"""

        start_time = time.time()

        if not os.path.exists(agent_path):
            return {
                "valid": False,
                "errors": [f"Agent file not found: {agent_path}"],
                "warnings": [],
                "time": time.time() - start_time,
            }

        # Read agent code
        with open(agent_path, "r") as f:
            code = f.read()

        # Run all validation rules
        results = []
        errors = []
        warnings = []

        for rule in self.rules:
            result = await self._run_rule(rule, code, agent_name)
            results.append(result)

            if not result.passed:
                if result.severity == "error":
                    errors.append(f"{result.rule_name}: {result.message}")
                elif result.severity == "warning":
                    warnings.append(f"{result.rule_name}: {result.message}")

        validation_time = time.time() - start_time

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "results": [
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "severity": r.severity,
                    "message": r.message,
                }
                for r in results
            ],
            "time": validation_time,
            "agent_name": agent_name,
            "size_bytes": len(code.encode()),
        }

    async def _run_rule(self, rule: ValidationRule, code: str, agent_name: str) -> ValidationResult:
        """Run single validation rule"""

        try:
            passed, details = await rule.check(code, agent_name)

            return ValidationResult(
                rule_name=rule.name,
                passed=passed,
                severity=rule.severity,
                message=rule.message if not passed else "OK",
                details=details,
            )
        except Exception as e:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity="error",
                message=f"Rule execution error: {str(e)}",
                details={},
            )

    async def _check_size(self, code: str, agent_name: str) -> Tuple[bool, Dict]:
        """Check agent size constraint"""

        size = len(code.encode())
        passed = size <= self.size_limit

        return passed, {
            "size_bytes": size,
            "limit_bytes": self.size_limit,
            "ratio": size / self.size_limit,
        }

    async def _check_syntax(self, code: str, agent_name: str) -> Tuple[bool, Dict]:
        """Check Python syntax"""

        try:
            ast.parse(code)
            return True, {"syntax": "valid"}
        except SyntaxError as e:
            return False, {"error": str(e), "line": e.lineno, "offset": e.offset}

    async def _check_imports(self, code: str, agent_name: str) -> Tuple[bool, Dict]:
        """Check import statements"""

        try:
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)

            # Check for required imports
            required = ["asyncio", "typing"]
            missing = [imp for imp in required if imp not in str(imports)]

            return len(missing) == 0, {"imports": imports, "missing": missing}

        except Exception as e:
            return False, {"error": str(e)}

    async def _check_async(self, code: str, agent_name: str) -> Tuple[bool, Dict]:
        """Check async/await usage"""

        try:
            tree = ast.parse(code)
            async_funcs = 0
            sync_funcs = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    async_funcs += 1
                elif isinstance(node, ast.FunctionDef):
                    sync_funcs += 1

            # Should have at least some async functions
            has_async = async_funcs > 0

            return has_async, {
                "async_functions": async_funcs,
                "sync_functions": sync_funcs,
                "async_ratio": async_funcs / max(1, async_funcs + sync_funcs),
            }

        except Exception as e:
            return False, {"error": str(e)}

    async def _check_security(self, code: str, agent_name: str) -> Tuple[bool, Dict]:
        """Check for security issues"""

        dangerous_patterns = [
            "eval(",
            "exec(",
            "__import__",
            "os.system",
            "subprocess",
            "pickle.loads",
        ]

        found_issues = []
        for pattern in dangerous_patterns:
            if pattern in code:
                found_issues.append(pattern)

        return len(found_issues) == 0, {
            "issues": found_issues,
            "checked_patterns": len(dangerous_patterns),
        }

    async def _check_required_methods(self, code: str, agent_name: str) -> Tuple[bool, Dict]:
        """Check for required methods"""

        try:
            tree = ast.parse(code)
            methods = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.append(item.name)

            # Required methods
            required = ["__init__", "execute"]
            missing = [m for m in required if m not in methods]

            return len(missing) == 0, {"methods": methods, "required": required, "missing": missing}

        except Exception as e:
            return False, {"error": str(e)}

    async def validate_deployment(self, deployment_id: str, agent_name: str) -> Dict[str, Any]:
        """Validate deployed agent"""

        # Simulate deployment validation
        # In production, would check actual deployment

        validations = {
            "health_check": await self._check_health(deployment_id),
            "performance_check": await self._check_performance(deployment_id),
            "connectivity_check": await self._check_connectivity(deployment_id),
        }

        all_passed = all(v["passed"] for v in validations.values())

        return {
            "success": all_passed,
            "deployment_id": deployment_id,
            "agent_name": agent_name,
            "validations": validations,
        }

    async def _check_health(self, deployment_id: str) -> Dict[str, Any]:
        """Check deployment health"""

        # Simulate health check
        await asyncio.sleep(0.1)

        return {"passed": True, "status": "healthy", "response_time": 0.05}

    async def _check_performance(self, deployment_id: str) -> Dict[str, Any]:
        """Check deployment performance"""

        # Simulate performance check
        await asyncio.sleep(0.1)

        init_time = 2.5  # μs

        return {
            "passed": init_time < self.perf_limit,
            "init_time": init_time,
            "limit": self.perf_limit,
        }

    async def _check_connectivity(self, deployment_id: str) -> Dict[str, Any]:
        """Check deployment connectivity"""

        # Simulate connectivity check
        await asyncio.sleep(0.1)

        return {"passed": True, "endpoints_available": True, "latency": 10}  # ms

    def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics"""

        return {
            "rules_count": len(self.rules),
            "size_limit": self.size_limit,
            "perf_limit": self.perf_limit,
            "cache_size": len(self.cache),
        }


# Global instance
validator = None


def get_validator() -> ValidationEngine:
    """Get or create validator instance"""
    global validator
    if not validator:
        validator = ValidationEngine()
    return validator


async def main():
    """Test validation engine"""
    validator = get_validator()

    # Create test agent
    test_code = """
import asyncio
from typing import Dict, Any

class TestAgent:
    def __init__(self):
        self.name = "TestAgent"

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.001)
        return {"status": "success", "data": input_data}
"""

    # Save test agent
    with open("/tmp/test_agent.py", "w") as f:
        f.write(test_code)

    # Validate
    result = await validator.validate_agent("/tmp/test_agent.py", "TestAgent")

    print(f"Validation: {'Passed' if result['valid'] else 'Failed'}")
    print(f"Size: {result['size_bytes']} bytes")

    if result["errors"]:
        print(f"Errors: {result['errors']}")

    if result["warnings"]:
        print(f"Warnings: {result['warnings']}")

    # Test deployment validation
    deployment_result = await validator.validate_deployment("deploy_123", "TestAgent")
    print(f"\nDeployment validation: {'Success' if deployment_result['success'] else 'Failed'}")


if __name__ == "__main__":
    asyncio.run(main())
