# backend/src/agents/implementations/generation_validator.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ast
import re

class ValidationLevel(Enum):
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"

@dataclass
class ValidationResult:
    level: ValidationLevel
    passed: bool
    issues: List[str]
    suggestions: List[str]
    score: float

class CodeValidator:
    """Comprehensive code validation system"""

    def __init__(self):
        self.syntax_validator = SyntaxValidator()
        self.security_validator = SecurityValidator()
        self.performance_validator = PerformanceValidator()
        self.style_validator = StyleValidator()

    async def validate_code(
        self,
        code: str,
        language: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, ValidationResult]:
        """Comprehensive code validation"""

        results = {}

        # Syntax validation
        results['syntax'] = await self.syntax_validator.validate(code, language)

        # Security validation
        results['security'] = await self.security_validator.validate(code, language)

        # Performance validation
        results['performance'] = await self.performance_validator.validate(code, language)

        # Style validation
        results['style'] = await self.style_validator.validate(code, language)

        # Requirements compliance
        results['requirements'] = await self._validate_requirements_compliance(
            code, requirements
        )

        return results

    async def _validate_requirements_compliance(
        self,
        code: str,
        requirements: Dict[str, Any]
    ) -> ValidationResult:
        """Validate code against requirements"""

        issues = []
        suggestions = []
        
        # Check if required functions are implemented
        required_functions = requirements.get('functions', [])
        for func in required_functions:
            if func not in code:
                issues.append(f"Required function '{func}' not found")
                suggestions.append(f"Implement the '{func}' function")

        # Check if required imports are present
        required_imports = requirements.get('imports', [])
        for imp in required_imports:
            if imp not in code:
                issues.append(f"Required import '{imp}' not found")
                suggestions.append(f"Add import: {imp}")

        passed = len(issues) == 0
        score = 1.0 if passed else max(0.0, 1.0 - (len(issues) * 0.2))

        return ValidationResult(
            level=ValidationLevel.SEMANTIC,
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

class SyntaxValidator:
    """Syntax validation for different languages"""

    async def validate(self, code: str, language: str) -> ValidationResult:
        """Validate syntax based on language"""

        if language.lower() == 'python':
            return await self._validate_python_syntax(code)
        elif language.lower() in ['javascript', 'typescript']:
            return await self._validate_js_syntax(code)
        else:
            return ValidationResult(
                level=ValidationLevel.SYNTAX,
                passed=True,
                issues=[],
                suggestions=[],
                score=1.0
            )

    async def _validate_python_syntax(self, code: str) -> ValidationResult:
        """Validate Python syntax"""
        issues = []
        suggestions = []

        try:
            ast.parse(code)
            passed = True
            score = 1.0
        except SyntaxError as e:
            passed = False
            issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
            suggestions.append("Fix syntax error before proceeding")
            score = 0.0

        return ValidationResult(
            level=ValidationLevel.SYNTAX,
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    async def _validate_js_syntax(self, code: str) -> ValidationResult:
        """Validate JavaScript/TypeScript syntax"""
        issues = []
        suggestions = []

        # Basic syntax checks
        bracket_balance = self._check_bracket_balance(code)
        if not bracket_balance['balanced']:
            issues.append("Unbalanced brackets detected")
            suggestions.append("Check bracket pairing")

        # Check for common syntax issues
        if code.count('"') % 2 != 0:
            issues.append("Unmatched quotes detected")
            suggestions.append("Check quote pairing")

        passed = len(issues) == 0
        score = 1.0 if passed else 0.5

        return ValidationResult(
            level=ValidationLevel.SYNTAX,
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def _check_bracket_balance(self, code: str) -> Dict[str, Any]:
        """Check if brackets are balanced"""
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        
        for char in code:
            if char in pairs:
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return {'balanced': False, 'error': f"Unmatched closing bracket: {char}"}
                if pairs[stack.pop()] != char:
                    return {'balanced': False, 'error': f"Mismatched bracket: {char}"}
        
        balanced = len(stack) == 0
        return {'balanced': balanced, 'error': None if balanced else "Unclosed brackets"}

class SecurityValidator:
    """Security validation for generated code"""

    def __init__(self):
        self.security_patterns = {
            'python': [
                (r'eval\s*\(', 'Avoid using eval() - security risk'),
                (r'exec\s*\(', 'Avoid using exec() - security risk'),
                (r'os\.system\s*\(', 'Avoid os.system() - use subprocess instead'),
                (r'input\s*\([^)]*\)', 'Validate user input properly'),
                (r'pickle\.loads?\s*\(', 'Pickle can be unsafe - consider alternatives')
            ],
            'javascript': [
                (r'eval\s*\(', 'Avoid using eval() - security risk'),
                (r'innerHTML\s*=', 'Use textContent or sanitize HTML'),
                (r'document\.write\s*\(', 'Avoid document.write - XSS risk'),
                (r'setTimeout\s*\(\s*["\']', 'Avoid string-based setTimeout'),
                (r'new Function\s*\(', 'Avoid Function constructor')
            ]
        }

    async def validate(self, code: str, language: str) -> ValidationResult:
        """Validate security aspects"""
        
        issues = []
        suggestions = []
        
        patterns = self.security_patterns.get(language.lower(), [])
        
        for pattern, message in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                issues.append(f"Security issue: {message}")
                suggestions.append(f"Review and fix: {message}")

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]

        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("Potential hardcoded secret detected")
                suggestions.append("Use environment variables for secrets")

        passed = len(issues) == 0
        score = max(0.0, 1.0 - (len(issues) * 0.3))

        return ValidationResult(
            level=ValidationLevel.SECURITY,
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

class PerformanceValidator:
    """Performance validation for generated code"""

    async def validate(self, code: str, language: str) -> ValidationResult:
        """Validate performance aspects"""
        
        issues = []
        suggestions = []

        # Check for performance anti-patterns
        if language.lower() == 'python':
            issues.extend(self._check_python_performance(code))
        elif language.lower() in ['javascript', 'typescript']:
            issues.extend(self._check_js_performance(code))

        # Generate suggestions based on issues
        for issue in issues:
            if 'loop' in issue.lower():
                suggestions.append("Consider optimizing loops or using vectorized operations")
            elif 'memory' in issue.lower():
                suggestions.append("Review memory usage and consider cleanup")

        passed = len(issues) == 0
        score = max(0.0, 1.0 - (len(issues) * 0.2))

        return ValidationResult(
            level=ValidationLevel.PERFORMANCE,
            passed=passed,
            issues=issues,
            suggestions=suggestions,
            score=score
        )

    def _check_python_performance(self, code: str) -> List[str]:
        """Check Python-specific performance issues"""
        issues = []
        
        # Check for inefficient patterns
        if re.search(r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', code):
            issues.append("Use enumerate() instead of range(len())")
        
        if '+=' in code and 'str' in code:
            issues.append("String concatenation in loop - consider join()")
        
        return issues

    def _check_js_performance(self, code: str) -> List[str]:
        """Check JavaScript-specific performance issues"""
        issues = []
        
        # Check for DOM queries in loops
        if re.search(r'for\s*\([^)]*\)\s*{[^}]*document\.', code):
            issues.append("DOM queries in loop - cache selectors")
        
        return issues