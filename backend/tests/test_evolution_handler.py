"""Unit tests for Evolution Lambda handler."""

import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Set environment variables before importing handler
os.environ["EVOLUTION_TABLE"] = "test-evolution"
os.environ["METRICS_TABLE"] = "test-metrics"
os.environ["ARTIFACTS_BUCKET"] = "test-artifacts"
os.environ["STATE_MACHINE_ARN"] = "arn:aws:states:test:123456789012:stateMachine:test"
os.environ["SNS_TOPIC_ARN"] = "arn:aws:sns:test:123456789012:test-topic"

# Import after setting environment variables
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../lambda_handlers")))
from evolution_handler import (
    EvolutionRequest,
    generate_evolution_id,
    handler,
    validate_request,
)


class TestEvolutionHandler:
    """Test suite for evolution handler."""

    def test_validate_request_valid(self):
        """Test validation with valid request."""
        event = {
            "body": json.dumps(
                {
                    "target_path": "/test/path",
                    "max_cycles": 5,
                    "min_improvement": 0.05,
                    "safety_checks": True,
                    "dry_run": False,
                }
            )
        }
        request = validate_request(event)
        assert request.target_path == "/test/path"
        assert request.max_cycles == 5
        assert request.min_improvement == 0.05
        assert request.safety_checks is True
        assert request.dry_run is False

    def test_validate_request_missing_target_path(self):
        """Test validation with missing target_path."""
        event = {"body": json.dumps({"max_cycles": 5})}
        with pytest.raises(ValueError) as exc_info:
            validate_request(event)
        assert "target_path is required" in str(exc_info.value)

    def test_validate_request_defaults(self):
        """Test validation with default values."""
        event = {"body": json.dumps({"target_path": "/test/path"})}
        request = validate_request(event)
        assert request.target_path == "/test/path"
        assert request.max_cycles == 10
        assert request.min_improvement == 0.01
        assert request.safety_checks is True
        assert request.dry_run is True
        assert request.auto_mode is False

    def test_generate_evolution_id(self):
        """Test evolution ID generation."""
        evolution_id = generate_evolution_id()
        assert evolution_id.startswith("evo-")
        assert len(evolution_id) > 20
        # Test uniqueness
        id2 = generate_evolution_id()
        assert evolution_id != id2

    @patch("evolution_handler.dynamodb")
    @patch("evolution_handler.stepfunctions")
    @patch("evolution_handler.sns")
    def test_handler_start_evolution(self, mock_sns, mock_sf, mock_dynamodb):
        """Test starting a new evolution."""
        # Setup mocks
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_sf.start_execution.return_value = {"executionArn": "test-arn"}

        event = {
            "httpMethod": "POST",
            "path": "/evolution/start",
            "body": json.dumps({"target_path": "/test/path", "max_cycles": 5}),
        }

        context = MagicMock()
        response = handler(event, context)

        # Assertions
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "running"
        assert body["message"] == "Evolution cycle started successfully"
        assert "evolution_id" in body

        # Verify DynamoDB calls
        assert mock_table.put_item.called
        assert mock_table.update_item.called

        # Verify Step Functions call
        assert mock_sf.start_execution.called

        # Verify SNS call
        assert mock_sns.publish.called

    @patch("evolution_handler.dynamodb")
    def test_handler_get_evolution_status(self, mock_dynamodb):
        """Test getting evolution status."""
        # Setup mock
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            "Item": {
                "evolution_id": "evo-test-123",
                "status": "running",
                "target_path": "/test/path",
                "created_at": datetime.utcnow().isoformat(),
            }
        }

        event = {"httpMethod": "GET", "path": "/evolution/evo-test-123"}

        context = MagicMock()
        response = handler(event, context)

        # Assertions
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["evolution_id"] == "evo-test-123"
        assert body["status"] == "running"

    @patch("evolution_handler.dynamodb")
    def test_handler_evolution_not_found(self, mock_dynamodb):
        """Test getting non-existent evolution."""
        # Setup mock
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {}

        event = {"httpMethod": "GET", "path": "/evolution/non-existent"}

        context = MagicMock()
        response = handler(event, context)

        # Assertions
        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert "not found" in body["error"]

    @patch("evolution_handler.dynamodb")
    @patch("evolution_handler.sns")
    def test_handler_stop_evolution(self, mock_sns, mock_dynamodb):
        """Test stopping an evolution."""
        # Setup mock
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table

        event = {
            "httpMethod": "POST",
            "path": "/evolution/stop",
            "body": json.dumps({"evolution_id": "evo-test-123"}),
        }

        context = MagicMock()
        response = handler(event, context)

        # Assertions
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "stopped"
        assert body["message"] == "Evolution stopped successfully"

        # Verify DynamoDB update
        assert mock_table.update_item.called

        # Verify SNS notification
        assert mock_sns.publish.called

    def test_handler_invalid_method(self):
        """Test handler with invalid HTTP method."""
        event = {"httpMethod": "DELETE", "path": "/evolution/test"}

        context = MagicMock()
        response = handler(event, context)

        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] == "Not found"

    def test_handler_validation_error(self):
        """Test handler with validation error."""
        event = {
            "httpMethod": "POST",
            "path": "/evolution/start",
            "body": json.dumps({}),  # Missing target_path
        }

        context = MagicMock()
        response = handler(event, context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "target_path is required" in body["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])