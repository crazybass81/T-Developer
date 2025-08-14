"""
TestGenerator Tests - Day 34
Tests for automatic test generation
"""

import pytest

from src.generators.test_generator import TestGenerator


class TestTestGenerator:
    """Tests for TestGenerator"""

    @pytest.fixture
    def generator(self):
        """Create TestGenerator instance"""
        return TestGenerator()

    @pytest.fixture
    def sample_code(self):
        """Sample code to generate tests for"""
        return """
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
"""

    def test_generator_initialization(self, generator):
        """Test TestGenerator initialization"""
        assert generator is not None
        assert hasattr(generator, "templates")
        assert hasattr(generator, "coverage_analyzer")

    def test_generate_unit_tests(self, generator, sample_code):
        """Test unit test generation"""
        tests = generator.generate_unit_tests(sample_code)

        assert "test_add" in tests
        assert "test_divide" in tests
        assert "assert" in tests
        assert "pytest" in tests

    def test_generate_integration_tests(self, generator):
        """Test integration test generation"""
        components = ["ComponentA", "ComponentB"]
        tests = generator.generate_integration_tests(components)

        assert "test_component_interaction" in tests
        assert all(comp in tests for comp in components)

    def test_generate_edge_cases(self, generator, sample_code):
        """Test edge case generation"""
        edge_cases = generator.generate_edge_cases(sample_code)

        assert len(edge_cases) > 0
        assert any("zero" in case.lower() for case in edge_cases)
        assert any("negative" in case.lower() for case in edge_cases)

    def test_generate_fixtures(self, generator):
        """Test fixture generation"""
        requirements = {
            "database": True,
            "mock_api": True,
            "test_data": ["users", "products"],
        }

        fixtures = generator.generate_fixtures(requirements)

        assert "@pytest.fixture" in fixtures
        assert "database" in fixtures
        assert "mock_api" in fixtures

    def test_generate_performance_tests(self, generator):
        """Test performance test generation"""
        config = {
            "function": "process_data",
            "expected_time": 1.0,
            "iterations": 1000,
        }

        perf_test = generator.generate_performance_test(config)

        assert "time.time()" in perf_test or "perf_counter" in perf_test
        assert "assert" in perf_test
        assert str(config["expected_time"]) in perf_test

    def test_generate_parameterized_tests(self, generator):
        """Test parameterized test generation"""
        params = [
            (1, 2, 3),
            (0, 0, 0),
            (-1, 1, 0),
        ]

        test = generator.generate_parameterized_test("add", params)

        assert "@pytest.mark.parametrize" in test
        assert all(str(p) in test for p in params)

    def test_generate_mocks(self, generator):
        """Test mock generation"""
        dependencies = ["database", "api_client", "file_system"]

        mocks = generator.generate_mocks(dependencies)

        assert "Mock" in mocks or "MagicMock" in mocks
        assert all(dep in mocks for dep in dependencies)

    def test_analyze_coverage(self, generator, sample_code):
        """Test coverage analysis"""
        existing_tests = "def test_add(): pass"

        coverage = generator.analyze_coverage(sample_code, existing_tests)

        assert "coverage_percent" in coverage
        assert "missing_tests" in coverage
        assert coverage["coverage_percent"] < 100

    def test_generate_property_tests(self, generator):
        """Test property-based test generation"""
        function_sig = "def sort_list(items: List[int]) -> List[int]"

        prop_test = generator.generate_property_test(function_sig)

        assert "hypothesis" in prop_test.lower() or "property" in prop_test
        assert "given" in prop_test or "for all" in prop_test.lower()

    def test_generate_async_tests(self, generator):
        """Test async test generation"""
        async_code = """
async def fetch_data(url: str) -> dict:
    # Async implementation
    pass
"""

        test = generator.generate_async_test(async_code)

        assert "async def test_" in test
        assert "await" in test
        assert "pytest.mark.asyncio" in test

    def test_generate_exception_tests(self, generator, sample_code):
        """Test exception test generation"""
        tests = generator.generate_exception_tests(sample_code)

        assert "pytest.raises" in tests
        assert "ValueError" in tests
        assert "divide" in tests

    def test_generate_regression_tests(self, generator):
        """Test regression test generation"""
        bug_report = {
            "function": "calculate_discount",
            "input": {"price": 100, "discount": 110},
            "expected": 0,
            "actual": -10,
        }

        test = generator.generate_regression_test(bug_report)

        assert "test_regression" in test
        assert str(bug_report["input"]["price"]) in test
        assert str(bug_report["expected"]) in test

    def test_generate_snapshot_tests(self, generator):
        """Test snapshot test generation"""
        component = "UserProfile"

        test = generator.generate_snapshot_test(component)

        assert "snapshot" in test.lower()
        assert component in test
        assert "assert" in test

    def test_generate_fuzz_tests(self, generator):
        """Test fuzz test generation"""
        function = "parse_input(data: str) -> dict"

        fuzz_test = generator.generate_fuzz_test(function)

        assert "random" in fuzz_test.lower() or "fuzz" in fuzz_test.lower()
        assert "for" in fuzz_test or "while" in fuzz_test

    def test_generate_contract_tests(self, generator):
        """Test contract test generation"""
        api_spec = {
            "endpoint": "/api/users",
            "method": "POST",
            "schema": {"name": "string", "age": "integer"},
        }

        test = generator.generate_contract_test(api_spec)

        assert api_spec["endpoint"] in test
        assert "schema" in test.lower() or "validate" in test.lower()

    def test_generate_security_tests(self, generator):
        """Test security test generation"""
        endpoint = "/api/login"

        tests = generator.generate_security_tests(endpoint)

        assert "injection" in tests.lower() or "xss" in tests.lower()
        assert "authentication" in tests.lower() or "auth" in tests.lower()

    def test_test_suite_optimization(self, generator):
        """Test test suite optimization"""
        tests = ["test_a", "test_b", "test_c"] * 10  # Duplicates

        optimized = generator.optimize_test_suite(tests)

        assert len(optimized) < len(tests)
        assert len(set(optimized)) == len(optimized)  # No duplicates
