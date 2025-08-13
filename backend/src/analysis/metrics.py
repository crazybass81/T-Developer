"""
Analysis Metrics and Quality Assessment
Day 7: AI Analysis Engine
Generated: 2024-11-18

Measure and validate quality of AI analysis results
"""

import statistics
from datetime import datetime
from typing import Dict, List


class AnalysisQualityChecker:
    """Assess quality of analysis results"""

    def __init__(self):
        self.quality_thresholds = {
            "min_confidence": 0.7,
            "max_response_time": 2.0,  # seconds
            "min_completeness": 0.8,
        }

    def assess_quality(self, analysis_result: Dict) -> Dict:
        """Assess overall quality of an analysis result"""
        quality_metrics = {}

        # Completeness score
        quality_metrics["completeness"] = self._calculate_completeness(analysis_result)

        # Confidence score
        quality_metrics["accuracy_confidence"] = analysis_result.get("confidence", 0.0)

        # Response time score
        response_time = analysis_result.get("execution_time", 0.5)
        quality_metrics["response_time"] = self._score_response_time(response_time)

        # Recommendation quality
        quality_metrics["recommendation_quality"] = self._assess_recommendations(
            analysis_result.get("recommendations", [])
        )

        # Overall score (weighted average)
        weights = {
            "completeness": 0.3,
            "accuracy_confidence": 0.3,
            "response_time": 0.2,
            "recommendation_quality": 0.2,
        }

        overall_score = sum(quality_metrics[metric] * weight for metric, weight in weights.items())

        quality_metrics["overall_score"] = overall_score
        quality_metrics["quality_grade"] = self._grade_quality(overall_score)

        return quality_metrics

    def _calculate_completeness(self, result: Dict) -> float:
        """Calculate completeness score based on expected fields"""
        expected_fields = ["issues", "confidence", "recommendations"]
        present_fields = sum(1 for field in expected_fields if field in result)

        return present_fields / len(expected_fields)

    def _score_response_time(self, response_time: float) -> float:
        """Score response time (lower is better)"""
        max_time = self.quality_thresholds["max_response_time"]
        if response_time <= max_time:
            return 1.0 - (response_time / max_time) * 0.5  # Max penalty 50%
        else:
            return max(0.0, 1.0 - (response_time / max_time))

    def _assess_recommendations(self, recommendations: List[str]) -> float:
        """Assess quality of recommendations"""
        if not recommendations:
            return 0.0

        quality_score = 0.0

        # Check for specific, actionable recommendations
        for rec in recommendations:
            if len(rec) > 20:  # Detailed recommendation
                quality_score += 0.3
            if any(keyword in rec.lower() for keyword in ["optimize", "refactor", "improve"]):
                quality_score += 0.2
            if any(keyword in rec.lower() for keyword in ["use", "consider", "implement"]):
                quality_score += 0.1

        return min(1.0, quality_score / len(recommendations))

    def _grade_quality(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"


class ConsistencyChecker:
    """Check consistency of analysis results across multiple runs"""

    def __init__(self):
        self.results: List[Dict] = []

    def add_result(self, result: Dict):
        """Add analysis result for consistency checking"""
        self.results.append(result)

    def calculate_consistency(self) -> Dict:
        """Calculate consistency metrics"""
        if len(self.results) < 2:
            return {"insufficient_data": True}

        consistency_metrics = {}

        # Issue consistency
        consistency_metrics["issue_consistency"] = self._calculate_issue_consistency()

        # Confidence variance
        consistency_metrics["confidence_variance"] = self._calculate_confidence_variance()

        # Recommendation consistency
        consistency_metrics[
            "recommendation_consistency"
        ] = self._calculate_recommendation_consistency()

        # Overall consistency score
        consistency_metrics["overall_consistency"] = self._calculate_overall_consistency(
            consistency_metrics
        )

        return consistency_metrics

    def _calculate_issue_consistency(self) -> float:
        """Calculate how consistent issue detection is"""
        all_issues = set()
        result_issues = []

        for result in self.results:
            issues = set(result.get("issues", []))
            all_issues.update(issues)
            result_issues.append(issues)

        if not all_issues:
            return 1.0  # No issues detected consistently

        # Calculate Jaccard similarity for each pair
        similarities = []
        for i in range(len(result_issues)):
            for j in range(i + 1, len(result_issues)):
                intersection = len(result_issues[i] & result_issues[j])
                union = len(result_issues[i] | result_issues[j])
                similarity = intersection / union if union > 0 else 1.0
                similarities.append(similarity)

        return statistics.mean(similarities) if similarities else 0.0

    def _calculate_confidence_variance(self) -> float:
        """Calculate variance in confidence scores"""
        confidences = [r.get("confidence", 0.0) for r in self.results]

        if len(confidences) < 2:
            return 0.0

        variance = statistics.variance(confidences)
        # Normalize to 0-1 range (lower variance is better)
        return max(0.0, 1.0 - variance)

    def _calculate_recommendation_consistency(self) -> float:
        """Calculate consistency in recommendations"""
        all_recommendations = []

        for result in self.results:
            recommendations = result.get("recommendations", [])
            all_recommendations.extend(recommendations)

        if not all_recommendations:
            return 1.0

        # Count recommendation frequency
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1

        # Calculate entropy-based consistency
        total_recs = len(all_recommendations)
        entropy = 0.0

        for count in rec_counts.values():
            probability = count / total_recs
            entropy -= probability * (probability.bit_length() - 1) if probability > 0 else 0

        max_entropy = (len(rec_counts).bit_length() - 1) if len(rec_counts) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Convert to consistency score (lower entropy = higher consistency)
        return 1.0 - normalized_entropy

    def _calculate_overall_consistency(self, metrics: Dict) -> float:
        """Calculate overall consistency score"""
        weights = {
            "issue_consistency": 0.4,
            "confidence_variance": 0.3,
            "recommendation_consistency": 0.3,
        }

        total_score = sum(
            metrics.get(metric, 0.0) * weight
            for metric, weight in weights.items()
            if metric in metrics
        )

        return total_score


class FalsePositiveDetector:
    """Detect false positive issues in analysis results"""

    def __init__(self):
        self.historical_data: List[Dict] = []

    def add_historical_data(
        self, reported_issue: str, actual_improvement: float, confidence: float
    ):
        """Add historical data point for false positive analysis"""
        self.historical_data.append(
            {
                "reported_issue": reported_issue,
                "actual_improvement": actual_improvement,
                "confidence": confidence,
                "timestamp": datetime.utcnow(),
            }
        )

    def calculate_false_positive_rate(self) -> float:
        """Calculate overall false positive rate"""
        if not self.historical_data:
            return 0.0

        # Define threshold for "real" improvement
        improvement_threshold = 0.05  # 5% improvement

        false_positives = 0
        total_predictions = len(self.historical_data)

        for data in self.historical_data:
            if data["actual_improvement"] < improvement_threshold:
                false_positives += 1

        return false_positives / total_predictions

    def get_issue_false_positive_rates(self) -> Dict[str, float]:
        """Get false positive rates by issue type"""
        issue_data = {}

        for data in self.historical_data:
            issue = data["reported_issue"]
            if issue not in issue_data:
                issue_data[issue] = {"total": 0, "false_positives": 0}

            issue_data[issue]["total"] += 1
            if data["actual_improvement"] < 0.05:  # 5% threshold
                issue_data[issue]["false_positives"] += 1

        # Calculate rates
        false_positive_rates = {}
        for issue, counts in issue_data.items():
            if counts["total"] > 0:
                false_positive_rates[issue] = counts["false_positives"] / counts["total"]

        return false_positive_rates

    def predict_false_positive_probability(self, issue: str, confidence: float) -> float:
        """Predict probability of false positive for new issue"""
        # Filter historical data for this issue type
        issue_data = [d for d in self.historical_data if d["reported_issue"] == issue]

        if not issue_data:
            return 0.5  # Default probability if no historical data

        # Find similar confidence levels (±0.1)
        similar_data = [d for d in issue_data if abs(d["confidence"] - confidence) <= 0.1]

        if not similar_data:
            similar_data = issue_data  # Use all data for this issue

        # Calculate false positive rate for similar cases
        false_positives = sum(1 for d in similar_data if d["actual_improvement"] < 0.05)

        return false_positives / len(similar_data)


class PerformanceMetrics:
    """Track performance metrics of the analysis system"""

    def __init__(self):
        self.metrics = {
            "total_analyses": 0,
            "average_latency": 0.0,
            "peak_latency": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0,  # analyses per second
            "latencies": [],
            "errors": 0,
            "start_time": datetime.utcnow(),
        }

    def record_analysis(self, latency: float, success: bool):
        """Record completion of an analysis"""
        self.metrics["total_analyses"] += 1
        self.metrics["latencies"].append(latency)

        if not success:
            self.metrics["errors"] += 1

        # Update peak latency
        if latency > self.metrics["peak_latency"]:
            self.metrics["peak_latency"] = latency

        # Update averages
        self._update_averages()

    def _update_averages(self):
        """Update average metrics"""
        if self.metrics["latencies"]:
            self.metrics["average_latency"] = statistics.mean(self.metrics["latencies"])

        if self.metrics["total_analyses"] > 0:
            self.metrics["error_rate"] = self.metrics["errors"] / self.metrics["total_analyses"]

        # Calculate throughput
        elapsed_time = (datetime.utcnow() - self.metrics["start_time"]).total_seconds()
        if elapsed_time > 0:
            self.metrics["throughput"] = self.metrics["total_analyses"] / elapsed_time

    def get_percentile_latency(self, percentile: float) -> float:
        """Get latency at specified percentile"""
        if not self.metrics["latencies"]:
            return 0.0

        sorted_latencies = sorted(self.metrics["latencies"])
        index = int(len(sorted_latencies) * percentile / 100)
        index = max(0, min(index, len(sorted_latencies) - 1))

        return sorted_latencies[index]

    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return {
            "total_analyses": self.metrics["total_analyses"],
            "average_latency": self.metrics["average_latency"],
            "p95_latency": self.get_percentile_latency(95),
            "p99_latency": self.get_percentile_latency(99),
            "peak_latency": self.metrics["peak_latency"],
            "error_rate": self.metrics["error_rate"],
            "throughput": self.metrics["throughput"],
            "uptime_minutes": (datetime.utcnow() - self.metrics["start_time"]).total_seconds() / 60,
        }

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "total_analyses": 0,
            "average_latency": 0.0,
            "peak_latency": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0,
            "latencies": [],
            "errors": 0,
            "start_time": datetime.utcnow(),
        }
