"""
Code Validator for Agent Registration
Comprehensive Python code validation and security checks
"""

import ast
import asyncio
import hashlib
import logging
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CodeMetrics:
    """Code complexity metrics"""

    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    maintainability_index: float
    number_of_functions: int
    number_of_classes: int
    imports_count: int
    docstring_coverage: float


class CodeValidator:
    """Comprehensive code validator for agent registration"""

    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        (r"eval\s*\(", "Use of eval() is prohibited for security reasons"),
        (r"exec\s*\(", "Use of exec() is prohibited for security reasons"),
        (r"__import__\s*\(", "Dynamic imports are not allowed"),
        (r"compile\s*\(", "Use of compile() is prohibited"),
        (r"globals\s*\(\s*\)", "Access to globals() is restricted"),
        (r"locals\s*\(\s*\)", "Access to locals() is restricted"),
        (r'open\s*\([^)]*["\']w["\']', "File write operations are restricted"),
        (r"os\.system\s*\(", "System calls are not allowed"),
        (r"subprocess\.", "Subprocess operations are not allowed"),
        (r"\__builtins\__", "Access to __builtins__ is restricted"),
        (r"setattr\s*\(", "Dynamic attribute setting is restricted"),
        (r"delattr\s*\(", "Dynamic attribute deletion is restricted"),
    ]

    # Required methods for agents
    REQUIRED_METHODS = ["__init__", "execute", "get_capabilities"]

    # Allowed imports (whitelist)
    ALLOWED_IMPORTS = [
        "json",
        "datetime",
        "typing",
        "dataclasses",
        "enum",
        "collections",
        "itertools",
        "functools",
        "math",
        "random",
        "re",
        "string",
        "hashlib",
        "base64",
        "urllib.parse",
        "numpy",
        "pandas",
        "requests",
        "aiohttp",
        "asyncio",
    ]

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []

    async def validate(self, code: str) -> "ValidationResult":
        """Validate agent code comprehensively"""
        from src.api.v1.models.agent_models import ValidationResult

        self.errors = []
        self.warnings = []
        self.suggestions = []

        # Step 1: Syntax validation
        if not self._validate_syntax(code):
            return ValidationResult(
                is_valid=False,
                errors=self.errors,
                warnings=self.warnings,
                suggestions=self.suggestions,
            )

        # Step 2: Security validation
        self._validate_security(code)

        # Step 3: Structure validation
        self._validate_structure(code)

        # Step 4: Import validation
        self._validate_imports(code)

        # Step 5: Complexity analysis
        metrics = self._analyze_complexity(code)

        # Step 6: Best practices check
        self._check_best_practices(code)

        # Step 7: Type hints validation
        self._validate_type_hints(code)

        # Step 8: Docstring validation
        self._validate_docstrings(code)

        # Determine if code is valid
        is_valid = len(self.errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            suggestions=self.suggestions,
            metrics={
                "lines_of_code": metrics.lines_of_code if metrics else 0,
                "complexity": metrics.cyclomatic_complexity if metrics else 0,
                "maintainability": metrics.maintainability_index if metrics else 0,
            },
        )

    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            return False
        except Exception as e:
            self.errors.append(f"Failed to parse code: {str(e)}")
            return False

    def _validate_security(self, code: str):
        """Check for security vulnerabilities"""
        for pattern, message in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                self.errors.append(f"Security violation: {message}")

        # Check for potential SQL injection
        if "SELECT" in code.upper() or "INSERT" in code.upper():
            if not re.search(r"\?|%s|:\w+", code):  # No parameterized queries
                self.warnings.append("Use parameterized queries to prevent SQL injection")

        # Check for hardcoded secrets
        secret_patterns = [
            (
                r'["\']\w*[Kk][Ee][Yy]\w*["\']\s*[:=]\s*["\'][^"\'\']{20,}["\']',
                "Potential hardcoded API key detected",
            ),
            (
                r'["\']\w*[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]\w*["\']\s*[:=]\s*["\'][^"\'\']+["\']',
                "Hardcoded password detected",
            ),
            (
                r'["\']\w*[Tt][Oo][Kk][Ee][Nn]\w*["\']\s*[:=]\s*["\'][^"\'\']{20,}["\']',
                "Potential hardcoded token detected",
            ),
        ]

        for pattern, message in secret_patterns:
            if re.search(pattern, code):
                self.errors.append(f"Security violation: {message}")

    def _validate_structure(self, code: str):
        """Validate code structure and required components"""
        try:
            tree = ast.parse(code)

            # Find all class definitions
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            if not classes:
                self.errors.append("No class definition found. Agent must be defined as a class.")
                return

            # Check for required methods in the main class
            main_class = classes[0]  # Assume first class is the agent
            method_names = [
                node.name for node in main_class.body if isinstance(node, ast.FunctionDef)
            ]

            for required_method in self.REQUIRED_METHODS:
                if required_method not in method_names:
                    self.errors.append(f"Missing required method: {required_method}")

            # Check execute method signature
            execute_methods = [
                node
                for node in main_class.body
                if isinstance(node, ast.FunctionDef) and node.name == "execute"
            ]

            if execute_methods:
                execute_method = execute_methods[0]
                # Check if it's async
                if isinstance(execute_method, ast.AsyncFunctionDef):
                    self.suggestions.append(
                        "execute() method is async - ensure proper async handling"
                    )

                # Check parameters
                args = execute_method.args
                if len(args.args) < 2:  # self + at least one parameter
                    self.warnings.append("execute() method should accept input parameters")

        except Exception as e:
            self.errors.append(f"Failed to analyze code structure: {str(e)}")

    def _validate_imports(self, code: str):
        """Validate import statements"""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split(".")[0]
                        if module not in self.ALLOWED_IMPORTS:
                            self.warnings.append(f"Import '{module}' is not in the allowed list")

                elif isinstance(node, ast.ImportFrom):
                    module = node.module.split(".")[0] if node.module else ""
                    if module and module not in self.ALLOWED_IMPORTS:
                        self.warnings.append(f"Import from '{module}' is not in the allowed list")

        except Exception as e:
            self.warnings.append(f"Could not validate imports: {str(e)}")

    def _analyze_complexity(self, code: str) -> Optional[CodeMetrics]:
        """Analyze code complexity metrics"""
        try:
            tree = ast.parse(code)

            # Count lines
            lines_of_code = len(code.splitlines())

            # Count functions and classes
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [
                node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
            ]

            # Calculate cyclomatic complexity (simplified)
            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

            # Calculate docstring coverage
            total_definitions = len(functions) + len(classes)
            documented = sum(
                1 for node in functions + classes if ast.get_docstring(node) is not None
            )
            docstring_coverage = (
                (documented / total_definitions * 100) if total_definitions > 0 else 0
            )

            # Maintainability index (simplified formula)
            maintainability_index = max(
                0, min(100, 171 - 5.2 * (complexity / 10) - 0.23 * lines_of_code)
            )

            metrics = CodeMetrics(
                lines_of_code=lines_of_code,
                cyclomatic_complexity=complexity,
                cognitive_complexity=complexity,  # Simplified
                maintainability_index=maintainability_index,
                number_of_functions=len(functions),
                number_of_classes=len(classes),
                imports_count=len(imports),
                docstring_coverage=docstring_coverage,
            )

            # Add warnings based on metrics
            if complexity > 10:
                self.warnings.append(
                    f"High cyclomatic complexity: {complexity}. Consider refactoring."
                )

            if lines_of_code > 500:
                self.warnings.append(
                    f"Large file: {lines_of_code} lines. Consider splitting into modules."
                )

            if docstring_coverage < 50:
                self.suggestions.append(
                    f"Low docstring coverage: {docstring_coverage:.1f}%. Add more documentation."
                )

            return metrics

        except Exception as e:
            self.warnings.append(f"Could not analyze complexity: {str(e)}")
            return None

    def _check_best_practices(self, code: str):
        """Check Python best practices"""
        # Check for proper exception handling
        if "except:" in code or "except Exception:" in code:
            self.warnings.append(
                "Avoid bare except or catching Exception. Be specific about exceptions."
            )

        # Check for logging
        if "print(" in code:
            self.suggestions.append("Consider using logging instead of print statements")

        # Check for magic numbers
        if re.search(r"[^0-9]\d{3,}[^0-9]", code):
            self.suggestions.append("Consider using named constants instead of magic numbers")

        # Check for TODO comments
        if "TODO" in code or "FIXME" in code:
            self.warnings.append("Unfinished code detected (TODO/FIXME comments)")

        # Check for proper resource management
        if "open(" in code and "with" not in code:
            self.warnings.append("Use context managers (with statement) for file operations")

    def _validate_type_hints(self, code: str):
        """Validate type hints usage"""
        try:
            tree = ast.parse(code)

            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            functions_without_hints = 0
            for func in functions:
                if func.name != "__init__":  # Skip __init__ for type hints
                    # Check return type hint
                    if func.returns is None:
                        functions_without_hints += 1

                    # Check parameter type hints
                    for arg in func.args.args:
                        if arg.arg != "self" and arg.annotation is None:
                            functions_without_hints += 1
                            break

            if functions_without_hints > 0:
                self.suggestions.append(
                    f"{functions_without_hints} functions lack type hints. Consider adding them for better code clarity."
                )

        except Exception as e:
            logger.debug(f"Could not validate type hints: {e}")

    def _validate_docstrings(self, code: str):
        """Validate docstring presence and quality"""
        try:
            tree = ast.parse(code)

            # Check main class docstring
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            if classes:
                main_class = classes[0]
                if not ast.get_docstring(main_class):
                    self.warnings.append("Main class lacks a docstring")

            # Check critical method docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name in self.REQUIRED_METHODS and not ast.get_docstring(node):
                        self.warnings.append(f"Required method '{node.name}' lacks a docstring")

        except Exception as e:
            logger.debug(f"Could not validate docstrings: {e}")


async def validate_agent_code(code: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Convenience function for quick validation"""
    validator = CodeValidator()
    result = await validator.validate(code)

    return (
        result.is_valid,
        result.errors,
        {
            "warnings": result.warnings,
            "suggestions": result.suggestions,
            "metrics": result.metrics,
        },
    )
