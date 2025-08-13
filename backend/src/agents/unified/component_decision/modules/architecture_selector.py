"""
Architecture Selector Module
Selects the best architecture pattern based on requirements
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class ArchitectureType(Enum):
    MONOLITHIC = "monolithic"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CQRS = "cqrs"
    SAGA = "saga"


class ArchitectureSelector:
    """Selects optimal architecture pattern"""

    def __init__(self):
        self.architecture_criteria = {
            ArchitectureType.MICROSERVICES: {
                "indicators": ["distributed", "scalable", "independent", "multi-team"],
                "min_services": 5,
                "complexity": "high",
                "team_size": 10,
                "benefits": [
                    "Independent deployment",
                    "Technology diversity",
                    "Fault isolation",
                ],
                "drawbacks": [
                    "Complex communication",
                    "Data consistency",
                    "Operational overhead",
                ],
            },
            ArchitectureType.SERVERLESS: {
                "indicators": [
                    "event-driven",
                    "cost-sensitive",
                    "variable-load",
                    "stateless",
                ],
                "complexity": "medium",
                "team_size": 3,
                "benefits": ["No server management", "Auto-scaling", "Pay per use"],
                "drawbacks": [
                    "Vendor lock-in",
                    "Cold starts",
                    "Limited execution time",
                ],
            },
            ArchitectureType.MONOLITHIC: {
                "indicators": [
                    "simple",
                    "rapid-development",
                    "small-team",
                    "consistent",
                ],
                "complexity": "low",
                "team_size": 5,
                "benefits": ["Simple deployment", "Easy debugging", "Data consistency"],
                "drawbacks": [
                    "Scaling limitations",
                    "Technology lock-in",
                    "Single point of failure",
                ],
            },
            ArchitectureType.EVENT_DRIVEN: {
                "indicators": [
                    "real-time",
                    "asynchronous",
                    "reactive",
                    "event-sourcing",
                ],
                "complexity": "high",
                "team_size": 8,
                "benefits": ["Loose coupling", "Scalability", "Real-time processing"],
                "drawbacks": [
                    "Complex debugging",
                    "Event ordering",
                    "Eventual consistency",
                ],
            },
            ArchitectureType.LAYERED: {
                "indicators": [
                    "traditional",
                    "clear-separation",
                    "maintainable",
                    "enterprise",
                ],
                "complexity": "medium",
                "team_size": 6,
                "benefits": [
                    "Clear structure",
                    "Separation of concerns",
                    "Testability",
                ],
                "drawbacks": [
                    "Performance overhead",
                    "Rigid structure",
                    "Cross-cutting concerns",
                ],
            },
        }

        self.decision_matrix = self._build_decision_matrix()

    async def select(
        self, requirements: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select optimal architecture based on requirements"""

        # Analyze requirements
        analysis = self._analyze_requirements(requirements)

        # Score each architecture
        scores = {}
        for arch_type in ArchitectureType:
            score = self._score_architecture(arch_type, analysis, constraints)
            scores[arch_type] = score

        # Select best architecture
        best_arch = max(scores, key=scores.get)

        # Generate architecture specification
        architecture = self._generate_architecture_spec(best_arch, requirements, constraints)

        # Add decision rationale
        architecture["decision_rationale"] = self._generate_rationale(best_arch, scores, analysis)

        # Add migration path if needed
        if self._needs_migration(requirements):
            architecture["migration_path"] = self._generate_migration_path(
                requirements.get("current_architecture"), best_arch
            )

        return architecture

    def _analyze_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Analyze requirements for architecture selection"""

        analysis = {
            "scale": self._analyze_scale(requirements),
            "complexity": self._analyze_complexity(requirements),
            "team": self._analyze_team(requirements),
            "performance": self._analyze_performance(requirements),
            "constraints": self._analyze_constraints(requirements),
            "integration": self._analyze_integration(requirements),
        }

        return analysis

    def _analyze_scale(self, requirements: Dict) -> Dict:
        """Analyze scale requirements"""
        scale_indicators = {
            "users": requirements.get("expected_users", 100),
            "transactions": requirements.get("transactions_per_second", 10),
            "data_volume": requirements.get("data_volume_gb", 10),
            "geographic_distribution": requirements.get("regions", 1),
        }

        scale_level = "small"
        if scale_indicators["users"] > 10000 or scale_indicators["transactions"] > 100:
            scale_level = "large"
        elif scale_indicators["users"] > 1000 or scale_indicators["transactions"] > 50:
            scale_level = "medium"

        return {
            "level": scale_level,
            "indicators": scale_indicators,
            "needs_auto_scaling": scale_level in ["medium", "large"],
        }

    def _analyze_complexity(self, requirements: Dict) -> Dict:
        """Analyze system complexity"""
        features = requirements.get("features", [])
        integrations = requirements.get("integrations", [])

        complexity_score = len(features) * 0.5 + len(integrations) * 1.5

        complexity_level = "low"
        if complexity_score > 20:
            complexity_level = "high"
        elif complexity_score > 10:
            complexity_level = "medium"

        return {
            "level": complexity_level,
            "score": complexity_score,
            "feature_count": len(features),
            "integration_count": len(integrations),
        }

    def _analyze_team(self, requirements: Dict) -> Dict:
        """Analyze team capabilities"""
        return {
            "size": requirements.get("team_size", 5),
            "expertise": requirements.get("team_expertise", "medium"),
            "distributed": requirements.get("distributed_team", False),
            "experience": requirements.get("architecture_experience", {}),
        }

    def _analyze_performance(self, requirements: Dict) -> Dict:
        """Analyze performance requirements"""
        return {
            "response_time": requirements.get("max_response_time_ms", 1000),
            "availability": requirements.get("availability_percent", 99.9),
            "throughput": requirements.get("throughput_rps", 100),
            "real_time": requirements.get("real_time_processing", False),
        }

    def _analyze_constraints(self, requirements: Dict) -> Dict:
        """Analyze technical constraints"""
        return {
            "budget": requirements.get("budget_constraint", "medium"),
            "timeline": requirements.get("timeline_months", 6),
            "compliance": requirements.get("compliance_requirements", []),
            "technology": requirements.get("technology_constraints", []),
        }

    def _analyze_integration(self, requirements: Dict) -> Dict:
        """Analyze integration requirements"""
        integrations = requirements.get("integrations", [])

        return {
            "count": len(integrations),
            "types": self._categorize_integrations(integrations),
            "complexity": self._assess_integration_complexity(integrations),
            "real_time": any("real-time" in str(i).lower() for i in integrations),
        }

    def _categorize_integrations(self, integrations: List) -> List[str]:
        """Categorize integration types"""
        categories = set()

        for integration in integrations:
            integration_str = str(integration).lower()
            if "payment" in integration_str:
                categories.add("payment")
            if "email" in integration_str or "sms" in integration_str:
                categories.add("communication")
            if "analytics" in integration_str:
                categories.add("analytics")
            if "storage" in integration_str or "s3" in integration_str:
                categories.add("storage")

        return list(categories)

    def _assess_integration_complexity(self, integrations: List) -> str:
        """Assess overall integration complexity"""
        if len(integrations) > 10:
            return "high"
        elif len(integrations) > 5:
            return "medium"
        return "low"

    def _score_architecture(
        self, arch_type: ArchitectureType, analysis: Dict, constraints: Dict
    ) -> float:
        """Score architecture fitness"""

        score = 0.0
        criteria = self.architecture_criteria[arch_type]

        # Scale fit
        if analysis["scale"]["level"] == "large":
            if arch_type in [
                ArchitectureType.MICROSERVICES,
                ArchitectureType.SERVERLESS,
            ]:
                score += 2.0
            elif arch_type == ArchitectureType.MONOLITHIC:
                score -= 1.0
        elif analysis["scale"]["level"] == "small":
            if arch_type == ArchitectureType.MONOLITHIC:
                score += 2.0
            elif arch_type == ArchitectureType.MICROSERVICES:
                score -= 1.0

        # Complexity fit
        if analysis["complexity"]["level"] == criteria["complexity"]:
            score += 1.5

        # Team fit
        team_size = analysis["team"]["size"]
        ideal_size = criteria["team_size"]
        if abs(team_size - ideal_size) <= 2:
            score += 1.0

        # Performance fit
        if analysis["performance"]["real_time"] and arch_type == ArchitectureType.EVENT_DRIVEN:
            score += 2.0

        # Cost considerations
        if constraints.get("budget") == "low" and arch_type == ArchitectureType.SERVERLESS:
            score += 1.5

        # Check indicators
        requirements_text = str(analysis).lower()
        matching_indicators = sum(
            1 for indicator in criteria["indicators"] if indicator in requirements_text
        )
        score += matching_indicators * 0.5

        return max(score, 0)

    def _generate_architecture_spec(
        self, arch_type: ArchitectureType, requirements: Dict, constraints: Dict
    ) -> Dict[str, Any]:
        """Generate detailed architecture specification"""

        criteria = self.architecture_criteria[arch_type]

        spec = {
            "type": arch_type.value,
            "name": f"{arch_type.value.replace('_', ' ').title()} Architecture",
            "description": self._get_architecture_description(arch_type),
            "benefits": criteria["benefits"],
            "drawbacks": criteria["drawbacks"],
            "components": self._get_architecture_components(arch_type),
            "patterns": self._get_architecture_patterns(arch_type),
            "deployment": self._get_deployment_model(arch_type),
            "scaling_strategy": self._get_scaling_strategy(arch_type),
            "data_management": self._get_data_strategy(arch_type),
            "communication": self._get_communication_patterns(arch_type),
            "security": self._get_security_considerations(arch_type),
            "monitoring": self._get_monitoring_strategy(arch_type),
            "estimated_complexity": criteria["complexity"],
            "recommended_team_size": criteria["team_size"],
        }

        return spec

    def _get_architecture_description(self, arch_type: ArchitectureType) -> str:
        """Get architecture description"""
        descriptions = {
            ArchitectureType.MICROSERVICES: "Distributed architecture with independent services",
            ArchitectureType.SERVERLESS: "Event-driven compute without server management",
            ArchitectureType.MONOLITHIC: "Single deployable unit with all functionality",
            ArchitectureType.EVENT_DRIVEN: "Asynchronous message-based architecture",
            ArchitectureType.LAYERED: "Traditional n-tier architecture with clear layers",
        }
        return descriptions.get(arch_type, "Custom architecture pattern")

    def _get_architecture_components(self, arch_type: ArchitectureType) -> List[str]:
        """Get required components for architecture"""
        components_map = {
            ArchitectureType.MICROSERVICES: [
                "API Gateway",
                "Service Registry",
                "Config Server",
                "Circuit Breaker",
                "Message Queue",
                "Service Mesh",
            ],
            ArchitectureType.SERVERLESS: [
                "Lambda Functions",
                "API Gateway",
                "Event Bridge",
                "DynamoDB",
                "S3",
                "Step Functions",
            ],
            ArchitectureType.MONOLITHIC: [
                "Web Server",
                "Application Server",
                "Database",
                "Cache",
                "Load Balancer",
            ],
            ArchitectureType.EVENT_DRIVEN: [
                "Event Bus",
                "Event Store",
                "Event Processors",
                "Message Queue",
                "Stream Processing",
            ],
            ArchitectureType.LAYERED: [
                "Presentation Layer",
                "Business Logic Layer",
                "Data Access Layer",
                "Database Layer",
            ],
        }
        return components_map.get(arch_type, [])

    def _get_architecture_patterns(self, arch_type: ArchitectureType) -> List[str]:
        """Get design patterns for architecture"""
        patterns_map = {
            ArchitectureType.MICROSERVICES: [
                "Service Discovery",
                "Circuit Breaker",
                "API Gateway",
                "Saga",
                "Event Sourcing",
                "CQRS",
            ],
            ArchitectureType.SERVERLESS: [
                "Function as a Service",
                "Backend for Frontend",
                "Event Sourcing",
                "Choreography",
            ],
            ArchitectureType.MONOLITHIC: [
                "MVC",
                "Repository",
                "Service Layer",
                "Dependency Injection",
            ],
            ArchitectureType.EVENT_DRIVEN: [
                "Publish-Subscribe",
                "Event Sourcing",
                "Command Query",
                "Saga",
            ],
            ArchitectureType.LAYERED: [
                "DAO",
                "DTO",
                "Service Layer",
                "Facade",
                "Repository",
            ],
        }
        return patterns_map.get(arch_type, [])

    def _get_deployment_model(self, arch_type: ArchitectureType) -> str:
        """Get deployment model for architecture"""
        deployment_map = {
            ArchitectureType.MICROSERVICES: "Container orchestration (Kubernetes/ECS)",
            ArchitectureType.SERVERLESS: "Function deployment (Lambda/Cloud Functions)",
            ArchitectureType.MONOLITHIC: "Traditional server or container deployment",
            ArchitectureType.EVENT_DRIVEN: "Message broker with distributed processors",
            ArchitectureType.LAYERED: "Tiered deployment with load balancing",
        }
        return deployment_map.get(arch_type, "Custom deployment")

    def _get_scaling_strategy(self, arch_type: ArchitectureType) -> str:
        """Get scaling strategy for architecture"""
        scaling_map = {
            ArchitectureType.MICROSERVICES: "Independent service scaling",
            ArchitectureType.SERVERLESS: "Automatic function scaling",
            ArchitectureType.MONOLITHIC: "Vertical and horizontal scaling",
            ArchitectureType.EVENT_DRIVEN: "Queue-based auto-scaling",
            ArchitectureType.LAYERED: "Layer-specific scaling",
        }
        return scaling_map.get(arch_type, "Manual scaling")

    def _get_data_strategy(self, arch_type: ArchitectureType) -> str:
        """Get data management strategy"""
        data_map = {
            ArchitectureType.MICROSERVICES: "Database per service",
            ArchitectureType.SERVERLESS: "Managed database services",
            ArchitectureType.MONOLITHIC: "Shared database",
            ArchitectureType.EVENT_DRIVEN: "Event sourcing with CQRS",
            ArchitectureType.LAYERED: "Centralized database with ORM",
        }
        return data_map.get(arch_type, "Custom data strategy")

    def _get_communication_patterns(self, arch_type: ArchitectureType) -> List[str]:
        """Get communication patterns"""
        comm_map = {
            ArchitectureType.MICROSERVICES: ["REST API", "gRPC", "Message Queue"],
            ArchitectureType.SERVERLESS: ["Event-driven", "API Gateway", "SQS/SNS"],
            ArchitectureType.MONOLITHIC: ["Direct method calls", "Shared memory"],
            ArchitectureType.EVENT_DRIVEN: [
                "Pub/Sub",
                "Event streaming",
                "Async messaging",
            ],
            ArchitectureType.LAYERED: ["Layer interfaces", "Service calls"],
        }
        return comm_map.get(arch_type, [])

    def _get_security_considerations(self, arch_type: ArchitectureType) -> List[str]:
        """Get security considerations"""
        security_map = {
            ArchitectureType.MICROSERVICES: [
                "Service-to-service authentication",
                "API Gateway security",
                "Network segmentation",
            ],
            ArchitectureType.SERVERLESS: [
                "Function permissions",
                "API authentication",
                "Secrets management",
            ],
            ArchitectureType.MONOLITHIC: [
                "Perimeter security",
                "Session management",
                "Input validation",
            ],
            ArchitectureType.EVENT_DRIVEN: [
                "Message encryption",
                "Event validation",
                "Access control",
            ],
            ArchitectureType.LAYERED: [
                "Layer isolation",
                "Authentication at presentation",
                "Data encryption",
            ],
        }
        return security_map.get(arch_type, [])

    def _get_monitoring_strategy(self, arch_type: ArchitectureType) -> Dict:
        """Get monitoring strategy"""
        return {
            "distributed_tracing": arch_type == ArchitectureType.MICROSERVICES,
            "centralized_logging": True,
            "metrics_aggregation": True,
            "health_checks": True,
            "alerting": True,
        }

    def _generate_rationale(
        self, selected: ArchitectureType, scores: Dict, analysis: Dict
    ) -> Dict[str, Any]:
        """Generate decision rationale"""

        return {
            "selected_architecture": selected.value,
            "score": scores[selected],
            "key_factors": self._identify_key_factors(selected, analysis),
            "alternatives_considered": [
                {
                    "architecture": arch.value,
                    "score": score,
                    "reason_not_selected": self._get_rejection_reason(arch, selected, scores),
                }
                for arch, score in scores.items()
                if arch != selected
            ],
            "risks": self._identify_risks(selected, analysis),
            "mitigations": self._suggest_mitigations(selected, analysis),
        }

    def _identify_key_factors(self, selected: ArchitectureType, analysis: Dict) -> List[str]:
        """Identify key decision factors"""
        factors = []

        if analysis["scale"]["level"] == "large":
            factors.append("High scalability requirements")

        if analysis["complexity"]["level"] == "high":
            factors.append("Complex business logic")

        if analysis["performance"]["real_time"]:
            factors.append("Real-time processing needs")

        if analysis["team"]["distributed"]:
            factors.append("Distributed development team")

        return factors

    def _get_rejection_reason(
        self, arch: ArchitectureType, selected: ArchitectureType, scores: Dict
    ) -> str:
        """Get reason for not selecting architecture"""

        if scores[arch] < scores[selected] * 0.5:
            return "Significantly lower fitness score"
        elif arch == ArchitectureType.MONOLITHIC and scores[selected] > scores[arch]:
            return "Scalability limitations"
        elif arch == ArchitectureType.MICROSERVICES and scores[selected] > scores[arch]:
            return "Excessive complexity for requirements"
        else:
            return "Better alternative available"

    def _identify_risks(self, selected: ArchitectureType, analysis: Dict) -> List[str]:
        """Identify architecture risks"""
        risks = []

        if selected == ArchitectureType.MICROSERVICES:
            risks.extend(
                [
                    "Increased operational complexity",
                    "Network latency between services",
                    "Data consistency challenges",
                ]
            )
        elif selected == ArchitectureType.SERVERLESS:
            risks.extend(["Vendor lock-in", "Cold start latency", "Limited execution time"])

        return risks

    def _suggest_mitigations(self, selected: ArchitectureType, analysis: Dict) -> List[str]:
        """Suggest risk mitigations"""
        mitigations = []

        if selected == ArchitectureType.MICROSERVICES:
            mitigations.extend(
                [
                    "Implement service mesh for communication",
                    "Use distributed tracing",
                    "Apply saga pattern for transactions",
                ]
            )
        elif selected == ArchitectureType.SERVERLESS:
            mitigations.extend(
                [
                    "Use provisioned concurrency for critical functions",
                    "Implement multi-cloud strategy",
                    "Design for stateless operations",
                ]
            )

        return mitigations

    def _needs_migration(self, requirements: Dict) -> bool:
        """Check if migration is needed"""
        return "current_architecture" in requirements

    def _generate_migration_path(
        self, current: Optional[str], target: ArchitectureType
    ) -> Dict[str, Any]:
        """Generate migration path"""

        if not current:
            return {}

        return {
            "from": current,
            "to": target.value,
            "phases": self._get_migration_phases(current, target),
            "estimated_duration": self._estimate_migration_duration(current, target),
            "risks": self._get_migration_risks(current, target),
            "strategies": self._get_migration_strategies(current, target),
        }

    def _get_migration_phases(self, current: str, target: ArchitectureType) -> List[Dict]:
        """Get migration phases"""
        phases = []

        if "monolithic" in current.lower() and target == ArchitectureType.MICROSERVICES:
            phases = [
                {"phase": 1, "name": "Identify boundaries", "duration": "2 weeks"},
                {"phase": 2, "name": "Extract first service", "duration": "4 weeks"},
                {"phase": 3, "name": "Incremental extraction", "duration": "12 weeks"},
                {"phase": 4, "name": "Complete migration", "duration": "4 weeks"},
            ]

        return phases

    def _estimate_migration_duration(self, current: str, target: ArchitectureType) -> str:
        """Estimate migration duration"""
        if "monolithic" in current.lower() and target == ArchitectureType.MICROSERVICES:
            return "3-6 months"
        return "1-3 months"

    def _get_migration_risks(self, current: str, target: ArchitectureType) -> List[str]:
        """Get migration risks"""
        return [
            "Service disruption during migration",
            "Data consistency during transition",
            "Team learning curve",
        ]

    def _get_migration_strategies(self, current: str, target: ArchitectureType) -> List[str]:
        """Get migration strategies"""
        return [
            "Strangler Fig pattern for gradual migration",
            "Branch by abstraction for code changes",
            "Blue-green deployment for risk mitigation",
        ]

    def _build_decision_matrix(self) -> Dict:
        """Build architecture decision matrix"""
        return {
            "factors": [
                "scalability",
                "complexity",
                "team_size",
                "performance",
                "cost",
                "time_to_market",
            ],
            "weights": {
                "scalability": 0.25,
                "complexity": 0.20,
                "team_size": 0.15,
                "performance": 0.20,
                "cost": 0.10,
                "time_to_market": 0.10,
            },
        }
