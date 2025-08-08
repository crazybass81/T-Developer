"""
Match Rate Agent Core Implementation
Phase 4 Tasks 4.41-4.50: 매칭률 계산 및 최적화 에이전트
"""

import json
import logging
import os
import time
import asyncio
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict
import numpy as np
from scipy import spatial
import hashlib

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from botocore.exceptions import ClientError

# Agno Framework 통합
try:
    from agno.agent import Agent
    from agno.models.aws import AwsBedrock
    from agno.memory import ConversationSummaryMemory
    from agno.tools import Tool
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

# Production 로깅 설정
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# AWS 클라이언트
ssm = boto3.client('ssm')
secrets = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')


class MatchType(Enum):
    """매칭 타입"""
    EXACT = "exact"  # 정확한 매칭
    PARTIAL = "partial"  # 부분 매칭
    SEMANTIC = "semantic"  # 의미적 매칭
    PATTERN = "pattern"  # 패턴 매칭
    FUZZY = "fuzzy"  # 퍼지 매칭
    COMPOSITE = "composite"  # 복합 매칭


class MatchingStrategy(Enum):
    """매칭 전략"""
    GREEDY = "greedy"  # 탐욕적 매칭
    OPTIMAL = "optimal"  # 최적 매칭
    WEIGHTED = "weighted"  # 가중치 기반 매칭
    HIERARCHICAL = "hierarchical"  # 계층적 매칭
    ENSEMBLE = "ensemble"  # 앙상블 매칭


@dataclass
class ComponentMatch:
    """컴포넌트 매치"""
    requirement_id: str
    component_id: str
    match_type: MatchType
    match_score: float
    confidence: float
    explanation: str
    metadata: Dict[str, Any]


@dataclass
class MatchingResult:
    """매칭 결과"""
    overall_match_rate: float
    component_matches: List[ComponentMatch]
    unmatched_requirements: List[str]
    coverage_analysis: Dict[str, float]
    optimization_suggestions: List[Dict[str, Any]]
    confidence_distribution: Dict[str, float]
    metadata: Dict[str, Any]


@dataclass
class TemplateMatch:
    """템플릿 매치"""
    template_id: str
    template_name: str
    category: str
    match_score: float
    matched_components: List[str]
    missing_components: List[str]
    adaptations_needed: List[Dict[str, Any]]
    reusability_score: float


@dataclass
class SimilarityMetrics:
    """유사도 메트릭"""
    cosine_similarity: float
    jaccard_similarity: float
    levenshtein_distance: int
    semantic_similarity: float
    structural_similarity: float
    weighted_average: float


@dataclass
class OptimizationRecommendation:
    """최적화 권장사항"""
    recommendation_type: str
    target_component: str
    improvement_potential: float
    implementation_effort: str  # low, medium, high
    expected_impact: Dict[str, float]
    action_items: List[str]
    priority: int


class MatchingEngine(Tool):
    """매칭 엔진 도구 (Agno Tool)"""
    
    def __init__(self):
        super().__init__(
            name="matching_engine",
            description="Calculate and optimize component matching rates"
        )
        self._init_similarity_models()
    
    def _init_similarity_models(self):
        """유사도 모델 초기화"""
        self.embeddings_cache = {}
        self.similarity_thresholds = {
            MatchType.EXACT: 1.0,
            MatchType.PARTIAL: 0.7,
            MatchType.SEMANTIC: 0.6,
            MatchType.PATTERN: 0.5,
            MatchType.FUZZY: 0.4
        }
    
    async def run(
        self,
        requirements: List[Dict[str, Any]],
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """매칭 실행"""
        matches = []
        
        for req in requirements:
            best_match = await self._find_best_match(req, components)
            if best_match:
                matches.append(best_match)
        
        # 매칭률 계산
        match_rate = len(matches) / len(requirements) if requirements else 0
        
        return {
            "match_rate": match_rate,
            "matches": matches,
            "unmatched": self._find_unmatched(requirements, matches)
        }
    
    async def _find_best_match(
        self,
        requirement: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """최적 매치 찾기"""
        best_score = 0
        best_component = None
        
        for component in components:
            score = await self._calculate_similarity(requirement, component)
            if score > best_score:
                best_score = score
                best_component = component
        
        if best_component and best_score > 0.3:  # 최소 임계값
            return {
                "requirement_id": requirement.get("id"),
                "component_id": best_component.get("id"),
                "score": best_score,
                "type": self._determine_match_type(best_score)
            }
        
        return None
    
    async def _calculate_similarity(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """유사도 계산"""
        # 텍스트 유사도
        text_sim = self._text_similarity(
            requirement.get("description", ""),
            component.get("description", "")
        )
        
        # 속성 유사도
        attr_sim = self._attribute_similarity(
            requirement.get("attributes", {}),
            component.get("attributes", {})
        )
        
        # 가중 평균
        return 0.6 * text_sim + 0.4 * attr_sim
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        # 간단한 자카드 유사도
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _attribute_similarity(self, attrs1: Dict, attrs2: Dict) -> float:
        """속성 유사도 계산"""
        if not attrs1 or not attrs2:
            return 0.0
        
        common_keys = set(attrs1.keys()).intersection(set(attrs2.keys()))
        if not common_keys:
            return 0.0
        
        matches = sum(1 for k in common_keys if attrs1[k] == attrs2[k])
        return matches / len(common_keys)
    
    def _determine_match_type(self, score: float) -> str:
        """매치 타입 결정"""
        for match_type, threshold in self.similarity_thresholds.items():
            if score >= threshold:
                return match_type.value
        return MatchType.FUZZY.value
    
    def _find_unmatched(
        self,
        requirements: List[Dict],
        matches: List[Dict]
    ) -> List[str]:
        """매칭되지 않은 요구사항 찾기"""
        matched_req_ids = {m["requirement_id"] for m in matches}
        return [
            req.get("id") for req in requirements
            if req.get("id") not in matched_req_ids
        ]


class MatchRateAgent:
    """Production-ready Match Rate Agent with full Task 4.41-4.50 implementation"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # Agno Agent 초기화
        if AGNO_AVAILABLE:
            self._init_agno_agent()
        else:
            logger.warning("Agno Framework not available, using fallback mode")
            self.agent = None
        
        # 컴포넌트 초기화
        self._init_components()
        
        # 템플릿 라이브러리 초기화
        self._init_template_library()
        
        # 매칭 규칙 초기화
        self._init_matching_rules()
        
        # 메트릭 초기화
        self.matching_times = []
        self.match_rates = []
        
        logger.info(f"Match Rate Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/match-rate-agent/',
                Recursive=True,
                WithDecryption=True
            )
            
            config = {}
            for param in response['Parameters']:
                key = param['Name'].split('/')[-1]
                config[key] = param['Value']
            
            return config
        except ClientError as e:
            logger.error(f"Failed to load config: {e}")
            return {
                'min_match_threshold': 0.3,
                'optimization_iterations': 10,
                'cache_ttl': 3600,
                'use_semantic_matching': True,
                'use_ml_optimization': True,
                'template_library_bucket': 't-developer-templates'
            }
    
    def _init_agno_agent(self):
        """Agno 에이전트 초기화"""
        try:
            self.agent = Agent(
                name="Match-Rate-Calculator",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-v2:0",
                    region="us-east-1"
                ),
                role="Expert in component matching and reusability optimization",
                instructions=[
                    "Calculate precise matching rates between requirements and components",
                    "Identify reusable components and templates",
                    "Optimize component selection for maximum reusability",
                    "Analyze coverage gaps and suggest improvements",
                    "Provide semantic and pattern-based matching",
                    "Generate adaptation recommendations",
                    "Perform multi-criteria matching analysis"
                ],
                memory=ConversationSummaryMemory(
                    storage_type="dynamodb",
                    table_name=f"t-dev-match-rates-{self.environment}"
                ),
                tools=[
                    MatchingEngine()
                ],
                temperature=0.2,
                max_retries=3
            )
            logger.info("Agno agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno agent: {e}")
            self.agent = None
    
    def _init_components(self):
        """컴포넌트 초기화"""
        from .similarity_calculator import SimilarityCalculator
        from .pattern_matcher import PatternMatcher
        from .semantic_analyzer import SemanticAnalyzer
        from .template_matcher import TemplateMatcher
        from .coverage_analyzer import CoverageAnalyzer
        from .optimization_engine import OptimizationEngine
        from .adaptation_recommender import AdaptationRecommender
        from .reusability_scorer import ReusabilityScorer
        from .gap_analyzer import GapAnalyzer
        from .ml_optimizer import MLOptimizer
        
        self.similarity_calculator = SimilarityCalculator()
        self.pattern_matcher = PatternMatcher()
        self.semantic_analyzer = SemanticAnalyzer()
        self.template_matcher = TemplateMatcher()
        self.coverage_analyzer = CoverageAnalyzer()
        self.optimization_engine = OptimizationEngine()
        self.adaptation_recommender = AdaptationRecommender()
        self.reusability_scorer = ReusabilityScorer()
        self.gap_analyzer = GapAnalyzer()
        self.ml_optimizer = MLOptimizer()
    
    def _init_template_library(self):
        """템플릿 라이브러리 초기화"""
        self.template_library = {
            'web_app': {
                'e_commerce': {
                    'components': ['ProductList', 'ShoppingCart', 'Checkout', 'UserAuth'],
                    'match_keywords': ['shop', 'store', 'product', 'cart', 'payment'],
                    'reusability': 0.85
                },
                'dashboard': {
                    'components': ['Charts', 'Tables', 'Filters', 'Export'],
                    'match_keywords': ['analytics', 'dashboard', 'metrics', 'reports'],
                    'reusability': 0.80
                },
                'social': {
                    'components': ['Feed', 'Profile', 'Messages', 'Notifications'],
                    'match_keywords': ['social', 'feed', 'post', 'follow', 'like'],
                    'reusability': 0.75
                }
            },
            'mobile_app': {
                'delivery': {
                    'components': ['MapView', 'Tracking', 'OrderStatus', 'Rating'],
                    'match_keywords': ['delivery', 'track', 'map', 'location', 'driver'],
                    'reusability': 0.82
                },
                'fitness': {
                    'components': ['WorkoutTracker', 'Progress', 'Goals', 'Social'],
                    'match_keywords': ['fitness', 'workout', 'exercise', 'health', 'track'],
                    'reusability': 0.78
                }
            },
            'backend_api': {
                'rest': {
                    'components': ['Authentication', 'CRUD', 'Validation', 'ErrorHandling'],
                    'match_keywords': ['api', 'rest', 'endpoint', 'resource'],
                    'reusability': 0.90
                },
                'graphql': {
                    'components': ['Schema', 'Resolvers', 'Mutations', 'Subscriptions'],
                    'match_keywords': ['graphql', 'query', 'mutation', 'subscription'],
                    'reusability': 0.85
                }
            }
        }
    
    def _init_matching_rules(self):
        """매칭 규칙 초기화"""
        self.matching_rules = {
            'exact_match': {
                'weight': 1.0,
                'threshold': 0.95,
                'methods': ['hash', 'string_exact']
            },
            'semantic_match': {
                'weight': 0.8,
                'threshold': 0.7,
                'methods': ['embedding', 'nlp', 'context']
            },
            'pattern_match': {
                'weight': 0.6,
                'threshold': 0.6,
                'methods': ['regex', 'template', 'structure']
            },
            'fuzzy_match': {
                'weight': 0.4,
                'threshold': 0.4,
                'methods': ['levenshtein', 'soundex', 'ngram']
            }
        }
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    async def calculate_match_rate(
        self,
        requirements: Dict[str, Any],
        component_library: Dict[str, Any],
        technology_stack: Dict[str, Any],
        use_ml: bool = True
    ) -> MatchingResult:
        """
        매칭률 계산 (Tasks 4.41-4.50)
        
        Args:
            requirements: 파싱된 요구사항
            component_library: 컴포넌트 라이브러리
            technology_stack: 선택된 기술 스택
            use_ml: ML 최적화 사용 여부
            
        Returns:
            MatchingResult: 매칭 결과
        """
        start_time = time.time()
        
        try:
            # 1. 컴포넌트 매칭 계산 (Task 4.41)
            component_matches = await self._calculate_component_matches(
                requirements, component_library
            )
            
            # 2. 템플릿 매칭 (Task 4.42)
            template_matches = await self._match_templates(
                requirements, self.template_library
            )
            
            # 3. 의미적 매칭 (Task 4.43)
            semantic_matches = await self._perform_semantic_matching(
                requirements, component_library
            )
            
            # 4. 패턴 기반 매칭 (Task 4.44)
            pattern_matches = await self._perform_pattern_matching(
                requirements, component_library
            )
            
            # 5. 재사용성 평가 (Task 4.45)
            reusability_scores = await self._evaluate_reusability(
                component_matches, template_matches
            )
            
            # 6. 커버리지 분석 (Task 4.46)
            coverage_analysis = await self._analyze_coverage(
                requirements, component_matches
            )
            
            # 7. 갭 분석 (Task 4.47)
            gap_analysis = await self._analyze_gaps(
                requirements, component_matches, coverage_analysis
            )
            
            # 8. 최적화 수행 (Task 4.48)
            if use_ml:
                optimized_matches = await self._optimize_matching_ml(
                    component_matches, requirements
                )
            else:
                optimized_matches = await self._optimize_matching_heuristic(
                    component_matches, requirements
                )
            
            # 9. 적응 권장사항 생성 (Task 4.49)
            adaptation_recommendations = await self._generate_adaptations(
                optimized_matches, gap_analysis
            )
            
            # 10. 최종 매칭 결과 생성 (Task 4.50)
            final_result = await self._generate_final_result(
                optimized_matches,
                coverage_analysis,
                adaptation_recommendations,
                reusability_scores
            )
            
            # 메트릭 기록
            processing_time = time.time() - start_time
            self.matching_times.append(processing_time)
            self.match_rates.append(final_result.overall_match_rate)
            
            metrics.add_metric(
                name="MatchingTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            metrics.add_metric(
                name="MatchRate",
                unit=MetricUnit.Percent,
                value=final_result.overall_match_rate * 100
            )
            
            logger.info(
                "Successfully calculated match rates",
                extra={
                    "overall_match_rate": final_result.overall_match_rate,
                    "matched_components": len(final_result.component_matches),
                    "unmatched_requirements": len(final_result.unmatched_requirements),
                    "processing_time": processing_time
                }
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error calculating match rates: {e}")
            metrics.add_metric(name="MatchingError", unit=MetricUnit.Count, value=1)
            raise
    
    async def _calculate_component_matches(
        self,
        requirements: Dict[str, Any],
        component_library: Dict[str, Any]
    ) -> List[ComponentMatch]:
        """Task 4.41: 컴포넌트 매칭 계산"""
        matches = []
        
        for req in requirements.get('functional_requirements', []):
            # 각 요구사항에 대해 최적 컴포넌트 찾기
            best_match = await self._find_best_component_match(
                req, component_library
            )
            
            if best_match:
                matches.append(best_match)
        
        return matches
    
    async def _match_templates(
        self,
        requirements: Dict[str, Any],
        template_library: Dict[str, Any]
    ) -> List[TemplateMatch]:
        """Task 4.42: 템플릿 매칭"""
        return await self.template_matcher.match(requirements, template_library)
    
    async def _perform_semantic_matching(
        self,
        requirements: Dict[str, Any],
        component_library: Dict[str, Any]
    ) -> List[ComponentMatch]:
        """Task 4.43: 의미적 매칭"""
        return await self.semantic_analyzer.match(requirements, component_library)
    
    async def _perform_pattern_matching(
        self,
        requirements: Dict[str, Any],
        component_library: Dict[str, Any]
    ) -> List[ComponentMatch]:
        """Task 4.44: 패턴 기반 매칭"""
        return await self.pattern_matcher.match(requirements, component_library)
    
    async def _evaluate_reusability(
        self,
        component_matches: List[ComponentMatch],
        template_matches: List[TemplateMatch]
    ) -> Dict[str, float]:
        """Task 4.45: 재사용성 평가"""
        return await self.reusability_scorer.evaluate(
            component_matches, template_matches
        )
    
    async def _analyze_coverage(
        self,
        requirements: Dict[str, Any],
        component_matches: List[ComponentMatch]
    ) -> Dict[str, float]:
        """Task 4.46: 커버리지 분석"""
        return await self.coverage_analyzer.analyze(requirements, component_matches)
    
    async def _analyze_gaps(
        self,
        requirements: Dict[str, Any],
        component_matches: List[ComponentMatch],
        coverage_analysis: Dict[str, float]
    ) -> Dict[str, Any]:
        """Task 4.47: 갭 분석"""
        return await self.gap_analyzer.analyze(
            requirements, component_matches, coverage_analysis
        )
    
    async def _optimize_matching_ml(
        self,
        component_matches: List[ComponentMatch],
        requirements: Dict[str, Any]
    ) -> List[ComponentMatch]:
        """Task 4.48: ML 기반 매칭 최적화"""
        return await self.ml_optimizer.optimize(component_matches, requirements)
    
    async def _optimize_matching_heuristic(
        self,
        component_matches: List[ComponentMatch],
        requirements: Dict[str, Any]
    ) -> List[ComponentMatch]:
        """Task 4.48: 휴리스틱 기반 매칭 최적화"""
        return await self.optimization_engine.optimize(component_matches, requirements)
    
    async def _generate_adaptations(
        self,
        optimized_matches: List[ComponentMatch],
        gap_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Task 4.49: 적응 권장사항 생성"""
        return await self.adaptation_recommender.generate(
            optimized_matches, gap_analysis
        )
    
    async def _generate_final_result(
        self,
        optimized_matches: List[ComponentMatch],
        coverage_analysis: Dict[str, float],
        adaptation_recommendations: List[Dict[str, Any]],
        reusability_scores: Dict[str, float]
    ) -> MatchingResult:
        """Task 4.50: 최종 매칭 결과 생성"""
        # 전체 매칭률 계산
        overall_match_rate = self._calculate_overall_match_rate(optimized_matches)
        
        # 매칭되지 않은 요구사항 식별
        unmatched_requirements = self._identify_unmatched_requirements(
            optimized_matches
        )
        
        # 신뢰도 분포 계산
        confidence_distribution = self._calculate_confidence_distribution(
            optimized_matches
        )
        
        # 최적화 제안 생성
        optimization_suggestions = self._generate_optimization_suggestions(
            optimized_matches,
            coverage_analysis,
            adaptation_recommendations
        )
        
        return MatchingResult(
            overall_match_rate=overall_match_rate,
            component_matches=optimized_matches,
            unmatched_requirements=unmatched_requirements,
            coverage_analysis=coverage_analysis,
            optimization_suggestions=optimization_suggestions,
            confidence_distribution=confidence_distribution,
            metadata={
                'reusability_scores': reusability_scores,
                'adaptation_recommendations': adaptation_recommendations,
                'timestamp': time.time(),
                'agent_version': '1.0.0'
            }
        )
    
    async def _find_best_component_match(
        self,
        requirement: Dict[str, Any],
        component_library: Dict[str, Any]
    ) -> Optional[ComponentMatch]:
        """최적 컴포넌트 매치 찾기"""
        best_match = None
        best_score = 0
        
        for category, components in component_library.items():
            for component_id, component in components.items():
                # 유사도 계산
                similarity = await self.similarity_calculator.calculate(
                    requirement, component
                )
                
                if similarity.weighted_average > best_score:
                    best_score = similarity.weighted_average
                    best_match = ComponentMatch(
                        requirement_id=requirement.get('id', ''),
                        component_id=component_id,
                        match_type=self._determine_match_type(similarity),
                        match_score=similarity.weighted_average,
                        confidence=self._calculate_confidence(similarity),
                        explanation=self._generate_explanation(requirement, component, similarity),
                        metadata={
                            'similarity_metrics': asdict(similarity),
                            'category': category
                        }
                    )
        
        # 최소 임계값 확인
        min_threshold = float(self.config.get('min_match_threshold', 0.3))
        if best_match and best_match.match_score >= min_threshold:
            return best_match
        
        return None
    
    def _determine_match_type(self, similarity: SimilarityMetrics) -> MatchType:
        """매치 타입 결정"""
        if similarity.weighted_average >= 0.95:
            return MatchType.EXACT
        elif similarity.semantic_similarity >= 0.7:
            return MatchType.SEMANTIC
        elif similarity.structural_similarity >= 0.6:
            return MatchType.PATTERN
        elif similarity.weighted_average >= 0.5:
            return MatchType.PARTIAL
        else:
            return MatchType.FUZZY
    
    def _calculate_confidence(self, similarity: SimilarityMetrics) -> float:
        """신뢰도 계산"""
        # 여러 메트릭의 일관성 기반 신뢰도
        metrics = [
            similarity.cosine_similarity,
            similarity.jaccard_similarity,
            similarity.semantic_similarity,
            similarity.structural_similarity
        ]
        
        # 표준편차가 작을수록 신뢰도 높음
        std_dev = np.std(metrics)
        confidence = 1.0 - min(std_dev * 2, 0.5)  # 최대 0.5 감소
        
        # 평균 점수도 고려
        avg_score = np.mean(metrics)
        confidence *= avg_score
        
        return confidence
    
    def _generate_explanation(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any],
        similarity: SimilarityMetrics
    ) -> str:
        """매칭 설명 생성"""
        explanations = []
        
        if similarity.cosine_similarity > 0.7:
            explanations.append("High textual similarity")
        
        if similarity.semantic_similarity > 0.7:
            explanations.append("Strong semantic relationship")
        
        if similarity.structural_similarity > 0.6:
            explanations.append("Similar structure/pattern")
        
        if similarity.jaccard_similarity > 0.5:
            explanations.append("Significant keyword overlap")
        
        return "; ".join(explanations) if explanations else "Partial match based on multiple factors"
    
    def _calculate_overall_match_rate(
        self,
        matches: List[ComponentMatch]
    ) -> float:
        """전체 매칭률 계산"""
        if not matches:
            return 0.0
        
        # 가중 평균 계산
        total_score = sum(m.match_score * m.confidence for m in matches)
        total_confidence = sum(m.confidence for m in matches)
        
        if total_confidence == 0:
            return 0.0
        
        return total_score / total_confidence
    
    def _identify_unmatched_requirements(
        self,
        matches: List[ComponentMatch]
    ) -> List[str]:
        """매칭되지 않은 요구사항 식별"""
        # 실제 구현에서는 전체 요구사항 목록과 비교
        matched_req_ids = {m.requirement_id for m in matches}
        # TODO: 전체 요구사항 목록에서 matched_req_ids를 제외
        return []
    
    def _calculate_confidence_distribution(
        self,
        matches: List[ComponentMatch]
    ) -> Dict[str, float]:
        """신뢰도 분포 계산"""
        if not matches:
            return {}
        
        confidences = [m.confidence for m in matches]
        
        return {
            'min': min(confidences),
            'max': max(confidences),
            'mean': np.mean(confidences),
            'median': np.median(confidences),
            'std': np.std(confidences),
            'high_confidence_ratio': sum(1 for c in confidences if c > 0.7) / len(confidences)
        }
    
    def _generate_optimization_suggestions(
        self,
        matches: List[ComponentMatch],
        coverage_analysis: Dict[str, float],
        adaptation_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """최적화 제안 생성"""
        suggestions = []
        
        # 낮은 매칭 점수 개선
        low_matches = [m for m in matches if m.match_score < 0.5]
        if low_matches:
            suggestions.append({
                'type': 'improve_matching',
                'priority': 'high',
                'target_components': [m.component_id for m in low_matches],
                'recommendation': 'Consider custom component development or adaptation'
            })
        
        # 커버리지 개선
        if coverage_analysis.get('overall_coverage', 1.0) < 0.8:
            suggestions.append({
                'type': 'improve_coverage',
                'priority': 'medium',
                'recommendation': 'Add missing components to cover gaps'
            })
        
        # 적응 권장사항 추가
        for adaptation in adaptation_recommendations[:3]:  # 상위 3개
            suggestions.append({
                'type': 'adaptation',
                'priority': 'medium',
                'details': adaptation
            })
        
        return suggestions


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    import asyncio
    
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        requirements = body.get('requirements', {})
        component_library = body.get('component_library', {})
        technology_stack = body.get('technology_stack', {})
        use_ml = body.get('use_ml', True)
        
        # Agent 실행
        agent = MatchRateAgent()
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        matching_result = loop.run_until_complete(
            agent.calculate_match_rate(
                requirements,
                component_library,
                technology_stack,
                use_ml
            )
        )
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(asdict(matching_result), ensure_ascii=False)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Error calculating match rates'
                }
            }, ensure_ascii=False)
        }