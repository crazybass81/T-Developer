"""
Resource Allocator - Optimal resource allocation for workflows
Size: < 6.5KB | Performance: < 3μs
Day 23: Phase 2 - Meta Agents
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ResourceAllocation:
    """Resource allocation for a step"""

    step_id: str
    cpu: float  # CPU cores
    memory: int  # MB
    disk: int  # MB
    network: float  # Mbps
    priority: int  # 1-10


@dataclass
class ResourcePool:
    """Available resource pool"""

    total_cpu: float
    total_memory: int
    total_disk: int
    total_network: float
    allocated_cpu: float = 0.0
    allocated_memory: int = 0
    allocated_disk: int = 0
    allocated_network: float = 0.0

    @property
    def available_cpu(self) -> float:
        return self.total_cpu - self.allocated_cpu

    @property
    def available_memory(self) -> int:
        return self.total_memory - self.allocated_memory

    @property
    def available_disk(self) -> int:
        return self.total_disk - self.allocated_disk

    @property
    def available_network(self) -> float:
        return self.total_network - self.allocated_network


class ResourceAllocator:
    """Allocate resources optimally for workflow execution"""

    def __init__(self):
        self.default_pool = ResourcePool(
            total_cpu=8.0,
            total_memory=16384,  # 16GB
            total_disk=102400,  # 100GB
            total_network=1000.0,  # 1Gbps
        )
        self.allocation_strategies = {
            "balanced": self._balanced_allocation,
            "performance": self._performance_allocation,
            "cost": self._cost_allocation,
            "fair": self._fair_allocation,
        }
        self.current_strategy = "balanced"

    async def allocate(
        self, dag: Any, constraints: Dict[str, Any]
    ) -> Dict[str, ResourceAllocation]:
        """Allocate resources for workflow DAG"""

        # Get resource pool from constraints or use default
        pool = self._get_resource_pool(constraints)

        # Estimate resource needs for each step
        step_requirements = self._estimate_requirements(dag)

        # Apply allocation strategy
        strategy = self.allocation_strategies[self.current_strategy]
        allocations = strategy(dag, step_requirements, pool)

        # Validate allocations
        if not self._validate_allocations(allocations, pool):
            # Fallback to minimal allocation
            allocations = self._minimal_allocation(dag, pool)

        return allocations

    def _get_resource_pool(self, constraints: Dict[str, Any]) -> ResourcePool:
        """Get resource pool from constraints"""

        if not constraints:
            return self.default_pool

        return ResourcePool(
            total_cpu=constraints.get("cpu", self.default_pool.total_cpu),
            total_memory=constraints.get("memory", self.default_pool.total_memory),
            total_disk=constraints.get("disk", self.default_pool.total_disk),
            total_network=constraints.get("network", self.default_pool.total_network),
        )

    def _estimate_requirements(self, dag: Any) -> Dict[str, Dict[str, float]]:
        """Estimate resource requirements for each step"""

        requirements = {}

        for step in dag.steps:
            # Base requirements by agent type
            if "analyzer" in step.agent.lower():
                req = {"cpu": 1.0, "memory": 512, "disk": 100, "network": 10}
            elif "generator" in step.agent.lower():
                req = {"cpu": 2.0, "memory": 1024, "disk": 500, "network": 50}
            elif "test" in step.agent.lower():
                req = {"cpu": 1.5, "memory": 768, "disk": 200, "network": 20}
            elif "deploy" in step.agent.lower():
                req = {"cpu": 0.5, "memory": 256, "disk": 1000, "network": 100}
            else:
                req = {"cpu": 0.5, "memory": 256, "disk": 50, "network": 10}

            requirements[step.id] = req

        return requirements

    def _balanced_allocation(
        self, dag: Any, requirements: Dict[str, Dict[str, float]], pool: ResourcePool
    ) -> Dict[str, ResourceAllocation]:
        """Balanced allocation strategy"""

        allocations = {}

        for step in dag.steps:
            req = requirements.get(step.id, {})

            # Allocate based on requirements with some buffer
            allocation = ResourceAllocation(
                step_id=step.id,
                cpu=min(req.get("cpu", 0.5) * 1.2, pool.available_cpu),
                memory=int(min(req.get("memory", 256) * 1.2, pool.available_memory)),
                disk=int(min(req.get("disk", 50) * 1.2, pool.available_disk)),
                network=min(req.get("network", 10) * 1.2, pool.available_network),
                priority=5,  # Medium priority
            )

            allocations[step.id] = allocation

            # Update pool
            pool.allocated_cpu += allocation.cpu
            pool.allocated_memory += allocation.memory
            pool.allocated_disk += allocation.disk
            pool.allocated_network += allocation.network

        return allocations

    def _performance_allocation(
        self, dag: Any, requirements: Dict[str, Dict[str, float]], pool: ResourcePool
    ) -> Dict[str, ResourceAllocation]:
        """Performance-focused allocation strategy"""

        allocations = {}

        for step in dag.steps:
            req = requirements.get(step.id, {})

            # Allocate maximum available resources for performance
            allocation = ResourceAllocation(
                step_id=step.id,
                cpu=min(req.get("cpu", 0.5) * 2.0, pool.available_cpu),
                memory=int(min(req.get("memory", 256) * 2.0, pool.available_memory)),
                disk=int(min(req.get("disk", 50) * 1.5, pool.available_disk)),
                network=min(req.get("network", 10) * 2.0, pool.available_network),
                priority=8,  # High priority
            )

            allocations[step.id] = allocation

            # Update pool
            pool.allocated_cpu += allocation.cpu
            pool.allocated_memory += allocation.memory
            pool.allocated_disk += allocation.disk
            pool.allocated_network += allocation.network

        return allocations

    def _cost_allocation(
        self, dag: Any, requirements: Dict[str, Dict[str, float]], pool: ResourcePool
    ) -> Dict[str, ResourceAllocation]:
        """Cost-optimized allocation strategy"""

        allocations = {}

        for step in dag.steps:
            req = requirements.get(step.id, {})

            # Allocate minimum required resources
            allocation = ResourceAllocation(
                step_id=step.id,
                cpu=min(req.get("cpu", 0.5) * 0.8, pool.available_cpu),
                memory=int(min(req.get("memory", 256) * 0.8, pool.available_memory)),
                disk=int(min(req.get("disk", 50) * 0.9, pool.available_disk)),
                network=min(req.get("network", 10) * 0.8, pool.available_network),
                priority=3,  # Low priority
            )

            allocations[step.id] = allocation

            # Update pool
            pool.allocated_cpu += allocation.cpu
            pool.allocated_memory += allocation.memory
            pool.allocated_disk += allocation.disk
            pool.allocated_network += allocation.network

        return allocations

    def _fair_allocation(
        self, dag: Any, requirements: Dict[str, Dict[str, float]], pool: ResourcePool
    ) -> Dict[str, ResourceAllocation]:
        """Fair share allocation strategy"""

        allocations = {}
        num_steps = len(dag.steps)

        if num_steps == 0:
            return allocations

        # Divide resources equally
        cpu_per_step = pool.total_cpu / num_steps
        memory_per_step = pool.total_memory // num_steps
        disk_per_step = pool.total_disk // num_steps
        network_per_step = pool.total_network / num_steps

        for step in dag.steps:
            allocation = ResourceAllocation(
                step_id=step.id,
                cpu=cpu_per_step,
                memory=memory_per_step,
                disk=disk_per_step,
                network=network_per_step,
                priority=5,  # Equal priority
            )

            allocations[step.id] = allocation

        return allocations

    def _minimal_allocation(self, dag: Any, pool: ResourcePool) -> Dict[str, ResourceAllocation]:
        """Minimal allocation fallback"""

        allocations = {}

        for step in dag.steps:
            allocation = ResourceAllocation(
                step_id=step.id, cpu=0.1, memory=128, disk=10, network=1.0, priority=1
            )
            allocations[step.id] = allocation

        return allocations

    def _validate_allocations(
        self, allocations: Dict[str, ResourceAllocation], pool: ResourcePool
    ) -> bool:
        """Validate resource allocations"""

        total_cpu = sum(a.cpu for a in allocations.values())
        total_memory = sum(a.memory for a in allocations.values())
        total_disk = sum(a.disk for a in allocations.values())
        total_network = sum(a.network for a in allocations.values())

        return (
            total_cpu <= pool.total_cpu
            and total_memory <= pool.total_memory
            and total_disk <= pool.total_disk
            and total_network <= pool.total_network
        )

    def optimize_allocation(
        self,
        allocations: Dict[str, ResourceAllocation],
        performance_data: Dict[str, Dict[str, float]],
    ) -> Dict[str, ResourceAllocation]:
        """Optimize allocation based on performance data"""

        optimized = {}

        for step_id, allocation in allocations.items():
            perf = performance_data.get(step_id, {})

            # Adjust based on actual usage
            cpu_usage = perf.get("cpu_usage", 0.5)
            memory_usage = perf.get("memory_usage", 0.5)

            optimized[step_id] = ResourceAllocation(
                step_id=step_id,
                cpu=allocation.cpu * cpu_usage * 1.1,  # 10% buffer
                memory=int(allocation.memory * memory_usage * 1.1),
                disk=allocation.disk,  # Keep disk same
                network=allocation.network,  # Keep network same
                priority=allocation.priority,
            )

        return optimized

    def calculate_cost(
        self, allocations: Dict[str, ResourceAllocation], pricing: Dict[str, float] = None
    ) -> float:
        """Calculate cost of resource allocation"""

        if not pricing:
            # Default pricing per unit per hour
            pricing = {
                "cpu": 0.05,  # $ per core per hour
                "memory": 0.001,  # $ per MB per hour
                "disk": 0.0001,  # $ per MB per hour
                "network": 0.01,  # $ per Mbps per hour
            }

        total_cost = 0.0

        for allocation in allocations.values():
            cost = (
                allocation.cpu * pricing["cpu"]
                + allocation.memory * pricing["memory"]
                + allocation.disk * pricing["disk"]
                + allocation.network * pricing["network"]
            )
            total_cost += cost

        return total_cost

    def get_utilization(self, pool: ResourcePool) -> Dict[str, float]:
        """Get resource utilization percentages"""

        return {
            "cpu": (pool.allocated_cpu / pool.total_cpu) * 100 if pool.total_cpu > 0 else 0,
            "memory": (pool.allocated_memory / pool.total_memory) * 100
            if pool.total_memory > 0
            else 0,
            "disk": (pool.allocated_disk / pool.total_disk) * 100 if pool.total_disk > 0 else 0,
            "network": (pool.allocated_network / pool.total_network) * 100
            if pool.total_network > 0
            else 0,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get allocator metrics"""
        return {
            "strategies": list(self.allocation_strategies.keys()),
            "current_strategy": self.current_strategy,
            "default_cpu": self.default_pool.total_cpu,
            "default_memory": self.default_pool.total_memory,
            "default_disk": self.default_pool.total_disk,
            "default_network": self.default_pool.total_network,
        }


# Global instance
allocator = None


def get_allocator() -> ResourceAllocator:
    """Get or create allocator instance"""
    global allocator
    if not allocator:
        allocator = ResourceAllocator()
    return allocator


def main():
    """Test resource allocator"""
    alloc = get_allocator()

    # Test cost calculation
    test_allocations = {
        "step1": ResourceAllocation("step1", 2.0, 1024, 500, 100, 5),
        "step2": ResourceAllocation("step2", 1.0, 512, 200, 50, 3),
    }

    cost = alloc.calculate_cost(test_allocations)
    print(f"Estimated cost: ${cost:.4f} per hour")

    # Test utilization
    pool = alloc.default_pool
    pool.allocated_cpu = 4.0
    pool.allocated_memory = 8192

    utilization = alloc.get_utilization(pool)
    print("\nResource utilization:")
    for resource, percent in utilization.items():
        print(f"  {resource}: {percent:.1f}%")


if __name__ == "__main__":
    main()
