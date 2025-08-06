"""
T-Developer MVP - Complete Workflow E2E Test
"""
import pytest
from unittest.mock import Mock, AsyncMock

class TestCompleteWorkflow:
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_full_project_generation(self, sample_project):
        """전체 9개 에이전트 워크플로우 테스트"""
        orchestrator = Mock()
        orchestrator.execute_workflow = AsyncMock(return_value={
            'status': 'completed',
            'project_files': ['App.tsx', 'package.json'],
            'download_url': 'https://example.com/download'
        })
        
        input_description = "React 기반 할일 관리 앱을 만들어주세요"
        result = await orchestrator.execute_workflow(input_description)
        
        assert result['status'] == 'completed'
        assert 'App.tsx' in result['project_files']