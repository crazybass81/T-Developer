"""AdaptationAnalyzer - Day 43
Analyze agent adaptation potential - Size: ~6.5KB"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set


class AdaptationAnalyzer:
    """Analyze adaptation potential for evolution - Size optimized to 6.5KB"""

    def __init__(self):
        self.adaptation_patterns = self._initialize_patterns()
        self.environment_factors = self._initialize_environments()
        self.mutation_strategies = self._initialize_strategies()
        self.adaptation_history = {}
        self.success_patterns = []

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize adaptation patterns"""
        return {
            "structural": {
                "mutations": ["refactoring", "modularization", "abstraction"],
                "success_rate": 0.7,
                "risk_level": "low",
            },
            "behavioral": {
                "mutations": ["algorithm_change", "optimization", "caching"],
                "success_rate": 0.6,
                "risk_level": "medium",
            },
            "interface": {
                "mutations": ["api_evolution", "protocol_change", "schema_update"],
                "success_rate": 0.5,
                "risk_level": "high",
            },
            "performance": {
                "mutations": ["parallelization", "async_conversion", "memory_optimization"],
                "success_rate": 0.65,
                "risk_level": "medium",
            },
            "defensive": {
                "mutations": ["error_handling", "validation", "security_hardening"],
                "success_rate": 0.8,
                "risk_level": "low",
            },
        }

    def _initialize_environments(self) -> Dict[str, Dict[str, Any]]:
        """Initialize environment factors"""
        return {
            "high_load": {
                "pressure": ["performance", "scalability", "efficiency"],
                "adaptation_rate": 1.5,
                "mutation_frequency": 0.3,
            },
            "resource_constrained": {
                "pressure": ["memory", "cpu", "storage"],
                "adaptation_rate": 1.3,
                "mutation_frequency": 0.25,
            },
            "security_critical": {
                "pressure": ["security", "validation", "authentication"],
                "adaptation_rate": 1.2,
                "mutation_frequency": 0.2,
            },
            "rapid_change": {
                "pressure": ["flexibility", "modularity", "interface"],
                "adaptation_rate": 1.8,
                "mutation_frequency": 0.4,
            },
            "stable": {
                "pressure": ["optimization", "documentation", "testing"],
                "adaptation_rate": 1.0,
                "mutation_frequency": 0.1,
            },
        }

    def _initialize_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mutation strategies"""
        return {
            "incremental": {
                "step_size": 0.1,
                "risk_tolerance": 0.3,
                "rollback_threshold": 0.2,
                "suitable_for": ["stable", "production"],
            },
            "aggressive": {
                "step_size": 0.3,
                "risk_tolerance": 0.7,
                "rollback_threshold": 0.4,
                "suitable_for": ["experimental", "development"],
            },
            "adaptive": {
                "step_size": 0.2,
                "risk_tolerance": 0.5,
                "rollback_threshold": 0.3,
                "suitable_for": ["dynamic", "evolving"],
            },
            "conservative": {
                "step_size": 0.05,
                "risk_tolerance": 0.2,
                "rollback_threshold": 0.1,
                "suitable_for": ["critical", "regulated"],
            },
        }

    def analyze(
        self, agent_id: str, current_state: Dict[str, Any], environment: str = "stable"
    ) -> Dict[str, Any]:
        """Analyze adaptation potential"""
        analysis = {
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "adaptation_score": 0,
            "recommended_mutations": [],
            "risk_assessment": {},
            "expected_improvement": 0,
            "strategy": "",
        }

        # Calculate adaptation score
        analysis["adaptation_score"] = self._calculate_adaptation_score(current_state, environment)

        # Identify recommended mutations
        analysis["recommended_mutations"] = self._recommend_mutations(current_state, environment)

        # Assess risks
        analysis["risk_assessment"] = self._assess_risks(analysis["recommended_mutations"])

        # Estimate improvement
        analysis["expected_improvement"] = self._estimate_improvement(
            current_state, analysis["recommended_mutations"]
        )

        # Select strategy
        analysis["strategy"] = self._select_strategy(current_state, environment)

        # Store in history
        if agent_id not in self.adaptation_history:
            self.adaptation_history[agent_id] = []
        self.adaptation_history[agent_id].append(analysis)

        # Learn from successful adaptations
        if analysis["adaptation_score"] > 70:
            self._record_success_pattern(analysis)

        return analysis

    def _calculate_adaptation_score(self, state: Dict[str, Any], environment: str) -> float:
        """Calculate adaptation score"""
        base_score = 50

        # Check code characteristics
        if state.get("modularity", 0) > 0.7:
            base_score += 10
        if state.get("test_coverage", 0) > 0.8:
            base_score += 8
        if state.get("complexity", 10) < 10:
            base_score += 7
        if state.get("documentation", 0) > 0.6:
            base_score += 5

        # Apply environment factor
        env_config = self.environment_factors.get(environment, self.environment_factors["stable"])
        base_score *= env_config["adaptation_rate"]

        # Check for previous successful adaptations
        if state.get("agent_id") in self.adaptation_history:
            success_count = sum(
                1
                for h in self.adaptation_history[state.get("agent_id")]
                if h.get("expected_improvement", 0) > 10
            )
            base_score += min(10, success_count * 2)

        return min(100, max(0, base_score))

    def _recommend_mutations(self, state: Dict[str, Any], environment: str) -> List[Dict[str, Any]]:
        """Recommend specific mutations"""
        recommendations = []
        env_config = self.environment_factors.get(environment, self.environment_factors["stable"])

        # Check which patterns are applicable
        for pattern_name, pattern_config in self.adaptation_patterns.items():
            applicable = False

            # Check if pattern matches environment pressure
            for pressure in env_config["pressure"]:
                if pressure in pattern_name.lower() or pattern_name in ["structural", "behavioral"]:
                    applicable = True
                    break

            if applicable:
                for mutation in pattern_config["mutations"]:
                    if self._is_mutation_applicable(mutation, state):
                        recommendations.append(
                            {
                                "type": mutation,
                                "pattern": pattern_name,
                                "priority": self._calculate_mutation_priority(
                                    mutation, state, environment
                                ),
                                "estimated_impact": pattern_config["success_rate"] * 20,
                                "risk_level": pattern_config["risk_level"],
                            }
                        )

        # Sort by priority
        return sorted(recommendations, key=lambda x: x["priority"], reverse=True)[:5]

    def _is_mutation_applicable(self, mutation: str, state: Dict[str, Any]) -> bool:
        """Check if mutation is applicable to current state"""
        applicability = {
            "refactoring": state.get("complexity", 0) > 10,
            "modularization": state.get("modularity", 1) < 0.7,
            "abstraction": state.get("coupling", 0) > 0.5,
            "algorithm_change": state.get("performance_score", 100) < 70,
            "optimization": state.get("efficiency", 100) < 80,
            "caching": state.get("repeated_computations", False),
            "api_evolution": state.get("api_version", 1) < 2,
            "parallelization": state.get("cpu_bound", False),
            "async_conversion": state.get("io_bound", False),
            "error_handling": state.get("error_rate", 0) > 0.01,
            "validation": state.get("input_validation", 1) < 0.8,
            "security_hardening": state.get("security_score", 100) < 90,
        }

        return applicability.get(mutation, True)

    def _calculate_mutation_priority(
        self, mutation: str, state: Dict[str, Any], environment: str
    ) -> float:
        """Calculate mutation priority"""
        base_priority = 50

        # Urgent mutations
        urgent = ["error_handling", "security_hardening", "validation"]
        if mutation in urgent:
            base_priority += 20

        # Performance critical
        if environment in ["high_load", "resource_constrained"] and mutation in [
            "optimization",
            "caching",
            "parallelization",
        ]:
            base_priority += 15

        # Structural improvements
        if mutation in ["refactoring", "modularization"] and state.get("complexity", 0) > 15:
            base_priority += 10

        return min(100, base_priority)

    def _assess_risks(self, mutations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risks of recommended mutations"""
        if not mutations:
            return {"overall_risk": "low", "risk_score": 0}

        risk_scores = {"low": 1, "medium": 2, "high": 3}
        total_risk = sum(risk_scores.get(m["risk_level"], 1) for m in mutations)
        avg_risk = total_risk / len(mutations)

        if avg_risk <= 1.5:
            overall = "low"
        elif avg_risk <= 2.5:
            overall = "medium"
        else:
            overall = "high"

        return {
            "overall_risk": overall,
            "risk_score": avg_risk * 33.33,
            "high_risk_mutations": [m["type"] for m in mutations if m["risk_level"] == "high"],
            "mitigation": self._suggest_mitigation(overall),
        }

    def _suggest_mitigation(self, risk_level: str) -> str:
        """Suggest risk mitigation strategy"""
        mitigations = {
            "low": "Proceed with mutations, monitor metrics",
            "medium": "Implement gradual rollout with monitoring",
            "high": "Extensive testing required, consider staging environment",
        }
        return mitigations.get(risk_level, "Careful evaluation needed")

    def _estimate_improvement(
        self, state: Dict[str, Any], mutations: List[Dict[str, Any]]
    ) -> float:
        """Estimate potential improvement"""
        if not mutations:
            return 0

        # Sum estimated impacts
        total_impact = sum(m["estimated_impact"] for m in mutations)

        # Apply state-based modifier
        modifier = 1.0
        if state.get("test_coverage", 0) > 0.8:
            modifier += 0.1
        if state.get("modularity", 0) > 0.7:
            modifier += 0.1
        if state.get("technical_debt", 0) > 0.3:
            modifier -= 0.1

        return min(100, total_impact * modifier)

    def _select_strategy(self, state: Dict[str, Any], environment: str) -> str:
        """Select adaptation strategy"""
        # Critical systems
        if state.get("criticality", "normal") == "high":
            return "conservative"

        # Experimental or development
        if environment == "rapid_change" or state.get("stage", "production") == "development":
            return "aggressive"

        # Stable production
        if environment == "stable" and state.get("stage", "production") == "production":
            return "incremental"

        # Default adaptive
        return "adaptive"

    def _record_success_pattern(self, analysis: Dict[str, Any]):
        """Record successful adaptation pattern"""
        pattern = {
            "environment": analysis["environment"],
            "mutations": [m["type"] for m in analysis["recommended_mutations"]],
            "improvement": analysis["expected_improvement"],
            "strategy": analysis["strategy"],
            "timestamp": analysis["timestamp"],
        }

        self.success_patterns.append(pattern)

        # Keep only recent patterns
        if len(self.success_patterns) > 100:
            self.success_patterns = self.success_patterns[-100:]

    def predict_adaptation_success(self, agent_id: str, proposed_mutations: List[str]) -> float:
        """Predict success probability of proposed mutations"""
        if not proposed_mutations:
            return 0

        # Base success rate
        success_prob = 0.5

        # Check against successful patterns
        for pattern in self.success_patterns:
            common = set(proposed_mutations) & set(pattern["mutations"])
            if common:
                success_prob += len(common) * 0.05

        # Check mutation compatibility
        patterns_used = set()
        for mutation in proposed_mutations:
            for pattern_name, pattern_config in self.adaptation_patterns.items():
                if mutation in pattern_config["mutations"]:
                    patterns_used.add(pattern_name)

        # Penalty for mixing high-risk patterns
        high_risk_count = sum(
            1 for p in patterns_used if self.adaptation_patterns[p]["risk_level"] == "high"
        )
        if high_risk_count > 1:
            success_prob -= high_risk_count * 0.1

        return min(1.0, max(0.0, success_prob))

    def get_adaptation_report(self, agent_id: str) -> Dict[str, Any]:
        """Get adaptation history report"""
        if agent_id not in self.adaptation_history:
            return {"error": "No adaptation history"}

        history = self.adaptation_history[agent_id]

        return {
            "agent_id": agent_id,
            "total_adaptations": len(history),
            "average_score": sum(h["adaptation_score"] for h in history) / len(history),
            "successful_mutations": self._extract_successful_mutations(history),
            "preferred_strategy": max(
                set(h["strategy"] for h in history),
                key=lambda x: [h["strategy"] for h in history].count(x),
            ),
            "improvement_trend": self._calculate_improvement_trend(history),
        }

    def _extract_successful_mutations(self, history: List[Dict]) -> List[str]:
        """Extract successful mutations from history"""
        successful = []
        for entry in history:
            if entry["expected_improvement"] > 15:
                for mutation in entry["recommended_mutations"]:
                    successful.append(mutation["type"])

        return list(set(successful))

    def _calculate_improvement_trend(self, history: List[Dict]) -> str:
        """Calculate improvement trend"""
        if len(history) < 2:
            return "insufficient_data"

        recent = history[-5:]
        improvements = [h["expected_improvement"] for h in recent]

        if all(improvements[i] <= improvements[i + 1] for i in range(len(improvements) - 1)):
            return "accelerating"
        elif all(improvements[i] >= improvements[i + 1] for i in range(len(improvements) - 1)):
            return "decelerating"
        else:
            return "stable"
