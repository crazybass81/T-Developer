"""AIEvaluator - Day 43
AI-based fitness evaluation using LLMs - Size: ~6.5KB"""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class AIEvaluator:
    """AI-based evaluation for evolution fitness - Size optimized to 6.5KB"""

    def __init__(self):
        self.evaluation_prompts = self._initialize_prompts()
        self.criteria = self._initialize_criteria()
        self.cache = {}  # Cache AI evaluations
        self.history = {}
        self.models = ["claude-3", "gpt-4", "local-llm"]  # Mock models

    def _initialize_prompts(self) -> Dict[str, str]:
        """Initialize evaluation prompts"""
        return {
            "code_quality": """Evaluate this code for quality:
            - Readability (1-10)
            - Maintainability (1-10)
            - Best practices (1-10)
            - Innovation (1-10)
            Code: {code}""",
            "evolution_potential": """Assess evolution potential:
            - Adaptability (1-10)
            - Modularity (1-10)
            - Extensibility (1-10)
            - Learning capacity (1-10)
            Code: {code}""",
            "performance_prediction": """Predict performance characteristics:
            - Speed (1-10)
            - Memory efficiency (1-10)
            - Scalability (1-10)
            - Resource usage (1-10)
            Code: {code}""",
            "security_assessment": """Assess security:
            - Vulnerability resistance (1-10)
            - Input validation (1-10)
            - Data protection (1-10)
            - Access control (1-10)
            Code: {code}""",
            "business_value": """Evaluate business value:
            - Problem solving (1-10)
            - User experience (1-10)
            - Cost effectiveness (1-10)
            - Innovation level (1-10)
            Code: {code}""",
        }

    def _initialize_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Initialize evaluation criteria"""
        return {
            "code_quality": {
                "weight": 0.2,
                "threshold": 7.0,
                "aspects": ["readability", "maintainability", "best_practices", "innovation"],
            },
            "evolution_potential": {
                "weight": 0.25,
                "threshold": 7.5,
                "aspects": ["adaptability", "modularity", "extensibility", "learning_capacity"],
            },
            "performance_prediction": {
                "weight": 0.2,
                "threshold": 7.0,
                "aspects": ["speed", "memory_efficiency", "scalability", "resource_usage"],
            },
            "security_assessment": {
                "weight": 0.15,
                "threshold": 8.0,
                "aspects": [
                    "vulnerability_resistance",
                    "input_validation",
                    "data_protection",
                    "access_control",
                ],
            },
            "business_value": {
                "weight": 0.2,
                "threshold": 6.5,
                "aspects": [
                    "problem_solving",
                    "user_experience",
                    "cost_effectiveness",
                    "innovation_level",
                ],
            },
        }

    def evaluate(self, agent_id: str, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate agent using AI"""
        # Check cache
        code_hash = hashlib.md5(code.encode()).hexdigest()
        cache_key = f"{agent_id}_{code_hash}"

        if cache_key in self.cache:
            cached = self.cache[cache_key]
            cached["from_cache"] = True
            return cached

        evaluation = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "ai_scores": {},
            "consensus_score": 0,
            "evolution_readiness": "",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
        }

        # Evaluate each criteria
        for criteria_name, criteria_config in self.criteria.items():
            ai_score = self._get_ai_evaluation(criteria_name, code, context)
            evaluation["ai_scores"][criteria_name] = ai_score

        # Calculate consensus score
        evaluation["consensus_score"] = self._calculate_consensus(evaluation["ai_scores"])

        # Determine evolution readiness
        evaluation["evolution_readiness"] = self._assess_readiness(evaluation["consensus_score"])

        # Identify strengths and weaknesses
        evaluation["strengths"] = self._identify_strengths(evaluation["ai_scores"])
        evaluation["weaknesses"] = self._identify_weaknesses(evaluation["ai_scores"])

        # Generate recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation)

        # Cache and store
        self.cache[cache_key] = evaluation
        if agent_id not in self.history:
            self.history[agent_id] = []
        self.history[agent_id].append(evaluation)

        return evaluation

    def _get_ai_evaluation(
        self, criteria: str, code: str, context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Get AI evaluation for specific criteria"""
        # Simulate AI evaluation (in production, would call actual LLM)
        prompt = self.evaluation_prompts[criteria].format(code=code[:500])  # Truncate for demo

        # Mock AI response based on code characteristics
        scores = self._mock_ai_response(criteria, code)

        return {
            "criteria": criteria,
            "scores": scores,
            "average": sum(scores.values()) / len(scores),
            "confidence": 0.85 + (len(code) % 10) / 100,  # Mock confidence
            "model_used": self.models[0],
        }

    def _mock_ai_response(self, criteria: str, code: str) -> Dict[str, float]:
        """Mock AI response for testing"""
        # Simulate scoring based on code characteristics
        base_score = 6.0

        # Adjust based on code quality indicators
        if "try" in code and "except" in code:
            base_score += 0.5
        if "class" in code:
            base_score += 0.3
        if "def " in code:
            base_score += 0.2
        if '"""' in code or "'''" in code:
            base_score += 0.4
        if "import" in code:
            base_score += 0.1
        if "# " in code:
            base_score += 0.2
        if "type hint" in code or ": " in code:
            base_score += 0.3

        # Cap at 10
        base_score = min(10, base_score)

        # Generate aspect scores
        aspects = self.criteria[criteria]["aspects"]
        scores = {}
        for i, aspect in enumerate(aspects):
            variation = (i - len(aspects) / 2) * 0.3
            scores[aspect] = min(10, max(1, base_score + variation))

        return scores

    def _calculate_consensus(self, ai_scores: Dict[str, Dict]) -> float:
        """Calculate consensus score from all AI evaluations"""
        total = 0
        total_weight = 0

        for criteria_name, score_data in ai_scores.items():
            if criteria_name in self.criteria:
                weight = self.criteria[criteria_name]["weight"]
                total += score_data["average"] * weight
                total_weight += weight

        return (total / total_weight * 10) if total_weight > 0 else 5.0

    def _assess_readiness(self, consensus_score: float) -> str:
        """Assess evolution readiness based on consensus score"""
        if consensus_score >= 8.5:
            return "highly_ready"
        elif consensus_score >= 7.0:
            return "ready"
        elif consensus_score >= 5.5:
            return "conditionally_ready"
        elif consensus_score >= 4.0:
            return "needs_improvement"
        else:
            return "not_ready"

    def _identify_strengths(self, ai_scores: Dict[str, Dict]) -> List[str]:
        """Identify agent strengths"""
        strengths = []

        for criteria_name, score_data in ai_scores.items():
            threshold = self.criteria[criteria_name]["threshold"]
            if score_data["average"] >= threshold:
                for aspect, score in score_data["scores"].items():
                    if score >= threshold:
                        strengths.append(f"Strong {aspect.replace('_', ' ')}")

        return list(set(strengths))[:5]  # Top 5 unique strengths

    def _identify_weaknesses(self, ai_scores: Dict[str, Dict]) -> List[str]:
        """Identify agent weaknesses"""
        weaknesses = []

        for criteria_name, score_data in ai_scores.items():
            threshold = self.criteria[criteria_name]["threshold"]
            if score_data["average"] < threshold:
                for aspect, score in score_data["scores"].items():
                    if score < threshold - 2:
                        weaknesses.append(f"Weak {aspect.replace('_', ' ')}")

        return list(set(weaknesses))[:5]  # Top 5 unique weaknesses

    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate AI-based recommendations"""
        recommendations = []

        for criteria_name, score_data in evaluation["ai_scores"].items():
            if score_data["average"] < self.criteria[criteria_name]["threshold"]:
                recommendations.append(
                    {
                        "area": criteria_name.replace("_", " ").title(),
                        "priority": "high" if score_data["average"] < 5 else "medium",
                        "suggestion": self._get_improvement_suggestion(criteria_name, score_data),
                    }
                )

        return sorted(recommendations, key=lambda x: x["priority"] == "high", reverse=True)[:3]

    def _get_improvement_suggestion(self, criteria: str, score_data: Dict) -> str:
        """Get improvement suggestion for criteria"""
        suggestions = {
            "code_quality": "Refactor for better readability and add documentation",
            "evolution_potential": "Increase modularity and implement interfaces",
            "performance_prediction": "Optimize algorithms and reduce complexity",
            "security_assessment": "Add input validation and security checks",
            "business_value": "Focus on user needs and problem-solving",
        }

        # Find weakest aspect
        weakest = min(score_data["scores"].items(), key=lambda x: x[1])
        return f"{suggestions.get(criteria, 'Improve ' + criteria)}. Focus on {weakest[0].replace('_', ' ')}"

    def get_multi_model_consensus(self, agent_id: str, code: str) -> Dict[str, Any]:
        """Get consensus from multiple AI models"""
        evaluations = []

        for model in self.models:
            # Simulate different model evaluations
            eval_result = self.evaluate(agent_id, code)
            eval_result["model"] = model
            evaluations.append(eval_result)

        # Calculate consensus
        consensus = {
            "agent_id": agent_id,
            "models_used": self.models,
            "consensus_score": sum(e["consensus_score"] for e in evaluations) / len(evaluations),
            "agreement_level": self._calculate_agreement(evaluations),
            "final_readiness": self._determine_final_readiness(evaluations),
        }

        return consensus

    def _calculate_agreement(self, evaluations: List[Dict]) -> float:
        """Calculate agreement level between models"""
        if len(evaluations) < 2:
            return 1.0

        scores = [e["consensus_score"] for e in evaluations]
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)

        # Lower variance means higher agreement
        return max(0, 1 - variance / 10)

    def _determine_final_readiness(self, evaluations: List[Dict]) -> str:
        """Determine final readiness from multiple evaluations"""
        readiness_scores = {
            "highly_ready": 5,
            "ready": 4,
            "conditionally_ready": 3,
            "needs_improvement": 2,
            "not_ready": 1,
        }

        total_score = sum(readiness_scores.get(e["evolution_readiness"], 1) for e in evaluations)
        avg_score = total_score / len(evaluations)

        if avg_score >= 4.5:
            return "highly_ready"
        elif avg_score >= 3.5:
            return "ready"
        elif avg_score >= 2.5:
            return "conditionally_ready"
        elif avg_score >= 1.5:
            return "needs_improvement"
        else:
            return "not_ready"

    def export_evaluation(self, agent_id: str) -> Dict[str, Any]:
        """Export evaluation history for agent"""
        if agent_id not in self.history:
            return {"error": "No evaluation history"}

        history = self.history[agent_id]
        return {
            "agent_id": agent_id,
            "total_evaluations": len(history),
            "latest": history[-1] if history else None,
            "trend": self._calculate_trend(history),
            "average_score": sum(e["consensus_score"] for e in history) / len(history),
        }

    def _calculate_trend(self, history: List[Dict]) -> str:
        """Calculate evaluation trend"""
        if len(history) < 2:
            return "insufficient_data"

        recent = history[-5:]
        scores = [e["consensus_score"] for e in recent]

        if all(scores[i] <= scores[i + 1] for i in range(len(scores) - 1)):
            return "improving"
        elif all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)):
            return "declining"
        else:
            return "stable"
