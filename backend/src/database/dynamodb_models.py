"""
DynamoDB Models
DynamoDB 테이블에 대한 데이터 모델 정의
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class ProjectModel(BaseModel):
    """프로젝트 모델"""
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: str
    project_type: str
    framework: str
    features: List[str] = []
    status: str = "created"
    created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    metadata: Dict[str, Any] = {}
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """DynamoDB 아이템으로 변환"""
        return self.dict()
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> "ProjectModel":
        """DynamoDB 아이템으로부터 모델 생성"""
        return cls(**item)

class UserModel(BaseModel):
    """사용자 모델"""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    organization: Optional[str] = None
    created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    last_login: Optional[int] = None
    api_keys: List[str] = []
    preferences: Dict[str, Any] = {}
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """DynamoDB 아이템으로 변환"""
        return self.dict()
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> "UserModel":
        """DynamoDB 아이템으로부터 모델 생성"""
        return cls(**item)

class AgentModel(BaseModel):
    """에이전트 모델"""
    agent_id: str
    version: int = 1
    name: str
    type: str
    capabilities: List[str] = []
    configuration: Dict[str, Any] = {}
    performance_metrics: Dict[str, Any] = {}
    created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """DynamoDB 아이템으로 변환"""
        return self.dict()
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> "AgentModel":
        """DynamoDB 아이템으로부터 모델 생성"""
        return cls(**item)

class SessionModel(BaseModel):
    """세션 모델"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    project_id: Optional[str] = None
    started_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    last_activity: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    ttl: int = Field(default_factory=lambda: int(datetime.now().timestamp()) + 3600)  # 1 hour TTL
    context: Dict[str, Any] = {}
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """DynamoDB 아이템으로 변환"""
        return self.dict()
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> "SessionModel":
        """DynamoDB 아이템으로부터 모델 생성"""
        return cls(**item)