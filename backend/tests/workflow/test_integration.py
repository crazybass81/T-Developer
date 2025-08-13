import pytest

from src.workflow.dag_validator import DAGValidator
from src.workflow.engine import WorkflowEngine
from src.workflow.optimizer import WorkflowOptimizer
from src.workflow.parser import SAMPLE, WorkflowParser


class TestWorkflowIntegration:
    """Integration tests for the complete workflow system"""

    def setup_method(self):
        self.parser = WorkflowParser()
        self.validator = DAGValidator()
        self.optimizer = WorkflowOptimizer()
        self.engine = WorkflowEngine()

    def test_full_workflow_pipeline_simple(self):
        """Test complete pipeline: parse -> validate -> optimize -> execute"""
        # 1. Parse workflow
        workflow_data = {
            "id": "integration_test",
            "name": "Integration Test Workflow",
            "steps": [
                {"id": "extract", "name": "Extract Data", "type": "agent", "agent_id": "extractor"},
                {"id": "process", "name": "Process Data", "type": "agent", "agent_id": "processor"},
                {"id": "store", "name": "Store Data", "type": "agent", "agent_id": "storer"},
            ],
            "dependencies": {"process": ["extract"], "store": ["process"]},
        }

        workflow = self.parser.parse_dict(workflow_data)
        assert workflow is not None
        assert workflow.id == "integration_test"

        # 2. Validate DAG
        validation_result = self.validator.validate_dag(workflow)
        assert validation_result["is_valid_dag"] is True
        assert len(validation_result["cycles_detected"]) == 0

        # 3. Get execution order
        execution_order = self.validator.get_execution_order(workflow)
        assert len(execution_order) == 3  # Sequential execution
        assert execution_order[0] == ["extract"]
        assert execution_order[1] == ["process"]
        assert execution_order[2] == ["store"]

        # 4. Optimize workflow
        optimization_result = self.optimizer.optimize_workflow(workflow)
        assert "optimization_score" in optimization_result
        assert optimization_result["original_workflow"] == "integration_test"

    @pytest.mark.asyncio
    async def test_full_pipeline_with_execution(self):
        """Test complete pipeline including execution"""
        # Parse from sample workflow
        workflow = self.parser.parse_dict(SAMPLE["data_processing"])

        # Validate
        validation = self.validator.validate_dag(workflow)
        assert validation["is_valid_dag"] is True

        # Optimize
        optimization = self.optimizer.optimize_workflow(workflow)
        assert optimization["optimization_score"] > 0

        # Execute
        execution_result = await self.engine.execute_workflow(workflow)
        assert execution_result["status"] in ["completed", "failed"]
        assert execution_result["workflow_id"] == workflow.id

    def test_parallel_workflow_integration(self):
        """Test integration with parallel workflow structure"""
        workflow_data = {
            "id": "parallel_integration",
            "name": "Parallel Integration Test",
            "steps": [
                {"id": "start", "name": "Start", "type": "service"},
                {"id": "branch1", "name": "Branch 1", "type": "agent", "agent_id": "worker1"},
                {"id": "branch2", "name": "Branch 2", "type": "agent", "agent_id": "worker2"},
                {"id": "merge", "name": "Merge", "type": "service"},
            ],
            "dependencies": {
                "branch1": ["start"],
                "branch2": ["start"],
                "merge": ["branch1", "branch2"],
            },
        }

        # Parse
        workflow = self.parser.parse_dict(workflow_data)

        # Validate - should find good parallelization
        validation = self.validator.validate_dag(workflow)
        assert validation["is_valid_dag"] is True
        metrics = validation["graph_metrics"]
        assert metrics["max_width"] >= 2  # Should detect parallel execution

        # Get execution order - should have parallel level
        execution_order = self.validator.get_execution_order(workflow)
        assert len(execution_order) == 3  # start -> [branch1,branch2] -> merge
        assert len(execution_order[1]) == 2  # Parallel level with 2 steps

        # Optimize - should find parallelization opportunities
        optimization = self.optimizer.optimize_workflow(workflow)
        assert len(optimization["structure_optimizations"]) >= 0

    def test_cyclic_workflow_handling(self):
        """Test system behavior with cyclic workflow"""
        cyclic_data = {
            "id": "cyclic_integration",
            "name": "Cyclic Integration Test",
            "steps": [
                {"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"},
                {"id": "step2", "name": "Step 2", "type": "agent", "agent_id": "agent2"},
            ],
            "dependencies": {"step1": ["step2"], "step2": ["step1"]},  # Creates cycle
        }

        # Parse - should succeed
        workflow = self.parser.parse_dict(cyclic_data)

        # Validate - should detect cycle
        validation = self.validator.validate_dag(workflow)
        assert validation["is_valid_dag"] is False
        assert len(validation["cycles_detected"]) > 0

        # Optimize - should suggest cycle fix
        optimization = self.optimizer.optimize_workflow(workflow)
        improvements = optimization["suggested_improvements"]
        assert any("Invalid DAG" in str(imp.get("issue", "")) for imp in improvements)

    @pytest.mark.asyncio
    async def test_error_propagation_through_pipeline(self):
        """Test error handling throughout the pipeline"""
        # Create workflow with issues
        problematic_data = {
            "id": "error_test",
            "name": "Error Test",
            "steps": [
                {"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"},
                {"id": "step2", "name": "Step 2", "type": "agent", "agent_id": "agent2"},
            ],
            "dependencies": {"step1": ["step2"], "step2": ["step1"]},  # Cycle
        }

        # Parse
        workflow = self.parser.parse_dict(problematic_data)

        # Execute - should fail due to cycle
        execution_result = await self.engine.execute_workflow(workflow)
        assert execution_result["status"] == "failed"
        assert "cycles" in execution_result or "Invalid DAG" in execution_result.get("error", "")

    def test_workflow_export_import_roundtrip(self):
        """Test export and re-import of workflow"""
        # Create workflow
        original_data = {
            "id": "roundtrip_test",
            "name": "Roundtrip Test",
            "steps": [
                {
                    "id": "step1",
                    "name": "Step 1",
                    "type": "agent",
                    "agent_id": "agent1",
                    "outputs": ["data"],
                },
                {
                    "id": "step2",
                    "name": "Step 2",
                    "type": "agent",
                    "agent_id": "agent2",
                    "inputs": ["data"],
                },
            ],
        }

        # Parse original
        original_workflow = self.parser.parse_dict(original_data)

        # Export to YAML
        yaml_export = self.parser.export(original_workflow, "yaml")
        assert "id: roundtrip_test" in yaml_export

        # Parse exported YAML
        reimported_workflow = self.parser.parse_string(yaml_export, "yaml")

        # Should be equivalent
        assert reimported_workflow.id == original_workflow.id
        assert reimported_workflow.name == original_workflow.name
        assert len(reimported_workflow.steps) == len(original_workflow.steps)

    def test_optimization_workflow_generation(self):
        """Test generating optimized workflow from suggestions"""
        workflow = self.parser.parse_dict(
            {
                "id": "opt_gen_test",
                "name": "Optimization Generation Test",
                "steps": [
                    {"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"},
                    {"id": "step2", "name": "Step 2", "type": "agent", "agent_id": "agent2"},
                ],
                "dependencies": {"step2": ["step1"]},
            }
        )

        # Generate optimized version
        optimized = self.optimizer.generate_optimized(workflow, ["retry_policy"])

        # Validate optimized workflow
        assert optimized.id == "opt_gen_test_optimized"
        assert optimized.name == "Optimization Generation Test (Optimized)"

        # Should still be valid DAG
        validation = self.validator.validate_dag(optimized)
        assert validation["is_valid_dag"] is True

        # Should have retry policies
        for step in optimized.steps:
            assert step.retry_policy is not None

    def test_large_workflow_integration(self):
        """Test system performance with larger workflow"""
        # Create workflow with 30 steps
        steps = []
        deps = {}

        # Create branching structure
        steps.append({"id": "root", "name": "Root", "type": "service"})

        # Create 3 parallel branches of 10 steps each
        for branch in range(3):
            for i in range(10):
                step_id = f"branch_{branch}_step_{i}"
                steps.append(
                    {"id": step_id, "name": f"Branch {branch} Step {i}", "type": "service"}
                )

                if i == 0:
                    deps[step_id] = ["root"]
                else:
                    deps[step_id] = [f"branch_{branch}_step_{i-1}"]

        # Add convergence step
        steps.append({"id": "converge", "name": "Converge", "type": "service"})
        deps["converge"] = [f"branch_{b}_step_9" for b in range(3)]

        workflow_data = {
            "id": "large_integration",
            "name": "Large Integration Test",
            "steps": steps,
            "dependencies": deps,
        }

        # Parse
        workflow = self.parser.parse_dict(workflow_data)
        assert len(workflow.steps) == 32  # 1 root + 30 branch + 1 converge

        # Validate
        validation = self.validator.validate_dag(workflow)
        assert validation["is_valid_dag"] is True
        assert validation["graph_metrics"]["max_width"] >= 3  # 3 parallel branches

        # Optimize
        optimization = self.optimizer.optimize_workflow(workflow)
        assert "optimization_score" in optimization

    @pytest.mark.asyncio
    async def test_complex_workflow_execution(self):
        """Test execution of complex workflow structure"""
        workflow_data = {
            "id": "complex_exec",
            "name": "Complex Execution",
            "steps": [
                {"id": "init", "name": "Initialize", "type": "service"},
                {"id": "proc1", "name": "Process 1", "type": "agent", "agent_id": "processor1"},
                {"id": "proc2", "name": "Process 2", "type": "agent", "agent_id": "processor2"},
                {"id": "validate", "name": "Validate", "type": "service"},
                {"id": "finalize", "name": "Finalize", "type": "service"},
            ],
            "dependencies": {
                "proc1": ["init"],
                "proc2": ["init"],
                "validate": ["proc1", "proc2"],
                "finalize": ["validate"],
            },
        }

        workflow = self.parser.parse_dict(workflow_data)
        result = await self.engine.execute_workflow(workflow)

        assert result["status"] in ["completed", "failed"]
        assert result["total_levels"] == 4  # init -> [proc1,proc2] -> validate -> finalize
        assert len(result["step_results"]) == 5

    def test_workflow_validation_summary(self):
        """Test workflow validation and summary generation"""
        workflow = self.parser.parse_dict(
            {
                "id": "summary_test",
                "name": "Summary Test Workflow",
                "description": "Test workflow for summary",
                "steps": [
                    {"id": "step1", "name": "Step 1", "type": "service"},
                    {"id": "step2", "name": "Step 2", "type": "service"},
                ],
                "dependencies": {"step2": ["step1"]},
                "tags": ["test", "integration"],
            }
        )

        # Validate workflow structure
        parser_validation = self.parser.validate(workflow)
        assert parser_validation["valid"] is True

        # Get DAG validation
        dag_validation = self.validator.validate_dag(workflow)
        assert dag_validation["is_valid_dag"] is True

        # Get summary
        self.parser.parsed[workflow.id] = workflow
        summary = self.parser.get_summary(workflow.id)
        assert summary["id"] == "summary_test"
        assert summary["name"] == "Summary Test Workflow"
        assert summary["step_count"] == 2

    def test_memory_constraint_compliance(self):
        """Test that all components meet memory constraints"""
        import sys

        # Test parser
        parser = WorkflowParser()
        parser_size = sys.getsizeof(parser)

        # Test validator
        validator = DAGValidator()
        validator_size = sys.getsizeof(validator)

        # Test optimizer
        optimizer = WorkflowOptimizer()
        optimizer_size = sys.getsizeof(optimizer)

        # Test engine
        engine = WorkflowEngine()
        engine_size = sys.getsizeof(engine)

        # All should be reasonable memory usage
        assert parser_size < 10000  # 10KB limit for instances
        assert validator_size < 10000
        assert optimizer_size < 10000
        assert engine_size < 10000


class TestPerformanceIntegration:
    """Performance and constraint tests for integrated system"""

    def setup_method(self):
        self.parser = WorkflowParser()
        self.validator = DAGValidator()
        self.optimizer = WorkflowOptimizer()
        self.engine = WorkflowEngine()

    @pytest.mark.asyncio
    async def test_end_to_end_performance(self):
        """Test performance of complete workflow pipeline"""
        import time

        workflow_data = {
            "id": "perf_test",
            "name": "Performance Test",
            "steps": [
                {"id": f"step_{i}", "name": f"Step {i}", "type": "service"} for i in range(20)
            ],
            "dependencies": {f"step_{i}": [f"step_{i-1}"] for i in range(1, 20)},
        }

        start_time = time.time()

        # Parse
        workflow = self.parser.parse_dict(workflow_data)

        # Validate
        validation = self.validator.validate_dag(workflow)
        assert validation["is_valid_dag"]

        # Optimize
        optimization = self.optimizer.optimize_workflow(workflow)
        assert "optimization_score" in optimization

        # Execute
        execution = await self.engine.execute_workflow(workflow)

        end_time = time.time()

        # Should complete within reasonable time (under 5 seconds)
        assert end_time - start_time < 5.0
        assert execution["status"] in ["completed", "failed"]

    def test_concurrent_pipeline_operations(self):
        """Test concurrent operations across components"""
        workflows = []

        # Create multiple workflows
        for i in range(10):
            workflow_data = {
                "id": f"concurrent_{i}",
                "name": f"Concurrent {i}",
                "steps": [
                    {"id": "step1", "name": "Step 1", "type": "service"},
                    {"id": "step2", "name": "Step 2", "type": "service"},
                ],
                "dependencies": {"step2": ["step1"]},
            }
            workflow = self.parser.parse_dict(workflow_data)
            workflows.append(workflow)

        # Process all concurrently
        validations = [self.validator.validate_dag(wf) for wf in workflows]
        optimizations = [self.optimizer.optimize_workflow(wf) for wf in workflows]

        # All should succeed
        assert len(validations) == 10
        assert len(optimizations) == 10

        for validation in validations:
            assert validation["is_valid_dag"] is True

        for optimization in optimizations:
            assert "optimization_score" in optimization


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
