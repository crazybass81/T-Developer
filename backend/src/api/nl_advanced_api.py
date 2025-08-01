from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio

from ..agents.implementations.nl_advanced_integration import AdvancedNLIntegration
from ..agents.implementations.nl_performance_optimizer import NLPerformanceOptimizer

router = APIRouter(prefix="/api/v1/agents/nl-advanced", tags=["NL Advanced"])

# 전역 인스턴스
advanced_nl = AdvancedNLIntegration()
optimizer = NLPerformanceOptimizer()

class AdvancedNLRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None
    enable_caching: bool = True
    enable_batching: bool = False
    include_domain_analysis: bool = True
    include_intent_analysis: bool = True
    include_prioritization: bool = True

class AdvancedNLResponse(BaseModel):
    basic_requirements: Dict[str, Any]
    domain_analysis: Optional[Dict[str, Any]] = None
    intent_analysis: Optional[Dict[str, Any]] = None
    prioritized_requirements: Optional[List[Dict[str, Any]]] = None
    confidence_score: float
    processing_time: float
    recommendations: List[str]
    performance_metrics: Dict[str, Any]

@router.on_event("startup")
async def startup_event():
    """API 시작 시 초기화"""
    await optimizer.initialize()

@router.on_event("shutdown")
async def shutdown_event():
    """API 종료 시 정리"""
    await optimizer.cleanup()

@router.post("/process", response_model=AdvancedNLResponse)
async def process_advanced_requirements(request: AdvancedNLRequest):
    """고급 요구사항 처리"""
    
    try:
        # 최적화된 처리
        result = await optimizer.optimize_processing(
            description=request.description,
            processor_func=lambda desc: advanced_nl.process_advanced_requirements(
                desc, request.context
            ),
            use_cache=request.enable_caching,
            use_batching=request.enable_batching
        )
        
        # 응답 구성
        response_data = {
            "basic_requirements": result.basic_requirements.__dict__,
            "confidence_score": result.confidence_score,
            "processing_time": result.processing_time,
            "recommendations": result.recommendations,
            "performance_metrics": optimizer.get_performance_stats()
        }
        
        # 선택적 분석 결과 포함
        if request.include_domain_analysis:
            response_data["domain_analysis"] = result.domain_analysis.__dict__
        
        if request.include_intent_analysis:
            response_data["intent_analysis"] = {
                "primary": result.intent_analysis.primary.value,
                "secondary": [intent.value for intent in result.intent_analysis.secondary],
                "confidence": result.intent_analysis.confidence,
                "business_goals": [goal.__dict__ for goal in result.intent_analysis.business_goals],
                "technical_goals": [goal.__dict__ for goal in result.intent_analysis.technical_goals],
                "constraints": result.intent_analysis.constraints
            }
        
        if request.include_prioritization:
            response_data["prioritized_requirements"] = [
                {
                    "requirement": req.requirement.__dict__,
                    "priority_score": req.priority_score,
                    "priority_factors": req.priority_factors,
                    "dependencies": req.dependencies,
                    "estimated_effort": req.estimated_effort,
                    "business_value": req.business_value,
                    "risk_level": req.risk_level,
                    "recommended_sprint": req.recommended_sprint
                }
                for req in result.prioritized_requirements
            ]
        
        return AdvancedNLResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/stats")
async def get_performance_stats():
    """성능 통계 조회"""
    return optimizer.get_performance_stats()

@router.post("/performance/clear-cache")
async def clear_cache():
    """캐시 정리"""
    optimizer.result_cache.clear()
    return {"message": "Cache cleared successfully"}

@router.get("/health")
async def health_check():
    """헬스 체크"""
    stats = optimizer.get_performance_stats()
    
    # 헬스 상태 판단
    is_healthy = (
        stats['error_rate'] < 0.05 and  # 5% 미만 에러율
        stats['cache_hit_rate'] > 0.3   # 30% 이상 캐시 적중률
    )
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "stats": stats,
        "timestamp": asyncio.get_event_loop().time()
    }