"""Unit Test Template - Day 34
Template for generating unit tests"""

UNIT_TEST_TEMPLATE = '''"""Unit tests for {module_name}"""
import pytest
from unittest.mock import Mock, patch
from {import_path} import {class_name}


class Test{class_name}:
    """Test suite for {class_name}"""

    def setup_method(self):
        """Setup test fixtures"""
        self.instance = {class_name}()

    def teardown_method(self):
        """Cleanup after tests"""
        self.instance = None

    {test_methods}

    def test_initialization(self):
        """Test {class_name} initialization"""
        assert self.instance is not None
        assert isinstance(self.instance, {class_name})

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(Exception):
            self.instance.invalid_method()
'''

METHOD_TEST_TEMPLATE = '''
    def test_{method_name}(self):
        """Test {method_name} method"""
        # Arrange
        {arrange_code}

        # Act
        result = self.instance.{method_name}({params})

        # Assert
        assert result is not None
        {assertions}'''

MOCK_TEST_TEMPLATE = '''
    @patch('{mock_target}')
    def test_{method_name}_with_mock(self, mock_{mock_name}):
        """Test {method_name} with mocked dependencies"""
        # Arrange
        mock_{mock_name}.return_value = {mock_return}

        # Act
        result = self.instance.{method_name}({params})

        # Assert
        mock_{mock_name}.assert_called_once()
        assert result == {expected}'''

PARAMETRIZED_TEST_TEMPLATE = '''
    @pytest.mark.parametrize("input_val,expected", [
        {test_cases}
    ])
    def test_{method_name}_parametrized(self, input_val, expected):
        """Test {method_name} with multiple inputs"""
        result = self.instance.{method_name}(input_val)
        assert result == expected'''

ASYNC_TEST_TEMPLATE = '''
    @pytest.mark.asyncio
    async def test_{method_name}_async(self):
        """Test async {method_name}"""
        result = await self.instance.{method_name}()
        assert result is not None'''
