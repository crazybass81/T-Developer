"""
Agent Repository Implementation
Database operations for agent storage and retrieval
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
import json
import logging

from src.core.models.agent_models import AgentModel, AgentVersionModel, AgentExecutionModel

logger = logging.getLogger(__name__)


class AgentRepository:
    """Repository for agent database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_agent(self, agent_data: Dict[str, Any]) -> str:
        """Save a new agent to database"""
        try:
            # Create agent model
            agent = AgentModel(
                agent_id=agent_data['agent_id'],
                name=agent_data['name'],
                version=agent_data.get('version', '1.0.0'),
                code=agent_data['code'],
                code_hash=agent_data['code_hash'],
                ai_capabilities=agent_data.get('ai_capabilities', {}),
                ai_quality_score=agent_data.get('ai_quality_score'),
                ai_analysis_timestamp=agent_data.get('ai_analysis_timestamp', datetime.utcnow()),
                ai_model_used=agent_data.get('ai_model_used', 'gpt-4-turbo'),
                created_by=agent_data.get('created_by', 'system')
            )
            
            self.session.add(agent)
            
            # Also create version record
            version = AgentVersionModel(
                agent_id=agent_data['agent_id'],
                version=agent_data.get('version', '1.0.0'),
                code=agent_data['code'],
                dependencies=agent_data.get('dependencies', {}),
                changelog=agent_data.get('changelog', 'Initial version'),
                created_by=agent_data.get('created_by', 'system')
            )
            
            self.session.add(version)
            
            await self.session.commit()
            await self.session.refresh(agent)
            
            logger.info(f"Saved agent {agent.agent_id} to database")
            return str(agent.id)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save agent: {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        try:
            result = await self.session.execute(
                select(AgentModel).where(AgentModel.agent_id == agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if agent:
                return self._model_to_dict(agent)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    async def get_agent_by_name(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get agent by name and optional version"""
        try:
            query = select(AgentModel).where(AgentModel.name == name)
            
            if version:
                query = query.where(AgentModel.version == version)
            else:
                # Get latest version
                query = query.order_by(AgentModel.created_at.desc()).limit(1)
            
            result = await self.session.execute(query)
            agent = result.scalar_one_or_none()
            
            if agent:
                return self._model_to_dict(agent)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get agent by name {name}: {e}")
            return None
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Update agent information"""
        try:
            # Build update statement
            stmt = update(AgentModel).where(
                AgentModel.agent_id == agent_id
            ).values(
                **updates,
                updated_at=datetime.utcnow()
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Updated agent {agent_id}")
                return True
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update agent {agent_id}: {e}")
            return False
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent (soft delete by setting deprecated_at)"""
        try:
            stmt = update(AgentModel).where(
                AgentModel.agent_id == agent_id
            ).values(
                deprecated_at=datetime.utcnow(),
                deprecation_reason='Deleted by user'
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Soft deleted agent {agent_id}")
                return True
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            return False
    
    async def list_agents(self, 
                         filters: Optional[Dict[str, Any]] = None,
                         limit: int = 100,
                         offset: int = 0) -> List[Dict[str, Any]]:
        """List agents with optional filters"""
        try:
            query = select(AgentModel)
            
            # Apply filters
            if filters:
                conditions = []
                
                if 'status' in filters:
                    # Active means no deprecation_at
                    if filters['status'] == 'active':
                        conditions.append(AgentModel.deprecated_at.is_(None))
                    elif filters['status'] == 'deprecated':
                        conditions.append(AgentModel.deprecated_at.isnot(None))
                
                if 'min_quality_score' in filters:
                    conditions.append(
                        AgentModel.ai_quality_score >= filters['min_quality_score']
                    )
                
                if 'created_after' in filters:
                    conditions.append(
                        AgentModel.created_at >= filters['created_after']
                    )
                
                if 'created_by' in filters:
                    conditions.append(
                        AgentModel.created_by == filters['created_by']
                    )
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            # Order by creation date (newest first)
            query = query.order_by(AgentModel.created_at.desc())
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            result = await self.session.execute(query)
            agents = result.scalars().all()
            
            return [self._model_to_dict(agent) for agent in agents]
            
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []
    
    async def update_execution_metrics(self, 
                                      agent_id: str,
                                      execution_data: Dict[str, Any]) -> bool:
        """Update agent execution metrics"""
        try:
            # Record execution
            execution = AgentExecutionModel(
                agent_id=agent_id,
                execution_id=execution_data['execution_id'],
                started_at=execution_data['started_at'],
                completed_at=execution_data.get('completed_at'),
                status=execution_data['status'],
                input_data=execution_data.get('input_data'),
                output_data=execution_data.get('output_data'),
                error_message=execution_data.get('error_message'),
                execution_time_ms=execution_data.get('execution_time_ms'),
                tokens_used=execution_data.get('tokens_used'),
                cost_usd=execution_data.get('cost_usd'),
                memory_used_mb=execution_data.get('memory_used_mb'),
                cpu_used_percent=execution_data.get('cpu_used_percent'),
                workflow_id=execution_data.get('workflow_id'),
                user_id=execution_data.get('user_id'),
                environment=execution_data.get('environment', 'dev')
            )
            
            self.session.add(execution)
            
            # Update agent metrics
            stmt = update(AgentModel).where(
                AgentModel.agent_id == agent_id
            ).values(
                execution_count=AgentModel.execution_count + 1,
                success_count=AgentModel.success_count + (
                    1 if execution_data['status'] == 'success' else 0
                ),
                failure_count=AgentModel.failure_count + (
                    1 if execution_data['status'] == 'failed' else 0
                ),
                total_tokens_used=AgentModel.total_tokens_used + (
                    execution_data.get('tokens_used', 0)
                ),
                total_cost_usd=AgentModel.total_cost_usd + (
                    execution_data.get('cost_usd', 0)
                ),
                last_executed_at=datetime.utcnow()
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            logger.info(f"Updated execution metrics for agent {agent_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update execution metrics: {e}")
            return False
    
    async def get_agent_versions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all versions of an agent"""
        try:
            result = await self.session.execute(
                select(AgentVersionModel)
                .where(AgentVersionModel.agent_id == agent_id)
                .order_by(AgentVersionModel.created_at.desc())
            )
            versions = result.scalars().all()
            
            return [self._version_to_dict(v) for v in versions]
            
        except Exception as e:
            logger.error(f"Failed to get agent versions: {e}")
            return []
    
    async def get_agent_executions(self, 
                                  agent_id: str,
                                  limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent executions of an agent"""
        try:
            result = await self.session.execute(
                select(AgentExecutionModel)
                .where(AgentExecutionModel.agent_id == agent_id)
                .order_by(AgentExecutionModel.started_at.desc())
                .limit(limit)
            )
            executions = result.scalars().all()
            
            return [self._execution_to_dict(e) for e in executions]
            
        except Exception as e:
            logger.error(f"Failed to get agent executions: {e}")
            return []
    
    async def get_top_agents_by_quality(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top agents by quality score"""
        try:
            result = await self.session.execute(
                select(AgentModel)
                .where(AgentModel.deprecated_at.is_(None))
                .order_by(AgentModel.ai_quality_score.desc())
                .limit(limit)
            )
            agents = result.scalars().all()
            
            return [self._model_to_dict(agent) for agent in agents]
            
        except Exception as e:
            logger.error(f"Failed to get top agents: {e}")
            return []
    
    async def get_most_used_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently used agents"""
        try:
            result = await self.session.execute(
                select(AgentModel)
                .where(AgentModel.deprecated_at.is_(None))
                .order_by(AgentModel.execution_count.desc())
                .limit(limit)
            )
            agents = result.scalars().all()
            
            return [self._model_to_dict(agent) for agent in agents]
            
        except Exception as e:
            logger.error(f"Failed to get most used agents: {e}")
            return []
    
    def _model_to_dict(self, model: AgentModel) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
        return {
            'id': str(model.id),
            'agent_id': model.agent_id,
            'name': model.name,
            'version': model.version,
            'code': model.code,
            'code_hash': model.code_hash,
            'ai_capabilities': model.ai_capabilities,
            'ai_quality_score': float(model.ai_quality_score) if model.ai_quality_score else None,
            'ai_analysis_timestamp': model.ai_analysis_timestamp.isoformat() if model.ai_analysis_timestamp else None,
            'ai_model_used': model.ai_model_used,
            'ai_confidence_score': float(model.ai_confidence_score) if model.ai_confidence_score else None,
            'ai_suggestions': model.ai_suggestions,
            'execution_count': model.execution_count,
            'success_count': model.success_count,
            'failure_count': model.failure_count,
            'avg_execution_time_ms': float(model.avg_execution_time_ms) if model.avg_execution_time_ms else None,
            'total_tokens_used': model.total_tokens_used,
            'total_cost_usd': float(model.total_cost_usd) if model.total_cost_usd else None,
            'created_at': model.created_at.isoformat(),
            'updated_at': model.updated_at.isoformat(),
            'created_by': model.created_by,
            'last_executed_at': model.last_executed_at.isoformat() if model.last_executed_at else None,
            'deprecated_at': model.deprecated_at.isoformat() if model.deprecated_at else None,
            'deprecation_reason': model.deprecation_reason
        }
    
    def _version_to_dict(self, model: AgentVersionModel) -> Dict[str, Any]:
        """Convert version model to dictionary"""
        return {
            'id': str(model.id),
            'agent_id': model.agent_id,
            'version': model.version,
            'code': model.code,
            'dependencies': model.dependencies,
            'changelog': model.changelog,
            'performance_metrics': model.performance_metrics,
            'deployment_status': model.deployment_status,
            'created_at': model.created_at.isoformat(),
            'created_by': model.created_by
        }
    
    def _execution_to_dict(self, model: AgentExecutionModel) -> Dict[str, Any]:
        """Convert execution model to dictionary"""
        return {
            'id': str(model.id),
            'agent_id': model.agent_id,
            'execution_id': model.execution_id,
            'started_at': model.started_at.isoformat(),
            'completed_at': model.completed_at.isoformat() if model.completed_at else None,
            'status': model.status,
            'execution_time_ms': model.execution_time_ms,
            'tokens_used': model.tokens_used,
            'cost_usd': float(model.cost_usd) if model.cost_usd else None,
            'memory_used_mb': float(model.memory_used_mb) if model.memory_used_mb else None,
            'cpu_used_percent': float(model.cpu_used_percent) if model.cpu_used_percent else None,
            'error_message': model.error_message,
            'workflow_id': model.workflow_id,
            'user_id': model.user_id,
            'environment': model.environment
        }