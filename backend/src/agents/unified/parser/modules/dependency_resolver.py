"""
Dependency Resolver Module
Resolves dependencies between requirements and components
"""

from collections import defaultdict, deque
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class DependencyType(Enum):
    REQUIRES = "requires"
    BLOCKS = "blocks"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    CONFLICTS_WITH = "conflicts_with"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"


class DependencyResolver:
    """Resolves dependencies between requirements"""

    def __init__(self):
        self.dependency_indicators = {
            "requires": ["requires", "needs", "depends on", "prerequisite"],
            "blocks": ["blocks", "prevents", "must be done before"],
            "related": ["related to", "associated with", "connected to"],
            "conflicts": ["conflicts with", "incompatible with", "cannot be used with"],
            "extends": ["extends", "enhances", "builds upon"],
            "implements": ["implements", "realizes", "fulfills"],
        }

    async def resolve(
        self, requirements: List[Dict[str, Any]], entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Resolve dependencies between requirements"""

        # Extract dependencies
        dependencies = self._extract_dependencies(requirements)

        # Build dependency graph
        graph = self._build_dependency_graph(dependencies, requirements)

        # Detect cycles
        cycles = self._detect_cycles(graph)

        # Calculate dependency order
        order = self._topological_sort(graph) if not cycles else []

        # Identify critical path
        critical_path = self._find_critical_path(graph, requirements)

        # Group related requirements
        clusters = self._cluster_requirements(dependencies, requirements)

        # Analyze impact
        impact_analysis = self._analyze_impact(graph, requirements)

        return {
            "dependencies": dependencies,
            "graph": self._graph_to_dict(graph),
            "cycles": cycles,
            "execution_order": order,
            "critical_path": critical_path,
            "clusters": clusters,
            "impact_analysis": impact_analysis,
            "statistics": self._calculate_statistics(dependencies, graph),
        }

    def _extract_dependencies(self, requirements: List[Dict]) -> List[Dict]:
        """Extract dependencies from requirements"""
        dependencies = []

        for i, req1 in enumerate(requirements):
            req1_id = req1.get("id", f"req_{i}")
            req1_text = req1.get("text", "").lower()
            req1_entities = set(req1.get("entities", []))

            for j, req2 in enumerate(requirements):
                if i == j:
                    continue

                req2_id = req2.get("id", f"req_{j}")
                req2_text = req2.get("text", "").lower()
                req2_entities = set(req2.get("entities", []))

                # Check for explicit dependencies
                dep_type = self._check_explicit_dependency(req1_text, req2_text)
                if dep_type:
                    dependencies.append(
                        {
                            "from": req1_id,
                            "to": req2_id,
                            "type": dep_type,
                            "strength": "strong",
                        }
                    )

                # Check for entity-based dependencies
                elif req1_entities & req2_entities:
                    dependencies.append(
                        {
                            "from": req1_id,
                            "to": req2_id,
                            "type": DependencyType.RELATED_TO.value,
                            "strength": "weak",
                            "shared_entities": list(req1_entities & req2_entities),
                        }
                    )

        return dependencies

    def _check_explicit_dependency(self, text1: str, text2: str) -> Optional[str]:
        """Check for explicit dependency indicators"""
        for dep_type, indicators in self.dependency_indicators.items():
            for indicator in indicators:
                if indicator in text1 and any(word in text1 for word in text2.split()[:3]):
                    return dep_type
        return None

    def _build_dependency_graph(
        self, dependencies: List[Dict], requirements: List[Dict]
    ) -> Dict[str, Set[str]]:
        """Build dependency graph"""
        graph = defaultdict(set)

        # Add all requirements as nodes
        for req in requirements:
            req_id = req.get("id", f"req_{requirements.index(req)}")
            if req_id not in graph:
                graph[req_id] = set()

        # Add edges
        for dep in dependencies:
            if dep["type"] in [
                DependencyType.REQUIRES.value,
                DependencyType.DEPENDS_ON.value,
            ]:
                graph[dep["from"]].add(dep["to"])
            elif dep["type"] == DependencyType.BLOCKS.value:
                graph[dep["to"]].add(dep["from"])

        return dict(graph)

    def _detect_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect cycles in dependency graph"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort on dependency graph"""
        in_degree = defaultdict(int)

        # Calculate in-degrees
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1

        # Find nodes with no dependencies
        queue = deque([node for node in graph if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result if len(result) == len(graph) else []

    def _find_critical_path(
        self, graph: Dict[str, Set[str]], requirements: List[Dict]
    ) -> List[str]:
        """Find critical path through dependencies"""
        # Simple implementation: find longest path
        req_map = {req.get("id", f"req_{i}"): req for i, req in enumerate(requirements)}

        def get_weight(req_id: str) -> int:
            req = req_map.get(req_id, {})
            complexity = {"low": 1, "medium": 2, "high": 3}
            return complexity.get(req.get("complexity", "medium"), 2)

        # Find longest path using DFS
        def dfs(node: str, visited: Set[str]) -> Tuple[int, List[str]]:
            if node in visited:
                return 0, []

            visited.add(node)
            max_dist = 0
            max_path = [node]

            for neighbor in graph.get(node, set()):
                dist, path = dfs(neighbor, visited.copy())
                dist += get_weight(node)

                if dist > max_dist:
                    max_dist = dist
                    max_path = [node] + path

            return max_dist, max_path

        # Find path from each starting node
        max_length = 0
        critical_path = []

        for node in graph:
            if not any(node in graph[other] for other in graph):
                # Starting node (no incoming edges)
                length, path = dfs(node, set())
                if length > max_length:
                    max_length = length
                    critical_path = path

        return critical_path

    def _cluster_requirements(
        self, dependencies: List[Dict], requirements: List[Dict]
    ) -> List[List[str]]:
        """Cluster related requirements"""
        clusters = []
        visited = set()

        # Build undirected graph for clustering
        connections = defaultdict(set)
        for dep in dependencies:
            if dep.get("strength") != "weak":
                connections[dep["from"]].add(dep["to"])
                connections[dep["to"]].add(dep["from"])

        # Find connected components
        def dfs(node: str, cluster: List[str]):
            visited.add(node)
            cluster.append(node)

            for neighbor in connections[node]:
                if neighbor not in visited:
                    dfs(neighbor, cluster)

        for req in requirements:
            req_id = req.get("id", f"req_{requirements.index(req)}")
            if req_id not in visited:
                cluster = []
                dfs(req_id, cluster)
                if len(cluster) > 1:
                    clusters.append(cluster)

        return clusters

    def _analyze_impact(
        self, graph: Dict[str, Set[str]], requirements: List[Dict]
    ) -> Dict[str, Dict]:
        """Analyze impact of each requirement"""
        impact = {}

        for req in requirements:
            req_id = req.get("id", f"req_{requirements.index(req)}")

            # Count direct and indirect dependencies
            direct = len(graph.get(req_id, set()))
            indirect = self._count_indirect_dependencies(req_id, graph)

            # Calculate impact score
            impact[req_id] = {
                "direct_dependencies": direct,
                "indirect_dependencies": indirect,
                "total_impact": direct + indirect,
                "criticality": "high" if indirect > 5 else "medium" if indirect > 2 else "low",
            }

        return impact

    def _count_indirect_dependencies(self, node: str, graph: Dict[str, Set[str]]) -> int:
        """Count indirect dependencies of a node"""
        visited = set()

        def dfs(current: str):
            visited.add(current)
            for neighbor in graph.get(current, set()):
                if neighbor not in visited:
                    dfs(neighbor)

        dfs(node)
        return len(visited) - 1  # Exclude the node itself

    def _graph_to_dict(self, graph: Dict[str, Set[str]]) -> Dict[str, List[str]]:
        """Convert graph sets to lists for JSON serialization"""
        return {node: list(neighbors) for node, neighbors in graph.items()}

    def _calculate_statistics(
        self, dependencies: List[Dict], graph: Dict[str, Set[str]]
    ) -> Dict[str, Any]:
        """Calculate dependency statistics"""
        return {
            "total_dependencies": len(dependencies),
            "total_nodes": len(graph),
            "strong_dependencies": sum(1 for d in dependencies if d.get("strength") == "strong"),
            "weak_dependencies": sum(1 for d in dependencies if d.get("strength") == "weak"),
            "average_dependencies": sum(len(neighbors) for neighbors in graph.values()) / len(graph)
            if graph
            else 0,
            "max_dependencies": max(len(neighbors) for neighbors in graph.values()) if graph else 0,
        }
