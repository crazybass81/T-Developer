# backend/src/agents/nl_input/performance_optimizer.py
import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import cachetools
import concurrent.futures

@dataclass
class PerformanceMetrics:
    processing_time: float
    memory_usage: float
    cache_hit_rate: float
    throughput: float
    error_rate: float

class NLAgentPerformanceOptimizer:
    """완성된 NL Agent 성능 최적화"""

    def __init__(self):
        # 캐시 시스템
        self.intent_cache = cachetools.TTLCache(maxsize=1000, ttl=3600)  # 1시간
        self.template_cache = cachetools.TTLCache(maxsize=500, ttl=7200)  # 2시간
        self.translation_cache = cachetools.TTLCache(maxsize=2000, ttl=1800)  # 30분
        
        # 스레드 풀
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        
        # 성능 메트릭
        self.metrics = PerformanceMetrics(0, 0, 0, 0, 0)
        self.request_count = 0
        self.cache_hits = 0

    async def optimize_intent_analysis(self, description: str, intent_analyzer) -> Dict[str, Any]:
        """의도 분석 최적화"""
        cache_key = f"intent_{hash(description)}"
        
        # 캐시 확인
        if cache_key in self.intent_cache:
            self.cache_hits += 1
            return self.intent_cache[cache_key]
        
        # 병렬 처리를 위한 태스크 분할
        start_time = time.time()
        
        # 의도 분석 실행
        result = await intent_analyzer.analyze_user_intent(description)
        
        # 결과를 직렬화 가능한 형태로 변환
        serializable_result = {
            'primary': result.primary.value,
            'secondary': [intent.value for intent in result.secondary],
            'confidence': result.confidence,
            'business_goals': [
                {
                    'type': goal.type,
                    'description': goal.description,
                    'priority': goal.priority
                } for goal in result.business_goals
            ],
            'technical_goals': [
                {
                    'type': goal.type,
                    'specification': goal.specification,
                    'target_state': goal.target_state
                } for goal in result.technical_goals
            ],
            'constraints': result.constraints
        }
        
        # 캐시에 저장
        self.intent_cache[cache_key] = serializable_result
        
        processing_time = time.time() - start_time
        self._update_metrics(processing_time)
        
        return serializable_result

    async def optimize_multilingual_processing(self, text: str, multilingual_processor) -> Dict[str, Any]:
        """다국어 처리 최적화"""
        cache_key = f"translation_{hash(text)}"
        
        # 캐시 확인
        if cache_key in self.translation_cache:
            self.cache_hits += 1
            return self.translation_cache[cache_key]
        
        start_time = time.time()
        
        # 언어 감지 및 번역 병렬 처리
        tasks = [
            self._detect_language_async(text),
            self._preprocess_text_async(text)
        ]
        
        language, preprocessed = await asyncio.gather(*tasks)
        
        # 번역 처리
        if language != 'en':
            translated = await multilingual_processor._translate_with_context(
                preprocessed, language, 'en'
            )
        else:
            translated = preprocessed
        
        result = {
            'original_language': language,
            'processed_text': translated,
            'translation_confidence': 0.9 if language != 'en' else 1.0
        }
        
        # 캐시에 저장
        self.translation_cache[cache_key] = result
        
        processing_time = time.time() - start_time
        self._update_metrics(processing_time)
        
        return result

    async def optimize_requirement_prioritization(self, requirements: List[Dict[str, Any]], prioritizer) -> List[Dict[str, Any]]:
        """요구사항 우선순위 최적화"""
        
        # 배치 처리를 위한 청킹
        chunk_size = 50
        chunks = [requirements[i:i + chunk_size] for i in range(0, len(requirements), chunk_size)]
        
        start_time = time.time()
        
        # 병렬 처리
        tasks = []
        for chunk in chunks:
            task = self._process_requirement_chunk(chunk, prioritizer)
            tasks.append(task)
        
        chunk_results = await asyncio.gather(*tasks)
        
        # 결과 병합
        all_prioritized = []
        for chunk_result in chunk_results:
            all_prioritized.extend(chunk_result)
        
        # 전체 정렬
        all_prioritized.sort(key=lambda x: x.priority_score, reverse=True)
        
        processing_time = time.time() - start_time
        self._update_metrics(processing_time)
        
        return all_prioritized

    async def _process_requirement_chunk(self, chunk: List[Dict[str, Any]], prioritizer) -> List[Dict[str, Any]]:
        """요구사항 청크 처리"""
        
        # 병렬로 각 요구사항 처리
        tasks = []
        for req in chunk:
            task = self._calculate_single_priority(req, prioritizer)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

    async def _calculate_single_priority(self, requirement: Dict[str, Any], prioritizer) -> Dict[str, Any]:
        """단일 요구사항 우선순위 계산"""
        
        # 비즈니스 가치 계산
        business_value = prioritizer._calculate_business_value(requirement, {})
        
        # 노력 추정
        effort = prioritizer._estimate_effort(requirement)
        
        # 리스크 평가
        risk = prioritizer._assess_risk(requirement)
        
        # WSJF 점수 계산
        wsjf_score = prioritizer._calculate_wsjf_score(business_value, effort, risk, 0)
        
        return {
            'requirement': requirement,
            'priority_score': wsjf_score,
            'business_value': business_value,
            'estimated_effort': effort,
            'risk_level': risk
        }

    async def _detect_language_async(self, text: str) -> str:
        """비동기 언어 감지"""
        loop = asyncio.get_event_loop()
        
        def detect_lang():
            try:
                import langdetect
                return langdetect.detect(text)
            except:
                return 'en'
        
        return await loop.run_in_executor(self.executor, detect_lang)

    async def _preprocess_text_async(self, text: str) -> str:
        """비동기 텍스트 전처리"""
        loop = asyncio.get_event_loop()
        
        def preprocess():
            # 기본 전처리
            return text.strip().lower()
        
        return await loop.run_in_executor(self.executor, preprocess)

    def _update_metrics(self, processing_time: float):
        """성능 메트릭 업데이트"""
        self.request_count += 1
        
        # 이동 평균으로 메트릭 업데이트
        alpha = 0.1  # 가중치
        self.metrics.processing_time = (
            alpha * processing_time + 
            (1 - alpha) * self.metrics.processing_time
        )
        
        # 캐시 히트율
        self.metrics.cache_hit_rate = self.cache_hits / self.request_count if self.request_count > 0 else 0
        
        # 처리량 (requests per second)
        self.metrics.throughput = 1.0 / processing_time if processing_time > 0 else 0

    async def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서 생성"""
        return {
            'metrics': {
                'avg_processing_time': self.metrics.processing_time,
                'cache_hit_rate': self.metrics.cache_hit_rate,
                'throughput_rps': self.metrics.throughput,
                'total_requests': self.request_count
            },
            'cache_stats': {
                'intent_cache_size': len(self.intent_cache),
                'template_cache_size': len(self.template_cache),
                'translation_cache_size': len(self.translation_cache)
            },
            'recommendations': self._generate_optimization_recommendations()
        }

    def _generate_optimization_recommendations(self) -> List[str]:
        """최적화 권장사항 생성"""
        recommendations = []
        
        if self.metrics.cache_hit_rate < 0.3:
            recommendations.append("Consider increasing cache TTL or size")
        
        if self.metrics.processing_time > 1.0:
            recommendations.append("Consider adding more parallel processing")
        
        if self.metrics.throughput < 10:
            recommendations.append("Consider optimizing bottleneck operations")
        
        return recommendations

    async def cleanup(self):
        """리소스 정리"""
        self.executor.shutdown(wait=True)
        self.intent_cache.clear()
        self.template_cache.clear()
        self.translation_cache.clear()