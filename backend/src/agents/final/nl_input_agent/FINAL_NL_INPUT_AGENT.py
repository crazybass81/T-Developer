"""
Final Production NL Input Agent
Complete integration of all NL Input functionalities
"""

import asyncio
import json
import re
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os

# AI Provider Imports
try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# AWS Imports
try:
    from aws_lambda_powertools import Logger, Tracer, Metrics
    from aws_lambda_powertools.metrics import MetricUnit
    import boto3
    AWS_AVAILABLE = True
    logger = Logger()
    tracer = Tracer()
    metrics = Metrics()
except ImportError:
    AWS_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)

# Redis for caching
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Import advanced features from implementation modules
# Handle both module and script execution
_imported_modules = {}

try:
    # Try relative imports (when used as module)
    from .multilingual_processor import MultilingualProcessor
    from .multimodal_processor import MultimodalProcessor
    from .performance_optimizer import PerformanceOptimizer
    from .nl_performance_cache import PerformanceCache
    from .nl_priority_analyzer import PriorityAnalyzer
    from .requirement_prioritizer import RequirementPrioritizer
    from .template_learner import TemplateLearner
    from .context_manager import ContextManager
    from .nl_intent_analyzer import IntentAnalyzer
    from .nl_domain_specific import DomainSpecificProcessor
    MODULES_AVAILABLE = True
except ImportError:
    try:
        # Try absolute imports (when run as script)
        from multilingual_processor import MultilingualProcessor
        from multimodal_processor import MultimodalProcessor
        from performance_optimizer import PerformanceOptimizer
        from nl_performance_cache import PerformanceCache
        from nl_priority_analyzer import PriorityAnalyzer
        from requirement_prioritizer import RequirementPrioritizer
        from template_learner import TemplateLearner
        from context_manager import ContextManager
        from nl_intent_analyzer import IntentAnalyzer
        from nl_domain_specific import DomainSpecificProcessor
        MODULES_AVAILABLE = True
    except ImportError:
        # Modules not available - will use basic processing only
        MODULES_AVAILABLE = False
        MultilingualProcessor = None
        MultimodalProcessor = None
        PerformanceOptimizer = None
        PerformanceCache = None
        PriorityAnalyzer = None
        RequirementPrioritizer = None
        TemplateLearner = None
        ContextManager = None
        IntentAnalyzer = None
        DomainSpecificProcessor = None


@dataclass
class ProjectRequirements:
    """Structured project requirements"""
    project_type: str
    project_name: str
    description: str
    features: List[str]
    technical_requirements: Dict[str, Any]
    non_functional_requirements: Dict[str, Any]
    constraints: List[str]
    estimated_complexity: str
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProcessingMode(Enum):
    """Processing modes for different scenarios"""
    FAST = "fast"  # Quick processing with basic features
    STANDARD = "standard"  # Normal processing with caching
    ADVANCED = "advanced"  # Full processing with all features
    ENTERPRISE = "enterprise"  # Enterprise features with monitoring


class FinalNLInputAgent:
    """
    Final Production NL Input Agent
    Integrates all NL processing capabilities
    """
    
    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.STANDARD,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Final NL Input Agent
        
        Args:
            mode: Processing mode
            config: Optional configuration
        """
        self.mode = mode
        self.config = config or {}
        
        # Core settings
        self.name = "final_nl_input_agent"
        self.version = "3.0.0"
        self.timeout = self.config.get("timeout", 30)
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        
        # AI Providers
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        
        # Redis Cache
        self.redis_client: Optional[redis.Redis] = None
        
        # Advanced Processors
        self.multilingual: Optional[MultilingualProcessor] = None
        self.multimodal: Optional[MultimodalProcessor] = None
        self.optimizer: Optional[PerformanceOptimizer] = None
        self.cache: Optional[PerformanceCache] = None
        self.priority_analyzer: Optional[PriorityAnalyzer] = None
        self.requirement_prioritizer: Optional[RequirementPrioritizer] = None
        self.template_learner: Optional[TemplateLearner] = None
        self.context_manager: Optional[ContextManager] = None
        self.intent_analyzer: Optional[IntentAnalyzer] = None
        self.domain_processor: Optional[DomainSpecificProcessor] = None
        
        # Metrics
        self.processing_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"Initialized {self.name} v{self.version} in {mode} mode")
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing NL Input Agent components")
        
        # Initialize AI Providers
        await self._initialize_ai_providers()
        
        # Initialize Redis Cache
        await self._initialize_cache()
        
        # Initialize Advanced Processors based on mode
        await self._initialize_processors()
        
        logger.info("NL Input Agent initialization complete")
    
    async def _initialize_ai_providers(self):
        """Initialize AI providers"""
        # Anthropic Claude
        if ANTHROPIC_AVAILABLE:
            try:
                api_key = await self._get_secret("ANTHROPIC_API_KEY")
                if api_key:
                    self.anthropic_client = AsyncAnthropic(api_key=api_key)
                    logger.info("Anthropic Claude initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic: {e}")
        
        # OpenAI
        if OPENAI_AVAILABLE:
            try:
                api_key = await self._get_secret("OPENAI_API_KEY")
                if api_key:
                    self.openai_client = AsyncOpenAI(api_key=api_key)
                    logger.info("OpenAI initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
    
    async def _initialize_cache(self):
        """Initialize Redis cache"""
        if REDIS_AVAILABLE and self.mode != ProcessingMode.FAST:
            try:
                redis_url = self.config.get("redis_url", "redis://localhost:6379")
                self.redis_client = await redis.from_url(redis_url)
                await self.redis_client.ping()
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
    
    async def _initialize_processors(self):
        """Initialize advanced processors based on mode"""
        if self.mode in [ProcessingMode.ADVANCED, ProcessingMode.ENTERPRISE]:
            if MODULES_AVAILABLE:
                try:
                    # Essential processors
                    self.multilingual = MultilingualProcessor() if MultilingualProcessor else None
                    self.multimodal = MultimodalProcessor() if MultimodalProcessor else None
                    self.optimizer = PerformanceOptimizer() if PerformanceOptimizer else None
                    self.intent_analyzer = IntentAnalyzer() if IntentAnalyzer else None
                    
                    # Advanced processors
                    self.priority_analyzer = PriorityAnalyzer() if PriorityAnalyzer else None
                    self.requirement_prioritizer = RequirementPrioritizer() if RequirementPrioritizer else None
                    self.template_learner = TemplateLearner() if TemplateLearner else None
                    self.context_manager = ContextManager() if ContextManager else None
                    self.domain_processor = DomainSpecificProcessor() if DomainSpecificProcessor else None
                    
                    # Performance cache
                    self.cache = PerformanceCache() if PerformanceCache else None
                    
                    logger.info("Advanced processors initialized")
                except Exception as e:
                    logger.warning(f"Some advanced processors failed to initialize: {e}")
            else:
                logger.warning("Advanced modules not available - using basic processing")
    
    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ProjectRequirements:
        """
        Main processing method for natural language input
        
        Args:
            query: Natural language project description
            context: Optional context information
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            ProjectRequirements: Structured project requirements
        """
        start_time = datetime.utcnow()
        
        # Create processing context
        proc_context = {
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": start_time.isoformat(),
            "mode": self.mode.value,
            **(context or {})
        }
        
        logger.info(
            "Processing NL query",
            extra={
                "query_length": len(query),
                "mode": self.mode.value,
                "user_id": user_id
            }
        )
        
        try:
            # Check cache first
            if self.mode != ProcessingMode.FAST:
                cached_result = await self._check_cache(query, proc_context)
                if cached_result:
                    logger.info("Cache hit - returning cached result")
                    self.cache_hits += 1
                    return cached_result
                self.cache_misses += 1
            
            # Pre-processing
            processed_query = await self._preprocess_query(query, proc_context)
            
            # Main processing based on mode
            if self.mode == ProcessingMode.FAST:
                requirements = await self._fast_processing(processed_query, proc_context)
            elif self.mode == ProcessingMode.STANDARD:
                requirements = await self._standard_processing(processed_query, proc_context)
            elif self.mode == ProcessingMode.ADVANCED:
                requirements = await self._advanced_processing(processed_query, proc_context)
            else:  # ENTERPRISE
                requirements = await self._enterprise_processing(processed_query, proc_context)
            
            # Post-processing
            requirements = await self._postprocess_requirements(requirements, proc_context)
            
            # Cache result
            if self.mode != ProcessingMode.FAST:
                await self._cache_result(query, requirements, proc_context)
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_metrics(processing_time, requirements)
            
            self.processing_count += 1
            
            logger.info(
                "NL processing complete",
                extra={
                    "processing_time": processing_time,
                    "project_type": requirements.project_type,
                    "confidence": requirements.confidence_score
                }
            )
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error processing NL query: {e}", exc_info=True)
            # Return basic fallback result
            return await self._fallback_processing(query)
    
    async def _preprocess_query(self, query: str, context: Dict) -> str:
        """Preprocess the query"""
        # Basic cleaning
        query = query.strip()
        
        # Advanced preprocessing if available
        if self.optimizer:
            query = await self.optimizer.optimize_query(query)
        
        # Language detection and translation if needed
        if self.multilingual:
            language = await self.multilingual.detect_language(query)
            if language != "en":
                query = await self.multilingual.translate_to_english(query)
                context["original_language"] = language
        
        return query
    
    async def _fast_processing(self, query: str, context: Dict) -> ProjectRequirements:
        """Fast processing mode - rule-based only"""
        return await self._rule_based_extraction(query)
    
    async def _standard_processing(self, query: str, context: Dict) -> ProjectRequirements:
        """Standard processing mode - AI with fallback"""
        # Try AI processing
        if self.anthropic_client:
            try:
                return await self._process_with_claude(query, context)
            except Exception as e:
                logger.warning(f"Claude processing failed: {e}")
        
        if self.openai_client:
            try:
                return await self._process_with_openai(query, context)
            except Exception as e:
                logger.warning(f"OpenAI processing failed: {e}")
        
        # Fallback to rule-based
        return await self._rule_based_extraction(query)
    
    async def _advanced_processing(self, query: str, context: Dict) -> ProjectRequirements:
        """Advanced processing mode - full feature set"""
        # Intent analysis
        intent = None
        if self.intent_analyzer:
            intent = await self.intent_analyzer.analyze(query)
            context["intent"] = intent
        
        # Domain-specific processing
        if self.domain_processor and intent:
            domain_enhanced = await self.domain_processor.process(query, intent.get("domain"))
            if domain_enhanced:
                query = domain_enhanced
        
        # Context enhancement
        if self.context_manager:
            enhanced_context = await self.context_manager.enhance_context(query, context)
            context.update(enhanced_context)
        
        # Standard AI processing
        requirements = await self._standard_processing(query, context)
        
        # Priority analysis
        if self.priority_analyzer:
            priorities = await self.priority_analyzer.analyze(requirements)
            requirements.metadata["priorities"] = priorities
        
        # Template learning
        if self.template_learner:
            await self.template_learner.learn_from_requirements(requirements)
        
        return requirements
    
    async def _enterprise_processing(self, query: str, context: Dict) -> ProjectRequirements:
        """Enterprise processing mode - full features with monitoring"""
        # Add tracing
        span_context = {"query_preview": query[:100], "mode": "enterprise"}
        
        if AWS_AVAILABLE:
            with tracer.capture_method(capture_response=False) as span:
                span.add_metadata("query_length", len(query))
                requirements = await self._advanced_processing(query, context)
                span.add_metadata("project_type", requirements.project_type)
        else:
            requirements = await self._advanced_processing(query, context)
        
        # Add enterprise metadata
        requirements.metadata["processing_mode"] = "enterprise"
        requirements.metadata["compliance"] = await self._check_compliance(requirements)
        
        return requirements
    
    async def _process_with_claude(self, query: str, context: Dict) -> ProjectRequirements:
        """Process with Anthropic Claude"""
        system_prompt = self._get_claude_system_prompt()
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze this project request and extract structured requirements:\n\n{query}"
                }
            ]
        )
        
        # Parse response
        result = self._parse_ai_response(response.content[0].text)
        return self._create_requirements_from_dict(result)
    
    async def _process_with_openai(self, query: str, context: Dict) -> ProjectRequirements:
        """Process with OpenAI"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": self._get_openai_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"Analyze this project request:\n\n{query}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4096
        )
        
        result = json.loads(response.choices[0].message.content)
        return self._create_requirements_from_dict(result)
    
    async def _rule_based_extraction(self, query: str) -> ProjectRequirements:
        """Rule-based requirement extraction"""
        query_lower = query.lower()
        
        # Project type detection
        project_type = self._detect_project_type(query_lower)
        
        # Feature extraction
        features = self._extract_features(query_lower)
        
        # Technical requirements
        tech_reqs = self._extract_technical_requirements(query_lower)
        
        # Complexity estimation
        complexity = self._estimate_complexity(features, tech_reqs)
        
        # Project name extraction
        project_name = self._extract_project_name(query)
        
        return ProjectRequirements(
            project_type=project_type,
            project_name=project_name,
            description=query[:500],
            features=features,
            technical_requirements=tech_reqs,
            non_functional_requirements=self._extract_nfr(query_lower),
            constraints=self._extract_constraints(query_lower),
            estimated_complexity=complexity,
            confidence_score=0.6  # Lower confidence for rule-based
        )
    
    def _detect_project_type(self, query: str) -> str:
        """Detect project type from query"""
        type_patterns = {
            "web_app": ["web app", "website", "web application", "portal", "dashboard"],
            "mobile_app": ["mobile app", "ios", "android", "flutter", "react native"],
            "api": ["api", "rest", "graphql", "backend", "microservice"],
            "desktop": ["desktop", "electron", "windows app", "mac app"],
            "cli": ["cli", "command line", "terminal", "console"],
            "ai_ml": ["ai", "machine learning", "ml", "neural", "deep learning"],
            "data_pipeline": ["etl", "data pipeline", "data processing", "analytics"],
            "blockchain": ["blockchain", "smart contract", "web3", "dapp"],
            "iot": ["iot", "embedded", "arduino", "raspberry pi"],
            "game": ["game", "unity", "unreal", "godot"]
        }
        
        for ptype, patterns in type_patterns.items():
            if any(pattern in query for pattern in patterns):
                return ptype
        
        return "web_app"  # Default
    
    def _extract_features(self, query: str) -> List[str]:
        """Extract features from query"""
        features = []
        
        feature_patterns = {
            "authentication": ["login", "auth", "signin", "signup", "user account"],
            "payment": ["payment", "billing", "subscription", "checkout", "stripe"],
            "search": ["search", "filter", "find", "query"],
            "chat": ["chat", "messaging", "conversation", "real-time"],
            "notification": ["notification", "alert", "email", "push"],
            "analytics": ["analytics", "dashboard", "metrics", "reporting"],
            "upload": ["upload", "file", "attachment", "media"],
            "social": ["social", "share", "comment", "like", "follow"],
            "admin": ["admin", "management", "crud", "backend"],
            "api": ["api", "integration", "webhook", "endpoint"]
        }
        
        for feature, patterns in feature_patterns.items():
            if any(pattern in query for pattern in patterns):
                features.append(feature)
        
        return features
    
    def _extract_technical_requirements(self, query: str) -> Dict[str, Any]:
        """Extract technical requirements"""
        tech_reqs = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud": [],
            "tools": []
        }
        
        # Language detection
        languages = {
            "python": ["python", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "nodejs"],
            "typescript": ["typescript", "ts"],
            "java": ["java", "spring"],
            "go": ["golang", "go "],
            "rust": ["rust"],
            "csharp": ["c#", "dotnet", ".net"]
        }
        
        for lang, patterns in languages.items():
            if any(pattern in query for pattern in patterns):
                tech_reqs["languages"].append(lang)
        
        # Framework detection
        frameworks = {
            "react": ["react", "nextjs", "next.js"],
            "vue": ["vue", "nuxt"],
            "angular": ["angular"],
            "django": ["django"],
            "flask": ["flask"],
            "fastapi": ["fastapi"],
            "express": ["express"],
            "spring": ["spring"]
        }
        
        for fw, patterns in frameworks.items():
            if any(pattern in query for pattern in patterns):
                tech_reqs["frameworks"].append(fw)
        
        # Database detection
        databases = {
            "postgresql": ["postgres", "postgresql"],
            "mysql": ["mysql"],
            "mongodb": ["mongo", "mongodb"],
            "redis": ["redis"],
            "elasticsearch": ["elastic", "elasticsearch"]
        }
        
        for db, patterns in databases.items():
            if any(pattern in query for pattern in patterns):
                tech_reqs["databases"].append(db)
        
        # Cloud provider detection
        cloud_providers = {
            "aws": ["aws", "amazon"],
            "gcp": ["gcp", "google cloud"],
            "azure": ["azure"],
            "vercel": ["vercel"],
            "netlify": ["netlify"]
        }
        
        for provider, patterns in cloud_providers.items():
            if any(pattern in query for pattern in patterns):
                tech_reqs["cloud"].append(provider)
        
        # Set defaults if empty
        if not tech_reqs["languages"]:
            tech_reqs["languages"] = ["python", "javascript"]
        if not tech_reqs["databases"]:
            tech_reqs["databases"] = ["postgresql"]
        
        return tech_reqs
    
    def _extract_nfr(self, query: str) -> Dict[str, Any]:
        """Extract non-functional requirements"""
        nfr = {
            "performance": {},
            "security": [],
            "scalability": {},
            "usability": {}
        }
        
        # Performance requirements
        if "fast" in query or "performance" in query:
            nfr["performance"]["response_time"] = "< 200ms"
        if "real-time" in query:
            nfr["performance"]["latency"] = "< 100ms"
        
        # Security requirements
        if "secure" in query or "security" in query:
            nfr["security"].append("encryption")
            nfr["security"].append("authentication")
        if "compliant" in query or "compliance" in query:
            nfr["security"].append("compliance")
        
        # Scalability
        if "scalable" in query or "scale" in query:
            nfr["scalability"]["horizontal"] = True
            nfr["scalability"]["auto_scaling"] = True
        
        # Usability
        if "user-friendly" in query or "intuitive" in query:
            nfr["usability"]["user_friendly"] = True
        if "mobile" in query or "responsive" in query:
            nfr["usability"]["responsive"] = True
        
        return nfr
    
    def _extract_constraints(self, query: str) -> List[str]:
        """Extract project constraints"""
        constraints = []
        
        # Timeline constraints
        if "urgent" in query or "asap" in query:
            constraints.append("urgent_timeline")
        if "week" in query:
            constraints.append("short_timeline")
        
        # Budget constraints
        if "budget" in query or "cheap" in query or "low cost" in query:
            constraints.append("budget_constraint")
        
        # Technical constraints
        if "existing" in query:
            constraints.append("existing_system_integration")
        if "legacy" in query:
            constraints.append("legacy_system_support")
        
        return constraints
    
    def _estimate_complexity(self, features: List[str], tech_reqs: Dict) -> str:
        """Estimate project complexity"""
        score = 0
        
        # Feature complexity
        score += len(features) * 2
        
        # Technical complexity
        score += len(tech_reqs.get("languages", [])) * 1
        score += len(tech_reqs.get("frameworks", [])) * 2
        score += len(tech_reqs.get("databases", [])) * 2
        
        # Determine complexity level
        if score < 5:
            return "low"
        elif score < 10:
            return "medium"
        elif score < 20:
            return "high"
        else:
            return "very_high"
    
    def _extract_project_name(self, query: str) -> str:
        """Extract project name from query"""
        # Look for quoted strings
        import re
        quoted = re.findall(r'"([^"]*)"', query)
        if quoted:
            return quoted[0]
        
        # Look for patterns like "called X" or "named X"
        named = re.search(r'(?:called|named)\s+(\w+)', query, re.IGNORECASE)
        if named:
            return named.group(1)
        
        # Look for "X app" or "X platform"
        app_name = re.search(r'(\w+)\s+(?:app|platform|system|application)', query, re.IGNORECASE)
        if app_name:
            return app_name.group(1)
        
        return "MyProject"
    
    async def _postprocess_requirements(
        self,
        requirements: ProjectRequirements,
        context: Dict
    ) -> ProjectRequirements:
        """Post-process requirements"""
        # Add metadata
        requirements.metadata.update({
            "processing_mode": self.mode.value,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_version": self.version
        })
        
        # Priority analysis if available
        if self.requirement_prioritizer:
            priorities = await self.requirement_prioritizer.prioritize(requirements)
            requirements.metadata["feature_priorities"] = priorities
        
        # Confidence adjustment
        if self.mode == ProcessingMode.ENTERPRISE:
            requirements.confidence_score = min(requirements.confidence_score * 1.1, 1.0)
        
        return requirements
    
    async def _check_cache(self, query: str, context: Dict) -> Optional[ProjectRequirements]:
        """Check cache for existing result"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(query, context)
            cached = await self.redis_client.get(cache_key)
            
            if cached:
                data = json.loads(cached)
                return self._create_requirements_from_dict(data)
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    async def _cache_result(
        self,
        query: str,
        requirements: ProjectRequirements,
        context: Dict
    ):
        """Cache the result"""
        if not self.redis_client:
            return
        
        try:
            cache_key = self._generate_cache_key(query, context)
            data = self._requirements_to_dict(requirements)
            
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
    
    def _generate_cache_key(self, query: str, context: Dict) -> str:
        """Generate cache key"""
        key_data = {
            "query": query,
            "mode": self.mode.value,
            "version": self.version
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"nl_input:{hashlib.sha256(key_string.encode()).hexdigest()}"
    
    async def _record_metrics(self, processing_time: float, requirements: ProjectRequirements):
        """Record processing metrics"""
        if AWS_AVAILABLE:
            metrics.add_metric(name="NLProcessingTime", unit=MetricUnit.Seconds, value=processing_time)
            metrics.add_metric(name="NLProcessingCount", unit=MetricUnit.Count, value=1)
            metrics.add_metadata("project_type", requirements.project_type)
            metrics.add_metadata("confidence", requirements.confidence_score)
    
    async def _check_compliance(self, requirements: ProjectRequirements) -> Dict[str, bool]:
        """Check compliance requirements"""
        compliance = {
            "gdpr": False,
            "hipaa": False,
            "pci": False,
            "sox": False
        }
        
        # Check for compliance keywords
        desc_lower = requirements.description.lower()
        
        if "gdpr" in desc_lower or "data protection" in desc_lower:
            compliance["gdpr"] = True
        if "hipaa" in desc_lower or "healthcare" in desc_lower:
            compliance["hipaa"] = True
        if "payment" in desc_lower or "pci" in desc_lower:
            compliance["pci"] = True
        if "financial" in desc_lower or "sox" in desc_lower:
            compliance["sox"] = True
        
        return compliance
    
    async def _fallback_processing(self, query: str) -> ProjectRequirements:
        """Fallback processing for error cases"""
        return ProjectRequirements(
            project_type="unknown",
            project_name="Project",
            description=query[:200],
            features=[],
            technical_requirements={},
            non_functional_requirements={},
            constraints=[],
            estimated_complexity="medium",
            confidence_score=0.1,
            metadata={"fallback": True}
        )
    
    def _get_claude_system_prompt(self) -> str:
        """Get Claude system prompt"""
        return """You are an expert software architect and requirements analyst. 
        Analyze the user's project request and extract detailed, structured requirements.
        
        Extract and provide:
        1. Project type (web_app, mobile_app, api, desktop, cli, ai_ml, etc.)
        2. Project name
        3. Detailed description
        4. List of features
        5. Technical requirements (languages, frameworks, databases)
        6. Non-functional requirements (performance, security, scalability)
        7. Constraints
        8. Estimated complexity (low, medium, high, very_high)
        
        Respond with a JSON object containing all these fields."""
    
    def _get_openai_system_prompt(self) -> str:
        """Get OpenAI system prompt"""
        return """You are an expert software architect and requirements analyst.
        Extract structured project requirements from the user's request.
        
        Return a JSON object with:
        - project_type: Type of project
        - project_name: Name of the project
        - description: Project description
        - features: Array of features
        - technical_requirements: Object with languages, frameworks, databases
        - non_functional_requirements: Object with performance, security, etc.
        - constraints: Array of constraints
        - estimated_complexity: Complexity level
        
        Be thorough and specific in your analysis."""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response to dictionary"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            
            # Try direct parsing
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            return {}
    
    def _create_requirements_from_dict(self, data: Dict[str, Any]) -> ProjectRequirements:
        """Create ProjectRequirements from dictionary"""
        return ProjectRequirements(
            project_type=data.get("project_type", "web_app"),
            project_name=data.get("project_name", "Project"),
            description=data.get("description", ""),
            features=data.get("features", []),
            technical_requirements=data.get("technical_requirements", {}),
            non_functional_requirements=data.get("non_functional_requirements", {}),
            constraints=data.get("constraints", []),
            estimated_complexity=data.get("estimated_complexity", "medium"),
            confidence_score=data.get("confidence_score", 0.8),
            metadata=data.get("metadata", {})
        )
    
    def _requirements_to_dict(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Convert ProjectRequirements to dictionary"""
        return {
            "project_type": requirements.project_type,
            "project_name": requirements.project_name,
            "description": requirements.description,
            "features": requirements.features,
            "technical_requirements": requirements.technical_requirements,
            "non_functional_requirements": requirements.non_functional_requirements,
            "constraints": requirements.constraints,
            "estimated_complexity": requirements.estimated_complexity,
            "confidence_score": requirements.confidence_score,
            "metadata": requirements.metadata
        }
    
    async def _get_secret(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager or environment"""
        if AWS_AVAILABLE:
            try:
                client = boto3.client('secretsmanager')
                response = client.get_secret_value(SecretId=key)
                return response['SecretString']
            except Exception:
                pass
        
        # Fallback to environment variable
        return os.getenv(key)
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up NL Input Agent")
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Cleanup processors
        if self.cache:
            await self.cache.cleanup()
        
        logger.info("NL Input Agent cleanup complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the agent"""
        health = {
            "status": "healthy",
            "name": self.name,
            "version": self.version,
            "mode": self.mode.value,
            "components": {}
        }
        
        # Check AI providers
        health["components"]["anthropic"] = "available" if self.anthropic_client else "unavailable"
        health["components"]["openai"] = "available" if self.openai_client else "unavailable"
        
        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health["components"]["redis"] = "connected"
            except:
                health["components"]["redis"] = "disconnected"
        else:
            health["components"]["redis"] = "not_configured"
        
        # Check advanced processors
        health["components"]["advanced_processors"] = (
            "enabled" if self.multilingual else "disabled"
        )
        
        # Statistics
        health["statistics"] = {
            "total_processed": self.processing_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0
            )
        }
        
        return health


# Convenience functions for different use cases
async def create_fast_processor() -> FinalNLInputAgent:
    """Create a fast processor for quick processing"""
    agent = FinalNLInputAgent(mode=ProcessingMode.FAST)
    await agent.initialize()
    return agent


async def create_standard_processor() -> FinalNLInputAgent:
    """Create a standard processor with AI and caching"""
    agent = FinalNLInputAgent(mode=ProcessingMode.STANDARD)
    await agent.initialize()
    return agent


async def create_advanced_processor() -> FinalNLInputAgent:
    """Create an advanced processor with all features"""
    agent = FinalNLInputAgent(mode=ProcessingMode.ADVANCED)
    await agent.initialize()
    return agent


async def create_enterprise_processor(config: Optional[Dict] = None) -> FinalNLInputAgent:
    """Create an enterprise processor with monitoring"""
    agent = FinalNLInputAgent(mode=ProcessingMode.ENTERPRISE, config=config)
    await agent.initialize()
    return agent


# Lambda handler for AWS deployment
def lambda_handler(event, context):
    """AWS Lambda handler for NL Input processing"""
    import asyncio
    
    # Parse event
    body = json.loads(event.get("body", "{}"))
    query = body.get("query", "")
    
    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Query is required"})
        }
    
    # Create and run processor
    async def process():
        processor = await create_standard_processor()
        try:
            requirements = await processor.process(
                query=query,
                user_id=body.get("user_id"),
                session_id=body.get("session_id")
            )
            return processor._requirements_to_dict(requirements)
        finally:
            await processor.cleanup()
    
    # Run async code
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(process())
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }


# FastAPI integration
def create_nl_input_api():
    """Create FastAPI app for NL Input processing"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(title="NL Input Agent API", version="3.0.0")
    
    # Global processor instance
    processor: Optional[FinalNLInputAgent] = None
    
    class ProcessRequest(BaseModel):
        query: str
        user_id: Optional[str] = None
        session_id: Optional[str] = None
        context: Optional[Dict[str, Any]] = None
    
    @app.on_event("startup")
    async def startup():
        global processor
        processor = await create_standard_processor()
    
    @app.on_event("shutdown")
    async def shutdown():
        if processor:
            await processor.cleanup()
    
    @app.post("/process")
    async def process_query(request: ProcessRequest):
        if not processor:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        try:
            requirements = await processor.process(
                query=request.query,
                context=request.context,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            return processor._requirements_to_dict(requirements)
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        if not processor:
            return {"status": "initializing"}
        
        return await processor.health_check()
    
    return app


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        # Create processor
        processor = await create_advanced_processor()
        
        # Process a query
        requirements = await processor.process(
            query="I need a web application for e-commerce with React frontend and Python backend. It should have user authentication, product catalog, shopping cart, and payment integration with Stripe."
        )
        
        # Print results
        print(f"Project Type: {requirements.project_type}")
        print(f"Project Name: {requirements.project_name}")
        print(f"Features: {requirements.features}")
        print(f"Tech Stack: {requirements.technical_requirements}")
        print(f"Complexity: {requirements.estimated_complexity}")
        print(f"Confidence: {requirements.confidence_score:.2f}")
        
        # Cleanup
        await processor.cleanup()
    
    asyncio.run(main())