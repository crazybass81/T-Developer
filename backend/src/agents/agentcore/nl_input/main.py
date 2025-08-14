"""
Natural Language Input Processing Agent
AgentCore-compatible wrapper
Size: < 6.5KB
"""
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
        """Analyze user intent using keyword matching and patterns"""
        text_lower = text.lower()

        # Intent patterns
        intents = {
            "create": ["create", "build", "make", "develop"],
            "modify": ["update", "modify", "change", "edit"],
            "fix": ["fix", "debug", "repair", "solve"],
            "deploy": ["deploy", "release", "publish"],
            "analyze": ["analyze", "review", "audit"],
            "test": ["test", "validate", "verify"],
        }

        # Score each intent
        scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[intent] = score

        # Return highest scoring intent
        if scores:
            return max(scores, key=scores.get)
        return "general_query"

    def _extract_entities(self, text: str) -> list:
        """Extract entities using pattern matching"""
        entities = []
        text_lower = text.lower()

        # Entity patterns (compact)
        patterns = {
            "platform": {
                "web": ["web", "website"],
                "mobile": ["mobile", "app", "ios", "android"],
                "cloud": ["cloud", "aws", "azure"],
            },
            "tech": {
                "python": ["python", "django", "flask"],
                "js": ["javascript", "js", "react", "node"],
                "db": ["database", "db", "sql", "mongo"],
                "api": ["api", "rest", "graphql"],
            },
        }

        # Extract entities by pattern matching
        for entity_type, values in patterns.items():
            for entity_name, keywords in values.items():
                if any(kw in text_lower for kw in keywords):
                    entities.append({"type": entity_type, "value": entity_name})

        return entities

    def _extract_requirements(self, text: str) -> list:
        """Extract and categorize requirements"""
        requirements = []

        # Split into sentences (simple approach)
        sentences = [
            s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()
        ]

        # Keywords (compact)
        hi_pri = ["must", "critical", "urgent"]
        lo_pri = ["optional", "maybe"]
        perf = ["fast", "performance", "speed"]
        sec = ["secure", "encrypt", "auth"]
        ui = ["ui", "ux", "design"]

        for sentence in sentences:
            sent_lower = sentence.lower()

            # Determine priority
            if any(kw in sent_lower for kw in hi_pri):
                p = "high"
            elif any(kw in sent_lower for kw in lo_pri):
                p = "low"
            else:
                p = "medium"

            # Determine type
            if any(kw in sent_lower for kw in perf):
                t = "perf"
            elif any(kw in sent_lower for kw in sec):
                t = "sec"
            elif any(kw in sent_lower for kw in ui):
                t = "ui"
            else:
                t = "func"

            requirements.append({"text": sentence, "priority": p, "type": t})

        return requirements

    def _get_capabilities(self) -> list:
        """Get agent capabilities"""
        return ["intent_analysis", "entity_extraction", "requirement_extraction"]


# AgentCore entry point
def handler(event, context):
    """AWS Lambda handler"""
    agent = NLInputAgent()
    return agent.process(event)
