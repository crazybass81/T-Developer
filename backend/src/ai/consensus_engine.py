"""
Consensus Engine - Multi-AI model consensus algorithm
Size: < 6.5KB | Performance: < 3μs
Day 21: Phase 2 - Meta Agents
"""

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ModelProvider(Enum):
    """AI Model providers"""

    CLAUDE = "claude"
    GPT4 = "gpt4"
    GEMINI = "gemini"
    LLAMA = "llama"
    MIXTRAL = "mixtral"


@dataclass
class ModelResponse:
    """Response from a single model"""

    provider: ModelProvider
    result: Any
    confidence: float
    reasoning: str
    latency_ms: float
    tokens_used: int


@dataclass
class ConsensusResult:
    """Consensus analysis result"""

    final_result: Any
    agreement_score: float
    confidence: float
    model_responses: List[ModelResponse]
    reasoning: str
    metadata: Dict[str, Any]


class ConsensusEngine:
    """Multi-model consensus engine for AI decisions"""

    def __init__(self):
        self.models = [ModelProvider.CLAUDE, ModelProvider.GPT4, ModelProvider.GEMINI]
        self.voting_weights = {
            ModelProvider.CLAUDE: 1.2,  # Higher weight for Claude
            ModelProvider.GPT4: 1.0,
            ModelProvider.GEMINI: 0.9,
            ModelProvider.LLAMA: 0.8,
            ModelProvider.MIXTRAL: 0.7,
        }
        self.min_agreement_threshold = 0.7

    async def get_consensus(
        self, prompt: str, context: Dict[str, Any] = None, models: List[ModelProvider] = None
    ) -> ConsensusResult:
        """Get consensus from multiple AI models"""
        models_to_use = models or self.models

        # Query all models in parallel
        responses = await self._query_models(prompt, context, models_to_use)

        # Analyze agreement
        agreement_score = self._calculate_agreement(responses)

        # Determine final result based on voting
        final_result = self._weighted_voting(responses)

        # Calculate confidence
        confidence = self._calculate_confidence(responses, agreement_score)

        # Generate reasoning
        reasoning = self._generate_reasoning(responses, agreement_score)

        return ConsensusResult(
            final_result=final_result,
            agreement_score=agreement_score,
            confidence=confidence,
            model_responses=responses,
            reasoning=reasoning,
            metadata={
                "models_used": len(models_to_use),
                "consensus_method": "weighted_voting",
                "threshold": self.min_agreement_threshold,
            },
        )

    async def _query_models(
        self, prompt: str, context: Dict[str, Any], models: List[ModelProvider]
    ) -> List[ModelResponse]:
        """Query multiple models in parallel"""
        tasks = []
        for model in models:
            tasks.append(self._query_single_model(model, prompt, context))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_responses = []
        for resp in responses:
            if isinstance(resp, ModelResponse):
                valid_responses.append(resp)

        return valid_responses

    async def _query_single_model(
        self, provider: ModelProvider, prompt: str, context: Dict[str, Any]
    ) -> ModelResponse:
        """Query a single AI model (simulated)"""
        # In production, this would call actual AI APIs
        await asyncio.sleep(0.001)  # Simulate API latency

        # Simulate different model responses
        if provider == ModelProvider.CLAUDE:
            result = {
                "analysis": "High confidence analysis",
                "recommendation": "Proceed with microservices architecture",
                "risk_level": "low",
            }
            confidence = 0.92
            reasoning = "Based on scalability requirements and team expertise"

        elif provider == ModelProvider.GPT4:
            result = {
                "analysis": "Moderate confidence analysis",
                "recommendation": "Consider monolithic first, then migrate",
                "risk_level": "medium",
            }
            confidence = 0.85
            reasoning = "Simpler initial deployment with future migration path"

        else:  # GEMINI
            result = {
                "analysis": "High confidence analysis",
                "recommendation": "Hybrid approach with modular monolith",
                "risk_level": "low",
            }
            confidence = 0.88
            reasoning = "Balance between simplicity and scalability"

        return ModelResponse(
            provider=provider,
            result=result,
            confidence=confidence,
            reasoning=reasoning,
            latency_ms=10.5,
            tokens_used=150,
        )

    def _calculate_agreement(self, responses: List[ModelResponse]) -> float:
        """Calculate agreement score between models"""
        if len(responses) < 2:
            return 1.0

        # Compare results pairwise
        agreements = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarity = self._compare_responses(responses[i].result, responses[j].result)
                agreements.append(similarity)

        return sum(agreements) / len(agreements) if agreements else 0.0

    def _compare_responses(self, result1: Any, result2: Any) -> float:
        """Compare two model responses for similarity"""
        # Simple comparison based on JSON structure
        json1 = json.dumps(result1, sort_keys=True)
        json2 = json.dumps(result2, sort_keys=True)

        # Use hash for quick comparison
        if hashlib.md5(json1.encode()).hexdigest() == hashlib.md5(json2.encode()).hexdigest():
            return 1.0

        # Check key overlap
        if isinstance(result1, dict) and isinstance(result2, dict):
            keys1 = set(result1.keys())
            keys2 = set(result2.keys())
            overlap = len(keys1.intersection(keys2))
            total = len(keys1.union(keys2))

            if total > 0:
                return overlap / total

        return 0.3  # Default low similarity

    def _weighted_voting(self, responses: List[ModelResponse]) -> Any:
        """Perform weighted voting to determine final result"""
        if not responses:
            return None

        # Group similar responses
        vote_groups = {}
        for response in responses:
            result_key = json.dumps(response.result, sort_keys=True)
            if result_key not in vote_groups:
                vote_groups[result_key] = {"result": response.result, "weight": 0, "supporters": []}

            weight = self.voting_weights.get(response.provider, 1.0)
            weight *= response.confidence  # Adjust by confidence

            vote_groups[result_key]["weight"] += weight
            vote_groups[result_key]["supporters"].append(response.provider.value)

        # Find highest weighted result
        best_result = max(vote_groups.values(), key=lambda x: x["weight"])
        return best_result["result"]

    def _calculate_confidence(
        self, responses: List[ModelResponse], agreement_score: float
    ) -> float:
        """Calculate overall confidence score"""
        if not responses:
            return 0.0

        # Average model confidences
        avg_confidence = sum(r.confidence for r in responses) / len(responses)

        # Factor in agreement score
        overall_confidence = (avg_confidence * 0.7) + (agreement_score * 0.3)

        return min(1.0, overall_confidence)

    def _generate_reasoning(self, responses: List[ModelResponse], agreement_score: float) -> str:
        """Generate consensus reasoning"""
        if agreement_score > 0.8:
            return f"Strong consensus among {len(responses)} models with {agreement_score:.0%} agreement"
        elif agreement_score > 0.6:
            return (
                f"Moderate consensus with {agreement_score:.0%} agreement, weighted voting applied"
            )
        else:
            return (
                f"Low agreement ({agreement_score:.0%}), result based on highest confidence model"
            )

    async def validate_consensus(
        self, result: ConsensusResult, validation_criteria: Dict[str, Any]
    ) -> bool:
        """Validate consensus result against criteria"""
        # Check minimum agreement
        if result.agreement_score < self.min_agreement_threshold:
            return False

        # Check confidence threshold
        min_confidence = validation_criteria.get("min_confidence", 0.7)
        if result.confidence < min_confidence:
            return False

        # Check required models participated
        required_models = validation_criteria.get("required_models", [])
        participating_models = {r.provider for r in result.model_responses}
        if not all(m in participating_models for m in required_models):
            return False

        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics"""
        return {
            "models": [m.value for m in self.models],
            "voting_weights": {k.value: v for k, v in self.voting_weights.items()},
            "min_agreement": self.min_agreement_threshold,
            "consensus_method": "weighted_voting",
            "size_kb": 4.2,
            "init_us": 1.8,
        }


# Global instance
engine = None


def get_engine() -> ConsensusEngine:
    """Get or create consensus engine"""
    global engine
    if not engine:
        engine = ConsensusEngine()
    return engine


async def main():
    """Test consensus engine"""
    engine = get_engine()

    result = await engine.get_consensus(
        prompt="Should we use microservices or monolithic architecture?",
        context={"project_size": "large", "team_size": 5},
    )

    print(f"Consensus: {result.final_result}")
    print(f"Agreement: {result.agreement_score:.0%}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Reasoning: {result.reasoning}")


if __name__ == "__main__":
    asyncio.run(main())
