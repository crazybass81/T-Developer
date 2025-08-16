"""AWS X-Ray integration for distributed tracing and performance analysis.

Phase 2: AWS Integration
P2-T4: X-Ray Integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class TraceSegmentType(Enum):
    """X-Ray trace segment types."""

    SUBSEGMENT = "subsegment"
    SERVICE = "service"


class AnnotationType(Enum):
    """X-Ray annotation types for indexing."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass
class TraceAnnotation:
    """X-Ray trace annotation.

    Attributes:
        key: Annotation key
        value: Annotation value
        type: Annotation type
    """

    key: str
    value: Any
    type: AnnotationType = AnnotationType.STRING

    def to_xray_format(self) -> dict[str, Any]:
        """Convert to X-Ray format."""
        return {self.key: self.value}


@dataclass
class TraceMetadata:
    """X-Ray trace metadata.

    Attributes:
        namespace: Metadata namespace
        data: Metadata content
    """

    namespace: str
    data: dict[str, Any]

    def to_xray_format(self) -> dict[str, Any]:
        """Convert to X-Ray format."""
        return {self.namespace: self.data}


@dataclass
class TraceException:
    """X-Ray exception information.

    Attributes:
        id: Exception ID
        message: Exception message
        type: Exception type
        remote: Whether exception occurred remotely
        truncated: Number of stack frames truncated
        skipped: Number of stack frames skipped
        cause: Cause ID
        stack: Stack trace frames
    """

    id: str
    message: str
    type: str = "Exception"
    remote: bool = False
    truncated: int = 0
    skipped: int = 0
    cause: Optional[str] = None
    stack: list[dict[str, Any]] = field(default_factory=list)

    def to_xray_format(self) -> dict[str, Any]:
        """Convert to X-Ray format."""
        exception_data = {
            "id": self.id,
            "message": self.message,
            "type": self.type,
            "remote": self.remote,
        }

        if self.truncated:
            exception_data["truncated"] = self.truncated

        if self.skipped:
            exception_data["skipped"] = self.skipped

        if self.cause:
            exception_data["cause"] = self.cause

        if self.stack:
            exception_data["stack"] = self.stack

        return exception_data


@dataclass
class TraceHttp:
    """HTTP information for X-Ray trace.

    Attributes:
        request: HTTP request information
        response: HTTP response information
    """

    request: Optional[dict[str, Any]] = None
    response: Optional[dict[str, Any]] = None

    def to_xray_format(self) -> dict[str, Any]:
        """Convert to X-Ray format."""
        http_data = {}

        if self.request:
            http_data["request"] = self.request

        if self.response:
            http_data["response"] = self.response

        return http_data


@dataclass
class TraceSegment:
    """X-Ray trace segment.

    Attributes:
        id: Segment ID
        name: Segment name
        trace_id: Trace ID
        parent_id: Parent segment ID
        start_time: Segment start time
        end_time: Segment end time
        in_progress: Whether segment is in progress
        annotations: Segment annotations
        metadata: Segment metadata
        subsegments: Child subsegments
        error: Whether segment had an error
        fault: Whether segment had a fault
        throttle: Whether request was throttled
        http: HTTP information
        aws: AWS service information
        exceptions: Exception information
        sql: SQL information
        namespace: Segment namespace
        user: User information
    """

    id: str
    name: str
    trace_id: str
    parent_id: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    in_progress: bool = True
    annotations: list[TraceAnnotation] = field(default_factory=list)
    metadata: list[TraceMetadata] = field(default_factory=list)
    subsegments: list[TraceSegment] = field(default_factory=list)
    error: bool = False
    fault: bool = False
    throttle: bool = False
    http: Optional[TraceHttp] = None
    aws: Optional[dict[str, Any]] = None
    exceptions: list[TraceException] = field(default_factory=list)
    sql: Optional[dict[str, Any]] = None
    namespace: str = "local"
    user: Optional[str] = None

    def to_xray_format(self) -> dict[str, Any]:
        """Convert to X-Ray segment format."""
        segment_data = {
            "id": self.id,
            "name": self.name,
            "trace_id": self.trace_id,
            "start_time": self.start_time or time.time(),
            "in_progress": self.in_progress,
            "namespace": self.namespace,
        }

        if self.parent_id:
            segment_data["parent_id"] = self.parent_id
            segment_data["type"] = "subsegment"

        if self.end_time:
            segment_data["end_time"] = self.end_time

        if self.annotations:
            annotations = {}
            for annotation in self.annotations:
                annotations.update(annotation.to_xray_format())
            segment_data["annotations"] = annotations

        if self.metadata:
            metadata = {}
            for meta in self.metadata:
                metadata.update(meta.to_xray_format())
            segment_data["metadata"] = metadata

        if self.subsegments:
            segment_data["subsegments"] = [subseg.to_xray_format() for subseg in self.subsegments]

        if self.error:
            segment_data["error"] = True

        if self.fault:
            segment_data["fault"] = True

        if self.throttle:
            segment_data["throttle"] = True

        if self.http:
            segment_data["http"] = self.http.to_xray_format()

        if self.aws:
            segment_data["aws"] = self.aws

        if self.exceptions:
            segment_data["cause"] = {
                "exceptions": [exc.to_xray_format() for exc in self.exceptions]
            }

        if self.sql:
            segment_data["sql"] = self.sql

        if self.user:
            segment_data["user"] = self.user

        return segment_data


class TraceContext:
    """X-Ray trace context manager."""

    def __init__(self, trace_id: Optional[str] = None):
        """Initialize trace context.

        Args:
            trace_id: Existing trace ID or None to generate new one
        """
        self.trace_id = trace_id or self._generate_trace_id()
        self.segments: dict[str, TraceSegment] = {}
        self.active_segment: Optional[str] = None

    def _generate_trace_id(self) -> str:
        """Generate a new X-Ray trace ID."""
        # X-Ray trace ID format: 1-{hex timestamp}-{hex random}
        timestamp = hex(int(time.time()))[2:]
        random_part = uuid.uuid4().hex[:24]
        return f"1-{timestamp}-{random_part}"

    def create_segment(
        self, name: str, parent_id: Optional[str] = None, namespace: str = "local"
    ) -> TraceSegment:
        """Create a new trace segment.

        Args:
            name: Segment name
            parent_id: Parent segment ID
            namespace: Segment namespace

        Returns:
            Created trace segment
        """
        segment_id = uuid.uuid4().hex[:16]

        segment = TraceSegment(
            id=segment_id,
            name=name,
            trace_id=self.trace_id,
            parent_id=parent_id,
            start_time=time.time(),
            namespace=namespace,
        )

        self.segments[segment_id] = segment
        return segment

    def get_segment(self, segment_id: str) -> Optional[TraceSegment]:
        """Get segment by ID.

        Args:
            segment_id: Segment identifier

        Returns:
            Trace segment or None
        """
        return self.segments.get(segment_id)

    def close_segment(self, segment_id: str, error: bool = False, fault: bool = False) -> None:
        """Close a trace segment.

        Args:
            segment_id: Segment identifier
            error: Whether segment had an error
            fault: Whether segment had a fault
        """
        if segment_id in self.segments:
            segment = self.segments[segment_id]
            segment.end_time = time.time()
            segment.in_progress = False
            segment.error = error
            segment.fault = fault


class XRayClient:
    """AWS X-Ray client for distributed tracing."""

    def __init__(
        self,
        region: str = "us-east-1",
        service_name: str = "t-developer-agentcore",
        config: Optional[dict[str, Any]] = None,
    ):
        """Initialize X-Ray client.

        Args:
            region: AWS region
            service_name: Service name for traces
            config: Additional configuration
        """
        self.region = region
        self.service_name = service_name
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize AWS X-Ray client
        aws_config = Config(region_name=region, retries={"max_attempts": 3})

        self.xray_client = boto3.client("xray", config=aws_config)

        # Trace buffering
        self.trace_buffer: list[TraceSegment] = []
        self.buffer_size = self.config.get("buffer_size", 50)
        self.flush_interval = self.config.get("flush_interval", 30)
        self._buffer_lock = asyncio.Lock()

        # Background tasks
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None

        # Active traces
        self.active_traces: dict[str, TraceContext] = {}

    async def start(self) -> None:
        """Start X-Ray client background tasks."""
        if self._running:
            return

        self._running = True

        # Start background flush task
        self._flush_task = asyncio.create_task(self._flush_loop())

        self.logger.info("X-Ray client started")

    async def stop(self) -> None:
        """Stop X-Ray client and flush remaining traces."""
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
        await self._flush_traces()

        self.logger.info("X-Ray client stopped")

    def create_trace_context(self, trace_id: Optional[str] = None) -> TraceContext:
        """Create a new trace context.

        Args:
            trace_id: Existing trace ID or None for new trace

        Returns:
            Trace context
        """
        context = TraceContext(trace_id)
        self.active_traces[context.trace_id] = context
        return context

    def get_trace_context(self, trace_id: str) -> Optional[TraceContext]:
        """Get existing trace context.

        Args:
            trace_id: Trace identifier

        Returns:
            Trace context or None
        """
        return self.active_traces.get(trace_id)

    @asynccontextmanager
    async def trace_segment(
        self,
        name: str,
        trace_context: Optional[TraceContext] = None,
        parent_id: Optional[str] = None,
        namespace: str = "local",
        annotations: Optional[list[TraceAnnotation]] = None,
        metadata: Optional[list[TraceMetadata]] = None,
    ) -> AsyncGenerator[TraceSegment, None]:
        """Context manager for tracing a code segment.

        Args:
            name: Segment name
            trace_context: Trace context (creates new if None)
            parent_id: Parent segment ID
            namespace: Segment namespace
            annotations: Segment annotations
            metadata: Segment metadata

        Yields:
            Trace segment
        """
        # Create or get trace context
        if trace_context is None:
            trace_context = self.create_trace_context()

        # Create segment
        segment = trace_context.create_segment(name=name, parent_id=parent_id, namespace=namespace)

        # Add annotations and metadata
        if annotations:
            segment.annotations.extend(annotations)

        if metadata:
            segment.metadata.extend(metadata)

        try:
            yield segment

        except Exception as e:
            # Record exception
            exception = TraceException(id=str(uuid.uuid4()), message=str(e), type=type(e).__name__)
            segment.exceptions.append(exception)
            segment.fault = True
            raise

        finally:
            # Close segment
            trace_context.close_segment(
                segment.id, error=bool(segment.exceptions), fault=segment.fault
            )

            # Buffer for submission
            await self._buffer_segment(segment)

    async def trace_agent_task(
        self,
        agent_id: str,
        task_id: str,
        task_type: str,
        trace_context: Optional[TraceContext] = None,
    ) -> AsyncGenerator[TraceSegment, None]:
        """Trace an agent task execution.

        Args:
            agent_id: Agent identifier
            task_id: Task identifier
            task_type: Task type
            trace_context: Trace context

        Yields:
            Trace segment for the task
        """
        annotations = [
            TraceAnnotation("agent_id", agent_id),
            TraceAnnotation("task_id", task_id),
            TraceAnnotation("task_type", task_type),
        ]

        metadata = [
            TraceMetadata(
                "task",
                {
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "task_type": task_type,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        ]

        async with self.trace_segment(
            name=f"agent-task-{task_type}",
            trace_context=trace_context,
            namespace="remote",
            annotations=annotations,
            metadata=metadata,
        ) as segment:
            yield segment

    async def trace_bedrock_call(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        trace_context: Optional[TraceContext] = None,
        parent_id: Optional[str] = None,
    ) -> AsyncGenerator[TraceSegment, None]:
        """Trace a Bedrock API call.

        Args:
            model_id: Bedrock model identifier
            input_tokens: Input token count
            output_tokens: Output token count
            trace_context: Trace context
            parent_id: Parent segment ID

        Yields:
            Trace segment for the Bedrock call
        """
        annotations = [
            TraceAnnotation("model_id", model_id),
            TraceAnnotation("input_tokens", input_tokens, AnnotationType.NUMBER),
            TraceAnnotation("output_tokens", output_tokens, AnnotationType.NUMBER),
        ]

        aws_data = {
            "bedrock": {
                "model_id": model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
        }

        async with self.trace_segment(
            name="bedrock-invoke",
            trace_context=trace_context,
            parent_id=parent_id,
            namespace="aws",
            annotations=annotations,
        ) as segment:
            segment.aws = aws_data
            yield segment

    async def trace_external_call(
        self,
        service_name: str,
        operation: str,
        url: Optional[str] = None,
        trace_context: Optional[TraceContext] = None,
        parent_id: Optional[str] = None,
    ) -> AsyncGenerator[TraceSegment, None]:
        """Trace an external service call.

        Args:
            service_name: External service name
            operation: Operation being performed
            url: Service URL
            trace_context: Trace context
            parent_id: Parent segment ID

        Yields:
            Trace segment for the external call
        """
        annotations = [
            TraceAnnotation("service", service_name),
            TraceAnnotation("operation", operation),
        ]

        http_data = None
        if url:
            http_data = TraceHttp(request={"url": url, "method": "POST"})

        async with self.trace_segment(
            name=f"{service_name}-{operation}",
            trace_context=trace_context,
            parent_id=parent_id,
            namespace="remote",
            annotations=annotations,
        ) as segment:
            if http_data:
                segment.http = http_data
            yield segment

    async def add_annotation(
        self,
        segment: TraceSegment,
        key: str,
        value: Any,
        annotation_type: AnnotationType = AnnotationType.STRING,
    ) -> None:
        """Add annotation to segment.

        Args:
            segment: Trace segment
            key: Annotation key
            value: Annotation value
            annotation_type: Annotation type
        """
        annotation = TraceAnnotation(key, value, annotation_type)
        segment.annotations.append(annotation)

    async def add_metadata(
        self, segment: TraceSegment, namespace: str, data: dict[str, Any]
    ) -> None:
        """Add metadata to segment.

        Args:
            segment: Trace segment
            namespace: Metadata namespace
            data: Metadata content
        """
        metadata = TraceMetadata(namespace, data)
        segment.metadata.append(metadata)

    async def get_trace_summary(
        self,
        trace_id: str,
        time_range_start: Optional[datetime] = None,
        time_range_end: Optional[datetime] = None,
    ) -> Optional[dict[str, Any]]:
        """Get trace summary from X-Ray.

        Args:
            trace_id: Trace identifier
            time_range_start: Start of time range
            time_range_end: End of time range

        Returns:
            Trace summary or None
        """
        try:
            params = {"TraceIds": [trace_id]}

            if time_range_start and time_range_end:
                params["TimeRangeType"] = "TimeRangeByStartTime"
                params["StartTime"] = time_range_start
                params["EndTime"] = time_range_end

            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.xray_client.get_trace_summaries(**params)
            )

            summaries = response.get("TraceSummaries", [])
            return summaries[0] if summaries else None

        except ClientError as e:
            self.logger.error(f"Failed to get trace summary: {e}")
            return None

    async def get_service_map(
        self, start_time: datetime, end_time: datetime
    ) -> list[dict[str, Any]]:
        """Get service map for time range.

        Args:
            start_time: Start time
            end_time: End time

        Returns:
            List of service map entries
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.xray_client.get_service_graph(StartTime=start_time, EndTime=end_time),
            )

            return response.get("Services", [])

        except ClientError as e:
            self.logger.error(f"Failed to get service map: {e}")
            return []

    async def _buffer_segment(self, segment: TraceSegment) -> None:
        """Buffer a segment for submission.

        Args:
            segment: Trace segment to buffer
        """
        async with self._buffer_lock:
            self.trace_buffer.append(segment)

            # Flush if buffer is full
            if len(self.trace_buffer) >= self.buffer_size:
                await self._flush_traces()

    async def _flush_traces(self) -> None:
        """Flush buffered traces to X-Ray."""
        async with self._buffer_lock:
            if not self.trace_buffer:
                return

            segments = self.trace_buffer.copy()
            self.trace_buffer.clear()

        try:
            # Convert segments to X-Ray format
            trace_documents = []
            for segment in segments:
                document = json.dumps(segment.to_xray_format())
                trace_documents.append(document)

            # Submit traces in batches
            batch_size = 50  # X-Ray limit
            for i in range(0, len(trace_documents), batch_size):
                batch = trace_documents[i : i + batch_size]

                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.xray_client.put_trace_segments(TraceSegmentDocuments=batch)
                )

            self.logger.debug(f"Flushed {len(segments)} trace segments to X-Ray")

        except ClientError as e:
            self.logger.error(f"Failed to flush traces: {e}")

    async def _flush_loop(self) -> None:
        """Background task to periodically flush traces."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_traces()

            except Exception as e:
                self.logger.error(f"Error in flush loop: {e}")
                await asyncio.sleep(self.flush_interval)


class XRayService:
    """High-level X-Ray service for distributed tracing."""

    def __init__(
        self,
        region: str = "us-east-1",
        service_name: str = "t-developer-agentcore",
        config: Optional[dict[str, Any]] = None,
    ):
        """Initialize X-Ray service.

        Args:
            region: AWS region
            service_name: Service name
            config: Service configuration
        """
        self.client = XRayClient(region=region, service_name=service_name, config=config)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def start(self) -> None:
        """Start the X-Ray service."""
        await self.client.start()

    async def stop(self) -> None:
        """Stop the X-Ray service."""
        await self.client.stop()

    async def trace_agent_execution(
        self, agent_id: str, task_id: str, task_type: str
    ) -> AsyncGenerator[TraceSegment, None]:
        """Trace agent task execution.

        Args:
            agent_id: Agent identifier
            task_id: Task identifier
            task_type: Task type

        Yields:
            Trace segment
        """
        async with self.client.trace_agent_task(
            agent_id=agent_id, task_id=task_id, task_type=task_type
        ) as segment:
            yield segment

    async def trace_llm_call(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        trace_context: Optional[TraceContext] = None,
        parent_id: Optional[str] = None,
    ) -> AsyncGenerator[TraceSegment, None]:
        """Trace LLM API call.

        Args:
            model_id: Model identifier
            input_tokens: Input token count
            output_tokens: Output token count
            trace_context: Trace context
            parent_id: Parent segment ID

        Yields:
            Trace segment
        """
        async with self.client.trace_bedrock_call(
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            trace_context=trace_context,
            parent_id=parent_id,
        ) as segment:
            yield segment

    async def analyze_performance(self, start_time: datetime, end_time: datetime) -> dict[str, Any]:
        """Analyze performance using trace data.

        Args:
            start_time: Analysis start time
            end_time: Analysis end time

        Returns:
            Performance analysis results
        """
        # Get service map
        service_map = await self.client.get_service_map(start_time, end_time)

        # Analyze bottlenecks
        bottlenecks = []
        for service in service_map:
            response_time_histogram = service.get("ResponseTimeHistogram", {})
            if response_time_histogram:
                high_latency = response_time_histogram.get("TotalTime", 0) > 1.0
                if high_latency:
                    bottlenecks.append(
                        {
                            "service": service.get("Name"),
                            "avg_response_time": response_time_histogram.get("TotalTime"),
                            "error_rate": service.get("SummaryStatistics", {})
                            .get("ErrorStatistics", {})
                            .get("ErrorRate", 0),
                        }
                    )

        return {
            "service_map": service_map,
            "bottlenecks": bottlenecks,
            "analysis_period": {"start": start_time.isoformat(), "end": end_time.isoformat()},
        }
