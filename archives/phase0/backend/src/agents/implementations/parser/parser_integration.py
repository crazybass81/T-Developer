# backend/src/agents/implementations/parser_integration.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
from parser_requirement_separator import RequirementSeparator, ParsedRequirement
from parser_dependency_analyzer import DependencyAnalyzer, DependencyGraph
from parser_user_story_generator import UserStoryGenerator, UserStory, Epic

@dataclass
class RequirementAnalysisResult:
    functional_requirements: List[ParsedRequirement]
    non_functional_requirements: List[ParsedRequirement]
    dependency_graph: DependencyGraph
    user_stories: List[UserStory]
    epics: List[Epic]
    personas: List[str]
    analysis_summary: Dict[str, Any]

class ParserRequirementAnalyzer:
    """Parser Agent의 요구사항 분석 통합 클래스"""

    def __init__(self):
        self.requirement_separator = RequirementSeparator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.user_story_generator = UserStoryGenerator()

    async def analyze_requirements(
        self,
        raw_requirements: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> RequirementAnalysisResult:
        """포괄적인 요구사항 분석 수행"""

        # 1. 기능/비기능 요구사항 분리
        functional_reqs, non_functional_reqs = await self.requirement_separator.separate_requirements(
            raw_requirements, context
        )

        # 2. 의존성 분석을 위한 데이터 준비
        all_requirements = []
        for req in functional_reqs + non_functional_reqs:
            all_requirements.append({
                'id': req.id,
                'description': req.description,
                'type': req.type.value,
                'category': req.category
            })

        # 3. 의존성 분석
        dependency_graph = await self.dependency_analyzer.analyze_dependencies(
            all_requirements, context
        )

        # 4. 사용자 스토리 생성 (기능 요구사항만)
        functional_req_dicts = [
            {
                'id': req.id,
                'type': 'functional',
                'description': req.description,
                'actor': req.actor,
                'action': req.action,
                'object_info': req.object_info
            }
            for req in functional_reqs
        ]

        story_result = await self.user_story_generator.generate_user_stories(
            functional_req_dicts, context
        )

        # 5. 분석 요약 생성
        analysis_summary = self._generate_analysis_summary(
            functional_reqs,
            non_functional_reqs,
            dependency_graph,
            story_result
        )

        return RequirementAnalysisResult(
            functional_requirements=functional_reqs,
            non_functional_requirements=non_functional_reqs,
            dependency_graph=dependency_graph,
            user_stories=story_result['user_stories'],
            epics=story_result.get('epics', []),
            personas=story_result.get('personas', []),
            analysis_summary=analysis_summary
        )

    def _generate_analysis_summary(
        self,
        functional_reqs: List[ParsedRequirement],
        non_functional_reqs: List[ParsedRequirement],
        dependency_graph: DependencyGraph,
        story_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """분석 요약 생성"""

        # 우선순위별 분포
        priority_distribution = {}
        for req in functional_reqs + non_functional_reqs:
            priority_distribution[req.priority] = priority_distribution.get(req.priority, 0) + 1

        # 카테고리별 분포
        category_distribution = {}
        for req in non_functional_reqs:
            category_distribution[req.category] = category_distribution.get(req.category, 0) + 1

        # 복잡도 분석
        complexity_analysis = self._analyze_complexity(functional_reqs, dependency_graph)

        return {
            'total_requirements': len(functional_reqs) + len(non_functional_reqs),
            'functional_count': len(functional_reqs),
            'non_functional_count': len(non_functional_reqs),
            'priority_distribution': priority_distribution,
            'category_distribution': category_distribution,
            'dependency_count': len(dependency_graph.edges),
            'circular_dependencies': len(dependency_graph.cycles),
            'user_stories_count': len(story_result.get('user_stories', [])),
            'epics_count': len(story_result.get('epics', [])),
            'total_story_points': story_result.get('total_story_points', 0),
            'personas_identified': len(story_result.get('personas', [])),
            'complexity_analysis': complexity_analysis,
            'critical_path_length': len(dependency_graph.critical_path),
            'max_dependency_level': max(dependency_graph.levels.values()) if dependency_graph.levels else 0
        }

    def _analyze_complexity(
        self,
        functional_reqs: List[ParsedRequirement],
        dependency_graph: DependencyGraph
    ) -> Dict[str, Any]:
        """복잡도 분석"""

        # 액터 다양성
        actors = set()
        for req in functional_reqs:
            if req.actor:
                actors.add(req.actor)

        # 액션 다양성
        actions = set()
        for req in functional_reqs:
            if req.action:
                actions.add(req.action)

        # 의존성 복잡도
        dependency_complexity = len(dependency_graph.edges) / len(dependency_graph.nodes) if dependency_graph.nodes else 0

        # 전체 복잡도 점수 (0-10)
        complexity_score = min(10, (
            len(actors) * 0.5 +
            len(actions) * 0.3 +
            dependency_complexity * 2 +
            len(dependency_graph.cycles) * 2
        ))

        return {
            'unique_actors': len(actors),
            'unique_actions': len(actions),
            'dependency_complexity': dependency_complexity,
            'circular_dependencies': len(dependency_graph.cycles),
            'overall_complexity_score': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score)
        }

    def _get_complexity_level(self, score: float) -> str:
        """복잡도 레벨 결정"""
        if score >= 8:
            return 'very_high'
        elif score >= 6:
            return 'high'
        elif score >= 4:
            return 'medium'
        elif score >= 2:
            return 'low'
        else:
            return 'very_low'

    async def validate_analysis_quality(
        self,
        result: RequirementAnalysisResult
    ) -> Dict[str, Any]:
        """분석 품질 검증"""

        quality_checks = {
            'completeness': self._check_completeness(result),
            'consistency': self._check_consistency(result),
            'traceability': self._check_traceability(result),
            'coverage': self._check_coverage(result)
        }

        overall_quality = sum(quality_checks.values()) / len(quality_checks)

        return {
            'quality_checks': quality_checks,
            'overall_quality_score': overall_quality,
            'quality_level': self._get_quality_level(overall_quality),
            'recommendations': self._generate_quality_recommendations(quality_checks)
        }

    def _check_completeness(self, result: RequirementAnalysisResult) -> float:
        """완성도 검사"""
        score = 0.0
        
        # 모든 기능 요구사항에 수용 기준이 있는지
        if result.functional_requirements:
            with_criteria = sum(1 for req in result.functional_requirements 
                              if req.acceptance_criteria and len(req.acceptance_criteria) > 0)
            score += (with_criteria / len(result.functional_requirements)) * 0.4
        
        # 사용자 스토리가 생성되었는지
        if result.user_stories:
            score += 0.3
        
        # 의존성이 분석되었는지
        if result.dependency_graph.edges:
            score += 0.3
        
        return min(1.0, score)

    def _check_consistency(self, result: RequirementAnalysisResult) -> float:
        """일관성 검사"""
        score = 1.0
        
        # 순환 의존성이 있으면 점수 감점
        if result.dependency_graph.cycles:
            score -= len(result.dependency_graph.cycles) * 0.2
        
        # ID 중복 검사
        all_ids = [req.id for req in result.functional_requirements + result.non_functional_requirements]
        if len(all_ids) != len(set(all_ids)):
            score -= 0.3
        
        return max(0.0, score)

    def _check_traceability(self, result: RequirementAnalysisResult) -> float:
        """추적성 검사"""
        score = 0.0
        
        # 사용자 스토리와 요구사항 간 추적성
        if result.user_stories and result.functional_requirements:
            score += 0.5
        
        # 의존성 그래프의 연결성
        if result.dependency_graph.edges:
            connected_nodes = set()
            for edge in result.dependency_graph.edges:
                connected_nodes.add(edge.source_id)
                connected_nodes.add(edge.target_id)
            
            if result.dependency_graph.nodes:
                connectivity = len(connected_nodes) / len(result.dependency_graph.nodes)
                score += connectivity * 0.5
        
        return score

    def _check_coverage(self, result: RequirementAnalysisResult) -> float:
        """커버리지 검사"""
        score = 0.0
        
        # 기능/비기능 요구사항 균형
        total_reqs = len(result.functional_requirements) + len(result.non_functional_requirements)
        if total_reqs > 0:
            functional_ratio = len(result.functional_requirements) / total_reqs
            # 적절한 비율 (60-80% 기능 요구사항)
            if 0.6 <= functional_ratio <= 0.8:
                score += 0.4
            else:
                score += 0.2
        
        # 페르소나 다양성
        if len(result.personas) >= 2:
            score += 0.3
        elif len(result.personas) >= 1:
            score += 0.2
        
        # 우선순위 분포
        priorities = [req.priority for req in result.functional_requirements + result.non_functional_requirements]
        unique_priorities = set(priorities)
        if len(unique_priorities) >= 3:
            score += 0.3
        elif len(unique_priorities) >= 2:
            score += 0.2
        
        return score

    def _get_quality_level(self, score: float) -> str:
        """품질 레벨 결정"""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'good'
        elif score >= 0.7:
            return 'acceptable'
        elif score >= 0.6:
            return 'needs_improvement'
        else:
            return 'poor'

    def _generate_quality_recommendations(self, quality_checks: Dict[str, float]) -> List[str]:
        """품질 개선 권장사항 생성"""
        recommendations = []
        
        if quality_checks['completeness'] < 0.8:
            recommendations.append("Add acceptance criteria to all functional requirements")
        
        if quality_checks['consistency'] < 0.8:
            recommendations.append("Resolve circular dependencies and ID conflicts")
        
        if quality_checks['traceability'] < 0.7:
            recommendations.append("Improve traceability between requirements and user stories")
        
        if quality_checks['coverage'] < 0.7:
            recommendations.append("Balance functional and non-functional requirements")
            recommendations.append("Identify additional personas and priorities")
        
        return recommendations