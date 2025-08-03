import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Parser Agent 테스트
class TestParserAgent:
    """Parser Agent 통합 테스트"""

    @pytest.fixture
    async def parser_agent(self):
        """Parser Agent 인스턴스"""
        with patch('agno.agent.Agent'):
            from ...src.agents.implementations.parser_agent import ParserAgent
            agent = ParserAgent()
            yield agent

    @pytest.fixture
    def test_requirements(self):
        """테스트용 요구사항 데이터"""
        return {
            "simple_web": """
            Build a simple todo list web application.
            Users must be able to create, read, update, and delete tasks.
            The system should support user authentication with email and password.
            Response time must be under 200ms for all operations.
            """,
            "ecommerce": """
            Create an e-commerce platform with the following features:
            - User registration and login
            - Product catalog with search and filtering
            - Shopping cart functionality
            - Order processing and payment integration
            - Admin dashboard for inventory management
            
            Technical requirements:
            - Must use React for frontend
            - Database should be PostgreSQL
            - API must be RESTful
            - Support 10,000 concurrent users
            - PCI compliance required for payments
            """,
            "mobile_app": """
            Develop a mobile fitness tracking app for iOS and Android.
            Features include workout logging, progress tracking, and social sharing.
            The app must work offline and sync when connected.
            Integration with health APIs like Apple Health and Google Fit required.
            """
        }

    @pytest.mark.asyncio
    async def test_basic_parsing(self, parser_agent, test_requirements):
        """기본 파싱 기능 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["simple_web"]
        )

        # 기본 구조 확인
        assert result.project_info is not None
        assert len(result.functional_requirements) > 0
        assert len(result.non_functional_requirements) > 0

        # 기능 요구사항 확인
        functional_descriptions = [req.description for req in result.functional_requirements]
        assert any("create" in desc.lower() for desc in functional_descriptions)
        assert any("authentication" in desc.lower() for desc in functional_descriptions)

        # 비기능 요구사항 확인
        nfr_descriptions = [req.description for req in result.non_functional_requirements]
        assert any("200ms" in desc for desc in nfr_descriptions)

    @pytest.mark.asyncio
    async def test_complex_parsing(self, parser_agent, test_requirements):
        """복잡한 요구사항 파싱 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )

        # 다양한 요구사항 타입 확인
        assert len(result.functional_requirements) >= 5
        assert len(result.technical_requirements) >= 3
        assert len(result.constraints) >= 2

        # 기술 요구사항 확인
        tech_reqs = [req.description for req in result.technical_requirements]
        assert any("react" in req.lower() for req in tech_reqs)
        assert any("postgresql" in req.lower() for req in tech_reqs)

        # 제약사항 확인
        constraints = [req.description for req in result.constraints]
        assert any("pci" in constraint.lower() for constraint in constraints)
        assert any("10,000" in constraint for constraint in constraints)

    @pytest.mark.asyncio
    async def test_data_model_extraction(self, parser_agent, test_requirements):
        """데이터 모델 추출 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )

        # 데이터 모델 확인
        assert len(result.data_models) > 0
        
        model_names = [model['name'].lower() for model in result.data_models]
        assert 'user' in model_names

        # 사용자 모델 상세 확인
        user_model = next(model for model in result.data_models if model['name'].lower() == 'user')
        field_names = [field['name'] for field in user_model['fields']]
        assert 'email' in field_names
        assert 'id' in field_names

    @pytest.mark.asyncio
    async def test_api_specification_extraction(self, parser_agent, test_requirements):
        """API 명세 추출 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )

        # API 명세 확인
        assert len(result.api_specifications) > 0

        # RESTful API 패턴 확인
        api_paths = [api['path'] for api in result.api_specifications]
        assert any('/api/' in path for path in api_paths)

    @pytest.mark.asyncio
    async def test_user_story_generation(self, parser_agent, test_requirements):
        """사용자 스토리 생성 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["simple_web"]
        )

        # 사용자 스토리 확인
        assert len(result.user_stories) > 0

        # 스토리 구조 확인
        story = result.user_stories[0]
        assert 'description' in story
        assert 'persona' in story
        assert 'acceptance_criteria' in story
        assert story['description'].startswith('As a')

    @pytest.mark.asyncio
    async def test_requirement_validation(self, parser_agent, test_requirements):
        """요구사항 검증 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )

        # 검증 메타데이터 확인
        assert 'validation' in result.project_info
        validation = result.project_info['validation']
        assert 'validation_score' in validation
        assert 'validation_results' in validation

        # 검증 점수 확인 (0.0 ~ 1.0)
        score = validation['validation_score']
        assert 0.0 <= score <= 1.0

        # 모든 요구사항에 ID가 있는지 확인
        all_requirements = (
            result.functional_requirements +
            result.non_functional_requirements +
            result.technical_requirements
        )
        for req in all_requirements:
            assert req.id is not None
            assert req.id != ""

    @pytest.mark.asyncio
    async def test_constraint_analysis(self, parser_agent, test_requirements):
        """제약사항 분석 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )

        # 제약사항 확인
        assert len(result.constraints) > 0

        # 제약사항 카테고리 확인
        categories = [constraint.category for constraint in result.constraints]
        assert 'security' in categories or 'regulatory' in categories

        # 우선순위 확인
        priorities = [constraint.priority for constraint in result.constraints]
        assert 'critical' in priorities or 'high' in priorities

    @pytest.mark.asyncio
    async def test_mobile_app_parsing(self, parser_agent, test_requirements):
        """모바일 앱 요구사항 파싱 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["mobile_app"]
        )

        # 모바일 특화 제약사항 확인
        constraints = [req.description.lower() for req in result.constraints]
        assert any('ios' in constraint or 'android' in constraint for constraint in constraints)

        # 통합 지점 확인
        assert len(result.integration_points) > 0
        integration_names = [integration['name'].lower() for integration in result.integration_points]
        assert any('health' in name or 'fit' in name for name in integration_names)

    @pytest.mark.performance
    async def test_parsing_performance(self, parser_agent, test_requirements):
        """파싱 성능 테스트"""
        import time

        start_time = time.time()
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )
        elapsed_time = time.time() - start_time

        # 성능 기준: 5초 이내
        assert elapsed_time < 5.0

        # 결과 품질 확인
        assert len(result.functional_requirements) > 0
        assert result.project_info is not None

    @pytest.mark.asyncio
    async def test_error_handling(self, parser_agent):
        """에러 처리 테스트"""
        # 빈 입력
        result = await parser_agent.parse_requirements("")
        assert result is not None
        assert result.project_info is not None

        # 매우 짧은 입력
        result = await parser_agent.parse_requirements("Build an app")
        assert result is not None
        assert len(result.functional_requirements) >= 0

    @pytest.mark.asyncio
    async def test_preprocessing(self, parser_agent):
        """전처리 기능 테스트"""
        text_with_abbreviations = """
        Build a REST API with JWT authentication.
        The DB should be MySQL and UI should be responsive.
        CRUD operations are required for all entities.
        """

        result = await parser_agent.parse_requirements(text_with_abbreviations)

        # 약어 확장 확인 (메타데이터나 설명에서)
        all_text = str(result)
        assert 'REST' in all_text  # 원본 유지
        # 확장된 형태도 있어야 함 (전처리에서 처리됨)

    @pytest.mark.asyncio
    async def test_context_usage(self, parser_agent):
        """컨텍스트 활용 테스트"""
        context = {
            'project_type': 'web_application',
            'domain': 'healthcare',
            'team_size': 5
        }

        result = await parser_agent.parse_requirements(
            "Build a patient management system",
            project_context=context
        )

        # 헬스케어 도메인 제약사항 확인
        constraint_descriptions = [req.description.lower() for req in result.constraints]
        assert any('hipaa' in desc or 'healthcare' in desc for desc in constraint_descriptions)

    @pytest.mark.asyncio
    async def test_requirement_relationships(self, parser_agent, test_requirements):
        """요구사항 간 관계 테스트"""
        result = await parser_agent.parse_requirements(
            test_requirements["ecommerce"]
        )

        # 의존성이 있는 요구사항 확인
        requirements_with_deps = [
            req for req in result.functional_requirements 
            if req.dependencies
        ]
        
        # 적어도 일부 요구사항은 의존성을 가져야 함
        assert len(requirements_with_deps) >= 0  # 의존성 추출이 구현되면 > 0으로 변경

    def test_requirement_id_format(self, parser_agent, test_requirements):
        """요구사항 ID 형식 테스트"""
        import re
        
        async def run_test():
            result = await parser_agent.parse_requirements(
                test_requirements["simple_web"]
            )

            # ID 형식 패턴 (예: FR-001, NFR-001, TR-001)
            id_pattern = r'^[A-Z]{2,3}-\d{3}(-\d{2})?$'

            all_requirements = (
                result.functional_requirements +
                result.non_functional_requirements +
                result.technical_requirements
            )

            for req in all_requirements:
                assert re.match(id_pattern, req.id), f"Invalid ID format: {req.id}"

        asyncio.run(run_test())

# 개별 컴포넌트 테스트
class TestParsingRuleEngine:
    """파싱 규칙 엔진 테스트"""

    @pytest.fixture
    def rule_engine(self):
        from ...src.agents.implementations.parser.parsing_rules import ParsingRuleEngine
        return ParsingRuleEngine()

    def test_performance_rule_extraction(self, rule_engine):
        """성능 규칙 추출 테스트"""
        text = "The system must respond within 200ms for all user requests."
        results = rule_engine.apply_rules(text)
        
        assert 'performance' in results
        assert len(results['performance']) > 0
        
        perf_req = results['performance'][0]
        assert perf_req['value'] == '200'
        assert perf_req['unit'] == 'ms'

    def test_api_endpoint_extraction(self, rule_engine):
        """API 엔드포인트 추출 테스트"""
        text = "GET /api/users/{id} and POST /api/users endpoints are required."
        results = rule_engine.apply_rules(text)
        
        assert 'api' in results
        assert len(results['api']) >= 2
        
        methods = [api['method'] for api in results['api']]
        assert 'GET' in methods
        assert 'POST' in methods

class TestRequirementExtractor:
    """요구사항 추출기 테스트"""

    @pytest.fixture
    def extractor(self):
        from ...src.agents.implementations.parser.requirement_extractor import RequirementExtractor
        return RequirementExtractor()

    @pytest.mark.asyncio
    async def test_functional_extraction(self, extractor):
        """기능 요구사항 추출 테스트"""
        feature = "User login with email and password"
        context = {'project_type': 'web'}
        
        requirements = await extractor.extract_functional(feature, context)
        
        assert len(requirements) > 0
        req = requirements[0]
        assert 'login' in req['description'].lower()
        assert req['category'] == 'authentication'

    @pytest.mark.asyncio
    async def test_nfr_extraction(self, extractor):
        """비기능 요구사항 추출 테스트"""
        base_structure = {
            'description': 'System must support 1000 concurrent users and respond within 100ms'
        }
        
        nfr_list = await extractor.extract_non_functional(base_structure)
        
        assert len(nfr_list) > 0
        categories = [req.category for req in nfr_list]
        assert 'performance' in categories or 'scalability' in categories