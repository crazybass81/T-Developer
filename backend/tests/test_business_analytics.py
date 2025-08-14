"""
Test suite for Business Analytics and ROI
Day 28: Phase 2 - ServiceImproverAgent
"""

import asyncio
from typing import Dict, List

import pytest

from src.agents.meta.business_analyzer import (
    BusinessAnalyzer,
    BusinessCase,
    BusinessMetrics,
    BusinessReport,
    get_analyzer,
)
from src.analytics.roi_calculator import (
    CostBreakdown,
    ROIAnalysis,
    ROICalculator,
    ValueBreakdown,
    get_calculator,
)
from src.analytics.satisfaction_scorer import (
    SatisfactionMetrics,
    SatisfactionReport,
    SatisfactionScorer,
    UserFeedback,
    get_scorer,
)


class TestBusinessAnalyzer:
    """Test business analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Get analyzer instance"""
        return get_analyzer()

    @pytest.mark.asyncio
    async def test_analyze_improvements(self, analyzer):
        """Test analyzing business improvements"""

        current_state = {
            "performance": 0.6,
            "reliability": 0.7,
            "user_count": 1000,
            "revenue_per_user": 20,
            "monthly_cost": 5000,
        }

        improvements = [
            {
                "type": "optimization",
                "description": "Cache implementation",
                "dev_hours": 15,
                "performance_gain": 0.2,
                "efficiency_gain": 0.15,
                "complexity": 0.3,
                "tested": True,
            }
        ]

        report = await analyzer.analyze(current_state, improvements)

        assert isinstance(report, BusinessReport)
        assert report.metrics is not None
        assert len(report.business_cases) == 1
        assert report.total_value > 0
        assert report.net_benefit != 0

    @pytest.mark.asyncio
    async def test_roi_calculation(self, analyzer):
        """Test ROI calculation in business analysis"""

        current_state = {"performance": 0.5, "user_count": 5000, "revenue_per_user": 50}

        improvements = [
            {
                "type": "performance",
                "dev_hours": 40,
                "performance_gain": 0.5,
                "efficiency_gain": 0.3,
            }
        ]

        report = await analyzer.analyze(current_state, improvements)

        assert report.metrics.roi > 0
        assert report.metrics.efficiency_gain >= 0
        assert len(report.recommendations) > 0

    @pytest.mark.asyncio
    async def test_priority_calculation(self, analyzer):
        """Test improvement priority calculation"""

        current_state = {"performance": 0.7}

        improvements = [
            {
                "type": "critical_fix",
                "dev_hours": 5,
                "performance_gain": 0.1,
                "complexity": 0.2,
                "tested": True,
            },
            {
                "type": "nice_to_have",
                "dev_hours": 50,
                "performance_gain": 0.05,
                "complexity": 0.8,
                "breaking_changes": True,
            },
        ]

        report = await analyzer.analyze(current_state, improvements)

        # First improvement should have higher priority
        assert report.business_cases[0].priority >= report.business_cases[1].priority

    def test_risk_assessment(self, analyzer):
        """Test risk assessment logic"""

        low_risk = {"complexity": 0.2, "tested": True, "breaking_changes": False}

        high_risk = {"complexity": 0.8, "tested": False, "breaking_changes": True}

        assert analyzer._assess_risk(low_risk) == "low"
        assert analyzer._assess_risk(high_risk) == "high"


class TestROICalculator:
    """Test ROI calculator"""

    @pytest.fixture
    def calculator(self):
        """Get calculator instance"""
        return get_calculator()

    def test_calculate_roi(self, calculator):
        """Test comprehensive ROI calculation"""

        specs = {
            "dev_hours": 50,
            "dev_level": "senior_dev",
            "test_hours": 15,
            "deployments": 2,
            "infrastructure": "small",
            "risk_factor": 0.9,
        }

        current = {
            "performance": 1.0,
            "downtime": 3.0,
            "max_users": 500,
            "user_satisfaction": 0.7,
            "efficiency": 0.6,
        }

        target = {
            "performance": 2.0,
            "downtime": 1.0,
            "max_users": 2000,
            "user_satisfaction": 0.85,
            "efficiency": 0.8,
        }

        analysis = calculator.calculate(specs, current, target)

        assert isinstance(analysis, ROIAnalysis)
        assert analysis.roi_percentage != 0
        assert analysis.payback_months > 0
        assert analysis.break_even_point > 0
        assert analysis.five_year_value != 0

    def test_cost_breakdown(self, calculator):
        """Test cost breakdown calculation"""

        specs = {"dev_hours": 40, "test_hours": 10, "deployments": 3, "infrastructure": "medium"}

        costs = calculator._calculate_costs(specs)

        assert isinstance(costs, CostBreakdown)
        assert costs.development > 0
        assert costs.testing > 0
        assert costs.deployment > 0
        assert costs.total == sum(
            [
                costs.development,
                costs.testing,
                costs.deployment,
                costs.maintenance,
                costs.infrastructure,
            ]
        )

    def test_value_calculation(self, calculator):
        """Test value calculation"""

        current = {
            "performance": 1.0,
            "downtime": 5.0,
            "max_users": 100,
            "user_satisfaction": 0.6,
            "efficiency": 0.5,
        }

        target = {
            "performance": 10.0,  # 10x improvement
            "downtime": 1.0,
            "max_users": 1000,
            "user_satisfaction": 0.9,
            "efficiency": 0.9,
        }

        values = calculator._calculate_values(current, target)

        assert isinstance(values, ValueBreakdown)
        assert values.performance_value > 0
        assert values.reliability_value > 0
        assert values.total > 0

    def test_quick_roi(self, calculator):
        """Test quick ROI calculation"""

        roi = calculator.quick_roi(10000, 5000, 3)

        assert roi == 50.0  # (15000 - 10000) / 10000 * 100

    def test_npv_calculation(self, calculator):
        """Test Net Present Value calculation"""

        cash_flows = [-10000, 3000, 4000, 5000, 6000]
        npv = calculator.calculate_npv(cash_flows, 0.1)

        assert npv > 0  # Positive NPV indicates good investment


class TestSatisfactionScorer:
    """Test satisfaction scorer"""

    @pytest.fixture
    def scorer(self):
        """Get scorer instance"""
        return get_scorer()

    def test_analyze_satisfaction(self, scorer):
        """Test satisfaction analysis"""

        user_metrics = {
            "avg_response_time": 300,
            "timeout_rate": 0.01,
            "uptime": 0.99,
            "error_rate": 0.02,
            "task_completion_rate": 0.8,
        }

        feedback_data = [
            {"user_id": "u1", "rating": 4.0, "category": "performance"},
            {"user_id": "u2", "rating": 3.5, "category": "usability"},
            {"user_id": "u3", "rating": 5.0, "category": "features"},
        ]

        report = scorer.analyze(user_metrics, feedback_data)

        assert isinstance(report, SatisfactionReport)
        assert report.metrics.overall_score > 0
        assert report.metrics.overall_score <= 1.0
        assert report.trend in ["improving", "stable", "declining"]

    def test_nps_calculation(self, scorer):
        """Test NPS calculation"""

        feedback = [
            UserFeedback("u1", 5.0, "general", "positive", "low", False),  # Promoter
            UserFeedback("u2", 4.5, "general", "positive", "low", False),  # Promoter
            UserFeedback("u3", 3.0, "general", "neutral", "medium", False),  # Neutral
            UserFeedback("u4", 2.0, "general", "negative", "high", True),  # Detractor
        ]

        nps = scorer._calculate_nps(feedback)

        # (2 promoters - 1 detractor) / 4 * 100 = 25
        assert nps == 25.0

    def test_performance_scoring(self, scorer):
        """Test performance satisfaction scoring"""

        # Fast response time
        fast_metrics = {"avg_response_time": 50, "timeout_rate": 0.001}
        fast_score = scorer._calculate_performance_score(fast_metrics)

        # Slow response time
        slow_metrics = {"avg_response_time": 2000, "timeout_rate": 0.05}
        slow_score = scorer._calculate_performance_score(slow_metrics)

        assert fast_score > slow_score
        assert fast_score > 0.9
        assert slow_score < 0.5

    def test_trend_analysis(self, scorer):
        """Test satisfaction trend analysis"""

        # Improving trend
        improving = scorer._analyze_trend(0.85, [0.70, 0.72, 0.75, 0.78])
        assert improving == "improving"

        # Declining trend
        declining = scorer._analyze_trend(0.65, [0.75, 0.73, 0.72, 0.70])
        assert declining == "declining"

        # Stable trend
        stable = scorer._analyze_trend(0.75, [0.74, 0.75, 0.74, 0.76])
        assert stable == "stable"

    def test_feedback_categorization(self, scorer):
        """Test feedback categorization"""

        feedback = [
            UserFeedback("u1", 4.0, "performance", "positive", "low", False),
            UserFeedback("u2", 3.0, "performance", "neutral", "medium", False),
            UserFeedback("u3", 5.0, "features", "positive", "low", False),
            UserFeedback("u4", 2.0, "bugs", "negative", "high", True),
        ]

        categories = scorer._categorize_feedback(feedback)

        assert "performance" in categories
        assert len(categories["performance"]) == 2
        assert "features" in categories
        assert "bugs" in categories


@pytest.mark.integration
class TestBusinessIntegration:
    """Integration tests for business analytics"""

    @pytest.mark.asyncio
    async def test_complete_business_flow(self):
        """Test complete business analysis flow"""

        # Get all components
        business_analyzer = get_analyzer()
        roi_calculator = get_calculator()
        satisfaction_scorer = get_scorer()

        # Current state
        current_state = {
            "performance": 0.7,
            "reliability": 0.85,
            "user_count": 2000,
            "revenue_per_user": 30,
            "monthly_cost": 8000,
            "downtime": 2.0,
            "max_users": 3000,
            "user_satisfaction": 0.75,
            "efficiency": 0.65,
        }

        # Improvements
        improvements = [
            {
                "type": "performance",
                "description": "Database optimization",
                "dev_hours": 30,
                "performance_gain": 0.4,
                "efficiency_gain": 0.2,
                "complexity": 0.5,
                "tested": True,
            }
        ]

        # User metrics for satisfaction
        user_metrics = {
            "avg_response_time": 400,
            "timeout_rate": 0.02,
            "uptime": 0.985,
            "error_rate": 0.015,
            "task_completion_rate": 0.75,
        }

        # Feedback
        feedback_data = [
            {"user_id": "u1", "rating": 4.0, "category": "performance"},
            {"user_id": "u2", "rating": 3.0, "category": "reliability"},
        ]

        # Analyze business value
        business_report = await business_analyzer.analyze(current_state, improvements)

        # Calculate ROI
        roi_specs = {"dev_hours": 30, "dev_level": "senior_dev", "infrastructure": "medium"}

        target_state = {
            "performance": 1.4,
            "downtime": 1.0,
            "max_users": 5000,
            "user_satisfaction": 0.85,
            "efficiency": 0.85,
        }

        roi_analysis = roi_calculator.calculate(roi_specs, current_state, target_state)

        # Analyze satisfaction
        satisfaction_report = satisfaction_scorer.analyze(user_metrics, feedback_data)

        # Verify results
        print("\nBusiness Analysis Results:")
        print(f"  Business ROI: {business_report.metrics.roi:.1f}%")
        print(f"  Detailed ROI: {roi_analysis.roi_percentage:.1f}%")
        print(f"  Satisfaction: {satisfaction_report.metrics.overall_score:.2f}")
        print(f"  Net Benefit: ${business_report.net_benefit:,.2f}")
        print(f"  Payback: {roi_analysis.payback_months:.1f} months")

        assert business_report.metrics.roi > 0
        assert roi_analysis.roi_percentage > 0
        assert satisfaction_report.metrics.overall_score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
