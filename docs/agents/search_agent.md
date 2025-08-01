# Search Agent

## 개요
Search Agent는 다양한 소스에서 컴포넌트를 검색하고, 지능형 쿼리 확장과 실시간 인덱싱을 통해 최적의 검색 결과를 제공합니다.

## 주요 기능

### 1. 다중 소스 검색 엔진
- NPM, GitHub, PyPI, Maven 등 다양한 소스 지원
- 병렬 검색으로 빠른 결과 제공

```python
search_engine = MultiSourceSearchEngine()
results = await search_engine.search_components('react component')
```

### 2. 지능형 쿼리 확장
- AI 기반 쿼리 확장
- 컨텍스트 인식 검색어 생성

```python
expander = IntelligentQueryExpander()
expanded_queries = await expander.expand_query('ui component', context)
```

### 3. 실시간 인덱싱 시스템
- 컴포넌트 메타데이터 자동 추출
- 검색 키워드 자동 생성

```python
indexer = RealtimeIndexingSystem()
await indexer.index_component(component)
```

### 4. 검색 결과 랭킹 시스템
- 관련성, 인기도, 품질, 최신성 기반 랭킹
- 가중치 기반 종합 점수 계산

```python
ranker = SearchResultRanker()
ranked_results = await ranker.rank_results(results, query, context)
```

## 검색 소스

### 지원 소스
- **NPM**: JavaScript/TypeScript 패키지
- **GitHub**: 오픈소스 저장소
- **PyPI**: Python 패키지
- **Maven**: Java 라이브러리

### 랭킹 요소
- 관련성 (40%)
- 인기도 (20%)
- 품질 (20%)
- 최신성 (10%)
- 호환성 (10%)

## 사용 예시

```python
from search.search_agent import MultiSourceSearchEngine, SearchResultRanker

# 컴포넌트 검색
search_engine = MultiSourceSearchEngine()
results = await search_engine.search_components(
    'responsive table component',
    {'language': 'javascript', 'framework': 'react'}
)

# 결과 랭킹
ranker = SearchResultRanker()
ranked_results = await ranker.rank_results(
    results, 
    'responsive table component',
    {'project_type': 'web'}
)

print(f"Found {len(ranked_results)} components")
for result in ranked_results[:5]:
    print(f"- {result.name}: {result.relevance_score:.2f}")
```

## 설정

환경 변수:
- `GITHUB_TOKEN`: GitHub API 토큰
- `NPM_REGISTRY_URL`: NPM 레지스트리 URL
- `SEARCH_CACHE_TTL`: 검색 캐시 TTL (기본: 3600초)
- `MAX_SEARCH_RESULTS`: 최대 검색 결과 수 (기본: 50)