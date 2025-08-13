"""
Technical Analyzer Module
Analyzes technical requirements and constraints
"""

import re
from typing import Any, Dict, List, Optional


class TechnicalAnalyzer:
    """Analyzes technical aspects of requirements"""

    def __init__(self):
        self.tech_keywords = {
            "platforms": [
                "web",
                "mobile",
                "desktop",
                "cloud",
                "ios",
                "android",
                "windows",
                "linux",
                "macos",
            ],
            "frameworks": [
                "react",
                "vue",
                "angular",
                "django",
                "flask",
                "spring",
                "express",
                "fastapi",
                "rails",
            ],
            "languages": [
                "python",
                "javascript",
                "typescript",
                "java",
                "csharp",
                "golang",
                "rust",
                "ruby",
                "php",
            ],
            "databases": [
                "postgresql",
                "mysql",
                "mongodb",
                "redis",
                "elasticsearch",
                "dynamodb",
                "firebase",
            ],
            "cloud": [
                "aws",
                "azure",
                "gcp",
                "heroku",
                "digitalocean",
                "vercel",
                "netlify",
            ],
            "tools": [
                "docker",
                "kubernetes",
                "jenkins",
                "github",
                "gitlab",
                "terraform",
                "ansible",
            ],
        }

        self.architecture_patterns = [
            "microservices",
            "monolithic",
            "serverless",
            "event-driven",
            "layered",
            "hexagonal",
            "mvc",
            "mvvm",
            "clean architecture",
        ]

    async def analyze(self, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical requirements"""

        text = nlp_result.get("original", "").lower()

        # Extract technology mentions
        tech_stack = self._extract_tech_stack(text)

        # Identify architecture pattern
        architecture = self._identify_architecture(text)

        # Extract performance requirements
        performance = self._extract_performance_requirements(text)

        # Identify integration requirements
        integrations = self._identify_integrations(text)

        # Extract deployment requirements
        deployment = self._extract_deployment_requirements(text)

        # Generate technical specifications
        specifications = self._generate_specifications(
            tech_stack, architecture, performance, integrations, deployment
        )

        # Calculate complexity
        complexity = self._calculate_complexity(tech_stack, integrations)

        # Generate recommendations
        recommendations = self._generate_recommendations(tech_stack, architecture)

        return {
            "tech_stack": tech_stack,
            "architecture": architecture,
            "performance": performance,
            "integrations": integrations,
            "deployment": deployment,
            "specifications": specifications,
            "complexity": complexity,
            "recommendations": recommendations,
        }

    def _extract_tech_stack(self, text: str) -> Dict[str, List[str]]:
        """Extract technology stack from text"""
        tech_stack = {}

        for category, keywords in self.tech_keywords.items():
            found = []
            for keyword in keywords:
                if keyword in text:
                    found.append(keyword)

            if found:
                tech_stack[category] = found

        # Set defaults if nothing found
        if not tech_stack:
            tech_stack = {
                "platforms": ["web"],
                "frameworks": ["react"],
                "languages": ["javascript", "python"],
                "databases": ["postgresql"],
            }

        return tech_stack

    def _identify_architecture(self, text: str) -> str:
        """Identify architecture pattern"""
        for pattern in self.architecture_patterns:
            if pattern in text:
                return pattern

        # Default based on other indicators
        if "microservice" in text or "distributed" in text:
            return "microservices"
        elif "serverless" in text or "lambda" in text:
            return "serverless"

        return "layered"  # Default

    def _extract_performance_requirements(self, text: str) -> Dict[str, Any]:
        """Extract performance requirements"""
        performance = {
            "response_time": None,
            "throughput": None,
            "concurrent_users": None,
            "availability": None,
        }

        # Response time
        response_pattern = r"(\d+)\s*(?:ms|milliseconds?|seconds?)\s*(?:response|latency)"
        match = re.search(response_pattern, text)
        if match:
            performance["response_time"] = {
                "value": int(match.group(1)),
                "unit": "ms" if "ms" in match.group(0) else "s",
            }

        # Concurrent users
        users_pattern = r"(\d+)\s*(?:concurrent|simultaneous)\s*users?"
        match = re.search(users_pattern, text)
        if match:
            performance["concurrent_users"] = int(match.group(1))

        # Availability
        availability_pattern = r"(\d+(?:\.\d+)?)\s*%\s*(?:availability|uptime)"
        match = re.search(availability_pattern, text)
        if match:
            performance["availability"] = float(match.group(1))

        return performance

    def _identify_integrations(self, text: str) -> List[str]:
        """Identify required integrations"""
        integrations = []

        integration_keywords = {
            "payment": ["payment", "stripe", "paypal", "checkout"],
            "email": ["email", "sendgrid", "mailgun", "smtp"],
            "sms": ["sms", "twilio", "text message"],
            "storage": ["s3", "blob", "file storage", "cdn"],
            "authentication": ["oauth", "saml", "ldap", "sso"],
            "analytics": ["analytics", "tracking", "google analytics"],
            "maps": ["maps", "geolocation", "google maps", "mapbox"],
        }

        for integration, keywords in integration_keywords.items():
            if any(keyword in text for keyword in keywords):
                integrations.append(integration)

        return integrations

    def _extract_deployment_requirements(self, text: str) -> Dict[str, Any]:
        """Extract deployment requirements"""
        deployment = {
            "environment": [],
            "containerization": False,
            "ci_cd": False,
            "scaling": "manual",
        }

        # Environments
        if "production" in text:
            deployment["environment"].append("production")
        if "staging" in text:
            deployment["environment"].append("staging")
        if "development" in text or "dev" in text:
            deployment["environment"].append("development")

        # Containerization
        if "docker" in text or "container" in text:
            deployment["containerization"] = True

        # CI/CD
        if "ci/cd" in text or "continuous" in text or "pipeline" in text:
            deployment["ci_cd"] = True

        # Scaling
        if "auto-scale" in text or "autoscale" in text:
            deployment["scaling"] = "auto"
        elif "scale" in text:
            deployment["scaling"] = "manual"

        return deployment

    def _generate_specifications(
        self,
        tech_stack: Dict,
        architecture: str,
        performance: Dict,
        integrations: List[str],
        deployment: Dict,
    ) -> Dict[str, Any]:
        """Generate technical specifications"""
        return {
            "architecture": {
                "pattern": architecture,
                "components": self._get_architecture_components(architecture),
            },
            "technology": tech_stack,
            "performance": performance,
            "integrations": integrations,
            "deployment": deployment,
            "security": {
                "authentication": "JWT",
                "authorization": "RBAC",
                "encryption": "TLS 1.3",
            },
        }

    def _get_architecture_components(self, architecture: str) -> List[str]:
        """Get components for architecture pattern"""
        components_map = {
            "microservices": ["API Gateway", "Service Registry", "Message Queue"],
            "serverless": ["Lambda Functions", "API Gateway", "Event Bridge"],
            "layered": ["Presentation Layer", "Business Layer", "Data Layer"],
            "mvc": ["Model", "View", "Controller"],
        }

        return components_map.get(architecture, ["Components"])

    def _calculate_complexity(self, tech_stack: Dict, integrations: List[str]) -> str:
        """Calculate technical complexity"""
        tech_count = sum(len(v) for v in tech_stack.values())
        integration_count = len(integrations)

        total = tech_count + integration_count

        if total > 15:
            return "high"
        elif total > 8:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, tech_stack: Dict, architecture: str) -> List[str]:
        """Generate technical recommendations"""
        recommendations = []

        # Architecture recommendations
        if architecture == "microservices":
            recommendations.append("Implement service discovery and circuit breakers")
            recommendations.append("Use API gateway for routing and authentication")
        elif architecture == "serverless":
            recommendations.append("Optimize cold start performance")
            recommendations.append("Implement proper error handling and retries")

        # Technology recommendations
        if "react" in tech_stack.get("frameworks", []):
            recommendations.append("Use React hooks for state management")
            recommendations.append("Implement code splitting for performance")

        if "postgresql" in tech_stack.get("databases", []):
            recommendations.append("Implement database connection pooling")
            recommendations.append("Use indexes for frequently queried columns")

        # General recommendations
        recommendations.append("Implement comprehensive logging and monitoring")
        recommendations.append("Set up automated testing pipeline")
        recommendations.append("Document API endpoints using OpenAPI")

        return recommendations
