"""Tests for Metrics Lambda handler."""

import json
import os
import unittest
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import MagicMock, patch

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lambda_handlers.metrics_handler import (
    MetricRequest,
    generate_metric_id,
    handler,
    validate_request,
)


class TestMetricsHandler(unittest.TestCase):
    """Test cases for Metrics Lambda handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_context = MagicMock()
        self.mock_context.request_id = "test-request-123"
        self.mock_context.function_name = "test-metrics-handler"
        self.mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789:function:test"

    def test_validate_request_save_metric(self):
        """Test validation for save metric request."""
        event = {
            "httpMethod": "POST",
            "path": "/metrics",
            "body": json.dumps({
                "metric_name": "test.metric",
                "value": 42.5,
                "tags": {"env": "test"}
            })
        }
        
        request = validate_request(event)
        self.assertIsInstance(request, MetricRequest)
        self.assertEqual(request.action, "save")
        self.assertEqual(request.metric_name, "test.metric")
        self.assertEqual(request.value, 42.5)

    def test_validate_request_get_metrics(self):
        """Test validation for get metrics request."""
        event = {
            "httpMethod": "GET",
            "path": "/metrics",
            "queryStringParameters": {
                "name": "test.metric",
                "start": "2025-08-17T00:00:00Z",
                "limit": "50"
            }
        }
        
        request = validate_request(event)
        self.assertIsInstance(request, MetricRequest)
        self.assertEqual(request.action, "get")
        self.assertEqual(request.metric_name, "test.metric")
        self.assertEqual(request.limit, 50)

    def test_validate_request_get_summary(self):
        """Test validation for get summary request."""
        event = {
            "httpMethod": "GET",
            "path": "/metrics/summary"
        }
        
        request = validate_request(event)
        self.assertIsInstance(request, MetricRequest)
        self.assertEqual(request.action, "summary")

    def test_validate_request_batch_save(self):
        """Test validation for batch save request."""
        event = {
            "httpMethod": "POST",
            "path": "/metrics/batch",
            "body": json.dumps({
                "metrics": [
                    {"metric_name": "metric1", "value": 10},
                    {"metric_name": "metric2", "value": 20}
                ]
            })
        }
        
        request = validate_request(event)
        self.assertIsInstance(request, MetricRequest)
        self.assertEqual(request.action, "batch")
        self.assertEqual(len(request.metrics), 2)

    def test_validate_request_invalid_method(self):
        """Test validation with invalid HTTP method."""
        event = {
            "httpMethod": "DELETE",
            "path": "/metrics"
        }
        
        with self.assertRaises(ValueError) as context:
            validate_request(event)
        self.assertIn("Unsupported", str(context.exception))

    def test_generate_metric_id(self):
        """Test metric ID generation."""
        metric_name = "test.metric"
        metric_id = generate_metric_id(metric_name)
        
        # Check format: metric-{name}-{timestamp}-{random}
        parts = metric_id.split("-")
        self.assertEqual(parts[0], "metric")
        self.assertTrue(parts[-2].isdigit())  # timestamp
        self.assertEqual(len(parts[-1]), 6)  # random string

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_save_metric(self, mock_resource):
        """Test handler for saving a metric."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        event = {
            "httpMethod": "POST",
            "path": "/metrics",
            "body": json.dumps({
                "metric_name": "evolution.cycles",
                "value": 5,
                "tags": {"phase": "testing"}
            })
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("metric_id", body)
        self.assertEqual(body["status"], "saved")
        
        # Verify DynamoDB write
        mock_table.put_item.assert_called_once()

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_get_metrics(self, mock_resource):
        """Test handler for getting metrics."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock query response
        mock_table.query.return_value = {
            "Items": [
                {
                    "metric_id": "metric-123",
                    "metric_name": "test.metric",
                    "value": 10,
                    "timestamp": "2025-08-17T12:00:00Z"
                },
                {
                    "metric_id": "metric-456",
                    "metric_name": "test.metric",
                    "value": 20,
                    "timestamp": "2025-08-17T12:01:00Z"
                }
            ]
        }
        
        event = {
            "httpMethod": "GET",
            "path": "/metrics",
            "queryStringParameters": {
                "name": "test.metric"
            }
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0]["value"], 10)
        
        # Verify DynamoDB query
        mock_table.query.assert_called_once()

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_get_summary(self, mock_resource):
        """Test handler for getting metrics summary."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock scan response for summary
        mock_table.scan.return_value = {
            "Items": [
                {"metric_name": "evolution.cycles", "value": 10},
                {"metric_name": "agent.executions", "value": 100},
                {"metric_name": "improvement.rate", "value": 15.5}
            ]
        }
        
        event = {
            "httpMethod": "GET",
            "path": "/metrics/summary"
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("kpis", body)
        self.assertIn("health", body)
        self.assertIn("timestamp", body)

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_batch_save(self, mock_resource):
        """Test handler for batch saving metrics."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        mock_table.batch_writer.return_value.__enter__ = MagicMock()
        mock_table.batch_writer.return_value.__exit__ = MagicMock()
        
        event = {
            "httpMethod": "POST",
            "path": "/metrics/batch",
            "body": json.dumps({
                "metrics": [
                    {"metric_name": "metric1", "value": 10, "tags": {}},
                    {"metric_name": "metric2", "value": 20, "tags": {}},
                    {"metric_name": "metric3", "value": 30, "tags": {}}
                ]
            })
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["saved_count"], 3)
        self.assertEqual(body["status"], "batch_saved")
        
        # Verify batch writer was used
        mock_table.batch_writer.assert_called_once()

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_invalid_request(self, mock_resource):
        """Test handler with invalid request."""
        event = {
            "httpMethod": "POST",
            "path": "/metrics",
            "body": "invalid json"
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertIn("error", body)

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_database_error(self, mock_resource):
        """Test handler when database operation fails."""
        # Mock DynamoDB to raise error
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        mock_table.put_item.side_effect = Exception("DynamoDB error")
        
        event = {
            "httpMethod": "POST",
            "path": "/metrics",
            "body": json.dumps({
                "metric_name": "test.metric",
                "value": 42
            })
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertIn("error", body)

    def test_metric_request_dataclass(self):
        """Test MetricRequest dataclass."""
        request = MetricRequest(
            action="save",
            metric_name="test.metric",
            value=100.5,
            tags={"env": "prod", "service": "api"},
            timestamp="2025-08-17T12:00:00Z"
        )
        
        self.assertEqual(request.action, "save")
        self.assertEqual(request.metric_name, "test.metric")
        self.assertEqual(request.value, 100.5)
        self.assertEqual(request.tags["env"], "prod")

    @patch("lambda_handlers.metrics_handler.boto3.resource")
    def test_handler_realtime_metrics(self, mock_resource):
        """Test handler for getting real-time metrics."""
        # Mock DynamoDB
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock query response with recent metrics
        now = datetime.utcnow()
        five_min_ago = now - timedelta(minutes=5)
        
        mock_table.scan.return_value = {
            "Items": [
                {
                    "metric_name": "api.latency",
                    "value": 125,
                    "timestamp": now.isoformat() + "Z"
                },
                {
                    "metric_name": "api.requests",
                    "value": 500,
                    "timestamp": (now - timedelta(minutes=1)).isoformat() + "Z"
                }
            ]
        }
        
        event = {
            "httpMethod": "GET",
            "path": "/metrics/realtime"
        }
        
        response = handler(event, self.mock_context)
        
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIsInstance(body, list)
        self.assertTrue(len(body) > 0)


if __name__ == "__main__":
    unittest.main()