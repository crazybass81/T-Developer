"""Workflow Monitor for Real-time Tracking < 6.5KB"""
import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WorkflowMetrics:
    workflow_id: str
    start_time: float
    end_time: Optional[float] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    avg_step_duration: float = 0
    status: str = "pending"
    
@dataclass
class StepMetrics:
    step_id: str
    workflow_id: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "pending"
    retry_count: int = 0
    error: Optional[str] = None

class WorkflowMonitor:
    def __init__(self):
        self.workflows: Dict[str, WorkflowMetrics] = {}
        self.steps: Dict[str, StepMetrics] = {}
        self.alerts: List[Dict] = []
        self.thresholds = {
            "max_step_duration": 60,  # seconds
            "max_retry_count": 3,
            "max_workflow_duration": 300  # seconds
        }
        self.monitoring = True
        self.monitor_task = None
        
    def start_workflow(self, workflow_id: str, total_steps: int):
        """Start monitoring workflow"""
        self.workflows[workflow_id] = WorkflowMetrics(
            workflow_id=workflow_id,
            start_time=time.time(),
            total_steps=total_steps,
            status="running"
        )
        
        # Start monitoring if not running
        if not self.monitor_task:
            try:
                loop = asyncio.get_running_loop()
                self.monitor_task = loop.create_task(self._monitor_loop())
            except RuntimeError:
                # No running loop, skip background monitoring
                pass
            
    def end_workflow(self, workflow_id: str, status: str):
        """End workflow monitoring"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.end_time = time.time()
            workflow.status = status
            
            # Calculate average step duration
            if workflow.completed_steps > 0:
                total_duration = sum(
                    s.end_time - s.start_time
                    for s in self.steps.values()
                    if s.workflow_id == workflow_id and s.end_time
                )
                workflow.avg_step_duration = total_duration / workflow.completed_steps
                
    def start_step(self, workflow_id: str, step_id: str):
        """Start monitoring step"""
        self.steps[step_id] = StepMetrics(
            step_id=step_id,
            workflow_id=workflow_id,
            start_time=time.time(),
            status="running"
        )
        
    def end_step(self, step_id: str, status: str, error: Optional[str] = None):
        """End step monitoring"""
        if step_id in self.steps:
            step = self.steps[step_id]
            step.end_time = time.time()
            step.status = status
            step.error = error
            
            # Update workflow metrics
            if step.workflow_id in self.workflows:
                workflow = self.workflows[step.workflow_id]
                if status == "completed":
                    workflow.completed_steps += 1
                elif status == "failed":
                    workflow.failed_steps += 1
                    
                # Check for alerts
                self._check_step_alerts(step)
                
    def retry_step(self, step_id: str):
        """Record step retry"""
        if step_id in self.steps:
            self.steps[step_id].retry_count += 1
            
            # Check retry threshold
            if self.steps[step_id].retry_count >= self.thresholds["max_retry_count"]:
                self._create_alert(
                    "high_retry_count",
                    f"Step {step_id} exceeded retry threshold",
                    {"step_id": step_id, "retry_count": self.steps[step_id].retry_count}
                )
                
    def _check_step_alerts(self, step: StepMetrics):
        """Check for step-related alerts"""
        if step.end_time and step.start_time:
            duration = step.end_time - step.start_time
            if duration > self.thresholds["max_step_duration"]:
                self._create_alert(
                    "slow_step",
                    f"Step {step.step_id} took {duration:.2f} seconds",
                    {"step_id": step.step_id, "duration": duration}
                )
                
    def _create_alert(self, alert_type: str, message: str, details: Dict):
        """Create monitoring alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
            
    async def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                current_time = time.time()
                
                # Check for slow workflows
                for workflow_id, workflow in self.workflows.items():
                    if workflow.status == "running":
                        duration = current_time - workflow.start_time
                        if duration > self.thresholds["max_workflow_duration"]:
                            self._create_alert(
                                "slow_workflow",
                                f"Workflow {workflow_id} running for {duration:.2f} seconds",
                                {"workflow_id": workflow_id, "duration": duration}
                            )
                            
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)
                
    def get_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """Get workflow metrics"""
        return self.workflows.get(workflow_id)
        
    def get_step_metrics(self, step_id: str) -> Optional[StepMetrics]:
        """Get step metrics"""
        return self.steps.get(step_id)
        
    def get_workflow_summary(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution summary"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}
            
        duration = (workflow.end_time or time.time()) - workflow.start_time
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "duration": duration,
            "total_steps": workflow.total_steps,
            "completed_steps": workflow.completed_steps,
            "failed_steps": workflow.failed_steps,
            "progress_percentage": (workflow.completed_steps / workflow.total_steps * 100) if workflow.total_steps > 0 else 0,
            "avg_step_duration": workflow.avg_step_duration,
            "steps": [
                {
                    "step_id": s.step_id,
                    "status": s.status,
                    "duration": (s.end_time - s.start_time) if s.end_time else None,
                    "retry_count": s.retry_count,
                    "error": s.error
                }
                for s in self.steps.values()
                if s.workflow_id == workflow_id
            ]
        }
        
    def get_active_workflows(self) -> List[str]:
        """Get list of active workflows"""
        return [
            wf_id for wf_id, wf in self.workflows.items()
            if wf.status == "running"
        ]
        
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return self.alerts[-limit:]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        total_workflows = len(self.workflows)
        active_workflows = len(self.get_active_workflows())
        
        completed_workflows = [
            wf for wf in self.workflows.values()
            if wf.status == "completed"
        ]
        
        failed_workflows = [
            wf for wf in self.workflows.values()
            if wf.status == "failed"
        ]
        
        avg_duration = 0
        if completed_workflows:
            avg_duration = sum(
                (wf.end_time - wf.start_time) for wf in completed_workflows
            ) / len(completed_workflows)
            
        return {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "completed_workflows": len(completed_workflows),
            "failed_workflows": len(failed_workflows),
            "success_rate": (len(completed_workflows) / total_workflows * 100) if total_workflows > 0 else 0,
            "avg_workflow_duration": avg_duration,
            "total_alerts": len(self.alerts),
            "recent_alerts": self.get_recent_alerts(5)
        }
        
    def cleanup_old_data(self, hours: int = 24):
        """Cleanup old monitoring data"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Remove old workflows
        old_workflows = [
            wf_id for wf_id, wf in self.workflows.items()
            if wf.end_time and wf.end_time < cutoff_time
        ]
        
        for wf_id in old_workflows:
            del self.workflows[wf_id]
            
        # Remove old steps
        old_steps = [
            s_id for s_id, s in self.steps.items()
            if s.workflow_id in old_workflows
        ]
        
        for s_id in old_steps:
            del self.steps[s_id]
            
        # Remove old alerts
        self.alerts = [
            a for a in self.alerts
            if a["timestamp"] >= cutoff_time
        ]

# Example usage
if __name__ == "__main__":
    async def test_monitor():
        monitor = WorkflowMonitor()
        
        # Start workflow
        monitor.start_workflow("wf1", total_steps=3)
        
        # Execute steps
        monitor.start_step("wf1", "step1")
        await asyncio.sleep(0.1)
        monitor.end_step("step1", "completed")
        
        monitor.start_step("wf1", "step2")
        monitor.retry_step("step2")
        await asyncio.sleep(0.1)
        monitor.end_step("step2", "completed")
        
        monitor.start_step("wf1", "step3")
        await asyncio.sleep(0.1)
        monitor.end_step("step3", "failed", "Test error")
        
        # End workflow
        monitor.end_workflow("wf1", "failed")
        
        # Get summary
        summary = monitor.get_workflow_summary("wf1")
        print(f"Summary: {summary}")
        
        # Get statistics
        stats = monitor.get_statistics()
        print(f"Stats: {stats}")
        
    asyncio.run(test_monitor())