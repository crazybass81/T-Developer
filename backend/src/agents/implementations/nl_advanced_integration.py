from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from .nl_input_agent import NLInputAgent
from .nl_domain_specific import DomainSpecificNLProcessor
from .nl_intent_analyzer import IntentAnalyzer
from .nl_priority_analyzer import RequirementPrioritizer, ParsedRequirement

@dataclass
class AdvancedNLResult:
    basic_requirements: Any
    domain_analysis: Any
    intent_analysis: Any
    prioritized_requirements: List[Any]
    confidence_score: float
    processing_time: float
    recommendations: List[str]

class AdvancedNLIntegration:
    """고급 NL 기능 통합 시스템"""
    
    def __init__(self):
        self.nl_agent = NLInputAgent()
        self.domain_processor = DomainSpecificNLProcessor()
        self.intent_analyzer = IntentAnalyzer()
        self.prioritizer = RequirementPrioritizer()
    
    async def process_advanced_requirements(
        self,
        description: str,
        context: Optional[Dict] = None
    ) -> AdvancedNLResult:
        """고급 요구사항 처리 통합"""
        
        import time
        start_time = time.time()
        
        # 병렬 처리
        tasks = [
            self.nl_agent.process_description(description, context),
            self.domain_processor.process_domain_specific_requirements(description),
            self.intent_analyzer.analyze_user_intent(description, context)
        ]
        
        basic_req, domain_analysis, intent_analysis = await asyncio.gather(*tasks)
        
        # 요구사항 우선순위 결정
        parsed_requirements = self._convert_to_parsed_requirements(basic_req)
        prioritized = await self.prioritizer.prioritize_requirements(
            parsed_requirements, 
            context or {}
        )
        
        # 신뢰도 점수 계산
        confidence = self._calculate_overall_confidence(
            basic_req, domain_analysis, intent_analysis
        )
        
        # 추천사항 생성
        recommendations = self._generate_recommendations(
            basic_req, domain_analysis, intent_analysis, prioritized
        )
        
        processing_time = time.time() - start_time
        
        return AdvancedNLResult(
            basic_requirements=basic_req,
            domain_analysis=domain_analysis,
            intent_analysis=intent_analysis,
            prioritized_requirements=prioritized,
            confidence_score=confidence,
            processing_time=processing_time,
            recommendations=recommendations
        )
    
    def _convert_to_parsed_requirements(self, basic_req: Any) -> List[ParsedRequirement]:
        """기본 요구사항을 ParsedRequirement로 변환"""
        requirements = []
        
        for i, req in enumerate(basic_req.technical_requirements):
            requirements.append(ParsedRequirement(
                id=f"req_{i}",
                description=req,
                type=self._classify_requirement_type(req),
                complexity=self._estimate_complexity(req)
            ))
        
        return requirements
    
    def _classify_requirement_type(self, requirement: str) -> str:
        """요구사항 타입 분류"""
        req_lower = requirement.lower()
        
        if any(word in req_lower for word in ['auth', 'login', 'user']):
            return 'user_management'
        elif any(word in req_lower for word in ['ui', 'interface', 'design']):
            return 'user_interface'
        elif any(word in req_lower for word in ['performance', 'speed', 'fast']):
            return 'performance'
        elif any(word in req_lower for word in ['security', 'encrypt', 'secure']):
            return 'security'
        elif any(word in req_lower for word in ['api', 'integrate', 'connect']):
            return 'integration'
        else:
            return 'core_functionality'
    
    def _estimate_complexity(self, requirement: str) -> int:
        """요구사항 복잡도 추정 (1-5)"""
        complexity_indicators = {
            'simple': ['basic', 'simple', 'standard'],
            'medium': ['advanced', 'complex', 'multiple'],
            'high': ['enterprise', 'scalable', 'distributed', 'real-time']
        }
        
        req_lower = requirement.lower()
        
        if any(word in req_lower for word in complexity_indicators['high']):
            return 5
        elif any(word in req_lower for word in complexity_indicators['medium']):
            return 3
        elif any(word in req_lower for word in complexity_indicators['simple']):
            return 1
        else:
            return 2
    
    def _calculate_overall_confidence(
        self, 
        basic_req: Any, 
        domain_analysis: Any, 
        intent_analysis: Any
    ) -> float:
        """전체 신뢰도 점수 계산"""
        
        # 기본 요구사항 신뢰도 (가정)
        basic_confidence = 0.8
        
        # 도메인 분석 신뢰도
        domain_confidence = 0.9 if domain_analysis.domain != 'general' else 0.6
        
        # 의도 분석 신뢰도
        intent_confidence = intent_analysis.confidence
        
        # 가중 평균
        overall_confidence = (
            basic_confidence * 0.4 +
            domain_confidence * 0.3 +
            intent_confidence * 0.3
        )
        
        return min(overall_confidence, 1.0)
    
    def _generate_recommendations(
        self,
        basic_req: Any,
        domain_analysis: Any,
        intent_analysis: Any,
        prioritized: List[Any]
    ) -> List[str]:
        """추천사항 생성"""
        recommendations = []
        
        # 도메인별 추천
        if domain_analysis.domain != 'general':
            recommendations.append(
                f"Consider {domain_analysis.domain} domain-specific requirements"
            )
            
            if domain_analysis.compliance_requirements:
                recommendations.append(
                    f"Ensure compliance with: {', '.join(domain_analysis.compliance_requirements)}"
                )
        
        # 의도별 추천
        if intent_analysis.primary.value == 'build_new':
            recommendations.append("Start with MVP approach for new development")
        elif intent_analysis.primary.value == 'migrate_existing':
            recommendations.append("Plan for gradual migration strategy")
        
        # 우선순위별 추천
        high_priority_count = sum(1 for p in prioritized if p.priority_score > 0.7)
        if high_priority_count > 5:
            recommendations.append("Consider breaking down into multiple phases")
        
        # 기술적 추천
        if any('performance' in req.lower() for req in basic_req.technical_requirements):
            recommendations.append("Implement performance monitoring from the start")
        
        if any('security' in req.lower() for req in basic_req.technical_requirements):
            recommendations.append("Conduct security review at each milestone")
        
        return recommendations