"""
Simplified pytest configuration without database dependencies
데이터베이스 의존성 없는 간단한 pytest 설정
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_project_data():
    """Mock 프로젝트 데이터"""
    return {
        "id": "test_project_123",
        "name": "Test Project",
        "description": "A test project",
        "status": "draft",
        "created_at": "2024-01-01T00:00:00"
    }


@pytest.fixture
def mock_user_data():
    """Mock 사용자 데이터"""
    return {
        "id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "is_active": True
    }


@pytest.fixture
def mock_agent_data():
    """Mock 에이전트 데이터"""
    return {
        "nl_input": {
            "name": "NLInputAgent",
            "status": "idle",
            "progress": 0
        },
        "ui_selection": {
            "name": "UISelectionAgent",
            "status": "idle",
            "progress": 0
        },
        "parser": {
            "name": "ParserAgent",
            "status": "idle",
            "progress": 0
        },
        "component_decision": {
            "name": "ComponentDecisionAgent",
            "status": "idle",
            "progress": 0
        },
        "match_rate": {
            "name": "MatchRateAgent",
            "status": "idle",
            "progress": 0
        },
        "search": {
            "name": "SearchAgent",
            "status": "idle",
            "progress": 0
        },
        "generation": {
            "name": "GenerationAgent",
            "status": "idle",
            "progress": 0
        },
        "assembly": {
            "name": "AssemblyAgent",
            "status": "idle",
            "progress": 0
        },
        "download": {
            "name": "DownloadAgent",
            "status": "idle",
            "progress": 0
        }
    }


@pytest.fixture
def mock_pipeline_result():
    """Mock 파이프라인 결과"""
    return {
        "success": True,
        "project_id": "test_project_123",
        "project_path": "/tmp/test_project_123",
        "metadata": {
            "files_generated": 15,
            "match_score": 92.5,
            "execution_time": 12.34,
            "agents_executed": 9,
            "agents_succeeded": 9
        },
        "errors": []
    }


# 환경 변수 설정
import os
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"