#!/usr/bin/env python3
"""
Performance Monitoring Dashboard
T-Developer MVP의 성능 모니터링 및 메트릭 수집
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import logging
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """시스템 메트릭"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_free_gb: float
    load_average: List[float]
    
    
@dataclass
class ProcessMetrics:
    """프로세스 메트릭"""
    timestamp: str
    process_name: str
    pid: int
    cpu_percent: float
    memory_percent: float
    memory_rss_mb: float
    threads_count: int
    open_files_count: int
    connections_count: int


@dataclass
class AgentMetrics:
    """Agent 성능 메트릭"""
    agent_name: str
    execution_count: int
    total_execution_time: float
    average_execution_time: float
    success_count: int
    error_count: int
    success_rate: float
    last_execution_time: float
    last_execution_status: str
    last_updated: str


@dataclass
class PipelineMetrics:
    """Pipeline 메트릭"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_pipeline_time: float
    total_pipeline_time: float
    success_rate: float
    throughput_per_minute: float
    last_execution_time: str


class MetricsCollector:
    """메트릭 수집기"""
    
    def __init__(self, collection_interval: int = 30):
        self.collection_interval = collection_interval
        self.system_metrics_history = deque(maxlen=1000)
        self.process_metrics_history = deque(maxlen=1000)
        self.agent_metrics = {}
        self.pipeline_metrics = PipelineMetrics(
            total_executions=0,
            successful_executions=0,
            failed_executions=0,
            average_pipeline_time=0,
            total_pipeline_time=0,
            success_rate=0,
            throughput_per_minute=0,
            last_execution_time=""
        )
        
        self.is_collecting = False
        self.collection_thread = None
        
        # Agent 실행 통계
        self.agent_stats = defaultdict(lambda: {
            'execution_times': deque(maxlen=100),
            'success_count': 0,
            'error_count': 0,
            'last_execution': None
        })
        
        # Pipeline 실행 기록
        self.pipeline_executions = deque(maxlen=1000)
    
    def start_collecting(self):
        """메트릭 수집 시작"""
        if not self.is_collecting:
            self.is_collecting = True
            self.collection_thread = threading.Thread(target=self._collect_metrics_loop)
            self.collection_thread.daemon = True
            self.collection_thread.start()
            logger.info("Metrics collection started")
    
    def stop_collecting(self):
        """메트릭 수집 중지"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """메트릭 수집 루프"""
        while self.is_collecting:
            try:
                # 시스템 메트릭 수집
                self._collect_system_metrics()
                
                # 프로세스 메트릭 수집
                self._collect_process_metrics()
                
                # Agent 메트릭 업데이트
                self._update_agent_metrics()
                
                # Pipeline 메트릭 업데이트
                self._update_pipeline_metrics()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                time.sleep(5)  # 에러 시 짧은 대기
    
    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # 디스크 정보
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            # 로드 평균
            try:
                load_average = list(psutil.getloadavg())
            except AttributeError:
                load_average = [0.0, 0.0, 0.0]  # Windows에서는 getloadavg가 없음
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_used_gb=disk_used_gb,
                disk_free_gb=disk_free_gb,
                load_average=load_average
            )
            
            self.system_metrics_history.append(metrics)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_process_metrics(self):
        """프로세스 메트릭 수집"""
        try:
            # 현재 프로세스 정보
            current_process = psutil.Process()
            
            # 프로세스 메트릭 수집
            with current_process.oneshot():
                cpu_percent = current_process.cpu_percent()
                memory_info = current_process.memory_info()
                memory_percent = current_process.memory_percent()
                
                try:
                    threads_count = current_process.num_threads()
                    open_files_count = len(current_process.open_files())
                    connections_count = len(current_process.connections())
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    threads_count = 0
                    open_files_count = 0
                    connections_count = 0
                
                metrics = ProcessMetrics(
                    timestamp=datetime.now().isoformat(),
                    process_name=current_process.name(),
                    pid=current_process.pid,
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    memory_rss_mb=memory_info.rss / (1024 * 1024),
                    threads_count=threads_count,
                    open_files_count=open_files_count,
                    connections_count=connections_count
                )
                
                self.process_metrics_history.append(metrics)
                
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
    
    def record_agent_execution(self, agent_name: str, execution_time: float, success: bool):
        """Agent 실행 기록"""
        stats = self.agent_stats[agent_name]
        stats['execution_times'].append(execution_time)
        stats['last_execution'] = datetime.now()
        
        if success:
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
    
    def record_pipeline_execution(self, execution_time: float, success: bool, details: Dict[str, Any] = None):
        """Pipeline 실행 기록"""
        execution_record = {
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'success': success,
            'details': details or {}
        }
        
        self.pipeline_executions.append(execution_record)
    
    def _update_agent_metrics(self):
        """Agent 메트릭 업데이트"""
        self.agent_metrics = {}
        
        for agent_name, stats in self.agent_stats.items():
            execution_times = list(stats['execution_times'])
            total_executions = len(execution_times)
            
            if total_executions > 0:
                total_time = sum(execution_times)
                average_time = total_time / total_executions
                last_execution_time = execution_times[-1]
                
                success_count = stats['success_count']
                error_count = stats['error_count']
                total_count = success_count + error_count
                success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
                
                self.agent_metrics[agent_name] = AgentMetrics(
                    agent_name=agent_name,
                    execution_count=total_executions,
                    total_execution_time=total_time,
                    average_execution_time=average_time,
                    success_count=success_count,
                    error_count=error_count,
                    success_rate=success_rate,
                    last_execution_time=last_execution_time,
                    last_execution_status="success" if success_count > error_count else "error",
                    last_updated=datetime.now().isoformat()
                )
    
    def _update_pipeline_metrics(self):
        """Pipeline 메트릭 업데이트"""
        if not self.pipeline_executions:
            return
        
        executions = list(self.pipeline_executions)
        total_executions = len(executions)
        successful_executions = sum(1 for e in executions if e['success'])
        failed_executions = total_executions - successful_executions
        
        total_time = sum(e['execution_time'] for e in executions)
        average_time = total_time / total_executions if total_executions > 0 else 0
        success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
        
        # 최근 1분간의 처리량 계산
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        recent_executions = [
            e for e in executions 
            if datetime.fromisoformat(e['timestamp']) > one_minute_ago
        ]
        throughput_per_minute = len(recent_executions)
        
        last_execution_time = executions[-1]['timestamp'] if executions else ""
        
        self.pipeline_metrics = PipelineMetrics(
            total_executions=total_executions,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            average_pipeline_time=average_time,
            total_pipeline_time=total_time,
            success_rate=success_rate,
            throughput_per_minute=throughput_per_minute,
            last_execution_time=last_execution_time
        )
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """현재 메트릭 조회"""
        return {
            "system": asdict(self.system_metrics_history[-1]) if self.system_metrics_history else None,
            "process": asdict(self.process_metrics_history[-1]) if self.process_metrics_history else None,
            "agents": {name: asdict(metrics) for name, metrics in self.agent_metrics.items()},
            "pipeline": asdict(self.pipeline_metrics),
            "collection_status": {
                "is_collecting": self.is_collecting,
                "last_updated": datetime.now().isoformat(),
                "metrics_count": {
                    "system": len(self.system_metrics_history),
                    "process": len(self.process_metrics_history),
                    "pipeline_executions": len(self.pipeline_executions)
                }
            }
        }
    
    def get_metrics_history(self, metric_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """메트릭 히스토리 조회"""
        if metric_type == "system":
            history = list(self.system_metrics_history)[-limit:]
            return [asdict(m) for m in history]
        elif metric_type == "process":
            history = list(self.process_metrics_history)[-limit:]
            return [asdict(m) for m in history]
        elif metric_type == "pipeline":
            return list(self.pipeline_executions)[-limit:]
        else:
            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 조회"""
        current_metrics = self.get_current_metrics()
        
        # 시스템 상태 평가
        system_status = "healthy"
        warnings = []
        
        if current_metrics["system"]:
            sys_metrics = current_metrics["system"]
            
            if sys_metrics["cpu_percent"] > 80:
                system_status = "warning"
                warnings.append("High CPU usage")
            
            if sys_metrics["memory_percent"] > 85:
                system_status = "warning"
                warnings.append("High memory usage")
            
            if sys_metrics["disk_usage_percent"] > 90:
                system_status = "critical"
                warnings.append("Low disk space")
        
        # Agent 성능 요약
        agent_summary = {}
        for agent_name, metrics in current_metrics["agents"].items():
            agent_summary[agent_name] = {
                "status": "healthy" if metrics["success_rate"] > 95 else "warning",
                "avg_execution_time": metrics["average_execution_time"],
                "success_rate": metrics["success_rate"]
            }
        
        return {
            "system_status": system_status,
            "warnings": warnings,
            "pipeline_success_rate": current_metrics["pipeline"]["success_rate"],
            "pipeline_throughput": current_metrics["pipeline"]["throughput_per_minute"],
            "agent_summary": agent_summary,
            "uptime": self._get_uptime(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_uptime(self) -> str:
        """시스템 업타임 조회"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_days = uptime_seconds // (24 * 3600)
            uptime_hours = (uptime_seconds % (24 * 3600)) // 3600
            uptime_minutes = (uptime_seconds % 3600) // 60
            
            return f"{int(uptime_days)}d {int(uptime_hours)}h {int(uptime_minutes)}m"
        except:
            return "Unknown"
    
    def export_metrics(self, filepath: str):
        """메트릭을 파일로 내보내기"""
        try:
            metrics_data = self.get_current_metrics()
            
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
            logger.info(f"Metrics exported to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")


# 글로벌 메트릭 수집기
metrics_collector = MetricsCollector()


class PerformanceDashboard:
    """성능 대시보드 API"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드 데이터 조회"""
        return {
            "current_metrics": self.collector.get_current_metrics(),
            "performance_summary": self.collector.get_performance_summary(),
            "system_history": self.collector.get_metrics_history("system", 50),
            "pipeline_history": self.collector.get_metrics_history("pipeline", 50)
        }
    
    async def get_agent_details(self, agent_name: str) -> Dict[str, Any]:
        """특정 Agent 상세 정보"""
        current_metrics = self.collector.get_current_metrics()
        agent_metrics = current_metrics["agents"].get(agent_name)
        
        if not agent_metrics:
            return {"error": f"Agent '{agent_name}' not found"}
        
        # Agent 실행 히스토리
        agent_stats = self.collector.agent_stats.get(agent_name, {})
        execution_times = list(agent_stats.get('execution_times', []))
        
        return {
            "agent_name": agent_name,
            "metrics": agent_metrics,
            "execution_history": execution_times[-20:],  # 최근 20개
            "performance_trend": self._calculate_performance_trend(execution_times)
        }
    
    def _calculate_performance_trend(self, execution_times: List[float]) -> str:
        """성능 트렌드 계산"""
        if len(execution_times) < 10:
            return "insufficient_data"
        
        # 최근 절반과 이전 절반 비교
        mid_point = len(execution_times) // 2
        recent_avg = sum(execution_times[mid_point:]) / (len(execution_times) - mid_point)
        previous_avg = sum(execution_times[:mid_point]) / mid_point
        
        if recent_avg < previous_avg * 0.9:
            return "improving"
        elif recent_avg > previous_avg * 1.1:
            return "degrading"
        else:
            return "stable"


# 글로벌 대시보드 인스턴스
dashboard = PerformanceDashboard(metrics_collector)


def initialize_monitoring():
    """모니터링 시스템 초기화"""
    try:
        metrics_collector.start_collecting()
        logger.info("Performance monitoring initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")
        return False


def shutdown_monitoring():
    """모니터링 시스템 종료"""
    try:
        metrics_collector.stop_collecting()
        logger.info("Performance monitoring shutdown")
    except Exception as e:
        logger.error(f"Error during monitoring shutdown: {e}")


if __name__ == "__main__":
    # 테스트 실행
    initialize_monitoring()
    
    print("Monitoring system started. Collecting metrics for 10 seconds...")
    time.sleep(10)
    
    # 테스트 데이터
    metrics_collector.record_agent_execution("test_agent", 1.5, True)
    metrics_collector.record_agent_execution("test_agent", 2.1, True)
    metrics_collector.record_agent_execution("test_agent", 0.8, False)
    
    metrics_collector.record_pipeline_execution(15.2, True, {"agents_used": 9})
    
    # 메트릭 조회
    current = metrics_collector.get_current_metrics()
    print("\nCurrent Metrics:")
    print(json.dumps(current, indent=2, default=str))
    
    summary = metrics_collector.get_performance_summary()
    print("\nPerformance Summary:")
    print(json.dumps(summary, indent=2, default=str))
    
    shutdown_monitoring()