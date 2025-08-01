from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import AgentMemory
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ProjectRequirements:
    description: str
    project_type: str
    technical_requirements: List[str]
    non_functional_requirements: List[str]
    technology_preferences: Dict[str, Any]
    constraints: List[str]
    extracted_entities: Dict[str, Any]

class ProjectTypeClassifier:
    async def classify(self, description: str) -> str:
        if any(word in description.lower() for word in ['web', 'website', 'webapp']):
            return 'web_application'
        elif any(word in description.lower() for word in ['mobile', 'app', 'ios', 'android']):
            return 'mobile_application'
        elif any(word in description.lower() for word in ['api', 'service', 'backend']):
            return 'api_service'
        else:
            return 'general_application'

class TechStackAnalyzer:
    async def analyze(self, description: str) -> Dict[str, List[str]]:
        tech_stack = {'frontend': [], 'backend': [], 'database': []}
        
        desc_lower = description.lower()
        
        # Frontend detection
        if 'react' in desc_lower:
            tech_stack['frontend'].append('React')
        if 'vue' in desc_lower:
            tech_stack['frontend'].append('Vue.js')
        if 'angular' in desc_lower:
            tech_stack['frontend'].append('Angular')
        
        # Backend detection
        if any(word in desc_lower for word in ['python', 'django', 'flask']):
            tech_stack['backend'].append('Python')
        if any(word in desc_lower for word in ['node', 'express', 'javascript']):
            tech_stack['backend'].append('Node.js')
        
        # Database detection
        if any(word in desc_lower for word in ['mysql', 'postgres', 'database']):
            tech_stack['database'].append('SQL Database')
        if 'mongodb' in desc_lower:
            tech_stack['database'].append('MongoDB')
        
        return tech_stack

class RequirementExtractor:
    async def extract(self, description: str) -> Dict[str, List[str]]:
        requirements = {
            'functional': [],
            'non_functional': []
        }
        
        # Simple keyword-based extraction
        if 'user' in description.lower():
            requirements['functional'].append('User management')
        if 'auth' in description.lower():
            requirements['functional'].append('Authentication')
        if 'payment' in description.lower():
            requirements['functional'].append('Payment processing')
        
        # Non-functional requirements
        if any(word in description.lower() for word in ['fast', 'performance', 'speed']):
            requirements['non_functional'].append('High performance')
        if any(word in description.lower() for word in ['secure', 'security']):
            requirements['non_functional'].append('Security')
        if any(word in description.lower() for word in ['scalable', 'scale']):
            requirements['non_functional'].append('Scalability')
        
        return requirements

class EntityRecognizer:
    async def recognize(self, description: str) -> Dict[str, List[str]]:
        entities = {
            'technologies': [],
            'features': [],
            'domains': []
        }
        
        # Technology entities
        tech_keywords = ['react', 'vue', 'angular', 'python', 'node', 'mysql', 'mongodb']
        for tech in tech_keywords:
            if tech in description.lower():
                entities['technologies'].append(tech)
        
        # Feature entities
        feature_keywords = ['authentication', 'payment', 'search', 'notification']
        for feature in feature_keywords:
            if feature in description.lower():
                entities['features'].append(feature)
        
        # Domain entities
        domain_keywords = ['ecommerce', 'healthcare', 'finance', 'education']
        for domain in domain_keywords:
            if domain in description.lower():
                entities['domains'].append(domain)
        
        return entities

class ContextEnhancer:
    async def enhance(self, description: str, context: Optional[Dict] = None) -> str:
        # Simple context enhancement
        enhanced = description
        
        if context and 'previous_projects' in context:
            enhanced += f"\n\nContext: User has experience with {context['previous_projects']}"
        
        return enhanced

class RequirementValidator:
    async def validate(self, requirements: Dict) -> Any:
        # Simple validation mock
        class ValidationResult:
            def __init__(self):
                self.has_ambiguities = False
                self.ambiguities = []
                self.data = requirements
        
        return ValidationResult()

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
            memory=AgentMemory(),
            tools=[
                ProjectTypeClassifier(),
                TechStackAnalyzer(),
                RequirementExtractor(),
                EntityRecognizer()
            ],
            temperature=0.3,
            max_retries=3
        )

        self.context_enhancer = ContextEnhancer()
        self.validation_engine = RequirementValidator()

    async def process_description(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
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

    async def _parse_analysis(self, analysis: Any) -> Dict[str, Any]:
        """분석 결과를 구조화된 데이터로 변환"""
        
        # 도구들을 사용하여 분석
        classifier = ProjectTypeClassifier()
        tech_analyzer = TechStackAnalyzer()
        req_extractor = RequirementExtractor()
        entity_recognizer = EntityRecognizer()
        
        # 분석 텍스트에서 설명 추출 (간단한 구현)
        description = str(analysis)
        
        project_type = await classifier.classify(description)
        tech_preferences = await tech_analyzer.analyze(description)
        requirements = await req_extractor.extract(description)
        entities = await entity_recognizer.recognize(description)
        
        return {
            'description': description,
            'project_type': project_type,
            'technical_requirements': requirements['functional'],
            'non_functional_requirements': requirements['non_functional'],
            'technology_preferences': tech_preferences,
            'constraints': [],
            'extracted_entities': entities
        }