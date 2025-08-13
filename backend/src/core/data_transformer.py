"""
Data transformation layer for agent communication
Handles data conversion between different agent formats
"""
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.core.agent_models import (
    AssemblyResult,
    ComponentDecisionResult,
    DownloadResult,
    GenerationResult,
    MatchRateResult,
    NLInputResult,
    ParserResult,
    SearchResult,
    UISelectionResult,
)
from src.core.interfaces import AgentInput, AgentResult, PipelineContext, ProcessingStatus


class DataTransformer:
    """Transform data between agent formats"""

    @staticmethod
    def serialize(obj: Any) -> Union[Dict, List, str, int, float, bool, None]:
        """Serialize complex objects to JSON-compatible format"""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (list, tuple)):
            return [DataTransformer.serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: DataTransformer.serialize(value) for key, value in obj.items()}
        elif is_dataclass(obj):
            return DataTransformer.serialize(asdict(obj))
        elif hasattr(obj, "to_dict"):
            return DataTransformer.serialize(obj.to_dict())
        elif hasattr(obj, "__dict__"):
            return DataTransformer.serialize(obj.__dict__)
        else:
            return str(obj)

    @staticmethod
    def deserialize(data: Union[Dict, str], target_class: type = None) -> Any:
        """Deserialize JSON data to target class"""
        if isinstance(data, str):
            data = json.loads(data)

        if target_class is None:
            return data

        if hasattr(target_class, "from_dict"):
            return target_class.from_dict(data)
        elif is_dataclass(target_class):
            return target_class(**data)
        else:
            return data

    # ============= Agent Input Transformers =============

    @staticmethod
    def nl_input_to_ui_selection(
        nl_result: NLInputResult, context: PipelineContext
    ) -> AgentInput[Dict]:
        """Transform NL Input result to UI Selection input"""
        return AgentInput(
            data={
                "project_type": nl_result.project_type,
                "features": nl_result.features,
                "preferences": nl_result.preferences,
                "technical_requirements": nl_result.technical_requirements,
                "complexity": nl_result.complexity,
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def ui_selection_to_parser(
        ui_result: UISelectionResult, nl_result: NLInputResult, context: PipelineContext
    ) -> AgentInput[Dict]:
        """Transform UI Selection result to Parser input"""
        return AgentInput(
            data={
                "project_type": nl_result.project_type,
                "features": nl_result.features,
                "framework": ui_result.framework.name,
                "ui_library": ui_result.ui_library.name if ui_result.ui_library else None,
                "styling": ui_result.styling_solution.name,
                "state_management": ui_result.state_management.name
                if ui_result.state_management
                else None,
                "bundler": ui_result.bundler.name,
                "testing": ui_result.testing_framework.name,
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def parser_to_component_decision(
        parser_result: ParserResult,
        ui_result: UISelectionResult,
        context: PipelineContext,
    ) -> AgentInput[Dict]:
        """Transform Parser result to Component Decision input"""
        return AgentInput(
            data={
                "file_structure": DataTransformer.serialize(parser_result.file_structure),
                "api_endpoints": [
                    DataTransformer.serialize(ep) for ep in parser_result.api_endpoints
                ],
                "modules": parser_result.modules,
                "framework": ui_result.framework.name,
                "ui_patterns": ui_result.ui_library.name if ui_result.ui_library else "custom",
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def component_to_match_rate(
        component_result: ComponentDecisionResult,
        parser_result: ParserResult,
        nl_result: NLInputResult,
        context: PipelineContext,
    ) -> AgentInput[Dict]:
        """Transform Component Decision result to Match Rate input"""
        return AgentInput(
            data={
                "project_type": nl_result.project_type,
                "features": nl_result.features,
                "components": [DataTransformer.serialize(c) for c in component_result.components],
                "architecture": component_result.architecture_pattern.value,
                "file_structure": DataTransformer.serialize(parser_result.file_structure),
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def match_rate_to_search(
        match_result: MatchRateResult,
        component_result: ComponentDecisionResult,
        ui_result: UISelectionResult,
        context: PipelineContext,
    ) -> AgentInput[Dict]:
        """Transform Match Rate result to Search input"""
        return AgentInput(
            data={
                "framework": ui_result.framework.name,
                "libraries_needed": [
                    ui_result.ui_library.name if ui_result.ui_library else None,
                    ui_result.styling_solution.name,
                    ui_result.state_management.name if ui_result.state_management else None,
                    ui_result.bundler.name,
                    ui_result.testing_framework.name,
                ],
                "missing_capabilities": match_result.missing_capabilities,
                "components": [c.name for c in component_result.components],
                "best_match_template": match_result.best_match.template_id
                if match_result.best_match
                else None,
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def search_to_generation(
        search_result: SearchResult,
        component_result: ComponentDecisionResult,
        parser_result: ParserResult,
        match_result: MatchRateResult,
        context: PipelineContext,
    ) -> AgentInput[Dict]:
        """Transform Search result to Generation input"""
        return AgentInput(
            data={
                "file_structure": DataTransformer.serialize(parser_result.file_structure),
                "components": [DataTransformer.serialize(c) for c in component_result.components],
                "libraries": {lib.name: lib.version for lib in search_result.libraries},
                "code_snippets": [
                    DataTransformer.serialize(s) for s in search_result.code_snippets[:5]
                ],
                "template": match_result.best_match.template_id
                if match_result.best_match
                else None,
                "api_endpoints": [
                    DataTransformer.serialize(ep) for ep in parser_result.api_endpoints
                ],
                "database_schemas": [
                    DataTransformer.serialize(s) for s in parser_result.database_schemas
                ],
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def generation_to_assembly(
        generation_result: GenerationResult,
        parser_result: ParserResult,
        search_result: SearchResult,
        context: PipelineContext,
    ) -> AgentInput[Dict]:
        """Transform Generation result to Assembly input"""
        return AgentInput(
            data={
                "files": [DataTransformer.serialize(f) for f in generation_result.files],
                "dependencies": {lib.name: lib.version for lib in search_result.libraries},
                "dev_dependencies": parser_result.dev_dependencies,
                "config_files": parser_result.config_files,
                "environment_variables": parser_result.environment_variables,
                "test_files": [f.path for f in generation_result.files if f.has_tests],
            },
            context=context,
            previous_results=[],
        )

    @staticmethod
    def assembly_to_download(
        assembly_result: AssemblyResult,
        generation_result: GenerationResult,
        nl_result: NLInputResult,
        ui_result: UISelectionResult,
        context: PipelineContext,
    ) -> AgentInput[Dict]:
        """Transform Assembly result to Download input"""
        return AgentInput(
            data={
                "project_path": assembly_result.project_path,
                "project_name": nl_result.main_functionality.replace(" ", "-").lower(),
                "framework": ui_result.framework.name,
                "language": nl_result.technical_requirements.get("language", "typescript"),
                "total_files": generation_result.total_files,
                "build_successful": assembly_result.build_result.success,
                "tests_passed": assembly_result.test_result.passed_tests
                if assembly_result.test_result
                else 0,
                "documentation_generated": assembly_result.readme_generated,
            },
            context=context,
            previous_results=[],
        )

    # ============= Result Aggregators =============

    @staticmethod
    def aggregate_pipeline_results(results: List[AgentResult]) -> Dict[str, Any]:
        """Aggregate all agent results into a single response"""
        aggregated = {
            "pipeline_id": None,
            "project_id": None,
            "success": True,
            "agents": {},
            "errors": [],
            "warnings": [],
            "metrics": {
                "total_execution_time_ms": 0,
                "total_memory_usage_mb": 0,
                "agents_executed": 0,
                "agents_succeeded": 0,
                "agents_failed": 0,
            },
        }

        for result in results:
            # Store agent result
            aggregated["agents"][result.agent_name] = {
                "status": result.status.value,
                "data": DataTransformer.serialize(result.data),
                "execution_time_ms": result.execution_time_ms,
                "confidence": result.confidence,
            }

            # Update metrics
            aggregated["metrics"]["agents_executed"] += 1
            aggregated["metrics"]["total_execution_time_ms"] += result.execution_time_ms
            aggregated["metrics"]["total_memory_usage_mb"] += result.memory_usage_mb

            if result.is_successful():
                aggregated["metrics"]["agents_succeeded"] += 1
            else:
                aggregated["metrics"]["agents_failed"] += 1
                aggregated["success"] = False
                if result.error:
                    aggregated["errors"].append(f"{result.agent_name}: {result.error}")

        return aggregated

    @staticmethod
    def validate_agent_chain(results: List[AgentResult]) -> bool:
        """Validate that agent results form a valid chain"""
        expected_agents = [
            "nl_input",
            "ui_selection",
            "parser",
            "component_decision",
            "match_rate",
            "search",
            "generation",
            "assembly",
            "download",
        ]

        # Check all agents executed
        executed_agents = [r.agent_name for r in results]
        for agent in expected_agents:
            if agent not in executed_agents:
                return False

        # Check all succeeded (except optional ones)
        for result in results:
            if not result.is_successful() and result.agent_name != "download":
                return False

        return True

    @staticmethod
    def extract_final_output(results: List[AgentResult]) -> Optional[Dict[str, Any]]:
        """Extract final output from pipeline results"""
        # Find download result
        download_result = None
        for result in results:
            if result.agent_name == "download" and result.is_successful():
                download_result = result.data
                break

        if not download_result:
            return None

        # Build final output
        return {
            "success": True,
            "download_url": download_result.package_url
            if hasattr(download_result, "package_url")
            else None,
            "package_size_mb": download_result.package_size_mb
            if hasattr(download_result, "package_size_mb")
            else None,
            "project_id": download_result.metadata.project_id
            if hasattr(download_result, "metadata")
            else None,
            "documentation_url": download_result.documentation_url
            if hasattr(download_result, "documentation_url")
            else None,
        }


class DataValidator:
    """Validate data between agents"""

    @staticmethod
    def validate_nl_input(data: Dict[str, Any]) -> List[str]:
        """Validate NL Input data"""
        errors = []

        required_fields = ["project_type", "features", "technical_requirements"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")

        if "complexity" in data and data["complexity"] not in [
            "simple",
            "medium",
            "complex",
        ]:
            errors.append("Invalid complexity value")

        return errors

    @staticmethod
    def validate_ui_selection(data: Dict[str, Any]) -> List[str]:
        """Validate UI Selection data"""
        errors = []

        if "framework" not in data or not data["framework"]:
            errors.append("Missing framework selection")

        if "bundler" not in data or not data["bundler"]:
            errors.append("Missing bundler selection")

        return errors

    @staticmethod
    def validate_generation_input(data: Dict[str, Any]) -> List[str]:
        """Validate Generation input data"""
        errors = []

        if "file_structure" not in data:
            errors.append("Missing file structure")

        if "components" not in data or not data["components"]:
            errors.append("Missing components list")

        if "libraries" not in data:
            errors.append("Missing libraries information")

        return errors

    @staticmethod
    def validate_pipeline_input(query: str) -> List[str]:
        """Validate initial pipeline input"""
        errors = []

        if not query or not isinstance(query, str):
            errors.append("Query must be a non-empty string")

        if len(query) < 10:
            errors.append("Query is too short (minimum 10 characters)")

        if len(query) > 1000:
            errors.append("Query is too long (maximum 1000 characters)")

        return errors


# Export classes
__all__ = ["DataTransformer", "DataValidator"]
