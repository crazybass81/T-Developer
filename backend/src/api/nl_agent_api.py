from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..agents.implementations.nl_integration import NLInputAgentIntegration

router = APIRouter(prefix="/v1/agents/nl-input", tags=["NL Input Agent"])

# Request/Response Models
class ProcessRequest(BaseModel):
    description: str
    context: Optional[Dict[str, Any]] = None

class ClarificationResponse(BaseModel):
    original_requirements: Dict[str, Any]
    responses: Dict[str, Any]

class ProcessResponse(BaseModel):
    requirements: Dict[str, Any]
    processing_status: str
    confidence_score: float
    ambiguities: int
    clarification_needed: bool
    clarification_questions: Optional[List[Dict[str, Any]]] = None

# Initialize agent
nl_integration = NLInputAgentIntegration()

@router.post("/process", response_model=ProcessResponse)
async def process_description(request: ProcessRequest):
    """자연어 프로젝트 설명 처리"""
    try:
        result = await nl_integration.process_complete_request(
            inputs=[request.description],
            user_context=request.context
        )
        
        if result['processing_status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error_message'])
            
        return ProcessResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-multimodal")
async def process_multimodal(
    description: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    context: Optional[str] = Form(default=None)
):
    """멀티모달 입력 처리"""
    try:
        inputs = [description]
        
        # 파일 처리
        for file in files:
            content = await file.read()
            inputs.append(content)
        
        # 컨텍스트 파싱
        user_context = None
        if context:
            import json
            user_context = json.loads(context)
        
        result = await nl_integration.process_complete_request(
            inputs=inputs,
            user_context=user_context
        )
        
        if result['processing_status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error_message'])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clarify")
async def process_clarification(request: ClarificationResponse):
    """명확화 응답 처리"""
    try:
        result = await nl_integration.process_clarification_response(
            original_requirements=request.original_requirements,
            responses=request.responses
        )
        
        if result['processing_status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error_message'])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "agent": "NL Input Agent",
        "version": "1.0.0"
    }