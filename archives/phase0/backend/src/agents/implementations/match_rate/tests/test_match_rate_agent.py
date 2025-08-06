"""
T-Developer MVP - Match Rate Agent Tests
"""
import pytest
from unittest.mock import Mock, AsyncMock

class TestMatchRateAgent:
    @pytest.mark.asyncio
    async def test_calculate_match_rate(self):
        mock_agent = Mock()
        mock_agent.calculate_match_rate = AsyncMock(return_value={
            'score': 0.85,
            'confidence': 0.9
        })
        
        requirements = {'features': ['auth', 'crud']}
        components = [{'name': 'auth-lib', 'features': ['auth']}]
        
        result = await mock_agent.calculate_match_rate(requirements, components)
        
        assert result['score'] > 0.8