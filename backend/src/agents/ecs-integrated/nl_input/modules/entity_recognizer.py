"""
Entity Recognizer Module
Recognizes and extracts named entities from text
"""

from typing import Dict, Any, List
import re

class EntityRecognizer:
    """Extracts entities like pages, components, actions from description"""
    
    def __init__(self):
        self.entity_patterns = {
            "pages": [
                r"(\w+)\s+page",
                r"page\s+(?:for|of)\s+(\w+)",
                r"(\w+)\s+screen",
                r"(\w+)\s+view"
            ],
            "components": [
                r"(\w+)\s+component",
                r"(\w+)\s+widget",
                r"(\w+)\s+element",
                r"(\w+)\s+section"
            ],
            "actions": [
                r"(create|add|insert)\s+\w+",
                r"(update|edit|modify)\s+\w+",
                r"(delete|remove)\s+\w+",
                r"(view|display|show)\s+\w+",
                r"(search|filter|sort)\s+\w+",
                r"(upload|download)\s+\w+"
            ],
            "data_models": [
                r"(\w+)\s+model",
                r"(\w+)\s+entity",
                r"(\w+)\s+table",
                r"(\w+)\s+schema",
                r"(\w+)\s+data"
            ],
            "apis": [
                r"(\w+)\s+api",
                r"(\w+)\s+endpoint",
                r"(\w+)\s+service",
                r"(\w+)\s+webhook"
            ],
            "features": [
                r"(\w+)\s+feature",
                r"(\w+)\s+functionality",
                r"(\w+)\s+capability",
                r"(\w+)\s+module"
            ]
        }
        
        self.common_entities = {
            "pages": ["home", "login", "signup", "dashboard", "profile", "settings", "about", "contact"],
            "components": ["header", "footer", "navbar", "sidebar", "modal", "form", "table", "card"],
            "data_models": ["user", "product", "order", "payment", "category", "post", "comment"],
            "actions": ["login", "logout", "register", "search", "filter", "sort", "export", "import"]
        }
    
    async def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities by type
        """
        
        entities = {
            "pages": [],
            "components": [],
            "actions": [],
            "data_models": [],
            "apis": [],
            "features": []
        }
        
        text_lower = text.lower()
        
        # Extract using patterns
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    entity = match if isinstance(match, str) else match[0]
                    if entity and len(entity) > 2:  # Filter out short matches
                        entities[entity_type].append(entity)
        
        # Add common entities if mentioned
        for entity_type, common_list in self.common_entities.items():
            for common in common_list:
                if common in text_lower and common not in entities.get(entity_type, []):
                    entities[entity_type].append(common)
        
        # Clean and deduplicate
        for entity_type in entities:
            entities[entity_type] = list(dict.fromkeys([
                e.strip().title() for e in entities[entity_type]
                if e and not e.strip().lower() in ['the', 'a', 'an', 'and', 'or']
            ]))
        
        return entities