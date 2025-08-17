"""
Production monitoring and observability hub for T-Developer.

This module provides comprehensive monitoring including SLO/SLA tracking,
distributed tracing, business metrics, and alert correlation for production systems.
"""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional


class MetricType(Enum):
    """Types of metrics collected."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status states."""

    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class SLOType(Enum):
    """Service Level Objective types."""

    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CUSTOM = "custom"


@dataclass
class MetricPoint:
    """Individual metric data point.

    Attributes:
        timestamp: When metric was recorded
        value: Metric value
        labels: Additional labels/tags
    """

    timestamp: datetime
    value: float
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition and data.

    Attributes:
        name: Metric name
        metric_type: Type of metric
        description: Metric description
        unit: Unit of measurement
        labels: Static labels for this metric
        data_points: Historical data points
        retention_hours: How long to retain data
    """

    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    data_points: deque = field(default_factory=lambda: deque(maxlen=10000))
    retention_hours: int = 24

    def add_point(self, value: float, labels: dict[str, str] = None) -> None:
        """Add a data point to the metric."""
        point = MetricPoint(
            timestamp=datetime.utcnow(), value=value, labels={**self.labels, **(labels or {})}
        )
        self.data_points.append(point)

    def get_current_value(self) -> Optional[float]:
        """Get the most recent metric value."""
        if self.data_points:
            return self.data_points[-1].value
        return None

    def get_values_since(self, since: datetime) -> list[MetricPoint]:
        """Get values since a specific time."""
        return [p for p in self.data_points if p.timestamp >= since]

    def cleanup_old_data(self) -> None:
        """Remove data points older than retention period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        # Convert to list, filter, then back to deque
        recent_points = [p for p in self.data_points if p.timestamp >= cutoff_time]
        self.data_points.clear()
        self.data_points.extend(recent_points)


@dataclass
class AlertRule:
    """Alert rule definition.

    Attributes:
        rule_id: Unique rule identifier
        name: Human-readable rule name
        description: Rule description
        metric_name: Metric to monitor
        condition: Alert condition (>, <, ==, etc.)
        threshold: Threshold value
        duration_seconds: How long condition must be true
        severity: Alert severity level
        labels: Additional labels for alerts
        enabled: Whether rule is active
        cooldown_seconds: Minimum time between alerts
    """

    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # >, <, ==, !=, >=, <=
    threshold: float
    duration_seconds: int = 300  # 5 minutes
    severity: AlertSeverity = AlertSeverity.WARNING
    labels: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    cooldown_seconds: int = 3600  # 1 hour
    last_fired: Optional[datetime] = None

    def should_fire(self, current_value: float, duration_met: bool) -> bool:
        """Check if alert should fire."""
        if not self.enabled or not duration_met:
            return False

        # Check cooldown
        if (
            self.last_fired
            and (datetime.utcnow() - self.last_fired).total_seconds() < self.cooldown_seconds
        ):
            return False

        # Evaluate condition
        conditions = {
            ">": current_value > self.threshold,
            "<": current_value < self.threshold,
            ">=": current_value >= self.threshold,
            "<=": current_value <= self.threshold,
            "==": current_value == self.threshold,
            "!=": current_value != self.threshold,
        }

        return conditions.get(self.condition, False)


@dataclass
class Alert:
    """Active alert instance.

    Attributes:
        alert_id: Unique alert identifier
        rule_id: Rule that generated this alert
        timestamp: When alert was created
        status: Current alert status
        severity: Alert severity
        summary: Short alert summary
        description: Detailed alert description
        metric_name: Metric that triggered alert
        current_value: Current metric value
        threshold: Threshold that was breached
        labels: Alert labels
        annotations: Additional annotations
        resolved_at: When alert was resolved
        acknowledged_by: Who acknowledged the alert
    """

    alert_id: str
    rule_id: str
    timestamp: datetime
    status: AlertStatus
    severity: AlertSeverity
    summary: str
    description: str
    metric_name: str
    current_value: float
    threshold: float
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    @property
    def duration_seconds(self) -> float:
        """Get alert duration in seconds."""
        end_time = self.resolved_at or datetime.utcnow()
        return (end_time - self.timestamp).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "severity": self.severity.value,
            "summary": self.summary,
            "description": self.description,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "labels": self.labels,
            "annotations": self.annotations,
            "duration_seconds": self.duration_seconds,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
        }


@dataclass
class SLO:
    """Service Level Objective definition.

    Attributes:
        slo_id: Unique SLO identifier
        name: SLO name
        description: SLO description
        slo_type: Type of SLO
        target_percentage: Target percentage (0.0-100.0)
        time_window_hours: Time window for SLO calculation
        metric_name: Metric used for SLO calculation
        error_budget_consumed: How much error budget is consumed
        compliance_percentage: Current compliance percentage
        last_calculated: When SLO was last calculated
    """

    slo_id: str
    name: str
    description: str
    slo_type: SLOType
    target_percentage: float
    time_window_hours: int = 24
    metric_name: str = ""
    error_budget_consumed: float = 0.0
    compliance_percentage: float = 100.0
    last_calculated: Optional[datetime] = None

    @property
    def error_budget_remaining(self) -> float:
        """Calculate remaining error budget."""
        return max(0.0, 100.0 - self.error_budget_consumed)

    @property
    def is_compliant(self) -> bool:
        """Check if SLO is currently compliant."""
        return self.compliance_percentage >= self.target_percentage


@dataclass
class TraceSpan:
    """Distributed trace span.

    Attributes:
        span_id: Unique span identifier
        trace_id: Trace identifier this span belongs to
        parent_span_id: Parent span identifier
        operation_name: Name of the operation
        start_time: When span started
        end_time: When span ended
        tags: Span tags
        logs: Span logs
        service_name: Service that created this span
        status: Span status (ok, error, timeout)
    """

    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    service_name: str = ""
    status: str = "ok"

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    def add_log(self, message: str, level: str = "info", fields: dict[str, Any] = None) -> None:
        """Add a log entry to the span."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "fields": fields or {},
        }
        self.logs.append(log_entry)


class MonitoringHub:
    """Production monitoring and observability hub.

    Provides comprehensive monitoring including metrics collection, alerting,
    SLO tracking, and distributed tracing for T-Developer production systems.

    Example:
        >>> hub = MonitoringHub()
        >>> await hub.initialize()
        >>> await hub.record_metric("api_requests_total", 1, {"endpoint": "/api/v1/status"})
        >>> slo = await hub.create_slo("API Availability", SLOType.AVAILABILITY, 99.9)
    """

    def __init__(self, config: dict[str, Any] = None) -> None:
        """Initialize monitoring hub.

        Args:
            config: Hub configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._metrics: dict[str, Metric] = {}
        self._alert_rules: dict[str, AlertRule] = {}
        self._active_alerts: dict[str, Alert] = {}
        self._alert_history: list[Alert] = []
        self._slos: dict[str, SLO] = {}
        self._traces: dict[str, list[TraceSpan]] = defaultdict(list)  # trace_id -> spans
        self._notification_handlers: list[Callable] = []
        self._monitoring_active = False

    async def initialize(self) -> None:
        """Initialize the monitoring hub.

        Sets up default metrics, alerts, and SLOs.
        """
        self.logger.info("Initializing monitoring hub")

        await self._setup_default_metrics()
        await self._setup_default_alerts()
        await self._setup_default_slos()

        self.logger.info("Monitoring hub initialized successfully")

    async def _setup_default_metrics(self) -> None:
        """Set up default system metrics."""
        default_metrics = [
            {
                "name": "api_requests_total",
                "metric_type": MetricType.COUNTER,
                "description": "Total number of API requests",
                "unit": "requests",
            },
            {
                "name": "api_request_duration_seconds",
                "metric_type": MetricType.HISTOGRAM,
                "description": "API request duration",
                "unit": "seconds",
            },
            {
                "name": "system_cpu_usage",
                "metric_type": MetricType.GAUGE,
                "description": "System CPU usage percentage",
                "unit": "percent",
            },
            {
                "name": "system_memory_usage",
                "metric_type": MetricType.GAUGE,
                "description": "System memory usage percentage",
                "unit": "percent",
            },
            {
                "name": "active_connections",
                "metric_type": MetricType.GAUGE,
                "description": "Number of active connections",
                "unit": "connections",
            },
            {
                "name": "error_rate",
                "metric_type": MetricType.GAUGE,
                "description": "Error rate percentage",
                "unit": "percent",
            },
        ]

        for metric_data in default_metrics:
            metric = Metric(**metric_data)
            self._metrics[metric.name] = metric

        self.logger.info(f"Set up {len(self._metrics)} default metrics")

    async def _setup_default_alerts(self) -> None:
        """Set up default alert rules."""
        default_alerts = [
            {
                "rule_id": "high_cpu_usage",
                "name": "High CPU Usage",
                "description": "System CPU usage is too high",
                "metric_name": "system_cpu_usage",
                "condition": ">",
                "threshold": 80.0,
                "duration_seconds": 300,
                "severity": AlertSeverity.WARNING,
            },
            {
                "rule_id": "high_memory_usage",
                "name": "High Memory Usage",
                "description": "System memory usage is too high",
                "metric_name": "system_memory_usage",
                "condition": ">",
                "threshold": 90.0,
                "duration_seconds": 300,
                "severity": AlertSeverity.ERROR,
            },
            {
                "rule_id": "high_error_rate",
                "name": "High Error Rate",
                "description": "Error rate is above acceptable threshold",
                "metric_name": "error_rate",
                "condition": ">",
                "threshold": 5.0,
                "duration_seconds": 180,
                "severity": AlertSeverity.CRITICAL,
            },
            {
                "rule_id": "api_latency_high",
                "name": "High API Latency",
                "description": "API response time is too high",
                "metric_name": "api_request_duration_seconds",
                "condition": ">",
                "threshold": 2.0,
                "duration_seconds": 300,
                "severity": AlertSeverity.WARNING,
            },
        ]

        for alert_data in default_alerts:
            alert_rule = AlertRule(**alert_data)
            self._alert_rules[alert_rule.rule_id] = alert_rule

        self.logger.info(f"Set up {len(self._alert_rules)} default alert rules")

    async def _setup_default_slos(self) -> None:
        """Set up default SLOs."""
        default_slos = [
            {
                "slo_id": "api_availability",
                "name": "API Availability",
                "description": "API should be available 99.9% of the time",
                "slo_type": SLOType.AVAILABILITY,
                "target_percentage": 99.9,
                "time_window_hours": 24,
            },
            {
                "slo_id": "api_latency_p95",
                "name": "API Latency P95",
                "description": "95% of API requests should complete within 1 second",
                "slo_type": SLOType.LATENCY,
                "target_percentage": 95.0,
                "time_window_hours": 24,
                "metric_name": "api_request_duration_seconds",
            },
            {
                "slo_id": "error_rate_slo",
                "name": "Error Rate SLO",
                "description": "Error rate should be below 1%",
                "slo_type": SLOType.ERROR_RATE,
                "target_percentage": 99.0,
                "time_window_hours": 24,
                "metric_name": "error_rate",
            },
        ]

        for slo_data in default_slos:
            slo = SLO(**slo_data)
            self._slos[slo.slo_id] = slo

        self.logger.info(f"Set up {len(self._slos)} default SLOs")

    async def start_monitoring(self) -> None:
        """Start continuous monitoring and alerting."""
        if self._monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self._monitoring_active = True
        self.logger.info("Started monitoring and alerting")

        # Start monitoring tasks
        asyncio.create_task(self._metric_cleanup_loop())
        asyncio.create_task(self._alerting_loop())
        asyncio.create_task(self._slo_calculation_loop())
        asyncio.create_task(self._trace_cleanup_loop())

    async def stop_monitoring(self) -> None:
        """Stop monitoring and alerting."""
        self._monitoring_active = False
        self.logger.info("Stopped monitoring and alerting")

    async def _metric_cleanup_loop(self) -> None:
        """Clean up old metric data."""
        while self._monitoring_active:
            try:
                for metric in self._metrics.values():
                    metric.cleanup_old_data()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Metric cleanup error: {e}")
                await asyncio.sleep(300)

    async def _alerting_loop(self) -> None:
        """Main alerting loop."""
        while self._monitoring_active:
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Alerting loop error: {e}")
                await asyncio.sleep(10)

    async def _slo_calculation_loop(self) -> None:
        """SLO calculation loop."""
        while self._monitoring_active:
            try:
                await self._calculate_slos()
                await asyncio.sleep(300)  # Calculate every 5 minutes
            except Exception as e:
                self.logger.error(f"SLO calculation error: {e}")
                await asyncio.sleep(60)

    async def _trace_cleanup_loop(self) -> None:
        """Clean up old trace data."""
        while self._monitoring_active:
            try:
                await self._cleanup_old_traces()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                self.logger.error(f"Trace cleanup error: {e}")
                await asyncio.sleep(300)

    async def record_metric(self, name: str, value: float, labels: dict[str, str] = None) -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            labels: Additional labels
        """
        if name in self._metrics:
            self._metrics[name].add_point(value, labels)
        else:
            # Auto-create metric if it doesn't exist
            metric = Metric(
                name=name, metric_type=MetricType.GAUGE, description=f"Auto-created metric: {name}"
            )
            metric.add_point(value, labels)
            self._metrics[name] = metric

    async def increment_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] = None
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Counter name
            value: Increment value
            labels: Additional labels
        """
        if name in self._metrics:
            current_value = self._metrics[name].get_current_value() or 0.0
            await self.record_metric(name, current_value + value, labels)
        else:
            # Create new counter
            metric = Metric(
                name=name,
                metric_type=MetricType.COUNTER,
                description=f"Auto-created counter: {name}",
            )
            metric.add_point(value, labels)
            self._metrics[name] = metric

    async def record_histogram(
        self, name: str, value: float, labels: dict[str, str] = None
    ) -> None:
        """Record a histogram value.

        Args:
            name: Histogram name
            value: Value to record
            labels: Additional labels
        """
        if name not in self._metrics:
            self._metrics[name] = Metric(
                name=name,
                metric_type=MetricType.HISTOGRAM,
                description=f"Auto-created histogram: {name}",
            )

        await self.record_metric(name, value, labels)

    async def _evaluate_alert_rules(self) -> None:
        """Evaluate all alert rules."""
        for rule in self._alert_rules.values():
            try:
                await self._evaluate_single_rule(rule)
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

    async def _evaluate_single_rule(self, rule: AlertRule) -> None:
        """Evaluate a single alert rule.

        Args:
            rule: Alert rule to evaluate
        """
        if not rule.enabled or rule.metric_name not in self._metrics:
            return

        metric = self._metrics[rule.metric_name]
        current_value = metric.get_current_value()

        if current_value is None:
            return

        # Check if condition has been true for required duration
        duration_start = datetime.utcnow() - timedelta(seconds=rule.duration_seconds)
        recent_points = metric.get_values_since(duration_start)

        if len(recent_points) == 0:
            return

        # Check if all recent points meet the condition
        duration_met = all(
            self._evaluate_condition(point.value, rule.condition, rule.threshold)
            for point in recent_points
        )

        if rule.should_fire(current_value, duration_met):
            await self._fire_alert(rule, current_value)
        else:
            # Check if we should resolve any existing alerts
            await self._check_alert_resolution(rule, current_value)

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate a condition.

        Args:
            value: Current value
            condition: Condition operator
            threshold: Threshold value

        Returns:
            True if condition is met
        """
        conditions = {
            ">": value > threshold,
            "<": value < threshold,
            ">=": value >= threshold,
            "<=": value <= threshold,
            "==": value == threshold,
            "!=": value != threshold,
        }

        return conditions.get(condition, False)

    async def _fire_alert(self, rule: AlertRule, current_value: float) -> None:
        """Fire an alert.

        Args:
            rule: Alert rule that triggered
            current_value: Current metric value
        """
        alert_id = f"alert_{rule.rule_id}_{int(time.time())}"

        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            timestamp=datetime.utcnow(),
            status=AlertStatus.FIRING,
            severity=rule.severity,
            summary=f"{rule.name}: {current_value} {rule.condition} {rule.threshold}",
            description=rule.description,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold,
            labels=rule.labels.copy(),
        )

        self._active_alerts[alert_id] = alert
        rule.last_fired = datetime.utcnow()

        # Send notifications
        await self._send_alert_notification(alert)

        self.logger.warning(f"Alert fired: {alert.summary}")

    async def _check_alert_resolution(self, rule: AlertRule, current_value: float) -> None:
        """Check if alerts should be resolved.

        Args:
            rule: Alert rule to check
            current_value: Current metric value
        """
        # Find active alerts for this rule
        rule_alerts = [
            alert
            for alert in self._active_alerts.values()
            if alert.rule_id == rule.rule_id and alert.status == AlertStatus.FIRING
        ]

        for alert in rule_alerts:
            # Check if condition is no longer met
            if not self._evaluate_condition(current_value, rule.condition, rule.threshold):
                await self._resolve_alert(alert, current_value)

    async def _resolve_alert(self, alert: Alert, current_value: float) -> None:
        """Resolve an alert.

        Args:
            alert: Alert to resolve
            current_value: Current metric value
        """
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.current_value = current_value

        # Move to history
        self._alert_history.append(alert)
        if alert.alert_id in self._active_alerts:
            del self._active_alerts[alert.alert_id]

        # Send resolution notification
        await self._send_alert_notification(alert)

        self.logger.info(f"Alert resolved: {alert.summary}")

    async def _send_alert_notification(self, alert: Alert) -> None:
        """Send alert notification.

        Args:
            alert: Alert to send notification for
        """
        for handler in self._notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Notification handler error: {e}")

    async def _calculate_slos(self) -> None:
        """Calculate SLO compliance."""
        for slo in self._slos.values():
            try:
                await self._calculate_single_slo(slo)
            except Exception as e:
                self.logger.error(f"SLO calculation error for {slo.slo_id}: {e}")

    async def _calculate_single_slo(self, slo: SLO) -> None:
        """Calculate a single SLO.

        Args:
            slo: SLO to calculate
        """
        if slo.slo_type == SLOType.AVAILABILITY:
            await self._calculate_availability_slo(slo)
        elif slo.slo_type == SLOType.LATENCY:
            await self._calculate_latency_slo(slo)
        elif slo.slo_type == SLOType.ERROR_RATE:
            await self._calculate_error_rate_slo(slo)
        elif slo.slo_type == SLOType.THROUGHPUT:
            await self._calculate_throughput_slo(slo)

        slo.last_calculated = datetime.utcnow()

    async def _calculate_availability_slo(self, slo: SLO) -> None:
        """Calculate availability SLO.

        Args:
            slo: Availability SLO to calculate
        """
        # In production, this would check actual uptime/downtime
        # For now, simulate based on error rate

        error_rate_metric = self._metrics.get("error_rate")
        if not error_rate_metric:
            slo.compliance_percentage = 100.0
            return

        time_window = datetime.utcnow() - timedelta(hours=slo.time_window_hours)
        recent_points = error_rate_metric.get_values_since(time_window)

        if not recent_points:
            slo.compliance_percentage = 100.0
            return

        # Calculate availability based on error rate
        avg_error_rate = statistics.mean(p.value for p in recent_points)
        availability = max(0.0, 100.0 - avg_error_rate)

        slo.compliance_percentage = availability
        slo.error_budget_consumed = (
            max(0.0, 100.0 - availability) / (100.0 - slo.target_percentage) * 100.0
        )

    async def _calculate_latency_slo(self, slo: SLO) -> None:
        """Calculate latency SLO.

        Args:
            slo: Latency SLO to calculate
        """
        if not slo.metric_name or slo.metric_name not in self._metrics:
            return

        metric = self._metrics[slo.metric_name]
        time_window = datetime.utcnow() - timedelta(hours=slo.time_window_hours)
        recent_points = metric.get_values_since(time_window)

        if not recent_points:
            slo.compliance_percentage = 100.0
            return

        # Calculate P95 latency
        values = sorted(p.value for p in recent_points)
        p95_index = int(len(values) * 0.95)
        p95_latency = values[p95_index] if p95_index < len(values) else values[-1]

        # Check if P95 is within target (assuming 1 second target)
        target_latency = 1.0  # 1 second
        if p95_latency <= target_latency:
            slo.compliance_percentage = slo.target_percentage
        else:
            # Proportional degradation
            slo.compliance_percentage = max(
                0.0, slo.target_percentage * (target_latency / p95_latency)
            )

        slo.error_budget_consumed = max(0.0, 100.0 - slo.compliance_percentage)

    async def _calculate_error_rate_slo(self, slo: SLO) -> None:
        """Calculate error rate SLO.

        Args:
            slo: Error rate SLO to calculate
        """
        if not slo.metric_name or slo.metric_name not in self._metrics:
            return

        metric = self._metrics[slo.metric_name]
        time_window = datetime.utcnow() - timedelta(hours=slo.time_window_hours)
        recent_points = metric.get_values_since(time_window)

        if not recent_points:
            slo.compliance_percentage = 100.0
            return

        avg_error_rate = statistics.mean(p.value for p in recent_points)

        # Error rate SLO: compliance is inverse of error rate
        max_error_rate = 100.0 - slo.target_percentage
        if avg_error_rate <= max_error_rate:
            slo.compliance_percentage = slo.target_percentage
        else:
            slo.compliance_percentage = max(0.0, 100.0 - avg_error_rate)

        slo.error_budget_consumed = max(0.0, avg_error_rate / max_error_rate * 100.0)

    async def _calculate_throughput_slo(self, slo: SLO) -> None:
        """Calculate throughput SLO.

        Args:
            slo: Throughput SLO to calculate
        """
        # In production, implement throughput calculation
        slo.compliance_percentage = 100.0

    async def start_trace(
        self, operation_name: str, service_name: str = "", parent_span_id: Optional[str] = None
    ) -> TraceSpan:
        """Start a new trace span.

        Args:
            operation_name: Name of the operation
            service_name: Service name
            parent_span_id: Parent span ID if this is a child span

        Returns:
            Created trace span
        """
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())

        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            service_name=service_name,
        )

        self._traces[trace_id].append(span)
        return span

    async def finish_trace_span(self, span: TraceSpan, status: str = "ok") -> None:
        """Finish a trace span.

        Args:
            span: Span to finish
            status: Final span status
        """
        span.end_time = datetime.utcnow()
        span.status = status

        # Record latency metric if this is a root span
        if not span.parent_span_id and span.duration_ms:
            await self.record_histogram(
                "trace_duration_ms",
                span.duration_ms,
                {"operation": span.operation_name, "service": span.service_name, "status": status},
            )

    async def _cleanup_old_traces(self) -> None:
        """Clean up old trace data."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)  # Keep 24 hours

        traces_to_remove = []
        for trace_id, spans in self._traces.items():
            if spans and spans[0].start_time < cutoff_time:
                traces_to_remove.append(trace_id)

        for trace_id in traces_to_remove:
            del self._traces[trace_id]

        if traces_to_remove:
            self.logger.debug(f"Cleaned up {len(traces_to_remove)} old traces")

    def add_notification_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add alert notification handler.

        Args:
            handler: Async function to handle alert notifications
        """
        self._notification_handlers.append(handler)

    async def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert.

        Args:
            alert_id: Alert to acknowledge
            user: User acknowledging the alert

        Returns:
            True if alert was acknowledged
        """
        if alert_id in self._active_alerts:
            alert = self._active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user

            self.logger.info(f"Alert {alert_id} acknowledged by {user}")
            return True

        return False

    async def silence_alert(self, alert_id: str, duration_minutes: int = 60) -> bool:
        """Silence an alert.

        Args:
            alert_id: Alert to silence
            duration_minutes: How long to silence

        Returns:
            True if alert was silenced
        """
        if alert_id in self._active_alerts:
            alert = self._active_alerts[alert_id]
            alert.status = AlertStatus.SILENCED

            # Set up automatic unsilencing
            async def unsilence():
                await asyncio.sleep(duration_minutes * 60)
                if alert_id in self._active_alerts and alert.status == AlertStatus.SILENCED:
                    alert.status = AlertStatus.FIRING

            asyncio.create_task(unsilence())

            self.logger.info(f"Alert {alert_id} silenced for {duration_minutes} minutes")
            return True

        return False

    async def get_monitoring_status(self) -> dict[str, Any]:
        """Get comprehensive monitoring status.

        Returns:
            Monitoring status and metrics
        """
        active_alerts_by_severity = defaultdict(int)
        for alert in self._active_alerts.values():
            active_alerts_by_severity[alert.severity.value] += 1

        slo_compliance = []
        for slo in self._slos.values():
            slo_compliance.append(
                {
                    "slo_id": slo.slo_id,
                    "name": slo.name,
                    "type": slo.slo_type.value,
                    "target": slo.target_percentage,
                    "current": slo.compliance_percentage,
                    "compliant": slo.is_compliant,
                    "error_budget_remaining": slo.error_budget_remaining,
                }
            )

        return {
            "monitoring_active": self._monitoring_active,
            "metrics": {
                "total": len(self._metrics),
                "with_data": sum(1 for m in self._metrics.values() if m.data_points),
            },
            "alerts": {
                "active": len(self._active_alerts),
                "by_severity": dict(active_alerts_by_severity),
                "rules": len(self._alert_rules),
            },
            "slos": {
                "total": len(self._slos),
                "compliant": sum(1 for slo in self._slos.values() if slo.is_compliant),
                "details": slo_compliance,
            },
            "traces": {
                "active_traces": len(self._traces),
                "total_spans": sum(len(spans) for spans in self._traces.values()),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    def get_metric_data(self, metric_name: str, hours: int = 1) -> Optional[dict[str, Any]]:
        """Get metric data.

        Args:
            metric_name: Metric to get data for
            hours: Number of hours of data

        Returns:
            Metric data or None if not found
        """
        if metric_name not in self._metrics:
            return None

        metric = self._metrics[metric_name]
        since_time = datetime.utcnow() - timedelta(hours=hours)
        data_points = metric.get_values_since(since_time)

        if not data_points:
            return {
                "name": metric.name,
                "type": metric.metric_type.value,
                "current_value": None,
                "data_points": [],
            }

        values = [p.value for p in data_points]

        return {
            "name": metric.name,
            "type": metric.metric_type.value,
            "description": metric.description,
            "unit": metric.unit,
            "current_value": metric.get_current_value(),
            "statistics": {
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "count": len(values),
            },
            "data_points": [
                {"timestamp": p.timestamp.isoformat(), "value": p.value, "labels": p.labels}
                for p in data_points
            ],
        }

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get all active alerts.

        Returns:
            List of active alerts
        """
        return [alert.to_dict() for alert in self._active_alerts.values()]

    def get_trace(self, trace_id: str) -> Optional[dict[str, Any]]:
        """Get trace by ID.

        Args:
            trace_id: Trace ID to retrieve

        Returns:
            Trace data or None if not found
        """
        if trace_id not in self._traces:
            return None

        spans = self._traces[trace_id]
        if not spans:
            return None

        # Calculate trace duration
        start_time = min(span.start_time for span in spans)
        end_times = [span.end_time for span in spans if span.end_time]
        end_time = max(end_times) if end_times else datetime.utcnow()

        duration_ms = (end_time - start_time).total_seconds() * 1000

        return {
            "trace_id": trace_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_ms": duration_ms,
            "span_count": len(spans),
            "services": list(set(span.service_name for span in spans if span.service_name)),
            "status": "error" if any(span.status == "error" for span in spans) else "ok",
            "spans": [
                {
                    "span_id": span.span_id,
                    "parent_span_id": span.parent_span_id,
                    "operation_name": span.operation_name,
                    "service_name": span.service_name,
                    "start_time": span.start_time.isoformat(),
                    "end_time": span.end_time.isoformat() if span.end_time else None,
                    "duration_ms": span.duration_ms,
                    "status": span.status,
                    "tags": span.tags,
                    "logs": span.logs,
                }
                for span in spans
            ],
        }
