"""
ServiceValidator - Day 31
Validates services built by ServiceBuilder
Size: ~6.5KB (optimized)
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Callable, Dict, List


class ServiceValidator:
    """Validates service specifications and implementations"""

    def __init__(self):
        from .constraint_validator import ConstraintValidator
        from .type_checker import TypeChecker

        self.type_checker = TypeChecker()
        self.constraint_validator = ConstraintValidator()
        self.validation_results = []
        self.custom_rules = {}
        self.cache = {}
        self.cache_hits = 0
        self.stats = {"total_validated": 0, "passed": 0, "failed": 0}

    def validate(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Complete service validation"""
        # Check cache
        service_hash = self._hash_service(service)
        if service_hash in self.cache:
            self.cache_hits += 1
            return self.cache[service_hash]

        result = {
            "valid": True,
            "service_name": service.get("name", "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "warnings": [],
            "errors": [],
        }

        # Structure validation
        result["structure"] = self.validate_structure(service)
        if not result["structure"]["valid"]:
            result["valid"] = False
            result["errors"].extend(result["structure"]["errors"])

        # Agent validation
        if "agents" in service and "constraints" in service:
            result["agents"] = self.validate_agents(service["agents"], service["constraints"])
            if not result["agents"]["valid"]:
                result["valid"] = False

        # Workflow validation
        if "workflow" in service and "agents" in service:
            result["workflow"] = self.validate_workflow(service["workflow"], service["agents"])
            if not result["workflow"]["valid"]:
                result["valid"] = False

        # Type checking
        result["types"] = self.check_types(service)
        if not result["types"]["valid"]:
            result["valid"] = False

        # Constraint checking
        result["constraints"] = self.check_constraints(service)
        if not result["constraints"]["valid"]:
            result["valid"] = False

        # Performance validation
        result["performance"] = self.validate_performance(service)

        # Dependency validation
        if "agents" in service:
            result["dependencies"] = self.validate_dependencies(service["agents"])

        # Add warnings
        self._add_warnings(service, result)

        # Update stats
        self.stats["total_validated"] += 1
        if result["valid"]:
            self.stats["passed"] += 1
        else:
            self.stats["failed"] += 1

        # Cache result
        self.cache[service_hash] = result
        self.validation_results.append(result)

        return result

    def validate_structure(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Validate service structure"""
        result = {"valid": True, "errors": [], "service_name": service.get("name")}

        required = ["name", "agents", "workflow", "constraints"]
        for field in required:
            if field not in service:
                result["valid"] = False
                result["errors"].append(f"Missing required field: {field}")

        if "agents" in service and not isinstance(service["agents"], list):
            result["valid"] = False
            result["errors"].append("agents must be a list")

        if "workflow" in service and not isinstance(service["workflow"], dict):
            result["valid"] = False
            result["errors"].append("workflow must be a dictionary")

        return result

    def validate_agents(self, agents: List[Dict], constraints: Dict) -> Dict[str, Any]:
        """Validate agent specifications"""
        result = {"valid": True, "total_agents": len(agents), "agents": []}

        max_size = constraints.get("max_size_kb", 6.5)
        max_time = constraints.get("max_instantiation_us", 3.0)

        for agent in agents:
            agent_result = {"name": agent.get("name"), "size_valid": True, "speed_valid": True}

            # Check size
            size = agent.get("size_kb", 0)
            if size > max_size:
                agent_result["size_valid"] = False
                agent_result["error"] = f"Size {size}KB exceeds maximum {max_size}KB"
                result["valid"] = False

            # Check instantiation time
            time = agent.get("instantiation_us", 0)
            if time > max_time:
                agent_result["speed_valid"] = False
                agent_result["error"] = f"Time {time}μs exceeds maximum {max_time}μs"
                result["valid"] = False

            result["agents"].append(agent_result)

        return result

    def validate_workflow(self, workflow: Dict, agents: List[Dict]) -> Dict[str, Any]:
        """Validate workflow definition"""
        result = {"valid": True, "steps_count": len(workflow.get("steps", [])), "steps": []}

        agent_names = {a.get("name") for a in agents}

        for step in workflow.get("steps", []):
            step_result = {"valid": True}

            if step.get("agent") not in agent_names:
                step_result["valid"] = False
                step_result["error"] = f"Agent '{step.get('agent')}' not found"
                result["valid"] = False

            result["steps"].append(step_result)

        return result

    def check_types(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Check type correctness"""
        return self.type_checker.check(service)

    def check_constraints(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Check constraint compliance"""
        return self.constraint_validator.validate(service)

    def validate_performance(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance metrics"""
        result = {"valid": True}

        if "agents" in service:
            total_time = sum(a.get("instantiation_us", 0) for a in service["agents"])
            total_memory = sum(a.get("size_kb", 0) for a in service["agents"])

            result["total_instantiation_time"] = total_time
            result["total_memory"] = total_memory

            if total_time >= 3.0:
                result["valid"] = False
                result["error"] = f"Total time {total_time}μs exceeds limit"

        return result

    def validate_dependencies(self, agents: List[Dict]) -> Dict[str, Any]:
        """Validate agent dependencies"""
        result = {"valid": True, "conflicts": []}

        all_deps = []
        for agent in agents:
            all_deps.extend(agent.get("dependencies", []))

        result["total_dependencies"] = len(set(all_deps))

        # Check for version conflicts (simplified)
        seen = {}
        for dep in all_deps:
            if dep in seen and seen[dep] != dep:
                result["conflicts"].append(f"Conflict: {dep}")
                result["valid"] = False
            seen[dep] = dep

        return result

    def validate_batch(self, services: List[Dict]) -> List[Dict]:
        """Validate multiple services"""
        results = []
        for service in services:
            results.append(self.validate(service))
        return results

    def generate_report(self, result: Dict[str, Any]) -> str:
        """Generate validation report"""
        status = "✅ PASSED" if result["valid"] else "❌ FAILED"

        report = f"""
ServiceValidator Report
=======================
Service: {result['service_name']}
Status: {status}
Timestamp: {result['timestamp']}

Structure: {'✅' if result.get('structure', {}).get('valid') else '❌'}
Agents: {'✅' if result.get('agents', {}).get('valid') else '❌'}
Workflow: {'✅' if result.get('workflow', {}).get('valid') else '❌'}
Types: {'✅' if result.get('types', {}).get('valid') else '❌'}
Constraints: {'✅' if result.get('constraints', {}).get('valid') else '❌'}

Warnings: {len(result.get('warnings', []))}
Errors: {len(result.get('errors', []))}
"""
        return report

    def add_rule(self, name: str, rule: Callable) -> None:
        """Add custom validation rule"""
        self.custom_rules[name] = rule

    def apply_custom_rules(self, service: Dict) -> Dict[str, Any]:
        """Apply custom validation rules"""
        result = {"custom_rules": {}}

        for name, rule in self.custom_rules.items():
            try:
                result["custom_rules"][name] = rule(service)
            except Exception as e:
                result["custom_rules"][name] = f"Error: {str(e)}"

        return result

    def export_results(self, result: Dict, filepath: str) -> None:
        """Export validation results to file"""
        with open(filepath, "w") as f:
            json.dump(result, f, indent=2, default=str)

    def get_stats(self) -> Dict[str, int]:
        """Get validation statistics"""
        return self.stats.copy()

    def _hash_service(self, service: Dict) -> str:
        """Generate hash for service specification"""
        service_str = json.dumps(service, sort_keys=True)
        return hashlib.md5(service_str.encode(), usedforsecurity=False).hexdigest()

    def _add_warnings(self, service: Dict, result: Dict) -> None:
        """Add warnings for near-limit values"""
        if "agents" in service:
            for agent in service["agents"]:
                size = agent.get("size_kb", 0)
                if 6.0 <= size < 6.5:
                    result["warnings"].append(
                        f"Agent '{agent.get('name')}' size {size}KB close to limit"
                    )
