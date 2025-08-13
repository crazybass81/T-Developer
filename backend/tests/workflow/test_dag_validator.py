import pytest

from src.workflow.dag_validator import CycleInfo, DAGValidator, GraphMetrics
from src.workflow.parser import WorkflowDefinition, WorkflowStep


class TestDAGValidator:
    def setup_method(self):
        self.validator = DAGValidator()

    def test_validator_initialization(self):
        assert isinstance(self.validator.cache, dict)

    def test_valid_dag_simple(self):
        workflow = WorkflowDefinition(
            id="simple_dag",
            name="Simple DAG",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
            ],
            dependencies={"step2": ["step1"]},
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is True
        assert len(result["cycles_detected"]) == 0

    def test_invalid_dag_with_cycle(self):
        workflow = WorkflowDefinition(
            id="cyclic_dag",
            name="Cyclic DAG",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
            ],
            dependencies={"step1": ["step2"], "step2": ["step1"]},  # Cycle
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is False
        assert len(result["cycles_detected"]) > 0

    def test_self_loop_detection(self):
        workflow = WorkflowDefinition(
            id="self_loop",
            name="Self Loop",
            steps=[WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")],
            dependencies={"step1": ["step1"]},  # Self loop
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is False
        cycles = result["cycles_detected"]
        assert len(cycles) > 0

    def test_complex_cycle_detection(self):
        workflow = WorkflowDefinition(
            id="complex_cycle",
            name="Complex Cycle",
            steps=[
                WorkflowStep(id="a", name="Step A", type="agent", agent_id="agent1"),
                WorkflowStep(id="b", name="Step B", type="agent", agent_id="agent2"),
                WorkflowStep(id="c", name="Step C", type="agent", agent_id="agent3"),
            ],
            dependencies={"b": ["a"], "c": ["b"], "a": ["c"]},  # A->B->C->A cycle
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is False
        assert len(result["cycles_detected"]) > 0

    def test_build_dependency_graph(self):
        workflow = WorkflowDefinition(
            id="graph_test",
            name="Graph Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="step2", name="Step 2", type="agent", agent_id="agent2"),
            ],
            dependencies={"step2": ["step1"]},
        )
        graph = self.validator._build_graph(workflow)
        assert "step1" in graph
        assert "step2" in graph
        assert "step2" in graph["step1"]

    def test_build_graph_with_io_dependencies(self):
        workflow = WorkflowDefinition(
            id="io_deps",
            name="IO Dependencies",
            steps=[
                WorkflowStep(
                    id="producer",
                    name="Producer",
                    type="agent",
                    agent_id="agent1",
                    outputs=["data"],
                ),
                WorkflowStep(
                    id="consumer", name="Consumer", type="agent", agent_id="agent2", inputs=["data"]
                ),
            ],
        )
        graph = self.validator._build_graph(workflow)
        assert "consumer" in graph["producer"]  # Implicit dependency from I/O

    def test_calculate_graph_metrics(self):
        workflow = WorkflowDefinition(
            id="metrics_test",
            name="Metrics Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
            ],
            dependencies={"step2": ["step1"], "step3": ["step2"]},
        )
        result = self.validator.validate_dag(workflow)
        metrics = result["graph_metrics"]
        assert "node_count" in metrics
        assert "edge_count" in metrics
        assert "max_depth" in metrics
        assert "max_width" in metrics
        assert metrics["node_count"] == 3

    def test_max_depth_calculation(self):
        workflow = WorkflowDefinition(
            id="depth_test",
            name="Depth Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
            ],
            dependencies={"step2": ["step1"], "step3": ["step2"]},  # Chain of 3
        )
        graph = self.validator._build_graph(workflow)
        depth = self.validator._max_depth(graph)
        assert depth == 3

    def test_max_width_calculation(self):
        workflow = WorkflowDefinition(
            id="width_test",
            name="Width Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
                WorkflowStep(id="step4", name="Step 4", type="service"),
            ],
            dependencies={"step3": ["step1"], "step4": ["step2"]},  # 2 parallel chains
        )
        graph = self.validator._build_graph(workflow)
        width = self.validator._max_width(graph)
        assert width >= 2  # At least 2 parallel steps

    def test_execution_order_simple(self):
        workflow = WorkflowDefinition(
            id="order_test",
            name="Order Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
            ],
            dependencies={"step2": ["step1"], "step3": ["step2"]},
        )
        order = self.validator.get_execution_order(workflow)
        assert len(order) == 3  # 3 levels
        assert order[0] == ["step1"]
        assert order[1] == ["step2"]
        assert order[2] == ["step3"]

    def test_execution_order_parallel(self):
        workflow = WorkflowDefinition(
            id="parallel_order",
            name="Parallel Order",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
                WorkflowStep(id="step3", name="Step 3", type="service"),
            ],
            dependencies={"step2": ["step1"], "step3": ["step1"]},  # step1 -> step2,step3
        )
        order = self.validator.get_execution_order(workflow)
        assert len(order) == 2  # 2 levels
        assert order[0] == ["step1"]
        assert sorted(order[1]) == ["step2", "step3"]  # Parallel execution

    def test_no_cycles_in_valid_dag(self):
        workflow = WorkflowDefinition(
            id="no_cycles",
            name="No Cycles",
            steps=[
                WorkflowStep(id="a", name="A", type="service"),
                WorkflowStep(id="b", name="B", type="service"),
                WorkflowStep(id="c", name="C", type="service"),
                WorkflowStep(id="d", name="D", type="service"),
            ],
            dependencies={"b": ["a"], "c": ["a"], "d": ["b", "c"]},  # Diamond pattern
        )
        graph = self.validator._build_graph(workflow)
        cycles = self.validator._detect_cycles(graph)
        assert len(cycles) == 0

    def test_cycle_detection_performance(self):
        # Test cycle detection on larger graph
        steps = []
        deps = {}
        for i in range(20):
            steps.append(WorkflowStep(id=f"step_{i}", name=f"Step {i}", type="service"))
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        workflow = WorkflowDefinition(
            id="large_dag", name="Large DAG", steps=steps, dependencies=deps
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is True
        assert len(result["cycles_detected"]) == 0

    def test_caching_behavior(self):
        workflow = WorkflowDefinition(
            id="cache_test",
            name="Cache Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
            version="1.0.0",
        )

        # First call should compute
        result1 = self.validator.validate_dag(workflow)

        # Second call should use cache
        result2 = self.validator.validate_dag(workflow)

        assert result1 == result2
        cache_key = f"{workflow.id}_{workflow.version}"
        assert cache_key in self.validator.cache

    def test_empty_workflow(self):
        workflow = WorkflowDefinition(id="empty", name="Empty", steps=[])
        result = self.validator.validate_dag(workflow)
        # Should not crash on empty workflow
        assert "is_valid_dag" in result

    def test_single_step_workflow(self):
        workflow = WorkflowDefinition(
            id="single",
            name="Single Step",
            steps=[WorkflowStep(id="only", name="Only Step", type="service")],
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is True
        assert len(result["cycles_detected"]) == 0

    def test_disconnected_components(self):
        workflow = WorkflowDefinition(
            id="disconnected",
            name="Disconnected Components",
            steps=[
                WorkflowStep(id="a", name="A", type="service"),
                WorkflowStep(id="b", name="B", type="service"),
                WorkflowStep(id="c", name="C", type="service"),
                WorkflowStep(id="d", name="D", type="service"),
            ],
            dependencies={"b": ["a"], "d": ["c"]},  # Two separate chains
        )
        result = self.validator.validate_dag(workflow)
        assert result["is_valid_dag"] is True


class TestCycleInfo:
    def test_cycle_info_creation(self):
        cycle = CycleInfo(
            cycle_nodes=["a", "b", "c"],
            cycle_edges=[("a", "b"), ("b", "c"), ("c", "a")],
            cycle_length=3,
            cycle_type="complex",
        )
        assert cycle.cycle_nodes == ["a", "b", "c"]
        assert len(cycle.cycle_edges) == 3
        assert cycle.cycle_length == 3
        assert cycle.cycle_type == "complex"


class TestGraphMetrics:
    def test_graph_metrics_creation(self):
        metrics = GraphMetrics(
            node_count=5,
            edge_count=4,
            max_depth=3,
            max_width=2,
            strongly_connected_components=0,
            topological_complexity=0.4,
            parallelization_factor=0.6,
        )
        assert metrics.node_count == 5
        assert metrics.edge_count == 4
        assert metrics.max_depth == 3
        assert metrics.max_width == 2
        assert metrics.strongly_connected_components == 0
        assert metrics.topological_complexity == 0.4
        assert metrics.parallelization_factor == 0.6


class TestPerformanceAndConstraints:
    def test_validator_memory_efficiency(self):
        validator = DAGValidator()

        # Test with multiple workflow validations
        for i in range(50):
            workflow = WorkflowDefinition(
                id=f"wf_{i}",
                name=f"Workflow {i}",
                steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
                version=f"1.0.{i}",
            )
            result = validator.validate_dag(workflow)
            assert result["is_valid_dag"] is True

        # Cache should contain all results
        assert len(validator.cache) == 50

    def test_large_dag_validation(self):
        # Test with larger workflow (100 steps)
        validator = DAGValidator()
        steps = []
        deps = {}

        # Create linear chain
        for i in range(100):
            steps.append(WorkflowStep(id=f"step_{i}", name=f"Step {i}", type="service"))
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        workflow = WorkflowDefinition(
            id="large_dag", name="Large DAG", steps=steps, dependencies=deps
        )
        result = validator.validate_dag(workflow)

        assert result["is_valid_dag"] is True
        assert result["graph_metrics"]["node_count"] == 100
        assert result["graph_metrics"]["max_depth"] == 100

    def test_wide_dag_validation(self):
        # Test with wide workflow (50 parallel steps)
        validator = DAGValidator()
        steps = []
        deps = {}

        # Create start and end nodes
        steps.append(WorkflowStep(id="start", name="Start", type="service"))
        steps.append(WorkflowStep(id="end", name="End", type="service"))

        # Create 50 parallel middle steps
        for i in range(50):
            step_id = f"parallel_{i}"
            steps.append(WorkflowStep(id=step_id, name=f"Parallel {i}", type="service"))
            deps[step_id] = ["start"]
            if "end" not in deps:
                deps["end"] = []
            deps["end"].append(step_id)

        workflow = WorkflowDefinition(
            id="wide_dag", name="Wide DAG", steps=steps, dependencies=deps
        )
        result = validator.validate_dag(workflow)

        assert result["is_valid_dag"] is True
        assert result["graph_metrics"]["node_count"] == 52
        assert result["graph_metrics"]["max_width"] >= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
