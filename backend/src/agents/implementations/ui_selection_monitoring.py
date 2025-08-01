"""UI Selection Agent Monitoring and Health Checks"""

import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass
import psutil
import requests

@dataclass
class HealthStatus:
    healthy: bool
    response_time: float
    cpu_usage: float
    memory_usage: float
    error_rate: float
    cache_hit_rate: float

class UISelectionMonitor:
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_failed': 0,
            'response_times': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    async def health_check(self) -> HealthStatus:
        """Comprehensive health check"""
        try:
            # Response time check
            start = time.time()
            response = requests.get('http://localhost:8000/health', timeout=5)
            response_time = time.time() - start
            
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Error rate calculation
            error_rate = (self.metrics['requests_failed'] / 
                         max(self.metrics['requests_total'], 1))
            
            # Cache hit rate
            total_cache_ops = self.metrics['cache_hits'] + self.metrics['cache_misses']
            cache_hit_rate = (self.metrics['cache_hits'] / 
                             max(total_cache_ops, 1))
            
            return HealthStatus(
                healthy=response.status_code == 200 and response_time < 0.3,
                response_time=response_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate
            )
            
        except Exception as e:
            return HealthStatus(
                healthy=False,
                response_time=999.0,
                cpu_usage=0,
                memory_usage=0,
                error_rate=1.0,
                cache_hit_rate=0
            )
    
    def record_request(self, success: bool, response_time: float):
        """Record request metrics"""
        self.metrics['requests_total'] += 1
        if not success:
            self.metrics['requests_failed'] += 1
        self.metrics['response_times'].append(response_time)
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_cache_hit(self, hit: bool):
        """Record cache metrics"""
        if hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        response_times = self.metrics['response_times']
        
        return {
            'requests_total': self.metrics['requests_total'],
            'error_rate': self.metrics['requests_failed'] / max(self.metrics['requests_total'], 1),
            'avg_response_time': sum(response_times) / max(len(response_times), 1),
            'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0,
            'cache_hit_rate': self.metrics['cache_hits'] / max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)
        }

# Global monitor instance
monitor = UISelectionMonitor()