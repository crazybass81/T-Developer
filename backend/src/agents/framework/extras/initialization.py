from typing import Dict, Any, List, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class InitializationConfig:
    """Configuration for agent initialization"""
    timeout: int = 30000  # milliseconds
    retry_attempts: int = 3
    retry_delay: int = 1000  # milliseconds
    required_resources: List[str] = None
    environment_variables: Dict[str, str] = None
    dependencies: List[str] = None

@dataclass
class InitializationResult:
    """Result of agent initialization"""
    agent_id: str
    success: bool = False
    error: Optional[str] = None
    initialized_at: Optional[datetime] = None
    duration_ms: int = 0

class AgentInitializer:
    """Manages agent initialization process"""
    
    def __init__(self):
        self.initialization_steps: List[str] = [
            "validate_environment",
            "acquire_resources", 
            "resolve_dependencies",
            "configure_agent",
            "run_initialization",
            "verify_initialization"
        ]
        
    async def initialize_agent(
        self,
        agent,
        config: InitializationConfig
    ) -> InitializationResult:
        """Initialize an agent with proper error handling and retries"""
        
        result = InitializationResult(agent_id=agent.agent_id)
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Validate environment
            await self._validate_environment(config)
            
            # Step 2: Check and acquire resources
            resources = await self._acquire_resources(config.required_resources or [])
            
            # Step 3: Resolve dependencies
            dependencies = await self._resolve_dependencies(config.dependencies or [])
            
            # Step 4: Configure agent
            await self._configure_agent(agent, config, resources, dependencies)
            
            # Step 5: Run initialization with timeout
            await asyncio.wait_for(
                agent.initialize(),
                timeout=config.timeout / 1000
            )
            
            # Step 6: Verify initialization
            await self._verify_initialization(agent)
            
            result.success = True
            result.initialized_at = datetime.utcnow()
            
        except asyncio.TimeoutError:
            result.error = "Initialization timeout"
            await self._handle_initialization_failure(agent, result)
            
        except Exception as e:
            result.error = str(e)
            await self._handle_initialization_failure(agent, result)
        
        finally:
            result.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
        return result
    
    async def _validate_environment(self, config: InitializationConfig) -> None:
        """Validate environment variables and settings"""
        if config.environment_variables:
            import os
            for key, expected_value in config.environment_variables.items():
                actual_value = os.getenv(key)
                if actual_value != expected_value:
                    raise ValueError(f"Environment variable {key} mismatch")
    
    async def _acquire_resources(self, required_resources: List[str]) -> Dict[str, Any]:
        """Acquire required resources"""
        resources = {}
        for resource in required_resources:
            # Mock resource acquisition
            resources[resource] = f"acquired_{resource}"
        return resources
    
    async def _resolve_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Resolve agent dependencies"""
        resolved = {}
        for dep in dependencies:
            # Mock dependency resolution
            resolved[dep] = f"resolved_{dep}"
        return resolved
    
    async def _configure_agent(self, agent, config, resources, dependencies) -> None:
        """Configure agent with resources and dependencies"""
        agent.resources = resources
        agent.dependencies = dependencies
    
    async def _verify_initialization(self, agent) -> None:
        """Verify agent is properly initialized"""
        if hasattr(agent, 'health_check'):
            health = await agent.health_check()
            if not health.healthy:
                raise RuntimeError(f"Agent health check failed: {health.status}")
    
    async def _handle_initialization_failure(self, agent, result: InitializationResult) -> None:
        """Handle initialization failure"""
        try:
            await agent.cleanup()
        except Exception as cleanup_error:
            result.error += f"; Cleanup failed: {cleanup_error}"