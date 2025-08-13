"""
Pytest Configuration
엔터프라이즈 테스트 설정 및 픽스처
"""

import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import jwt
from datetime import datetime, timedelta

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["LOG_LEVEL"] = "error"
os.environ["TESTING"] = "true"

# Test Redis
TEST_REDIS_URL = "redis://localhost:6379/15"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB client for testing"""
    with patch("boto3.resource") as mock_resource:
        # Create mock DynamoDB table
        mock_table = Mock()
        mock_table.put_item = AsyncMock(
            return_value={"ResponseMetadata": {"HTTPStatusCode": 200}}
        )
        mock_table.get_item = AsyncMock(return_value={"Item": {"id": "test_id"}})
        mock_table.query = AsyncMock(return_value={"Items": []})
        mock_table.scan = AsyncMock(return_value={"Items": []})
        mock_table.delete_item = AsyncMock(
            return_value={"ResponseMetadata": {"HTTPStatusCode": 200}}
        )

        mock_resource.return_value.Table.return_value = mock_table
        yield mock_resource


@pytest.fixture
def dynamodb_client():
    """Mock DynamoDB client with common operations"""
    client = Mock()
    client.put_item = AsyncMock(
        return_value={"ResponseMetadata": {"HTTPStatusCode": 200}}
    )
    client.get_item = AsyncMock(return_value={"Item": {}})
    client.query = AsyncMock(return_value={"Items": [], "Count": 0})
    client.scan = AsyncMock(return_value={"Items": [], "Count": 0})
    client.delete_item = AsyncMock(
        return_value={"ResponseMetadata": {"HTTPStatusCode": 200}}
    )
    client.create_table = AsyncMock(
        return_value={"TableDescription": {"TableStatus": "ACTIVE"}}
    )
    return client


@pytest.fixture
def mock_bedrock():
    """Mock Bedrock client"""
    with patch("boto3.client") as mock:
        yield mock


@pytest.fixture
def sample_project():
    """Sample project data for testing"""
    return {
        "id": "test_project_001",
        "name": "Test Project",
        "description": "테스트용 React 웹 애플리케이션",
        "type": "web_application",
        "framework": "react",
    }
