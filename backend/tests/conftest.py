"""
Pytest Configuration
엔터프라이즈 테스트 설정 및 픽스처
"""

import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis
from unittest.mock import Mock, AsyncMock, patch
import jwt
from datetime import datetime, timedelta

# Set test environment
os.environ['ENVIRONMENT'] = 'testing'
os.environ['LOG_LEVEL'] = 'error'

# Import application components
from src.database.base import Base, get_db
from src.database.models import User, Project, Organization
from src.auth.jwt_handler import JWTHandler

# Test database URL (SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Test Redis
TEST_REDIS_URL = "redis://localhost:6379/15"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create test database session"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

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