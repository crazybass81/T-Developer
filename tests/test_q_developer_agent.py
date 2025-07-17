"""
QDeveloperAgent 테스트
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json

from agents.q_developer.agent import QDeveloperAgent

class TestQDeveloperAgent(unittest.TestCase):
    """QDeveloperAgent 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_dir = tempfile.mkdtemp()
        
        # 환경 변수 패치
        self.env_patcher = patch.dict('os.environ', {
            'Q_DEVELOPER_WORKSPACE': self.temp_dir
        })
        self.env_patcher.start()
        
        # subprocess.run 패치
        self.subprocess_patcher = patch('agents.q_developer.agent.subprocess.run')
        self.mock_subprocess = self.subprocess_patcher.start()
        self.mock_subprocess.return_value = MagicMock()
        self.mock_subprocess.return_value.returncode = 0
        self.mock_subprocess.return_value.stdout = "mock output"
        self.mock_subprocess.return_value.stderr = ""
        
        # open 패치
        self.open_patcher = patch('builtins.open', unittest.mock.mock_open(read_data='{"success": true}'))
        self.mock_open = self.open_patcher.start()
        
        # os.path.exists 패치
        self.exists_patcher = patch('os.path.exists')
        self.mock_exists = self.exists_patcher.start()
        self.mock_exists.return_value = True
        
    def tearDown(self):
        """테스트 정리"""
        # 패치 중지
        self.env_patcher.stop()
        self.subprocess_patcher.stop()
        self.open_patcher.stop()
        self.exists_patcher.stop()
        
        # 임시 디렉토리 삭제
        os.rmdir(self.temp_dir)
        os.rmdir(self.workspace_dir)
    
    def test_init(self):
        """QDeveloperAgent 초기화 테스트"""
        agent = QDeveloperAgent()
        self.assertEqual(agent.workspace_dir, self.temp_dir)
    
    def test_execute_task(self):
        """execute_task 메서드 테스트"""
        agent = QDeveloperAgent()
        
        # 테스트 지시 생성
        instruction = {
            "task_id": "test-task",
            "feature_name": "Test Feature",
            "description": "Test description"
        }
        
        # subprocess.run이 여러 번 호출될 때 다른 결과 반환하도록 설정
        self.mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # Q Developer CLI 호출
            MagicMock(returncode=0, stdout="diff --git a/test.py b/test.py", stderr=""),  # git diff
            MagicMock(returncode=0, stdout="M test.py", stderr="")  # git status
        ]
        
        # json.load가 결과를 반환하도록 설정
        with patch('json.load') as mock_json_load:
            mock_json_load.return_value = {"success": True}
            
            result = agent.execute_task(instruction, self.workspace_dir)
            
            # 결과 확인
            self.assertTrue(result["success"])
            self.assertEqual(result["diff"], "diff --git a/test.py b/test.py")
            
            # subprocess.run 호출 확인
            self.assertEqual(self.mock_subprocess.call_count, 3)
            
            # 첫 번째 호출 (Q Developer CLI)
            args, kwargs = self.mock_subprocess.call_args_list[0]
            self.assertEqual(args[0][0], "amazonq")
            self.assertEqual(args[0][1], "developer")
            self.assertEqual(args[0][2], "/dev")
            self.assertEqual(kwargs["cwd"], self.workspace_dir)
    
    def test_run_tests(self):
        """run_tests 메서드 테스트"""
        agent = QDeveloperAgent()
        
        # pytest 실행 결과 설정
        self.mock_subprocess.return_value.stdout = "===== test session starts =====\n5 passed in 0.5s\n"
        
        result = agent.run_tests(self.workspace_dir)
        
        # subprocess.run 호출 확인
        self.mock_subprocess.assert_called_once()
        args, kwargs = self.mock_subprocess.call_args
        self.assertEqual(args[0][0], "pytest")
        self.assertEqual(kwargs["cwd"], self.workspace_dir)
        
        # 결과 확인
        self.assertTrue(result["success"])
        self.assertEqual(result["passed"], 5)
        self.assertEqual(result["failed"], 0)
    
    def test_fix_test_failures(self):
        """fix_test_failures 메서드 테스트"""
        agent = QDeveloperAgent()
        
        # 테스트 실패 정보
        failures = [
            {"file": "test_module.py", "test": "test_function", "message": "Test failed"}
        ]
        
        # subprocess.run이 여러 번 호출될 때 다른 결과 반환하도록 설정
        self.mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # Q Developer CLI 호출
            MagicMock(returncode=0, stdout="M test_module.py", stderr="")  # git status
        ]
        
        # json.load가 결과를 반환하도록 설정
        with patch('json.load') as mock_json_load:
            mock_json_load.return_value = {"success": True}
            
            result = agent.fix_test_failures(failures, self.workspace_dir)
            
            # 결과 확인
            self.assertTrue(result["success"])
            self.assertEqual(result["fixed"], 1)
            self.assertEqual(result["changes"], ["test_module.py"])
            
            # subprocess.run 호출 확인
            self.assertEqual(self.mock_subprocess.call_count, 2)
    
    def test_mock_code_implementation(self):
        """_mock_code_implementation 메서드 테스트"""
        agent = QDeveloperAgent()
        
        # 인증 관련 지시
        auth_instruction = {
            "task_id": "test-task",
            "feature_name": "Authentication",
            "description": "Add authentication feature"
        }
        
        auth_result = agent._mock_code_implementation(auth_instruction)
        
        # 결과 확인
        self.assertTrue(auth_result["success"])
        self.assertIn("utils/jwt_util.py", auth_result["created_files"])
        self.assertIn("services/auth_service.py", auth_result["modified_files"])
        self.assertIn("import jwt", auth_result["diff"])
        
        # API 관련 지시
        api_instruction = {
            "task_id": "test-task",
            "feature_name": "API Endpoint",
            "description": "Add new API endpoint"
        }
        
        api_result = agent._mock_code_implementation(api_instruction)
        
        # 결과 확인
        self.assertTrue(api_result["success"])
        self.assertIn("routes/api.py", api_result["modified_files"])
        self.assertIn("services/feature_service.py", api_result["created_files"])
        self.assertIn("@router.get('/api/features')", api_result["diff"])

if __name__ == '__main__':
    unittest.main()