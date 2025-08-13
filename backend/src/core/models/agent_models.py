"""
Agent Database Models
SQLAlchemy models for agent registry and evolution tracking
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class AgentModel(Base):
    """Agent registry model"""

    __tablename__ = "agents"
    __table_args__ = (
        Index("idx_agent_id", "agent_id"),
        Index("idx_agent_name_version", "name", "version"),
        Index("idx_agent_quality", "ai_quality_score"),
        Index("idx_agent_created", "created_at"),
        {"schema": "agents"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False, default="1.0.0")
    code = Column(Text, nullable=False)
    code_hash = Column(String(64), nullable=False)
    description = Column(Text)
    tags = Column(JSON, default=list)

    # AI Analysis fields
    ai_capabilities = Column(JSON, default=dict)
    ai_quality_score = Column(
        Float, CheckConstraint("ai_quality_score >= 0 AND ai_quality_score <= 1")
    )
    ai_analysis_timestamp = Column(DateTime(timezone=True))
    ai_model_used = Column(String(100))
    ai_confidence_score = Column(
        Float, CheckConstraint("ai_confidence_score >= 0 AND ai_confidence_score <= 1")
    )
    ai_suggestions = Column(JSON, default=list)

    # Execution metrics
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_execution_time_ms = Column(Float)
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=False)
    last_executed_at = Column(DateTime(timezone=True))
    deprecated_at = Column(DateTime(timezone=True))
    deprecation_reason = Column(Text)

    # Relationships
    versions = relationship(
        "AgentVersionModel", back_populates="agent", cascade="all, delete-orphan"
    )
    executions = relationship(
        "AgentExecutionModel", back_populates="agent", cascade="all, delete-orphan"
    )
    evolution_history = relationship("AgentEvolutionModel", back_populates="agent")

    def __repr__(self):
        return f"<Agent(id={self.agent_id}, name={self.name}, version={self.version})>"


class AgentVersionModel(Base):
    """Agent version history"""

    __tablename__ = "agent_versions"
    __table_args__ = (
        UniqueConstraint("agent_id", "version"),
        Index("idx_version_agent", "agent_id"),
        Index("idx_version_created", "created_at"),
        {"schema": "agents"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), ForeignKey("agents.agents.agent_id"), nullable=False)
    version = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    code_hash = Column(String(64), nullable=False)

    # Version metadata
    changelog = Column(Text)
    dependencies = Column(JSON, default=dict)
    performance_metrics = Column(JSON, default=dict)
    deployment_status = Column(
        String(50), default="draft"
    )  # draft, testing, production, deprecated

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=False)
    promoted_at = Column(DateTime(timezone=True))
    deprecated_at = Column(DateTime(timezone=True))

    # Relationship
    agent = relationship("AgentModel", back_populates="versions")

    def __repr__(self):
        return f"<AgentVersion(agent={self.agent_id}, version={self.version})>"


class AgentExecutionModel(Base):
    """Agent execution history"""

    __tablename__ = "agent_executions"
    __table_args__ = (
        Index("idx_exec_agent", "agent_id"),
        Index("idx_exec_started", "started_at"),
        Index("idx_exec_status", "status"),
        {"schema": "monitoring"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), ForeignKey("agents.agents.agent_id"), nullable=False)
    execution_id = Column(
        String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    # Execution details
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False)  # pending, running, success, failed, timeout

    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)

    # Performance metrics
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost_usd = Column(Float)
    memory_used_mb = Column(Float)
    cpu_used_percent = Column(Float)

    # Context
    workflow_id = Column(String(100))
    user_id = Column(String(100))
    environment = Column(String(50), default="dev")

    # Relationship
    agent = relationship("AgentModel", back_populates="executions")

    def __repr__(self):
        return (
            f"<AgentExecution(id={self.execution_id}, agent={self.agent_id}, status={self.status})>"
        )


class AgentEvolutionModel(Base):
    """Agent evolution tracking"""

    __tablename__ = "agent_evolutions"
    __table_args__ = (
        Index("idx_evolution_agent", "agent_id"),
        Index("idx_evolution_generation", "generation"),
        Index("idx_evolution_fitness", "fitness_score"),
        {"schema": "evolution"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    evolution_id = Column(
        String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    agent_id = Column(String(100), ForeignKey("agents.agents.agent_id"), nullable=False)

    # Evolution metadata
    generation = Column(Integer, nullable=False)
    parent_agent_id = Column(String(100))
    mutation_type = Column(String(100))  # crossover, mutation, hybrid
    mutation_details = Column(JSON)

    # Fitness evaluation
    fitness_score = Column(Float, nullable=False)
    fitness_components = Column(JSON)  # breakdown of fitness score
    evaluation_metrics = Column(JSON)

    # Genetic information
    genome = Column(JSON)  # genetic representation
    phenotype = Column(JSON)  # expressed characteristics

    # Selection
    selected_for_reproduction = Column(Boolean, default=False)
    offspring_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    evaluated_at = Column(DateTime(timezone=True))

    # Relationship
    agent = relationship("AgentModel", back_populates="evolution_history")

    def __repr__(self):
        return f"<AgentEvolution(id={self.evolution_id}, agent={self.agent_id}, gen={self.generation})>"


class WorkflowModel(Base):
    """Workflow definition model"""

    __tablename__ = "workflows"
    __table_args__ = (
        Index("idx_workflow_name", "name"),
        Index("idx_workflow_status", "status"),
        {"schema": "workflows"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(
        String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    name = Column(String(100), nullable=False)
    version = Column(String(20), default="1.0.0")
    description = Column(Text)

    # Workflow definition
    dag_definition = Column(JSON, nullable=False)  # DAG structure
    agent_nodes = Column(JSON, nullable=False)  # list of agent IDs
    connections = Column(JSON, nullable=False)  # edge definitions

    # Configuration
    config = Column(JSON, default=dict)
    retry_policy = Column(JSON)
    timeout_seconds = Column(Integer, default=3600)

    # Status
    status = Column(String(50), default="draft")  # draft, active, deprecated

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=False)

    # Relationships
    executions = relationship(
        "WorkflowExecutionModel",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Workflow(id={self.workflow_id}, name={self.name})>"


class WorkflowExecutionModel(Base):
    """Workflow execution tracking"""

    __tablename__ = "workflow_executions"
    __table_args__ = (
        Index("idx_wf_exec_workflow", "workflow_id"),
        Index("idx_wf_exec_started", "started_at"),
        Index("idx_wf_exec_status", "status"),
        {"schema": "workflows"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(
        String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    workflow_id = Column(String(100), ForeignKey("workflows.workflows.workflow_id"), nullable=False)

    # Execution details
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False)  # pending, running, success, failed, timeout

    # Execution state
    current_step = Column(String(100))
    steps_completed = Column(JSON, default=list)
    step_results = Column(JSON, default=dict)

    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)

    # Performance
    total_duration_ms = Column(Integer)
    total_cost_usd = Column(Float)

    # Context
    user_id = Column(String(100))
    environment = Column(String(50), default="dev")
    trigger_type = Column(String(50))  # manual, scheduled, api

    # Relationship
    workflow = relationship("WorkflowModel", back_populates="executions")

    def __repr__(self):
        return f"<WorkflowExecution(id={self.execution_id}, workflow={self.workflow_id}, status={self.status})>"
