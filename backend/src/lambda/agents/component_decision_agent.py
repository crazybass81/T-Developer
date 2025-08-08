"""
Component Decision Agent - Production Ready Implementation
컴포넌트 상세 설계 및 인터페이스 정의

EC2/ECS에서 실행 (실행시간 > 1분, 복잡한 분석)
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import hashlib

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
bedrock = boto3.client('bedrock-runtime')


class ComponentType(Enum):
    """컴포넌트 타입"""
    PAGE = "page"
    LAYOUT = "layout"
    CONTAINER = "container"
    PRESENTATIONAL = "presentational"
    FORM = "form"
    DATA_DISPLAY = "data_display"
    NAVIGATION = "navigation"
    FEEDBACK = "feedback"
    UTILITY = "utility"
    SERVICE = "service"
    HOOK = "hook"
    CONTEXT = "context"
    STORE = "store"
    MIDDLEWARE = "middleware"
    GUARD = "guard"


class ComponentComplexity(Enum):
    """컴포넌트 복잡도"""
    SIMPLE = "simple"      # < 50 lines
    MEDIUM = "medium"      # 50-200 lines
    COMPLEX = "complex"    # 200-500 lines
    VERY_COMPLEX = "very_complex"  # > 500 lines


@dataclass
class ComponentProperty:
    """컴포넌트 속성"""
    name: str
    type: str
    required: bool
    default_value: Optional[Any]
    description: str
    validation: Optional[str] = None


@dataclass
class ComponentMethod:
    """컴포넌트 메서드"""
    name: str
    parameters: List[Dict[str, str]]
    return_type: str
    description: str
    is_async: bool = False
    is_private: bool = False


@dataclass
class ComponentState:
    """컴포넌트 상태"""
    name: str
    type: str
    initial_value: Any
    description: str
    is_local: bool = True


@dataclass
class ComponentInterface:
    """컴포넌트 인터페이스"""
    props: List[ComponentProperty]
    methods: List[ComponentMethod]
    states: List[ComponentState]
    events: List[str]
    dependencies: List[str]
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'props': [asdict(p) for p in self.props],
            'methods': [asdict(m) for m in self.methods],
            'states': [asdict(s) for s in self.states],
            'events': self.events,
            'dependencies': self.dependencies
        }


@dataclass
class ComponentSpecification:
    """컴포넌트 상세 명세"""
    name: str
    type: ComponentType
    complexity: ComponentComplexity
    description: str
    file_path: str
    interface: ComponentInterface
    styling: Dict[str, Any]
    accessibility: Dict[str, Any]
    performance: Dict[str, Any]
    testing: Dict[str, Any]
    documentation: str
    estimated_lines: int
    reusability_score: float
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'name': self.name,
            'type': self.type.value,
            'complexity': self.complexity.value,
            'description': self.description,
            'file_path': self.file_path,
            'interface': self.interface.to_dict(),
            'styling': self.styling,
            'accessibility': self.accessibility,
            'performance': self.performance,
            'testing': self.testing,
            'documentation': self.documentation,
            'estimated_lines': self.estimated_lines,
            'reusability_score': self.reusability_score
        }


@dataclass
class ComponentDecisionResult:
    """Component Decision 결과"""
    components: List[ComponentSpecification]
    component_tree: Dict[str, Any]
    interaction_matrix: Dict[str, List[str]]
    data_flow: Dict[str, Dict[str, Any]]
    state_management: Dict[str, Any]
    routing_config: Dict[str, Any]
    api_contracts: List[Dict[str, Any]]
    design_patterns: List[str]
    total_components: int
    estimated_total_lines: int
    reusability_analysis: Dict[str, Any]
    metadata: Dict[str, Any]


class ComponentDecisionAgent:
    """Production-ready Component Decision Agent"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # 컴포넌트 템플릿 초기화
        self._init_component_templates()
        
        # 디자인 패턴 초기화
        self._init_design_patterns()
        
        # 메트릭 초기화
        self.decision_times = []
        
        logger.info(f"Component Decision Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/component-decision-agent/',
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
                'max_components': 500,
                'min_reusability_score': 0.6,
                'use_ai_analysis': True,
                'timeout_seconds': 120
            }
    
    def _init_component_templates(self):
        """컴포넌트 템플릿 초기화"""
        
        # React 컴포넌트 템플릿
        self.react_templates = {
            'Button': {
                'type': ComponentType.PRESENTATIONAL,
                'props': [
                    {'name': 'onClick', 'type': 'function', 'required': False},
                    {'name': 'children', 'type': 'ReactNode', 'required': True},
                    {'name': 'variant', 'type': 'string', 'required': False, 'default': 'primary'},
                    {'name': 'disabled', 'type': 'boolean', 'required': False, 'default': False},
                    {'name': 'size', 'type': 'string', 'required': False, 'default': 'medium'}
                ],
                'complexity': ComponentComplexity.SIMPLE
            },
            'Form': {
                'type': ComponentType.FORM,
                'props': [
                    {'name': 'onSubmit', 'type': 'function', 'required': True},
                    {'name': 'initialValues', 'type': 'object', 'required': False},
                    {'name': 'validation', 'type': 'object', 'required': False}
                ],
                'states': [
                    {'name': 'values', 'type': 'object'},
                    {'name': 'errors', 'type': 'object'},
                    {'name': 'touched', 'type': 'object'},
                    {'name': 'isSubmitting', 'type': 'boolean'}
                ],
                'complexity': ComponentComplexity.COMPLEX
            },
            'DataTable': {
                'type': ComponentType.DATA_DISPLAY,
                'props': [
                    {'name': 'data', 'type': 'array', 'required': True},
                    {'name': 'columns', 'type': 'array', 'required': True},
                    {'name': 'onSort', 'type': 'function', 'required': False},
                    {'name': 'onFilter', 'type': 'function', 'required': False},
                    {'name': 'pagination', 'type': 'object', 'required': False}
                ],
                'complexity': ComponentComplexity.COMPLEX
            },
            'Modal': {
                'type': ComponentType.FEEDBACK,
                'props': [
                    {'name': 'isOpen', 'type': 'boolean', 'required': True},
                    {'name': 'onClose', 'type': 'function', 'required': True},
                    {'name': 'title', 'type': 'string', 'required': False},
                    {'name': 'children', 'type': 'ReactNode', 'required': True}
                ],
                'complexity': ComponentComplexity.MEDIUM
            },
            'Layout': {
                'type': ComponentType.LAYOUT,
                'props': [
                    {'name': 'children', 'type': 'ReactNode', 'required': True},
                    {'name': 'sidebar', 'type': 'boolean', 'required': False},
                    {'name': 'header', 'type': 'boolean', 'required': False},
                    {'name': 'footer', 'type': 'boolean', 'required': False}
                ],
                'complexity': ComponentComplexity.MEDIUM
            }
        }
        
        # 서비스/유틸리티 템플릿
        self.service_templates = {
            'AuthService': {
                'methods': [
                    {'name': 'login', 'params': ['credentials'], 'async': True},
                    {'name': 'logout', 'params': [], 'async': True},
                    {'name': 'getCurrentUser', 'params': [], 'async': False},
                    {'name': 'refreshToken', 'params': [], 'async': True}
                ]
            },
            'ApiService': {
                'methods': [
                    {'name': 'get', 'params': ['url', 'config'], 'async': True},
                    {'name': 'post', 'params': ['url', 'data', 'config'], 'async': True},
                    {'name': 'put', 'params': ['url', 'data', 'config'], 'async': True},
                    {'name': 'delete', 'params': ['url', 'config'], 'async': True}
                ]
            },
            'ValidationService': {
                'methods': [
                    {'name': 'validateEmail', 'params': ['email'], 'async': False},
                    {'name': 'validatePassword', 'params': ['password'], 'async': False},
                    {'name': 'validateForm', 'params': ['values', 'schema'], 'async': False}
                ]
            }
        }
    
    def _init_design_patterns(self):
        """디자인 패턴 초기화"""
        self.design_patterns = {
            'component_composition': {
                'name': 'Component Composition',
                'description': '작은 컴포넌트를 조합하여 복잡한 UI 구성',
                'use_cases': ['복잡한 UI', '재사용성 중요']
            },
            'container_presentational': {
                'name': 'Container/Presentational',
                'description': '로직과 뷰 분리',
                'use_cases': ['테스트 용이성', '재사용성']
            },
            'render_props': {
                'name': 'Render Props',
                'description': '컴포넌트 간 코드 공유',
                'use_cases': ['로직 공유', '유연한 렌더링']
            },
            'higher_order_component': {
                'name': 'Higher Order Component',
                'description': '컴포넌트 기능 확장',
                'use_cases': ['공통 기능 추가', '인증/권한']
            },
            'compound_component': {
                'name': 'Compound Component',
                'description': '관련 컴포넌트 그룹화',
                'use_cases': ['복잡한 컴포넌트', 'API 단순화']
            },
            'provider_pattern': {
                'name': 'Provider Pattern',
                'description': '전역 상태/서비스 제공',
                'use_cases': ['전역 상태', '테마', '인증']
            }
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    def decide_components(
        self,
        project_structure: Dict[str, Any],
        requirements: Dict[str, Any],
        ui_stack: Dict[str, Any],
        parsed_structure: Dict[str, Any]
    ) -> ComponentDecisionResult:
        """
        컴포넌트 상세 설계 결정
        
        Args:
            project_structure: 프로젝트 구조
            requirements: 프로젝트 요구사항
            ui_stack: UI 스택 정보
            parsed_structure: 파싱된 구조
            
        Returns:
            ComponentDecisionResult: 컴포넌트 설계 결과
        """
        start_time = time.time()
        
        try:
            # 입력 검증
            self._validate_input(project_structure, requirements)
            
            # 필요한 컴포넌트 식별
            required_components = self._identify_required_components(
                requirements,
                ui_stack
            )
            
            # 컴포넌트 명세 생성
            components = []
            for comp_name, comp_info in required_components.items():
                spec = self._create_component_specification(
                    comp_name,
                    comp_info,
                    ui_stack,
                    requirements
                )
                components.append(spec)
            
            # 컴포넌트 트리 구성
            component_tree = self._build_component_tree(components, parsed_structure)
            
            # 상호작용 매트릭스 생성
            interaction_matrix = self._create_interaction_matrix(components)
            
            # 데이터 플로우 분석
            data_flow = self._analyze_data_flow(components, requirements)
            
            # 상태 관리 전략
            state_management = self._design_state_management(
                components,
                ui_stack,
                requirements
            )
            
            # 라우팅 설정
            routing_config = self._design_routing(components, requirements)
            
            # API 계약 정의
            api_contracts = self._define_api_contracts(components, requirements)
            
            # 디자인 패턴 선택
            selected_patterns = self._select_design_patterns(
                components,
                requirements,
                ui_stack
            )
            
            # 재사용성 분석
            reusability_analysis = self._analyze_reusability(components)
            
            # 통계 계산
            total_components = len(components)
            estimated_total_lines = sum(c.estimated_lines for c in components)
            
            # 메타데이터 생성
            metadata = self._generate_metadata(start_time)
            
            # 결과 생성
            result = ComponentDecisionResult(
                components=components,
                component_tree=component_tree,
                interaction_matrix=interaction_matrix,
                data_flow=data_flow,
                state_management=state_management,
                routing_config=routing_config,
                api_contracts=api_contracts,
                design_patterns=selected_patterns,
                total_components=total_components,
                estimated_total_lines=estimated_total_lines,
                reusability_analysis=reusability_analysis,
                metadata=metadata
            )
            
            # 처리 시간 기록
            processing_time = time.time() - start_time
            self.decision_times.append(processing_time)
            metrics.add_metric(
                name="ComponentDecisionTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            
            logger.info(
                f"Successfully decided components",
                extra={
                    "total_components": total_components,
                    "estimated_lines": estimated_total_lines,
                    "processing_time": processing_time
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error deciding components: {e}")
            metrics.add_metric(name="ComponentDecisionError", unit=MetricUnit.Count, value=1)
            raise
    
    def _validate_input(self, project_structure: Dict, requirements: Dict):
        """입력 검증"""
        if not project_structure:
            raise ValueError("프로젝트 구조가 필요합니다")
        
        if not requirements:
            raise ValueError("요구사항이 필요합니다")
    
    def _identify_required_components(
        self,
        requirements: Dict[str, Any],
        ui_stack: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """필요한 컴포넌트 식별"""
        components = {}
        
        # 기본 컴포넌트
        if ui_stack.get('framework') in ['react', 'vue', 'angular']:
            # 레이아웃 컴포넌트
            components['Layout'] = {
                'type': ComponentType.LAYOUT,
                'required': True,
                'template': 'Layout'
            }
            components['Header'] = {
                'type': ComponentType.LAYOUT,
                'required': True
            }
            components['Footer'] = {
                'type': ComponentType.LAYOUT,
                'required': True
            }
            
            # 네비게이션
            components['Navigation'] = {
                'type': ComponentType.NAVIGATION,
                'required': True
            }
        
        # 기능별 컴포넌트
        features = requirements.get('functional_requirements', [])
        
        for feature in features:
            feature_lower = feature.lower() if isinstance(feature, str) else str(feature).lower()
            
            # 인증 관련
            if any(word in feature_lower for word in ['로그인', 'login', '인증', 'auth']):
                components['LoginForm'] = {
                    'type': ComponentType.FORM,
                    'template': 'Form'
                }
                components['AuthProvider'] = {
                    'type': ComponentType.CONTEXT,
                    'service': 'AuthService'
                }
            
            # CRUD 관련
            if any(word in feature_lower for word in ['crud', '생성', '조회', '수정', '삭제']):
                components['DataTable'] = {
                    'type': ComponentType.DATA_DISPLAY,
                    'template': 'DataTable'
                }
                components['CreateForm'] = {
                    'type': ComponentType.FORM,
                    'template': 'Form'
                }
                components['EditForm'] = {
                    'type': ComponentType.FORM,
                    'template': 'Form'
                }
                components['DeleteModal'] = {
                    'type': ComponentType.FEEDBACK,
                    'template': 'Modal'
                }
            
            # 검색 관련
            if any(word in feature_lower for word in ['검색', 'search', '필터', 'filter']):
                components['SearchBar'] = {
                    'type': ComponentType.FORM
                }
                components['FilterPanel'] = {
                    'type': ComponentType.FORM
                }
                components['SearchResults'] = {
                    'type': ComponentType.DATA_DISPLAY
                }
            
            # 대시보드
            if any(word in feature_lower for word in ['대시보드', 'dashboard', '통계']):
                components['Dashboard'] = {
                    'type': ComponentType.PAGE
                }
                components['StatCard'] = {
                    'type': ComponentType.DATA_DISPLAY
                }
                components['Chart'] = {
                    'type': ComponentType.DATA_DISPLAY
                }
            
            # 프로필
            if any(word in feature_lower for word in ['프로필', 'profile', '설정', 'settings']):
                components['ProfilePage'] = {
                    'type': ComponentType.PAGE
                }
                components['ProfileForm'] = {
                    'type': ComponentType.FORM
                }
                components['SettingsPanel'] = {
                    'type': ComponentType.CONTAINER
                }
        
        # UI 컴포넌트
        components.update({
            'Button': {
                'type': ComponentType.PRESENTATIONAL,
                'template': 'Button'
            },
            'Input': {
                'type': ComponentType.PRESENTATIONAL
            },
            'Card': {
                'type': ComponentType.PRESENTATIONAL
            },
            'Modal': {
                'type': ComponentType.FEEDBACK,
                'template': 'Modal'
            },
            'Loading': {
                'type': ComponentType.FEEDBACK
            },
            'ErrorBoundary': {
                'type': ComponentType.UTILITY
            }
        })
        
        # 서비스 컴포넌트
        if ui_stack.get('framework') != 'fastapi':  # Frontend only
            components.update({
                'ApiService': {
                    'type': ComponentType.SERVICE,
                    'template': 'ApiService'
                },
                'ValidationService': {
                    'type': ComponentType.SERVICE,
                    'template': 'ValidationService'
                }
            })
        
        return components
    
    def _create_component_specification(
        self,
        name: str,
        info: Dict[str, Any],
        ui_stack: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> ComponentSpecification:
        """컴포넌트 명세 생성"""
        
        # 템플릿 사용
        template = None
        if info.get('template') and ui_stack.get('framework') == 'react':
            template = self.react_templates.get(info['template'])
        elif info.get('service'):
            template = self.service_templates.get(info['service'])
        
        # 인터페이스 생성
        interface = self._create_component_interface(name, info, template)
        
        # 복잡도 계산
        complexity = self._calculate_complexity(name, interface, info)
        
        # 파일 경로 결정
        file_path = self._determine_file_path(name, info['type'], ui_stack)
        
        # 스타일링 설정
        styling = self._define_styling(name, ui_stack)
        
        # 접근성 설정
        accessibility = self._define_accessibility(name, info['type'])
        
        # 성능 설정
        performance = self._define_performance(name, complexity)
        
        # 테스트 설정
        testing = self._define_testing(name, complexity)
        
        # 예상 라인 수
        estimated_lines = self._estimate_lines(complexity, interface)
        
        # 재사용성 점수
        reusability_score = self._calculate_reusability(name, info['type'], interface)
        
        # 문서화
        documentation = self._generate_documentation(name, interface, info['type'])
        
        return ComponentSpecification(
            name=name,
            type=info['type'],
            complexity=complexity,
            description=f"{name} 컴포넌트",
            file_path=file_path,
            interface=interface,
            styling=styling,
            accessibility=accessibility,
            performance=performance,
            testing=testing,
            documentation=documentation,
            estimated_lines=estimated_lines,
            reusability_score=reusability_score
        )
    
    def _create_component_interface(
        self,
        name: str,
        info: Dict[str, Any],
        template: Optional[Dict]
    ) -> ComponentInterface:
        """컴포넌트 인터페이스 생성"""
        props = []
        methods = []
        states = []
        events = []
        dependencies = []
        
        # 템플릿에서 가져오기
        if template:
            # Props
            if 'props' in template:
                for prop_info in template['props']:
                    props.append(ComponentProperty(
                        name=prop_info['name'],
                        type=prop_info['type'],
                        required=prop_info.get('required', False),
                        default_value=prop_info.get('default'),
                        description=f"{prop_info['name']} property"
                    ))
            
            # States
            if 'states' in template:
                for state_info in template['states']:
                    states.append(ComponentState(
                        name=state_info['name'],
                        type=state_info['type'],
                        initial_value=None,
                        description=f"{state_info['name']} state"
                    ))
            
            # Methods (서비스)
            if 'methods' in template:
                for method_info in template['methods']:
                    methods.append(ComponentMethod(
                        name=method_info['name'],
                        parameters=[{'name': p, 'type': 'any'} for p in method_info.get('params', [])],
                        return_type='Promise<any>' if method_info.get('async') else 'any',
                        description=f"{method_info['name']} method",
                        is_async=method_info.get('async', False)
                    ))
        
        # 타입별 기본 설정
        if info['type'] == ComponentType.PAGE:
            dependencies.extend(['react-router-dom', 'Layout'])
        elif info['type'] == ComponentType.FORM:
            events.extend(['onSubmit', 'onChange', 'onValidate'])
            dependencies.append('ValidationService')
        elif info['type'] == ComponentType.DATA_DISPLAY:
            props.append(ComponentProperty(
                name='data',
                type='array',
                required=True,
                default_value=[],
                description='Display data'
            ))
        
        return ComponentInterface(
            props=props,
            methods=methods,
            states=states,
            events=events,
            dependencies=dependencies
        )
    
    def _calculate_complexity(
        self,
        name: str,
        interface: ComponentInterface,
        info: Dict[str, Any]
    ) -> ComponentComplexity:
        """복잡도 계산"""
        score = 0
        
        # Props 복잡도
        score += len(interface.props) * 2
        
        # States 복잡도
        score += len(interface.states) * 3
        
        # Methods 복잡도
        score += len(interface.methods) * 5
        
        # 타입별 가중치
        type_weights = {
            ComponentType.PAGE: 20,
            ComponentType.FORM: 15,
            ComponentType.DATA_DISPLAY: 15,
            ComponentType.CONTAINER: 10,
            ComponentType.PRESENTATIONAL: 5,
            ComponentType.SERVICE: 25
        }
        score += type_weights.get(info['type'], 10)
        
        # 복잡도 레벨 결정
        if score < 20:
            return ComponentComplexity.SIMPLE
        elif score < 40:
            return ComponentComplexity.MEDIUM
        elif score < 60:
            return ComponentComplexity.COMPLEX
        else:
            return ComponentComplexity.VERY_COMPLEX
    
    def _determine_file_path(
        self,
        name: str,
        comp_type: ComponentType,
        ui_stack: Dict[str, Any]
    ) -> str:
        """파일 경로 결정"""
        framework = ui_stack.get('framework', 'react')
        typescript = ui_stack.get('typescript', False)
        extension = '.tsx' if typescript else '.jsx'
        
        # 타입별 경로
        type_paths = {
            ComponentType.PAGE: 'pages',
            ComponentType.LAYOUT: 'layouts',
            ComponentType.CONTAINER: 'containers',
            ComponentType.PRESENTATIONAL: 'components',
            ComponentType.FORM: 'components/forms',
            ComponentType.DATA_DISPLAY: 'components/data',
            ComponentType.NAVIGATION: 'components/navigation',
            ComponentType.FEEDBACK: 'components/feedback',
            ComponentType.UTILITY: 'utils',
            ComponentType.SERVICE: 'services',
            ComponentType.HOOK: 'hooks',
            ComponentType.CONTEXT: 'contexts',
            ComponentType.STORE: 'store'
        }
        
        base_path = type_paths.get(comp_type, 'components')
        
        # 서비스는 .ts 확장자
        if comp_type == ComponentType.SERVICE:
            extension = '.ts'
        
        return f"src/{base_path}/{name}{extension}"
    
    def _define_styling(self, name: str, ui_stack: Dict[str, Any]) -> Dict[str, Any]:
        """스타일링 설정"""
        css_framework = ui_stack.get('css_framework', 'css')
        
        styling = {
            'method': css_framework,
            'scoped': True,
            'responsive': True
        }
        
        if css_framework == 'tailwindcss':
            styling['classes'] = {
                'container': 'flex flex-col p-4',
                'title': 'text-2xl font-bold mb-4',
                'content': 'flex-1'
            }
        elif css_framework == 'styled-components':
            styling['styled'] = True
            styling['theme'] = True
        
        return styling
    
    def _define_accessibility(self, name: str, comp_type: ComponentType) -> Dict[str, Any]:
        """접근성 설정"""
        accessibility = {
            'aria_label': True,
            'keyboard_navigation': True,
            'screen_reader': True
        }
        
        # 타입별 추가 설정
        if comp_type == ComponentType.FORM:
            accessibility['form_labels'] = True
            accessibility['error_announcements'] = True
        elif comp_type == ComponentType.NAVIGATION:
            accessibility['skip_links'] = True
            accessibility['breadcrumbs'] = True
        elif comp_type == ComponentType.DATA_DISPLAY:
            accessibility['table_headers'] = True
            accessibility['alt_text'] = True
        
        return accessibility
    
    def _define_performance(self, name: str, complexity: ComponentComplexity) -> Dict[str, Any]:
        """성능 설정"""
        performance = {
            'lazy_loading': False,
            'memoization': False,
            'virtualization': False,
            'code_splitting': False
        }
        
        # 복잡도별 최적화
        if complexity in [ComponentComplexity.COMPLEX, ComponentComplexity.VERY_COMPLEX]:
            performance['memoization'] = True
            performance['code_splitting'] = True
        
        # 특정 컴포넌트 최적화
        if 'Table' in name or 'List' in name:
            performance['virtualization'] = True
        if 'Page' in name:
            performance['lazy_loading'] = True
        
        return performance
    
    def _define_testing(self, name: str, complexity: ComponentComplexity) -> Dict[str, Any]:
        """테스트 설정"""
        testing = {
            'unit_tests': True,
            'integration_tests': False,
            'snapshot_tests': True,
            'coverage_target': 80
        }
        
        # 복잡도별 테스트
        if complexity in [ComponentComplexity.COMPLEX, ComponentComplexity.VERY_COMPLEX]:
            testing['integration_tests'] = True
            testing['coverage_target'] = 90
        
        return testing
    
    def _estimate_lines(
        self,
        complexity: ComponentComplexity,
        interface: ComponentInterface
    ) -> int:
        """예상 라인 수 계산"""
        base_lines = {
            ComponentComplexity.SIMPLE: 50,
            ComponentComplexity.MEDIUM: 150,
            ComponentComplexity.COMPLEX: 300,
            ComponentComplexity.VERY_COMPLEX: 500
        }
        
        lines = base_lines[complexity]
        
        # 인터페이스 요소별 추가
        lines += len(interface.props) * 5
        lines += len(interface.methods) * 20
        lines += len(interface.states) * 10
        
        return lines
    
    def _calculate_reusability(
        self,
        name: str,
        comp_type: ComponentType,
        interface: ComponentInterface
    ) -> float:
        """재사용성 점수 계산"""
        score = 0.5  # 기본 점수
        
        # 타입별 점수
        type_scores = {
            ComponentType.PRESENTATIONAL: 0.9,
            ComponentType.UTILITY: 0.95,
            ComponentType.SERVICE: 0.85,
            ComponentType.HOOK: 0.9,
            ComponentType.FORM: 0.7,
            ComponentType.PAGE: 0.3,
            ComponentType.LAYOUT: 0.6
        }
        
        if comp_type in type_scores:
            score = type_scores[comp_type]
        
        # 의존성이 적을수록 재사용성 높음
        if len(interface.dependencies) < 2:
            score += 0.1
        elif len(interface.dependencies) > 5:
            score -= 0.2
        
        # Props가 많으면 유연성 증가
        if len(interface.props) > 3:
            score += 0.05
        
        return min(max(score, 0.0), 1.0)
    
    def _generate_documentation(
        self,
        name: str,
        interface: ComponentInterface,
        comp_type: ComponentType
    ) -> str:
        """문서 생성"""
        doc = f"""
# {name} Component

## Type
{comp_type.value}

## Description
{name} component implementation

## Props
"""
        for prop in interface.props:
            req = "required" if prop.required else "optional"
            doc += f"- `{prop.name}` ({prop.type}) - {req}\n"
        
        if interface.methods:
            doc += "\n## Methods\n"
            for method in interface.methods:
                async_str = "async " if method.is_async else ""
                doc += f"- `{async_str}{method.name}()` - {method.description}\n"
        
        if interface.states:
            doc += "\n## State\n"
            for state in interface.states:
                doc += f"- `{state.name}` ({state.type}) - {state.description}\n"
        
        return doc
    
    def _build_component_tree(
        self,
        components: List[ComponentSpecification],
        parsed_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """컴포넌트 트리 구성"""
        tree = {
            'root': 'App',
            'children': {}
        }
        
        # 페이지 컴포넌트를 최상위로
        pages = [c for c in components if c.type == ComponentType.PAGE]
        for page in pages:
            tree['children'][page.name] = {
                'type': 'page',
                'children': {}
            }
        
        # 레이아웃 컴포넌트
        layouts = [c for c in components if c.type == ComponentType.LAYOUT]
        for layout in layouts:
            if layout.name == 'Layout':
                tree['children']['Layout'] = {
                    'type': 'layout',
                    'children': tree['children']
                }
                tree['children'] = {'Layout': tree['children']['Layout']}
                break
        
        return tree
    
    def _create_interaction_matrix(
        self,
        components: List[ComponentSpecification]
    ) -> Dict[str, List[str]]:
        """상호작용 매트릭스 생성"""
        matrix = {}
        
        for component in components:
            interactions = []
            
            # 의존성 기반 상호작용
            for dep in component.interface.dependencies:
                # 의존성이 다른 컴포넌트인 경우
                if any(c.name == dep for c in components):
                    interactions.append(dep)
            
            # 타입 기반 상호작용
            if component.type == ComponentType.FORM:
                # Form은 보통 Button과 상호작용
                if any(c.name == 'Button' for c in components):
                    interactions.append('Button')
            elif component.type == ComponentType.PAGE:
                # Page는 여러 컴포넌트와 상호작용
                interactions.extend(['Header', 'Footer', 'Navigation'])
            
            matrix[component.name] = interactions
        
        return matrix
    
    def _analyze_data_flow(
        self,
        components: List[ComponentSpecification],
        requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """데이터 플로우 분석"""
        data_flow = {
            'sources': [],
            'sinks': [],
            'transformers': [],
            'flow_diagram': {}
        }
        
        # 데이터 소스 식별
        for component in components:
            if component.type == ComponentType.SERVICE:
                data_flow['sources'].append(component.name)
            elif component.type == ComponentType.FORM:
                data_flow['sources'].append(component.name)
            elif component.type == ComponentType.DATA_DISPLAY:
                data_flow['sinks'].append(component.name)
            elif component.type in [ComponentType.CONTAINER, ComponentType.PAGE]:
                data_flow['transformers'].append(component.name)
        
        # 플로우 다이어그램
        data_flow['flow_diagram'] = {
            'UserInput': ['Form'],
            'Form': ['ValidationService', 'ApiService'],
            'ApiService': ['Store'],
            'Store': ['Components'],
            'Components': ['UI']
        }
        
        return data_flow
    
    def _design_state_management(
        self,
        components: List[ComponentSpecification],
        ui_stack: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상태 관리 설계"""
        state_mgmt = ui_stack.get('state_management', 'context-api')
        
        design = {
            'solution': state_mgmt,
            'global_state': {},
            'local_state': {},
            'derived_state': {}
        }
        
        # 전역 상태
        design['global_state'] = {
            'user': {
                'type': 'object',
                'description': '사용자 정보',
                'persistence': 'localStorage'
            },
            'theme': {
                'type': 'string',
                'description': '테마 설정',
                'persistence': 'localStorage'
            }
        }
        
        # 기능별 상태
        if any('auth' in str(r).lower() for r in requirements.get('functional_requirements', [])):
            design['global_state']['auth'] = {
                'type': 'object',
                'description': '인증 상태',
                'persistence': 'sessionStorage'
            }
        
        # 로컬 상태
        for component in components:
            if component.interface.states:
                design['local_state'][component.name] = [
                    s.name for s in component.interface.states
                ]
        
        return design
    
    def _design_routing(
        self,
        components: List[ComponentSpecification],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """라우팅 설계"""
        routing = {
            'type': 'client-side',
            'routes': [],
            'guards': [],
            'redirects': []
        }
        
        # 페이지 컴포넌트를 라우트로
        pages = [c for c in components if c.type == ComponentType.PAGE]
        
        for page in pages:
            route_path = f"/{page.name.lower().replace('page', '')}"
            if 'Dashboard' in page.name:
                route_path = '/'
            elif 'Profile' in page.name:
                route_path = '/profile'
            
            routing['routes'].append({
                'path': route_path,
                'component': page.name,
                'exact': True
            })
        
        # 기본 라우트
        routing['routes'].extend([
            {'path': '/login', 'component': 'LoginPage', 'exact': True},
            {'path': '/404', 'component': 'NotFoundPage', 'exact': True}
        ])
        
        # 가드
        if any('auth' in str(r).lower() for r in requirements.get('functional_requirements', [])):
            routing['guards'].append({
                'name': 'AuthGuard',
                'routes': ['/dashboard', '/profile'],
                'redirect': '/login'
            })
        
        return routing
    
    def _define_api_contracts(
        self,
        components: List[ComponentSpecification],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """API 계약 정의"""
        contracts = []
        
        # 기본 CRUD API
        if any('crud' in str(r).lower() for r in requirements.get('functional_requirements', [])):
            contracts.append({
                'endpoint': '/api/items',
                'methods': {
                    'GET': {'description': 'Get all items', 'response': 'Item[]'},
                    'POST': {'description': 'Create item', 'body': 'Item', 'response': 'Item'}
                }
            })
            contracts.append({
                'endpoint': '/api/items/:id',
                'methods': {
                    'GET': {'description': 'Get item by ID', 'response': 'Item'},
                    'PUT': {'description': 'Update item', 'body': 'Item', 'response': 'Item'},
                    'DELETE': {'description': 'Delete item', 'response': 'void'}
                }
            })
        
        # 인증 API
        if any('auth' in str(r).lower() for r in requirements.get('functional_requirements', [])):
            contracts.append({
                'endpoint': '/api/auth/login',
                'methods': {
                    'POST': {
                        'description': 'User login',
                        'body': 'LoginCredentials',
                        'response': 'AuthToken'
                    }
                }
            })
            contracts.append({
                'endpoint': '/api/auth/logout',
                'methods': {
                    'POST': {'description': 'User logout', 'response': 'void'}
                }
            })
        
        return contracts
    
    def _select_design_patterns(
        self,
        components: List[ComponentSpecification],
        requirements: Dict[str, Any],
        ui_stack: Dict[str, Any]
    ) -> List[str]:
        """디자인 패턴 선택"""
        selected_patterns = []
        
        # 컴포넌트 구성은 기본
        selected_patterns.append('component_composition')
        
        # Container/Presentational 분리
        has_containers = any(c.type == ComponentType.CONTAINER for c in components)
        has_presentational = any(c.type == ComponentType.PRESENTATIONAL for c in components)
        if has_containers and has_presentational:
            selected_patterns.append('container_presentational')
        
        # Provider Pattern (상태 관리)
        if ui_stack.get('state_management'):
            selected_patterns.append('provider_pattern')
        
        # HOC (인증 등)
        if any('auth' in str(r).lower() for r in requirements.get('functional_requirements', [])):
            selected_patterns.append('higher_order_component')
        
        # Compound Component (복잡한 컴포넌트)
        complex_components = [c for c in components if c.complexity in [
            ComponentComplexity.COMPLEX,
            ComponentComplexity.VERY_COMPLEX
        ]]
        if len(complex_components) > 3:
            selected_patterns.append('compound_component')
        
        return selected_patterns
    
    def _analyze_reusability(
        self,
        components: List[ComponentSpecification]
    ) -> Dict[str, Any]:
        """재사용성 분석"""
        analysis = {
            'highly_reusable': [],
            'moderately_reusable': [],
            'low_reusability': [],
            'average_score': 0,
            'recommendations': []
        }
        
        total_score = 0
        for component in components:
            total_score += component.reusability_score
            
            if component.reusability_score >= 0.8:
                analysis['highly_reusable'].append(component.name)
            elif component.reusability_score >= 0.5:
                analysis['moderately_reusable'].append(component.name)
            else:
                analysis['low_reusability'].append(component.name)
        
        analysis['average_score'] = total_score / len(components) if components else 0
        
        # 권장사항
        if analysis['average_score'] < 0.6:
            analysis['recommendations'].append(
                "컴포넌트를 더 작은 단위로 분리하여 재사용성을 높이세요"
            )
        
        if len(analysis['low_reusability']) > len(components) * 0.3:
            analysis['recommendations'].append(
                "공통 기능을 유틸리티나 훅으로 추출하세요"
            )
        
        return analysis
    
    def _generate_metadata(self, start_time: float) -> Dict[str, Any]:
        """메타데이터 생성"""
        return {
            'agent_name': 'component-decision-agent',
            'version': '1.0.0',
            'environment': self.environment,
            'processing_time': time.time() - start_time,
            'timestamp': time.time(),
            'ai_analysis_used': self.config.get('use_ai_analysis', False)
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러
    
    Note: 이 에이전트는 복잡한 분석으로 인해 EC2/ECS에서 실행 권장
    Lambda에서 실행 시 timeout 설정 필요 (최소 2분)
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        project_structure = body.get('project_structure', {})
        requirements = body.get('requirements', {})
        ui_stack = body.get('ui_stack', {})
        parsed_structure = body.get('parsed_structure', {})
        
        # Agent 실행
        agent = ComponentDecisionAgent()
        result = agent.decide_components(
            project_structure,
            requirements,
            ui_stack,
            parsed_structure
        )
        
        # 응답 구성
        response_body = {
            'components': [c.to_dict() for c in result.components],
            'component_tree': result.component_tree,
            'interaction_matrix': result.interaction_matrix,
            'data_flow': result.data_flow,
            'state_management': result.state_management,
            'routing_config': result.routing_config,
            'api_contracts': result.api_contracts,
            'design_patterns': result.design_patterns,
            'statistics': {
                'total_components': result.total_components,
                'estimated_total_lines': result.estimated_total_lines
            },
            'reusability_analysis': result.reusability_analysis,
            'metadata': result.metadata
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body, ensure_ascii=False)
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
    test_agent = ComponentDecisionAgent('development')
    
    test_case = {
        'project_structure': {
            'root_name': 'todo-app',
            'framework': 'react',
            'project_type': 'web-application'
        },
        'requirements': {
            'functional_requirements': [
                '사용자 인증 및 로그인',
                'Todo CRUD 작업',
                '검색 및 필터링',
                '대시보드 통계'
            ]
        },
        'ui_stack': {
            'framework': 'react',
            'typescript': True,
            'css_framework': 'tailwindcss',
            'state_management': 'redux-toolkit'
        },
        'parsed_structure': {
            'directories': ['src', 'components', 'pages']
        }
    }
    
    print("테스트 실행 중...")
    result = test_agent.decide_components(
        test_case['project_structure'],
        test_case['requirements'],
        test_case['ui_stack'],
        test_case['parsed_structure']
    )
    
    print(f"\n총 컴포넌트: {result.total_components}")
    print(f"예상 총 라인 수: {result.estimated_total_lines}")
    print(f"선택된 디자인 패턴: {', '.join(result.design_patterns)}")
    print(f"평균 재사용성: {result.reusability_analysis['average_score']:.2f}")
    
    print("\n주요 컴포넌트:")
    for comp in result.components[:5]:
        print(f"  - {comp.name} ({comp.type.value}): {comp.estimated_lines} lines")