"""
Agent Gene Pool Model
Day 6: Agent Registry Data Model
Generated: 2024-11-18

Manage genetic diversity and selection in agent evolution
"""

import math
from typing import Dict, List, Optional


class AgentGenePool:
    """Manage pool of agents for evolution"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.agents: Dict[str, Dict] = {}

    def add_agent(self, agent_id: str, fitness: float, genes: Dict = None):
        """Add an agent to the gene pool"""
        self.agents[agent_id] = {"fitness": fitness, "genes": genes or {}, "age": 0}

        # Apply selection pressure if pool is full
        if len(self.agents) > self.max_size:
            self._apply_selection_pressure()

    def size(self) -> int:
        """Get current pool size"""
        return len(self.agents)

    def get_best_agent(self) -> Optional[str]:
        """Get agent with highest fitness"""
        if not self.agents:
            return None

        return max(self.agents.keys(), key=lambda k: self.agents[k]["fitness"])

    def get_average_fitness(self) -> float:
        """Calculate average fitness of pool"""
        if not self.agents:
            return 0.0

        total_fitness = sum(a["fitness"] for a in self.agents.values())
        return total_fitness / len(self.agents)

    def get_all_agents(self) -> List[Dict]:
        """Get all agents in pool"""
        return [{"id": agent_id, **data} for agent_id, data in self.agents.items()]

    def _apply_selection_pressure(self):
        """Remove least fit agents to maintain pool size"""
        # Sort agents by fitness
        sorted_agents = sorted(self.agents.items(), key=lambda x: x[1]["fitness"], reverse=True)

        # Keep only top agents
        self.agents = dict(sorted_agents[: self.max_size])

    def select_parents(self, count: int = 2) -> List[str]:
        """Select parents for reproduction using tournament selection"""
        if len(self.agents) < count:
            return list(self.agents.keys())

        # Tournament selection
        selected = []
        tournament_size = min(5, len(self.agents))

        for _ in range(count):
            # Random tournament
            import random

            tournament = random.sample(list(self.agents.keys()), tournament_size)

            # Select best from tournament
            winner = max(tournament, key=lambda k: self.agents[k]["fitness"])
            selected.append(winner)

        return selected


class GeneticDiversity:
    """Track and maintain genetic diversity"""

    def __init__(self):
        self.genomes: Dict[str, Dict] = {}

    def add_genome(self, agent_id: str, genome: Dict):
        """Add agent genome"""
        self.genomes[agent_id] = genome

    def calculate_diversity(self) -> float:
        """Calculate genetic diversity score"""
        if len(self.genomes) < 2:
            return 0.0

        # Calculate pairwise distances
        agents = list(self.genomes.keys())
        total_distance = 0
        pairs = 0

        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                distance = self._genetic_distance(self.genomes[agents[i]], self.genomes[agents[j]])
                total_distance += distance
                pairs += 1

        # Average distance as diversity measure
        if pairs > 0:
            avg_distance = total_distance / pairs
            # Normalize to 0-1 range
            return min(1.0, avg_distance / 10)

        return 0.0

    def _genetic_distance(self, genome1: Dict, genome2: Dict) -> float:
        """Calculate distance between two genomes"""
        all_keys = set(genome1.keys()) | set(genome2.keys())

        if not all_keys:
            return 0.0

        distance = 0.0
        for key in all_keys:
            val1 = genome1.get(key, 0)
            val2 = genome2.get(key, 0)

            # Calculate difference
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                distance += abs(val1 - val2)
            elif val1 != val2:
                distance += 1

        return distance

    def needs_diversity_injection(self, threshold: float = 0.2) -> bool:
        """Check if diversity is too low"""
        return self.calculate_diversity() < threshold
