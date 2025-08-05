# Task 4.4: Multi-Criteria Decision Making System
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import asyncio

@dataclass
class DecisionAlternative:
    name: str
    criteria_scores: Dict[str, float]
    metadata: Dict[str, Any]

class MultiCriteriaDecisionSystem:
    """다중 기준 의사결정 시스템 (MCDM)"""

    def __init__(self):
        self.methods = {
            'topsis': self._topsis_method,
            'ahp': self._analytic_hierarchy_process,
            'weighted_sum': self._weighted_sum_method,
            'electre': self._electre_method
        }

    async def make_decision(
        self,
        alternatives: List[DecisionAlternative],
        criteria_weights: Dict[str, float],
        method: str = 'topsis'
    ) -> Dict[str, Any]:
        """다중 기준 의사결정 수행"""

        if method not in self.methods:
            raise ValueError(f"Unknown method: {method}")

        # 의사결정 매트릭스 구성
        decision_matrix = self._build_decision_matrix(alternatives, criteria_weights)
        
        # 선택된 방법으로 의사결정
        decision_method = self.methods[method]
        result = await decision_method(decision_matrix, criteria_weights)
        
        # 민감도 분석
        sensitivity_analysis = await self._sensitivity_analysis(
            alternatives, criteria_weights, method
        )
        
        return {
            'method_used': method,
            'ranking': result['ranking'],
            'scores': result['scores'],
            'decision_matrix': decision_matrix,
            'sensitivity_analysis': sensitivity_analysis,
            'recommendation': result['ranking'][0] if result['ranking'] else None
        }

    def _build_decision_matrix(
        self,
        alternatives: List[DecisionAlternative],
        criteria_weights: Dict[str, float]
    ) -> np.ndarray:
        """의사결정 매트릭스 구성"""
        
        criteria_names = list(criteria_weights.keys())
        matrix = []
        
        for alternative in alternatives:
            row = []
            for criterion in criteria_names:
                score = alternative.criteria_scores.get(criterion, 5.0)
                row.append(score)
            matrix.append(row)
        
        return np.array(matrix)

    async def _topsis_method(
        self,
        matrix: np.ndarray,
        criteria_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)"""
        
        # 1. 정규화
        normalized = matrix / np.sqrt(np.sum(matrix**2, axis=0))
        
        # 2. 가중치 적용
        weights = np.array(list(criteria_weights.values()))
        weighted = normalized * weights
        
        # 3. 이상적 해와 부정적 이상적 해
        ideal_positive = np.max(weighted, axis=0)
        ideal_negative = np.min(weighted, axis=0)
        
        # 4. 거리 계산
        distances_positive = np.sqrt(np.sum((weighted - ideal_positive)**2, axis=1))
        distances_negative = np.sqrt(np.sum((weighted - ideal_negative)**2, axis=1))
        
        # 5. TOPSIS 점수
        scores = distances_negative / (distances_positive + distances_negative)
        
        # 6. 순위 매기기
        ranking_indices = np.argsort(scores)[::-1]
        
        return {
            'scores': scores.tolist(),
            'ranking': ranking_indices.tolist(),
            'ideal_positive': ideal_positive.tolist(),
            'ideal_negative': ideal_negative.tolist()
        }

    async def _analytic_hierarchy_process(
        self,
        matrix: np.ndarray,
        criteria_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """AHP (Analytic Hierarchy Process)"""
        
        # 1. 쌍대비교 매트릭스 생성 (간소화된 버전)
        n_alternatives = matrix.shape[0]
        pairwise_matrix = np.zeros((n_alternatives, n_alternatives))
        
        # 2. 각 대안의 종합 점수 계산
        weights = np.array(list(criteria_weights.values()))
        weighted_scores = np.dot(matrix, weights)
        
        # 3. 쌍대비교 매트릭스 채우기
        for i in range(n_alternatives):
            for j in range(n_alternatives):
                if i != j:
                    ratio = weighted_scores[i] / weighted_scores[j]
                    pairwise_matrix[i][j] = ratio
                else:
                    pairwise_matrix[i][j] = 1.0
        
        # 4. 고유벡터 계산 (우선순위 벡터)
        eigenvalues, eigenvectors = np.linalg.eig(pairwise_matrix)
        max_eigenvalue_index = np.argmax(eigenvalues.real)
        priority_vector = eigenvectors[:, max_eigenvalue_index].real
        priority_vector = priority_vector / np.sum(priority_vector)
        
        # 5. 일관성 비율 계산
        max_eigenvalue = eigenvalues[max_eigenvalue_index].real
        ci = (max_eigenvalue - n_alternatives) / (n_alternatives - 1)
        ri = self._get_random_index(n_alternatives)
        cr = ci / ri if ri > 0 else 0
        
        # 6. 순위 매기기
        ranking_indices = np.argsort(priority_vector)[::-1]
        
        return {
            'scores': priority_vector.tolist(),
            'ranking': ranking_indices.tolist(),
            'consistency_ratio': cr,
            'pairwise_matrix': pairwise_matrix.tolist()
        }

    def _get_random_index(self, n: int) -> float:
        """AHP 랜덤 인덱스"""
        ri_values = {
            1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
        }
        return ri_values.get(n, 1.49)

    async def _weighted_sum_method(
        self,
        matrix: np.ndarray,
        criteria_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """가중합 방법"""
        
        # 1. 정규화 (최대값으로 나누기)
        normalized = matrix / np.max(matrix, axis=0)
        
        # 2. 가중치 적용
        weights = np.array(list(criteria_weights.values()))
        weighted_scores = np.dot(normalized, weights)
        
        # 3. 순위 매기기
        ranking_indices = np.argsort(weighted_scores)[::-1]
        
        return {
            'scores': weighted_scores.tolist(),
            'ranking': ranking_indices.tolist(),
            'normalized_matrix': normalized.tolist()
        }

    async def _electre_method(
        self,
        matrix: np.ndarray,
        criteria_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """ELECTRE 방법"""
        
        n_alternatives = matrix.shape[0]
        n_criteria = matrix.shape[1]
        weights = np.array(list(criteria_weights.values()))
        
        # 1. 정규화
        normalized = matrix / np.sqrt(np.sum(matrix**2, axis=0))
        
        # 2. 가중 정규화
        weighted = normalized * weights
        
        # 3. 일치 집합과 불일치 집합 계산
        concordance_matrix = np.zeros((n_alternatives, n_alternatives))
        discordance_matrix = np.zeros((n_alternatives, n_alternatives))
        
        for i in range(n_alternatives):
            for j in range(n_alternatives):
                if i != j:
                    # 일치 집합
                    concordance_set = []
                    discordance_set = []
                    
                    for k in range(n_criteria):
                        if weighted[i][k] >= weighted[j][k]:
                            concordance_set.append(k)
                        else:
                            discordance_set.append(k)
                    
                    # 일치 지수
                    concordance_index = sum(weights[k] for k in concordance_set)
                    concordance_matrix[i][j] = concordance_index
                    
                    # 불일치 지수
                    if discordance_set:
                        max_discordance = max(
                            abs(weighted[j][k] - weighted[i][k]) 
                            for k in discordance_set
                        )
                        max_overall = np.max(np.abs(weighted[j] - weighted[i]))
                        discordance_matrix[i][j] = max_discordance / max_overall if max_overall > 0 else 0
        
        # 4. 우월 관계 결정
        concordance_threshold = 0.6
        discordance_threshold = 0.4
        
        dominance_matrix = np.zeros((n_alternatives, n_alternatives))
        for i in range(n_alternatives):
            for j in range(n_alternatives):
                if (concordance_matrix[i][j] >= concordance_threshold and 
                    discordance_matrix[i][j] <= discordance_threshold):
                    dominance_matrix[i][j] = 1
        
        # 5. 순위 계산 (우월 점수 기반)
        dominance_scores = np.sum(dominance_matrix, axis=1)
        ranking_indices = np.argsort(dominance_scores)[::-1]
        
        return {
            'scores': dominance_scores.tolist(),
            'ranking': ranking_indices.tolist(),
            'concordance_matrix': concordance_matrix.tolist(),
            'discordance_matrix': discordance_matrix.tolist(),
            'dominance_matrix': dominance_matrix.tolist()
        }

    async def _sensitivity_analysis(
        self,
        alternatives: List[DecisionAlternative],
        criteria_weights: Dict[str, float],
        method: str
    ) -> Dict[str, Any]:
        """민감도 분석"""
        
        sensitivity_results = {}
        
        # 각 기준의 가중치를 ±20% 변경하여 결과 변화 관찰
        for criterion in criteria_weights.keys():
            variations = []
            
            for variation in [-0.2, -0.1, 0.1, 0.2]:
                modified_weights = criteria_weights.copy()
                original_weight = modified_weights[criterion]
                new_weight = max(0.01, min(1.0, original_weight * (1 + variation)))
                modified_weights[criterion] = new_weight
                
                # 가중치 정규화
                total_weight = sum(modified_weights.values())
                modified_weights = {k: v/total_weight for k, v in modified_weights.items()}
                
                # 수정된 가중치로 의사결정 재실행
                result = await self.make_decision(alternatives, modified_weights, method)
                
                variations.append({
                    'weight_change': variation,
                    'new_weight': new_weight,
                    'ranking': result['ranking'][:3],  # 상위 3개만
                    'top_alternative': result['ranking'][0] if result['ranking'] else None
                })
            
            sensitivity_results[criterion] = variations
        
        # 안정성 점수 계산
        stability_score = await self._calculate_stability_score(sensitivity_results)
        
        return {
            'criterion_sensitivity': sensitivity_results,
            'stability_score': stability_score,
            'robust_alternatives': await self._identify_robust_alternatives(sensitivity_results)
        }

    async def _calculate_stability_score(self, sensitivity_results: Dict[str, Any]) -> float:
        """안정성 점수 계산"""
        
        total_variations = 0
        consistent_rankings = 0
        
        for criterion, variations in sensitivity_results.items():
            original_top = variations[0]['top_alternative'] if variations else None
            
            for variation in variations:
                total_variations += 1
                if variation['top_alternative'] == original_top:
                    consistent_rankings += 1
        
        return consistent_rankings / total_variations if total_variations > 0 else 0.0

    async def _identify_robust_alternatives(
        self,
        sensitivity_results: Dict[str, Any]
    ) -> List[str]:
        """강건한 대안 식별"""
        
        alternative_appearances = {}
        
        for criterion, variations in sensitivity_results.items():
            for variation in variations:
                top_alt = variation['top_alternative']
                if top_alt:
                    alternative_appearances[top_alt] = alternative_appearances.get(top_alt, 0) + 1
        
        # 가장 자주 1위를 차지한 대안들
        max_appearances = max(alternative_appearances.values()) if alternative_appearances else 0
        robust_alternatives = [
            alt for alt, count in alternative_appearances.items()
            if count >= max_appearances * 0.7  # 70% 이상
        ]
        
        return robust_alternatives