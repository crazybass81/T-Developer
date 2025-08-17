"""
Knowledge Graph System for T-Developer

This module implements a graph-based knowledge representation system
for T-Developer learning, enabling complex relationship queries and
knowledge discovery through graph algorithms.

The KnowledgeGraph builds relationships between learned concepts,
patterns, failures, and metrics to enable intelligent reasoning
and recommendation generation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import aiosqlite
import networkx as nx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: int = 30
MAX_GRAPH_SIZE: int = 10000
MIN_RELATIONSHIP_STRENGTH: float = 0.3


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""

    PATTERN = "pattern"
    FAILURE = "failure"
    MEMORY = "memory"
    METRIC = "metric"
    CONCEPT = "concept"
    AGENT = "agent"
    TASK = "task"
    CONTEXT = "context"


class RelationshipType(Enum):
    """Types of relationships between nodes."""

    CAUSES = "causes"
    PREVENTS = "prevents"
    IMPROVES = "improves"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    LEADS_TO = "leads_to"
    CONFLICTS_WITH = "conflicts_with"
    ENHANCES = "enhances"
    DERIVED_FROM = "derived_from"


@dataclass
class KnowledgeNode:
    """Node in the knowledge graph.

    Attributes:
        id: Unique node identifier
        type: Type of node
        label: Human-readable label
        properties: Node properties
        created_at: When node was created
        last_updated: When node was last updated
        importance: Importance score (0-1)
        tags: Tags for categorization
    """

    id: str
    type: NodeType
    label: str
    properties: dict[str, Any]
    created_at: datetime
    last_updated: datetime
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "importance": self.importance,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeNode:
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            type=NodeType(data["type"]),
            label=data["label"],
            properties=data["properties"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            importance=data.get("importance", 0.5),
            tags=data.get("tags", []),
        )


@dataclass
class KnowledgeRelationship:
    """Relationship between nodes in the knowledge graph.

    Attributes:
        id: Unique relationship identifier
        source_id: Source node ID
        target_id: Target node ID
        type: Type of relationship
        strength: Relationship strength (0-1)
        properties: Relationship properties
        created_at: When relationship was created
        confidence: Confidence in relationship (0-1)
    """

    id: str
    source_id: str
    target_id: str
    type: RelationshipType
    strength: float
    properties: dict[str, Any]
    created_at: datetime
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        """Convert relationship to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "strength": self.strength,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeRelationship:
        """Create relationship from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=RelationshipType(data["type"]),
            strength=data["strength"],
            properties=data["properties"],
            created_at=datetime.fromisoformat(data["created_at"]),
            confidence=data.get("confidence", 0.8),
        )


class GraphStorage:
    """Storage backend for knowledge graph using SQLite."""

    def __init__(self, db_path: str = "knowledge_graph.db"):
        """Initialize graph storage.

        Args:
            db_path: Database file path
        """
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self) -> None:
        """Initialize storage and create tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Create nodes table
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    tags TEXT NOT NULL DEFAULT '[]'
                )
            """
            )

            # Create relationships table
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    strength REAL NOT NULL,
                    properties TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.8,
                    FOREIGN KEY (source_id) REFERENCES nodes (id),
                    FOREIGN KEY (target_id) REFERENCES nodes (id)
                )
            """
            )

            # Create indexes
            await db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes (type)")
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_nodes_importance ON nodes (importance)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships (target_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (type)"
            )

            await db.commit()

        self.logger.info(f"Graph storage initialized at {self.db_path}")

    async def store_node(self, node: KnowledgeNode) -> None:
        """Store a node in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO nodes
                (id, type, label, properties, created_at, last_updated, importance, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    node.id,
                    node.type.value,
                    node.label,
                    json.dumps(node.properties),
                    node.created_at.isoformat(),
                    node.last_updated.isoformat(),
                    node.importance,
                    json.dumps(node.tags),
                ),
            )
            await db.commit()

    async def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)) as cursor:
                row = await cursor.fetchone()

            if row:
                return self._row_to_node(row)
            return None

    async def store_relationship(self, relationship: KnowledgeRelationship) -> None:
        """Store a relationship in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO relationships
                (id, source_id, target_id, type, strength, properties, created_at, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    relationship.id,
                    relationship.source_id,
                    relationship.target_id,
                    relationship.type.value,
                    relationship.strength,
                    json.dumps(relationship.properties),
                    relationship.created_at.isoformat(),
                    relationship.confidence,
                ),
            )
            await db.commit()

    async def get_node_relationships(
        self, node_id: str, relationship_type: Optional[RelationshipType] = None
    ) -> list[KnowledgeRelationship]:
        """Get all relationships for a node."""
        query = """
            SELECT * FROM relationships
            WHERE source_id = ? OR target_id = ?
        """
        params = [node_id, node_id]

        if relationship_type:
            query += " AND type = ?"
            params.append(relationship_type.value)

        relationships = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    relationships.append(self._row_to_relationship(row))

        return relationships

    async def search_nodes(self, criteria: dict[str, Any], limit: int = 100) -> list[KnowledgeNode]:
        """Search nodes by criteria."""
        where_clauses = []
        params = []

        if "type" in criteria:
            where_clauses.append("type = ?")
            params.append(criteria["type"])

        if "min_importance" in criteria:
            where_clauses.append("importance >= ?")
            params.append(criteria["min_importance"])

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"""
            SELECT * FROM nodes
            WHERE {where_clause}
            ORDER BY importance DESC
            LIMIT ?
        """
        params.append(limit)

        nodes = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    nodes.append(self._row_to_node(row))

        return nodes

    async def get_all_nodes(self) -> list[KnowledgeNode]:
        """Get all nodes in the graph."""
        nodes = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM nodes") as cursor:
                async for row in cursor:
                    nodes.append(self._row_to_node(row))
        return nodes

    async def get_all_relationships(self) -> list[KnowledgeRelationship]:
        """Get all relationships in the graph."""
        relationships = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM relationships") as cursor:
                async for row in cursor:
                    relationships.append(self._row_to_relationship(row))
        return relationships

    async def delete_node(self, node_id: str) -> bool:
        """Delete a node and its relationships."""
        async with aiosqlite.connect(self.db_path) as db:
            # Delete relationships first
            await db.execute(
                "DELETE FROM relationships WHERE source_id = ? OR target_id = ?", (node_id, node_id)
            )

            # Delete node
            cursor = await db.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
            await db.commit()

            return cursor.rowcount > 0

    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM relationships WHERE id = ?", (relationship_id,))
            await db.commit()

            return cursor.rowcount > 0

    def _row_to_node(self, row: tuple) -> KnowledgeNode:
        """Convert database row to KnowledgeNode."""
        return KnowledgeNode(
            id=row[0],
            type=NodeType(row[1]),
            label=row[2],
            properties=json.loads(row[3]),
            created_at=datetime.fromisoformat(row[4]),
            last_updated=datetime.fromisoformat(row[5]),
            importance=row[6],
            tags=json.loads(row[7]),
        )

    def _row_to_relationship(self, row: tuple) -> KnowledgeRelationship:
        """Convert database row to KnowledgeRelationship."""
        return KnowledgeRelationship(
            id=row[0],
            source_id=row[1],
            target_id=row[2],
            type=RelationshipType(row[3]),
            strength=row[4],
            properties=json.loads(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            confidence=row[7],
        )


class GraphAnalyzer:
    """Analyzer for discovering patterns and insights in the knowledge graph."""

    def __init__(self):
        """Initialize graph analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    async def find_shortest_path(
        self, graph: nx.DiGraph, source_id: str, target_id: str
    ) -> Optional[list[str]]:
        """Find shortest path between two nodes."""
        try:
            if source_id not in graph or target_id not in graph:
                return None

            path = nx.shortest_path(graph, source_id, target_id)
            return path

        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            self.logger.error(f"Error finding shortest path: {e}")
            return None

    async def find_strongly_connected_components(self, graph: nx.DiGraph) -> list[set[str]]:
        """Find strongly connected components in the graph."""
        try:
            components = list(nx.strongly_connected_components(graph))
            # Filter out single-node components
            return [comp for comp in components if len(comp) > 1]

        except Exception as e:
            self.logger.error(f"Error finding connected components: {e}")
            return []

    async def calculate_centrality_measures(self, graph: nx.DiGraph) -> dict[str, dict[str, float]]:
        """Calculate various centrality measures for nodes."""
        try:
            centrality_measures = {}

            # Degree centrality
            centrality_measures["degree"] = nx.degree_centrality(graph)

            # Betweenness centrality
            centrality_measures["betweenness"] = nx.betweenness_centrality(graph)

            # Closeness centrality
            centrality_measures["closeness"] = nx.closeness_centrality(graph)

            # PageRank
            centrality_measures["pagerank"] = nx.pagerank(graph)

            return centrality_measures

        except Exception as e:
            self.logger.error(f"Error calculating centrality measures: {e}")
            return {}

    async def detect_communities(self, graph: nx.Graph) -> list[set[str]]:
        """Detect communities in the graph using modularity."""
        try:
            # Convert to undirected graph for community detection
            undirected_graph = graph.to_undirected()

            # Use greedy modularity maximization
            communities = nx.community.greedy_modularity_communities(undirected_graph)
            return list(communities)

        except Exception as e:
            self.logger.error(f"Error detecting communities: {e}")
            return []

    async def find_influential_nodes(
        self, graph: nx.DiGraph, top_k: int = 10
    ) -> list[tuple[str, float]]:
        """Find most influential nodes based on multiple centrality measures."""
        try:
            centrality_measures = await self.calculate_centrality_measures(graph)

            if not centrality_measures:
                return []

            # Combine centrality scores
            combined_scores = defaultdict(float)

            for measure_name, scores in centrality_measures.items():
                weight = {
                    "degree": 0.25,
                    "betweenness": 0.3,
                    "closeness": 0.2,
                    "pagerank": 0.25,
                }.get(measure_name, 0.25)

                for node_id, score in scores.items():
                    combined_scores[node_id] += score * weight

            # Sort by combined score
            influential_nodes = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

            return influential_nodes[:top_k]

        except Exception as e:
            self.logger.error(f"Error finding influential nodes: {e}")
            return []

    async def recommend_relationships(
        self, graph: nx.DiGraph, node_id: str, max_recommendations: int = 5
    ) -> list[tuple[str, float]]:
        """Recommend potential relationships for a node."""
        try:
            if node_id not in graph:
                return []

            recommendations = []

            # Get neighbors of neighbors (2-hop relationships)
            neighbors = set(graph.neighbors(node_id))
            neighbors_of_neighbors = set()

            for neighbor in neighbors:
                neighbors_of_neighbors.update(graph.neighbors(neighbor))

            # Remove direct neighbors and the node itself
            candidates = neighbors_of_neighbors - neighbors - {node_id}

            # Calculate recommendation scores based on common neighbors
            for candidate in candidates:
                common_neighbors = len(neighbors.intersection(set(graph.neighbors(candidate))))
                score = common_neighbors / max(len(neighbors), 1)
                recommendations.append((candidate, score))

            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:max_recommendations]

        except Exception as e:
            self.logger.error(f"Error recommending relationships: {e}")
            return []

    async def analyze_relationship_patterns(
        self, relationships: list[KnowledgeRelationship]
    ) -> dict[str, Any]:
        """Analyze patterns in relationships."""
        try:
            patterns = {
                "type_distribution": defaultdict(int),
                "strength_distribution": {"strong": 0, "medium": 0, "weak": 0},
                "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
                "temporal_patterns": defaultdict(int),
            }

            for rel in relationships:
                # Type distribution
                patterns["type_distribution"][rel.type.value] += 1

                # Strength distribution
                if rel.strength >= 0.7:
                    patterns["strength_distribution"]["strong"] += 1
                elif rel.strength >= 0.4:
                    patterns["strength_distribution"]["medium"] += 1
                else:
                    patterns["strength_distribution"]["weak"] += 1

                # Confidence distribution
                if rel.confidence >= 0.8:
                    patterns["confidence_distribution"]["high"] += 1
                elif rel.confidence >= 0.5:
                    patterns["confidence_distribution"]["medium"] += 1
                else:
                    patterns["confidence_distribution"]["low"] += 1

                # Temporal patterns (by month)
                month_key = rel.created_at.strftime("%Y-%m")
                patterns["temporal_patterns"][month_key] += 1

            return dict(patterns)

        except Exception as e:
            self.logger.error(f"Error analyzing relationship patterns: {e}")
            return {}


class KnowledgeGraph:
    """Main knowledge graph system.

    Provides graph-based knowledge representation with complex queries,
    relationship discovery, and intelligent reasoning capabilities.

    Example:
        >>> graph = KnowledgeGraph()
        >>> await graph.initialize()
        >>> node = KnowledgeNode(...)
        >>> await graph.add_node(node)
        >>> related = await graph.find_related_nodes(node.id)
    """

    def __init__(self, storage: Optional[GraphStorage] = None):
        """Initialize knowledge graph.

        Args:
            storage: Storage backend (creates SQLite if None)
        """
        self.storage = storage or GraphStorage()
        self.analyzer = GraphAnalyzer()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._graph_cache: Optional[nx.DiGraph] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=10)

    async def initialize(self) -> None:
        """Initialize the knowledge graph."""
        await self.storage.initialize()
        self.logger.info("Knowledge graph initialized")

    async def add_node(self, node: KnowledgeNode) -> None:
        """Add a node to the knowledge graph.

        Args:
            node: Node to add

        Raises:
            ValueError: If node is invalid
            RuntimeError: If storage fails
        """
        if not node.id or not node.label:
            raise ValueError("Node must have id and label")

        try:
            await self.storage.store_node(node)
            self._invalidate_cache()
            self.logger.debug(f"Added node: {node.id}")

        except Exception as e:
            self.logger.error(f"Failed to add node {node.id}: {e}")
            raise RuntimeError(f"Node addition failed: {e}")

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float = 0.5,
        properties: Optional[dict[str, Any]] = None,
        confidence: float = 0.8,
    ) -> KnowledgeRelationship:
        """Add a relationship between nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Type of relationship
            strength: Relationship strength (0-1)
            properties: Additional properties
            confidence: Confidence in relationship (0-1)

        Returns:
            Created relationship

        Raises:
            ValueError: If nodes don't exist or parameters are invalid
            RuntimeError: If storage fails
        """
        # Validate nodes exist
        source_node = await self.storage.get_node(source_id)
        target_node = await self.storage.get_node(target_id)

        if not source_node:
            raise ValueError(f"Source node {source_id} not found")
        if not target_node:
            raise ValueError(f"Target node {target_id} not found")

        if not 0 <= strength <= 1:
            raise ValueError("Strength must be between 0 and 1")
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

        # Create relationship
        relationship_id = f"rel_{hashlib.md5(f'{source_id}_{target_id}_{relationship_type.value}'.encode()).hexdigest()[:8]}"

        relationship = KnowledgeRelationship(
            id=relationship_id,
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            strength=strength,
            properties=properties or {},
            created_at=datetime.now(),
            confidence=confidence,
        )

        try:
            await self.storage.store_relationship(relationship)
            self._invalidate_cache()
            self.logger.debug(f"Added relationship: {relationship_id}")
            return relationship

        except Exception as e:
            self.logger.error(f"Failed to add relationship {relationship_id}: {e}")
            raise RuntimeError(f"Relationship addition failed: {e}")

    async def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID.

        Args:
            node_id: Node identifier

        Returns:
            Node if found, None otherwise
        """
        return await self.storage.get_node(node_id)

    async def find_related_nodes(
        self,
        node_id: str,
        relationship_types: Optional[list[RelationshipType]] = None,
        max_depth: int = 2,
        min_strength: float = MIN_RELATIONSHIP_STRENGTH,
    ) -> list[tuple[KnowledgeNode, float, int]]:
        """Find nodes related to a given node.

        Args:
            node_id: Source node ID
            relationship_types: Types of relationships to follow
            max_depth: Maximum traversal depth
            min_strength: Minimum relationship strength

        Returns:
            List of (node, combined_strength, depth) tuples
        """
        try:
            related_nodes = []
            visited = set()
            queue = deque([(node_id, 1.0, 0)])  # (node_id, strength, depth)

            while queue:
                current_id, current_strength, depth = queue.popleft()

                if current_id in visited or depth > max_depth:
                    continue

                visited.add(current_id)

                # Get relationships for current node
                relationships = await self.storage.get_node_relationships(current_id)

                for rel in relationships:
                    # Skip weak relationships
                    if rel.strength < min_strength:
                        continue

                    # Skip unwanted relationship types
                    if relationship_types and rel.type not in relationship_types:
                        continue

                    # Determine target node
                    target_id = rel.target_id if rel.source_id == current_id else rel.source_id

                    if target_id == node_id:  # Don't include source node
                        continue

                    # Calculate combined strength
                    combined_strength = current_strength * rel.strength

                    # Add to queue for further exploration
                    if depth < max_depth:
                        queue.append((target_id, combined_strength, depth + 1))

                    # Add to results if not source node
                    if depth > 0:
                        target_node = await self.storage.get_node(target_id)
                        if target_node:
                            related_nodes.append((target_node, combined_strength, depth))

            # Remove duplicates and sort by strength
            unique_nodes = {}
            for node, strength, depth in related_nodes:
                if node.id not in unique_nodes or strength > unique_nodes[node.id][1]:
                    unique_nodes[node.id] = (node, strength, depth)

            result = list(unique_nodes.values())
            result.sort(key=lambda x: x[1], reverse=True)  # Sort by strength

            return result

        except Exception as e:
            self.logger.error(f"Failed to find related nodes for {node_id}: {e}")
            return []

    async def query_graph(self, query: dict[str, Any]) -> list[KnowledgeNode]:
        """Query the knowledge graph with complex criteria.

        Args:
            query: Query specification

        Returns:
            List of matching nodes
        """
        try:
            # Basic node search
            if "node_criteria" in query:
                nodes = await self.storage.search_nodes(
                    query["node_criteria"], query.get("limit", 100)
                )
            else:
                nodes = await self.storage.get_all_nodes()

            # Apply relationship filters
            if "relationship_filters" in query:
                nodes = await self._filter_by_relationships(nodes, query["relationship_filters"])

            # Apply graph structure filters
            if "structure_filters" in query:
                nodes = await self._filter_by_structure(nodes, query["structure_filters"])

            return nodes

        except Exception as e:
            self.logger.error(f"Failed to query graph: {e}")
            return []

    async def _filter_by_relationships(
        self, nodes: list[KnowledgeNode], filters: dict[str, Any]
    ) -> list[KnowledgeNode]:
        """Filter nodes based on relationship criteria."""
        filtered_nodes = []

        for node in nodes:
            relationships = await self.storage.get_node_relationships(node.id)

            # Check relationship count
            if "min_relationships" in filters:
                if len(relationships) < filters["min_relationships"]:
                    continue

            # Check specific relationship types
            if "has_relationship_type" in filters:
                required_type = RelationshipType(filters["has_relationship_type"])
                if not any(rel.type == required_type for rel in relationships):
                    continue

            # Check relationship strength
            if "min_relationship_strength" in filters:
                min_strength = filters["min_relationship_strength"]
                if not any(rel.strength >= min_strength for rel in relationships):
                    continue

            filtered_nodes.append(node)

        return filtered_nodes

    async def _filter_by_structure(
        self, nodes: list[KnowledgeNode], filters: dict[str, Any]
    ) -> list[KnowledgeNode]:
        """Filter nodes based on graph structure criteria."""
        # This would require building the graph structure
        graph = await self._get_cached_graph()

        filtered_nodes = []

        for node in nodes:
            if node.id not in graph:
                continue

            # Check centrality measures
            if "min_centrality" in filters:
                centrality_measures = await self.analyzer.calculate_centrality_measures(graph)
                node_centrality = centrality_measures.get("pagerank", {}).get(node.id, 0)

                if node_centrality < filters["min_centrality"]:
                    continue

            # Check connectivity
            if "min_degree" in filters:
                if graph.degree(node.id) < filters["min_degree"]:
                    continue

            filtered_nodes.append(node)

        return filtered_nodes

    async def _get_cached_graph(self) -> nx.DiGraph:
        """Get cached NetworkX graph or build it."""
        now = datetime.now()

        if (
            self._graph_cache is None
            or self._cache_timestamp is None
            or now - self._cache_timestamp > self._cache_ttl
        ):
            # Rebuild cache
            self._graph_cache = await self._build_networkx_graph()
            self._cache_timestamp = now

        return self._graph_cache

    async def _build_networkx_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from stored data."""
        graph = nx.DiGraph()

        # Add nodes
        nodes = await self.storage.get_all_nodes()
        for node in nodes:
            graph.add_node(
                node.id,
                type=node.type.value,
                label=node.label,
                importance=node.importance,
                **node.properties,
            )

        # Add edges
        relationships = await self.storage.get_all_relationships()
        for rel in relationships:
            graph.add_edge(
                rel.source_id,
                rel.target_id,
                type=rel.type.value,
                strength=rel.strength,
                confidence=rel.confidence,
                **rel.properties,
            )

        return graph

    def _invalidate_cache(self) -> None:
        """Invalidate the graph cache."""
        self._graph_cache = None
        self._cache_timestamp = None

    async def get_graph_statistics(self) -> dict[str, Any]:
        """Get statistics about the knowledge graph.

        Returns:
            Dictionary containing graph statistics
        """
        try:
            graph = await self._get_cached_graph()

            stats = {
                "total_nodes": graph.number_of_nodes(),
                "total_relationships": graph.number_of_edges(),
                "node_types": {},
                "relationship_types": {},
                "average_degree": 0,
                "density": 0,
                "connected_components": 0,
            }

            # Node type distribution
            nodes = await self.storage.get_all_nodes()
            for node in nodes:
                node_type = node.type.value
                stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

            # Relationship type distribution
            relationships = await self.storage.get_all_relationships()
            for rel in relationships:
                rel_type = rel.type.value
                stats["relationship_types"][rel_type] = (
                    stats["relationship_types"].get(rel_type, 0) + 1
                )

            # Graph metrics
            if graph.number_of_nodes() > 0:
                stats["average_degree"] = (
                    sum(dict(graph.degree()).values()) / graph.number_of_nodes()
                )
                stats["density"] = nx.density(graph)

            # Connected components
            undirected_graph = graph.to_undirected()
            stats["connected_components"] = nx.number_connected_components(undirected_graph)

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get graph statistics: {e}")
            return {"error": str(e)}

    async def find_shortest_path(self, source_id: str, target_id: str) -> Optional[list[str]]:
        """Find shortest path between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            List of node IDs in path, or None if no path exists
        """
        graph = await self._get_cached_graph()
        return await self.analyzer.find_shortest_path(graph, source_id, target_id)

    async def get_influential_nodes(self, top_k: int = 10) -> list[tuple[str, float]]:
        """Get most influential nodes in the graph.

        Args:
            top_k: Number of nodes to return

        Returns:
            List of (node_id, influence_score) tuples
        """
        graph = await self._get_cached_graph()
        return await self.analyzer.find_influential_nodes(graph, top_k)

    async def recommend_relationships(
        self, node_id: str, max_recommendations: int = 5
    ) -> list[tuple[str, float]]:
        """Recommend potential relationships for a node.

        Args:
            node_id: Node to recommend relationships for
            max_recommendations: Maximum number of recommendations

        Returns:
            List of (recommended_node_id, score) tuples
        """
        graph = await self._get_cached_graph()
        return await self.analyzer.recommend_relationships(graph, node_id, max_recommendations)

    async def detect_communities(self) -> list[set[str]]:
        """Detect communities in the knowledge graph.

        Returns:
            List of sets containing node IDs in each community
        """
        graph = await self._get_cached_graph()
        return await self.analyzer.detect_communities(graph)

    async def analyze_relationship_patterns(self) -> dict[str, Any]:
        """Analyze patterns in graph relationships.

        Returns:
            Dictionary containing relationship pattern analysis
        """
        relationships = await self.storage.get_all_relationships()
        return await self.analyzer.analyze_relationship_patterns(relationships)

    async def create_pattern_node(
        self, pattern_id: str, pattern_data: dict[str, Any]
    ) -> KnowledgeNode:
        """Create a node for a pattern.

        Args:
            pattern_id: Pattern identifier
            pattern_data: Pattern data

        Returns:
            Created knowledge node
        """
        node = KnowledgeNode(
            id=f"pattern_{pattern_id}",
            type=NodeType.PATTERN,
            label=pattern_data.get("name", f"Pattern {pattern_id}"),
            properties={
                "category": pattern_data.get("category"),
                "success_rate": pattern_data.get("success_rate"),
                "usage_count": pattern_data.get("usage_count"),
                "confidence": pattern_data.get("confidence"),
            },
            created_at=datetime.now(),
            last_updated=datetime.now(),
            importance=pattern_data.get("confidence", 0.5),
            tags=["pattern", pattern_data.get("category", "unknown")],
        )

        await self.add_node(node)
        return node

    async def create_failure_node(
        self, failure_id: str, failure_data: dict[str, Any]
    ) -> KnowledgeNode:
        """Create a node for a failure pattern.

        Args:
            failure_id: Failure identifier
            failure_data: Failure data

        Returns:
            Created knowledge node
        """
        node = KnowledgeNode(
            id=f"failure_{failure_id}",
            type=NodeType.FAILURE,
            label=failure_data.get("signature", f"Failure {failure_id}"),
            properties={
                "category": failure_data.get("category"),
                "severity": failure_data.get("severity"),
                "frequency": failure_data.get("frequency"),
                "root_cause": failure_data.get("root_cause"),
            },
            created_at=datetime.now(),
            last_updated=datetime.now(),
            importance=1.0
            - failure_data.get("frequency", 1) / 10,  # More frequent = higher importance
            tags=["failure", failure_data.get("category", "unknown")],
        )

        await self.add_node(node)
        return node

    async def create_memory_node(
        self, memory_id: str, memory_data: dict[str, Any]
    ) -> KnowledgeNode:
        """Create a node for a memory.

        Args:
            memory_id: Memory identifier
            memory_data: Memory data

        Returns:
            Created knowledge node
        """
        node = KnowledgeNode(
            id=f"memory_{memory_id}",
            type=NodeType.MEMORY,
            label=f"Memory {memory_data.get('type', 'Unknown')}",
            properties={
                "memory_type": memory_data.get("type"),
                "cycle_id": memory_data.get("cycle_id"),
                "agent_id": memory_data.get("agent_id"),
                "importance": memory_data.get("importance"),
            },
            created_at=datetime.now(),
            last_updated=datetime.now(),
            importance=memory_data.get("importance", 0.5),
            tags=["memory", memory_data.get("type", "unknown")],
        )

        await self.add_node(node)
        return node
