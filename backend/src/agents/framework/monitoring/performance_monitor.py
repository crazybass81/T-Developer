# backend/src/agents/framework/performance_monitor.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import statistics
from collections import deque

@dataclass
class PerformanceMetric:
    name: str
    value: float
    timestamp: datetime
    agent_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentPerformanceStats:
    agent_id: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    error_rate: float = 0.0
    throughput: float = 0.0  # executions per second

class PerformanceMonitor:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = {}
        self.agent_stats: Dict[str, AgentPerformanceStats] = {}
        self.execution_times: Dict[str, deque] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_execution(self, agent_id: str, execution_id: str):
        """Mark the start of an execution"""
        self.start_times[execution_id] = time.time()
    
    def end_execution(self, agent_id: str, execution_id: str, success: bool = True, metadata: Dict[str, Any] = None):
        """Mark the end of an execution and record metrics"""
        if execution_id not in self.start_times:
            return
        
        execution_time = time.time() - self.start_times[execution_id]
        del self.start_times[execution_id]
        
        # Update agent stats
        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = AgentPerformanceStats(agent_id=agent_id)
        
        stats = self.agent_stats[agent_id]
        stats.total_executions += 1
        stats.last_execution = datetime.utcnow()
        
        if success:
            stats.successful_executions += 1
        else:
            stats.failed_executions += 1
        
        # Update execution time stats
        if agent_id not in self.execution_times:
            self.execution_times[agent_id] = deque(maxlen=self.max_history)
        
        self.execution_times[agent_id].append(execution_time)
        
        # Calculate statistics
        times = list(self.execution_times[agent_id])
        stats.avg_execution_time = statistics.mean(times)
        stats.min_execution_time = min(times)
        stats.max_execution_time = max(times)
        stats.error_rate = stats.failed_executions / stats.total_executions
        
        # Calculate throughput (executions per second over last minute)
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_executions = sum(1 for t in times if t > one_minute_ago.timestamp())
        stats.throughput = recent_executions / 60.0
        
        # Record metric
        self.record_metric(
            name="execution_time",
            value=execution_time,
            agent_id=agent_id,
            metadata=metadata or {}
        )
    
    def record_metric(self, name: str, value: float, agent_id: str, metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            metadata=metadata or {}
        )
        
        metric_key = f"{agent_id}:{name}"
        if metric_key not in self.metrics:
            self.metrics[metric_key] = deque(maxlen=self.max_history)
        
        self.metrics[metric_key].append(metric)
    
    def get_agent_stats(self, agent_id: str) -> Optional[AgentPerformanceStats]:
        """Get performance statistics for an agent"""
        return self.agent_stats.get(agent_id)
    
    def get_all_agent_stats(self) -> Dict[str, AgentPerformanceStats]:
        """Get performance statistics for all agents"""
        return self.agent_stats.copy()
    
    def get_metric_history(self, agent_id: str, metric_name: str, limit: int = 100) -> List[PerformanceMetric]:
        """Get metric history for an agent"""
        metric_key = f"{agent_id}:{metric_name}"
        metrics = self.metrics.get(metric_key, deque())
        return list(metrics)[-limit:]
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide performance overview"""
        if not self.agent_stats:
            return {"total_agents": 0}
        
        all_stats = list(self.agent_stats.values())
        
        total_executions = sum(s.total_executions for s in all_stats)
        total_successful = sum(s.successful_executions for s in all_stats)
        total_failed = sum(s.failed_executions for s in all_stats)
        
        avg_execution_times = [s.avg_execution_time for s in all_stats if s.avg_execution_time > 0]
        avg_error_rates = [s.error_rate for s in all_stats]
        
        return {
            "total_agents": len(all_stats),
            "total_executions": total_executions,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate": total_successful / total_executions if total_executions > 0 else 0,
            "avg_execution_time": statistics.mean(avg_execution_times) if avg_execution_times else 0,
            "avg_error_rate": statistics.mean(avg_error_rates) if avg_error_rates else 0,
            "total_throughput": sum(s.throughput for s in all_stats)
        }
    
    def get_top_performers(self, metric: str = "throughput", limit: int = 10) -> List[AgentPerformanceStats]:
        """Get top performing agents by metric"""
        all_stats = list(self.agent_stats.values())
        
        if metric == "throughput":
            sorted_stats = sorted(all_stats, key=lambda s: s.throughput, reverse=True)
        elif metric == "success_rate":
            sorted_stats = sorted(all_stats, key=lambda s: 1 - s.error_rate, reverse=True)
        elif metric == "avg_execution_time":
            sorted_stats = sorted(all_stats, key=lambda s: s.avg_execution_time)
        else:
            return []
        
        return sorted_stats[:limit]
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts for agents that need attention"""
        alerts = []
        
        for agent_id, stats in self.agent_stats.items():
            # High error rate alert
            if stats.error_rate > 0.1:  # 10% error rate
                alerts.append({
                    "type": "high_error_rate",
                    "agent_id": agent_id,
                    "error_rate": stats.error_rate,
                    "severity": "high" if stats.error_rate > 0.2 else "medium"
                })
            
            # Slow execution alert
            if stats.avg_execution_time > 10.0:  # 10 seconds
                alerts.append({
                    "type": "slow_execution",
                    "agent_id": agent_id,
                    "avg_execution_time": stats.avg_execution_time,
                    "severity": "high" if stats.avg_execution_time > 30.0 else "medium"
                })
            
            # Low throughput alert
            if stats.throughput < 0.1 and stats.total_executions > 10:  # Less than 1 execution per 10 seconds
                alerts.append({
                    "type": "low_throughput",
                    "agent_id": agent_id,
                    "throughput": stats.throughput,
                    "severity": "medium"
                })
            
            # Stale agent alert
            if stats.last_execution:
                time_since_last = datetime.utcnow() - stats.last_execution
                if time_since_last > timedelta(hours=1):
                    alerts.append({
                        "type": "stale_agent",
                        "agent_id": agent_id,
                        "last_execution": stats.last_execution,
                        "severity": "low"
                    })
        
        return alerts
    
    def reset_agent_stats(self, agent_id: str):
        """Reset statistics for an agent"""
        if agent_id in self.agent_stats:
            del self.agent_stats[agent_id]
        
        if agent_id in self.execution_times:
            del self.execution_times[agent_id]
        
        # Remove metrics
        keys_to_remove = [k for k in self.metrics.keys() if k.startswith(f"{agent_id}:")]
        for key in keys_to_remove:
            del self.metrics[key]
    
    def cleanup_old_metrics(self, days: int = 7):
        """Remove metrics older than specified days"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        for metric_key, metric_deque in self.metrics.items():
            # Filter out old metrics
            filtered_metrics = deque(
                [m for m in metric_deque if m.timestamp > cutoff_time],
                maxlen=self.max_history
            )
            self.metrics[metric_key] = filtered_metrics