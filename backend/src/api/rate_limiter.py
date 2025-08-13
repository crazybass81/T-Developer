"""Rate Limiter - Day 9: Optimized"""

import threading
import time
from datetime import datetime
from typing import Dict, Optional


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_status(self) -> Dict:
        with self.lock:
            self._refill()
            return {
                "tokens_available": int(self.tokens),
                "capacity": self.capacity,
                "refill_rate": self.refill_rate,
                "percentage_full": (self.tokens / self.capacity) * 100,
            }


class RateLimiter:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.requests_per_minute = self.config.get("requests_per_minute", 60)
        self.burst_size = self.config.get(
            "burst_size", max(10, self.config.get("requests_per_minute", 60) // 2)
        )
        self.refill_rate = self.requests_per_minute / 60.0
        self.client_buckets = {}
        self.cleanup_interval = 300
        self.last_cleanup = time.time()

    def check_rate_limit(self, client_id: str) -> Dict:
        self._cleanup_old_buckets()

        if client_id not in self.client_buckets:
            self.client_buckets[client_id] = TokenBucket(
                capacity=self.burst_size, refill_rate=self.refill_rate
            )

        bucket = self.client_buckets[client_id]
        allowed = bucket.consume(1)

        result = {
            "allowed": allowed,
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if not allowed:
            status = bucket.get_status()
            retry_after = max(1, int((1 - status["tokens_available"]) / self.refill_rate))

            result.update(
                {
                    "rate_limit_exceeded": True,
                    "retry_after_seconds": retry_after,
                    "bucket_status": status,
                }
            )

        return result

    def get_client_status(self, client_id: str) -> Dict:
        if client_id not in self.client_buckets:
            return {
                "client_id": client_id,
                "tokens_available": self.burst_size,
                "capacity": self.burst_size,
                "percentage_full": 100.0,
            }

        bucket = self.client_buckets[client_id]
        status = bucket.get_status()
        status["client_id"] = client_id
        return status

    def reset_client_limit(self, client_id: str) -> bool:
        if client_id in self.client_buckets:
            del self.client_buckets[client_id]
            return True
        return False

    def _cleanup_old_buckets(self):
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = now - self.cleanup_interval
        to_remove = []

        for client_id, bucket in self.client_buckets.items():
            if bucket.last_refill < cutoff_time:
                to_remove.append(client_id)

        for client_id in to_remove:
            del self.client_buckets[client_id]

        self.last_cleanup = now

    def _refill_buckets(self):
        for bucket in self.client_buckets.values():
            bucket._refill()

    def get_global_stats(self) -> Dict:
        total_clients = len(self.client_buckets)
        active_clients = 0
        total_tokens = 0

        for bucket in self.client_buckets.values():
            status = bucket.get_status()
            total_tokens += status["tokens_available"]
            if status["tokens_available"] < status["capacity"]:
                active_clients += 1

        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "requests_per_minute_limit": self.requests_per_minute,
            "burst_size": self.burst_size,
            "average_tokens_available": total_tokens / max(total_clients, 1),
            "cleanup_interval_seconds": self.cleanup_interval,
        }

    def update_limits(
        self, requests_per_minute: Optional[int] = None, burst_size: Optional[int] = None
    ):
        if requests_per_minute:
            self.requests_per_minute = requests_per_minute
            self.refill_rate = requests_per_minute / 60.0

        if burst_size:
            self.burst_size = burst_size

        self.client_buckets.clear()


class AdaptiveRateLimiter(RateLimiter):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.base_requests_per_minute = self.requests_per_minute
        self.load_factor = 1.0
        self.load_history = []
        self.max_history = 60

    def update_system_load(self, cpu_percent: float, memory_percent: float):
        load_score = (cpu_percent + memory_percent) / 2
        self.load_history.append(load_score)

        if len(self.load_history) > self.max_history:
            self.load_history.pop(0)

        avg_load = sum(self.load_history) / len(self.load_history)

        if avg_load > 80:
            self.load_factor = 0.5
        elif avg_load > 60:
            self.load_factor = 0.75
        else:
            self.load_factor = 1.0

        new_limit = int(self.base_requests_per_minute * self.load_factor)
        self.update_limits(requests_per_minute=new_limit)

    def get_adaptive_stats(self) -> Dict:
        base_stats = self.get_global_stats()
        base_stats.update(
            {
                "base_requests_per_minute": self.base_requests_per_minute,
                "current_load_factor": self.load_factor,
                "average_system_load": sum(self.load_history) / len(self.load_history)
                if self.load_history
                else 0,
                "adaptive_enabled": True,
            }
        )
        return base_stats
