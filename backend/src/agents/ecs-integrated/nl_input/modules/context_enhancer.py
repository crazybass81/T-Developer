"""
Context Enhancer Module
Enhances input with additional context and domain knowledge
"""

from typing import Dict, Any, List, Optional
import re

class ContextEnhancer:
    """Enhances natural language input with contextual information"""
    
    def __init__(self):
        self.domain_keywords = {
            "e-commerce": ["shop", "store", "product", "cart", "checkout", "payment"],
            "social": ["post", "friend", "follow", "share", "comment", "like"],
            "education": ["course", "lesson", "student", "teacher", "quiz", "grade"],
            "healthcare": ["patient", "doctor", "appointment", "medical", "prescription"],
            "finance": ["transaction", "account", "balance", "payment", "invoice"],
            "gaming": ["player", "score", "level", "achievement", "multiplayer"],
            "productivity": ["task", "project", "deadline", "team", "workflow"],
            "content": ["article", "blog", "media", "publish", "editor", "cms"]
        }
        
        self.tech_indicators = {
            "mobile": ["ios", "android", "mobile", "app", "native", "flutter", "react native"],
            "web": ["website", "web app", "browser", "responsive", "spa", "pwa"],
            "desktop": ["desktop", "windows", "mac", "linux", "electron"],
            "api": ["api", "rest", "graphql", "microservice", "backend", "endpoint"],
            "ai": ["ai", "machine learning", "ml", "neural", "nlp", "computer vision"],
            "blockchain": ["blockchain", "crypto", "smart contract", "web3", "defi"],
            "iot": ["iot", "sensor", "device", "embedded", "arduino", "raspberry"]
        }
    
    async def enhance(self, description: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Enhance description with additional context
        
        Args:
            description: Original user description
            context: Additional context information
            
        Returns:
            Enhanced description with additional context
        """
        
        enhanced = description
        
        # Add user context if provided
        if context:
            context_info = self._format_context(context)
            if context_info:
                enhanced = f"{description}\n\nAdditional Context:\n{context_info}"
        
        # Detect and add domain context
        domain = self._detect_domain(description)
        if domain:
            enhanced = f"{enhanced}\n\nDetected Domain: {domain}"
        
        # Detect and add tech context
        tech_type = self._detect_tech_type(description)
        if tech_type:
            enhanced = f"{enhanced}\nTechnology Type: {tech_type}"
        
        # Expand abbreviations
        enhanced = self._expand_abbreviations(enhanced)
        
        # Add implicit requirements
        implicit = self._add_implicit_requirements(description, domain)
        if implicit:
            enhanced = f"{enhanced}\n\nImplicit Requirements:\n{implicit}"
        
        return enhanced
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into readable string"""
        
        formatted = []
        
        if "user_type" in context:
            formatted.append(f"User Type: {context['user_type']}")
        
        if "industry" in context:
            formatted.append(f"Industry: {context['industry']}")
        
        if "budget" in context:
            formatted.append(f"Budget: {context['budget']}")
        
        if "timeline" in context:
            formatted.append(f"Timeline: {context['timeline']}")
        
        if "team_size" in context:
            formatted.append(f"Team Size: {context['team_size']}")
        
        if "existing_stack" in context:
            formatted.append(f"Existing Stack: {', '.join(context['existing_stack'])}")
        
        return "\n".join(formatted)
    
    def _detect_domain(self, description: str) -> Optional[str]:
        """Detect the domain/industry from description"""
        
        description_lower = description.lower()
        detected_domains = []
        
        for domain, keywords in self.domain_keywords.items():
            match_count = sum(1 for keyword in keywords if keyword in description_lower)
            if match_count >= 2:  # At least 2 keywords match
                detected_domains.append((domain, match_count))
        
        if detected_domains:
            # Return domain with most matches
            detected_domains.sort(key=lambda x: x[1], reverse=True)
            return detected_domains[0][0]
        
        return None
    
    def _detect_tech_type(self, description: str) -> Optional[str]:
        """Detect technology type from description"""
        
        description_lower = description.lower()
        detected_types = []
        
        for tech_type, indicators in self.tech_indicators.items():
            for indicator in indicators:
                if indicator in description_lower:
                    detected_types.append(tech_type)
                    break
        
        return ", ".join(detected_types) if detected_types else None
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations"""
        
        abbreviations = {
            r'\bCRM\b': 'Customer Relationship Management (CRM)',
            r'\bERP\b': 'Enterprise Resource Planning (ERP)',
            r'\bCMS\b': 'Content Management System (CMS)',
            r'\bPOS\b': 'Point of Sale (POS)',
            r'\bHR\b': 'Human Resources (HR)',
            r'\bSaaS\b': 'Software as a Service (SaaS)',
            r'\bB2B\b': 'Business to Business (B2B)',
            r'\bB2C\b': 'Business to Consumer (B2C)',
            r'\bMVP\b': 'Minimum Viable Product (MVP)',
            r'\bPOC\b': 'Proof of Concept (POC)',
            r'\bUI\b': 'User Interface (UI)',
            r'\bUX\b': 'User Experience (UX)',
            r'\bAPI\b': 'Application Programming Interface (API)',
            r'\bSEO\b': 'Search Engine Optimization (SEO)',
            r'\bKPI\b': 'Key Performance Indicator (KPI)'
        }
        
        result = text
        for abbr, expansion in abbreviations.items():
            # Only expand if not already expanded
            if expansion not in result:
                result = re.sub(abbr, expansion, result, flags=re.IGNORECASE)
        
        return result
    
    def _add_implicit_requirements(self, description: str, domain: Optional[str]) -> str:
        """Add implicit requirements based on description and domain"""
        
        implicit = []
        description_lower = description.lower()
        
        # General implicit requirements
        if any(word in description_lower for word in ["user", "customer", "client"]):
            if "login" not in description_lower and "auth" not in description_lower:
                implicit.append("- User authentication and authorization")
        
        if "data" in description_lower or "information" in description_lower:
            if "backup" not in description_lower:
                implicit.append("- Data backup and recovery")
            if "security" not in description_lower:
                implicit.append("- Data security and encryption")
        
        if "payment" in description_lower or "transaction" in description_lower:
            implicit.append("- PCI compliance for payment processing")
            implicit.append("- Transaction logging and audit trail")
        
        # Domain-specific implicit requirements
        if domain == "e-commerce":
            implicit.extend([
                "- Inventory management",
                "- Order tracking",
                "- Tax calculation",
                "- Shipping integration"
            ])
        elif domain == "healthcare":
            implicit.extend([
                "- HIPAA compliance",
                "- Patient data privacy",
                "- Audit logging for compliance"
            ])
        elif domain == "finance":
            implicit.extend([
                "- Financial regulations compliance",
                "- Transaction security",
                "- Audit trail"
            ])
        elif domain == "education":
            implicit.extend([
                "- Progress tracking",
                "- Multi-user roles (student, teacher, admin)",
                "- Content management"
            ])
        
        return "\n".join(implicit) if implicit else ""