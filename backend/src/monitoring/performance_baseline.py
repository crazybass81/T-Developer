"""
Performance Baseline Tracker
Day 5: TDD Implementation - GREEN Phase
Generated: 2024-11-18

Establishes and monitors performance baselines for Evolution System
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class PerformanceBaseline:
    """Establish and monitor performance baselines"""

    def __init__(self):
        """Initialize performance baseline tracker"""
        self.baselines = {}
        self.measurements = []
        self._established = False

        # Statistical parameters
        self.confidence_level = 0.95
        self.z_score_threshold = 3.0  # For anomaly detection

    def establish(self, measurements: List[Dict]):
        """Establish baseline from measurements"""
        if not measurements:
            raise ValueError("Cannot establish baseline without measurements")

        self.measurements = measurements

        # Calculate baselines for each metric
        metrics = {}
        for measurement in measurements:
            for key, value in measurement.items():
                if key not in metrics:
                    metrics[key] = []
                metrics[key].append(value)

        # Calculate statistical baselines
        for metric_name, values in metrics.items():
            if values:
                self.baselines[metric_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "p50": np.percentile(values, 50),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99),
                    "count": len(values),
                }

        self._established = True
        logger.info(f"Baseline established with {len(measurements)} measurements")

        return self.baselines

    def is_established(self) -> bool:
        """Check if baseline is established"""
        return self._established

    def get_threshold(self, metric_name: str) -> Optional[float]:
        """Get threshold for a metric based on baseline"""
        if not self._established or metric_name not in self.baselines:
            return None

        baseline = self.baselines[metric_name]

        # Use p99 as threshold, or mean + 3*std
        threshold = baseline["p99"]

        # Apply known constraints
        if metric_name == "instantiation_us":
            threshold = min(threshold, 3.0)  # Hard limit
        elif metric_name == "memory_kb":
            threshold = min(threshold, 6.5)  # Hard limit

        return threshold

    def check_anomaly(self, measurement: Dict) -> Dict:
        """Check if measurement is anomalous compared to baseline"""
        if not self._established:
            return {"is_anomaly": False, "reason": "Baseline not established", "violations": []}

        violations = []
        anomaly_scores = {}

        for metric_name, value in measurement.items():
            if metric_name in self.baselines:
                baseline = self.baselines[metric_name]

                # Calculate z-score
                if baseline["std"] > 0:
                    z_score = abs((value - baseline["mean"]) / baseline["std"])
                else:
                    # When std is 0, use percentage-based threshold
                    # Allow up to 5% deviation when std is 0
                    deviation_pct = (
                        abs((value - baseline["mean"]) / baseline["mean"])
                        if baseline["mean"] != 0
                        else 0
                    )
                    z_score = 0 if deviation_pct < 0.05 else float("inf")

                anomaly_scores[metric_name] = z_score

                # Check if anomalous
                if z_score > self.z_score_threshold:
                    violations.append(metric_name)
                    logger.warning(
                        f"Anomaly detected in {metric_name}: "
                        f"value={value}, mean={baseline['mean']:.2f}, "
                        f"z_score={z_score:.2f}"
                    )

        is_anomaly = len(violations) > 0

        return {
            "is_anomaly": is_anomaly,
            "violations": violations,
            "anomaly_scores": anomaly_scores,
            "measurement": measurement,
        }

    def update_baseline(self, new_measurements: List[Dict]):
        """Update baseline with new measurements"""
        if not new_measurements:
            return

        # Combine with existing measurements
        self.measurements.extend(new_measurements)

        # Keep only recent measurements (sliding window)
        max_measurements = 1000
        if len(self.measurements) > max_measurements:
            self.measurements = self.measurements[-max_measurements:]

        # Re-establish baseline
        self.establish(self.measurements)

    def get_baseline_summary(self) -> Dict:
        """Get summary of current baselines"""
        if not self._established:
            return {"established": False}

        return {
            "established": True,
            "metrics": list(self.baselines.keys()),
            "measurement_count": len(self.measurements),
            "baselines": self.baselines,
        }

    def export_for_monitoring(self) -> Dict:
        """Export baseline data for monitoring dashboard"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "established": self._established,
            "baselines": self.baselines if self._established else {},
            "thresholds": {metric: self.get_threshold(metric) for metric in self.baselines.keys()}
            if self._established
            else {},
        }

    def detect_trend(self, metric_name: str, window_size: int = 10) -> Optional[str]:
        """Detect trend in recent measurements"""
        if not self.measurements or len(self.measurements) < window_size:
            return None

        # Get recent values
        recent_values = []
        for measurement in self.measurements[-window_size:]:
            if metric_name in measurement:
                recent_values.append(measurement[metric_name])

        if len(recent_values) < window_size:
            return None

        # Calculate trend using linear regression
        x = np.arange(len(recent_values))
        coefficients = np.polyfit(x, recent_values, 1)
        slope = coefficients[0]

        # Determine trend
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    def get_health_score(self) -> float:
        """Calculate overall health score based on baselines"""
        if not self._established or not self.measurements:
            return 1.0  # Assume healthy if no data

        # Get recent measurements
        recent = self.measurements[-10:] if len(self.measurements) >= 10 else self.measurements

        total_score = 0
        metric_count = 0

        for measurement in recent:
            anomaly_result = self.check_anomaly(measurement)
            if not anomaly_result["is_anomaly"]:
                total_score += 1
            metric_count += 1

        return total_score / metric_count if metric_count > 0 else 1.0
