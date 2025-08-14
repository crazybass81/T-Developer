"""
MetaCoordinator - Day 36
ServiceBuilder-Improver coordination system
Size: < 6.5KB
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Task status enum"""

    PENDING = "pending"
    BUILDING = "building"
    IMPROVING = "improving"
    TESTING = "testing"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MetaTask:
    """Meta agent task"""

    id: str
    type: str
    requirements: Dict
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


class MetaCoordinator:
    """Coordinate ServiceBuilder and ServiceImprover"""

    def __init__(self):
        """Initialize meta coordinator"""
        self.tasks = {}
        self.builder_queue = asyncio.Queue()
        self.improver_queue = asyncio.Queue()
        self.feedback_loop = []
        self.metrics = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_completion_time": 0,
        }

    async def coordinate_service_creation(self, requirements: Dict) -> Dict:
        """Coordinate new service creation"""
        # Create task
        task = MetaTask(
            id=self._generate_task_id(),
            type="service_creation",
            requirements=requirements,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
        )

        self.tasks[task.id] = task
        self.metrics["tasks_created"] += 1

        try:
            # Phase 1: Build service
            task.status = TaskStatus.BUILDING
            build_result = await self._build_service(requirements)

            # Phase 2: Initial improvement
            task.status = TaskStatus.IMPROVING
            improved = await self._improve_service(build_result)

            # Phase 3: Test service
            task.status = TaskStatus.TESTING
            test_result = await self._test_service(improved)

            # Phase 4: Deploy if tests pass
            if test_result["passed"]:
                task.status = TaskStatus.DEPLOYING
                deployment = await self._deploy_service(improved)

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = {"service": improved, "deployment": deployment, "tests": test_result}

                self.metrics["tasks_completed"] += 1
                self._update_avg_completion_time(task)

                return task.result
            else:
                # Retry improvement if tests fail
                return await self._retry_with_feedback(task, test_result)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.metrics["tasks_failed"] += 1
            raise

    async def _build_service(self, requirements: Dict) -> Dict:
        """Build service using ServiceBuilder"""
        # Queue task for ServiceBuilder
        await self.builder_queue.put(requirements)

        # Simulate ServiceBuilder processing
        await asyncio.sleep(0.1)

        return {
            "agents": self._generate_agents(requirements),
            "workflow": self._generate_workflow(requirements),
            "config": requirements,
        }

    async def _improve_service(self, service: Dict) -> Dict:
        """Improve service using ServiceImprover"""
        # Queue task for ServiceImprover
        await self.improver_queue.put(service)

        # Simulate ServiceImprover processing
        await asyncio.sleep(0.1)

        # Apply improvements
        improvements = {
            "performance": self._optimize_performance(service),
            "quality": self._improve_code_quality(service),
            "security": self._enhance_security(service),
        }

        # Merge improvements
        improved_service = service.copy()
        improved_service["improvements"] = improvements
        improved_service["version"] = "2.0"

        return improved_service

    async def _test_service(self, service: Dict) -> Dict:
        """Test the service"""
        tests = {
            "unit_tests": True,
            "integration_tests": True,
            "performance_tests": True,
            "security_tests": True,
        }

        # Simulate testing
        await asyncio.sleep(0.05)

        # Check constraints
        constraints_met = self._check_constraints(service)

        return {
            "passed": all(tests.values()) and constraints_met,
            "tests": tests,
            "constraints": constraints_met,
        }

    async def _deploy_service(self, service: Dict) -> Dict:
        """Deploy the service"""
        # Simulate deployment
        await asyncio.sleep(0.05)

        return {
            "status": "deployed",
            "endpoint": f"/api/services/{service.get('config', {}).get('name', 'service')}",
            "timestamp": datetime.now().isoformat(),
        }

    async def _retry_with_feedback(self, task: MetaTask, test_result: Dict) -> Dict:
        """Retry improvement with feedback"""
        # Collect feedback
        feedback = {
            "failed_tests": [k for k, v in test_result["tests"].items() if not v],
            "suggestions": self._generate_suggestions(test_result),
        }

        self.feedback_loop.append(feedback)

        # Re-improve with feedback
        task.status = TaskStatus.IMPROVING
        improved = await self._improve_with_feedback(task.result.get("service", {}), feedback)

        # Re-test
        task.status = TaskStatus.TESTING
        new_test_result = await self._test_service(improved)

        if new_test_result["passed"]:
            # Deploy successful retry
            task.status = TaskStatus.DEPLOYING
            deployment = await self._deploy_service(improved)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = {
                "service": improved,
                "deployment": deployment,
                "tests": new_test_result,
                "retries": 1,
            }

            return task.result
        else:
            # Mark as failed after retry
            task.status = TaskStatus.FAILED
            task.error = "Tests failed after retry"
            raise Exception(task.error)

    async def _improve_with_feedback(self, service: Dict, feedback: Dict) -> Dict:
        """Improve service based on feedback"""
        improved = service.copy()

        # Apply targeted improvements based on feedback
        for suggestion in feedback["suggestions"]:
            if suggestion["type"] == "performance":
                improved["optimizations"] = suggestion["actions"]
            elif suggestion["type"] == "quality":
                improved["refactoring"] = suggestion["actions"]

        return improved

    def _generate_agents(self, requirements: Dict) -> List[Dict]:
        """Generate agents for service"""
        agents = []

        for feature in requirements.get("features", []):
            agents.append({"name": f"{feature}_agent", "type": feature, "size_kb": 5.0})

        return agents

    def _generate_workflow(self, requirements: Dict) -> Dict:
        """Generate workflow for service"""
        return {
            "steps": [
                {"name": "input", "type": "receive"},
                {"name": "process", "type": "transform"},
                {"name": "output", "type": "respond"},
            ],
            "parallel": requirements.get("parallel", False),
        }

    def _optimize_performance(self, service: Dict) -> Dict:
        """Optimize service performance"""
        return {"caching": True, "async_processing": True, "batch_size": 100}

    def _improve_code_quality(self, service: Dict) -> Dict:
        """Improve code quality"""
        return {"refactored": True, "test_coverage": 85, "complexity_reduced": True}

    def _enhance_security(self, service: Dict) -> Dict:
        """Enhance security"""
        return {"authentication": True, "encryption": True, "audit_logging": True}

    def _check_constraints(self, service: Dict) -> bool:
        """Check service constraints"""
        # Check size constraint
        for agent in service.get("agents", []):
            if agent.get("size_kb", 0) > 6.5:
                return False

        return True

    def _generate_suggestions(self, test_result: Dict) -> List[Dict]:
        """Generate improvement suggestions"""
        suggestions = []

        if not test_result["tests"].get("performance_tests"):
            suggestions.append(
                {"type": "performance", "actions": ["optimize_loops", "add_caching"]}
            )

        if not test_result["tests"].get("security_tests"):
            suggestions.append(
                {"type": "security", "actions": ["add_validation", "implement_auth"]}
            )

        return suggestions

    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        import uuid

        return str(uuid.uuid4())[:8]

    def _update_avg_completion_time(self, task: MetaTask) -> None:
        """Update average completion time metric"""
        if task.completed_at and task.created_at:
            duration = (task.completed_at - task.created_at).total_seconds()

            # Calculate running average
            n = self.metrics["tasks_completed"]
            prev_avg = self.metrics["avg_completion_time"]
            self.metrics["avg_completion_time"] = (prev_avg * (n - 1) + duration) / n

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        task = self.tasks.get(task_id)
        if task:
            return {
                "id": task.id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error": task.error,
            }
        return None

    def get_metrics(self) -> Dict:
        """Get coordinator metrics"""
        return self.metrics.copy()
