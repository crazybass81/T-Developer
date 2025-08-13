"""
Risk Analyzer Module
Analyzes risks associated with components
"""

from typing import Dict, List, Any, Optional


class RiskAnalyzer:
    """Analyzes component risks"""

    async def analyze(
        self, components: List[Dict[str, Any]], requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze component risks"""

        risk_results = {}

        for component in components:
            component_id = component.get("id", component.get("name"))

            risk_analysis = {
                "technical_risk": self._assess_technical_risk(component),
                "security_risk": self._assess_security_risk(component),
                "maintenance_risk": self._assess_maintenance_risk(component),
                "vendor_risk": self._assess_vendor_risk(component),
                "compliance_risk": self._assess_compliance_risk(
                    component, requirements
                ),
                "overall_risk": 0.0,
            }

            # Calculate overall risk (lower is better)
            risks = [v for k, v in risk_analysis.items() if k != "overall_risk"]
            risk_analysis["overall_risk"] = sum(risks) / len(risks)

            risk_results[component_id] = risk_analysis

        return risk_results

    def _assess_technical_risk(self, component: Dict) -> float:
        """Assess technical risk"""
        # Consider factors like maturity, stability
        maturity = component.get("maturity_years", 2)
        stability = component.get("stability_score", 0.8)

        maturity_risk = max(0.0, (5 - maturity) / 5)  # Higher risk for newer components
        stability_risk = 1 - stability

        return (maturity_risk + stability_risk) / 2

    def _assess_security_risk(self, component: Dict) -> float:
        """Assess security risk"""
        vulnerabilities = component.get("known_vulnerabilities", 0)
        last_security_update = component.get("last_security_update_days", 30)

        vuln_risk = min(1.0, vulnerabilities / 10)
        update_risk = min(1.0, max(0, last_security_update - 90) / 365)

        return (vuln_risk + update_risk) / 2

    def _assess_maintenance_risk(self, component: Dict) -> float:
        """Assess maintenance risk"""
        last_update = component.get("last_updated_days", 30)
        maintainer_count = component.get("maintainers", 1)

        update_risk = min(1.0, max(0, last_update - 90) / 365)
        maintainer_risk = max(0.0, (3 - maintainer_count) / 3)

        return (update_risk + maintainer_risk) / 2

    def _assess_vendor_risk(self, component: Dict) -> float:
        """Assess vendor/dependency risk"""
        is_open_source = component.get("open_source", True)
        vendor_stability = component.get("vendor_stability", 0.8)

        if is_open_source:
            return 1 - vendor_stability * 0.5  # Open source has lower vendor risk
        else:
            return 1 - vendor_stability

    def _assess_compliance_risk(self, component: Dict, requirements: Dict) -> float:
        """Assess compliance risk"""
        required_standards = requirements.get("compliance_standards", [])
        component_compliance = component.get("compliance_certifications", [])

        if not required_standards:
            return 0.0  # No compliance requirements

        compliance_coverage = len(
            set(component_compliance).intersection(set(required_standards))
        )
        total_required = len(required_standards)

        return 1 - (compliance_coverage / total_required) if total_required > 0 else 0.0
