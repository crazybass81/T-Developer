from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ModelCapabilities:
    context_length: int
    supported_languages: List[str]
    specialties: List[str]
    cost_per_token: float
    latency: str  # 'low', 'medium', 'high'
    availability: float  # 0-1


@dataclass
class RoutingCriteria:
    task_type: str
    required_context: int
    target_language: Optional[str] = None
    max_cost: Optional[float] = None
    max_latency: Optional[str] = None
    required_capabilities: Optional[List[str]] = None


class ModelRouter:
    def __init__(self):
        self.model_registry = self._initialize_model_registry()
        self.performance_history = defaultdict(list)

    def _initialize_model_registry(self) -> Dict[str, ModelCapabilities]:
        return {
            "gpt-4": ModelCapabilities(
                context_length=128000,
                supported_languages=["all"],
                specialties=["reasoning", "coding", "analysis"],
                cost_per_token=0.00003,
                latency="medium",
                availability=0.99,
            ),
            "claude-3-opus": ModelCapabilities(
                context_length=200000,
                supported_languages=["all"],
                specialties=["long-context", "analysis", "creative"],
                cost_per_token=0.000015,
                latency="low",
                availability=0.98,
            ),
            "gpt-3.5-turbo": ModelCapabilities(
                context_length=16385,
                supported_languages=["all"],
                specialties=["general", "fast"],
                cost_per_token=0.000002,
                latency="low",
                availability=0.995,
            ),
        }

    async def select_model(self, criteria: RoutingCriteria) -> str:
        candidates = self._filter_candidates(criteria)

        if not candidates:
            raise ValueError("No suitable model found for criteria")

        scores = await self._score_models(candidates, criteria)
        best_model = max(scores, key=scores.get)

        await self._record_selection(best_model, criteria)
        return best_model

    def _filter_candidates(self, criteria: RoutingCriteria) -> List[str]:
        candidates = []

        for model, capabilities in self.model_registry.items():
            if capabilities.context_length < criteria.required_context:
                continue

            if (
                criteria.target_language
                and "all" not in capabilities.supported_languages
                and criteria.target_language not in capabilities.supported_languages
            ):
                continue

            if criteria.max_latency:
                latency_order = ["low", "medium", "high"]
                if latency_order.index(capabilities.latency) > latency_order.index(
                    criteria.max_latency
                ):
                    continue

            candidates.append(model)

        return candidates

    async def _score_models(
        self, candidates: List[str], criteria: RoutingCriteria
    ) -> Dict[str, float]:
        scores = {}

        for model in candidates:
            capabilities = self.model_registry[model]
            score = 0

            # Specialty score
            specialty_score = self._calculate_specialty_score(
                capabilities.specialties, criteria.task_type
            )
            score += specialty_score * 0.3

            # Cost score
            if criteria.max_cost:
                cost_score = 1 - (capabilities.cost_per_token / criteria.max_cost)
                score += max(0, cost_score) * 0.2

            # Performance history score
            performance_score = await self._get_performance_score(model)
            score += performance_score * 0.3

            # Availability score
            score += capabilities.availability * 0.2

            scores[model] = score

        return scores

    def _calculate_specialty_score(self, specialties: List[str], task_type: str) -> float:
        if task_type in specialties:
            return 1.0

        # Partial matching
        task_words = task_type.lower().split()
        for specialty in specialties:
            if any(word in specialty.lower() for word in task_words):
                return 0.7

        return 0.3

    async def _get_performance_score(self, model: str) -> float:
        history = self.performance_history[model]
        if not history:
            return 0.5  # Default score

        # Calculate average success rate
        successes = sum(1 for record in history if record.get("success", False))
        return successes / len(history)

    async def _record_selection(self, model: str, criteria: RoutingCriteria) -> None:
        # Record selection for learning
        pass
