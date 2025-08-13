import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema
import yaml
from pydantic import BaseModel, Field, field_validator


class WorkflowStep(BaseModel):
    id: str
    name: str
    type: str
    agent_id: Optional[str] = None
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v not in {"agent", "service", "condition", "parallel", "sequential", "loop"}:
            raise ValueError("Invalid step type")
        return v


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    created_at: Optional[str] = None
    steps: List[WorkflowStep]
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    timeout: Optional[int] = None
    error_handling: str = "stop"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowParser:
    def __init__(self):
        self.parsed = {}
        self.errors = []
        self.schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "steps": {"type": "array", "minItems": 1},
            },
            "required": ["id", "name", "steps"],
        }

    def parse_file(self, file_path: Union[str, Path]) -> Optional[WorkflowDefinition]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r") as f:
            content = f.read()
        if file_path.suffix.lower() in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)
        return self.parse_dict(data)

    def parse_string(self, content: str, fmt: str = "yaml") -> Optional[WorkflowDefinition]:
        data = yaml.safe_load(content) if fmt == "yaml" else json.loads(content)
        return self.parse_dict(data)

    def parse_dict(self, data: Dict[str, Any]) -> Optional[WorkflowDefinition]:
        self.errors.clear()
        jsonschema.validate(data, self.schema)
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow().isoformat()
        workflow = WorkflowDefinition.model_validate(data)
        self._validate(workflow)
        self.parsed[workflow.id] = workflow
        return workflow

    def _validate(self, wf: WorkflowDefinition):
        sids = {s.id for s in wf.steps}
        if len(sids) != len(wf.steps):
            raise ValueError("Duplicate step IDs")
        for sid, deps in wf.dependencies.items():
            if sid not in sids or any(d not in sids for d in deps):
                raise ValueError("Invalid dependencies")
        for s in wf.steps:
            if s.type == "agent" and not s.agent_id:
                raise ValueError(f"Agent step {s.id} missing agent_id")

    def export(self, wf: WorkflowDefinition, fmt: str = "yaml") -> str:
        data = wf.model_dump(exclude_unset=True)
        return (
            yaml.dump(data, default_flow_style=False)
            if fmt == "yaml"
            else json.dumps(data, indent=2)
        )

    def validate(self, wf: WorkflowDefinition) -> Dict[str, Any]:
        result = {"valid": True, "errors": [], "warnings": []}
        if not wf.steps:
            result["errors"].append("No steps")
            result["valid"] = False
        return result

    def get_summary(self, wid: str) -> Optional[Dict[str, Any]]:
        if wid not in self.parsed:
            return None
        wf = self.parsed[wid]
        return {"id": wf.id, "name": wf.name, "step_count": len(wf.steps)}


def create_simple(name: str, steps: List[Dict[str, Any]]) -> WorkflowDefinition:
    ws = []
    deps = {}
    for i, cfg in enumerate(steps):
        sid = cfg.get("id", f"step_{i+1}")
        ws.append(
            WorkflowStep(
                id=sid,
                name=cfg.get("name", f"Step {i+1}"),
                type=cfg.get("type", "agent"),
                agent_id=cfg.get("agent_id"),
                inputs=cfg.get("inputs", []),
                outputs=cfg.get("outputs", []),
            )
        )
        if i > 0:
            deps[sid] = [ws[i - 1].id]
    return WorkflowDefinition(
        id=name.lower().replace(" ", "_"), name=name, steps=ws, dependencies=deps
    )


SAMPLE = {
    "data_processing": {
        "id": "data_processing_pipeline",
        "name": "Data Processing Pipeline",
        "steps": [
            {
                "id": "extract",
                "name": "Extract Data",
                "type": "agent",
                "agent_id": "data_extractor",
                "outputs": ["raw_data"],
            },
            {
                "id": "transform",
                "name": "Transform Data",
                "type": "agent",
                "agent_id": "data_transformer",
                "inputs": ["raw_data"],
                "outputs": ["processed_data"],
            },
            {
                "id": "load",
                "name": "Load Data",
                "type": "agent",
                "agent_id": "data_loader",
                "inputs": ["processed_data"],
                "outputs": ["loaded_data"],
            },
        ],
        "dependencies": {"transform": ["extract"], "load": ["transform"]},
    }
}
