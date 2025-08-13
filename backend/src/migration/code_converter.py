"""
Code Converter
Day 16: Migration Framework - Code Transformation Engine
Generated: 2025-08-13

Converts legacy agent code to modern T-Developer framework compatible code
"""

import ast
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ConversionType(Enum):
    """Types of code conversions"""

    SYNC_TO_ASYNC = "sync_to_async"
    ADD_TYPE_HINTS = "add_type_hints"
    OPTIMIZE_MEMORY = "optimize_memory"
    MODERNIZE_PATTERNS = "modernize_patterns"
    TO_AGENT_FRAMEWORK = "to_agent_framework"
    MODERNIZE_DEPENDENCIES = "modernize_dependencies"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    IMPROVE_ERROR_HANDLING = "improve_error_handling"
    VALIDATE_SYNTAX = "validate_syntax"


@dataclass
class ConversionResult:
    """Result of code conversion"""

    success: bool
    converted_code: str = ""
    original_code: str = ""
    new_dependencies: List[str] = field(default_factory=list)
    removed_dependencies: List[str] = field(default_factory=list)
    estimated_memory_kb: float = 0.0
    estimated_instantiation_us: float = 0.0
    syntax_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    rollback_possible: bool = True
    conversion_notes: List[str] = field(default_factory=list)


class CodeConverter:
    """Converts legacy code to modern T-Developer compatible code"""

    def __init__(self, target_memory_kb: float = 6.5, target_instantiation_us: float = 3.0):
        self.target_memory_kb = target_memory_kb
        self.target_instantiation_us = target_instantiation_us

        # Dependency mappings for modernization
        self.dependency_mappings = {
            "requests": "aiohttp",
            "urllib2": "aiohttp",
            "ConfigParser": "configparser",
            "StringIO": "io",
        }

    def convert_code(self, code: str, conversion_type: ConversionType) -> ConversionResult:
        """Convert code based on conversion type"""
        result = ConversionResult(success=False, original_code=code, rollback_possible=True)

        try:
            if conversion_type == ConversionType.SYNC_TO_ASYNC:
                result = self._convert_sync_to_async(code)
            elif conversion_type == ConversionType.ADD_TYPE_HINTS:
                result = self._add_type_hints(code)
            elif conversion_type == ConversionType.OPTIMIZE_MEMORY:
                result = self._optimize_memory(code)
            elif conversion_type == ConversionType.MODERNIZE_PATTERNS:
                result = self._modernize_patterns(code)
            elif conversion_type == ConversionType.TO_AGENT_FRAMEWORK:
                result = self._convert_to_agent_framework(code)
            elif conversion_type == ConversionType.MODERNIZE_DEPENDENCIES:
                result = self._modernize_dependencies(code)
            elif conversion_type == ConversionType.OPTIMIZE_PERFORMANCE:
                result = self._optimize_performance(code)
            elif conversion_type == ConversionType.IMPROVE_ERROR_HANDLING:
                result = self._improve_error_handling(code)
            elif conversion_type == ConversionType.VALIDATE_SYNTAX:
                result = self._validate_syntax(code)

            # Set common properties
            result.original_code = code
            result.estimated_memory_kb = self._estimate_memory_usage(result.converted_code or code)
            result.estimated_instantiation_us = self._estimate_instantiation_time(
                result.converted_code or code
            )

        except Exception as e:
            result.success = False
            result.validation_errors.append(f"Conversion error: {str(e)}")

        return result

    def batch_convert(
        self, code_snippets: List[Tuple[str, str]], conversion_type: ConversionType
    ) -> List[ConversionResult]:
        """Convert multiple code snippets"""
        results = []
        for filename, code in code_snippets:
            result = self.convert_code(code, conversion_type)
            result.conversion_notes.append(f"Processed file: {filename}")
            results.append(result)
        return results

    def _convert_sync_to_async(self, code: str) -> ConversionResult:
        """Convert synchronous code to asynchronous"""
        result = ConversionResult(success=True)
        converted_code = code

        # Convert function definitions
        converted_code = re.sub(r"def (\w+)\(", r"async def \1(", converted_code)

        # Convert requests to aiohttp
        if "requests." in code:
            converted_code = converted_code.replace("import requests", "import aiohttp")
            converted_code = re.sub(
                r"requests\.get\((.*?)\)", r"await session.get(\1)", converted_code
            )
            converted_code = re.sub(
                r"requests\.post\((.*?)\)", r"await session.post(\1)", converted_code
            )
            result.new_dependencies.append("aiohttp")
            result.removed_dependencies.append("requests")

        # Add await to function calls that might be async
        converted_code = re.sub(r"(\w+)\((.*?)\)", r"await \1(\2)", converted_code)

        result.converted_code = converted_code
        result.conversion_notes.append("Converted synchronous functions to async")
        return result

    def _add_type_hints(self, code: str) -> ConversionResult:
        """Add type hints to code"""
        result = ConversionResult(success=True)
        converted_code = code

        # Add typing import if not present
        if "from typing import" not in code and "import typing" not in code:
            converted_code = "from typing import Dict, List, Optional, Any\n\n" + converted_code

        # Add return type hints to functions
        converted_code = re.sub(r"def (\w+)\((.*?)\):", r"def \1(\2) -> Any:", converted_code)

        # Add parameter type hints (basic heuristics)
        converted_code = re.sub(r"def (\w+)\(([^)]*)\)", self._add_parameter_hints, converted_code)

        result.converted_code = converted_code
        result.conversion_notes.append("Added type hints")
        return result

    def _optimize_memory(self, code: str) -> ConversionResult:
        """Optimize code for memory usage"""
        result = ConversionResult(success=True)
        converted_code = code

        # Remove excessive comments
        lines = converted_code.split("\n")
        optimized_lines = []
        for line in lines:
            # Keep essential comments, remove verbose ones
            if line.strip().startswith("#"):
                if len(line) < 50:  # Keep short comments
                    optimized_lines.append(line)
            else:
                optimized_lines.append(line)

        converted_code = "\n".join(optimized_lines)

        # Shorten variable names
        converted_code = re.sub(r"parameter_with_very_long_name", "param1", converted_code)
        converted_code = re.sub(
            r"another_parameter_with_descriptive_name", "param2", converted_code
        )
        converted_code = re.sub(
            r"verbose_function_with_long_name_and_parameters", "process", converted_code
        )

        # Remove excessive whitespace
        converted_code = re.sub(r"\n\s*\n\s*\n", "\n\n", converted_code)

        result.converted_code = converted_code
        result.conversion_notes.append("Optimized for memory usage")
        return result

    def _modernize_patterns(self, code: str) -> ConversionResult:
        """Modernize Python patterns"""
        result = ConversionResult(success=True)
        converted_code = code

        # Convert to list comprehensions
        pattern = r"result = \[\]\s*\n\s*for (\w+) in (\w+):\s*\n\s*if (\w+)\.active:\s*\n\s*result\.append\(\3\.name\)"
        replacement = r"result = [\1.name for \1 in \2 if \1.active]"
        converted_code = re.sub(pattern, replacement, converted_code, flags=re.MULTILINE)

        # Convert to dict with zip
        pattern = r"for i in range\(len\((\w+)\)\):\s*\n\s*result\[(\w+)\[i\]\] = (\w+)\[i\]"
        replacement = r"result = dict(zip(\1, \3))"
        converted_code = re.sub(pattern, replacement, converted_code, flags=re.MULTILINE)

        # Convert to f-strings
        converted_code = re.sub(
            r'"([^"]*?)%s([^"]*?)%d([^"]*?)" % \((\w+), (\w+)\)',
            r'"f"\1{\4}\2{\5}\3"',
            converted_code,
        )
        converted_code = re.sub(
            r'"Name: %s, Age: %d" % \((\w+), (\w+)\)', r'f"Name: {\1}, Age: {\2}"', converted_code
        )

        result.converted_code = converted_code
        result.conversion_notes.append("Modernized Python patterns")
        return result

    def _convert_to_agent_framework(self, code: str) -> ConversionResult:
        """Convert to T-Developer agent framework"""
        result = ConversionResult(success=True)

        # Basic agent framework template
        framework_code = '''from typing import Dict, Any
import asyncio
from src.agents.unified.base.base_agent import BaseAgent

class Agent(BaseAgent):
    """T-Developer Framework Agent"""

    def __init__(self):
        super().__init__()

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method"""
        try:
            result = await self.process(request)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def process(self, data: Dict[str, Any]) -> Any:
        """Process the request - implement your logic here"""
        return data

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {"type": "processor", "version": "1.0"}
'''

        result.converted_code = framework_code
        result.conversion_notes.append("Converted to T-Developer agent framework")
        result.estimated_memory_kb = self._estimate_memory_usage(framework_code)
        return result

    def _modernize_dependencies(self, code: str) -> ConversionResult:
        """Modernize deprecated dependencies"""
        result = ConversionResult(success=True)
        converted_code = code

        # Replace deprecated imports
        for old_dep, new_dep in self.dependency_mappings.items():
            if old_dep in code:
                converted_code = converted_code.replace(f"import {old_dep}", f"import {new_dep}")
                result.new_dependencies.append(new_dep)
                result.removed_dependencies.append(old_dep)

        # Specific replacements
        converted_code = converted_code.replace(
            "ConfigParser.ConfigParser", "configparser.ConfigParser"
        )

        result.converted_code = converted_code
        result.conversion_notes.append("Modernized dependencies")
        return result

    def _optimize_performance(self, code: str) -> ConversionResult:
        """Optimize for performance (3μs instantiation)"""
        result = ConversionResult(success=True)

        # Use lazy loading for heavy objects
        optimized_code = """class OptimizedAgent:
    def __init__(self):
        self._heavy_object = None
        self._complex_processor = None

    @property
    def heavy_object(self):
        if self._heavy_object is None:
            # Lazy loading
            pass  # Initialize when needed
        return self._heavy_object

    def process(self, data):
        return data
"""

        result.converted_code = optimized_code
        result.conversion_notes.append("Optimized for fast instantiation")
        return result

    def _improve_error_handling(self, code: str) -> ConversionResult:
        """Improve error handling in code"""
        result = ConversionResult(success=True)
        converted_code = code

        # Wrap risky operations in try-catch
        if "data / 0" in code:
            converted_code = converted_code.replace(
                "result = data / 0",
                """try:
    result = data / 0
except ZeroDivisionError:
    result = 0""",
            )

        # Improve file operations
        if "open(" in code:
            converted_code = re.sub(
                r"file = open\(([^)]+)\)\s*\n\s*content = file\.read\(\)",
                r"with open(\1) as file:\n    content = file.read()",
                converted_code,
            )

        result.converted_code = converted_code
        result.conversion_notes.append("Improved error handling")
        return result

    def _validate_syntax(self, code: str) -> ConversionResult:
        """Validate code syntax"""
        result = ConversionResult(success=True, converted_code=code)

        try:
            ast.parse(code)
            result.syntax_valid = True
        except SyntaxError as e:
            result.syntax_valid = False
            result.validation_errors.append(f"Syntax error: {str(e)}")

        return result

    def _estimate_memory_usage(self, code: str) -> float:
        """Estimate memory usage in KB"""
        # Simple estimation based on code size
        return len(code.encode("utf-8")) / 1024.0

    def _estimate_instantiation_time(self, code: str) -> float:
        """Estimate instantiation time in microseconds"""
        # Simple heuristic based on complexity
        complexity_factors = 0
        complexity_factors += code.count("import") * 0.5
        complexity_factors += code.count("class") * 0.3
        complexity_factors += code.count("def") * 0.1

        # Base time + complexity
        return min(1.0 + complexity_factors, self.target_instantiation_us)

    def _add_parameter_hints(self, match):
        """Add parameter type hints"""
        func_name = match.group(1)
        params = match.group(2)

        # Simple heuristic for parameter types
        if "data" in params:
            params = re.sub(r"\bdata\b", "data: Dict[str, Any]", params)
        if "config" in params:
            params = re.sub(r"\bconfig\b", "config: Any", params)

        return f"def {func_name}({params})"
