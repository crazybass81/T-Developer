"""
CORS Configuration
Cross-Origin Resource Sharing 설정
"""

import os
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware


class CORSConfig:
    """CORS 설정 관리"""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")

        # Environment-specific origins
        self.allowed_origins = self._get_allowed_origins()
        self.allow_credentials = True
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allowed_headers = [
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-API-Key",
            "X-Client-Version",
            "X-Tenant-ID",
        ]
        self.expose_headers = [
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Process-Time",
            "Content-Disposition",
        ]
        self.max_age = 86400  # 24 hours

    def _get_allowed_origins(self) -> List[str]:
        """환경별 허용 Origin 설정"""

        if self.environment == "production":
            # Production origins only
            return [
                "https://t-developer.com",
                "https://www.t-developer.com",
                "https://app.t-developer.com",
                "https://api.t-developer.com",
            ]

        elif self.environment == "staging":
            # Staging origins
            return [
                "https://staging.t-developer.com",
                "https://staging-app.t-developer.com",
                "http://localhost:3000",
                "http://localhost:5173",
            ]

        else:  # development
            # Allow all common development origins
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                # Docker networks
                "http://frontend:3000",
                "http://backend:8000",
                # Allow all in dev (careful!)
                "*",
            ]

    def add_origin(self, origin: str):
        """동적으로 Origin 추가"""
        if origin not in self.allowed_origins:
            self.allowed_origins.append(origin)

    def remove_origin(self, origin: str):
        """Origin 제거"""
        if origin in self.allowed_origins:
            self.allowed_origins.remove(origin)

    def get_middleware(self) -> CORSMiddleware:
        """FastAPI CORS Middleware 생성"""
        return CORSMiddleware(
            app=None,  # Will be set by FastAPI
            allow_origins=self.allowed_origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allowed_methods,
            allow_headers=self.allowed_headers,
            expose_headers=self.expose_headers,
            max_age=self.max_age,
        )

    def validate_origin(self, origin: Optional[str]) -> bool:
        """Origin 검증"""
        if not origin:
            return False

        # Allow all in development
        if self.environment == "development" and "*" in self.allowed_origins:
            return True

        # Check exact match
        if origin in self.allowed_origins:
            return True

        # Check wildcard patterns
        for allowed in self.allowed_origins:
            if "*" in allowed:
                # Simple wildcard matching
                pattern = allowed.replace("*", ".*")
                import re

                if re.match(pattern, origin):
                    return True

        return False


# Global instance
cors_config = CORSConfig()


def setup_cors(app):
    """FastAPI 앱에 CORS 설정 적용"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allowed_origins,
        allow_credentials=cors_config.allow_credentials,
        allow_methods=cors_config.allowed_methods,
        allow_headers=cors_config.allowed_headers,
        expose_headers=cors_config.expose_headers,
        max_age=cors_config.max_age,
    )
