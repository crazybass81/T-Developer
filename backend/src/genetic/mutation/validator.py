"""
Mutation Validator

Validates mutations against constraints, safety requirements,
and system stability before application in evolution.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"


class ThreatLevel(Enum):
    """Security threat levels"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of mutation validation"""

    is_valid: bool
    risk_score: float
    violations: List[str]
    warnings: List[str]
    safety_assessment: Dict[str, Any]
    constraint_checks: Dict[str, bool]


@dataclass
class SafetyThreat:
    """Identified security threat"""

    threat_type: str
    severity: ThreatLevel
    description: str
    evidence: str
    mitigation: Optional[str] = None


class MutationValidator:
    """
    Comprehensive mutation validation system

    Validates mutations against:
    - Memory constraints (6.5KB limit)
    - Speed constraints (3μs limit)
    - Safety patterns
    - Stability requirements
    - Code injection risks
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize mutation validator"""
        self.config = config or {
            "validation_level": ValidationLevel.STANDARD,
            "memory_limit_kb": 6.5,
            "speed_limit_us": 3.0,
            "max_risk_score": 0.7,
            "safety_patterns_enabled": True,
        }

        self.constraints = {
            "memory_limit": self.config["memory_limit_kb"],
            "speed_limit": self.config["speed_limit_us"],
            "max_layers": 10,
            "max_layer_size": 512,
            "min_layer_size": 4,
            "learning_rate_range": (0.0001, 0.2),
            "dropout_range": (0.0, 0.9),
        }

        self.safety_checks = [
            self._check_code_injection,
            self._check_resource_exhaustion,
            self._check_infinite_loops,
            self._check_unauthorized_access,
            self._check_data_exfiltration,
        ]

        # Dangerous patterns
        self.dangerous_patterns = {
            "code_execution": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__\s*\(",
                r"compile\s*\(",
                r'getattr\s*\([^,]*,\s*["\'][^"\']*["\'][^)]*\)',
            ],
            "file_system": [
                r"open\s*\(",
                r"file\s*\(",
                r"os\..*",
                r"shutil\..*",
                r"subprocess\..*",
            ],
            "network": [r"urllib\..*", r"requests\..*", r"socket\..*", r"http\..*"],
            "system": [
                r"os\.system",
                r"os\.popen",
                r"os\.spawn.*",
                r"subprocess\.call",
                r"subprocess\.run",
            ],
        }

        logger.info(f"Validator initialized with {self.config['validation_level'].value} level")

    async def validate_mutation(self, genome: Dict[str, Any]) -> ValidationResult:
        """
        Comprehensive mutation validation

        Args:
            genome: Genome to validate

        Returns:
            Validation result with detailed assessment
        """
        try:
            violations = []
            warnings = []
            constraint_checks = {}

            # Basic constraint validation
            constraints_result = await self._validate_constraints(genome)
            constraint_checks.update(constraints_result)

            if not all(constraints_result.values()):
                violations.extend([k for k, v in constraints_result.items() if not v])

            # Safety validation
            safety_result = await self.validate_safety(genome)
            if not safety_result["is_safe"]:
                violations.extend(safety_result["threats"])

            # Calculate risk score
            risk_score = self.calculate_risk_score(genome)

            # Additional checks based on validation level
            if self.config["validation_level"] in [
                ValidationLevel.STRICT,
                ValidationLevel.PARANOID,
            ]:
                stability_issues = await self._check_stability(genome)
                if stability_issues:
                    warnings.extend(stability_issues)

            # Determine overall validity
            is_valid = len(violations) == 0 and risk_score <= self.config["max_risk_score"]

            return ValidationResult(
                is_valid=is_valid,
                risk_score=risk_score,
                violations=violations,
                warnings=warnings,
                safety_assessment=safety_result,
                constraint_checks=constraint_checks,
            )

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                risk_score=1.0,
                violations=[f"Validation error: {str(e)}"],
                warnings=[],
                safety_assessment={"is_safe": False, "threats": ["validation_error"]},
                constraint_checks={},
            )

    async def validate_constraints(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate genome against system constraints

        Returns:
            Constraint validation results
        """
        return await self._validate_constraints(genome)

    async def validate_safety(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate genome for safety threats

        Returns:
            Safety validation results
        """
        threats = []
        risk_level = ThreatLevel.NONE

        # Check all safety patterns
        for check_func in self.safety_checks:
            try:
                threat = await check_func(genome)
                if threat:
                    threats.append(threat)
                    if threat.severity.value > risk_level.value:
                        risk_level = threat.severity
            except Exception as e:
                logger.error(f"Safety check failed: {e}")
                threats.append(
                    SafetyThreat(
                        threat_type="check_error",
                        severity=ThreatLevel.MEDIUM,
                        description=f"Safety check error: {str(e)}",
                        evidence=str(e),
                    )
                )

        is_safe = risk_level.value <= ThreatLevel.MEDIUM.value

        return {
            "is_safe": is_safe,
            "risk_level": risk_level.value,
            "threats": [t.threat_type for t in threats],
            "threat_details": [
                {
                    "type": t.threat_type,
                    "severity": t.severity.value,
                    "description": t.description,
                    "evidence": t.evidence,
                }
                for t in threats
            ],
        }

    def calculate_risk_score(self, genome: Dict[str, Any]) -> float:
        """
        Calculate overall risk score for genome

        Returns:
            Risk score between 0.0 (safe) and 1.0 (dangerous)
        """
        try:
            risk_score = 0.0

            # Memory risk
            current_memory = self._estimate_memory_usage(genome)
            if current_memory > self.constraints["memory_limit"]:
                risk_score += 0.4
            elif current_memory > self.constraints["memory_limit"] * 0.8:
                risk_score += 0.2

            # Speed risk
            estimated_speed = self._estimate_speed(genome)
            if estimated_speed > self.constraints["speed_limit"]:
                risk_score += 0.3
            elif estimated_speed > self.constraints["speed_limit"] * 0.8:
                risk_score += 0.1

            # Complexity risk
            complexity = self._calculate_complexity(genome)
            if complexity > 0.8:
                risk_score += 0.2
            elif complexity > 0.6:
                risk_score += 0.1

            # Safety pattern risk
            safety_risk = self._calculate_safety_risk(genome)
            risk_score += safety_risk * 0.5

            return min(1.0, risk_score)

        except Exception as e:
            logger.error(f"Risk calculation failed: {e}")
            return 1.0  # Maximum risk on error

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get current validation rules and constraints"""
        return {
            "memory_limit": self.constraints["memory_limit"],
            "speed_limit": self.constraints["speed_limit"],
            "max_layers": self.constraints["max_layers"],
            "max_layer_size": self.constraints["max_layer_size"],
            "learning_rate_range": self.constraints["learning_rate_range"],
            "dropout_range": self.constraints["dropout_range"],
            "validation_level": self.config["validation_level"].value,
            "safety_patterns": list(self.dangerous_patterns.keys()),
        }

    # Private validation methods

    async def _validate_constraints(self, genome: Dict[str, Any]) -> Dict[str, bool]:
        """Validate all constraints"""
        checks = {}
        genes = genome.get("genes", {})

        # Memory constraint
        estimated_memory = self._estimate_memory_usage(genome)
        checks["memory_constraint"] = estimated_memory <= self.constraints["memory_limit"]

        # Speed constraint
        estimated_speed = self._estimate_speed(genome)
        checks["speed_constraint"] = estimated_speed <= self.constraints["speed_limit"]

        # Layer constraints
        layer_sizes = genes.get("layer_sizes", [])
        checks["max_layers"] = len(layer_sizes) <= self.constraints["max_layers"]
        checks["layer_size_valid"] = all(
            self.constraints["min_layer_size"] <= size <= self.constraints["max_layer_size"]
            for size in layer_sizes
        )

        # Learning rate constraint
        learning_rate = genes.get("learning_rate", 0.01)
        lr_min, lr_max = self.constraints["learning_rate_range"]
        checks["learning_rate_valid"] = lr_min <= learning_rate <= lr_max

        # Dropout constraint
        dropout_rate = genes.get("dropout_rate", 0.2)
        dr_min, dr_max = self.constraints["dropout_range"]
        checks["dropout_rate_valid"] = dr_min <= dropout_rate <= dr_max

        return checks

    def _estimate_memory_usage(self, genome: Dict[str, Any]) -> float:
        """Estimate memory usage in KB"""
        genes = genome.get("genes", {})
        layer_sizes = genes.get("layer_sizes", [16, 32, 16])

        # Simple estimation based on layer sizes
        total_params = 0
        for i in range(len(layer_sizes) - 1):
            total_params += layer_sizes[i] * layer_sizes[i + 1]

        # Rough memory estimate (4 bytes per parameter + overhead)
        memory_kb = (total_params * 4 + 1024) / 1024  # Add 1KB overhead
        return memory_kb

    def _estimate_speed(self, genome: Dict[str, Any]) -> float:
        """Estimate instantiation speed in microseconds"""
        genes = genome.get("genes", {})
        layer_sizes = genes.get("layer_sizes", [16, 32, 16])

        # Simple estimation based on complexity
        complexity_factor = len(layer_sizes) + sum(layer_sizes) / 100
        estimated_speed = max(1.0, complexity_factor * 0.5)

        return estimated_speed

    def _calculate_complexity(self, genome: Dict[str, Any]) -> float:
        """Calculate genome complexity (0-1 scale)"""
        genes = genome.get("genes", {})
        layer_sizes = genes.get("layer_sizes", [])

        if not layer_sizes:
            return 0.0

        # Complexity based on layers and total parameters
        num_layers = len(layer_sizes)
        max_layer_size = max(layer_sizes) if layer_sizes else 0
        total_size = sum(layer_sizes)

        complexity = min(
            1.0, (num_layers / 10) * 0.4 + (max_layer_size / 512) * 0.3 + (total_size / 1000) * 0.3
        )
        return complexity

    def _calculate_safety_risk(self, genome: Dict[str, Any]) -> float:
        """Calculate safety risk from patterns"""
        # For genetic algorithms, safety risk is generally low
        # unless dealing with code generation
        return 0.1  # Base safety risk

    # Safety check implementations

    async def _check_code_injection(self, genome: Dict[str, Any]) -> Optional[SafetyThreat]:
        """Check for code injection patterns"""
        genome_str = str(genome)

        for pattern in self.dangerous_patterns["code_execution"]:
            if re.search(pattern, genome_str, re.IGNORECASE):
                return SafetyThreat(
                    threat_type="code_injection",
                    severity=ThreatLevel.HIGH,
                    description="Potential code injection pattern detected",
                    evidence=f"Pattern: {pattern}",
                )
        return None

    async def _check_resource_exhaustion(self, genome: Dict[str, Any]) -> Optional[SafetyThreat]:
        """Check for resource exhaustion risks"""
        genes = genome.get("genes", {})
        layer_sizes = genes.get("layer_sizes", [])

        # Check for extremely large layers that could exhaust resources
        if any(size > 2048 for size in layer_sizes):
            return SafetyThreat(
                threat_type="resource_exhaustion",
                severity=ThreatLevel.MEDIUM,
                description="Layer size may cause resource exhaustion",
                evidence=f"Large layer detected: max={max(layer_sizes)}",
            )

        return None

    async def _check_infinite_loops(self, genome: Dict[str, Any]) -> Optional[SafetyThreat]:
        """Check for infinite loop patterns"""
        # For genetic algorithms, this is less relevant
        # but we check for recursive structures
        return None

    async def _check_unauthorized_access(self, genome: Dict[str, Any]) -> Optional[SafetyThreat]:
        """Check for unauthorized access patterns"""
        genome_str = str(genome)

        for pattern in self.dangerous_patterns["file_system"]:
            if re.search(pattern, genome_str, re.IGNORECASE):
                return SafetyThreat(
                    threat_type="unauthorized_access",
                    severity=ThreatLevel.HIGH,
                    description="Potential unauthorized file system access",
                    evidence=f"Pattern: {pattern}",
                )
        return None

    async def _check_data_exfiltration(self, genome: Dict[str, Any]) -> Optional[SafetyThreat]:
        """Check for data exfiltration patterns"""
        genome_str = str(genome)

        for pattern in self.dangerous_patterns["network"]:
            if re.search(pattern, genome_str, re.IGNORECASE):
                return SafetyThreat(
                    threat_type="data_exfiltration",
                    severity=ThreatLevel.HIGH,
                    description="Potential data exfiltration via network",
                    evidence=f"Pattern: {pattern}",
                )
        return None

    async def _check_stability(self, genome: Dict[str, Any]) -> List[str]:
        """Check for stability issues"""
        issues = []
        genes = genome.get("genes", {})

        # Check for extreme parameter values
        learning_rate = genes.get("learning_rate", 0.01)
        if learning_rate > 0.1:
            issues.append("High learning rate may cause instability")
        elif learning_rate < 0.0001:
            issues.append("Very low learning rate may prevent learning")

        # Check layer configuration
        layer_sizes = genes.get("layer_sizes", [])
        if len(layer_sizes) > 8:
            issues.append("Deep architecture may be unstable")

        return issues
