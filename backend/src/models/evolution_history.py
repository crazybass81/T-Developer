"""
Evolution History Tracking Model
Day 6: Agent Registry Data Model
Generated: 2024-11-18

Track agent evolution lineage and patterns
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class EvolutionRecord:
    """Record of an evolution event"""

    agent_id: str
    generation: int
    parent_ids: List[str] = field(default_factory=list)
    mutations: List[str] = field(default_factory=list)
    fitness_score: float = 0.0
    constraints_met: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_successful(self) -> bool:
        """Check if evolution was successful"""
        return self.constraints_met and self.fitness_score > 0.5


class EvolutionLineage:
    """Track evolution lineage of agents"""

    def __init__(self, root_agent_id: str):
        self.root_agent_id = root_agent_id
        self.lineage_tree: Dict[str, Dict] = {
            root_agent_id: {"generation": 0, "parent": None, "children": [], "fitness": 0.0}
        }
        self.generation_count = 0

    def add_evolution(
        self, parent_id: str, child_id: str, generation: int, fitness_improvement: float
    ) -> Dict:
        """Add an evolution step to lineage"""

        if parent_id in self.lineage_tree:
            # Add child to parent's children list
            self.lineage_tree[parent_id]["children"].append(child_id)

            # Add child node
            parent_fitness = self.lineage_tree[parent_id]["fitness"]
            self.lineage_tree[child_id] = {
                "generation": generation,
                "parent": parent_id,
                "children": [],
                "fitness": parent_fitness + fitness_improvement,
            }

            self.generation_count = max(self.generation_count, generation)

            return self.lineage_tree[child_id]

        return {}

    def get_generation_count(self) -> int:
        """Get total number of generations"""
        return self.generation_count

    def get_total_fitness_improvement(self) -> float:
        """Get total fitness improvement from root"""
        best_agent = self.get_best_agent()
        if best_agent and best_agent in self.lineage_tree:
            return self.lineage_tree[best_agent]["fitness"]
        return 0.0

    def get_best_agent(self) -> str:
        """Get agent with highest fitness"""
        best_agent = None
        best_fitness = -1

        for agent_id, data in self.lineage_tree.items():
            if data["fitness"] > best_fitness:
                best_fitness = data["fitness"]
                best_agent = agent_id

        return best_agent

    def get_ancestors(self, agent_id: str) -> List[str]:
        """Get all ancestors of an agent"""
        ancestors = []
        current = agent_id

        while current in self.lineage_tree:
            parent = self.lineage_tree[current]["parent"]
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break

        return ancestors


class EvolutionMetrics:
    """Track and analyze evolution metrics"""

    def __init__(self):
        self.records: List[Dict] = []

    def record_evolution(
        self, agent_id: str, generation: int, fitness: float, size_kb: float, speed_us: float
    ):
        """Record evolution metrics"""
        self.records.append(
            {
                "agent_id": agent_id,
                "generation": generation,
                "fitness": fitness,
                "size_kb": size_kb,
                "speed_us": speed_us,
                "timestamp": datetime.utcnow(),
            }
        )

    def get_statistics(self) -> Dict:
        """Get statistical summary of evolution"""
        if not self.records:
            return {}

        fitness_values = [r["fitness"] for r in self.records]
        size_values = [r["size_kb"] for r in self.records]
        speed_values = [r["speed_us"] for r in self.records]

        # Determine fitness trend
        if len(fitness_values) >= 2:
            if fitness_values[-1] > fitness_values[0]:
                fitness_trend = "improving"
            elif fitness_values[-1] < fitness_values[0]:
                fitness_trend = "degrading"
            else:
                fitness_trend = "stable"
        else:
            fitness_trend = "unknown"

        return {
            "avg_fitness": sum(fitness_values) / len(fitness_values),
            "avg_size_kb": sum(size_values) / len(size_values),
            "avg_speed_us": sum(speed_values) / len(speed_values),
            "fitness_trend": fitness_trend,
            "total_generations": len(self.records),
        }


class PatternAnalyzer:
    """Analyze successful evolution patterns"""

    def __init__(self):
        self.patterns: Dict[str, Dict] = {}

    def record_pattern(self, pattern_type: str, success_rate: float, avg_improvement: float):
        """Record an evolution pattern"""
        self.patterns[pattern_type] = {
            "type": pattern_type,
            "success_rate": success_rate,
            "avg_improvement": avg_improvement,
            "occurrences": self.patterns.get(pattern_type, {}).get("occurrences", 0) + 1,
        }

    def get_best_patterns(self, top_n: int = 5) -> List[Dict]:
        """Get the most successful patterns"""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda x: x["success_rate"] * x["avg_improvement"],
            reverse=True,
        )
        return sorted_patterns[:top_n]

    def get_pattern_by_type(self, pattern_type: str) -> Optional[Dict]:
        """Get a specific pattern by type"""
        return self.patterns.get(pattern_type)

    def get_average_success_rate(self) -> float:
        """Get average success rate across all patterns"""
        if not self.patterns:
            return 0.0

        rates = [p["success_rate"] for p in self.patterns.values()]
        return sum(rates) / len(rates)
