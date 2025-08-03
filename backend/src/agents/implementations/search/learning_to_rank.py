# backend/src/agents/implementations/search/learning_to_rank.py
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import ndcg_score
import joblib
import asyncio

class LearningToRankModel:
    """Learning to Rank 모델"""

    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_names = [
            'relevance_score',
            'popularity_score', 
            'quality_score',
            'freshness_score',
            'compatibility_score',
            'click_through_rate',
            'dwell_time',
            'query_component_match'
        ]
        self.is_trained = False
        self.training_data = []

    async def train(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """모델 훈련"""

        if len(training_data) < 100:
            return {'error': 'Insufficient training data'}

        # 특성과 레이블 준비
        X, y, groups = self._prepare_training_data(training_data)

        # 훈련/검증 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 모델 훈련
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # 성능 평가
        y_pred = self.model.predict(X_test)
        
        # NDCG 계산 (그룹별로)
        ndcg_scores = []
        test_groups = self._get_groups_for_split(groups, len(X_test), len(X))
        
        for group_queries in test_groups:
            if len(group_queries) > 1:
                group_true = [y_test[i] for i in group_queries]
                group_pred = [y_pred[i] for i in group_queries]
                
                # NDCG@10 계산
                ndcg = ndcg_score(
                    [group_true], 
                    [group_pred], 
                    k=10
                )
                ndcg_scores.append(ndcg)

        avg_ndcg = np.mean(ndcg_scores) if ndcg_scores else 0.0

        # 특성 중요도
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))

        return {
            'ndcg_score': avg_ndcg,
            'feature_importance': feature_importance,
            'training_samples': len(training_data)
        }

    async def predict_scores(
        self,
        features: List[List[float]]
    ) -> List[float]:
        """점수 예측"""

        if not self.is_trained:
            # 모델이 훈련되지 않은 경우 기본 점수 반환
            return [0.5] * len(features)

        try:
            scores = self.model.predict(features)
            return scores.tolist()
        except Exception as e:
            print(f"Prediction error: {e}")
            return [0.5] * len(features)

    def _prepare_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray, List[List[int]]]:
        """훈련 데이터 준비"""

        X = []
        y = []
        groups = []
        current_group = []
        current_query = None
        sample_idx = 0

        for sample in training_data:
            query = sample['query']
            
            # 새로운 쿼리 그룹 시작
            if query != current_query:
                if current_group:
                    groups.append(current_group)
                current_group = []
                current_query = query

            # 특성 벡터 생성
            features = [
                sample.get('relevance_score', 0.0),
                sample.get('popularity_score', 0.0),
                sample.get('quality_score', 0.0),
                sample.get('freshness_score', 0.0),
                sample.get('compatibility_score', 0.0),
                sample.get('click_through_rate', 0.0),
                sample.get('dwell_time', 0.0),
                sample.get('query_component_match', 0.0)
            ]

            X.append(features)
            y.append(sample.get('relevance_label', 0))  # 0-4 스케일
            current_group.append(sample_idx)
            sample_idx += 1

        # 마지막 그룹 추가
        if current_group:
            groups.append(current_group)

        return np.array(X), np.array(y), groups

    async def collect_feedback(
        self,
        query: str,
        results: List[Dict[str, Any]],
        user_interactions: Dict[str, Any]
    ) -> None:
        """사용자 피드백 수집"""

        clicked_results = user_interactions.get('clicked_results', [])
        dwell_times = user_interactions.get('dwell_times', {})

        for i, result in enumerate(results):
            component_id = result.get('id', '')
            
            # 클릭 여부
            was_clicked = component_id in clicked_results
            
            # 체류 시간
            dwell_time = dwell_times.get(component_id, 0)
            
            # 관련성 레이블 계산 (휴리스틱)
            relevance_label = self._calculate_relevance_label(
                position=i,
                was_clicked=was_clicked,
                dwell_time=dwell_time
            )

            # 훈련 데이터에 추가
            training_sample = {
                'query': query,
                'component_id': component_id,
                'position': i,
                'relevance_score': result.get('relevance_score', 0.0),
                'popularity_score': result.get('popularity_score', 0.0),
                'quality_score': result.get('quality_score', 0.0),
                'freshness_score': result.get('freshness_score', 0.0),
                'compatibility_score': result.get('compatibility_score', 0.0),
                'click_through_rate': 1.0 if was_clicked else 0.0,
                'dwell_time': dwell_time,
                'query_component_match': self._calculate_query_match(
                    query, 
                    result
                ),
                'relevance_label': relevance_label
            }

            self.training_data.append(training_sample)

        # 주기적으로 재훈련
        if len(self.training_data) % 1000 == 0:
            await self.retrain()

    def _calculate_relevance_label(
        self,
        position: int,
        was_clicked: bool,
        dwell_time: float
    ) -> int:
        """관련성 레이블 계산"""

        if not was_clicked:
            return 0

        # 클릭된 경우
        if dwell_time > 30:  # 30초 이상 체류
            return 4  # 매우 관련성 높음
        elif dwell_time > 10:  # 10초 이상 체류
            return 3  # 관련성 높음
        elif dwell_time > 3:   # 3초 이상 체류
            return 2  # 보통 관련성
        else:
            return 1  # 낮은 관련성

    async def retrain(self) -> None:
        """모델 재훈련"""

        if len(self.training_data) >= 100:
            await self.train(self.training_data)
            
            # 오래된 데이터 정리 (최근 10000개만 유지)
            if len(self.training_data) > 10000:
                self.training_data = self.training_data[-10000:]

    def save_model(self, filepath: str) -> None:
        """모델 저장"""
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'training_data_size': len(self.training_data)
        }
        
        joblib.dump(model_data, filepath)

    def load_model(self, filepath: str) -> None:
        """모델 로드"""
        
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            print(f"Model loaded with {model_data['training_data_size']} training samples")
        except Exception as e:
            print(f"Failed to load model: {e}")

class RankingOptimizer:
    """랭킹 최적화기"""

    def __init__(self):
        self.ab_test_manager = ABTestManager()
        self.performance_tracker = PerformanceTracker()

    async def optimize_ranking(
        self,
        current_ranker: Any,
        search_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """랭킹 최적화"""

        # 현재 성능 분석
        current_performance = await self.performance_tracker.analyze(
            search_logs
        )

        # 개선 제안
        improvements = await self._suggest_improvements(
            current_performance,
            search_logs
        )

        # A/B 테스트 설정
        ab_test_config = await self.ab_test_manager.setup_test(
            improvements
        )

        return {
            'current_performance': current_performance,
            'suggested_improvements': improvements,
            'ab_test_config': ab_test_config
        }

    async def _suggest_improvements(
        self,
        performance: Dict[str, Any],
        search_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """개선 제안"""

        suggestions = []

        # CTR이 낮은 경우
        if performance.get('overall_ctr', 0) < 0.1:
            suggestions.append({
                'type': 'weight_adjustment',
                'description': 'Increase relevance weight',
                'parameters': {'relevance_weight': 0.4}
            })

        # 다양성이 부족한 경우
        if performance.get('diversity_score', 0) < 0.3:
            suggestions.append({
                'type': 'diversification',
                'description': 'Increase diversity parameter',
                'parameters': {'diversity_weight': 0.4}
            })

        # 신선도 점수가 낮은 경우
        if performance.get('avg_freshness', 0) < 0.5:
            suggestions.append({
                'type': 'freshness_boost',
                'description': 'Boost freshness weight',
                'parameters': {'freshness_weight': 0.2}
            })

        return suggestions