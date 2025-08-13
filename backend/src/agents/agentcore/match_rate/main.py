"""
Solution matching and scoring agent
AgentCore-compatible wrapper
Size: < 6.5KB
"""
import json
from typing import Any, Dict


class MatchRateAgent:
    """AgentCore wrapper for Match Rate Agent"""

    def __init__(self):
        self.name = "match_rate"
        self.version = "1.0.0"
        self.description = "Solution matching and scoring agent"
        self._initialized = True

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method"""
        try:
            # Validate input
            validation = self.validate_input(request)
            if not validation["valid"]:
                return {"status": "error", "error": validation["error"]}

            # Process request based on agent type
            result = self._execute_logic(request)

            return {"status": "success", "agent": self.name, "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def validate_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input request"""
        if not request:
            return {"valid": False, "error": "Empty request"}

        if "input" not in request:
            return {"valid": False, "error": "Missing input field"}

        return {"valid": True}

    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self._get_capabilities(),
            "constraints": {"max_memory_kb": 6.5, "max_instantiation_us": 3.0},
        }

    def _execute_logic(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific logic"""
        # Match Rate processing logic
        query = request.get("query", {})
        candidates = request.get("candidates", [])

        # Calculate similarity scores
        scores = self._calculate_similarity(query, candidates)

        # Assess quality
        quality = self._assess_quality(candidates, scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(scores, quality)

        return {
            "scores": scores,
            "quality_metrics": quality,
            "recommendations": recommendations,
            "best_match": self._find_best_match(scores),
        }

    def _calculate_similarity(self, query: dict, candidates: list) -> list:
        """Calculate similarity scores"""
        scores = []

        for candidate in candidates:
            score = 0.0

            # Feature matching
            for feature in query.get("features", []):
                if feature in candidate.get("features", []):
                    score += 0.2

            # Technology matching
            for tech in query.get("technologies", []):
                if tech in candidate.get("technologies", []):
                    score += 0.15

            # Constraint matching
            if query.get("budget") and candidate.get("cost"):
                if candidate["cost"] <= query["budget"]:
                    score += 0.3

            scores.append(
                {"candidate_id": candidate.get("id"), "score": min(score, 1.0), "confidence": 0.85}
            )

        return sorted(scores, key=lambda x: x["score"], reverse=True)

    def _assess_quality(self, candidates: list, scores: list) -> dict:
        """Assess solution quality"""
        return {
            "average_score": sum(s["score"] for s in scores) / len(scores) if scores else 0,
            "top_match_score": scores[0]["score"] if scores else 0,
            "match_count": len([s for s in scores if s["score"] > 0.7]),
            "quality_rating": "high" if scores and scores[0]["score"] > 0.8 else "medium",
        }

    def _generate_recommendations(self, scores: list, quality: dict) -> list:
        """Generate match recommendations"""
        recommendations = []

        if quality["average_score"] < 0.5:
            recommendations.append("Consider expanding search criteria")

        if quality["match_count"] == 0:
            recommendations.append("No high-quality matches found - review requirements")

        if quality["top_match_score"] > 0.9:
            recommendations.append("Excellent match found - proceed with implementation")

        return recommendations

    def _find_best_match(self, scores: list) -> dict:
        """Find the best matching solution"""
        if not scores:
            return {"candidate_id": None, "score": 0}
        return scores[0]

    def _get_capabilities(self) -> list:
        """Get agent capabilities"""
        return ["similarity_calculation", "quality_assessment", "recommendation_engine"]


# AgentCore entry point
def handler(event, context):
    """AWS Lambda handler"""
    agent = MatchRateAgent()
    return agent.process(event)
