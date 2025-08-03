from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# Import the complete NL Input Agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.implementations.nl_input_agent_complete import NLInputAgent, ProjectRequirements

# API Models
class ProcessDescriptionRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=5000, description="Project description")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_id: Optional[str] = Field(None, description="User identifier")

class ProcessDescriptionResponse(BaseModel):
    success: bool
    project_type: str
    estimated_complexity: str
    functional_requirements: List[str]
    technical_requirements: List[Dict[str, Any]]
    non_functional_requirements: List[str]
    technology_preferences: Dict[str, Any]
    constraints: List[str]
    extracted_entities: Dict[str, Any]
    confidence_score: float
    ambiguities: List[str]
    processing_time_ms: float
    created_at: str

class HealthResponse(BaseModel):
    status: str
    agent_ready: bool
    timestamp: str

# Router setup
router = APIRouter(prefix="/api/nl-agent", tags=["NL Input Agent"])

# Global agent instance
nl_agent = None

async def get_nl_agent():
    """NL Agent 인스턴스 가져오기"""
    global nl_agent
    if nl_agent is None:
        nl_agent = NLInputAgent()
    return nl_agent

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        agent = await get_nl_agent()
        return HealthResponse(
            status="healthy",
            agent_ready=agent is not None,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            agent_ready=False,
            timestamp=datetime.now().isoformat()
        )

@router.post("/process", response_model=ProcessDescriptionResponse)
async def process_description(
    request: ProcessDescriptionRequest,
    agent: NLInputAgent = Depends(get_nl_agent)
):
    """프로젝트 설명 처리"""
    try:
        start_time = datetime.now()
        
        # NL Agent로 처리
        result = await agent.process_description(
            description=request.description,
            context=request.context
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        # 기술 요구사항 직렬화
        tech_reqs_serialized = [
            {
                "id": tr.id,
                "description": tr.description,
                "category": tr.category,
                "priority": tr.priority.value,
                "measurable_criteria": tr.measurable_criteria
            }
            for tr in result.technical_requirements
        ]
        
        return ProcessDescriptionResponse(
            success=True,
            project_type=result.project_type.value,
            estimated_complexity=result.estimated_complexity,
            functional_requirements=result.functional_requirements,
            technical_requirements=tech_reqs_serialized,
            non_functional_requirements=result.non_functional_requirements,
            technology_preferences=result.technology_preferences,
            constraints=result.constraints,
            extracted_entities=result.extracted_entities,
            confidence_score=result.confidence_score,
            ambiguities=result.ambiguities,
            processing_time_ms=processing_time,
            created_at=result.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@router.get("/capabilities")
async def get_capabilities():
    """에이전트 능력 정보"""
    return {
        "supported_project_types": [
            "web_application",
            "mobile_application", 
            "api_service",
            "cli_tool",
            "full_stack"
        ],
        "supported_languages": ["korean", "english"],
        "max_description_length": 5000,
        "features": [
            "project_type_classification",
            "requirement_extraction",
            "technology_stack_analysis",
            "entity_recognition",
            "complexity_estimation",
            "ambiguity_detection"
        ],
        "performance": {
            "average_processing_time_ms": 500,
            "max_concurrent_requests": 100
        }
    }

@router.post("/validate")
async def validate_description(request: ProcessDescriptionRequest):
    """설명 유효성 검사"""
    try:
        agent = await get_nl_agent()
        result = await agent.process_description(request.description)
        
        validation_result = {
            "is_valid": True,
            "confidence_score": result.confidence_score,
            "warnings": [],
            "suggestions": []
        }
        
        # 신뢰도 기반 검증
        if result.confidence_score < 0.3:
            validation_result["warnings"].append("Very low confidence in analysis")
            validation_result["suggestions"].append("Please provide more detailed description")
        elif result.confidence_score < 0.6:
            validation_result["warnings"].append("Low confidence in analysis")
            validation_result["suggestions"].append("Consider adding more technical details")
        
        # 모호성 검사
        if result.ambiguities:
            validation_result["warnings"].extend(result.ambiguities)
            validation_result["suggestions"].append("Please clarify the ambiguous requirements")
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )

@router.get("/examples")
async def get_examples():
    """예시 프로젝트 설명들"""
    return {
        "examples": [
            {
                "title": "Simple Web App",
                "description": "간단한 할일 관리 웹 애플리케이션을 만들어주세요. 사용자는 할일을 추가, 수정, 삭제할 수 있어야 합니다.",
                "expected_type": "web_application",
                "complexity": "simple"
            },
            {
                "title": "E-commerce Platform", 
                "description": "React와 Node.js를 사용한 이커머스 플랫폼입니다. 사용자 인증, 상품 관리, 장바구니, 결제 기능이 필요하고 PostgreSQL을 사용합니다. 10,000명의 동시 사용자를 지원해야 합니다.",
                "expected_type": "web_application",
                "complexity": "complex"
            },
            {
                "title": "Mobile Social App",
                "description": "iOS와 Android를 지원하는 소셜 미디어 앱을 개발해주세요. 사진 공유, 실시간 채팅, 푸시 알림 기능이 필요합니다.",
                "expected_type": "mobile_application", 
                "complexity": "medium"
            },
            {
                "title": "REST API Service",
                "description": "사용자 관리를 위한 RESTful API 서비스입니다. JWT 인증, CRUD 작업, 데이터 검증 기능이 포함되어야 합니다.",
                "expected_type": "api_service",
                "complexity": "medium"
            }
        ]
    }

# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(
        status_code=400,
        detail=f"Invalid input: {str(exc)}"
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )