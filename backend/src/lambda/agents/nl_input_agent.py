"""
NL Input Agent - Production Ready Implementation
자연어 입력을 분석하여 구조화된 프로젝트 요구사항으로 변환

AWS Lambda에서 실행 (실행시간 < 30초)
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import re

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from botocore.exceptions import ClientError

# Production 로깅 설정
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# AWS 클라이언트
ssm = boto3.client('ssm')
secrets = boto3.client('secretsmanager')


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


class NLInputAgent:
    """Production-ready NL Input Agent"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # 패턴 매칭 규칙 초기화
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
            # 기본 설정 반환
            return {
                'max_input_length': 5000,
                'min_confidence_score': 0.3,
                'timeout_seconds': 30
            }
    
    def _init_patterns(self):
        """정규표현식 패턴 초기화"""
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
    def process_input(self, query: str, framework: Optional[str] = None) -> ProjectRequirements:
        """
        자연어 입력을 구조화된 요구사항으로 변환
        
        Args:
            query: 사용자의 자연어 입력
            framework: 선호 프레임워크 (선택사항)
            
        Returns:
            ProjectRequirements: 구조화된 요구사항
            
        Raises:
            ValueError: 입력 검증 실패
            TimeoutError: 처리 시간 초과
        """
        start_time = time.time()
        
        try:
            # 입력 검증
            self._validate_input(query)
            
            # 프로젝트 타입 감지
            project_type = self._detect_project_type(query)
            metrics.add_metric(name="ProjectTypeDetected", unit=MetricUnit.Count, value=1)
            
            # 요구사항 추출
            functional_reqs = self._extract_functional_requirements(query)
            non_functional_reqs = self._extract_non_functional_requirements(query)
            
            # 기술 선호사항 추출
            tech_prefs = self._extract_technology_preferences(query, framework)
            
            # 엔티티 추출
            entities = self._extract_entities(query)
            
            # 제약사항 추출
            constraints = self._extract_constraints(query)
            
            # 복잡도 평가
            complexity = self._evaluate_complexity(
                functional_reqs, 
                entities, 
                tech_prefs
            )
            
            # 신뢰도 점수 계산
            confidence = self._calculate_confidence_score(
                project_type,
                functional_reqs,
                entities
            )
            
            # 메타데이터 생성
            metadata = self._generate_metadata(query, start_time)
            
            # 결과 구성
            requirements = ProjectRequirements(
                description=query,
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
            
            # 처리 시간 기록
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
                    "project_type": project_type.value,
                    "confidence": confidence,
                    "processing_time": processing_time
                }
            )
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            metrics.add_metric(name="ProcessingError", unit=MetricUnit.Count, value=1)
            raise
    
    def _validate_input(self, query: str):
        """입력 검증"""
        if not query or not query.strip():
            raise ValueError("입력이 비어있습니다")
        
        max_length = int(self.config.get('max_input_length', 5000))
        if len(query) > max_length:
            raise ValueError(f"입력이 너무 깁니다 (최대 {max_length}자)")
        
        # SQL Injection, XSS 방지
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
        query_lower = query.lower()
        scores = {}
        
        for project_type, pattern in self.project_patterns.items():
            matches = re.findall(pattern, query_lower)
            scores[project_type] = len(matches)
        
        # 가장 높은 점수의 타입 선택
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return ProjectType.UNKNOWN
    
    def _extract_functional_requirements(self, query: str) -> List[str]:
        """기능 요구사항 추출"""
        requirements = []
        
        # 키워드 기반 추출
        feature_keywords = {
            '로그인': '사용자 인증 및 로그인 기능',
            '회원가입': '사용자 등록 기능',
            '검색': '검색 및 필터링 기능',
            '결제': '결제 처리 기능',
            '알림': '알림 및 푸시 메시지 기능',
            '채팅': '실시간 채팅 기능',
            '업로드': '파일 업로드 기능',
            '다운로드': '파일 다운로드 기능',
            '공유': '콘텐츠 공유 기능',
            '댓글': '댓글 작성 및 관리 기능',
            '좋아요': '좋아요/북마크 기능',
            '프로필': '사용자 프로필 관리',
            '설정': '애플리케이션 설정 관리',
            '대시보드': '관리자 대시보드',
            '통계': '데이터 분석 및 통계',
            'api': 'RESTful API 제공',
            'crud': 'CRUD 작업 (생성, 조회, 수정, 삭제)'
        }
        
        query_lower = query.lower()
        for keyword, requirement in feature_keywords.items():
            if keyword in query_lower:
                requirements.append(requirement)
        
        # 문장 분석으로 추가 요구사항 추출
        sentences = re.split(r'[.!?]', query)
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['필요', '포함', '구현', '만들']):
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    requirements.append(sentence)
        
        return requirements[:10]  # 최대 10개
    
    def _extract_non_functional_requirements(self, query: str) -> List[str]:
        """비기능 요구사항 추출"""
        requirements = []
        
        # 성능 관련
        if any(word in query.lower() for word in ['빠른', '빠르게', '성능', '속도']):
            requirements.append('높은 성능 및 빠른 응답 속도')
        
        # 보안 관련
        if any(word in query.lower() for word in ['보안', '안전', '암호화', 'ssl']):
            requirements.append('강화된 보안 및 데이터 암호화')
        
        # 확장성 관련
        if any(word in query.lower() for word in ['확장', '스케일', '대용량', '많은 사용자']):
            requirements.append('확장 가능한 아키텍처')
        
        # 가용성 관련
        if any(word in query.lower() for word in ['24시간', '무중단', '고가용성']):
            requirements.append('24/7 고가용성')
        
        # 사용성 관련
        if any(word in query.lower() for word in ['쉬운', '간단한', '직관적', 'ui', 'ux']):
            requirements.append('직관적인 사용자 인터페이스')
        
        # 호환성 관련
        if any(word in query.lower() for word in ['모바일', '반응형', 'responsive']):
            requirements.append('반응형 디자인 (모바일/데스크톱)')
        
        return requirements
    
    def _extract_technology_preferences(
        self, 
        query: str, 
        framework: Optional[str]
    ) -> TechnologyPreferences:
        """기술 스택 선호사항 추출"""
        tech_prefs = TechnologyPreferences()
        query_lower = query.lower()
        
        # 프레임워크
        if framework:
            tech_prefs.framework = framework
        else:
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
            'dynamodb': ['dynamodb', '다이나모'],
            'firebase': ['firebase', '파이어베이스']
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
            'chakra': ['chakra', '차크라'],
            'styled-components': ['styled-components'],
            'sass': ['sass', 'scss']
        }
        
        for style, keywords in styling.items():
            if any(kw in query_lower for kw in keywords):
                tech_prefs.styling = style
                break
        
        # 인증
        if any(word in query_lower for word in ['oauth', 'jwt', '소셜로그인', 'social']):
            tech_prefs.authentication = 'oauth2/jwt'
        elif any(word in query_lower for word in ['세션', 'session']):
            tech_prefs.authentication = 'session-based'
        
        # 배포
        if any(word in query_lower for word in ['aws', '아마존']):
            tech_prefs.deployment = 'aws'
        elif any(word in query_lower for word in ['docker', '도커', '컨테이너']):
            tech_prefs.deployment = 'docker'
        elif any(word in query_lower for word in ['vercel']):
            tech_prefs.deployment = 'vercel'
        
        return tech_prefs
    
    def _extract_entities(self, query: str) -> ExtractedEntities:
        """엔티티 추출"""
        query_lower = query.lower()
        
        # 페이지 추출
        pages = []
        page_keywords = ['홈', '로그인', '회원가입', '프로필', '설정', '대시보드', 
                        '상품', '장바구니', '결제', '주문', '게시판', '상세']
        for keyword in page_keywords:
            if keyword in query_lower:
                pages.append(f"{keyword} 페이지")
        
        # 컴포넌트 추출
        components = []
        component_keywords = ['헤더', '푸터', '네비게이션', '사이드바', '모달', 
                             '테이블', '폼', '버튼', '카드', '리스트', '차트']
        for keyword in component_keywords:
            if keyword in query_lower:
                components.append(f"{keyword} 컴포넌트")
        
        # 액션 추출
        actions = []
        action_keywords = ['생성', '조회', '수정', '삭제', '검색', '필터링', 
                          '정렬', '업로드', '다운로드', '공유', '좋아요']
        for keyword in action_keywords:
            if keyword in query_lower:
                actions.append(f"{keyword} 기능")
        
        # 데이터 모델 추출
        data_models = []
        model_keywords = ['사용자', '유저', '상품', '제품', '주문', '결제', 
                         '게시글', '댓글', '카테고리', '태그']
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
    
    def _generate_metadata(self, query: str, start_time: float) -> Dict[str, Any]:
        """메타데이터 생성"""
        return {
            'agent_name': 'nl-input-agent',
            'version': '1.0.0',
            'environment': self.environment,
            'processing_time': time.time() - start_time,
            'input_length': len(query),
            'word_count': len(query.split()),
            'language': 'ko' if any(ord(c) > 127 for c in query) else 'en',
            'timestamp': time.time()
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        framework = body.get('framework')
        
        # Agent 실행
        agent = NLInputAgent()
        requirements = agent.process_input(query, framework)
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(asdict(requirements), ensure_ascii=False)
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


if __name__ == "__main__":
    # 로컬 테스트
    test_agent = NLInputAgent('development')
    
    test_queries = [
        "React로 Todo 앱을 만들어줘. 로그인 기능과 실시간 동기화가 필요해",
        "QR코드 기반 근태관리 시스템을 만들어줘",
        "블로그 웹사이트를 만들어줘. 글 작성, 수정, 삭제가 가능하고 댓글 기능도 필요해"
    ]
    
    for query in test_queries:
        print(f"\n테스트 쿼리: {query}")
        result = test_agent.process_input(query)
        print(f"프로젝트 타입: {result.project_type}")
        print(f"신뢰도: {result.confidence_score:.2f}")
        print(f"복잡도: {result.estimated_complexity}")
        print(f"기능 요구사항: {result.functional_requirements[:3]}")