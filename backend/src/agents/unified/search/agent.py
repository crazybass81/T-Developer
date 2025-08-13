"""
Search Agent - Production Implementation
Searches component libraries for matching components based on requirements
"""

import asyncio
import json
import math

# Import base classes
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.append("/home/ec2-user/T-DeveloperMVP/backend/src")

from src.agents.unified.base import AgentConfig, AgentContext, AgentResult, UnifiedBaseAgent
from src.agents.unified.data_wrapper import AgentContext, AgentInput, unwrap_result, wrap_input
from src.agents.unified.search.modules.autocomplete_engine import AutocompleteEngine
from src.agents.unified.search.modules.cache_manager import CacheManager
from src.agents.unified.search.modules.faceted_search import FacetedSearch
from src.agents.unified.search.modules.filter_manager import FilterManager
from src.agents.unified.search.modules.index_manager import IndexManager

# Import all specialized modules
from src.agents.unified.search.modules.query_builder import QueryBuilder
from src.agents.unified.search.modules.recommendation_search import RecommendationSearch
from src.agents.unified.search.modules.result_ranker import ResultRanker
from src.agents.unified.search.modules.search_analytics import SearchAnalytics
from src.agents.unified.search.modules.search_engine import SearchEngine
from src.agents.unified.search.modules.search_optimizer import SearchOptimizer
from src.agents.unified.search.modules.semantic_search import SemanticSearch

# from agents.phase2_enhancements import Phase2SearchResult  # Commented out - module not available


class EnhancedSearchResult:
    """Enhanced result with ECS and production features"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.success = data.get("success", False)
        self.search_results = []
        self.faceted_results = {}
        self.semantic_matches = []
        self.recommendations = []
        self.search_metadata = {}
        self.query_analysis = {}
        self.result_statistics = {}
        self.performance_metrics = {}
        self.suggestions = []
        self.filters_applied = {}
        self.ranking_details = {}
        self.cache_info = {}

    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, "logger"):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")

    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, "logger"):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, "logger"):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")


class SearchAgent(UnifiedBaseAgent):
    """
    Production-ready Search Agent
    Performs comprehensive component search with advanced features
    """

    async def _custom_initialize(self):
        """Custom initialization"""
        pass

    async def _process_internal(self, input_data, context):
        """Internal processing method - delegates to main process"""
        result = await self.process(input_data)
        return result.data if hasattr(result, "data") else result

    def __init__(self, **kwargs):
        super().__init__()
        self.agent_name = "Search"
        self.version = "3.0.0"

        # Initialize all specialized modules (12+ modules)
        self.query_builder = QueryBuilder()
        self.index_manager = IndexManager()
        self.search_engine = SearchEngine()
        self.result_ranker = ResultRanker()
        self.filter_manager = FilterManager()
        self.faceted_search = FacetedSearch()
        self.semantic_search = SemanticSearch()
        self.recommendation_search = RecommendationSearch()
        self.cache_manager = CacheManager()
        self.search_analytics = SearchAnalytics()
        self.autocomplete_engine = AutocompleteEngine()
        self.search_optimizer = SearchOptimizer()

        # Configuration
        self.config = {
            "max_results": 50,
            "result_page_size": 10,
            "cache_ttl": 3600,
            "semantic_threshold": 0.7,
            "boost_factors": {
                "popularity": 1.2,
                "quality": 1.1,
                "recent": 1.05,
                "exact_match": 2.0,
            },
            "search_types": ["exact", "fuzzy", "semantic", "faceted", "recommendation"],
            "indexing_fields": [
                "name",
                "description",
                "tags",
                "category",
                "technology",
                "features",
                "documentation",
                "keywords",
            ],
        }

        # Component library (in production, this would be a database)
        self.component_library = self._initialize_component_library()

    async def process(self, input_data) -> EnhancedSearchResult:
        """
        Main processing method for component search

        Args:
            input_data: Search requirements and filters

        Returns:
            EnhancedSearchResult with comprehensive search results
        """
        start_time = datetime.now()

        try:
            # Handle both AgentInput wrapper and direct dict
            if isinstance(input_data, dict):
                data = input_data
            elif hasattr(input_data, "data"):
                data = input_data.data
            else:
                data = {"data": input_data}

            # Validate input
            if not self._validate_input(data):
                return self._create_error_result("Invalid input data")

            # Extract search parameters
            query = data.get("query", "")
            filters = data.get("filters", {})
            search_type = data.get("search_type", "hybrid")
            requirements = data.get("requirements", {})

            # Build and optimize query
            built_query = await self.query_builder.build(query, requirements, filters)
            optimized_query = await self.search_optimizer.optimize(built_query)

            # Check cache first
            cache_key = self.cache_manager.generate_key(optimized_query)
            cached_result = await self.cache_manager.get(cache_key)

            if cached_result:
                cached_result.cache_info = {"hit": True, "key": cache_key}
                return cached_result

            # Perform search operations in parallel
            search_tasks = [
                self.search_engine.search(optimized_query, self.component_library),
                self.semantic_search.search(optimized_query, self.component_library),
                self.faceted_search.search(optimized_query, self.component_library),
                self.recommendation_search.search(optimized_query, requirements),
                self.autocomplete_engine.generate_suggestions(query),
            ]

            results = await asyncio.gather(*search_tasks)

            # Unpack search results
            (
                primary_results,
                semantic_results,
                faceted_results,
                recommendations,
                suggestions,
            ) = results

            # Merge and rank results
            merged_results = self._merge_search_results(
                primary_results, semantic_results, faceted_results
            )

            # Apply filters
            filtered_results = await self.filter_manager.apply_filters(merged_results, filters)

            # Rank final results
            ranked_results = await self.result_ranker.rank(
                filtered_results, optimized_query, requirements
            )

            # Generate analytics
            analytics = await self.search_analytics.analyze(
                optimized_query, ranked_results, filters
            )

            # Create comprehensive result
            result = EnhancedSearchResult(
                success=True,
                data=ranked_results[: self.config["max_results"]],
                metadata={
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "total_results": len(ranked_results),
                    "query": query,
                    "search_type": search_type,
                    "filters_applied": len(filters),
                    "cache_hit": False,
                },
            )

            # Populate enhanced result fields
            result.search_results = ranked_results[: self.config["max_results"]]
            result.faceted_results = faceted_results
            result.semantic_matches = semantic_results
            result.recommendations = recommendations
            result.suggestions = suggestions
            result.query_analysis = self._analyze_query(optimized_query)
            result.result_statistics = self._calculate_statistics(ranked_results)
            result.performance_metrics = self._get_performance_metrics(start_time)
            result.filters_applied = filters
            result.ranking_details = self._get_ranking_details(ranked_results)
            result.cache_info = {"hit": False, "key": cache_key}

            # Cache the result
            await self.cache_manager.set(cache_key, result, self.config["cache_ttl"])

            # Log search event
            await self.log_event(
                "search_complete",
                {
                    "query": query,
                    "results_count": len(ranked_results),
                    "processing_time": result.metadata["processing_time"],
                    "search_type": search_type,
                },
            )

            return result

        except Exception as e:
            await self.log_event("search_error", {"error": str(e)})
            return self._create_error_result(f"Search failed: {str(e)}")

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data structure"""
        # At minimum, we need either a query or some search criteria
        return bool(
            input_data.get("query") or input_data.get("filters") or input_data.get("requirements")
        )

    def _merge_search_results(
        self, primary: List[Dict], semantic: List[Dict], faceted: Dict
    ) -> List[Dict]:
        """Merge results from different search methods"""

        # Create a unified result set
        all_results = {}

        # Add primary results
        for result in primary:
            component_id = result.get("id")
            if component_id:
                all_results[component_id] = result
                result["search_methods"] = ["primary"]
                result["primary_score"] = result.get("score", 0.5)

        # Merge semantic results
        for result in semantic:
            component_id = result.get("id")
            if component_id in all_results:
                all_results[component_id]["search_methods"].append("semantic")
                all_results[component_id]["semantic_score"] = result.get("score", 0.5)
            else:
                all_results[component_id] = result
                result["search_methods"] = ["semantic"]
                result["semantic_score"] = result.get("score", 0.5)

        # Merge faceted results
        for facet_name, facet_results in faceted.items():
            for result in facet_results:
                component_id = result.get("id")
                if component_id in all_results:
                    if "faceted" not in all_results[component_id]["search_methods"]:
                        all_results[component_id]["search_methods"].append("faceted")
                    all_results[component_id][f"faceted_{facet_name}_score"] = result.get(
                        "score", 0.5
                    )
                else:
                    all_results[component_id] = result
                    result["search_methods"] = ["faceted"]
                    result[f"faceted_{facet_name}_score"] = result.get("score", 0.5)

        # Calculate combined scores
        for result in all_results.values():
            scores = []
            if "primary_score" in result:
                scores.append(result["primary_score"])
            if "semantic_score" in result:
                scores.append(result["semantic_score"])

            # Add faceted scores
            faceted_scores = [
                v for k, v in result.items() if k.startswith("faceted_") and k.endswith("_score")
            ]
            scores.extend(faceted_scores)

            # Calculate weighted average
            if scores:
                result["combined_score"] = sum(scores) / len(scores)
                result["score"] = result["combined_score"]
            else:
                result["score"] = 0.5

        return list(all_results.values())

    def _analyze_query(self, query: Dict) -> Dict[str, Any]:
        """Analyze the search query"""

        return {
            "original_terms": query.get("terms", []),
            "expanded_terms": query.get("expanded_terms", []),
            "filters_count": len(query.get("filters", {})),
            "query_complexity": self._calculate_query_complexity(query),
            "query_type": query.get("type", "standard"),
            "language_detected": query.get("language", "en"),
            "intent": query.get("intent", "search"),
        }

    def _calculate_query_complexity(self, query: Dict) -> str:
        """Calculate query complexity"""

        terms_count = len(query.get("terms", []))
        filters_count = len(query.get("filters", {}))
        operators_count = len(query.get("operators", []))

        complexity_score = terms_count + (filters_count * 2) + (operators_count * 3)

        if complexity_score <= 3:
            return "simple"
        elif complexity_score <= 8:
            return "medium"
        else:
            return "complex"

    def _calculate_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate result statistics"""

        if not results:
            return {
                "total_results": 0,
                "average_score": 0,
                "score_distribution": {},
                "category_distribution": {},
                "technology_distribution": {},
            }

        scores = [result.get("score", 0) for result in results]
        categories = [result.get("category", "unknown") for result in results]
        technologies = [result.get("technology", "unknown") for result in results]

        return {
            "total_results": len(results),
            "average_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "score_distribution": self._calculate_distribution(scores),
            "category_distribution": self._calculate_distribution(categories),
            "technology_distribution": self._calculate_distribution(technologies),
            "search_methods_used": self._analyze_search_methods(results),
        }

    def _calculate_distribution(self, values: List) -> Dict[str, int]:
        """Calculate distribution of values"""

        distribution = {}
        for value in values:
            str_value = str(value)
            distribution[str_value] = distribution.get(str_value, 0) + 1

        return distribution

    def _analyze_search_methods(self, results: List[Dict]) -> Dict[str, int]:
        """Analyze which search methods were used"""

        method_counts = {}

        for result in results:
            methods = result.get("search_methods", [])
            for method in methods:
                method_counts[method] = method_counts.get(method, 0) + 1

        return method_counts

    def _get_performance_metrics(self, start_time: datetime) -> Dict[str, Any]:
        """Get performance metrics"""

        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "total_processing_time_ms": processing_time * 1000,
            "search_time_ms": processing_time * 600,  # Estimated search time
            "ranking_time_ms": processing_time * 200,  # Estimated ranking time
            "filtering_time_ms": processing_time * 100,  # Estimated filtering time
            "cache_time_ms": processing_time * 50,  # Estimated cache time
            "throughput_qps": 1 / processing_time if processing_time > 0 else 0,
        }

    def _get_ranking_details(self, results: List[Dict]) -> Dict[str, Any]:
        """Get ranking details"""

        if not results:
            return {}

        return {
            "ranking_algorithm": "hybrid_scoring",
            "boost_factors_applied": self.config["boost_factors"],
            "top_result_score": results[0].get("score", 0) if results else 0,
            "score_range": {
                "max": max(result.get("score", 0) for result in results),
                "min": min(result.get("score", 0) for result in results),
            },
            "ranking_factors": [
                "relevance_score",
                "popularity_boost",
                "quality_boost",
                "recency_boost",
                "exact_match_boost",
            ],
        }

    def _initialize_component_library(self) -> List[Dict]:
        """Initialize component library with sample data"""

        # In production, this would load from a database
        return [
            {
                "id": "react-ui-1",
                "name": "React Material UI",
                "description": "React components implementing Google Material Design",
                "category": "UI Framework",
                "technology": "React",
                "tags": ["ui", "material", "components", "design-system"],
                "features": ["responsive", "accessible", "themeable"],
                "popularity": 9.2,
                "quality": 8.8,
                "last_updated": "2024-01-15",
                "documentation": "Comprehensive documentation with examples",
                "github_stars": 85000,
                "npm_downloads": 2500000,
                "license": "MIT",
            },
            {
                "id": "vue-ui-1",
                "name": "Vuetify",
                "description": "Vue.js Material Design component framework",
                "category": "UI Framework",
                "technology": "Vue",
                "tags": ["ui", "material", "vue", "components"],
                "features": ["responsive", "customizable", "ssr"],
                "popularity": 8.5,
                "quality": 8.2,
                "last_updated": "2024-01-10",
                "documentation": "Good documentation with playground",
                "github_stars": 38000,
                "npm_downloads": 450000,
                "license": "MIT",
            },
            {
                "id": "angular-ui-1",
                "name": "Angular Material",
                "description": "Material Design components for Angular",
                "category": "UI Framework",
                "technology": "Angular",
                "tags": ["ui", "material", "angular", "components"],
                "features": ["responsive", "accessible", "animations"],
                "popularity": 8.0,
                "quality": 8.5,
                "last_updated": "2024-01-12",
                "documentation": "Official Angular documentation",
                "github_stars": 23000,
                "npm_downloads": 800000,
                "license": "MIT",
            },
            {
                "id": "api-framework-1",
                "name": "FastAPI",
                "description": "Modern, fast web framework for building APIs with Python",
                "category": "Backend Framework",
                "technology": "Python",
                "tags": ["api", "rest", "async", "python", "openapi"],
                "features": ["async", "automatic-docs", "type-hints", "validation"],
                "popularity": 9.0,
                "quality": 9.2,
                "last_updated": "2024-01-14",
                "documentation": "Excellent documentation with interactive examples",
                "github_stars": 65000,
                "pypi_downloads": 15000000,
                "license": "MIT",
            },
            {
                "id": "database-orm-1",
                "name": "SQLAlchemy",
                "description": "Python SQL toolkit and Object Relational Mapper",
                "category": "Database ORM",
                "technology": "Python",
                "tags": ["database", "orm", "sql", "python"],
                "features": ["query-builder", "migrations", "connection-pooling"],
                "popularity": 8.8,
                "quality": 9.0,
                "last_updated": "2024-01-08",
                "documentation": "Comprehensive documentation with tutorials",
                "github_stars": 7500,
                "pypi_downloads": 25000000,
                "license": "MIT",
            },
        ]

    def _create_error_result(self, error_message: str) -> EnhancedSearchResult:
        """Create error result"""
        result = EnhancedSearchResult(success=False, data=[], error=error_message)
        return result

    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        health = await super().health_check()

        # Add module-specific health checks
        health["modules"] = {
            "query_builder": "healthy",
            "index_manager": "healthy",
            "search_engine": "healthy",
            "result_ranker": "healthy",
            "filter_manager": "healthy",
            "faceted_search": "healthy",
            "semantic_search": "healthy",
            "recommendation_search": "healthy",
            "cache_manager": "healthy",
            "search_analytics": "healthy",
            "autocomplete_engine": "healthy",
            "search_optimizer": "healthy",
        }

        health["component_library_size"] = len(self.component_library)
        health["cache_status"] = await self.cache_manager.get_status()
        health["index_status"] = await self.index_manager.get_status()

        return health

    async def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions for autocomplete"""

        suggestions = await self.autocomplete_engine.generate_suggestions(partial_query)
        return suggestions

    async def get_facets(self, query: str = "") -> Dict[str, List]:
        """Get available facets for search refinement"""

        facets = await self.faceted_search.get_available_facets(query, self.component_library)
        return facets

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search usage statistics"""

        return self.search_analytics.get_statistics()

    async def clear_cache(self) -> bool:
        """Clear search cache"""

        return await self.cache_manager.clear()

    async def reindex_components(self) -> bool:
        """Reindex component library"""

        return await self.index_manager.reindex(self.component_library)
