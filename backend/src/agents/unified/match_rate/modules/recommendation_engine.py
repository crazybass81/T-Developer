"""
Recommendation Engine Module
Generates recommendations based on match analysis
"""

from typing import Dict, List, Any, Optional


class RecommendationEngine:
    """Generates intelligent recommendations"""

    async def generate(
        self, components: List[Dict[str, Any]], requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations"""

        recommendations = []

        # Analyze components for recommendations
        for component in components:
            component_id = component.get("id", component.get("name"))

            # Generate component-specific recommendations
            component_recommendations = self._generate_component_recommendations(
                component, requirements
            )

            recommendations.extend(component_recommendations)

        # Add general recommendations
        general_recommendations = self._generate_general_recommendations(
            components, requirements
        )
        recommendations.extend(general_recommendations)

        # Sort by priority
        recommendations.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return recommendations[:10]  # Top 10 recommendations

    def _generate_component_recommendations(
        self, component: Dict, requirements: Dict
    ) -> List[Dict[str, Any]]:
        """Generate component-specific recommendations"""

        recommendations = []
        component_name = component.get("name", "Component")

        # Performance recommendations
        if component.get("performance_score", 0.8) < 0.6:
            recommendations.append(
                {
                    "type": "performance",
                    "component": component_name,
                    "message": f"Consider performance optimization for {component_name}",
                    "priority": 8,
                    "action": "optimization",
                }
            )

        # Security recommendations
        if component.get("security_score", 0.8) < 0.7:
            recommendations.append(
                {
                    "type": "security",
                    "component": component_name,
                    "message": f"Review security features of {component_name}",
                    "priority": 9,
                    "action": "security_review",
                }
            )

        # Maintenance recommendations
        last_update = component.get("last_updated_days", 30)
        if last_update > 180:
            recommendations.append(
                {
                    "type": "maintenance",
                    "component": component_name,
                    "message": f"{component_name} hasn't been updated recently - consider alternatives",
                    "priority": 6,
                    "action": "evaluate_alternatives",
                }
            )

        return recommendations

    def _generate_general_recommendations(
        self, components: List[Dict], requirements: Dict
    ) -> List[Dict[str, Any]]:
        """Generate general recommendations"""

        recommendations = []

        # Budget recommendations
        total_cost = sum(component.get("cost", 1000) for component in components)
        budget = requirements.get("budget", 10000)

        if total_cost > budget:
            recommendations.append(
                {
                    "type": "budget",
                    "message": f"Total cost (${total_cost}) exceeds budget (${budget})",
                    "priority": 8,
                    "action": "cost_optimization",
                }
            )

        # Technology diversity recommendation
        technologies = set()
        for component in components:
            tech = component.get("technology", "unknown")
            technologies.add(tech)

        if len(technologies) > 5:
            recommendations.append(
                {
                    "type": "architecture",
                    "message": "High technology diversity may increase complexity",
                    "priority": 5,
                    "action": "simplify_stack",
                }
            )

        return recommendations
