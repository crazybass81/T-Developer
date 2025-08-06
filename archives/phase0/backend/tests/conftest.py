"""
T-Developer MVP - Test Configuration

pytest configuration and fixtures for integration and E2E tests

Author: T-Developer Team
Created: 2024-12
"""
import pytest
import asyncio
import os
from unittest.mock import Mock, patch

# Set test environment
os.environ['NODE_ENV'] = 'test'
os.environ['LOG_LEVEL'] = 'error'

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB client"""
    with patch('boto3.resource') as mock:
        yield mock

@pytest.fixture
def mock_bedrock():
    """Mock Bedrock client"""
    with patch('boto3.client') as mock:
        yield mock

@pytest.fixture
def sample_project():
    """Sample project data for testing"""
    return {
        'id': 'test_project_001',
        'name': 'Test Project',
        'description': '테스트용 React 웹 애플리케이션',
        'type': 'web_application',
        'framework': 'react'
    }