import pytest
from unittest.mock import Mock, AsyncMock
from backend.src.agents.implementations.requirement_clarification import (
    RequirementClarificationSystem,
    Ambiguity,
    ClarificationQuestion
)
from backend.src.agents.implementations.nl_input_agent import ProjectRequirements

class TestRequirementClarificationSystem:
    """요구사항 명확화 시스템 테스트"""

    @pytest.fixture
    def clarification_system(self):
        return RequirementClarificationSystem()

    @pytest.fixture
    def sample_requirements(self):
        return ProjectRequirements(
            description="웹 애플리케이션을 만들어주세요",
            project_type="web_application",
            technical_requirements=["사용자 관리", "데이터 저장"],
            non_functional_requirements=[],
            technology_preferences={},
            constraints=[],
            extracted_entities={}
        )

    @pytest.fixture
    def complete_requirements(self):
        return ProjectRequirements(
            description="React와 Node.js로 1000명 사용자를 위한 인증 기능이 있는 웹앱",
            project_type="web_application",
            technical_requirements=["사용자 관리", "인증"],
            non_functional_requirements=["1000명 사용자 지원"],
            technology_preferences={"frontend": ["react"], "backend": ["node"]},
            constraints=[],
            extracted_entities={}
        )

    @pytest.mark.asyncio
    async def test_identify_ambiguities_missing_tech(self, clarification_system, sample_requirements):
        """기술 스택 누락 모호성 식별 테스트"""
        ambiguities = await clarification_system.identify_ambiguities(sample_requirements)
        
        # 프론트엔드, 백엔드 기술 스택이 없으므로 모호성 발견
        assert len(ambiguities) >= 2
        
        tech_ambiguities = [a for a in ambiguities if a.type == 'missing_tech_choice']
        assert len(tech_ambiguities) >= 2

    @pytest.mark.asyncio
    async def test_identify_ambiguities_missing_scale(self, clarification_system, sample_requirements):
        """규모 정보 누락 모호성 식별 테스트"""
        ambiguities = await clarification_system.identify_ambiguities(sample_requirements)
        
        scale_ambiguities = [a for a in ambiguities if a.type == 'missing_scale_info']
        assert len(scale_ambiguities) >= 1

    @pytest.mark.asyncio
    async def test_identify_ambiguities_missing_security(self, clarification_system, sample_requirements):
        """보안 정보 누락 모호성 식별 테스트"""
        ambiguities = await clarification_system.identify_ambiguities(sample_requirements)
        
        security_ambiguities = [a for a in ambiguities if a.type == 'missing_security_info']
        assert len(security_ambiguities) >= 1

    @pytest.mark.asyncio
    async def test_no_ambiguities_complete_requirements(self, clarification_system, complete_requirements):
        """완전한 요구사항에서 모호성 없음 테스트"""
        ambiguities = await clarification_system.identify_ambiguities(complete_requirements)
        
        # 완전한 요구사항이므로 모호성이 적어야 함
        assert len(ambiguities) <= 1  # 일부 모호성은 여전히 있을 수 있음

    @pytest.mark.asyncio
    async def test_generate_clarification_questions(self, clarification_system):
        """명확화 질문 생성 테스트"""
        ambiguities = [
            Ambiguity(
                type='missing_tech_choice',
                field='frontend_framework',
                severity='high'
            ),
            Ambiguity(
                type='missing_scale_info',
                field='expected_user_count',
                severity='medium'
            )
        ]
        
        questions = await clarification_system.generate_clarification_questions(ambiguities)
        
        assert len(questions) == 2
        
        # 우선순위 정렬 확인 (high가 먼저)
        assert questions[0].impact == 'high'
        assert questions[1].impact == 'medium'

    @pytest.mark.asyncio
    async def test_process_user_responses(self, clarification_system):
        """사용자 응답 처리 테스트"""
        questions = [
            ClarificationQuestion(
                id='missing_tech_choice_frontend_framework',
                category='missing_tech_choice',
                question='프론트엔드 프레임워크를 선택하세요',
                options=['React', 'Vue.js'],
                impact='high'
            )
        ]
        
        responses = {
            'missing_tech_choice_frontend_framework': 'React'
        }
        
        refined = await clarification_system.process_user_responses(questions, responses)
        
        assert refined.data['frontend_framework'] == 'React'

    def test_has_security_requirements_positive(self, clarification_system):
        """보안 요구사항 존재 확인 테스트 (긍정)"""
        requirements = ProjectRequirements(
            description="로그인 기능이 있는 웹앱",
            project_type="web_application",
            technical_requirements=["사용자 인증"],
            non_functional_requirements=[],
            technology_preferences={},
            constraints=[],
            extracted_entities={}
        )
        
        has_security = clarification_system._has_security_requirements(requirements)
        assert has_security == True

    def test_has_security_requirements_negative(self, clarification_system):
        """보안 요구사항 존재 확인 테스트 (부정)"""
        requirements = ProjectRequirements(
            description="간단한 계산기 앱",
            project_type="web_application",
            technical_requirements=["계산 기능"],
            non_functional_requirements=[],
            technology_preferences={},
            constraints=[],
            extracted_entities={}
        )
        
        has_security = clarification_system._has_security_requirements(requirements)
        assert has_security == False

    @pytest.mark.asyncio
    async def test_question_priority_sorting(self, clarification_system):
        """질문 우선순위 정렬 테스트"""
        ambiguities = [
            Ambiguity(type='missing_scale_info', field='users', severity='low'),
            Ambiguity(type='missing_tech_choice', field='frontend', severity='high'),
            Ambiguity(type='missing_security_info', field='auth', severity='medium')
        ]
        
        questions = await clarification_system.generate_clarification_questions(ambiguities)
        
        # high -> medium -> low 순서로 정렬되어야 함
        impacts = [q.impact for q in questions]
        expected_order = ['high', 'medium', 'low']
        assert impacts == expected_order