"""
Advanced Rate Limiter
Redis 기반 분산 Rate Limiting
"""

import time
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis
from fastapi import Request, HTTPException, status
from functools import wraps
import asyncio


class RateLimiter:
    """분산 환경 지원 Rate Limiter"""

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        default_limit: int = 100,
        default_window: int = 60,
    ):
        self.redis_client = redis_client or redis.Redis(
            host="localhost", port=6379, db=1, decode_responses=True
        )
        self.default_limit = default_limit
        self.default_window = default_window

        # Different limits for different tiers
        self.tier_limits = {
            "free": {"requests": 100, "window": 3600},  # 100 requests per hour
            "basic": {"requests": 1000, "window": 3600},  # 1000 requests per hour
            "premium": {"requests": 10000, "window": 3600},  # 10000 requests per hour
            "enterprise": {
                "requests": 100000,
                "window": 3600,
            },  # 100000 requests per hour
            "unlimited": {"requests": float("inf"), "window": 1},  # No limit
        }

        # Endpoint-specific limits
        self.endpoint_limits = {
            "/api/v1/generate": {"requests": 10, "window": 60},  # Heavy endpoint
            "/api/v1/auth/login": {"requests": 5, "window": 60},  # Prevent brute force
            "/api/v1/auth/register": {"requests": 3, "window": 60},  # Prevent spam
        }

    def get_client_id(self, request: Request, user_id: Optional[str] = None) -> str:
        """클라이언트 식별자 생성"""
        if user_id:
            return f"user:{user_id}"

        # Use IP + User-Agent for anonymous users
        client_ip = request.client.host
        user_agent = request.headers.get("User-Agent", "")

        # Create hash for privacy
        identifier = f"{client_ip}:{user_agent}"
        return hashlib.md5(identifier.encode()).hexdigest()

    async def check_rate_limit(
        self,
        request: Request,
        user_id: Optional[str] = None,
        tier: str = "free",
        custom_limit: Optional[int] = None,
        custom_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Rate limit 확인"""

        client_id = self.get_client_id(request, user_id)
        endpoint = request.url.path

        # Determine limits
        if custom_limit and custom_window:
            limit = custom_limit
            window = custom_window
        elif endpoint in self.endpoint_limits:
            limit = self.endpoint_limits[endpoint]["requests"]
            window = self.endpoint_limits[endpoint]["window"]
        elif tier in self.tier_limits:
            limit = self.tier_limits[tier]["requests"]
            window = self.tier_limits[tier]["window"]
        else:
            limit = self.default_limit
            window = self.default_window

        # Unlimited tier
        if limit == float("inf"):
            return {"allowed": True, "limit": limit, "remaining": limit, "reset": 0}

        # Use sliding window algorithm
        now = time.time()
        key = f"rate_limit:{client_id}:{endpoint}"

        try:
            # Atomic operation using Lua script
            lua_script = """
            local key = KEYS[1]
            local now = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])

            -- Remove old entries
            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

            -- Count current requests
            local current = redis.call('ZCARD', key)

            if current < limit then
                -- Add new request
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, window)
                return {1, limit - current - 1}
            else
                return {0, 0}
            end
            """

            result = self.redis_client.eval(lua_script, 1, key, now, window, limit)

            allowed = result[0] == 1
            remaining = result[1]

            # Calculate reset time
            if not allowed:
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_time = oldest[0][1] + window
                else:
                    reset_time = now + window
            else:
                reset_time = now + window

            return {
                "allowed": allowed,
                "limit": limit,
                "remaining": remaining,
                "reset": int(reset_time),
            }

        except Exception as e:
            # Fallback to in-memory if Redis fails
            return self._fallback_rate_limit(client_id, endpoint, limit, window)

    def _fallback_rate_limit(
        self, client_id: str, endpoint: str, limit: int, window: int
    ) -> Dict[str, Any]:
        """Redis 실패시 메모리 기반 fallback"""
        # Simple in-memory rate limiting
        if not hasattr(self, "_memory_limits"):
            self._memory_limits = {}

        key = f"{client_id}:{endpoint}"
        now = time.time()

        if key not in self._memory_limits:
            self._memory_limits[key] = []

        # Remove old entries
        self._memory_limits[key] = [
            t for t in self._memory_limits[key] if t > now - window
        ]

        if len(self._memory_limits[key]) < limit:
            self._memory_limits[key].append(now)
            return {
                "allowed": True,
                "limit": limit,
                "remaining": limit - len(self._memory_limits[key]),
                "reset": int(now + window),
            }

        return {
            "allowed": False,
            "limit": limit,
            "remaining": 0,
            "reset": int(self._memory_limits[key][0] + window),
        }

    def rate_limit_decorator(
        self, requests: int = 100, window: int = 60, tier_based: bool = False
    ):
        """Rate limiting 데코레이터"""

        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                # Extract user info if available
                user = kwargs.get("current_user")
                user_id = user.id if user else None
                tier = user.subscription_tier if user and tier_based else "free"

                # Check rate limit
                result = await self.check_rate_limit(
                    request,
                    user_id,
                    tier,
                    None if tier_based else requests,
                    None if tier_based else window,
                )

                if not result["allowed"]:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded",
                        headers={
                            "X-RateLimit-Limit": str(result["limit"]),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(result["reset"]),
                            "Retry-After": str(result["reset"] - int(time.time())),
                        },
                    )

                # Add rate limit headers to response
                response = await func(request, *args, **kwargs)
                response.headers["X-RateLimit-Limit"] = str(result["limit"])
                response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
                response.headers["X-RateLimit-Reset"] = str(result["reset"])

                return response

            return wrapper

        return decorator


class IPBlocker:
    """IP 차단 시스템"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(
            host="localhost", port=6379, db=2, decode_responses=True
        )

        # Auto-block thresholds
        self.thresholds = {
            "401": {
                "count": 10,
                "window": 300,
                "block_duration": 3600,
            },  # 10 unauthorized in 5 min = 1 hour block
            "403": {
                "count": 10,
                "window": 300,
                "block_duration": 3600,
            },  # 10 forbidden in 5 min = 1 hour block
            "429": {
                "count": 5,
                "window": 60,
                "block_duration": 1800,
            },  # 5 rate limits in 1 min = 30 min block
        }

    async def check_ip_blocked(self, ip: str) -> bool:
        """IP 차단 여부 확인"""
        try:
            return self.redis_client.exists(f"blocked_ip:{ip}") > 0
        except:
            return False

    async def block_ip(self, ip: str, reason: str, duration: int = 3600):
        """IP 차단"""
        try:
            self.redis_client.setex(
                f"blocked_ip:{ip}",
                duration,
                json.dumps(
                    {
                        "reason": reason,
                        "blocked_at": datetime.now().isoformat(),
                        "duration": duration,
                    }
                ),
            )
        except:
            pass

    async def track_suspicious_activity(self, ip: str, status_code: int):
        """의심스러운 활동 추적"""
        status_str = str(status_code)

        if status_str not in self.thresholds:
            return

        threshold = self.thresholds[status_str]
        key = f"suspicious:{ip}:{status_str}"

        try:
            # Increment counter
            count = self.redis_client.incr(key)

            # Set expiry on first increment
            if count == 1:
                self.redis_client.expire(key, threshold["window"])

            # Check if threshold exceeded
            if count >= threshold["count"]:
                await self.block_ip(
                    ip, f"Too many {status_str} responses", threshold["block_duration"]
                )
                # Reset counter
                self.redis_client.delete(key)
        except:
            pass


# Global instances
rate_limiter = RateLimiter()
ip_blocker = IPBlocker()
