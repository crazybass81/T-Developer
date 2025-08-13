"""Real-time Workflow Executor < 6.5KB"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    id: str
    name: str
    agent_id: str
    input_mapping: Dict[str, str]
    output_mapping: Dict[str, str]
    retry_count: int = 3
    timeout: int = 30

@dataclass
class WorkflowResult:
    step_id: str
    status: WorkflowStatus
    data: Optional[Dict] = None
    error: Optional[str] = None
    duration: float = 0

class WorkflowExecutor:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.steps: List[WorkflowStep] = []
        self.context: Dict[str, Any] = {}
        self.results: Dict[str, WorkflowResult] = {}
        self.status = WorkflowStatus.PENDING
        self.cancel_event = asyncio.Event()
        
    def add_step(self, step: WorkflowStep):
        """Add step to workflow"""
        self.steps.append(step)
        
    def set_context(self, context: Dict[str, Any]):
        """Set initial workflow context"""
        self.context = context
        
    async def execute(self) -> Dict[str, Any]:
        """Execute workflow"""
        self.status = WorkflowStatus.RUNNING
        start_time = time.time()
        
        try:
            for step in self.steps:
                if self.cancel_event.is_set():
                    self.status = WorkflowStatus.CANCELLED
                    break
                    
                result = await self._execute_step(step)
                self.results[step.id] = result
                
                if result.status == WorkflowStatus.FAILED:
                    self.status = WorkflowStatus.FAILED
                    break
                    
                # Update context with step output
                if result.data:
                    for key, value in step.output_mapping.items():
                        self.context[value] = result.data.get(key)
                        
            if self.status == WorkflowStatus.RUNNING:
                self.status = WorkflowStatus.COMPLETED
                
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            return {
                "workflow_id": self.workflow_id,
                "status": self.status.value,
                "error": str(e),
                "duration": time.time() - start_time
            }
            
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "results": {k: asdict(v) for k, v in self.results.items()},
            "context": self.context,
            "duration": time.time() - start_time
        }
        
    async def execute_streaming(self) -> AsyncGenerator[Dict, None]:
        """Execute workflow with streaming results"""
        self.status = WorkflowStatus.RUNNING
        
        yield {
            "type": "start",
            "workflow_id": self.workflow_id,
            "timestamp": time.time()
        }
        
        for step in self.steps:
            if self.cancel_event.is_set():
                self.status = WorkflowStatus.CANCELLED
                yield {
                    "type": "cancelled",
                    "step_id": step.id,
                    "timestamp": time.time()
                }
                break
                
            # Yield step start
            yield {
                "type": "step_start",
                "step_id": step.id,
                "step_name": step.name,
                "timestamp": time.time()
            }
            
            result = await self._execute_step(step)
            self.results[step.id] = result
            
            # Yield step result
            yield {
                "type": "step_complete",
                "step_id": step.id,
                "status": result.status.value,
                "data": result.data,
                "error": result.error,
                "duration": result.duration,
                "timestamp": time.time()
            }
            
            if result.status == WorkflowStatus.FAILED:
                self.status = WorkflowStatus.FAILED
                yield {
                    "type": "failed",
                    "step_id": step.id,
                    "error": result.error,
                    "timestamp": time.time()
                }
                break
                
            # Update context
            if result.data:
                for key, value in step.output_mapping.items():
                    self.context[value] = result.data.get(key)
                    
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.COMPLETED
            
        yield {
            "type": "complete",
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "context": self.context,
            "timestamp": time.time()
        }
        
    async def _execute_step(self, step: WorkflowStep) -> WorkflowResult:
        """Execute single workflow step"""
        start_time = time.time()
        
        for attempt in range(step.retry_count):
            try:
                # Prepare input from context
                input_data = {}
                for key, value in step.input_mapping.items():
                    input_data[key] = self.context.get(value)
                    
                # Simulate agent execution (replace with actual call)
                result = await self._call_agent(step.agent_id, input_data, step.timeout)
                
                return WorkflowResult(
                    step_id=step.id,
                    status=WorkflowStatus.COMPLETED,
                    data=result,
                    duration=time.time() - start_time
                )
                
            except asyncio.TimeoutError:
                if attempt == step.retry_count - 1:
                    return WorkflowResult(
                        step_id=step.id,
                        status=WorkflowStatus.FAILED,
                        error="Timeout",
                        duration=time.time() - start_time
                    )
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                if attempt == step.retry_count - 1:
                    return WorkflowResult(
                        step_id=step.id,
                        status=WorkflowStatus.FAILED,
                        error=str(e),
                        duration=time.time() - start_time
                    )
                await asyncio.sleep(2 ** attempt)
                
    async def _call_agent(self, agent_id: str, input_data: Dict, timeout: int) -> Dict:
        """Call agent (placeholder)"""
        # Simulate agent call
        await asyncio.sleep(0.1)
        return {"result": f"Processed by {agent_id}", "data": input_data}
        
    def cancel(self):
        """Cancel workflow execution"""
        self.cancel_event.set()
        
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "completed_steps": len([r for r in self.results.values() if r.status == WorkflowStatus.COMPLETED]),
            "total_steps": len(self.steps),
            "results": {k: {"status": v.status.value, "error": v.error} for k, v in self.results.items()}
        }

def asdict(obj):
    """Convert dataclass to dict"""
    return {
        "step_id": obj.step_id,
        "status": obj.status.value,
        "data": obj.data,
        "error": obj.error,
        "duration": obj.duration
    }

# Example usage
if __name__ == "__main__":
    async def test_workflow():
        executor = WorkflowExecutor("test_workflow")
        
        # Add workflow steps
        executor.add_step(WorkflowStep(
            id="step1",
            name="Parse Input",
            agent_id="nl_input",
            input_mapping={"text": "user_input"},
            output_mapping={"parsed": "parsed_input"}
        ))
        
        executor.add_step(WorkflowStep(
            id="step2",
            name="Generate Response",
            agent_id="generator",
            input_mapping={"input": "parsed_input"},
            output_mapping={"response": "final_output"}
        ))
        
        # Set initial context
        executor.set_context({"user_input": "Test input"})
        
        # Execute with streaming
        async for event in executor.execute_streaming():
            print(f"Event: {json.dumps(event, indent=2)}")
            
    asyncio.run(test_workflow())