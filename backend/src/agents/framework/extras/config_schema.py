from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ResourceRequirement:
    cpu: Optional[float] = None  # CPU cores
    memory: Optional[int] = None  # MB
    gpu: Optional[bool] = False
    storage: Optional[int] = None  # GB

@dataclass
class NetworkConfig:
    enable_http: bool = True
    enable_websocket: bool = False
    timeout: int = 30000  # milliseconds
    retry_policy: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.retry_policy is None:
            self.retry_policy = {
                "max_attempts": 3,
                "backoff_multiplier": 2,
                "initial_delay": 1000
            }

@dataclass
class AgentConfig:
    """Configuration schema for agents"""
    
    # Basic settings
    agent_type: str
    version: str = "1.0.0"
    enabled: bool = True
    
    # Runtime settings
    max_concurrent_tasks: int = 10
    task_timeout: int = 60000  # milliseconds
    
    # Resource requirements
    resources: ResourceRequirement = None
    
    # Network configuration
    network: NetworkConfig = None
    
    # Logging configuration
    logging: Dict[str, Any] = None
    
    # Model configuration (for AI agents)
    model_config: Optional[Dict[str, Any]] = None
    
    # Custom settings
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.resources is None:
            self.resources = ResourceRequirement()
        
        if self.network is None:
            self.network = NetworkConfig()
        
        if self.logging is None:
            self.logging = {
                "level": LogLevel.INFO,
                "format": "json",
                "destination": "console"
            }
        
        if self.custom_settings is None:
            self.custom_settings = {}
    
    def validate(self) -> List[str]:
        """Validate configuration and return errors"""
        errors = []
        
        if not self.agent_type:
            errors.append("agent_type is required")
        
        if self.max_concurrent_tasks < 1:
            errors.append("max_concurrent_tasks must be >= 1")
        
        if self.task_timeout < 1000:
            errors.append("task_timeout must be >= 1000ms")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_type": self.agent_type,
            "version": self.version,
            "enabled": self.enabled,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_timeout": self.task_timeout,
            "resources": {
                "cpu": self.resources.cpu,
                "memory": self.resources.memory,
                "gpu": self.resources.gpu,
                "storage": self.resources.storage
            },
            "network": {
                "enable_http": self.network.enable_http,
                "enable_websocket": self.network.enable_websocket,
                "timeout": self.network.timeout,
                "retry_policy": self.network.retry_policy
            },
            "logging": self.logging,
            "model_config": self.model_config,
            "custom_settings": self.custom_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create from dictionary"""
        resources = ResourceRequirement(**data.get("resources", {}))
        network = NetworkConfig(**data.get("network", {}))
        
        return cls(
            agent_type=data["agent_type"],
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 10),
            task_timeout=data.get("task_timeout", 60000),
            resources=resources,
            network=network,
            logging=data.get("logging", {}),
            model_config=data.get("model_config"),
            custom_settings=data.get("custom_settings", {})
        )