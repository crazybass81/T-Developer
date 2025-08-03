# backend/src/agents/implementations/search_optimization.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from agno.agent import Agent
from agno.models.aws import AwsBedrock

@dataclass
class OptimizationRecommendation:
    type: str
    priority: str  # high, medium, low
    description: str
    expected_impact: float
    implementation_effort: str

class SearchOptimizer:
    """검색 최적화 엔진"""

    def __init__(self):
        self.optimizer_agent = Agent(
            name="Search-Optimizer",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Search optimization specialist",
            instructions=[
                "Analyze search performance data",
                "Identify optimization opportunities",
                "Recommend specific improvements",
                "Prioritize recommendations by impact"
            ],
            temperature=0.2
        )
        
        self.query_expander = QueryExpander()
        self.result_ranker = ResultRanker()

    async def optimize_search_performance(
        self,
        analytics_data: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """검색 성능 최적화 추천"""
        
        recommendations = []
        
        # 쿼리 확장 최적화
        if analytics_data.get('zero_result_rate', 0) > 0.2:
            recommendations.append(OptimizationRecommendation(
                type='query_expansion',
                priority='high',
                description='Implement query expansion for zero-result queries',
                expected_impact=0.3,
                implementation_effort='medium'
            ))
        
        # 결과 랭킹 개선
        if performance_metrics.get('mrr', 0) < 0.5:
            recommendations.append(OptimizationRecommendation(
                type='ranking_improvement',
                priority='high',
                description='Improve result ranking algorithm',
                expected_impact=0.4,
                implementation_effort='high'
            ))
        
        # 응답 시간 최적화
        if performance_metrics.get('avg_response_time', 0) > 1000:
            recommendations.append(OptimizationRecommendation(
                type='performance_optimization',
                priority='medium',
                description='Optimize search response time',
                expected_impact=0.2,
                implementation_effort='medium'
            ))
        
        # 캐시 최적화
        cache_hit_rate = performance_metrics.get('cache_hit_rate', 0)
        if cache_hit_rate < 0.7:
            recommendations.append(OptimizationRecommendation(
                type='cache_optimization',
                priority='medium',
                description='Improve cache hit rate',
                expected_impact=0.25,
                implementation_effort='low'
            ))
        
        return sorted(recommendations, key=lambda x: x.expected_impact, reverse=True)

    async def optimize_query(self, query: str, context: Dict[str, Any]) -> str:
        """개별 쿼리 최적화"""
        
        # 쿼리 확장
        expanded_query = await self.query_expander.expand(query, context)
        
        # 동의어 처리
        synonymized_query = await self._apply_synonyms(expanded_query)
        
        # 오타 수정
        corrected_query = await self._correct_typos(synonymized_query)
        
        return corrected_query

    async def _apply_synonyms(self, query: str) -> str:
        """동의어 적용"""
        synonym_map = {
            'js': 'javascript',
            'py': 'python',
            'db': 'database',
            'api': 'application programming interface'
        }
        
        words = query.lower().split()
        expanded_words = [synonym_map.get(word, word) for word in words]
        return ' '.join(expanded_words)

    async def _correct_typos(self, query: str) -> str:
        """오타 수정"""
        # 간단한 오타 수정 로직
        corrections = {
            'javascirpt': 'javascript',
            'pyhton': 'python',
            'databse': 'database'
        }
        
        for typo, correction in corrections.items():
            query = query.replace(typo, correction)
        
        return query

class QueryExpander:
    """쿼리 확장기"""

    async def expand(self, query: str, context: Dict[str, Any]) -> str:
        """쿼리 확장"""
        
        # 기술 스택 기반 확장
        if 'react' in query.lower():
            return f"{query} frontend javascript ui"
        elif 'python' in query.lower():
            return f"{query} backend programming language"
        elif 'database' in query.lower():
            return f"{query} sql nosql storage"
        
        return query

class ResultRanker:
    """결과 랭킹 최적화"""

    def __init__(self):
        self.ranking_factors = {
            'relevance': 0.4,
            'popularity': 0.3,
            'quality': 0.2,
            'freshness': 0.1
        }

    async def rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """결과 재랭킹"""
        
        scored_results = []
        
        for result in results:
            score = await self._calculate_ranking_score(result, query, user_context)
            result['ranking_score'] = score
            scored_results.append(result)
        
        return sorted(scored_results, key=lambda x: x['ranking_score'], reverse=True)

    async def _calculate_ranking_score(
        self,
        result: Dict[str, Any],
        query: str,
        context: Dict[str, Any]
    ) -> float:
        """랭킹 점수 계산"""
        
        # 관련성 점수
        relevance = self._calculate_relevance(result, query)
        
        # 인기도 점수
        popularity = result.get('popularity_score', 0.5)
        
        # 품질 점수
        quality = result.get('quality_score', 0.5)
        
        # 신선도 점수
        freshness = self._calculate_freshness(result)
        
        # 가중 합계
        total_score = (
            relevance * self.ranking_factors['relevance'] +
            popularity * self.ranking_factors['popularity'] +
            quality * self.ranking_factors['quality'] +
            freshness * self.ranking_factors['freshness']
        )
        
        return float(total_score)

    def _calculate_relevance(self, result: Dict[str, Any], query: str) -> float:
        """관련성 계산"""
        query_words = set(query.lower().split())
        result_text = f"{result.get('name', '')} {result.get('description', '')}".lower()
        result_words = set(result_text.split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words & result_words
        return len(intersection) / len(query_words)

    def _calculate_freshness(self, result: Dict[str, Any]) -> float:
        """신선도 계산"""
        last_updated = result.get('last_updated')
        if not last_updated:
            return 0.5
        
        # 간단한 신선도 계산 (실제로는 더 복잡한 로직 필요)
        from datetime import datetime, timedelta
        
        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except:
                return 0.5
        
        days_old = (datetime.now() - last_updated.replace(tzinfo=None)).days
        
        if days_old < 30:
            return 1.0
        elif days_old < 90:
            return 0.8
        elif days_old < 365:
            return 0.6
        else:
            return 0.3