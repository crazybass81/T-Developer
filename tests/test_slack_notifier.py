"""
SlackNotifier 테스트
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from slack.notifier import SlackNotifier
from core.task import Task, TaskStatus

class TestSlackNotifier(unittest.TestCase):
    """SlackNotifier 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 환경 변수 패치
        self.env_patcher = patch.dict('os.environ', {
            'SLACK_BOT_TOKEN': 'test_token',
            'SLACK_CHANNEL': '#test-channel',
            'NOTIFICATION_LEVEL': 'normal'
        })
        self.env_patcher.start()
        
        # slack_sdk.WebClient 패치
        self.slack_client_patcher = patch('slack.notifier.WebClient')
        self.mock_client = self.slack_client_patcher.start()
        self.mock_client_instance = MagicMock()
        self.mock_client.return_value = self.mock_client_instance
        
        # chat_postMessage 응답 설정
        self.mock_client_instance.chat_postMessage.return_value = {
            "ok": True,
            "ts": "1234567890.123456"
        }
        
        # 테스트용 Task 객체 생성
        self.task = Task(
            task_id="TEST-123",
            request="Test request",
            user_id="U123456",
            status=TaskStatus.RECEIVED,
            created_at=datetime.now().isoformat()
        )
        
    def tearDown(self):
        """테스트 정리"""
        # 패치 중지
        self.env_patcher.stop()
        self.slack_client_patcher.stop()
    
    def test_init(self):
        """SlackNotifier 초기화 테스트"""
        notifier = SlackNotifier()
        self.assertEqual(notifier.channel, '#test-channel')
        self.assertEqual(notifier.notification_level, 'normal')
        self.mock_client.assert_called_once_with(token='test_token')
    
    def test_init_no_token(self):
        """토큰 없는 경우 초기화 테스트"""
        with patch.dict('os.environ', {'SLACK_BOT_TOKEN': ''}):
            notifier = SlackNotifier()
            self.assertIsNone(notifier.client)
    
    def test_send_message(self):
        """send_message 메서드 테스트"""
        notifier = SlackNotifier()
        text = "Test message"
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        
        result = notifier.send_message(text, blocks)
        
        # chat_postMessage 호출 확인
        self.mock_client_instance.chat_postMessage.assert_called_once()
        args, kwargs = self.mock_client_instance.chat_postMessage.call_args
        self.assertEqual(kwargs["channel"], '#test-channel')
        self.assertEqual(kwargs["text"], text)
        self.assertEqual(kwargs["blocks"], blocks)
        
        # 결과 확인
        self.assertEqual(result, "1234567890.123456")
    
    def test_send_thread_message(self):
        """send_thread_message 메서드 테스트"""
        notifier = SlackNotifier()
        thread_ts = "1234567890.123456"
        text = "Test thread message"
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        
        result = notifier.send_thread_message(thread_ts, text, blocks)
        
        # chat_postMessage 호출 확인
        self.mock_client_instance.chat_postMessage.assert_called_once()
        args, kwargs = self.mock_client_instance.chat_postMessage.call_args
        self.assertEqual(kwargs["channel"], '#test-channel')
        self.assertEqual(kwargs["text"], text)
        self.assertEqual(kwargs["blocks"], blocks)
        self.assertEqual(kwargs["thread_ts"], thread_ts)
        
        # 결과 확인
        self.assertEqual(result, "1234567890.123456")
    
    def test_send_acknowledgment(self):
        """send_acknowledgment 메서드 테스트"""
        notifier = SlackNotifier()
        
        result = notifier.send_acknowledgment(self.task)
        
        # chat_postMessage 호출 확인
        self.mock_client_instance.chat_postMessage.assert_called_once()
        args, kwargs = self.mock_client_instance.chat_postMessage.call_args
        
        # 메시지에 작업 ID가 포함되어 있는지 확인
        self.assertIn(self.task.task_id, kwargs["text"])
        
        # 결과 확인
        self.assertEqual(result, "1234567890.123456")
    
    def test_send_planning_started(self):
        """send_planning_started 메서드 테스트"""
        notifier = SlackNotifier()
        
        result = notifier.send_planning_started(self.task)
        
        # chat_postMessage 호출 확인
        self.mock_client_instance.chat_postMessage.assert_called_once()
        
        # 결과 확인
        self.assertEqual(result, "1234567890.123456")
    
    def test_send_plan_created(self):
        """send_plan_created 메서드 테스트"""
        notifier = SlackNotifier()
        plan_summary = "Test plan summary"
        
        result = notifier.send_plan_created(self.task, plan_summary)
        
        # chat_postMessage 호출 확인
        self.mock_client_instance.chat_postMessage.assert_called_once()
        args, kwargs = self.mock_client_instance.chat_postMessage.call_args
        
        # 메시지에 계획 요약이 포함되어 있는지 확인
        self.assertIn(plan_summary, str(kwargs["blocks"]))
        
        # 결과 확인
        self.assertEqual(result, "1234567890.123456")
    
    def test_minimal_notification_level(self):
        """minimal 알림 수준 테스트"""
        with patch.dict('os.environ', {'NOTIFICATION_LEVEL': 'minimal'}):
            notifier = SlackNotifier()
            
            # minimal 수준에서는 시작 알림을 보내지 않음
            result = notifier.send_planning_started(self.task)
            self.mock_client_instance.chat_postMessage.assert_not_called()
            self.assertIsNone(result)
            
            # 완료 알림은 보냄
            result = notifier.send_plan_created(self.task, "Test plan")
            self.mock_client_instance.chat_postMessage.assert_called_once()
    
    def test_verbose_notification_level(self):
        """verbose 알림 수준 테스트"""
        with patch.dict('os.environ', {'NOTIFICATION_LEVEL': 'verbose'}):
            notifier = SlackNotifier()
            
            # verbose 수준에서는 모든 알림을 보냄
            result = notifier.send_planning_started(self.task)
            self.mock_client_instance.chat_postMessage.assert_called_once()
            self.assertEqual(result, "1234567890.123456")

if __name__ == '__main__':
    unittest.main()