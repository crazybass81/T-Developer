"""
Matching Rate Agent - 컴포넌트와 요구사항 간의 매칭률 계산
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import asyncio
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from agno.agent import Agent
from agno.models.aws import AwsBedrock
import json

@dataclass
class MatchingResult:
    component_id: str
    requirement_id: str
    overall_score: float
    functional_score: float
    technical_score: float
    performance_score: float
    compatibility_score: float
    confidence: float
    reasoning: str
    risks: List[str]

@dataclass
class ComponentProfile:
    id: str
    name: str
    description: str
    features: List[str]
    tech_stack: List[str]
    performance_metrics: Dict[str, Any]
    compatibility_info: Dict[str, Any]
    metadata: Dict[str, Any]

class MatchingRateAgent:
    """컴포넌트와 요구사항 간의 정확한 매칭률을 계산하는 에이전트"""
    
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
                "Provide detailed reasoning for matching decisions",
                "Identify potential integration risks and challenges"
            ],
            temperature=0.2,
            max_retries=3
        )
        
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    async def calculate_matching_rates(
        self,
        requirements: List[Dict[str, Any]],
        components: List[ComponentProfile]
    ) -> List[List[MatchingResult]]:
        """요구사항과 컴포넌트 간의 매칭률 계산"""
        
        matching_matrix = []
        
        # 벡터화를 위한 텍스트 준비
        req_texts = [self._extract_requirement_text(req) for req in requirements]
        comp_texts = [self._extract_component_text(comp) for comp in components]
        
        # TF-IDF 벡터화
        all_texts = req_texts + comp_texts
        if all_texts:
            vectors = self.vectorizer.fit_transform(all_texts)
            req_vectors = vectors[:len(requirements)]
            comp_vectors = vectors[len(requirements):]
        else:
            req_vectors = comp_vectors = []
        
        # 각 요구사항에 대해 모든 컴포넌트와의 매칭률 계산
        for i, requirement in enumerate(requirements):
            requirement_matches = []
            
            for j, component in enumerate(components):
                # 다차원 매칭 점수 계산
                matching_result = await self._calculate_detailed_match(
                    requirement,
                    component,
                    req_vectors[i] if req_vectors else None,
                    comp_vectors[j] if comp_vectors else None
                )
                
                requirement_matches.append(matching_result)
            
            # 점수순으로 정렬
            requirement_matches.sort(key=lambda x: x.overall_score, reverse=True)
            matching_matrix.append(requirement_matches)
        
        return matching_matrix
    
    async def _calculate_detailed_match(
        self,
        requirement: Dict[str, Any],
        component: ComponentProfile,
        req_vector: Any,
        comp_vector: Any
    ) -> MatchingResult:
        """상세한 매칭 점수 계산"""
        
        # 1. 기능적 매칭 (40%)
        functional_score = await self._calculate_functional_match(requirement, component)
        
        # 2. 기술적 매칭 (30%)
        technical_score = await self._calculate_technical_match(requirement, component)
        
        # 3. 성능 매칭 (20%)
        performance_score = await self._calculate_performance_match(requirement, component)
        
        # 4. 호환성 매칭 (10%)
        compatibility_score = await self._calculate_compatibility_match(requirement, component)
        
        # 5. 의미적 유사도 (벡터 기반)
        semantic_score = 0.0
        if req_vector is not None and comp_vector is not None:
            semantic_score = float(cosine_similarity(req_vector, comp_vector)[0][0])
        
        # 가중 평균으로 전체 점수 계산
        overall_score = (
            functional_score * 0.4 +
            technical_score * 0.3 +
            performance_score * 0.2 +
            compatibility_score * 0.1
        )
        
        # 의미적 유사도로 보정
        overall_score = (overall_score * 0.8) + (semantic_score * 0.2)
        
        # AI 에이전트를 통한 추가 분석
        ai_analysis = await self._get_ai_analysis(requirement, component, overall_score)
        
        return MatchingResult(
            component_id=component.id,
            requirement_id=requirement.get('id', ''),
            overall_score=min(overall_score, 1.0),
            functional_score=functional_score,
            technical_score=technical_score,
            performance_score=performance_score,
            compatibility_score=compatibility_score,
            confidence=ai_analysis.get('confidence', 0.8),
            reasoning=ai_analysis.get('reasoning', ''),
            risks=ai_analysis.get('risks', [])
        )
    
    async def _calculate_functional_match(
        self,
        requirement: Dict[str, Any],
        component: ComponentProfile
    ) -> float:
        """기능적 매칭 점수 계산"""
        
        req_features = set(requirement.get('features', []))
        comp_features = set(component.features)
        
        if not req_features:
            return 0.5
        
        intersection = req_features.intersection(comp_features)
        union = req_features.union(comp_features)
        
        jaccard_score = len(intersection) / len(union) if union else 0
        
        required_features = requirement.get('required_features', [])
        missing_required = set(required_features) - comp_features
        
        if missing_required:
            penalty = len(missing_required) / len(required_features) * 0.5
            jaccard_score = max(0, jaccard_score - penalty)
        
        return min(jaccard_score, 1.0)
    
    async def _calculate_technical_match(
        self,
        requirement: Dict[str, Any],
        component: ComponentProfile
    ) -> float:
        """기술적 매칭 점수 계산"""
        
        req_tech = set(requirement.get('technology_stack', []))
        comp_tech = set(component.tech_stack)
        
        if not req_tech:
            return 0.7
        
        compatible_count = 0
        conflict_count = 0
        
        for tech in req_tech:
            if tech in comp_tech:
                compatible_count += 1
            elif self._is_conflicting_tech(tech, comp_tech):
                conflict_count += 1
        
        compatibility_ratio = compatible_count / len(req_tech)
        conflict_penalty = conflict_count / len(req_tech) * 0.3
        
        return max(0, compatibility_ratio - conflict_penalty)
    
    async def _calculate_performance_match(
        self,
        requirement: Dict[str, Any],
        component: ComponentProfile
    ) -> float:
        """성능 매칭 점수 계산"""
        
        req_performance = requirement.get('performance_requirements', {})
        comp_performance = component.performance_metrics
        
        if not req_performance:
            return 0.8
        
        score = 0.0
        criteria_count = 0
        
        if 'response_time' in req_performance and 'response_time' in comp_performance:
            req_time = req_performance['response_time']
            comp_time = comp_performance['response_time']
            
            if comp_time <= req_time:
                score += 1.0
            else:
                ratio = req_time / comp_time
                score += max(0, ratio)
            
            criteria_count += 1
        
        if 'throughput' in req_performance and 'throughput' in comp_performance:
            req_throughput = req_performance['throughput']
            comp_throughput = comp_performance['throughput']
            
            if comp_throughput >= req_throughput:
                score += 1.0
            else:
                ratio = comp_throughput / req_throughput
                score += max(0, ratio)
            
            criteria_count += 1
        
        return score / criteria_count if criteria_count > 0 else 0.8
    
    async def _calculate_compatibility_match(
        self,
        requirement: Dict[str, Any],
        component: ComponentProfile
    ) -> float:
        """호환성 매칭 점수 계산"""
        
        compatibility_score = 1.0
        
        req_platforms = requirement.get('target_platforms', [])
        comp_platforms = component.compatibility_info.get('platforms', [])
        
        if req_platforms and comp_platforms:
            platform_match = len(set(req_platforms) & set(comp_platforms)) / len(req_platforms)
            compatibility_score *= platform_match
        
        req_versions = requirement.get('version_requirements', {})
        comp_versions = component.compatibility_info.get('supported_versions', {})
        
        for tech, req_version in req_versions.items():
            if tech in comp_versions:
                if not self._is_version_compatible(req_version, comp_versions[tech]):
                    compatibility_score *= 0.5
        
        return compatibility_score
    
    async def _get_ai_analysis(
        self,
        requirement: Dict[str, Any],
        component: ComponentProfile,
        calculated_score: float
    ) -> Dict[str, Any]:
        """AI 에이전트를 통한 추가 분석"""
        
        prompt = f"""
        Analyze the matching between this requirement and component:
        
        Requirement: {json.dumps(requirement, indent=2)}
        Component: {json.dumps(component.__dict__, indent=2)}
        Calculated Score: {calculated_score:.3f}
        
        Provide:
        1. Confidence level (0-1)
        2. Detailed reasoning for the match
        3. Potential risks or challenges
        
        Return as JSON with keys: confidence, reasoning, risks
        """
        
        try:
            response = await self.agent.arun(prompt)
            return json.loads(response.content)
        except Exception:
            return {
                'confidence': 0.7,
                'reasoning': f'Calculated based on feature overlap and technical compatibility. Score: {calculated_score:.3f}',
                'risks': ['Manual verification recommended']
            }
    
    def _extract_requirement_text(self, requirement: Dict[str, Any]) -> str:
        """요구사항에서 텍스트 추출"""
        texts = []
        
        if 'description' in requirement:
            texts.append(requirement['description'])
        
        if 'features' in requirement:
            texts.extend(requirement['features'])
        
        if 'acceptance_criteria' in requirement:
            texts.extend(requirement['acceptance_criteria'])
        
        return ' '.join(texts)
    
    def _extract_component_text(self, component: ComponentProfile) -> str:
        """컴포넌트에서 텍스트 추출"""
        texts = [component.description]
        texts.extend(component.features)
        texts.extend(component.tech_stack)
        
        return ' '.join(texts)
    
    def _is_conflicting_tech(self, tech: str, comp_tech_stack: set) -> bool:
        """기술 스택 충돌 확인"""
        conflicts = {
            'react': ['vue', 'angular'],
            'vue': ['react', 'angular'],
            'angular': ['react', 'vue'],
            'mysql': ['postgresql', 'mongodb'],
            'postgresql': ['mysql', 'mongodb'],
            'mongodb': ['mysql', 'postgresql']
        }
        
        tech_lower = tech.lower()
        if tech_lower in conflicts:
            return any(conflict in [t.lower() for t in comp_tech_stack] 
                      for conflict in conflicts[tech_lower])
        
        return False
    
    def _is_version_compatible(self, required: str, supported: str) -> bool:
        """버전 호환성 확인"""
        try:
            req_parts = [int(x) for x in required.split('.')]
            sup_parts = [int(x) for x in supported.split('.')]
            
            return (req_parts[0] == sup_parts[0] and 
                   sup_parts[1] >= req_parts[1])
        except:
            return True