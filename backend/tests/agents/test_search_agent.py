"""
Search Agent 테스트
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from backend.src.agents.implementations.search_agent import (
    SearchAgent,
    SearchQuery,
    SearchResult,
    NPMSearcher,
    GitHubSearcher
)

class TestSearchAgent:
    """Search Agent 테스트"""

    @pytest.fixture
    def search_agent(self):
        return SearchAgent()

    @pytest.fixture
    def sample_query(self):
        return SearchQuery(
            keywords=['authentication', 'jwt'],
            language='javascript',
            framework='react',
            min_stars=10,
            license_filter=['MIT', 'Apache-2.0']
        )

    @pytest.fixture
    def sample_requirements(self):
        return [
            {
                'id': 'req-001',
                'description': 'User authentication with JWT tokens',
                'features': ['login', 'logout', 'token_refresh'],
                'language': 'javascript',
                'framework': 'react'
            }
        ]

    @pytest.mark.asyncio
    async def test_search_components(self, search_agent, sample_query):
        """컴포넌트 검색 테스트"""
        
        # Mock search sources
        mock_results = [
            SearchResult(
                id='test-auth',
                name='test-auth',
                description='Authentication library',
                source='npm',
                url='https://npmjs.com/test-auth',
                score=0.8,
                metadata={'stars': 100},
                compatibility_info={}
            )
        ]
        
        with patch.object(search_agent.search_sources['npm'], 'search', 
                         return_value=mock_results):
            with patch.object(search_agent.search_sources['github'], 'search',
                             return_value=[]):
                with patch.object(search_agent.search_sources['pypi'], 'search',
                                 return_value=[]):
                    with patch.object(search_agent.search_sources['maven'], 'search',
                                     return_value=[]):
                        
                        results = await search_agent.search_components(sample_query)
                        
                        assert len(results) > 0
                        assert results[0].name == 'test-auth'
                        assert results[0].source == 'npm'

    @pytest.mark.asyncio
    async def test_search_by_requirements(self, search_agent, sample_requirements):
        """요구사항 기반 검색 테스트"""
        
        with patch.object(search_agent, 'search_components') as mock_search:
            mock_search.return_value = [
                SearchResult(
                    id='auth-lib',
                    name='auth-lib',
                    description='JWT authentication',
                    source='npm',
                    url='https://npmjs.com/auth-lib',
                    score=0.9,
                    metadata={},
                    compatibility_info={}
                )
            ]
            
            results = await search_agent.search_by_requirements(sample_requirements)
            
            assert 'req-001' in results
            assert len(results['req-001']) > 0
            assert results['req-001'][0].name == 'auth-lib'

    @pytest.mark.asyncio
    async def test_generate_search_query(self, search_agent, sample_requirements):
        """검색 쿼리 생성 테스트"""
        
        with patch.object(search_agent.agent, 'arun') as mock_arun:
            mock_arun.return_value = Mock(
                content='{"keywords": ["auth", "jwt"], "language": "javascript", "framework": "react"}'
            )
            
            query = await search_agent._generate_search_query(sample_requirements[0])
            
            assert 'auth' in query.keywords
            assert query.language == 'javascript'
            assert query.framework == 'react'

    def test_extract_basic_keywords(self, search_agent):
        """기본 키워드 추출 테스트"""
        
        requirement = {
            'description': 'User authentication system with database integration',
            'features': ['login', 'logout']
        }
        
        keywords = search_agent._extract_basic_keywords(requirement)
        
        assert 'auth' in keywords or 'authentication' in keywords
        assert 'database' in keywords
        assert 'login' in keywords

    def test_should_search_source(self, search_agent, sample_query):
        """소스별 검색 여부 결정 테스트"""
        
        # JavaScript는 NPM에서 검색해야 함
        assert search_agent._should_search_source('npm', sample_query)
        
        # JavaScript는 PyPI에서 검색하지 않음
        assert not search_agent._should_search_source('pypi', sample_query)
        
        # GitHub은 모든 언어 검색
        assert search_agent._should_search_source('github', sample_query)

    def test_deduplicate_results(self, search_agent):
        """중복 결과 제거 테스트"""
        
        results = [
            SearchResult('1', 'test-lib', 'desc', 'npm', 'url1', 0.8, {}, {}),
            SearchResult('2', 'test_lib', 'desc', 'github', 'url2', 0.7, {}, {}),  # 중복
            SearchResult('3', 'other-lib', 'desc', 'npm', 'url3', 0.9, {}, {})
        ]
        
        unique_results = search_agent._deduplicate_results(results)
        
        assert len(unique_results) == 2
        assert unique_results[0].name == 'test-lib'
        assert unique_results[1].name == 'other-lib'


class TestNPMSearcher:
    """NPM Searcher 테스트"""

    @pytest.fixture
    def npm_searcher(self):
        return NPMSearcher()

    def test_parse_npm_results(self, npm_searcher):
        """NPM 결과 파싱 테스트"""
        
        mock_data = [
            {
                'package': {
                    'name': 'test-package',
                    'description': 'Test package',
                    'version': '1.0.0',
                    'keywords': ['test'],
                    'license': 'MIT'
                },
                'score': {'final': 0.8}
            }
        ]
        
        results = npm_searcher._parse_npm_results(mock_data)
        
        assert len(results) == 1
        assert results[0].name == 'test-package'
        assert results[0].score == 0.8
        assert results[0].metadata['license'] == 'MIT'


class TestGitHubSearcher:
    """GitHub Searcher 테스트"""

    @pytest.fixture
    def github_searcher(self):
        return GitHubSearcher()

    def test_parse_github_results(self, github_searcher):
        """GitHub 결과 파싱 테스트"""
        
        mock_data = [
            {
                'full_name': 'user/repo',
                'name': 'repo',
                'description': 'Test repository',
                'html_url': 'https://github.com/user/repo',
                'stargazers_count': 1000,
                'forks_count': 100,
                'language': 'JavaScript',
                'license': {'name': 'MIT'},
                'updated_at': '2023-01-01T00:00:00Z',
                'topics': ['auth', 'jwt']
            }
        ]
        
        results = github_searcher._parse_github_results(mock_data)
        
        assert len(results) == 1
        assert results[0].name == 'repo'
        assert results[0].metadata['stars'] == 1000
        assert results[0].metadata['language'] == 'JavaScript'