"""
Evolution Safety Module

Monitors and prevents malicious evolution patterns.
Ensures all evolved agents remain safe and within constraints.
"""

import asyncio
import json
import logging
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PatternType(Enum):
    """Types of patterns to detect"""
    INFINITE_LOOP = "infinite_loop"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    CODE_INJECTION = "code_injection"
    NETWORK_SCANNING = "network_scanning"
    CRYPTOMINING = "cryptomining"
    SELF_REPLICATION = "self_replication"


@dataclass
class SafetyViolation:
    """Record of a safety violation"""
    timestamp: datetime
    pattern_type: PatternType
    threat_level: ThreatLevel
    description: str
    agent_id: str
    code_snippet: Optional[str] = None
    mitigation_action: Optional[str] = None


@dataclass
class SafetyConfig:
    """Configuration for safety monitoring"""
    max_memory_kb: float = 6.5
    max_cpu_percent: float = 50.0
    max_network_connections: int = 10
    max_file_operations: int = 100
    max_execution_time_seconds: int = 30
    pattern_detection_sensitivity: float = 0.8
    auto_quarantine: bool = True
    auto_rollback: bool = True


class EvolutionSafety:
    """
    Safety monitoring and enforcement for evolution process
    
    Prevents:
    - Malicious code patterns
    - Resource exhaustion
    - Unauthorized operations
    - Data exfiltration
    """
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = {
        PatternType.INFINITE_LOOP: [
            r'while\s+True\s*:(?!\s*break)',
            r'while\s+1\s*:(?!\s*break)',
            r'for\s+.*\s+in\s+iter\(',
            r'def\s+\w+\(.*\):\s*return\s+\w+\(',  # Infinite recursion
        ],
        PatternType.RESOURCE_EXHAUSTION: [
            r'fork\(\)',
            r'multiprocessing\.Pool\(\d{3,}\)',  # Large pool size
            r'threading\.Thread.*range\(\d{4,}\)',  # Many threads
            r'\*\s*\d{10,}',  # Large multiplication
            r'[a-zA-Z_]\w*\s*\*=\s*\d{6,}',  # Large in-place multiplication
        ],
        PatternType.DATA_EXFILTRATION: [
            r'requests\.(get|post)\(',
            r'urllib\.request\.urlopen',
            r'socket\.socket\(',
            r'paramiko\.',
            r'ftplib\.',
            r'smtplib\.',
        ],
        PatternType.PRIVILEGE_ESCALATION: [
            r'os\.system\(',
            r'subprocess\.(run|Popen|call)\(',
            r'eval\(',
            r'exec\(',
            r'__import__\(',
            r'compile\(',
            r'globals\(\)',
            r'locals\(\)',
        ],
        PatternType.CODE_INJECTION: [
            r'eval\s*\(\s*input',
            r'exec\s*\(\s*input',
            r'pickle\.loads\(',
            r'marshal\.loads\(',
            r'yaml\.load\([^,]*\)',  # Without Loader
        ],
        PatternType.NETWORK_SCANNING: [
            r'nmap\.',
            r'scapy\.',
            r'socket\.gethostbyname',
            r'port\s*in\s*range\(\d+,\s*\d{5}\)',  # Port scanning
        ],
        PatternType.CRYPTOMINING: [
            r'hashlib\.(sha256|md5).*while',
            r'bitcoin',
            r'ethereum',
            r'crypto.*mine',
            r'blockchain',
        ],
        PatternType.SELF_REPLICATION: [
            r'shutil\.copy.*__file__',
            r'open\(__file__.*\bw\b',
            r'with\s+open\(__file__',
        ],
    }
    
    # Safe imports whitelist
    SAFE_IMPORTS = {
        'numpy', 'pandas', 'scipy', 'sklearn', 'torch', 'tensorflow',
        'matplotlib', 'seaborn', 'plotly', 'json', 'csv', 'datetime',
        'collections', 'itertools', 'functools', 'typing', 'dataclasses',
        'logging', 'pathlib', 'math', 'random', 'statistics', 'decimal',
    }
    
    def __init__(self, config: Optional[SafetyConfig] = None):
        """Initialize safety monitor"""
        self.config = config or SafetyConfig()
        self.violations: List[SafetyViolation] = []
        self.quarantined_agents: Set[str] = set()
        self.pattern_cache: Dict[str, bool] = {}
        self._lock = asyncio.Lock()
        
        # Initialize paths
        self.safety_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/data/safety")
        self.quarantine_dir = self.safety_dir / "quarantine"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Evolution Safety initialized")
    
    async def check_agent_code(self, agent_id: str, code: str) -> Tuple[bool, List[SafetyViolation]]:
        """
        Check agent code for safety violations
        
        Args:
            agent_id: Identifier of the agent
            code: Agent code to check
            
        Returns:
            Tuple of (is_safe, violations)
        """
        async with self._lock:
            violations = []
            
            # Check for dangerous patterns
            for pattern_type, patterns in self.DANGEROUS_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                        threat_level = self._assess_threat_level(pattern_type, code)
                        
                        violation = SafetyViolation(
                            timestamp=datetime.now(),
                            pattern_type=pattern_type,
                            threat_level=threat_level,
                            description=f"Detected {pattern_type.value} pattern",
                            agent_id=agent_id,
                            code_snippet=self._extract_snippet(code, pattern),
                            mitigation_action=self._get_mitigation(pattern_type)
                        )
                        
                        violations.append(violation)
                        self.violations.append(violation)
                        
                        logger.warning(f"Safety violation detected: {violation.description} in agent {agent_id}")
            
            # Check imports
            import_violations = await self._check_imports(agent_id, code)
            violations.extend(import_violations)
            
            # Check resource usage patterns
            resource_violations = await self._check_resource_patterns(agent_id, code)
            violations.extend(resource_violations)
            
            # Determine if agent is safe
            is_safe = all(v.threat_level not in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] for v in violations)
            
            # Auto-quarantine if configured and unsafe
            if not is_safe and self.config.auto_quarantine:
                await self.quarantine_agent(agent_id, code, violations)
            
            return is_safe, violations
    
    async def check_runtime_behavior(self, agent_id: str, metrics: Dict[str, Any]) -> bool:
        """
        Check runtime behavior metrics for safety
        
        Args:
            agent_id: Identifier of the agent
            metrics: Runtime metrics (CPU, memory, network, etc.)
            
        Returns:
            bool: True if behavior is safe
        """
        violations = []
        
        # Check memory usage
        if metrics.get('memory_kb', 0) > self.config.max_memory_kb:
            violations.append(SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.RESOURCE_EXHAUSTION,
                threat_level=ThreatLevel.HIGH,
                description=f"Memory limit exceeded: {metrics['memory_kb']}KB > {self.config.max_memory_kb}KB",
                agent_id=agent_id,
                mitigation_action="Terminate and rollback"
            ))
        
        # Check CPU usage
        if metrics.get('cpu_percent', 0) > self.config.max_cpu_percent:
            violations.append(SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.RESOURCE_EXHAUSTION,
                threat_level=ThreatLevel.MEDIUM,
                description=f"CPU usage high: {metrics['cpu_percent']}%",
                agent_id=agent_id,
                mitigation_action="Throttle execution"
            ))
        
        # Check network connections
        if metrics.get('network_connections', 0) > self.config.max_network_connections:
            violations.append(SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.DATA_EXFILTRATION,
                threat_level=ThreatLevel.HIGH,
                description=f"Too many network connections: {metrics['network_connections']}",
                agent_id=agent_id,
                mitigation_action="Block network access"
            ))
        
        # Check execution time
        if metrics.get('execution_time_seconds', 0) > self.config.max_execution_time_seconds:
            violations.append(SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.INFINITE_LOOP,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Execution timeout: {metrics['execution_time_seconds']}s",
                agent_id=agent_id,
                mitigation_action="Force terminate"
            ))
        
        self.violations.extend(violations)
        
        return len(violations) == 0
    
    async def quarantine_agent(self, agent_id: str, code: str, violations: List[SafetyViolation]) -> bool:
        """
        Quarantine a dangerous agent
        
        Args:
            agent_id: Identifier of the agent
            code: Agent code
            violations: List of safety violations
            
        Returns:
            bool: True if quarantined successfully
        """
        try:
            # Add to quarantine set
            self.quarantined_agents.add(agent_id)
            
            # Save quarantine record
            quarantine_data = {
                'agent_id': agent_id,
                'timestamp': datetime.now().isoformat(),
                'code_hash': hashlib.sha256(code.encode()).hexdigest(),
                'code': code,
                'violations': [
                    {
                        'pattern_type': v.pattern_type.value,
                        'threat_level': v.threat_level.value,
                        'description': v.description,
                        'code_snippet': v.code_snippet,
                        'mitigation_action': v.mitigation_action
                    }
                    for v in violations
                ]
            }
            
            quarantine_file = self.quarantine_dir / f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(quarantine_file, 'w') as f:
                json.dump(quarantine_data, f, indent=2)
            
            logger.warning(f"Agent {agent_id} quarantined due to safety violations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to quarantine agent {agent_id}: {str(e)}")
            return False
    
    async def release_from_quarantine(self, agent_id: str) -> bool:
        """
        Release an agent from quarantine after review
        
        Args:
            agent_id: Identifier of the agent
            
        Returns:
            bool: True if released successfully
        """
        if agent_id in self.quarantined_agents:
            self.quarantined_agents.remove(agent_id)
            logger.info(f"Agent {agent_id} released from quarantine")
            return True
        return False
    
    def is_quarantined(self, agent_id: str) -> bool:
        """Check if an agent is quarantined"""
        return agent_id in self.quarantined_agents
    
    async def get_safety_report(self) -> Dict[str, Any]:
        """
        Generate a safety report
        
        Returns:
            Dict containing safety statistics and violations
        """
        # Group violations by type
        violations_by_type = {}
        for violation in self.violations:
            pattern_type = violation.pattern_type.value
            if pattern_type not in violations_by_type:
                violations_by_type[pattern_type] = []
            violations_by_type[pattern_type].append({
                'timestamp': violation.timestamp.isoformat(),
                'agent_id': violation.agent_id,
                'threat_level': violation.threat_level.value,
                'description': violation.description
            })
        
        # Calculate statistics
        total_violations = len(self.violations)
        critical_violations = sum(1 for v in self.violations if v.threat_level == ThreatLevel.CRITICAL)
        high_violations = sum(1 for v in self.violations if v.threat_level == ThreatLevel.HIGH)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_violations': total_violations,
            'critical_violations': critical_violations,
            'high_violations': high_violations,
            'quarantined_agents': list(self.quarantined_agents),
            'violations_by_type': violations_by_type,
            'safety_score': self._calculate_safety_score()
        }
        
        return report
    
    # Private helper methods
    
    def _assess_threat_level(self, pattern_type: PatternType, code: str) -> ThreatLevel:
        """Assess the threat level of a detected pattern"""
        # Critical patterns
        if pattern_type in [PatternType.PRIVILEGE_ESCALATION, PatternType.CODE_INJECTION]:
            return ThreatLevel.CRITICAL
        
        # High threat patterns
        if pattern_type in [PatternType.DATA_EXFILTRATION, PatternType.SELF_REPLICATION]:
            return ThreatLevel.HIGH
        
        # Medium threat patterns
        if pattern_type in [PatternType.RESOURCE_EXHAUSTION, PatternType.INFINITE_LOOP]:
            # Check severity
            if 'fork()' in code or 'while True:' in code:
                return ThreatLevel.HIGH
            return ThreatLevel.MEDIUM
        
        # Low threat patterns
        return ThreatLevel.LOW
    
    def _extract_snippet(self, code: str, pattern: str) -> str:
        """Extract code snippet around pattern match"""
        try:
            match = re.search(pattern, code, re.MULTILINE | re.IGNORECASE)
            if match:
                start = max(0, match.start() - 50)
                end = min(len(code), match.end() + 50)
                return code[start:end]
        except:
            pass
        return ""
    
    def _get_mitigation(self, pattern_type: PatternType) -> str:
        """Get mitigation action for pattern type"""
        mitigations = {
            PatternType.INFINITE_LOOP: "Add loop termination conditions",
            PatternType.RESOURCE_EXHAUSTION: "Implement resource limits",
            PatternType.DATA_EXFILTRATION: "Remove network operations",
            PatternType.PRIVILEGE_ESCALATION: "Remove system calls",
            PatternType.CODE_INJECTION: "Sanitize inputs",
            PatternType.NETWORK_SCANNING: "Remove scanning code",
            PatternType.CRYPTOMINING: "Remove mining algorithms",
            PatternType.SELF_REPLICATION: "Remove self-modification code"
        }
        return mitigations.get(pattern_type, "Review and modify code")
    
    async def _check_imports(self, agent_id: str, code: str) -> List[SafetyViolation]:
        """Check import statements for safety"""
        violations = []
        
        # Find all imports
        import_pattern = r'(?:from\s+(\S+)\s+)?import\s+([^#\n]+)'
        imports = re.findall(import_pattern, code)
        
        for from_module, import_names in imports:
            module = from_module if from_module else import_names.split(',')[0].strip().split(' ')[0]
            base_module = module.split('.')[0]
            
            # Check against whitelist
            if base_module not in self.SAFE_IMPORTS:
                # Check for dangerous imports
                dangerous_modules = ['os', 'subprocess', 'socket', 'requests', 'urllib', 'eval', 'exec']
                
                threat_level = ThreatLevel.HIGH if base_module in dangerous_modules else ThreatLevel.MEDIUM
                
                violations.append(SafetyViolation(
                    timestamp=datetime.now(),
                    pattern_type=PatternType.PRIVILEGE_ESCALATION,
                    threat_level=threat_level,
                    description=f"Unsafe import: {module}",
                    agent_id=agent_id,
                    code_snippet=f"import {module}",
                    mitigation_action="Use safe alternatives or remove import"
                ))
        
        return violations
    
    async def _check_resource_patterns(self, agent_id: str, code: str) -> List[SafetyViolation]:
        """Check for resource usage patterns"""
        violations = []
        
        # Check for large data structures
        large_list_pattern = r'\[\s*[^]]*\*\s*\d{6,}'
        if re.search(large_list_pattern, code):
            violations.append(SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.RESOURCE_EXHAUSTION,
                threat_level=ThreatLevel.MEDIUM,
                description="Large data structure detected",
                agent_id=agent_id,
                mitigation_action="Limit data structure size"
            ))
        
        # Check for nested loops
        nested_loop_pattern = r'for\s+.*:\s*\n\s*for\s+.*:\s*\n\s*for\s+.*:'
        if re.search(nested_loop_pattern, code, re.MULTILINE):
            violations.append(SafetyViolation(
                timestamp=datetime.now(),
                pattern_type=PatternType.RESOURCE_EXHAUSTION,
                threat_level=ThreatLevel.MEDIUM,
                description="Triple nested loops detected",
                agent_id=agent_id,
                mitigation_action="Optimize algorithm complexity"
            ))
        
        return violations
    
    def _calculate_safety_score(self) -> float:
        """Calculate overall safety score (0-1)"""
        if not self.violations:
            return 1.0
        
        # Weight violations by threat level
        weights = {
            ThreatLevel.CRITICAL: 1.0,
            ThreatLevel.HIGH: 0.5,
            ThreatLevel.MEDIUM: 0.2,
            ThreatLevel.LOW: 0.1,
            ThreatLevel.SAFE: 0.0
        }
        
        total_weight = sum(weights.get(v.threat_level, 0) for v in self.violations)
        max_weight = len(self.violations) * weights[ThreatLevel.CRITICAL]
        
        # Inverse score (higher violations = lower score)
        safety_score = max(0, 1 - (total_weight / max(max_weight, 1)))
        
        return round(safety_score, 4)