"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
async def memory_hub():
    """메모리 허브 픽스처."""
    from backend.packages.memory.hub import MemoryHub
    
    hub = MemoryHub()
    await hub.initialize()
    
    yield hub
    
    # 정리
    from backend.packages.memory.contexts import ContextType
    await hub.clear_context(ContextType.A_CTX)
    await hub.clear_context(ContextType.S_CTX)
    await hub.shutdown()


@pytest.fixture
def bedrock_config():
    """Bedrock 설정 픽스처."""
    return {
        "model": "claude-3-sonnet",
        "region": "us-east-1"
    }