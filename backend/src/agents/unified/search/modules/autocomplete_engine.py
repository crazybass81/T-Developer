"""
Autocomplete Engine Module
Advanced autocomplete and query suggestion system
"""

import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class AutocompleteEngine:
    """Advanced autocomplete engine with intelligent suggestions"""

    def __init__(self):
        # Autocomplete data structures
        self.trie = AutocompleteTrie()
        self.query_history = []
        self.popular_terms = Counter()
        self.contextual_suggestions = defaultdict(list)

        # Suggestion sources
        self.suggestion_sources = {
            "popular_queries": self._get_popular_query_suggestions,
            "semantic_expansion": self._get_semantic_suggestions,
            "category_based": self._get_category_suggestions,
            "technology_based": self._get_technology_suggestions,
            "completion_based": self._get_completion_suggestions,
            "contextual": self._get_contextual_suggestions,
            "trending": self._get_trending_suggestions,
            "personalized": self._get_personalized_suggestions,
        }

        # Configuration
        self.config = {
            "max_suggestions": 10,
            "min_query_length": 2,
            "enable_fuzzy_matching": True,
            "fuzzy_threshold": 0.7,
            "popularity_weight": 0.3,
            "recency_weight": 0.2,
            "semantic_weight": 0.25,
            "contextual_weight": 0.25,
            "suggestion_cache_ttl": 3600,  # 1 hour
        }

        # Pre-built suggestion datasets
        self.component_terms = self._build_component_terms()
        self.technology_terms = self._build_technology_terms()
        self.action_terms = self._build_action_terms()
        self.quality_terms = self._build_quality_terms()

        # Suggestion cache
        self.suggestion_cache = {}
        self.cache_timestamps = {}

        # Initialize with common terms
        self._initialize_common_suggestions()

    async def generate_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate autocomplete suggestions for partial query"""

        if len(partial_query) < self.config["min_query_length"]:
            return []

        # Check cache first
        cache_key = self._generate_cache_key(partial_query, context)
        cached_suggestions = self._get_cached_suggestions(cache_key)
        if cached_suggestions:
            return cached_suggestions

        # Collect suggestions from different sources
        all_suggestions = []

        for source_name, source_func in self.suggestion_sources.items():
            try:
                suggestions = await source_func(partial_query, context)
                for suggestion in suggestions:
                    all_suggestions.append(
                        {
                            "text": suggestion,
                            "source": source_name,
                            "score": self._calculate_suggestion_score(
                                suggestion, partial_query, source_name, context
                            ),
                        }
                    )
            except Exception as e:
                # Continue with other sources if one fails
                continue

        # Deduplicate and rank suggestions
        unique_suggestions = self._deduplicate_suggestions(all_suggestions)
        ranked_suggestions = self._rank_suggestions(unique_suggestions, partial_query, context)

        # Format final suggestions
        final_suggestions = [
            s["text"] for s in ranked_suggestions[: self.config["max_suggestions"]]
        ]

        # Cache the results
        self._cache_suggestions(cache_key, final_suggestions)

        return final_suggestions

    async def _get_popular_query_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get suggestions based on popular historical queries"""

        suggestions = []
        partial_lower = partial_query.lower()

        # Search through historical queries
        for query in self.query_history:
            if query["text"].lower().startswith(partial_lower):
                suggestions.append(query["text"])

        # Search through popular terms
        for term, frequency in self.popular_terms.most_common(50):
            if term.lower().startswith(partial_lower):
                suggestions.append(term)

        return suggestions[:8]

    async def _get_semantic_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get semantically related suggestions"""

        suggestions = []
        partial_lower = partial_query.lower()

        # Get semantic expansions
        semantic_terms = self._get_semantic_expansions(partial_query)

        for term in semantic_terms:
            if term.lower().startswith(partial_lower) or partial_lower in term.lower():
                suggestions.append(term)

        # Generate compound suggestions
        if " " not in partial_query:
            # Single term - suggest combinations
            for category in ["framework", "library", "component", "tool"]:
                if partial_lower in category or category.startswith(partial_lower):
                    suggestions.append(f"{partial_query} {category}")

        return suggestions[:6]

    async def _get_category_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get category-based suggestions"""

        suggestions = []
        partial_lower = partial_query.lower()

        # Category-specific terms
        category_terms = {
            "ui": ["ui framework", "ui component", "ui library", "user interface"],
            "api": ["api framework", "rest api", "api client", "api wrapper"],
            "data": [
                "data visualization",
                "data processing",
                "database",
                "data analysis",
            ],
            "test": [
                "testing framework",
                "test runner",
                "unit testing",
                "test automation",
            ],
            "auth": ["authentication", "authorization", "oauth", "jwt"],
            "performance": ["optimization", "caching", "monitoring", "profiling"],
        }

        for prefix, terms in category_terms.items():
            if partial_lower.startswith(prefix) or prefix.startswith(partial_lower):
                for term in terms:
                    if term.startswith(partial_lower):
                        suggestions.append(term)

        return suggestions[:5]

    async def _get_technology_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get technology-specific suggestions"""

        suggestions = []
        partial_lower = partial_query.lower()

        # Technology combinations
        tech_combinations = {
            "react": ["react component", "react hooks", "react router", "react native"],
            "vue": ["vue component", "vuex", "vue router", "vuetify"],
            "angular": ["angular component", "angular material", "angular forms"],
            "node": ["node.js framework", "express", "fastify", "node modules"],
            "python": ["python library", "django", "flask", "fastapi"],
            "javascript": ["javascript library", "js framework", "npm package"],
        }

        for tech, combinations in tech_combinations.items():
            if partial_lower.startswith(tech) or tech.startswith(partial_lower):
                for combo in combinations:
                    if combo.startswith(partial_lower):
                        suggestions.append(combo)

        # Technology-specific terms
        for term in self.technology_terms:
            if term.lower().startswith(partial_lower):
                suggestions.append(term)

        return suggestions[:6]

    async def _get_completion_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get completion-based suggestions using trie"""

        suggestions = self.trie.get_completions(partial_query.lower(), limit=8)
        return suggestions

    async def _get_contextual_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get context-aware suggestions"""

        suggestions = []

        if not context:
            return suggestions

        # Domain-based suggestions
        domain = context.get("domain")
        if domain:
            domain_suggestions = self.contextual_suggestions.get(domain, [])
            partial_lower = partial_query.lower()

            for suggestion in domain_suggestions:
                if suggestion.lower().startswith(partial_lower):
                    suggestions.append(suggestion)

        # Project type suggestions
        project_type = context.get("project_type")
        if project_type:
            project_suggestions = self._get_project_type_suggestions(project_type, partial_query)
            suggestions.extend(project_suggestions)

        # User preference suggestions
        user_prefs = context.get("user_preferences", {})
        if user_prefs:
            pref_suggestions = self._get_preference_based_suggestions(user_prefs, partial_query)
            suggestions.extend(pref_suggestions)

        return suggestions[:5]

    async def _get_trending_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get trending query suggestions"""

        suggestions = []
        partial_lower = partial_query.lower()

        # Mock trending data (in production, get from analytics)
        trending_queries = [
            "react hooks",
            "vue 3",
            "next.js",
            "fastapi",
            "docker",
            "kubernetes",
            "microservices",
            "graphql",
            "mongodb",
        ]

        for query in trending_queries:
            if query.lower().startswith(partial_lower):
                suggestions.append(query)

        return suggestions[:4]

    async def _get_personalized_suggestions(
        self, partial_query: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get personalized suggestions based on user history"""

        suggestions = []

        if not context or "user_history" not in context:
            return suggestions

        user_history = context["user_history"]
        partial_lower = partial_query.lower()

        # Suggestions based on frequently searched categories
        frequent_categories = user_history.get("frequent_categories", [])
        for category in frequent_categories:
            category_query = f"{partial_query} {category}"
            if len(category_query) > len(partial_query):
                suggestions.append(category_query)

        # Suggestions based on previous searches
        previous_searches = user_history.get("previous_searches", [])
        for search in previous_searches:
            if search.lower().startswith(partial_lower) and search != partial_query:
                suggestions.append(search)

        return suggestions[:4]

    def add_query_to_history(self, query: str, result_count: int = 0):
        """Add a query to the autocomplete history"""

        query_data = {
            "text": query,
            "timestamp": datetime.now(),
            "result_count": result_count,
            "frequency": 1,
        }

        # Check if query already exists
        existing_query = None
        for i, q in enumerate(self.query_history):
            if q["text"].lower() == query.lower():
                existing_query = i
                break

        if existing_query is not None:
            # Update existing query
            self.query_history[existing_query]["frequency"] += 1
            self.query_history[existing_query]["timestamp"] = datetime.now()
        else:
            # Add new query
            self.query_history.append(query_data)

        # Update popular terms
        terms = query.lower().split()
        for term in terms:
            self.popular_terms[term] += 1

        # Add to trie
        self.trie.insert(query.lower())

        # Cleanup old history
        self._cleanup_old_history()

    def learn_from_component_data(self, components: List[Dict[str, Any]]):
        """Learn suggestions from component data"""

        for component in components:
            # Add component names
            name = component.get("name", "")
            if name:
                self.trie.insert(name.lower())
                self.popular_terms[name.lower()] += 1

            # Add categories
            category = component.get("category", "")
            if category:
                self.trie.insert(category.lower())
                self.popular_terms[category.lower()] += 1

            # Add technologies
            technology = component.get("technology", "")
            if technology:
                self.trie.insert(technology.lower())
                self.popular_terms[technology.lower()] += 1

            # Add tags
            for tag in component.get("tags", []):
                self.trie.insert(tag.lower())
                self.popular_terms[tag.lower()] += 1

    def _calculate_suggestion_score(
        self,
        suggestion: str,
        partial_query: str,
        source: str,
        context: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate score for a suggestion"""

        score = 0.0

        # Base score from source type
        source_weights = {
            "popular_queries": 0.8,
            "completion_based": 0.7,
            "semantic_expansion": 0.6,
            "category_based": 0.65,
            "technology_based": 0.7,
            "contextual": 0.75,
            "trending": 0.6,
            "personalized": 0.85,
        }

        score += source_weights.get(source, 0.5)

        # Popularity factor
        suggestion_lower = suggestion.lower()
        popularity = self.popular_terms.get(suggestion_lower, 0)
        popularity_score = min(math.log10(popularity + 1) / 4, 1.0)
        score += popularity_score * self.config["popularity_weight"]

        # Prefix matching factor
        if suggestion_lower.startswith(partial_query.lower()):
            score += 0.3  # Boost for prefix matches

        # Length factor (prefer shorter, more concise suggestions)
        length_factor = max(1.0 - (len(suggestion) / 100), 0.3)
        score += length_factor * 0.1

        # Recency factor
        recent_score = self._calculate_recency_score(suggestion)
        score += recent_score * self.config["recency_weight"]

        # Context relevance factor
        if context:
            context_score = self._calculate_context_relevance(suggestion, context)
            score += context_score * self.config["contextual_weight"]

        return score

    def _deduplicate_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate suggestions, keeping the highest scored"""

        unique_suggestions = {}

        for suggestion in suggestions:
            text = suggestion["text"].lower()
            if (
                text not in unique_suggestions
                or suggestion["score"] > unique_suggestions[text]["score"]
            ):
                unique_suggestions[text] = suggestion

        return list(unique_suggestions.values())

    def _rank_suggestions(
        self,
        suggestions: List[Dict[str, Any]],
        partial_query: str,
        context: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Rank suggestions by their calculated scores"""

        # Sort by score (descending)
        ranked = sorted(suggestions, key=lambda x: x["score"], reverse=True)

        # Apply diversity factor to avoid too many similar suggestions
        diversified = self._apply_diversity_factor(ranked, partial_query)

        return diversified

    def _apply_diversity_factor(
        self, suggestions: List[Dict[str, Any]], partial_query: str
    ) -> List[Dict[str, Any]]:
        """Apply diversity to avoid too many similar suggestions"""

        diverse_suggestions = []
        used_prefixes = set()

        for suggestion in suggestions:
            suggestion_text = suggestion["text"]

            # Extract first meaningful word
            first_word = suggestion_text.split()[0] if suggestion_text.split() else suggestion_text

            # Skip if we already have too many suggestions with same prefix
            prefix_count = sum(1 for prefix in used_prefixes if prefix == first_word)

            if prefix_count < 2:  # Max 2 suggestions per prefix
                diverse_suggestions.append(suggestion)
                used_prefixes.add(first_word)

            if len(diverse_suggestions) >= self.config["max_suggestions"]:
                break

        return diverse_suggestions

    def _get_semantic_expansions(self, query: str) -> List[str]:
        """Get semantic expansions for a query"""

        expansions = []
        query_lower = query.lower()

        # Synonym mappings
        synonyms = {
            "ui": ["interface", "frontend", "view", "component"],
            "api": ["service", "endpoint", "rest", "backend"],
            "fast": ["quick", "rapid", "efficient", "optimized"],
            "simple": ["easy", "basic", "minimal", "straightforward"],
            "secure": ["safe", "protected", "encrypted", "auth"],
            "modern": ["latest", "current", "new", "updated"],
        }

        # Related terms
        related_terms = {
            "component": ["widget", "element", "module", "part"],
            "framework": ["library", "toolkit", "platform", "solution"],
            "database": ["db", "storage", "persistence", "data"],
            "testing": ["test", "qa", "validation", "verification"],
        }

        # Apply synonym and related term expansion
        for term, expansion_list in {**synonyms, **related_terms}.items():
            if term in query_lower:
                for expansion in expansion_list:
                    expanded_query = query_lower.replace(term, expansion)
                    expansions.append(expanded_query)

        return expansions

    def _get_project_type_suggestions(self, project_type: str, partial_query: str) -> List[str]:
        """Get suggestions based on project type"""

        project_suggestions = {
            "web_app": [
                "react component",
                "vue framework",
                "css library",
                "routing",
                "state management",
                "ui framework",
            ],
            "mobile_app": [
                "react native",
                "flutter",
                "ionic",
                "mobile ui",
                "navigation",
                "native modules",
            ],
            "api_server": [
                "express",
                "fastapi",
                "rest framework",
                "database orm",
                "authentication",
                "middleware",
            ],
            "data_app": [
                "data visualization",
                "analytics",
                "charting library",
                "data processing",
                "machine learning",
            ],
        }

        suggestions = project_suggestions.get(project_type, [])
        partial_lower = partial_query.lower()

        return [s for s in suggestions if s.startswith(partial_lower)]

    def _get_preference_based_suggestions(
        self, preferences: Dict[str, Any], partial_query: str
    ) -> List[str]:
        """Get suggestions based on user preferences"""

        suggestions = []
        partial_lower = partial_query.lower()

        # Technology preferences
        preferred_techs = preferences.get("technologies", [])
        for tech in preferred_techs:
            tech_query = f"{partial_query} {tech}"
            if tech_query.lower().startswith(partial_lower):
                suggestions.append(tech_query)

        # Category preferences
        preferred_categories = preferences.get("categories", [])
        for category in preferred_categories:
            cat_query = f"{partial_query} {category}"
            if cat_query.lower().startswith(partial_lower):
                suggestions.append(cat_query)

        return suggestions

    def _calculate_recency_score(self, suggestion: str) -> float:
        """Calculate recency score for suggestion"""

        # Find most recent usage of this suggestion
        most_recent = None
        for query in self.query_history:
            if suggestion.lower() in query["text"].lower():
                if most_recent is None or query["timestamp"] > most_recent:
                    most_recent = query["timestamp"]

        if most_recent is None:
            return 0.3  # Default score for new suggestions

        # Calculate recency score
        days_ago = (datetime.now() - most_recent).days

        if days_ago <= 1:
            return 1.0
        elif days_ago <= 7:
            return 0.8
        elif days_ago <= 30:
            return 0.6
        else:
            return 0.4

    def _calculate_context_relevance(self, suggestion: str, context: Dict[str, Any]) -> float:
        """Calculate how relevant suggestion is to context"""

        relevance = 0.0
        suggestion_lower = suggestion.lower()

        # Domain relevance
        domain = context.get("domain", "")
        domain_keywords = {
            "frontend": ["ui", "component", "react", "vue", "angular", "css"],
            "backend": ["api", "server", "database", "framework", "service"],
            "mobile": ["mobile", "app", "native", "ios", "android"],
            "data": ["data", "analytics", "visualization", "ml", "ai"],
        }

        if domain in domain_keywords:
            keywords = domain_keywords[domain]
            matches = sum(1 for keyword in keywords if keyword in suggestion_lower)
            relevance += (matches / len(keywords)) * 0.4

        # Technology stack relevance
        tech_stack = context.get("tech_stack", [])
        for tech in tech_stack:
            if tech.lower() in suggestion_lower:
                relevance += 0.3
                break

        # Project phase relevance
        project_phase = context.get("project_phase", "")
        phase_keywords = {
            "planning": ["architecture", "design", "framework", "planning"],
            "development": ["component", "library", "tool", "implementation"],
            "testing": ["test", "qa", "validation", "automation"],
            "deployment": ["deploy", "production", "monitoring", "ci/cd"],
        }

        if project_phase in phase_keywords:
            keywords = phase_keywords[project_phase]
            if any(keyword in suggestion_lower for keyword in keywords):
                relevance += 0.3

        return min(relevance, 1.0)

    def _build_component_terms(self) -> List[str]:
        """Build list of component-related terms"""

        return [
            "component",
            "widget",
            "element",
            "module",
            "plugin",
            "addon",
            "extension",
            "package",
            "library",
            "framework",
            "toolkit",
            "suite",
            "collection",
            "bundle",
            "utility",
        ]

    def _build_technology_terms(self) -> List[str]:
        """Build list of technology terms"""

        return [
            "react",
            "vue",
            "angular",
            "svelte",
            "node",
            "express",
            "fastapi",
            "django",
            "flask",
            "spring",
            "laravel",
            "javascript",
            "typescript",
            "python",
            "java",
            "go",
            "rust",
            "php",
            "ruby",
            "kotlin",
            "swift",
        ]

    def _build_action_terms(self) -> List[str]:
        """Build list of action terms"""

        return [
            "find",
            "search",
            "get",
            "fetch",
            "load",
            "create",
            "build",
            "generate",
            "make",
            "develop",
            "implement",
            "add",
            "install",
            "setup",
            "configure",
            "optimize",
        ]

    def _build_quality_terms(self) -> List[str]:
        """Build list of quality-related terms"""

        return [
            "fast",
            "quick",
            "efficient",
            "optimized",
            "lightweight",
            "secure",
            "safe",
            "reliable",
            "stable",
            "modern",
            "popular",
            "trending",
            "best",
            "top",
            "recommended",
            "simple",
            "easy",
            "minimal",
            "clean",
            "elegant",
        ]

    def _initialize_common_suggestions(self):
        """Initialize with common search suggestions"""

        common_suggestions = [
            "react components",
            "vue framework",
            "angular library",
            "ui components",
            "css framework",
            "javascript library",
            "node.js framework",
            "express middleware",
            "database orm",
            "authentication library",
            "testing framework",
            "api client",
            "data visualization",
            "chart library",
            "form validation",
            "state management",
            "routing library",
            "http client",
        ]

        for suggestion in common_suggestions:
            self.trie.insert(suggestion.lower())
            self.popular_terms[suggestion.lower()] += 5  # Boost common terms

    def _generate_cache_key(self, partial_query: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for suggestions"""

        key_parts = [partial_query.lower()]

        if context:
            if "domain" in context:
                key_parts.append(f"domain:{context['domain']}")
            if "project_type" in context:
                key_parts.append(f"type:{context['project_type']}")

        return "|".join(key_parts)

    def _get_cached_suggestions(self, cache_key: str) -> Optional[List[str]]:
        """Get cached suggestions if still valid"""

        if cache_key not in self.suggestion_cache:
            return None

        # Check if cache is expired
        cache_time = self.cache_timestamps.get(cache_key)
        if cache_time:
            age_seconds = (datetime.now() - cache_time).total_seconds()
            if age_seconds > self.config["suggestion_cache_ttl"]:
                del self.suggestion_cache[cache_key]
                del self.cache_timestamps[cache_key]
                return None

        return self.suggestion_cache[cache_key]

    def _cache_suggestions(self, cache_key: str, suggestions: List[str]):
        """Cache suggestions with timestamp"""

        self.suggestion_cache[cache_key] = suggestions
        self.cache_timestamps[cache_key] = datetime.now()

        # Cleanup old cache entries
        self._cleanup_suggestion_cache()

    def _cleanup_old_history(self):
        """Remove old query history entries"""

        # Keep only recent queries (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        self.query_history = [q for q in self.query_history if q["timestamp"] > cutoff_date]

        # Keep only top 1000 queries to manage memory
        if len(self.query_history) > 1000:
            self.query_history = sorted(
                self.query_history, key=lambda x: x["frequency"], reverse=True
            )[:1000]

    def _cleanup_suggestion_cache(self):
        """Clean up expired cache entries"""

        current_time = datetime.now()
        expired_keys = []

        for cache_key, cache_time in self.cache_timestamps.items():
            age_seconds = (current_time - cache_time).total_seconds()
            if age_seconds > self.config["suggestion_cache_ttl"]:
                expired_keys.append(cache_key)

        for key in expired_keys:
            self.suggestion_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)


class AutocompleteTrie:
    """Trie data structure for efficient autocomplete"""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        """Insert word into trie"""

        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end_of_word = True
        node.frequency += 1

    def get_completions(self, prefix: str, limit: int = 10) -> List[str]:
        """Get completions for given prefix"""

        node = self.root

        # Navigate to prefix
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect completions
        completions = []
        self._collect_completions(node, prefix, completions, limit)

        # Sort by frequency
        completions.sort(key=lambda x: x[1], reverse=True)

        return [word for word, freq in completions[:limit]]

    def _collect_completions(
        self,
        node: "TrieNode",
        current_word: str,
        completions: List[Tuple[str, int]],
        limit: int,
    ):
        """Recursively collect completions"""

        if len(completions) >= limit:
            return

        if node.is_end_of_word:
            completions.append((current_word, node.frequency))

        for char, child_node in node.children.items():
            self._collect_completions(child_node, current_word + char, completions, limit)


class TrieNode:
    """Node in the trie structure"""

    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0
