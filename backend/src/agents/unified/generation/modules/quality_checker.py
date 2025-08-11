"""
Quality Checker Module for Generation Agent
Analyzes code quality, security, and performance metrics
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import asyncio
import json
import re
import ast
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import math


class QualityMetric(Enum):
    CODE_COVERAGE = "code_coverage"
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    MAINTAINABILITY_INDEX = "maintainability_index"
    DUPLICATION_RATIO = "duplication_ratio"
    TECHNICAL_DEBT = "technical_debt"
    SECURITY_SCORE = "security_score"
    PERFORMANCE_SCORE = "performance_score"
    ACCESSIBILITY_SCORE = "accessibility_score"


class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityIssue:
    type: str
    severity: Severity
    message: str
    file_path: str
    line_number: int
    column_number: int = 0
    rule_id: str = ""
    suggestion: str = ""


@dataclass
class QualityMetrics:
    code_coverage: float
    cyclomatic_complexity: float
    maintainability_index: float
    duplication_ratio: float
    technical_debt_hours: float
    security_score: float
    performance_score: float
    accessibility_score: float
    lines_of_code: int
    files_analyzed: int


@dataclass
class QualityResult:
    success: bool
    metrics: QualityMetrics
    issues: List[QualityIssue]
    overall_score: float
    grade: str
    recommendations: List[str]
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


class QualityChecker:
    """Advanced code quality analyzer"""
    
    def __init__(self):
        self.version = "1.0.0"
        
        # Quality thresholds
        self.thresholds = {
            QualityMetric.CODE_COVERAGE: 80.0,
            QualityMetric.CYCLOMATIC_COMPLEXITY: 10.0,
            QualityMetric.MAINTAINABILITY_INDEX: 70.0,
            QualityMetric.DUPLICATION_RATIO: 5.0,
            QualityMetric.TECHNICAL_DEBT: 20.0,
            QualityMetric.SECURITY_SCORE: 80.0,
            QualityMetric.PERFORMANCE_SCORE: 75.0,
            QualityMetric.ACCESSIBILITY_SCORE: 85.0
        }
        
        # Security patterns to check
        self.security_patterns = {
            'sql_injection': [
                r'SELECT.*\+.*',
                r'INSERT.*\+.*',
                r'UPDATE.*\+.*',
                r'DELETE.*\+.*'
            ],
            'xss_vulnerability': [
                r'innerHTML\s*=',
                r'document\.write\(',
                r'eval\(',
                r'dangerouslySetInnerHTML'
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ],
            'insecure_random': [
                r'Math\.random\(',
                r'random\.choice\(',
                r'rand\('
            ]
        }
        
        # Performance anti-patterns
        self.performance_patterns = {
            'inefficient_loops': [
                r'for.*in.*Object\.keys\(',
                r'\.length.*for\s*\(',
                r'while.*true.*break'
            ],
            'memory_leaks': [
                r'setInterval.*without.*clearInterval',
                r'addEventListener.*without.*removeEventListener',
                r'new.*Array\(\d{4,}\)'  # Large array allocations
            ],
            'blocking_operations': [
                r'fs\.readFileSync\(',
                r'\.sync\(\)',
                r'sleep\('
            ]
        }
        
        # Code smell patterns
        self.code_smells = {
            'long_parameter_list': 5,  # More than 5 parameters
            'large_class': 500,        # More than 500 lines
            'long_method': 50,         # More than 50 lines
            'deep_nesting': 4          # More than 4 levels of nesting
        }
        
        # Framework-specific analyzers
        self.framework_analyzers = {
            'react': self._analyze_react_quality,
            'vue': self._analyze_vue_quality,
            'angular': self._analyze_angular_quality,
            'express': self._analyze_express_quality,
            'fastapi': self._analyze_fastapi_quality,
            'django': self._analyze_django_quality,
            'flask': self._analyze_flask_quality
        }
    
    async def analyze_project(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> QualityResult:
        """Analyze project quality"""
        
        start_time = datetime.now()
        
        try:
            framework = context.get('target_framework', 'react')
            language = context.get('target_language', 'javascript')
            
            # Collect all files to analyze
            files_to_analyze = await self._collect_files(project_path, language)
            
            # Initialize metrics
            metrics = QualityMetrics(
                code_coverage=0.0,
                cyclomatic_complexity=0.0,
                maintainability_index=0.0,
                duplication_ratio=0.0,
                technical_debt_hours=0.0,
                security_score=0.0,
                performance_score=0.0,
                accessibility_score=0.0,
                lines_of_code=0,
                files_analyzed=len(files_to_analyze)
            )
            
            issues = []
            
            # Analyze each file
            for file_path in files_to_analyze:
                file_issues, file_metrics = await self._analyze_file(
                    file_path, language, framework
                )
                
                issues.extend(file_issues)
                metrics = self._aggregate_metrics(metrics, file_metrics)
            
            # Calculate derived metrics
            metrics = self._calculate_derived_metrics(metrics, len(files_to_analyze))
            
            # Framework-specific analysis
            if framework in self.framework_analyzers:
                framework_issues, framework_metrics = await self.framework_analyzers[framework](
                    project_path, context
                )
                issues.extend(framework_issues)
                metrics = self._merge_framework_metrics(metrics, framework_metrics)
            
            # Calculate overall score and grade
            overall_score, grade = self._calculate_overall_score(metrics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(metrics, issues, framework)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return QualityResult(
                success=True,
                metrics=metrics,
                issues=issues,
                overall_score=overall_score,
                grade=grade,
                recommendations=recommendations,
                processing_time=processing_time,
                metadata={
                    'framework': framework,
                    'language': language,
                    'files_analyzed': len(files_to_analyze),
                    'total_issues': len(issues),
                    'critical_issues': len([i for i in issues if i.severity == Severity.CRITICAL])
                }
            )
            
        except Exception as e:
            return QualityResult(
                success=False,
                metrics=QualityMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                issues=[],
                overall_score=0.0,
                grade='F',
                recommendations=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e)
            )
    
    async def _collect_files(self, project_path: str, language: str) -> List[str]:
        """Collect files to analyze based on language"""
        
        extensions = {
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'python': ['.py'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs']
        }
        
        file_extensions = extensions.get(language, ['.js', '.ts'])
        files = []
        
        # In a real implementation, this would recursively scan the directory
        # For now, return a simulated list
        for i in range(10):  # Simulate 10 files
            files.append(f"{project_path}/src/component_{i}.ts")
        
        return files
    
    async def _analyze_file(
        self, 
        file_path: str, 
        language: str, 
        framework: str
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze a single file"""
        
        issues = []
        
        # Simulate file content reading and analysis
        file_content = f"// Simulated content for {file_path}\n" * 50
        
        # Calculate basic metrics
        lines_of_code = len(file_content.split('\n'))
        
        # Security analysis
        security_issues = await self._analyze_security(file_content, file_path)
        issues.extend(security_issues)
        
        # Performance analysis
        performance_issues = await self._analyze_performance(file_content, file_path)
        issues.extend(performance_issues)
        
        # Code smell detection
        code_smell_issues = await self._analyze_code_smells(file_content, file_path, language)
        issues.extend(code_smell_issues)
        
        # Calculate complexity
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(file_content, language)
        
        file_metrics = {
            'lines_of_code': lines_of_code,
            'cyclomatic_complexity': cyclomatic_complexity,
            'issues_count': len(issues),
            'security_issues': len(security_issues),
            'performance_issues': len(performance_issues)
        }
        
        return issues, file_metrics
    
    async def _analyze_security(self, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze security vulnerabilities"""
        
        issues = []
        
        for vulnerability_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    line_number = content[:match.start()].count('\n') + 1
                    
                    issues.append(QualityIssue(
                        type=vulnerability_type,
                        severity=Severity.HIGH,
                        message=f"Potential {vulnerability_type.replace('_', ' ')} detected",
                        file_path=file_path,
                        line_number=line_number,
                        rule_id=f"security.{vulnerability_type}",
                        suggestion=self._get_security_suggestion(vulnerability_type)
                    ))
        
        return issues
    
    async def _analyze_performance(self, content: str, file_path: str) -> List[QualityIssue]:
        """Analyze performance issues"""
        
        issues = []
        
        for issue_type, patterns in self.performance_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    line_number = content[:match.start()].count('\n') + 1
                    
                    issues.append(QualityIssue(
                        type=issue_type,
                        severity=Severity.MEDIUM,
                        message=f"Performance issue: {issue_type.replace('_', ' ')}",
                        file_path=file_path,
                        line_number=line_number,
                        rule_id=f"performance.{issue_type}",
                        suggestion=self._get_performance_suggestion(issue_type)
                    ))
        
        return issues
    
    async def _analyze_code_smells(
        self, 
        content: str, 
        file_path: str, 
        language: str
    ) -> List[QualityIssue]:
        """Analyze code smells"""
        
        issues = []
        lines = content.split('\n')
        
        # Check for long methods
        method_lines = 0
        in_method = False
        method_start_line = 0
        
        for i, line in enumerate(lines, 1):
            # Simple method detection (would be more sophisticated in real implementation)
            if ('function ' in line or 'def ' in line or 
                ('(' in line and '{' in line and not line.strip().startswith('//'))):
                in_method = True
                method_start_line = i
                method_lines = 1
            elif in_method:
                if '}' in line or (language == 'python' and line.strip() and not line.startswith(' ')):
                    if method_lines > self.code_smells['long_method']:
                        issues.append(QualityIssue(
                            type='long_method',
                            severity=Severity.MEDIUM,
                            message=f"Method is too long ({method_lines} lines)",
                            file_path=file_path,
                            line_number=method_start_line,
                            rule_id="maintainability.long_method",
                            suggestion="Consider breaking this method into smaller, more focused methods"
                        ))
                    in_method = False
                    method_lines = 0
                else:
                    method_lines += 1
        
        # Check for deep nesting
        max_nesting = 0
        current_nesting = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try']):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.startswith('}') or (language == 'python' and not line.startswith(' ')):
                current_nesting = max(0, current_nesting - 1)
        
        if max_nesting > self.code_smells['deep_nesting']:
            issues.append(QualityIssue(
                type='deep_nesting',
                severity=Severity.MEDIUM,
                message=f"Deep nesting detected ({max_nesting} levels)",
                file_path=file_path,
                line_number=1,
                rule_id="maintainability.deep_nesting",
                suggestion="Consider extracting nested logic into separate methods"
            ))
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, content: str, language: str) -> float:
        """Calculate cyclomatic complexity"""
        
        # Simplified complexity calculation
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', '&&', '||']
        
        for keyword in decision_keywords:
            complexity += content.count(keyword)
        
        return min(complexity / 10.0, 20.0)  # Normalize to reasonable range
    
    def _aggregate_metrics(
        self, 
        current: QualityMetrics, 
        file_metrics: Dict[str, Any]
    ) -> QualityMetrics:
        """Aggregate metrics from file analysis"""
        
        return QualityMetrics(
            code_coverage=current.code_coverage,  # Will be calculated later
            cyclomatic_complexity=current.cyclomatic_complexity + file_metrics.get('cyclomatic_complexity', 0),
            maintainability_index=current.maintainability_index,  # Will be calculated later
            duplication_ratio=current.duplication_ratio,  # Will be calculated later
            technical_debt_hours=current.technical_debt_hours + file_metrics.get('issues_count', 0) * 0.5,
            security_score=current.security_score,  # Will be calculated later
            performance_score=current.performance_score,  # Will be calculated later
            accessibility_score=current.accessibility_score,  # Will be calculated later
            lines_of_code=current.lines_of_code + file_metrics.get('lines_of_code', 0),
            files_analyzed=current.files_analyzed
        )
    
    def _calculate_derived_metrics(
        self, 
        metrics: QualityMetrics, 
        file_count: int
    ) -> QualityMetrics:
        """Calculate derived metrics"""
        
        if file_count == 0:
            return metrics
        
        # Average cyclomatic complexity
        avg_complexity = metrics.cyclomatic_complexity / file_count
        
        # Estimated code coverage (would be from actual test runs)
        estimated_coverage = max(60.0, 100.0 - avg_complexity * 5)
        
        # Maintainability index calculation (simplified)
        # Real formula: 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        # Where HV = Halstead Volume, CC = Cyclomatic Complexity, LOC = Lines of Code
        volume = math.log(max(metrics.lines_of_code, 1))
        complexity = avg_complexity
        loc = math.log(max(metrics.lines_of_code, 1))
        
        maintainability = max(0, 171 - 5.2 * volume - 0.23 * complexity - 16.2 * loc)
        
        # Security score (inverse of security issues)
        security_score = max(0, 100 - metrics.technical_debt_hours * 2)
        
        # Performance score (inverse of performance issues)
        performance_score = max(0, 100 - metrics.technical_debt_hours * 1.5)
        
        # Accessibility score (would be from actual accessibility tests)
        accessibility_score = 85.0  # Default score
        
        # Duplication ratio (simplified estimation)
        duplication_ratio = min(10.0, metrics.technical_debt_hours / file_count)
        
        return QualityMetrics(
            code_coverage=estimated_coverage,
            cyclomatic_complexity=avg_complexity,
            maintainability_index=maintainability,
            duplication_ratio=duplication_ratio,
            technical_debt_hours=metrics.technical_debt_hours,
            security_score=security_score,
            performance_score=performance_score,
            accessibility_score=accessibility_score,
            lines_of_code=metrics.lines_of_code,
            files_analyzed=metrics.files_analyzed
        )
    
    def _calculate_overall_score(self, metrics: QualityMetrics) -> Tuple[float, str]:
        """Calculate overall quality score and grade"""
        
        weights = {
            'code_coverage': 0.20,
            'cyclomatic_complexity': 0.15,
            'maintainability_index': 0.20,
            'security_score': 0.25,
            'performance_score': 0.15,
            'accessibility_score': 0.05
        }
        
        # Normalize cyclomatic complexity (lower is better)
        complexity_score = max(0, 100 - metrics.cyclomatic_complexity * 10)
        
        weighted_score = (
            metrics.code_coverage * weights['code_coverage'] +
            complexity_score * weights['cyclomatic_complexity'] +
            metrics.maintainability_index * weights['maintainability_index'] +
            metrics.security_score * weights['security_score'] +
            metrics.performance_score * weights['performance_score'] +
            metrics.accessibility_score * weights['accessibility_score']
        )
        
        # Determine grade
        if weighted_score >= 90:
            grade = 'A'
        elif weighted_score >= 80:
            grade = 'B'
        elif weighted_score >= 70:
            grade = 'C'
        elif weighted_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return weighted_score, grade
    
    async def _generate_recommendations(
        self, 
        metrics: QualityMetrics, 
        issues: List[QualityIssue], 
        framework: str
    ) -> List[str]:
        """Generate quality improvement recommendations"""
        
        recommendations = []
        
        # Code coverage recommendations
        if metrics.code_coverage < self.thresholds[QualityMetric.CODE_COVERAGE]:
            recommendations.append(
                f"Increase test coverage from {metrics.code_coverage:.1f}% to at least {self.thresholds[QualityMetric.CODE_COVERAGE]}%"
            )
        
        # Complexity recommendations
        if metrics.cyclomatic_complexity > self.thresholds[QualityMetric.CYCLOMATIC_COMPLEXITY]:
            recommendations.append(
                f"Reduce cyclomatic complexity from {metrics.cyclomatic_complexity:.1f} to below {self.thresholds[QualityMetric.CYCLOMATIC_COMPLEXITY]}"
            )
        
        # Security recommendations
        security_issues = [i for i in issues if i.type in self.security_patterns.keys()]
        if security_issues:
            recommendations.append(
                f"Fix {len(security_issues)} security vulnerabilities to improve security score"
            )
        
        # Performance recommendations
        performance_issues = [i for i in issues if i.type in self.performance_patterns.keys()]
        if performance_issues:
            recommendations.append(
                f"Address {len(performance_issues)} performance issues for better application speed"
            )
        
        # Technical debt recommendations
        if metrics.technical_debt_hours > self.thresholds[QualityMetric.TECHNICAL_DEBT]:
            recommendations.append(
                f"Reduce technical debt from {metrics.technical_debt_hours:.1f} hours to below {self.thresholds[QualityMetric.TECHNICAL_DEBT]} hours"
            )
        
        # Framework-specific recommendations
        if framework == 'react':
            recommendations.extend([
                "Use React.memo for component optimization",
                "Implement proper error boundaries",
                "Use useCallback and useMemo for expensive computations"
            ])
        elif framework in ['fastapi', 'django', 'flask']:
            recommendations.extend([
                "Implement proper input validation",
                "Add rate limiting to API endpoints",
                "Use database query optimization"
            ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _get_security_suggestion(self, vulnerability_type: str) -> str:
        """Get security improvement suggestion"""
        
        suggestions = {
            'sql_injection': "Use parameterized queries or ORM to prevent SQL injection",
            'xss_vulnerability': "Sanitize user input and use secure DOM manipulation methods",
            'hardcoded_secrets': "Move sensitive data to environment variables or secure vaults",
            'insecure_random': "Use cryptographically secure random number generators"
        }
        
        return suggestions.get(vulnerability_type, "Review and fix this security issue")
    
    def _get_performance_suggestion(self, issue_type: str) -> str:
        """Get performance improvement suggestion"""
        
        suggestions = {
            'inefficient_loops': "Optimize loop operations and avoid repeated calculations",
            'memory_leaks': "Properly clean up event listeners and intervals",
            'blocking_operations': "Use asynchronous operations to avoid blocking"
        }
        
        return suggestions.get(issue_type, "Review and optimize this performance issue")
    
    # Framework-specific analyzers (simplified)
    async def _analyze_react_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze React-specific quality metrics"""
        
        issues = []
        metrics = {
            'component_reusability': 85.0,
            'hook_usage': 90.0,
            'prop_drilling': 15.0  # Lower is better
        }
        
        return issues, metrics
    
    async def _analyze_vue_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze Vue-specific quality metrics"""
        return [], {}
    
    async def _analyze_angular_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze Angular-specific quality metrics"""
        return [], {}
    
    async def _analyze_express_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze Express-specific quality metrics"""
        return [], {}
    
    async def _analyze_fastapi_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze FastAPI-specific quality metrics"""
        return [], {}
    
    async def _analyze_django_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze Django-specific quality metrics"""
        return [], {}
    
    async def _analyze_flask_quality(
        self, 
        project_path: str, 
        context: Dict[str, Any]
    ) -> Tuple[List[QualityIssue], Dict[str, Any]]:
        """Analyze Flask-specific quality metrics"""
        return [], {}
    
    def _merge_framework_metrics(
        self, 
        base_metrics: QualityMetrics, 
        framework_metrics: Dict[str, Any]
    ) -> QualityMetrics:
        """Merge framework-specific metrics with base metrics"""
        
        # Framework metrics would influence overall scores
        # This is a simplified implementation
        return base_metrics