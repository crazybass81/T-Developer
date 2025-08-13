"""🧬 T-Developer Recommendation Search <6.5KB"""
import math
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple


class RecommendationSearch:
    """Ultra-lightweight recommendation engine"""

    def __init__(self):
        self.algorithms = {
            "collaborative": self._collaborative,
            "content": self._content_based,
            "popularity": self._popularity,
            "contextual": self._contextual,
        }

        self.weights = {"collaborative": 0.3, "content": 0.3, "popularity": 0.2, "contextual": 0.2}
        self.component_scores = defaultdict(float)
        self.user_patterns = defaultdict(list)

    async def search(self, query: Dict, requirements: Dict) -> List[Dict]:
        """Generate recommendations"""
        context = self._extract_context(query, requirements)
        recommendations = []

        for algo_name, algo_func in self.algorithms.items():
            results = algo_func(context)
            weight = self.weights[algo_name]

            for result in results:
                result["score"] *= weight
                recommendations.append(result)

        # Merge and rank
        merged = self._merge_recommendations(recommendations)
        return sorted(merged, key=lambda x: x["score"], reverse=True)[:10]

    def _extract_context(self, query: Dict, requirements: Dict) -> Dict:
        """Extract recommendation context"""
        return {
            "framework": query.get("framework", ""),
            "category": query.get("category", ""),
            "features": requirements.get("features", []),
            "constraints": requirements.get("constraints", {}),
            "user_type": query.get("user_type", "beginner"),
        }

    def _collaborative(self, context: Dict) -> List[Dict]:
        """Collaborative filtering recommendations"""
        framework = context["framework"]
        user_type = context["user_type"]

        # Collaborative filtering data
        base = {
            "react": [
                ("react-router", 0.9, "routing"),
                ("styled-components", 0.8, "styling"),
                ("axios", 0.85, "http"),
            ],
            "vue": [
                ("vue-router", 0.9, "routing"),
                ("vuetify", 0.8, "ui"),
                ("axios", 0.85, "http"),
            ],
            "express": [
                ("cors", 0.9, "middleware"),
                ("helmet", 0.85, "security"),
                ("morgan", 0.8, "logging"),
            ],
        }
        components = base.get(framework, [])
        return [{"name": name, "score": score, "type": typ} for name, score, typ in components]

    def _content_based(self, context: Dict) -> List[Dict]:
        """Content-based filtering"""
        features = context["features"]
        fmap = {
            "authentication": ("passport", 0.9, "auth"),
            "database": ("sequelize", 0.85, "orm"),
            "ui": ("material-ui", 0.8, "ui"),
            "testing": ("jest", 0.9, "testing"),
            "state": ("redux", 0.85, "state"),
            "routing": ("react-router", 0.9, "routing"),
        }

        return [
            {"name": name, "score": score, "type": typ}
            for feature in features
            if feature in fmap
            for name, score, typ in [fmap[feature]]
        ]

    def _popularity(self, context: Dict) -> List[Dict]:
        """Popularity-based recommendations"""
        fw = context["framework"]
        pop = {
            "react": [
                ("lodash", 0.95, "utility"),
                ("moment", 0.8, "date"),
                ("react-hook-form", 0.85, "forms"),
            ],
            "express": [
                ("body-parser", 0.9, "middleware"),
                ("express-validator", 0.8, "validation"),
                ("nodemon", 0.75, "dev"),
            ],
        }
        return [{"name": n, "score": s, "type": t} for n, s, t in pop.get(fw, [])]

    def _contextual(self, context: Dict) -> List[Dict]:
        """Contextual recommendations"""
        user_type = context["user_type"]
        constraints = context["constraints"]

        if user_type == "beginner":
            return [
                {"name": "create-react-app", "score": 0.9, "type": "starter"},
                {"name": "bootstrap", "score": 0.8, "type": "ui"},
            ]
        elif constraints.get("performance", False):
            return [
                {"name": "react-memo", "score": 0.85, "type": "optimization"},
                {"name": "compression", "score": 0.8, "type": "middleware"},
            ]

        return []

    def _merge_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Merge duplicate recommendations"""
        merged = {}

        for rec in recommendations:
            name = rec["name"]
            if name in merged:
                merged[name]["score"] += rec["score"]
            else:
                merged[name] = rec.copy()

        return list(merged.values())

    def update_user_pattern(self, user_id: str, component: str, action: str):
        """Update user behavior pattern"""
        self.user_patterns[user_id].append(
            {
                "component": component,
                "action": action,
                "timestamp": math.floor(1000000),  # Simplified timestamp
            }
        )

    def get_trending_components(self, framework: str = None) -> List[Dict]:
        """Get trending components"""
        trending = [
            {"name": "typescript", "score": 0.95, "growth": 0.15},
            {"name": "tailwindcss", "score": 0.9, "growth": 0.25},
            {"name": "next.js", "score": 0.85, "growth": 0.12},
        ]

        if framework:
            # Filter by framework in real implementation
            pass

        return trending[:5]

    def recommend_similar(self, component_name: str) -> List[str]:
        """Find similar components"""
        similar_map = {
            "react": ["preact", "vue"],
            "angular": ["react", "vue"],
            "express": ["koa", "fastify"],
            "mongoose": ["sequelize", "prisma"],
            "jest": ["mocha", "cypress"],
        }

        return similar_map.get(component_name, [])


def search_recommendations(query: Dict, requirements: Dict) -> List[Dict]:
    """Quick recommendation search"""
    engine = RecommendationSearch()
    import asyncio

    return asyncio.run(engine.search(query, requirements))


def get_popular_components(framework: str) -> List[Dict]:
    """Get popular components for framework"""
    engine = RecommendationSearch()
    context = {
        "framework": framework,
        "features": [],
        "constraints": {},
        "user_type": "intermediate",
    }
    return engine._popularity(context)
