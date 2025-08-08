"""
Parser Agent Core Implementation
Phase 4 Tasks 4.21-4.30: 요구사항 파싱 및 구조화 에이전트
"""

import json
import logging
import os
import time
import re
import asyncio
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from botocore.exceptions import ClientError

# Agno Framework 통합
try:
    from agno.agent import Agent
    from agno.models.aws import AwsBedrock
    from agno.memory import ConversationSummaryMemory
    from agno.tools import Tool
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

# Production 로깅 설정
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# AWS 클라이언트
ssm = boto3.client('ssm')
secrets = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
comprehend = boto3.client('comprehend')


class RequirementType(Enum):
    """요구사항 타입 분류"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non-functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    CONSTRAINT = "constraint"
    USER_STORY = "user-story"


class RequirementPriority(Enum):
    """요구사항 우선순위"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NICE_TO_HAVE = "nice-to-have"


@dataclass
class ParsedRequirement:
    """파싱된 개별 요구사항"""
    id: str
    type: RequirementType
    title: str
    description: str
    priority: RequirementPriority
    acceptance_criteria: List[str]
    dependencies: List[str]
    constraints: List[str]
    metadata: Dict[str, Any]
    confidence_score: float


@dataclass
class UserStory:
    """사용자 스토리"""
    id: str
    as_a: str  # 사용자 역할
    i_want: str  # 원하는 기능
    so_that: str  # 목적/가치
    acceptance_criteria: List[str]
    story_points: Optional[int] = None
    priority: RequirementPriority = RequirementPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DataModel:
    """데이터 모델 정의"""
    name: str
    type: str  # entity, value_object, aggregate
    attributes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    constraints: List[str]
    indexes: List[str]
    validations: Dict[str, Any]


@dataclass
class APISpecification:
    """API 명세"""
    endpoint: str
    method: str
    description: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    parameters: List[Dict[str, Any]]
    headers: List[Dict[str, Any]]
    authentication: Dict[str, Any]
    rate_limiting: Optional[Dict[str, Any]] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class UIComponent:
    """UI 컴포넌트 정의"""
    name: str
    type: str  # page, component, layout
    description: str
    properties: Dict[str, Any]
    events: List[Dict[str, Any]]
    data_bindings: List[str]
    child_components: List[str]
    styling_requirements: Dict[str, Any]


@dataclass
class IntegrationPoint:
    """통합 포인트 정의"""
    name: str
    type: str  # internal, external, third-party
    source: str
    target: str
    protocol: str
    data_format: str
    security_requirements: List[str]
    error_handling: Dict[str, Any]


@dataclass
class ParsedProject:
    """완전히 파싱된 프로젝트 구조"""
    # Task 4.21: 핵심 파싱 결과
    project_info: Dict[str, Any]
    functional_requirements: List[ParsedRequirement]
    non_functional_requirements: List[ParsedRequirement]
    technical_requirements: List[ParsedRequirement]
    business_requirements: List[ParsedRequirement]
    
    # Task 4.22: 사용자 스토리
    user_stories: List[UserStory]
    use_cases: List[Dict[str, Any]]
    
    # Task 4.23: 데이터 모델
    data_models: List[DataModel]
    database_schema: Dict[str, Any]
    
    # Task 4.24: API 명세
    api_specifications: List[APISpecification]
    
    # Task 4.25: UI 컴포넌트
    ui_components: List[UIComponent]
    navigation_flow: Dict[str, Any]
    
    # Task 4.26: 통합 포인트
    integration_points: List[IntegrationPoint]
    
    # Task 4.27: 제약사항
    constraints: List[Dict[str, Any]]
    assumptions: List[str]
    risks: List[Dict[str, Any]]
    
    # Task 4.28: 의존성
    dependency_graph: Dict[str, List[str]]
    
    # Task 4.29: 검증 규칙
    validation_rules: List[Dict[str, Any]]
    
    # Task 4.30: 메타데이터
    metadata: Dict[str, Any]
    parsing_confidence: float
    traceability_matrix: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return asdict(self)


class RequirementParser(Tool):
    """요구사항 파싱 도구 (Agno Tool)"""
    
    def __init__(self):
        super().__init__(
            name="requirement_parser",
            description="Parse and structure requirements from natural language"
        )
    
    async def run(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """요구사항 파싱 실행"""
        # NLP 기반 파싱
        entities = await self._extract_entities(text)
        intents = await self._extract_intents(text)
        
        # 요구사항 분류
        requirements = self._classify_requirements(text, entities, intents)
        
        return {
            "requirements": requirements,
            "entities": entities,
            "intents": intents
        }
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """엔티티 추출"""
        try:
            response = comprehend.detect_entities(Text=text, LanguageCode='en')
            return response.get('Entities', [])
        except:
            # Fallback to pattern matching
            return self._extract_entities_fallback(text)
    
    async def _extract_intents(self, text: str) -> List[str]:
        """의도 추출"""
        intents = []
        intent_patterns = {
            'create': r'(create|make|build|generate|add)',
            'read': r'(view|show|display|list|get)',
            'update': r'(update|modify|edit|change)',
            'delete': r'(delete|remove|destroy)',
            'search': r'(search|find|query|filter)',
            'authenticate': r'(login|authenticate|authorize)',
            'validate': r'(validate|verify|check)',
            'integrate': r'(integrate|connect|sync)'
        }
        
        text_lower = text.lower()
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, text_lower):
                intents.append(intent)
        
        return intents
    
    def _classify_requirements(
        self, 
        text: str, 
        entities: List[Dict],
        intents: List[str]
    ) -> List[Dict[str, Any]]:
        """요구사항 분류"""
        requirements = []
        
        # 문장 단위로 분리
        sentences = text.split('.')
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            req_type = self._determine_requirement_type(sentence)
            priority = self._determine_priority(sentence)
            
            requirements.append({
                'text': sentence.strip(),
                'type': req_type,
                'priority': priority,
                'entities': [e for e in entities if e.get('Text', '') in sentence],
                'intents': [i for i in intents if i in sentence.lower()]
            })
        
        return requirements
    
    def _determine_requirement_type(self, text: str) -> str:
        """요구사항 타입 결정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['performance', 'security', 'scalability']):
            return RequirementType.NON_FUNCTIONAL.value
        elif any(word in text_lower for word in ['api', 'database', 'framework']):
            return RequirementType.TECHNICAL.value
        elif any(word in text_lower for word in ['revenue', 'cost', 'market']):
            return RequirementType.BUSINESS.value
        elif any(word in text_lower for word in ['must not', 'cannot', 'limit']):
            return RequirementType.CONSTRAINT.value
        else:
            return RequirementType.FUNCTIONAL.value
    
    def _determine_priority(self, text: str) -> str:
        """우선순위 결정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'must', 'essential']):
            return RequirementPriority.CRITICAL.value
        elif any(word in text_lower for word in ['important', 'should']):
            return RequirementPriority.HIGH.value
        elif any(word in text_lower for word in ['nice to have', 'optional']):
            return RequirementPriority.LOW.value
        else:
            return RequirementPriority.MEDIUM.value
    
    def _extract_entities_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback 엔티티 추출"""
        entities = []
        
        # 패턴 기반 추출
        patterns = {
            'USER': r'\b(user|customer|client|member)\b',
            'PRODUCT': r'\b(product|item|service)\b',
            'LOCATION': r'\b(location|address|place)\b',
            'ORGANIZATION': r'\b(company|organization|team)\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'Type': entity_type,
                    'Text': match.group(),
                    'BeginOffset': match.start(),
                    'EndOffset': match.end()
                })
        
        return entities


class ParserAgent:
    """Production-ready Parser Agent with full Task 4.21-4.30 implementation"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # Agno Agent 초기화
        if AGNO_AVAILABLE:
            self._init_agno_agent()
        else:
            logger.warning("Agno Framework not available, using fallback mode")
            self.agent = None
        
        # 컴포넌트 초기화
        self._init_components()
        
        # 패턴 및 규칙 초기화
        self._init_parsing_rules()
        
        # 메트릭 초기화
        self.parsing_times = []
        self.accuracy_scores = []
        
        logger.info(f"Parser Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/parser-agent/',
                Recursive=True,
                WithDecryption=True
            )
            
            config = {}
            for param in response['Parameters']:
                key = param['Name'].split('/')[-1]
                config[key] = param['Value']
            
            return config
        except ClientError as e:
            logger.error(f"Failed to load config: {e}")
            return {
                'max_parsing_depth': 5,
                'min_confidence_score': 0.6,
                'timeout_seconds': 60,
                'use_agno': True,
                'use_comprehend': True,
                'parallel_processing': True
            }
    
    def _init_agno_agent(self):
        """Agno 에이전트 초기화"""
        try:
            self.agent = Agent(
                name="Requirements-Parser",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-v2:0",
                    region="us-east-1"
                ),
                role="Expert requirements analyst and system architect",
                instructions=[
                    "Parse and structure project requirements comprehensively",
                    "Identify all types of requirements (functional, non-functional, technical, business)",
                    "Generate user stories and use cases",
                    "Extract data models and API specifications",
                    "Identify UI components and integration points",
                    "Analyze constraints and dependencies",
                    "Create traceability matrix"
                ],
                memory=ConversationSummaryMemory(
                    storage_type="dynamodb",
                    table_name=f"t-dev-parser-sessions-{self.environment}"
                ),
                tools=[
                    RequirementParser()
                ],
                temperature=0.2,
                max_retries=3
            )
            logger.info("Agno agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno agent: {e}")
            self.agent = None
    
    def _init_components(self):
        """컴포넌트 초기화"""
        # 지연 import로 순환 참조 방지
        from .requirement_extractor import RequirementExtractor
        from .user_story_generator import UserStoryGenerator
        from .data_model_parser import DataModelParser
        from .api_spec_parser import APISpecificationParser
        from .ui_component_identifier import UIComponentIdentifier
        from .integration_analyzer import IntegrationAnalyzer
        from .constraint_analyzer import ConstraintAnalyzer
        from .dependency_analyzer import DependencyAnalyzer
        from .validation_framework import ValidationFramework
        from .traceability_generator import TraceabilityGenerator
        
        self.requirement_extractor = RequirementExtractor()
        self.user_story_generator = UserStoryGenerator()
        self.data_model_parser = DataModelParser()
        self.api_spec_parser = APISpecificationParser()
        self.ui_component_identifier = UIComponentIdentifier()
        self.integration_analyzer = IntegrationAnalyzer()
        self.constraint_analyzer = ConstraintAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.validation_framework = ValidationFramework()
        self.traceability_generator = TraceabilityGenerator()
    
    def _init_parsing_rules(self):
        """파싱 규칙 초기화"""
        # 요구사항 패턴
        self.requirement_patterns = {
            'functional': [
                r'(?:system|application|user) (?:shall|must|should) (\w+)',
                r'(?:ability|feature) to (\w+)',
                r'(?:allow|enable|provide) (\w+)',
            ],
            'non_functional': [
                r'(?:performance|security|reliability) (?:requirement|constraint)',
                r'(?:response time|throughput|availability) (?:shall|must) be',
                r'(?:encrypt|secure|protect) (?:data|information)',
            ],
            'technical': [
                r'(?:use|implement|integrate) (?:framework|library|service)',
                r'(?:database|api|architecture) (?:design|specification)',
                r'(?:technology|platform|language) (?:stack|choice)',
            ],
            'business': [
                r'(?:business|market|revenue) (?:goal|objective|requirement)',
                r'(?:cost|budget|timeline) (?:constraint|limitation)',
                r'(?:compliance|regulation|policy) (?:requirement)',
            ]
        }
        
        # 사용자 스토리 템플릿
        self.story_templates = {
            'standard': "As a {role}, I want {feature} so that {benefit}",
            'extended': "As a {role}, I want {feature} so that {benefit}, given {context}",
            'epic': "As {stakeholder}, we need {capability} to {objective}"
        }
        
        # 데이터 모델 패턴
        self.data_patterns = {
            'entity': r'(?:entity|model|object) (\w+)',
            'attribute': r'(?:field|property|attribute) (\w+)',
            'relationship': r'(\w+) (?:has|contains|references) (\w+)',
            'constraint': r'(?:unique|required|nullable|index) (\w+)'
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    async def parse_project(
        self,
        input_data: Dict[str, Any],
        use_agno: bool = True,
        deep_parsing: bool = True
    ) -> ParsedProject:
        """
        프로젝트 요구사항 완전 파싱 (Task 4.21-4.30)
        
        Args:
            input_data: NL Input Agent의 출력
            use_agno: Agno Framework 사용 여부
            deep_parsing: 심층 파싱 수행 여부
            
        Returns:
            ParsedProject: 완전히 파싱된 프로젝트 구조
        """
        start_time = time.time()
        
        try:
            # 1. 입력 검증
            self._validate_input(input_data)
            
            # 2. 기본 파싱 (Task 4.21)
            if use_agno and self.agent:
                base_parsing = await self._parse_with_agno(input_data)
            else:
                base_parsing = await self._parse_with_fallback(input_data)
            
            # 3. 심층 파싱 (Tasks 4.22-4.30)
            if deep_parsing:
                # 병렬 처리
                parsing_tasks = [
                    self._generate_user_stories(base_parsing),  # Task 4.22
                    self._parse_data_models(base_parsing),  # Task 4.23
                    self._parse_api_specifications(base_parsing),  # Task 4.24
                    self._identify_ui_components(base_parsing),  # Task 4.25
                    self._analyze_integrations(base_parsing),  # Task 4.26
                    self._analyze_constraints(base_parsing),  # Task 4.27
                    self._analyze_dependencies(base_parsing),  # Task 4.28
                    self._create_validation_rules(base_parsing),  # Task 4.29
                    self._generate_traceability(base_parsing)  # Task 4.30
                ]
                
                results = await asyncio.gather(*parsing_tasks)
                
                # 결과 통합
                parsed_project = self._merge_results(base_parsing, results)
            else:
                parsed_project = base_parsing
            
            # 4. 검증
            validation_result = await self.validation_framework.validate(parsed_project)
            parsed_project.metadata['validation'] = validation_result
            
            # 5. 최적화
            if self.config.get('optimize_output', True):
                parsed_project = self._optimize_output(parsed_project)
            
            # 6. 메트릭 기록
            processing_time = time.time() - start_time
            self.parsing_times.append(processing_time)
            metrics.add_metric(
                name="ParsingTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            
            # 7. 정확도 계산
            accuracy = self._calculate_accuracy(parsed_project)
            self.accuracy_scores.append(accuracy)
            
            logger.info(
                "Successfully parsed project",
                extra={
                    "requirements_count": len(parsed_project.functional_requirements),
                    "user_stories_count": len(parsed_project.user_stories),
                    "data_models_count": len(parsed_project.data_models),
                    "processing_time": processing_time,
                    "accuracy": accuracy
                }
            )
            
            return parsed_project
            
        except Exception as e:
            logger.error(f"Error parsing project: {e}")
            metrics.add_metric(name="ParsingError", unit=MetricUnit.Count, value=1)
            raise
    
    async def _parse_with_agno(self, input_data: Dict[str, Any]) -> ParsedProject:
        """Agno Agent를 사용한 파싱"""
        
        # 프롬프트 구성
        parsing_prompt = f"""
        Parse the following project requirements into a structured format:
        
        Input: {json.dumps(input_data, ensure_ascii=False)}
        
        Extract and structure:
        1. Functional requirements with acceptance criteria
        2. Non-functional requirements (performance, security, etc.)
        3. Technical requirements and specifications
        4. Business requirements and constraints
        5. User stories in standard format
        6. Data models and relationships
        7. API endpoints and specifications
        8. UI components and navigation flow
        9. Integration points
        10. Dependencies and constraints
        
        Return structured JSON with all extracted information.
        """
        
        # Agno Agent 실행
        result = await self.agent.arun(parsing_prompt)
        
        # 결과 파싱
        return self._parse_agno_result(result, input_data)
    
    async def _parse_with_fallback(self, input_data: Dict[str, Any]) -> ParsedProject:
        """Fallback 파싱 (Agno 없이)"""
        
        description = input_data.get('description', '')
        
        # 요구사항 추출
        functional_reqs = await self._extract_requirements(
            description, RequirementType.FUNCTIONAL
        )
        non_functional_reqs = await self._extract_requirements(
            description, RequirementType.NON_FUNCTIONAL
        )
        technical_reqs = await self._extract_requirements(
            description, RequirementType.TECHNICAL
        )
        business_reqs = await self._extract_requirements(
            description, RequirementType.BUSINESS
        )
        
        # 프로젝트 정보 생성
        project_info = {
            'name': input_data.get('project_name', 'Unnamed Project'),
            'type': input_data.get('project_type', 'unknown'),
            'description': description,
            'complexity': input_data.get('estimated_complexity', 'medium')
        }
        
        return ParsedProject(
            project_info=project_info,
            functional_requirements=functional_reqs,
            non_functional_requirements=non_functional_reqs,
            technical_requirements=technical_reqs,
            business_requirements=business_reqs,
            user_stories=[],
            use_cases=[],
            data_models=[],
            database_schema={},
            api_specifications=[],
            ui_components=[],
            navigation_flow={},
            integration_points=[],
            constraints=[],
            assumptions=[],
            risks=[],
            dependency_graph={},
            validation_rules=[],
            metadata={
                'agent_name': 'parser-agent',
                'version': '1.0.0',
                'environment': self.environment,
                'timestamp': time.time()
            },
            parsing_confidence=0.7,
            traceability_matrix={}
        )
    
    async def _extract_requirements(
        self, 
        text: str, 
        req_type: RequirementType
    ) -> List[ParsedRequirement]:
        """특정 타입의 요구사항 추출"""
        requirements = []
        
        # 패턴 매칭
        patterns = self.requirement_patterns.get(req_type.value, [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                req_text = match.group(0)
                
                # 요구사항 생성
                requirement = ParsedRequirement(
                    id=f"{req_type.value}_{len(requirements)+1}",
                    type=req_type,
                    title=self._generate_title(req_text),
                    description=req_text,
                    priority=self._determine_priority(req_text),
                    acceptance_criteria=self._extract_acceptance_criteria(req_text),
                    dependencies=[],
                    constraints=[],
                    metadata={'source': 'pattern_matching'},
                    confidence_score=0.7
                )
                
                requirements.append(requirement)
        
        return requirements
    
    async def _generate_user_stories(self, base_parsing: ParsedProject) -> List[UserStory]:
        """Task 4.22: 사용자 스토리 생성"""
        stories = []
        
        # 기능 요구사항에서 사용자 스토리 생성
        for req in base_parsing.functional_requirements:
            story = await self.user_story_generator.generate_from_requirement(req)
            if story:
                stories.append(story)
        
        # 추가 스토리 생성
        additional_stories = await self.user_story_generator.generate_additional_stories(
            base_parsing.project_info
        )
        stories.extend(additional_stories)
        
        return stories
    
    async def _parse_data_models(self, base_parsing: ParsedProject) -> Tuple[List[DataModel], Dict]:
        """Task 4.23: 데이터 모델 파싱"""
        models = await self.data_model_parser.parse(base_parsing)
        schema = await self.data_model_parser.generate_schema(models)
        return models, schema
    
    async def _parse_api_specifications(self, base_parsing: ParsedProject) -> List[APISpecification]:
        """Task 4.24: API 명세 파싱"""
        return await self.api_spec_parser.parse(base_parsing)
    
    async def _identify_ui_components(self, base_parsing: ParsedProject) -> Tuple[List[UIComponent], Dict]:
        """Task 4.25: UI 컴포넌트 식별"""
        components = await self.ui_component_identifier.identify(base_parsing)
        navigation = await self.ui_component_identifier.generate_navigation_flow(components)
        return components, navigation
    
    async def _analyze_integrations(self, base_parsing: ParsedProject) -> List[IntegrationPoint]:
        """Task 4.26: 통합 포인트 분석"""
        return await self.integration_analyzer.analyze(base_parsing)
    
    async def _analyze_constraints(self, base_parsing: ParsedProject) -> Tuple[List[Dict], List[str], List[Dict]]:
        """Task 4.27: 제약사항 분석"""
        constraints = await self.constraint_analyzer.analyze_constraints(base_parsing)
        assumptions = await self.constraint_analyzer.identify_assumptions(base_parsing)
        risks = await self.constraint_analyzer.assess_risks(base_parsing)
        return constraints, assumptions, risks
    
    async def _analyze_dependencies(self, base_parsing: ParsedProject) -> Dict[str, List[str]]:
        """Task 4.28: 의존성 분석"""
        return await self.dependency_analyzer.build_dependency_graph(base_parsing)
    
    async def _create_validation_rules(self, base_parsing: ParsedProject) -> List[Dict]:
        """Task 4.29: 검증 규칙 생성"""
        return await self.validation_framework.create_rules(base_parsing)
    
    async def _generate_traceability(self, base_parsing: ParsedProject) -> Dict[str, Any]:
        """Task 4.30: 추적성 매트릭스 생성"""
        return await self.traceability_generator.generate(base_parsing)
    
    def _merge_results(
        self, 
        base_parsing: ParsedProject,
        results: List[Any]
    ) -> ParsedProject:
        """파싱 결과 병합"""
        # Task 4.22 결과
        base_parsing.user_stories = results[0]
        
        # Task 4.23 결과
        base_parsing.data_models, base_parsing.database_schema = results[1]
        
        # Task 4.24 결과
        base_parsing.api_specifications = results[2]
        
        # Task 4.25 결과
        base_parsing.ui_components, base_parsing.navigation_flow = results[3]
        
        # Task 4.26 결과
        base_parsing.integration_points = results[4]
        
        # Task 4.27 결과
        constraints, assumptions, risks = results[5]
        base_parsing.constraints = constraints
        base_parsing.assumptions = assumptions
        base_parsing.risks = risks
        
        # Task 4.28 결과
        base_parsing.dependency_graph = results[6]
        
        # Task 4.29 결과
        base_parsing.validation_rules = results[7]
        
        # Task 4.30 결과
        base_parsing.traceability_matrix = results[8]
        
        return base_parsing
    
    def _optimize_output(self, parsed_project: ParsedProject) -> ParsedProject:
        """출력 최적화"""
        # 중복 제거
        parsed_project.functional_requirements = self._remove_duplicates(
            parsed_project.functional_requirements
        )
        
        # 우선순위 정렬
        parsed_project.functional_requirements.sort(
            key=lambda x: x.priority.value
        )
        
        # 의존성 정렬
        parsed_project.user_stories = self._topological_sort(
            parsed_project.user_stories,
            parsed_project.dependency_graph
        )
        
        return parsed_project
    
    def _calculate_accuracy(self, parsed_project: ParsedProject) -> float:
        """파싱 정확도 계산"""
        scores = []
        
        # 요구사항 완전성
        req_completeness = min(
            len(parsed_project.functional_requirements) / 10, 1.0
        )
        scores.append(req_completeness)
        
        # 사용자 스토리 품질
        story_quality = sum(
            1 for s in parsed_project.user_stories 
            if s.as_a and s.i_want and s.so_that
        ) / max(len(parsed_project.user_stories), 1)
        scores.append(story_quality)
        
        # 데이터 모델 완전성
        model_completeness = min(
            len(parsed_project.data_models) / 5, 1.0
        )
        scores.append(model_completeness)
        
        # API 명세 완전성
        api_completeness = min(
            len(parsed_project.api_specifications) / 10, 1.0
        )
        scores.append(api_completeness)
        
        return sum(scores) / len(scores)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """입력 검증"""
        if not input_data:
            raise ValueError("Input data is empty")
        
        if 'description' not in input_data:
            raise ValueError("Project description is required")
        
        if not input_data['description'].strip():
            raise ValueError("Project description cannot be empty")
    
    def _generate_title(self, text: str) -> str:
        """요구사항 제목 생성"""
        # 첫 50자 또는 첫 문장
        title = text[:50]
        if '.' in text[:50]:
            title = text.split('.')[0]
        return title.strip()
    
    def _determine_priority(self, text: str) -> RequirementPriority:
        """우선순위 결정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'must', 'essential']):
            return RequirementPriority.CRITICAL
        elif any(word in text_lower for word in ['important', 'should']):
            return RequirementPriority.HIGH
        elif any(word in text_lower for word in ['nice to have', 'optional']):
            return RequirementPriority.LOW
        else:
            return RequirementPriority.MEDIUM
    
    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """수용 기준 추출"""
        criteria = []
        
        # Given-When-Then 패턴
        gwt_pattern = r'given .+ when .+ then .+'
        matches = re.finditer(gwt_pattern, text, re.IGNORECASE)
        for match in matches:
            criteria.append(match.group(0))
        
        # 조건문 패턴
        if_pattern = r'if .+ then .+'
        matches = re.finditer(if_pattern, text, re.IGNORECASE)
        for match in matches:
            criteria.append(match.group(0))
        
        return criteria
    
    def _remove_duplicates(self, requirements: List[ParsedRequirement]) -> List[ParsedRequirement]:
        """중복 제거"""
        seen = set()
        unique = []
        
        for req in requirements:
            key = req.description.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(req)
        
        return unique
    
    def _topological_sort(
        self,
        items: List[Any],
        dependency_graph: Dict[str, List[str]]
    ) -> List[Any]:
        """위상 정렬"""
        # 간단한 구현 (실제로는 더 복잡한 알고리즘 필요)
        return items
    
    def _parse_agno_result(self, result: str, input_data: Dict[str, Any]) -> ParsedProject:
        """Agno 결과 파싱"""
        try:
            if isinstance(result, str):
                data = json.loads(result)
            else:
                data = result
            
            # ParsedProject 객체 생성
            return ParsedProject(
                project_info=data.get('project_info', {}),
                functional_requirements=self._convert_requirements(
                    data.get('functional_requirements', []),
                    RequirementType.FUNCTIONAL
                ),
                non_functional_requirements=self._convert_requirements(
                    data.get('non_functional_requirements', []),
                    RequirementType.NON_FUNCTIONAL
                ),
                technical_requirements=self._convert_requirements(
                    data.get('technical_requirements', []),
                    RequirementType.TECHNICAL
                ),
                business_requirements=self._convert_requirements(
                    data.get('business_requirements', []),
                    RequirementType.BUSINESS
                ),
                user_stories=self._convert_user_stories(data.get('user_stories', [])),
                use_cases=data.get('use_cases', []),
                data_models=self._convert_data_models(data.get('data_models', [])),
                database_schema=data.get('database_schema', {}),
                api_specifications=self._convert_api_specs(data.get('api_specifications', [])),
                ui_components=self._convert_ui_components(data.get('ui_components', [])),
                navigation_flow=data.get('navigation_flow', {}),
                integration_points=self._convert_integrations(data.get('integration_points', [])),
                constraints=data.get('constraints', []),
                assumptions=data.get('assumptions', []),
                risks=data.get('risks', []),
                dependency_graph=data.get('dependency_graph', {}),
                validation_rules=data.get('validation_rules', []),
                metadata=data.get('metadata', {}),
                parsing_confidence=data.get('confidence', 0.8),
                traceability_matrix=data.get('traceability_matrix', {})
            )
        except Exception as e:
            logger.error(f"Failed to parse Agno result: {e}")
            return self._parse_with_fallback(input_data)
    
    def _convert_requirements(
        self,
        req_list: List[Dict],
        req_type: RequirementType
    ) -> List[ParsedRequirement]:
        """요구사항 변환"""
        requirements = []
        
        for idx, req_data in enumerate(req_list):
            requirement = ParsedRequirement(
                id=req_data.get('id', f"{req_type.value}_{idx+1}"),
                type=req_type,
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                priority=RequirementPriority(req_data.get('priority', 'medium')),
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                dependencies=req_data.get('dependencies', []),
                constraints=req_data.get('constraints', []),
                metadata=req_data.get('metadata', {}),
                confidence_score=req_data.get('confidence', 0.8)
            )
            requirements.append(requirement)
        
        return requirements
    
    def _convert_user_stories(self, story_list: List[Dict]) -> List[UserStory]:
        """사용자 스토리 변환"""
        stories = []
        
        for story_data in story_list:
            story = UserStory(
                id=story_data.get('id', ''),
                as_a=story_data.get('as_a', ''),
                i_want=story_data.get('i_want', ''),
                so_that=story_data.get('so_that', ''),
                acceptance_criteria=story_data.get('acceptance_criteria', []),
                story_points=story_data.get('story_points'),
                priority=RequirementPriority(story_data.get('priority', 'medium')),
                dependencies=story_data.get('dependencies', [])
            )
            stories.append(story)
        
        return stories
    
    def _convert_data_models(self, model_list: List[Dict]) -> List[DataModel]:
        """데이터 모델 변환"""
        models = []
        
        for model_data in model_list:
            model = DataModel(
                name=model_data.get('name', ''),
                type=model_data.get('type', 'entity'),
                attributes=model_data.get('attributes', []),
                relationships=model_data.get('relationships', []),
                constraints=model_data.get('constraints', []),
                indexes=model_data.get('indexes', []),
                validations=model_data.get('validations', {})
            )
            models.append(model)
        
        return models
    
    def _convert_api_specs(self, spec_list: List[Dict]) -> List[APISpecification]:
        """API 명세 변환"""
        specs = []
        
        for spec_data in spec_list:
            spec = APISpecification(
                endpoint=spec_data.get('endpoint', ''),
                method=spec_data.get('method', 'GET'),
                description=spec_data.get('description', ''),
                request_schema=spec_data.get('request_schema', {}),
                response_schema=spec_data.get('response_schema', {}),
                parameters=spec_data.get('parameters', []),
                headers=spec_data.get('headers', []),
                authentication=spec_data.get('authentication', {}),
                rate_limiting=spec_data.get('rate_limiting'),
                examples=spec_data.get('examples', [])
            )
            specs.append(spec)
        
        return specs
    
    def _convert_ui_components(self, comp_list: List[Dict]) -> List[UIComponent]:
        """UI 컴포넌트 변환"""
        components = []
        
        for comp_data in comp_list:
            component = UIComponent(
                name=comp_data.get('name', ''),
                type=comp_data.get('type', 'component'),
                description=comp_data.get('description', ''),
                properties=comp_data.get('properties', {}),
                events=comp_data.get('events', []),
                data_bindings=comp_data.get('data_bindings', []),
                child_components=comp_data.get('child_components', []),
                styling_requirements=comp_data.get('styling_requirements', {})
            )
            components.append(component)
        
        return components
    
    def _convert_integrations(self, int_list: List[Dict]) -> List[IntegrationPoint]:
        """통합 포인트 변환"""
        integrations = []
        
        for int_data in int_list:
            integration = IntegrationPoint(
                name=int_data.get('name', ''),
                type=int_data.get('type', 'internal'),
                source=int_data.get('source', ''),
                target=int_data.get('target', ''),
                protocol=int_data.get('protocol', ''),
                data_format=int_data.get('data_format', ''),
                security_requirements=int_data.get('security_requirements', []),
                error_handling=int_data.get('error_handling', {})
            )
            integrations.append(integration)
        
        return integrations


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    import asyncio
    
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        input_data = body.get('input_data', {})
        use_agno = body.get('use_agno', True)
        deep_parsing = body.get('deep_parsing', True)
        
        # Agent 실행
        agent = ParserAgent()
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        parsed_project = loop.run_until_complete(
            agent.parse_project(input_data, use_agno, deep_parsing)
        )
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(parsed_project.to_dict(), ensure_ascii=False)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Error parsing project requirements'
                }
            }, ensure_ascii=False)
        }