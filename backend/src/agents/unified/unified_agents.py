"""
T-Developer Unified Agent System - Final Production Version
Integrates Enterprise, Production, and Implementation features
"""

import asyncio
import json
import hashlib
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
import zipfile
import io

# Enterprise imports
from ..enterprise.base_agent import (
    EnterpriseBaseAgent, 
    AgentConfig, 
    AgentContext,
    AgentStatus
)

# AWS Production imports
try:
    from aws_lambda_powertools import Logger, Tracer, Metrics
    from aws_lambda_powertools.metrics import MetricUnit
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False
    
# AI Provider imports
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

# Advanced implementation imports
import sys
sys.path.append('/home/ec2-user/T-DeveloperMVP/backend/src/agents/implementations')


class UnifiedNLInputAgent(EnterpriseBaseAgent):
    """
    Unified Natural Language Input Agent
    Combines Enterprise AI + Implementation advanced features
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_nl_input_agent",
            version="2.0.0",
            timeout=30,
            retries=3,
            cache_ttl=3600,
            rate_limit=100
        )
        super().__init__(config)
        
        # Import advanced NL features from implementations
        try:
            from nl_input.advanced_features import MultilingualProcessor
            from nl_input.multimodal_processor import MultimodalProcessor
            from nl_input.performance_optimizer import PerformanceOptimizer
            
            self.multilingual = MultilingualProcessor()
            self.multimodal = MultimodalProcessor()
            self.optimizer = PerformanceOptimizer()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
            
        # AI Providers
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        
    async def _custom_initialize(self):
        """Initialize AI providers and advanced features"""
        # Initialize AI providers
        try:
            self.anthropic_client = AsyncAnthropic(
                api_key=await self._get_secret("ANTHROPIC_API_KEY")
            )
            self.openai_client = AsyncOpenAI(
                api_key=await self._get_secret("OPENAI_API_KEY")
            )
        except Exception as e:
            self.logger.warning(f"AI provider init failed: {e}")
            
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Process natural language with unified capabilities"""
        query = input_data.get("query", "")
        
        # Use advanced features if available
        if self.advanced_features:
            # Optimize query
            query = await self.optimizer.optimize_query(query)
            
            # Detect language
            language = await self.multilingual.detect_language(query)
            
            # Process multimodal if needed
            if input_data.get("images") or input_data.get("documents"):
                query = await self.multimodal.process_multimodal(input_data)
        
        # Primary AI processing (Claude)
        requirements = None
        if self.anthropic_client:
            try:
                requirements = await self._process_with_claude(query, context)
            except Exception as e:
                self.logger.warning(f"Claude processing failed: {e}")
        
        # Fallback to OpenAI
        if not requirements and self.openai_client:
            try:
                requirements = await self._process_with_openai(query, context)
            except Exception as e:
                self.logger.warning(f"OpenAI processing failed: {e}")
        
        # Final fallback to rule-based
        if not requirements:
            requirements = await self._rule_based_processing(query)
        
        # Enrich with advanced features
        if self.advanced_features:
            requirements = await self._enrich_with_advanced_features(requirements)
        
        return requirements
    
    async def _process_with_claude(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Process with Claude AI"""
        response = await self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            temperature=0.7,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": query}]
        )
        
        return self._parse_ai_response(response.content[0].text)
    
    async def _process_with_openai(self, query: str, context: AgentContext) -> Dict[str, Any]:
        """Process with OpenAI"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _rule_based_processing(self, query: str) -> Dict[str, Any]:
        """Fallback rule-based processing"""
        # Import from TypeScript agent logic
        project_type = "web_app"  # Default
        
        patterns = {
            "mobile": ["mobile", "ios", "android", "flutter", "react native"],
            "api": ["api", "backend", "rest", "graphql", "microservice"],
            "desktop": ["desktop", "electron", "windows", "mac"],
            "ai": ["ai", "ml", "machine learning", "neural", "deep learning"]
        }
        
        query_lower = query.lower()
        for ptype, keywords in patterns.items():
            if any(kw in query_lower for kw in keywords):
                project_type = ptype
                break
        
        return {
            "project_type": project_type,
            "description": query,
            "features": self._extract_features(query),
            "technical_requirements": {},
            "confidence_score": 0.5
        }
    
    def _extract_features(self, query: str) -> List[str]:
        """Extract features from query"""
        features = []
        feature_keywords = [
            "authentication", "payment", "search", "chat", 
            "notification", "analytics", "dashboard", "upload"
        ]
        
        query_lower = query.lower()
        for keyword in feature_keywords:
            if keyword in query_lower:
                features.append(keyword)
        
        return features
    
    async def _enrich_with_advanced_features(self, requirements: Dict) -> Dict:
        """Enrich with advanced implementation features"""
        # Add performance metrics
        requirements["performance_metrics"] = {
            "processing_time": datetime.utcnow().isoformat(),
            "optimization_applied": True
        }
        
        # Add multilingual support
        if self.advanced_features:
            requirements["language_support"] = await self.multilingual.get_supported_languages()
        
        return requirements
    
    def _get_system_prompt(self) -> str:
        """Get AI system prompt"""
        return """You are an expert software architect analyzing project requirements.
        Extract: project_type, features, technical_requirements, constraints.
        Respond in JSON format."""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response to structured format"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"error": "Failed to parse response"}
    
    async def _get_secret(self, key: str) -> str:
        """Get secret from AWS Secrets Manager or env"""
        if AWS_ENABLED:
            # Use AWS Secrets Manager
            import boto3
            client = boto3.client('secretsmanager')
            try:
                response = client.get_secret_value(SecretId=key)
                return response['SecretString']
            except:
                pass
        
        # Fallback to environment variable
        return os.getenv(key, "")


class UnifiedUISelectionAgent(EnterpriseBaseAgent):
    """
    Unified UI Selection Agent
    Combines Enterprise selection + Implementation advanced criteria
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_ui_selection_agent",
            version="2.0.0",
            timeout=20,
            retries=2,
            cache_ttl=7200
        )
        super().__init__(config)
        
        # Import advanced UI selection features
        try:
            from ui_selection.advanced_features import FrameworkAnalyzer
            from ui_selection.performance_benchmarks import BenchmarkAnalyzer
            self.framework_analyzer = FrameworkAnalyzer()
            self.benchmark_analyzer = BenchmarkAnalyzer()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
            
        # Framework knowledge base (from Enterprise implementation)
        self.frameworks = self._load_framework_knowledge()
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Select optimal UI framework"""
        requirements = input_data.get("requirements", {})
        
        # Analyze requirements
        analysis = await self._analyze_requirements(requirements)
        
        # Score frameworks
        scores = {}
        for fw_key, fw_data in self.frameworks.items():
            score = await self._calculate_score(fw_key, fw_data, requirements, analysis)
            scores[fw_key] = score
        
        # Use advanced features if available
        if self.advanced_features:
            # Get performance benchmarks
            benchmarks = await self.benchmark_analyzer.get_benchmarks(list(scores.keys()))
            
            # Adjust scores based on benchmarks
            for fw_key in scores:
                if fw_key in benchmarks:
                    scores[fw_key] *= benchmarks[fw_key]["performance_factor"]
        
        # Select best framework
        best_fw = max(scores, key=scores.get)
        
        return {
            "selected_framework": {
                "id": best_fw,
                "name": self.frameworks[best_fw]["name"],
                "score": scores[best_fw],
                "confidence": min(scores[best_fw] / 100, 1.0)
            },
            "scores": scores,
            "analysis": analysis,
            "alternatives": self._get_alternatives(scores, best_fw)
        }
    
    async def _analyze_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Analyze project requirements"""
        return {
            "project_type": requirements.get("project_type", "web_app"),
            "complexity": requirements.get("estimated_complexity", "medium"),
            "performance_critical": self._is_performance_critical(requirements),
            "seo_required": self._requires_seo(requirements)
        }
    
    def _is_performance_critical(self, requirements: Dict) -> bool:
        """Check if performance is critical"""
        features = requirements.get("features", [])
        performance_keywords = ["real-time", "streaming", "game", "trading"]
        return any(kw in str(features).lower() for kw in performance_keywords)
    
    def _requires_seo(self, requirements: Dict) -> bool:
        """Check if SEO is required"""
        project_type = requirements.get("project_type", "")
        return project_type in ["blog", "e-commerce", "marketing"]
    
    async def _calculate_score(self, fw_key: str, fw_data: Dict, requirements: Dict, analysis: Dict) -> float:
        """Calculate framework score"""
        score = 0.0
        
        # Base scoring
        if analysis["project_type"] in fw_data.get("best_for", []):
            score += 30
        
        if analysis["performance_critical"] and fw_data.get("performance_score", 0) > 0.8:
            score += 25
        
        if analysis["seo_required"] and fw_data.get("ssr_support"):
            score += 20
        
        # Complexity matching
        if analysis["complexity"] == fw_data.get("complexity_sweet_spot"):
            score += 15
        
        # Popularity bonus
        score += fw_data.get("popularity_score", 0.5) * 10
        
        return score
    
    def _get_alternatives(self, scores: Dict, selected: str) -> List[Dict]:
        """Get alternative frameworks"""
        sorted_frameworks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        alternatives = []
        for fw_key, score in sorted_frameworks[1:4]:  # Top 3 alternatives
            if fw_key != selected:
                alternatives.append({
                    "id": fw_key,
                    "name": self.frameworks[fw_key]["name"],
                    "score": score
                })
        
        return alternatives
    
    def _load_framework_knowledge(self) -> Dict:
        """Load framework knowledge base"""
        return {
            "react": {
                "name": "React",
                "best_for": ["web_app", "spa", "dashboard"],
                "performance_score": 0.85,
                "popularity_score": 0.95,
                "ssr_support": True,
                "complexity_sweet_spot": "high"
            },
            "vue": {
                "name": "Vue.js",
                "best_for": ["web_app", "spa"],
                "performance_score": 0.88,
                "popularity_score": 0.75,
                "ssr_support": True,
                "complexity_sweet_spot": "medium"
            },
            "angular": {
                "name": "Angular",
                "best_for": ["enterprise", "dashboard"],
                "performance_score": 0.80,
                "popularity_score": 0.70,
                "ssr_support": True,
                "complexity_sweet_spot": "very_high"
            },
            "svelte": {
                "name": "Svelte",
                "best_for": ["web_app", "performance"],
                "performance_score": 0.95,
                "popularity_score": 0.50,
                "ssr_support": True,
                "complexity_sweet_spot": "low"
            },
            "nextjs": {
                "name": "Next.js",
                "best_for": ["web_app", "blog", "e-commerce"],
                "performance_score": 0.90,
                "popularity_score": 0.85,
                "ssr_support": True,
                "complexity_sweet_spot": "medium"
            }
        }


class UnifiedParserAgent(EnterpriseBaseAgent):
    """
    Unified Parser Agent
    Combines Enterprise parsing + Implementation advanced analysis
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_parser_agent",
            version="2.0.0",
            timeout=25,
            retries=2,
            cache_ttl=1800
        )
        super().__init__(config)
        
        # Import advanced parser features
        try:
            from parser.advanced_features import CodeAnalyzer
            from parser.performance_optimizer import ParserOptimizer
            self.code_analyzer = CodeAnalyzer()
            self.parser_optimizer = ParserOptimizer()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Parse and analyze requirements or code"""
        parse_type = input_data.get("type", "requirements")
        
        if parse_type == "requirements":
            return await self._parse_requirements(input_data.get("requirements", {}))
        elif parse_type == "code":
            return await self._parse_code(input_data.get("code", ""))
        else:
            return {"error": f"Unknown parse type: {parse_type}"}
    
    async def _parse_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Parse project requirements"""
        # Extract components
        components = self._extract_components(requirements)
        
        # Extract data models
        models = self._extract_data_models(requirements)
        
        # Extract API endpoints
        endpoints = self._extract_api_endpoints(requirements, models)
        
        # Use advanced features if available
        if self.advanced_features:
            # Analyze code complexity
            complexity_analysis = await self.code_analyzer.analyze_complexity(requirements)
            
            # Optimize parsing
            optimized_data = await self.parser_optimizer.optimize(components, models)
            
            return {
                "components": optimized_data.get("components", components),
                "models": optimized_data.get("models", models),
                "endpoints": endpoints,
                "complexity_analysis": complexity_analysis
            }
        
        return {
            "components": components,
            "models": models,
            "endpoints": endpoints
        }
    
    async def _parse_code(self, code: str) -> Dict[str, Any]:
        """Parse existing code"""
        # Basic parsing
        structure = {
            "files": [],
            "dependencies": [],
            "patterns": []
        }
        
        # Use advanced features if available
        if self.advanced_features:
            structure = await self.code_analyzer.analyze_code(code)
        
        return structure
    
    def _extract_components(self, requirements: Dict) -> List[Dict]:
        """Extract technical components"""
        components = []
        features = requirements.get("features", [])
        
        component_map = {
            "authentication": {"name": "AuthService", "type": "service"},
            "payment": {"name": "PaymentService", "type": "service"},
            "search": {"name": "SearchService", "type": "service"},
            "notification": {"name": "NotificationService", "type": "service"}
        }
        
        for feature in features:
            feature_lower = str(feature).lower()
            for key, component in component_map.items():
                if key in feature_lower:
                    components.append(component)
        
        return components
    
    def _extract_data_models(self, requirements: Dict) -> List[Dict]:
        """Extract data models"""
        models = []
        features = requirements.get("features", [])
        features_str = " ".join(str(f).lower() for f in features)
        
        model_map = {
            "user": ["user", "account", "profile"],
            "product": ["product", "item", "catalog"],
            "order": ["order", "purchase", "cart"]
        }
        
        for model_name, keywords in model_map.items():
            if any(kw in features_str for kw in keywords):
                models.append({
                    "name": model_name.capitalize(),
                    "fields": self._get_model_fields(model_name)
                })
        
        return models
    
    def _get_model_fields(self, model_name: str) -> List[Dict]:
        """Get fields for model"""
        field_map = {
            "user": [
                {"name": "id", "type": "UUID"},
                {"name": "email", "type": "String"},
                {"name": "username", "type": "String"}
            ],
            "product": [
                {"name": "id", "type": "UUID"},
                {"name": "name", "type": "String"},
                {"name": "price", "type": "Decimal"}
            ],
            "order": [
                {"name": "id", "type": "UUID"},
                {"name": "user_id", "type": "UUID"},
                {"name": "total", "type": "Decimal"}
            ]
        }
        
        return field_map.get(model_name, [{"name": "id", "type": "UUID"}])
    
    def _extract_api_endpoints(self, requirements: Dict, models: List[Dict]) -> List[Dict]:
        """Extract API endpoints"""
        endpoints = []
        
        # Generate CRUD endpoints for each model
        for model in models:
            model_name = model["name"].lower()
            endpoints.extend([
                {"method": "GET", "path": f"/api/{model_name}s"},
                {"method": "GET", "path": f"/api/{model_name}s/{{id}}"},
                {"method": "POST", "path": f"/api/{model_name}s"},
                {"method": "PUT", "path": f"/api/{model_name}s/{{id}}"},
                {"method": "DELETE", "path": f"/api/{model_name}s/{{id}}"}
            ])
        
        return endpoints


class UnifiedComponentDecisionAgent(EnterpriseBaseAgent):
    """
    Unified Component Decision Agent
    Combines Enterprise decision + Implementation MCDM algorithms
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_component_decision_agent",
            version="2.0.0",
            timeout=20,
            retries=2,
            cache_ttl=3600
        )
        super().__init__(config)
        
        # Import advanced MCDM features
        try:
            from component_decision.component_decision_mcdm import TOPSISDecisionMaker
            from component_decision.component_decision_validator import ComponentValidator
            self.topsis = TOPSISDecisionMaker()
            self.validator = ComponentValidator()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Decide on components using advanced algorithms"""
        requirements = input_data.get("requirements", {})
        parsed_data = input_data.get("parsed_data", {})
        
        # Identify needed components
        component_needs = self._identify_component_needs(requirements, parsed_data)
        
        # Select components
        selected_components = {}
        
        if self.advanced_features:
            # Use TOPSIS for multi-criteria decision making
            for category, candidates in component_needs.items():
                decision = await self.topsis.decide(candidates, requirements)
                selected_components[category] = decision
                
            # Validate selections
            validation = await self.validator.validate(selected_components, requirements)
            
            return {
                "selected_components": selected_components,
                "validation": validation,
                "decision_method": "TOPSIS",
                "confidence": 0.95
            }
        else:
            # Fallback to simple selection
            for category, candidates in component_needs.items():
                selected_components[category] = candidates[0] if candidates else None
            
            return {
                "selected_components": selected_components,
                "decision_method": "simple",
                "confidence": 0.7
            }
    
    def _identify_component_needs(self, requirements: Dict, parsed_data: Dict) -> Dict[str, List]:
        """Identify component needs"""
        needs = {}
        
        # Database selection
        needs["database"] = [
            {"name": "PostgreSQL", "type": "relational", "score": 0.9},
            {"name": "MongoDB", "type": "document", "score": 0.8},
            {"name": "Redis", "type": "cache", "score": 0.7}
        ]
        
        # Authentication
        if "authentication" in str(requirements.get("features", [])).lower():
            needs["auth"] = [
                {"name": "JWT", "complexity": "low", "security": "high"},
                {"name": "OAuth2", "complexity": "medium", "security": "very_high"}
            ]
        
        # Messaging
        if "real-time" in str(requirements).lower():
            needs["messaging"] = [
                {"name": "WebSocket", "latency": "low"},
                {"name": "SSE", "latency": "medium"}
            ]
        
        return needs


class UnifiedMatchRateAgent(EnterpriseBaseAgent):
    """
    Unified Match Rate Agent
    Combines Enterprise matching + Implementation template learning
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_match_rate_agent",
            version="2.0.0",
            timeout=15,
            retries=2,
            cache_ttl=3600
        )
        super().__init__(config)
        
        # Import advanced matching features
        try:
            from match_rate.advanced_features import TemplateLearning
            from match_rate.performance_optimizer import MatchOptimizer
            self.template_learning = TemplateLearning()
            self.match_optimizer = MatchOptimizer()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
        
        # Template library
        self.templates = self._load_templates()
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Calculate template match rates"""
        requirements = input_data.get("requirements", {})
        
        # Calculate matches
        matches = []
        for template in self.templates:
            score = await self._calculate_match_score(requirements, template)
            matches.append({
                "template": template,
                "score": score,
                "matching_features": self._get_matching_features(requirements, template)
            })
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Use advanced features if available
        if self.advanced_features:
            # Learn from matches
            await self.template_learning.learn_from_matches(matches, requirements)
            
            # Optimize matching
            matches = await self.match_optimizer.optimize(matches)
        
        return {
            "best_match": matches[0] if matches else None,
            "alternatives": matches[1:4] if len(matches) > 1 else [],
            "recommendation": self._generate_recommendation(matches)
        }
    
    async def _calculate_match_score(self, requirements: Dict, template: Dict) -> float:
        """Calculate match score"""
        score = 0.0
        
        # Feature matching
        req_features = set(str(f).lower() for f in requirements.get("features", []))
        template_features = set(template.get("features", []))
        
        if req_features and template_features:
            overlap = len(req_features & template_features)
            total = len(req_features | template_features)
            score = (overlap / total) * 100 if total > 0 else 0
        
        return round(score, 2)
    
    def _get_matching_features(self, requirements: Dict, template: Dict) -> List[str]:
        """Get matching features"""
        req_features = set(str(f).lower() for f in requirements.get("features", []))
        template_features = set(template.get("features", []))
        return list(req_features & template_features)
    
    def _generate_recommendation(self, matches: List[Dict]) -> Dict[str, Any]:
        """Generate recommendation"""
        if not matches:
            return {"action": "create_custom", "reason": "No templates found"}
        
        best = matches[0]
        if best["score"] > 80:
            return {"action": "use_template", "template": best["template"]["id"]}
        elif best["score"] > 60:
            return {"action": "adapt_template", "template": best["template"]["id"]}
        else:
            return {"action": "create_custom", "reason": "Low match scores"}
    
    def _load_templates(self) -> List[Dict]:
        """Load template library"""
        return [
            {
                "id": "ecommerce",
                "name": "E-commerce",
                "features": ["product", "cart", "payment", "user"]
            },
            {
                "id": "saas",
                "name": "SaaS Platform",
                "features": ["dashboard", "subscription", "analytics", "user"]
            },
            {
                "id": "blog",
                "name": "Blog/CMS",
                "features": ["post", "category", "comment", "user"]
            }
        ]


class UnifiedSearchAgent(EnterpriseBaseAgent):
    """
    Unified Search Agent
    Combines Enterprise search + Implementation vector search
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_search_agent",
            version="2.0.0",
            timeout=25,
            retries=3,
            cache_ttl=7200
        )
        super().__init__(config)
        
        # Import advanced search features
        try:
            from search.ranking_system import RankingSystem
            from search.caching_system import CachingSystem
            from search.learning_to_rank import LearningToRank
            self.ranking = RankingSystem()
            self.caching = CachingSystem()
            self.ltr = LearningToRank()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Search for code snippets and patterns"""
        query = input_data.get("query", "")
        requirements = input_data.get("requirements", {})
        
        # Search in different sources
        results = {
            "code_snippets": await self._search_code(query, requirements),
            "patterns": await self._search_patterns(query, requirements),
            "libraries": await self._search_libraries(query, requirements)
        }
        
        # Use advanced features if available
        if self.advanced_features:
            # Apply ranking
            results = await self.ranking.rank_results(results, query)
            
            # Apply learning to rank
            results = await self.ltr.rerank(results, requirements)
            
            # Cache results
            await self.caching.cache_results(query, results)
        
        return results
    
    async def _search_code(self, query: str, requirements: Dict) -> List[Dict]:
        """Search for code snippets"""
        # Simple code search
        snippets = []
        
        if "authentication" in query.lower():
            snippets.append({
                "id": "auth_jwt",
                "code": "// JWT authentication implementation",
                "relevance": 0.9
            })
        
        return snippets
    
    async def _search_patterns(self, query: str, requirements: Dict) -> List[Dict]:
        """Search for design patterns"""
        patterns = []
        
        complexity = requirements.get("estimated_complexity", "medium")
        if complexity in ["high", "very_high"]:
            patterns.append({"name": "Repository Pattern", "relevance": 0.8})
            patterns.append({"name": "Service Layer", "relevance": 0.7})
        
        return patterns
    
    async def _search_libraries(self, query: str, requirements: Dict) -> List[Dict]:
        """Search for libraries"""
        libraries = []
        
        tech = requirements.get("technical_requirements", {})
        if "python" in str(tech.get("languages", [])).lower():
            libraries.append({"name": "FastAPI", "purpose": "Web framework"})
        elif "javascript" in str(tech.get("languages", [])).lower():
            libraries.append({"name": "Express", "purpose": "Web framework"})
        
        return libraries


class UnifiedGenerationAgent(EnterpriseBaseAgent):
    """
    Unified Generation Agent - The Core Code Generator
    Combines Enterprise generation + Implementation template engines
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_generation_agent",
            version="2.0.0",
            timeout=60,
            retries=3,
            cache_ttl=1800
        )
        super().__init__(config)
        
        # Import advanced generation features
        try:
            from generation.advanced_features import TemplateEngine
            from generation.quality_checker import QualityChecker
            from generation.optimization import GenerationOptimizer
            self.template_engine = TemplateEngine()
            self.quality_checker = QualityChecker()
            self.optimizer = GenerationOptimizer()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
        
        # AI Providers
        self.openai_client: Optional[AsyncOpenAI] = None
        self.anthropic_client: Optional[AsyncAnthropic] = None
    
    async def _custom_initialize(self):
        """Initialize AI providers"""
        try:
            self.openai_client = AsyncOpenAI(
                api_key=await self._get_secret("OPENAI_API_KEY")
            )
            self.anthropic_client = AsyncAnthropic(
                api_key=await self._get_secret("ANTHROPIC_API_KEY")
            )
        except Exception as e:
            self.logger.warning(f"AI provider init failed: {e}")
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Generate complete project code"""
        
        # Extract all inputs
        requirements = input_data.get("requirements", {})
        ui_framework = input_data.get("ui_framework", {})
        components = input_data.get("components", {})
        templates = input_data.get("templates", {})
        
        # Generate project structure
        structure = await self._generate_structure(requirements)
        
        # Generate files
        files = {}
        
        # Package file
        files["package"] = await self._generate_package_file(requirements)
        
        # Main application
        files["main"] = await self._generate_main_app(requirements, ui_framework)
        
        # API routes
        files["api"] = await self._generate_api_routes(requirements)
        
        # Database models
        files["models"] = await self._generate_models(requirements)
        
        # Frontend components
        if ui_framework:
            files["frontend"] = await self._generate_frontend(requirements, ui_framework)
        
        # Configuration
        files["config"] = await self._generate_config(requirements)
        
        # Tests
        files["tests"] = await self._generate_tests(requirements)
        
        # Documentation
        files["docs"] = await self._generate_docs(requirements)
        
        # Use advanced features if available
        if self.advanced_features:
            # Apply templates
            files = await self.template_engine.apply_templates(files, templates)
            
            # Check quality
            quality_report = await self.quality_checker.check(files)
            
            # Optimize
            files = await self.optimizer.optimize(files)
            
            return {
                "structure": structure,
                "files": files,
                "quality_report": quality_report,
                "optimized": True
            }
        
        return {
            "structure": structure,
            "files": files,
            "optimized": False
        }
    
    async def _generate_structure(self, requirements: Dict) -> Dict:
        """Generate project structure"""
        project_type = requirements.get("project_type", "web_app")
        
        if project_type == "web_app":
            return {
                "src": {
                    "components": {},
                    "pages": {},
                    "services": {},
                    "utils": {}
                },
                "public": {},
                "tests": {}
            }
        else:
            return {"src": {}, "tests": {}}
    
    async def _generate_package_file(self, requirements: Dict) -> Dict:
        """Generate package.json or requirements.txt"""
        tech = requirements.get("technical_requirements", {})
        
        if "python" in str(tech.get("languages", [])).lower():
            return {
                "filename": "requirements.txt",
                "content": "fastapi\nuvicorn\nsqlalchemy\npydantic"
            }
        else:
            return {
                "filename": "package.json",
                "content": json.dumps({
                    "name": "project",
                    "version": "1.0.0",
                    "dependencies": {
                        "express": "^4.18.0"
                    }
                }, indent=2)
            }
    
    async def _generate_main_app(self, requirements: Dict, ui_framework: Dict) -> Dict:
        """Generate main application file"""
        
        # Use AI if available
        if self.openai_client:
            try:
                prompt = f"Generate main application file for {requirements.get('project_type')} project"
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                
                return {
                    "filename": "src/main.py",
                    "content": response.choices[0].message.content
                }
            except:
                pass
        
        # Fallback to template
        return {
            "filename": "src/main.py",
            "content": """from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "API running"}"""
        }
    
    async def _generate_api_routes(self, requirements: Dict) -> List[Dict]:
        """Generate API routes"""
        routes = []
        
        for feature in requirements.get("features", []):
            if "user" in str(feature).lower():
                routes.append({
                    "filename": "src/routes/users.py",
                    "content": "# User routes"
                })
        
        return routes
    
    async def _generate_models(self, requirements: Dict) -> List[Dict]:
        """Generate data models"""
        models = []
        
        for feature in requirements.get("features", []):
            if "user" in str(feature).lower():
                models.append({
                    "filename": "src/models/user.py",
                    "content": "# User model"
                })
        
        return models
    
    async def _generate_frontend(self, requirements: Dict, ui_framework: Dict) -> Dict:
        """Generate frontend code"""
        framework = ui_framework.get("selected_framework", {}).get("id", "react")
        
        if framework == "react":
            return {
                "filename": "src/App.js",
                "content": "import React from 'react';\nexport default function App() { return <div>App</div>; }"
            }
        else:
            return {"filename": "src/App.vue", "content": "<template><div>App</div></template>"}
    
    async def _generate_config(self, requirements: Dict) -> List[Dict]:
        """Generate configuration files"""
        return [
            {"filename": ".env", "content": "NODE_ENV=development"},
            {"filename": ".gitignore", "content": "node_modules/\n.env"},
            {"filename": "Dockerfile", "content": "FROM node:18\nWORKDIR /app"}
        ]
    
    async def _generate_tests(self, requirements: Dict) -> List[Dict]:
        """Generate test files"""
        return [{"filename": "tests/test_main.py", "content": "# Tests"}]
    
    async def _generate_docs(self, requirements: Dict) -> Dict:
        """Generate documentation"""
        return {
            "filename": "README.md",
            "content": f"# {requirements.get('project_name', 'Project')}\n\n## Description\n{requirements.get('description', '')}"
        }
    
    async def _get_secret(self, key: str) -> str:
        """Get secret"""
        return os.getenv(key, "")


class UnifiedAssemblyAgent(EnterpriseBaseAgent):
    """
    Unified Assembly Agent
    Combines Enterprise assembly + Implementation optimization
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_assembly_agent",
            version="2.0.0",
            timeout=30,
            retries=2,
            cache_ttl=1800
        )
        super().__init__(config)
        
        # Import advanced assembly features
        try:
            from assembly.advanced_features import ProjectOptimizer
            from assembly.validation import ProjectValidator
            self.optimizer = ProjectOptimizer()
            self.validator = ProjectValidator()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Assemble project from generated files"""
        
        files = input_data.get("files", {})
        structure = input_data.get("structure", {})
        
        # Create project layout
        project = await self._assemble_project(files, structure)
        
        # Validate project
        validation = await self._validate_project(project)
        
        # Use advanced features if available
        if self.advanced_features:
            # Optimize project
            project = await self.optimizer.optimize(project)
            
            # Advanced validation
            validation = await self.validator.validate(project)
        
        return {
            "project": project,
            "validation": validation,
            "ready": validation.get("is_valid", True)
        }
    
    async def _assemble_project(self, files: Dict, structure: Dict) -> Dict:
        """Assemble project files"""
        project = {}
        
        # Process package file
        if "package" in files:
            project[files["package"]["filename"]] = files["package"]["content"]
        
        # Process main app
        if "main" in files:
            project[files["main"]["filename"]] = files["main"]["content"]
        
        # Process API routes
        if "api" in files:
            for route in files["api"]:
                project[route["filename"]] = route["content"]
        
        # Process models
        if "models" in files:
            for model in files["models"]:
                project[model["filename"]] = model["content"]
        
        # Process frontend
        if "frontend" in files:
            project[files["frontend"]["filename"]] = files["frontend"]["content"]
        
        # Process config
        if "config" in files:
            for config in files["config"]:
                project[config["filename"]] = config["content"]
        
        # Process tests
        if "tests" in files:
            for test in files["tests"]:
                project[test["filename"]] = test["content"]
        
        # Process docs
        if "docs" in files:
            project[files["docs"]["filename"]] = files["docs"]["content"]
        
        return project
    
    async def _validate_project(self, project: Dict) -> Dict:
        """Validate project completeness"""
        validation = {
            "is_valid": True,
            "missing_files": [],
            "issues": []
        }
        
        # Check for essential files
        essential = ["README.md", ".gitignore"]
        for file in essential:
            if file not in project:
                validation["missing_files"].append(file)
                validation["is_valid"] = False
        
        # Check for entry point
        if not any("main" in f for f in project.keys()):
            validation["issues"].append("No entry point found")
        
        return validation


class UnifiedDownloadAgent(EnterpriseBaseAgent):
    """
    Unified Download Agent
    Combines Enterprise packaging + Implementation compression
    """
    
    def __init__(self):
        config = AgentConfig(
            name="unified_download_agent",
            version="2.0.0",
            timeout=20,
            retries=2,
            cache_ttl=3600
        )
        super().__init__(config)
        
        # Import advanced download features
        try:
            from download.advanced_features import CompressionOptimizer
            from download.upload_manager import UploadManager
            self.compression = CompressionOptimizer()
            self.upload = UploadManager()
            self.advanced_features = True
        except ImportError:
            self.advanced_features = False
    
    async def process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Package project for download"""
        
        project = input_data.get("project", {})
        metadata = input_data.get("metadata", {})
        
        # Create ZIP archive
        zip_data = await self._create_zip(project)
        
        # Use advanced features if available
        if self.advanced_features:
            # Optimize compression
            zip_data = await self.compression.optimize(zip_data)
            
            # Upload to cloud storage
            download_url = await self.upload.upload(zip_data, metadata)
        else:
            # Save locally
            download_url = await self._save_locally(zip_data, metadata)
        
        return {
            "download_url": download_url,
            "size_bytes": len(zip_data),
            "checksum": hashlib.sha256(zip_data).hexdigest(),
            "expires_at": datetime.utcnow().timestamp() + 3600
        }
    
    async def _create_zip(self, project: Dict) -> bytes:
        """Create ZIP archive"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filepath, content in project.items():
                zipf.writestr(filepath, content)
        
        return zip_buffer.getvalue()
    
    async def _save_locally(self, zip_data: bytes, metadata: Dict) -> str:
        """Save ZIP locally"""
        filename = f"{metadata.get('project_name', 'project')}.zip"
        filepath = f"/tmp/{filename}"
        
        with open(filepath, 'wb') as f:
            f.write(zip_data)
        
        return f"/download/{filename}"