"""
JWT Token Handler
엔터프라이즈급 JWT 토큰 관리
"""

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
import redis
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class JWTHandler:
    """JWT 토큰 생성 및 검증"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", self._generate_secret())
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        self.issuer = os.getenv("JWT_ISSUER", "T-Developer")

        # Redis for token blacklist
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            decode_responses=True,
        )

        # RSA keys for RS256 (production)
        if self.algorithm == "RS256":
            self.private_key, self.public_key = self._generate_rsa_keys()

    def _generate_secret(self) -> str:
        """시크릿 키 생성"""
        return hashlib.sha256(os.urandom(32)).hexdigest()

    def _generate_rsa_keys(self):
        """RSA 키 페어 생성 (프로덕션용)"""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: list = None,
        permissions: list = None,
        custom_claims: Dict[str, Any] = None,
    ) -> str:
        """Access Token 생성"""

        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire)

        payload = {
            "sub": user_id,  # Subject (user ID)
            "email": email,
            "roles": roles or ["user"],
            "permissions": permissions or [],
            "iat": now,  # Issued at
            "exp": expire,  # Expiration
            "nbf": now,  # Not before
            "iss": self.issuer,  # Issuer
            "jti": self._generate_jti(),  # JWT ID
            "type": "access",
        }

        # Add custom claims
        if custom_claims:
            payload.update(custom_claims)

        # Choose signing key based on algorithm
        if self.algorithm == "RS256":
            key = self.private_key
        else:
            key = self.secret_key

        token = jwt.encode(payload, key, algorithm=self.algorithm)

        # Store token metadata in Redis for tracking
        self._store_token_metadata(payload["jti"], user_id, "access", expire)

        return token

    def create_refresh_token(self, user_id: str, email: str) -> str:
        """Refresh Token 생성"""

        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire)

        payload = {
            "sub": user_id,
            "email": email,
            "iat": now,
            "exp": expire,
            "iss": self.issuer,
            "jti": self._generate_jti(),
            "type": "refresh",
        }

        if self.algorithm == "RS256":
            key = self.private_key
        else:
            key = self.secret_key

        token = jwt.encode(payload, key, algorithm=self.algorithm)

        # Store in Redis
        self._store_token_metadata(payload["jti"], user_id, "refresh", expire)

        return token

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            # Choose verification key
            if self.algorithm == "RS256":
                key = self.public_key
            else:
                key = self.secret_key

            # Decode and verify
            payload = jwt.decode(
                token,
                key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                options={"verify_exp": True, "verify_nbf": True},
            )

            # Check token type
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")

            # Check if token is blacklisted
            if self._is_token_blacklisted(payload["jti"]):
                raise jwt.InvalidTokenError("Token has been revoked")

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")

    def revoke_token(self, token: str) -> bool:
        """토큰 무효화 (블랙리스트 추가)"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})

            jti = payload.get("jti")
            if jti:
                # Add to blacklist
                expire_at = datetime.fromtimestamp(payload["exp"])
                ttl = (expire_at - datetime.now()).total_seconds()

                if ttl > 0:
                    self.redis_client.setex(
                        f"blacklist:{jti}",
                        int(ttl),
                        json.dumps({"revoked_at": datetime.now().isoformat()}),
                    )
                return True

        except Exception:
            pass

        return False

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh Token으로 새 Access Token 발급"""
        try:
            payload = self.verify_token(refresh_token, token_type="refresh")

            if payload:
                # Create new access token
                return self.create_access_token(user_id=payload["sub"], email=payload["email"])

        except Exception:
            pass

        return None

    def _generate_jti(self) -> str:
        """JWT ID 생성"""
        return hashlib.sha256(os.urandom(32)).hexdigest()

    def _store_token_metadata(self, jti: str, user_id: str, token_type: str, expire: datetime):
        """토큰 메타데이터 저장"""
        try:
            ttl = int((expire - datetime.now(timezone.utc)).total_seconds())
            if ttl > 0:
                self.redis_client.setex(
                    f"token:{jti}",
                    ttl,
                    json.dumps(
                        {
                            "user_id": user_id,
                            "type": token_type,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                    ),
                )
        except Exception:
            pass  # Redis 연결 실패시 무시

    def _is_token_blacklisted(self, jti: str) -> bool:
        """토큰 블랙리스트 확인"""
        try:
            return self.redis_client.exists(f"blacklist:{jti}") > 0
        except Exception:
            return False  # Redis 연결 실패시 허용


# Singleton instance
jwt_handler = JWTHandler()


# Helper functions
def create_access_token(user_id: str, email: str, **kwargs) -> str:
    """Access Token 생성 헬퍼"""
    return jwt_handler.create_access_token(user_id, email, **kwargs)


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """토큰 검증 헬퍼"""
    return jwt_handler.verify_token(token, token_type)
