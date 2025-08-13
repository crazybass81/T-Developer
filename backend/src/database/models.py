"""
Database Models
엔터프라이즈 데이터베이스 모델
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, BigInteger, Boolean, CheckConstraint, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Index, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from .base import Base

# Association tables for many-to-many relationships
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE")),
    UniqueConstraint("user_id", "role_id", name="uq_user_role"),
)

project_collaborators = Table(
    "project_collaborators",
    Base.metadata,
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE")),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("role", String(50), default="viewer"),
    Column("added_at", DateTime, default=func.now()),
    UniqueConstraint("project_id", "user_id", name="uq_project_collaborator"),
)


# Enums
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"


class User(Base):
    """사용자 모델"""

    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    bio = Column(Text)

    # Status
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Subscription
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires_at = Column(DateTime)

    # Organization
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL")
    )
    department = Column(String(100))
    employee_id = Column(String(50))

    # Quotas
    api_quota = Column(Integer, default=100)
    storage_quota = Column(BigInteger, default=1073741824)  # 1GB in bytes
    project_quota = Column(Integer, default=10)

    # Usage tracking
    api_calls_today = Column(Integer, default=0)
    storage_used = Column(BigInteger, default=0)
    total_projects = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime)
    email_verified_at = Column(DateTime)

    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_user_email_status", "email", "status"),
        Index("ix_user_org_dept", "organization_id", "department"),
    )


class Organization(Base):
    """조직 모델"""

    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255))

    # Billing
    billing_email = Column(String(255))
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.ENTERPRISE)
    subscription_seats = Column(Integer, default=10)

    # Settings
    settings = Column(JSONB, default={})
    allowed_email_domains = Column(ARRAY(String), default=[])

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")


class Role(Base):
    """역할 모델"""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, default=[])

    # System role flag
    is_system = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")


class Project(Base):
    """프로젝트 모델"""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(100), index=True)

    # Owner
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL")
    )

    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    visibility = Column(String(20), default="private")  # private, internal, public

    # Project data
    query = Column(Text)  # Original NL query
    requirements = Column(JSONB, default={})
    project_metadata = Column(
        JSONB, default={}
    )  # Renamed from metadata to avoid SQLAlchemy conflict

    # Generation details
    framework = Column(String(50))
    language = Column(String(50))
    features = Column(ARRAY(String), default=[])

    # Files
    file_path = Column(String(500))
    download_url = Column(String(500))
    preview_data = Column(JSONB)

    # Statistics
    generation_time = Column(Float)  # seconds
    file_size = Column(BigInteger)  # bytes
    file_count = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Relationships
    owner = relationship("User", back_populates="projects")
    organization = relationship("Organization", back_populates="projects")
    agent_executions = relationship(
        "AgentExecution", back_populates="project", cascade="all, delete-orphan"
    )
    collaborators = relationship("User", secondary=project_collaborators)

    # Indexes
    __table_args__ = (
        Index("ix_project_owner_status", "owner_id", "status"),
        Index("ix_project_created", "created_at"),
    )


class Agent(Base):
    """에이전트 정의 모델"""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Agent info
    name = Column(String(100), unique=True, nullable=False)
    version = Column(String(20), default="1.0.0")
    description = Column(Text)

    # Configuration
    config = Column(JSONB, default={})
    capabilities = Column(ARRAY(String), default=[])
    dependencies = Column(ARRAY(String), default=[])

    # Performance metrics
    avg_execution_time = Column(Float)
    success_rate = Column(Float)
    total_executions = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    executions = relationship("AgentExecution", back_populates="agent")


class AgentExecution(Base):
    """에이전트 실행 로그"""

    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))

    # Execution details
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.IDLE)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    error_message = Column(Text)

    # Performance
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    execution_time = Column(Float)  # seconds
    memory_usage = Column(BigInteger)  # bytes

    # Tracing
    trace_id = Column(String(100))
    parent_execution_id = Column(UUID(as_uuid=True))

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="executions")
    project = relationship("Project", back_populates="agent_executions")

    # Indexes
    __table_args__ = (
        Index("ix_agent_exec_project", "project_id", "agent_id"),
        Index("ix_agent_exec_time", "created_at"),
    )


class ApiKey(Base):
    """API 키 모델"""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Key info
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Permissions
    scopes = Column(ARRAY(String), default=[])
    rate_limit = Column(Integer, default=1000)

    # Restrictions
    allowed_ips = Column(ARRAY(String), default=[])
    allowed_domains = Column(ARRAY(String), default=[])

    # Usage limits
    daily_limit = Column(Integer)
    monthly_limit = Column(Integer)
    total_limit = Column(Integer)

    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)

    # Revocation
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    revoked_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="api_keys")

    # Indexes
    __table_args__ = (
        Index("ix_api_key_user", "user_id", "is_active"),
        Index("ix_api_key_hash", "key_hash"),
    )


class UserSession(Base):
    """사용자 세션 모델"""

    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Session info
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True)

    # Client info
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_id = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index("ix_session_token", "session_token"),
        Index("ix_session_user_active", "user_id", "is_active"),
    )


class AuditLog(Base):
    """감사 로그 모델"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Action
    action = Column(String(100), nullable=False)  # login, logout, create_project, etc.
    resource_type = Column(String(50))  # user, project, api_key, etc.
    resource_id = Column(String(100))

    # Details
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    audit_metadata = Column(JSONB)  # Renamed from metadata to avoid SQLAlchemy conflict

    # Result
    status = Column(String(20))  # success, failure, error
    error_message = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("ix_audit_user_action", "user_id", "action"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_created", "created_at"),
    )
