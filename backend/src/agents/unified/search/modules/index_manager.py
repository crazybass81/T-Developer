"""
Index Manager Module
Manages search indexes for efficient component retrieval
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime


class IndexManager:
    """Manages search indexes"""

    def __init__(self):
        self.indexes = {}
        self.index_status = "ready"
        self.last_update = None

    async def create_index(self, components: List[Dict[str, Any]]) -> bool:
        """Create search indexes from components"""

        try:
            # Create inverted index for text fields
            self.indexes["text"] = self._create_text_index(components)

            # Create category index
            self.indexes["category"] = self._create_category_index(components)

            # Create technology index
            self.indexes["technology"] = self._create_technology_index(components)

            # Create popularity index
            self.indexes["popularity"] = self._create_popularity_index(components)

            # Create tag index
            self.indexes["tags"] = self._create_tag_index(components)

            # Create composite index
            self.indexes["composite"] = self._create_composite_index(components)

            self.last_update = datetime.now()
            self.index_status = "ready"

            return True

        except Exception as e:
            self.index_status = f"error: {str(e)}"
            return False

    def _create_text_index(self, components: List[Dict]) -> Dict[str, List[str]]:
        """Create inverted text index"""

        index = {}

        for component in components:
            component_id = component.get("id")

            # Index text fields
            text_fields = ["name", "description", "documentation"]
            for field in text_fields:
                if field in component:
                    words = str(component[field]).lower().split()
                    for word in words:
                        if word not in index:
                            index[word] = []
                        if component_id not in index[word]:
                            index[word].append(component_id)

        return index

    def _create_category_index(self, components: List[Dict]) -> Dict[str, List[str]]:
        """Create category index"""

        index = {}

        for component in components:
            component_id = component.get("id")
            category = component.get("category", "uncategorized")

            if category not in index:
                index[category] = []
            index[category].append(component_id)

        return index

    def _create_technology_index(self, components: List[Dict]) -> Dict[str, List[str]]:
        """Create technology index"""

        index = {}

        for component in components:
            component_id = component.get("id")
            technology = component.get("technology", "unknown")

            if technology not in index:
                index[technology] = []
            index[technology].append(component_id)

        return index

    def _create_popularity_index(
        self, components: List[Dict]
    ) -> List[Tuple[str, float]]:
        """Create popularity-sorted index"""

        popularity_list = []

        for component in components:
            component_id = component.get("id")
            popularity = component.get("popularity", 0.0)
            popularity_list.append((component_id, popularity))

        # Sort by popularity descending
        popularity_list.sort(key=lambda x: x[1], reverse=True)

        return popularity_list

    def _create_tag_index(self, components: List[Dict]) -> Dict[str, List[str]]:
        """Create tag index"""

        index = {}

        for component in components:
            component_id = component.get("id")
            tags = component.get("tags", [])

            for tag in tags:
                if tag not in index:
                    index[tag] = []
                index[tag].append(component_id)

        return index

    def _create_composite_index(self, components: List[Dict]) -> Dict[str, Dict]:
        """Create composite index combining multiple factors"""

        index = {}

        for component in components:
            component_id = component.get("id")

            # Create composite key
            category = component.get("category", "unknown")
            technology = component.get("technology", "unknown")
            composite_key = f"{category}:{technology}"

            if composite_key not in index:
                index[composite_key] = {
                    "components": [],
                    "avg_popularity": 0.0,
                    "count": 0,
                }

            index[composite_key]["components"].append(component_id)
            index[composite_key]["count"] += 1

            # Update average popularity
            popularity = component.get("popularity", 0.0)
            current_avg = index[composite_key]["avg_popularity"]
            count = index[composite_key]["count"]
            index[composite_key]["avg_popularity"] = (
                (current_avg * (count - 1)) + popularity
            ) / count

        return index

    async def search_index(
        self, index_name: str, query: str, max_results: int = 100
    ) -> List[str]:
        """Search a specific index"""

        if index_name not in self.indexes:
            return []

        index = self.indexes[index_name]
        results = []

        if index_name == "text":
            # Search text index
            query_words = query.lower().split()
            for word in query_words:
                if word in index:
                    results.extend(index[word])

        elif index_name in ["category", "technology", "tags"]:
            # Search categorical indexes
            if query in index:
                results.extend(index[query])

        elif index_name == "popularity":
            # Return top popular components
            results = [comp_id for comp_id, _ in index[:max_results]]

        # Remove duplicates while preserving order
        unique_results = []
        seen = set()
        for result in results:
            if result not in seen:
                unique_results.append(result)
                seen.add(result)

        return unique_results[:max_results]

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""

        stats = {
            "total_indexes": len(self.indexes),
            "status": self.index_status,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }

        for index_name, index_data in self.indexes.items():
            if index_name == "text":
                stats[f"{index_name}_terms"] = len(index_data)
            elif index_name == "popularity":
                stats[f"{index_name}_entries"] = len(index_data)
            elif isinstance(index_data, dict):
                stats[f"{index_name}_categories"] = len(index_data)

        return stats

    async def reindex(self, components: List[Dict[str, Any]]) -> bool:
        """Reindex components"""

        self.index_status = "rebuilding"
        success = await self.create_index(components)

        return success

    async def get_status(self) -> str:
        """Get index manager status"""

        return self.index_status

    def get_available_facets(self, components: List[Dict]) -> Dict[str, List]:
        """Get available facets from components"""

        facets = {
            "categories": [],
            "technologies": [],
            "tags": [],
            "popularity_ranges": ["0-2", "2-5", "5-7", "7-9", "9-10"],
            "licenses": [],
        }

        categories = set()
        technologies = set()
        all_tags = set()
        licenses = set()

        for component in components:
            if "category" in component:
                categories.add(component["category"])
            if "technology" in component:
                technologies.add(component["technology"])
            if "tags" in component:
                all_tags.update(component["tags"])
            if "license" in component:
                licenses.add(component["license"])

        facets["categories"] = sorted(list(categories))
        facets["technologies"] = sorted(list(technologies))
        facets["tags"] = sorted(list(all_tags))
        facets["licenses"] = sorted(list(licenses))

        return facets
