# Task 4.5: Advanced Matching Rate Calculation System
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools import LambdaAgent, VectorDatabaseSearch
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import asyncio
from dataclasses import dataclass
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

@dataclass
class ComponentMatch:
    component: Dict[str, Any]
    overall_score: float
    dimension_scores: Dict[str, float]
    integration_effort: str
    risks: List[str]
    recommendations: List[str]

@dataclass
class MatchingResults:
    matrix: List['RequirementMatches']
    overall_coverage: float
    gap_analysis: Dict[str, Any]
    recommendations: List[str]

class AdvancedMatchingRateCalculator:
    """고급 매칭률 계산 시스템"""

    def __init__(self):
        self.agent = Agent(
            name="Matching-Rate-Calculator",
            model=AwsBedrock(id="amazon.nova-pro-v1:0"),
            role="Expert in calculating component compatibility scores",
            tools=[
                LambdaAgent("semantic-similarity-calculator"),
                LambdaAgent("api-compatibility-checker"),
                LambdaAgent("performance-predictor"),
                VectorDatabaseSearch()
            ],
            instructions=[
                "Calculate precise matching scores between requirements and components",
                "Consider multiple dimensions: functional, technical, performance",
                "Predict integration complexity and effort",
                "Identify potential conflicts and incompatibilities"
            ]
        )
        
        self.similarity_engine = SemanticSimilarityEngine()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        self.performance_predictor = PerformancePredictor()

    async def calculate_matching_rates(
        self,
        requirements: List[Dict[str, Any]],
        components: List[Dict[str, Any]]
    ) -> MatchingResults:
        """종합적인 매칭률 계산"""

        matching_matrix = []
        
        # 병렬 처리를 위한 세마포어
        semaphore = asyncio.Semaphore(10)
        
        for requirement in requirements:
            component_matches = []
            
            # 각 컴포넌트에 대해 병렬 매칭 계산
            tasks = []
            for component in components:
                task = asyncio.create_task(
                    self._calculate_component_match(requirement, component, semaphore)
                )
                tasks.append(task)
            
            matches = await asyncio.gather(*tasks)
            
            # 점수 기준으로 정렬
            sorted_matches = sorted(matches, key=lambda x: x.overall_score, reverse=True)
            component_matches.extend(sorted_matches)
            
            matching_matrix.append(RequirementMatches(
                requirement=requirement,
                matches=component_matches
            ))

        # 전체 분석
        overall_coverage = self._calculate_coverage(matching_matrix)
        gap_analysis = await self._analyze_gaps(matching_matrix)
        recommendations = await self._generate_recommendations(matching_matrix)

        return MatchingResults(
            matrix=matching_matrix,
            overall_coverage=overall_coverage,
            gap_analysis=gap_analysis,
            recommendations=recommendations
        )

    async def _calculate_component_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any],
        semaphore: asyncio.Semaphore
    ) -> ComponentMatch:
        """단일 컴포넌트 매칭 계산"""
        
        async with semaphore:
            # 다차원 매칭 점수 계산
            scores = await asyncio.gather(
                self._calculate_functional_match(requirement, component),
                self._calculate_technical_match(requirement, component),
                self._calculate_performance_match(requirement, component),
                self._calculate_compatibility_score(requirement, component),
                self._calculate_semantic_similarity(requirement, component)
            )
            
            functional_score, technical_score, performance_score, compatibility_score, semantic_score = scores
            
            # 가중치 적용한 종합 점수
            weights = {
                'functional': 0.3,
                'technical': 0.25,
                'performance': 0.2,
                'compatibility': 0.15,
                'semantic': 0.1
            }
            
            overall_score = (
                functional_score * weights['functional'] +
                technical_score * weights['technical'] +
                performance_score * weights['performance'] +
                compatibility_score * weights['compatibility'] +
                semantic_score * weights['semantic']
            )
            
            # 상세 분석
            integration_effort = await self._estimate_integration_effort(
                requirement, component, overall_score
            )
            
            risks = await self._identify_risks(requirement, component)
            recommendations = await self._generate_component_recommendations(
                requirement, component, overall_score
            )
            
            return ComponentMatch(
                component=component,
                overall_score=overall_score,
                dimension_scores={
                    'functional': functional_score,
                    'technical': technical_score,
                    'performance': performance_score,
                    'compatibility': compatibility_score,
                    'semantic': semantic_score
                },
                integration_effort=integration_effort,
                risks=risks,
                recommendations=recommendations
            )

    async def _calculate_functional_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """기능적 매칭 점수 계산"""
        
        req_features = set(requirement.get('required_features', []))
        comp_features = set(component.get('features', []))
        
        if not req_features:
            return 8.0  # 기본 점수
        
        # 교집합 비율
        intersection = req_features.intersection(comp_features)
        coverage_ratio = len(intersection) / len(req_features)
        
        # 추가 기능 보너스
        extra_features = comp_features - req_features
        bonus = min(1.0, len(extra_features) * 0.1)
        
        # AI 에이전트를 통한 의미적 분석
        semantic_analysis = await self.agent.arun(f"""
        요구사항: {requirement.get('description', '')}
        컴포넌트 기능: {component.get('description', '')}
        
        기능적 적합성을 1-10점으로 평가해주세요.
        """)
        
        ai_score = await self._extract_score_from_analysis(semantic_analysis)
        
        # 종합 점수
        final_score = (coverage_ratio * 6 + bonus + ai_score * 0.3)
        return min(10.0, max(1.0, final_score))

    async def _calculate_technical_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """기술적 매칭 점수 계산"""
        
        score = 5.0  # 기본 점수
        
        # 기술 스택 호환성
        req_tech = set(requirement.get('technology_stack', []))
        comp_tech = set(component.get('technology_stack', []))
        
        if req_tech and comp_tech:
            tech_overlap = len(req_tech.intersection(comp_tech)) / len(req_tech.union(comp_tech))
            score += tech_overlap * 3.0
        
        # 아키텍처 패턴 호환성
        req_patterns = requirement.get('architecture_patterns', [])
        comp_patterns = component.get('supported_patterns', [])
        
        pattern_match = any(pattern in comp_patterns for pattern in req_patterns)
        if pattern_match:
            score += 1.5
        
        # 버전 호환성
        req_version = requirement.get('version_requirements', {})
        comp_version = component.get('version', '')
        
        if self._check_version_compatibility(req_version, comp_version):
            score += 1.0
        
        return min(10.0, max(1.0, score))

    async def _calculate_performance_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """성능 매칭 점수 계산"""
        
        req_performance = requirement.get('performance_requirements', {})
        comp_performance = component.get('performance_metrics', {})
        
        if not req_performance or not comp_performance:
            return 7.0  # 기본 점수
        
        score = 0.0
        criteria_count = 0
        
        # 처리량 비교
        if 'throughput' in req_performance and 'throughput' in comp_performance:
            req_throughput = req_performance['throughput']
            comp_throughput = comp_performance['throughput']
            
            if comp_throughput >= req_throughput:
                score += 10.0
            else:
                ratio = comp_throughput / req_throughput
                score += ratio * 10.0
            
            criteria_count += 1
        
        # 지연시간 비교
        if 'latency' in req_performance and 'latency' in comp_performance:
            req_latency = req_performance['latency']
            comp_latency = comp_performance['latency']
            
            if comp_latency <= req_latency:
                score += 10.0
            else:
                ratio = req_latency / comp_latency
                score += ratio * 10.0
            
            criteria_count += 1
        
        # 메모리 사용량 비교
        if 'memory_usage' in req_performance and 'memory_usage' in comp_performance:
            req_memory = req_performance['memory_usage']
            comp_memory = comp_performance['memory_usage']
            
            if comp_memory <= req_memory:
                score += 10.0
            else:
                ratio = req_memory / comp_memory
                score += ratio * 10.0
            
            criteria_count += 1
        
        return score / criteria_count if criteria_count > 0 else 7.0

    async def _calculate_semantic_similarity(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """의미적 유사도 계산"""
        
        req_text = f"{requirement.get('description', '')} {' '.join(requirement.get('keywords', []))}"
        comp_text = f"{component.get('description', '')} {' '.join(component.get('tags', []))}"
        
        if not req_text.strip() or not comp_text.strip():
            return 5.0
        
        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        try:
            tfidf_matrix = vectorizer.fit_transform([req_text, comp_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # 0-1 범위를 1-10 범위로 변환
            return 1.0 + similarity * 9.0
            
        except Exception:
            return 5.0

class SemanticSimilarityEngine:
    """의미적 유사도 엔진"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.embeddings_cache = {}

    async def calculate_similarity(
        self,
        text1: str,
        text2: str,
        method: str = 'tfidf'
    ) -> float:
        """텍스트 간 의미적 유사도 계산"""
        
        if method == 'tfidf':
            return await self._tfidf_similarity(text1, text2)
        elif method == 'embedding':
            return await self._embedding_similarity(text1, text2)
        else:
            raise ValueError(f"Unknown similarity method: {method}")

    async def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """TF-IDF 기반 유사도"""
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception:
            return 0.0

    async def _embedding_similarity(self, text1: str, text2: str) -> float:
        """임베딩 기반 유사도 (향후 구현)"""
        # 실제 구현에서는 BERT, Sentence-BERT 등 사용
        return await self._tfidf_similarity(text1, text2)

class CompatibilityAnalyzer:
    """호환성 분석기"""
    
    async def analyze_compatibility(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> Dict[str, Any]:
        """종합적인 호환성 분석"""
        
        compatibility_checks = [
            self._check_api_compatibility(requirement, component),
            self._check_dependency_compatibility(requirement, component),
            self._check_license_compatibility(requirement, component),
            self._check_platform_compatibility(requirement, component)
        ]
        
        results = await asyncio.gather(*compatibility_checks)
        
        overall_compatibility = all(result['compatible'] for result in results)
        compatibility_score = sum(result['score'] for result in results) / len(results)
        
        return {
            'overall_compatible': overall_compatibility,
            'compatibility_score': compatibility_score,
            'detailed_results': {
                'api': results[0],
                'dependency': results[1],
                'license': results[2],
                'platform': results[3]
            }
        }

    async def _check_api_compatibility(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> Dict[str, Any]:
        """API 호환성 검사"""
        
        req_api = requirement.get('api_requirements', {})
        comp_api = component.get('api_specification', {})
        
        if not req_api or not comp_api:
            return {'compatible': True, 'score': 8.0, 'issues': []}
        
        issues = []
        score = 10.0
        
        # API 버전 호환성
        req_version = req_api.get('version')
        comp_version = comp_api.get('version')
        
        if req_version and comp_version:
            if not self._is_version_compatible(req_version, comp_version):
                issues.append(f"API version mismatch: required {req_version}, provided {comp_version}")
                score -= 3.0
        
        # 필수 엔드포인트 확인
        req_endpoints = set(req_api.get('required_endpoints', []))
        comp_endpoints = set(comp_api.get('available_endpoints', []))
        
        missing_endpoints = req_endpoints - comp_endpoints
        if missing_endpoints:
            issues.append(f"Missing endpoints: {list(missing_endpoints)}")
            score -= len(missing_endpoints) * 1.0
        
        return {
            'compatible': len(issues) == 0,
            'score': max(1.0, score),
            'issues': issues
        }

class PerformancePredictor:
    """성능 예측기"""
    
    async def predict_integration_performance(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 성능 예측"""
        
        # 기본 성능 메트릭
        base_performance = component.get('performance_metrics', {})
        
        # 요구사항에 따른 성능 조정
        adjusted_performance = await self._adjust_for_requirements(
            base_performance, requirement
        )
        
        # 통합 오버헤드 계산
        integration_overhead = await self._calculate_integration_overhead(
            requirement, component
        )
        
        # 최종 예측 성능
        predicted_performance = self._apply_overhead(
            adjusted_performance, integration_overhead
        )
        
        return {
            'predicted_metrics': predicted_performance,
            'integration_overhead': integration_overhead,
            'performance_grade': self._calculate_performance_grade(predicted_performance),
            'bottlenecks': await self._identify_bottlenecks(predicted_performance)
        }

    async def _calculate_integration_overhead(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> Dict[str, float]:
        """통합 오버헤드 계산"""
        
        overhead = {
            'latency_overhead_ms': 0.0,
            'throughput_reduction_percent': 0.0,
            'memory_overhead_mb': 0.0
        }
        
        # 아키텍처 패턴에 따른 오버헤드
        req_patterns = requirement.get('architecture_patterns', [])
        
        if 'microservices' in req_patterns:
            overhead['latency_overhead_ms'] += 10.0
            overhead['memory_overhead_mb'] += 5.0
        
        if 'event_driven' in req_patterns:
            overhead['latency_overhead_ms'] += 5.0
            overhead['throughput_reduction_percent'] += 2.0
        
        # 보안 요구사항에 따른 오버헤드
        security_reqs = requirement.get('security_requirements', [])
        
        if 'encryption' in security_reqs:
            overhead['latency_overhead_ms'] += 15.0
            overhead['throughput_reduction_percent'] += 5.0
        
        return overhead