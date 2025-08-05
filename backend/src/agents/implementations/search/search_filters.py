# backend/src/agents/implementations/search_filters.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta

class FilterType(Enum):
    LICENSE = "license"
    LANGUAGE = "language"
    POPULARITY = "popularity"
    FRESHNESS = "freshness"
    QUALITY = "quality"
    SECURITY = "security"

@dataclass
class SearchFilter:
    type: FilterType
    criteria: Dict[str, Any]
    weight: float = 1.0

class SearchFilterEngine:
    """검색 필터 엔진"""

    def __init__(self):
        self.filters = {}
        self.filter_processors = {
            FilterType.LICENSE: self._process_license_filter,
            FilterType.LANGUAGE: self._process_language_filter,
            FilterType.POPULARITY: self._process_popularity_filter,
            FilterType.FRESHNESS: self._process_freshness_filter,
            FilterType.QUALITY: self._process_quality_filter,
            FilterType.SECURITY: self._process_security_filter
        }

    def add_filter(self, filter_config: SearchFilter):
        """필터 추가"""
        self.filters[filter_config.type] = filter_config

    async def apply_filters(
        self,
        results: List[Any],  # SearchResult objects
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """필터 적용"""

        filtered_results = results.copy()

        # 각 필터 적용
        for filter_type, filter_config in self.filters.items():
            processor = self.filter_processors.get(filter_type)
            if processor:
                filtered_results = await processor(
                    filtered_results,
                    filter_config,
                    requirements
                )

        return filtered_results

    async def _process_license_filter(
        self,
        results: List[Any],
        filter_config: SearchFilter,
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """라이선스 필터 처리"""

        allowed_licenses = filter_config.criteria.get('allowed', [])
        blocked_licenses = filter_config.criteria.get('blocked', [])
        commercial_use = filter_config.criteria.get('commercial_use', False)

        filtered = []

        for result in results:
            license_info = result.metadata.get('license', '').lower()
            
            # 허용된 라이선스 확인
            if allowed_licenses:
                if not any(lic.lower() in license_info for lic in allowed_licenses):
                    continue

            # 차단된 라이선스 확인
            if blocked_licenses:
                if any(lic.lower() in license_info for lic in blocked_licenses):
                    continue

            # 상업적 사용 확인
            if commercial_use and not self._allows_commercial_use(license_info):
                continue

            filtered.append(result)

        return filtered

    async def _process_language_filter(
        self,
        results: List[Any],
        filter_config: SearchFilter,
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """언어 필터 처리"""

        preferred_languages = filter_config.criteria.get('preferred', [])
        excluded_languages = filter_config.criteria.get('excluded', [])

        if not preferred_languages and not excluded_languages:
            return results

        filtered = []

        for result in results:
            language = result.metadata.get('language', '').lower()
            
            # 선호 언어 확인
            if preferred_languages:
                if not any(lang.lower() in language for lang in preferred_languages):
                    continue

            # 제외 언어 확인
            if excluded_languages:
                if any(lang.lower() in language for lang in excluded_languages):
                    continue

            filtered.append(result)

        return filtered

    async def _process_popularity_filter(
        self,
        results: List[Any],
        filter_config: SearchFilter,
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """인기도 필터 처리"""

        min_stars = filter_config.criteria.get('min_stars', 0)
        min_downloads = filter_config.criteria.get('min_downloads', 0)
        min_forks = filter_config.criteria.get('min_forks', 0)

        filtered = []

        for result in results:
            metadata = result.metadata
            
            # GitHub 스타 확인
            stars = metadata.get('stars', 0)
            if stars < min_stars:
                continue

            # 다운로드 수 확인
            downloads = metadata.get('downloads', 0)
            if downloads < min_downloads:
                continue

            # 포크 수 확인
            forks = metadata.get('forks', 0)
            if forks < min_forks:
                continue

            filtered.append(result)

        return filtered

    async def _process_freshness_filter(
        self,
        results: List[Any],
        filter_config: SearchFilter,
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """최신성 필터 처리"""

        max_age_days = filter_config.criteria.get('max_age_days', 365)
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        filtered = []

        for result in results:
            updated_at = result.metadata.get('updated_at')
            
            if not updated_at:
                # 업데이트 날짜가 없으면 통과
                filtered.append(result)
                continue

            try:
                # ISO 형식 날짜 파싱
                update_date = datetime.fromisoformat(
                    updated_at.replace('Z', '+00:00')
                )
                
                if update_date >= cutoff_date:
                    filtered.append(result)
                    
            except:
                # 날짜 파싱 실패 시 통과
                filtered.append(result)

        return filtered

    async def _process_quality_filter(
        self,
        results: List[Any],
        filter_config: SearchFilter,
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """품질 필터 처리"""

        min_quality_score = filter_config.criteria.get('min_score', 0.5)
        require_documentation = filter_config.criteria.get('require_docs', False)
        require_tests = filter_config.criteria.get('require_tests', False)

        filtered = []

        for result in results:
            # 품질 점수 계산
            quality_score = self._calculate_quality_score(result)
            
            if quality_score < min_quality_score:
                continue

            # 문서화 요구사항
            if require_documentation and not self._has_documentation(result):
                continue

            # 테스트 요구사항
            if require_tests and not self._has_tests(result):
                continue

            filtered.append(result)

        return filtered

    async def _process_security_filter(
        self,
        results: List[Any],
        filter_config: SearchFilter,
        requirements: Dict[str, Any]
    ) -> List[Any]:
        """보안 필터 처리"""

        max_vulnerabilities = filter_config.criteria.get('max_vulnerabilities', 0)
        require_security_audit = filter_config.criteria.get('require_audit', False)

        filtered = []

        for result in results:
            # 취약점 수 확인
            vulnerabilities = result.metadata.get('vulnerabilities', 0)
            if vulnerabilities > max_vulnerabilities:
                continue

            # 보안 감사 요구사항
            if require_security_audit and not self._has_security_audit(result):
                continue

            filtered.append(result)

        return filtered

    def _allows_commercial_use(self, license_info: str) -> bool:
        """상업적 사용 허용 여부"""
        commercial_licenses = [
            'mit', 'apache', 'bsd', 'isc', 'unlicense'
        ]
        return any(lic in license_info for lic in commercial_licenses)

    def _calculate_quality_score(self, result: Any) -> float:
        """품질 점수 계산"""
        score = 0.0
        metadata = result.metadata

        # 라이선스 존재
        if metadata.get('license'):
            score += 0.2

        # 설명 존재
        if result.description and len(result.description) > 20:
            score += 0.2

        # 인기도
        stars = metadata.get('stars', 0)
        if stars > 100:
            score += 0.3
        elif stars > 10:
            score += 0.1

        # 최근 업데이트
        if metadata.get('updated_at'):
            score += 0.2

        # 공식 패키지
        if metadata.get('is_official'):
            score += 0.1

        return min(score, 1.0)

    def _has_documentation(self, result: Any) -> bool:
        """문서화 존재 여부"""
        # 간단한 휴리스틱
        description = result.description.lower()
        return len(description) > 50 or 'readme' in result.metadata

    def _has_tests(self, result: Any) -> bool:
        """테스트 존재 여부"""
        # 간단한 휴리스틱
        return 'test' in result.metadata or result.metadata.get('has_tests', False)

    def _has_security_audit(self, result: Any) -> bool:
        """보안 감사 존재 여부"""
        return result.metadata.get('security_audit', False)


class SmartFilterRecommender:
    """스마트 필터 추천기"""

    def __init__(self):
        self.filter_templates = {
            'enterprise': {
                FilterType.LICENSE: {
                    'allowed': ['MIT', 'Apache-2.0', 'BSD-3-Clause'],
                    'commercial_use': True
                },
                FilterType.SECURITY: {
                    'max_vulnerabilities': 0,
                    'require_audit': True
                },
                FilterType.QUALITY: {
                    'min_score': 0.8,
                    'require_docs': True,
                    'require_tests': True
                }
            },
            'startup': {
                FilterType.LICENSE: {
                    'allowed': ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC'],
                    'commercial_use': True
                },
                FilterType.POPULARITY: {
                    'min_stars': 50
                },
                FilterType.FRESHNESS: {
                    'max_age_days': 730  # 2년
                }
            },
            'open_source': {
                FilterType.LICENSE: {
                    'blocked': ['Proprietary', 'Commercial']
                },
                FilterType.QUALITY: {
                    'min_score': 0.6,
                    'require_docs': True
                }
            }
        }

    def recommend_filters(
        self,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[SearchFilter]:
        """필터 추천"""

        filters = []
        
        # 프로젝트 타입에 따른 템플릿 선택
        project_type = context.get('project_type', 'general') if context else 'general'
        
        if project_type in self.filter_templates:
            template = self.filter_templates[project_type]
            
            for filter_type, criteria in template.items():
                filter_config = SearchFilter(
                    type=filter_type,
                    criteria=criteria,
                    weight=1.0
                )
                filters.append(filter_config)

        # 요구사항 기반 추가 필터
        additional_filters = self._generate_requirement_filters(requirements)
        filters.extend(additional_filters)

        return filters

    def _generate_requirement_filters(
        self,
        requirements: Dict[str, Any]
    ) -> List[SearchFilter]:
        """요구사항 기반 필터 생성"""

        filters = []

        # 기술 스택 필터
        tech_stack = requirements.get('technology_stack', [])
        if tech_stack:
            language_filter = SearchFilter(
                type=FilterType.LANGUAGE,
                criteria={'preferred': tech_stack}
            )
            filters.append(language_filter)

        # 라이선스 요구사항
        license_requirements = requirements.get('license_requirements', {})
        if license_requirements:
            license_filter = SearchFilter(
                type=FilterType.LICENSE,
                criteria=license_requirements
            )
            filters.append(license_filter)

        # 보안 요구사항
        if requirements.get('security_critical', False):
            security_filter = SearchFilter(
                type=FilterType.SECURITY,
                criteria={
                    'max_vulnerabilities': 0,
                    'require_audit': True
                }
            )
            filters.append(security_filter)

        # 성능 요구사항
        performance_reqs = requirements.get('performance_requirements', {})
        if performance_reqs.get('high_performance', False):
            quality_filter = SearchFilter(
                type=FilterType.QUALITY,
                criteria={
                    'min_score': 0.8,
                    'require_tests': True
                }
            )
            filters.append(quality_filter)

        return filters


class FilterValidator:
    """필터 검증기"""

    def validate_filters(
        self,
        filters: List[SearchFilter],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """필터 검증"""

        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }

        # 필터 충돌 검사
        conflicts = self._check_filter_conflicts(filters)
        if conflicts:
            validation_result['warnings'].extend(conflicts)

        # 과도한 필터링 검사
        if self._is_over_filtering(filters):
            validation_result['warnings'].append(
                "Too many restrictive filters may result in few or no results"
            )

        # 필수 필터 누락 검사
        missing_filters = self._check_missing_filters(filters, requirements)
        if missing_filters:
            validation_result['suggestions'].extend(missing_filters)

        return validation_result

    def _check_filter_conflicts(
        self,
        filters: List[SearchFilter]
    ) -> List[str]:
        """필터 충돌 검사"""

        conflicts = []
        
        # 라이선스 필터 충돌
        license_filters = [f for f in filters if f.type == FilterType.LICENSE]
        if len(license_filters) > 1:
            conflicts.append("Multiple license filters may conflict")

        # 언어 필터 충돌
        language_filters = [f for f in filters if f.type == FilterType.LANGUAGE]
        for lang_filter in language_filters:
            preferred = lang_filter.criteria.get('preferred', [])
            excluded = lang_filter.criteria.get('excluded', [])
            
            overlap = set(preferred) & set(excluded)
            if overlap:
                conflicts.append(f"Language filter conflict: {overlap}")

        return conflicts

    def _is_over_filtering(self, filters: List[SearchFilter]) -> bool:
        """과도한 필터링 검사"""
        
        restrictive_count = 0
        
        for filter_config in filters:
            if filter_config.type == FilterType.POPULARITY:
                min_stars = filter_config.criteria.get('min_stars', 0)
                if min_stars > 1000:
                    restrictive_count += 1
            
            elif filter_config.type == FilterType.QUALITY:
                min_score = filter_config.criteria.get('min_score', 0)
                if min_score > 0.8:
                    restrictive_count += 1
            
            elif filter_config.type == FilterType.FRESHNESS:
                max_age = filter_config.criteria.get('max_age_days', 365)
                if max_age < 90:
                    restrictive_count += 1

        return restrictive_count >= 3

    def _check_missing_filters(
        self,
        filters: List[SearchFilter],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """필수 필터 누락 검사"""

        suggestions = []
        filter_types = {f.type for f in filters}

        # 상업적 프로젝트인데 라이선스 필터 없음
        if (requirements.get('commercial_use', False) and 
            FilterType.LICENSE not in filter_types):
            suggestions.append("Consider adding license filter for commercial use")

        # 보안 중요 프로젝트인데 보안 필터 없음
        if (requirements.get('security_critical', False) and 
            FilterType.SECURITY not in filter_types):
            suggestions.append("Consider adding security filter for critical projects")

        return suggestions