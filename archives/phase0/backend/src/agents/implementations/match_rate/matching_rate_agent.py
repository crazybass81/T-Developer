"""
Matching Rate Agent - Component compatibility scoring and matching analysis
Calculates precise matching scores between requirements and components
"""

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class MatchingScore:
    overall_score: float
    functional_score: float
    technical_score: float
    performance_score: float
    compatibility_score: float
    confidence: float
    explanation: str

@dataclass
class ComponentMatch:
    component_id: str
    component_name: str
    matching_score: MatchingScore
    pros: List[str]
    cons: List[str]
    integration_effort: str
    risks: List[str]

class SemanticSimilarityAnalyzer:
    """의미적 유사도 분석기"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.embeddings_cache = {}
    
    async def calculate_semantic_similarity(
        self,
        requirement_text: str,
        component_description: str
    ) -> float:
        """의미적 유사도 계산"""
        
        # 캐시 확인
        cache_key = f"{hash(requirement_text)}_{hash(component_description)}"
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
        
        # TF-IDF 벡터화
        texts = [requirement_text, component_description]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # 코사인 유사도 계산
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # 캐시 저장
        self.embeddings_cache[cache_key] = similarity
        
        return float(similarity)
    
    async def analyze_feature_overlap(
        self,
        required_features: List[str],
        component_features: List[str]
    ) -> Dict[str, float]:
        """기능 중복도 분석"""
        
        if not required_features or not component_features:
            return {'overlap_ratio': 0.0, 'coverage_score': 0.0}
        
        # 정확한 매칭
        exact_matches = set(required_features) & set(component_features)
        
        # 의미적 매칭
        semantic_matches = 0
        for req_feature in required_features:
            for comp_feature in component_features:
                similarity = await self.calculate_semantic_similarity(
                    req_feature, comp_feature
                )
                if similarity > 0.7:  # 임계값
                    semantic_matches += 1
                    break
        
        total_matches = len(exact_matches) + semantic_matches
        overlap_ratio = total_matches / len(required_features)
        coverage_score = total_matches / len(set(required_features + component_features))
        
        return {
            'overlap_ratio': overlap_ratio,
            'coverage_score': coverage_score,
            'exact_matches': len(exact_matches),
            'semantic_matches': semantic_matches
        }

class CompatibilityAnalyzer:
    """호환성 분석기"""
    
    def __init__(self):
        self.compatibility_matrix = self._load_compatibility_matrix()
        self.version_analyzer = VersionAnalyzer()
    
    def _load_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """호환성 매트릭스 로드"""
        return {
            'react': {
                'typescript': 0.95,
                'javascript': 1.0,
                'webpack': 0.9,
                'vite': 0.95,
                'jest': 0.9
            },
            'vue': {
                'typescript': 0.9,
                'javascript': 1.0,
                'webpack': 0.85,
                'vite': 0.95,
                'vitest': 0.95
            },
            'angular': {
                'typescript': 1.0,
                'javascript': 0.7,
                'webpack': 0.95,
                'jasmine': 0.9
            }
        }
    
    async def analyze_technical_compatibility(
        self,
        component: Dict[str, Any],
        tech_stack: List[str]
    ) -> Dict[str, float]:
        """기술적 호환성 분석"""
        
        component_name = component.get('name', '').lower()
        compatibility_scores = {}
        
        for tech in tech_stack:
            tech_lower = tech.lower()
            
            # 직접 호환성 매트릭스에서 조회
            if component_name in self.compatibility_matrix:
                score = self.compatibility_matrix[component_name].get(tech_lower, 0.5)
            else:
                # 기본 호환성 점수
                score = await self._estimate_compatibility(component_name, tech_lower)
            
            compatibility_scores[tech] = score
        
        return compatibility_scores
    
    async def _estimate_compatibility(self, component: str, technology: str) -> float:
        """호환성 추정"""
        
        # 일반적인 호환성 패턴
        common_patterns = {
            ('react', 'redux'): 0.95,
            ('vue', 'vuex'): 0.95,
            ('angular', 'rxjs'): 0.95,
            ('express', 'node'): 1.0,
            ('fastapi', 'python'): 1.0
        }
        
        pattern_key = (component, technology)
        if pattern_key in common_patterns:
            return common_patterns[pattern_key]
        
        # 언어 기반 호환성
        language_compatibility = {
            'javascript': ['react', 'vue', 'express', 'node'],
            'typescript': ['angular', 'react', 'vue'],
            'python': ['django', 'flask', 'fastapi'],
            'java': ['spring', 'hibernate']
        }
        
        for lang, frameworks in language_compatibility.items():
            if technology == lang and component in frameworks:
                return 0.9
        
        return 0.5  # 기본값
    
    async def check_version_compatibility(
        self,
        component: Dict[str, Any],
        required_versions: Dict[str, str]
    ) -> Dict[str, bool]:
        """버전 호환성 검사"""
        
        compatibility_results = {}
        component_version = component.get('version', '1.0.0')
        
        for dep_name, required_version in required_versions.items():
            is_compatible = await self.version_analyzer.is_compatible(
                component.get('name'),
                component_version,
                dep_name,
                required_version
            )
            compatibility_results[dep_name] = is_compatible
        
        return compatibility_results

class PerformancePredictor:
    """성능 예측기"""
    
    def __init__(self):
        self.performance_benchmarks = self._load_benchmarks()
    
    def _load_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """성능 벤치마크 데이터"""
        return {
            'react': {
                'bundle_size_kb': 42,
                'initial_load_ms': 150,
                'render_time_ms': 16,
                'memory_usage_mb': 25
            },
            'vue': {
                'bundle_size_kb': 34,
                'initial_load_ms': 120,
                'render_time_ms': 14,
                'memory_usage_mb': 20
            },
            'angular': {
                'bundle_size_kb': 130,
                'initial_load_ms': 200,
                'render_time_ms': 18,
                'memory_usage_mb': 35
            }
        }
    
    async def predict_performance_impact(
        self,
        component: Dict[str, Any],
        performance_requirements: Dict[str, Any]
    ) -> Dict[str, float]:
        """성능 영향 예측"""
        
        component_name = component.get('name', '').lower()
        benchmarks = self.performance_benchmarks.get(component_name, {})
        
        if not benchmarks:
            return {'performance_score': 0.5}
        
        scores = {}
        
        # 번들 크기 점수
        max_bundle_size = performance_requirements.get('max_bundle_size_kb', 500)
        bundle_score = max(0, 1 - (benchmarks.get('bundle_size_kb', 100) / max_bundle_size))
        scores['bundle_size_score'] = bundle_score
        
        # 로딩 시간 점수
        max_load_time = performance_requirements.get('max_load_time_ms', 3000)
        load_score = max(0, 1 - (benchmarks.get('initial_load_ms', 1000) / max_load_time))
        scores['load_time_score'] = load_score
        
        # 메모리 사용량 점수
        max_memory = performance_requirements.get('max_memory_mb', 100)
        memory_score = max(0, 1 - (benchmarks.get('memory_usage_mb', 50) / max_memory))
        scores['memory_score'] = memory_score
        
        # 전체 성능 점수
        scores['performance_score'] = np.mean(list(scores.values()))
        
        return scores

class MatchingRateAgent:
    """매칭률 계산 에이전트"""
    
    def __init__(self):
        self.agent = Agent(
            name="Matching-Rate-Calculator",
            model=AwsBedrock(
                id="amazon.nova-pro-v1:0",
                region="us-east-1"
            ),
            role="Expert in calculating component compatibility and matching scores",
            instructions=[
                "Calculate precise matching scores between requirements and components",
                "Consider functional, technical, performance, and compatibility dimensions",
                "Provide detailed explanations for matching decisions",
                "Identify potential integration challenges and solutions"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-matching-memory"
            ),
            temperature=0.2
        )
        
        self.semantic_analyzer = SemanticSimilarityAnalyzer()
        self.compatibility_analyzer = CompatibilityAnalyzer()
        self.performance_predictor = PerformancePredictor()
    
    async def calculate_matching_score(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> MatchingScore:
        """종합 매칭 점수 계산"""
        
        if weights is None:
            weights = {
                'functional': 0.3,
                'technical': 0.25,
                'performance': 0.25,
                'compatibility': 0.2
            }
        
        # 1. 기능적 매칭 점수
        functional_score = await self._calculate_functional_score(requirement, component)
        
        # 2. 기술적 매칭 점수
        technical_score = await self._calculate_technical_score(requirement, component)
        
        # 3. 성능 매칭 점수
        performance_score = await self._calculate_performance_score(requirement, component)
        
        # 4. 호환성 점수
        compatibility_score = await self._calculate_compatibility_score(requirement, component)
        
        # 5. 가중 평균 계산
        overall_score = (
            functional_score * weights['functional'] +
            technical_score * weights['technical'] +
            performance_score * weights['performance'] +
            compatibility_score * weights['compatibility']
        )
        
        # 6. 신뢰도 계산
        confidence = await self._calculate_confidence(
            functional_score, technical_score, performance_score, compatibility_score
        )
        
        # 7. AI 기반 설명 생성
        explanation = await self._generate_explanation(
            requirement, component, overall_score,
            functional_score, technical_score, performance_score, compatibility_score
        )
        
        return MatchingScore(
            overall_score=overall_score,
            functional_score=functional_score,
            technical_score=technical_score,
            performance_score=performance_score,
            compatibility_score=compatibility_score,
            confidence=confidence,
            explanation=explanation
        )
    
    async def _calculate_functional_score(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """기능적 매칭 점수 계산"""
        
        req_features = requirement.get('required_features', [])
        comp_features = component.get('features', [])
        
        if not req_features:
            return 0.8  # 기본 점수
        
        # 기능 중복도 분석
        overlap_analysis = await self.semantic_analyzer.analyze_feature_overlap(
            req_features, comp_features
        )
        
        # 의미적 유사도 계산
        req_description = requirement.get('description', '')
        comp_description = component.get('description', '')
        
        semantic_similarity = await self.semantic_analyzer.calculate_semantic_similarity(
            req_description, comp_description
        )
        
        # 기능 점수 = 중복도 * 0.7 + 의미적 유사도 * 0.3
        functional_score = (
            overlap_analysis['overlap_ratio'] * 0.7 +
            semantic_similarity * 0.3
        )
        
        return min(functional_score, 1.0)
    
    async def _calculate_technical_score(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """기술적 매칭 점수 계산"""
        
        required_tech_stack = requirement.get('tech_stack', [])
        
        if not required_tech_stack:
            return 0.8  # 기본 점수
        
        # 기술적 호환성 분석
        compatibility_scores = await self.compatibility_analyzer.analyze_technical_compatibility(
            component, required_tech_stack
        )
        
        if not compatibility_scores:
            return 0.5
        
        # 평균 호환성 점수
        avg_compatibility = np.mean(list(compatibility_scores.values()))
        
        # 버전 호환성 검사
        required_versions = requirement.get('version_requirements', {})
        if required_versions:
            version_compatibility = await self.compatibility_analyzer.check_version_compatibility(
                component, required_versions
            )
            version_score = sum(version_compatibility.values()) / len(version_compatibility)
            
            # 기술 점수 = 호환성 * 0.7 + 버전 호환성 * 0.3
            technical_score = avg_compatibility * 0.7 + version_score * 0.3
        else:
            technical_score = avg_compatibility
        
        return min(technical_score, 1.0)
    
    async def _calculate_performance_score(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """성능 매칭 점수 계산"""
        
        performance_requirements = requirement.get('performance_requirements', {})
        
        if not performance_requirements:
            return 0.8  # 기본 점수
        
        # 성능 영향 예측
        performance_impact = await self.performance_predictor.predict_performance_impact(
            component, performance_requirements
        )
        
        return performance_impact.get('performance_score', 0.5)
    
    async def _calculate_compatibility_score(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """호환성 점수 계산"""
        
        # 플랫폼 호환성
        required_platforms = requirement.get('target_platforms', [])
        supported_platforms = component.get('supported_platforms', [])
        
        if required_platforms and supported_platforms:
            platform_overlap = len(set(required_platforms) & set(supported_platforms))
            platform_score = platform_overlap / len(required_platforms)
        else:
            platform_score = 0.8  # 기본 점수
        
        # 라이선스 호환성
        required_license = requirement.get('license_requirements', 'any')
        component_license = component.get('license', 'unknown')
        
        license_score = await self._check_license_compatibility(
            required_license, component_license
        )
        
        # 전체 호환성 점수
        compatibility_score = (platform_score * 0.6 + license_score * 0.4)
        
        return min(compatibility_score, 1.0)
    
    async def _check_license_compatibility(
        self,
        required_license: str,
        component_license: str
    ) -> float:
        """라이선스 호환성 검사"""
        
        if required_license == 'any':
            return 1.0
        
        # 라이선스 호환성 매트릭스
        license_compatibility = {
            'mit': ['mit', 'bsd', 'apache-2.0', 'isc'],
            'apache-2.0': ['apache-2.0', 'mit', 'bsd'],
            'gpl-3.0': ['gpl-3.0', 'lgpl-3.0'],
            'commercial': ['commercial', 'proprietary']
        }
        
        required_lower = required_license.lower()
        component_lower = component_license.lower()
        
        if required_lower in license_compatibility:
            compatible_licenses = license_compatibility[required_lower]
            return 1.0 if component_lower in compatible_licenses else 0.3
        
        return 0.5  # 불확실한 경우
    
    async def _calculate_confidence(
        self,
        functional_score: float,
        technical_score: float,
        performance_score: float,
        compatibility_score: float
    ) -> float:
        """신뢰도 계산"""
        
        scores = [functional_score, technical_score, performance_score, compatibility_score]
        
        # 점수들의 표준편차가 낮을수록 신뢰도 높음
        std_dev = np.std(scores)
        mean_score = np.mean(scores)
        
        # 신뢰도 = 평균 점수 * (1 - 정규화된 표준편차)
        confidence = mean_score * (1 - min(std_dev, 0.5))
        
        return min(confidence, 1.0)
    
    async def _generate_explanation(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any],
        overall_score: float,
        functional_score: float,
        technical_score: float,
        performance_score: float,
        compatibility_score: float
    ) -> str:
        """AI 기반 매칭 설명 생성"""
        
        explanation_prompt = f"""
        다음 컴포넌트 매칭 결과에 대한 상세한 설명을 제공해주세요:
        
        요구사항: {requirement.get('name', 'Unknown')}
        컴포넌트: {component.get('name', 'Unknown')} v{component.get('version', '1.0.0')}
        
        점수 분석:
        - 전체 점수: {overall_score:.2f}
        - 기능적 매칭: {functional_score:.2f}
        - 기술적 매칭: {technical_score:.2f}
        - 성능 매칭: {performance_score:.2f}
        - 호환성: {compatibility_score:.2f}
        
        다음 관점에서 설명해주세요:
        1. 왜 이 점수가 나왔는가?
        2. 주요 강점과 약점
        3. 통합 시 고려사항
        4. 개선 방안
        """
        
        response = await self.agent.arun(explanation_prompt)
        return response.content
    
    async def batch_calculate_matching(
        self,
        requirement: Dict[str, Any],
        components: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None
    ) -> List[ComponentMatch]:
        """배치 매칭 점수 계산"""
        
        # 병렬 처리로 성능 최적화
        tasks = []
        for component in components:
            task = self.calculate_matching_score(requirement, component, weights)
            tasks.append(task)
        
        matching_scores = await asyncio.gather(*tasks)
        
        # ComponentMatch 객체 생성
        matches = []
        for i, score in enumerate(matching_scores):
            component = components[i]
            
            # 장단점 분석
            pros, cons = await self._analyze_pros_cons(requirement, component, score)
            
            # 통합 노력 추정
            integration_effort = await self._estimate_integration_effort(score)
            
            # 위험 요소 식별
            risks = await self._identify_risks(requirement, component, score)
            
            match = ComponentMatch(
                component_id=component.get('id', f"comp_{i}"),
                component_name=component.get('name', 'Unknown'),
                matching_score=score,
                pros=pros,
                cons=cons,
                integration_effort=integration_effort,
                risks=risks
            )
            matches.append(match)
        
        # 점수순 정렬
        matches.sort(key=lambda x: x.matching_score.overall_score, reverse=True)
        
        return matches
    
    async def _analyze_pros_cons(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any],
        score: MatchingScore
    ) -> Tuple[List[str], List[str]]:
        """장단점 분석"""
        
        pros = []
        cons = []
        
        # 점수 기반 장단점
        if score.functional_score > 0.8:
            pros.append("Excellent functional match")
        elif score.functional_score < 0.5:
            cons.append("Limited functional alignment")
        
        if score.technical_score > 0.8:
            pros.append("High technical compatibility")
        elif score.technical_score < 0.5:
            cons.append("Technical integration challenges")
        
        if score.performance_score > 0.8:
            pros.append("Meets performance requirements")
        elif score.performance_score < 0.5:
            cons.append("Performance concerns")
        
        if score.compatibility_score > 0.8:
            pros.append("Good ecosystem compatibility")
        elif score.compatibility_score < 0.5:
            cons.append("Compatibility issues")
        
        return pros, cons
    
    async def _estimate_integration_effort(self, score: MatchingScore) -> str:
        """통합 노력 추정"""
        
        if score.overall_score > 0.8:
            return "Low - Straightforward integration"
        elif score.overall_score > 0.6:
            return "Medium - Some customization needed"
        elif score.overall_score > 0.4:
            return "High - Significant adaptation required"
        else:
            return "Very High - Major integration challenges"
    
    async def _identify_risks(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any],
        score: MatchingScore
    ) -> List[str]:
        """위험 요소 식별"""
        
        risks = []
        
        if score.technical_score < 0.6:
            risks.append("Technical compatibility risks")
        
        if score.performance_score < 0.6:
            risks.append("Performance degradation risk")
        
        if score.compatibility_score < 0.6:
            risks.append("Ecosystem integration risks")
        
        if score.confidence < 0.7:
            risks.append("Uncertain matching accuracy")
        
        # 컴포넌트 특성 기반 위험
        if component.get('maturity', 'stable') == 'experimental':
            risks.append("Component stability concerns")
        
        if not component.get('community_support', True):
            risks.append("Limited community support")
        
        return risks