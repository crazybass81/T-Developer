"""
T-Developer MVP - System Monitoring

시스템 모니터링 및 로깅
"""

import logging
import asyncio
import psutil
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_connections: int
    response_time_ms: float

@dataclass
class AgentMetrics:
    agent_type: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    last_activity: str

class SystemMonitor:
    """시스템 모니터링"""
    
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.monitoring_active = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('t_developer_monitor')
        logger.setLevel(logging.INFO)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 파일 핸들러
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/system_monitor.log')
        file_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """모니터링 시작"""
        self.monitoring_active = True
        self.logger.info("System monitoring started")
        
        while self.monitoring_active:
            try:
                metrics = await self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # 히스토리 크기 제한 (최근 1000개)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # 경고 조건 확인
                await self.check_alerts(metrics)
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        self.logger.info("System monitoring stopped")
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / 1024 / 1024
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # 네트워크 연결 수
        connections = len(psutil.net_connections())
        
        metrics = SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_usage_percent=disk_usage_percent,
            active_connections=connections,
            response_time_ms=0.0  # 별도로 측정
        )
        
        return metrics
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        if not self.metrics_history:
            return {'status': 'no_data'}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            'current': asdict(latest_metrics),
            'agent_metrics': {
                agent_type: asdict(metrics) 
                for agent_type, metrics in self.agent_metrics.items()
            },
            'health_status': 'healthy'
        }
    
    async def check_alerts(self, metrics: SystemMetrics):
        """경고 조건 확인"""
        if metrics.cpu_percent > 80:
            self.logger.warning(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > 85:
            self.logger.warning(f"High memory usage: {metrics.memory_percent:.1f}%")

# 전역 모니터 인스턴스
system_monitor = SystemMonitor()

def get_monitoring_status():
    """모니터링 상태 조회"""
    return system_monitor.get_system_status()