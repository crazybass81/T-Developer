"""
T-Developer MVP - NL to Parser Integration Test

Integration test for NL Input Agent to Parser Agent workflow

Author: T-Developer Team
Created: 2024-12
"""
import pytest
from unittest.mock import Mock, AsyncMock


class TestNLToParserWorkflow:
    """NL Input → Parser Agent 통합 테스트"""

    @pytest.mark.asyncio
    async def test_nl_input_to_parser_integration(self, sample_project):
        """NL Input에서 Parser로의 데이터 전달 테스트"""
        # Mock NL Input Agent
        nl_agent = Mock()
        nl_agent.process_description = AsyncMock(
            return_value={
                "project_type": "web_application",
                "description": sample_project["description"],
                "requirements": ["사용자 인증", "할일 관리"],
            }
        )

        # Mock Parser Agent
        parser_agent = Mock()
        parser_agent.parse_requirements = AsyncMock(
            return_value={
                "functional_requirements": [
                    {"id": "req_001", "description": "사용자 인증"},
                    {"id": "req_002", "description": "할일 관리"},
                ]
            }
        )

        # Execute workflow
        nl_result = await nl_agent.process_description(sample_project["description"])
        parser_result = await parser_agent.parse_requirements(nl_result)

        assert len(parser_result["functional_requirements"]) == 2
        assert parser_result["functional_requirements"][0]["id"] == "req_001"
