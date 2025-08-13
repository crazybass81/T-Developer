import json
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.workflow.parser import (
    SAMPLE,
    WorkflowDefinition,
    WorkflowParser,
    WorkflowStep,
    create_simple,
)


class TestWorkflowParser:
    def setup_method(self):
        self.parser = WorkflowParser()

    def test_parser_initialization(self):
        assert isinstance(self.parser.parsed, dict)
        assert isinstance(self.parser.errors, list)
        assert isinstance(self.parser.schema, dict)

    def test_parse_valid_dict(self):
        data = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "steps": [{"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"}],
        }
        workflow = self.parser.parse_dict(data)
        assert isinstance(workflow, WorkflowDefinition)
        assert workflow.id == "test_workflow"
        assert len(workflow.steps) == 1
        assert workflow.steps[0].id == "step1"

    def test_parse_missing_required_fields(self):
        data = {"name": "Test Workflow"}  # Missing id and steps
        with pytest.raises(Exception):
            self.parser.parse_dict(data)

    def test_parse_invalid_step_type(self):
        data = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "steps": [{"id": "step1", "name": "Step 1", "type": "invalid_type"}],
        }
        with pytest.raises(ValidationError):
            self.parser.parse_dict(data)

    def test_parse_yaml_file(self):
        yaml_content = """
id: yaml_workflow
name: YAML Workflow
steps:
  - id: step1
    name: Step 1
    type: agent
    agent_id: agent1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            workflow = self.parser.parse_file(f.name)
            assert workflow.id == "yaml_workflow"
            assert len(workflow.steps) == 1
        Path(f.name).unlink()

    def test_parse_json_file(self):
        json_data = {
            "id": "json_workflow",
            "name": "JSON Workflow",
            "steps": [{"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"}],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            f.flush()
            workflow = self.parser.parse_file(f.name)
            assert workflow.id == "json_workflow"
            assert len(workflow.steps) == 1
        Path(f.name).unlink()

    def test_parse_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("nonexistent.yaml")

    def test_parse_string_yaml(self):
        yaml_str = "id: str_workflow\nname: String Workflow\nsteps:\n  - id: step1\n    name: Step 1\n    type: agent\n    agent_id: agent1"
        workflow = self.parser.parse_string(yaml_str, "yaml")
        assert workflow.id == "str_workflow"

    def test_parse_string_json(self):
        json_str = '{"id": "json_str", "name": "JSON String", "steps": [{"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"}]}'
        workflow = self.parser.parse_string(json_str, "json")
        assert workflow.id == "json_str"

    def test_validate_agent_step_missing_agent_id(self):
        data = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "steps": [{"id": "step1", "name": "Step 1", "type": "agent"}],  # Missing agent_id
        }
        with pytest.raises(ValueError, match="Agent step step1 missing agent_id"):
            self.parser.parse_dict(data)

    def test_validate_duplicate_step_ids(self):
        data = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "steps": [
                {"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"},
                {"id": "step1", "name": "Step 2", "type": "service"},  # Duplicate ID
            ],
        }
        with pytest.raises(ValueError, match="Duplicate step IDs"):
            self.parser.parse_dict(data)

    def test_validate_invalid_dependencies(self):
        data = {
            "id": "test_workflow",
            "name": "Test Workflow",
            "steps": [{"id": "step1", "name": "Step 1", "type": "agent", "agent_id": "agent1"}],
            "dependencies": {"step2": ["step1"]},  # step2 doesn't exist
        }
        with pytest.raises(ValueError, match="Invalid dependencies"):
            self.parser.parse_dict(data)

    def test_export_yaml(self):
        workflow = WorkflowDefinition(
            id="export_test",
            name="Export Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")],
        )
        result = self.parser.export(workflow, "yaml")
        assert "id: export_test" in result
        assert "name: Export Test" in result

    def test_export_json(self):
        workflow = WorkflowDefinition(
            id="export_test",
            name="Export Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")],
        )
        result = self.parser.export(workflow, "json")
        data = json.loads(result)
        assert data["id"] == "export_test"
        assert data["name"] == "Export Test"

    def test_validate_workflow(self):
        workflow = WorkflowDefinition(
            id="valid_wf",
            name="Valid Workflow",
            steps=[WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")],
        )
        result = self.parser.validate(workflow)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_empty_workflow(self):
        workflow = WorkflowDefinition(id="empty_wf", name="Empty Workflow", steps=[])
        result = self.parser.validate(workflow)
        assert result["valid"] is False
        assert "No steps" in result["errors"]

    def test_get_summary(self):
        workflow = WorkflowDefinition(
            id="summary_test",
            name="Summary Test",
            steps=[WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")],
        )
        self.parser.parsed[workflow.id] = workflow
        summary = self.parser.get_summary("summary_test")
        assert summary["id"] == "summary_test"
        assert summary["name"] == "Summary Test"
        assert summary["step_count"] == 1

    def test_get_summary_nonexistent(self):
        assert self.parser.get_summary("nonexistent") is None

    def test_created_at_auto_generation(self):
        data = {
            "id": "auto_time",
            "name": "Auto Time",
            "steps": [{"id": "step1", "name": "Step 1", "type": "service"}],
        }
        workflow = self.parser.parse_dict(data)
        assert workflow.created_at is not None
        assert "T" in workflow.created_at  # ISO format check


class TestWorkflowStep:
    def test_step_creation(self):
        step = WorkflowStep(id="test_step", name="Test Step", type="agent", agent_id="agent1")
        assert step.id == "test_step"
        assert step.name == "Test Step"
        assert step.type == "agent"
        assert step.agent_id == "agent1"

    def test_step_defaults(self):
        step = WorkflowStep(id="default_step", name="Default Step", type="service")
        assert step.inputs == []
        assert step.outputs == []
        assert step.parameters == {}
        assert step.timeout is None
        assert step.retry_policy is None

    def test_step_type_validation(self):
        with pytest.raises(ValidationError):
            WorkflowStep(id="invalid", name="Invalid", type="invalid_type")


class TestWorkflowDefinition:
    def test_workflow_creation(self):
        steps = [WorkflowStep(id="step1", name="Step 1", type="agent", agent_id="agent1")]
        workflow = WorkflowDefinition(id="test_wf", name="Test Workflow", steps=steps)
        assert workflow.id == "test_wf"
        assert workflow.name == "Test Workflow"
        assert len(workflow.steps) == 1

    def test_workflow_defaults(self):
        steps = [WorkflowStep(id="step1", name="Step 1", type="service")]
        workflow = WorkflowDefinition(id="default_wf", name="Default Workflow", steps=steps)
        assert workflow.version == "1.0.0"
        assert workflow.dependencies == {}
        assert workflow.error_handling == "stop"
        assert workflow.tags == []
        assert workflow.metadata == {}


class TestUtilityFunctions:
    def test_create_simple_workflow(self):
        steps_config = [
            {"id": "step1", "name": "Extract", "type": "agent", "agent_id": "extractor"},
            {"id": "step2", "name": "Transform", "type": "agent", "agent_id": "transformer"},
        ]
        workflow = create_simple("Test Pipeline", steps_config)
        assert workflow.id == "test_pipeline"
        assert workflow.name == "Test Pipeline"
        assert len(workflow.steps) == 2
        assert workflow.dependencies == {"step2": ["step1"]}

    def test_sample_workflow_exists(self):
        assert "data_processing" in SAMPLE
        sample = SAMPLE["data_processing"]
        assert "id" in sample
        assert "name" in sample
        assert "steps" in sample
        assert len(sample["steps"]) >= 2


class TestPerformanceAndConstraints:
    def test_parser_memory_efficiency(self):
        # Test that parser handles multiple workflows efficiently
        parser = WorkflowParser()
        for i in range(100):
            data = {
                "id": f"workflow_{i}",
                "name": f"Workflow {i}",
                "steps": [{"id": f"step_{i}", "name": f"Step {i}", "type": "service"}],
            }
            workflow = parser.parse_dict(data)
            assert workflow.id == f"workflow_{i}"
        assert len(parser.parsed) == 100

    def test_large_workflow_parsing(self):
        # Test parser with large workflow (50 steps)
        steps = []
        deps = {}
        for i in range(50):
            steps.append({"id": f"step_{i}", "name": f"Step {i}", "type": "service"})
            if i > 0:
                deps[f"step_{i}"] = [f"step_{i-1}"]

        data = {"id": "large_wf", "name": "Large Workflow", "steps": steps, "dependencies": deps}
        workflow = self.parser.parse_dict(data)
        assert len(workflow.steps) == 50
        assert len(workflow.dependencies) == 49

    def setup_method(self):
        self.parser = WorkflowParser()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
