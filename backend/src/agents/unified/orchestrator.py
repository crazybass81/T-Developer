"""
Unified Agent Orchestrator - Final Production Version
Orchestrates the 9-agent pipeline with enterprise features
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json

from .unified_agents import (
    UnifiedNLInputAgent,
    UnifiedUISelectionAgent,
    UnifiedParserAgent,
    UnifiedComponentDecisionAgent,
    UnifiedMatchRateAgent,
    UnifiedSearchAgent,
    UnifiedGenerationAgent,
    UnifiedAssemblyAgent,
    UnifiedDownloadAgent
)

from ..enterprise.base_agent import AgentContext

# AWS imports for production
try:
    from aws_lambda_powertools import Logger, Tracer, Metrics
    from aws_lambda_powertools.metrics import MetricUnit
    logger = Logger()
    tracer = Tracer()
    metrics = Metrics()
    AWS_ENABLED = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    AWS_ENABLED = False


class UnifiedOrchestrator:
    """
    Orchestrates the complete 9-agent pipeline
    Handles workflow, error recovery, and monitoring
    """
    
    def __init__(self):
        # Initialize all agents
        self.agents = {
            "nl_input": UnifiedNLInputAgent(),
            "ui_selection": UnifiedUISelectionAgent(),
            "parser": UnifiedParserAgent(),
            "component_decision": UnifiedComponentDecisionAgent(),
            "match_rate": UnifiedMatchRateAgent(),
            "search": UnifiedSearchAgent(),
            "generation": UnifiedGenerationAgent(),
            "assembly": UnifiedAssemblyAgent(),
            "download": UnifiedDownloadAgent()
        }
        
        # Pipeline configuration
        self.pipeline = [
            "nl_input",
            "ui_selection", 
            "parser",
            "component_decision",
            "match_rate",
            "search",
            "generation",
            "assembly",
            "download"
        ]
        
        # State management
        self.state = {}
        self.context = None
        
    async def initialize(self):
        """Initialize all agents"""
        logger.info("Initializing orchestrator and agents")
        
        init_tasks = []
        for agent_name, agent in self.agents.items():
            init_tasks.append(self._initialize_agent(agent_name, agent))
        
        results = await asyncio.gather(*init_tasks, return_exceptions=True)
        
        # Check for initialization failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_name = list(self.agents.keys())[i]
                logger.error(f"Failed to initialize {agent_name}: {result}")
        
        logger.info("Orchestrator initialization complete")
    
    async def _initialize_agent(self, name: str, agent):
        """Initialize individual agent"""
        try:
            await agent.initialize()
            logger.info(f"Initialized {name} agent")
        except Exception as e:
            logger.error(f"Error initializing {name}: {e}")
            raise
    
    async def execute_pipeline(
        self,
        query: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete 9-agent pipeline
        """
        
        # Create execution context
        self.context = AgentContext(
            trace_id=str(uuid.uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            session_id=str(uuid.uuid4()),
            metadata=metadata or {}
        )
        
        logger.info(
            "Starting pipeline execution",
            extra={
                "trace_id": self.context.trace_id,
                "user_id": user_id,
                "query_length": len(query)
            }
        )
        
        # Initialize state with query
        self.state = {
            "original_query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_results": {}
        }
        
        # Execute pipeline stages
        try:
            for agent_name in self.pipeline:
                await self._execute_stage(agent_name)
                
                # Check for critical failures
                if self.state.get("pipeline_failed"):
                    break
            
            # Final result
            result = self._prepare_final_result()
            
            logger.info(
                "Pipeline execution completed",
                extra={
                    "trace_id": self.context.trace_id,
                    "duration": self._calculate_duration(),
                    "success": not self.state.get("pipeline_failed")
                }
            )
            
            # Record metrics if AWS enabled
            if AWS_ENABLED:
                metrics.add_metric(name="PipelineExecutions", unit=MetricUnit.Count, value=1)
                metrics.add_metric(
                    name="PipelineDuration",
                    unit=MetricUnit.Milliseconds,
                    value=self._calculate_duration() * 1000
                )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Pipeline execution failed: {e}",
                extra={"trace_id": self.context.trace_id}
            )
            
            return {
                "error": True,
                "error_message": str(e),
                "trace_id": self.context.trace_id,
                "partial_results": self.state.get("pipeline_results", {})
            }
    
    async def _execute_stage(self, agent_name: str):
        """Execute a single pipeline stage"""
        
        logger.info(f"Executing stage: {agent_name}")
        
        agent = self.agents[agent_name]
        
        # Prepare input for agent
        agent_input = self._prepare_agent_input(agent_name)
        
        try:
            # Execute agent with timeout
            result = await asyncio.wait_for(
                agent.execute(agent_input, self.context),
                timeout=agent.config.timeout + 10  # Add buffer
            )
            
            # Store result
            self.state["pipeline_results"][agent_name] = result
            
            # Update state with agent output
            self._update_state(agent_name, result)
            
            logger.info(
                f"Stage {agent_name} completed successfully",
                extra={"trace_id": self.context.trace_id}
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Stage {agent_name} timed out")
            self._handle_stage_failure(agent_name, "timeout")
            
        except Exception as e:
            logger.error(f"Stage {agent_name} failed: {e}")
            self._handle_stage_failure(agent_name, str(e))
    
    def _prepare_agent_input(self, agent_name: str) -> Dict[str, Any]:
        """Prepare input for specific agent"""
        
        base_input = {}
        
        if agent_name == "nl_input":
            base_input = {
                "query": self.state["original_query"]
            }
            
        elif agent_name == "ui_selection":
            base_input = {
                "requirements": self.state["pipeline_results"].get("nl_input", {})
            }
            
        elif agent_name == "parser":
            base_input = {
                "type": "requirements",
                "requirements": self.state["pipeline_results"].get("nl_input", {})
            }
            
        elif agent_name == "component_decision":
            base_input = {
                "requirements": self.state["pipeline_results"].get("nl_input", {}),
                "parsed_data": self.state["pipeline_results"].get("parser", {})
            }
            
        elif agent_name == "match_rate":
            base_input = {
                "requirements": self.state["pipeline_results"].get("nl_input", {})
            }
            
        elif agent_name == "search":
            base_input = {
                "query": self.state["original_query"],
                "requirements": self.state["pipeline_results"].get("nl_input", {})
            }
            
        elif agent_name == "generation":
            base_input = {
                "requirements": self.state["pipeline_results"].get("nl_input", {}),
                "ui_framework": self.state["pipeline_results"].get("ui_selection", {}),
                "components": self.state["pipeline_results"].get("component_decision", {}),
                "templates": self.state["pipeline_results"].get("match_rate", {})
            }
            
        elif agent_name == "assembly":
            base_input = self.state["pipeline_results"].get("generation", {})
            
        elif agent_name == "download":
            base_input = {
                "project": self.state["pipeline_results"].get("assembly", {}).get("project", {}),
                "metadata": {
                    "project_name": self.state["pipeline_results"].get("nl_input", {}).get("project_name", "project"),
                    "trace_id": self.context.trace_id
                }
            }
        
        return base_input
    
    def _update_state(self, agent_name: str, result: Dict[str, Any]):
        """Update orchestrator state with agent result"""
        
        # Store key results in state for easy access
        if agent_name == "nl_input":
            self.state["requirements"] = result
            
        elif agent_name == "ui_selection":
            self.state["selected_framework"] = result.get("selected_framework")
            
        elif agent_name == "component_decision":
            self.state["selected_components"] = result.get("selected_components")
            
        elif agent_name == "generation":
            self.state["generated_files"] = result.get("files")
            
        elif agent_name == "download":
            self.state["download_url"] = result.get("download_url")
    
    def _handle_stage_failure(self, agent_name: str, error: str):
        """Handle stage failure"""
        
        self.state["pipeline_results"][agent_name] = {
            "error": True,
            "error_message": error
        }
        
        # Determine if failure is critical
        critical_agents = ["nl_input", "generation", "assembly"]
        
        if agent_name in critical_agents:
            logger.error(f"Critical agent {agent_name} failed - stopping pipeline")
            self.state["pipeline_failed"] = True
        else:
            logger.warning(f"Non-critical agent {agent_name} failed - continuing")
    
    def _prepare_final_result(self) -> Dict[str, Any]:
        """Prepare final pipeline result"""
        
        if self.state.get("pipeline_failed"):
            return {
                "success": False,
                "error": "Pipeline failed",
                "trace_id": self.context.trace_id,
                "partial_results": self.state.get("pipeline_results", {})
            }
        
        return {
            "success": True,
            "trace_id": self.context.trace_id,
            "download_url": self.state.get("download_url"),
            "project_details": {
                "requirements": self.state.get("requirements", {}),
                "framework": self.state.get("selected_framework"),
                "components": self.state.get("selected_components"),
                "files_generated": len(self.state.get("generated_files", {}))
            },
            "execution_time": self._calculate_duration(),
            "pipeline_results": self.state.get("pipeline_results", {})
        }
    
    def _calculate_duration(self) -> float:
        """Calculate pipeline duration in seconds"""
        if "timestamp" in self.state:
            start = datetime.fromisoformat(self.state["timestamp"])
            duration = (datetime.utcnow() - start).total_seconds()
            return round(duration, 2)
        return 0.0
    
    async def cleanup(self):
        """Cleanup orchestrator resources"""
        logger.info("Cleaning up orchestrator")
        
        cleanup_tasks = []
        for agent_name, agent in self.agents.items():
            cleanup_tasks.append(agent.cleanup())
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        logger.info("Orchestrator cleanup complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents"""
        health_status = {
            "orchestrator": "healthy",
            "agents": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for agent_name, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health_status["agents"][agent_name] = agent_health.get("status", "unknown")
            except Exception as e:
                health_status["agents"][agent_name] = "unhealthy"
                logger.error(f"Health check failed for {agent_name}: {e}")
        
        # Overall health
        unhealthy_agents = [
            name for name, status in health_status["agents"].items()
            if status != "healthy"
        ]
        
        if unhealthy_agents:
            health_status["orchestrator"] = "degraded"
            health_status["unhealthy_agents"] = unhealthy_agents
        
        return health_status


# FastAPI integration
def create_orchestrator_api():
    """Create FastAPI app with orchestrator endpoints"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(title="T-Developer Unified API", version="2.0.0")
    
    # Initialize orchestrator
    orchestrator = UnifiedOrchestrator()
    
    class GenerateRequest(BaseModel):
        query: str
        user_id: Optional[str] = None
        tenant_id: Optional[str] = None
        metadata: Optional[Dict] = None
    
    @app.on_event("startup")
    async def startup():
        """Initialize orchestrator on startup"""
        await orchestrator.initialize()
    
    @app.on_event("shutdown")
    async def shutdown():
        """Cleanup on shutdown"""
        await orchestrator.cleanup()
    
    @app.post("/api/v1/generate")
    async def generate_project(request: GenerateRequest):
        """Generate project from natural language"""
        try:
            result = await orchestrator.execute_pipeline(
                query=request.query,
                user_id=request.user_id,
                tenant_id=request.tenant_id,
                metadata=request.metadata
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            return result
            
        except Exception as e:
            logger.error(f"API error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return await orchestrator.health_check()
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "T-Developer Unified API",
            "version": "2.0.0",
            "status": "running"
        }
    
    return app


# Lambda handler for AWS deployment
def lambda_handler(event, context):
    """AWS Lambda handler"""
    
    if not AWS_ENABLED:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "AWS not configured"})
        }
    
    # Parse event
    body = json.loads(event.get("body", "{}"))
    query = body.get("query")
    
    if not query:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Query required"})
        }
    
    # Create and run orchestrator
    orchestrator = UnifiedOrchestrator()
    
    # Run async code in Lambda
    import asyncio
    loop = asyncio.get_event_loop()
    
    try:
        # Initialize
        loop.run_until_complete(orchestrator.initialize())
        
        # Execute pipeline
        result = loop.run_until_complete(
            orchestrator.execute_pipeline(query)
        )
        
        # Cleanup
        loop.run_until_complete(orchestrator.cleanup())
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


if __name__ == "__main__":
    # Run FastAPI app
    import uvicorn
    
    app = create_orchestrator_api()
    uvicorn.run(app, host="0.0.0.0", port=8000)