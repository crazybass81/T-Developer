# backend/src/agents/implementations/search_analytics.py
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class SearchAnalytics:
    total_queries: int
    unique_queries: int
    avg_response_time: float
    zero_result_rate: float
    top_queries: List[Tuple[str, int]]
    query_trends: Dict[str, Any]

class SearchAnalyticsEngine:
    """검색 분석 엔진"""

    def __init__(self):
        self.query_analyzer = QueryPatternAnalyzer()
        self.trend_detector = TrendDetector()
        self.anomaly_detector = AnomalyDetector()

    async def analyze_search_patterns(
        self,
        query_logs: List[Dict[str, Any]],
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> SearchAnalytics:
        """검색 패턴 종합 분석"""
        
        # 기본 통계
        basic_stats = self._calculate_basic_stats(query_logs)
        
        # 쿼리 패턴 분석
        patterns = await self.query_analyzer.analyze(query_logs)
        
        # 트렌드 분석
        trends = await self.trend_detector.detect_trends(query_logs, 'daily')
        
        # 품질 메트릭
        quality_metrics = await self._calculate_quality_metrics(query_logs)
        
        return SearchAnalytics(
            total_queries=basic_stats['total_queries'],
            unique_queries=basic_stats['unique_queries'],
            avg_response_time=basic_stats['avg_response_time_ms'],
            zero_result_rate=basic_stats['zero_result_rate'],
            top_queries=basic_stats['top_queries'],
            query_trends=trends
        )

    def _calculate_basic_stats(self, query_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """기본 통계 계산"""
        total_queries = len(query_logs)
        unique_queries = len(set(log['query'] for log in query_logs))
        
        query_counts = Counter(log['query'] for log in query_logs)
        top_queries = query_counts.most_common(10)
        
        response_times = [log.get('response_time_ms', 0) for log in query_logs]
        avg_response_time = np.mean(response_times) if response_times else 0
        
        zero_results = sum(1 for log in query_logs if log.get('result_count', 0) == 0)
        zero_result_rate = zero_results / total_queries if total_queries > 0 else 0
        
        return {
            'total_queries': total_queries,
            'unique_queries': unique_queries,
            'top_queries': top_queries,
            'avg_response_time_ms': avg_response_time,
            'zero_result_rate': zero_result_rate
        }

    async def _calculate_quality_metrics(self, query_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """검색 품질 메트릭"""
        if not query_logs:
            return {'ctr': 0, 'mrr': 0}
            
        clicks = sum(1 for log in query_logs if log.get('clicked_results'))
        ctr = clicks / len(query_logs)
        
        # Mean Reciprocal Rank 계산
        reciprocal_ranks = []
        for log in query_logs:
            clicked = log.get('clicked_results', [])
            if clicked:
                first_position = min(click.get('position', 0) for click in clicked)
                reciprocal_ranks.append(1 / (first_position + 1))
            else:
                reciprocal_ranks.append(0)
        
        mrr = np.mean(reciprocal_ranks) if reciprocal_ranks else 0
        
        return {'ctr': ctr, 'mrr': mrr}

class QueryPatternAnalyzer:
    """쿼리 패턴 분석기"""

    async def analyze(self, query_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """쿼리 패턴 분석"""
        queries = [log['query'] for log in query_logs]
        
        # 쿼리 유형 분류
        query_types = self._classify_query_types(queries)
        
        # N-gram 분석
        ngrams = self._analyze_ngrams(queries)
        
        return {
            'query_types': query_types,
            'common_ngrams': ngrams,
            'avg_query_length': np.mean([len(q.split()) for q in queries]) if queries else 0
        }

    def _classify_query_types(self, queries: List[str]) -> Dict[str, int]:
        """쿼리 유형 분류"""
        types = {'short': 0, 'medium': 0, 'long': 0}
        
        for query in queries:
            word_count = len(query.split())
            if word_count <= 2:
                types['short'] += 1
            elif word_count <= 5:
                types['medium'] += 1
            else:
                types['long'] += 1
        
        return types

    def _analyze_ngrams(self, queries: List[str]) -> Dict[str, List[Tuple[str, int]]]:
        """N-gram 분석"""
        bigrams = []
        for query in queries:
            words = query.lower().split()
            for i in range(len(words) - 1):
                bigrams.append(f"{words[i]} {words[i+1]}")
        
        bigram_counts = Counter(bigrams).most_common(10)
        return {'bigrams': bigram_counts}

class TrendDetector:
    """트렌드 감지기"""

    async def detect_trends(self, query_logs: List[Dict[str, Any]], granularity: str) -> Dict[str, Any]:
        """트렌드 감지"""
        if not query_logs:
            return {'volume_trend': 'stable', 'emerging_queries': []}
        
        # 시간별 쿼리 볼륨
        time_buckets = defaultdict(int)
        for log in query_logs:
            timestamp = log.get('timestamp', datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            bucket = timestamp.strftime('%Y-%m-%d') if granularity == 'daily' else timestamp.strftime('%Y-%m-%d %H')
            time_buckets[bucket] += 1
        
        # 트렌드 방향 계산
        volumes = list(time_buckets.values())
        if len(volumes) >= 2:
            trend = 'increasing' if volumes[-1] > volumes[0] else 'decreasing' if volumes[-1] < volumes[0] else 'stable'
        else:
            trend = 'stable'
        
        # 새로운 쿼리 감지
        recent_queries = [log['query'] for log in query_logs[-100:]]  # 최근 100개
        emerging = Counter(recent_queries).most_common(5)
        
        return {
            'volume_trend': trend,
            'emerging_queries': emerging,
            'daily_volumes': dict(time_buckets)
        }

class AnomalyDetector:
    """이상 감지기"""

    async def detect(self, query_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """이상 패턴 감지"""
        anomalies = []
        
        if not query_logs:
            return anomalies
        
        # 응답 시간 이상
        response_times = [log.get('response_time_ms', 0) for log in query_logs]
        if response_times:
            mean_time = np.mean(response_times)
            std_time = np.std(response_times)
            threshold = mean_time + 3 * std_time
            
            slow_queries = [log for log in query_logs if log.get('response_time_ms', 0) > threshold]
            if slow_queries:
                anomalies.append({
                    'type': 'slow_response',
                    'count': len(slow_queries),
                    'threshold': threshold
                })
        
        # 제로 결과 급증
        zero_results = sum(1 for log in query_logs if log.get('result_count', 0) == 0)
        zero_rate = zero_results / len(query_logs)
        if zero_rate > 0.3:  # 30% 이상
            anomalies.append({
                'type': 'high_zero_results',
                'rate': zero_rate
            })
        
        return anomalies