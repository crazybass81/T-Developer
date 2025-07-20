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
import requests
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
# S3 웹사이트 오리진 허용
def get_allowed_origins():
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "*",  # 모든 오리진 허용 (동적 포트 할당을 위해)
    ]
    
    # S3 버킷 웹사이트 오리진 추가
    bucket_name = os.environ.get("FRONTEND_BUCKET_NAME", "tdeveloper-frontend")
    regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ap-northeast-2"]
    
    for region in regions:
        origins.append(f"http://{bucket_name}.s3-website-{region}.amazonaws.com")
        origins.append(f"http://{bucket_name}.s3-website.{region}.amazonaws.com")
    
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
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

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project_request: ProjectRequest):
    """
    새로운 프로젝트 생성
    
    Args:
        project_request: 프로젝트 요청 정보
        
    Returns:
        프로젝트 응답 정보
    """
    logger.info(f"Received project creation request: {project_request.name}")
    
    # 프로젝트 ID 생성
    project_id = f"PROJ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    try:
        # 프로젝트 저장
        from context.dynamo.project_store import ProjectStore
        project_store = ProjectStore()
        
        project = {
            "project_id": project_id,
            "name": project_request.name,
            "description": project_request.description,
            "github_repo": project_request.github_repo,
            "slack_channel": project_request.slack_channel,
            "created_at": datetime.now().isoformat()
        }
        
        project_store.save_project(project)
        logger.info(f"Project created: {project_id}")
        
        # 프로젝트 설명을 글로벌 컨텍스트에 추가 (선택사항)
        try:
            global_context = mao.task_store.get_global_context()
            global_context["project_description"] = project_request.description
            if project_request.github_repo:
                global_context["github_repo"] = project_request.github_repo
            mao.task_store.save_global_context(global_context)
            logger.info("Updated global context with project information")
        except Exception as e:
            logger.warning(f"Failed to update global context: {e}")
        
        return ProjectResponse(
            project_id=project_id,
            name=project_request.name,
            status="created",
            message="Project created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@app.get("/api/projects")
async def get_projects():
    """
    프로젝트 목록 조회
    
    Returns:
        프로젝트 목록
    """
    logger.info("Getting projects list")
    
    try:
        from context.dynamo.project_store import ProjectStore
        project_store = ProjectStore()
        projects = project_store.list_projects()
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting projects: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """
    프로젝트 조회
    
    Args:
        project_id: 프로젝트 ID
        
    Returns:
        프로젝트 정보
    """
    logger.info(f"Getting project: {project_id}")
    
    try:
        from context.dynamo.project_store import ProjectStore
        project_store = ProjectStore()
        project = project_store.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")

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
    
    # 프로젝트 정보 조회
    project_context = {}
    if task_request.project_id:
        try:
            from context.dynamo.project_store import ProjectStore
            project_store = ProjectStore()
            project = project_store.get_project(task_request.project_id)
            
            if project:
                logger.info(f"Found project: {project['name']} for task")
                project_context = {
                    "project_id": project["project_id"],
                    "project_name": project["name"],
                    "slack_channel": project.get("slack_channel"),
                    "github_repo": project.get("github_repo")
                }
                
                # 프로젝트 정보 로깅
                logger.info(f"Project context for task: {project_context}")
        except Exception as e:
            logger.warning(f"Failed to get project info: {e}")
    else:
        logger.warning("No project_id provided for task, using default settings")
    
    # 비동기로 작업 처리 (프로젝트 컨텍스트 포함)
    task_id = mao.process_request_async(task_request.request, task_request.user_id, project_context)
    
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
        # 이벤트 처리
        event = body.get("event", {})
        
        # 메시지 이벤트 처리
        if event.get("type") == "message":
            # 봇 메시지 무시 (bot_id 또는 bot_profile이 있는 경우)
            if event.get("bot_id") or event.get("bot_profile") or event.get("subtype") == "bot_message":
                logger.debug("Ignoring bot message")
                return {"status": "ok", "message": "Bot message ignored"}
            
            # 메시지 텍스트 가져오기
            text = event.get("text", "")
            user = event.get("user", "unknown")
            
            # 자신이 보낸 메시지인지 확인 (앱 사용자 ID와 메시지 사용자 ID 비교)
            app_user_id = None
            if settings.SLACK_BOT_TOKEN:
                try:
                    from slack.notifier import SlackNotifier
                    slack = SlackNotifier()
                    if slack.client:
                        auth_info = slack.client.auth_test()
                        if auth_info["ok"]:
                            app_user_id = auth_info["user_id"]
                            logger.info(f"Found bot ID: {app_user_id}")
                except Exception as e:
                    logger.warning(f"Failed to get bot ID: {e}")
            
            # 자신이 보낸 메시지면 무시
            if app_user_id and user == app_user_id:
                logger.debug("Ignoring message from self")
                return {"status": "ok", "message": "Ignoring message from self"}
            
            # 멘션 패턴 확인
            is_bot_mention = False
            request_text = ""
            
            # 1. 정규식을 사용하여 문장 시작 부분의 멘션 패턴 확인
            import re
            
            # 실제 봇 ID 기반 멘션 확인 (문장 시작 부분에 있는 경우만)
            if app_user_id:
                # <@BOT_ID>: 또는 <@BOT_ID> 패턴 (문장 시작)
                bot_mention_pattern = re.compile(f"^\s*<@{app_user_id}>:?\s*(.+)$")
                match = bot_mention_pattern.match(text)
                if match:
                    is_bot_mention = True
                    request_text = match.group(1).strip()
                    logger.info(f"Matched bot mention pattern with ID {app_user_id}: {request_text[:30]}...")
                else:
                    # 문장 중간에 있는 멘션도 확인 (더 유연한 패턴 매칭)
                    anywhere_pattern = re.compile(f"<@{app_user_id}>:?\s*(.+)")
                    match = anywhere_pattern.search(text)
                    if match:
                        is_bot_mention = True
                        request_text = match.group(1).strip()
                        logger.info(f"Matched bot mention anywhere in text with ID {app_user_id}: {request_text[:30]}...")
            
            # 2. 이벤트의 mentions 필드 확인 (Slack API가 제공하는 경우)
            if not is_bot_mention and "mentions" in event and event["mentions"]:
                for mention in event["mentions"]:
                    # 멘션된 사용자가 봇인 경우
                    if app_user_id and mention.get("user_id") == app_user_id:
                        is_bot_mention = True
                        # 멘션 텍스트 추출 (위치에 상관없이)
                        mention_text = f"<@{app_user_id}>"
                        parts = text.split(mention_text, 1)
                        if len(parts) > 1:
                            request_text = parts[1].strip()
                            # 콜론으로 시작하면 제거
                            if request_text.startswith(":"):
                                request_text = request_text[1:].strip()
                            logger.info(f"Matched bot mention from mentions field: {request_text[:30]}...")
                        else:
                            # 멘션만 있고 텍스트가 없는 경우
                            request_text = "도움말"
                            logger.info("Mention without text, defaulting to help request")
                        break
            
            # 3. 일반 텍스트 기반 멘션 확인 (fallback - 더 유연한 패턴 매칭)
            if not is_bot_mention:
                # T-Developer: 또는 @T-Developer: 패턴 (문장 시작 또는 중간)
                text_mention_patterns = [
                    r"^\s*(@?T-Developer):?\s*(.+)$",  # 문장 시작
                    r"\s+(@?T-Developer):?\s*(.+)"    # 문장 중간
                ]
                
                for pattern in text_mention_patterns:
                    match = re.search(pattern, text)
                    if match:
                        is_bot_mention = True
                        request_text = match.group(2).strip()
                        logger.info(f"Matched text mention pattern: {request_text[:30]}...")
                        break
                    
            # 멘션이 없거나 텍스트가 없는 경우는 무시
            if not is_bot_mention or not request_text:
                logger.debug(f"Ignoring message without proper bot mention: {text[:30]}...")
                return {"status": "ok", "message": "Message ignored (no proper bot mention)"}
                
            logger.info(f"Processing bot mention: '{request_text[:50]}...'")
            
            # 멘션이 확인되었으므로 처리
            
            # 프로젝트 지정 확인 ("project:ProjectName" 형태로 지정)
            project_id = None
            project_prefix = "project:"
            
            if project_prefix in request_text.lower():
                # 프로젝트 이름 추출
                parts = request_text.split(project_prefix, 1)
                if len(parts) > 1:
                    project_part = parts[1].strip()
                    project_name = project_part.split()[0].strip()  # 첫 번째 단어를 프로젝트 이름으로 간주
                    
                    # 프로젝트 이름으로 프로젝트 ID 찾기
                    try:
                        from context.dynamo.project_store import ProjectStore
                        project_store = ProjectStore()
                        projects = project_store.list_projects()
                        
                        for project in projects:
                            if project["name"].lower() == project_name.lower():
                                project_id = project["project_id"]
                                logger.info(f"Found project ID {project_id} for name {project_name}")
                                break
                        
                        # 프로젝트 이름 부분 제거
                        request_text = request_text.replace(f"{project_prefix}{project_name}", "").strip()
                    except Exception as e:
                        logger.warning(f"Failed to find project by name {project_name}: {e}")
                        # 오류 발생 시 프로젝트 이름 부분만 제거
                        request_text = request_text.replace(f"{project_prefix}{project_name}", "").strip()
            
            # 프로젝트 정보 가져오기
            project_context = {}
            try:
                from context.dynamo.project_store import ProjectStore
                project_store = ProjectStore()
                
                # 프로젝트 ID가 지정된 경우
                if project_id:
                    project = project_store.get_project(project_id)
                    if project:
                        logger.info(f"Using specified project for Slack request: {project['name']}")
                        project_context = {
                            "project_id": project["project_id"],
                            "project_name": project["name"],
                            "slack_channel": project.get("slack_channel"),
                            "github_repo": project.get("github_repo")
                        }
                # 프로젝트 ID가 없는 경우 기본 프로젝트 사용
                else:
                    projects = project_store.list_projects()
                    if projects:
                        project = projects[0]  # 첫 번째 프로젝트 사용
                        logger.info(f"Using default project for Slack request: {project['name']}")
                        project_context = {
                            "project_id": project["project_id"],
                            "project_name": project["name"],
                            "slack_channel": project.get("slack_channel"),
                            "github_repo": project.get("github_repo")
                        }
            except Exception as e:
                logger.warning(f"Failed to get project for Slack request: {e}")
            
            # 비동기로 작업 처리 (프로젝트 컨텍스트 포함)
            task_id = mao.process_request_async(request_text, user, project_context)
            
            # 로그 추가
            project_info = ""
            if "project_id" in project_context:
                project_info = f" for project {project_context['project_id']}"
            logger.info(f"Created task {task_id}{project_info} from Slack message by user {user}")
            
            return {"status": "ok", "task_id": task_id, "project_info": project_context.get("project_id")}
        else:
            # 멘션이 아닌 경우 무시
            logger.debug(f"Ignoring message without bot mention: {text[:30]}...")
            return {"status": "ok", "message": "Message ignored (no bot mention)"}
    
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
    
    # 프로젝트 정보 저장 (DynamoDB에 저장)
    from context.dynamo.project_store import ProjectStore
    project_store = ProjectStore()
    
    # 프로젝트 데이터 구성
    project_data = {
        "project_id": project_id,
        "name": project_request.name,
        "description": project_request.description,
        "github_repo": project_request.github_repo,
        "slack_channel": project_request.slack_channel,
        "created_at": datetime.now().isoformat()
    }
    
    # 프로젝트 저장
    project_store.save_project(project_data)
    logger.info(f"Project created and saved: {project_id}, {project_request.name}")
    
    # 프로젝트 설정을 글로벌 컨텍스트에 반영
    if project_request.github_repo or project_request.slack_channel:
        try:
            # 글로벌 컨텍스트 업데이트
            global_context = mao.task_store.get_global_context()
            if project_request.github_repo:
                repo_parts = project_request.github_repo.strip().split('/')
                if len(repo_parts) >= 2:
                    # github.com/owner/repo 형식에서 추출
                    owner = repo_parts[-2]
                    repo = repo_parts[-1]
                    global_context["github_owner"] = owner
                    global_context["github_repo"] = repo
                    logger.info(f"Setting GitHub repo: {owner}/{repo}")
            
            if project_request.slack_channel:
                global_context["slack_channel"] = project_request.slack_channel
                logger.info(f"Setting Slack channel: {project_request.slack_channel}")
            
            # 글로벌 컨텍스트 저장
            mao.task_store.save_global_context(global_context)
        except Exception as e:
            logger.error(f"Failed to update global context: {e}")
    
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
    
    # DynamoDB에서 프로젝트 목록 조회
    from context.dynamo.project_store import ProjectStore
    project_store = ProjectStore()
    
    try:
        projects = project_store.list_projects()
        logger.info(f"Retrieved {len(projects)} projects from database")
        
        # 프로젝트가 없으면 기본 프로젝트 제공 (새 사용자를 위한 기본값)
        if not projects:
            default_project = {
                "project_id": "PROJ-DEFAULT",
                "name": "GovChat",
                "description": "정부 지원사업 매칭 챗봇 (기본 프로젝트)",
                "github_repo": settings.GITHUB_OWNER + "/" + settings.GITHUB_REPO,
                "slack_channel": settings.SLACK_CHANNEL,
                "created_at": datetime.now().isoformat()
            }
            projects = [default_project]
            
            # 기본 프로젝트 저장 (선택사항)
            try:
                project_store.save_project(default_project)
                logger.info("Created default project")
            except Exception as e:
                logger.warning(f"Failed to save default project: {e}")
        
        return projects
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        # 오류 발생 시 기본 프로젝트 반환
        return [{
            "project_id": "PROJ-ERROR",
            "name": "GovChat",
            "description": "정부 지원사업 매칭 챗봇 (오류 발생)",
            "github_repo": settings.GITHUB_OWNER + "/" + settings.GITHUB_REPO,
            "slack_channel": settings.SLACK_CHANNEL,
            "created_at": datetime.now().isoformat()
        }]

@app.get("/health")
async def health_check():
    """
    기본 헬스 체크
    
    Returns:
        기본 상태 정보
    """
    return {
        "status": "ok", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """
    상세 헬스 체크
    
    Returns:
        상세 상태 정보
    """
    # 프로젝트 개수 확인
    project_count = 0
    try:
        from context.dynamo.project_store import ProjectStore
        project_store = ProjectStore()
        projects = project_store.list_projects()
        project_count = len(projects)
    except Exception as e:
        logger.warning(f"Failed to get project count: {e}")
    
    # 작업 개수 확인
    task_count = 0
    completed_tasks = 0
    error_tasks = 0
    try:
        all_tasks = mao.task_store.find_tasks_by_status(None)  # 모든 작업 가져오기
        task_count = len(all_tasks)
        # 완료된 작업 수 계산
        completed_tasks = sum(1 for task in all_tasks if task.status in [TaskStatus.COMPLETED, TaskStatus.DEPLOYED])
        # 오류 작업 수 계산
        error_tasks = sum(1 for task in all_tasks if task.status == TaskStatus.ERROR)
    except Exception as e:
        logger.warning(f"Failed to get task count: {e}")
    
    # 시스템 정보 수집
    import platform
    import psutil
    import os
    from datetime import timedelta
    
    # 시스템 부팅 시간 계산
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    system_info = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_human": str(timedelta(seconds=int(uptime.total_seconds())))
    }
    
    # 연결 상태 확인
    connections = {
        "aws": "unknown",
        "github": "unknown",
        "slack": "unknown"
    }
    
    # AWS 연결 테스트
    try:
        # DynamoDB 테이블 존재 확인
        table_name = mao.task_store.table_name
        mao.task_store.dynamodb.meta.client.describe_table(TableName=table_name)
        connections["aws"] = "connected"
    except Exception as e:
        connections["aws"] = f"error: {str(e)[:100]}"
    
    # GitHub 연결 테스트
    try:
        if settings.GITHUB_TOKEN and settings.GITHUB_OWNER and settings.GITHUB_REPO:
            from tools.git.github import GitHubTool
            github_tool = GitHubTool()
            # 저장소 정보 확인
            url = f"{github_tool.api_base}/repos/{github_tool.owner}/{github_tool.repo}"
            headers = {
                "Authorization": f"token {github_tool.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                connections["github"] = "connected"
            else:
                connections["github"] = f"error: {response.status_code}"
        else:
            connections["github"] = "not configured"
    except Exception as e:
        connections["github"] = f"error: {str(e)[:100]}"
    
    # Slack 연결 테스트
    try:
        if settings.SLACK_BOT_TOKEN:
            from slack.notifier import SlackNotifier
            slack = SlackNotifier()
            if slack.client:
                # 간단한 API 호출로 토큰 유효성 확인
                response = slack.client.auth_test()
                if response["ok"]:
                    connections["slack"] = f"connected as {response['user']}"
                else:
                    connections["slack"] = f"error: {response.get('error')}"
            else:
                connections["slack"] = "client initialization failed"
        else:
            connections["slack"] = "not configured"
    except Exception as e:
        connections["slack"] = f"error: {str(e)[:100]}"
    
    return {
        "status": "ok", 
        "version": "1.0.0",
        "projects": project_count,
        "tasks": {
            "total": task_count,
            "completed": completed_tasks,
            "error": error_tasks,
            "in_progress": task_count - completed_tasks - error_tasks
        },
        "system": system_info,
        "connections": connections,
        "environment": settings.ENV,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)