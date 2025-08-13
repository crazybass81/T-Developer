"""
NL Input Agent 테스트 스위트
목표 커버리지: 80% 이상
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lambda.agents.nl_input_agent import (
    NLInputAgent,
    ProjectType,
    ProjectRequirements,
    ExtractedEntities,
    TechnologyPreferences,
    lambda_handler
)


class TestNLInputAgent:
    """NL Input Agent 단위 테스트"""

    @pytest.fixture
    def agent(self):
        """테스트용 에이전트 인스턴스"""
        with patch('src.lambda.agents.nl_input_agent.ssm') as mock_ssm:
            mock_ssm.get_parameters_by_path.return_value = {
                'Parameters': [
                    {'Name': '/t-developer/test/nl-input-agent/max_input_length', 'Value': '5000'},
                    {'Name': '/t-developer/test/nl-input-agent/min_confidence_score', 'Value': '0.3'}
                ]
            }
            return NLInputAgent('test')

    def test_init(self, agent):
        """초기화 테스트"""
        assert agent.environment == 'test'
        assert agent.config['max_input_length'] == '5000'
        assert len(agent.project_patterns) > 0
        assert len(agent.feature_patterns) > 0

    def test_validate_input_empty(self, agent):
        """빈 입력 검증 테스트"""
        with pytest.raises(ValueError, match="입력이 비어있습니다"):
            agent._validate_input("")

        with pytest.raises(ValueError, match="입력이 비어있습니다"):
            agent._validate_input("   ")

    def test_validate_input_too_long(self, agent):
        """너무 긴 입력 검증 테스트"""
        long_input = "a" * 6000
        with pytest.raises(ValueError, match="입력이 너무 깁니다"):
            agent._validate_input(long_input)

    def test_validate_input_dangerous(self, agent):
        """위험한 입력 검증 테스트"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "DROP TABLE users;",
            "javascript:alert(1)",
            "onclick='malicious()'"
        ]

        for dangerous in dangerous_inputs:
            with pytest.raises(ValueError, match="위험한 입력"):
                agent._validate_input(dangerous)

    def test_detect_project_type_web(self, agent):
        """웹 프로젝트 타입 감지 테스트"""
        queries = [
            "웹사이트를 만들어줘",
            "홈페이지 제작이 필요해",
            "React web application",
            "프론트엔드 개발"
        ]

        for query in queries:
            result = agent._detect_project_type(query)
            assert result == ProjectType.WEB_APP

    def test_detect_project_type_mobile(self, agent):
        """모바일 프로젝트 타입 감지 테스트"""
        queries = [
            "모바일 앱을 만들어줘",
            "iOS 앱 개발",
            "Android application",
            "React Native 앱"
        ]

        for query in queries:
            result = agent._detect_project_type(query)
            assert result == ProjectType.MOBILE_APP

    def test_detect_project_type_unknown(self, agent):
        """알 수 없는 프로젝트 타입 테스트"""
        query = "무언가를 만들어줘"
        result = agent._detect_project_type(query)
        assert result == ProjectType.UNKNOWN

    def test_extract_functional_requirements(self, agent):
        """기능 요구사항 추출 테스트"""
        query = "로그인 기능과 검색 기능이 있는 웹사이트를 만들어줘. 결제도 필요하고 알림 기능도 포함해줘."

        requirements = agent._extract_functional_requirements(query)

        assert len(requirements) > 0
        assert any("로그인" in req or "인증" in req for req in requirements)
        assert any("검색" in req for req in requirements)
        assert any("결제" in req for req in requirements)
        assert any("알림" in req for req in requirements)

    def test_extract_non_functional_requirements(self, agent):
        """비기능 요구사항 추출 테스트"""
        query = "빠른 성능과 높은 보안이 필요하고, 모바일에서도 잘 작동해야 해"

        requirements = agent._extract_non_functional_requirements(query)

        assert len(requirements) > 0
        assert any("성능" in req for req in requirements)
        assert any("보안" in req for req in requirements)
        assert any("반응형" in req or "모바일" in req for req in requirements)

    def test_extract_technology_preferences(self, agent):
        """기술 선호사항 추출 테스트"""
        query = "React를 사용하고 PostgreSQL 데이터베이스와 Tailwind CSS를 써서 만들어줘"

        tech_prefs = agent._extract_technology_preferences(query, None)

        assert tech_prefs.framework == "react"
        assert tech_prefs.database == "postgresql"
        assert tech_prefs.styling == "tailwind"

    def test_extract_technology_preferences_with_framework(self, agent):
        """프레임워크 명시 테스트"""
        query = "웹사이트를 만들어줘"

        tech_prefs = agent._extract_technology_preferences(query, "vue")

        assert tech_prefs.framework == "vue"

    def test_extract_entities(self, agent):
        """엔티티 추출 테스트"""
        query = "홈 페이지와 로그인 페이지가 있고, 헤더와 푸터 컴포넌트가 필요해. 사용자와 상품 데이터 모델도 만들어줘."

        entities = agent._extract_entities(query)

        assert len(entities.pages) > 0
        assert any("홈" in page for page in entities.pages)
        assert any("로그인" in page for page in entities.pages)

        assert len(entities.components) > 0
        assert any("헤더" in comp for comp in entities.components)
        assert any("푸터" in comp for comp in entities.components)

        assert len(entities.data_models) > 0
        assert any("사용자" in model for model in entities.data_models)
        assert any("상품" in model for model in entities.data_models)

    def test_extract_constraints(self, agent):
        """제약사항 추출 테스트"""
        query = "2주 안에 완성해야 하고, GDPR 규정을 준수해야 해"

        constraints = agent._extract_constraints(query)

        assert len(constraints) > 0
        assert any("2주" in c for c in constraints)
        assert any("개인정보" in c or "GDPR" in c for c in constraints)

    def test_evaluate_complexity_low(self, agent):
        """낮은 복잡도 평가 테스트"""
        functional_reqs = ["로그인"]
        entities = ExtractedEntities(
            pages=["홈"],
            components=["헤더"],
            actions=[],
            data_models=[],
            apis=[],
            features=[]
        )
        tech_prefs = TechnologyPreferences()

        complexity = agent._evaluate_complexity(functional_reqs, entities, tech_prefs)
        assert complexity == "low"

    def test_evaluate_complexity_high(self, agent):
        """높은 복잡도 평가 테스트"""
        functional_reqs = ["로그인", "검색", "결제", "알림", "채팅"]
        entities = ExtractedEntities(
            pages=["홈", "로그인", "프로필", "대시보드"],
            components=["헤더", "푸터", "사이드바", "모달"],
            actions=["생성", "조회", "수정", "삭제"],
            data_models=["사용자", "상품", "주문"],
            apis=["GET", "POST"],
            features=["authentication", "payment", "realtime"]
        )
        tech_prefs = TechnologyPreferences(
            framework="react",
            database="postgresql",
            authentication="oauth2"
        )

        complexity = agent._evaluate_complexity(functional_reqs, entities, tech_prefs)
        assert complexity in ["high", "very-high"]

    def test_calculate_confidence_score(self, agent):
        """신뢰도 점수 계산 테스트"""
        # 높은 신뢰도
        high_confidence = agent._calculate_confidence_score(
            ProjectType.WEB_APP,
            ["요구사항1", "요구사항2", "요구사항3"],
            ExtractedEntities(
                pages=["페이지1", "페이지2"],
                components=["컴포넌트1"],
                actions=[],
                data_models=["모델1"],
                apis=[],
                features=["feature1", "feature2"]
            )
        )
        assert high_confidence > 0.5

        # 낮은 신뢰도
        low_confidence = agent._calculate_confidence_score(
            ProjectType.UNKNOWN,
            [],
            ExtractedEntities([], [], [], [], [], [])
        )
        assert low_confidence < 0.5

    def test_process_input_success(self, agent):
        """전체 처리 성공 테스트"""
        query = "React로 Todo 앱을 만들어줘. 로그인 기능과 데이터베이스가 필요해."

        with patch.object(agent, '_validate_input'):
            result = agent.process_input(query)

        assert isinstance(result, ProjectRequirements)
        assert result.description == query
        assert result.project_type != "unknown"
        assert len(result.functional_requirements) > 0
        assert result.confidence_score > 0
        assert result.estimated_complexity in ["low", "medium", "high", "very-high"]

    def test_process_input_with_framework(self, agent):
        """프레임워크 지정 처리 테스트"""
        query = "웹사이트를 만들어줘"

        with patch.object(agent, '_validate_input'):
            result = agent.process_input(query, framework="vue")

        assert result.technology_preferences.framework == "vue"

    @patch('src.lambda.agents.nl_input_agent.time.time')
    def test_process_input_metrics(self, mock_time, agent):
        """메트릭 기록 테스트"""
        mock_time.side_effect = [0, 1, 1]  # start, end, metadata

        query = "간단한 웹사이트"

        with patch.object(agent, '_validate_input'):
            result = agent.process_input(query)

        assert len(agent.processing_times) == 1
        assert agent.processing_times[0] == 1.0

    def test_process_input_error_handling(self, agent):
        """에러 처리 테스트"""
        with pytest.raises(ValueError):
            agent.process_input("")

        with patch.object(agent, '_detect_project_type', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                agent.process_input("정상 쿼리")


class TestLambdaHandler:
    """Lambda 핸들러 테스트"""

    @patch('src.lambda.agents.nl_input_agent.NLInputAgent')
    def test_lambda_handler_success(self, mock_agent_class):
        """Lambda 핸들러 성공 테스트"""
        mock_agent = Mock()
        mock_agent.process_input.return_value = ProjectRequirements(
            description="test",
            project_type="web-application",
            functional_requirements=[],
            non_functional_requirements=[],
            technology_preferences=TechnologyPreferences(),
            constraints=[],
            extracted_entities=ExtractedEntities([], [], [], [], [], []),
            confidence_score=0.8,
            estimated_complexity="medium",
            metadata={}
        )
        mock_agent_class.return_value = mock_agent

        event = {
            'body': json.dumps({
                'query': 'Test query',
                'framework': 'react'
            })
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        assert 'body' in response
        body = json.loads(response['body'])
        assert body['project_type'] == 'web-application'
        assert body['confidence_score'] == 0.8

    @patch('src.lambda.agents.nl_input_agent.NLInputAgent')
    def test_lambda_handler_validation_error(self, mock_agent_class):
        """Lambda 핸들러 검증 에러 테스트"""
        mock_agent = Mock()
        mock_agent.process_input.side_effect = ValueError("Invalid input")
        mock_agent_class.return_value = mock_agent

        event = {
            'body': json.dumps({
                'query': ''
            })
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert body['error']['code'] == 'VALIDATION_ERROR'

    @patch('src.lambda.agents.nl_input_agent.NLInputAgent')
    def test_lambda_handler_internal_error(self, mock_agent_class):
        """Lambda 핸들러 내부 에러 테스트"""
        mock_agent = Mock()
        mock_agent.process_input.side_effect = Exception("Unexpected error")
        mock_agent_class.return_value = mock_agent

        event = {
            'body': json.dumps({
                'query': 'Test query'
            })
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
        assert body['error']['code'] == 'INTERNAL_ERROR'

    def test_lambda_handler_malformed_event(self):
        """잘못된 이벤트 처리 테스트"""
        event = {
            'body': 'not json'
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.lambda.agents.nl_input_agent", "--cov-report=term-missing"])
