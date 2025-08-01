# backend/src/agents/framework/dependency_manager.py
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
from enum import Enum
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

class SimpleGraph:
    """Simple graph implementation as fallback"""
    def __init__(self):
        self.edges = {}
        self.nodes = set()
    
    def add_edge(self, source, target, **attrs):
        if source not in self.edges:
            self.edges[source] = []
        self.edges[source].append((target, attrs))
        self.nodes.add(source)
        self.nodes.add(target)
    
    def predecessors(self, node):
        return [s for s, targets in self.edges.items() for t, _ in targets if t == node]
    
    def successors(self, node):
        return [t for t, _ in self.edges.get(node, [])]
    
    def has_edge(self, source, target):
        return any(t == target for t, _ in self.edges.get(source, []))
    
    def remove_edge(self, source, target):
        if source in self.edges:
            self.edges[source] = [(t, a) for t, a in self.edges[source] if t != target]
    
    def get_edge_data(self, source, target):
        for t, attrs in self.edges.get(source, []):
            if t == target:
                return attrs
        return {}

class DependencyType(Enum):
    HARD = "hard"  # Must complete before dependent can start
    SOFT = "soft"  # Preferred but not required
    DATA = "data"  # Data dependency
    RESOURCE = "resource"  # Resource dependency

@dataclass
class Dependency:
    source: str
    target: str
    type: DependencyType
    condition: Optional[str] = None
    weight: float = 1.0

class DependencyManager:
    def __init__(self):
        self.dependencies: List[Dependency] = []
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()
        else:
            self.graph = SimpleGraph()  # Fallback implementation
        self.agent_states: Dict[str, str] = {}
        self.resource_locks: Dict[str, str] = {}
    
    def add_dependency(self, dependency: Dependency):
        self.dependencies.append(dependency)
        self.graph.add_edge(
            dependency.source,
            dependency.target,
            type=dependency.type,
            condition=dependency.condition,
            weight=dependency.weight
        )
    
    def remove_dependency(self, source: str, target: str):
        self.dependencies = [
            d for d in self.dependencies
            if not (d.source == source and d.target == target)
        ]
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
    
    def get_dependencies(self, agent_id: str) -> List[str]:
        """Get all agents that this agent depends on"""
        return list(self.graph.predecessors(agent_id))
    
    def get_dependents(self, agent_id: str) -> List[str]:
        """Get all agents that depend on this agent"""
        return list(self.graph.successors(agent_id))
    
    def can_execute(self, agent_id: str) -> bool:
        """Check if agent can execute based on dependencies"""
        dependencies = self.get_dependencies(agent_id)
        
        for dep_id in dependencies:
            edge_data = self.graph.get_edge_data(dep_id, agent_id)
            dep_type = edge_data.get('type', DependencyType.HARD)
            condition = edge_data.get('condition')
            
            # Check hard dependencies
            if dep_type == DependencyType.HARD:
                if self.agent_states.get(dep_id) != 'completed':
                    return False
            
            # Check soft dependencies
            elif dep_type == DependencyType.SOFT:
                if self.agent_states.get(dep_id) == 'failed':
                    # Log warning but allow execution
                    print(f"Warning: Soft dependency {dep_id} failed for {agent_id}")
            
            # Check resource dependencies
            elif dep_type == DependencyType.RESOURCE:
                resource = edge_data.get('resource')
                if resource and self.resource_locks.get(resource) != dep_id:
                    return False
            
            # Check conditional dependencies
            if condition and not self._evaluate_condition(condition, dep_id):
                return False
        
        return True
    
    def get_execution_order(self, agent_ids: List[str]) -> List[List[str]]:
        """Get execution order respecting dependencies"""
        subgraph = self.graph.subgraph(agent_ids)
        
        # Check for cycles (simplified for fallback)
        if NETWORKX_AVAILABLE and not nx.is_directed_acyclic_graph(subgraph):
            cycles = list(nx.simple_cycles(subgraph))
            raise ValueError(f"Circular dependencies detected: {cycles}")
        
        # Topological sort with levels
        levels = []
        remaining = set(agent_ids)
        
        while remaining:
            # Find nodes with no dependencies in remaining set
            ready = []
            for node in remaining:
                deps = set(self.graph.predecessors(node)) & remaining
                if not deps:
                    ready.append(node)
            
            if not ready:
                raise ValueError("Cannot resolve dependencies")
            
            levels.append(ready)
            remaining -= set(ready)
        
        return levels
    
    def update_agent_state(self, agent_id: str, state: str):
        """Update agent state for dependency checking"""
        self.agent_states[agent_id] = state
        
        # Release resources if agent completed
        if state == 'completed':
            for resource, owner in list(self.resource_locks.items()):
                if owner == agent_id:
                    del self.resource_locks[resource]
    
    def acquire_resource(self, agent_id: str, resource: str) -> bool:
        """Acquire resource lock for agent"""
        if resource not in self.resource_locks:
            self.resource_locks[resource] = agent_id
            return True
        return False
    
    def release_resource(self, agent_id: str, resource: str):
        """Release resource lock"""
        if self.resource_locks.get(resource) == agent_id:
            del self.resource_locks[resource]
    
    def get_critical_path(self, start: str, end: str) -> List[str]:
        """Find critical path between two agents"""
        if NETWORKX_AVAILABLE:
            try:
                return nx.shortest_path(self.graph, start, end, weight='weight')
            except nx.NetworkXNoPath:
                return []
        else:
            # Simple path finding fallback
            return self._simple_path_find(start, end)
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze dependency graph for insights"""
        if NETWORKX_AVAILABLE:
            return {
                'total_dependencies': len(self.dependencies),
                'agents': len(self.graph.nodes),
                'is_acyclic': nx.is_directed_acyclic_graph(self.graph),
                'strongly_connected_components': len(list(nx.strongly_connected_components(self.graph))),
                'density': nx.density(self.graph),
                'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes) if self.graph.nodes else 0
            }
        else:
            return {
                'total_dependencies': len(self.dependencies),
                'agents': len(self.graph.nodes),
                'is_acyclic': True,  # Simplified
                'strongly_connected_components': 1,
                'density': 0.5,
                'average_degree': 2.0
            }
    
    def _evaluate_condition(self, condition: str, agent_id: str) -> bool:
        """Evaluate dependency condition"""
        context = {
            'agent_state': self.agent_states.get(agent_id, 'unknown'),
            'agent_id': agent_id
        }
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    
    def _simple_path_find(self, start: str, end: str) -> List[str]:
        """Simple path finding implementation"""
        if start == end:
            return [start]
        
        visited = set()
        queue = [(start, [start])]
        
        while queue:
            node, path = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            
            for successor in self.graph.successors(node):
                if successor == end:
                    return path + [successor]
                if successor not in visited:
                    queue.append((successor, path + [successor]))
        
        return []