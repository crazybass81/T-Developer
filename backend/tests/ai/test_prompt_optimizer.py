"""
PromptOptimizer Tests - Day 32
Tests for prompt engineering optimization
"""

import pytest

from src.ai.prompt_optimizer import PromptOptimizer


class TestPromptOptimizer:
    """Tests for PromptOptimizer"""

    @pytest.fixture
    def optimizer(self):
        """Create PromptOptimizer instance"""
        return PromptOptimizer()

    @pytest.fixture
    def sample_prompt(self):
        """Sample prompt for testing"""
        return {
            "template": "Generate a {language} function that {action}",
            "variables": {"language": "Python", "action": "sorts a list"},
            "context": "Code generation task",
            "max_tokens": 500,
        }

    def test_optimizer_initialization(self, optimizer):
        """Test PromptOptimizer initialization"""
        assert optimizer is not None
        assert hasattr(optimizer, "strategies")
        assert hasattr(optimizer, "metrics")

    def test_optimize_prompt(self, optimizer, sample_prompt):
        """Test prompt optimization"""
        result = optimizer.optimize(sample_prompt)

        assert "optimized_prompt" in result
        assert "improvements" in result
        assert "score" in result
        assert result["score"] >= 0.7

    def test_chain_of_thought_injection(self, optimizer):
        """Test chain-of-thought reasoning injection"""
        prompt = "Solve this problem: 5 * 3 + 2"
        result = optimizer.inject_chain_of_thought(prompt)

        assert "Let's think step by step" in result or "step-by-step" in result.lower()

    def test_few_shot_learning(self, optimizer):
        """Test few-shot learning examples"""
        task = "Classify sentiment"
        examples = [
            {"input": "Great product!", "output": "positive"},
            {"input": "Terrible service", "output": "negative"},
        ]

        result = optimizer.add_few_shot_examples(task, examples)
        assert len(examples) <= 5  # Limit examples
        assert "Examples:" in result or any(ex["input"] in result for ex in examples)

    def test_context_compression(self, optimizer):
        """Test context compression"""
        long_context = "This is a very long context " * 100
        result = optimizer.compress_context(long_context, max_tokens=100)

        assert len(result) < len(long_context)
        assert result["compressed"] is True

    def test_prompt_template_generation(self, optimizer):
        """Test automatic template generation"""
        requirements = {
            "task": "code review",
            "language": "Python",
            "focus": ["performance", "security"],
        }

        template = optimizer.generate_template(requirements)
        assert "{code}" in template
        assert "performance" in template.lower() or "security" in template.lower()

    def test_cost_estimation(self, optimizer, sample_prompt):
        """Test cost estimation for prompts"""
        cost = optimizer.estimate_cost(sample_prompt)

        assert "tokens" in cost
        assert "estimated_cost" in cost
        assert cost["estimated_cost"] >= 0

    def test_prompt_caching(self, optimizer, sample_prompt):
        """Test prompt caching mechanism"""
        # First call
        result1 = optimizer.optimize_with_cache(sample_prompt)

        # Second call (should use cache)
        result2 = optimizer.optimize_with_cache(sample_prompt)

        assert result1 == result2
        assert optimizer.get_cache_stats()["hits"] >= 1

    def test_multi_model_optimization(self, optimizer):
        """Test optimization for different models"""
        prompt = "Generate code"

        claude_optimized = optimizer.optimize_for_model(prompt, "claude")
        gpt_optimized = optimizer.optimize_for_model(prompt, "gpt-4")

        assert claude_optimized != gpt_optimized
        assert "Human:" in claude_optimized or "Assistant:" in claude_optimized

    def test_prompt_validation(self, optimizer):
        """Test prompt validation"""
        invalid_prompt = {"template": ""}  # Missing required fields

        is_valid, errors = optimizer.validate_prompt(invalid_prompt)
        assert is_valid is False
        assert len(errors) > 0

    def test_prompt_scoring(self, optimizer, sample_prompt):
        """Test prompt quality scoring"""
        score = optimizer.score_prompt(sample_prompt)

        assert 0 <= score["clarity"] <= 1
        assert 0 <= score["specificity"] <= 1
        assert 0 <= score["overall"] <= 1

    def test_iterative_refinement(self, optimizer):
        """Test iterative prompt refinement"""
        initial_prompt = "Write code"

        refined = optimizer.iterative_refine(initial_prompt, iterations=3)

        assert len(refined["history"]) == 3
        assert refined["final_prompt"] != initial_prompt
        assert refined["improvement_rate"] > 0

    def test_prompt_versioning(self, optimizer, sample_prompt):
        """Test prompt versioning"""
        version_id = optimizer.save_version(sample_prompt, "v1.0")

        retrieved = optimizer.get_version(version_id)
        assert retrieved == sample_prompt

        versions = optimizer.list_versions()
        assert len(versions) >= 1

    def test_a_b_testing_setup(self, optimizer):
        """Test A/B testing setup for prompts"""
        variant_a = "Be concise: {task}"
        variant_b = "Provide detailed explanation: {task}"

        test_config = optimizer.setup_ab_test(variant_a, variant_b)

        assert "test_id" in test_config
        assert "variants" in test_config
        assert len(test_config["variants"]) == 2

    def test_token_optimization(self, optimizer):
        """Test token usage optimization"""
        verbose_prompt = """
        Please, if you would be so kind, I would really appreciate it if you could
        potentially help me with generating some code that might possibly work
        """

        optimized = optimizer.optimize_tokens(verbose_prompt)

        assert len(optimized) < len(verbose_prompt)
        assert optimizer.count_tokens(optimized) < optimizer.count_tokens(verbose_prompt)

    def test_safety_check(self, optimizer):
        """Test safety and compliance checking"""
        unsafe_prompt = "How to hack into systems"
        safe_prompt = "How to secure systems"

        assert optimizer.is_safe(unsafe_prompt) is False
        assert optimizer.is_safe(safe_prompt) is True

    def test_performance_metrics(self, optimizer):
        """Test performance metrics collection"""
        optimizer.optimize({"template": "test", "variables": {}})

        metrics = optimizer.get_metrics()
        assert "total_optimizations" in metrics
        assert "average_improvement" in metrics
        assert metrics["total_optimizations"] >= 1
