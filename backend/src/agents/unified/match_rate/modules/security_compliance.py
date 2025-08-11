"""
Security Compliance Module
Checks security compliance and requirements matching
"""

from typing import Dict, List, Any, Optional
import re


class SecurityCompliance:
    """Checks security compliance"""
    
    def __init__(self):
        self.security_frameworks = self._build_security_frameworks()
        self.compliance_standards = self._build_compliance_standards()
        
    async def check(
        self,
        components: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Check security compliance"""
        
        compliance_results = {}
        
        # Extract security requirements
        security_requirements = self._extract_security_requirements(requirements)
        
        for component in components:
            component_id = component.get('id', component.get('name'))
            
            # Extract security features
            security_features = self._extract_security_features(component)
            
            # Check compliance areas
            compliance_checks = {
                'authentication': self._check_authentication_compliance(security_features, security_requirements),
                'authorization': self._check_authorization_compliance(security_features, security_requirements),
                'encryption': self._check_encryption_compliance(security_features, security_requirements),
                'data_protection': self._check_data_protection_compliance(security_features, security_requirements),
                'audit_logging': self._check_audit_compliance(security_features, security_requirements),
                'vulnerability_management': self._check_vulnerability_management(security_features, security_requirements)
            }
            
            # Calculate overall compliance score
            compliance_score = self._calculate_compliance_score(compliance_checks)
            
            compliance_results[component_id] = {
                'compliance_score': compliance_score,
                'detailed_checks': compliance_checks,
                'security_gaps': self._identify_security_gaps(compliance_checks),
                'compliance_level': self._determine_compliance_level(compliance_score),
                'remediation_actions': self._suggest_remediation_actions(compliance_checks)
            }
        
        return compliance_results
    
    def _extract_security_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Extract security requirements"""
        
        text = str(requirements).lower()
        
        return {
            'authentication_required': any(term in text for term in ['auth', 'login', 'signin']),
            'authorization_required': any(term in text for term in ['authorization', 'permissions', 'roles']),
            'encryption_required': any(term in text for term in ['encrypt', 'ssl', 'tls', 'https']),
            'audit_required': any(term in text for term in ['audit', 'logging', 'compliance']),
            'compliance_standards': self._extract_compliance_standards(text),
            'data_sensitivity': self._assess_data_sensitivity(text),
            'security_level': requirements.get('security_level', 'standard')
        }
    
    def _extract_compliance_standards(self, text: str) -> List[str]:
        """Extract compliance standards from text"""
        
        standards = []
        compliance_patterns = {
            'GDPR': r'\b(gdpr|general data protection regulation)\b',
            'HIPAA': r'\b(hipaa|health insurance portability)\b',
            'PCI-DSS': r'\b(pci|payment card industry|pci-dss)\b',
            'SOC2': r'\b(soc2|soc 2|service organization control)\b',
            'ISO27001': r'\b(iso 27001|iso27001)\b'
        }
        
        for standard, pattern in compliance_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                standards.append(standard)
        
        return standards
    
    def _assess_data_sensitivity(self, text: str) -> str:
        """Assess data sensitivity level"""
        
        high_sensitivity_indicators = ['personal', 'financial', 'medical', 'credit card', 'ssn', 'pii']
        medium_sensitivity_indicators = ['user data', 'email', 'phone', 'address']
        
        if any(indicator in text for indicator in high_sensitivity_indicators):
            return 'high'
        elif any(indicator in text for indicator in medium_sensitivity_indicators):
            return 'medium'
        else:
            return 'low'
    
    def _extract_security_features(self, component: Dict) -> Dict[str, Any]:
        """Extract security features from component"""
        
        text = str(component).lower()
        
        return {
            'has_authentication': any(term in text for term in ['authentication', 'login', 'oauth', 'jwt']),
            'has_authorization': any(term in text for term in ['authorization', 'rbac', 'permissions']),
            'has_encryption': any(term in text for term in ['encryption', 'ssl', 'tls', 'aes']),
            'has_audit_logging': any(term in text for term in ['audit', 'logging', 'trail']),
            'has_input_validation': any(term in text for term in ['validation', 'sanitization', 'xss']),
            'has_security_headers': any(term in text for term in ['csrf', 'cors', 'csp']),
            'vulnerability_scanning': any(term in text for term in ['security scan', 'vulnerability', 'penetration']),
            'compliance_certifications': self._extract_certifications(text)
        }
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract security certifications"""
        
        certifications = []
        cert_patterns = ['soc2', 'iso27001', 'pci compliant', 'hipaa compliant', 'gdpr compliant']
        
        for pattern in cert_patterns:
            if pattern in text:
                certifications.append(pattern.upper())
        
        return certifications
    
    def _check_authentication_compliance(self, features: Dict, requirements: Dict) -> Dict[str, Any]:
        """Check authentication compliance"""
        
        required = requirements.get('authentication_required', False)
        available = features.get('has_authentication', False)
        
        if not required:
            return {'score': 1.0, 'status': 'not_required', 'compliant': True}
        
        score = 1.0 if available else 0.0
        
        return {
            'score': score,
            'required': required,
            'available': available,
            'compliant': available,
            'status': 'compliant' if available else 'non_compliant'
        }
    
    def _check_authorization_compliance(self, features: Dict, requirements: Dict) -> Dict[str, Any]:
        """Check authorization compliance"""
        
        required = requirements.get('authorization_required', False)
        available = features.get('has_authorization', False)
        
        if not required:
            return {'score': 1.0, 'status': 'not_required', 'compliant': True}
        
        score = 1.0 if available else 0.0
        
        return {
            'score': score,
            'required': required,
            'available': available,
            'compliant': available,
            'status': 'compliant' if available else 'non_compliant'
        }
    
    def _check_encryption_compliance(self, features: Dict, requirements: Dict) -> Dict[str, Any]:
        """Check encryption compliance"""
        
        required = requirements.get('encryption_required', False)
        available = features.get('has_encryption', False)
        
        if not required:
            return {'score': 0.8, 'status': 'recommended', 'compliant': True}
        
        score = 1.0 if available else 0.0
        
        return {
            'score': score,
            'required': required,
            'available': available,
            'compliant': available,
            'status': 'compliant' if available else 'non_compliant'
        }
    
    def _check_data_protection_compliance(self, features: Dict, requirements: Dict) -> Dict[str, Any]:
        """Check data protection compliance"""
        
        data_sensitivity = requirements.get('data_sensitivity', 'low')
        has_validation = features.get('has_input_validation', False)
        has_encryption = features.get('has_encryption', False)
        
        protection_score = 0
        if has_validation:
            protection_score += 0.5
        if has_encryption:
            protection_score += 0.5
        
        # Adjust based on data sensitivity
        if data_sensitivity == 'high' and protection_score < 1.0:
            protection_score *= 0.5
        
        return {
            'score': protection_score,
            'data_sensitivity': data_sensitivity,
            'has_validation': has_validation,
            'has_encryption': has_encryption,
            'compliant': protection_score >= 0.7,
            'status': 'compliant' if protection_score >= 0.7 else 'partial_compliance'
        }
    
    def _check_audit_compliance(self, features: Dict, requirements: Dict) -> Dict[str, Any]:
        """Check audit logging compliance"""
        
        required = requirements.get('audit_required', False)
        available = features.get('has_audit_logging', False)
        
        compliance_standards = requirements.get('compliance_standards', [])
        audit_required_for_compliance = any(std in ['SOC2', 'HIPAA', 'PCI-DSS'] for std in compliance_standards)
        
        if audit_required_for_compliance:
            required = True
        
        if not required:
            return {'score': 0.8, 'status': 'recommended', 'compliant': True}
        
        score = 1.0 if available else 0.0
        
        return {
            'score': score,
            'required': required,
            'available': available,
            'compliant': available,
            'compliance_driven': audit_required_for_compliance,
            'status': 'compliant' if available else 'non_compliant'
        }
    
    def _check_vulnerability_management(self, features: Dict, requirements: Dict) -> Dict[str, Any]:
        """Check vulnerability management"""
        
        has_scanning = features.get('vulnerability_scanning', False)
        security_level = requirements.get('security_level', 'standard')
        
        score = 1.0 if has_scanning else 0.6  # Some points for basic security
        
        if security_level == 'high' and not has_scanning:
            score = 0.3
        
        return {
            'score': score,
            'has_scanning': has_scanning,
            'security_level': security_level,
            'compliant': score >= 0.7,
            'status': 'compliant' if score >= 0.7 else 'needs_improvement'
        }
    
    def _calculate_compliance_score(self, checks: Dict[str, Dict]) -> float:
        """Calculate overall compliance score"""
        
        weights = {
            'authentication': 0.2,
            'authorization': 0.2,
            'encryption': 0.2,
            'data_protection': 0.15,
            'audit_logging': 0.15,
            'vulnerability_management': 0.1
        }
        
        total_score = sum(
            checks[category]['score'] * weights[category]
            for category in weights.keys()
            if category in checks
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _identify_security_gaps(self, checks: Dict[str, Dict]) -> List[str]:
        """Identify security gaps"""
        
        gaps = []
        
        for category, check in checks.items():
            if not check.get('compliant', True):
                gaps.append(f"Non-compliant {category.replace('_', ' ')}")
            elif check.get('score', 1.0) < 0.7:
                gaps.append(f"Weak {category.replace('_', ' ')}")
        
        return gaps
    
    def _determine_compliance_level(self, score: float) -> str:
        """Determine compliance level"""
        
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'good'
        elif score >= 0.6:
            return 'acceptable'
        elif score >= 0.4:
            return 'poor'
        else:
            return 'non_compliant'
    
    def _suggest_remediation_actions(self, checks: Dict[str, Dict]) -> List[str]:
        """Suggest remediation actions"""
        
        actions = []
        
        for category, check in checks.items():
            if not check.get('compliant', True):
                if category == 'authentication':
                    actions.append('Implement robust authentication mechanism (OAuth2/JWT)')
                elif category == 'authorization':
                    actions.append('Add role-based access control (RBAC)')
                elif category == 'encryption':
                    actions.append('Enable TLS/SSL encryption for data in transit')
                elif category == 'data_protection':
                    actions.append('Implement input validation and data sanitization')
                elif category == 'audit_logging':
                    actions.append('Enable comprehensive audit logging')
                elif category == 'vulnerability_management':
                    actions.append('Implement regular vulnerability scanning')
        
        if not actions:
            actions.append('Security compliance looks good - maintain current practices')
        
        return actions
    
    def _build_security_frameworks(self) -> Dict[str, Dict]:
        """Build security frameworks mapping"""
        
        return {
            'OWASP': {
                'injection': 'Input validation and parameterized queries',
                'broken_authentication': 'Strong authentication mechanisms',
                'sensitive_data_exposure': 'Proper encryption and data protection',
                'xml_external_entities': 'Disable XML external entity processing',
                'broken_access_control': 'Implement proper authorization',
                'security_misconfiguration': 'Secure configuration management',
                'cross_site_scripting': 'Input validation and output encoding',
                'insecure_deserialization': 'Secure deserialization practices',
                'components_with_vulnerabilities': 'Regular security updates',
                'insufficient_logging': 'Comprehensive audit logging'
            }
        }
    
    def _build_compliance_standards(self) -> Dict[str, Dict]:
        """Build compliance standards requirements"""
        
        return {
            'GDPR': {
                'data_protection': True,
                'consent_management': True,
                'right_to_erasure': True,
                'data_portability': True,
                'breach_notification': True
            },
            'HIPAA': {
                'access_control': True,
                'audit_controls': True,
                'integrity': True,
                'person_authentication': True,
                'transmission_security': True
            },
            'PCI-DSS': {
                'firewall_configuration': True,
                'default_passwords': False,
                'cardholder_data_protection': True,
                'encrypted_transmission': True,
                'antivirus_software': True,
                'secure_systems': True,
                'access_control': True,
                'unique_ids': True,
                'physical_access': True,
                'network_monitoring': True,
                'security_testing': True,
                'information_security_policy': True
            }
        }
