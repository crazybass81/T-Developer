"""
LambdaSlackNotifier - Lambda 기반 Slack 알림 모듈

Lambda 함수를 사용하여 Slack 알림을 전송하는 기능을 제공합니다.
"""
import json
import logging
import boto3
from typing import Dict, List, Any, Optional

from config import settings
from core.task import Task, TaskStatus

# 로깅 설정
logger = logging.getLogger(__name__)

class LambdaSlackNotifier:
    """
    Lambda 기반 Slack 알림 모듈
    
    Lambda 함수를 사용하여 Slack 알림을 전송하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """LambdaSlackNotifier 초기화"""
        self.lambda_client = boto3.client('lambda', region_name=settings.AWS_REGION)
        self.lambda_function_name = "t-developer-slack-notifier"
        self.channel = settings.SLACK_CHANNEL
        self.notification_level = settings.NOTIFICATION_LEVEL
        logger.info(f"LambdaSlackNotifier initialized for function: {self.lambda_function_name}")
    
    def _invoke_lambda(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lambda 함수 호출
        
        Args:
            payload: Lambda 함수에 전달할 페이로드
            
        Returns:
            Lambda 함수 응답
        """
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # 응답 처리
            if response['StatusCode'] == 200:
                payload = json.loads(response['Payload'].read().decode())
                logger.info(f"Lambda function invoked successfully: {payload}")
                return payload
            else:
                logger.error(f"Lambda function invocation failed: {response}")
                return {"error": f"Lambda function invocation failed: {response['StatusCode']}"}
        
        except Exception as e:
            logger.error(f"Error invoking Lambda function: {e}")
            return {"error": str(e)}
    
    def _send_task_message(self, task: Task, text: str, blocks: List[Dict[str, Any]]) -> Optional[str]:
        """
        프로젝트별 채널을 고려하여 메시지 전송
        
        Args:
            task: Task 객체
            text: 메시지 텍스트
            blocks: 메시지 블록
            
        Returns:
            메시지 타임스탬프
        """
        # 프로젝트별 Slack 채널 확인 (메타데이터에서 먼저 확인)
        project_slack_channel = task.metadata.get("slack_channel")
        thread_ts = task.metadata.get("slack_thread_ts")
        
        # 메타데이터에 없으면 프로젝트 정보에서 확인
        if not project_slack_channel and task.project_id:
            try:
                from context.dynamo.project_store import ProjectStore
                project_store = ProjectStore()
                project = project_store.get_project(task.project_id)
                if project and "slack_channel" in project:
                    project_slack_channel = project["slack_channel"]
                    # 메타데이터에 저장하여 다음 호출에서 재사용
                    task.metadata["slack_channel"] = project_slack_channel
                    logger.info(f"Found project-specific Slack channel from project {task.project_id}: {project_slack_channel}")
                    
                    # TaskStore를 통해 Task 업데이트 (메타데이터 저장)
                    try:
                        from context.dynamo.task_store import TaskStore
                        TaskStore().update_task(task)
                        logger.info(f"Updated task metadata with project Slack channel: {project_slack_channel}")
                    except Exception as e:
                        logger.error(f"Failed to save project Slack channel to task metadata: {e}")
            except Exception as e:
                logger.warning(f"Failed to get project Slack channel for task {task.task_id}: {e}")
        
        if project_slack_channel:
            logger.info(f"Using project-specific Slack channel for task {task.task_id}: {project_slack_channel}")
        
        # Lambda 함수에 전달할 페이로드 구성
        payload = {
            "type": "task_message",
            "message": text,
            "blocks": blocks,
            "channel": project_slack_channel or self.channel
        }
        
        # 스레드 타임스탬프가 있으면 추가
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        # Lambda 함수 호출
        response = self._invoke_lambda(payload)
        
        # 응답에서 타임스탬프 추출
        if "body" in response:
            try:
                body = json.loads(response["body"]) if isinstance(response["body"], str) else response["body"]
                if body.get("status") == "success":
                    ts = body.get("timestamp")
                    
                    # 스레드 타임스탬프 저장
                    if ts and not thread_ts:
                        task.metadata["slack_thread_ts"] = ts
                        # 사용한 채널도 저장
                        if project_slack_channel:
                            task.metadata["slack_channel"] = project_slack_channel
                        try:
                            # TaskStore를 통해 Task 업데이트 (스레드 ts 저장)
                            from context.dynamo.task_store import TaskStore
                            TaskStore().update_task(task)
                        except Exception as e:
                            logger.error(f"Failed to save Slack thread_ts for {task.task_id}: {e}")
                    
                    return ts
            except Exception as e:
                logger.error(f"Error processing Lambda response: {e}")
        
        return None
    
    # 기존 SlackNotifier의 모든 메서드를 동일한 인터페이스로 구현
    # 각 메서드는 _send_task_message를 호출하여 Lambda 함수를 통해 메시지 전송
    
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
        
        return self._send_task_message(task, text, blocks)
    
    # 나머지 메서드들은 기존 SlackNotifier와 동일한 구현을 가지므로 생략
    # 실제 구현에서는 모든 메서드를 동일하게 구현해야 함
    
    # 예시로 몇 가지 중요한 메서드만 구현
    
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
        
        return self._send_task_message(task, text, blocks)
    
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
        
        return self._send_task_message(task, text, blocks)
    
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
        
        return self._send_task_message(task, text, blocks)