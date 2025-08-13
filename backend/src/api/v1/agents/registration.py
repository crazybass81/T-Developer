"""
Agent Registration API Endpoints
FastAPI routes for agent registration and management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional, List, Any
from datetime import datetime
from uuid import uuid4
import structlog
import hashlib

from src.core.database import get_db
from src.core.registry.base_registry import BaseAgentRegistry
from src.core.registry.agent_repository import AgentRepository
from src.core.registry.ai_capability_analyzer import AICapabilityAnalyzer
from src.api.v1.models.agent_models import (
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    AgentUpdateRequest,
    AgentListResponse,
    AgentDetailResponse,
)
from src.core.auth.dependencies import get_current_user, User
from src.core.validation.code_validator import CodeValidator

router = APIRouter(prefix="/api/v1/agents", tags=["agent-registration"])
logger = structlog.get_logger()


@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(
    request: AgentRegistrationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register a new agent with AI analysis

    This endpoint:
    1. Validates the agent code
    2. Initiates AI analysis in background
    3. Stores agent in registry
    4. Returns registration status
    """

    try:
        # Check user permissions
        if not current_user.has_permission("agent:create"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create agents",
            )

        # Initialize validator
        validator = CodeValidator()

        # Validate agent code
        validation_result = await validator.validate(request.agent_code)

        if not validation_result.is_valid:
            return AgentRegistrationResponse(
                status="validation_failed",
                errors=validation_result.errors,
                message="Agent code validation failed",
            )

        # Generate agent ID
        agent_id = f"agent_{uuid4().hex[:8]}_{datetime.utcnow().strftime('%Y%m%d')}"

        # Calculate code hash
        code_hash = hashlib.sha256(request.agent_code.encode()).hexdigest()

        # Create initial agent data
        agent_data = {
            "agent_id": agent_id,
            "name": request.agent_name,
            "version": request.version or "1.0.0",
            "code": request.agent_code,
            "code_hash": code_hash,
            "description": request.description,
            "tags": request.tags or [],
            "created_by": current_user.username,
            "created_at": datetime.utcnow(),
            "status": "analyzing",
        }

        # Initialize registry and save agent
        registry = BaseAgentRegistry(db)
        saved_agent_id = await registry.register_agent(agent_data)

        if not saved_agent_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register agent",
            )

        # Create background task for AI analysis
        analysis_task_id = str(uuid4())
        background_tasks.add_task(
            analyze_agent_with_ai,
            agent_id=saved_agent_id,
            agent_code=request.agent_code,
            agent_name=request.agent_name,
            task_id=analysis_task_id,
            db=db,
            user_id=current_user.id,
        )

        logger.info(
            "Agent registration initiated",
            agent_id=saved_agent_id,
            user=current_user.username,
            analysis_task_id=analysis_task_id,
        )

        return AgentRegistrationResponse(
            status="processing",
            agent_id=saved_agent_id,
            analysis_task_id=analysis_task_id,
            message="Agent registered successfully. AI analysis in progress.",
            estimated_completion_time=30,  # seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Agent registration failed", error=str(e), user=current_user.username
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.get("/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get agent details by ID"""

    try:
        # Check permissions
        if not current_user.has_permission("agent:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to read agents",
            )

        # Get agent from repository
        repository = AgentRepository(db)
        agent = await repository.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        # Get execution history
        executions = await repository.get_agent_executions(agent_id, limit=10)

        # Get versions
        versions = await repository.get_agent_versions(agent_id)

        return AgentDetailResponse(
            agent_id=agent["agent_id"],
            name=agent["name"],
            version=agent["version"],
            description=agent.get("description"),
            code=agent["code"]
            if current_user.has_permission("agent:code:read")
            else None,
            ai_capabilities=agent.get("ai_capabilities", {}),
            ai_quality_score=agent.get("ai_quality_score"),
            execution_count=agent.get("execution_count", 0),
            success_rate=calculate_success_rate(agent),
            last_executed_at=agent.get("last_executed_at"),
            created_at=agent["created_at"],
            created_by=agent["created_by"],
            versions=versions,
            recent_executions=executions,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent: {str(e)}",
        )


@router.put("/{agent_id}", response_model=Dict[str, Any])
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update agent information"""

    try:
        # Check permissions
        if not current_user.has_permission("agent:update"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update agents",
            )

        # Build update data
        updates = {}
        if request.name:
            updates["name"] = request.name
        if request.description:
            updates["description"] = request.description
        if request.tags:
            updates["tags"] = request.tags
        if request.version:
            updates["version"] = request.version

        # If code is updated, revalidate and reanalyze
        if request.code:
            validator = CodeValidator()
            validation_result = await validator.validate(request.code)

            if not validation_result.is_valid:
                return {
                    "status": "validation_failed",
                    "errors": validation_result.errors,
                }

            updates["code"] = request.code
            updates["code_hash"] = hashlib.sha256(request.code.encode()).hexdigest()

            # Trigger re-analysis in background
            background_tasks.add_task(
                analyze_agent_with_ai,
                agent_id=agent_id,
                agent_code=request.code,
                agent_name=request.name or agent_id,
                task_id=str(uuid4()),
                db=db,
                user_id=current_user.id,
            )

        # Update agent
        repository = AgentRepository(db)
        success = await repository.update_agent(agent_id, updates)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found or update failed",
            )

        logger.info(f"Agent {agent_id} updated", user=current_user.username)

        return {
            "status": "success",
            "agent_id": agent_id,
            "message": "Agent updated successfully",
            "reanalysis_triggered": "code" in updates,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent {agent_id}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}",
        )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (deprecate) an agent"""

    try:
        # Check permissions
        if not current_user.has_permission("agent:delete"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete agents",
            )

        # Soft delete the agent
        repository = AgentRepository(db)
        success = await repository.delete_agent(agent_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        logger.info(f"Agent {agent_id} deleted", user=current_user.username)

        return {"status": "success", "message": f"Agent {agent_id} has been deprecated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent {agent_id}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}",
        )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None,
    min_quality_score: Optional[float] = None,
    created_by: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List agents with optional filters"""

    try:
        # Check permissions
        if not current_user.has_permission("agent:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to list agents",
            )

        # Build filters
        filters = {}
        if status:
            filters["status"] = status
        if min_quality_score:
            filters["min_quality_score"] = min_quality_score
        if created_by:
            filters["created_by"] = created_by

        # Get agents from repository
        repository = AgentRepository(db)
        agents = await repository.list_agents(
            filters=filters, limit=limit, offset=offset
        )

        # Get total count
        total_count = len(agents)  # In production, use a separate count query

        return AgentListResponse(
            agents=agents, total_count=total_count, limit=limit, offset=offset
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list agents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}",
        )


@router.get("/top/quality", response_model=List[Dict[str, Any]])
async def get_top_quality_agents(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get top agents by quality score"""

    try:
        repository = AgentRepository(db)
        agents = await repository.get_top_agents_by_quality(limit=limit)

        return agents

    except Exception as e:
        logger.error("Failed to get top quality agents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top agents: {str(e)}",
        )


@router.get("/top/usage", response_model=List[Dict[str, Any]])
async def get_most_used_agents(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get most frequently used agents"""

    try:
        repository = AgentRepository(db)
        agents = await repository.get_most_used_agents(limit=limit)

        return agents

    except Exception as e:
        logger.error("Failed to get most used agents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get most used agents: {str(e)}",
        )


# Background task for AI analysis
async def analyze_agent_with_ai(
    agent_id: str,
    agent_code: str,
    agent_name: str,
    task_id: str,
    db: AsyncSession,
    user_id: str,
):
    """Background task to analyze agent with AI"""

    try:
        logger.info(f"Starting AI analysis for agent {agent_id}", task_id=task_id)

        # Initialize AI analyzer
        analyzer = AICapabilityAnalyzer()

        # Analyze capabilities
        capabilities = await analyzer.analyze_capabilities(agent_code)

        # Assess quality
        quality_score = await analyzer.assess_quality(agent_code)

        # Get optimization suggestions
        suggestions = await analyzer.get_optimization_suggestions(agent_code)

        # Update agent with AI analysis results
        repository = AgentRepository(db)
        await repository.update_agent(
            agent_id,
            {
                "ai_capabilities": capabilities,
                "ai_quality_score": quality_score,
                "ai_analysis_timestamp": datetime.utcnow(),
                "ai_model_used": "gpt-4-turbo/claude-3-opus",
                "ai_suggestions": suggestions,
                "ai_confidence_score": capabilities.get("confidence_score", 0.0),
                "status": "active",
            },
        )

        # Update task status (would be in a task tracking table)
        logger.info(
            f"AI analysis completed for agent {agent_id}",
            task_id=task_id,
            quality_score=quality_score,
        )

        # Send notification if needed
        # await notify_user(user_id, agent_id, "analysis_complete")

    except Exception as e:
        logger.error(
            f"AI analysis failed for agent {agent_id}", task_id=task_id, error=str(e)
        )

        # Update agent status to indicate analysis failure
        try:
            repository = AgentRepository(db)
            await repository.update_agent(
                agent_id,
                {"status": "analysis_failed", "ai_suggestions": {"error": str(e)}},
            )
        except:
            pass


def calculate_success_rate(agent: Dict[str, Any]) -> float:
    """Calculate agent success rate"""
    execution_count = agent.get("execution_count", 0)
    if execution_count == 0:
        return 0.0

    success_count = agent.get("success_count", 0)
    return (success_count / execution_count) * 100
