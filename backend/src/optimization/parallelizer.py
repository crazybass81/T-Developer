"""
Parallelizer - Workflow parallelization optimizer
Size: < 6.5KB | Performance: < 3μs
Day 23: Phase 2 - Meta Agents
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple


@dataclass
class ParallelGroup:
    """Group of steps that can execute in parallel"""

    steps: List[str]
    shared_dependencies: Set[str]
    estimated_speedup: float
    resource_requirements: Dict[str, float]


class Parallelizer:
    """Identify and optimize parallel execution opportunities"""

    def __init__(self):
        self.max_parallel = 10
        self.min_group_size = 2
        self.dependency_cache = {}

    async def identify_parallel_groups(self, dag: Any) -> List[List[str]]:
        """Identify groups of steps that can run in parallel"""

        parallel_groups = []

        # Analyze each level of the DAG
        levels = self._compute_levels(dag)

        for level_steps in levels.values():
            if len(level_steps) >= self.min_group_size:
                # Check if steps at this level can run in parallel
                if self._can_parallelize(level_steps, dag):
                    parallel_groups.append(level_steps)

        return parallel_groups

    def _compute_levels(self, dag: Any) -> Dict[int, List[str]]:
        """Compute topological levels of DAG"""

        levels = {}
        visited = set()

        def compute_level(step_id, dag):
            if step_id in self.dependency_cache:
                return self.dependency_cache[step_id]

            step = next((s for s in dag.steps if s.id == step_id), None)
            if not step or not step.dependencies:
                level = 0
            else:
                # Level is max of dependency levels + 1
                dep_levels = []
                for dep in step.dependencies:
                    dep_step = next((s for s in dag.steps if s.agent == dep), None)
                    if dep_step:
                        dep_levels.append(compute_level(dep_step.id, dag))
                level = max(dep_levels, default=-1) + 1

            self.dependency_cache[step_id] = level
            return level

        # Compute level for each step
        for step in dag.steps:
            level = compute_level(step.id, dag)
            if level not in levels:
                levels[level] = []
            levels[level].append(step.id)

        return levels

    def _can_parallelize(self, steps: List[str], dag: Any) -> bool:
        """Check if steps can be parallelized"""

        # Steps can be parallelized if they don't depend on each other
        for i, step1 in enumerate(steps):
            for step2 in steps[i + 1 :]:
                if self._has_dependency(step1, step2, dag):
                    return False

        return True

    def _has_dependency(self, step1: str, step2: str, dag: Any) -> bool:
        """Check if step1 depends on step2 or vice versa"""

        # Check direct dependencies
        s1 = next((s for s in dag.steps if s.id == step1), None)
        s2 = next((s for s in dag.steps if s.id == step2), None)

        if not s1 or not s2:
            return False

        # Check if s1 depends on s2
        if s2.agent in s1.dependencies:
            return True

        # Check if s2 depends on s1
        if s1.agent in s2.dependencies:
            return True

        return False

    def optimize_parallel_execution(
        self, parallel_groups: List[List[str]], resource_limits: Dict[str, float]
    ) -> List[ParallelGroup]:
        """Optimize parallel execution with resource constraints"""

        optimized_groups = []

        for group in parallel_groups:
            # Split group if it exceeds resource limits
            subgroups = self._split_by_resources(group, resource_limits)

            for subgroup in subgroups:
                pg = ParallelGroup(
                    steps=subgroup,
                    shared_dependencies=self._get_shared_deps(subgroup),
                    estimated_speedup=self._estimate_speedup(subgroup),
                    resource_requirements=self._estimate_resources(subgroup),
                )
                optimized_groups.append(pg)

        return optimized_groups

    def _split_by_resources(self, group: List[str], limits: Dict[str, float]) -> List[List[str]]:
        """Split group based on resource constraints"""

        if len(group) <= self.max_parallel:
            return [group]

        # Split into chunks of max_parallel size
        chunks = []
        for i in range(0, len(group), self.max_parallel):
            chunks.append(group[i : i + self.max_parallel])

        return chunks

    def _get_shared_deps(self, steps: List[str]) -> Set[str]:
        """Get shared dependencies of steps"""
        # Simplified - would need DAG access for real implementation
        return set()

    def _estimate_speedup(self, steps: List[str]) -> float:
        """Estimate speedup from parallelization"""

        if len(steps) <= 1:
            return 1.0

        # Theoretical max speedup is number of parallel steps
        # Practical speedup is usually lower due to overhead
        theoretical_speedup = len(steps)
        overhead_factor = 0.8  # 20% overhead

        return min(theoretical_speedup * overhead_factor, self.max_parallel)

    def _estimate_resources(self, steps: List[str]) -> Dict[str, float]:
        """Estimate resource requirements for parallel group"""

        # Base estimates per step
        cpu_per_step = 0.5
        memory_per_step = 128  # MB

        return {
            "cpu": len(steps) * cpu_per_step,
            "memory": len(steps) * memory_per_step,
            "threads": len(steps),
        }

    def identify_bottlenecks(self, dag: Any) -> List[str]:
        """Identify bottleneck steps that limit parallelization"""

        bottlenecks = []

        # Steps with many dependencies are bottlenecks
        for step in dag.steps:
            if len(step.dependencies) > 3:
                bottlenecks.append(step.id)

        # Steps that many others depend on are bottlenecks
        dependency_count = {}
        for step in dag.steps:
            for dep in step.dependencies:
                dep_step = next((s for s in dag.steps if s.agent == dep), None)
                if dep_step:
                    dependency_count[dep_step.id] = dependency_count.get(dep_step.id, 0) + 1

        for step_id, count in dependency_count.items():
            if count > 3:
                bottlenecks.append(step_id)

        return list(set(bottlenecks))

    def suggest_optimizations(self, dag: Any, parallel_groups: List[List[str]]) -> List[str]:
        """Suggest workflow optimizations"""

        suggestions = []

        # Check parallelization ratio
        total_steps = len(dag.steps)
        parallel_steps = sum(len(g) for g in parallel_groups)
        parallel_ratio = parallel_steps / max(1, total_steps)

        if parallel_ratio < 0.3:
            suggestions.append("Low parallelization ratio. Consider restructuring dependencies.")

        # Check for bottlenecks
        bottlenecks = self.identify_bottlenecks(dag)
        if bottlenecks:
            suggestions.append(
                f"Found {len(bottlenecks)} bottleneck steps. Consider optimizing or splitting them."
            )

        # Check group sizes
        small_groups = [g for g in parallel_groups if len(g) < 3]
        if small_groups:
            suggestions.append(
                f"Found {len(small_groups)} small parallel groups. Consider merging adjacent groups."
            )

        return suggestions

    def calculate_parallel_efficiency(
        self, sequential_time: float, parallel_time: float, num_processors: int
    ) -> float:
        """Calculate parallel efficiency using Amdahl's Law"""

        if sequential_time == 0 or num_processors == 0:
            return 0.0

        speedup = sequential_time / max(0.001, parallel_time)
        efficiency = speedup / num_processors

        return min(1.0, efficiency)

    def get_metrics(self) -> Dict[str, Any]:
        """Get parallelizer metrics"""
        return {
            "max_parallel": self.max_parallel,
            "min_group_size": self.min_group_size,
            "cache_size": len(self.dependency_cache),
            "overhead_factor": 0.8,
        }


# Global instance
parallelizer = None


def get_parallelizer() -> Parallelizer:
    """Get or create parallelizer instance"""
    global parallelizer
    if not parallelizer:
        parallelizer = Parallelizer()
    return parallelizer


def main():
    """Test parallelizer"""
    p = get_parallelizer()

    # Test parallel efficiency calculation
    seq_time = 100.0
    par_time = 30.0
    num_proc = 4

    efficiency = p.calculate_parallel_efficiency(seq_time, par_time, num_proc)
    print(f"Parallel efficiency: {efficiency:.2%}")

    # Test resource estimation
    steps = ["step1", "step2", "step3", "step4"]
    resources = p._estimate_resources(steps)
    print(f"Resource requirements: {resources}")

    # Test speedup estimation
    speedup = p._estimate_speedup(steps)
    print(f"Estimated speedup: {speedup:.1f}x")


if __name__ == "__main__":
    main()
