"""
Evolution System Monitor
Day 5: TDD Implementation - GREEN Phase
Generated: 2024-11-18

Implements monitoring for Evolution System with strict constraints:
- Agent instantiation: < 3μs
- Agent memory: < 6.5KB
- AI autonomy: 85%
"""

import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import boto3
from aws_xray_sdk import core as xray_core

logger = logging.getLogger(__name__)


@dataclass
class MonitorConfig:
    """Monitor configuration"""

    environment: str = "development"
    region: str = "us-east-1"
    namespace: str = "T-Developer/Evolution"

    # Constraints
    max_instantiation_us: float = 3.0
    max_memory_kb: float = 6.5
    min_ai_autonomy: float = 0.85

    # Alert thresholds
    error_rate_threshold: float = 0.1
    safety_violation_threshold: int = 0


class EvolutionMonitor:
    """Monitor for Evolution System metrics and constraints"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize monitor with configuration"""
        if config:
            self.config = MonitorConfig(**config)
        else:
            self.config = MonitorConfig()

        self.environment = self.config.environment
        self.region = self.config.region
        self.namespace = self.config.namespace

        # Initialize AWS clients
        self._init_aws_clients()

        # Metrics storage
        self.metrics = {
            "instantiation": [],
            "memory": [],
            "evolution_cycles": [],
            "safety_checks": [],
            "operations": [],
        }

        # Alert thresholds
        self.alert_thresholds = {
            "error_rate": self.config.error_rate_threshold,
            "safety_violations": self.config.safety_violation_threshold,
        }

        self._connected = True

    def _init_aws_clients(self):
        """Initialize AWS service clients"""
        try:
            self.cloudwatch = boto3.client("cloudwatch", region_name=self.region)
            self.sns = boto3.client("sns", region_name=self.region)
            self.logs = boto3.client("logs", region_name=self.region)
        except Exception as e:
            logger.warning(f"AWS clients initialization failed: {e}")
            self.cloudwatch = None
            self.sns = None
            self.logs = None

    def is_connected(self) -> bool:
        """Check if monitor is connected"""
        return self._connected

    def track_instantiation(self, agent_id: str, time_us: float) -> Dict:
        """Track agent instantiation time"""
        result = {
            "agent_id": agent_id,
            "time_us": time_us,
            "threshold_us": self.config.max_instantiation_us,
            "constraint_met": time_us <= self.config.max_instantiation_us,
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Check for violation
        if not result["constraint_met"]:
            result["alert_triggered"] = True
            self._trigger_alert(
                "instantiation_violation",
                {
                    "agent_id": agent_id,
                    "time_us": time_us,
                    "threshold_us": self.config.max_instantiation_us,
                },
            )
        else:
            result["alert_triggered"] = False

        # Store metric
        self.metrics["instantiation"].append(result)

        # Send to CloudWatch
        self._send_metric(
            "InstantiationTime",
            time_us,
            "Microseconds",
            {"AgentId": agent_id, "ConstraintMet": str(result["constraint_met"])},
        )

        return result

    def track_memory(self, agent_id: str, memory_kb: float) -> Dict:
        """Track agent memory usage"""
        result = {
            "agent_id": agent_id,
            "memory_kb": memory_kb,
            "threshold_kb": self.config.max_memory_kb,
            "constraint_met": memory_kb <= self.config.max_memory_kb,
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Check for violation
        if not result["constraint_met"]:
            result["alert_triggered"] = True
            self._trigger_alert(
                "memory_violation",
                {
                    "agent_id": agent_id,
                    "memory_kb": memory_kb,
                    "threshold_kb": self.config.max_memory_kb,
                },
            )
        else:
            result["alert_triggered"] = False

        # Store metric
        self.metrics["memory"].append(result)

        # Send to CloudWatch
        self._send_metric(
            "MemoryUsage",
            memory_kb,
            "Kilobytes",
            {"AgentId": agent_id, "ConstraintMet": str(result["constraint_met"])},
        )

        return result

    def track_evolution_cycle(self, cycle_data: Dict) -> Dict:
        """Track evolution cycle metrics"""
        fitness_scores = cycle_data.get("fitness_scores", [])

        result = {
            "cycle_id": cycle_data.get("cycle_id"),
            "generation": cycle_data.get("generation", 0),
            "population_size": cycle_data.get("population_size", len(fitness_scores)),
            "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0,
            "max_fitness": max(fitness_scores) if fitness_scores else 0,
            "min_fitness": min(fitness_scores) if fitness_scores else 0,
            "mutations": cycle_data.get("mutations", 0),
            "crossovers": cycle_data.get("crossovers", 0),
            "evolution_rate": 0,  # Will be calculated
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Calculate evolution rate
        if len(self.metrics["evolution_cycles"]) > 0:
            prev_fitness = self.metrics["evolution_cycles"][-1]["avg_fitness"]
            result["evolution_rate"] = result["avg_fitness"] - prev_fitness
        else:
            result["evolution_rate"] = result["avg_fitness"]

        # Store metric
        self.metrics["evolution_cycles"].append(result)

        # Send metrics to CloudWatch
        self._send_metric("EvolutionCycles", 1, "Count", {"Generation": str(result["generation"])})
        self._send_metric("FitnessScore", result["avg_fitness"], "None", {"Type": "Average"})
        self._send_metric("FitnessScore", result["max_fitness"], "None", {"Type": "Maximum"})

        return result

    def track_safety_check(self, safety_data: Dict) -> Dict:
        """Track safety system checks"""
        violations = safety_data.get("violations", [])
        risk_score = safety_data.get("risk_score", 0)

        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.7:
            risk_level = "medium"
        else:
            risk_level = "critical"

        result = {
            "check_id": safety_data.get("check_id"),
            "agent_id": safety_data.get("agent_id"),
            "patterns_checked": safety_data.get("patterns_checked", []),
            "violations": violations,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "passed": len(violations) == 0,
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Check for emergency stop
        if risk_level == "critical" and not result["passed"]:
            result["emergency_stop"] = True
            self._trigger_emergency_stop(safety_data)
        else:
            result["emergency_stop"] = False

        # Store metric
        self.metrics["safety_checks"].append(result)

        # Send to CloudWatch
        if violations:
            self._send_metric(
                "SafetyViolations", len(violations), "Count", {"RiskLevel": risk_level}
            )

        return result

    def send_metrics(self, metrics: List[Dict]) -> Dict:
        """Send metrics to CloudWatch"""
        if not self.cloudwatch:
            return {"success": False, "error": "CloudWatch client not initialized"}

        try:
            metric_data = []
            for metric in metrics:
                metric_data.append(
                    {
                        "MetricName": metric["name"],
                        "Value": metric["value"],
                        "Unit": metric.get("unit", "None"),
                        "Timestamp": datetime.utcnow(),
                    }
                )

            self.cloudwatch.put_metric_data(Namespace=self.namespace, MetricData=metric_data)

            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to send metrics: {e}")
            return {"success": False, "error": str(e)}

    @contextmanager
    def trace_operation(self, operation_name: str):
        """Context manager for X-Ray tracing"""
        subsegment = None
        try:
            # Always try to call begin_subsegment (for mocking purposes)
            subsegment = xray_core.xray_recorder.begin_subsegment(operation_name)
        except Exception:
            # If no segment exists, that's ok - we'll continue without tracing
            pass

        try:
            yield subsegment
        except Exception as e:
            if subsegment:
                try:
                    subsegment.add_exception(e)
                except Exception:
                    pass
            raise
        finally:
            # Always try to call end_subsegment (for mocking purposes)
            try:
                xray_core.xray_recorder.end_subsegment()
            except Exception:
                pass  # Ignore if subsegment doesn't exist

    def get_performance_stats(self) -> Dict:
        """Get aggregated performance statistics"""
        stats = {}

        # Instantiation stats
        if self.metrics["instantiation"]:
            times = [m["time_us"] for m in self.metrics["instantiation"]]
            violations = sum(1 for m in self.metrics["instantiation"] if not m["constraint_met"])
            stats["instantiation"] = {
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "violations": violations,
            }

        # Memory stats
        if self.metrics["memory"]:
            memories = [m["memory_kb"] for m in self.metrics["memory"]]
            violations = sum(1 for m in self.metrics["memory"] if not m["constraint_met"])
            stats["memory"] = {
                "count": len(memories),
                "avg": sum(memories) / len(memories),
                "min": min(memories),
                "max": max(memories),
                "violations": violations,
            }

        # Evolution stats
        if self.metrics["evolution_cycles"]:
            stats["evolution"] = {
                "cycles": len(self.metrics["evolution_cycles"]),
                "avg_fitness": sum(c["avg_fitness"] for c in self.metrics["evolution_cycles"])
                / len(self.metrics["evolution_cycles"]),
                "max_fitness": max(c["max_fitness"] for c in self.metrics["evolution_cycles"]),
            }

        return stats

    def set_alert_threshold(self, metric_name: str, threshold: float):
        """Set alert threshold for a metric"""
        self.alert_thresholds[metric_name] = threshold

    def track_operation_result(self, result: str):
        """Track operation results (success/error)"""
        self.metrics["operations"].append(
            {"result": result, "timestamp": datetime.utcnow().isoformat()}
        )

    def get_active_alerts(self) -> List[Dict]:
        """Get currently active alerts"""
        alerts = []

        # Check error rate
        if self.metrics["operations"]:
            recent_ops = self.metrics["operations"][-100:]  # Last 100 operations
            error_count = sum(1 for op in recent_ops if op["result"] == "error")
            error_rate = error_count / len(recent_ops)

            if error_rate > self.alert_thresholds["error_rate"]:
                alerts.append(
                    {
                        "type": "error_rate",
                        "severity": "high",
                        "value": error_rate,
                        "threshold": self.alert_thresholds["error_rate"],
                        "message": f"Error rate {error_rate:.2%} exceeds threshold",
                    }
                )

        # Check safety violations
        if self.metrics["safety_checks"]:
            recent_checks = self.metrics["safety_checks"][-10:]
            violations = sum(len(check["violations"]) for check in recent_checks)

            if violations > self.alert_thresholds["safety_violations"]:
                alerts.append(
                    {
                        "type": "safety_violations",
                        "severity": "critical",
                        "value": violations,
                        "threshold": self.alert_thresholds["safety_violations"],
                        "message": f"Safety violations detected: {violations}",
                    }
                )

        return alerts

    def export_dashboard_metrics(self) -> Dict:
        """Export metrics for dashboard visualization"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": self.environment,
            "instantiation": self.metrics["instantiation"][-10:]
            if self.metrics["instantiation"]
            else [],
            "memory": self.metrics["memory"][-10:] if self.metrics["memory"] else [],
            "evolution": {
                "cycles": self.metrics["evolution_cycles"][-5:]
                if self.metrics["evolution_cycles"]
                else [],
                "current_generation": self.metrics["evolution_cycles"][-1]["generation"]
                if self.metrics["evolution_cycles"]
                else 0,
            },
            "safety": {
                "recent_checks": self.metrics["safety_checks"][-5:]
                if self.metrics["safety_checks"]
                else [],
                "total_violations": sum(
                    len(check["violations"]) for check in self.metrics["safety_checks"]
                ),
            },
            "alerts": self.get_active_alerts(),
        }

    def _send_metric(self, metric_name: str, value: float, unit: str, dimensions: Dict = None):
        """Send single metric to CloudWatch"""
        if not self.cloudwatch:
            return

        try:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow(),
            }

            if dimensions:
                metric_data["Dimensions"] = [
                    {"Name": k, "Value": str(v)} for k, v in dimensions.items()
                ]

            self.cloudwatch.put_metric_data(Namespace=self.namespace, MetricData=[metric_data])
        except Exception as e:
            logger.error(f"Failed to send metric {metric_name}: {e}")

    def _trigger_alert(self, alert_type: str, details: Dict):
        """Trigger alert via SNS"""
        if not self.sns:
            return

        try:
            message = {
                "alert_type": alert_type,
                "environment": self.environment,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
            }

            # Send to SNS topic
            self.sns.publish(
                TopicArn=f"arn:aws:sns:{self.region}:*:t-developer-evolution-alerts-{self.environment}",
                Subject=f"Evolution System Alert: {alert_type}",
                Message=json.dumps(message, indent=2),
            )
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")

    def _trigger_emergency_stop(self, safety_data: Dict):
        """Trigger emergency stop for critical safety violations"""
        logger.critical(f"EMERGENCY STOP triggered for agent {safety_data.get('agent_id')}")

        # Send critical alert
        self._trigger_alert("emergency_stop", safety_data)

        # TODO: Implement actual emergency stop logic
        # This would involve:
        # 1. Stopping evolution engine
        # 2. Quarantining the agent
        # 3. Rolling back to safe state
        # 4. Notifying administrators
