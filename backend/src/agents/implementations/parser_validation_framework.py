# backend/src/agents/implementations/parser_validation_framework.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import asyncio

class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    level: ValidationLevel
    message: str
    field: str
    suggestion: Optional[str] = None

class ParserValidationFramework:
    """Parser Agent 검증 프레임워크"""

    def __init__(self):
        self.validators = self._initialize_validators()
        self.quality_metrics = QualityMetrics()

    def _initialize_validators(self) -> Dict[str, Any]:
        """검증기 초기화"""
        return {
            'completeness': CompletenessValidator(),
            'consistency': ConsistencyValidator(),
            'quality': QualityValidator(),
            'traceability': TraceabilityValidator(),
            'coverage': CoverageValidator()
        }

    async def validate_parsing_result(
        self,
        parsing_result,
        original_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """파싱 결과 종합 검증"""
        
        validation_results = {}
        
        # 각 검증기 실행
        for validator_name, validator in self.validators.items():
            try:
                result = await validator.validate(
                    parsing_result,
                    original_input,
                    context
                )
                validation_results[validator_name] = result
            except Exception as e:
                validation_results[validator_name] = {
                    'status': 'error',
                    'message': f"Validation failed: {str(e)}"
                }
        
        # 전체 품질 점수 계산
        quality_score = self.quality_metrics.calculate_overall_score(
            validation_results
        )
        
        # 검증 요약
        summary = self._generate_validation_summary(
            validation_results,
            quality_score
        )
        
        return {
            'validation_results': validation_results,
            'quality_score': quality_score,
            'summary': summary,
            'recommendations': self._generate_recommendations(validation_results)
        }

    def _generate_validation_summary(
        self,
        validation_results: Dict[str, Any],
        quality_score: float
    ) -> Dict[str, Any]:
        """검증 요약 생성"""
        
        total_errors = 0
        total_warnings = 0
        
        for validator_name, result in validation_results.items():
            if isinstance(result, dict) and 'issues' in result:
                for issue in result['issues']:
                    if issue.level == ValidationLevel.ERROR:
                        total_errors += 1
                    elif issue.level == ValidationLevel.WARNING:
                        total_warnings += 1
        
        # 전체 상태 결정
        if total_errors > 0:
            overall_status = 'FAILED'
        elif total_warnings > 5:
            overall_status = 'WARNING'
        else:
            overall_status = 'PASSED'
        
        return {
            'overall_status': overall_status,
            'quality_score': quality_score,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'validation_passed': total_errors == 0
        }

    def _generate_recommendations(
        self,
        validation_results: Dict[str, Any]
    ) -> List[str]:
        """개선 권장사항 생성"""
        
        recommendations = []
        
        for validator_name, result in validation_results.items():
            if isinstance(result, dict) and 'issues' in result:
                for issue in result['issues']:
                    if issue.suggestion:
                        recommendations.append(
                            f"{validator_name.title()}: {issue.suggestion}"
                        )
        
        return recommendations[:10]  # 상위 10개만 반환


class CompletenessValidator:
    """완성도 검증기"""

    async def validate(
        self,
        parsing_result,
        original_input: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """완성도 검증"""
        
        issues = []
        
        # 필수 필드 검증
        if not parsing_result.functional_requirements:
            issues.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="No functional requirements found",
                field="functional_requirements",
                suggestion="Review input for functional requirements"
            ))
        
        # 요구사항 ID 검증
        for req in parsing_result.functional_requirements:
            if not req.id:
                issues.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="Requirement missing ID",
                    field="requirement.id",
                    suggestion="Ensure all requirements have unique IDs"
                ))
        
        # 설명 완성도 검증
        for req in parsing_result.functional_requirements:
            if not req.description or len(req.description.strip()) < 10:
                issues.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="Requirement description too short",
                    field="requirement.description",
                    suggestion="Provide more detailed descriptions"
                ))
        
        # 우선순위 설정 검증
        missing_priority = [
            req for req in parsing_result.functional_requirements
            if not req.priority
        ]
        
        if missing_priority:
            issues.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"{len(missing_priority)} requirements missing priority",
                field="requirement.priority",
                suggestion="Set priority for all requirements"
            ))
        
        return {
            'status': 'completed',
            'issues': issues,
            'completeness_score': self._calculate_completeness_score(
                parsing_result,
                issues
            )
        }

    def _calculate_completeness_score(
        self,
        parsing_result,
        issues: List[ValidationResult]
    ) -> float:
        """완성도 점수 계산"""
        
        total_requirements = len(parsing_result.functional_requirements)
        if total_requirements == 0:
            return 0.0
        
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        # 점수 계산 (에러는 -0.2, 경고는 -0.1)
        penalty = (error_count * 0.2) + (warning_count * 0.1)
        score = max(0.0, 1.0 - penalty)
        
        return score


class ConsistencyValidator:
    """일관성 검증기"""

    async def validate(
        self,
        parsing_result,
        original_input: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """일관성 검증"""
        
        issues = []
        
        # ID 중복 검증
        all_ids = [req.id for req in parsing_result.functional_requirements if req.id]
        duplicate_ids = [id for id in set(all_ids) if all_ids.count(id) > 1]
        
        if duplicate_ids:
            issues.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Duplicate requirement IDs: {duplicate_ids}",
                field="requirement.id",
                suggestion="Ensure all requirement IDs are unique"
            ))
        
        # 우선순위 일관성 검증
        priority_values = [
            req.priority for req in parsing_result.functional_requirements
            if req.priority
        ]
        
        valid_priorities = {'critical', 'high', 'medium', 'low'}
        invalid_priorities = [p for p in priority_values if p not in valid_priorities]
        
        if invalid_priorities:
            issues.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Invalid priority values: {set(invalid_priorities)}",
                field="requirement.priority",
                suggestion="Use standard priority values: critical, high, medium, low"
            ))
        
        # 카테고리 일관성 검증
        categories = [
            req.category for req in parsing_result.functional_requirements
            if hasattr(req, 'category') and req.category
        ]
        
        # 카테고리 명명 일관성 확인
        inconsistent_categories = self._find_inconsistent_categories(categories)
        
        if inconsistent_categories:
            issues.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Inconsistent category naming: {inconsistent_categories}",
                field="requirement.category",
                suggestion="Use consistent category naming conventions"
            ))
        
        return {
            'status': 'completed',
            'issues': issues,
            'consistency_score': self._calculate_consistency_score(issues)
        }

    def _find_inconsistent_categories(self, categories: List[str]) -> List[str]:
        """일관성 없는 카테고리 찾기"""
        
        # 유사한 카테고리 그룹화
        category_groups = {}
        
        for category in set(categories):
            normalized = category.lower().replace('_', '').replace('-', '')
            
            # 기존 그룹과 유사한지 확인
            found_group = False
            for group_key in category_groups:
                if self._are_similar_categories(normalized, group_key):
                    category_groups[group_key].append(category)
                    found_group = True
                    break
            
            if not found_group:
                category_groups[normalized] = [category]
        
        # 여러 변형이 있는 그룹 찾기
        inconsistent = []
        for group_categories in category_groups.values():
            if len(group_categories) > 1:
                inconsistent.extend(group_categories)
        
        return inconsistent

    def _are_similar_categories(self, cat1: str, cat2: str) -> bool:
        """카테고리 유사성 확인"""
        
        # 편집 거리 기반 유사성
        if len(cat1) == 0 or len(cat2) == 0:
            return False
        
        # 간단한 유사성 검사
        longer = max(cat1, cat2, key=len)
        shorter = min(cat1, cat2, key=len)
        
        if shorter in longer:
            return True
        
        # 공통 접두사/접미사 확인
        if len(shorter) >= 3:
            if (longer.startswith(shorter[:3]) or 
                longer.endswith(shorter[-3:]) or
                shorter.startswith(longer[:3]) or
                shorter.endswith(longer[-3:])):
                return True
        
        return False

    def _calculate_consistency_score(self, issues: List[ValidationResult]) -> float:
        """일관성 점수 계산"""
        
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        penalty = (error_count * 0.3) + (warning_count * 0.1)
        score = max(0.0, 1.0 - penalty)
        
        return score


class QualityValidator:
    """품질 검증기"""

    async def validate(
        self,
        parsing_result,
        original_input: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """품질 검증"""
        
        issues = []
        
        # 요구사항 명확성 검증
        for req in parsing_result.functional_requirements:
            clarity_score = self._assess_clarity(req.description)
            
            if clarity_score < 0.5:
                issues.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Requirement '{req.id}' lacks clarity",
                    field="requirement.description",
                    suggestion="Make requirement description more specific and clear"
                ))
        
        # 수용 기준 품질 검증
        for req in parsing_result.functional_requirements:
            if not req.acceptance_criteria or len(req.acceptance_criteria) == 0:
                issues.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Requirement '{req.id}' missing acceptance criteria",
                    field="requirement.acceptance_criteria",
                    suggestion="Add specific acceptance criteria"
                ))
        
        # 사용자 스토리 품질 검증
        for story in parsing_result.user_stories:
            if not self._is_valid_user_story_format(story.get('description', '')):
                issues.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="User story doesn't follow standard format",
                    field="user_story.description",
                    suggestion="Use 'As a [user], I want [goal] so that [benefit]' format"
                ))
        
        return {
            'status': 'completed',
            'issues': issues,
            'quality_score': self._calculate_quality_score(parsing_result, issues)
        }

    def _assess_clarity(self, description: str) -> float:
        """설명 명확성 평가"""
        
        if not description:
            return 0.0
        
        clarity_indicators = {
            'specific_verbs': ['create', 'update', 'delete', 'display', 'calculate'],
            'measurable_terms': ['number', 'count', 'percentage', 'time', 'size'],
            'clear_subjects': ['user', 'system', 'application', 'admin', 'customer']
        }
        
        score = 0.0
        description_lower = description.lower()
        
        # 구체적 동사 확인
        verb_count = sum(1 for verb in clarity_indicators['specific_verbs'] 
                        if verb in description_lower)
        score += min(verb_count * 0.2, 0.4)
        
        # 측정 가능한 용어 확인
        measurable_count = sum(1 for term in clarity_indicators['measurable_terms']
                              if term in description_lower)
        score += min(measurable_count * 0.1, 0.3)
        
        # 명확한 주체 확인
        subject_count = sum(1 for subject in clarity_indicators['clear_subjects']
                           if subject in description_lower)
        score += min(subject_count * 0.1, 0.3)
        
        return min(score, 1.0)

    def _is_valid_user_story_format(self, description: str) -> bool:
        """사용자 스토리 형식 검증"""
        
        # "As a ... I want ... so that ..." 패턴 확인
        pattern = r'as\s+a\s+.+\s+i\s+want\s+.+\s+so\s+that\s+.+'
        return bool(re.search(pattern, description.lower()))

    def _calculate_quality_score(
        self,
        parsing_result,
        issues: List[ValidationResult]
    ) -> float:
        """품질 점수 계산"""
        
        base_score = 1.0
        
        # 이슈 기반 감점
        error_penalty = len([i for i in issues if i.level == ValidationLevel.ERROR]) * 0.2
        warning_penalty = len([i for i in issues if i.level == ValidationLevel.WARNING]) * 0.05
        
        # 완성도 보너스
        completeness_bonus = 0.0
        if parsing_result.functional_requirements:
            complete_reqs = sum(1 for req in parsing_result.functional_requirements
                              if req.description and req.acceptance_criteria)
            completeness_bonus = (complete_reqs / len(parsing_result.functional_requirements)) * 0.2
        
        final_score = base_score - error_penalty - warning_penalty + completeness_bonus
        return max(0.0, min(1.0, final_score))


class QualityMetrics:
    """품질 메트릭 계산기"""

    def calculate_overall_score(
        self,
        validation_results: Dict[str, Any]
    ) -> float:
        """전체 품질 점수 계산"""
        
        scores = []
        weights = {
            'completeness': 0.3,
            'consistency': 0.25,
            'quality': 0.25,
            'traceability': 0.1,
            'coverage': 0.1
        }
        
        for validator_name, result in validation_results.items():
            if isinstance(result, dict) and 'status' in result:
                if result['status'] == 'completed':
                    # 각 검증기의 점수 추출
                    score_key = f"{validator_name}_score"
                    if score_key in result:
                        weight = weights.get(validator_name, 0.1)
                        scores.append(result[score_key] * weight)
        
        return sum(scores) if scores else 0.0


# 검증 실행 스크립트
async def validate_parser_result(parsing_result, original_input: str):
    """파서 결과 검증 실행"""
    
    validator = ParserValidationFramework()
    
    validation_result = await validator.validate_parsing_result(
        parsing_result,
        original_input
    )
    
    print("=== Parser Validation Results ===")
    print(f"Overall Status: {validation_result['summary']['overall_status']}")
    print(f"Quality Score: {validation_result['quality_score']:.2f}")
    print(f"Errors: {validation_result['summary']['total_errors']}")
    print(f"Warnings: {validation_result['summary']['total_warnings']}")
    
    if validation_result['recommendations']:
        print("\nRecommendations:")
        for rec in validation_result['recommendations']:
            print(f"- {rec}")
    
    return validation_result