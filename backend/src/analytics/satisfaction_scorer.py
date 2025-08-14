"""
Satisfaction Scorer - User satisfaction analysis and scoring
Size: < 6.5KB | Performance: < 3μs
Day 28: Phase 2 - ServiceImproverAgent
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class SatisfactionMetrics:
    """User satisfaction metrics"""

    overall_score: float  # 0-1
    performance_score: float
    reliability_score: float
    usability_score: float
    feature_score: float
    support_score: float
    nps_score: float  # Net Promoter Score (-100 to 100)


@dataclass
class UserFeedback:
    """Individual user feedback"""

    user_id: str
    rating: float  # 1-5 stars
    category: str
    sentiment: str  # positive, neutral, negative
    priority: str  # critical, high, medium, low
    actionable: bool


@dataclass
class SatisfactionReport:
    """Complete satisfaction analysis report"""

    metrics: SatisfactionMetrics
    feedback_summary: Dict[str, List[UserFeedback]]
    improvement_areas: List[str]
    strengths: List[str]
    recommendations: List[str]
    trend: str  # improving, stable, declining


class SatisfactionScorer:
    """Analyze and score user satisfaction"""

    def __init__(self):
        self.weights = self._init_weights()
        self.thresholds = self._init_thresholds()

    def _init_weights(self) -> Dict[str, float]:
        """Initialize scoring weights"""
        return {
            "performance": 0.25,
            "reliability": 0.30,
            "usability": 0.20,
            "features": 0.15,
            "support": 0.10,
        }

    def _init_thresholds(self) -> Dict[str, float]:
        """Initialize satisfaction thresholds"""
        return {
            "excellent": 0.9,
            "good": 0.75,
            "acceptable": 0.6,
            "poor": 0.4,
            "critical": 0.2,
        }

    def analyze(
        self,
        user_metrics: Dict[str, any],
        feedback_data: List[Dict[str, any]],
        historical_data: Optional[List[float]] = None,
    ) -> SatisfactionReport:
        """Analyze user satisfaction comprehensively"""

        # Process user feedback
        feedback = self._process_feedback(feedback_data)

        # Calculate metrics
        metrics = self._calculate_metrics(user_metrics, feedback)

        # Categorize feedback
        feedback_summary = self._categorize_feedback(feedback)

        # Identify improvement areas
        improvement_areas = self._identify_improvements(metrics, feedback_summary)

        # Identify strengths
        strengths = self._identify_strengths(metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, improvement_areas)

        # Analyze trend
        trend = self._analyze_trend(metrics.overall_score, historical_data)

        return SatisfactionReport(
            metrics=metrics,
            feedback_summary=feedback_summary,
            improvement_areas=improvement_areas,
            strengths=strengths,
            recommendations=recommendations,
            trend=trend,
        )

    def _process_feedback(self, feedback_data: List[Dict[str, any]]) -> List[UserFeedback]:
        """Process raw feedback data"""

        processed = []

        for item in feedback_data:
            feedback = UserFeedback(
                user_id=item.get("user_id", "anonymous"),
                rating=item.get("rating", 3.0),
                category=item.get("category", "general"),
                sentiment=self._analyze_sentiment(item.get("rating", 3.0)),
                priority=self._determine_priority(item),
                actionable=self._is_actionable(item),
            )
            processed.append(feedback)

        return processed

    def _analyze_sentiment(self, rating: float) -> str:
        """Analyze sentiment from rating"""
        if rating >= 4.0:
            return "positive"
        elif rating >= 3.0:
            return "neutral"
        else:
            return "negative"

    def _determine_priority(self, feedback_item: Dict[str, any]) -> str:
        """Determine feedback priority"""

        rating = feedback_item.get("rating", 3.0)
        impact = feedback_item.get("impact", "medium")
        frequency = feedback_item.get("frequency", 1)

        if rating <= 2.0 and impact == "high":
            return "critical"
        elif rating <= 2.5 or frequency > 10:
            return "high"
        elif rating <= 3.5 or frequency > 5:
            return "medium"
        else:
            return "low"

    def _is_actionable(self, feedback_item: Dict[str, any]) -> bool:
        """Determine if feedback is actionable"""

        # Check if feedback contains specific issues
        has_specifics = feedback_item.get("specific_issue", False)
        has_suggestion = feedback_item.get("suggestion", False)
        is_bug = feedback_item.get("category") == "bug"

        return has_specifics or has_suggestion or is_bug

    def _calculate_metrics(
        self, user_metrics: Dict[str, any], feedback: List[UserFeedback]
    ) -> SatisfactionMetrics:
        """Calculate satisfaction metrics"""

        # Calculate component scores
        performance_score = self._calculate_performance_score(user_metrics)
        reliability_score = self._calculate_reliability_score(user_metrics)
        usability_score = self._calculate_usability_score(user_metrics, feedback)
        feature_score = self._calculate_feature_score(feedback)
        support_score = self._calculate_support_score(feedback)

        # Calculate overall score
        overall_score = (
            performance_score * self.weights["performance"]
            + reliability_score * self.weights["reliability"]
            + usability_score * self.weights["usability"]
            + feature_score * self.weights["features"]
            + support_score * self.weights["support"]
        )

        # Calculate NPS
        nps_score = self._calculate_nps(feedback)

        return SatisfactionMetrics(
            overall_score=overall_score,
            performance_score=performance_score,
            reliability_score=reliability_score,
            usability_score=usability_score,
            feature_score=feature_score,
            support_score=support_score,
            nps_score=nps_score,
        )

    def _calculate_performance_score(self, metrics: Dict[str, any]) -> float:
        """Calculate performance satisfaction score"""

        response_time = metrics.get("avg_response_time", 1000)  # ms
        timeout_rate = metrics.get("timeout_rate", 0.01)

        # Score based on response time
        if response_time < 100:
            time_score = 1.0
        elif response_time < 500:
            time_score = 0.8
        elif response_time < 1000:
            time_score = 0.6
        else:
            time_score = 0.4

        # Adjust for timeouts
        timeout_penalty = min(0.5, timeout_rate * 10)

        return max(0, time_score - timeout_penalty)

    def _calculate_reliability_score(self, metrics: Dict[str, any]) -> float:
        """Calculate reliability satisfaction score"""

        uptime = metrics.get("uptime", 0.99)
        error_rate = metrics.get("error_rate", 0.01)

        # Base score from uptime
        if uptime >= 0.999:
            base_score = 1.0
        elif uptime >= 0.99:
            base_score = 0.8
        elif uptime >= 0.95:
            base_score = 0.6
        else:
            base_score = 0.3

        # Adjust for errors
        error_penalty = min(0.5, error_rate * 10)

        return max(0, base_score - error_penalty)

    def _calculate_usability_score(
        self, metrics: Dict[str, any], feedback: List[UserFeedback]
    ) -> float:
        """Calculate usability satisfaction score"""

        # From metrics
        task_completion = metrics.get("task_completion_rate", 0.8)

        # From feedback
        usability_feedback = [f for f in feedback if f.category == "usability"]
        if usability_feedback:
            avg_rating = sum(f.rating for f in usability_feedback) / len(usability_feedback)
            feedback_score = avg_rating / 5.0
        else:
            feedback_score = 0.7

        return task_completion * 0.6 + feedback_score * 0.4

    def _calculate_feature_score(self, feedback: List[UserFeedback]) -> float:
        """Calculate feature satisfaction score"""

        feature_feedback = [f for f in feedback if f.category == "features"]
        if not feature_feedback:
            return 0.7  # Default

        avg_rating = sum(f.rating for f in feature_feedback) / len(feature_feedback)
        return avg_rating / 5.0

    def _calculate_support_score(self, feedback: List[UserFeedback]) -> float:
        """Calculate support satisfaction score"""

        support_feedback = [f for f in feedback if f.category == "support"]
        if not support_feedback:
            return 0.7  # Default

        avg_rating = sum(f.rating for f in support_feedback) / len(support_feedback)
        return avg_rating / 5.0

    def _calculate_nps(self, feedback: List[UserFeedback]) -> float:
        """Calculate Net Promoter Score"""

        if not feedback:
            return 0

        promoters = len([f for f in feedback if f.rating >= 4.5])
        detractors = len([f for f in feedback if f.rating <= 2.5])
        total = len(feedback)

        nps = ((promoters - detractors) / total) * 100

        return nps

    def _categorize_feedback(self, feedback: List[UserFeedback]) -> Dict[str, List[UserFeedback]]:
        """Categorize feedback by type"""

        categories = {}

        for item in feedback:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        return categories

    def _identify_improvements(
        self, metrics: SatisfactionMetrics, feedback_summary: Dict[str, List[UserFeedback]]
    ) -> List[str]:
        """Identify areas needing improvement"""

        improvements = []

        # Check metric thresholds
        if metrics.performance_score < self.thresholds["acceptable"]:
            improvements.append("Performance optimization needed")

        if metrics.reliability_score < self.thresholds["good"]:
            improvements.append("Improve system reliability")

        if metrics.usability_score < self.thresholds["acceptable"]:
            improvements.append("Enhance user interface")

        # Check feedback patterns
        for category, items in feedback_summary.items():
            negative = [i for i in items if i.sentiment == "negative"]
            if len(negative) > len(items) * 0.3:
                improvements.append(f"Address {category} issues")

        return improvements[:5]

    def _identify_strengths(self, metrics: SatisfactionMetrics) -> List[str]:
        """Identify system strengths"""

        strengths = []

        if metrics.performance_score >= self.thresholds["excellent"]:
            strengths.append("Excellent performance")

        if metrics.reliability_score >= self.thresholds["excellent"]:
            strengths.append("High reliability")

        if metrics.nps_score > 50:
            strengths.append("Strong user advocacy")

        if metrics.overall_score >= self.thresholds["good"]:
            strengths.append("Good overall satisfaction")

        return strengths

    def _generate_recommendations(
        self, metrics: SatisfactionMetrics, improvements: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Priority recommendations
        if metrics.overall_score < self.thresholds["acceptable"]:
            recommendations.append("Urgent: Address critical satisfaction issues")

        # Specific recommendations
        if "Performance" in str(improvements):
            recommendations.append("Implement caching and query optimization")

        if "reliability" in str(improvements).lower():
            recommendations.append("Add redundancy and error recovery")

        if "interface" in str(improvements).lower():
            recommendations.append("Conduct UX review and redesign")

        # NPS-based recommendations
        if metrics.nps_score < 0:
            recommendations.append("Focus on converting detractors to neutrals")
        elif metrics.nps_score < 30:
            recommendations.append("Work on creating more promoters")

        return recommendations[:5]

    def _analyze_trend(self, current_score: float, historical: Optional[List[float]]) -> str:
        """Analyze satisfaction trend"""

        if not historical or len(historical) < 2:
            return "stable"

        # Calculate trend
        recent_avg = sum(historical[-3:]) / len(historical[-3:])

        if current_score > recent_avg * 1.05:  # More sensitive to improvements
            return "improving"
        elif current_score < recent_avg * 0.95:  # More sensitive to declines
            return "declining"
        else:
            return "stable"

    def get_metrics(self) -> Dict[str, any]:
        """Get scorer metrics"""
        return {"weights": self.weights, "thresholds": self.thresholds}


# Global instance
scorer = None


def get_scorer() -> SatisfactionScorer:
    """Get or create scorer instance"""
    global scorer
    if not scorer:
        scorer = SatisfactionScorer()
    return scorer


def main():
    """Test satisfaction scorer"""
    scorer = get_scorer()

    # User metrics
    user_metrics = {
        "avg_response_time": 250,  # ms
        "timeout_rate": 0.005,
        "uptime": 0.995,
        "error_rate": 0.01,
        "task_completion_rate": 0.85,
    }

    # Feedback data
    feedback_data = [
        {"user_id": "u1", "rating": 4.5, "category": "performance"},
        {"user_id": "u2", "rating": 3.0, "category": "usability", "specific_issue": True},
        {"user_id": "u3", "rating": 5.0, "category": "features"},
        {"user_id": "u4", "rating": 2.0, "category": "reliability", "impact": "high"},
        {"user_id": "u5", "rating": 4.0, "category": "support"},
    ]

    # Historical scores
    historical = [0.72, 0.74, 0.73, 0.75]

    report = scorer.analyze(user_metrics, feedback_data, historical)

    print("Satisfaction Analysis:")
    print(f"  Overall Score: {report.metrics.overall_score:.2f}")
    print(f"  NPS Score: {report.metrics.nps_score:.1f}")
    print(f"  Trend: {report.trend}")

    print("\nComponent Scores:")
    print(f"  Performance: {report.metrics.performance_score:.2f}")
    print(f"  Reliability: {report.metrics.reliability_score:.2f}")
    print(f"  Usability: {report.metrics.usability_score:.2f}")

    print("\nStrengths:")
    for strength in report.strengths:
        print(f"  - {strength}")

    print("\nImprovement Areas:")
    for area in report.improvement_areas:
        print(f"  - {area}")

    print("\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    main()
