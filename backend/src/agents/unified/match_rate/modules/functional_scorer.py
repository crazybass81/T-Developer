"""
Functional Scorer Module
Scores components based on functional requirements matching
"""

from typing import Dict, List, Any, Optional
import re


class FunctionalScorer:
    """Scores functional requirement matching"""

    def __init__(self):
        self.functional_categories = self._build_functional_categories()

    async def score(
        self, components: List[Dict[str, Any]], requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Score components based on functional requirements"""

        functional_scores = {}

        # Extract functional requirements
        func_requirements = self._extract_functional_requirements(requirements)

        for component in components:
            component_id = component.get("id", component.get("name"))

            # Extract component capabilities
            capabilities = self._extract_component_capabilities(component)

            # Score different functional aspects
            scores = {
                "feature_coverage": self._score_feature_coverage(
                    capabilities, func_requirements
                ),
                "use_case_match": self._score_use_case_matching(
                    capabilities, func_requirements
                ),
                "workflow_support": self._score_workflow_support(
                    capabilities, func_requirements
                ),
                "integration_capabilities": self._score_integration_capabilities(
                    capabilities, func_requirements
                ),
                "customization_support": self._score_customization_support(
                    capabilities, func_requirements
                ),
                "scalability_features": self._score_scalability_features(
                    capabilities, func_requirements
                ),
            }

            # Calculate total functional score
            total_score = self._calculate_total_functional_score(scores)

            functional_scores[component_id] = {
                "individual_scores": scores,
                "total_score": total_score,
                "coverage_analysis": self._analyze_coverage(
                    capabilities, func_requirements
                ),
                "gap_analysis": self._analyze_gaps(capabilities, func_requirements),
                "recommendations": self._generate_functional_recommendations(scores),
            }

        return functional_scores

    def _extract_functional_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Extract functional requirements from requirements data"""

        func_req = {
            "features": [],
            "use_cases": [],
            "workflows": [],
            "integrations": [],
            "user_roles": [],
            "business_rules": [],
        }

        # Extract from various requirement fields
        text = str(requirements).lower()

        # Feature extraction
        feature_patterns = [
            r"(user can|users can|ability to|feature to|functionality to)\s+(.+?)(?:\.|,|$)",
            r"(create|read|update|delete|manage|view|edit)\s+(.+?)(?:\.|,|$)",
            r"(support for|supports|includes|provides)\s+(.+?)(?:\.|,|$)",
        ]

        for pattern in feature_patterns:
            matches = re.findall(pattern, text)
            func_req["features"].extend([match[1].strip() for match in matches])

        # Use case extraction
        if "use_cases" in requirements:
            func_req["use_cases"] = requirements["use_cases"]

        # Integration requirements
        integration_keywords = ["api", "integration", "connect", "webhook", "sync"]
        for keyword in integration_keywords:
            if keyword in text:
                func_req["integrations"].append(keyword)

        return func_req

    def _extract_component_capabilities(self, component: Dict) -> Dict[str, Any]:
        """Extract capabilities from component data"""

        capabilities = {
            "features": [],
            "supported_use_cases": [],
            "integrations": [],
            "apis": [],
            "customization_options": [],
            "scalability_features": [],
        }

        # Extract from component description/documentation
        text = str(component).lower()

        # Feature capabilities
        if "features" in component:
            capabilities["features"] = component["features"]

        # API capabilities
        api_indicators = ["rest api", "graphql", "webhook", "sdk", "api endpoint"]
        for indicator in api_indicators:
            if indicator in text:
                capabilities["apis"].append(indicator)

        # Integration capabilities
        integration_indicators = ["integration", "connector", "plugin", "extension"]
        for indicator in integration_indicators:
            if indicator in text:
                capabilities["integrations"].append(indicator)

        return capabilities

    def _score_feature_coverage(self, capabilities: Dict, requirements: Dict) -> float:
        """Score how well component features cover requirements"""

        required_features = set(requirements.get("features", []))
        available_features = set(capabilities.get("features", []))

        if not required_features:
            return 1.0  # No specific features required

        # Calculate coverage using keyword matching
        coverage_count = 0
        for req_feature in required_features:
            for avail_feature in available_features:
                if self._features_match(req_feature, avail_feature):
                    coverage_count += 1
                    break

        return coverage_count / len(required_features)

    def _features_match(self, required: str, available: str) -> bool:
        """Check if features match using fuzzy matching"""

        req_words = set(required.lower().split())
        avail_words = set(available.lower().split())

        # Calculate word overlap
        overlap = len(req_words.intersection(avail_words))
        total_req_words = len(req_words)

        return (overlap / total_req_words) > 0.5 if total_req_words > 0 else False

    def _score_use_case_matching(self, capabilities: Dict, requirements: Dict) -> float:
        """Score use case matching"""

        required_use_cases = requirements.get("use_cases", [])
        supported_use_cases = capabilities.get("supported_use_cases", [])

        if not required_use_cases:
            return 0.8  # Default good score if no specific use cases

        match_count = 0
        for req_case in required_use_cases:
            for supp_case in supported_use_cases:
                if self._use_cases_match(req_case, supp_case):
                    match_count += 1
                    break

        return match_count / len(required_use_cases) if required_use_cases else 0.8

    def _use_cases_match(self, required: str, supported: str) -> bool:
        """Check if use cases match"""

        # Simple keyword-based matching
        req_keywords = set(str(required).lower().split())
        supp_keywords = set(str(supported).lower().split())

        overlap = len(req_keywords.intersection(supp_keywords))
        return overlap > 0

    def _score_workflow_support(self, capabilities: Dict, requirements: Dict) -> float:
        """Score workflow support capabilities"""

        workflow_indicators = {
            "sequential": ["sequence", "step", "workflow", "process"],
            "parallel": ["parallel", "concurrent", "batch"],
            "conditional": ["if", "condition", "rule", "logic"],
            "approval": ["approval", "review", "authorize"],
            "notification": ["notify", "alert", "email", "message"],
        }

        req_text = str(requirements).lower()
        cap_text = str(capabilities).lower()

        supported_workflows = 0
        total_workflows = 0

        for workflow_type, keywords in workflow_indicators.items():
            req_has_workflow = any(keyword in req_text for keyword in keywords)
            cap_supports_workflow = any(keyword in cap_text for keyword in keywords)

            if req_has_workflow:
                total_workflows += 1
                if cap_supports_workflow:
                    supported_workflows += 1

        return supported_workflows / total_workflows if total_workflows > 0 else 0.7

    def _score_integration_capabilities(
        self, capabilities: Dict, requirements: Dict
    ) -> float:
        """Score integration capabilities"""

        required_integrations = requirements.get("integrations", [])
        available_integrations = capabilities.get(
            "integrations", []
        ) + capabilities.get("apis", [])

        if not required_integrations:
            return 0.8  # Good default if no specific integrations required

        # Score based on integration type matching
        integration_types = {
            "api": ["rest", "graphql", "api", "http"],
            "webhook": ["webhook", "callback", "event"],
            "database": ["database", "sql", "nosql"],
            "file": ["file", "csv", "json", "xml"],
            "messaging": ["message", "queue", "pub/sub", "kafka"],
        }

        score = 0
        for req_integration in required_integrations:
            integration_score = 0
            for int_type, keywords in integration_types.items():
                if any(keyword in str(req_integration).lower() for keyword in keywords):
                    if any(
                        keyword in str(available_integrations).lower()
                        for keyword in keywords
                    ):
                        integration_score = 1.0
                        break
            score += integration_score

        return score / len(required_integrations)

    def _score_customization_support(
        self, capabilities: Dict, requirements: Dict
    ) -> float:
        """Score customization support"""

        customization_indicators = [
            "customize",
            "configure",
            "extend",
            "plugin",
            "theme",
            "template",
        ]

        req_text = str(requirements).lower()
        cap_text = str(capabilities).lower()

        needs_customization = any(
            indicator in req_text for indicator in customization_indicators
        )
        supports_customization = any(
            indicator in cap_text for indicator in customization_indicators
        )

        if not needs_customization:
            return 0.9  # High score if customization not needed

        return 1.0 if supports_customization else 0.3

    def _score_scalability_features(
        self, capabilities: Dict, requirements: Dict
    ) -> float:
        """Score scalability features"""

        scalability_indicators = [
            "scale",
            "performance",
            "load",
            "concurrent",
            "cluster",
        ]

        req_text = str(requirements).lower()
        cap_text = str(capabilities).lower()

        needs_scalability = any(
            indicator in req_text for indicator in scalability_indicators
        )
        supports_scalability = any(
            indicator in cap_text for indicator in scalability_indicators
        )

        if not needs_scalability:
            return 0.8  # Good default if scalability not critical

        return 1.0 if supports_scalability else 0.4

    def _calculate_total_functional_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted total functional score"""

        weights = {
            "feature_coverage": 0.3,
            "use_case_match": 0.25,
            "workflow_support": 0.15,
            "integration_capabilities": 0.15,
            "customization_support": 0.1,
            "scalability_features": 0.05,
        }

        total = sum(scores[category] * weights[category] for category in weights.keys())
        return min(1.0, max(0.0, total))

    def _analyze_coverage(
        self, capabilities: Dict, requirements: Dict
    ) -> Dict[str, Any]:
        """Analyze requirement coverage"""

        return {
            "covered_requirements": self._find_covered_requirements(
                capabilities, requirements
            ),
            "coverage_percentage": self._calculate_coverage_percentage(
                capabilities, requirements
            ),
            "critical_coverage": self._analyze_critical_coverage(
                capabilities, requirements
            ),
        }

    def _find_covered_requirements(
        self, capabilities: Dict, requirements: Dict
    ) -> List[str]:
        """Find which requirements are covered"""

        covered = []
        required_features = requirements.get("features", [])

        for feature in required_features:
            if self._is_requirement_covered(feature, capabilities):
                covered.append(feature)

        return covered

    def _is_requirement_covered(self, requirement: str, capabilities: Dict) -> bool:
        """Check if a requirement is covered by capabilities"""

        cap_text = str(capabilities).lower()
        req_words = requirement.lower().split()

        # Simple keyword matching
        return any(word in cap_text for word in req_words)

    def _calculate_coverage_percentage(
        self, capabilities: Dict, requirements: Dict
    ) -> float:
        """Calculate overall coverage percentage"""

        total_requirements = len(requirements.get("features", [])) + len(
            requirements.get("use_cases", [])
        )
        covered_count = len(self._find_covered_requirements(capabilities, requirements))

        return (
            (covered_count / total_requirements) * 100
            if total_requirements > 0
            else 100
        )

    def _analyze_critical_coverage(
        self, capabilities: Dict, requirements: Dict
    ) -> Dict[str, bool]:
        """Analyze coverage of critical requirements"""

        critical_features = [
            "authentication",
            "security",
            "data storage",
            "user management",
        ]

        coverage = {}
        for feature in critical_features:
            coverage[feature] = self._is_requirement_covered(feature, capabilities)

        return coverage

    def _analyze_gaps(self, capabilities: Dict, requirements: Dict) -> List[str]:
        """Analyze gaps in functionality"""

        gaps = []
        required_features = requirements.get("features", [])

        for feature in required_features:
            if not self._is_requirement_covered(feature, capabilities):
                gaps.append(feature)

        return gaps

    def _generate_functional_recommendations(
        self, scores: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations based on functional scores"""

        recommendations = []

        for category, score in scores.items():
            if score < 0.5:
                recommendations.append(
                    f"Low {category.replace('_', ' ')} - consider alternatives"
                )
            elif score < 0.7:
                recommendations.append(
                    f"Moderate {category.replace('_', ' ')} - may need customization"
                )

        if not recommendations:
            recommendations.append("Good functional match - proceed with integration")

        return recommendations

    def _build_functional_categories(self) -> Dict[str, List[str]]:
        """Build functional categories mapping"""

        return {
            "core_features": [
                "authentication",
                "authorization",
                "user_management",
                "data_storage",
                "search",
                "reporting",
            ],
            "ui_features": [
                "responsive_design",
                "mobile_support",
                "accessibility",
                "themes",
                "customization",
                "widgets",
            ],
            "integration_features": [
                "rest_api",
                "webhooks",
                "third_party_integrations",
                "data_import_export",
                "sso",
            ],
            "workflow_features": [
                "approval_workflows",
                "notifications",
                "automation",
                "scheduling",
                "batch_processing",
            ],
        }
