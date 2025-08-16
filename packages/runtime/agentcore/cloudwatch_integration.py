"""AWS CloudWatch integration for monitoring and logging.

Phase 2: AWS Integration
P2-T3: CloudWatch Integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class MetricUnit(Enum):
    """CloudWatch metric units."""

    SECONDS = "Seconds"
    MICROSECONDS = "Microseconds"
    MILLISECONDS = "Milliseconds"
    BYTES = "Bytes"
    KILOBYTES = "Kilobytes"
    MEGABYTES = "Megabytes"
    GIGABYTES = "Gigabytes"
    TERABYTES = "Terabytes"
    BITS = "Bits"
    KILOBITS = "Kilobits"
    MEGABITS = "Megabits"
    GIGABITS = "Gigabits"
    TERABITS = "Terabits"
    PERCENT = "Percent"
    COUNT = "Count"
    COUNT_PER_SECOND = "Count/Second"
    NONE = "None"


class AlarmState(Enum):
    """CloudWatch alarm states."""

    OK = "OK"
    ALARM = "ALARM"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class MetricData:
    """CloudWatch metric data point.

    Attributes:
        metric_name: Name of the metric
        value: Metric value
        unit: Metric unit
        dimensions: Metric dimensions
        timestamp: Metric timestamp
        namespace: CloudWatch namespace
    """

    metric_name: str
    value: Union[int, float]
    unit: MetricUnit = MetricUnit.COUNT
    dimensions: dict[str, str] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    namespace: str = "T-Developer/AgentCore"

    def to_cloudwatch_format(self) -> dict[str, Any]:
        """Convert to CloudWatch API format."""
        data = {
            "MetricName": self.metric_name,
            "Value": self.value,
            "Unit": self.unit.value,
            "Timestamp": self.timestamp or datetime.utcnow(),
        }

        if self.dimensions:
            data["Dimensions"] = [
                {"Name": name, "Value": value} for name, value in self.dimensions.items()
            ]

        return data


@dataclass
class LogEvent:
    """CloudWatch log event.

    Attributes:
        message: Log message
        timestamp: Event timestamp
        level: Log level
        metadata: Additional metadata
    """

    message: str
    timestamp: Optional[datetime] = None
    level: str = "INFO"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_cloudwatch_format(self) -> dict[str, Any]:
        """Convert to CloudWatch Logs API format."""
        timestamp_ms = int((self.timestamp or datetime.utcnow()).timestamp() * 1000)

        # Build structured message
        structured_message = {"level": self.level, "message": self.message, **self.metadata}

        return {"timestamp": timestamp_ms, "message": json.dumps(structured_message)}


@dataclass
class DashboardWidget:
    """CloudWatch dashboard widget configuration.

    Attributes:
        title: Widget title
        type: Widget type (metric, log, etc.)
        properties: Widget properties
        x: X position in grid
        y: Y position in grid
        width: Widget width
        height: Widget height
    """

    title: str
    type: str
    properties: dict[str, Any]
    x: int = 0
    y: int = 0
    width: int = 6
    height: int = 6

    def to_cloudwatch_format(self) -> dict[str, Any]:
        """Convert to CloudWatch dashboard format."""
        return {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "properties": {"title": self.title, **self.properties},
        }


class MetricBuffer:
    """Buffer for batching metric submissions."""

    def __init__(self, max_size: int = 20, flush_interval: int = 60):
        """Initialize metric buffer.

        Args:
            max_size: Maximum metrics per batch
            flush_interval: Auto-flush interval in seconds
        """
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.buffer: list[MetricData] = []
        self.last_flush = time.time()
        self._lock = asyncio.Lock()

    async def add_metric(self, metric: MetricData) -> bool:
        """Add metric to buffer.

        Args:
            metric: Metric to add

        Returns:
            True if buffer should be flushed
        """
        async with self._lock:
            self.buffer.append(metric)

            # Check if buffer should be flushed
            should_flush = (
                len(self.buffer) >= self.max_size
                or time.time() - self.last_flush >= self.flush_interval
            )

            return should_flush

    async def get_and_clear(self) -> list[MetricData]:
        """Get all buffered metrics and clear buffer.

        Returns:
            List of buffered metrics
        """
        async with self._lock:
            metrics = self.buffer.copy()
            self.buffer.clear()
            self.last_flush = time.time()
            return metrics


class LogBuffer:
    """Buffer for batching log submissions."""

    def __init__(self, max_size: int = 100, flush_interval: int = 30):
        """Initialize log buffer.

        Args:
            max_size: Maximum log events per batch
            flush_interval: Auto-flush interval in seconds
        """
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.buffer: list[LogEvent] = []
        self.last_flush = time.time()
        self._lock = asyncio.Lock()

    async def add_log(self, log_event: LogEvent) -> bool:
        """Add log event to buffer.

        Args:
            log_event: Log event to add

        Returns:
            True if buffer should be flushed
        """
        async with self._lock:
            self.buffer.append(log_event)

            # Check if buffer should be flushed
            should_flush = (
                len(self.buffer) >= self.max_size
                or time.time() - self.last_flush >= self.flush_interval
            )

            return should_flush

    async def get_and_clear(self) -> list[LogEvent]:
        """Get all buffered log events and clear buffer.

        Returns:
            List of buffered log events
        """
        async with self._lock:
            events = self.buffer.copy()
            self.buffer.clear()
            self.last_flush = time.time()
            return events


class CloudWatchClient:
    """AWS CloudWatch client for metrics and logging."""

    def __init__(
        self,
        region: str = "us-east-1",
        namespace: str = "T-Developer/AgentCore",
        log_group: str = "/t-developer/agentcore",
        config: Optional[dict[str, Any]] = None,
    ):
        """Initialize CloudWatch client.

        Args:
            region: AWS region
            namespace: CloudWatch namespace for metrics
            log_group: CloudWatch log group
            config: Additional configuration
        """
        self.region = region
        self.namespace = namespace
        self.log_group = log_group
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize AWS clients
        aws_config = Config(region_name=region, retries={"max_attempts": 3})

        self.cloudwatch = boto3.client("cloudwatch", config=aws_config)
        self.logs_client = boto3.client("logs", config=aws_config)

        # Initialize buffers
        self.metric_buffer = MetricBuffer(
            max_size=self.config.get("metric_batch_size", 20),
            flush_interval=self.config.get("metric_flush_interval", 60),
        )

        self.log_buffer = LogBuffer(
            max_size=self.config.get("log_batch_size", 100),
            flush_interval=self.config.get("log_flush_interval", 30),
        )

        # Log stream tracking
        self.log_streams: dict[str, str] = {}  # stream_name -> sequence_token

        # Background tasks
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start CloudWatch client background tasks."""
        if self._running:
            return

        self._running = True

        # Ensure log group exists
        await self._ensure_log_group()

        # Start background flush task
        self._flush_task = asyncio.create_task(self._flush_loop())

        self.logger.info("CloudWatch client started")

    async def stop(self) -> None:
        """Stop CloudWatch client and flush remaining data."""
        if not self._running:
            return

        self._running = False

        # Cancel background task
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self._flush_metrics()
        await self._flush_logs()

        self.logger.info("CloudWatch client stopped")

    async def put_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        unit: MetricUnit = MetricUnit.COUNT,
        dimensions: Optional[dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Submit a metric to CloudWatch.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Metric unit
            dimensions: Metric dimensions
            timestamp: Metric timestamp
        """
        metric = MetricData(
            metric_name=metric_name,
            value=value,
            unit=unit,
            dimensions=dimensions or {},
            timestamp=timestamp,
            namespace=self.namespace,
        )

        should_flush = await self.metric_buffer.add_metric(metric)
        if should_flush:
            asyncio.create_task(self._flush_metrics())

    async def put_log(
        self,
        message: str,
        level: str = "INFO",
        stream_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Submit a log event to CloudWatch Logs.

        Args:
            message: Log message
            level: Log level
            stream_name: Log stream name (defaults to hostname/datetime)
            metadata: Additional metadata
            timestamp: Log timestamp
        """
        if not stream_name:
            stream_name = f"agentcore-{datetime.now().strftime('%Y-%m-%d')}"

        log_event = LogEvent(
            message=message, timestamp=timestamp, level=level, metadata=metadata or {}
        )

        should_flush = await self.log_buffer.add_log(log_event)
        if should_flush:
            asyncio.create_task(self._flush_logs())

    async def create_alarm(
        self,
        alarm_name: str,
        metric_name: str,
        comparison_operator: str,
        threshold: float,
        evaluation_periods: int = 2,
        period: int = 300,
        statistic: str = "Average",
        dimensions: Optional[dict[str, str]] = None,
        alarm_description: Optional[str] = None,
        alarm_actions: Optional[list[str]] = None,
        ok_actions: Optional[list[str]] = None,
    ) -> bool:
        """Create a CloudWatch alarm.

        Args:
            alarm_name: Name of the alarm
            metric_name: Metric to monitor
            comparison_operator: Comparison operator (GreaterThanThreshold, etc.)
            threshold: Alarm threshold
            evaluation_periods: Number of periods to evaluate
            period: Period in seconds
            statistic: Statistic to monitor
            dimensions: Metric dimensions
            alarm_description: Alarm description
            alarm_actions: Actions to take when alarm state
            ok_actions: Actions to take when OK state

        Returns:
            True if alarm was created successfully
        """
        try:
            alarm_config = {
                "AlarmName": alarm_name,
                "ComparisonOperator": comparison_operator,
                "EvaluationPeriods": evaluation_periods,
                "MetricName": metric_name,
                "Namespace": self.namespace,
                "Period": period,
                "Statistic": statistic,
                "Threshold": threshold,
                "ActionsEnabled": True,
                "Unit": MetricUnit.COUNT.value,
            }

            if alarm_description:
                alarm_config["AlarmDescription"] = alarm_description

            if dimensions:
                alarm_config["Dimensions"] = [
                    {"Name": name, "Value": value} for name, value in dimensions.items()
                ]

            if alarm_actions:
                alarm_config["AlarmActions"] = alarm_actions

            if ok_actions:
                alarm_config["OKActions"] = ok_actions

            # Create alarm
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.cloudwatch.put_metric_alarm(**alarm_config)
            )

            self.logger.info(f"Created CloudWatch alarm: {alarm_name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to create alarm {alarm_name}: {e}")
            return False

    async def create_dashboard(self, dashboard_name: str, widgets: list[DashboardWidget]) -> bool:
        """Create a CloudWatch dashboard.

        Args:
            dashboard_name: Name of the dashboard
            widgets: List of dashboard widgets

        Returns:
            True if dashboard was created successfully
        """
        try:
            # Convert widgets to CloudWatch format
            dashboard_body = {"widgets": [widget.to_cloudwatch_format() for widget in widgets]}

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.cloudwatch.put_dashboard(
                    DashboardName=dashboard_name, DashboardBody=json.dumps(dashboard_body)
                ),
            )

            self.logger.info(f"Created CloudWatch dashboard: {dashboard_name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to create dashboard {dashboard_name}: {e}")
            return False

    async def get_metric_statistics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        period: int = 300,
        statistics: Optional[list[str]] = None,
        dimensions: Optional[dict[str, str]] = None,
    ) -> list[dict[str, Any]]:
        """Get metric statistics from CloudWatch.

        Args:
            metric_name: Name of the metric
            start_time: Start time for data
            end_time: End time for data
            period: Period in seconds
            statistics: List of statistics to retrieve
            dimensions: Metric dimensions

        Returns:
            List of metric data points
        """
        try:
            params = {
                "Namespace": self.namespace,
                "MetricName": metric_name,
                "StartTime": start_time,
                "EndTime": end_time,
                "Period": period,
                "Statistics": statistics or ["Average"],
            }

            if dimensions:
                params["Dimensions"] = [
                    {"Name": name, "Value": value} for name, value in dimensions.items()
                ]

            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.cloudwatch.get_metric_statistics(**params)
            )

            return response.get("Datapoints", [])

        except ClientError as e:
            self.logger.error(f"Failed to get metric statistics: {e}")
            return []

    async def _ensure_log_group(self) -> None:
        """Ensure log group exists."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.logs_client.create_log_group(logGroupName=self.log_group)
            )
            self.logger.info(f"Created log group: {self.log_group}")

        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                self.logger.error(f"Failed to create log group: {e}")
            else:
                self.logger.debug(f"Log group already exists: {self.log_group}")

    async def _ensure_log_stream(self, stream_name: str) -> None:
        """Ensure log stream exists.

        Args:
            stream_name: Name of the log stream
        """
        if stream_name in self.log_streams:
            return

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.logs_client.create_log_stream(
                    logGroupName=self.log_group, logStreamName=stream_name
                ),
            )

            self.log_streams[stream_name] = None  # No sequence token yet
            self.logger.debug(f"Created log stream: {stream_name}")

        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
                self.logger.error(f"Failed to create log stream: {e}")
            else:
                self.log_streams[stream_name] = None

    async def _flush_metrics(self) -> None:
        """Flush buffered metrics to CloudWatch."""
        metrics = await self.metric_buffer.get_and_clear()
        if not metrics:
            return

        try:
            # Group metrics by namespace
            namespaces = {}
            for metric in metrics:
                namespace = metric.namespace
                if namespace not in namespaces:
                    namespaces[namespace] = []
                namespaces[namespace].append(metric.to_cloudwatch_format())

            # Submit metrics by namespace
            for namespace, metric_data in namespaces.items():
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.cloudwatch.put_metric_data(
                        Namespace=namespace, MetricData=metric_data
                    ),
                )

            self.logger.debug(f"Flushed {len(metrics)} metrics to CloudWatch")

        except ClientError as e:
            self.logger.error(f"Failed to flush metrics: {e}")

    async def _flush_logs(self) -> None:
        """Flush buffered logs to CloudWatch Logs."""
        log_events = await self.log_buffer.get_and_clear()
        if not log_events:
            return

        # Group logs by stream (for now, use single default stream)
        stream_name = f"agentcore-{datetime.now().strftime('%Y-%m-%d')}"
        await self._ensure_log_stream(stream_name)

        try:
            # Convert to CloudWatch format and sort by timestamp
            formatted_events = [event.to_cloudwatch_format() for event in log_events]
            formatted_events.sort(key=lambda x: x["timestamp"])

            # Prepare put_log_events parameters
            params = {
                "logGroupName": self.log_group,
                "logStreamName": stream_name,
                "logEvents": formatted_events,
            }

            # Add sequence token if we have one
            sequence_token = self.log_streams.get(stream_name)
            if sequence_token:
                params["sequenceToken"] = sequence_token

            # Submit logs
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.logs_client.put_log_events(**params)
            )

            # Update sequence token
            self.log_streams[stream_name] = response.get("nextSequenceToken")

            self.logger.debug(f"Flushed {len(log_events)} log events to CloudWatch")

        except ClientError as e:
            self.logger.error(f"Failed to flush logs: {e}")

    async def _flush_loop(self) -> None:
        """Background task to periodically flush buffers."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._flush_metrics()
                await self._flush_logs()

            except Exception as e:
                self.logger.error(f"Error in flush loop: {e}")
                await asyncio.sleep(30)


class CloudWatchService:
    """High-level CloudWatch service for agent monitoring."""

    def __init__(
        self,
        region: str = "us-east-1",
        namespace: str = "T-Developer/AgentCore",
        config: Optional[dict[str, Any]] = None,
    ):
        """Initialize CloudWatch service.

        Args:
            region: AWS region
            namespace: CloudWatch namespace
            config: Service configuration
        """
        self.client = CloudWatchClient(region=region, namespace=namespace, config=config)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def start(self) -> None:
        """Start the CloudWatch service."""
        await self.client.start()
        await self._setup_default_dashboard()
        await self._setup_default_alarms()

    async def stop(self) -> None:
        """Stop the CloudWatch service."""
        await self.client.stop()

    async def record_agent_metric(
        self,
        agent_id: str,
        metric_name: str,
        value: Union[int, float],
        unit: MetricUnit = MetricUnit.COUNT,
    ) -> None:
        """Record an agent-specific metric.

        Args:
            agent_id: Agent identifier
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
        """
        await self.client.put_metric(
            metric_name=metric_name, value=value, unit=unit, dimensions={"AgentId": agent_id}
        )

    async def record_task_metric(
        self,
        task_type: str,
        metric_name: str,
        value: Union[int, float],
        agent_id: Optional[str] = None,
        unit: MetricUnit = MetricUnit.COUNT,
    ) -> None:
        """Record a task-specific metric.

        Args:
            task_type: Task type
            metric_name: Metric name
            value: Metric value
            agent_id: Optional agent identifier
            unit: Metric unit
        """
        dimensions = {"TaskType": task_type}
        if agent_id:
            dimensions["AgentId"] = agent_id

        await self.client.put_metric(
            metric_name=metric_name, value=value, unit=unit, dimensions=dimensions
        )

    async def log_agent_event(
        self,
        agent_id: str,
        event_type: str,
        message: str,
        level: str = "INFO",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an agent event.

        Args:
            agent_id: Agent identifier
            event_type: Event type
            message: Log message
            level: Log level
            metadata: Additional metadata
        """
        event_metadata = {"agent_id": agent_id, "event_type": event_type, **(metadata or {})}

        await self.client.put_log(message=message, level=level, metadata=event_metadata)

    async def _setup_default_dashboard(self) -> None:
        """Set up default monitoring dashboard."""
        widgets = [
            DashboardWidget(
                title="Agent Count",
                type="metric",
                properties={
                    "metrics": [[self.client.namespace, "agents_count"]],
                    "period": 300,
                    "stat": "Average",
                    "region": self.client.region,
                    "view": "singleValue",
                },
                x=0,
                y=0,
                width=6,
                height=6,
            ),
            DashboardWidget(
                title="Task Queue Size",
                type="metric",
                properties={
                    "metrics": [[self.client.namespace, "queue_size"]],
                    "period": 300,
                    "stat": "Average",
                    "region": self.client.region,
                    "view": "timeSeries",
                },
                x=6,
                y=0,
                width=6,
                height=6,
            ),
            DashboardWidget(
                title="Task Completion Rate",
                type="metric",
                properties={
                    "metrics": [
                        [self.client.namespace, "task_completed", "status", "completed"],
                        [self.client.namespace, "task_completed", "status", "failed"],
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": self.client.region,
                    "view": "timeSeries",
                },
                x=0,
                y=6,
                width=12,
                height=6,
            ),
            DashboardWidget(
                title="Agent Logs",
                type="log",
                properties={
                    "query": f"SOURCE '{self.client.log_group}' | fields @timestamp, message\n| filter level = 'ERROR'\n| sort @timestamp desc\n| limit 20",
                    "region": self.client.region,
                    "view": "table",
                },
                x=0,
                y=12,
                width=12,
                height=6,
            ),
        ]

        await self.client.create_dashboard(dashboard_name="T-Developer-AgentCore", widgets=widgets)

    async def _setup_default_alarms(self) -> None:
        """Set up default monitoring alarms."""
        # High error rate alarm
        await self.client.create_alarm(
            alarm_name="T-Developer-HighErrorRate",
            metric_name="task_completed",
            comparison_operator="GreaterThanThreshold",
            threshold=10,
            period=300,
            statistic="Sum",
            dimensions={"status": "failed"},
            alarm_description="High task failure rate detected",
        )

        # Large queue size alarm
        await self.client.create_alarm(
            alarm_name="T-Developer-LargeQueueSize",
            metric_name="queue_size",
            comparison_operator="GreaterThanThreshold",
            threshold=100,
            period=300,
            statistic="Average",
            alarm_description="Task queue is getting large",
        )
