"""
PromptOptimizer - Day 32
Prompt engineering optimization system
Size: ~6.5KB (optimized)
"""

import hashlib
import json
import re
import time
from collections import defaultdict
from typing import Any, Dict, List, Tuple


class PromptOptimizer:
    """Optimizes prompts for better AI model performance"""

    def __init__(self):
        self.strategies = self._init_strategies()
        self.metrics = defaultdict(int)
        self.cache = {}
        self.cache_stats = {"hits": 0, "misses": 0}
        self.versions = {}
        self.ab_tests = {}

    def optimize(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a prompt configuration"""
        template = prompt_config.get("template", "")
        variables = prompt_config.get("variables", {})

        # Apply optimization strategies
        optimized = template
        improvements = []

        # Add clarity
        if "please" in optimized.lower():
            optimized = optimized.replace("please", "").strip()
            improvements.append("removed_politeness")

        # Add specificity
        if not any(word in optimized.lower() for word in ["specific", "exact", "precise"]):
            optimized = f"Be specific: {optimized}"
            improvements.append("added_specificity")

        # Format variables
        for key, value in variables.items():
            optimized = optimized.replace(f"{{{key}}}", str(value))

        score = self._calculate_score(optimized)
        self.metrics["total_optimizations"] += 1
        self.metrics["total_score"] += score

        return {
            "optimized_prompt": optimized,
            "improvements": improvements,
            "score": score,
            "original": template,
        }

    def inject_chain_of_thought(self, prompt: str) -> str:
        """Inject chain-of-thought reasoning"""
        cot_prefix = "Let's think step by step:\n"
        if "step" not in prompt.lower():
            return f"{cot_prefix}{prompt}"
        return prompt

    def add_few_shot_examples(self, task: str, examples: List[Dict]) -> str:
        """Add few-shot learning examples"""
        if len(examples) > 5:
            examples = examples[:5]  # Limit to 5 examples

        prompt = f"Task: {task}\n\nExamples:\n"
        for i, ex in enumerate(examples, 1):
            prompt += f"{i}. Input: {ex['input']}\n   Output: {ex['output']}\n"

        prompt += "\nNow, for the new input:\n"
        return prompt

    def compress_context(self, context: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Compress long context to fit token limits"""
        words = context.split()

        if len(words) <= max_tokens:
            return {"text": context, "compressed": False}

        # Simple compression: take first and last parts
        half = max_tokens // 2
        compressed = " ".join(words[:half]) + " ... " + " ".join(words[-half:])

        return {"text": compressed, "compressed": True, "original_length": len(words)}

    def generate_template(self, requirements: Dict[str, Any]) -> str:
        """Generate prompt template from requirements"""
        task = requirements.get("task", "general")
        language = requirements.get("language", "any")
        focus_areas = requirements.get("focus", [])

        template = f"Task: {task}\n"

        if language != "any":
            template += f"Language: {language}\n"

        template += "Input: {code}\n"

        if focus_areas:
            template += f"Focus on: {', '.join(focus_areas)}\n"

        template += "Provide detailed analysis.\n"

        return template

    def estimate_cost(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate token usage and cost"""
        text = prompt_config.get("template", "")
        max_tokens = prompt_config.get("max_tokens", 500)

        # Simple token estimation (4 chars = 1 token approximately)
        input_tokens = len(text) // 4

        # Cost per 1K tokens (example rates)
        input_cost_per_1k = 0.01
        output_cost_per_1k = 0.03

        estimated_cost = (input_tokens / 1000) * input_cost_per_1k + (
            max_tokens / 1000
        ) * output_cost_per_1k

        return {
            "tokens": input_tokens + max_tokens,
            "input_tokens": input_tokens,
            "output_tokens": max_tokens,
            "estimated_cost": round(estimated_cost, 4),
        }

    def optimize_with_cache(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize with caching"""
        cache_key = hashlib.sha256(json.dumps(prompt_config, sort_keys=True).encode()).hexdigest()

        if cache_key in self.cache:
            self.cache_stats["hits"] += 1
            return self.cache[cache_key]

        self.cache_stats["misses"] += 1
        result = self.optimize(prompt_config)
        self.cache[cache_key] = result

        return result

    def optimize_for_model(self, prompt: str, model: str) -> str:
        """Optimize for specific model"""
        if model == "claude":
            # Claude prefers conversational format
            return f"Human: {prompt}\n\nAssistant:"
        elif model.startswith("gpt"):
            # GPT works well with direct instructions
            return f"Instructions: {prompt}"
        else:
            return prompt

    def validate_prompt(self, prompt_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate prompt configuration"""
        errors = []

        if not prompt_config.get("template"):
            errors.append("Template is required")

        if "variables" not in prompt_config:
            errors.append("Variables dict is required")

        template = prompt_config.get("template", "")
        if len(template) > 10000:
            errors.append("Template too long (>10000 chars)")

        return len(errors) == 0, errors

    def score_prompt(self, prompt_config: Dict[str, Any]) -> Dict[str, float]:
        """Score prompt quality"""
        template = prompt_config.get("template", "")

        # Clarity score
        clarity = 1.0
        if len(template) > 500:
            clarity -= 0.2
        if template.count(",") > 10:
            clarity -= 0.1

        # Specificity score
        specificity = 0.5
        specific_words = ["specific", "exact", "precise", "detailed"]
        for word in specific_words:
            if word in template.lower():
                specificity += 0.1

        overall = (clarity + specificity) / 2

        return {
            "clarity": max(0, min(1, clarity)),
            "specificity": max(0, min(1, specificity)),
            "overall": max(0, min(1, overall)),
        }

    def iterative_refine(self, prompt: str, iterations: int = 3) -> Dict[str, Any]:
        """Iteratively refine prompt"""
        history = []
        current = prompt

        for i in range(iterations):
            # Apply refinements
            if i == 0:
                current = self.inject_chain_of_thought(current)
            elif i == 1:
                current = f"Be concise and specific: {current}"
            else:
                current = current.replace("  ", " ")

            history.append(current)

        improvement = len(current) / len(prompt) if len(prompt) > 0 else 1

        return {
            "final_prompt": current,
            "history": history,
            "improvement_rate": improvement,
            "iterations": iterations,
        }

    def save_version(self, prompt_config: Dict[str, Any], version: str) -> str:
        """Save prompt version"""
        version_id = f"{version}_{int(time.time())}"
        self.versions[version_id] = prompt_config
        return version_id

    def get_version(self, version_id: str) -> Dict[str, Any]:
        """Get prompt version"""
        return self.versions.get(version_id, {})

    def list_versions(self) -> List[str]:
        """List all versions"""
        return list(self.versions.keys())

    def setup_ab_test(self, variant_a: str, variant_b: str) -> Dict[str, Any]:
        """Setup A/B test for prompts"""
        test_id = f"test_{int(time.time())}"

        self.ab_tests[test_id] = {
            "variants": [variant_a, variant_b],
            "results": {"a": [], "b": []},
            "created_at": time.time(),
        }

        return {
            "test_id": test_id,
            "variants": ["a", "b"],
            "status": "active",
        }

    def optimize_tokens(self, prompt: str) -> str:
        """Optimize token usage"""
        # Remove redundant words
        redundant = ["please", "could you", "would you", "if possible", "kindly"]
        optimized = prompt

        for word in redundant:
            optimized = re.sub(rf"\b{word}\b", "", optimized, flags=re.IGNORECASE)

        # Remove extra spaces
        optimized = " ".join(optimized.split())

        return optimized

    def count_tokens(self, text: str) -> int:
        """Estimate token count"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def is_safe(self, prompt: str) -> bool:
        """Check if prompt is safe and compliant"""
        unsafe_patterns = [
            "hack",
            "exploit",
            "illegal",
            "malicious",
            "password",
            "credential",
            "private key",
        ]

        prompt_lower = prompt.lower()
        for pattern in unsafe_patterns:
            if pattern in prompt_lower:
                return False

        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get optimization metrics"""
        total = self.metrics["total_optimizations"]
        avg_improvement = self.metrics["total_score"] / total if total > 0 else 0

        return {
            "total_optimizations": total,
            "average_improvement": round(avg_improvement, 3),
            "cache_hit_rate": self._get_cache_hit_rate(),
            "versions_saved": len(self.versions),
            "active_ab_tests": len(self.ab_tests),
        }

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return self.cache_stats.copy()

    def _init_strategies(self) -> Dict[str, Any]:
        """Initialize optimization strategies"""
        return {
            "clarity": {"weight": 0.3},
            "specificity": {"weight": 0.3},
            "brevity": {"weight": 0.2},
            "structure": {"weight": 0.2},
        }

    def _calculate_score(self, prompt: str) -> float:
        """Calculate prompt quality score"""
        score = 0.5  # Base score

        # Bonus for clarity indicators
        if any(word in prompt.lower() for word in ["specific", "clear", "exact"]):
            score += 0.2

        # Bonus for structure
        if "\n" in prompt:
            score += 0.1

        # Penalty for verbosity
        if len(prompt) > 1000:
            score -= 0.1

        return max(0, min(1, score))

    def _get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total == 0:
            return 0.0
        return round(self.cache_stats["hits"] / total, 3)
