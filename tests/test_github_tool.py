"""
GitHubTool 테스트
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from tools.git.github import GitHubTool

class TestGitHubTool(unittest.TestCase):
    """GitHubTool 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        
        # 환경 변수 패치
        self.env_patcher = patch.dict('os.environ', {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_REPO': 'test_repo',
            'GITHUB_OWNER': 'test_owner',
            'Q_DEVELOPER_WORKSPACE': self.temp_dir
        })
        self.env_patcher.start()
        
        # GitHubTool의 _run_git_command 메서드 패치
        self.run_git_patcher = patch('tools.git.github.GitHubTool._run_git_command')
        self.mock_run_git = self.run_git_patcher.start()
        self.mock_run_git.return_value = "mock_output"
        
        # requests.post 패치
        self.requests_post_patcher = patch('tools.git.github.requests.post')
        self.mock_post = self.requests_post_patcher.start()
        self.mock_post.return_value = MagicMock()
        self.mock_post.return_value.json.return_value = {
            "html_url": "https://github.com/test_owner/test_repo/pull/1",
            "number": 1
        }
        self.mock_post.return_value.raise_for_status = MagicMock()
        
        # requests.put 패치
        self.requests_put_patcher = patch('tools.git.github.requests.put')
        self.mock_put = self.requests_put_patcher.start()
        self.mock_put.return_value = MagicMock()
        self.mock_put.return_value.json.return_value = {
            "merged": True,
            "message": "Pull Request successfully merged"
        }
        self.mock_put.return_value.raise_for_status = MagicMock()
        
        # requests.delete 패치
        self.requests_delete_patcher = patch('tools.git.github.requests.delete')
        self.mock_delete = self.requests_delete_patcher.start()
        
    def tearDown(self):
        """테스트 정리"""
        # 패치 중지
        self.env_patcher.stop()
        self.run_git_patcher.stop()
        self.requests_post_patcher.stop()
        self.requests_put_patcher.stop()
        self.requests_delete_patcher.stop()
        
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """GitHubTool 초기화 테스트"""
        # 작업 ID 없이 초기화
        tool = GitHubTool()
        self.assertEqual(tool.token, 'test_token')
        self.assertEqual(tool.repo, 'test_repo')
        self.assertEqual(tool.owner, 'test_owner')
        self.assertEqual(tool.workspace_dir, self.temp_dir)
        
        # 작업 ID로 초기화
        task_id = "test-task-id"
        tool_with_task = GitHubTool(task_id=task_id)
        expected_workspace = os.path.join(self.temp_dir, task_id)
        self.assertEqual(tool_with_task.workspace_dir, expected_workspace)
    
    def test_create_branch(self):
        """브랜치 생성 테스트"""
        tool = GitHubTool()
        branch_name = "test-branch"
        tool.create_branch(branch_name)
        
        # _run_git_command 호출 확인
        self.mock_run_git.assert_any_call(["git", "checkout", "main"])
        self.mock_run_git.assert_any_call(["git", "pull", "origin", "main"])
        self.mock_run_git.assert_any_call(["git", "checkout", "-b", branch_name])
    
    def test_commit_changes(self):
        """변경사항 커밋 테스트"""
        tool = GitHubTool()
        branch_name = "test-branch"
        commit_message = "Test commit"
        
        # 커밋 해시 설정
        self.mock_run_git.return_value = "abcdef1234567890"
        
        result = tool.commit_changes(branch_name, commit_message)
        
        # _run_git_command 호출 확인
        self.mock_run_git.assert_any_call(["git", "checkout", branch_name])
        self.mock_run_git.assert_any_call(["git", "add", "."])
        self.mock_run_git.assert_any_call(["git", "commit", "-m", commit_message])
        self.mock_run_git.assert_any_call(["git", "push", "origin", branch_name])
        self.mock_run_git.assert_any_call(["git", "rev-parse", "HEAD"])
        
        # 결과 확인
        self.assertEqual(result, "abcdef1234567890")
    
    def test_create_pull_request(self):
        """PR 생성 테스트"""
        tool = GitHubTool()
        head = "test-branch"
        base = "main"
        title = "Test PR"
        body = "Test PR body"
        
        result = tool.create_pull_request(head, base, title, body)
        
        # requests.post 호출 확인
        self.mock_post.assert_called_once()
        args, kwargs = self.mock_post.call_args
        self.assertEqual(args[0], "https://api.github.com/repos/test_owner/test_repo/pulls")
        self.assertEqual(kwargs["json"]["head"], head)
        self.assertEqual(kwargs["json"]["base"], base)
        self.assertEqual(kwargs["json"]["title"], title)
        self.assertEqual(kwargs["json"]["body"], body)
        
        # 결과 확인
        self.assertEqual(result, "https://github.com/test_owner/test_repo/pull/1")
    
    def test_merge_pull_request(self):
        """PR 병합 테스트"""
        tool = GitHubTool()
        pr_url = "https://github.com/test_owner/test_repo/pull/1"
        head = "test-branch"
        
        result = tool.merge_pull_request(pr_url, head)
        
        # requests.put 호출 확인
        self.mock_put.assert_called_once()
        args, kwargs = self.mock_put.call_args
        self.assertEqual(args[0], "https://api.github.com/repos/test_owner/test_repo/pulls/1/merge")
        self.assertEqual(kwargs["json"]["merge_method"], "squash")
        
        # _cleanup_branch 호출 확인 (requests.delete 호출 확인)
        self.mock_delete.assert_called_once()
        
        # 결과 확인
        self.assertTrue(result["merged"])
        self.assertEqual(result["message"], "PR merged successfully")
        
    def test_cleanup_branch(self):
        """브랜치 정리 테스트"""
        tool = GitHubTool()
        branch_name = "test-branch"
        
        tool._cleanup_branch(branch_name)
        
        # _run_git_command 호출 확인
        self.mock_run_git.assert_any_call(["git", "checkout", "main"], ignore_errors=True)
        self.mock_run_git.assert_any_call(["git", "branch", "-D", branch_name], ignore_errors=True)
        
        # requests.delete 호출 확인
        self.mock_delete.assert_called_once()
        args, kwargs = self.mock_delete.call_args
        self.assertEqual(args[0], "https://api.github.com/repos/test_owner/test_repo/git/refs/heads/test-branch")

if __name__ == '__main__':
    unittest.main()