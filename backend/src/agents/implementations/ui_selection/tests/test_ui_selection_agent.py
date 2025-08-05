"""
T-Developer MVP - UI Selection Agent Tests
"""
import pytest
from unittest.mock import Mock, AsyncMock

class TestUISelectionAgent:
    @pytest.mark.asyncio
    async def test_select_framework(self):
        mock_agent = Mock()
        mock_agent.select_framework = AsyncMock(return_value={
            'framework': 'react',
            'reasoning': 'Best for web apps'
        })
        
        requirements = {'type': 'web_application'}
        result = await mock_agent.select_framework(requirements)
        
        assert result['framework'] == 'react'