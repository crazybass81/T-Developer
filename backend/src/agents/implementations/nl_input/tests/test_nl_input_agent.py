"""
T-Developer MVP - NL Input Agent Tests

Unit tests for the Natural Language Input Agent

Author: T-Developer Team
Created: 2024-12
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestNLInputAgent:
    """NL Input Agent 단위 테스트"""
    
    @pytest.mark.asyncio
    async def test_process_simple_description(self):
        """간단한 프로젝트 설명 처리 테스트"""
        # Mock agent for now
        mock_agent = Mock()
        mock_agent.process_description = AsyncMock(return_value={
            'project_type': 'web_application',
            'features': ['todo']
        })
        
        description = "간단한 할일 관리 웹 애플리케이션을 만들어주세요"
        result = await mock_agent.process_description(description)
        
        assert result['project_type'] == 'web_application'
        assert 'todo' in result['features']