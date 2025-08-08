"""
Search Agent Core Implementation
Phase 4 Tasks 4.51-4.60: 컴포넌트 검색 및 탐색 에이전트
"""

import json
import logging
import os
import time
import asyncio
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict
import numpy as np
from urllib.parse import urlparse
import aiohttp
import hashlib

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from botocore.exceptions import ClientError

# Agno Framework 통합
try:
    from agno.agent import Agent
    from agno.models.aws import AwsBedrock
    from agno.memory import ConversationSummaryMemory
    from agno.tools import Tool
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

# Production 로깅 설정
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# AWS 클라이언트
ssm = boto3.client('ssm')
secrets = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')
elasticsearch = boto3.client('es')


class SearchSource(Enum):
    """검색 소스"""
    GITHUB = "github"
    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    DOCKER_HUB = "docker-hub"
    AWS_MARKETPLACE = "aws-marketplace"
    INTERNAL = "internal"
    CUSTOM = "custom"


class SearchStrategy(Enum):
    """검색 전략"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    FACETED = "faceted"
    GRAPH_BASED = "graph-based"
    ML_ENHANCED = "ml-enhanced"


class SearchFilter(Enum):
    """검색 필터"""
    LICENSE = "license"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    STARS = "stars"
    DOWNLOADS = "downloads"
    LAST_UPDATED = "last-updated"
    COMPATIBILITY = "compatibility"
    SECURITY = "security"


@dataclass
class SearchQuery:
    """검색 쿼리"""
    query_text: str
    source: SearchSource
    filters: Dict[SearchFilter, Any]
    strategy: SearchStrategy
    max_results: int = 50
    include_metrics: bool = True
    include_dependencies: bool = True


@dataclass
class SearchResult:
    """검색 결과"""
    id: str
    name: str
    source: SearchSource
    url: str
    description: str
    version: str
    license: str
    score: float
    metrics: Dict[str, Any]
    dependencies: List[str]
    metadata: Dict[str, Any]


@dataclass
class SearchSession:
    """검색 세션"""
    session_id: str
    queries: List[SearchQuery]
    results: List[SearchResult]
    refinements: List[Dict[str, Any]]
    context: Dict[str, Any]
    timestamp: float


@dataclass
class ComponentRepository:
    """컴포넌트 저장소"""
    name: str
    source: SearchSource
    url: str
    api_endpoint: Optional[str]
    authentication: Optional[Dict[str, Any]]
    rate_limit: Optional[Dict[str, Any]]
    cache_config: Optional[Dict[str, Any]]


@dataclass
class SearchIndex:
    """검색 인덱스"""
    index_name: str
    index_type: str  # elasticsearch, algolia, custom
    mappings: Dict[str, Any]
    settings: Dict[str, Any]
    last_updated: float
    document_count: int


@dataclass
class SearchAnalytics:
    """검색 분석"""
    total_searches: int
    avg_response_time: float
    hit_rate: float
    popular_queries: List[str]
    failed_searches: List[str]
    user_satisfaction: float


class ComponentSearcher(Tool):
    """컴포넌트 검색 도구 (Agno Tool)"""
    
    def __init__(self):
        super().__init__(
            name="component_searcher",
            description="Search and discover components from various sources"
        )
        self._init_repositories()
        self._init_search_clients()
    
    def _init_repositories(self):
        """저장소 초기화"""
        self.repositories = {
            SearchSource.GITHUB: ComponentRepository(
                name="GitHub",
                source=SearchSource.GITHUB,
                url="https://github.com",
                api_endpoint="https://api.github.com",
                authentication={"type": "token"},
                rate_limit={"requests_per_hour": 5000},
                cache_config={"ttl": 3600}
            ),
            SearchSource.NPM: ComponentRepository(
                name="NPM Registry",
                source=SearchSource.NPM,
                url="https://www.npmjs.com",
                api_endpoint="https://registry.npmjs.org",
                authentication=None,
                rate_limit={"requests_per_minute": 100},
                cache_config={"ttl": 1800}
            ),
            SearchSource.PYPI: ComponentRepository(
                name="PyPI",
                source=SearchSource.PYPI,
                url="https://pypi.org",
                api_endpoint="https://pypi.org/pypi",
                authentication=None,
                rate_limit={"requests_per_minute": 60},
                cache_config={"ttl": 1800}
            )
        }
    
    def _init_search_clients(self):
        """검색 클라이언트 초기화"""
        self.search_clients = {}
        # 실제 구현에서는 각 소스별 클라이언트 초기화
    
    async def run(
        self,
        query: SearchQuery,
        context: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """검색 실행"""
        # 저장소 선택
        repository = self.repositories.get(query.source)
        if not repository:
            return []
        
        # 검색 수행
        results = await self._search_repository(query, repository)
        
        # 결과 필터링
        filtered_results = self._apply_filters(results, query.filters)
        
        # 점수 계산 및 정렬
        scored_results = self._score_results(filtered_results, query)
        
        return scored_results[:query.max_results]
    
    async def _search_repository(
        self,
        query: SearchQuery,
        repository: ComponentRepository
    ) -> List[SearchResult]:
        """저장소 검색"""
        # 실제 API 호출 구현
        # 여기서는 모의 결과 반환
        mock_results = []
        
        if query.source == SearchSource.NPM:
            mock_results = [
                SearchResult(
                    id=f"npm-{i}",
                    name=f"component-{i}",
                    source=SearchSource.NPM,
                    url=f"https://npmjs.com/package/component-{i}",
                    description=f"Component {i} description",
                    version=f"1.0.{i}",
                    license="MIT",
                    score=0.8 - i * 0.1,
                    metrics={"downloads": 1000 - i * 100, "stars": 100 - i * 10},
                    dependencies=[],
                    metadata={}
                )
                for i in range(5)
            ]
        
        return mock_results
    
    def _apply_filters(
        self,
        results: List[SearchResult],
        filters: Dict[SearchFilter, Any]
    ) -> List[SearchResult]:
        """필터 적용"""
        filtered = results
        
        for filter_type, filter_value in filters.items():
            if filter_type == SearchFilter.LICENSE:
                filtered = [r for r in filtered if r.license == filter_value]
            elif filter_type == SearchFilter.LANGUAGE:
                filtered = [r for r in filtered if filter_value in r.metadata.get('languages', [])]
        
        return filtered
    
    def _score_results(
        self,
        results: List[SearchResult],
        query: SearchQuery
    ) -> List[SearchResult]:
        """결과 점수 계산"""
        # 이미 점수가 있는 경우 정렬만
        return sorted(results, key=lambda r: r.score, reverse=True)


class SearchAgent:
    """Production-ready Search Agent with full Task 4.51-4.60 implementation"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # Agno Agent 초기화
        if AGNO_AVAILABLE:
            self._init_agno_agent()
        else:
            logger.warning("Agno Framework not available, using fallback mode")
            self.agent = None
        
        # 컴포넌트 초기화
        self._init_components()
        
        # 검색 인덱스 초기화
        self._init_search_indices()
        
        # 캐시 초기화
        self._init_cache()
        
        # 메트릭 초기화
        self.search_times = []
        self.search_hit_rates = []
        
        logger.info(f"Search Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/search-agent/',
                Recursive=True,
                WithDecryption=True
            )
            
            config = {}
            for param in response['Parameters']:
                key = param['Name'].split('/')[-1]
                config[key] = param['Value']
            
            return config
        except ClientError as e:
            logger.error(f"Failed to load config: {e}")
            return {
                'max_search_results': 100,
                'search_timeout': 30,
                'cache_ttl': 3600,
                'use_elasticsearch': True,
                'use_ml_ranking': True,
                'parallel_search': True,
                'github_token': None,
                'npm_token': None
            }
    
    def _init_agno_agent(self):
        """Agno 에이전트 초기화"""
        try:
            self.agent = Agent(
                name="Component-Search-Expert",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-v2:0",
                    region="us-east-1"
                ),
                role="Expert in searching and discovering software components",
                instructions=[
                    "Search components from multiple sources (GitHub, NPM, PyPI, etc.)",
                    "Apply intelligent filters and ranking",
                    "Perform semantic and fuzzy search",
                    "Analyze component quality and compatibility",
                    "Track component dependencies and versions",
                    "Provide search analytics and insights",
                    "Optimize search queries for better results"
                ],
                memory=ConversationSummaryMemory(
                    storage_type="dynamodb",
                    table_name=f"t-dev-search-sessions-{self.environment}"
                ),
                tools=[
                    ComponentSearcher()
                ],
                temperature=0.3,
                max_retries=3
            )
            logger.info("Agno agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno agent: {e}")
            self.agent = None
    
    def _init_components(self):
        """컴포넌트 초기화"""
        from .query_builder import QueryBuilder
        from .multi_source_searcher import MultiSourceSearcher
        from .semantic_searcher import SemanticSearcher
        from .faceted_searcher import FacetedSearcher
        from .dependency_resolver import DependencyResolver
        from .quality_analyzer import QualityAnalyzer
        from .compatibility_checker import CompatibilityChecker
        from .search_optimizer import SearchOptimizer
        from .result_ranker import ResultRanker
        from .analytics_tracker import AnalyticsTracker
        
        self.query_builder = QueryBuilder()
        self.multi_source_searcher = MultiSourceSearcher()
        self.semantic_searcher = SemanticSearcher()
        self.faceted_searcher = FacetedSearcher()
        self.dependency_resolver = DependencyResolver()
        self.quality_analyzer = QualityAnalyzer()
        self.compatibility_checker = CompatibilityChecker()
        self.search_optimizer = SearchOptimizer()
        self.result_ranker = ResultRanker()
        self.analytics_tracker = AnalyticsTracker()
    
    def _init_search_indices(self):
        """검색 인덱스 초기화"""
        self.search_indices = {
            'components': SearchIndex(
                index_name='t-dev-components',
                index_type='elasticsearch',
                mappings={
                    'properties': {
                        'name': {'type': 'text', 'analyzer': 'standard'},
                        'description': {'type': 'text'},
                        'tags': {'type': 'keyword'},
                        'version': {'type': 'keyword'},
                        'license': {'type': 'keyword'},
                        'downloads': {'type': 'long'},
                        'stars': {'type': 'integer'},
                        'last_updated': {'type': 'date'}
                    }
                },
                settings={
                    'number_of_shards': 3,
                    'number_of_replicas': 1
                },
                last_updated=time.time(),
                document_count=0
            ),
            'templates': SearchIndex(
                index_name='t-dev-templates',
                index_type='elasticsearch',
                mappings={
                    'properties': {
                        'name': {'type': 'text'},
                        'category': {'type': 'keyword'},
                        'framework': {'type': 'keyword'},
                        'components': {'type': 'nested'}
                    }
                },
                settings={
                    'number_of_shards': 2,
                    'number_of_replicas': 1
                },
                last_updated=time.time(),
                document_count=0
            )
        }
    
    def _init_cache(self):
        """캐시 초기화"""
        self.cache = {
            'queries': {},  # 쿼리 캐시
            'results': {},  # 결과 캐시
            'metadata': {}  # 메타데이터 캐시
        }
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    async def search_components(
        self,
        requirements: Dict[str, Any],
        technology_stack: Dict[str, Any],
        matching_result: Dict[str, Any],
        search_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        컴포넌트 검색 수행 (Tasks 4.51-4.60)
        
        Args:
            requirements: 파싱된 요구사항
            technology_stack: 선택된 기술 스택
            matching_result: 매칭 결과
            search_config: 검색 설정
            
        Returns:
            Dict: 검색 결과
        """
        start_time = time.time()
        
        try:
            # 1. 검색 쿼리 구성 (Task 4.51)
            search_queries = await self._build_search_queries(
                requirements, technology_stack, matching_result
            )
            
            # 2. 다중 소스 검색 (Task 4.52)
            multi_source_results = await self._search_multiple_sources(
                search_queries, search_config
            )
            
            # 3. 의미적 검색 (Task 4.53)
            semantic_results = await self._perform_semantic_search(
                requirements, multi_source_results
            )
            
            # 4. 패싯 검색 (Task 4.54)
            faceted_results = await self._perform_faceted_search(
                search_queries, multi_source_results
            )
            
            # 5. 의존성 해결 (Task 4.55)
            dependency_resolution = await self._resolve_dependencies(
                semantic_results, technology_stack
            )
            
            # 6. 품질 분석 (Task 4.56)
            quality_analysis = await self._analyze_quality(
                semantic_results, dependency_resolution
            )
            
            # 7. 호환성 검증 (Task 4.57)
            compatibility_check = await self._check_compatibility(
                semantic_results, technology_stack
            )
            
            # 8. 검색 최적화 (Task 4.58)
            optimized_results = await self._optimize_search(
                semantic_results, quality_analysis, compatibility_check
            )
            
            # 9. 결과 순위 결정 (Task 4.59)
            ranked_results = await self._rank_results(
                optimized_results, requirements, quality_analysis
            )
            
            # 10. 검색 분석 (Task 4.60)
            search_analytics = await self._analyze_search(
                search_queries, ranked_results, start_time
            )
            
            # 최종 결과 구성
            final_results = {
                'search_results': ranked_results,
                'facets': faceted_results,
                'dependencies': dependency_resolution,
                'quality_metrics': quality_analysis,
                'compatibility': compatibility_check,
                'analytics': search_analytics,
                'metadata': {
                    'total_results': len(ranked_results),
                    'sources_searched': list(set(r.source.value for r in ranked_results)),
                    'search_time': time.time() - start_time,
                    'cache_hit_rate': self._calculate_cache_hit_rate()
                }
            }
            
            # 메트릭 기록
            processing_time = time.time() - start_time
            self.search_times.append(processing_time)
            
            metrics.add_metric(
                name="SearchTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            metrics.add_metric(
                name="SearchResults",
                unit=MetricUnit.Count,
                value=len(ranked_results)
            )
            
            logger.info(
                "Successfully completed component search",
                extra={
                    "total_results": len(ranked_results),
                    "processing_time": processing_time,
                    "sources": final_results['metadata']['sources_searched']
                }
            )
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            metrics.add_metric(name="SearchError", unit=MetricUnit.Count, value=1)
            raise
    
    async def _build_search_queries(
        self,
        requirements: Dict[str, Any],
        technology_stack: Dict[str, Any],
        matching_result: Dict[str, Any]
    ) -> List[SearchQuery]:
        """Task 4.51: 검색 쿼리 구성"""
        queries = []
        
        # 매칭되지 않은 요구사항에 대한 쿼리 생성
        for unmatched_req in matching_result.get('unmatched_requirements', []):
            query = await self.query_builder.build_from_requirement(
                unmatched_req, technology_stack
            )
            queries.append(query)
        
        # 낮은 매칭률 컴포넌트에 대한 대체 검색
        for match in matching_result.get('component_matches', []):
            if match['match_score'] < 0.5:
                alt_query = await self.query_builder.build_alternative_query(
                    match, technology_stack
                )
                queries.append(alt_query)
        
        # 기술 스택 기반 추가 컴포넌트 검색
        stack_queries = await self.query_builder.build_from_stack(technology_stack)
        queries.extend(stack_queries)
        
        return queries
    
    async def _search_multiple_sources(
        self,
        queries: List[SearchQuery],
        config: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Task 4.52: 다중 소스 검색"""
        all_results = []
        
        # 병렬 검색 수행
        if self.config.get('parallel_search', True):
            search_tasks = []
            for query in queries:
                task = self.multi_source_searcher.search(query, config)
                search_tasks.append(task)
            
            results_lists = await asyncio.gather(*search_tasks)
            for results in results_lists:
                all_results.extend(results)
        else:
            # 순차 검색
            for query in queries:
                results = await self.multi_source_searcher.search(query, config)
                all_results.extend(results)
        
        # 중복 제거
        unique_results = self._deduplicate_results(all_results)
        
        return unique_results
    
    async def _perform_semantic_search(
        self,
        requirements: Dict[str, Any],
        initial_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Task 4.53: 의미적 검색"""
        # 요구사항을 벡터로 변환
        req_embeddings = await self.semantic_searcher.get_embeddings(requirements)
        
        # 결과를 벡터로 변환하고 유사도 계산
        enhanced_results = await self.semantic_searcher.enhance_with_semantics(
            initial_results, req_embeddings
        )
        
        return enhanced_results
    
    async def _perform_faceted_search(
        self,
        queries: List[SearchQuery],
        results: List[SearchResult]
    ) -> Dict[str, Any]:
        """Task 4.54: 패싯 검색"""
        return await self.faceted_searcher.generate_facets(queries, results)
    
    async def _resolve_dependencies(
        self,
        results: List[SearchResult],
        technology_stack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Task 4.55: 의존성 해결"""
        return await self.dependency_resolver.resolve(results, technology_stack)
    
    async def _analyze_quality(
        self,
        results: List[SearchResult],
        dependencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Task 4.56: 품질 분석"""
        return await self.quality_analyzer.analyze(results, dependencies)
    
    async def _check_compatibility(
        self,
        results: List[SearchResult],
        technology_stack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Task 4.57: 호환성 검증"""
        return await self.compatibility_checker.check(results, technology_stack)
    
    async def _optimize_search(
        self,
        results: List[SearchResult],
        quality: Dict[str, Any],
        compatibility: Dict[str, Any]
    ) -> List[SearchResult]:
        """Task 4.58: 검색 최적화"""
        return await self.search_optimizer.optimize(results, quality, compatibility)
    
    async def _rank_results(
        self,
        results: List[SearchResult],
        requirements: Dict[str, Any],
        quality: Dict[str, Any]
    ) -> List[SearchResult]:
        """Task 4.59: 결과 순위 결정"""
        if self.config.get('use_ml_ranking', True):
            return await self.result_ranker.rank_with_ml(results, requirements, quality)
        else:
            return await self.result_ranker.rank_with_heuristics(results, requirements, quality)
    
    async def _analyze_search(
        self,
        queries: List[SearchQuery],
        results: List[SearchResult],
        start_time: float
    ) -> SearchAnalytics:
        """Task 4.60: 검색 분석"""
        analytics = await self.analytics_tracker.track(
            queries, results, time.time() - start_time
        )
        
        # 분석 결과를 DynamoDB에 저장
        await self._save_analytics(analytics)
        
        return analytics
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """결과 중복 제거"""
        seen = set()
        unique = []
        
        for result in results:
            # 이름과 소스 조합으로 고유성 판단
            key = f"{result.name}:{result.source.value}:{result.version}"
            if key not in seen:
                seen.add(key)
                unique.append(result)
        
        return unique
    
    def _calculate_cache_hit_rate(self) -> float:
        """캐시 히트율 계산"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        if total == 0:
            return 0.0
        return self.cache_stats['hits'] / total
    
    async def _save_analytics(self, analytics: SearchAnalytics):
        """분석 결과 저장"""
        try:
            table = dynamodb.Table(f't-dev-search-analytics-{self.environment}')
            table.put_item(
                Item={
                    'timestamp': int(time.time()),
                    'analytics': asdict(analytics)
                }
            )
        except Exception as e:
            logger.error(f"Failed to save analytics: {e}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    import asyncio
    
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        requirements = body.get('requirements', {})
        technology_stack = body.get('technology_stack', {})
        matching_result = body.get('matching_result', {})
        search_config = body.get('search_config')
        
        # Agent 실행
        agent = SearchAgent()
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        search_results = loop.run_until_complete(
            agent.search_components(
                requirements,
                technology_stack,
                matching_result,
                search_config
            )
        )
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(search_results, ensure_ascii=False, default=str)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Error searching components'
                }
            }, ensure_ascii=False)
        }