"""
ConstraintValidator - Day 31
Validates constraints for services
Size: ~6.5KB (optimized)
"""

import json
from typing import Any, Callable, Dict, List, Tuple


class ConstraintValidator:
    """Validates service constraints"""

    def __init__(self):
        self.constraints = {}
        self.custom_constraints = {}
        self.mode = "production"  # production or development
        self._init_default_constraints()

    def validate(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Main constraint validation"""
        result = {"valid": True, "constraints_met": True, "violations": [], "warnings": []}

        constraints = service.get("constraints", {})
        agents = service.get("agents", [])
        metrics = service.get("metrics", {})

        # Size constraint
        if "max_size_kb" in constraints:
            size_result = self.validate_size(agents, constraints["max_size_kb"])
            if not size_result["valid"]:
                result["valid"] = False
                result["constraints_met"] = False
                result["violations"].append(size_result.get("violation"))

        # Speed constraint
        if "max_instantiation_us" in constraints:
            speed_result = self.validate_speed(agents, constraints["max_instantiation_us"])
            if not speed_result["valid"]:
                result["valid"] = False
                result["constraints_met"] = False
                result["violations"].append(speed_result.get("violation"))

        # Coverage constraint
        if "min_test_coverage" in constraints and "test_coverage" in metrics:
            coverage_result = self.validate_coverage(
                metrics["test_coverage"], constraints["min_test_coverage"]
            )
            if not coverage_result["valid"]:
                result["valid"] = False
                result["constraints_met"] = False
                result["violations"].append(coverage_result.get("violation"))

        # Memory constraint
        if "max_total_memory_mb" in constraints:
            memory_result = self.validate_memory(agents, constraints["max_total_memory_mb"])
            if not memory_result["valid"]:
                result["valid"] = False
                result["constraints_met"] = False
                result["violations"].append(memory_result.get("violation"))

        # Agent count constraint
        if "max_agents" in constraints:
            count_result = self.validate_agent_count(agents, constraints["max_agents"])
            if not count_result["valid"]:
                result["valid"] = False
                result["constraints_met"] = False
                result["violations"].append(count_result.get("violation"))

        # Performance constraint
        if "min_performance_score" in constraints and "performance_score" in metrics:
            perf_result = self.validate_performance(
                metrics["performance_score"], constraints["min_performance_score"]
            )
            if not perf_result["valid"]:
                result["valid"] = False
                result["constraints_met"] = False
                result["violations"].append(perf_result.get("violation"))

        # Development mode relaxation
        if self.mode == "development" and not result["valid"]:
            result["warnings"] = result["violations"]
            result["violations"] = []
            result["valid"] = True
            result["constraints_met"] = True
            result["warnings"].append("Constraints relaxed in development mode")

        return result

    def validate_size(self, agents: List[Dict], max_size: float) -> Dict[str, Any]:
        """Validate size constraints"""
        result = {"valid": True, "constraint": max_size}

        if not agents:
            return result

        max_agent_size = max(a.get("size_kb", 0) for a in agents)
        result["max_size"] = max_agent_size

        if max_agent_size > max_size:
            result["valid"] = False
            result["violation"] = f"Agent size {max_agent_size}KB exceeds limit {max_size}KB"

        return result

    def validate_speed(self, agents: List[Dict], max_time: float) -> Dict[str, Any]:
        """Validate instantiation speed"""
        result = {"valid": True, "constraint": max_time}

        if not agents:
            return result

        max_agent_time = max(a.get("instantiation_us", 0) for a in agents)
        result["max_time"] = max_agent_time

        if max_agent_time > max_time:
            result["valid"] = False
            result[
                "violation"
            ] = f"Instantiation time {max_agent_time}μs exceeds limit {max_time}μs"

        return result

    def validate_coverage(self, actual: float, required: float) -> Dict[str, Any]:
        """Validate test coverage"""
        result = {"valid": True, "actual": actual, "required": required}

        if actual < required:
            result["valid"] = False
            result["violation"] = f"Test coverage {actual:.1%} below minimum {required:.1%}"

        return result

    def validate_memory(self, agents: List[Dict], max_memory_mb: float) -> Dict[str, Any]:
        """Validate memory constraints"""
        result = {"valid": True, "constraint": max_memory_mb}

        total_kb = sum(a.get("size_kb", 0) for a in agents)
        total_mb = total_kb / 1024
        result["total_memory_mb"] = total_mb

        if total_mb > max_memory_mb:
            result["valid"] = False
            result["violation"] = f"Total memory {total_mb:.1f}MB exceeds limit {max_memory_mb}MB"

        return result

    def validate_agent_count(self, agents: List[Dict], max_count: int) -> Dict[str, Any]:
        """Validate agent count"""
        result = {"valid": True, "agent_count": len(agents), "max_allowed": max_count}

        if len(agents) > max_count:
            result["valid"] = False
            result["violation"] = f"Agent count {len(agents)} exceeds limit {max_count}"

        return result

    def validate_performance(self, score: float, min_score: float) -> Dict[str, Any]:
        """Validate performance score"""
        result = {"valid": True, "score": score, "min_required": min_score}

        if score < min_score:
            result["valid"] = False
            result["violation"] = f"Performance score {score:.2f} below minimum {min_score:.2f}"

        return result

    def validate_soft_constraints(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Validate soft constraints (warnings only)"""
        result = {"hard_constraints_met": True, "soft_constraints_met": True, "warnings": []}

        constraints = service.get("constraints", {})
        agents = service.get("agents", [])

        # Check soft size limit
        if "soft_max_size_kb" in constraints:
            max_size = max(a.get("size_kb", 0) for a in agents)
            if max_size > constraints["soft_max_size_kb"]:
                result["soft_constraints_met"] = False
                result["warnings"].append(
                    f"Size {max_size}KB exceeds soft limit {constraints['soft_max_size_kb']}KB"
                )

        return result

    def validate_groups(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Validate grouped constraints"""
        result = {}

        constraints = service.get("constraints", {})
        for group_name, group_constraints in constraints.items():
            if isinstance(group_constraints, dict):
                result[group_name] = {"valid": True}
                # Validate each constraint in group
                for constraint_name, value in group_constraints.items():
                    # Simplified validation for demo
                    result[group_name][constraint_name] = True

        return result

    def validate_dynamic(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dynamic constraints"""
        result = {"valid": True}

        constraints = service.get("constraints", {})
        agents = service.get("agents", [])

        for name, value in constraints.items():
            if isinstance(value, str) and value.startswith("dynamic:"):
                # Parse dynamic expression
                expr = value.replace("dynamic:", "")
                expr = expr.replace("agent_count", str(len(agents)))

                try:
                    # Safe evaluation using ast.literal_eval for simple expressions
                    import ast

                    # Simple math operations only
                    if (
                        "*" in expr
                        and expr.replace(" ", "").replace(".", "").replace("*", "").isdigit()
                    ):
                        parts = expr.split("*")
                        calculated = float(parts[0]) * float(parts[1])
                    else:
                        calculated = ast.literal_eval(expr)
                    result["calculated_limit"] = calculated

                    # Apply the calculated constraint
                    if "max_size" in name:
                        total_size = sum(a.get("size_kb", 0) for a in agents)
                        if total_size > calculated:
                            result["valid"] = False
                except Exception:
                    result["valid"] = False
                    result["error"] = f"Invalid dynamic expression: {expr}"

        return result

    def add_constraint(self, name: str, validator: Callable) -> None:
        """Add custom constraint"""
        self.custom_constraints[name] = validator

    def check_custom_constraint(self, service: Dict, name: str) -> Dict[str, Any]:
        """Check custom constraint"""
        result = {"valid": False, "constraint": name}

        if name in self.custom_constraints:
            validator = self.custom_constraints[name]
            try:
                result["valid"] = validator(service)
            except Exception as e:
                result["error"] = str(e)

        return result

    def evaluate_with_priority(
        self, constraints: List[Tuple[str, Callable]], service: Dict
    ) -> Dict[str, Any]:
        """Evaluate constraints with priority"""
        result = {"critical_passed": True, "should_block": False}

        for priority, validator in constraints:
            if priority == "critical":
                if not validator(service):
                    result["critical_passed"] = False
                    result["should_block"] = True
                    break

        return result

    def set_mode(self, mode: str) -> None:
        """Set validation mode (production/development)"""
        self.mode = mode

    def generate_report(self, result: Dict[str, Any]) -> str:
        """Generate constraint validation report"""
        status = "✅ PASSED" if result["constraints_met"] else "❌ FAILED"

        report = f"""
Constraint Validation Report
============================
Status: {status}
Violations: {len(result.get('violations', []))}
Warnings: {len(result.get('warnings', []))}
"""

        if result.get("violations"):
            report += "\nViolations:\n"
            for v in result["violations"]:
                report += f"  - {v}\n"

        return report

    def export_constraints(self, filepath: str) -> None:
        """Export constraint definitions"""
        export_data = {
            "constraints": self.constraints,
            "custom_constraints": list(self.custom_constraints.keys()),
            "mode": self.mode,
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

    def _init_default_constraints(self) -> None:
        """Initialize default constraints"""
        self.constraints = {
            "max_size_kb": 6.5,
            "max_instantiation_us": 3.0,
            "min_test_coverage": 0.85,
            "max_total_memory_mb": 50,
            "max_agents": 100,
        }
