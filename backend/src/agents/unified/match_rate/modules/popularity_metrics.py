"""
Popularity Metrics Module
Gathers and analyzes popularity metrics
"""

from typing import Any, Dict, List, Optional


class PopularityMetrics:
    """Gathers popularity metrics"""

    async def gather(self, components: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Gather popularity metrics"""

        popularity_results = {}

        for component in components:
            component_id = component.get("id", component.get("name"))

            popularity_data = {
                "github_stars": component.get("github_stars", 100),
                "npm_downloads": component.get("npm_downloads", 1000),
                "community_size": component.get("community_size", 500),
                "stackoverflow_tags": component.get("stackoverflow_tags", 50),
                "popularity_score": self._calculate_popularity_score(component),
            }

            popularity_results[component_id] = popularity_data

        return popularity_results

    def _calculate_popularity_score(self, component: Dict) -> float:
        """Calculate overall popularity score"""
        stars = component.get("github_stars", 100)
        downloads = component.get("npm_downloads", 1000)

        # Normalize and combine metrics
        star_score = min(1.0, stars / 10000)
        download_score = min(1.0, downloads / 100000)

        return (star_score + download_score) / 2
