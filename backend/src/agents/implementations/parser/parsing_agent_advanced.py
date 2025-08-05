# Task 4.3: Advanced Parsing Agent Implementation
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools import LambdaAgent, S3FileHandler, GitHubIntegration
from typing import Dict, List, Any, Optional
import ast
import asyncio
from dataclasses import dataclass

@dataclass
class CodebaseAnalysis:
    structure_map: Dict[str, Any]
    components: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    patterns: List[Dict[str, Any]]
    reusable_modules: List[Dict[str, Any]]
    metrics: Dict[str, float]
    suggestions: List[str]

class AdvancedParsingAgent:
    """고급 코드 파싱 및 분석 에이전트"""

    def __init__(self):
        self.agent = Agent(
            name="Advanced-Code-Parser",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Expert code analyst and architect",
            tools=[
                LambdaAgent("ast-parser-lambda"),
                LambdaAgent("dependency-analyzer-lambda"),
                LambdaAgent("security-scanner-lambda"),
                S3FileHandler(),
                GitHubIntegration()
            ],
            instructions=[
                "Parse codebases to understand structure and patterns",
                "Identify reusable components and modules",
                "Detect anti-patterns and code smells",
                "Map dependencies and relationships",
                "Extract API contracts and interfaces"
            ]
        )
        
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_mapper = DependencyMapper()
        self.pattern_detector = PatternDetector()

    async def parse_codebase(self, codebase_location: str) -> CodebaseAnalysis:
        """코드베이스 파싱 및 분석"""

        # 1. 코드베이스 검색
        codebase = await self._retrieve_codebase(codebase_location)
        
        # 2. 병렬 AST 분석
        ast_results = await self.ast_analyzer.analyze_parallel(
            files=codebase.files,
            languages=codebase.detected_languages,
            max_workers=10
        )
        
        # 3. 의존성 매핑
        dependencies = await self.dependency_mapper.map_dependencies(
            ast_results=ast_results,
            package_files=codebase.package_files
        )
        
        # 4. 패턴 감지
        patterns = await self.pattern_detector.detect_patterns(
            ast_results=ast_results,
            pattern_types=["design_patterns", "architectural_patterns", "anti_patterns"]
        )
        
        # 5. 종합 분석
        analysis_prompt = f"""
        코드베이스 분석 결과를 바탕으로 다음을 제공해주세요:
        
        1. 재사용 가능한 컴포넌트 식별
        2. 아키텍처 개선 제안
        3. 코드 품질 메트릭
        4. 리팩토링 우선순위
        
        AST 분석: {len(ast_results)} 파일
        의존성: {len(dependencies)} 관계
        패턴: {len(patterns)} 개 감지
        """
        
        comprehensive_analysis = await self.agent.arun(analysis_prompt)
        
        return CodebaseAnalysis(
            structure_map=await self._build_structure_map(ast_results),
            components=await self._identify_components(ast_results),
            dependencies=dependencies,
            patterns=patterns,
            reusable_modules=await self._find_reusable_modules(ast_results),
            metrics=await self._calculate_metrics(ast_results),
            suggestions=await self._parse_suggestions(comprehensive_analysis)
        )

    async def _retrieve_codebase(self, location: str) -> 'Codebase':
        """코드베이스 검색 및 로드"""
        if location.startswith('github://'):
            return await self._load_from_github(location)
        elif location.startswith('s3://'):
            return await self._load_from_s3(location)
        else:
            return await self._load_from_local(location)

class ASTAnalyzer:
    """AST 분석기"""
    
    async def analyze_parallel(
        self,
        files: List[str],
        languages: List[str],
        max_workers: int = 10
    ) -> Dict[str, Any]:
        """병렬 AST 분석"""
        
        semaphore = asyncio.Semaphore(max_workers)
        tasks = []
        
        for file_path in files:
            task = asyncio.create_task(
                self._analyze_single_file(file_path, semaphore)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 정리
        successful_results = {}
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                successful_results[files[i]] = result
        
        return successful_results

    async def _analyze_single_file(self, file_path: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """단일 파일 AST 분석"""
        
        async with semaphore:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 언어별 파싱
                if file_path.endswith('.py'):
                    return await self._parse_python(content, file_path)
                elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                    return await self._parse_javascript(content, file_path)
                elif file_path.endswith('.java'):
                    return await self._parse_java(content, file_path)
                else:
                    return await self._parse_generic(content, file_path)
                    
            except Exception as e:
                return {'error': str(e), 'file': file_path}

    async def _parse_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Python 코드 파싱"""
        
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'bases': [self._get_name(base) for base in node.bases]
                    })
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [self._get_name(dec) for dec in node.decorator_list]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(self._extract_import(node))
            
            return {
                'language': 'python',
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'complexity': await self._calculate_complexity(tree),
                'loc': len(content.split('\n'))
            }
            
        except SyntaxError as e:
            return {'error': f'Syntax error: {e}', 'file': file_path}

    def _get_name(self, node) -> str:
        """AST 노드에서 이름 추출"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)

class DependencyMapper:
    """의존성 매핑 시스템"""
    
    async def map_dependencies(
        self,
        ast_results: Dict[str, Any],
        package_files: List[str]
    ) -> Dict[str, List[str]]:
        """의존성 관계 매핑"""
        
        dependency_graph = {}
        
        # 1. 내부 의존성 분석
        for file_path, analysis in ast_results.items():
            if 'imports' in analysis:
                dependencies = []
                for import_info in analysis['imports']:
                    if self._is_internal_import(import_info, ast_results.keys()):
                        dependencies.append(import_info['module'])
                
                dependency_graph[file_path] = dependencies
        
        # 2. 외부 의존성 분석
        external_deps = await self._analyze_external_dependencies(package_files)
        dependency_graph['external'] = external_deps
        
        # 3. 순환 의존성 감지
        cycles = await self._detect_circular_dependencies(dependency_graph)
        if cycles:
            dependency_graph['circular_dependencies'] = cycles
        
        return dependency_graph

    def _is_internal_import(self, import_info: Dict[str, Any], file_paths: List[str]) -> bool:
        """내부 임포트 여부 확인"""
        module_name = import_info.get('module', '')
        
        # 상대 임포트는 내부 의존성
        if module_name.startswith('.'):
            return True
        
        # 프로젝트 내 모듈인지 확인
        for file_path in file_paths:
            if module_name.replace('.', '/') in file_path:
                return True
        
        return False

class PatternDetector:
    """디자인 패턴 감지기"""
    
    async def detect_patterns(
        self,
        ast_results: Dict[str, Any],
        pattern_types: List[str]
    ) -> List[Dict[str, Any]]:
        """패턴 감지"""
        
        detected_patterns = []
        
        for pattern_type in pattern_types:
            if pattern_type == "design_patterns":
                patterns = await self._detect_design_patterns(ast_results)
                detected_patterns.extend(patterns)
            elif pattern_type == "architectural_patterns":
                patterns = await self._detect_architectural_patterns(ast_results)
                detected_patterns.extend(patterns)
            elif pattern_type == "anti_patterns":
                patterns = await self._detect_anti_patterns(ast_results)
                detected_patterns.extend(patterns)
        
        return detected_patterns

    async def _detect_design_patterns(self, ast_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """디자인 패턴 감지"""
        
        patterns = []
        
        for file_path, analysis in ast_results.items():
            if 'classes' in analysis:
                for class_info in analysis['classes']:
                    # Singleton 패턴 감지
                    if self._is_singleton_pattern(class_info):
                        patterns.append({
                            'type': 'Singleton',
                            'file': file_path,
                            'class': class_info['name'],
                            'confidence': 0.8
                        })
                    
                    # Factory 패턴 감지
                    if self._is_factory_pattern(class_info):
                        patterns.append({
                            'type': 'Factory',
                            'file': file_path,
                            'class': class_info['name'],
                            'confidence': 0.7
                        })
        
        return patterns

    def _is_singleton_pattern(self, class_info: Dict[str, Any]) -> bool:
        """Singleton 패턴 여부 확인"""
        methods = class_info.get('methods', [])
        return ('__new__' in methods or 
                'getInstance' in methods or
                any('instance' in method.lower() for method in methods))

    def _is_factory_pattern(self, class_info: Dict[str, Any]) -> bool:
        """Factory 패턴 여부 확인"""
        class_name = class_info.get('name', '').lower()
        methods = class_info.get('methods', [])
        
        return ('factory' in class_name or
                any('create' in method.lower() for method in methods) or
                any('build' in method.lower() for method in methods))