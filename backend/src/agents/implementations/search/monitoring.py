# backend/src/agents/implementations/search/monitoring.py
from typing import Dict, List, Any, Optional
import time
import asyncio
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

@dataclass
class SearchMetrics:
    timestamp: float
    query: str
    response_time_ms: float
    result_count: int
    cache_hit: bool
    error: Optional[str]
    user_id: Optional[str]

@dataclass
class AggregatedMetrics:
    total_queries: int
    avg_response_time: float
    p95_response_time: float
    cache_hit_rate: float
    error_rate: float
    queries_per_second: float

class SearchMonitor:
    """검색 모니터링 시스템"""

    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)
        self.alert_manager = AlertManager()
        self.dashboard_updater = DashboardUpdater()
        
        # 실시간 메트릭
        self.current_metrics = {
            'active_queries': 0,
            'total_queries_today': 0,
            'avg_response_time': 0.0,
            'error_count': 0
        }

    async def record_search(
        self,
        query: str,
        response_time_ms: float,
        result_count: int,
        cache_hit: bool = False,
        error: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """검색 메트릭 기록"""

        metric = SearchMetrics(
            timestamp=time.time(),
            query=query,
            response_time_ms=response_time_ms,
            result_count=result_count,
            cache_hit=cache_hit,
            error=error,
            user_id=user_id
        )

        # 버퍼에 추가
        self.metrics_buffer.append(metric)

        # 실시간 메트릭 업데이트
        await self._update_realtime_metrics(metric)

        # 알림 체크
        await self.alert_manager.check_alerts(metric, self.current_metrics)

        # 대시보드 업데이트 (비동기)
        asyncio.create_task(
            self.dashboard_updater.update_metrics(self.current_metrics)
        )

    async def get_aggregated_metrics(
        self,
        time_window_minutes: int = 60
    ) -> AggregatedMetrics:
        """집계된 메트릭 반환"""

        cutoff_time = time.time() - (time_window_minutes * 60)
        recent_metrics = [
            m for m in self.metrics_buffer 
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return AggregatedMetrics(0, 0, 0, 0, 0, 0)

        # 집계 계산
        total_queries = len(recent_metrics)
        response_times = [m.response_time_ms for m in recent_metrics]
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        errors = sum(1 for m in recent_metrics if m.error)

        return AggregatedMetrics(
            total_queries=total_queries,
            avg_response_time=sum(response_times) / len(response_times),
            p95_response_time=self._percentile(response_times, 95),
            cache_hit_rate=cache_hits / total_queries,
            error_rate=errors / total_queries,
            queries_per_second=total_queries / (time_window_minutes * 60)
        )

    async def _update_realtime_metrics(self, metric: SearchMetrics) -> None:
        """실시간 메트릭 업데이트"""

        self.current_metrics['total_queries_today'] += 1

        # 이동 평균으로 응답 시간 업데이트
        current_avg = self.current_metrics['avg_response_time']
        total_queries = self.current_metrics['total_queries_today']
        
        self.current_metrics['avg_response_time'] = (
            (current_avg * (total_queries - 1) + metric.response_time_ms) / total_queries
        )

        if metric.error:
            self.current_metrics['error_count'] += 1

    def _percentile(self, values: List[float], percentile: int) -> float:
        """백분위수 계산"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

class AlertManager:
    """알림 관리자"""

    def __init__(self):
        self.alert_rules = [
            {
                'name': 'high_response_time',
                'condition': lambda m, cm: m.response_time_ms > 1000,
                'severity': 'warning',
                'cooldown': 300  # 5분
            },
            {
                'name': 'high_error_rate',
                'condition': lambda m, cm: cm['error_count'] / max(cm['total_queries_today'], 1) > 0.05,
                'severity': 'critical',
                'cooldown': 600  # 10분
            },
            {
                'name': 'low_cache_hit_rate',
                'condition': lambda m, cm: self._calculate_recent_cache_rate() < 0.5,
                'severity': 'warning',
                'cooldown': 900  # 15분
            }
        ]
        
        self.last_alert_times = {}

    async def check_alerts(
        self,
        metric: SearchMetrics,
        current_metrics: Dict[str, Any]
    ) -> None:
        """알림 조건 체크"""

        for rule in self.alert_rules:
            rule_name = rule['name']
            
            # 쿨다운 체크
            if rule_name in self.last_alert_times:
                if time.time() - self.last_alert_times[rule_name] < rule['cooldown']:
                    continue

            # 조건 체크
            if rule['condition'](metric, current_metrics):
                await self._send_alert(rule, metric, current_metrics)
                self.last_alert_times[rule_name] = time.time()

    async def _send_alert(
        self,
        rule: Dict[str, Any],
        metric: SearchMetrics,
        current_metrics: Dict[str, Any]
    ) -> None:
        """알림 전송"""

        alert_data = {
            'rule_name': rule['name'],
            'severity': rule['severity'],
            'timestamp': time.time(),
            'metric': asdict(metric),
            'current_metrics': current_metrics,
            'message': self._generate_alert_message(rule, metric, current_metrics)
        }

        # 실제 구현에서는 Slack, Email, SMS 등으로 전송
        print(f"ALERT: {alert_data['message']}")

    def _generate_alert_message(
        self,
        rule: Dict[str, Any],
        metric: SearchMetrics,
        current_metrics: Dict[str, Any]
    ) -> str:
        """알림 메시지 생성"""

        if rule['name'] == 'high_response_time':
            return f"High response time detected: {metric.response_time_ms}ms for query '{metric.query}'"
        elif rule['name'] == 'high_error_rate':
            error_rate = current_metrics['error_count'] / max(current_metrics['total_queries_today'], 1)
            return f"High error rate detected: {error_rate:.2%}"
        elif rule['name'] == 'low_cache_hit_rate':
            cache_rate = self._calculate_recent_cache_rate()
            return f"Low cache hit rate detected: {cache_rate:.2%}"
        
        return f"Alert triggered for rule: {rule['name']}"

class DashboardUpdater:
    """대시보드 업데이터"""

    def __init__(self):
        self.websocket_connections = set()
        self.update_interval = 5  # 5초마다 업데이트

    async def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """대시보드 메트릭 업데이트"""

        dashboard_data = {
            'timestamp': time.time(),
            'metrics': metrics,
            'charts': await self._generate_chart_data()
        }

        # WebSocket으로 실시간 업데이트 전송
        await self._broadcast_to_dashboard(dashboard_data)

    async def _generate_chart_data(self) -> Dict[str, Any]:
        """차트 데이터 생성"""

        # 시간별 쿼리 수
        hourly_queries = defaultdict(int)
        
        # 응답 시간 히스토그램
        response_time_buckets = defaultdict(int)
        
        # 인기 쿼리 TOP 10
        query_frequency = defaultdict(int)

        # 실제 구현에서는 메트릭 버퍼에서 데이터 추출
        return {
            'hourly_queries': dict(hourly_queries),
            'response_time_histogram': dict(response_time_buckets),
            'top_queries': dict(query_frequency)
        }

    async def _broadcast_to_dashboard(self, data: Dict[str, Any]) -> None:
        """대시보드로 데이터 브로드캐스트"""

        if not self.websocket_connections:
            return

        message = json.dumps(data)
        
        # 모든 WebSocket 연결에 전송
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send(message)
            except Exception:
                disconnected.add(ws)

        # 끊어진 연결 제거
        self.websocket_connections -= disconnected

class PerformanceProfiler:
    """성능 프로파일러"""

    def __init__(self):
        self.profiling_enabled = False
        self.profile_data = defaultdict(list)

    async def profile_search_operation(
        self,
        operation_name: str,
        func,
        *args,
        **kwargs
    ):
        """검색 작업 프로파일링"""

        if not self.profiling_enabled:
            return await func(*args, **kwargs)

        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        try:
            result = await func(*args, **kwargs)
            
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            # 프로파일 데이터 기록
            self.profile_data[operation_name].append({
                'timestamp': time.time(),
                'duration_ms': (end_time - start_time) * 1000,
                'memory_delta_mb': (end_memory - start_memory) / 1024 / 1024,
                'success': True
            })

            return result

        except Exception as e:
            end_time = time.perf_counter()
            
            self.profile_data[operation_name].append({
                'timestamp': time.time(),
                'duration_ms': (end_time - start_time) * 1000,
                'memory_delta_mb': 0,
                'success': False,
                'error': str(e)
            })
            
            raise

    def _get_memory_usage(self) -> int:
        """현재 메모리 사용량 반환 (bytes)"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except:
            return 0

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서 생성"""

        report = {}
        
        for operation, data_points in self.profile_data.items():
            if not data_points:
                continue

            durations = [dp['duration_ms'] for dp in data_points if dp['success']]
            memory_deltas = [dp['memory_delta_mb'] for dp in data_points if dp['success']]
            
            success_rate = sum(1 for dp in data_points if dp['success']) / len(data_points)

            report[operation] = {
                'total_calls': len(data_points),
                'success_rate': success_rate,
                'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
                'p95_duration_ms': self._percentile(durations, 95) if durations else 0,
                'avg_memory_delta_mb': sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0
            }

        return report

    def _percentile(self, values: List[float], percentile: int) -> float:
        """백분위수 계산"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]