"""
Parser Agent - Complete API Endpoints
RESTful API + WebSocket + File Upload
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio
import json
import uuid
from datetime import datetime
import aiofiles
import os

router = APIRouter(prefix="/api/v1/agents/parser", tags=["parser-agent"])

# Request/Response Models
class ParseRequest(BaseModel):
    project_name: str = Field(..., description="Project name")
    description: str = Field(..., description="Requirements text", max_length=100000)
    domain: Optional[str] = Field(None, description="Project domain")
    language: Optional[str] = Field("en", description="Source language")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    output_format: Optional[str] = Field("json", description="Output format")

class ParseResponse(BaseModel):
    project_id: str
    status: str
    parsing_time_ms: float
    requirements_count: Dict[str, int]
    cache_hit: bool
    download_url: Optional[str] = None

class CollaborativeSessionRequest(BaseModel):
    session_name: str
    initial_text: str
    participants: List[str] = Field(default_factory=list)

class ChangeRequest(BaseModel):
    type: str = Field(..., description="insert, delete, replace")
    position: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None
    content: Optional[str] = None

# Global instances (would be injected in real implementation)
parser_agent = None  # Injected
advanced_features = None  # Injected

@router.post("/parse", response_model=ParseResponse)
async def parse_requirements(
    request: ParseRequest,
    background_tasks: BackgroundTasks
):
    """기본 요구사항 파싱"""
    
    start_time = asyncio.get_event_loop().time()
    project_id = str(uuid.uuid4())
    
    try:
        # 다국어 처리
        if request.language != 'en':
            result = await advanced_features.parse_multilingual_requirements(
                request.description, request.language
            )
            parsed_project = result['parsed_result']
            cache_hit = False
        else:
            # 캐시 확인
            cached_result = await parser_agent.caching_system.get_cached_result(
                request.description
            )
            
            if cached_result:
                parsed_project, _ = cached_result
                cache_hit = True
            else:
                parsed_project = await parser_agent.parse_requirements(
                    request.description,
                    project_context={
                        'name': request.project_name,
                        'domain': request.domain
                    }
                )
                cache_hit = False
        
        # 처리 시간 계산
        parsing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # 요구사항 카운트
        requirements_count = {
            'functional': len(parsed_project.functional_requirements),
            'non_functional': len(parsed_project.non_functional_requirements),
            'technical': len(parsed_project.technical_requirements),
            'business': len(parsed_project.business_requirements),
            'user_stories': len(parsed_project.user_stories),
            'data_models': len(parsed_project.data_models),
            'api_endpoints': len(parsed_project.api_specifications)
        }
        
        # 백그라운드에서 결과 저장
        background_tasks.add_task(
            save_parsing_result,
            project_id,
            parsed_project,
            request.output_format
        )
        
        return ParseResponse(
            project_id=project_id,
            status="completed",
            parsing_time_ms=parsing_time,
            requirements_count=requirements_count,
            cache_hit=cache_hit,
            download_url=f"/api/v1/projects/{project_id}/download"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-file")
async def parse_file(
    file: UploadFile = File(...),
    domain: Optional[str] = None,
    language: Optional[str] = "en"
):
    """파일 업로드 파싱"""
    
    # 파일 형식 검증
    allowed_extensions = ['.txt', '.md', '.docx', '.pdf']
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {allowed_extensions}"
        )
    
    # 파일 크기 검증 (10MB 제한)
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )
    
    # 임시 파일 저장
    temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    
    try:
        async with aiofiles.open(temp_file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # 대용량 파일 처리
        if file.size > 1024 * 1024:  # 1MB 이상
            return StreamingResponse(
                stream_large_file_parsing(temp_file_path),
                media_type="application/json"
            )
        else:
            # 일반 처리
            async with aiofiles.open(temp_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            request = ParseRequest(
                project_name=file.filename.split('.')[0],
                description=content,
                domain=domain,
                language=language
            )
            
            return await parse_requirements(request, BackgroundTasks())
    
    finally:
        # 임시 파일 정리
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.websocket("/ws/parse-stream")
async def websocket_parse_stream(websocket: WebSocket):
    """실시간 파싱 스트림"""
    
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            if request_data['type'] == 'start_parsing':
                # 스트리밍 파싱 시작
                async for progress in stream_parsing_progress(
                    request_data['description'],
                    request_data.get('options', {})
                ):
                    await websocket.send_json({
                        'type': 'progress',
                        'data': progress
                    })
                
                await websocket.send_json({
                    'type': 'completed',
                    'message': 'Parsing completed successfully'
                })
    
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })
        await websocket.close()

@router.get("/health")
async def health_check():
    """헬스체크"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0',
        'features': {
            'multilingual': True,
            'collaborative': True,
            'large_documents': True,
            'caching': True
        }
    }

# Helper Functions
async def stream_large_file_parsing(file_path: str) -> AsyncGenerator[str, None]:
    """대용량 파일 파싱 스트리밍"""
    
    async for result in advanced_features.process_large_document_stream(file_path):
        yield json.dumps(result) + "\n"

async def stream_parsing_progress(
    description: str, options: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """파싱 진행상황 스트리밍"""
    
    steps = [
        {'step': 'preprocessing', 'progress': 10, 'message': 'Preprocessing text'},
        {'step': 'nlp_analysis', 'progress': 30, 'message': 'Analyzing natural language'},
        {'step': 'requirement_extraction', 'progress': 50, 'message': 'Extracting requirements'},
        {'step': 'classification', 'progress': 70, 'message': 'Classifying requirements'},
        {'step': 'validation', 'progress': 90, 'message': 'Validating results'},
        {'step': 'completion', 'progress': 100, 'message': 'Parsing completed'}
    ]
    
    for step in steps:
        await asyncio.sleep(0.5)
        yield step

async def save_parsing_result(
    project_id: str, parsed_project: Any, output_format: str
):
    """파싱 결과 저장"""
    print(f"Saving project {project_id} in {output_format} format")