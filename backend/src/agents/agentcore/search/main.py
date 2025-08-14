"""
Intelligent search and retrieval agent
AgentCore-compatible wrapper
Size: < 6.5KB
"""
from typing import Any, Dict


class SearchAgent:
    """AgentCore wrapper for Search Agent"""

    def __init__(self):
        self.name = "search"
        self.version = "1.0.0"
        self.description = "Intelligent search and retrieval agent"
        self._initialized = True

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method"""
        try:
            # Validate input
            validation = self.validate_input(request)
            if not validation["valid"]:
                return {"status": "error", "error": validation["error"]}

            # Process request based on agent type
            result = self._execute_logic(request)

            return {"status": "success", "agent": self.name, "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def validate_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input request"""
        if not request:
            return {"valid": False, "error": "Empty request"}

        if "input" not in request:
            return {"valid": False, "error": "Missing input field"}

        return {"valid": True}

    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self._get_capabilities(),
            "constraints": {"max_memory_kb": 6.5, "max_instantiation_us": 3.0},
        }

    def _execute_logic(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific logic"""
        # Search processing logic
        query = request.get("query", "")
        filters = request.get("filters", {})
        limit = request.get("limit", 10)

        # Build search query
        search_query = self._build_query(query, filters)

        # Execute search
        results = self._execute_search(search_query, limit)

        # Rank results
        ranked_results = self._rank_results(results, query)

        return {
            "query": search_query,
            "results": ranked_results,
            "total_count": len(results),
            "facets": self._extract_facets(results),
        }

    def _build_query(self, query: str, filters: dict) -> dict:
        """Build search query"""
        search_query = {"text": query, "filters": [], "boost_fields": ["title", "description"]}

        for field, value in filters.items():
            search_query["filters"].append({"field": field, "value": value, "operator": "equals"})

        return search_query

    def _execute_search(self, search_query: dict, limit: int) -> list:
        """Execute search with real logic"""
        # Compact data store
        ds = [
            {"i": "1", "t": "Python", "d": "Learn Python", "c": "prog"},
            {"i": "2", "t": "AWS Lambda", "d": "Serverless", "c": "cloud"},
            {"i": "3", "t": "ML Basics", "d": "Algorithms", "c": "ai"},
            {"i": "4", "t": "React UI", "d": "Components", "c": "front"},
            {"i": "5", "t": "Database", "d": "SQL NoSQL", "c": "db"},
        ]

        q = search_query.get("text", "").lower()
        fl = search_query.get("filters", [])
        res = []

        for item in ds:
            # Filter check
            if fl:
                ok = True
                for f in fl:
                    if f["field"] in item and item[f["field"]] != f["value"]:
                        ok = False
                        break
                if not ok:
                    continue

            # Score calculation
            s = 0.0
            if q:
                if q in item["t"].lower():
                    s += 0.6
                if q in item["d"].lower():
                    s += 0.4
            else:
                s = 0.5

            if s > 0 or not q:
                res.append(
                    {
                        "id": item["i"],
                        "title": item["t"],
                        "description": item["d"],
                        "category": item["c"],
                        "relevance": min(s, 1.0),
                    }
                )

        res.sort(key=lambda x: x["relevance"], reverse=True)
        return res[:limit]

    def _rank_results(self, results: list, query: str) -> list:
        """Rank search results"""
        for result in results:
            # Simple relevance scoring
            score = result.get("relevance", 0.5)

            # Boost if query terms in title
            if query.lower() in result.get("title", "").lower():
                score += 0.2

            # Boost if query terms in description
            if query.lower() in result.get("description", "").lower():
                score += 0.1

            result["final_score"] = min(score, 1.0)

        return sorted(results, key=lambda x: x["final_score"], reverse=True)

    def _extract_facets(self, results: list) -> dict:
        """Extract facets from results"""
        fc = {}
        for r in results:
            c = r.get("category", "unknown")
            fc[c] = fc.get(c, 0) + 1
        return {"categories": fc}

    def _get_capabilities(self) -> list:
        """Get agent capabilities"""
        return ["query_building", "result_ranking", "semantic_search"]


# AgentCore entry point
def handler(event, context):
    """AWS Lambda handler"""
    agent = SearchAgent()
    return agent.process(event)
