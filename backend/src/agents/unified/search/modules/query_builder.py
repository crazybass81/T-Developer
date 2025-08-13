"""
Query Builder Module
Builds optimized search queries from user input
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime


class QueryBuilder:
    """Builds and optimizes search queries"""

    def __init__(self):
        self.stop_words = {
            "the",
            "is",
            "at",
            "which",
            "on",
            "and",
            "a",
            "to",
            "for",
            "of",
            "with",
            "in",
            "by",
            "from",
            "as",
            "an",
            "are",
            "was",
        }
        self.synonyms = self._build_synonyms()

    async def build(
        self, query: str, requirements: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build optimized search query"""

        # Parse and clean query
        terms = self._parse_query(query)
        cleaned_terms = self._clean_terms(terms)

        # Expand terms with synonyms
        expanded_terms = self._expand_synonyms(cleaned_terms)

        # Extract operators and modifiers
        operators = self._extract_operators(query)

        # Build query object
        built_query = {
            "original_query": query,
            "terms": cleaned_terms,
            "expanded_terms": expanded_terms,
            "operators": operators,
            "filters": filters,
            "requirements": requirements,
            "query_type": self._determine_query_type(query, requirements),
            "boost_fields": self._determine_boost_fields(requirements),
            "fuzzy_threshold": self._calculate_fuzzy_threshold(query),
            "created_at": datetime.now().isoformat(),
        }

        return built_query

    def _parse_query(self, query: str) -> List[str]:
        """Parse query into terms"""

        # Handle quoted phrases
        quoted_phrases = re.findall(r'"([^"]*)"', query)

        # Remove quoted phrases from query for word extraction
        query_without_quotes = re.sub(r'"[^"]*"', "", query)

        # Extract individual words
        words = re.findall(r"\b\w+\b", query_without_quotes.lower())

        # Combine phrases and words
        terms = quoted_phrases + words

        return terms

    def _clean_terms(self, terms: List[str]) -> List[str]:
        """Clean and filter terms"""

        cleaned = []

        for term in terms:
            # Remove stop words (except for quoted phrases)
            if len(term.split()) > 1 or term.lower() not in self.stop_words:
                # Remove special characters but keep spaces for phrases
                cleaned_term = re.sub(r"[^\w\s-]", "", term)
                if cleaned_term and len(cleaned_term) > 1:
                    cleaned.append(cleaned_term)

        return cleaned

    def _expand_synonyms(self, terms: List[str]) -> List[str]:
        """Expand terms with synonyms"""

        expanded = []

        for term in terms:
            expanded.append(term)

            # Add synonyms
            for synonym_group in self.synonyms:
                if term.lower() in synonym_group:
                    for synonym in synonym_group:
                        if synonym != term.lower() and synonym not in expanded:
                            expanded.append(synonym)

        return expanded

    def _extract_operators(self, query: str) -> List[str]:
        """Extract search operators"""

        operators = []

        # Boolean operators
        if " AND " in query.upper():
            operators.append("AND")
        if " OR " in query.upper():
            operators.append("OR")
        if " NOT " in query.upper():
            operators.append("NOT")

        # Field operators
        field_operators = re.findall(r"(\w+):", query)
        operators.extend(field_operators)

        # Wildcard operators
        if "*" in query:
            operators.append("WILDCARD")
        if "?" in query:
            operators.append("FUZZY")

        return operators

    def _determine_query_type(self, query: str, requirements: Dict) -> str:
        """Determine the type of search query"""

        # Exact match query
        if query.startswith('"') and query.endswith('"'):
            return "exact"

        # Boolean query
        if any(op in query.upper() for op in ["AND", "OR", "NOT"]):
            return "boolean"

        # Field query
        if ":" in query:
            return "field"

        # Semantic query (based on requirements)
        if requirements and len(str(requirements)) > 100:
            return "semantic"

        # Fuzzy query
        if "~" in query or "?" in query:
            return "fuzzy"

        return "standard"

    def _determine_boost_fields(self, requirements: Dict) -> Dict[str, float]:
        """Determine which fields to boost based on requirements"""

        boost_fields = {
            "name": 2.0,  # Always boost name matches
            "tags": 1.5,  # Tags are important
            "description": 1.2,  # Description has good context
        }

        # Boost based on requirements
        req_text = str(requirements).lower()

        if "ui" in req_text or "component" in req_text:
            boost_fields["category"] = 1.8
            boost_fields["features"] = 1.6

        if "framework" in req_text or "library" in req_text:
            boost_fields["technology"] = 2.0

        if "performance" in req_text:
            boost_fields["performance_metrics"] = 1.7

        if "popular" in req_text or "trending" in req_text:
            boost_fields["popularity"] = 1.5

        return boost_fields

    def _calculate_fuzzy_threshold(self, query: str) -> float:
        """Calculate fuzzy matching threshold"""

        query_length = len(query.replace(" ", ""))

        # Shorter queries need higher precision
        if query_length < 5:
            return 0.9
        elif query_length < 10:
            return 0.8
        elif query_length < 20:
            return 0.7
        else:
            return 0.6

    def _build_synonyms(self) -> List[List[str]]:
        """Build synonym groups"""

        return [
            ["ui", "interface", "frontend", "view"],
            ["component", "widget", "element", "control"],
            ["framework", "library", "toolkit", "package"],
            ["api", "service", "endpoint", "rest"],
            ["database", "db", "storage", "persistence"],
            ["fast", "quick", "rapid", "speedy", "efficient"],
            ["modern", "latest", "current", "new", "recent"],
            ["simple", "easy", "basic", "straightforward"],
            ["responsive", "mobile", "adaptive", "flexible"],
            ["secure", "safe", "protected", "encrypted"],
        ]
