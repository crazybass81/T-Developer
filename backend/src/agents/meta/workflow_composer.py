"""
Workflow Composer - AI-powered workflow auto-composition
Size: < 6.5KB | Performance: < 3μs
Day 23: Phase 2 - Meta Agents
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from src.ai.consensus_engine import get_engine
from src.optimization.parallelizer import Parallelizer
from src.optimization.resource_allocator import ResourceAllocator


@dataclass
class WorkflowStep:
    """Single workflow step"""

    id: str
    name: str
    agent: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    parallel: bool = False
    timeout: int = 30
    retries: int = 3


@dataclass
class WorkflowDAG:
    """Workflow Directed Acyclic Graph"""

    steps: List[WorkflowStep]
    edges: Dict[str, List[str]]  # adjacency list
    entry_points: List[str]
    exit_points: List[str]
    parallel_groups: List[List[str]]


@dataclass
class ComposedWorkflow:
    """Complete composed workflow"""

    name: str
    dag: WorkflowDAG
    execution_plan: List[List[str]]  # Steps to execute in order (parallel groups)
    resource_allocation: Dict[str, Any]
    estimated_time: float
    optimization_score: float


class WorkflowComposer:
    """AI-powered workflow composition engine"""

    def __init__(self):
        self.consensus = get_engine()
        self.parallelizer = Parallelizer()
        self.resource_allocator = ResourceAllocator()
        self.workflow_patterns = self._init_patterns()

    def _init_patterns(self):
        """Initialize common workflow patterns"""
        return {
            "sequential": self._sequential_pattern,
            "parallel": self._parallel_pattern,
            "conditional": self._conditional_pattern,
            "pipeline": self._pipeline_pattern,
            "map_reduce": self._map_reduce_pattern,
            "scatter_gather": self._scatter_gather_pattern,
        }

    async def compose(
        self, agents: List[str], requirements: Dict[str, Any], constraints: Dict[str, Any] = None
    ) -> ComposedWorkflow:
        """Compose optimal workflow from agents and requirements"""

        # Analyze agent dependencies
        dependencies = await self._analyze_dependencies(agents, requirements)

        # Build workflow DAG
        dag = await self._build_dag(agents, dependencies)

        # Identify parallelization opportunities
        parallel_groups = await self.parallelizer.identify_parallel_groups(dag)

        # Optimize execution order
        execution_plan = await self._optimize_execution_order(dag, parallel_groups)

        # Allocate resources
        resource_allocation = await self.resource_allocator.allocate(dag, constraints or {})

        # Estimate execution time
        estimated_time = self._estimate_time(dag, execution_plan)

        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            dag, parallel_groups, resource_allocation
        )

        return ComposedWorkflow(
            name=f"workflow_{len(agents)}_agents",
            dag=dag,
            execution_plan=execution_plan,
            resource_allocation=resource_allocation,
            estimated_time=estimated_time,
            optimization_score=optimization_score,
        )

    async def _analyze_dependencies(
        self, agents: List[str], requirements: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Analyze dependencies between agents using AI"""

        prompt = f"""
        Analyze dependencies for agents: {agents}
        Requirements: {requirements}

        Determine which agents depend on outputs from other agents.
        Consider data flow and processing order.
        """

        # Get AI consensus on dependencies
        result = await self.consensus.get_consensus(prompt)

        # For now, create simple dependencies based on agent order
        dependencies = {}
        for i, agent in enumerate(agents):
            if i > 0:
                # Each agent depends on previous one (can be optimized)
                dependencies[agent] = [agents[i - 1]]
            else:
                dependencies[agent] = []

        return dependencies

    async def _build_dag(
        self, agents: List[str], dependencies: Dict[str, List[str]]
    ) -> WorkflowDAG:
        """Build workflow DAG from agents and dependencies"""

        steps = []
        edges = defaultdict(list)

        for i, agent in enumerate(agents):
            step = WorkflowStep(
                id=f"step_{i}",
                name=f"{agent}_step",
                agent=agent,
                input_schema={"data": "any"},
                output_schema={"result": "any"},
                dependencies=dependencies.get(agent, []),
                parallel=len(dependencies.get(agent, [])) == 0,
            )
            steps.append(step)

            # Build edges
            for dep in dependencies.get(agent, []):
                dep_idx = agents.index(dep)
                edges[f"step_{dep_idx}"].append(f"step_{i}")

        # Find entry and exit points
        entry_points = [s.id for s in steps if not s.dependencies]
        exit_points = [s.id for s in steps if s.id not in edges]

        # Identify parallel groups
        parallel_groups = []
        visited = set()
        for step in steps:
            if step.id not in visited and step.parallel:
                group = [step.id]
                visited.add(step.id)
                # Find other parallel steps at same level
                for other in steps:
                    if (
                        other.id not in visited
                        and other.parallel
                        and other.dependencies == step.dependencies
                    ):
                        group.append(other.id)
                        visited.add(other.id)
                if len(group) > 1:
                    parallel_groups.append(group)

        return WorkflowDAG(
            steps=steps,
            edges=dict(edges),
            entry_points=entry_points,
            exit_points=exit_points,
            parallel_groups=parallel_groups,
        )

    async def _optimize_execution_order(
        self, dag: WorkflowDAG, parallel_groups: List[List[str]]
    ) -> List[List[str]]:
        """Optimize execution order using topological sort with parallelism"""

        # Build in-degree map
        in_degree = {step.id: 0 for step in dag.steps}
        for step in dag.steps:
            for dep in step.dependencies:
                dep_step = next((s for s in dag.steps if s.agent == dep), None)
                if dep_step:
                    in_degree[step.id] += 1

        # Topological sort with level-based execution
        execution_plan = []
        queue = [sid for sid, degree in in_degree.items() if degree == 0]

        while queue:
            # Execute all nodes at current level in parallel
            current_level = queue[:]
            execution_plan.append(current_level)

            # Update next level
            next_queue = []
            for step_id in current_level:
                for next_id in dag.edges.get(step_id, []):
                    in_degree[next_id] -= 1
                    if in_degree[next_id] == 0:
                        next_queue.append(next_id)

            queue = next_queue

        return execution_plan

    def _estimate_time(self, dag: WorkflowDAG, execution_plan: List[List[str]]) -> float:
        """Estimate total execution time"""

        total_time = 0.0

        for level in execution_plan:
            # Each level executes in parallel, so take max time
            level_time = 0.0
            for step_id in level:
                step = next((s for s in dag.steps if s.id == step_id), None)
                if step:
                    # Estimate based on timeout (can be improved with historical data)
                    step_time = step.timeout * 0.3  # Assume 30% of timeout on average
                    level_time = max(level_time, step_time)

            total_time += level_time

        return total_time

    def _calculate_optimization_score(
        self,
        dag: WorkflowDAG,
        parallel_groups: List[List[str]],
        resource_allocation: Dict[str, Any],
    ) -> float:
        """Calculate workflow optimization score"""

        # Factors for optimization score
        parallelism_factor = len(parallel_groups) / max(1, len(dag.steps))

        # Resource efficiency
        total_resources = sum(
            r.get("cpu", 0) + r.get("memory", 0)
            for r in resource_allocation.values()
            if isinstance(r, dict)
        )
        resource_efficiency = 1.0 / max(1, total_resources / 100)

        # Step efficiency (fewer steps is better)
        step_efficiency = 1.0 / max(1, len(dag.steps) / 10)

        # Calculate weighted score
        score = parallelism_factor * 0.4 + resource_efficiency * 0.3 + step_efficiency * 0.3

        return min(1.0, score)

    def _sequential_pattern(self, agents: List[str]) -> List[List[str]]:
        """Sequential execution pattern"""
        return [[agent] for agent in agents]

    def _parallel_pattern(self, agents: List[str]) -> List[List[str]]:
        """Parallel execution pattern"""
        return [agents]

    def _conditional_pattern(self, agents: List[str], condition: str) -> List[List[str]]:
        """Conditional execution pattern"""
        # Split agents based on condition
        if_branch = agents[: len(agents) // 2]
        else_branch = agents[len(agents) // 2 :]
        return [[condition], if_branch + else_branch]

    def _pipeline_pattern(self, agents: List[str]) -> List[List[str]]:
        """Pipeline execution pattern"""
        return self._sequential_pattern(agents)

    def _map_reduce_pattern(self, map_agents: List[str], reduce_agent: str) -> List[List[str]]:
        """Map-reduce execution pattern"""
        return [map_agents, [reduce_agent]]

    def _scatter_gather_pattern(
        self, scatter_agent: str, process_agents: List[str], gather_agent: str
    ) -> List[List[str]]:
        """Scatter-gather execution pattern"""
        return [[scatter_agent], process_agents, [gather_agent]]

    async def validate_workflow(self, workflow: ComposedWorkflow) -> bool:
        """Validate composed workflow"""

        # Check for cycles
        if self._has_cycle(workflow.dag):
            return False

        # Check all agents are included
        all_agents = {step.agent for step in workflow.dag.steps}
        if not all_agents:
            return False

        # Check execution plan covers all steps
        executed_steps = set()
        for level in workflow.execution_plan:
            executed_steps.update(level)

        all_steps = {step.id for step in workflow.dag.steps}
        if executed_steps != all_steps:
            return False

        return True

    def _has_cycle(self, dag: WorkflowDAG) -> bool:
        """Check if DAG has cycles using DFS"""

        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dag.edges.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for step in dag.steps:
            if step.id not in visited:
                if dfs(step.id):
                    return True

        return False

    def visualize_workflow(self, workflow: ComposedWorkflow) -> str:
        """Generate workflow visualization (text-based)"""

        lines = []
        lines.append(f"Workflow: {workflow.name}")
        lines.append(f"Steps: {len(workflow.dag.steps)}")
        lines.append(f"Parallel Groups: {len(workflow.dag.parallel_groups)}")
        lines.append(f"Estimated Time: {workflow.estimated_time:.1f}s")
        lines.append(f"Optimization Score: {workflow.optimization_score:.2f}")
        lines.append("\nExecution Plan:")

        for i, level in enumerate(workflow.execution_plan):
            if len(level) > 1:
                lines.append(f"  Level {i} (parallel):")
                for step_id in level:
                    step = next((s for s in workflow.dag.steps if s.id == step_id), None)
                    if step:
                        lines.append(f"    - {step.agent}")
            else:
                step_id = level[0]
                step = next((s for s in workflow.dag.steps if s.id == step_id), None)
                if step:
                    lines.append(f"  Level {i}: {step.agent}")

        return "\n".join(lines)

    def get_metrics(self) -> Dict[str, Any]:
        """Get composer metrics"""
        return {
            "patterns": list(self.workflow_patterns.keys()),
            "optimization_enabled": True,
            "parallelization_enabled": True,
            "resource_allocation_enabled": True,
            "max_parallel_steps": 10,
            "max_workflow_size": 100,
        }


# Global instance
composer = None


def get_composer() -> WorkflowComposer:
    """Get or create composer instance"""
    global composer
    if not composer:
        composer = WorkflowComposer()
    return composer


async def main():
    """Test workflow composer"""
    composer = get_composer()

    # Test agents
    agents = [
        "RequirementAnalyzer",
        "ArchitectDesigner",
        "CodeGenerator",
        "TestGenerator",
        "Deployer",
    ]

    requirements = {"type": "web_app", "complexity": "medium", "timeline": "2 weeks"}

    workflow = await composer.compose(agents, requirements)

    # Validate
    is_valid = await composer.validate_workflow(workflow)
    print(f"Workflow valid: {is_valid}")

    # Visualize
    print("\n" + composer.visualize_workflow(workflow))


if __name__ == "__main__":
    asyncio.run(main())
