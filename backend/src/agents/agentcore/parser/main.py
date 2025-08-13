"""
Requirement Parser Agent
AgentCore-compatible wrapper
Size: < 6.5KB
"""
import json
from typing import Any, Dict


class ParserAgent:
    """AgentCore wrapper for Parser Agent"""

    def __init__(self):
        self.name = "parser"
        self.version = "1.0.0"
        self.description = "Requirement Parser Agent"
        self._initialized = True

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method"""
        try:
            # Validate input
            validation = self.validate_input(request)
            if not validation["valid"]:
                return {"status": "error", "error": validation["error"]}

            # Process request based on agent type
            result = self._execute_logic(request)

            return {"status": "success", "agent": self.name, "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def validate_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input request"""
        if not request:
            return {"valid": False, "error": "Empty request"}

        if "input" not in request:
            return {"valid": False, "error": "Missing input field"}

        return {"valid": True}

    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self._get_capabilities(),
            "constraints": {"max_memory_kb": 6.5, "max_instantiation_us": 3.0},
        }

    def _execute_logic(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific logic"""
        # Parser processing logic
        input_data = request.get("input", "")
        data_type = request.get("type", "text")

        # Parse requirements
        parsed = self._parse_requirements(input_data, data_type)

        # Build specification
        specification = self._build_specification(parsed)

        # Validate specification
        validation = self._validate_specification(specification)

        return {
            "parsed_requirements": parsed,
            "specification": specification,
            "validation": validation,
            "status": "valid" if validation["is_valid"] else "needs_review",
        }

    def _parse_requirements(self, data: str, data_type: str) -> dict:
        """Parse requirements from input"""
        requirements = {"functional": [], "non_functional": [], "constraints": []}

        # Simple parsing logic
        lines = data.split("\n") if data_type == "text" else [data]
        for line in lines:
            if line.strip():
                if "must" in line.lower():
                    requirements["functional"].append(line.strip())
                elif "should" in line.lower():
                    requirements["non_functional"].append(line.strip())
                else:
                    requirements["constraints"].append(line.strip())

        return requirements

    def _build_specification(self, parsed: dict) -> dict:
        """Build formal specification"""
        return {
            "version": "1.0.0",
            "requirements": parsed,
            "metadata": {"created_at": "2025-08-15", "agent": self.name},
        }

    def _validate_specification(self, spec: dict) -> dict:
        """Validate specification"""
        issues = []

        if not spec.get("requirements"):
            issues.append("No requirements found")

        functional = spec.get("requirements", {}).get("functional", [])
        if len(functional) == 0:
            issues.append("No functional requirements")

        return {"is_valid": len(issues) == 0, "issues": issues}

    def _get_capabilities(self) -> list:
        """Get agent capabilities"""
        return ["requirement_parsing", "specification_building", "validation"]


# AgentCore entry point
def handler(event, context):
    """AWS Lambda handler"""
    agent = ParserAgent()
    return agent.process(event)
