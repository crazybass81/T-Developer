"""Lambda handler for evolution system operations."""

import json
import logging
import os
from dataclasses import asdict, dataclass
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
sns = boto3.client("sns")
stepfunctions = boto3.client("stepfunctions")

# Environment variables
EVOLUTION_TABLE = os.environ.get("EVOLUTION_TABLE", "t-developer-evolution")
METRICS_TABLE = os.environ.get("METRICS_TABLE", "t-developer-metrics")
ARTIFACTS_BUCKET = os.environ.get("ARTIFACTS_BUCKET", "t-developer-artifacts")
STATE_MACHINE_ARN = os.environ.get("STATE_MACHINE_ARN", "")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


@dataclass
class EvolutionRequest:
    """Evolution request data structure."""

    target_path: str
    max_cycles: int = 10
    min_improvement: float = 0.01
    safety_checks: bool = True
    dry_run: bool = True
    auto_mode: bool = False
    config: dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class EvolutionResponse:
    """Evolution response data structure."""

    evolution_id: str
    status: str
    message: str
    created_at: str
    metadata: dict[str, Any] = None


def validate_request(event: dict[str, Any]) -> EvolutionRequest:
    """Validate and parse the incoming request.

    Args:
        event: Lambda event object

    Returns:
        EvolutionRequest object

    Raises:
        ValueError: If request is invalid
    """
    body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event

    # Validate required fields
    if "target_path" not in body:
        raise ValueError("target_path is required")

    # Create request object
    return EvolutionRequest(
        target_path=body["target_path"],
        max_cycles=body.get("max_cycles", 10),
        min_improvement=body.get("min_improvement", 0.01),
        safety_checks=body.get("safety_checks", True),
        dry_run=body.get("dry_run", True),
        auto_mode=body.get("auto_mode", False),
        config=body.get("config", {}),
    )


def generate_evolution_id() -> str:
    """Generate a unique evolution ID."""
    from uuid import uuid4

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"evo-{timestamp}-{str(uuid4())[:8]}"


def save_evolution_to_db(evolution_id: str, request: EvolutionRequest, status: str) -> None:
    """Save evolution record to DynamoDB.

    Args:
        evolution_id: Unique evolution ID
        request: Evolution request data
        status: Current status
    """
    table = dynamodb.Table(EVOLUTION_TABLE)

    try:
        table.put_item(
            Item={
                "evolution_id": evolution_id,
                "target_path": request.target_path,
                "status": status,
                "max_cycles": request.max_cycles,
                "min_improvement": str(request.min_improvement),
                "safety_checks": request.safety_checks,
                "dry_run": request.dry_run,
                "auto_mode": request.auto_mode,
                "config": request.config,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "current_cycle": 0,
                "improvements": {"docstring": 0, "coverage": 0, "complexity": 0, "security": 0},
            }
        )
    except ClientError as e:
        logger.error(f"Failed to save evolution to DB: {e}")
        raise


def start_evolution_workflow(evolution_id: str, request: EvolutionRequest) -> dict[str, Any]:
    """Start the evolution Step Functions workflow.

    Args:
        evolution_id: Unique evolution ID
        request: Evolution request data

    Returns:
        Step Functions execution response
    """
    if not STATE_MACHINE_ARN:
        logger.warning("STATE_MACHINE_ARN not configured, skipping workflow start")
        return {"executionArn": "mock-execution-arn"}

    try:
        response = stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=evolution_id,
            input=json.dumps(
                {
                    "evolution_id": evolution_id,
                    "target_path": request.target_path,
                    "max_cycles": request.max_cycles,
                    "min_improvement": request.min_improvement,
                    "safety_checks": request.safety_checks,
                    "dry_run": request.dry_run,
                    "config": request.config,
                }
            ),
        )
        return response
    except ClientError as e:
        logger.error(f"Failed to start Step Functions workflow: {e}")
        raise


def send_notification(evolution_id: str, status: str, message: str) -> None:
    """Send SNS notification about evolution status.

    Args:
        evolution_id: Unique evolution ID
        status: Current status
        message: Status message
    """
    if not SNS_TOPIC_ARN:
        logger.info("SNS_TOPIC_ARN not configured, skipping notification")
        return

    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Evolution {evolution_id} - {status}",
            Message=json.dumps(
                {
                    "evolution_id": evolution_id,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                indent=2,
            ),
            MessageAttributes={
                "evolution_id": {"DataType": "String", "StringValue": evolution_id},
                "status": {"DataType": "String", "StringValue": status},
            },
        )
    except ClientError as e:
        logger.error(f"Failed to send SNS notification: {e}")


def get_evolution_status(evolution_id: str) -> Optional[dict[str, Any]]:
    """Get evolution status from DynamoDB.

    Args:
        evolution_id: Unique evolution ID

    Returns:
        Evolution status data or None if not found
    """
    table = dynamodb.Table(EVOLUTION_TABLE)

    try:
        response = table.get_item(Key={"evolution_id": evolution_id})
        return response.get("Item")
    except ClientError as e:
        logger.error(f"Failed to get evolution status: {e}")
        return None


def update_evolution_status(evolution_id: str, status: str, **kwargs) -> None:
    """Update evolution status in DynamoDB.

    Args:
        evolution_id: Unique evolution ID
        status: New status
        **kwargs: Additional attributes to update
    """
    table = dynamodb.Table(EVOLUTION_TABLE)

    update_expr = "SET #status = :status, updated_at = :updated_at"
    expr_values = {":status": status, ":updated_at": datetime.utcnow().isoformat()}

    # Add additional attributes
    for key, value in kwargs.items():
        update_expr += f", {key} = :{key}"
        expr_values[f":{key}"] = value

    try:
        table.update_item(
            Key={"evolution_id": evolution_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues=expr_values,
        )
    except ClientError as e:
        logger.error(f"Failed to update evolution status: {e}")
        raise


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Main Lambda handler function.

    Args:
        event: Lambda event object
        context: Lambda context object

    Returns:
        API Gateway response
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Get HTTP method and path
    http_method = event.get(
        "httpMethod", event.get("requestContext", {}).get("http", {}).get("method", "POST")
    )
    path = event.get("path", event.get("rawPath", "/evolution"))

    try:
        # Route based on method and path
        if http_method == "POST" and path == "/evolution/start":
            # Start new evolution
            request = validate_request(event)
            evolution_id = generate_evolution_id()

            # Save to database
            save_evolution_to_db(evolution_id, request, "initializing")

            # Start workflow
            workflow_response = start_evolution_workflow(evolution_id, request)

            # Update status
            update_evolution_status(
                evolution_id, "running", execution_arn=workflow_response.get("executionArn")
            )

            # Send notification
            send_notification(
                evolution_id, "started", f"Evolution started for {request.target_path}"
            )

            response = EvolutionResponse(
                evolution_id=evolution_id,
                status="running",
                message="Evolution cycle started successfully",
                created_at=datetime.utcnow().isoformat(),
                metadata={
                    "execution_arn": workflow_response.get("executionArn"),
                    "target_path": request.target_path,
                },
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(asdict(response)),
            }

        elif http_method == "GET" and "/evolution/" in path:
            # Get evolution status
            evolution_id = path.split("/")[-1]
            status_data = get_evolution_status(evolution_id)

            if not status_data:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({"error": f"Evolution {evolution_id} not found"}),
                }

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(status_data, default=str),
            }

        elif http_method == "POST" and "/evolution/stop" in path:
            # Stop evolution
            body = json.loads(event.get("body", "{}"))
            evolution_id = body.get("evolution_id")

            if not evolution_id:
                raise ValueError("evolution_id is required")

            # Update status
            update_evolution_status(
                evolution_id, "stopped", stopped_at=datetime.utcnow().isoformat()
            )

            # Send notification
            send_notification(evolution_id, "stopped", "Evolution manually stopped")

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(
                    {
                        "evolution_id": evolution_id,
                        "status": "stopped",
                        "message": "Evolution stopped successfully",
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
