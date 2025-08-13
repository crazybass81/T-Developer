"""
Authentication Middleware
FastAPI 인증 미들웨어 및 의존성
"""

import time
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_handler import jwt_handler
from .models import User

# Bearer token scheme
bearer_scheme = HTTPBearer()


class JWTAuthMiddleware:
    """JWT 인증 미들웨어"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        """모든 요청에 대한 인증 처리"""

        # Skip auth for public endpoints
        public_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
        ]

        if any(request.url.path.startswith(path) for path in public_paths):
            response = await call_next(request)
            return response

        # Extract token from header
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            # 인증 필요한 엔드포인트인지 확인
            if request.url.path.startswith("/api/"):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing authentication token"},
                )

        # Process request
        start_time = time.time()
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Add request ID for tracing
        request_id = request.headers.get("X-Request-ID", str(time.time()))
        response.headers["X-Request-ID"] = request_id

        # Add response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    """현재 인증된 사용자 가져오기"""

    token = credentials.credentials

    try:
        payload = jwt_handler.verify_token(token, token_type="access")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create user object from token payload
        user = User(
            id=payload["sub"],
            email=payload["email"],
            roles=payload.get("roles", ["user"]),
            permissions=payload.get("permissions", []),
            is_active=True,
        )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """활성 사용자만 허용"""

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """관리자만 허용"""

    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return current_user


class RateLimitMiddleware:
    """Rate Limiting 미들웨어"""

    def __init__(self, app, requests_per_minute: int = 60):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}

    async def __call__(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        current_minute = int(time.time() // 60)

        # Initialize or update request count
        key = f"{client_ip}:{current_minute}"

        if key not in self.request_counts:
            self.request_counts[key] = 0

        self.request_counts[key] += 1

        # Check rate limit
        if self.request_counts[key] > self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": "60"},
            )

        # Clean old entries
        current_time = int(time.time() // 60)
        keys_to_delete = [
            k for k in self.request_counts.keys() if int(k.split(":")[1]) < current_time - 1
        ]
        for key in keys_to_delete:
            del self.request_counts[key]

        response = await call_next(request)
        return response


from starlette.responses import JSONResponse
