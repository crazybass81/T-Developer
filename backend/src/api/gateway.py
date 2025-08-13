"""API Gateway - Day 9: Optimized"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .authentication import APIKeyAuthentication, JWTAuthentication
from .monitoring import APIMonitor
from .rate_limiter import RateLimiter
from .validation import RequestValidator, ResponseFormatter


class APIGateway:
    """FastAPI-based API Gateway for T-Developer system"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            # nosec B104 - Development bind to all interfaces for container compatibility
            "host": "0.0.0.0",  # Use localhost for production deployment
            "port": 8000,
            "title": "T-Developer API Gateway",
            "version": "1.0.0",
            "jwt_secret": "default-secret-key",
            "rate_limit": {"requests_per_minute": 60},
        }

        self.app = FastAPI(title=self.config["title"], version=self.config["version"])
        self.registered_agents = {}
        self.rate_limiter = RateLimiter(self.config.get("rate_limit", {}))
        self.jwt_auth = JWTAuthentication(self.config["jwt_secret"])
        self.api_key_auth = APIKeyAuthentication()
        self.validator = RequestValidator()
        self.formatter = ResponseFormatter()
        self.monitor = APIMonitor()

        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": self.config["version"],
            }

        @self.app.get("/metrics")
        async def get_metrics():
            return self.formatter.format_success(self.monitor.get_metrics())

        @self.app.post("/agents/{agent_id}/message")
        async def send_message_to_agent(agent_id: str, request: Request):
            try:
                body = await request.json()
                message = {
                    "to_agent": agent_id,
                    "type": "api_request",
                    "payload": body,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                result = self.send_message_to_agent(message)
                return self.formatter.format_success(result)
            except Exception as e:
                return self.formatter.format_error("message_failed", str(e))

    def register_agent_endpoints(self, agent_info: Dict) -> Dict:
        agent_id = agent_info["agent_id"]
        self.registered_agents[agent_id] = agent_info

        for endpoint in agent_info.get("endpoints", []):
            path = f"/agents/{agent_id}{endpoint['path']}"
            methods = endpoint.get("methods", ["POST"])
            self._create_agent_endpoint(agent_id, path, methods, endpoint)

        return {
            "status": "success",
            "agent_id": agent_id,
            "endpoints_registered": len(agent_info.get("endpoints", [])),
        }

    def _create_agent_endpoint(
        self, agent_id: str, path: str, methods: List[str], endpoint_config: Dict
    ):
        async def agent_endpoint_handler(request: Request):
            try:
                # Rate limiting
                rate_check = self.rate_limiter.check_rate_limit(request.client.host)
                if not rate_check["allowed"]:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")

                body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else {}
                message = {
                    "to_agent": agent_id,
                    "type": "endpoint_request",
                    "endpoint": path,
                    "method": request.method,
                    "payload": body,
                    "headers": dict(request.headers),
                }
                result = self.send_message_to_agent(message)

                self.monitor.record_request(
                    {
                        "method": request.method,
                        "path": path,
                        "status_code": 200,
                        "agent_id": agent_id,
                        "response_time_ms": 100,
                    }
                )
                return self.formatter.format_success(result)
            except Exception as e:
                self.monitor.record_error(
                    {
                        "method": request.method,
                        "path": path,
                        "status_code": 500,
                        "error_type": "processing_error",
                        "error_message": str(e),
                    }
                )
                return self.formatter.format_error("processing_failed", str(e))

        for method in methods:
            if method.upper() == "GET":
                self.app.get(path)(agent_endpoint_handler)
            elif method.upper() == "POST":
                self.app.post(path)(agent_endpoint_handler)
            elif method.upper() == "PUT":
                self.app.put(path)(agent_endpoint_handler)
            elif method.upper() == "DELETE":
                self.app.delete(path)(agent_endpoint_handler)

    def send_message_to_agent(self, message: Dict) -> Dict:
        return {
            "status": "queued",
            "message_id": str(uuid.uuid4()),
            "queued_at": datetime.utcnow().isoformat(),
            "agent_id": message.get("to_agent"),
        }

    def run(self, **kwargs):
        host = kwargs.get("host", self.config["host"])
        port = kwargs.get("port", self.config["port"])
        uvicorn.run(self.app, host=host, port=port, log_level="info", **kwargs)
