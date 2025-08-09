"""
NL Input Agent - ECS Integrated Version
Natural Language Processing and Requirement Extraction
Based on phase4-4.1.1 specifications
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent, AgentConfig, AgentContext, AgentResult

# Import modules - 절대 임포트로 변경
import importlib.util
import sys
from pathlib import Path

def safe_import_module(module_name, file_path):
    """안전한 모듈 임포트"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")
        return None

# 모듈들을 절대 경로로 임포트
modules_path = Path(__file__).parent / "modules"

context_enhancer_mod = safe_import_module("context_enhancer", modules_path / "context_enhancer.py")
ContextEnhancer = getattr(context_enhancer_mod, "ContextEnhancer", None) if context_enhancer_mod else None

requirement_validator_mod = safe_import_module("requirement_validator", modules_path / "requirement_validator.py")
RequirementValidator = getattr(requirement_validator_mod, "RequirementValidator", None) if requirement_validator_mod else None

project_type_classifier_mod = safe_import_module("project_type_classifier", modules_path / "project_type_classifier.py")
ProjectTypeClassifier = getattr(project_type_classifier_mod, "ProjectTypeClassifier", None) if project_type_classifier_mod else None

tech_stack_analyzer_mod = safe_import_module("tech_stack_analyzer", modules_path / "tech_stack_analyzer.py")
TechStackAnalyzer = getattr(tech_stack_analyzer_mod, "TechStackAnalyzer", None) if tech_stack_analyzer_mod else None

requirement_extractor_mod = safe_import_module("requirement_extractor", modules_path / "requirement_extractor.py")
RequirementExtractor = getattr(requirement_extractor_mod, "RequirementExtractor", None) if requirement_extractor_mod else None

entity_recognizer_mod = safe_import_module("entity_recognizer", modules_path / "entity_recognizer.py")
EntityRecognizer = getattr(entity_recognizer_mod, "EntityRecognizer", None) if entity_recognizer_mod else None

multilingual_processor_mod = safe_import_module("multilingual_processor", modules_path / "multilingual_processor.py")
MultilingualProcessor = getattr(multilingual_processor_mod, "MultilingualProcessor", None) if multilingual_processor_mod else None

intent_analyzer_mod = safe_import_module("intent_analyzer", modules_path / "intent_analyzer.py")
IntentAnalyzer = getattr(intent_analyzer_mod, "IntentAnalyzer", None) if intent_analyzer_mod else None

ambiguity_resolver_mod = safe_import_module("ambiguity_resolver", modules_path / "ambiguity_resolver.py")
AmbiguityResolver = getattr(ambiguity_resolver_mod, "AmbiguityResolver", None) if ambiguity_resolver_mod else None

template_matcher_mod = safe_import_module("template_matcher", modules_path / "template_matcher.py")
TemplateMatcher = getattr(template_matcher_mod, "TemplateMatcher", None) if template_matcher_mod else None

# AI Provider Support
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

@dataclass
class ProjectRequirements:
    """Structured project requirements output"""
    description: str
    project_type: str
    project_name: str = ""
    technical_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    functional_requirements: List[str] = field(default_factory=list)
    technology_preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    target_users: List[str] = field(default_factory=list)
    use_scenarios: List[str] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)

class NLInputAgent(BaseAgent):
    """
    Natural Language Input Processing Agent
    Analyzes user descriptions and extracts structured requirements
    """
    
    def __init__(self):
        config = AgentConfig(
            name="nl-input-agent",
            version="2.0.0",
            timeout=30,
            retries=3,
            cache_ttl=3600,
            enable_monitoring=True,
            enable_caching=True
        )
        super().__init__(config)
        
        # Initialize modules with None check
        self.context_enhancer = ContextEnhancer() if ContextEnhancer else None
        self.requirement_validator = RequirementValidator() if RequirementValidator else None
        self.project_classifier = ProjectTypeClassifier() if ProjectTypeClassifier else None
        self.tech_analyzer = TechStackAnalyzer() if TechStackAnalyzer else None
        self.requirement_extractor = RequirementExtractor() if RequirementExtractor else None
        self.entity_recognizer = EntityRecognizer() if EntityRecognizer else None
        self.multilingual_processor = MultilingualProcessor() if MultilingualProcessor else None
        self.intent_analyzer = IntentAnalyzer() if IntentAnalyzer else None
        self.ambiguity_resolver = AmbiguityResolver() if AmbiguityResolver else None
        self.template_matcher = TemplateMatcher() if TemplateMatcher else None
        
        # AI clients
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        
        # Processing statistics
        self.processed_languages = set()
        self.template_hits = 0
        self.ai_fallbacks = 0
        
    async def _custom_initialize(self):
        """Initialize NL Input specific resources"""
        
        # Initialize AI providers
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
    
    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult[ProjectRequirements]:
        """
        Process natural language description and extract requirements
        """
        
        try:
            # Extract input
            description = input_data.get("description", "")
            user_context = input_data.get("context", {})
            preferred_language = input_data.get("language", "auto")
            
            if not description:
                return AgentResult(
                    success=False,
                    error="No description provided"
                )
            
            self.logger.info(f"Processing NL input: {len(description)} chars")
            
            # Step 1: Language Detection and Translation
            language, translated_desc = await self.multilingual_processor.process(
                description,
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
                requirements = await self._process_template_match(template_match, enhanced_input)
            else:
                # Step 4: AI Processing (comprehensive path)
                requirements = await self._process_with_ai(enhanced_input, user_context)
            
            # Step 5: Intent Analysis
            intent_analysis = await self.intent_analyzer.analyze(enhanced_input)
            requirements.metadata["intent"] = intent_analysis
            
            # Step 6: Entity Recognition
            entities = await self.entity_recognizer.extract(enhanced_input)
            requirements.extracted_entities = entities
            
            # Step 7: Project Type Classification
            project_type = await self.project_classifier.classify(enhanced_input, entities)
            requirements.project_type = project_type
            
            # Step 8: Technology Stack Analysis
            tech_stack = await self.tech_analyzer.analyze(
                enhanced_input,
                project_type,
                user_context.get("preferred_stack")
            )
            requirements.technology_preferences = tech_stack
            
            # Step 9: Requirement Extraction
            functional, non_functional, technical = await self.requirement_extractor.extract(
                enhanced_input,
                project_type,
                entities
            )
            requirements.functional_requirements = functional
            requirements.non_functional_requirements = non_functional
            requirements.technical_requirements = technical
            
            # Step 10: Ambiguity Resolution
            ambiguities = await self.ambiguity_resolver.detect(requirements)
            if ambiguities:
                clarifications = await self.ambiguity_resolver.generate_questions(ambiguities)
                requirements.clarification_questions = clarifications
            
            # Step 11: Validation
            validation_result = await self.requirement_validator.validate(requirements)
            if not validation_result.is_valid:
                requirements.metadata["validation_issues"] = validation_result.issues
                requirements.confidence_score *= 0.8
            
            # Step 12: Confidence Scoring
            requirements.confidence_score = await self._calculate_confidence(
                requirements,
                template_match is not None,
                validation_result.is_valid
            )
            
            # Add metadata
            requirements.metadata.update({
                "processing_time": context.start_time,
                "language_detected": language,
                "template_used": template_match.template_name if template_match else None,
                "ai_provider": self._get_ai_provider_used(),
                "trace_id": context.trace_id
            })
            
            self.logger.info(
                f"NL processing complete",
                extra={
                    "project_type": requirements.project_type,
                    "confidence": requirements.confidence_score,
                    "requirements_count": len(requirements.functional_requirements),
                    "language": language
                }
            )
            
            return AgentResult(
                success=True,
                data=requirements,
                metadata={
                    "language": language,
                    "confidence": requirements.confidence_score,
                    "ambiguities": len(requirements.clarification_questions)
                }
            )
            
        except Exception as e:
            self.logger.error(f"NL processing failed: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                error=f"Processing failed: {str(e)}"
            )
    
    async def _process_with_ai(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> ProjectRequirements:
        """Process with AI providers (Claude or GPT)"""
        
        self.ai_fallbacks += 1
        
        # Try Claude first
        if self.anthropic_client:
            try:
                return await self._process_with_claude(description, context)
            except Exception as e:
                self.logger.warning(f"Claude processing failed: {e}")
        
        # Fallback to GPT
        if self.openai_client:
            try:
                return await self._process_with_gpt(description, context)
            except Exception as e:
                self.logger.warning(f"GPT processing failed: {e}")
        
        # Final fallback to rule-based
        return await self._process_rule_based(description, context)
    
    async def _process_with_claude(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> ProjectRequirements:
        """Process with Anthropic Claude"""
        
        prompt = f"""Analyze this project description and extract structured requirements:

Description: {description}

Context: {json.dumps(context, indent=2)}

Extract:
1. Project type and name
2. Functional requirements (user-facing features)
3. Technical requirements (implementation details)
4. Non-functional requirements (performance, security, etc.)
5. Technology preferences
6. Constraints and limitations
7. Target users and use cases
8. Any ambiguous points needing clarification

Respond in JSON format."""

        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        result_text = response.content[0].text
        result_json = json.loads(result_text)
        
        return self._parse_ai_response(result_json, description)
    
    async def _process_with_gpt(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> ProjectRequirements:
        """Process with OpenAI GPT"""
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a requirements analyst. Extract structured requirements from project descriptions."
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
        return self._parse_ai_response(result_json, description)
    
    async def _process_rule_based(
        self,
        description: str,
        context: Dict[str, Any]
    ) -> ProjectRequirements:
        """Fallback rule-based processing"""
        
        requirements = ProjectRequirements(
            description=description,
            project_type="web_app",  # default
            metadata={"processing_method": "rule_based"}
        )
        
        # Extract project name
        name_match = re.search(r'(?:called|named|titulo)\s+"?([^"]+)"?', description, re.I)
        if name_match:
            requirements.project_name = name_match.group(1)
        
        # Extract features using keywords
        feature_keywords = [
            "login", "authentication", "signup", "register",
            "search", "filter", "sort", "pagination",
            "upload", "download", "export", "import",
            "payment", "checkout", "cart", "billing",
            "dashboard", "analytics", "reports", "charts",
            "chat", "messaging", "notifications", "email",
            "api", "integration", "webhook", "rest",
            "admin", "management", "crud", "cms"
        ]
        
        description_lower = description.lower()
        for keyword in feature_keywords:
            if keyword in description_lower:
                requirements.functional_requirements.append(f"{keyword.title()} functionality")
        
        return requirements
    
    async def _process_template_match(
        self,
        template_match: Any,
        description: str
    ) -> ProjectRequirements:
        """Process using matched template"""
        
        requirements = ProjectRequirements(
            description=description,
            project_type=template_match.project_type,
            project_name=template_match.suggested_name,
            functional_requirements=template_match.features,
            technology_preferences=template_match.tech_stack,
            metadata={"template": template_match.template_name}
        )
        
        # Customize based on description
        customizations = await self.template_matcher.customize(template_match, description)
        requirements.functional_requirements.extend(customizations.get("additional_features", []))
        
        return requirements
    
    def _parse_ai_response(self, response: Dict, description: str) -> ProjectRequirements:
        """Parse AI response into ProjectRequirements"""
        
        return ProjectRequirements(
            description=description,
            project_type=response.get("project_type", "web_app"),
            project_name=response.get("project_name", ""),
            functional_requirements=response.get("functional_requirements", []),
            non_functional_requirements=response.get("non_functional_requirements", []),
            technical_requirements=response.get("technical_requirements", []),
            technology_preferences=response.get("technology_preferences", {}),
            constraints=response.get("constraints", []),
            extracted_entities=response.get("entities", {}),
            target_users=response.get("target_users", []),
            use_scenarios=response.get("use_scenarios", []),
            clarification_questions=response.get("clarifications", [])
        )
    
    async def _calculate_confidence(
        self,
        requirements: ProjectRequirements,
        template_used: bool,
        validation_passed: bool
    ) -> float:
        """Calculate confidence score for extracted requirements"""
        
        score = 0.5  # Base score
        
        # Template match bonus
        if template_used:
            score += 0.2
        
        # Validation bonus
        if validation_passed:
            score += 0.1
        
        # Completeness bonuses
        if requirements.functional_requirements:
            score += min(0.1, len(requirements.functional_requirements) * 0.02)
        
        if requirements.technology_preferences:
            score += 0.1
        
        if requirements.project_name:
            score += 0.05
        
        if not requirements.clarification_questions:
            score += 0.05
        
        # AI processing penalty (less confident than templates)
        if requirements.metadata.get("processing_method") == "rule_based":
            score *= 0.7
        
        return min(1.0, score)
    
    def _get_ai_provider_used(self) -> str:
        """Get which AI provider was used"""
        if self.anthropic_client:
            return "claude"
        elif self.openai_client:
            return "gpt"
        else:
            return "rule_based"
    
    async def _custom_cleanup(self):
        """Cleanup NL Input specific resources"""
        # Close AI client connections if needed
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.get_metrics()
        stats.update({
            "languages_processed": list(self.processed_languages),
            "template_hit_rate": self.template_hits / max(1, self.processing_count),
            "ai_fallback_rate": self.ai_fallbacks / max(1, self.processing_count),
            "ai_provider": self._get_ai_provider_used()
        })
        return stats


# Standalone function for direct usage
async def process_nl_input(description: str, context: Optional[Dict] = None) -> ProjectRequirements:
    """Convenience function for processing NL input"""
    agent = NLInputAgent()
    await agent.initialize()
    
    try:
        result = await agent.execute(
            {"description": description, "context": context or {}},
            AgentContext(trace_id=f"nl-{datetime.now().timestamp()}")
        )
        
        if result.success:
            return result.data
        else:
            raise Exception(result.error)
            
    finally:
        await agent.cleanup()