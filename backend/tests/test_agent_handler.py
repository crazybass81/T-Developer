"""Tests for Agent Lambda handler."""

import json
import os
import unittest
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, patch

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lambda_handlers.agent_handler import (
    AgentRequest,
    generate_execution_id,
    handler,
    validate_request,
)


class TestAgentHandler(unittest.TestCase):
    """Test cases for Agent Lambda handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_context = MagicMock()
        self.mock_context.request_id = "test-request-123"
        self.mock_context.function_name = "test-agent-handler"
        self.mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789:function:test"

    def test_validate_request_valid(self):
        """Test validation with valid request."""
        event = {
            "body": json.dumps({
                "agent_type": "research",
                "task": {
                    "action": "analyze",
                    "target": "/test/path"
                }
            })
        }
        
        request = validate_request(event)
        self.assertIsInstance(request, AgentRequest)
        self.assertEqual(request.agent_type, "research")
        self.assertEqual(request.task["action"], "analyze")

    def test_validate_request_missing_body(self):
        """Test validation with missing body."""
        event = {}
        
        with self.assertRaises(ValueError) as context:
            validate_request(event)
        self.assertIn("body", str(context.exception))

    def test_validate_request_invalid_json(self):
        """Test validation with invalid JSON."""
        event = {"body": "invalid json"}
        
        with self.assertRaises(ValueError) as context:
            validate_request(event)
        self.assertIn("Invalid JSON", str(context.exception))

    def test_validate_request_missing_agent_type(self):
        """Test validation with missing agent_type."""
        event = {
            "body": json.dumps({
                "task": {"action": "analyze"}
            })
        }
        
        with self.assertRaises(ValueError) as context:
            validate_request(event)
        self.assertIn("agent_type", str(context.exception))

    def test_generate_execution_id(self):
        """Test execution ID generation."""
        agent_type = "research"
        execution_id = generate_execution_id(agent_type)
        
        # Check format: agent-{type}-{timestamp}-{random}
        parts = execution_id.split("-")
        self.assertEqual(parts[0], "agent")
        self.assertEqual(parts[1], agent_type)
        self.assertTrue(parts[2].isdigit())  # timestamp
        self.assertEqual(len(parts[3]), 6)  # random string

    @patch("lambda_handlers.agent_handler.boto3.resource")
    @patch("lambda_handlers.agent_handler.boto3.client")
    def test_handler_success(self, mock_client, mock_resource):
        """Test successful handler execution."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock StepFunctions
        mock_sfn = MagicMock()
        mock_client.return_value = mock_sfn
        mock_sfn.start_execution.return_value = {
            "executionArn": "arn:aws:states:execution:123"
        }
        
        event = {
            "body": json.dumps({
                "agent_type": "research",
                "task": {
                    "action": "analyze",
                    "target": "/test/path"
                }
            })
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("execution_id", body)
        self.assertEqual(body["status"], "started")
        
        # Verify DynamoDB write
        mock_table.put_item.assert_called_once()
        
        # Verify StepFunctions start
        mock_sfn.start_execution.assert_called_once()

    @patch("lambda_handlers.agent_handler.boto3.resource")
    def test_handler_invalid_request(self, mock_resource):
        """Test handler with invalid request."""
        event = {"body": "invalid json"}
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertIn("error", body)

    @patch("lambda_handlers.agent_handler.boto3.resource")
    @patch("lambda_handlers.agent_handler.boto3.client")
    def test_handler_stepfunctions_error(self, mock_client, mock_resource):
        """Test handler when StepFunctions fails."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock StepFunctions to raise error
        mock_sfn = MagicMock()
        mock_client.return_value = mock_sfn
        mock_sfn.start_execution.side_effect = Exception("StepFunctions error")
        
        event = {
            "body": json.dumps({
                "agent_type": "research",
                "task": {"action": "analyze"}
            })
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertIn("error", body)

    def test_agent_request_dataclass(self):
        """Test AgentRequest dataclass."""
        request = AgentRequest(
            agent_type="planner",
            task={"action": "plan", "target": "/path"},
            config={"timeout": 300}
        )
        
        self.assertEqual(request.agent_type, "planner")
        self.assertEqual(request.task["action"], "plan")
        self.assertEqual(request.config["timeout"], 300)

    @patch("lambda_handlers.agent_handler.boto3.resource")
    @patch("lambda_handlers.agent_handler.boto3.client")
    def test_handler_with_optional_config(self, mock_client, mock_resource):
        """Test handler with optional configuration."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock StepFunctions
        mock_sfn = MagicMock()
        mock_client.return_value = mock_sfn
        mock_sfn.start_execution.return_value = {
            "executionArn": "arn:aws:states:execution:123"
        }
        
        event = {
            "body": json.dumps({
                "agent_type": "evaluator",
                "task": {"action": "evaluate"},
                "config": {
                    "timeout": 600,
                    "retry_count": 5
                },
                "async_mode": False
            })
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("execution_id", body)
        
        # Verify config was passed to StepFunctions
        call_args = mock_sfn.start_execution.call_args
        input_data = json.loads(call_args[1]["input"])
        self.assertEqual(input_data["config"]["timeout"], 600)


if __name__ == "__main__":
    unittest.main()