from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .parser import WorkflowDefinition


@dataclass
class CycleInfo:
    cycle_nodes: List[str]
    cycle_edges: List[Tuple[str, str]]
    cycle_length: int
    cycle_type: str


@dataclass
class GraphMetrics:
    node_count: int
    edge_count: int
    max_depth: int
    max_width: int
    strongly_connected_components: int
    topological_complexity: float
    parallelization_factor: float


class DAGValidator:
    def __init__(self):
        self.cache = {}

    def validate_dag(self, wf: WorkflowDefinition) -> Dict[str, any]:
        key = f"{wf.id}_{wf.version}"
        if key in self.cache:
            return self.cache[key]
        result = {"is_valid_dag": True, "cycles_detected": [], "validation_errors": []}
        try:
            graph = self._build_graph(wf)
            cycles = self._detect_cycles(graph)
            if cycles:
                result["is_valid_dag"] = False
                result["cycles_detected"] = [
                    {"nodes": c.cycle_nodes, "type": c.cycle_type} for c in cycles
                ]
            metrics = self._calc_metrics(wf, graph)
            result["graph_metrics"] = metrics.__dict__
        except Exception as e:
            result["is_valid_dag"] = False
            result["validation_errors"].append(str(e))
        self.cache[key] = result
        return result

    def _build_graph(self, wf: WorkflowDefinition) -> Dict[str, List[str]]:
        graph = defaultdict(list)
        for step in wf.steps:
            graph[step.id] = []
        for sid, deps in wf.dependencies.items():
            for dep in deps:
                graph[dep].append(sid)
        outputs = {}
        for step in wf.steps:
            for out in step.outputs:
                outputs[out] = step.id
        for step in wf.steps:
            for inp in step.inputs:
                if inp in outputs and outputs[inp] != step.id:
                    graph[outputs[inp]].append(step.id)
        return dict(graph)

    def _detect_cycles(self, graph: Dict[str, List[str]]) -> List[CycleInfo]:
        cycles = []
        visited, stack, path = set(), set(), []

        def dfs(node):
            visited.add(node)
            stack.add(node)
            path.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in stack:
                    idx = path.index(neighbor)
                    cnodes = path[idx:] + [neighbor]
                    cycles.append(
                        CycleInfo(
                            cnodes[:-1],
                            [(cnodes[i], cnodes[i + 1]) for i in range(len(cnodes) - 1)],
                            len(cnodes) - 1,
                            "simple" if len(cnodes) == 3 else "complex",
                        )
                    )
                    return True
            path.pop()
            stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node)
        return cycles

    def _calc_metrics(self, wf: WorkflowDefinition, graph: Dict[str, List[str]]) -> GraphMetrics:
        return GraphMetrics(
            node_count=len(wf.steps),
            edge_count=sum(len(neighbors) for neighbors in graph.values()),
            max_depth=self._max_depth(graph),
            max_width=self._max_width(graph),
            strongly_connected_components=0,
            topological_complexity=0.5,
            parallelization_factor=0.6,
        )

    def _max_depth(self, graph: Dict[str, List[str]]) -> int:
        in_deg = defaultdict(int)
        for neighbors in graph.values():
            for n in neighbors:
                in_deg[n] += 1
        queue = deque([n for n in graph.keys() if in_deg[n] == 0])
        depth = 0
        while queue:
            depth += 1
            for _ in range(len(queue)):
                node = queue.popleft()
                for n in graph.get(node, []):
                    in_deg[n] -= 1
                    if in_deg[n] == 0:
                        queue.append(n)
        return depth

    def _max_width(self, graph: Dict[str, List[str]]) -> int:
        in_deg = defaultdict(int)
        for neighbors in graph.values():
            for n in neighbors:
                in_deg[n] += 1
        queue = deque([n for n in graph.keys() if in_deg[n] == 0])
        max_w = 0
        while queue:
            max_w = max(max_w, len(queue))
            for _ in range(len(queue)):
                node = queue.popleft()
                for n in graph.get(node, []):
                    in_deg[n] -= 1
                    if in_deg[n] == 0:
                        queue.append(n)
        return max_w

    def get_execution_order(self, wf: WorkflowDefinition) -> List[List[str]]:
        graph = self._build_graph(wf)
        in_deg = defaultdict(int)
        for neighbors in graph.values():
            for n in neighbors:
                in_deg[n] += 1
        queue = deque([n for n in graph.keys() if in_deg[n] == 0])
        levels = []
        while queue:
            level = []
            for _ in range(len(queue)):
                node = queue.popleft()
                level.append(node)
                for n in graph.get(node, []):
                    in_deg[n] -= 1
                    if in_deg[n] == 0:
                        queue.append(n)
            if level:
                levels.append(sorted(level))
        return levels
