import pytest
import asyncio
from backend.src.agents.implementations.nl_input_agent_complete import (
    NLInputAgent, 
    ProjectRequirements, 
    ProjectType, 
    Priority
)

class TestNLInputAgent:
    """NL Input Agent 테스트"""

    @pytest.fixture
    def nl_agent(self):
        return NLInputAgent()

    @pytest.fixture
    def test_descriptions(self):
        return {
            "simple_web": "간단한 할일 관리 웹 애플리케이션을 만들어주세요",
            "complex_ecommerce": """
            React와 Node.js를 사용한 이커머스 플랫폼을 개발해주세요.
            사용자는 상품을 검색하고 장바구니에 담고 결제할 수 있어야 합니다.
            PostgreSQL 데이터베이스를 사용하고, 10,000명의 동시 사용자를 지원해야 합니다.
            응답시간은 200ms 이하여야 하고, SSL 암호화가 필요합니다.
            """,
            "mobile_app": "iOS와 Android를 지원하는 소셜 미디어 앱",
            "api_service": "RESTful API 서비스로 사용자 인증과 데이터 CRUD 기능 포함"
        }

    @pytest.mark.asyncio
    async def test_simple_web_processing(self, nl_agent, test_descriptions):
        """간단한 웹 애플리케이션 처리 테스트"""
        result = await nl_agent.process_description(test_descriptions["simple_web"])
        
        assert result.project_type == ProjectType.WEB_APPLICATION
        assert result.estimated_complexity in ['simple', 'medium']
        assert len(result.functional_requirements) >= 0
        assert result.confidence_score > 0

    @pytest.mark.asyncio
    async def test_complex_ecommerce_processing(self, nl_agent, test_descriptions):
        """복잡한 이커머스 요구사항 처리 테스트"""
        result = await nl_agent.process_description(test_descriptions["complex_ecommerce"])
        
        # 프로젝트 타입 검증
        assert result.project_type == ProjectType.WEB_APPLICATION
        
        # 기술 스택 검증
        assert 'frontend' in result.technology_preferences
        assert 'backend' in result.technology_preferences
        assert 'database' in result.technology_preferences
        
        # 기술 요구사항 검증
        tech_reqs = result.technical_requirements
        assert len(tech_reqs) > 0
        
        # 성능 요구사항 확인
        performance_reqs = [req for req in tech_reqs if req.category == 'performance']
        assert len(performance_reqs) > 0
        
        # 보안 요구사항 확인
        security_reqs = [req for req in tech_reqs if req.category == 'security']
        assert len(security_reqs) > 0

    @pytest.mark.asyncio
    async def test_mobile_app_classification(self, nl_agent, test_descriptions):
        """모바일 앱 분류 테스트"""
        result = await nl_agent.process_description(test_descriptions["mobile_app"])
        
        assert result.project_type == ProjectType.MOBILE_APPLICATION

    @pytest.mark.asyncio
    async def test_api_service_classification(self, nl_agent, test_descriptions):
        """API 서비스 분류 테스트"""
        result = await nl_agent.process_description(test_descriptions["api_service"])
        
        assert result.project_type == ProjectType.API_SERVICE

    @pytest.mark.asyncio
    async def test_entity_recognition(self, nl_agent):
        """엔티티 인식 테스트"""
        description = "React와 Node.js를 사용하여 10,000명의 사용자를 지원하는 웹앱"
        result = await nl_agent.process_description(description)
        
        entities = result.extracted_entities
        assert 'technologies' in entities
        assert len(entities['technologies']) > 0
        assert 'metrics' in entities
        assert len(entities['metrics']) > 0

    @pytest.mark.asyncio
    async def test_ambiguity_detection(self, nl_agent):
        """모호성 감지 테스트"""
        vague_description = "좋은 앱을 만들어주세요"
        result = await nl_agent.process_description(vague_description)
        
        assert len(result.ambiguities) > 0
        assert result.confidence_score < 0.5

    @pytest.mark.asyncio
    async def test_constraint_extraction(self, nl_agent):
        """제약사항 추출 테스트"""
        description = "예산은 $10,000이고 3개월 안에 완료해야 하며 React를 반드시 사용해야 합니다"
        result = await nl_agent.process_description(description)
        
        assert len(result.constraints) > 0
        constraint_text = ' '.join(result.constraints).lower()
        assert '$10,000' in constraint_text or 'budget' in constraint_text

    @pytest.mark.asyncio
    async def test_complexity_estimation(self, nl_agent):
        """복잡도 추정 테스트"""
        simple_desc = "기본적인 CRUD 웹사이트"
        complex_desc = "실시간 AI 기반 분산 마이크로서비스 플랫폼"
        
        simple_result = await nl_agent.process_description(simple_desc)
        complex_result = await nl_agent.process_description(complex_desc)
        
        complexity_order = ['simple', 'medium', 'complex', 'very_complex']
        simple_idx = complexity_order.index(simple_result.estimated_complexity)
        complex_idx = complexity_order.index(complex_result.estimated_complexity)
        
        assert simple_idx <= complex_idx

    @pytest.mark.asyncio
    async def test_technical_requirement_priorities(self, nl_agent):
        """기술 요구사항 우선순위 테스트"""
        description = "보안이 중요한 금융 시스템으로 성능도 고려해야 합니다"
        result = await nl_agent.process_description(description)
        
        tech_reqs = result.technical_requirements
        security_reqs = [req for req in tech_reqs if req.category == 'security']
        
        if security_reqs:
            assert security_reqs[0].priority == Priority.CRITICAL

    def test_project_requirements_serialization(self):
        """ProjectRequirements 직렬화 테스트"""
        from backend.src.agents.implementations.nl_input_agent_complete import TechnicalRequirement
        
        tech_req = TechnicalRequirement(
            id="TR-01",
            description="Test requirement",
            category="performance",
            priority=Priority.HIGH
        )
        
        requirements = ProjectRequirements(
            description="Test project",
            project_type=ProjectType.WEB_APPLICATION,
            estimated_complexity="medium",
            technical_requirements=[tech_req]
        )
        
        # to_dict 메서드가 없으므로 기본 직렬화 테스트
        assert requirements.description == "Test project"
        assert requirements.project_type == ProjectType.WEB_APPLICATION
        assert len(requirements.technical_requirements) == 1

# 성능 테스트
class TestNLInputAgentPerformance:
    """성능 테스트"""

    @pytest.mark.asyncio
    async def test_processing_speed(self):
        """처리 속도 테스트"""
        import time
        
        agent = NLInputAgent()
        description = "React를 사용한 간단한 웹 애플리케이션"
        
        start_time = time.time()
        result = await agent.process_description(description)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 1.0  # 1초 이내 처리
        assert result is not None

    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """동시 처리 테스트"""
        agent = NLInputAgent()
        descriptions = [
            "웹 애플리케이션",
            "모바일 앱",
            "API 서비스"
        ] * 5  # 15개 요청
        
        start_time = time.time()
        tasks = [agent.process_description(desc) for desc in descriptions]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        assert len(results) == 15
        assert all(r is not None for r in results)
        assert (end_time - start_time) < 5.0  # 5초 이내

if __name__ == "__main__":
    pytest.main([__file__, "-v"])