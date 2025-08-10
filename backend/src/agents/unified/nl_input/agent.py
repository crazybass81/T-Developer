"""
Unified NL Input Agent - Production Implementation
Combines the best features from all three implementations
"""

import asyncio
import re
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field

# Unified base imports
from src.agents.unified.base import UnifiedBaseAgent, AgentConfig, AgentContext, AgentResult

# Phase 2 imports
from src.core.interfaces import AgentInput, ProcessingStatus, ValidationResult
from src.core.agent_models import NLInputResult
from src.core.event_bus import publish_agent_event, EventType
from src.core.security import InputValidator

# Module imports
from .modules import (
    ContextEnhancer,
    RequirementValidator,
    ProjectTypeClassifier,
    TechStackAnalyzer,
    RequirementExtractor,
    EntityRecognizer,
    MultilingualProcessor,
    IntentAnalyzer,
    AmbiguityResolver,
    TemplateMatcher
)

# AI Provider Support (optional)
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

import logging
logger = logging.getLogger(__name__)


@dataclass
class EnhancedNLInputResult(NLInputResult):
    """Extended NL Input result with additional fields"""
    project_name: str = ""
    description: str = ""
    non_functional_requirements: List[str] = field(default_factory=list)
    functional_requirements: List[str] = field(default_factory=list)
    technology_preferences: Dict[str, Any] = field(default_factory=dict)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    target_users: List[str] = field(default_factory=list)
    use_scenarios: List[str] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)
    template_used: Optional[str] = None
    ai_provider: Optional[str] = None


class UnifiedNLInputAgent(UnifiedBaseAgent):
    """
    Unified NL Input Agent
    Combines Phase 2 integration, ECS optimization, and production logic
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        # Initialize with default config if not provided
        if not config:
            config = AgentConfig(
                name="nl_input",
                version="3.0.0",
                timeout=30,
                retries=3,
                cache_ttl=3600,
                enable_monitoring=True,
                enable_caching=True,
                enable_state_management=True,
                ecs_optimized=False  # Can be toggled based on deployment
            )
        
        super().__init__(config)
        
        # Initialize modules
        self.context_enhancer = ContextEnhancer()
        self.requirement_validator = RequirementValidator()
        self.project_classifier = ProjectTypeClassifier()
        self.tech_analyzer = TechStackAnalyzer()
        self.requirement_extractor = RequirementExtractor()
        self.entity_recognizer = EntityRecognizer()
        self.multilingual_processor = MultilingualProcessor()
        self.intent_analyzer = IntentAnalyzer()
        self.ambiguity_resolver = AmbiguityResolver()
        self.template_matcher = TemplateMatcher()
        
        # AI clients
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        
        # Processing statistics
        self.processed_languages = set()
        self.template_hits = 0
        self.ai_fallbacks = 0
        
        # Enhanced keyword dictionaries (from implementations version)
        self.keywords = {
            'project_types': {
                'todo': ['todo', 'task', 'list', 'checklist', '할일', '투두', '작업'],
                'blog': ['blog', 'post', 'article', 'writing', '블로그', '글쓰기', '포스트'],
                'ecommerce': ['shop', 'store', 'cart', 'product', 'payment', '쇼핑', '상품', '결제'],
                'dashboard': ['dashboard', 'admin', 'analytics', 'metrics', '대시보드', '관리자', '분석'],
                'chat': ['chat', 'message', 'conversation', 'messenger', '채팅', '메시지', '대화'],
                'portfolio': ['portfolio', 'gallery', 'showcase', 'resume', '포트폴리오', '갤러리'],
                'social': ['social', 'network', 'community', 'forum', '소셜', '커뮤니티', '포럼'],
                'saas': ['saas', 'subscription', 'service', 'platform', '서비스', '플랫폼'],
                'game': ['game', 'play', 'score', 'level', '게임', '플레이', '점수'],
                'education': ['education', 'learning', 'course', 'tutorial', '교육', '학습', '강의']
            },
            'frameworks': {
                'react': ['react', 'nextjs', 'next.js', 'next', '리액트', '넥스트'],
                'vue': ['vue', 'nuxt', 'vuejs', '뷰', '뷰제이에스'],
                'angular': ['angular', 'ng', '앵귤러'],
                'svelte': ['svelte', 'sveltekit', '스벨트'],
                'solid': ['solid', 'solidjs', '솔리드'],
                'express': ['express', 'node', 'nodejs', '익스프레스', '노드'],
                'fastapi': ['fastapi', 'python', '패스트API', '파이썬'],
                'django': ['django', '장고'],
                'rails': ['rails', 'ruby', '레일즈', '루비']
            },
            'features': {
                'auth': ['login', 'auth', 'user', 'signin', 'signup', 'oauth', '로그인', '인증', '회원'],
                'database': ['database', 'db', 'storage', 'persist', 'save', '데이터베이스', '저장', 'DB'],
                'api': ['api', 'backend', 'server', 'rest', 'graphql', 'endpoint', 'API', '백엔드'],
                'responsive': ['responsive', 'mobile', 'tablet', 'adaptive', '반응형', '모바일', '태블릿'],
                'realtime': ['realtime', 'live', 'websocket', 'streaming', '실시간', '라이브', '웹소켓'],
                'typescript': ['typescript', 'ts', 'typed', '타입스크립트', '타입'],
                'tailwind': ['tailwind', 'tailwindcss', 'utility', '테일윈드'],
                'testing': ['test', 'testing', 'jest', 'vitest', 'cypress', '테스트', '테스팅'],
                'docker': ['docker', 'container', 'kubernetes', '도커', '컨테이너'],
                'ci_cd': ['ci', 'cd', 'pipeline', 'deploy', 'github actions', 'CI/CD', '배포'],
                'seo': ['seo', 'search', 'meta', 'sitemap', 'SEO', '검색', '메타'],
                'pwa': ['pwa', 'offline', 'service worker', 'PWA', '오프라인'],
                'payment': ['payment', 'stripe', 'paypal', 'checkout', '결제', '페이먼트'],
                'email': ['email', 'mail', 'smtp', 'newsletter', '이메일', '메일'],
                'notification': ['notification', 'alert', 'push', 'notify', '알림', '푸시'],
                'search': ['search', 'filter', 'query', 'find', '검색', '필터', '찾기'],
                'upload': ['upload', 'file', 'image', 'media', '업로드', '파일', '이미지'],
                'chart': ['chart', 'graph', 'visualization', 'plot', '차트', '그래프', '시각화'],
                'map': ['map', 'location', 'gps', 'geocoding', '지도', '위치', 'GPS'],
                'ai': ['ai', 'ml', 'machine learning', 'gpt', 'AI', '인공지능', '머신러닝']
            },
            'ui_preferences': {
                'dark_mode': ['dark', 'night', 'dark mode', 'dark theme', '다크', '다크모드', '어두운'],
                'light_mode': ['light', 'bright', 'light mode', '라이트', '밝은'],
                'minimalist': ['minimal', 'simple', 'clean', 'minimalist', '미니멀', '심플', '깔끔'],
                'modern': ['modern', 'contemporary', 'trendy', '모던', '현대적', '트렌디'],
                'colorful': ['colorful', 'vibrant', 'bright colors', '컬러풀', '화려한', '밝은색'],
                'professional': ['professional', 'business', 'corporate', '전문적', '비즈니스', '기업']
            }
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            'simple': ['simple', 'basic', 'easy', 'quick', '간단한', '기본', '쉬운', '빠른'],
            'medium': ['standard', 'normal', 'typical', '표준', '일반적인', '보통'],
            'complex': ['complex', 'advanced', 'sophisticated', 'enterprise', '복잡한', '고급', '정교한', '엔터프라이즈']
        }
    
    async def _custom_initialize(self):
        """Initialize NL Input specific resources"""
        
        # Initialize AI providers if in ECS mode or explicitly enabled
        if self.config.ecs_optimized:
            if ANTHROPIC_AVAILABLE:
                api_key = await self._get_secret("anthropic-api-key")
                if api_key:
                    self.anthropic_client = AsyncAnthropic(api_key=api_key)
                    self.logger.info("Anthropic Claude initialized")
            
            if OPENAI_AVAILABLE:
                api_key = await self._get_secret("openai-api-key")
                if api_key:
                    self.openai_client = AsyncOpenAI(api_key=api_key)
                    self.logger.info("OpenAI GPT initialized")
        
        # Load templates
        await self.template_matcher.load_templates()
        
        # Initialize language models
        await self.multilingual_processor.initialize()
        
        self.logger.info("NL Input Agent initialization complete")
    
    async def validate_input(self, input_data: AgentInput[Dict]) -> ValidationResult:
        """Enhanced input validation"""
        result = await super().validate_input(input_data)
        
        # Additional NL-specific validation
        if not input_data.data:
            result.add_error("Input data is empty")
            return result
        
        # Support multiple input formats
        query = input_data.data.get('query', 
                input_data.data.get('description', 
                input_data.data.get('user_input', ''))).strip()
        
        # Use security validator
        validation = InputValidator.validate_project_query(query)
        if not validation['valid']:
            for error in validation['errors']:
                result.add_error(error)
        
        for warning in validation.get('warnings', []):
            result.add_warning(warning)
        
        return result
    
    async def process(self, input_data: AgentInput[Dict]) -> AgentResult[EnhancedNLInputResult]:
        """Process natural language input - Phase 2 interface"""
        
        try:
            # Extract and sanitize query
            query = InputValidator.sanitize_string(
                input_data.data.get('query', 
                    input_data.data.get('description', 
                    input_data.data.get('user_input', ''))),
                max_length=1000
            )
            
            # Get additional context
            user_context = input_data.data.get('context', {})
            preferred_language = input_data.data.get('language', 'auto')
            
            # Create context for processing
            context = AgentContext(
                trace_id=input_data.context.pipeline_id,
                pipeline_context=input_data.context,
                metadata={"query_length": len(query)}
            )
            
            # Process with unified logic
            result = await self._process_unified(
                query,
                user_context,
                preferred_language,
                context
            )
            
            return result
            
        except Exception as e:
            logger.error(f"NL Input Agent error: {e}")
            self.metrics.increment_counter("nl_input.errors")
            
            await publish_agent_event(
                EventType.AGENT_FAILED,
                self.config.name,
                input_data.context.pipeline_id,
                {"error": str(e)}
            )
            
            return AgentResult(
                success=False,
                error=str(e),
                status=ProcessingStatus.FAILED,
                agent_name=self.config.name,
                agent_version=self.config.version
            )
    
    async def _process_internal(self, input_data: Dict[str, Any], context: AgentContext) -> AgentResult:
        """Process for ECS mode - internal interface"""
        
        # Extract inputs
        query = input_data.get('description', input_data.get('query', ''))
        user_context = input_data.get('context', {})
        preferred_language = input_data.get('language', 'auto')
        
        # Process with unified logic
        return await self._process_unified(
            query,
            user_context,
            preferred_language,
            context
        )
    
    async def _process_unified(
        self,
        query: str,
        user_context: Dict[str, Any],
        preferred_language: str,
        context: AgentContext
    ) -> AgentResult[EnhancedNLInputResult]:
        """Unified processing logic for all modes"""
        
        timer_id = None
        if self.perf_tracker:
            timer_id = self.perf_tracker.start_timer("nl_input_processing")
        
        try:
            if not query:
                return AgentResult(
                    success=False,
                    error="No description provided",
                    status=ProcessingStatus.FAILED,
                    agent_name=self.config.name,
                    agent_version=self.config.version
                )
            
            self.logger.info(f"Processing NL input: {len(query)} chars")
            
            # Publish start event
            if context.pipeline_context:
                await publish_agent_event(
                    EventType.AGENT_STARTED,
                    self.config.name,
                    context.pipeline_context.pipeline_id,
                    {"query_length": len(query)}
                )
            
            # Step 1: Language Detection and Translation
            language, translated_desc = await self.multilingual_processor.process(
                query,
                target_language="en" if preferred_language == "auto" else preferred_language
            )
            self.processed_languages.add(language)
            
            # Step 2: Context Enhancement
            enhanced_input = await self.context_enhancer.enhance(
                translated_desc,
                user_context
            )
            
            # Step 3: Template Matching (fast path)
            template_match = await self.template_matcher.match(enhanced_input)
            
            if template_match and template_match.confidence > 0.8:
                self.template_hits += 1
                self.logger.info(f"Template match found: {template_match.template_name}")
                result_data = await self._process_template_match(
                    template_match,
                    enhanced_input,
                    query
                )
            else:
                # Step 4: Rule-based processing with AI fallback
                result_data = await self._process_comprehensive(
                    enhanced_input,
                    query,
                    user_context,
                    language
                )
            
            # Step 5: Validation
            validation_result = await self.requirement_validator.validate(result_data)
            if not validation_result.is_valid:
                result_data.metadata["validation_issues"] = validation_result.issues
                result_data.intent_confidence *= 0.8
            
            # Calculate final confidence
            result_data.intent_confidence = self._calculate_confidence(
                query,
                result_data.project_type,
                result_data.features,
                result_data.clarity_score
            )
            
            # Add metadata
            result_data.metadata.update({
                "processing_time": context.start_time,
                "language_detected": language,
                "template_used": result_data.template_used,
                "ai_provider": result_data.ai_provider,
                "trace_id": context.trace_id
            })
            
            # Stop timer and record metrics
            duration = 0
            if timer_id and self.perf_tracker:
                duration = self.perf_tracker.stop_timer(timer_id)
            
            if self.metrics:
                self.metrics.increment_counter("nl_input.processed")
                self.metrics.record_histogram("nl_input.features_count", len(result_data.features))
                self.metrics.set_gauge("nl_input.confidence", result_data.intent_confidence)
            
            # Publish completion event
            if context.pipeline_context:
                await publish_agent_event(
                    EventType.AGENT_COMPLETED,
                    self.config.name,
                    context.pipeline_context.pipeline_id,
                    {
                        "project_type": result_data.project_type,
                        "features_count": len(result_data.features),
                        "confidence": result_data.intent_confidence
                    }
                )
            
            return AgentResult(
                success=True,
                data=result_data,
                status=ProcessingStatus.COMPLETED,
                agent_name=self.config.name,
                agent_version=self.config.version,
                confidence=result_data.intent_confidence,
                quality_score=result_data.clarity_score,
                processing_time=duration,
                metadata={
                    "query_length": len(query),
                    "detected_language": language,
                    "features_extracted": len(result_data.features)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}", exc_info=True)
            
            if timer_id and self.perf_tracker:
                self.perf_tracker.stop_timer(timer_id)
            
            return AgentResult(
                success=False,
                error=f"Processing failed: {str(e)}",
                status=ProcessingStatus.FAILED,
                agent_name=self.config.name,
                agent_version=self.config.version
            )
    
    async def _process_comprehensive(
        self,
        enhanced_input: str,
        original_query: str,
        user_context: Dict[str, Any],
        language: str
    ) -> EnhancedNLInputResult:
        """Comprehensive processing with all modules"""
        
        # Core analysis using rule-based methods
        project_type = self._detect_project_type(enhanced_input)
        main_functionality = self._extract_main_functionality(enhanced_input, project_type)
        features = self._extract_features(enhanced_input)
        technical_reqs = self._analyze_technical_requirements(enhanced_input, features)
        constraints = self._extract_constraints(enhanced_input)
        preferences = self._extract_preferences(enhanced_input)
        complexity = self._assess_complexity(enhanced_input, features)
        keywords = self._extract_keywords(enhanced_input)
        
        # Additional analysis
        sentiment = self._analyze_sentiment(enhanced_input)
        clarity_score = self._calculate_clarity_score(enhanced_input, project_type, features)
        estimated_effort = self._estimate_effort(complexity, len(features))
        
        # Intent Analysis
        intent_analysis = await self.intent_analyzer.analyze(enhanced_input)
        
        # Entity Recognition
        entities = await self.entity_recognizer.extract(enhanced_input)
        
        # Technology Stack Analysis
        tech_stack = await self.tech_analyzer.analyze(
            enhanced_input,
            project_type,
            user_context.get('preferred_stack')
        )
        
        # Requirement Extraction
        functional, non_functional, technical = await self.requirement_extractor.extract(
            enhanced_input,
            project_type,
            entities
        )
        
        # Ambiguity Resolution
        ambiguities = await self.ambiguity_resolver.detect_from_text(enhanced_input)
        clarification_questions = []
        if ambiguities:
            clarification_questions = await self.ambiguity_resolver.generate_questions(ambiguities)
        
        # Try AI enhancement if available
        ai_provider = None
        if self.config.ecs_optimized and (self.anthropic_client or self.openai_client):
            try:
                ai_result = await self._enhance_with_ai(
                    enhanced_input,
                    user_context,
                    project_type
                )
                if ai_result:
                    # Merge AI insights
                    functional.extend(ai_result.get('functional_requirements', []))
                    non_functional.extend(ai_result.get('non_functional_requirements', []))
                    ai_provider = ai_result.get('provider')
                    self.ai_fallbacks += 1
            except Exception as e:
                self.logger.warning(f"AI enhancement failed: {e}")
        
        # Create result
        return EnhancedNLInputResult(
            project_type=project_type,
            project_name=self._extract_project_name(original_query),
            description=original_query,
            main_functionality=main_functionality,
            technical_requirements=technical_reqs,
            features=features,
            functional_requirements=functional,
            non_functional_requirements=non_functional,
            technology_preferences=tech_stack or preferences,
            constraints=constraints,
            preferences=preferences,
            complexity=complexity,
            estimated_effort_hours=estimated_effort,
            keywords=keywords,
            intent_confidence=0.0,  # Will be calculated later
            language=language,
            sentiment=sentiment,
            clarity_score=clarity_score,
            extracted_entities=entities,
            target_users=self._extract_target_users(enhanced_input),
            use_scenarios=self._extract_use_scenarios(enhanced_input, project_type),
            clarification_questions=clarification_questions,
            template_used=None,
            ai_provider=ai_provider,
            metadata={"intent": intent_analysis}
        )
    
    async def _process_template_match(
        self,
        template_match: Any,
        enhanced_input: str,
        original_query: str
    ) -> EnhancedNLInputResult:
        """Process using matched template"""
        
        # Customize template based on input
        customizations = await self.template_matcher.customize(template_match, enhanced_input)
        
        # Extract additional details
        features = template_match.features[:]
        features.extend(customizations.get('additional_features', []))
        
        # Quick analysis for missing pieces
        constraints = self._extract_constraints(enhanced_input)
        preferences = self._extract_preferences(enhanced_input)
        complexity = self._assess_complexity(enhanced_input, features)
        
        return EnhancedNLInputResult(
            project_type=template_match.project_type,
            project_name=template_match.suggested_name or self._extract_project_name(original_query),
            description=original_query,
            main_functionality=template_match.description,
            technical_requirements=template_match.technical_requirements,
            features=features,
            functional_requirements=template_match.functional_requirements,
            non_functional_requirements=template_match.non_functional_requirements,
            technology_preferences=template_match.tech_stack,
            constraints=constraints,
            preferences=preferences,
            complexity=complexity,
            estimated_effort_hours=template_match.estimated_hours,
            keywords=self._extract_keywords(enhanced_input),
            intent_confidence=template_match.confidence,
            language=self._detect_language(original_query),
            sentiment="neutral",
            clarity_score=0.9,  # High clarity for template matches
            extracted_entities={},
            target_users=template_match.target_users,
            use_scenarios=template_match.use_scenarios,
            clarification_questions=[],
            template_used=template_match.template_name,
            ai_provider=None,
            metadata={"template_confidence": template_match.confidence}
        )
    
    async def _enhance_with_ai(
        self,
        description: str,
        context: Dict[str, Any],
        project_type: str
    ) -> Optional[Dict[str, Any]]:
        """Enhance analysis with AI providers"""
        
        # Try Claude first
        if self.anthropic_client:
            try:
                return await self._process_with_claude(description, context, project_type)
            except Exception as e:
                self.logger.warning(f"Claude processing failed: {e}")
        
        # Fallback to GPT
        if self.openai_client:
            try:
                return await self._process_with_gpt(description, context, project_type)
            except Exception as e:
                self.logger.warning(f"GPT processing failed: {e}")
        
        return None
    
    async def _process_with_claude(
        self,
        description: str,
        context: Dict[str, Any],
        project_type: str
    ) -> Dict[str, Any]:
        """Process with Anthropic Claude"""
        
        prompt = f"""Analyze this {project_type} project description and extract additional requirements:

Description: {description}
Context: {json.dumps(context, indent=2)}

Extract any additional:
1. Functional requirements not explicitly stated
2. Non-functional requirements (performance, security, etc.)
3. Potential technical challenges

Respond in JSON format."""

        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        result_json = json.loads(result_text)
        result_json['provider'] = 'claude'
        
        return result_json
    
    async def _process_with_gpt(
        self,
        description: str,
        context: Dict[str, Any],
        project_type: str
    ) -> Dict[str, Any]:
        """Process with OpenAI GPT"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": f"You are analyzing a {project_type} project. Extract additional requirements."
                },
                {
                    "role": "user",
                    "content": f"Analyze: {description}\nContext: {json.dumps(context)}"
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result_json = json.loads(response.choices[0].message.content)
        result_json['provider'] = 'gpt'
        
        return result_json
    
    # Core analysis methods (from implementations version)
    def _detect_project_type(self, text: str) -> str:
        """Enhanced project type detection with scoring"""
        text_lower = text.lower()
        scores = {}
        
        for ptype, keywords in self.keywords['project_types'].items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight by keyword length (longer = more specific)
                    score += len(keyword) / 3
            
            if score > 0:
                scores[ptype] = score
        
        if scores:
            # Return type with highest score
            return max(scores, key=scores.get)
        
        # Fallback detection based on general terms
        if any(word in text_lower for word in ['web', 'website', 'site', '웹', '웹사이트']):
            return 'web_application'
        elif any(word in text_lower for word in ['app', 'application', '앱', '애플리케이션']):
            return 'web_application'
        
        return 'web_application'  # Default
    
    def _extract_main_functionality(self, text: str, project_type: str) -> str:
        """Extract the main functionality description"""
        text_lower = text.lower()
        
        # Remove common prefixes
        prefixes = ['create', 'build', 'make', 'develop', '만들어', '개발', '생성', '구축']
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                text_lower = text_lower[len(prefix):].strip()
        
        # Extract first significant phrase
        sentences = re.split(r'[.!?]', text)
        if sentences:
            main_sentence = sentences[0].strip()
            # Limit to reasonable length
            if len(main_sentence) > 100:
                main_sentence = main_sentence[:100] + "..."
            return main_sentence
        
        return f"{project_type} application"
    
    def _extract_project_name(self, text: str) -> str:
        """Extract project name from text"""
        # Look for quoted names
        name_match = re.search(r'(?:called|named|titulo)\s+"?([^"]+)"?', text, re.I)
        if name_match:
            return name_match.group(1)
        
        # Look for "my <something> app" pattern
        my_match = re.search(r'my\s+(\w+)\s+(?:app|application|project)', text, re.I)
        if my_match:
            return f"my-{my_match.group(1)}-app"
        
        return "my-app"  # Default
    
    def _extract_features(self, text: str) -> List[str]:
        """Enhanced feature extraction with priority"""
        text_lower = text.lower()
        features = []
        feature_scores = {}
        
        for feature, keywords in self.keywords['features'].items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Score based on keyword specificity
                    score = len(keyword) / 5
                    if feature not in feature_scores:
                        feature_scores[feature] = 0
                    feature_scores[feature] += score
        
        # Sort by score and take features
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        features = [f[0] for f in sorted_features]
        
        # Add implicit features
        if 'auth' in features and 'database' not in features:
            features.append('database')  # Auth requires database
        
        if 'payment' in features and 'auth' not in features:
            features.append('auth')  # Payment requires auth
        
        if 'realtime' in features and 'api' not in features:
            features.append('api')  # Realtime requires API
        
        return features
    
    def _analyze_technical_requirements(self, text: str, features: List[str]) -> Dict[str, Any]:
        """Comprehensive technical requirements analysis"""
        text_lower = text.lower()
        
        tech_reqs = {
            'frontend': [],
            'backend': [],
            'database': [],
            'infrastructure': [],
            'performance': 'standard',
            'security': 'standard',
            'scalability': 'standard'
        }
        
        # Frontend requirements
        for framework, keywords in self.keywords['frameworks'].items():
            if any(kw in text_lower for kw in keywords):
                tech_reqs['frontend'].append(framework)
                break
        
        if not tech_reqs['frontend']:
            tech_reqs['frontend'].append('react')  # Default
        
        # Add TypeScript if mentioned or implied
        if 'typescript' in features or 'ts' in text_lower or '타입' in text_lower:
            tech_reqs['frontend'].append('typescript')
        
        # Backend requirements
        if 'api' in features or 'backend' in text_lower:
            if 'graphql' in text_lower:
                tech_reqs['backend'].append('graphql')
            else:
                tech_reqs['backend'].append('rest')
            
            # Detect backend framework
            if 'express' in text_lower or 'node' in text_lower:
                tech_reqs['backend'].append('express')
            elif 'fastapi' in text_lower or 'python' in text_lower:
                tech_reqs['backend'].append('fastapi')
            elif 'django' in text_lower:
                tech_reqs['backend'].append('django')
            else:
                tech_reqs['backend'].append('express')  # Default
        
        # Database requirements
        if 'database' in features or 'auth' in features:
            if 'postgres' in text_lower or 'postgresql' in text_lower:
                tech_reqs['database'].append('postgresql')
            elif 'mongo' in text_lower or 'mongodb' in text_lower:
                tech_reqs['database'].append('mongodb')
            elif 'mysql' in text_lower:
                tech_reqs['database'].append('mysql')
            else:
                tech_reqs['database'].append('postgresql')  # Default
        
        # Infrastructure
        if 'docker' in features:
            tech_reqs['infrastructure'].append('docker')
        if 'ci_cd' in features:
            tech_reqs['infrastructure'].append('github_actions')
        if 'deploy' in text_lower or '배포' in text_lower:
            tech_reqs['infrastructure'].append('vercel')
        
        # Performance requirements
        if any(word in text_lower for word in ['fast', 'performance', 'optimize', '빠른', '성능', '최적화']):
            tech_reqs['performance'] = 'optimized'
        elif any(word in text_lower for word in ['enterprise', 'scale', '엔터프라이즈', '대규모']):
            tech_reqs['performance'] = 'enterprise'
        
        # Security requirements
        if any(word in text_lower for word in ['secure', 'security', 'encryption', '보안', '암호화']):
            tech_reqs['security'] = 'enhanced'
        
        # Scalability requirements
        if any(word in text_lower for word in ['scalable', 'scale', 'million', '확장', '백만']):
            tech_reqs['scalability'] = 'high'
        
        return tech_reqs
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extract project constraints"""
        constraints = []
        text_lower = text.lower()
        
        # Time constraints
        time_patterns = [
            r'\b(\d+)\s*(day|days|일)\b',
            r'\b(\d+)\s*(week|weeks|주)\b',
            r'\b(\d+)\s*(month|months|개월)\b'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                constraints.append(f"Time limit: {match.group(0)}")
        
        # Budget constraints
        if any(word in text_lower for word in ['budget', 'cost', 'cheap', 'free', '예산', '비용', '무료']):
            constraints.append("Budget conscious")
        
        # Technical constraints
        if 'no backend' in text_lower or '백엔드 없이' in text_lower:
            constraints.append("No backend required")
        
        if 'offline' in text_lower or '오프라인' in text_lower:
            constraints.append("Offline capability required")
        
        if 'mobile first' in text_lower or '모바일 우선' in text_lower:
            constraints.append("Mobile-first design")
        
        return constraints
    
    def _extract_preferences(self, text: str) -> Dict[str, str]:
        """Extract user preferences"""
        preferences = {}
        text_lower = text.lower()
        
        # UI preferences
        for pref_type, keywords in self.keywords['ui_preferences'].items():
            for keyword in keywords:
                if keyword in text_lower:
                    if 'theme' not in preferences:
                        preferences['theme'] = pref_type
                    if 'style' not in preferences and pref_type not in ['dark_mode', 'light_mode']:
                        preferences['style'] = pref_type
        
        # Set defaults if not specified
        if 'theme' not in preferences:
            preferences['theme'] = 'light_mode'
        if 'style' not in preferences:
            preferences['style'] = 'modern'
        
        # Styling preferences
        if 'tailwind' in text_lower:
            preferences['styling'] = 'tailwind'
        elif 'css modules' in text_lower:
            preferences['styling'] = 'css_modules'
        elif 'styled components' in text_lower:
            preferences['styling'] = 'styled_components'
        else:
            preferences['styling'] = 'tailwind'  # Default
        
        return preferences
    
    def _assess_complexity(self, text: str, features: List[str]) -> str:
        """Assess project complexity"""
        text_lower = text.lower()
        
        # Check for explicit complexity indicators
        for level, indicators in self.complexity_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level
        
        # Assess based on feature count and requirements
        feature_count = len(features)
        
        if feature_count <= 3:
            return 'simple'
        elif feature_count <= 7:
            return 'medium'
        else:
            return 'complex'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove stop words and extract significant terms
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were',
                     'that', 'this', 'these', 'those', 'i', 'you', 'we', 'they',
                     'create', 'build', 'make', 'want', 'need', 'app', 'application'}
        
        # Tokenize and filter
        words = re.findall(r'\b[a-z]+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequency and return top keywords
        from collections import Counter
        word_freq = Counter(keywords)
        
        return [word for word, _ in word_freq.most_common(10)]
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the input"""
        korean_pattern = re.compile(r'[\u3131-\u3163\uac00-\ud7a3]+')
        if korean_pattern.search(text):
            return 'ko'
        return 'en'
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        positive_words = ['love', 'great', 'awesome', 'excellent', 'good', 'nice',
                         '좋은', '훌륭한', '멋진', '최고']
        negative_words = ['hate', 'bad', 'terrible', 'awful', 'poor', 'worst',
                         '나쁜', '최악', '별로']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
    
    def _calculate_clarity_score(self, text: str, project_type: str, features: List[str]) -> float:
        """Calculate how clear the requirements are"""
        score = 0.5  # Base score
        
        # Clear project type increases score
        if project_type != 'web_application':  # Not default
            score += 0.15
        
        # Number of identified features
        if len(features) >= 3:
            score += 0.1
        if len(features) >= 5:
            score += 0.1
        
        # Text length (reasonable detail)
        word_count = len(text.split())
        if 20 <= word_count <= 100:
            score += 0.1
        elif word_count > 100:
            score += 0.05
        
        # Presence of technical details
        tech_terms = ['api', 'database', 'frontend', 'backend', 'deploy']
        if any(term in text.lower() for term in tech_terms):
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_effort(self, complexity: str, feature_count: int) -> int:
        """Estimate development effort in hours"""
        base_hours = {
            'simple': 40,
            'medium': 120,
            'complex': 320
        }
        
        hours = base_hours.get(complexity, 120)
        
        # Add hours based on features
        hours += feature_count * 8
        
        return hours
    
    def _calculate_confidence(self, text: str, project_type: str, 
                            features: List[str], clarity_score: float) -> float:
        """Calculate overall confidence in the analysis"""
        confidence = 0.5  # Base confidence
        
        # Project type clarity
        if project_type != 'web_application':
            confidence += 0.15
        
        # Features identified
        if len(features) > 0:
            confidence += min(len(features) * 0.05, 0.2)
        
        # Clarity score contribution
        confidence += clarity_score * 0.15
        
        # Text length contribution
        word_count = len(text.split())
        if word_count >= 20:
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    def _extract_target_users(self, text: str) -> List[str]:
        """Extract target user groups"""
        text_lower = text.lower()
        users = []
        
        user_keywords = {
            'developers': ['developer', 'programmer', 'engineer', '개발자'],
            'students': ['student', 'learner', 'education', '학생', '교육'],
            'businesses': ['business', 'company', 'enterprise', '비즈니스', '기업'],
            'consumers': ['consumer', 'customer', 'user', '소비자', '고객'],
            'admins': ['admin', 'administrator', 'manager', '관리자']
        }
        
        for user_type, keywords in user_keywords.items():
            if any(kw in text_lower for kw in keywords):
                users.append(user_type)
        
        if not users:
            users.append('general_users')
        
        return users
    
    def _extract_use_scenarios(self, text: str, project_type: str) -> List[str]:
        """Extract use case scenarios"""
        scenarios = []
        
        # Default scenarios by project type
        default_scenarios = {
            'todo': ['Create and manage tasks', 'Track progress', 'Set priorities'],
            'blog': ['Write and publish posts', 'Manage comments', 'Categorize content'],
            'ecommerce': ['Browse products', 'Add to cart', 'Complete checkout'],
            'dashboard': ['View analytics', 'Monitor metrics', 'Generate reports'],
            'chat': ['Send messages', 'Create channels', 'Share files']
        }
        
        if project_type in default_scenarios:
            scenarios = default_scenarios[project_type]
        else:
            scenarios = ['Primary user flow', 'Admin management', 'Data visualization']
        
        return scenarios
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.get_metrics()
        stats.update({
            "languages_processed": list(self.processed_languages),
            "template_hit_rate": self.template_hits / max(1, self.processing_count),
            "ai_fallback_rate": self.ai_fallbacks / max(1, self.processing_count),
            "ai_provider": self._get_ai_provider()
        })
        return stats
    
    def _get_ai_provider(self) -> str:
        """Get which AI provider is configured"""
        if self.anthropic_client:
            return "claude"
        elif self.openai_client:
            return "gpt"
        else:
            return "rule_based"


# Export the agent
__all__ = ['UnifiedNLInputAgent', 'EnhancedNLInputResult']