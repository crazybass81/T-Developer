# backend/src/agents/implementations/search_agent.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import aiohttp
from agno.agent import Agent
from agno.models.aws import AwsBedrock

@dataclass
class SearchResult:
    component_id: str
    name: str
    description: str
    source: str  # npm, pypi, github, etc.
    score: float
    metadata: Dict[str, Any]

class SearchAgent:
    """컴포넌트 검색 및 발견 에이전트"""

    def __init__(self):
        self.search_agent = Agent(
            name="Component-Search-Engine",
            model=AwsBedrock(id="amazon.nova-lite-v1:0"),
            role="Expert component discovery specialist",
            instructions=[
                "Search and discover relevant components from multiple sources",
                "Evaluate component quality and relevance",
                "Provide comprehensive search results with metadata"
            ],
            temperature=0.1
        )
        
        self.search_engines = {
            'npm': NPMSearchEngine(),
            'pypi': PyPISearchEngine(),
            'github': GitHubSearchEngine(),
            'maven': MavenSearchEngine()
        }
        
        self.quality_evaluator = ComponentQualityEvaluator()

    async def search_components(
        self,
        requirements: Dict[str, Any],
        search_options: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """컴포넌트 검색"""
        
        # 검색 쿼리 생성
        search_queries = await self._generate_search_queries(requirements)
        
        # 병렬 검색 실행
        search_tasks = []
        for source, engine in self.search_engines.items():
            if self._should_search_source(source, requirements):
                task = self._search_in_source(engine, search_queries, requirements)
                search_tasks.append(task)
        
        # 모든 검색 결과 수집
        all_results = []
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        for results in search_results:
            if isinstance(results, list):
                all_results.extend(results)
        
        # 품질 평가 및 필터링
        evaluated_results = await self._evaluate_and_filter(all_results, requirements)
        
        # 중복 제거 및 순위 매기기
        final_results = self._deduplicate_and_rank(evaluated_results)
        
        return final_results[:20]  # 상위 20개 결과

    async def _generate_search_queries(
        self,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """검색 쿼리 생성"""
        
        queries = []
        
        # 기본 키워드 기반 쿼리
        if 'keywords' in requirements:
            queries.extend(requirements['keywords'])
        
        # 기능 기반 쿼리
        if 'features' in requirements:
            for feature in requirements['features']:
                queries.append(feature)
        
        # 기술 스택 기반 쿼리
        if 'technologies' in requirements:
            for tech in requirements['technologies']:
                queries.append(tech)
        
        # AI 기반 쿼리 확장
        expanded_queries = await self._expand_queries_with_ai(queries, requirements)
        queries.extend(expanded_queries)
        
        return list(set(queries))  # 중복 제거

    async def _search_in_source(
        self,
        engine: 'SearchEngine',
        queries: List[str],
        requirements: Dict[str, Any]
    ) -> List[SearchResult]:
        """특정 소스에서 검색"""
        
        results = []
        
        for query in queries:
            try:
                source_results = await engine.search(query, requirements)
                results.extend(source_results)
            except Exception as e:
                print(f"Search error in {engine.name}: {e}")
        
        return results

    async def _evaluate_and_filter(
        self,
        results: List[SearchResult],
        requirements: Dict[str, Any]
    ) -> List[SearchResult]:
        """품질 평가 및 필터링"""
        
        evaluated_results = []
        
        for result in results:
            # 품질 점수 계산
            quality_score = await self.quality_evaluator.evaluate(result)
            
            # 관련성 점수 계산
            relevance_score = await self._calculate_relevance(result, requirements)
            
            # 종합 점수
            result.score = (quality_score * 0.6 + relevance_score * 0.4)
            
            # 최소 임계값 필터링
            if result.score >= 0.3:
                evaluated_results.append(result)
        
        return evaluated_results

    def _deduplicate_and_rank(self, results: List[SearchResult]) -> List[SearchResult]:
        """중복 제거 및 순위 매기기"""
        
        # 이름 기반 중복 제거
        seen_names = set()
        unique_results = []
        
        for result in sorted(results, key=lambda x: x.score, reverse=True):
            if result.name not in seen_names:
                unique_results.append(result)
                seen_names.add(result.name)
        
        return unique_results

    def _should_search_source(self, source: str, requirements: Dict[str, Any]) -> bool:
        """소스 검색 여부 결정"""
        
        tech_stack = requirements.get('technologies', [])
        
        # 기술 스택에 따른 소스 선택
        if source == 'npm' and any(tech in ['javascript', 'typescript', 'node.js'] for tech in tech_stack):
            return True
        elif source == 'pypi' and 'python' in tech_stack:
            return True
        elif source == 'maven' and 'java' in tech_stack:
            return True
        elif source == 'github':
            return True  # GitHub는 항상 검색
        
        return False

class SearchEngine:
    """검색 엔진 베이스 클래스"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def search(self, query: str, requirements: Dict[str, Any]) -> List[SearchResult]:
        raise NotImplementedError

class NPMSearchEngine(SearchEngine):
    """NPM 패키지 검색"""
    
    def __init__(self):
        super().__init__('npm')
    
    async def search(self, query: str, requirements: Dict[str, Any]) -> List[SearchResult]:
        """NPM 검색 실행"""
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            url = f"https://registry.npmjs.org/-/v1/search?text={query}&size=10"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for package in data.get('objects', []):
                            pkg_info = package.get('package', {})
                            
                            result = SearchResult(
                                component_id=f"npm:{pkg_info.get('name', '')}",
                                name=pkg_info.get('name', ''),
                                description=pkg_info.get('description', ''),
                                source='npm',
                                score=0.0,  # 나중에 계산
                                metadata={
                                    'version': pkg_info.get('version', ''),
                                    'keywords': pkg_info.get('keywords', []),
                                    'author': pkg_info.get('author', {}),
                                    'repository': pkg_info.get('repository', {}),
                                    'downloads': package.get('searchScore', 0)
                                }
                            )
                            
                            results.append(result)
            
            except Exception as e:
                print(f"NPM search error: {e}")
        
        return results

class ComponentQualityEvaluator:
    """컴포넌트 품질 평가기"""
    
    async def evaluate(self, component: SearchResult) -> float:
        """품질 점수 계산"""
        
        score = 0.0
        
        # 메타데이터 기반 평가
        metadata = component.metadata
        
        # 다운로드 수 (NPM의 경우)
        if 'downloads' in metadata:
            downloads = metadata['downloads']
            if downloads > 1000000:
                score += 0.3
            elif downloads > 100000:
                score += 0.2
            elif downloads > 10000:
                score += 0.1
        
        # 문서화 품질
        if component.description and len(component.description) > 50:
            score += 0.2
        
        # 키워드 존재
        if metadata.get('keywords'):
            score += 0.1
        
        # 저장소 존재
        if metadata.get('repository'):
            score += 0.2
        
        # 최신성 (버전 정보)
        if metadata.get('version'):
            score += 0.2
        
        return min(score, 1.0)

class PyPISearchEngine(SearchEngine):
    """PyPI 패키지 검색"""
    
    def __init__(self):
        super().__init__('pypi')
    
    async def search(self, query: str, requirements: Dict[str, Any]) -> List[SearchResult]:
        # PyPI 검색 구현 (간단한 버전)
        return []

class GitHubSearchEngine(SearchEngine):
    """GitHub 저장소 검색"""
    
    def __init__(self):
        super().__init__('github')
    
    async def search(self, query: str, requirements: Dict[str, Any]) -> List[SearchResult]:
        # GitHub API 검색 구현 (간단한 버전)
        return []

class MavenSearchEngine(SearchEngine):
    """Maven 중앙 저장소 검색"""
    
    def __init__(self):
        super().__init__('maven')
    
    async def search(self, query: str, requirements: Dict[str, Any]) -> List[SearchResult]:
        # Maven 검색 구현 (간단한 버전)
        return []