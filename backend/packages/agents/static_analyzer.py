"""정적 코드 분석기 (StaticAnalyzer) - 코드 실행 없이 코드베이스 구조 분석

이 에이전트는 코드를 실행하지 않고 정적 분석을 수행하여 코드베이스의 구조, 의존성,
복잡성 및 잠재적 문제를 파악합니다.

주요 기능:
1. 코드베이스 전체 구조 분석 및 아키텍처 레이어 감지
2. 파일간 의존성 그래프 생성 및 순환 의존성 검출
3. 순환 복잡도 계산 및 복잡도 핫스팟 식별
4. API 엔드포인트 자동 감지 (Flask/FastAPI 패턴)
5. 보안 취약점 스캔 (하드코딩된 비밀번호, SQL 인젝션 등)
6. 테스트 커버리지 추정 및 코드 스멜 감지
7. 계약(Contract) 및 인터페이스 추출
8. 다중 언어 지원 (Python, JavaScript, TypeScript 등)

입력 매개변수:
- path: 분석할 코드베이스 루트 경로
- recursive: 하위 디렉토리 분석 여부 (기본: True)
- ignore_patterns: 제외할 패턴 목록 (기본: ['__pycache__', '.git', 'node_modules'])

출력 형식:
- total_files: 분석된 총 파일 수
- total_lines: 총 코드 라인 수
- language_distribution: 언어별 파일 분포
- dependency_graph: 파일간 의존성 그래프
- complexity_hotspots: 복잡도가 높은 영역 목록
- architecture_layers: 아키텍처 레이어 분류
- api_endpoints: 감지된 API 엔드포인트 목록
- security_issues: 발견된 보안 이슈
- test_coverage_estimate: 테스트 커버리지 추정치
- contracts: 추출된 계약 정보
- interfaces: 추출된 인터페이스 정보

문서 참조 관계:
- 읽어오는 보고서: 없음 (원시 코드 파일만 분석)
- 출력을 사용하는 에이전트:
  - CodeImproverAgent: 리팩토링 대상 식별
  - QualityGate: 품질 검증 기준선
  - PlannerAgent: 개선 계획 수립
  - ImpactAnalyzer: 변경 영향도 분석

사용 예시:
```python
analyzer = StaticAnalyzer()
result = await analyzer.execute({
    'path': '/project/src',
    'recursive': True,
    'ignore_patterns': ['tests', '__pycache__']
})
print(f"분석된 파일: {result.data['analysis']['total_files']}개")
print(f"복잡도 핫스팟: {len(result.data['analysis']['complexity_hotspots'])}개")
```

작성자: T-Developer v2 Team
버전: 1.2.0
최종 수정: 2025-08-23
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import logging

from backend.packages.agents.base import BaseAgent, AgentResult, TaskStatus


@dataclass
class CodeMetrics:
    """Metrics for a single code file."""
    
    file_path: str
    lines_of_code: int = 0
    cyclomatic_complexity: int = 0
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    code_smells: List[str] = field(default_factory=list)


@dataclass
class CodebaseAnalysis:
    """Complete analysis of a codebase."""
    
    total_files: int = 0
    total_lines: int = 0
    language_distribution: Dict[str, int] = field(default_factory=dict)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    complexity_hotspots: List[Dict[str, Any]] = field(default_factory=list)
    architecture_layers: Dict[str, List[str]] = field(default_factory=dict)
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    security_issues: List[Dict[str, Any]] = field(default_factory=list)
    test_coverage_estimate: float = 0.0
    metrics_by_file: Dict[str, CodeMetrics] = field(default_factory=dict)
    contracts: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    interfaces: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


class StaticAnalyzer(BaseAgent):
    """Static code analysis agent.
    
    Analyzes codebases without execution to understand:
    - Structure and architecture
    - Dependencies and coupling
    - Complexity and maintainability
    - Security vulnerabilities
    - Code quality issues
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # File extensions to analyze
        self.analyzable_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.sh': 'shell',
            '.dockerfile': 'docker',
            '.tf': 'terraform'
        }
    
    async def analyze_codebase(
        self,
        path: str,
        recursive: bool = True,
        ignore_patterns: Optional[List[str]] = None
    ) -> CodebaseAnalysis:
        """Analyze an entire codebase.
        
        Args:
            path: Root path of the codebase
            recursive: Whether to analyze subdirectories
            ignore_patterns: Patterns to ignore (e.g., ['*.test.py', 'node_modules'])
            
        Returns:
            Complete codebase analysis
        """
        analysis = CodebaseAnalysis()
        ignore_patterns = ignore_patterns or ['__pycache__', '.git', 'node_modules', 'venv', '.env']
        
        # Collect all files
        files_to_analyze = self._collect_files(path, recursive, ignore_patterns)
        analysis.total_files = len(files_to_analyze)
        
        # Analyze each file
        for file_path in files_to_analyze:
            try:
                metrics = await self._analyze_file(file_path)
                analysis.metrics_by_file[file_path] = metrics
                
                # Update aggregate metrics
                analysis.total_lines += metrics.lines_of_code
                
                # Track language distribution
                ext = Path(file_path).suffix
                if ext in self.analyzable_extensions:
                    lang = self.analyzable_extensions[ext]
                    analysis.language_distribution[lang] = \
                        analysis.language_distribution.get(lang, 0) + 1
                
                # Build dependency graph
                if metrics.dependencies:
                    analysis.dependency_graph[file_path] = metrics.dependencies
                
                # Track complexity hotspots
                if metrics.cyclomatic_complexity > 10:
                    analysis.complexity_hotspots.append({
                        'file': file_path,
                        'complexity': metrics.cyclomatic_complexity,
                        'functions': metrics.functions
                    })
                    
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Analyze architecture layers
        analysis.architecture_layers = self._detect_architecture_layers(analysis.metrics_by_file)
        
        # Detect API endpoints
        analysis.api_endpoints = self._detect_api_endpoints(analysis.metrics_by_file)
        
        # Security scan
        analysis.security_issues = self._scan_security_issues(analysis.metrics_by_file)
        
        # Estimate test coverage
        analysis.test_coverage_estimate = self._estimate_test_coverage(files_to_analyze)
        
        # Extract contracts and interfaces
        contracts, interfaces = self._extract_contracts_and_interfaces(analysis.metrics_by_file)
        analysis.contracts = contracts
        analysis.interfaces = interfaces
        
        return analysis
    
    def _collect_files(
        self,
        path: str,
        recursive: bool,
        ignore_patterns: List[str]
    ) -> List[str]:
        """Collect all files to analyze."""
        files = []
        path_obj = Path(path)
        
        if not path_obj.exists():
            return files
        
        if path_obj.is_file():
            return [str(path_obj)]
        
        # Directory traversal
        pattern = '**/*' if recursive else '*'
        for file_path in path_obj.glob(pattern):
            if file_path.is_file():
                # Check ignore patterns
                if any(pattern in str(file_path) for pattern in ignore_patterns):
                    continue
                    
                # Check if analyzable
                if file_path.suffix in self.analyzable_extensions:
                    files.append(str(file_path))
        
        return files
    
    async def _analyze_file(self, file_path: str) -> CodeMetrics:
        """Analyze a single file."""
        metrics = CodeMetrics(file_path=file_path)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                metrics.lines_of_code = len(lines)
        except Exception as e:
            self.logger.warning(f"Could not read {file_path}: {e}")
            return metrics
        
        # Language-specific analysis
        ext = Path(file_path).suffix
        
        if ext == '.py':
            metrics = self._analyze_python_file(content, metrics)
        elif ext in ['.js', '.ts']:
            metrics = self._analyze_javascript_file(content, metrics)
        elif ext in ['.yaml', '.yml']:
            metrics = self._analyze_yaml_file(content, metrics)
        
        # Common pattern detection
        metrics.code_smells = self._detect_code_smells(content)
        
        return metrics
    
    def _analyze_python_file(self, content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Analyze Python-specific patterns."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Collect imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metrics.imports.append(alias.name)
                        metrics.dependencies.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        metrics.imports.append(node.module)
                        metrics.dependencies.add(node.module.split('.')[0])
                
                # Collect classes
                elif isinstance(node, ast.ClassDef):
                    metrics.classes.append(node.name)
                
                # Collect functions
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    metrics.functions.append(node.name)
                    # Simple complexity calculation
                    metrics.cyclomatic_complexity += self._calculate_complexity(node)
                    
        except SyntaxError as e:
            self.logger.warning(f"Syntax error in Python file: {e}")
            
        return metrics
    
    def _analyze_javascript_file(self, content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Analyze JavaScript/TypeScript patterns."""
        # Simple regex-based analysis for JS/TS
        
        # Find imports
        import_pattern = r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]'
        for match in re.finditer(import_pattern, content):
            module = match.group(1)
            metrics.imports.append(module)
            if not module.startswith('.'):
                metrics.dependencies.add(module.split('/')[0])
        
        # Find classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            metrics.classes.append(match.group(1))
        
        # Find functions
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\()'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                metrics.functions.append(func_name)
        
        return metrics
    
    def _analyze_yaml_file(self, content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Analyze YAML configuration files."""
        # Look for API definitions, configurations, etc.
        if 'openapi:' in content or 'swagger:' in content:
            metrics.code_smells.append('API_DEFINITION_FOUND')
        
        return metrics
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a Python function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
    
    def _detect_code_smells(self, content: str) -> List[str]:
        """Detect common code smells and anti-patterns."""
        smells = []
        
        # Long lines
        lines = content.split('\n')
        if any(len(line) > 120 for line in lines):
            smells.append('LONG_LINES')
        
        # TODO comments
        if 'TODO' in content or 'FIXME' in content:
            smells.append('UNFINISHED_WORK')
        
        # Hardcoded credentials
        if re.search(r'(password|api_key|secret)\s*=\s*[\'"][^\'"]+[\'"]', content, re.IGNORECASE):
            smells.append('HARDCODED_CREDENTIALS')
        
        # Large functions (simple heuristic)
        func_pattern = r'def\s+\w+.*?(?=\ndef|\nclass|\Z)'
        for match in re.finditer(func_pattern, content, re.DOTALL):
            if len(match.group().split('\n')) > 50:
                smells.append('LARGE_FUNCTION')
                break
        
        return smells
    
    def _detect_architecture_layers(
        self,
        metrics_by_file: Dict[str, CodeMetrics]
    ) -> Dict[str, List[str]]:
        """Detect architectural layers based on file paths and patterns."""
        layers = {
            'presentation': [],
            'business': [],
            'data': [],
            'infrastructure': [],
            'tests': []
        }
        
        for file_path in metrics_by_file:
            path_lower = file_path.lower()
            
            if any(pattern in path_lower for pattern in ['test', 'spec']):
                layers['tests'].append(file_path)
            elif any(pattern in path_lower for pattern in ['view', 'ui', 'frontend', 'component']):
                layers['presentation'].append(file_path)
            elif any(pattern in path_lower for pattern in ['service', 'business', 'logic', 'domain']):
                layers['business'].append(file_path)
            elif any(pattern in path_lower for pattern in ['model', 'entity', 'schema', 'database', 'repository']):
                layers['data'].append(file_path)
            elif any(pattern in path_lower for pattern in ['config', 'util', 'helper', 'middleware']):
                layers['infrastructure'].append(file_path)
        
        return layers
    
    def _detect_api_endpoints(
        self,
        metrics_by_file: Dict[str, CodeMetrics]
    ) -> List[Dict[str, Any]]:
        """Detect API endpoints from code patterns."""
        endpoints = []
        
        for file_path, metrics in metrics_by_file.items():
            # Simple heuristic: look for route decorators or patterns
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Flask/FastAPI patterns
                route_pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
                for match in re.finditer(route_pattern, content):
                    endpoints.append({
                        'file': file_path,
                        'method': match.group(1).upper(),
                        'path': match.group(2)
                    })
                    
            except Exception:
                pass
        
        return endpoints
    
    def _scan_security_issues(
        self,
        metrics_by_file: Dict[str, CodeMetrics]
    ) -> List[Dict[str, Any]]:
        """Scan for common security issues."""
        issues = []
        
        for file_path, metrics in metrics_by_file.items():
            # Check for hardcoded credentials
            if 'HARDCODED_CREDENTIALS' in metrics.code_smells:
                issues.append({
                    'file': file_path,
                    'type': 'HARDCODED_CREDENTIALS',
                    'severity': 'HIGH',
                    'description': 'Possible hardcoded credentials detected'
                })
            
            # Check for SQL injection risks (simple pattern)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(r'execute\([\'"].*?%s.*?[\'"]', content):
                        issues.append({
                            'file': file_path,
                            'type': 'SQL_INJECTION_RISK',
                            'severity': 'HIGH',
                            'description': 'Possible SQL injection vulnerability'
                        })
            except Exception:
                pass
        
        return issues
    
    def _estimate_test_coverage(self, files: List[str]) -> float:
        """Estimate test coverage based on test file ratio."""
        test_files = [f for f in files if 'test' in f.lower()]
        non_test_files = [f for f in files if 'test' not in f.lower()]
        
        if not non_test_files:
            return 0.0
        
        # Simple heuristic: ratio of test files to non-test files
        ratio = len(test_files) / len(non_test_files)
        # Cap at 100%
        return min(ratio * 100, 100.0)
    
    def _extract_contracts_and_interfaces(
        self,
        metrics_by_file: Dict[str, CodeMetrics]
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
        """Extract contracts and interfaces from analyzed files.
        
        Contracts are:
        - Function signatures with type hints
        - Class method signatures
        - Expected input/output specifications
        - Docstring specifications
        
        Interfaces are:
        - Abstract base classes
        - Protocol definitions
        - Public API methods
        - Type definitions
        """
        contracts = {}
        interfaces = {}
        
        for file_path, metrics in metrics_by_file.items():
            file_contracts = []
            file_interfaces = []
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Extract class definitions (potential interfaces)
                    if isinstance(node, ast.ClassDef):
                        is_interface = False
                        methods = []
                        
                        # Check if it's an ABC or Protocol
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                if base.id in ['ABC', 'Protocol', 'BaseAgent', 'BaseClass']:
                                    is_interface = True
                            elif isinstance(base, ast.Attribute):
                                if base.attr in ['ABC', 'Protocol']:
                                    is_interface = True
                        
                        # Extract methods
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_info = self._extract_function_contract(item)
                                methods.append(method_info)
                                
                                # Add to contracts
                                if method_info['has_type_hints'] or method_info['has_docstring']:
                                    file_contracts.append({
                                        'type': 'method',
                                        'class': node.name,
                                        'name': method_info['name'],
                                        'signature': method_info['signature'],
                                        'docstring': method_info['docstring'],
                                        'line': item.lineno
                                    })
                        
                        if is_interface or node.name.startswith('I') or node.name.endswith('Interface'):
                            file_interfaces.append({
                                'name': node.name,
                                'type': 'class_interface',
                                'methods': methods,
                                'line': node.lineno,
                                'is_abstract': is_interface
                            })
                    
                    # Extract function definitions (contracts)
                    elif isinstance(node, ast.FunctionDef):
                        # Skip methods (already handled in classes)
                        if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree) 
                                  if hasattr(p, 'body') and node in p.body):
                            func_info = self._extract_function_contract(node)
                            
                            if func_info['has_type_hints'] or func_info['has_docstring']:
                                file_contracts.append({
                                    'type': 'function',
                                    'name': func_info['name'],
                                    'signature': func_info['signature'],
                                    'docstring': func_info['docstring'],
                                    'line': node.lineno,
                                    'is_public': not func_info['name'].startswith('_')
                                })
                    
                    # Extract type aliases and TypedDicts (interfaces)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Check if it's a type alias
                                if isinstance(node.value, (ast.Subscript, ast.Name)):
                                    if target.id[0].isupper():  # Likely a type definition
                                        file_interfaces.append({
                                            'name': target.id,
                                            'type': 'type_alias',
                                            'line': node.lineno
                                        })
                
                # Store results
                if file_contracts:
                    contracts[file_path] = file_contracts
                if file_interfaces:
                    interfaces[file_path] = file_interfaces
                    
            except Exception as e:
                self.logger.debug(f"Could not extract contracts from {file_path}: {e}")
        
        return contracts, interfaces
    
    def _extract_function_contract(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract contract information from a function node."""
        # Get function signature
        args = []
        has_type_hints = False
        
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                has_type_hints = True
                if hasattr(ast, 'unparse'):
                    arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Check return type
        return_type = None
        if node.returns:
            has_type_hints = True
            if hasattr(ast, 'unparse'):
                return_type = ast.unparse(node.returns)
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        signature = f"({', '.join(args)})"
        if return_type:
            signature += f" -> {return_type}"
        
        return {
            'name': node.name,
            'signature': signature,
            'has_type_hints': has_type_hints,
            'has_docstring': bool(docstring),
            'docstring': docstring,
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'decorators': [d.id if isinstance(d, ast.Name) else str(d) 
                          for d in node.decorator_list]
        }
    
    async def execute(self, task) -> AgentResult:
        """Execute static analysis task.
        
        Args:
            task: Task (dict or AgentTask) with 'path' and optional 'recursive', 'ignore_patterns'
            
        Returns:
            AgentResult with analysis data
        """
        try:
            # Handle both dict and AgentTask inputs
            if isinstance(task, dict):
                inputs = task
            else:
                inputs = task.inputs
            
            path = inputs.get('path', '.')
            recursive = inputs.get('recursive', True)
            ignore_patterns = inputs.get('ignore_patterns', None)
            
            self.logger.info(f"Starting static analysis of {path}")
            
            analysis = await self.analyze_codebase(path, recursive, ignore_patterns)
            
            # Prepare summary
            summary = {
                'total_files': analysis.total_files,
                'total_lines': analysis.total_lines,
                'languages': analysis.language_distribution,
                'complexity_hotspots': len(analysis.complexity_hotspots),
                'security_issues': len(analysis.security_issues),
                'api_endpoints': len(analysis.api_endpoints),
                'test_coverage_estimate': f"{analysis.test_coverage_estimate:.1f}%"
            }
            
            self.logger.info(f"Analysis complete: {summary}")
            
            return AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data={
                    'analysis': analysis.__dict__,
                    'summary': summary
                },
                metadata={"message": f"Successfully analyzed {analysis.total_files} files"}
            )
            
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
            return AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                error=str(e),
                metadata={"message": "Static analysis failed"}
            )