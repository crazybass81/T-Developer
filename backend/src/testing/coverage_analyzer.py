"""CoverageAnalyzer - Day 34
Test coverage analysis - Size: ~6.5KB"""
import ast
import os
from typing import Any, Dict, List, Tuple


class CoverageAnalyzer:
    """Analyze test coverage - Size optimized to 6.5KB"""

    def __init__(self):
        self.metrics = {
            "lines": 0,
            "covered": 0,
            "functions": 0,
            "tested": 0,
            "branches": 0,
            "covered_branches": 0,
        }

    def analyze_file(self, file_path: str, test_path: str = None) -> Dict[str, Any]:
        """Analyze single file coverage"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        with open(file_path, "r") as f:
            code = f.read()

        test_code = ""
        if test_path and os.path.exists(test_path):
            with open(test_path, "r") as f:
                test_code = f.read()

        return self.analyze_code(code, test_code)

    def analyze_code(self, code: str, test_code: str = "") -> Dict[str, Any]:
        """Analyze code coverage"""
        try:
            tree = ast.parse(code)
        except:
            return {"error": "Parse error"}

        # Analyze source
        funcs = []
        classes = []
        lines = len(code.split("\n"))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        # Analyze tests
        tested = []
        if test_code:
            try:
                test_tree = ast.parse(test_code)
                for node in ast.walk(test_tree):
                    if isinstance(node, ast.FunctionDef):
                        # Extract tested function from test name
                        if node.name.startswith("test_"):
                            tested.append(node.name[5:])
            except:
                pass

        # Calculate coverage
        func_coverage = len(tested) / max(len(funcs), 1) * 100

        return {
            "lines": lines,
            "functions": len(funcs),
            "classes": len(classes),
            "tested_functions": len(tested),
            "function_coverage": round(func_coverage, 1),
            "untested": [f for f in funcs if f not in tested][:10],  # Limit to 10
        }

    def analyze_directory(self, dir_path: str) -> Dict[str, Any]:
        """Analyze directory coverage"""
        results = {
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "tested_functions": 0,
            "coverage": 0.0,
        }

        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    file_path = os.path.join(root, file)
                    test_path = os.path.join(root, f"test_{file}")

                    analysis = self.analyze_file(file_path, test_path)
                    if "error" not in analysis:
                        results["total_files"] += 1
                        results["total_lines"] += analysis["lines"]
                        results["total_functions"] += analysis["functions"]
                        results["tested_functions"] += analysis["tested_functions"]

        if results["total_functions"] > 0:
            results["coverage"] = round(
                results["tested_functions"] / results["total_functions"] * 100, 1
            )

        return results

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate coverage report"""
        report = f"""Coverage Report
===============
Files: {analysis.get("total_files", 0)}
Lines: {analysis.get("total_lines", 0)}
Functions: {analysis.get("total_functions", 0)}
Tested: {analysis.get("tested_functions", 0)}
Coverage: {analysis.get("coverage", 0)}%

"""

        if "untested" in analysis and analysis["untested"]:
            report += "Untested Functions:\n"
            for func in analysis["untested"][:5]:  # Limit display
                report += f"  - {func}\n"

        return report

    def find_gaps(self, code: str) -> List[str]:
        """Find coverage gaps"""
        gaps = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for error handling
                    has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
                    if not has_try:
                        gaps.append(f"{node.name}: No error handling")

                    # Check for return
                    has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                    if not has_return and node.name != "__init__":
                        gaps.append(f"{node.name}: No return statement")
        except:
            gaps.append("Parse error")

        return gaps[:10]  # Limit results
