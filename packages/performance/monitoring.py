"""Monitoring and Alerting - Comprehensive monitoring for T-Developer.

Phase 6: P6-T2 - Reliability Engineering
Advanced monitoring, alerting, and observability system.
"""

from __future__ import annotations

import asyncio
import logging
import smtplib
import statistics
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Optional, Union

import aiohttp
import psutil

# Constants
DEFAULT_COLLECTION_INTERVAL: int = 30  # 30 seconds
DEFAULT_RETENTION_HOURS: int = 24
DEFAULT_ALERT_COOLDOWN: int = 300  # 5 minutes
MAX_METRIC_HISTORY: int = 1000

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"


class AlertStatus(Enum):
    """Alert status."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class Metric:
    """Individual metric data point."""

    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)
    help_text: str = ""

    def to_prometheus_format(self) -> str:
        """Convert to Prometheus format."""
        labels_str = ""
        if self.labels:
            labels_list = [f'{k}="{v}"' for k, v in self.labels.items()]
            labels_str = "{" + ",".join(labels_list) + "}"

        timestamp_ms = int(self.timestamp.timestamp() * 1000)
        return f"{self.name}{labels_str} {self.value} {timestamp_ms}"


@dataclass
class Alert:
    """Alert definition and state."""

    name: str
    description: str
    severity: AlertSeverity
    condition: str  # Alert condition expression
    threshold: Union[int, float]
    duration: int = 0  # Duration in seconds before alerting

    # State
    status: AlertStatus = AlertStatus.ACTIVE
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    last_evaluation: Optional[datetime] = None

    # Metadata
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    runbook_url: Optional[str] = None

    # Internal state
    consecutive_breaches: int = 0
    last_notification: Optional[datetime] = None

    def is_firing(self) -> bool:
        """Check if alert is currently firing."""
        return self.status == AlertStatus.ACTIVE and self.triggered_at is not None

    def should_notify(self, cooldown_seconds: int = DEFAULT_ALERT_COOLDOWN) -> bool:
        """Check if notification should be sent."""
        if not self.is_firing():
            return False

        if self.last_notification is None:
            return True

        return (datetime.now() - self.last_notification).total_seconds() > cooldown_seconds


class MetricCollector:
    """Collect system and application metrics."""

    def __init__(self, collection_interval: int = DEFAULT_COLLECTION_INTERVAL):
        """Initialize metric collector.

        Args:
            collection_interval: Collection interval in seconds
        """
        self.collection_interval = collection_interval
        self.metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=MAX_METRIC_HISTORY))
        self.custom_collectors: list[Callable[[], list[Metric]]] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def add_custom_collector(self, collector: Callable[[], list[Metric]]) -> None:
        """Add custom metric collector.

        Args:
            collector: Function that returns list of metrics
        """
        self.custom_collectors.append(collector)

    async def start_collection(self) -> None:
        """Start metric collection."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._collection_loop())
        self.logger.info("Started metric collection")

    async def stop_collection(self) -> None:
        """Stop metric collection."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped metric collection")

    async def _collection_loop(self) -> None:
        """Main collection loop."""
        while self._running:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                for metric in system_metrics:
                    self.metrics[metric.name].append(metric)

                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                for metric in app_metrics:
                    self.metrics[metric.name].append(metric)

                # Collect custom metrics
                for collector in self.custom_collectors:
                    try:
                        custom_metrics = collector()
                        for metric in custom_metrics:
                            self.metrics[metric.name].append(metric)
                    except Exception as e:
                        self.logger.error(f"Custom collector failed: {e}")

            except Exception as e:
                self.logger.error(f"Metric collection failed: {e}")

            await asyncio.sleep(self.collection_interval)

    def _collect_system_metrics(self) -> list[Metric]:
        """Collect system-level metrics."""
        metrics = []
        timestamp = datetime.now()

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            metrics.append(
                Metric(
                    name="system_cpu_usage_percent",
                    value=cpu_percent,
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="CPU usage percentage",
                )
            )

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(
                Metric(
                    name="system_memory_usage_percent",
                    value=memory.percent,
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Memory usage percentage",
                )
            )

            metrics.append(
                Metric(
                    name="system_memory_available_bytes",
                    value=memory.available,
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Available memory in bytes",
                )
            )

            # Disk metrics
            disk = psutil.disk_usage("/")
            metrics.append(
                Metric(
                    name="system_disk_usage_percent",
                    value=(disk.used / disk.total) * 100,
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Disk usage percentage",
                )
            )

            # Network metrics
            network = psutil.net_io_counters()
            if network:
                metrics.append(
                    Metric(
                        name="system_network_bytes_sent_total",
                        value=network.bytes_sent,
                        metric_type=MetricType.COUNTER,
                        timestamp=timestamp,
                        help_text="Total bytes sent",
                    )
                )

                metrics.append(
                    Metric(
                        name="system_network_bytes_recv_total",
                        value=network.bytes_recv,
                        metric_type=MetricType.COUNTER,
                        timestamp=timestamp,
                        help_text="Total bytes received",
                    )
                )

            # Process metrics
            process = psutil.Process()
            metrics.append(
                Metric(
                    name="process_cpu_usage_percent",
                    value=process.cpu_percent(),
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Process CPU usage",
                )
            )

            memory_info = process.memory_info()
            metrics.append(
                Metric(
                    name="process_memory_rss_bytes",
                    value=memory_info.rss,
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Process RSS memory",
                )
            )

            metrics.append(
                Metric(
                    name="process_open_files_count",
                    value=len(process.open_files()),
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Number of open files",
                )
            )

        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")

        return metrics

    def _collect_application_metrics(self) -> list[Metric]:
        """Collect application-specific metrics."""
        metrics = []
        timestamp = datetime.now()

        # These would typically be provided by the application
        # For now, we'll simulate some basic metrics

        try:
            # Simulated API metrics
            metrics.append(
                Metric(
                    name="api_requests_total",
                    value=self._get_simulated_counter("api_requests"),
                    metric_type=MetricType.COUNTER,
                    timestamp=timestamp,
                    labels={"endpoint": "/api/v1"},
                    help_text="Total API requests",
                )
            )

            metrics.append(
                Metric(
                    name="api_request_duration_seconds",
                    value=self._get_simulated_histogram_value(),
                    metric_type=MetricType.HISTOGRAM,
                    timestamp=timestamp,
                    help_text="API request duration",
                )
            )

            # Simulated agent metrics
            metrics.append(
                Metric(
                    name="agents_active_count",
                    value=self._get_simulated_gauge("active_agents"),
                    metric_type=MetricType.GAUGE,
                    timestamp=timestamp,
                    help_text="Number of active agents",
                )
            )

            metrics.append(
                Metric(
                    name="services_generated_total",
                    value=self._get_simulated_counter("services_generated"),
                    metric_type=MetricType.COUNTER,
                    timestamp=timestamp,
                    help_text="Total services generated",
                )
            )

        except Exception as e:
            self.logger.error(f"Error collecting application metrics: {e}")

        return metrics

    def _get_simulated_counter(self, name: str) -> float:
        """Get simulated counter value."""
        # This would be replaced with actual metric collection
        return time.time() % 1000

    def _get_simulated_gauge(self, name: str) -> float:
        """Get simulated gauge value."""
        # This would be replaced with actual metric collection
        return abs(hash(name + str(time.time()))) % 100

    def _get_simulated_histogram_value(self) -> float:
        """Get simulated histogram value."""
        # This would be replaced with actual metric collection
        import random

        return random.uniform(0.01, 2.0)

    def get_metric_history(self, metric_name: str, duration_minutes: int = 60) -> list[Metric]:
        """Get metric history for specified duration.

        Args:
            metric_name: Name of metric
            duration_minutes: Duration in minutes

        Returns:
            List of metrics within time range
        """
        if metric_name not in self.metrics:
            return []

        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        return [m for m in self.metrics[metric_name] if m.timestamp >= cutoff_time]

    def get_metric_statistics(
        self, metric_name: str, duration_minutes: int = 60
    ) -> dict[str, float]:
        """Get statistical summary of metric.

        Args:
            metric_name: Name of metric
            duration_minutes: Duration in minutes

        Returns:
            Statistical summary
        """
        history = self.get_metric_history(metric_name, duration_minutes)
        if not history:
            return {}

        values = [m.value for m in history]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99),
        }

    def _percentile(self, values: list[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


class AlertManager:
    """Manage alerts and notifications."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize alert manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.alerts: dict[str, Alert] = {}
        self.notification_channels: list[NotificationChannel] = []
        self.logger = logging.getLogger(self.__class__.__name__)

        # State
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.evaluation_interval = self.config.get("evaluation_interval", 60)

    def register_alert(self, alert: Alert) -> None:
        """Register an alert.

        Args:
            alert: Alert to register
        """
        self.alerts[alert.name] = alert
        self.logger.info(f"Registered alert: {alert.name}")

    def add_notification_channel(self, channel: NotificationChannel) -> None:
        """Add notification channel.

        Args:
            channel: Notification channel
        """
        self.notification_channels.append(channel)

    async def start_monitoring(self, metric_collector: MetricCollector) -> None:
        """Start alert monitoring.

        Args:
            metric_collector: Metric collector instance
        """
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop(metric_collector))
        self.logger.info("Started alert monitoring")

    async def stop_monitoring(self) -> None:
        """Stop alert monitoring."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped alert monitoring")

    async def _monitoring_loop(self, metric_collector: MetricCollector) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._evaluate_alerts(metric_collector)
            except Exception as e:
                self.logger.error(f"Alert evaluation failed: {e}")

            await asyncio.sleep(self.evaluation_interval)

    async def _evaluate_alerts(self, metric_collector: MetricCollector) -> None:
        """Evaluate all alerts."""
        for alert in self.alerts.values():
            try:
                await self._evaluate_single_alert(alert, metric_collector)
            except Exception as e:
                self.logger.error(f"Failed to evaluate alert {alert.name}: {e}")

    async def _evaluate_single_alert(self, alert: Alert, metric_collector: MetricCollector) -> None:
        """Evaluate a single alert."""
        alert.last_evaluation = datetime.now()

        # Parse condition and get metric value
        metric_value = self._get_metric_value_for_condition(alert.condition, metric_collector)

        if metric_value is None:
            return

        # Check if threshold is breached
        threshold_breached = self._check_threshold(metric_value, alert.threshold, alert.condition)

        if threshold_breached:
            alert.consecutive_breaches += 1

            # Check if duration requirement is met
            if alert.consecutive_breaches * self.evaluation_interval >= alert.duration:
                if alert.status != AlertStatus.ACTIVE:
                    # Fire alert
                    alert.status = AlertStatus.ACTIVE
                    alert.triggered_at = datetime.now()
                    await self._send_notifications(alert, "FIRING")
                    self.logger.warning(f"Alert FIRING: {alert.name}")
                elif alert.should_notify():
                    # Send reminder notification
                    await self._send_notifications(alert, "FIRING")

        else:
            # Reset consecutive breaches
            alert.consecutive_breaches = 0

            # Resolve alert if it was firing
            if alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                await self._send_notifications(alert, "RESOLVED")
                self.logger.info(f"Alert RESOLVED: {alert.name}")

    def _get_metric_value_for_condition(
        self, condition: str, metric_collector: MetricCollector
    ) -> Optional[float]:
        """Extract metric value from condition."""
        # Simple condition parsing - in production, use a proper expression parser
        # Format: "metric_name > threshold" or "metric_name < threshold"

        parts = condition.split()
        if len(parts) < 3:
            return None

        metric_name = parts[0]

        # Get latest metric value
        if metric_name not in metric_collector.metrics:
            return None

        metrics = metric_collector.metrics[metric_name]
        if not metrics:
            return None

        return metrics[-1].value  # Latest value

    def _check_threshold(self, value: float, threshold: float, condition: str) -> bool:
        """Check if value breaches threshold."""
        if ">" in condition:
            return value > threshold
        elif "<" in condition:
            return value < threshold
        elif ">=" in condition:
            return value >= threshold
        elif "<=" in condition:
            return value <= threshold
        elif "==" in condition:
            return abs(value - threshold) < 0.001  # Float comparison
        return False

    async def _send_notifications(self, alert: Alert, status: str) -> None:
        """Send notifications for alert."""
        alert.last_notification = datetime.now()

        for channel in self.notification_channels:
            try:
                await channel.send_notification(alert, status)
            except Exception as e:
                self.logger.error(
                    f"Failed to send notification via {channel.__class__.__name__}: {e}"
                )


class NotificationChannel(ABC):
    """Abstract notification channel."""

    @abstractmethod
    async def send_notification(self, alert: Alert, status: str) -> None:
        """Send notification for alert."""
        pass


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel."""

    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        """Initialize Slack notification channel.

        Args:
            webhook_url: Slack webhook URL
            channel: Slack channel
        """
        self.webhook_url = webhook_url
        self.channel = channel
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_notification(self, alert: Alert, status: str) -> None:
        """Send Slack notification."""
        color = {"FIRING": "danger", "RESOLVED": "good"}.get(status, "warning")

        emoji = {"FIRING": "🚨", "RESOLVED": "✅"}.get(status, "⚠️")

        message = {
            "channel": self.channel,
            "username": "T-Developer Monitoring",
            "icon_emoji": ":robot_face:",
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} Alert {status}: {alert.name}",
                    "text": alert.description,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Status", "value": status, "short": True},
                        {"title": "Condition", "value": alert.condition, "short": False},
                    ],
                    "footer": "T-Developer Monitoring",
                    "ts": int(datetime.now().timestamp()),
                }
            ],
        }

        if alert.runbook_url:
            message["attachments"][0]["actions"] = [
                {"type": "button", "text": "View Runbook", "url": alert.runbook_url}
            ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=message) as response:
                    if response.status != 200:
                        self.logger.error(f"Slack notification failed: {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel."""

    def __init__(
        self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: list[str]
    ):
        """Initialize email notification channel.

        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            recipients: List of email recipients
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_notification(self, alert: Alert, status: str) -> None:
        """Send email notification."""
        subject = f"T-Developer Alert {status}: {alert.name}"

        body = f"""
Alert: {alert.name}
Status: {status}
Severity: {alert.severity.value.upper()}
Description: {alert.description}

Condition: {alert.condition}
Triggered At: {alert.triggered_at or 'N/A'}

{f'Runbook: {alert.runbook_url}' if alert.runbook_url else ''}

---
T-Developer Monitoring System
"""

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")


class MonitoringDashboard:
    """Simple monitoring dashboard."""

    def __init__(self, metric_collector: MetricCollector, alert_manager: AlertManager):
        """Initialize monitoring dashboard.

        Args:
            metric_collector: Metric collector instance
            alert_manager: Alert manager instance
        """
        self.metric_collector = metric_collector
        self.alert_manager = alert_manager
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_dashboard_data(self) -> dict[str, Any]:
        """Generate dashboard data."""
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "system_overview": self._get_system_overview(),
            "active_alerts": self._get_active_alerts(),
            "metric_summary": self._get_metric_summary(),
            "performance_indicators": self._get_performance_indicators(),
        }

        return dashboard_data

    def _get_system_overview(self) -> dict[str, Any]:
        """Get system overview metrics."""
        overview = {}

        # Get latest system metrics
        for metric_name in [
            "system_cpu_usage_percent",
            "system_memory_usage_percent",
            "system_disk_usage_percent",
        ]:
            if metric_name in self.metric_collector.metrics:
                metrics = self.metric_collector.metrics[metric_name]
                if metrics:
                    overview[metric_name] = metrics[-1].value

        return overview

    def _get_active_alerts(self) -> list[dict[str, Any]]:
        """Get active alerts."""
        active_alerts = []

        for alert in self.alert_manager.alerts.values():
            if alert.is_firing():
                active_alerts.append(
                    {
                        "name": alert.name,
                        "severity": alert.severity.value,
                        "description": alert.description,
                        "triggered_at": alert.triggered_at.isoformat()
                        if alert.triggered_at
                        else None,
                        "duration": (datetime.now() - alert.triggered_at).total_seconds()
                        if alert.triggered_at
                        else 0,
                    }
                )

        return active_alerts

    def _get_metric_summary(self) -> dict[str, Any]:
        """Get metric summary."""
        summary = {}

        for metric_name in self.metric_collector.metrics:
            stats = self.metric_collector.get_metric_statistics(metric_name, 60)
            if stats:
                summary[metric_name] = stats

        return summary

    def _get_performance_indicators(self) -> dict[str, Any]:
        """Get key performance indicators."""
        indicators = {}

        # Calculate SLO compliance
        indicators["slo_compliance"] = self._calculate_slo_compliance()

        # System health score
        indicators["health_score"] = self._calculate_health_score()

        # Alert summary
        total_alerts = len(self.alert_manager.alerts)
        active_alerts = len([a for a in self.alert_manager.alerts.values() if a.is_firing()])
        indicators["alert_summary"] = {
            "total": total_alerts,
            "active": active_alerts,
            "healthy": total_alerts - active_alerts,
        }

        return indicators

    def _calculate_slo_compliance(self) -> float:
        """Calculate SLO compliance percentage."""
        # Simplified SLO compliance calculation
        # In production, this would be based on actual SLO definitions
        return 99.5  # 99.5% compliance

    def _calculate_health_score(self) -> float:
        """Calculate overall system health score."""
        score = 100.0

        # Reduce score based on active alerts
        for alert in self.alert_manager.alerts.values():
            if alert.is_firing():
                if alert.severity == AlertSeverity.CRITICAL:
                    score -= 20
                elif alert.severity == AlertSeverity.WARNING:
                    score -= 10
                elif alert.severity == AlertSeverity.INFO:
                    score -= 5

        return max(0, score)


# Predefined alerts for T-Developer
def create_t_developer_alerts() -> list[Alert]:
    """Create predefined alerts for T-Developer."""
    alerts = []

    # High CPU usage
    cpu_alert = Alert(
        name="high_cpu_usage",
        description="System CPU usage is above 80%",
        severity=AlertSeverity.WARNING,
        condition="system_cpu_usage_percent > 80",
        threshold=80,
        duration=300,  # 5 minutes
        runbook_url="https://runbooks.t-developer.ai/cpu-high",
    )
    alerts.append(cpu_alert)

    # High memory usage
    memory_alert = Alert(
        name="high_memory_usage",
        description="System memory usage is above 85%",
        severity=AlertSeverity.CRITICAL,
        condition="system_memory_usage_percent > 85",
        threshold=85,
        duration=180,  # 3 minutes
        runbook_url="https://runbooks.t-developer.ai/memory-high",
    )
    alerts.append(memory_alert)

    # High disk usage
    disk_alert = Alert(
        name="high_disk_usage",
        description="Disk usage is above 90%",
        severity=AlertSeverity.CRITICAL,
        condition="system_disk_usage_percent > 90",
        threshold=90,
        duration=60,  # 1 minute
        runbook_url="https://runbooks.t-developer.ai/disk-full",
    )
    alerts.append(disk_alert)

    # API latency
    latency_alert = Alert(
        name="high_api_latency",
        description="API response time is above 500ms",
        severity=AlertSeverity.WARNING,
        condition="api_request_duration_seconds > 0.5",
        threshold=0.5,
        duration=120,  # 2 minutes
        runbook_url="https://runbooks.t-developer.ai/latency-high",
    )
    alerts.append(latency_alert)

    return alerts


# Main monitoring function
async def start_monitoring_system(config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Start comprehensive monitoring system.

    Args:
        config: Configuration dictionary

    Returns:
        Monitoring system components
    """
    config = config or {}

    # Initialize components
    metric_collector = MetricCollector(
        collection_interval=config.get("collection_interval", DEFAULT_COLLECTION_INTERVAL)
    )

    alert_manager = AlertManager(config.get("alerting", {}))

    # Register predefined alerts
    alerts = create_t_developer_alerts()
    for alert in alerts:
        alert_manager.register_alert(alert)

    # Add notification channels if configured
    if "slack_webhook" in config:
        slack_channel = SlackNotificationChannel(
            webhook_url=config["slack_webhook"], channel=config.get("slack_channel", "#alerts")
        )
        alert_manager.add_notification_channel(slack_channel)

    if "email" in config:
        email_config = config["email"]
        email_channel = EmailNotificationChannel(
            smtp_server=email_config["smtp_server"],
            smtp_port=email_config["smtp_port"],
            username=email_config["username"],
            password=email_config["password"],
            recipients=email_config["recipients"],
        )
        alert_manager.add_notification_channel(email_channel)

    # Start monitoring
    await metric_collector.start_collection()
    await alert_manager.start_monitoring(metric_collector)

    # Create dashboard
    dashboard = MonitoringDashboard(metric_collector, alert_manager)

    logger.info("Monitoring system started successfully")

    return {
        "metric_collector": metric_collector,
        "alert_manager": alert_manager,
        "dashboard": dashboard,
        "status": "running",
    }
