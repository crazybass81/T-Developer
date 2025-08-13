"""
Master Orchestrator for T-Developer 9-Agent Pipeline
Coordinates all agents with error handling, monitoring, and optimization
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..agents.unified.assembly import AssemblyAgent
from ..agents.unified.component_decision import ComponentDecisionAgent
from ..agents.unified.download import DownloadAgent
from ..agents.unified.generation import GenerationAgent
from ..agents.unified.match_rate import MatchRateAgent
from ..agents.unified.nl_input import NLInputAgent
from ..agents.unified.parser import ParserAgent
from ..agents.unified.search import SearchAgent
from ..agents.unified.ui_selection import UISelectionAgent
from ..core.event_bus import EventBus
from ..core.interfaces import AgentResult, PipelineContext
from ..core.monitoring import MetricsCollector
from ..core.state_manager import PipelineStateManager

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline execution stages"""

    INIT = "initialization"
    NL_INPUT = "nl_input"
    UI_SELECTION = "ui_selection"
    PARSER = "parser"
    COMPONENT_DECISION = "component_decision"
    MATCH_RATE = "match_rate"
    SEARCH = "search"
    GENERATION = "generation"
    ASSEMBLY = "assembly"
    DOWNLOAD = "download"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class PipelineConfig:
    """Pipeline configuration settings"""

    enable_parallel_processing: bool = True
    max_retry_attempts: int = 3
    timeout_seconds: int = 300
    checkpoint_interval: int = 2  # Save state every N stages
    enable_monitoring: bool = True
    enable_caching: bool = True
    debug_mode: bool = False
    performance_tracking: bool = True


@dataclass
class StageResult:
    """Result of a pipeline stage execution"""

    stage: PipelineStage
    success: bool
    data: Dict[str, Any]
    execution_time: float
    memory_usage: float
    error_message: str = ""
    retry_count: int = 0
    cached: bool = False
    metrics: Dict[str, float] = field(default_factory=dict)


class MasterOrchestrator:
    """
    Master Orchestrator for the 9-Agent Pipeline
    Handles execution flow, error recovery, monitoring, and optimization
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()

        # Initialize agents
        self.agents = {
            PipelineStage.NL_INPUT: NLInputAgent(),
            PipelineStage.UI_SELECTION: UISelectionAgent(),
            PipelineStage.PARSER: ParserAgent(),
            PipelineStage.COMPONENT_DECISION: ComponentDecisionAgent(),
            PipelineStage.MATCH_RATE: MatchRateAgent(),
            PipelineStage.SEARCH: SearchAgent(),
            PipelineStage.GENERATION: GenerationAgent(),
            PipelineStage.ASSEMBLY: AssemblyAgent(),
            PipelineStage.DOWNLOAD: DownloadAgent(),
        }

        # Initialize infrastructure
        self.state_manager = PipelineStateManager()
        self.metrics_collector = MetricsCollector() if config.enable_monitoring else None
        self.event_bus = EventBus()

        # Execution state
        self.current_stage = PipelineStage.INIT
        self.stage_results: Dict[PipelineStage, StageResult] = {}
        self.start_time = None
        self.context: Optional[PipelineContext] = None

        # Performance optimization
        self.result_cache: Dict[str, Any] = {}
        self.parallel_stages = self._identify_parallel_stages()

        # Error handling
        self.error_handlers: Dict[Exception, Callable] = {}
        self.retry_strategies: Dict[PipelineStage, Callable] = {}

        logger.info(f"MasterOrchestrator initialized with config: {self.config}")

    async def execute_pipeline(
        self, user_input: str, context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete 9-agent pipeline
        """
        self.start_time = datetime.now()

        try:
            # Initialize context
            self.context = PipelineContext(
                project_id=f"project_{int(time.time())}",
                timestamp=self.start_time,
                metadata=context_data or {},
                user_input=user_input,
            )

            # Start monitoring
            if self.metrics_collector:
                await self.metrics_collector.start_pipeline_tracking(self.context.project_id)

            await self._emit_event(
                "pipeline_started",
                {"project_id": self.context.project_id, "user_input": user_input},
            )

            # Execute pipeline stages
            pipeline_result = await self._execute_sequential_pipeline()

            # Finalize and return results
            total_time = (datetime.now() - self.start_time).total_seconds()

            final_result = {
                "success": True,
                "project_id": self.context.project_id,
                "execution_time": total_time,
                "pipeline_result": pipeline_result,
                "stage_results": {
                    stage.value: result.__dict__ for stage, result in self.stage_results.items()
                },
                "performance_metrics": await self._generate_performance_report(),
            }

            await self._emit_event("pipeline_completed", final_result)

            logger.info(f"Pipeline completed successfully in {total_time:.2f}s")
            return final_result

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")

            error_result = {
                "success": False,
                "project_id": self.context.project_id if self.context else "unknown",
                "error": str(e),
                "execution_time": (datetime.now() - self.start_time).total_seconds(),
                "current_stage": self.current_stage.value,
                "stage_results": {
                    stage.value: result.__dict__ for stage, result in self.stage_results.items()
                },
            }

            await self._emit_event("pipeline_failed", error_result)
            return error_result

    async def _execute_sequential_pipeline(self) -> Dict[str, Any]:
        """Execute pipeline stages in sequence with error handling"""

        stage_data = {"user_input": self.context.user_input}

        # Define execution order
        execution_order = [
            PipelineStage.NL_INPUT,
            PipelineStage.UI_SELECTION,
            PipelineStage.PARSER,
            PipelineStage.COMPONENT_DECISION,
            PipelineStage.MATCH_RATE,
            PipelineStage.SEARCH,
            PipelineStage.GENERATION,
            PipelineStage.ASSEMBLY,
            PipelineStage.DOWNLOAD,
        ]

        # Execute each stage
        for stage in execution_order:
            self.current_stage = stage

            # Check if we can use parallel execution
            if self.config.enable_parallel_processing and stage in self.parallel_stages:
                stage_result = await self._execute_parallel_stages([stage], stage_data)
                stage_data.update(stage_result)
            else:
                stage_result = await self._execute_single_stage(stage, stage_data)
                stage_data.update(stage_result)

            # Save checkpoint if configured
            if len(self.stage_results) % self.config.checkpoint_interval == 0:
                await self._save_checkpoint()

        return stage_data

    async def _execute_single_stage(
        self, stage: PipelineStage, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single pipeline stage with retry logic"""

        agent = self.agents[stage]
        retry_count = 0
        last_error = None

        while retry_count <= self.config.max_retry_attempts:
            try:
                stage_start = datetime.now()

                # Check cache first
                cache_key = self._generate_cache_key(stage, input_data)
                if self.config.enable_caching and cache_key in self.result_cache:
                    cached_result = self.result_cache[cache_key]

                    self.stage_results[stage] = StageResult(
                        stage=stage,
                        success=True,
                        data=cached_result,
                        execution_time=0.0,
                        memory_usage=0.0,
                        cached=True,
                    )

                    logger.info(f"Using cached result for {stage.value}")
                    return cached_result

                # Execute agent
                logger.info(f"Executing {stage.value} (attempt {retry_count + 1})")

                if asyncio.iscoroutinefunction(agent.process):
                    result = await asyncio.wait_for(
                        agent.process(input_data), timeout=self.config.timeout_seconds
                    )
                else:
                    # Run synchronous agent in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, agent.process, input_data
                    )

                execution_time = (datetime.now() - stage_start).total_seconds()
                memory_usage = self._get_memory_usage()

                # Validate result
                if not self._validate_stage_result(stage, result):
                    raise ValueError(f"Invalid result from {stage.value}")

                # Cache result if successful
                if self.config.enable_caching:
                    self.result_cache[cache_key] = result

                # Record stage result
                self.stage_results[stage] = StageResult(
                    stage=stage,
                    success=True,
                    data=result,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    retry_count=retry_count,
                )

                # Emit stage completion event
                await self._emit_event(
                    f"stage_completed_{stage.value}",
                    {
                        "stage": stage.value,
                        "execution_time": execution_time,
                        "retry_count": retry_count,
                    },
                )

                logger.info(f"Completed {stage.value} in {execution_time:.2f}s")
                return result

            except asyncio.TimeoutError:
                last_error = f"{stage.value} timed out after {self.config.timeout_seconds}s"
                logger.warning(last_error)

            except Exception as e:
                last_error = f"{stage.value} failed: {str(e)}"
                logger.warning(f"{last_error} (attempt {retry_count + 1})")

                # Apply custom error handling if available
                if type(e) in self.error_handlers:
                    await self.error_handlers[type(e)](e, stage, input_data)

            retry_count += 1

            # Apply retry strategy if available
            if stage in self.retry_strategies and retry_count <= self.config.max_retry_attempts:
                await self.retry_strategies[stage](retry_count, last_error)
            else:
                # Default backoff strategy
                await asyncio.sleep(min(2**retry_count, 10))

        # All retries exhausted
        execution_time = (datetime.now() - stage_start).total_seconds()

        self.stage_results[stage] = StageResult(
            stage=stage,
            success=False,
            data={},
            execution_time=execution_time,
            memory_usage=self._get_memory_usage(),
            error_message=last_error,
            retry_count=retry_count - 1,
        )

        await self._emit_event(
            f"stage_failed_{stage.value}",
            {"stage": stage.value, "error": last_error, "retry_count": retry_count - 1},
        )

        raise RuntimeError(f"Stage {stage.value} failed after {retry_count} attempts: {last_error}")

    async def _execute_parallel_stages(
        self, stages: List[PipelineStage], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute multiple stages in parallel"""

        tasks = []
        for stage in stages:
            task = asyncio.create_task(
                self._execute_single_stage(stage, input_data),
                name=f"stage_{stage.value}",
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_result = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise result
            combined_result.update(result)

        return combined_result

    def _identify_parallel_stages(self) -> List[PipelineStage]:
        """Identify stages that can be executed in parallel"""

        # In current pipeline, stages are mostly sequential
        # But some optimization analysis could be parallel with generation
        parallel_stages = []

        # Future: Could run certain analysis in parallel
        # parallel_stages = [PipelineStage.MATCH_RATE, PipelineStage.SEARCH]

        return parallel_stages

    def _generate_cache_key(self, stage: PipelineStage, input_data: Dict[str, Any]) -> str:
        """Generate cache key for stage result"""

        import hashlib
        import json

        # Create a simplified key based on stage and critical input data
        cache_data = {
            "stage": stage.value,
            "user_input": input_data.get("user_input", ""),
            "framework": input_data.get("framework", ""),
            "project_type": input_data.get("project_type", ""),
        }

        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _validate_stage_result(self, stage: PipelineStage, result: Any) -> bool:
        """Validate stage result format and content"""

        if not isinstance(result, dict):
            return False

        # Stage-specific validation
        stage_validators = {
            PipelineStage.NL_INPUT: lambda r: "requirements" in r and "intent" in r,
            PipelineStage.UI_SELECTION: lambda r: "framework" in r and "components" in r,
            PipelineStage.PARSER: lambda r: "structure" in r and "dependencies" in r,
            PipelineStage.COMPONENT_DECISION: lambda r: "architecture" in r,
            PipelineStage.MATCH_RATE: lambda r: "match_score" in r,
            PipelineStage.SEARCH: lambda r: "search_results" in r,
            PipelineStage.GENERATION: lambda r: "generated_files" in r,
            PipelineStage.ASSEMBLY: lambda r: "assembled_project" in r,
            PipelineStage.DOWNLOAD: lambda r: "download_url" in r,
        }

        validator = stage_validators.get(stage)
        if validator:
            return validator(result)

        return True

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""

        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0

    async def _save_checkpoint(self) -> None:
        """Save pipeline state checkpoint"""

        checkpoint_data = {
            "project_id": self.context.project_id,
            "current_stage": self.current_stage.value,
            "stage_results": {
                stage.value: result.__dict__ for stage, result in self.stage_results.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

        await self.state_manager.save_checkpoint(self.context.project_id, checkpoint_data)

        logger.info(f"Checkpoint saved for {self.context.project_id}")

    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit pipeline event"""

        try:
            await self.event_bus.emit(
                event_type,
                {
                    "project_id": self.context.project_id if self.context else "unknown",
                    "timestamp": datetime.now().isoformat(),
                    **data,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to emit event {event_type}: {str(e)}")

    async def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""

        if not self.metrics_collector:
            return {}

        total_time = (datetime.now() - self.start_time).total_seconds()

        stage_times = {
            stage.value: result.execution_time for stage, result in self.stage_results.items()
        }

        memory_usage = {
            stage.value: result.memory_usage for stage, result in self.stage_results.items()
        }

        return {
            "total_execution_time": total_time,
            "stage_execution_times": stage_times,
            "stage_memory_usage": memory_usage,
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "retry_counts": {
                stage.value: result.retry_count for stage, result in self.stage_results.items()
            },
            "success_rate": len([r for r in self.stage_results.values() if r.success])
            / len(self.stage_results),
            "bottleneck_stage": max(stage_times.items(), key=lambda x: x[1])[0]
            if stage_times
            else None,
        }

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""

        if not self.stage_results:
            return 0.0

        cached_results = len([r for r in self.stage_results.values() if r.cached])
        total_results = len(self.stage_results)

        return cached_results / total_results

    async def resume_pipeline(self, project_id: str) -> Dict[str, Any]:
        """Resume pipeline from last checkpoint"""

        try:
            checkpoint = await self.state_manager.load_checkpoint(project_id)

            if not checkpoint:
                raise ValueError(f"No checkpoint found for project {project_id}")

            logger.info(f"Resuming pipeline {project_id} from {checkpoint['current_stage']}")

            # Restore state
            self.context = PipelineContext(
                project_id=project_id,
                timestamp=datetime.fromisoformat(checkpoint["timestamp"]),
                metadata={},
            )

            self.current_stage = PipelineStage(checkpoint["current_stage"])

            # Rebuild stage results
            for stage_name, result_data in checkpoint["stage_results"].items():
                stage = PipelineStage(stage_name)
                self.stage_results[stage] = StageResult(**result_data)

            # Continue execution from current stage
            return await self._execute_sequential_pipeline()

        except Exception as e:
            logger.error(f"Failed to resume pipeline {project_id}: {str(e)}")
            raise

    def add_error_handler(self, exception_type: type, handler: Callable) -> None:
        """Add custom error handler for specific exception types"""

        self.error_handlers[exception_type] = handler

    def add_retry_strategy(self, stage: PipelineStage, strategy: Callable) -> None:
        """Add custom retry strategy for specific stages"""

        self.retry_strategies[stage] = strategy

    async def get_pipeline_status(self, project_id: str) -> Dict[str, Any]:
        """Get current pipeline status"""

        return {
            "project_id": project_id,
            "current_stage": self.current_stage.value if self.current_stage else "not_started",
            "completed_stages": [stage.value for stage in self.stage_results.keys()],
            "success_rate": len([r for r in self.stage_results.values() if r.success])
            / len(self.stage_results)
            if self.stage_results
            else 0,
            "total_execution_time": (datetime.now() - self.start_time).total_seconds()
            if self.start_time
            else 0,
            "is_running": self.current_stage not in [PipelineStage.COMPLETE, PipelineStage.ERROR],
        }

    async def cleanup(self) -> None:
        """Cleanup resources and connections"""

        try:
            # Clear cache
            self.result_cache.clear()

            # Close connections
            if self.metrics_collector:
                await self.metrics_collector.close()

            await self.event_bus.close()
            await self.state_manager.close()

            logger.info("MasterOrchestrator cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
