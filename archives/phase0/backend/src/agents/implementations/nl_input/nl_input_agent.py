"""
T-Developer MVP - NL Input Agent Core

자연어 프로젝트 설명을 분석하고 요구사항을 추출하는 핵심 에이전트
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from agno.tools import Tool

@dataclass
class ProjectRequirements:
    description: str
    project_type: str
    technical_requirements: List[str]
    non_functional_requirements: List[str]
    technology_preferences: Dict[str, Any]
    constraints: List[str]
    extracted_entities: Dict[str, Any]
    confidence_score: float = 0.0

class RequirementExtractor(Tool):
    """요구사항 추출 도구"""
    
    def __init__(self):
        super().__init__(
            name="requirement_extractor",
            description="Extract structured requirements from natural language"
        )
    
    async def run(self, text: str) -> Dict[str, Any]:
        # 기능 요구사항 추출
        functional_reqs = self._extract_functional_requirements(text)
        
        # 비기능 요구사항 추출
        non_functional_reqs = self._extract_non_functional_requirements(text)
        
        # 기술 스택 추출
        tech_stack = self._extract_technology_stack(text)
        
        return {
            "functional_requirements": functional_reqs,
            "non_functional_requirements": non_functional_reqs,
            "technology_stack": tech_stack
        }
    
    def _extract_functional_requirements(self, text: str) -> List[str]:
        """기능 요구사항 추출"""
        import re
        
        patterns = [
            r'사용자는\s+(.+?)할\s+수\s+있어야\s+한다',
            r'시스템은\s+(.+?)해야\s+한다',
            r'(.+?)\s+기능이\s+필요하다',
            r'(.+?)\s+구현해야\s+한다'
        ]
        
        requirements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)
        
        return list(set(requirements))
    
    def _extract_non_functional_requirements(self, text: str) -> List[str]:
        """비기능 요구사항 추출"""
        import re
        
        patterns = [
            r'(\d+)\s*명의?\s*사용자',
            r'(\d+)\s*초\s*이내',
            r'보안이?\s+중요',
            r'확장\s*가능',
            r'성능이?\s+중요'
        ]
        
        requirements = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                requirements.append(pattern)
        
        return requirements
    
    def _extract_technology_stack(self, text: str) -> List[str]:
        """기술 스택 추출"""
        tech_keywords = [
            'React', 'Vue', 'Angular', 'Next.js', 'Nuxt',
            'Node.js', 'Python', 'Java', 'Spring',
            'MySQL', 'PostgreSQL', 'MongoDB',
            'AWS', 'Docker', 'Kubernetes'
        ]
        
        found_tech = []
        for tech in tech_keywords:
            if tech.lower() in text.lower():
                found_tech.append(tech)
        
        return found_tech

class ProjectTypeClassifier(Tool):
    """프로젝트 타입 분류 도구"""
    
    def __init__(self):
        super().__init__(
            name="project_type_classifier",
            description="Classify project type from description"
        )
    
    async def run(self, text: str) -> str:
        """프로젝트 타입 분류"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['웹', 'web', '웹사이트', 'website']):
            return 'web_application'
        elif any(keyword in text_lower for keyword in ['모바일', 'mobile', '앱', 'app']):
            return 'mobile_application'
        elif any(keyword in text_lower for keyword in ['api', 'rest', 'graphql']):
            return 'api_service'
        elif any(keyword in text_lower for keyword in ['데스크톱', 'desktop', '데스크탑']):
            return 'desktop_application'
        else:
            return 'general_application'

class NLInputAgent:
    """자연어 프로젝트 설명을 분석하고 요구사항을 추출하는 에이전트"""

    def __init__(self):
        self.agent = Agent(
            name="NL-Input-Processor",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Senior requirements analyst specializing in software project analysis",
            instructions=[
                "프로젝트 설명에서 핵심 요구사항을 추출",
                "기술적/비기술적 요구사항을 구분",
                "프로젝트 유형과 규모를 파악",
                "선호 기술 스택과 제약사항을 식별",
                "모호한 부분에 대해 명확화 질문 생성"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-nl-conversations"
            ),
            tools=[
                RequirementExtractor(),
                ProjectTypeClassifier()
            ],
            temperature=0.3,
            max_retries=3
        )

        self.context_enhancer = ContextEnhancer()
        self.validation_engine = RequirementValidator()

    async def process_description(
        self, 
        description: str, 
        context: Optional[Dict] = None
    ) -> ProjectRequirements:
        """자연어 프로젝트 설명 처리"""

        # 1. 컨텍스트 향상
        enhanced_input = await self.context_enhancer.enhance(description, context)

        # 2. 초기 분석
        analysis_prompt = f"""
        다음 프로젝트 설명을 분석하고 요구사항을 추출하세요:

        설명: {enhanced_input}

        추출해야 할 항목:
        1. 프로젝트 유형 (웹앱, 모바일앱, API, CLI 도구 등)
        2. 핵심 기능 요구사항
        3. 기술적 요구사항
        4. 성능/보안 등 비기능적 요구사항
        5. 선호하는 기술 스택
        6. 제약사항이나 특별 요구사항
        7. 타겟 사용자와 사용 시나리오
        """

        initial_analysis = await self.agent.arun(analysis_prompt)

        # 3. 구조화된 데이터로 변환
        structured_data = await self._parse_analysis(initial_analysis)

        # 4. 검증 및 보완
        validated_requirements = await self.validation_engine.validate(structured_data)

        return ProjectRequirements(**validated_requirements.data)

    async def _parse_analysis(self, analysis_result) -> Dict[str, Any]:
        """분석 결과를 구조화된 데이터로 변환"""
        
        # 도구를 사용하여 요구사항 추출
        extracted = await self.agent.tools[0].run(analysis_result.content)
        
        # 프로젝트 타입 분류
        project_type = await self.agent.tools[1].run(analysis_result.content)
        
        return {
            "description": analysis_result.content,
            "project_type": project_type,
            "technical_requirements": extracted.get("functional_requirements", []),
            "non_functional_requirements": extracted.get("non_functional_requirements", []),
            "technology_preferences": {
                "stack": extracted.get("technology_stack", [])
            },
            "constraints": [],
            "extracted_entities": extracted,
            "confidence_score": 0.8
        }

class ContextEnhancer:
    """컨텍스트 향상 도구"""
    
    async def enhance(self, text: str, context: Optional[Dict] = None) -> str:
        """텍스트 컨텍스트 향상"""
        enhanced = text
        
        if context:
            # 이전 대화 컨텍스트 추가
            if 'previous_context' in context:
                enhanced = f"이전 컨텍스트: {context['previous_context']}\n\n{enhanced}"
            
            # 사용자 프로필 정보 추가
            if 'user_profile' in context:
                enhanced = f"사용자 정보: {context['user_profile']}\n\n{enhanced}"
        
        return enhanced

class RequirementValidator:
    """요구사항 검증 도구"""
    
    async def validate(self, data: Dict[str, Any]) -> 'ValidationResult':
        """요구사항 데이터 검증"""
        
        # 필수 필드 확인
        required_fields = ['description', 'project_type', 'technical_requirements']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Required field missing: {field}")
        
        # 신뢰도 점수 계산
        confidence = self._calculate_confidence(data)
        data['confidence_score'] = confidence
        
        return ValidationResult(
            is_valid=True,
            data=data,
            confidence=confidence
        )
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        score = 0.5  # 기본 점수
        
        # 기술 요구사항이 있으면 +0.2
        if data.get('technical_requirements'):
            score += 0.2
        
        # 기술 스택이 명시되어 있으면 +0.2
        if data.get('technology_preferences', {}).get('stack'):
            score += 0.2
        
        # 프로젝트 타입이 명확하면 +0.1
        if data.get('project_type') != 'general_application':
            score += 0.1
        
        return min(score, 1.0)

class ValidationResult:
    """검증 결과"""
    
    def __init__(self, is_valid: bool, data: Dict[str, Any], confidence: float):
        self.is_valid = is_valid
        self.data = data
        self.confidence = confidence
        self.has_ambiguities = confidence < 0.7
        self.ambiguities = []