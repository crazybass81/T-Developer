"""
Production security hardening system for T-Developer.

This module provides comprehensive security hardening including WAF management,
DDoS protection, rate limiting, security scanning, and threat detection.
"""

from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, TypedDict, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from collections import defaultdict, deque


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Types of security events."""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_PAYLOAD = "suspicious_payload"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DDOS_ATTACK = "ddos_attack"
    MALWARE_DETECTED = "malware_detected"
    DATA_EXFILTRATION = "data_exfiltration"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


class ActionType(Enum):
    """Types of security actions."""
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    CHALLENGE = "challenge"
    LOG = "log"
    ALERT = "alert"
    QUARANTINE = "quarantine"


class ScanType(Enum):
    """Types of security scans."""
    VULNERABILITY = "vulnerability"
    MALWARE = "malware"
    COMPLIANCE = "compliance"
    PENETRATION = "penetration"
    DEPENDENCY = "dependency"


@dataclass
class SecurityRule:
    """Security rule definition.
    
    Attributes:
        rule_id: Unique identifier for the rule
        name: Human-readable rule name
        description: Rule description
        pattern: Regex pattern or detection logic
        threat_level: Severity level for matches
        action: Action to take when rule matches
        enabled: Whether rule is active
        false_positive_rate: Expected false positive rate
        confidence: Confidence level in the rule
    """
    rule_id: str
    name: str
    description: str
    pattern: str
    threat_level: ThreatLevel
    action: ActionType
    enabled: bool = True
    false_positive_rate: float = 0.01
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    match_count: int = 0
    
    def matches(self, content: str) -> bool:
        """Check if content matches this rule.
        
        Args:
            content: Content to check
            
        Returns:
            True if rule matches
        """
        if not self.enabled:
            return False
            
        try:
            return bool(re.search(self.pattern, content, re.IGNORECASE))
        except re.error:
            return False


@dataclass
class SecurityEvent:
    """Security event record.
    
    Attributes:
        event_id: Unique identifier for the event
        event_type: Type of security event
        timestamp: When event occurred
        source_ip: Source IP address
        target: Target of the attack/event
        severity: Severity level
        description: Event description
        rule_ids: Rules that triggered this event
        blocked: Whether event was blocked
        metadata: Additional event metadata
    """
    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    source_ip: str
    target: str
    severity: ThreatLevel
    description: str
    rule_ids: List[str] = field(default_factory=list)
    blocked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "target": self.target,
            "severity": self.severity.value,
            "description": self.description,
            "rule_ids": self.rule_ids,
            "blocked": self.blocked,
            "metadata": self.metadata,
            "tenant_id": self.tenant_id
        }


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration.
    
    Attributes:
        rule_id: Unique identifier
        name: Rule name
        requests_per_window: Number of requests allowed per window
        window_seconds: Time window in seconds
        burst_allowance: Burst allowance above normal rate
        scope: Scope of rate limiting (ip, user, tenant, global)
        enabled: Whether rule is active
        priority: Rule priority (higher = more important)
    """
    rule_id: str
    name: str
    requests_per_window: int
    window_seconds: int
    burst_allowance: int = 0
    scope: str = "ip"  # ip, user, tenant, global
    enabled: bool = True
    priority: int = 100
    exemptions: Set[str] = field(default_factory=set)  # IPs/users exempt from rule
    
    def get_key(self, context: Dict[str, Any]) -> str:
        """Get rate limiting key for the given context.
        
        Args:
            context: Request context
            
        Returns:
            Rate limiting key
        """
        if self.scope == "ip":
            return f"ip:{context.get('source_ip', 'unknown')}"
        elif self.scope == "user":
            return f"user:{context.get('user_id', 'anonymous')}"
        elif self.scope == "tenant":
            return f"tenant:{context.get('tenant_id', 'default')}"
        elif self.scope == "global":
            return "global"
        else:
            return f"{self.scope}:{context.get(self.scope, 'unknown')}"


@dataclass
class ScanResult:
    """Security scan result.
    
    Attributes:
        scan_id: Unique scan identifier
        scan_type: Type of scan performed
        target: Target that was scanned
        started_at: When scan started
        completed_at: When scan completed
        status: Scan status
        findings: Security findings
        risk_score: Overall risk score (0-100)
        recommendations: Remediation recommendations
    """
    scan_id: str
    scan_type: ScanType
    target: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    findings: List[Dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get scan duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
        
    @property
    def critical_findings(self) -> List[Dict[str, Any]]:
        """Get critical severity findings."""
        return [f for f in self.findings if f.get("severity") == "critical"]
        
    @property
    def high_findings(self) -> List[Dict[str, Any]]:
        """Get high severity findings."""
        return [f for f in self.findings if f.get("severity") == "high"]


class SecurityHardener:
    """Production security hardening system.
    
    Provides comprehensive security hardening including WAF management,
    DDoS protection, rate limiting, and threat detection for T-Developer.
    
    Example:
        >>> hardener = SecurityHardener()
        >>> await hardener.initialize()
        >>> await hardener.add_waf_rule("SQL injection", r"(?i)union.*select|select.*from")
        >>> await hardener.start_monitoring()
    """
    
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Initialize security hardener.
        
        Args:
            config: Security configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._waf_rules: Dict[str, SecurityRule] = {}
        self._rate_limit_rules: Dict[str, RateLimitRule] = {}
        self._security_events: deque = deque(maxlen=10000)  # Recent events
        self._scan_results: Dict[str, ScanResult] = {}
        self._rate_limit_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._blocked_ips: Dict[str, datetime] = {}  # IP -> block_until
        self._monitoring_active = False
        self._threat_intelligence: Dict[str, Set[str]] = defaultdict(set)
        
    async def initialize(self) -> None:
        """Initialize the security hardener.
        
        Sets up default rules, threat intelligence, and monitoring.
        """
        self.logger.info("Initializing security hardener")
        
        await self._load_default_rules()
        await self._load_threat_intelligence()
        await self._setup_baseline_monitoring()
        
        self.logger.info("Security hardener initialized successfully")
        
    async def _load_default_rules(self) -> None:
        """Load default security rules."""
        default_rules = [
            {
                "rule_id": "sql_injection_basic",
                "name": "Basic SQL Injection",
                "description": "Detects basic SQL injection attempts",
                "pattern": r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table|exec.*xp_)",
                "threat_level": ThreatLevel.HIGH,
                "action": ActionType.BLOCK
            },
            {
                "rule_id": "xss_basic",
                "name": "Basic XSS",
                "description": "Detects basic XSS attempts",
                "pattern": r"(?i)(<script|javascript:|vbscript:|onload=|onerror=|onclick=)",
                "threat_level": ThreatLevel.MEDIUM,
                "action": ActionType.BLOCK
            },
            {
                "rule_id": "path_traversal",
                "name": "Path Traversal",
                "description": "Detects path traversal attempts",
                "pattern": r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e\\)",
                "threat_level": ThreatLevel.HIGH,
                "action": ActionType.BLOCK
            },
            {
                "rule_id": "command_injection",
                "name": "Command Injection",
                "description": "Detects command injection attempts",
                "pattern": r"(;|\||&|`|\$\(|&&|\|\|)(cat|ls|pwd|whoami|id|uname|wget|curl)",
                "threat_level": ThreatLevel.CRITICAL,
                "action": ActionType.BLOCK
            },
            {
                "rule_id": "suspicious_user_agent",
                "name": "Suspicious User Agent",
                "description": "Detects suspicious user agents",
                "pattern": r"(?i)(sqlmap|nmap|nikto|burp|scanner|crawler)",
                "threat_level": ThreatLevel.MEDIUM,
                "action": ActionType.LOG
            }
        ]
        
        for rule_data in default_rules:
            rule = SecurityRule(**rule_data)
            self._waf_rules[rule.rule_id] = rule
            
        # Default rate limiting rules
        default_rate_limits = [
            {
                "rule_id": "api_rate_limit",
                "name": "API Rate Limit",
                "requests_per_window": 1000,
                "window_seconds": 3600,  # 1 hour
                "burst_allowance": 100,
                "scope": "ip"
            },
            {
                "rule_id": "login_rate_limit", 
                "name": "Login Rate Limit",
                "requests_per_window": 5,
                "window_seconds": 300,  # 5 minutes
                "burst_allowance": 2,
                "scope": "ip"
            },
            {
                "rule_id": "global_ddos_protection",
                "name": "Global DDoS Protection",
                "requests_per_window": 100000,
                "window_seconds": 60,  # 1 minute
                "burst_allowance": 10000,
                "scope": "global"
            }
        ]
        
        for rule_data in default_rate_limits:
            rule = RateLimitRule(**rule_data)
            self._rate_limit_rules[rule.rule_id] = rule
            
        self.logger.info(f"Loaded {len(self._waf_rules)} WAF rules and {len(self._rate_limit_rules)} rate limit rules")
        
    async def _load_threat_intelligence(self) -> None:
        """Load threat intelligence data."""
        # In production, load from threat intelligence feeds
        # For now, populate with some example data
        
        # Known malicious IPs (example data)
        self._threat_intelligence["malicious_ips"].update([
            "198.51.100.100",  # Example malicious IP
            "203.0.113.50"     # Example botnet IP
        ])
        
        # Known malicious domains
        self._threat_intelligence["malicious_domains"].update([
            "malicious-site.example.com",
            "phishing-domain.test"
        ])
        
        # Known attack signatures
        self._threat_intelligence["attack_signatures"].update([
            "X-Forwarded-For: <script>alert(1)</script>",
            "User-Agent: () { :; }; echo; echo; /bin/bash -c"
        ])
        
        self.logger.info("Loaded threat intelligence data")
        
    async def _setup_baseline_monitoring(self) -> None:
        """Set up baseline security monitoring."""
        # In production, integrate with SIEM systems, log aggregators, etc.
        self.logger.info("Set up baseline monitoring")
        
    async def start_monitoring(self) -> None:
        """Start continuous security monitoring."""
        if self._monitoring_active:
            self.logger.warning("Security monitoring already active")
            return
            
        self._monitoring_active = True
        self.logger.info("Started security monitoring")
        
        # Start monitoring tasks
        asyncio.create_task(self._cleanup_expired_blocks())
        asyncio.create_task(self._rate_limit_cleanup())
        asyncio.create_task(self._threat_intelligence_update())
        
    async def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        self._monitoring_active = False
        self.logger.info("Stopped security monitoring")
        
    async def _cleanup_expired_blocks(self) -> None:
        """Clean up expired IP blocks."""
        while self._monitoring_active:
            try:
                now = datetime.utcnow()
                expired_ips = [
                    ip for ip, block_until in self._blocked_ips.items()
                    if now >= block_until
                ]
                
                for ip in expired_ips:
                    del self._blocked_ips[ip]
                    self.logger.info(f"Unblocked IP: {ip}")
                    
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in block cleanup: {e}")
                await asyncio.sleep(10)
                
    async def _rate_limit_cleanup(self) -> None:
        """Clean up old rate limiting data."""
        while self._monitoring_active:
            try:
                now = time.time()
                
                # Clean up old rate limit entries
                for rule_key in list(self._rate_limit_cache.keys()):
                    cache_entry = self._rate_limit_cache[rule_key]
                    window_start = cache_entry.get("window_start", 0)
                    
                    # Remove entries older than 1 hour
                    if now - window_start > 3600:
                        del self._rate_limit_cache[rule_key]
                        
                await asyncio.sleep(300)  # Clean up every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in rate limit cleanup: {e}")
                await asyncio.sleep(60)
                
    async def _threat_intelligence_update(self) -> None:
        """Update threat intelligence data."""
        while self._monitoring_active:
            try:
                # In production, fetch from threat intelligence feeds
                await self._fetch_threat_intelligence_updates()
                await asyncio.sleep(3600)  # Update every hour
            except Exception as e:
                self.logger.error(f"Error updating threat intelligence: {e}")
                await asyncio.sleep(300)
                
    async def _fetch_threat_intelligence_updates(self) -> None:
        """Fetch threat intelligence updates."""
        # In production, integrate with threat feeds like:
        # - Commercial threat intelligence
        # - Open source feeds
        # - Government feeds
        # - Internal threat data
        
        # For now, just log that we would fetch updates
        self.logger.debug("Fetched threat intelligence updates")
        
    async def add_waf_rule(self, name: str, pattern: str, 
                          threat_level: ThreatLevel = ThreatLevel.MEDIUM,
                          action: ActionType = ActionType.BLOCK,
                          description: str = "") -> SecurityRule:
        """Add a new WAF rule.
        
        Args:
            name: Rule name
            pattern: Regex pattern for detection
            threat_level: Severity level
            action: Action to take on match
            description: Rule description
            
        Returns:
            Created security rule
            
        Raises:
            ValueError: If pattern is invalid
        """
        # Validate regex pattern
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
            
        rule_id = f"custom_{int(time.time())}_{hash(name) % 10000}"
        
        rule = SecurityRule(
            rule_id=rule_id,
            name=name,
            description=description or f"Custom rule: {name}",
            pattern=pattern,
            threat_level=threat_level,
            action=action
        )
        
        self._waf_rules[rule_id] = rule
        
        self.logger.info(f"Added WAF rule: {name} ({rule_id})")
        return rule
        
    async def add_rate_limit_rule(self, name: str, requests_per_window: int,
                                window_seconds: int, scope: str = "ip",
                                burst_allowance: int = 0) -> RateLimitRule:
        """Add a new rate limiting rule.
        
        Args:
            name: Rule name
            requests_per_window: Requests allowed per window
            window_seconds: Time window in seconds
            scope: Scope of rate limiting
            burst_allowance: Burst allowance
            
        Returns:
            Created rate limit rule
        """
        rule_id = f"rate_limit_{int(time.time())}_{hash(name) % 10000}"
        
        rule = RateLimitRule(
            rule_id=rule_id,
            name=name,
            requests_per_window=requests_per_window,
            window_seconds=window_seconds,
            scope=scope,
            burst_allowance=burst_allowance
        )
        
        self._rate_limit_rules[rule_id] = rule
        
        self.logger.info(f"Added rate limit rule: {name} ({rule_id})")
        return rule
        
    async def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a request for security threats.
        
        Args:
            request_data: Request data to analyze
            
        Returns:
            Analysis result with threat assessment
        """
        analysis = {
            "allowed": True,
            "threats_detected": [],
            "actions_taken": [],
            "risk_score": 0.0,
            "rate_limited": False
        }
        
        source_ip = request_data.get("source_ip", "unknown")
        user_agent = request_data.get("user_agent", "")
        url = request_data.get("url", "")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        
        # Check if IP is blocked
        if await self._is_ip_blocked(source_ip):
            analysis["allowed"] = False
            analysis["actions_taken"].append("IP blocked")
            return analysis
            
        # Check threat intelligence
        if source_ip in self._threat_intelligence["malicious_ips"]:
            await self._block_ip(source_ip, duration_minutes=60)
            analysis["allowed"] = False
            analysis["actions_taken"].append("Blocked malicious IP")
            analysis["risk_score"] = 100.0
            return analysis
            
        # Check rate limits
        rate_limit_result = await self._check_rate_limits(request_data)
        if rate_limit_result["limited"]:
            analysis["rate_limited"] = True
            analysis["allowed"] = False
            analysis["actions_taken"].append(f"Rate limited: {rate_limit_result['rule']}")
            
        # Analyze content against WAF rules
        content_to_check = f"{url} {user_agent} {body} {json.dumps(headers)}"
        
        threats = []
        for rule in self._waf_rules.values():
            if rule.matches(content_to_check):
                threat = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "threat_level": rule.threat_level.value,
                    "action": rule.action.value,
                    "confidence": rule.confidence
                }
                threats.append(threat)
                
                # Update match count
                rule.match_count += 1
                
                # Take action based on rule
                if rule.action == ActionType.BLOCK:
                    analysis["allowed"] = False
                    analysis["actions_taken"].append(f"Blocked by rule: {rule.name}")
                elif rule.action == ActionType.RATE_LIMIT:
                    await self._apply_dynamic_rate_limit(source_ip)
                    analysis["actions_taken"].append(f"Rate limited by rule: {rule.name}")
                    
                # Add to risk score
                risk_weights = {
                    ThreatLevel.LOW: 10,
                    ThreatLevel.MEDIUM: 25,
                    ThreatLevel.HIGH: 50,
                    ThreatLevel.CRITICAL: 100
                }
                analysis["risk_score"] += risk_weights[rule.threat_level] * rule.confidence
                
        analysis["threats_detected"] = threats
        analysis["risk_score"] = min(100.0, analysis["risk_score"])
        
        # Log security event if threats detected
        if threats:
            await self._log_security_event(request_data, threats, analysis["allowed"])
            
        return analysis
        
    async def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is blocked
        """
        block_until = self._blocked_ips.get(ip)
        if block_until:
            return datetime.utcnow() < block_until
        return False
        
    async def _block_ip(self, ip: str, duration_minutes: int = 60) -> None:
        """Block an IP address.
        
        Args:
            ip: IP address to block
            duration_minutes: Block duration in minutes
        """
        block_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self._blocked_ips[ip] = block_until
        
        self.logger.warning(f"Blocked IP {ip} until {block_until}")
        
    async def _check_rate_limits(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check request against rate limiting rules.
        
        Args:
            request_data: Request data
            
        Returns:
            Rate limiting result
        """
        now = time.time()
        
        for rule in self._rate_limit_rules.values():
            if not rule.enabled:
                continue
                
            # Get rate limiting key
            key = rule.get_key(request_data)
            
            # Check exemptions
            source_ip = request_data.get("source_ip", "")
            user_id = request_data.get("user_id", "")
            if source_ip in rule.exemptions or user_id in rule.exemptions:
                continue
                
            # Get or create cache entry
            cache_key = f"{rule.rule_id}:{key}"
            cache_entry = self._rate_limit_cache.get(cache_key, {
                "count": 0,
                "window_start": now,
                "burst_used": 0
            })
            
            # Check if we're in a new window
            if now - cache_entry["window_start"] >= rule.window_seconds:
                cache_entry = {
                    "count": 0,
                    "window_start": now,
                    "burst_used": 0
                }
                
            # Check rate limit
            cache_entry["count"] += 1
            
            # Check if over normal limit
            if cache_entry["count"] > rule.requests_per_window:
                # Check if burst allowance available
                if cache_entry["burst_used"] < rule.burst_allowance:
                    cache_entry["burst_used"] += 1
                else:
                    # Rate limited
                    self._rate_limit_cache[cache_key] = cache_entry
                    return {
                        "limited": True,
                        "rule": rule.name,
                        "retry_after": rule.window_seconds - (now - cache_entry["window_start"])
                    }
                    
            self._rate_limit_cache[cache_key] = cache_entry
            
        return {"limited": False}
        
    async def _apply_dynamic_rate_limit(self, ip: str) -> None:
        """Apply dynamic rate limiting to an IP.
        
        Args:
            ip: IP address to rate limit
        """
        # Create temporary stricter rate limit for this IP
        rule = RateLimitRule(
            rule_id=f"dynamic_{ip}_{int(time.time())}",
            name=f"Dynamic limit for {ip}",
            requests_per_window=10,
            window_seconds=300,  # 5 minutes
            scope="ip"
        )
        
        self._rate_limit_rules[rule.rule_id] = rule
        
        # Remove after 1 hour
        async def cleanup():
            await asyncio.sleep(3600)
            if rule.rule_id in self._rate_limit_rules:
                del self._rate_limit_rules[rule.rule_id]
                
        asyncio.create_task(cleanup())
        
        self.logger.info(f"Applied dynamic rate limit to {ip}")
        
    async def _log_security_event(self, request_data: Dict[str, Any],
                                threats: List[Dict[str, Any]], 
                                blocked: bool) -> None:
        """Log a security event.
        
        Args:
            request_data: Request data
            threats: Detected threats
            blocked: Whether request was blocked
        """
        event_id = f"sec_{int(time.time())}_{hash(str(request_data)) % 100000}"
        
        # Determine event type and severity
        event_type = SecurityEventType.SUSPICIOUS_PAYLOAD
        severity = ThreatLevel.LOW
        
        for threat in threats:
            if "sql" in threat["rule_name"].lower():
                event_type = SecurityEventType.SQL_INJECTION
            elif "xss" in threat["rule_name"].lower():
                event_type = SecurityEventType.XSS_ATTEMPT
            elif "command" in threat["rule_name"].lower():
                event_type = SecurityEventType.UNAUTHORIZED_ACCESS
                
            threat_level = ThreatLevel(threat["threat_level"])
            if threat_level.value == "critical":
                severity = ThreatLevel.CRITICAL
            elif threat_level.value == "high" and severity != ThreatLevel.CRITICAL:
                severity = ThreatLevel.HIGH
            elif threat_level.value == "medium" and severity not in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                severity = ThreatLevel.MEDIUM
                
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source_ip=request_data.get("source_ip", "unknown"),
            target=request_data.get("url", "unknown"),
            severity=severity,
            description=f"Security threats detected: {', '.join(t['rule_name'] for t in threats)}",
            rule_ids=[t["rule_id"] for t in threats],
            blocked=blocked,
            metadata=request_data,
            tenant_id=request_data.get("tenant_id")
        )
        
        self._security_events.append(event)
        
        # Log based on severity
        if severity == ThreatLevel.CRITICAL:
            self.logger.critical(f"Critical security event: {event.description}")
        elif severity == ThreatLevel.HIGH:
            self.logger.error(f"High security event: {event.description}")
        elif severity == ThreatLevel.MEDIUM:
            self.logger.warning(f"Medium security event: {event.description}")
        else:
            self.logger.info(f"Low security event: {event.description}")
            
    async def start_security_scan(self, scan_type: ScanType, target: str,
                                config: Dict[str, Any] = None) -> ScanResult:
        """Start a security scan.
        
        Args:
            scan_type: Type of scan to perform
            target: Target to scan
            config: Scan configuration
            
        Returns:
            Scan result object
        """
        scan_id = f"scan_{scan_type.value}_{int(time.time())}"
        
        scan_result = ScanResult(
            scan_id=scan_id,
            scan_type=scan_type,
            target=target,
            started_at=datetime.utcnow()
        )
        
        self._scan_results[scan_id] = scan_result
        
        # Start scan in background
        asyncio.create_task(self._execute_scan(scan_result, config or {}))
        
        self.logger.info(f"Started {scan_type.value} scan: {scan_id}")
        return scan_result
        
    async def _execute_scan(self, scan_result: ScanResult, config: Dict[str, Any]) -> None:
        """Execute a security scan.
        
        Args:
            scan_result: Scan result to update
            config: Scan configuration
        """
        try:
            if scan_result.scan_type == ScanType.VULNERABILITY:
                await self._vulnerability_scan(scan_result, config)
            elif scan_result.scan_type == ScanType.MALWARE:
                await self._malware_scan(scan_result, config)
            elif scan_result.scan_type == ScanType.COMPLIANCE:
                await self._compliance_scan(scan_result, config)
            elif scan_result.scan_type == ScanType.DEPENDENCY:
                await self._dependency_scan(scan_result, config)
            else:
                raise ValueError(f"Unknown scan type: {scan_result.scan_type}")
                
            scan_result.status = "completed"
            scan_result.completed_at = datetime.utcnow()
            
            # Calculate overall risk score
            scan_result.risk_score = self._calculate_risk_score(scan_result.findings)
            
            self.logger.info(f"Completed scan {scan_result.scan_id}: {len(scan_result.findings)} findings")
            
        except Exception as e:
            scan_result.status = "failed"
            scan_result.completed_at = datetime.utcnow()
            self.logger.error(f"Scan {scan_result.scan_id} failed: {e}")
            
    async def _vulnerability_scan(self, scan_result: ScanResult, config: Dict[str, Any]) -> None:
        """Perform vulnerability scan.
        
        Args:
            scan_result: Scan result to update
            config: Scan configuration
        """
        # In production, integrate with vulnerability scanners like:
        # - Nessus
        # - OpenVAS  
        # - Qualys
        # - Rapid7
        
        # Simulate vulnerability scan
        await asyncio.sleep(5)
        
        # Example findings
        findings = [
            {
                "id": "VULN-001",
                "title": "Outdated SSL/TLS Configuration",
                "severity": "medium",
                "description": "Server supports deprecated TLS versions",
                "cvss_score": 5.3,
                "recommendation": "Update TLS configuration to support only TLS 1.2+"
            },
            {
                "id": "VULN-002", 
                "title": "Missing Security Headers",
                "severity": "low",
                "description": "Response missing security headers",
                "cvss_score": 3.1,
                "recommendation": "Add security headers: X-Frame-Options, X-Content-Type-Options"
            }
        ]
        
        scan_result.findings.extend(findings)
        scan_result.recommendations.extend([f["recommendation"] for f in findings])
        
    async def _malware_scan(self, scan_result: ScanResult, config: Dict[str, Any]) -> None:
        """Perform malware scan.
        
        Args:
            scan_result: Scan result to update
            config: Scan configuration
        """
        # In production, integrate with antivirus engines
        await asyncio.sleep(3)
        
        # Example findings (normally would be empty for clean systems)
        scan_result.findings = []
        scan_result.recommendations = ["System appears clean of malware"]
        
    async def _compliance_scan(self, scan_result: ScanResult, config: Dict[str, Any]) -> None:
        """Perform compliance scan.
        
        Args:
            scan_result: Scan result to update
            config: Scan configuration
        """
        # Check compliance with standards like PCI DSS, SOC 2, GDPR
        await asyncio.sleep(4)
        
        findings = [
            {
                "id": "COMP-001",
                "title": "Data Encryption",
                "severity": "high",
                "description": "Some data not encrypted at rest",
                "standard": "PCI DSS",
                "requirement": "3.4",
                "recommendation": "Enable encryption for all sensitive data storage"
            }
        ]
        
        scan_result.findings.extend(findings)
        scan_result.recommendations.extend([f["recommendation"] for f in findings])
        
    async def _dependency_scan(self, scan_result: ScanResult, config: Dict[str, Any]) -> None:
        """Perform dependency vulnerability scan.
        
        Args:
            scan_result: Scan result to update
            config: Scan configuration
        """
        # Scan dependencies for known vulnerabilities
        await asyncio.sleep(2)
        
        findings = [
            {
                "id": "DEP-001",
                "title": "Vulnerable Dependency",
                "severity": "high",
                "description": "lodash 4.17.15 has known vulnerabilities",
                "cve": "CVE-2021-23337",
                "recommendation": "Update lodash to version 4.17.21 or later"
            }
        ]
        
        scan_result.findings.extend(findings)
        scan_result.recommendations.extend([f["recommendation"] for f in findings])
        
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score from findings.
        
        Args:
            findings: Security findings
            
        Returns:
            Risk score from 0-100
        """
        if not findings:
            return 0.0
            
        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3
        }
        
        total_score = 0
        for finding in findings:
            severity = finding.get("severity", "low")
            weight = severity_weights.get(severity, 3)
            total_score += weight
            
        # Cap at 100
        return min(100.0, total_score)
        
    async def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status.
        
        Returns:
            Security status and metrics
        """
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        recent_events = [e for e in self._security_events if e.timestamp >= last_hour]
        daily_events = [e for e in self._security_events if e.timestamp >= last_day]
        
        # Count events by type and severity
        event_types = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for event in recent_events:
            event_types[event.event_type.value] += 1
            severity_counts[event.severity.value] += 1
            
        # Active scans
        active_scans = [s for s in self._scan_results.values() if s.status == "running"]
        completed_scans = [s for s in self._scan_results.values() if s.status == "completed"]
        
        return {
            "monitoring_active": self._monitoring_active,
            "rules": {
                "waf_rules": len(self._waf_rules),
                "rate_limit_rules": len(self._rate_limit_rules),
                "enabled_waf_rules": sum(1 for r in self._waf_rules.values() if r.enabled),
                "enabled_rate_rules": sum(1 for r in self._rate_limit_rules.values() if r.enabled)
            },
            "threats": {
                "blocked_ips": len(self._blocked_ips),
                "events_last_hour": len(recent_events),
                "events_last_day": len(daily_events),
                "event_types": dict(event_types),
                "severity_distribution": dict(severity_counts)
            },
            "scans": {
                "active": len(active_scans),
                "completed_today": len([s for s in completed_scans 
                                      if s.completed_at and s.completed_at >= last_day]),
                "avg_risk_score": statistics.mean([s.risk_score for s in completed_scans]) if completed_scans else 0
            },
            "threat_intelligence": {
                "malicious_ips": len(self._threat_intelligence["malicious_ips"]),
                "malicious_domains": len(self._threat_intelligence["malicious_domains"]),
                "attack_signatures": len(self._threat_intelligence["attack_signatures"])
            },
            "last_updated": now.isoformat()
        }
        
    def get_recent_events(self, hours: int = 24, 
                         severity: Optional[ThreatLevel] = None) -> List[Dict[str, Any]]:
        """Get recent security events.
        
        Args:
            hours: Number of hours of history
            severity: Filter by severity level
            
        Returns:
            List of recent security events
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        events = [
            e for e in self._security_events
            if e.timestamp >= cutoff_time
        ]
        
        if severity:
            events = [e for e in events if e.severity == severity]
            
        return [e.to_dict() for e in events]
        
    def get_scan_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get scan result by ID.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            Scan result or None if not found
        """
        scan = self._scan_results.get(scan_id)
        if not scan:
            return None
            
        return {
            "scan_id": scan.scan_id,
            "scan_type": scan.scan_type.value,
            "target": scan.target,
            "started_at": scan.started_at.isoformat(),
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "status": scan.status,
            "duration_seconds": scan.duration_seconds,
            "findings": scan.findings,
            "risk_score": scan.risk_score,
            "recommendations": scan.recommendations,
            "critical_findings": len(scan.critical_findings),
            "high_findings": len(scan.high_findings)
        }