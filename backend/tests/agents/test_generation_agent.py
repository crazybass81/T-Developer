# backend/tests/agents/test_generation_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from generation_agent import GenerationAgent, GenerationType, GenerationRequest
from generation_templates import TemplateEngine
from generation_validator import CodeValidator

@pytest.mark.asyncio
class TestGenerationAgent:
    """Generation Agent comprehensive test suite"""

    @pytest.fixture
    async def generation_agent(self):
        """Generation Agent instance"""
        agent = GenerationAgent()
        # Mock the AI agents for testing
        agent.main_generator.arun = AsyncMock()
        agent.test_generator.arun = AsyncMock()
        yield agent

    @pytest.fixture
    def sample_requests(self):
        """Sample generation requests"""
        return {
            'react_component': GenerationRequest(
                type=GenerationType.COMPONENT,
                requirements={
                    'name': 'UserProfile',
                    'props': [
                        {'name': 'user', 'type': 'User', 'optional': False},
                        {'name': 'onEdit', 'type': '() => void', 'optional': True}
                    ],
                    'features': ['display user info', 'edit functionality']
                },
                context={'framework': 'react', 'typescript': True},
                constraints=['responsive design', 'accessibility'],
                target_language='typescript',
                framework='react'
            ),
            'api_endpoint': GenerationRequest(
                type=GenerationType.API,
                requirements={
                    'endpoint': '/api/users',
                    'methods': ['GET', 'POST'],
                    'authentication': 'jwt',
                    'validation': 'joi'
                },
                context={'database': 'postgresql'},
                constraints=['rate limiting', 'input validation'],
                target_language='typescript',
                framework='express'
            )
        }

    async def test_basic_code_generation(self, generation_agent, sample_requests):
        """Test basic code generation functionality"""
        
        # Mock the generator response
        mock_code = """
        import React from 'react';
        
        interface UserProfileProps {
          user: User;
          onEdit?: () => void;
        }
        
        export const UserProfile: React.FC<UserProfileProps> = ({ user, onEdit }) => {
          return (
            <div className="user-profile">
              <h2>{user.name}</h2>
              <p>{user.email}</p>
              {onEdit && <button onClick={onEdit}>Edit</button>}
            </div>
          );
        };
        """
        
        generation_agent.main_generator.arun.return_value = Mock(content=mock_code)
        generation_agent.test_generator.arun.return_value = Mock(content="// Test code")
        
        # Test generation
        request = sample_requests['react_component']
        result = await generation_agent.generate_code(request)
        
        # Assertions
        assert result.code is not None
        assert result.language == 'typescript'
        assert result.framework == 'react'
        assert result.tests is not None
        assert isinstance(result.quality_score, float)
        assert 0 <= result.quality_score <= 1

    async def test_template_based_generation(self):
        """Test template-based code generation"""
        
        template_engine = TemplateEngine()
        
        # Test React component template
        variables = {
            'componentName': 'TestComponent',
            'interfaces': 'TestProps',
            'props': 'name: string;\n  age: number;',
            'propNames': 'name, age',
            'stateDeclarations': 'const [count, setCount] = useState<number>(0);',
            'useEffectHooks': '',
            'eventHandlers': '',
            'className': 'test-component',
            'jsx': '<div>{name} is {age} years old</div>'
        }
        
        code = template_engine.generate_from_template('react_component', variables)
        
        # Assertions
        assert 'TestComponent' in code
        assert 'TestProps' in code
        assert 'name: string' in code
        assert 'useState<number>(0)' in code

    async def test_code_validation(self):
        """Test code validation functionality"""
        
        validator = CodeValidator()
        
        # Test valid Python code
        valid_python = """
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
        """
        
        results = await validator.validate_code(
            valid_python,
            'python',
            {'functions': ['hello_world']}
        )
        
        # Assertions
        assert 'syntax' in results
        assert results['syntax'].passed
        assert results['syntax'].score == 1.0

    async def test_security_validation(self):
        """Test security validation"""
        
        validator = CodeValidator()
        
        # Test insecure Python code
        insecure_code = """
import os
user_input = input("Enter command: ")
os.system(user_input)  # Security risk
        """
        
        results = await validator.validate_code(insecure_code, 'python', {})
        
        # Assertions
        assert 'security' in results
        assert not results['security'].passed
        assert len(results['security'].issues) > 0
        assert 'os.system' in str(results['security'].issues)

    async def test_performance_validation(self):
        """Test performance validation"""
        
        validator = CodeValidator()
        
        # Test inefficient Python code
        inefficient_code = """
items = ['a', 'b', 'c', 'd', 'e']
for i in range(len(items)):
    print(items[i])
        """
        
        results = await validator.validate_code(inefficient_code, 'python', {})
        
        # Assertions
        assert 'performance' in results
        assert len(results['performance'].issues) > 0
        assert 'enumerate' in str(results['performance'].suggestions)

    async def test_multiple_language_support(self, generation_agent):
        """Test generation for multiple programming languages"""
        
        languages = ['python', 'typescript', 'javascript', 'java']
        
        for language in languages:
            request = GenerationRequest(
                type=GenerationType.SERVICE,
                requirements={'name': 'TestService'},
                context={},
                constraints=[],
                target_language=language
            )
            
            generation_agent.main_generator.arun.return_value = Mock(
                content=f"// {language} code here"
            )
            generation_agent.test_generator.arun.return_value = Mock(
                content=f"// {language} test code"
            )
            
            result = await generation_agent.generate_code(request)
            
            assert result.language == language
            assert result.code is not None

    @pytest.mark.performance
    async def test_generation_performance(self, generation_agent, sample_requests):
        """Test generation performance"""
        
        import time
        
        generation_agent.main_generator.arun.return_value = Mock(content="mock code")
        generation_agent.test_generator.arun.return_value = Mock(content="mock tests")
        
        # Test single generation
        start_time = time.time()
        request = sample_requests['react_component']
        await generation_agent.generate_code(request)
        single_duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert single_duration < 5.0  # 5 seconds max
        
        # Test concurrent generations
        start_time = time.time()
        tasks = [
            generation_agent.generate_code(request)
            for _ in range(5)
        ]
        await asyncio.gather(*tasks)
        concurrent_duration = time.time() - start_time
        
        # Concurrent should be more efficient than sequential
        assert concurrent_duration < single_duration * 5

    async def test_error_handling(self, generation_agent):
        """Test error handling in generation"""
        
        # Test with invalid request
        invalid_request = GenerationRequest(
            type=GenerationType.COMPONENT,
            requirements={},  # Empty requirements
            context={},
            constraints=[],
            target_language='invalid_language'
        )
        
        generation_agent.main_generator.arun.side_effect = Exception("Generation failed")
        
        with pytest.raises(Exception):
            await generation_agent.generate_code(invalid_request)

    async def test_dependency_extraction(self, generation_agent):
        """Test dependency extraction from generated code"""
        
        code_with_imports = """
import React from 'react';
import { useState, useEffect } from 'react';
import axios from 'axios';
const lodash = require('lodash');
        """
        
        dependencies = generation_agent._extract_dependencies(code_with_imports)
        
        # Assertions
        assert len(dependencies) >= 3
        assert any('react' in dep for dep in dependencies)
        assert any('axios' in dep for dep in dependencies)
        assert any('lodash' in dep for dep in dependencies)

    async def test_quality_analysis(self):
        """Test code quality analysis"""
        
        from generation_agent import CodeQualityAnalyzer
        
        analyzer = CodeQualityAnalyzer()
        
        # Test high-quality code
        good_code = """
def calculate_average(numbers):
    \"\"\"Calculate the average of a list of numbers.\"\"\"
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
        """
        
        score = await analyzer.analyze(good_code)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        
        # Test low-quality code (very long, no comments)
        bad_code = "x=1\n" * 1000  # 1000 lines of bad code
        
        bad_score = await analyzer.analyze(bad_code)
        assert bad_score < score  # Should be lower quality

    async def test_code_optimization(self):
        """Test code optimization functionality"""
        
        from generation_agent import CodeOptimizer
        
        optimizer = CodeOptimizer()
        
        original_code = """
def slow_function():
    result = ""
    for i in range(1000):
        result += str(i)
    return result
        """
        
        request = GenerationRequest(
            type=GenerationType.SERVICE,
            requirements={},
            context={},
            constraints=[],
            target_language='python'
        )
        
        optimized = await optimizer.optimize(original_code, request)
        
        # Should return optimized code (even if same for now)
        assert isinstance(optimized, str)
        assert len(optimized) > 0