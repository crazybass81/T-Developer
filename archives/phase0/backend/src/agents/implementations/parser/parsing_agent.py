"""
Parsing Agent - Code analysis and parsing system
Analyzes codebases to understand structure, patterns, and dependencies
"""

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import ast
import re
import os
import json
import asyncio
from pathlib import Path

@dataclass
class CodeMetrics:
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    technical_debt_ratio: float
    test_coverage: float
    code_smells: List[str]

@dataclass
class ParsedComponent:
    name: str
    type: str
    file_path: str
    dependencies: List[str]
    exports: List[str]
    complexity: int
    reusability_score: float
    patterns: List[str]

class ASTAnalyzer:
    """Abstract Syntax Tree 분석기"""
    
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'typescript', 'java']
        
    async def analyze_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """파일 AST 분석"""
        
        if language == 'python':
            return await self._analyze_python_ast(file_path)
        elif language in ['javascript', 'typescript']:
            return await self._analyze_js_ast(file_path)
        elif language == 'java':
            return await self._analyze_java_ast(file_path)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    async def _analyze_python_ast(self, file_path: str) -> Dict[str, Any]:
        """Python AST 분석"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
            
            analysis = {
                'classes': [],
                'functions': [],
                'imports': [],
                'variables': [],
                'complexity': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'line': node.lineno
                    })
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'line': node.lineno,
                        'complexity': self._calculate_complexity(node)
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f"{module}.{alias.name}")
            
            return analysis
            
        except SyntaxError as e:
            return {'error': f"Syntax error: {e}"}
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """순환 복잡도 계산"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class DependencyMapper:
    """의존성 매핑 시스템"""
    
    def __init__(self):
        self.dependency_graph = {}
        
    async def map_dependencies(self, codebase_path: str) -> Dict[str, Any]:
        """코드베이스 의존성 매핑"""
        
        dependency_map = {
            'internal_dependencies': {},
            'external_dependencies': set(),
            'circular_dependencies': [],
            'dependency_graph': {}
        }
        
        # 모든 파일 스캔
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java')):
                    file_path = os.path.join(root, file)
                    deps = await self._extract_file_dependencies(file_path)
                    
                    relative_path = os.path.relpath(file_path, codebase_path)
                    dependency_map['internal_dependencies'][relative_path] = deps['internal']
                    dependency_map['external_dependencies'].update(deps['external'])
        
        # 순환 의존성 검사
        circular = await self._detect_circular_dependencies(
            dependency_map['internal_dependencies']
        )
        dependency_map['circular_dependencies'] = circular
        
        return dependency_map
    
    async def _extract_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """파일별 의존성 추출"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        internal_deps = []
        external_deps = []
        
        # Python imports
        if file_path.endswith('.py'):
            import_pattern = r'(?:from\s+(\S+)\s+import|import\s+(\S+))'
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                module = match[0] or match[1]
                if module.startswith('.') or '/' in module:
                    internal_deps.append(module)
                else:
                    external_deps.append(module)
        
        # JavaScript/TypeScript imports
        elif file_path.endswith(('.js', '.ts')):
            import_pattern = r'(?:import.*from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))'
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                module = match[0] or match[1]
                if module.startswith('./') or module.startswith('../'):
                    internal_deps.append(module)
                else:
                    external_deps.append(module)
        
        return {
            'internal': internal_deps,
            'external': external_deps
        }
    
    async def _detect_circular_dependencies(self, deps: Dict[str, List[str]]) -> List[List[str]]:
        """순환 의존성 검출"""
        
        def dfs(node, path, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in deps.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, path + [neighbor], visited, rec_stack)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # 순환 발견
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        visited = set()
        cycles = []
        
        for node in deps:
            if node not in visited:
                cycle = dfs(node, [node], visited, set())
                if cycle:
                    cycles.append(cycle)
        
        return cycles

class PatternDetector:
    """코드 패턴 감지기"""
    
    def __init__(self):
        self.patterns = {
            'singleton': self._detect_singleton,
            'factory': self._detect_factory,
            'observer': self._detect_observer,
            'mvc': self._detect_mvc,
            'repository': self._detect_repository
        }
    
    async def detect_patterns(self, codebase_path: str) -> Dict[str, List[Dict]]:
        """디자인 패턴 감지"""
        
        detected_patterns = {}
        
        for pattern_name, detector in self.patterns.items():
            patterns = await detector(codebase_path)
            if patterns:
                detected_patterns[pattern_name] = patterns
        
        return detected_patterns
    
    async def _detect_singleton(self, codebase_path: str) -> List[Dict]:
        """싱글톤 패턴 감지"""
        
        singletons = []
        
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 싱글톤 패턴 검사
                    if re.search(r'__new__.*cls\._instance', content, re.DOTALL):
                        singletons.append({
                            'file': file_path,
                            'type': 'classic_singleton',
                            'confidence': 0.9
                        })
        
        return singletons
    
    async def _detect_factory(self, codebase_path: str) -> List[Dict]:
        """팩토리 패턴 감지"""
        
        factories = []
        
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 팩토리 메서드 패턴
                    if re.search(r'def\s+create_\w+|def\s+make_\w+', content):
                        factories.append({
                            'file': file_path,
                            'type': 'factory_method',
                            'confidence': 0.7
                        })
        
        return factories
    
    async def _detect_observer(self, codebase_path: str) -> List[Dict]:
        """옵저버 패턴 감지"""
        return []
    
    async def _detect_mvc(self, codebase_path: str) -> List[Dict]:
        """MVC 패턴 감지"""
        return []
    
    async def _detect_repository(self, codebase_path: str) -> List[Dict]:
        """리포지토리 패턴 감지"""
        return []

class ParsingAgent:
    """코드 파싱 및 분석 에이전트"""
    
    def __init__(self):
        self.agent = Agent(
            name="Code-Parser",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Expert code analyst and architecture reviewer",
            instructions=[
                "Analyze code structure and identify patterns",
                "Extract reusable components and modules",
                "Detect code smells and anti-patterns",
                "Generate comprehensive analysis reports"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-parsing-memory"
            ),
            temperature=0.2
        )
        
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_mapper = DependencyMapper()
        self.pattern_detector = PatternDetector()
    
    async def parse_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """코드베이스 종합 분석"""
        
        analysis_result = {
            'summary': {},
            'structure': {},
            'dependencies': {},
            'patterns': {},
            'metrics': {},
            'recommendations': []
        }
        
        # 1. 코드베이스 구조 분석
        structure = await self._analyze_structure(codebase_path)
        analysis_result['structure'] = structure
        
        # 2. 의존성 매핑
        dependencies = await self.dependency_mapper.map_dependencies(codebase_path)
        analysis_result['dependencies'] = dependencies
        
        # 3. 패턴 감지
        patterns = await self.pattern_detector.detect_patterns(codebase_path)
        analysis_result['patterns'] = patterns
        
        # 4. 코드 메트릭 계산
        metrics = await self._calculate_metrics(codebase_path)
        analysis_result['metrics'] = metrics
        
        # 5. AI 기반 분석
        ai_analysis = await self._ai_analysis(analysis_result)
        analysis_result['ai_insights'] = ai_analysis
        
        # 6. 개선 권장사항
        recommendations = await self._generate_recommendations(analysis_result)
        analysis_result['recommendations'] = recommendations
        
        return analysis_result
    
    async def _analyze_structure(self, codebase_path: str) -> Dict[str, Any]:
        """코드베이스 구조 분석"""
        
        structure = {
            'files': {},
            'directories': {},
            'languages': {},
            'total_files': 0,
            'total_lines': 0
        }
        
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, codebase_path)
                
                # 파일 확장자별 분류
                ext = os.path.splitext(file)[1]
                if ext not in structure['languages']:
                    structure['languages'][ext] = 0
                structure['languages'][ext] += 1
                
                # 파일 분석
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                    
                    structure['files'][relative_path] = {
                        'lines': lines,
                        'size': os.path.getsize(file_path),
                        'extension': ext
                    }
                    
                    structure['total_lines'] += lines
                    structure['total_files'] += 1
                    
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return structure
    
    async def _calculate_metrics(self, codebase_path: str) -> CodeMetrics:
        """코드 메트릭 계산"""
        
        total_complexity = 0
        total_files = 0
        code_smells = []
        
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        analysis = await self.ast_analyzer.analyze_file(file_path, 'python')
                        
                        if 'functions' in analysis:
                            for func in analysis['functions']:
                                total_complexity += func.get('complexity', 1)
                                
                                # 코드 스멜 검사
                                if func.get('complexity', 1) > 10:
                                    code_smells.append(f"High complexity function: {func['name']}")
                        
                        total_files += 1
                        
                    except Exception:
                        continue
        
        avg_complexity = total_complexity / max(total_files, 1)
        
        return CodeMetrics(
            lines_of_code=0,  # 실제 구현에서 계산
            cyclomatic_complexity=avg_complexity,
            maintainability_index=85.0 - (avg_complexity * 2),
            technical_debt_ratio=len(code_smells) / max(total_files, 1),
            test_coverage=0.0,  # 실제 구현에서 계산
            code_smells=code_smells
        )
    
    async def _ai_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI 기반 코드 분석"""
        
        analysis_prompt = f"""
        다음 코드베이스 분석 결과를 검토하고 인사이트를 제공해주세요:
        
        구조: {json.dumps(analysis_data['structure'], indent=2)}
        의존성: {json.dumps(analysis_data['dependencies'], indent=2)}
        패턴: {json.dumps(analysis_data['patterns'], indent=2)}
        
        다음 관점에서 분석해주세요:
        1. 아키텍처 품질
        2. 코드 재사용성
        3. 유지보수성
        4. 확장성
        5. 보안 고려사항
        """
        
        ai_response = await self.agent.arun(analysis_prompt)
        
        return {
            'architecture_quality': ai_response.get('architecture_quality', 'Good'),
            'reusability_score': ai_response.get('reusability_score', 0.7),
            'maintainability': ai_response.get('maintainability', 'High'),
            'scalability': ai_response.get('scalability', 'Good'),
            'security_concerns': ai_response.get('security_concerns', []),
            'insights': ai_response.content
        }
    
    async def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """개선 권장사항 생성"""
        
        recommendations = []
        
        # 순환 의존성 해결
        if analysis_data['dependencies'].get('circular_dependencies'):
            recommendations.append({
                'type': 'architecture',
                'priority': 'high',
                'title': 'Resolve Circular Dependencies',
                'description': 'Found circular dependencies that should be resolved',
                'affected_files': analysis_data['dependencies']['circular_dependencies']
            })
        
        # 복잡도 개선
        metrics = analysis_data.get('metrics', {})
        if hasattr(metrics, 'cyclomatic_complexity') and metrics.cyclomatic_complexity > 10:
            recommendations.append({
                'type': 'code_quality',
                'priority': 'medium',
                'title': 'Reduce Code Complexity',
                'description': 'High cyclomatic complexity detected',
                'suggestion': 'Consider breaking down complex functions'
            })
        
        # 패턴 개선
        if not analysis_data.get('patterns'):
            recommendations.append({
                'type': 'design',
                'priority': 'low',
                'title': 'Consider Design Patterns',
                'description': 'No clear design patterns detected',
                'suggestion': 'Consider implementing appropriate design patterns'
            })
        
        return recommendations
    
    async def extract_reusable_components(self, codebase_path: str) -> List[ParsedComponent]:
        """재사용 가능한 컴포넌트 추출"""
        
        components = []
        
        # 파일별 분석
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        analysis = await self.ast_analyzer.analyze_file(file_path, 'python')
                        
                        # 클래스를 컴포넌트로 간주
                        for cls in analysis.get('classes', []):
                            component = ParsedComponent(
                                name=cls['name'],
                                type='class',
                                file_path=file_path,
                                dependencies=[],  # 실제 구현에서 추출
                                exports=[cls['name']],
                                complexity=len(cls.get('methods', [])),
                                reusability_score=self._calculate_reusability_score(cls),
                                patterns=[]  # 실제 구현에서 감지
                            )
                            components.append(component)
                            
                    except Exception:
                        continue
        
        return components
    
    def _calculate_reusability_score(self, component_data: Dict) -> float:
        """재사용성 점수 계산"""
        
        score = 0.5  # 기본 점수
        
        # 메서드 수가 적절한 경우 점수 증가
        method_count = len(component_data.get('methods', []))
        if 3 <= method_count <= 10:
            score += 0.2
        
        # 이름이 일반적인 경우 점수 증가
        name = component_data.get('name', '').lower()
        if any(keyword in name for keyword in ['base', 'common', 'util', 'helper']):
            score += 0.3
        
        return min(score, 1.0)