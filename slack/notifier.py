"""
SlackNotifier - Slack 알림 모듈

작업 상태 변화를 Slack 채널에 알리는 기능을 제공합니다.
"""
import logging
from typing import Dict, List, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import settings
from core.task import Task, TaskStatus

# 로깅 설정
logger = logging.getLogger(__name__)

class SlackNotifier:
    """
    Slack 알림 모듈
    
    작업 상태 변화를 Slack 채널에 알리는 기능을 제공합니다.
    """
    
    def __init__(self):
        """SlackNotifier 초기화"""
        self.token = settings.SLACK_BOT_TOKEN
        self.channel = settings.SLACK_CHANNEL
        self.notification_level = settings.NOTIFICATION_LEVEL
        
        # Slack 클라이언트 초기화
        if self.token:
            self.client = WebClient(token=self.token)
            logger.info(f"SlackNotifier initialized for channel: {self.channel}")
        else:
            self.client = None
            logger.warning("SlackNotifier initialized without token, notifications will be logged only")
    
    def send_message(self, text: str, blocks: List[Dict[str, Any]] = None) -> Optional[str]:
        """
        Slack 메시지 전송
        
        Args:
            text: 메시지 텍스트
            blocks: 메시지 블록 (Slack Block Kit)
            
        Returns:
            메시지 타임스탬프 (스레드 ID로 사용)
        """
        if not self.client:
            logger.info(f"[SLACK MESSAGE] {text}")
            return None
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                blocks=blocks
            )
            logger.info(f"Slack message sent to {self.channel}")
            return response['ts']
        except SlackApiError as e:
            logger.error(f"Error sending Slack message: {e}")
            return None
    
    def send_thread_message(self, thread_ts: str, text: str, blocks: List[Dict[str, Any]] = None) -> Optional[str]:
        """
        Slack 스레드 메시지 전송
        
        Args:
            thread_ts: 스레드 타임스탬프
            text: 메시지 텍스트
            blocks: 메시지 블록 (Slack Block Kit)
            
        Returns:
            메시지 타임스탬프
        """
        if not self.client:
            logger.info(f"[SLACK THREAD MESSAGE] {text}")
            return None
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                blocks=blocks,
                thread_ts=thread_ts
            )
            logger.info(f"Slack thread message sent to {self.channel}")
            return response['ts']
        except SlackApiError as e:
            logger.error(f"Error sending Slack thread message: {e}")
            return None
    
    def send_acknowledgment(self, task: Task) -> Optional[str]:
        """
        작업 접수 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        text = f"✅ 작업 접수: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*작업 접수됨*\n*ID:* {task.task_id}\n*요청:* {task.request}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"요청자: {task.user_id} | 상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        ts = self.send_message(text, blocks)
        
        # 스레드 타임스탬프 저장
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
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        # minimal 모드에서는 시작 알림 생략
        if self.notification_level == "minimal":
            return None
        
        text = f"🔄 계획 수립 시작: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*계획 수립 시작*\n*ID:* {task.task_id}\n*요청:* {task.request}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_plan_created(self, task: Task) -> Optional[str]:
        """
        계획 수립 완료 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        text = f"📋 계획 수립 완료: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*계획 수립 완료*\n*ID:* {task.task_id}\n*요약:* {task.plan_summary}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_coding_started(self, task: Task) -> Optional[str]:
        """
        코드 구현 시작 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        # minimal 모드에서는 시작 알림 생략
        if self.notification_level == "minimal":
            return None
        
        text = f"💻 코드 구현 시작: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*코드 구현 시작*\n*ID:* {task.task_id}\n*브랜치:* {task.branch_name}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_coding_completed(self, task: Task) -> Optional[str]:
        """
        코드 구현 완료 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        modified_count = len(task.modified_files)
        created_count = len(task.created_files)
        
        text = f"💾 코드 구현 완료: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*코드 구현 완료*\n*ID:* {task.task_id}\n*수정된 파일:* {modified_count}개\n*생성된 파일:* {created_count}개"
                }
            }
        ]
        
        # verbose 모드에서는 파일 목록 추가
        if self.notification_level == "verbose":
            file_list = ""
            if task.modified_files:
                file_list += "*수정된 파일:*\n"
                for file in task.modified_files:
                    file_list += f"• {file}\n"
            if task.created_files:
                file_list += "*생성된 파일:*\n"
                for file in task.created_files:
                    file_list += f"• {file}\n"
            
            if file_list:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": file_list
                    }
                })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"커밋: {task.commit_hash} | 상태: {task.status.value}"
                }
            ]
        })
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_testing_started(self, task: Task) -> Optional[str]:
        """
        테스트 시작 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        # minimal 모드에서는 시작 알림 생략
        if self.notification_level == "minimal":
            return None
        
        text = f"🧪 테스트 시작: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*테스트 시작*\n*ID:* {task.task_id}\n*브랜치:* {task.branch_name}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_tests_passed(self, task: Task) -> Optional[str]:
        """
        테스트 통과 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        text = f"✅ 테스트 통과: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*테스트 통과*\n*ID:* {task.task_id}\n*브랜치:* {task.branch_name}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_test_failure(self, task: Task, failures: List[Dict[str, Any]]) -> Optional[str]:
        """
        테스트 실패 알림
        
        Args:
            task: Task 객체
            failures: 실패한 테스트 정보
            
        Returns:
            메시지 타임스탬프
        """
        text = f"❌ 테스트 실패: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*테스트 실패*\n*ID:* {task.task_id}\n*실패한 테스트:* {len(failures)}개"
                }
            }
        ]
        
        # verbose 모드에서는 실패 목록 추가
        if self.notification_level == "verbose" and failures:
            failure_list = "*실패한 테스트:*\n"
            for failure in failures:
                failure_list += f"• {failure.get('file')}::{failure.get('test')}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": failure_list
                }
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"상태: {task.status.value}"
                }
            ]
        })
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_test_fix_attempt(self, task: Task, attempt: int, max_retries: int) -> Optional[str]:
        """
        테스트 실패 수정 시도 알림
        
        Args:
            task: Task 객체
            attempt: 시도 횟수
            max_retries: 최대 재시도 횟수
            
        Returns:
            메시지 타임스탬프
        """
        # minimal 모드에서는 시도 알림 생략
        if self.notification_level == "minimal":
            return None
        
        text = f"🔄 테스트 실패 수정 시도 ({attempt}/{max_retries}): {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*테스트 실패 수정 시도 ({attempt}/{max_retries})*\n*ID:* {task.task_id}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_deploying(self, task: Task) -> Optional[str]:
        """
        배포 시작 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        # minimal 모드에서는 시작 알림 생략
        if self.notification_level == "minimal":
            return None
        
        text = f"🚀 배포 시작: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*배포 시작*\n*ID:* {task.task_id}\n*브랜치:* {task.branch_name}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_deployment_success(self, task: Task) -> Optional[str]:
        """
        배포 성공 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        text = f"🎉 배포 성공: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*배포 성공*\n*ID:* {task.task_id}\n*버전:* {task.deployed_version or 'N/A'}"
                }
            }
        ]
        
        # PR URL이 있으면 추가
        if task.pr_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*PR:* <{task.pr_url}|GitHub에서 보기>"
                }
            })
        
        # 배포 URL이 있으면 추가
        if task.deployed_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*배포 URL:* <{task.deployed_url}|서비스 확인하기>"
                }
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"상태: {task.status.value}"
                }
            ]
        })
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_deployment_failure(self, task: Task, error_message: str) -> Optional[str]:
        """
        배포 실패 알림
        
        Args:
            task: Task 객체
            error_message: 오류 메시지
            
        Returns:
            메시지 타임스탬프
        """
        text = f"⚠️ 배포 실패: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*배포 실패*\n*ID:* {task.task_id}\n*오류:* {error_message}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_completion(self, task: Task) -> Optional[str]:
        """
        작업 완료 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        text = f"✅ 작업 완료: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*작업 완료*\n*ID:* {task.task_id}\n*요청:* {task.request}"
                }
            }
        ]
        
        # PR URL이 있으면 추가
        if task.pr_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*PR:* <{task.pr_url}|GitHub에서 보기>"
                }
            })
        
        # 배포 URL이 있으면 추가
        if task.deployed_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*배포 URL:* <{task.deployed_url}|서비스 확인하기>"
                }
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"상태: {task.status.value} | 완료 시간: {task.completed_at}"
                }
            ]
        })
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)
    
    def send_error(self, task: Task) -> Optional[str]:
        """
        오류 알림
        
        Args:
            task: Task 객체
            
        Returns:
            메시지 타임스탬프
        """
        text = f"❌ 오류 발생: {task.task_id}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*오류 발생*\n*ID:* {task.task_id}\n*오류:* {task.error or '알 수 없는 오류'}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {task.status.value}"
                    }
                ]
            }
        ]
        
        thread_ts = task.metadata.get("slack_thread_ts")
        if thread_ts:
            return self.send_thread_message(thread_ts, text, blocks)
        else:
            return self.send_message(text, blocks)