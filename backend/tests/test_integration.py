import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app
from backend.src.agents.implementations.nl_integration import NLInputAgentIntegration

client = TestClient(app)

class TestNLInputAgentIntegration:
    """NL Input Agent 통합 테스트"""

    def test_api_health(self):
        """API 헬스 체크"""
        response = client.get("/v1/agents/nl-input/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        assert "T-Developer NL Input Agent" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """완전한 워크플로우 테스트"""
        integration = NLInputAgentIntegration()
        
        # 1. 기본 처리
        result = await integration.process_complete_request([
            "React와 Node.js를 사용한 웹 애플리케이션을 만들어주세요"
        ])
        
        assert result['processing_status'] in ['completed', 'needs_clarification']
        assert 'requirements' in result
        assert 'confidence_score' in result

    @pytest.mark.asyncio 
    async def test_performance_target(self):
        """성능 목표 달성 테스트"""
        import time
        
        integration = NLInputAgentIntegration()
        
        start_time = time.time()
        result = await integration.process_complete_request([
            "간단한 할일 관리 앱을 만들어주세요"
        ])
        elapsed = time.time() - start_time
        
        # 2초 이하 목표
        assert elapsed < 2.0
        assert result['processing_status'] != 'error'

    def test_api_error_handling(self):
        """API 에러 처리 테스트"""
        response = client.post("/v1/agents/nl-input/process", json={})
        assert response.status_code == 422  # Validation error