"""
Base Agent Registry Implementation
Core functionality for agent registration and management
"""

from typing import Dict, Optional, Any, List
import hashlib
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
import boto3
import json
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Agent metadata structure"""
    agent_id: str
    name: str
    version: str
    code_hash: str
    capabilities: Dict[str, Any]
    quality_score: float
    created_at: datetime
    updated_at: datetime
    status: str = 'active'
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class BaseAgentRegistry:
    """Base agent registry with AWS integration"""
    
    def __init__(self, db_session: Optional[AsyncSession] = None, config: Optional[Dict] = None):
        self.db = db_session
        self.config = config or {}
        self.environment = self.config.get('environment', 'dev')
        
        # AWS clients
        self.ssm = boto3.client('ssm', region_name=self.config.get('region', 'us-east-1'))
        self.sm = boto3.client('secretsmanager', region_name=self.config.get('region', 'us-east-1'))
        self.cloudwatch = boto3.client('cloudwatch', region_name=self.config.get('region', 'us-east-1'))
        
        # Caches
        self._agents_cache: Dict[str, Any] = {}
        self._parameters_cache: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        
        # Load configuration from AWS
        self._load_aws_config()
    
    def _load_aws_config(self):
        """Load configuration from AWS Parameter Store"""
        try:
            # Get all parameters for environment
            response = self.ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}',
                Recursive=True,
                WithDecryption=True
            )
            
            for param in response['Parameters']:
                key = param['Name'].replace(f'/t-developer/{self.environment}/', '')
                self._parameters_cache[key] = param['Value']
            
            logger.info(f"Loaded {len(self._parameters_cache)} parameters from AWS")
            
        except Exception as e:
            logger.warning(f"Could not load AWS parameters: {e}")
    
    def _get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Get secret from AWS Secrets Manager"""
        try:
            response = self.sm.get_secret_value(
                SecretId=f'/t-developer/{self.environment}/{secret_name}'
            )
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            return {}
    
    def _get_parameter(self, param_name: str, default: Any = None) -> str:
        """Get parameter from cache or AWS Parameter Store"""
        # Check cache first
        if param_name in self._parameters_cache:
            return self._parameters_cache[param_name]
        
        # Fetch from AWS
        try:
            response = self.ssm.get_parameter(
                Name=f'/t-developer/{self.environment}/{param_name}',
                WithDecryption=True
            )
            value = response['Parameter']['Value']
            self._parameters_cache[param_name] = value
            return value
        except Exception as e:
            logger.warning(f"Parameter {param_name} not found: {e}")
            return default
    
    def _calculate_code_hash(self, code: str) -> str:
        """Calculate SHA256 hash of code"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    async def _validate_agent_code(self, code: str) -> tuple[bool, List[str]]:
        """Validate agent code structure"""
        errors = []
        
        # Check for required methods
        required_methods = ['__init__', 'execute', 'get_capabilities']
        for method in required_methods:
            if f'def {method}' not in code and f'async def {method}' not in code:
                errors.append(f"Missing required method: {method}")
        
        # Check for basic structure
        if 'class' not in code:
            errors.append("No class definition found")
        
        # Check for imports
        if 'import' not in code:
            errors.append("No import statements found")
        
        # Security checks
        dangerous_patterns = ['eval(', 'exec(', '__import__', 'compile(', 'globals()', 'locals()']
        for pattern in dangerous_patterns:
            if pattern in code:
                errors.append(f"Dangerous pattern detected: {pattern}")
        
        return len(errors) == 0, errors
    
    async def register_agent(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """Register a new agent"""
        async with self._lock:
            try:
                # Validate required fields
                required_fields = ['name', 'code']
                for field in required_fields:
                    if field not in agent_data:
                        raise ValueError(f"Missing required field: {field}")
                
                # Generate agent ID if not provided
                agent_id = agent_data.get('agent_id') or f"agent_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(agent_data['name'].encode()).hexdigest()[:8]}"
                
                # Calculate code hash
                code_hash = self._calculate_code_hash(agent_data['code'])
                
                # Validate code
                is_valid, errors = await self._validate_agent_code(agent_data['code'])
                if not is_valid:
                    logger.error(f"Code validation failed for {agent_id}: {errors}")
                    raise ValueError(f"Code validation failed: {', '.join(errors)}")
                
                # Create metadata
                metadata = AgentMetadata(
                    agent_id=agent_id,
                    name=agent_data['name'],
                    version=agent_data.get('version', '1.0.0'),
                    code_hash=code_hash,
                    capabilities=agent_data.get('capabilities', {}),
                    quality_score=agent_data.get('quality_score', 0.0),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # Store in cache
                self._agents_cache[agent_id] = {
                    'metadata': metadata,
                    'code': agent_data['code']
                }
                
                # Store in database if available
                if self.db:
                    await self._store_agent_in_db(metadata, agent_data['code'])
                
                # Send metrics to CloudWatch
                await self._send_metrics('AgentRegistered', 1, {'AgentId': agent_id})
                
                logger.info(f"Successfully registered agent: {agent_id}")
                return agent_id
                
            except Exception as e:
                logger.error(f"Failed to register agent: {e}")
                await self._send_metrics('AgentRegistrationFailed', 1)
                return None
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        # Check cache first
        if agent_id in self._agents_cache:
            return self._agents_cache[agent_id]
        
        # Load from database if available
        if self.db:
            agent = await self._load_agent_from_db(agent_id)
            if agent:
                self._agents_cache[agent_id] = agent
                return agent
        
        return None
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Update agent information"""
        async with self._lock:
            try:
                agent = await self.get_agent(agent_id)
                if not agent:
                    logger.error(f"Agent {agent_id} not found")
                    return False
                
                # Update metadata
                metadata = agent['metadata']
                if isinstance(metadata, dict):
                    metadata = AgentMetadata(**metadata)
                
                # Update fields
                if 'name' in updates:
                    metadata.name = updates['name']
                if 'version' in updates:
                    metadata.version = updates['version']
                if 'capabilities' in updates:
                    metadata.capabilities = updates['capabilities']
                if 'quality_score' in updates:
                    metadata.quality_score = updates['quality_score']
                if 'code' in updates:
                    agent['code'] = updates['code']
                    metadata.code_hash = self._calculate_code_hash(updates['code'])
                
                metadata.updated_at = datetime.utcnow()
                
                # Update cache
                agent['metadata'] = metadata
                self._agents_cache[agent_id] = agent
                
                # Update database if available
                if self.db:
                    await self._update_agent_in_db(agent_id, metadata, agent.get('code'))
                
                # Send metrics
                await self._send_metrics('AgentUpdated', 1, {'AgentId': agent_id})
                
                logger.info(f"Successfully updated agent: {agent_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update agent {agent_id}: {e}")
                return False
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent"""
        async with self._lock:
            try:
                # Remove from cache
                if agent_id in self._agents_cache:
                    del self._agents_cache[agent_id]
                
                # Remove from database if available
                if self.db:
                    await self._delete_agent_from_db(agent_id)
                
                # Send metrics
                await self._send_metrics('AgentDeleted', 1, {'AgentId': agent_id})
                
                logger.info(f"Successfully deleted agent: {agent_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete agent {agent_id}: {e}")
                return False
    
    async def list_agents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all agents with optional filters"""
        agents = []
        
        # Get from cache
        for agent_id, agent_data in self._agents_cache.items():
            metadata = agent_data['metadata']
            if isinstance(metadata, AgentMetadata):
                metadata = metadata.to_dict()
            
            # Apply filters
            if filters:
                match = True
                for key, value in filters.items():
                    if key in metadata and metadata[key] != value:
                        match = False
                        break
                if not match:
                    continue
            
            agents.append({
                'agent_id': agent_id,
                'metadata': metadata
            })
        
        # Load from database if cache is empty and db is available
        if not agents and self.db:
            agents = await self._load_agents_from_db(filters)
        
        return agents
    
    async def update_execution_metrics(self, agent_id: str, success: bool, execution_time_ms: float):
        """Update agent execution metrics"""
        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                return
            
            metadata = agent['metadata']
            if isinstance(metadata, dict):
                metadata = AgentMetadata(**metadata)
            
            # Update counters
            metadata.execution_count += 1
            if success:
                metadata.success_count += 1
            else:
                metadata.failure_count += 1
            
            # Update cache
            agent['metadata'] = metadata
            self._agents_cache[agent_id] = agent
            
            # Send metrics to CloudWatch
            await self._send_metrics('AgentExecution', 1, {
                'AgentId': agent_id,
                'Status': 'Success' if success else 'Failure'
            })
            
            await self._send_metrics('AgentExecutionTime', execution_time_ms, {
                'AgentId': agent_id
            }, unit='Milliseconds')
            
        except Exception as e:
            logger.error(f"Failed to update execution metrics for {agent_id}: {e}")
    
    async def _send_metrics(self, metric_name: str, value: float, dimensions: Optional[Dict] = None, unit: str = 'Count'):
        """Send metrics to CloudWatch"""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
            
            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': str(v)} for k, v in dimensions.items()
                ]
            
            self.cloudwatch.put_metric_data(
                Namespace='TDeveloper/Registry',
                MetricData=[metric_data]
            )
            
        except Exception as e:
            logger.warning(f"Failed to send metric {metric_name}: {e}")
    
    # Database operations (to be implemented with actual ORM)
    async def _store_agent_in_db(self, metadata: AgentMetadata, code: str):
        """Store agent in database"""
        # Implementation depends on actual database schema
        pass
    
    async def _load_agent_from_db(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent from database"""
        # Implementation depends on actual database schema
        return None
    
    async def _update_agent_in_db(self, agent_id: str, metadata: AgentMetadata, code: Optional[str]):
        """Update agent in database"""
        # Implementation depends on actual database schema
        pass
    
    async def _delete_agent_from_db(self, agent_id: str):
        """Delete agent from database"""
        # Implementation depends on actual database schema
        pass
    
    async def _load_agents_from_db(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Load agents from database"""
        # Implementation depends on actual database schema
        return []