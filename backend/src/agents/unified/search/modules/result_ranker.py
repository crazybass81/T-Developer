"""
Result Ranker Module
Advanced ranking algorithms for search results
"""

from typing import Dict, List, Any, Optional, Tuple
import math
from datetime import datetime


class ResultRanker:
    """Advanced result ranking with multiple algorithms"""
    
    def __init__(self):
        self.ranking_algorithms = {
            'relevance': self._rank_by_relevance,
            'popularity': self._rank_by_popularity,
            'quality': self._rank_by_quality,
            'recency': self._rank_by_recency,
            'hybrid': self._rank_by_hybrid,
            'ml_based': self._rank_by_ml_features
        }
        
        # Ranking weights for different factors
        self.ranking_weights = {
            'relevance_score': 0.4,
            'popularity_score': 0.2,
            'quality_score': 0.2,
            'recency_score': 0.1,
            'user_preference': 0.05,
            'diversity': 0.05
        }
        
        # Category-specific weights
        self.category_weights = {
            'ui_framework': {'usability': 1.3, 'community': 1.2},
            'backend_framework': {'performance': 1.3, 'security': 1.2},
            'database': {'reliability': 1.4, 'scalability': 1.2},
            'testing': {'simplicity': 1.2, 'coverage': 1.3}
        }
        
    async def rank(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any],
        algorithm: str = 'hybrid'
    ) -> List[Dict[str, Any]]:
        """Rank search results using specified algorithm"""
        
        if not results:
            return results
        
        # Apply ranking algorithm
        if algorithm in self.ranking_algorithms:
            ranked_results = await self.ranking_algorithms[algorithm](
                results, query, requirements
            )
        else:
            ranked_results = await self._rank_by_hybrid(results, query, requirements)
        
        # Add ranking metadata
        for i, result in enumerate(ranked_results):
            result['rank'] = i + 1
            result['ranking_algorithm'] = algorithm
            result['ranking_timestamp'] = datetime.now().isoformat()
        
        return ranked_results
    
    async def _rank_by_relevance(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank by relevance score only"""
        
        # Sort by existing score (relevance)
        sorted_results = sorted(
            results,
            key=lambda x: x.get('score', 0),
            reverse=True
        )
        
        return sorted_results
    
    async def _rank_by_popularity(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank by popularity metrics"""
        
        for result in results:
            popularity_score = self._calculate_popularity_score(result)
            result['popularity_rank_score'] = popularity_score
        
        sorted_results = sorted(
            results,
            key=lambda x: x.get('popularity_rank_score', 0),
            reverse=True
        )
        
        return sorted_results
    
    async def _rank_by_quality(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank by quality indicators"""
        
        for result in results:
            quality_score = self._calculate_quality_score(result)
            result['quality_rank_score'] = quality_score
        
        sorted_results = sorted(
            results,
            key=lambda x: x.get('quality_rank_score', 0),
            reverse=True
        )
        
        return sorted_results
    
    async def _rank_by_recency(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank by recency (most recently updated first)"""
        
        for result in results:
            recency_score = self._calculate_recency_score(result)
            result['recency_rank_score'] = recency_score
        
        sorted_results = sorted(
            results,
            key=lambda x: x.get('recency_rank_score', 0),
            reverse=True
        )
        
        return sorted_results
    
    async def _rank_by_hybrid(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Hybrid ranking combining multiple factors"""
        
        for result in results:
            # Calculate individual scores
            relevance_score = result.get('score', 0)
            popularity_score = self._calculate_popularity_score(result)
            quality_score = self._calculate_quality_score(result)
            recency_score = self._calculate_recency_score(result)
            requirement_score = self._calculate_requirement_match_score(result, requirements)
            diversity_score = self._calculate_diversity_score(result, results)
            
            # Normalize scores to 0-1 range
            relevance_normalized = self._normalize_score(relevance_score, 0, 10)
            popularity_normalized = self._normalize_score(popularity_score, 0, 10)
            quality_normalized = self._normalize_score(quality_score, 0, 10)
            recency_normalized = self._normalize_score(recency_score, 0, 1)
            requirement_normalized = self._normalize_score(requirement_score, 0, 1)
            diversity_normalized = self._normalize_score(diversity_score, 0, 1)
            
            # Apply category-specific weights
            category_boost = self._get_category_boost(result, requirements)
            
            # Calculate weighted hybrid score
            hybrid_score = (
                relevance_normalized * self.ranking_weights['relevance_score'] +
                popularity_normalized * self.ranking_weights['popularity_score'] +
                quality_normalized * self.ranking_weights['quality_score'] +
                recency_normalized * self.ranking_weights['recency_score'] +
                requirement_normalized * self.ranking_weights['user_preference'] +
                diversity_normalized * self.ranking_weights['diversity']
            ) * category_boost
            
            result['hybrid_rank_score'] = hybrid_score
            result['ranking_details'] = {
                'relevance': relevance_normalized,
                'popularity': popularity_normalized,
                'quality': quality_normalized,
                'recency': recency_normalized,
                'requirements': requirement_normalized,
                'diversity': diversity_normalized,
                'category_boost': category_boost
            }
        
        sorted_results = sorted(
            results,
            key=lambda x: x.get('hybrid_rank_score', 0),
            reverse=True
        )
        
        return sorted_results
    
    async def _rank_by_ml_features(
        self,
        results: List[Dict[str, Any]],
        query: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ML-based ranking using feature vectors"""
        
        for result in results:
            feature_vector = self._extract_ml_features(result, query, requirements)
            ml_score = self._calculate_ml_score(feature_vector)
            result['ml_rank_score'] = ml_score
            result['feature_vector'] = feature_vector
        
        sorted_results = sorted(
            results,
            key=lambda x: x.get('ml_rank_score', 0),
            reverse=True
        )
        
        return sorted_results
    
    def _calculate_popularity_score(self, result: Dict[str, Any]) -> float:
        """Calculate popularity score based on various metrics"""
        
        # GitHub stars (if available)
        github_stars = result.get('github_stars', 0)
        stars_score = min(math.log10(github_stars + 1) / 6, 1.0) * 3  # Max 3 points
        
        # Downloads (npm, pypi, etc.)
        downloads = max(
            result.get('npm_downloads', 0),
            result.get('pypi_downloads', 0),
            result.get('downloads', 0)
        )
        downloads_score = min(math.log10(downloads + 1) / 8, 1.0) * 3  # Max 3 points
        
        # Community metrics
        popularity_rating = result.get('popularity', 5.0)  # 0-10 scale
        community_score = popularity_rating / 10.0 * 2  # Max 2 points
        
        # Contributors/maintainers
        contributors = result.get('contributors', 1)
        contributor_score = min(math.log10(contributors) / 3, 1.0) * 1  # Max 1 point
        
        # Recent activity
        activity_score = self._calculate_activity_score(result)  # Max 1 point
        
        total_score = stars_score + downloads_score + community_score + contributor_score + activity_score
        return min(total_score, 10.0)
    
    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score based on code metrics and indicators"""
        
        # Base quality rating
        quality_rating = result.get('quality', 5.0)  # 0-10 scale
        base_score = quality_rating / 10.0 * 4  # Max 4 points
        
        # Documentation quality
        doc_completeness = result.get('documentation_score', 0.5)  # 0-1 scale
        doc_score = doc_completeness * 2  # Max 2 points
        
        # Test coverage
        test_coverage = result.get('test_coverage', 0.5)  # 0-1 scale
        test_score = test_coverage * 1.5  # Max 1.5 points
        
        # Code quality metrics
        code_quality = result.get('code_quality_score', 0.5)  # 0-1 scale
        code_score = code_quality * 1.5  # Max 1.5 points
        
        # Security score
        security_score = result.get('security_score', 0.5)  # 0-1 scale
        security_points = security_score * 1  # Max 1 point
        
        total_score = base_score + doc_score + test_score + code_score + security_points
        return min(total_score, 10.0)
    
    def _calculate_recency_score(self, result: Dict[str, Any]) -> float:
        """Calculate recency score based on last update"""
        
        last_updated = result.get('last_updated')
        if not last_updated:
            return 0.5  # Neutral score if no date
        
        try:
            if isinstance(last_updated, str):
                update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            else:
                update_date = last_updated
                
            now = datetime.now(update_date.tzinfo if update_date.tzinfo else None)
            days_ago = (now - update_date).days
            
            # Scoring based on recency
            if days_ago <= 7:
                return 1.0  # Very recent
            elif days_ago <= 30:
                return 0.9  # Recent
            elif days_ago <= 90:
                return 0.8  # Moderately recent
            elif days_ago <= 180:
                return 0.6  # Somewhat old
            elif days_ago <= 365:
                return 0.4  # Old
            else:
                return 0.2  # Very old
                
        except (ValueError, AttributeError, TypeError):
            return 0.5  # Default if parsing fails
    
    def _calculate_requirement_match_score(
        self, 
        result: Dict[str, Any], 
        requirements: Dict[str, Any]
    ) -> float:
        """Calculate how well the result matches user requirements"""
        
        if not requirements:
            return 0.5  # Neutral if no requirements
        
        match_score = 0.0
        total_requirements = 0
        
        # Technology requirements
        if 'technology' in requirements:
            total_requirements += 1
            required_tech = requirements['technology'].lower()
            result_tech = result.get('technology', '').lower()
            
            if required_tech == result_tech:
                match_score += 1.0
            elif required_tech in result_tech or result_tech in required_tech:
                match_score += 0.7
        
        # Category requirements
        if 'category' in requirements:
            total_requirements += 1
            required_category = requirements['category'].lower()
            result_category = result.get('category', '').lower()
            
            if required_category == result_category:
                match_score += 1.0
            elif required_category in result_category:
                match_score += 0.8
        
        # Feature requirements
        if 'features' in requirements:
            total_requirements += 1
            required_features = set(req.lower() for req in requirements['features'])
            result_features = set(feat.lower() for feat in result.get('features', []))
            
            if required_features:
                feature_overlap = len(required_features & result_features)
                feature_match = feature_overlap / len(required_features)
                match_score += feature_match
        
        # Performance requirements
        if 'performance' in requirements:
            total_requirements += 1
            min_performance = requirements['performance']
            result_performance = result.get('performance_score', 5.0)
            
            if result_performance >= min_performance:
                match_score += 1.0
            else:
                match_score += result_performance / min_performance
        
        # License requirements
        if 'license' in requirements:
            total_requirements += 1
            acceptable_licenses = [lic.lower() for lic in requirements['license']]
            result_license = result.get('license', '').lower()
            
            if result_license in acceptable_licenses:
                match_score += 1.0
        
        return match_score / total_requirements if total_requirements > 0 else 0.5
    
    def _calculate_diversity_score(
        self, 
        result: Dict[str, Any], 
        all_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate diversity score to promote varied results"""
        
        result_category = result.get('category', '')
        result_technology = result.get('technology', '')
        
        # Count similar results
        similar_category_count = sum(
            1 for r in all_results 
            if r.get('category') == result_category and r != result
        )
        
        similar_tech_count = sum(
            1 for r in all_results 
            if r.get('technology') == result_technology and r != result
        )
        
        # Penalize overrepresented categories/technologies
        category_penalty = min(similar_category_count * 0.1, 0.5)
        tech_penalty = min(similar_tech_count * 0.1, 0.5)
        
        diversity_score = 1.0 - category_penalty - tech_penalty
        return max(diversity_score, 0.1)  # Minimum score
    
    def _get_category_boost(
        self, 
        result: Dict[str, Any], 
        requirements: Dict[str, Any]
    ) -> float:
        """Get category-specific boost based on requirements"""
        
        category = result.get('category', '').lower().replace(' ', '_')
        
        if category not in self.category_weights:
            return 1.0
        
        boost = 1.0
        category_boosts = self.category_weights[category]
        
        # Apply requirement-specific boosts
        req_text = str(requirements).lower()
        
        for boost_type, boost_value in category_boosts.items():
            if boost_type in req_text:
                boost *= boost_value
        
        return boost
    
    def _extract_ml_features(
        self, 
        result: Dict[str, Any], 
        query: Dict[str, Any], 
        requirements: Dict[str, Any]
    ) -> List[float]:
        """Extract feature vector for ML-based ranking"""
        
        features = []
        
        # Basic scores (normalized to 0-1)
        features.append(self._normalize_score(result.get('score', 0), 0, 10))
        features.append(self._normalize_score(result.get('popularity', 0), 0, 10))
        features.append(self._normalize_score(result.get('quality', 0), 0, 10))
        features.append(self._calculate_recency_score(result))
        
        # Text matching features
        query_terms = query.get('terms', [])
        name_matches = sum(1 for term in query_terms if term.lower() in result.get('name', '').lower())
        features.append(name_matches / len(query_terms) if query_terms else 0)
        
        # Category encoding (binary features for top categories)
        top_categories = ['ui_framework', 'backend_framework', 'database', 'testing', 'utility']
        category = result.get('category', '').lower().replace(' ', '_')
        for cat in top_categories:
            features.append(1.0 if cat == category else 0.0)
        
        # Numerical features (log-scaled and normalized)
        features.append(self._normalize_score(math.log10(result.get('github_stars', 1)), 0, 6))
        features.append(self._normalize_score(math.log10(result.get('npm_downloads', 1)), 0, 8))
        
        return features
    
    def _calculate_ml_score(self, features: List[float]) -> float:
        """Simple ML scoring function (in production, use trained model)"""
        
        # Simple weighted sum (replace with trained model in production)
        weights = [
            0.3, 0.2, 0.2, 0.1,  # Basic scores
            0.1,                  # Name matches
            0.02, 0.02, 0.01, 0.01, 0.01,  # Category features
            0.05, 0.05            # Numerical features
        ]
        
        # Ensure we have enough weights
        weights = weights[:len(features)]
        if len(weights) < len(features):
            weights.extend([0.01] * (len(features) - len(weights)))
        
        score = sum(f * w for f, w in zip(features, weights))
        return max(0, min(score, 1))  # Clamp to 0-1
    
    def _calculate_activity_score(self, result: Dict[str, Any]) -> float:
        """Calculate activity score based on recent commits, releases, etc."""
        
        # Recent commits
        recent_commits = result.get('recent_commits', 0)
        commit_score = min(recent_commits / 10, 1.0) * 0.4
        
        # Recent releases
        recent_releases = result.get('recent_releases', 0)
        release_score = min(recent_releases / 3, 1.0) * 0.3
        
        # Issue activity
        issues_closed = result.get('issues_closed_recently', 0)
        issue_score = min(issues_closed / 20, 1.0) * 0.3
        
        return commit_score + release_score + issue_score
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize score to 0-1 range"""
        
        if max_val == min_val:
            return 0.5
        
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(normalized, 1))
    
    async def get_ranking_explanation(
        self, 
        result: Dict[str, Any], 
        rank: int
    ) -> Dict[str, Any]:
        """Get explanation for why a result was ranked at its position"""
        
        explanation = {
            'rank': rank,
            'component_name': result.get('name'),
            'overall_score': result.get('hybrid_rank_score', 0),
            'factors': {}
        }
        
        if 'ranking_details' in result:
            details = result['ranking_details']
            explanation['factors'] = {
                'relevance_contribution': details.get('relevance', 0) * self.ranking_weights['relevance_score'],
                'popularity_contribution': details.get('popularity', 0) * self.ranking_weights['popularity_score'],
                'quality_contribution': details.get('quality', 0) * self.ranking_weights['quality_score'],
                'recency_contribution': details.get('recency', 0) * self.ranking_weights['recency_score'],
                'requirements_contribution': details.get('requirements', 0) * self.ranking_weights['user_preference'],
                'diversity_contribution': details.get('diversity', 0) * self.ranking_weights['diversity'],
                'category_boost': details.get('category_boost', 1.0)
            }
        
        return explanation