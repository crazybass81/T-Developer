"""
GitHubTool - GitHub 연동 도구

GitHub 저장소 클론, 브랜치 생성, 커밋, PR 생성 등의 기능을 제공합니다.
"""
import logging
import os
import subprocess
import requests
from typing import Dict, List, Any, Optional, Tuple

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class GitHubTool:
    """
    GitHub 연동 도구
    
    GitHub 저장소 클론, 브랜치 생성, 커밋, PR 생성 등의 기능을 제공합니다.
    """
    
    def __init__(self, task_id: str = None):
        """
        GitHubTool 초기화
        
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
        
        # 워크스페이스 초기화
        self._init_workspace()
        
        logger.info(f"GitHubTool initialized for {self.owner}/{self.repo} with workspace: {self.workspace_dir}")
    
    def _init_workspace(self):
        """
        작업 디렉토리 초기화
        
        저장소가 없으면 클론, 있으면 최신 상태로 업데이트
        """
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # GitHub 설정 확인
        if not self.token or not self.owner or not self.repo:
            logger.warning("GitHub configuration is incomplete. Using mock repository.")
            # 가짜 저장소 생성 (GitHub 연동 없이 작동하기 위해)
            mock_git_dir = os.path.join(self.workspace_dir, ".git")
            if not os.path.exists(mock_git_dir):
                os.makedirs(mock_git_dir, exist_ok=True)
                with open(os.path.join(mock_git_dir, "config"), "w") as f:
                    f.write("[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n")
            return
        
        # .git 디렉토리 존재 여부 확인
        git_dir = os.path.join(self.workspace_dir, ".git")
        try:
            if not os.path.exists(git_dir):
                # 저장소 클론
                logger.info(f"Cloning repository to {self.workspace_dir}")
                self._run_git_command(["git", "clone", self.repo_url, self.workspace_dir], ignore_errors=True)
            else:
                # 저장소 업데이트
                logger.info(f"Updating repository in {self.workspace_dir}")
                self._run_git_command(["git", "fetch", "origin"], cwd=self.workspace_dir, ignore_errors=True)
                self._run_git_command(["git", "reset", "--hard", "origin/main"], cwd=self.workspace_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error initializing workspace: {e}")
            # 가짜 저장소 생성 (오류 발생 시 대체 작동)
            if not os.path.exists(git_dir):
                os.makedirs(git_dir, exist_ok=True)
                with open(os.path.join(git_dir, "config"), "w") as f:
                    f.write("[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n")
    
    def _run_git_command(self, command: List[str], cwd: str = None, ignore_errors: bool = False) -> str:
        """
        Git 명령 실행
        
        Args:
            command: Git 명령 (리스트)
            cwd: 작업 디렉토리 (기본값: self.workspace_dir)
            ignore_errors: 오류 무시 여부
            
        Returns:
            명령 출력 (stdout)
        """
        if cwd is None:
            cwd = self.workspace_dir
        
        # Git 인증 환경 변수 설정
        env = os.environ.copy()
        
        # 명령어가 clone이나 push 등 원격 저장소 접근이 필요한 경우 토큰 사용
        if command[0] == "git" and command[1] in ["clone", "push", "pull", "fetch"]:
            # URL에 토큰을 직접 포함시키는 방식으로 변경
            if command[1] == "clone":
                # clone 명령의 경우 URL을 토큰이 포함된 형태로 변경
                repo_url_with_token = f"https://{self.token}@github.com/{self.owner}/{self.repo}.git"
                command_idx = command.index(self.repo_url)
                command[command_idx] = repo_url_with_token
            elif command[1] in ["push", "pull", "fetch"]:
                # 원격 저장소 URL 설정
                self._run_git_command(["git", "remote", "set-url", "origin", 
                                     f"https://{self.token}@github.com/{self.owner}/{self.repo}.git"], 
                                     cwd=cwd, ignore_errors=True)
        
        try:
            process = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=not ignore_errors
            )
            
            if process.returncode == 0:
                logger.info(f"Git command succeeded: {' '.join(command)}")
                return process.stdout.strip()
            else:
                if ignore_errors:
                    logger.warning(f"Git command failed (ignored): {' '.join(command)}")
                    logger.warning(f"Error: {process.stderr}")
                    return ""
                else:
                    logger.error(f"Git command failed: {' '.join(command)}")
                    logger.error(f"Error: {process.stderr}")
                    raise subprocess.CalledProcessError(
                        process.returncode,
                        command,
                        output=process.stdout,
                        stderr=process.stderr
                    )
        except Exception as e:
            if ignore_errors:
                logger.warning(f"Git command exception (ignored): {e}")
                return ""
            else:
                logger.error(f"Git command exception: {e}")
                raise
    
    def create_branch(self, branch_name: str) -> bool:
        """
        브랜치 생성
        
        Args:
            branch_name: 브랜치 이름
            
        Returns:
            성공 여부
        """
        try:
            # main 브랜치로 체크아웃
            self._run_git_command(["git", "checkout", "main"])
            
            # main 브랜치 최신화
            self._run_git_command(["git", "pull", "origin", "main"])
            
            # 새 브랜치 생성
            self._run_git_command(["git", "checkout", "-b", branch_name])
            
            logger.info(f"Branch {branch_name} created")
            return True
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def commit_changes(self, branch: str, message: str) -> Optional[str]:
        """
        변경사항 커밋
        
        Args:
            branch: 브랜치 이름
            message: 커밋 메시지
            
        Returns:
            커밋 해시
        """
        try:
            # 브랜치 체크아웃
            self._run_git_command(["git", "checkout", branch])
            
            # 민감 파일 제외
            for pattern in settings.RESTRICTED_FILES:
                self._run_git_command(["git", "rm", "--cached", pattern], ignore_errors=True)
            
            # 변경사항 스테이징
            self._run_git_command(["git", "add", "."])
            
            # 커밋
            self._run_git_command(["git", "commit", "-m", message])
            
            # 원격 저장소에 푸시
            self._run_git_command(["git", "push", "origin", branch])
            
            # 커밋 해시 가져오기
            commit_hash = self._run_git_command(["git", "rev-parse", "HEAD"])
            
            logger.info(f"Changes committed to {branch} with hash {commit_hash}")
            return commit_hash
        except Exception as e:
            logger.error(f"Error committing changes to {branch}: {e}")
            return None
    
    def create_pull_request(self, head: str, base: str, title: str, body: str) -> Optional[str]:
        """
        Pull Request 생성
        
        Args:
            head: 소스 브랜치
            base: 대상 브랜치
            title: PR 제목
            body: PR 본문
            
        Returns:
            PR URL
        """
        try:
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
            
            logger.info(f"Pull request created: {pr_url}")
            return pr_url
        except Exception as e:
            logger.error(f"Error creating pull request: {e}")
            return None
    
    def merge_pull_request(self, pr_url: str, head: str) -> Dict[str, Any]:
        """
        Pull Request 병합
        
        Args:
            pr_url: PR URL
            head: 소스 브랜치 이름
            
        Returns:
            병합 결과 정보
        """
        try:
            # GitHub 설정 확인
            if not self.token or not self.owner or not self.repo:
                logger.warning("GitHub configuration is incomplete. Simulating PR merge.")
                # PR 병합 시뮬레이션
                if head:
                    self._cleanup_branch(head)
                return {
                    "merged": True,
                    "message": "PR merge simulated successfully",
                    "version": "v1.0.0",
                    "url": f"https://github.com/{self.owner or 'mock'}/{self.repo or 'mock'}/tree/main"
                }
            
            # PR 번호 추출
            pr_number = pr_url.split("/")[-1]
            
            # GitHub API를 통해 실제 PR 병합 수행
            url = f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/merge"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "merge_method": "squash",
                "commit_title": f"Merge PR #{pr_number}",
                "commit_message": "Automatically merged by T-Developer"
            }
            
            response = requests.put(url, headers=headers, json=data)
            merge_success = response.status_code == 200
            
            # 브랜치 정리 (성공 여부와 관계없이 정리 시도)
            if head:
                self._cleanup_branch(head)
            else:
                logger.warning("No branch name provided for cleanup after merge")
            
            # 버전 정보 가져오기 (태그 기반)
            version = self._get_latest_version()
            
            if merge_success:
                logger.info(f"Pull request {pr_number} merged successfully")
                return {
                    "merged": True,
                    "message": "PR merged successfully",
                    "version": version,
                    "url": f"https://github.com/{self.owner}/{self.repo}/tree/main"
                }
            else:
                error_message = response.json().get("message", "Error merging PR via API")
                logger.error(f"Failed to merge PR: {error_message}")
                return {
                    "merged": False,
                    "message": error_message
                }
        except Exception as e:
            logger.error(f"Error in merge_pull_request: {e}")
            # 브랜치 정리 시도 (오류 발생 시에도)
            if head:
                try:
                    self._cleanup_branch(head)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up branch after error: {cleanup_error}")
            
            return {
                "merged": False,
                "message": f"Error merging PR: {str(e)}"
            }
    
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
        최신 버전 정보 가져오기
        
        Returns:
            최신 버전 (태그 기반)
        """
        try:
            # 태그 가져오기
            tags = self._run_git_command(["git", "tag", "--sort=-v:refname"])
            
            if tags:
                # 최신 태그 반환
                return tags.split("\n")[0]
            else:
                # 태그가 없으면 기본값 반환
                return "v1.0.0"
        except Exception as e:
            logger.warning(f"Failed to get latest version: {str(e)}")
            return "v1.0.0"
    
    def find_related_files(self, query: str) -> List[Dict[str, str]]:
        """
        관련 파일 검색
        
        Args:
            query: 검색어
            
        Returns:
            관련 파일 목록 (파일 경로와 설명)
        """
        # 실제 구현에서는 GitHub 코드 검색 API나 로컬 grep을 사용하는 것이 좋습니다.
        # 간단한 구현을 위해 키워드 기반으로 하드코딩된 파일 목록 반환
        
        related_files = []
        
        # 키워드별 관련 파일 매핑
        if "auth" in query.lower() or "authentication" in query.lower():
            related_files.extend([
                {"path": "auth_service.py", "description": "인증 서비스 모듈"},
                {"path": "models/user.py", "description": "사용자 모델"},
                {"path": "utils/jwt_util.py", "description": "JWT 유틸리티"}
            ])
        
        if "api" in query.lower() or "endpoint" in query.lower():
            related_files.extend([
                {"path": "api.py", "description": "API 라우터"},
                {"path": "controllers/api_controller.py", "description": "API 컨트롤러"}
            ])
        
        if "database" in query.lower() or "db" in query.lower():
            related_files.extend([
                {"path": "db/connection.py", "description": "데이터베이스 연결 모듈"},
                {"path": "models/base.py", "description": "기본 모델 클래스"}
            ])
        
        # 기본 파일 추가
        if not related_files:
            related_files.extend([
                {"path": "app.py", "description": "애플리케이션 진입점"},
                {"path": "config.py", "description": "설정 모듈"}
            ])
        
        logger.info(f"Found {len(related_files)} related files for query: {query}")
        return related_files