"""
Technology Stack Builder Module
Builds comprehensive technology stack based on requirements
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class TechCategory(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGING = "messaging"
    SEARCH = "search"
    MONITORING = "monitoring"
    INFRASTRUCTURE = "infrastructure"
    CI_CD = "ci_cd"
    SECURITY = "security"


class TechnologyStackBuilder:
    """Builds optimal technology stack"""

    def __init__(self):
        self.tech_catalog = self._build_tech_catalog()
        self.compatibility_matrix = self._build_compatibility_matrix()

    async def build(
        self, requirements: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build technology stack based on requirements"""

        stack = {}

        # Select frontend technologies
        stack["frontend"] = self._select_frontend_stack(requirements, constraints)

        # Select backend technologies
        stack["backend"] = self._select_backend_stack(requirements, constraints)

        # Select database technologies
        stack["database"] = self._select_database_stack(requirements, constraints)

        # Select infrastructure technologies
        stack["infrastructure"] = self._select_infrastructure_stack(requirements, constraints)

        # Select supporting technologies
        stack["supporting"] = self._select_supporting_stack(requirements, constraints)

        # Validate compatibility
        stack = self._ensure_compatibility(stack)

        # Add version information
        stack = self._add_versions(stack)

        # Generate deployment configuration
        stack["deployment"] = self._generate_deployment_config(stack)

        # Calculate complexity and cost
        stack["metrics"] = {
            "complexity": self._calculate_complexity(stack),
            "estimated_cost": self._estimate_cost(stack),
            "learning_curve": self._assess_learning_curve(stack),
        }

        return stack

    def _select_frontend_stack(self, requirements: Dict, constraints: Dict) -> Dict:
        """Select frontend technology stack"""

        stack = {
            "framework": self._select_frontend_framework(requirements),
            "language": "TypeScript" if requirements.get("type_safety", True) else "JavaScript",
            "styling": self._select_styling_solution(requirements),
            "state_management": self._select_state_management(requirements),
            "build_tool": self._select_build_tool(requirements),
            "testing": {
                "unit": "Jest",
                "integration": "React Testing Library",
                "e2e": "Playwright",
            },
            "libraries": self._select_frontend_libraries(requirements),
        }

        return stack

    def _select_backend_stack(self, requirements: Dict, constraints: Dict) -> Dict:
        """Select backend technology stack"""

        language = self._select_backend_language(requirements, constraints)

        stack = {
            "language": language,
            "framework": self._select_backend_framework(language, requirements),
            "api_style": self._select_api_style(requirements),
            "authentication": self._select_auth_solution(requirements),
            "validation": self._select_validation_library(language),
            "orm": self._select_orm(language, requirements),
            "testing": self._select_backend_testing(language),
            "libraries": self._select_backend_libraries(language, requirements),
        }

        return stack

    def _select_database_stack(self, requirements: Dict, constraints: Dict) -> Dict:
        """Select database technology stack"""

        primary_db = self._select_primary_database(requirements)

        stack = {
            "primary": primary_db,
            "cache": self._select_cache_solution(requirements),
            "search": self._select_search_engine(requirements)
            if requirements.get("search_required")
            else None,
            "time_series": "InfluxDB" if requirements.get("metrics_storage") else None,
            "graph": "Neo4j" if requirements.get("graph_data") else None,
            "migrations": self._select_migration_tool(primary_db),
            "backup": self._select_backup_solution(primary_db),
        }

        # Remove None values
        stack = {k: v for k, v in stack.items() if v is not None}

        return stack

    def _select_infrastructure_stack(self, requirements: Dict, constraints: Dict) -> Dict:
        """Select infrastructure technology stack"""

        cloud_provider = self._select_cloud_provider(constraints)

        stack = {
            "cloud": cloud_provider,
            "container": "Docker",
            "orchestration": self._select_orchestration(requirements, cloud_provider),
            "ci_cd": self._select_ci_cd_tools(constraints),
            "monitoring": self._select_monitoring_stack(requirements),
            "logging": self._select_logging_stack(requirements),
            "security": self._select_security_tools(requirements),
            "cdn": self._select_cdn(requirements, cloud_provider),
            "load_balancer": self._select_load_balancer(cloud_provider),
            "service_mesh": "Istio" if requirements.get("microservices") else None,
        }

        # Remove None values
        stack = {k: v for k, v in stack.items() if v is not None}

        return stack

    def _select_supporting_stack(self, requirements: Dict, constraints: Dict) -> Dict:
        """Select supporting technologies"""

        stack = {
            "message_queue": self._select_message_queue(requirements),
            "email": "SendGrid" if requirements.get("email_required") else None,
            "sms": "Twilio" if requirements.get("sms_required") else None,
            "payment": self._select_payment_processor(requirements),
            "storage": self._select_storage_solution(requirements),
            "analytics": self._select_analytics_tools(requirements),
            "error_tracking": "Sentry",
            "performance": "New Relic" if requirements.get("apm_required") else None,
        }

        # Remove None values
        stack = {k: v for k, v in stack.items() if v is not None}

        return stack

    def _select_frontend_framework(self, requirements: Dict) -> str:
        """Select frontend framework"""

        if requirements.get("spa", True):
            if requirements.get("ecosystem", "") == "react":
                return "React"
            elif requirements.get("ecosystem", "") == "vue":
                return "Vue.js"
            elif requirements.get("ecosystem", "") == "angular":
                return "Angular"
            else:
                # Default based on requirements
                if requirements.get("enterprise"):
                    return "Angular"
                elif requirements.get("rapid_development"):
                    return "Vue.js"
                else:
                    return "React"
        elif requirements.get("ssr"):
            return "Next.js"
        elif requirements.get("static_site"):
            return "Gatsby"
        else:
            return "React"

    def _select_styling_solution(self, requirements: Dict) -> str:
        """Select styling solution"""

        if requirements.get("design_system"):
            return "Material-UI"
        elif requirements.get("utility_first"):
            return "Tailwind CSS"
        elif requirements.get("css_in_js"):
            return "Styled Components"
        else:
            return "CSS Modules"

    def _select_state_management(self, requirements: Dict) -> str:
        """Select state management solution"""

        complexity = requirements.get("state_complexity", "medium")

        if complexity == "simple":
            return "Context API"
        elif complexity == "medium":
            return "Zustand"
        else:
            return "Redux Toolkit"

    def _select_build_tool(self, requirements: Dict) -> str:
        """Select build tool"""

        if requirements.get("modern_build"):
            return "Vite"
        elif requirements.get("webpack_required"):
            return "Webpack"
        else:
            return "Vite"

    def _select_frontend_libraries(self, requirements: Dict) -> List[str]:
        """Select frontend libraries"""

        libraries = ["Axios", "React Router"]

        if requirements.get("forms"):
            libraries.append("React Hook Form")
        if requirements.get("animations"):
            libraries.append("Framer Motion")
        if requirements.get("charts"):
            libraries.append("Recharts")
        if requirements.get("tables"):
            libraries.append("React Table")

        return libraries

    def _select_backend_language(self, requirements: Dict, constraints: Dict) -> str:
        """Select backend programming language"""

        preferred = constraints.get("preferred_language")
        if preferred:
            return preferred

        # Select based on requirements
        if requirements.get("machine_learning"):
            return "Python"
        elif requirements.get("real_time"):
            return "Go"
        elif requirements.get("enterprise"):
            return "Java"
        elif requirements.get("rapid_development"):
            return "Python"
        else:
            return "Python"  # Default

    def _select_backend_framework(self, language: str, requirements: Dict) -> str:
        """Select backend framework based on language"""

        frameworks = {
            "Python": {
                "async": "FastAPI",
                "full_featured": "Django",
                "lightweight": "Flask",
            },
            "JavaScript": {
                "default": "Express.js",
                "full_featured": "NestJS",
                "lightweight": "Fastify",
            },
            "Go": {"default": "Gin", "full_featured": "Echo", "lightweight": "Fiber"},
            "Java": {
                "default": "Spring Boot",
                "reactive": "Spring WebFlux",
                "lightweight": "Micronaut",
            },
        }

        lang_frameworks = frameworks.get(language, {})

        if requirements.get("async"):
            return lang_frameworks.get("async", lang_frameworks.get("default", "Express.js"))
        elif requirements.get("full_featured"):
            return lang_frameworks.get(
                "full_featured", lang_frameworks.get("default", "Express.js")
            )
        else:
            return lang_frameworks.get("default", "Express.js")

    def _select_api_style(self, requirements: Dict) -> str:
        """Select API style"""

        if requirements.get("graphql"):
            return "GraphQL"
        elif requirements.get("grpc"):
            return "gRPC"
        else:
            return "REST"

    def _select_auth_solution(self, requirements: Dict) -> str:
        """Select authentication solution"""

        if requirements.get("oauth"):
            return "Auth0"
        elif requirements.get("enterprise_sso"):
            return "Okta"
        elif requirements.get("simple_auth"):
            return "JWT"
        else:
            return "JWT"

    def _select_validation_library(self, language: str) -> str:
        """Select validation library"""

        libraries = {
            "Python": "Pydantic",
            "JavaScript": "Joi",
            "Go": "Validator",
            "Java": "Hibernate Validator",
        }

        return libraries.get(language, "Custom")

    def _select_orm(self, language: str, requirements: Dict) -> str:
        """Select ORM"""

        orms = {
            "Python": "SQLAlchemy" if requirements.get("complex_queries") else "Django ORM",
            "JavaScript": "Prisma" if requirements.get("type_safe") else "Sequelize",
            "Go": "GORM",
            "Java": "Hibernate",
        }

        return orms.get(language, "None")

    def _select_backend_testing(self, language: str) -> Dict:
        """Select backend testing tools"""

        testing = {
            "Python": {
                "unit": "pytest",
                "integration": "pytest",
                "mocking": "pytest-mock",
            },
            "JavaScript": {
                "unit": "Jest",
                "integration": "Supertest",
                "mocking": "Sinon",
            },
            "Go": {"unit": "testing", "integration": "testify", "mocking": "gomock"},
            "Java": {
                "unit": "JUnit",
                "integration": "Spring Test",
                "mocking": "Mockito",
            },
        }

        return testing.get(language, {"unit": "Default", "integration": "Default"})

    def _select_backend_libraries(self, language: str, requirements: Dict) -> List[str]:
        """Select backend libraries"""

        libraries = []

        if language == "Python":
            libraries.extend(["requests", "celery", "python-dotenv"])
        elif language == "JavaScript":
            libraries.extend(["axios", "bull", "dotenv"])

        return libraries

    def _select_primary_database(self, requirements: Dict) -> str:
        """Select primary database"""

        data_type = requirements.get("data_type", "relational")

        if data_type == "relational":
            if requirements.get("enterprise"):
                return "PostgreSQL"
            else:
                return "MySQL"
        elif data_type == "document":
            return "MongoDB"
        elif data_type == "key_value":
            return "DynamoDB"
        elif data_type == "graph":
            return "Neo4j"
        else:
            return "PostgreSQL"

    def _select_cache_solution(self, requirements: Dict) -> str:
        """Select cache solution"""

        if requirements.get("distributed_cache"):
            return "Redis Cluster"
        elif requirements.get("simple_cache"):
            return "Memcached"
        else:
            return "Redis"

    def _select_search_engine(self, requirements: Dict) -> str:
        """Select search engine"""

        if requirements.get("full_text_search"):
            return "Elasticsearch"
        elif requirements.get("simple_search"):
            return "PostgreSQL Full Text"
        else:
            return "Elasticsearch"

    def _select_migration_tool(self, database: str) -> str:
        """Select database migration tool"""

        tools = {
            "PostgreSQL": "Flyway",
            "MySQL": "Liquibase",
            "MongoDB": "Mongock",
            "DynamoDB": "AWS SDK",
        }

        return tools.get(database, "Custom")

    def _select_backup_solution(self, database: str) -> str:
        """Select backup solution"""

        if "AWS" in database or database == "DynamoDB":
            return "AWS Backup"
        else:
            return "Automated Snapshots"

    def _select_cloud_provider(self, constraints: Dict) -> str:
        """Select cloud provider"""

        preferred = constraints.get("cloud_provider")
        if preferred:
            return preferred

        # Default based on common usage
        return "AWS"

    def _select_orchestration(self, requirements: Dict, cloud: str) -> str:
        """Select container orchestration"""

        if requirements.get("serverless"):
            return f"{cloud} Lambda"
        elif requirements.get("kubernetes"):
            if cloud == "AWS":
                return "EKS"
            elif cloud == "Azure":
                return "AKS"
            elif cloud == "GCP":
                return "GKE"
            else:
                return "Kubernetes"
        elif cloud == "AWS":
            return "ECS Fargate"
        else:
            return "Docker Compose"

    def _select_ci_cd_tools(self, constraints: Dict) -> Dict:
        """Select CI/CD tools"""

        if constraints.get("github"):
            return {
                "ci": "GitHub Actions",
                "cd": "GitHub Actions",
                "registry": "GitHub Container Registry",
            }
        else:
            return {"ci": "Jenkins", "cd": "ArgoCD", "registry": "Docker Hub"}

    def _select_monitoring_stack(self, requirements: Dict) -> Dict:
        """Select monitoring stack"""

        if requirements.get("cloud_native"):
            return {
                "metrics": "CloudWatch",
                "traces": "X-Ray",
                "logs": "CloudWatch Logs",
            }
        else:
            return {
                "metrics": "Prometheus",
                "traces": "Jaeger",
                "logs": "ELK Stack",
                "visualization": "Grafana",
            }

    def _select_logging_stack(self, requirements: Dict) -> Dict:
        """Select logging stack"""

        return {
            "aggregation": "Fluentd",
            "storage": "Elasticsearch",
            "visualization": "Kibana",
        }

    def _select_security_tools(self, requirements: Dict) -> Dict:
        """Select security tools"""

        return {
            "secrets": "HashiCorp Vault",
            "scanning": "Snyk",
            "sast": "SonarQube",
            "dast": "OWASP ZAP",
        }

    def _select_cdn(self, requirements: Dict, cloud: str) -> str:
        """Select CDN"""

        if cloud == "AWS":
            return "CloudFront"
        elif cloud == "Azure":
            return "Azure CDN"
        else:
            return "Cloudflare"

    def _select_load_balancer(self, cloud: str) -> str:
        """Select load balancer"""

        if cloud == "AWS":
            return "Application Load Balancer"
        elif cloud == "Azure":
            return "Azure Load Balancer"
        else:
            return "Nginx"

    def _select_message_queue(self, requirements: Dict) -> str:
        """Select message queue"""

        if requirements.get("event_streaming"):
            return "Apache Kafka"
        elif requirements.get("simple_queue"):
            return "RabbitMQ"
        elif requirements.get("cloud_native"):
            return "AWS SQS"
        else:
            return "Redis Queue"

    def _select_payment_processor(self, requirements: Dict) -> str:
        """Select payment processor"""

        if not requirements.get("payments"):
            return None

        if requirements.get("international"):
            return "Stripe"
        elif requirements.get("subscriptions"):
            return "Stripe"
        else:
            return "PayPal"

    def _select_storage_solution(self, requirements: Dict) -> str:
        """Select storage solution"""

        if requirements.get("file_storage"):
            return "AWS S3"
        return None

    def _select_analytics_tools(self, requirements: Dict) -> List[str]:
        """Select analytics tools"""

        tools = []

        if requirements.get("web_analytics"):
            tools.append("Google Analytics")
        if requirements.get("product_analytics"):
            tools.append("Mixpanel")
        if requirements.get("business_intelligence"):
            tools.append("Tableau")

        return tools if tools else None

    def _ensure_compatibility(self, stack: Dict) -> Dict:
        """Ensure technology compatibility"""

        # Check and fix incompatibilities
        # This is a simplified version

        return stack

    def _add_versions(self, stack: Dict) -> Dict:
        """Add version information"""

        versions = {
            "React": "18.2.0",
            "Vue.js": "3.3.0",
            "Angular": "16.0.0",
            "FastAPI": "0.104.0",
            "Django": "4.2.0",
            "PostgreSQL": "15.0",
            "Redis": "7.0",
            "Docker": "24.0",
        }

        # Add versions to stack components
        for category, components in stack.items():
            if isinstance(components, dict):
                for key, value in components.items():
                    if isinstance(value, str) and value in versions:
                        components[key] = {"name": value, "version": versions[value]}

        return stack

    def _generate_deployment_config(self, stack: Dict) -> Dict:
        """Generate deployment configuration"""

        return {
            "containerization": "Docker",
            "orchestration": stack.get("infrastructure", {}).get("orchestration", "Docker Compose"),
            "environments": ["development", "staging", "production"],
            "deployment_strategy": "Blue-Green",
            "rollback": "Automatic",
        }

    def _calculate_complexity(self, stack: Dict) -> float:
        """Calculate stack complexity"""

        total_components = sum(
            len(v) if isinstance(v, (list, dict)) else 1 for v in stack.values() if v is not None
        )

        return min(total_components * 0.1, 10.0)

    def _estimate_cost(self, stack: Dict) -> Dict:
        """Estimate monthly cost"""

        base_costs = {
            "AWS": 500,
            "Azure": 450,
            "GCP": 480,
            "Kubernetes": 300,
            "Database": 200,
            "Cache": 50,
            "CDN": 100,
            "Monitoring": 150,
        }

        monthly_cost = 0
        for key, cost in base_costs.items():
            if key.lower() in str(stack).lower():
                monthly_cost += cost

        return {"monthly": monthly_cost, "yearly": monthly_cost * 12, "currency": "USD"}

    def _assess_learning_curve(self, stack: Dict) -> str:
        """Assess learning curve for the stack"""

        complexity = self._calculate_complexity(stack)

        if complexity < 3:
            return "Low"
        elif complexity < 6:
            return "Medium"
        else:
            return "High"

    def _build_tech_catalog(self) -> Dict:
        """Build technology catalog"""

        return {
            "frontend_frameworks": ["React", "Vue.js", "Angular", "Svelte"],
            "backend_frameworks": ["Express", "FastAPI", "Django", "Spring Boot"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "DynamoDB"],
            "cache": ["Redis", "Memcached", "Hazelcast"],
            "message_queues": ["RabbitMQ", "Kafka", "SQS", "Redis Queue"],
            "cloud_providers": ["AWS", "Azure", "GCP", "DigitalOcean"],
        }

    def _build_compatibility_matrix(self) -> Dict:
        """Build technology compatibility matrix"""

        return {
            "React": ["Express", "FastAPI", "Django"],
            "Angular": ["Spring Boot", "Express", ".NET Core"],
            "PostgreSQL": ["SQLAlchemy", "Prisma", "Hibernate"],
            "MongoDB": ["Mongoose", "PyMongo", "Spring Data"],
        }
