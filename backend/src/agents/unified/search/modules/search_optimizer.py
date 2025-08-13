"""🧬 T-Developer Search Optimizer <6.5KB"""
import math
import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple


class SearchOptimizer:
    """Ultra-lightweight search optimizer"""

    def __init__(self):
        self.strategies = {
            "rewrite": self._rewrite_query,
            "expand": self._expand_terms,
            "boost": self._adjust_boost,
            "filter": self._optimize_filters,
            "cache": self._optimize_cache,
        }

        self.config = {"max_results": 50, "boost_factor": 1.5, "cache_ttl": 300, "min_score": 0.1}

        self.query_cache = {}
        self.term_synonyms = {
            "js": ["javascript", "node"],
            "py": ["python"],
            "db": ["database", "storage"],
            "auth": ["authentication", "login"],
            "ui": ["interface", "frontend"],
        }

    async def optimize(self, query: Dict, context: Dict = None) -> Dict:
        """Optimize search query"""
        context = context or {}
        optimized_query = query.copy()

        # Apply optimization strategies
        for strategy_name, strategy_func in self.strategies.items():
            try:
                optimized_query = strategy_func(optimized_query, context)
            except Exception:
                continue  # Skip failed optimizations

        # Add performance metadata
        optimized_query["_opt"] = {
            "strategies": len(self.strategies),
            "terms_diff": len(optimized_query.get("terms", [])) - len(query.get("terms", [])),
        }

        return optimized_query

    def _rewrite_query(self, query: Dict, context: Dict) -> Dict:
        """Rewrite query for better matching"""
        terms = query.get("terms", [])
        rewritten_terms = []

        for term in terms:
            # Fix common typos
            cleaned = self._fix_typos(term)
            # Standardize casing
            cleaned = cleaned.lower().strip()
            # Remove noise words
            if len(cleaned) > 2 and cleaned not in ["the", "and", "or"]:
                rewritten_terms.append(cleaned)

        query["terms"] = rewritten_terms
        return query

    def _expand_terms(self, query: Dict, context: Dict) -> Dict:
        """Expand query terms with synonyms"""
        terms = query.get("terms", [])
        expanded_terms = set(terms)

        for term in terms:
            if term in self.term_synonyms:
                expanded_terms.update(self.term_synonyms[term])

        query["terms"] = list(expanded_terms)
        return query

    def _adjust_boost(self, query: Dict, context: Dict) -> Dict:
        """Adjust boost factors"""
        framework = context.get("framework", "")
        category = context.get("category", "")

        boosts = query.get("boosts", {})

        # Framework-specific boosts
        if framework:
            boosts[f"framework:{framework}"] = 2.0

        # Category boosts
        if category:
            boosts[f"category:{category}"] = 1.5

        # Popular term boosts
        for term in query.get("terms", []):
            if term in ["react", "vue", "express", "typescript", "python"]:
                boosts[f"term:{term}"] = self.config["boost_factor"]

        query["boosts"] = boosts
        return query

    def _optimize_filters(self, query: Dict, context: Dict) -> Dict:
        """Optimize search filters"""
        filters = query.get("filters", {})

        # Add implicit filters
        if context.get("user_level") == "beginner":
            filters["complexity"] = "low"

        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}

        query["filters"] = filters
        return query

    def _optimize_cache(self, query: Dict, context: Dict) -> Dict:
        """Add cache optimization hints"""
        cache_key = self._generate_cache_key(query)
        query["_cache_key"] = cache_key
        query["_cache_ttl"] = self.config["cache_ttl"]
        return query

    def _fix_typos(self, term: str) -> str:
        """Fix common typos"""
        typos = {
            "javascirpt": "javascript",
            "pyhton": "python",
            "reactjs": "react",
            "vuejs": "vue",
            "databse": "database",
            "authetication": "authentication",
        }
        return typos.get(term.lower(), term)

    def _generate_cache_key(self, query: Dict) -> str:
        """Generate cache key for query"""
        terms = sorted(query.get("terms", []))
        filters = sorted(query.get("filters", {}).items())
        return f"search:{hash(str(terms + filters))}"

    def analyze_performance(self, query: Dict, results: List[Dict], exec_time: float) -> Dict:
        """Analyze search performance"""
        return {
            "complexity": len(query.get("terms", [])),
            "count": len(results),
            "time": exec_time,
            "avg_score": sum(r.get("score", 0) for r in results) / max(len(results), 1),
            "recs": self._get_optimization_recommendations(query, exec_time),
        }

    def _get_optimization_recommendations(self, query: Dict, exec_time: float) -> List[str]:
        """Get optimization recommendations"""
        recs = []
        if exec_time > 1.0:
            recs.append("Reduce query complexity")
        if len(query.get("terms", [])) > 10:
            recs.append("Too many search terms")
        if not query.get("filters"):
            recs.append("Add filters")
        return recs

    def suggest_related_queries(self, query: str) -> List[str]:
        """Suggest related queries"""
        suggestions = []
        for term in query.lower().split():
            if term in self.term_synonyms:
                for syn in self.term_synonyms[term][:2]:
                    new_query = query.replace(term, syn)
                    if new_query != query:
                        suggestions.append(new_query)
        return suggestions[:3]

    def get_search_stats(self) -> Dict:
        """Get search optimization statistics"""
        return {
            "cache": len(self.query_cache),
            "synonyms": sum(len(s) for s in self.term_synonyms.values()),
        }


def optimize_search_query(query: Dict, context: Dict = None) -> Dict:
    """Quick search query optimization"""
    optimizer = SearchOptimizer()
    import asyncio

    return asyncio.run(optimizer.optimize(query, context))


def suggest_query_improvements(query_text: str) -> List[str]:
    """Suggest query improvements"""
    optimizer = SearchOptimizer()
    return optimizer.suggest_related_queries(query_text)
