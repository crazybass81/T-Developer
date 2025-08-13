"""API Monitoring - Day 9: Optimized"""

import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional


class APIMonitor:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.max_history_size = self.config.get("max_history_size", 1000)
        self.metrics_window_minutes = self.config.get("metrics_window_minutes", 5)
        self.request_history = deque(maxlen=self.max_history_size)
        self.error_history = deque(maxlen=self.max_history_size)
        self.total_requests = 0
        self.total_errors = 0
        self.agent_requests = defaultdict(int)
        self.endpoint_requests = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.response_times = deque(maxlen=self.max_history_size)
        self.lock = threading.Lock()
        self.start_time = time.time()

    def record_request(self, request_data: Dict):
        with self.lock:
            timestamp = time.time()
            request_record = {
                **request_data,
                "timestamp": timestamp,
                "datetime": datetime.utcnow().isoformat(),
            }
            self.request_history.append(request_record)
            self.total_requests += 1
            self.agent_requests[request_data.get("agent_id", "unknown")] += 1
            self.endpoint_requests[request_data.get("path", "unknown")] += 1
            self.status_codes[request_data.get("status_code", 0)] += 1
            rt = request_data.get("response_time_ms", 0)
            if rt > 0:
                self.response_times.append(rt)

    def record_error(self, error_data: Dict):
        with self.lock:
            error_record = {
                **error_data,
                "timestamp": time.time(),
                "datetime": datetime.utcnow().isoformat(),
            }
            self.error_history.append(error_record)
            self.total_errors += 1

    def get_metrics(self) -> Dict:
        with self.lock:
            ct = time.time()
            uptime = ct - self.start_time
            ws = ct - (self.metrics_window_minutes * 60)
            recent_req = [r for r in self.request_history if r["timestamp"] > ws]
            recent_err = [e for e in self.error_history if e["timestamp"] > ws]
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": int(uptime),
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "success_rate": (self.total_requests - self.total_errors) / self.total_requests
                if self.total_requests
                else 1.0,
                "recent_requests": len(recent_req),
                "recent_errors": len(recent_err),
                "requests_per_minute": len(recent_req) / max(self.metrics_window_minutes, 1),
                "agent_requests": dict(self.agent_requests),
                "top_endpoints": self._get_top_endpoints(),
                "status_codes": dict(self.status_codes),
                "response_times": self._calc_response_stats(),
            }

    def get_error_metrics(self) -> Dict:
        with self.lock:
            et = defaultdict(int)
            for error in self.error_history:
                et[error.get("error_type", "unknown")] += 1
            return {"total_errors": self.total_errors, "error_types": dict(et)}

    def get_health_status(self) -> Dict:
        with self.lock:
            ct = time.time()
            ws = ct - (self.metrics_window_minutes * 60)
            rr = [r for r in self.request_history if r["timestamp"] > ws]
            re = [e for e in self.error_history if e["timestamp"] > ws]
            er = len(re) / max(len(rr), 1)
            art = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            healthy = er <= 0.1 and art <= 5000
            return {
                "status": "healthy" if healthy else "degraded",
                "healthy": healthy,
                "error_rate": er,
                "average_response_time_ms": art,
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _calc_response_stats(self) -> Dict:
        if not self.response_times:
            return {"count": 0, "average_ms": 0}
        times = list(self.response_times)
        return {"count": len(times), "average_ms": sum(times) / len(times)}

    def _get_top_endpoints(self, limit: int = 5) -> List[Dict]:
        sorted_endpoints = sorted(self.endpoint_requests.items(), key=lambda x: x[1], reverse=True)
        return [{"endpoint": ep, "requests": c} for ep, c in sorted_endpoints[:limit]]

    def reset_metrics(self):
        with self.lock:
            self.request_history.clear()
            self.error_history.clear()
            self.total_requests = 0
            self.total_errors = 0
            self.agent_requests.clear()
            self.endpoint_requests.clear()
            self.status_codes.clear()
            self.response_times.clear()
            self.start_time = time.time()


class AlertManager:
    def __init__(self, config: Optional[Dict] = None):
        self.thresholds = {"error_rate": 0.1, "response_time_ms": 5000}
        self.alerts = []

    def check_alerts(self, metrics: Dict) -> List[Dict]:
        alerts = []
        er = metrics.get("total_errors", 0) / max(metrics.get("total_requests", 1), 1)
        if er > self.thresholds["error_rate"]:
            alerts.append(
                {
                    "type": "error_rate",
                    "level": "warning" if er < 0.2 else "critical",
                    "message": f"High error rate: {er:.2%}",
                }
            )
        art = metrics.get("response_times", {}).get("average_ms", 0)
        if art > self.thresholds["response_time_ms"]:
            alerts.append(
                {
                    "type": "response_time",
                    "level": "warning",
                    "message": f"High response time: {art:.0f}ms",
                }
            )
        self.alerts = alerts
        return alerts

    def get_active_alerts(self) -> List[Dict]:
        return self.alerts
