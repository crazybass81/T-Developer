"""TestGenerator - Day 34
Automatic test generation - Size: ~6.5KB"""
import ast
from typing import Any, Dict, List


class TestGenerator:
    """Generate tests automatically - Size optimized to 6.5KB"""

    def __init__(self):
        self.templates = {
            "unit": "def test_{n}():\n    assert {a}",
            "integration": "def test_{n}_integration():\n    # Test {c} components\n    assert True",
            "performance": "def test_{n}_perf():\n    import time\n    start = time.time()\n    # Operation\n    assert time.time() - start < {t}",
        }

    def generate_unit_tests(self, code: str) -> str:
        """Generate unit tests from code"""
        try:
            tree = ast.parse(code)
        except:
            return "# Parse error"

        tests = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cn = node.name
                for m in node.body:
                    if isinstance(m, ast.FunctionDef) and not m.name.startswith("_"):
                        tests.append(self._gen_test(cn, m.name))

        return "\n".join(tests)

    def generate_integration_tests(self, components: List[str]) -> str:
        """Generate integration tests"""
        test = f'''def test_integration():
    """Test {len(components)} components"""
    components = {{}}
'''
        for c in components:
            test += f"    components['{c}'] = {c}()\n"

        test += """
    # Test initialization
    for name, comp in components.items():
        assert comp is not None, f"{name} failed"

    # Test interaction
    result = components[list(components.keys())[0]].process({})
    assert result is not None
"""
        return test

    def generate_performance_tests(self, operations: Dict[str, float]) -> str:
        """Generate performance tests"""
        tests = []
        for op, threshold in operations.items():
            test = f'''def test_{op}_performance():
    """Test {op} < {threshold}ms"""
    import time
    times = []
    for _ in range(100):
        start = time.perf_counter()
        # {op} operation
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    avg = sum(times) / len(times)
    assert avg < {threshold}, f"Avg {{avg}}ms > {threshold}ms"
'''
            tests.append(test)

        return "\n".join(tests)

    def generate_test_suite(self, config: Dict[str, Any]) -> str:
        """Generate complete test suite"""
        suite = '''"""Auto-generated test suite"""
import pytest
from unittest.mock import Mock, patch

'''

        if "code" in config:
            suite += "# Unit tests\n"
            suite += self.generate_unit_tests(config["code"])
            suite += "\n\n"

        if "components" in config:
            suite += "# Integration tests\n"
            suite += self.generate_integration_tests(config["components"])
            suite += "\n\n"

        if "performance" in config:
            suite += "# Performance tests\n"
            suite += self.generate_performance_tests(config["performance"])

        return suite

    def analyze_coverage(self, code: str, tests: str) -> Dict[str, Any]:
        """Analyze test coverage"""
        try:
            code_tree = ast.parse(code)
            test_tree = ast.parse(tests)
        except:
            return {"error": "Parse error"}

        # Count functions
        code_funcs = []
        test_funcs = []

        for node in ast.walk(code_tree):
            if isinstance(node, ast.FunctionDef):
                code_funcs.append(node.name)

        for node in ast.walk(test_tree):
            if isinstance(node, ast.FunctionDef):
                test_funcs.append(node.name)

        coverage = len(test_funcs) / max(len(code_funcs), 1) * 100

        return {
            "functions": len(code_funcs),
            "tests": len(test_funcs),
            "coverage": round(coverage, 1),
            "untested": [f for f in code_funcs if f"test_{f}" not in test_funcs],
        }

    def _gen_test(self, class_name: str, method_name: str) -> str:
        """Generate single test"""
        return f'''
def test_{class_name}_{method_name}():
    """Test {class_name}.{method_name}"""
    instance = {class_name}()
    result = instance.{method_name}()
    assert result is not None
'''
