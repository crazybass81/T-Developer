# backend/src/agents/implementations/search/ranking_system.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import asyncio

@dataclass
class RankingFeature:
    name: str
    value: float
    weight: float
    normalized_value: float

@dataclass
class RankedResult:
    component: Dict[str, Any]
    final_score: float
    ranking_features: List[RankingFeature]
    rank_position: int
    confidence: float

class SearchResultRanker:
    """검색 결과 랭킹 시스템"""

    def __init__(self):
        self.feature_extractors = {
            'relevance': RelevanceScorer(),
            'popularity': PopularityScorer(),
            'quality': QualityScorer(),
            'freshness': FreshnessScorer(),
            'compatibility': CompatibilityScorer()
        }
        
        self.scaler = MinMaxScaler()
        self.learning_to_rank = LearningToRankModel()
        
        # 기본 가중치
        self.default_weights = {
            'relevance': 0.35,
            'popularity': 0.20,
            'quality': 0.20,
            'freshness': 0.10,
            'compatibility': 0.15
        }

    async def rank_results(
        self,
        search_results: List[Dict[str, Any]],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[RankedResult]:
        """검색 결과 랭킹"""

        if not search_results:
            return []

        # 특성 추출
        features_matrix = await self._extract_features(
            search_results,
            query,
            context
        )

        # 가중치 조정
        weights = self._adjust_weights(context)

        # 점수 계산
        scores = await self._calculate_scores(
            features_matrix,
            weights
        )

        # 랭킹 생성
        ranked_results = self._create_ranked_results(
            search_results,
            features_matrix,
            scores
        )

        # 다양성 조정
        diversified_results = await self._apply_diversification(
            ranked_results,
            context
        )

        return diversified_results

    async def _extract_features(
        self,
        results: List[Dict[str, Any]],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> List[List[RankingFeature]]:
        """특성 추출"""

        features_matrix = []

        for result in results:
            features = []
            
            # 병렬로 특성 추출
            tasks = [
                extractor.extract(result, query, context)
                for extractor in self.feature_extractors.values()
            ]
            
            feature_values = await asyncio.gather(*tasks)
            
            for i, (name, extractor) in enumerate(self.feature_extractors.items()):
                features.append(RankingFeature(
                    name=name,
                    value=feature_values[i],
                    weight=self.default_weights[name],
                    normalized_value=0.0  # 나중에 정규화
                ))
            
            features_matrix.append(features)

        # 특성 정규화
        self._normalize_features(features_matrix)

        return features_matrix

    def _normalize_features(
        self,
        features_matrix: List[List[RankingFeature]]
    ) -> None:
        """특성 정규화"""

        # 특성별로 값 수집
        feature_values = {}
        for features in features_matrix:
            for feature in features:
                if feature.name not in feature_values:
                    feature_values[feature.name] = []
                feature_values[feature.name].append(feature.value)

        # 특성별 정규화
        for feature_name, values in feature_values.items():
            if len(set(values)) > 1:  # 모든 값이 같지 않은 경우
                min_val = min(values)
                max_val = max(values)
                
                for features in features_matrix:
                    for feature in features:
                        if feature.name == feature_name:
                            feature.normalized_value = (
                                (feature.value - min_val) / (max_val - min_val)
                            )
            else:
                # 모든 값이 같은 경우
                for features in features_matrix:
                    for feature in features:
                        if feature.name == feature_name:
                            feature.normalized_value = 0.5

    async def _calculate_scores(
        self,
        features_matrix: List[List[RankingFeature]],
        weights: Dict[str, float]
    ) -> List[float]:
        """점수 계산"""

        scores = []

        for features in features_matrix:
            # 가중 합계
            weighted_score = sum(
                feature.normalized_value * weights[feature.name]
                for feature in features
            )
            
            scores.append(weighted_score)

        return scores

    def _create_ranked_results(
        self,
        results: List[Dict[str, Any]],
        features_matrix: List[List[RankingFeature]],
        scores: List[float]
    ) -> List[RankedResult]:
        """랭킹된 결과 생성"""

        # 점수 기준 정렬
        sorted_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        ranked_results = []
        for rank, idx in enumerate(sorted_indices):
            confidence = self._calculate_confidence(
                features_matrix[idx],
                scores[idx]
            )

            ranked_results.append(RankedResult(
                component=results[idx],
                final_score=scores[idx],
                ranking_features=features_matrix[idx],
                rank_position=rank + 1,
                confidence=confidence
            ))

        return ranked_results

class RelevanceScorer:
    """관련성 점수 계산기"""

    async def extract(
        self,
        component: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """관련성 점수 추출"""

        # 텍스트 매칭 점수
        text_score = self._calculate_text_relevance(
            component,
            query
        )

        # 태그 매칭 점수
        tag_score = self._calculate_tag_relevance(
            component.get('tags', []),
            query
        )

        # 카테고리 매칭 점수
        category_score = self._calculate_category_relevance(
            component.get('category', ''),
            query
        )

        # 종합 점수
        return (text_score * 0.5 + tag_score * 0.3 + category_score * 0.2)

    def _calculate_text_relevance(
        self,
        component: Dict[str, Any],
        query: str
    ) -> float:
        """텍스트 관련성 계산"""

        # 제목, 설명에서 키워드 매칭
        title = component.get('name', '').lower()
        description = component.get('description', '').lower()
        query_lower = query.lower()

        # 정확한 매칭
        exact_match_score = 0.0
        if query_lower in title:
            exact_match_score += 1.0
        elif query_lower in description:
            exact_match_score += 0.7

        # 키워드 매칭
        query_words = query_lower.split()
        title_words = title.split()
        desc_words = description.split()

        title_matches = len(set(query_words) & set(title_words))
        desc_matches = len(set(query_words) & set(desc_words))

        keyword_score = (
            (title_matches / len(query_words)) * 0.8 +
            (desc_matches / len(query_words)) * 0.2
        ) if query_words else 0.0

        return min(1.0, exact_match_score + keyword_score)

class PopularityScorer:
    """인기도 점수 계산기"""

    async def extract(
        self,
        component: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """인기도 점수 추출"""

        # GitHub 스타 수
        stars = component.get('github_stars', 0)
        
        # 다운로드 수
        downloads = component.get('downloads', 0)
        
        # 포크 수
        forks = component.get('forks', 0)

        # 로그 스케일 적용
        star_score = np.log10(max(1, stars)) / 6  # 최대 1M 스타 기준
        download_score = np.log10(max(1, downloads)) / 8  # 최대 100M 다운로드 기준
        fork_score = np.log10(max(1, forks)) / 5  # 최대 100K 포크 기준

        return min(1.0, star_score * 0.4 + download_score * 0.4 + fork_score * 0.2)

class QualityScorer:
    """품질 점수 계산기"""

    async def extract(
        self,
        component: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """품질 점수 추출"""

        # 문서화 점수
        has_readme = bool(component.get('has_readme', False))
        has_docs = bool(component.get('has_documentation', False))
        doc_score = (has_readme * 0.3 + has_docs * 0.7)

        # 테스트 커버리지
        test_coverage = component.get('test_coverage', 0) / 100.0

        # 이슈 대응률
        open_issues = component.get('open_issues', 0)
        closed_issues = component.get('closed_issues', 0)
        total_issues = open_issues + closed_issues
        
        issue_response_rate = (
            closed_issues / total_issues if total_issues > 0 else 0.5
        )

        # 최근 활동
        last_commit_days = component.get('days_since_last_commit', 365)
        activity_score = max(0, 1 - (last_commit_days / 365))

        return (
            doc_score * 0.3 +
            test_coverage * 0.2 +
            issue_response_rate * 0.2 +
            activity_score * 0.3
        )

class FreshnessScorer:
    """신선도 점수 계산기"""

    async def extract(
        self,
        component: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """신선도 점수 추출"""

        # 최근 업데이트
        days_since_update = component.get('days_since_last_update', 365)
        update_score = max(0, 1 - (days_since_update / 365))

        # 버전 신선도
        version = component.get('version', '0.0.0')
        version_score = self._calculate_version_freshness(version)

        return update_score * 0.7 + version_score * 0.3

    def _calculate_version_freshness(self, version: str) -> float:
        """버전 신선도 계산"""
        try:
            parts = version.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            # 메이저 버전이 높을수록, 마이너 버전이 높을수록 신선
            return min(1.0, (major * 0.3 + minor * 0.1) / 10)
        except:
            return 0.5

class CompatibilityScorer:
    """호환성 점수 계산기"""

    async def extract(
        self,
        component: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """호환성 점수 추출"""

        if not context:
            return 0.5

        # 기술 스택 호환성
        required_tech = set(context.get('tech_stack', []))
        component_tech = set(component.get('technologies', []))
        
        tech_overlap = len(required_tech & component_tech)
        tech_score = tech_overlap / len(required_tech) if required_tech else 1.0

        # 라이선스 호환성
        required_license = context.get('license_preference', [])
        component_license = component.get('license', '')
        
        license_score = 1.0 if (
            not required_license or 
            component_license in required_license
        ) else 0.3

        # 플랫폼 호환성
        required_platforms = set(context.get('platforms', []))
        component_platforms = set(component.get('platforms', []))
        
        platform_overlap = len(required_platforms & component_platforms)
        platform_score = (
            platform_overlap / len(required_platforms) 
            if required_platforms else 1.0
        )

        return tech_score * 0.5 + license_score * 0.2 + platform_score * 0.3