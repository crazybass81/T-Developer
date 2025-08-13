"""
Security Validator Module
Validates download security and prevents malicious access
"""

from typing import Dict, List, Any, Optional
import asyncio
import os
import re
import hashlib
import ipaddress
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SecurityCheck:
    check_name: str
    passed: bool
    risk_level: str  # low, medium, high, critical
    message: str
    recommendation: str


@dataclass
class SecurityReport:
    token: str
    client_ip: str
    user_agent: str
    checks: List[SecurityCheck]
    overall_risk: str
    allowed: bool
    timestamp: datetime


class SecurityValidator:
    """Advanced security validation for downloads"""

    def __init__(self):
        self.version = "1.0.0"

        self.security_config = {
            "blocked_ips": set(),
            "blocked_user_agents": [
                r".*bot.*",
                r".*crawler.*",
                r".*scraper.*",
                r".*wget.*",
                r".*curl.*",
            ],
            "allowed_countries": [],  # Empty means allow all
            "max_requests_per_minute": 10,
            "require_referer": False,
            "allowed_referers": [],
            "token_entropy_threshold": 20,
            "max_token_age_hours": 24,
        }

        self.request_history = []
        self.suspicious_activity = []

        # Known malicious patterns
        self.malicious_patterns = {
            "path_traversal": [r"\.\.\/+", r"%2e%2e%2f", r"%252e%252e%252f"],
            "xss_attempts": [r"<script.*?>", r"javascript:", r"onload=", r"onerror="],
            "injection_attempts": [
                r"union\s+select",
                r"drop\s+table",
                r"exec\s*\(",
                r"eval\s*\(",
            ],
        }

    async def validate_download_request(
        self, token: str, client_info: Dict[str, Any]
    ) -> SecurityReport:
        """Perform comprehensive security validation"""

        client_ip = client_info.get("ip", "unknown")
        user_agent = client_info.get("user_agent", "")
        referer = client_info.get("referer", "")

        checks = []

        # 1. IP Address validation
        ip_check = await self._validate_ip_address(client_ip)
        checks.append(ip_check)

        # 2. User Agent validation
        ua_check = await self._validate_user_agent(user_agent)
        checks.append(ua_check)

        # 3. Token security validation
        token_check = await self._validate_token_security(token)
        checks.append(token_check)

        # 4. Rate limiting check
        rate_check = await self._validate_rate_limiting(client_ip)
        checks.append(rate_check)

        # 5. Referer validation (if required)
        if self.security_config["require_referer"]:
            referer_check = await self._validate_referer(referer)
            checks.append(referer_check)

        # 6. Malicious pattern detection
        pattern_check = await self._detect_malicious_patterns(
            token, user_agent, referer
        )
        checks.append(pattern_check)

        # 7. Suspicious activity detection
        activity_check = await self._detect_suspicious_activity(client_ip)
        checks.append(activity_check)

        # Calculate overall risk and decision
        overall_risk, allowed = self._calculate_risk_score(checks)

        # Log request
        await self._log_request(client_ip, user_agent, token, allowed)

        return SecurityReport(
            token=token,
            client_ip=client_ip,
            user_agent=user_agent,
            checks=checks,
            overall_risk=overall_risk,
            allowed=allowed,
            timestamp=datetime.now(),
        )

    async def _validate_ip_address(self, client_ip: str) -> SecurityCheck:
        """Validate client IP address"""

        try:
            # Check if IP is blocked
            if client_ip in self.security_config["blocked_ips"]:
                return SecurityCheck(
                    check_name="ip_validation",
                    passed=False,
                    risk_level="critical",
                    message=f"IP {client_ip} is blocked",
                    recommendation="Access denied from this IP",
                )

            # Check if IP is valid
            if client_ip != "unknown":
                ip_obj = ipaddress.ip_address(client_ip)

                # Check for private/localhost IPs in production
                if ip_obj.is_private and not self._is_development_mode():
                    return SecurityCheck(
                        check_name="ip_validation",
                        passed=False,
                        risk_level="medium",
                        message="Private IP detected in production",
                        recommendation="Review network configuration",
                    )

            return SecurityCheck(
                check_name="ip_validation",
                passed=True,
                risk_level="low",
                message="IP address validation passed",
                recommendation="Continue monitoring",
            )

        except ValueError:
            return SecurityCheck(
                check_name="ip_validation",
                passed=False,
                risk_level="medium",
                message="Invalid IP address format",
                recommendation="Verify client IP detection",
            )

    async def _validate_user_agent(self, user_agent: str) -> SecurityCheck:
        """Validate user agent string"""

        if not user_agent:
            return SecurityCheck(
                check_name="user_agent_validation",
                passed=False,
                risk_level="medium",
                message="No user agent provided",
                recommendation="Investigate client configuration",
            )

        # Check against blocked user agents
        for pattern in self.security_config["blocked_user_agents"]:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return SecurityCheck(
                    check_name="user_agent_validation",
                    passed=False,
                    risk_level="high",
                    message=f"Blocked user agent pattern: {pattern}",
                    recommendation="Access denied for automated tools",
                )

        # Check for suspicious patterns
        suspicious_patterns = [
            r"python-requests",
            r"urllib",
            r"httplib",
            r"libwww-perl",
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return SecurityCheck(
                    check_name="user_agent_validation",
                    passed=False,
                    risk_level="medium",
                    message=f"Suspicious user agent: {user_agent}",
                    recommendation="Monitor for automated access",
                )

        return SecurityCheck(
            check_name="user_agent_validation",
            passed=True,
            risk_level="low",
            message="User agent validation passed",
            recommendation="Continue monitoring",
        )

    async def _validate_token_security(self, token: str) -> SecurityCheck:
        """Validate download token security"""

        # Check token length
        if len(token) < 16:
            return SecurityCheck(
                check_name="token_security",
                passed=False,
                risk_level="high",
                message="Token too short",
                recommendation="Use longer, more secure tokens",
            )

        # Check token entropy
        entropy = self._calculate_entropy(token)
        if entropy < self.security_config["token_entropy_threshold"]:
            return SecurityCheck(
                check_name="token_security",
                passed=False,
                risk_level="medium",
                message=f"Low token entropy: {entropy}",
                recommendation="Use tokens with higher randomness",
            )

        # Check for common patterns
        common_patterns = [r"123456", r"abcdef", r"000000", r"ffffff"]

        for pattern in common_patterns:
            if re.search(pattern, token, re.IGNORECASE):
                return SecurityCheck(
                    check_name="token_security",
                    passed=False,
                    risk_level="medium",
                    message="Token contains common patterns",
                    recommendation="Generate more random tokens",
                )

        return SecurityCheck(
            check_name="token_security",
            passed=True,
            risk_level="low",
            message="Token security validation passed",
            recommendation="Continue using secure tokens",
        )

    async def _validate_rate_limiting(self, client_ip: str) -> SecurityCheck:
        """Validate request rate limiting"""

        if client_ip == "unknown":
            return SecurityCheck(
                check_name="rate_limiting",
                passed=True,
                risk_level="low",
                message="Rate limiting skipped for unknown IP",
                recommendation="Improve IP detection",
            )

        # Count recent requests
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_requests = [
            req
            for req in self.request_history
            if (req["ip"] == client_ip and req["timestamp"] > one_minute_ago)
        ]

        request_count = len(recent_requests)
        max_requests = self.security_config["max_requests_per_minute"]

        if request_count >= max_requests:
            return SecurityCheck(
                check_name="rate_limiting",
                passed=False,
                risk_level="high",
                message=f"Rate limit exceeded: {request_count}/{max_requests}",
                recommendation="Implement stricter rate limiting",
            )

        return SecurityCheck(
            check_name="rate_limiting",
            passed=True,
            risk_level="low",
            message=f"Rate limit OK: {request_count}/{max_requests}",
            recommendation="Continue monitoring request patterns",
        )

    async def _validate_referer(self, referer: str) -> SecurityCheck:
        """Validate referer header"""

        if not referer:
            return SecurityCheck(
                check_name="referer_validation",
                passed=False,
                risk_level="medium",
                message="Missing required referer",
                recommendation="Ensure proper referer headers",
            )

        # Check against allowed referers
        if self.security_config["allowed_referers"]:
            allowed = False
            for allowed_referer in self.security_config["allowed_referers"]:
                if allowed_referer in referer:
                    allowed = True
                    break

            if not allowed:
                return SecurityCheck(
                    check_name="referer_validation",
                    passed=False,
                    risk_level="high",
                    message=f"Referer not allowed: {referer}",
                    recommendation="Access from allowed domains only",
                )

        return SecurityCheck(
            check_name="referer_validation",
            passed=True,
            risk_level="low",
            message="Referer validation passed",
            recommendation="Continue monitoring referers",
        )

    async def _detect_malicious_patterns(
        self, token: str, user_agent: str, referer: str
    ) -> SecurityCheck:
        """Detect malicious patterns in request"""

        all_text = f"{token} {user_agent} {referer}".lower()

        for category, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, all_text, re.IGNORECASE):
                    return SecurityCheck(
                        check_name="malicious_pattern_detection",
                        passed=False,
                        risk_level="critical",
                        message=f"Malicious pattern detected: {category}",
                        recommendation="Block request and investigate",
                    )

        return SecurityCheck(
            check_name="malicious_pattern_detection",
            passed=True,
            risk_level="low",
            message="No malicious patterns detected",
            recommendation="Continue monitoring",
        )

    async def _detect_suspicious_activity(self, client_ip: str) -> SecurityCheck:
        """Detect suspicious activity patterns"""

        if client_ip == "unknown":
            return SecurityCheck(
                check_name="suspicious_activity_detection",
                passed=True,
                risk_level="low",
                message="Activity detection skipped for unknown IP",
                recommendation="Improve IP tracking",
            )

        # Check for rapid sequential requests
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_requests = [
            req
            for req in self.request_history
            if (req["ip"] == client_ip and req["timestamp"] > one_hour_ago)
        ]

        if len(recent_requests) > 50:  # Arbitrary threshold
            return SecurityCheck(
                check_name="suspicious_activity_detection",
                passed=False,
                risk_level="high",
                message=f"Excessive requests: {len(recent_requests)} in 1 hour",
                recommendation="Investigate potential abuse",
            )

        # Check for failed authentication attempts
        failed_attempts = len(
            [
                act
                for act in self.suspicious_activity
                if (
                    act["ip"] == client_ip
                    and act["type"] == "failed_auth"
                    and act["timestamp"] > one_hour_ago
                )
            ]
        )

        if failed_attempts > 5:
            return SecurityCheck(
                check_name="suspicious_activity_detection",
                passed=False,
                risk_level="medium",
                message=f"Multiple failed attempts: {failed_attempts}",
                recommendation="Consider temporary IP blocking",
            )

        return SecurityCheck(
            check_name="suspicious_activity_detection",
            passed=True,
            risk_level="low",
            message="No suspicious activity detected",
            recommendation="Continue monitoring",
        )

    def _calculate_risk_score(self, checks: List[SecurityCheck]) -> tuple[str, bool]:
        """Calculate overall risk score and access decision"""

        risk_scores = {"low": 1, "medium": 3, "high": 7, "critical": 15}

        total_score = 0
        critical_failures = 0

        for check in checks:
            if not check.passed:
                total_score += risk_scores.get(check.risk_level, 1)
                if check.risk_level == "critical":
                    critical_failures += 1

        # Immediate deny for critical failures
        if critical_failures > 0:
            return "critical", False

        # Calculate overall risk
        if total_score == 0:
            overall_risk = "low"
            allowed = True
        elif total_score <= 5:
            overall_risk = "medium"
            allowed = True  # Allow with monitoring
        elif total_score <= 10:
            overall_risk = "high"
            allowed = False  # Deny access
        else:
            overall_risk = "critical"
            allowed = False

        return overall_risk, allowed

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""

        if not text:
            return 0

        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Calculate entropy
        entropy = 0
        text_len = len(text)

        for count in char_counts.values():
            probability = count / text_len
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)

        return entropy * text_len

    def _is_development_mode(self) -> bool:
        """Check if running in development mode"""

        # Simple check - in production, use proper environment detection
        return os.getenv("ENVIRONMENT", "production") != "production"

    async def _log_request(
        self, client_ip: str, user_agent: str, token: str, allowed: bool
    ) -> None:
        """Log download request for analysis"""

        request_record = {
            "ip": client_ip,
            "user_agent": user_agent,
            "token": token[:8] + "...",  # Partial token for privacy
            "allowed": allowed,
            "timestamp": datetime.now(),
        }

        self.request_history.append(request_record)

        # Keep only recent history (last 24 hours)
        one_day_ago = datetime.now() - timedelta(hours=24)
        self.request_history = [
            req for req in self.request_history if req["timestamp"] > one_day_ago
        ]

        # Log suspicious activity
        if not allowed:
            self.suspicious_activity.append(
                {
                    "type": "blocked_download",
                    "ip": client_ip,
                    "details": f"Download blocked for token: {token[:8]}...",
                    "timestamp": datetime.now(),
                }
            )

    async def block_ip(self, ip: str, reason: str) -> None:
        """Block IP address"""

        self.security_config["blocked_ips"].add(ip)

        self.suspicious_activity.append(
            {
                "type": "ip_blocked",
                "ip": ip,
                "details": f"IP blocked: {reason}",
                "timestamp": datetime.now(),
            }
        )

    async def unblock_ip(self, ip: str) -> bool:
        """Unblock IP address"""

        if ip in self.security_config["blocked_ips"]:
            self.security_config["blocked_ips"].remove(ip)
            return True
        return False

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""

        total_requests = len(self.request_history)
        blocked_requests = len(
            [req for req in self.request_history if not req["allowed"]]
        )

        return {
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "block_rate": blocked_requests / total_requests
            if total_requests > 0
            else 0,
            "blocked_ips": len(self.security_config["blocked_ips"]),
            "suspicious_activities": len(self.suspicious_activity),
        }
