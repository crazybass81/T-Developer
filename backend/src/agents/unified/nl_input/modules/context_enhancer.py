"""
Context Enhancer Module
Enhances user input with additional context
"""

from typing import Dict, Any
import re


class ContextEnhancer:
    """Enhances natural language input with contextual information"""
    
    def __init__(self):
        self.enhancement_patterns = {
            'implicit_features': {
                'login system': ['authentication', 'user management', 'session handling'],
                'shopping cart': ['product catalog', 'inventory', 'checkout process'],
                'blog platform': ['content management', 'comments', 'categories', 'tags'],
                'chat application': ['real-time messaging', 'user presence', 'notifications'],
                'dashboard': ['data visualization', 'analytics', 'reporting']
            },
            'technical_implications': {
                'real-time': ['websockets', 'event-driven architecture'],
                'e-commerce': ['payment processing', 'order management', 'inventory'],
                'social': ['user profiles', 'friend connections', 'activity feeds'],
                'mobile-friendly': ['responsive design', 'touch optimization', 'offline capability']
            }
        }
    
    async def enhance(self, text: str, context: Dict[str, Any]) -> str:
        """
        Enhance the input text with additional context
        
        Args:
            text: Original user input
            context: Additional context dictionary
            
        Returns:
            Enhanced text with contextual information
        """
        enhanced = text
        
        # Add user preferences from context
        if context.get('previous_projects'):
            enhanced += f" Based on previous projects: {context['previous_projects']}."
        
        if context.get('tech_stack_preference'):
            enhanced += f" Preferred technology: {context['tech_stack_preference']}."
        
        if context.get('target_audience'):
            enhanced += f" Target audience: {context['target_audience']}."
        
        # Add implicit features based on keywords
        text_lower = text.lower()
        for keyword, implications in self.enhancement_patterns['implicit_features'].items():
            if keyword in text_lower:
                enhanced += f" This implies: {', '.join(implications)}."
        
        # Add technical implications
        for keyword, implications in self.enhancement_patterns['technical_implications'].items():
            if keyword in text_lower:
                enhanced += f" Technical requirements: {', '.join(implications)}."
        
        # Add common patterns
        if 'crud' in text_lower or 'admin' in text_lower:
            enhanced += " This requires Create, Read, Update, Delete operations."
        
        if 'api' in text_lower:
            enhanced += " This requires RESTful or GraphQL API design."
        
        if 'secure' in text_lower or 'security' in text_lower:
            enhanced += " This requires authentication, authorization, and data encryption."
        
        return enhanced
    
    def extract_domain_context(self, text: str) -> Dict[str, Any]:
        """Extract domain-specific context from text"""
        domains = {
            'healthcare': ['patient', 'medical', 'health', 'doctor', 'clinic'],
            'finance': ['payment', 'transaction', 'banking', 'investment', 'financial'],
            'education': ['student', 'teacher', 'course', 'learning', 'education'],
            'retail': ['product', 'shopping', 'cart', 'order', 'inventory'],
            'social': ['friend', 'post', 'share', 'like', 'comment', 'follow']
        }
        
        text_lower = text.lower()
        detected_domains = []
        
        for domain, keywords in domains.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_domains.append(domain)
        
        return {
            'domains': detected_domains,
            'is_specialized': len(detected_domains) > 0,
            'requires_compliance': 'healthcare' in detected_domains or 'finance' in detected_domains
        }