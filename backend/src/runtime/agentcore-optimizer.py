import boto3
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import asyncio


class AgentCoreOptimizer:
    """AWS Bedrock AgentCore 런타임 최적화"""

    def __init__(self):
        self.bedrock_client = boto3.client("bedrock-agent-runtime")
        self.cloudwatch = boto3.client("cloudwatch")
        self.application_autoscaling = boto3.client("application-autoscaling")

    async def optimize_runtime(self, runtime_id: str) -> Dict[str, Any]:
        """AgentCore 런타임 최적화"""

        # 현재 성능 메트릭 수집
        metrics = await self.collect_runtime_metrics(runtime_id)

        # 최적화 필요 여부 판단
        optimizations_needed = self.analyze_metrics(metrics)

        if not optimizations_needed:
            return {"status": "optimal", "metrics": metrics}

        # 최적화 실행
        optimization_results = []
        for optimization in optimizations_needed:
            result = await self.apply_optimization(runtime_id, optimization)
            optimization_results.append(result)

        return {
            "status": "optimized",
            "optimizations": optimization_results,
            "metrics": metrics,
        }

    async def collect_runtime_metrics(self, runtime_id: str) -> Dict[str, Any]:
        """런타임 메트릭 수집"""

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)

        # CPU 사용률
        cpu_response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/Bedrock",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "RuntimeId", "Value": runtime_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=["Average", "Maximum"],
        )

        # 메모리 사용률
        memory_response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/Bedrock",
            MetricName="MemoryUtilization",
            Dimensions=[{"Name": "RuntimeId", "Value": runtime_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=["Average", "Maximum"],
        )

        return {
            "cpu_utilization": self._get_latest_metric(cpu_response, "Average"),
            "memory_utilization": self._get_latest_metric(memory_response, "Average"),
            "session_count": await self._get_active_sessions(runtime_id),
            "average_latency": await self._get_average_latency(runtime_id),
            "error_rate": await self._get_error_rate(runtime_id),
        }

    def analyze_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """메트릭 분석 및 최적화 제안"""

        optimizations = []

        # CPU 최적화
        if metrics["cpu_utilization"] > 80:
            optimizations.append(
                {
                    "type": "scale_out",
                    "reason": "High CPU utilization",
                    "current_value": metrics["cpu_utilization"],
                    "target_value": 70,
                }
            )
        elif metrics["cpu_utilization"] < 20:
            optimizations.append(
                {
                    "type": "scale_in",
                    "reason": "Low CPU utilization",
                    "current_value": metrics["cpu_utilization"],
                    "target_value": 40,
                }
            )

        # 메모리 최적화
        if metrics["memory_utilization"] > 85:
            optimizations.append(
                {
                    "type": "increase_memory",
                    "reason": "High memory utilization",
                    "current_value": metrics["memory_utilization"],
                    "recommended_increase": "25%",
                }
            )

        # 레이턴시 최적화
        if metrics["average_latency"] > 500:  # 500ms
            optimizations.append(
                {
                    "type": "optimize_caching",
                    "reason": "High latency detected",
                    "current_value": metrics["average_latency"],
                    "target_latency": 200,
                }
            )

        return optimizations

    async def apply_optimization(
        self, runtime_id: str, optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """최적화 적용"""

        try:
            if optimization["type"] == "scale_out":
                return await self._scale_runtime(runtime_id, "out")
            elif optimization["type"] == "scale_in":
                return await self._scale_runtime(runtime_id, "in")
            elif optimization["type"] == "increase_memory":
                return await self._adjust_memory(runtime_id, optimization)
            elif optimization["type"] == "optimize_caching":
                return await self._optimize_caching(runtime_id)

            return {"status": "unknown_optimization_type"}

        except Exception as e:
            return {"status": "failed", "error": str(e), "optimization": optimization}

    async def _scale_runtime(self, runtime_id: str, direction: str) -> Dict[str, Any]:
        """런타임 스케일링"""

        # 현재 용량 조회
        response = self.application_autoscaling.describe_scalable_targets(
            ServiceNamespace="bedrock", ResourceIds=[f"runtime/{runtime_id}"]
        )

        if not response["ScalableTargets"]:
            return {"status": "no_scaling_target"}

        current_capacity = response["ScalableTargets"][0]["DesiredCapacity"]

        if direction == "out":
            new_capacity = min(current_capacity + 1, 10)  # 최대 10개
        else:
            new_capacity = max(current_capacity - 1, 2)  # 최소 2개

        # 스케일링 실행
        self.application_autoscaling.register_scalable_target(
            ServiceNamespace="bedrock",
            ResourceId=f"runtime/{runtime_id}",
            ScalableDimension="bedrock:runtime:InstanceCount",
            MinCapacity=2,
            MaxCapacity=10,
            DesiredCapacity=new_capacity,
        )

        return {
            "status": "success",
            "action": f"scaled_{direction}",
            "previous_capacity": current_capacity,
            "new_capacity": new_capacity,
        }

    async def _adjust_memory(
        self, runtime_id: str, optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메모리 조정"""

        # 메모리 증가는 런타임 재시작이 필요하므로 권장사항만 반환
        return {
            "status": "recommendation",
            "action": "increase_memory",
            "recommendation": f"Increase memory by {optimization['recommended_increase']}",
            "note": "Memory adjustment requires runtime restart",
        }

    async def _optimize_caching(self, runtime_id: str) -> Dict[str, Any]:
        """캐싱 최적화"""

        # 캐시 설정 최적화 (실제로는 AgentCore 설정 API 호출)
        return {
            "status": "success",
            "action": "cache_optimization",
            "changes": [
                "Enabled L2 cache",
                "Increased cache TTL to 300s",
                "Enabled cache compression",
            ],
        }

    def _get_latest_metric(self, response: Dict[str, Any], statistic: str) -> float:
        """최신 메트릭 값 추출"""

        datapoints = response.get("Datapoints", [])
        if not datapoints:
            return 0.0

        # 최신 데이터포인트 반환
        latest = max(datapoints, key=lambda x: x["Timestamp"])
        return latest.get(statistic, 0.0)

    async def _get_active_sessions(self, runtime_id: str) -> int:
        """활성 세션 수 조회"""
        # 실제로는 AgentCore API 호출
        return 42  # 모의 값

    async def _get_average_latency(self, runtime_id: str) -> float:
        """평균 레이턴시 조회"""
        # 실제로는 CloudWatch 메트릭 조회
        return 150.5  # 모의 값 (ms)

    async def _get_error_rate(self, runtime_id: str) -> float:
        """에러율 조회"""
        # 실제로는 CloudWatch 메트릭 조회
        return 0.02  # 모의 값 (2%)
