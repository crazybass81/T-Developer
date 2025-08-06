# backend/src/agents/implementations/search/cache_strategies.py
from typing import Dict, List, Any, Optional, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
import asyncio

class CacheStrategy(Protocol):
    """캐시 전략 인터페이스"""
    
    async def should_cache(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """캐시 저장 여부 결정"""
        ...
    
    def calculate_ttl(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> int:
        """TTL 계산"""
        ...

@dataclass
class CacheDecision:
    should_cache: bool
    ttl: int
    priority: int  # 1-10
    reason: str

class AdaptiveCacheStrategy:
    """적응형 캐시 전략"""

    def __init__(self):
        self.query_patterns = {}
        self.performance_history = {}
        self.base_ttl = 3600  # 1시간

    async def should_cache(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> CacheDecision:
        """종합적인 캐시 결정"""

        # 1. 쿼리 빈도 분석
        frequency_score = self._analyze_query_frequency(query)
        
        # 2. 결과 안정성 분석
        stability_score = await self._analyze_result_stability(query, results)
        
        # 3. 컴퓨팅 비용 분석
        cost_score = self._analyze_computation_cost(query, context)
        
        # 4. 메모리 효율성 분석
        memory_score = self._analyze_memory_efficiency(results)

        # 종합 점수 계산
        total_score = (
            frequency_score * 0.3 +
            stability_score * 0.3 +
            cost_score * 0.2 +
            memory_score * 0.2
        )

        # 캐시 결정
        should_cache = total_score >= 0.6
        ttl = self._calculate_adaptive_ttl(total_score, context)
        priority = min(10, int(total_score * 10))

        return CacheDecision(
            should_cache=should_cache,
            ttl=ttl,
            priority=priority,
            reason=f"Score: {total_score:.2f} (freq:{frequency_score:.2f}, stability:{stability_score:.2f})"
        )

    def _analyze_query_frequency(self, query: str) -> float:
        """쿼리 빈도 분석"""
        pattern_key = self._normalize_query(query)
        
        if pattern_key not in self.query_patterns:
            self.query_patterns[pattern_key] = {
                'count': 1,
                'first_seen': time.time(),
                'last_seen': time.time()
            }
            return 0.1  # 새로운 쿼리는 낮은 점수
        
        pattern = self.query_patterns[pattern_key]
        pattern['count'] += 1
        pattern['last_seen'] = time.time()
        
        # 빈도 기반 점수 (로그 스케일)
        import math
        frequency_score = min(1.0, math.log(pattern['count']) / math.log(100))
        
        # 최근성 가중치
        time_diff = time.time() - pattern['last_seen']
        recency_weight = max(0.1, 1.0 - (time_diff / 86400))  # 24시간 기준
        
        return frequency_score * recency_weight

    async def _analyze_result_stability(
        self,
        query: str,
        current_results: List[Dict[str, Any]]
    ) -> float:
        """결과 안정성 분석"""
        
        query_hash = hash(query)
        
        if query_hash not in self.performance_history:
            self.performance_history[query_hash] = {
                'results_history': [current_results],
                'stability_score': 0.5
            }
            return 0.5
        
        history = self.performance_history[query_hash]
        history['results_history'].append(current_results)
        
        # 최근 5개 결과만 유지
        if len(history['results_history']) > 5:
            history['results_history'] = history['results_history'][-5:]
        
        # 결과 유사도 계산
        if len(history['results_history']) >= 2:
            similarity_scores = []
            for i in range(1, len(history['results_history'])):
                similarity = self._calculate_result_similarity(
                    history['results_history'][i-1],
                    history['results_history'][i]
                )
                similarity_scores.append(similarity)
            
            stability_score = sum(similarity_scores) / len(similarity_scores)
            history['stability_score'] = stability_score
            return stability_score
        
        return 0.5

    def _calculate_result_similarity(
        self,
        results1: List[Dict[str, Any]],
        results2: List[Dict[str, Any]]
    ) -> float:
        """두 결과 집합의 유사도 계산"""
        
        if not results1 or not results2:
            return 0.0
        
        # ID 기반 교집합 계산
        ids1 = {r.get('id', '') for r in results1}
        ids2 = {r.get('id', '') for r in results2}
        
        intersection = len(ids1 & ids2)
        union = len(ids1 | ids2)
        
        return intersection / union if union > 0 else 0.0

    def _analyze_computation_cost(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> float:
        """컴퓨팅 비용 분석"""
        
        cost_factors = 0.0
        
        # 쿼리 복잡도
        if len(query.split()) > 5:
            cost_factors += 0.3
        
        # 필터 복잡도
        filters = context.get('filters', {})
        if len(filters) > 3:
            cost_factors += 0.2
        
        # 정렬 요구사항
        if context.get('sort_by'):
            cost_factors += 0.2
        
        # 페이지네이션
        if context.get('page_size', 10) > 50:
            cost_factors += 0.3
        
        return min(1.0, cost_factors)

    def _analyze_memory_efficiency(
        self,
        results: List[Dict[str, Any]]
    ) -> float:
        """메모리 효율성 분석"""
        
        if not results:
            return 1.0  # 빈 결과는 효율적
        
        # 결과 크기 추정
        import sys
        total_size = sum(sys.getsizeof(str(result)) for result in results)
        size_mb = total_size / (1024 * 1024)
        
        # 크기 기반 효율성 점수
        if size_mb < 1:
            return 1.0
        elif size_mb < 5:
            return 0.8
        elif size_mb < 10:
            return 0.6
        else:
            return 0.3

    def _calculate_adaptive_ttl(
        self,
        score: float,
        context: Dict[str, Any]
    ) -> int:
        """적응형 TTL 계산"""
        
        # 기본 TTL에 점수 기반 배수 적용
        base_multiplier = 0.5 + (score * 1.5)  # 0.5 ~ 2.0
        
        # 컨텍스트 기반 조정
        context_multiplier = 1.0
        
        if context.get('real_time', False):
            context_multiplier *= 0.1  # 실시간 데이터는 짧은 TTL
        
        if context.get('stable_data', False):
            context_multiplier *= 2.0  # 안정적 데이터는 긴 TTL
        
        final_ttl = int(self.base_ttl * base_multiplier * context_multiplier)
        
        # TTL 범위 제한
        return max(60, min(86400, final_ttl))  # 1분 ~ 24시간

class QueryBasedCacheStrategy:
    """쿼리 기반 캐시 전략"""

    def __init__(self):
        self.strategy_rules = {
            'popular_components': {
                'patterns': ['react', 'vue', 'angular', 'node'],
                'ttl': 7200,  # 2시간
                'priority': 9
            },
            'specific_versions': {
                'patterns': ['@', 'version', 'v1', 'v2'],
                'ttl': 1800,  # 30분
                'priority': 7
            },
            'broad_searches': {
                'patterns': ['component', 'library', 'framework'],
                'ttl': 3600,  # 1시간
                'priority': 5
            }
        }

    async def should_cache(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> CacheDecision:
        """쿼리 패턴 기반 캐시 결정"""

        query_lower = query.lower()
        
        for strategy_name, config in self.strategy_rules.items():
            if any(pattern in query_lower for pattern in config['patterns']):
                return CacheDecision(
                    should_cache=True,
                    ttl=config['ttl'],
                    priority=config['priority'],
                    reason=f"Matched strategy: {strategy_name}"
                )
        
        # 기본 전략
        return CacheDecision(
            should_cache=len(results) > 0,
            ttl=1800,  # 30분
            priority=3,
            reason="Default strategy"
        )

class ResultBasedCacheStrategy:
    """결과 기반 캐시 전략"""

    async def should_cache(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> CacheDecision:
        """결과 특성 기반 캐시 결정"""

        if not results:
            return CacheDecision(
                should_cache=False,
                ttl=0,
                priority=0,
                reason="No results to cache"
            )

        # 결과 품질 분석
        quality_score = self._analyze_result_quality(results)
        
        # 결과 다양성 분석
        diversity_score = self._analyze_result_diversity(results)
        
        # 결과 완성도 분석
        completeness_score = self._analyze_result_completeness(results)

        # 종합 점수
        overall_score = (
            quality_score * 0.4 +
            diversity_score * 0.3 +
            completeness_score * 0.3
        )

        should_cache = overall_score >= 0.6
        ttl = int(1800 + (overall_score * 1800))  # 30분 ~ 1시간
        priority = min(10, int(overall_score * 10))

        return CacheDecision(
            should_cache=should_cache,
            ttl=ttl,
            priority=priority,
            reason=f"Result quality score: {overall_score:.2f}"
        )

    def _analyze_result_quality(self, results: List[Dict[str, Any]]) -> float:
        """결과 품질 분석"""
        
        quality_indicators = []
        
        for result in results:
            score = 0.0
            
            # 메타데이터 완성도
            if result.get('description'):
                score += 0.2
            if result.get('documentation_url'):
                score += 0.2
            if result.get('github_stars', 0) > 100:
                score += 0.3
            if result.get('last_updated'):
                score += 0.3
            
            quality_indicators.append(score)
        
        return sum(quality_indicators) / len(quality_indicators) if quality_indicators else 0.0

    def _analyze_result_diversity(self, results: List[Dict[str, Any]]) -> float:
        """결과 다양성 분석"""
        
        categories = set()
        languages = set()
        
        for result in results:
            if result.get('category'):
                categories.add(result['category'])
            if result.get('language'):
                languages.add(result['language'])
        
        # 다양성 점수 (카테고리와 언어 다양성)
        category_diversity = min(1.0, len(categories) / 5)  # 최대 5개 카테고리
        language_diversity = min(1.0, len(languages) / 3)  # 최대 3개 언어
        
        return (category_diversity + language_diversity) / 2

    def _analyze_result_completeness(self, results: List[Dict[str, Any]]) -> float:
        """결과 완성도 분석"""
        
        required_fields = ['id', 'name', 'description', 'version']
        completeness_scores = []
        
        for result in results:
            present_fields = sum(1 for field in required_fields if result.get(field))
            completeness = present_fields / len(required_fields)
            completeness_scores.append(completeness)
        
        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0

class HybridCacheStrategy:
    """하이브리드 캐시 전략"""

    def __init__(self):
        self.adaptive_strategy = AdaptiveCacheStrategy()
        self.query_strategy = QueryBasedCacheStrategy()
        self.result_strategy = ResultBasedCacheStrategy()

    async def should_cache(
        self,
        query: str,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> CacheDecision:
        """여러 전략을 조합한 최종 캐시 결정"""

        # 모든 전략 실행
        decisions = await asyncio.gather(
            self.adaptive_strategy.should_cache(query, results, context),
            self.query_strategy.should_cache(query, results, context),
            self.result_strategy.should_cache(query, results, context)
        )

        # 가중 평균으로 최종 결정
        weights = [0.4, 0.3, 0.3]  # adaptive, query, result
        
        should_cache_votes = sum(
            1 for decision in decisions if decision.should_cache
        )
        
        weighted_ttl = sum(
            decision.ttl * weight 
            for decision, weight in zip(decisions, weights)
        )
        
        weighted_priority = sum(
            decision.priority * weight 
            for decision, weight in zip(decisions, weights)
        )

        # 최종 결정 (과반수 찬성)
        final_should_cache = should_cache_votes >= 2
        
        return CacheDecision(
            should_cache=final_should_cache,
            ttl=int(weighted_ttl),
            priority=int(weighted_priority),
            reason=f"Hybrid decision: {should_cache_votes}/3 strategies agreed"
        )