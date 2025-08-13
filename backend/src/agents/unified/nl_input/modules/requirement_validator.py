"""
Requirement Validator Module
Validates extracted requirements for completeness and consistency
"""

from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of requirement validation"""

    is_valid: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class RequirementValidator:
    """Validates project requirements"""

    def __init__(self):
        self.required_fields = ["project_type", "main_functionality", "features"]

        self.validation_rules = {
            "min_features": 1,
            "max_features": 20,
            "min_description_length": 10,
            "max_description_length": 5000,
        }

    async def validate(self, requirements: Any) -> ValidationResult:
        """
        Validate the extracted requirements

        Args:
            requirements: Requirements object to validate

        Returns:
            ValidationResult with issues, warnings, and suggestions
        """
        issues = []
        warnings = []
        suggestions = []

        # Check required fields
        for field in self.required_fields:
            if not hasattr(requirements, field) or not getattr(requirements, field):
                issues.append(f"Missing required field: {field}")

        # Validate feature count
        if hasattr(requirements, "features"):
            feature_count = len(requirements.features)
            if feature_count < self.validation_rules["min_features"]:
                issues.append("At least one feature must be specified")
            elif feature_count > self.validation_rules["max_features"]:
                warnings.append(
                    f"Too many features ({feature_count}). Consider prioritizing."
                )

        # Validate description length
        if hasattr(requirements, "description"):
            desc_length = len(requirements.description)
            if desc_length < self.validation_rules["min_description_length"]:
                warnings.append("Description is too short. More details would help.")
            elif desc_length > self.validation_rules["max_description_length"]:
                warnings.append("Description is very long. Consider summarizing.")

        # Check for conflicting requirements
        if hasattr(requirements, "constraints"):
            constraints = requirements.constraints
            if "No backend required" in constraints and hasattr(
                requirements, "features"
            ):
                if (
                    "api" in requirements.features
                    or "database" in requirements.features
                ):
                    issues.append(
                        "Conflict: No backend constraint with API/database features"
                    )

        # Validate technical requirements
        if hasattr(requirements, "technical_requirements"):
            tech_reqs = requirements.technical_requirements

            # Check for incompatible tech stack
            if isinstance(tech_reqs, dict):
                if "frontend" in tech_reqs and "backend" in tech_reqs:
                    frontend = tech_reqs.get("frontend", [])
                    backend = tech_reqs.get("backend", [])

                    # Check for reasonable combinations
                    if "react" in frontend and "django" in backend:
                        suggestions.append(
                            "Consider using Django REST Framework for React integration"
                        )

                    if not backend and hasattr(requirements, "features"):
                        if (
                            "auth" in requirements.features
                            or "database" in requirements.features
                        ):
                            warnings.append(
                                "Backend required for authentication and database features"
                            )

        # Check complexity vs effort estimation
        if hasattr(requirements, "complexity") and hasattr(
            requirements, "estimated_effort_hours"
        ):
            complexity = requirements.complexity
            effort = requirements.estimated_effort_hours

            expected_ranges = {
                "simple": (20, 80),
                "medium": (80, 200),
                "complex": (200, 500),
            }

            if complexity in expected_ranges:
                min_effort, max_effort = expected_ranges[complexity]
                if effort < min_effort:
                    warnings.append(
                        f"Effort estimate seems low for {complexity} project"
                    )
                elif effort > max_effort:
                    warnings.append(
                        f"Effort estimate seems high for {complexity} project"
                    )

        # Provide suggestions based on project type
        if hasattr(requirements, "project_type"):
            project_type = requirements.project_type
            type_suggestions = {
                "todo": [
                    "Consider adding task categories",
                    "Include due date functionality",
                ],
                "blog": ["Add SEO optimization", "Include RSS feed support"],
                "ecommerce": [
                    "Implement inventory tracking",
                    "Add order status tracking",
                ],
                "dashboard": [
                    "Include data export functionality",
                    "Add customizable widgets",
                ],
                "chat": ["Implement message encryption", "Add file sharing capability"],
            }

            if project_type in type_suggestions:
                for suggestion in type_suggestions[project_type]:
                    if suggestion.lower() not in str(requirements).lower():
                        suggestions.append(suggestion)

        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid, issues=issues, warnings=warnings, suggestions=suggestions
        )
