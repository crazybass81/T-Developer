#!/usr/bin/env python3
"""
Unit Tests for Agent Registration API
Tests the complete agent registration flow
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.api.v1.models.agent_models import (
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    ValidationResult
)
from src.core.validation.code_validator import CodeValidator


class TestAgentRegistration:
    """Test suite for agent registration"""
    
    @pytest.fixture
    def sample_agent_code(self):
        """Sample valid agent code"""
        return '''
class DataProcessingAgent:
    """A simple data processing agent"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.version = "1.0.0"
    
    def execute(self, input_data):
        """Execute the agent logic"""
        try:
            # Process data
            result = self._process(input_data)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_capabilities(self):
        """Return agent capabilities"""
        return {
            "data_processing": True,
            "async_support": False,
            "batch_processing": True
        }
    
    def _process(self, data):
        """Internal processing logic"""
        # Transform data
        return {"processed": data, "timestamp": str(datetime.now())}
'''
    
    @pytest.fixture
    def invalid_agent_code(self):
        """Sample invalid agent code"""
        return '''
# Missing class definition and required methods
def process_data(data):
    eval(data)  # Security violation
    return data
'''
    
    @pytest.fixture
    def registration_request(self, sample_agent_code):
        """Sample registration request"""
        return AgentRegistrationRequest(
            agent_name="test_data_processor",
            agent_code=sample_agent_code,
            description="Test data processing agent",
            version="1.0.0",
            tags=["data", "processing", "test"]
        )
    
    @pytest.mark.asyncio
    async def test_code_validator_valid_code(self, sample_agent_code):
        """Test code validator with valid code"""
        validator = CodeValidator()
        result = await validator.validate(sample_agent_code)
        
        assert result.is_valid == True
        assert len(result.errors) == 0
        assert result.metrics is not None
    
    @pytest.mark.asyncio
    async def test_code_validator_invalid_code(self, invalid_agent_code):
        """Test code validator with invalid code"""
        validator = CodeValidator()
        result = await validator.validate(invalid_agent_code)
        
        assert result.is_valid == False
        assert len(result.errors) > 0
        assert any('eval()' in error for error in result.errors)
        assert any('class definition' in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_code_validator_security_checks(self):
        """Test security validation"""
        dangerous_code = '''
class MaliciousAgent:
    def __init__(self):
        pass
    
    def execute(self, data):
        exec(data)  # Security violation
        os.system("rm -rf /")  # Security violation
        return eval(data)  # Security violation
    
    def get_capabilities(self):
        return {}
'''
        
        validator = CodeValidator()
        result = await validator.validate(dangerous_code)
        
        assert result.is_valid == False
        assert len(result.errors) >= 2  # At least exec and eval violations
        assert any('exec()' in error for error in result.errors)
        assert any('eval()' in error for error in result.errors)
        # os.system check is part of general subprocess check
        assert any('System calls' in error or 'os.system' in error for error in result.errors)
    
    def test_registration_request_validation(self):
        """Test registration request model validation"""
        # Valid request
        valid_request = AgentRegistrationRequest(
            agent_name="valid_agent",
            agent_code="class Agent:\n    def execute(self): pass\n    def get_capabilities(self): pass",
            version="1.0.0"
        )
        assert valid_request.agent_name == "valid_agent"
        
        # Invalid name
        with pytest.raises(ValueError, match="alphanumeric"):
            AgentRegistrationRequest(
                agent_name="invalid@agent!",
                agent_code="class Agent: pass"
            )
        
        # Invalid version
        with pytest.raises(ValueError):
            AgentRegistrationRequest(
                agent_name="valid_agent",
                agent_code="class Agent: pass",
                version="invalid"
            )
    
    @pytest.mark.asyncio
    async def test_code_complexity_analysis(self, sample_agent_code):
        """Test code complexity metrics"""
        validator = CodeValidator()
        result = await validator.validate(sample_agent_code)
        
        assert result.metrics is not None
        assert 'lines_of_code' in result.metrics
        assert 'complexity' in result.metrics
        assert 'maintainability' in result.metrics
        
        # Check reasonable values
        assert result.metrics['lines_of_code'] > 10
        assert result.metrics['complexity'] > 0
        assert 0 <= result.metrics['maintainability'] <= 100
    
    @pytest.mark.asyncio
    async def test_best_practices_validation(self):
        """Test best practices checking"""
        poor_code = '''
class PoorAgent:
    def __init__(self):
        pass
    
    def execute(self, data):
        try:
            print("Processing...")  # Should use logging
            result = self.process(data)
            return result
        except:  # Bare except
            pass  # Empty except block
    
    def get_capabilities(self):
        return {}
    
    def process(self, data):
        # TODO: implement this
        magic_number = 12345  # Magic number
        return data * magic_number
'''
        
        validator = CodeValidator()
        result = await validator.validate(poor_code)
        
        # Should have warnings and suggestions
        assert len(result.warnings) > 0
        assert len(result.suggestions) > 0
        assert any('logging' in s for s in result.suggestions)
        assert any('except' in w for w in result.warnings)
        assert any('TODO' in w for w in result.warnings)
    
    def test_registration_response_model(self):
        """Test registration response model"""
        response = AgentRegistrationResponse(
            status="processing",
            agent_id="agent_12345",
            analysis_task_id="task_67890",
            message="Agent registered successfully",
            estimated_completion_time=30
        )
        
        assert response.status == "processing"
        assert response.agent_id == "agent_12345"
        assert response.estimated_completion_time == 30
        
        # Error response
        error_response = AgentRegistrationResponse(
            status="validation_failed",
            message="Validation failed",
            errors=["Missing required method", "Security violation"]
        )
        
        assert error_response.status == "validation_failed"
        assert len(error_response.errors) == 2


def run_tests():
    """Run tests standalone"""
    print("\n" + "="*50)
    print("Running Agent Registration Unit Tests")
    print("="*50 + "\n")
    
    # Create test instance
    test = TestAgentRegistration()
    
    # Get sample code directly (not as fixtures)
    sample_code = '''
class DataProcessingAgent:
    """A simple data processing agent"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.version = "1.0.0"
    
    def execute(self, input_data):
        """Execute the agent logic"""
        try:
            # Process data
            result = self._process(input_data)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_capabilities(self):
        """Return agent capabilities"""
        return {
            "data_processing": True,
            "async_support": False,
            "batch_processing": True
        }
    
    def _process(self, data):
        """Internal processing logic"""
        # Transform data
        from datetime import datetime
        return {"processed": data, "timestamp": str(datetime.now())}
'''
    
    invalid_code = '''
# Missing class definition and required methods
def process_data(data):
    eval(data)  # Security violation
    return data
'''
    
    # Run async tests
    loop = asyncio.get_event_loop()
    
    print("1. Testing valid code validation...")
    result = loop.run_until_complete(
        test.test_code_validator_valid_code(sample_code)
    )
    print("   ✓ Valid code passed validation")
    
    print("\n2. Testing invalid code validation...")
    result = loop.run_until_complete(
        test.test_code_validator_invalid_code(invalid_code)
    )
    print("   ✓ Invalid code detected correctly")
    
    print("\n3. Testing security checks...")
    result = loop.run_until_complete(
        test.test_code_validator_security_checks()
    )
    print("   ✓ Security violations detected")
    
    print("\n4. Testing request validation...")
    test.test_registration_request_validation()
    print("   ✓ Request validation working")
    
    print("\n5. Testing response model...")
    test.test_registration_response_model()
    print("   ✓ Response model working")
    
    print("\n" + "="*50)
    print("✅ All tests passed!")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_tests()