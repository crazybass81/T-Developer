# backend/src/agents/implementations/component_decision_validator.py
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    severity: ValidationSeverity
    message: str
    component_id: Optional[str] = None
    suggestion: Optional[str] = None

class ComponentDecisionValidator:
    """컴포넌트 결정 검증기"""

    def __init__(self):
        self.validators = [
            self._validate_decision_consistency,
            self._validate_requirement_coverage,
            self._validate_risk_assessment,
            self._validate_compatibility_conflicts,
            self._validate_license_compliance,
            self._validate_performance_requirements,
            self._validate_security_requirements
        ]

    async def validate_decisions(
        self,
        decisions: List[Any],  # ComponentDecision objects
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """결정 검증"""

        validation_results = []

        # 각 검증기 실행
        for validator in self.validators:
            try:
                results = await validator(decisions, requirements, context)
                validation_results.extend(results)
            except Exception as e:
                validation_results.append(ValidationResult(
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation error in {validator.__name__}: {str(e)}"
                ))

        return validation_results

    async def _validate_decision_consistency(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """결정 일관성 검증"""

        results = []

        # 선택된 컴포넌트가 있는지 확인
        selected = [d for d in decisions if d.decision == 'selected']
        conditional = [d for d in decisions if d.decision == 'conditional']

        if not selected and not conditional:
            results.append(ValidationResult(
                severity=ValidationSeverity.ERROR,
                message="No components selected or conditionally accepted",
                suggestion="Review selection criteria or consider additional components"
            ))

        # 점수와 결정의 일관성 확인
        for decision in decisions:
            if decision.decision == 'selected' and decision.score < 0.6:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"Component {decision.component_name} selected with low score ({decision.score:.2f})",
                    component_id=decision.component_id,
                    suggestion="Review selection criteria or component evaluation"
                ))

            elif decision.decision == 'rejected' and decision.score > 0.7:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"Component {decision.component_name} rejected despite high score ({decision.score:.2f})",
                    component_id=decision.component_id,
                    suggestion="Review rejection reasons"
                ))

        return results

    async def _validate_requirement_coverage(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """요구사항 커버리지 검증"""

        results = []

        # 선택된 컴포넌트들의 기능 수집
        selected_components = [d for d in decisions if d.decision in ['selected', 'conditional']]
        
        if not selected_components:
            return results

        # 기능 요구사항 커버리지 확인
        required_features = set(requirements.get('functional_requirements', []))
        covered_features = set()

        for decision in selected_components:
            # 실제 구현에서는 컴포넌트 메타데이터에서 기능 추출
            component_features = self._extract_component_features(decision)
            covered_features.update(component_features)

        uncovered_features = required_features - covered_features

        if uncovered_features:
            results.append(ValidationResult(
                severity=ValidationSeverity.WARNING,
                message=f"Uncovered functional requirements: {', '.join(uncovered_features)}",
                suggestion="Consider additional components or custom implementation"
            ))

        # 성능 요구사항 확인
        perf_requirements = requirements.get('performance_requirements', {})
        if perf_requirements:
            coverage = self._check_performance_coverage(selected_components, perf_requirements)
            if coverage < 0.8:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"Performance requirements coverage: {coverage:.1%}",
                    suggestion="Review performance characteristics of selected components"
                ))

        return results

    async def _validate_risk_assessment(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """리스크 평가 검증"""

        results = []

        # 고위험 컴포넌트 선택 확인
        for decision in decisions:
            if decision.decision == 'selected' and len(decision.risks) > 2:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"High-risk component selected: {decision.component_name}",
                    component_id=decision.component_id,
                    suggestion=f"Address risks: {', '.join(decision.risks[:2])}"
                ))

        # 전체 리스크 수준 평가
        total_risks = sum(len(d.risks) for d in decisions if d.decision in ['selected', 'conditional'])
        selected_count = len([d for d in decisions if d.decision in ['selected', 'conditional']])

        if selected_count > 0:
            avg_risk = total_risks / selected_count
            if avg_risk > 2:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"High average risk level: {avg_risk:.1f} risks per component",
                    suggestion="Consider risk mitigation strategies"
                ))

        return results

    async def _validate_compatibility_conflicts(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """호환성 충돌 검증"""

        results = []

        selected_components = [d for d in decisions if d.decision == 'selected']

        # 기술 스택 충돌 확인
        tech_stacks = []
        for decision in selected_components:
            component_tech = self._extract_component_technologies(decision)
            tech_stacks.append((decision.component_name, component_tech))

        conflicts = self._detect_technology_conflicts(tech_stacks)
        for conflict in conflicts:
            results.append(ValidationResult(
                severity=ValidationSeverity.ERROR,
                message=f"Technology conflict: {conflict['description']}",
                suggestion=f"Choose between {' and '.join(conflict['components'])}"
            ))

        # 라이선스 충돌 확인
        license_conflicts = self._detect_license_conflicts(selected_components)
        for conflict in license_conflicts:
            results.append(ValidationResult(
                severity=ValidationSeverity.ERROR,
                message=f"License conflict: {conflict['description']}",
                suggestion="Review license compatibility"
            ))

        return results

    async def _validate_license_compliance(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """라이선스 컴플라이언스 검증"""

        results = []

        project_license = context.get('project_license') if context else None
        commercial_use = context.get('commercial_use', False) if context else False

        for decision in decisions:
            if decision.decision in ['selected', 'conditional']:
                component_license = self._extract_component_license(decision)
                
                # 상업적 사용 제한 확인
                if commercial_use and not self._allows_commercial_use(component_license):
                    results.append(ValidationResult(
                        severity=ValidationSeverity.ERROR,
                        message=f"Component {decision.component_name} license prohibits commercial use",
                        component_id=decision.component_id,
                        suggestion="Find alternative with commercial-friendly license"
                    ))

                # 카피레프트 라이선스 경고
                if self._is_copyleft_license(component_license):
                    results.append(ValidationResult(
                        severity=ValidationSeverity.WARNING,
                        message=f"Component {decision.component_name} uses copyleft license ({component_license})",
                        component_id=decision.component_id,
                        suggestion="Ensure compliance with copyleft requirements"
                    ))

        return results

    async def _validate_performance_requirements(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """성능 요구사항 검증"""

        results = []

        perf_requirements = requirements.get('performance_requirements', {})
        if not perf_requirements:
            return results

        selected_components = [d for d in decisions if d.decision == 'selected']

        # 응답 시간 요구사항
        if 'response_time' in perf_requirements:
            required_response_time = perf_requirements['response_time']
            
            for decision in selected_components:
                component_perf = self._extract_component_performance(decision)
                if component_perf.get('response_time', 0) > required_response_time:
                    results.append(ValidationResult(
                        severity=ValidationSeverity.WARNING,
                        message=f"Component {decision.component_name} may not meet response time requirement",
                        component_id=decision.component_id,
                        suggestion="Performance testing recommended"
                    ))

        # 동시 사용자 요구사항
        if 'concurrent_users' in perf_requirements:
            required_users = perf_requirements['concurrent_users']
            
            total_capacity = sum(
                self._extract_component_performance(d).get('max_users', 0)
                for d in selected_components
            )
            
            if total_capacity < required_users:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"Selected components may not support {required_users} concurrent users",
                    suggestion="Consider scalability improvements or additional components"
                ))

        return results

    async def _validate_security_requirements(
        self,
        decisions: List[Any],
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """보안 요구사항 검증"""

        results = []

        security_requirements = requirements.get('security_requirements', [])
        if not security_requirements:
            return results

        selected_components = [d for d in decisions if d.decision == 'selected']

        # 보안 기능 커버리지 확인
        required_security_features = set(security_requirements)
        provided_security_features = set()

        for decision in selected_components:
            component_security = self._extract_component_security_features(decision)
            provided_security_features.update(component_security)

        missing_security = required_security_features - provided_security_features

        if missing_security:
            results.append(ValidationResult(
                severity=ValidationSeverity.ERROR,
                message=f"Missing security features: {', '.join(missing_security)}",
                suggestion="Add components with required security features"
            ))

        # 보안 취약점 확인
        for decision in selected_components:
            vulnerabilities = self._check_component_vulnerabilities(decision)
            if vulnerabilities:
                results.append(ValidationResult(
                    severity=ValidationSeverity.WARNING,
                    message=f"Component {decision.component_name} has known vulnerabilities",
                    component_id=decision.component_id,
                    suggestion="Update to latest version or find alternative"
                ))

        return results

    # Helper methods
    def _extract_component_features(self, decision: Any) -> List[str]:
        """컴포넌트 기능 추출"""
        # 실제 구현에서는 컴포넌트 메타데이터에서 추출
        return []

    def _check_performance_coverage(
        self,
        components: List[Any],
        requirements: Dict[str, Any]
    ) -> float:
        """성능 커버리지 확인"""
        # 간단한 구현
        return 0.8

    def _extract_component_technologies(self, decision: Any) -> List[str]:
        """컴포넌트 기술 스택 추출"""
        return []

    def _detect_technology_conflicts(
        self,
        tech_stacks: List[Tuple[str, List[str]]]
    ) -> List[Dict[str, Any]]:
        """기술 충돌 감지"""
        conflicts = []
        
        # 간단한 충돌 감지 로직
        conflicting_pairs = [
            ('React', 'Vue'),
            ('Angular', 'React'),
            ('MySQL', 'PostgreSQL')
        ]
        
        for comp1_name, tech1 in tech_stacks:
            for comp2_name, tech2 in tech_stacks:
                if comp1_name != comp2_name:
                    for t1 in tech1:
                        for t2 in tech2:
                            if (t1, t2) in conflicting_pairs or (t2, t1) in conflicting_pairs:
                                conflicts.append({
                                    'description': f"{t1} and {t2} conflict",
                                    'components': [comp1_name, comp2_name]
                                })
        
        return conflicts

    def _detect_license_conflicts(self, components: List[Any]) -> List[Dict[str, Any]]:
        """라이선스 충돌 감지"""
        return []

    def _extract_component_license(self, decision: Any) -> str:
        """컴포넌트 라이선스 추출"""
        return "MIT"  # 기본값

    def _allows_commercial_use(self, license: str) -> bool:
        """상업적 사용 허용 여부"""
        commercial_licenses = ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC']
        return license in commercial_licenses

    def _is_copyleft_license(self, license: str) -> bool:
        """카피레프트 라이선스 여부"""
        copyleft_licenses = ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0', 'LGPL-2.1', 'LGPL-3.0']
        return license in copyleft_licenses

    def _extract_component_performance(self, decision: Any) -> Dict[str, Any]:
        """컴포넌트 성능 정보 추출"""
        return {}

    def _extract_component_security_features(self, decision: Any) -> List[str]:
        """컴포넌트 보안 기능 추출"""
        return []

    def _check_component_vulnerabilities(self, decision: Any) -> List[str]:
        """컴포넌트 취약점 확인"""
        return []