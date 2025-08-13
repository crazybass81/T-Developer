"""
Validation Engine Module
Validates parsed requirements and specifications
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationEngine:
    """Validates requirements and specifications"""

    def __init__(self):
        self.validation_rules = {
            "completeness": ["has_actor", "has_action", "has_criteria"],
            "consistency": ["no_conflicts", "clear_dependencies"],
            "feasibility": ["technically_possible", "resource_available"],
            "testability": ["measurable", "verifiable"],
            "clarity": ["unambiguous", "specific"],
        }

    async def validate(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specifications"""

        issues = []

        # Validate completeness
        issues.extend(self._validate_completeness(specifications))

        # Validate consistency
        issues.extend(self._validate_consistency(specifications))

        # Validate feasibility
        issues.extend(self._validate_feasibility(specifications))

        # Generate recommendations
        recommendations = self._generate_recommendations(issues)

        return {
            "valid": len(
                [i for i in issues if i["level"] == ValidationLevel.ERROR.value]
            )
            == 0,
            "issues": issues,
            "recommendations": recommendations,
            "score": self._calculate_validation_score(issues),
        }

    def _validate_completeness(self, specs: Dict) -> List[Dict]:
        """Check specification completeness"""
        issues = []

        if not specs.get("functional", {}).get("features"):
            issues.append(
                {
                    "level": ValidationLevel.WARNING.value,
                    "category": "completeness",
                    "message": "No functional features specified",
                }
            )

        if not specs.get("data", {}).get("models"):
            issues.append(
                {
                    "level": ValidationLevel.WARNING.value,
                    "category": "completeness",
                    "message": "No data models defined",
                }
            )

        return issues

    def _validate_consistency(self, specs: Dict) -> List[Dict]:
        """Check for inconsistencies"""
        issues = []

        # Check for conflicting requirements
        functional = specs.get("functional", {})
        non_functional = specs.get("non_functional", {})

        if functional and non_functional:
            # Simple check for performance vs feature conflicts
            if len(functional.get("features", [])) > 20 and any(
                "real-time" in str(p) for p in non_functional.get("performance", [])
            ):
                issues.append(
                    {
                        "level": ValidationLevel.WARNING.value,
                        "category": "consistency",
                        "message": "Large feature set may conflict with real-time performance requirements",
                    }
                )

        return issues

    def _validate_feasibility(self, specs: Dict) -> List[Dict]:
        """Check technical feasibility"""
        issues = []

        # Check for unrealistic performance requirements
        performance = specs.get("non_functional", {}).get("performance", [])
        for perf in performance:
            if isinstance(perf, dict) and perf.get("value"):
                if "response_time" in str(perf) and perf.get("value", 1000) < 10:
                    issues.append(
                        {
                            "level": ValidationLevel.WARNING.value,
                            "category": "feasibility",
                            "message": f"Response time requirement may be unrealistic: {perf.get('value')}ms",
                        }
                    )

        return issues

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []

        issue_categories = set(i["category"] for i in issues)

        if "completeness" in issue_categories:
            recommendations.append("Review requirements for missing details")

        if "consistency" in issue_categories:
            recommendations.append("Resolve conflicting requirements with stakeholders")

        if "feasibility" in issue_categories:
            recommendations.append(
                "Validate technical requirements with development team"
            )

        return recommendations

    def _calculate_validation_score(self, issues: List[Dict]) -> float:
        """Calculate overall validation score"""
        if not issues:
            return 1.0

        error_count = sum(
            1 for i in issues if i["level"] == ValidationLevel.ERROR.value
        )
        warning_count = sum(
            1 for i in issues if i["level"] == ValidationLevel.WARNING.value
        )

        score = 1.0 - (error_count * 0.2) - (warning_count * 0.1)
        return max(0.0, score)
