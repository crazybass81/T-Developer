"""
Search Analytics Module
Advanced analytics and metrics collection for search operations
"""

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class SearchAnalytics:
    """Comprehensive search analytics and metrics system"""

    def __init__(self):
        # Analytics storage
        self.search_logs = []
        self.query_patterns = defaultdict(int)
        self.result_interactions = defaultdict(list)
        self.performance_metrics = []
        self.user_behavior = defaultdict(lambda: defaultdict(list))

        # Analytics configuration
        self.config = {
            "max_log_entries": 10000,
            "retention_days": 30,
            "enable_detailed_logging": True,
            "enable_performance_tracking": True,
            "enable_user_tracking": True,
            "analytics_batch_size": 100,
        }

        # Metric thresholds
        self.thresholds = {
            "slow_query_ms": 1000,
            "low_relevance_score": 0.3,
            "min_click_through_rate": 0.1,
            "max_bounce_rate": 0.8,
        }

        # Real-time analytics
        self.realtime_stats = {
            "queries_per_minute": 0,
            "avg_response_time": 0,
            "active_sessions": set(),
            "trending_queries": [],
            "last_updated": datetime.now(),
        }

    async def analyze(
        self,
        query: Dict[str, Any],
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze search operation and generate insights"""

        start_time = datetime.now()

        # Log the search event
        search_event = await self._log_search_event(query, results, filters)

        # Analyze query patterns
        query_analysis = self._analyze_query_patterns(query)

        # Analyze result quality
        result_analysis = self._analyze_result_quality(results, query)

        # Analyze search effectiveness
        effectiveness_analysis = self._analyze_search_effectiveness(query, results, search_event)

        # Generate performance insights
        performance_insights = self._generate_performance_insights(search_event)

        # Update real-time statistics
        await self._update_realtime_stats(query, results)

        # Compile comprehensive analysis
        analysis = {
            "search_id": search_event["id"],
            "timestamp": search_event["timestamp"],
            "query_analysis": query_analysis,
            "result_analysis": result_analysis,
            "effectiveness": effectiveness_analysis,
            "performance": performance_insights,
            "recommendations": self._generate_analytics_recommendations(
                query_analysis, result_analysis, effectiveness_analysis
            ),
            "metrics": self._calculate_search_metrics(search_event),
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
        }

        return analysis

    async def _log_search_event(
        self,
        query: Dict[str, Any],
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Log detailed search event"""

        search_event = {
            "id": self._generate_search_id(),
            "timestamp": datetime.now().isoformat(),
            "query": {
                "original_text": query.get("original_query", ""),
                "processed_terms": query.get("terms", []),
                "expanded_terms": query.get("expanded_terms", []),
                "query_type": query.get("query_type", "standard"),
                "complexity_score": self._calculate_query_complexity(query),
            },
            "filters": filters,
            "results": {
                "total_count": len(results),
                "top_scores": [r.get("score", 0) for r in results[:5]],
                "categories": list(set(r.get("category") for r in results if r.get("category"))),
                "technologies": list(
                    set(r.get("technology") for r in results if r.get("technology"))
                ),
            },
            "context": {
                "session_id": self._get_session_id(),
                "user_agent": self._get_user_agent(),
                "ip_hash": self._get_ip_hash(),
            },
        }

        # Store in logs
        if self.config["enable_detailed_logging"]:
            self.search_logs.append(search_event)

            # Cleanup old logs if needed
            if len(self.search_logs) > self.config["max_log_entries"]:
                self.search_logs = self.search_logs[-self.config["max_log_entries"] :]

        return search_event

    def _analyze_query_patterns(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query patterns and characteristics"""

        original_query = query.get("original_query", "")
        terms = query.get("terms", [])

        # Update pattern tracking
        self.query_patterns[original_query.lower()] += 1

        # Analyze query structure
        structure_analysis = {
            "length_chars": len(original_query),
            "word_count": len(terms),
            "has_operators": bool(query.get("operators", [])),
            "has_filters": bool(query.get("filters", {})),
            "query_type": query.get("query_type", "standard"),
            "specificity_score": self._calculate_query_specificity(original_query),
            "technical_level": self._calculate_technical_level(original_query),
            "intent_confidence": self._calculate_intent_confidence(query),
        }

        # Find similar queries
        similar_queries = self._find_similar_queries(original_query)

        # Calculate query popularity
        popularity_metrics = {
            "frequency_rank": self._get_query_frequency_rank(original_query),
            "trending_score": self._calculate_trending_score(original_query),
            "similar_query_count": len(similar_queries),
        }

        return {
            "structure": structure_analysis,
            "popularity": popularity_metrics,
            "similar_queries": similar_queries[:5],  # Top 5 similar
            "patterns": self._identify_query_patterns(original_query, terms),
        }

    def _analyze_result_quality(
        self, results: List[Dict[str, Any]], query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze quality and relevance of search results"""

        if not results:
            return {
                "overall_quality": 0.0,
                "relevance_distribution": {},
                "diversity_score": 0.0,
                "coverage_score": 0.0,
                "issues": ["no_results_found"],
            }

        # Calculate quality metrics
        quality_metrics = {
            "avg_relevance_score": sum(r.get("score", 0) for r in results) / len(results),
            "max_relevance_score": max(r.get("score", 0) for r in results),
            "min_relevance_score": min(r.get("score", 0) for r in results),
            "score_variance": self._calculate_score_variance(results),
        }

        # Analyze result diversity
        diversity_metrics = {
            "category_diversity": self._calculate_category_diversity(results),
            "technology_diversity": self._calculate_technology_diversity(results),
            "feature_diversity": self._calculate_feature_diversity(results),
            "popularity_range": self._calculate_popularity_range(results),
        }

        # Calculate coverage
        coverage_metrics = {
            "query_term_coverage": self._calculate_term_coverage(query, results),
            "requirement_coverage": self._calculate_requirement_coverage(query, results),
            "domain_coverage": self._calculate_domain_coverage(results),
        }

        # Identify quality issues
        quality_issues = self._identify_quality_issues(results, quality_metrics)

        # Overall quality score
        overall_quality = self._calculate_overall_quality(
            quality_metrics, diversity_metrics, coverage_metrics
        )

        return {
            "overall_quality": overall_quality,
            "quality_metrics": quality_metrics,
            "diversity_metrics": diversity_metrics,
            "coverage_metrics": coverage_metrics,
            "issues": quality_issues,
            "recommendations": self._generate_quality_recommendations(quality_issues),
        }

    def _analyze_search_effectiveness(
        self,
        query: Dict[str, Any],
        results: List[Dict[str, Any]],
        search_event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze overall search effectiveness"""

        effectiveness_metrics = {
            "result_count_adequacy": self._assess_result_count_adequacy(results),
            "precision_estimate": self._estimate_precision(results),
            "recall_estimate": self._estimate_recall(query, results),
            "user_satisfaction_prediction": self._predict_user_satisfaction(
                query, results, search_event
            ),
            "search_success_probability": self._calculate_search_success_probability(
                query, results
            ),
        }

        # Time-based effectiveness
        if self.performance_metrics:
            effectiveness_metrics.update(
                {
                    "response_time_impact": self._assess_response_time_impact(search_event),
                    "efficiency_score": self._calculate_efficiency_score(search_event),
                }
            )

        return effectiveness_metrics

    def _generate_performance_insights(self, search_event: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance insights"""

        # Record performance metrics
        performance_data = {
            "timestamp": search_event["timestamp"],
            "query_complexity": search_event["query"]["complexity_score"],
            "result_count": search_event["results"]["total_count"],
            "processing_time": search_event.get("processing_time_ms", 0),
        }

        if self.config["enable_performance_tracking"]:
            self.performance_metrics.append(performance_data)

        # Calculate performance insights
        insights = {
            "current_performance": performance_data,
            "performance_trend": self._calculate_performance_trend(),
            "bottlenecks": self._identify_performance_bottlenecks(),
            "optimization_opportunities": self._identify_optimization_opportunities(),
        }

        # Compare with historical data
        if len(self.performance_metrics) > 10:
            insights["historical_comparison"] = self._compare_with_historical_performance(
                performance_data
            )

        return insights

    async def _update_realtime_stats(self, query: Dict[str, Any], results: List[Dict[str, Any]]):
        """Update real-time statistics"""

        current_minute = datetime.now().replace(second=0, microsecond=0)

        # Update queries per minute
        minute_key = current_minute.isoformat()
        if not hasattr(self, "_minute_queries"):
            self._minute_queries = defaultdict(int)
        self._minute_queries[minute_key] += 1

        # Clean up old minute data
        cutoff_time = current_minute - timedelta(minutes=5)
        self._minute_queries = {
            k: v
            for k, v in self._minute_queries.items()
            if datetime.fromisoformat(k) >= cutoff_time
        }

        # Update current QPM
        self.realtime_stats["queries_per_minute"] = sum(self._minute_queries.values()) / 5

        # Update trending queries
        query_text = query.get("original_query", "")
        if query_text:
            self._update_trending_queries(query_text)

        # Update session tracking
        session_id = self._get_session_id()
        if session_id:
            self.realtime_stats["active_sessions"].add(session_id)

        self.realtime_stats["last_updated"] = datetime.now()

    def _generate_analytics_recommendations(
        self,
        query_analysis: Dict[str, Any],
        result_analysis: Dict[str, Any],
        effectiveness: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis"""

        recommendations = []

        # Query-based recommendations
        if query_analysis["structure"]["specificity_score"] < 0.3:
            recommendations.append(
                {
                    "type": "query_improvement",
                    "priority": "medium",
                    "message": "Query is too vague - suggest more specific terms",
                    "action": "provide_query_suggestions",
                }
            )

        if query_analysis["structure"]["technical_level"] > 0.8:
            recommendations.append(
                {
                    "type": "result_filtering",
                    "priority": "low",
                    "message": "Technical query - prioritize advanced components",
                    "action": "boost_technical_results",
                }
            )

        # Result quality recommendations
        if result_analysis["overall_quality"] < 0.5:
            recommendations.append(
                {
                    "type": "search_improvement",
                    "priority": "high",
                    "message": "Search quality is low - review ranking algorithm",
                    "action": "optimize_ranking",
                }
            )

        if result_analysis["diversity_metrics"]["category_diversity"] < 0.3:
            recommendations.append(
                {
                    "type": "diversity_improvement",
                    "priority": "medium",
                    "message": "Results lack diversity - improve category coverage",
                    "action": "enhance_diversity",
                }
            )

        # Effectiveness recommendations
        if effectiveness["user_satisfaction_prediction"] < 0.6:
            recommendations.append(
                {
                    "type": "user_experience",
                    "priority": "high",
                    "message": "Low predicted satisfaction - review search UX",
                    "action": "improve_user_experience",
                }
            )

        return recommendations

    def _calculate_search_metrics(self, search_event: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key search metrics"""

        return {
            "query_complexity": search_event["query"]["complexity_score"],
            "result_density": len(search_event["results"]["categories"])
            / max(len(search_event["results"]["top_scores"]), 1),
            "score_consistency": 1.0
            - self._calculate_score_variance_from_list(search_event["results"]["top_scores"]),
            "category_coverage": len(search_event["results"]["categories"]),
            "technology_coverage": len(search_event["results"]["technologies"]),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive search statistics"""

        return {
            "overview": {
                "total_searches": len(self.search_logs),
                "unique_queries": len(self.query_patterns),
                "avg_results_per_search": self._calculate_avg_results_per_search(),
                "most_common_query_type": self._get_most_common_query_type(),
            },
            "query_patterns": {
                "top_queries": self._get_top_queries(10),
                "query_length_distribution": self._get_query_length_distribution(),
                "complexity_distribution": self._get_complexity_distribution(),
                "trending_queries": self.realtime_stats.get("trending_queries", []),
            },
            "performance": {
                "avg_response_time_ms": self._calculate_avg_response_time(),
                "queries_per_minute": self.realtime_stats.get("queries_per_minute", 0),
                "slow_query_percentage": self._calculate_slow_query_percentage(),
                "performance_trend": self._calculate_performance_trend(),
            },
            "quality": {
                "avg_result_quality": self._calculate_avg_result_quality(),
                "quality_trend": self._calculate_quality_trend(),
                "common_quality_issues": self._get_common_quality_issues(),
            },
            "usage": {
                "search_frequency": self._calculate_search_frequency(),
                "peak_hours": self._identify_peak_hours(),
                "category_popularity": self._get_category_popularity(),
                "technology_popularity": self._get_technology_popularity(),
            },
        }

    # Helper methods for calculations

    def _generate_search_id(self) -> str:
        """Generate unique search ID"""
        return f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.search_logs)}"

    def _calculate_query_complexity(self, query: Dict[str, Any]) -> float:
        """Calculate query complexity score"""

        complexity = 0.0

        # Length factor
        original_query = query.get("original_query", "")
        complexity += min(len(original_query) / 100, 0.3)

        # Term count factor
        terms = query.get("terms", [])
        complexity += min(len(terms) / 10, 0.3)

        # Operators factor
        operators = query.get("operators", [])
        complexity += len(operators) * 0.1

        # Filters factor
        filters = query.get("filters", {})
        complexity += len(filters) * 0.05

        return min(complexity, 1.0)

    def _calculate_query_specificity(self, query_text: str) -> float:
        """Calculate how specific the query is"""

        specific_terms = [
            "framework",
            "library",
            "component",
            "tool",
            "package",
            "version",
            "specific",
            "exactly",
            "must",
            "required",
        ]

        query_lower = query_text.lower()
        specificity = sum(0.2 for term in specific_terms if term in query_lower)

        # Length factor
        word_count = len(query_text.split())
        specificity += min(word_count / 20, 0.4)

        return min(specificity, 1.0)

    def _calculate_technical_level(self, query_text: str) -> float:
        """Calculate technical complexity of query"""

        technical_terms = [
            "architecture",
            "scalability",
            "performance",
            "optimization",
            "microservices",
            "api",
            "database",
            "algorithm",
            "implementation",
        ]

        query_lower = query_text.lower()
        tech_level = sum(0.15 for term in technical_terms if term in query_lower)

        return min(tech_level, 1.0)

    def _calculate_intent_confidence(self, query: Dict[str, Any]) -> float:
        """Calculate confidence in detected intent"""

        # Simple heuristic based on query structure
        original_query = query.get("original_query", "")

        intent_indicators = [
            "find",
            "search",
            "need",
            "want",
            "looking for",
            "help with",
        ]
        confidence = 0.5  # Base confidence

        for indicator in intent_indicators:
            if indicator in original_query.lower():
                confidence += 0.1

        return min(confidence, 1.0)

    def _find_similar_queries(self, query_text: str) -> List[str]:
        """Find similar historical queries"""

        query_lower = query_text.lower()
        similar = []

        for historical_query in self.query_patterns.keys():
            if historical_query != query_lower:
                similarity = self._calculate_text_similarity(query_lower, historical_query)
                if similarity > 0.6:
                    similar.append(historical_query)

        return sorted(similar, key=lambda q: self.query_patterns[q], reverse=True)

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation"""

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _identify_query_patterns(self, query_text: str, terms: List[str]) -> List[str]:
        """Identify patterns in the query"""

        patterns = []
        query_lower = query_text.lower()

        if any(word in query_lower for word in ["ui", "interface", "frontend"]):
            patterns.append("frontend_focused")

        if any(word in query_lower for word in ["api", "backend", "server"]):
            patterns.append("backend_focused")

        if any(word in query_lower for word in ["fast", "performance", "optimize"]):
            patterns.append("performance_focused")

        if len(terms) == 1:
            patterns.append("single_term")
        elif len(terms) > 5:
            patterns.append("multi_term")

        return patterns

    def _calculate_score_variance(self, results: List[Dict[str, Any]]) -> float:
        """Calculate variance in result scores"""

        scores = [r.get("score", 0) for r in results]
        return self._calculate_score_variance_from_list(scores)

    def _calculate_score_variance_from_list(self, scores: List[float]) -> float:
        """Calculate variance from list of scores"""

        if len(scores) <= 1:
            return 0.0

        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)

        return math.sqrt(variance)  # Return standard deviation

    def _calculate_category_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calculate diversity of categories in results"""

        categories = [r.get("category") for r in results if r.get("category")]
        unique_categories = set(categories)

        if not categories:
            return 0.0

        return len(unique_categories) / len(categories)

    def _calculate_technology_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calculate diversity of technologies in results"""

        technologies = [r.get("technology") for r in results if r.get("technology")]
        unique_technologies = set(technologies)

        if not technologies:
            return 0.0

        return len(unique_technologies) / len(technologies)

    def _calculate_feature_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calculate diversity of features in results"""

        all_features = []
        for result in results:
            features = result.get("features", [])
            all_features.extend(features)

        if not all_features:
            return 0.0

        unique_features = set(all_features)
        return len(unique_features) / len(all_features)

    def _calculate_popularity_range(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate range of popularity in results"""

        popularities = [r.get("popularity", 0) for r in results]

        if not popularities:
            return {"min": 0, "max": 0, "range": 0, "std": 0}

        min_pop = min(popularities)
        max_pop = max(popularities)
        mean_pop = sum(popularities) / len(popularities)
        std_pop = math.sqrt(sum((p - mean_pop) ** 2 for p in popularities) / len(popularities))

        return {
            "min": min_pop,
            "max": max_pop,
            "range": max_pop - min_pop,
            "std": std_pop,
        }

    def _calculate_term_coverage(
        self, query: Dict[str, Any], results: List[Dict[str, Any]]
    ) -> float:
        """Calculate how well results cover query terms"""

        query_terms = set(term.lower() for term in query.get("terms", []))
        if not query_terms:
            return 1.0

        total_coverage = 0.0

        for result in results:
            result_text = " ".join(
                [
                    str(result.get("name", "")),
                    str(result.get("description", "")),
                    " ".join(result.get("tags", [])),
                ]
            ).lower()

            covered_terms = sum(1 for term in query_terms if term in result_text)
            coverage = covered_terms / len(query_terms)
            total_coverage += coverage

        return total_coverage / len(results) if results else 0.0

    def _calculate_requirement_coverage(
        self, query: Dict[str, Any], results: List[Dict[str, Any]]
    ) -> float:
        """Calculate requirement coverage (simplified)"""

        requirements = query.get("requirements", {})
        if not requirements:
            return 1.0

        # Simple coverage calculation based on category and technology
        coverage_score = 0.0
        coverage_count = 0

        if "category" in requirements:
            required_category = requirements["category"].lower()
            matching_results = sum(
                1 for r in results if r.get("category", "").lower() == required_category
            )
            coverage_score += matching_results / len(results) if results else 0
            coverage_count += 1

        if "technology" in requirements:
            required_tech = requirements["technology"].lower()
            matching_results = sum(
                1 for r in results if r.get("technology", "").lower() == required_tech
            )
            coverage_score += matching_results / len(results) if results else 0
            coverage_count += 1

        return coverage_score / coverage_count if coverage_count > 0 else 1.0

    def _calculate_domain_coverage(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate domain coverage in results"""

        domains = defaultdict(int)

        for result in results:
            category = result.get("category", "unknown").lower()

            if any(term in category for term in ["ui", "frontend", "interface"]):
                domains["frontend"] += 1
            elif any(term in category for term in ["api", "backend", "server"]):
                domains["backend"] += 1
            elif any(term in category for term in ["mobile", "app"]):
                domains["mobile"] += 1
            elif any(term in category for term in ["data", "analytics"]):
                domains["data"] += 1
            else:
                domains["other"] += 1

        return dict(domains)

    def _identify_quality_issues(
        self, results: List[Dict[str, Any]], quality_metrics: Dict[str, float]
    ) -> List[str]:
        """Identify quality issues with search results"""

        issues = []

        if quality_metrics["avg_relevance_score"] < self.thresholds["low_relevance_score"]:
            issues.append("low_relevance_scores")

        if quality_metrics["score_variance"] > 0.5:
            issues.append("inconsistent_scoring")

        if len(results) < 5:
            issues.append("insufficient_results")

        if len(results) > 100:
            issues.append("too_many_results")

        # Check for duplicates (simplified)
        names = [r.get("name", "") for r in results]
        if len(names) != len(set(names)):
            issues.append("duplicate_results")

        return issues

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on quality issues"""

        recommendations = []

        if "low_relevance_scores" in issues:
            recommendations.append("Improve relevance scoring algorithm")

        if "inconsistent_scoring" in issues:
            recommendations.append("Normalize scoring methodology")

        if "insufficient_results" in issues:
            recommendations.append("Expand search index or reduce filtering")

        if "too_many_results" in issues:
            recommendations.append("Improve result filtering and ranking")

        if "duplicate_results" in issues:
            recommendations.append("Implement deduplication logic")

        return recommendations

    def _calculate_overall_quality(
        self,
        quality_metrics: Dict[str, float],
        diversity_metrics: Dict[str, float],
        coverage_metrics: Dict[str, float],
    ) -> float:
        """Calculate overall quality score"""

        quality_score = quality_metrics["avg_relevance_score"] * 0.4
        diversity_score = diversity_metrics["category_diversity"] * 0.3
        coverage_score = coverage_metrics["query_term_coverage"] * 0.3

        return quality_score + diversity_score + coverage_score

    def _get_session_id(self) -> str:
        """Get session ID (placeholder)"""
        return "session_placeholder"

    def _get_user_agent(self) -> str:
        """Get user agent (placeholder)"""
        return "user_agent_placeholder"

    def _get_ip_hash(self) -> str:
        """Get hashed IP (placeholder)"""
        return "ip_hash_placeholder"

    # Additional helper methods would continue here...
    # For brevity, I'm including just the core functionality

    def _assess_result_count_adequacy(self, results: List[Dict[str, Any]]) -> str:
        """Assess if result count is adequate"""
        count = len(results)

        if count == 0:
            return "no_results"
        elif count < 5:
            return "too_few"
        elif count > 50:
            return "too_many"
        else:
            return "adequate"

    def _estimate_precision(self, results: List[Dict[str, Any]]) -> float:
        """Estimate precision based on scores"""
        if not results:
            return 0.0

        relevant_results = sum(1 for r in results if r.get("score", 0) >= 0.5)
        return relevant_results / len(results)

    def _estimate_recall(self, query: Dict[str, Any], results: List[Dict[str, Any]]) -> float:
        """Estimate recall (simplified)"""
        # This would require knowledge of total relevant documents
        # For now, return a heuristic based on result diversity
        unique_categories = set(r.get("category") for r in results if r.get("category"))
        return min(len(unique_categories) / 5, 1.0)  # Assume 5 main categories

    def _predict_user_satisfaction(
        self,
        query: Dict[str, Any],
        results: List[Dict[str, Any]],
        search_event: Dict[str, Any],
    ) -> float:
        """Predict user satisfaction based on various factors"""

        satisfaction = 0.5  # Base satisfaction

        # Result quality factor
        if results:
            avg_score = sum(r.get("score", 0) for r in results) / len(results)
            satisfaction += avg_score * 0.3

        # Result count factor
        result_count = len(results)
        if 5 <= result_count <= 20:
            satisfaction += 0.2
        elif result_count > 20:
            satisfaction -= 0.1

        # Query complexity vs result quality
        query_complexity = query.get("complexity_score", 0.5)
        if query_complexity > 0.7 and results:
            # Complex queries need high-quality results
            top_score = max(r.get("score", 0) for r in results)
            if top_score > 0.8:
                satisfaction += 0.1
            else:
                satisfaction -= 0.1

        return min(max(satisfaction, 0.0), 1.0)

    def _calculate_search_success_probability(
        self, query: Dict[str, Any], results: List[Dict[str, Any]]
    ) -> float:
        """Calculate probability of search success"""

        if not results:
            return 0.0

        # Factors contributing to success
        factors = []

        # High-scoring results
        top_scores = sorted([r.get("score", 0) for r in results], reverse=True)[:3]
        avg_top_score = sum(top_scores) / len(top_scores) if top_scores else 0
        factors.append(avg_top_score)

        # Result diversity
        categories = set(r.get("category") for r in results if r.get("category"))
        diversity = min(len(categories) / 3, 1.0)
        factors.append(diversity * 0.8)

        # Query-result alignment
        query_terms = set(term.lower() for term in query.get("terms", []))
        alignment_scores = []

        for result in results[:5]:  # Check top 5 results
            result_text = " ".join(
                [str(result.get("name", "")), str(result.get("description", ""))]
            ).lower()

            matched_terms = sum(1 for term in query_terms if term in result_text)
            alignment = matched_terms / len(query_terms) if query_terms else 0
            alignment_scores.append(alignment)

        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0
        factors.append(avg_alignment * 0.6)

        # Calculate weighted average
        return sum(factors) / len(factors)

    # Placeholder methods for statistics - would implement with real data
    def _calculate_avg_results_per_search(self) -> float:
        if not self.search_logs:
            return 0.0
        total_results = sum(log["results"]["total_count"] for log in self.search_logs)
        return total_results / len(self.search_logs)

    def _get_most_common_query_type(self) -> str:
        if not self.search_logs:
            return "standard"
        query_types = [log["query"]["query_type"] for log in self.search_logs]
        return Counter(query_types).most_common(1)[0][0] if query_types else "standard"

    def _get_top_queries(self, limit: int) -> List[Tuple[str, int]]:
        return self.query_patterns.most_common(limit)

    def _update_trending_queries(self, query_text: str):
        """Update trending queries list"""
        # Simple trending logic - in production would use more sophisticated algorithm
        trending = self.realtime_stats.get("trending_queries", [])

        # Add or update query
        found = False
        for item in trending:
            if item["query"] == query_text:
                item["count"] += 1
                item["last_seen"] = datetime.now()
                found = True
                break

        if not found:
            trending.append(
                {
                    "query": query_text,
                    "count": 1,
                    "first_seen": datetime.now(),
                    "last_seen": datetime.now(),
                }
            )

        # Sort by count and keep top 10
        trending.sort(key=lambda x: x["count"], reverse=True)
        self.realtime_stats["trending_queries"] = trending[:10]
