"""🧬 T-Developer Production Pipeline - Optimized"""
import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS integration (optional)
try:
    import boto3

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False


@dataclass
class PipelineConfig:
    """Pipeline configuration"""

    max_workers: int = 3
    timeout: int = 300
    retry_count: int = 2
    enable_metrics: bool = True
    aws_region: str = "us-east-1"


@dataclass
class PipelineResult:
    """Pipeline execution result"""

    success: bool
    pipeline_id: str
    execution_time: float
    stages_completed: List[str]
    final_output: Dict
    error: Optional[str] = None
    metrics: Optional[Dict] = None


class ProductionPipeline:
    """Production-grade ECS pipeline orchestrator"""

    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.pipeline_id = None
        self.start_time = None
        self.stages = [
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

        # AWS clients (if available)
        if AWS_AVAILABLE:
            try:
                self.cloudwatch = boto3.client("cloudwatch", region_name=self.config.aws_region)
                self.s3 = boto3.client("s3", region_name=self.config.aws_region)
                logger.info("AWS services initialized")
            except Exception as e:
                logger.warning(f"AWS initialization failed: {e}")
                self.cloudwatch = None
                self.s3 = None
        else:
            self.cloudwatch = None
            self.s3 = None

    async def execute(self, input_data: Dict) -> PipelineResult:
        """Execute the production pipeline"""
        self.pipeline_id = f"pipeline_{int(time.time())}"
        self.start_time = time.time()

        logger.info(f"Starting pipeline {self.pipeline_id}")

        try:
            # Initialize pipeline state
            pipeline_state = {
                "input": input_data,
                "current_stage": 0,
                "stage_results": {},
                "metadata": {"start_time": self.start_time, "pipeline_id": self.pipeline_id},
            }

            # Execute stages
            stages_completed = []

            for i, stage_name in enumerate(self.stages):
                logger.info(f"Executing stage: {stage_name}")

                try:
                    # Execute stage with timeout
                    stage_result = await asyncio.wait_for(
                        self._execute_stage(stage_name, pipeline_state), timeout=self.config.timeout
                    )

                    pipeline_state["stage_results"][stage_name] = stage_result
                    stages_completed.append(stage_name)

                    # Update progress
                    await self._update_progress(i + 1, len(self.stages))

                except asyncio.TimeoutError:
                    error_msg = f"Stage {stage_name} timed out"
                    logger.error(error_msg)
                    return self._create_error_result(stages_completed, error_msg)

                except Exception as e:
                    error_msg = f"Stage {stage_name} failed: {str(e)}"
                    logger.error(error_msg)

                    # Retry logic
                    if self.config.retry_count > 0:
                        for retry in range(self.config.retry_count):
                            logger.info(f"Retrying {stage_name}, attempt {retry + 1}")
                            try:
                                stage_result = await asyncio.wait_for(
                                    self._execute_stage(stage_name, pipeline_state),
                                    timeout=self.config.timeout,
                                )
                                pipeline_state["stage_results"][stage_name] = stage_result
                                stages_completed.append(stage_name)
                                break
                            except Exception as retry_e:
                                if retry == self.config.retry_count - 1:
                                    return self._create_error_result(stages_completed, str(retry_e))
                                continue
                    else:
                        return self._create_error_result(stages_completed, error_msg)

            # Create success result
            execution_time = time.time() - self.start_time
            final_output = self._compile_final_output(pipeline_state)

            result = PipelineResult(
                success=True,
                pipeline_id=self.pipeline_id,
                execution_time=execution_time,
                stages_completed=stages_completed,
                final_output=final_output,
                metrics=self._collect_metrics(pipeline_state),
            )

            # Send metrics to CloudWatch
            if self.config.enable_metrics and self.cloudwatch:
                await self._send_metrics(result)

            logger.info(
                f"Pipeline {self.pipeline_id} completed successfully in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            logger.error(error_msg)
            return self._create_error_result([], error_msg)

    async def _execute_stage(self, stage_name: str, pipeline_state: Dict) -> Dict:
        """Execute individual pipeline stage"""
        # Import agents dynamically to reduce memory usage
        agent_map = {
            "nl_input": "src.agents.unified.nl_input.agent.NLInputAgent",
            "ui_selection": "src.agents.unified.ui_selection.agent.UISelectionAgent",
            "parser": "src.agents.unified.parser.agent.ParserAgent",
            "component_decision": "src.agents.unified.component_decision.agent.ComponentDecisionAgent",
            "match_rate": "src.agents.unified.match_rate.agent.MatchRateAgent",
            "search": "src.agents.unified.search.agent.SearchAgent",
            "generation": "src.agents.unified.generation.agent.GenerationAgent",
            "assembly": "src.agents.unified.assembly.agent.AssemblyAgent",
            "download": "src.agents.unified.download.agent.DownloadAgent",
        }

        if stage_name not in agent_map:
            raise ValueError(f"Unknown stage: {stage_name}")

        # Dynamic import and execution
        module_path = agent_map[stage_name]
        module_name, class_name = module_path.rsplit(".", 1)

        try:
            module = __import__(module_name, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            agent = agent_class()

            # Prepare input for this stage
            stage_input = self._prepare_stage_input(stage_name, pipeline_state)

            # Execute agent
            result = await agent.process(stage_input)

            return {
                "success": True,
                "output": result,
                "execution_time": time.time() - pipeline_state["metadata"]["start_time"],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - pipeline_state["metadata"]["start_time"],
            }

    def _prepare_stage_input(self, stage_name: str, pipeline_state: Dict) -> Any:
        """Prepare input data for specific stage"""
        if stage_name == "nl_input":
            return pipeline_state["input"]

        # For subsequent stages, use output from previous stage
        stage_results = pipeline_state["stage_results"]

        if stage_name == "ui_selection":
            return stage_results.get("nl_input", {}).get("output", {})

        # Chain outputs from previous stages
        prev_stage_index = self.stages.index(stage_name) - 1
        if prev_stage_index >= 0:
            prev_stage = self.stages[prev_stage_index]
            return stage_results.get(prev_stage, {}).get("output", {})

        return {}

    def _compile_final_output(self, pipeline_state: Dict) -> Dict:
        """Compile final output from all stages"""
        final_output = {
            "pipeline_id": self.pipeline_id,
            "execution_time": time.time() - self.start_time,
            "stages": {},
        }

        # Collect outputs from all stages
        for stage_name, stage_result in pipeline_state["stage_results"].items():
            if stage_result.get("success"):
                final_output["stages"][stage_name] = stage_result["output"]

        # The final output is from the download stage
        download_result = pipeline_state["stage_results"].get("download", {})
        if download_result.get("success"):
            final_output.update(download_result["output"])

        return final_output

    def _collect_metrics(self, pipeline_state: Dict) -> Dict:
        """Collect execution metrics"""
        metrics = {
            "total_execution_time": time.time() - self.start_time,
            "stages_executed": len(pipeline_state["stage_results"]),
            "successful_stages": sum(
                1 for r in pipeline_state["stage_results"].values() if r.get("success")
            ),
            "stage_timings": {},
        }

        for stage_name, result in pipeline_state["stage_results"].items():
            metrics["stage_timings"][stage_name] = result.get("execution_time", 0)

        return metrics

    async def _update_progress(self, completed: int, total: int):
        """Update pipeline progress"""
        progress = (completed / total) * 100
        logger.info(f"Pipeline progress: {progress:.1f}% ({completed}/{total})")

    async def _send_metrics(self, result: PipelineResult):
        """Send metrics to CloudWatch"""
        if not self.cloudwatch:
            return

        try:
            metrics_data = [
                {
                    "MetricName": "PipelineExecutionTime",
                    "Value": result.execution_time,
                    "Unit": "Seconds",
                    "Dimensions": [{"Name": "PipelineId", "Value": result.pipeline_id}],
                },
                {
                    "MetricName": "StagesCompleted",
                    "Value": len(result.stages_completed),
                    "Unit": "Count",
                    "Dimensions": [{"Name": "PipelineId", "Value": result.pipeline_id}],
                },
            ]

            self.cloudwatch.put_metric_data(
                Namespace="T-Developer/Production", MetricData=metrics_data
            )
        except Exception as e:
            logger.warning(f"Failed to send metrics: {e}")

    def _create_error_result(self, stages_completed: List[str], error_msg: str) -> PipelineResult:
        """Create error result"""
        execution_time = time.time() - self.start_time if self.start_time else 0

        return PipelineResult(
            success=False,
            pipeline_id=self.pipeline_id or "unknown",
            execution_time=execution_time,
            stages_completed=stages_completed,
            final_output={},
            error=error_msg,
        )


# Convenience functions
async def run_production_pipeline(
    input_data: Dict, config: PipelineConfig = None
) -> PipelineResult:
    """Run production pipeline with given input"""
    pipeline = ProductionPipeline(config)
    return await pipeline.execute(input_data)


def create_pipeline_config(**kwargs) -> PipelineConfig:
    """Create pipeline configuration"""
    return PipelineConfig(**kwargs)
