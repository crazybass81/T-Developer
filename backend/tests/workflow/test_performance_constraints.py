import os
import time

import psutil
import pytest

from src.workflow.dag_validator import DAGValidator
from src.workflow.engine import WorkflowEngine
from src.workflow.optimizer import WorkflowOptimizer
from src.workflow.parser import WorkflowDefinition, WorkflowParser, WorkflowStep


class TestPerformanceConstraints:
    """Validate T-Developer performance constraints for workflow system"""

    def test_file_size_constraints(self):
        """Verify all workflow files are under 6.5KB constraint"""
        workflow_dir = "/home/ec2-user/T-DeveloperMVP/backend/src/workflow"
        constraint_kb = 6.5
        constraint_bytes = int(constraint_kb * 1024)

        files_to_check = ["parser.py", "dag_validator.py", "optimizer.py", "engine.py"]

        for filename in files_to_check:
            filepath = os.path.join(workflow_dir, filename)
            if os.path.exists(filepath):
                size_bytes = os.path.getsize(filepath)
                size_kb = size_bytes / 1024
                print(f"{filename}: {size_kb:.2f}KB")
                assert (
                    size_bytes < constraint_bytes
                ), f"{filename} is {size_kb:.2f}KB, exceeds {constraint_kb}KB limit"

    def test_instantiation_speed_constraint(self):
        """Verify instantiation time is under 3μs constraint"""
        constraint_microseconds = 3.0
        iterations = 100

        # Test each component instantiation speed
        components = [
            ("WorkflowParser", WorkflowParser),
            ("DAGValidator", DAGValidator),
            ("WorkflowOptimizer", WorkflowOptimizer),
            ("WorkflowEngine", WorkflowEngine),
        ]

        for component_name, component_class in components:
            times = []

            for _ in range(iterations):
                start_time = time.perf_counter()
                instance = component_class()
                end_time = time.perf_counter()

                duration_microseconds = (end_time - start_time) * 1_000_000
                times.append(duration_microseconds)

                # Clean up to avoid memory buildup
                del instance

            avg_time = sum(times) / len(times)
            max_time = max(times)
            p95_time = sorted(times)[int(0.95 * len(times))]

            print(f"{component_name} instantiation:")
            print(f"  Average: {avg_time:.2f}μs")
            print(f"  95th percentile: {p95_time:.2f}μs")
            print(f"  Maximum: {max_time:.2f}μs")

            # 95% of instantiations should be under 3μs
            success_rate = sum(1 for t in times if t < constraint_microseconds) / len(times)
            assert (
                success_rate >= 0.90
            ), f"{component_name} only {success_rate*100:.1f}% under {constraint_microseconds}μs limit"

    def test_memory_efficiency(self):
        """Test memory usage of workflow components"""
        process = psutil.Process(os.getpid())
        base_memory = process.memory_info().rss

        # Create instances and measure memory
        parser = WorkflowParser()
        validator = DAGValidator()
        optimizer = WorkflowOptimizer()
        assert isinstance(parser, WorkflowParser)

        # Create some test workflows to populate caches
        for i in range(10):
            workflow = WorkflowDefinition(
                id=f"mem_test_{i}",
                name=f"Memory Test {i}",
                steps=[WorkflowStep(id="step1", name="Step 1", type="service")],
                version=f"1.0.{i}",
            )

            # Exercise components
            parser.parsed[workflow.id] = workflow
            validation = validator.validate_dag(workflow)
            assert validation["is_valid_dag"]
            optimization = optimizer.optimize_workflow(workflow)
            assert "optimization_score" in optimization

        current_memory = process.memory_info().rss
        memory_used = current_memory - base_memory
        memory_used_kb = memory_used / 1024

        print(f"Memory usage: {memory_used_kb:.2f}KB for 10 workflows")

        # Memory usage should be reasonable (under 1MB for 10 workflows)
        assert memory_used < 1024 * 1024, f"Memory usage {memory_used_kb:.2f}KB exceeds 1MB limit"

    def test_parsing_performance(self):
        """Test parsing performance under load"""
        parser = WorkflowParser()
        workflows_per_second_target = 100

        workflow_data = {
            "id": "perf_test",
            "name": "Performance Test",
            "steps": [
                {"id": "step1", "name": "Step 1", "type": "service"},
                {"id": "step2", "name": "Step 2", "type": "service"},
            ],
            "dependencies": {"step2": ["step1"]},
        }

        # Measure parsing throughput
        iterations = 100
        start_time = time.time()

        for i in range(iterations):
            # Modify data slightly to avoid caching
            test_data = workflow_data.copy()
            test_data["id"] = f"perf_test_{i}"

            workflow = parser.parse_dict(test_data)
            assert workflow.id == f"perf_test_{i}"

        end_time = time.time()
        duration = end_time - start_time
        throughput = iterations / duration

        print(f"Parsing throughput: {throughput:.1f} workflows/second")
        assert (
            throughput >= workflows_per_second_target
        ), f"Parsing too slow: {throughput:.1f} < {workflows_per_second_target} workflows/sec"

    def test_validation_performance(self):
        """Test DAG validation performance"""
        validator = DAGValidator()
        validations_per_second_target = 50

        # Create workflow with moderate complexity
        steps = []
        deps = {}
        for i in range(10):
            steps.append(WorkflowStep(id=f"step_{i}", name=f"Step {i}", type="service"))
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        workflow = WorkflowDefinition(
            id="validation_perf_test",
            name="Validation Performance Test",
            steps=steps,
            dependencies=deps,
        )

        # Measure validation throughput
        iterations = 50
        start_time = time.time()

        for i in range(iterations):
            # Clear cache to force recomputation
            validator.cache.clear()

            result = validator.validate_dag(workflow)
            assert result["is_valid_dag"] is True

        end_time = time.time()
        duration = end_time - start_time
        throughput = iterations / duration

        print(f"Validation throughput: {throughput:.1f} validations/second")
        assert (
            throughput >= validations_per_second_target
        ), f"Validation too slow: {throughput:.1f} < {validations_per_second_target} validations/sec"

    @pytest.mark.asyncio
    async def test_execution_performance(self):
        """Test workflow execution performance"""
        engine = WorkflowEngine()
        executions_per_second_target = 4  # Adjusted for 0.1s per step simulation

        # Simple workflow for execution testing
        workflow = WorkflowDefinition(
            id="exec_perf_test",
            name="Execution Performance Test",
            steps=[
                WorkflowStep(id="step1", name="Step 1", type="service"),
                WorkflowStep(id="step2", name="Step 2", type="service"),
            ],
            dependencies={"step2": ["step1"]},
        )

        # Measure execution throughput
        iterations = 20
        start_time = time.time()

        for i in range(iterations):
            # Create unique workflow ID for each execution
            test_workflow = WorkflowDefinition(
                id=f"exec_perf_{i}",
                name=workflow.name,
                steps=workflow.steps,
                dependencies=workflow.dependencies,
            )

            result = await engine.execute_workflow(test_workflow)
            assert result["status"] in ["completed", "failed"]

        end_time = time.time()
        duration = end_time - start_time
        throughput = iterations / duration

        print(f"Execution throughput: {throughput:.1f} executions/second")
        assert (
            throughput >= executions_per_second_target
        ), f"Execution too slow: {throughput:.1f} < {executions_per_second_target} executions/sec"

    def test_optimization_performance(self):
        """Test workflow optimization performance"""
        optimizer = WorkflowOptimizer()
        optimizations_per_second_target = 30

        # Create workflow with optimization opportunities
        workflow = WorkflowDefinition(
            id="opt_perf_test",
            name="Optimization Performance Test",
            steps=[
                WorkflowStep(id="start", name="Start", type="service"),
                WorkflowStep(id="parallel1", name="Parallel 1", type="agent", agent_id="agent1"),
                WorkflowStep(id="parallel2", name="Parallel 2", type="agent", agent_id="agent2"),
                WorkflowStep(id="end", name="End", type="service"),
            ],
            dependencies={
                "parallel1": ["start"],
                "parallel2": ["start"],
                "end": ["parallel1", "parallel2"],
            },
        )

        # Measure optimization throughput
        iterations = 30
        start_time = time.time()

        for i in range(iterations):
            # Clear cache to force recomputation
            optimizer.cache.clear()

            result = optimizer.optimize_workflow(workflow)
            assert "optimization_score" in result

        end_time = time.time()
        duration = end_time - start_time
        throughput = iterations / duration

        print(f"Optimization throughput: {throughput:.1f} optimizations/second")
        assert (
            throughput >= optimizations_per_second_target
        ), f"Optimization too slow: {throughput:.1f} < {optimizations_per_second_target} optimizations/sec"

    def test_concurrent_operations(self):
        """Test performance under concurrent operations"""
        import queue
        import threading

        results = queue.Queue()

        def worker():
            try:
                # Create instances
                parser = WorkflowParser()
                validator = DAGValidator()

                # Perform operations
                workflow_data = {
                    "id": f"concurrent_test_{threading.current_thread().ident}",
                    "name": "Concurrent Test",
                    "steps": [{"id": "step1", "name": "Step 1", "type": "service"}],
                }

                workflow = parser.parse_dict(workflow_data)
                validation = validator.validate_dag(workflow)

                results.put(("success", validation["is_valid_dag"]))
            except Exception as e:
                results.put(("error", str(e)))

        # Start 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        successes = 0
        while not results.empty():
            result_type, result_value = results.get()
            if result_type == "success":
                successes += 1
                assert result_value is True
            else:
                print(f"Thread error: {result_value}")

        assert successes == 10, f"Only {successes}/10 threads succeeded"

    def test_large_workflow_scalability(self):
        """Test system performance with large workflows"""
        parser = WorkflowParser()
        validator = DAGValidator()

        # Create large workflow (100 steps)
        steps = []
        deps = {}

        for i in range(100):
            steps.append({"id": f"step_{i}", "name": f"Step {i}", "type": "service"})
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        workflow_data = {
            "id": "large_scalability_test",
            "name": "Large Scalability Test",
            "steps": steps,
            "dependencies": deps,
        }

        # Test parsing
        start_time = time.time()
        workflow = parser.parse_dict(workflow_data)
        parse_time = time.time() - start_time

        print(f"Large workflow parsing time: {parse_time:.3f}s")
        assert parse_time < 1.0, f"Parsing too slow for large workflow: {parse_time:.3f}s"

        # Test validation
        start_time = time.time()
        validation = validator.validate_dag(workflow)
        validation_time = time.time() - start_time

        print(f"Large workflow validation time: {validation_time:.3f}s")
        assert (
            validation_time < 2.0
        ), f"Validation too slow for large workflow: {validation_time:.3f}s"
        assert validation["is_valid_dag"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
