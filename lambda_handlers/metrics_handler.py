"""Lambda handler for metrics collection and retrieval."""

import json
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
dynamodb = boto3.resource("dynamodb")
cloudwatch = boto3.client("cloudwatch")
timestream = boto3.client("timestream-write")
timestream_query = boto3.client("timestream-query")

# Environment variables
METRICS_TABLE = os.environ.get("METRICS_TABLE", "t-developer-metrics")
TIMESTREAM_DB = os.environ.get("TIMESTREAM_DB", "t-developer-metrics")
TIMESTREAM_TABLE = os.environ.get("TIMESTREAM_TABLE", "metrics")


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for Decimal types."""

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def validate_metrics_request(event: dict[str, Any]) -> dict[str, Any]:
    """Validate metrics request."""
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event

    # Validate metric name format
    if "metric_name" in body:
        metric_name = body["metric_name"]
        if not metric_name or not isinstance(metric_name, str):
            raise ValueError("Invalid metric_name")

    # Validate metric value
    if "value" in body:
        try:
            float(body["value"])
        except (TypeError, ValueError):
            raise ValueError("Invalid metric value - must be numeric")

    return body


def save_metric(
    metric_name: str, value: float, tags: dict[str, str] = None, timestamp: Optional[str] = None
) -> str:
    """Save metric to DynamoDB and TimeStream.

    Args:
        metric_name: Name of the metric
        value: Metric value
        tags: Optional tags for the metric
        timestamp: Optional timestamp (ISO format)

    Returns:
        Metric ID
    """
    from uuid import uuid4

    metric_id = f"metric-{uuid4()!s}"

    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()

    if tags is None:
        tags = {}

    # Save to DynamoDB
    table = dynamodb.Table(METRICS_TABLE)

    try:
        table.put_item(
            Item={
                "metric_id": metric_id,
                "metric_name": metric_name,
                "value": Decimal(str(value)),
                "tags": tags,
                "timestamp": timestamp,
                "ttl": int((datetime.utcnow() + timedelta(days=30)).timestamp()),  # 30 day TTL
            }
        )
        logger.info(f"Saved metric {metric_name}={value} with ID {metric_id}")
    except ClientError as e:
        logger.error(f"Failed to save metric to DynamoDB: {e}")
        raise

    # Save to TimeStream if configured
    if TIMESTREAM_DB and TIMESTREAM_TABLE:
        try:
            save_to_timestream(metric_name, value, tags, timestamp)
        except Exception as e:
            logger.warning(f"Failed to save to TimeStream: {e}")

    # Send to CloudWatch
    try:
        send_to_cloudwatch(metric_name, value, tags)
    except Exception as e:
        logger.warning(f"Failed to send to CloudWatch: {e}")

    return metric_id


def save_to_timestream(
    metric_name: str, value: float, tags: dict[str, str], timestamp: str
) -> None:
    """Save metric to AWS TimeStream."""
    try:
        # Convert timestamp to milliseconds
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        time_value = str(int(dt.timestamp() * 1000))

        # Prepare dimensions
        dimensions = [{"Name": "metric_name", "Value": metric_name}]
        for key, val in tags.items():
            dimensions.append({"Name": key, "Value": str(val)})

        # Write to TimeStream
        timestream.write_records(
            DatabaseName=TIMESTREAM_DB,
            TableName=TIMESTREAM_TABLE,
            Records=[
                {
                    "Time": time_value,
                    "TimeUnit": "MILLISECONDS",
                    "Dimensions": dimensions,
                    "MeasureName": "value",
                    "MeasureValue": str(value),
                    "MeasureValueType": "DOUBLE",
                }
            ],
        )
    except ClientError as e:
        logger.error(f"Failed to write to TimeStream: {e}")
        raise


def send_to_cloudwatch(metric_name: str, value: float, tags: dict[str, str]) -> None:
    """Send metric to CloudWatch."""
    try:
        # Prepare dimensions
        dimensions = []
        for key, val in tags.items():
            dimensions.append({"Name": key, "Value": str(val)})

        # Send to CloudWatch
        cloudwatch.put_metric_data(
            Namespace="TDeveloper/Metrics",
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": "None",
                    "Dimensions": dimensions,
                }
            ],
        )
    except ClientError as e:
        logger.error(f"Failed to send to CloudWatch: {e}")


def get_metrics(
    metric_name: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Get metrics from DynamoDB.

    Args:
        metric_name: Optional metric name filter
        start_time: Optional start time (ISO format)
        end_time: Optional end time (ISO format)
        limit: Maximum number of results

    Returns:
        List of metrics
    """
    table = dynamodb.Table(METRICS_TABLE)

    # Default time range (last 24 hours)
    if not start_time:
        start_time = (datetime.utcnow() - timedelta(days=1)).isoformat()
    if not end_time:
        end_time = datetime.utcnow().isoformat()

    try:
        if metric_name:
            # Query by metric name and time range
            response = table.query(
                IndexName="metric_name_timestamp_index",
                KeyConditionExpression="metric_name = :name AND #ts BETWEEN :start AND :end",
                ExpressionAttributeNames={"#ts": "timestamp"},
                ExpressionAttributeValues={
                    ":name": metric_name,
                    ":start": start_time,
                    ":end": end_time,
                },
                Limit=limit,
                ScanIndexForward=False,  # Most recent first
            )
        else:
            # Scan with time filter
            response = table.scan(
                FilterExpression="#ts BETWEEN :start AND :end",
                ExpressionAttributeNames={"#ts": "timestamp"},
                ExpressionAttributeValues={":start": start_time, ":end": end_time},
                Limit=limit,
            )

        return response.get("Items", [])
    except ClientError as e:
        logger.error(f"Failed to get metrics: {e}")
        return []


def get_metric_statistics(
    metric_name: str,
    statistic: str = "Average",
    period: int = 300,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Get metric statistics from CloudWatch.

    Args:
        metric_name: Metric name
        statistic: Statistic type (Average, Sum, Minimum, Maximum, SampleCount)
        period: Period in seconds
        start_time: Start time (ISO format)
        end_time: End time (ISO format)

    Returns:
        List of data points
    """
    if not start_time:
        start_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    if not end_time:
        end_time = datetime.utcnow().isoformat()

    try:
        response = cloudwatch.get_metric_statistics(
            Namespace="TDeveloper/Metrics",
            MetricName=metric_name,
            Statistics=[statistic],
            StartTime=datetime.fromisoformat(start_time.replace("Z", "+00:00")),
            EndTime=datetime.fromisoformat(end_time.replace("Z", "+00:00")),
            Period=period,
        )

        return response.get("Datapoints", [])
    except ClientError as e:
        logger.error(f"Failed to get metric statistics: {e}")
        return []


def get_metric_summary() -> dict[str, Any]:
    """Get metrics summary for dashboard."""
    try:
        # Get various metric summaries
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        # Get recent metrics
        recent_metrics = get_metrics(limit=10)

        # Get key performance indicators
        kpis = {
            "evolution_cycles": get_metric_value("evolution.cycles.completed", day_ago.isoformat()),
            "agent_executions": get_metric_value("agent.executions.total", day_ago.isoformat()),
            "improvement_rate": get_metric_value("evolution.improvement.rate", day_ago.isoformat()),
            "error_rate": get_metric_value("system.error.rate", hour_ago.isoformat()),
            "avg_execution_time": get_metric_value(
                "agent.execution.time.avg", hour_ago.isoformat()
            ),
        }

        # Get system health
        health = {
            "cpu_usage": get_latest_metric_value("system.cpu.usage"),
            "memory_usage": get_latest_metric_value("system.memory.usage"),
            "disk_usage": get_latest_metric_value("system.disk.usage"),
            "active_agents": get_latest_metric_value("agent.active.count"),
            "queue_depth": get_latest_metric_value("system.queue.depth"),
        }

        return {
            "timestamp": now.isoformat(),
            "kpis": kpis,
            "health": health,
            "recent_metrics": recent_metrics[:5],
        }
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        return {"timestamp": datetime.utcnow().isoformat(), "error": str(e)}


def get_metric_value(metric_name: str, since: str) -> Optional[float]:
    """Get aggregated metric value since a given time."""
    metrics = get_metrics(metric_name, start_time=since, limit=1000)
    if not metrics:
        return None

    values = [float(m.get("value", 0)) for m in metrics]
    return sum(values) / len(values) if values else None


def get_latest_metric_value(metric_name: str) -> Optional[float]:
    """Get the latest value for a metric."""
    metrics = get_metrics(metric_name, limit=1)
    if metrics:
        return float(metrics[0].get("value", 0))
    return None


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Main Lambda handler for metrics operations.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        API Gateway response
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Get HTTP method and path
    http_method = event.get(
        "httpMethod", event.get("requestContext", {}).get("http", {}).get("method", "GET")
    )
    path = event.get("path", event.get("rawPath", "/metrics"))

    try:
        # Route based on method and path
        if http_method == "POST" and path == "/metrics":
            # Save new metric
            body = validate_metrics_request(event)

            metric_id = save_metric(
                metric_name=body["metric_name"],
                value=body["value"],
                tags=body.get("tags", {}),
                timestamp=body.get("timestamp"),
            )

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "metric_id": metric_id,
                        "status": "saved",
                        "message": "Metric saved successfully",
                    }
                ),
            }

        elif http_method == "GET" and path == "/metrics":
            # Get metrics with optional filters
            params = event.get("queryStringParameters", {}) or {}

            metrics = get_metrics(
                metric_name=params.get("name"),
                start_time=params.get("start"),
                end_time=params.get("end"),
                limit=int(params.get("limit", 100)),
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(metrics, cls=DecimalEncoder),
            }

        elif http_method == "GET" and path == "/metrics/summary":
            # Get metrics summary
            summary = get_metric_summary()

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(summary, cls=DecimalEncoder),
            }

        elif http_method == "GET" and path == "/metrics/statistics":
            # Get metric statistics
            params = event.get("queryStringParameters", {}) or {}

            if "name" not in params:
                raise ValueError("metric name is required")

            stats = get_metric_statistics(
                metric_name=params["name"],
                statistic=params.get("statistic", "Average"),
                period=int(params.get("period", 300)),
                start_time=params.get("start"),
                end_time=params.get("end"),
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(stats, default=str),
            }

        elif http_method == "POST" and path == "/metrics/batch":
            # Save multiple metrics
            body = json.loads(event.get("body", "{}"))
            metrics = body.get("metrics", [])

            if not metrics:
                raise ValueError("metrics array is required")

            saved_ids = []
            for metric in metrics:
                try:
                    metric_id = save_metric(
                        metric_name=metric["metric_name"],
                        value=metric["value"],
                        tags=metric.get("tags", {}),
                        timestamp=metric.get("timestamp"),
                    )
                    saved_ids.append(metric_id)
                except Exception as e:
                    logger.error(f"Failed to save metric: {e}")

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "saved": len(saved_ids),
                        "total": len(metrics),
                        "metric_ids": saved_ids,
                        "message": f"Saved {len(saved_ids)} of {len(metrics)} metrics",
                    }
                ),
            }

        elif http_method == "GET" and path == "/metrics/realtime":
            # Get real-time metrics (last 5 minutes)
            start_time = (datetime.utcnow() - timedelta(minutes=5)).isoformat()

            metrics = get_metrics(start_time=start_time, limit=50)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(metrics, cls=DecimalEncoder),
            }

        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Not found"}),
            }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Internal server error"}),
        }
