"""
Message Security Implementation
Day 8: Message Queue System
Generated: 2024-11-18

Message encryption, authentication, and rate limiting
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class MessageEncryption:
    """Message encryption and decryption using Fernet"""

    def __init__(self, key: str):
        # Derive a proper key from the provided string
        self.key = self._derive_key(key.encode())
        self.cipher = Fernet(self.key)

    def _derive_key(self, password: bytes) -> bytes:
        """Derive encryption key from password"""
        salt = b"T-Developer-Salt"  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_message(self, message: Dict) -> Dict:
        """Encrypt sensitive message content"""
        # Serialize message
        message_json = json.dumps(message)

        # Encrypt the serialized message
        encrypted_data = self.cipher.encrypt(message_json.encode())

        # Return wrapper with encrypted payload
        return {
            "encrypted": True,
            "encrypted_payload": base64.b64encode(encrypted_data).decode(),
            "timestamp": datetime.utcnow().isoformat(),
            "encryption_method": "fernet",
        }

    def decrypt_message(self, encrypted_message: Dict) -> Dict:
        """Decrypt encrypted message"""
        if not encrypted_message.get("encrypted"):
            return encrypted_message

        try:
            # Decode and decrypt
            encrypted_data = base64.b64decode(encrypted_message["encrypted_payload"])
            decrypted_data = self.cipher.decrypt(encrypted_data)

            # Parse back to dict
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt message: {e}")


class MessageAuthenticator:
    """Message authentication using HMAC"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def sign_message(self, message: Dict) -> Dict:
        """Add HMAC signature to message"""
        # Add timestamp for replay protection
        signed_message = {**message, "timestamp": datetime.utcnow().isoformat()}

        # Create message string for signing (excluding signature field)
        message_string = self._create_canonical_string(signed_message)

        # Generate HMAC signature
        signature = hmac.new(self.secret_key, message_string.encode(), hashlib.sha256).hexdigest()

        signed_message["signature"] = signature
        return signed_message

    def verify_message(self, signed_message: Dict) -> bool:
        """Verify message HMAC signature"""
        if "signature" not in signed_message:
            return False

        # Extract signature
        received_signature = signed_message.pop("signature")

        # Recreate signature
        message_string = self._create_canonical_string(signed_message)
        expected_signature = hmac.new(
            self.secret_key, message_string.encode(), hashlib.sha256
        ).hexdigest()

        # Restore signature to message
        signed_message["signature"] = received_signature

        # Constant-time comparison
        return hmac.compare_digest(received_signature, expected_signature)

    def _create_canonical_string(self, message: Dict) -> str:
        """Create canonical string representation for signing"""
        # Sort keys and create deterministic string
        sorted_items = sorted(message.items())
        return json.dumps(sorted_items, separators=(",", ":"))

    def is_message_fresh(self, signed_message: Dict, max_age_seconds: int = 300) -> bool:
        """Check if message timestamp is within acceptable range"""
        timestamp_str = signed_message.get("timestamp")
        if not timestamp_str:
            return False

        try:
            message_time = datetime.fromisoformat(timestamp_str)
            age = (datetime.utcnow() - message_time).total_seconds()
            return 0 <= age <= max_age_seconds
        except (ValueError, TypeError):
            return False


class MessageRateLimiter:
    """Rate limiting for message sending"""

    def __init__(self, max_messages: int, time_window: int):
        self.max_messages = max_messages
        self.time_window = time_window  # seconds
        self.agent_activity = {}  # agent_id -> [timestamps]

    def check_rate_limit(self, agent_id: str) -> bool:
        """Check if agent is within rate limit"""
        current_time = time.time()

        # Get agent's activity history
        if agent_id not in self.agent_activity:
            self.agent_activity[agent_id] = []

        activity = self.agent_activity[agent_id]

        # Remove old timestamps outside the time window
        cutoff_time = current_time - self.time_window
        activity[:] = [timestamp for timestamp in activity if timestamp > cutoff_time]

        # Check if under limit
        if len(activity) < self.max_messages:
            # Add current timestamp and allow
            activity.append(current_time)
            return True

        # Rate limit exceeded
        return False

    def get_rate_limit_status(self, agent_id: str) -> Dict:
        """Get current rate limit status for agent"""
        current_time = time.time()

        if agent_id not in self.agent_activity:
            return {
                "messages_sent": 0,
                "messages_remaining": self.max_messages,
                "reset_time": current_time + self.time_window,
            }

        activity = self.agent_activity[agent_id]
        cutoff_time = current_time - self.time_window

        # Count recent messages
        recent_messages = sum(1 for timestamp in activity if timestamp > cutoff_time)

        # Find when oldest message in window will expire
        recent_timestamps = [t for t in activity if t > cutoff_time]
        reset_time = (
            min(recent_timestamps) + self.time_window if recent_timestamps else current_time
        )

        return {
            "messages_sent": recent_messages,
            "messages_remaining": max(0, self.max_messages - recent_messages),
            "reset_time": reset_time,
            "time_until_reset": max(0, reset_time - current_time),
        }

    def reset_rate_limit(self, agent_id: str):
        """Reset rate limit for specific agent"""
        if agent_id in self.agent_activity:
            del self.agent_activity[agent_id]

    def get_global_statistics(self) -> Dict:
        """Get global rate limiting statistics"""
        current_time = time.time()
        cutoff_time = current_time - self.time_window

        total_agents = len(self.agent_activity)
        active_agents = 0
        total_messages = 0
        blocked_agents = 0

        for agent_id, activity in self.agent_activity.items():
            recent_messages = sum(1 for timestamp in activity if timestamp > cutoff_time)
            total_messages += recent_messages

            if recent_messages > 0:
                active_agents += 1

            if recent_messages >= self.max_messages:
                blocked_agents += 1

        return {
            "total_registered_agents": total_agents,
            "active_agents_in_window": active_agents,
            "blocked_agents": blocked_agents,
            "total_messages_in_window": total_messages,
            "average_messages_per_active_agent": total_messages / max(active_agents, 1),
            "block_rate": blocked_agents / max(total_agents, 1),
        }


class MessageValidator:
    """Validate message structure and content"""

    def __init__(self):
        self.required_fields = ["type", "timestamp"]
        self.max_message_size = 1024 * 1024  # 1MB
        self.max_payload_depth = 10

    def validate_message(self, message: Dict) -> Dict:
        """Validate message structure and content"""
        errors = []
        warnings = []

        # Check required fields
        for field in self.required_fields:
            if field not in message:
                errors.append(f"Missing required field: {field}")

        # Check message size
        message_size = len(json.dumps(message))
        if message_size > self.max_message_size:
            errors.append(f"Message size {message_size} exceeds limit {self.max_message_size}")

        # Check payload depth
        if "payload" in message:
            depth = self._get_dict_depth(message["payload"])
            if depth > self.max_payload_depth:
                warnings.append(
                    f"Payload depth {depth} exceeds recommended limit {self.max_payload_depth}"
                )

        # Check for potential security issues
        security_issues = self._check_security_issues(message)
        warnings.extend(security_issues)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "message_size_bytes": message_size,
        }

    def _get_dict_depth(self, obj, depth=0):
        """Calculate maximum depth of nested dictionary"""
        if not isinstance(obj, dict):
            return depth

        if not obj:
            return depth + 1

        return max(self._get_dict_depth(value, depth + 1) for value in obj.values())

    def _check_security_issues(self, message: Dict) -> List[str]:
        """Check for potential security issues in message"""
        issues = []

        # Check for potential injection patterns
        message_str = json.dumps(message).lower()

        suspicious_patterns = [
            "javascript:",
            "<script",
            "eval(",
            "system(",
            "exec(",
            "import os",
            "subprocess",
        ]

        for pattern in suspicious_patterns:
            if pattern in message_str:
                issues.append(f"Suspicious pattern detected: {pattern}")

        # Check for potential credential exposure
        credential_patterns = ["password", "secret", "key", "token", "credential"]

        for pattern in credential_patterns:
            if pattern in message_str and len(message_str) > 50:
                issues.append(f"Potential credential exposure: field containing '{pattern}'")

        return issues


class SecureMessageQueue:
    """Message queue with integrated security features"""

    def __init__(self, encryption_key: str, hmac_key: str, rate_limit_config: Dict):
        self.encryptor = MessageEncryption(encryption_key)
        self.authenticator = MessageAuthenticator(hmac_key)
        self.rate_limiter = MessageRateLimiter(
            rate_limit_config.get("max_messages", 100), rate_limit_config.get("time_window", 3600)
        )
        self.validator = MessageValidator()

    def secure_enqueue(self, message: Dict, agent_id: str, encrypt: bool = False) -> Dict:
        """Enqueue message with security checks"""
        # Validate message
        validation_result = self.validator.validate_message(message)
        if not validation_result["valid"]:
            return {
                "status": "rejected",
                "reason": "validation_failed",
                "errors": validation_result["errors"],
            }

        # Check rate limit
        if not self.rate_limiter.check_rate_limit(agent_id):
            return {
                "status": "rejected",
                "reason": "rate_limited",
                "rate_limit_status": self.rate_limiter.get_rate_limit_status(agent_id),
            }

        # Encrypt if requested
        if encrypt:
            message = self.encryptor.encrypt_message(message)

        # Sign message
        signed_message = self.authenticator.sign_message(message)

        return {
            "status": "accepted",
            "message": signed_message,
            "validation_warnings": validation_result["warnings"],
        }

    def secure_dequeue(self, signed_message: Dict, max_age_seconds: int = 300) -> Dict:
        """Dequeue and verify message security"""
        # Verify signature
        if not self.authenticator.verify_message(signed_message):
            return {"status": "rejected", "reason": "invalid_signature"}

        # Check message freshness
        if not self.authenticator.is_message_fresh(signed_message, max_age_seconds):
            return {"status": "rejected", "reason": "message_too_old"}

        # Decrypt if encrypted
        if signed_message.get("encrypted"):
            try:
                decrypted_message = self.encryptor.decrypt_message(signed_message)
                return {"status": "accepted", "message": decrypted_message, "was_encrypted": True}
            except ValueError as e:
                return {"status": "rejected", "reason": "decryption_failed", "error": str(e)}

        return {"status": "accepted", "message": signed_message, "was_encrypted": False}


class MessageSecurityManager:
    """Unified message security manager for API Gateway integration"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.enable_encryption = self.config.get("enable_encryption", True)

        # Initialize security components
        encryption_key = self.config.get("encryption_key", "default-encryption-key")
        hmac_key = self.config.get("hmac_key", "default-hmac-key")

        self.encryptor = MessageEncryption(encryption_key)
        self.authenticator = MessageAuthenticator(hmac_key)
        self.validator = MessageValidator()

        # Rate limiting config
        rate_limit_config = self.config.get(
            "rate_limit", {"max_messages": 100, "time_window": 3600}
        )
        self.rate_limiter = MessageRateLimiter(
            rate_limit_config["max_messages"], rate_limit_config["time_window"]
        )

    def initialize(self):
        """Initialize the security manager"""
        # Perform any necessary initialization
        pass

    def encrypt_message(self, message: Dict) -> Dict:
        """Encrypt message if encryption is enabled"""
        if self.enable_encryption:
            return self.encryptor.encrypt_message(message)
        return message

    def decrypt_message(self, message: Dict) -> Dict:
        """Decrypt message if it's encrypted"""
        if message.get("encrypted"):
            return self.encryptor.decrypt_message(message)
        return message

    def validate_message_security(self, message: Dict, agent_id: str) -> Dict:
        """Validate message security aspects"""
        # Validate message structure
        validation_result = self.validator.validate_message(message)
        if not validation_result["valid"]:
            return {
                "valid": False,
                "reason": "validation_failed",
                "errors": validation_result["errors"],
            }

        # Check rate limits
        if not self.rate_limiter.check_rate_limit(agent_id):
            return {
                "valid": False,
                "reason": "rate_limited",
                "rate_limit_status": self.rate_limiter.get_rate_limit_status(agent_id),
            }

        return {"valid": True, "warnings": validation_result.get("warnings", [])}

    def sign_message(self, message: Dict) -> Dict:
        """Sign message for authentication"""
        return self.authenticator.sign_message(message)

    def verify_message(self, signed_message: Dict) -> bool:
        """Verify message signature"""
        return self.authenticator.verify_message(signed_message)

    def get_security_stats(self) -> Dict:
        """Get security statistics"""
        return {
            "encryption_enabled": self.enable_encryption,
            "rate_limiting_stats": self.rate_limiter.get_global_statistics(),
            "timestamp": datetime.utcnow().isoformat(),
        }
