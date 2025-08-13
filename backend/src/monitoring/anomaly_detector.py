"""🧬 T-Developer Anomaly Detector <6.5KB"""
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Anomaly:
    type: str
    severity: int  # 1-4
    metric: str
    value: float
    expected: Tuple[float, float]
    confidence: float
    timestamp: float
    agent_id: str = None
    desc: str = ""


class AnomalyDetector:
    def __init__(self, window_size: int = 30):
        self.windows = defaultdict(lambda: deque(maxlen=window_size))
        self.anomalies = deque(maxlen=50)
        self.stats = {"checks": 0, "found": 0}

    def add_metric(self, name: str, value: float, ts: float = None, agent: str = None):
        ts = ts or time.time()
        window = self.windows[name]
        window.append((value, ts, agent))

        anomalies = self._detect(name, value, ts, agent, window)
        self.anomalies.extend(anomalies)

        self.stats["checks"] += 1
        self.stats["found"] += len(anomalies)
        return anomalies

    def get_anomalies(self, n: int = 10) -> List[Anomaly]:
        return list(self.anomalies)[-n:]

    def get_summary(self) -> Dict[str, Any]:
        anomalies = list(self.anomalies)
        if not anomalies:
            return {"total": 0, "by_type": {}, "trend": "stable"}

        by_type = defaultdict(int)
        for a in anomalies:
            by_type[a.type] += 1

        current = time.time()
        recent = [a for a in anomalies if current - a.timestamp < 3600]

        return {
            "total": len(anomalies),
            "recent": len(recent),
            "by_type": dict(by_type),
            "stats": self.stats,
        }

    def _detect(
        self, name: str, value: float, ts: float, agent: str, window: deque
    ) -> List[Anomaly]:
        if len(window) < 5:
            return []

        anomalies = []
        values = [v[0] for v in window]
        mean = statistics.mean(values)

        if len(values) > 1:
            std = statistics.stdev(values)
            if std > 0:
                z_score = abs(value - mean) / std
                if z_score > 3.0:
                    severity = 4 if z_score > 4.0 else 3
                    anomalies.append(
                        Anomaly(
                            type="outlier",
                            severity=severity,
                            metric=name,
                            value=value,
                            expected=(mean - 2 * std, mean + 2 * std),
                            confidence=min(0.99, z_score / 5.0),
                            timestamp=ts,
                            agent_id=agent,
                            desc=f"Z-score: {z_score:.2f}",
                        )
                    )

        # Performance check
        if "time" in name and value > 1000 and value > mean * 2.5:
            anomalies.append(
                Anomaly(
                    type="performance",
                    severity=4 if value > 5000 else 3,
                    metric=name,
                    value=value,
                    expected=(0, mean * 2.0),
                    confidence=0.85,
                    timestamp=ts,
                    agent_id=agent,
                    desc=f"Slow: {value:.0f}ms",
                )
            )

        # Memory check
        if "memory" in name and value > 6656:
            anomalies.append(
                Anomaly(
                    type="memory",
                    severity=4,
                    metric=name,
                    value=value,
                    expected=(0, 6656),
                    confidence=1.0,
                    timestamp=ts,
                    agent_id=agent,
                    desc=f"Over 6.5KB limit",
                )
            )

        return anomalies


# Global instance
_detector = None


def get_detector() -> AnomalyDetector:
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector


def detect_anomaly(name: str, value: float, agent: str = None) -> List[Anomaly]:
    return get_detector().add_metric(name, value, agent=agent)


def get_anomalies(n: int = 10) -> List[Anomaly]:
    return get_detector().get_anomalies(n)


def get_report() -> Dict[str, Any]:
    return get_detector().get_summary()
