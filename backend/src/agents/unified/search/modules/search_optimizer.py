"""
Search Optimizer Module
Advanced search query optimization and performance tuning
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import math
from collections import defaultdict, Counter
from datetime import datetime
import asyncio


class SearchOptimizer:
    """Advanced search query optimizer with performance tuning"""

    def __init__(self):
        # Optimization strategies
        self.optimization_strategies = {
            "query_rewriting": self._optimize_query_rewriting,
            "term_expansion": self._optimize_term_expansion,
            "boost_adjustment": self._optimize_boost_factors,
            "filter_optimization": self._optimize_filters,
            "result_limiting": self._optimize_result_limits,
            "cache_optimization": self._optimize_caching,
            "performance_tuning": self._optimize_performance,
            "relevance_tuning": self._optimize_relevance,
        }

        # Optimization configuration
        self.config = {
            "enable_query_rewriting": True,
            "enable_term_expansion": True,
            "enable_auto_boosting": True,
            "enable_filter_optimization": True,
            "enable_performance_optimization": True,
            "max_expanded_terms": 15,
            "min_term_length": 2,
            "boost_threshold": 0.1,
            "cache_optimization_threshold": 100,  # ms
            "result_limit_optimization": True,
        }

        # Performance metrics
        self.performance_history = []
        self.query_patterns = defaultdict(list)
        self.optimization_stats = {
            "queries_optimized": 0,
            "avg_improvement_ms": 0,
            "successful_optimizations": 0,
            "failed_optimizations": 0,
        }

        # Query analysis patterns
        self.problematic_patterns = {
            "too_broad": r"^[a-z]{1,3}$",  # Very short queries
            "too_specific": r"^.{100,}$",  # Very long queries
            "stop_words_heavy": r"^(the|a|an|and|or|but|in|on|at|to|for|of|with|by)\s",
            "typos_likely": r".*[aeiou]{3,}.*|.*[bcdfghjklmnpqrstvwxyz]{4,}.*",
        }

        # Optimization rules
        self.rewriting_rules = self._build_rewriting_rules()
        self.expansion_rules = self._build_expansion_rules()
        self.boost_rules = self._build_boost_rules()

    async def optimize(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize search query for better performance and relevance"""

        start_time = datetime.now()
        original_query = query.copy()

        # Analyze query for optimization opportunities
        analysis = self._analyze_query_optimization_needs(query)

        # Apply optimization strategies based on analysis
        optimized_query = query.copy()
        applied_optimizations = []

        for strategy_name, strategy_func in self.optimization_strategies.items():
            if self._should_apply_optimization(strategy_name, analysis):
                try:
                    optimization_result = await strategy_func(optimized_query, analysis)
                    if optimization_result:
                        optimized_query = optimization_result
                        applied_optimizations.append(strategy_name)
                except Exception as e:
                    # Log error but continue with other optimizations
                    continue

        # Calculate optimization impact
        optimization_time = (datetime.now() - start_time).total_seconds() * 1000

        # Add optimization metadata
        optimized_query["optimization_metadata"] = {
            "applied_optimizations": applied_optimizations,
            "optimization_time_ms": optimization_time,
            "optimization_analysis": analysis,
            "original_complexity": self._calculate_query_complexity(original_query),
            "optimized_complexity": self._calculate_query_complexity(optimized_query),
        }

        # Update optimization statistics
        self._update_optimization_stats(applied_optimizations, optimization_time)

        return optimized_query

    async def _optimize_query_rewriting(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize query through intelligent rewriting"""

        if not self.config["enable_query_rewriting"]:
            return None

        original_text = query.get("original_query", "")
        rewritten_query = original_text

        # Apply rewriting rules
        for pattern, replacement in self.rewriting_rules.items():
            if isinstance(replacement, str):
                rewritten_query = re.sub(
                    pattern, replacement, rewritten_query, flags=re.IGNORECASE
                )
            elif callable(replacement):
                rewritten_query = replacement(rewritten_query)

        # Handle common query problems
        if analysis.get("too_broad"):
            rewritten_query = self._handle_broad_query(rewritten_query, query)

        if analysis.get("too_specific"):
            rewritten_query = self._handle_specific_query(rewritten_query, query)

        if analysis.get("typos_likely"):
            rewritten_query = self._handle_typo_correction(rewritten_query, query)

        # Only return if query was actually changed
        if rewritten_query != original_text:
            optimized_query = query.copy()
            optimized_query["original_query"] = rewritten_query
            optimized_query["rewritten"] = True
            optimized_query["rewrite_reason"] = self._get_rewrite_reason(analysis)
            return optimized_query

        return None

    async def _optimize_term_expansion(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize through intelligent term expansion"""

        if not self.config["enable_term_expansion"]:
            return None

        original_terms = query.get("terms", [])
        expanded_terms = query.get("expanded_terms", original_terms.copy())

        # Add semantic expansions
        semantic_expansions = self._get_semantic_expansions(original_terms, analysis)
        for expansion in semantic_expansions:
            if expansion not in expanded_terms:
                expanded_terms.append(expansion)

        # Add contextual expansions
        contextual_expansions = self._get_contextual_expansions(
            original_terms, analysis
        )
        for expansion in contextual_expansions:
            if expansion not in expanded_terms:
                expanded_terms.append(expansion)

        # Add domain-specific expansions
        domain_expansions = self._get_domain_specific_expansions(
            original_terms, analysis
        )
        for expansion in domain_expansions:
            if expansion not in expanded_terms:
                expanded_terms.append(expansion)

        # Limit expanded terms to prevent over-expansion
        if len(expanded_terms) > self.config["max_expanded_terms"]:
            # Keep most relevant expansions
            scored_terms = [
                (term, self._calculate_term_relevance(term, original_terms))
                for term in expanded_terms
            ]
            scored_terms.sort(key=lambda x: x[1], reverse=True)
            expanded_terms = [
                term
                for term, score in scored_terms[: self.config["max_expanded_terms"]]
            ]

        # Only return if terms were expanded
        if len(expanded_terms) > len(original_terms):
            optimized_query = query.copy()
            optimized_query["expanded_terms"] = expanded_terms
            optimized_query["expansion_count"] = len(expanded_terms) - len(
                original_terms
            )
            return optimized_query

        return None

    async def _optimize_boost_factors(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize boost factors based on query analysis"""

        if not self.config["enable_auto_boosting"]:
            return None

        current_boosts = query.get("boost_fields", {})
        optimized_boosts = current_boosts.copy()

        # Apply boost rules based on query characteristics
        for rule_name, rule_func in self.boost_rules.items():
            boost_adjustments = rule_func(query, analysis)
            for field, boost_value in boost_adjustments.items():
                if boost_value > self.config["boost_threshold"]:
                    optimized_boosts[field] = (
                        optimized_boosts.get(field, 1.0) * boost_value
                    )

        # Domain-specific boost optimization
        domain_boosts = self._optimize_domain_boosts(query, analysis)
        for field, boost in domain_boosts.items():
            optimized_boosts[field] = optimized_boosts.get(field, 1.0) * boost

        # Query type specific boosts
        query_type_boosts = self._optimize_query_type_boosts(query, analysis)
        for field, boost in query_type_boosts.items():
            optimized_boosts[field] = optimized_boosts.get(field, 1.0) * boost

        # Only return if boosts were modified
        if optimized_boosts != current_boosts:
            optimized_query = query.copy()
            optimized_query["boost_fields"] = optimized_boosts
            optimized_query["boost_optimization"] = True
            return optimized_query

        return None

    async def _optimize_filters(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize filters for better performance"""

        if not self.config["enable_filter_optimization"]:
            return None

        current_filters = query.get("filters", {})
        if not current_filters:
            return None

        optimized_filters = current_filters.copy()
        filter_optimizations = []

        # Optimize filter order (more selective filters first)
        filter_selectivity = self._calculate_filter_selectivity(current_filters)
        if filter_selectivity:
            # Reorder filters by selectivity
            ordered_filters = {}
            for filter_name, selectivity in sorted(
                filter_selectivity.items(), key=lambda x: x[1]
            ):
                ordered_filters[filter_name] = current_filters[filter_name]
            optimized_filters = ordered_filters
            filter_optimizations.append("reordered_by_selectivity")

        # Combine compatible filters
        combined_filters = self._combine_compatible_filters(optimized_filters)
        if combined_filters != optimized_filters:
            optimized_filters = combined_filters
            filter_optimizations.append("combined_compatible_filters")

        # Remove redundant filters
        non_redundant_filters = self._remove_redundant_filters(optimized_filters)
        if non_redundant_filters != optimized_filters:
            optimized_filters = non_redundant_filters
            filter_optimizations.append("removed_redundant_filters")

        # Only return if filters were optimized
        if filter_optimizations:
            optimized_query = query.copy()
            optimized_query["filters"] = optimized_filters
            optimized_query["filter_optimizations"] = filter_optimizations
            return optimized_query

        return None

    async def _optimize_result_limits(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize result limits for better performance"""

        if not self.config["result_limit_optimization"]:
            return None

        query_complexity = analysis.get("complexity_score", 0.5)
        expected_precision = analysis.get("expected_precision", 0.5)

        # Calculate optimal result limit
        optimal_limit = self._calculate_optimal_result_limit(
            query_complexity, expected_precision
        )
        current_limit = query.get("result_limit", 50)

        if optimal_limit != current_limit:
            optimized_query = query.copy()
            optimized_query["result_limit"] = optimal_limit
            optimized_query[
                "limit_optimization_reason"
            ] = self._get_limit_optimization_reason(
                current_limit, optimal_limit, query_complexity, expected_precision
            )
            return optimized_query

        return None

    async def _optimize_caching(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize caching strategy"""

        query_cachability = self._assess_query_cachability(query, analysis)

        if query_cachability["should_cache"]:
            optimized_query = query.copy()
            optimized_query["cache_settings"] = {
                "enabled": True,
                "ttl": query_cachability["optimal_ttl"],
                "cache_key_strategy": query_cachability["key_strategy"],
                "cache_priority": query_cachability["priority"],
            }
            return optimized_query

        return None

    async def _optimize_performance(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Apply performance-specific optimizations"""

        if not self.config["enable_performance_optimization"]:
            return None

        performance_optimizations = []
        optimized_query = query.copy()

        # Parallel processing optimization
        if analysis.get("complexity_score", 0) > 0.7:
            optimized_query["enable_parallel_search"] = True
            performance_optimizations.append("parallel_processing")

        # Index optimization hints
        index_hints = self._generate_index_hints(query, analysis)
        if index_hints:
            optimized_query["index_hints"] = index_hints
            performance_optimizations.append("index_hints")

        # Memory optimization
        memory_settings = self._optimize_memory_usage(query, analysis)
        if memory_settings:
            optimized_query["memory_settings"] = memory_settings
            performance_optimizations.append("memory_optimization")

        # Early termination conditions
        early_termination = self._set_early_termination_conditions(query, analysis)
        if early_termination:
            optimized_query["early_termination"] = early_termination
            performance_optimizations.append("early_termination")

        if performance_optimizations:
            optimized_query["performance_optimizations"] = performance_optimizations
            return optimized_query

        return None

    async def _optimize_relevance(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimize for better relevance"""

        relevance_optimizations = []
        optimized_query = query.copy()

        # Adjust scoring algorithm based on query type
        scoring_adjustments = self._optimize_scoring_algorithm(query, analysis)
        if scoring_adjustments:
            optimized_query["scoring_adjustments"] = scoring_adjustments
            relevance_optimizations.append("scoring_algorithm")

        # Field weight optimization
        field_weights = self._optimize_field_weights(query, analysis)
        if field_weights:
            optimized_query["field_weights"] = field_weights
            relevance_optimizations.append("field_weights")

        # Proximity scoring optimization
        if analysis.get("multi_term_query"):
            proximity_settings = self._optimize_proximity_scoring(query, analysis)
            if proximity_settings:
                optimized_query["proximity_settings"] = proximity_settings
                relevance_optimizations.append("proximity_scoring")

        if relevance_optimizations:
            optimized_query["relevance_optimizations"] = relevance_optimizations
            return optimized_query

        return None

    def _analyze_query_optimization_needs(
        self, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze query to determine optimization needs"""

        original_query = query.get("original_query", "")
        terms = query.get("terms", [])

        analysis = {
            "complexity_score": self._calculate_query_complexity(query),
            "term_count": len(terms),
            "query_length": len(original_query),
            "has_operators": bool(query.get("operators", [])),
            "has_filters": bool(query.get("filters", {})),
            "query_type": query.get("query_type", "standard"),
            "multi_term_query": len(terms) > 1,
            "expected_precision": self._estimate_query_precision(query),
        }

        # Check for problematic patterns
        for pattern_name, pattern_regex in self.problematic_patterns.items():
            if re.match(pattern_regex, original_query, re.IGNORECASE):
                analysis[pattern_name] = True

        # Domain analysis
        analysis["domain_hints"] = self._extract_domain_hints(query)

        # Performance prediction
        analysis["predicted_performance"] = self._predict_query_performance(query)

        return analysis

    def _should_apply_optimization(
        self, strategy_name: str, analysis: Dict[str, Any]
    ) -> bool:
        """Determine if optimization strategy should be applied"""

        strategy_conditions = {
            "query_rewriting": analysis.get("too_broad")
            or analysis.get("typos_likely"),
            "term_expansion": analysis["term_count"] <= 3
            and not analysis.get("too_specific"),
            "boost_adjustment": analysis["complexity_score"] > 0.3,
            "filter_optimization": analysis["has_filters"],
            "result_limiting": True,  # Always consider result limiting
            "cache_optimization": analysis["complexity_score"] > 0.5,
            "performance_tuning": analysis.get("predicted_performance", 0) > 500,  # ms
            "relevance_tuning": analysis["multi_term_query"]
            or analysis["complexity_score"] > 0.4,
        }

        return strategy_conditions.get(strategy_name, False)

    def _build_rewriting_rules(self) -> Dict[str, Any]:
        """Build query rewriting rules"""

        return {
            # Fix common typos and variations
            r"\bframwork\b": "framework",
            r"\blibarary\b": "library",
            r"\bcomponet\b": "component",
            r"\bjavascirpt\b": "javascript",
            r"\btypescirpt\b": "typescript",
            # Expand abbreviations
            r"\bjs\b": "javascript",
            r"\bts\b": "typescript",
            r"\bapi\b": "api framework",
            r"\bui\b": "user interface",
            # Normalize technical terms
            r"\bnode\.?js\b": "node",
            r"\breact\.?js\b": "react",
            r"\bvue\.?js\b": "vue",
            # Handle stop word heavy queries
            r"^(the|a|an)\s+": "",  # Remove leading articles
        }

    def _build_expansion_rules(self) -> Dict[str, List[str]]:
        """Build term expansion rules"""

        return {
            "ui": ["interface", "frontend", "component", "design"],
            "api": ["service", "endpoint", "rest", "backend"],
            "fast": ["quick", "efficient", "optimized", "performance"],
            "simple": ["easy", "minimal", "basic", "straightforward"],
            "secure": ["safe", "auth", "encryption", "protected"],
            "modern": ["latest", "current", "new", "updated"],
            "database": ["db", "storage", "persistence", "data"],
            "testing": ["test", "qa", "validation", "verification"],
        }

    def _build_boost_rules(self) -> Dict[str, Any]:
        """Build boost adjustment rules"""

        return {
            "exact_match_boost": lambda query, analysis: {
                "name": 2.0 if analysis.get("query_type") == "exact" else 1.0
            },
            "category_boost": lambda query, analysis: {
                "category": 1.5 if "category" in query.get("requirements", {}) else 1.0
            },
            "technology_boost": lambda query, analysis: {
                "technology": 1.5
                if "technology" in query.get("requirements", {})
                else 1.0
            },
            "popularity_boost": lambda query, analysis: {
                "popularity": 1.3 if analysis.get("complexity_score", 0) < 0.5 else 1.0
            },
        }

    def _calculate_query_complexity(self, query: Dict[str, Any]) -> float:
        """Calculate query complexity score"""

        complexity = 0.0

        # Term count factor
        terms = query.get("terms", [])
        complexity += min(len(terms) / 10, 0.3)

        # Query length factor
        original_query = query.get("original_query", "")
        complexity += min(len(original_query) / 100, 0.2)

        # Operators factor
        operators = query.get("operators", [])
        complexity += len(operators) * 0.1

        # Filters factor
        filters = query.get("filters", {})
        complexity += len(filters) * 0.1

        # Boost fields factor
        boost_fields = query.get("boost_fields", {})
        complexity += len(boost_fields) * 0.05

        return min(complexity, 1.0)

    def _estimate_query_precision(self, query: Dict[str, Any]) -> float:
        """Estimate expected precision of query"""

        # Heuristic based on query characteristics
        precision = 0.5  # Base precision

        # More terms generally mean higher precision
        terms = query.get("terms", [])
        if len(terms) > 3:
            precision += 0.2
        elif len(terms) == 1:
            precision -= 0.2

        # Specific query types
        query_type = query.get("query_type", "standard")
        if query_type == "exact":
            precision += 0.3
        elif query_type == "fuzzy":
            precision -= 0.1

        # Filters increase precision
        if query.get("filters"):
            precision += 0.2

        # Requirements increase precision
        if query.get("requirements"):
            precision += 0.1

        return min(max(precision, 0.0), 1.0)

    def _predict_query_performance(self, query: Dict[str, Any]) -> int:
        """Predict query performance in milliseconds"""

        base_time = 100  # Base 100ms

        # Complexity factor
        complexity = self._calculate_query_complexity(query)
        complexity_time = complexity * 300

        # Term expansion factor
        expanded_terms = query.get("expanded_terms", [])
        expansion_time = len(expanded_terms) * 20

        # Filter factor
        filters = query.get("filters", {})
        filter_time = len(filters) * 50

        # Boost factor
        boost_fields = query.get("boost_fields", {})
        boost_time = len(boost_fields) * 10

        return int(
            base_time + complexity_time + expansion_time + filter_time + boost_time
        )

    def _extract_domain_hints(self, query: Dict[str, Any]) -> List[str]:
        """Extract domain hints from query"""

        hints = []
        query_text = query.get("original_query", "").lower()

        domain_keywords = {
            "frontend": ["ui", "interface", "react", "vue", "angular", "css", "html"],
            "backend": ["api", "server", "database", "node", "express", "django"],
            "mobile": ["mobile", "ios", "android", "native", "app"],
            "data": ["data", "analytics", "visualization", "ml", "ai"],
            "devops": ["docker", "kubernetes", "deploy", "ci/cd", "infrastructure"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in query_text for keyword in keywords):
                hints.append(domain)

        return hints

    def _handle_broad_query(self, query_text: str, query: Dict[str, Any]) -> str:
        """Handle overly broad queries"""

        # Add context based on requirements
        requirements = query.get("requirements", {})

        if "category" in requirements:
            return f"{query_text} {requirements['category']}"
        elif "technology" in requirements:
            return f"{query_text} {requirements['technology']}"
        else:
            # Add generic context
            return f"{query_text} library"

    def _handle_specific_query(self, query_text: str, query: Dict[str, Any]) -> str:
        """Handle overly specific queries"""

        # Simplify by removing less important words
        words = query_text.split()

        # Keep important words (nouns, adjectives, technical terms)
        important_words = []
        skip_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }

        for word in words:
            if word.lower() not in skip_words and len(word) > 2:
                important_words.append(word)

        # Keep first 8 important words
        simplified_words = important_words[:8]

        return " ".join(simplified_words)

    def _handle_typo_correction(self, query_text: str, query: Dict[str, Any]) -> str:
        """Handle potential typos in query"""

        # Simple typo correction (in production, use proper spell checker)
        typo_corrections = {
            "framwork": "framework",
            "libraray": "library",
            "javascirpt": "javascript",
            "typescirpt": "typescript",
            "compoent": "component",
            "databse": "database",
        }

        corrected_query = query_text
        for typo, correction in typo_corrections.items():
            corrected_query = re.sub(
                rf"\b{typo}\b", correction, corrected_query, flags=re.IGNORECASE
            )

        return corrected_query

    def _get_rewrite_reason(self, analysis: Dict[str, Any]) -> str:
        """Get reason for query rewriting"""

        reasons = []

        if analysis.get("too_broad"):
            reasons.append("query_too_broad")
        if analysis.get("too_specific"):
            reasons.append("query_too_specific")
        if analysis.get("typos_likely"):
            reasons.append("typo_correction")
        if analysis.get("stop_words_heavy"):
            reasons.append("stop_word_removal")

        return ", ".join(reasons) if reasons else "general_optimization"

    def _get_semantic_expansions(
        self, terms: List[str], analysis: Dict[str, Any]
    ) -> List[str]:
        """Get semantic expansions for terms"""

        expansions = []
        expansion_rules = self._build_expansion_rules()

        for term in terms:
            term_lower = term.lower()
            if term_lower in expansion_rules:
                expansions.extend(expansion_rules[term_lower])

        return expansions

    def _get_contextual_expansions(
        self, terms: List[str], analysis: Dict[str, Any]
    ) -> List[str]:
        """Get contextual expansions based on domain hints"""

        expansions = []
        domain_hints = analysis.get("domain_hints", [])

        for domain in domain_hints:
            if domain == "frontend":
                expansions.extend(["component", "ui", "interface"])
            elif domain == "backend":
                expansions.extend(["api", "server", "service"])
            elif domain == "mobile":
                expansions.extend(["app", "native", "mobile"])

        return expansions

    def _get_domain_specific_expansions(
        self, terms: List[str], analysis: Dict[str, Any]
    ) -> List[str]:
        """Get domain-specific term expansions"""

        expansions = []

        # Technology-specific expansions
        tech_expansions = {
            "react": ["jsx", "hooks", "component"],
            "vue": ["vuex", "composition", "directive"],
            "angular": ["typescript", "service", "directive"],
            "node": ["express", "npm", "module"],
            "python": ["pip", "module", "package"],
        }

        for term in terms:
            term_lower = term.lower()
            if term_lower in tech_expansions:
                expansions.extend(tech_expansions[term_lower])

        return expansions

    def _calculate_term_relevance(self, term: str, original_terms: List[str]) -> float:
        """Calculate relevance of expanded term"""

        relevance = 0.5  # Base relevance

        # Boost if term is related to original terms
        for original_term in original_terms:
            if self._are_terms_related(term, original_term):
                relevance += 0.3

        # Boost for common technical terms
        technical_terms = ["framework", "library", "component", "service", "api"]
        if term.lower() in technical_terms:
            relevance += 0.2

        return min(relevance, 1.0)

    def _are_terms_related(self, term1: str, term2: str) -> bool:
        """Check if two terms are semantically related"""

        # Simple related term check (in production, use embeddings)
        related_groups = [
            ["ui", "interface", "frontend", "component"],
            ["api", "service", "backend", "server"],
            ["database", "storage", "data", "persistence"],
            ["test", "testing", "qa", "validation"],
        ]

        term1_lower = term1.lower()
        term2_lower = term2.lower()

        for group in related_groups:
            if term1_lower in group and term2_lower in group:
                return True

        return False

    def _optimize_domain_boosts(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Optimize boosts based on domain hints"""

        boosts = {}
        domain_hints = analysis.get("domain_hints", [])

        for domain in domain_hints:
            if domain == "frontend":
                boosts.update({"category": 1.3, "features": 1.2})
            elif domain == "backend":
                boosts.update({"technology": 1.3, "performance_metrics": 1.2})
            elif domain == "mobile":
                boosts.update({"platform_support": 1.4, "features": 1.2})

        return boosts

    def _optimize_query_type_boosts(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Optimize boosts based on query type"""

        boosts = {}
        query_type = analysis.get("query_type", "standard")

        if query_type == "exact":
            boosts["name"] = 2.0
        elif query_type == "semantic":
            boosts["description"] = 1.5
        elif query_type == "fuzzy":
            boosts["tags"] = 1.3

        return boosts

    def _calculate_filter_selectivity(
        self, filters: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate selectivity of filters (lower = more selective)"""

        # Estimated selectivity based on filter type
        selectivity_estimates = {
            "category": 0.2,  # Very selective
            "technology": 0.3,  # Selective
            "license": 0.4,  # Moderately selective
            "tags": 0.6,  # Less selective
            "popularity": 0.7,  # Least selective
            "date_range": 0.5,  # Moderately selective
        }

        filter_selectivity = {}
        for filter_name in filters:
            filter_selectivity[filter_name] = selectivity_estimates.get(
                filter_name, 0.5
            )

        return filter_selectivity

    def _combine_compatible_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine compatible filters for better performance"""

        # Simple combination logic (in production, use more sophisticated approach)
        combined = filters.copy()

        # Combine range filters
        range_filters = {}
        non_range_filters = {}

        for filter_name, filter_value in filters.items():
            if isinstance(filter_value, dict) and (
                "min" in filter_value or "max" in filter_value
            ):
                range_filters[filter_name] = filter_value
            else:
                non_range_filters[filter_name] = filter_value

        # If multiple range filters, combine them
        if len(range_filters) > 1:
            combined_ranges = {"combined_range": range_filters}
            combined = {**non_range_filters, **combined_ranges}

        return combined

    def _remove_redundant_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant filters"""

        # Simple redundancy removal
        non_redundant = {}

        for filter_name, filter_value in filters.items():
            # Skip empty filters
            if not filter_value:
                continue

            # Skip redundant category filters if technology is specified
            if filter_name == "category" and "technology" in filters:
                # Keep if they're not redundant
                if not self._is_category_redundant_with_technology(
                    filter_value, filters["technology"]
                ):
                    non_redundant[filter_name] = filter_value
            else:
                non_redundant[filter_name] = filter_value

        return non_redundant

    def _is_category_redundant_with_technology(
        self, category: str, technology: str
    ) -> bool:
        """Check if category filter is redundant with technology filter"""

        # Simple redundancy check
        redundant_pairs = [
            ("ui framework", "react"),
            ("ui framework", "vue"),
            ("ui framework", "angular"),
            ("backend framework", "node"),
            ("backend framework", "express"),
        ]

        return (category.lower(), technology.lower()) in redundant_pairs

    def _calculate_optimal_result_limit(
        self, complexity: float, precision: float
    ) -> int:
        """Calculate optimal result limit"""

        base_limit = 20

        # Adjust based on complexity
        if complexity > 0.7:
            limit = base_limit + 30  # More results for complex queries
        elif complexity < 0.3:
            limit = base_limit - 10  # Fewer results for simple queries
        else:
            limit = base_limit

        # Adjust based on precision
        if precision > 0.8:
            limit = int(limit * 0.8)  # Fewer results for high precision queries
        elif precision < 0.4:
            limit = int(limit * 1.2)  # More results for low precision queries

        return max(10, min(limit, 100))  # Clamp between 10 and 100

    def _get_limit_optimization_reason(
        self,
        current_limit: int,
        optimal_limit: int,
        complexity: float,
        precision: float,
    ) -> str:
        """Get reason for limit optimization"""

        reasons = []

        if optimal_limit > current_limit:
            if complexity > 0.7:
                reasons.append("increased_for_complex_query")
            if precision < 0.4:
                reasons.append("increased_for_low_precision")
        else:
            if precision > 0.8:
                reasons.append("decreased_for_high_precision")
            if complexity < 0.3:
                reasons.append("decreased_for_simple_query")

        return ", ".join(reasons) if reasons else "general_optimization"

    def _assess_query_cachability(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess if and how query should be cached"""

        cachability = {
            "should_cache": False,
            "optimal_ttl": 300,  # 5 minutes default
            "key_strategy": "full_query",
            "priority": "normal",
        }

        # Cache if query is complex or commonly used
        if analysis["complexity_score"] > 0.5:
            cachability["should_cache"] = True
            cachability["optimal_ttl"] = 1800  # 30 minutes for complex queries
            cachability["priority"] = "high"

        # Cache popular query patterns
        query_text = query.get("original_query", "").lower()
        if any(
            pattern in query_text for pattern in ["react", "vue", "angular", "popular"]
        ):
            cachability["should_cache"] = True
            cachability["optimal_ttl"] = 3600  # 1 hour for popular queries

        return cachability

    def _generate_index_hints(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate index optimization hints"""

        hints = {}

        # Suggest primary index based on query type
        if analysis.get("has_filters"):
            hints["primary_index"] = "filtered_search"
        elif analysis["term_count"] > 3:
            hints["primary_index"] = "full_text_search"
        else:
            hints["primary_index"] = "simple_search"

        # Suggest secondary indexes based on domain
        domain_hints = analysis.get("domain_hints", [])
        if "frontend" in domain_hints:
            hints["secondary_index"] = "category_technology"
        elif "backend" in domain_hints:
            hints["secondary_index"] = "technology_performance"

        return hints

    def _optimize_memory_usage(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize memory usage settings"""

        settings = {}

        # Adjust based on query complexity
        complexity = analysis["complexity_score"]

        if complexity > 0.8:
            settings["memory_limit"] = "high"
            settings["batch_size"] = 1000
        elif complexity < 0.3:
            settings["memory_limit"] = "low"
            settings["batch_size"] = 100
        else:
            settings["memory_limit"] = "medium"
            settings["batch_size"] = 500

        return settings

    def _set_early_termination_conditions(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set early termination conditions"""

        conditions = {}

        # Set based on expected precision
        precision = analysis.get("expected_precision", 0.5)

        if precision > 0.8:
            conditions["min_results"] = 5
            conditions["score_threshold"] = 0.8
        elif precision < 0.3:
            conditions["min_results"] = 20
            conditions["score_threshold"] = 0.3
        else:
            conditions["min_results"] = 10
            conditions["score_threshold"] = 0.5

        return conditions

    def _optimize_scoring_algorithm(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize scoring algorithm parameters"""

        adjustments = {}

        query_type = analysis.get("query_type", "standard")

        if query_type == "exact":
            adjustments["exact_match_weight"] = 2.0
            adjustments["fuzzy_match_weight"] = 0.5
        elif query_type == "fuzzy":
            adjustments["exact_match_weight"] = 1.0
            adjustments["fuzzy_match_weight"] = 1.5
        elif query_type == "semantic":
            adjustments["semantic_weight"] = 1.5
            adjustments["keyword_weight"] = 0.8

        return adjustments

    def _optimize_field_weights(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Optimize field weights for scoring"""

        weights = {}

        # Base weights
        base_weights = {
            "name": 1.0,
            "description": 0.8,
            "tags": 0.9,
            "category": 0.7,
            "technology": 0.7,
        }

        # Adjust based on query characteristics
        if analysis["term_count"] == 1:
            # Single term queries - boost name matching
            weights["name"] = base_weights["name"] * 1.5
        elif analysis["term_count"] > 5:
            # Multi-term queries - boost description matching
            weights["description"] = base_weights["description"] * 1.3

        # Domain-specific adjustments
        domain_hints = analysis.get("domain_hints", [])
        if "frontend" in domain_hints:
            weights["category"] = base_weights["category"] * 1.2

        return {**base_weights, **weights}

    def _optimize_proximity_scoring(
        self, query: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize proximity scoring for multi-term queries"""

        settings = {}

        term_count = analysis["term_count"]

        if term_count > 1:
            settings["enable_proximity"] = True
            settings["proximity_boost"] = 1.2
            settings["max_distance"] = min(term_count * 2, 10)

            if term_count > 5:
                # For very long queries, be more lenient with proximity
                settings["proximity_boost"] = 1.1
                settings["max_distance"] = 15

        return settings

    def _update_optimization_stats(
        self, applied_optimizations: List[str], optimization_time: float
    ):
        """Update optimization statistics"""

        self.optimization_stats["queries_optimized"] += 1

        if applied_optimizations:
            self.optimization_stats["successful_optimizations"] += 1
        else:
            self.optimization_stats["failed_optimizations"] += 1

        # Update average improvement time
        current_avg = self.optimization_stats["avg_improvement_ms"]
        total_queries = self.optimization_stats["queries_optimized"]

        new_avg = (
            (current_avg * (total_queries - 1)) + optimization_time
        ) / total_queries
        self.optimization_stats["avg_improvement_ms"] = new_avg
