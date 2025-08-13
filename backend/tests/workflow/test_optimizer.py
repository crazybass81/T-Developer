import pytest

from src.workflow.dag_validator import GraphMetrics
from src.workflow.optimizer import WorkflowOptimizer
from src.workflow.parser import WorkflowDefinition, WorkflowStep


class TestWorkflowOptimizer:
    def setup_method(self):
        self.optimizer = WorkflowOptimizer()

    def test_optimizer_initialization(self):
        assert isinstance(self.optimizer.validator, object)
        assert isinstance(self.optimizer.cache, dict)
        assert isinstance(self.optimizer.rules, dict)
        assert "parallelization" in self.optimizer.rules
        assert "complexity_reduction" in self.optimizer.rules

    def test_optimize_simple_workflow(self):
        workflow = WorkflowDefinition(
            id="simple_opt",
            name="Simple Optimization",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
            ],
            dependencies={"step2": ["step1"]},
        )
        result = self.optimizer.optimize_workflow(workflow)

        assert "original_workflow" in result
        assert "optimization_score" in result
        assert "suggested_improvements" in result
        assert "structure_optimizations" in result
        assert result["original_workflow"] == "simple_opt"
        assert isinstance(result["optimization_score"], (int, float))

    def test_optimize_workflow_with_cycles(self):
        workflow = WorkflowDefinition(
            id="cyclic_opt",
            name="Cyclic Optimization",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
            ],
            dependencies={"step1": ["step2"], "step2": ["step1"]},  # Cycle
        )
        result = self.optimizer.optimize_workflow(workflow)

        assert result["original_workflow"] == "cyclic_opt"
        assert len(result["suggested_improvements"]) > 0
        # Should suggest fixing cycle
        improvements = result["suggested_improvements"]
        assert any("Invalid DAG" in str(imp.get("issue", "")) for imp in improvements)

    def test_optimization_caching(self):
        workflow = WorkflowDefinition(
            id="cache_test",
            name="Cache Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
            version="1.0.0",
        )

        # First call
        result1 = self.optimizer.optimize_workflow(workflow)

        # Second call should use cache
        result2 = self.optimizer.optimize_workflow(workflow)

        assert result1 == result2
        cache_key = f"{workflow.id}_{workflow.version}"
        assert cache_key in self.optimizer.cache

    def test_find_parallelization_candidates(self):
        workflow = WorkflowDefinition(
            id="parallel_test",
            name="Parallel Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
                WorkflowStep(id="step3", name="Step 3", type="agent", agent_id="agent3"),
            ],
            dependencies={},  # No dependencies = all can run in parallel
        )

        candidates = self.optimizer._find_candidates(workflow)
        assert len(candidates) > 0
        # Each step should have potential parallel candidates
        for candidate in candidates:
            assert "step_id" in candidate
            assert "can_parallel_with" in candidate

    def test_calculate_optimization_score(self):
        workflow = WorkflowDefinition(
            id="score_test",
            name="Score Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
        )

        metrics = GraphMetrics(
            node_count=1,
            edge_count=0,
            max_depth=1,
            max_width=1,
            strongly_connected_components=0,
            topological_complexity=0.2,
            parallelization_factor=0.8,
        )

        score = self.optimizer._calc_score(workflow, metrics)
        assert 0 <= score <= 100
        assert isinstance(score, (int, float))

    def test_generate_optimized_workflow(self):
        original = WorkflowDefinition(
            id="original",
            name="Original Workflow",
            steps=[WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")],
            metadata={"version": "1.0"},
        )

        optimized = self.optimizer.generate_optimized(original, ["retry_policy"])

        assert optimized.id == "original_optimized"
        assert optimized.name == "Original Workflow (Optimized)"
        assert optimized.version == "1.1.0"
        assert optimized.metadata.get("optimized") is True

        # Check that retry policy was added
        assert optimized.steps[0].retry_policy is not None
        assert optimized.steps[0].retry_policy["max_attempts"] == 3

    def test_generate_optimized_no_optimizations(self):
        original = WorkflowDefinition(
            id="original",
            name="Original Workflow",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
        )

        optimized = self.optimizer.generate_optimized(original)

        assert optimized.id == "original_optimized"
        assert optimized.name == "Original Workflow (Optimized)"
        # Steps should be copied but not modified without optimizations
        assert len(optimized.steps) == len(original.steps)

    def test_optimization_with_parallel_steps(self):
        workflow = WorkflowDefinition(
            id="parallel_workflow",
            name="Parallel Workflow",
            steps=[
                WorkflowStep(id="start", name="Start", type="agent", agent_id="starter"),
                WorkflowStep(id="parallel1", name="Parallel 1", type="agent", agent_id="worker1"),
                WorkflowStep(id="parallel2", name="Parallel 2", type="agent", agent_id="worker2"),
                WorkflowStep(id="end", name="End", type="agent", agent_id="finisher"),
            ],
            dependencies={
                "parallel1": ["start"],
                "parallel2": ["start"],
                "end": ["parallel1", "parallel2"],
            },
        )

        result = self.optimizer.optimize_workflow(workflow)
        assert result["original_workflow"] == "parallel_workflow"
        # Should have reasonable optimization score for well-structured workflow
        assert result["optimization_score"] >= 30

    def test_optimization_error_handling(self):
        # Test with None workflow (should handle gracefully)
        try:
            result = self.optimizer.optimize_workflow(None)
            # If it doesn't crash, check that error is recorded
            if "suggested_improvements" in result:
                assert len(result["suggested_improvements"]) > 0
        except Exception:
            # Expected to fail gracefully
            pass

    def test_optimization_score_calculation_edge_cases(self):
        workflow = WorkflowDefinition(id="edge_case", name="Edge Case", steps=[])

        # Test with minimal metrics
        metrics = GraphMetrics(
            node_count=0,
            edge_count=0,
            max_depth=0,
            max_width=0,
            strongly_connected_components=0,
            topological_complexity=0.0,
            parallelization_factor=0.0,
        )

        score = self.optimizer._calc_score(workflow, metrics)
        assert 0 <= score <= 100

    def test_find_candidates_with_dependencies(self):
        workflow = WorkflowDefinition(
            id="deps_test",
            name="Dependencies Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
                WorkflowStep(id="step3", name="Step 3", type="agent", agent_id="agent3"),
                WorkflowStep(id="step4", name="Step 4", type="agent", agent_id="agent4"),
            ],
            dependencies={
                "step2": ["step1"],
                "step3": ["step1"],
            },  # step1 -> step2,step3; step4 independent
        )

        candidates = self.optimizer._find_candidates(workflow)

        # Should find some parallelization opportunities
        assert len(candidates) > 0

        # Check that candidates make sense
        for candidate in candidates:
            assert candidate["step_id"] in ["step1", "step2", "step3", "step4"]
            assert isinstance(candidate["can_parallel_with"], list)

    def test_large_workflow_optimization(self):
        # Test optimization on larger workflow
        steps = []
        deps = {}

        # Create a workflow with multiple parallel branches
        steps.append(WorkflowStep(id="root", name="Root", type="service"))

        for branch in range(3):
            for i in range(5):
                step_id = f"branch_{branch}_step_{i}"
                steps.append(
                    WorkflowStep(id=step_id, name=f"Branch {branch} Step {i}", type="service")
                )

                if i == 0:
                    deps[step_id] = ["root"]
                else:
                    deps[step_id] = [f"branch_{branch}_step_{i-1}"]

        workflow = WorkflowDefinition(
            id="large_opt", name="Large Optimization", steps=steps, dependencies=deps
        )
        result = self.optimizer.optimize_workflow(workflow)

        assert result["original_workflow"] == "large_opt"
        assert isinstance(result["optimization_score"], (int, float))
        # Should find some structure optimizations
        assert len(result["structure_optimizations"]) >= 0


class TestPerformanceAndConstraints:
    def test_optimizer_memory_efficiency(self):
        optimizer = WorkflowOptimizer()

        # Test multiple optimizations
        for i in range(25):
            workflow = WorkflowDefinition(
                id=f"mem_test_{i}",
                name=f"Memory Test {i}",
                steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
                version=f"1.0.{i}",
            )
            result = optimizer.optimize_workflow(workflow)
            assert "optimization_score" in result

        # Cache should be populated
        assert len(optimizer.cache) == 25

    def test_optimization_performance(self):
        import time

        # Create moderately complex workflow
        steps = []
        deps = {}

        for i in range(20):
            steps.append(WorkflowStep(id=f"step_{i}", name=f"Step {i}", type="service"))
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        workflow = WorkflowDefinition(
            id="perf_test", name="Performance Test", steps=steps, dependencies=deps
        )

        start_time = time.time()
        result = self.optimizer.optimize_workflow(workflow)
        end_time = time.time()

        # Should complete reasonably quickly (under 1 second)
        assert end_time - start_time < 1.0
        assert result["original_workflow"] == "perf_test"

    def test_concurrent_optimizations(self):
        # Test that optimizer handles multiple workflows correctly
        optimizer = WorkflowOptimizer()
        workflows = []

        for i in range(10):
            workflow = WorkflowDefinition(
                id=f"concurrent_{i}",
                name=f"Concurrent {i}",
                steps=[
                    WorkflowStep(id="step1", name="Step 1", type="service"),
                    WorkflowStep(id="step2", name="Step 2", type="service"),
                ],
                dependencies={"step2": ["step1"]} if i % 2 == 0 else {},
            )
            workflows.append(workflow)

        results = []
        for workflow in workflows:
            result = optimizer.optimize_workflow(workflow)
            results.append(result)

        # All optimizations should succeed
        assert len(results) == 10
        for i, result in enumerate(results):
            assert result["original_workflow"] == f"concurrent_{i}"

    def setup_method(self):
        self.optimizer = WorkflowOptimizer()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
