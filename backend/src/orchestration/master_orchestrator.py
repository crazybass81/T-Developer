"""
Master Orchestrator for T-Developer 9-Agent Pipeline
Coordinates all agents with error handling, monitoring, and optimization
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from ..agents.unified.nl_input import NLInputAgent
from ..agents.unified.ui_selection import UISelectionAgent
from ..agents.unified.parser import ParserAgent
from ..agents.unified.component_decision import ComponentDecisionAgent
from ..agents.unified.match_rate import MatchRateAgent
from ..agents.unified.search import SearchAgent
from ..agents.unified.generation import GenerationAgent
from ..agents.unified.assembly import AssemblyAgent
from ..agents.unified.download import DownloadAgent

from ..core.interfaces import PipelineContext, AgentResult
from ..core.state_manager import PipelineStateManager
from ..core.monitoring import MetricsCollector
from ..core.event_bus import EventBus

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
            PipelineStage.DOWNLOAD: DownloadAgent()
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
        self, 
        user_input: str, 
        context_data: Optional[Dict[str, Any]] = None
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
                user_input=user_input
            )
            
            # Start monitoring
            if self.metrics_collector:
                await self.metrics_collector.start_pipeline_tracking(self.context.project_id)
            
            await self._emit_event("pipeline_started", {
                "project_id": self.context.project_id,
                "user_input": user_input
            })
            
            # Execute pipeline stages
            pipeline_result = await self._execute_sequential_pipeline()
            
            # Finalize and return results
            total_time = (datetime.now() - self.start_time).total_seconds()
            
            final_result = {
                "success": True,
                "project_id": self.context.project_id,
                "execution_time": total_time,
                "pipeline_result": pipeline_result,
                "stage_results": {stage.value: result.__dict__ for stage, result in self.stage_results.items()},
                "performance_metrics": await self._generate_performance_report()
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
                "stage_results": {stage.value: result.__dict__ for stage, result in self.stage_results.items()}
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
            PipelineStage.DOWNLOAD
        ]
        
        # Execute each stage
        for stage in execution_order:\n            self.current_stage = stage\n            \n            # Check if we can use parallel execution\n            if self.config.enable_parallel_processing and stage in self.parallel_stages:\n                stage_result = await self._execute_parallel_stages([stage], stage_data)\n                stage_data.update(stage_result)\n            else:\n                stage_result = await self._execute_single_stage(stage, stage_data)\n                stage_data.update(stage_result)\n            \n            # Save checkpoint if configured\n            if len(self.stage_results) % self.config.checkpoint_interval == 0:\n                await self._save_checkpoint()\n        \n        return stage_data\n    \n    async def _execute_single_stage(\n        self, \n        stage: PipelineStage, \n        input_data: Dict[str, Any]\n    ) -> Dict[str, Any]:\n        \"\"\"Execute a single pipeline stage with retry logic\"\"\"\n        \n        agent = self.agents[stage]\n        retry_count = 0\n        last_error = None\n        \n        while retry_count <= self.config.max_retry_attempts:\n            try:\n                stage_start = datetime.now()\n                \n                # Check cache first\n                cache_key = self._generate_cache_key(stage, input_data)\n                if self.config.enable_caching and cache_key in self.result_cache:\n                    cached_result = self.result_cache[cache_key]\n                    \n                    self.stage_results[stage] = StageResult(\n                        stage=stage,\n                        success=True,\n                        data=cached_result,\n                        execution_time=0.0,\n                        memory_usage=0.0,\n                        cached=True\n                    )\n                    \n                    logger.info(f\"Using cached result for {stage.value}\")\n                    return cached_result\n                \n                # Execute agent\n                logger.info(f\"Executing {stage.value} (attempt {retry_count + 1})\")\n                \n                if asyncio.iscoroutinefunction(agent.process):\n                    result = await asyncio.wait_for(\n                        agent.process(input_data),\n                        timeout=self.config.timeout_seconds\n                    )\n                else:\n                    # Run synchronous agent in thread pool\n                    result = await asyncio.get_event_loop().run_in_executor(\n                        None, agent.process, input_data\n                    )\n                \n                execution_time = (datetime.now() - stage_start).total_seconds()\n                memory_usage = self._get_memory_usage()\n                \n                # Validate result\n                if not self._validate_stage_result(stage, result):\n                    raise ValueError(f\"Invalid result from {stage.value}\")\n                \n                # Cache result if successful\n                if self.config.enable_caching:\n                    self.result_cache[cache_key] = result\n                \n                # Record stage result\n                self.stage_results[stage] = StageResult(\n                    stage=stage,\n                    success=True,\n                    data=result,\n                    execution_time=execution_time,\n                    memory_usage=memory_usage,\n                    retry_count=retry_count\n                )\n                \n                # Emit stage completion event\n                await self._emit_event(f\"stage_completed_{stage.value}\", {\n                    \"stage\": stage.value,\n                    \"execution_time\": execution_time,\n                    \"retry_count\": retry_count\n                })\n                \n                logger.info(f\"Completed {stage.value} in {execution_time:.2f}s\")\n                return result\n                \n            except asyncio.TimeoutError:\n                last_error = f\"{stage.value} timed out after {self.config.timeout_seconds}s\"\n                logger.warning(last_error)\n                \n            except Exception as e:\n                last_error = f\"{stage.value} failed: {str(e)}\"\n                logger.warning(f\"{last_error} (attempt {retry_count + 1})\")\n                \n                # Apply custom error handling if available\n                if type(e) in self.error_handlers:\n                    await self.error_handlers[type(e)](e, stage, input_data)\n            \n            retry_count += 1\n            \n            # Apply retry strategy if available\n            if stage in self.retry_strategies and retry_count <= self.config.max_retry_attempts:\n                await self.retry_strategies[stage](retry_count, last_error)\n            else:\n                # Default backoff strategy\n                await asyncio.sleep(min(2 ** retry_count, 10))\n        \n        # All retries exhausted\n        execution_time = (datetime.now() - stage_start).total_seconds()\n        \n        self.stage_results[stage] = StageResult(\n            stage=stage,\n            success=False,\n            data={},\n            execution_time=execution_time,\n            memory_usage=self._get_memory_usage(),\n            error_message=last_error,\n            retry_count=retry_count - 1\n        )\n        \n        await self._emit_event(f\"stage_failed_{stage.value}\", {\n            \"stage\": stage.value,\n            \"error\": last_error,\n            \"retry_count\": retry_count - 1\n        })\n        \n        raise RuntimeError(f\"Stage {stage.value} failed after {retry_count} attempts: {last_error}\")\n    \n    async def _execute_parallel_stages(\n        self, \n        stages: List[PipelineStage], \n        input_data: Dict[str, Any]\n    ) -> Dict[str, Any]:\n        \"\"\"Execute multiple stages in parallel\"\"\"\n        \n        tasks = []\n        for stage in stages:\n            task = asyncio.create_task(\n                self._execute_single_stage(stage, input_data),\n                name=f\"stage_{stage.value}\"\n            )\n            tasks.append(task)\n        \n        results = await asyncio.gather(*tasks, return_exceptions=True)\n        \n        combined_result = {}\n        for i, result in enumerate(results):\n            if isinstance(result, Exception):\n                raise result\n            combined_result.update(result)\n        \n        return combined_result\n    \n    def _identify_parallel_stages(self) -> List[PipelineStage]:\n        \"\"\"Identify stages that can be executed in parallel\"\"\"\n        \n        # In current pipeline, stages are mostly sequential\n        # But some optimization analysis could be parallel with generation\n        parallel_stages = []\n        \n        # Future: Could run certain analysis in parallel\n        # parallel_stages = [PipelineStage.MATCH_RATE, PipelineStage.SEARCH]\n        \n        return parallel_stages\n    \n    def _generate_cache_key(self, stage: PipelineStage, input_data: Dict[str, Any]) -> str:\n        \"\"\"Generate cache key for stage result\"\"\"\n        \n        import hashlib\n        import json\n        \n        # Create a simplified key based on stage and critical input data\n        cache_data = {\n            \"stage\": stage.value,\n            \"user_input\": input_data.get(\"user_input\", \"\"),\n            \"framework\": input_data.get(\"framework\", \"\"),\n            \"project_type\": input_data.get(\"project_type\", \"\")\n        }\n        \n        cache_string = json.dumps(cache_data, sort_keys=True)\n        return hashlib.md5(cache_string.encode()).hexdigest()\n    \n    def _validate_stage_result(self, stage: PipelineStage, result: Any) -> bool:\n        \"\"\"Validate stage result format and content\"\"\"\n        \n        if not isinstance(result, dict):\n            return False\n        \n        # Stage-specific validation\n        stage_validators = {\n            PipelineStage.NL_INPUT: lambda r: \"requirements\" in r and \"intent\" in r,\n            PipelineStage.UI_SELECTION: lambda r: \"framework\" in r and \"components\" in r,\n            PipelineStage.PARSER: lambda r: \"structure\" in r and \"dependencies\" in r,\n            PipelineStage.COMPONENT_DECISION: lambda r: \"architecture\" in r,\n            PipelineStage.MATCH_RATE: lambda r: \"match_score\" in r,\n            PipelineStage.SEARCH: lambda r: \"search_results\" in r,\n            PipelineStage.GENERATION: lambda r: \"generated_files\" in r,\n            PipelineStage.ASSEMBLY: lambda r: \"assembled_project\" in r,\n            PipelineStage.DOWNLOAD: lambda r: \"download_url\" in r\n        }\n        \n        validator = stage_validators.get(stage)\n        if validator:\n            return validator(result)\n        \n        return True\n    \n    def _get_memory_usage(self) -> float:\n        \"\"\"Get current memory usage in MB\"\"\"\n        \n        try:\n            import psutil\n            process = psutil.Process()\n            return process.memory_info().rss / 1024 / 1024\n        except:\n            return 0.0\n    \n    async def _save_checkpoint(self) -> None:\n        \"\"\"Save pipeline state checkpoint\"\"\"\n        \n        checkpoint_data = {\n            \"project_id\": self.context.project_id,\n            \"current_stage\": self.current_stage.value,\n            \"stage_results\": {stage.value: result.__dict__ for stage, result in self.stage_results.items()},\n            \"timestamp\": datetime.now().isoformat()\n        }\n        \n        await self.state_manager.save_checkpoint(\n            self.context.project_id, \n            checkpoint_data\n        )\n        \n        logger.info(f\"Checkpoint saved for {self.context.project_id}\")\n    \n    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:\n        \"\"\"Emit pipeline event\"\"\"\n        \n        try:\n            await self.event_bus.emit(event_type, {\n                \"project_id\": self.context.project_id if self.context else \"unknown\",\n                \"timestamp\": datetime.now().isoformat(),\n                **data\n            })\n        except Exception as e:\n            logger.warning(f\"Failed to emit event {event_type}: {str(e)}\")\n    \n    async def _generate_performance_report(self) -> Dict[str, Any]:\n        \"\"\"Generate comprehensive performance report\"\"\"\n        \n        if not self.metrics_collector:\n            return {}\n        \n        total_time = (datetime.now() - self.start_time).total_seconds()\n        \n        stage_times = {\n            stage.value: result.execution_time \n            for stage, result in self.stage_results.items()\n        }\n        \n        memory_usage = {\n            stage.value: result.memory_usage \n            for stage, result in self.stage_results.items()\n        }\n        \n        return {\n            \"total_execution_time\": total_time,\n            \"stage_execution_times\": stage_times,\n            \"stage_memory_usage\": memory_usage,\n            \"cache_hit_rate\": self._calculate_cache_hit_rate(),\n            \"retry_counts\": {\n                stage.value: result.retry_count \n                for stage, result in self.stage_results.items()\n            },\n            \"success_rate\": len([r for r in self.stage_results.values() if r.success]) / len(self.stage_results),\n            \"bottleneck_stage\": max(stage_times.items(), key=lambda x: x[1])[0] if stage_times else None\n        }\n    \n    def _calculate_cache_hit_rate(self) -> float:\n        \"\"\"Calculate cache hit rate\"\"\"\n        \n        if not self.stage_results:\n            return 0.0\n        \n        cached_results = len([r for r in self.stage_results.values() if r.cached])\n        total_results = len(self.stage_results)\n        \n        return cached_results / total_results\n    \n    async def resume_pipeline(self, project_id: str) -> Dict[str, Any]:\n        \"\"\"Resume pipeline from last checkpoint\"\"\"\n        \n        try:\n            checkpoint = await self.state_manager.load_checkpoint(project_id)\n            \n            if not checkpoint:\n                raise ValueError(f\"No checkpoint found for project {project_id}\")\n            \n            logger.info(f\"Resuming pipeline {project_id} from {checkpoint['current_stage']}\")\n            \n            # Restore state\n            self.context = PipelineContext(\n                project_id=project_id,\n                timestamp=datetime.fromisoformat(checkpoint['timestamp']),\n                metadata={}\n            )\n            \n            self.current_stage = PipelineStage(checkpoint['current_stage'])\n            \n            # Rebuild stage results\n            for stage_name, result_data in checkpoint['stage_results'].items():\n                stage = PipelineStage(stage_name)\n                self.stage_results[stage] = StageResult(**result_data)\n            \n            # Continue execution from current stage\n            return await self._execute_sequential_pipeline()\n            \n        except Exception as e:\n            logger.error(f\"Failed to resume pipeline {project_id}: {str(e)}\")\n            raise\n    \n    def add_error_handler(self, exception_type: type, handler: Callable) -> None:\n        \"\"\"Add custom error handler for specific exception types\"\"\"\n        \n        self.error_handlers[exception_type] = handler\n    \n    def add_retry_strategy(self, stage: PipelineStage, strategy: Callable) -> None:\n        \"\"\"Add custom retry strategy for specific stages\"\"\"\n        \n        self.retry_strategies[stage] = strategy\n    \n    async def get_pipeline_status(self, project_id: str) -> Dict[str, Any]:\n        \"\"\"Get current pipeline status\"\"\"\n        \n        return {\n            \"project_id\": project_id,\n            \"current_stage\": self.current_stage.value if self.current_stage else \"not_started\",\n            \"completed_stages\": [stage.value for stage in self.stage_results.keys()],\n            \"success_rate\": len([r for r in self.stage_results.values() if r.success]) / len(self.stage_results) if self.stage_results else 0,\n            \"total_execution_time\": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,\n            \"is_running\": self.current_stage not in [PipelineStage.COMPLETE, PipelineStage.ERROR]\n        }\n    \n    async def cleanup(self) -> None:\n        \"\"\"Cleanup resources and connections\"\"\"\n        \n        try:\n            # Clear cache\n            self.result_cache.clear()\n            \n            # Close connections\n            if self.metrics_collector:\n                await self.metrics_collector.close()\n            \n            await self.event_bus.close()\n            await self.state_manager.close()\n            \n            logger.info(\"MasterOrchestrator cleanup completed\")\n            \n        except Exception as e:\n            logger.error(f\"Error during cleanup: {str(e)}\")