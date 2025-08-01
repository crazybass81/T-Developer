from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import time

from .nl_input_agent import NLInputAgent
from .nl_advanced_integration import AdvancedNLIntegration
from .nl_performance_optimizer import NLPerformanceOptimizer
from .nl_context_manager import ConversationContextManager
from .nl_multilingual import MultilingualNLProcessor
from .nl_realtime_feedback import RealtimeFeedbackProcessor

@dataclass
class ComprehensiveNLResult:
    """종합 NL 처리 결과"""
    session_id: str
    user_id: str
    original_language: str
    processed_requirements: Any
    advanced_analysis: Any
    context_updates: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    confidence_score: float
    processing_time: float
    next_actions: List[str]

class ComprehensiveNLAgent:
    """완전한 NL Input Agent 통합 시스템"""
    
    def __init__(self):
        # 핵심 컴포넌트
        self.basic_agent = NLInputAgent()
        self.advanced_integration = AdvancedNLIntegration()
        self.performance_optimizer = NLPerformanceOptimizer()
        
        # 컨텍스트 및 다국어 지원
        self.context_manager = ConversationContextManager(None)  # storage_client는 실제 구현에서 주입
        self.multilingual_processor = MultilingualNLProcessor(self.basic_agent)
        self.feedback_processor = RealtimeFeedbackProcessor(self.basic_agent)
        
        # 초기화 상태
        self.initialized = False
    
    async def initialize(self):
        """시스템 초기화"""
        if not self.initialized:
            await self.performance_optimizer.initialize()
            self.initialized = True
    
    async def process_comprehensive_request(
        self,
        description: str,
        session_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        enable_advanced_analysis: bool = True,
        target_language: str = 'en'
    ) -> ComprehensiveNLResult:
        """종합적인 NL 요청 처리"""
        
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        
        # 1. 언어 감지 및 다국어 처리
        multilingual_result = await self.multilingual_processor.process_multilingual_input(
            description, target_language
        )
        
        processed_requirements = multilingual_result[0]
        language_metadata = multilingual_result[1]
        
        # 2. 컨텍스트 로드 및 업데이트
        conversation_context = await self.context_manager.get_conversation_context(
            session_id, user_id
        )
        
        # 3. 고급 분석 (선택적)
        advanced_analysis = None
        if enable_advanced_analysis:
            advanced_analysis = await self.advanced_integration.process_advanced_requirements(
                description, context
            )
        
        # 4. 컨텍스트 업데이트
        await self.context_manager.update_context(
            session_id,
            {
                "user_id": user_id,
                "role": "user",
                "content": description
            },
            extracted_info={
                "requirements": processed_requirements.__dict__,
                "language": language_metadata["original_language"],
                "advanced_analysis": advanced_analysis.__dict__ if advanced_analysis else None
            }
        )
        
        # 5. 성능 메트릭 수집
        processing_time = time.time() - start_time
        performance_metrics = self.performance_optimizer.get_performance_stats()
        performance_metrics["current_processing_time"] = processing_time
        
        # 6. 신뢰도 점수 계산
        confidence_score = self._calculate_comprehensive_confidence(
            processed_requirements,
            advanced_analysis,
            language_metadata
        )
        
        # 7. 다음 액션 결정
        next_actions = self._determine_next_actions(
            processed_requirements,
            advanced_analysis,
            confidence_score
        )
        
        return ComprehensiveNLResult(
            session_id=session_id,
            user_id=user_id,
            original_language=language_metadata["original_language"],
            processed_requirements=processed_requirements,
            advanced_analysis=advanced_analysis,
            context_updates={"session_updated": True},
            performance_metrics=performance_metrics,
            confidence_score=confidence_score,
            processing_time=processing_time,
            next_actions=next_actions
        )
    
    async def handle_realtime_feedback(
        self,
        session_id: str,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실시간 피드백 처리"""
        
        # 피드백 처리 (WebSocket 연결은 실제 구현에서 처리)
        # 여기서는 피드백 데이터 구조만 정의
        
        feedback_result = {
            "feedback_processed": True,
            "session_id": session_id,
            "updated_requirements": None,  # 실제로는 업데이트된 요구사항
            "confidence_change": 0.0
        }
        
        return feedback_result
    
    def _calculate_comprehensive_confidence(
        self,
        basic_requirements: Any,
        advanced_analysis: Optional[Any],
        language_metadata: Dict[str, Any]
    ) -> float:
        """종합 신뢰도 점수 계산"""
        
        # 기본 요구사항 신뢰도
        base_confidence = 0.8
        
        # 언어 처리 신뢰도
        language_confidence = 0.9 if language_metadata["original_language"] == "en" else 0.7
        
        # 고급 분석 신뢰도
        advanced_confidence = advanced_analysis.confidence_score if advanced_analysis else 0.6
        
        # 가중 평균
        overall_confidence = (
            base_confidence * 0.4 +
            language_confidence * 0.3 +
            advanced_confidence * 0.3
        )
        
        return min(overall_confidence, 1.0)
    
    def _determine_next_actions(
        self,
        basic_requirements: Any,
        advanced_analysis: Optional[Any],
        confidence_score: float
    ) -> List[str]:
        """다음 액션 결정"""
        
        actions = []
        
        # 신뢰도 기반 액션
        if confidence_score < 0.7:
            actions.append("request_clarification")
        
        # 요구사항 복잡도 기반
        if len(basic_requirements.technical_requirements) > 10:
            actions.append("break_down_requirements")
        
        # 고급 분석 기반
        if advanced_analysis:
            if len(advanced_analysis.prioritized_requirements) > 0:
                actions.append("proceed_to_ui_selection")
            
            if advanced_analysis.domain_analysis.domain != 'general':
                actions.append("apply_domain_specific_templates")
        
        # 기본 액션
        if not actions:
            actions.append("proceed_to_next_agent")
        
        return actions
    
    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        
        performance_stats = self.performance_optimizer.get_performance_stats()
        
        return {
            "initialized": self.initialized,
            "performance": performance_stats,
            "components": {
                "basic_agent": "active",
                "advanced_integration": "active",
                "performance_optimizer": "active",
                "context_manager": "active",
                "multilingual_processor": "active",
                "feedback_processor": "active"
            },
            "health_score": self._calculate_health_score(performance_stats)
        }
    
    def _calculate_health_score(self, performance_stats: Dict[str, Any]) -> float:
        """시스템 건강도 점수"""
        
        # 에러율 기반 점수 (낮을수록 좋음)
        error_score = max(0, 1 - performance_stats.get('error_rate', 0) * 10)
        
        # 캐시 적중률 기반 점수 (높을수록 좋음)
        cache_score = performance_stats.get('cache_hit_rate', 0)
        
        # 종합 점수
        health_score = (error_score * 0.6 + cache_score * 0.4)
        
        return min(health_score, 1.0)
    
    async def cleanup(self):
        """시스템 정리"""
        if self.initialized:
            await self.performance_optimizer.cleanup()
            self.initialized = False