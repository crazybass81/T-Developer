"""
T-Developer MVP Squad API
통합 API 엔드포인트
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import uuid
from datetime import datetime

from orchestration.agent_squad import AgentSquadOrchestrator, SquadConfiguration

app = FastAPI(
    title="T-Developer MVP API",
    description="AI-powered project generation from natural language",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 오케스트레이터
orchestrator = AgentSquadOrchestrator()


class ProjectGenerationRequest(BaseModel):
    """프로젝트 생성 요청"""
    user_input: str = Field(..., description="Natural language project description")
    user_id: Optional[str] = Field(None, description="User identifier")
    project_name: Optional[str] = Field("untitled", description="Project name")
    parallel_execution: Optional[bool] = Field(False, description="Enable parallel execution")
    save_intermediate: Optional[bool] = Field(True, description="Save intermediate results")
    enable_notifications: Optional[bool] = Field(True, description="Enable notifications")


class ProjectGenerationResponse(BaseModel):
    """프로젝트 생성 응답"""
    success: bool
    session_id: str
    download_links: List[Dict[str, Any]]
    project_manifest: Dict[str, Any]
    execution_time: float
    stages_completed: List[str]


class AsyncJobResponse(BaseModel):
    """비동기 작업 응답"""
    job_id: str
    status: str
    message: str


# 진행 중인 작업 추적
active_jobs = {}


@app.get("/")
async def root():
    """API 루트"""
    return {
        "name": "T-Developer MVP API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "generate": "/api/v1/generate",
            "generate_async": "/api/v1/generate/async",
            "status": "/api/v1/jobs/{job_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "t-developer-squad-api"
    }


@app.post("/api/v1/generate", response_model=ProjectGenerationResponse)
async def generate_project(request: ProjectGenerationRequest):
    """
    동기식 프로젝트 생성
    
    자연어 입력을 받아 완성된 프로젝트를 생성합니다.
    """
    try:
        # Squad 설정
        squad_config = SquadConfiguration(
            parallel_execution=request.parallel_execution,
            save_intermediate=request.save_intermediate,
            enable_notifications=request.enable_notifications
        )
        
        # 파이프라인 실행
        result = await orchestrator.execute_pipeline(
            user_input=request.user_input,
            user_id=request.user_id or str(uuid.uuid4()),
            project_name=request.project_name,
            squad_config=squad_config
        )
        
        return ProjectGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/async", response_model=AsyncJobResponse)
async def generate_project_async(
    request: ProjectGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    비동기식 프로젝트 생성
    
    장시간 실행되는 프로젝트 생성을 백그라운드에서 처리합니다.
    """
    job_id = str(uuid.uuid4())
    
    # 백그라운드 작업 추가
    background_tasks.add_task(
        execute_async_pipeline,
        job_id,
        request
    )
    
    # 작업 상태 초기화
    active_jobs[job_id] = {
        "status": "started",
        "started_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    return AsyncJobResponse(
        job_id=job_id,
        status="started",
        message="Project generation started. Check status at /api/v1/jobs/{job_id}"
    )


async def execute_async_pipeline(job_id: str, request: ProjectGenerationRequest):
    """백그라운드 파이프라인 실행"""
    try:
        active_jobs[job_id]["status"] = "processing"
        
        # Squad 설정
        squad_config = SquadConfiguration(
            parallel_execution=request.parallel_execution,
            save_intermediate=request.save_intermediate,
            enable_notifications=request.enable_notifications
        )
        
        # 파이프라인 실행
        result = await orchestrator.execute_pipeline(
            user_input=request.user_input,
            user_id=request.user_id or str(uuid.uuid4()),
            project_name=request.project_name,
            squad_config=squad_config
        )
        
        # 결과 저장
        active_jobs[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "result": result
        })
        
    except Exception as e:
        active_jobs[job_id].update({
            "status": "failed",
            "failed_at": datetime.now().isoformat(),
            "error": str(e)
        })


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    작업 상태 조회
    
    비동기 작업의 현재 상태를 확인합니다.
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return active_jobs[job_id]


@app.post("/api/v1/agents/{agent_name}/execute")
async def execute_single_agent(
    agent_name: str,
    request: Request
):
    """
    단일 에이전트 실행
    
    특정 에이전트만 개별적으로 실행합니다.
    """
    valid_agents = [
        "nl_input", "ui_selection", "parser", "component_decision",
        "match_rate", "search", "generation", "assembly", "download"
    ]
    
    if agent_name not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent name. Valid agents: {valid_agents}"
        )
    
    try:
        body = await request.json()
        
        # 에이전트 가져오기
        from orchestration.agent_squad import PipelineStage
        stage = PipelineStage(agent_name)
        agent = orchestrator.agents.get(stage)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # 에이전트 실행 (간단한 예시)
        # 실제로는 각 에이전트별 입력 처리 필요
        result = {"message": f"Agent {agent_name} executed", "input": body}
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/pipeline/stages")
async def get_pipeline_stages():
    """
    파이프라인 단계 정보
    
    전체 파이프라인의 단계별 정보를 반환합니다.
    """
    stages = [
        {
            "order": 1,
            "name": "nl_input",
            "description": "Natural Language Input Processing",
            "required_input": ["user_input"],
            "output": "ProjectRequirements"
        },
        {
            "order": 2,
            "name": "ui_selection",
            "description": "UI Framework Selection",
            "required_input": ["requirements"],
            "output": "UISelectionResult"
        },
        {
            "order": 3,
            "name": "parser",
            "description": "Requirements Parsing",
            "required_input": ["nl_result", "ui_result"],
            "output": "ParsedProject"
        },
        {
            "order": 4,
            "name": "component_decision",
            "description": "Component Decision Making",
            "required_input": ["parsed_project", "ui_selection"],
            "output": "TechnologyStack"
        },
        {
            "order": 5,
            "name": "match_rate",
            "description": "Match Rate Calculation",
            "required_input": ["requirements", "technology_stack"],
            "output": "MatchingResult"
        },
        {
            "order": 6,
            "name": "search",
            "description": "Component Search",
            "required_input": ["requirements", "technology_stack", "matching_result"],
            "output": "SearchResults"
        },
        {
            "order": 7,
            "name": "generation",
            "description": "Code Generation",
            "required_input": ["parsed_project", "technology_stack", "search_results"],
            "output": "GenerationResult"
        },
        {
            "order": 8,
            "name": "assembly",
            "description": "Project Assembly",
            "required_input": ["generation_result", "technology_stack"],
            "output": "AssemblyResult"
        },
        {
            "order": 9,
            "name": "download",
            "description": "Download Preparation",
            "required_input": ["assembly_result"],
            "output": "DownloadResult"
        }
    ]
    
    return {"stages": stages, "total": len(stages)}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """글로벌 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "path": request.url.path
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)