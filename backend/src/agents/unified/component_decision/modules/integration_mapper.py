"""
Integration Mapper Module
Maps and configures integrations between components
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class IntegrationType(Enum):
    API = "api"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"


class IntegrationMapper:
    """Maps integrations between components"""

    def __init__(self):
        self.integration_patterns = self._build_integration_patterns()

    async def map(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map required integrations"""

        integrations = []

        # Identify required integrations
        required = self._identify_required_integrations(requirements)

        # Map each integration
        for integration_type in required:
            integration = self._create_integration(integration_type, requirements)
            integrations.append(integration)

        # Add inter-component integrations
        component_integrations = self._map_component_integrations(requirements)
        integrations.extend(component_integrations)

        # Generate integration specifications
        for integration in integrations:
            integration["specification"] = self._generate_specification(integration)
            integration["configuration"] = self._generate_configuration(integration)
            integration["security"] = self._define_security(integration)
            integration["monitoring"] = self._define_monitoring(integration)

        return integrations

    def _identify_required_integrations(self, requirements: Dict) -> List[str]:
        """Identify required integrations from requirements"""

        integrations = []
        req_text = str(requirements).lower()

        integration_keywords = {
            "payment": ["payment", "stripe", "paypal"],
            "email": ["email", "smtp", "sendgrid"],
            "sms": ["sms", "twilio", "text"],
            "storage": ["s3", "blob", "file"],
            "analytics": ["analytics", "tracking"],
            "search": ["search", "elasticsearch"],
            "maps": ["maps", "location", "geocoding"],
        }

        for integration, keywords in integration_keywords.items():
            if any(keyword in req_text for keyword in keywords):
                integrations.append(integration)

        return integrations

    def _create_integration(self, integration_type: str, requirements: Dict) -> Dict:
        """Create integration specification"""

        integrations_map = {
            "payment": {
                "name": "Payment Gateway",
                "type": IntegrationType.API.value,
                "provider": "Stripe",
                "protocol": "REST",
                "authentication": "API Key",
            },
            "email": {
                "name": "Email Service",
                "type": IntegrationType.API.value,
                "provider": "SendGrid",
                "protocol": "REST",
                "authentication": "API Key",
            },
            "sms": {
                "name": "SMS Service",
                "type": IntegrationType.API.value,
                "provider": "Twilio",
                "protocol": "REST",
                "authentication": "Auth Token",
            },
            "storage": {
                "name": "Object Storage",
                "type": IntegrationType.API.value,
                "provider": "AWS S3",
                "protocol": "REST",
                "authentication": "IAM",
            },
        }

        base_integration = integrations_map.get(
            integration_type,
            {
                "name": integration_type,
                "type": IntegrationType.API.value,
                "provider": "Generic",
                "protocol": "REST",
                "authentication": "API Key",
            },
        )

        return base_integration

    def _map_component_integrations(self, requirements: Dict) -> List[Dict]:
        """Map integrations between components"""

        integrations = []
        components = requirements.get("components", [])

        for i, comp1 in enumerate(components):
            for comp2 in components[i + 1 :]:
                if self._components_need_integration(comp1, comp2):
                    integration = self._create_component_integration(comp1, comp2)
                    integrations.append(integration)

        return integrations

    def _components_need_integration(self, comp1: Dict, comp2: Dict) -> bool:
        """Check if components need integration"""

        # Simple heuristic
        type1 = comp1.get("type", "")
        type2 = comp2.get("type", "")

        integration_pairs = [
            ("frontend", "backend"),
            ("backend", "database"),
            ("backend", "cache"),
            ("backend", "queue"),
        ]

        return (type1, type2) in integration_pairs or (
            type2,
            type1,
        ) in integration_pairs

    def _create_component_integration(self, comp1: Dict, comp2: Dict) -> Dict:
        """Create integration between components"""

        return {
            "name": f"{comp1['name']} to {comp2['name']}",
            "type": self._determine_integration_type(comp1, comp2),
            "source": comp1["name"],
            "target": comp2["name"],
            "protocol": self._determine_protocol(comp1, comp2),
            "bidirectional": self._is_bidirectional(comp1, comp2),
        }

    def _determine_integration_type(self, comp1: Dict, comp2: Dict) -> str:
        """Determine integration type between components"""

        if "database" in comp2.get("type", ""):
            return IntegrationType.DATABASE.value
        elif "queue" in comp2.get("type", ""):
            return IntegrationType.MESSAGE_QUEUE.value
        else:
            return IntegrationType.API.value

    def _determine_protocol(self, comp1: Dict, comp2: Dict) -> str:
        """Determine communication protocol"""

        if "database" in comp2.get("type", ""):
            return "SQL"
        elif "queue" in comp2.get("type", ""):
            return "AMQP"
        elif "websocket" in str(comp1) or "websocket" in str(comp2):
            return "WebSocket"
        else:
            return "REST"

    def _is_bidirectional(self, comp1: Dict, comp2: Dict) -> bool:
        """Check if integration is bidirectional"""

        return comp1.get("type") == "frontend" and comp2.get("type") == "backend"

    def _generate_specification(self, integration: Dict) -> Dict:
        """Generate integration specification"""

        return {
            "endpoints": self._define_endpoints(integration),
            "data_format": self._define_data_format(integration),
            "error_handling": self._define_error_handling(integration),
            "retry_policy": self._define_retry_policy(integration),
            "rate_limiting": self._define_rate_limiting(integration),
        }

    def _define_endpoints(self, integration: Dict) -> List[Dict]:
        """Define integration endpoints"""

        if integration["type"] == IntegrationType.API.value:
            return [
                {"method": "GET", "path": "/api/v1/resource"},
                {"method": "POST", "path": "/api/v1/resource"},
                {"method": "PUT", "path": "/api/v1/resource/{id}"},
                {"method": "DELETE", "path": "/api/v1/resource/{id}"},
            ]
        return []

    def _define_data_format(self, integration: Dict) -> str:
        """Define data format for integration"""

        if integration.get("protocol") == "REST":
            return "JSON"
        elif integration.get("protocol") == "SOAP":
            return "XML"
        else:
            return "Binary"

    def _define_error_handling(self, integration: Dict) -> Dict:
        """Define error handling strategy"""

        return {
            "strategy": "exponential_backoff",
            "max_retries": 3,
            "timeout": 30,
            "circuit_breaker": True,
        }

    def _define_retry_policy(self, integration: Dict) -> Dict:
        """Define retry policy"""

        return {
            "max_attempts": 3,
            "initial_delay": 1000,
            "max_delay": 10000,
            "multiplier": 2,
        }

    def _define_rate_limiting(self, integration: Dict) -> Dict:
        """Define rate limiting"""

        return {"requests_per_second": 100, "burst_size": 1000, "window": 60}

    def _generate_configuration(self, integration: Dict) -> Dict:
        """Generate integration configuration"""

        config = {
            "connection": {"timeout": 30000, "keep_alive": True, "pool_size": 10},
            "authentication": {
                "type": integration.get("authentication", "API Key"),
                "credentials_source": "environment",
            },
            "logging": {
                "level": "INFO",
                "include_headers": False,
                "include_body": False,
            },
        }

        return config

    def _define_security(self, integration: Dict) -> Dict:
        """Define security requirements"""

        return {
            "encryption": "TLS 1.3",
            "authentication": integration.get("authentication", "API Key"),
            "authorization": "RBAC",
            "data_validation": True,
            "sanitization": True,
        }

    def _define_monitoring(self, integration: Dict) -> Dict:
        """Define monitoring requirements"""

        return {
            "metrics": ["request_count", "error_rate", "latency", "throughput"],
            "alerts": [
                {"metric": "error_rate", "threshold": 0.05},
                {"metric": "latency", "threshold": 1000},
            ],
            "dashboards": ["overview", "errors", "performance"],
        }

    def _build_integration_patterns(self) -> Dict:
        """Build integration patterns catalog"""

        return {
            "synchronous": {
                "description": "Request-response pattern",
                "use_cases": ["API calls", "Database queries"],
                "pros": ["Simple", "Immediate response"],
                "cons": ["Blocking", "Tight coupling"],
            },
            "asynchronous": {
                "description": "Fire-and-forget pattern",
                "use_cases": ["Email sending", "Batch processing"],
                "pros": ["Non-blocking", "Scalable"],
                "cons": ["Complex error handling", "No immediate response"],
            },
            "pub_sub": {
                "description": "Publish-subscribe pattern",
                "use_cases": ["Event notifications", "Real-time updates"],
                "pros": ["Loose coupling", "Scalable"],
                "cons": ["Message ordering", "Delivery guarantees"],
            },
        }
