"""API endpoint for upgrade orchestrator.

UI와 업그레이드 오케스트레이터를 연결하는 API입니다.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=4)

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig,
    UpgradeReport
)
from backend.packages.orchestrator.newbuild_orchestrator import (
    NewBuildOrchestrator,
    NewBuildConfig
)
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType

app = FastAPI(title="T-Developer Upgrade API", version="2.0.0")

# 글로벌 오케스트레이터 인스턴스
orchestrator: Optional[UpgradeOrchestrator] = None
memory_hub: Optional[MemoryHub] = None


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트."""
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/test")
async def test_endpoint():
    """테스트 엔드포인트 - 즉시 반환."""
    return {"status": "ok", "message": "Test successful"}


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """작업 상태 조회."""
    global memory_hub
    
    if not memory_hub:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # 상태 조회
    status_data = await memory_hub.read(
        ContextType.O_CTX,
        f"task_{task_id}_status"
    )
    
    if not status_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return UpgradeStatus(
        task_id=task_id,
        status=status_data.get("status", "unknown"),
        progress=status_data.get("progress", 0.0),
        current_phase=status_data.get("current_phase"),
        message=status_data.get("message")
    )


@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """작업 결과 조회."""
    global memory_hub
    
    if not memory_hub:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # 결과 조회
    result_data = await memory_hub.read(
        ContextType.O_CTX,
        f"task_{task_id}_result"
    )
    
    if not result_data:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return result_data


class UpgradeRequest(BaseModel):
    """업그레이드 요청 모델."""
    
    requirements: str  # 자연어 요구사항
    project_path: str  # 분석할 프로젝트 경로
    orchestrator_type: str = "upgrade"  # upgrade or newbuild
    enable_dynamic_analysis: bool = False  # 동적 분석 활성화
    include_behavior_analysis: bool = True  # 행동 분석 포함
    generate_impact_matrix: bool = True  # 영향도 매트릭스 생성


class UpgradeStatus(BaseModel):
    """업그레이드 상태 응답."""
    
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 ~ 1.0
    current_phase: Optional[str] = None
    message: Optional[str] = None
    result_path: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화."""
    global memory_hub
    memory_hub = MemoryHub()
    await memory_hub.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 정리."""
    global orchestrator, memory_hub
    if orchestrator:
        if hasattr(orchestrator, 'shutdown'):
            await orchestrator.shutdown()
    if memory_hub:
        if hasattr(memory_hub, 'shutdown'):
            await memory_hub.shutdown()


@app.post("/upgrade", response_model=UpgradeStatus)
async def start_upgrade_analysis(
    request: UpgradeRequest,
    background_tasks: BackgroundTasks
) -> UpgradeStatus:
    """업그레이드 분석 시작.
    
    Args:
        request: 업그레이드 요청
        background_tasks: 백그라운드 작업
        
    Returns:
        작업 상태
    """
    global orchestrator
    
    # NewBuilder의 경우 빈 폴더 생성
    if request.orchestrator_type == "newbuild":
        if not os.path.exists(request.project_path):
            os.makedirs(request.project_path, exist_ok=True)
    else:
        # Upgrade의 경우 기존 프로젝트 검증
        if not os.path.exists(request.project_path):
            raise HTTPException(status_code=400, detail="Project path does not exist")
        
        if not os.path.isdir(request.project_path):
            raise HTTPException(status_code=400, detail="Project path is not a directory")
    
    # 작업 ID 생성
    prefix = "newbuild" if request.orchestrator_type == "newbuild" else "upgrade"
    task_id = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 오케스트레이터 생성 (초기화는 백그라운드에서)
    if request.orchestrator_type == "newbuild":
        config = NewBuildConfig(
            project_path=request.project_path,
            output_dir=f"/tmp/t-developer/reports/{task_id}"
        )
        orchestrator = NewBuildOrchestrator(config)
    else:
        config = UpgradeConfig(
            project_path=request.project_path,
            output_dir=f"/tmp/t-developer/reports/{task_id}",
            enable_dynamic_analysis=request.enable_dynamic_analysis,
            include_behavior_analysis=request.include_behavior_analysis,
            generate_impact_matrix=request.generate_impact_matrix
        )
        orchestrator = UpgradeOrchestrator(config)
    
    # ThreadPoolExecutor를 사용하여 백그라운드에서 실행
    # 새로운 이벤트 루프에서 실행하여 충돌 방지
    executor.submit(
        run_analysis_wrapper,
        task_id,
        orchestrator,
        request.requirements
    )
    
    # 초기 상태 저장
    await memory_hub.write(
        ContextType.O_CTX,
        f"task_{task_id}_status",
        {
            "status": "running",
            "progress": 0.0,
            "current_phase": "initialization",
            "started_at": datetime.now().isoformat()
        },
        ttl_seconds=86400
    )
    
    return UpgradeStatus(
        task_id=task_id,
        status="running",
        progress=0.0,
        current_phase="initialization",
        message="Analysis started"
    )


def run_analysis_wrapper(task_id: str, orchestrator, requirements: str):
    """백그라운드 태스크 실행을 위한 동기 래퍼.
    
    새로운 이벤트 루프를 생성하여 비동기 함수를 실행합니다.
    """
    # 새로운 이벤트 루프 생성
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 비동기 함수 실행
        loop.run_until_complete(
            run_analysis_with_init_async(task_id, orchestrator, requirements)
        )
    finally:
        loop.close()


async def run_analysis_with_init_async(task_id: str, orchestrator, requirements: str):
    """백그라운드에서 초기화 후 분석 실행 (비동기)."""
    try:
        print(f"[{task_id}] Starting initialization...")
        # 오케스트레이터 초기화
        await orchestrator.initialize()
        print(f"[{task_id}] Initialization complete, starting analysis...")
        
        # 분석 실행
        await run_analysis(task_id, orchestrator, requirements)
        print(f"[{task_id}] Analysis complete")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        
        # 에러 저장
        await memory_hub.write(
            ContextType.O_CTX,
            f"task_{task_id}_status",
            {
                "status": "failed",
                "progress": 0.0,
                "current_phase": "initialization_error",
                "message": str(e),
                "error_detail": error_detail,
                "failed_at": datetime.now().isoformat()
            },
            ttl_seconds=86400
        )
        
        print(f"Task {task_id} initialization failed: {error_detail}")


async def run_analysis(task_id: str, orchestrator, requirements: str):
    """백그라운드에서 분석 실행.
    
    Args:
        task_id: 작업 ID
        orchestrator: 오케스트레이터
        requirements: 요구사항
    """
    try:
        print(f"[{task_id}] Starting orchestrator execution...")
        # 오케스트레이터 타입에 따라 실행
        if isinstance(orchestrator, NewBuildOrchestrator):
            print(f"[{task_id}] Running NewBuildOrchestrator.build()...")
            # NewBuilder는 build 사용
            report = await orchestrator.build(requirements)
        else:
            print(f"[{task_id}] Running UpgradeOrchestrator.analyze()...")
            # Upgrade는 analyze 사용
            report = await orchestrator.analyze(requirements)
        
        print(f"[{task_id}] Orchestrator execution complete")
        
        # 결과 저장
        await memory_hub.write(
            ContextType.O_CTX,
            f"task_{task_id}_status",
            {
                "status": "completed",
                "progress": 1.0,
                "current_phase": "completed",
                "completed_at": datetime.now().isoformat(),
                "result_path": orchestrator.config.output_dir
            },
            ttl_seconds=86400
        )
        
        # 리포트 저장
        if hasattr(report, '__dict__'):
            report_data = report.__dict__
        else:
            report_data = report if isinstance(report, dict) else {"result": str(report)}
            
        await memory_hub.write(
            ContextType.O_CTX,
            f"task_{task_id}_report",
            report_data,
            ttl_seconds=86400 * 7
        )
        
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        
        # 에러 저장
        await memory_hub.write(
            ContextType.O_CTX,
            f"task_{task_id}_status",
            {
                "status": "failed",
                "progress": 0.0,
                "current_phase": "error",
                "message": str(e),
                "error_detail": error_detail,
                "failed_at": datetime.now().isoformat()
            },
            ttl_seconds=86400
        )
        
        # 에러 로그 출력
        print(f"Task {task_id} failed: {error_detail}")


@app.get("/api/upgrade/status/{task_id}", response_model=UpgradeStatus)
async def get_upgrade_status(task_id: str) -> UpgradeStatus:
    """업그레이드 분석 상태 조회.
    
    Args:
        task_id: 작업 ID
        
    Returns:
        작업 상태
    """
    # 메모리에서 상태 조회
    status_data = await memory_hub.read(
        ContextType.O_CTX,
        f"task_{task_id}_status"
    )
    
    if not status_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return UpgradeStatus(
        task_id=task_id,
        status=status_data.get("status", "unknown"),
        progress=status_data.get("progress", 0.0),
        current_phase=status_data.get("current_phase"),
        message=status_data.get("error") if status_data.get("status") == "failed" else None,
        result_path=status_data.get("result_path")
    )


@app.get("/api/upgrade/report/{task_id}")
async def get_upgrade_report(task_id: str) -> Dict[str, Any]:
    """업그레이드 분석 리포트 조회.
    
    Args:
        task_id: 작업 ID
        
    Returns:
        분석 리포트
    """
    # 메모리에서 리포트 조회
    report_data = await memory_hub.read(
        ContextType.O_CTX,
        f"task_{task_id}_report"
    )
    
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report_data


@app.get("/api/upgrade/document/{task_id}/{doc_name}")
async def get_document(task_id: str, doc_name: str) -> FileResponse:
    """생성된 문서 조회.
    
    Args:
        task_id: 작업 ID
        doc_name: 문서 이름 (1_Goal.md, 2_CurrentState.md, 3_Plan.md, etc.)
        
    Returns:
        문서 파일
    """
    # 상태에서 결과 경로 조회
    status_data = await memory_hub.read(
        ContextType.O_CTX,
        f"task_{task_id}_status"
    )
    
    if not status_data or not status_data.get("result_path"):
        raise HTTPException(status_code=404, detail="Task or result not found")
    
    # 문서 경로 구성
    doc_path = Path(status_data["result_path"]) / doc_name
    
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 파일 타입에 따른 MIME 타입 설정
    media_type = "text/plain"
    if doc_name.endswith(".md"):
        media_type = "text/markdown"
    elif doc_name.endswith(".html"):
        media_type = "text/html"
    elif doc_name.endswith(".json"):
        media_type = "application/json"
    
    return FileResponse(
        path=str(doc_path),
        media_type=media_type,
        filename=doc_name
    )


@app.get("/api/upgrade/list")
async def list_analyses() -> Dict[str, Any]:
    """모든 분석 작업 목록 조회.
    
    Returns:
        작업 목록
    """
    # 메모리에서 모든 작업 조회
    tasks = []
    
    # O_CTX에서 task_* 패턴으로 저장된 모든 작업 조회
    # 실제 구현에서는 메모리 허브의 scan 기능 필요
    # 여기서는 예시로 최근 작업만 반환
    
    latest_path = await memory_hub.read(
        ContextType.O_CTX,
        "latest_report_path"
    )
    
    if latest_path:
        # summary.json 읽기
        summary_path = Path(latest_path) / "summary.json"
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                tasks.append(summary)
    
    return {
        "tasks": tasks,
        "total": len(tasks)
    }


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """헬스 체크.
    
    Returns:
        상태 정보
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)