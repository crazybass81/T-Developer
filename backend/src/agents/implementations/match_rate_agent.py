# backend/src/agents/implementations/match_rate_agent.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class MatchScore:
    requirement_id: str
    component_id: str
    score: float  # 0.0 ~ 1.0
    confidence: float
    match_details: Dict[str, Any]

class MatchRateAgent:
    """요구사항과 컴포넌트 간의 매칭률을 계산하는 에이전트"""

    def __init__(self):
        self.matcher = Agent(
            name="Match-Rate-Calculator",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Expert component matching specialist",
            instructions=[
                "Calculate precise matching scores between requirements and components",
                "Consider functional, technical, and quality aspects",
                "Provide detailed match analysis and recommendations"
            ],
            temperature=0.2
        )
        
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.semantic_matcher = SemanticMatcher()
        self.technical_matcher = TechnicalMatcher()

    async def calculate_match_rates(
        self,
        requirements: List[Dict[str, Any]],
        components: List[Dict[str, Any]]
    ) -> List[List[MatchScore]]:
        """요구사항과 컴포넌트 간의 매칭률 계산"""
        
        match_matrix = []
        
        for req in requirements:
            req_matches = []
            
            for comp in components:
                # 다차원 매칭 수행
                semantic_score = await self._calculate_semantic_match(req, comp)
                technical_score = await self._calculate_technical_match(req, comp)
                functional_score = await self._calculate_functional_match(req, comp)
                
                # 가중 평균으로 최종 점수 계산
                final_score = (
                    semantic_score * 0.4 +
                    technical_score * 0.3 +
                    functional_score * 0.3
                )
                
                # 신뢰도 계산
                confidence = self._calculate_confidence([
                    semantic_score, technical_score, functional_score
                ])
                
                match_score = MatchScore(
                    requirement_id=req.get('id', ''),
                    component_id=comp.get('id', ''),
                    score=final_score,
                    confidence=confidence,
                    match_details={
                        'semantic': semantic_score,
                        'technical': technical_score,
                        'functional': functional_score
                    }
                )
                
                req_matches.append(match_score)
            
            # 점수 기준 정렬
            req_matches.sort(key=lambda x: x.score, reverse=True)
            match_matrix.append(req_matches)
        
        return match_matrix

    async def _calculate_semantic_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """의미적 유사도 계산"""
        
        req_text = self._extract_text(requirement)
        comp_text = self._extract_text(component)
        
        if not req_text or not comp_text:
            return 0.0
        
        # TF-IDF 벡터화
        texts = [req_text, comp_text]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # 코사인 유사도 계산
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(max(0.0, similarity))

    async def _calculate_technical_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """기술적 매칭 점수"""
        
        req_tech = set(requirement.get('technologies', []))
        comp_tech = set(component.get('technologies', []))
        
        if not req_tech:
            return 1.0  # 기술 요구사항이 없으면 완전 매칭
        
        # 교집합 비율 계산
        intersection = req_tech.intersection(comp_tech)
        match_ratio = len(intersection) / len(req_tech)
        
        return float(match_ratio)

    async def _calculate_functional_match(
        self,
        requirement: Dict[str, Any],
        component: Dict[str, Any]
    ) -> float:
        """기능적 매칭 점수"""
        
        req_features = set(requirement.get('features', []))
        comp_features = set(component.get('features', []))
        
        if not req_features:
            return 1.0
        
        # 기능 매칭 비율
        matched_features = req_features.intersection(comp_features)
        match_ratio = len(matched_features) / len(req_features)
        
        return float(match_ratio)

    def _extract_text(self, item: Dict[str, Any]) -> str:
        """텍스트 추출"""
        text_parts = []
        
        if 'description' in item:
            text_parts.append(item['description'])
        if 'name' in item:
            text_parts.append(item['name'])
        if 'summary' in item:
            text_parts.append(item['summary'])
        
        return ' '.join(text_parts)

    def _calculate_confidence(self, scores: List[float]) -> float:
        """신뢰도 계산"""
        if not scores:
            return 0.0
        
        # 점수들의 표준편차가 낮을수록 신뢰도 높음
        std_dev = np.std(scores)
        confidence = 1.0 - min(std_dev, 1.0)
        
        return float(confidence)

class SemanticMatcher:
    """의미적 매칭 엔진"""
    
    async def match(self, text1: str, text2: str) -> float:
        """의미적 유사도 계산"""
        # 실제 구현에서는 sentence transformers 등 사용
        return 0.8  # 임시값

class TechnicalMatcher:
    """기술적 매칭 엔진"""
    
    async def match(self, req_tech: List[str], comp_tech: List[str]) -> float:
        """기술 스택 매칭"""
        if not req_tech:
            return 1.0
        
        matched = set(req_tech).intersection(set(comp_tech))
        return len(matched) / len(req_tech)