"""API Validation - Day 9: Optimized"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import jsonschema


class RequestValidator:
    def __init__(self):
        self.schemas = {}
        self.default_max_size = 1024 * 1024

    def validate(self, data: Dict, schema: Dict) -> Dict:
        try:
            jsonschema.validate(instance=data, schema=schema)
            return {"valid": True, "data": data, "timestamp": datetime.utcnow().isoformat()}
        except jsonschema.exceptions.ValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "error_path": list(e.absolute_path),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "timestamp": datetime.utcnow().isoformat(),
            }

    def validate_size(self, data: Any, max_size: Optional[int] = None) -> Dict:
        max_allowed = max_size or self.default_max_size
        try:
            data_size = len(json.dumps(data, default=str))
            if data_size > max_allowed:
                return {
                    "valid": False,
                    "errors": [
                        f"Request size {data_size} bytes exceeds limit of {max_allowed} bytes"
                    ],
                    "size_bytes": data_size,
                    "max_allowed_bytes": max_allowed,
                }
            return {"valid": True, "size_bytes": data_size, "max_allowed_bytes": max_allowed}
        except Exception as e:
            return {"valid": False, "errors": [f"Size validation error: {str(e)}"]}

    def register_schema(self, schema_name: str, schema: Dict):
        self.schemas[schema_name] = schema

    def validate_with_schema(self, data: Dict, schema_name: str) -> Dict:
        if schema_name not in self.schemas:
            return {"valid": False, "errors": [f"Schema '{schema_name}' not found"]}
        return self.validate(data, self.schemas[schema_name])

    def validate_agent_message(self, message: Dict) -> Dict:
        schema = {
            "type": "object",
            "properties": {
                "to_agent": {"type": "string", "minLength": 1},
                "type": {"type": "string", "minLength": 1},
                "payload": {"type": "object"},
            },
            "required": ["to_agent", "type", "payload"],
        }
        return self.validate(message, schema)

    def validate_message(self, message: Dict) -> bool:
        """Validate message format for API Gateway"""
        required_fields = ["type", "payload"]
        for field in required_fields:
            if field not in message:
                return False

        # Type must be string
        if not isinstance(message["type"], str) or len(message["type"].strip()) == 0:
            return False

        # Payload must be dict
        if not isinstance(message["payload"], dict):
            return False

        return True

    def validate_agent_registration(self, agent_info: Dict) -> bool:
        """Validate agent registration data"""
        required_fields = ["agent_id", "name", "capabilities"]

        for field in required_fields:
            if field not in agent_info:
                return False

        # Agent ID validation
        agent_id = agent_info["agent_id"]
        if not isinstance(agent_id, str) or len(agent_id.strip()) == 0 or len(agent_id) > 100:
            return False

        # Name validation
        name = agent_info["name"]
        if not isinstance(name, str) or len(name.strip()) == 0 or len(name) > 200:
            return False

        # Capabilities validation
        capabilities = agent_info["capabilities"]
        if not isinstance(capabilities, list):
            return False

        for capability in capabilities:
            if not isinstance(capability, str) or len(capability.strip()) == 0:
                return False

        # Endpoints validation (optional)
        if "endpoints" in agent_info:
            endpoints = agent_info["endpoints"]
            if not isinstance(endpoints, list):
                return False

            for endpoint in endpoints:
                if not isinstance(endpoint, dict):
                    return False
                if "path" not in endpoint:
                    return False
                if not isinstance(endpoint["path"], str) or len(endpoint["path"].strip()) == 0:
                    return False

        return True

    def validate_endpoint_request(self, request_data: Dict, endpoint_config: Dict) -> bool:
        """Validate endpoint request data"""
        # Basic validation - can be extended based on endpoint config
        if not isinstance(request_data, dict):
            return False

        # Check required fields if specified in config
        required_fields = endpoint_config.get("required_fields", [])
        for field in required_fields:
            if field not in request_data:
                return False

        # Check field types if specified
        field_types = endpoint_config.get("field_types", {})
        for field, expected_type in field_types.items():
            if field in request_data:
                actual_value = request_data[field]
                if expected_type == "string" and not isinstance(actual_value, str):
                    return False
                elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                    return False
                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    return False
                elif expected_type == "array" and not isinstance(actual_value, list):
                    return False
                elif expected_type == "object" and not isinstance(actual_value, dict):
                    return False

        return True

    def sanitize_input(self, data: Any) -> Any:
        if isinstance(data, str):
            patterns = ["<script", "javascript:", "SELECT", "DROP"]
            for pattern in patterns:
                data = data.replace(pattern, "").replace(pattern.lower(), "")
            return data.strip()
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data


class ResponseFormatter:
    def __init__(self):
        self.default_headers = {
            "Content-Type": "application/json",
            "X-API-Version": "1.0.0",
            "X-Timestamp": "",
        }

    def format_success(self, data: Any, message: str = None, status_code: int = 200) -> Dict:
        return {
            "status": "success",
            "status_code": status_code,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": None,
        }

    def format_error(
        self, error_code: str, message: str, details: Any = None, status_code: int = 400
    ) -> Dict:
        return {
            "status": "error",
            "status_code": status_code,
            "error": {"code": error_code, "message": message, "details": details},
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": None,
        }

    def format_validation_error(self, validation_result: Dict) -> Dict:
        return self.format_error(
            error_code="validation_failed",
            message="Request validation failed",
            details=validation_result.get("errors", []),
            status_code=422,
        )

    def format_rate_limit_error(self, rate_limit_result: Dict) -> Dict:
        return self.format_error(
            error_code="rate_limit_exceeded",
            message="Too many requests",
            details={
                "retry_after_seconds": rate_limit_result.get("retry_after_seconds"),
                "client_id": rate_limit_result.get("client_id"),
            },
            status_code=429,
        )

    def format_paginated_response(self, data: List, page: int, per_page: int, total: int) -> Dict:
        total_pages = (total + per_page - 1) // per_page
        return self.format_success(
            {
                "items": data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            }
        )

    def add_headers(self, response: Dict, additional_headers: Dict = None) -> Dict:
        headers = self.default_headers.copy()
        headers["X-Timestamp"] = datetime.utcnow().isoformat()
        if additional_headers:
            headers.update(additional_headers)
        response["headers"] = headers
        return response

    def format_agent_response(
        self, agent_id: str, result: Any, processing_time_ms: float = None
    ) -> Dict:
        response_data = {
            "agent_id": agent_id,
            "result": result,
            "processing_time_ms": processing_time_ms,
        }
        return self.format_success(response_data, "Agent processing completed")

    def format_health_check(self, components: Dict = None) -> Dict:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": 0,
            "version": "1.0.0",
        }
        if components:
            health_data["components"] = components
        return self.format_success(health_data)
