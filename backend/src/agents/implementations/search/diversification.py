# backend/src/agents/implementations/search/diversification.py
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class DiversityMetric:
    name: str
    value: float
    threshold: float

class ResultDiversifier:
    """검색 결과 다양성 조정기"""

    def __init__(self):
        self.similarity_calculator = SimilarityCalculator()
        self.category_balancer = CategoryBalancer()
        
        # 다양성 파라미터
        self.diversity_weight = 0.3  # 다양성 vs 관련성 균형
        self.max_similar_results = 3  # 유사한 결과 최대 개수

    async def diversify_results(
        self,
        ranked_results: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """결과 다양성 조정"""

        if len(ranked_results) <= 5:
            return ranked_results  # 결과가 적으면 다양성 조정 생략

        # MMR (Maximal Marginal Relevance) 적용
        diversified = await self._apply_mmr(
            ranked_results,
            self.diversity_weight
        )

        # 카테고리 균형 조정
        balanced = await self.category_balancer.balance(
            diversified,
            context
        )

        # 중복 제거
        deduplicated = self._remove_duplicates(balanced)

        return deduplicated

    async def _apply_mmr(
        self,
        results: List[Any],
        lambda_param: float
    ) -> List[Any]:
        """Maximal Marginal Relevance 적용"""

        if not results:
            return []

        # 첫 번째 결과는 가장 관련성이 높은 것
        selected = [results[0]]
        remaining = results[1:]

        while remaining and len(selected) < len(results):
            best_score = -1
            best_idx = -1

            for i, candidate in enumerate(remaining):
                # 관련성 점수
                relevance_score = candidate.final_score

                # 이미 선택된 결과들과의 유사도
                max_similarity = 0
                for selected_result in selected:
                    similarity = await self.similarity_calculator.calculate(
                        candidate.component,
                        selected_result.component
                    )
                    max_similarity = max(max_similarity, similarity)

                # MMR 점수 계산
                mmr_score = (
                    lambda_param * relevance_score - 
                    (1 - lambda_param) * max_similarity
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i

            if best_idx >= 0:
                selected.append(remaining.pop(best_idx))
            else:
                break

        return selected

    def _remove_duplicates(
        self,
        results: List[Any]
    ) -> List[Any]:
        """중복 결과 제거"""

        seen_ids = set()
        unique_results = []

        for result in results:
            component_id = result.component.get('id')
            if component_id and component_id not in seen_ids:
                seen_ids.add(component_id)
                unique_results.append(result)
            elif not component_id:
                # ID가 없는 경우 이름으로 중복 체크
                name = result.component.get('name', '')
                if name not in seen_ids:
                    seen_ids.add(name)
                    unique_results.append(result)

        return unique_results

class SimilarityCalculator:
    """유사도 계산기"""

    async def calculate(
        self,
        component1: Dict[str, Any],
        component2: Dict[str, Any]
    ) -> float:
        """두 컴포넌트 간 유사도 계산"""

        # 텍스트 유사도
        text_sim = self._calculate_text_similarity(
            component1,
            component2
        )

        # 카테고리 유사도
        category_sim = self._calculate_category_similarity(
            component1.get('category', ''),
            component2.get('category', '')
        )

        # 태그 유사도
        tag_sim = self._calculate_tag_similarity(
            component1.get('tags', []),
            component2.get('tags', [])
        )

        # 기술 스택 유사도
        tech_sim = self._calculate_tech_similarity(
            component1.get('technologies', []),
            component2.get('technologies', [])
        )

        # 가중 평균
        return (
            text_sim * 0.3 +
            category_sim * 0.2 +
            tag_sim * 0.3 +
            tech_sim * 0.2
        )

    def _calculate_text_similarity(
        self,
        comp1: Dict[str, Any],
        comp2: Dict[str, Any]
    ) -> float:
        """텍스트 유사도 계산"""

        text1 = f"{comp1.get('name', '')} {comp1.get('description', '')}"
        text2 = f"{comp2.get('name', '')} {comp2.get('description', '')}"

        # 간단한 Jaccard 유사도
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union

    def _calculate_tag_similarity(
        self,
        tags1: List[str],
        tags2: List[str]
    ) -> float:
        """태그 유사도 계산"""

        if not tags1 and not tags2:
            return 1.0
        if not tags1 or not tags2:
            return 0.0

        set1 = set(tag.lower() for tag in tags1)
        set2 = set(tag.lower() for tag in tags2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union

class CategoryBalancer:
    """카테고리 균형 조정기"""

    def __init__(self):
        self.max_per_category = 5  # 카테고리당 최대 결과 수

    async def balance(
        self,
        results: List[Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Any]:
        """카테고리 균형 조정"""

        if not results:
            return []

        # 카테고리별 그룹화
        category_groups = {}
        for result in results:
            category = result.component.get('category', 'unknown')
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(result)

        # 각 카테고리에서 상위 결과만 선택
        balanced_results = []
        
        # 카테고리별로 순환하면서 결과 선택
        max_rounds = max(len(group) for group in category_groups.values())
        
        for round_num in range(max_rounds):
            for category, group in category_groups.items():
                if round_num < len(group) and len([
                    r for r in balanced_results 
                    if r.component.get('category') == category
                ]) < self.max_per_category:
                    balanced_results.append(group[round_num])

        # 원래 순서 유지하면서 정렬
        original_order = {id(result): i for i, result in enumerate(results)}
        balanced_results.sort(key=lambda x: original_order.get(id(x), float('inf')))

        return balanced_results