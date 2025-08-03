# backend/tests/agents/test_agents_integration.py
import pytest
import asyncio
from typing import Dict, Any, List

@pytest.mark.integration
class TestAgentsIntegration:
    """Task 4.31-4.50 에이전트 통합 테스트"""

    @pytest.fixture
    async def component_decision_agent(self):
        from agents.implementations.component_decision_agent import ComponentDecisionAgent
        agent = ComponentDecisionAgent()
        yield agent

    @pytest.fixture
    async def match_rate_agent(self):
        from agents.implementations.match_rate_agent import MatchRateAgent
        agent = MatchRateAgent()
        yield agent

    @pytest.fixture
    async def search_agent(self):
        from agents.implementations.search_agent import SearchAgent
        agent = SearchAgent()
        yield agent

    @pytest.fixture
    async def generation_agent(self):
        from agents.implementations.generation_agent import GenerationAgent
        agent = GenerationAgent()
        yield agent

    @pytest.fixture
    def sample_requirements(self):
        return {
            'id': 'req_001',
            'description': 'Build a REST API for user management',
            'features': ['user_registration', 'authentication', 'profile_management'],
            'technologies': ['python', 'fastapi', 'postgresql'],
            'performance': {'response_time': '< 200ms', 'concurrent_users': 1000}
        }

    @pytest.fixture
    def sample_components(self):
        return [
            {
                'id': 'comp_001',
                'name': 'FastAPI User Service',
                'description': 'Complete user management service with FastAPI',
                'features': ['user_registration', 'authentication', 'profile_management', 'admin_panel'],
                'technologies': ['python', 'fastapi', 'sqlalchemy'],
                'source': 'github',
                'quality_score': 0.85
            },
            {
                'id': 'comp_002', 
                'name': 'Django User Auth',
                'description': 'Django-based user authentication system',
                'features': ['authentication', 'user_management'],
                'technologies': ['python', 'django'],
                'source': 'pypi',
                'quality_score': 0.75
            }
        ]

    @pytest.mark.asyncio
    async def test_component_decision_workflow(
        self,
        component_decision_agent,
        sample_requirements,
        sample_components
    ):
        """컴포넌트 결정 워크플로우 테스트"""
        
        decisions = await component_decision_agent.make_component_decisions(
            sample_requirements,
            sample_components
        )
        
        assert len(decisions) == len(sample_components)
        assert all(d.confidence >= 0.0 and d.confidence <= 1.0 for d in decisions)
        assert all(d.decision in ['selected', 'rejected', 'conditional'] for d in decisions)

    @pytest.mark.asyncio
    async def test_match_rate_calculation(
        self,
        match_rate_agent,
        sample_requirements,
        sample_components
    ):
        """매칭률 계산 테스트"""
        
        match_matrix = await match_rate_agent.calculate_match_rates(
            [sample_requirements],
            sample_components
        )
        
        assert len(match_matrix) == 1  # 하나의 요구사항
        assert len(match_matrix[0]) == len(sample_components)
        
        # 점수 검증
        for match in match_matrix[0]:
            assert 0.0 <= match.score <= 1.0
            assert 0.0 <= match.confidence <= 1.0
            assert match.match_details is not None

    @pytest.mark.asyncio
    async def test_component_search(
        self,
        search_agent,
        sample_requirements
    ):
        """컴포넌트 검색 테스트"""
        
        search_results = await search_agent.search_components(
            sample_requirements,
            {'max_results': 10}
        )
        
        assert isinstance(search_results, list)
        assert len(search_results) <= 10
        
        for result in search_results:
            assert result.name is not None
            assert result.source is not None
            assert 0.0 <= result.score <= 1.0

    @pytest.mark.asyncio
    async def test_code_generation(
        self,
        generation_agent
    ):
        """코드 생성 테스트"""
        
        specification = {
            'name': 'UserService',
            'description': 'User management service',
            'language': 'python',
            'framework': 'fastapi',
            'features': ['create_user', 'get_user', 'update_user'],
            'requirements': ['RESTful API', 'Input validation', 'Error handling']
        }
        
        component = await generation_agent.generate_component(
            specification,
            {'generate_tests': True, 'generate_docs': True}
        )
        
        assert component.name == 'UserService'
        assert component.language == 'python'
        assert component.framework == 'fastapi'
        assert len(component.code) > 100  # 실제 코드가 생성되었는지
        assert component.tests is not None
        assert component.documentation is not None
        assert isinstance(component.dependencies, list)

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(
        self,
        search_agent,
        match_rate_agent,
        component_decision_agent,
        generation_agent,
        sample_requirements
    ):
        """전체 워크플로우 통합 테스트"""
        
        # 1. 컴포넌트 검색
        search_results = await search_agent.search_components(
            sample_requirements,
            {'max_results': 5}
        )
        
        # 2. 매칭률 계산
        components = [
            {
                'id': result.component_id,
                'name': result.name,
                'description': result.description,
                'features': sample_requirements['features'],  # 실제로는 결과에서 추출
                'technologies': sample_requirements['technologies']
            }
            for result in search_results[:3]  # 상위 3개만
        ]
        
        if components:
            match_matrix = await match_rate_agent.calculate_match_rates(
                [sample_requirements],
                components
            )
            
            # 3. 컴포넌트 결정
            decisions = await component_decision_agent.make_component_decisions(
                sample_requirements,
                components
            )
            
            # 4. 필요시 코드 생성
            selected_components = [d for d in decisions if d.decision == 'selected']
            
            if not selected_components:
                # 적합한 컴포넌트가 없으면 새로 생성
                specification = {
                    'name': 'CustomUserService',
                    'description': sample_requirements['description'],
                    'language': 'python',
                    'framework': 'fastapi',
                    'features': sample_requirements['features'],
                    'requirements': ['RESTful API', 'Database integration']
                }
                
                generated_component = await generation_agent.generate_component(
                    specification
                )
                
                assert generated_component is not None
                assert len(generated_component.code) > 0
        
        # 워크플로우가 오류 없이 완료되면 성공
        assert True

    @pytest.mark.performance
    async def test_agents_performance(
        self,
        match_rate_agent,
        sample_requirements,
        sample_components
    ):
        """에이전트 성능 테스트"""
        
        import time
        
        # 매칭률 계산 성능 테스트
        start_time = time.time()
        
        # 10개 요구사항 x 10개 컴포넌트 매칭
        requirements_list = [sample_requirements] * 10
        components_list = sample_components * 5  # 10개 컴포넌트
        
        tasks = []
        for req in requirements_list:
            task = match_rate_agent.calculate_match_rates([req], components_list)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        
        # 성능 기준: 100개 매칭을 5초 이내에 완료
        assert elapsed_time < 5.0
        assert len(results) == 10
        
        print(f"Performance test completed in {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])