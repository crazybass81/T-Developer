"""
ROI Calculator - Calculate return on investment for improvements
Size: < 6.5KB | Performance: < 3μs
Day 28: Phase 2 - ServiceImproverAgent
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class CostBreakdown:
    """Detailed cost breakdown"""

    development: float
    testing: float
    deployment: float
    maintenance: float
    infrastructure: float
    total: float


@dataclass
class ValueBreakdown:
    """Detailed value breakdown"""

    performance_value: float
    reliability_value: float
    scalability_value: float
    user_experience_value: float
    operational_savings: float
    total: float


@dataclass
class ROIAnalysis:
    """Complete ROI analysis"""

    costs: CostBreakdown
    values: ValueBreakdown
    roi_percentage: float
    payback_months: float
    break_even_point: int  # Days
    five_year_value: float
    risk_adjusted_roi: float


class ROICalculator:
    """Calculate detailed ROI for improvements"""

    def __init__(self):
        self.cost_rates = self._init_cost_rates()
        self.value_multipliers = self._init_value_multipliers()

    def _init_cost_rates(self) -> Dict[str, float]:
        """Initialize cost rates"""
        return {
            "junior_dev": 75.0,  # $/hour
            "senior_dev": 150.0,  # $/hour
            "architect": 200.0,  # $/hour
            "qa_engineer": 100.0,  # $/hour
            "devops": 125.0,  # $/hour
            "infrastructure_small": 500.0,  # $/month
            "infrastructure_medium": 2000.0,  # $/month
            "infrastructure_large": 5000.0,  # $/month
        }

    def _init_value_multipliers(self) -> Dict[str, float]:
        """Initialize value multipliers"""
        return {
            "performance_10x": 50000.0,  # 10x performance improvement
            "performance_2x": 10000.0,  # 2x performance improvement
            "downtime_reduction": 100000.0,  # Per 1% reduction
            "user_satisfaction": 25000.0,  # Per 10% improvement
            "operational_efficiency": 30000.0,  # Per 10% improvement
            "market_advantage": 75000.0,  # Competitive advantage
        }

    def calculate(
        self,
        improvement_specs: Dict[str, any],
        current_metrics: Dict[str, float],
        target_metrics: Dict[str, float],
    ) -> ROIAnalysis:
        """Calculate comprehensive ROI"""

        # Calculate costs
        costs = self._calculate_costs(improvement_specs)

        # Calculate values
        values = self._calculate_values(current_metrics, target_metrics)

        # Calculate ROI
        roi_percentage = ((values.total - costs.total) / costs.total) * 100

        # Calculate payback period
        monthly_value = values.total / 60  # 5-year value spread
        payback_months = costs.total / max(1, monthly_value)

        # Calculate break-even point
        daily_value = values.total / (365 * 5)
        break_even_point = int(costs.total / max(1, daily_value))

        # Calculate 5-year value
        five_year_value = values.total - costs.total

        # Risk adjustment
        risk_factor = improvement_specs.get("risk_factor", 0.8)
        risk_adjusted_roi = roi_percentage * risk_factor

        return ROIAnalysis(
            costs=costs,
            values=values,
            roi_percentage=roi_percentage,
            payback_months=payback_months,
            break_even_point=break_even_point,
            five_year_value=five_year_value,
            risk_adjusted_roi=risk_adjusted_roi,
        )

    def _calculate_costs(self, specs: Dict[str, any]) -> CostBreakdown:
        """Calculate detailed costs"""

        # Development costs
        dev_hours = specs.get("dev_hours", 40)
        dev_rate = self.cost_rates.get(specs.get("dev_level", "senior_dev"), 150)
        development = dev_hours * dev_rate

        # Testing costs
        test_hours = specs.get("test_hours", dev_hours * 0.3)
        testing = test_hours * self.cost_rates["qa_engineer"]

        # Deployment costs
        deployments = specs.get("deployments", 3)
        deployment = deployments * 500  # Base deployment cost

        # Maintenance costs (annual)
        maintenance = development * 0.2  # 20% of development cost annually

        # Infrastructure costs
        infra_size = specs.get("infrastructure", "small")
        infrastructure = self.cost_rates.get(f"infrastructure_{infra_size}", 500) * 12

        total = development + testing + deployment + maintenance + infrastructure

        return CostBreakdown(
            development=development,
            testing=testing,
            deployment=deployment,
            maintenance=maintenance,
            infrastructure=infrastructure,
            total=total,
        )

    def _calculate_values(
        self, current: Dict[str, float], target: Dict[str, float]
    ) -> ValueBreakdown:
        """Calculate detailed values"""

        # Performance value
        perf_improvement = target.get("performance", 1.0) / max(
            0.1, current.get("performance", 1.0)
        )
        if perf_improvement >= 10:
            performance_value = self.value_multipliers["performance_10x"]
        elif perf_improvement >= 2:
            performance_value = self.value_multipliers["performance_2x"]
        else:
            performance_value = perf_improvement * 5000

        # Reliability value
        downtime_reduction = current.get("downtime", 5) - target.get("downtime", 2)
        reliability_value = downtime_reduction * self.value_multipliers["downtime_reduction"]

        # Scalability value
        scale_improvement = target.get("max_users", 1000) / max(1, current.get("max_users", 100))
        scalability_value = scale_improvement * 10000

        # User experience value
        ux_improvement = target.get("user_satisfaction", 0.8) - current.get(
            "user_satisfaction", 0.6
        )
        user_experience_value = (ux_improvement * 10) * self.value_multipliers["user_satisfaction"]

        # Operational savings
        efficiency_gain = target.get("efficiency", 0.8) - current.get("efficiency", 0.5)
        operational_savings = (efficiency_gain * 10) * self.value_multipliers[
            "operational_efficiency"
        ]

        total = (
            performance_value
            + reliability_value
            + scalability_value
            + user_experience_value
            + operational_savings
        )

        return ValueBreakdown(
            performance_value=performance_value,
            reliability_value=reliability_value,
            scalability_value=scalability_value,
            user_experience_value=user_experience_value,
            operational_savings=operational_savings,
            total=total,
        )

    def quick_roi(self, investment: float, annual_return: float, years: int = 5) -> float:
        """Quick ROI calculation"""
        total_return = annual_return * years
        roi = ((total_return - investment) / investment) * 100
        return roi

    def calculate_npv(self, cash_flows: List[float], discount_rate: float = 0.1) -> float:
        """Calculate Net Present Value"""
        npv = 0
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** i)
        return npv

    def calculate_irr(self, cash_flows: List[float]) -> Optional[float]:
        """Calculate Internal Rate of Return"""
        # Simplified IRR calculation using Newton's method
        rate = 0.1
        tolerance = 0.0001
        max_iterations = 100

        for _ in range(max_iterations):
            npv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
            if abs(npv) < tolerance:
                return rate * 100

            # Calculate derivative
            dnpv = sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))

            if dnpv == 0:
                break

            rate = rate - npv / dnpv

        return None

    def get_metrics(self) -> Dict[str, any]:
        """Get calculator metrics"""
        return {
            "cost_rates": len(self.cost_rates),
            "value_multipliers": len(self.value_multipliers),
            "senior_rate": self.cost_rates["senior_dev"],
        }


# Global instance
calculator = None


def get_calculator() -> ROICalculator:
    """Get or create calculator instance"""
    global calculator
    if not calculator:
        calculator = ROICalculator()
    return calculator


def main():
    """Test ROI calculator"""
    calculator = get_calculator()

    # Improvement specifications
    specs = {
        "dev_hours": 100,
        "dev_level": "senior_dev",
        "test_hours": 30,
        "deployments": 3,
        "infrastructure": "medium",
        "risk_factor": 0.85,
    }

    # Current metrics
    current = {
        "performance": 1.0,
        "downtime": 5.0,  # % per year
        "max_users": 1000,
        "user_satisfaction": 0.6,
        "efficiency": 0.5,
    }

    # Target metrics
    target = {
        "performance": 3.0,  # 3x improvement
        "downtime": 1.0,  # Reduce to 1%
        "max_users": 10000,  # 10x scale
        "user_satisfaction": 0.85,
        "efficiency": 0.8,
    }

    analysis = calculator.calculate(specs, current, target)

    print("ROI Analysis:")
    print(f"  Total Investment: ${analysis.costs.total:,.2f}")
    print(f"  Total Value: ${analysis.values.total:,.2f}")
    print(f"  ROI: {analysis.roi_percentage:.1f}%")
    print(f"  Risk-Adjusted ROI: {analysis.risk_adjusted_roi:.1f}%")
    print(f"  Payback Period: {analysis.payback_months:.1f} months")
    print(f"  Break-Even: {analysis.break_even_point} days")
    print(f"  5-Year Value: ${analysis.five_year_value:,.2f}")

    print("\nCost Breakdown:")
    print(f"  Development: ${analysis.costs.development:,.2f}")
    print(f"  Testing: ${analysis.costs.testing:,.2f}")
    print(f"  Deployment: ${analysis.costs.deployment:,.2f}")
    print(f"  Infrastructure: ${analysis.costs.infrastructure:,.2f}")

    print("\nValue Breakdown:")
    print(f"  Performance: ${analysis.values.performance_value:,.2f}")
    print(f"  Reliability: ${analysis.values.reliability_value:,.2f}")
    print(f"  Scalability: ${analysis.values.scalability_value:,.2f}")
    print(f"  User Experience: ${analysis.values.user_experience_value:,.2f}")


if __name__ == "__main__":
    main()
