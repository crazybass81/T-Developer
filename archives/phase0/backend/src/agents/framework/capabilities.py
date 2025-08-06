from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import inspect

class CapabilityType(Enum):
    ANALYSIS = "analysis"
    GENERATION = "generation"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    INTEGRATION = "integration"
    MONITORING = "monitoring"

@dataclass
class Capability:
    name: str
    type: CapabilityType
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_permissions: List[str]
    estimated_duration: Optional[int] = None  # milliseconds
    
class CapabilityMixin:
    """Mixin to add capability management to agents"""
    
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._capability_handlers: Dict[str, Callable] = {}
        
    def register_capability(
        self,
        capability: Capability,
        handler: Callable
    ) -> None:
        """Register a new capability"""
        self._capabilities[capability.name] = capability
        self._capability_handlers[capability.name] = handler
        
    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability"""
        return capability_name in self._capabilities
        
    def get_capabilities(self) -> List[Capability]:
        """Get all agent capabilities"""
        return list(self._capabilities.values())
        
    async def execute_capability(
        self,
        capability_name: str,
        input_data: Dict[str, Any]
    ) -> Any:
        """Execute a specific capability"""
        if not self.has_capability(capability_name):
            raise ValueError(f"Capability '{capability_name}' not found")
            
        capability = self._capabilities[capability_name]
        handler = self._capability_handlers[capability_name]
        
        # Validate input against schema
        self._validate_schema(input_data, capability.input_schema)
        
        # Execute handler
        if inspect.iscoroutinefunction(handler):
            result = await handler(input_data)
        else:
            result = handler(input_data)
            
        # Validate output against schema
        self._validate_schema(result, capability.output_schema)
        
        return result
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """Basic schema validation"""
        # Simple validation - can be enhanced with jsonschema
        if not isinstance(data, dict) and schema.get('type') == 'object':
            raise ValueError("Data must be an object")
        
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' missing")
    
    def get_capability_info(self, capability_name: str) -> Dict[str, Any]:
        """Get detailed information about a capability"""
        if not self.has_capability(capability_name):
            raise ValueError(f"Capability '{capability_name}' not found")
        
        capability = self._capabilities[capability_name]
        return {
            'name': capability.name,
            'type': capability.type.value,
            'description': capability.description,
            'input_schema': capability.input_schema,
            'output_schema': capability.output_schema,
            'required_permissions': capability.required_permissions,
            'estimated_duration': capability.estimated_duration
        }