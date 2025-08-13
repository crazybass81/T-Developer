"""
Endpoint Monitoring System
Real-time monitoring of agent endpoints
"""
import asyncio
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3


@dataclass
class EndpointMetrics:
    endpoint_id: str
    timestamp: float
    response_time_ms: float
    status_code: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class EndpointHealth:
    endpoint_id: str
    is_healthy: bool
    uptime_percentage: float
    avg_response_time_ms: float
    total_requests: int
    failed_requests: int
    last_check: float


class EndpointMonitor:
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.metrics: Dict[str, List[EndpointMetrics]] = {}
        self.health_status: Dict[str, EndpointHealth] = {}
        self.cloudwatch_client = boto3.client("cloudwatch", region_name="us-east-1")
        self.running = False
        self.monitor_task = None

    async def start_monitoring(self, registry):
        """Start continuous monitoring"""
        self.running = True
        self.registry = registry
        self.monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_task:
            await self.monitor_task

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._check_all_endpoints()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(10)

    async def _check_all_endpoints(self):
        """Check all registered endpoints"""
        endpoints = self.registry.get_active_endpoints()
        tasks = [self._check_endpoint(ep) for ep in endpoints]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_endpoint(self, endpoint):
        """Check single endpoint health"""
        start_time = time.time()

        try:
            # Simulate endpoint check (replace with actual HTTP call)
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=endpoint.method,
                    url=endpoint.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    metric = EndpointMetrics(
                        endpoint_id=endpoint.id,
                        timestamp=time.time(),
                        response_time_ms=response_time,
                        status_code=response.status,
                        success=response.status == 200,
                        error_message=None if response.status == 200 else f"HTTP {response.status}",
                    )

        except asyncio.TimeoutError:
            metric = EndpointMetrics(
                endpoint_id=endpoint.id,
                timestamp=time.time(),
                response_time_ms=(time.time() - start_time) * 1000,
                status_code=0,
                success=False,
                error_message="Timeout",
            )
        except Exception as e:
            metric = EndpointMetrics(
                endpoint_id=endpoint.id,
                timestamp=time.time(),
                response_time_ms=(time.time() - start_time) * 1000,
                status_code=0,
                success=False,
                error_message=str(e),
            )

        # Store metric
        if endpoint.id not in self.metrics:
            self.metrics[endpoint.id] = []
        self.metrics[endpoint.id].append(metric)

        # Keep only last 1000 metrics per endpoint
        if len(self.metrics[endpoint.id]) > 1000:
            self.metrics[endpoint.id] = self.metrics[endpoint.id][-1000:]

        # Update health status
        self._update_health_status(endpoint.id)

        # Send to CloudWatch
        await self._send_to_cloudwatch(metric, endpoint)

    def _update_health_status(self, endpoint_id: str):
        """Update endpoint health status"""
        if endpoint_id not in self.metrics:
            return

        metrics = self.metrics[endpoint_id]
        if not metrics:
            return

        # Calculate health metrics
        total = len(metrics)
        successful = sum(1 for m in metrics if m.success)
        failed = total - successful
        uptime_pct = (successful / total * 100) if total > 0 else 0

        # Calculate average response time
        success_metrics = [m for m in metrics if m.success]
        avg_response = (
            sum(m.response_time_ms for m in success_metrics) / len(success_metrics)
            if success_metrics
            else 0
        )

        # Determine if healthy (>95% uptime and <1000ms avg response)
        is_healthy = uptime_pct >= 95 and avg_response < 1000

        self.health_status[endpoint_id] = EndpointHealth(
            endpoint_id=endpoint_id,
            is_healthy=is_healthy,
            uptime_percentage=uptime_pct,
            avg_response_time_ms=avg_response,
            total_requests=total,
            failed_requests=failed,
            last_check=time.time(),
        )

    async def _send_to_cloudwatch(self, metric: EndpointMetrics, endpoint):
        """Send metrics to CloudWatch"""
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace="T-Developer/Endpoints",
                MetricData=[
                    {
                        "MetricName": "ResponseTime",
                        "Value": metric.response_time_ms,
                        "Unit": "Milliseconds",
                        "Timestamp": datetime.fromtimestamp(metric.timestamp),
                        "Dimensions": [
                            {"Name": "AgentName", "Value": endpoint.agent_name},
                            {"Name": "Version", "Value": endpoint.version},
                        ],
                    },
                    {
                        "MetricName": "HealthCheck",
                        "Value": 1 if metric.success else 0,
                        "Unit": "None",
                        "Timestamp": datetime.fromtimestamp(metric.timestamp),
                        "Dimensions": [
                            {"Name": "AgentName", "Value": endpoint.agent_name},
                            {"Name": "Version", "Value": endpoint.version},
                        ],
                    },
                ],
            )
        except Exception as e:
            print(f"CloudWatch error: {e}")

    def get_endpoint_health(self, endpoint_id: str) -> Optional[EndpointHealth]:
        """Get health status for endpoint"""
        return self.health_status.get(endpoint_id)

    def get_unhealthy_endpoints(self) -> List[str]:
        """Get list of unhealthy endpoints"""
        return [ep_id for ep_id, health in self.health_status.items() if not health.is_healthy]

    def get_metrics_summary(self, endpoint_id: str, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for endpoint"""
        if endpoint_id not in self.metrics:
            return {}

        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [m for m in self.metrics[endpoint_id] if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return {}

        successful = [m for m in recent_metrics if m.success]
        failed = [m for m in recent_metrics if not m.success]

        return {
            "endpoint_id": endpoint_id,
            "period_hours": hours,
            "total_requests": len(recent_metrics),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "uptime_percentage": (len(successful) / len(recent_metrics) * 100)
            if recent_metrics
            else 0,
            "avg_response_time_ms": (
                sum(m.response_time_ms for m in successful) / len(successful) if successful else 0
            ),
            "min_response_time_ms": min((m.response_time_ms for m in successful), default=0),
            "max_response_time_ms": max((m.response_time_ms for m in successful), default=0),
            "error_types": self._count_errors(failed),
        }

    def _count_errors(self, failed_metrics: List[EndpointMetrics]) -> Dict[str, int]:
        """Count error types"""
        errors = {}
        for metric in failed_metrics:
            error_type = metric.error_message or "Unknown"
            errors[error_type] = errors.get(error_type, 0) + 1
        return errors

    def generate_alert(self, endpoint_id: str) -> Optional[Dict[str, Any]]:
        """Generate alert if endpoint is unhealthy"""
        health = self.get_endpoint_health(endpoint_id)
        if not health or health.is_healthy:
            return None

        return {
            "alert_type": "endpoint_unhealthy",
            "endpoint_id": endpoint_id,
            "timestamp": time.time(),
            "details": {
                "uptime_percentage": health.uptime_percentage,
                "avg_response_time_ms": health.avg_response_time_ms,
                "failed_requests": health.failed_requests,
                "total_requests": health.total_requests,
            },
            "severity": "high" if health.uptime_percentage < 50 else "medium",
            "message": f"Endpoint {endpoint_id} is unhealthy: {health.uptime_percentage:.1f}% uptime",
        }


# Example usage
if __name__ == "__main__":

    async def test_monitor():
        from endpoint_registry import EndpointRegistry, EndpointStatus

        # Create registry and add endpoints
        registry = EndpointRegistry()
        ep_id = registry.register_endpoint(
            agent_name="test_agent", version="1.0.0", url="https://api.example.com/agent"
        )
        registry.update_status(ep_id, EndpointStatus.ACTIVE)

        # Create and start monitor
        monitor = EndpointMonitor(check_interval=30)
        await monitor.start_monitoring(registry)

        # Run for a bit
        await asyncio.sleep(35)

        # Get health status
        health = monitor.get_endpoint_health(ep_id)
        if health:
            print(f"Health: {health}")

        # Get metrics summary
        summary = monitor.get_metrics_summary(ep_id)
        print(f"Summary: {json.dumps(summary, indent=2)}")

        # Stop monitoring
        await monitor.stop_monitoring()

    asyncio.run(test_monitor())
