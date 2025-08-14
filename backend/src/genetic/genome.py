"""Day 46: Agent Genome Representation System - 6.5KB"""
import hashlib
import random
from typing import Any, Dict, List, Optional


class Genome:
    """Genetic representation of an agent with DNA structure"""

    def __init__(self, dna: Optional[Dict[str, Any]] = None):
        """Initialize genome with DNA structure"""
        if dna:
            self.dna = dna
        else:
            self.dna = self._create_default_dna()
        self._fitness_cache = None

    def _create_default_dna(self) -> Dict[str, Any]:
        """Create default DNA structure for agent"""
        return {
            "genes": {
                "memory": random.randint(3000, 6500),  # Memory in bytes
                "speed": random.uniform(1.0, 3.0),  # Microseconds
                "capabilities": self._random_capabilities(),
                "optimization": random.uniform(0.5, 1.0),
                "architecture": random.choice(["reactive", "deliberative", "hybrid"]),
                "learning_rate": random.uniform(0.001, 0.1),
                "exploration": random.uniform(0.1, 0.3),
                "parallelism": random.randint(1, 4),
                "cache_size": random.randint(10, 100),
                "error_tolerance": random.uniform(0.8, 0.99),
            },
            "metadata": {
                "generation": 0,
                "parent_ids": [],
                "mutation_count": 0,
                "creation_time": None,
                "lineage": [],
            },
        }

    def _random_capabilities(self) -> List[str]:
        """Generate random capabilities for agent"""
        all_caps = [
            "search",
            "analysis",
            "generation",
            "validation",
            "optimization",
            "prediction",
            "classification",
            "clustering",
            "transformation",
            "aggregation",
        ]
        count = random.randint(2, 5)
        return random.sample(all_caps, count)

    def encode_traits(self, traits: Dict[str, Any]) -> str:
        """Encode agent traits into genetic string"""
        # Simple encoding: convert to binary representation
        encoded_parts = []

        # Encode numeric values
        if "memory_limit" in traits:
            mem_bits = format(min(traits["memory_limit"], 6500), "013b")
            encoded_parts.append(mem_bits)

        if "instantiation_time" in traits:
            time_bits = format(int(traits["instantiation_time"] * 1000), "012b")
            encoded_parts.append(time_bits)

        if "optimization_level" in traits:
            opt_bits = format(int(traits["optimization_level"] * 100), "07b")
            encoded_parts.append(opt_bits)

        # Encode capabilities as bit flags
        if "capabilities" in traits:
            cap_map = {
                "search": 0,
                "analysis": 1,
                "generation": 2,
                "validation": 3,
                "optimization": 4,
                "prediction": 5,
                "classification": 6,
                "clustering": 7,
                "transformation": 8,
                "aggregation": 9,
            }
            cap_bits = ["0"] * 10
            for cap in traits.get("capabilities", []):
                if cap in cap_map:
                    cap_bits[cap_map[cap]] = "1"
            encoded_parts.append("".join(cap_bits))

        # Convert binary to DNA-like sequence (AGCT)
        binary_str = "".join(encoded_parts)
        dna_map = {"00": "A", "01": "G", "10": "C", "11": "T"}

        dna_sequence = []
        for i in range(0, len(binary_str), 2):
            if i + 1 < len(binary_str):
                pair = binary_str[i : i + 2]
                dna_sequence.append(dna_map[pair])
            else:
                dna_sequence.append("A")  # Padding

        return "".join(dna_sequence)

    def decode_genes(self, encoded: str) -> Dict[str, Any]:
        """Decode genetic string back to traits"""
        # Convert DNA sequence back to binary
        dna_map = {"A": "00", "G": "01", "C": "10", "T": "11"}
        binary_str = "".join(dna_map.get(c, "00") for c in encoded)

        traits = {}
        pos = 0

        # Decode memory (13 bits)
        if pos + 13 <= len(binary_str):
            mem_bits = binary_str[pos : pos + 13]
            traits["memory_limit"] = int(mem_bits, 2)
            pos += 13

        # Decode time (12 bits)
        if pos + 12 <= len(binary_str):
            time_bits = binary_str[pos : pos + 12]
            traits["instantiation_time"] = int(time_bits, 2) / 1000.0
            pos += 12

        # Decode optimization (7 bits)
        if pos + 7 <= len(binary_str):
            opt_bits = binary_str[pos : pos + 7]
            traits["optimization_level"] = int(opt_bits, 2) / 100.0
            pos += 7

        # Decode capabilities (10 bits)
        if pos + 10 <= len(binary_str):
            cap_bits = binary_str[pos : pos + 10]
            cap_names = [
                "search",
                "analysis",
                "generation",
                "validation",
                "optimization",
                "prediction",
                "classification",
                "clustering",
                "transformation",
                "aggregation",
            ]
            capabilities = []
            for i, bit in enumerate(cap_bits):
                if bit == "1" and i < len(cap_names):
                    capabilities.append(cap_names[i])
            traits["capabilities"] = capabilities

        return traits

    def mutate(self, rate: float = 0.01) -> None:
        """Apply mutations to genome"""
        genes = self.dna["genes"]

        for key in genes:
            if random.random() < rate:
                if key == "memory":
                    # Mutate memory within constraints
                    delta = random.randint(-500, 500)
                    genes[key] = max(1000, min(6500, genes[key] + delta))
                elif key == "speed":
                    # Mutate speed
                    delta = random.uniform(-0.5, 0.5)
                    genes[key] = max(0.5, min(5.0, genes[key] + delta))
                elif key == "capabilities":
                    # Add or remove capability
                    if random.random() < 0.5 and len(genes[key]) > 1:
                        genes[key].pop(random.randrange(len(genes[key])))
                    else:
                        new_cap = random.choice(self._random_capabilities())
                        if new_cap not in genes[key]:
                            genes[key].append(new_cap)
                elif key == "optimization":
                    delta = random.uniform(-0.1, 0.1)
                    genes[key] = max(0.0, min(1.0, genes[key] + delta))
                elif key == "architecture":
                    genes[key] = random.choice(["reactive", "deliberative", "hybrid"])
                elif key == "learning_rate":
                    genes[key] *= random.uniform(0.8, 1.2)
                    genes[key] = max(0.0001, min(0.2, genes[key]))

        self.dna["metadata"]["mutation_count"] += 1
        self._fitness_cache = None  # Invalidate cache

    def crossover(self, other: "Genome") -> "Genome":
        """Create offspring through crossover with another genome"""
        # Single-point crossover
        offspring_dna = {"genes": {}, "metadata": {}}

        genes1 = self.dna["genes"]
        genes2 = other.dna["genes"]

        gene_keys = list(genes1.keys())
        crossover_point = random.randint(1, len(gene_keys) - 1)

        # Take genes from both parents
        for i, key in enumerate(gene_keys):
            if i < crossover_point:
                offspring_dna["genes"][key] = genes1[key]
            else:
                offspring_dna["genes"][key] = genes2[key]

        # Update metadata
        offspring_dna["metadata"] = {
            "generation": max(
                self.dna["metadata"]["generation"], other.dna["metadata"]["generation"]
            )
            + 1,
            "parent_ids": [id(self), id(other)],
            "mutation_count": 0,
            "creation_time": None,
            "lineage": self.dna["metadata"].get("lineage", []) + [id(self)],
        }

        return Genome(offspring_dna)

    def calculate_fitness(self) -> float:
        """Calculate fitness score for this genome"""
        if self._fitness_cache is not None:
            return self._fitness_cache

        genes = self.dna["genes"]
        fitness = 0.0

        # Memory efficiency (prefer lower memory)
        memory_score = 1.0 - (genes["memory"] / 6500.0) * 0.3
        fitness += memory_score * 0.25

        # Speed score (prefer faster)
        speed_score = 1.0 - (genes["speed"] / 3.0) * 0.5
        fitness += speed_score * 0.25

        # Capability diversity
        cap_score = len(genes["capabilities"]) / 10.0
        fitness += cap_score * 0.2

        # Optimization level
        fitness += genes["optimization"] * 0.15

        # Architecture bonus
        if genes["architecture"] == "hybrid":
            fitness += 0.05

        # Learning capability
        lr_score = min(1.0, genes["learning_rate"] / 0.01)
        fitness += lr_score * 0.1

        # Normalize to [0, 1]
        fitness = max(0.0, min(1.0, fitness))

        self._fitness_cache = fitness
        return fitness

    def to_hash(self) -> str:
        """Generate unique hash for this genome"""
        gene_str = str(sorted(self.dna["genes"].items()))
        return hashlib.md5(gene_str.encode()).hexdigest()[:16]

    def distance_to(self, other: "Genome") -> float:
        """Calculate genetic distance to another genome"""
        distance = 0.0
        genes1 = self.dna["genes"]
        genes2 = other.dna["genes"]

        # Compare numeric genes
        for key in ["memory", "speed", "optimization", "learning_rate"]:
            if key in genes1 and key in genes2:
                diff = abs(genes1[key] - genes2[key])
                # Normalize difference
                if key == "memory":
                    diff /= 6500.0
                elif key == "speed":
                    diff /= 3.0
                else:
                    diff = min(1.0, diff)
                distance += diff

        # Compare capabilities
        caps1 = set(genes1.get("capabilities", []))
        caps2 = set(genes2.get("capabilities", []))
        cap_diff = len(caps1.symmetric_difference(caps2)) / 10.0
        distance += cap_diff

        # Compare architecture
        if genes1.get("architecture") != genes2.get("architecture"):
            distance += 0.5

        return distance / 6.0  # Normalize by number of comparisons
