"""
Unified Parser Agent
Parses and structures natural language requirements into actionable specifications
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from src.agents.unified.base import UnifiedBaseAgent, AgentConfig, AgentResult
from src.agents.unified.data_wrapper import (
    AgentInput,
    AgentContext,
    wrap_input,
    unwrap_result,
)
from src.agents.unified.input_handler import unwrap_input

# from ...phase2.agents.parser import ParserAgent as Phase2Parser, ParserResult  # Commented out - module not available


# Define ParserResult locally since phase2 is not available
class ParserResult:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.success = data.get("success", False)
        self.parsed_requirements = data.get("parsed_requirements", {})

    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, "logger"):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")

    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, "logger"):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, "logger"):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")


class EnhancedParserResult(ParserResult):
    """Enhanced result from Parser Agent"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.entities = data.get("entities", {})
        self.dependencies = data.get("dependencies", [])
        self.constraints = data.get("constraints", {})
        self.specifications = data.get("specifications", {})
        self.data_model = data.get("data_model", {})
        self.api_definitions = data.get("api_definitions", [])
        self.business_rules = data.get("business_rules", [])
        self.user_stories = data.get("user_stories", [])
        self.acceptance_criteria = data.get("acceptance_criteria", [])
        self.technical_requirements = data.get("technical_requirements", {})


class UnifiedParserAgent(UnifiedBaseAgent):
    """
    Unified Parser Agent
    Combines Phase 2 structured parsing with advanced NLP capabilities
    """

    def __init__(self, config: Optional[AgentConfig] = None, **kwargs):
        if not config:
            config = AgentConfig(
                name="parser",
                version="3.0.0",
                timeout=25,
                enable_monitoring=True,
                enable_caching=True,
            )

        super().__init__(config)
        # Phase2Parser not available - commented out
        # self.phase2_parser = Phase2Parser()

        # Initialize parsing modules (will be created separately)
        self._init_modules()

        # Parsing patterns
        self.patterns = {
            "entity": r"\b(?:user|admin|customer|product|order|payment|account|profile|dashboard|report)\b",
            "action": r"\b(?:create|read|update|delete|list|search|filter|sort|export|import|upload|download)\b",
            "requirement": r"\b(?:must|should|shall|need|require|want)\b",
            "constraint": r"\b(?:maximum|minimum|limit|within|before|after|between|less than|greater than)\b",
            "api_endpoint": r"(?:GET|POST|PUT|DELETE|PATCH)\s+\/[\w\/\{\}]+",
            "data_type": r"\b(?:string|number|integer|boolean|array|object|date|email|url|uuid)\b",
        }

        # Entity extraction rules
        self.entity_rules = {
            "user_management": [
                "user",
                "authentication",
                "authorization",
                "role",
                "permission",
            ],
            "data_management": ["database", "storage", "backup", "migration", "schema"],
            "ui_components": [
                "form",
                "table",
                "chart",
                "modal",
                "navigation",
                "layout",
            ],
            "business_logic": [
                "workflow",
                "process",
                "rule",
                "validation",
                "calculation",
            ],
            "integration": ["api", "webhook", "service", "endpoint", "external"],
        }

    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, "logger"):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")

    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, "logger"):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, "logger"):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")

    async def _custom_initialize(self):
        """Custom initialization for Parser agent"""
        pass

    async def _process_internal(
        self, input_data: Dict[str, Any], context: Any
    ) -> Dict[str, Any]:
        """Internal processing method"""
        # Call the main process method
        result = await self.process(input_data)
        return result.data if hasattr(result, "data") else result

    def _init_modules(self):
        """Initialize parsing modules"""
        try:
            from src.agents.unified.parser.modules import (
                NLPProcessor,
                EntityExtractor,
                RequirementAnalyzer,
                DataModelBuilder,
                APIParser,
                ConstraintAnalyzer,
                DependencyResolver,
                UserStoryGenerator,
                ValidationEngine,
                SpecificationBuilder,
                BusinessRuleExtractor,
                TechnicalAnalyzer,
            )

            self.nlp_processor = NLPProcessor()
            self.entity_extractor = EntityExtractor()
            self.requirement_analyzer = RequirementAnalyzer()
            self.data_model_builder = DataModelBuilder()
            self.api_parser = APIParser()
            self.constraint_analyzer = ConstraintAnalyzer()
            self.dependency_resolver = DependencyResolver()
            self.user_story_generator = UserStoryGenerator()
            self.validation_engine = ValidationEngine()
            self.specification_builder = SpecificationBuilder()
            self.business_rule_extractor = BusinessRuleExtractor()
            self.technical_analyzer = TechnicalAnalyzer()
        except ImportError:
            # Modules will be created separately
            self.nlp_processor = None
            self.entity_extractor = None
            self.requirement_analyzer = None
            self.data_model_builder = None
            self.api_parser = None
            self.constraint_analyzer = None
            self.dependency_resolver = None
            self.user_story_generator = None
            self.validation_engine = None
            self.specification_builder = None
            self.business_rule_extractor = None
            self.technical_analyzer = None

    async def process(self, input_data: Any) -> EnhancedParserResult:
        """
        Process input through the Parser agent

        Args:
            input_data: Input containing natural language requirements

        Returns:
            EnhancedParserResult with structured specifications
        """
        self.log_info(f"Processing parser request")

        try:
            # Use common input handler
            data, context = unwrap_input(input_data)

            # Extract text from input
            text = self._extract_text(data)

            # Process with NLP
            nlp_result = await self._process_nlp(text)

            # Extract entities
            entities = await self._extract_entities(nlp_result)

            # Analyze requirements
            requirements = await self._analyze_requirements(nlp_result, entities)

            # Build data model
            data_model = await self._build_data_model(entities, requirements)

            # Parse API definitions
            api_definitions = await self._parse_apis(text, entities)

            # Analyze constraints
            constraints = await self._analyze_constraints(nlp_result)

            # Resolve dependencies
            dependencies = await self._resolve_dependencies(requirements, entities)

            # Generate user stories
            user_stories = await self._generate_user_stories(requirements, entities)

            # Extract business rules
            business_rules = await self._extract_business_rules(nlp_result)

            # Analyze technical requirements
            technical_reqs = await self._analyze_technical(nlp_result)

            # Build specifications
            specifications = await self._build_specifications(
                entities, requirements, data_model, api_definitions, constraints
            )

            # Validate everything
            validation = await self._validate_all(specifications)

            # Create acceptance criteria
            acceptance_criteria = await self._create_acceptance_criteria(
                user_stories, requirements
            )

            # Combine results
            result = {
                "success": True,
                "entities": entities,
                "requirements": requirements,
                "data_model": data_model,
                "api_definitions": api_definitions,
                "constraints": constraints,
                "dependencies": dependencies,
                "user_stories": user_stories,
                "business_rules": business_rules,
                "technical_requirements": technical_reqs,
                "specifications": specifications,
                "acceptance_criteria": acceptance_criteria,
                "validation": validation,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": self.config.version,
                    "word_count": len(text.split()),
                    "entity_count": len(entities),
                    "requirement_count": len(requirements),
                },
            }

            self.log_info(f"Parser processing complete")
            return EnhancedParserResult(result)

        except Exception as e:
            self.log_error(f"Parser processing failed: {str(e)}")
            return EnhancedParserResult({"success": False, "error": str(e)})

    def _extract_text(self, input_data: Any) -> str:
        """Extract text from input data"""
        # Handle AgentInput wrapper
        if hasattr(input_data, "data"):
            data = input_data.data
        elif isinstance(input_data, dict):
            data = input_data
        else:
            return str(input_data)

        if isinstance(data, str):
            return data

        text_parts = []

        # Extract from various fields
        if "query" in data:
            text_parts.append(data["query"])
        if "requirements" in data:
            if isinstance(data["requirements"], list):
                text_parts.extend(data["requirements"])
            else:
                text_parts.append(str(data["requirements"]))
        if "description" in data:
            text_parts.append(data["description"])
        if "text" in data:
            text_parts.append(data["text"])

        return " ".join(text_parts)

    async def _process_nlp(self, text: str) -> Dict[str, Any]:
        """Process text with NLP using AI service"""
        if self.nlp_processor:
            return await self.nlp_processor.process(text)

        # Use AI service for advanced NLP
        try:
            from src.services.ai_service import ai_service

            prompt = f"""Analyze the following text for NLP processing:

"{text}"

Extract and return a JSON object with:
- sentences: array of sentences
- tokens: array of tokens (words)
- entities: array of named entities (people, organizations, locations, etc.)
- pos_tags: array of part-of-speech tags
- key_phrases: array of important phrases
- sentiment: overall sentiment (positive/neutral/negative)
- language: detected language
- intent: primary intent of the text

Respond with only the JSON object."""

            response = await ai_service.generate(prompt)

            # Try to parse AI response as JSON
            import json
            import re

            # Extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                nlp_result = json.loads(json_match.group())
                nlp_result["original"] = text
                return nlp_result
        except Exception as e:
            self.log_warning(f"AI NLP processing failed: {e}")

        # Fallback processing
        sentences = text.split(".")
        tokens = text.lower().split()

        return {
            "original": text,
            "sentences": sentences,
            "tokens": tokens,
            "pos_tags": [],
            "entities": [],
            "dependencies": [],
            "key_phrases": [],
            "sentiment": "neutral",
            "intent": "unknown",
        }

    async def _extract_entities(self, nlp_result: Dict) -> Dict[str, List]:
        """Extract entities from NLP result"""
        if self.entity_extractor:
            return await self.entity_extractor.extract(nlp_result)

        # Fallback extraction
        text = nlp_result["original"].lower()
        entities = {
            "users": [],
            "objects": [],
            "actions": [],
            "attributes": [],
            "relationships": [],
        }

        # Extract users
        user_patterns = ["user", "admin", "customer", "client", "member"]
        for pattern in user_patterns:
            if pattern in text:
                entities["users"].append(
                    {"name": pattern, "type": "actor", "properties": []}
                )

        # Extract objects
        object_patterns = ["product", "order", "invoice", "report", "dashboard"]
        for pattern in object_patterns:
            if pattern in text:
                entities["objects"].append(
                    {"name": pattern, "type": "entity", "properties": []}
                )

        # Extract actions
        for match in re.finditer(self.patterns["action"], text):
            entities["actions"].append({"name": match.group(), "type": "operation"})

        return entities

    async def _analyze_requirements(
        self, nlp_result: Dict, entities: Dict
    ) -> List[Dict]:
        """Analyze requirements from text using AI"""
        if self.requirement_analyzer:
            return await self.requirement_analyzer.analyze(nlp_result, entities)

        # Use AI service for requirement analysis
        try:
            from src.services.ai_service import ai_service

            prompt = f"""Analyze the following text to extract software requirements:

Text: "{nlp_result['original']}"

Identified Entities: {json.dumps(entities, indent=2)}

Extract all requirements and return a JSON array where each requirement has:
- text: the requirement statement
- type: mandatory/recommended/optional/functional/non-functional
- priority: critical/high/medium/low
- category: feature/performance/security/usability/compatibility
- actors: list of actors involved
- preconditions: list of preconditions
- postconditions: list of postconditions
- acceptance_criteria: list of testable criteria
- dependencies: list of other requirement dependencies
- estimated_complexity: simple/medium/complex

Focus on extracting actionable, specific requirements.
Respond with only the JSON array."""

            response = await ai_service.generate(prompt)

            # Parse AI response
            import json
            import re

            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                requirements = json.loads(json_match.group())

                # Enhance with entity mappings
                for req in requirements:
                    req["entities"] = self._find_entities_in_text(req["text"], entities)

                return requirements
        except Exception as e:
            self.log_warning(f"AI requirement analysis failed: {e}")

        # Fallback analysis
        requirements = []
        text = nlp_result["original"]
        sentences = nlp_result["sentences"]

        for sentence in sentences:
            # Check for requirement keywords
            if re.search(self.patterns["requirement"], sentence, re.IGNORECASE):
                requirements.append(
                    {
                        "text": sentence.strip(),
                        "type": self._classify_requirement(sentence),
                        "priority": self._determine_priority(sentence),
                        "entities": self._find_entities_in_text(sentence, entities),
                        "category": "feature",
                        "actors": [],
                        "preconditions": [],
                        "postconditions": [],
                        "acceptance_criteria": [],
                        "dependencies": [],
                        "estimated_complexity": "medium",
                    }
                )

        return requirements

    async def _build_data_model(
        self, entities: Dict, requirements: List[Dict]
    ) -> Dict[str, Any]:
        """Build data model from entities and requirements"""
        if self.data_model_builder:
            return await self.data_model_builder.build(entities, requirements)

        # Fallback model building
        models = {}

        for entity_type, entity_list in entities.items():
            if entity_type == "objects":
                for entity in entity_list:
                    model_name = entity["name"].capitalize()
                    models[model_name] = {
                        "fields": self._infer_fields(entity, requirements),
                        "relationships": self._infer_relationships(entity, entities),
                        "validations": self._infer_validations(entity, requirements),
                    }

        return models

    async def _parse_apis(self, text: str, entities: Dict) -> List[Dict]:
        """Parse API definitions from text"""
        if self.api_parser:
            return await self.api_parser.parse(text, entities)

        # Fallback API parsing
        apis = []

        # Look for REST endpoints
        for match in re.finditer(self.patterns["api_endpoint"], text):
            endpoint = match.group()
            method, path = endpoint.split(None, 1)

            apis.append(
                {
                    "method": method,
                    "path": path,
                    "description": self._extract_api_description(text, endpoint),
                    "parameters": self._extract_api_parameters(path),
                    "response": self._infer_api_response(method, path, entities),
                }
            )

        # Generate CRUD APIs for entities
        for entity_type, entity_list in entities.items():
            if entity_type == "objects":
                for entity in entity_list:
                    apis.extend(self._generate_crud_apis(entity))

        return apis

    async def _analyze_constraints(self, nlp_result: Dict) -> Dict[str, List]:
        """Analyze constraints from text"""
        if self.constraint_analyzer:
            return await self.constraint_analyzer.analyze(nlp_result)

        # Fallback constraint analysis
        constraints = {
            "performance": [],
            "security": [],
            "business": [],
            "technical": [],
        }

        text = nlp_result["original"].lower()

        # Performance constraints
        if "response time" in text or "performance" in text:
            constraints["performance"].append(
                {
                    "type": "response_time",
                    "value": "< 1 second",
                    "description": "API response time requirement",
                }
            )

        # Security constraints
        if "secure" in text or "encryption" in text or "authentication" in text:
            constraints["security"].append(
                {
                    "type": "authentication",
                    "value": "required",
                    "description": "User authentication required",
                }
            )

        # Business constraints
        for match in re.finditer(self.patterns["constraint"], text):
            constraints["business"].append(
                {
                    "type": "limit",
                    "value": match.group(),
                    "description": "Business rule constraint",
                }
            )

        return constraints

    async def _resolve_dependencies(
        self, requirements: List[Dict], entities: Dict
    ) -> List[Dict]:
        """Resolve dependencies between requirements"""
        if self.dependency_resolver:
            return await self.dependency_resolver.resolve(requirements, entities)

        # Fallback dependency resolution
        dependencies = []

        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements):
                if i != j:
                    # Check if req2 depends on req1
                    if self._check_dependency(req1, req2):
                        dependencies.append(
                            {
                                "from": i,
                                "to": j,
                                "type": "requires",
                                "description": f"Requirement {j} depends on {i}",
                            }
                        )

        return dependencies

    async def _generate_user_stories(
        self, requirements: List[Dict], entities: Dict
    ) -> List[Dict]:
        """Generate user stories from requirements"""
        if self.user_story_generator:
            return await self.user_story_generator.generate(requirements, entities)

        # Fallback user story generation
        stories = []

        for req in requirements:
            # Extract actors and actions
            actors = entities.get("users", [])
            actions = entities.get("actions", [])

            for actor in actors:
                for action in actions:
                    if action["name"] in req["text"].lower():
                        stories.append(
                            {
                                "title": f"{actor['name'].capitalize()} {action['name']}s",
                                "description": f"As a {actor['name']}, I want to {action['name']} so that {self._infer_benefit(req['text'])}",
                                "acceptance_criteria": [],
                                "priority": req.get("priority", "medium"),
                                "effort": self._estimate_effort(req),
                            }
                        )

        return stories

    async def _extract_business_rules(self, nlp_result: Dict) -> List[Dict]:
        """Extract business rules from text"""
        if self.business_rule_extractor:
            return await self.business_rule_extractor.extract(nlp_result)

        # Fallback business rule extraction
        rules = []
        text = nlp_result["original"]

        # Look for conditional statements
        rule_patterns = [
            r"if\s+(.+?)\s+then\s+(.+)",
            r"when\s+(.+?)\s+must\s+(.+)",
            r"(.+?)\s+requires\s+(.+)",
            r"(.+?)\s+should\s+(.+)",
        ]

        for pattern in rule_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                rules.append(
                    {
                        "condition": match.group(1).strip(),
                        "action": match.group(2).strip(),
                        "type": "business_logic",
                        "enforceable": True,
                    }
                )

        return rules

    async def _analyze_technical(self, nlp_result: Dict) -> Dict[str, Any]:
        """Analyze technical requirements"""
        if self.technical_analyzer:
            return await self.technical_analyzer.analyze(nlp_result)

        # Fallback technical analysis
        tech_reqs = {
            "platform": [],
            "frameworks": [],
            "databases": [],
            "integrations": [],
            "deployment": [],
        }

        text = nlp_result["original"].lower()

        # Detect platforms
        platforms = ["web", "mobile", "desktop", "cloud", "ios", "android"]
        for platform in platforms:
            if platform in text:
                tech_reqs["platform"].append(platform)

        # Detect frameworks
        frameworks = ["react", "vue", "angular", "django", "flask", "spring", "express"]
        for framework in frameworks:
            if framework in text:
                tech_reqs["frameworks"].append(framework)

        # Detect databases
        databases = ["mysql", "postgresql", "mongodb", "redis", "elasticsearch"]
        for db in databases:
            if db in text:
                tech_reqs["databases"].append(db)

        return tech_reqs

    async def _build_specifications(
        self,
        entities: Dict,
        requirements: List[Dict],
        data_model: Dict,
        apis: List[Dict],
        constraints: Dict,
    ) -> Dict[str, Any]:
        """Build complete specifications"""
        if self.specification_builder:
            return await self.specification_builder.build(
                entities, requirements, data_model, apis, constraints
            )

        # Fallback specification building
        return {
            "functional": {
                "features": self._extract_features(requirements),
                "use_cases": self._generate_use_cases(entities, requirements),
                "workflows": self._design_workflows(entities, requirements),
            },
            "non_functional": {
                "performance": constraints.get("performance", []),
                "security": constraints.get("security", []),
                "scalability": self._infer_scalability(requirements),
                "usability": self._infer_usability(requirements),
            },
            "data": {
                "models": data_model,
                "schemas": self._generate_schemas(data_model),
                "migrations": [],
            },
            "api": {
                "endpoints": apis,
                "authentication": self._design_auth(constraints),
                "documentation": self._generate_api_docs(apis),
            },
        }

    async def _validate_all(self, specifications: Dict) -> Dict[str, Any]:
        """Validate all specifications"""
        if self.validation_engine:
            return await self.validation_engine.validate(specifications)

        # Fallback validation
        validation = {"valid": True, "errors": [], "warnings": [], "suggestions": []}

        # Check for completeness
        if not specifications.get("functional", {}).get("features"):
            validation["warnings"].append("No features specified")

        if not specifications.get("data", {}).get("models"):
            validation["warnings"].append("No data models defined")

        if not specifications.get("api", {}).get("endpoints"):
            validation["suggestions"].append("Consider defining API endpoints")

        return validation

    async def _create_acceptance_criteria(
        self, user_stories: List[Dict], requirements: List[Dict]
    ) -> List[Dict]:
        """Create acceptance criteria for user stories"""
        criteria = []

        for story in user_stories:
            story_criteria = {"story": story["title"], "criteria": []}

            # Generate criteria based on story
            story_criteria["criteria"].append(
                f"Given the user is a {story['title'].split()[0].lower()}"
            )
            story_criteria["criteria"].append(f"When they perform the action")
            story_criteria["criteria"].append(f"Then the expected outcome occurs")

            criteria.append(story_criteria)

        return criteria

    # Helper methods
    def _classify_requirement(self, text: str) -> str:
        """Classify requirement type"""
        text_lower = text.lower()

        if "must" in text_lower or "shall" in text_lower:
            return "mandatory"
        elif "should" in text_lower:
            return "recommended"
        elif "could" in text_lower or "may" in text_lower:
            return "optional"
        else:
            return "functional"

    def _determine_priority(self, text: str) -> str:
        """Determine requirement priority"""
        text_lower = text.lower()

        if "critical" in text_lower or "urgent" in text_lower:
            return "critical"
        elif "high" in text_lower or "important" in text_lower:
            return "high"
        elif "low" in text_lower or "minor" in text_lower:
            return "low"
        else:
            return "medium"

    def _find_entities_in_text(self, text: str, entities: Dict) -> List[str]:
        """Find entities mentioned in text"""
        found = []
        text_lower = text.lower()

        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                if entity["name"] in text_lower:
                    found.append(entity["name"])

        return found

    def _infer_fields(self, entity: Dict, requirements: List[Dict]) -> List[Dict]:
        """Infer fields for an entity"""
        fields = [
            {"name": "id", "type": "uuid", "required": True},
            {"name": "created_at", "type": "datetime", "required": True},
            {"name": "updated_at", "type": "datetime", "required": True},
        ]

        # Add common fields based on entity type
        if "user" in entity["name"].lower():
            fields.extend(
                [
                    {"name": "email", "type": "email", "required": True},
                    {"name": "password", "type": "string", "required": True},
                    {"name": "name", "type": "string", "required": True},
                ]
            )
        elif "product" in entity["name"].lower():
            fields.extend(
                [
                    {"name": "name", "type": "string", "required": True},
                    {"name": "price", "type": "decimal", "required": True},
                    {"name": "description", "type": "text", "required": False},
                ]
            )

        return fields

    def _infer_relationships(self, entity: Dict, all_entities: Dict) -> List[Dict]:
        """Infer relationships between entities"""
        relationships = []

        # Add common relationships
        if "order" in entity["name"].lower():
            relationships.append(
                {"type": "belongs_to", "target": "User", "foreign_key": "user_id"}
            )
            relationships.append(
                {"type": "has_many", "target": "Product", "through": "OrderItem"}
            )

        return relationships

    def _infer_validations(self, entity: Dict, requirements: List[Dict]) -> List[Dict]:
        """Infer validations for an entity"""
        validations = []

        # Add common validations
        validations.append({"field": "email", "type": "format", "pattern": "email"})

        return validations

    def _extract_api_description(self, text: str, endpoint: str) -> str:
        """Extract API description from text"""
        # Find sentence containing the endpoint
        sentences = text.split(".")
        for sentence in sentences:
            if endpoint in sentence:
                return sentence.strip()
        return f"API endpoint: {endpoint}"

    def _extract_api_parameters(self, path: str) -> List[Dict]:
        """Extract parameters from API path"""
        params = []

        # Extract path parameters
        for match in re.finditer(r"\{(\w+)\}", path):
            params.append({"name": match.group(1), "type": "path", "required": True})

        return params

    def _infer_api_response(self, method: str, path: str, entities: Dict) -> Dict:
        """Infer API response structure"""
        if method == "GET":
            if "{" in path:  # Single resource
                return {"type": "object", "status": 200}
            else:  # Collection
                return {"type": "array", "status": 200}
        elif method == "POST":
            return {"type": "object", "status": 201}
        elif method == "PUT" or method == "PATCH":
            return {"type": "object", "status": 200}
        elif method == "DELETE":
            return {"type": "null", "status": 204}
        else:
            return {"type": "object", "status": 200}

    def _generate_crud_apis(self, entity: Dict) -> List[Dict]:
        """Generate CRUD APIs for an entity"""
        name = entity["name"].lower()
        return [
            {
                "method": "GET",
                "path": f"/{name}s",
                "description": f"List all {name}s",
                "parameters": [],
                "response": {"type": "array", "status": 200},
            },
            {
                "method": "GET",
                "path": f"/{name}s/{{id}}",
                "description": f"Get a specific {name}",
                "parameters": [{"name": "id", "type": "path", "required": True}],
                "response": {"type": "object", "status": 200},
            },
            {
                "method": "POST",
                "path": f"/{name}s",
                "description": f"Create a new {name}",
                "parameters": [],
                "response": {"type": "object", "status": 201},
            },
            {
                "method": "PUT",
                "path": f"/{name}s/{{id}}",
                "description": f"Update a {name}",
                "parameters": [{"name": "id", "type": "path", "required": True}],
                "response": {"type": "object", "status": 200},
            },
            {
                "method": "DELETE",
                "path": f"/{name}s/{{id}}",
                "description": f"Delete a {name}",
                "parameters": [{"name": "id", "type": "path", "required": True}],
                "response": {"type": "null", "status": 204},
            },
        ]

    def _check_dependency(self, req1: Dict, req2: Dict) -> bool:
        """Check if req2 depends on req1"""
        # Simple heuristic: check if entities from req1 are mentioned in req2
        req1_entities = req1.get("entities", [])
        req2_text = req2.get("text", "").lower()

        for entity in req1_entities:
            if entity in req2_text:
                return True

        return False

    def _infer_benefit(self, text: str) -> str:
        """Infer benefit from requirement text"""
        if "improve" in text.lower():
            return "I can improve efficiency"
        elif "track" in text.lower():
            return "I can track progress"
        elif "manage" in text.lower():
            return "I can manage resources effectively"
        else:
            return "I can achieve my goals"

    def _estimate_effort(self, requirement: Dict) -> str:
        """Estimate effort for a requirement"""
        text = requirement.get("text", "").lower()

        # Simple heuristic based on keywords
        if "complex" in text or "integration" in text:
            return "high"
        elif "simple" in text or "basic" in text:
            return "low"
        else:
            return "medium"

    def _extract_features(self, requirements: List[Dict]) -> List[Dict]:
        """Extract features from requirements"""
        features = []

        for req in requirements:
            if req.get("type") in ["mandatory", "functional"]:
                features.append(
                    {
                        "name": self._generate_feature_name(req["text"]),
                        "description": req["text"],
                        "priority": req.get("priority", "medium"),
                    }
                )

        return features

    def _generate_feature_name(self, text: str) -> str:
        """Generate feature name from text"""
        # Take first few words and capitalize
        words = text.split()[:5]
        return " ".join(words).title()

    def _generate_use_cases(
        self, entities: Dict, requirements: List[Dict]
    ) -> List[Dict]:
        """Generate use cases"""
        use_cases = []

        for req in requirements:
            use_cases.append(
                {
                    "name": self._generate_feature_name(req["text"]),
                    "actors": entities.get("users", []),
                    "description": req["text"],
                    "steps": [],
                }
            )

        return use_cases

    def _design_workflows(self, entities: Dict, requirements: List[Dict]) -> List[Dict]:
        """Design workflows"""
        workflows = []

        # Create basic workflow
        workflows.append(
            {
                "name": "Main Workflow",
                "steps": [
                    {"action": "Start", "next": "Process"},
                    {"action": "Process", "next": "Complete"},
                    {"action": "Complete", "next": "End"},
                ],
            }
        )

        return workflows

    def _infer_scalability(self, requirements: List[Dict]) -> List[Dict]:
        """Infer scalability requirements"""
        return [{"type": "horizontal", "description": "Support horizontal scaling"}]

    def _infer_usability(self, requirements: List[Dict]) -> List[Dict]:
        """Infer usability requirements"""
        return [
            {"type": "responsive", "description": "Responsive design for all devices"}
        ]

    def _generate_schemas(self, data_model: Dict) -> Dict[str, Any]:
        """Generate database schemas"""
        schemas = {}

        for model_name, model_def in data_model.items():
            schemas[model_name.lower()] = {
                "table": f"{model_name.lower()}s",
                "columns": model_def.get("fields", []),
            }

        return schemas

    def _design_auth(self, constraints: Dict) -> Dict[str, Any]:
        """Design authentication system"""
        return {
            "type": "JWT",
            "required": True,
            "endpoints": ["/login", "/logout", "/refresh"],
        }

    def _generate_api_docs(self, apis: List[Dict]) -> Dict[str, Any]:
        """Generate API documentation"""
        return {"format": "OpenAPI 3.0", "endpoints": len(apis), "generated": True}
