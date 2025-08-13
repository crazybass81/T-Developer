"""
Analysis History Tracking
Day 7: AI Analysis Engine
Generated: 2024-11-18

Track analysis results over time and detect trends and patterns
"""

from datetime import datetime
from typing import Dict, List


class AnalysisHistory:
    """Track analysis results over time for trend analysis"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.analyses: List[Dict] = []

    def add_analysis(self, timestamp: datetime, score: float, issues: List[str]):
        """Add a new analysis result to history"""
        analysis = {
            "timestamp": timestamp,
            "score": score,
            "issues": issues,
            "issue_count": len(issues),
        }

        self.analyses.append(analysis)

        # Sort by timestamp to maintain chronological order
        self.analyses.sort(key=lambda x: x["timestamp"])

    def get_trend(self) -> str:
        """Analyze overall trend of the agent performance"""
        if len(self.analyses) < 2:
            return "insufficient_data"

        # Compare first and last scores
        first_score = self.analyses[0]["score"]
        last_score = self.analyses[-1]["score"]

        if last_score > first_score + 0.1:  # Significant improvement
            return "improving"
        elif last_score < first_score - 0.1:  # Significant degradation
            return "degrading"
        else:
            return "stable"

    def get_improvement_rate(self) -> float:
        """Calculate rate of improvement over time"""
        if len(self.analyses) < 2:
            return 0.0

        first_score = self.analyses[0]["score"]
        last_score = self.analyses[-1]["score"]

        time_span = (self.analyses[-1]["timestamp"] - self.analyses[0]["timestamp"]).days
        if time_span == 0:
            time_span = 1  # Avoid division by zero

        improvement = last_score - first_score
        return improvement / time_span  # Improvement per day

    def get_recent_analyses(self, count: int = 5) -> List[Dict]:
        """Get the most recent analysis results"""
        return self.analyses[-count:] if len(self.analyses) >= count else self.analyses

    def get_score_variance(self) -> float:
        """Calculate variance in scores to measure stability"""
        if len(self.analyses) < 2:
            return 0.0

        scores = [a["score"] for a in self.analyses]
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)

        return variance


class IssueTracker:
    """Track when specific issues are detected and resolved"""

    def __init__(self):
        self.issue_history: Dict[int, List[str]] = {}  # generation -> issues
        self.resolution_history: Dict[str, Dict] = {}  # issue -> resolution info

    def record_issues(self, issues: List[str], generation: int):
        """Record issues found in a specific generation"""
        self.issue_history[generation] = issues

        # Check for newly resolved issues
        if generation > 1:
            previous_issues = set(self.issue_history.get(generation - 1, []))
            current_issues = set(issues)
            resolved_issues = previous_issues - current_issues

            for issue in resolved_issues:
                if issue not in self.resolution_history:
                    self.resolution_history[issue] = {
                        "first_detected": self._find_first_occurrence(issue),
                        "resolved_in_generation": generation,
                        "resolution_time_generations": generation
                        - self._find_first_occurrence(issue),
                    }

    def get_resolution_history(self) -> Dict[str, Dict]:
        """Get history of issue resolutions"""
        return self.resolution_history

    def get_persistent_issues(self, min_generations: int = 3) -> List[str]:
        """Get issues that have persisted for multiple generations"""
        if not self.issue_history:
            return []

        # Find issues present in recent generations
        recent_generations = sorted(self.issue_history.keys())[-min_generations:]
        if len(recent_generations) < min_generations:
            return []

        # Find issues common to all recent generations
        persistent = set(self.issue_history[recent_generations[0]])
        for gen in recent_generations[1:]:
            persistent &= set(self.issue_history[gen])

        return list(persistent)

    def _find_first_occurrence(self, issue: str) -> int:
        """Find the first generation where an issue was detected"""
        for generation in sorted(self.issue_history.keys()):
            if issue in self.issue_history[generation]:
                return generation
        return 1  # Default to generation 1 if not found


class PatternDetector:
    """Detect patterns in analysis results over time"""

    def __init__(self):
        self.analyses: List[Dict] = []

    def add_analysis(self, analysis: Dict):
        """Add analysis result for pattern detection"""
        self.analyses.append(analysis)

    def detect_patterns(self) -> Dict:
        """Detect patterns in the analysis data"""
        if len(self.analyses) < 3:
            return {"insufficient_data": True}

        patterns = {}

        # Detect recurring issues
        patterns["recurring_issues"] = self._find_recurring_issues()

        # Detect cyclical patterns
        patterns["cyclical_patterns"] = self._detect_cycles()

        # Detect improvement plateaus
        patterns["plateaus"] = self._detect_plateaus()

        return patterns

    def _find_recurring_issues(self) -> List[str]:
        """Find issues that appear repeatedly"""
        issue_counts = {}

        for analysis in self.analyses:
            issues = analysis.get("issues", [])
            for issue in issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Return issues that appear in at least 50% of analyses
        threshold = len(self.analyses) * 0.5
        recurring = [issue for issue, count in issue_counts.items() if count >= threshold]

        return recurring

    def _detect_cycles(self) -> Dict:
        """Detect cyclical patterns in issues"""
        if len(self.analyses) < 6:
            return {"detected": False}

        # Simple cycle detection: look for repeating issue patterns
        issue_sequences = [set(a.get("issues", [])) for a in self.analyses]

        # Look for repeating 2-3 step patterns
        for cycle_length in [2, 3]:
            if self._has_repeating_pattern(issue_sequences, cycle_length):
                return {"detected": True, "cycle_length": cycle_length, "confidence": 0.7}

        return {"detected": False}

    def _has_repeating_pattern(self, sequences: List[set], cycle_length: int) -> bool:
        """Check if there's a repeating pattern of given length"""
        if len(sequences) < cycle_length * 2:
            return False

        # Check if pattern repeats at least twice
        for start in range(len(sequences) - cycle_length * 2 + 1):
            pattern = sequences[start : start + cycle_length]
            next_pattern = sequences[start + cycle_length : start + cycle_length * 2]

            if pattern == next_pattern:
                return True

        return False

    def _detect_plateaus(self) -> Dict:
        """Detect periods where improvement has plateaued"""
        if len(self.analyses) < 5:
            return {"detected": False}

        # Look for recent period with minimal score changes
        recent_count = min(5, len(self.analyses))
        recent_analyses = self.analyses[-recent_count:]

        scores = [a.get("score", 0) for a in recent_analyses if "score" in a]
        if len(scores) < 3:
            return {"detected": False}

        # Calculate variance in recent scores
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)

        # Low variance indicates plateau
        if variance < 0.01:  # Threshold for plateau detection
            return {
                "detected": True,
                "duration": recent_count,
                "average_score": mean_score,
                "variance": variance,
            }

        return {"detected": False}


class TrendAnalyzer:
    """Advanced trend analysis for agent performance"""

    def __init__(self):
        self.data_points: List[Dict] = []

    def add_data_point(self, timestamp: datetime, metrics: Dict):
        """Add a data point for trend analysis"""
        self.data_points.append({"timestamp": timestamp, "metrics": metrics})

        # Sort by timestamp
        self.data_points.sort(key=lambda x: x["timestamp"])

    def calculate_trend_slope(self, metric_name: str) -> float:
        """Calculate trend slope for a specific metric using linear regression"""
        if len(self.data_points) < 2:
            return 0.0

        # Extract metric values
        values = []
        for point in self.data_points:
            value = point["metrics"].get(metric_name)
            if value is not None:
                values.append(value)

        if len(values) < 2:
            return 0.0

        # Simple linear regression
        n = len(values)
        x_values = list(range(n))

        # Calculate slope
        x_sum = sum(x_values)
        y_sum = sum(values)
        xy_sum = sum(x * y for x, y in zip(x_values, values))
        x2_sum = sum(x * x for x in x_values)

        # Slope = (n*Σ(xy) - Σ(x)*Σ(y)) / (n*Σ(x²) - (Σ(x))²)
        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0

        slope = (n * xy_sum - x_sum * y_sum) / denominator
        return slope

    def detect_anomalies(self, metric_name: str, threshold: float = 2.0) -> List[Dict]:
        """Detect anomalous values in a metric"""
        if len(self.data_points) < 3:
            return []

        values = []
        for point in self.data_points:
            value = point["metrics"].get(metric_name)
            if value is not None:
                values.append((point["timestamp"], value))

        if len(values) < 3:
            return []

        # Calculate mean and standard deviation
        metric_values = [v[1] for v in values]
        mean = sum(metric_values) / len(metric_values)
        variance = sum((v - mean) ** 2 for v in metric_values) / len(metric_values)
        std_dev = variance**0.5

        if std_dev == 0:
            return []

        # Find anomalies (values beyond threshold standard deviations)
        anomalies = []
        for timestamp, value in values:
            z_score = abs(value - mean) / std_dev
            if z_score > threshold:
                anomalies.append(
                    {
                        "timestamp": timestamp,
                        "value": value,
                        "z_score": z_score,
                        "severity": "high" if z_score > 3.0 else "medium",
                    }
                )

        return anomalies
