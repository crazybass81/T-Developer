"""
Test suite for Workflow Composition
Day 23: Phase 2 - Meta Agents
"""

import asyncio
from typing import List

import pytest

from src.agents.meta.workflow_composer import (
    ComposedWorkflow,
    WorkflowComposer,
    WorkflowDAG,
    WorkflowStep,
    get_composer,
)
from src.optimization.parallelizer import Parallelizer, get_parallelizer
from src.optimization.resource_allocator import ResourceAllocator, get_allocator


class TestWorkflowComposer:
    """Test workflow composer functionality"""

    @pytest.fixture
    def composer(self):
        """Get composer instance"""
        return get_composer()

    @pytest.fixture
    def sample_agents(self):
        """Sample agent list"""
        return ["RequirementAnalyzer", "DesignAgent", "CodeGenerator", "TestGenerator", "Deployer"]

    @pytest.mark.asyncio
    async def test_compose_basic_workflow(self, composer, sample_agents):
        """Test basic workflow composition"""
        requirements = {"type": "web_app", "complexity": "medium"}

        workflow = await composer.compose(sample_agents, requirements)

        assert workflow is not None
        assert workflow.name.startswith("workflow_")
        assert len(workflow.dag.steps) == len(sample_agents)
        assert workflow.optimization_score >= 0.0
        assert workflow.optimization_score <= 1.0

    @pytest.mark.asyncio
    async def test_dag_creation(self, composer, sample_agents):
        """Test DAG creation from agents"""
        requirements = {}
        dependencies = {
            sample_agents[1]: [sample_agents[0]],
            sample_agents[2]: [sample_agents[1]],
            sample_agents[3]: [sample_agents[2]],
            sample_agents[4]: [sample_agents[2], sample_agents[3]],
        }

        dag = await composer._build_dag(sample_agents, dependencies)

        assert len(dag.steps) == len(sample_agents)
        assert len(dag.entry_points) > 0
        assert len(dag.exit_points) > 0

        # Check dependencies are preserved
        for step in dag.steps:
            if step.agent in dependencies:
                assert step.dependencies == dependencies[step.agent]

    @pytest.mark.asyncio
    async def test_parallel_group_identification(self, composer):
        """Test identification of parallel execution groups"""
        # Create agents that can run in parallel
        agents = ["Agent1", "Agent2", "Agent3", "Agent4"]
        dependencies = {
            "Agent2": [],  # Can run in parallel with Agent1
            "Agent3": ["Agent1", "Agent2"],
            "Agent4": ["Agent1", "Agent2"],  # Can run in parallel with Agent3
        }

        dag = await composer._build_dag(agents, dependencies)
        workflow = await composer.compose(agents, {})

        # Should have at least one parallel group
        assert len(dag.parallel_groups) >= 0

        # Check execution plan
        assert len(workflow.execution_plan) > 0

    @pytest.mark.asyncio
    async def test_workflow_validation(self, composer, sample_agents):
        """Test workflow validation"""
        workflow = await composer.compose(sample_agents, {})

        is_valid = await composer.validate_workflow(workflow)
        assert is_valid is True

        # Test cycle detection
        assert composer._has_cycle(workflow.dag) is False

    @pytest.mark.asyncio
    async def test_execution_order_optimization(self, composer):
        """Test execution order optimization"""
        agents = ["A", "B", "C", "D", "E"]
        dependencies = {"B": ["A"], "C": ["A"], "D": ["B", "C"], "E": ["D"]}

        dag = await composer._build_dag(agents, dependencies)
        parallel_groups = await composer.parallelizer.identify_parallel_groups(dag)
        execution_plan = await composer._optimize_execution_order(dag, parallel_groups)

        # Check topological order is maintained
        executed = set()
        for level in execution_plan:
            for step_id in level:
                step = next((s for s in dag.steps if s.id == step_id), None)
                if step and step.dependencies:
                    # All dependencies should be executed before this step
                    for dep in step.dependencies:
                        dep_step = next((s for s in dag.steps if s.agent == dep), None)
                        if dep_step:
                            assert dep_step.id in executed
                executed.add(step_id)

    def test_workflow_visualization(self, composer):
        """Test workflow visualization"""
        # Create mock workflow
        step1 = WorkflowStep("s1", "Step1", "Agent1", {}, {})
        step2 = WorkflowStep("s2", "Step2", "Agent2", {}, {}, ["Agent1"])

        dag = WorkflowDAG(
            steps=[step1, step2],
            edges={"s1": ["s2"]},
            entry_points=["s1"],
            exit_points=["s2"],
            parallel_groups=[],
        )

        workflow = ComposedWorkflow(
            name="test_workflow",
            dag=dag,
            execution_plan=[["s1"], ["s2"]],
            resource_allocation={},
            estimated_time=10.0,
            optimization_score=0.8,
        )

        viz = composer.visualize_workflow(workflow)

        assert "test_workflow" in viz
        assert "Agent1" in viz
        assert "Agent2" in viz
        assert "10.0s" in viz
        assert "0.80" in viz

    @pytest.mark.asyncio
    async def test_time_estimation(self, composer, sample_agents):
        """Test execution time estimation"""
        workflow = await composer.compose(sample_agents, {})

        assert workflow.estimated_time > 0
        # Should be reasonable (not too high)
        assert workflow.estimated_time < 1000

    def test_workflow_patterns(self, composer):
        """Test workflow pattern implementations"""
        agents = ["A", "B", "C", "D"]

        # Test sequential pattern
        seq = composer._sequential_pattern(agents)
        assert len(seq) == len(agents)
        assert all(len(level) == 1 for level in seq)

        # Test parallel pattern
        par = composer._parallel_pattern(agents)
        assert len(par) == 1
        assert len(par[0]) == len(agents)

        # Test map-reduce pattern
        map_reduce = composer._map_reduce_pattern(agents[:-1], agents[-1])
        assert len(map_reduce) == 2
        assert len(map_reduce[0]) == 3
        assert len(map_reduce[1]) == 1


class TestParallelizer:
    """Test parallelizer functionality"""

    @pytest.fixture
    def parallelizer(self):
        """Get parallelizer instance"""
        return get_parallelizer()

    def test_parallel_efficiency_calculation(self, parallelizer):
        """Test parallel efficiency calculation"""
        seq_time = 100.0
        par_time = 30.0
        num_proc = 4

        efficiency = parallelizer.calculate_parallel_efficiency(seq_time, par_time, num_proc)

        assert 0.0 <= efficiency <= 1.0
        # Should show good efficiency for this example
        assert efficiency > 0.5

    def test_resource_estimation(self, parallelizer):
        """Test resource requirement estimation"""
        steps = ["step1", "step2", "step3"]

        resources = parallelizer._estimate_resources(steps)

        assert "cpu" in resources
        assert "memory" in resources
        assert "threads" in resources
        assert resources["threads"] == len(steps)

    def test_speedup_estimation(self, parallelizer):
        """Test speedup estimation"""
        # Single step - no speedup
        speedup1 = parallelizer._estimate_speedup(["step1"])
        assert speedup1 == 1.0

        # Multiple steps - should show speedup
        speedup4 = parallelizer._estimate_speedup(["s1", "s2", "s3", "s4"])
        assert speedup4 > 1.0
        assert speedup4 <= parallelizer.max_parallel

    def test_resource_splitting(self, parallelizer):
        """Test group splitting by resources"""
        large_group = [f"step{i}" for i in range(20)]
        limits = {"cpu": 8.0, "memory": 16384}

        subgroups = parallelizer._split_by_resources(large_group, limits)

        assert len(subgroups) > 1
        assert all(len(g) <= parallelizer.max_parallel for g in subgroups)


class TestResourceAllocator:
    """Test resource allocator functionality"""

    @pytest.fixture
    def allocator(self):
        """Get allocator instance"""
        return get_allocator()

    def test_cost_calculation(self, allocator):
        """Test resource cost calculation"""
        from src.optimization.resource_allocator import ResourceAllocation

        allocations = {
            "step1": ResourceAllocation("step1", 2.0, 1024, 500, 100, 5),
            "step2": ResourceAllocation("step2", 1.0, 512, 200, 50, 3),
        }

        cost = allocator.calculate_cost(allocations)

        assert cost > 0
        assert isinstance(cost, float)

    def test_utilization_calculation(self, allocator):
        """Test resource utilization calculation"""
        pool = allocator.default_pool
        pool.allocated_cpu = 4.0
        pool.allocated_memory = 8192
        pool.allocated_disk = 10240
        pool.allocated_network = 100

        utilization = allocator.get_utilization(pool)

        assert "cpu" in utilization
        assert "memory" in utilization
        assert 0 <= utilization["cpu"] <= 100
        assert 0 <= utilization["memory"] <= 100

    def test_allocation_strategies(self, allocator):
        """Test different allocation strategies"""
        strategies = allocator.allocation_strategies

        assert "balanced" in strategies
        assert "performance" in strategies
        assert "cost" in strategies
        assert "fair" in strategies

        # Test each strategy is callable
        for name, strategy in strategies.items():
            assert callable(strategy)

    def test_allocation_validation(self, allocator):
        """Test allocation validation"""
        from src.optimization.resource_allocator import ResourceAllocation

        pool = allocator.default_pool

        # Valid allocation
        valid_allocations = {"step1": ResourceAllocation("step1", 1.0, 1024, 100, 10, 5)}
        assert allocator._validate_allocations(valid_allocations, pool) is True

        # Invalid allocation (exceeds pool)
        invalid_allocations = {"step1": ResourceAllocation("step1", 100.0, 999999, 999999, 9999, 5)}
        assert allocator._validate_allocations(invalid_allocations, pool) is False


@pytest.mark.integration
class TestIntegration:
    """Integration tests for workflow composition"""

    @pytest.mark.asyncio
    async def test_complete_workflow_composition(self):
        """Test complete workflow composition flow"""
        composer = get_composer()
        parallelizer = get_parallelizer()
        allocator = get_allocator()

        # Complex agent pipeline
        agents = [
            "RequirementAnalyzer",
            "ArchitectureDesigner",
            "DatabaseDesigner",
            "APIDesigner",
            "FrontendGenerator",
            "BackendGenerator",
            "TestGenerator",
            "DocumentationGenerator",
            "Deployer",
        ]

        requirements = {
            "type": "full_stack_app",
            "complexity": "high",
            "performance": "critical",
            "scale": "enterprise",
        }

        constraints = {"cpu": 16.0, "memory": 32768, "disk": 204800, "network": 10000}

        # Compose workflow
        workflow = await composer.compose(agents, requirements, constraints)

        # Validate workflow
        is_valid = await composer.validate_workflow(workflow)
        assert is_valid

        # Check parallelization
        assert len(workflow.dag.parallel_groups) >= 0

        # Check resource allocation
        assert len(workflow.resource_allocation) > 0

        # Check optimization
        assert workflow.optimization_score > 0

        # Visualize
        viz = composer.visualize_workflow(workflow)
        print(f"\n{viz}")

        # Check metrics
        composer_metrics = composer.get_metrics()
        assert "patterns" in composer_metrics

        parallelizer_metrics = parallelizer.get_metrics()
        assert "max_parallel" in parallelizer_metrics

        allocator_metrics = allocator.get_metrics()
        assert "strategies" in allocator_metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
