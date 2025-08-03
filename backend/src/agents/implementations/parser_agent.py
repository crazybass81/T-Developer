from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import asyncio
import json
from datetime import datetime
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.models.openai import OpenAIChat

@dataclass
class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"

@dataclass
class ParsedRequirement:
    id: str
    type: RequirementType
    category: str
    description: str
    priority: str  # high, medium, low
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    technical_details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParsedProject:
    project_info: Dict[str, Any]
    functional_requirements: List[ParsedRequirement]
    non_functional_requirements: List[ParsedRequirement]
    technical_requirements: List[ParsedRequirement]
    business_requirements: List[ParsedRequirement]
    constraints: List[ParsedRequirement]
    assumptions: List[ParsedRequirement]
    user_stories: List[Dict[str, Any]]
    use_cases: List[Dict[str, Any]]
    data_models: List[Dict[str, Any]]
    api_specifications: List[Dict[str, Any]]
    ui_components: List[Dict[str, Any]]
    integration_points: List[Dict[str, Any]]

class ParserAgent:
    """요구사항 파싱 및 구조화 에이전트"""

    def __init__(self):
        # 주 파서 - Claude 3 (긴 문맥 처리에 최적화)
        self.main_parser = Agent(
            name="Requirements-Parser",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Expert requirements analyst and system architect",
            instructions=[
                "Parse and structure project requirements from natural language",
                "Identify functional and non-functional requirements",
                "Extract technical specifications and constraints",
                "Create user stories and use cases",
                "Define data models and API specifications",
                "Identify dependencies and relationships between requirements"
            ],
            temperature=0.2,
            max_retries=3
        )

        # 보조 파서 - GPT-4 (세부 분석)
        self.detail_parser = Agent(
            name="Detail-Parser",
            model=OpenAIChat(id="gpt-4-turbo-preview"),
            role="Technical requirements specialist",
            instructions=[
                "Extract technical details from requirements",
                "Identify specific technologies and frameworks mentioned",
                "Parse API endpoints and data structures",
                "Extract performance and security requirements"
            ],
            temperature=0.1
        )

        # 전문 파서들 (구현 필요)
        from .parser.requirement_extractor import RequirementExtractor
        from .parser.user_story_generator import UserStoryGenerator
        from .parser.data_model_parser import DataModelParser
        from .parser.api_spec_parser import APISpecificationParser
        from .parser.constraint_analyzer import ConstraintAnalyzer
        from .parser.parsing_rules import ParsingRuleEngine
        from .parser.requirement_validator import RequirementValidator

        self.requirement_extractor = RequirementExtractor()
        self.user_story_generator = UserStoryGenerator()
        self.data_model_parser = DataModelParser()
        self.api_spec_parser = APISpecificationParser()
        self.constraint_analyzer = ConstraintAnalyzer()
        self.parsing_rules = ParsingRuleEngine()
        self.requirement_validator = RequirementValidator()

    async def parse_requirements(
        self,
        raw_description: str,
        project_context: Optional[Dict[str, Any]] = None,
        parsing_options: Optional[Dict[str, Any]] = None
    ) -> ParsedProject:
        """프로젝트 요구사항 파싱"""

        # 1. 전처리
        preprocessed_text = await self._preprocess_text(raw_description, project_context)

        # 2. 기본 구조 파싱
        base_structure = await self._parse_base_structure(preprocessed_text)

        # 3. 병렬 상세 파싱
        parsing_tasks = [
            self._parse_functional_requirements(base_structure),
            self._parse_non_functional_requirements(base_structure),
            self._parse_technical_requirements(base_structure),
            self._parse_business_requirements(base_structure),
            self._parse_constraints(base_structure),
            self._parse_assumptions(base_structure),
            self._generate_user_stories(base_structure),
            self._extract_use_cases(base_structure),
            self._parse_data_models(base_structure),
            self._parse_api_specifications(base_structure),
            self._identify_ui_components(base_structure),
            self._identify_integration_points(base_structure)
        ]

        results = await asyncio.gather(*parsing_tasks)

        # 4. 결과 조합
        parsed_project = ParsedProject(
            project_info=base_structure.get('project_info', {}),
            functional_requirements=results[0],
            non_functional_requirements=results[1],
            technical_requirements=results[2],
            business_requirements=results[3],
            constraints=results[4],
            assumptions=results[5],
            user_stories=results[6],
            use_cases=results[7],
            data_models=results[8],
            api_specifications=results[9],
            ui_components=results[10],
            integration_points=results[11]
        )

        # 5. 검증 및 보완
        validated_project = await self._validate_and_enrich(parsed_project)

        return validated_project

    async def _preprocess_text(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """텍스트 전처리"""
        # 구조화된 섹션 감지
        sections = self._detect_sections(text)
        
        # 약어 및 전문 용어 확장
        expanded_text = self._expand_abbreviations(text, context)
        
        # 참조 해결
        resolved_text = self._resolve_references(expanded_text, context)
        
        # 형식 정규화
        normalized_text = self._normalize_format(resolved_text)
        
        return normalized_text

    def _detect_sections(self, text: str) -> Dict[str, str]:
        """구조화된 섹션 감지"""
        sections = {}
        section_patterns = {
            'requirements': r'(?i)(requirements?|기능|요구사항)',
            'features': r'(?i)(features?|기능|특징)',
            'constraints': r'(?i)(constraints?|제약|한계)',
            'api': r'(?i)(api|endpoint|interface)',
            'data': r'(?i)(data|database|model|스키마)'
        }
        
        for section_name, pattern in section_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                sections[section_name] = text[match.start():match.start()+200]
        
        return sections

    def _expand_abbreviations(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """약어 및 전문 용어 확장"""
        abbreviations = {
            'API': 'Application Programming Interface',
            'UI': 'User Interface',
            'UX': 'User Experience',
            'DB': 'Database',
            'CRUD': 'Create Read Update Delete',
            'REST': 'Representational State Transfer',
            'JWT': 'JSON Web Token',
            'OAuth': 'Open Authorization'
        }
        
        expanded = text
        for abbr, full in abbreviations.items():
            expanded = re.sub(rf'\b{abbr}\b', f'{abbr} ({full})', expanded)
        
        return expanded

    def _resolve_references(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """참조 해결"""
        # 간단한 참조 해결 (실제로는 더 복잡한 로직 필요)
        resolved = text
        if context and 'previous_requirements' in context:
            resolved = resolved.replace('as mentioned above', str(context['previous_requirements']))
        
        return resolved

    def _normalize_format(self, text: str) -> str:
        """형식 정규화"""
        # 여러 공백을 하나로
        normalized = re.sub(r'\s+', ' ', text)
        # 줄바꿈 정리
        normalized = re.sub(r'\n\s*\n', '\n\n', normalized)
        
        return normalized.strip()

    async def _parse_base_structure(self, text: str) -> Dict[str, Any]:
        """기본 구조 파싱"""
        prompt = f"""
        Parse the following project requirements and extract the basic structure:

        {text}

        Extract:
        1. Project name and description
        2. Project type (web, mobile, desktop, api, etc.)
        3. Target users and stakeholders
        4. High-level goals and objectives
        5. Key features and functionalities
        6. Technical context and constraints
        7. Timeline and milestones
        8. Success criteria

        Return as structured JSON.
        """

        result = await self.main_parser.arun(prompt)
        return self._parse_json_response(result.content)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        try:
            # JSON 블록 추출
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # 직접 JSON 파싱 시도
            return json.loads(response)
        except json.JSONDecodeError:
            # 파싱 실패 시 기본 구조 반환
            return {
                'project_info': {'name': 'Unknown Project'},
                'key_features': [],
                'technical_context': {},
                'constraints': []
            }

    async def _parse_functional_requirements(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """기능 요구사항 파싱"""
        features = base_structure.get('key_features', [])
        requirements = []

        for idx, feature in enumerate(features):
            detailed_reqs = await self.requirement_extractor.extract_functional(
                feature, context=base_structure
            )

            for req_idx, req in enumerate(detailed_reqs):
                parsed_req = ParsedRequirement(
                    id=f"FR-{idx+1:03d}-{req_idx+1:02d}",
                    type=RequirementType.FUNCTIONAL,
                    category=req.get('category', 'general'),
                    description=req.get('description', ''),
                    priority=req.get('priority', 'medium'),
                    dependencies=req.get('dependencies', []),
                    acceptance_criteria=req.get('acceptance_criteria', []),
                    technical_details=req.get('technical_details', {}),
                    metadata={
                        'feature': feature,
                        'extracted_at': datetime.utcnow().isoformat()
                    }
                )
                requirements.append(parsed_req)

        return requirements

    async def _parse_non_functional_requirements(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """비기능 요구사항 파싱"""
        return await self.requirement_extractor.extract_non_functional(base_structure)

    async def _parse_technical_requirements(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """기술 요구사항 파싱"""
        return await self.requirement_extractor.extract_technical(base_structure)

    async def _parse_business_requirements(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """비즈니스 요구사항 파싱"""
        return await self.requirement_extractor.extract_business(base_structure)

    async def _parse_constraints(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """제약사항 파싱"""
        return await self.constraint_analyzer.analyze(base_structure)

    async def _parse_assumptions(self, base_structure: Dict[str, Any]) -> List[ParsedRequirement]:
        """가정사항 파싱"""
        assumptions = base_structure.get('assumptions', [])
        return [
            ParsedRequirement(
                id=f"AS-{idx+1:03d}",
                type=RequirementType.ASSUMPTION,
                category='assumption',
                description=assumption,
                priority='low'
            ) for idx, assumption in enumerate(assumptions)
        ]

    async def _generate_user_stories(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """사용자 스토리 생성"""
        return await self.user_story_generator.generate(base_structure)

    async def _extract_use_cases(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """사용 사례 추출"""
        features = base_structure.get('key_features', [])
        use_cases = []
        
        for feature in features:
            use_case = {
                'name': f"Use Case: {feature}",
                'description': f"User interacts with {feature}",
                'actors': ['User'],
                'preconditions': [],
                'steps': [],
                'postconditions': []
            }
            use_cases.append(use_case)
        
        return use_cases

    async def _parse_data_models(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """데이터 모델 파싱"""
        return await self.data_model_parser.parse(base_structure)

    async def _parse_api_specifications(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API 명세 파싱"""
        return await self.api_spec_parser.parse(base_structure)

    async def _identify_ui_components(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """UI 컴포넌트 식별"""
        features = base_structure.get('key_features', [])
        ui_components = []
        
        ui_keywords = ['form', 'button', 'table', 'list', 'menu', 'dashboard']
        
        for feature in features:
            for keyword in ui_keywords:
                if keyword.lower() in feature.lower():
                    ui_components.append({
                        'name': f"{keyword.title()} Component",
                        'type': keyword,
                        'feature': feature
                    })
        
        return ui_components

    async def _identify_integration_points(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """통합 지점 식별"""
        integrations = []
        tech_context = base_structure.get('technical_context', {})
        
        if 'external_apis' in tech_context:
            for api in tech_context['external_apis']:
                integrations.append({
                    'type': 'external_api',
                    'name': api,
                    'method': 'REST'
                })
        
        return integrations

    async def _validate_and_enrich(self, project: ParsedProject) -> ParsedProject:
        """검증 및 보완"""
        validated = await self.requirement_validator.validate(project)
        return validated