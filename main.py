"""
T-Developer API 서버

FastAPI 기반의 API 서버로, 작업 요청 및 Slack 이벤트를 처리합니다.
"""
import logging
import os
import time
import hmac
import hashlib
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.mao import MAO
from core.task import Task, TaskStatus
from config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('t-developer.log')
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="T-Developer API",
    description="T-Developer API 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 개발 서버 주소
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# MAO 인스턴스 생성
mao = MAO()

# API 모델
class TaskRequest(BaseModel):
    """작업 요청 모델"""
    request: str
    user_id: str = "web-user"
    project_id: str = None

class TaskResponse(BaseModel):
    """작업 응답 모델"""
    task_id: str
    status: str
    message: str = "Task received"
    
class ProjectRequest(BaseModel):
    """프로젝트 요청 모델"""
    name: str
    description: str = ""
    github_repo: str = None
    slack_channel: str = None
    
class ProjectResponse(BaseModel):
    """프로젝트 응답 모델"""
    project_id: str
    name: str
    status: str = "created"
    message: str = "Project created"

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """
    새로운 작업 생성
    
    Args:
        task_request: 작업 요청 정보
        background_tasks: 백그라운드 작업
        
    Returns:
        작업 응답 정보
    """
    logger.info(f"Received task request: {task_request.request}")
    
    # 비동기로 작업 처리
    task_id = mao.process_request_async(task_request.request, task_request.user_id)
    
    return TaskResponse(
        task_id=task_id,
        status="received"
    )

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """
    작업 조회
    
    Args:
        task_id: 작업 ID
        
    Returns:
        작업 정보
    """
    logger.info(f"Getting task: {task_id}")
    
    task = mao.task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return task.to_dict()

@app.get("/api/tasks/{task_id}/diff/{file_path:path}")
async def get_file_diff(task_id: str, file_path: str):
    """
    파일 diff 조회
    
    Args:
        task_id: 작업 ID
        file_path: 파일 경로
        
    Returns:
        파일 diff 정보
    """
    logger.info(f"Getting diff for task {task_id}, file: {file_path}")
    
    task = mao.task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if not task.diff_s3_key:
        raise HTTPException(status_code=404, detail=f"No diff available for task {task_id}")
    
    try:
        # S3에서 diff 파일 가져오기
        diff_content = mao.artifact_store.get_artifact(task.diff_s3_key)
        
        # 파일별 diff 추출
        # 간단한 구현: diff 파일에서 해당 파일에 대한 부분만 추출
        file_diff = ""
        in_target_file = False
        for line in diff_content.split('\n'):
            if line.startswith(f"diff --git a/{file_path} b/{file_path}"):
                in_target_file = True
                file_diff = line + "\n"
            elif in_target_file and line.startswith("diff --git"):
                in_target_file = False
            elif in_target_file:
                file_diff += line + "\n"
        
        if not file_diff:
            # 해당 파일에 대한 diff가 없는 경우
            if file_path in task.created_files:
                file_diff = f"// {file_path} - 새로 생성된 파일\n// 전체 diff를 확인하려면 PR을 참조하세요."
            else:
                file_diff = f"// {file_path} - 해당 파일의 diff를 찾을 수 없습니다."
        
        return {"diff": file_diff}
    except Exception as e:
        logger.error(f"Error getting diff for task {task_id}, file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting diff: {str(e)}")

@app.get("/api/tasks/{task_id}/plan")
async def get_task_plan(task_id: str):
    """
    작업 계획 조회
    
    Args:
        task_id: 작업 ID
        
    Returns:
        작업 계획 정보
    """
    logger.info(f"Getting plan for task: {task_id}")
    
    task = mao.task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if not task.plan_s3_key:
        raise HTTPException(status_code=404, detail=f"No plan available for task {task_id}")
    
    try:
        # S3에서 계획 파일 가져오기
        plan_content = mao.artifact_store.get_artifact(task.plan_s3_key)
        return json.loads(plan_content)
    except Exception as e:
        logger.error(f"Error getting plan for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting plan: {str(e)}")

@app.get("/api/tasks/{task_id}/test-log")
async def get_test_log(task_id: str):
    """
    테스트 로그 조회
    
    Args:
        task_id: 작업 ID
        
    Returns:
        테스트 로그 정보
    """
    logger.info(f"Getting test log for task: {task_id}")
    
    task = mao.task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    if not task.test_log_s3_key:
        raise HTTPException(status_code=404, detail=f"No test log available for task {task_id}")
    
    try:
        # S3에서 테스트 로그 파일 가져오기
        log_content = mao.artifact_store.get_artifact(task.test_log_s3_key)
        return {"log": log_content}
    except Exception as e:
        logger.error(f"Error getting test log for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting test log: {str(e)}")

@app.post("/api/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    """
    Slack 이벤트 처리
    
    Args:
        request: HTTP 요청
        background_tasks: 백그라운드 작업
        
    Returns:
        응답 정보
    """
    # Slack 서명 검증
    if settings.SLACK_SIGNING_SECRET:
        # 요청 본문 가져오기
        body_bytes = await request.body()
        body_text = body_bytes.decode()
        
        # 서명 헤더 가져오기
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        
        # 타임스탬프 검증 (재사용 공격 방지)
        if not timestamp or abs(time.time() - float(timestamp)) > 60 * 5:
            logger.warning("Slack request timestamp is invalid or too old")
            raise HTTPException(status_code=401, detail="Invalid timestamp")
        
        # 서명 검증
        if not signature:
            logger.warning("No Slack signature provided")
            raise HTTPException(status_code=401, detail="No signature provided")
        
        # 서명 계산
        sig_basestring = f"v0:{timestamp}:{body_text}"
        my_signature = "v0=" + hmac.new(
            settings.SLACK_SIGNING_SECRET.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # 서명 비교
        if not hmac.compare_digest(my_signature, signature):
            logger.warning("Invalid Slack signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 요청 본문 파싱
    body = await request.json()
    
    # 이벤트 유형 확인
    event_type = body.get("type")
    
    if event_type == "url_verification":
        # URL 검증 응답
        return {"challenge": body.get("challenge")}
    
    elif event_type == "event_callback":
        # 이벤트 콜백 처리
        event = body.get("event", {})
        
        # 메시지 이벤트 처리
        if event.get("type") == "message":
            # 봇 메시지 무시
            if event.get("bot_id"):
                return {"status": "ok", "message": "Bot message ignored"}
            
            # 메시지 텍스트 가져오기
            text = event.get("text", "")
            user = event.get("user", "unknown")
            
            # T-Developer 멘션 확인
            if text.startswith("<@T-Developer>:") or text.startswith("T-Developer:"):
                # 멘션 제거하고 요청 추출
                if text.startswith("<@T-Developer>:"):
                    request_text = text[len("<@T-Developer>:"):].strip()
                else:
                    request_text = text[len("T-Developer:"):].strip()
                
                # 비동기로 작업 처리
                task_id = mao.process_request_async(request_text, user)
                
                return {"status": "ok", "task_id": task_id}
    
    # 기타 이벤트는 무시
    return {"status": "ok"}

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project_request: ProjectRequest):
    """
    새로운 프로젝트 생성
    
    Args:
        project_request: 프로젝트 요청 정보
        
    Returns:
        프로젝트 응답 정보
    """
    logger.info(f"Creating project: {project_request.name}")
    
    # 프로젝트 ID 생성
    project_id = f"PROJ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    # 프로젝트 정보 저장 (실제 구현에서는 DynamoDB에 저장)
    # 현재는 임시 구현으로 로그만 남김
    logger.info(f"Project created: {project_id}, {project_request.name}")
    
    # 프로젝트 설정을 글로벌 컨텍스트에 반영 (실제 구현에서는 프로젝트별 설정 관리)
    # 현재는 임시 구현으로 로그만 남김
    if project_request.github_repo:
        logger.info(f"Setting GitHub repo: {project_request.github_repo}")
    if project_request.slack_channel:
        logger.info(f"Setting Slack channel: {project_request.slack_channel}")
    
    return ProjectResponse(
        project_id=project_id,
        name=project_request.name,
        status="created",
        message="Project created successfully"
    )

@app.get("/api/projects")
async def get_projects():
    """
    프로젝트 목록 조회
    
    Returns:
        프로젝트 목록
    """
    logger.info("Getting projects")
    
    # 임시 프로젝트 목록 (실제 구현에서는 DynamoDB에서 조회)
    projects = [
        {
            "project_id": "PROJ-20250101-12345678",
            "name": "GovChat",
            "description": "정부 지원사업 매칭 챗봇",
            "github_repo": "user/govchat",
            "slack_channel": "#govchat-dev",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]
    
    return projects

@app.get("/health")
async def health_check():
    """
    헬스 체크
    
    Returns:
        상태 정보
    """
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)