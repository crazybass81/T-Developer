"""
🧬 T-Developer AI Code Analyzer
6.5KB Ultra-lightweight AI Code Analysis Engine
"""
import ast
import inspect
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodeMetrics:
    """Code quality metrics"""

    lines: int = 0
    functions: int = 0
    classes: int = 0
    complexity: int = 0
    imports: int = 0
    memory_score: float = 0.0  # Memory efficiency score


@dataclass
class AnalysisResult:
    """AI analysis result"""

    capabilities: List[str]
    metrics: CodeMetrics
    suggestions: List[str]
    quality_score: float
    memory_efficient: bool


class CodeAnalyzer:
    """Ultra-fast code analyzer with <6.5KB footprint"""

    def __init__(self):
        self.capability_patterns = {
            "data_processing": [r"pandas", r"numpy", r"\.csv", r"\.json"],
            "api_handling": [r"requests", r"fastapi", r"@app\.", r"router"],
            "database": [r"sqlalchemy", r"pymongo", r"SELECT", r"INSERT"],
            "file_ops": [r"open\(", r"Path", r"\.read", r"\.write"],
            "async": [r"async def", r"await", r"asyncio"],
            "testing": [r"pytest", r"unittest", r"assert", r"test_"],
            "ml_ai": [r"tensorflow", r"torch", r"sklearn", r"model"],
        }

    def analyze_code(self, code: str, file_path: str = "") -> AnalysisResult:
        """Analyze code and extract capabilities"""
        try:
            tree = ast.parse(code)
            metrics = self._calculate_metrics(code, tree)
            capabilities = self._extract_capabilities(code)
            suggestions = self._generate_suggestions(metrics, code)
            quality_score = self._calculate_quality_score(metrics)
            memory_efficient = metrics.lines < 100  # 6.5KB ~= 100 lines

            return AnalysisResult(
                capabilities=capabilities,
                metrics=metrics,
                suggestions=suggestions,
                quality_score=quality_score,
                memory_efficient=memory_efficient,
            )
        except Exception as e:
            return AnalysisResult([], CodeMetrics(), [f"Parse error: {str(e)}"], 0.0, False)

    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze Python file"""
        try:
            code = file_path.read_text()
            return self.analyze_code(code, str(file_path))
        except Exception as e:
            return AnalysisResult([], CodeMetrics(), [f"File error: {str(e)}"], 0.0, False)

    def _calculate_metrics(self, code: str, tree: ast.AST) -> CodeMetrics:
        """Calculate code metrics"""
        lines = len(code.split("\n"))
        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        imports = sum(
            1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
        )

        # Simple complexity (nested blocks)
        complexity = sum(
            1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While, ast.With))
        )

        # Memory efficiency score (smaller is better for 6.5KB constraint)
        memory_score = max(0, 10 - (lines / 10))  # 10 perfect score at 0 lines

        return CodeMetrics(lines, functions, classes, complexity, imports, memory_score)

    def _extract_capabilities(self, code: str) -> List[str]:
        """Extract code capabilities using pattern matching"""
        capabilities = []
        for capability, patterns in self.capability_patterns.items():
            if any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns):
                capabilities.append(capability)
        return capabilities

    def _generate_suggestions(self, metrics: CodeMetrics, code: str) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []

        if metrics.lines > 100:
            suggestions.append("Consider splitting into smaller modules for 6.5KB constraint")

        if metrics.complexity > 10:
            suggestions.append("High complexity detected - consider refactoring")

        if "import *" in code:
            suggestions.append("Avoid wildcard imports for memory efficiency")

        if metrics.functions == 0 and metrics.classes == 0:
            suggestions.append("Consider organizing code into functions")

        return suggestions

    def _calculate_quality_score(self, metrics: CodeMetrics) -> float:
        """Calculate overall quality score (0-10)"""
        score = 5.0  # Base score

        # Bonus for functions/classes
        score += min(2.0, metrics.functions * 0.5)
        score += min(1.0, metrics.classes * 0.5)

        # Penalty for high complexity
        score -= min(2.0, metrics.complexity * 0.2)

        # Memory efficiency bonus (6.5KB constraint)
        score += metrics.memory_score * 0.3

        return max(0.0, min(10.0, score))


# Factory function for easy instantiation
def create_analyzer() -> CodeAnalyzer:
    """Create code analyzer instance"""
    return CodeAnalyzer()


# Quick analysis function
def quick_analyze(code: str) -> Dict[str, Any]:
    """Quick code analysis with minimal overhead"""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_code(code)
    return {
        "capabilities": result.capabilities,
        "quality_score": result.quality_score,
        "memory_efficient": result.memory_efficient,
        "lines": result.metrics.lines,
    }
