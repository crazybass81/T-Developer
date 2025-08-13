"""
Security Layer Implementation
Handles authentication, authorization, input validation, and data protection
"""
import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import jwt

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for operations"""

    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ADMIN = "admin"


class DataClassification(Enum):
    """Data classification levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class SecurityContext:
    """Security context for requests"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    roles: Set[str] = field(default_factory=set)
    authenticated: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions or "admin" in self.roles

    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.roles


class InputValidator:
    """Validates and sanitizes user input"""

    # Patterns for validation
    PATTERNS = {
        "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
        "url": re.compile(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        "alphanumeric": re.compile(r"^[a-zA-Z0-9]+$"),
        "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
        "safe_string": re.compile(r"^[a-zA-Z0-9\s\-_.]+$"),
    }

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),  # Event handlers
        re.compile(r"<iframe", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
        re.compile(r"DROP\s+TABLE", re.IGNORECASE),
        re.compile(r"DELETE\s+FROM", re.IGNORECASE),
        re.compile(r"INSERT\s+INTO", re.IGNORECASE),
        re.compile(r"UPDATE\s+SET", re.IGNORECASE),
    ]

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email address"""
        return bool(cls.PATTERNS["email"].match(email))

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL"""
        return bool(cls.PATTERNS["url"].match(url))

    @classmethod
    def validate_uuid(cls, uuid_str: str) -> bool:
        """Validate UUID"""
        return bool(cls.PATTERNS["uuid"].match(uuid_str.lower()))

    @classmethod
    def sanitize_string(cls, input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not input_str:
            return ""

        # Truncate to max length
        sanitized = input_str[:max_length]

        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = pattern.sub("", sanitized)

        # Escape HTML entities
        sanitized = sanitized.replace("<", "&lt;")
        sanitized = sanitized.replace(">", "&gt;")
        sanitized = sanitized.replace('"', "&quot;")
        sanitized = sanitized.replace("'", "&#x27;")

        return sanitized.strip()

    @classmethod
    def validate_project_query(cls, query: str) -> Dict[str, Any]:
        """Validate project generation query"""
        errors = []
        warnings = []

        # Check length
        if len(query) < 10:
            errors.append("Query too short (minimum 10 characters)")
        if len(query) > 1000:
            errors.append("Query too long (maximum 1000 characters)")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(query):
                errors.append("Query contains potentially dangerous content")
                break

        # Check for suspicious requests
        suspicious_keywords = ["hack", "exploit", "malware", "virus", "backdoor"]
        for keyword in suspicious_keywords:
            if keyword.lower() in query.lower():
                warnings.append(f"Query contains suspicious keyword: {keyword}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "sanitized_query": cls.sanitize_string(query) if len(errors) == 0 else None,
        }

    @classmethod
    def validate_json(cls, json_str: str) -> Dict[str, Any]:
        """Validate JSON input"""
        try:
            data = json.loads(json_str)
            return {"valid": True, "data": data}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}


class AuthenticationManager:
    """Manages user authentication"""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expiry = timedelta(hours=24)
        self.refresh_token_expiry = timedelta(days=7)

    def generate_token(
        self, user_id: str, permissions: List[str] = None, roles: List[str] = None
    ) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "permissions": permissions or [],
            "roles": roles or [],
            "exp": datetime.utcnow() + self.token_expiry,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + self.refresh_token_expiry,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def create_security_context(self, token: str) -> Optional[SecurityContext]:
        """Create security context from token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        return SecurityContext(
            user_id=payload.get("user_id"),
            permissions=set(payload.get("permissions", [])),
            roles=set(payload.get("roles", [])),
            authenticated=True,
        )

    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2"""
        salt = secrets.token_bytes(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return base64.b64encode(salt + key).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            decoded = base64.b64decode(hashed.encode())
            salt = decoded[:32]
            stored_key = decoded[32:]

            key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

            return hmac.compare_digest(stored_key, key)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


class AuthorizationManager:
    """Manages user authorization"""

    # Role-permission mappings
    ROLE_PERMISSIONS = {
        "admin": {
            "pipeline.execute",
            "pipeline.view",
            "pipeline.delete",
            "project.create",
            "project.view",
            "project.delete",
            "user.manage",
            "settings.manage",
        },
        "developer": {
            "pipeline.execute",
            "pipeline.view",
            "project.create",
            "project.view",
            "project.delete",
        },
        "user": {"pipeline.execute", "pipeline.view", "project.create", "project.view"},
        "viewer": {"pipeline.view", "project.view"},
    }

    @classmethod
    def check_permission(cls, context: SecurityContext, permission: str) -> bool:
        """Check if user has permission"""
        if not context.authenticated:
            return False

        # Check direct permission
        if context.has_permission(permission):
            return True

        # Check role-based permissions
        for role in context.roles:
            if role in cls.ROLE_PERMISSIONS:
                if permission in cls.ROLE_PERMISSIONS[role]:
                    return True

        return False

    @classmethod
    def check_resource_access(
        cls, context: SecurityContext, resource_type: str, resource_id: str, action: str
    ) -> bool:
        """Check if user can access specific resource"""
        # Build permission string
        permission = f"{resource_type}.{action}"

        # Check base permission
        if not cls.check_permission(context, permission):
            return False

        # Additional resource-specific checks could go here
        # For example, checking if user owns the resource

        return True

    @classmethod
    def get_user_permissions(cls, roles: List[str]) -> Set[str]:
        """Get all permissions for given roles"""
        permissions = set()

        for role in roles:
            if role in cls.ROLE_PERMISSIONS:
                permissions.update(cls.ROLE_PERMISSIONS[role])

        return permissions


class DataProtection:
    """Handles data encryption and protection"""

    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key or secrets.token_bytes(32)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

        # Derive key from encryption key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"stable_salt",  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key))

        # Encrypt data
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())

        return base64.b64encode(encrypted).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

        # Derive key
        kdf = PBKDF2(algorithm=hashes.SHA256(), length=32, salt=b"stable_salt", iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key))

        # Decrypt data
        f = Fernet(key)
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = f.decrypt(encrypted)

        return decrypted.decode()

    def mask_pii(self, text: str) -> str:
        """Mask personally identifiable information"""
        # Mask email addresses
        email_pattern = re.compile(r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")
        text = email_pattern.sub(r"***@\2", text)

        # Mask phone numbers
        phone_pattern = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
        text = phone_pattern.sub("XXX-XXX-XXXX", text)

        # Mask credit card numbers
        cc_pattern = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b")
        text = cc_pattern.sub("XXXX-XXXX-XXXX-XXXX", text)

        # Mask SSN
        ssn_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        text = ssn_pattern.sub("XXX-XX-XXXX", text)

        return text

    def sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for logging"""
        sensitive_keys = [
            "password",
            "token",
            "api_key",
            "secret",
            "credit_card",
            "ssn",
            "email",
        ]

        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_log_data(value)
            elif isinstance(value, str):
                sanitized[key] = self.mask_pii(value)
            else:
                sanitized[key] = value

        return sanitized


class RateLimiter:
    """Rate limiting for API protection"""

    def __init__(self):
        self._limits: Dict[str, Dict[str, Any]] = {}
        self._request_history: Dict[str, List[datetime]] = {}

    def configure_limit(self, resource: str, max_requests: int, time_window: int) -> None:
        """Configure rate limit for resource"""
        self._limits[resource] = {
            "max_requests": max_requests,
            "time_window": time_window,  # seconds
        }

    def check_rate_limit(self, resource: str, identifier: str) -> bool:
        """Check if request is within rate limit"""
        if resource not in self._limits:
            return True  # No limit configured

        limit = self._limits[resource]
        key = f"{resource}:{identifier}"
        now = datetime.utcnow()

        # Initialize history if needed
        if key not in self._request_history:
            self._request_history[key] = []

        # Clean old requests
        cutoff = now - timedelta(seconds=limit["time_window"])
        self._request_history[key] = [
            req_time for req_time in self._request_history[key] if req_time > cutoff
        ]

        # Check limit
        if len(self._request_history[key]) >= limit["max_requests"]:
            return False

        # Add current request
        self._request_history[key].append(now)
        return True

    def get_remaining_requests(self, resource: str, identifier: str) -> int:
        """Get remaining requests in current window"""
        if resource not in self._limits:
            return -1  # No limit

        limit = self._limits[resource]
        key = f"{resource}:{identifier}"

        if key not in self._request_history:
            return limit["max_requests"]

        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=limit["time_window"])

        current_requests = sum(1 for req_time in self._request_history[key] if req_time > cutoff)

        return max(0, limit["max_requests"] - current_requests)


# Singleton instances
_auth_manager: Optional[AuthenticationManager] = None
_data_protection: Optional[DataProtection] = None
_rate_limiter: Optional[RateLimiter] = None


def get_auth_manager() -> AuthenticationManager:
    """Get singleton authentication manager"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager


def get_data_protection() -> DataProtection:
    """Get singleton data protection"""
    global _data_protection
    if _data_protection is None:
        _data_protection = DataProtection()
    return _data_protection


def get_rate_limiter() -> RateLimiter:
    """Get singleton rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
        # Configure default limits
        _rate_limiter.configure_limit("pipeline.execute", 10, 60)  # 10 per minute
        _rate_limiter.configure_limit("project.create", 5, 60)  # 5 per minute
    return _rate_limiter


# Export classes and functions
__all__ = [
    "SecurityLevel",
    "DataClassification",
    "SecurityContext",
    "InputValidator",
    "AuthenticationManager",
    "AuthorizationManager",
    "DataProtection",
    "RateLimiter",
    "get_auth_manager",
    "get_data_protection",
    "get_rate_limiter",
]
