import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.src.api.nl_agent_api import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestNLAgentAPI:
    """NL Agent API 테스트"""

    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/v1/agents/nl-input/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @patch('backend.src.api.nl_agent_api.nl_integration')
    def test_process_description_success(self, mock_integration):
        """설명 처리 성공 테스트"""
        mock_integration.process_complete_request = AsyncMock(return_value={
            'requirements': {
                'description': 'Test app',
                'project_type': 'web_application',
                'technical_requirements': ['user management'],
                'non_functional_requirements': [],
                'technology_preferences': {},
                'constraints': [],
                'extracted_entities': {}
            },
            'processing_status': 'completed',
            'confidence_score': 0.8,
            'ambiguities': 0,
            'clarification_needed': False
        })
        
        response = client.post("/v1/agents/nl-input/process", json={
            "description": "Create a web application"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"
        assert data["confidence_score"] == 0.8

    @patch('backend.src.api.nl_agent_api.nl_integration')
    def test_process_description_with_clarification(self, mock_integration):
        """명확화 필요한 경우 테스트"""
        mock_integration.process_complete_request = AsyncMock(return_value={
            'requirements': {
                'description': 'Make an app',
                'project_type': 'general',
                'technical_requirements': [],
                'non_functional_requirements': [],
                'technology_preferences': {},
                'constraints': [],
                'extracted_entities': {}
            },
            'processing_status': 'needs_clarification',
            'confidence_score': 0.3,
            'ambiguities': 2,
            'clarification_needed': True,
            'clarification_questions': [
                {
                    'id': 'missing_tech_choice_frontend_framework',
                    'question': '프론트엔드 프레임워크를 선택하세요',
                    'options': ['React', 'Vue.js']
                }
            ]
        })
        
        response = client.post("/v1/agents/nl-input/process", json={
            "description": "Make an app"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["clarification_needed"] == True
        assert len(data["clarification_questions"]) > 0

    @patch('backend.src.api.nl_agent_api.nl_integration')
    def test_process_clarification(self, mock_integration):
        """명확화 응답 처리 테스트"""
        mock_integration.process_clarification_response = AsyncMock(return_value={
            'requirements': {
                'description': 'React web app',
                'project_type': 'web_application',
                'technical_requirements': ['user management'],
                'non_functional_requirements': [],
                'technology_preferences': {'frontend': ['React']},
                'constraints': [],
                'extracted_entities': {}
            },
            'processing_status': 'completed',
            'confidence_score': 0.9,
            'clarification_applied': True
        })
        
        response = client.post("/v1/agents/nl-input/clarify", json={
            "original_requirements": {
                "description": "Make an app",
                "project_type": "general"
            },
            "responses": {
                "missing_tech_choice_frontend_framework": "React"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["clarification_applied"] == True
        assert data["confidence_score"] == 0.9

    def test_process_multimodal_text_only(self):
        """텍스트만 있는 멀티모달 처리 테스트"""
        with patch('backend.src.api.nl_agent_api.nl_integration') as mock_integration:
            mock_integration.process_complete_request = AsyncMock(return_value={
                'requirements': {},
                'processing_status': 'completed',
                'confidence_score': 0.8,
                'ambiguities': 0,
                'clarification_needed': False
            })
            
            response = client.post("/v1/agents/nl-input/process-multimodal", data={
                "description": "Create a web app"
            })
            
            assert response.status_code == 200

    @patch('backend.src.api.nl_agent_api.nl_integration')
    def test_error_handling(self, mock_integration):
        """에러 처리 테스트"""
        mock_integration.process_complete_request = AsyncMock(return_value={
            'processing_status': 'error',
            'error_message': 'Processing failed',
            'error_type': 'ValueError'
        })
        
        response = client.post("/v1/agents/nl-input/process", json={
            "description": "Invalid input"
        })
        
        assert response.status_code == 500