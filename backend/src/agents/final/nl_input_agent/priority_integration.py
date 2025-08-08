"""
T-Developer MVP - Priority Integration

요구사항 우선순위 자동화와 NL Input Agent 통합

Author: T-Developer Team
Created: 2025-01-31
"""

from typing import Dict, List, Any, Optional
from .requirement_prioritizer import RequirementPrioritizer, PrioritizedRequirement

class PriorityIntegration:
    """우선순위 자동화 통합 클래스"""
    
    def __init__(self):
        self.prioritizer = RequirementPrioritizer()
    
    async def integrate_with_nl_agent(
        self,
        project_requirements: Dict[str, Any],
        project_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """NL Input Agent 결과와 우선순위 자동화 통합"""
        
        # 요구사항을 우선순위 시스템 형식으로 변환
        formatted_requirements = self._format_requirements(project_requirements)
        
        # 프로젝트 컨텍스트 준비
        context = self._prepare_context(project_requirements, project_context)
        
        # 우선순위 계산
        prioritized = await self.prioritizer.prioritize_requirements(
            formatted_requirements, 
            context
        )
        
        # 결과를 원래 형식에 통합
        return self._integrate_results(project_requirements, prioritized)
    
    def _format_requirements(self, project_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """요구사항을 우선순위 시스템 형식으로 변환"""
        formatted = []
        
        # 기능 요구사항 변환
        for i, req in enumerate(project_requirements.get('functional_requirements', [])):
            formatted.append({
                'id': f'FR-{i+1:03d}',
                'description': req,
                'type': 'functional',
                'complexity': self._estimate_complexity_from_text(req),
                'user_impact': self._estimate_user_impact(req),
                'business_priority': 'medium'
            })
        
        # 기술 요구사항 변환
        for i, req in enumerate(project_requirements.get('technical_requirements', [])):
            formatted.append({
                'id': f'TR-{i+1:03d}',
                'description': req.get('description', str(req)),
                'type': 'technical',
                'complexity': req.get('complexity', 'medium'),
                'technical_risk': req.get('priority', 'medium').lower(),
                'business_priority': req.get('priority', 'medium').lower()
            })
        
        return formatted
    
    def _prepare_context(
        self, 
        project_requirements: Dict[str, Any], 
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """프로젝트 컨텍스트 준비"""
        context = {
            'project_type': project_requirements.get('project_type', 'web_application'),
            'complexity': project_requirements.get('estimated_complexity', 'medium'),
            'sprint_capacity': 20,  # 기본값
            'strategic_goals': []
        }
        
        # 기술 선호도에서 전략적 목표 추출
        tech_prefs = project_requirements.get('technology_preferences', {})
        if tech_prefs:
            context['strategic_goals'].extend([
                f"use {tech}" for tech in tech_prefs.get('preferred', [])
            ])
        
        # 추가 컨텍스트 병합
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def _integrate_results(
        self, 
        original_requirements: Dict[str, Any], 
        prioritized: List[PrioritizedRequirement]
    ) -> Dict[str, Any]:
        """우선순위 결과를 원래 요구사항에 통합"""
        result = original_requirements.copy()
        
        # 우선순위 정보 추가
        result['prioritized_requirements'] = [
            {
                'id': req.requirement['id'],
                'description': req.requirement['description'],
                'type': req.requirement['type'],
                'priority_score': req.priority_score,
                'estimated_effort': req.estimated_effort,
                'business_value': req.business_value,
                'risk_level': req.risk_level,
                'recommended_sprint': req.recommended_sprint,
                'dependencies': req.dependencies
            }
            for req in prioritized
        ]
        
        # 스프린트 계획 생성
        result['sprint_plan'] = self._generate_sprint_plan(prioritized)
        
        # 우선순위 요약
        result['priority_summary'] = self._generate_priority_summary(prioritized)
        
        return result
    
    def _generate_sprint_plan(self, prioritized: List[PrioritizedRequirement]) -> Dict[str, Any]:
        """스프린트 계획 생성"""
        sprints = {}
        
        for req in prioritized:
            sprint_num = req.recommended_sprint
            if sprint_num not in sprints:
                sprints[sprint_num] = {
                    'sprint': sprint_num,
                    'requirements': [],
                    'total_effort': 0,
                    'total_value': 0
                }
            
            sprints[sprint_num]['requirements'].append({
                'id': req.requirement['id'],
                'description': req.requirement['description'],
                'effort': req.estimated_effort,
                'value': req.business_value
            })
            sprints[sprint_num]['total_effort'] += req.estimated_effort
            sprints[sprint_num]['total_value'] += req.business_value
        
        return {
            'total_sprints': len(sprints),
            'sprints': list(sprints.values())
        }
    
    def _generate_priority_summary(self, prioritized: List[PrioritizedRequirement]) -> Dict[str, Any]:
        """우선순위 요약 생성"""
        if not prioritized:
            return {}
        
        high_priority = [req for req in prioritized if req.priority_score > 0.7]
        medium_priority = [req for req in prioritized if 0.3 <= req.priority_score <= 0.7]
        low_priority = [req for req in prioritized if req.priority_score < 0.3]
        
        return {
            'total_requirements': len(prioritized),
            'high_priority_count': len(high_priority),
            'medium_priority_count': len(medium_priority),
            'low_priority_count': len(low_priority),
            'average_priority_score': sum(req.priority_score for req in prioritized) / len(prioritized),
            'total_estimated_effort': sum(req.estimated_effort for req in prioritized),
            'highest_priority_requirement': {
                'id': prioritized[0].requirement['id'],
                'description': prioritized[0].requirement['description'],
                'score': prioritized[0].priority_score
            } if prioritized else None
        }
    
    def _estimate_complexity_from_text(self, text: str) -> str:
        """텍스트에서 복잡도 추정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['simple', 'basic', 'crud']):
            return 'simple'
        elif any(word in text_lower for word in ['complex', 'advanced', 'integrate']):
            return 'complex'
        else:
            return 'medium'
    
    def _estimate_user_impact(self, text: str) -> str:
        """텍스트에서 사용자 영향도 추정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'essential', 'must']):
            return 'high'
        elif any(word in text_lower for word in ['nice', 'optional', 'enhancement']):
            return 'low'
        else:
            return 'medium'