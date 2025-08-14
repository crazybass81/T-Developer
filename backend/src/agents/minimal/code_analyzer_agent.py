"""Code Analyzer Agent - Minimal unit for analyzing code structure and quality"""
import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.agents.evolution.base_agent import BaseEvolutionAgent


class CodeAnalyzerAgent(BaseEvolutionAgent):
    """코드 분석 최소 단위 에이전트"""

    def __init__(self):
        super().__init__(name="CodeAnalyzerAgent", version="1.0.0")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        코드 분석 실행
        input_data: {
            "file_path": "분석할 파일 경로",
            "code": "분석할 코드 (파일 경로 대신)",
            "analysis_type": ["structure", "complexity", "quality", "dependencies"]
        }
        """
        file_path = input_data.get("file_path")
        code = input_data.get("code")
        analysis_types = input_data.get("analysis_type", ["structure", "quality"])

        # 코드 가져오기
        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                source_file = file_path
        else:
            source_file = "inline_code"

        if not code:
            return {"error": "No code provided for analysis"}

        result = {"source": source_file, "analysis": {}}

        # 구조 분석
        if "structure" in analysis_types:
            result["analysis"]["structure"] = self._analyze_structure(code)

        # 복잡도 분석
        if "complexity" in analysis_types:
            result["analysis"]["complexity"] = self._analyze_complexity(code)

        # 품질 분석
        if "quality" in analysis_types:
            result["analysis"]["quality"] = self._analyze_quality(code)

        # 의존성 분석
        if "dependencies" in analysis_types:
            result["analysis"]["dependencies"] = self._analyze_dependencies(code)

        # 개선 제안
        result["improvements"] = self._suggest_improvements(result["analysis"])

        self.log_execution(input_data, result)
        return result

    def _analyze_structure(self, code: str) -> Dict:
        """코드 구조 분석"""
        try:
            tree = ast.parse(code)

            structure = {
                "classes": [],
                "functions": [],
                "imports": [],
                "global_variables": [],
                "line_count": len(code.splitlines()),
                "docstring_count": 0,
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": [],
                        "line_start": node.lineno,
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(item.name)
                    structure["classes"].append(class_info)
                    if class_info["has_docstring"]:
                        structure["docstring_count"] += 1

                elif isinstance(node, ast.FunctionDef) and not self._is_nested(node, tree):
                    func_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line_start": node.lineno,
                        "has_docstring": ast.get_docstring(node) is not None,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                    structure["functions"].append(func_info)
                    if func_info["has_docstring"]:
                        structure["docstring_count"] += 1

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            structure["imports"].append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            structure["imports"].append(f"{module}.{alias.name}")

                elif isinstance(node, ast.Assign) and not self._is_nested(node, tree):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            structure["global_variables"].append(target.id)

            return structure

        except SyntaxError as e:
            return {"error": f"Syntax error in code: {e}"}

    def _analyze_complexity(self, code: str) -> Dict:
        """복잡도 분석 (Cyclomatic Complexity)"""
        try:
            tree = ast.parse(code)

            complexity = {
                "cyclomatic_complexity": 1,  # Base complexity
                "nesting_depth": 0,
                "branch_count": 0,
                "loop_count": 0,
            }

            def calculate_complexity(node, depth=0):
                nonlocal complexity

                complexity["nesting_depth"] = max(complexity["nesting_depth"], depth)

                if isinstance(node, (ast.If, ast.While, ast.For)):
                    complexity["cyclomatic_complexity"] += 1
                    complexity["branch_count"] += 1

                if isinstance(node, (ast.While, ast.For)):
                    complexity["loop_count"] += 1

                if isinstance(node, ast.Try):
                    complexity["cyclomatic_complexity"] += len(node.handlers)

                for child in ast.iter_child_nodes(node):
                    calculate_complexity(child, depth + 1)

            calculate_complexity(tree)

            # 복잡도 평가
            cc = complexity["cyclomatic_complexity"]
            if cc <= 5:
                complexity["rating"] = "Simple"
            elif cc <= 10:
                complexity["rating"] = "Moderate"
            elif cc <= 20:
                complexity["rating"] = "Complex"
            else:
                complexity["rating"] = "Very Complex"

            return complexity

        except SyntaxError:
            return {"error": "Cannot analyze complexity due to syntax errors"}

    def _analyze_quality(self, code: str) -> Dict:
        """코드 품질 분석"""
        lines = code.splitlines()

        quality = {
            "total_lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(1 for line in lines if line.strip().startswith("#")),
            "long_lines": sum(1 for line in lines if len(line) > 79),
            "todo_count": sum(1 for line in lines if "TODO" in line or "FIXME" in line),
            "has_type_hints": "Optional[" in code or "List[" in code or "Dict[" in code,
            "has_docstrings": '"""' in code or "'''" in code,
            "quality_score": 0,
        }

        # 품질 점수 계산 (0-100)
        score = 100

        # 긴 라인 페널티
        if quality["long_lines"] > 0:
            score -= min(20, quality["long_lines"] * 2)

        # 주석 부족 페널티
        comment_ratio = quality["comment_lines"] / max(1, quality["total_lines"])
        if comment_ratio < 0.1:
            score -= 10

        # TODO/FIXME 페널티
        score -= min(10, quality["todo_count"] * 2)

        # 타입 힌트 보너스
        if quality["has_type_hints"]:
            score += 5

        # Docstring 보너스
        if quality["has_docstrings"]:
            score += 5

        quality["quality_score"] = max(0, min(100, score))

        return quality

    def _analyze_dependencies(self, code: str) -> Dict:
        """의존성 분석"""
        try:
            tree = ast.parse(code)

            dependencies = {
                "imports": [],
                "from_imports": [],
                "standard_lib": [],
                "third_party": [],
                "local": [],
            }

            standard_libs = {
                "os",
                "sys",
                "json",
                "datetime",
                "pathlib",
                "typing",
                "ast",
                "inspect",
                "hashlib",
                "sqlite3",
                "importlib",
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies["imports"].append(alias.name)
                        if alias.name in standard_libs:
                            dependencies["standard_lib"].append(alias.name)
                        elif alias.name.startswith("."):
                            dependencies["local"].append(alias.name)
                        else:
                            dependencies["third_party"].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    dependencies["from_imports"].append(
                        {"module": module, "names": [alias.name for alias in node.names]}
                    )

                    if module in standard_libs or module.split(".")[0] in standard_libs:
                        dependencies["standard_lib"].append(module)
                    elif module.startswith("."):
                        dependencies["local"].append(module)
                    else:
                        dependencies["third_party"].append(module)

            return dependencies

        except SyntaxError:
            return {"error": "Cannot analyze dependencies due to syntax errors"}

    def _suggest_improvements(self, analysis: Dict) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 구조 기반 제안
        if "structure" in analysis:
            struct = analysis["structure"]
            if not isinstance(struct, dict) or "error" not in struct:
                if struct.get("docstring_count", 0) == 0:
                    suggestions.append("Add docstrings to classes and functions")
                if len(struct.get("functions", [])) > 10:
                    suggestions.append("Consider splitting into multiple modules")
                if len(struct.get("global_variables", [])) > 5:
                    suggestions.append("Reduce global variables, use classes or functions")

        # 복잡도 기반 제안
        if "complexity" in analysis:
            comp = analysis["complexity"]
            if not isinstance(comp, dict) or "error" not in comp:
                if comp.get("cyclomatic_complexity", 0) > 10:
                    suggestions.append("Reduce complexity by extracting functions")
                if comp.get("nesting_depth", 0) > 4:
                    suggestions.append("Reduce nesting depth for better readability")

        # 품질 기반 제안
        if "quality" in analysis:
            qual = analysis["quality"]
            if qual.get("long_lines", 0) > 0:
                suggestions.append(f"Fix {qual['long_lines']} lines exceeding 79 characters")
            if qual.get("todo_count", 0) > 0:
                suggestions.append(f"Address {qual['todo_count']} TODO/FIXME comments")
            if not qual.get("has_type_hints"):
                suggestions.append("Add type hints for better code clarity")

        return suggestions

    def _is_nested(self, node, tree) -> bool:
        """노드가 중첩되어 있는지 확인"""
        for parent in ast.walk(tree):
            if parent != node:
                for child in ast.iter_child_nodes(parent):
                    if child == node and isinstance(parent, (ast.ClassDef, ast.FunctionDef)):
                        return True
        return False

    def get_capabilities(self) -> List[str]:
        return [
            "code_analysis",
            "structure_analysis",
            "complexity_calculation",
            "quality_assessment",
            "dependency_extraction",
            "improvement_suggestions",
            "ast_parsing",
        ]
