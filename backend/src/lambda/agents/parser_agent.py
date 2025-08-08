"""
Parser Agent - Production Ready Implementation
프로젝트 구조를 분석하고 파일/폴더 구조를 설계

AWS Lambda에서 실행 (실행시간 < 20초)
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pathlib import Path

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


class FileType(Enum):
    """파일 타입 분류"""
    SOURCE = "source"
    CONFIG = "config"
    TEST = "test"
    ASSET = "asset"
    DOCUMENTATION = "documentation"
    SCRIPT = "script"
    DATA = "data"
    TEMPLATE = "template"


@dataclass
class FileNode:
    """파일 노드"""
    name: str
    type: FileType
    extension: Optional[str]
    size_estimate: int  # bytes
    description: str
    template_key: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'name': self.name,
            'type': self.type.value,
            'extension': self.extension,
            'size_estimate': self.size_estimate,
            'description': self.description,
            'template_key': self.template_key,
            'dependencies': self.dependencies
        }


@dataclass
class DirectoryNode:
    """디렉토리 노드"""
    name: str
    path: str
    description: str
    files: List[FileNode] = field(default_factory=list)
    subdirectories: Dict[str, 'DirectoryNode'] = field(default_factory=dict)
    
    def add_file(self, file: FileNode):
        """파일 추가"""
        self.files.append(file)
    
    def add_subdirectory(self, dir_node: 'DirectoryNode'):
        """서브디렉토리 추가"""
        self.subdirectories[dir_node.name] = dir_node
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'name': self.name,
            'path': self.path,
            'description': self.description,
            'files': [f.to_dict() for f in self.files],
            'subdirectories': {
                name: dir.to_dict() 
                for name, dir in self.subdirectories.items()
            }
        }


@dataclass
class ProjectStructure:
    """프로젝트 구조"""
    root_name: str
    framework: str
    project_type: str
    root: DirectoryNode
    total_files: int
    total_directories: int
    estimated_size: int  # bytes
    entry_points: List[str]
    build_outputs: List[str]
    ignored_paths: List[str]
    
    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'root_name': self.root_name,
            'framework': self.framework,
            'project_type': self.project_type,
            'structure': self.root.to_dict(),
            'statistics': {
                'total_files': self.total_files,
                'total_directories': self.total_directories,
                'estimated_size': self.estimated_size
            },
            'entry_points': self.entry_points,
            'build_outputs': self.build_outputs,
            'ignored_paths': self.ignored_paths
        }


@dataclass
class ParserResult:
    """Parser 결과"""
    project_structure: ProjectStructure
    file_mappings: Dict[str, str]  # 파일 경로 -> 템플릿 키 매핑
    directory_tree: str  # 시각적 트리 표현
    configuration_files: List[str]
    dependency_graph: Dict[str, List[str]]
    architecture_pattern: str
    conventions: Dict[str, Any]
    metadata: Dict[str, Any]


class ParserAgent:
    """Production-ready Parser Agent"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # 프레임워크별 구조 템플릿
        self._init_structure_templates()
        
        # 메트릭 초기화
        self.parsing_times = []
        
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
            # 기본 설정 반환
            return {
                'max_depth': 10,
                'max_files': 1000,
                'timeout_seconds': 20
            }
    
    def _init_structure_templates(self):
        """프레임워크별 구조 템플릿 초기화"""
        
        # React 프로젝트 구조
        self.react_structure = {
            'src': {
                'description': '소스 코드 디렉토리',
                'subdirs': {
                    'components': '재사용 가능한 React 컴포넌트',
                    'pages': '페이지 컴포넌트',
                    'hooks': '커스텀 React 훅',
                    'services': 'API 서비스 및 비즈니스 로직',
                    'utils': '유틸리티 함수',
                    'styles': '글로벌 스타일 및 CSS',
                    'assets': '이미지, 폰트 등 정적 리소스',
                    'store': '상태 관리 (Redux/Context)',
                    'types': 'TypeScript 타입 정의'
                },
                'files': {
                    'App.tsx': 'Root 애플리케이션 컴포넌트',
                    'index.tsx': '애플리케이션 진입점',
                    'setupTests.ts': '테스트 설정'
                }
            },
            'public': {
                'description': '정적 파일 디렉토리',
                'files': {
                    'index.html': 'HTML 템플릿',
                    'manifest.json': 'PWA 매니페스트',
                    'robots.txt': '검색 엔진 크롤러 설정'
                }
            },
            'config': {
                'description': '설정 파일',
                'files': {
                    'webpack.config.js': 'Webpack 설정',
                    'jest.config.js': 'Jest 테스트 설정'
                }
            }
        }
        
        # Vue 프로젝트 구조
        self.vue_structure = {
            'src': {
                'description': '소스 코드 디렉토리',
                'subdirs': {
                    'components': 'Vue 컴포넌트',
                    'views': '페이지 뷰 컴포넌트',
                    'router': '라우팅 설정',
                    'store': 'Vuex/Pinia 상태 관리',
                    'composables': 'Composition API 함수',
                    'assets': '정적 리소스',
                    'styles': '스타일 파일',
                    'utils': '유틸리티 함수',
                    'api': 'API 통신 모듈'
                },
                'files': {
                    'App.vue': 'Root Vue 컴포넌트',
                    'main.ts': '애플리케이션 진입점'
                }
            }
        }
        
        # FastAPI 프로젝트 구조
        self.fastapi_structure = {
            'app': {
                'description': '애플리케이션 코드',
                'subdirs': {
                    'api': 'API 엔드포인트',
                    'core': '핵심 설정 및 보안',
                    'models': '데이터베이스 모델',
                    'schemas': 'Pydantic 스키마',
                    'services': '비즈니스 로직',
                    'db': '데이터베이스 연결',
                    'dependencies': 'FastAPI 의존성',
                    'middleware': '미들웨어',
                    'utils': '유틸리티 함수'
                },
                'files': {
                    'main.py': 'FastAPI 애플리케이션',
                    '__init__.py': '패키지 초기화'
                }
            },
            'tests': {
                'description': '테스트 코드',
                'subdirs': {
                    'unit': '단위 테스트',
                    'integration': '통합 테스트',
                    'e2e': 'E2E 테스트'
                }
            },
            'alembic': {
                'description': '데이터베이스 마이그레이션',
                'files': {
                    'alembic.ini': 'Alembic 설정'
                }
            }
        }
        
        # Next.js 프로젝트 구조
        self.nextjs_structure = {
            'app': {
                'description': 'App Router 디렉토리',
                'subdirs': {
                    'api': 'API 라우트',
                    'components': '공유 컴포넌트',
                    '(auth)': '인증 관련 라우트 그룹',
                    '(marketing)': '마케팅 페이지 그룹'
                },
                'files': {
                    'layout.tsx': 'Root 레이아웃',
                    'page.tsx': '홈페이지',
                    'loading.tsx': '로딩 UI',
                    'error.tsx': '에러 UI',
                    'not-found.tsx': '404 페이지'
                }
            },
            'components': {
                'description': '재사용 가능한 컴포넌트',
                'subdirs': {
                    'ui': 'UI 컴포넌트',
                    'forms': '폼 컴포넌트',
                    'layouts': '레이아웃 컴포넌트'
                }
            },
            'lib': {
                'description': '라이브러리 및 유틸리티',
                'files': {
                    'db.ts': '데이터베이스 연결',
                    'auth.ts': '인증 유틸리티'
                }
            }
        }
        
        # Mobile (React Native) 프로젝트 구조
        self.react_native_structure = {
            'src': {
                'description': '소스 코드',
                'subdirs': {
                    'screens': '화면 컴포넌트',
                    'components': '재사용 컴포넌트',
                    'navigation': '네비게이션 설정',
                    'services': 'API 서비스',
                    'store': '상태 관리',
                    'utils': '유틸리티',
                    'assets': '이미지 및 리소스',
                    'styles': '스타일 정의'
                },
                'files': {
                    'App.tsx': 'Root 컴포넌트'
                }
            },
            'android': {
                'description': 'Android 네이티브 코드'
            },
            'ios': {
                'description': 'iOS 네이티브 코드'
            }
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    def parse_project_structure(
        self,
        project_type: str,
        framework: str,
        requirements: Dict[str, Any],
        ui_stack: Optional[Dict[str, Any]] = None
    ) -> ParserResult:
        """
        프로젝트 구조 분석 및 생성
        
        Args:
            project_type: 프로젝트 타입
            framework: 선택된 프레임워크
            requirements: 프로젝트 요구사항
            ui_stack: UI 스택 정보
            
        Returns:
            ParserResult: 분석된 프로젝트 구조
        """
        start_time = time.time()
        
        try:
            # 입력 검증
            self._validate_input(project_type, framework)
            
            # 기본 구조 템플릿 선택
            base_structure = self._select_base_structure(framework)
            
            # 프로젝트 루트 생성
            root_name = requirements.get('project_name', 'my-app')
            root = DirectoryNode(
                name=root_name,
                path='/',
                description=f'{framework} 프로젝트 루트'
            )
            
            # 구조 생성
            self._build_structure(root, base_structure, requirements, ui_stack)
            
            # 설정 파일 추가
            config_files = self._add_configuration_files(root, framework, ui_stack)
            
            # 테스트 구조 추가
            self._add_test_structure(root, framework)
            
            # 통계 계산
            stats = self._calculate_statistics(root)
            
            # 프로젝트 구조 객체 생성
            project_structure = ProjectStructure(
                root_name=root_name,
                framework=framework,
                project_type=project_type,
                root=root,
                total_files=stats['total_files'],
                total_directories=stats['total_directories'],
                estimated_size=stats['estimated_size'],
                entry_points=self._identify_entry_points(framework),
                build_outputs=self._identify_build_outputs(framework),
                ignored_paths=self._get_ignored_paths(framework)
            )
            
            # 파일 매핑 생성
            file_mappings = self._create_file_mappings(root)
            
            # 디렉토리 트리 생성
            directory_tree = self._generate_directory_tree(root)
            
            # 의존성 그래프 생성
            dependency_graph = self._analyze_dependencies(root, framework)
            
            # 아키텍처 패턴 식별
            architecture_pattern = self._identify_architecture_pattern(
                project_structure,
                requirements
            )
            
            # 코딩 컨벤션 설정
            conventions = self._set_conventions(framework, ui_stack)
            
            # 메타데이터 생성
            metadata = self._generate_metadata(start_time)
            
            # 결과 생성
            result = ParserResult(
                project_structure=project_structure,
                file_mappings=file_mappings,
                directory_tree=directory_tree,
                configuration_files=config_files,
                dependency_graph=dependency_graph,
                architecture_pattern=architecture_pattern,
                conventions=conventions,
                metadata=metadata
            )
            
            # 처리 시간 기록
            processing_time = time.time() - start_time
            self.parsing_times.append(processing_time)
            metrics.add_metric(
                name="ParsingTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            
            logger.info(
                f"Successfully parsed project structure",
                extra={
                    "framework": framework,
                    "total_files": stats['total_files'],
                    "processing_time": processing_time
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing project structure: {e}")
            metrics.add_metric(name="ParsingError", unit=MetricUnit.Count, value=1)
            raise
    
    def _validate_input(self, project_type: str, framework: str):
        """입력 검증"""
        if not project_type:
            raise ValueError("프로젝트 타입이 필요합니다")
        
        if not framework:
            raise ValueError("프레임워크가 필요합니다")
        
        valid_frameworks = [
            'react', 'vue', 'angular', 'nextjs', 'svelte',
            'fastapi', 'express', 'django', 'flask',
            'react-native', 'flutter', 'ionic'
        ]
        
        if framework.lower() not in valid_frameworks:
            raise ValueError(f"지원하지 않는 프레임워크: {framework}")
    
    def _select_base_structure(self, framework: str) -> Dict:
        """기본 구조 템플릿 선택"""
        framework_lower = framework.lower()
        
        if framework_lower == 'react':
            return self.react_structure
        elif framework_lower == 'vue':
            return self.vue_structure
        elif framework_lower == 'fastapi':
            return self.fastapi_structure
        elif framework_lower == 'nextjs':
            return self.nextjs_structure
        elif framework_lower == 'react-native':
            return self.react_native_structure
        else:
            # 기본 구조
            return {
                'src': {
                    'description': '소스 코드',
                    'subdirs': {},
                    'files': {}
                }
            }
    
    def _build_structure(
        self,
        parent: DirectoryNode,
        template: Dict,
        requirements: Dict[str, Any],
        ui_stack: Optional[Dict[str, Any]]
    ):
        """구조 빌드"""
        for dir_name, dir_info in template.items():
            if isinstance(dir_info, dict):
                # 디렉토리 생성
                dir_node = DirectoryNode(
                    name=dir_name,
                    path=f"{parent.path}/{dir_name}",
                    description=dir_info.get('description', '')
                )
                
                # 서브디렉토리 처리
                if 'subdirs' in dir_info:
                    for subdir_name, subdir_desc in dir_info['subdirs'].items():
                        subdir_node = DirectoryNode(
                            name=subdir_name,
                            path=f"{dir_node.path}/{subdir_name}",
                            description=subdir_desc
                        )
                        dir_node.add_subdirectory(subdir_node)
                        
                        # 기본 파일 추가
                        self._add_default_files(subdir_node, subdir_name, ui_stack)
                
                # 파일 처리
                if 'files' in dir_info:
                    for file_name, file_desc in dir_info['files'].items():
                        file_node = FileNode(
                            name=file_name,
                            type=self._determine_file_type(file_name),
                            extension=Path(file_name).suffix,
                            size_estimate=1000,  # 기본 1KB
                            description=file_desc
                        )
                        dir_node.add_file(file_node)
                
                parent.add_subdirectory(dir_node)
    
    def _add_default_files(
        self,
        dir_node: DirectoryNode,
        dir_type: str,
        ui_stack: Optional[Dict[str, Any]]
    ):
        """디렉토리 타입별 기본 파일 추가"""
        typescript = ui_stack and ui_stack.get('typescript', False)
        extension = '.tsx' if typescript and dir_type in ['components', 'pages', 'screens'] else '.jsx'
        
        if dir_type == 'components':
            # 기본 컴포넌트
            files = [
                ('Button' + extension, 'Button 컴포넌트'),
                ('Input' + extension, 'Input 컴포넌트'),
                ('Card' + extension, 'Card 컴포넌트'),
                ('index.ts', '컴포넌트 export')
            ]
            for name, desc in files:
                dir_node.add_file(FileNode(
                    name=name,
                    type=FileType.SOURCE,
                    extension=Path(name).suffix,
                    size_estimate=2000,
                    description=desc
                ))
        
        elif dir_type == 'services':
            # API 서비스
            files = [
                ('api.ts', 'API 클라이언트'),
                ('auth.service.ts', '인증 서비스'),
                ('user.service.ts', '사용자 서비스')
            ]
            for name, desc in files:
                dir_node.add_file(FileNode(
                    name=name,
                    type=FileType.SOURCE,
                    extension='.ts',
                    size_estimate=3000,
                    description=desc
                ))
        
        elif dir_type == 'utils':
            # 유틸리티
            files = [
                ('constants.ts', '상수 정의'),
                ('helpers.ts', '헬퍼 함수'),
                ('validators.ts', '검증 함수')
            ]
            for name, desc in files:
                dir_node.add_file(FileNode(
                    name=name,
                    type=FileType.SOURCE,
                    extension='.ts',
                    size_estimate=1500,
                    description=desc
                ))
    
    def _add_configuration_files(
        self,
        root: DirectoryNode,
        framework: str,
        ui_stack: Optional[Dict[str, Any]]
    ) -> List[str]:
        """설정 파일 추가"""
        config_files = []
        
        # 공통 설정 파일
        common_configs = [
            ('package.json', 'NPM 패키지 설정', 2000),
            ('.gitignore', 'Git 무시 파일', 500),
            ('README.md', '프로젝트 문서', 3000),
            ('.env.example', '환경변수 예제', 500)
        ]
        
        for name, desc, size in common_configs:
            root.add_file(FileNode(
                name=name,
                type=FileType.CONFIG,
                extension=Path(name).suffix if '.' in name else None,
                size_estimate=size,
                description=desc
            ))
            config_files.append(name)
        
        # TypeScript 설정
        if ui_stack and ui_stack.get('typescript'):
            root.add_file(FileNode(
                name='tsconfig.json',
                type=FileType.CONFIG,
                extension='.json',
                size_estimate=1500,
                description='TypeScript 설정'
            ))
            config_files.append('tsconfig.json')
        
        # 프레임워크별 설정
        if framework == 'react':
            if ui_stack and ui_stack.get('build_tool') == 'vite':
                root.add_file(FileNode(
                    name='vite.config.js',
                    type=FileType.CONFIG,
                    extension='.js',
                    size_estimate=1000,
                    description='Vite 빌드 설정'
                ))
                config_files.append('vite.config.js')
        
        elif framework == 'nextjs':
            root.add_file(FileNode(
                name='next.config.js',
                type=FileType.CONFIG,
                extension='.js',
                size_estimate=1000,
                description='Next.js 설정'
            ))
            config_files.append('next.config.js')
        
        elif framework == 'fastapi':
            root.add_file(FileNode(
                name='pyproject.toml',
                type=FileType.CONFIG,
                extension='.toml',
                size_estimate=1500,
                description='Python 프로젝트 설정'
            ))
            root.add_file(FileNode(
                name='requirements.txt',
                type=FileType.CONFIG,
                extension='.txt',
                size_estimate=500,
                description='Python 의존성'
            ))
            config_files.extend(['pyproject.toml', 'requirements.txt'])
        
        # CSS 프레임워크 설정
        if ui_stack and ui_stack.get('css_framework') == 'tailwindcss':
            root.add_file(FileNode(
                name='tailwind.config.js',
                type=FileType.CONFIG,
                extension='.js',
                size_estimate=1000,
                description='Tailwind CSS 설정'
            ))
            root.add_file(FileNode(
                name='postcss.config.js',
                type=FileType.CONFIG,
                extension='.js',
                size_estimate=500,
                description='PostCSS 설정'
            ))
            config_files.extend(['tailwind.config.js', 'postcss.config.js'])
        
        return config_files
    
    def _add_test_structure(self, root: DirectoryNode, framework: str):
        """테스트 구조 추가"""
        if framework in ['react', 'vue', 'angular', 'nextjs']:
            # JavaScript/TypeScript 테스트
            test_dir = DirectoryNode(
                name='tests',
                path='/tests',
                description='테스트 코드'
            )
            
            # 테스트 타입별 디렉토리
            for test_type in ['unit', 'integration', 'e2e']:
                subdir = DirectoryNode(
                    name=test_type,
                    path=f'/tests/{test_type}',
                    description=f'{test_type} 테스트'
                )
                test_dir.add_subdirectory(subdir)
            
            # 테스트 설정 파일
            test_dir.add_file(FileNode(
                name='setup.js',
                type=FileType.TEST,
                extension='.js',
                size_estimate=1000,
                description='테스트 설정'
            ))
            
            root.add_subdirectory(test_dir)
            
            # Jest 설정
            root.add_file(FileNode(
                name='jest.config.js',
                type=FileType.CONFIG,
                extension='.js',
                size_estimate=1000,
                description='Jest 설정'
            ))
        
        elif framework == 'fastapi':
            # Python 테스트는 이미 구조에 포함됨
            pass
    
    def _determine_file_type(self, filename: str) -> FileType:
        """파일 타입 결정"""
        extension = Path(filename).suffix.lower()
        name_lower = filename.lower()
        
        # 확장자 기반 분류
        if extension in ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go']:
            return FileType.SOURCE
        elif extension in ['.json', '.yaml', '.yml', '.toml', '.ini', '.env']:
            return FileType.CONFIG
        elif extension in ['.test.js', '.spec.js', '.test.ts', '.spec.ts']:
            return FileType.TEST
        elif extension in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']:
            return FileType.ASSET
        elif extension in ['.md', '.txt', '.rst']:
            return FileType.DOCUMENTATION
        elif extension in ['.sh', '.bat', '.ps1']:
            return FileType.SCRIPT
        elif extension in ['.csv', '.json', '.xml']:
            return FileType.DATA
        elif extension in ['.html', '.ejs', '.pug', '.hbs']:
            return FileType.TEMPLATE
        
        # 이름 기반 분류
        if 'test' in name_lower or 'spec' in name_lower:
            return FileType.TEST
        elif 'config' in name_lower or 'setup' in name_lower:
            return FileType.CONFIG
        
        return FileType.SOURCE
    
    def _calculate_statistics(self, root: DirectoryNode) -> Dict[str, int]:
        """통계 계산"""
        total_files = 0
        total_directories = 0
        estimated_size = 0
        
        def traverse(node: DirectoryNode):
            nonlocal total_files, total_directories, estimated_size
            
            total_directories += 1
            total_files += len(node.files)
            
            for file in node.files:
                estimated_size += file.size_estimate
            
            for subdir in node.subdirectories.values():
                traverse(subdir)
        
        traverse(root)
        
        return {
            'total_files': total_files,
            'total_directories': total_directories - 1,  # 루트 제외
            'estimated_size': estimated_size
        }
    
    def _identify_entry_points(self, framework: str) -> List[str]:
        """진입점 식별"""
        entry_points = {
            'react': ['src/index.tsx', 'src/index.jsx'],
            'vue': ['src/main.ts', 'src/main.js'],
            'angular': ['src/main.ts'],
            'nextjs': ['app/layout.tsx', 'pages/_app.tsx'],
            'fastapi': ['app/main.py'],
            'express': ['src/index.js', 'src/app.js'],
            'react-native': ['index.js', 'App.tsx']
        }
        
        return entry_points.get(framework.lower(), ['src/index.js'])
    
    def _identify_build_outputs(self, framework: str) -> List[str]:
        """빌드 출력 경로 식별"""
        build_outputs = {
            'react': ['build/', 'dist/'],
            'vue': ['dist/'],
            'angular': ['dist/'],
            'nextjs': ['.next/', 'out/'],
            'fastapi': ['__pycache__/', '*.pyc'],
            'express': ['dist/', 'build/'],
            'react-native': ['android/app/build/', 'ios/build/']
        }
        
        return build_outputs.get(framework.lower(), ['dist/'])
    
    def _get_ignored_paths(self, framework: str) -> List[str]:
        """무시할 경로 목록"""
        common_ignores = [
            'node_modules/',
            '.git/',
            '.env',
            '*.log',
            '.DS_Store',
            'coverage/',
            '.vscode/',
            '.idea/'
        ]
        
        framework_specific = {
            'react': ['build/', '.cache/'],
            'nextjs': ['.next/', 'out/'],
            'fastapi': ['__pycache__/', '*.pyc', '.pytest_cache/'],
            'react-native': ['.expo/', '.gradle/']
        }
        
        ignores = common_ignores.copy()
        if framework.lower() in framework_specific:
            ignores.extend(framework_specific[framework.lower()])
        
        return ignores
    
    def _create_file_mappings(self, root: DirectoryNode) -> Dict[str, str]:
        """파일 매핑 생성"""
        mappings = {}
        
        def traverse(node: DirectoryNode):
            for file in node.files:
                file_path = f"{node.path}/{file.name}"
                template_key = file.template_key or f"template_{file.type.value}_{file.extension}"
                mappings[file_path] = template_key
            
            for subdir in node.subdirectories.values():
                traverse(subdir)
        
        traverse(root)
        return mappings
    
    def _generate_directory_tree(self, root: DirectoryNode, indent: str = "") -> str:
        """디렉토리 트리 생성"""
        lines = []
        
        def traverse(node: DirectoryNode, prefix: str = "", is_last: bool = True):
            # 디렉토리 이름
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node.name}/")
            
            # 하위 prefix 계산
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension
            
            # 파일 출력
            for i, file in enumerate(node.files):
                is_last_file = (i == len(node.files) - 1) and len(node.subdirectories) == 0
                file_connector = "└── " if is_last_file else "├── "
                lines.append(f"{new_prefix}{file_connector}{file.name}")
            
            # 서브디렉토리 출력
            subdirs = list(node.subdirectories.values())
            for i, subdir in enumerate(subdirs):
                is_last_subdir = (i == len(subdirs) - 1)
                traverse(subdir, new_prefix, is_last_subdir)
        
        lines.append(f"{root.name}/")
        for i, subdir in enumerate(root.subdirectories.values()):
            is_last = (i == len(root.subdirectories) - 1)
            traverse(subdir, "", is_last)
        
        return "\n".join(lines)
    
    def _analyze_dependencies(self, root: DirectoryNode, framework: str) -> Dict[str, List[str]]:
        """의존성 분석"""
        dependency_graph = {}
        
        # 프레임워크별 기본 의존성
        if framework == 'react':
            dependency_graph['src/App.tsx'] = ['src/components/index.ts', 'src/hooks/index.ts']
            dependency_graph['src/index.tsx'] = ['src/App.tsx']
        elif framework == 'vue':
            dependency_graph['src/App.vue'] = ['src/components/index.ts', 'src/router/index.ts']
            dependency_graph['src/main.ts'] = ['src/App.vue', 'src/store/index.ts']
        elif framework == 'fastapi':
            dependency_graph['app/main.py'] = ['app/api/index.py', 'app/core/config.py']
            dependency_graph['app/api/index.py'] = ['app/services/index.py']
        
        return dependency_graph
    
    def _identify_architecture_pattern(
        self,
        structure: ProjectStructure,
        requirements: Dict[str, Any]
    ) -> str:
        """아키텍처 패턴 식별"""
        # 프레임워크와 구조를 기반으로 패턴 식별
        if structure.framework in ['react', 'vue', 'angular']:
            if 'store' in [d for d in structure.root.subdirectories]:
                return "Component-based with State Management"
            else:
                return "Component-based Architecture"
        elif structure.framework == 'nextjs':
            return "File-based Routing with SSR/SSG"
        elif structure.framework == 'fastapi':
            return "Layered Architecture (API-Service-Repository)"
        elif structure.framework == 'react-native':
            return "Mobile Component Architecture"
        else:
            return "Modular Architecture"
    
    def _set_conventions(self, framework: str, ui_stack: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """코딩 컨벤션 설정"""
        conventions = {
            'naming': {
                'components': 'PascalCase',
                'files': 'camelCase',
                'constants': 'UPPER_SNAKE_CASE',
                'css_classes': 'kebab-case'
            },
            'structure': {
                'max_file_lines': 300,
                'max_component_lines': 200,
                'index_exports': True
            }
        }
        
        # TypeScript 사용 시
        if ui_stack and ui_stack.get('typescript'):
            conventions['typescript'] = {
                'strict': True,
                'no_any': True,
                'interfaces_over_types': True
            }
        
        # 프레임워크별 컨벤션
        if framework == 'react':
            conventions['react'] = {
                'functional_components': True,
                'hooks_prefix': 'use',
                'prop_types': False if ui_stack and ui_stack.get('typescript') else True
            }
        elif framework == 'vue':
            conventions['vue'] = {
                'composition_api': True,
                'script_setup': True,
                'style_scoped': True
            }
        elif framework == 'fastapi':
            conventions['python'] = {
                'pep8': True,
                'type_hints': True,
                'docstrings': 'Google Style'
            }
        
        return conventions
    
    def _generate_metadata(self, start_time: float) -> Dict[str, Any]:
        """메타데이터 생성"""
        return {
            'agent_name': 'parser-agent',
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
        framework = body.get('framework', '')
        requirements = body.get('requirements', {})
        ui_stack = body.get('ui_stack')
        
        # Agent 실행
        agent = ParserAgent()
        result = agent.parse_project_structure(
            project_type,
            framework,
            requirements,
            ui_stack
        )
        
        # 응답 구성
        response_body = {
            'project_structure': result.project_structure.to_dict(),
            'file_mappings': result.file_mappings,
            'directory_tree': result.directory_tree,
            'configuration_files': result.configuration_files,
            'dependency_graph': result.dependency_graph,
            'architecture_pattern': result.architecture_pattern,
            'conventions': result.conventions,
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
    test_agent = ParserAgent('development')
    
    test_cases = [
        {
            'project_type': 'web-application',
            'framework': 'react',
            'requirements': {
                'project_name': 'todo-app',
                'features': ['authentication', 'crud', 'realtime']
            },
            'ui_stack': {
                'typescript': True,
                'css_framework': 'tailwindcss',
                'state_management': 'redux-toolkit',
                'build_tool': 'vite'
            }
        },
        {
            'project_type': 'backend-api',
            'framework': 'fastapi',
            'requirements': {
                'project_name': 'api-service',
                'database': 'postgresql'
            },
            'ui_stack': None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"프레임워크: {test_case['framework']}")
        
        result = test_agent.parse_project_structure(
            test_case['project_type'],
            test_case['framework'],
            test_case['requirements'],
            test_case['ui_stack']
        )
        
        print(f"총 파일: {result.project_structure.total_files}")
        print(f"총 디렉토리: {result.project_structure.total_directories}")
        print(f"아키텍처 패턴: {result.architecture_pattern}")
        print(f"\n디렉토리 구조:")
        print(result.directory_tree[:500] + "..." if len(result.directory_tree) > 500 else result.directory_tree)