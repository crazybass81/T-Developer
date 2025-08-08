# backend/src/agents/framework/deployment_scaling.py
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from datetime import datetime, timedelta

class ScalingPolicy(Enum):
    MANUAL = "manual"
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    QUEUE_BASED = "queue_based"
    CUSTOM = "custom"

@dataclass
class ScalingConfig:
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_percent: float = 70.0
    target_memory_percent: float = 80.0
    target_queue_length: int = 100
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3

@dataclass
class DeploymentTarget:
    target_id: str
    target_type: str  # local, kubernetes, lambda, ecs
    endpoint: str
    credentials: Dict[str, Any]
    config: Dict[str, Any]

class AgentDeploymentManager:
    def __init__(self):
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.scaling_configs: Dict[str, ScalingConfig] = {}
        self.deployment_targets: Dict[str, DeploymentTarget] = {}
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.last_scaling_action: Dict[str, datetime] = {}
        self.metrics_collectors: Dict[str, Callable] = {}
    
    def register_deployment_target(self, target: DeploymentTarget):
        """Register a deployment target"""
        self.deployment_targets[target.target_id] = target
    
    def register_metrics_collector(self, agent_id: str, collector: Callable):
        """Register metrics collector for an agent"""
        self.metrics_collectors[agent_id] = collector
    
    async def deploy_agent(self, 
                          agent_id: str,
                          version: str,
                          target_id: str,
                          instances: int = 1,
                          config: Dict[str, Any] = None) -> bool:
        """Deploy agent to target"""
        target = self.deployment_targets.get(target_id)
        if not target:
            raise ValueError(f"Deployment target {target_id} not found")
        
        deployment_info = {
            "agent_id": agent_id,
            "version": version,
            "target_id": target_id,
            "instances": instances,
            "config": config or {},
            "deployed_at": datetime.utcnow(),
            "status": "deploying"
        }
        
        try:
            # Deploy based on target type
            if target.target_type == "kubernetes":
                success = await self._deploy_to_kubernetes(agent_id, version, target, instances, config)
            elif target.target_type == "lambda":
                success = await self._deploy_to_lambda(agent_id, version, target, config)
            elif target.target_type == "ecs":
                success = await self._deploy_to_ecs(agent_id, version, target, instances, config)
            else:
                success = await self._deploy_local(agent_id, version, target, instances, config)
            
            deployment_info["status"] = "deployed" if success else "failed"
            self.deployments[f"{agent_id}:{target_id}"] = deployment_info
            
            return success
            
        except Exception as e:
            deployment_info["status"] = "failed"
            deployment_info["error"] = str(e)
            self.deployments[f"{agent_id}:{target_id}"] = deployment_info
            return False
    
    async def _deploy_to_kubernetes(self, agent_id: str, version: str, target: DeploymentTarget, instances: int, config: Dict[str, Any]) -> bool:
        """Deploy to Kubernetes"""
        # This would integrate with Kubernetes API
        # For now, simulate deployment
        await asyncio.sleep(2)  # Simulate deployment time
        return True
    
    async def _deploy_to_lambda(self, agent_id: str, version: str, target: DeploymentTarget, config: Dict[str, Any]) -> bool:
        """Deploy to AWS Lambda"""
        # This would integrate with AWS Lambda API
        await asyncio.sleep(1)
        return True
    
    async def _deploy_to_ecs(self, agent_id: str, version: str, target: DeploymentTarget, instances: int, config: Dict[str, Any]) -> bool:
        """Deploy to AWS ECS"""
        # This would integrate with AWS ECS API
        await asyncio.sleep(3)
        return True
    
    async def _deploy_local(self, agent_id: str, version: str, target: DeploymentTarget, instances: int, config: Dict[str, Any]) -> bool:
        """Deploy locally"""
        # This would start local processes
        await asyncio.sleep(0.5)
        return True
    
    def configure_auto_scaling(self, agent_id: str, target_id: str, policy: ScalingPolicy, config: ScalingConfig):
        """Configure auto-scaling for deployed agent"""
        key = f"{agent_id}:{target_id}"
        self.scaling_configs[key] = config
        self.scaling_policies[key] = policy
    
    async def start_auto_scaling(self, agent_id: str, target_id: str):
        """Start auto-scaling monitoring"""
        key = f"{agent_id}:{target_id}"
        
        if key not in self.scaling_policies:
            raise ValueError(f"No scaling policy configured for {key}")
        
        # Start scaling loop
        asyncio.create_task(self._scaling_loop(agent_id, target_id))
    
    async def _scaling_loop(self, agent_id: str, target_id: str):
        """Auto-scaling monitoring loop"""
        key = f"{agent_id}:{target_id}"
        
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                policy = self.scaling_policies.get(key)
                config = self.scaling_configs.get(key)
                
                if not policy or not config:
                    continue
                
                # Get current metrics
                metrics = await self._collect_metrics(agent_id, target_id)
                if not metrics:
                    continue
                
                # Determine scaling action
                action = self._determine_scaling_action(key, metrics, config, policy)
                
                if action:
                    await self._execute_scaling_action(agent_id, target_id, action)
                
            except Exception as e:
                print(f"Scaling loop error for {key}: {e}")
    
    async def _collect_metrics(self, agent_id: str, target_id: str) -> Optional[Dict[str, float]]:
        """Collect metrics for scaling decisions"""
        collector = self.metrics_collectors.get(agent_id)
        if not collector:
            return None
        
        try:
            return await collector()
        except Exception as e:
            print(f"Metrics collection error: {e}")
            return None
    
    def _determine_scaling_action(self, key: str, metrics: Dict[str, float], config: ScalingConfig, policy: ScalingPolicy) -> Optional[str]:
        """Determine if scaling action is needed"""
        deployment = self.deployments.get(key)
        if not deployment:
            return None
        
        current_instances = deployment.get("instances", 1)
        
        # Check cooldown periods
        last_action = self.last_scaling_action.get(key)
        if last_action:
            time_since_last = (datetime.utcnow() - last_action).total_seconds()
            if time_since_last < config.scale_up_cooldown:
                return None
        
        # Determine scaling need based on policy
        scale_up_needed = False
        scale_down_needed = False
        
        if policy == ScalingPolicy.CPU_BASED:
            cpu_usage = metrics.get("cpu_percent", 0)
            scale_up_needed = cpu_usage > config.target_cpu_percent * config.scale_up_threshold
            scale_down_needed = cpu_usage < config.target_cpu_percent * config.scale_down_threshold
        
        elif policy == ScalingPolicy.MEMORY_BASED:
            memory_usage = metrics.get("memory_percent", 0)
            scale_up_needed = memory_usage > config.target_memory_percent * config.scale_up_threshold
            scale_down_needed = memory_usage < config.target_memory_percent * config.scale_down_threshold
        
        elif policy == ScalingPolicy.QUEUE_BASED:
            queue_length = metrics.get("queue_length", 0)
            scale_up_needed = queue_length > config.target_queue_length * config.scale_up_threshold
            scale_down_needed = queue_length < config.target_queue_length * config.scale_down_threshold
        
        # Determine action
        if scale_up_needed and current_instances < config.max_instances:
            return "scale_up"
        elif scale_down_needed and current_instances > config.min_instances:
            return "scale_down"
        
        return None
    
    async def _execute_scaling_action(self, agent_id: str, target_id: str, action: str):
        """Execute scaling action"""
        key = f"{agent_id}:{target_id}"
        deployment = self.deployments.get(key)
        
        if not deployment:
            return
        
        current_instances = deployment["instances"]
        
        if action == "scale_up":
            new_instances = min(current_instances + 1, self.scaling_configs[key].max_instances)
        elif action == "scale_down":
            new_instances = max(current_instances - 1, self.scaling_configs[key].min_instances)
        else:
            return
        
        if new_instances != current_instances:
            success = await self._scale_instances(agent_id, target_id, new_instances)
            
            if success:
                deployment["instances"] = new_instances
                self.last_scaling_action[key] = datetime.utcnow()
                print(f"Scaled {key} from {current_instances} to {new_instances} instances")
    
    async def _scale_instances(self, agent_id: str, target_id: str, new_count: int) -> bool:
        """Scale instances to new count"""
        target = self.deployment_targets.get(target_id)
        if not target:
            return False
        
        try:
            # Scale based on target type
            if target.target_type == "kubernetes":
                return await self._scale_kubernetes(agent_id, target, new_count)
            elif target.target_type == "ecs":
                return await self._scale_ecs(agent_id, target, new_count)
            else:
                return await self._scale_local(agent_id, target, new_count)
        
        except Exception as e:
            print(f"Scaling error: {e}")
            return False
    
    async def _scale_kubernetes(self, agent_id: str, target: DeploymentTarget, new_count: int) -> bool:
        """Scale Kubernetes deployment"""
        # This would use kubectl or Kubernetes API
        await asyncio.sleep(1)
        return True
    
    async def _scale_ecs(self, agent_id: str, target: DeploymentTarget, new_count: int) -> bool:
        """Scale ECS service"""
        # This would use AWS ECS API
        await asyncio.sleep(1)
        return True
    
    async def _scale_local(self, agent_id: str, target: DeploymentTarget, new_count: int) -> bool:
        """Scale local processes"""
        # This would manage local process pool
        await asyncio.sleep(0.5)
        return True
    
    def get_deployment_status(self, agent_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        key = f"{agent_id}:{target_id}"
        return self.deployments.get(key)
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments"""
        return list(self.deployments.values())
    
    async def undeploy_agent(self, agent_id: str, target_id: str) -> bool:
        """Undeploy agent from target"""
        key = f"{agent_id}:{target_id}"
        
        if key not in self.deployments:
            return False
        
        try:
            # Stop scaling
            if key in self.scaling_policies:
                del self.scaling_policies[key]
                del self.scaling_configs[key]
            
            # Undeploy
            target = self.deployment_targets.get(target_id)
            if target:
                await self._undeploy_from_target(agent_id, target)
            
            # Remove from deployments
            del self.deployments[key]
            
            return True
            
        except Exception as e:
            print(f"Undeployment error: {e}")
            return False
    
    async def _undeploy_from_target(self, agent_id: str, target: DeploymentTarget):
        """Undeploy from specific target"""
        # Implementation would depend on target type
        await asyncio.sleep(1)