"""Lambda handler for agent operations."""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
sqs = boto3.client("sqs")
cloudwatch = boto3.client("cloudwatch")

# Environment variables
AGENTS_TABLE = os.environ.get("AGENTS_TABLE", "t-developer-agents")
EXECUTION_TABLE = os.environ.get("EXECUTION_TABLE", "t-developer-executions")
QUEUE_URL = os.environ.get("AGENT_QUEUE_URL", "")
RESULTS_BUCKET = os.environ.get("RESULTS_BUCKET", "t-developer-results")


@dataclass
class AgentConfig:
    """Agent configuration."""

    name: str
    type: str
    config: dict[str, Any]
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 300


@dataclass
class ExecutionRequest:
    """Agent execution request."""

    agent_id: str
    task: dict[str, Any]
    priority: int = 5
    callback_url: Optional[str] = None


@dataclass
class ExecutionResult:
    """Agent execution result."""

    execution_id: str
    agent_id: str
    status: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    metrics: Optional[dict[str, Any]] = None


def validate_agent_request(event: dict[str, Any]) -> dict[str, Any]:
    """Validate agent request."""
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event

    # Check required fields for different operations
    operation = event.get("pathParameters", {}).get("operation", "execute")

    if operation == "create":
        if "name" not in body or "type" not in body:
            raise ValueError("name and type are required for agent creation")
    elif operation == "execute":
        if "agent_id" not in body or "task" not in body:
            raise ValueError("agent_id and task are required for execution")

    return body


def generate_execution_id() -> str:
    """Generate unique execution ID."""
    from uuid import uuid4

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"exec-{timestamp}-{str(uuid4())[:8]}"


def create_agent(config: AgentConfig) -> str:
    """Create new agent in DynamoDB.

    Args:
        config: Agent configuration

    Returns:
        Agent ID
    """
    from uuid import uuid4

    agent_id = f"agent-{uuid4()!s}"
    table = dynamodb.Table(AGENTS_TABLE)

    try:
        table.put_item(
            Item={
                "agent_id": agent_id,
                "name": config.name,
                "type": config.type,
                "config": config.config,
                "enabled": config.enabled,
                "max_retries": config.max_retries,
                "timeout": config.timeout,
                "status": "idle",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "avg_execution_time": 0,
                    "last_execution": None,
                },
            }
        )
        logger.info(f"Created agent {agent_id} with name {config.name}")
        return agent_id
    except ClientError as e:
        logger.error(f"Failed to create agent: {e}")
        raise


def get_agent(agent_id: str) -> Optional[dict[str, Any]]:
    """Get agent from DynamoDB."""
    table = dynamodb.Table(AGENTS_TABLE)

    try:
        response = table.get_item(Key={"agent_id": agent_id})
        return response.get("Item")
    except ClientError as e:
        logger.error(f"Failed to get agent: {e}")
        return None


def list_agents(filter_type: Optional[str] = None) -> list[dict[str, Any]]:
    """List all agents or filter by type."""
    table = dynamodb.Table(AGENTS_TABLE)

    try:
        if filter_type:
            response = table.scan(
                FilterExpression="#type = :type",
                ExpressionAttributeNames={"#type": "type"},
                ExpressionAttributeValues={":type": filter_type},
            )
        else:
            response = table.scan()

        return response.get("Items", [])
    except ClientError as e:
        logger.error(f"Failed to list agents: {e}")
        return []


def update_agent_status(agent_id: str, status: str, **kwargs) -> None:
    """Update agent status in DynamoDB."""
    table = dynamodb.Table(AGENTS_TABLE)

    update_expr = "SET #status = :status, updated_at = :updated_at"
    expr_values = {":status": status, ":updated_at": datetime.utcnow().isoformat()}
    expr_names = {"#status": "status"}

    # Add additional updates
    for key, value in kwargs.items():
        if key in ["name", "type"]:  # Reserved words
            update_expr += f", #{key} = :{key}"
            expr_names[f"#{key}"] = key
        else:
            update_expr += f", {key} = :{key}"
        expr_values[f":{key}"] = value

    try:
        table.update_item(
            Key={"agent_id": agent_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
        )
    except ClientError as e:
        logger.error(f"Failed to update agent status: {e}")
        raise


def save_execution(execution_id: str, agent_id: str, task: dict[str, Any], status: str) -> None:
    """Save execution record to DynamoDB."""
    table = dynamodb.Table(EXECUTION_TABLE)

    try:
        table.put_item(
            Item={
                "execution_id": execution_id,
                "agent_id": agent_id,
                "task": task,
                "status": status,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        )
    except ClientError as e:
        logger.error(f"Failed to save execution: {e}")
        raise


def queue_agent_task(agent_id: str, execution_id: str, task: dict[str, Any]) -> None:
    """Queue agent task to SQS."""
    if not QUEUE_URL:
        logger.warning("AGENT_QUEUE_URL not configured, skipping queue")
        return

    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(
                {
                    "execution_id": execution_id,
                    "agent_id": agent_id,
                    "task": task,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            MessageAttributes={
                "agent_id": {"DataType": "String", "StringValue": agent_id},
                "execution_id": {"DataType": "String", "StringValue": execution_id},
            },
        )
        logger.info(f"Queued task for agent {agent_id}, execution {execution_id}")
    except ClientError as e:
        logger.error(f"Failed to queue task: {e}")
        raise


def update_agent_metrics(agent_id: str, execution_time: float, success: bool) -> None:
    """Update agent performance metrics."""
    table = dynamodb.Table(AGENTS_TABLE)

    try:
        # Get current metrics
        response = table.get_item(Key={"agent_id": agent_id})
        agent = response.get("Item", {})
        metrics = agent.get(
            "metrics",
            {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "avg_execution_time": 0,
                "last_execution": None,
            },
        )

        # Update metrics
        metrics["total_executions"] += 1
        if success:
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1

        # Update average execution time
        current_avg = metrics.get("avg_execution_time", 0)
        total = metrics["total_executions"]
        metrics["avg_execution_time"] = ((current_avg * (total - 1)) + execution_time) / total
        metrics["last_execution"] = datetime.utcnow().isoformat()

        # Save updated metrics
        table.update_item(
            Key={"agent_id": agent_id},
            UpdateExpression="SET metrics = :metrics",
            ExpressionAttributeValues={":metrics": metrics},
        )

        # Send metrics to CloudWatch
        send_cloudwatch_metrics(agent_id, execution_time, success)

    except ClientError as e:
        logger.error(f"Failed to update agent metrics: {e}")


def send_cloudwatch_metrics(agent_id: str, execution_time: float, success: bool) -> None:
    """Send metrics to CloudWatch."""
    try:
        cloudwatch.put_metric_data(
            Namespace="TDeveloper/Agents",
            MetricData=[
                {
                    "MetricName": "ExecutionTime",
                    "Value": execution_time,
                    "Unit": "Seconds",
                    "Dimensions": [{"Name": "AgentId", "Value": agent_id}],
                },
                {
                    "MetricName": "ExecutionCount",
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [
                        {"Name": "AgentId", "Value": agent_id},
                        {"Name": "Status", "Value": "success" if success else "failure"},
                    ],
                },
            ],
        )
    except ClientError as e:
        logger.error(f"Failed to send CloudWatch metrics: {e}")


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Main Lambda handler for agent operations.

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
    path = event.get("path", event.get("rawPath", "/agents"))

    try:
        # Route based on method and path
        if http_method == "POST" and path == "/agents/create":
            # Create new agent
            body = validate_agent_request(event)
            config = AgentConfig(
                name=body["name"],
                type=body["type"],
                config=body.get("config", {}),
                enabled=body.get("enabled", True),
                max_retries=body.get("max_retries", 3),
                timeout=body.get("timeout", 300),
            )

            agent_id = create_agent(config)

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "agent_id": agent_id,
                        "name": config.name,
                        "type": config.type,
                        "status": "created",
                        "message": f"Agent {config.name} created successfully",
                    }
                ),
            }

        elif http_method == "GET" and path == "/agents":
            # List all agents
            filter_type = (
                event.get("queryStringParameters", {}).get("type")
                if event.get("queryStringParameters")
                else None
            )
            agents = list_agents(filter_type)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(agents, default=str),
            }

        elif http_method == "GET" and "/agents/" in path:
            # Get specific agent
            agent_id = path.split("/")[-1]
            agent = get_agent(agent_id)

            if not agent:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({"error": f"Agent {agent_id} not found"}),
                }

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(agent, default=str),
            }

        elif http_method == "POST" and "/agents/execute" in path:
            # Execute agent task
            body = validate_agent_request(event)
            agent_id = body["agent_id"]
            task = body["task"]

            # Check if agent exists and is enabled
            agent = get_agent(agent_id)
            if not agent:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({"error": f"Agent {agent_id} not found"}),
                }

            if not agent.get("enabled", True):
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({"error": f"Agent {agent_id} is disabled"}),
                }

            # Generate execution ID
            execution_id = generate_execution_id()

            # Save execution record
            save_execution(execution_id, agent_id, task, "queued")

            # Update agent status
            update_agent_status(agent_id, "running")

            # Queue task for processing
            queue_agent_task(agent_id, execution_id, task)

            return {
                "statusCode": 202,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "execution_id": execution_id,
                        "agent_id": agent_id,
                        "status": "queued",
                        "message": "Task queued for execution",
                    }
                ),
            }

        elif http_method == "PUT" and "/agents/" in path:
            # Update agent
            agent_id = path.split("/")[-1]
            body = json.loads(event.get("body", "{}"))

            # Update agent
            update_agent_status(agent_id, body.get("status", "idle"), **body)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "agent_id": agent_id,
                        "status": "updated",
                        "message": "Agent updated successfully",
                    }
                ),
            }

        elif http_method == "DELETE" and "/agents/" in path:
            # Delete agent (soft delete by disabling)
            agent_id = path.split("/")[-1]
            update_agent_status(agent_id, "disabled", enabled=False)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "agent_id": agent_id,
                        "status": "disabled",
                        "message": "Agent disabled successfully",
                    }
                ),
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
