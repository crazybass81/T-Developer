# backend/tests/agents/test_generation_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from backend.src.agents.implementations.generation_agent import (
    GenerationAgent,
    GenerationRequest,
    GeneratedCode,
    CodeQualityAnalyzer,
    TemplateManager,
    CodeOptimizer
)

@pytest.fixture
def generation_agent():
    """Create GenerationAgent instance for testing"""
    return GenerationAgent()

@pytest.fixture
def sample_generation_request():
    """Sample generation request"""
    return GenerationRequest(
        component_type="user_authentication",
        requirements=[
            "User login with email and password",
            "JWT token generation",
            "Password hashing with bcrypt",
            "Input validation",
            "Error handling"
        ],
        framework="react",
        language="javascript",
        dependencies=["react", "axios"],
        constraints={
            "max_complexity": "medium",
            "security_level": "high"
        },
        context={
            "project_type": "web_application",
            "architecture": "mvc",
            "database": "postgresql"
        }
    )

class TestGenerationAgent:
    """Test GenerationAgent functionality"""

    @pytest.mark.asyncio
    async def test_generate_component_basic(self, generation_agent, sample_generation_request):
        """Test basic component generation"""
        
        # Mock the AI agents
        with patch.object(generation_agent.code_generator, 'arun') as mock_code_gen, \
             patch.object(generation_agent.test_generator, 'arun') as mock_test_gen, \
             patch.object(generation_agent.doc_generator, 'arun') as mock_doc_gen:
            
            # Setup mocks
            mock_code_gen.return_value = Mock(content="""
import React, { useState } from 'react';
import axios from 'axios';

const UserAuthentication = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post('/api/auth/login', {
        email,
        password
      });
      
      onLogin(response.data.token);
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

export default UserAuthentication;
""")
            
            mock_test_gen.return_value = Mock(content="""
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import UserAuthentication from './UserAuthentication';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('UserAuthentication', () => {
  const mockOnLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login form', () => {
    render(<UserAuthentication onLogin={mockOnLogin} />);
    
    expect(screen.getByRole('textbox', { name: /email/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    const mockToken = 'mock-jwt-token';
    mockedAxios.post.mockResolvedValue({ data: { token: mockToken } });

    render(<UserAuthentication onLogin={mockOnLogin} />);
    
    fireEvent.change(screen.getByRole('textbox', { name: /email/i }), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith(mockToken);
    });
  });
});
""")
            
            mock_doc_gen.return_value = Mock(content="""
# UserAuthentication Component

## Overview
A React component that provides user authentication functionality with email and password.

## Props
- `onLogin`: Function called when login is successful, receives JWT token

## Features
- Email and password validation
- Loading state management
- Error handling
- JWT token handling

## Usage
```jsx
import UserAuthentication from './UserAuthentication';

const App = () => {
  const handleLogin = (token) => {
    localStorage.setItem('authToken', token);
    // Redirect to dashboard
  };

  return <UserAuthentication onLogin={handleLogin} />;
};
```
""")

            # Execute generation
            result = await generation_agent.generate_component(sample_generation_request)

            # Assertions
            assert isinstance(result, GeneratedCode)
            assert result.component_name == "user_authentication"
            assert result.language == "javascript"
            assert result.framework == "react"
            assert "UserAuthentication" in result.source_code
            assert "test" in result.test_code.lower()
            assert "overview" in result.documentation.lower()
            assert len(result.dependencies) > 0
            assert result.quality_score > 0
            assert "src/" in str(result.file_structure)

    @pytest.mark.asyncio
    async def test_generate_python_component(self, generation_agent):
        """Test Python component generation"""
        
        request = GenerationRequest(
            component_type="data_processor",
            requirements=[
                "Process CSV data",
                "Data validation",
                "Error logging",
                "Export to JSON"
            ],
            framework="django",
            language="python",
            dependencies=["pandas", "django"]
        )

        with patch.object(generation_agent.code_generator, 'arun') as mock_code_gen, \
             patch.object(generation_agent.test_generator, 'arun') as mock_test_gen, \
             patch.object(generation_agent.doc_generator, 'arun') as mock_doc_gen:
            
            mock_code_gen.return_value = Mock(content="""
import pandas as pd
import json
import logging
from typing import Dict, List, Any

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_csv(self, file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_csv(file_path)
            validated_data = self.validate_data(df)
            return self.export_to_json(validated_data)
        except Exception as e:
            self.logger.error(f"Error processing CSV: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove empty rows
        df = df.dropna()
        return df
    
    def export_to_json(self, df: pd.DataFrame) -> Dict[str, Any]:
        return df.to_dict('records')
""")
            
            mock_test_gen.return_value = Mock(content="""
import pytest
import pandas as pd
from unittest.mock import patch, mock_open
from data_processor import DataProcessor

class TestDataProcessor:
    def setup_method(self):
        self.processor = DataProcessor()
    
    def test_process_csv_success(self):
        csv_data = "name,age\\nJohn,25\\nJane,30"
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('pandas.read_csv') as mock_read_csv:
                mock_df = pd.DataFrame({'name': ['John', 'Jane'], 'age': [25, 30]})
                mock_read_csv.return_value = mock_df
                
                result = self.processor.process_csv('test.csv')
                
                assert len(result) == 2
                assert result[0]['name'] == 'John'
""")
            
            mock_doc_gen.return_value = Mock(content="# DataProcessor Documentation")

            result = await generation_agent.generate_component(request)

            assert result.language == "python"
            assert result.framework == "django"
            assert "DataProcessor" in result.source_code
            assert "pytest" in result.test_code
            assert result.file_structure["src/data_processor.py"]
            assert result.file_structure["tests/test_data_processor.py"]

    def test_template_selection(self, generation_agent):
        """Test template selection logic"""
        
        request = GenerationRequest(
            component_type="component",
            requirements=["Basic component"],
            framework="react",
            language="javascript"
        )

        # Test template selection
        template = asyncio.run(generation_agent._select_template(request))
        
        # Should find React template or return None
        if template:
            assert template.framework == "react" or template.language == "javascript"

    def test_file_structure_generation(self, generation_agent):
        """Test file structure generation"""
        
        request = GenerationRequest(
            component_type="user_profile",
            requirements=["Display user info"],
            framework="vue",
            language="javascript"
        )

        source_code = "const UserProfile = {};"
        test_code = "describe('UserProfile', () => {});"

        structure = generation_agent._generate_file_structure(request, source_code, test_code)

        assert "src/user_profile.js" in structure
        assert "tests/user_profile.test.js" in structure
        assert "package.json" in structure
        assert structure["src/user_profile.js"] == source_code
        assert structure["tests/user_profile.test.js"] == test_code

    def test_dependency_extraction(self, generation_agent):
        """Test dependency extraction from code"""
        
        code = """
import React from 'react';
import axios from 'axios';
import { useState } from 'react';
const lodash = require('lodash');
"""

        dependencies = generation_agent._extract_dependencies(code, "react")

        assert "react" in dependencies
        assert "axios" in dependencies or len(dependencies) > 0  # Basic extraction

class TestCodeQualityAnalyzer:
    """Test CodeQualityAnalyzer"""

    def setup_method(self):
        self.analyzer = CodeQualityAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_quality_good_code(self):
        """Test quality analysis for good code"""
        
        source_code = """
def calculate_total(items):
    '''Calculate total price of items'''
    if not items:
        return 0
    
    total = 0
    for item in items:
        if item.get('price', 0) > 0:
            total += item['price']
    
    return total
"""

        test_code = """
def test_calculate_total():
    items = [{'price': 10}, {'price': 20}]
    assert calculate_total(items) == 30

def test_calculate_total_empty():
    assert calculate_total([]) == 0

def test_calculate_total_invalid_price():
    items = [{'price': -5}]
    assert calculate_total(items) == 0
"""

        score = await self.analyzer.analyze(source_code, test_code)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be decent quality

    @pytest.mark.asyncio
    async def test_analyze_quality_poor_code(self):
        """Test quality analysis for poor code"""
        
        source_code = """
def bad_function(x):
    if x:
        if x > 0:
            if x < 100:
                if x % 2 == 0:
                    return x * 2
    return 0
"""

        test_code = ""  # No tests

        score = await self.analyzer.analyze(source_code, test_code)
        
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Should be poor quality

    def test_complexity_analysis(self):
        """Test complexity analysis"""
        
        simple_code = "def simple(): return 1"
        complex_code = """
def complex():
    for i in range(10):
        if i % 2:
            while i > 0:
                try:
                    if i == 5:
                        break
                except:
                    pass
                i -= 1
"""

        simple_score = self.analyzer._analyze_complexity(simple_code)
        complex_score = self.analyzer._analyze_complexity(complex_code)
        
        assert simple_score > complex_score

    def test_coverage_estimation(self):
        """Test coverage estimation"""
        
        source_code = "def func1(): pass\ndef func2(): pass"
        
        no_tests = ""
        some_tests = "def test_func1(): pass"
        many_tests = "def test_func1(): pass\ndef test_func2(): pass\ndef test_edge_case(): pass"

        no_coverage = self.analyzer._estimate_coverage(source_code, no_tests)
        some_coverage = self.analyzer._estimate_coverage(source_code, some_tests)
        high_coverage = self.analyzer._estimate_coverage(source_code, many_tests)

        assert no_coverage == 0.0
        assert some_coverage > no_coverage
        assert high_coverage > some_coverage

class TestTemplateManager:
    """Test TemplateManager"""

    def setup_method(self):
        self.manager = TemplateManager()

    def test_find_similar_templates(self):
        """Test finding similar templates"""
        
        similar = self.manager.find_similar("javascript", "react", "component")
        
        # Should return list (may be empty if no templates loaded)
        assert isinstance(similar, list)

    def test_template_loading(self):
        """Test template loading"""
        
        # Should have loaded default templates
        assert len(self.manager.templates) > 0
        
        # Check React template exists
        react_templates = [
            t for t in self.manager.templates.values()
            if t.framework == "react"
        ]
        assert len(react_templates) > 0

class TestCodeOptimizer:
    """Test CodeOptimizer"""

    def setup_method(self):
        self.optimizer = CodeOptimizer()

    @pytest.mark.asyncio
    async def test_optimize_javascript(self):
        """Test JavaScript optimization"""
        
        code = """
function test() {
    console.log('test');
}
"""

        optimized = await self.optimizer.optimize(code, "javascript", "react")
        
        # Should add 'use strict'
        assert "'use strict';" in optimized

    @pytest.mark.asyncio
    async def test_optimize_python(self):
        """Test Python optimization"""
        
        code = """
def test_function(x):
    return x + 1
"""

        optimized = await self.optimizer.optimize(code, "python", "django")
        
        # Should return optimized code (may be same if no optimizations apply)
        assert len(optimized) > 0

@pytest.mark.integration
class TestGenerationAgentIntegration:
    """Integration tests for GenerationAgent"""

    @pytest.fixture
    def integration_agent(self):
        """Create agent for integration testing"""
        agent = GenerationAgent()
        
        # Mock the AI agents to avoid actual API calls
        agent.code_generator.arun = AsyncMock()
        agent.test_generator.arun = AsyncMock()
        agent.doc_generator.arun = AsyncMock()
        
        return agent

    @pytest.mark.asyncio
    async def test_full_generation_workflow(self, integration_agent):
        """Test complete generation workflow"""
        
        # Setup mocks
        integration_agent.code_generator.arun.return_value = Mock(
            content="const Component = () => <div>Test</div>;"
        )
        integration_agent.test_generator.arun.return_value = Mock(
            content="test('renders', () => {});"
        )
        integration_agent.doc_generator.arun.return_value = Mock(
            content="# Component Documentation"
        )

        request = GenerationRequest(
            component_type="test_component",
            requirements=["Render test content"],
            framework="react",
            language="javascript"
        )

        result = await integration_agent.generate_component(request)

        # Verify complete workflow
        assert result.source_code
        assert result.test_code
        assert result.documentation
        assert result.file_structure
        assert result.quality_score >= 0
        assert len(result.dependencies) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, integration_agent):
        """Test error handling in generation"""
        
        # Make code generator fail
        integration_agent.code_generator.arun.side_effect = Exception("Generation failed")
        
        request = GenerationRequest(
            component_type="failing_component",
            requirements=["This will fail"],
            framework="react",
            language="javascript"
        )

        with pytest.raises(Exception):
            await integration_agent.generate_component(request)

    @pytest.mark.performance
    async def test_generation_performance(self, integration_agent):
        """Test generation performance"""
        
        # Setup fast mocks
        integration_agent.code_generator.arun.return_value = Mock(content="code")
        integration_agent.test_generator.arun.return_value = Mock(content="test")
        integration_agent.doc_generator.arun.return_value = Mock(content="doc")

        request = GenerationRequest(
            component_type="perf_test",
            requirements=["Performance test"],
            framework="react",
            language="javascript"
        )

        import time
        start_time = time.time()
        
        result = await integration_agent.generate_component(request)
        
        end_time = time.time()
        generation_time = end_time - start_time

        # Should complete within reasonable time (with mocks)
        assert generation_time < 1.0  # 1 second with mocks
        assert result is not None