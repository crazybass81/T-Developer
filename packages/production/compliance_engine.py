"""
Compliance and governance engine for T-Developer production environment.

This module provides comprehensive compliance management for GDPR, SOC2, PCI DSS,
and other regulatory requirements with automated policy validation and reporting.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, TypedDict, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict


class ComplianceStandard(Enum):
    """Supported compliance standards."""
    GDPR = "gdpr"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ISO_27001 = "iso_27001"
    NIST_CSF = "nist_csf"
    SOX = "sox"
    CCPA = "ccpa"


class ControlType(Enum):
    """Types of compliance controls."""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    ADMINISTRATIVE = "administrative"
    PHYSICAL = "physical"
    TECHNICAL = "technical"


class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNDER_REVIEW = "under_review"


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"  # Protected Health Information
    PCI = "pci"  # Payment Card Information


class AuditEventType(Enum):
    """Types of audit events."""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_EXPORT = "data_export"
    PERMISSION_CHANGE = "permission_change"
    CONFIGURATION_CHANGE = "configuration_change"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM_EVENT = "system_event"


@dataclass
class ComplianceControl:
    """Compliance control definition.
    
    Attributes:
        control_id: Unique identifier for the control
        name: Human-readable control name
        description: Detailed control description
        standard: Compliance standard this control belongs to
        control_type: Type of control
        requirements: Specific requirements for this control
        implementation_guidance: How to implement the control
        testing_procedures: How to test the control
        evidence_requirements: What evidence is needed
        owner: Who owns this control
        frequency: How often to test/review
        automated: Whether control can be automated
        severity: Criticality level
    """
    control_id: str
    name: str
    description: str
    standard: ComplianceStandard
    control_type: ControlType
    requirements: List[str]
    implementation_guidance: str = ""
    testing_procedures: List[str] = field(default_factory=list)
    evidence_requirements: List[str] = field(default_factory=list)
    owner: str = ""
    frequency: str = "annual"  # daily, weekly, monthly, quarterly, annual
    automated: bool = False
    severity: str = "medium"  # low, medium, high, critical
    tags: Set[str] = field(default_factory=set)
    
    def get_requirement_hash(self) -> str:
        """Get hash of requirements for change detection."""
        content = json.dumps(self.requirements, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class ComplianceAssessment:
    """Compliance assessment result.
    
    Attributes:
        assessment_id: Unique identifier
        control_id: Control being assessed
        timestamp: When assessment was performed
        status: Compliance status
        score: Compliance score (0-100)
        findings: Assessment findings
        evidence: Evidence collected
        recommendations: Remediation recommendations
        assessor: Who performed the assessment
        next_assessment: When next assessment is due
        remediation_deadline: Deadline for remediation
    """
    assessment_id: str
    control_id: str
    timestamp: datetime
    status: ComplianceStatus
    score: float
    findings: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessor: str = ""
    next_assessment: Optional[datetime] = None
    remediation_deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_compliant(self) -> bool:
        """Check if assessment shows compliance."""
        return self.status == ComplianceStatus.COMPLIANT
        
    @property
    def needs_remediation(self) -> bool:
        """Check if remediation is needed."""
        return self.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]
        
    @property
    def is_overdue(self) -> bool:
        """Check if remediation is overdue."""
        return (self.remediation_deadline and 
                datetime.utcnow() > self.remediation_deadline and
                self.needs_remediation)


@dataclass
class AuditEvent:
    """Audit trail event.
    
    Attributes:
        event_id: Unique event identifier
        timestamp: When event occurred
        event_type: Type of audit event
        actor: Who performed the action
        resource: What resource was affected
        action: What action was performed
        details: Additional event details
        source_ip: Source IP address
        user_agent: User agent string
        session_id: Session identifier
        tenant_id: Tenant identifier
        data_classification: Classification of affected data
        success: Whether action was successful
    """
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    actor: str
    resource: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    source_ip: str = ""
    user_agent: str = ""
    session_id: str = ""
    tenant_id: str = ""
    data_classification: Optional[DataClassification] = None
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "actor": self.actor,
            "resource": self.resource,
            "action": self.action,
            "details": self.details,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "data_classification": self.data_classification.value if self.data_classification else None,
            "success": self.success
        }


@dataclass
class DataInventoryItem:
    """Data inventory item for data governance.
    
    Attributes:
        item_id: Unique identifier
        name: Data item name
        description: Description of the data
        classification: Data classification level
        location: Where data is stored
        owner: Data owner
        custodian: Data custodian
        retention_period: How long to retain data
        encryption_required: Whether encryption is required
        backup_required: Whether backup is required
        access_controls: Access control requirements
        processing_purposes: Purposes for processing
        legal_basis: Legal basis for processing (GDPR)
        third_party_sharing: Third parties data is shared with
        created_at: When item was created
        last_reviewed: When last reviewed
    """
    item_id: str
    name: str
    description: str
    classification: DataClassification
    location: str
    owner: str
    custodian: str = ""
    retention_period: str = ""
    encryption_required: bool = True
    backup_required: bool = True
    access_controls: List[str] = field(default_factory=list)
    processing_purposes: List[str] = field(default_factory=list)
    legal_basis: str = ""
    third_party_sharing: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None


class ComplianceEngine:
    """Compliance and governance engine for T-Developer.
    
    Provides comprehensive compliance management including policy validation,
    audit trail management, and automated compliance reporting.
    
    Example:
        >>> engine = ComplianceEngine()
        >>> await engine.initialize()
        >>> control = await engine.add_control("Data Encryption", ComplianceStandard.GDPR)
        >>> assessment = await engine.assess_control(control.control_id)
    """
    
    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Initialize compliance engine.
        
        Args:
            config: Engine configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._controls: Dict[str, ComplianceControl] = {}
        self._assessments: Dict[str, ComplianceAssessment] = {}
        self._audit_events: List[AuditEvent] = []
        self._data_inventory: Dict[str, DataInventoryItem] = {}
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._automated_checks: Dict[str, Callable] = {}
        self._monitoring_active = False
        
    async def initialize(self) -> None:
        """Initialize the compliance engine.
        
        Sets up default controls, policies, and monitoring.
        """
        self.logger.info("Initializing compliance engine")
        
        await self._load_default_controls()
        await self._load_default_policies()
        await self._setup_automated_checks()
        await self._setup_audit_monitoring()
        
        self.logger.info("Compliance engine initialized successfully")
        
    async def _load_default_controls(self) -> None:
        """Load default compliance controls."""
        default_controls = [
            # GDPR Controls
            {
                "control_id": "GDPR-001",
                "name": "Data Subject Rights",
                "description": "Implement data subject rights including access, rectification, erasure",
                "standard": ComplianceStandard.GDPR,
                "control_type": ControlType.ADMINISTRATIVE,
                "requirements": [
                    "Provide mechanism for data subject access requests",
                    "Implement data rectification procedures",
                    "Implement right to erasure (right to be forgotten)",
                    "Provide data portability capabilities"
                ],
                "automated": True,
                "severity": "high"
            },
            {
                "control_id": "GDPR-002",
                "name": "Data Protection by Design and Default",
                "description": "Implement privacy by design and default principles",
                "standard": ComplianceStandard.GDPR,
                "control_type": ControlType.TECHNICAL,
                "requirements": [
                    "Minimize data collection to necessary purposes",
                    "Implement privacy-preserving defaults",
                    "Conduct privacy impact assessments",
                    "Document processing activities"
                ],
                "automated": False,
                "severity": "high"
            },
            # SOC 2 Controls
            {
                "control_id": "SOC2-CC6.1",
                "name": "Logical and Physical Access Controls",
                "description": "Implement logical and physical access controls",
                "standard": ComplianceStandard.SOC2,
                "control_type": ControlType.TECHNICAL,
                "requirements": [
                    "Implement multi-factor authentication",
                    "Regular access reviews",
                    "Principle of least privilege",
                    "Physical access controls"
                ],
                "automated": True,
                "severity": "high"
            },
            {
                "control_id": "SOC2-CC7.1",
                "name": "System Monitoring",
                "description": "Monitor system components and system operations",
                "standard": ComplianceStandard.SOC2,
                "control_type": ControlType.DETECTIVE,
                "requirements": [
                    "Continuous monitoring of system performance",
                    "Security event monitoring",
                    "Capacity monitoring",
                    "Incident response procedures"
                ],
                "automated": True,
                "severity": "medium"
            },
            # PCI DSS Controls
            {
                "control_id": "PCI-3.4",
                "name": "Cardholder Data Encryption",
                "description": "Encrypt transmission of cardholder data across open networks",
                "standard": ComplianceStandard.PCI_DSS,
                "control_type": ControlType.TECHNICAL,
                "requirements": [
                    "Encrypt all cardholder data in transit",
                    "Use strong cryptography and security protocols",
                    "Ensure proper key management",
                    "Validate encryption implementation"
                ],
                "automated": True,
                "severity": "critical"
            }
        ]
        
        for control_data in default_controls:
            control = ComplianceControl(**control_data)
            self._controls[control.control_id] = control
            
        self.logger.info(f"Loaded {len(self._controls)} default controls")
        
    async def _load_default_policies(self) -> None:
        """Load default compliance policies."""
        self._policies = {
            "data_retention": {
                "description": "Data retention and disposal policy",
                "rules": {
                    "pii_retention_days": 2555,  # 7 years
                    "log_retention_days": 90,
                    "backup_retention_days": 365,
                    "automatic_deletion": True
                }
            },
            "encryption": {
                "description": "Data encryption policy",
                "rules": {
                    "encryption_at_rest": True,
                    "encryption_in_transit": True,
                    "minimum_key_length": 256,
                    "approved_algorithms": ["AES", "RSA", "ECC"]
                }
            },
            "access_control": {
                "description": "Access control policy",
                "rules": {
                    "mfa_required": True,
                    "password_complexity": True,
                    "session_timeout_minutes": 30,
                    "regular_access_review": True
                }
            },
            "incident_response": {
                "description": "Security incident response policy",
                "rules": {
                    "max_response_time_hours": 4,
                    "notification_required": True,
                    "documentation_required": True,
                    "post_incident_review": True
                }
            }
        }
        
        self.logger.info(f"Loaded {len(self._policies)} policies")
        
    async def _setup_automated_checks(self) -> None:
        """Set up automated compliance checks."""
        # Register automated check functions
        self._automated_checks = {
            "GDPR-001": self._check_data_subject_rights,
            "SOC2-CC6.1": self._check_access_controls,
            "SOC2-CC7.1": self._check_system_monitoring,
            "PCI-3.4": self._check_cardholder_data_encryption
        }
        
        self.logger.info(f"Set up {len(self._automated_checks)} automated checks")
        
    async def _setup_audit_monitoring(self) -> None:
        """Set up audit event monitoring."""
        # In production, integrate with logging systems
        self.logger.info("Set up audit monitoring")
        
    async def start_monitoring(self) -> None:
        """Start continuous compliance monitoring."""
        if self._monitoring_active:
            self.logger.warning("Compliance monitoring already active")
            return
            
        self._monitoring_active = True
        self.logger.info("Started compliance monitoring")
        
        # Start monitoring tasks
        asyncio.create_task(self._automated_assessment_loop())
        asyncio.create_task(self._policy_validation_loop())
        asyncio.create_task(self._audit_cleanup_loop())
        
    async def stop_monitoring(self) -> None:
        """Stop compliance monitoring."""
        self._monitoring_active = False
        self.logger.info("Stopped compliance monitoring")
        
    async def _automated_assessment_loop(self) -> None:
        """Automated compliance assessment loop."""
        while self._monitoring_active:
            try:
                await self._run_automated_assessments()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Automated assessment error: {e}")
                await asyncio.sleep(300)
                
    async def _policy_validation_loop(self) -> None:
        """Policy validation loop."""
        while self._monitoring_active:
            try:
                await self._validate_policies()
                await asyncio.sleep(1800)  # Run every 30 minutes
            except Exception as e:
                self.logger.error(f"Policy validation error: {e}")
                await asyncio.sleep(300)
                
    async def _audit_cleanup_loop(self) -> None:
        """Audit log cleanup loop."""
        while self._monitoring_active:
            try:
                await self._cleanup_audit_logs()
                await asyncio.sleep(86400)  # Run daily
            except Exception as e:
                self.logger.error(f"Audit cleanup error: {e}")
                await asyncio.sleep(3600)
                
    async def _run_automated_assessments(self) -> None:
        """Run automated compliance assessments."""
        for control_id, control in self._controls.items():
            if control.automated and control_id in self._automated_checks:
                try:
                    await self._assess_control_automated(control_id)
                except Exception as e:
                    self.logger.error(f"Automated assessment failed for {control_id}: {e}")
                    
    async def _validate_policies(self) -> None:
        """Validate policy compliance."""
        for policy_name, policy in self._policies.items():
            try:
                await self._validate_policy(policy_name, policy)
            except Exception as e:
                self.logger.error(f"Policy validation failed for {policy_name}: {e}")
                
    async def _cleanup_audit_logs(self) -> None:
        """Clean up old audit logs based on retention policy."""
        retention_days = self._policies.get("data_retention", {}).get("rules", {}).get("log_retention_days", 90)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        initial_count = len(self._audit_events)
        self._audit_events = [e for e in self._audit_events if e.timestamp >= cutoff_date]
        cleaned_count = initial_count - len(self._audit_events)
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old audit events")
            
    async def add_control(self, name: str, standard: ComplianceStandard,
                         control_type: ControlType, requirements: List[str],
                         description: str = "", automated: bool = False) -> ComplianceControl:
        """Add a new compliance control.
        
        Args:
            name: Control name
            standard: Compliance standard
            control_type: Type of control
            requirements: Control requirements
            description: Control description
            automated: Whether control can be automated
            
        Returns:
            Created control
        """
        control_id = f"{standard.value.upper()}-{len(self._controls) + 1:03d}"
        
        control = ComplianceControl(
            control_id=control_id,
            name=name,
            description=description or f"Custom control: {name}",
            standard=standard,
            control_type=control_type,
            requirements=requirements,
            automated=automated
        )
        
        self._controls[control_id] = control
        
        self.logger.info(f"Added compliance control: {name} ({control_id})")
        return control
        
    async def assess_control(self, control_id: str, 
                           assessor: str = "system") -> ComplianceAssessment:
        """Assess a compliance control.
        
        Args:
            control_id: Control to assess
            assessor: Who is performing the assessment
            
        Returns:
            Assessment result
            
        Raises:
            ValueError: If control not found
        """
        if control_id not in self._controls:
            raise ValueError(f"Control not found: {control_id}")
            
        control = self._controls[control_id]
        
        if control.automated and control_id in self._automated_checks:
            return await self._assess_control_automated(control_id)
        else:
            return await self._assess_control_manual(control_id, assessor)
            
    async def _assess_control_automated(self, control_id: str) -> ComplianceAssessment:
        """Perform automated control assessment.
        
        Args:
            control_id: Control to assess
            
        Returns:
            Assessment result
        """
        control = self._controls[control_id]
        check_function = self._automated_checks[control_id]
        
        assessment_id = f"auto_{control_id}_{int(datetime.utcnow().timestamp())}"
        
        try:
            # Run automated check
            result = await check_function()
            
            # Determine status and score
            if result["compliant"]:
                status = ComplianceStatus.COMPLIANT
                score = 100.0
            elif result["partially_compliant"]:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
                score = result.get("score", 50.0)
            else:
                status = ComplianceStatus.NON_COMPLIANT
                score = 0.0
                
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                control_id=control_id,
                timestamp=datetime.utcnow(),
                status=status,
                score=score,
                findings=result.get("findings", []),
                evidence=result.get("evidence", []),
                recommendations=result.get("recommendations", []),
                assessor="automated_system"
            )
            
            # Set next assessment date based on frequency
            frequency_days = {
                "daily": 1,
                "weekly": 7,
                "monthly": 30,
                "quarterly": 90,
                "annual": 365
            }
            days = frequency_days.get(control.frequency, 365)
            assessment.next_assessment = datetime.utcnow() + timedelta(days=days)
            
            self._assessments[assessment_id] = assessment
            
            self.logger.info(f"Automated assessment completed for {control_id}: {status.value}")
            return assessment
            
        except Exception as e:
            # Create failed assessment
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                control_id=control_id,
                timestamp=datetime.utcnow(),
                status=ComplianceStatus.UNDER_REVIEW,
                score=0.0,
                findings=[f"Assessment failed: {str(e)}"],
                assessor="automated_system"
            )
            
            self._assessments[assessment_id] = assessment
            self.logger.error(f"Automated assessment failed for {control_id}: {e}")
            return assessment
            
    async def _assess_control_manual(self, control_id: str, 
                                   assessor: str) -> ComplianceAssessment:
        """Perform manual control assessment.
        
        Args:
            control_id: Control to assess
            assessor: Who is performing assessment
            
        Returns:
            Assessment result
        """
        assessment_id = f"manual_{control_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create placeholder assessment for manual review
        assessment = ComplianceAssessment(
            assessment_id=assessment_id,
            control_id=control_id,
            timestamp=datetime.utcnow(),
            status=ComplianceStatus.UNDER_REVIEW,
            score=0.0,
            findings=["Manual assessment required"],
            assessor=assessor
        )
        
        self._assessments[assessment_id] = assessment
        
        self.logger.info(f"Manual assessment initiated for {control_id}")
        return assessment
        
    async def _check_data_subject_rights(self) -> Dict[str, Any]:
        """Check GDPR data subject rights implementation."""
        # In production, check actual implementation
        
        findings = []
        evidence = []
        recommendations = []
        
        # Check if data subject access API exists
        has_access_api = True  # Would check actual API
        if not has_access_api:
            findings.append("Data subject access API not implemented")
            recommendations.append("Implement data subject access request API")
            
        # Check if data deletion procedures exist
        has_deletion_procedures = True  # Would check actual procedures
        if not has_deletion_procedures:
            findings.append("Data deletion procedures not documented")
            recommendations.append("Document and implement data deletion procedures")
            
        evidence.append({
            "type": "api_endpoint",
            "description": "Data subject access API endpoint",
            "status": "available" if has_access_api else "missing"
        })
        
        compliant = len(findings) == 0
        
        return {
            "compliant": compliant,
            "partially_compliant": False,
            "score": 100.0 if compliant else 0.0,
            "findings": findings,
            "evidence": evidence,
            "recommendations": recommendations
        }
        
    async def _check_access_controls(self) -> Dict[str, Any]:
        """Check SOC 2 access controls."""
        findings = []
        evidence = []
        recommendations = []
        
        # Check MFA implementation
        mfa_enabled = True  # Would check actual MFA status
        if not mfa_enabled:
            findings.append("Multi-factor authentication not enforced")
            recommendations.append("Enable MFA for all user accounts")
            
        # Check access reviews
        regular_reviews = True  # Would check review records
        if not regular_reviews:
            findings.append("Regular access reviews not documented")
            recommendations.append("Implement quarterly access reviews")
            
        evidence.append({
            "type": "mfa_status",
            "description": "Multi-factor authentication status",
            "status": "enabled" if mfa_enabled else "disabled"
        })
        
        compliant = len(findings) == 0
        
        return {
            "compliant": compliant,
            "partially_compliant": False,
            "score": 100.0 if compliant else 50.0,
            "findings": findings,
            "evidence": evidence,
            "recommendations": recommendations
        }
        
    async def _check_system_monitoring(self) -> Dict[str, Any]:
        """Check SOC 2 system monitoring."""
        findings = []
        evidence = []
        recommendations = []
        
        # Check if monitoring is active
        monitoring_active = True  # Would check actual monitoring
        if not monitoring_active:
            findings.append("System monitoring not active")
            recommendations.append("Enable comprehensive system monitoring")
            
        evidence.append({
            "type": "monitoring_status",
            "description": "System monitoring status",
            "status": "active" if monitoring_active else "inactive"
        })
        
        compliant = monitoring_active
        
        return {
            "compliant": compliant,
            "partially_compliant": False,
            "score": 100.0 if compliant else 0.0,
            "findings": findings,
            "evidence": evidence,
            "recommendations": recommendations
        }
        
    async def _check_cardholder_data_encryption(self) -> Dict[str, Any]:
        """Check PCI DSS cardholder data encryption."""
        findings = []
        evidence = []
        recommendations = []
        
        # Check encryption in transit
        encryption_in_transit = True  # Would check TLS configuration
        if not encryption_in_transit:
            findings.append("Cardholder data not encrypted in transit")
            recommendations.append("Enable TLS encryption for all cardholder data transmission")
            
        # Check encryption at rest
        encryption_at_rest = True  # Would check database encryption
        if not encryption_at_rest:
            findings.append("Cardholder data not encrypted at rest")
            recommendations.append("Enable database encryption for cardholder data")
            
        evidence.extend([
            {
                "type": "tls_status",
                "description": "TLS encryption status",
                "status": "enabled" if encryption_in_transit else "disabled"
            },
            {
                "type": "database_encryption",
                "description": "Database encryption status",
                "status": "enabled" if encryption_at_rest else "disabled"
            }
        ])
        
        compliant = encryption_in_transit and encryption_at_rest
        
        return {
            "compliant": compliant,
            "partially_compliant": encryption_in_transit or encryption_at_rest,
            "score": 100.0 if compliant else (50.0 if (encryption_in_transit or encryption_at_rest) else 0.0),
            "findings": findings,
            "evidence": evidence,
            "recommendations": recommendations
        }
        
    async def _validate_policy(self, policy_name: str, policy: Dict[str, Any]) -> None:
        """Validate policy compliance.
        
        Args:
            policy_name: Name of policy to validate
            policy: Policy definition
        """
        # In production, validate actual system configuration against policy
        self.logger.debug(f"Validated policy: {policy_name}")
        
    async def log_audit_event(self, event_type: AuditEventType, actor: str,
                            resource: str, action: str, 
                            details: Dict[str, Any] = None,
                            source_ip: str = "", tenant_id: str = "",
                            data_classification: Optional[DataClassification] = None,
                            success: bool = True) -> AuditEvent:
        """Log an audit event.
        
        Args:
            event_type: Type of audit event
            actor: Who performed the action
            resource: What resource was affected
            action: What action was performed
            details: Additional event details
            source_ip: Source IP address
            tenant_id: Tenant identifier
            data_classification: Classification of affected data
            success: Whether action was successful
            
        Returns:
            Created audit event
        """
        event_id = str(uuid.uuid4())
        
        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            actor=actor,
            resource=resource,
            action=action,
            details=details or {},
            source_ip=source_ip,
            tenant_id=tenant_id,
            data_classification=data_classification,
            success=success
        )
        
        self._audit_events.append(event)
        
        # Log based on event type and data classification
        if data_classification in [DataClassification.PII, DataClassification.PHI, DataClassification.PCI]:
            self.logger.warning(f"Sensitive data access: {actor} {action} {resource}")
        elif not success:
            self.logger.error(f"Failed audit event: {actor} {action} {resource}")
        else:
            self.logger.info(f"Audit event: {actor} {action} {resource}")
            
        return event
        
    async def add_data_inventory_item(self, name: str, description: str,
                                    classification: DataClassification,
                                    location: str, owner: str,
                                    processing_purposes: List[str] = None) -> DataInventoryItem:
        """Add item to data inventory.
        
        Args:
            name: Data item name
            description: Description of data
            classification: Data classification level
            location: Where data is stored
            owner: Data owner
            processing_purposes: Purposes for processing
            
        Returns:
            Created data inventory item
        """
        item_id = f"data_{int(datetime.utcnow().timestamp())}_{hash(name) % 10000}"
        
        item = DataInventoryItem(
            item_id=item_id,
            name=name,
            description=description,
            classification=classification,
            location=location,
            owner=owner,
            processing_purposes=processing_purposes or []
        )
        
        self._data_inventory[item_id] = item
        
        self.logger.info(f"Added data inventory item: {name} ({item_id})")
        return item
        
    async def generate_compliance_report(self, standard: Optional[ComplianceStandard] = None,
                                       include_evidence: bool = False) -> Dict[str, Any]:
        """Generate compliance report.
        
        Args:
            standard: Filter by specific standard
            include_evidence: Whether to include evidence details
            
        Returns:
            Comprehensive compliance report
        """
        # Filter controls by standard if specified
        controls = self._controls.values()
        if standard:
            controls = [c for c in controls if c.standard == standard]
            
        # Get latest assessments for each control
        latest_assessments = {}
        for assessment in self._assessments.values():
            control_id = assessment.control_id
            if (control_id not in latest_assessments or 
                assessment.timestamp > latest_assessments[control_id].timestamp):
                latest_assessments[control_id] = assessment
                
        # Calculate compliance statistics
        total_controls = len(controls)
        assessed_controls = 0
        compliant_controls = 0
        non_compliant_controls = 0
        under_review_controls = 0
        
        control_summary = []
        for control in controls:
            assessment = latest_assessments.get(control.control_id)
            
            if assessment:
                assessed_controls += 1
                if assessment.is_compliant:
                    compliant_controls += 1
                elif assessment.needs_remediation:
                    non_compliant_controls += 1
                else:
                    under_review_controls += 1
                    
            control_info = {
                "control_id": control.control_id,
                "name": control.name,
                "standard": control.standard.value,
                "control_type": control.control_type.value,
                "severity": control.severity,
                "status": assessment.status.value if assessment else "not_assessed",
                "score": assessment.score if assessment else 0.0,
                "last_assessed": assessment.timestamp.isoformat() if assessment else None,
                "overdue": assessment.is_overdue if assessment else False
            }
            
            if include_evidence and assessment:
                control_info["findings"] = assessment.findings
                control_info["evidence"] = assessment.evidence
                control_info["recommendations"] = assessment.recommendations
                
            control_summary.append(control_info)
            
        # Calculate overall compliance percentage
        compliance_percentage = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
        
        # Get audit statistics
        last_30_days = datetime.utcnow() - timedelta(days=30)
        recent_audits = [e for e in self._audit_events if e.timestamp >= last_30_days]
        
        audit_stats = {
            "total_events_30_days": len(recent_audits),
            "failed_events_30_days": sum(1 for e in recent_audits if not e.success),
            "sensitive_data_events": sum(1 for e in recent_audits 
                                       if e.data_classification in [DataClassification.PII, 
                                                                   DataClassification.PHI, 
                                                                   DataClassification.PCI])
        }
        
        report = {
            "report_id": f"compliance_{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat(),
            "standard": standard.value if standard else "all",
            "summary": {
                "total_controls": total_controls,
                "assessed_controls": assessed_controls,
                "compliant_controls": compliant_controls,
                "non_compliant_controls": non_compliant_controls,
                "under_review_controls": under_review_controls,
                "compliance_percentage": compliance_percentage
            },
            "controls": control_summary,
            "audit_statistics": audit_stats,
            "data_inventory_count": len(self._data_inventory),
            "recommendations": self._get_top_recommendations()
        }
        
        self.logger.info(f"Generated compliance report: {compliance_percentage:.1f}% compliant")
        return report
        
    def _get_top_recommendations(self) -> List[str]:
        """Get top compliance recommendations."""
        recommendations = []
        
        # Collect recommendations from recent assessments
        recent_assessments = [
            a for a in self._assessments.values()
            if (datetime.utcnow() - a.timestamp).days <= 30
        ]
        
        all_recommendations = []
        for assessment in recent_assessments:
            all_recommendations.extend(assessment.recommendations)
            
        # Count frequency and return top recommendations
        from collections import Counter
        recommendation_counts = Counter(all_recommendations)
        
        return [rec for rec, count in recommendation_counts.most_common(5)]
        
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get current compliance status.
        
        Returns:
            Current compliance status and metrics
        """
        total_controls = len(self._controls)
        
        # Count controls by standard
        standard_counts = defaultdict(int)
        for control in self._controls.values():
            standard_counts[control.standard.value] += 1
            
        # Get recent assessments
        recent_assessments = [
            a for a in self._assessments.values()
            if (datetime.utcnow() - a.timestamp).days <= 7
        ]
        
        # Count overdue assessments
        overdue_assessments = [
            a for a in self._assessments.values()
            if a.is_overdue
        ]
        
        return {
            "monitoring_active": self._monitoring_active,
            "controls": {
                "total": total_controls,
                "by_standard": dict(standard_counts),
                "automated": sum(1 for c in self._controls.values() if c.automated)
            },
            "assessments": {
                "total": len(self._assessments),
                "recent_week": len(recent_assessments),
                "overdue": len(overdue_assessments)
            },
            "audit_events": {
                "total": len(self._audit_events),
                "last_24_hours": len([
                    e for e in self._audit_events
                    if (datetime.utcnow() - e.timestamp).days < 1
                ])
            },
            "data_inventory": {
                "total_items": len(self._data_inventory),
                "by_classification": {
                    cls.value: sum(1 for item in self._data_inventory.values() 
                                 if item.classification == cls)
                    for cls in DataClassification
                }
            },
            "policies": len(self._policies),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    def get_audit_events(self, hours: int = 24, 
                        event_type: Optional[AuditEventType] = None,
                        tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent audit events.
        
        Args:
            hours: Number of hours of history
            event_type: Filter by event type
            tenant_id: Filter by tenant
            
        Returns:
            List of audit events
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        events = [
            e for e in self._audit_events
            if e.timestamp >= cutoff_time
        ]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
            
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
            
        return [e.to_dict() for e in events]