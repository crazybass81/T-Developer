"""Tests for Planner Agent - TDD approach."""

from datetime import datetime, timedelta

import pytest

from packages.agents.base import AgentInput, AgentOutput, AgentStatus
from packages.agents.planner import (
    DependencyAnalyzer,
    Milestone,
    Plan,
    PlannerAgent,
    PlannerConfig,
    Task,
    TaskDecomposer,
    TimeEstimator,
)


class TestTask:
    """Test Task dataclass."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            id="task-001",
            name="Add type hints",
            description="Add type hints to all functions",
            estimated_hours=2.0,
            dependencies=[],
            priority="high",
            category="refactoring",
        )

        assert task.id == "task-001"
        assert task.estimated_hours == 2.0
        assert task.priority == "high"
        assert len(task.dependencies) == 0

    def test_task_with_dependencies(self):
        """Test task with dependencies."""
        task = Task(
            id="task-002",
            name="Run tests",
            description="Execute test suite",
            estimated_hours=0.5,
            dependencies=["task-001"],
            priority="medium",
            category="testing",
        )

        assert "task-001" in task.dependencies
        assert task.can_start_after(["task-001"]) is True
        assert task.can_start_after([]) is False


class TestMilestone:
    """Test Milestone dataclass."""

    def test_milestone_creation(self):
        """Test creating a milestone."""
        milestone = Milestone(
            id="m1",
            name="Phase 1 Complete",
            tasks=["task-001", "task-002"],
            deadline=datetime.now() + timedelta(days=7),
            success_criteria=["All tests pass", "Coverage > 80%"],
        )

        assert milestone.id == "m1"
        assert len(milestone.tasks) == 2
        assert len(milestone.success_criteria) == 2

    def test_milestone_progress(self):
        """Test milestone progress tracking."""
        milestone = Milestone(
            id="m2",
            name="Testing Complete",
            tasks=["t1", "t2", "t3"],
            completed_tasks=["t1"],
            deadline=datetime.now() + timedelta(days=1),
        )

        assert milestone.progress == pytest.approx(33.33, rel=1e-2)
        assert milestone.is_complete is False

        milestone.completed_tasks = ["t1", "t2", "t3"]
        assert milestone.is_complete is True


class TestPlan:
    """Test Plan dataclass."""

    def test_plan_creation(self):
        """Test creating a plan."""
        tasks = [
            Task("t1", "Task 1", "Description", 2.0, [], "high", "dev"),
            Task("t2", "Task 2", "Description", 3.0, ["t1"], "medium", "dev"),
        ]

        plan = Plan(
            id="plan-001",
            goal="Improve code quality",
            tasks=tasks,
            milestones=[],
            total_estimated_hours=5.0,
            created_at=datetime.now(),
        )

        assert plan.id == "plan-001"
        assert len(plan.tasks) == 2
        assert plan.total_estimated_hours == 5.0

    def test_plan_validation(self):
        """Test plan validation."""
        # Valid plan with proper dependencies
        tasks = [
            Task("t1", "First", "Do first", 1.0, [], "high", "setup"),
            Task("t2", "Second", "Do second", 1.0, ["t1"], "medium", "dev"),
        ]
        plan = Plan("p1", "Test", tasks, [], 2.0, datetime.now())
        assert plan.validate() is True

        # Invalid plan with circular dependency
        tasks = [
            Task("t1", "First", "Do first", 1.0, ["t2"], "high", "setup"),
            Task("t2", "Second", "Do second", 1.0, ["t1"], "medium", "dev"),
        ]
        plan = Plan("p2", "Test", tasks, [], 2.0, datetime.now())
        assert plan.validate() is False

    def test_plan_critical_path(self):
        """Test finding critical path."""
        tasks = [
            Task("t1", "Setup", "Initial setup", 1.0, [], "high", "setup"),
            Task("t2", "Dev A", "Develop feature A", 3.0, ["t1"], "high", "dev"),
            Task("t3", "Dev B", "Develop feature B", 2.0, ["t1"], "medium", "dev"),
            Task("t4", "Test", "Test all", 1.0, ["t2", "t3"], "high", "test"),
        ]
        plan = Plan("p3", "Feature", tasks, [], 7.0, datetime.now())

        critical_path = plan.get_critical_path()
        assert critical_path == ["t1", "t2", "t4"]  # Longest path


class TestTaskDecomposer:
    """Test task decomposer."""

    @pytest.fixture
    def decomposer(self):
        """Create task decomposer."""
        return TaskDecomposer()

    def test_decompose_simple_goal(self, decomposer):
        """Test decomposing a simple goal."""
        goal = "Add logging to the application"
        research_data = {
            "improvements": [
                {"type": "logging", "location": "auth.py", "priority": "high"},
                {"type": "logging", "location": "api.py", "priority": "medium"},
            ]
        }

        tasks = decomposer.decompose(goal, research_data)

        assert len(tasks) > 0
        assert all(isinstance(t, Task) for t in tasks)
        assert any("logging" in t.name.lower() for t in tasks)

    def test_decompose_complex_goal(self, decomposer):
        """Test decomposing a complex goal."""
        goal = "Migrate from Express to Fastify"
        research_data = {
            "improvements": [],
            "external_references": {
                "recommendations": {
                    "migration_steps": [
                        "Setup Fastify alongside Express",
                        "Migrate middleware",
                        "Migrate routes",
                        "Switch traffic",
                        "Remove Express",
                    ]
                }
            },
        }

        tasks = decomposer.decompose(goal, research_data, max_hours_per_task=4)

        assert len(tasks) >= 5
        assert all(t.estimated_hours <= 4 for t in tasks)
        # Check dependencies are set
        assert any(len(t.dependencies) > 0 for t in tasks)

    def test_respect_max_hours(self, decomposer):
        """Test that tasks respect maximum hours constraint."""
        goal = "Complete refactoring"
        research_data = {"improvements": [{"type": "refactor", "effort": "8h"}]}

        tasks = decomposer.decompose(goal, research_data, max_hours_per_task=4)

        # Should split into multiple tasks
        assert all(t.estimated_hours <= 4 for t in tasks)


class TestTimeEstimator:
    """Test time estimator."""

    @pytest.fixture
    def estimator(self):
        """Create time estimator."""
        return TimeEstimator()

    def test_estimate_refactoring(self, estimator):
        """Test estimating refactoring time."""
        task_data = {"type": "refactoring", "files_affected": 5, "complexity": "medium"}

        hours = estimator.estimate(task_data)

        assert hours > 0
        assert hours <= 8  # Reasonable upper bound

    def test_estimate_with_historical_data(self, estimator):
        """Test estimation with historical data."""
        task_data = {"type": "testing", "scope": "unit_tests", "files": 10}

        historical_data = [
            {"type": "testing", "files": 5, "actual_hours": 2},
            {"type": "testing", "files": 15, "actual_hours": 5},
        ]

        hours = estimator.estimate(task_data, historical_data)

        # Should interpolate between 2-5 hours for 10 files
        assert 2 < hours < 5

    def test_buffer_for_uncertainty(self, estimator):
        """Test adding buffer for uncertainty."""
        task_data = {"type": "unknown", "complexity": "high"}

        hours = estimator.estimate(task_data, buffer_percentage=20)
        base_hours = estimator.estimate(task_data, buffer_percentage=0)

        assert hours > base_hours
        assert hours == pytest.approx(base_hours * 1.2, rel=1e-2)


class TestDependencyAnalyzer:
    """Test dependency analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create dependency analyzer."""
        return DependencyAnalyzer()

    def test_analyze_file_dependencies(self, analyzer):
        """Test analyzing file dependencies."""
        tasks = [
            Task("t1", "Modify base.py", "Change base class", 2, [], "high", "dev"),
            Task("t2", "Update derived.py", "Update derived class", 1, [], "medium", "dev"),
            Task("t3", "Fix tests", "Fix broken tests", 1, [], "high", "test"),
        ]

        file_deps = {"derived.py": ["base.py"], "tests/test_derived.py": ["derived.py", "base.py"]}

        analyzer.analyze(tasks, file_deps)

        # t2 should depend on t1 (derived depends on base)
        assert "t1" in tasks[1].dependencies
        # t3 should depend on both
        assert "t1" in tasks[2].dependencies or "t2" in tasks[2].dependencies

    def test_detect_circular_dependencies(self, analyzer):
        """Test detecting circular dependencies."""
        deps = {"A": ["B"], "B": ["C"], "C": ["A"]}  # Circular!

        has_circular = analyzer.has_circular_dependency(deps)
        assert has_circular is True

        deps_valid = {"A": ["B"], "B": ["C"], "C": []}

        has_circular = analyzer.has_circular_dependency(deps_valid)
        assert has_circular is False

    def test_topological_sort(self, analyzer):
        """Test topological sorting of tasks."""
        tasks = [
            Task("t3", "Third", "Do third", 1, ["t1", "t2"], "low", "dev"),
            Task("t1", "First", "Do first", 1, [], "high", "dev"),
            Task("t2", "Second", "Do second", 1, ["t1"], "medium", "dev"),
        ]

        sorted_tasks = analyzer.topological_sort(tasks)

        # t1 should come first
        assert sorted_tasks[0].id == "t1"
        # t3 should come last
        assert sorted_tasks[-1].id == "t3"
        # t2 should be in middle
        assert sorted_tasks[1].id == "t2"


class TestPlannerConfig:
    """Test planner configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = PlannerConfig()

        assert config.max_hours_per_task == 4.0
        assert config.min_hours_per_task == 0.5
        assert config.buffer_percentage == 20
        assert config.parallel_tasks_limit == 3

    def test_custom_config(self):
        """Test custom configuration."""
        config = PlannerConfig(
            max_hours_per_task=2.0, buffer_percentage=30, enable_ai_planning=True
        )

        assert config.max_hours_per_task == 2.0
        assert config.buffer_percentage == 30
        assert config.enable_ai_planning is True


class TestPlannerAgent:
    """Test planner agent."""

    @pytest.fixture
    def agent(self):
        """Create planner agent."""
        config = PlannerConfig(enable_ai_planning=False)
        return PlannerAgent("planner", config)

    @pytest.mark.asyncio
    async def test_create_plan_from_research(self, agent):
        """Test creating plan from research data."""
        input_data = AgentInput(
            intent="plan",
            task_id="test-001",
            payload={
                "goal": "Improve test coverage",
                "research_data": {
                    "improvements": [
                        {"type": "test", "location": "auth.py", "missing": "unit tests"},
                        {"type": "test", "location": "api.py", "missing": "integration tests"},
                    ],
                    "summary": {"files_analyzed": 10, "test_coverage": 60},
                },
                "constraints": {"deadline": "2024-02-01", "max_hours": 20},
            },
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) > 0

        plan_artifact = next((a for a in output.artifacts if a.kind == "plan"), None)
        assert plan_artifact is not None

        plan = plan_artifact.content
        assert plan["goal"] == "Improve test coverage"
        assert len(plan["tasks"]) > 0
        assert plan["total_estimated_hours"] <= 20

    @pytest.mark.asyncio
    async def test_plan_with_milestones(self, agent):
        """Test creating plan with milestones."""
        input_data = AgentInput(
            intent="plan",
            task_id="test-002",
            payload={
                "goal": "Launch new feature",
                "research_data": {
                    "improvements": [],
                    "recommendations": {"phases": ["Development", "Testing", "Deployment"]},
                },
                "constraints": {
                    "milestones": [
                        {"name": "Dev Complete", "deadline": "2024-01-20"},
                        {"name": "Testing Complete", "deadline": "2024-01-25"},
                        {"name": "Deployed", "deadline": "2024-02-01"},
                    ]
                },
            },
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        plan = output.artifacts[0].content
        assert len(plan["milestones"]) == 3
        assert plan["milestones"][0]["name"] == "Dev Complete"

    @pytest.mark.asyncio
    async def test_validate_output(self, agent):
        """Test output validation."""
        valid_output = AgentOutput(
            task_id="test-003",
            status=AgentStatus.OK,
            artifacts=[
                {
                    "kind": "plan",
                    "ref": "plan-001.json",
                    "content": {"goal": "Test", "tasks": [], "total_estimated_hours": 0},
                }
            ],
            metrics={"tasks_created": 5},
        )

        assert await agent.validate(valid_output) is True

        invalid_output = AgentOutput(
            task_id="test-004", status=AgentStatus.OK, artifacts=[], metrics={}  # No plan artifact
        )

        assert await agent.validate(invalid_output) is False

    def test_get_capabilities(self, agent):
        """Test capabilities declaration."""
        capabilities = agent.get_capabilities()

        assert capabilities["name"] == "planner"
        assert "plan" in capabilities["supported_intents"]
        assert "task_decomposition" in capabilities["features"]
        assert capabilities["max_hours_per_task"] == 4.0
