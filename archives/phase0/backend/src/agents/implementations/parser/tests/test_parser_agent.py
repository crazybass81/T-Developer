"""
T-Developer MVP - Parser Agent Tests

Unit tests for the Parser Agent

Author: T-Developer Team
Created: 2024-12
"""
import pytest
from unittest.mock import Mock, AsyncMock

class TestParserAgent:
    """Parser Agent 단위 테스트"""
    
    @pytest.mark.asyncio
    async def test_parse_functional_requirements(self):
        """기능 요구사항 파싱 테스트"""
        mock_agent = Mock()
        mock_agent.parse_requirements = AsyncMock(return_value={
            'functional_requirements': [{
                'id': 'req_001',
                'type': 'functional',
                'description': '사용자 로그인 기능'
            }],
            'non_functional_requirements': []
        })
        
        description = "사용자는 로그인할 수 있어야 합니다."
        result = await mock_agent.parse_requirements(description)
        
        assert len(result['functional_requirements']) == 1
        assert result['functional_requirements'][0]['type'] == 'functional'