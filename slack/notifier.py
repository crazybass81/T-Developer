"""
SlackNotifier - Slack 알림 도구

이 모듈은 Slack을 통해 T-Developer 작업 상태 및 결과를 알리는 기능을 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import settings
from core.task import Task, TaskStatus

# 로깅 설정
logger = logging.getLogger(__name__)

class SlackNotifier:
    """
    Slack 알림 도구
    
    작업 상태 및 결과를 Slack 채널에 알리는 기능을 제공합니다.
    """
    
    def __init__(self):
        """SlackNotifier 초기화"""
        self.token = settings.SLACK_BOT_TOKEN
        self.channel = settings.SLACK_CHANNEL
        self.client = WebClient(token=self.token) if self.token else None
        self.notification_level = settings.NOTIFICATION_LEVEL
        
        if self.client:
            logger.info(f"SlackNotifier initialized for channel: {self.channel}")
        else:
            logger.warning("SlackNotifier initialized without token, notifications will be logged only")
    
    def send_message(self, text: str, blocks: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
        """
        Slack 메시지 전송
        
        Args:
            text: 메시지 텍스트
            blocks: 메시지 블록 (옵션)
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        logger.info(f"Sending Slack message: {text[:50]}...")
        
        if not self.client:
            logger.info(f"Slack notification (simulated): {text}")
            return None
        
        try:
            # Slack API로 메시지 전송
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                blocks=blocks
            )
            
            logger.info(f"Slack message sent successfully")
            return response["ts"]
        except SlackApiError as e:
            logger.error(f"Failed to send Slack message: {str(e)}", exc_info=True)
            return None
    
    def send_thread_message(self, thread_ts: str, text: str, 
                           blocks: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
        """
        Slack 스레드 메시지 전송
        
        Args:
            thread_ts: 스레드 타임스탬프
            text: 메시지 텍스트
            blocks: 메시지 블록 (옵션)
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        logger.info(f"Sending Slack thread message: {text[:50]}...")
        
        if not self.client:
            logger.info(f"Slack thread notification (simulated): {text}")
            return None
        
        try:
            # Slack API로 스레드 메시지 전송
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                thread_ts=thread_ts,
                blocks=blocks
            )
            
            logger.info(f"Slack thread message sent successfully")
            return response["ts"]
        except SlackApiError as e:
            logger.error(f"Failed to send Slack thread message: {str(e)}", exc_info=True)
            return None
    
    def send_acknowledgment(self, task: Task) -> Optional[str]:
        """
        작업 접수 알림
        
        Args:
            task: 접수된 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"✅ Received task {task.task_id}: {task.request}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Task {task.task_id} received*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Request: {task.request}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Status: {task.status.value} | Created: {task.created_at}"
                    }
                ]
            }
        ]
        
        # 메시지 전송
        ts = self.send_message(text, blocks)
        
        # 작업 객체에 스레드 타임스탬프 저장
        if ts:
            task.metadata["slack_thread_ts"] = ts
            try:
                # TaskStore를 통해 Task 업데이트 (스레드 ts 저장)
                from context.dynamo.task_store import TaskStore
                TaskStore().update_task(task)
            except Exception as e:
                logger.error(f"Failed to save Slack thread_ts for {task.task_id}: {e}")
        
        return ts
    
    def send_planning_started(self, task: Task) -> Optional[str]:
        """
        계획 수립 시작 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        # 최소 알림 모드에서는 전송하지 않음
        if self.notification_level == "minimal":
            return None
        
        text = f"🔄 Planning task {task.task_id}..."
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Planning in progress*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_plan_created(self, task: Task, plan_summary: str) -> Optional[str]:
        """
        계획 수립 완료 알림
        
        Args:
            task: 작업 객체
            plan_summary: 계획 요약
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"📋 Plan created for task {task.task_id}: {plan_summary}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Plan created*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Plan: {plan_summary}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_coding_started(self, task: Task) -> Optional[str]:
        """
        코딩 시작 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        # 최소 알림 모드에서는 전송하지 않음
        if self.notification_level == "minimal":
            return None
        
        text = f"💻 Coding in progress for task {task.task_id}..."
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Coding in progress*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_coding_completed(self, task: Task) -> Optional[str]:
        """
        코딩 완료 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        # 파일 변경 요약
        modified_summary = f"{len(task.modified_files)} files modified"
        created_summary = f"{len(task.created_files)} files created"
        
        text = f"✅ Coding complete for task {task.task_id}: {modified_summary}, {created_summary}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Coding complete*"
                }
            }
        ]
        
        # 상세 정보 추가 (verbose 모드)
        if self.notification_level == "verbose":
            # 수정된 파일 목록
            if task.modified_files:
                modified_files_text = "\n".join([f"• {file}" for file in task.modified_files])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Modified files:*\n{modified_files_text}"
                    }
                })
            
            # 생성된 파일 목록
            if task.created_files:
                created_files_text = "\n".join([f"• {file}" for file in task.created_files])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Created files:*\n{created_files_text}"
                    }
                })
        else:
            # 간단한 요약
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{modified_summary}, {created_summary}"
                }
            })
        
        # 상태 정보
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Task {task.task_id} | Status: {task.status.value} | Branch: {task.branch_name}"
                }
            ]
        })
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_testing_started(self, task: Task) -> Optional[str]:
        """
        테스트 시작 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        # 최소 알림 모드에서는 전송하지 않음
        if self.notification_level == "minimal":
            return None
        
        text = f"🧪 Running tests for task {task.task_id}..."
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Running tests*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_tests_passed(self, task: Task) -> Optional[str]:
        """
        테스트 통과 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"✅ All tests passed for task {task.task_id}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*All tests passed*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_test_failure(self, task: Task) -> Optional[str]:
        """
        테스트 실패 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"❌ Tests failed for task {task.task_id}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Tests failed*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Error: {task.error}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_test_fix_attempt(self, task: Task, attempt: int) -> Optional[str]:
        """
        테스트 수정 시도 알림
        
        Args:
            task: 작업 객체
            attempt: 시도 횟수
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        # 최소 알림 모드에서는 전송하지 않음
        if self.notification_level == "minimal":
            return None
        
        text = f"🔄 Fixing test failures for task {task.task_id} (attempt {attempt})..."
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Fixing test failures* (attempt {attempt})"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_deploying(self, task: Task) -> Optional[str]:
        """
        배포 시작 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"🚀 Deploying task {task.task_id}..."
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Deploying*"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_deployment_success(self, task: Task) -> Optional[str]:
        """
        배포 성공 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        # 배포 URL 포함
        url_text = f" at {task.deployed_url}" if task.deployed_url else ""
        version_text = f" (version {task.deployed_version})" if task.deployed_version else ""
        
        text = f"🚀 Deployment successful for task {task.task_id}{url_text}{version_text}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Deployment successful*"
                }
            }
        ]
        
        # URL 추가
        if task.deployed_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Deployed at: <{task.deployed_url}|{task.deployed_url}>"
                }
            })
        
        # 버전 추가
        if task.deployed_version:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Version: {task.deployed_version}"
                }
            })
        
        # PR 링크 추가
        if task.pr_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Pull Request: <{task.pr_url}|View PR>"
                }
            })
        
        # 상태 정보
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Task {task.task_id} | Status: {task.status.value}"
                }
            ]
        })
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_deployment_failure(self, task: Task) -> Optional[str]:
        """
        배포 실패 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"⚠️ Deployment failed for task {task.task_id}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Deployment failed*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Error: {task.error}"
                }
            }
        ]
        
        # PR 링크 추가
        if task.pr_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Pull Request: <{task.pr_url}|View PR>"
                }
            })
        
        # 상태 정보
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Task {task.task_id} | Status: {task.status.value}"
                }
            ]
        })
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_completion(self, task: Task) -> Optional[str]:
        """
        작업 완료 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"🎉 Task {task.task_id} completed: {task.request}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Task completed*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Request: {task.request}"
                }
            }
        ]
        
        # 배포 정보 추가
        if task.deployed and task.deployed_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Deployed at: <{task.deployed_url}|{task.deployed_url}>"
                }
            })
        
        # PR 링크 추가
        if task.pr_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Pull Request: <{task.pr_url}|View PR>"
                }
            })
        
        # 상태 정보
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Task {task.task_id} | Status: {task.status.value} | Completed at: {task.completed_at}"
                }
            ]
        })
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_error(self, task: Task) -> Optional[str]:
        """
        오류 알림
        
        Args:
            task: 작업 객체
            
        Returns:
            메시지 타임스탬프 또는 None
        """
        text = f"⚠️ Error in task {task.task_id}: {task.error}"
        
        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error occurred*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Error: {task.error}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Task {task.task_id} | Status: {task.status.value}"
                    }
                ]
            }
        ]
        
        # 스레드 타임스탬프 가져오기
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메시지 전송
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)