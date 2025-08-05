"""
Parser Agent - Requirement Validation System
SubTask 4.23.1: 요구사항 검증 시스템 구현
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime

@dataclass
class ValidationError:
    requirement_id: str
    error_type: str
    severity: str  # critical, high, medium, low
    message: str
    suggestion: Optional[str] = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    quality_score: float
    completeness_score: float
    consistency_score: float
    recommendations: List[str]

class RequirementValidator:
    """요구사항 검증 시스템"""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.quality_metrics = self._initialize_quality_metrics()
        self.consistency_checker = ConsistencyChecker()
        self.completeness_checker = CompletenessChecker()

    async def validate(self, parsed_project) -> 'ParsedProject':
        """프로젝트 요구사항 검증"""
        
        # 1. 개별 요구사항 검증
        all_requirements = (
            parsed_project.functional_requirements +
            parsed_project.non_functional_requirements +
            parsed_project.technical_requirements +
            parsed_project.business_requirements
        )
        
        validation_results = []
        for req in all_requirements:
            result = await self._validate_single_requirement(req)
            validation_results.append(result)
        
        # 2. 일관성 검증
        consistency_result = await self.consistency_checker.check_consistency(all_requirements)
        
        # 3. 완성도 검증
        completeness_result = await self.completeness_checker.check_completeness(parsed_project)
        
        # 4. 전체 품질 점수 계산
        overall_quality = self._calculate_overall_quality(
            validation_results,
            consistency_result,
            completeness_result
        )
        
        # 5. 검증 결과를 메타데이터에 추가
        parsed_project.project_info['validation'] = {
            'validated_at': datetime.utcnow().isoformat(),
            'quality_score': overall_quality,
            'validation_results': validation_results,
            'consistency_score': consistency_result.score,
            'completeness_score': completeness_result.score
        }
        
        return parsed_project

    async def _validate_single_requirement(self, requirement) -> ValidationResult:
        """단일 요구사항 검증"""
        
        errors = []
        warnings = []
        
        # 1. 기본 구조 검증
        structure_errors = self._validate_structure(requirement)
        errors.extend(structure_errors)
        
        # 2. 내용 품질 검증
        quality_errors, quality_warnings = self._validate_quality(requirement)
        errors.extend(quality_errors)
        warnings.extend(quality_warnings)
        
        # 3. 명확성 검증
        clarity_warnings = self._validate_clarity(requirement)
        warnings.extend(clarity_warnings)
        
        # 4. 측정 가능성 검증
        measurability_warnings = self._validate_measurability(requirement)
        warnings.extend(measurability_warnings)
        
        # 5. 점수 계산
        quality_score = self._calculate_quality_score(requirement, errors, warnings)
        completeness_score = self._calculate_completeness_score(requirement)
        consistency_score = self._calculate_consistency_score(requirement)
        
        # 6. 추천사항 생성
        recommendations = self._generate_recommendations(requirement, errors, warnings)
        
        return ValidationResult(
            is_valid=len([e for e in errors if e.severity in ['critical', 'high']]) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            recommendations=recommendations
        )

    def _validate_structure(self, requirement) -> List[ValidationError]:
        """구조 검증"""
        errors = []
        
        # 필수 필드 검증
        required_fields = ['id', 'type', 'description', 'priority']
        for field in required_fields:
            if not hasattr(requirement, field) or not getattr(requirement, field):
                errors.append(ValidationError(
                    requirement_id=getattr(requirement, 'id', 'unknown'),
                    error_type='missing_field',
                    severity='critical',
                    message=f"Required field '{field}' is missing or empty",
                    suggestion=f"Please provide a value for '{field}'"
                ))
        
        # ID 형식 검증
        if hasattr(requirement, 'id') and requirement.id:
            if not re.match(r'^[A-Z]{2,3}-\d{3}$', requirement.id):
                errors.append(ValidationError(
                    requirement_id=requirement.id,
                    error_type='invalid_format',
                    severity='medium',
                    message="Requirement ID format is invalid",
                    suggestion="Use format like 'FR-001' or 'NFR-001'"
                ))
        
        # 우선순위 값 검증
        if hasattr(requirement, 'priority') and requirement.priority:
            valid_priorities = ['critical', 'high', 'medium', 'low']
            if requirement.priority not in valid_priorities:
                errors.append(ValidationError(
                    requirement_id=getattr(requirement, 'id', 'unknown'),
                    error_type='invalid_value',
                    severity='medium',
                    message=f"Invalid priority value: {requirement.priority}",
                    suggestion=f"Use one of: {', '.join(valid_priorities)}"
                ))
        
        return errors

    def _validate_quality(self, requirement) -> Tuple[List[ValidationError], List[ValidationError]]:
        """품질 검증"""
        errors = []
        warnings = []
        
        if not hasattr(requirement, 'description') or not requirement.description:
            return errors, warnings
        
        description = requirement.description
        
        # 길이 검증
        if len(description) < 10:
            warnings.append(ValidationError(
                requirement_id=getattr(requirement, 'id', 'unknown'),
                error_type='too_short',
                severity='medium',
                message="Requirement description is too short",
                suggestion="Provide more detailed description (at least 10 characters)"
            ))
        elif len(description) > 500:
            warnings.append(ValidationError(
                requirement_id=getattr(requirement, 'id', 'unknown'),
                error_type='too_long',
                severity='low',
                message="Requirement description is very long",
                suggestion="Consider breaking into smaller requirements"
            ))
        
        # 모호한 표현 검증
        ambiguous_words = ['some', 'many', 'few', 'several', 'appropriate', 'reasonable', 'good', 'bad']
        found_ambiguous = [word for word in ambiguous_words if word in description.lower()]
        
        if found_ambiguous:
            warnings.append(ValidationError(
                requirement_id=getattr(requirement, 'id', 'unknown'),
                error_type='ambiguous_language',
                severity='medium',
                message=f"Ambiguous words found: {', '.join(found_ambiguous)}",
                suggestion="Use specific, measurable terms instead"
            ))
        
        # 수동태 검증
        passive_patterns = [r'\bis\s+\w+ed\b', r'\bwill\s+be\s+\w+ed\b', r'\bshould\s+be\s+\w+ed\b']
        passive_found = any(re.search(pattern, description, re.IGNORECASE) for pattern in passive_patterns)
        
        if passive_found:
            warnings.append(ValidationError(
                requirement_id=getattr(requirement, 'id', 'unknown'),
                error_type='passive_voice',
                severity='low',
                message="Passive voice detected in requirement",
                suggestion="Use active voice for clearer requirements"
            ))
        
        return errors, warnings

    def _validate_clarity(self, requirement) -> List[ValidationError]:
        """명확성 검증"""
        warnings = []
        
        if not hasattr(requirement, 'description'):
            return warnings
        
        description = requirement.description
        
        # 복잡한 문장 구조 검증
        sentence_count = len([s for s in description.split('.') if s.strip()])
        if sentence_count > 3:
            warnings.append(ValidationError(
                requirement_id=getattr(requirement, 'id', 'unknown'),
                error_type='complex_structure',
                severity='low',
                message="Requirement contains multiple sentences",
                suggestion="Consider splitting into separate requirements"
            ))
        
        # 전문 용어 검증
        technical_terms = ['API', 'UI', 'UX', 'DB', 'SQL', 'HTTP', 'JSON', 'XML']
        undefined_terms = []
        
        for term in technical_terms:
            if term in description and f"{term} (" not in description:
                undefined_terms.append(term)
        
        if undefined_terms:
            warnings.append(ValidationError(
                requirement_id=getattr(requirement, 'id', 'unknown'),
                error_type='undefined_terms',
                severity='low',
                message=f"Technical terms may need definition: {', '.join(undefined_terms)}",
                suggestion="Consider defining technical terms for clarity"
            ))
        
        return warnings

    def _validate_measurability(self, requirement) -> List[ValidationError]:
        """측정 가능성 검증"""
        warnings = []
        
        if not hasattr(requirement, 'type') or not hasattr(requirement, 'description'):
            return warnings
        
        # 비기능 요구사항의 측정 가능성 검증
        if requirement.type == 'non_functional':
            description = requirement.description.lower()
            
            # 정량적 지표 확인
            has_numbers = bool(re.search(r'\d+', description))
            has_units = bool(re.search(r'\d+\s*(ms|seconds?|minutes?|%|users?)', description))
            
            if not has_numbers:
                warnings.append(ValidationError(
                    requirement_id=getattr(requirement, 'id', 'unknown'),
                    error_type='not_measurable',
                    severity='medium',
                    message="Non-functional requirement lacks quantitative metrics",
                    suggestion="Add specific numbers, percentages, or measurable criteria"
                ))
            elif not has_units:
                warnings.append(ValidationError(
                    requirement_id=getattr(requirement, 'id', 'unknown'),
                    error_type='missing_units',
                    severity='low',
                    message="Metrics found but units may be missing",
                    suggestion="Specify units for all quantitative measures"
                ))
        
        # 수용 기준 검증
        if hasattr(requirement, 'acceptance_criteria'):
            if not requirement.acceptance_criteria or len(requirement.acceptance_criteria) == 0:
                warnings.append(ValidationError(
                    requirement_id=getattr(requirement, 'id', 'unknown'),
                    error_type='missing_acceptance_criteria',
                    severity='medium',
                    message="Requirement lacks acceptance criteria",
                    suggestion="Add specific, testable acceptance criteria"
                ))
        
        return warnings

    def _calculate_quality_score(self, requirement, errors: List[ValidationError], warnings: List[ValidationError]) -> float:
        """품질 점수 계산"""
        base_score = 100.0
        
        # 에러에 따른 점수 차감
        for error in errors:
            if error.severity == 'critical':
                base_score -= 25
            elif error.severity == 'high':
                base_score -= 15
            elif error.severity == 'medium':
                base_score -= 10
            elif error.severity == 'low':
                base_score -= 5
        
        # 경고에 따른 점수 차감
        for warning in warnings:
            if warning.severity == 'medium':
                base_score -= 5
            elif warning.severity == 'low':
                base_score -= 2
        
        return max(0.0, min(100.0, base_score))

    def _calculate_completeness_score(self, requirement) -> float:
        """완성도 점수 계산"""
        score = 0.0
        total_fields = 8
        
        # 필수 필드 확인
        if hasattr(requirement, 'id') and requirement.id:
            score += 12.5
        if hasattr(requirement, 'description') and requirement.description:
            score += 25.0  # 가장 중요한 필드
        if hasattr(requirement, 'priority') and requirement.priority:
            score += 12.5
        if hasattr(requirement, 'type') and requirement.type:
            score += 12.5
        
        # 선택적 필드 확인
        if hasattr(requirement, 'acceptance_criteria') and requirement.acceptance_criteria:
            score += 12.5
        if hasattr(requirement, 'dependencies') and requirement.dependencies:
            score += 12.5
        if hasattr(requirement, 'technical_details') and requirement.technical_details:
            score += 12.5
        if hasattr(requirement, 'metadata') and requirement.metadata:
            score += 12.5
        
        return min(100.0, score)

    def _calculate_consistency_score(self, requirement) -> float:
        """일관성 점수 계산"""
        # 단일 요구사항의 내부 일관성 검증
        score = 100.0
        
        if not hasattr(requirement, 'description') or not hasattr(requirement, 'type'):
            return score
        
        description = requirement.description.lower()
        req_type = requirement.type
        
        # 타입과 내용의 일관성 검증
        if req_type == 'functional':
            functional_keywords = ['user', 'system', 'create', 'update', 'delete', 'manage']
            if not any(keyword in description for keyword in functional_keywords):
                score -= 20
        elif req_type == 'non_functional':
            nfr_keywords = ['performance', 'security', 'scalability', 'reliability', 'usability']
            if not any(keyword in description for keyword in nfr_keywords):
                score -= 20
        
        return max(0.0, score)

    def _generate_recommendations(self, requirement, errors: List[ValidationError], warnings: List[ValidationError]) -> List[str]:
        """추천사항 생성"""
        recommendations = []
        
        # 에러 기반 추천
        if any(e.error_type == 'missing_field' for e in errors):
            recommendations.append("Complete all required fields for the requirement")
        
        if any(e.error_type == 'ambiguous_language' for e in warnings):
            recommendations.append("Replace ambiguous terms with specific, measurable criteria")
        
        if any(e.error_type == 'not_measurable' for e in warnings):
            recommendations.append("Add quantitative metrics to make the requirement testable")
        
        if any(e.error_type == 'missing_acceptance_criteria' for e in warnings):
            recommendations.append("Define clear acceptance criteria using Given-When-Then format")
        
        # 품질 개선 추천
        if hasattr(requirement, 'description') and requirement.description:
            if len(requirement.description) < 20:
                recommendations.append("Expand the requirement description with more details")
        
        return recommendations

    def _calculate_overall_quality(self, validation_results: List[ValidationResult], 
                                 consistency_result, completeness_result) -> float:
        """전체 품질 점수 계산"""
        if not validation_results:
            return 0.0
        
        # 개별 요구사항 품질 점수 평균
        avg_quality = sum(r.quality_score for r in validation_results) / len(validation_results)
        
        # 가중 평균 계산
        overall_score = (
            avg_quality * 0.5 +
            consistency_result.score * 0.3 +
            completeness_result.score * 0.2
        )
        
        return round(overall_score, 2)

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """검증 규칙 초기화"""
        return {
            'required_fields': ['id', 'type', 'description', 'priority'],
            'valid_priorities': ['critical', 'high', 'medium', 'low'],
            'valid_types': ['functional', 'non_functional', 'technical', 'business'],
            'min_description_length': 10,
            'max_description_length': 500,
            'ambiguous_words': ['some', 'many', 'few', 'several', 'appropriate', 'reasonable']
        }

    def _initialize_quality_metrics(self) -> Dict[str, float]:
        """품질 메트릭 초기화"""
        return {
            'completeness_weight': 0.3,
            'clarity_weight': 0.25,
            'consistency_weight': 0.25,
            'measurability_weight': 0.2
        }

class ConsistencyChecker:
    """일관성 검증기"""
    
    async def check_consistency(self, requirements: List) -> 'ConsistencyResult':
        """요구사항 간 일관성 검증"""
        
        conflicts = []
        duplicates = []
        
        # 중복 검증
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements[i+1:], i+1):
                similarity = self._calculate_similarity(req1.description, req2.description)
                if similarity > 0.8:
                    duplicates.append((req1.id, req2.id, similarity))
        
        # 충돌 검증
        conflicts = self._detect_conflicts(requirements)
        
        # 일관성 점수 계산
        score = self._calculate_consistency_score(requirements, conflicts, duplicates)
        
        return type('ConsistencyResult', (), {
            'score': score,
            'conflicts': conflicts,
            'duplicates': duplicates
        })()
    
    def _calculate_similarity(self, desc1: str, desc2: str) -> float:
        """텍스트 유사도 계산"""
        words1 = set(desc1.lower().split())
        words2 = set(desc2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _detect_conflicts(self, requirements: List) -> List[Dict[str, Any]]:
        """충돌 감지"""
        conflicts = []
        
        # 간단한 충돌 패턴 검사
        for req in requirements:
            if hasattr(req, 'description'):
                desc = req.description.lower()
                if 'must not' in desc and 'must' in desc:
                    conflicts.append({
                        'requirement_id': req.id,
                        'type': 'contradictory_statements',
                        'description': 'Contains both positive and negative requirements'
                    })
        
        return conflicts
    
    def _calculate_consistency_score(self, requirements: List, conflicts: List, duplicates: List) -> float:
        """일관성 점수 계산"""
        base_score = 100.0
        
        # 충돌에 따른 점수 차감
        base_score -= len(conflicts) * 15
        
        # 중복에 따른 점수 차감
        base_score -= len(duplicates) * 10
        
        return max(0.0, base_score)

class CompletenessChecker:
    """완성도 검증기"""
    
    async def check_completeness(self, parsed_project) -> 'CompletenessResult':
        """프로젝트 완성도 검증"""
        
        missing_elements = []
        
        # 필수 요소 확인
        if not parsed_project.functional_requirements:
            missing_elements.append('functional_requirements')
        
        if not parsed_project.project_info:
            missing_elements.append('project_info')
        
        # 권장 요소 확인
        recommended_missing = []
        if not parsed_project.non_functional_requirements:
            recommended_missing.append('non_functional_requirements')
        
        if not parsed_project.user_stories:
            recommended_missing.append('user_stories')
        
        # 완성도 점수 계산
        score = self._calculate_completeness_score(parsed_project, missing_elements, recommended_missing)
        
        return type('CompletenessResult', (), {
            'score': score,
            'missing_elements': missing_elements,
            'recommended_missing': recommended_missing
        })()
    
    def _calculate_completeness_score(self, parsed_project, missing_elements: List, recommended_missing: List) -> float:
        """완성도 점수 계산"""
        base_score = 100.0
        
        # 필수 요소 누락에 따른 점수 차감
        base_score -= len(missing_elements) * 25
        
        # 권장 요소 누락에 따른 점수 차감
        base_score -= len(recommended_missing) * 10
        
        return max(0.0, base_score)