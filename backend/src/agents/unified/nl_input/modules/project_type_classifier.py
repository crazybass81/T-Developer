"""
Project Type Classifier Module
Classifies projects into specific categories
"""

from typing import Any, Dict, List


class ProjectTypeClassifier:
    """Classifies project types based on content analysis"""

    def __init__(self):
        self.project_patterns = {
            "todo": {
                "keywords": ["todo", "task", "checklist", "productivity"],
                "features": ["task_management", "reminders", "categories"],
                "confidence_boost": 0.3,
            },
            "blog": {
                "keywords": ["blog", "article", "post", "content", "writing"],
                "features": ["content_editor", "publishing", "comments"],
                "confidence_boost": 0.3,
            },
            "ecommerce": {
                "keywords": ["shop", "store", "product", "cart", "payment"],
                "features": ["product_catalog", "shopping_cart", "checkout"],
                "confidence_boost": 0.4,
            },
            "dashboard": {
                "keywords": ["dashboard", "analytics", "metrics", "monitoring"],
                "features": ["data_visualization", "reporting", "charts"],
                "confidence_boost": 0.3,
            },
            "chat": {
                "keywords": ["chat", "messaging", "conversation", "communication"],
                "features": ["real_time_messaging", "user_presence", "channels"],
                "confidence_boost": 0.35,
            },
            "portfolio": {
                "keywords": ["portfolio", "showcase", "gallery", "resume"],
                "features": ["project_gallery", "about_section", "contact"],
                "confidence_boost": 0.3,
            },
            "social": {
                "keywords": ["social", "network", "community", "friends"],
                "features": ["user_profiles", "connections", "feed"],
                "confidence_boost": 0.35,
            },
            "saas": {
                "keywords": ["saas", "subscription", "service", "platform"],
                "features": ["user_management", "billing", "multi_tenancy"],
                "confidence_boost": 0.4,
            },
            "game": {
                "keywords": ["game", "play", "score", "level"],
                "features": ["game_mechanics", "scoring", "leaderboard"],
                "confidence_boost": 0.35,
            },
            "education": {
                "keywords": ["education", "learning", "course", "tutorial"],
                "features": ["course_management", "progress_tracking", "quizzes"],
                "confidence_boost": 0.3,
            },
        }

    async def classify(self, text: str, entities: Dict[str, Any]) -> str:
        """
        Classify the project type

        Args:
            text: Project description
            entities: Extracted entities

        Returns:
            Project type string
        """
        text_lower = text.lower()
        scores = {}

        for project_type, pattern in self.project_patterns.items():
            score = 0.0

            # Check keywords
            for keyword in pattern["keywords"]:
                if keyword in text_lower:
                    score += 0.2

            # Check for feature mentions
            for feature in pattern["features"]:
                feature_words = feature.replace("_", " ")
                if feature_words in text_lower:
                    score += 0.3

            # Check entities
            if entities:
                entity_types = entities.get("types", [])
                if project_type in entity_types:
                    score += pattern["confidence_boost"]

            if score > 0:
                scores[project_type] = score

        if scores:
            # Return the type with highest score
            return max(scores, key=scores.get)

        # Default to web application
        return "web_application"

    def get_project_characteristics(self, project_type: str) -> Dict[str, Any]:
        """Get characteristics of a project type"""
        characteristics = {
            "todo": {
                "complexity": "simple",
                "typical_features": ["task_crud", "categories", "priorities"],
                "recommended_stack": "react",
                "database_needed": True,
            },
            "blog": {
                "complexity": "medium",
                "typical_features": ["content_management", "comments", "tags"],
                "recommended_stack": "nextjs",
                "database_needed": True,
            },
            "ecommerce": {
                "complexity": "complex",
                "typical_features": ["product_catalog", "cart", "payments"],
                "recommended_stack": "nextjs",
                "database_needed": True,
            },
            "dashboard": {
                "complexity": "medium",
                "typical_features": ["charts", "metrics", "reports"],
                "recommended_stack": "react",
                "database_needed": True,
            },
            "chat": {
                "complexity": "complex",
                "typical_features": ["real_time", "messaging", "notifications"],
                "recommended_stack": "react",
                "database_needed": True,
            },
        }

        return characteristics.get(
            project_type,
            {
                "complexity": "medium",
                "typical_features": [],
                "recommended_stack": "react",
                "database_needed": False,
            },
        )
