"""API Authentication - Day 9: Optimized"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt


class JWTAuthentication:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.default_expiry_hours = 24

    def create_token(self, payload: Dict, expires_in_hours: Optional[int] = None) -> str:
        expires_in = expires_in_hours or self.default_expiry_hours
        expiry = datetime.utcnow() + timedelta(hours=expires_in)

        token_payload = {
            **payload,
            "exp": expiry,
            "iat": datetime.utcnow(),
            "iss": "t-developer-api-gateway",
        }

        return jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    def is_token_valid(self, token: str) -> bool:
        try:
            self.verify_token(token)
            return True
        except ValueError:
            return False

    def refresh_token(self, token: str) -> str:
        try:
            payload = self.verify_token(token)
            payload.pop("exp", None)
            payload.pop("iat", None)
            return self.create_token(payload)
        except ValueError:
            raise ValueError("Cannot refresh invalid token")


class APIKeyAuthentication:
    def __init__(self):
        self.api_keys = {}
        self.key_length = 32

    def generate_api_key(
        self, client_identifier: str, permissions: Optional[List[str]] = None
    ) -> str:
        api_key = secrets.token_urlsafe(self.key_length)

        self.api_keys[api_key] = {
            "client_id": client_identifier,
            "permissions": permissions or [],
            "created_at": datetime.utcnow(),
            "last_used": None,
            "usage_count": 0,
            "active": True,
        }

        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        if api_key not in self.api_keys:
            return False

        key_info = self.api_keys[api_key]
        if not key_info.get("active", False):
            return False

        key_info["last_used"] = datetime.utcnow()
        key_info["usage_count"] += 1

        return True

    def get_api_key_info(self, api_key: str) -> Optional[Dict]:
        if api_key in self.api_keys and self.api_keys[api_key].get("active"):
            return self.api_keys[api_key].copy()
        return None

    def revoke_api_key(self, api_key: str) -> bool:
        if api_key in self.api_keys:
            self.api_keys[api_key]["active"] = False
            return True
        return False

    def list_client_keys(self, client_identifier: str) -> List[Dict]:
        client_keys = []
        for key, info in self.api_keys.items():
            if info["client_id"] == client_identifier and info.get("active"):
                safe_info = info.copy()
                safe_info["api_key"] = key[:8] + "..."
                client_keys.append(safe_info)
        return client_keys

    def check_permission(self, api_key: str, required_permission: str) -> bool:
        if not self.validate_api_key(api_key):
            return False

        permissions = self.api_keys[api_key].get("permissions", [])
        if not permissions:
            return True

        return required_permission in permissions or "admin" in permissions


class AuthenticationMiddleware:
    def __init__(self, jwt_auth: JWTAuthentication, api_key_auth: APIKeyAuthentication):
        self.jwt_auth = jwt_auth
        self.api_key_auth = api_key_auth

    def authenticate_request(self, headers: Dict) -> Dict:
        authorization = headers.get("authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            try:
                payload = self.jwt_auth.verify_token(token)
                return {
                    "authenticated": True,
                    "method": "jwt",
                    "user_info": payload,
                    "permissions": payload.get("permissions", []),
                }
            except ValueError:
                pass

        api_key = headers.get("x-api-key") or headers.get("api-key")
        if api_key and self.api_key_auth.validate_api_key(api_key):
            key_info = self.api_key_auth.get_api_key_info(api_key)
            return {
                "authenticated": True,
                "method": "api_key",
                "client_id": key_info["client_id"],
                "permissions": key_info["permissions"],
            }

        return {"authenticated": False, "reason": "no_valid_credentials"}

    def require_authentication(self, headers: Dict) -> None:
        auth_result = self.authenticate_request(headers)
        if not auth_result["authenticated"]:
            raise ValueError("Authentication required")
        return auth_result

    def require_permission(self, headers: Dict, permission: str) -> None:
        auth_result = self.require_authentication(headers)

        if auth_result["method"] == "api_key":
            api_key = headers.get("x-api-key") or headers.get("api-key")
            if not self.api_key_auth.check_permission(api_key, permission):
                raise ValueError(f"Permission '{permission}' required")
        elif auth_result["method"] == "jwt":
            user_permissions = auth_result.get("permissions", [])
            if permission not in user_permissions and "admin" not in user_permissions:
                raise ValueError(f"Permission '{permission}' required")
