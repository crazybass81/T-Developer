"""
Requirement Validator Module
Validates extracted requirements for completeness and consistency
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of requirement validation"""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]

class RequirementValidator:
    """Validates project requirements for completeness and consistency"""
    
    def __init__(self):
        self.required_fields = {
            "web_app": ["functional_requirements", "technology_preferences"],
            "mobile_app": ["functional_requirements", "technology_preferences", "target_users"],
            "api": ["functional_requirements", "technical_requirements"],
            "e_commerce": ["functional_requirements", "payment", "technology_preferences"],
            "saas": ["functional_requirements", "subscription", "multi_tenancy"]
        }
        
        self.minimum_requirements = {
            "functional": 3,
            "non_functional": 2,
            "technical": 1
        }
    
    async def validate(self, requirements: Any) -> ValidationResult:
        """
        Validate project requirements
        
        Args:
            requirements: ProjectRequirements object
            
        Returns:
            ValidationResult with issues and suggestions
        """
        
        issues = []
        warnings = []
        suggestions = []
        
        # Check for minimum requirements
        if len(requirements.functional_requirements) < self.minimum_requirements["functional"]:
            warnings.append(f"Only {len(requirements.functional_requirements)} functional requirements found (minimum: {self.minimum_requirements['functional']})")
            suggestions.append("Consider adding more specific functional requirements")
        
        if len(requirements.non_functional_requirements) < self.minimum_requirements["non_functional"]:
            warnings.append(f"Only {len(requirements.non_functional_requirements)} non-functional requirements found")
            suggestions.append("Add performance, security, or usability requirements")
        
        # Check for project name
        if not requirements.project_name:
            warnings.append("No project name specified")
            suggestions.append("Provide a descriptive project name")
        
        # Check for technology preferences
        if not requirements.technology_preferences:
            warnings.append("No technology preferences specified")
            suggestions.append("Specify preferred technologies or let the system recommend")
        
        # Check for conflicting requirements
        conflicts = self._check_conflicts(requirements)
        if conflicts:
            issues.extend(conflicts)
        
        # Check completeness for project type
        completeness_issues = self._check_completeness(requirements)
        if completeness_issues:
            warnings.extend(completeness_issues)
        
        # Determine overall validity
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _check_conflicts(self, requirements: Any) -> List[str]:
        """Check for conflicting requirements"""
        
        conflicts = []
        
        # Check technology conflicts
        tech_prefs = requirements.technology_preferences
        if isinstance(tech_prefs, dict):
            if tech_prefs.get("frontend") == ["Angular"] and tech_prefs.get("backend") == ["PHP"]:
                conflicts.append("Angular and PHP are not commonly used together")
            
            if tech_prefs.get("database") == ["MongoDB"] and "ACID compliance" in str(requirements.non_functional_requirements):
                conflicts.append("MongoDB may not provide full ACID compliance")
        
        # Check scalability vs simplicity conflicts
        if "serverless" in str(requirements.technical_requirements) and "stateful" in str(requirements.functional_requirements):
            conflicts.append("Serverless architecture conflicts with stateful requirements")
        
        return conflicts
    
    def _check_completeness(self, requirements: Any) -> List[str]:
        """Check completeness based on project type"""
        
        issues = []
        project_type = requirements.project_type
        
        # Check project-specific requirements
        if project_type == "e_commerce":
            if not any("payment" in req.lower() for req in requirements.functional_requirements):
                issues.append("E-commerce project missing payment processing requirement")
            if not any("cart" in req.lower() for req in requirements.functional_requirements):
                issues.append("E-commerce project missing shopping cart requirement")
        
        elif project_type == "saas":
            if not any("subscription" in req.lower() or "billing" in req.lower() 
                      for req in requirements.functional_requirements):
                issues.append("SaaS project missing subscription/billing requirement")
            if not any("tenant" in req.lower() for req in requirements.technical_requirements):
                issues.append("SaaS project missing multi-tenancy requirement")
        
        elif project_type == "mobile_app":
            if not requirements.target_users:
                issues.append("Mobile app missing target user definition")
            if not any("offline" in req.lower() or "sync" in req.lower() 
                      for req in requirements.non_functional_requirements):
                issues.append("Mobile app should consider offline functionality")
        
        return issues