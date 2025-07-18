"""
T-Developer 메인 애플리케이션

이 모듈은 T-Developer 시스템의 진입점으로, 웹 서버를 실행하고 API 엔드포인트를 제공합니다.
"""
import logging
import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.mao import MAO
from config import settings
from context.dynamo.project_store import ProjectStore

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('t-developer.log')
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="T-Developer API",
    description="T-Developer 시스템의 API 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 구현에서는 허용할 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MAO 인스턴스 생성
mao = MAO()

# ProjectStore 인스턴스 생성
project_store = ProjectStore()

# 요청 모델
class TaskRequest(BaseModel):
    """작업 요청 모델"""
    request: str
    user_id: str
    project_id: Optional[str] = None

# 응답 모델
class TaskResponse(BaseModel):
    """작업 응답 모델"""
    task_id: str
    status: str
    message: str

# 프로젝트 요청 모델
class ProjectRequest(BaseModel):
    """프로젝트 생성 요청 모델"""
    name: str
    description: str
    github_repo: str
    slack_channel: str

# 프로젝트 응답 모델
class ProjectResponse(BaseModel):
    """프로젝트 응답 모델"""
    project_id: str
    name: str
    description: str
    github_repo: str
    slack_channel: str

# API 엔드포인트
@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest):
    """
    새 작업 생성 엔드포인트
    
    Args:
        task_request: 작업 요청 정보
        
    Returns:
        작업 응답 정보
    """
    logger.info(f"Received task request: {task_request.request}")
    
    try:
        # MAO에 작업 비동기 처리 요청
        task_id = mao.process_request_async(task_request.request, task_request.user_id, task_request.project_id)
        
        return TaskResponse(
            task_id=task_id,
            status="received",
            message="Task received and processing started"
        )
    except Exception as e:
        logger.error(f"Error processing task request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """
    작업 상태 조회 엔드포인트
    
    Args:
        task_id: 조회할 작업 ID
        
    Returns:
        작업 상태 정보
    """
    logger.info(f"Getting task status for {task_id}")
    
    try:
        # 작업 상태 조회
        task = mao.task_store.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Task 객체의 모든 필드를 디셔너리로 변환
        task_dict = task.to_dict()
        
        # None 값은 제외
        return {k: v for k, v in task_dict.items() if v is not None}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")

@app.get("/api/tasks/{task_id}/diff")
async def get_task_diff(task_id: str):
    """
    작업의 전체 diff 조회 엔드포인트
    
    Args:
        task_id: 조회할 작업 ID
        
    Returns:
        diff 텍스트
    """
    logger.info(f"Getting diff for task {task_id}")
    
    try:
        # 작업 정보 조회
        task = mao.task_store.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if not task.diff_s3_key:
            raise HTTPException(status_code=404, detail=f"No diff found for task {task_id}")
        
        # S3에서 diff 파일 가져오기
        diff_text = mao.artifact_store.get_artifact(task.diff_s3_key)
        
        return {"diff": diff_text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting diff for task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting diff: {str(e)}")

@app.get("/api/tasks/{task_id}/diff/{file_path:path}")
async def get_file_diff(task_id: str, file_path: str):
    """
    특정 파일의 diff 조회 엔드포인트
    
    Args:
        task_id: 조회할 작업 ID
        file_path: 파일 경로
        
    Returns:
        해당 파일의 diff 텍스트
    """
    logger.info(f"Getting diff for file {file_path} in task {task_id}")
    
    try:
        # 작업 정보 조회
        task = mao.task_store.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if not task.diff_s3_key:
            raise HTTPException(status_code=404, detail=f"No diff found for task {task_id}")
        
        # S3에서 diff 파일 가져오기
        diff_text = mao.artifact_store.get_artifact(task.diff_s3_key)
        
        # diff 텍스트에서 해당 파일의 diff 부분만 추출
        file_diff = extract_file_diff(diff_text, file_path)
        
        if not file_diff:
            raise HTTPException(status_code=404, detail=f"No diff found for file {file_path} in task {task_id}")
        
        return {"diff": file_diff}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting diff for file {file_path} in task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting file diff: {str(e)}")

@app.get("/api/tasks/{task_id}/plan")
async def get_task_plan(task_id: str):
    """
    작업의 계획 조회 엔드포인트
    
    Args:
        task_id: 조회할 작업 ID
        
    Returns:
        계획 JSON
    """
    logger.info(f"Getting plan for task {task_id}")
    
    try:
        # 작업 정보 조회
        task = mao.task_store.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if not task.plan_s3_key:
            raise HTTPException(status_code=404, detail=f"No plan found for task {task_id}")
        
        # S3에서 계획 파일 가져오기
        plan_text = mao.artifact_store.get_artifact(task.plan_s3_key)
        
        # JSON 파싱
        try:
            plan_json = json.loads(plan_text)
            return plan_json
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 그대로 반환
            return {"plan": plan_text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan for task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting plan: {str(e)}")

@app.get("/api/tasks/{task_id}/test-log")
async def get_task_test_log(task_id: str):
    """
    작업의 테스트 로그 조회 엔드포인트
    
    Args:
        task_id: 조회할 작업 ID
        
    Returns:
        테스트 로그 텍스트
    """
    logger.info(f"Getting test log for task {task_id}")
    
    try:
        # 작업 정보 조회
        task = mao.task_store.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if not task.test_log_s3_key:
            raise HTTPException(status_code=404, detail=f"No test log found for task {task_id}")
        
        # S3에서 테스트 로그 파일 가져오기
        test_log = mao.artifact_store.get_artifact(task.test_log_s3_key)
        
        return {"log": test_log}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting test log for task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting test log: {str(e)}")

def extract_file_diff(diff_text: str, file_path: str) -> str:
    """
    diff 텍스트에서 특정 파일의 diff 부분만 추출
    
    Args:
        diff_text: 전체 diff 텍스트
        file_path: 추출할 파일 경로
        
    Returns:
        해당 파일의 diff 텍스트
    """
    # diff 텍스트를 줄 단위로 분할
    lines = diff_text.split('\n')
    
    # 파일별 diff 부분을 구분하는 패턴
    file_diff_start = None
    file_diff_end = None
    
    # 해당 파일의 diff 부분 찾기
    for i, line in enumerate(lines):
        # diff --git 로 시작하는 줄이 파일의 시작점
        if line.startswith(f"diff --git") and file_path in line:
            file_diff_start = i
        # 다음 파일의 diff 시작점이나 끝까지 도달한 경우
        elif file_diff_start is not None and line.startswith("diff --git"):
            file_diff_end = i
            break
    
    # 해당 파일의 diff가 없는 경우
    if file_diff_start is None:
        return ""
    
    # 마지막 파일인 경우
    if file_diff_end is None:
        file_diff_end = len(lines)
    
    # 해당 파일의 diff 부분만 추출
    file_diff_lines = lines[file_diff_start:file_diff_end]
    
    return "\n".join(file_diff_lines)

@app.post("/api/slack/events")
async def slack_events(request: Request):
    """
    Slack 이벤트 처리 엔드포인트
    
    Args:
        request: HTTP 요청 객체
        
    Returns:
        응답 메시지
    """
    try:
        # Slack 서명 검증
        if settings.SLACK_SIGNING_SECRET:
            import hmac
            import hashlib
            import time
            
            # 요청 본문 가져오기
            body_bytes = await request.body()
            body_text = body_bytes.decode()
            
            # 서명 헤더 가져오기
            timestamp = request.headers.get("X-Slack-Request-Timestamp")
            signature = request.headers.get("X-Slack-Signature")
            
            # 타임스태프 검증 (재사용 공격 방지)
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
        
        # Slack 이벤트 유형 확인
        event_type = body.get("type")
        
        # URL 검증 이벤트 처리
        if event_type == "url_verification":
            return {"challenge": body.get("challenge")}
        
        # 메시지 이벤트 처리
        if event_type == "event_callback":
            event = body.get("event", {})
            
            # 메시지 이벤트인 경우
            if event.get("type") == "message":
                text = event.get("text", "")
                user = event.get("user", "unknown")
                channel = event.get("channel", "")
                bot_id = event.get("bot_id")
                
                # 봇 자신의 메시지는 무시
                if bot_id:
                    logger.debug(f"Ignoring bot message from bot_id: {bot_id}")
                    return {"status": "ok"}
                
                # T-Developer 호출 확인 (예: "@T-Developer: 작업 요청")
                # 멘션이 문장 시작부에 있거나 콜론으로 구분되는 경우만 처리
                if text.startswith("<@") and ">:" in text or text.startswith("T-Developer:"):
                    # 작업 요청 추출
                    request_text = text.split(":", 1)[1].strip() if ":" in text else text.replace("@T-Developer", "").strip()
                    
                    # 프로젝트 ID 가져오기 (없으면 기본 프로젝트 사용)
                    projects = project_store.list_projects()
                    project_id = None
                    if projects:
                        project_id = projects[0].get('project_id')
                    
                    # MAO에 작업 비동기 처리 요청
                    task_id = mao.process_request_async(request_text, user, project_id)
                    
                    return {"status": "ok", "task_id": task_id}
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing Slack event: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project_request: ProjectRequest):
    """
    새 프로젝트 생성 엔드포인트
    
    Args:
        project_request: 프로젝트 생성 요청 정보
        
    Returns:
        생성된 프로젝트 정보
    """
    logger.info(f"Received project creation request: {project_request.name}")
    
    try:
        # 프로젝트 데이터 준비
        project_data = {
            "name": project_request.name,
            "description": project_request.description,
            "github_repo": project_request.github_repo,
            "slack_channel": project_request.slack_channel,
            "created_at": datetime.now().isoformat()
        }
        
        # 프로젝트 저장
        project_id = project_store.save_project(project_data)
        
        # 글로벌 컨텍스트 업데이트 (프로젝트 설명을 글로벌 컨텍스트로 사용)
        global_context = {
            "project_name": project_request.name,
            "description": project_request.description,
            "framework": "FastAPI",  # 기본값
            "coding_style": "PEP8",  # 기본값
            "test_framework": "pytest"  # 기본값
        }
        mao.task_store.save_task({
            "task_id": "GLOBAL_CONTEXT",
            "request": f"Global context for {project_request.name}",
            "user_id": "system",
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "context": global_context
        })
        
        # 응답 반환
        return ProjectResponse(
            project_id=project_id,
            name=project_request.name,
            description=project_request.description,
            github_repo=project_request.github_repo,
            slack_channel=project_request.slack_channel
        )
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@app.get("/api/projects", response_model=List[ProjectResponse])
async def list_projects():
    """
    프로젝트 목록 조회 엔드포인트
    
    Returns:
        프로젝트 목록
    """
    logger.info("Getting project list")
    
    try:
        # 프로젝트 목록 조회
        projects = project_store.list_projects()
        
        # 응답 모델로 변환
        return [
            ProjectResponse(
                project_id=project.get("project_id", ""),
                name=project.get("name", ""),
                description=project.get("description", ""),
                github_repo=project.get("github_repo", ""),
                slack_channel=project.get("slack_channel", "")
            )
            for project in projects
        ]
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """
    프로젝트 정보 조회 엔드포인트
    
    Args:
        project_id: 조회할 프로젝트 ID
        
    Returns:
        프로젝트 정보
    """
    logger.info(f"Getting project {project_id}")
    
    try:
        # 프로젝트 정보 조회
        project = project_store.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # 응답 모델로 변환
        return ProjectResponse(
            project_id=project.get("project_id", ""),
            name=project.get("name", ""),
            description=project.get("description", ""),
            github_repo=project.get("github_repo", ""),
            slack_channel=project.get("slack_channel", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")

@app.get("/health")
async def health_check():
    """
    상태 확인 엔드포인트
    
    Returns:
        상태 정보
    """
    return {"status": "ok", "version": "1.0.0"}

# 메인 함수
def main():
    """애플리케이션 실행"""
    logger.info("Starting T-Developer API server")
    
    # 환경 변수에서 호스트 및 포트 가져오기
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # 서버 실행
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()