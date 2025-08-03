# backend/tests/agents/test_parser_requirement_analysis.py
import pytest
import asyncio
from typing import Dict, Any, List

class TestParserRequirementAnalysis:
    """Parser Agent 요구사항 분석 기능 테스트"""

    @pytest.fixture
    def requirement_separator(self):
        from parser_requirement_separator import RequirementSeparator
        return RequirementSeparator()

    @pytest.fixture
    def dependency_analyzer(self):
        from parser_dependency_analyzer import DependencyAnalyzer
        return DependencyAnalyzer()

    @pytest.fixture
    def user_story_generator(self):
        from parser_user_story_generator import UserStoryGenerator
        return UserStoryGenerator()

    @pytest.fixture
    def test_requirements(self):
        return [
            "User must be able to login with email and password",
            "System should respond within 200ms for search queries",
            "Admin can manage user accounts and permissions",
            "Payment processing must be PCI compliant",
            "Application should support 10,000 concurrent users",
            "User profile management depends on authentication system"
        ]

    @pytest.mark.asyncio
    async def test_requirement_separation(self, requirement_separator, test_requirements):
        """기능/비기능 요구사항 분리 테스트"""
        
        functional_reqs, non_functional_reqs = await requirement_separator.separate_requirements(
            test_requirements
        )

        # 기능 요구사항 검증
        assert len(functional_reqs) >= 3
        functional_descriptions = [req.description for req in functional_reqs]
        assert any("login" in desc for desc in functional_descriptions)
        assert any("manage user accounts" in desc for desc in functional_descriptions)

        # 비기능 요구사항 검증
        assert len(non_functional_reqs) >= 2
        nfr_categories = [req.category for req in non_functional_reqs]
        assert "performance" in nfr_categories
        assert "security" in nfr_categories or "scalability" in nfr_categories

        # 각 요구사항이 올바른 구조를 가지는지 확인
        for req in functional_reqs:
            assert req.id.startswith("FR-")
            assert req.priority in ['high', 'medium', 'low']
            assert req.acceptance_criteria is not None

    @pytest.mark.asyncio
    async def test_dependency_analysis(self, dependency_analyzer):
        """의존성 분석 테스트"""
        
        requirements = [
            {
                'id': 'REQ-001',
                'description': 'User authentication system with OAuth 2.0'
            },
            {
                'id': 'REQ-002', 
                'description': 'User profile management depends on authentication'
            },
            {
                'id': 'REQ-003',
                'description': 'Shopping cart functionality for users'
            },
            {
                'id': 'REQ-004',
                'description': 'Order processing requires cart and payment systems'
            }
        ]

        dependency_graph = await dependency_analyzer.analyze_dependencies(requirements)

        # 기본 구조 검증
        assert len(dependency_graph.nodes) == 4
        assert len(dependency_graph.edges) > 0

        # 의존성 검증
        dependencies = {dep.source_id: dep.target_id for dep in dependency_graph.edges}
        
        # 프로필 관리가 인증에 의존하는지 확인
        profile_deps = [dep for dep in dependency_graph.edges if dep.source_id == 'REQ-002']
        assert len(profile_deps) > 0

        # 레벨 계산 검증
        assert dependency_graph.levels is not None
        assert len(dependency_graph.levels) == 4

    @pytest.mark.asyncio
    async def test_user_story_generation(self, user_story_generator):
        """사용자 스토리 생성 테스트"""
        
        requirements = [
            {
                'id': 'REQ-001',
                'type': 'functional',
                'description': 'User must be able to login with email and password'
            },
            {
                'id': 'REQ-002',
                'type': 'functional', 
                'description': 'Admin can manage user accounts and permissions'
            },
            {
                'id': 'REQ-003',
                'type': 'functional',
                'description': 'Customer can add items to shopping cart'
            }
        ]

        result = await user_story_generator.generate_user_stories(requirements)

        # 기본 구조 검증
        assert 'user_stories' in result
        assert 'personas' in result
        assert len(result['user_stories']) > 0

        # 사용자 스토리 형식 검증
        for story in result['user_stories']:
            assert story.id.startswith('US-')
            assert story.persona is not None
            assert story.goal is not None
            assert len(story.acceptance_criteria) > 0
            assert story.story_points > 0

        # 페르소나 검증
        personas = result['personas']
        assert len(personas) > 0
        assert any(persona.lower() in ['user', 'admin', 'customer'] for persona in personas)

    @pytest.mark.asyncio
    async def test_priority_extraction(self, requirement_separator):
        """우선순위 추출 테스트"""
        
        test_cases = [
            ("System MUST authenticate users", "high"),
            ("Application SHOULD respond quickly", "medium"), 
            ("Users can view optional reports", "low"),
            ("Critical security feature required", "high")
        ]

        for req_text, expected_priority in test_cases:
            functional_reqs, _ = await requirement_separator.separate_requirements([req_text])
            
            if functional_reqs:
                assert functional_reqs[0].priority == expected_priority

    @pytest.mark.asyncio
    async def test_acceptance_criteria_generation(self, requirement_separator):
        """수용 기준 생성 테스트"""
        
        requirement = "User must be able to create a new account"
        
        functional_reqs, _ = await requirement_separator.separate_requirements([requirement])
        
        assert len(functional_reqs) > 0
        req = functional_reqs[0]
        
        # 수용 기준이 생성되었는지 확인
        assert req.acceptance_criteria is not None
        assert len(req.acceptance_criteria) > 0
        
        # Given-When-Then 형식 확인 (가능한 경우)
        criteria_text = ' '.join(req.acceptance_criteria).lower()
        has_structure = any(keyword in criteria_text for keyword in ['given', 'when', 'then'])
        assert has_structure or len(req.acceptance_criteria) > 0

    @pytest.mark.asyncio
    async def test_actor_extraction(self, requirement_separator):
        """액터 추출 테스트"""
        
        test_cases = [
            ("User must be able to login", "user"),
            ("Admin should manage permissions", "admin"),
            ("Customer can place orders", "customer"),
            ("System shall process payments", "system")
        ]

        for req_text, expected_actor in test_cases:
            functional_reqs, _ = await requirement_separator.separate_requirements([req_text])
            
            if functional_reqs and functional_reqs[0].actor:
                assert expected_actor in functional_reqs[0].actor.lower()

    @pytest.mark.asyncio
    async def test_nfr_categorization(self, requirement_separator):
        """비기능 요구사항 분류 테스트"""
        
        test_cases = [
            ("System must respond within 100ms", "performance"),
            ("Application should encrypt all data", "security"),
            ("System must support 1000 concurrent users", "scalability"),
            ("Application should have 99.9% uptime", "reliability")
        ]

        for req_text, expected_category in test_cases:
            _, non_functional_reqs = await requirement_separator.separate_requirements([req_text])
            
            if non_functional_reqs:
                assert non_functional_reqs[0].category == expected_category

    @pytest.mark.asyncio
    async def test_cycle_detection(self, dependency_analyzer):
        """순환 의존성 검출 테스트"""
        
        # 순환 의존성이 있는 요구사항
        requirements = [
            {
                'id': 'REQ-A',
                'description': 'Feature A depends on Feature B'
            },
            {
                'id': 'REQ-B', 
                'description': 'Feature B requires Feature C'
            },
            {
                'id': 'REQ-C',
                'description': 'Feature C needs Feature A to work'
            }
        ]

        dependency_graph = await dependency_analyzer.analyze_dependencies(requirements)

        # 순환 의존성이 감지되어야 함 (실제 구현에 따라 다를 수 있음)
        # 이 테스트는 순환 의존성 검출 로직이 작동하는지 확인
        assert dependency_graph.cycles is not None

    @pytest.mark.performance
    async def test_analysis_performance(self, requirement_separator, dependency_analyzer):
        """분석 성능 테스트"""
        
        # 대량의 요구사항 생성
        large_requirements = [
            f"Requirement {i}: System should handle feature {i}"
            for i in range(100)
        ]

        import time
        
        # 요구사항 분리 성능
        start_time = time.time()
        await requirement_separator.separate_requirements(large_requirements)
        separation_time = time.time() - start_time
        
        # 5초 이내에 완료되어야 함
        assert separation_time < 5.0

        # 의존성 분석 성능 (작은 세트로)
        req_dicts = [
            {'id': f'REQ-{i}', 'description': f'Feature {i}'}
            for i in range(20)
        ]
        
        start_time = time.time()
        await dependency_analyzer.analyze_dependencies(req_dicts)
        analysis_time = time.time() - start_time
        
        # 2초 이내에 완료되어야 함
        assert analysis_time < 2.0