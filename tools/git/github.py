"""
GitHubTool - GitHub 연동 도구

이 모듈은 GitHub API를 사용하여 코드 저장소와 상호작용하는 기능을 제공합니다.
"""
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Any
import requests

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class GitHubTool:
    """
    GitHub 연동 도구
    
    코드 저장소 클론, 브랜치 생성, 커밋, PR 생성 등의 기능을 제공합니다.
    """
    
    def __init__(self, task_id: str = None):
        """GitHubTool 초기화
        
        Args:
            task_id: 작업 ID (지정된 경우 작업별 워크스페이스 사용)
        """
        self.token = settings.GITHUB_TOKEN
        self.repo = settings.GITHUB_REPO
        self.owner = settings.GITHUB_OWNER
        self.api_base = "https://api.github.com"
        self.repo_url = f"https://github.com/{self.owner}/{self.repo}.git"
        
        # 작업별 워크스페이스 사용
        if task_id:
            self.workspace_dir = os.path.join(settings.Q_DEVELOPER_WORKSPACE, task_id)
        else:
            self.workspace_dir = settings.Q_DEVELOPER_WORKSPACE
        
        # 작업 디렉토리 초기화
        self._init_workspace()
        
        logger.info(f"GitHubTool initialized for repo: {self.owner}/{self.repo} in workspace: {self.workspace_dir}")
    
    def _init_workspace(self) -> None:
        """
        작업 디렉토리 초기화
        """
        # 작업 디렉토리가 없으면 생성
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Git 저장소 클론 또는 풀
        if not os.path.exists(os.path.join(self.workspace_dir, ".git")):
            logger.info(f"Cloning repository to {self.workspace_dir}")
            self._run_git_command(["git", "clone", self.repo_url, self.workspace_dir])
        else:
            logger.info(f"Pulling latest changes in {self.workspace_dir}")
            self._run_git_command(["git", "fetch", "origin"])
            self._run_git_command(["git", "reset", "--hard", "origin/main"])
    
    def create_branch(self, branch_name: str) -> None:
        """
        브랜치 생성
        
        Args:
            branch_name: 생성할 브랜치 이름
        """
        logger.info(f"Creating branch: {branch_name}")
        
        # 메인 브랜치로 전환
        self._run_git_command(["git", "checkout", "main"])
        
        # 최신 변경사항 가져오기
        self._run_git_command(["git", "pull", "origin", "main"])
        
        # 브랜치 생성 및 전환
        self._run_git_command(["git", "checkout", "-b", branch_name])
        
        logger.info(f"Branch {branch_name} created successfully")
    
    def commit_changes(self, branch_name: str, commit_message: str) -> str:
        """
        변경사항 커밋
        
        Args:
            branch_name: 커밋할 브랜치 이름
            commit_message: 커밋 메시지
            
        Returns:
            커밋 해시
        """
        logger.info(f"Committing changes to branch: {branch_name}")
        
        # 브랜치 전환
        self._run_git_command(["git", "checkout", branch_name])
        
        # 민감 파일 제외
        for pattern in settings.RESTRICTED_FILES:
            self._run_git_command(["git", "rm", "--cached", pattern], ignore_errors=True)
        
        # 변경사항 스테이징
        self._run_git_command(["git", "add", "."])
        
        # 커밋
        self._run_git_command(["git", "commit", "-m", commit_message])
        
        # 원격 저장소에 푸시
        self._run_git_command(["git", "push", "origin", branch_name])
        
        # 커밋 해시 가져오기
        commit_hash = self._run_git_command(["git", "rev-parse", "HEAD"]).strip()
        
        logger.info(f"Changes committed to {branch_name} with hash: {commit_hash}")
        return commit_hash
    
    def create_pull_request(self, head: str, base: str, title: str, body: str) -> str:
        """
        Pull Request 생성
        
        Args:
            head: 소스 브랜치
            base: 대상 브랜치
            title: PR 제목
            body: PR 본문
            
        Returns:
            생성된 PR URL
        """
        logger.info(f"Creating PR from {head} to {base}: {title}")
        
        # GitHub API로 PR 생성
        url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        pr_data = response.json()
        pr_url = pr_data["html_url"]
        pr_number = pr_data["number"]
        
        logger.info(f"PR #{pr_number} created: {pr_url}")
        return pr_url
    
    def merge_pull_request(self, pr_url: str) -> Dict[str, Any]:
        """
        Pull Request 병합
        
        Args:
            pr_url: PR URL
            
        Returns:
            병합 결과 정보
        """
        # PR 번호 추출
        pr_number = pr_url.split("/")[-1]
        logger.info(f"Merging PR #{pr_number}")
        
        # GitHub API로 PR 병합
        url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "merge_method": "squash"
        }
        
        try:
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            
            # 병합 결과
            result = {
                "merged": True,
                "message": "PR merged successfully",
                "version": f"v{self._get_latest_version()}",
                "url": f"https://github.com/{self.owner}/{self.repo}/tree/main"
            }
            
            # 머지된 브랜치 정리
            self._cleanup_branch(head)
            
            logger.info(f"PR #{pr_number} merged successfully")
            return result
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to merge PR #{pr_number}: {str(e)}", exc_info=True)
            
            # 병합 실패 결과
            return {
                "merged": False,
                "message": f"Failed to merge PR: {str(e)}",
                "version": None,
                "url": pr_url
            }
    
    def find_related_files(self, query: str) -> List[Dict[str, Any]]:
        """
        관련 파일 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            관련 파일 정보 목록
        """
        logger.info(f"Finding files related to: {query[:50]}...")
        
        # 검색어를 키워드로 분리
        keywords = [kw.lower() for kw in query.split() if len(kw) > 3]
        
        try:
            # 저장소 내 파일 검색
            # 실제 구현에서는 GitHub 코드 검색 API 또는 로컬 grep 사용
            # 여기서는 간단한 예시로 구현
            
            # 임시 결과
            related_files = []
            
            # 인증 관련 검색어인 경우
            if any(kw in ["auth", "authentication", "login", "jwt", "token"] for kw in keywords):
                related_files.extend([
                    {
                        "name": "AuthService",
                        "path": "services/auth_service.py",
                        "description": "Authentication service with password hashing"
                    },
                    {
                        "name": "User Model",
                        "path": "models/user.py",
                        "description": "User database model with credentials"
                    }
                ])
            
            # API 관련 검색어인 경우
            if any(kw in ["api", "endpoint", "route", "controller"] for kw in keywords):
                related_files.extend([
                    {
                        "name": "API Routes",
                        "path": "routes/api.py",
                        "description": "API endpoint definitions"
                    },
                    {
                        "name": "App Config",
                        "path": "config/app.py",
                        "description": "Application configuration including API settings"
                    }
                ])
            
            logger.info(f"Found {len(related_files)} related files")
            return related_files
        except Exception as e:
            logger.error(f"Failed to find related files: {str(e)}", exc_info=True)
            return []
    
    def _run_git_command(self, command: List[str], ignore_errors: bool = False) -> str:
        """
        Git 명령 실행
        
        Args:
            command: 실행할 Git 명령 (리스트)
            ignore_errors: 오류 무시 여부
            
        Returns:
            명령 실행 결과
        """
        logger.debug(f"Running git command: {' '.join(command)}")
        
        # GitHub 토큰이 필요한 명령어인 경우 환경 변수 설정
        env = os.environ.copy()
        if self.token and (command[0] == "git" and command[1] in ["clone", "push", "pull", "fetch"]):
            # Git 자격 증명 도우미 설정
            env["GIT_ASKPASS"] = "echo"
            env["GIT_USERNAME"] = self.token
            env["GIT_PASSWORD"] = "x-oauth-basic"
        
        try:
            result = subprocess.run(
                command,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            if ignore_errors:
                logger.warning(f"Git command failed (ignored): {e.stderr}")
                return ""
            else:
                logger.error(f"Git command failed: {e.stderr}", exc_info=True)
                raise
    
    def _cleanup_branch(self, branch_name: str) -> None:
        """
        머지된 브랜치 정리
        
        Args:
            branch_name: 정리할 브랜치 이름
        """
        try:
            # 로컬 브랜치 정리
            self._run_git_command(["git", "checkout", "main"], ignore_errors=True)
            self._run_git_command(["git", "branch", "-D", branch_name], ignore_errors=True)
            
            # 원격 브랜치 삭제 (GitHub API 사용)
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            requests.delete(url, headers=headers)
            logger.info(f"Branch {branch_name} cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up branch {branch_name}: {str(e)}")
    
    def _get_latest_version(self) -> str:
        """
        최신 버전 번호 조회
        
        Returns:
            최신 버전 번호
        """
        try:
            # Git 태그에서 최신 버전 가져오기
            tags = self._run_git_command(["git", "tag", "--sort=-v:refname"]).splitlines()
            
            if tags:
                latest_tag = tags[0]
                # v1.0.0 형식에서 숫자만 추출
                if latest_tag.startswith("v"):
                    return latest_tag[1:]
                return latest_tag
            
            # 태그가 없으면 기본값 반환
            return "0.1.0"
        except Exception:
            # 오류 시 기본값 반환
            return "0.1.0"