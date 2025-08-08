"""
Enterprise Natural Language Input Agent
Production-grade implementation with AI providers, caching, and fallback
"""

from typing import Dict, Any, Optional, List
import asyncio
import json
import re
from datetime import datetime
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
import hashlib

from .base_agent import EnterpriseBaseAgent, AgentConfig, AgentContext

class EnterpriseNLInputAgent(EnterpriseBaseAgent):
    """
    Natural Language Input Processing Agent
    Analyzes user requirements and extracts structured project specifications
    """
    
    def __init__(self):
        config = AgentConfig(
            name="nl_input_agent",
            version="1.0.0",
            timeout=30,
            retries=3,
            cache_ttl=3600,
            rate_limit=100
        )
        super().__init__(config)
        
        # AI providers
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        
        # Pattern matchers for project types
        self.project_patterns = {
            "web_app": [
                r"web\s*app",
                r"website",
                r"portal",
                r"dashboard",
                r"frontend",
                r"react",
                r"vue",
                r"angular"
            ],
            "mobile_app": [
                r"mobile\s*app",
                r"ios",
                r"android",
                r"flutter",
                r"react\s*native",
                r"swift"
            ],
            "api": [
                r"api",
                r"rest",
                r"graphql",
                r"backend",
                r"microservice",
                r"server"
            ],
            "cli": [
                r"cli",
                r"command\s*line",
                r"terminal",
                r"console",
                r"script"
            ],
            "desktop": [
                r"desktop",
                r"electron",
                r"native\s*app",
                r"windows\s*app",
                r"mac\s*app"
            ],
            "data_pipeline": [
                r"etl",
                r"data\s*pipeline",
                r"data\s*processing",
                r"analytics",
                r"machine\s*learning",
                r"ml\s*pipeline"
            ],
            "ai_ml": [
                r"ai",
                r"artificial\s*intelligence",
                r"machine\s*learning",
                r"deep\s*learning",
                r"neural\s*network",
                r"nlp",
                r"computer\s*vision"
            ],
            "blockchain": [
                r"blockchain",
                r"smart\s*contract",
                r"dapp",
                r"web3",
                r"ethereum",
                r"solidity"
            ],
            "iot": [
                r"iot",
                r"embedded",
                r"arduino",
                r"raspberry\s*pi",
                r"sensor",
                r"device"
            ],
            "game": [
                r"game",
                r"unity",
                r"unreal",
                r"godot",
                r"pygame"
            ]
        }
        
        # Technology stack patterns
        self.tech_patterns = {
            "frontend": {
                "react": [r"react", r"next\.?js"],
                "vue": [r"vue", r"nuxt"],
                "angular": [r"angular"],
                "svelte": [r"svelte", r"sveltekit"],
                "vanilla": [r"vanilla", r"plain\s*js", r"html"]
            },
            "backend": {
                "node": [r"node", r"express", r"nest\.?js", r"fastify"],
                "python": [r"python", r"django", r"flask", r"fastapi"],
                "java": [r"java", r"spring"],
                "go": [r"go", r"golang", r"gin", r"fiber"],
                "rust": [r"rust", r"actix", r"rocket"],
                "dotnet": [r"\.net", r"c#", r"asp\.net"]
            },
            "database": {
                "postgresql": [r"postgres", r"postgresql"],
                "mysql": [r"mysql", r"mariadb"],
                "mongodb": [r"mongo", r"mongodb"],
                "redis": [r"redis"],
                "elasticsearch": [r"elastic", r"elasticsearch"],
                "sqlite": [r"sqlite"],
                "dynamodb": [r"dynamodb"],
                "cassandra": [r"cassandra"]
            },
            "cloud": {
                "aws": [r"aws", r"amazon"],
                "gcp": [r"gcp", r"google\s*cloud"],
                "azure": [r"azure", r"microsoft\s*cloud"],
                "vercel": [r"vercel"],
                "netlify": [r"netlify"],
                "heroku": [r"heroku"]
            }
        }
    
    async def _custom_initialize(self):
        """Initialize AI providers"""
        try:
            # Initialize Anthropic Claude
            self.anthropic_client = AsyncAnthropic(
                api_key=await self._get_secret("ANTHROPIC_API_KEY")
            )
            
            # Initialize OpenAI
            self.openai_client = AsyncOpenAI(
                api_key=await self._get_secret("OPENAI_API_KEY")
            )
            
            self.logger.info("AI providers initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI providers: {str(e)}")
            # Continue without AI providers - will use rule-based fallback
    
    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Process natural language input and extract project requirements
        """
        query = input_data.get("query", "")
        additional_context = input_data.get("context", {})
        
        if not query:
            raise ValueError("No query provided for NL processing")
        
        self.logger.info(
            "Processing NL query",
            query_length=len(query),
            trace_id=context.trace_id
        )
        
        # Try AI-based processing first
        result = None
        
        if self.anthropic_client:
            try:
                result = await self._process_with_claude(query, additional_context, context)
                self.logger.info("Successfully processed with Claude")
            except Exception as e:
                self.logger.warning(f"Claude processing failed: {str(e)}")
        
        if not result and self.openai_client:
            try:
                result = await self._process_with_openai(query, additional_context, context)
                self.logger.info("Successfully processed with OpenAI")
            except Exception as e:
                self.logger.warning(f"OpenAI processing failed: {str(e)}")
        
        if not result:
            # Fallback to rule-based processing
            self.logger.info("Using rule-based processing as fallback")
            result = await self._rule_based_processing(query, additional_context)
        
        # Enrich result with additional analysis
        enriched_result = await self._enrich_requirements(result, query, context)
        
        return enriched_result
    
    async def _process_with_claude(
        self,
        query: str,
        additional_context: Dict,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Process with Anthropic Claude"""
        
        system_prompt = """You are an expert software architect analyzing project requirements.
        Extract and structure the following information from the user's request:
        
        1. Project Type (web_app, mobile_app, api, cli, desktop, data_pipeline, ai_ml, blockchain, iot, game)
        2. Project Name and Description
        3. Core Features (list of main functionalities)
        4. Technical Requirements:
           - Programming languages
           - Frameworks and libraries
           - Database requirements
           - Third-party integrations
        5. Non-Functional Requirements:
           - Performance requirements
           - Scalability needs
           - Security requirements
           - Compliance requirements
        6. User Interface Requirements (if applicable)
        7. Target Audience/Users
        8. Deployment Environment (cloud, on-premise, hybrid)
        9. Development Constraints (timeline, budget, team size)
        10. Success Criteria
        
        Respond in JSON format with these exact keys:
        {
            "project_type": "",
            "project_name": "",
            "description": "",
            "features": [],
            "technical_requirements": {
                "languages": [],
                "frameworks": [],
                "databases": [],
                "integrations": []
            },
            "non_functional_requirements": {
                "performance": {},
                "scalability": {},
                "security": [],
                "compliance": []
            },
            "ui_requirements": {},
            "target_audience": "",
            "deployment": {},
            "constraints": {},
            "success_criteria": [],
            "estimated_complexity": "low|medium|high|very_high"
        }
        """
        
        user_prompt = f"""Analyze this project request and extract structured requirements:
        
        {query}
        
        Additional Context:
        {json.dumps(additional_context, indent=2) if additional_context else "None"}
        """
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Extract JSON from response
        try:
            # Find JSON block in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response_text)
                
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Claude response: {str(e)}")
            raise
    
    async def _process_with_openai(
        self,
        query: str,
        additional_context: Dict,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Process with OpenAI GPT-4"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert software architect analyzing project requirements.
                Extract structured requirements from the user's request and respond in JSON format."""
            },
            {
                "role": "user",
                "content": f"""Analyze this project request:
                
                {query}
                
                Context: {json.dumps(additional_context) if additional_context else "None"}
                
                Extract: project_type, features, technical_requirements, non_functional_requirements, etc."""
            }
        ]
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def _rule_based_processing(
        self,
        query: str,
        additional_context: Dict
    ) -> Dict[str, Any]:
        """Fallback rule-based processing"""
        
        query_lower = query.lower()
        
        # Detect project type
        project_type = "web_app"  # default
        for ptype, patterns in self.project_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    project_type = ptype
                    break
        
        # Extract technology preferences
        detected_tech = {
            "frontend": [],
            "backend": [],
            "database": [],
            "cloud": []
        }
        
        for category, techs in self.tech_patterns.items():
            for tech_name, patterns in techs.items():
                for pattern in patterns:
                    if re.search(pattern, query_lower):
                        detected_tech[category].append(tech_name)
        
        # Extract features (basic keyword extraction)
        feature_keywords = [
            "authentication", "auth", "login", "signup",
            "payment", "billing", "subscription",
            "search", "filter", "sort",
            "upload", "download", "file",
            "chat", "messaging", "notification",
            "dashboard", "analytics", "reporting",
            "api", "integration", "webhook",
            "admin", "management", "crud",
            "social", "sharing", "comment",
            "map", "location", "gps"
        ]
        
        features = []
        for keyword in feature_keywords:
            if keyword in query_lower:
                features.append(keyword)
        
        # Estimate complexity
        complexity = "low"
        if len(features) > 10:
            complexity = "very_high"
        elif len(features) > 7:
            complexity = "high"
        elif len(features) > 4:
            complexity = "medium"
        
        return {
            "project_type": project_type,
            "project_name": self._extract_project_name(query),
            "description": query[:500],  # First 500 chars as description
            "features": features,
            "technical_requirements": {
                "languages": self._detect_languages(query_lower),
                "frameworks": detected_tech.get("frontend", []) + detected_tech.get("backend", []),
                "databases": detected_tech.get("database", []),
                "integrations": []
            },
            "non_functional_requirements": {
                "performance": {
                    "response_time": "< 200ms",
                    "concurrent_users": 1000
                },
                "scalability": {
                    "horizontal": True,
                    "auto_scaling": True
                },
                "security": ["authentication", "authorization", "encryption"],
                "compliance": []
            },
            "ui_requirements": {
                "responsive": True,
                "mobile_friendly": True,
                "accessibility": "WCAG 2.1 AA"
            },
            "target_audience": "general",
            "deployment": {
                "environment": detected_tech.get("cloud", ["aws"])[0] if detected_tech.get("cloud") else "cloud",
                "containerized": True
            },
            "constraints": {
                "timeline": "3 months",
                "budget": "standard"
            },
            "success_criteria": [
                "Functional requirements met",
                "Performance targets achieved",
                "Security standards implemented"
            ],
            "estimated_complexity": complexity
        }
    
    def _extract_project_name(self, query: str) -> str:
        """Extract project name from query"""
        # Look for quoted strings
        quoted = re.findall(r'"([^"]*)"', query)
        if quoted:
            return quoted[0]
        
        # Look for "called X" or "named X"
        named = re.search(r'(?:called|named)\s+(\w+)', query, re.IGNORECASE)
        if named:
            return named.group(1)
        
        # Look for "X app" or "X application"
        app_name = re.search(r'(\w+)\s+(?:app|application|system|platform)', query, re.IGNORECASE)
        if app_name:
            return app_name.group(1)
        
        return "MyProject"
    
    def _detect_languages(self, query: str) -> List[str]:
        """Detect programming languages from query"""
        languages = []
        
        language_patterns = {
            "python": [r"python", r"py"],
            "javascript": [r"javascript", r"js", r"node"],
            "typescript": [r"typescript", r"ts"],
            "java": [r"java(?!script)"],
            "csharp": [r"c#", r"csharp", r"\.net"],
            "go": [r"\bgo\b", r"golang"],
            "rust": [r"rust"],
            "php": [r"php"],
            "ruby": [r"ruby"],
            "swift": [r"swift"],
            "kotlin": [r"kotlin"]
        }
        
        for lang, patterns in language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    languages.append(lang)
        
        return languages if languages else ["python"]  # Default to Python
    
    async def _enrich_requirements(
        self,
        requirements: Dict[str, Any],
        original_query: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Enrich requirements with additional analysis"""
        
        # Add metadata
        requirements["metadata"] = {
            "analyzed_at": datetime.utcnow().isoformat(),
            "agent_version": self.config.version,
            "trace_id": context.trace_id,
            "confidence_score": self._calculate_confidence(requirements),
            "query_length": len(original_query),
            "processing_method": "ai" if self.anthropic_client or self.openai_client else "rule_based"
        }
        
        # Add suggested architecture
        requirements["suggested_architecture"] = self._suggest_architecture(requirements)
        
        # Add estimated resources
        requirements["estimated_resources"] = self._estimate_resources(requirements)
        
        # Add risk assessment
        requirements["risk_assessment"] = self._assess_risks(requirements)
        
        return requirements
    
    def _calculate_confidence(self, requirements: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted requirements"""
        score = 0.0
        
        # Check completeness of required fields
        if requirements.get("project_type"):
            score += 0.2
        if requirements.get("features") and len(requirements["features"]) > 0:
            score += 0.2
        if requirements.get("technical_requirements", {}).get("frameworks"):
            score += 0.2
        if requirements.get("description") and len(requirements["description"]) > 50:
            score += 0.2
        if requirements.get("success_criteria"):
            score += 0.2
        
        return min(score, 1.0)
    
    def _suggest_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest architecture based on requirements"""
        project_type = requirements.get("project_type", "web_app")
        complexity = requirements.get("estimated_complexity", "medium")
        
        architectures = {
            "web_app": {
                "low": "monolithic",
                "medium": "modular_monolith",
                "high": "microservices",
                "very_high": "microservices_event_driven"
            },
            "mobile_app": {
                "low": "mvc",
                "medium": "mvvm",
                "high": "clean_architecture",
                "very_high": "clean_architecture_modular"
            },
            "api": {
                "low": "rest_monolithic",
                "medium": "rest_modular",
                "high": "graphql_federation",
                "very_high": "event_driven_microservices"
            }
        }
        
        architecture_type = architectures.get(project_type, {}).get(complexity, "modular")
        
        return {
            "type": architecture_type,
            "components": self._get_architecture_components(architecture_type),
            "patterns": self._get_design_patterns(project_type, complexity)
        }
    
    def _get_architecture_components(self, architecture_type: str) -> List[str]:
        """Get components for architecture type"""
        components_map = {
            "monolithic": ["api", "database", "cache"],
            "modular_monolith": ["api", "database", "cache", "message_queue"],
            "microservices": ["api_gateway", "services", "database", "cache", "message_broker", "service_mesh"],
            "microservices_event_driven": ["api_gateway", "services", "database", "cache", "event_bus", "service_mesh", "saga_orchestrator"]
        }
        
        return components_map.get(architecture_type, ["api", "database"])
    
    def _get_design_patterns(self, project_type: str, complexity: str) -> List[str]:
        """Get recommended design patterns"""
        patterns = ["repository", "factory", "singleton"]
        
        if complexity in ["high", "very_high"]:
            patterns.extend(["cqrs", "event_sourcing", "saga"])
        
        if project_type == "api":
            patterns.append("api_gateway")
        
        return patterns
    
    def _estimate_resources(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate required resources"""
        complexity = requirements.get("estimated_complexity", "medium")
        
        resources_map = {
            "low": {
                "developers": 1,
                "timeline_weeks": 4,
                "infrastructure_cost_monthly": 100
            },
            "medium": {
                "developers": 2,
                "timeline_weeks": 12,
                "infrastructure_cost_monthly": 500
            },
            "high": {
                "developers": 4,
                "timeline_weeks": 24,
                "infrastructure_cost_monthly": 2000
            },
            "very_high": {
                "developers": 8,
                "timeline_weeks": 48,
                "infrastructure_cost_monthly": 5000
            }
        }
        
        return resources_map.get(complexity, resources_map["medium"])
    
    def _assess_risks(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess project risks"""
        risks = []
        
        # Complexity risk
        if requirements.get("estimated_complexity") in ["high", "very_high"]:
            risks.append({
                "type": "complexity",
                "level": "high",
                "description": "High project complexity may lead to delays",
                "mitigation": "Break down into smaller milestones"
            })
        
        # Technology risk
        tech_reqs = requirements.get("technical_requirements", {})
        if len(tech_reqs.get("frameworks", [])) > 5:
            risks.append({
                "type": "technology",
                "level": "medium",
                "description": "Multiple technology dependencies",
                "mitigation": "Ensure team expertise in all technologies"
            })
        
        # Integration risk
        if len(tech_reqs.get("integrations", [])) > 3:
            risks.append({
                "type": "integration",
                "level": "medium",
                "description": "Multiple third-party integrations",
                "mitigation": "Plan for API changes and fallbacks"
            })
        
        return risks
    
    async def _get_secret(self, key: str) -> str:
        """Get secret from secure storage"""
        # In production, this would fetch from AWS Secrets Manager or similar
        # For now, using environment variables as fallback
        import os
        return os.getenv(key, "")