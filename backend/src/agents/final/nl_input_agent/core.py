"""
NL Input Agent Core Implementation
Phase 4 Task 4.1: 핵심 에이전트 구현
"""

import json
import logging
import os
import time
import asyncio
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

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


class ProjectType(Enum):
    """지원하는 프로젝트 타입"""
    WEB_APP = "web-application"
    MOBILE_APP = "mobile-application"
    BACKEND_API = "backend-api"
    CLI_TOOL = "cli-tool"
    DESKTOP_APP = "desktop-application"
    MICROSERVICE = "microservice"
    ML_PROJECT = "ml-project"
    BLOCKCHAIN = "blockchain"
    IOT = "iot-application"
    GAME = "game-development"
    UNKNOWN = "unknown"


@dataclass
class ExtractedEntities:
    """추출된 엔티티 정보"""
    pages: List[str]
    components: List[str]
    actions: List[str]
    data_models: List[str]
    apis: List[str]
    features: List[str]


@dataclass
class TechnologyPreferences:
    """기술 스택 선호사항"""
    framework: Optional[str] = None
    database: Optional[str] = None
    styling: Optional[str] = None
    authentication: Optional[str] = None
    deployment: Optional[str] = None
    testing: Optional[str] = None


@dataclass
class ProjectRequirements:
    """구조화된 프로젝트 요구사항"""
    description: str
    project_type: str
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    technology_preferences: TechnologyPreferences
    constraints: List[str]
    extracted_entities: ExtractedEntities
    confidence_score: float
    estimated_complexity: str
    metadata: Dict[str, Any]
    clarification_needed: bool = False
    clarification_questions: List[str] = None
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return asdict(self)


class RequirementExtractor(Tool):
    """요구사항 추출 도구 (Agno Tool)"""
    
    def __init__(self):
        super().__init__(
            name="requirement_extractor",
            description="Extract structured requirements from natural language"
        )
    
    async def run(self, text: str) -> Dict[str, Any]:
        """요구사항 추출 실행"""
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
        requirements = []
        keywords = {
            '로그인': '사용자 인증 및 로그인 기능',
            '회원가입': '사용자 등록 기능',
            '검색': '검색 및 필터링 기능',
            '결제': '결제 처리 기능',
            '알림': '알림 및 푸시 메시지 기능',
            '채팅': '실시간 채팅 기능',
            'crud': 'CRUD 작업 (생성, 조회, 수정, 삭제)'
        }
        
        text_lower = text.lower()
        for keyword, requirement in keywords.items():
            if keyword in text_lower:
                requirements.append(requirement)
        
        return requirements
    
    def _extract_non_functional_requirements(self, text: str) -> List[str]:
        """비기능 요구사항 추출"""
        requirements = []
        
        if any(word in text.lower() for word in ['빠른', '성능', 'performance']):
            requirements.append('높은 성능 및 빠른 응답 속도')
        
        if any(word in text.lower() for word in ['보안', 'secure', 'security']):
            requirements.append('강화된 보안 및 데이터 암호화')
        
        if any(word in text.lower() for word in ['확장', 'scalable']):
            requirements.append('확장 가능한 아키텍처')
        
        return requirements
    
    def _extract_technology_stack(self, text: str) -> Dict[str, str]:
        """기술 스택 추출"""
        stack = {}
        text_lower = text.lower()
        
        # 프레임워크
        frameworks = {
            'react': 'React', 'vue': 'Vue.js', 'angular': 'Angular',
            'nextjs': 'Next.js', 'django': 'Django', 'fastapi': 'FastAPI'
        }
        for key, value in frameworks.items():
            if key in text_lower:
                stack['framework'] = value
                break
        
        # 데이터베이스
        databases = {
            'postgresql': 'PostgreSQL', 'mysql': 'MySQL',
            'mongodb': 'MongoDB', 'redis': 'Redis'
        }
        for key, value in databases.items():
            if key in text_lower:
                stack['database'] = value
                break
        
        return stack


class NLInputAgent:
    """Production-ready NL Input Agent with Agno Framework"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # Agno Agent 초기화 (사용 가능한 경우)
        if AGNO_AVAILABLE:
            self._init_agno_agent()
        else:
            logger.warning("Agno Framework not available, using fallback mode")
            self.agent = None
        
        # 컴포넌트 초기화
        self._init_components()
        
        # 패턴 초기화
        self._init_patterns()
        
        # 메트릭 초기화
        self.processing_times = []
        
        logger.info(f"NL Input Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/nl-input-agent/',
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
                'max_input_length': 5000,
                'min_confidence_score': 0.3,
                'timeout_seconds': 30,
                'use_agno': True,
                'use_bedrock': True
            }
    
    def _init_agno_agent(self):
        """Agno 에이전트 초기화"""
        try:
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
                    table_name=f"t-dev-nl-conversations-{self.environment}"
                ),
                tools=[
                    RequirementExtractor()
                ],
                temperature=0.3,
                max_retries=3
            )
            logger.info("Agno agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno agent: {e}")
            self.agent = None
    
    def _init_components(self):
        """컴포넌트 초기화"""
        # 지연 import로 순환 참조 방지
        from .context import ContextEnhancer
        from .clarification import ClarificationSystem
        from .intent_analyzer import IntentAnalyzer
        from .priority_analyzer import PriorityAnalyzer
        
        self.context_enhancer = ContextEnhancer()
        self.clarification_system = ClarificationSystem()
        self.intent_analyzer = IntentAnalyzer()
        self.priority_analyzer = PriorityAnalyzer()
    
    def _init_patterns(self):
        """정규표현식 패턴 초기화"""
        import re
        
        # 프로젝트 타입 패턴
        self.project_patterns = {
            ProjectType.WEB_APP: r'(웹|web|사이트|website|홈페이지|프론트엔드)',
            ProjectType.MOBILE_APP: r'(모바일|mobile|앱|app|ios|android|react native|flutter)',
            ProjectType.BACKEND_API: r'(백엔드|backend|api|서버|server|rest|graphql)',
            ProjectType.CLI_TOOL: r'(cli|command line|터미널|terminal|콘솔|console)',
            ProjectType.DESKTOP_APP: r'(데스크톱|desktop|electron|윈도우|windows|맥|mac)',
            ProjectType.MICROSERVICE: r'(마이크로서비스|microservice|msa|분산|distributed)',
            ProjectType.ML_PROJECT: r'(머신러닝|machine learning|ml|ai|인공지능|딥러닝)',
            ProjectType.BLOCKCHAIN: r'(블록체인|blockchain|스마트컨트랙트|smart contract|web3)',
            ProjectType.IOT: r'(iot|사물인터넷|센서|sensor|임베디드|embedded)',
            ProjectType.GAME: r'(게임|game|unity|unreal|godot)'
        }
        
        # 기능 추출 패턴
        self.feature_patterns = {
            'authentication': r'(로그인|login|인증|authentication|회원가입|signup)',
            'database': r'(데이터베이스|database|db|저장|storage|mysql|postgresql|mongodb)',
            'payment': r'(결제|payment|구매|purchase|장바구니|cart)',
            'realtime': r'(실시간|realtime|real-time|웹소켓|websocket|채팅|chat)',
            'crud': r'(생성|create|조회|read|수정|update|삭제|delete|crud)',
            'search': r'(검색|search|필터|filter|정렬|sort)',
            'notification': r'(알림|notification|이메일|email|sms|푸시|push)',
            'admin': r'(관리자|admin|대시보드|dashboard|통계|analytics)'
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    async def process_description(
        self,
        description: str,
        context: Optional[Dict] = None,
        use_agno: bool = True
    ) -> ProjectRequirements:
        """
        자연어 프로젝트 설명 처리
        
        Args:
            description: 사용자의 자연어 입력
            context: 추가 컨텍스트
            use_agno: Agno Framework 사용 여부
            
        Returns:
            ProjectRequirements: 구조화된 요구사항
        """
        start_time = time.time()
        
        try:
            # 1. 입력 검증
            self._validate_input(description)
            
            # 2. 컨텍스트 향상
            enhanced_input = await self.context_enhancer.enhance(description, context)
            
            # 3. Agno Agent 또는 Fallback 처리
            if use_agno and self.agent:
                requirements = await self._process_with_agno(enhanced_input, context)
            else:
                requirements = await self._process_with_fallback(enhanced_input, context)
            
            # 4. 의도 분석
            intent_analysis = await self.intent_analyzer.analyze(description)
            requirements.metadata['intent'] = intent_analysis
            
            # 5. 우선순위 분석
            priorities = await self.priority_analyzer.analyze(requirements)
            requirements.metadata['priorities'] = priorities
            
            # 6. 명확화 필요 여부 확인
            if requirements.confidence_score < float(self.config.get('min_confidence_score', 0.3)):
                clarifications = await self.clarification_system.generate_questions(
                    requirements,
                    enhanced_input
                )
                requirements.clarification_needed = True
                requirements.clarification_questions = clarifications
            
            # 7. 처리 시간 기록
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            metrics.add_metric(
                name="ProcessingTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            
            logger.info(
                f"Successfully processed input",
                extra={
                    "project_type": requirements.project_type,
                    "confidence": requirements.confidence_score,
                    "processing_time": processing_time
                }
            )
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            metrics.add_metric(name="ProcessingError", unit=MetricUnit.Count, value=1)
            raise
    
    async def _process_with_agno(
        self,
        enhanced_input: str,
        context: Optional[Dict]
    ) -> ProjectRequirements:
        """Agno Agent를 사용한 처리"""
        
        # Agno Agent 프롬프트 구성
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
        
        JSON 형식으로 응답하세요.
        """
        
        # Agno Agent 실행
        result = await self.agent.arun(analysis_prompt)
        
        # 결과 파싱
        return self._parse_agno_result(result, enhanced_input)
    
    async def _process_with_fallback(
        self,
        enhanced_input: str,
        context: Optional[Dict]
    ) -> ProjectRequirements:
        """Fallback 처리 (Agno 없이)"""
        
        # 프로젝트 타입 감지
        project_type = self._detect_project_type(enhanced_input)
        
        # 요구사항 추출
        functional_reqs = self._extract_functional_requirements(enhanced_input)
        non_functional_reqs = self._extract_non_functional_requirements(enhanced_input)
        
        # 기술 선호사항 추출
        tech_prefs = self._extract_technology_preferences(enhanced_input)
        
        # 엔티티 추출
        entities = self._extract_entities(enhanced_input)
        
        # 제약사항 추출
        constraints = self._extract_constraints(enhanced_input)
        
        # 복잡도 평가
        complexity = self._evaluate_complexity(functional_reqs, entities, tech_prefs)
        
        # 신뢰도 점수 계산
        confidence = self._calculate_confidence_score(project_type, functional_reqs, entities)
        
        # 메타데이터 생성
        metadata = self._generate_metadata(enhanced_input)
        
        return ProjectRequirements(
            description=enhanced_input,
            project_type=project_type.value,
            functional_requirements=functional_reqs,
            non_functional_requirements=non_functional_reqs,
            technology_preferences=tech_prefs,
            constraints=constraints,
            extracted_entities=entities,
            confidence_score=confidence,
            estimated_complexity=complexity,
            metadata=metadata
        )
    
    def _validate_input(self, query: str):
        """입력 검증"""
        if not query or not query.strip():
            raise ValueError("입력이 비어있습니다")
        
        max_length = int(self.config.get('max_input_length', 5000))
        if len(query) > max_length:
            raise ValueError(f"입력이 너무 깁니다 (최대 {max_length}자)")
        
        # SQL Injection, XSS 방지
        import re
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'INSERT\s+INTO'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError("잠재적으로 위험한 입력이 감지되었습니다")
    
    def _detect_project_type(self, query: str) -> ProjectType:
        """프로젝트 타입 감지"""
        import re
        query_lower = query.lower()
        scores = {}
        
        for project_type, pattern in self.project_patterns.items():
            matches = re.findall(pattern, query_lower)
            scores[project_type] = len(matches)
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return ProjectType.UNKNOWN
    
    def _extract_functional_requirements(self, query: str) -> List[str]:
        """기능 요구사항 추출"""
        requirements = []
        
        feature_keywords = {
            '로그인': '사용자 인증 및 로그인 기능',
            '회원가입': '사용자 등록 기능',
            '검색': '검색 및 필터링 기능',
            '결제': '결제 처리 기능',
            '알림': '알림 및 푸시 메시지 기능',
            '채팅': '실시간 채팅 기능',
            '업로드': '파일 업로드 기능',
            '다운로드': '파일 다운로드 기능',
            'crud': 'CRUD 작업 (생성, 조회, 수정, 삭제)'
        }
        
        query_lower = query.lower()
        for keyword, requirement in feature_keywords.items():
            if keyword in query_lower:
                requirements.append(requirement)
        
        return requirements[:10]  # 최대 10개
    
    def _extract_non_functional_requirements(self, query: str) -> List[str]:
        """비기능 요구사항 추출"""
        requirements = []
        
        if any(word in query.lower() for word in ['빠른', '빠르게', '성능', '속도']):
            requirements.append('높은 성능 및 빠른 응답 속도')
        
        if any(word in query.lower() for word in ['보안', '안전', '암호화', 'ssl']):
            requirements.append('강화된 보안 및 데이터 암호화')
        
        if any(word in query.lower() for word in ['확장', '스케일', '대용량', '많은 사용자']):
            requirements.append('확장 가능한 아키텍처')
        
        if any(word in query.lower() for word in ['24시간', '무중단', '고가용성']):
            requirements.append('24/7 고가용성')
        
        if any(word in query.lower() for word in ['쉬운', '간단한', '직관적', 'ui', 'ux']):
            requirements.append('직관적인 사용자 인터페이스')
        
        if any(word in query.lower() for word in ['모바일', '반응형', 'responsive']):
            requirements.append('반응형 디자인 (모바일/데스크톱)')
        
        return requirements
    
    def _extract_technology_preferences(self, query: str) -> TechnologyPreferences:
        """기술 스택 선호사항 추출"""
        tech_prefs = TechnologyPreferences()
        query_lower = query.lower()
        
        # 프레임워크
        frameworks = {
            'react': ['react', '리액트'],
            'vue': ['vue', '뷰'],
            'angular': ['angular', '앵귤러'],
            'nextjs': ['next', '넥스트'],
            'django': ['django', '장고'],
            'fastapi': ['fastapi'],
            'spring': ['spring', '스프링'],
            'express': ['express'],
            'flask': ['flask', '플라스크']
        }
        
        for fw, keywords in frameworks.items():
            if any(kw in query_lower for kw in keywords):
                tech_prefs.framework = fw
                break
        
        # 데이터베이스
        databases = {
            'postgresql': ['postgresql', 'postgres', '포스트그레'],
            'mysql': ['mysql'],
            'mongodb': ['mongodb', '몽고'],
            'redis': ['redis', '레디스'],
            'dynamodb': ['dynamodb', '다이나모']
        }
        
        for db, keywords in databases.items():
            if any(kw in query_lower for kw in keywords):
                tech_prefs.database = db
                break
        
        # 스타일링
        styling = {
            'tailwind': ['tailwind', '테일윈드'],
            'bootstrap': ['bootstrap', '부트스트랩'],
            'material-ui': ['material', '머티리얼'],
            'chakra': ['chakra', '차크라']
        }
        
        for style, keywords in styling.items():
            if any(kw in query_lower for kw in keywords):
                tech_prefs.styling = style
                break
        
        return tech_prefs
    
    def _extract_entities(self, query: str) -> ExtractedEntities:
        """엔티티 추출"""
        import re
        query_lower = query.lower()
        
        # 페이지 추출
        pages = []
        page_keywords = ['홈', '로그인', '회원가입', '프로필', '설정', '대시보드']
        for keyword in page_keywords:
            if keyword in query_lower:
                pages.append(f"{keyword} 페이지")
        
        # 컴포넌트 추출
        components = []
        component_keywords = ['헤더', '푸터', '네비게이션', '사이드바', '모달']
        for keyword in component_keywords:
            if keyword in query_lower:
                components.append(f"{keyword} 컴포넌트")
        
        # 액션 추출
        actions = []
        action_keywords = ['생성', '조회', '수정', '삭제', '검색', '필터링']
        for keyword in action_keywords:
            if keyword in query_lower:
                actions.append(f"{keyword} 기능")
        
        # 데이터 모델 추출
        data_models = []
        model_keywords = ['사용자', '유저', '상품', '제품', '주문', '결제']
        for keyword in model_keywords:
            if keyword in query_lower:
                data_models.append(f"{keyword} 모델")
        
        # API 추출
        apis = []
        if 'api' in query_lower or 'rest' in query_lower:
            apis.extend(['GET', 'POST', 'PUT', 'DELETE'])
        
        # 기능 추출
        features = []
        for feature, pattern in self.feature_patterns.items():
            if re.search(pattern, query_lower):
                features.append(feature)
        
        return ExtractedEntities(
            pages=pages,
            components=components,
            actions=actions,
            data_models=data_models,
            apis=apis,
            features=features
        )
    
    def _extract_constraints(self, query: str) -> List[str]:
        """제약사항 추출"""
        import re
        constraints = []
        query_lower = query.lower()
        
        # 시간 제약
        time_patterns = [
            (r'(\d+)일 안에', '{}일 내 완료'),
            (r'(\d+)주 안에', '{}주 내 완료'),
            (r'(\d+)개월 안에', '{}개월 내 완료')
        ]
        
        for pattern, template in time_patterns:
            match = re.search(pattern, query_lower)
            if match:
                constraints.append(template.format(match.group(1)))
        
        # 예산 제약
        if '예산' in query_lower or '비용' in query_lower:
            constraints.append('예산 제약 고려 필요')
        
        # 기술 제약
        if 'legacy' in query_lower or '레거시' in query_lower:
            constraints.append('레거시 시스템과의 통합 필요')
        
        # 규정 준수
        if any(word in query_lower for word in ['gdpr', '개인정보', 'privacy']):
            constraints.append('개인정보보호 규정 준수')
        
        return constraints
    
    def _evaluate_complexity(
        self,
        functional_reqs: List[str],
        entities: ExtractedEntities,
        tech_prefs: TechnologyPreferences
    ) -> str:
        """프로젝트 복잡도 평가"""
        score = 0
        
        # 기능 요구사항 수
        score += len(functional_reqs) * 2
        
        # 엔티티 복잡도
        score += len(entities.pages)
        score += len(entities.components)
        score += len(entities.data_models) * 2
        score += len(entities.features) * 3
        
        # 기술 스택 복잡도
        if tech_prefs.database:
            score += 3
        if tech_prefs.authentication:
            score += 2
        if tech_prefs.deployment:
            score += 2
        
        # 복잡도 레벨 결정
        if score < 10:
            return "low"
        elif score < 25:
            return "medium"
        elif score < 40:
            return "high"
        else:
            return "very-high"
    
    def _calculate_confidence_score(
        self,
        project_type: ProjectType,
        functional_reqs: List[str],
        entities: ExtractedEntities
    ) -> float:
        """신뢰도 점수 계산"""
        score = 0.0
        
        # 프로젝트 타입이 명확한 경우
        if project_type != ProjectType.UNKNOWN:
            score += 0.3
        
        # 기능 요구사항이 있는 경우
        if functional_reqs:
            score += min(len(functional_reqs) * 0.05, 0.3)
        
        # 엔티티가 추출된 경우
        total_entities = (
            len(entities.pages) +
            len(entities.components) +
            len(entities.data_models) +
            len(entities.features)
        )
        if total_entities > 0:
            score += min(total_entities * 0.02, 0.4)
        
        return min(score, 1.0)
    
    def _generate_metadata(self, query: str) -> Dict[str, Any]:
        """메타데이터 생성"""
        return {
            'agent_name': 'nl-input-agent',
            'version': '1.0.0',
            'environment': self.environment,
            'input_length': len(query),
            'word_count': len(query.split()),
            'language': 'ko' if any(ord(c) > 127 for c in query) else 'en',
            'timestamp': time.time(),
            'agno_used': self.agent is not None
        }
    
    def _parse_agno_result(self, result: str, original_input: str) -> ProjectRequirements:
        """Agno 결과 파싱"""
        try:
            # JSON 파싱 시도
            if isinstance(result, str):
                import json
                data = json.loads(result)
            else:
                data = result
            
            # 데이터 매핑
            project_type = data.get('project_type', 'unknown')
            functional_reqs = data.get('functional_requirements', [])
            non_functional_reqs = data.get('non_functional_requirements', [])
            
            # 기술 선호사항
            tech_prefs = TechnologyPreferences()
            if 'technology_stack' in data:
                tech_prefs.framework = data['technology_stack'].get('framework')
                tech_prefs.database = data['technology_stack'].get('database')
            
            # 엔티티
            entities = ExtractedEntities(
                pages=data.get('pages', []),
                components=data.get('components', []),
                actions=data.get('actions', []),
                data_models=data.get('data_models', []),
                apis=data.get('apis', []),
                features=data.get('features', [])
            )
            
            # 제약사항
            constraints = data.get('constraints', [])
            
            # 복잡도와 신뢰도
            complexity = data.get('complexity', 'medium')
            confidence = data.get('confidence', 0.7)
            
            return ProjectRequirements(
                description=original_input,
                project_type=project_type,
                functional_requirements=functional_reqs,
                non_functional_requirements=non_functional_reqs,
                technology_preferences=tech_prefs,
                constraints=constraints,
                extracted_entities=entities,
                confidence_score=confidence,
                estimated_complexity=complexity,
                metadata={'agno_result': data}
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Agno result: {e}")
            # Fallback 처리
            return self._process_with_fallback(original_input, None)


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
        query = body.get('query', '')
        framework = body.get('framework')
        context_data = body.get('context')
        
        # Agent 실행
        agent = NLInputAgent()
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        requirements = loop.run_until_complete(
            agent.process_description(query, context_data)
        )
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(requirements.to_dict(), ensure_ascii=False)
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
                    'message': '처리 중 오류가 발생했습니다'
                }
            }, ensure_ascii=False)
        }