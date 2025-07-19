"""
Task - 작업 모델

작업(Task) 정보를 표현하는 모델 클래스입니다.
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class TaskStatus(Enum):
    """작업 상태 열거형"""
    RECEIVED = "received"      # 작업 접수됨
    PLANNING = "planning"      # 계획 수립 중
    PLANNED = "planned"        # 계획 수립 완료
    CODING = "coding"          # 코드 구현 중
    CODED = "coded"            # 코드 구현 완료
    TESTING = "testing"        # 테스트 중
    TESTED = "tested"          # 테스트 완료
    DEPLOYING = "deploying"    # 배포 중
    DEPLOYED = "deployed"      # 배포 완료
    COMPLETED = "completed"    # 작업 완료
    ERROR = "error"            # 오류 발생

class Task:
    """
    작업(Task) 모델
    
    작업 정보를 표현하는 클래스입니다.
    """
    
    def __init__(
        self,
        task_id: str,
        request: str,
        user_id: str,
        status: TaskStatus = TaskStatus.RECEIVED,
        created_at: str = None,
        completed_at: str = None,
        plan_summary: str = None,
        plan_s3_key: str = None,
        branch_name: str = None,
        commit_hash: str = None,
        modified_files: List[str] = None,
        created_files: List[str] = None,
        diff_s3_key: str = None,
        test_success: bool = None,
        test_log_s3_key: str = None,
        deployed: bool = None,
        deployed_version: str = None,
        deployed_url: str = None,
        pr_url: str = None,
        error: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Task 초기화
        
        Args:
            task_id: 작업 ID
            request: 요청 내용
            user_id: 사용자 ID
            status: 작업 상태
            created_at: 생성 시간
            completed_at: 완료 시간
            plan_summary: 계획 요약
            plan_s3_key: 계획 S3 키
            branch_name: Git 브랜치 이름
            commit_hash: Git 커밋 해시
            modified_files: 수정된 파일 목록
            created_files: 생성된 파일 목록
            diff_s3_key: 코드 diff S3 키
            test_success: 테스트 성공 여부
            test_log_s3_key: 테스트 로그 S3 키
            deployed: 배포 여부
            deployed_version: 배포 버전
            deployed_url: 배포 URL
            pr_url: PR URL
            error: 오류 메시지
            metadata: 메타데이터
        """
        self.task_id = task_id
        self.request = request
        self.user_id = user_id
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.plan_summary = plan_summary
        self.plan_s3_key = plan_s3_key
        self.branch_name = branch_name
        self.commit_hash = commit_hash
        self.modified_files = modified_files or []
        self.created_files = created_files or []
        self.diff_s3_key = diff_s3_key
        self.test_success = test_success
        self.test_log_s3_key = test_log_s3_key
        self.deployed = deployed
        self.deployed_version = deployed_version
        self.deployed_url = deployed_url
        self.pr_url = pr_url
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Task 객체를 딕셔너리로 변환
        
        Returns:
            Task 딕셔너리
        """
        result = {
            'task_id': self.task_id,
            'request': self.request,
            'user_id': self.user_id,
            'status': self.status.value if isinstance(self.status, TaskStatus) else self.status,
            'created_at': self.created_at
        }
        
        # None이 아닌 필드만 추가
        if self.completed_at:
            result['completed_at'] = self.completed_at
        if self.plan_summary:
            result['plan_summary'] = self.plan_summary
        if self.plan_s3_key:
            result['plan_s3_key'] = self.plan_s3_key
        if self.branch_name:
            result['branch_name'] = self.branch_name
        if self.commit_hash:
            result['commit_hash'] = self.commit_hash
        if self.modified_files:
            result['modified_files'] = self.modified_files
        if self.created_files:
            result['created_files'] = self.created_files
        if self.diff_s3_key:
            result['diff_s3_key'] = self.diff_s3_key
        if self.test_success is not None:
            result['test_success'] = self.test_success
        if self.test_log_s3_key:
            result['test_log_s3_key'] = self.test_log_s3_key
        if self.deployed is not None:
            result['deployed'] = self.deployed
        if self.deployed_version:
            result['deployed_version'] = self.deployed_version
        if self.deployed_url:
            result['deployed_url'] = self.deployed_url
        if self.pr_url:
            result['pr_url'] = self.pr_url
        if self.error:
            result['error'] = self.error
        if self.metadata:
            result['metadata'] = self.metadata
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        딕셔너리에서 Task 객체 생성
        
        Args:
            data: Task 딕셔너리
            
        Returns:
            Task 객체
        """
        # 상태 문자열을 TaskStatus 열거형으로 변환
        status_str = data.get('status')
        status = TaskStatus(status_str) if status_str else TaskStatus.RECEIVED
        
        return cls(
            task_id=data.get('task_id'),
            request=data.get('request'),
            user_id=data.get('user_id'),
            status=status,
            created_at=data.get('created_at'),
            completed_at=data.get('completed_at'),
            plan_summary=data.get('plan_summary'),
            plan_s3_key=data.get('plan_s3_key'),
            branch_name=data.get('branch_name'),
            commit_hash=data.get('commit_hash'),
            modified_files=data.get('modified_files'),
            created_files=data.get('created_files'),
            diff_s3_key=data.get('diff_s3_key'),
            test_success=data.get('test_success'),
            test_log_s3_key=data.get('test_log_s3_key'),
            deployed=data.get('deployed'),
            deployed_version=data.get('deployed_version'),
            deployed_url=data.get('deployed_url'),
            pr_url=data.get('pr_url'),
            error=data.get('error'),
            metadata=data.get('metadata')
        )