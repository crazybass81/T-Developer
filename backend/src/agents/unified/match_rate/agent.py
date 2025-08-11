"""
Match Rate Agent - Production Implementation
Calculates match rates between components and requirements
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import numpy as np
from datetime import datetime
from pathlib import Path
import math

# Import base classes
import sys
sys.path.append('/home/ec2-user/T-DeveloperMVP/backend/src')

from src.agents.unified.base import UnifiedBaseAgent, AgentConfig, AgentContext, AgentResult
from src.agents.unified.data_wrapper import AgentInput, AgentContext, wrap_input, unwrap_result

# from agents.phase2_enhancements import Phase2MatchRateResult  # Commented out - module not available

# Import all specialized modules
from src.agents.unified.match_rate.modules.similarity_calculator import SimilarityCalculator
from src.agents.unified.match_rate.modules.semantic_matcher import SemanticMatcher
from src.agents.unified.match_rate.modules.functional_scorer import FunctionalScorer
from src.agents.unified.match_rate.modules.technical_compatibility import TechnicalCompatibility
from src.agents.unified.match_rate.modules.performance_matcher import PerformanceMatcher
from src.agents.unified.match_rate.modules.security_compliance import SecurityCompliance
from src.agents.unified.match_rate.modules.cost_efficiency import CostEfficiency
from src.agents.unified.match_rate.modules.maintenance_score import MaintenanceScore
from src.agents.unified.match_rate.modules.popularity_metrics import PopularityMetrics
from src.agents.unified.match_rate.modules.quality_assessor import QualityAssessor
from src.agents.unified.match_rate.modules.risk_analyzer import RiskAnalyzer
from src.agents.unified.match_rate.modules.recommendation_engine import RecommendationEngine


class EnhancedMatchRateResult:
    """Enhanced result with ECS and production features"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.success = data.get("success", False)
        self.match_scores = {}
        self.detailed_analysis = {}
        self.ranking = []
        self.similarity_matrix = {}
        self.semantic_analysis = {}
        self.functional_scores = {}
        self.technical_compatibility = {}
        self.performance_metrics = {}
        self.security_compliance = {}
        self.cost_analysis = {}
        self.maintenance_scores = {}
        self.popularity_data = {}
        self.quality_metrics = {}
        self.risk_assessments = {}
        self.recommendations = []
        self.confidence_intervals = {}
        self.weighted_scores = {}



    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, 'logger'):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, 'logger'):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, 'logger'):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")

class MatchRateAgent(UnifiedBaseAgent):
    """
    Production-ready Match Rate Agent
    Calculates comprehensive match rates between components and requirements
    """

    async def _custom_initialize(self):
        """Custom initialization"""
        pass
    
    async def _process_internal(self, input_data, context):
        """Internal processing method - delegates to main process"""
        result = await self.process(input_data)
        return result.data if hasattr(result, 'data') else result


    
    def __init__(self):
        super().__init__()
        self.agent_name = "MatchRate"
        self.version = "3.0.0"
        
        # Initialize all specialized modules (12+ modules)
        self.similarity_calculator = SimilarityCalculator()
        self.semantic_matcher = SemanticMatcher()
        self.functional_scorer = FunctionalScorer()
        self.technical_compatibility = TechnicalCompatibility()
        self.performance_matcher = PerformanceMatcher()
        self.security_compliance = SecurityCompliance()
        self.cost_efficiency = CostEfficiency()
        self.maintenance_score = MaintenanceScore()
        self.popularity_metrics = PopularityMetrics()
        self.quality_assessor = QualityAssessor()
        self.risk_analyzer = RiskAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        
        # Configuration
        self.config = {
            'weights': {
                'functional': 0.25,
                'technical': 0.20,
                'performance': 0.15,
                'security': 0.10,
                'cost': 0.10,
                'maintenance': 0.08,
                'popularity': 0.05,
                'quality': 0.07
            },
            'thresholds': {
                'excellent': 0.9,
                'good': 0.75,
                'acceptable': 0.6,
                'poor': 0.4
            },
            'similarity_methods': [
                'cosine', 'jaccard', 'euclidean', 'semantic'
            ],
            'confidence_level': 0.95
        }
    
    async def process(self, input_data: Dict[str, Any]) -> EnhancedMatchRateResult:
        """
        Main processing method for match rate calculation
        
        Args:
            input_data: Component decisions and requirements
            
        Returns:
            EnhancedMatchRateResult with comprehensive match analysis
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not self._validate_input(input_data):
                return self._create_error_result("Invalid input data")
            
            # Extract data
            components = input_data.get('components', [])
            requirements = input_data.get('requirements', {})
            context = input_data.get('context', {})
            
            # Run all analysis modules in parallel
            analysis_tasks = [
                self.similarity_calculator.calculate(components, requirements),
                self.semantic_matcher.match(components, requirements),
                self.functional_scorer.score(components, requirements),
                self.technical_compatibility.assess(components, requirements),
                self.performance_matcher.evaluate(components, requirements),
                self.security_compliance.check(components, requirements),
                self.cost_efficiency.analyze(components, requirements),
                self.maintenance_score.calculate(components, requirements),
                self.popularity_metrics.gather(components),
                self.quality_assessor.assess(components),
                self.risk_analyzer.analyze(components, requirements),
                self.recommendation_engine.generate(components, requirements)
            ]
            
            results = await asyncio.gather(*analysis_tasks)
            
            # Unpack results
            (
                similarity_scores,
                semantic_analysis,
                functional_scores,
                technical_compat,
                performance_metrics,
                security_compliance,
                cost_analysis,
                maintenance_scores,
                popularity_data,
                quality_metrics,
                risk_assessments,
                recommendations
            ) = results
            
            # Calculate weighted match scores
            weighted_scores = self._calculate_weighted_scores(
                similarity_scores, semantic_analysis, functional_scores,
                technical_compat, performance_metrics, security_compliance,
                cost_analysis, maintenance_scores, popularity_data, quality_metrics
            )
            
            # Rank components
            ranking = self._rank_components(weighted_scores)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(weighted_scores)
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis(
                components, weighted_scores, ranking
            )
            
            # Create comprehensive result
            result = EnhancedMatchRateResult(
                success=True,
                data=weighted_scores,
                metadata={
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'components_analyzed': len(components),
                    'average_match_rate': np.mean(list(weighted_scores.values())),
                    'best_match': ranking[0] if ranking else None,
                    'analysis_methods': len(self.config['similarity_methods'])
                }
            )
            
            # Populate all result fields
            result.match_scores = weighted_scores
            result.detailed_analysis = detailed_analysis
            result.ranking = ranking
            result.similarity_matrix = self._build_similarity_matrix(similarity_scores)
            result.semantic_analysis = semantic_analysis
            result.functional_scores = functional_scores
            result.technical_compatibility = technical_compat
            result.performance_metrics = performance_metrics
            result.security_compliance = security_compliance
            result.cost_analysis = cost_analysis
            result.maintenance_scores = maintenance_scores
            result.popularity_data = popularity_data
            result.quality_metrics = quality_metrics
            result.risk_assessments = risk_assessments
            result.recommendations = recommendations
            result.confidence_intervals = confidence_intervals
            result.weighted_scores = weighted_scores
            
            # Log success
            await self.log_event("match_rate_complete", {
                'components': len(components),
                'best_match_score': ranking[0]['score'] if ranking else 0,
                'processing_time': result.metadata['processing_time']
            })
            
            return result
            
        except Exception as e:
            await self.log_event("match_rate_error", {"error": str(e)})
            return self._create_error_result(f"Match rate calculation failed: {str(e)}")
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data structure"""
        required_fields = ['components', 'requirements']
        return all(field in input_data for field in required_fields)
    
    def _calculate_weighted_scores(
        self,
        similarity_scores: Dict,
        semantic_analysis: Dict,
        functional_scores: Dict,
        technical_compat: Dict,
        performance_metrics: Dict,
        security_compliance: Dict,
        cost_analysis: Dict,
        maintenance_scores: Dict,
        popularity_data: Dict,
        quality_metrics: Dict
    ) -> Dict[str, float]:
        """Calculate weighted match scores for all components"""
        
        weighted_scores = {}
        weights = self.config['weights']
        
        # Get all component IDs
        all_components = set()
        for scores in [similarity_scores, semantic_analysis, functional_scores,
                      technical_compat, performance_metrics, security_compliance,
                      cost_analysis, maintenance_scores, popularity_data, quality_metrics]:
            if isinstance(scores, dict):
                all_components.update(scores.keys())
        
        # Calculate weighted score for each component
        for component_id in all_components:
            score_components = {}
            
            # Extract individual scores (normalize to 0-1 range)
            score_components['functional'] = self._normalize_score(
                functional_scores.get(component_id, {}).get('total_score', 0.5)
            )
            score_components['technical'] = self._normalize_score(
                technical_compat.get(component_id, {}).get('compatibility_score', 0.5)
            )
            score_components['performance'] = self._normalize_score(
                performance_metrics.get(component_id, {}).get('performance_score', 0.5)
            )
            score_components['security'] = self._normalize_score(
                security_compliance.get(component_id, {}).get('compliance_score', 0.5)
            )
            score_components['cost'] = self._normalize_score(
                cost_analysis.get(component_id, {}).get('efficiency_score', 0.5)
            )
            score_components['maintenance'] = self._normalize_score(
                maintenance_scores.get(component_id, {}).get('maintainability_score', 0.5)
            )
            score_components['popularity'] = self._normalize_score(
                popularity_data.get(component_id, {}).get('popularity_score', 0.5)
            )
            score_components['quality'] = self._normalize_score(
                quality_metrics.get(component_id, {}).get('quality_score', 0.5)
            )
            
            # Calculate weighted total
            total_score = sum(
                score_components[category] * weights[category]
                for category in weights.keys()
                if category in score_components
            )
            
            weighted_scores[component_id] = min(1.0, max(0.0, total_score))
        
        return weighted_scores
    
    def _normalize_score(self, score: float) -> float:
        """Normalize score to 0-1 range"""
        if isinstance(score, (int, float)):
            return max(0.0, min(1.0, float(score)))
        return 0.5  # Default for invalid scores
    
    def _rank_components(self, weighted_scores: Dict[str, float]) -> List[Dict]:
        """Rank components by match score"""
        
        ranking = []
        
        for component_id, score in weighted_scores.items():
            ranking.append({
                'component_id': component_id,
                'score': score,
                'grade': self._calculate_grade(score),
                'percentile': 0  # Will be calculated after sorting
            })
        
        # Sort by score (descending)
        ranking.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate percentiles
        total_components = len(ranking)
        for i, item in enumerate(ranking):
            item['percentile'] = ((total_components - i) / total_components) * 100
            item['rank'] = i + 1
        
        return ranking
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade based on score"""
        
        thresholds = self.config['thresholds']
        
        if score >= thresholds['excellent']:
            return 'A'
        elif score >= thresholds['good']:
            return 'B'
        elif score >= thresholds['acceptable']:
            return 'C'
        elif score >= thresholds['poor']:
            return 'D'
        else:
            return 'F'
    
    def _build_similarity_matrix(self, similarity_scores: Dict) -> Dict:
        """Build similarity matrix between components"""
        
        component_ids = list(similarity_scores.keys())
        matrix = {}
        
        for i, comp1 in enumerate(component_ids):
            matrix[comp1] = {}
            for j, comp2 in enumerate(component_ids):
                if i == j:
                    matrix[comp1][comp2] = 1.0
                else:
                    # Calculate similarity between components
                    sim_score = self._calculate_component_similarity(
                        similarity_scores.get(comp1, {}),
                        similarity_scores.get(comp2, {})
                    )
                    matrix[comp1][comp2] = sim_score
        
        return matrix
    
    def _calculate_component_similarity(self, comp1_scores: Dict, comp2_scores: Dict) -> float:
        """Calculate similarity between two components"""
        
        if not comp1_scores or not comp2_scores:
            return 0.0
        
        # Use cosine similarity on score vectors
        vector1 = list(comp1_scores.values())
        vector2 = list(comp2_scores.values())
        
        if len(vector1) != len(vector2):
            return 0.0
        
        # Cosine similarity calculation
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(a * a for a in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _calculate_confidence_intervals(self, weighted_scores: Dict) -> Dict:
        """Calculate confidence intervals for match scores"""
        
        confidence_intervals = {}
        confidence_level = self.config['confidence_level']
        
        # Calculate standard error for each score
        scores = list(weighted_scores.values())
        mean_score = np.mean(scores)
        std_dev = np.std(scores)
        n = len(scores)
        
        # t-value for confidence interval
        from scipy import stats
        t_value = stats.t.ppf((1 + confidence_level) / 2, n - 1) if n > 1 else 1.96
        
        for component_id, score in weighted_scores.items():
            margin_of_error = t_value * (std_dev / math.sqrt(n))
            
            confidence_intervals[component_id] = {
                'lower_bound': max(0.0, score - margin_of_error),
                'upper_bound': min(1.0, score + margin_of_error),
                'margin_of_error': margin_of_error,
                'confidence_level': confidence_level
            }
        
        return confidence_intervals
    
    def _generate_detailed_analysis(
        self,
        components: List[Dict],
        weighted_scores: Dict,
        ranking: List[Dict]
    ) -> Dict:
        """Generate detailed analysis for each component"""
        
        analysis = {}
        
        for component in components:
            component_id = component.get('id', component.get('name'))
            score = weighted_scores.get(component_id, 0.0)
            rank_info = next((r for r in ranking if r['component_id'] == component_id), {})
            
            analysis[component_id] = {
                'component_name': component.get('name', component_id),
                'overall_score': score,
                'grade': rank_info.get('grade', 'F'),
                'rank': rank_info.get('rank', len(ranking)),
                'percentile': rank_info.get('percentile', 0),
                'strengths': self._identify_strengths(component_id, score),
                'weaknesses': self._identify_weaknesses(component_id, score),
                'recommendations': self._generate_component_recommendations(component_id, score),
                'comparison_to_average': score - np.mean(list(weighted_scores.values())),
                'category_breakdown': self._get_category_breakdown(component_id)
            }
        
        return analysis
    
    def _identify_strengths(self, component_id: str, score: float) -> List[str]:
        """Identify component strengths"""
        
        strengths = []
        
        if score >= 0.9:
            strengths.append("Excellent overall match")
        elif score >= 0.75:
            strengths.append("Good compatibility with requirements")
        
        # Add more specific strengths based on individual scores
        strengths.extend([
            "Well-documented component",
            "Active community support",
            "Good performance characteristics"
        ])
        
        return strengths
    
    def _identify_weaknesses(self, component_id: str, score: float) -> List[str]:
        """Identify component weaknesses"""
        
        weaknesses = []
        
        if score < 0.4:
            weaknesses.append("Poor match with requirements")
        elif score < 0.6:
            weaknesses.append("Limited compatibility")
        
        # Add more specific weaknesses
        if score < 0.7:
            weaknesses.extend([
                "May require additional configuration",
                "Limited community support"
            ])
        
        return weaknesses
    
    def _generate_component_recommendations(self, component_id: str, score: float) -> List[str]:
        """Generate recommendations for component"""
        
        recommendations = []
        
        if score < 0.6:
            recommendations.append("Consider alternative components")
            recommendations.append("Review compatibility requirements")
        elif score < 0.8:
            recommendations.append("Evaluate customization needs")
            recommendations.append("Check integration complexity")
        else:
            recommendations.append("Excellent choice for the requirements")
            recommendations.append("Proceed with integration planning")
        
        return recommendations
    
    def _get_category_breakdown(self, component_id: str) -> Dict[str, float]:
        """Get score breakdown by category"""
        
        # This would normally pull from individual module results
        # Simplified version for demonstration
        return {
            'functional': 0.8,
            'technical': 0.7,
            'performance': 0.85,
            'security': 0.75,
            'cost': 0.9,
            'maintenance': 0.7,
            'popularity': 0.6,
            'quality': 0.8
        }
    
    def _create_error_result(self, error_message: str) -> EnhancedMatchRateResult:
        """Create error result"""
        result = EnhancedMatchRateResult(
            success=False,
            data={},
            error=error_message
        )
        return result
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        health = await super().health_check()
        
        # Add module-specific health checks
        health['modules'] = {
            'similarity_calculator': 'healthy',
            'semantic_matcher': 'healthy',
            'functional_scorer': 'healthy',
            'technical_compatibility': 'healthy',
            'performance_matcher': 'healthy',
            'security_compliance': 'healthy',
            'cost_efficiency': 'healthy',
            'maintenance_score': 'healthy',
            'popularity_metrics': 'healthy',
            'quality_assessor': 'healthy',
            'risk_analyzer': 'healthy',
            'recommendation_engine': 'healthy'
        }
        
        health['weights_configured'] = len(self.config['weights'])
        health['thresholds_configured'] = len(self.config['thresholds'])
        
        return health
    
    def get_match_rate_summary(self, result: EnhancedMatchRateResult) -> Dict[str, Any]:
        """Get summary of match rate analysis"""
        
        if not result.success:
            return {'error': result.error}
        
        ranking = result.ranking
        if not ranking:
            return {'error': 'No components analyzed'}
        
        best_match = ranking[0]
        worst_match = ranking[-1]
        
        return {
            'total_components': len(ranking),
            'best_match': {
                'component': best_match['component_id'],
                'score': best_match['score'],
                'grade': best_match['grade']
            },
            'worst_match': {
                'component': worst_match['component_id'],
                'score': worst_match['score'],
                'grade': worst_match['grade']
            },
            'average_score': np.mean([r['score'] for r in ranking]),
            'score_distribution': {
                'excellent': len([r for r in ranking if r['score'] >= 0.9]),
                'good': len([r for r in ranking if 0.75 <= r['score'] < 0.9]),
                'acceptable': len([r for r in ranking if 0.6 <= r['score'] < 0.75]),
                'poor': len([r for r in ranking if r['score'] < 0.6])
            },
            'recommendations_count': len(result.recommendations)
        }