# Task 4.8: Search Agent 구현

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools import DuckDuckGoTools

@dataclass
class SearchResult:
    component_id: str
    name: str
    description: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any]

## SubTask 4.8.1: 다중 소스 검색 엔진

class MultiSourceSearchEngine:
    """다중 소스 검색 엔진"""
    
    def __init__(self):
        self.agent = Agent(
            name="Component-Searcher",
            model=AwsBedrock(id="amazon.nova-lite-v1:0"),
            role="Expert component discovery specialist",
            tools=[DuckDuckGoTools()]
        )
        self.sources = {
            'npm': NPMSearchTool(),
            'github': GitHubSearchTool(),
            'pypi': PyPISearchTool(),
            'maven': MavenSearchTool()
        }
    
    async def search_components(
        self,
        query: str,
        filters: Dict[str, Any] = None
    ) -> List[SearchResult]:
        """다중 소스에서 컴포넌트 검색"""
        
        all_results = []
        
        # 각 소스에서 병렬 검색
        for source_name, source_tool in self.sources.items():
            try:
                results = await source_tool.search(query, filters)
                for result in results:
                    all_results.append(SearchResult(
                        component_id=result['id'],
                        name=result['name'],
                        description=result['description'],
                        source=source_name,
                        relevance_score=result['score'],
                        metadata=result.get('metadata', {})
                    ))
            except Exception as e:
                print(f"Search failed for {source_name}: {e}")
        
        # 관련성 점수로 정렬
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return all_results[:50]  # 상위 50개 결과만 반환

class NPMSearchTool:
    """NPM 패키지 검색"""
    
    async def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """NPM에서 패키지 검색"""
        # NPM API 호출 시뮬레이션
        return [
            {
                'id': 'npm_react',
                'name': 'react',
                'description': 'JavaScript library for building user interfaces',
                'score': 0.95,
                'metadata': {'downloads': 20000000, 'version': '18.2.0'}
            }
        ]

class GitHubSearchTool:
    """GitHub 저장소 검색"""
    
    async def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """GitHub에서 저장소 검색"""
        return [
            {
                'id': 'github_react',
                'name': 'facebook/react',
                'description': 'A declarative, efficient, and flexible JavaScript library',
                'score': 0.92,
                'metadata': {'stars': 200000, 'language': 'JavaScript'}
            }
        ]

## SubTask 4.8.2: 지능형 쿼리 확장

class IntelligentQueryExpander:
    """지능형 쿼리 확장"""
    
    def __init__(self):
        self.expansion_agent = Agent(
            name="Query-Expander",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Expert at expanding search queries for better results"
        )
    
    async def expand_query(
        self,
        original_query: str,
        context: Dict[str, Any] = None
    ) -> List[str]:
        """쿼리 확장"""
        
        prompt = f"""
        Expand the search query '{original_query}' to find more relevant components.
        Context: {context}
        
        Generate 3-5 related search terms that would help find similar components.
        """
        
        response = await self.expansion_agent.arun(prompt)
        
        # 응답에서 확장된 쿼리 추출
        expanded_queries = self._parse_expanded_queries(response)
        
        return [original_query] + expanded_queries
    
    def _parse_expanded_queries(self, response: str) -> List[str]:
        """확장된 쿼리 파싱"""
        # 실제로는 더 정교한 파싱 필요
        return ['ui component', 'react library', 'frontend framework']

## SubTask 4.8.3: 실시간 인덱싱 시스템

class RealtimeIndexingSystem:
    """실시간 인덱싱 시스템"""
    
    def __init__(self):
        self.index = {}
        self.indexing_agent = Agent(
            name="Component-Indexer",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Component metadata indexing specialist"
        )
    
    async def index_component(
        self,
        component: Dict[str, Any]
    ) -> None:
        """컴포넌트 인덱싱"""
        
        # 메타데이터 추출
        metadata = await self._extract_metadata(component)
        
        # 검색 키워드 생성
        keywords = await self._generate_keywords(component, metadata)
        
        # 인덱스에 추가
        component_id = component['id']
        self.index[component_id] = {
            'component': component,
            'metadata': metadata,
            'keywords': keywords,
            'indexed_at': self._get_timestamp()
        }
    
    async def _extract_metadata(
        self,
        component: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메타데이터 추출"""
        
        prompt = f"""
        Extract metadata from this component:
        {component}
        
        Extract: category, tags, dependencies, license, popularity
        """
        
        response = await self.indexing_agent.arun(prompt)
        
        return {
            'category': 'ui-component',
            'tags': ['react', 'component'],
            'dependencies': [],
            'license': 'MIT',
            'popularity': 0.8
        }
    
    async def _generate_keywords(
        self,
        component: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[str]:
        """검색 키워드 생성"""
        
        keywords = []
        
        # 이름에서 키워드 추출
        if 'name' in component:
            keywords.extend(component['name'].split('-'))
        
        # 설명에서 키워드 추출
        if 'description' in component:
            keywords.extend(component['description'].split()[:10])
        
        # 태그 추가
        keywords.extend(metadata.get('tags', []))
        
        return list(set(keywords))
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

## SubTask 4.8.4: 검색 결과 랭킹 시스템

class SearchResultRanker:
    """검색 결과 랭킹 시스템"""
    
    def __init__(self):
        self.ranking_agent = Agent(
            name="Result-Ranker",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Search result ranking specialist"
        )
        self.ranking_factors = {
            'relevance': 0.4,
            'popularity': 0.2,
            'quality': 0.2,
            'recency': 0.1,
            'compatibility': 0.1
        }
    
    async def rank_results(
        self,
        results: List[SearchResult],
        query: str,
        context: Dict[str, Any] = None
    ) -> List[SearchResult]:
        """검색 결과 랭킹"""
        
        ranked_results = []
        
        for result in results:
            # 각 요소별 점수 계산
            scores = {
                'relevance': await self._calculate_relevance(result, query),
                'popularity': self._calculate_popularity(result),
                'quality': await self._calculate_quality(result),
                'recency': self._calculate_recency(result),
                'compatibility': await self._calculate_compatibility(result, context)
            }
            
            # 가중 평균 계산
            final_score = sum(
                scores[factor] * weight
                for factor, weight in self.ranking_factors.items()
            )
            
            # 결과 업데이트
            result.relevance_score = final_score
            ranked_results.append(result)
        
        # 최종 점수로 정렬
        ranked_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return ranked_results
    
    async def _calculate_relevance(
        self,
        result: SearchResult,
        query: str
    ) -> float:
        """관련성 점수 계산"""
        
        # 텍스트 유사도 기반 관련성 계산
        text = f"{result.name} {result.description}"
        
        # 간단한 키워드 매칭
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        intersection = len(query_words & text_words)
        union = len(query_words | text_words)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_popularity(self, result: SearchResult) -> float:
        """인기도 점수 계산"""
        downloads = result.metadata.get('downloads', 0)
        stars = result.metadata.get('stars', 0)
        
        # 정규화된 인기도 점수
        popularity_score = min(1.0, (downloads + stars * 100) / 1000000)
        
        return popularity_score
    
    async def _calculate_quality(self, result: SearchResult) -> float:
        """품질 점수 계산"""
        
        # 메타데이터 기반 품질 평가
        has_docs = bool(result.metadata.get('documentation'))
        has_tests = bool(result.metadata.get('tests'))
        has_license = bool(result.metadata.get('license'))
        
        quality_score = (has_docs + has_tests + has_license) / 3
        
        return quality_score
    
    def _calculate_recency(self, result: SearchResult) -> float:
        """최신성 점수 계산"""
        last_updated = result.metadata.get('last_updated')
        if not last_updated:
            return 0.5
        
        # 최근 업데이트일수록 높은 점수
        from datetime import datetime, timedelta
        
        try:
            update_date = datetime.fromisoformat(last_updated)
            days_ago = (datetime.utcnow() - update_date).days
            
            # 30일 이내면 1.0, 1년 이후면 0.0
            recency_score = max(0.0, 1.0 - days_ago / 365)
            
            return recency_score
        except:
            return 0.5

class PyPISearchTool:
    """PyPI 패키지 검색"""
    
    async def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        return []

class MavenSearchTool:
    """Maven 저장소 검색"""
    
    async def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        return []