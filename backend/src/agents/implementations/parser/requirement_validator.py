from typing import Dict, List, Any, Optional
from ..parser_agent import ParsedProject, ParsedRequirement
import re

class RequirementValidator:
    """요구사항 검증기"""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.quality_metrics = self._load_quality_metrics()

    def _load_validation_rules(self) -> Dict[str, Any]:
        """검증 규칙 로드"""
        return {
            'completeness': {
                'min_functional_requirements': 3,
                'required_fields': ['id', 'description', 'priority'],
                'acceptance_criteria_required': True
            },
            'consistency': {
                'priority_levels': ['critical', 'high', 'medium', 'low'],
                'category_mapping': {
                    'functional': ['authentication', 'data_management', 'user_interface'],
                    'non_functional': ['performance', 'security', 'scalability']
                }
            },
            'clarity': {
                'min_description_length': 10,
                'max_description_length': 500,
                'avoid_ambiguous_words': ['maybe', 'possibly', 'might', 'could be']
            },
            'traceability': {
                'id_format': r'^[A-Z]{2,3}-\d{3}(-\d{2})?$',
                'dependency_validation': True
            }
        }

    def _load_quality_metrics(self) -> Dict[str, float]:
        """품질 메트릭 임계값"""
        return {
            'completeness_threshold': 0.8,
            'consistency_threshold': 0.9,
            'clarity_threshold': 0.7,
            'traceability_threshold': 0.85
        }

    async def validate(self, project: ParsedProject) -> ParsedProject:
        """프로젝트 검증"""
        validation_results = {
            'completeness': await self._validate_completeness(project),
            'consistency': await self._validate_consistency(project),
            'clarity': await self._validate_clarity(project),
            'traceability': await self._validate_traceability(project)
        }

        # 검증 결과를 바탕으로 프로젝트 보완
        enhanced_project = await self._enhance_project(project, validation_results)

        # 검증 메타데이터 추가
        enhanced_project.project_info['validation'] = {
            'validated_at': self._get_timestamp(),
            'validation_score': self._calculate_overall_score(validation_results),
            'validation_results': validation_results
        }

        return enhanced_project

    async def _validate_completeness(self, project: ParsedProject) -> Dict[str, Any]:
        """완성도 검증"""
        results = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }

        # 기능 요구사항 수 확인
        min_functional = self.validation_rules['completeness']['min_functional_requirements']
        if len(project.functional_requirements) < min_functional:
            results['issues'].append(
                f"Insufficient functional requirements: {len(project.functional_requirements)} < {min_functional}"
            )
            results['suggestions'].append("Add more detailed functional requirements")

        # 필수 필드 확인
        required_fields = self.validation_rules['completeness']['required_fields']
        all_requirements = (
            project.functional_requirements +
            project.non_functional_requirements +
            project.technical_requirements +
            project.business_requirements
        )

        missing_fields_count = 0
        for req in all_requirements:
            for field in required_fields:
                if not hasattr(req, field) or not getattr(req, field):
                    missing_fields_count += 1

        # 수용 기준 확인
        if self.validation_rules['completeness']['acceptance_criteria_required']:
            no_criteria_count = sum(
                1 for req in project.functional_requirements
                if not req.acceptance_criteria
            )
            if no_criteria_count > 0:
                results['issues'].append(
                    f"{no_criteria_count} functional requirements missing acceptance criteria"
                )

        # 점수 계산
        total_checks = 3
        passed_checks = total_checks - len(results['issues'])
        results['score'] = passed_checks / total_checks

        return results

    async def _validate_consistency(self, project: ParsedProject) -> Dict[str, Any]:
        """일관성 검증"""
        results = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }

        # 우선순위 일관성 확인
        valid_priorities = self.validation_rules['consistency']['priority_levels']
        all_requirements = self._get_all_requirements(project)

        invalid_priorities = []
        for req in all_requirements:
            if req.priority not in valid_priorities:
                invalid_priorities.append(req.id)

        if invalid_priorities:
            results['issues'].append(
                f"Invalid priorities found in: {', '.join(invalid_priorities)}"
            )

        # 카테고리 일관성 확인
        category_mapping = self.validation_rules['consistency']['category_mapping']
        category_issues = []

        for req in all_requirements:
            req_type = req.type.value
            if req_type in category_mapping:
                valid_categories = category_mapping[req_type]
                if req.category not in valid_categories and req.category != 'general':
                    category_issues.append(req.id)

        if category_issues:
            results['issues'].append(
                f"Inconsistent categories in: {', '.join(category_issues)}"
            )

        # ID 형식 일관성 확인
        id_pattern = self.validation_rules['traceability']['id_format']
        invalid_ids = []
        for req in all_requirements:
            if not re.match(id_pattern, req.id):
                invalid_ids.append(req.id)

        if invalid_ids:
            results['issues'].append(
                f"Invalid ID format: {', '.join(invalid_ids)}"
            )

        # 점수 계산
        total_checks = 3
        passed_checks = total_checks - len(results['issues'])
        results['score'] = passed_checks / total_checks

        return results

    async def _validate_clarity(self, project: ParsedProject) -> Dict[str, Any]:
        """명확성 검증"""
        results = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }

        clarity_rules = self.validation_rules['clarity']
        all_requirements = self._get_all_requirements(project)

        # 설명 길이 확인
        length_issues = []
        for req in all_requirements:
            desc_length = len(req.description)
            if desc_length < clarity_rules['min_description_length']:
                length_issues.append(f"{req.id}: too short ({desc_length} chars)")
            elif desc_length > clarity_rules['max_description_length']:
                length_issues.append(f"{req.id}: too long ({desc_length} chars)")

        if length_issues:
            results['issues'].append(f"Description length issues: {', '.join(length_issues)}")

        # 모호한 표현 확인
        ambiguous_words = clarity_rules['avoid_ambiguous_words']
        ambiguous_requirements = []

        for req in all_requirements:
            desc_lower = req.description.lower()
            found_ambiguous = [word for word in ambiguous_words if word in desc_lower]
            if found_ambiguous:
                ambiguous_requirements.append(f"{req.id}: {', '.join(found_ambiguous)}")

        if ambiguous_requirements:
            results['issues'].append(f"Ambiguous language: {'; '.join(ambiguous_requirements)}")
            results['suggestions'].append("Use more specific and concrete language")

        # 점수 계산
        total_requirements = len(all_requirements)
        problematic_requirements = len(length_issues) + len(ambiguous_requirements)
        
        if total_requirements > 0:
            results['score'] = max(0, (total_requirements - problematic_requirements) / total_requirements)
        else:
            results['score'] = 0.0

        return results

    async def _validate_traceability(self, project: ParsedProject) -> Dict[str, Any]:
        """추적성 검증"""
        results = {
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }

        all_requirements = self._get_all_requirements(project)

        # ID 유일성 확인
        ids = [req.id for req in all_requirements]
        duplicate_ids = [id for id in set(ids) if ids.count(id) > 1]
        
        if duplicate_ids:
            results['issues'].append(f"Duplicate IDs found: {', '.join(duplicate_ids)}")

        # 의존성 유효성 확인
        if self.validation_rules['traceability']['dependency_validation']:
            invalid_dependencies = []
            
            for req in all_requirements:
                for dep_id in req.dependencies:
                    if dep_id not in ids:
                        invalid_dependencies.append(f"{req.id} -> {dep_id}")

            if invalid_dependencies:
                results['issues'].append(f"Invalid dependencies: {', '.join(invalid_dependencies)}")

        # 순환 의존성 확인
        circular_deps = self._detect_circular_dependencies(all_requirements)
        if circular_deps:
            results['issues'].append(f"Circular dependencies detected: {', '.join(circular_deps)}")

        # 점수 계산
        total_checks = 3
        passed_checks = total_checks - len(results['issues'])
        results['score'] = passed_checks / total_checks

        return results

    def _detect_circular_dependencies(self, requirements: List[ParsedRequirement]) -> List[str]:
        """순환 의존성 감지"""
        # 간단한 순환 의존성 감지 알고리즘
        dep_graph = {}
        for req in requirements:
            dep_graph[req.id] = req.dependencies

        def has_cycle(node, visited, rec_stack):
            visited[node] = True
            rec_stack[node] = True

            for neighbor in dep_graph.get(node, []):
                if neighbor in dep_graph:
                    if not visited.get(neighbor, False):
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif rec_stack.get(neighbor, False):
                        return True

            rec_stack[node] = False
            return False

        visited = {}
        rec_stack = {}
        cycles = []

        for req_id in dep_graph:
            if not visited.get(req_id, False):
                if has_cycle(req_id, visited, rec_stack):
                    cycles.append(req_id)

        return cycles

    async def _enhance_project(
        self, 
        project: ParsedProject, 
        validation_results: Dict[str, Any]
    ) -> ParsedProject:
        """검증 결과를 바탕으로 프로젝트 보완"""
        
        # 누락된 수용 기준 추가
        for req in project.functional_requirements:
            if not req.acceptance_criteria:
                req.acceptance_criteria = self._generate_default_acceptance_criteria(req)

        # 잘못된 우선순위 수정
        valid_priorities = self.validation_rules['consistency']['priority_levels']
        all_requirements = self._get_all_requirements(project)
        
        for req in all_requirements:
            if req.priority not in valid_priorities:
                req.priority = 'medium'  # 기본값으로 설정

        # 모호한 설명 개선 제안
        ambiguous_words = self.validation_rules['clarity']['avoid_ambiguous_words']
        for req in all_requirements:
            for word in ambiguous_words:
                if word in req.description.lower():
                    if 'enhancement_suggestions' not in req.metadata:
                        req.metadata['enhancement_suggestions'] = []
                    req.metadata['enhancement_suggestions'].append(
                        f"Consider replacing '{word}' with more specific language"
                    )

        return project

    def _generate_default_acceptance_criteria(self, requirement: ParsedRequirement) -> List[str]:
        """기본 수용 기준 생성"""
        criteria = [
            f"Given the system is operational",
            f"When {requirement.description.lower()}",
            f"Then the requirement should be satisfied",
            f"And the user should receive appropriate feedback"
        ]
        return criteria

    def _get_all_requirements(self, project: ParsedProject) -> List[ParsedRequirement]:
        """모든 요구사항 반환"""
        return (
            project.functional_requirements +
            project.non_functional_requirements +
            project.technical_requirements +
            project.business_requirements +
            project.constraints +
            project.assumptions
        )

    def _calculate_overall_score(self, validation_results: Dict[str, Any]) -> float:
        """전체 검증 점수 계산"""
        weights = {
            'completeness': 0.3,
            'consistency': 0.25,
            'clarity': 0.25,
            'traceability': 0.2
        }

        total_score = 0.0
        for category, weight in weights.items():
            if category in validation_results:
                total_score += validation_results[category]['score'] * weight

        return round(total_score, 2)

    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.utcnow().isoformat()