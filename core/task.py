"""
Task 모듈 - T-Developer 작업 관리

이 모듈은 T-Developer 시스템에서 사용자 요청을 처리하는 작업(Task)을 정의합니다.
"""
import enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TaskStatus(str, enum.Enum):
    """작업 상태 열거형"""
    RECEIVED = "received"       # 요청 접수됨
    PLANNING = "planning"       # 계획 수립 중
    PLANNED = "planned"         # 계획 수립 완료
    CODING = "coding"           # 코드 구현 중
    CODED = "coded"             # 코드 구현 완료
    TESTING = "testing"         # 테스트 중
    TESTED = "tested"           # 테스트 완료
    DEPLOYING = "deploying"     # 배포 중
    DEPLOYED = "deployed"       # 배포 완료
    COMPLETED = "completed"     # 작업 완료
    ERROR = "error"             # 오류 발생


class Task(BaseModel):
    """
    T-Developer 작업 클래스
    
    사용자 요청에 대한 작업 정보와 상태를 관리합니다.
    """
    # 기본 정보
    task_id: str
    request: str
    user_id: str
    project_id: Optional[str] = None
    status: TaskStatus = TaskStatus.RECEIVED
    
    # 시간 정보
    created_at: str
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # 계획 정보
    plan_summary: Optional[str] = None
    plan_s3_key: Optional[str] = None
    
    # 코드 구현 정보
    branch_name: Optional[str] = None
    commit_hash: Optional[str] = None
    modified_files: List[str] = Field(default_factory=list)
    created_files: List[str] = Field(default_factory=list)
    diff_s3_key: Optional[str] = None
    
    # 테스트 정보
    test_success: Optional[bool] = None
    test_log_s3_key: Optional[str] = None
    
    # 배포 정보
    pr_url: Optional[str] = None
    deployed: Optional[bool] = None
    deployed_version: Optional[str] = None
    deployed_url: Optional[str] = None
    
    # 오류 정보
    error: Optional[str] = None
    
    # 추가 메타데이터
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        작업 객체를 딕셔너리로 변환
        
        Returns:
            작업 정보를 담은 딕셔너리
        """
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        딕셔너리에서 작업 객체 생성
        
        Args:
            data: 작업 정보를 담은 딕셔너리
            
        Returns:
            생성된 Task 객체
        """
        # TaskStatus 열거형 처리
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus(data['status'])
            
        return cls(**data)