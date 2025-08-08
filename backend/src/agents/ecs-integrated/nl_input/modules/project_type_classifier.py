"""
Project Type Classifier Module
Classifies project into predefined categories
"""

from typing import Dict, Any, List, Optional
import re

class ProjectTypeClassifier:
    """Classifies projects into specific types based on description and entities"""
    
    def __init__(self):
        self.project_types = {
            "web_app": {
                "keywords": ["website", "web app", "web application", "portal", "online platform"],
                "patterns": [r"web\s*(site|app|application)", r"online\s+\w+", r"browser.*based"],
                "weight": 1.0
            },
            "mobile_app": {
                "keywords": ["mobile app", "ios", "android", "smartphone", "tablet app"],
                "patterns": [r"(ios|android)\s*app", r"mobile\s*application", r"native\s*app"],
                "weight": 1.2
            },
            "desktop_app": {
                "keywords": ["desktop", "windows app", "mac app", "linux app", "electron"],
                "patterns": [r"desktop\s*app", r"(windows|mac|linux)\s*application"],
                "weight": 1.1
            },
            "api": {
                "keywords": ["api", "rest api", "graphql", "backend service", "microservice"],
                "patterns": [r"(rest|graphql)\s*api", r"backend\s*service", r"micro\s*service"],
                "weight": 1.0
            },
            "cli_tool": {
                "keywords": ["cli", "command line", "terminal", "console app", "script"],
                "patterns": [r"command\s*line", r"cli\s*tool", r"terminal\s*app"],
                "weight": 0.9
            },
            "saas": {
                "keywords": ["saas", "software as a service", "cloud platform", "subscription service"],
                "patterns": [r"saas\s*platform", r"cloud\s*service", r"subscription\s*based"],
                "weight": 1.3
            },
            "e_commerce": {
                "keywords": ["e-commerce", "online store", "shop", "marketplace", "shopping cart"],
                "patterns": [r"e[\s-]*commerce", r"online\s*(store|shop)", r"market\s*place"],
                "weight": 1.2
            },
            "game": {
                "keywords": ["game", "gaming", "multiplayer", "single player", "arcade"],
                "patterns": [r"video\s*game", r"(multi|single)\s*player", r"gaming\s*app"],
                "weight": 1.0
            },
            "ai_ml": {
                "keywords": ["ai", "machine learning", "ml model", "neural network", "deep learning"],
                "patterns": [r"(ai|ml)\s*model", r"machine\s*learning", r"neural\s*network"],
                "weight": 1.4
            },
            "iot": {
                "keywords": ["iot", "internet of things", "smart device", "sensor", "embedded"],
                "patterns": [r"iot\s*device", r"smart\s*\w+", r"sensor\s*network"],
                "weight": 1.1
            },
            "blockchain": {
                "keywords": ["blockchain", "dapp", "smart contract", "crypto", "web3"],
                "patterns": [r"block\s*chain", r"smart\s*contract", r"d\s*app"],
                "weight": 1.3
            },
            "data_pipeline": {
                "keywords": ["etl", "data pipeline", "data processing", "analytics", "big data"],
                "patterns": [r"etl\s*pipeline", r"data\s*processing", r"analytics\s*platform"],
                "weight": 1.2
            }
        }
        
        # Secondary indicators for refinement
        self.refinement_indicators = {
            "admin_panel": ["admin", "management", "dashboard", "control panel"],
            "marketplace": ["marketplace", "vendors", "sellers", "multi-vendor"],
            "social_platform": ["social", "network", "community", "forum", "chat"],
            "educational": ["learning", "course", "tutorial", "education", "training"],
            "healthcare": ["medical", "health", "patient", "clinic", "hospital"],
            "finance": ["banking", "finance", "trading", "investment", "payment"]
        }
    
    async def classify(
        self,
        description: str,
        entities: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Classify project type based on description and entities
        
        Args:
            description: Project description
            entities: Extracted entities from description
            
        Returns:
            Project type identifier
        """
        
        scores = await self._calculate_scores(description, entities)
        
        if not scores:
            return "web_app"  # Default fallback
        
        # Get the highest scoring type
        best_type = max(scores.items(), key=lambda x: x[1])
        
        # Refine with secondary indicators
        refined_type = await self._refine_classification(best_type[0], description)
        
        return refined_type
    
    async def _calculate_scores(
        self,
        description: str,
        entities: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate confidence scores for each project type"""
        
        scores = {}
        description_lower = description.lower()
        
        for project_type, config in self.project_types.items():
            score = 0.0
            
            # Check keywords
            keyword_matches = sum(
                1 for keyword in config["keywords"]
                if keyword in description_lower
            )
            score += keyword_matches * 2.0
            
            # Check patterns
            pattern_matches = sum(
                1 for pattern in config["patterns"]
                if re.search(pattern, description_lower, re.IGNORECASE)
            )
            score += pattern_matches * 3.0
            
            # Entity bonus
            if entities:
                score += self._entity_bonus(project_type, entities)
            
            # Apply weight
            score *= config["weight"]
            
            if score > 0:
                scores[project_type] = score
        
        return scores
    
    def _entity_bonus(self, project_type: str, entities: Dict[str, Any]) -> float:
        """Calculate bonus score based on extracted entities"""
        
        bonus = 0.0
        
        # Check for relevant entities
        if project_type == "web_app" and entities.get("pages"):
            bonus += len(entities["pages"]) * 0.5
        
        elif project_type == "mobile_app" and entities.get("screens"):
            bonus += len(entities["screens"]) * 0.5
        
        elif project_type == "api" and entities.get("endpoints"):
            bonus += len(entities["endpoints"]) * 0.5
        
        elif project_type == "e_commerce" and entities.get("products"):
            bonus += 2.0
        
        elif project_type == "game" and entities.get("game_mechanics"):
            bonus += 2.0
        
        return bonus
    
    async def _refine_classification(self, base_type: str, description: str) -> str:
        """Refine classification with secondary indicators"""
        
        description_lower = description.lower()
        
        # Check for specialized subtypes
        if base_type == "web_app":
            # Check if it's actually an e-commerce site
            if any(word in description_lower for word in ["shop", "store", "product", "cart"]):
                return "e_commerce"
            
            # Check if it's a SaaS platform
            if any(word in description_lower for word in ["subscription", "multi-tenant", "saas"]):
                return "saas"
            
            # Check for admin panel
            if any(word in description_lower for word in self.refinement_indicators["admin_panel"]):
                return "admin_dashboard"
        
        elif base_type == "mobile_app":
            # Check if it's a game
            if any(word in description_lower for word in ["game", "play", "score", "level"]):
                return "mobile_game"
        
        return base_type
    
    def get_project_characteristics(self, project_type: str) -> Dict[str, Any]:
        """Get characteristics of a project type"""
        
        characteristics = {
            "web_app": {
                "platform": "web",
                "deployment": "cloud/server",
                "ui_type": "responsive",
                "typical_stack": ["React", "Node.js", "PostgreSQL"],
                "scalability": "horizontal"
            },
            "mobile_app": {
                "platform": "mobile",
                "deployment": "app_store",
                "ui_type": "native/hybrid",
                "typical_stack": ["React Native", "Flutter", "Firebase"],
                "scalability": "backend_dependent"
            },
            "api": {
                "platform": "backend",
                "deployment": "cloud/server",
                "ui_type": "none",
                "typical_stack": ["Node.js/Python", "PostgreSQL", "Redis"],
                "scalability": "horizontal"
            },
            "e_commerce": {
                "platform": "web",
                "deployment": "cloud",
                "ui_type": "responsive",
                "typical_stack": ["Next.js", "Node.js", "PostgreSQL", "Stripe"],
                "scalability": "horizontal",
                "special_requirements": ["payment_processing", "inventory", "shipping"]
            },
            "saas": {
                "platform": "web",
                "deployment": "cloud",
                "ui_type": "responsive",
                "typical_stack": ["React", "Node.js", "PostgreSQL", "Redis"],
                "scalability": "horizontal",
                "special_requirements": ["multi_tenancy", "subscription", "billing"]
            }
        }
        
        return characteristics.get(project_type, characteristics["web_app"])