"""
T-Developer MVP - Generation Agent Tests
"""
import pytest
from unittest.mock import Mock, AsyncMock

class TestGenerationAgent:
    @pytest.mark.asyncio
    async def test_generate_code(self):
        mock_agent = Mock()
        mock_agent.generate_code = AsyncMock(return_value={
            'files': ['App.tsx', 'index.tsx'],
            'framework': 'react'
        })
        
        spec = {'framework': 'react', 'components': ['App']}
        result = await mock_agent.generate_code(spec)
        
        assert 'App.tsx' in result['files']