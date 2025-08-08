"""
UI Selection Agent - Production Ready Implementation
프로젝트 타입에 따른 최적 UI 프레임워크와 기술 스택 선택

AWS Lambda에서 실행 (실행시간 < 10초)
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

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


class FrameworkCategory(Enum):
    """프레임워크 카테고리"""
    FRONTEND = "frontend"
    MOBILE = "mobile"
    BACKEND = "backend"
    DESKTOP = "desktop"
    CLI = "cli"
    GAME = "game"
    ML = "ml"
    BLOCKCHAIN = "blockchain"
    IOT = "iot"


@dataclass
class FrameworkInfo:
    """프레임워크 상세 정보"""
    name: str
    category: str
    version: str
    popularity: float  # 0.0 ~ 1.0
    learning_curve: str  # easy, medium, hard
    performance: str  # low, medium, high
    ecosystem: str  # small, medium, large
    pros: List[str]
    cons: List[str]
    best_for: List[str]
    dependencies: List[str]


@dataclass
class UIStack:
    """선택된 UI 스택"""
    framework: str
    ui_library: Optional[str]
    css_framework: Optional[str]
    state_management: Optional[str]
    routing: Optional[str]
    build_tool: Optional[str]
    testing_framework: Optional[str]
    package_manager: str
    language: str
    typescript: bool


@dataclass
class UISelectionResult:
    """UI 선택 결과"""
    project_type: str
    recommended_stack: UIStack
    alternative_stacks: List[UIStack]
    framework_details: FrameworkInfo
    rationale: str
    setup_commands: List[str]
    folder_structure: Dict[str, Any]
    dependencies: Dict[str, str]
    dev_dependencies: Dict[str, str]
    configuration_files: List[str]
    confidence_score: float
    metadata: Dict[str, Any]


class UISelectionAgent:
    """Production-ready UI Selection Agent"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # 프레임워크 데이터베이스 초기화
        self._init_framework_database()
        
        # 메트릭 초기화
        self.selection_times = []
        
        logger.info(f"UI Selection Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/ui-selection-agent/',
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
                'max_alternatives': 3,
                'min_confidence_score': 0.5,
                'timeout_seconds': 10
            }
    
    def _init_framework_database(self):
        """프레임워크 데이터베이스 초기화"""
        
        # Frontend 프레임워크
        self.frontend_frameworks = {
            'react': FrameworkInfo(
                name='React',
                category='frontend',
                version='18.2.0',
                popularity=0.95,
                learning_curve='medium',
                performance='high',
                ecosystem='large',
                pros=[
                    '거대한 커뮤니티와 생태계',
                    '유연한 아키텍처',
                    '뛰어난 성능 (Virtual DOM)',
                    '풍부한 컴포넌트 라이브러리'
                ],
                cons=[
                    '초기 설정 복잡도',
                    '많은 보일러플레이트',
                    '빠른 버전 변화'
                ],
                best_for=[
                    '대규모 SPA',
                    '복잡한 상태 관리',
                    '재사용 가능한 컴포넌트'
                ],
                dependencies=['react', 'react-dom']
            ),
            'vue': FrameworkInfo(
                name='Vue.js',
                category='frontend',
                version='3.3.0',
                popularity=0.85,
                learning_curve='easy',
                performance='high',
                ecosystem='large',
                pros=[
                    '쉬운 학습 곡선',
                    '뛰어난 문서',
                    '템플릿 기반 구문',
                    '점진적 도입 가능'
                ],
                cons=[
                    'React보다 작은 생태계',
                    '대규모 앱에서 복잡도',
                    '타입스크립트 지원 미흡'
                ],
                best_for=[
                    '중소규모 애플리케이션',
                    '빠른 프로토타이핑',
                    '기존 프로젝트 통합'
                ],
                dependencies=['vue']
            ),
            'angular': FrameworkInfo(
                name='Angular',
                category='frontend',
                version='17.0.0',
                popularity=0.75,
                learning_curve='hard',
                performance='high',
                ecosystem='large',
                pros=[
                    '완전한 프레임워크',
                    '강력한 CLI',
                    '엔터프라이즈 지원',
                    'TypeScript 기본 지원'
                ],
                cons=[
                    '가파른 학습 곡선',
                    '무거운 번들 크기',
                    '복잡한 개념'
                ],
                best_for=[
                    '엔터프라이즈 애플리케이션',
                    '대규모 팀 프로젝트',
                    '강타입 시스템'
                ],
                dependencies=['@angular/core', '@angular/common']
            ),
            'svelte': FrameworkInfo(
                name='Svelte',
                category='frontend',
                version='4.2.0',
                popularity=0.65,
                learning_curve='easy',
                performance='very-high',
                ecosystem='medium',
                pros=[
                    '컴파일 타임 최적화',
                    '작은 번들 크기',
                    '반응형 프로그래밍',
                    'No Virtual DOM'
                ],
                cons=[
                    '작은 커뮤니티',
                    '제한된 생태계',
                    '도구 지원 부족'
                ],
                best_for=[
                    '성능 중심 앱',
                    '작은 번들 필요',
                    '인터랙티브 UI'
                ],
                dependencies=['svelte']
            ),
            'nextjs': FrameworkInfo(
                name='Next.js',
                category='frontend',
                version='14.0.0',
                popularity=0.90,
                learning_curve='medium',
                performance='very-high',
                ecosystem='large',
                pros=[
                    'SSR/SSG 지원',
                    'SEO 최적화',
                    '파일 기반 라우팅',
                    '빌트인 최적화'
                ],
                cons=[
                    'React 지식 필요',
                    '복잡한 배포',
                    'Vercel 종속성'
                ],
                best_for=[
                    'SEO 중요 사이트',
                    '전자상거래',
                    '블로그/CMS'
                ],
                dependencies=['next', 'react', 'react-dom']
            )
        }
        
        # Mobile 프레임워크
        self.mobile_frameworks = {
            'react-native': FrameworkInfo(
                name='React Native',
                category='mobile',
                version='0.72.0',
                popularity=0.90,
                learning_curve='medium',
                performance='high',
                ecosystem='large',
                pros=[
                    'React 지식 재사용',
                    '크로스 플랫폼',
                    '핫 리로드',
                    '네이티브 모듈'
                ],
                cons=[
                    '네이티브 성능 차이',
                    '디버깅 어려움',
                    '업데이트 복잡도'
                ],
                best_for=[
                    '크로스 플랫폼 앱',
                    'MVP 개발',
                    'React 팀'
                ],
                dependencies=['react-native', 'react']
            ),
            'flutter': FrameworkInfo(
                name='Flutter',
                category='mobile',
                version='3.16.0',
                popularity=0.85,
                learning_curve='medium',
                performance='very-high',
                ecosystem='large',
                pros=[
                    '뛰어난 성능',
                    '아름다운 UI',
                    '핫 리로드',
                    'Dart 언어'
                ],
                cons=[
                    'Dart 학습 필요',
                    '큰 앱 크기',
                    '플랫폼 특화 기능'
                ],
                best_for=[
                    '아름다운 UI',
                    '고성능 앱',
                    '구글 서비스'
                ],
                dependencies=['flutter']
            ),
            'ionic': FrameworkInfo(
                name='Ionic',
                category='mobile',
                version='7.0.0',
                popularity=0.70,
                learning_curve='easy',
                performance='medium',
                ecosystem='large',
                pros=[
                    '웹 기술 사용',
                    '빠른 개발',
                    'PWA 지원',
                    '다양한 플러그인'
                ],
                cons=[
                    '성능 제한',
                    '네이티브 느낌 부족',
                    'WebView 의존'
                ],
                best_for=[
                    '하이브리드 앱',
                    'PWA',
                    '웹 개발자'
                ],
                dependencies=['@ionic/angular', '@capacitor/core']
            )
        }
        
        # Backend 프레임워크
        self.backend_frameworks = {
            'fastapi': FrameworkInfo(
                name='FastAPI',
                category='backend',
                version='0.104.0',
                popularity=0.85,
                learning_curve='easy',
                performance='very-high',
                ecosystem='large',
                pros=[
                    '자동 문서화',
                    '타입 힌트',
                    '비동기 지원',
                    '뛰어난 성능'
                ],
                cons=[
                    '상대적으로 신규',
                    'ORM 미포함',
                    'Python 전용'
                ],
                best_for=[
                    'REST API',
                    '마이크로서비스',
                    'ML 서비스'
                ],
                dependencies=['fastapi', 'uvicorn']
            ),
            'express': FrameworkInfo(
                name='Express.js',
                category='backend',
                version='4.18.0',
                popularity=0.95,
                learning_curve='easy',
                performance='high',
                ecosystem='very-large',
                pros=[
                    '간단하고 유연',
                    '거대한 생태계',
                    '많은 미들웨어',
                    '빠른 개발'
                ],
                cons=[
                    '구조 없음',
                    '보안 직접 구현',
                    '콜백 지옥'
                ],
                best_for=[
                    'REST API',
                    '실시간 앱',
                    'Node.js 서비스'
                ],
                dependencies=['express']
            )
        }
        
        # 프로젝트 타입별 추천 매핑
        self.project_type_mapping = {
            'web-application': ['react', 'vue', 'angular', 'nextjs', 'svelte'],
            'mobile-application': ['react-native', 'flutter', 'ionic'],
            'backend-api': ['fastapi', 'express'],
            'desktop-application': ['electron', 'tauri'],
            'cli-tool': ['python', 'nodejs', 'go'],
            'microservice': ['fastapi', 'express', 'go'],
            'ml-project': ['python', 'jupyter'],
            'blockchain': ['solidity', 'rust'],
            'iot-application': ['python', 'c++', 'rust'],
            'game-development': ['unity', 'godot', 'unreal']
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    def select_ui_stack(
        self,
        project_type: str,
        requirements: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> UISelectionResult:
        """
        프로젝트에 최적화된 UI 스택 선택
        
        Args:
            project_type: 프로젝트 타입
            requirements: 프로젝트 요구사항
            preferences: 사용자 선호사항
            
        Returns:
            UISelectionResult: 선택된 UI 스택
        """
        start_time = time.time()
        
        try:
            # 입력 검증
            self._validate_input(project_type, requirements)
            
            # 프레임워크 후보 선정
            candidates = self._get_framework_candidates(project_type, requirements, preferences)
            
            # 최적 프레임워크 선택
            best_framework = self._select_best_framework(candidates, requirements, preferences)
            
            # UI 스택 구성
            ui_stack = self._build_ui_stack(best_framework, requirements, preferences)
            
            # 대안 스택 생성
            alternatives = self._generate_alternatives(candidates, requirements, preferences, best_framework)
            
            # 프로젝트 구조 생성
            folder_structure = self._generate_folder_structure(ui_stack)
            
            # 의존성 분석
            dependencies, dev_dependencies = self._analyze_dependencies(ui_stack)
            
            # 설정 파일 목록
            config_files = self._get_configuration_files(ui_stack)
            
            # 설치 명령어 생성
            setup_commands = self._generate_setup_commands(ui_stack)
            
            # 선택 이유 생성
            rationale = self._generate_rationale(best_framework, requirements)
            
            # 신뢰도 계산
            confidence = self._calculate_confidence(best_framework, requirements, preferences)
            
            # 메타데이터 생성
            metadata = self._generate_metadata(start_time)
            
            # 결과 구성
            result = UISelectionResult(
                project_type=project_type,
                recommended_stack=ui_stack,
                alternative_stacks=alternatives,
                framework_details=self._get_framework_info(best_framework),
                rationale=rationale,
                setup_commands=setup_commands,
                folder_structure=folder_structure,
                dependencies=dependencies,
                dev_dependencies=dev_dependencies,
                configuration_files=config_files,
                confidence_score=confidence,
                metadata=metadata
            )
            
            # 처리 시간 기록
            processing_time = time.time() - start_time
            self.selection_times.append(processing_time)
            metrics.add_metric(
                name="UISelectionTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            
            logger.info(
                f"Successfully selected UI stack",
                extra={
                    "framework": ui_stack.framework,
                    "confidence": confidence,
                    "processing_time": processing_time
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error selecting UI stack: {e}")
            metrics.add_metric(name="UISelectionError", unit=MetricUnit.Count, value=1)
            raise
    
    def _validate_input(self, project_type: str, requirements: Dict[str, Any]):
        """입력 검증"""
        if not project_type:
            raise ValueError("프로젝트 타입이 필요합니다")
        
        if not requirements:
            raise ValueError("요구사항이 필요합니다")
        
        if project_type not in self.project_type_mapping:
            raise ValueError(f"지원하지 않는 프로젝트 타입: {project_type}")
    
    def _get_framework_candidates(
        self,
        project_type: str,
        requirements: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> List[str]:
        """프레임워크 후보 선정"""
        # 기본 후보
        candidates = self.project_type_mapping.get(project_type, [])
        
        # 사용자 선호 프레임워크 우선
        if preferences and preferences.get('framework'):
            preferred = preferences['framework']
            if preferred in candidates:
                candidates = [preferred] + [c for c in candidates if c != preferred]
        
        return candidates[:5]  # 최대 5개 후보
    
    def _select_best_framework(
        self,
        candidates: List[str],
        requirements: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> str:
        """최적 프레임워크 선택"""
        scores = {}
        
        for candidate in candidates:
            score = 0.0
            
            # 인기도 점수
            framework_info = self._get_framework_info(candidate)
            if framework_info:
                score += framework_info.popularity * 30
                
                # 학습 곡선 고려
                if requirements.get('experience_level') == 'beginner':
                    if framework_info.learning_curve == 'easy':
                        score += 20
                    elif framework_info.learning_curve == 'medium':
                        score += 10
                
                # 성능 요구사항
                if requirements.get('performance_critical'):
                    if 'high' in framework_info.performance:
                        score += 20
                
                # 생태계 크기
                if framework_info.ecosystem in ['large', 'very-large']:
                    score += 15
            
            # 사용자 선호
            if preferences and preferences.get('framework') == candidate:
                score += 30
            
            scores[candidate] = score
        
        # 최고 점수 프레임워크 선택
        return max(scores, key=scores.get) if scores else candidates[0]
    
    def _build_ui_stack(
        self,
        framework: str,
        requirements: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> UIStack:
        """UI 스택 구성"""
        stack = UIStack(
            framework=framework,
            ui_library=None,
            css_framework=None,
            state_management=None,
            routing=None,
            build_tool=None,
            testing_framework=None,
            package_manager='npm',
            language='javascript',
            typescript=False
        )
        
        # TypeScript 설정
        if preferences and preferences.get('typescript'):
            stack.typescript = True
            stack.language = 'typescript'
        elif requirements.get('type_safety'):
            stack.typescript = True
            stack.language = 'typescript'
        
        # React 스택
        if framework == 'react':
            stack.ui_library = 'react'
            stack.css_framework = preferences.get('styling', 'tailwindcss') if preferences else 'tailwindcss'
            stack.state_management = 'redux-toolkit' if requirements.get('complex_state') else 'context-api'
            stack.routing = 'react-router-dom'
            stack.build_tool = 'vite'
            stack.testing_framework = 'jest + react-testing-library'
        
        # Vue 스택
        elif framework == 'vue':
            stack.ui_library = 'vue'
            stack.css_framework = 'tailwindcss'
            stack.state_management = 'pinia'
            stack.routing = 'vue-router'
            stack.build_tool = 'vite'
            stack.testing_framework = 'vitest'
        
        # Angular 스택
        elif framework == 'angular':
            stack.ui_library = '@angular/core'
            stack.css_framework = 'angular-material'
            stack.state_management = 'ngrx' if requirements.get('complex_state') else 'services'
            stack.routing = '@angular/router'
            stack.build_tool = 'angular-cli'
            stack.testing_framework = 'karma + jasmine'
            stack.typescript = True  # Angular는 항상 TypeScript
            stack.language = 'typescript'
        
        # Next.js 스택
        elif framework == 'nextjs':
            stack.ui_library = 'react'
            stack.css_framework = 'tailwindcss'
            stack.state_management = 'zustand'
            stack.routing = 'file-based'
            stack.build_tool = 'next'
            stack.testing_framework = 'jest + react-testing-library'
        
        # React Native 스택
        elif framework == 'react-native':
            stack.ui_library = 'react-native'
            stack.css_framework = 'styled-components'
            stack.state_management = 'redux-toolkit'
            stack.routing = 'react-navigation'
            stack.build_tool = 'metro'
            stack.testing_framework = 'jest + detox'
        
        # FastAPI 스택
        elif framework == 'fastapi':
            stack.ui_library = None
            stack.css_framework = None
            stack.state_management = None
            stack.routing = 'fastapi'
            stack.build_tool = 'poetry'
            stack.testing_framework = 'pytest'
            stack.package_manager = 'pip'
            stack.language = 'python'
            stack.typescript = False
        
        return stack
    
    def _generate_alternatives(
        self,
        candidates: List[str],
        requirements: Dict[str, Any],
        preferences: Optional[Dict[str, Any]],
        selected: str
    ) -> List[UIStack]:
        """대안 스택 생성"""
        alternatives = []
        max_alternatives = int(self.config.get('max_alternatives', 3))
        
        for candidate in candidates[:max_alternatives + 1]:
            if candidate != selected:
                alt_stack = self._build_ui_stack(candidate, requirements, preferences)
                alternatives.append(alt_stack)
        
        return alternatives[:max_alternatives]
    
    def _generate_folder_structure(self, stack: UIStack) -> Dict[str, Any]:
        """프로젝트 폴더 구조 생성"""
        if stack.framework in ['react', 'vue', 'angular', 'nextjs', 'svelte']:
            return {
                'src': {
                    'components': {},
                    'pages': {} if stack.framework == 'nextjs' else None,
                    'views': {} if stack.framework == 'vue' else None,
                    'services': {},
                    'utils': {},
                    'hooks': {} if stack.framework == 'react' else None,
                    'stores': {} if stack.state_management else None,
                    'styles': {},
                    'assets': {
                        'images': {},
                        'fonts': {}
                    }
                },
                'public': {},
                'tests': {
                    'unit': {},
                    'integration': {},
                    'e2e': {}
                },
                'config': {}
            }
        elif stack.framework == 'fastapi':
            return {
                'app': {
                    'api': {
                        'v1': {
                            'endpoints': {},
                            'deps': {}
                        }
                    },
                    'core': {},
                    'models': {},
                    'schemas': {},
                    'services': {},
                    'db': {}
                },
                'tests': {},
                'alembic': {},
                'scripts': {}
            }
        else:
            return {'src': {}}
    
    def _analyze_dependencies(self, stack: UIStack) -> Tuple[Dict[str, str], Dict[str, str]]:
        """의존성 분석"""
        dependencies = {}
        dev_dependencies = {}
        
        if stack.framework == 'react':
            dependencies = {
                'react': '^18.2.0',
                'react-dom': '^18.2.0'
            }
            if stack.routing:
                dependencies['react-router-dom'] = '^6.20.0'
            if stack.state_management == 'redux-toolkit':
                dependencies['@reduxjs/toolkit'] = '^2.0.0'
                dependencies['react-redux'] = '^9.0.0'
            
            dev_dependencies = {
                'vite': '^5.0.0',
                '@vitejs/plugin-react': '^4.2.0'
            }
            if stack.typescript:
                dev_dependencies['typescript'] = '^5.3.0'
                dev_dependencies['@types/react'] = '^18.2.0'
                dev_dependencies['@types/react-dom'] = '^18.2.0'
        
        elif stack.framework == 'vue':
            dependencies = {
                'vue': '^3.3.0'
            }
            if stack.routing:
                dependencies['vue-router'] = '^4.2.0'
            if stack.state_management == 'pinia':
                dependencies['pinia'] = '^2.1.0'
            
            dev_dependencies = {
                'vite': '^5.0.0',
                '@vitejs/plugin-vue': '^4.5.0'
            }
        
        elif stack.framework == 'fastapi':
            dependencies = {
                'fastapi': '>=0.104.0',
                'uvicorn': '>=0.24.0',
                'pydantic': '>=2.5.0',
                'sqlalchemy': '>=2.0.0'
            }
            dev_dependencies = {
                'pytest': '>=7.4.0',
                'pytest-asyncio': '>=0.21.0',
                'black': '>=23.11.0',
                'mypy': '>=1.7.0'
            }
        
        # CSS 프레임워크
        if stack.css_framework == 'tailwindcss':
            dev_dependencies['tailwindcss'] = '^3.3.0'
            dev_dependencies['autoprefixer'] = '^10.4.0'
            dev_dependencies['postcss'] = '^8.4.0'
        
        return dependencies, dev_dependencies
    
    def _get_configuration_files(self, stack: UIStack) -> List[str]:
        """설정 파일 목록"""
        files = ['package.json', '.gitignore', 'README.md']
        
        if stack.framework in ['react', 'vue', 'svelte']:
            files.extend(['vite.config.js', 'index.html'])
        elif stack.framework == 'angular':
            files.extend(['angular.json', 'tsconfig.json'])
        elif stack.framework == 'nextjs':
            files.extend(['next.config.js', 'tsconfig.json'])
        elif stack.framework == 'fastapi':
            files = ['pyproject.toml', 'requirements.txt', '.env', 'README.md']
        
        if stack.typescript and stack.framework != 'angular':
            files.append('tsconfig.json')
        
        if stack.css_framework == 'tailwindcss':
            files.extend(['tailwind.config.js', 'postcss.config.js'])
        
        if stack.testing_framework:
            if 'jest' in stack.testing_framework:
                files.append('jest.config.js')
            elif 'vitest' in stack.testing_framework:
                files.append('vitest.config.js')
            elif 'pytest' in stack.testing_framework:
                files.append('pytest.ini')
        
        return files
    
    def _generate_setup_commands(self, stack: UIStack) -> List[str]:
        """설치 명령어 생성"""
        commands = []
        
        if stack.framework == 'react':
            if stack.build_tool == 'vite':
                commands.append('npm create vite@latest . -- --template react')
                if stack.typescript:
                    commands[-1] = 'npm create vite@latest . -- --template react-ts'
            commands.append('npm install')
            if stack.css_framework == 'tailwindcss':
                commands.append('npm install -D tailwindcss postcss autoprefixer')
                commands.append('npx tailwindcss init -p')
        
        elif stack.framework == 'vue':
            commands.append('npm create vue@latest .')
            commands.append('npm install')
        
        elif stack.framework == 'angular':
            commands.append('npm install -g @angular/cli')
            commands.append('ng new . --routing --style=css')
        
        elif stack.framework == 'nextjs':
            commands.append('npx create-next-app@latest . --typescript --tailwind --app')
        
        elif stack.framework == 'fastapi':
            commands.append('python -m venv venv')
            commands.append('source venv/bin/activate  # Linux/Mac')
            commands.append('pip install fastapi uvicorn[standard]')
            commands.append('pip install -r requirements.txt')
        
        commands.append('# 개발 서버 실행')
        if stack.framework in ['react', 'vue']:
            commands.append('npm run dev')
        elif stack.framework == 'angular':
            commands.append('ng serve')
        elif stack.framework == 'nextjs':
            commands.append('npm run dev')
        elif stack.framework == 'fastapi':
            commands.append('uvicorn app.main:app --reload')
        
        return commands
    
    def _generate_rationale(self, framework: str, requirements: Dict[str, Any]) -> str:
        """선택 이유 생성"""
        framework_info = self._get_framework_info(framework)
        if not framework_info:
            return f"{framework}가 선택되었습니다."
        
        rationale = f"{framework_info.name}를 선택한 이유:\n"
        
        # 장점 기반 설명
        if framework_info.pros:
            rationale += f"• 주요 장점: {', '.join(framework_info.pros[:3])}\n"
        
        # 요구사항 매칭
        if requirements.get('performance_critical') and 'high' in framework_info.performance:
            rationale += "• 높은 성능 요구사항을 충족합니다\n"
        
        if requirements.get('experience_level') == 'beginner' and framework_info.learning_curve == 'easy':
            rationale += "• 초보자에게 적합한 쉬운 학습 곡선을 가지고 있습니다\n"
        
        if framework_info.ecosystem in ['large', 'very-large']:
            rationale += "• 풍부한 생태계와 커뮤니티 지원을 제공합니다\n"
        
        # 최적 사용 사례
        if framework_info.best_for:
            rationale += f"• 최적 사용 사례: {', '.join(framework_info.best_for[:2])}\n"
        
        return rationale
    
    def _calculate_confidence(
        self,
        framework: str,
        requirements: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> float:
        """신뢰도 점수 계산"""
        score = 0.5  # 기본 점수
        
        framework_info = self._get_framework_info(framework)
        if framework_info:
            # 인기도 기반
            score += framework_info.popularity * 0.2
            
            # 생태계 크기
            if framework_info.ecosystem in ['large', 'very-large']:
                score += 0.1
            
            # 사용자 선호 일치
            if preferences and preferences.get('framework') == framework:
                score += 0.2
            
            # 요구사항 매칭
            matches = 0
            total = 0
            
            if requirements.get('performance_critical'):
                total += 1
                if 'high' in framework_info.performance:
                    matches += 1
            
            if requirements.get('experience_level'):
                total += 1
                if requirements['experience_level'] == 'beginner' and framework_info.learning_curve == 'easy':
                    matches += 1
                elif requirements['experience_level'] == 'expert' and framework_info.learning_curve in ['medium', 'hard']:
                    matches += 1
            
            if total > 0:
                score += (matches / total) * 0.2
        
        return min(score, 1.0)
    
    def _get_framework_info(self, framework: str) -> Optional[FrameworkInfo]:
        """프레임워크 정보 조회"""
        # 모든 프레임워크 데이터베이스 통합
        all_frameworks = {
            **self.frontend_frameworks,
            **self.mobile_frameworks,
            **self.backend_frameworks
        }
        return all_frameworks.get(framework)
    
    def _generate_metadata(self, start_time: float) -> Dict[str, Any]:
        """메타데이터 생성"""
        return {
            'agent_name': 'ui-selection-agent',
            'version': '1.0.0',
            'environment': self.environment,
            'processing_time': time.time() - start_time,
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
        project_type = body.get('project_type', '')
        requirements = body.get('requirements', {})
        preferences = body.get('preferences')
        
        # Agent 실행
        agent = UISelectionAgent()
        result = agent.select_ui_stack(project_type, requirements, preferences)
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(asdict(result), ensure_ascii=False)
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
    test_agent = UISelectionAgent('development')
    
    test_cases = [
        {
            'project_type': 'web-application',
            'requirements': {
                'performance_critical': True,
                'complex_state': True,
                'experience_level': 'intermediate'
            },
            'preferences': {
                'framework': 'react',
                'typescript': True,
                'styling': 'tailwindcss'
            }
        },
        {
            'project_type': 'mobile-application',
            'requirements': {
                'cross_platform': True,
                'native_performance': True
            },
            'preferences': None
        },
        {
            'project_type': 'backend-api',
            'requirements': {
                'async_support': True,
                'auto_documentation': True
            },
            'preferences': {
                'framework': 'fastapi'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"프로젝트 타입: {test_case['project_type']}")
        
        result = test_agent.select_ui_stack(
            test_case['project_type'],
            test_case['requirements'],
            test_case['preferences']
        )
        
        print(f"추천 프레임워크: {result.recommended_stack.framework}")
        print(f"신뢰도: {result.confidence_score:.2f}")
        print(f"설치 명령어:")
        for cmd in result.setup_commands[:3]:
            print(f"  $ {cmd}")