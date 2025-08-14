"""
TypeChecker Tests - Day 31
Tests for type validation in services
"""

import pytest

from src.validator.type_checker import TypeChecker


class TestTypeChecker:
    """Tests for TypeChecker"""

    @pytest.fixture
    def checker(self):
        """Create TypeChecker instance"""
        return TypeChecker()

    @pytest.fixture
    def sample_data(self):
        """Sample data for type checking"""
        return {
            "name": "TestService",
            "version": "1.0.0",
            "agents": [{"name": "agent1", "size_kb": 5.2}, {"name": "agent2", "size_kb": 4.8}],
            "config": {"timeout": 30, "retry": True, "max_workers": 4},
        }

    def test_checker_initialization(self, checker):
        """Test TypeChecker initialization"""
        assert checker is not None
        assert hasattr(checker, "type_definitions")
        assert hasattr(checker, "check")

    def test_check_string_type(self, checker):
        """Test string type validation"""
        result = checker.check_field("test", str)
        assert result["valid"] is True
        assert result["actual_type"] == "str"

        result = checker.check_field(123, str)
        assert result["valid"] is False
        assert "Expected str" in result["error"]

    def test_check_number_types(self, checker):
        """Test number type validation"""
        # Integer
        result = checker.check_field(42, int)
        assert result["valid"] is True

        # Float
        result = checker.check_field(3.14, float)
        assert result["valid"] is True

        # Wrong type
        result = checker.check_field("42", int)
        assert result["valid"] is False

    def test_check_list_type(self, checker):
        """Test list type validation"""
        result = checker.check_field([1, 2, 3], list)
        assert result["valid"] is True

        result = checker.check_field({"a": 1}, list)
        assert result["valid"] is False

    def test_check_dict_type(self, checker):
        """Test dictionary type validation"""
        result = checker.check_field({"key": "value"}, dict)
        assert result["valid"] is True

        result = checker.check_field([1, 2], dict)
        assert result["valid"] is False

    def test_check_nested_types(self, checker, sample_data):
        """Test nested type validation"""
        schema = {"name": str, "agents": list, "config": dict}

        result = checker.check_schema(sample_data, schema)
        assert result["valid"] is True
        assert len(result["type_errors"]) == 0

    def test_check_invalid_schema(self, checker):
        """Test validation with invalid schema"""
        data = {"name": 123, "count": "five"}  # Should be string  # Should be int
        schema = {"name": str, "count": int}

        result = checker.check_schema(data, schema)
        assert result["valid"] is False
        assert len(result["type_errors"]) == 2

    def test_check_optional_fields(self, checker):
        """Test optional field validation"""
        data = {"required": "value"}
        schema = {"required": str, "optional?": int}  # ? indicates optional

        result = checker.check_schema(data, schema)
        assert result["valid"] is True

    def test_check_union_types(self, checker):
        """Test union type validation"""
        # String or int
        result = checker.check_union_type("test", [str, int])
        assert result["valid"] is True

        result = checker.check_union_type(42, [str, int])
        assert result["valid"] is True

        result = checker.check_union_type(3.14, [str, int])
        assert result["valid"] is False

    def test_validate_service_types(self, checker, sample_data):
        """Test complete service type validation"""
        result = checker.check(sample_data)

        assert result["valid"] is True
        assert "checked_fields" in result
        assert len(result["type_errors"]) == 0

    def test_custom_type_definition(self, checker):
        """Test custom type definitions"""
        checker.define_type("AgentSize", lambda x: 0 < x <= 6.5)

        result = checker.check_custom_type(5.2, "AgentSize")
        assert result["valid"] is True

        result = checker.check_custom_type(7.0, "AgentSize")
        assert result["valid"] is False

    def test_array_element_types(self, checker):
        """Test array element type checking"""
        data = [1, 2, 3, 4, 5]
        result = checker.check_array_elements(data, int)
        assert result["valid"] is True

        data = [1, "two", 3]
        result = checker.check_array_elements(data, int)
        assert result["valid"] is False
        assert result["invalid_indices"] == [1]

    def test_recursive_validation(self, checker):
        """Test recursive type validation"""
        data = {"level1": {"level2": {"level3": {"value": 42}}}}

        result = checker.check_recursive(data, max_depth=5)
        assert result["valid"] is True
        assert result["max_depth_reached"] == 4

    def test_type_coercion(self, checker):
        """Test type coercion capabilities"""
        result = checker.coerce("42", int)
        assert result["success"] is True
        assert result["value"] == 42

        result = checker.coerce("invalid", int)
        assert result["success"] is False

    def test_validation_performance(self, checker, sample_data):
        """Test validation performance"""
        import time

        start = time.time()
        for _ in range(1000):
            checker.check(sample_data)
        elapsed = time.time() - start

        # Should validate 1000 times in under 1 second
        assert elapsed < 1.0

    def test_type_inference(self, checker):
        """Test type inference from data"""
        data = {"name": "test", "count": 5, "active": True}

        inferred = checker.infer_schema(data)
        assert inferred["name"] == str
        assert inferred["count"] == int
        assert inferred["active"] == bool

    def test_strict_mode(self, checker):
        """Test strict type checking mode"""
        checker.set_strict_mode(True)

        # In strict mode, no type coercion
        result = checker.check_field(1, float)
        assert result["valid"] is False  # int is not float in strict mode

    def test_type_reporting(self, checker, sample_data):
        """Test type checking report generation"""
        result = checker.check(sample_data)
        report = checker.generate_report(result)

        assert isinstance(report, str)
        assert "Type Check Report" in report
        assert "Valid: True" in report
