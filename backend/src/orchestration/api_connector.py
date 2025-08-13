"""API Connector for Agent Communication < 6.5KB"""
import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp


@dataclass
class APIRequest:
    agent_name: str
    endpoint: str
    method: str
    data: Dict[str, Any]
    headers: Optional[Dict] = None
    timeout: int = 30
    retries: int = 3


@dataclass
class APIResponse:
    status: int
    data: Optional[Dict] = None
    error: Optional[str] = None
    latency_ms: float = 0


class APIConnector:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:8000"
        self.session: Optional[aiohttp.ClientSession] = None
        self.circuit_breaker: Dict[str, Dict] = {}
        self.rate_limits: Dict[str, Dict] = {}
        self.metrics: Dict[str, List] = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call_agent(self, request: APIRequest) -> APIResponse:
        """Call agent endpoint with circuit breaker and rate limiting"""
        agent_key = f"{request.agent_name}:{request.endpoint}"

        # Check circuit breaker
        if self._is_circuit_open(agent_key):
            return APIResponse(status=503, error="Circuit breaker open", latency_ms=0)

        # Check rate limit
        if not self._check_rate_limit(agent_key):
            return APIResponse(status=429, error="Rate limit exceeded", latency_ms=0)

        # Execute request with retries
        for attempt in range(request.retries):
            try:
                response = await self._execute_request(request)
                self._record_success(agent_key)
                return response
            except Exception as e:
                self._record_failure(agent_key)
                if attempt == request.retries - 1:
                    return APIResponse(status=500, error=str(e), latency_ms=0)
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def _execute_request(self, request: APIRequest) -> APIResponse:
        """Execute single HTTP request"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}/agents/{request.agent_name}/{request.endpoint}"
        start_time = time.time()

        try:
            async with self.session.request(
                method=request.method,
                url=url,
                json=request.data,
                headers=request.headers or {},
                timeout=aiohttp.ClientTimeout(total=request.timeout),
            ) as response:
                latency = (time.time() - start_time) * 1000

                if response.status == 200:
                    data = await response.json()
                    return APIResponse(status=response.status, data=data, latency_ms=latency)
                else:
                    text = await response.text()
                    return APIResponse(status=response.status, error=text, latency_ms=latency)
        except asyncio.TimeoutError:
            raise Exception("Request timeout")
        except Exception as e:
            raise e

    def _is_circuit_open(self, agent_key: str) -> bool:
        """Check if circuit breaker is open"""
        if agent_key not in self.circuit_breaker:
            self.circuit_breaker[agent_key] = {"failures": 0, "last_failure": 0, "state": "closed"}

        cb = self.circuit_breaker[agent_key]

        # Reset if enough time has passed
        if cb["state"] == "open" and time.time() - cb["last_failure"] > 60:
            cb["state"] = "half_open"
            cb["failures"] = 0

        return cb["state"] == "open"

    def _check_rate_limit(self, agent_key: str) -> bool:
        """Check rate limit using token bucket"""
        if agent_key not in self.rate_limits:
            self.rate_limits[agent_key] = {
                "tokens": 100,
                "max_tokens": 100,
                "refill_rate": 10,  # tokens per second
                "last_refill": time.time(),
            }

        rl = self.rate_limits[agent_key]

        # Refill tokens
        now = time.time()
        elapsed = now - rl["last_refill"]
        tokens_to_add = elapsed * rl["refill_rate"]
        rl["tokens"] = min(rl["max_tokens"], rl["tokens"] + tokens_to_add)
        rl["last_refill"] = now

        # Check if request allowed
        if rl["tokens"] >= 1:
            rl["tokens"] -= 1
            return True
        return False

    def _record_success(self, agent_key: str):
        """Record successful call"""
        if agent_key in self.circuit_breaker:
            cb = self.circuit_breaker[agent_key]
            cb["failures"] = 0
            if cb["state"] == "half_open":
                cb["state"] = "closed"

        # Record metric
        if agent_key not in self.metrics:
            self.metrics[agent_key] = []
        self.metrics[agent_key].append({"timestamp": time.time(), "success": True})

    def _record_failure(self, agent_key: str):
        """Record failed call"""
        if agent_key not in self.circuit_breaker:
            self.circuit_breaker[agent_key] = {"failures": 0, "last_failure": 0, "state": "closed"}

        cb = self.circuit_breaker[agent_key]
        cb["failures"] += 1
        cb["last_failure"] = time.time()

        # Open circuit if too many failures
        if cb["failures"] >= 5:
            cb["state"] = "open"

        # Record metric
        if agent_key not in self.metrics:
            self.metrics[agent_key] = []
        self.metrics[agent_key].append({"timestamp": time.time(), "success": False})

    async def batch_call(self, requests: List[APIRequest]) -> List[APIResponse]:
        """Execute multiple requests in parallel"""
        tasks = [self.call_agent(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_metrics(self, agent_key: Optional[str] = None) -> Dict[str, Any]:
        """Get connector metrics"""
        if agent_key:
            if agent_key not in self.metrics:
                return {}

            metrics = self.metrics[agent_key]
            total = len(metrics)
            success = sum(1 for m in metrics if m["success"])

            return {
                "agent_key": agent_key,
                "total_calls": total,
                "success_rate": (success / total * 100) if total > 0 else 0,
                "circuit_state": self.circuit_breaker.get(agent_key, {}).get("state", "closed"),
                "rate_limit_tokens": self.rate_limits.get(agent_key, {}).get("tokens", 100),
            }
        else:
            # Return all metrics
            all_metrics = {}
            for key in self.metrics:
                all_metrics[key] = self.get_metrics(key)
            return all_metrics

    async def health_check(self, agent_name: str) -> bool:
        """Check agent health"""
        request = APIRequest(
            agent_name=agent_name, endpoint="health", method="GET", data={}, timeout=5, retries=1
        )
        response = await self.call_agent(request)
        return response.status == 200


# Example usage
if __name__ == "__main__":

    async def test_connector():
        async with APIConnector() as connector:
            # Single agent call
            request = APIRequest(
                agent_name="nl_input",
                endpoint="process",
                method="POST",
                data={"text": "Test input"},
            )
            response = await connector.call_agent(request)
            print(f"Response: {response}")

            # Batch calls
            requests = [
                APIRequest("parser", "parse", "POST", {"data": "test1"}),
                APIRequest("generator", "generate", "POST", {"template": "test2"}),
            ]
            responses = await connector.batch_call(requests)
            print(f"Batch responses: {responses}")

            # Get metrics
            metrics = connector.get_metrics()
            print(f"Metrics: {json.dumps(metrics, indent=2)}")

    asyncio.run(test_connector())
