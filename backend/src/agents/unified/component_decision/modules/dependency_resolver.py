"""
Dependency Resolver Module
Resolves dependencies between components
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import networkx as nx


class DependencyType(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    PEER = "peer"
    DEVELOPMENT = "development"


class DependencyResolver:
    """Resolves component dependencies"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.known_dependencies = self._build_known_dependencies()
        
    async def resolve(self, specifications: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Resolve dependencies for specifications"""
        
        # Build dependency graph
        self._build_dependency_graph(specifications)
        
        # Detect circular dependencies
        circular = self._detect_circular_dependencies()
        
        # Perform topological sort
        if not circular:
            resolved_order = self._topological_sort()
        else:
            resolved_order = self._handle_circular_dependencies(circular)
        
        # Generate dependency tree
        dependency_tree = self._generate_dependency_tree(resolved_order)
        
        # Calculate versions
        versions = self._resolve_versions(dependency_tree)
        
        # Generate lock file
        lock_file = self._generate_lock_file(dependency_tree, versions)
        
        return {
            'resolved_order': resolved_order,
            'dependency_tree': dependency_tree,
            'versions': versions,
            'lock_file': lock_file,
            'circular_dependencies': circular,
            'statistics': self._calculate_statistics()
        }
    
    def _build_dependency_graph(self, specifications: Dict):
        """Build dependency graph from specifications"""
        
        components = specifications.get('components', [])
        
        for component in components:
            comp_name = component.get('name')
            self.dependency_graph.add_node(comp_name, **component)
            
            # Add dependencies
            for dep in component.get('dependencies', []):
                self.dependency_graph.add_edge(comp_name, dep['name'], 
                                              type=dep.get('type', 'required'))
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies"""
        
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []
    
    def _topological_sort(self) -> List[str]:
        """Perform topological sort on dependency graph"""
        
        try:
            return list(nx.topological_sort(self.dependency_graph))
        except nx.NetworkXError:
            # Fall back to DFS if cyclic
            return list(nx.dfs_preorder_nodes(self.dependency_graph))
    
    def _handle_circular_dependencies(self, circular: List[List[str]]) -> List[str]:
        """Handle circular dependencies"""
        
        # Break cycles by removing weakest links
        for cycle in circular:
            if len(cycle) > 1:
                # Find optional dependency to break
                for i in range(len(cycle)):
                    edge = (cycle[i], cycle[(i+1) % len(cycle)])
                    edge_data = self.dependency_graph.get_edge_data(*edge)
                    if edge_data and edge_data.get('type') == 'optional':
                        self.dependency_graph.remove_edge(*edge)
                        break
        
        # Retry topological sort
        return self._topological_sort()
    
    def _generate_dependency_tree(self, resolved_order: List[str]) -> Dict:
        """Generate dependency tree"""
        
        tree = {}
        
        for node in resolved_order:
            dependencies = list(self.dependency_graph.predecessors(node))
            tree[node] = {
                'direct': dependencies,
                'transitive': self._get_transitive_dependencies(node),
                'level': self._calculate_dependency_level(node)
            }
        
        return tree
    
    def _get_transitive_dependencies(self, node: str) -> List[str]:
        """Get all transitive dependencies"""
        
        visited = set()
        to_visit = [node]
        
        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                predecessors = list(self.dependency_graph.predecessors(current))
                to_visit.extend(predecessors)
        
        visited.discard(node)
        return list(visited)
    
    def _calculate_dependency_level(self, node: str) -> int:
        """Calculate dependency level (depth in tree)"""
        
        if not list(self.dependency_graph.predecessors(node)):
            return 0
        
        max_level = 0
        for predecessor in self.dependency_graph.predecessors(node):
            level = self._calculate_dependency_level(predecessor)
            max_level = max(max_level, level)
        
        return max_level + 1
    
    def _resolve_versions(self, dependency_tree: Dict) -> Dict[str, str]:
        """Resolve component versions"""
        
        versions = {}
        
        for component in dependency_tree:
            node_data = self.dependency_graph.nodes.get(component, {})
            version = node_data.get('version', '1.0.0')
            
            # Check for version conflicts
            required_versions = self._get_required_versions(component)
            if required_versions:
                version = self._resolve_version_conflict(required_versions)
            
            versions[component] = version
        
        return versions
    
    def _get_required_versions(self, component: str) -> List[str]:
        """Get required versions from dependents"""
        
        versions = []
        for successor in self.dependency_graph.successors(component):
            edge_data = self.dependency_graph.get_edge_data(successor, component)
            if edge_data and 'version' in edge_data:
                versions.append(edge_data['version'])
        
        return versions
    
    def _resolve_version_conflict(self, versions: List[str]) -> str:
        """Resolve version conflicts using semver"""
        
        # Simple implementation - take the highest version
        return max(versions)
    
    def _generate_lock_file(self, tree: Dict, versions: Dict) -> Dict:
        """Generate dependency lock file"""
        
        return {
            'components': {
                name: {
                    'version': versions.get(name, '1.0.0'),
                    'dependencies': deps['direct'],
                    'resolved': deps['transitive']
                }
                for name, deps in tree.items()
            },
            'metadata': {
                'generated': 'auto',
                'resolver_version': '1.0.0'
            }
        }
    
    def _calculate_statistics(self) -> Dict:
        """Calculate dependency statistics"""
        
        return {
            'total_components': self.dependency_graph.number_of_nodes(),
            'total_dependencies': self.dependency_graph.number_of_edges(),
            'max_depth': max(
                (self._calculate_dependency_level(n) 
                 for n in self.dependency_graph.nodes()),
                default=0
            ),
            'average_dependencies': (
                self.dependency_graph.number_of_edges() / 
                max(self.dependency_graph.number_of_nodes(), 1)
            )
        }
    
    def _build_known_dependencies(self) -> Dict:
        """Build known dependency mappings"""
        
        return {
            'React': ['react-dom', 'webpack', 'babel'],
            'Express': ['body-parser', 'cors', 'helmet'],
            'PostgreSQL': ['pg', 'sequelize'],
            'Redis': ['redis', 'ioredis']
        }
