"""
Search Agent - 컴포넌트 검색 및 발견 에이전트
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import aiohttp
from agno.agent import Agent
from agno.models.aws import AwsBedrock
import json
import re

@dataclass
class SearchResult:
    id: str
    name: str
    description: str
    source: str
    url: str
    score: float
    metadata: Dict[str, Any]
    compatibility_info: Dict[str, Any]

@dataclass
class SearchQuery:
    keywords: List[str]
    language: Optional[str]
    framework: Optional[str]
    category: Optional[str]
    min_stars: int = 0
    license_filter: List[str] = None

class SearchAgent:
    """다중 소스에서 컴포넌트를 검색하고 발견하는 에이전트"""
    
    def __init__(self):
        self.agent = Agent(
            name="Component-Search-Agent",
            model=AwsBedrock(
                id="amazon.nova-lite-v1:0",
                region="us-east-1"
            ),
            role="Expert in finding and evaluating software components",
            instructions=[
                "Search for components across multiple sources",
                "Evaluate component quality and relevance",
                "Rank results by matching score and quality",
                "Filter results based on requirements"
            ],
            temperature=0.3,
            max_retries=3
        )
        
        self.search_sources = {
            'npm': NPMSearcher(),
            'pypi': PyPISearcher(),
            'github': GitHubSearcher(),
            'maven': MavenSearcher()
        }
        
        self.result_ranker = ResultRanker()
        self.quality_evaluator = QualityEvaluator()
        
    async def search_components(
        self,
        query: SearchQuery,
        max_results: int = 50
    ) -> List[SearchResult]:
        """컴포넌트 검색 실행"""
        
        # 1. 병렬 검색 실행
        search_tasks = []
        for source_name, searcher in self.search_sources.items():
            if self._should_search_source(source_name, query):
                task = searcher.search(query, max_results // len(self.search_sources))
                search_tasks.append((source_name, task))
        
        # 2. 검색 결과 수집
        all_results = []
        for source_name, task in search_tasks:
            try:
                results = await task
                for result in results:
                    result.source = source_name
                all_results.extend(results)
            except Exception as e:
                print(f"Search failed for {source_name}: {e}")
        
        # 3. 중복 제거
        unique_results = self._deduplicate_results(all_results)
        
        # 4. 품질 평가
        evaluated_results = await self._evaluate_quality(unique_results)
        
        # 5. 결과 랭킹
        ranked_results = await self.result_ranker.rank_results(
            evaluated_results,
            query
        )
        
        return ranked_results[:max_results]
    
    async def search_by_requirements(
        self,
        requirements: List[Dict[str, Any]],
        matching_results: List[Any] = None
    ) -> Dict[str, List[SearchResult]]:
        """요구사항 기반 검색"""
        
        search_results = {}
        
        for req in requirements:
            # 요구사항에서 검색 쿼리 생성
            query = await self._generate_search_query(req)
            
            # 매칭 결과가 있으면 우선순위 조정
            if matching_results:
                query = self._adjust_query_with_matching(query, req, matching_results)
            
            # 검색 실행
            results = await self.search_components(query)
            search_results[req.get('id', f'req_{len(search_results)}')] = results
        
        return search_results
    
    async def _generate_search_query(self, requirement: Dict[str, Any]) -> SearchQuery:
        """요구사항에서 검색 쿼리 생성"""
        
        # AI 에이전트를 통한 키워드 추출
        prompt = f"""
        Extract search keywords from this requirement:
        
        Requirement: {json.dumps(requirement, indent=2)}
        
        Return JSON with:
        - keywords: list of search terms
        - language: programming language if specified
        - framework: framework if specified
        - category: component category
        """
        
        try:
            response = await self.agent.arun(prompt)
            query_data = json.loads(response.content)
            
            return SearchQuery(
                keywords=query_data.get('keywords', []),
                language=query_data.get('language'),
                framework=query_data.get('framework'),
                category=query_data.get('category'),
                min_stars=10,
                license_filter=['MIT', 'Apache-2.0', 'BSD']
            )
        except Exception:
            # 폴백: 기본 키워드 추출
            keywords = self._extract_basic_keywords(requirement)
            return SearchQuery(
                keywords=keywords,
                language=requirement.get('language'),
                framework=requirement.get('framework'),
                min_stars=10
            )
    
    def _extract_basic_keywords(self, requirement: Dict[str, Any]) -> List[str]:
        """기본 키워드 추출"""
        keywords = []
        
        # 설명에서 키워드 추출
        description = requirement.get('description', '')
        words = re.findall(r'\b\w+\b', description.lower())
        
        # 기술 관련 키워드 필터링
        tech_keywords = [
            'auth', 'database', 'api', 'ui', 'component',
            'library', 'framework', 'service', 'client'
        ]
        
        keywords.extend([w for w in words if w in tech_keywords])
        
        # 기능에서 키워드 추출
        if 'features' in requirement:
            keywords.extend(requirement['features'])
        
        return list(set(keywords))[:10]
    
    def _should_search_source(self, source: str, query: SearchQuery) -> bool:
        """소스별 검색 여부 결정"""
        
        language_mapping = {
            'npm': ['javascript', 'typescript', 'node'],
            'pypi': ['python'],
            'maven': ['java', 'kotlin', 'scala'],
            'github': ['all']
        }
        
        if not query.language:
            return True
        
        return (query.language.lower() in language_mapping.get(source, []) or 
                source == 'github')
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """중복 결과 제거"""
        seen_names = set()
        unique_results = []
        
        for result in results:
            # 이름 정규화
            normalized_name = result.name.lower().replace('-', '').replace('_', '')
            
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_results.append(result)
        
        return unique_results
    
    async def _evaluate_quality(self, results: List[SearchResult]) -> List[SearchResult]:
        """품질 평가"""
        
        for result in results:
            quality_score = await self.quality_evaluator.evaluate(result)
            result.metadata['quality_score'] = quality_score
            
            # 전체 점수에 품질 점수 반영
            result.score = (result.score * 0.7) + (quality_score * 0.3)
        
        return results


class NPMSearcher:
    """NPM 패키지 검색"""
    
    async def search(self, query: SearchQuery, limit: int) -> List[SearchResult]:
        """NPM 검색 실행"""
        
        search_url = "https://registry.npmjs.org/-/v1/search"
        params = {
            'text': ' '.join(query.keywords),
            'size': limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_npm_results(data.get('objects', []))
        
        return []
    
    def _parse_npm_results(self, objects: List[Dict]) -> List[SearchResult]:
        """NPM 결과 파싱"""
        results = []
        
        for obj in objects:
            package = obj.get('package', {})
            
            result = SearchResult(
                id=package.get('name', ''),
                name=package.get('name', ''),
                description=package.get('description', ''),
                source='npm',
                url=f"https://www.npmjs.com/package/{package.get('name', '')}",
                score=obj.get('score', {}).get('final', 0),
                metadata={
                    'version': package.get('version', ''),
                    'keywords': package.get('keywords', []),
                    'author': package.get('author', {}),
                    'license': package.get('license', ''),
                    'downloads': obj.get('score', {}).get('detail', {}).get('popularity', 0)
                },
                compatibility_info={}
            )
            results.append(result)
        
        return results


class PyPISearcher:
    """PyPI 패키지 검색"""
    
    async def search(self, query: SearchQuery, limit: int) -> List[SearchResult]:
        """PyPI 검색 실행"""
        
        search_url = "https://pypi.org/simple/"
        # PyPI는 간단한 검색만 지원하므로 GitHub API 활용
        
        github_searcher = GitHubSearcher()
        github_results = await github_searcher.search_by_language(
            query, 'python', limit
        )
        
        # PyPI에서 실제 패키지 확인
        verified_results = []
        for result in github_results:
            if await self._verify_pypi_package(result.name):
                result.source = 'pypi'
                verified_results.append(result)
        
        return verified_results
    
    async def _verify_pypi_package(self, package_name: str) -> bool:
        """PyPI 패키지 존재 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://pypi.org/pypi/{package_name}/json"
                async with session.get(url) as response:
                    return response.status == 200
        except:
            return False


class GitHubSearcher:
    """GitHub 저장소 검색"""
    
    async def search(self, query: SearchQuery, limit: int) -> List[SearchResult]:
        """GitHub 검색 실행"""
        
        if query.language:
            return await self.search_by_language(query, query.language, limit)
        else:
            return await self.search_general(query, limit)
    
    async def search_by_language(
        self, 
        query: SearchQuery, 
        language: str, 
        limit: int
    ) -> List[SearchResult]:
        """언어별 GitHub 검색"""
        
        search_terms = ' '.join(query.keywords)
        search_query = f"{search_terms} language:{language}"
        
        if query.min_stars > 0:
            search_query += f" stars:>={query.min_stars}"
        
        return await self._github_api_search(search_query, limit)
    
    async def search_general(self, query: SearchQuery, limit: int) -> List[SearchResult]:
        """일반 GitHub 검색"""
        
        search_terms = ' '.join(query.keywords)
        search_query = search_terms
        
        if query.min_stars > 0:
            search_query += f" stars:>={query.min_stars}"
        
        return await self._github_api_search(search_query, limit)
    
    async def _github_api_search(self, query: str, limit: int) -> List[SearchResult]:
        """GitHub API 검색"""
        
        url = "https://api.github.com/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': min(limit, 100)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_github_results(data.get('items', []))
        
        return []
    
    def _parse_github_results(self, items: List[Dict]) -> List[SearchResult]:
        """GitHub 결과 파싱"""
        results = []
        
        for item in items:
            result = SearchResult(
                id=item.get('full_name', ''),
                name=item.get('name', ''),
                description=item.get('description', ''),
                source='github',
                url=item.get('html_url', ''),
                score=item.get('stargazers_count', 0) / 1000,  # 정규화
                metadata={
                    'stars': item.get('stargazers_count', 0),
                    'forks': item.get('forks_count', 0),
                    'language': item.get('language', ''),
                    'license': item.get('license', {}).get('name', '') if item.get('license') else '',
                    'updated_at': item.get('updated_at', ''),
                    'topics': item.get('topics', [])
                },
                compatibility_info={}
            )
            results.append(result)
        
        return results


class MavenSearcher:
    """Maven Central 검색"""
    
    async def search(self, query: SearchQuery, limit: int) -> List[SearchResult]:
        """Maven 검색 실행"""
        
        search_url = "https://search.maven.org/solrsearch/select"
        params = {
            'q': ' '.join(query.keywords),
            'rows': limit,
            'wt': 'json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_maven_results(
                        data.get('response', {}).get('docs', [])
                    )
        
        return []
    
    def _parse_maven_results(self, docs: List[Dict]) -> List[SearchResult]:
        """Maven 결과 파싱"""
        results = []
        
        for doc in docs:
            result = SearchResult(
                id=f"{doc.get('g', '')}:{doc.get('a', '')}",
                name=doc.get('a', ''),
                description='',  # Maven에서 설명 제공 안함
                source='maven',
                url=f"https://mvnrepository.com/artifact/{doc.get('g', '')}/{doc.get('a', '')}",
                score=1.0,  # 기본 점수
                metadata={
                    'group_id': doc.get('g', ''),
                    'artifact_id': doc.get('a', ''),
                    'latest_version': doc.get('latestVersion', ''),
                    'version_count': doc.get('versionCount', 0)
                },
                compatibility_info={}
            )
            results.append(result)
        
        return results


class ResultRanker:
    """검색 결과 랭킹"""
    
    async def rank_results(
        self, 
        results: List[SearchResult], 
        query: SearchQuery
    ) -> List[SearchResult]:
        """결과 랭킹"""
        
        for result in results:
            # 키워드 매칭 점수
            keyword_score = self._calculate_keyword_match(result, query.keywords)
            
            # 인기도 점수
            popularity_score = self._calculate_popularity_score(result)
            
            # 최신성 점수
            freshness_score = self._calculate_freshness_score(result)
            
            # 최종 점수 계산
            final_score = (
                result.score * 0.4 +
                keyword_score * 0.3 +
                popularity_score * 0.2 +
                freshness_score * 0.1
            )
            
            result.score = final_score
        
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _calculate_keyword_match(self, result: SearchResult, keywords: List[str]) -> float:
        """키워드 매칭 점수"""
        if not keywords:
            return 0.5
        
        text = f"{result.name} {result.description}".lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text)
        
        return matches / len(keywords)
    
    def _calculate_popularity_score(self, result: SearchResult) -> float:
        """인기도 점수"""
        if result.source == 'github':
            stars = result.metadata.get('stars', 0)
            return min(stars / 10000, 1.0)  # 10k stars = 1.0
        elif result.source == 'npm':
            downloads = result.metadata.get('downloads', 0)
            return min(downloads / 1000000, 1.0)  # 1M downloads = 1.0
        
        return 0.5
    
    def _calculate_freshness_score(self, result: SearchResult) -> float:
        """최신성 점수"""
        # 간단한 구현 - 실제로는 updated_at 파싱 필요
        return 0.8


class QualityEvaluator:
    """품질 평가기"""
    
    async def evaluate(self, result: SearchResult) -> float:
        """품질 점수 계산"""
        
        score = 0.5  # 기본 점수
        
        # 문서화 점수
        if result.description and len(result.description) > 20:
            score += 0.1
        
        # 라이선스 점수
        license_name = result.metadata.get('license', '').lower()
        if any(good_license in license_name for good_license in ['mit', 'apache', 'bsd']):
            score += 0.1
        
        # 소스별 추가 평가
        if result.source == 'github':
            score += self._evaluate_github_quality(result)
        elif result.source == 'npm':
            score += self._evaluate_npm_quality(result)
        
        return min(score, 1.0)
    
    def _evaluate_github_quality(self, result: SearchResult) -> float:
        """GitHub 품질 평가"""
        score = 0.0
        
        stars = result.metadata.get('stars', 0)
        forks = result.metadata.get('forks', 0)
        
        if stars > 100:
            score += 0.1
        if stars > 1000:
            score += 0.1
        if forks > 10:
            score += 0.1
        
        return score
    
    def _evaluate_npm_quality(self, result: SearchResult) -> float:
        """NPM 품질 평가"""
        score = 0.0
        
        downloads = result.metadata.get('downloads', 0)
        
        if downloads > 1000:
            score += 0.1
        if downloads > 100000:
            score += 0.1
        
        return score