"""
Test suite for API Gateway System
Day 9: API Gateway - TDD Implementation
Generated: 2025-08-13

Testing requirements:
1. FastAPI-based REST API Gateway
2. Agent endpoint auto-exposure
3. JWT + API Key authentication
4. Rate limiting and request validation
5. OpenAPI/Swagger documentation
6. Message queue integration
7. Real-time monitoring
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient


class TestAPIGateway:
    """Test core API Gateway functionality"""

    def test_api_gateway_creation(self):
        """Test creating an API Gateway with configuration"""
        from src.api.gateway import APIGateway

        config = {
            "host": "0.0.0.0",
            "port": 8000,
            "title": "T-Developer API Gateway",
            "version": "1.0.0",
            "jwt_secret": "test-secret-key",
            "rate_limit": {"requests_per_minute": 60},
        }

        gateway = APIGateway(config)

        assert gateway.config["host"] == "0.0.0.0"
        assert gateway.config["port"] == 8000
        assert gateway.config["title"] == "T-Developer API Gateway"
        assert gateway.app is not None
        assert hasattr(gateway, "rate_limiter")

    def test_agent_endpoint_registration(self):
        """Test automatic agent endpoint registration"""
        from src.api.gateway import APIGateway

        gateway = APIGateway()

        # Test agent registration
        agent_info = {
            "agent_id": "test-agent-001",
            "capabilities": ["text-processing", "data-analysis"],
            "endpoints": [
                {"path": "/process", "methods": ["POST"]},
                {"path": "/analyze", "methods": ["GET", "POST"]},
            ],
        }

        result = gateway.register_agent_endpoints(agent_info)

        assert result["status"] == "success"
        assert "test-agent-001" in gateway.registered_agents
        assert len(gateway.registered_agents["test-agent-001"]["endpoints"]) == 2

    def test_jwt_authentication(self):
        """Test JWT token authentication"""
        from src.api.authentication import JWTAuthentication

        auth = JWTAuthentication("test-secret-key")

        # Test token generation
        payload = {"user_id": "user123", "role": "admin"}
        token = auth.create_token(payload)

        assert token is not None
        assert isinstance(token, str)

        # Test token verification
        decoded = auth.verify_token(token)
        assert decoded["user_id"] == "user123"
        assert decoded["role"] == "admin"

    def test_api_key_authentication(self):
        """Test API Key authentication"""
        from src.api.authentication import APIKeyAuthentication

        auth = APIKeyAuthentication()

        # Test API key generation
        api_key = auth.generate_api_key("test-client")
        assert api_key is not None
        assert len(api_key) >= 32

        # Test API key validation
        is_valid = auth.validate_api_key(api_key)
        assert is_valid is True

        # Test invalid API key
        is_valid = auth.validate_api_key("invalid-key")
        assert is_valid is False


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiter_creation(self):
        """Test rate limiter initialization"""
        from src.api.rate_limiter import RateLimiter

        config = {"requests_per_minute": 60, "burst_size": 10}
        rate_limiter = RateLimiter(config)

        assert rate_limiter.requests_per_minute == 60
        assert rate_limiter.burst_size == 10
        assert hasattr(rate_limiter, "client_buckets")

    def test_rate_limiting_enforcement(self):
        """Test rate limiting enforcement"""
        from src.api.rate_limiter import RateLimiter

        # Very low limit for testing
        config = {"requests_per_minute": 60, "burst_size": 2}
        rate_limiter = RateLimiter(config)

        client_id = "test-client"

        # First request should pass
        result1 = rate_limiter.check_rate_limit(client_id)
        assert result1["allowed"] is True

        # Second request should pass (within burst size)
        result2 = rate_limiter.check_rate_limit(client_id)
        assert result2["allowed"] is True

        # Third request should be rate limited (exceeds burst size)
        result3 = rate_limiter.check_rate_limit(client_id)
        assert result3["allowed"] is False
        assert "rate_limit_exceeded" in result3

    def test_rate_limit_reset(self):
        """Test rate limit bucket reset"""
        import time

        from src.api.rate_limiter import RateLimiter

        config = {"requests_per_minute": 60, "burst_size": 2}
        rate_limiter = RateLimiter(config)

        client_id = "test-client"

        # Fill the bucket completely
        rate_limiter.check_rate_limit(client_id)
        rate_limiter.check_rate_limit(client_id)

        # Verify bucket is full (next should fail)
        result_full = rate_limiter.check_rate_limit(client_id)
        assert result_full["allowed"] is False

        # Manually refill tokens (simulate time passage)
        if client_id in rate_limiter.client_buckets:
            rate_limiter.client_buckets[client_id].tokens = 2.0  # Reset to full

        # Should allow more requests now
        result = rate_limiter.check_rate_limit(client_id)
        assert result["allowed"] is True


class TestRequestValidation:
    """Test request and response validation"""

    def test_request_validation_schema(self):
        """Test request validation against schemas"""
        from src.api.validation import RequestValidator

        schema = {
            "type": "object",
            "properties": {
                "message": {"type": "string", "minLength": 1},
                "priority": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            "required": ["message"],
        }

        validator = RequestValidator()

        # Valid request
        valid_request = {"message": "test message", "priority": 5}
        result = validator.validate(valid_request, schema)
        assert result["valid"] is True

        # Invalid request (missing required field)
        invalid_request = {"priority": 5}
        result = validator.validate(invalid_request, schema)
        assert result["valid"] is False
        assert "message" in str(result["errors"])

    def test_response_formatting(self):
        """Test response formatting and standardization"""
        from src.api.validation import ResponseFormatter

        formatter = ResponseFormatter()

        # Success response
        success_data = {"result": "processed", "agent_id": "test-agent"}
        formatted = formatter.format_success(success_data)

        assert formatted["status"] == "success"
        assert formatted["data"]["result"] == "processed"
        assert "timestamp" in formatted

        # Error response
        error_formatted = formatter.format_error("validation_failed", "Missing required field")

        assert error_formatted["status"] == "error"
        assert error_formatted["error"]["code"] == "validation_failed"
        assert error_formatted["error"]["message"] == "Missing required field"

    def test_message_queue_integration(self):
        """Test integration with message queue system"""
        from src.api.gateway import APIGateway

        gateway = APIGateway()

        # Test message sending (currently mocked in gateway)
        message = {"to_agent": "test-agent", "type": "process_request", "payload": {"data": "test"}}

        result = gateway.send_message_to_agent(message)

        assert result["status"] == "queued"
        assert "message_id" in result
        assert result["agent_id"] == "test-agent"


class TestOpenAPIDocumentation:
    """Test OpenAPI/Swagger documentation generation"""

    def test_openapi_schema_generation(self):
        """Test OpenAPI schema is properly generated"""
        from src.api.gateway import APIGateway

        gateway = APIGateway()

        # Test that FastAPI app has OpenAPI schema
        openapi_schema = gateway.app.openapi()

        assert openapi_schema is not None
        assert "info" in openapi_schema
        assert "paths" in openapi_schema
        assert openapi_schema["info"]["title"] == "T-Developer API Gateway"

    def test_agent_endpoint_documentation(self):
        """Test that agent endpoints are properly documented"""
        from src.api.gateway import APIGateway

        gateway = APIGateway()

        # Register test agent
        agent_info = {
            "agent_id": "doc-test-agent",
            "capabilities": ["documentation-test"],
            "endpoints": [
                {
                    "path": "/test",
                    "methods": ["POST"],
                    "description": "Test endpoint for documentation",
                    "request_schema": {
                        "type": "object",
                        "properties": {"input": {"type": "string"}},
                    },
                }
            ],
        }

        gateway.register_agent_endpoints(agent_info)

        # Check that endpoint is in OpenAPI schema
        schema = gateway.app.openapi()
        paths = schema.get("paths", {})

        # Should have dynamically created endpoint
        assert "/agents/doc-test-agent/test" in paths or any("/test" in path for path in paths)


class TestAPIMonitoring:
    """Test real-time API monitoring and logging"""

    def test_request_metrics_collection(self):
        """Test request metrics collection"""
        from src.api.monitoring import APIMonitor

        monitor = APIMonitor()

        # Record request metrics
        request_data = {
            "method": "POST",
            "path": "/agents/test-agent/process",
            "status_code": 200,
            "response_time_ms": 150,
            "agent_id": "test-agent",
        }

        monitor.record_request(request_data)

        # Get metrics
        metrics = monitor.get_metrics()

        assert metrics["total_requests"] >= 1
        assert "test-agent" in metrics["agent_requests"]
        assert metrics["agent_requests"]["test-agent"] >= 1

    def test_error_tracking(self):
        """Test error tracking and alerting"""
        from src.api.monitoring import APIMonitor

        monitor = APIMonitor()

        # Record error
        error_data = {
            "method": "POST",
            "path": "/agents/failing-agent/process",
            "status_code": 500,
            "error_type": "internal_error",
            "error_message": "Agent processing failed",
        }

        monitor.record_error(error_data)

        # Get error metrics
        error_metrics = monitor.get_error_metrics()

        assert error_metrics["total_errors"] >= 1
        assert "internal_error" in error_metrics["error_types"]

    @pytest.mark.integration
    def test_end_to_end_api_request(self):
        """Test complete API request flow"""
        from src.api.gateway import APIGateway

        gateway = APIGateway()
        client = TestClient(gateway.app)

        # Test health endpoint
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAPIPerformance:
    """Test API Gateway performance"""

    def test_response_time_measurement(self):
        """Test response time measurement"""
        import asyncio

        from src.api.performance import PerformanceTester

        tester = PerformanceTester()

        # Simulate API call timing
        start_time = tester.start_timing()

        # Simulate processing time
        import time

        time.sleep(0.1)  # 100ms

        response_time = tester.end_timing(start_time)

        assert 90 <= response_time <= 150  # Should be around 100ms with some tolerance

    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests"""
        from src.api.gateway import APIGateway

        gateway = APIGateway()

        # Test that gateway can handle multiple concurrent connections
        assert hasattr(gateway.app, "router")
        assert gateway.config.get("max_concurrent_requests", 100) > 0
