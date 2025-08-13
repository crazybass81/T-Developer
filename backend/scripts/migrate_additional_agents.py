#!/usr/bin/env python3
"""
Day 18: Additional Agent Migration Script
Migrates Component Decision, Match Rate, and Search agents to AgentCore
"""
import json
import logging
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.create_agentcore_wrapper import AGENTCORE_TEMPLATE

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Additional agents to migrate
ADDITIONAL_AGENTS = {
    "component_decision": {
        "class_name": "ComponentDecisionAgent",
        "name": "Component Decision Agent",
        "description": "Component architecture decision agent",
        "capabilities": [
            "architecture_selection",
            "component_analysis",
            "technology_stack_building",
        ],
        "logic": '''# Component Decision processing logic
        requirements = request.get("requirements", {})
        constraints = request.get("constraints", {})

        # Analyze architecture needs
        architecture = self._select_architecture(requirements)

        # Select components
        components = self._analyze_components(requirements, architecture)

        # Build technology stack
        tech_stack = self._build_tech_stack(components, constraints)

        return {
            "architecture": architecture,
            "components": components,
            "tech_stack": tech_stack,
            "recommendations": self._generate_recommendations(tech_stack)
        }

    def _select_architecture(self, requirements: dict) -> dict:
        """Select appropriate architecture"""
        if requirements.get("scalability") == "high":
            return {"type": "microservices", "pattern": "event-driven"}
        elif requirements.get("simplicity") == "high":
            return {"type": "monolithic", "pattern": "mvc"}
        else:
            return {"type": "modular", "pattern": "layered"}

    def _analyze_components(self, requirements: dict, architecture: dict) -> list:
        """Analyze and select components"""
        components = []

        # Core components
        components.append({"name": "api_gateway", "type": "infrastructure"})
        components.append({"name": "database", "type": "data"})

        if architecture["type"] == "microservices":
            components.append({"name": "message_queue", "type": "messaging"})
            components.append({"name": "service_registry", "type": "infrastructure"})

        if requirements.get("authentication"):
            components.append({"name": "auth_service", "type": "security"})

        return components

    def _build_tech_stack(self, components: list, constraints: dict) -> dict:
        """Build technology stack"""
        stack = {
            "backend": "Python/FastAPI" if constraints.get("language") == "python" else "Node.js/Express",
            "database": "PostgreSQL" if constraints.get("sql") else "MongoDB",
            "cache": "Redis",
            "queue": "RabbitMQ" if "message_queue" in [c["name"] for c in components] else None
        }
        return {k: v for k, v in stack.items() if v is not None}

    def _generate_recommendations(self, tech_stack: dict) -> list:
        """Generate architecture recommendations"""
        recommendations = []

        if "PostgreSQL" in tech_stack.values():
            recommendations.append("Use connection pooling for database optimization")

        if "Redis" in tech_stack.values():
            recommendations.append("Implement cache invalidation strategy")

        if "RabbitMQ" in tech_stack.values():
            recommendations.append("Set up dead letter queues for error handling")

        return recommendations''',
    },
    "match_rate": {
        "class_name": "MatchRateAgent",
        "name": "Match Rate Agent",
        "description": "Solution matching and scoring agent",
        "capabilities": ["similarity_calculation", "quality_assessment", "recommendation_engine"],
        "logic": '''# Match Rate processing logic
        query = request.get("query", {})
        candidates = request.get("candidates", [])

        # Calculate similarity scores
        scores = self._calculate_similarity(query, candidates)

        # Assess quality
        quality = self._assess_quality(candidates, scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(scores, quality)

        return {
            "scores": scores,
            "quality_metrics": quality,
            "recommendations": recommendations,
            "best_match": self._find_best_match(scores)
        }

    def _calculate_similarity(self, query: dict, candidates: list) -> list:
        """Calculate similarity scores"""
        scores = []

        for candidate in candidates:
            score = 0.0

            # Feature matching
            for feature in query.get("features", []):
                if feature in candidate.get("features", []):
                    score += 0.2

            # Technology matching
            for tech in query.get("technologies", []):
                if tech in candidate.get("technologies", []):
                    score += 0.15

            # Constraint matching
            if query.get("budget") and candidate.get("cost"):
                if candidate["cost"] <= query["budget"]:
                    score += 0.3

            scores.append({
                "candidate_id": candidate.get("id"),
                "score": min(score, 1.0),
                "confidence": 0.85
            })

        return sorted(scores, key=lambda x: x["score"], reverse=True)

    def _assess_quality(self, candidates: list, scores: list) -> dict:
        """Assess solution quality"""
        return {
            "average_score": sum(s["score"] for s in scores) / len(scores) if scores else 0,
            "top_match_score": scores[0]["score"] if scores else 0,
            "match_count": len([s for s in scores if s["score"] > 0.7]),
            "quality_rating": "high" if scores and scores[0]["score"] > 0.8 else "medium"
        }

    def _generate_recommendations(self, scores: list, quality: dict) -> list:
        """Generate match recommendations"""
        recommendations = []

        if quality["average_score"] < 0.5:
            recommendations.append("Consider expanding search criteria")

        if quality["match_count"] == 0:
            recommendations.append("No high-quality matches found - review requirements")

        if quality["top_match_score"] > 0.9:
            recommendations.append("Excellent match found - proceed with implementation")

        return recommendations

    def _find_best_match(self, scores: list) -> dict:
        """Find the best matching solution"""
        if not scores:
            return {"candidate_id": None, "score": 0}
        return scores[0]''',
    },
    "search": {
        "class_name": "SearchAgent",
        "name": "Search Agent",
        "description": "Intelligent search and retrieval agent",
        "capabilities": ["query_building", "result_ranking", "semantic_search"],
        "logic": '''# Search processing logic
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
            "facets": self._extract_facets(results)
        }

    def _build_query(self, query: str, filters: dict) -> dict:
        """Build search query"""
        search_query = {
            "text": query,
            "filters": [],
            "boost_fields": ["title", "description"]
        }

        for field, value in filters.items():
            search_query["filters"].append({
                "field": field,
                "value": value,
                "operator": "equals"
            })

        return search_query

    def _execute_search(self, search_query: dict, limit: int) -> list:
        """Execute search (mock implementation)"""
        # In production, this would query actual search index
        mock_results = []

        for i in range(min(limit, 5)):
            mock_results.append({
                "id": f"result_{i+1}",
                "title": f"Result {i+1}",
                "description": f"Description for result {i+1}",
                "relevance": 0.9 - (i * 0.1),
                "category": "technology" if i % 2 == 0 else "business"
            })

        return mock_results

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
        facets = {"categories": {}, "tags": {}}

        for result in results:
            category = result.get("category", "unknown")
            facets["categories"][category] = facets["categories"].get(category, 0) + 1

        return facets''',
    },
}


def create_agent_wrapper(agent_id: str, config: Dict) -> str:
    """Create AgentCore wrapper for an agent"""
    return AGENTCORE_TEMPLATE.format(
        agent_id=agent_id,
        class_name=config["class_name"],
        name=config["name"],
        description=config["description"],
        capabilities=json.dumps(config["capabilities"]),
        agent_logic=config["logic"],
    )


def migrate_additional_agents():
    """Migrate additional agents to AgentCore format"""
    logger.info("🧬 Day 18: Additional Agent Migration")
    logger.info("=" * 50)

    base_dir = Path("src/agents/agentcore")
    base_dir.mkdir(parents=True, exist_ok=True)

    migration_results = []

    for agent_id, config in ADDITIONAL_AGENTS.items():
        logger.info(f"📦 Migrating {config['name']}...")

        try:
            # Create agent directory
            agent_dir = base_dir / agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Generate wrapper code
            wrapper_code = create_agent_wrapper(agent_id, config)

            # Check size
            size_kb = len(wrapper_code.encode()) / 1024
            if size_kb > 6.5:
                logger.warning(f"  ⚠️ Agent exceeds size limit: {size_kb:.2f} KB")
                # Continue anyway for now

            # Save wrapper
            wrapper_file = agent_dir / "main.py"
            wrapper_file.write_text(wrapper_code)
            logger.info(f"  ✅ Created: {wrapper_file} ({size_kb:.2f} KB)")

            # Create metadata
            metadata = {
                "agent_id": agent_id,
                "name": config["name"],
                "description": config["description"],
                "version": "1.0.0",
                "size_kb": size_kb,
                "capabilities": config["capabilities"],
                "created_at": "2025-08-16T00:00:00Z",
            }

            metadata_file = agent_dir / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))
            logger.info(f"  ✅ Metadata: {metadata_file}")

            migration_results.append(
                {
                    "agent_id": agent_id,
                    "name": config["name"],
                    "status": "success",
                    "size_kb": size_kb,
                }
            )

        except Exception as e:
            logger.error(f"  ❌ Failed to migrate {config['name']}: {e}")
            migration_results.append(
                {"agent_id": agent_id, "name": config["name"], "status": "failed", "error": str(e)}
            )

    # Summary
    logger.info("\n📊 Migration Summary:")
    successful = sum(1 for r in migration_results if r["status"] == "success")
    failed = sum(1 for r in migration_results if r["status"] == "failed")

    for result in migration_results:
        icon = "✅" if result["status"] == "success" else "❌"
        size_info = f" ({result.get('size_kb', 0):.2f} KB)" if result["status"] == "success" else ""
        logger.info(f"{icon} {result['name']}: {result['status']}{size_info}")

    logger.info(f"\nTotal: {len(migration_results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")

    # Save results
    results_file = Path("logs/day18_migration_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(
        json.dumps(
            {
                "migration_results": migration_results,
                "summary": {
                    "total": len(migration_results),
                    "successful": successful,
                    "failed": failed,
                },
            },
            indent=2,
        )
    )

    logger.info(f"\n📁 Results saved to {results_file}")

    return successful == len(migration_results)


if __name__ == "__main__":
    success = migrate_additional_agents()
    sys.exit(0 if success else 1)
