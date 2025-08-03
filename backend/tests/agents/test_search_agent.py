# backend/tests/agents/test_search_agent.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

@pytest.mark.asyncio
class TestSearchAgent:
    """Search Agent 테스트"""

    @pytest.fixture
    async def search_agent(self):
        """Search Agent 인스턴스"""
        from search_agent import SearchAgent
        
        agent = SearchAgent()
        # Mock the AI agent to avoid actual API calls
        agent.search_optimizer.arun = AsyncMock(return_value=Mock(
            content='[{"keywords": ["react", "dashboard"], "category": "ui", "language": "javascript"}]'
        ))
        
        yield agent

    @pytest.fixture
    def sample_requirements(self):
        """샘플 요구사항"""
        return {
            'functional_requirements': [
                'User dashboard with charts',
                'Real-time data updates',
                'User authentication'
            ],
            'technical_requirements': [
                'React framework',
                'TypeScript support',
                'REST API integration'
            ],
            'technology_stack': ['javascript', 'react', 'typescript'],
            'license_filter': ['MIT', 'Apache-2.0'],
            'min_stars': 100
        }

    @pytest.fixture
    def mock_search_results(self):
        """Mock 검색 결과"""
        from search_agent import SearchResult
        
        return [
            SearchResult(
                component_id="npm:react-dashboard",
                name="react-dashboard",
                description="Modern dashboard component for React",
                source="npm",
                url="https://npmjs.com/package/react-dashboard",
                score=0.8,
                metadata={
                    'version': '2.1.0',
                    'keywords': ['react', 'dashboard', 'ui'],
                    'license': 'MIT',
                    'downloads': 50000
                }
            ),
            SearchResult(
                component_id="github:admin-dashboard",
                name="admin-dashboard",
                description="Admin dashboard with authentication",
                source="github",
                url="https://github.com/user/admin-dashboard",
                score=0.9,
                metadata={
                    'stars': 1500,
                    'forks': 200,
                    'language': 'JavaScript',
                    'license': 'MIT',
                    'updated_at': '2024-01-15T00:00:00Z'
                }
            ),
            SearchResult(
                component_id="npm:auth-component",
                name="auth-component",
                description="Authentication component for React apps",
                source="npm",
                url="https://npmjs.com/package/auth-component",
                score=0.7,
                metadata={
                    'version': '1.5.0',
                    'keywords': ['auth', 'react', 'login'],
                    'license': 'Apache-2.0',
                    'downloads': 25000
                }
            )
        ]

    async def test_basic_search(self, search_agent, sample_requirements, mock_search_results):
        """기본 검색 기능 테스트"""
        
        # Mock all search sources
        with patch.object(search_agent, '_search_single_source', return_value=mock_search_results):
            results = await search_agent.search_components(sample_requirements)
            
            # 결과가 반환되어야 함
            assert len(results) > 0
            
            # 각 결과에 필요한 필드가 있어야 함
            for result in results:
                assert result.component_id is not None
                assert result.name is not None
                assert result.description is not None
                assert result.source is not None
                assert result.url is not None
                assert 0 <= result.score <= 1

    async def test_query_generation(self, search_agent, sample_requirements):
        """쿼리 생성 테스트"""
        
        queries = await search_agent._generate_search_queries(sample_requirements)
        
        # 쿼리가 생성되어야 함
        assert len(queries) > 0
        
        # 각 쿼리에 키워드가 있어야 함
        for query in queries:
            assert len(query.keywords) > 0

    async def test_source_selection(self, search_agent, sample_requirements):
        """소스 선택 테스트"""
        
        # JavaScript 프로젝트는 npm과 github 사용
        assert search_agent._should_use_source('npm', sample_requirements)
        assert search_agent._should_use_source('github', sample_requirements)
        
        # Python 프로젝트 테스트
        python_requirements = {
            'technology_stack': ['python', 'django']
        }
        assert search_agent._should_use_source('pypi', python_requirements)
        assert not search_agent._should_use_source('npm', python_requirements)

    async def test_result_deduplication(self, search_agent):
        """결과 중복 제거 테스트"""
        from search_agent import SearchResult
        
        # 중복된 결과 생성
        duplicate_results = [
            SearchResult(
                component_id="test1",
                name="react-component",
                description="Test component",
                source="npm",
                url="https://npmjs.com/package/react-component",
                score=0.8
            ),
            SearchResult(
                component_id="test2",
                name="react-component",  # 같은 이름
                description="Test component",
                source="github",
                url="https://npmjs.com/package/react-component",  # 같은 URL
                score=0.9
            ),
            SearchResult(
                component_id="test3",
                name="different-component",
                description="Different component",
                source="npm",
                url="https://npmjs.com/package/different-component",
                score=0.7
            )
        ]
        
        unique_results = search_agent._deduplicate_results(duplicate_results)
        
        # 중복이 제거되어야 함
        assert len(unique_results) == 2
        
        # 이름과 URL이 다른 결과들만 남아야 함
        names_urls = [(r.name.lower(), r.url) for r in unique_results]
        assert len(set(names_urls)) == len(unique_results)

    @patch('aiohttp.ClientSession.get')
    async def test_npm_search(self, mock_get, search_agent):
        """NPM 검색 테스트"""
        from search_agent import SearchQuery
        
        # Mock NPM API 응답
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'objects': [
                {
                    'package': {
                        'name': 'test-package',
                        'description': 'Test package description',
                        'version': '1.0.0',
                        'keywords': ['test', 'package'],
                        'license': 'MIT'
                    },
                    'score': {
                        'final': 0.8,
                        'detail': {
                            'popularity': 0.7
                        }
                    }
                }
            ]
        })
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # NPM 검색 실행
        npm_searcher = search_agent.search_sources['npm']
        query = SearchQuery(keywords=['test', 'package'])
        
        results = await npm_searcher.search(query)
        
        # 결과 검증
        assert len(results) == 1
        assert results[0].name == 'test-package'
        assert results[0].source == 'npm'
        assert 'version' in results[0].metadata

    @patch('aiohttp.ClientSession.get')
    async def test_github_search(self, mock_get, search_agent):
        """GitHub 검색 테스트"""
        from search_agent import SearchQuery
        
        # Mock GitHub API 응답
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'items': [
                {
                    'name': 'test-repo',
                    'full_name': 'user/test-repo',
                    'description': 'Test repository',
                    'html_url': 'https://github.com/user/test-repo',
                    'stargazers_count': 500,
                    'forks_count': 50,
                    'language': 'JavaScript',
                    'license': {
                        'name': 'MIT License'
                    },
                    'updated_at': '2024-01-15T00:00:00Z'
                }
            ]
        })
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # GitHub 검색 실행
        github_searcher = search_agent.search_sources['github']
        query = SearchQuery(keywords=['test'], language='javascript', min_stars=100)
        
        results = await github_searcher.search(query)
        
        # 결과 검증
        assert len(results) == 1
        assert results[0].name == 'test-repo'
        assert results[0].source == 'github'
        assert results[0].metadata['stars'] == 500

    async def test_result_ranking(self, search_agent, sample_requirements, mock_search_results):
        """결과 랭킹 테스트"""
        
        ranker = search_agent.result_ranker
        ranked_results = await ranker.rank_results(mock_search_results, sample_requirements)
        
        # 결과가 점수 순으로 정렬되어야 함
        for i in range(len(ranked_results) - 1):
            assert ranked_results[i].score >= ranked_results[i + 1].score

    async def test_relevance_calculation(self, search_agent, sample_requirements):
        """관련성 계산 테스트"""
        from search_agent import SearchResult
        
        ranker = search_agent.result_ranker
        
        # 관련성이 높은 결과
        relevant_result = SearchResult(
            component_id="test1",
            name="react-dashboard-auth",
            description="React dashboard with authentication and charts",
            source="npm",
            url="https://test.com",
            score=0.5
        )
        
        # 관련성이 낮은 결과
        irrelevant_result = SearchResult(
            component_id="test2",
            name="python-ml-library",
            description="Machine learning library for Python",
            source="pypi",
            url="https://test2.com",
            score=0.5
        )
        
        relevant_score = await ranker._calculate_relevance(relevant_result, sample_requirements)
        irrelevant_score = await ranker._calculate_relevance(irrelevant_result, sample_requirements)
        
        # 관련성이 높은 결과가 더 높은 점수를 받아야 함
        assert relevant_score > irrelevant_score

    async def test_popularity_calculation(self, search_agent):
        """인기도 계산 테스트"""
        from search_agent import SearchResult
        
        ranker = search_agent.result_ranker
        
        # 인기 있는 GitHub 프로젝트
        popular_result = SearchResult(
            component_id="test1",
            name="popular-repo",
            description="Popular repository",
            source="github",
            url="https://github.com/user/popular-repo",
            score=0.5,
            metadata={'stars': 5000, 'forks': 500}
        )
        
        # 인기 없는 프로젝트
        unpopular_result = SearchResult(
            component_id="test2",
            name="unpopular-repo",
            description="Unpopular repository",
            source="github",
            url="https://github.com/user/unpopular-repo",
            score=0.5,
            metadata={'stars': 10, 'forks': 1}
        )
        
        popular_score = ranker._calculate_popularity(popular_result)
        unpopular_score = ranker._calculate_popularity(unpopular_result)
        
        # 인기 있는 프로젝트가 더 높은 점수를 받아야 함
        assert popular_score > unpopular_score

    async def test_quality_calculation(self, search_agent):
        """품질 계산 테스트"""
        from search_agent import SearchResult
        
        ranker = search_agent.result_ranker
        
        # 고품질 결과
        quality_result = SearchResult(
            component_id="test1",
            name="quality-component",
            description="Well-documented component with comprehensive features",
            source="npm",
            url="https://test.com",
            score=0.5,
            metadata={
                'license': 'MIT',
                'updated_at': '2024-01-15T00:00:00Z',
                'is_official': True
            }
        )
        
        # 저품질 결과
        poor_result = SearchResult(
            component_id="test2",
            name="poor-component",
            description="Basic component",
            source="npm",
            url="https://test2.com",
            score=0.5,
            metadata={}
        )
        
        quality_score = ranker._calculate_quality(quality_result)
        poor_score = ranker._calculate_quality(poor_result)
        
        # 고품질 결과가 더 높은 점수를 받아야 함
        assert quality_score > poor_score

    async def test_query_expansion(self, search_agent):
        """쿼리 확장 테스트"""
        from search_agent import SearchQuery
        
        expander = search_agent.query_expander
        
        # 기본 쿼리
        base_query = SearchQuery(keywords=['auth', 'ui'])
        
        # 쿼리 확장
        expanded_queries = expander.expand_query(base_query)
        
        # 확장된 쿼리가 생성되어야 함
        assert len(expanded_queries) > 1
        
        # 동의어가 추가되어야 함
        all_keywords = []
        for query in expanded_queries:
            all_keywords.extend(query.keywords)
        
        # 'auth'의 동의어들이 포함되어야 함
        auth_synonyms = ['authentication', 'login', 'oauth', 'jwt']
        assert any(synonym in all_keywords for synonym in auth_synonyms)

    @pytest.mark.performance
    async def test_search_performance(self, search_agent, sample_requirements):
        """검색 성능 테스트"""
        import time
        
        # Mock search sources to return quickly
        async def mock_search(query):
            await asyncio.sleep(0.01)  # Simulate network delay
            return []
        
        for searcher in search_agent.search_sources.values():
            searcher.search = mock_search
        
        start_time = time.time()
        results = await search_agent.search_components(sample_requirements)
        elapsed_time = time.time() - start_time
        
        # 검색이 5초 이내에 완료되어야 함
        assert elapsed_time < 5.0

    @pytest.mark.integration
    async def test_end_to_end_search(self, search_agent, sample_requirements):
        """전체 검색 플로우 테스트"""
        
        # Mock all external dependencies
        with patch.object(search_agent, '_search_single_source') as mock_search:
            mock_search.return_value = [
                Mock(
                    component_id="test1",
                    name="test-component",
                    description="Test component",
                    source="npm",
                    url="https://test.com",
                    score=0.8,
                    metadata={'license': 'MIT'}
                )
            ]
            
            # 전체 검색 실행
            results = await search_agent.search_components(
                sample_requirements,
                {'max_results': 10}
            )
            
            # 결과 검증
            assert len(results) > 0
            assert all(hasattr(r, 'component_id') for r in results)
            assert all(hasattr(r, 'score') for r in results)
            
            # 최대 결과 수 제한 확인
            assert len(results) <= 10