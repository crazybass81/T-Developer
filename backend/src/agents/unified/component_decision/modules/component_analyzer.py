"""
Component Analyzer Module
Analyzes and identifies required components based on requirements
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class ComponentType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    AUTHENTICATION = "authentication"
    MONITORING = "monitoring"
    LOGGING = "logging"
    SECURITY = "security"


class ComponentAnalyzer:
    """Analyzes and identifies required components"""

    def __init__(self):
        self.component_catalog = self._build_component_catalog()
        self.dependency_graph = self._build_dependency_graph()

    async def analyze(
        self, requirements: Dict[str, Any], specifications: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze requirements and identify needed components"""

        components = []

        # Identify core components
        core_components = self._identify_core_components(requirements)
        components.extend(core_components)

        # Identify feature-specific components
        feature_components = self._identify_feature_components(specifications)
        components.extend(feature_components)

        # Identify infrastructure components
        infra_components = self._identify_infrastructure_components(requirements)
        components.extend(infra_components)

        # Resolve dependencies
        components = self._resolve_dependencies(components)

        # Optimize component selection
        components = self._optimize_components(components)

        # Add component specifications
        for component in components:
            component["specification"] = self._generate_component_spec(component)
            component["configuration"] = self._generate_configuration(component)
            component["interfaces"] = self._define_interfaces(component)
            component["metrics"] = self._define_metrics(component)

        return components

    def _identify_core_components(self, requirements: Dict) -> List[Dict]:
        """Identify core system components"""
        components = []

        # Frontend component
        if requirements.get("has_ui", True):
            components.append(
                {
                    "type": ComponentType.FRONTEND.value,
                    "name": "Web Application",
                    "technology": self._select_frontend_tech(requirements),
                    "priority": 10,
                    "required": True,
                }
            )

        # Backend component
        components.append(
            {
                "type": ComponentType.BACKEND.value,
                "name": "API Server",
                "technology": self._select_backend_tech(requirements),
                "priority": 10,
                "required": True,
            }
        )

        # Database component
        components.append(
            {
                "type": ComponentType.DATABASE.value,
                "name": "Primary Database",
                "technology": self._select_database_tech(requirements),
                "priority": 10,
                "required": True,
            }
        )

        # Cache component
        if self._needs_cache(requirements):
            components.append(
                {
                    "type": ComponentType.CACHE.value,
                    "name": "Cache Layer",
                    "technology": "Redis",
                    "priority": 8,
                    "required": False,
                }
            )

        return components

    def _identify_feature_components(self, specifications: Dict) -> List[Dict]:
        """Identify feature-specific components"""
        components = []

        # Authentication component
        if specifications.get("requires_auth", True):
            components.append(
                {
                    "type": ComponentType.AUTHENTICATION.value,
                    "name": "Authentication Service",
                    "technology": self._select_auth_tech(specifications),
                    "priority": 9,
                    "required": True,
                }
            )

        # Message queue for async processing
        if specifications.get("async_processing", False):
            components.append(
                {
                    "type": ComponentType.QUEUE.value,
                    "name": "Message Queue",
                    "technology": self._select_queue_tech(specifications),
                    "priority": 7,
                    "required": True,
                }
            )

        # File storage
        if specifications.get("file_uploads", False):
            components.append(
                {
                    "type": ComponentType.STORAGE.value,
                    "name": "File Storage",
                    "technology": "S3",
                    "priority": 6,
                    "required": True,
                }
            )

        # Search engine
        if specifications.get("search_capability", False):
            components.append(
                {
                    "type": "search",
                    "name": "Search Engine",
                    "technology": "Elasticsearch",
                    "priority": 5,
                    "required": False,
                }
            )

        # Analytics
        if specifications.get("analytics", False):
            components.append(
                {
                    "type": "analytics",
                    "name": "Analytics Service",
                    "technology": "Google Analytics",
                    "priority": 4,
                    "required": False,
                }
            )

        return components

    def _identify_infrastructure_components(self, requirements: Dict) -> List[Dict]:
        """Identify infrastructure components"""
        components = []

        # Load balancer
        if requirements.get("high_availability", False):
            components.append(
                {
                    "type": "load_balancer",
                    "name": "Load Balancer",
                    "technology": "ALB",
                    "priority": 8,
                    "required": True,
                }
            )

        # CDN
        if requirements.get("global_distribution", False):
            components.append(
                {
                    "type": "cdn",
                    "name": "Content Delivery Network",
                    "technology": "CloudFront",
                    "priority": 6,
                    "required": False,
                }
            )

        # Monitoring
        components.append(
            {
                "type": ComponentType.MONITORING.value,
                "name": "Monitoring System",
                "technology": "CloudWatch",
                "priority": 7,
                "required": True,
            }
        )

        # Logging
        components.append(
            {
                "type": ComponentType.LOGGING.value,
                "name": "Centralized Logging",
                "technology": "ELK Stack",
                "priority": 7,
                "required": True,
            }
        )

        # Security components
        security_components = self._identify_security_components(requirements)
        components.extend(security_components)

        return components

    def _identify_security_components(self, requirements: Dict) -> List[Dict]:
        """Identify security components"""
        components = []

        # WAF
        if requirements.get("web_application_firewall", False):
            components.append(
                {
                    "type": ComponentType.SECURITY.value,
                    "name": "Web Application Firewall",
                    "technology": "AWS WAF",
                    "priority": 8,
                    "required": True,
                }
            )

        # Secrets management
        components.append(
            {
                "type": ComponentType.SECURITY.value,
                "name": "Secrets Manager",
                "technology": "AWS Secrets Manager",
                "priority": 9,
                "required": True,
            }
        )

        # Certificate management
        if requirements.get("https", True):
            components.append(
                {
                    "type": ComponentType.SECURITY.value,
                    "name": "Certificate Manager",
                    "technology": "ACM",
                    "priority": 8,
                    "required": True,
                }
            )

        return components

    def _select_frontend_tech(self, requirements: Dict) -> str:
        """Select frontend technology"""
        if requirements.get("spa", True):
            if requirements.get("typescript", False):
                return "React + TypeScript"
            return "React"
        elif requirements.get("ssr", False):
            return "Next.js"
        return "Vue.js"

    def _select_backend_tech(self, requirements: Dict) -> str:
        """Select backend technology"""
        language = requirements.get("backend_language", "python")

        if language == "python":
            if requirements.get("async", False):
                return "FastAPI"
            return "Django"
        elif language == "javascript":
            return "Express.js"
        elif language == "java":
            return "Spring Boot"
        return "FastAPI"

    def _select_database_tech(self, requirements: Dict) -> str:
        """Select database technology"""
        data_type = requirements.get("data_type", "relational")

        if data_type == "relational":
            if requirements.get("scale", "medium") == "large":
                return "PostgreSQL"
            return "MySQL"
        elif data_type == "document":
            return "MongoDB"
        elif data_type == "key_value":
            return "DynamoDB"
        elif data_type == "graph":
            return "Neo4j"
        return "PostgreSQL"

    def _select_auth_tech(self, specifications: Dict) -> str:
        """Select authentication technology"""
        if specifications.get("oauth", False):
            return "Auth0"
        elif specifications.get("social_login", False):
            return "Firebase Auth"
        elif specifications.get("enterprise", False):
            return "Okta"
        return "JWT + Custom"

    def _select_queue_tech(self, specifications: Dict) -> str:
        """Select message queue technology"""
        if specifications.get("event_streaming", False):
            return "Kafka"
        elif specifications.get("simple_queue", True):
            return "RabbitMQ"
        elif specifications.get("aws_native", False):
            return "SQS"
        return "Redis Queue"

    def _needs_cache(self, requirements: Dict) -> bool:
        """Determine if cache is needed"""
        indicators = [
            requirements.get("high_traffic", False),
            requirements.get("performance_critical", False),
            requirements.get("expected_users", 0) > 1000,
            requirements.get("read_heavy", False),
        ]
        return any(indicators)

    def _resolve_dependencies(self, components: List[Dict]) -> List[Dict]:
        """Resolve component dependencies"""
        resolved = []
        component_types = {c["type"] for c in components}

        for component in components:
            resolved.append(component)

            # Add missing dependencies
            dependencies = self.dependency_graph.get(component["type"], [])
            for dep in dependencies:
                if dep not in component_types:
                    resolved.append(self._create_dependency_component(dep))
                    component_types.add(dep)

        return resolved

    def _create_dependency_component(self, dep_type: str) -> Dict:
        """Create a dependency component"""
        catalog_entry = self.component_catalog.get(dep_type, {})

        return {
            "type": dep_type,
            "name": catalog_entry.get("name", dep_type),
            "technology": catalog_entry.get("default_tech", "Generic"),
            "priority": catalog_entry.get("priority", 5),
            "required": True,
            "auto_added": True,
        }

    def _optimize_components(self, components: List[Dict]) -> List[Dict]:
        """Optimize component selection"""
        optimized = []
        seen_types = set()

        # Remove duplicates, keeping highest priority
        sorted_components = sorted(
            components, key=lambda x: x.get("priority", 0), reverse=True
        )

        for component in sorted_components:
            comp_key = f"{component['type']}_{component.get('technology', '')}"
            if comp_key not in seen_types:
                optimized.append(component)
                seen_types.add(comp_key)

        # Merge similar components
        optimized = self._merge_similar_components(optimized)

        return optimized

    def _merge_similar_components(self, components: List[Dict]) -> List[Dict]:
        """Merge similar components"""
        # For now, return as is
        # Could implement logic to merge multiple cache layers, etc.
        return components

    def _generate_component_spec(self, component: Dict) -> Dict:
        """Generate component specification"""
        return {
            "version": self._get_component_version(component),
            "resources": self._estimate_component_resources(component),
            "scaling": self._define_scaling_policy(component),
            "health_check": self._define_health_check(component),
            "backup": self._define_backup_policy(component),
        }

    def _get_component_version(self, component: Dict) -> str:
        """Get component version"""
        version_map = {
            "React": "18.2.0",
            "FastAPI": "0.104.0",
            "PostgreSQL": "15.0",
            "Redis": "7.0",
            "Elasticsearch": "8.10",
        }

        tech = component.get("technology", "")
        for key, version in version_map.items():
            if key in tech:
                return version

        return "latest"

    def _estimate_component_resources(self, component: Dict) -> Dict:
        """Estimate resource requirements"""
        resource_map = {
            ComponentType.FRONTEND.value: {"cpu": "1", "memory": "2GB"},
            ComponentType.BACKEND.value: {"cpu": "2", "memory": "4GB"},
            ComponentType.DATABASE.value: {
                "cpu": "4",
                "memory": "8GB",
                "storage": "100GB",
            },
            ComponentType.CACHE.value: {"cpu": "2", "memory": "4GB"},
            ComponentType.QUEUE.value: {"cpu": "1", "memory": "2GB", "storage": "50GB"},
        }

        return resource_map.get(component["type"], {"cpu": "1", "memory": "2GB"})

    def _define_scaling_policy(self, component: Dict) -> Dict:
        """Define scaling policy"""
        if component["type"] in [
            ComponentType.BACKEND.value,
            ComponentType.FRONTEND.value,
        ]:
            return {
                "type": "horizontal",
                "min_instances": 2,
                "max_instances": 10,
                "target_cpu": 70,
                "target_memory": 80,
            }
        elif component["type"] == ComponentType.DATABASE.value:
            return {"type": "vertical", "read_replicas": True, "max_connections": 1000}

        return {"type": "manual"}

    def _define_health_check(self, component: Dict) -> Dict:
        """Define health check configuration"""
        return {
            "enabled": True,
            "endpoint": "/health",
            "interval": "30s",
            "timeout": "5s",
            "unhealthy_threshold": 3,
            "healthy_threshold": 2,
        }

    def _define_backup_policy(self, component: Dict) -> Dict:
        """Define backup policy"""
        if component["type"] == ComponentType.DATABASE.value:
            return {
                "enabled": True,
                "frequency": "daily",
                "retention": "30 days",
                "type": "automated",
            }
        elif component["type"] == ComponentType.STORAGE.value:
            return {"enabled": True, "versioning": True, "lifecycle": "90 days"}

        return {"enabled": False}

    def _generate_configuration(self, component: Dict) -> Dict:
        """Generate component configuration"""
        base_config = {
            "environment": "production",
            "logging_level": "INFO",
            "monitoring": True,
            "alerts": True,
        }

        # Add component-specific configuration
        if component["type"] == ComponentType.DATABASE.value:
            base_config.update(
                {"connection_pool": 20, "max_connections": 100, "query_timeout": "30s"}
            )
        elif component["type"] == ComponentType.CACHE.value:
            base_config.update(
                {"eviction_policy": "LRU", "max_memory": "4GB", "ttl": 3600}
            )

        return base_config

    def _define_interfaces(self, component: Dict) -> List[Dict]:
        """Define component interfaces"""
        interfaces = []

        if component["type"] == ComponentType.BACKEND.value:
            interfaces.extend(
                [
                    {"type": "REST", "port": 8000, "protocol": "HTTP"},
                    {"type": "GraphQL", "port": 8000, "protocol": "HTTP"},
                    {"type": "WebSocket", "port": 8001, "protocol": "WS"},
                ]
            )
        elif component["type"] == ComponentType.DATABASE.value:
            interfaces.append({"type": "SQL", "port": 5432, "protocol": "TCP"})
        elif component["type"] == ComponentType.CACHE.value:
            interfaces.append({"type": "Redis", "port": 6379, "protocol": "TCP"})

        return interfaces

    def _define_metrics(self, component: Dict) -> List[str]:
        """Define component metrics"""
        base_metrics = ["availability", "latency", "error_rate"]

        component_metrics = {
            ComponentType.BACKEND.value: ["requests_per_second", "response_time"],
            ComponentType.DATABASE.value: ["query_time", "connections", "locks"],
            ComponentType.CACHE.value: ["hit_rate", "evictions", "memory_usage"],
            ComponentType.QUEUE.value: ["queue_depth", "message_rate", "consumer_lag"],
        }

        return base_metrics + component_metrics.get(component["type"], [])

    def _build_component_catalog(self) -> Dict:
        """Build component catalog"""
        return {
            "api_gateway": {
                "name": "API Gateway",
                "default_tech": "Kong",
                "priority": 9,
            },
            "service_mesh": {
                "name": "Service Mesh",
                "default_tech": "Istio",
                "priority": 7,
            },
            "container_registry": {
                "name": "Container Registry",
                "default_tech": "ECR",
                "priority": 6,
            },
        }

    def _build_dependency_graph(self) -> Dict:
        """Build component dependency graph"""
        return {
            ComponentType.BACKEND.value: [ComponentType.DATABASE.value],
            ComponentType.FRONTEND.value: [ComponentType.BACKEND.value],
            ComponentType.QUEUE.value: [ComponentType.DATABASE.value],
            "search": [ComponentType.DATABASE.value],
        }
