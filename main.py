"""
T-Developer 메인 애플리케이션

이 모듈은 T-Developer 시스템의 진입점으로, 웹 서버를 실행하고 API 엔드포인트를 제공합니다.
"""
import logging
import os
import sys
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.mao import MAO
from config import settings

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

# 요청 모델
class TaskRequest(BaseModel):
    """작업 요청 모델"""
    request: str
    user_id: str

# 응답 모델
class TaskResponse(BaseModel):
    """작업 응답 모델"""
    task_id: str
    status: str
    message: str

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
        task_id = mao.process_request_async(task_request.request, task_request.user_id)
        
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
        
        return {
            "task_id": task.task_id,
            "request": task.request,
            "status": task.status,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "completed_at": task.completed_at,
            "error": task.error
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")

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
                    
                    # MAO에 작업 비동기 처리 요청
                    task_id = mao.process_request_async(request_text, user)
                    
                    return {"status": "ok", "task_id": task_id}
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing Slack event: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

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