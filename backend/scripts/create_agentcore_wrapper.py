#!/usr/bin/env python3
"""
Day 17: AgentCore Wrapper Creator
Creates AgentCore-compatible wrappers for existing agents
"""
import json
from pathlib import Path
from typing import Dict

# Template for AgentCore wrapper
AGENTCORE_TEMPLATE = '''"""
{description}
AgentCore-compatible wrapper
Size: < 6.5KB
"""
import json
from typing import Dict, Any

class {class_name}:
    """AgentCore wrapper for {name}"""

    def __init__(self):
        self.name = "{agent_id}"
        self.version = "1.0.0"
        self.description = "{description}"
        self._initialized = True

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method"""
        try:
            # Validate input
            validation = self.validate_input(request)
            if not validation["valid"]:
                return {{
                    "status": "error",
                    "error": validation["error"]
                }}

            # Process request based on agent type
            result = self._execute_logic(request)

            return {{
                "status": "success",
                "agent": self.name,
                "result": result
            }}
        except Exception as e:
            return {{
                "status": "error",
                "error": str(e)
            }}

    def validate_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input request"""
        if not request:
            return {{"valid": False, "error": "Empty request"}}

        if "input" not in request:
            return {{"valid": False, "error": "Missing input field"}}

        return {{"valid": True}}

    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {{
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self._get_capabilities(),
            "constraints": {{
                "max_memory_kb": 6.5,
                "max_instantiation_us": 3.0
            }}
        }}

    def _execute_logic(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific logic"""
        {agent_logic}

    def _get_capabilities(self) -> list:
        """Get agent capabilities"""
        return {capabilities}

# AgentCore entry point
def handler(event, context):
    """AWS Lambda handler"""
    agent = {class_name}()
    return agent.process(event)
'''

AGENT_CONFIGS = {
    "nl_input": {
        "class_name": "NLInputAgent",
        "name": "NL Input Agent",
        "description": "Natural Language Input Processing Agent",
        "capabilities": ["intent_analysis", "entity_extraction", "requirement_extraction"],
        "logic": '''# NL Input processing logic
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
            "confidence": 0.85
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
        sentences = text.split('.')
        for sentence in sentences:
            if sentence.strip():
                requirements.append({
                    "text": sentence.strip(),
                    "priority": "medium",
                    "type": "functional"
                })
        return requirements''',
    },
    "ui_selection": {
        "class_name": "UISelectionAgent",
        "name": "UI Selection Agent",
        "description": "UI Component Selection Agent",
        "capabilities": ["component_selection", "theme_generation", "layout_optimization"],
        "logic": '''# UI Selection processing logic
        requirements = request.get("requirements", {})
        platform = request.get("platform", "web")

        # Select components
        components = self._select_components(requirements, platform)

        # Generate theme
        theme = self._generate_theme(requirements)

        # Optimize layout
        layout = self._optimize_layout(components, platform)

        return {
            "components": components,
            "theme": theme,
            "layout": layout,
            "framework": "react" if platform == "web" else "react-native"
        }

    def _select_components(self, requirements: dict, platform: str) -> list:
        """Select UI components"""
        components = []
        # Basic component selection logic
        components.append({"type": "header", "props": {"title": "Application"}})
        components.append({"type": "navigation", "props": {"style": "sidebar"}})
        components.append({"type": "content", "props": {"layout": "grid"}})
        components.append({"type": "footer", "props": {"links": ["About", "Contact"]}})
        return components

    def _generate_theme(self, requirements: dict) -> dict:
        """Generate UI theme"""
        return {
            "primaryColor": "#007bff",
            "secondaryColor": "#6c757d",
            "backgroundColor": "#ffffff",
            "textColor": "#333333",
            "fontFamily": "Inter, sans-serif",
            "borderRadius": "8px"
        }

    def _optimize_layout(self, components: list, platform: str) -> dict:
        """Optimize layout for platform"""
        if platform == "mobile":
            return {"type": "stack", "direction": "vertical", "spacing": "medium"}
        else:
            return {"type": "grid", "columns": 12, "gap": "20px"}''',
    },
    "parser": {
        "class_name": "ParserAgent",
        "name": "Parser Agent",
        "description": "Requirement Parser Agent",
        "capabilities": ["requirement_parsing", "specification_building", "validation"],
        "logic": '''# Parser processing logic
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
            "status": "valid" if validation["is_valid"] else "needs_review"
        }

    def _parse_requirements(self, data: str, data_type: str) -> dict:
        """Parse requirements from input"""
        requirements = {
            "functional": [],
            "non_functional": [],
            "constraints": []
        }

        # Simple parsing logic
        lines = data.split('\\n') if data_type == "text" else [data]
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
            "metadata": {
                "created_at": "2025-08-15",
                "agent": self.name
            }
        }

    def _validate_specification(self, spec: dict) -> dict:
        """Validate specification"""
        issues = []

        if not spec.get("requirements"):
            issues.append("No requirements found")

        functional = spec.get("requirements", {}).get("functional", [])
        if len(functional) == 0:
            issues.append("No functional requirements")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }''',
    },
}


def create_agentcore_wrapper(agent_id: str, config: Dict) -> str:
    """Create AgentCore wrapper for an agent"""
    return AGENTCORE_TEMPLATE.format(
        agent_id=agent_id,
        class_name=config["class_name"],
        name=config["name"],
        description=config["description"],
        capabilities=json.dumps(config["capabilities"]),
        agent_logic=config["logic"],
    )


def main():
    """Create AgentCore wrappers for all agents"""
    print("🧬 Creating AgentCore Wrappers")
    print("=" * 50)

    base_dir = Path("src/agents/agentcore")
    base_dir.mkdir(parents=True, exist_ok=True)

    for agent_id, config in AGENT_CONFIGS.items():
        print(f"📦 Creating wrapper for {config['name']}...")

        # Create agent directory
        agent_dir = base_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Generate wrapper code
        wrapper_code = create_agentcore_wrapper(agent_id, config)

        # Save wrapper
        wrapper_file = agent_dir / "main.py"
        wrapper_file.write_text(wrapper_code)

        # Check size
        size_kb = len(wrapper_code.encode()) / 1024
        print(f"  ✅ Created: {wrapper_file} ({size_kb:.2f} KB)")

        # Create metadata
        metadata = {
            "agent_id": agent_id,
            "name": config["name"],
            "description": config["description"],
            "version": "1.0.0",
            "size_kb": size_kb,
            "capabilities": config["capabilities"],
            "created_at": "2025-08-15T00:00:00Z",
        }

        metadata_file = agent_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))
        print(f"  ✅ Metadata: {metadata_file}")

    print("\n✅ All AgentCore wrappers created successfully!")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
