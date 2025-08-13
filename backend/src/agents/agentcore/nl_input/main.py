"""
Natural Language Input Processing Agent
AgentCore-compatible wrapper
Size: < 6.5KB
"""
import json
from typing import Any, Dict


class NLInputAgent:
    """AgentCore wrapper for NL Input Agent"""

    def __init__(self):
        self.name = "nl_input"
        self.version = "1.0.0"
        self.description = "Natural Language Input Processing Agent"
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
        # NL Input processing logic
        input_text = request.get("input", "")

        # Analyze intent
        intent = self._analyze_intent(input_text)

        # Extract entities
        entities = self._extract_entities(input_text)

        # Extract requirements
        requirements = self._extract_requirements(input_text)

        return {
            "intent": intent,
            "entities": entities,
            "requirements": requirements,
            "confidence": 0.85,
        }

    def _analyze_intent(self, text: str) -> str:
        """Analyze user intent"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["create", "build", "make", "develop"]):
            return "create_application"
        elif any(word in text_lower for word in ["update", "modify", "change"]):
            return "modify_application"
        elif any(word in text_lower for word in ["fix", "debug", "repair"]):
            return "fix_issue"
        else:
            return "general_query"

    def _extract_entities(self, text: str) -> list:
        """Extract entities from text"""
        entities = []
        # Simple entity extraction
        if "web" in text.lower() or "website" in text.lower():
            entities.append({"type": "platform", "value": "web"})
        if "mobile" in text.lower() or "app" in text.lower():
            entities.append({"type": "platform", "value": "mobile"})
        if "api" in text.lower():
            entities.append({"type": "component", "value": "api"})
        if "database" in text.lower() or "db" in text.lower():
            entities.append({"type": "component", "value": "database"})
        return entities

    def _extract_requirements(self, text: str) -> list:
        """Extract requirements from text"""
        requirements = []
        sentences = text.split(".")
        for sentence in sentences:
            if sentence.strip():
                requirements.append(
                    {"text": sentence.strip(), "priority": "medium", "type": "functional"}
                )
        return requirements

    def _get_capabilities(self) -> list:
        """Get agent capabilities"""
        return ["intent_analysis", "entity_extraction", "requirement_extraction"]


# AgentCore entry point
def handler(event, context):
    """AWS Lambda handler"""
    agent = NLInputAgent()
    return agent.process(event)
