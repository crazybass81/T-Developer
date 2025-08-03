# backend/src/agents/implementations/component_decision_agent.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from agno.agent import Agent
from agno.models.aws import AwsBedrock

@dataclass
class ComponentDecision:
    component_id: str
    decision: str  # selected, rejected, conditional
    confidence: float
    reasoning: str
    alternatives: List[str]
    risks: List[str]
    adaptation_required: bool

class ComponentDecisionAgent:
    """컴포넌트 선택 결정을 내리는 에이전트"""

    def __init__(self):
        self.decision_agent = Agent(
            name="Component-Decision-Maker",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            role="Expert software architect making component decisions",
            instructions=[
                "Analyze component options and make optimal selections",
                "Consider technical fit, maintainability, and risks",
                "Provide clear reasoning for decisions",
                "Identify potential alternatives and fallbacks"
            ],
            temperature=0.3
        )
        
        self.risk_analyzer = RiskAnalyzer()
        self.compatibility_checker = CompatibilityChecker()

    async def make_component_decisions(
        self,
        requirements: Dict[str, Any],
        component_options: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ComponentDecision]:
        """컴포넌트 선택 결정"""
        
        decisions = []
        
        for component in component_options:
            # 기술적 적합성 평가
            tech_fit = await self._evaluate_technical_fit(component, requirements)
            
            # 리스크 분석
            risks = await self.risk_analyzer.analyze(component, context)
            
            # 호환성 검사
            compatibility = await self.compatibility_checker.check(component, requirements)
            
            # 최종 결정
            decision = await self._make_final_decision(
                component, tech_fit, risks, compatibility
            )
            
            decisions.append(decision)
        
        return self._rank_decisions(decisions)

    async def _evaluate_technical_fit(
        self,
        component: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> float:
        """기술적 적합성 평가"""
        
        prompt = f"""
        Evaluate technical fit between component and requirements:
        
        Component: {component.get('name', 'Unknown')}
        - Technology: {component.get('technology', [])}
        - Features: {component.get('features', [])}
        
        Requirements:
        - Tech Stack: {requirements.get('tech_stack', [])}
        - Features Needed: {requirements.get('features', [])}
        
        Rate fit from 0.0 to 1.0 and explain reasoning.
        """
        
        result = await self.decision_agent.arun(prompt)
        return self._extract_score(result.content)

    def _rank_decisions(self, decisions: List[ComponentDecision]) -> List[ComponentDecision]:
        """결정 순위 매기기"""
        return sorted(decisions, key=lambda d: d.confidence, reverse=True)

class RiskAnalyzer:
    """컴포넌트 리스크 분석기"""
    
    async def analyze(self, component: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        risks = []
        
        # 기술적 리스크
        if component.get('maturity', 'stable') == 'experimental':
            risks.append("Experimental technology - stability concerns")
        
        # 라이선스 리스크
        license_type = component.get('license', 'unknown')
        if license_type in ['GPL', 'AGPL']:
            risks.append("Copyleft license may restrict commercial use")
        
        # 의존성 리스크
        deps = component.get('dependencies', [])
        if len(deps) > 20:
            risks.append("High dependency count increases maintenance burden")
        
        return risks

class CompatibilityChecker:
    """호환성 검사기"""
    
    async def check(self, component: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """호환성 점수 계산"""
        
        score = 1.0
        
        # 버전 호환성
        req_version = requirements.get('version_constraints', {})
        comp_version = component.get('version', '1.0.0')
        
        if not self._version_compatible(comp_version, req_version):
            score *= 0.5
        
        # 플랫폼 호환성
        req_platforms = set(requirements.get('platforms', []))
        comp_platforms = set(component.get('supported_platforms', []))
        
        if req_platforms and not req_platforms.intersection(comp_platforms):
            score *= 0.3
        
        return score
    
    def _version_compatible(self, version: str, constraints: Dict[str, str]) -> bool:
        """버전 호환성 검사"""
        # 간단한 버전 체크 로직
        return True  # 실제 구현에서는 semver 라이브러리 사용