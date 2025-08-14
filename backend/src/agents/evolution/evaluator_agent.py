"""EvaluatorAgent - Code evaluation and quality assessment agent"""
import ast
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List

from src.agents.evolution.base_agent import BaseEvolutionAgent


class EvaluatorAgent(BaseEvolutionAgent):
    """
    코드 평가 및 검증 에이전트
    - 개선 전후 비교
    - 품질 메트릭 측정
    - 테스트 실행
    - 성공/실패 판단
    """

    def __init__(self) -> Any:
        """Function __init__(self)"""
        super().__init__(name="EvaluatorAgent", version="1.0.0")
        self.metrics_history = []

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        코드 평가 실행
        input_data: {
            "before": "개선 전 코드/경로",
            "after": "개선 후 코드/경로",
            "criteria": ["quality", "performance", "test", "documentation"],
            "target_metrics": {"docstring_coverage": 80, "test_coverage": 70},
            "run_tests": True/False
        }
        """
        before = input_data.get("before")
        after = input_data.get("after")
        criteria = input_data.get("criteria", ["quality", "documentation"])
        target_metrics = input_data.get("target_metrics", {})
        run_tests = input_data.get("run_tests", False)
        result = {
            "timestamp": datetime.now().isoformat(),
            "evaluation": {},
            "metrics": {"before": {}, "after": {}, "improvement": {}},
            "success": False,
            "score": 0.0,
            "recommendations": [],
        }
        if before:
            result["metrics"]["before"] = await self._collect_metrics(before, criteria)
        if after:
            result["metrics"]["after"] = await self._collect_metrics(after, criteria)
        if before and after:
            result["metrics"]["improvement"] = self._calculate_improvement(
                result["metrics"]["before"], result["metrics"]["after"]
            )
        for criterion in criteria:
            if criterion == "quality":
                result["evaluation"]["quality"] = self._evaluate_quality(result["metrics"])
            elif criterion == "documentation":
                result["evaluation"]["documentation"] = self._evaluate_documentation(
                    result["metrics"]
                )
            elif criterion == "performance":
                result["evaluation"]["performance"] = await self._evaluate_performance(after)
            elif criterion == "test" and run_tests:
                result["evaluation"]["test"] = await self._run_tests(after)
        result["score"] = self._calculate_score(result["evaluation"], target_metrics)
        result["success"] = self._determine_success(result["score"], result["evaluation"])
        result["recommendations"] = self._generate_recommendations(result)
        self.metrics_history.append(
            {
                "timestamp": result["timestamp"],
                "score": result["score"],
                "success": result["success"],
            }
        )
        self.log_execution(input_data, result)
        return result

    async def _collect_metrics(self, target: str, criteria: List[str]) -> Dict:
        """코드 메트릭 수집"""
        metrics = {}
        if os.path.isfile(target):
            code = open(target, "r", encoding="utf-8").read()
            files = [target]
        elif os.path.isdir(target):
            files = self._get_python_files(target)
            code = self._aggregate_code(files)
        else:
            code = target
            files = []
        metrics["line_count"] = len(code.splitlines())
        metrics["file_count"] = len(files)
        metrics["char_count"] = len(code)
        try:
            tree = ast.parse(code)
            metrics["class_count"] = sum((1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef)))
            metrics["function_count"] = sum(
                (1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
            )
            metrics["import_count"] = sum(
                (1 for _ in ast.walk(tree) if isinstance(_, (ast.Import, ast.ImportFrom)))
            )
            docstring_stats = self._analyze_docstrings(tree)
            metrics.update(docstring_stats)
            complexity_stats = self._analyze_complexity(tree)
            metrics.update(complexity_stats)
        except SyntaxError:
            metrics["parse_error"] = True
        quality_metrics = self._analyze_code_quality(code)
        metrics.update(quality_metrics)
        if "test" in criteria:
            test_metrics = await self._analyze_test_coverage(files)
            metrics.update(test_metrics)
        return metrics

    def _analyze_docstrings(self, tree: ast.AST) -> Dict:
        """Docstring 분석"""
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1
            elif isinstance(node, ast.ClassDef):
                total_classes += 1
                if ast.get_docstring(node):
                    documented_classes += 1
        total_items = total_functions + total_classes
        documented_items = documented_functions + documented_classes
        return {
            "total_functions": total_functions,
            "documented_functions": documented_functions,
            "total_classes": total_classes,
            "documented_classes": documented_classes,
            "docstring_coverage": documented_items / max(1, total_items) * 100,
            "function_doc_rate": documented_functions / max(1, total_functions) * 100,
            "class_doc_rate": documented_classes / max(1, total_classes) * 100,
        }

    def _analyze_complexity(self, tree: ast.AST) -> Dict:
        """복잡도 분석"""
        complexity = {"cyclomatic_complexity": 1, "max_nesting": 0, "avg_function_length": 0}
        function_lengths = []

        def analyze_node(node, depth=0) -> Any:
            """Function analyze_node(node, depth)"""
            nonlocal complexity
            complexity["max_nesting"] = max(complexity["max_nesting"], depth)
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity["cyclomatic_complexity"] += 1
            elif isinstance(node, ast.Try):
                complexity["cyclomatic_complexity"] += len(node.handlers)
            if isinstance(node, ast.FunctionDef):
                function_lengths.append(len(node.body))
            for child in ast.iter_child_nodes(node):
                analyze_node(child, depth + 1)

        analyze_node(tree)
        if function_lengths:
            complexity["avg_function_length"] = sum(function_lengths) / len(function_lengths)
        return complexity

    def _analyze_code_quality(self, code: str) -> Dict:
        """코드 품질 분석"""
        lines = code.splitlines()
        return {
            "blank_lines": sum((1 for line in lines if not line.strip())),
            "comment_lines": sum((1 for line in lines if line.strip().startswith("#"))),
            "long_lines": sum((1 for line in lines if len(line) > 79)),
            "todo_count": sum((1 for line in lines if "TODO" in line or "FIXME" in line)),
            "type_hints_present": "Optional[" in code
            or "List[" in code
            or "Dict[" in code
            or ("->" in code),
            "uses_f_strings": 'f"' in code or "f'" in code,
            "has_main_guard": 'if __name__ == "__main__"' in code,
        }

    async def _analyze_test_coverage(self, files: List[str]) -> Dict:
        """테스트 커버리지 분석 (간단한 추정)"""
        test_files = [f for f in files if "test_" in os.path.basename(f) or "_test.py" in f]
        source_files = [f for f in files if f not in test_files]
        return {
            "test_file_count": len(test_files),
            "source_file_count": len(source_files),
            "test_to_source_ratio": len(test_files) / max(1, len(source_files)),
            "has_tests": len(test_files) > 0,
        }

    def _calculate_improvement(self, before: Dict, after: Dict) -> Dict:
        """개선도 계산"""
        improvement = {}
        for key in before:
            if key in after and isinstance(before[key], (int, float)):
                before_val = before[key]
                after_val = after[key]
                if before_val != 0:
                    change_pct = (after_val - before_val) / before_val * 100
                else:
                    change_pct = 100 if after_val > 0 else 0
                improvement[f"{key}_change"] = round(change_pct, 2)
                improvement[f"{key}_improved"] = after_val > before_val
        if "docstring_coverage" in before and "docstring_coverage" in after:
            improvement["documentation_improved"] = (
                after["docstring_coverage"] > before["docstring_coverage"]
            )
            improvement["documentation_delta"] = (
                after["docstring_coverage"] - before["docstring_coverage"]
            )
        if "cyclomatic_complexity" in before and "cyclomatic_complexity" in after:
            improvement["complexity_improved"] = (
                after["cyclomatic_complexity"] <= before["cyclomatic_complexity"]
            )
            improvement["complexity_delta"] = (
                before["cyclomatic_complexity"] - after["cyclomatic_complexity"]
            )
        return improvement

    def _evaluate_quality(self, metrics: Dict) -> Dict:
        """품질 평가"""
        evaluation = {"score": 0, "issues": [], "strengths": []}
        after_metrics = metrics.get("after", {})
        complexity = after_metrics.get("cyclomatic_complexity", 0)
        if complexity <= 10:
            evaluation["score"] += 20
            evaluation["strengths"].append("Low complexity")
        else:
            evaluation["issues"].append(f"High complexity: {complexity}")
        if after_metrics.get("long_lines", 0) == 0:
            evaluation["score"] += 10
            evaluation["strengths"].append("No long lines")
        else:
            evaluation["issues"].append(f"{after_metrics['long_lines']} long lines")
        if after_metrics.get("todo_count", 0) == 0:
            evaluation["score"] += 10
            evaluation["strengths"].append("No TODOs")
        else:
            evaluation["issues"].append(f"{after_metrics['todo_count']} TODOs remaining")
        if after_metrics.get("type_hints_present", False):
            evaluation["score"] += 15
            evaluation["strengths"].append("Uses type hints")
        else:
            evaluation["issues"].append("No type hints")
        return evaluation

    def _evaluate_documentation(self, metrics: Dict) -> Dict:
        """문서화 평가"""
        evaluation = {"score": 0, "coverage": 0, "issues": [], "strengths": []}
        after_metrics = metrics.get("after", {})
        improvement = metrics.get("improvement", {})
        coverage = after_metrics.get("docstring_coverage", 0)
        evaluation["coverage"] = coverage
        if coverage >= 80:
            evaluation["score"] = 40
            evaluation["strengths"].append(f"Excellent documentation: {coverage:.1f}%")
        elif coverage >= 60:
            evaluation["score"] = 30
            evaluation["strengths"].append(f"Good documentation: {coverage:.1f}%")
        elif coverage >= 40:
            evaluation["score"] = 20
            evaluation["issues"].append(f"Moderate documentation: {coverage:.1f}%")
        else:
            evaluation["score"] = 10
            evaluation["issues"].append(f"Poor documentation: {coverage:.1f}%")
        if improvement.get("documentation_improved", False):
            evaluation["score"] += 10
            evaluation["strengths"].append(
                f"Documentation improved by {improvement.get('documentation_delta', 0):.1f}%"
            )
        return evaluation

    async def _evaluate_performance(self, code: str) -> Dict:
        """성능 평가 (간단한 추정)"""
        evaluation = {"score": 0, "estimated_complexity": "O(n)", "issues": [], "strengths": []}
        if "for" in code and "for" in code[code.index("for") + 3 :]:
            evaluation["estimated_complexity"] = "O(n²) or higher"
            evaluation["issues"].append("Nested loops detected")
        else:
            evaluation["score"] += 20
            evaluation["strengths"].append("No obvious performance issues")
        return evaluation

    async def _run_tests(self, target: str) -> Dict:
        """테스트 실행"""
        evaluation = {"score": 0, "passed": 0, "failed": 0, "errors": []}
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", target, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            if "passed" in output:
                import re

                match = re.search("(\\d+) passed", output)
                if match:
                    evaluation["passed"] = int(match.group(1))
                    evaluation["score"] = min(40, evaluation["passed"] * 10)
            if "failed" in output:
                match = re.search("(\\d+) failed", output)
                if match:
                    evaluation["failed"] = int(match.group(1))
                    evaluation["score"] = max(0, evaluation["score"] - evaluation["failed"] * 5)
            if result.returncode != 0:
                evaluation["errors"].append("Some tests failed")
        except subprocess.TimeoutExpired:
            evaluation["errors"].append("Test timeout")
        except Exception as e:
            evaluation["errors"].append(str(e))
        return evaluation

    def _calculate_score(self, evaluation: Dict, target_metrics: Dict) -> float:
        """종합 점수 계산"""
        total_score = 0
        total_weight = 0
        weights = {"quality": 0.3, "documentation": 0.3, "performance": 0.2, "test": 0.2}
        for criterion, weight in weights.items():
            if criterion in evaluation:
                score = evaluation[criterion].get("score", 0)
                total_score += score * weight
                total_weight += weight
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0
        if target_metrics:
            achievement_score = self._calculate_target_achievement(evaluation, target_metrics)
            normalized_score = (normalized_score + achievement_score) / 2
        return round(normalized_score, 2)

    def _calculate_target_achievement(self, evaluation: Dict, targets: Dict) -> float:
        """목표 달성도 계산"""
        achievements = []
        if "docstring_coverage" in targets:
            actual = evaluation.get("documentation", {}).get("coverage", 0)
            target = targets["docstring_coverage"]
            achievement = min(100, actual / target * 100)
            achievements.append(achievement)
        return sum(achievements) / len(achievements) if achievements else 0

    def _determine_success(self, score: float, evaluation: Dict) -> bool:
        """성공 여부 판단"""
        if score >= 70:
            return True
        critical_issues = []
        for criterion in evaluation.values():
            if isinstance(criterion, dict):
                issues = criterion.get("issues", [])
                critical_issues.extend([i for i in issues if "error" in i.lower()])
        if not critical_issues and score >= 50:
            return True
        return False

    def _generate_recommendations(self, result: Dict) -> List[str]:
        """개선 추천사항 생성"""
        recommendations = []
        metrics = result.get("metrics", {}).get("after", {})
        evaluation = result.get("evaluation", {})
        if metrics.get("docstring_coverage", 0) < 80:
            recommendations.append(
                f"Increase docstring coverage from {metrics.get('docstring_coverage', 0):.1f}% to 80%"
            )
        if metrics.get("cyclomatic_complexity", 0) > 10:
            recommendations.append("Reduce cyclomatic complexity by extracting functions")
        quality_issues = evaluation.get("quality", {}).get("issues", [])
        for issue in quality_issues[:3]:
            recommendations.append(f"Fix: {issue}")
        if not metrics.get("has_tests", False):
            recommendations.append("Add unit tests")
        return recommendations

    def _get_python_files(self, directory: str) -> List[str]:
        """Python 파일 목록 가져오기"""
        python_files = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files

    def _aggregate_code(self, files: List[str]) -> str:
        """여러 파일의 코드를 하나로 합치기"""
        aggregated = []
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    aggregated.append(f.read())
            except Exception:
                pass
        return "\n\n".join(aggregated)

    def get_capabilities(self) -> List[str]:
        """Function get_capabilities(self)"""
        return [
            "code_evaluation",
            "quality_assessment",
            "documentation_analysis",
            "performance_estimation",
            "test_execution",
            "metric_comparison",
            "improvement_tracking",
            "success_determination",
            "recommendation_generation",
        ]
