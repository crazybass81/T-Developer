"""QualityEvaluator - Day 42
Code quality evaluation across multiple dimensions - Size: ~6.5KB"""
import ast
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class QualityEvaluator:
    """Evaluate code quality across multiple dimensions - Size optimized to 6.5KB"""

    def __init__(self):
        self.quality_dimensions = self._initialize_dimensions()
        self.patterns = self._initialize_patterns()
        self.weights = self._initialize_weights()
        self.history = {}
        self.standards = self._initialize_standards()

    def _initialize_dimensions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality dimensions"""
        return {
            "maintainability": {
                "metrics": ["complexity", "duplication", "coupling"],
                "weight": 0.25,
                "threshold": 70,
            },
            "reliability": {
                "metrics": ["error_handling", "test_coverage", "assertions"],
                "weight": 0.25,
                "threshold": 80,
            },
            "security": {
                "metrics": ["vulnerabilities", "input_validation", "encryption"],
                "weight": 0.2,
                "threshold": 90,
            },
            "documentation": {
                "metrics": ["docstrings", "comments", "type_hints"],
                "weight": 0.15,
                "threshold": 60,
            },
            "best_practices": {
                "metrics": ["naming", "structure", "patterns"],
                "weight": 0.15,
                "threshold": 70,
            },
        }

    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize code patterns for analysis"""
        return {
            "docstring": re.compile(r'""".*?"""', re.DOTALL),
            "comment": re.compile(r"#.*$", re.MULTILINE),
            "type_hint": re.compile(r":\s*[A-Z]\w+(\[.*?\])?"),
            "error_handling": re.compile(r"\btry\b.*?\bexcept\b", re.DOTALL),
            "input_validation": re.compile(
                r"if\s+.*?(is\s+None|isinstance|hasattr|len\(|\.strip\()"
            ),
            "hardcoded_secret": re.compile(
                r'(password|api_key|secret|token)\s*=\s*["\'].*?["\']', re.IGNORECASE
            ),
            "sql_injection": re.compile(r"(execute|query)\s*\(.*?%s.*?\)", re.DOTALL),
            "camel_case": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
            "snake_case": re.compile(r"^[a-z][a-z0-9_]*$"),
            "constant_case": re.compile(r"^[A-Z][A-Z0-9_]*$"),
        }

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize metric weights"""
        return {
            "complexity": 0.4,
            "duplication": 0.3,
            "coupling": 0.3,
            "error_handling": 0.4,
            "test_coverage": 0.35,
            "assertions": 0.25,
            "vulnerabilities": 0.5,
            "input_validation": 0.3,
            "encryption": 0.2,
            "docstrings": 0.4,
            "comments": 0.3,
            "type_hints": 0.3,
            "naming": 0.35,
            "structure": 0.35,
            "patterns": 0.3,
        }

    def _initialize_standards(self) -> Dict[str, Any]:
        """Initialize coding standards"""
        return {
            "max_complexity": 10,
            "max_function_length": 50,
            "max_class_length": 200,
            "min_test_coverage": 85,
            "max_duplication": 5,
            "min_docstring_coverage": 80,
            "max_parameters": 5,
            "max_nesting_depth": 4,
        }

    def evaluate(self, agent_id: str, code: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate code quality"""
        evaluation = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "dimensions": {},
            "overall_score": 0,
            "issues": [],
            "suggestions": [],
        }

        # Parse code if possible
        try:
            tree = ast.parse(code)
            ast_analysis = self._analyze_ast(tree)
        except SyntaxError:
            ast_analysis = None

        # Evaluate each dimension
        for dim_name, dim_config in self.quality_dimensions.items():
            dim_score = self._evaluate_dimension(dim_name, dim_config, code, ast_analysis, metadata)
            evaluation["dimensions"][dim_name] = dim_score

        # Calculate overall score
        evaluation["overall_score"] = self._calculate_overall_score(evaluation["dimensions"])

        # Identify issues
        evaluation["issues"] = self._identify_issues(code, ast_analysis)

        # Generate suggestions
        evaluation["suggestions"] = self._generate_suggestions(evaluation)

        # Store in history
        if agent_id not in self.history:
            self.history[agent_id] = []
        self.history[agent_id].append(evaluation)

        return evaluation

    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze AST for quality metrics"""
        analysis = {
            "functions": 0,
            "classes": 0,
            "max_complexity": 0,
            "max_nesting": 0,
            "total_lines": 0,
            "docstrings": 0,
            "type_hints": 0,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"] += 1
                complexity = self._calculate_complexity(node)
                analysis["max_complexity"] = max(analysis["max_complexity"], complexity)
                if ast.get_docstring(node):
                    analysis["docstrings"] += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    analysis["type_hints"] += 1
            elif isinstance(node, ast.ClassDef):
                analysis["classes"] += 1
                if ast.get_docstring(node):
                    analysis["docstrings"] += 1

        return analysis

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _evaluate_dimension(
        self,
        dim_name: str,
        dim_config: Dict[str, Any],
        code: str,
        ast_analysis: Optional[Dict],
        metadata: Optional[Dict],
    ) -> Dict[str, Any]:
        """Evaluate a quality dimension"""
        scores = {}

        if dim_name == "maintainability":
            scores = self._evaluate_maintainability(code, ast_analysis)
        elif dim_name == "reliability":
            scores = self._evaluate_reliability(code, metadata)
        elif dim_name == "security":
            scores = self._evaluate_security(code)
        elif dim_name == "documentation":
            scores = self._evaluate_documentation(code, ast_analysis)
        elif dim_name == "best_practices":
            scores = self._evaluate_best_practices(code, ast_analysis)

        # Calculate dimension score
        total_score = 0
        total_weight = 0
        for metric, score in scores.items():
            weight = self.weights.get(metric, 1.0)
            total_score += score * weight
            total_weight += weight

        dimension_score = (total_score / total_weight) if total_weight > 0 else 50

        return {
            "score": dimension_score,
            "normalized": dimension_score / 100,
            "metrics": scores,
            "status": self._get_status(dimension_score, dim_config["threshold"]),
        }

    def _evaluate_maintainability(
        self, code: str, ast_analysis: Optional[Dict]
    ) -> Dict[str, float]:
        """Evaluate maintainability metrics"""
        scores = {}

        # Complexity
        if ast_analysis:
            max_complexity = ast_analysis.get("max_complexity", 0)
            if max_complexity <= 5:
                scores["complexity"] = 100
            elif max_complexity <= 10:
                scores["complexity"] = 75
            elif max_complexity <= 15:
                scores["complexity"] = 50
            else:
                scores["complexity"] = 25
        else:
            scores["complexity"] = 50

        # Duplication (simplified)
        lines = code.split("\n")
        unique_lines = len(set(lines))
        duplication_ratio = 1 - (unique_lines / len(lines)) if lines else 0
        scores["duplication"] = max(0, 100 - duplication_ratio * 200)

        # Coupling (simplified - count imports)
        import_count = len(re.findall(r"^import |^from ", code, re.MULTILINE))
        if import_count <= 5:
            scores["coupling"] = 100
        elif import_count <= 10:
            scores["coupling"] = 75
        elif import_count <= 15:
            scores["coupling"] = 50
        else:
            scores["coupling"] = 25

        return scores

    def _evaluate_reliability(self, code: str, metadata: Optional[Dict]) -> Dict[str, float]:
        """Evaluate reliability metrics"""
        scores = {}

        # Error handling
        try_blocks = len(self.patterns["error_handling"].findall(code))
        func_count = code.count("def ")
        if func_count > 0:
            error_coverage = min(100, (try_blocks / func_count) * 100)
            scores["error_handling"] = error_coverage
        else:
            scores["error_handling"] = 50

        # Test coverage (from metadata if available)
        if metadata and "test_coverage" in metadata:
            scores["test_coverage"] = metadata["test_coverage"]
        else:
            # Estimate based on test presence
            has_tests = "test_" in code or "assert" in code
            scores["test_coverage"] = 75 if has_tests else 25

        # Assertions
        assertion_count = code.count("assert ")
        scores["assertions"] = min(100, assertion_count * 10)

        return scores

    def _evaluate_security(self, code: str) -> Dict[str, float]:
        """Evaluate security metrics"""
        scores = {}

        # Check for vulnerabilities
        vulnerabilities = 0
        if self.patterns["hardcoded_secret"].search(code):
            vulnerabilities += 1
        if self.patterns["sql_injection"].search(code):
            vulnerabilities += 1
        if "eval(" in code or "exec(" in code:
            vulnerabilities += 1

        scores["vulnerabilities"] = max(0, 100 - vulnerabilities * 30)

        # Input validation
        validation_count = len(self.patterns["input_validation"].findall(code))
        func_count = code.count("def ")
        if func_count > 0:
            scores["input_validation"] = min(100, (validation_count / func_count) * 100)
        else:
            scores["input_validation"] = 50

        # Encryption (check for crypto imports)
        has_crypto = any(term in code for term in ["hashlib", "cryptography", "bcrypt", "secrets"])
        scores["encryption"] = 80 if has_crypto else 40

        return scores

    def _evaluate_documentation(self, code: str, ast_analysis: Optional[Dict]) -> Dict[str, float]:
        """Evaluate documentation metrics"""
        scores = {}

        # Docstrings
        if ast_analysis:
            total_items = ast_analysis["functions"] + ast_analysis["classes"]
            if total_items > 0:
                docstring_coverage = (ast_analysis["docstrings"] / total_items) * 100
                scores["docstrings"] = docstring_coverage
            else:
                scores["docstrings"] = 50
        else:
            has_docstrings = '"""' in code or "'''" in code
            scores["docstrings"] = 75 if has_docstrings else 25

        # Comments
        comment_lines = len(self.patterns["comment"].findall(code))
        total_lines = len(code.split("\n"))
        comment_ratio = (comment_lines / total_lines) * 100 if total_lines > 0 else 0
        scores["comments"] = min(100, comment_ratio * 10)

        # Type hints
        type_hint_count = len(self.patterns["type_hint"].findall(code))
        func_count = code.count("def ")
        if func_count > 0:
            scores["type_hints"] = min(100, (type_hint_count / func_count) * 50)
        else:
            scores["type_hints"] = 50

        return scores

    def _evaluate_best_practices(self, code: str, ast_analysis: Optional[Dict]) -> Dict[str, float]:
        """Evaluate best practices"""
        scores = {}

        # Naming conventions
        good_names = 0
        total_names = 0
        for line in code.split("\n"):
            if "def " in line:
                total_names += 1
                func_name = line.split("def ")[1].split("(")[0]
                if self.patterns["snake_case"].match(func_name):
                    good_names += 1
            elif "class " in line:
                total_names += 1
                class_name = line.split("class ")[1].split("(")[0].split(":")[0]
                if self.patterns["camel_case"].match(class_name):
                    good_names += 1

        scores["naming"] = (good_names / total_names * 100) if total_names > 0 else 75

        # Structure
        if ast_analysis:
            scores["structure"] = 100 if ast_analysis["max_complexity"] <= 10 else 50
        else:
            scores["structure"] = 60

        # Design patterns (simplified check)
        patterns_used = sum(
            1
            for pattern in ["@property", "@staticmethod", "@classmethod", "__init__"]
            if pattern in code
        )
        scores["patterns"] = min(100, patterns_used * 25)

        return scores

    def _get_status(self, score: float, threshold: float) -> str:
        """Get status based on score and threshold"""
        if score >= threshold:
            return "good"
        elif score >= threshold * 0.8:
            return "acceptable"
        elif score >= threshold * 0.6:
            return "warning"
        else:
            return "critical"

    def _calculate_overall_score(self, dimensions: Dict[str, Dict]) -> float:
        """Calculate overall quality score"""
        total = 0
        total_weight = 0

        for dim_name, dim_result in dimensions.items():
            if dim_name in self.quality_dimensions:
                weight = self.quality_dimensions[dim_name]["weight"]
                total += dim_result["score"] * weight
                total_weight += weight

        return total / total_weight if total_weight > 0 else 0

    def _identify_issues(self, code: str, ast_analysis: Optional[Dict]) -> List[Dict[str, Any]]:
        """Identify quality issues"""
        issues = []

        # Check complexity
        if ast_analysis and ast_analysis["max_complexity"] > self.standards["max_complexity"]:
            issues.append(
                {
                    "type": "complexity",
                    "severity": "high",
                    "description": f"Complexity exceeds limit: {ast_analysis['max_complexity']}",
                }
            )

        # Check for security issues
        if self.patterns["hardcoded_secret"].search(code):
            issues.append(
                {
                    "type": "security",
                    "severity": "critical",
                    "description": "Hardcoded secrets detected",
                }
            )

        return issues

    def _generate_suggestions(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        for dim_name, dim_result in evaluation["dimensions"].items():
            if dim_result["status"] in ["warning", "critical"]:
                if dim_name == "maintainability":
                    suggestions.append("Reduce code complexity and eliminate duplication")
                elif dim_name == "reliability":
                    suggestions.append("Add error handling and increase test coverage")
                elif dim_name == "security":
                    suggestions.append("Remove hardcoded secrets and validate inputs")
                elif dim_name == "documentation":
                    suggestions.append("Add docstrings and type hints")
                elif dim_name == "best_practices":
                    suggestions.append("Follow naming conventions and design patterns")

        return suggestions
