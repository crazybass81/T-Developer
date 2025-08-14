"""
Tournament Selection Implementation

Simple tournament selection for genetic algorithms.
"""

import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TournamentSelection:
    """Simple tournament selection implementation"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize tournament selection"""
        self.config = config or {}
        self.tournament_size = self.config.get("tournament_size", 3)
        self.pressure = self.config.get("pressure", 2.0)

    async def select(
        self, population: List[Dict[str, Any]], num_parents: int, fitness_key: str = "fitness"
    ) -> List[Dict[str, Any]]:
        """Select parents using tournament selection"""
        parents = []

        for _ in range(num_parents):
            # Run tournament
            tournament = random.sample(population, min(self.tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x.get(fitness_key, 0.0))
            parents.append(winner.copy())

        return parents
